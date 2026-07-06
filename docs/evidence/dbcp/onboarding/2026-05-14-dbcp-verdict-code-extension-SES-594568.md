---
title: "DBCP — extend metric_formula_verification.verdict_code CHECK with 'deterministic_passed'"
session: SES-594568
date: 2026-05-14
status: executed
executed_at: 2026-05-14
type: dbcp-execution
authority: DEC-a17d0f
related:
  - 2026-05-14-slice1-promotion-gate-plan-SES-594568.md
  - 2026-05-14-slice1-preflight-result-SES-594568.md
  - 2026-05-14-pass1-calibration-q1-q4-SES-594568.md
classification: dbcp
dbcp_kind: check-constraint-extension
dbcp_target_schema: metric
dbcp_target_table: metric_formula_verification
---

# DBCP — extend `verdict_code` CHECK with `deterministic_passed`

Draft only. **No execution.** Awaits operator approval before any
DDL runs.

## 1. Why this DBCP exists

Slice (1) (seed → catalog promotion gate, one metric,
`revenue_collection_rate`) was approved with verification path
**Option 2 — deterministic-only formula self-demonstration**
(operator decision 2026-05-14). Pre-execution schema inspection
found that `metric.metric_formula_verification.verdict_code`
carries a CHECK constraint admitting only four values, all of
which encode dual-AI maker-checker outcomes:

```
CHECK (verdict_code = ANY (ARRAY['agree','reconciled','disputed','failed']::text[]))
```

Vocabulary meaning:

| Value | Meaning |
|---|---|
| `agree` | Both makers agreed |
| `reconciled` | Makers disagreed; moderator reconciled |
| `disputed` | Makers disagreed; moderator could not reconcile |
| `failed` | Verification act failed |

No existing value names a **deterministic-only** verdict. Using
`agree` for a deterministic-only result would assert (falsely)
that two AI makers compared notes. Per operator instruction
("maker/checker/moderator fields should not be fabricated"),
slice (1) cannot write a verification row honestly under the
current CHECK.

This DBCP extends the CHECK with one new permitted value,
`deterministic_passed`, naming exactly what slice (1) will
produce. The change is **strictly additive**: every value the
current CHECK admits remains admitted; one new value joins them.

## 2. Current state (pre-DBCP)

| Property | Value |
|---|---|
| Schema | `metric` |
| Table | `metric_formula_verification` |
| Column | `verdict_code` (text, NOT NULL) |
| CHECK constraint name | `metric_formula_verification_verdict_code_check` |
| Current CHECK definition | `CHECK ((verdict_code = ANY (ARRAY['agree'::text, 'reconciled'::text, 'disputed'::text, 'failed'::text])))` |
| Rows in table today | **3** (pre-flight finding; Pass 1 §3.3.3) |
| Distribution of `verdict_code` across rows today | Not separately captured; the 3 rows pre-date this DBCP and use the legacy vocabulary. |

Drizzle schema reference (no TypeScript-level enum enforcement;
only a free-text comment):

```ts
// bc-core/src/database/schema/metric/metric-formula.ts:96
verdictCode: text('verdict_code').notNull(), // agree, reconciled, disputed, failed
```

No DTO, zod schema, or TypeScript union narrows the value set
further; the CHECK is the single enforcement point.

## 3. Forward DDL

Two statements, one transaction. PostgreSQL has no
`ALTER CHECK` for value-set changes; the constraint must be
dropped and re-added.

```sql
BEGIN;

ALTER TABLE metric.metric_formula_verification
  DROP CONSTRAINT metric_formula_verification_verdict_code_check;

ALTER TABLE metric.metric_formula_verification
  ADD CONSTRAINT metric_formula_verification_verdict_code_check
  CHECK (verdict_code = ANY (
    ARRAY['agree','reconciled','disputed','failed','deterministic_passed']::text[]
  ));

COMMIT;
```

No data migration. No row updates. No index changes. No FK
changes. No default value change. The column remains `text
NOT NULL`.

## 4. Rollback DDL

Two statements, one transaction. Symmetric to §3 with the new
value removed.

