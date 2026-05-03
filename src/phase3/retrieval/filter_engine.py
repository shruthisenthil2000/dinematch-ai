"""Orchestrate Phase 3 filtering + ranking (see filtering.py, ranking.py)."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

from phase3.retrieval.filtering import (
    REQUIRED_COLUMNS,
    build_retrieval_location_mask,
    cuisine_cell_to_sequence,
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
    retrieval_meta: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Apply structured filters, rank deterministically, return at most ``cap`` rows.

    ``preferences`` matches ``schemas/user-preferences.schema.json`` (after
    validation): ``location``, ``budget``, ``cuisines``, ``min_rating``.

    Location:
    - Normalized whitespace/case; flexible substring match on ``city`` and ``locality``.
    - Alias expansion for common Bengaluru areas (e.g. HSR ↔ HSR Layout, EC ↔ Electronic City).
    - If primary area matches are sparse, eligible Bengaluru queries widen to metro ``city``
      matches while keeping budget / cuisine / rating filters; closer area matches rank higher.

    Other rules:
    - **Budget:** ``cost_band`` must equal ``budget``; null ``cost_band`` excluded.
    - **Cuisines:** empty → no cuisine filter; else at least one overlapping token.
    - **Min rating:** ``<= 0`` → no floor; else non-null ``rating >= min_rating``.

    Sort: ``retrieval_score`` (with primary-location boost), then stable tie-breaks.

    If ``retrieval_meta`` is a dict, it may receive keys ``location_search_expanded`` (bool)
    and ``dining_match_note`` (customer-facing str, empty when not expanded).
    """
    if cap < 1:
        raise ValueError("cap must be >= 1")
    validate_canonical_frame(df)

    work = df.copy()
    mask, loc_primary = build_retrieval_location_mask(work, preferences, retrieval_meta=retrieval_meta)
    filtered = work[mask].copy()
    if len(filtered) == 0:
        return apply_candidate_cap(filtered, cap)

    user_tokens = user_cuisine_tokens(preferences)
    filtered["retrieval_score"] = retrieval_score_series(filtered, user_tokens)
    # Prefer rows that matched the requested area before any metro-wide broadening.
    tier = loc_primary.loc[filtered.index].astype(float)
    filtered["retrieval_score"] = filtered["retrieval_score"] + tier * 8.0
    filtered = sort_candidates_mergesort(filtered)
    return apply_candidate_cap(filtered, cap)
