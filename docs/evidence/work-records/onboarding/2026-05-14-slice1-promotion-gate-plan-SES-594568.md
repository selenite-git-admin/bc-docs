---
title: "Slice (1) plan — Seed → Catalog promotion gate, one metric"
session: SES-594568
date: 2026-05-14
status: plan
type: slice-plan
authority: DEC-a17d0f
related:
  - 2026-05-14-pass1-calibration-q1-q4-SES-594568.md
  - 2026-05-14-slice1-preflight-result-SES-594568.md
  - 2026-05-14-session-findings-SES-594568.md
  - 2026-05-14-slice0-mc-onboarding-extension-plan-SES-594568.md
  - 2026-05-14-slice0-execution-result-SES-594568.md
  - 2026-05-14-slice0.5-execution-result-SES-594568.md
  - DEC-01df6b   # contract_json authoritative; catalog derived
  - DEC-01419c   # MC body purity, 9 keys
  - DEC-a8e8fc   # D365 — CC posting_date_field + canonical resolution stamps fiscal_period
  - DEC-4a8abb   # D329 — MC constant value propagation
  - D232         # JSON-first
revision_note: |
  Un-parked 2026-05-14 after slices (0) and (0.5) shipped.
  Slice (1) execution is now a single POST to
  `/api/onboarding/seed/:metric_definition_id/promote`, mediated
  by `SeedPromotionService` (introduced in slice 0). All raw-DB-
  write framing in §3 / §10 / §11 of the historical body is
  superseded by §0 below; the rest of the historical body is
  preserved as design context. Awaits operator approval of the
  execution payload before any DB writes.
---

## 0. Status & execution path (2026-05-14)

**Approved 2026-05-14.** Awaits operator approval of the final
execution payload (§5 below + the patched §3 in this section)
before any DB writes.

### Unblocking work that shipped

| Slice | Commit | Result MWR |
|---|---|---|
| Slice (0) — `SeedPromotionService` wrapper + β header overrides on `McOnboardingService` + DBCP `deterministic_passed` | `bc-core@17836ae` | `2026-05-14-slice0-execution-result-SES-594568.md` |
| Slice (0.5) — `McOnboardingService.preview` honors D365 / DEC-a8e8fc derived columns (`fiscal_period`, `fiscal_year`) | `bc-core@6723c62` | `2026-05-14-slice0.5-execution-result-SES-594568.md` |

After Slice (0.5), the official preview returned `valid: true`
for the `revenue_collection_rate` DTO. The gate is now
mechanically consistent across schema-provisioner, chain-status,
and MC preview.

### Execution endpoint

```
POST /api/onboarding/seed/5cb2c71c-07ac-424e-b96a-cadb7ba67748/promote
Authorization: Bearer <admin Cognito JWT>
Content-Type: application/json
```

`@PlatformOnly()`. Body matches `SeedPromotionService.PromoteSeedInput`
(see §5). The path parameter is `revenue_collection_rate`'s
`metric_definition_id`.

### What the wrapper does (mediated by SeedPromotionService)

Three logical phases. **No raw INSERT or UPDATE statements
anywhere** — the wrapper composes `MetricDefinitionRepository.createVerification`,
`McOnboardingService.create`, and a single Drizzle UPDATE on
`metric_definition`.

1. **Phase 1 — load seed.** `MetricDefinitionRepository.findById`
   then a Drizzle read of `metric_formula` (`is_current=true`)
   and its `metric_formula_variable` rows. Rejects if seed not
   found or `status_code != 'draft'`.
2. **Phase 2 — deterministic verification.** In-memory. Uses
   `evaluateFormulaDeterministic` (slice 0). Compares
   `computedOutput` to operator-provided `expectedOutput` with
   epsilon 1e-9. **Rejects with `UnprocessableEntityException`
   on any mismatch — zero writes.**
3. **Phase 3a — TX1 audit.** One row to
   `metric.metric_formula_verification` via the existing
   `MetricDefinitionRepository.createVerification` writer.
   `verdict_code = 'deterministic_passed'` (DBCP `f60523a`).
   `maker_a_output` carries the deterministic trace
   `{evidence_type, formula, values, expectedOutput, computedOutput}`.
   All AI columns (`maker_a_model`, `maker_b_model`,
   `maker_b_output`, `cross_validation`, `moderator_model`,
   `moderator_verdict`) are **NULL** — no fabricated AI agreement.
4. **Phase 3b — TX2 promotion.** Calls
   `McOnboardingService.create(dto)`. Service builds the 9-key
   body envelope (using `derivedFactColumnsForCc` per Slice 0.5),
   runs CR-QG-MC-001 (14 gates including the D365-aware
   `grain_cf_mapped` and `grain_in_cc_schema`), writes
   `contract.metric_contract` + `contract.metric_contract_version`
   atomically, calls `ContractService.activateVersion('1.0.0')`.
   Both new rows are mediated by the official service, not by
   slice (1) code.
5. **Phase 3c — TX3 seed advance.** One Drizzle UPDATE on
   `metric.metric_definition`: `status_code = 'active'`,
   `verification_result_code = 'pass'`,
   `verification_evidence_id = <verification_id>`.

If Phase 2 fails, no writes anywhere. If Phase 3a commits but
Phase 3b fails (CR-QG-MC-001 rejection), the verification row
remains as honest evidence "verification passed, gate rejected"
and Phase 3c is not attempted.

