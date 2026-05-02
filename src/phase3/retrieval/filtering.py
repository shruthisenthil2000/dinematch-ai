"""Deterministic preference filters on canonical restaurant rows (Phase 3)."""

from __future__ import annotations

from typing import Any, Mapping

import pandas as pd

# Columns required for Phase 3 filtering (Phase 1 canonical output).
REQUIRED_COLUMNS = frozenset(
    {
        "restaurant_id",
        "name",
        "city",
        "cuisines",
        "rating",
        "votes",
        "cost_band",
    }
)


def validate_canonical_frame(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"canonical table missing columns: {sorted(missing)}")


def _normalize_city(value: str) -> str:
    return str(value).strip().casefold()


def cuisine_cell_to_sequence(cuisines: Any) -> list[Any]:
    """Normalize list-like cells (including ndarray after Parquet) to a Python list."""
    if cuisines is None or (isinstance(cuisines, float) and pd.isna(cuisines)):
        return []
    if isinstance(cuisines, (list, tuple)):
        return list(cuisines)
    if hasattr(cuisines, "tolist") and not isinstance(cuisines, (str, bytes)):
        raw = cuisines.tolist()
        if isinstance(raw, list):
            return raw
        return [raw]
    return [cuisines]


def _normalize_cuisine_tokens(cuisines: Any) -> set[str]:
    seq = cuisine_cell_to_sequence(cuisines)
    return {str(c).strip().casefold() for c in seq if str(c).strip()}


def user_cuisine_tokens(preferences: Mapping[str, Any]) -> set[str]:
    raw = preferences.get("cuisines") or []
    if not isinstance(raw, list):
        return set()
    return {str(c).strip().casefold() for c in raw if str(c).strip()}


def cuisine_overlap_mask(series: pd.Series, user_tokens: set[str]) -> pd.Series:
    """True when user has no cuisine filter, else at least one overlapping token."""
    if not user_tokens:
        return pd.Series(True, index=series.index)

    def hit(cell: Any) -> bool:
        rest = _normalize_cuisine_tokens(cell)
        return bool(user_tokens & rest)

    return series.map(hit)


def preference_filter_mask(df: pd.DataFrame, preferences: Mapping[str, Any]) -> pd.Series:
    """
    Boolean mask: location (city), budget band, cuisine overlap, min rating.

    Same semantics as ``retrieve_candidates`` in ``filter_engine``.
    """
    loc = _normalize_city(str(preferences["location"]))
    budget = str(preferences["budget"]).strip().casefold()

    city_match = df["city"].astype(str).str.strip().str.casefold() == loc
    if "locality" in df.columns:
        locality_match = df["locality"].astype(str).str.strip().str.casefold() == loc
        city_ok = city_match | locality_match
    else:
        city_ok = city_match
    band_ok = df["cost_band"].notna() & (
        df["cost_band"].astype(str).str.strip().str.casefold() == budget
    )

    user_tokens = user_cuisine_tokens(preferences)
    cuisine_ok = cuisine_overlap_mask(df["cuisines"], user_tokens)

    min_rating = float(preferences["min_rating"])
    if min_rating <= 0:
        rating_ok = pd.Series(True, index=df.index)
    else:
        rating_ok = df["rating"].notna() & (df["rating"].astype(float) >= min_rating)

    return city_ok & band_ok & cuisine_ok & rating_ok
