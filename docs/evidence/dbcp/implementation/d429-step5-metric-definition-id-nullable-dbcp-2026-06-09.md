---
title: "D429 Step-5 — contract.metric_contract.metric_definition_id Nullable — DDL sub-DBCP (held)"
description: Held DDL sub-DBCP isolating the only schema change the Step-5 ARPI materialization writer needs — make contract.metric_contract.metric_definition_id nullable so MCF-authored metrics (which have no legacy metric_definition) can be written SERVICES-ONLY. Refines the writer DBCP §8 to DROP NOT NULL only (keep the FK, which exempts NULL). This is the D428 §9 implementing DDL. Includes the live schema confirm, golden-snapshot/backward-compat verification, rollback, exact stop conditions, and the OI-1 probe result. DDL proposal only — no apply, no writer, no materialization, no DB mutation.
status: applied
date: 2026-06-09
project: bc-core
domain: contracts
subdomain: metric-store
focus: schema
governs: DEC-61f7c8 (D428 §9) · DEC-a4e550 (Database Change Protocol)
parent: d429-step5-arpi-materialization-writer-dbcp-2026-06-09.md
task: TSK-f06131
---

# D429 Step-5 — `metric_definition_id` Nullable — DDL sub-DBCP

> **✅ APPLIED 2026-06-09T05:55:14Z (operator-approved).** The DDL below was applied to `bc_platform_dev` after a fresh golden snapshot; all post-apply checks pass (see §Apply evidence). This is the **isolated DDL dependency** of the Step-5 writer DBCP (§8 there) and the **D428 §9 implementing DDL** for MCF-authored metric contracts.
>
> ⚠️ **Code-side SSOT drift (tracked, by design):** the live DB column is now nullable, but `src/database/schema/contract/metric-contract.ts` (`.notNull()`) and `docker/redesign/02-contract.sql` (NOT NULL) are **not yet updated** — that reconciliation travels with the held writer PR (TSK-0ba31e) per writer DBCP §8, to honour this gate's "apply DDL only / no writer / no unrelated changes" scope. No runtime break (all 780 rows non-null; the evaluate path never dereferences the column).

## Apply evidence (2026-06-09T05:55:14Z)

| Step | Result |
|---|---|
| Golden snapshot | `bc-core/docker/snapshots/golden-platform-pre-d429-metricdefid-2026-06-09.dump` (**47,496,228 bytes**; `pg_dump --format=custom --compress=9 bc_platform_dev`) |
| Pre-apply | `is_nullable=NO` · FK present · 2 indexes present · **0 NULL / 780 rows** · `idle_in_txn=0` · no active query on the table |
| **DDL applied** | `ALTER TABLE contract.metric_contract ALTER COLUMN metric_definition_id DROP NOT NULL;` → `ALTER TABLE`, exit 0, via `psql` in `bc-postgres` |
| Post-apply 1 | column `is_nullable=YES` ✅ |
| Post-apply 2 | FK `fk_metric_contract__metric_definition` present, definition unchanged ✅ |
| Post-apply 3 | both indexes present (`idx_metric_contract__metric_definition`, `uq_metric_contract__one_active_per_definition`) ✅ |
| Post-apply 4 | 780 rows · 780 non-null · 0 null — existing values unchanged ✅ |
| Post-apply 5 | rolled-back NULL-insert proof: `INSERT 0 1` (781/1 in-tx) → `ROLLBACK` → 780/0 · 0 leftover rows ✅ |
| Post-apply 6 | no authoring (`mcv_created_last_15min=0`) · no materialization (`mcf.metric_contract`=7, `mcf.metric_supersession`=1, unchanged) · no runtime eval · ARPI `b1933c30` still `active` ✅ |

**Rollback (if needed):** `ALTER TABLE contract.metric_contract ALTER COLUMN metric_definition_id SET NOT NULL;` (valid only while 0 NULL rows — archive any MCF NULL-definition row first) + restore Drizzle `.notNull()`; golden-snapshot `pg_restore` as the backstop.

Change record: DevHub report keyed to **TSK-f06131**.

## 1. Current schema (confirmed live, read-only — `bc_platform_dev`)

