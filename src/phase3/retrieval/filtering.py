"""Deterministic preference filters on canonical restaurant rows."""

from __future__ import annotations

import os
import re
from typing import Any, Mapping

import pandas as pd

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

# Friendly copy when we add venues from adjacent areas (never whole-city metro widening).
DINING_NEARBY_ALTERNATIVES_NOTE = (
    "We added nearby alternatives just outside your selected area — see the “Nearby alternatives” section."
)
DINING_RELAXED_FILTERS_NOTE = (
    "We broadened things a touch so you still get a strong shortlist of places to try."
)

# Shown when filters leave no rows (including all-null / zero ratings removed before ranking).
EMPTY_SHORTLIST_AFTER_FILTERING_NOTE = (
    "No restaurants with a dependable rating matched these filters. "
    "Try a wider area, a lower minimum rating, fewer cuisines, or a different budget."
)

# When primary (area-flex) matches fall below this count, eligible Bengaluru queries widen to metro city.
_DEFAULT_MIN_PRIMARY = 3


def _min_primary_before_broaden() -> int:
    raw = (os.environ.get("PHASE3_MIN_CANDIDATES_BEFORE_BROADEN") or "").strip()
    if not raw:
        return _DEFAULT_MIN_PRIMARY
    try:
        n = int(raw)
        return max(1, min(n, 50))
    except ValueError:
        return _DEFAULT_MIN_PRIMARY


def validate_canonical_frame(df: pd.DataFrame) -> None:
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"canonical table missing columns: {sorted(missing)}")


def normalize_location_input(raw: str) -> str:
    """Collapse whitespace, strip, lowercase for comparisons."""
    s = re.sub(r"\s+", " ", str(raw).strip()).casefold()
    return s


def _alias_groups() -> tuple[frozenset[str], ...]:
    """Synonymous / typo variants for Bengaluru localities (all normalized)."""
    return (
        frozenset(
            {
                "hsr",
                "hsr layout",
                "hsr layout sector 1",
                "hsr layout sector 2",
                "hsr layout sector 3",
                "hsr layout sector 4",
                "hsr layout sector 5",
                "hsr layout sector 6",
                "hsr layout sector 7",
            }
        ),
        frozenset(
            {
                "ec",
                "electronic city",
                "electronics city",
                "e city",
                "electronic city phase 1",
                "electronic city phase 2",
                "electronic city phase ii",
                "electronic city phase iii",
                "electronic city phase 3",
                "electronic city phase i",
            }
        ),
        frozenset(
            {
                "koramangala",
                "koramngala",
                "koramangla",
                "koramangala 1st block",
                "koramangala 2nd block",
                "koramangala 3rd block",
                "koramangala 4th block",
                "koramangala 5th block",
                "koramangala 6th block",
                "koramangala 7th block",
                "koramangala 8th block",
            }
        ),
        frozenset(
            {
                "whitefield",
                "whitefield main road",
                "brookefield",
                "itpl",
                "kadugodi",
                "varthur",
                "seegehalli",
                "gunjur",
                "graphite india",
            }
        ),
        frozenset(
            {
                "indiranagar",
                "indira nagar",
                "100 feet road",
                "indiranagar 100 feet road",
            }
        ),
        frozenset(
            {
                "bellandur",
                "bellandur gate",
                "bellandur lake",
                "bellandur outer ring road",
            }
        ),
        frozenset(
            {
                "marathahalli",
                "marathahalli bridge",
                "marathahalli junction",
            }
        ),
        frozenset(
            {
                "mg road",
                "mahatma gandhi road",
                "trinity",
                "trinity circle",
                "commercial street",
                "church street",
            }
        ),
        frozenset(
            {
                "jayanagar",
                "jayanagar 3rd block",
                "jayanagar 4th block",
                "jayanagar 7th block",
                "jayanagar 9th block",
                "jp nagar",
                "j p nagar",
            }
        ),
    )


def expand_location_needles(norm: str) -> frozenset[str]:
    """
    Build a set of normalized substrings for flexible locality / city matching.

    Includes the raw normalized input plus any alias group that overlaps the query
    (exact, substring either direction).
    """
    needles: set[str] = set()
    if norm:
        needles.add(norm)
    for group in _alias_groups():
        hit = False
        for member in group:
            if norm == member or (norm and norm in member) or (norm and member in norm):
                hit = True
                break
        if hit:
            needles |= set(group)
    # Drop unsafe ultra-short tokens except known abbreviations handled by groups.
    safe: set[str] = set()
    for n in needles:
        if len(n) >= 3:
            safe.add(n)
        elif n in {"ec", "hsr"}:
            safe.add(n)
    return frozenset(safe)


