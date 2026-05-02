# Detailed Edge Cases: AI Restaurant Recommendation

This document lists edge cases and failure modes for the system described in [problemstatement.md](./problemstatement.md), organized to align with [phase-wise-architecture.md](./phase-wise-architecture.md). For each case: **what goes wrong**, **why it matters**, and **expected handling** (for design and tests).

---

## Legend

| Severity | Meaning |
|----------|---------|
| **P0** | Wrong answers, data corruption, or security/privacy risk |
| **P1** | Bad UX, empty results when avoidable, or broken demo path |
| **P2** | Degraded quality or polish; acceptable with messaging |

---

## Phase 0 — Contracts, Scope, and Evaluation

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E0.1 | **Ambiguous “location”** (e.g., “NCR”, “South Delhi”, typo “Delly”) | Filters return zero or wrong city | Define normalization rules: alias map, fuzzy match with confirmation, or strict enum with helpful error. |
| E0.2 | **Budget bands don’t match dataset encoding** (e.g., user “medium” vs numeric cost for two) | Silent mismatches or empty sets | Document mapping table from dataset cost field → low/medium/high; unit-test boundaries. |
| E0.3 | **“Cuisine” is multi-label in data but single string from user** | Missed matches or over-filtering | Specify match rule: any overlap, all required, or primary cuisine only. |
| E0.4 | **No stable restaurant identifier in cleaned data** | Cannot verify “LLM only picked from candidates” | Enforce internal `restaurant_id` or canonical `(name, location)` key in contracts. |
| E0.5 | **Golden-set expectations drift** when dataset updates | CI/evals flip without code change | Version dataset; cache hash in config; pin eval subset. |

---

## Phase 1 — Data Ingestion and Preparation

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E1.1 | **Hugging Face download fails** (network, rate limit, revoked revision) | App won’t start | Retry with backoff; support offline/local Parquet fallback; clear error with remediation. |
| E1.2 | **Schema change** (new/renamed columns) | Broken ETL or null-heavy table | Schema validation step; fail fast with diff report; mapping layer isolated from raw names. |
| E1.3 | **Duplicate restaurants** (same name, different rows; or true duplicates) | Double recommendations | Deduplicate with rules (keep highest rating, merge cuisines, etc.); log dropped rows count. |
| E1.4 | **Missing critical fields** (name, location, rating, cost) | Unusable rows or misleading filters | Drop or impute per policy; never pass incomplete rows to LLM without flagging “unknown”. |
| E1.5 | **Rating out of range or string** (“4.5/5”, “New”, empty) | Sort/filter bugs | Parse to numeric; coerce invalid to null; exclude from “min rating” filter or treat as 0 only if explicitly allowed. |
| E1.6 | **Cost missing or inconsistent** (ranges, “₹₹”, outliers) | Budget filter wrong | Normalize to numeric band; cap outliers; document how “unknown cost” interacts with budget (exclude vs include). |
| E1.7 | **Cuisine field is messy** (“Chinese, Thai”, “Fast Food”, casing) | Weak matching | Tokenize, lowercase, trim; optional synonym map (e.g., “Continental” ↔ set of tags). |
| E1.8 | **Location granularity mismatch** (city vs neighborhood vs full address) | User searches “Bangalore” but data has localities only | Normalize to parent city where possible; or require user to pick from autocomplete of known locations. |
| E1.9 | **Very large dataset / memory pressure** | OOM or slow load | Stream load; column pruning; indexed store (DuckDB/SQLite); lazy init. |
| E1.10 | **Encoding / special characters** in names | Display or CSV breakage | UTF-8 everywhere; sanitize only for unsafe UI contexts, not for storage. |

---

