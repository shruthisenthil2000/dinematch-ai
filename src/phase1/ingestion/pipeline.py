from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from phase1.ingestion.constants import DATASET_ID
from phase1.ingestion.convert import assign_cost_bands, raw_to_canonical
from phase1.ingestion.load import SourceKind, load_raw
from phase1.ingestion.normalize import deduplicate_restaurants, drop_unusable_rows, validate_and_order_raw_columns

OutputFormat = Literal["parquet", "csv", "both"]


@dataclass
class PipelineResult:
    manifest_path: Path
    table_path: Path


def run_pipeline(
    *,
    source: SourceKind,
    cache_dir: Path,
    csv_path: Path | None,
    output_dir: Path,
    output_format: OutputFormat = "parquet",
    dataset_revision: str | None = None,
) -> PipelineResult:
    output_dir.mkdir(parents=True, exist_ok=True)

    raw = load_raw(source=source, cache_dir=cache_dir, csv_path=csv_path)
    raw = validate_and_order_raw_columns(raw)
    raw_count = len(raw)

    canonical_intermediate = raw_to_canonical(raw)
    after_drop = drop_unusable_rows(canonical_intermediate)
    canonical = deduplicate_restaurants(after_drop)

    bands, band_meta = assign_cost_bands(canonical["approx_cost_for_two"])
    canonical["cost_band"] = bands
    canonical["votes"] = canonical["votes"].astype("Int64")

    stem = "canonical_restaurants"
    primary_path: Path

    if output_format in ("parquet", "both"):
        pq_path = output_dir / f"{stem}.parquet"
        canonical.to_parquet(pq_path, index=False)
        primary_path = pq_path

    if output_format in ("csv", "both"):
        csv_out = output_dir / f"{stem}.csv"
        exp = canonical.copy()
        exp["cuisines"] = exp["cuisines"].map(lambda xs: ", ".join(xs) if xs else "")
        exp.to_csv(csv_out, index=False)
        if output_format == "csv":
            primary_path = csv_out

    manifest: dict[str, Any] = {
        "phase": 1,
        "dataset_id": DATASET_ID,
        "dataset_revision": dataset_revision or "unknown",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "row_counts": {
            "raw": raw_count,
            "after_drop_unusable": len(after_drop),
            "canonical_after_dedupe": len(canonical),
        },
        "dedupe_policy": "subset name+city+locality; keep highest rating then votes",
        "budget_bands": band_meta,
        "output": {
            "format": output_format,
            "primary_table": str(primary_path.name),
        },
    }

    manifest_path = output_dir / "dataset_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return PipelineResult(manifest_path=manifest_path, table_path=primary_path)
