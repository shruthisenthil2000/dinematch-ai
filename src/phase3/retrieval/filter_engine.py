"""Orchestrate Phase 3 filtering + ranking (see filtering.py, ranking.py)."""

from __future__ import annotations

import os
from typing import Any, Mapping

import pandas as pd

from phase3.retrieval.filtering import (
    DINING_RELAXED_FILTERS_NOTE,
    build_retrieval_location_mask,
    cuisine_cell_to_sequence,
    expand_location_needles,
    normalize_location_input,
    triggers_bengaluru_metro_broaden,
    user_cuisine_tokens,
    validate_canonical_frame,
)
from phase3.retrieval.ranking import apply_candidate_cap, retrieval_score_series, sort_candidates_mergesort

# Backward compatibility: public constants and helpers used by other modules/tests.
_cuisine_cell_to_sequence = cuisine_cell_to_sequence


def _target_min_candidates() -> int:
    raw = (os.environ.get("PHASE3_TARGET_MIN_CANDIDATES") or "").strip()
    if not raw:
        return 3
    try:
        return max(1, min(int(raw), 50))
    except ValueError:
        return 3


def _effective_preferences(preferences: Mapping[str, Any]) -> dict[str, Any]:
    d = dict(preferences)
    c = d.get("cuisines")
    d["cuisines"] = list(c) if isinstance(c, list) else []
    return d


def retrieve_candidates(
    df: pd.DataFrame,
    preferences: Mapping[str, Any],
    *,
    cap: int = 25,
    retrieval_meta: dict[str, Any] | None = None,
) -> pd.DataFrame:
    """
    Apply structured filters, rank deterministically, return at most ``cap`` rows.

    Location uses partial, case-insensitive matching on ``city`` and ``locality`` with
    Bengaluru alias expansion. If matches are sparse, metro-wide broadening may apply.
    If the candidate pool is still below ``PHASE3_TARGET_MIN_CANDIDATES`` (default 3),
    ``min_rating`` is stepped down and then cuisine filters are cleared—without
    changing the original request object passed in by callers.
    """
    if cap < 1:
        raise ValueError("cap must be >= 1")
    validate_canonical_frame(df)

    work = df.copy()
    prefs_eff = _effective_preferences(preferences)
    target_min = _target_min_candidates()
    relax_rounds = 0
    needles = expand_location_needles(normalize_location_input(str(preferences.get("location", ""))))
    can_relax = triggers_bengaluru_metro_broaden(needles)
    mask, loc_primary = build_retrieval_location_mask(work, prefs_eff, retrieval_meta=retrieval_meta)
    while can_relax and int(mask.sum()) < target_min and relax_rounds < 16:
        changed = False
        mr = float(prefs_eff.get("min_rating") or 0.0)
        if mr > 0.0:
            prefs_eff["min_rating"] = max(0.0, mr - 0.5)
            changed = True
        elif prefs_eff.get("cuisines"):
            prefs_eff["cuisines"] = []
            changed = True
        else:
            break
        if changed:
            relax_rounds += 1
            mask, loc_primary = build_retrieval_location_mask(work, prefs_eff, retrieval_meta=retrieval_meta)

    if retrieval_meta is not None and relax_rounds > 0:
        note = str(retrieval_meta.get("dining_match_note") or "").strip()
        extra = DINING_RELAXED_FILTERS_NOTE
        if extra.lower() not in note.lower():
            retrieval_meta["dining_match_note"] = f"{note} {extra}".strip() if note else extra
        retrieval_meta["filters_relaxed"] = True

    filtered = work[mask].copy()
    if len(filtered) == 0:
        return apply_candidate_cap(filtered, cap)

    user_tokens = user_cuisine_tokens(preferences)
    filtered["retrieval_score"] = retrieval_score_series(filtered, user_tokens)
    tier = loc_primary.loc[filtered.index].astype(float)
    filtered["retrieval_score"] = filtered["retrieval_score"] + tier * 8.0
    filtered = sort_candidates_mergesort(filtered)
    return apply_candidate_cap(filtered, cap)
