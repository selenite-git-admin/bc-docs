---
uid: d418-gate-5-physical-disposition-dbcp-design
title: D418 Gate 5 — Physical Disposition DBCP design
description: Design-only DBCP note for physically disposing of the D417/D418 quarantined legacy vocabulary and runtime surfaces. Recommends DEC-f48f99 Path C (migrate/denormalize audit context before BO drop) as the disposition strategy for the two historical FK sinks. Specifies the 7 tables + 1 column in scope, the 2 dependent FK columns on non-quarantined tables that must also drop to avoid dangling UUIDs, the carve-outs, the FK dependency inventory, the proposed DDL sequence by phase, the dry-run evidence required for Gate 5.1, the apply safety + rollback story for Gate 5.2, post-apply verification, and stop conditions. Design only — no code, no DDL execution, no DB writes, no migrations. status proposed; awaiting operator review-back.
status: proposed
date: 2026-05-25
project: bc-docs
domain: contracts
subdomain: quarantine-and-retirement
focus: governance
---

# D418 Gate 5 — Physical Disposition DBCP design

> **What this is.** The **Gate 5.0** design — the DBCP/design note for physically
> disposing of the **D417/D418 quarantined legacy vocabulary and runtime surfaces**
> from the platform DB. It elaborates the consequences clause in
> **DEC-f48f99 / D419** (Historical FK Sink Classification) and proposes the
> concrete DDL sequence. **Design only** — no code, no DDL execution, no DB
> writes, no migrations, no bc-core / bc-admin / bc-ai changes. `status: proposed`
> — awaiting operator review-back before opening Gate 5.1 (dry-run).

## 1. Scope and grounding

This Gate 5.0 design closes the loop that the D417/D418 retirement chain opened
operationally but did not close physically. After 16 merged PRs across bc-core
and bc-admin plus one ADR in bc-docs-v3 (DEC-f48f99 / D419), the legacy
substrate is **operationally neutralized but physically retained**: every active
legacy runtime row referencing a quarantined surface has been archived (Gate
1.2, 686 rows); every active read path that surfaced quarantined data is
filtered, removed, or formally allowlisted as historical/audit (Gates 1.3.1 →
1.3.3); every authoring UI that wrote to the quarantined substrate is gone
(Gates 2, 2.5-A/B, 2.6, 2.7-A/B). The bc-core boot is clean post-removal.
What remains is the schema itself.

This document proposes the **physical disposition** — the literal `DROP TABLE`
sequence — under the **operator-preferred path**: DEC-f48f99 Path C
(migrate/denormalize audit context before BO drop). Paths A (drop FK only,
leave dangling UUIDs) and B (cascade-delete audit history) are documented for
completeness but **not recommended**.

### Grounding

| Artifact | Role |
|---|---|
| ADR **DEC-6c57e2 / D417** | Legacy vocabulary stack quarantine. §2 enumerates the 7 tables + 1 column in scope. Authoritative for "what is quarantined." |
| ADR **DEC-a19428 / D418** | Pre-production legacy active-runtime retirement. Authorized the Gate 1.2 archival. |
| ADR **DEC-f48f99 / D419** | Historical FK sink classification. §Consequences §"Gate 5" specifies path A/B/C and defers the path selection to Gate 5 time. |
| bc-core **PR #88** (`fc19605`) | Gate 1.2 archival apply: 42 CC + 589 MC + 55 OC + 0 Reader = 686 rows archived. |
| bc-core **PR #94** (`1cc6ba5`) | Gate 1.3.3 audit script + clean re-run. The script is now committed and reproducibly verifies 5/5 PASS. |
| bc-admin **PRs #11–#14** | Business Chain UI removal (Gate 2), BO-bound wizard retirement (Gate 2.5-A), orphan cleanup (Gate 2.6), metric-contract wizard retirement (Gate 2.7-A). |
| bc-core **PRs #89–#95** | Static read cleanup (Gates 1.3.1 A/B/C/D-1), wizard backend retirement (Gates 2.5-B + 2.7-B). |

