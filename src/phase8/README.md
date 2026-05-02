# Phase 8 — Streamlit deployment (source code)

Implements [docs/phase-wise-architecture.md](../../docs/phase-wise-architecture.md) (Phase 8): a **Streamlit** UI for the same preference contract as Phase 6, calling recommendations either **in-process** (`phase5.orchestrator.run_recommendation_from_json_body`) or over **HTTP** (`POST /api/recommend` on a running Phase 5 deployment).

## Prerequisites

- **Dataset:** Canonical Parquet from Phase 1 at `phase1/output/canonical_restaurants.parquet` (default), or set `PHASE5_PARQUET` to an absolute path. That path is gitignored locally; generate with `python -m phase1.run_etl` from repo root (see [`src/phase1/README.md`](../phase1/README.md)).
- **LLM (optional):** For `use_llm=true`, set `GROQ_API_KEY` in the environment or in Streamlit secrets (see below).

## Setup

From repository root:

```bash
.venv/bin/pip install -r src/phase8/requirements.txt
```

## Run locally

```bash
# From repo root (PYTHONPATH so phase* imports resolve)
PYTHONPATH=src streamlit run src/phase8/app.py --server.port 8501
```

Open **http://127.0.0.1:8501/**.

### Optional: HTTP mode (split backend)

If Phase 5 is already running (e.g. `PYTHONPATH=src python -m phase5.run_server` on port 5055):

```bash
export PHASE8_API_BASE=http://127.0.0.1:5055
PYTHONPATH=src streamlit run src/phase8/app.py
```

The app forwards the same JSON body as Phase 6 to `{PHASE8_API_BASE}/api/recommend`.

### Optional: local secrets file

Create **`.streamlit/secrets.toml`** at the repo root (do not commit; see root `.gitignore`) for keys such as:

```toml
GROQ_API_KEY = "your-key"
# PHASE5_PARQUET = "/absolute/path/to/canonical_restaurants.parquet"
```

Top-level string entries are copied into `os.environ` before the pipeline runs (only if the variable is not already set).

## Deploy — Streamlit Community Cloud

1. Push this repository to GitHub (ensure the app can access your Parquet — e.g. commit a small demo Parquet in a allowed path **or** set `PHASE5_PARQUET` / secrets to a hosted file URL is **not** supported by the orchestrator today; use a path inside the repo or mount — typically you add a **release artifact** or document running ETL in a Cloud **build step** / manual upload to a path you set in secrets).
2. On [Streamlit Community Cloud](https://streamlit.io/cloud), **New app** → pick the repo.
3. **Main file:** `src/phase8/app.py`
4. **Requirements file:** `requirements-streamlit.txt` (repo root), so Cloud installs Phase 5’s transitive dependencies.
5. **Python version:** 3.11+ recommended.
6. **Secrets:** In the app dashboard → Secrets, add at least `GROQ_API_KEY` if using the LLM. Add `PHASE5_PARQUET` if your dataset is not at the default path inside the deployed tree.
7. **Advanced:** If the repo root is not the working directory, set the app root accordingly; Streamlit runs `streamlit run` from the configured root.

For a **minimal Cloud demo without LLM**, use the in-app **“Use live LLM”** unchecked so the deterministic path runs (still requires the Parquet file to exist at the configured path).

## Environment

| Variable | Purpose |
|----------|---------|
| `PHASE8_API_BASE` | If set, recommendations go to this base URL + `/api/recommend` instead of in-process orchestration. |
| `PHASE5_PARQUET` | Override path to canonical Parquet (same as Phase 5). |
| `GROQ_API_KEY` | Groq API key for LLM path (same as Phase 4/5). |
