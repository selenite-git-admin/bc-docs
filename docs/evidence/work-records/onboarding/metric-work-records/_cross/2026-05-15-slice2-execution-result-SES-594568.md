---
title: "Slice (2) execution result — SeedContextReadinessService (three-layer)"
session: SES-594568
date: 2026-05-15
status: executed
executed_at: 2026-05-15
type: slice-execution-result
authority: DEC-a17d0f
related:
  - 2026-05-14-slice1-execution-result-SES-594568.md
  - 2026-05-14-slice1b-execution-result-SES-594568.md
  - DEC-bebaec   # D305
---

# Slice (2) execution result — Seed Context Readiness

After slices 1 and 1b proved the canonical promotion path works for a
seed with sufficient surrounding context, slice 2 adds the read-only
diagnostic that answers, for a draft seed: **"what context exists,
what semantic checks passed / failed / are unevaluable, and what must
be authored or fixed before promotion?"**

## 1. Commits

| Repo | Commit | Push |
|---|---|---|
| `bc-core` | **`bd493e7`** (service + tests) + **`004426e`** (SQL fix for the `IN (...)` clause) | `c4c780c..004426e` |
| `bc-docs-v3` | (this MWR) | pending |

## 2. The three-layer model

Per operator decision 2026-05-15: **availability is not readiness**.

| Layer | Purpose | Verdict allowed? |
|---|---|---|
| `contextAvailability` | Pure inventory: seed / formula / variables / CF / BF / CC bindings / grain candidates (incl. D365 derived `fiscal_period`) / constants. | **No.** Existence flags only. |
| `semanticReadiness` | Authority checks: `cfSemanticFamilyPerInputCf` (null = unevaluable); `bfCfCompatibility` via `CompatibilityFilterService.check` 15-rule matrix over (BF, CF, resolution_rule) triples; `bfSdaGates: 'deferred_in_v1'`. | Yes. Red = blocking. Yellow / inconclusive / missing semantic_family = unknown, **not pass**. |
| `promotionReadiness` | Aggregate verdict + blockers + operator authoring requirements with suggested defaults. | Three states. |

### Verdict states

| Verdict | Conditions |
|---|---|
| `blocked` | Any availability blocker (CF missing, no CC binds input, formula missing, seed not draft, seed already promoted) **or** any `red` compatibility verdict. |
| `needs_authoring` | No blockers, but missing semantic_family on any CF **or** yellow/inconclusive compatibility **or** SDA `deferred_in_v1` **or** constants need operator completion. |
| `ready_for_preview` | No blockers, no yellow/inconclusive/missing-semantic-family, no constants needing completion, SDA evaluable. **Structurally unreachable in v1 by design** — `bfSdaGates: 'deferred_in_v1'` always pushes to `needs_authoring` per spec. |

The reachability of `ready_for_preview` is gated on the v2 SDA BF gate evaluation work. Slice 2 cannot honestly emit `ready_for_preview` today.

## 3. Endpoint

```
GET /api/onboarding/seed/:metric_definition_id/readiness
Authorization: Bearer <admin JWT>
```

`@PlatformOnly()`. Read-only. No body. No promotion side-effects.

## 4. Files

| File | Action |
|---|---|
| `bc-core/src/registry/seed-context-readiness.service.ts` | new (~480 lines after refactor) |
| `bc-core/src/registry/seed-context-readiness.controller.ts` | new (~40 lines) |
| `bc-core/src/registry/seed-context-readiness.service.spec.ts` | new (11 cases R1–R11) |
| `bc-core/src/registry/execution.module.ts` | provider + controller wiring |

## 5. Reuses (no rule duplication, no new architecture)