### Updated invariants (override the historical body where they conflict)

- **Verification stays outside `contract_json`**, in
  `metric.metric_formula_verification`.
- **Constants live in `contract_json.body.variables[].value`**
  via D329-R4 — populated by the service from
  `CreateMcDto.variables[].value`.
- **`header.kind = "metric"`** — hardcoded in
  `buildMetricEnvelope`. Unchanged by this slice.
- **β header path** — `purposeStatement` and `classificationTags`
  flow through the slice (0) extension to override the historical
  formulaic defaults.
- **`co_bindings` are auto-resolved** by
  `McOnboardingService.resolveCoBindings` from CC
  `field_selection`. The operator does **not** author them; the
  preview already returned 2 real bindings (`cc__receivable_hdr`,
  `cc__invoice_hdr`) for `revenue_collection_rate`. The
  historical `co_bindings: []` framing in §4.3 / §4.4 / §15 is
  superseded.
- **Exactly 4 thresholds required** per
  `validateThresholdsAndGrain`. The historical `thresholds: []`
  framing is superseded.
- **`fiscal_period` grain preview is now green** because Slice
  (0.5) made `McOnboardingService.preview` honor D365 derived
  columns — same rule schema-provisioner and chain-status apply.

### What in the historical body remains current

| Section | Status |
|---|---|
| §2 Candidate (`revenue_collection_rate`) | Current. |
| §4.1 / §4.2 / §4.5 body composition rules | Current. |
| §7 "Green demonstration" criteria | Current; the service performs the writes. |
| §8 "What the gate blocks" | Current; enforced by `McOnboardingService.preview`. |
| §13 Boundaries | Current. |
| §16 Slice-local lifecycle (direct-to-`active`) | Current; `activateVersion` does it inside the service. |
| §17 Slice-local header decision (β) | Current; implemented in Slice (0). |

| Section | Status |
|---|---|
| §3 Target state (raw INSERT description) | **Superseded** by §0 above. |
| §4.3 "Empty for this slice" for `co_bindings` | **Superseded**; service auto-resolves. |
| §4.4 "Abstract MC" framing | **Superseded**; bindings are real. |
| §6 / §6.1 capability gap discussion | **Resolved** by Slice (0) — Option 2 chosen, deterministic-only. |
| §10 Code paths (file-by-file changes) | **Superseded**; all in Slice (0). |
| §11 Transactional model | **Superseded** by the three-phase description in §0 above. |
| §12 Postflight queries | **Still useful** but reframe: the writes happen via the service, not from slice code. Queries themselves are correct. |
| §14.7–14.10 pre-flight items | **Closed** by Slice (0)/(0.5) execution result MWRs. |
| §15 "Does not bind" framing | **Superseded** by service-resolved bindings. |

Read §0 first, then §2 / §4 / §5 / §7 / §8 / §16 / §17 for the
authoritative current state. Sections marked "superseded" are
preserved for design context and audit trail.

---

**End of §0. The historical body (§1–§18) follows, preserved
for design context.**

---

# Slice (1) plan — Seed → Catalog promotion gate

Plan only. No code, no DB writes, no ADR/DBCP filed yet. Operator
approval required before execution.

Pre-flight is complete; results recorded in
`2026-05-14-slice1-preflight-result-SES-594568.md`. The plan below
incorporates pre-flight findings and the operator's review
decisions of 2026-05-14.

## 1. Goal

Wire the seed → catalog promotion gate end-to-end on **exactly one
metric**, producing — if and only if verification passes:

- one row in `contract.metric_contract` (the promoted MC parent),
- one row in `contract.metric_contract_version` with the 9-key
  `contract_json` body, `version_code='1.0.0'`,
  `governance_state_code='active'` (slice-local lifecycle
  decision — see §16),
- one row in `metric.metric_formula_verification` with
  `verdict_code='pass'` and evidence whose shape depends on the
  verification path chosen in §6 (see decision point §6.1),
- the seed row advanced: `metric_definition.status_code='draft' →
  'active'`, with `verification_result_code='pass'` and
  `verification_evidence_id` set.

After this slice: the promotion gate is real for one metric. No
broader migration, no bulk promotion, no universal-bridge work,
no `z_extension` work, no test-bench changes, no retroactive
verification fill on the 729 already-active-without-verification
MCs (tracked separately by `TSK-9ecaee`).

## 2. Candidate (locked)

**`revenue_collection_rate`** (AR sub-function, primary
composition).

- `metric_definition_id` — to be captured at execution start
  (one `SELECT` lookup), recorded in the result MWR.
- `metric_name`: `revenue_collection_rate`
- `display_name`: `Revenue Collection Rate`
- `function_code`: `finance`
- `subfunction_code`: `accounts_receivable`
- `composition_code`: `primary`
- `direction_code`: `higher_is_better`
- `formula_text`: `O1 = (I1 / I2) * C1`
- `variables` (from `metric_formula_variable`):
  - `O1` — role `output`
  - `I1` — role `input` (collected amount)
  - `I2` — role `input` (invoiced amount)
  - `C1` — role `constant` (scale factor; `constant_value=100`
    in the seed row, to be confirmed)

Why this candidate:

- Formula is non-trivial but simple — exercises the verifier's
  arithmetic and intent reasoning without becoming an
  identity-metric trivialisation (`counterparty_risk`'s `O1 = I1`
  was rejected on that basis).
