---
title: "Slice (0) plan — MC onboarding service extension + seed-promotion wrapper"
session: SES-594568
date: 2026-05-14
status: plan
type: slice-plan
authority: DEC-a17d0f
related:
  - 2026-05-14-pass1-calibration-q1-q4-SES-594568.md
  - 2026-05-14-slice1-preflight-result-SES-594568.md
  - 2026-05-14-slice1-promotion-gate-plan-SES-594568.md
  - 2026-05-14-session-findings-SES-594568.md
  - 2026-05-14-dbcp-verdict-code-extension-SES-594568.md
  - DEC-01419c   # MC body purity
  - DEC-01df6b   # contract_json authoritative
  - DEC-4a8abb   # D329 — MC constants
---

# Slice (0) plan — MC onboarding service extension + seed-promotion wrapper

Plan only. No code, no DB writes, no ADR/DBCP filed yet.
Operator approval required before execution.

## 1. Goal

Make the official MC onboarding path capable of supporting
slice (1)'s seed→catalog promotion act honestly, without raw
DB writes. Two narrow extensions, designed to compose:

- **(A) Header overrides on `McOnboardingService`.** Optional
  caller-supplied `purposeStatement` and `classificationTags`,
  defaulting to today's hardcoded values when omitted. Keeps
  existing callers byte-identical. New callers (slice (1) and
  beyond) can author Foundation-strict header values per the
  session-findings §4 β decision.
- **(B) New `SeedPromotionService` wrapper.** Reads a seed,
  runs deterministic formula self-demonstration, writes the
  `metric_formula_verification` ledger entry, calls the
  extended `McOnboardingService.create()` on pass, advances
  the seed's `status_code`. The wrapper composes the existing
  service rather than reimplementing it.

After slice (0) succeeds: slice (1) is unblocked and becomes a
single wrapper call against `revenue_collection_rate`.

## 2. Scope

In:

- TypeScript code in `bc-core/src/registry/mc-onboarding.service.ts`
  (DTO extension + envelope-builder call-site changes).
- A new TypeScript file
  `bc-core/src/registry/seed-promotion.service.ts` and its
  controller `seed-promotion.controller.ts`.
- A new endpoint `POST /onboarding/seed/:id/promote`.
- Unit tests for both surfaces.
- One integration test exercising both passes and rejections.

Out:

- No DB schema change. The DBCP from earlier this session
  (`deterministic_passed` added to `verdict_code` CHECK) is
  already applied; no further DBCP needed.
- No master-shape JSON change. The slice operates within the
  existing 9-key body shape and existing header keys; only
  caller-supplied default-override behavior changes.
- No header `kind` change. Builder keeps `kind="metric"` —
  reframing kind is a separate architectural question.
- No CC creation, no BF/CF creation, no tenant binding.
- No promotion of any actual metric. (That's slice (1).)
- No backfill of existing 540 MCs' headers. (Tracked
  separately if/when chosen.)
- No new ADR. The decisions baked in (β header authoring,
  seed-thinness/promotion-formalization, deterministic
  verification tier) are operator decisions already recorded
  in the calibration MWR + session findings MWR; this slice
  implements them.

## 3. Existing surface (briefly)

`McOnboardingService.create(dto: CreateMcDto)` today:

- Runs `preview(dto)` — builds envelope via
  `buildMetricEnvelope` from `contract-envelope.builder.ts`,
  validates against CR-QG-MC-001 (14 quality gates including
  D329 constant-value presence per R5), resolves `co_bindings`
  from CC field_selection, returns `valid` + checks +
  envelope.
- On invalid preview: throws `UnprocessableEntityException`
  with failed checks.
- On valid preview: registers any missing output BFs as
  computed, calls `ContractService.createContract` →
  `createVersion(envelope)` → `activateVersion('1.0.0')`.
- Hardcodes header `tags = dto.variables.map(v => v.varCode)`
  (line 443) and `description = \`Metric contract: ${dto.formula.text}\``
  (line 442). These are the source of the live drift
  recorded in session findings §4.

`McOnboardingController` mounts at `/onboarding/mc` with
`@PlatformOnly()`. No tenant scoping.

The service does **not** write to
`metric.metric_formula_verification` and does **not** touch
`metric.metric_definition.status_code`. Those are out of its
current concern.

## 4. Design — Part A: `McOnboardingService` header overrides

