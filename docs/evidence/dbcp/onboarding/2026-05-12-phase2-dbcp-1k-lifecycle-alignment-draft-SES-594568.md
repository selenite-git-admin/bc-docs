---
title: "DBCP-1k — SDA primitive lifecycle alignment (Tranche 2 draft)"
session: SES-594568
date: 2026-05-12
status: applied
type: dbcp-packet
authority: DEC-a17d0f
related:
  - DEC-a17d0f # SDA umbrella
  - DEC-b7affa # Lane C1 — semantic compatibility / G11
  - DBCP-1c    # Tranche 1: certification_record table (live)
predecessors:
  - "DBCP-1a (executed) — certification_record"
  - "DBCP-1c (executed) — certification gates ledger"
  - "DBCP-1f (executed) — primitive_provenance"
  - "DBCP-1j (executed) — supersession columns on primitives"
  - "DBCP-2a (executed) — mc_envelope_audit_record"
gates_blocked: SDA-4
---

# DBCP-1k — SDA primitive lifecycle alignment (Tranche 2 draft)

**This is a draft. No DDL executes from this packet. Operator approval required before any forward step.**

## 1. Why this packet exists

SDA-4 (state-transition endpoints) cannot be implemented against the current
primitive schema. The DEC-a17d0f lifecycle vocabulary is six states:

```
draft → proposed → reviewing → certified → deprecated
                                    ↑
                              (proposed/reviewing → withdrawn)
```

The live primitive tables hold a strict subset of those values and use
inconsistent vocabulary. Any write of `proposed`, `reviewing`, or `withdrawn`
to `canonical_field` or `business_object` is rejected at COMMIT by the CHECK
constraint. `business_object` uses `approved` where DEC-a17d0f says
`certified`. `business_field` carries the column under the legacy name
`status` rather than `status_code`, and the live CHECK is undeclared in the
Drizzle schema.

This packet aligns all three primitive tables to a single vocabulary so that
SDA-4 can ship as a single coherent slice rather than a dual-write workaround.

## 2. Live state inventory

Queried via `mcp__bc-postgres__pg_query` against
`bc_platform_dev.contract.*` on 2026-05-12.

### 2.1 Status distribution

| Table | Column | Value | Rows |
|---|---|---|---|
| `contract.canonical_field` | `status_code` | `draft` | 3,097 |
| `contract.business_object` | `status_code` | `approved` | 194 |
| `contract.business_object` | `status_code` | `deprecated` | 8 |
| `contract.business_field` | `status` | `certified` | 6,779 |
| `contract.business_field` | `status` | `draft` | 283 |

Total touched rows: **10,361.**

### 2.2 Live CHECK constraints

| Table | Constraint | Definition |
|---|---|---|
| `contract.canonical_field` | `ck_canonical_field__status` | `status_code IN ('draft','certified','deprecated')` |
| `contract.business_object` | `business_object_status_code_check` | `status_code IN ('draft','approved','deprecated')` |
| `contract.business_field` | `ck_business_field__status` | `status IN ('draft','certified')` |

The constraint name on `business_object` follows a different convention
(`business_object_status_code_check`) than the other two (`ck_*__status`).
The packet fixes this in the rename step.

### 2.3 Drizzle / live drift (pre-existing)

`src/database/schema/contract/business-field.ts` declares no CHECK on the
`status` column, but `ck_business_field__status` is live. The packet
re-declares the CHECK on the new column in the Drizzle schema as part of the
alignment.

## 3. Code-reference inventory

Inventory taken via `Grep` against `bc-core/src` on 2026-05-12.

### 3.1 `business_object` `approved` literal — ~10 sites across 6 files

