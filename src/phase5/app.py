"""Phase 5 Flask API: validated preferences → orchestrated recommendations."""

from __future__ import annotations

import logging
import traceback

from flask import Flask, jsonify, request

from phase2.preferences.schema_validate import validate_preferences
from phase5.orchestrator import run_recommendation_from_json_body

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "phase": 5})

    @app.post("/api/recommend")
    def api_recommend():
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json."}), 400
        body = request.get_json(silent=True)
        if body is None:
            return jsonify({"error": "Invalid JSON body."}), 400

        prefs_obj = body.get("preferences") if isinstance(body, dict) else None
        ok, errors, normalized = validate_preferences(prefs_obj)
        if not ok:
            return jsonify({"valid": False, "errors": errors}), 400

        assert normalized is not None
        body = dict(body) if isinstance(body, dict) else {}
        body["preferences"] = normalized

        try:
            response, metrics = run_recommendation_from_json_body(body)
        except FileNotFoundError as e:
            logger.warning("phase5 parquet missing: %s", e)
            return jsonify({"error": "dataset_not_found", "detail": str(e)}), 503
        except ValueError as e:
            return jsonify({"error": "bad_request", "detail": str(e)}), 400
        except Exception:
            logger.error("phase5 pipeline error:\n%s", traceback.format_exc())
            return jsonify({"error": "internal_error"}), 500

        return jsonify(
            {
                "valid": True,
                "response": response,
                "observability": {
                    "latency_ms": metrics.latency_ms,
                    "candidate_count": metrics.candidate_count,
                    "prompt_chars": metrics.prompt_chars,
                    "recommendation_count": metrics.recommendation_count,
                    "outcome_notes": metrics.outcome_notes,
                    "cache_hit": metrics.cache_hit,
                    "dataset_fingerprint": metrics.dataset_fingerprint,
                },
            }
        )

    return app
