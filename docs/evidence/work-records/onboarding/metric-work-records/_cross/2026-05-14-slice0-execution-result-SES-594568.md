---
title: "Slice (0) execution result — MC onboarding extension + SeedPromotionService"
session: SES-594568
date: 2026-05-14
status: executed
executed_at: 2026-05-14
type: slice-execution-result
authority: DEC-a17d0f
related:
  - 2026-05-14-slice0-mc-onboarding-extension-plan-SES-594568.md
  - 2026-05-14-slice1-promotion-gate-plan-SES-594568.md
  - 2026-05-14-session-findings-SES-594568.md
  - 2026-05-14-dbcp-verdict-code-extension-SES-594568.md
  - DEC-01419c
  - DEC-01df6b
  - DEC-4a8abb   # D329
---

# Slice (0) execution result

Plan: `2026-05-14-slice0-mc-onboarding-extension-plan-SES-594568.md`.
Executed 2026-05-14 in disciplined mode (read pass → propose diffs →
approval → implement → test → commit → push → record).

## 1. Commit

| Property | Value |
|---|---|
| Repo | `bc-core` |
| Commit | **`17836ae`** on `main` |
| Push range | `77763ff..17836ae` to `origin/main` |
| Pre-commit hooks | passed cleanly (no `--no-verify`) |
| Files added | 6 |
| Files modified | 2 |
| Total insertions | 1,135 lines |
| Total deletions | 4 lines |

## 2. What was committed

### 2.1 New files

| Path | Lines | Purpose |
|---|---|---|
| `src/registry/formula-deterministic-evaluator.ts` | ~155 | Pure-function recursive-descent arithmetic evaluator. No dynamic code generation. Returns `{value}` or `{error}`. |
| `src/registry/formula-deterministic-evaluator.spec.ts` | ~90 | 14 unit tests. |
| `src/registry/seed-promotion.service.ts` | ~280 | Wrapper service composing `McOnboardingService` with deterministic verification, evidence ledger write, and seed status advance. Three logical phases; orchestration body refactored to 5 small private helpers per QA function-length rule. |
| `src/registry/seed-promotion.service.spec.ts` | ~225 | 8 unit tests (B1–B7 + parse-error case). Factory pattern with Partial mocks. |
| `src/registry/seed-promotion.controller.ts` | ~55 | `POST /onboarding/seed/:id/promote`, `@PlatformOnly()`. |
| `src/registry/mc-onboarding.service.spec.ts` | ~165 | 7 unit tests (A1–A6 + integration on `create()`). |

### 2.2 Modified files

| Path | Change |
|---|---|
| `src/registry/mc-onboarding.service.ts` | (a) `CreateMcDto` gains optional `purposeStatement` and `classificationTags`. (b) New private `validateHeaderOverrides` runs inside `preview()`. (c) Two override sites added with `??` fall-through — one inside `buildMcEnvelope` (header for `contract_json`), one inside `create()` (catalog row passed to `ContractService.createContract`). |
| `src/registry/execution.module.ts` | Register `SeedPromotionService` provider + `SeedPromotionController` controller. Two-line additions plus import lines. |

## 3. Test results

### 3.1 New tests (29 total, all passing)

```
Test Files  3 passed (3)
Tests      29 passed (29)
Duration    ~3.5s
```

Breakdown:

| Spec file | Cases | Status |
|---|---|---|
| `formula-deterministic-evaluator.spec.ts` | 14 | all pass |
| `mc-onboarding.service.spec.ts` | 7 | all pass |
| `seed-promotion.service.spec.ts` | 8 | all pass |

### 3.2 Full suite

```
Test Files  1 failed | 86 passed | 17 skipped (104)
Tests      11 failed | 1353 passed | 69 skipped (1433)
Duration   ~18s
```

The single failing spec file (`reader-runtime.service.spec.ts`, 11
tests, error `Cannot read properties of undefined (reading 'get')`) is
**confirmed pre-existing**: stashing slice (0) changes and re-running
the spec produces identical failures. The break is in
`src/boundary/reader-runtime/`, untouched by this slice. Not caused
by, and not within scope of, slice (0).

### 3.3 TypeScript strict mode

`npx tsc --noEmit -p tsconfig.json` returns **zero errors in slice (0)
files**. The codebase has pre-existing tsc errors in unrelated files
(`src/boundary/action.service.ts`, `src/boundary/evaluation.service.ts`,
`src/boundary/metric.service.ts`, `src/registry/bo-verification.service.ts`,
`src/registry/cc-onboarding.service.ts`, `src/registry/cc-version-bump.service.ts`,
and a few test-only files). These are not caused by slice (0) and are
not within scope.

## 4. Hard rules honored

- **No raw writes to `contract.metric_contract` or
  `contract.metric_contract_version`.** Confirmed by inspection of
  `seed-promotion.service.ts`: only `MetricDefinitionRepository.createVerification`,
  `McOnboardingService.create`, and a single `metric_definition` UPDATE
  are invoked. The contract-tier writes happen inside the official
  service.