| File | Lines | Nature |
|---|---|---|
| `src/registry/business-object.service.ts` | 22–25 | `VALID_TRANSITIONS` map (state machine) |
| `src/registry/business-object.service.ts` | 618 | `bo.statusCode === 'approved'` guard |
| `src/registry/business-object.service.ts` | 637 | `repo.update(..., { statusCode: 'approved' })` |
| `src/registry/business-object.service.ts` | 644 | audit log `afterJson` payload |
| `src/registry/business-object.service.ts` | 765 | `repo.list({ statusCode: 'approved', ... })` |
| `src/registry/business-object.controller.ts` | 51 | Swagger `@ApiQuery` enum |
| `src/registry/dto/create-business-object.dto.ts` | 164, 167 | `@ApiPropertyOptional` + `@IsIn` validator |
| `src/registry/oc-onboarding.service.ts` | 128–130 | gate check + operator-facing error message |
| `src/database/schema/contract/business-object.ts` | 57 | Drizzle CHECK declaration |
| `src/registry/semantic-definitions/profiles.ts` | 77 | maps `approved → certified` (already correct — **no change needed**) |

`BusinessObjectService.VALID_TRANSITIONS` is a service-internal state machine
that needs to coexist with or be replaced by the SDA-4 transition service.
Decision deferred to §6.

### 3.2 `business_field` `status` column — 8 sites across 5 files

| File | Lines | Nature |
|---|---|---|
| `src/database/schema/contract/business-field.ts` | 29 | column declaration |
| `src/registry/business-object.repository.ts` | 165 | SELECT projection `status: businessField.status` |
| `src/registry/semantic-definitions/semantic-definitions-projection.repository.ts` | 133 | WHERE clause `eq(businessField.status, params.status)` |
| `src/registry/standard-field.repository.ts` | 41, 71, 86, 89, 135, 163 | 6 sites: WHERE filters, projections, literal writes |
| `src/registry/standard-field.service.ts` | 293, 343, 453, 604 | literal `'draft' / 'certified'` writes |
| `src/registry/dto/update-standard-field.dto.ts` | 60 | DTO field `status?: string` (wire-format; see §6) |

### 3.3 `canonical_field` status — 4 sites across 3 files

| File | Lines | Nature |
|---|---|---|
| `src/database/schema/contract/canonical-field.ts` | 52 | Drizzle CHECK declaration |
| `src/registry/canonical-field.repository.ts` | 116 | WHERE filter `eq(canonicalField.statusCode, params.status)` |
| `src/registry/canonical-field.controller.ts` | 58 | Swagger `@ApiQuery` enum |
| `src/registry/semantic-definitions/semantic-definitions-projection.repository.ts` | 110, 205 | filter + projection |

No state-machine code exists on CF today — all 3,097 rows sit in `draft`.
This is the lowest-risk of the three primitives.

### 3.4 What is NOT touched

- `master.standard_field` is a different table; the `standardField` symbol
  imported in `standard-field.repository.ts` resolves through the contract
  barrel as an alias to `businessField` (not the master table). Verified.
- `contract.certification_record.from_state_code` / `to_state_code` columns
  have **no** CHECK constraint — they already accept the full DEC-a17d0f
  vocabulary. No change required there.
- `MCEAuditRecordRepository` and `ProvenanceRecordRepository` do not reference
  primitive status — out of scope.

## 4. Target schema (proposed)

### 4.1 Unified column + vocabulary

All three primitive tables expose a column named `status_code` with the
identical CHECK:

```sql
status_code IN (
  'draft',
  'proposed',
  'reviewing',
  'certified',
  'deprecated',
  'withdrawn'
)
```

`draft` is the default. `draft` remains valid permanently (compatibility for
in-flight authoring; SDA-4 is the only path that transitions out of `draft`).

### 4.2 Per-table changes

| Table | Change |
|---|---|
| `canonical_field` | Replace CHECK only. Column already named `status_code`. No data migration. |
| `business_object` | Replace CHECK. **Data migration**: `UPDATE … SET status_code='certified' WHERE status_code='approved'` (194 rows). Rename constraint to `ck_business_object__status` for naming consistency. |
| `business_field` | **Column rename**: `ALTER TABLE … RENAME COLUMN status TO status_code`. Replace CHECK. No row data change (all values `draft` / `certified` are valid under the new vocabulary). |

