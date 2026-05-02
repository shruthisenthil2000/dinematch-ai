"""End-to-end tests: load → validate → convert → drop → dedupe → bands → outputs."""

from __future__ import annotations

import json

import pandas as pd
import pytest

from phase1.ingestion.constants import EXPECTED_RAW_COLUMNS, RAW_CITY_COL, RAW_COST_COL, RAW_LOCALITY_COL
from phase1.ingestion.convert import assign_cost_bands, raw_to_canonical
from phase1.ingestion.normalize import deduplicate_restaurants, drop_unusable_rows, validate_and_order_raw_columns
from phase1.ingestion.pipeline import run_pipeline


def _row(**kwargs):
    base = {c: "" for c in EXPECTED_RAW_COLUMNS}
    merged = {**base, **kwargs}
    return [merged[c] for c in EXPECTED_RAW_COLUMNS]


EXPECTED_CANONICAL_COLUMNS = [
    "name",
    "city",
    "locality",
    "cuisines",
    "rating",
    "votes",
    "approx_cost_for_two",
    "rest_type",
    "online_order",
    "book_table",
    "url",
    "address",
    "restaurant_id",
    "cost_band",
]


def test_pipeline_steps_batch_mixed_valid_invalid_no_crash():
    raw = pd.DataFrame(
        [
            _row(
                name="Good",
                **{RAW_CITY_COL: "Pune", RAW_LOCALITY_COL: "A"},
                rate="4.0/5",
                votes="10",
                **{RAW_COST_COL: "500"},
                cuisines="Italian",
            ),
            _row(
                name="",
                **{RAW_CITY_COL: "Pune", RAW_LOCALITY_COL: "B"},
                rate="3/5",
                votes="5",
                **{RAW_COST_COL: "400"},
            ),
            _row(
                name="Dup",
                **{RAW_CITY_COL: "Pune", RAW_LOCALITY_COL: "A"},
                rate="3/5",
                votes="1",
                **{RAW_COST_COL: "600"},
                cuisines="Chinese",
            ),
            _row(
                name="Dup",
                **{RAW_CITY_COL: "Pune", RAW_LOCALITY_COL: "A"},
                rate="4.5/5",
                votes="99",
                **{RAW_COST_COL: "700"},
                cuisines="Chinese",
            ),
        ],
        columns=list(EXPECTED_RAW_COLUMNS),
    )

    raw = validate_and_order_raw_columns(raw)
    canon = raw_to_canonical(raw)
    after_drop = drop_unusable_rows(canon)
    canon2 = deduplicate_restaurants(after_drop)
    bands, _ = assign_cost_bands(canon2["approx_cost_for_two"])
    canon2 = canon2.copy()
    canon2["cost_band"] = bands
    canon2["votes"] = canon2["votes"].astype("Int64")

    assert len(raw) == 4
    assert len(after_drop) == 3
    assert len(canon2) == 2
    assert list(canon2.columns) == EXPECTED_CANONICAL_COLUMNS
    dup = canon2[canon2["name"] == "Dup"].iloc[0]
    assert dup["rating"] == 4.5
    assert dup["votes"] == 99


def test_run_pipeline_csv_end_to_end_schema_and_manifest(tmp_path):
    csv_path = tmp_path / "in.csv"
    df = pd.DataFrame(
        [
            _row(
                name="A",
                **{RAW_CITY_COL: "City", RAW_LOCALITY_COL: "L1"},
                rate="4/5",
                votes="10",
                **{RAW_COST_COL: "500"},
                cuisines="X",
            ),
            _row(
                name="B",
                **{RAW_CITY_COL: "City", RAW_LOCALITY_COL: "L2"},
                rate="3/5",
                votes="20",
                **{RAW_COST_COL: "600"},
                cuisines="Y",
            ),
        ],
        columns=list(EXPECTED_RAW_COLUMNS),
    )
    df.to_csv(csv_path, index=False)

    out_dir = tmp_path / "out"
    result = run_pipeline(
        source="csv",
        cache_dir=tmp_path / "cache",
        csv_path=csv_path,
        output_dir=out_dir,
        output_format="parquet",
        dataset_revision="test-rev",
    )

    written = pd.read_parquet(result.table_path)
    assert list(written.columns) == EXPECTED_CANONICAL_COLUMNS
    assert len(written) == 2

    manifest = json.loads(result.manifest_path.read_text(encoding="utf-8"))
    assert manifest["phase"] == 1
    assert manifest["dataset_revision"] == "test-rev"
    assert manifest["row_counts"]["raw"] == 2
    assert manifest["row_counts"]["after_drop_unusable"] == 2
    assert manifest["row_counts"]["canonical_after_dedupe"] == 2
    assert "budget_bands" in manifest
    assert manifest["output"]["primary_table"] == "canonical_restaurants.parquet"
