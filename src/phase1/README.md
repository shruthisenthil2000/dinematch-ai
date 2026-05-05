# Phase 1 — Data ingestion (source code)

Runtime outputs and HF cache stay under repo **`phase1/output/`** and **`phase1/.hf_cache/`** by default. Source lives here: **`src/phase1/`**.

## Setup

From repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r src/phase1/requirements.txt
```

## Run ETL

Always set **`PYTHONPATH=src`** (or use `pytest` / tooling that reads `pytest.ini`).

```bash
# Smoke test (fixture)
PYTHONPATH=src python -m phase1.run_etl --fixture --format both

# Full Hugging Face download
PYTHONPATH=src python -m phase1.run_etl --source huggingface --format parquet

# Local CSV
PYTHONPATH=src python -m phase1.run_etl --source csv --csv /path/to/zomato.csv

# Project dataset shortcut (writes parquet + csv + manifest)
PYTHONPATH=src python scripts/regenerate_phase1_data.py --csv data/zomato.csv
```

## Layout

| Path | Role |
|------|------|
| `src/phase1/ingestion/` | Load, normalize, convert, pipeline |
| `src/phase1/run_etl.py` | CLI module |
| `src/phase1/fixtures/` | Tiny CSV for `--fixture` |
| `src/phase1/field_dictionary.md` | Canonical column reference |
| `phase1/output/` | Default parquet + manifest (repo root) |
| `phase1/.hf_cache/` | Default Hugging Face cache (repo root) |

## Tests

```bash
python -m pytest tests/phase1/ -q
```
