---
title: MCF Seed Reservoir — Mongo vs Postgres (design check)
description: Short design check answering whether the operational MCF metric-seed reservoir should move from Mongo bc_seed.seed_metrics into Postgres. Docs/design only — no code, no DB writes. Recommends a raw/thin Postgres operational candidate reservoir (mcf.seed_metric) refreshed from the Mongo/export preserved upstream seed archive; MCF intake/runtime reads Postgres, not Mongo; the panel remains the enrichment mechanism.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: catalog
focus: mcf-seed-reservoir
---

# MCF Seed Reservoir — Mongo vs Postgres (design check, 2026-06-07)

> **Decision question:** should the operational MCF metric-seed reservoir move from Mongo `bc_seed.seed_metrics` into Postgres? **Scope: docs/design only — no code, no DB writes.** Operator lean: **Postgres operational reservoir, raw/thin** (not a new enriched legacy catalog); **panel remains the enrichment mechanism**.

## 1. Current Mongo source + how the MCF adapter expects it (verified)

- **`bc_seed.seed_metrics` = 12,501 docs.** Fields: `_id`, `metric_name`, `display_name`, `description`, `function_code`, `subfunction_code`, `industry_category_code`, `industry_code`, `tier_code`, `direction`, `bsc_perspective`, `reference_formula`, `measurement_approach`, `thresholds`, `co_bindings` (legacy), `related_metrics`, `search_tags`, `sources[]`, `confidence`, `created_at`, `updated_at`. **Many fields are nullable** (e.g. the asset-management sample has null `reference_formula`) — expected for a raw catalog.
- **`SeedMetricsAdapter`** expects a Mongo collection (`find(filter).limit(n).toArray()`): maps `_id → reservoir_entry_id`; requires `metric_name` + `description`; `confidence → confidence_band`; APQC absent → null; **strips `co_bindings`** (Layer-2/3). It is **dormant** today — `McfModule` injects no Mongo collection and no route calls `ingestFromSeedMetrics`.
- **Precedent:** `bc_seed.pg_staging` (**1,737 docs**; keys `pg_object_id, exported_at, fields_reconciled, table_name, system…`) shows a **Mongo→Postgres export convention already exists** for the source-table catalog. So a Mongo→PG metric-seed import follows an established pattern.

## 2. Pros / cons

| | Keep Mongo as reservoir (rejected) | Import to Postgres — operational reservoir (chosen) |
|---|---|---|
| Migration cost | None (adapter written) | One-time import + refresh job |
| Runtime deps | **Mongo dependency in bc-core authoring path** (connection lifecycle in McfModule) | **No Mongo dep in authoring runtime** — all MCF in PG |
| Observability | Reservoir (Mongo) vs intake/`mcf.*` (PG) split — can't join | **Reservoir + intake + `mcf.*` all in PG — joinable, one inspect surface** |
| Maintainability / future-engineer model | "MCF lives in PG, except the reservoir is in Mongo" | **"All MCF is Postgres"** — clean mental model |
| Backup / DR | Two stores | One store (PG) + Mongo as archive |
| Archive vs operational reservoir | Mongo = preserved upstream seed archive | PG `mcf.seed_metric` = operational reservoir (govern PG←Mongo refresh) |
| Precedent | — | Matches existing `pg_staging` Mongo→PG export |

