# Phase 1 — runtime data (output & cache)

ETL **source code** lives under **`src/phase1/`** (see [`src/phase1/README.md`](../src/phase1/README.md)).

This folder keeps generated artefacts by default:

| Path | Purpose |
|------|---------|
| `output/` | `canonical_restaurants.parquet`, `dataset_manifest.json` |
| `.hf_cache/` | Hugging Face dataset cache |
