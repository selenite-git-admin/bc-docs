---
title: R3 Verifier Repair Design — Filter Clause Application in Self-Verification (2026-06-23)
description: Diagnosis + smallest-correct-change design for extending `mcf-verifier-v1` so declared `metric_filter_clause` rows are applied during fixture playback. No patch yet — design only.
status: draft
authority: implementation-design
date: 2026-06-23
project: bc-docs-v3
domain: mcf
subdomain: m10-self-verification
focus: verifier-repair-design
governing_adr: DEC-c3e57f
---

# R3 Verifier Repair Design — Filter Clause Application

## 0. Scope and non-goals

**Scope:** read-only diagnosis + design for the smallest correct change to make the M10 self-verifier apply declared `mcf.metric_filter_clause` rows during fixture playback. The current verifier (`mcf-verifier-v1`) hashes filter clauses into `filter_set_hash` (part of the package signature) but never *executes* them, producing a verifier that counts/sums/aggregates unfiltered fixture rowsets.

**Non-goals:** no patch in this batch. No verifier rerun. No fixture append. No Publication Review re-run. No Metric Activation. No PR.

**Known failing case:** Paid Customer Invoice Count v2 (MCV `db3e1bd0…`); see §1.

---

## 1. Confirmed defect (one-paragraph diagnosis)

`MetricSelfVerificationService.verifyFixture` (`metric-self-verification.service.ts:159`) calls `formulaExecutionEngine.execute(ast, sectionA, sectionC)`. The signature does **not** accept filter clauses. The engine's 9 AST node kinds (`variable_ref`, `literal`, `aggregate`, `arithmetic`, `comparison`, `case`, `window`, `time_anchor_resolution`, `bucket_assign`) have no `filter` node — formulas reference variables via `variable_ref(role)` which returns the raw Section A rowset for that role; aggregates then operate on that unfiltered rowset. The metric's filter clauses live in `mcf.metric_filter_clause` and are loaded into `FixtureContext.filterClauses` by `fixture-structural-check.service.ts` (line 103), used by M9 structural checks to confirm fixture rows carry the required `filter_inputs` per row (so per-row data exists), but then **never passed to the engine**. Result: filtered metric formulas evaluate against the full fixture rowset, ignoring the WHERE filters.

For Paid Customer Invoice Count v2: filter `WHERE status (BC 0a860227…) = 'paid'` is declared; the fixture's 3 rows carry per-row `filter_inputs[0a860227…] ∈ {paid, paid, open}`; expected output 2; actual output 3 (all 3 rows counted because the filter wasn't applied).

---

## 2. Filter-clause data plumbing — what already exists

The pre-existing surface is more complete than the defect suggests:

| Layer | Status |
|---|---|
| `mcf.metric_filter_clause` substrate table | ✅ exists; CHECK constraints enforce 11-operator vocabulary (`eq, ne, lt, lte, gt, gte, in, not_in, is_null, is_not_null, between`) and 3 role codes (`where, having, pre_filter`) |
| `FixtureContextFilterClause` TS interface | ✅ defined at `fixture-structural-check.service.ts:82-87` — fields: `clause_role_code`, `bound_business_concept_id`, `operator_code`, `literal_value_json` |
| `loadFixtureContext` returns filter clauses | ✅ confirmed at `fixture-structural-check.service.ts:862` — `filterClauses: asRowArray(filterRows) as FixtureContextFilterClause[]` |
| `MetricSelfVerificationService` calls `loadFixtureContext` | ✅ at line 204-206 — context flows through `executeAndCompare` |
| M9 structural check verifies fixture rows carry `filter_inputs` for declared clauses | ✅ at lines 533-535 (`rowFilterInputContains`) + 539-540 (`collectFilterMissDefectsForVariable`) — defects emitted under structural_reject if fixture rows lack the expected `filter_inputs` for declared filter clauses |
| Filter clauses participate in `filter_set_hash` (package signature) | ✅ via `FormulaCanonicalizationService.computeFilterSetHash` |
| **Engine actually applies filter clauses** | ❌ **MISSING — this is the entire defect** |

The fixture rows are required to carry per-row `filter_inputs` keyed by `bound_business_concept_id` (the M9 check enforces this). So the fixture is "data-complete" for filtering; the engine just has no code path that reads `filter_inputs` against the declared clauses.

---

