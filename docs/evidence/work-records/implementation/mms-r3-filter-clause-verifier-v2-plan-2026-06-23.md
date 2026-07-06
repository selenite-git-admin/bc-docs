---
title: R3 Verifier v2 — Implementation Plan
description: Engineering checklist for the v1→v2 self-verifier bump per ADR DEC-2411e4 / D450. Files-to-change, test list, dry-run procedure, merge sequence, post-merge verification. Companion to the ADR's "why" with the "how".
status: draft
authority: implementation-plan
date: 2026-06-23
project: bc-docs-v3
domain: mcf
subdomain: m10-self-verification
focus: verifier-v2-implementation
governing_adr: DEC-2411e4
related_adrs: [DEC-c3e57f]
---

# R3 Verifier v2 — Implementation Plan

This document is the engineering checklist for the `mcf-verifier-v1 → mcf-verifier-v2` bump. The ADR [DEC-2411e4 / D450](../../../governance/adrs/ADR-2411e4.md) is the authority for *why*; this plan is the *how*. No code is patched in this batch.

## 0. Operator-gated entry criteria

Before any code is written:

- [ ] ADR `DEC-2411e4` reviewed and flipped from `proposed` → `decided` by the operator.
- [ ] CIA dry-run forecast complete (see §4) and Scenario A/B verdict known. If Scenario B, fixture-amendment plan authored before merge.
- [ ] No conflicting active engineering work on `formula-execution.engine.ts` or `metric-self-verification.service.ts`.

## 1. Files to change

### Production source (2 files)

| File | Change |
|---|---|
| `bc-core/src/registry/mcf/formula-execution.engine.ts` | Add optional `filterClauses?: FixtureContextFilterClause[]` parameter to `execute()`. Add private `applyFilterClauses(sectionA, filterClauses)` helper. Add private `evaluateClauseAgainstRow(row, clause)` with 11-operator switch. Throw `NotImplementedError` on any `having` clause. Update file-header comment to `mcf-verifier-v2` + cite DEC-2411e4 in the algorithm-version locks. No AST grammar change. |
| `bc-core/src/registry/mcf/metric-self-verification.service.ts` | `export const M10_VERIFIER_ALGORITHM_VERSION = 'mcf-verifier-v2';` (line 44). Update the file-header JSDoc reference from "Algorithm version: mcf-verifier-v1" to v2 + cite DEC-2411e4. Pass `context.filterClauses` into `formulaExecutionEngine.execute(ast, sectionA, sectionC, context.filterClauses)` at the call site currently at line 159. |

### Spec source (2 files)

| File | Change |
|---|---|
| `bc-core/src/registry/mcf/formula-execution.engine.spec.ts` | Add a new `describe('FormulaExecutionEngine — filter clause application (v2)')` block with the 9 unit cases listed in §2. |
| `bc-core/src/registry/mcf/metric-self-verification.service.spec.ts` | Add `describe('M10 v2 — filter clause replay')` block with 2 integration-shaped cases (Paid Customer Invoice Count v2, CIA dry-run reproduction). |

### Imports

`formula-execution.engine.ts` needs to import `FixtureContextFilterClause` from `./fixture-structural-check.service`. The interface is already exported.

### What does NOT change

- No DDL changes.
- No new schema columns.
- No new tables.
- No new env vars.
- No new dependencies.
- No NestJS module / DI changes.
- No new package_signature inputs.
- The 9 AST node kinds remain unchanged.
- The `mcf.metric_filter_clause` table is unchanged.
- The `M10_VERIFIER_ALGORITHM_VERSION` is the ONLY runtime VALUE that changes (and it changes by one character: `v1` → `v2`).

## 2. Unit test cases (in `formula-execution.engine.spec.ts`)

Each case constructs a minimal AST + Section A + filter clause set and asserts the engine's `execute()` output.

