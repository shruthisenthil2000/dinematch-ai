"""Phase 4: preferences + candidate frame → schema-valid recommendation JSON (Groq)."""

from __future__ import annotations

import logging
from typing import Any, Mapping, Optional, Set

import pandas as pd

from phase4.llm.groq_adapter import GroqChatClient, GroqConfig
from phase4.llm.prompt_builder import build_recommendation_prompt, dataframe_to_candidate_dicts
from phase4.llm.response_parse import get_response_validator, parse_and_validate_response

logger = logging.getLogger(__name__)


def _allowed_ids_from_frame(df: pd.DataFrame) -> Set[str]:
    return {str(x) for x in df["restaurant_id"].tolist()}


def _estimated_cost_row(row: pd.Series) -> str:
    band = row.get("cost_band")
    approx = row.get("approx_cost_for_two")
    parts = []
    if band is not None and not (isinstance(band, float) and pd.isna(band)):
        parts.append(str(band))
    if approx is not None and not (isinstance(approx, float) and pd.isna(approx)):
        parts.append(f"~{float(approx):.0f} for two")
    return ", ".join(parts) if parts else "unknown"


def _fallback_payload(
    candidates_df: pd.DataFrame,
    *,
    top_n: int,
    notes: str,
    candidate_count: Optional[int] = None,
) -> dict[str, Any]:
    """Deterministic schema-valid response when LLM is skipped or unusable."""
    n = max(0, min(int(top_n), len(candidates_df)))
    recs: list[dict[str, Any]] = []
    for i in range(n):
        row = candidates_df.iloc[i]
        rating = row.get("rating")
        r_val = 0.0
        if rating is not None and not (isinstance(rating, float) and pd.isna(rating)):
            r_val = float(rating)
        r_val = max(0.0, min(5.0, r_val))
        cuisines = row.get("cuisines")
        if isinstance(cuisines, float) and pd.isna(cuisines):
            cuisine_str = ""
        elif hasattr(cuisines, "tolist") and not isinstance(cuisines, (str, bytes)):
            cuisine_str = ", ".join(str(x) for x in cuisines.tolist())
        elif isinstance(cuisines, (list, tuple)):
            cuisine_str = ", ".join(str(x) for x in cuisines)
        else:
            cuisine_str = str(cuisines or "")
        recs.append(
            {
                "restaurant_id": str(row["restaurant_id"]),
                "name": str(row["name"]),
                "cuisine": cuisine_str or "Unknown",
                "rating": r_val,
                "estimated_cost": _estimated_cost_row(row),
                "ai_rationale": "Structured shortlist pick (automated fallback).",
                "rank": i + 1,
            }
        )
    count = candidate_count if candidate_count is not None else len(candidates_df)
    return {
        "recommendations": recs,
        "meta": {
            "candidate_count": count,
            "notes": notes,
        },
    }


def recommend_with_groq(
    preferences: Mapping[str, Any],
    candidates_df: pd.DataFrame,
    *,
    top_n: int = 5,
    config: Optional[GroqConfig] = None,
    client: Optional[GroqChatClient] = None,
    use_llm: bool = True,
    max_parse_retries: int = 2,
) -> dict[str, Any]:
    """
    Produce a ``RecommendationResponse`` dict (Phase 0 schema).

    - Empty ``candidates_df``: returns ``recommendations: []`` without calling Groq.
    - ``use_llm=False``: deterministic fallback from the first ``top_n`` rows.
    - On Groq errors or repeated parse/validation failures: deterministic fallback.
    """
    if "restaurant_id" not in candidates_df.columns:
        raise ValueError("candidates_df must include restaurant_id")

    if len(candidates_df) == 0:
        return {
            "recommendations": [],
            "meta": {
                "candidate_count": 0,
                "notes": "no_candidates_after_retrieval",
            },
        }

    allowed = _allowed_ids_from_frame(candidates_df)
    validator = get_response_validator()

    if not use_llm:
        return _fallback_payload(
            candidates_df,
            top_n=top_n,
            notes="llm_disabled",
            candidate_count=len(candidates_df),
        )

    groq_client = client
    cfg = config
    if groq_client is None:
        if cfg is None:
            cfg = GroqConfig.from_env()
        groq_client = GroqChatClient(cfg)

    candidates = dataframe_to_candidate_dicts(candidates_df)
    user_prompt = build_recommendation_prompt(preferences, candidates, top_n=top_n)
    system = (
        "You output only valid JSON for restaurant recommendations. "
        "Never invent restaurant_id values; only use IDs from the candidate list."
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_prompt},
    ]

    last_raw = ""
    last_err = ""
    attempts = 1 + max(0, int(max_parse_retries))

    for attempt in range(attempts):
        try:
            last_raw = groq_client.complete(messages)
        except Exception as exc:
            logger.warning("Groq request failed: %s", type(exc).__name__)
            return _fallback_payload(
                candidates_df,
                top_n=top_n,
                notes=f"groq_error:{type(exc).__name__}",
                candidate_count=len(candidates_df),
            )

        payload, err = parse_and_validate_response(last_raw, allowed_ids=allowed, validator=validator)
        if payload is not None:
            if "meta" not in payload or not isinstance(payload.get("meta"), dict):
                payload["meta"] = {}
            meta = payload["meta"]
            meta.setdefault("candidate_count", len(candidates_df))
            meta.setdefault("notes", "groq_ok")
            return payload

        last_err = err
        if attempt + 1 >= attempts:
            break
        messages.append({"role": "assistant", "content": last_raw})
        messages.append(
            {
                "role": "user",
                "content": (
                    "Your previous reply was invalid. "
                    f"Reason: {err}\n"
                    "Return ONLY a corrected JSON object (same schema). "
                    "Use only restaurant_id values from the candidate list."
                ),
            }
        )

    logger.warning("LLM output failed validation after retries: %s", last_err)
    return _fallback_payload(
        candidates_df,
        top_n=top_n,
        notes="llm_parse_failed",
        candidate_count=len(candidates_df),
    )
