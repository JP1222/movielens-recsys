"""
Item-based collaborative filtering utilities.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict

import numpy as np
import pandas as pd
from scipy import sparse

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ItemCFArtifacts:
    """Container for item-based similarity outputs."""

    matrix: sparse.csr_matrix
    movie_index: Dict[int, int]
    index_movie: Dict[int, int]


def build_item_cf_neighbors(
    ratings_df: pd.DataFrame,
    k: int,
    min_rating: float,
) -> Dict[str, object]:
    """
    Construct cosine similarities between items using sparse vectors.

    Returns
    -------
    dict
        A mapping containing the similarity matrix and index lookups.
    """

    logger.info("Building item-CF neighbors with k=%d", k)
    filtered = ratings_df[ratings_df["rating"] >= min_rating]

    user_ids = filtered["userId"].unique()
    movie_ids = filtered["movieId"].unique()

    user_index = {uid: idx for idx, uid in enumerate(user_ids)}
    movie_index = {mid: idx for idx, mid in enumerate(movie_ids)}
    index_movie = {idx: mid for mid, idx in movie_index.items()}

    rows = filtered["userId"].map(user_index)
    cols = filtered["movieId"].map(movie_index)
    data = filtered["rating"].astype(float)

    interaction_matrix = sparse.coo_matrix(
        (data, (rows, cols)),
        shape=(len(user_index), len(movie_index)),
    ).tocsr()

    normalized = sparse.csr_matrix(interaction_matrix)
    item_norms = sparse.linalg.norm(normalized, axis=0)
    item_norms[item_norms == 0] = 1.0
    normalized = normalized.multiply(1 / item_norms)

    similarity = normalized.T @ normalized

    # Zero out diagonal and keep top-k similarities per item
    similarity.setdiag(0.0)
    if k < similarity.shape[0]:
        similarity = _keep_top_k(similarity, k=k)

    logger.info("Item similarity matrix shape: %s", similarity.shape)
    return {
        "matrix": similarity.tocsr(),
        "movie_index": movie_index,
        "index_movie": index_movie,
    }


def _keep_top_k(matrix: sparse.csr_matrix, k: int) -> sparse.csr_matrix:
    """
    Retain only the top-k largest values per row in a CSR matrix.
    """

    matrix = matrix.tolil()
    for i in range(matrix.shape[0]):
        row = matrix.data[i]
        if len(row) > k:
            idx = np.argpartition(row, -k)[: -k]
            matrix.rows[i] = [col for j, col in enumerate(matrix.rows[i]) if j not in idx]
            matrix.data[i] = [value for j, value in enumerate(row) if j not in idx]
    return matrix.tocsr()

