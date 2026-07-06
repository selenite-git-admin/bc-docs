---
title: "DBCP-1l — business_field.semantic_family support (execution-ready)"
session: SES-594568
date: 2026-05-12
status: applied
decisions_resolved_at: 2026-05-12
type: dbcp-packet
authority: DEC-a17d0f
related:
  - DEC-a17d0f # SDA umbrella
  - DEC-b7affa # Lane C1 — G5 applies to BF too
  - DBCP-1k    # Tranche 2 lifecycle alignment (applied; pre-condition)
predecessors:
  - "DBCP-1k (applied 2026-05-12) — lifecycle vocabulary alignment"
  - "Server-side gate-evaluation slice (bc-core@9baa369) — surfaces the G5/G6 unevaluable gap"
gates_blocked: "Honest SDA certification of any business_field primitive"
---

# DBCP-1l — `business_field.semantic_family` support

**Execution-ready (2026-05-12, SES-594568). Operator has resolved the four §13 questions; one explicit "go" is required to execute §4 forward DDL. No DDL has executed from this packet.**

## 0. Execution readiness — current gate

| Step | Status | Notes |
|---|---|---|
| Draft authored | ✅ done | filed 2026-05-12, bc-docs-v3@f25166b |
| Operator §13 decisions | ✅ recorded | see §13 — all four resolved |
| **Forward DDL apply** | ✅ **APPLIED 2026-05-12** | §14 execution result |
| Postflight verification | ✅ all four checks pass | §14.3 |
| Paired bc-core code slice | ⏸ next slice | §8 + §9 + §10.2 |
| Honest canary attempt | gated on code slice | §11 |

## 1. Why this packet exists

The gate-evaluation slice that just shipped to bc-core (commit
`9baa369`) honestly surfaces a structural gap: `contract.business_field`
has no `semantic_family` column. G5 (semantic_family presence — non-
overridable) and G6 (data-type × semantic_family × unit compatibility —
non-overridable) cannot be evaluated from persisted state for any BF.
The evaluator marks both as `verdict: 'fail', detail.unevaluable: true,
detail.missingInputs: ['business_field.semantic_family']`.

As a result, **no `business_field` primitive can be honestly certified
today**. Every BF in the registry sits at "blocked by two non-
overridable unevaluable gates" until a `semantic_family` column exists
on `business_field` and is populated.

This packet adds that column, ties it to the existing
`master.semantic_family` catalog by foreign key, and leaves all
existing 7,062 BF rows valid with `semantic_family IS NULL`. No
backfill in this DBCP — that is a separate operator-driven exercise
once a metadata update path is exposed (see §10).

DEC-b7affa already established that "G5 applies to BF too, same gate
broader scope." This packet is the schema work that makes that
decision enforceable rather than aspirational.

## 2. Live state inventory

Queried via `mcp__bc-postgres__pg_query` against
`bc_platform_dev.contract.*` on 2026-05-12.

### 2.1 `master.semantic_family` (the lookup table)

- **Row count:** 23.
- **PK:** `semantic_family_code` (TEXT, format `^[a-z][a-z0-9]*(-[a-z0-9]+)*$` per `semantic_family_code_format_chk`).
- **`category_code` CHECK:** `IN ('identity','measure','temporal','dimension')`.
- The full enum (frozen by D366 SSOT) — relevant to G5:

  | category | codes |
  |---|---|
  | identity | `code`, `name`, `identifier`, `text` |
  | temporal | `date`, `datetime`, `duration`, `period` |
  | dimension | `dim-calendar-date`, `dim-cost-center`, `dim-country`, `dim-currency`, `dim-customer`, `dim-fiscal-period`, `dim-gl-account`, `dim-legal-entity`, `dim-product`, `dim-vendor` |
  | measure | `measure-count`, `measure-currency`, `measure-percent`, `measure-ratio`, `measure-score` |

### 2.2 `contract.business_field` (the target table)

