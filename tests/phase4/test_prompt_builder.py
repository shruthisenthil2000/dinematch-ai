"""Phase 4 prompt construction."""

from __future__ import annotations

import pandas as pd

from phase4.llm.prompt_builder import build_recommendation_prompt, dataframe_to_candidate_dicts


def _row(rid, name, city, cuisines, rating, band):
    return {
        "restaurant_id": rid,
        "name": name,
        "city": city,
        "locality": "l",
        "cuisines": cuisines,
        "rating": rating,
        "votes": 1,
        "approx_cost_for_two": 500.0,
        "cost_band": band,
        "rest_type": None,
        "online_order": None,
        "book_table": None,
        "url": None,
        "address": None,
    }


def test_dataframe_to_candidate_dicts_shape():
    df = pd.DataFrame([_row("a", "N", "Pune", ["italian"], 4.2, "medium")])
    rows = dataframe_to_candidate_dicts(df)
    assert rows[0]["restaurant_id"] == "a"
    assert rows[0]["locality"] == "l"
    assert rows[0]["cuisines"] == ["italian"]
    assert rows[0]["rating"] == 4.2


def test_build_prompt_lists_allowed_ids():
    prefs = {"location": "Pune", "budget": "medium", "cuisines": [], "min_rating": 0.0}
    cands = [{"restaurant_id": "x1", "name": "A", "city": "Pune", "cuisines": [], "rating": 4.0, "cost_band": "medium", "approx_cost_for_two": 400.0, "votes": 1}]
    text = build_recommendation_prompt(prefs, cands, top_n=3)
    assert "x1" in text
    assert "ONLY" in text or "only" in text.lower()
    assert "JSON" in text
