# Phase 7 — Evaluation checklist and limitations

## Checklist

- Correctness
  - Run golden queries from `contracts/golden-queries.json` (or `phase7-nextjs/public/golden-queries.json`).
  - Verify each response respects `top_n` and does not exceed `candidate_count`.
  - Verify no duplicate `restaurant_id` values in one response.
  - Verify rating threshold is not violated (`rating >= min_rating`).

- Relevance
  - Spot-check that rationales reference user preferences (location, budget, cuisines, constraints) without inventing facts.
  - Track empty-result frequency for strict filters to identify poor defaults.

- Safety
  - Soft-flag prompt-injection-like and harmful terms in optional constraints.
  - Confirm backend still enforces structured filters and schema output.

- Ops
  - Keep backend URL and model/API behavior environment-driven.
  - Confirm API key remains server-side only (never exposed in browser bundle).

## Known limitations

- Strict proof that all returned IDs/names are subset of the backend candidate set needs backend candidate IDs exposed in eval mode; current UI approximates via `candidate_count`.
- Relevance checks are lightweight; robust human-scored evaluation is still required for production confidence.
- Safety checks in this phase are heuristic warnings, not policy-grade moderation.
