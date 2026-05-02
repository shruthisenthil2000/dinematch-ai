# Phase 0 Implementation

This document records what was implemented for **Phase 0 — Scope, Contracts, and Success Criteria** in [phase-wise-architecture.md](./phase-wise-architecture.md), and how it connects to [problemstatement.md](./problemstatement.md).

## Input surface (Phase 0 decision)

- **Primary source of input:** a **basic web UI** (forms for location, budget, cuisines, minimum rating, optional free-text constraints). Submitted data MUST conform to `schemas/user-preferences.schema.json`.
- **Secondary (optional):** a REST handler or CLI may send the same JSON shape for testing or automation; they are not required for the MVP if the web UI is sufficient.

## Goals (recap)

- Fix **input** and **output** shapes so later phases (ingestion, filtering, LLM, presentation) share one contract, with the **web UI** as the main way users provide preferences.
- Record **success criteria**, **quality bar**, and **non-goals** in a machine-readable manifest.
- Provide **golden queries** for manual and semi-automated evaluation.
- Define the **source dataset layout** and the **canonical row** Phase 1 should produce (see [contracts/dataset_contract.md](../contracts/dataset_contract.md)).

## Artifact inventory

| Artifact | Path | Role |
|----------|------|------|
| User preference JSON Schema | `schemas/user-preferences.schema.json` | Validates payloads from the **basic web UI** (and any optional API/CLI): `location`, `budget`, `cuisines`, `min_rating`, `optional_constraints`. |
| Recommendation response JSON Schema | `schemas/recommendation-response.schema.json` | Validates ranked results (`restaurant_id`, display fields, `ai_rationale`, `rank`, optional `comparative_summary`, `meta`). |
| Scope manifest | `contracts/phase0-scope.json` | Non-goals, success criteria, quality bar; pointers to problem statement and architecture. |
| Dataset contract | `contracts/dataset_contract.md` | Raw Hugging Face CSV schema → canonical columns for Phase 1+. |
| Golden queries | `contracts/golden-queries.json` | Example preference payloads + manual evaluation notes (includes edge-style cases). |
| Sample response fixture | `contracts/sample-recommendation-response.json` | Example document that validates against the response schema. |
| Contract validator | `scripts/validate_phase0_contracts.py` (→ `src/phase0/validate_contracts.py`) | Ensures golden preferences and the sample response validate against the JSON Schemas. |
| Python deps (validator) | `requirements-contracts.txt` | `jsonschema` for Draft 2020-12 validation. |

## Input contract (summary)

- **Required:** `location`, `budget` (`low` | `medium` | `high`), `min_rating` (0–5, inclusive `>=` in later phases).
- **Optional:** `cuisines` (empty array = any cuisine); `optional_constraints` (free text, max length in schema).
- **Phase 1+:** `budget` must map consistently from dataset cost fields; see dataset contract for source column and proposed normalization.

Full normative definition: `schemas/user-preferences.schema.json`.

## Output contract (summary)

- **`recommendations[]`:** Each item must include `restaurant_id`, `name`, `cuisine`, `rating`, `estimated_cost`, `ai_rationale`, and `rank` (1-based).
- **Optional:** `comparative_summary`, `meta` (e.g. `dataset_version`, `candidate_count`).

Full normative definition: `schemas/recommendation-response.schema.json`.

## Quality bar (operational)

- **Hard filters:** Every returned row must satisfy structured filters applied in Phase 3+ (location, budget mapping, cuisine policy, `min_rating`).
- **Grounding:** Every `restaurant_id` must appear in the candidate set passed to the LLM; no invented venues.
- **Explanations:** `ai_rationale` should tie to user preferences using attributes present in data (not fabricated ratings or prices).

Source: `contracts/phase0-scope.json` → `quality_bar`.

## Non-goals (recap)

Listed explicitly in `contracts/phase0-scope.json` (e.g. no live Zomato API, no payments/maps/auth in scope unless added later).

## Running the validator

From the repository root:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-contracts.txt
.venv/bin/python scripts/validate_phase0_contracts.py
# or:
PYTHONPATH=src .venv/bin/python -m phase0.validate_contracts
```

Expected: all golden-query `preferences` objects validate; `contracts/sample-recommendation-response.json` validates.

## Golden queries

File: `contracts/golden-queries.json`.

Each example includes `id`, `label`, `preferences`, and `manual_evaluation` hints (expected filters, LLM behavior, empty-result cases). Implementations should document the **cuisine match policy** (`ANY` overlap vs `ALL`) in Phase 2/3; the golden file references this under `cuisine_match_policy_documentation`.

## Handoff to Phase 1

1. Run ETL per [`src/phase1/README.md`](../src/phase1/README.md): `PYTHONPATH=src python -m phase1.run_etl` (outputs default to `phase1/output/`).
2. Raw layout and canonical mapping: [contracts/dataset_contract.md](../contracts/dataset_contract.md) and [src/phase1/field_dictionary.md](../src/phase1/field_dictionary.md).
3. Pin **dataset revision** (`--dataset-revision`) for reproducible `meta.dataset_version` in later phases.

## Related docs

- [problemstatement.md](./problemstatement.md) — product workflow and fields.
- [phase-wise-architecture.md](./phase-wise-architecture.md) — full phased plan.
- [edge-cases.md](./edge-cases.md) — edge cases that inform validation and prompts.