- Test data is obvious: `I1=80000, I2=100000, C1=100`, expected
  `O1=80`. The number is independently checkable by reading the
  formula.
- AR subfunction is adjacent to the Phase 1 SDA work — familiar
  domain, but no functional coupling to the SDA primitives.
- Excludes the two `ML_MODEL` metrics in the candidate pool
  (engine does not support the token; their `variables` rows are
  NULL).

Backup candidate (only used if `revenue_collection_rate` fails
pre-execution sanity — see §14): `write_off_rate` (same formula
shape, also AR sub-function, `lower_is_better`).

## 3. Seed state → target catalog state

### Seed state (today, for the selected candidate)

One row in `metric.metric_definition`:

- `status_code = 'draft'`
- `formula_text` (via `metric.metric_formula`) — `O1 = (I1 / I2) * C1`
- `metric.metric_formula_variable` rows — four (O1, I1, I2, C1)
- `description_text` — natural-language intent (322 chars)
- `verification_result_code = NULL`, `verification_evidence_id = NULL`
- `category_code = NULL`, `temporality_kind = NULL`, `type_code = NULL`
  — **classification metadata is absent on the seed**; the
  promotion act authors the classification fields directly into
  the contract body (this matches the historical pattern for the
  778 already-promoted seeds; see pre-flight Finding A and the
  body inspection result that all existing active MCs carry
  fully-populated `temporal_gate` and `grain` despite seed-side
  nulls).
- No corresponding `contract.metric_contract` row.

### Target state (after slice, on `verdict_code='pass'`)

1. One row in `contract.metric_contract` referencing the seed's
   `metric_definition_id`, with `metric_contract_name='mc__revenue_collection_rate'`,
   `display_name='Revenue Collection Rate'`,
   `function_code='finance'`, `subfunction_code='accounts_receivable'`.
2. One row in `contract.metric_contract_version` with:
   - `version_code = '1.0.0'`
   - `governance_state_code = 'active'` (per §16)
   - `contract_json` — the 9-key body composed per §4.
3. One row in `metric.metric_formula_verification` with the
   dual-maker + moderator structure (§6), `verdict_code='pass'`,
   FK `metric_formula_id` pointing to the **already-existing**
   formula row on the seed.
4. Seed row updated: `status_code='active'`,
   `verification_result_code='pass'`, `verification_evidence_id`
   = the new `verification_id`.

No formula or variable creation: those rows already exist at the
seed level (pre-flight Finding A). No `metric_binding` row
(`co_bindings` is empty — slice scope).

## 4. The 9-key Metric Contract body

Live master-shape JSON (`legacy-v2/.../metric-v1.json`) and
DEC-01419c both define the 9 required body keys. They are
populated as follows:

### 4.1 Seed-derived (4 keys)