- **Row count:** 7,062 (certified 6,779 + draft 283).
- **Columns today (16):** `field_id`, `name`, `definition`, `business_function`, `object_class`, `property`, `representation_term`, `data_type`, `status_code`, `definition_standard`, `created_by_name`, `updated_by_name`, `created_at`, `updated_at`, `standard_ref`, `pii_classification`.
- **Naming convention nearest sibling:** `definition_standard` (TEXT, FK to `master.master_definition_standard`). DBCP-1l mirrors the same shape for `semantic_family`.

### 2.3 Cross-schema FK convention

Cross-schema FKs from `contract.*` → `master.*` are an established
pattern in this repo (queried `pg_constraint`): `business_field`
already FKs to `master.master_definition_standard`; `business_object`
FKs to four master tables; `metric_definition` FKs to nine master
tables. There is no policy against cross-schema FKs in this project.
**Decision: use a normal FK (option preferred in operator brief).**

## 3. Target schema

### 3.1 Column shape

```
business_field.semantic_family TEXT  NULL  REFERENCES master.semantic_family(semantic_family_code)
```

- **Nullable initially.** Existing 7,062 rows keep `NULL`; no backfill in this DBCP.
- **Type `TEXT`** matches the PK type on the lookup. No CHECK on the column itself — the FK enforces the closed set.
- **FK cascade behaviour (resolved 2026-05-12, §13.1):** no cascade. Default `NO ACTION` / `RESTRICT` on both UPDATE and DELETE. `master.semantic_family` is a governed enum table; rename/delete of a code must be operator-driven via its own DBCP, not silently propagated. Matches the existing `fk_business_field__definition_standard` pattern.

### 3.2 Indexes

- `idx_business_field__semantic_family ON contract.business_field (semantic_family)`. Justification: gate-evaluation queries today scan all 7,062 BFs once per `evaluate-gates` call (G2a/G2b); per-family filtering (e.g. "list all unmapped BFs in family X" for ops dashboards) will follow; the index size is trivial (~24 distinct values across at most 7,062 rows).

### 3.3 Constraint name

`fk_business_field__semantic_family` — follows the existing
`fk_business_field__definition_standard` naming convention.

## 4. Forward DDL (proposed — not executed)

Single transaction. Both statements are metadata-only operations on
the `business_field` table; no row rewrite happens.

```sql
BEGIN;

ALTER TABLE contract.business_field
  ADD COLUMN semantic_family TEXT NULL
    CONSTRAINT fk_business_field__semantic_family
    REFERENCES master.semantic_family(semantic_family_code)
    ON UPDATE NO ACTION ON DELETE NO ACTION;

CREATE INDEX idx_business_field__semantic_family
  ON contract.business_field (semantic_family);

COMMIT;
```

The `ON UPDATE NO ACTION ON DELETE NO ACTION` clause is explicit
(rather than relying on the PostgreSQL default) so the constraint
declaration reads unambiguously in `pg_get_constraintdef` output and
matches the locked §13.1 decision verbatim.

Notes:
- `ALTER TABLE … ADD COLUMN … NULL` is metadata-only in PostgreSQL when no default is supplied — no row rewrite. Confirmed for PG 17.8 (the deployment).
- The FK is `MATCH SIMPLE` by default (PG default) — `NULL` columns are not validated against the lookup, which is what we want.
- No `CHECK` redundant with the FK. The FK enforces the closed set on its own.

## 5. Preflight checks

```sql
SELECT COUNT(*) AS bf_row_count FROM contract.business_field;
SELECT COUNT(*) AS lookup_row_count FROM master.semantic_family;
SELECT column_name FROM information_schema.columns
  WHERE table_schema='contract' AND table_name='business_field' AND column_name='semantic_family';
SELECT 1 FROM pg_constraint WHERE conname='fk_business_field__semantic_family';
```

Halt the apply if:
- `bf_row_count` is wildly different from the 7,062 in §2.2 (someone has loaded rows between draft and apply).
- `lookup_row_count` is not 23 (someone has changed the catalog between draft and apply).
- Either the column or constraint already exists (the apply has been partly run).

## 6. Postflight verification