## 3. Smallest correct change — design

### 3.1 Files to change

| File | Change |
|---|---|
| `bc-core/src/registry/mcf/formula-execution.engine.ts` | Add optional `filterClauses` parameter to `execute()`. Pre-filter every variable in `sectionA` whose rowset rows can be tested against the declared `where` filters. Pass the filtered Section A to the existing AST evaluation. No AST grammar change. |
| `bc-core/src/registry/mcf/metric-self-verification.service.ts` | Single-line plumbing: pass `context.filterClauses` from `executeAndCompare` (line 156-159) into the new `execute()` parameter. |
| `bc-core/src/registry/mcf/formula-execution.engine.spec.ts` | Add the filter-clause unit-test surface (§3.7). |
| `bc-core/src/registry/mcf/metric-self-verification.service.spec.ts` | Add integration-shaped tests that load a real context with filter clauses and confirm pass/fail outcomes. |

**No DDL changes. No new tables. No AST grammar amendment. No schema migration. No new package_signature input.**

### 3.2 Algorithm — pre-filter the Section A rowsets

```ts
execute(ast, sectionA, sectionC, filterClauses): ExecutionResult {
  const filtered = this.applyFilterClauses(sectionA, filterClauses ?? []);
  return this.evaluateNode(ast, filtered, sectionC);
}

private applyFilterClauses(sectionA, filterClauses): SectionAInputs {
  // First pass: support clause_role_code = 'where' only.
  const whereClauses = filterClauses.filter(c => c.clause_role_code === 'where');
  if (whereClauses.length === 0) return sectionA;
  return {
    variables: sectionA.variables.map(v => this.filterVariable(v, whereClauses)),
  };
}

private filterVariable(v, whereClauses): SectionAVariable {
  if (!v.rowset || !Array.isArray(v.rowset)) return v;
  const kept = v.rowset.filter(row => this.rowSatisfiesAll(row, whereClauses));
  return { ...v, rowset: kept };
}

private rowSatisfiesAll(row, whereClauses): boolean {
  for (const clause of whereClauses) {
    if (!this.evaluateClauseAgainstRow(row, clause)) return false;
  }
  return true;
}

private evaluateClauseAgainstRow(row, clause): boolean {
  const fi = row.filter_inputs ?? {};
  const bcId = clause.bound_business_concept_id;
  // M9 structural check has already enforced fixture rows carry filter_inputs[bcId]
  // for declared clauses. Defense-in-depth: missing input means clause cannot be
  // proven satisfied — drop the row to match conservative-filter semantics.
  const input = bcId ? fi[bcId] : null;
  switch (clause.operator_code) {
    case 'eq':         return input === clause.literal_value_json;
    case 'ne':         return input !== clause.literal_value_json;
    case 'is_null':    return input === null || input === undefined;
    case 'is_not_null':return input !== null && input !== undefined;
    case 'lt':         return cmp(input, clause.literal_value_json) <  0;
    case 'lte':        return cmp(input, clause.literal_value_json) <= 0;
    case 'gt':         return cmp(input, clause.literal_value_json) >  0;
    case 'gte':        return cmp(input, clause.literal_value_json) >= 0;
    case 'in':         return Array.isArray(clause.literal_value_json) && clause.literal_value_json.includes(input);
    case 'not_in':     return Array.isArray(clause.literal_value_json) && !clause.literal_value_json.includes(input);
    case 'between':    return Array.isArray(clause.literal_value_json) && cmp(input, clause.literal_value_json[0]) >= 0 && cmp(input, clause.literal_value_json[1]) <= 0;
    default: throw new ExecutionError(`Unknown filter operator: '${clause.operator_code}'`);
  }
}
```

**Key invariants:**
- `where` clauses are conjunctive (row must satisfy ALL `where` clauses → matches SQL semantics).
- `pre_filter` clauses (if any exist in active metrics — currently zero per substrate query) are treated identically to `where` for v2 first pass (semantically clearer: applied before any aggregate).
- `having` clauses are **deferred** — they require post-aggregate evaluation against grouped output, which is a non-trivial addition. First pass throws `NotImplementedError` if any `having` clause is present, so failing safely is loud.
- Missing `filter_inputs[bcId]` for a row drops the row (conservative; M9 should have already structural-rejected).

### 3.3 Operator support scope — first pass

