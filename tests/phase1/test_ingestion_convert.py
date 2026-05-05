"""Tests for phase1.ingestion.convert (canonical mapping, ids, cost bands)."""

from __future__ import annotations

import pandas as pd
import pytest

from phase1.ingestion.constants import (
    EXPECTED_RAW_COLUMNS,
    RAW_COST_COL,
    RAW_CITY_COL,
    RAW_LOCALITY_COL,
)
from phase1.ingestion.convert import assign_cost_bands, canonical_city_locality, raw_to_canonical, restaurant_id


def _minimal_raw_df(rows: list[dict]) -> pd.DataFrame:
    """Build a raw-shaped DataFrame with all contract columns (values from base + overrides)."""
    base = {c: "" for c in EXPECTED_RAW_COLUMNS}
    out_rows = []
    for r in rows:
        row = {**base, **r}
        out_rows.append([row[c] for c in EXPECTED_RAW_COLUMNS])
    return pd.DataFrame(out_rows, columns=list(EXPECTED_RAW_COLUMNS))


def test_raw_to_canonical_maps_fields_and_title_cases_city():
    df = _minimal_raw_df(
        [
            {
                "name": "  Cafe  ",
                RAW_CITY_COL: "bangalore",
                RAW_LOCALITY_COL: " koramangala ",
                "cuisines": "Italian, Thai",
                "rate": "4.0/5",
                "votes": "99",
                RAW_COST_COL: "500",
                "rest_type": " Casual ",
                "online_order": "Yes",
                "book_table": "No",
                "url": "https://example.com/x",
                "address": " 1 St ",
            }
        ]
    )
    canon = raw_to_canonical(df)
    assert len(canon) == 1
    assert canon.iloc[0]["name"] == "Cafe"
    assert canon.iloc[0]["city"] == "Bengaluru"
    assert canon.iloc[0]["locality"] == "koramangala"
    assert canon.iloc[0]["cuisines"] == ["italian", "thai"]
    assert canon.iloc[0]["rating"] == 4.0
    assert canon.iloc[0]["votes"] == 99
    assert canon.iloc[0]["approx_cost_for_two"] == 500.0
    assert canon.iloc[0]["rest_type"] == "Casual"
    assert canon.iloc[0]["online_order"] == True  # noqa: E712 — numpy.bool_ vs `is True`
    assert canon.iloc[0]["book_table"] == False  # noqa: E712
    assert canon.iloc[0]["url"] == "https://example.com/x"
    assert canon.iloc[0]["address"] == "1 St"


def test_raw_to_canonical_uses_fallback_restaurant_id_when_url_empty():
    df = _minimal_raw_df(
        [
            {
                "name": "N",
                RAW_CITY_COL: "Delhi",
                RAW_LOCALITY_COL: "CP",
                "url": "",
            }
        ]
    )
    canon = raw_to_canonical(df)
    expected = restaurant_id("", "N", "Delhi", "CP")
    assert canon.iloc[0]["restaurant_id"] == expected


def test_raw_to_canonical_null_rating_and_cost_become_none():
    df = _minimal_raw_df(
        [
            {
                "name": "X",
                RAW_CITY_COL: "Mumbai",
                RAW_LOCALITY_COL: "L",
                "rate": "NEW",
                RAW_COST_COL: "-",
                "votes": "",
            }
        ]
    )
    canon = raw_to_canonical(df)
    assert canon.iloc[0]["rating"] is None
    assert canon.iloc[0]["approx_cost_for_two"] is None
    assert canon.iloc[0]["votes"] is None


def test_canonical_city_locality_maps_bengaluru_area_labels_safely():
    city, locality = canonical_city_locality("Koramangala 5th Block", "HSR")
    assert city == "Bengaluru"
    assert locality == "HSR"


def test_canonical_city_locality_preserves_non_bengaluru_city():
    city, locality = canonical_city_locality("Pune", "Baner")
    assert city == "Pune"
    assert locality == "Baner"


def test_raw_to_canonical_ignores_extra_columns_without_error():
    """raw_to_canonical only reads known columns; extra columns do not break mapping."""
    df = _minimal_raw_df([{"name": "A", RAW_CITY_COL: "C", RAW_LOCALITY_COL: "L"}])
    df["extra_debug_col"] = ["ignored"]
    canon = raw_to_canonical(df)
    assert "extra_debug_col" not in canon.columns
    assert len(canon) == 1


def test_raw_to_canonical_missing_required_raw_column_raises():
    df = pd.DataFrame({"name": ["a"], "rate": ["4"]})
    with pytest.raises(KeyError):
        raw_to_canonical(df)


def test_assign_cost_bands_fixed_fallback_when_few_samples():
    costs = pd.Series([100.0, 200.0, 300.0])
    bands, meta = assign_cost_bands(costs)
    assert meta["method"] == "fixed_fallback_inr"
    assert list(bands) == ["low", "low", "low"]


def test_assign_cost_bands_global_tertiles_when_enough_samples():
    costs = pd.Series([100.0 * i for i in range(1, 11)])
    bands, meta = assign_cost_bands(costs)
    assert meta["method"] == "global_tertiles"
    assert meta["q1_cutoff"] < meta["q2_cutoff"]
    assert len(bands) == 10


def test_assign_cost_bands_null_cost_gets_none_band():
    costs = pd.Series([100.0, None, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1100.0, 1200.0])
    bands, _ = assign_cost_bands(costs)
    assert pd.isna(bands.iloc[1]) or bands.iloc[1] is None
