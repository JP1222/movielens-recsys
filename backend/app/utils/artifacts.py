"""
Helpers for loading offline artifacts into memory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd
from scipy import sparse

logger = logging.getLogger(__name__)


def load_popularity_scores(path: Path) -> pd.DataFrame:
    """Load popular movies Parquet file."""

    logger.info("Loading popularity scores from %s", path)
    return pd.read_parquet(path)


def load_item_neighbors(matrix_path: Path, index_path: Path) -> Dict[str, object]:
    """Load item-based similarity artifacts."""

    logger.info("Loading item neighbors from %s", matrix_path)
    matrix = sparse.load_npz(matrix_path)
    with index_path.open("r", encoding="utf-8") as fp:
        metadata = json.load(fp)
    return {
        "matrix": matrix,
        "movie_index": {int(k): int(v) for k, v in metadata["movie_index"].items()},
        "index_movie": {int(k): int(v) for k, v in metadata["index_movie"].items()},
    }


def load_content_neighbors(matrix_path: Path, index_path: Path) -> Dict[str, object]:
    """Load content similarity artifacts."""

    logger.info("Loading content neighbors from %s", matrix_path)
    matrix = sparse.load_npz(matrix_path)
    with index_path.open("r", encoding="utf-8") as fp:
        metadata = json.load(fp)
    return {
        "matrix": matrix,
        "movie_index": {int(k): int(v) for k, v in metadata["movie_index"].items()},
        "index_movie": {int(k): int(v) for k, v in metadata["index_movie"].items()},
    }


def load_movie_metadata(path: Path) -> pd.DataFrame:
    """Load movie metadata table."""

    logger.info("Loading movie metadata from %s", path)
    return pd.read_parquet(path)


def load_user_history(path: Path) -> pd.DataFrame:
    """Load per-user history artifact."""

    logger.info("Loading user history from %s", path)
    return pd.read_parquet(path)