| Body key | From | Value for this candidate |
|---|---|---|
| `formula` | `metric_formula.formula_text` | `{ "text": "O1 = (I1 / I2) * C1" }` |
| `variables` | `metric_formula_variable` rows, **completed at promotion** (see §4.5) | Array of `{var_code, role, field_name, unit_type_code, sort_order, constant_value}` projected from the four seed-side rows, with operator-authored completions filling NULL `constant_value` cells where appropriate |
| `unit` | `metric_formula.unit_type_code` (output variable's unit) | To be confirmed at execution from the O1 variable's `unit_type_code` |
| `direction_code` | `metric_definition.direction_code` | `higher_is_better` |

### 4.2 Operator-authored at promotion (3 keys)

| Body key | Authored value | Notes |
|---|---|---|
| `input_type` | Operator declares — e.g. `'bf_field'`, `'canonical_field'`, or whatever value the existing 729 active MCs use for ratio metrics with no CO bindings yet. To be inspected and aligned at execution. | Must match the master-shape's permitted vocabulary for this key; one `SELECT` against existing `contract_json` bodies confirms acceptable values. |
| `temporal_gate` | `{ "field_code": "fiscal_period", "required_periods": 1, "completeness_threshold": 0.8 }` | Matches the pattern observed on existing active MCs (e.g. `mc__account_reconciliation_completion`). Operator confirms. |
| `grain` | `[{"key":"company_code","source":"business_field","field_code":"company_code"}, {"key":"fiscal_period","source":"business_field","field_code":"fiscal_period"}]` | Matches the pattern observed on existing active MCs. Operator confirms. |

### 4.3 Empty for this slice (2 keys)

| Body key | Value | Why empty |
|---|---|---|
| `co_bindings` | `[]` | Slice (1) does not bind to any CC. The promoted MC is abstract — defined but unbound. Bindings are slice (2) territory. |
| `thresholds` | `[]` | Thresholds are added later, not at gate. |

### 4.4 Constraint on this slice

`co_bindings=[]` makes the promoted MC **abstract** — it has a
formula, variables, units, temporal gate, and grain, but no CO it
can yet evaluate against. The slice's verification act proves the
formula computes the expected output on test data; it does not
prove the MC produces a snapshot. Snapshot production is a
chain-readiness concern downstream.

### 4.5 Seed thinness and promotion-time completion (operator decision, 2026-05-14)

The seed catalog is **intentionally incomplete**. Seed rows
declare the metric's structure and intent; they do not always
encode every literal value required to make the body
self-contained. The promotion act is the **formalization act**
that closes that gap — by *authoring* into the body, not by
patching the seed.

Concrete cases of seed thinness this slice handles:

- **NULL `constant_value` on a `role='constant'` variable.** The
  seed may declare a constant by `var_code`, `field_name`,
  `unit_type_code`, and `description`, while leaving
  `constant_value` NULL. The operator authors the literal value
  at promotion. The value **lands in the body's `variables[]`
  entry only** — the seed row is not modified.
- (Future slices may extend the list — e.g. NULL `field_name` on
  an input that the operator binds at promotion. Not in scope
  for slice (1).)

For `revenue_collection_rate`:

- Seed-side C1 row: `constant_value = NULL`. Confirmed at
  execution-start §14.1'.
- Operator-authored completion for the body: `C1.constant_value
  = 100`.
- This completion is written **only** into the promoted
  `contract_json.body.variables[]`. The seed
  `metric.metric_formula_variable` row for C1 remains
  `constant_value = NULL` throughout the slice.

This preserves two invariants:

- `contract_json` is the authority (DEC-01df6b). The body is
  self-sufficient for evaluation; the seed-side projection is
  not the read path.
- The seed catalog's character — declarative, incomplete by
  design — is preserved. Promotion does not "repair" the seed;
  it formalizes a contract from it.

Post-flight §12.7 explicitly verifies seed C1 remains NULL.

## 5. Promotion-act input contract

The operator (via the eventual UI / endpoint) provides at
promotion time:

| Input | Type | Purpose |
|---|---|---|
| `metricDefinitionId` | uuid | The seed to promote. |
| `inputType` | string | Body key §4.2. |
| `temporalGate` | object | Body key §4.2. |
| `grain` | array | Body key §4.2. |
| `constantCompletions` | map | Map of `var_code → constant_value` for any seed-side variable with `role='constant'` AND `constant_value IS NULL`. For this candidate: `{ "C1": 100 }`. Authored into `body.variables[]`, not into the seed. See §4.5. |
| `testData` | object | `{ "I1": 80000, "I2": 100000, "C1": 100 }` |
| `expectedOutput` | number | `80` |
| `coBindings` | array | **Must be `[]`** for this slice — explicit confirmation. |
| `thresholds` | array | **Must be `[]`** for this slice — explicit confirmation. |

Everything else (formula, variables, unit, direction_code) is
read from the seed-side rows; the operator does not re-state them.

## 6. Verification path — bc-ai capability gap

**Pre-flight finding (operator audit, 2026-05-14):** the existing
`bc-ai/app/prompts/metric-verify/v1.0/` prompts (`maker.md`,
`checker.md`, `gate.md`) are **not** a formula self-demonstration
verifier. They cover:

- Gate 1: metric classification (is this actually a measurable KPI?)
- Gate 2: semantic dedup (does it duplicate an existing metric?)
- Gate 3: function / subfunction validation
- Gate 4: name canonicalization

Input: `metric_name, display_name, description, function_code,
subfunction_code, [reference_formula], [existing_metrics]`.
Output: classification verdict, dedup verdict, function
validation, canonicalized name. The checker reviews the maker's
4-gate assessment — it is **not** a second independent formula
verifier.

**Neither prompt:**

- accepts `testData` / `expectedOutput`,
- computes the formula's actual output,
- compares actual vs expected,
- validates a 9-key Metric Contract body,
- produces cross-family formula self-demonstration evidence.

The earlier plan revision's assertion ("bc-ai-side: no change
required") was incorrect. `metric-verify/v1.0` is suitable for
*seed registration quality* gates, not for the *promotion-time
formula demonstration* this slice needs.

### 6.1 Decision point (operator)

Two paths forward. The slice cannot proceed until one is chosen.

#### Option 1 — Build `formula-verify/v1.0` for this slice

Create a new bc-ai pipeline, parallel to `metric-verify/v1.0`,
purpose-built for cross-family formula self-demonstration:

- New prompts: `bc-ai/app/prompts/formula-verify/v1.0/maker.md`,
  `checker.md`, optionally `gate.md` and a moderator prompt.
- Maker accepts: `formula_text`, `variables`,
  `test_inputs`, `expected_output`. Maker computes the formula
  symbolically, evaluates against `test_inputs`, returns
  `{actual, verdict, reasoning}`.
- Checker independently re-computes against the same inputs.
  Returns `{agreement, divergence, verdict, reasoning}`.
- Moderator only invoked on divergence; returns
  `{verdict: pass|fail|escalate, rationale}`.
- New bc-ai FastAPI endpoint:
  `POST /api/ai/suggest/formula-verify`.
- New bc-core client method:
  `BcAiClient.invokeFormulaVerifier(body)`.

Verification row on pass would carry:

```
maker_a_model    = "claude-haiku-4-5-20251001"
maker_a_output   = {inputs, expected, actual, verdict, reasoning}
maker_b_model    = "claude-sonnet-4-5-20250929"
maker_b_output   = {inputs, expected, actual, verdict, reasoning}
cross_validation = {agreement: true|false, divergence: ...}
moderator_model  = "claude-haiku-4-5-20251001"  (if invoked)
moderator_verdict= {verdict, rationale}          (if invoked)
verdict_code     = "pass"
```

This honors the calibration MWR's Q4 close ("cross-family AI
verification runs once") and produces **Cross-family-passed**
evidence per `docs/ai/ai-trust-and-verification.md`.

**Cost of Option 1:** slice scope grows to include the new prompt
authoring, prompt review, bc-ai endpoint, bc-core client method,
and an integration test on one metric. Roughly doubles the
slice's surface.

#### Option 2 — Deterministic-only for this slice; defer cross-family AI

Scope slice (1) to the deterministic floor:

- Parse the formula (`O1 = (I1/I2)*C1`).
- Substitute `testData` (I1=80000, I2=100000, C1=100).
- Compute the actual output.
- Compare to `expectedOutput=80`. If equal, verdict `pass`.

Verification row on pass:

```
maker_a_model    = NULL
maker_a_output   = {inputs, expected, actual, verdict: "pass",
                    evidence_type: "deterministic_formula_eval"}
maker_b_model    = NULL
maker_b_output   = NULL
cross_validation = NULL
moderator_model  = NULL
moderator_verdict= NULL
verdict_code     = "pass"
```

`maker_a_output` carries the deterministic computation trace.
The maker/checker/moderator slots stay NULL — the verification
row table accepts this shape (those columns are nullable).

Trust posture: **Deterministic-passed** per the trust ladder.
Lower than cross-family-passed but still a real verdict.

Cross-family AI verification is then a follow-up slice (call it
slice (1.x) or fold into slice (1.b) for stuck-mid-promotion).
A separate prompt/endpoint is built when that slice runs.

**Cost of Option 2:** slice stays tight; calibration MWR Q4
close softens from "cross-family runs once" to "verification
runs once; cross-family path is real but built in a follow-up
slice."

#### What I cannot do

I cannot pick this for you. Either option is defensible:

- Option 1 honors the cross-family commitment cleanly but
  expands the slice.
- Option 2 ships smaller now and defers the AI commitment.

Note: even if Option 2 is chosen, the existing
`metric-verify/v1.0` prompts remain useful for a **separate**
seed-registration-quality gate (a different concern), and
should not be deprecated by this slice.

## 7. "Green demonstration"

The slice is green if **all** of the following hold post-execution:

1. The selected seed row advances: `status_code='active'`,
   `verification_result_code='pass'`,
   `verification_evidence_id` is non-null and references the new
   verification row.
2. Exactly one new row in `contract.metric_contract` with
   `metric_definition_id` = the seed UID.
3. Exactly one new row in `contract.metric_contract_version` with
   that contract's id, `version_code='1.0.0'`,
   `governance_state_code='active'`, and `contract_json.body`
   carrying all 9 required keys.
4. `contract_json.body.formula.text` equals the seed-side
   `metric_formula.formula_text`.
5. `contract_json.body.variables` length equals the count of
   `metric_formula_variable` rows for the seed's current formula.
6. Exactly one new row in `metric.metric_formula_verification`
   with `verdict_code='pass'`, FK to the seed's existing
   `metric_formula_id`.
7. No row outside this selected-seed → MC chain changes (i.e.
   the 1,215 other draft seeds, 778 existing contracts, 1,020
   existing contract_version rows, and 3 historical verification
   rows are byte-identical pre- and post-).
8. The Metric Evaluator's read path (code-level inspection, not
   execution) confirms it reads `contract_json` for this MC, not
   any catalog-table projection — DEC-01df6b conformance check
   for this metric.