### 4.3 Drizzle schema follow-ups (in the same release)

- `contract/canonical-field.ts`: update CHECK SQL string.
- `contract/business-object.ts`: update CHECK SQL string + constraint name.
- `contract/business-field.ts`: rename column property `status` → `statusCode`, declare CHECK explicitly.
- Adjust six WHERE / projection sites listed in §3.2.

### 4.4 Code-side renames (in the same release)

- `BusinessObjectService.VALID_TRANSITIONS`: see §6.
- All `'approved'` literals in §3.1 become `'certified'` (or are removed if part of the legacy state machine).
- Swagger `@ApiQuery` and `@IsIn` enums updated to the six-value set.

## 5. Forward DDL (proposed — not executed)

Each step is one statement, in order. Wrapped in a single transaction at
execution time per the standard DBCP pattern.

```sql
BEGIN;

-- 5.1 canonical_field — CHECK expansion only
ALTER TABLE contract.canonical_field DROP CONSTRAINT ck_canonical_field__status;
ALTER TABLE contract.canonical_field ADD CONSTRAINT ck_canonical_field__status
  CHECK (status_code IN ('draft','proposed','reviewing','certified','deprecated','withdrawn'));

-- 5.2 business_object — data migration + CHECK swap + rename for naming consistency
ALTER TABLE contract.business_object DROP CONSTRAINT business_object_status_code_check;
UPDATE contract.business_object SET status_code='certified' WHERE status_code='approved';
ALTER TABLE contract.business_object ADD CONSTRAINT ck_business_object__status
  CHECK (status_code IN ('draft','proposed','reviewing','certified','deprecated','withdrawn'));

-- 5.3 business_field — column rename + CHECK swap
ALTER TABLE contract.business_field DROP CONSTRAINT ck_business_field__status;
ALTER TABLE contract.business_field RENAME COLUMN status TO status_code;
ALTER TABLE contract.business_field ADD CONSTRAINT ck_business_field__status
  CHECK (status_code IN ('draft','proposed','reviewing','certified','deprecated','withdrawn'));

COMMIT;
```

Note: ALTER … RENAME COLUMN is a metadata-only operation in PostgreSQL —
no row rewrite, no table lock beyond AccessExclusive for the rename itself.
The 6,779 certified BF rows and the 194 BO rows are touched only by the
UPDATE on BO (single statement, ~milliseconds at this row count).

## 6. Open design decisions (need operator answer before forward DDL)

### 6.1 BO `VALID_TRANSITIONS` state machine — **RESOLVED 2026-05-12**

`BusinessObjectService` ships a 3-state machine (`draft → approved →
deprecated`) at lines 22–25. SDA-4 ships a 6-state machine via the
state-transition service.

**Operator decision (2026-05-12, SES-594568):** retire
`BusinessObjectService.VALID_TRANSITIONS` for SDA-governed primitive
lifecycle. Route all BO lifecycle transitions through SDA-4 once SDA-4
exists. **Until SDA-4 exists, do not add new BO lifecycle behavior in
`BusinessObjectService`.** The existing line-637
`repo.update(..., { statusCode: 'approved' })` site is preserved unchanged
during the Tranche 2 code slice (it continues to write the certified-
equivalent value, now spelled `'certified'` post-rename) and is replaced
with a call to the SDA-4 transition service when that slice ships.

### 6.2 `update-standard-field.dto.ts` wire-format — **RESOLVED 2026-05-12**

The DTO field is named `status` on the API surface. The column rename is
internal — we can preserve API stability by keeping the DTO field name
`status` and mapping to the renamed column inside the service.

**Operator decision (2026-05-12, SES-594568):** keep the external API
wire field as `status` for backward compatibility. Internally map it to
`status_code` after the schema alignment. **Do not break the API just
to rename the database column.** The code slice paired with this DBCP
keeps `update-standard-field.dto.ts` line 60 (`status?: string`) intact
and adds the mapping `dto.status → column.status_code` inside the
service / repository layer.