The combined effect of these 16 PRs is the **pre-condition** for Gate 5: no
active authoring surface, no active runtime surface, no active read path, no
in-flight wizard sessions, no test that exercises a write to the quarantined
substrate. The Gate 1.3.3 audit script reproducibly proves this state and
gates any regression.

## 2. Tables in physical-disposition scope

Per **DEC-6c57e2 / D417 §2**, the quarantined substrate consists of **7 tables**:

| # | Schema.Table | Rows (as of Gate 1.3.3 re-run) | Notes |
|---|---|---|---|
| 1 | `contract.business_field` | reference | "BF" — ISO 11179 field registry |
| 2 | `contract.business_object` | reference | "BO" — domain concept definitions |
| 3 | `contract.business_field_alias` | 1,962 (internal-quarantine FK to BF) | BF alias mappings |
| 4 | `contract.business_object_field` | 6,352 (internal-quarantine FK to BO + BF) | BO ↔ BF composition |
| 5 | `contract.business_object_relation` | 59 (internal-quarantine self-FK on BO) | BO ↔ BO relations |
| 6 | `contract.canonical_field` | reference | "CF" — canonical field registry |
| 7 | `contract.cc_field_mapping` | 1,614 / 1,616 (internal-quarantine FK to BF + CF + CC) | "CM" — CC field mapping |

Plus **1 column** in column-level scope:

| Schema.Table.Column | Notes |
|---|---|
| `contract.observation_field_map.business_field_id` | Per D417 §2 — the column is quarantined, the table itself stays |

### Dependent FK columns on non-quarantined tables (must also drop)

The D418 archival predicates archived rows that had these FK columns non-null,
but the columns themselves remain on the (non-quarantined) parent tables.
Dropping the BO table requires dropping these FK constraints (or the columns
themselves). Per operator instruction, **drop the COLUMNS** to avoid leaving
dangling FK-less UUIDs:

| Schema.Table.Column | Non-null active rows | Archived rows with this column non-null | Disposition |
|---|---|---|---|
| `contract.canonical_contract.object_id` | 0 (Gate 1.2 archived all 42 BO-bound CCs) | 42 | DROP COLUMN |
| `runtime.reader.business_object_id` | 0 (Gate 1.2 archived all 0 BO-bound readers) | 0 | DROP COLUMN |

The 42 archived CC rows still carry their `archived_at` timestamp; they're
historical evidence and stay. Only the now-meaningless `object_id` column is
removed.

## 3. Tables explicitly out of scope / carve-outs

Per **DEC-6c57e2 §5** carve-outs + **DEC-f48f99** historical FK sinks:

| Surface | Rationale |
|---|---|
| `operations.bo_enrichment_log` | **Historical FK sink** per DEC-f48f99. Audit trail. **Preserved**; FK to BO handled via Path C migration (see §5). |
| `operations.bo_verification_log` | **Historical FK sink** per DEC-f48f99. Audit trail. **Preserved**; FK to BO handled via Path C migration. |
| `contract.canonical_contract` (base table) | Non-quarantined surface. 42 archived BO-bound rows stay archived; surviving non-BO rows continue to be active. |
| `contract.metric_contract` (base table) | Non-quarantined. 589 archived BO-binding-transitive rows stay archived; surviving rows active. |
| `contract.observation_contract` (base table) | Non-quarantined. 55 archived BF-bound rows stay archived; surviving rows active. |
| `runtime.reader` (base table) | Non-quarantined. Survives sans `business_object_id` column. |
| `contract.observation_field_map` (base table) | Non-quarantined. Survives sans `business_field_id` column (per D417 §2 column-level scope). |
| `contract.source_contract` + `admission_contract` + their versions/approvals | Source/admission contract family preserved per DEC-6c57e2 §5. |
| `contract.canonical_contract_version` + `metric_contract_version` + `observation_contract_version` | Version body tables — preserved per Gate 1.2 carve-out set. |
| `contract.canonical_contract_approval` + `metric_contract_approval` + `observation_contract_approval` | Approval rows — preserved per Gate 1.2 carve-out set. |
| `source.*` (provider, system, version, module, object, field) | Source catalog — preserved per Gate 1.2 carve-out set. |
| `metric.metric_definition` + `metric_knowledge` | KPI catalog as operator intent — preserved per Gate 1.2 carve-out set. |
| `metric.metric_binding` | Active runtime artifact for non-archived MCs; surviving binding rows reference surviving CCs. |
| `concept_registry.*` (BCF entity/business_concept/characteristic + versions + supersessions) | **Successor surface**. Untouched throughout the arc. |
| `tenant.*`, `runtime.*` (except `reader.business_object_id`), `evaluation.*`, `metric.*` (except per above), `operations.*` (except per Path C), `compliance.*`, `permissioning.*`, etc. | Untouched. |

