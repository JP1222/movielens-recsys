"""
Shared FastAPI dependencies for the recommender service.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from .services.recommender import RecommenderService


def get_recommender(request: Request) -> RecommenderService:
    """
    Retrieve the singleton RecommenderService instance stored on the app.
    """

    recommender: RecommenderService | None = getattr(request.app.state, "recommender", None)
    if recommender is None:
        raise RuntimeError("RecommenderService has not been initialized.")
    return recommender


RecommenderDep = Annotated[RecommenderService, Depends(get_recommender)]

