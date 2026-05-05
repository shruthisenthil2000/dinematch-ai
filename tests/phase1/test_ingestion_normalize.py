"""Tests for phase1.ingestion.normalize (parsers, validate/order, drop, dedupe)."""

from __future__ import annotations

import pandas as pd
import pytest

from phase1.ingestion.constants import EXPECTED_RAW_COLUMNS
from phase1.ingestion.normalize import (
    deduplicate_restaurants,
    drop_unusable_rows,
    normalize_yes_no,
    parse_approx_cost_for_two,
    parse_rating,
    parse_votes,
    split_cuisines,
    validate_and_order_raw_columns,
)


def _strip(s):
    """Mirror production _strip via parsers (not exported)."""
    from phase1.ingestion.normalize import _strip as strip_fn

    return strip_fn(s)


def test_strip_trims_whitespace_and_handles_null_like_values():
    assert _strip("  hello  ") == "hello"
    assert _strip(None) == ""
    assert _strip(float("nan")) == ""
    assert _strip("") == ""


def test_parse_rating_trims_and_parses_fraction_form():
    assert parse_rating("  4.2/5  ") == 4.2
    assert parse_rating("3/5") == 3.0


def test_parse_rating_null_safe_for_missing_or_sentinel_strings():
    assert parse_rating(None) is None
    assert parse_rating("") is None
    assert parse_rating("-") is None
    assert parse_rating("NEW") is None
    assert parse_rating("not-a-rating") is None


def test_parse_rating_rejects_out_of_range_numeric():
    assert parse_rating("6/5") is None


def test_parse_approx_cost_strips_noise_and_handles_missing():
    assert parse_approx_cost_for_two("  ₹800  ") == 800.0
    assert parse_approx_cost_for_two(None) is None
    assert parse_approx_cost_for_two("-") is None


def test_parse_votes_handles_commas_and_rejects_non_numeric():
    assert parse_votes(" 1,234 ") == 1234
    assert parse_votes("") is None
    assert parse_votes("abc") is None


def test_split_cuisines_trims_lowercases_and_empty():
    assert split_cuisines(" Italian , Chinese ") == ["italian", "chinese"]
    assert split_cuisines("") == []
    assert split_cuisines(None) == []


def test_normalize_yes_no_standardizes_known_tokens():
    assert normalize_yes_no(" YES ") is True
    assert normalize_yes_no("no") is False
    assert normalize_yes_no("maybe") is None
    assert normalize_yes_no("") is None


def test_validate_and_order_reorders_columns_to_contract_order():
    cols = list(EXPECTED_RAW_COLUMNS)
    data = {c: [c] for c in cols}
    df = pd.DataFrame(data)
    df = df[[c for c in reversed(cols)]]
    out = validate_and_order_raw_columns(df)
    assert list(out.columns) == list(EXPECTED_RAW_COLUMNS)


def test_validate_and_order_raises_on_extra_columns():
    cols = list(EXPECTED_RAW_COLUMNS)
    data = {c: [""] for c in cols}
    data["unexpected_extra"] = ["x"]
    df = pd.DataFrame(data)
    with pytest.raises(ValueError, match="Unexpected columns"):
        validate_and_order_raw_columns(df)


def test_validate_and_order_raises_on_missing_columns():
    df = pd.DataFrame({"name": ["a"], "url": [""]})
    with pytest.raises(ValueError, match="Missing columns"):
        validate_and_order_raw_columns(df)


def test_drop_unusable_rows_removes_empty_name_or_city():
    df = pd.DataFrame(
        [
            {"name": "A", "city": "X", "locality": "L"},
            {"name": "", "city": "X", "locality": "L"},
            {"name": "B", "city": "", "locality": "L"},
            {"name": "C", "city": "Y", "locality": "L"},
        ]
    )
    out = drop_unusable_rows(df)
    assert len(out) == 2
    assert set(out["name"]) == {"A", "C"}


def test_drop_unusable_rows_removes_null_heavy_rows():
    df = pd.DataFrame(
        [
            {
                "name": "KeptByRating",
                "city": "Bengaluru",
                "locality": "",
                "cuisines": [],
                "rating": 4.1,
                "approx_cost_for_two": None,
            },
            {
                "name": "DropMe",
                "city": "Bengaluru",
                "locality": "",
                "cuisines": [],
                "rating": None,
                "approx_cost_for_two": None,
            },
        ]
    )
    out = drop_unusable_rows(df)
    assert list(out["name"]) == ["KeptByRating"]


def test_deduplicate_restaurants_keeps_higher_rating_then_votes():
    df = pd.DataFrame(
        [
            {"name": "Same", "city": "C", "locality": "L", "rating": 3.0, "votes": 100},
            {"name": "Same", "city": "C", "locality": "L", "rating": 4.5, "votes": 1},
            {"name": "Same", "city": "C", "locality": "L", "rating": 4.5, "votes": 50},
            {"name": "Other", "city": "C", "locality": "L", "rating": 2.0, "votes": 1},
        ]
    )
    out = deduplicate_restaurants(df)
    assert len(out) == 2
    dup = out[(out["name"] == "Same") & (out["city"] == "C")]
    assert len(dup) == 1
    assert dup.iloc[0]["rating"] == 4.5
    assert dup.iloc[0]["votes"] == 50


def test_deduplicate_empty_frame_returns_empty():
    df = pd.DataFrame(columns=["name", "city", "locality", "rating", "votes"])
    out = deduplicate_restaurants(df)
    assert len(out) == 0
