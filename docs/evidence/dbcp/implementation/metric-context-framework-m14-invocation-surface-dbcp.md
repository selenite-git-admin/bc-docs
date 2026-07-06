---
uid: metric-context-framework-m14-invocation-surface-dbcp
title: MCF M14 Invocation Surface DBCP
description: Design blueprint for the minimal HTTP/controller surface that wraps McfCertWriterService.activateMetric — the MCF gate that transitions an MCV from approved → active. Locks the MCV-scoped route, the literal mcf_publisher auth policy (super_admin wildcard NOT sufficient on this endpoint), the request body shape (rationaleText ≥ 40 chars; idempotencyKey optional; no dryRun in v1), the 10-step handler flow, the PE-MC fetch + aggregation gate, the M14_VERIFIER_VERSION = mcf-m14-v1 substrate constant, the idempotency-key construction, the expected writes, the 8 tests, and the file list for the bc-core implementation PR. DBCP-only. No bc-core code change. No DB mutation. No DDL apply. No M14 invocation. No legacy writes. No Cognito changes. The implementation PR is a separately operator-authorized follow-up.
status: proposed
date: 2026-06-02
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m14-invocation-surface-dbcp
---

# MCF M14 Invocation Surface DBCP

## 0. Scope and discipline

DBCP-only design pass. No bc-core implementation, no DDL apply, no DB write, no M14 invocation, no legacy writes, no Cognito changes. `bc-postgres` MCP `allow_write=false` throughout. The implementation PR (bc-core) is separately operator-authorized.

