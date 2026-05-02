# Phase 6 — Output presentation frontend (source code)

Implements [docs/phase-wise-architecture.md](../../docs/phase-wise-architecture.md) (Phase 6): browser form UX with a same-origin proxy endpoint (`/api/recommend`) that forwards to **Phase 5** `POST /api/recommend`, then renders recommendation cards, comparative summary, loading, error, and empty states.

## Setup

From repository root:

```bash
.venv/bin/pip install -r src/phase6/requirements.txt
```

## Run frontend

```bash
# Terminal 1: backend
PYTHONPATH=src python -m phase5.run_server

# Terminal 2: frontend
PYTHONPATH=src python -m phase6.run_server
```

Open **http://127.0.0.1:5060/**.

## Environment

| Variable | Purpose |
|----------|---------|
| `PHASE6_PORT` | Frontend server port (default `5060`) |
| `PHASE6_API_BASE` | Base URL for backend API (default `http://127.0.0.1:5055`) |

## Notes

- The browser calls Phase 6 endpoint `/api/recommend` with:
  - `{ "preferences": { ... }, "cap": int, "top_n": int, "use_llm": bool }`
- Phase 6 forwards this payload to `${PHASE6_API_BASE}/api/recommend` server-side (avoids CORS issues across ports).
- The frontend renders:
  - `response.recommendations`
  - optional `response.comparative_summary`
  - selected observability fields for user feedback (`candidate_count`, `latency_ms`, `outcome_notes`, `cache_hit`)

## Next.js + Google Stitch

To generate UI mockups with **Google Stitch** for a **Next.js** implementation, use the copy-paste prompt in [`docs/google-stitch-nextjs-ui-prompt.md`](../../docs/google-stitch-nextjs-ui-prompt.md).