```sql
BEGIN;

ALTER TABLE metric.metric_formula_verification
  DROP CONSTRAINT metric_formula_verification_verdict_code_check;

ALTER TABLE metric.metric_formula_verification
  ADD CONSTRAINT metric_formula_verification_verdict_code_check
  CHECK (verdict_code = ANY (
    ARRAY['agree','reconciled','disputed','failed']::text[]
  ));

COMMIT;
```

**Rollback precondition:** zero rows with
`verdict_code='deterministic_passed'` must exist at rollback
time. Otherwise the `ADD CONSTRAINT` fails. Rollback is
therefore conditional on either (a) slice (1) not having run
yet, or (b) rows produced by slice (1) being explicitly archived
or relabelled first. **Rollback is not automatic** — it is an
operator-explicit recovery path.

## 5. Pre-flight queries (read-only, run immediately before §3)

```sql
-- 5.1 Confirm the constraint still has its current name and shape
SELECT con.conname, pg_get_constraintdef(con.oid) AS def
FROM pg_constraint con
JOIN pg_class cls ON cls.oid = con.conrelid
JOIN pg_namespace nsp ON nsp.oid = cls.relnamespace
WHERE nsp.nspname = 'metric'
  AND cls.relname = 'metric_formula_verification'
  AND con.conname = 'metric_formula_verification_verdict_code_check';
-- Expect 1 row, def matching §2.

-- 5.2 Confirm no row already uses the proposed new value
--     (a value that should not yet be valid; if present, indicates
--     pre-existing schema drift and DBCP is blocked).
SELECT COUNT(*) AS n_unexpected
FROM metric.metric_formula_verification
WHERE verdict_code = 'deterministic_passed';
-- Expect 0.

-- 5.3 Snapshot current row count for post-DDL comparison
SELECT COUNT(*) AS rows_pre FROM metric.metric_formula_verification;
-- Expect 3 (pre-flight finding).

-- 5.4 Snapshot current distribution by verdict_code
SELECT verdict_code, COUNT(*) FROM metric.metric_formula_verification
GROUP BY verdict_code ORDER BY 1;
-- Will be re-checked post-DDL to confirm no row changed.
```

## 6. Post-flight queries (read-only, run immediately after §3)

```sql
-- 6.1 Confirm new CHECK definition is in place
SELECT pg_get_constraintdef(con.oid) AS def
FROM pg_constraint con
JOIN pg_class cls ON cls.oid = con.conrelid
JOIN pg_namespace nsp ON nsp.oid = cls.relnamespace
WHERE nsp.nspname = 'metric'
  AND cls.relname = 'metric_formula_verification'
  AND con.conname = 'metric_formula_verification_verdict_code_check';
-- Expect definition listing all 5 values.

-- 6.2 Confirm row count unchanged
SELECT COUNT(*) AS rows_post FROM metric.metric_formula_verification;
-- Expect 3 (same as pre-flight 5.3).

-- 6.3 Confirm distribution unchanged
SELECT verdict_code, COUNT(*) FROM metric.metric_formula_verification
GROUP BY verdict_code ORDER BY 1;
-- Expect identical to pre-flight 5.4.

-- 6.4 Confirm a probe insert with the new value would succeed
--     (read-only test via a dry-run pattern — does NOT actually
--     insert; runs the CHECK against a synthetic VALUES row).
--     Optional. Slice (1)'s execution will exercise this for real.
SELECT 'deterministic_passed' = ANY (
  ARRAY['agree','reconciled','disputed','failed','deterministic_passed']::text[]
) AS new_value_admitted;
-- Expect true.
```

## 7. Risk assessment

| Risk | Severity | Mitigation |
|---|---|---|
| Existing row(s) violate new constraint | None | New CHECK is strictly broader. All 4 currently-valid values remain valid. PostgreSQL `ADD CONSTRAINT` validates rows on add; relaxation passes by definition. |
| Concurrent writes during DDL | Low | `ALTER TABLE` acquires `ACCESS EXCLUSIVE` lock briefly. Writes pause for the duration (sub-second). No writer is currently active on this table outside this slice's scope. |
| Replication / read-replica lag | None applicable | Single-node dev DB. No replica. |
| Dependent constraints / triggers | None | Single CHECK on this column; no triggers, no FKs reference this column. |
| Drizzle schema drift | Low | The Drizzle schema comment lists 4 values (`bc-core/src/database/schema/metric/metric-formula.ts:96`). The comment becomes stale after DDL. Paired update is a one-line comment refresh — see §10. |
| Misuse of new value in code | Low | No TypeScript enum / zod schema exists; the comment is descriptive only. Writers in slice (1) will use the new value explicitly. |
| Rollback blocked by emitted rows | Low | Rollback precondition is documented in §4. Operator-explicit. |
| Hidden coupling to v3-doc data dictionary | Low | The data dictionary at `bc-docs-v3/docs/data-dictionary/` is auto-generated. Will reflect the new CHECK on next regeneration. |

