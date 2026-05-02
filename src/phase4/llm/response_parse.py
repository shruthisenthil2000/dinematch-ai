"""Extract JSON from LLM text, validate with JSON Schema, enforce candidate ID subset."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

import jsonschema
from jsonschema import Draft202012Validator

from phase4.paths import repo_root


@lru_cache(maxsize=1)
def get_response_validator() -> Draft202012Validator:
    path = repo_root() / "schemas" / "recommendation-response.schema.json"
    with path.open(encoding="utf-8") as f:
        schema = json.load(f)
    return Draft202012Validator(schema)


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    """Parse first JSON object from raw model output (markdown fence or brace slice)."""
    raw = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw, re.IGNORECASE)
    if m:
        raw = m.group(1).strip()
    try:
        obj = json.loads(raw)
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        pass
    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        obj = json.loads(raw[start : end + 1])
        return obj if isinstance(obj, dict) else None
    except json.JSONDecodeError:
        return None


def _allowed_subset(payload: Dict[str, Any], allowed_ids: Set[str]) -> Tuple[bool, str]:
    recs = payload.get("recommendations")
    if not isinstance(recs, list):
        return False, "recommendations must be an array"
    for i, item in enumerate(recs):
        if not isinstance(item, dict):
            return False, f"recommendations[{i}] must be an object"
        rid = item.get("restaurant_id")
        if rid not in allowed_ids:
            return False, f"restaurant_id not in candidate set: {rid!r}"
    return True, ""


def parse_and_validate_response(
    text: str,
    *,
    allowed_ids: Set[str],
    validator: Optional[Draft202012Validator] = None,
) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Return ``(payload, "")`` on success, or ``(None, error_message)`` on failure.
    """
    v = validator or get_response_validator()
    obj = extract_json_object(text)
    if obj is None:
        return None, "Could not parse a JSON object from model output."
    try:
        v.validate(obj)
    except jsonschema.ValidationError as e:
        return None, f"Schema validation failed: {e.message}"
    ok, msg = _allowed_subset(obj, allowed_ids)
    if not ok:
        return None, msg
    return obj, ""