def _bengaluru_broaden_trigger_roots() -> frozenset[str]:
    """If the query needles intersect this set, nearby-cluster supplement is allowed when primary is thin."""
    parts: set[str] = set()
    for g in _alias_groups():
        parts |= set(g)
    parts.update(
        {
            "bangalore",
            "bengaluru",
            "electronic city",
            "electronics city",
            "koramangala",
            "whitefield",
            "indiranagar",
            "bellandur",
            "marathahalli",
            "jayanagar",
            "mg road",
            "hsr layout",
        }
    )
    return frozenset(parts)


def triggers_bengaluru_nearby_supplement(needles: frozenset[str]) -> bool:
    if not needles:
        return False
    roots = _bengaluru_broaden_trigger_roots()
    if needles & roots:
        return True
    for n in needles:
        for r in roots:
            if len(n) >= 4 and (r in n or n in r):
                return True
    return False


def _nearby_cluster_union_needles() -> tuple[frozenset[str], ...]:
    """
    Bengaluru clusters used only when primary (alias-aware) matches are sparse.

    Each tuple entry is the union of expand_location_needles for a few anchor roots
    in the same commute band so we never fall back to unrelated parts of the city.
    """
    roots_groups: tuple[tuple[str, ...], ...] = (
        ("marathahalli", "bellandur", "whitefield"),
        ("koramangala", "indiranagar", "mg road", "hsr layout", "jayanagar"),
        ("electronic city",),
    )
    out: list[frozenset[str]] = []
    for roots in roots_groups:
        needles: set[str] = set()
        for r in roots:
            needles |= set(expand_location_needles(normalize_location_input(r)))
        out.append(frozenset(needles))
    return tuple(out)


def nearby_supplement_needles(user_norm: str) -> frozenset[str]:
    """
    Extra locality needles for sparse-primary expansion, excluding anything already
    matched by the user's primary alias set.
    """
    primary = set(expand_location_needles(user_norm))
    extra: set[str] = set()
    for cluster in _nearby_cluster_union_needles():
        if primary & cluster:
            extra |= cluster
    extra -= primary
    safe: set[str] = set()
    for n in extra:
        if len(n) >= 3:
            safe.add(n)
        elif n in {"ec", "hsr"}:
            safe.add(n)
    return frozenset(safe)


