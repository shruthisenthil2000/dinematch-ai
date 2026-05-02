"""Phase 5 orchestrator: preferences → retrieval → LLM → validated recommendations."""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from phase3.retrieval import load_canonical_parquet, retrieve_candidates
from phase4.llm.prompt_builder import build_recommendation_prompt, dataframe_to_candidate_dicts
from phase4.paths import repo_root
from phase4.recommend import recommend_with_groq
from phase5.cache import ResponseCache, cache_key, dataset_fingerprint, get_global_cache

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OrchestrationMetrics:
    latency_ms: float
    candidate_count: int
    prompt_chars: int
    recommendation_count: int
    outcome_notes: str
    cache_hit: bool
    dataset_fingerprint: str


def default_parquet_path() -> Path:
    override = (os.environ.get("PHASE5_PARQUET") or "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return (repo_root() / "phase1" / "output" / "canonical_restaurants.parquet").resolve()


def _cache_from_env() -> tuple[bool, Path | None]:
    if (os.environ.get("PHASE5_DISABLE_CACHE") or "").strip() in ("1", "true", "yes"):
        return False, None
    raw = (os.environ.get("PHASE5_CACHE_DIR") or "").strip()
    cache_dir = Path(raw).expanduser().resolve() if raw else None
    return True, cache_dir


def _observability_log(metrics: OrchestrationMetrics) -> None:
    """Log counts and timing only (no preference text or candidate names)."""
    logger.info(
        "phase5_recommendation_done latency_ms=%.2f candidate_count=%d prompt_chars=%d "
        "recommendation_count=%d outcome=%s cache_hit=%s ds_fp=%s",
        metrics.latency_ms,
        metrics.candidate_count,
        metrics.prompt_chars,
        metrics.recommendation_count,
        metrics.outcome_notes,
        metrics.cache_hit,
        metrics.dataset_fingerprint,
    )


def run_recommendation(
    preferences: Mapping[str, Any],
    *,
    parquet_path: Path | None = None,
    cap: int = 25,
    top_n: int = 5,
    use_llm: bool = True,
    use_cache: bool | None = None,
    cache: ResponseCache | None = None,
) -> tuple[dict[str, Any], OrchestrationMetrics]:
    """
    Full pipeline: load canonical table, retrieve candidates, call Phase 4 (or fallback).

    When ``use_cache`` is None, follows ``PHASE5_DISABLE_CACHE`` / ``PHASE5_CACHE_DIR``.
    """
    path = parquet_path if parquet_path is not None else default_parquet_path()
    if not path.is_file():
        raise FileNotFoundError(f"Canonical parquet not found: {path}")

    ds_fp = dataset_fingerprint(path)
    cache_on, cache_dir = _cache_from_env()
    if use_cache is not None:
        cache_on = bool(use_cache) and cache_on

    key: str | None = None
    active_cache = cache
    if cache_on and active_cache is None:
        max_e = int(os.environ.get("PHASE5_CACHE_MAX_ENTRIES", "256"))
        active_cache = get_global_cache(max_entries=max_e, cache_dir=cache_dir)

    t0 = time.perf_counter()
    if cache_on and active_cache is not None:
        key = cache_key(preferences, dataset_fp=ds_fp, cap=cap, top_n=top_n, use_llm=use_llm)
        hit = active_cache.get(key)
        if hit is not None:
            meta = hit.get("meta") or {}
            notes = str(meta.get("notes", "cache_hit"))
            nrec = len(hit.get("recommendations") or [])
            metrics = OrchestrationMetrics(
                latency_ms=(time.perf_counter() - t0) * 1000.0,
                candidate_count=int(meta.get("candidate_count", -1)),
                prompt_chars=0,
                recommendation_count=nrec,
                outcome_notes=notes,
                cache_hit=True,
                dataset_fingerprint=ds_fp,
            )
            _observability_log(metrics)
            return hit, metrics

    df = load_canonical_parquet(path)
    candidates = retrieve_candidates(df, preferences, cap=cap)
    cand_count = len(candidates)
    prompt_chars = 0
    if cand_count > 0:
        cand_dicts = dataframe_to_candidate_dicts(candidates)
        prompt_chars = len(
            build_recommendation_prompt(preferences, cand_dicts, top_n=top_n)
        )

    response = recommend_with_groq(
        preferences,
        candidates,
        top_n=top_n,
        use_llm=use_llm,
    )

    meta = response.get("meta") or {}
    notes = str(meta.get("notes", ""))
    nrec = len(response.get("recommendations") or [])
    elapsed_ms = (time.perf_counter() - t0) * 1000.0

    metrics = OrchestrationMetrics(
        latency_ms=elapsed_ms,
        candidate_count=cand_count,
        prompt_chars=prompt_chars,
        recommendation_count=nrec,
        outcome_notes=notes or ("llm_disabled" if not use_llm else "unknown"),
        cache_hit=False,
        dataset_fingerprint=ds_fp,
    )
    _observability_log(metrics)

    if cache_on and active_cache is not None and key is not None:
        active_cache.set(key, response)

    return response, metrics


def run_recommendation_from_json_body(body: object) -> tuple[dict[str, Any], OrchestrationMetrics]:
    """
    Parse Phase 5 API envelope: ``{"preferences": {...}, "cap": optional, ...}``.
    """
    if not isinstance(body, dict):
        raise ValueError("body_must_be_object")
    prefs = body.get("preferences")
    if not isinstance(prefs, dict):
        raise ValueError("preferences_required")

    cap = body.get("cap", 25)
    top_n = body.get("top_n", 5)
    use_llm = body.get("use_llm", True)
    parquet_override = body.get("parquet_path")

    if not isinstance(cap, int) or cap < 1:
        raise ValueError("cap_invalid")
    if not isinstance(top_n, int) or top_n < 1:
        raise ValueError("top_n_invalid")
    if not isinstance(use_llm, bool):
        raise ValueError("use_llm_invalid")

    pq: Path | None = None
    if parquet_override is not None:
        if not isinstance(parquet_override, str) or not parquet_override.strip():
            raise ValueError("parquet_path_invalid")
        pq = Path(parquet_override).expanduser()

    return run_recommendation(
        prefs,
        parquet_path=pq,
        cap=cap,
        top_n=top_n,
        use_llm=use_llm,
    )
