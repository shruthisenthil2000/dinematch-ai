"""Phase 6 frontend: browser form + results UI backed by Phase 5 API."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

_PHASE6_ROOT = Path(__file__).resolve().parent


def _phase5_api_base() -> str:
    return (os.environ.get("PHASE6_API_BASE") or "http://127.0.0.1:5055").rstrip("/")


def _forward(path: str, *, body: bytes | None = None, method: str = "GET") -> Response:
    url = f"{_phase5_api_base()}{path}"
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            payload = r.read()
            status = r.getcode()
    except urllib.error.HTTPError as e:
        payload = e.read()
        status = e.code
    except Exception as exc:
        return jsonify({"error": "phase5_unreachable", "detail": str(exc)}), 503

    return Response(payload, status=status, content_type="application/json")


def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=str(_PHASE6_ROOT / "templates"),
    )

    @app.get("/")
    def index():
        return render_template("index.html", api_base=_phase5_api_base())

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "phase": 6})

    @app.get("/api/backend-health")
    def backend_health():
        return _forward("/health")

    @app.post("/api/recommend")
    def api_recommend():
        body = request.get_json(silent=True)
        if body is None:
            return jsonify({"error": "Invalid JSON body."}), 400
        return _forward("/api/recommend", body=json.dumps(body).encode("utf-8"), method="POST")

    return app
