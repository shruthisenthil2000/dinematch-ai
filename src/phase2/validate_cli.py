#!/usr/bin/env python3
"""Validate a JSON file against user-preferences.schema.json. Exit 0 if valid, 1 otherwise."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from phase2.preferences.schema_validate import validate_preferences  # noqa: E402


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m phase2.validate_cli <preferences.json>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 2
    data = json.loads(path.read_text(encoding="utf-8"))
    ok, errors, normalized = validate_preferences(data)
    if ok:
        print(json.dumps(normalized, indent=2))
        return 0
    for e in errors:
        print(e, file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
