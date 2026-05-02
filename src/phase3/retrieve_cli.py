"""CLI: load canonical Parquet + preferences JSON → print capped candidate JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Phase 3 structured retrieval (stdout JSON array).")
    p.add_argument("--parquet", required=True, type=Path, help="Path to canonical_restaurants.parquet")
    p.add_argument("--prefs", required=True, type=Path, help="Path to user preferences JSON")
    p.add_argument("--cap", type=int, default=25, help="Max candidates (default 25)")
    args = p.parse_args(argv)

    from phase3.retrieval import load_canonical_parquet, retrieve_candidates

    df = load_canonical_parquet(args.parquet)
    prefs = json.loads(args.prefs.read_text(encoding="utf-8"))
    out = retrieve_candidates(df, prefs, cap=args.cap)

    rows = out.to_dict(orient="records")
    for row in rows:
        if isinstance(row.get("cuisines"), list):
            row["cuisines"] = list(row["cuisines"])
    print(json.dumps(rows, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
