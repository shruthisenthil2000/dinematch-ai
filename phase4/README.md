# Phase 4 — Groq LLM layer (runtime notes)

**Source code** lives under **`src/phase4/`** (see [`src/phase4/README.md`](../src/phase4/README.md)).

| Requirement | Notes |
|-------------|--------|
| `GROQ_API_KEY` | Required for live LLM calls ([Groq console](https://console.groq.com/)) |
| `GROQ_MODEL` | Optional; default `llama-3.3-70b-versatile` |
| Phase 1 Parquet | e.g. `phase1/output/canonical_restaurants.parquet` |
| Preferences JSON | Same shape as Phase 0 / Phase 2 (`schemas/user-preferences.schema.json`) |

```bash
export GROQ_API_KEY=...
PYTHONPATH=src python -m phase4.recommend_cli \
  --parquet phase1/output/canonical_restaurants.parquet \
  --prefs prefs.json
```

Use **`--no-llm`** for a schema-valid offline response with no API key.
