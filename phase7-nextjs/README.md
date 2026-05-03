# Phase 7 (Next.js) — Evaluation, Safety, and Hardening

Implements Phase 7 from `docs/phase-wise-architecture.md` in **Next.js**.

## Covers all Phase 7 tracks

- **Correctness:** automatic checks on recommendation integrity (top_n cap, no duplicate IDs, min_rating respected, sequential rank warnings)
- **Relevance:** lightweight quality gate via rating-threshold checks and per-query eval runs
- **Safety:** soft warnings for harmful/prompt-injection-like optional constraints before submit
- **Ops:** runtime backend URL config through environment variable (`PHASE5_API_BASE`)

## App pages

- `/` — Stitch-inspired **landing_preferences** dark UI: preference form, safety soft-checks in the insights rail, `POST /api/recommend`, then navigate to results
- `/recommendations` — **AI recommendations grid** populated from the latest successful response (sessionStorage); refresh re-calls the API with the same payload
- `/eval` — golden-query evaluation using `public/golden-queries.json` (same API proxy)

## API routes

- `POST /api/recommend` — server-side proxy to `${PHASE5_API_BASE}/api/recommend`
- `GET /api/backend-health` — proxy to `${PHASE5_API_BASE}/health`

## Run locally

1) Start Phase 5 backend from repo root:

```bash
PYTHONPATH=src python -m phase5.run_server
```

2) In `phase7-nextjs/`:

```bash
cp .env.example .env.local
# install dependencies with your package manager (npm/pnpm/yarn)
# then run:
next dev -p 3000
```

## Phase 7 eval checklist and limitations

See: `docs/phase7-eval-checklist.md`.