- `MetricDefinitionRepository.findById` (seed)
- `CanonicalFieldRepository` — `findByName`, `findExistingNames`, `findCcForCanonicalField`, `hasCcMapping`
- `StandardFieldRepository.findExistingNames` (output BF check)
- `ContractService` (typed injection; CC bodies read via REGISTRY_DB filtered to active versions)
- `CompatibilityFilterService.check` (the same 15-rule matrix chain-status and the runtime engine consult)
- `derivedFactColumnsForCc` (same shared helper schema-provisioner, chain-status, mc-onboarding use for D365)
- Raw SQL only for: slice-0.9-style non-archived MC lookup (`archived_at IS NULL` filter — `findContractByName` does not honor it); compatibility triple join over `cc_field_mapping × business_field × canonical_field × canonical_contract`.

## 6. Live exercise on three metrics

Probed the endpoint against three seeds covering the verdict matrix:

### 6.1 `revenue_collection_rate` (promoted in slice 1 via resume)

```jsonc
{
  "verdict": "blocked",
  "blockers": [
    { "layer": "availability", "code": "seed_not_draft" },
    { "layer": "availability", "code": "seed_already_promoted" }
  ],
  "seed": { "statusCode": "active", "metricCode": "MT-05032" },
  "alreadyPromoted": {
    "hasMc": true,
    "metricContractId": "019e25b7-2ee0-7f8a-96c9-e5843f81b3dd",
    "versionCode": "1.0.0",
    "governanceStateCode": "active"
  },
  "boundCcs": ["cc__invoice_hdr", "cc__receivable_hdr"],
  "fiscal_period": { "derivedFromAnyBoundCcPostingDate": true },
  "semanticOverall": {
    "hasRedCompatibility": false,
    "hasYellowCompatibility": false,
    "hasInconclusiveCompatibility": true,
    "anyCfSemanticFamilyMissing": true
  },
  "bfSdaGates": "deferred_in_v1",
  "compatibilityTriplesCount": 2
}
```

Both availability blockers fire as expected. Semantic surface: two BF↔CF triples discovered (one per input field), but `semantic_family` is NULL on all CFs (`hasInconclusiveCompatibility: true`) — honest "unknown, not pass."

### 6.2 `ar_growth_rate` (promoted in slice 1b via fresh-create)

Same shape: `blocked` with `seed_not_draft` + `seed_already_promoted`. Single bound CC (`cc__receivable_hdr`). 2 compatibility triples. semantic_family missing. fiscal_period derived from CC's `posting_date_field`.

### 6.3 `ar_concentration_risk` (never promoted)

```jsonc
{
  "verdict": "needs_authoring",
  "blockers": [],
  "seed": { "statusCode": "draft", "metricCode": "MT-04969" },
  "alreadyPromoted": { "hasMc": false, ... },
  "boundCcs": ["cc__receivable_hdr"],
  "fiscal_period": { "derivedFromAnyBoundCcPostingDate": true },
  "semanticOverall": {
    "hasRedCompatibility": false,
    "hasYellowCompatibility": false,
    "hasInconclusiveCompatibility": true,
    "anyCfSemanticFamilyMissing": true
  },
  "bfSdaGates": "deferred_in_v1",
  "compatibilityTriplesCount": 2
}
```

This is the most informative probe. **Availability is green** — draft seed, no existing MC, CC binding resolved, D365 fiscal_period derivable. **Semantic is unknown** — CFs have `semantic_family = NULL` (inconclusive per the rule matrix), SDA gates deferred. **Verdict: `needs_authoring`** — correctly refuses to claim `ready_for_preview` because the platform cannot make a semantic-correctness claim.

The fact that `revenue_collection_rate` and `ar_growth_rate` were both promoted successfully despite identical `semantic_family = NULL` is informative on its own: the platform's promotion path does not currently enforce semantic readiness; slice 2 is the new layer that surfaces it honestly.

## 7. Tests R1–R11 (all pass)