| # | Case | Setup | Assertion |
|---:|---|---|---|
| 1 | Empty / undefined filter clauses → identical to v1 | Any AST, 3-row rowset, `filterClauses = []` (or omitted) | `actual.value` equals what v1 produced |
| 2 | Single `where:eq` clause | `count_distinct(id)`, 3 rows {paid, paid, open}, clause `WHERE status_bc = 'paid'` | `actual.value = 2` |
| 3 | `where:ne` clause | Same shape but `WHERE status_bc != 'open'` | `actual.value = 2` |
| 4 | `where:is_null` and `where:is_not_null` | Rows where one BC has null, others not | `is_null` keeps the null row; `is_not_null` drops it |
| 5 | Numeric range: `lt, lte, gt, gte, between` | Rows with amounts 100, 200, 300 | Each operator's boundary semantics |
| 6 | Array membership: `in, not_in` | Rows with status ∈ {paid, open, void} | `in:['paid','open']` keeps 2; `not_in:['void']` keeps 2 |
| 7 | Two conjunctive `where` clauses | 3 rows with two BCs each | Row must satisfy both; output count reflects intersection |
| 8 | Missing `filter_inputs[bcId]` | Row lacks the required `filter_inputs` key | Row is DROPPED, no throw |
| 9 | `having` clause present | Any clause with `clause_role_code='having'` | Engine throws `NotImplementedError` mentioning DEC-2411e4 |
| 10 | `pre_filter` clause | Clause with `clause_role_code='pre_filter'` and same shape as `where` | Treated identically to `where` |
| 11 | Null literal with non-null operator | Should not occur (DDL CHECK forbids), but defensive | Engine throws `ExecutionError` if encountered |

## 3. Integration test cases (in `metric-self-verification.service.spec.ts`)

| # | Case | Setup | Assertion |
|---:|---|---|---|
| 12 | Paid Customer Invoice Count v2 replay | Real fixture body (3 rows: INV-1001 paid, INV-1002 paid, INV-1003 open) + real filter clause `WHERE status_bc='paid'` + count_distinct AST | Verifier produces `verdict_code='pass'`, `actual.value=2` matching `expected.value=2` |
| 13 | CIA-shaped fixture replay (Scenario A — likely) | CIA's fixture rows that satisfy both `is_not_null` + `eq` clauses | `verdict_code='pass'`, `actual.value` matches CIA's expected output |
| 14 | CIA-shaped fixture replay (Scenario B — if forecast surfaces it) | CIA's fixture rows where at least one fails a filter | Documents the v2 actual output for operator decision (test may be PENDING until CIA is amended) |
| 15 | Filter-free regression — ARPI/IPCT shape | Existing fixture with no filter clauses | `verdict_code='pass'`, identical actual.value to v1 record |

## 4. CIA dry-run procedure (pre-merge, REQUIRED)

The dry-run forecasts whether v2 changes CIA's verdict before the constant is flipped. Two acceptable execution modes:

### Option A — pure unit-test dry-run (recommended)

Add a temporary unit test that:
1. Constructs a `FormulaExecutionEngine` instance.
2. Loads CIA's fixture body (`section_a_inputs_json`, AST) from substrate via a one-off SELECT or a test-fixture copy.
3. Loads CIA's two filter clauses from substrate (via SELECT against `mcf.metric_filter_clause`).
4. Calls `engine.execute(ast, sectionA, sectionC, filterClauses)`.
5. Compares the result to CIA's existing v1 `verdict_payload_json.diff.actual.value`.
6. Reports Scenario A (identical) or Scenario B (different); does NOT write to substrate.

This is contained entirely in the spec layer; the production constant remains `'mcf-verifier-v1'` throughout the dry-run.

### Option B — temporary scratch path (if Option A blocked)

Add a `verifyFixtureDryRun(fixtureUid, deps)` method that runs the v2 pipeline but does NOT call `insertResultRow`. Returns the verdict + actual value without persisting. Remove the method after the dry-run completes. Risk: introduces a temporary code path that must be cleaned up before merge.

Option A is preferred — it has no production surface area.

### Dry-run outcome routing

- **Scenario A (identical):** proceed to §5. CIA's v1 PASS evidence remains valid; v2 will produce the same outcome.
- **Scenario B (different):** halt merge. Author a CIA fixture-amendment plan: identify which rows fail a filter, decide whether the fixture is wrong (re-author rows) or the metric semantics are wrong (operator decision, possibly R7 Restart from Draft for CIA). Re-attempt v2 merge only after CIA's fixture is corrected and a v2 dry-run produces PASS.

## 5. Merge sequence

