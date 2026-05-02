# Phase 6 — Frontend UI (runtime notes)

Source code lives under **`src/phase6/`** (see [`src/phase6/README.md`](../src/phase6/README.md)).

Run from repo root:

```bash
PYTHONPATH=src python -m phase5.run_server
PYTHONPATH=src python -m phase6.run_server
```

Open: **http://127.0.0.1:5060/**.

Optional env vars:

- `PHASE6_API_BASE` (default `http://127.0.0.1:5055`; target for server-side proxy)
- `PHASE6_PORT` (default `5060`)

Browser requests stay on Phase 6 origin (`/api/recommend`) and are forwarded to Phase 5 by the Phase 6 server.

For a **Next.js** UI / mockup prompt you can paste into **Google Stitch**, see [`docs/google-stitch-nextjs-ui-prompt.md`](../docs/google-stitch-nextjs-ui-prompt.md).