- **Verification stays outside `contract_json`**, in
  `metric.metric_formula_verification`, via the existing repository
  writer. Maker/checker/moderator AI columns left NULL — no fabricated
  agreement.
- **Constants persist in `contract_json.body.variables[].value`** via
  the existing service's D329-aware envelope builder. Slice (0) does
  not bypass this.
- **Header purpose / tags override both surfaces** — the
  `contract_json` header (via `buildMcEnvelope`) and the catalog row
  (via `ContractService.createContract`). Backward compatible: existing
  callers (which omit the new fields) get byte-identical behavior to
  pre-slice-(0).
- **`header.kind` kept as `"metric"`.** The envelope builder hardcodes
  it; slice (0) leaves that hardcode alone.
- **`thresholds: []` is no longer valid for slice (1).** Wrapper input
  shape requires exactly 4 thresholds; `McOnboardingService` rejects
  any other count via CR-QG-MC-001.
- **Integration test deferred.** Documented as a deliberate deferral
  in the plan (§6.3) and again in this result — it lives with slice (1)
  execution, not slice (0).

## 5. Plan-vs-reality corrections discovered during read pass

The read pass before implementation surfaced six mismatches between the
slice (0) plan and the actual code. The implementation followed the
real shapes:

1. Header overrides have **two** injection sites (envelope builder + catalog row), not one. Both patched.
2. Module wiring lives in `execution.module.ts` (not `registry.module.ts`).
3. Repository writer is `createVerification` (not `recordFormulaVerification`).
4. No prior spec file existed for `mc-onboarding.service`; the spec is new, not extended.
5. `McOnboardingService.validateThresholdsAndGrain` requires **exactly 4 thresholds**. `PromoteSeedInput.thresholds` is typed accordingly. Slice (1)'s earlier `thresholds: []` design is invalid.
6. The existing engine's `evaluateFormulaExpr` is private and tightly coupled to runtime payloads. A scalar-only standalone evaluator was written; no engine refactor needed.

## 6. Boundaries honored

- One slice. No metric promoted (that's slice (1)).
- No DB schema change. No DBCP filed.
- No bc-admin / bc-portal / bc-ai change.
- No new ADR.
- No RBAC change (TSK-620cf3, out of scope).
- No `KNOWN_CONSTANTS` retirement (TSK-1f4988, out of scope).
- No backfill of existing 540 drift-header MCs (separate slice if ever).
- All new code is additive and backward-compatible.

## 7. Pre-commit QA checks

| Check | Status |
|---|---|
| ESLint | passed |
| No `eval()` / `new Function()` | passed (after rephrasing a comment line that previously matched the regex) |
| Function length cap (60 lines) | passed (after refactoring `promoteSeed` into 5 small helpers) |
| Power-of-Ten / Foundation grep | passed |

No `--no-verify`. The two pre-commit fixes were applied inline before
the successful commit.

## 8. Slice (1) un-park follow-up (separate doc commit)

Slice (1) plan is currently `status: parked`. Un-parking it requires
a separate doc commit that:

- Flips status `parked → plan`.
- Replaces §10 code paths and §11 transactional model with "calls
  `POST /onboarding/seed/:id/promote`".
- Drops the `thresholds: []` framing in §4.3; requires exactly 4
  thresholds.
- References this execution-result MWR.

This MWR does not perform that un-park; it's a separate operator-approved
act.

## 9. What this slice unlocks

- Slice (1) can now promote `revenue_collection_rate` via a single
  POST to the new endpoint, with operator-authored:
  - `purposeStatement` (Foundation-strict description)
  - `classificationTags` (real domain/subfunction slugs)
  - `temporalGate`, `grain`, `thresholds` (4 bands), `inputType`
  - `constantCompletions = { C1: 100 }` (seed-thinness §4.5)
  - `testData` + `expectedOutput` (deterministic check)
- The promotion will:
  - Run the deterministic evaluator and confirm `80`.
  - Write one `metric_formula_verification` row with
    `verdict_code='deterministic_passed'`.
  - Go through `McOnboardingService.create()` (14 quality gates, atomic
    contract writes).
  - Advance the seed's `status_code` from `draft` to `active`.

## 10. Open items for the next session

- **Slice (1) un-park** (doc-only; minor patches to its plan MWR).
- **Slice (1) execution** (single POST + postflight checks + execution-result MWR).
- Pre-flight verification before slice (1) executes — most important: confirm `revenue_collection_rate`'s variables map to a CC `field_selection`. If they don't, `McOnboardingService.preview()` will reject — that's the gate doing its job, and surfaces a real "no CC binds these CFs" condition that operator must resolve before promotion. (Same condition CR-QG-MC-001 was designed to enforce.)

---

**End of slice (0) execution result.**
