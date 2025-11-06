"""
End-to-end orchestration for building offline artifacts.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

from .config import PipelineConfig
from .utils import (
    ensure_dir,
    log_dataframe_info,
    read_table,
    save_json,
    save_parquet,
    time_block,
)

logger = logging.getLogger(__name__)


def read_raw_data(config: PipelineConfig) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load the raw MovieLens ratings and movies metadata tables.
    """

    ratings_df = read_table(
        config.dataset.ratings_path,
        column_names=["userId", "movieId", "rating", "timestamp"],
    )
    movies_df = read_table(
        config.dataset.movies_path,
        column_names=["movieId", "title", "genres"],
    )
    log_dataframe_info("ratings_raw", ratings_df)
    log_dataframe_info("movies_raw", movies_df)
    return ratings_df, movies_df


def leave_one_out_split(
    ratings_df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Apply leave-one-out split by user, keeping the most recent interaction per user for testing.
    """

    if "timestamp" not in ratings_df.columns:
        raise ValueError("ratings_df must contain a 'timestamp' column for leave-one-out split.")

    ratings_df = ratings_df.sort_values(["userId", "timestamp"])
    test_idx = ratings_df.groupby("userId").tail(1).index
    test_df = ratings_df.loc[test_idx]
    train_df = ratings_df.drop(test_idx)
    log_dataframe_info("ratings_train", train_df)
    log_dataframe_info("ratings_test", test_df)
    return train_df, test_df


def build_user_history(
    ratings_df: pd.DataFrame,
    min_rating_threshold: float,
) -> pd.DataFrame:
    """
    Construct per-user interaction summaries for quick lookups by the API.
    """

    interactions = (
        ratings_df.groupby("userId")
        .agg(
            watched_items=("movieId", list),
            liked_items=("rating", lambda s: ratings_df.loc[s.index, "movieId"][s >= min_rating_threshold].tolist()),
        )
        .reset_index()
    )
    log_dataframe_info("user_history", interactions)
    return interactions


def enrich_movie_metadata(movies_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract normalized metadata columns (year, primary genre tokens).
    """

    metadata = movies_df.copy()
    metadata["year"] = metadata["title"].str.extract(r"\((\d{4})\)").astype("float")
    metadata["genres_list"] = metadata["genres"].str.split("|")
    metadata["clean_title"] = metadata["title"].str.replace(r"\(\d{4}\)", "", regex=True).str.strip()
    log_dataframe_info("movie_meta", metadata)
    return metadata


def export_artifacts(
    config: PipelineConfig,
    pop_scores: pd.DataFrame,
    item_neighbors: Dict[str, object],
    content_neighbors: Dict[str, object],
    user_history: pd.DataFrame,
    movie_meta: pd.DataFrame,
) -> None:
    """
    Write pre-computed artifacts to disk.
    """

    save_parquet(pop_scores, config.artifacts.pop_score_path)
    ensure_dir(config.artifacts.item_neighbors_path)
    ensure_dir(config.artifacts.content_neighbors_path)
    from scipy import sparse

    logger.info("Writing item neighbors to %s", config.artifacts.item_neighbors_path)
    sparse.save_npz(config.artifacts.item_neighbors_path, item_neighbors["matrix"])
    save_json(
        {
            "movie_index": {int(k): int(v) for k, v in item_neighbors["movie_index"].items()},
            "index_movie": {int(k): int(v) for k, v in item_neighbors["index_movie"].items()},
        },
        config.artifacts.item_index_path,
    )
    logger.info("Writing content neighbors to %s", config.artifacts.content_neighbors_path)
    sparse.save_npz(config.artifacts.content_neighbors_path, content_neighbors["matrix"])
    save_json(
        {
            "movie_index": {int(k): int(v) for k, v in content_neighbors["movie_index"].items()},
            "index_movie": {int(k): int(v) for k, v in content_neighbors["index_movie"].items()},
        },
        config.artifacts.content_index_path,
    )
    save_parquet(user_history, config.artifacts.user_history_path)
    save_parquet(movie_meta, config.artifacts.movie_meta_path)


def run_pipeline(config: PipelineConfig) -> Dict[str, Path]:
    """
    Execute the full offline pipeline and return written artifact paths.
    """

    logger.info("Starting offline pipeline")
    with time_block("read_raw_data"):
        ratings_df, movies_df = read_raw_data(config)

    with time_block("leave_one_out_split"):
        train_df, test_df = leave_one_out_split(ratings_df)

    from .popularity import compute_popularity_scores
    from .item_cf import build_item_cf_neighbors
    from .content_based import build_content_neighbors

    with time_block("compute_popularity"):
        pop_scores = compute_popularity_scores(
            train_df, config.popularity_smoothing, config.min_rating_threshold
        )

    with time_block("build_item_cf"):
        item_neighbors = build_item_cf_neighbors(
            train_df, k=config.topk_neighbors, min_rating=config.min_rating_threshold
        )

    with time_block("build_content_neighbors"):
        content_neighbors = build_content_neighbors(
            movies_df, k=config.topk_neighbors
        )

    with time_block("user_history"):
        user_history = build_user_history(train_df, config.min_rating_threshold)

    with time_block("movie_metadata"):
        movie_meta = enrich_movie_metadata(movies_df)

    export_artifacts(config, pop_scores, item_neighbors, content_neighbors, user_history, movie_meta)

    logger.info("Pipeline completed")
    return {
        "popularity": config.artifacts.pop_score_path,
        "item_neighbors": config.artifacts.item_neighbors_path,
        "content_neighbors": config.artifacts.content_neighbors_path,
        "user_history": config.artifacts.user_history_path,
        "movie_meta": config.artifacts.movie_meta_path,
    }