Overall risk: **low**. The change is the smallest, most additive
shape a CHECK extension can take.

## 8. Nullability and "no fabrication" confirmation

The dual-AI columns on `metric.metric_formula_verification` are
all nullable:

| Column | Nullable | Slice (1) writes |
|---|---|---|
| `maker_a_model` | yes | NULL |
| `maker_a_output` | yes | structured deterministic-compute trace (inputs, expected, actual, formula text, deterministic verdict). The column is JSONB and the contents are honest — no maker model name, no AI reasoning text. |
| `maker_b_model` | yes | NULL |
| `maker_b_output` | yes | NULL |
| `cross_validation` | yes | NULL |
| `moderator_model` | yes | NULL |
| `moderator_verdict` | yes | NULL |

No row written by slice (1) under this DBCP will fabricate AI
agreement, maker identity, or moderator activity. The
`verdict_code='deterministic_passed'` value plus the
deterministic trace in `maker_a_output` is the complete and
honest description of what happened.

## 9. Trust-tier note (carry into slice (1) result MWR)

`deterministic_passed` sits **below** cross-family AI
verification on the trust ladder
(`docs/ai/ai-trust-and-verification.md`):

> Unverified → Deterministic-passed → Single-AI-passed →
> Cross-family-passed → Human-approved

Implications recorded explicitly:

- Slice (1) emits **deterministic** evidence only.
- The calibration MWR's Q4 close named **cross-family AI
  verification** as the long-term promotion gate. This DBCP
  does **not** revise Q4; slice (1) is a pilot/proof of
  promotion mechanics that ships under a lower trust tier as a
  deliberate transitional choice.
- Metric Contract completeness at the future target still
  requires cross-family-passed evidence unless Q4 is formally
  amended by a future ADR.
- The verification rows produced by slice (1) (and any later
  slices that also emit `deterministic_passed`) are honest but
  insufficient for "complete" status under the Q4 target.
  They are real ledger entries; they declare exactly what
  produced them.

## 10. Paired code update (later step, NOT executed in this DBCP)

The Drizzle schema comment will go out of date:

```ts
// bc-core/src/database/schema/metric/metric-formula.ts:96
verdictCode: text('verdict_code').notNull(), // agree, reconciled, disputed, failed
```

Should become:

```ts
verdictCode: text('verdict_code').notNull(),
// agree, reconciled, disputed, failed, deterministic_passed
```

**Not part of this DBCP's DDL.** This comment update is a paired
code change to be made when slice (1)'s code work begins, in the
same commit that introduces the deterministic verifier service
(per slice (1) plan §10). No other code change is forced by the
DBCP. No TypeScript enum exists; no DTO needs updating; no
existing code path reads or writes `verdict_code` with a value
list that needs widening.

A grep audit of `bc-core/src` for the four legacy values
returned no enforced enum and no callsite that lists the
allowed values as a tuple — confirming the paired update is
limited to the schema comment alone.

## 11. What this DBCP does NOT do

- Does **not** add a new column.
- Does **not** drop a column.
- Does **not** change data type.
- Does **not** change nullability of any column.
- Does **not** change indexes or FKs.
- Does **not** alter any other CHECK constraint.
- Does **not** migrate any row.
- Does **not** update any application code (see §10).
- Does **not** change the master-shape JSON, Foundation
  chapter, or any ADR.
- Does **not** add `deterministic_passed` to any other table
  with a verdict-style CHECK (none have been identified, but
  the scope is limited to this single table regardless).

## 12. Boundaries honoured

- Read-only inspection completed first (§2, §5).
- DDL is two-statement, single-transaction, idempotent on
  retry only if the prior attempt rolled back cleanly.