### 4.1 DTO addition

`CreateMcDto` gains two optional fields:

```ts
export interface CreateMcDto {
  // ... existing fields unchanged ...
  /**
   * Foundation §Common Header `description` — contract purpose
   * statement. When provided, replaces the default formulaic
   * value. Recommended for new promotions per session-findings §4 (β path).
   */
  purposeStatement?: string;
  /**
   * Foundation §Common Header `tags` — array of classification
   * slug strings. When provided, replaces the default variable-code
   * fallback. Recommended for new promotions per session-findings §4 (β path).
   */
  classificationTags?: string[];
}
```

Both fields are **optional**. Backward-compatible default
behavior preserved.

### 4.2 Service create() change-site

Lines 442–443 today:

```ts
description: `Metric contract: ${dto.formula.text}`,
tags: dto.variables.map(v => v.varCode),
```

Become:

```ts
description: dto.purposeStatement ?? `Metric contract: ${dto.formula.text}`,
tags: dto.classificationTags ?? dto.variables.map(v => v.varCode),
```

Same pattern applies inside `preview()` if it builds the
envelope independently (to be confirmed at execution-start —
one read of `preview()` body).

### 4.3 Validation rule additions (CR-QG-MC-001)

Two **soft** validation rules added (warnings, not failures —
both fields are optional):

- If `classificationTags` is provided, each entry must be a
  lowercase slug `^[a-z][a-z0-9_-]{1,40}$`. Reject malformed.
- If `purposeStatement` is provided, length ∈ [40, 2000]
  characters. Reject otherwise. (Foundation says "Contract
  purpose statement" without bounds; the floor matches the
  SDA-4 override rationale floor of 40 from earlier sessions.)

These are validation failures, not gate count increases — the
gate count stays at 14 unless we explicitly add a new gate.
Decision recorded: **do not add a new CR-QG gate in this slice**;
the new fields are caller-controlled, not catalog invariants.

### 4.4 What does NOT change in Part A

- `header.kind` stays hardcoded to `"metric"` in
  `buildMetricEnvelope`. Reframing kind as a Foundation-aligned
  subtype is a separate slice, not this one.
- `header.owner`, `header.tenant_scope`, `header.governance`,
  `header.compatibility_policy` all keep their current default
  shapes.
- `header.lineage` and `header.bindings` stay `[]` per current
  pattern (existing MCs are all-empty for these; reviewing
  whether they should be populated is a separate finding).
- D329 `variables[].value` handling — already correct, no
  change.

## 5. Design — Part B: `SeedPromotionService` wrapper

### 5.1 Purpose

The generic `McOnboardingService.create()` is generic. The
seed → catalog promotion act is **richer**: it adds
deterministic verification + ledger emission + seed advance.
Per operator decision 2026-05-14, those concerns live in a
**new wrapper service**, not inside `McOnboardingService`.

### 5.2 New file: `bc-core/src/registry/seed-promotion.service.ts`

Public method:

```ts
async promoteSeed(input: PromoteSeedInput): Promise<PromoteSeedResult>
```

Where:

```ts
export interface PromoteSeedInput {
  metricDefinitionId: string;          // uuid — the seed
  // Body fields the seed does NOT supply (per seed-thinness):
  inputType: 'primary' | 'derived';    // master-shape enum
  temporalGate: { fieldCode: string; requiredPeriods: number; completenessThreshold: number };
  grain: Array<{ key: string; source: 'business_field' | 'evaluation_period'; fieldCode?: string }>;
  // Constant completions for seed-side NULL constants (D329 / §4.5):
  constantCompletions?: Record<string /* var_code */, number>;
  // Deterministic verification payload:
  testData: Record<string /* var_code */, number>;
  expectedOutput: number;
  // Foundation-strict header (β path, both optional):
  purposeStatement?: string;
  classificationTags?: string[];
}

export interface PromoteSeedResult {
  metricContractId: string;
  metricContractVersionCode: '1.0.0';
  verificationId: string;
  seedStatusAdvanced: boolean;
}
```

### 5.3 Service algorithm (high-level)

1. **Load the seed.** Fail if not found or not `status_code='draft'`.
2. **Load the seed's current formula + variables** from
   `metric.metric_formula` (is_current=true) +
   `metric.metric_formula_variable`. Build a normalized
   variables array, projecting seed `field_name` → body
   `field_code`, applying `constantCompletions` to populate
   `value` for constants whose seed-side `constant_value` is
   NULL, and translating seed `direction_code` (snake_case) →
   master-shape kebab-case.
