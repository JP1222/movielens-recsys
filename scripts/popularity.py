"""Compute popularity-based recommendation scores with Bayesian smoothing."""

from __future__ import annotations

import logging
from typing import Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def compute_popularity_scores(
    ratings_df: pd.DataFrame,
    smoothing: float,
    min_rating_threshold: float,
) -> pd.DataFrame:
    """
    Compute Bayesian-smoothed movie popularity scores.

    Parameters
    ----------
    ratings_df:
        Training ratings after leave-one-out split.
    smoothing:
        Prior strength for Bayesian mean smoothing.
    min_rating_threshold:
        Ratings equal to or above this threshold count as positive feedback.
    """

    logger.info("Computing popularity scores with smoothing=%s", smoothing)
    agg = (
        ratings_df.groupby("movieId")
        .agg(
            rating_count=("rating", "size"),
            rating_sum=("rating", "sum"),
            positive_count=("rating", lambda x: (x >= min_rating_threshold).sum()),
        )
        .reset_index()
    )

    global_mean = ratings_df["rating"].mean()
    agg["bayesian_score"] = (agg["rating_sum"] + smoothing * global_mean) / (
        agg["rating_count"] + smoothing
    )
    agg["positive_ratio"] = agg["positive_count"] / agg["rating_count"].replace(0, np.nan)
    agg.fillna({"positive_ratio": 0.0}, inplace=True)
    agg.sort_values("bayesian_score", ascending=False, inplace=True)
    logger.info("Computed popularity for %d titles", len(agg))
    return agg[["movieId", "bayesian_score", "rating_count", "positive_ratio"]]