### 6.3 Drizzle BF CHECK re-declaration

The packet adds the CHECK explicitly to the Drizzle schema to close the
pre-existing drift (live has CHECK, schema declares none). This is included
in the same code slice.

**Action required:** none — included.

### 6.4 No supersede / archive / unarchive in this packet — **CONFIRMED 2026-05-12**

DEC-a17d0f's full lifecycle includes `supersede` and `archive` / `unarchive`
acts. Those are deferred to a separate DBCP slice (call it 1l) because
`supersede` requires the survivor-link column work that DBCP-1j already
landed on the primitive tables, plus a separate `archived_at` column not yet
in scope.

**Operator confirmation (2026-05-12, SES-594568):** Tranche 2 SDA-4 ships
exactly **five** endpoints, no more, no less:

- `submit-for-review`
- `certify`
- `return-to-author`
- `withdraw`
- `deprecate`

`supersede` / `archive` / `unarchive` remain deferred to a future DBCP +
code slice.

## 7. Preflight checks (executed at apply time)

```sql
-- 7.1 Confirm row counts haven't shifted since packet draft
SELECT 'canonical_field' AS t, status_code, COUNT(*) FROM contract.canonical_field GROUP BY status_code
UNION ALL
SELECT 'business_object', status_code, COUNT(*) FROM contract.business_object GROUP BY status_code
UNION ALL
SELECT 'business_field', status, COUNT(*) FROM contract.business_field GROUP BY status;

-- 7.2 Confirm no unexpected status values exist (would block the new CHECK)
SELECT status_code, COUNT(*) FROM contract.canonical_field
  WHERE status_code NOT IN ('draft','proposed','reviewing','certified','deprecated','withdrawn')
  GROUP BY status_code;
SELECT status_code, COUNT(*) FROM contract.business_object
  WHERE status_code NOT IN ('draft','proposed','reviewing','certified','deprecated','withdrawn','approved')
  GROUP BY status_code;
SELECT status, COUNT(*) FROM contract.business_field
  WHERE status NOT IN ('draft','proposed','reviewing','certified','deprecated','withdrawn')
  GROUP BY status;
```

Halt + report if any of 7.2 returns rows.

## 8. Postflight verification

```sql
-- 8.1 New CHECK definitions present
SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
  WHERE conname IN ('ck_canonical_field__status','ck_business_object__status','ck_business_field__status');

-- 8.2 Row distribution after migration
SELECT 'canonical_field' AS t, status_code, COUNT(*) FROM contract.canonical_field GROUP BY status_code
UNION ALL
SELECT 'business_object', status_code, COUNT(*) FROM contract.business_object GROUP BY status_code
UNION ALL
SELECT 'business_field', status_code, COUNT(*) FROM contract.business_field GROUP BY status_code;

-- 8.3 Confirm 'approved' has been fully migrated on BO
SELECT COUNT(*) FROM contract.business_object WHERE status_code='approved';
-- expect 0

-- 8.4 Confirm old column 'status' no longer exists on business_field
SELECT column_name FROM information_schema.columns
  WHERE table_schema='contract' AND table_name='business_field' AND column_name='status';
-- expect 0 rows

-- 8.5 Confirm Drizzle code compiles and tests pass (separate code slice — see §10)
```

## 9. Rollback

If any step fails inside the BEGIN/COMMIT, the transaction rolls back atomically.
If the apply commits but a later issue is detected, the inverse migration is:

