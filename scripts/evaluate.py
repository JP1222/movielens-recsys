"""
Evaluation metrics helpers for recommendation lists.
"""

from __future__ import annotations

import logging
from typing import Dict, Iterable, List, Sequence

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def precision_at_k(recommended: Sequence[int], relevant: Sequence[int], k: int) -> float:
    """Compute precision@k for a single user."""

    if k <= 0:
        return 0.0
    recommended_k = recommended[:k]
    relevant_set = set(relevant)
    hits = sum(1 for item in recommended_k if item in relevant_set)
    return hits / k


def recall_at_k(recommended: Sequence[int], relevant: Sequence[int], k: int) -> float:
    """Compute recall@k for a single user."""

    relevant_set = set(relevant)
    if not relevant_set:
        return 0.0
    recommended_k = recommended[:k]
    hits = sum(1 for item in recommended_k if item in relevant_set)
    return hits / len(relevant_set)


def ndcg_at_k(recommended: Sequence[int], relevant: Sequence[int], k: int) -> float:
    """Compute discounted cumulative gain normalized by ideal DCG."""

    recommended_k = recommended[:k]
    gains = np.array([1.0 if item in relevant else 0.0 for item in recommended_k], dtype=float)
    if gains.size == 0:
        return 0.0
    discounts = 1 / np.log2(np.arange(2, gains.size + 2))
    dcg = float(np.sum(gains * discounts))
    ideal_gains = np.sort(gains)[::-1]
    idcg = np.sum(ideal_gains * discounts)
    return float(dcg / idcg) if idcg > 0 else 0.0


def evaluate_model(
    recommendations: Dict[int, Sequence[int]],
    ground_truth: Dict[int, Sequence[int]],
    k_values: Iterable[int] = (10,),
) -> pd.DataFrame:
    """
    Evaluate recommendation quality across multiple cutoffs.
    """

    rows: List[Dict[str, float]] = []
    for k in k_values:
        metrics = {"k": k, "precision": 0.0, "recall": 0.0, "ndcg": 0.0}
        user_count = 0
        for user_id, recs in recommendations.items():
            relevant = ground_truth.get(user_id, [])
            if not relevant:
                continue
            user_count += 1
            metrics["precision"] += precision_at_k(recs, relevant, k)
            metrics["recall"] += recall_at_k(recs, relevant, k)
            metrics["ndcg"] += ndcg_at_k(recs, relevant, k)

        if user_count > 0:
            for key in ("precision", "recall", "ndcg"):
                metrics[key] /= user_count
        rows.append(metrics)

    result = pd.DataFrame(rows)
    logger.info("Evaluation results:\n%s", result)
    return result
