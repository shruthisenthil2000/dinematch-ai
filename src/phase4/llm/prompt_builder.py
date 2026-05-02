"""Build prompts: user preferences + compact candidate table + JSON output rules."""

from __future__ import annotations

import json
from typing import Any, Mapping

import pandas as pd

from phase3.retrieval.filtering import cuisine_cell_to_sequence


def dataframe_to_candidate_dicts(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Turn a Phase 3 candidate frame into compact JSON-serializable rows for the LLM."""
    rows: list[dict[str, Any]] = []
    for _, r in df.iterrows():
        cuisines = cuisine_cell_to_sequence(r.get("cuisines"))
        rating = r.get("rating")
        cost_band = r.get("cost_band")
        approx = r.get("approx_cost_for_two")
        votes = r.get("votes")
        rows.append(
            {
                "restaurant_id": str(r["restaurant_id"]),
                "name": str(r["name"]),
                "city": str(r.get("city", "")),
                "cuisines": [str(c) for c in cuisines],
                "rating": None if rating is None or (isinstance(rating, float) and pd.isna(rating)) else float(rating),
                "cost_band": None
                if cost_band is None or (isinstance(cost_band, float) and pd.isna(cost_band))
                else str(cost_band),
                "approx_cost_for_two": None
                if approx is None or (isinstance(approx, float) and pd.isna(approx))
                else float(approx),
                "votes": None
                if votes is None or (isinstance(votes, float) and pd.isna(votes))
                else int(votes),
            }
        )
    return rows


def build_recommendation_prompt(
    preferences: Mapping[str, Any],
    candidates: list[dict[str, Any]],
    *,
    top_n: int,
) -> str:
    """
    User message body: preferences JSON, candidate table, guardrails, strict JSON schema hints.

    The model must return JSON only (optionally wrapped in a markdown fence) matching
    ``schemas/recommendation-response.schema.json``.
    """
    allowed_ids = [c["restaurant_id"] for c in candidates]
    prefs_json = json.dumps(dict(preferences), indent=2, sort_keys=True)
    cand_json = json.dumps(candidates, indent=2, sort_keys=True)

    return f"""You are ranking restaurants for a user. Use ONLY the candidates below. Do not invent restaurants or IDs.

## User preferences (JSON)
{prefs_json}

## Candidate restaurants (JSON). You MUST only use restaurant_id values from this list:
{json.dumps(allowed_ids)}

## Candidates (full rows)
{cand_json}

## Rules
1. Recommend at most {top_n} restaurants, ordered best-first (rank 1 = best).
2. Each recommendation object MUST include: restaurant_id, name, cuisine (string), rating (number 0-5), estimated_cost (short human-readable string from cost_band and/or approx_cost_for_two), ai_rationale (non-empty), rank (integer >= 1).
3. restaurant_id and name MUST match the candidate row exactly.
4. cuisine should summarize the candidate's cuisines field for display.
5. estimated_cost should reflect data (e.g. band label and optional INR hint); do not invent prices not supported by the row.
6. Output a single JSON object with key "recommendations" (array). You may include optional keys "comparative_summary" (string) and "meta" (object).
7. Return ONLY the JSON object (no commentary), or wrap it in a ```json code block.

If no candidate is suitable, return {{"recommendations": []}}.
"""
