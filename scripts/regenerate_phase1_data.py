"""Regenerate canonical dataset used by phases 3-5 from local zomato.csv."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from phase1.ingestion.pipeline import run_pipeline


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parents[1]
    p = argparse.ArgumentParser(description="Rebuild Phase 1 canonical outputs from a local CSV.")
    p.add_argument(
        "--csv",
        type=Path,
        default=repo_root / "data" / "zomato.csv",
        help="Source zomato.csv path (default: data/zomato.csv)",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=repo_root / "phase1" / "output",
        help="Output directory for canonical table + manifest",
    )
    args = p.parse_args(argv)

    csv_path = args.csv.expanduser().resolve()
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    result = run_pipeline(
        source="csv",
        cache_dir=repo_root / "phase1" / ".hf_cache",
        csv_path=csv_path,
        output_dir=args.output_dir.expanduser().resolve(),
        output_format="both",
        dataset_revision=f"local-csv-sha256:{_sha256(csv_path)}",
    )
    print(f"Wrote {result.table_path}")
    print(f"Wrote {result.manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