- Rollback DDL provided (§4), with precondition.
- No live writes pending in the table beyond the 3 historical
  rows (none of which violate the new constraint).
- No new ADR, no Foundation amendment.
- One DBCP per the SDA-4 discipline (one act, one MWR).
- Paired code update is explicitly scoped to a single comment
  line, not bundled into this DBCP.

## 13. Approval surface

This DBCP requires operator approval before §3 executes. To
approve:

- Say "approve DBCP verdict_code extension" or equivalent.
- Optionally name a different new-value spelling (e.g.
  `deterministic_pass`, `pass_deterministic`) — I will adjust
  the DDL before executing.

On approval, execution sequence:

1. Run §5 (4 pre-flight queries). Report results.
2. If all pre-flight expectations hold, run §3 (forward DDL)
   inside the BEGIN/COMMIT block.
3. Run §6 (4 post-flight queries). Report results.
4. Write a short DBCP result MWR recording: timestamps,
   pre/post row counts, distribution, new CHECK definition.
5. Stop. Slice (1) execution remains gated on a separate
   "approve slice (1) execution" instruction.

The paired Drizzle comment update (§10) is not executed by this
DBCP — it lands in slice (1)'s code commit.

---

## 14. Execution result (2026-05-14)

DBCP executed on operator approval. Sequence: §5 pre-flight → §3
forward DDL → §6 post-flight. All steps green.

### 14.1 Pre-flight (§5) — actual

| # | Expected | Actual | Verdict |
|---|---|---|---|
| 5.1 | Constraint present with 4-value CHECK | Present. Definition: `CHECK ((verdict_code = ANY (ARRAY['agree'::text, 'reconciled'::text, 'disputed'::text, 'failed'::text])))` | ✓ match |
| 5.2 | 0 rows with `deterministic_passed` | 0 | ✓ |
| 5.3 | 3 rows total | 3 | ✓ |
| 5.4 | Distribution snapshot | All 3 rows `verdict_code='agree'` | ✓ captured |

### 14.2 Forward DDL (§3) — execution

DDL ran via `docker exec` on `bc-postgres-redesign` container,
psql with `-v ON_ERROR_STOP=1`, single transaction.

Statements echoed:

```
BEGIN
ALTER TABLE   -- DROP CONSTRAINT
ALTER TABLE   -- ADD CONSTRAINT (5-value CHECK)
COMMIT
```

No errors. Transaction committed.

### 14.3 Post-flight (§6) — actual

| # | Expected | Actual | Verdict |
|---|---|---|---|
| 6.1 | New CHECK definition lists 5 values | `CHECK ((verdict_code = ANY (ARRAY['agree'::text, 'reconciled'::text, 'disputed'::text, 'failed'::text, 'deterministic_passed'::text])))` | ✓ match |
| 6.2 | Row count unchanged at 3 | 3 | ✓ |
| 6.3 | Distribution unchanged | All 3 rows `verdict_code='agree'` | ✓ identical to pre-flight 5.4 |
| 6.4 | Probe shows new value admitted | `true` | ✓ |

### 14.4 What is now true

- `metric.metric_formula_verification.verdict_code` admits five
  values: `agree`, `reconciled`, `disputed`, `failed`,
  `deterministic_passed`.
- The 3 historical rows are unchanged. None were touched, none
  were re-evaluated.
- Slice (1)'s deterministic verifier can now write a row with
  `verdict_code='deterministic_passed'` honestly.

### 14.5 What remains for slice (1) (NOT done by this DBCP)

- The paired Drizzle schema comment update at
  `bc-core/src/database/schema/metric/metric-formula.ts:96`
  remains pending. Per §10, this is bundled with slice (1)'s
  code commit, not this DBCP. The DB and the comment are now
  in a knowingly drifted state until slice (1) executes; this
  is the explicitly accepted transitional state.
- No verification row has been written. No promotion has run.
- Slice (1) execution remains gated on a separate "approve
  slice (1) execution" instruction.

### 14.6 Rollback availability

Rollback DDL (§4) remains valid. Precondition (zero
`deterministic_passed` rows) currently holds. Rollback becomes
conditional once slice (1) emits its first such row.

---

**End of DBCP execution record.**