3. **Deterministic verification.** Pure-function evaluator
   parses formula text, substitutes `testData` (including
   constants from completions), computes actual output,
   compares to `expectedOutput`. **Held in memory; no DB write
   yet.**
4. **On verification fail:** throw
   `UnprocessableEntityException`; **no row written anywhere**
   (matches slice (1) §8: failed verification writes nothing).
5. **On verification pass — TX1 (audit):** insert one row into
   `metric.metric_formula_verification` via existing
   `MetricDefinitionRepository.recordFormulaVerification`
   helper, with `verdict_code='deterministic_passed'`,
   `maker_a_output` carrying the deterministic trace, all
   maker/checker/moderator AI columns NULL. Capture the
   returned `verification_id`.
6. **TX2 (state advance) — invoke McOnboardingService.create().**
   Build the `CreateMcDto` with seed-derived + operator-authored
   body fields, plus `purposeStatement` / `classificationTags`
   passed through. Service runs CR-QG-MC-001 and creates the
   contract atomically.
7. **TX3 (seed advance) — update seed.** `UPDATE metric.metric_definition
   SET status_code='active', verification_result_code='pass',
   verification_evidence_id=$verification_id WHERE metric_definition_id=$1`.
8. **Return result.**

Three transactions, but they compose:
- TX1 commits independently — verification audit is durable
  whether or not promotion completes.
- TX2 is the service's own internal transaction.
- TX3 is small and runs only after TX2 succeeds.

If TX2 fails (e.g. CR-QG-MC-001 rejects), TX1's verification
row remains as evidence; the operator has an audit trail of
"verification passed but promotion gate rejected." Acceptable
state.

If TX3 fails after TX2 succeeded, the operator manually
recovers (rare; the UPDATE is one row, no FK issues).

### 5.4 Controller

New `bc-core/src/registry/seed-promotion.controller.ts`:

```ts
@PlatformOnly()
@Controller('onboarding/seed')
export class SeedPromotionController {
  constructor(private readonly service: SeedPromotionService) {}

  @Post(':id/promote')
  @HttpCode(HttpStatus.CREATED)
  promote(
    @Param('id', ParseUUIDPipe) metricDefinitionId: string,
    @Body() dto: Omit<PromoteSeedInput, 'metricDefinitionId'>,
  ) {
    return this.service.promoteSeed({ ...dto, metricDefinitionId });
  }
}
```

Mounted under the existing onboarding namespace. `@PlatformOnly()`
per bc-admin scope.

### 5.5 Module wiring

`registry.module.ts` (or wherever `McOnboardingService` is
registered) gains:

- `SeedPromotionService` as a provider
- `SeedPromotionController` registered
- `MetricDefinitionRepository` as a dependency (already
  exists)

No changes to other modules.

## 6. Tests

### 6.1 Part A — McOnboardingService header overrides

Unit tests in
`bc-core/src/registry/mc-onboarding.service.spec.ts` (extend
existing):

| # | Case | Assertion |
|---|---|---|
| A1 | `purposeStatement` omitted | `header.description = "Metric contract: <formula.text>"` (existing default preserved) |
| A2 | `purposeStatement = "<40 chars"` | `UnprocessableEntityException`, message names the rule |
| A3 | `purposeStatement = "<sane string ≥40>"` | `header.description = "<sane string>"` |
| A4 | `classificationTags` omitted | `header.tags = ["O1","I1","I2",...]` (existing default preserved) |
| A5 | `classificationTags = ["TAG"]` (uppercase) | rejection with slug-format message |
| A6 | `classificationTags = ["finance","ar"]` | `header.tags = ["finance","ar"]` |

### 6.2 Part B — SeedPromotionService

Unit tests in new
`bc-core/src/registry/seed-promotion.service.spec.ts`:

| # | Case | Assertion |
|---|---|---|
| B1 | Seed not found | `NotFoundException` |
| B2 | Seed `status_code != 'draft'` | `UnprocessableEntityException` |
| B3 | Formula parses, deterministic check matches | TX1 row written with `deterministic_passed`, TX2 + TX3 succeed |
| B4 | Deterministic computed ≠ expected | `UnprocessableEntityException`, **no row written** anywhere |
| B5 | TX2 fails (CR-QG-MC-001 rejection — e.g. missing CC field_selection) | TX1 verification row exists, TX2 throws, TX3 not attempted, seed stays `draft` |
| B6 | Constant completion provided when seed-side `constant_value` NULL | `value` lands in body via service DTO `variables[].value` |
| B7 | β header authoring | `purposeStatement` + `classificationTags` reach the envelope through Part A |

