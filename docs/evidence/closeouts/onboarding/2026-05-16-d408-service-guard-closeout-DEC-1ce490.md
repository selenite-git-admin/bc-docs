---
title: "D408 service-guard closeout"
date: 2026-05-16
authority: DEC-1ce490
adr: bc-docs-v3/docs/adrs/ADR-1ce490.md
predecessor: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md
session: SES-8714df
type: service-guard-closeout
status: complete
---

# D408 service-guard closeout

**D408 core enforcement is complete on dev.** The data model, the four enforcement boundaries (GS-1 / GS-2 / GS-3 / GS-4), and the initial visibility surface (GS-5 partial) are all landed. Further D408 work is additive UX or successor decisions and is named explicitly in §3 below.

## 1. Data model — complete

Per the earlier closeout at [`2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md`](2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md):

- **DBCP-1q-A schema** (`bc-core@513404d`) applied on dev: 13 additive columns on `contract.business_field`; new `contract.business_field_foundational_whitelist` table + 3 seed rows; `certification_record.action_code` CHECK widened to 15 values.
- **DBCP-1q-A backfill** applied on dev: 1,681 rows updated (1,651 grandfather → `certified_catalog`, 30 corrections → `correction_required`); 1,681 paired `certification_record` ledger rows inserted.
- **Importer fallback fix** (`bc-core@186979d`): synthetic OAGIS fallback definitions no longer enter the catalog as auto-certified.
- **DBCP-1q-B demotion** applied on dev: 374 rows demoted (259 P3 + 115 P4); 374 paired `demote_bf_catalog` ledger rows.

### Final catalog state on dev

| `catalog_state_code` | Count |
|---|---:|
| `candidate_import` | **5,007** |
| `certified_catalog` | **1,651** |
| `correction_required` | **30** |
| `demoted_catalog` | **374** |
| `recertify_pending` | **0** |
| **Total** | **7,062** |

D408 invariant `remediate_bf_semantics = 1,392` held throughout the entire pipeline. Confirmed at this closeout.

## 2. Enforcement boundaries — complete

Five service-guard slices landed across the session.

| Slice | Boundary | Behaviour | Commit |
|---|---|---|---|
| **GS-1** | `FieldMappingService.suggest()` | Defaults to `catalog_state_code='certified_catalog'`; non-certified BFs no longer surface in source-field mapping suggestions, alias matching, exact-name matching, or description matching. Stats expose `totalBoFieldsRaw` + `filteredNonCertifiedBoFields`. | `bc-core@b22bc84` |
| **GS-2** | `CanonicalWizardService` | Step 2 read filters to `certified_catalog`; `writeCanonicalVersion()` builds `resolved_schema` from certified BFs only; refuses commit with `422 non_certified_bf_catalog_empty` when BO has BFs but none are certified. | `bc-core@2706452` |
| **GS-3** | `cc_field_mapping` write paths | `createFieldMappings`, `addMappings`, `replaceMapping` all refuse non-`certified_catalog` BFs with `422 non_certified_bf` (problem+json with `field_id` + `catalog_state_code` + `catalog_state_reason_code` + `certification_record_id` + `boundary`). Shared `assertBfCertifiedForBinding` helper exported for future GS-6. | `bc-core@2b28a48` |
| **GS-4** | SDA gate-evaluation diagnostics | `GateEvaluationResult.catalogState` surfaces `catalog_state_code` + reason + ledger id on every BF gate evaluation. Distinguishes the three previously-conflated axes (legacy `status_code` / D408 `catalog_state_code` / SDA evidence). Evaluation verdicts unchanged. | `bc-core@2cb7289` |
| **GS-5 partial** | bc-admin catalog visibility | Backend `GET /business-fields` list response widened with three catalog-state fields; `<BFStateChip />` rendered on `StandardFieldsPage` (new column) + `BusinessFieldDetailPage` (header). 5 closed-set state labels with reason-code tooltip. | `bc-core@e8e1659` + `bc-admin@7a45f55` |

Suggestion + write + diagnostic + initial-visibility boundaries all enforce or surface D408 catalog admission. Demoted, candidate, correction-required, and recertify-pending BFs cannot reach `cc_field_mapping` and do not appear in authoring suggestions or wizard pick-lists.

## 3. Explicit deprecation note: IntegrityService

`bc-core/src/registry/integrity.service.ts` is **deprecated by ADR-bebaec (D305)** in favour of `ChainStatusService`. The in-file comment at lines 1283-1290 says:

> *"IntegrityService is deprecated by ADR-bebaec (D305) in favour of ChainStatusService. It remains live because ContractService.transitionState still calls getKpiIntegrity as the pre-activation gate (transitionState:456). Do NOT extend IntegrityService."*

D408 GS-4 therefore did **not** extend IntegrityService even though it was named in the original service-guard plan. The correct move is a separate cleanup that:

1. Audits all call sites of `IntegrityService.getKpiIntegrity()` (notably `ContractService.transitionState`).
2. Migrates those call sites to `ChainStatusService` or to the MLS gate family.
3. Removes IntegrityService from the module wiring.
4. Deletes the file.

