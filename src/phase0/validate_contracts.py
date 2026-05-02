#!/usr/bin/env python3
"""Validate Phase 0 JSON artifacts against JSON Schema (phase-wise-architecture.md Phase 0)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    print("Install dependencies: pip install -r requirements-contracts.txt", file=sys.stderr)
    sys.exit(2)


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "schemas" / "user-preferences.schema.json").is_file():
            return p
    raise RuntimeError("Could not find repo root (schemas/user-preferences.schema.json).")


ROOT = _repo_root()


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    pref_schema = load_json(ROOT / "schemas" / "user-preferences.schema.json")
    resp_schema = load_json(ROOT / "schemas" / "recommendation-response.schema.json")
    golden = load_json(ROOT / "contracts" / "golden-queries.json")

    pref_validator = Draft202012Validator(pref_schema)
    examples = golden.get("examples", [])
    errors: list[str] = []

    for ex in examples:
        ex_id = ex.get("id", "?")
        prefs = ex.get("preferences")
        if not isinstance(prefs, dict):
            errors.append(f"{ex_id}: missing or invalid 'preferences' object")
            continue
        for err in pref_validator.iter_errors(prefs):
            errors.append(f"{ex_id} preferences: {err.message} at {list(err.path)}")

    sample_response_path = ROOT / "contracts" / "sample-recommendation-response.json"
    if sample_response_path.exists():
        sample = load_json(sample_response_path)
        resp_validator = Draft202012Validator(resp_schema)
        for err in resp_validator.iter_errors(sample):
            errors.append(f"sample response: {err.message} at {list(err.path)}")

    if errors:
        print("Validation failed:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    print(f"OK: {len(examples)} golden-query preference payloads valid against user-preferences schema.")
    if sample_response_path.exists():
        print("OK: sample-recommendation-response.json valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
