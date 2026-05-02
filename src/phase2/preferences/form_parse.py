"""Build a preference dict from HTML form fields (before JSON Schema validation)."""

from __future__ import annotations

from typing import Any, Mapping


def build_preferences_from_form(form: Mapping[str, Any]) -> dict[str, Any]:
    """
    Map form keys to the user-preferences JSON shape.

    Defaults (documented in src/phase2/README.md):
    - cuisines: comma-separated input → list of trimmed strings; empty → [] (any cuisine).
    - min_rating: empty → 0.0 (no minimum).
    - optional_constraints: omitted when blank.
    """
    location = (form.get("location") or "").strip()
    budget = (form.get("budget") or "").strip().lower()

    cuisines_raw = (form.get("cuisines") or "").strip()
    if cuisines_raw:
        cuisines = [c.strip() for c in cuisines_raw.split(",") if c.strip()]
    else:
        cuisines = []

    min_rating_raw = (form.get("min_rating") or "").strip()
    if min_rating_raw == "":
        min_rating = 0.0
    else:
        try:
            min_rating = float(min_rating_raw)
        except ValueError:
            min_rating = min_rating_raw

    out: dict[str, Any] = {
        "location": location,
        "budget": budget,
        "cuisines": cuisines,
        "min_rating": min_rating,
    }

    oc = (form.get("optional_constraints") or "").strip()
    if oc:
        out["optional_constraints"] = oc

    return out
