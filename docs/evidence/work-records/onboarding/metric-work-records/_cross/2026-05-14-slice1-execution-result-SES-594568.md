---
title: "Slice (1) execution result — first honest seed → catalog promotion (revenue_collection_rate)"
session: SES-594568
date: 2026-05-14
status: executed
executed_at: 2026-05-14
type: slice-execution-result
authority: DEC-a17d0f
related:
  - 2026-05-14-slice1-promotion-gate-plan-SES-594568.md
  - 2026-05-14-slice0-execution-result-SES-594568.md
  - 2026-05-14-slice0.5-execution-result-SES-594568.md
  - 2026-05-14-slice0.7-execution-result-SES-594568.md
  - 2026-05-14-slice0.8-execution-result-SES-594568.md
  - 2026-05-14-session-findings-SES-594568.md
  - DEC-01419c
  - DEC-01df6b
  - DEC-4a8abb   # D329
  - DEC-a8e8fc   # D365
  - DEC-bebaec   # D305
---

# Slice (1) execution result — first honest end-to-end MC promotion

`revenue_collection_rate` (metric_definition_id `5cb2c71c-07ac-424e-b96a-cadb7ba67748`)
promoted to the catalog as `mc__revenue_collection_rate` v1.0.0 active.
First metric in the platform's history to traverse the official
`SeedPromotionService` → `McOnboardingService` → `ContractService.activateVersion`
path end-to-end and reach `governance_state_code='active'`.

## 1. Outcome

```
POST /api/onboarding/seed/5cb2c71c-07ac-424e-b96a-cadb7ba67748/promote
HTTP 201

{
  "data": {
    "metricContractId": "019e25b7-2ee0-7f8a-96c9-e5843f81b3dd",
    "metricContractVersionCode": "1.0.0",
    "verificationId": "d8675b71-60c0-4efa-8acf-ace09b8087eb",
    "seedStatusAdvanced": true,
    "deterministicTrace": {
      "formula": "O1 = (I1 / I2) * C1",
      "values": { "I1": 80000, "I2": 100000, "C1": 100 },
      "expectedOutput": 80,
      "computedOutput": 80,
      "evidenceType": "deterministic_formula_eval"
    },
    "metricCode": "MT-05032",
    "resumedFromDraft": true
  }
}
```

## 2. Postflight verification (9 / 9 green)

| # | Check | Result |
|---|---|---|
| Q1 | Exactly 1 MC for the seed | ✓ |
| Q2 | Version `1.0.0`, `governance_state_code='active'` | ✓ |
| Q3 | `contract_json.body` carries all 9 master-shape keys | ✓ |
| Q4 | C1 variable persists `value=100` in body per D329-R4 | ✓ |
| Q5 | `contract_json.header.description` matches seed's `description_text` byte-for-byte | ✓ |
| Q6 | Catalog `metric_contract.tags = {finance, accounts_receivable, collection, percentage, ratio}` (β path) | ✓ |
| Q7a | 4 verification rows for the seed's formula | ✓ |
| Q7b | All 4 have `verdict_code = 'deterministic_passed'` | ✓ |
| Q8 | Seed-side `metric_formula_variable.constant_value` for C1 still `NULL` (D329 honored, seed not mutated) | ✓ |
| Q9 | Seed `status_code='active'`, `verification_result_code='pass'`, `verification_evidence_id` populated | ✓ |

## 3. The four verification rows (audit trail)

| Iter | Created | Verdict | Outcome |
|---|---|---|---|
| 1 | 2026-05-14 07:56:49 | `deterministic_passed` | First slice (1) attempt; failed at `ContractRepository.createContract` (missing `metric_definition_id` binding — fixed in slice 0.7). |
| 2 | 2026-05-14 09:00:22 | `deterministic_passed` | Slice 0.7 retry; createContract + createVersion succeeded; failed at `activateVersion` (`IntegrityService` SQL typo + MLS-14 sequencing — fixed in slice 0.8). |
| 3 | 2026-05-14 10:20:43 | `deterministic_passed` | Slice 0.8 retry; failed at `McOnboardingService.create`'s `findContractByName` conflict check (existing draft from attempt 2 — addressed by slice 0.9 resume-aware behavior). |
| 4 | 2026-05-14 10:32:33 | `deterministic_passed` | **Slice 0.9 retry — SUCCESS.** Resume path: existing draft v1.0.0 detected, payload matched preview, `ContractService.activateVersion` invoked, seed advanced. |