## 4. Current FK dependency inventory

Per the Gate 1.3.3 audit script (`bc-core/scripts/d418-gate-1-3-verification.mjs`)
Check #2 (FK-graph sweep), 14 FK constraints touch the 7 quarantined tables.
Classification breakdown:

| Classification | Count | Disposition under Gate 5 |
|---|---|---|
| `covered_by_apply_predicate` | 3 | Source columns dropped (CC.object_id, OFM.business_field_id, Reader.business_object_id). The 4th apply predicate (metric_binding → CC) is transitive and not direct. |
| `internal_to_quarantine` | 9 | Dropped with their parent quarantined tables (CASCADE-irrelevant — all sides being dropped). |
| `historical_fk_sink` | 2 | Path C — migrate snapshot columns + DROP CONSTRAINT before BO drop. |

### The 9 internal-to-quarantine FKs (drop order matters)

These FKs are between quarantined tables. Postgres requires the dependent
table dropped first OR the FK constraint dropped first OR the parent dropped
with CASCADE. Recommendation: explicit drop ordering (dependent → parent) so
the DDL reads as deliberate.

| FK | Source → Target | Drop dependent first |
|---|---|---|
| `cc_field_mapping.business_field_id` → `business_field` | CM → BF | drop CM first |
| `cc_field_mapping.canonical_field_id` → `canonical_field` | CM → CF | drop CM first |
| `cc_field_mapping.canonical_contract_id` → `canonical_contract` | CM → CC (non-quarantined target) | drop CM first |
| `business_object_field.field_id` → `business_field` | BOF → BF | drop BOF first |
| `business_object_field.object_id` → `business_object` | BOF → BO | drop BOF first |
| `business_object_relation.source_object_id` → `business_object` | BOR → BO | drop BOR first |
| `business_object_relation.target_object_id` → `business_object` | BOR → BO | drop BOR first |
| `business_field_alias.field_id` → `business_field` | BFA → BF | drop BFA first |
| `business_field.supersedes_id` → `business_field` (self) | BF self-FK | dropped with BF (self) |

Drop order falls out naturally: **CM, BOF, BOR, BFA, CF, BO, BF** — drop the
"leaf" quarantined tables first, then BO and BF last.

### The 2 historical FK sink FKs (Path C handling)

Per DEC-f48f99 / D419:

| FK | Source rows | Path C action |
|---|---|---|
| `operations.bo_enrichment_log.object_id` → `business_object` | 4,135 | snapshot + drop constraint |
| `operations.bo_verification_log.object_id` → `business_object` | 401 | snapshot + drop constraint |

## 5. Historical FK sink handling — Path A/B/C comparison

DEC-f48f99 §Consequences §"Gate 5" enumerates three feasible paths. Operator
preference and the design recommendation are both **Path C**.