| Aspect | Live value |
|---|---|
| Column | `contract.metric_contract.metric_definition_id` — `uuid`, **`is_nullable=NO`**, no default |
| FK | **`fk_metric_contract__metric_definition`** — `FOREIGN KEY (metric_definition_id) REFERENCES metric.metric_definition(metric_definition_id)` |
| Index 1 | `idx_metric_contract__metric_definition` — plain btree on `(metric_definition_id)` |
| Index 2 (D068) | `uq_metric_contract__one_active_per_definition` — **UNIQUE** btree on `(metric_definition_id) WHERE archived_at IS NULL` |
| Data | **0 NULL** / **780 total** rows |
| Incoming FKs | **none** reference this column |

(Probe: `bc-core/scripts/_step5-ddl-and-oi1-probe.mjs`, SELECT/`pg_catalog`/`information_schema` only.)

## 2. Proposed minimal DDL — **DROP NOT NULL only (keep the FK + both indexes)**

```sql
ALTER TABLE contract.metric_contract ALTER COLUMN metric_definition_id DROP NOT NULL;
```
+ the Drizzle edit `src/database/schema/contract/metric-contract.ts:25-27` — remove **`.notNull()`** from the column (keep `.references(...)`).

**Refinement vs writer DBCP §8** (which listed *drop FK + nullable*): the FK does **not** need to be dropped. PostgreSQL **exempts NULL from FK enforcement** — an MCF metric written with `metric_definition_id = NULL` passes the FK, while every legacy metric retains full referential integrity for its non-null value. Dropping the FK would *weaken* integrity for any future non-null definition with no benefit. So the minimal, safer change is **one statement**: drop NOT NULL.

**Indexes are unaffected** — both tolerate NULL: the plain btree indexes NULLs; the partial-unique `uq_…` treats NULLs as distinct (PostgreSQL), so multiple NULL-definition active MCs may coexist. The only behavioural consequence: the D068 *one-active-per-definition* guarantee does not apply to NULL-definition MCs (acceptable — the writer creates exactly one ARPI MC; MCF identity is governed in `mcf.*`).

**No data migration** (permissive change; 0 existing rows affected). **No default added** (column stays explicit-or-NULL).

## 3. Why this is the D428 §9 implementing DDL dependency

D428 §9: *"GUARDRAIL: no MCF materialization into contract.* and no legacy wipe until this amendment AND its implementing DBCP(s) are approved"* (`ADR-61f7c8.md:32`). The Step-5 writer (writer DBCP) materializes ARPI into `contract.metric_contract*` SERVICES-ONLY, but `ContractMetricsRepository.createMinimalMetricContract` cannot insert a parent row without a `metric_definition_id` (NOT NULL + FK). An MCF-authored metric has **no legacy `metric.metric_definition`** (the clean-slate intent of D428 is to *not* re-entangle that legacy table). Minting a fake stub is rejected (writer DBCP Q1: it needs `discipline_code` + a composite FK + a service change — worse). So **making the column nullable is the precise, minimal DDL that unblocks MCF materialization without re-entangling legacy** — exactly the "implementing DBCP" §9 names. MCF provenance rides in `contract_json.header.provenance` until/unless a typed `mcf_*` provenance column is added later (writer DBCP OI-5 / option c).

## 4. Runtime / evaluation paths do not dereference `metric_definition_id` (confirmed)

- **Evaluate path: zero references.** `src/boundary/*` (the load+evaluate path: `metric.service.ts` `loadEnvelope`/`normalizeEnvelope`, `metric-evaluation-engine.service.ts`) has **0** matches for `metric_definition_id`/`metricDefinitionId` (grep, this session).
- **Discovery/catalog: passthrough only.** `metric-catalog-reader.repository.ts:153` selects it into the DTO but **never filters/joins** on it; `ChainStatusService` **drops** it from its projection (`chain-status.service.ts:864-871`).
- **Readiness already null-tolerant.** `metric-readiness.service.ts:299-319` explicitly handles `metric_definition_id IS NULL` (orphan banner, not a crash). 44 files reference it — all catalog/inspection/lifecycle surfaces, none in the evaluate path as a required key.
- **No incoming FKs** depend on it (probe).

⇒ Making it nullable breaks **no runtime evaluation reader**. The only visible effect: an MCF MC with NULL definition appears in `getOrphanContracts()` (cosmetic admin banner) and yields no row in the `getDefinitionReadinessList` LEFT JOIN.

## 5. Golden-snapshot + backward-compatibility verification

