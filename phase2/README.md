# Phase 2 — user preferences (runtime notes)

Application **source code** lives under **`src/phase2/`** (see [`src/phase2/README.md`](../src/phase2/README.md)).

## Defaults (form → JSON)

| Field | Rule |
|-------|------|
| `cuisines` | Comma-separated in the form; empty input → `[]` (any cuisine). |
| `min_rating` | Empty input → `0.0` (no minimum). |
| `optional_constraints` | Omitted from JSON when blank. |

Run the server from the repo root:

```bash
PYTHONPATH=src python -m phase2.run_server
```
