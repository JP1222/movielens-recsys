"""
Central configuration for the offline pipeline.

The defaults assume the MovieLens data is already available locally. Paths can
be overridden through environment variables or CLI arguments.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class DatasetConfig:
    """Settings describing where to find the raw datasets."""

    ratings_path: Path
    movies_path: Path
    links_path: Optional[Path] = None
    tags_path: Optional[Path] = None


@dataclass(slots=True)
class ArtifactConfig:
    """Settings for output artifacts produced by the offline jobs."""

    output_dir: Path
    pop_score_path: Path = field(init=False)
    item_neighbors_path: Path = field(init=False)
    content_neighbors_path: Path = field(init=False)
    item_index_path: Path = field(init=False)
    content_index_path: Path = field(init=False)
    user_history_path: Path = field(init=False)
    movie_meta_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pop_score_path = self.output_dir / "pop_score.parquet"
        self.item_neighbors_path = self.output_dir / "item_neighbors.npz"
        self.content_neighbors_path = self.output_dir / "content_neighbors.npz"
        self.item_index_path = self.output_dir / "item_index.json"
        self.content_index_path = self.output_dir / "content_index.json"
        self.user_history_path = self.output_dir / "user_history.parquet"
        self.movie_meta_path = self.output_dir / "movie_meta.parquet"


@dataclass(slots=True)
class PipelineConfig:
    """Aggregated configuration for complete pipeline runs."""

    dataset: DatasetConfig
    artifacts: ArtifactConfig
    min_rating_threshold: float = 4.0
    topk_neighbors: int = 100
    popularity_smoothing: float = 20.0
    random_seed: int = 42
