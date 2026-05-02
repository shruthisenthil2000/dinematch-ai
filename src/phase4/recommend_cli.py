"""CLI: Parquet + preferences → Phase 3 retrieval → Phase 4 Groq recommendation JSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Phase 4: Groq LLM recommendations (stdout = recommendation-response JSON)."
    )
    p.add_argument("--parquet", required=True, type=Path, help="canonical_restaurants.parquet")
    p.add_argument("--prefs", required=True, type=Path, help="user preferences JSON")
    p.add_argument("--cap", type=int, default=25, help="Max candidates from Phase 3 filter")
    p.add_argument("--top-n", type=int, default=5, dest="top_n", help="Max recommendations in output")
    p.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip Groq; emit schema-valid fallback from ranked candidates (no API key).",
    )
    args = p.parse_args(argv)

    from phase3.retrieval import load_canonical_parquet, retrieve_candidates
    from phase4.recommend import recommend_with_groq

    prefs = json.loads(args.prefs.read_text(encoding="utf-8"))
    df = load_canonical_parquet(args.parquet)
    candidates = retrieve_candidates(df, prefs, cap=args.cap)
    try:
        out = recommend_with_groq(
            prefs,
            candidates,
            top_n=args.top_n,
            use_llm=not args.no_llm,
        )
    except RuntimeError as e:
        if "GROQ_API_KEY" in str(e) and not args.no_llm:
            print(str(e), file=sys.stderr)
            print("Hint: pass --no-llm for offline fallback, or export GROQ_API_KEY.", file=sys.stderr)
            return 1
        raise
    print(json.dumps(out, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
