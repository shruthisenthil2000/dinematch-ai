# Canonical field dictionary (Phase 1 output)

Output table: `canonical_restaurants.parquet` (and optional `.csv`) plus `dataset_manifest.json`.

| Column | Type | Description |
|--------|------|-------------|
| `restaurant_id` | string (64-char hex) | SHA-256 of `url` if non-empty, else `name|city|locality`. Stable for a given snapshot and id algorithm. |
| `name` | string | Trimmed restaurant name. |
| `city` | string | From `listed_in(city)`; trimmed, title-cased. Used for user `location` matching. |
| `locality` | string | From `location` (area within city). |
| `cuisines` | list\<string\> | Split on comma from raw `cuisines`; tokens lowercased, empty list if missing. |
| `rating` | float or null | Parsed from `rate` (e.g. `4.1/5`); invalid or `NEW` → null. |
| `votes` | int or null | Parsed from `votes`; non-numeric → null. |
| `approx_cost_for_two` | float or null | Numeric cost for two; currency symbols / noise stripped. |
| `cost_band` | string or null | `low` / `medium` / `high` from **global** tertiles on non-null costs (see `dataset_manifest.json` → `budget_bands`); null if cost unknown. |
| `rest_type` | string or null | Trimmed; empty → null. |
| `online_order` | bool or null | Normalized from yes/no style strings. |
| `book_table` | bool or null | Same. |
| `url` | string or null | Trimmed. |
| `address` | string or null | Trimmed. |

## Manifest (`dataset_manifest.json`)

- `row_counts`: raw rows, after dropping rows without name/city, after deduplication.
- `budget_bands`: `method`, `q1_cutoff`, `q2_cutoff`, human-readable band rules.
- `dedupe_policy`: documented string for reproducibility.

## Raw schema

See [contracts/dataset_contract.md](../../contracts/dataset_contract.md). Phase 1 fails fast if column names or order do not match `EXPECTED_RAW_COLUMNS` in `src/phase1/ingestion/constants.py`.