```sql
BEGIN;

ALTER TABLE contract.business_field DROP CONSTRAINT ck_business_field__status;
ALTER TABLE contract.business_field RENAME COLUMN status_code TO status;
ALTER TABLE contract.business_field ADD CONSTRAINT ck_business_field__status
  CHECK (status IN ('draft','certified'));

ALTER TABLE contract.business_object DROP CONSTRAINT ck_business_object__status;
UPDATE contract.business_object SET status_code='approved' WHERE status_code='certified';
ALTER TABLE contract.business_object ADD CONSTRAINT business_object_status_code_check
  CHECK (status_code IN ('draft','approved','deprecated'));

ALTER TABLE contract.canonical_field DROP CONSTRAINT ck_canonical_field__status;
ALTER TABLE contract.canonical_field ADD CONSTRAINT ck_canonical_field__status
  CHECK (status_code IN ('draft','certified','deprecated'));

COMMIT;
```

Rollback only restores the **schema**. If `proposed` / `reviewing` /
`withdrawn` rows were written between apply and rollback, those rows must
be re-mapped to a pre-rollback value (most likely `draft`) before the
rollback's CHECK is reinstated. This is documented to prevent surprise; the
apply window for this packet is short enough that the rollback path is
expected to be theoretical.

## 10. Code-slice sequencing

This DBCP is paired with a code slice that lands **after** the apply, not
before. Sequence:

1. Operator approves this packet.
2. Operator approves the BO state-machine retirement (§6.1) and DTO naming
   (§6.2).
3. Forward DDL (§5) executes inside a transaction.
4. Postflight (§8.1–8.4) confirms DB-side success.
5. Code slice lands:
   - Drizzle schema updates for all three tables.
   - 18 code-site updates per §3.
   - `BusinessObjectService.VALID_TRANSITIONS` retirement.
6. Test sweep (SDA + MCE + schema + business-object tests) goes green.
7. Commit + push bc-core.
8. **Then** SDA-4 state-transition endpoint slice begins (separate session
   / packet, not this one).

If the code slice (step 5) fails to land cleanly, the DB schema and the
running code are temporarily inconsistent. Mitigation: BO `'approved'`
literals will fail Postgres' new CHECK at COMMIT, surfacing the gap
immediately rather than masking it. This is intentional fail-loud
behavior, matching D366 patterns.

## 11. Authority + scope reminders

This packet:
- Does NOT execute DDL.
- Does NOT implement SDA-4 endpoints.
- Does NOT introduce ledger-only state-transition acts (operator explicitly
  rejected Option C in this session).
- Does NOT touch `supersede` / `archive` / `unarchive` — those are a
  separate later DBCP.
- Does NOT touch `metric_contract` / `cc_field_mapping` / tenant binding.

This packet does:
- Document live state and code surface accurately.
- Propose a clean unified target.
- Surface the two operator decisions (§6.1, §6.2) that gate apply.
- Provide forward DDL, preflight, postflight, and rollback that are
  ready to run after approval.

Apply only on explicit operator approval.

---

## 12. Execution result — 2026-05-12, SES-594568

**Status: APPLIED.** Forward DDL §5 executed in a single transaction against
`bc_platform_dev` (Docker container `bc-postgres-redesign`, PostgreSQL 17.8)
via `psql -v ON_ERROR_STOP=1`.

### 12.1 Transaction trace

```
BEGIN
ALTER TABLE          -- 5.1 drop ck_canonical_field__status
ALTER TABLE          -- 5.1 add ck_canonical_field__status (6-value)
ALTER TABLE          -- 5.2 drop business_object_status_code_check
UPDATE 194           -- 5.2 approved → certified on business_object
ALTER TABLE          -- 5.2 add ck_business_object__status (6-value)
ALTER TABLE          -- 5.3 drop ck_business_field__status (legacy 2-value)
ALTER TABLE          -- 5.3 rename column status → status_code
ALTER TABLE          -- 5.3 add ck_business_field__status (6-value)
COMMIT
```

No errors. No statement halted. UPDATE row count matches packet projection (194).

### 12.2 Preflight (§7) — clean

- 7.1 row counts: CF=3,097/draft; BO=194/approved + 8/deprecated;
  BF=6,779/certified + 283/draft. Match packet assumptions exactly.