def _norm_geo_cell(value: Any) -> str:
    """Normalize city/locality: blanks, NaN, 'nan' strings, collapse spaces, casefold."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    t = re.sub(r"\s+", " ", str(value).strip()).casefold()
    if t in ("", "nan", "none", "null"):
        return ""
    return t


def flexible_location_match_mask(df: pd.DataFrame, needles: frozenset[str]) -> pd.Series:
    """
    Partial, case-insensitive location match on ``city`` and ``locality``.

    Matches when any needle equals a field, appears as a substring of ``city`` or
    ``locality``, or when a non-empty ``city``/``locality`` appears inside a longer
    needle (helps when the dataset uses a shorter city label than the user query).
    Rows with only locality populated still match area-style needles.
    """
    city = df["city"].map(_norm_geo_cell)
    if "locality" in df.columns:
        loc = df["locality"].map(_norm_geo_cell)
    else:
        loc = pd.Series("", index=df.index, dtype=object)
    blob = city.str.cat(loc, sep="|")
    m = pd.Series(False, index=df.index)
    for needle in needles:
        if len(needle) < 2:
            continue
        in_city = city.str.contains(needle, regex=False, na=False)
        in_loc = loc.str.contains(needle, regex=False, na=False)
        eq = (city == needle) | (loc == needle)
        blob_hit = blob.str.contains(needle, regex=False, na=False)
        m = m | eq | in_city | in_loc | blob_hit
        # Longer user/needle phrases vs shorter canonical locality (substring both ways).
        if len(needle) >= 4:
            m = m | city.map(lambda c: bool(c) and c in needle)
            m = m | loc.map(lambda lo: bool(lo) and lo in needle)
    return m


def cuisine_cell_to_sequence(cuisines: Any) -> list[Any]:
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
    if not user_tokens:
        return pd.Series(True, index=series.index)

    def hit(cell: Any) -> bool:
        rest = _normalize_cuisine_tokens(cell)
        return bool(user_tokens & rest)

    return series.map(hit)


def numeric_rating_series(df: pd.DataFrame) -> pd.Series:
    """Coerce ``rating`` to float; invalid cells become NaN (matches ``pd.to_numeric(..., errors='coerce')``)."""
    return pd.to_numeric(df["rating"], errors="coerce")


def valid_service_rating_mask(df: pd.DataFrame) -> pd.Series:
    """
    Rows usable for recommendations: finite rating strictly between 0 and 5 (inclusive upper bound).

    Excludes null, NaN, non-numeric, zero, and out-of-range values so they never enter ranking or Phase 4.
    """
    s = numeric_rating_series(df)
    return s.notna() & (s > 0.0) & (s <= 5.0)


def non_location_preference_mask(df: pd.DataFrame, preferences: Mapping[str, Any]) -> pd.Series:
    """Budget, cuisines, and rating: requires a real rating (>0, ≤5) and ``rating >= min_rating`` (inclusive).

    Matches the Next.js home screen: ``min_rating`` is 0–5 from a range input; 0 means no minimum *among
    rated venues*, but rows without a positive rating are still excluded.
    """
    budget = str(preferences["budget"]).strip().casefold()
    band_ok = df["cost_band"].notna() & (
        df["cost_band"].astype(str).str.strip().str.casefold() == budget
    )
    user_tokens = user_cuisine_tokens(preferences)
    cuisine_ok = cuisine_overlap_mask(df["cuisines"], user_tokens)
    s = numeric_rating_series(df)
    min_rating = float(preferences["min_rating"])
    min_rating = max(0.0, min(5.0, min_rating))
    rating_ok = valid_service_rating_mask(df) & (s >= min_rating)
    return band_ok & cuisine_ok & rating_ok


def preference_filter_mask(df: pd.DataFrame, preferences: Mapping[str, Any]) -> pd.Series:
    """
    Boolean mask: flexible location + budget + cuisine + rating.

    Does **not** apply sparse-area nearby supplement; use ``retrieve_candidates`` for that.
    """
    loc_norm = normalize_location_input(str(preferences["location"]))
    needles = expand_location_needles(loc_norm)
    loc_ok = flexible_location_match_mask(df, needles)
    return non_location_preference_mask(df, preferences) & loc_ok


def build_retrieval_location_mask(
    df: pd.DataFrame,
    preferences: Mapping[str, Any],
    *,
    retrieval_meta: dict[str, Any] | None = None,
) -> tuple[pd.Series, pd.Series]:
    """
    Return ``(combined_mask, primary_location_mask)``.

    When primary (alias-aware) area matches are fewer than
    ``PHASE3_MIN_CANDIDATES_BEFORE_BROADEN`` (default 3) and the query looks like a
    Bengaluru neighborhood we recognize, the combined mask may add rows from the same
    **nearby cluster** only (never all of metro Bangalore).

    ``primary_location_mask`` is True only on rows matched by the user's primary needles
    (used for ranking boost and ``location_match_tier``).
    """
    loc_norm = normalize_location_input(str(preferences["location"]))
    needles = expand_location_needles(loc_norm)
    nl = non_location_preference_mask(df, preferences)
    loc_primary = flexible_location_match_mask(df, needles)
    primary = nl & loc_primary
    min_n = _min_primary_before_broaden()
    supplemented = False
    if int(primary.sum()) < min_n and triggers_bengaluru_nearby_supplement(needles):
        sup = nearby_supplement_needles(loc_norm)
        if sup:
            loc_nearby = flexible_location_match_mask(df, sup)
            combined = nl & (loc_primary | loc_nearby)
            if int(combined.sum()) > int(primary.sum()):
                supplemented = True
            mask = combined
        else:
            mask = primary
    else:
        mask = primary

    if retrieval_meta is not None:
        retrieval_meta["location_search_expanded"] = supplemented
        retrieval_meta["dining_match_note"] = DINING_NEARBY_ALTERNATIVES_NOTE if supplemented else ""

    return mask, loc_primary
