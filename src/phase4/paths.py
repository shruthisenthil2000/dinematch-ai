"""Repository root resolution (schemas live at repo root)."""

from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    here = Path(__file__).resolve()
    for p in [here.parent, *here.parents]:
        if (p / "schemas" / "recommendation-response.schema.json").is_file():
            return p
    raise RuntimeError(
        "Could not find repo root (schemas/recommendation-response.schema.json missing)."
    )
