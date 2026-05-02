"""Phase 5 HTTP API."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from phase5.app import create_app


def _minimal_parquet(path) -> None:
    df = pd.DataFrame(
        [
            {
                "restaurant_id": "aa",
                "name": "Alpha",
                "city": "Pune",
                "cuisines": ["italian"],
                "rating": 4.5,
                "votes": 10,
                "cost_band": "medium",
            }
        ]
    )
    df.to_parquet(path, index=False)


@pytest.fixture
def client(tmp_path, monkeypatch):
    pq = tmp_path / "c.parquet"
    _minimal_parquet(pq)
    monkeypatch.setenv("PHASE5_PARQUET", str(pq))
    monkeypatch.setenv("PHASE5_DISABLE_CACHE", "1")
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["phase"] == 5


def test_recommend_invalid_preferences(client):
    r = client.post(
        "/api/recommend",
        data=json.dumps({"preferences": {"location": "", "budget": "medium", "min_rating": 0}}),
        content_type="application/json",
    )
    assert r.status_code == 400
    body = r.get_json()
    assert body["valid"] is False


def test_recommend_ok_offline(client):
    body = {
        "preferences": {
            "location": "Pune",
            "budget": "medium",
            "cuisines": [],
            "min_rating": 0.0,
        },
        "use_llm": False,
    }
    r = client.post("/api/recommend", data=json.dumps(body), content_type="application/json")
    assert r.status_code == 200
    data = r.get_json()
    assert data["valid"] is True
    assert len(data["response"]["recommendations"]) == 1
    assert data["observability"]["cache_hit"] is False
    assert data["observability"]["candidate_count"] == 1