| | Path A | Path B | Path C **(recommended)** |
|---|---|---|---|
| **Action** | DROP CONSTRAINT only | DELETE audit history (CASCADE) | Snapshot BO context into denormalized columns, then DROP CONSTRAINT |
| **Audit data** | Preserved | **Destroyed** | Preserved |
| **Audit queryability post-drop** | UUID is a dangling pointer; can't resolve to a name | n/a (no rows) | Snapshot columns are queryable (object_name, display_name, function_code) |
| **Operator readability of historical incidents** | Bad — "what was object_id 7e3a…?" → no answer | Bad — incidents disappear | Good — incident reports can still name the BO |
| **Storage cost** | +0 | −4,536 rows × audit JSONB | +4,536 rows × ~3 short text fields (~negligible) |
| **Migration cost** | Trivial (1 ALTER per table) | Trivial (1 DELETE per table) | Moderate (1 ALTER + 1 UPDATE per table; the UPDATE is a one-time pass) |
| **Compliance posture** | Weak — audit references that can't be resolved | **Worst** — destroys auditable evidence | Strongest — fully self-contained audit |
| **Reversibility before COMMIT** | High (re-add FK) | None | High (drop snapshot columns) |
| **Reversibility after COMMIT** | Requires BO restore from backup | Requires audit restore from backup | Snapshot columns persist; FK can be re-added if BO is later restored |
| **Foundation Invariant fit** | Weakens **VI** (evidence-is-emitted) | Violates **III** (immutable state of historical audit) + **VI** | Strongest match to **III** + **VI** |

**Path B is rejected** unless the operator explicitly justifies destroying
audit history — which is the inverse of the design intent of the audit logs
themselves.

**Path A leaves dangling UUIDs as the preferred final state** — operator's
Gate 5.0 brief explicitly says don't do that unless Path C proves too costly.
Path C's migration is a single transactional UPDATE over 4,536 rows; in
Postgres on the dev-class hardware this completes in single-digit seconds.
Not "too costly."

**Path C is the recommended disposition** for both `bo_enrichment_log` and
`bo_verification_log`.

### Path C snapshot column schema

Add to each `operations.bo_*_log` table:

| Column | Type | Source (current) | Notes |
|---|---|---|---|
| `object_name_snapshot` | `text` | `business_object.object_name` | Machine-readable BO name |
| `object_display_name_snapshot` | `text` | `business_object.display_name` | Human-readable BO name |
| `object_function_code_snapshot` | `text` | `business_object.function_code` | Functional classification |

After snapshot, the `object_id` column stays as an opaque UUID (no longer FK)
— it remains useful for joining same-BO audit incidents across the two
audit tables before BO data is dropped. The snapshot columns provide the
human-readable resolution.

## 6. Proposed DDL sequence by phase

### Phase definitions

| Phase | Gate | Activity |
|---|---|---|
| **Phase 0** | Gate 5.0 (this) | Design doc — no execution |
| **Phase 1** | Gate 5.1 | Dry-run script emits full DDL + row counts + carve-out hash snapshot; no execution |
| **Phase 2** | Gate 5.2 | Apply gate — DBCP-approved, atomic transaction with rollback story |
| **Phase 3** | Gate 5.3 (post-apply) | Verification + Gate 1.3.3 audit re-run + bootstrap sanity |

### Phase 2 — proposed DDL (single atomic transaction)

The full sequence is one `BEGIN`/`COMMIT` block. Any error rolls the entire
disposition back. The transaction has three logical groups: **Path C snapshot**
(steps 1-4), **dependent column drops on non-quarantined tables** (steps 5-7),
**quarantined table drops** (steps 8-14).