## 8. What the gate blocks

The gate **rejects promotion** and writes **no rows at all** if:

- Formula does not parse (or parses to a structure inconsistent
  with declared variables).
- Test data is missing, malformed, or `expectedOutput` is not a
  finite number.
- Operator-authored body keys (`input_type`, `temporal_gate`,
  `grain`) are missing, malformed, or fail master-shape
  validation.
- `coBindings` or `thresholds` is not `[]` on input (the slice
  enforces emptiness explicitly).
- Cross-family verification returns `verdict_code` ≠ `'pass'`
  (i.e. `'fail'` or `'escalate'`).
- The deterministic formula computation against `testData`
  yields a value ≠ `expectedOutput`.

On rejection: **no `metric_contract` row, no `metric_contract_version`
row, no `metric_formula_verification` row, no seed status
update.** The seed stays in `draft` exactly as it was.

This is a deliberate slice-local choice. The SDA-4 pattern emits
a ledger row even on failed acts (Invariant VI — evidence is
emitted), but the verification ledger today is keyed by an
already-existing `metric_formula_id` so the row would suggest the
verifier "ran against a promoted MC" — which on rejection is not
true. Inventing a seed-anchored failed-verification table is out
of scope for this slice (operator decision, 2026-05-14). If a
future slice adds a seed-anchored audit table, failed-verification
evidence can be filled retroactively; this slice does not create
it.

## 9. DB changes required before code

**None.** Pre-flight confirmed:

- `metric_definition.status_code` CHECK already permits `active`
  (no DBCP).
- `metric_contract_version.governance_state_code` CHECK permits
  `active` directly (see §16).
- All target tables and columns exist.

## 10. Code paths that will change

