"""Phase 2 Flask app: basic web UI + JSON API for user preferences."""

from __future__ import annotations

from pathlib import Path

from flask import Flask, jsonify, render_template, request, url_for

from preferences.form_parse import build_preferences_from_form
from preferences.schema_validate import validate_preferences

_PHASE2_ROOT = Path(__file__).resolve().parent


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(_PHASE2_ROOT / "templates"),
    )

    @app.get("/")
    def index():
        return render_template("index.html", errors=None, payload=None)

    @app.post("/submit")
    def submit_form():
        raw = build_preferences_from_form(request.form)
        ok, errors, normalized = validate_preferences(raw)
        if ok:
            return render_template("index.html", errors=None, payload=normalized)
        return render_template("index.html", errors=errors, payload=raw), 400

    @app.post("/api/preferences")
    def api_preferences():
        if not request.is_json:
            return jsonify({"valid": False, "errors": ["Content-Type must be application/json."]}), 400
        body = request.get_json(silent=True)
        ok, errors, normalized = validate_preferences(body)
        if ok:
            return jsonify({"valid": True, "preferences": normalized})
        return jsonify({"valid": False, "errors": errors}), 400

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "phase": 2})

    return app
