"""
Utility helpers shared by the offline scripts.
"""

from __future__ import annotations

import json
import logging
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Iterator, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def ensure_dir(path: Path) -> None:
    """Create the parent directory for ``path`` if it does not exist."""

    path.parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def time_block(name: str) -> Iterator[None]:
    """
    Context manager to measure execution time.

    Yields the elapsed seconds after the block finishes to allow the caller to
    log the result or append it to a diagnostics table.
    """

    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    logger.info("Stage %s completed in %.2fs", name, elapsed)


def read_table(path: Path, column_names: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Load a MovieLens TSV or CSV file, inferring the delimiter.

    The MovieLens releases mix separators depending on the variant, so we keep
    the logic flexible and delegate to pandas' automatic sniffing while
    handling the double-colon separator used in older datasets.
    """

    if not path.exists():
        raise FileNotFoundError(path)
    logger.info("Loading table %s", path)
    header = 0
    sep: Optional[str] = None
    if path.suffix == ".dat":
        header = None
        sep = "::"
    try:
        df = pd.read_csv(
            path,
            sep=sep,
            engine="python",
            header=header,
            encoding="latin-1",  # Handle extended characters present in MovieLens metadata.
        )
    except ValueError:
        df = pd.read_csv(
            path,
            sep="::",
            engine="python",
            header=header,
            encoding="latin-1",
        )
    if column_names and len(df.columns) == len(column_names):
        df.columns = column_names
    return df


def memory_usage_mb(df: pd.DataFrame) -> float:
    """Return the approximate memory footprint in megabytes."""

    return df.memory_usage(index=True, deep=True).sum() / (1024**2)


def log_dataframe_info(name: str, df: pd.DataFrame) -> None:
    """Emit standard diagnostics for a pandas DataFrame."""

    logger.info(
        "%s -> rows=%d, cols=%d, memory=%.2f MB",
        name,
        len(df),
        df.shape[1],
        memory_usage_mb(df),
    )


def save_parquet(df: pd.DataFrame, path: Path) -> None:
    """Persist a DataFrame to Parquet with snappy compression."""

    ensure_dir(path)
    logger.info("Writing Parquet: %s", path)
    df.to_parquet(path, index=False, compression="snappy")


def serialize_metrics(metrics: Dict[str, float], path: Path) -> None:
    """Persist evaluation metrics to a JSON sidecar for later visualization."""

    ensure_dir(path)
    logger.info("Saving metrics to %s", path)
    pd.Series(metrics).to_json(path, indent=2)


def save_json(payload: Dict[str, object], path: Path) -> None:
    """Write a JSON helper file."""

    ensure_dir(path)
    logger.info("Writing JSON: %s", path)
    with path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)
