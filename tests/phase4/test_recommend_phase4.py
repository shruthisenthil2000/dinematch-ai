"""Phase 4 recommend_with_groq: offline paths, mocks, fallbacks."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from phase4.llm.response_parse import get_response_validator
from phase4.recommend import recommend_with_groq


def _df():
    return pd.DataFrame(
        [
            {
                "restaurant_id": "r1",
                "name": "One",
                "city": "Pune",
                "locality": "a",
                "cuisines": ["italian"],
                "rating": 4.5,
                "votes": 10,
                "approx_cost_for_two": 600.0,
                "cost_band": "medium",
                "rest_type": None,
                "online_order": None,
                "book_table": None,
                "url": None,
                "address": None,
            },
            {
                "restaurant_id": "r2",
                "name": "Two",
                "city": "Pune",
                "locality": "b",
                "cuisines": ["chinese"],
                "rating": 4.0,
                "votes": 5,
                "approx_cost_for_two": 500.0,
                "cost_band": "medium",
                "rest_type": None,
                "online_order": None,
                "book_table": None,
                "url": None,
                "address": None,
            },
        ]
    )


def _prefs():
    return {"location": "Pune", "budget": "medium", "cuisines": [], "min_rating": 0.0}


def test_empty_candidates_no_llm_path():
    empty = pd.DataFrame(
        columns=[
            "restaurant_id",
            "name",
            "city",
            "locality",
            "cuisines",
            "rating",
            "votes",
            "approx_cost_for_two",
            "cost_band",
            "rest_type",
            "online_order",
            "book_table",
            "url",
            "address",
        ]
    )
    out = recommend_with_groq(_prefs(), empty, top_n=3, use_llm=False)
    assert out["recommendations"] == []
    assert out["meta"]["candidate_count"] == 0


def test_use_llm_false_validates_schema():
    df = _df()
    out = recommend_with_groq(_prefs(), df, top_n=1, use_llm=False)
    get_response_validator().validate(out)
    assert len(out["recommendations"]) == 1
    assert out["recommendations"][0]["restaurant_id"] == "r1"
    assert out["meta"]["notes"] == "llm_disabled"


class ScriptedGroq:
    def __init__(self, responses):
        self._responses = list(responses)

    def complete(self, messages):
        if not self._responses:
            raise RuntimeError("no scripted responses left")
        return self._responses.pop(0)


def test_retries_then_accepts_valid_llm_output():
    good = {
        "recommendations": [
            {
                "restaurant_id": "r1",
                "name": "One",
                "cuisine": "italian",
                "rating": 4.5,
                "estimated_cost": "medium, ~600 for two",
                "ai_rationale": "Matches preferences.",
                "rank": 1,
            }
        ],
        "meta": {"notes": "from_model"},
    }
    client = ScriptedGroq(["not json at all", json.dumps(good)])
    out = recommend_with_groq(
        _prefs(),
        _df(),
        top_n=2,
        client=client,
        use_llm=True,
        max_parse_retries=1,
    )
    get_response_validator().validate(out)
    assert out["recommendations"][0]["restaurant_id"] == "r1"
    assert out["meta"]["notes"] == "from_model"


def test_falls_back_after_exhausted_retries():
    client = ScriptedGroq(["{", "not valid", "also bad"])
    out = recommend_with_groq(
        _prefs(),
        _df(),
        top_n=1,
        client=client,
        use_llm=True,
        max_parse_retries=2,
    )
    get_response_validator().validate(out)
    assert out["meta"]["notes"] == "llm_parse_failed"
    assert out["recommendations"][0]["restaurant_id"] == "r1"


def test_llm_zero_rating_dropped_then_deterministic_fallback():
    bad_rating = {
        "recommendations": [
            {
                "restaurant_id": "r1",
                "name": "One",
                "cuisine": "italian",
                "rating": 0,
                "estimated_cost": "medium",
                "ai_rationale": "x",
                "rank": 1,
            }
        ],
        "meta": {"notes": "from_model"},
    }
    client = ScriptedGroq([json.dumps(bad_rating)])
    out = recommend_with_groq(
        _prefs(),
        _df(),
        top_n=2,
        client=client,
        use_llm=True,
        max_parse_retries=0,
    )
    get_response_validator().validate(out)
    assert out["meta"]["notes"] == "llm_ratings_failed_validation"
    assert out["recommendations"][0]["restaurant_id"] == "r1"
    assert out["recommendations"][0]["rating"] == 4.5


def test_llm_below_min_rating_dropped_and_reranked():
    prefs = {"location": "Pune", "budget": "medium", "cuisines": [], "min_rating": 4.3}
    payload = {
        "recommendations": [
            {
                "restaurant_id": "r2",
                "name": "Two",
                "cuisine": "chinese",
                "rating": 4.0,
                "estimated_cost": "medium",
                "ai_rationale": "low",
                "rank": 1,
            },
            {
                "restaurant_id": "r1",
                "name": "One",
                "cuisine": "italian",
                "rating": 4.5,
                "estimated_cost": "medium",
                "ai_rationale": "high",
                "rank": 2,
            },
        ],
        "meta": {"notes": "from_model"},
    }
    client = ScriptedGroq([json.dumps(payload)])
    out = recommend_with_groq(
        prefs,
        _df(),
        top_n=5,
        client=client,
        use_llm=True,
        max_parse_retries=0,
    )
    assert len(out["recommendations"]) == 1
    assert out["recommendations"][0]["restaurant_id"] == "r1"
    assert out["recommendations"][0]["rank"] == 1


def test_missing_restaurant_id_column_raises():
    bad = pd.DataFrame([{"name": "x"}])
    with pytest.raises(ValueError, match="restaurant_id"):
        recommend_with_groq(_prefs(), bad, use_llm=False)
