"""
Phase 1 ETL entrypoint (docs/phase-wise-architecture.md).

Run from repo root (with PYTHONPATH=src), e.g.:
  PYTHONPATH=src python -m phase1.run_etl --fixture
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PHASE1_SRC = Path(__file__).resolve().parent


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 1: ingest and normalize Zomato restaurant data.")
    p.add_argument(
        "--source",
        choices=["huggingface", "csv"],
        default="huggingface",
        help="Load from Hugging Face (default) or a local zomato.csv",
    )
    p.add_argument("--csv", type=Path, help="Path to zomato.csv (required when --source csv)")
    p.add_argument(
        "--output-dir",
        type=Path,
        default=_REPO_ROOT / "phase1" / "output",
        help="Directory for canonical_restaurants.parquet and dataset_manifest.json",
    )
    p.add_argument(
        "--cache-dir",
        type=Path,
        default=_REPO_ROOT / "phase1" / ".hf_cache",
        help="Hugging Face cache directory (default: repo phase1/.hf_cache)",
    )
    p.add_argument(
        "--format",
        choices=["parquet", "csv", "both"],
        default="parquet",
        dest="outfmt",
        help="Output table format",
    )
    p.add_argument(
        "--dataset-revision",
        default=None,
        help="Optional Git revision string for dataset_manifest.json (e.g. HF commit SHA)",
    )
    p.add_argument(
        "--fixture",
        action="store_true",
        help="Use bundled tiny CSV under src/phase1/fixtures/ (smoke test)",
    )
    args = p.parse_args()

    if str(_REPO_ROOT / "src") not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT / "src"))

    from phase1.ingestion.pipeline import run_pipeline  # noqa: E402

    if args.fixture:
        fixture = _PHASE1_SRC / "fixtures" / "zomato_sample.csv"
        if not fixture.is_file():
            print(f"Missing fixture: {fixture}", file=sys.stderr)
            return 1
        args.source = "csv"
        args.csv = fixture

    if args.source == "csv" and not args.csv:
        print("--csv is required when --source csv", file=sys.stderr)
        return 1

    try:
        result = run_pipeline(
            source=args.source,
            cache_dir=args.cache_dir,
            csv_path=args.csv,
            output_dir=args.output_dir,
            output_format=args.outfmt,
            dataset_revision=args.dataset_revision,
        )
    except Exception as e:
        print(f"ETL failed: {e}", file=sys.stderr)
        return 1

    print(f"Wrote {result.table_path}")
    print(f"Wrote {result.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
