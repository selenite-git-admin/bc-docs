---
title: "Slice (1b) execution result — fresh-create proof (ar_growth_rate)"
session: SES-594568
date: 2026-05-14
status: executed
executed_at: 2026-05-14
type: slice-execution-result
authority: DEC-a17d0f
related:
  - 2026-05-14-slice1-execution-result-SES-594568.md
  - 2026-05-14-slice0.9-execution-result-SES-594568.md
  - 2026-05-14-slice0.8-execution-result-SES-594568.md
---

# Slice (1b) execution result — fresh-create proof

Slice (1) succeeded via the resume path (slice 0.9's branch). To prove
the fresh-create path also works end-to-end, a second promotion was
run on a clean seed with no prior MC of any kind. Per operator
direction.

## 1. Outcome

```
POST /api/onboarding/seed/35e28695-35c2-49e2-bfa1-ed54c25ca1e9/promote
HTTP 201

{
  "data": {
    "metricContractId": "019e2613-fc7a-7755-b76f-6b1433ab247b",
    "metricContractVersionCode": "1.0.0",
    "verificationId": "9d48eedb-3bee-48af-b3e1-89bc051617c1",
    "seedStatusAdvanced": true,
    "deterministicTrace": {
      "formula": "O1 = ((I1 - I2) / I2) * C1",
      "values": { "I1": 120000, "I2": 100000, "C1": 100 },
      "expectedOutput": 20,
      "computedOutput": 20,
      "evidenceType": "deterministic_formula_eval"
    },
    "metricCode": "MT-04970",
    "resumedFromDraft": false
  }
}
```

`resumedFromDraft: false` confirms the fresh-create branch was taken,
not the slice 0.9 resume branch. This is the first metric promoted
end-to-end through the canonical `McOnboardingService.create()` path
without traversing the resume code path.

## 2. Postflight 11 / 11 green

| # | Check | Result |
|---|---|---|
| Q1 | 1 MC for the seed | ✓ |
| Q2 | Version `1.0.0`, `governance_state_code='active'` | ✓ |
| Q3 | `contract_json.body` carries all 9 master-shape keys | ✓ |
| Q4 | C1 carries `value=100` in body per D329-R4 | ✓ |
| **Q4b** | `body.direction_code = 'target-is-optimal'` (kebab-case) | ✓ — **first non-`higher-is-better` promotion** |
| Q5 | `header.description` matches seed's `description_text` | ✓ byte-for-byte |
| Q6 | Catalog `tags = {finance, accounts_receivable, growth, percentage, ratio}` | ✓ |
| Q7a | 1 verification row for this formula | ✓ |
| Q7b | `verdict_code = 'deterministic_passed'` | ✓ |
| Q8 | Seed-side `metric_formula_variable.constant_value` for C1 still `NULL` | ✓ (D329 honored; seed not mutated) |
| Q9 | Seed `status_code='active'`, `verification_result_code='pass'` | ✓ |

## 3. What this proves that slice (1) didn't

| Aspect | Slice (1) | Slice (1b) |
|---|---|---|
| Path taken | resume (slice 0.9's branch) | **fresh-create** (`McOnboardingService.create` end-to-end) |
| `direction_code` exercised | `higher-is-better` | **`target-is-optimal`** (kebab-case translation tested for 3rd enum value) |
| Formula shape | `O1 = (I1/I2)*C1` | **`O1 = ((I1-I2)/I2)*C1`** (deterministic evaluator's subtraction path) |
| CC bindings shape | 2 CCs, 1 field each | **1 CC, 2 fields** |
| Verification rows accumulated for this formula | 4 (3 failed + 1 success) | **1** (clean first attempt) |
| Prior partial state | extensive | **none** |

The path that worked, end-to-end, in one POST:

1. Phase 1 — load seed `ar_growth_rate` (status `draft`).
2. Phase 2 — deterministic check: `((120000 - 100000) / 100000) * 100 = 20`. Pass.
3. Phase 3a (TX1 audit) — `metric_formula_verification` row at `iter=1`.
4. Phase 4 — `lookupExistingMcForSeed` returns **empty** → **fresh-create branch**.
5. Phase 4 (fresh) — `McOnboardingService.create()`:
   - `preview()` runs CR-QG-MC-001 (14 checks) green.
   - `contractService.createContract` (slice 0.7's `metric` family branch) binds `metric_definition_id` and writes `contract.metric_contract` row.
   - `contractService.createVersion` writes `contract.metric_contract_version` in `draft` with the 9-key `contract_json`.
   - `contractService.activateVersion('1.0.0')`:
     - `IntegrityService.getKpiIntegrity` (slice 0.8 SQL fix) — passes.
     - `ChainStatusService.refreshChainStatusForVersion` (slice 0.8 new method) — writes the chain_status row pre-MLS-14.
     - `MLS-14 Activation Gate` — passes.
     - `versionRepo.updateVersionState(..., 'active')`.
     - Fire-and-forget `chainStatusService.refreshChainStatus` (post-activation).
6. Phase 5 — seed `status_code` → `active`.

## 4. State of the catalog after slice (1b)

| Catalog dimension | Count |
|---|---|
| Total `contract.metric_contract` rows | 780 (778 historical + 2 from this session: revenue_collection_rate + ar_growth_rate) |
| Non-archived | 591 |
| Active versions | 731 (729 historical + 2 from this session) |
| Promoted-and-verified via canonical path | **2** (both from this session) |
| Other historical | 540 (via parallel paths, now quarantined per slice 0.8) |
| Verification rows total (`metric_formula_verification`) | 8 (3 historical + 4 for revenue_collection_rate + 1 for ar_growth_rate) |

Two MCs in the catalog have been promoted through the disciplined path. The fresh-create path is now proven.

## 5. Constraints honored

- No archive of any row.
- No rollback of any verification row.
- No code change in this slice — purely exercising the slice 0/0.5/0.7/0.8/0.9 surfaces.
- `MetricWizardService.completeMetric` remains quarantined.
- `KNOWN_CONSTANTS` TS map remains in place for legacy MCs (untouched).
- 437 - 1 = **436 unpromoted candidate seeds** remain (down from 437).

## 6. Repeatability

Slice (1b) demonstrates that future promotions repeat in one POST without re-traversing the slice ladder:

- The slice 0/0.5/0.7/0.8/0.9 surfaces are all in place in `bc-core@c4c780c`.
- Operator builds DTO + POSTs to `/api/onboarding/seed/:id/promote`.
- If preview passes → promotion succeeds.
- If preview fails → real grain/binding/threshold gap surfaces honestly.
- If a prior partial-state MC exists for the same seed → slice 0.9's resume branch handles it.

The 436 remaining candidate seeds are repeatable promotions through this path.

## 7. What this does NOT do (deliberate, slice (1b) scope)

- Did not promote any other metric beyond ar_growth_rate.
- Did not refactor `MetricWizardService.completeMetric` to delegate (Option B follow-up).
- Did not migrate historical 540 MCs.
- Did not address remaining tracking tasks (TSK-9ecaee, TSK-1f4988, TSK-620cf3).

---

**End of slice (1b) execution result.**

The fresh-create path works. The official promotion pipeline is proven on
two metrics — one via fresh-create, one via resume. 436 candidates remain.
