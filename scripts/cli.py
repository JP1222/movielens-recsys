"""
Command-line entry point for running the offline pipeline.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import ArtifactConfig, DatasetConfig, PipelineConfig
from .data_pipeline import run_pipeline
from .logging_utils import setup_logging


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the offline pipeline."""

    parser = argparse.ArgumentParser(description="Run MovieLens offline pipelines.")
    parser.add_argument("--ratings", type=Path, required=True, help="Path to ratings data file.")
    parser.add_argument("--movies", type=Path, required=True, help="Path to movies metadata file.")
    parser.add_argument(
        "--output-dir", type=Path, required=True, help="Directory where artifacts will be written."
    )
    parser.add_argument("--topk", type=int, default=100, help="Neighbors to retain per item.")
    parser.add_argument(
        "--min-rating", type=float, default=4.0, help="Minimum rating to treat as positive feedback."
    )
    parser.add_argument(
        "--smoothing",
        type=float,
        default=20.0,
        help="Smoothing constant for Bayesian popularity.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser.parse_args()


def main() -> None:
    """Entrypoint invoked by the ``python -m scripts.cli`` command."""

    args = parse_args()
    setup_logging(getattr(logging, args.log_level))

    config = PipelineConfig(
        dataset=DatasetConfig(ratings_path=args.ratings, movies_path=args.movies),
        artifacts=ArtifactConfig(output_dir=args.output_dir),
        topk_neighbors=args.topk,
        min_rating_threshold=args.min_rating,
        popularity_smoothing=args.smoothing,
    )
    run_pipeline(config)


if __name__ == "__main__":
    main()