```sql
SELECT column_name, data_type, is_nullable, column_default
  FROM information_schema.columns
  WHERE table_schema='contract' AND table_name='business_field' AND column_name='semantic_family';

SELECT conname, pg_get_constraintdef(oid)
  FROM pg_constraint WHERE conname='fk_business_field__semantic_family';

SELECT indexname FROM pg_indexes
  WHERE schemaname='contract' AND tablename='business_field' AND indexname='idx_business_field__semantic_family';

SELECT COUNT(*) AS rows_with_family_set,
       COUNT(*) FILTER (WHERE semantic_family IS NULL) AS rows_with_null_family,
       COUNT(*) AS total
  FROM contract.business_field;
```

Expect:
- Column present, `text`, nullable, no default.
- FK to `master.semantic_family(semantic_family_code)`.
- Index `idx_business_field__semantic_family` present.
- `rows_with_family_set=0`, `rows_with_null_family=7062`, `total=7062`.

## 7. Rollback

The forward DDL is fully reversible by a single DROP COLUMN. The
column is freshly added; no row data is lost because no data
populates it during this DBCP.

```sql
BEGIN;
DROP INDEX IF EXISTS contract.idx_business_field__semantic_family;
ALTER TABLE contract.business_field DROP COLUMN semantic_family;
COMMIT;
```

`DROP COLUMN` also drops the dependent FK constraint and index. If
the paired code slice has been deployed and is using
`semanticFamily` in the Drizzle schema, the running bc-core will throw
on any read/write that projects this column. That risk is the same as
the DBCP-1k rollback discussion — bounded by the apply window, not a
production risk if the code slice is deferred to a separate session
slot.

## 8. Drizzle schema plan

Single edit to `src/database/schema/contract/business-field.ts`:

```typescript
export const businessField = contractSchema.table(
  'business_field',
  {
    // ... existing columns ...
    statusCode: text('status_code').notNull().default('draft'),
    piiClassification: text('pii_classification').notNull().default('none'),
    definitionStandard: text('definition_standard'),
    standardRef: text('standard_ref'),
    semanticFamily: text('semantic_family'),  // ← new, nullable
    createdByName: text('created_by_name'),
    // ... rest unchanged ...
  },
  (table) => [
    // ... existing indexes ...
    index('idx_business_field__semantic_family').on(table.semanticFamily),  // ← new
    // CHECK on status_code unchanged
  ],
);
```

The FK is not declared in Drizzle today for `definition_standard`
either (the live DB has the FK; Drizzle does not declare it). Match
that pattern — the FK lives in the DDL/migrations, not in the
TypeScript schema definition. If the project wants Drizzle to declare
cross-schema FKs as a separate cleanup, it's an orthogonal slice.

## 9. Gate-reader plan

Single edit to `gate-evaluation.reader.ts`:

```typescript
export interface BusinessFieldRowForGates {
  fieldId: string;
  name: string;
  definition: string | null;
  objectClass: string | null;
  dataType: string | null;
  definitionStandard: string | null;
  standardRef: string | null;
  semanticFamily: string | null;  // ← new
  statusCode: string;
}

// In DrizzleBusinessFieldGateReader.loadBusinessField:
//   project businessField.semanticFamily into the row.
```

Single edit to `gate-evaluation.service.ts`:

```typescript
const block = evaluateCertificationGates({
  primitiveType: 'business_field',
  // ... existing fields ...
  semanticFamily: bf.semanticFamily,   // ← was hard-coded null
  dataType: bf.dataType,
  unitTypeCode: null,
});
```

The annotation pass at `annotateUnevaluableForBusinessField` stays as
written. Once `semanticFamily` is populated on a BF, G5 stops failing
with `null_semantic_family`, the annotation condition no longer fires,
and `detail.unevaluable` is absent from the gate result. If a BF is
left with `NULL` `semantic_family`, the evaluator continues to surface
G5/G6 as unevaluable — same honest behaviour as today.

