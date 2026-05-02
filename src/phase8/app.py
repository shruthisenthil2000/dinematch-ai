"""Streamlit entrypoint for Phase 8 — preference form + recommendations (see README.md)."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_SRC = Path(__file__).resolve().parents[1]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st

from phase2.preferences.schema_validate import validate_preferences
from phase5.orchestrator import OrchestrationMetrics, run_recommendation_from_json_body


def _apply_streamlit_secrets_to_environ() -> None:
    """Promote top-level string entries from st.secrets into os.environ (do not override)."""
    try:
        secrets = st.secrets
    except (AttributeError, RuntimeError):
        return
    for key in secrets:
        if key in os.environ:
            continue
        val = secrets[key]
        if isinstance(val, str):
            os.environ[key] = val


def _api_base() -> str:
    return (os.environ.get("PHASE8_API_BASE") or "").strip().rstrip("/")


def _csv_to_cuisines(raw: str) -> list[str]:
    t = (raw or "").strip()
    if not t:
        return []
    return [x.strip() for x in t.split(",") if x.strip()]


def _init_widget_defaults() -> None:
    defaults: dict[str, Any] = {
        "p_location": "Bellandur",
        "p_budget": "high",
        "p_min_rating": 4.0,
        "p_top_n": 5,
        "p_cap": 25,
        "p_cuisines": "",
        "p_optional_constraints": "Approximate budget around INR 2000 for two.",
        "p_use_llm": True,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _fill_demo() -> None:
    st.session_state["p_location"] = "Bellandur"
    st.session_state["p_budget"] = "high"
    st.session_state["p_min_rating"] = 4.0
    st.session_state["p_top_n"] = 5
    st.session_state["p_cap"] = 25
    st.session_state["p_cuisines"] = ""
    st.session_state["p_optional_constraints"] = "Approximate budget around INR 2000 for two."
    st.session_state["p_use_llm"] = True


def _build_request_body() -> dict[str, Any]:
    prefs: dict[str, Any] = {
        "location": str(st.session_state.get("p_location", "")).strip(),
        "budget": st.session_state.get("p_budget", "medium"),
        "cuisines": _csv_to_cuisines(str(st.session_state.get("p_cuisines", ""))),
        "min_rating": float(st.session_state.get("p_min_rating", 0.0)),
    }
    oc = str(st.session_state.get("p_optional_constraints", "")).strip()
    if oc:
        prefs["optional_constraints"] = oc
    return {
        "preferences": prefs,
        "cap": int(st.session_state.get("p_cap", 25)),
        "top_n": int(st.session_state.get("p_top_n", 5)),
        "use_llm": bool(st.session_state.get("p_use_llm", True)),
    }


def _recommend_in_process(body: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    """Run orchestrator in-process; ``preferences`` must already be schema-validated."""
    try:
        response, metrics = run_recommendation_from_json_body(body)
    except FileNotFoundError as e:
        return None, [str(e)]
    except ValueError as e:
        return None, [str(e)]
    obs = _metrics_to_obs(metrics)
    return {"valid": True, "response": response, "observability": obs}, []


def _metrics_to_obs(metrics: OrchestrationMetrics) -> dict[str, Any]:
    return {
        "latency_ms": metrics.latency_ms,
        "candidate_count": metrics.candidate_count,
        "prompt_chars": metrics.prompt_chars,
        "recommendation_count": metrics.recommendation_count,
        "outcome_notes": metrics.outcome_notes,
        "cache_hit": metrics.cache_hit,
        "dataset_fingerprint": metrics.dataset_fingerprint,
    }


def _recommend_http(base: str, body: dict[str, Any]) -> tuple[dict[str, Any] | None, list[str]]:
    url = f"{base}/api/recommend"
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            payload = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return None, [f"HTTP {e.code}: {raw[:500]}"]
        errs = payload.get("errors")
        if isinstance(errs, list):
            return None, [str(x) for x in errs]
        detail = payload.get("detail") or payload.get("error")
        return None, [str(detail or f"HTTP {e.code}")]
    except urllib.error.URLError as e:
        return None, [f"Could not reach Phase 5 at {base}: {e.reason!r}"]
    except Exception as e:  # noqa: BLE001 — surface any network/parse failure
        return None, [str(e)]

    if not isinstance(payload, dict):
        return None, ["Invalid JSON response from Phase 5."]
    if payload.get("valid") is not True:
        errs = payload.get("errors")
        if isinstance(errs, list) and errs:
            return None, [str(x) for x in errs]
        return None, [str(payload.get("detail") or payload.get("error") or "request_failed")]
    return payload, []


def _render_results(payload: dict[str, Any]) -> None:
    response = payload.get("response") or {}
    recs = response.get("recommendations") if isinstance(response, dict) else None
    if not isinstance(recs, list):
        recs = []

    summary = response.get("comparative_summary") if isinstance(response, dict) else None
    if summary:
        st.success(str(summary))

    if not recs:
        st.info(
            "No recommendations matched the current filters. "
            "Try lowering min rating or relaxing cuisines."
        )
        return

    for rec in recs:
        if not isinstance(rec, dict):
            continue
        rank = rec.get("rank", "")
        name = rec.get("name", "Restaurant")
        with st.container():
            st.subheader(f"#{rank} {name}")
            cuisine = rec.get("cuisine", "")
            rating = rec.get("rating", "")
            cost = rec.get("estimated_cost", "")
            st.caption(f"{cuisine} | Rating {rating} | {cost}")
            rid = rec.get("restaurant_id", "")
            if rid != "":
                st.caption(f"id: {rid}")
            rationale = rec.get("ai_rationale") or ""
            if rationale:
                st.write(rationale)
            st.divider()

    obs = payload.get("observability") or {}
    if isinstance(obs, dict):
        lat = obs.get("latency_ms")
        lat_s = f"{float(lat):.1f} ms" if isinstance(lat, (int, float)) else "n/a"
        st.caption(
            f"Observability: candidates={obs.get('candidate_count', 'n/a')}, "
            f"recommendations={obs.get('recommendation_count', len(recs))}, "
            f"latency={lat_s}, notes={obs.get('outcome_notes', 'n/a')}, "
            f"cache_hit={obs.get('cache_hit', 'n/a')}"
        )


def main() -> None:
    st.set_page_config(page_title="Restaurant recommendations", layout="wide")
    _apply_streamlit_secrets_to_environ()
    _init_widget_defaults()

    st.title("Phase 8 — Restaurant recommendations")
    st.caption("Streamlit demo aligned with `schemas/user-preferences.schema.json` → Phase 5 pipeline.")

    base = _api_base()
    with st.sidebar:
        st.subheader("Mode")
        if base:
            st.markdown(f"**HTTP** → `{base}/api/recommend`")
        else:
            st.markdown("**In-process** — `phase5.orchestrator` on this machine.")
        st.divider()
        if st.button("Load Bellandur demo", use_container_width=True):
            _fill_demo()
            st.rerun()

    col1, col2 = st.columns((1, 1), gap="large")
    with col1:
        st.subheader("Preferences")
        st.text_input("Location", key="p_location")
        st.selectbox("Budget", ("low", "medium", "high"), key="p_budget")
        st.number_input("Min rating", min_value=0.0, max_value=5.0, step=0.1, key="p_min_rating")
        st.text_input("Cuisines (comma-separated)", key="p_cuisines")
        st.text_area("Optional constraints", key="p_optional_constraints", height=100)
        st.number_input("Candidate cap", min_value=1, max_value=100, step=1, key="p_cap")
        st.number_input("Top N", min_value=1, max_value=20, step=1, key="p_top_n")
        st.checkbox("Use live LLM (uncheck for deterministic fallback)", key="p_use_llm")

    with col2:
        st.subheader("Recommendations")
        go = st.button("Get recommendations", type="primary", use_container_width=True)
        if go:
            body = _build_request_body()
            ok, verr, normalized = validate_preferences(body.get("preferences"))
            if not ok:
                st.error("\n".join(verr))
            else:
                body_send = {**body, "preferences": normalized}
                if base:
                    payload, errors = _recommend_http(base, body_send)
                else:
                    payload, errors = _recommend_in_process(body_send)
                if errors:
                    st.error("\n".join(errors))
                elif payload:
                    _render_results(payload)


if __name__ == "__main__":
    main()

