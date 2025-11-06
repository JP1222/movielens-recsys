"""
Smoke tests for the FastAPI application.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_health_check_popular_endpoint(monkeypatch):
    """Ensure the popular endpoint returns a 200 when recommender is stubbed."""

    class DummyService:
        def recommend_popular(self, user_id, k):
            return [{"movie_id": 1, "title": "Dummy", "genres": ["Drama"], "score": 1.0, "source": "popular"}]

        def recommend_item_cf(self, user_id, k):
            return []

        def recommend_by_titles(self, titles, k):
            return []

    monkeypatch.setattr(app.state, "recommender", DummyService())
    client = TestClient(app)
    response = client.get("/recommend/popular?k=5")
    assert response.status_code == 200
    assert response.json()["items"], "Expected non-empty recommendations"