```sql
BEGIN;

-- ─── GROUP 1: Path C snapshot (preserve audit context) ──────────────────────

-- 1. ADD snapshot columns to bo_enrichment_log
ALTER TABLE operations.bo_enrichment_log
  ADD COLUMN object_name_snapshot TEXT,
  ADD COLUMN object_display_name_snapshot TEXT,
  ADD COLUMN object_function_code_snapshot TEXT;

-- 2. UPDATE — copy BO context into bo_enrichment_log rows
--    Expected affected: 4,135 rows
UPDATE operations.bo_enrichment_log el
  SET object_name_snapshot         = bo.object_name,
      object_display_name_snapshot = bo.display_name,
      object_function_code_snapshot = bo.function_code
  FROM contract.business_object bo
  WHERE el.object_id = bo.object_id;

-- 3. ADD snapshot columns to bo_verification_log
ALTER TABLE operations.bo_verification_log
  ADD COLUMN object_name_snapshot TEXT,
  ADD COLUMN object_display_name_snapshot TEXT,
  ADD COLUMN object_function_code_snapshot TEXT;

-- 4. UPDATE — copy BO context into bo_verification_log rows
--    Expected affected: 401 rows
UPDATE operations.bo_verification_log vl
  SET object_name_snapshot         = bo.object_name,
      object_display_name_snapshot = bo.display_name,
      object_function_code_snapshot = bo.function_code
  FROM contract.business_object bo
  WHERE vl.object_id = bo.object_id;

-- IN-TX ASSERTION: snapshot UPDATEs hit the expected row counts
--   (If any UPDATE affected zero rows or fewer than the inventoried count,
--    raise an exception and ROLLBACK. Encoded in the apply script as a
--    DO $$ BEGIN ... IF ... THEN RAISE EXCEPTION ... END IF; END $$ block.)

-- ─── GROUP 2: Drop dependent FK columns on non-quarantined tables ───────────

-- 5. DROP the FK constraints on the historical sink tables (Path C step)
ALTER TABLE operations.bo_enrichment_log
  DROP CONSTRAINT bo_enrichment_log_object_id_fkey;
ALTER TABLE operations.bo_verification_log
  DROP CONSTRAINT bo_verification_log_object_id_fkey;
-- (object_id column STAYS on both audit tables as an opaque historical UUID;
--  the snapshot columns provide the human-readable resolution.)

-- 6. DROP the BF column from observation_field_map (D417 §2 column-level scope)
ALTER TABLE contract.observation_field_map
  DROP COLUMN business_field_id;

-- 7. DROP the FK columns from canonical_contract + reader
--    (Avoid dangling FK-less UUIDs per operator instruction)
ALTER TABLE contract.canonical_contract DROP COLUMN object_id;
ALTER TABLE runtime.reader              DROP COLUMN business_object_id;

-- ─── GROUP 3: Drop quarantined tables (order: leaf → root) ──────────────────

-- 8. Drop CM (depends on BF, CF, CC — CC is non-quarantined; CC.object_id
--    was just dropped in step 7, so CM is the last cross-reference into the
--    BF/CF/BO cluster from CC's side)
DROP TABLE contract.cc_field_mapping;

-- 9. Drop business_object_field (depends on BF + BO)
DROP TABLE contract.business_object_field;

-- 10. Drop business_object_relation (depends on BO)
DROP TABLE contract.business_object_relation;

-- 11. Drop business_field_alias (depends on BF)
DROP TABLE contract.business_field_alias;

-- 12. Drop canonical_field
DROP TABLE contract.canonical_field;

-- 13. Drop business_object (now no FK dependents — Path C in step 5 dropped
--     the audit FKs, step 7 dropped CC + reader FKs, steps 9-10 dropped
--     internal FKs from BOF + BOR)
DROP TABLE contract.business_object;

-- 14. Drop business_field (now no FK dependents — step 6 dropped OFM column,
--     step 8 dropped CM, step 9 dropped BOF, step 11 dropped BFA, and BF's
--     self-FK on supersedes_id is dropped with the table itself)
DROP TABLE contract.business_field;

COMMIT;
```

### Why this order is correct (FK resolution check)