**Decisive axis (operator's "core platform" value): maintainability + one clear store + future-engineer clarity → Postgres.** The cost (one governed import + a refresh job) is small and bounded.

## 3. Recommended target schema/table

**`mcf.seed_metric`** (singular per D148; MCF schema because it is the MCF candidate reservoir; the existing `reservoir_name = 'seed_metrics'` enum value is preserved for compatibility). *Alternative if a framework-neutral home is preferred: `master.metric_seed`.* Lean: **`mcf.seed_metric`**.

## 4. Minimal columns (raw/thin — incl. `raw_json` + `source_hash`)

Per D162 (queryable data = columns, opaque payload = JSONB; ≤20 cols; `archived_at` soft-delete):

| Column | Type | Purpose |
|---|---|---|
| `seed_metric_id` | uuid PK | internal id |
| `mongo_id` | text **UNIQUE** | Mongo `_id` — lineage key (= `reservoir_entry_id`) |
| `metric_name` | text NOT NULL | queryable (name lookup) |
| `display_name` | text | — |
| `function_code` | text | **queryable — Gate-0 scoping filter** |
| `subfunction_code` | text | queryable scoping |
| `confidence_band` | text | queryable (reservoir policy filter) |
| `reference_formula` | text NULL | Maker context |
| `description_text` | text NULL | Maker context |
| `raw_json` | jsonb NOT NULL | **full raw Mongo doc** (opaque payload — the faithful raw mirror; `co_bindings` retained in raw, stripped at ingest) |
| `source_hash` | text NOT NULL | sha256 of canonicalized raw doc — parity / dedup / drift |
| `source_ref` | text | provenance, e.g. `bc_seed.seed_metrics` |
| `imported_at` / `updated_at` | timestamptz | sync bookkeeping |
| `archived_at` | timestamptz NULL | soft-delete if removed upstream |

~14 columns. Indexes: `uq_seed_metric_mongo_id`; `idx_seed_metric_function` (function_code, subfunction_code) for Gate-0 scoping. **Raw/thin by design — NOT an enriched catalog.** Enrichment stays panel-side.

## 5. Preserve Mongo / raw archive

- **Mongo `bc_seed` / its export = preserved upstream seed archive** (maintained by the bc-sdg seed pipeline). **`mcf.seed_metric` = the operational candidate reservoir** (`raw_json` + `source_hash`). **Runtime / MCF reads Postgres, not Mongo.**
- Optional belt-and-suspenders: a one-time `mongoexport → S3 JSONL (Object Lock / WORM)` immutable archive of `seed_metrics`, matching the platform S3-archive pattern.
- Import is **idempotent** on (`mongo_id`, `source_hash`) → PG is re-syncable from Mongo any time; nothing is lost by importing.

## 6. Effect on Gate 0 + D426 amendment wording

- **Gate 0 becomes:** (a) a small **DBCP** — create `mcf.seed_metric` + import 12,501 raw rows (idempotent, parity-verified); (b) a **PG-backed seed adapter** (or repoint `SeedMetricsAdapter` to read `mcf.seed_metric`) + ingest route/job **filtered by `function_code`**; (c) live ingest→panel test. **It removes** the Mongo-in-`McfModule` wiring (no Mongo runtime dependency in authoring). Net: cleaner runtime, one governed import.
- **D426 amendment bullet (b) wording:** *"`mcf.seed_metric` = operational candidate reservoir, refreshed from `bc_seed.seed_metrics` via a governed import; Mongo / export = preserved upstream seed archive; runtime/MCF reads Postgres."* — **not** "Mongo `seed_metrics` = reservoir."

## 7. Migration proof needed (count / hash / sample parity)

1. **Count parity:** `count(mcf.seed_metric WHERE archived_at IS NULL)` == `bc_seed.seed_metrics.countDocuments()` == 12,501.
2. **Hash parity:** per-row `source_hash = sha256(canonical(raw))`; aggregate hash (sorted concat of per-row hashes, re-hashed) matches on both sides.
3. **Sample parity:** N random `mongo_id`s → deep-equal `raw_json` (PG) vs Mongo doc (after canonicalization).
4. **Idempotency:** re-running the import = 0 inserts/updates (only updates where `source_hash` changed).
5. **Drift = 0:** no Mongo-only (missing) and no PG-only (stale) rows.

## Recommendation

**Adopt the operator's lean: a raw/thin Postgres operational reservoir `mcf.seed_metric`** (`raw_json` + scoping columns + `source_hash`), refreshed from the Mongo seed corpus, with **Mongo / its export preserved as the upstream seed archive** (runtime/MCF reads Postgres, not Mongo). The **panel remains the enricher** (per the 2026-06-07 enrichment experiment). One-time governed import + a refresh job; fully parity-proven. This is the maintainable single-datastore choice and removes a Mongo runtime dependency — at small, bounded cost. **This resolves the reservoir wording for the D426 amendment.**
