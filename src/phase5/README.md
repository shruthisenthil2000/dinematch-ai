# Phase 5 — Orchestration and API

Implements [docs/phase-wise-architecture.md](../../docs/phase-wise-architecture.md) (Phase 5): one pipeline **preferences → Phase 3 retrieval → Phase 4 LLM (or fallback) → validated response**, optional **cache** (SHA-256 of prefs + dataset fingerprint + cap/top_n/use_llm), and **observability** (latency, candidate count, prompt size, outcome notes; no preference text in logs).

## Setup

From repository root:

```bash
.venv/bin/pip install -r src/phase5/requirements.txt
export GROQ_API_KEY="..."   # optional if using use_llm / default true
```

## Environment

| Variable | Purpose |
|----------|---------|
| `PHASE5_PARQUET` | Path to `canonical_restaurants.parquet` (default: `phase1/output/...` under repo root) |
| `PHASE5_DISABLE_CACHE` | `1` to turn off caching |
| `PHASE5_CACHE_DIR` | Optional directory for JSON cache files (in addition to in-memory LRU) |
| `PHASE5_CACHE_MAX_ENTRIES` | In-memory LRU size (default `256`) |
| `PHASE5_PORT` | HTTP port (default `5055`) |

## Library API

```python
from pathlib import Path
from phase5 import run_recommendation

prefs = {"location": "Pune", "budget": "medium", "cuisines": [], "min_rating": 4.0}
response, metrics = run_recommendation(prefs, parquet_path=Path("phase1/output/canonical_restaurants.parquet"), use_llm=False)
```

## HTTP API

```bash
PYTHONPATH=src python -m phase5.run_server
```

- `GET /health` — liveness.
- `POST /api/recommend` — JSON body:

```json
{
  "preferences": {
    "location": "Pune",
    "budget": "medium",
    "cuisines": [],
    "min_rating": 4.0
  },
  "cap": 25,
  "top_n": 5,
  "use_llm": true
}
```

Response: `{ "valid": true, "response": { ... RecommendationResponse ... }, "observability": { ... } }`. Preferences are validated with the same schema as Phase 2.

## CLI

```bash
PYTHONPATH=src python -m phase5.cli --prefs prefs.json --no-llm --verbose
```

Stdout is the recommendation JSON; with `--verbose`, metrics go to stderr.