| Layer | Path | Change |
|---|---|---|
| Service | `bc-core/src/registry/metric-definition.service.ts` (or a new `metric-contract-promotion.service.ts`) | Add `promoteDefinition(metricDefinitionId, input)` orchestrating verification + atomic write per §11. |
| Service | bc-core | Add `buildContractBodyFromInput(seedRows, operatorInput)` — pure projection that composes the 9-key body. Pure function; testable in isolation. |
| Client | bc-core `BcAiClient` | **If §6.1 Option 1:** new `invokeFormulaVerifier(body)` client method calling `POST /api/ai/suggest/formula-verify`. **If §6.1 Option 2:** no bc-ai client invocation; deterministic compute happens in bc-core only. The existing `invokeMetricVerifier` is **not** used by this slice — it covers seed registration quality, not formula self-demonstration. |
| Service / pure | bc-core | A pure formula evaluator: parse `formula_text` to AST, substitute variable values, compute output. Used by both options (Option 2 as the sole verifier; Option 1 alongside the AI verdict as the deterministic cross-check). |
| bc-ai | `bc-ai/app/prompts/formula-verify/v1.0/` | **Only if §6.1 Option 1.** New maker.md, checker.md, optional gate.md / moderator. New FastAPI endpoint `POST /api/ai/suggest/formula-verify` registered in `main.py`. New agent class in `app/agents/`. |
| Repository | bc-core | New inserts on `contract.metric_contract` + `contract.metric_contract_version` (used in atomic block). |
| Repository | `MetricDefinitionRepository.recordFormulaVerification` (existing, line 606) | Used as-is on pass; not called on rejection. |
| Repository | bc-core | New `updateDefinitionStatus(metricDefinitionId, {statusCode, verificationResultCode, verificationEvidenceId})` for the seed-status advance. |
| Controller | bc-core platform endpoint | Add `POST /metric-definitions/:id/promote` — `@PlatformOnly()`, body matches §5. |
| Spec | bc-core test files | One end-to-end Vitest spec exercising pass and rejection paths against a test DB. |

All changes additive — no existing path removed or modified
beyond what is strictly necessary. The existing 729 active MCs
are not touched.

bc-ai-side: change is **conditional on §6.1**. If Option 1,
new prompts + endpoint + agent are added. If Option 2, no
bc-ai change.

## 11. Transactional model

### Single atomic transaction

The act is **one DB transaction**. All-or-nothing.

On `verdict_code='pass'` from the cross-family verifier, the
transaction writes (in order):

1. `contract.metric_contract` (1 row)
2. `contract.metric_contract_version` (1 row, with `contract_json`)
3. `metric.metric_formula_verification` (1 row, with verdict)
4. `metric.metric_definition` UPDATE (status_code='active',
   verification_result_code='pass', verification_evidence_id)

If verifier verdict is `fail` or `escalate`, the transaction
**does not begin** — no rows are written anywhere (§8 above). The
verification step runs **before** the transaction opens; only its
result determines whether to enter the transaction at all.

This resolves the earlier contradiction. The single-transaction
model is supported because:

- The verifier is called synchronously, outside any DB
  transaction.
- Its result is held in application memory.
- Only on `pass` does the transaction open and commit the four
  writes atomically.
- On non-pass, the verifier's output is **discarded** for this
  slice (operator decision, 2026-05-14).

### Rollback

- If the transaction commits and the operator decides to undo: a
  follow-up decommissioning act sets `archived_at` on the
  `metric_contract` row, reverts the seed `status_code` to
  `draft`, and leaves the verification row in place (Invariant
  III — the ledger row records the act that happened).
- Rollback is **operator-explicit**, not automatic. No automatic
  retry, no automatic decommission on downstream failure.

## 12. Postflight checks

Read-only, run by the operator after the act, with
`$1 = metric_definition_id` of the candidate:

