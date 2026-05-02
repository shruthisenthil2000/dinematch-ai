"""Smoke tests for Phase 6 frontend app."""

from __future__ import annotations

from phase6.app import create_app


def test_health_ok():
    c = create_app().test_client()
    r = c.get("/health")
    assert r.status_code == 200
    assert r.json["phase"] == 6


def test_index_contains_recommend_endpoint():
    c = create_app().test_client()
    r = c.get("/")
    assert r.status_code == 200
    text = r.get_data(as_text=True)
    assert "Phase 6 Frontend" in text
    assert "/api/recommend" in text


def test_recommend_requires_json_body():
    c = create_app().test_client()
    r = c.post("/api/recommend", data="not-json", content_type="application/json")
    assert r.status_code == 400
