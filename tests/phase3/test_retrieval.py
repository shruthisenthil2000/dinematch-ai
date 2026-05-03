"""Phase 3 deterministic filtering and ranking."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from phase3.retrieval import load_canonical_parquet, retrieve_candidates


def _minimal_row(
    *,
    restaurant_id: str,
    name: str,
    city: str,
    cuisines: list[str],
    rating: float | None,
    votes: int | None,
    cost_band: str | None,
) -> dict:
    return {
        "restaurant_id": restaurant_id,
        "name": name,
        "city": city,
        "locality": "x",
        "cuisines": cuisines,
        "rating": rating,
        "votes": votes,
        "approx_cost_for_two": 500.0,
        "cost_band": cost_band,
        "rest_type": None,
        "online_order": None,
        "book_table": None,
        "url": None,
        "address": None,
    }


def _prefs(**kwargs):
    base = {
        "location": "Pune",
        "budget": "medium",
        "cuisines": [],
        "min_rating": 0.0,
    }
    base.update(kwargs)
    return base


def test_missing_required_column_raises():
    df = pd.DataFrame([{"restaurant_id": "a", "name": "n", "city": "Pune"}])
    with pytest.raises(ValueError, match="missing columns"):
        retrieve_candidates(df, _prefs(), cap=5)


def test_city_case_insensitive():
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="1",
                name="A",
                city="Pune",
                cuisines=["italian"],
                rating=4.0,
                votes=10,
                cost_band="medium",
            ),
            _minimal_row(
                restaurant_id="2",
                name="B",
                city="Mumbai",
                cuisines=["italian"],
                rating=5.0,
                votes=20,
                cost_band="medium",
            ),
        ]
    )
    out = retrieve_candidates(df, _prefs(location="pune"), cap=10)
    assert len(out) == 1
    assert out.iloc[0]["restaurant_id"] == "1"


def test_location_matches_locality_when_city_differs():
    """User may enter an area (locality) while canonical city is wider (e.g. Bangalore / Bellandur)."""
    df = pd.DataFrame(
        [
            {
                **_minimal_row(
                    restaurant_id="1",
                    name="A",
                    city="Bangalore",
                    cuisines=["italian"],
                    rating=4.0,
                    votes=10,
                    cost_band="medium",
                ),
                "locality": "Bellandur",
            },
            {
                **_minimal_row(
                    restaurant_id="2",
                    name="B",
                    city="Bangalore",
                    cuisines=["italian"],
                    rating=5.0,
                    votes=20,
                    cost_band="medium",
                ),
                "locality": "Koramangala",
            },
        ]
    )
    out = retrieve_candidates(df, _prefs(location="bellandur"), cap=10)
    assert len(out) == 1
    assert out.iloc[0]["restaurant_id"] == "1"


def test_budget_and_null_cost_band_excluded():
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="1",
                name="A",
                city="Pune",
                cuisines=[],
                rating=4.0,
                votes=1,
                cost_band="medium",
            ),
            _minimal_row(
                restaurant_id="2",
                name="B",
                city="Pune",
                cuisines=[],
                rating=4.5,
                votes=2,
                cost_band=None,
            ),
        ]
    )
    out = retrieve_candidates(df, _prefs(budget="medium"), cap=10)
    assert list(out["restaurant_id"]) == ["1"]


def test_cuisine_filter_requires_overlap_when_nonempty():
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="1",
                name="A",
                city="Pune",
                cuisines=["chinese"],
                rating=4.0,
                votes=1,
                cost_band="low",
            ),
            _minimal_row(
                restaurant_id="2",
                name="B",
                city="Pune",
                cuisines=["italian", "chinese"],
                rating=3.5,
                votes=5,
                cost_band="low",
            ),
        ]
    )
    out = retrieve_candidates(df, _prefs(budget="low", cuisines=["Italian"]), cap=10)
    # Row 1 is Chinese-only; row 2 includes Italian.
    assert set(out["restaurant_id"]) == {"2"}

    out_none = retrieve_candidates(df, _prefs(budget="low", cuisines=["Mexican"]), cap=10)
    assert len(out_none) == 0


def test_min_rating_excludes_null_and_low():
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="1",
                name="A",
                city="Pune",
                cuisines=[],
                rating=None,
                votes=1,
                cost_band="low",
            ),
            _minimal_row(
                restaurant_id="2",
                name="B",
                city="Pune",
                cuisines=[],
                rating=3.9,
                votes=2,
                cost_band="low",
            ),
            _minimal_row(
                restaurant_id="3",
                name="C",
                city="Pune",
                cuisines=[],
                rating=4.1,
                votes=3,
                cost_band="low",
            ),
        ]
    )
    out = retrieve_candidates(df, _prefs(budget="low", min_rating=4.0), cap=10)
    assert list(out["restaurant_id"]) == ["3"]


def test_min_rating_zero_includes_null_rating():
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="1",
                name="A",
                city="Pune",
                cuisines=[],
                rating=None,
                votes=1,
                cost_band="low",
            ),
        ]
    )
    out = retrieve_candidates(df, _prefs(budget="low", min_rating=0.0), cap=10)
    assert len(out) == 1


def test_deterministic_order_same_inputs():
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="b",
                name="B",
                city="Pune",
                cuisines=["italian"],
                rating=4.0,
                votes=10,
                cost_band="medium",
            ),
            _minimal_row(
                restaurant_id="a",
                name="A",
                city="Pune",
                cuisines=["italian"],
                rating=4.0,
                votes=10,
                cost_band="medium",
            ),
        ]
    )
    prefs = _prefs(cuisines=["italian"])
    o1 = retrieve_candidates(df, prefs, cap=10)
    o2 = retrieve_candidates(df, prefs, cap=10)
    assert list(o1["restaurant_id"]) == list(o2["restaurant_id"])
    # Same score/votes/rating → tie-break by restaurant_id ascending
    assert list(o1["restaurant_id"]) == ["a", "b"]


def test_ranking_prefers_higher_score_then_votes():
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="low",
                name="L",
                city="Pune",
                cuisines=["italian"],
                rating=3.0,
                votes=100,
                cost_band="high",
            ),
            _minimal_row(
                restaurant_id="high",
                name="H",
                city="Pune",
                cuisines=["italian", "pizza"],
                rating=5.0,
                votes=1,
                cost_band="high",
            ),
        ]
    )
    prefs = _prefs(budget="high", cuisines=["italian", "pizza"])
    out = retrieve_candidates(df, prefs, cap=10)
    # "high" matches both cuisines → cuisine weight 1.0, score 5.0
    # "low" matches one of two user cuisines → weight 0.5, score 1.5
    assert out.iloc[0]["restaurant_id"] == "high"
    assert out.iloc[1]["restaurant_id"] == "low"


def test_cap_limits_rows():
    rows = [
        _minimal_row(
            restaurant_id=str(i),
            name=f"R{i}",
            city="Pune",
            cuisines=[],
            rating=4.0,
            votes=i,
            cost_band="low",
        )
        for i in range(5)
    ]
    df = pd.DataFrame(rows)
    out = retrieve_candidates(df, _prefs(budget="low"), cap=2)
    assert len(out) == 2


def test_hsr_alias_matches_hsr_layout_locality():
    df = pd.DataFrame(
        [
            {
                **_minimal_row(
                    restaurant_id="1",
                    name="Cafe",
                    city="Bangalore",
                    cuisines=["cafe"],
                    rating=4.2,
                    votes=5,
                    cost_band="medium",
                ),
                "locality": "HSR Layout Sector 1",
            },
        ]
    )
    out = retrieve_candidates(
        df,
        _prefs(location="HSR", budget="medium", cuisines=[], min_rating=0.0),
        cap=10,
    )
    assert len(out) == 1
    assert out.iloc[0]["restaurant_id"] == "1"


def test_electronics_city_typo_matches_electronic_city_locality():
    df = pd.DataFrame(
        [
            {
                **_minimal_row(
                    restaurant_id="ec1",
                    name="EC Diner",
                    city="Bangalore",
                    cuisines=["south indian"],
                    rating=4.0,
                    votes=12,
                    cost_band="low",
                ),
                "locality": "Electronic City Phase 1",
            },
        ]
    )
    out = retrieve_candidates(
        df,
        _prefs(location="Electronics City", budget="low", cuisines=[], min_rating=0.0),
        cap=10,
    )
    assert len(out) == 1
    assert out.iloc[0]["restaurant_id"] == "ec1"


def test_metro_broadening_adds_candidates_when_area_sparse(monkeypatch):
    monkeypatch.setenv("PHASE3_MIN_CANDIDATES_BEFORE_BROADEN", "3")
    rows = [
        {
            **_minimal_row(
                restaurant_id="b1",
                name="Bellandur Only",
                city="Bangalore",
                cuisines=["italian"],
                rating=4.5,
                votes=20,
                cost_band="medium",
            ),
            "locality": "Bellandur",
        },
    ]
    for i in range(4):
        rows.append(
            {
                **_minimal_row(
                    restaurant_id=f"o{i}",
                    name=f"Other{i}",
                    city="Bangalore",
                    cuisines=["italian"],
                    rating=4.0,
                    votes=10 + i,
                    cost_band="medium",
                ),
                "locality": "Marathahalli",
            }
        )
    df = pd.DataFrame(rows)
    meta: dict = {}
    out = retrieve_candidates(
        df,
        _prefs(location="Bellandur", budget="medium", cuisines=["Italian"], min_rating=0.0),
        cap=25,
        retrieval_meta=meta,
    )
    assert len(out) >= 4
    assert meta.get("location_search_expanded") is True
    assert "nearby" in (meta.get("dining_match_note") or "").lower()


def test_parquet_round_trip(tmp_path):
    df = pd.DataFrame(
        [
            _minimal_row(
                restaurant_id="x",
                name="Only",
                city="Delhi",
                cuisines=["north indian"],
                rating=4.2,
                votes=50,
                cost_band="medium",
            ),
        ]
    )
    path = tmp_path / "c.parquet"
    df.to_parquet(path, index=False)
    loaded = load_canonical_parquet(path)
    out = retrieve_candidates(
        loaded,
        {"location": "delhi", "budget": "medium", "cuisines": ["North Indian"], "min_rating": 4.0},
        cap=5,
    )
    assert len(out) == 1
    assert out.iloc[0]["name"] == "Only"
