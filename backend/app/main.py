"""
FastAPI application that exposes recommendation endpoints.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI

from .api.routes import router
from .core.config import settings
from .services.recommender import RecommenderService

logger = logging.getLogger(__name__)

app = FastAPI(
    title="MovieLens Recommender",
    description="Unified API for popularity, item-based CF, and content similarity recommendations.",
    version="0.1.0",
)


@app.on_event("startup")
async def startup_event() -> None:
    """Load artifacts into memory when the server starts."""

    logger.info("Loading artifacts from %s", settings.artifact_dir)
    app.state.recommender = RecommenderService.from_settings(settings)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Release any cached resources during shutdown."""

    recommender: RecommenderService | None = getattr(app.state, "recommender", None)
    if recommender:
        recommender.close()


app.include_router(router)