The DDL CHECK admits 11 operators. The failing case + the existing Cleared Invoice Amount active metric together cover 3 operators:
- `eq` (Paid Customer Invoice Count v2)
- `is_not_null` (Cleared Invoice Amount, 1 of 2 clauses)
- `eq` (Cleared Invoice Amount, 1 of 2 clauses)

**First-pass scope: support all 11 operators.** They are mechanically uniform per the design above; the cost of supporting one is roughly the cost of supporting all eleven. Implementing all of them in v1-of-the-fix saves a future expansion cycle.

### 3.4 Null / missing filter input behavior

- **Missing key in `filter_inputs`** for a non-null operator → drop row (defense-in-depth; M9 structural check should have already rejected the fixture).
- **Explicit null value in `filter_inputs[bcId]`:**
  - `is_null` operator → KEEP row
  - `is_not_null` operator → DROP row
  - All other operators → DROP row (null doesn't satisfy comparison or equality)
- **Comparison operators against null literal** → undefined behavior in SQL; design: throw `ExecutionError` (operator must be `is_null`/`is_not_null` for null-literal semantics, per the DDL CHECK).

### 3.5 Algorithm version bump — REQUIRED

The current verifier is `mcf-verifier-v1`. Code header (line 27-28 of `formula-execution.engine.ts`):

> Algorithm version: `mcf-verifier-v1` per D-M10-4. **Forever-locked until ADR-governed bump per DBCP §14.3.**

Adding filter application changes the verifier's behavior for any metric with filter clauses. **This requires an ADR-governed bump to `mcf-verifier-v2`.**

**Implementation requirements:**
- New constant: `export const M10_VERIFIER_ALGORITHM_VERSION = 'mcf-verifier-v2';` in `metric-self-verification.service.ts:44`
- Old `mcf-verifier-v1` verification_result rows on existing MCVs remain immutable per Foundation Invariant III (they are valid historical evidence of "the verifier as of v1, which didn't apply filters")
- New runs under v2 add NEW rows alongside (the substrate unique constraint is on `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)`, so v1 + v2 rows coexist for the same fixture)
- An ADR proposal documenting the v1→v2 semantic change is required before merging

### 3.6 Blast radius on existing active metrics

`metric_filter_clause` row counts per active MC + the two stuck candidates:

| Metric | MCV state | Filter clauses | Operators in use | v2 verdict-change risk |
|---|---|---:|---|---|
| Average Revenue per Invoice (ARPI) | active | **0** | — | **NONE** — v2 verifier is identical to v1 for filter-free metrics |
| Billing Volume | active | **0** | — | **NONE** |
| Cleared Invoice Amount | active | **2** | `where:is_not_null`, `where:eq` | **REAL** — current v1 verifier passed because filters were ignored; v2 would re-evaluate and may produce a different verdict |
| Invoice Processing Cycle Time | active | **0** | — | **NONE** |
| Billing Cycle Time | review (stuck on PE-MC-11 / chain) | **0** | — | **NONE** — orthogonal failure mode |
| Paid Customer Invoice Count v2 | review (stuck on PE-MC-10 / verifier) | **1** | `where:eq` | **TARGET** — v2 should change actual=3 → actual=2, flipping PE-MC-10 to PASS |

**Cleared Invoice Amount is the blast-radius concern.** It's currently active under v1 evidence. Two scenarios under v2:
- **Scenario A (likely):** CIA's fixture rows happen to satisfy all 2 filter clauses (e.g., `clearing_date` is not null for all rows AND status equals the expected value). v2 verifier produces PASS — identical functional outcome to v1.
- **Scenario B:** CIA's fixture has at least one row that fails the filters, so v2 verifier evaluates the formula against a different (smaller) rowset and produces a different `actual.value`. If `actual ≠ expected`, v2 returns FAIL.

**Recovery handling for CIA if Scenario B occurs:**
- CIA's MCV `57ea07d0…` stays ACTIVE per Foundation IV (activation is irrevocable; v1 PASS evidence remains valid).
- The new v2 FAIL row is added alongside; PE-MC-10 (if Publication Review is re-run under v6) would surface the v2 fail and flip to REJECT.
- This does NOT auto-deactivate CIA. But it creates a documented inconsistency the operator must resolve (typically by re-authoring CIA's fixture under correct filter semantics; an Append Fixture operation re-binds against a passing v2 verifier_result).

**Recommended mitigation:**
- Run v2 verification against CIA's fixture as a **read-only dry run** (perhaps via a feature flag or test-mode invocation that does NOT write to substrate) to forecast which scenario applies before merging v2.
- If Scenario B, prepare a CIA fixture-amendment plan **before** merging the v2 patch.

### 3.7 Tests required

Add unit tests in `formula-execution.engine.spec.ts`:

1. **filter_clauses: undefined or empty** → identical behavior to current engine (regression).
2. **`where:eq`** → rows matching keep, others drop. Verify count_distinct + sum.
3. **`where:is_null` + `where:is_not_null`** → null semantics.
4. **`where:lt`/`lte`/`gt`/`gte`/`between`** → numeric range filtering.
5. **`where:in`/`not_in`** → array-membership filtering.
6. **Multiple `where` clauses** → conjunctive semantics.
7. **Missing `filter_inputs[bcId]`** → defensive drop (M9 should have caught this; engine treats as drop, not throw).
8. **`having` clause present** → throws `NotImplementedError` (loud failure for the deferred path).
9. **`pre_filter` clause** → treated like `where` (or operator-decided to defer in a follow-up).

Add integration tests in `metric-self-verification.service.spec.ts`:

10. **Paid Customer Invoice Count v2 replay** (real fixture body + real filter clause) → produces actual=2, verdict=pass under v2.
11. **CIA-shaped fixture with `is_not_null` + `eq` filters** → produces the expected outcome (specific value TBD by operator after Scenario A/B determination).

### 3.8 Estimated patch surface (no patch in this batch)

- 2 production files changed (`formula-execution.engine.ts`, `metric-self-verification.service.ts`)
- 2 spec files updated (unit + integration)
- 1 constant value change (`'mcf-verifier-v1'` → `'mcf-verifier-v2'`)
- 1 ADR authored for the verifier bump
- ~120-180 lines added (estimate)
- Zero migrations, zero schema changes, zero new env vars, zero new dependencies

---

## 4. Recommendation

**Proceed to implementation after these gates are cleared:**

1. **Author the ADR** for the `mcf-verifier-v1 → mcf-verifier-v2` bump under D-M10-4's ADR-governed-bump requirement. Capture the rationale ("filter clauses were declared and hashed but never executed; v2 adds executor application"), the blast-radius analysis (this document), and the migration semantics (additive; old v1 rows preserved under Foundation III).
2. **Run a read-only v2 dry-run against CIA's fixture** to forecast Scenario A vs B. If Scenario B, prepare CIA fixture re-authoring plan before merging.
3. **Implement v2** per §3.2 + §3.7 design. Test under feature-flag or new code path; flip `M10_VERIFIER_ALGORITHM_VERSION` constant only after spec coverage is in place.
4. **Run v2 against Paid Customer Invoice Count v2's fixture** — expected to flip PE-MC-10 PASS once Publication Review re-evaluates under `mcf-m13-v6` (a follow-up R1 step after v2 lands).
5. **Re-run v2 against CIA** under the resolved Scenario A or B plan.

**Not recommended:** treating the change as a "bug fix inside v1" (no version bump). This violates the D-M10-4 forever-lock and creates silent semantic drift for any preserved v1 evidence row. The Foundation-disciplined path is the ADR-governed bump.

---

## 5. Open questions for operator decision

1. **Scenario A vs B for CIA** — dry-run before merge, or merge and accept whichever scenario surfaces?
2. **`having` clause** — defer to a v3 or implement now? (Currently zero active metrics use `having`; can defer safely.)
3. **`pre_filter` clause** — treat identically to `where` in v2 (recommended), or implement distinct semantics? (Currently zero active metrics use `pre_filter`.)
4. **Backfill verification under v2** — should the operator schedule v2 dry-runs against all existing fixtures (including the 4 active MCs) to verify Scenario A holds before any production-side v2 invocation?

---

## 6. No-patch confirmation

This document is design and recommendation only. No file was edited, no DB row written, no verifier rerun, no fixture append, no Publication Review re-run, no Metric Activation attempted, no PR opened. The two stuck MCVs (`Billing Cycle Time` and `Paid Customer Invoice Count v2`) remain in their `review` state with no MCF substrate changes from this investigation.

Implementation requires operator authorization following ADR drafting + CIA dry-run forecast.
