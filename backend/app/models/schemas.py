"""
API schema definitions using Pydantic models.
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RecommendationResponse(BaseModel):
    """Single recommendation item returned by the API."""

    movie_id: int = Field(..., description="MovieLens movie identifier.")
    title: str
    genres: List[str] = Field(default_factory=list)
    score: float = Field(..., description="Relevance score returned by the algorithm.")
    source: str = Field(..., description="Algorithm that produced the item.")
    reason: Optional[str] = Field(None, description="Short explanation for the recommendation.")


class RecommendationsEnvelope(BaseModel):
    """Envelope for recommendation lists returned by the endpoints."""

    user_id: Optional[int]
    algorithm: str
    items: List[RecommendationResponse]


class RecommendationPayload(BaseModel):
    """Request payload for recommending by titles."""

    titles: List[str] = Field(..., min_items=1, description="Seed movie titles to base recommendations on.")