**Baseline at DBCP-author time:**
- `bc-core` main = `1931521a7cd9f1d54b06bd33c070c32485933f6d` (PR #208 — M13 evaluator version bump v1 → v2)
- `bc-docs-v3` main = `fbd3386` (PR #47 — D-M13-9 version-bump policy)
- M13 first real run on MCV `8c088f55-…` succeeded under `mcf-m13-v2`: MCV `review → approved`; all 6 parent MC hash columns stamped; 10 M13 v2 PE rows persisted; 10 prior v1 rows preserved per Invariant V. M14 is technically eligible — but **NOT yet invocable** (no HTTP surface).

This DBCP closes that gap with the minimum surface area.

## 1. Authority

- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF Build Plan
- ADR: `bc-docs-v3/docs/adrs/ADR-3f093f.md` (DEC-3f093f / D426) — MCF Canonicality and Legacy Runtime Boundary
- M13 PE-MC evaluator DBCP: `metric-context-framework-m13-pe-mc-evaluator-dbcp.md` — defines the PE-MC rows this controller consumes; D-M13-9 version-bump policy is the symmetric precedent for `M14_VERIFIER_VERSION`
- M4 cert writer DBCP: `metric-context-framework-m4-lifecycle-certification-dbcp.md` — defines `activateMetric` (approved → active; one `metric_transition` cert; M3 trigger demotes prior `is_current=TRUE` sibling)
- M14 governance DBCP: `metric-context-framework-m14-m12-governance-dbcp.md` — defines the governance-side unblock; this DBCP defines the runtime invocation surface (orthogonal axes)
- bc-core PR #207 / DEC-3f093f / D426 — PE-MC-1 + PE-MC-6 substrate-authority alignment
- bc-core PR #208 — M13 evaluator version bump `mcf-m13-v1` → `mcf-m13-v2`

## 2. Decisions

| ID | Question | Decision | Alternatives rejected |
|---|---|---|---|
| **D-M14-IS-1** | Route shape | **`POST /api/mcf/metric-contract-versions/:mcvUid/activate`** — MCV-scoped. | MC-scoped (`metric-contracts/:mcUid/activate` with internal MCV resolution) — rejected; introduces controller ambiguity about which version is activatable; doesn't lock the operator's intent in the URL. |
| **D-M14-IS-2** | Auth | `@Roles('mcf_publisher')` decorator **AND** in-handler literal precheck (`user.roles.includes('mcf_publisher')` — 403 if absent). `super_admin` wildcard via `RolesGuard` line 35 does NOT satisfy this endpoint's auth. | (a) Decorator only — rejected; the shared `RolesGuard` wildcard would let `super_admin` activate metrics without explicit publisher authorization. (b) Modifying `RolesGuard` to a global "no-wildcard" mode — rejected; too wide a blast radius for the M14 surface PR. A future ADR can introduce a `@LiteralRolesOnly()` decorator for "high-stakes endpoints"; this DBCP records the policy inline (§5) so a future ADR has a precedent. |
| **D-M14-IS-3** | Request body | `{ rationaleText: string, idempotencyKey?: string }`. No `dryRun` in v1. | dryRun in v1 — deferred (§13). Body field aliases / additional fields — rejected; minimal surface principle. |
| **D-M14-IS-4** | PE-MC supply pattern | Controller **fetches** the 10 PE rows itself from substrate. Caller MUST NOT supply them in the request. | Caller-supplied PE rows — rejected; trust boundary violation (PE rows are M13 evaluation evidence; the operator's role is to authorize activation, not to compose evidence). |
| **D-M14-IS-5** | PE-row aggregation gate | Read latest 10 PE rows for the MCV under `verifier_version = M13_EVALUATOR_VERSION` (= `mcf-m13-v2` today). Require exactly 10 rows; require each row's `evidence_json.current_package_signature_hash` to equal MC's stamped `package_signature_hash`; require PE-MC-1, 2, 3, 4, 5, 6, 7, 9, 10 all `PASS`; require PE-MC-8 to be either `PASS` or `OPERATOR_REVIEW` with `mode='default-pass-pending-m18+'`. | Trust M13's aggregation in-line via `evaluation_signature_hash` lookup — rejected; the activation gate must be substrate-derivable from current PE row state, not from a derived hash. |
| **D-M14-IS-6** | M14 PE-row substrate-side dedup | Introduce `export const M14_VERIFIER_VERSION = 'mcf-m14-v1' as const;` in bc-core. M14's PE row writes carry `verifier_version='mcf-m14-v1'`, distinct from M13's `mcf-m13-v2`. Index `idx_mcf_mper_mcv_check_eval_pkg` keys on column → v1/v2/m14-v1 coexist freely for the same `(mcv, pe_check_code)`. **Symmetric to D-M13-9 version-bump policy:** any future M14 semantic change MUST bump `M14_VERIFIER_VERSION`. | (a) Reuse `mcf-m13-v2` — rejected; partial unique index would reject the M14 INSERT (same 4-tuple as M13's pre-approve rows). (b) `verifier_version=NULL` — rejected; bypasses the partial index (the `WHERE verifier_version IS NOT NULL` clause), losing substrate-side guard against concurrent-retry duplicates of M14 rows; also semantically conflates M14 rows with pre-M13 NULL-verifier rows from M4 spec tests. |
| **D-M14-IS-7** | Idempotency-key construction | Controller composes the default: `mcf-m14-activate/<mcvUid>/<currentPackageSignatureHash>/<m13EvaluationSignatureHash>` when the request omits `idempotencyKey`. Operator-supplied `idempotencyKey` overrides the default. Length-bounded, JCS-safe. | Service-generated only — rejected; the operator needs the ability to override (e.g., to retry a stuck-pending claim with a distinct key). No-default — rejected; would make the happy path require operator-supplied keys for every invocation. |
| **D-M14-IS-8** | Expected writes — substrate only | M4's existing `activateMetricInTx` deltas are the complete write surface: 1 `mcf.certification_record`; 10 `mcf.metric_publication_eligibility_result` (linked to the cert); 1 `mcf.metric_contract_version` UPDATE (`approved → active`); 0..1 UPDATE on prior `is_current=TRUE` sibling via the M3 trigger. **Zero writes to `metric.*` or `contract.*` legacy tables (D426 / HA-1).** | Writing a compatibility projection row in `metric.metric_definition` at activation time — rejected per D426 §5 ("no compatibility projection before M14 active-state proof for at least one metric"). The proof from this DBCP's first run becomes the authority for a separate projection ADR if/when one is filed. |
| **D-M14-IS-9** | Tests | 8 tests (§10). MCV-fidelity test is new and locks the URL-vs-substrate binding in both directions. Tests 7 + 8 are integration (`BCCORE_INTEGRATION_DB=1` gated, SAVEPOINT-rolled-back pattern); the rest are unit. | Skipping integration spec — rejected; the legacy zero-delta and MCV-fidelity assertions are integration-only assertions that the unit-test layer's mocks cannot prove. |
| **D-M14-IS-10** | Single-controller vs split | New controller `McfPublicationActivationController` at base `mcf/metric-contract-versions`. Single endpoint. **Not** added to `McfPublicationEligibilityController` (which is at `mcf/metric-contracts` and is M13-scoped). | Reuse `McfPublicationEligibilityController` — rejected; route base path differs (`mcf/metric-contract-versions` vs `mcf/metric-contracts`); semantic responsibility differs (M13 evaluation vs M14 activation); collapsing them inflates the M13 controller's surface across two MCF gates. |

## 3. Route

```
POST /api/mcf/metric-contract-versions/:mcvUid/activate
```

Decorators (production order):

```
@ApiTags('MCF / M14 Publication Activation')
@PlatformOnly()
@Controller('mcf/metric-contract-versions')
class McfPublicationActivationController {
  @Post(':mcvUid/activate')
  @Roles('mcf_publisher')
  @HttpCode(201)
  async activate(@Param('mcvUid') mcvUid: string, @Body() body: ActivateRequestBody, @CurrentUser() user: AuthUser) { ... }
}
```

`mcvUid` is the substrate identity that gets mutated. The path param **IS** the activation target; the controller MUST NOT infer or resolve a different MCV from any other input.

## 4. Request and response shape

**Request body (v1):**

```jsonc
{
  "rationaleText":  "string — required; ≥ 40 chars (M4 RATIONALE_MIN_CHARS); operator-meaningful audit justification",
  "idempotencyKey": "string — optional; controller composes a default if absent (see D-M14-IS-7)"
}
```

**Response body (201):** the literal `ActivateMetricResult` returned by `McfCertWriterService.activateMetric` (see `mcf-cert-writer.service.ts:279`):

```ts
{
  metricContractVersionUid: string,
  newStateCode: 'active',
  certificationRecordId: string,
  peResultUids: string[],          // 10 UIDs, in PE_MC_CODES order
  isCurrentDemoted: string | null, // prior is_current=TRUE sibling, or null on first activation
  committed: boolean
}
```

**Error responses (Problem+JSON envelope):**
- `400 Bad Request` — body validation failure (e.g., rationale too short, missing field).
- `403 Forbidden` — JWT lacks literal `mcf_publisher` (even with `super_admin`).
- `404 Not Found` — MCV `mcvUid` does not exist in `mcf.metric_contract_version`.
- `409 Conflict` — MCV not in `approved` state; missing/incomplete/non-PASS PE evidence; stale PE evidence (package hash drift); parent MC hashes not yet stamped (defensive — should not occur post-M13).
- `500 Internal Server Error` — uncaught M4 error.

## 5. Auth (D-M14-IS-2)

Literal `mcf_publisher` enforcement at TWO layers:

1. **Decorator layer:** `@Roles('mcf_publisher')` on the handler. This is the dev-time intent declaration. Today, the shared `RolesGuard` (`src/auth/guards/roles.guard.ts:35`) treats `super_admin` and `admin` as wildcards that bypass the `@Roles()` check.

2. **In-handler precheck:** as the FIRST statement of the handler body, **before any substrate read**:

   ```ts
   if (!user.roles.includes('mcf_publisher')) {
     throw new ForbiddenException('mcf_publisher role required for metric activation');
   }
   ```

   This makes the literal-role requirement an explicit runtime invariant, independent of `RolesGuard` configuration. If a future hardening removes the wildcard, this check becomes redundant but harmless.

**Policy (recorded inline; not yet promoted to platform-wide ADR — see §13):** activation-class MCF endpoints require a literal authorization role; the shared `RolesGuard` wildcard does NOT apply to this endpoint. If the implementation review proves the policy needs broader platform treatment, a standalone ADR can be carved out separately.

A unit test (Test 2 in §10) asserts that a JWT carrying `super_admin` but NOT `mcf_publisher` receives a 403. An HA-style source-guard test asserts the in-handler precheck literal text is present in the controller source.

## 6. Handler flow (10 steps)

The handler MUST execute these steps in order. Each step is checkpointed; failures throw the listed exception immediately.

```
1.  Literal-role precheck (§5).
    user.roles.includes('mcf_publisher') → else ForbiddenException (403).

2.  Body validation.
    rationaleText.length ≥ 40 → else BadRequestException (400).
    No other body fields permitted (extra fields ignored or rejected per
    existing platform validation pipe convention).

3.  Read MCV row (FOR UPDATE locked inside the M4 outer tx is preferred;
    pre-tx read at controller layer is acceptable since M4 re-locks).
    MCV exists → else NotFoundException (404).
    MCV.governance_state_code === 'approved' → else ConflictException (409,
    reason: "mcv state is X; activation requires approved").

4.  Read parent MC stamped package_signature_hash + 5 other hash columns.
    All 6 columns non-NULL → else ConflictException (409, reason: "parent mc
    hashes not stamped; M13 evaluation has not yet approved this mcv").

5.  Read latest 10 PE rows for the MCV:
      verifier_version = M13_EVALUATOR_VERSION (= 'mcf-m13-v2' at DBCP time)
      ORDER BY evaluated_at DESC
      Deduplicate by pe_check_code (first occurrence wins).
    Exactly 10 rows present (one per PE_MC_CODES) → else 409.

6.  Aggregation gate (D-M14-IS-5):
    For each row:
      a. evidence_json.current_package_signature_hash === MC.package_signature_hash
         → else 409 (reason: "stale PE evidence: substrate has drifted").
    For verdicts:
      a. PE-MC-1, 2, 3, 4, 5, 6, 7, 9, 10 all === 'PASS' → else 409.
      b. PE-MC-8 ∈ {'PASS', 'OPERATOR_REVIEW with mode=default-pass-pending-m18+'}
         → else 409.

7.  Compose idempotencyKey (D-M14-IS-7):
    body.idempotencyKey ?? `mcf-m14-activate/${mcvUid}/${MC.package_signature_hash}/${pe[0].evidence_json.evaluation_signature_hash}`
    (or equivalent — the value MUST be deterministic across same-substrate retries
    AND distinct across substrate changes).

8.  Build PeEligibilityResultInput[] from the 10 fetched rows.
    For each fetched row, carry-forward: peCheckCode, verdictCode, evidenceJson,
    panelRunUid. Set verifierVersion = M14_VERIFIER_VERSION ('mcf-m14-v1').
    Do NOT carry-forward certification_record_id (M4 fills it post-insertCert).

9.  Build ActivateMetricInput:
      metricContractVersionUid: mcvUid (from path param — NO inference).
      cert: {
        actionCode: 'metric_transition',
        fromStateCode: 'approved',
        toStateCode: 'active',
        certifierRoleAtAction: 'operator',
        rationaleText: body.rationaleText,
        certifierSub: user.userId,
        ... (other CertContextInput fields per M4 contract).
      }
      peEligibilityResults: [the 10 inputs from step 8]
      idempotencyKey: (from step 7)
      // dryRun: NOT set (deferred — §13)

10. Invoke certWriter.activateMetric(input).
    Return the result as the HTTP response body (201 Created).
    M4 handles: substrate lock, cert INSERT, PE INSERT, MCV UPDATE,
    M3 trigger fires (demotes prior is_current sibling), idempotency
    claim management. Errors bubble per the exception filter map.
```

## 7. PE-row read + aggregation gate (D-M14-IS-5)

The read MUST scope to `verifier_version = M13_EVALUATOR_VERSION` — the **currently-active M13 evaluator version constant**, not a hard-coded `'mcf-m13-v2'` literal. The constant is imported from the M13 service. This ensures that a future M13 version bump (v3, v4) requires no change to the M14 controller — the M14 controller always consumes the current M13 evaluator's output.

Query shape (read-only; bound to `tx ?? db`):

```sql
SELECT pe_check_code, verdict_code, evidence_json, panel_run_uid, evaluated_at
FROM mcf.metric_publication_eligibility_result
WHERE metric_contract_version_uid = $1
  AND verifier_version = $2  -- M13_EVALUATOR_VERSION
ORDER BY evaluated_at DESC
```

Caller dedupes by `pe_check_code` (first occurrence wins → latest evaluation under the current evaluator). If <10 distinct codes present, the gate fails. The aggregation rule mirrors M13's §4.5 (operator-supplied PE-MC-8 OPERATOR_REVIEW is treated as PASS-equivalent only for PE-MC-8).

A new `McfReadService.readM14ActivationGateInputs(mcvUid)` (or three smaller methods) encapsulates this read. Returns a typed structure `{mcvState, parentMcStampedHash, peRows}` so the handler is a thin orchestrator.

## 8. M14_VERIFIER_VERSION (D-M14-IS-6)

```ts
/** Per D-M14-IS-6: substrate-side dedup key for M14 activation PE rows.
 *
 * Version-bump policy (symmetric to D-M13-9): any semantic change to the
 * activation aggregation gate (§6 step 6 / §7 of this DBCP) MUST bump this
 * constant so re-evaluation of activation eligibility is not masked by
 * cached M4 idempotency results from the prior semantic. */
export const M14_VERIFIER_VERSION = 'mcf-m14-v1' as const;
```

Lives in `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` (next to existing constants) or in a new `mcf-m14-constants.ts` co-located with the controller — the implementation PR picks one. The bc-core PR also adds a unit test asserting current value (mirror of PR #208's M13 lock test) so any future bump is intentional.

## 9. Expected writes (D-M14-IS-8 + HA-1 / D426)

All writes performed by `McfCertWriterService.activateMetric` (the controller adds zero new writes):

| Table | Operation | Rows | Notes |
|---|---|---|---|
| `mcf.certification_record` | INSERT | 1 | `action_code='metric_transition'`, `subject_kind='metric_publication'`, `primitive_id=mcvUid`, `certifier_role_at_action='operator'` |
| `mcf.metric_publication_eligibility_result` | INSERT | 10 | `certification_record_id=<new certId>`, `verifier_version='mcf-m14-v1'`. One row per `PE_MC_CODES` |
| `mcf.metric_contract_version` | UPDATE | 1 | `governance_state_code: 'approved' → 'active'` on `mcvUid` |
| `mcf.metric_contract_version` (via M3 trigger) | UPDATE | 0..1 | Prior `is_current=TRUE` sibling on the same parent MC → `is_current=FALSE`. New row gets `is_current=TRUE` (atomic with state UPDATE per M3 trigger semantics) |
| `mcf.idempotency_claim` | INSERT / UPDATE | 0..2 | M4 idempotency-claim writes; per `acquireIdempotencyClaim` + `markIdempotencyCommittedInTx` |

**Forbidden tables (zero delta per HA-1 / D426 §5):**

```
metric.metric_definition
metric.metric_definition_knowledge
metric.metric_binding
metric.metric_thresholds
contract.metric_contract
contract.metric_contract_version
contract.metric_variable_binding
contract.metric_filter_clause
contract.panel_output_record       (M13 read-only; M14 does not touch)
contract.authoring_panel_rejection_log
mcf.metric_supersession            (M15 territory)
```

The integration spec (Test 7 in §10) asserts the deltas on all the above are 0 across the activation tx.

## 10. Tests (D-M14-IS-9)

| # | Test | Layer | Asserts |
|---|---|---|---|
| 1 | **Happy path** | unit + integration | HTTP 201; response body matches `ActivateMetricResult`; MCV `approved → active`; cert + 10 PE rows inserted; `is_current=true`; integration assertion: M4's `submitForReviewInTx`/`approveForActivationInTx` paths NOT called; only `activateMetric` / `activateMetricInTx` exercised. |
| 2 | **Auth: literal `mcf_publisher` missing** | unit | JWT carries `super_admin` (and `mcf_author`) but NOT `mcf_publisher`. HTTP 403. Zero DB writes (cert + PE + MCV row-count deltas all 0). |
| 3 | **Rationale too short** | unit | `rationaleText.length === 39`. HTTP 400; Problem+JSON detail names the field; zero DB writes. |
| 4 | **MCV not approved** | unit | Substrate MCV in `review`/`draft`/`active`/`superseded`. HTTP 409; detail names the current state; zero DB writes. |
| 5 | **Missing/invalid PE evidence** | unit | Five sub-cases: (a) zero v2 rows; (b) only 9 of 10 codes present; (c) PE-MC-1 = REJECT; (d) PE-MC-6 = OPERATOR_REVIEW; (e) PE evidence carries stale `current_package_signature_hash`. Each → HTTP 409 with specific reason; zero DB writes. |
| 6 | **Idempotent retry** | unit + integration | Two sequential calls with identical body + JWT + MCV. Second call returns cached result (`committed: true` first time; M4 returns cached structure second time). Total cert delta = 1; total PE row delta = 10. |
| 7 | **Legacy zero-delta** | integration | `BCCORE_INTEGRATION_DB=1` gated, SAVEPOINT-rolled-back pattern. Asserts deltas on all forbidden tables (§9) are 0 across the activation tx. Mirrors M13 integration spec's `FORBIDDEN_TABLES` pattern. |
| 8 | **MCV-fidelity (new — locks URL binding)** | integration | Seed two MCVs (MCV-A, MCV-B) under same parent MC, both `approved` with valid PE rows. Call `POST /api/mcf/metric-contract-versions/<MCV-A.uid>/activate`. Assert: ONLY MCV-A `governance_state_code` flips to `active`; MCV-B remains `approved`; activation cert's `primitive_id = MCV-A.uid`; the 10 new PE rows link to MCV-A. Then symmetric: separate test seeds same shape, activates MCV-B's URL, asserts MCV-B activates (not MCV-A). |

Plus the **HA-style source guard test** (mirror of PR #207's HA-1): test reads the controller source file and grep-asserts (a) zero references to `metric.metric_definition`, `contract.metric_contract`, `contract.metric_contract_version`, etc. — no legacy table mentions; (b) the literal-role precheck string `mcf_publisher` is present in the source as an explicit `user.roles.includes(...)` call (defends against accidental removal in a future refactor).

## 11. File list (bc-core implementation PR)

| File | Type | Purpose | Est. LOC |
|---|---|---|---|
| `src/registry/mcf/mcf-publication-activation.controller.ts` | NEW | The controller. Decorators + handler implementing the §6 10 steps. | ~90-110 |
| `src/registry/mcf/mcf-publication-activation.controller.spec.ts` | NEW | Unit tests 1-6 + HA source guard. | ~280-340 |
| `src/registry/mcf/mcf-publication-activation.controller.integration.spec.ts` | NEW | Integration tests 1 (round-trip), 6 (idempotent), 7 (legacy zero-delta), 8 (MCV-fidelity, both directions). `BCCORE_INTEGRATION_DB=1` gated. | ~230-290 |
| `src/registry/mcf/mcf.module.ts` (or current MCF module) | EDIT | Register `McfPublicationActivationController`. | +1-3 |
| `src/registry/mcf/mcf-cert-writer.service.ts` | EDIT | Add `M14_VERIFIER_VERSION` constant + JSDoc. | +10 |
| `src/registry/mcf/mcf-read.service.ts` | EDIT | Add `readM14ActivationGateInputs(mcvUid)` (or three smaller helpers). | +30-50 |

**bc-core net:** ~700 LOC. Runtime production code: ~150 LOC (controller + constants + read helper). The rest is tests.

**bc-docs-v3:** this file only (no ADR, no M13 DBCP cross-reference edit).

## 12. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Unique-index collision between M13 v2 and M14 rows | MEDIUM (would block first activation) | D-M14-IS-6: `M14_VERIFIER_VERSION='mcf-m14-v1'` (distinct 4-tuple). Integration Test 6 verifies INSERT succeeds. |
| `super_admin` bypass via shared `RolesGuard` | MEDIUM | D-M14-IS-2: decorator + in-handler precheck (§5). Test 2 + HA source guard. |
| Stale PE evidence (substrate drifted between M13 and M14) | LOW | Handler §6 step 6(a): hash gate; Test 5(e). |
| Operator surprised by `dryRun` absence | LOW | §13 records it as v2 deferred so the choice is documented. |
| Future M13 version bump silently breaks M14's PE-row read | LOW | D-M14-IS-5: read scoped to `M13_EVALUATOR_VERSION` constant, not a literal. Any M13 bump automatically reaches M14. |
| MCV-fidelity drift (controller activates the wrong MCV) | LOW (eliminated by URL design) | D-M14-IS-1 + Test 8 (two directions). |
| M3 trigger silently broken or absent | LOW | Integration Test 1: `isCurrentDemoted` assertion matches fixture (null on first; UID on subsequent). |
| Legacy writes leak through M4 transitively | LOW (already audited under D426) | Test 7 SAVEPOINT-rolled-back delta-zero assertion; HA source guard. |

No HIGH-severity risks remain after the mitigations above.

## 13. Deferred / out of scope

| Item | Why deferred |
|---|---|
| **`dryRun` body field** | v1 minimal-surface principle. The M4 method already accepts it; the controller can plumb it through in v2 without semantic change. v2 PR can be a small additive change to the controller + body schema; no DBCP amendment needed beyond a one-line note. |
| **Broader platform-wide literal-role guard** | The §5 in-handler precheck pattern handles M14 specifically. A `@LiteralRolesOnly()` decorator + companion guard that consumes the same `@Roles(...)` metadata and skips the `RolesGuard` wildcard would generalize the policy. Carve out a standalone ADR if the implementation review proves the pattern recurs (e.g., M15 supersession surface, future tenant-binding endpoints). |
| **Runtime / product visibility of activated metric** | M14 active-state proof is a precondition for the runtime visibility decision; per D426 §5, no compatibility projection is filed before that proof. The active-state visibility bridge (read-API vs projection vs hybrid) is an open D426 follow-up ADR. |
| **Legacy `metric.*` / `contract.*` projection at activation time** | Same as above. D426 §5 forbids; this DBCP enforces zero legacy writes; a future projection ADR sets the contract for any cross-store write at activation time. |
| **M14 supersedes-aware activation** (activating a successor version when a prior `active` sibling exists) | M3 trigger already demotes the prior `is_current=TRUE` sibling (one UPDATE). What's NOT yet specified: whether the prior sibling's `governance_state_code` should also flip to `superseded` (M15 territory) or stay `active` with `is_current=FALSE`. Per M4 service comment (`mcf-cert-writer.service.ts:1238`), the prior row stays state=`active` and is_current=`FALSE`; M15 supersession is a separate gate. The M14 v1 surface accepts this; M15's controller surface is a separate DBCP. |

## 14. Constraints respected

- ✓ Design only; no bc-core code change
- ✓ No M14 invocation
- ✓ No DB mutation
- ✓ No DDL apply
- ✓ No legacy writes (HA-1 / D426 enforced via §9 forbidden table list + Test 7 integration assertion + HA source guard)
- ✓ No Cognito changes
- ✓ Single concise DBCP — no separate ADR; no M13 DBCP edit (per operator's "do not make this a gravity well" direction)

## 15. Open questions for the implementation PR

The bc-core PR will resolve the following without revisiting this DBCP:

1. **Where does `M14_VERIFIER_VERSION` live?** Recommendation: alongside `M13_EVALUATOR_VERSION` constants in the existing `mcf-cert-writer.service.ts` or a new `mcf-m14-constants.ts`. Implementation chooses; either works.
2. **One read helper vs three on `McfReadService`?** Single `readM14ActivationGateInputs(mcvUid)` returning `{mcvState, parentMcStampedHash, peRows}` is preferred — keeps the controller a thin orchestrator. Implementation may split if readability suggests it.
3. **Where do new exception classes live (if needed)?** Reuse M4's `InvalidInputError`, `McvNotFoundError` (or M13's). New M14-specific exceptions are NOT required by this DBCP — the existing exception filter map covers Problem+JSON translation.
4. **Idempotency-key default format** — final string template is a one-line constant; the DBCP §6 step 7 / D-M14-IS-7 lock the inputs and the determinism contract; the exact separator (`/`) is implementation-chosen.

None of the above changes the substrate writes, the auth model, or the API contract specified above.

---

**End of DBCP.**

Implementation PR (bc-core) is a separately operator-authorized follow-up. No code change lands until that PR opens, reviews, and merges. No M14 invocation occurs until the bc-core PR is merged AND the operator explicitly authorizes the first run on a specific MCV.