This is a follow-up, not a D408 obligation — see §4.

## 4. Remaining follow-ups (none gate session closure)

These items remain after D408 core enforcement. None block stopping the SES-8714df session; each is independent and benefits from a fresh session.

### Service-guard remainder
- **GS-5 remainder** — `/catalog/business-fields/review-queue` page; binding-time admission drawer (UI side of approve-in-place); chip rendering on the remaining ~8 BF-referencing pages (`MappingsPage`, `FieldResolutionPage`, `CanonicalReaderWizardPage`, `CreateCanonicalContractPage`, `CreateBusinessObjectPage`, `CreateMetric*Page` x3). Larger bc-admin surface; operator-visible polish, not enforcement.
- **GS-6 MC variable / grain bind refusal** — separate slice; not part of GS-1..GS-5. The `assertBfCertifiedForBinding` helper from GS-3 is forward-compatible (already accepts `boundary='mc_variable_binding'` and `boundary='mc_grain_binding'`).

### Successor ADRs
- **Registered-abbreviation registry** (ADR §2.1 future enforcement) — until filed, `naming_policy_violation` advisories remain advisory.
- **G3 LLM domain assist** — LLM-assisted plausibility check on `(domain, subdomain)` placement.
- **G4 duplicate-embedding stack** — embedding-based semantic-overlap detection.
- **Admission rule versioning scheme** — concretises the `admission_rule_version_at_certify` column's value scheme (currently literal `'v1'`).

### Code housekeeping
- **IntegrityService retirement audit** — per §3. Caller migration to `ChainStatusService` / MLS gate family, then deletion.
- **OAGIS onboarding refactor** — `onboardNoun()` carries scoped `eslint-disable max-lines-per-function, max-depth` per `bc-core@186979d`. Extract scalar/complex handlers when scope permits.
- **`seed-context-readiness.service.{ts,spec.ts}`** — dirty WIP at the time of GS-4; should be reviewed and either landed or reverted, then optionally extended with catalog-state awareness.
- **`canonical_field` gate result** — `evaluateCanonicalField()` does not yet carry `catalogState` because `canonical_field` has no D408 admission columns. Mirror GS-4 once those columns land.

### Data work
- **30 `correction_required` row correction plan** — author definitions + type-pair fixes for the P0 + P1 + P2 cohort. Each fix lands as a `recertify_bf_catalog` ledger action moving the row back to `certified_catalog`. Smallest data follow-up; high signal.
- **5,007 `candidate_import` triage policy** — largest residual cohort. Decide which subset is worth investing in (promote via SDA + G6) versus demoting in a future tranche. Requires an operator policy decision, not just engineering.

### Session housekeeping
- **TSK-9515d5 Phase 3 closure** — reference DEC-1ce490 + the artifacts in the closeout commit ledger. Phase 3's original deeper-scrape remediation path is superseded by the D408 admission pipeline.
- **SES-03f268 separate closure** — orphaned session from the Phase 3 work. Cross-reference DEC-1ce490 + this closeout + the data-side closeout. SES-03f268 itself remains untouched.

## 5. Stopping point

**D408 core enforcement is complete enough to stop this session.** Every offending boundary the original ADR identified is now either refused at the write layer, filtered at the suggestion layer, or surfaced at the diagnostic / visibility layer. Demoted and candidate rows cannot enter canonical mappings; correction-required rows are visible and ledgered; the catalog admission state is exposed wherever an operator needs to see it.

The remaining work in §4 is genuinely independent — each item belongs to its own session focus (UI surface, MC binding, code cleanup, data triage, session housekeeping). Bundling further work into SES-8714df would only extend a thread that has already covered the schema design, two DBCPs with applies, an importer fix, five guard slices, and two closeout documents.

## 6. References

- ADR: [ADR-1ce490](../../../governance/adrs/ADR-1ce490.md)
- DBCP design: [2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md](../../dbcp/onboarding/2026-05-16-d408-bf-catalog-admission-cleanup-dbcp-plan-DEC-1ce490.md)
- DBCP-1q-A verification plan: [2026-05-16-d408-dbcp-1q-a-verification-plan.md](../../dbcp/onboarding/2026-05-16-d408-dbcp-1q-a-verification-plan.md)
- DBCP-1q-B verification plan: [2026-05-16-d408-dbcp-1q-b-verification-plan.md](../../dbcp/onboarding/2026-05-16-d408-dbcp-1q-b-verification-plan.md)
- Data-side closeout: [2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md](2026-05-16-d408-bf-catalog-admission-cleanup-closeout-DEC-1ce490.md)
- Service-guard plan: [2026-05-16-d408-service-guards-plan-DEC-1ce490.md](../../work-records/onboarding/2026-05-16-d408-service-guards-plan-DEC-1ce490.md)
- D162 (database rules): `bc-docs-v3/docs/adrs/ADR-1918d0.md`
- D268 (session discipline): `bc-docs-v3/docs/adrs/ADR-ebf0b4.md`
- Foundation invariants: `bc-docs-v3/docs/foundation/the-invariants.md`
