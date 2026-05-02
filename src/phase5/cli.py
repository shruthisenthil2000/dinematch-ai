"""CLI: preferences JSON → Phase 5 orchestration (stdout = recommendation JSON)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from phase5.orchestrator import run_recommendation


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Phase 5: orchestrated recommendations (retrieval + LLM + cache + metrics log)."
    )
    p.add_argument("--parquet", type=Path, help="canonical_restaurants.parquet (default: PHASE5_PARQUET or phase1/output/...)")
    p.add_argument("--prefs", required=True, type=Path, help="user preferences JSON")
    p.add_argument("--cap", type=int, default=25)
    p.add_argument("--top-n", type=int, default=5, dest="top_n")
    p.add_argument("--no-llm", action="store_true", help="Offline deterministic ranking (no Groq).")
    p.add_argument("--no-cache", action="store_true", help="Bypass response cache for this run.")
    p.add_argument("--verbose", action="store_true", help="Print observability JSON on stderr.")
    args = p.parse_args(argv)

    prefs = json.loads(args.prefs.read_text(encoding="utf-8"))
    try:
        response, metrics = run_recommendation(
            prefs,
            parquet_path=args.parquet,
            cap=args.cap,
            top_n=args.top_n,
            use_llm=not args.no_llm,
            use_cache=not args.no_cache,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 1
    except RuntimeError as e:
        if "GROQ_API_KEY" in str(e) and not args.no_llm:
            print(str(e), file=sys.stderr)
            print("Hint: pass --no-llm or set GROQ_API_KEY.", file=sys.stderr)
            return 1
        raise

    if args.verbose:
        obs = {
            "latency_ms": metrics.latency_ms,
            "candidate_count": metrics.candidate_count,
            "prompt_chars": metrics.prompt_chars,
            "recommendation_count": metrics.recommendation_count,
            "outcome_notes": metrics.outcome_notes,
            "cache_hit": metrics.cache_hit,
            "dataset_fingerprint": metrics.dataset_fingerprint,
        }
        print(json.dumps(obs, indent=2), file=sys.stderr)

    print(json.dumps(response, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
