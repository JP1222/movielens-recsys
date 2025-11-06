"""
Content-based similarity computations backed by TF-IDF on genres and titles.
"""

from __future__ import annotations

import logging
from typing import Dict

import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def build_content_neighbors(
    movies_df: pd.DataFrame,
    k: int,
) -> Dict[str, object]:
    """
    Generate nearest neighbors for each movie based on content features.
    """

    logger.info("Computing content-based neighbors with k=%d", k)
    features = (
        movies_df["title"].fillna("")
        + " "
        + movies_df["genres"].fillna("").str.replace("|", " ")
    )

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    feature_matrix = vectorizer.fit_transform(features)
    logger.info("TF-IDF matrix shape: %s", feature_matrix.shape)

    similarity = cosine_similarity(feature_matrix, dense_output=False)
    similarity = sparse.csr_matrix(similarity)
    similarity.setdiag(0.0)
    if k < similarity.shape[0]:
        similarity = _keep_top_k(similarity, k=k)

    movie_index = {mid: idx for idx, mid in enumerate(movies_df["movieId"].tolist())}
    index_movie = {idx: mid for mid, idx in movie_index.items()}

    return {
        "matrix": similarity,
        "movie_index": movie_index,
        "index_movie": index_movie,
        "vectorizer": vectorizer,
    }


def _keep_top_k(matrix: sparse.csr_matrix, k: int) -> sparse.csr_matrix:
    """Helper identical to the collaborative filtering pruning."""

    matrix = matrix.tolil()
    for i in range(matrix.shape[0]):
        row = matrix.data[i]
        if len(row) > k:
            cutoff = sorted(row, reverse=True)[k - 1]
            keep = [idx for idx, value in enumerate(row) if value >= cutoff]
            matrix.rows[i] = [matrix.rows[i][j] for j in keep]
            matrix.data[i] = [matrix.data[i][j] for j in keep]
    return matrix.tocsr()