## Phase 2 — User Preference Collection

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E2.1 | **Empty location** | Meaningless geo filter | Reject with validation error or define “all locations” mode explicitly. |
| E2.2 | **Empty cuisine list** | Ambiguity: “any” vs “none” | Default to “any cuisine”; document in API/UI. |
| E2.3 | **Min rating = 0 or negative** | Nonsense constraint | Clamp or reject; if 0 means “no minimum”, name the field accordingly (`min_rating` optional). |
| E2.4 | **Min rating above max in dataset** (e.g., 5.0 when data max is 4.9) | Always empty | Return friendly empty state; suggest lowering threshold or show max available rating. |
| E2.5 | **Conflicting preferences** (“low budget” + “fine dining only” if tags exist) | User frustration | Allow but surface warning; or detect known conflict patterns from tags. |
| E2.6 | **Very long free-text constraints** (prompt injection, spam) | Token blow-up, odd model behavior | Max length; strip control chars; optional moderation pass; separate system vs user content in API. |
| E2.7 | **Non-ASCII / mixed-language input** | Validation false negatives | Unicode-normalize; avoid overly strict regex. |
| E2.8 | **Multiple cuisines with AND vs OR** unspecified | Surprise results | Expose toggle or fix policy (OR is usually better for recommendations). |
| E2.9 | **Optional tags not in schema** (e.g., “romantic”) | Filter always fails | Map tags to dataset columns or send tags only to LLM as soft preferences, not hard SQL filters. |

---

## Phase 3 — Structured Retrieval (Candidate Generation)

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E3.1 | **Zero candidates after filters** | Core user path breaks | Empty state copy; suggest relaxing cuisine, budget, or rating; offer “nearest” alternatives if product allows. |
| E3.2 | **Thousands of candidates** | Prompt too large; slow; costly | Cap *K*; pre-rank deterministically before LLM; increase cap only if token budget allows. |
| E3.3 | **Ties on pre-LLM score** | Unstable ordering across runs | Secondary sort key (name/id); stable sort. |
| E3.4 | **Location partial match** false positives | Wrong city results | Prefer exact city match; fuzzy match only with score threshold and user confirmation. |
| E3.5 | **Cuisine overlap edge** (“Asian” vs “Japanese”) | Missed or wrong inclusion | Synonym/hierarchy optional; otherwise document limitation. |
| E3.6 | **Budget boundary** (exactly at medium/high threshold) | Off-by-one disputes | Document inclusive/exclusive bounds; test boundary values. |
| E3.7 | **Rating equality** (rating == min_rating) | Inclusion/exclusion ambiguity | Define inclusive min rating; test `>=` not `>`. |
| E3.8 | **All candidates identical on paper** | LLM “ranking” is arbitrary | Still return list; explanations should acknowledge similarity or use secondary attributes. |

---

## Phase 4 — LLM Integration Layer

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E4.1 | **Hallucinated restaurant** (name not in candidate set) | Trust violation (P0) | Validator rejects response; retry with stricter prompt; fallback to deterministic top-*N* without prose. |
| E4.2 | **Wrong rating/cost in narrative** | Misleading user (P0) | Ground explanations: instruct model to copy fields verbatim; post-validate numbers against data. |
| E4.3 | **Malformed JSON / truncated output** | Parse errors | Retry with lower temperature / shorter rationale; schema repair; max tokens tuned. |
| E4.4 | **Model refuses or returns policy message** | No recommendations | Detect refusal; fallback to structured non-LLM ranking + template explanation. |
| E4.5 | **Prompt injection via “preferences”** (“ignore prior instructions…”) | Safety / behavior drift | System/developer message boundaries; treat user text as data, not instructions. |
| E4.6 | **Non-determinism** (different ranks each call) | Confusing in demos | Lower temperature; optional seed where supported; cache by request hash. |
| E4.7 | **Empty candidate list still sent to LLM** | Waste and odd replies | Short-circuit before LLM (Phase 3). |
| E4.8 | **Biased or offensive rationale** | Brand/reputation risk | Content policy; truncate; replace with neutral template; log for review (careful with PII). |
| E4.9 | **Language mismatch** (user writes Hindi, UI English) | Mixed output | Detect language or pin output language in prompt. |

---