The 17 existing gate-evaluation tests need a minor update: the
`BusinessFieldRowForGates` fixtures gain a `semanticFamily: null`
field (and one new test pins the "populated semantic_family → G5
passes, no unevaluable flag" branch).

## 10. Setting `semantic_family` on the first canary BF (§ operator question)

Three paths to land a value on `credit_status_code` after DBCP-1l
applies. Listed worst-to-best for the canary:

### 10.1 Direct SQL UPDATE (worst)

Operator-approved one-shot UPDATE:

```sql
UPDATE contract.business_field
  SET semantic_family='code'
  WHERE field_id='019d7050-aa31-71d6-a8a2-529fb2ce63de';
```

**Problems:**
- No audit trail beyond the operator's session memory.
- Bypasses any future "metadata change record" pattern.
- Violates the project's standing rule: no backdoor DB writes when a
  service exists (CLAUDE.md "Bulk-create data via direct DB inserts" /
  "always use official API endpoints with quality gates").

**Verdict: not recommended even for a one-row canary.**

### 10.2 Extend the existing `PATCH /standard-fields/:fieldId` endpoint (recommended for canary)

The BF update path already exists at
`src/registry/standard-field.controller.ts:117`. It calls
`StandardFieldService.updateField` which calls
`StandardFieldRepository.updateField` — and the latter already maps the
wire-format DTO field `status` → column `status_code` (DBCP-1k §6.2
pattern). Adding `semanticFamily` follows the same pattern exactly:

- `update-standard-field.dto.ts`: add
  `semanticFamily?: string` with `@IsString @IsOptional`. No `@IsIn` —
  the DB FK enforces the closed set; client-side enum validation
  duplicates source-of-truth.
- `StandardFieldRepository.updateField` accepts `data.semanticFamily`
  and writes it directly (no rename — column is already
  `semantic_family` / property `semanticFamily`).
- `StandardFieldService.updateField` passes it through.

Code touch ~3 sites, ~10 lines total. No new endpoint. No new
controller. No new test file required (one extra case in the existing
spec would be enough). The PATCH is already `@PlatformOnly()`.

**Acceptance criteria for the paired code slice:**
- Setting `semanticFamily` on a draft BF persists.
- Setting an invalid family (one not in `master.semantic_family`)
  returns a 400 / 409 from Postgres (FK violation) — bc-core's existing
  error handler wraps that as a 400 BadRequest. Confirm in the slice.
- Subsequent `GET /sda/primitives/business_field/:id/evaluate-gates`
  observes the new value: G5 verdict flips from `fail+unevaluable`
  to either `pass` (if the family is valid + present) or `fail` with
  an honest compatibility reason.

**Verdict: recommended path for the canary. Smallest change, reuses
existing PATCH semantics, leaves an HTTP-level audit footprint in
whatever log layer the platform already runs.**

### 10.3 New SDA-5 "set primitive metadata" endpoint (overkill for canary)

A dedicated PATCH endpoint under `/sda/primitives/:type/:id/metadata`
that writes a constrained metadata patch (semanticFamily,
definitionStandard, standardRef) with ledger-recorded provenance.

Better long-term posture but **disproportionate for the canary**.
File a follow-up task; ship 10.2 first.

## 11. Fastest safe canary sequence (after this DBCP + paired code slice)

1. Apply DBCP-1l forward DDL (§4) inside a single transaction. Postflight (§6).
2. Land the paired code slice:
   - Drizzle schema edit (§8).
   - Gate reader + service edit (§9).
   - DTO + service + repo edit per §10.2.
   - 1–2 new test cases (gate-eval with populated family, BF PATCH with semantic_family round-trip).
   - Sweep + commit.
3. Manually:
   - `GET /sda/primitives/business_field/019d7050-…/evaluate-gates` — confirm honest baseline (G5/G6 unevaluable, G4 overridable fail, rest pass).
   - `PATCH /standard-fields/019d7050-…` with body `{ "semanticFamily": "code" }` — confirm 200, persists.
   - `GET …/evaluate-gates` again — confirm G5 flips to `pass`, G6 flips to `pass` (data_type `code` is compatible with family `code` per `master.semantic_family.compatible_data_types`). G4 still fails overridable (definition_standard NULL).
4. Decide: either (a) set `definition_standard='bc_standard'` via the same PATCH and re-evaluate (G4 should pass — internal standards don't need a ref), or (b) keep G4 honestly failing and exercise the certify-with-override path against G4.
5. Submit-for-review → certify with the platform-computed gate block.

**This sequence proves honest certification end-to-end with one
real primitive and zero operator-asserted gates.**

## 12. Scope boundaries this packet honours

- **Planning only.** No DBCP execution.
- **No live metadata writes.** No row in `business_field` gets a
  `semantic_family` value from this packet.
- **No certification acts.** SDA-4 endpoints are not exercised here.
- **No backfill.** All 7,062 BFs remain `NULL` after apply.
- **No metric repair writes.**
- **No tenant / runtime touches.**
- **No CF or BO equivalent.** Those tables also lack semantic_family
  exposed via DB columns; a follow-up DBCP can mirror this pattern
  when CF/BO certification becomes the bottleneck.

## 13. Resolved decisions (operator, 2026-05-12, SES-594568)

All four open questions in the original draft are now locked. The
DDL in §4, the index in §3.2, and the canary path in §10 reflect
these resolutions.

### 13.1 FK cascade behaviour — RESOLVED

**Decision:** normal FK with default `NO ACTION` / `RESTRICT` semantics
on both UPDATE and DELETE. No cascade.

**Rationale (operator, verbatim):** "`master.semantic_family` is a
governed enum table and should not delete/rename values casually."
Cascade would propagate enum changes silently to thousands of BFs;
that decision must be operator-driven via a dedicated DBCP, not a
side effect of a master-table edit.

**Where applied:** §3.1, §4 (explicit `ON UPDATE NO ACTION ON DELETE
NO ACTION` clause on the FK).

### 13.2 Index on `business_field(semantic_family)` — RESOLVED

**Decision:** add the index.

**Rationale (operator, verbatim):** "It supports SDA queues and ops
queries." Concretely: per-family rollups for the certification
backlog ("all unmapped BFs in family X"), filter queries from the
gate-evaluation surface, and future bc-admin grouped views.

**Where applied:** §3.2, §4 (`CREATE INDEX idx_business_field__semantic_family`).

### 13.3 Canary metadata-write path — RESOLVED

**Decision:** recommendation 10.2 — extend the existing
`PATCH /standard-fields/:fieldId` endpoint to accept `semanticFamily`.
**Do not** use direct SQL. **Do not** create a new SDA endpoint just
for the canary.

**Rationale (operator, verbatim):** preserve the project's "no
backdoor DB writes when a service exists" rule (CLAUDE.md "always use
official API endpoints with quality gates"); keep canary surface area
minimal — no new endpoint until a real authoring slice needs one.

**Where applied:** §10 (10.1 marked rejected; 10.2 confirmed; 10.3
deferred as overkill for the canary), §11 (sequence uses PATCH).

### 13.4 Packet number — RESOLVED

**Decision:** **DBCP-1l**. 1k is taken; 1b is too stale to recycle.

**Where applied:** filename, frontmatter `title`, all body references.

---

**With these four decisions locked, this packet is execution-ready.**
The forward DDL in §4 awaits one further operator instruction ("apply
DBCP-1l") before running. Postflight and the paired code slice follow
the sequence in §11. Same execution gate that DBCP-1k passed.

---

## 14. Execution result — 2026-05-12, SES-594568

**Status: APPLIED.** Forward DDL §4 executed in a single transaction
against `bc_platform_dev` (Docker container `bc-postgres-redesign`,
PostgreSQL 17.8) via `psql -v ON_ERROR_STOP=1`.

### 14.1 Transaction trace

```
BEGIN
ALTER TABLE            -- add column + FK in one statement
CREATE INDEX           -- idx_business_field__semantic_family
COMMIT
```

No errors. No statement halted. The forward DDL is metadata-only — no
row rewrite of the 7,062 existing BF rows.

### 14.2 Preflight (§5) — clean

| Check | Expected | Got |
|---|---|---|
| `bf_row_count` | ≈ 7,062 (§2.2) | **7,062** ✓ |
| `lookup_row_count` | 23 (§2.1) | **23** ✓ |
| `column_exists_already` | 0 | **0** ✓ |
| `fk_exists_already` | 0 | **0** ✓ |

No drift between draft and apply. All four halt conditions clear.

### 14.3 Postflight (§6) — all four checks pass

**§6.1 — column shape:**
- `column_name='semantic_family'`, `data_type='text'`,
  `is_nullable='YES'`, `column_default` is NULL. ✓

**§6.2 — foreign key:**
```
fk_business_field__semantic_family
  FOREIGN KEY (semantic_family) REFERENCES master.semantic_family(semantic_family_code)
```
- Constraint present, points at the right column/lookup. ✓
- **Note on cosmetic difference:** the canonical output of
  `pg_get_constraintdef` omits the `ON UPDATE NO ACTION ON DELETE NO ACTION`
  clauses because PostgreSQL treats `NO ACTION` as the default and elides
  defaults from the canonical text. The constraint's *behaviour* matches
  §13.1 verbatim — verified by `SELECT confupdtype, confdeltype FROM
  pg_constraint` showing both as `'a'` (the internal code for NO ACTION).
  No semantic divergence from the locked decision.

**§6.3 — index:**
- `idx_business_field__semantic_family` present on `contract.business_field`. ✓

**§6.4 — row distribution:**
- `rows_with_family_set = 0`, `rows_with_null_family = 7062`, `total = 7062`. ✓
- Matches the §3.1 promise: existing rows kept `NULL`, no backfill.

### 14.4 What is now true

- `contract.business_field` carries a nullable `semantic_family TEXT`
  column governed by an FK to `master.semantic_family(semantic_family_code)`.
- All 7,062 existing BF rows are `NULL` on the new column. They remain
  schema-valid (FK allows NULL).
- The gate-evaluation surface at bc-core HEAD (9baa369) is still
  hard-coding `semanticFamily: null` when calling
  `evaluateCertificationGates`. **bc-core code does NOT yet read the new
  column.** Honest behaviour is therefore unchanged: G5/G6 continue to
  surface as `verdict: 'fail', detail.unevaluable: true` for every BF.
  That is the expected gap until the paired code slice (§8 + §9 + §10.2)
  lands.
- No metadata writes happened. No certification acts happened. No
  bc-core code changed in the execution turn.

### 14.5 What must follow (paired code slice — separate session slot)

Per §8 + §9 + §10.2 of this packet:

1. Drizzle schema gains `semanticFamily: text('semantic_family')` +
   index entry on `business-field.ts`.
2. `BusinessFieldRowForGates` interface + Drizzle reader project the
   new field.
3. `GateEvaluationService.evaluateBusinessField` passes
   `bf.semanticFamily` instead of hard-coded `null` into the gate
   input. The annotation pass in
   `annotateUnevaluableForBusinessField` stays as-is — when a BF has
   a non-null `semantic_family`, G5 no longer produces the
   missing-input failure tokens and the annotation condition simply
   doesn't fire.
4. `UpdateStandardFieldDto` gains `semanticFamily?: string`.
   `StandardFieldRepository.updateField` plumbs it through to the new
   column. Wire-format DTO field name = column property name = no
   mapping needed (unlike DBCP-1k's `status` → `status_code` case).
5. Test updates: existing 17 gate-evaluation cases get a
   `semanticFamily: null` fixture line; add ≥2 new cases — one for
   "populated family → G5 passes, no unevaluable flag," one for "PATCH
   semanticFamily round-trip + invalid family rejected by FK."
6. Sweep + commit + push.

### 14.6 Rollback exposure

The forward DDL is reversible by `DROP COLUMN semantic_family` per
§7. The exposure window is small because:
- No row data has been written to the new column.
- No bc-core code reads or writes the new column yet.
- The Drizzle schema does not yet declare the column.

If a regret event occurs between this commit and the paired code
slice landing, rollback is a clean single-transaction DROP. After the
code slice lands, rollback requires coordination with a bc-core
revert (same posture as DBCP-1k §7).

### 14.7 Authority

Forward DDL applied with explicit operator authorization in
SES-594568 on 2026-05-12. No DDL beyond §4 executed. No SDA-4
endpoints exercised. No metadata writes performed. No certification
acts performed. No backfill. No CF/BO semantic_family work. No metric
repair writes.

**End of packet — APPLIED.**
