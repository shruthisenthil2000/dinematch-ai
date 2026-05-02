"""Smoke tests for Phase 2 Flask app."""

from __future__ import annotations

from phase2.app import create_app


def test_health_ok():
    c = create_app().test_client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json["phase"] == 2


def test_api_preferences_valid():
    c = create_app().test_client()
    r = c.post("/api/preferences", json={"location": "X", "budget": "low", "min_rating": 3.0})
    assert r.status_code == 200
    assert r.json["valid"] is True
    assert r.json["preferences"]["cuisines"] == []