**Pre-apply (required):**
- Fresh **golden snapshot** of `bc_platform_dev` (`bc-core/docker/redesign/golden-snapshot-*.sql` convention) — the rollback backstop.
- Re-confirm **0 NULL** rows + **no trigger/CHECK** enforces non-null beyond the column NOT NULL (apply-time pre-check; the probe found only the column constraint + the FK).
- Confirm `metric-contract.ts` Drizzle edit is the only code change in the DDL PR (no behaviour change).

**Backward-compat analysis:** the change is **permissive** (NOT NULL → nullable). All 780 existing rows carry non-null values → **unaffected**; the FK still validates them. Drizzle's column type widens to `string | null`; TS callers already null-guard (§4). No reader, gate, or index changes behaviour for existing data.

**Post-apply verification:**
- `information_schema`: `is_nullable='YES'`; FK `fk_metric_contract__metric_definition` still present; both indexes present; row count still **780**, all still non-null.
- **Smoke:** a sample legacy metric (e.g. `mc__revenue_collection_rate`, active) still loads + evaluates unchanged.
- **Nullable proof (rolled-back tx):** an INSERT with `metric_definition_id = NULL` succeeds inside a transaction that is **rolled back** (proves the constraint is gone without leaving a row).

## 6. Rollback plan

- **Revert DDL:** `ALTER TABLE contract.metric_contract ALTER COLUMN metric_definition_id SET NOT NULL;` — succeeds **only if 0 NULL rows exist**, so first archive/remove any NULL-definition MCF row written by the writer (soft-archive via the governed path). The FK was never dropped, so nothing to re-add. Drizzle revert: re-add `.notNull()`.
- **Backstop:** restore the pre-apply golden snapshot.
- No tenant facts are produced by this DBCP (DDL only), so there is nothing downstream to unwind.

## 7. Stop conditions

- **No apply until separately approved** (operator + this DBCP + D428 §9). DDL is gated by the Database Change Protocol (overrides all permission modes).
- **No apply without** a fresh golden snapshot **and** a verified revert script.
- **Do NOT drop the FK** or **either index** (refined scope — drop NOT NULL only).
- **Apply-time pre-check fails** (NULL rows appear, or a trigger/CHECK enforces non-null) → **STOP**, do not force.
- **DDL-only:** this DBCP authors no contract, runs no writer, materializes nothing, writes no `fact.*`/`progression.*`. Those are the writer DBCP's scope, gated separately.
- The writer code PR must not execute until this DDL is **applied** (writer DBCP §6.5).

## 8. No apply until separately approved

This document **proposes** the DDL. Nothing is applied. Apply is a distinct, separately-approved step requiring the golden snapshot (§5) and explicit operator go — consistent with the Database Change Protocol and D428 §9.

---

## OI-1 probe result (read-only — for the writer DBCP precondition §6.2)

**Verdict: GO — no upstream CC-v2 correction required.** The active `cc__customer_invoice_arpi_slice` (`019ea703…`, v1.0.0, `barecount/canonical/v2`) **declares `body.posting_date_field = "document_date"`** — present, equal to the document-date canonical field, and in `field_selection` (`amount`, `document_number`, `document_date`). This is exactly the field the `temporal_anchor` concept resolved to in Slice 0, so the canonical-resolution `enrichFiscalPeriod` step (`canonical-resolution.service.ts:1076`) will stamp `payload.fiscal_period` at evaluation — the writer's `fiscal_period` grain (writer DBCP Q3) is satisfied on the CC side.

**OI-2 (fiscal calendar) — Bar-2 prerequisite, currently UNSEEDED (not a writer-PR blocker).** Platform `master.dim_fiscal_calendar` and `master.dim_fiscal_period` show **0 rows** (approx, `pg_stat_user_tables`). `FiscalCalendarService.resolve` reads `master.dim_fiscal_period` (+ tenant-DB `organization.fiscal_calendar_config`, D368). So **before any actual ARPI evaluation** (Bar 2), the D364 fiscal-calendar seeder must run for the evaluation tenant's calendar, and the tenant must have an active `fiscal_calendar_config`. This is **deferred runtime work**, not a blocker for the writer PR (which reaches platform-ready — active MCV + `chain_verdict='complete'` — without evaluating). Verify + seed at Bar-2 time.

**Net:** OI-1 is cleared → the writer PR is **not** blocked on a CC correction. OI-2 (fiscal seeding) is flagged for Bar-2.

**No DB mutation, no DDL applied, no writer, no materialization. D428 §9 intact. bc-core on `main d92dda3`.**