- 7.2 unexpected-values check: 0 rows. No values outside the union of
  legacy + target vocabularies on any of the three tables.

### 12.3 Postflight (§8) — all four checks pass

**§8.1 — CHECK definitions after apply:**

| Constraint | Definition |
|---|---|
| `ck_canonical_field__status` | `status_code IN ('draft','proposed','reviewing','certified','deprecated','withdrawn')` |
| `ck_business_object__status` | `status_code IN ('draft','proposed','reviewing','certified','deprecated','withdrawn')` |
| `ck_business_field__status`  | `status_code IN ('draft','proposed','reviewing','certified','deprecated','withdrawn')` |

All three tables now carry the identical 6-value CHECK on the unified
`status_code` column. The legacy `business_object_status_code_check`
constraint name is gone (renamed to `ck_business_object__status` for
naming consistency with the other two).

**§8.2 — Row distribution after migration:**

| Table | status_code | rows |
|---|---|---|
| `canonical_field` | `draft` | 3,097 |
| `business_object` | `certified` | 194 |
| `business_object` | `deprecated` | 8 |
| `business_field`  | `certified` | 6,779 |
| `business_field`  | `draft` | 283 |

Totals unchanged at 10,361. No row loss. The 194 BO rows previously
spelled `approved` now read `certified`.

**§8.3 — `approved` fully migrated:**
`SELECT COUNT(*) FROM contract.business_object WHERE status_code='approved'` → `0`.

**§8.4 — Old `business_field.status` column removed:**
`information_schema.columns` returns 0 rows for `(business_field, status)`
and 1 row for `(business_field, status_code)`. Column rename is complete.

**§8.5 — Drizzle/code sweep:** NOT YET RUN. Per operator instruction this
session: "No paired bc-core code slice until DBCP execution succeeds."
The paired Drizzle schema updates + 22 code-site updates + test sweep
will land in a follow-up commit (separate slice).

### 12.4 What is now true

- All three SDA primitive tables hold the full DEC-a17d0f lifecycle
  vocabulary at the database layer.
- Schema/port drift on `business_field` (live had CHECK, Drizzle did not)
  is no longer a drift the *live* DB has; it now lives entirely on the
  Drizzle side as a stale schema definition that must be updated in
  the paired code slice.
- bc-core code at HEAD (89c50dc) is **temporarily inconsistent with the
  DB**: any write of `status_code='approved'` to business_object via the
  current code will fail Postgres' new CHECK at COMMIT. The
  `BusinessObjectService` line-637 site, the `oc-onboarding.service.ts`
  line-128 guard, and the `business_field.status` references at six
  more sites will all error against the new schema. This is the expected
  fail-loud window between DDL apply and the paired code slice.

### 12.5 What must follow (paired code slice — not in this commit)

Per §10 of this packet:

1. Drizzle schema updates for all three tables
   (`contract/canonical-field.ts`, `contract/business-object.ts`,
   `contract/business-field.ts`) — CHECK definitions + BF column rename
   `status` → `statusCode`.
2. 22 code-site updates per §3 — `'approved'` → `'certified'` on BO;
   `.status` → `.statusCode` on BF; Swagger enums; DTO validators.
3. Per §6.1 decision: do **not** modify `BusinessObjectService.VALID_TRANSITIONS`
   in this slice (other than its `'approved'` literals becoming `'certified'`).
   No new BO lifecycle behavior is added; the existing service is preserved
   for the SDA-4 slice to replace.
4. Per §6.2 decision: keep `update-standard-field.dto.ts` line 60
   (`status?: string`) wire-format intact; map to `status_code` internally.
5. Full SDA + MCE + schema + business-object test sweep goes green.
6. Commit + push bc-core.

### 12.6 Authority

Forward DDL applied with explicit operator authorization in SES-594568
on 2026-05-12. No DDL beyond §5 executed; no SDA-4 endpoints written;
no metric repair writes performed; no paired bc-core code changes
committed in the same change window.

**End of packet — APPLIED.**
