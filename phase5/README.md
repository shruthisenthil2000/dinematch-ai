# Phase 5 — Orchestration API (runtime notes)

**Source code** lives under **`src/phase5/`** (see [`src/phase5/README.md`](../src/phase5/README.md)).

| Requirement | Notes |
|-------------|--------|
| Canonical Parquet | e.g. `phase1/output/canonical_restaurants.parquet` (`PHASE5_PARQUET`) |
| `GROQ_API_KEY` | For `use_llm: true` (default); omit or use CLI `--no-llm` for offline fallback |
| Cache | Optional `PHASE5_CACHE_DIR`; disable with `PHASE5_DISABLE_CACHE=1` |

```bash
PYTHONPATH=src python -m phase5.run_server
```
