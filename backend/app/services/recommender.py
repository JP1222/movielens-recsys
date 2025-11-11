"""
Service for retrieving recommendations from offline artifacts.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from scipy import sparse

from ..core.config import Settings
from ..utils.artifacts import (
    load_content_neighbors,
    load_item_neighbors,
    load_movie_metadata,
    load_popularity_scores,
    load_user_history,
)

logger = logging.getLogger(__name__)


@dataclass
class RecommenderService:
    """Facade around offline artifacts to produce API-ready responses."""

    popularity_df: pd.DataFrame
    item_similarity: sparse.csr_matrix
    item_index: Dict[int, int]
    index_item: Dict[int, int]
    content_similarity: sparse.csr_matrix
    content_index: Dict[int, int]
    index_content: Dict[int, int]
    movie_meta: pd.DataFrame
    user_history: pd.DataFrame

    @classmethod
    def from_settings(cls, settings: Settings) -> "RecommenderService":
        """Factory that loads all artifacts based on configured paths."""

        popularity_df = load_popularity_scores(settings.popularity_path)
        item_artifacts = load_item_neighbors(
            settings.item_neighbors_path, settings.item_index_path
        )
        content_artifacts = load_content_neighbors(
            settings.content_neighbors_path, settings.content_index_path
        )
        movie_meta = load_movie_metadata(settings.movie_meta_path)
        user_history = load_user_history(settings.user_history_path)
        return cls(
            popularity_df=popularity_df,
            item_similarity=item_artifacts["matrix"],
            item_index=item_artifacts["movie_index"],
            index_item=item_artifacts["index_movie"],
            content_similarity=content_artifacts["matrix"],
            content_index=content_artifacts["movie_index"],
            index_content=content_artifacts["index_movie"],
            movie_meta=movie_meta,
            user_history=user_history,
        )

    def close(self) -> None:
        """Placeholder for compatibility with context managers."""

        logger.info("RecommenderService shutdown complete.")

    def recommend_popular(self, user_id: Optional[int], k: int) -> List[Dict[str, object]]:
        """Return top-k popular titles enriched with metadata."""

        top_df = self.popularity_df.head(k).merge(
            self.movie_meta[["movieId", "clean_title", "title", "genres_list", "year"]],
            how="left",
            left_on="movieId",
            right_on="movieId",
        )
        return [
            {
                "movie_id": int(row.movieId),
                "title": self._format_title(
                    getattr(row, "clean_title", None) or getattr(row, "title", str(row.movieId))
                ),
                "genres": self._coerce_genres(getattr(row, "genres_list", None)),
                "score": float(row.bayesian_score),
                "source": "popular",
                "reason": "Highly rated by the community.",
            }
            for row in top_df.itertuples()
        ]

    def recommend_item_cf(self, user_id: int, k: int) -> List[Dict[str, object]]:
        """Produce item-based collaborative filtering recommendations."""

        history_row = self.user_history[self.user_history["userId"] == user_id]
        if history_row.empty:
            return []

        liked_items = self._ensure_list(history_row.iloc[0]["liked_items"])
        if not liked_items:
            liked_items = self._ensure_list(history_row.iloc[0]["watched_items"])
        if not liked_items:
            return []

        scores = np.zeros(self.item_similarity.shape[0])
        for movie_id in liked_items:
            idx = self.item_index.get(movie_id)
            if idx is None:
                continue
            scores += self.item_similarity[idx].toarray().ravel()

        # Remove already seen items
        seen = set(self._ensure_list(history_row.iloc[0]["watched_items"]))
        ranked_indices = np.argsort(scores)[::-1]
        recommendations: List[Dict[str, object]] = []
        for idx in ranked_indices:
            movie_id = self.index_item.get(idx)
            if movie_id is None or movie_id in seen:
                continue
            metadata = self._lookup_metadata(movie_id)
            seed_info = self._lookup_metadata(liked_items[0]) if liked_items else {}
            recommendations.append(
                {
                    "movie_id": movie_id,
                    "title": metadata.get("title"),
                    "genres": metadata.get("genres", []),
                    "score": float(scores[idx]),
                    "source": "item_cf",
                    "reason": f"Because you liked {seed_info.get('title', liked_items[0])}",
                }
            )
            if len(recommendations) >= k:
                break
        return recommendations

    def recommend_by_titles(self, titles: List[str], k: int) -> List[Dict[str, object]]:
        """Recommend similar titles leveraging the content similarity matrix."""

        seed_indices = [
            self.content_index.get(self._find_movie_id_by_title(title)) for title in titles
        ]
        seed_indices = [idx for idx in seed_indices if idx is not None]
        if not seed_indices:
            return []

        scores = np.zeros(self.content_similarity.shape[0])
        for idx in seed_indices:
            scores += self.content_similarity[idx].toarray().ravel()
        ranked_indices = np.argsort(scores)[::-1]

        seeds = {self.index_content[idx] for idx in seed_indices}
        recommendations: List[Dict[str, object]] = []
        for idx in ranked_indices:
            movie_id = self.index_content.get(idx)
            if movie_id is None or movie_id in seeds:
                continue
            metadata = self._lookup_metadata(movie_id)
            recommendations.append(
                {
                    "movie_id": movie_id,
                    "title": metadata.get("title"),
                    "genres": metadata.get("genres", []),
                    "score": float(scores[idx]),
                    "source": "content",
                    "reason": f"Similar to {titles[0]}",
                }
            )
            if len(recommendations) >= k:
                break
        return recommendations

    def _lookup_metadata(self, movie_id: int) -> Dict[str, object]:
        """Helper to map metadata row into a serializable payload."""

        row = self.movie_meta[self.movie_meta["movieId"] == movie_id]
        if row.empty:
            return {"title": f"Movie {movie_id}", "genres": []}
        entry = row.iloc[0]
        return {
            "title": self._format_title(entry.get("clean_title") or entry.get("title")),
            "genres": self._coerce_genres(entry.get("genres_list")),
            "year": entry.get("year"),
        }

    def _find_movie_id_by_title(self, title: str) -> Optional[int]:
        """Perform a simple contains search over normalized titles."""

        mask = self.movie_meta["clean_title"].str.contains(title, case=False, na=False)
        match = self.movie_meta[mask].head(1)
        if match.empty:
            return None
        return int(match.iloc[0]["movieId"])

    @staticmethod
    def _ensure_list(value: object) -> List[int]:
        """Coerce stored array-like values into Python lists."""

        if value is None:
            return []
        if isinstance(value, list):
            return value
        if hasattr(value, "tolist"):
            converted = value.tolist()
            return converted if isinstance(converted, list) else [converted]
        if isinstance(value, (set, tuple)):
            return list(value)
        return [value]

    @staticmethod
    def _coerce_genres(value: object) -> List[str]:
        """Normalize heterogeneous genre containers into a simple list of strings."""

        if value is None:
            return []
        if isinstance(value, list):
            return [str(v) for v in value]
        if hasattr(value, "tolist"):
            converted = value.tolist()
            if isinstance(converted, list):
                return [str(v) for v in converted]
            return [str(converted)]
        if isinstance(value, (tuple, set)):
            return [str(v) for v in value]
        if isinstance(value, str):
            return [value]
        return []

    @staticmethod
    def _format_title(raw_title: object) -> str:
        """Present titles without the trailing article suffix used in MovieLens metadata."""

        if not raw_title:
            return ""
        title = str(raw_title).strip()
        for article in ("The", "An", "A"):
            suffix = f", {article}"
            if title.endswith(suffix):
                return f"{article} {title[: -len(suffix)].strip()}"
        return title
