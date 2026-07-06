---
uid: metric-context-framework-m11-reservoir-ingestion-dbcp
title: MCF M11 Reservoir Ingestion DBCP
description: Combined design-blueprint for MCF gate M11 (Reservoir Ingestion) per operator-accepted preflight decisions D-M11-1..D-M11-8 (preflight 79142b6). Realizes M11-B — single mcf-owned mcf.metric_authoring_intake_queue durable table + single ReservoirIngestionService with 3 source methods (Mongo bc_seed.seed_metrics + Postgres carve-out metric.metric_definition/metric_knowledge + operator-direct CLI submissions). Substrate change ALL IN ONE NEW TABLE — mcf.metric_authoring_intake_queue (14 columns; 8 constraints — 1 PK + 1 UNIQUE on (reservoir_name, reservoir_entry_id) for idempotency per D-M11-8 + 6 CHECK: reservoir-name enum + confidence-band enum + status enum + co_bindings rejection via JSONB regex per D-M11-5 + co_bindings_stripped_flag forced true + rejected-status-requires-reason) + 3 indexes (status / reservoir_name / ingested_at). NO trigger (no immutability requirement at substrate — status transitions are allowed; service-side discipline governs). NO FKs (substrate leaf — M11 doesn't depend on any other mcf.* table; downstream FK from mcf.metric_authoring_panel_run referencing intake_queue_uid will be added in M12 amendment). New service ReservoirIngestionService with 3 source methods per D-M11-3 + Mongo client reuse strategy per D-M11-2 + 3-layer co_bindings enforcement per D-M11-5 (substrate JSONB regex CHECK + service-side strip + service-side assert) + confidence-band filter (v1 high only per D-M11-6) + APQC subset filter (fixed v1 config per D-M11-7). New CLI script scripts/mcf-m11-operator-direct-ingest.mjs for operator-direct submissions per D-M11-4 (REST endpoint deferred to M12 panel-side write path). 10 operator approvals (O-M11-1..O-M11-10). All atomic inside one BEGIN/COMMIT per M3/M5/M7-M8/M9/M10 atomicity pattern. Rollback file with row-count precondition guard refusing reverse if intake-queue rows exist. Dry-run verifier plan (8 checks; 4 HARD-GATEs). Post-apply verifier plan (15 checks; 5 structural + 9 behavioral SAVEPOINT-protected synthetic-row exercises + 1 cleanup). Unit/integration test plan: per-source adapter normalization + co_bindings strip enforcement + confidence-band filter + APQC subset filter + idempotency catch + integration tests with fake tx. NO bc-core edits this session. NO DDL apply this session. NO Mongo connection attempts this session. NO data writes this session. NO real MCF metric contracts. NO panel implementation. NO M12/M13/M14+ work.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m11-reservoir-ingestion-dbcp
---

# MCF M11 Reservoir Ingestion DBCP

## 1. Scope and grounding

Design the M11 reservoir ingestion substrate + service per the operator-locked preflight recommendations. M11 ships the first **content-flow** gate of the MCF arc — it routes candidate metric proposals from 3 reservoirs into a panel-ready intake queue with full reservoir provenance for downstream M5 mapr binding.

The substrate stays **dormant** post-apply: no ingestion runs are triggered automatically. The service is callable but no real reservoir data is ingested until operator drives an ingest run (manual trigger).

### 1.1 Source documents consumed

| Source | Role |
|---|---|
| M11 preflight (`79142b6`) | Decision options the operator accepted |
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority |
| MCF build plan §M11 | Scope: 3 reservoirs + co_bindings strip + confidence filter + intake queue; T-shirt M; primary risk co_bindings strip bypass |
| MCF addendum §2.3 | Reservoir taxonomy (3 sources) |
| MCF addendum §3.5 | Confidence + APQC filter discipline |
| MCF addendum guardrail #3 | `co_bindings` L3 lock |
| MCF addendum guardrail #6 | Reservoir-provenance fields on panel-run row |
| M5 DBCP `bc-docs-v3 00435c0` §6 | `mcf.metric_authoring_panel_run` reservoir-provenance fields (1:1 mapping target for M11 intake-queue → M12 panel-run binding) |
| M10 closeout `bc-docs-v3 d70f863` | Live state: 16 mcf.* tables, all 0 rows, BCF untouched |
| Live `mcf.*` substrate post-M10 apply | Verified empirically: 16 tables; M11 has no FK dependency on any of them |

### 1.2 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits this session | ✓ — read-only |
| No DDL applied | ✓ — DBCP designs the substrate change; apply is a separate gate |
| No Mongo connection attempts | ✓ — bc-core Mongo client inventory deferred to DBCP review time / impl PR |
| No real MCF metric contracts | ✓ — substrate stays empty |
| No intake-queue rows | ✓ — substrate dormant post-apply |
| No panel runs written | ✓ — M12 owns mapr writes |
| No BCF data touched | ✓ |
| No M12 / M13 / M14+ work | ✓ — downstream gates |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. Accepted operator decisions (D-M11-1..D-M11-8)

| # | Decision | Locked |
|---|---|---|
| **D-M11-1** | ACCEPT M11-B — single durable mcf-owned intake queue table `mcf.metric_authoring_intake_queue` | ACCEPTED |
| **D-M11-2** | Mongo client — reuse existing bc-core Mongo client if inventory at DBCP-review/impl-PR time confirms one; no new dependency unless none exists | ACCEPTED |
| **D-M11-3** | Single `ReservoirIngestionService` with 3 source methods (coordinator+adapters refactor deferred) | ACCEPTED |
| **D-M11-4** | Operator-direct interface = CLI script for v1 (REST endpoint + panel-side direct write deferred to M12 panel implementation) | ACCEPTED |
| **D-M11-5** | 3-layer `co_bindings` enforcement: substrate JSONB regex CHECK + service-side strip + service-side assert | ACCEPTED |
| **D-M11-6** | Confidence-band v1 default = `high` only (expand to `high+medium` post-operator-validation as future amendment) | ACCEPTED |
| **D-M11-7** | APQC subset filter = fixed v1 config (operator-managed via service constructor / env config; not via runtime config table) | ACCEPTED |
| **D-M11-8** | Idempotency key = UNIQUE `(reservoir_name, reservoir_entry_id)` (content-hash dedup deferred to future amendment if cosmetic-only source changes prove problematic) | ACCEPTED |

---

## 3. Current live substrate state

After bc-core `67124e5` + bc-docs-v3 `79142b6`:

| | |
|---|---|
| bc-core main | `67124e5` (M10 evidence merged) |
| bc-docs-v3 main | `79142b6` (M11 preflight) |
| `mcf.*` tables | **16 present, all 0 rows** |
| `mcf.metric_authoring_intake_queue` | does NOT yet exist |
| M2→M10 substrate + services | live; dormant |
| M5 mapr reservoir-provenance fields | live (M5 `00435c0`): `reservoir_name` + `reservoir_entry_id` + `reservoir_provenance_source_json` + `reservoir_confidence_band` — all nullable; all-or-none CHECK; M11 intake-queue fields map 1:1 |
| BCF | untouched (24 panel + 1 rejection log) |
| External reservoirs | `bc_seed.seed_metrics` (Mongo) + `metric.metric_definition` + `metric.metric_knowledge` (Postgres carve-out) — both external to MCF arc; not touched by this DBCP |

### 3.1 No FK dependencies — substrate leaf

`mcf.metric_authoring_intake_queue` is a substrate leaf:
- M11 does NOT depend on any other `mcf.*` table for INSERT (intake rows are self-contained — `reservoir_*` fields are operator-asserted source metadata; no upstream MC/MCV reference)
- Downstream FK from `mcf.metric_authoring_panel_run` referencing `intake_queue_uid` will be added in **M12 amendment** (not in M11 scope)

This is intentional: M11 ships only the substrate + ingestion service; M12 panel implementation will amend `mcf.metric_authoring_panel_run` to add a `consumed_intake_queue_uid` column + FK back to M11's substrate at M12 DBCP time.

---

## 4. M11 ownership boundary

### 4.1 M11 MUST own

| # | Deliverable | Location |
|---|---|---|
| 1 | `mcf.metric_authoring_intake_queue` table (14 columns; per §5) | New DDL `11-mcf-reservoir-ingestion.sql` |
| 2 | 6 CHECK constraints (3 enum + 1 co_bindings rejection + 1 stripped-flag + 1 rejected-status-requires-reason) | Inline in CREATE TABLE |
| 3 | 1 UNIQUE on `(reservoir_name, reservoir_entry_id)` for idempotency per D-M11-8 | Inline |
| 4 | 3 indexes (status_code / reservoir_name / ingested_at) | CREATE INDEX |
| 5 | NO FKs at M11 (substrate leaf — downstream FK in M12 amendment) | n/a |
| 6 | NO trigger at M11 (status transitions allowed; service-side discipline) | n/a |
| 7 | COMMENT ON TABLE | DDL §4 |
| 8 | `ReservoirIngestionService` with 3 source methods per D-M11-3 | New service `bc-core/src/registry/mcf/reservoir-ingestion.service.ts` |
| 9 | Mongo `bc_seed.seed_metrics` adapter (reuse existing bc-core Mongo client per D-M11-2 if inventory confirms; new dedicated reader otherwise) | inline in service |
| 10 | Postgres `metric.metric_definition` + `metric.metric_knowledge` adapter | inline in service |
| 11 | Operator-direct submission adapter | inline in service |
| 12 | 3-layer `co_bindings` enforcement per D-M11-5: substrate JSONB regex CHECK + service-side strip + service-side assert | substrate CHECK + service code |
| 13 | Confidence-band filter (v1 `high` only per D-M11-6) | service code |
| 14 | APQC subset filter (v1 fixed config per D-M11-7) | service code |
| 15 | Idempotency via UNIQUE catch-and-return per D-M11-8 | service code |
| 16 | CLI script for operator-direct submissions per D-M11-4 | `bc-core/scripts/mcf-m11-operator-direct-ingest.mjs` |
| 17 | Drizzle schema + index.ts re-export | `bc-core/src/database/schema/mcf/metric-authoring-intake-queue.ts` + `index.ts` |
| 18 | Dry-run + post-apply verifier scripts | `bc-core/scripts/mcf-m11-dry-run.mjs` + `mcf-m11-post-apply-verification.mjs` |
| 19 | Rollback DDL with row-count precondition guard | `11-mcf-reservoir-ingestion-rollback.sql` |
| 20 | Unit + integration tests | `*.spec.ts` for the service + adapters |

### 4.2 M11 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | Panel authoring / three-model consensus | **M12** |
| 2 | `mcf.metric_authoring_panel_run` writes (M11 doesn't write to mapr; M12 reads from intake-queue at panel-open time and writes mapr) | **M12** |
| 3 | Downstream FK from mapr → intake-queue (`consumed_intake_queue_uid` column + activation) | **M12 amendment** |
| 4 | Fixture authoring | M12 |
| 5 | PE-MC evaluation | M13 |
| 6 | Publication path | M14 |
| 7 | Real MC versions written to `mcf.metric_contract` | gated on M12+M14 |
| 8 | Real verification results | M10 substrate ready; gated on M12+operator runs |
| 9 | BCF concept enrichment | NEVER in MCF gates |
| 10 | Mongo schema changes to `bc_seed.seed_metrics` | external reservoir |
| 11 | Postgres carve-out schema changes to `metric.metric_definition` | external reservoir |
| 12 | Confidence-band re-grading after ingestion | M12 panel re-grades during three-model consensus |
| 13 | REST endpoint for operator-direct submission | deferred to M12 panel-side write path per D-M11-4 |
| 14 | Status-transition triggers / lifecycle constraints | service-side discipline only (status enum CHECK at substrate is sufficient) |
| 15 | Auto-trigger ingestion runs on a schedule | operator manually invokes service / CLI; cron deferred |

---

## 5. Intake table design: `mcf.metric_authoring_intake_queue`

### 5.1 Column inventory (14 columns)

| Column | Type | NULL | Default | Notes |
|---|---|---|---|---|
| `intake_queue_uid` | `uuid` | NOT NULL | `gen_random_uuid()` | PRIMARY KEY |
| `reservoir_name` | `text` | NOT NULL | — | CHECK IN (`'seed_metrics'`,`'metric_definition'`,`'operator_direct'`); maps 1:1 to M5 mapr `reservoir_name` |
| `reservoir_entry_id` | `text` | NOT NULL | — | Source-specific identifier (Mongo `_id` / Postgres `metric_definition_id` / operator submission uid); maps to M5 mapr `reservoir_entry_id` |
| `reservoir_provenance_source_json` | `jsonb` | NOT NULL | — | Full source payload + ingestion metadata (source connection details, ingestion timestamp, adapter version); maps to M5 mapr `reservoir_provenance_source_json` |
| `reservoir_confidence_band` | `text` | NOT NULL | — | CHECK IN (`'high'`,`'medium'`,`'low'`); maps to M5 mapr `reservoir_confidence_band` |
| `apqc_subset_classification_text` | `text` | NULL allowed | — | APQC taxonomy entry if classified; NULL if source didn't carry one |
| `candidate_name` | `text` | NOT NULL | — | Proposed MC name (denormalized from normalized_candidate_json for query efficiency) |
| `candidate_description_text` | `text` | NOT NULL | — | Operator-asserted description / prose |
| `normalized_candidate_json` | `jsonb` | NOT NULL | — | Full normalized IntakeCandidate payload per §7; CHECK rejects `co_bindings` key at any nesting level per D-M11-5 |
| `co_bindings_stripped_flag` | `boolean` | NOT NULL | — | CHECK = TRUE — substrate-level assertion that the strip happened (defense-in-depth with the JSONB CHECK) |
| `status_code` | `text` | NOT NULL | `'pending'` | CHECK IN (`'pending'`,`'consumed_by_panel'`,`'rejected'`,`'superseded'`) |
| `status_reason_text` | `text` | NULL allowed | — | CHECK: NULL OR (status_code='rejected' AND length >= 20) — rejection requires explanation |
| `ingested_at` | `timestamptz` | NOT NULL | `now()` | Ingestion timestamp |
| `ingested_by_name` | `text` | NOT NULL | — | Service identity (`reservoir-ingestion@hostname`) for adapter ingests; operator name for operator-direct CLI ingests |

**Total: 14 columns** (under D162's 20-column max).

### 5.2 Constraint inventory (8 constraints)

| Constraint | Type | Definition |
|---|---|---|
| `maiq_pkey` | PRIMARY KEY | `(intake_queue_uid)` |
| `uq_maiq_reservoir_entry` | UNIQUE | `(reservoir_name, reservoir_entry_id)` — substrate-side idempotency per D-M11-8 |
| `maiq_reservoir_name_chk` | CHECK | `reservoir_name IN ('seed_metrics','metric_definition','operator_direct')` |
| `maiq_confidence_band_chk` | CHECK | `reservoir_confidence_band IN ('high','medium','low')` |
| `maiq_status_code_chk` | CHECK | `status_code IN ('pending','consumed_by_panel','rejected','superseded')` |
| `maiq_co_bindings_rejection_chk` | CHECK | **`NOT (normalized_candidate_json::text ~ '"co_bindings"\s*:')`** — substrate-level co_bindings rejection per D-M11-5; regex catches `"co_bindings":` at any nesting level inside the JSONB serialized form |
| `maiq_co_bindings_stripped_flag_chk` | CHECK | `co_bindings_stripped_flag = TRUE` — substrate forces the flag (defense-in-depth) |
| `maiq_rejected_status_requires_reason_chk` | CHECK | `status_code != 'rejected' OR (status_reason_text IS NOT NULL AND LENGTH(status_reason_text) >= 20)` |

**Total: 8 constraints** (1 PK + 1 UNIQUE + 6 CHECK; **no FKs** per §3.1 / §4.1 substrate-leaf design).

### 5.3 Index inventory (3 indexes)

| Index | Definition | Purpose |
|---|---|---|
| `idx_mcf_maiq_status` | `(status_code)` | M12 panel queries `WHERE status_code = 'pending'` for next-to-consume candidates |
| `idx_mcf_maiq_reservoir_name` | `(reservoir_name)` | Audit / stats by reservoir |
| `idx_mcf_maiq_ingested_at` | `(ingested_at)` | Chronological scan / retention queries |

(`uq_maiq_reservoir_entry` UNIQUE already provides the (reservoir_name, reservoir_entry_id) lookup index.)

### 5.4 No trigger at M11 substrate

Unlike M5/M9/M10 substrates which carry append-only immutability triggers, M11 intake-queue rows are **mutable in `status_code` and `status_reason_text` only** — M12 panel transitions rows from `pending` → `consumed_by_panel`; service-side discipline transitions rejected rows from `pending` → `rejected` with a reason.

Substrate-level constraint enforcement (CHECK on status_code enum + rejected-requires-reason) is sufficient. No trigger needed.

### 5.5 DDL

```sql
CREATE TABLE mcf.metric_authoring_intake_queue (
  intake_queue_uid                  uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  reservoir_name                    text NOT NULL,
  reservoir_entry_id                text NOT NULL,
  reservoir_provenance_source_json  jsonb NOT NULL,
  reservoir_confidence_band         text NOT NULL,
  apqc_subset_classification_text   text,
  candidate_name                    text NOT NULL,
  candidate_description_text        text NOT NULL,
  normalized_candidate_json         jsonb NOT NULL,
  co_bindings_stripped_flag         boolean NOT NULL,
  status_code                       text NOT NULL DEFAULT 'pending',
  status_reason_text                text,
  ingested_at                       timestamptz NOT NULL DEFAULT now(),
  ingested_by_name                  text NOT NULL,

  CONSTRAINT maiq_reservoir_name_chk
    CHECK (reservoir_name IN ('seed_metrics','metric_definition','operator_direct')),
  CONSTRAINT maiq_confidence_band_chk
    CHECK (reservoir_confidence_band IN ('high','medium','low')),
  CONSTRAINT maiq_status_code_chk
    CHECK (status_code IN ('pending','consumed_by_panel','rejected','superseded')),
  CONSTRAINT maiq_co_bindings_rejection_chk
    CHECK (NOT (normalized_candidate_json::text ~ '"co_bindings"\s*:')),
  CONSTRAINT maiq_co_bindings_stripped_flag_chk
    CHECK (co_bindings_stripped_flag = TRUE),
  CONSTRAINT maiq_rejected_status_requires_reason_chk
    CHECK (status_code != 'rejected' OR (status_reason_text IS NOT NULL AND LENGTH(status_reason_text) >= 20)),
  CONSTRAINT uq_maiq_reservoir_entry
    UNIQUE (reservoir_name, reservoir_entry_id)
);

CREATE INDEX idx_mcf_maiq_status ON mcf.metric_authoring_intake_queue (status_code);
CREATE INDEX idx_mcf_maiq_reservoir_name ON mcf.metric_authoring_intake_queue (reservoir_name);
CREATE INDEX idx_mcf_maiq_ingested_at ON mcf.metric_authoring_intake_queue (ingested_at);
```

---

## 6. Reservoir source contracts

### 6.1 Source 1 — Mongo `bc_seed.seed_metrics`

**Adapter signature:**
```typescript
async ingestFromSeedMetrics(opts: { confidenceFilter?: ConfidenceBand[]; apqcSubsets?: string[]; limit?: number }, deps: { tx: Tx }): Promise<IngestSummary>
```

**Source-to-IntakeCandidate mapping:**
- `reservoir_name` = `'seed_metrics'`
- `reservoir_entry_id` = Mongo document `_id` (string-ified)
- `reservoir_provenance_source_json` = full Mongo document + ingestion metadata (collection name, server hostname, adapter version, ingestion timestamp)
- `reservoir_confidence_band` = derived from source confidence indicators per addendum §3.5 (if source doesn't carry one, default to `'medium'` and route to rejected-status if filter excludes)
- `apqc_subset_classification_text` = source's APQC linkage if present
- `candidate_name` = source `metric_name`
- `candidate_description_text` = source `description` / `prose` fields
- `normalized_candidate_json` = source fields stripped of `co_bindings` + standardized to IntakeCandidate shape

### 6.2 Source 2 — Postgres carve-out `metric.metric_definition` + `metric.metric_knowledge`

**Adapter signature:**
```typescript
async ingestFromMetricDefinition(opts: { confidenceFilter?: ConfidenceBand[]; apqcSubsets?: string[]; limit?: number }, deps: { tx: Tx }): Promise<IngestSummary>
```

**Source-to-IntakeCandidate mapping:**
- `reservoir_name` = `'metric_definition'`
- `reservoir_entry_id` = `metric.metric_definition.metric_definition_id` (uuid string)
- `reservoir_provenance_source_json` = JOIN of `metric_definition` + `metric_knowledge` (1:N) + ingestion metadata
- `reservoir_confidence_band` = derived from `metric_definition` confidence fields per addendum §3.5
- `apqc_subset_classification_text` = `metric_definition` APQC linkage
- `candidate_name` = `metric_definition.metric_code` / `display_name`
- `candidate_description_text` = `metric_definition.description_text` + `metric_knowledge` aggregated context
- `normalized_candidate_json` = projected fields stripped of `co_bindings` + standardized

**Critical:** `metric.metric_definition` carries `co_bindings` (legacy). The adapter MUST strip this before constructing the IntakeCandidate. Service-side strip + substrate-side regex CHECK enforce.

### 6.3 Source 3 — Operator-direct submissions (CLI per D-M11-4)

**Adapter signature:**
```typescript
async ingestOperatorDirectSubmission(submission: OperatorSubmission, deps: { tx: Tx }): Promise<IngestSummary>
```

**Source-to-IntakeCandidate mapping:**
- `reservoir_name` = `'operator_direct'`
- `reservoir_entry_id` = operator-supplied uid OR auto-generated `'op-' + crypto.randomUUID()`
- `reservoir_provenance_source_json` = operator submission + CLI metadata (operator name, hostname, CLI version, timestamp)
- `reservoir_confidence_band` = operator self-asserts (still subject to filter discipline)
- `apqc_subset_classification_text` = operator-supplied or NULL
- `candidate_name` + `candidate_description_text` = operator-supplied required fields
- `normalized_candidate_json` = operator submission stripped (defensive — operator shouldn't include co_bindings, but strip happens regardless)

### 6.4 Connection inventory (per D-M11-2)

At DBCP review / impl PR time, the implementer MUST:
1. Check `bc-core` for existing Mongo client (likely under `src/lib/mongo.ts` or similar)
2. If present, REUSE it
3. If absent, add new `MongoClient` from `mongodb` npm package (already a transitive bc-core dep per build plan §M11 assumption)

Either way, the connection details (URL + credentials) come from existing bc-core `.env` patterns; no new env vars added.

---

## 7. Normalized IntakeCandidate contract

### 7.1 TypeScript interface

```typescript
export type ReservoirName = 'seed_metrics' | 'metric_definition' | 'operator_direct';
export type ConfidenceBand = 'high' | 'medium' | 'low';

export interface IntakeCandidate {
  reservoir_name: ReservoirName;
  reservoir_entry_id: string;
  reservoir_provenance_source_json: Record<string, unknown>;
  reservoir_confidence_band: ConfidenceBand;
  apqc_subset_classification_text: string | null;
  candidate_name: string;
  candidate_description_text: string;
  normalized_candidate_json: Record<string, unknown>; // CO_BINDINGS-FREE per L3 lock
  co_bindings_stripped_flag: true; // always true per substrate CHECK
}
```

### 7.2 normalized_candidate_json shape (illustrative — adapter populates per source)

```jsonc
{
  "metric_class": "ratio",                          // adapter-asserted classification
  "proposed_formula_prose": "...",                  // human-readable formula intent
  "proposed_grain_entity_name": "customer",         // adapter-asserted grain candidate
  "proposed_temporal_gate_shape": "instantaneous",  // adapter-asserted temporal gate
  "source_specific_fields": {                       // per-source non-normalized fields preserved for panel context
    "...": "..."
  }
  // co_bindings: NEVER PRESENT (substrate CHECK rejects; service-side asserts absence)
}
```

The shape is intentionally loose — the panel (M12) will refine these into proper MC `formula_ast_canonical_json` + bindings + filters during three-model consensus. M11 just preserves the source's best-effort metadata as ingestion-time evidence.

---

## 8. Provenance and confidence-band rules

### 8.1 Provenance 1:1 mapping to M5 mapr

The 4 reservoir-provenance fields on `mcf.metric_authoring_intake_queue` map **1:1 by column name** to `mcf.metric_authoring_panel_run`:

| intake_queue column | mapr column | Notes |
|---|---|---|
| `reservoir_name` | `reservoir_name` | Same enum values |
| `reservoir_entry_id` | `reservoir_entry_id` | Same string |
| `reservoir_provenance_source_json` | `reservoir_provenance_source_json` | Same JSONB |
| `reservoir_confidence_band` | `reservoir_confidence_band` | Same enum |

**M12 panel will copy these 4 fields from the intake_queue row into the mapr row at panel-open time.** This satisfies addendum guardrail #6 (every reservoir-attributed panel run carries reservoir provenance) + M5 NF1 all-or-none CHECK (all 4 NULL or all 4 NOT NULL).

### 8.2 Confidence-band v1 default per D-M11-6

`high` only. Ingestion service rejects (or marks `rejected` with reason) candidates with `medium` or `low` confidence. Operator-configurable via service constructor:

```typescript
new ReservoirIngestionService({
  allowedConfidenceBands: ['high'],  // v1 default per D-M11-6
  apqcSubsets: ['process_management', 'financial'],  // v1 fixed list per D-M11-7
});
```

Future amendments can broaden the filter without DDL changes (constructor parameter).

### 8.3 APQC subset filter per D-M11-7

Fixed v1 list managed via service constructor (above). Per addendum §3.5, the v1 first-cohort is narrow (specific APQC process groups); operator can expand by changing the constructor param.

Sources without APQC classification are admitted only if the operator-direct path (which has no APQC requirement) is used; adapter-sourced candidates without APQC are routed to `rejected` with reason.

---

## 9. `co_bindings` enforcement (3-layer per D-M11-5)

### 9.1 Layer 1 — substrate JSONB regex CHECK

```sql
CONSTRAINT maiq_co_bindings_rejection_chk
  CHECK (NOT (normalized_candidate_json::text ~ '"co_bindings"\s*:'))
```

Catches `"co_bindings":` substring at ANY nesting level inside the JSONB's text serialization. More aggressive than a top-level `?` operator (which only checks top-level keys).

**Risk:** the regex would also match a string value that happens to be `"co_bindings":` (e.g. a description field saying `"this metric uses 'co_bindings':"`). Practical impact is near-zero — operator-authored descriptions wouldn't accidentally include this exact substring. If false-positive concerns emerge, the v2 substrate amendment can use a JSONB recursive-walk function.

### 9.2 Layer 2 — service-side strip

Before constructing the IntakeCandidate, the adapter:
```typescript
function stripCoBindings(payload: Record<string, unknown>): Record<string, unknown> {
  const stripped: Record<string, unknown> = {};
  for (const [k, v] of Object.entries(payload)) {
    if (k === 'co_bindings') continue;
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      stripped[k] = stripCoBindings(v as Record<string, unknown>);
    } else if (Array.isArray(v)) {
      stripped[k] = v.map((item) =>
        item && typeof item === 'object' && !Array.isArray(item)
          ? stripCoBindings(item as Record<string, unknown>)
          : item,
      );
    } else {
      stripped[k] = v;
    }
  }
  return stripped;
}
```

Recursive strip — removes `co_bindings` at every nesting level.

### 9.3 Layer 3 — service-side assert

After strip, the service asserts the resulting payload's serialized form does NOT contain `"co_bindings":`:
```typescript
function assertCoBindingsStripped(payload: Record<string, unknown>): void {
  const serialized = JSON.stringify(payload);
  if (/"co_bindings"\s*:/.test(serialized)) {
    throw new CoBindingsLeakError(`co_bindings leaked through strip — service bug; payload kept out of intake queue`);
  }
}
```

Sets `co_bindings_stripped_flag = true` only after both strip + assert succeed.

### 9.4 Why 3 layers

- Substrate CHECK is the **last line of defense** — rejects any row where strip failed (service bug, bypass)
- Service-side strip + assert is the **first line of defense** — catches the issue with a clear error before the INSERT
- `co_bindings_stripped_flag = TRUE` substrate CHECK is **operational documentation** — every row asserts strip happened; trivially queryable for audit

---

## 10. Idempotency and status lifecycle

### 10.1 Idempotency per D-M11-8 — UNIQUE `(reservoir_name, reservoir_entry_id)`

Same pattern as M10's `uq_msvr_fixture_version_pkg_hash`:
- Re-ingesting the same `(reservoir_name, reservoir_entry_id)` raises `unique_violation`
- Service catches + SELECTs existing row's `intake_queue_uid` and returns it (idempotent)
- Operator can safely re-trigger ingest runs without duplicate intake rows

### 10.2 Status lifecycle

```
   ┌─────────┐    M12 panel consumes  ┌───────────────────┐
   │ pending │ ─────────────────────> │ consumed_by_panel │
   └─────────┘                        └───────────────────┘
        │
        │ M11 service rejects (filter / strip failure)
        ↓
   ┌──────────┐
   │ rejected │ (status_reason_text >= 20 chars required)
   └──────────┘

   ┌─────────┐    operator manually marks   ┌───────────┐
   │ pending │ ──────────────────────────> │ superseded │
   └─────────┘                              └───────────┘
```

Transitions:
- `pending → consumed_by_panel` — M12 panel UPDATE at panel-open time
- `pending → rejected` — M11 service UPDATE if confidence/APQC filter fails post-INSERT (rare; usually filtered pre-INSERT)
- `pending → superseded` — operator manual UPDATE (e.g. "this candidate is replaced by a newer entry")
- `consumed_by_panel → *` — terminal; panel can't un-consume
- `rejected → *` — terminal
- `superseded → *` — terminal

**Substrate enforces enum + rejected-reason discipline; service governs transitions** (no trigger at substrate; status mutability is intentional).

### 10.3 Re-ingestion after `rejected` / `superseded`

Re-ingesting the same `(reservoir_name, reservoir_entry_id)` always hits the UNIQUE constraint. Operators who want to admit a previously-rejected candidate must:
1. Update the existing row to `superseded` (with reason)
2. Author the new candidate via operator-direct path with a NEW `reservoir_entry_id` (e.g. `'op-<new-uuid>'`)

This preserves the audit trail of why the prior version was rejected/superseded.

---

## 11. ReservoirIngestionService design

### 11.1 Class shape (single service with 3 methods per D-M11-3)

```typescript
// bc-core/src/registry/mcf/reservoir-ingestion.service.ts
import { sql } from 'drizzle-orm';
import { MongoClient } from 'mongodb';

export interface ReservoirIngestionServiceConfig {
  allowedConfidenceBands: ConfidenceBand[];   // v1 default ['high'] per D-M11-6
  apqcSubsets: string[];                       // v1 fixed list per D-M11-7
}

export interface ReservoirIngestionServiceDeps {
  tx: Tx;
  mongoClient?: MongoClient;  // optional — undefined if Mongo unavailable
}

export interface IngestSummary {
  source: ReservoirName;
  candidates_read: number;
  candidates_admitted: number;
  candidates_rejected_confidence: number;
  candidates_rejected_apqc: number;
  candidates_rejected_co_bindings: number;
  candidates_skipped_duplicate: number;  // existing intake_queue row found
  intake_queue_uids: string[];
}

export class ReservoirIngestionService {
  constructor(
    private readonly config: ReservoirIngestionServiceConfig,
    private readonly ingestorIdentity: string = 'reservoir-ingestion@unknown-host',
  ) {}

  async ingestFromSeedMetrics(opts: { limit?: number }, deps: ReservoirIngestionServiceDeps): Promise<IngestSummary>;
  async ingestFromMetricDefinition(opts: { limit?: number }, deps: ReservoirIngestionServiceDeps): Promise<IngestSummary>;
  async ingestOperatorDirectSubmission(submission: OperatorSubmission, deps: ReservoirIngestionServiceDeps): Promise<IngestSummary>;
}
```

### 11.2 Common per-source flow

1. **Read** from source (Mongo / Postgres / operator submission)
2. **Filter** by confidence-band + APQC subset (drop rejected; track counts)
3. **Strip** `co_bindings` recursively (Layer 2)
4. **Assert** `co_bindings` absent (Layer 3)
5. **INSERT** into intake-queue with `co_bindings_stripped_flag = TRUE` + status `pending`
6. **Catch** unique_violation → return existing row UID (idempotent)
7. **Return** `IngestSummary`

### 11.3 Substrate-side idempotency catch pattern (mirrors M10)

```typescript
try {
  const inserted = await tx`INSERT INTO mcf.metric_authoring_intake_queue (...) RETURNING intake_queue_uid`;
  return inserted[0].intake_queue_uid;
} catch (err) {
  if (this.isUniqueViolation(err, 'uq_maiq_reservoir_entry')) {
    const existing = await tx`SELECT intake_queue_uid FROM mcf.metric_authoring_intake_queue WHERE reservoir_name = $1 AND reservoir_entry_id = $2`;
    return existing[0].intake_queue_uid;
  }
  throw err;
}
```

---

## 12. Mongo / Postgres / operator-direct connection patterns

### 12.1 Mongo per D-M11-2

**Inventory at DBCP review / impl PR time:**
- Check `bc-core/src/lib/`, `bc-core/src/db/`, `bc-core/src/registry/` for existing `MongoClient` instantiation
- Search for `from 'mongodb'` imports
- If found: import + reuse the existing connection
- If not found: add `import { MongoClient } from 'mongodb'`; instantiate with `process.env.MCF_SEED_MONGO_URL` (new env var if needed); document in impl PR

**Connection-health check at service construction time:**
```typescript
if (!deps.mongoClient) {
  // Mongo unavailable — service throws on ingestFromSeedMetrics; other paths still work
}
```

The service gracefully degrades — Postgres + operator-direct paths remain functional even if Mongo is unreachable.

### 12.2 Postgres carve-out

Reuses the bc-core Postgres `tx` (per `deps.tx`). Queries `metric.metric_definition` + `metric.metric_knowledge` directly under M11's tx scope. No new connection.

### 12.3 Operator-direct via CLI

Operator runs:
```bash
node scripts/mcf-m11-operator-direct-ingest.mjs --file submission.json
```

The CLI reads the JSON file, validates shape, opens a Drizzle tx, and calls `service.ingestOperatorDirectSubmission(submission, { tx })`. See §13.

---

## 13. Operator-direct CLI script design

### 13.1 Script: `bc-core/scripts/mcf-m11-operator-direct-ingest.mjs`

```javascript
#!/usr/bin/env node
/**
 * M11 Operator-Direct Reservoir Ingestion CLI per D-M11-4.
 *
 * Usage:
 *   node scripts/mcf-m11-operator-direct-ingest.mjs --file submission.json [--operator <name>]
 *
 * submission.json shape:
 *   {
 *     "reservoir_entry_id": "op-<uuid>",            // optional; auto-generated if omitted
 *     "candidate_name": "...",                      // required
 *     "candidate_description_text": "...",          // required
 *     "reservoir_confidence_band": "high",          // required; subject to filter
 *     "apqc_subset_classification_text": "...",     // optional
 *     "normalized_candidate_json": { ... }           // required; co_bindings stripped + asserted
 *   }
 *
 * Exits:
 *   0 — admitted (intake_queue_uid printed)
 *   1 — file not found / JSON invalid
 *   2 — submission shape validation failed
 *   3 — co_bindings leaked through strip (CoBindingsLeakError)
 *   4 — confidence-band filter rejected
 *   5 — APQC subset filter rejected
 *   6 — duplicate (existing row found; existing intake_queue_uid printed; idempotent)
 *   7 — unexpected error
 */
```

### 13.2 Why CLI not REST per D-M11-4

- Lower v1 surface — no new endpoint to secure, audit, rate-limit
- Operator-only authentication (CLI requires shell access to bc-core repo)
- Auditable via shell history + operator-name parameter (recorded in `ingested_by_name`)
- REST endpoint can be added in M12 panel-side write path if operator demand emerges

---

## 14. DDL apply sequence and rollback story

### 14.1 Forward DDL file

`bc-core/docker/redesign/11-mcf-reservoir-ingestion.sql` (single file; whole-file `BEGIN/COMMIT` per M3/M5/M7-M8/M9/M10 atomicity pattern).

### 14.2 Apply sequence (single transaction)

```sql
BEGIN;

-- Step 1: CREATE mcf.metric_authoring_intake_queue (per §5.5)
CREATE TABLE mcf.metric_authoring_intake_queue ( ... );

-- Step 2: 3 indexes per §5.3
CREATE INDEX idx_mcf_maiq_status         ON mcf.metric_authoring_intake_queue (status_code);
CREATE INDEX idx_mcf_maiq_reservoir_name ON mcf.metric_authoring_intake_queue (reservoir_name);
CREATE INDEX idx_mcf_maiq_ingested_at    ON mcf.metric_authoring_intake_queue (ingested_at);

-- Step 3: COMMENT ON TABLE
COMMENT ON TABLE mcf.metric_authoring_intake_queue IS '...';

COMMIT;
```

**3 steps total** (smaller than M10's 6 steps — no FK activation, no comment-on-column correction, no trigger).

### 14.3 Atomicity rationale

All 3 steps commit together or roll back together. Single-table substrate; intra-tx step ordering doesn't matter beyond CREATE TABLE → CREATE INDEX → COMMENT.

### 14.4 Rollback DDL

`bc-core/docker/redesign/11-mcf-reservoir-ingestion-rollback.sql`.

**Precondition guard:**
```sql
DO $$
DECLARE
  intake_count integer;
BEGIN
  SELECT COUNT(*) INTO intake_count FROM mcf.metric_authoring_intake_queue;
  IF intake_count > 0 THEN
    RAISE EXCEPTION 'M11 rollback REFUSED: mcf.metric_authoring_intake_queue has % rows. Drop rows first OR accept data loss with manual override.',
      intake_count USING ERRCODE = 'check_violation';
  END IF;
END $$;
```

**Reversal:**
```sql
BEGIN;
DROP TABLE mcf.metric_authoring_intake_queue;  -- cascades indexes + constraints
COMMIT;
```

No M2-M10 substrate touched.

---

## 15. Drizzle impact

### 15.1 New Drizzle schema file

| File | Purpose |
|---|---|
| `bc-core/src/database/schema/mcf/metric-authoring-intake-queue.ts` | Mirrors §5.5 DDL byte-equivalently |
| `bc-core/src/database/schema/mcf/index.ts` | Export `metricAuthoringIntakeQueue` |

### 15.2 No FKs — no `foreignKey()` declarations needed

M11 substrate is a leaf (no upstream `mcf.*` dependency); no `foreignKey()` calls in the Drizzle schema. Future M12 amendment will add `consumed_intake_queue_uid` to `metric_authoring_panel_run` with a `foreignKey()` declaration referencing `metricAuthoringIntakeQueue.intakeQueueUid`.

### 15.3 Byte-matching DDL discipline

Mirrors M5/M9/M10 — all 6 CHECKs are single-line; no semantic-equivalence carve-out needed.

---

## 16. Dry-run verifier plan

### 16.1 Script

`bc-core/scripts/mcf-m11-dry-run.mjs` (mirrors M5/M9/M10 dry-run pattern).

### 16.2 Checks (8 total)

| # | Check | HARD-GATE? |
|---|---|---|
| #1 | M10 substrate prereq — all 16 mcf.* tables present incl. M10 result table | YES |
| #2 | `mcf.metric_authoring_intake_queue` does NOT yet exist (clean slate) | YES |
| #3 | All 16 mcf.* tables empty (no real rows to displace) | YES |
| #4 | External reservoir reachability advisory (NOT a hard-gate — service is callable even if Mongo unavailable per §12.1) | NO |
| #5 | bc-core Mongo client inventory check (informational only — flags whether reuse OR new dependency per D-M11-2) | NO |
| #6 | DDL parse counts: 1 CREATE TABLE + 3 CREATE INDEX + 1 COMMENT ON TABLE + BEGIN/COMMIT | NO (parse failure aborts) |
| #7 | M5 mapr reservoir-provenance columns present (regression — confirms M5 substrate intact for downstream M12 binding) | NO (advisory) |
| #8 | DDL + rollback sha256 captured | YES |

### 16.3 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All checks PASS |
| 1 | DATABASE_URL not set |
| 2 | DDL file not found |
| 3-10 | Per-check failure |
| 20 | Hard-gate refused |

---

## 17. Post-apply verifier plan

### 17.1 Script

`bc-core/scripts/mcf-m11-post-apply-verification.mjs`.

### 17.2 Checks (15 total — SAVEPOINT-protected from start per M-M5-1 + carrying M9/M10 lessons)

**Structural (1–5):**

| # | Check |
|---|---|
| #1 | `mcf.metric_authoring_intake_queue` present with 14 cols + 6 CHECKs **byte-matched via `pg_get_constraintdef()`** (3 enum + 1 co_bindings regex + 1 flag-forced + 1 rejected-requires-reason) |
| #2 | UNIQUE `uq_maiq_reservoir_entry` on `(reservoir_name, reservoir_entry_id)` present |
| #3 | 3 non-PK / non-UNIQUE indexes present (`idx_mcf_maiq_status` + `idx_mcf_maiq_reservoir_name` + `idx_mcf_maiq_ingested_at`) |
| #4 | NO FK on the new table (substrate-leaf design) |
| #5 | NO trigger on the new table (status transitions allowed; service-side discipline) |

**Behavioral (6–14) — SAVEPOINT-protected synthetic-row exercises:**

| # | Check |
|---|---|
| #6 | Valid INSERT (operator_direct candidate, high confidence, no co_bindings, stripped_flag=true) succeeds; rolls back |
| #7 | (SAVEPOINT) Duplicate `(reservoir_name, reservoir_entry_id)` INSERT → REJECTED by `uq_maiq_reservoir_entry` |
| #8 | (SAVEPOINT) Invalid `reservoir_name` (e.g. `'unknown'`) → REJECTED by `maiq_reservoir_name_chk` |
| #9 | (SAVEPOINT) Invalid `reservoir_confidence_band` (e.g. `'critical'`) → REJECTED by `maiq_confidence_band_chk` |
| #10 | (SAVEPOINT) Invalid `status_code` (e.g. `'queued'`) → REJECTED by `maiq_status_code_chk` |
| #11 | (SAVEPOINT) Payload containing `"co_bindings": [...]` at top level → REJECTED by `maiq_co_bindings_rejection_chk` |
| #12 | (SAVEPOINT) Payload containing `"co_bindings": [...]` at nested level → REJECTED by `maiq_co_bindings_rejection_chk` (regex catches nested) |
| #13 | (SAVEPOINT) `co_bindings_stripped_flag = FALSE` → REJECTED by `maiq_co_bindings_stripped_flag_chk` |
| #14 | (SAVEPOINT) `status_code = 'rejected'` AND `status_reason_text IS NULL` → REJECTED by `maiq_rejected_status_requires_reason_chk` |

**Cleanup (15):**

| # | Check |
|---|---|
| #15 | All 17 mcf.* tables (16 pre-M11 + 1 new M11) empty after verifier; BCF 24+1 untouched |

### 17.3 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All 15 checks PASS |
| 1 | DATABASE_URL not set |
| 3-17 | Per-check failure |
| 18 | Unexpected error |

---

## 18. Unit / integration test plan

### 18.1 Unit tests

| File | Coverage |
|---|---|
| `reservoir-ingestion.service.spec.ts` | Service-level orchestration tests with fake tx + mocked adapters |
| `seed-metrics-adapter.spec.ts` | Mongo adapter normalization (with fake `MongoClient`); co_bindings strip + assert; confidence + APQC filter |
| `metric-definition-adapter.spec.ts` | Postgres adapter normalization (with fake tx); co_bindings strip + assert; confidence + APQC filter |
| `operator-direct-adapter.spec.ts` | Operator submission normalization; defensive co_bindings strip |
| `co-bindings-strip.spec.ts` | `stripCoBindings()` helper unit tests — top-level, nested, array of objects, deeply nested |

### 18.2 Integration tests

| File | Coverage |
|---|---|
| `reservoir-ingestion.service.integration.spec.ts` | Full ingestion flow with fake tx + queued responses (M5/M9/M10 pattern); per-source paths; idempotency catch on duplicate UNIQUE; filter rejection paths |

### 18.3 CLI script tests

`scripts/mcf-m11-operator-direct-ingest.spec.mjs` — input validation; JSON parse errors; expected exit codes per shape failure mode.

### 18.4 Reproducibility / property-style cross-checks

- Same source payload + same filter config → same intake_queue row (idempotent)
- co_bindings strip is deterministic (same input → byte-equal stripped output)

---

## 19. Risks and mitigations

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M11-1 | **`co_bindings` strip bypass** — direct writes to intake-queue from non-service paths | Medium (per build plan §M11 primary risk) | 3-layer enforcement per D-M11-5 (substrate JSONB regex CHECK + service strip + service assert); operational DB GRANT restriction in production environment |
| R-M11-2 | **JSONB regex CHECK false-positive** — a description string containing literal `"co_bindings":` substring triggers rejection | Low | Practical risk near-zero (operator-authored descriptions won't include this exact substring); v2 substrate amendment can use a recursive JSONB walk function if false-positives emerge |
| R-M11-3 | **Mongo client unavailable** — bc-core has no existing Mongo client AND new dependency rejected | Medium | Service gracefully degrades — Postgres + operator-direct paths remain functional; impl PR includes connection-health check + clear error message if `ingestFromSeedMetrics` invoked without Mongo client; alternative: new dependency added per D-M11-2 fallback |
| R-M11-4 | **Confidence-band v1 too restrictive** — `high` only filter excludes important medium-confidence candidates | Low | v1 default per D-M11-6 chosen for operator-validation cohort; constructor-configurable; future amendment relaxes without DDL change |
| R-M11-5 | **APQC subset filter excludes important metrics** | Low | Operator-managed v1 fixed list per D-M11-7; constructor-configurable; expand as operator demand emerges |
| R-M11-6 | **Reservoir schema drift** — upstream `bc_seed.seed_metrics` or `metric.metric_definition` evolves | Medium | Per-adapter normalizer absorbs source-schema changes; impl PR includes schema-snapshot fixtures for both sources; adapter unit tests catch drift |
| R-M11-7 | **Idempotency key under-discriminates** — same Mongo `_id` reused across collections | Low | UNIQUE on `(reservoir_name, reservoir_entry_id)` discriminates by source; cross-reservoir `_id` collision unlikely; if it happens, operator-direct override path with new uid |
| R-M11-8 | **Status lifecycle bypass** — service updates status without checking valid transitions | Low | Status transitions governed by service-side discipline (no substrate trigger); impl PR ships per-transition guard methods; future amendment can add substrate trigger if abuse emerges |
| R-M11-9 | **CLI operator-direct discoverability** — operator doesn't know to use the CLI; submits via REST or panel | Low | CLI is v1 only per D-M11-4; M12 panel may add REST endpoint as part of panel-side write path; operator documentation in CLI script header |
| R-M11-10 | **Substrate-side regex CHECK performance at scale** | Low | Intake-queue is bounded (hundreds-to-thousands of rows, not millions); regex check is cheap relative to JSONB validation overall; queryable via EXPLAIN if perf concerns |

### 19.1 Stop conditions

- bc-core Mongo client inventory at DBCP review time reveals no existing client AND operator rejects new dependency → service ships without Mongo path (Postgres + operator-direct only); document explicitly in impl PR
- `metric.metric_definition` schema differs significantly from build-plan assumptions → adapter normalization needs operator validation before impl PR proceeds
- §19.13 operator-question landings affect filter design

---

## 20. Operator approvals for implementation PR (O-M11-1..O-M11-10)

Before the M11 implementation PR opens, the operator approves these 10 items:

| # | Approval item |
|---|---|
| **O-M11-1** | Confirm D-M11-1 (M11-B single mcf-owned intake queue table) |
| **O-M11-2** | Confirm `mcf.metric_authoring_intake_queue` 14-column shape + 8 constraints (1 PK + 1 UNIQUE + 6 CHECK; no FKs) + 3 indexes |
| **O-M11-3** | Confirm 3-layer `co_bindings` enforcement (substrate JSONB regex CHECK + service strip + service assert) per D-M11-5 |
| **O-M11-4** | Confirm UNIQUE `(reservoir_name, reservoir_entry_id)` idempotency key per D-M11-8 |
| **O-M11-5** | Confirm single `ReservoirIngestionService` with 3 source methods per D-M11-3 |
| **O-M11-6** | Confirm Mongo client reuse strategy per D-M11-2 (inventory at DBCP-review / impl-PR time; reuse if found; new dependency if not — operator approves either path) |
| **O-M11-7** | Confirm operator-direct CLI per D-M11-4 (REST endpoint deferred) |
| **O-M11-8** | Confirm confidence-band v1 default `high` only per D-M11-6 + APQC subset fixed v1 config per D-M11-7 |
| **O-M11-9** | Confirm DDL atomicity (single BEGIN/COMMIT; 3 steps); rollback row-count precondition guard |
| **O-M11-10** | Approve the next gate: M11 implementation PR (NO DB APPLY) |

---

## 21. Recommended next gate

### 21.1 Recommendation: open M11 implementation PR (NO DB APPLY)

The implementation PR ships:

**Substrate:**
1. `bc-core/docker/redesign/11-mcf-reservoir-ingestion.sql` (forward DDL per §14.2)
2. `bc-core/docker/redesign/11-mcf-reservoir-ingestion-rollback.sql` (rollback per §14.4)
3. `bc-core/src/database/schema/mcf/metric-authoring-intake-queue.ts` (Drizzle per §15.1)
4. `bc-core/src/database/schema/mcf/index.ts` (re-export)
5. `bc-core/scripts/mcf-m11-dry-run.mjs` (8 checks per §16.2)
6. `bc-core/scripts/mcf-m11-post-apply-verification.mjs` (15 checks per §17.2 — SAVEPOINT-protected from start)

**Service + adapters + tests:**
7. `bc-core/src/registry/mcf/reservoir-ingestion.service.ts` (orchestrator per §11)
8. `bc-core/src/registry/mcf/seed-metrics-adapter.ts` (Mongo adapter)
9. `bc-core/src/registry/mcf/metric-definition-adapter.ts` (Postgres adapter)
10. `bc-core/src/registry/mcf/operator-direct-adapter.ts` (operator submission adapter)
11. `bc-core/src/registry/mcf/co-bindings-strip.ts` (recursive strip helper)
12. Matching `*.spec.ts` files for each (per §18)
13. `bc-core/src/registry/mcf/reservoir-ingestion.service.integration.spec.ts` (per §18.2)

**CLI:**
14. `bc-core/scripts/mcf-m11-operator-direct-ingest.mjs` (CLI per §13.1)

**Suggested PR title:** `feat(mcf): M11 Reservoir Ingestion — intake queue substrate + ingestion service + CLI (NO DB APPLY)`

### 21.2 Sequencing per established pattern

1. M11 DBCP → operator review → 10 approvals O-M11-1..O-M11-10 ← **THIS DBCP**
2. M11 implementation PR (NO DB APPLY) — combined per §21.1
3. M11 small-DDL apply gate (separate operator-authorized session)
4. M11 evidence PR + bc-docs-v3 closeout
5. M11 substrate dormant; M12 panel implementation begins (parallel-eligible with M11 apply once M11 substrate ships)

### 21.3 What unblocks after M11

- **M12** Metric Authoring Panel — can begin consuming intake-queue rows
- **M11+M12** combined enables real reservoir-attributed panel runs (first content-flow milestone)

---

## 22. What stays closed

| | |
|---|---|
| M11 impl PR | not opened by this DBCP |
| M11 DDL apply | pending impl PR |
| M11 evidence PR | pending apply |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M11 substrate (then parallel-eligible) |
| **M12 amendment adding `consumed_intake_queue_uid` to mapr + FK back to M11** | CLOSED — M12 owns |
| **M13 PE-MC evaluator** | CLOSED — gated on M11 + M12 + M10 |
| **M14+** | CLOSED |
| **Real MCF metric contracts** | CLOSED — substrate stays empty pending M12+operator runs |
| **Real intake-queue rows** | CLOSED — substrate dormant post-apply; operator triggers ingestion runs manually |
| **BCF data changes** | CLOSED — 24 BCF panel + 1 rejection log untouched throughout MCF arc |
| **Mongo schema changes** | NEVER — external reservoir |
| **Postgres `metric.*` carve-out schema changes** | NEVER — external reservoir |
| **REST endpoint for operator-direct submission** | DEFERRED to M12 per D-M11-4 |
| **Coordinator + adapters refactor** | DEFERRED — single service v1 per D-M11-3 |
| **Status-transition substrate trigger** | DEFERRED — service-side discipline v1; future amendment if abuse emerges |
| **Confidence-band re-grading at ingestion** | CLOSED — M12 panel re-grades during consensus |
| **Auto-scheduled ingestion runs (cron)** | DEFERRED — operator-manual v1 |
| **MCF defect-code v2 taxonomy** | CLOSED |
| **MCF hash algorithm v2 bump** | CLOSED — `mcf-hash-v1` forever-locked |
| **MCF verifier algorithm v2 bump** | CLOSED — `mcf-verifier-v1` forever-locked |