## Phase 5 — Orchestration, API, and Caching

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E5.1 | **LLM timeout / rate limit** | Hung or failed requests | Timeouts; circuit breaker; degrade to filter-only results with static blurbs. |
| E5.2 | **Partial failure after filter** (LLM ok but parse fails) | Inconsistent state | Single transaction id per request; never return half-parsed items; retry policy. |
| E5.3 | **Concurrent identical requests** | Duplicate LLM cost | Optional request coalescing / idempotency key. |
| E5.4 | **Stale cache** after dataset reload | Wrong recommendations | Include dataset version in cache key; invalidate on ETL completion. |
| E5.5 | **API abuse** (huge batch, rapid fire) | Cost and DoS | Rate limit; max batch size; auth if deployed. |

---

## Phase 6 — Output Presentation

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E6.1 | **Missing fields for display** (no cost in row) | Broken UI | Show “Not available”; don’t hide card. |
| E6.2 | **Very long restaurant or rationale text** | Layout breaks | Clamp lines with expand; markdown sanitization if rendering HTML. |
| E6.3 | **Duplicate names different branches** | User confusion | Show location/locality disambiguator. |
| E6.4 | **Accessibility** (screen readers, contrast) | Exclusion | Semantic markup; don’t rely on color alone for rating. |
| E6.5 | **Mobile narrow width** | Overflow | Responsive cards; horizontal scroll only for tables as last resort. |

---

## Phase 7 — Evaluation, Safety, and Operations

| ID | Edge case | Why it matters | Expected handling |
|----|-----------|----------------|-------------------|
| E7.1 | **“Correct” filter violated in final list** | Silent logic bug (P0) | Automated check: every output id satisfies hard constraints. |
| E7.2 | **Sensitive data in logs** (exact addresses, user notes) | Privacy (P0) | Redact; structured logging with allowlist fields. |
| E7.3 | **Secrets in client** (API keys in frontend) | Security (P0) | Server-side LLM calls only for web apps. |
| E7.4 | **Non-reproducible evals** | Can't trust improvements | Pin data + model + prompt version per run. |

---

## Cross-Cutting: Trust and Expected Outcome

These align with the “relevance + trust” goal in [problemstatement.md § Expected Outcome](./problemstatement.md#expected-outcome).

| Theme | Edge case | Expected handling |
|-------|-----------|-------------------|
| **Grounding** | User asks for “best” but data is stale | Disclose data vintage; avoid superlatives without evidence. |
| **Transparency** | User doesn’t know what was filtered | Show active filters and candidate count pre-LLM. |
| **Fairness** | All top results from one small area | Optional diversity constraint in prompt or post-processing. |
| **Explainability** | Vague rationale (“great place”) | Prompt requires tying reason to explicit user prefs + visible attributes. |

---

## Suggested Test Matrix (Abbreviated)

| Area | Representative tests |
|------|----------------------|
| Data | E1.3 duplicates, E1.5 bad ratings, E1.7 messy cuisines |
| Prefs | E2.3–E2.4 rating bounds, E2.6 long text |
| Retrieval | E3.1 zero candidates, E3.2 large *K*, E3.7 inclusive min |
| LLM | E4.1 hallucination guard, E4.2 numeric grounding, E4.3 parse retry |
| E2E | E5.1 timeout fallback, E7.1 constraint verifier |

---

## Traceability Quick Map

| [problemstatement.md](./problemstatement.md) section | Edge case IDs (examples) |
|------------------------------------------------------|---------------------------|
| §1 Data ingestion | E1.1–E1.10 |
| §2 User input | E2.1–E2.9 |
| §3 Retrieval + LLM integration | E3.1–E3.8, E4.1–E4.9 |
| §4 Recommendation generation | E4.x, E5.1–E5.3 |
| §5 Output presentation | E6.1–E6.5 |
| Expected outcome / trust | Cross-cutting, E7.x |

| [phase-wise-architecture.md](./phase-wise-architecture.md) phase | Primary IDs |
|------------------------------------------------------------------|------------|
| Phase 0 | E0.1–E0.5 |
| Phase 1 | E1.1–E1.10 |
| Phase 2 | E2.1–E2.9 |
| Phase 3 | E3.1–E3.8 |
| Phase 4 | E4.1–E4.9 |
| Phase 5 | E5.1–E5.5 |
| Phase 6 | E6.1–E6.5 |
| Phase 7 | E7.1–E7.4 |
