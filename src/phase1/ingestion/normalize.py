from __future__ import annotations

import re
from typing import Any

import pandas as pd

from phase1.ingestion.constants import EXPECTED_RAW_COLUMNS

_WS = re.compile(r"\s+")
_RATE = re.compile(r"(\d+\.?\d*)\s*(?:/\s*5)?")
_NON_NUMERIC_COST = re.compile(r"[^\d.]")


def _strip(s: Any) -> str:
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return ""
    return str(s).strip()


def parse_rating(raw: Any) -> float | None:
    s = _strip(raw).upper()
    if not s or s in {"-", "NEW", "NAN", "NONE"}:
        return None
    m = _RATE.search(s.replace(" ", ""))
    if not m:
        return None
    val = float(m.group(1))
    if val < 0 or val > 5:
        return None
    return val


def parse_approx_cost_for_two(raw: Any) -> float | None:
    s = _strip(raw)
    if not s or s in {"-", "NAN"}:
        return None
    digits = _NON_NUMERIC_COST.sub("", s.split(".")[0] if s else "")
    if not digits:
        # e.g. "800 for two" might leave digits after strip - try full string
        m = re.search(r"(\d{2,6})", s.replace(",", ""))
        if not m:
            return None
        digits = m.group(1)
    try:
        return float(digits)
    except ValueError:
        return None


def parse_votes(raw: Any) -> int | None:
    s = _strip(raw).replace(",", "")
    if not s or not s.isdigit():
        return None
    return int(s)


def split_cuisines(raw: Any) -> list[str]:
    s = _strip(raw)
    if not s:
        return []
    parts = [p.strip().lower() for p in s.split(",")]
    return [p for p in parts if p]


def normalize_yes_no(raw: Any) -> bool | None:
    s = _strip(raw).lower()
    if not s or s in {"-", "nan"}:
        return None
    if s in {"yes", "y", "true", "1"}:
        return True
    if s in {"no", "n", "false", "0"}:
        return False
    return None


def validate_and_order_raw_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all expected columns exist (exact names); reorder to match dataset_contract.md order."""
    cols = set(df.columns)
    expected = list(EXPECTED_RAW_COLUMNS)
    missing = [c for c in expected if c not in cols]
    extra = [c for c in cols if c not in expected]
    if missing or extra:
        msg = ["Raw CSV schema drift vs contracts/dataset_contract.md."]
        if missing:
            msg.append(f"Missing columns: {missing}")
        if extra:
            msg.append(f"Unexpected columns: {extra}")
        raise ValueError("\n".join(msg))
    return df[list(expected)].copy()


def drop_unusable_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove rows without name or city (cannot satisfy user location matching)."""
    mask = df["name"].str.len() > 0
    mask &= df["city"].str.len() > 0
    return df.loc[mask].reset_index(drop=True)


def deduplicate_restaurants(df: pd.DataFrame) -> pd.DataFrame:
    """
    Same name + city + locality: keep one row — prefer higher rating, then more votes.
    """
    if df.empty:
        return df
    sort_keys = ["rating", "votes"]
    ascending = [False, False]
    sorted_df = df.sort_values(sort_keys, ascending=ascending, na_position="last")
    subset = ["name", "city", "locality"]
    return sorted_df.drop_duplicates(subset=subset, keep="first").reset_index(drop=True)
