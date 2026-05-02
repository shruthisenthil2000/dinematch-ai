#!/usr/bin/env python3
"""
Live Phase 4 demo: Bellandur-area intent, ~INR 2000 for two, minimum rating 4.0, top 5.

Phase 3 matches ``location`` to canonical ``city`` (dataset column from listed_in(city)).
Bellandur is a locality in Bengaluru — this script uses city ``Bangalore`` for structured
retrieval and puts Bellandur + spend hint in ``optional_constraints`` for the LLM.

Usage (repo root):
  export GROQ_API_KEY=...   # required unless --no-llm
  PYTHONPATH=src .venv/bin/python scripts/run_phase4_live_demo.py

  PYTHONPATH=src .venv/bin/python scripts/run_phase4_live_demo.py --no-llm

Optional: values from ``.env`` in the repo root are loaded if present (no extra deps).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

from phase3.retrieval import load_canonical_parquet, retrieve_candidates
from phase4.recommend import recommend_with_groq


def _load_dotenv_simple(path: Path) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = val


def _pick_budget_band(df, prefs_base: dict, cap: int) -> tuple[str, object]:
    """Try budget bands until retrieval returns at least one row (fixture-friendly)."""
    for band in ("medium", "high", "low"):
        p = {**prefs_base, "budget": band}
        out = retrieve_candidates(df, p, cap=cap)
        if len(out) > 0:
            return band, out
    p = {**prefs_base, "budget": "medium"}
    return "medium", retrieve_candidates(df, p, cap=cap)


def _normalize_payload(out: Any) -> Dict[str, Any]:
    if isinstance(out, str):
        return json.loads(out)
    if isinstance(out, dict):
        return out
    return {}


def _format_recommendation_line(rank: int, item: Dict[str, Any]) -> str:
    name = str(item.get("name") or "Unknown").strip()
    rating = item.get("rating")
    rationale = (item.get("ai_rationale") or "").strip().replace("\n", " ")

    rating_part = ""
    if isinstance(rating, (int, float)):
        try:
            rating_part = f" ({float(rating):.1f}★)"
        except (TypeError, ValueError):
            pass

    if rationale and len(rationale) > 120:
        rationale = rationale[:117] + "..."

    if rating_part and rationale:
        return f"{rank}. {name}{rating_part} — {rationale}"
    if rating_part:
        return f"{rank}. {name}{rating_part}"
    if rationale:
        return f"{rank}. {name} — {rationale}"
    return f"{rank}. {name}"


def _print_top_restaurants(payload: Dict[str, Any], max_items: int) -> None:
    recs_raw = payload.get("recommendations")
    recs: List[Dict[str, Any]] = recs_raw if isinstance(recs_raw, list) else []

    def rank_key(row: Dict[str, Any]) -> int:
        try:
            return int(row.get("rank", 0))
        except (TypeError, ValueError):
            return 0

    recs = sorted(recs, key=rank_key)
    recs = recs[:max_items]

    print("Top 5 Restaurants:")
    if not recs:
        print("(No recommendations returned.)")
        return
    for i, item in enumerate(recs, start=1):
        print(_format_recommendation_line(i, item))


def main() -> int:
    _load_dotenv_simple(_REPO_ROOT / ".env")

    ap = argparse.ArgumentParser(description="Phase 4 live demo (Bellandur / ~2000 INR / 4.0+ / top 5).")
    ap.add_argument(
        "--parquet",
        type=Path,
        default=_REPO_ROOT / "phase1" / "output" / "canonical_restaurants.parquet",
        help="Canonical Phase 1 Parquet",
    )
    ap.add_argument("--cap", type=int, default=30, help="Max candidates after Phase 3 filter")
    ap.add_argument("--top-n", type=int, default=5, dest="top_n", help="Recommendations from LLM")
    ap.add_argument("--no-llm", action="store_true", help="Schema-valid fallback without Groq")
    args = ap.parse_args()

    if not args.parquet.is_file():
        print("Missing data file. Run: PYTHONPATH=src python -m phase1.run_etl --fixture", file=sys.stderr)
        return 1

    df = load_canonical_parquet(args.parquet)

    prefs_base = {
        "location": "Bangalore",
        "cuisines": [],
        "min_rating": 4.0,
        "optional_constraints": (
            "Prefer restaurants in or near Bellandur, Bengaluru. "
            "Target spend about INR 2000 for two people."
        ),
    }

    band, candidates = _pick_budget_band(df, prefs_base, args.cap)
    prefs = {**prefs_base, "budget": band}

    if len(candidates) == 0:
        print("Top 5 Restaurants:")
        print("(No recommendations returned.)")
        return 0

    loc = candidates["locality"].astype(str)
    bell = candidates[loc.str.contains("Bellandur", case=False, na=False)]
    candidates_use = bell if len(bell) > 0 else candidates

    if not args.no_llm and not (os.environ.get("GROQ_API_KEY") or "").strip():
        print("Set GROQ_API_KEY or use --no-llm.", file=sys.stderr)
        return 1

    out = recommend_with_groq(
        prefs,
        candidates_use,
        top_n=args.top_n,
        use_llm=not args.no_llm,
    )
    try:
        payload = _normalize_payload(out)
    except (json.JSONDecodeError, TypeError):
        print("Top 5 Restaurants:")
        print("(Could not parse response.)")
        return 1

    _print_top_restaurants(payload, max_items=min(5, args.top_n))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
