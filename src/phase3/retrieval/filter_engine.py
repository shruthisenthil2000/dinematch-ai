"""Orchestrate Phase 3 filtering + ranking (see filtering.py, ranking.py)."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from phase3.retrieval.filtering import (
    REQUIRED_COLUMNS,
    cuisine_cell_to_sequence,
    preference_filter_mask,
    user_cuisine_tokens,
    validate_canonical_frame,
)
from phase3.retrieval.ranking import apply_candidate_cap, retrieval_score_series, sort_candidates_mergesort

# Backward compatibility: public constants and helpers used by other modules/tests.
_cuisine_cell_to_sequence = cuisine_cell_to_sequence


def retrieve_candidates(
    df: pd.DataFrame,
    preferences: Mapping[str, Any],
    *,
    cap: int = 25,
) -> pd.DataFrame:
    """
    Apply structured filters, rank deterministically, return at most ``cap`` rows.

    ``preferences`` matches ``schemas/user-preferences.schema.json`` (after
    validation): ``location``, ``budget``, ``cuisines``, ``min_rating``.

    Rules:
    - **City:** case-insensitive equality on ``city`` vs ``location``.
    - **Budget:** ``cost_band`` must equal ``budget``; rows with null ``cost_band`` excluded.
    - **Cuisines:** empty ``cuisines`` → no cuisine filter; otherwise at least one
      token overlap (case-insensitive) between user list and row ``cuisines``.
    - **Min rating:** ``min_rating`` <= 0 → no rating floor; else require
      non-null ``rating`` >= ``min_rating``.

    Sort order (stable): ``retrieval_score`` desc, ``votes`` desc (null as 0),
    ``rating`` desc (null as -1), ``restaurant_id`` asc. Same inputs and frame
    always yield the same row order.
    """
    if cap < 1:
        raise ValueError("cap must be >= 1")
    validate_canonical_frame(df)

    work = df.copy()
    mask = preference_filter_mask(work, preferences)
    filtered = work[mask].copy()
    user_tokens = user_cuisine_tokens(preferences)
    filtered["retrieval_score"] = retrieval_score_series(filtered, user_tokens)
    filtered = sort_candidates_mergesort(filtered)
    return apply_candidate_cap(filtered, cap)
