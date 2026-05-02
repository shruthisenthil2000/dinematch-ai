# Phase 3 — Structured retrieval (source code)

Implements [docs/phase-wise-architecture.md](../../docs/phase-wise-architecture.md) (Phase 3): deterministic filters on Phase 1 canonical data, optional pre-LLM ranking score, and a hard cap on candidate count.

## Setup

From repository root:

```bash
.venv/bin/pip install -r src/phase3/requirements.txt
```

(Usually already satisfied if Phase 1 deps are installed.)

## Library API

```python
from phase3.retrieval import load_canonical_parquet, retrieve_candidates

df = load_canonical_parquet("phase1/output/canonical_restaurants.parquet")
prefs = {
    "location": "Bangalore",
    "budget": "medium",
    "cuisines": ["italian"],
    "min_rating": 4.0,
}
shortlist = retrieve_candidates(df, prefs, cap=20)
```

`preferences` must match [schemas/user-preferences.schema.json](../../schemas/user-preferences.schema.json) (validate with Phase 2 or `jsonschema` before calling in production).

## Module layout

| Module | Role |
|--------|------|
| `phase3.retrieval.filtering` | Location, budget, cuisine overlap, min-rating masks |
| `phase3.retrieval.ranking` | `retrieval_score` (rating × cuisine match), stable sort, cap |
| `phase3.retrieval.filter_engine` | `retrieve_candidates` orchestration |

## Filter semantics

| Field | Rule |
|-------|------|
| `location` | Case-insensitive match on canonical `city`. |
| `budget` | `cost_band` must equal `budget`; rows with null `cost_band` are excluded. |
| `cuisines` | Empty list → no cuisine filter; else at least one overlapping cuisine token (case-insensitive). |
| `min_rating` | `<= 0` → no floor; else require non-null `rating >= min_rating`. |

Results are sorted stably by `retrieval_score` (rating × cuisine overlap weight), then `votes`, `rating`, `restaurant_id`. The returned frame includes a `retrieval_score` column for debugging or downstream prompts.

## CLI

```bash
PYTHONPATH=src python -m phase3.retrieve_cli \
  --parquet phase1/output/canonical_restaurants.parquet \
  --prefs path/to/preferences.json \
  --cap 25
```

Writes a JSON array of row dicts to stdout.

## Runtime data

Default Phase 1 outputs live under [`phase1/output/`](../../phase1/README.md) at the repo root.
