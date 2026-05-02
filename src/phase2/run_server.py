#!/usr/bin/env python3
"""Run the Phase 2 preference web UI (default http://127.0.0.1:5050)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from app import create_app  # noqa: E402

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    create_app().run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
