# Phase 4 — LLM integration (Groq)

Implements [docs/phase-wise-architecture.md](../../docs/phase-wise-architecture.md) (Phase 4): prompt builder, **Groq** chat adapter, JSON extraction + **jsonschema** validation against [schemas/recommendation-response.schema.json](../../schemas/recommendation-response.schema.json), guardrails in the prompt (candidates only), parse retries, and a **deterministic fallback** when the API fails or output is invalid.

Depends on Phase 1 (canonical table) and Phase 3 (structured retrieval).

## Setup

```bash
.venv/bin/pip install -r src/phase4/requirements.txt
export GROQ_API_KEY="..."   # from https://console.groq.com/
# optional:
export GROQ_MODEL="llama-3.3-70b-versatile"
```

## Library API

```python
import pandas as pd
from phase3.retrieval import load_canonical_parquet, retrieve_candidates
from phase4 import recommend_with_groq

prefs = {"location": "Bangalore", "budget": "medium", "cuisines": [], "min_rating": 4.0}
df = load_canonical_parquet("phase1/output/canonical_restaurants.parquet")
candidates = retrieve_candidates(df, prefs, cap=20)
response = recommend_with_groq(prefs, candidates, top_n=5)
```

- **`use_llm=False`:** schema-valid response built from the top rows of `candidates_df` (no network).
- **Empty candidates:** returns `{"recommendations": [], "meta": {"candidate_count": 0, ...}}` without calling Groq.

## CLI

From repo root (requires `PYTHONPATH=src` or equivalent):

```bash
PYTHONPATH=src python -m phase4.recommend_cli \
  --parquet phase1/output/canonical_restaurants.parquet \
  --prefs prefs.json \
  --cap 25 \
  --top-n 5
```

Offline / CI without an API key:

```bash
PYTHONPATH=src python -m phase4.recommend_cli \
  --parquet phase1/output/canonical_restaurants.parquet \
  --prefs prefs.json \
  --no-llm
```

## Example script (Bellandur, ~₹2000, rating 4+, top 5)

[`scripts/run_phase4_live_demo.py`](../../scripts/run_phase4_live_demo.py) loads optional repo-root `.env`, uses **Bangalore** as structured `location` (Phase 3 matches `city`), adds Bellandur + INR hint in `optional_constraints`, picks a non-empty `budget` band, then calls Groq for **top 5** (or `--no-llm`).

```bash
PYTHONPATH=src .venv/bin/python -m phase1.run_etl --fixture   # if Parquet missing
PYTHONPATH=src .venv/bin/python scripts/run_phase4_live_demo.py
```

## Behaviour notes

- **Retries:** Up to `max_parse_retries` (default 2) follow-up turns ask the model to fix invalid JSON or IDs outside the candidate set.
- **Fallback:** If Groq errors or validation still fails, output uses the first `top_n` retrieval-ranked rows with a short generic rationale (schema-safe).
- **Logs:** Groq failures log the exception type only (no API key in logs).
