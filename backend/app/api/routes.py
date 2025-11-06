"""
HTTP route definitions for the recommendation service.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import RecommenderDep
from ..models.schemas import (
    RecommendationPayload,
    RecommendationResponse,
    RecommendationsEnvelope,
)

router = APIRouter(prefix="/recommend", tags=["recommendations"])


@router.get(
    "/popular",
    response_model=RecommendationsEnvelope,
    summary="Retrieve globally popular movies",
)
async def recommend_popular(
    recommender: RecommenderDep,
    user_id: int | None = Query(None, description="User identifier for logging."),
    k: int = Query(10, ge=1, le=200),
) -> RecommendationsEnvelope:
    """Return the top-k popular movies computed offline."""

    results = recommender.recommend_popular(user_id=user_id, k=k)
    return RecommendationsEnvelope(
        user_id=user_id,
        algorithm="popular",
        items=[RecommendationResponse(**item) for item in results],
    )


@router.get(
    "/itemcf",
    response_model=RecommendationsEnvelope,
    summary="Retrieve personalized item-based collaborative filtering results",
)
async def recommend_item_cf(
    recommender: RecommenderDep,
    user_id: int = Query(..., ge=1),
    k: int = Query(10, ge=1, le=200),
) -> RecommendationsEnvelope:
    """Return personalized recommendations using item-based CF."""

    results = recommender.recommend_item_cf(user_id=user_id, k=k)
    if not results:
        raise HTTPException(status_code=404, detail=f"No history found for user {user_id}.")
    return RecommendationsEnvelope(
        user_id=user_id,
        algorithm="item_cf",
        items=[RecommendationResponse(**item) for item in results],
    )


@router.post(
    "/by-titles",
    response_model=RecommendationsEnvelope,
    summary="Recommend similar movies based on input titles",
)
async def recommend_by_titles(
    recommender: RecommenderDep,
    payload: RecommendationPayload,
    k: int = Query(10, ge=1, le=200),
) -> RecommendationsEnvelope:
    """Return content-based similar movies based on submitted titles."""

    results = recommender.recommend_by_titles(payload.titles, k=k)
    if not results:
        raise HTTPException(status_code=404, detail="No matching titles found.")
    return RecommendationsEnvelope(
        user_id=None,
        algorithm="content",
        items=[RecommendationResponse(**item) for item in results],
    )
