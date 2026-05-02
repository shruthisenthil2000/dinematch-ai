# Phase 3 — structured retrieval (runtime notes)

**Source code** lives under **`src/phase3/`** (see [`src/phase3/README.md`](../src/phase3/README.md)).

Use Phase 1 Parquet output as input:

| Path | Purpose |
|------|---------|
| `phase1/output/canonical_restaurants.parquet` | Filter/rank source table |
| `phase1/output/dataset_manifest.json` | Dataset version / band metadata |

Example:

```bash
PYTHONPATH=src python -m phase3.retrieve_cli \
  --parquet phase1/output/canonical_restaurants.parquet \
  --prefs prefs.json \
  --cap 25
```