1. Write the v2 engine code + spec coverage per §1 + §2 + §3.
2. Run the CIA dry-run unit test per §4 (Option A). Confirm Scenario A or B.
3. If Scenario A: continue. If Scenario B: halt; address CIA fixture; restart.
4. Flip `M10_VERIFIER_ALGORITHM_VERSION` from `'mcf-verifier-v1'` to `'mcf-verifier-v2'`.
5. Run full bc-core unit + integration test suite. All 4 active MCs' specs must pass (ARPI/Billing Volume/IPCT unchanged; CIA covered by Scenario A confirmation).
6. Run `npx tsc --noEmit` and confirm no new errors.
7. Author the commit with subject: `feat(mcf): bump self-verifier to mcf-verifier-v2 — apply filter clauses (DEC-2411e4)`.

No PR opened automatically — operator authorization required for PR creation per session locks.

## 6. Post-merge verification

After the v2 patch merges and bc-core is restarted with the new constant:

### 6.1 Recovery of Paid Customer Invoice Count v2

- [ ] Operator-authorized call to re-verify the fixture under v2. Choice of path:
  - **Path A (recommended):** call the M10 verifier service directly (e.g., via a small Node CLI or the operator-direct verify endpoint if one is exposed) to produce a fresh v2 row.
  - **Path B:** wait for the next Publication Review re-evaluation to trigger upstream re-verification.
- [ ] Expected post-condition: a new `mcf.metric_self_verification_result` row with `verifier_algorithm_version = 'mcf-verifier-v2'`, `verdict_code = 'pass'`, `verdict_payload_json.diff.actual.value = 2`.
- [ ] Run R1 Re-evaluate Publication Review under `mcf-m13-v6` for MCV `db3e1bd0-051b-401f-8278-e3cd84e622a7`. Expected: PE-MC-10 = PASS (was REJECT).
- [ ] Confirm `governance_state_code` remains `review` (no auto-activation).
- [ ] Operator decision on Metric Activation timing (separate batch).

### 6.2 Cleared Invoice Amount post-merge

- [ ] If Scenario A confirmed in §4: optionally re-verify CIA under v2 to materialize the v2 evidence row alongside the v1 row. Confirms zero verdict change in production. Operator decision on whether to do this proactively.
- [ ] If Scenario B was resolved via fixture amendment: ensure the amended fixture has a v2 PASS row; verify Publication Review under `mcf-m13-v6` shows PE-MC-10 PASS.

### 6.3 Other active MCs (ARPI, Billing Volume, IPCT)

- [ ] No required action — zero filter clauses → v2 produces identical results to v1 for these metrics. Optional proactive re-verification under v2 for hygiene; not blocking.

## 7. Rollback plan

If v2 surfaces an unexpected problem after merge that cannot be safely contained:

- Revert the commit. The constant returns to `'mcf-verifier-v1'`. New runs again produce v1 rows.
- v2 rows already written remain immutable under Foundation III; they continue to be valid evidence of "what v2 did when it ran."
- No data loss; no migration to roll back.

The rollback path is purely a code revert; no substrate cleanup required.

## 8. Out of scope / future work

- **`having` clause** — deferred to v3 or v2.1 ADR amendment. No active or stuck metric currently uses it.
- **AST `filter` node kind** — if a future metric needs filters expressed inside the formula (e.g., conditional aggregates), an AST grammar extension is required. Separate ADR.
- **Cross-variable filter clauses** — current scope assumes each filter clause's `bound_business_concept_id` matches one BC referenced by one variable's `filter_inputs`. Filters spanning multiple variables (joins) are out of scope.
- **Filter clause caching / optimization** — the v2 pre-filter is O(rows × clauses) per variable. No optimization needed at current scale.

## 9. Estimated effort

- ADR drafting: complete (this batch).
- Code + spec implementation: 3–5 hours of focused work.
- CIA dry-run: 30 minutes if Scenario A; 1–3 days if Scenario B (fixture re-authoring).
- Operator-authorized recovery of Paid Customer Invoice Count v2 + Publication Review re-evaluation: ~30 minutes.
- Total wall-clock: 1 day (Scenario A path) or 2–4 days (Scenario B path).

## 10. No-patch confirmation

This document is plan and recommendation only. No file in `bc-core/src` was edited. The `M10_VERIFIER_ALGORITHM_VERSION` constant remains `'mcf-verifier-v1'`. No DB row was written, no verifier rerun, no fixture append, no Publication Review re-run, no Metric Activation, no PR.

The two stuck MCVs (`Billing Cycle Time` and `Paid Customer Invoice Count v2`) remain in their current `review` state with no MCF substrate changes from this design step.

Implementation is gated on operator review of ADR DEC-2411e4 and authorization of the CIA dry-run path.
