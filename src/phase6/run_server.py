#!/usr/bin/env python3
"""Run the Phase 6 frontend (default http://127.0.0.1:5060)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from phase6.app import create_app  # noqa: E402


def main() -> None:
    port = int(os.environ.get("PHASE6_PORT", "5060"))
    create_app().run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")


if __name__ == "__main__":
    main()
