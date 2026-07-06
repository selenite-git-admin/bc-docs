---
title: "MCF Gate 0 — PG Seed Reservoir (mcf.seed_metric) — DBCP"
description: Database Change Protocol to create/import/wire mcf.seed_metric as the operational MCF candidate reservoir (raw/thin Postgres mirror of the Mongo/export seed archive), replacing the dormant Mongo runtime path. Docs/DBCP only — no code, no DB writes, no migration. Apply is gated on explicit operator approval. Enacts DEC-61f7c8/D428 Gate 0.
status: implemented
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: metric-store
focus: seed-reservoir
---

# MCF Gate 0 — PG Seed Reservoir (`mcf.seed_metric`) — DBCP (IMPLEMENTED)

> ✅ **IMPLEMENTED — Gate 0 CLOSED (2026-06-07).** Merged to bc-core `main` @ `6d8c083` (PR #233, squash). `mcf.seed_metric` is live with **12,501 active seeds**; the operational candidate reservoir is **Postgres**, not Mongo-at-runtime; seed status is **master-backed** (`master.master_status` context `mcf_seed_metric`, 8 statuses, no table CHECK); `POST /api/mcf/intakes/from-seed` is **rerun-safe** (skips already-ingested seeds). Parity G0-V1…V5 + live proof G0-V6 passed. **No legacy wipe, no `contract.*` materialization, no D400/D401/D427** — those remain later, separately-approved gates. Non-blocking follow-up: `TSK-6dda6f` (operator-direct duplicate idempotency). Evidence: `bc-core/scripts/audit-output/mcf-gate0-*.json`. *(Original DBCP text preserved below for the record.)*

## Authority
- **ADR:** DEC-61f7c8 / D428 (store amendment) · DEC-3f093f / D426 · DEC-c3e57f / D422.
- **Design:** `mcf-seed-reservoir-postgres-design-2026-06-07.md` (recommendation) · `mcf-enrichment-experiment-2026-06-07.md` (E2: panel self-enriches from thin seeds).
- **DB rules:** DEC-1918d0 / D162 (10 rules) · naming DEC-69f09e / D148 · DDL SoT = `bc-core/docker/redesign/*.sql` (Drizzle must match on apply).
- **Protocol:** Database Change Protocol (CLAUDE.md) — table create requires explicit approval before apply.

## Objective
Create / import / wire **`mcf.seed_metric`** as the **operational MCF candidate reservoir** — a raw/thin Postgres mirror refreshed from the **Mongo/export preserved upstream seed archive**. MCF intake reads Postgres, not Mongo. The panel remains the enrichment mechanism.

## Scope
- **IN:** new table `mcf.seed_metric`; one-time import (~12,501) from the seed archive with parity; idempotent refresh; PG-backed seed adapter (repoint) + function/subfunction-scoped intake route/job; one live seed→intake→panel proof.
- **OUT (explicit locks):** no batch enrichment (panel = enricher); no legacy `metric.*`/`contract.*` wipe; no MCF→`contract.*` materialization; no D400/D401/D427; no tenant/runtime/engine change.

## Decisions
| # | Decision |
|---|---|
| G0-D1 | Table = **`mcf.seed_metric`** (singular, `mcf` schema). Reservoir enum value `reservoir_name='seed_metrics'` preserved for compatibility with the existing intake substrate. |
| G0-D2 | **Raw/thin:** queryable scoping columns + `raw_json` (opaque payload) + `source_hash`. **No enrichment columns** (no `definition_summary`/`formula_explanation`/etc.). |
| G0-D3 | Import source = **Mongo `bc_seed.seed_metrics`** (= preserved upstream seed archive). PG = operational reservoir; runtime/MCF reads PG. |
| G0-D4 | **Idempotent** on `mongo_id`, with `source_hash` change-detection; `archived_at` for upstream deletions. |
| G0-D5 | **Adapter repoint:** the existing `ReservoirIngestionService` already exposes 3 source methods; swap the seed source's data access from a Mongo collection to a **PG read of `mcf.seed_metric`** (tx-based), preserving the `co_bindings` strip (Layer-2/3) + `IntakeCandidate` mapping. `McfModule` injects `CONTROL_PLANE_DB` (already present) instead of a Mongo collection. The dormant `ingestFromSeedMetrics(mongoCollection)` is removed or left unwired. |
| G0-D6 | Ingest is **`function_code`-scoped** (optional `subfunction_code`) so a wave targets a pilot slice (e.g. `finance`), never a 12,501-row dump. |

## 1. Table shape — `mcf.seed_metric` (DDL proposal; NOT applied)
~15 columns (≤20 per D162); snake_case (D148); `archived_at` soft-delete; no queryable JSONB (`raw_json` is opaque payload, allowed); no FK out (reservoir staging keyed to the external archive by `mongo_id`).

```sql
-- PROPOSAL — apply only after approval; mirror in Drizzle + docker/redesign DDL.
CREATE TABLE mcf.seed_metric (
  seed_metric_id     uuid PRIMARY KEY DEFAULT gen_random_uuid(),  -- or house uid generator
  mongo_id           text        NOT NULL,                        -- bc_seed.seed_metrics _id (lineage key = reservoir_entry_id)
  metric_name        text        NOT NULL,                        -- queryable
  display_name       text,
  function_code      text,                                        -- queryable (Gate-0 scoping)
  subfunction_code   text,                                        -- queryable (scoping)
  confidence_band    text,                                        -- queryable (reservoir policy filter)
  reference_formula  text,                                        -- Maker context (nullable)
  description_text   text,                                        -- Maker context (nullable)
  raw_json           jsonb       NOT NULL,                        -- full raw archive doc (opaque payload)
  source_hash        text        NOT NULL,                        -- sha256(canonical(raw_json)) — parity/dedup/drift
  source_ref         text        NOT NULL DEFAULT 'bc_seed.seed_metrics',
  imported_at        timestamptz NOT NULL DEFAULT now(),
  updated_at         timestamptz NOT NULL DEFAULT now(),
  archived_at        timestamptz,                                 -- set when row removed upstream
  CONSTRAINT uq_seed_metric_mongo_id UNIQUE (mongo_id)
);
CREATE INDEX idx_seed_metric_function ON mcf.seed_metric (function_code, subfunction_code) WHERE archived_at IS NULL;
CREATE INDEX idx_seed_metric_source_hash ON mcf.seed_metric (source_hash);
```

## 2. Import from Mongo/export + parity
- **Procedure (one-time, then refresh):** read the seed archive (Mongo `bc_seed.seed_metrics`, or a `mongoexport` JSONL snapshot) → for each doc upsert `(mongo_id, metric_name, display_name, function_code, subfunction_code, confidence_band, reference_formula, description_text, raw_json, source_hash)`. `source_hash = sha256(canonicalized raw doc)`.
- **Parity gates (must all pass before cutover):**
  - **G0-V1 count:** `count(mcf.seed_metric WHERE archived_at IS NULL)` == archive `countDocuments()` (≈ 12,501).
  - **G0-V2 aggregate hash:** `sha256(sorted concat of per-row source_hash)` matches on PG vs archive.
  - **G0-V3 sample:** N (≥20) random `mongo_id`s → `raw_json` (PG) deep-equals the archive doc after canonicalization.
  - **G0-V4 drift = 0:** no archive-only (missing) and no PG-only (stale) `mongo_id`s.

## 3. Idempotent refresh behavior
- Re-run is **upsert by `mongo_id`**: insert new; update **only** where `source_hash` changed (touch `updated_at`); set `archived_at` for `mongo_id`s absent upstream; **0 duplicates** (enforced by `uq_seed_metric_mongo_id`).
- A clean re-run on an unchanged archive produces **0 inserts / 0 updates / 0 archives** (G0-V5). Safe to re-run anytime; PG is a derived mirror — nothing is lost by re-importing.

## 4. PG-backed seed adapter / repoint plan
- **No new pipeline.** `ReservoirIngestionService` keeps its shape; the **seed source's data access** changes from `MongoCollectionLike.find().limit().toArray()` to a tx-based PG read:
  `SELECT … FROM mcf.seed_metric WHERE archived_at IS NULL AND function_code = $1 [AND subfunction_code = $2] ORDER BY metric_name LIMIT $n`.
- Map each row → `IntakeCandidate` exactly as today (`reservoir_name='seed_metrics'`, `reservoir_entry_id=mongo_id`, `normalized_candidate_json` from `raw_json` minus `co_bindings`; **Layer-2 strip + Layer-3 assert preserved**).
- `McfModule`: inject `CONTROL_PLANE_DB` into the seed adapter (already available); **drop the Mongo collection wiring**. `ingestFromSeedMetrics(mongo)` removed or left unwired.
- Confidence/APQC policy unchanged (`allowedConfidenceBands: ['high','medium','low']`, `rejectMissingApqc: false`) — seed docs lack APQC, which is admitted.

## 5. Function/subfunction-scoped ingest route / job
- **Route:** `POST /api/mcf/intakes/from-seed` (platform-admin, role-guarded) — body `{ function_code, subfunction_code?, limit? }` → reads `mcf.seed_metric` (scoped) → `ingestFromSeed*` → intake-queue rows. Mirrors the existing `from-metric-definition` route pattern + envelope.
- **Or batch job:** same query, operator-invoked, scoped by `function_code`. Either way: **never an unfiltered 12,501-row ingest.**

## 6. Live proof (one metric)
- Pick **one finance/AR seed** from `mcf.seed_metric` → ingest via the seed route → **M12 panel** → inspect the Maker proposal. Reuses the path proven 2026-06-07 (`panel_run b85186ef` / `088e22f9` used operator-direct; this proves the **seed** source end-to-end).
- **Acceptance (G0-V6):** intake row created with `reservoir_name='seed_metrics'` + `reservoir_entry_id=<mongo_id>`; panel runs to a verdict with `defect_code=null`; Maker self-grounds via BCF tool calls (claims + tool_calls > 0). A clean `APPROVE_FOR_DRAFT` is a bonus, not required (per the experiment, predicate/grammar metrics may route to OPERATOR_REVIEW — a separate gate, not a reservoir failure).

## 7. Rollback
- `DROP TABLE mcf.seed_metric` (no FK in; nothing depends on it pre-cutover) → reverts the schema change cleanly.
- Revert the adapter/route via `git revert` of the impl PR.
- **The Mongo/export seed archive is untouched** → **zero data loss** (PG is a derived mirror; re-importable). The dormant Mongo path can be re-wired if ever needed.

## 8. Guardrails (locks — restated)
- **Single-seed live proof (Gate-0 scope lock).** Gate-0 live proof invokes M12 on exactly one selected seed only. No batch panel execution, no bulk authoring, and no unfiltered 12,501 ingest during Gate 0. Broader ingestion/authoring requires a separate operator-approved wave.
- **No batch enrichment.** The **panel is the enrichment mechanism** (E2 validated). `mcf.seed_metric` is raw/thin; `metric_knowledge` is **not** reproduced here.
- **No legacy wipe and no `contract.*` materialization** in this gate. Those are later, separately-approved DBCPs (D428 sequence steps 5–6).
- **Runtime engine unchanged**; **D400 / D401 / D427 remain separate gates.**

## 9. Acceptance / verification gates (summary)
| Gate | Pass condition |
|---|---|
| G0-V1 | count parity == archive count (≈12,501) |
| G0-V2 | aggregate `source_hash` parity (PG == archive) |
| G0-V3 | ≥20-sample `raw_json` deep-equal |
| G0-V4 | drift = 0 (no missing / no stale) |
| G0-V5 | idempotent re-run = 0 inserts/updates/archives on unchanged archive |
| G0-V6 | live seed→intake→panel: intake `reservoir_name='seed_metrics'`, panel `defect_code=null`, Maker self-grounds |

## Database Change Protocol (apply gate)
This DBCP proposes **one table create + one import + adapter/route wiring**. **No apply until explicit operator approval.** On approval, the apply sequence is: (1) update Drizzle schema + `docker/redesign` DDL to match §1; (2) golden snapshot; (3) create table + run import; (4) verify G0-V1…V5; (5) wire adapter/route; (6) live proof G0-V6; (7) report. Rollback per §7 at any step.