After step 5, `bo_enrichment_log` and `bo_verification_log` no longer reference
`business_object`. After step 6, `observation_field_map.business_field_id`
column no longer exists. After step 7, neither `canonical_contract` nor
`runtime.reader` has any column pointing to `business_object`. After step 8,
`cc_field_mapping` (which referenced all three of BF, CF, CC) is gone.
After step 9, `business_object_field` is gone (severs BOF → BF and BOF → BO).
After step 10, `business_object_relation` is gone (severs the BO self-FK from
BOR's side). After step 11, `business_field_alias` is gone (severs BFA → BF).
After step 12, `canonical_field` is gone. By step 13, `business_object` has
zero remaining FK references and drops cleanly. Same for `business_field`
in step 14.

### Optional Phase 2.1 — Drizzle schema cleanup (deferred)

After the SQL DROP completes, the bc-core Drizzle schema files still declare
the dropped tables + columns. The Drizzle declarations don't enforce DB-side
state; they're TypeScript types. Removing them is a **separate, deferred
gate** (out of Gate 5 scope per §11) so this DBCP focuses purely on the DB
operation.

## 7. Dry-run evidence required for Gate 5.1

Gate 5.1 is a separate gate that executes a dry-run script and produces
evidence artifacts. The script must:

1. **Emit the full DDL** above as `scripts/audit-output/d418-gate-5-1-disposition-{ts}.sql`.

2. **Emit pre-condition row counts** as JSONL evidence:
   - `SELECT COUNT(*) FROM operations.bo_enrichment_log WHERE object_id IS NOT NULL` → expect 4,135
   - `SELECT COUNT(*) FROM operations.bo_verification_log WHERE object_id IS NOT NULL` → expect 401
   - `SELECT COUNT(*) FROM contract.canonical_contract WHERE object_id IS NOT NULL` → expect 0 (active) + 42 (archived)
   - `SELECT COUNT(*) FROM runtime.reader WHERE business_object_id IS NOT NULL` → expect 0 + 0
   - `SELECT COUNT(*) FROM contract.business_object` (reference; before drop)
   - `SELECT COUNT(*) FROM contract.business_field` (reference)
   - Same for each of the other 5 quarantined tables.

3. **Re-run the Gate 1.3.3 audit script** to confirm no regression in the
   pre-condition state (5/5 PASS expected).

4. **Capture carve-out hashes** for the 18 surfaces enumerated in the Gate
   1.2 carve-out list — Gate 5.2 will compare these against post-apply hashes
   to prove the carve-outs were untouched by the disposition.

5. **No DDL execution.** The dry-run is read-only.

6. **Operator review** of the dry-run artifacts before Gate 5.2 opens.

## 8. Apply safety / rollback story for Gate 5.2

Gate 5.2 is the **DBCP apply gate**. The apply script:

1. **Pre-apply backup** — emit JSONL backups of every quarantined table to
   `scripts/audit-output/d418-gate-5-2-backup-{ts}/`:
   - `business_field.jsonl` (all rows)
   - `business_object.jsonl`
   - `business_field_alias.jsonl`
   - `business_object_field.jsonl`
   - `business_object_relation.jsonl`
   - `canonical_field.jsonl`
   - `cc_field_mapping.jsonl`
   - `observation_field_map.business_field_id-projection.jsonl` (just the column being dropped + the row PK)
   - Plus a snapshot of `canonical_contract.object_id` (just the column being dropped + the row PK)
   - Plus a snapshot of `runtime.reader.business_object_id` (same)
   
   These JSONL files **are the rollback story.** Once `COMMIT` lands, no
   in-DB undo is possible; the backups are the only recovery path.

2. **Atomic transaction** — the entire DDL sequence runs inside one `BEGIN`
   / `COMMIT`. Any error (constraint violation, syntax error, in-tx assertion
   failure) triggers `ROLLBACK` and leaves the DB unchanged.

3. **In-transaction assertions** (encoded as `DO $$ ... $$` blocks):
   - After step 2: assert `bo_enrichment_log` rows with non-null
     `object_name_snapshot` = count of rows with non-null `object_id` (Path C
     completeness).
   - Same after step 4 for `bo_verification_log`.
   - Before step 13 (DROP business_object): assert no FK constraint in the
     DB has `business_object` as its target (re-query
     `information_schema.constraint_column_usage`).
   - Before step 14 (DROP business_field): same assertion for
     `business_field`.

4. **DBCP approval** per CLAUDE.md Database Change Protocol — the apply
   script must NOT run until operator explicitly approves the dry-run output
   AND types "apply".

5. **No `--force`, no `--no-verify`, no auto-execution.** The apply script
   reads `--dry-run` by default; `--apply` is an explicit operator flag.

6. **Post-COMMIT rollback** (if the operator discovers an issue post-apply):
   - Restore from the JSONL backups using a separate restore script.
   - The restore is non-atomic with the original DBCP (different transaction);
     the operator accepts that the platform is in a transient broken state
     between detection and restore completion.
   - This rollback path is **expected to be unused** in pre-production but
     must exist for ISO 27001 change-control compliance.

## 9. Verification after apply (Gate 5.3)

A separate Gate 5.3 (post-apply verification) runs:

1. **Gate 1.3.3 audit script re-run** with updated allowlists:
   - The 2 `historical_fk_sink` allowlist entries become moot (the FKs no
     longer exist) — the audit script may either ignore moot entries or flag
     them as candidates for allowlist cleanup (operator decision).
   - Check #1 (apply reconfirmation) becomes vacuously true — the queried
     columns (object_id, business_object_id, etc.) no longer exist.
   - Check #2 (FK-graph sweep) returns 0 FKs into quarantined tables (the
     tables themselves don't exist).
   - Check #3 (static analysis) unchanged — bc-core source code is
     untouched in Gate 5.
   - Check #4 (carve-out idempotency) — same 18 carve-out surfaces; their
     hashes must match the Gate 5.1 dry-run capture.
   - Check #5 (BCF/MCF substrate) — unchanged.

2. **bc-core typecheck** — expected NEW errors because the Drizzle schema
   files still declare the dropped tables. This is the **deferred Gate
   5.2.1** (Drizzle cleanup). The new errors should be exactly the type
   references to the dropped surfaces.

3. **bc-core vitest** — same expectation; tests that reference dropped
   schema types via Drizzle imports will fail to compile.

4. **bc-core `npm run start:dev`** — likely fails to boot until the Drizzle
   schema is cleaned up. If the Drizzle cleanup is deferred (Phase 2.1),
   then Gate 5 leaves bc-core in a "DB clean, code stale" state until Phase
   2.1 ships. **Recommendation**: pair Gate 5.2 (DB drop) with an immediate
   follow-up Gate 5.2.1 (Drizzle cleanup) within the same operator session
   to minimize the inconsistency window.

5. **bc-admin** — unaffected (no schema dependency).

6. **Production-equivalent check** — n/a (pre-production).

## 10. Risks and stop conditions

### Stop conditions (refuse to apply Gate 5.2 if any of these hold)

| # | Condition | Detection |
|---|---|---|
| R1 | DBCP approval not granted by operator | Manual gate |
| R2 | Gate 5.1 dry-run shows any pre-condition mismatch (e.g., active row count > 0 for the apply-predicate FKs) | Dry-run artifact comparison |
| R3 | Any non-archived row in a non-quarantined table references a quarantined surface (post-Gate-1.3.3 regression) | Re-run Gate 1.3.3 audit script — must pass 5/5 |
| R4 | Any new operations.*_log FK to a quarantined surface has been added since DEC-f48f99 | Gate 1.3.3 FK-graph sweep — would surface as `HIDDEN_ACTIVE_REFERENCE` (not on the explicit allowlist) |
| R5 | bc-portal / bc-ai / bc-sdg / any external service reads from a quarantined table | Cross-stack inventory required before Gate 5.2 opens (separate evidence step) |
| R6 | Any new BO-bound row created in any non-quarantined table since Gate 1.2 archival | `SELECT COUNT(*) WHERE archived_at IS NULL AND <bo-bound column> IS NOT NULL` must remain 0 |
| R7 | Any in-flight wizard session in operations or runtime referencing a quarantined surface | n/a (Gates 2.5-A/B and 2.7-A/B removed the wizards; sessions are in-memory and pre-production means none are persistent) |

### Risks during apply (within the transaction)

| # | Risk | Mitigation |
|---|---|---|
| A1 | The Path C UPDATE takes longer than expected | In dev DB, 4,536 row UPDATE is < 1 second; if production tier shows a multi-minute wait, abort and revisit |
| A2 | A new FK to a quarantined table is added between Gate 5.1 dry-run and Gate 5.2 apply | In-transaction assertion before each DROP TABLE catches this; the transaction rolls back |
| A3 | DROP TABLE on a table that turns out to have FK dependents | Same — in-tx assertion before each DROP TABLE checks `information_schema.constraint_column_usage` |
| A4 | Connection drops mid-transaction | Postgres rolls back automatically; the disposition does not partially apply |

### Risks after apply (post-COMMIT)

| # | Risk | Mitigation |
|---|---|---|
| P1 | bc-core Drizzle schema declares dropped tables → compile errors | Pair Gate 5.2 with immediate Gate 5.2.1 (Drizzle cleanup) — see §9.4 |
| P2 | A surviving runtime path tries to query a dropped table | Gate 1.3.3 audit gates this pre-apply; post-apply queries fail with Postgres `relation does not exist` — caught at boot or first request |
| P3 | Audit query that joins `bo_*_log` to `business_object` for human-readable BO names is no longer valid | Path C snapshot columns provide the replacement query — `SELECT object_name_snapshot, ... FROM operations.bo_enrichment_log` |
| P4 | A future need to "un-archive" a BO-bound row arises | The original BO data is in the Gate 5.2 JSONL backup; restoration is possible but requires re-creating the schema first |

## 11. Non-goals

This gate is **physical disposition of D417/D418 quarantined surfaces only**.
It does **not**:

- Migrate any concept from BF/BO/CF/CM to BCF (Entity/BusinessConcept/
  Characteristic) — that is the multi-gate BCF + MCF program, not this DBCP.
- Clean up the bc-core Drizzle schema files for the dropped tables — deferred
  to **Gate 5.2.1** (paired follow-up) per §9.4.
- Write migration files in `bc-core/docker/redesign/migrations/` for replay
  purposes — the disposition is a one-time pre-production event; the
  authoritative DDL is in `bc-core/docker/redesign/02-platform-tables/`
  and that file should be updated separately under its own DBCP.
- Delete any audit_log / activity_log entries that reference quarantined
  entities — `operations.audit_log` uses a polymorphic `varchar` entity_id
  (no FK); rows referencing dropped BOs become stale text but harmless.
- Touch the BCF Registry (`concept_registry.*`) in any way.
- Touch bc-admin, bc-ai, bc-sdg, bc-portal, bc-infra.
- Decide on Path A/B/C selection for future operations.*_log tables that
  may emerge — those are scoped to DEC-f48f99's auto-application criteria
  AND would require Gate 5.0-style design + explicit allowlist entry per
  Gate 1.3.3 discipline.
- Update the Gate 1.3.3 audit script to remove the now-moot
  `historical_fk_sink` allowlist entries — separate cleanup gate after
  Gate 5.3 verification passes.

---

## Open questions for operator review-back

| # | Question |
|---|---|
| Q1 | Confirm Path C selection — proceed as designed, or revisit? |
| Q2 | Confirm the 2 dependent FK column drops on non-quarantined tables (CC.object_id + reader.business_object_id) are also DROP COLUMN (per "no dangling FK-less UUIDs"), not DROP CONSTRAINT only. |
| Q3 | Confirm Gate 5.2.1 (Drizzle cleanup) is paired-immediate with Gate 5.2 (DB drop) to minimize the inconsistency window — or accept the temporary "DB clean, code stale" state? |
| Q4 | Confirm `operations.audit_log` rows referencing dropped BO entity_ids stay as stale-text (polymorphic, no FK; harmless) — or do they also need cleanup? |
| Q5 | Confirm the order of authoritative DDL updates: (a) update `bc-core/docker/redesign/02-platform-tables/` first under a separate DBCP, then Gate 5.2 applies to the live DB; (b) or Gate 5.2 applies first, then the DDL files are updated to match? Recommendation: (a), so the redesign files always reflect the target state. |

## Status and next gate

**Status: proposed.** Awaiting operator review-back before opening Gate 5.1
(dry-run script + evidence emission).

**Gate 5.1 scope (recommended after review-back)**: write `scripts/d418-gate-5-1-dry-run.mjs`
in `bc-core`. The script emits the SQL above as a file + pre-condition row
counts + Gate 1.3.3 audit re-run + carve-out hash snapshot. No DDL execution.
PR pattern same as Gate 1.1 (`scripts(d418): add archival inventory + dry-run audit script`).

**Gate 5.2 scope (operator-gated after Gate 5.1 review)**: write
`scripts/d418-gate-5-2-apply.mjs` with explicit `--dry-run` default and
`--apply` flag. JSONL backups before transaction. Atomic disposition.
In-tx assertions. ROLLBACK on any failure.

**Stop after commit; do not execute SQL** (Gate 5.0 operator instruction).
