# Phase 2 — User preference collection (source code)

Implements [docs/phase-wise-architecture.md](../../docs/phase-wise-architecture.md) (Phase 2): JSON Schema validation, **basic web UI**, and **`POST /api/preferences`**.

## Setup

From repository root:

```bash
.venv/bin/pip install -r src/phase2/requirements.txt
```

## Run web UI

```bash
PYTHONPATH=src python -m phase2.run_server
```

Open **http://127.0.0.1:5050/** (`PORT` env overrides).

## JSON API & CLI

- `POST /api/preferences` — JSON body, same schema as Phase 0.
- `GET /health`
- CLI: `PYTHONPATH=src python -m phase2.validate_cli path/to.json`

## Defaults

See table in the repo root `phase2/README.md` (or duplicate): empty cuisines → `[]` (any); empty min rating → `0.0`; blank optional constraints omitted.