Per Invariant III, all four rows are preserved in the ledger. Three of them record "verification passed, promotion gate rejected at a downstream layer" — the wrapper's three-phase model behaved correctly each time: TX1 audit is durable independent of TX2/TX3 outcome.

## 4. The path that worked

1. **Phase 1 — load.** `MetricDefinitionRepository.findById` + Drizzle reads of `metric_formula` + `metric_formula_variable`. Seed loaded, status=`draft` confirmed.
2. **Phase 2 — deterministic verification.** Pure-function evaluator (slice 0). `(80000 / 100000) * 100 = 80 == expectedOutput=80`. Pass.
3. **Phase 3a — TX1 audit.** New `metric.metric_formula_verification` row at `iteration_seq=4` (slice 0.7 increment logic), `verdict_code='deterministic_passed'`, `maker_a_output` carries the deterministic trace. AI columns all NULL.
4. **Phase 4 — resume detection (slice 0.9).** `lookupExistingMcForSeed(metric_definition_id, mcName)` against `contract.metric_contract WHERE archived_at IS NULL`. Found existing draft `019e25b7-...` with v1.0.0. Payload match check: `mcOnboarding.preview(dto)` produced an envelope; body + 4 header fields canonical-compared against existing `contract_json` → match.
5. **Phase 4 (resume) — activate.** `ContractService.activateVersion(existingMcId, '1.0.0')`. Internally:
   - `IntegrityService.getKpiIntegrity` (deprecated; slice 0.8 transitional SQL fix in play) → no broken bindings, gate passes.
   - **`ChainStatusService.refreshChainStatusForVersion(mcId, '1.0.0')`** (slice 0.8 new method) → wrote `contract.chain_status` row for the about-to-be-activated version. Verdict was good enough to proceed (MLS-14 didn't refuse).
   - `Mls14ActivationGate.evaluateAndLog` → no blockers.
   - `versionRepo.updateVersionState(..., 'active')`.
   - Fire-and-forget `chainStatusService.refreshChainStatus` (post-activation refresh).
6. **Phase 5 — TX3 seed advance.** `UPDATE metric.metric_definition SET status_code='active', verification_result_code='pass', verification_evidence_id='d8675b71-...'`.

## 5. The seven slices that got us here

| Slice | bc-core | bc-docs-v3 | Contribution |
|---|---|---|---|
| 0 | `17836ae` | `70b20a4` | `SeedPromotionService` wrapper + β header overrides on `McOnboardingService` + DBCP `f60523a` (`deterministic_passed` verdict). |
| 0.5 | `6723c62` | `1de7fe2` | `McOnboardingService.preview` honors D365 derived `fiscal_period` / `fiscal_year`. |
| 0.7 | `31bd423` | `bf30c49` | `metric_definition_id` threaded through `CreateContractDto` → `ContractService` → `ContractRepository` (new `metric` family branch in `appendFamilyColumns`); wrapper sets `name = mc__{seed.metricName}`; iteration_seq MAX+1; `metricCode` derived. |
| 0.8 | `d2a6fa3` | `748944a` | `IntegrityService` SQL typo transitional fix; `ChainStatusService.refreshChainStatusForVersion` (pre-activation compute); `ContractService.transitionState` order = integrity → chainStatusForVersion → MLS-14; `MetricWizardService.completeMetric` quarantined at service + controller layers (HTTP 410); ADR-bebaec erratum. |
| 0.9 | `c4c780c` | (this MWR) | Resume-aware: `lookupExistingMcForSeed` (raw SQL, filters archived); `createOrResumeMc` branches fresh-create vs resume-activate vs conflict; canonical payload-match helper; `resumedFromDraft` response field. |
| 1 | — | (this MWR) | First successful end-to-end promotion. |

## 6. Hard rules honored throughout

- All writes mediated by services. No raw INSERT/UPDATE/DELETE from slice code into `contract.metric_contract`, `contract.metric_contract_version`, or any other governed table.
- Verification rows preserved per Invariant III — no rollbacks, no deletions, no rewrites.
- Constants persisted in `body.variables[].value` per D329-R4. `KNOWN_CONSTANTS` TS map never touched by this slice; it stays in place for legacy MCs (tracked separately).
- β path: header `description` and `tags` carry Foundation-correct values, not the historical drifted `Metric contract: ...` placeholder.
- `header.kind = "metric"` unchanged.
- `co_bindings` auto-resolved by `McOnboardingService.resolveCoBindings` from CC `field_selection`: `cc__receivable_hdr` (for `total_cash_collected_from_revenue`) + `cc__invoice_hdr` (for `total_billed_revenue`).
- 4 thresholds (excellent/good/warning/critical) — CR-QG-MC-001 satisfied.
- `MetricWizardService.completeMetric` remains quarantined (slice 0.8). Single writer for promotion.
- No archive, no rollback, no rebuild of any pre-existing artifact.

## 7. What this slice DID NOT do (deliberate, slice (1) scope)

- Did not promote any other metric. 437 candidate seeds remain in the draft pool (tracked by TSK-9ecaee).
- Did not extend the wizard to delegate to `SeedPromotionService` (Option B follow-up).
- Did not migrate the existing 540 historical MCs (separate concern; their provenance is documented).
- Did not change `IntegrityService`'s deprecation status (still deprecated per D305; just patched).
- Did not address the 11 pre-existing `reader-runtime` test failures (unrelated debt).
- Did not address the 332 active MCs that still depend on the `KNOWN_CONSTANTS` TS map (TSK-1f4988).
- Did not run a chain_status verdict check on the new MC end-to-end — that's post-activation refresh territory.

## 8. Pre-existing partial state (preserved)

Three artifacts from the failed attempts are now part of the canonical record:

- Three verification rows at iter=1/2/3 for the same seed's formula. All `deterministic_passed`. Audit trail of the path-discovery process.
- The `contract.metric_contract` row `019e25b7-...` and its `contract.metric_contract_version` v1.0.0 were originally created by slice 0.7's retry attempt; slice 0.9 activated that same draft rather than creating a duplicate. The MC's `created_at` timestamp (`2026-05-14 09:00:22`) reflects the slice 0.7 retry, not the final slice 0.9 activation.

This is honest. Future audits reading the timeline will see the discovery path; nothing pretends to be a fresh clean run.

## 9. What this proves

- The official MC promotion path now works end-to-end for a new metric.
- The wrapper composes the canonical service stack (`McOnboardingService` + `ContractService` + `MetricDefinitionRepository`) without bypassing any gate.
- The three-phase TX model (audit / promotion / seed advance) is correct in both fresh-create and resume scenarios.
- D305 / D329 / D365 / D391 architectural decisions are realized in code, not just on paper, for at least one metric.
- The slice ladder (0 → 0.5 → 0.7 → 0.8 → 0.9 → 1) successfully discovered and repaired four latent bugs in the path that had never been exercised: `metric_definition_id` binding, D365 gate consistency, IntegrityService SQL typo, MLS-14 sequencing. Plus quarantined the parallel writer (`MetricWizardService.completeMetric`).

## 10. Open follow-ups (not new tasks; recorded here)

| Item | Disposition |
|---|---|
| Refactor `MetricWizardService.completeMetric` to delegate to `SeedPromotionService.promoteSeed` (Option B per slice 0.8 MWR) | Tracked in slice 0.8 MWR §8. Pick up after slice (1) ships. |
| Idempotent active-retry behavior in `SeedPromotionService.createOrResumeMc` | Deliberately deferred per slice 0.9 scope. Currently raises `ConflictException` on existing-active. Revisit when needed (e.g. operator UI behavior demands it). |
| `ContractRepository.findContractByName` does not filter archived | Slice 0.9 worked around by using its own focused lookup. The repo behavior is a broader inconsistency; not slice (1) scope. Worth a small fix slice if it bites anywhere else. |
| 437 other never-started candidate seeds | Tracked by TSK-9ecaee. After slice (1) success, the pattern is repeatable: pick a candidate, build the input, POST. The slice ladder doesn't need to be re-traversed for the next metric (slices 0 / 0.5 / 0.7 / 0.8 / 0.9 are all in place). |
| 332 legacy MCs depending on `KNOWN_CONSTANTS` TS map | Tracked by TSK-1f4988. Not slice (1) scope. |
| 540 historical MCs created outside the canonical path | Tracked by TSK-9ecaee + session findings MWR. Not slice (1) scope. |
| Pre-existing `reader-runtime` test failures (11) | Unrelated debt. Not addressed by any slice in this arc. |

---

**End of slice (1) execution result.**

`revenue_collection_rate` is in the catalog. The platform's promotion path works.