### 6.3 Integration test

One end-to-end Vitest spec hitting the real `/onboarding/seed/:id/promote`
endpoint against the test DB. Seeds a definition + formula + variables,
calls the endpoint, asserts on the four post-states (MC row, version
row, verification row, seed status).

## 7. Postflight checks (after slice (0) execution)

```bash
# Run new unit tests
npx vitest run mc-onboarding.service.spec.ts
npx vitest run seed-promotion.service.spec.ts

# Run full test suite to confirm no regression
npx vitest run
```

DB state assertion (post-slice-0):

- `metric.metric_formula_verification` row count unchanged
  from 3 (slice (0) doesn't write rows — only slice (1) does).
- No new `contract.metric_contract` row (slice (0) doesn't
  promote anything).
- All existing tests still pass.

## 8. What slice (0) does NOT do

- Does not promote any metric.
- Does not write to `metric.metric_formula_verification`.
- Does not write to `contract.metric_contract` or
  `contract.metric_contract_version`.
- Does not advance any seed's `status_code`.
- Does not change header `kind`.
- Does not change CR-QG-MC-001 gate count (14 stays 14).
- Does not backfill any existing MC's header.
- Does not retire `KNOWN_CONSTANTS` (TSK-1f4988).
- Does not address `co_bindings.minItems: 1` — slice (1) will
  honor it via the service's existing CC field_selection
  resolution. If `revenue_collection_rate`'s variables map to
  no CC field_selection, slice (1) will fail at
  `McOnboardingService.preview()` — that's the gate doing its
  job. The remediation question (what CC, what field_selection)
  is a slice (1) execution-time concern.

## 9. Code paths

| Layer | Path | Change |
|---|---|---|
| DTO | `mc-onboarding.service.ts` `CreateMcDto` | Add two optional fields. |
| Service | `mc-onboarding.service.ts` `preview()` / `create()` | Two `??` defaults at envelope build site(s). |
| Service | new `seed-promotion.service.ts` | New file. |
| Repo | reuse `MetricDefinitionRepository.recordFormulaVerification` | No change. |
| Controller | new `seed-promotion.controller.ts` | New file. |
| Module | `registry.module.ts` | Register new provider + controller. |
| Tests | extended + new spec files | Per §6. |

All additive. No existing path's default behavior changes.

## 10. Rollback

- TypeScript-only slice. Rollback = `git revert` on the slice
  commit. No DB state mutation.
- Existing callers of `McOnboardingService.create()` (if any
  beyond the controller) are byte-compatible — the two new
  DTO fields are optional and default to today's behavior.

## 11. Definition of done

Slice (0) is done when:

- The 4 code files (DTO + service edit + new wrapper service +
  new controller + module wire) are committed.
- All unit tests (§6.1, §6.2) pass.
- The integration test (§6.3) passes against a test DB.
- The `npx vitest run` suite is green.
- An execution-result MWR documents what was committed (commit
  SHA, tests passed, files added/modified).
- This plan's status flips `plan` → `executed`.
- Slice (1) plan is updated to reference the new wrapper and
  un-park.

## 12. After slice (0) — slice (1) un-park sequence

Once slice (0) is committed:

1. Patch slice (1) plan: remove §0 PARKED notice, rewrite §10
   code paths and §11 transactional model to call
   `POST /onboarding/seed/:id/promote`.
2. Operator approves slice (1) re-execution.
3. The candidate `revenue_collection_rate` is promoted via the
   new wrapper, in one POST call.
4. Postflight per slice (1) §12 confirms green.

## 13. Boundaries honoured

- All work in bc-core only; no bc-admin, no bc-portal, no
  bc-ai, no docs changes (beyond this plan).
- No DB schema changes. No DBCP.
- No new ADR.
- No master-shape JSON edit.
- No metric promoted. No tenant touched. No runtime
  evaluation triggered.
- Backward-compatible — existing callers continue to work
  byte-identically.

---

**End of slice (0) plan.**