```sql
-- 12.1 Exactly one new MC for the selected seed
SELECT COUNT(*) FROM contract.metric_contract WHERE metric_definition_id=$1; -- 1

-- 12.2 Body has all 9 master-shape keys
SELECT (mcv.contract_json -> 'body') ?& ARRAY[
  'input_type','formula','variables','co_bindings',
  'temporal_gate','unit','direction_code','thresholds','grain'
] AS body_has_all_9_keys
FROM contract.metric_contract_version mcv
JOIN contract.metric_contract mc ON mc.metric_contract_id = mcv.metric_contract_id
WHERE mc.metric_definition_id=$1 AND mcv.version_code='1.0.0'; -- true

-- 12.3 body.formula.text matches seed-side formula_text
SELECT (mcv.contract_json -> 'body' -> 'formula' ->> 'text') =
       (SELECT mf.formula_text FROM metric.metric_formula mf
        WHERE mf.metric_definition_id = mc.metric_definition_id
          AND mf.is_current=true) AS formula_matches
FROM contract.metric_contract_version mcv
JOIN contract.metric_contract mc ON mc.metric_contract_id = mcv.metric_contract_id
WHERE mc.metric_definition_id=$1; -- true

-- 12.4 Exactly one passing verification row keyed by seed's existing formula
SELECT COUNT(*) FROM metric.metric_formula_verification v
JOIN metric.metric_formula f ON f.metric_formula_id = v.metric_formula_id
WHERE f.metric_definition_id=$1 AND v.verdict_code='pass'; -- 1

-- 12.5 Seed status advanced
SELECT status_code, verification_result_code,
       verification_evidence_id IS NOT NULL AS has_evidence
FROM metric.metric_definition WHERE metric_definition_id=$1;
-- expect ('active', 'pass', true)

-- 12.6 No unrelated row changed in the window
SELECT COUNT(*) FROM contract.metric_contract
WHERE updated_at > $slice_start_ts AND metric_definition_id <> $1; -- 0
SELECT COUNT(*) FROM contract.metric_contract_version
WHERE created_at > $slice_start_ts
  AND metric_contract_id NOT IN (SELECT metric_contract_id FROM contract.metric_contract WHERE metric_definition_id=$1); -- 0
SELECT COUNT(*) FROM metric.metric_definition
WHERE updated_at > $slice_start_ts AND metric_definition_id <> $1; -- 0

-- 12.7 Seed C1 remains NULL — promotion authored the constant
-- only into the body, did not touch the seed (per §4.5)
SELECT mfv.var_code, mfv.constant_value
FROM metric.metric_formula_variable mfv
JOIN metric.metric_formula mf ON mf.metric_formula_id = mfv.metric_formula_id
WHERE mf.metric_definition_id=$1 AND mf.is_current=true AND mfv.role='constant';
-- expect: C1, NULL  (unchanged from pre-flight)

-- 12.8 Body's C1 carries the authored constant_value=100
SELECT v->>'var_code' AS var_code, v->>'constant_value' AS constant_value
FROM contract.metric_contract_version mcv,
     jsonb_array_elements(mcv.contract_json -> 'body' -> 'variables') v
JOIN contract.metric_contract mc ON mc.metric_contract_id = mcv.metric_contract_id
WHERE mc.metric_definition_id=$1 AND v->>'role'='constant';
-- expect: ('C1','100')

-- 12.9 Verification evidence carries the deterministic trace
SELECT v.verdict_code,
       v.maker_a_model IS NULL AS maker_a_null,
       v.maker_b_model IS NULL AS maker_b_null,
       v.cross_validation IS NULL AS xv_null,
       v.moderator_model IS NULL AS mod_null,
       v.maker_a_output -> 'testData' ->> 'C1' AS testdata_c1,
       v.maker_a_output ->> 'expectedOutput' AS expected,
       v.maker_a_output ->> 'computedOutput' AS computed,
       v.maker_a_output ->> 'evidence_type' AS evidence_type
FROM metric.metric_formula_verification v
JOIN metric.metric_formula f ON f.metric_formula_id = v.metric_formula_id
WHERE f.metric_definition_id=$1;
-- expect: ('deterministic_passed', true, true, true, true, '100', '80', '80', 'deterministic_formula_eval')

-- 12.10 Evaluator authority check (code-level, not DB):
-- inspect MetricEvaluator's read path; confirm it loads contract_json
-- and does not fall back to catalog-table projections.
```

## 13. Boundaries honoured

- One metric only. The 1,215 other draft seeds untouched.
- No code change before this plan is approved.
- No DBCP — pre-flight confirmed no schema change needed.
- No new ADR.
- No metric repair writes. No tenant / runtime touches.
- No bc-ai change required.
- No `metric_formula_verification` backfill for the existing 3
  rows or the 726 zero-row active MCs (tracked separately by
  `TSK-9ecaee`).
- No mass status migration. Only the one seed advances.

## 14. Pre-flight resolutions (closed)

The ten §14 questions from the earlier plan revision are resolved
in `2026-05-14-slice1-preflight-result-SES-594568.md`. Summary:

- All target tables / columns exist; no DB schema change.
- bc-ai endpoint and bc-core client both exist.
- Cross-family models configured (Haiku 4.5 + Sonnet 4.5).
- Master-shape JSON is current; DEC-01419c not superseded.
- Formulas already exist at seed level; promotion is wrapping +
  body construction + verification, not formula creation.

Remaining factual confirmations to do at execution start (before
opening the transaction):

| # | Confirm | How |
|---|---|---|
| 14.1' | Capture the actual `metric_definition_id` for `revenue_collection_rate` | `SELECT metric_definition_id FROM metric.metric_definition WHERE metric_name='revenue_collection_rate' AND status_code='draft'` |
| 14.2' | Capture the four `metric_formula_variable` rows (O1, I1, I2, C1) — verify `constant_value=100` on C1, `unit_type_code` on each | `SELECT * FROM metric.metric_formula_variable mfv JOIN metric.metric_formula mf ON mf.metric_formula_id = mfv.metric_formula_id WHERE mf.metric_definition_id = $1 AND mf.is_current=true ORDER BY mfv.sort_order` |
| 14.3' | Inspect an existing active MC's `contract_json.body.input_type` value to align this slice's authored value with the established pattern | One `SELECT` on `contract.metric_contract_version` filtered to an AR-rate-like MC |
| 14.4' | **Resolved 2026-05-14:** `bc-ai/app/prompts/metric-verify/v1.0/` is **not** a formula self-demonstration verifier (it covers seed registration quality — classification, dedup, function validation, name canonicalization). See §6.1 decision point. | Operator audit + Claude re-read |
| 14.5' | **Resolved 2026-05-14 (Slice 0.5):** `McOnboardingService.preview` now honors D365 / DEC-a8e8fc derived columns. The `fiscal_period` grain question that surfaced as a preview-red is gate-consistency, not a structural CC-side gap. The two bound CCs (`cc__receivable_hdr`, `cc__invoice_hdr`) declare `posting_date_field`. Re-run preview returned `valid: true` (zero failed checks). | Slice 0.5 execution-result MWR |

None of 14.1'–14.4' requires a write.

## 15. What this slice does NOT do

To make the boundary unambiguous:

- Does not author any CF, BF, BO, SC, OC, AC, CC, or IC.
- Does not bind the promoted MC to any tenant.
- Does not produce a metric snapshot.
- Does not run the metric evaluator end-to-end.
- Does not change the existing 729 active MCs in any way.
- Does not backfill verification for the existing 3 rows or the
  726 zero-row active MCs (tracked by `TSK-9ecaee`).
- Does not introduce the universal-bridge inventory (slice (2)).
- Does not introduce `z_extension` admission rejection (slice
  (3)).
- Does not write a failed-verification audit row (§8 above).
- Does not redesign the contract lifecycle generally (§16 below).

## 16. Slice-local lifecycle decision (deliberate)

The five-state Foundation lifecycle is `draft → review →
approved → active → superseded` per
`the-contract-grammar.md`. Live data shows the system has never
used `review` or `approved` (0 rows in either state across 1,020
contract versions); existing versions move directly from `draft`
to `active`, or land in `active` on insert.

This slice writes the version row directly to
`governance_state_code='active'` after verification passes. The
deliberate substitution is:

- **`review` was supposed to mean** "authoring complete and under
  review."
- **`approved` was supposed to mean** "review complete but not
  yet active."
- **In this slice, both are subsumed by the verification act**:
  the cross-family AI verdict + the test-data formula check are
  the review evidence. The verification row in
  `metric_formula_verification` is the audit trail of that
  review.

This is a **slice-local implementation choice**, not a universal
lifecycle redesign:

- No ADR filed. The Foundation lifecycle text remains as
  documented.
- A future ADR may amend the lifecycle, formally subsume `review`
  and `approved` under the verification act, or split them back
  out — outside this slice's scope.
- Other slices and future promotion paths may make different
  choices. This slice records what it did and why.

## 17. Slice-local header decision — Foundation strict (β)

Operator decision 2026-05-14: this slice authors the header per
Foundation §Common Header semantics, **not** the live-data
pattern observed on the 540 existing active MCs.

### What this means concretely

| Header key | Live-MC pattern (drift) | This slice (β — Foundation strict) |
|---|---|---|
| `tags` | Variable codes, e.g. `["O1","I1","I2","C1"]` | Real classification slugs, e.g. `["finance","accounts_receivable","collection","percentage"]` |
| `description` | Formulaic placeholder, e.g. `"Metric contract: O1 = (I1 / I2) * C1"` | The seed's `description_text` used as a contract purpose statement |

The variable codes (`O1`, `I1`, `I2`, `C1`) remain in
`body.variables[]` — they belong there, not in `tags`. The
formula remains in `body.formula.text` — it belongs there, not
in `description`.

### Scope of this decision

- **Slice-local precedent.** This is the first new promoted MC
  after the divergence was surfaced
  (`2026-05-14-session-findings-SES-594568.md` §4). Future
  promotions should follow the same Foundation-strict header
  unless explicitly amended.
- **No broad remediation of the 540 existing-drift MCs in this
  slice.** They keep their drifted header values. Backfill is a
  separate slice if and when chosen.
- **Recorded as a deliberate, justified divergence from
  precedent**, not as a one-off variation. Future sessions
  reading the active catalog will find one MC whose header
  matches Foundation and 540 that don't; this MWR + the session
  findings MWR explain why.

### Cross-referenced

- Foundation: `bc-docs-v3/docs/foundation/the-contract-grammar.md`
  §Common Header (16 required keys, sub-shape definitions).
- Session findings MWR: `2026-05-14-session-findings-SES-594568.md`
  §4 (the divergence and the two paths).

## 18. Definition of done for this plan

This plan is "done" when:

- Operator confirms decisions 1–6 (already recorded as patched
  in this revision):
  1. Body-authoring step required (§4.2).
  2. Candidate locked to `revenue_collection_rate` (§2).
  3. Lifecycle: version row written directly to `active` (§16).
  4. Schema names use live form (`metric.metric_formula`,
     `metric.metric_formula_variable`, `metric.metric_binding`;
     `contract.metric_contract`, `contract.metric_contract_version`).
  5. Body keys unified to live master-shape (§4).
  6. Failed verification writes nothing (§8, §11).
- Decision 7 — §6.1 verification path: **Option 2 (approved
  2026-05-14)**. Deterministic-only verifier in bc-core.
  Deterministic-passed evidence. Cross-family AI deferred to a
  follow-up slice. Implemented in Slice (0).
- Decision 8 — §17 header path: **(β) Foundation-strict
  (approved 2026-05-14)**. Implemented in Slice (0).
- **Decision 9 — execution path (un-park 2026-05-14):** call
  `POST /api/onboarding/seed/:metric_definition_id/promote` per
  §0. No raw DB writes. Wrapper service mediates.
- Operator approves the final execution payload (see §5 +
  surfaced via the runner before any POST), then says "execute"
  to begin DB writes.

### Execution gate before any POST

The operator-facing checkpoint right before the act:

1. The exact `PromoteSeedInput` body is rendered to the operator.
2. Operator confirms the four operator-authored elements:
   - `purposeStatement` matches §17 / β intent.
   - `classificationTags` matches §17 / β intent.
   - `thresholds` has exactly 4 bands.
   - `testData` + `expectedOutput` deterministic pair is
     correct (e.g. `(80000 / 100000) * 100 = 80`).
3. On "execute", one POST is made; postflight queries (§12) run;
   execution-result MWR is written.

Execution does not begin until the plan is approved.

---

**End of plan.**
