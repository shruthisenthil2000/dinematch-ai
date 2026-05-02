"""Phase 4 JSON extraction and schema + subset validation."""

from __future__ import annotations

import json

from phase4.llm.response_parse import extract_json_object, parse_and_validate_response


def test_extract_json_object_bare():
    obj = extract_json_object('  {"recommendations": []} ')
    assert obj == {"recommendations": []}


def test_extract_json_object_fenced():
    text = 'Here:\n```json\n{"recommendations": []}\n```\n'
    assert extract_json_object(text) == {"recommendations": []}


def test_extract_json_object_brace_slice():
    text = 'Prefix noise {"recommendations": []} trailing'
    assert extract_json_object(text) == {"recommendations": []}


def test_parse_and_validate_subset_ok():
    allowed = {"r1"}
    payload = {
        "recommendations": [
            {
                "restaurant_id": "r1",
                "name": "A",
                "cuisine": "Italian",
                "rating": 4.0,
                "estimated_cost": "medium",
                "ai_rationale": "ok",
                "rank": 1,
            }
        ]
    }
    text = json.dumps(payload)
    out, err = parse_and_validate_response(text, allowed_ids=allowed)
    assert err == ""
    assert out is not None
    assert len(out["recommendations"]) == 1


def test_parse_rejects_unknown_restaurant_id():
    allowed = {"r1"}
    payload = {
        "recommendations": [
            {
                "restaurant_id": "ghost",
                "name": "A",
                "cuisine": "Italian",
                "rating": 4.0,
                "estimated_cost": "medium",
                "ai_rationale": "ok",
                "rank": 1,
            }
        ]
    }
    out, err = parse_and_validate_response(json.dumps(payload), allowed_ids=allowed)
    assert out is None
    assert "not in candidate set" in err


def test_parse_schema_missing_top_level_required_key():
    out, err = parse_and_validate_response(json.dumps({}), allowed_ids=set())
    assert out is None
    assert "Schema validation" in err