| # | Case | Verdict |
|---|---|---|
| R1 | seed not found | `NotFoundException` |
| R2 | seed status='active' | `blocked` (`seed_not_draft`) |
| R3 | non-archived MC exists | `blocked` (`seed_already_promoted`) |
| R4 | archived-only MC | not blocked on that |
| R5 | all availability + semantic green | `needs_authoring` (SDA `deferred_in_v1` per spec) |
| R6 | input CF missing | `blocked` (`cf_input_missing`) |
| R7 | input CF exists but no CC binds it | `blocked` (`no_cc_binds_input`) |
| R8 | bound CC declares `posting_date_field` | fiscal_period `derivedFromAnyBoundCcPostingDate: true` |
| R9 | availability green + `semantic_family = null` | `needs_authoring` (semantic unknown) |
| R10 | compatibility RED (`measure-currency` + `latest`) | `blocked` (`bf_cf_compatibility_red`) |
| R11 | compatibility YELLOW (`datetime` CF + `date` BF) | `needs_authoring` with yellow warning surfaced |

11/11 pass. Full suite 1391/1402 active pass; 11 pre-existing `reader-runtime` failures unchanged.

## 8. Beta header policy honored

Per session-findings §4 + operator decision:

- `purposeStatement.status = 'required_for_beta_header'`. Suggested = seed.description_text.
- `classificationTags.status = 'required_for_beta_header'`. Suggested = [function, subfunction] derived from seed.

Not "recommended."

## 9. Hard boundaries honored

- **Read-only.** GET endpoint only. No INSERT/UPDATE/DELETE anywhere in the service.
- **No promotion POST.** Endpoint does not trigger promotion side-effects.
- **No auto-creation.** Missing CF/BF/CC/context surfaces as blockers with owning service named; service does not create.
- **No TestBench / AdminInspection / McIntegrity / MetricWizard changes.**
- **No new architecture.** Reuses `CompatibilityFilterService` and `derivedFactColumnsForCc`.
- **Semantic correctness is not claimed unless the authority actually evaluated it.** `bfSdaGates: 'deferred_in_v1'` is explicit; not treated as pass anywhere.

## 10. Mid-slice issue: SQL fix

Initial commit (`bd493e7`) passed unit tests but failed at HTTP 500 on live exercise. Root cause: Drizzle's `${array}::text[]` template parameterization produces `($1, $2)::text[]` (tuple-cast), not a Postgres array literal. Switched to the `sql.join` + `IN (...)` pattern that `integrity.service.ts:1281` already uses. Committed as `004426e`. Unit tests unaffected; live exercise green afterwards.

This is the kind of bug that an integration test against a real DB would catch immediately. Unit tests with mocked `db.execute` don't parse SQL. Worth flagging as a slice-2 observation: the readiness service is a good candidate for a small integration test in a future slice (exercise it against the real DB on a known seed).

## 11. Open follow-ups (deferred to v2)

| Item | Disposition |
|---|---|
| SDA BF gate evaluation per input/output BF | `GateEvaluationService.evaluateBusinessField` exists. Calling it for every BF in the chain is meaningful work; surface as a future v2 slice. |
| Live `McOnboardingService.preview` pass-through (operator submits candidate inputs, readiness reports preview's verdict) | Would require POST variant; v2. |
| `ready_for_preview` unreachable in v1 | By design — SDA deferred. Reachability resumes after v2 SDA evaluation. |
| Strict-mode toggle (inconclusive = blocked) | v2 if operator policy demands stricter behavior. |
| Per-input CF↔BF mapping enumeration (not just compatibility verdict) | v1 surfaces compatibility verdicts but does not enumerate every mapping row. v2 could add. |

## 12. What this slice does NOT do

- Does not promote any metric.
- Does not auto-create missing CFs / BFs / CCs / cc_field_mappings.
- Does not block historical promotion via SeedPromotionService (slice 2 is diagnostic only; slice 0.9's wrapper is unchanged).
- Does not change the response shape of any existing service.

---

**End of slice (2) execution result.**

For 436 candidate seeds in the unpromoted pool, the readiness endpoint
now tells the operator (or future AI orchestration) exactly what's
missing and which owning service should fix it — without claiming
semantic correctness the platform cannot yet vouch for.
