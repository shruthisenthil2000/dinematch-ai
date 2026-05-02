"""Validate user preference payloads against Phase 0 JSON Schema."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from jsonschema import Draft202012Validator


def _repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "schemas" / "user-preferences.schema.json").is_file():
            return p
    raise RuntimeError("Could not find repo root (schemas/user-preferences.schema.json).")


def get_preference_schema_path() -> Path:
    return _repo_root() / "schemas" / "user-preferences.schema.json"


@lru_cache(maxsize=1)
def load_validator() -> Draft202012Validator:
    path = get_preference_schema_path()
    if not path.is_file():
        raise FileNotFoundError(f"Preference schema not found: {path}")
    with path.open(encoding="utf-8") as f:
        schema = json.load(f)
    return Draft202012Validator(schema)


def validate_preferences(data: object) -> tuple[bool, list[str], dict | None]:
    """
    Validate a preference document (dict) against schemas/user-preferences.schema.json.

    Returns (ok, human_readable_errors, normalized_dict_or_none).
    On success, normalized_dict matches the schema (includes explicit defaults where applied).
    """
    if not isinstance(data, dict):
        return False, ["Body must be a JSON object."], None

    validator = load_validator()
    errors: list[str] = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "(root)"
        errors.append(f"{loc}: {err.message}")

    if errors:
        return False, errors, None

    normalized = dict(data)
    if "cuisines" not in normalized:
        normalized["cuisines"] = []
    return True, [], normalized
