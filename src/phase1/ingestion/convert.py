from __future__ import annotations

import hashlib
from typing import Any

import pandas as pd

from phase1.ingestion.constants import RAW_COST_COL, RAW_CITY_COL, RAW_LOCALITY_COL
from phase1.ingestion.normalize import (
    _strip,
    normalize_yes_no,
    parse_approx_cost_for_two,
    parse_rating,
    parse_votes,
    split_cuisines,
)


def restaurant_id(url: Any, name: str, city: str, locality: str) -> str:
    u = _strip(url)
    key = u if u else f"{name}|{city}|{locality}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def raw_to_canonical(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw Hugging Face / CSV rows to canonical columns (dataset_contract.md)."""
    out = pd.DataFrame()
    out["name"] = df["name"].map(lambda x: _strip(x))
    out["city"] = df[RAW_CITY_COL].map(lambda x: _strip(x).title() if _strip(x) else "")
    out["locality"] = df[RAW_LOCALITY_COL].map(lambda x: _strip(x))
    out["cuisines"] = df["cuisines"].map(split_cuisines)
    out["rating"] = df["rate"].map(parse_rating)
    out["votes"] = df["votes"].map(parse_votes)
    out["approx_cost_for_two"] = df[RAW_COST_COL].map(parse_approx_cost_for_two)
    out["rest_type"] = df["rest_type"].map(lambda x: _strip(x) or None)
    out["online_order"] = df["online_order"].map(normalize_yes_no)
    out["book_table"] = df["book_table"].map(normalize_yes_no)
    out["url"] = df["url"].map(lambda x: _strip(x) or None)
    out["address"] = df["address"].map(lambda x: _strip(x) or None)
    out["restaurant_id"] = [
        restaurant_id(df["url"].iloc[i], out["name"].iloc[i], out["city"].iloc[i], out["locality"].iloc[i])
        for i in range(len(out))
    ]
    return out


def assign_cost_bands(
    approx_cost: pd.Series,
    *,
    q1: float | None = None,
    q2: float | None = None,
) -> tuple[pd.Series, dict[str, float | str | None]]:
    """
    Assign low / medium / high from global tertiles on non-null costs.
    Returns (band series, manifest fragment with q1, q2 and method).
    """
    valid = approx_cost.dropna()
    method = "global_tertiles"
    if len(valid) < 10:
        method = "fixed_fallback_inr"
        q1, q2 = 400.0, 800.0
    elif q1 is None or q2 is None:
        q1 = float(valid.quantile(1 / 3))
        q2 = float(valid.quantile(2 / 3))
        if q1 >= q2:
            method = "fixed_fallback_inr_equal_quantiles"
            q1, q2 = 400.0, 800.0

    def band(v: Any) -> str | None:
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return None
        fv = float(v)
        if fv <= q1:
            return "low"
        if fv <= q2:
            return "medium"
        return "high"

    bands = approx_cost.map(band)
    meta: dict[str, float | str | None] = {
        "method": method,
        "q1_cutoff": float(q1),
        "q2_cutoff": float(q2),
        "low": f"approx_cost_for_two <= {q1}",
        "medium": f"{q1} < approx_cost_for_two <= {q2}",
        "high": f"approx_cost_for_two > {q2}",
    }
    return bands, meta
