"""
Runtime configuration powered by Pydantic settings.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration for the FastAPI application."""

    artifact_dir: Path = Path(os.getenv("ARTIFACT_DIR", "./data/artifacts/ml-1m")).resolve()
    popularity_path: Path = Path(os.getenv("POPULARITY_PATH", artifact_dir / "pop_score.parquet")).resolve()
    item_neighbors_path: Path = Path(os.getenv("ITEM_NEIGHBORS_PATH", artifact_dir / "item_neighbors.npz")).resolve()
    item_index_path: Path = Path(os.getenv("ITEM_INDEX_PATH", artifact_dir / "item_index.json")).resolve()
    content_neighbors_path: Path = Path(os.getenv("CONTENT_NEIGHBORS_PATH", artifact_dir / "content_neighbors.npz")).resolve()
    content_index_path: Path = Path(os.getenv("CONTENT_INDEX_PATH", artifact_dir / "content_index.json")).resolve()
    user_history_path: Path = Path(os.getenv("USER_HISTORY_PATH", artifact_dir / "user_history.parquet")).resolve()
    movie_meta_path: Path = Path(os.getenv("MOVIE_META_PATH", artifact_dir / "movie_meta.parquet")).resolve()

    class Config:
        env_prefix = "RECSYS_"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
