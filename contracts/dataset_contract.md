# Dataset Contract (Phase 0)

Normative description of the **source restaurant dataset** and the **canonical row** implementations should target after Phase 1 ingestion. Phase 0 locks vocabulary and mapping expectations; Phase 1 verifies raw files against this contract and updates this document if the upstream schema drifts.

## Source

| Property | Value |
|----------|--------|
| Provider | Hugging Face Datasets |
| Dataset id | `ManikaSaini/zomato-restaurant-recommendation` |
| Primary file | `zomato.csv` (CSV, header row) |
| Reference | [https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) |

**Note:** Row counts and file size may change when the dataset revision updates. Phase 1 SHOULD record the resolved revision (Git SHA or snapshot date) in build metadata or `meta.dataset_version`.

## Raw CSV schema

The following columns were observed on the header row of `zomato.csv` (order as in file). Types are **logical** types for ETL; actual cells may need cleaning (whitespace, `"-"`, `NEW`, etc.).

| Column name | Logical type | Description / usage |
|-------------|--------------|---------------------|
| `url` | string | Source page URL (optional for recommendations; useful for deduplication or debugging). |
| `address` | string | Street / full address text. |
| `name` | string | Restaurant name (display). |
| `online_order` | string | Flag or category (e.g. Yes/No); normalize in Phase 1. |
| `book_table` | string | Table booking availability flag; normalize in Phase 1. |
| `rate` | string | Rating as stored in CSV (often like `4.1/5` or similar); **must be parsed** to numeric 0–5 in Phase 1. |
| `votes` | integer (nullable) | Vote count; optional feature for ranking or display. |
| `phone` | string | Contact; treat as sensitive in logs/UI if displayed. |
| `location` | string | Area / locality within city (dataset-specific granularity). |
| `rest_type` | string | Restaurant type (e.g. Casual Dining); optional filter or LLM context. |
| `dish_liked` | string | Dishes liked (free text or list-like string); optional soft-matching. |
| `cuisines` | string | Often comma-separated labels; split and normalize for matching user `cuisines`. |
| `approx_cost(for two people)` | string or number | Cost for two; often numeric or currency string; **must be normalized** for `budget` bands. |
| `reviews_list` | string | Serialized reviews; optional for NLP; not required for MVP filtering. |
| `menu_item` | string | Menu text blob; optional. |
| `listed_in(type)` | string | Listing category; optional filter. |
| `listed_in(city)` | string | City-level listing; primary field for **user `location`** matching alongside `location` (locality). |

### Raw header (authoritative string)

```text
url,address,name,online_order,book_table,rate,votes,phone,location,rest_type,dish_liked,cuisines,approx_cost(for two people),reviews_list,menu_item,listed_in(type),listed_in(city)
```

If Phase 1 detects a different header set, **stop and update this contract** before proceeding.

## Canonical restaurant record (Phase 1 output)

This is the **normalized row** stored or held in memory for filtering and for building LLM candidate tables. All names below are suggestions; implementations may use equivalent names if they map 1:1 in code and in API responses.

| Canonical field | Type | Source (raw columns) | Rules / notes |
|-----------------|------|------------------------|---------------|
| `restaurant_id` | string | Derived | Stable unique id: e.g. hash of (`url`) if present and unique, else hash of (`name`, `listed_in(city)`, `location`). Must be stable across runs for the same snapshot. |
| `name` | string | `name` | Trim; non-empty required for usable rows. |
| `city` | string | `listed_in(city)` | Normalize casing; used for user `location` matching. |
| `locality` | string | `location` | Area within city; optional disambiguation in UI. |
| `cuisines` | array of string | `cuisines` | Split on comma; trim; optional lowercase for matching. |
| `rating` | number (nullable) | `rate` | Parse `4.2/5` → `4.2`; invalid → null or drop row per policy. |
| `votes` | integer (nullable) | `votes` | Coerce; invalid → null. |
| `approx_cost_for_two` | number (nullable) | `approx_cost(for two people)` | Parse numeric “cost for two”; currency symbols stripped. |
| `cost_band` | enum (nullable) | Derived from `approx_cost_for_two` | `low` \| `medium` \| `high` — **mapping must be documented** once percentiles or fixed thresholds are chosen (see below). |
| `rest_type` | string (nullable) | `rest_type` | Optional. |
| `online_order` | boolean or string (nullable) | `online_order` | Normalized. |
| `book_table` | boolean or string (nullable) | `book_table` | Normalized. |
| `url` | string (nullable) | `url` | Optional. |
| `address` | string (nullable) | `address` | Optional. |

### Budget band mapping (Phase 1)

Phase 1 assigns `cost_band` using **global tertiles** on non-null `approx_cost_for_two` after deduplication. Cutoffs (`q1_cutoff`, `q2_cutoff`) and the applied rules are written to **`phase1/output/dataset_manifest.json`** under `budget_bands` each time ETL runs. If there are fewer than 10 non-null costs or quantiles collapse, the pipeline falls back to fixed INR-style cutoffs (400 / 800) and sets `method` accordingly (see `src/phase1/ingestion/convert.py`).

ETL entrypoint: `PYTHONPATH=src python -m phase1.run_etl` (see [`src/phase1/README.md`](../src/phase1/README.md)).

## Alignment with user preferences (`schemas/user-preferences.schema.json`)

| User field | Canonical / raw basis |
|------------|------------------------|
| `location` | Match against `city` first; optionally fuzzy-match `locality` or show disambiguation if product requires. |
| `budget` | Match against `cost_band` after Phase 1 defines thresholds. |
| `cuisines` | Overlap with `cuisines[]` per product policy (`ANY` vs `ALL`). |
| `min_rating` | `rating >= min_rating` (inclusive). Null ratings: exclude or handle per `docs/edge-cases.md`. |
| `optional_constraints` | Soft signals for LLM; map to structured fields only when reliable columns exist. |

## Alignment with recommendation output (`schemas/recommendation-response.schema.json`)

| Response field | Typical source |
|----------------|----------------|
| `restaurant_id` | Canonical `restaurant_id`. |
| `name` | Canonical `name`. |
| `cuisine` | Joined canonical `cuisines` for display. |
| `rating` | Canonical `rating` (or null → policy for display). |
| `estimated_cost` | Formatted from `approx_cost_for_two` and/or original raw cost string. |

## Data quality expectations (Phase 1)

- **Duplicates:** Same `name` + `city` + `locality` may appear; define deduplication policy.
- **Missing cost or rating:** Rows may still exist; filtering and LLM grounding must not fabricate values.
- **Encoding:** File SHOULD be UTF-8; handle odd characters in names and reviews fields.

## Change control

| Change | Action |
|--------|--------|
| New or renamed CSV column | Update **Raw CSV schema** and ETL mapping; bump `meta.dataset_version`. |
| Budget threshold change | Update mapping section; re-run golden evals. |
| `restaurant_id` algorithm change | Treat as breaking; bump dataset version and invalidate caches. |
