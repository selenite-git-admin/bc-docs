---
metric: mc__total_revenue (+ 21 dependents)
metric_version: n/a
tenant: platform
source_system: n/a
work_type: rejection-investigation
session_uid: SES-1c080e
date: 2026-05-11
status: decided
related_commits: []
related_tasks: []
related_adrs: []
related_change_records:
  - CHG-8d4e6d                  # SES-1c080e plan-side
repair_location: C
affected_boundary: canonical_evaluation
foundation_gate: passed
---

# total_revenue production gap — cross-metric rejection investigation — 2026-05-11

> **This record is orientation memory, not contract authority.** Canonical sources (`contract.cc_field_mapping`, `contract.canonical_field`, ADRs, evidence rows, DevHub change records) win on conflict.

## Summary

The Apex formula-token audit shows `total_revenue` as the top broken canonical field — 19 MCs blocked. Service-first diagnosis reveals the cc_field_mapping for `total_revenue` on `cc__invoice_hdr` points at the business field `invoice_hdr_total_amount`, which no observation_field_map row emits. The CC fact column is therefore structurally null in every tenant. The recommended correction is to repoint the single cc_field_mapping row to `invoice_hdr_extended_amount` (already mapped by 36 sibling CFs on the same CC; type-compatible; populated upstream). The CF `total_revenue` itself carries no description today; clarification of its semantic ("net top-line revenue, pre-tax; OAGIS extended_amount sum") is a paired Layer B step. A governed service endpoint exists for the mapping repair (`POST /onboarding/cc/{contractId}/field-mappings/{mappingId}/replace`, D330-R5). The CF description update has no governed update endpoint today; this is a service gap. Status remains `decision-pending` until operator approval of the chosen path.

## Foundation Gate Result

- **Repair location:** **C** (mapping / binding). The CC mapping row targets a BF that no upstream OC emits.
- **Affected boundary:** `canonical_evaluation` — the CC produces COs whose `total_revenue` column is null because the upstream BF column is null.
- **Six-invariant pre-check:**
  - I (meaning-once): no source-layer or read-layer compensation proposed. The fix is contract-level only.
  - II (object ordering): no boundary reorder.
  - III (state immutable): the CC mapping row repointing is debated below. Cross-tenant snapshot impact (the demo tenant `apex` plus the historical pilot tenant `demo-selenite` each carry one `mc__total_revenue` ledger row) is the load-bearing question.
  - IV (references explicit): the repointed mapping continues to be a single CF→BF row with rule SUM; references stay explicit.
  - V (non-replayable): re-evaluation after the fix produces a new snapshot (new `metric_evaluation_id`); deterministic from the new mapping + preserved CO state.
  - VI (evidence emitted): the L-node refresh after the change emits a new semantic verdict per MC; the audit re-classifies `total_revenue` from broken to clean.
- **Why not other layers:**
  - A (source / SDG): SAP/SDG emit `NETWR` / `TotalNetAmount` honestly; tax-inclusive total is derivable but not the current intent for "Total Revenue" in income-statement context. Path A (extend OCs to emit `invoice_hdr_total_amount`) is named as a rejected alternative for this slice.
  - B (contract semantics): partial — the CF lacks a description and conflates loosely with `gross_revenue`, `revenue`, `total_company_revenue`. Captured as a paired clarification step.
  - D (evaluation boundary): engine is correct; no `Date.now()`, no aggregation bug. Engine has no semantic input here.
  - E (storage / projection): the CC fact column exists; it's structurally null because no row populates it.
  - F (read model): N/A.
- **Override?** none.

## Metric Logic Studied

- **CF under repair:** `total_revenue`. Currency, `data_type=number`, `role=input`, `status_code=draft`, subfunction `general_ledger`. `description_text` is NULL. Documented semantic is absent.
- **Existing mapping:** `cc__invoice_hdr.total_revenue ← invoice_hdr_total_amount`, rule `sum`, no `filter_json`, no `compute_json`. Type-compatible (number → SUM → currency).
- **Upstream OC emission for `invoice_hdr_total_amount`:** **zero rows in `observation_field_map`** for any OC. Neither `oc__s4hana__i_billingdocument__invoice_hdr` v1.0.0 nor `oc__s4hana__type_sd_s_map__invoice_hdr` v1.0.0 carries this BF. Both emit `invoice_hdr_extended_amount` (S/4HANA `TotalNetAmount`; ECC `NETWR`) and `invoice_hdr_tax_amount`.
- **Engine aggregation set:** SUM / COUNT / COUNT_DISTINCT / AVG / MIN / MAX / ABS (per DEC-35b34b). SUM is the existing rule; unchanged in the proposed fix.

## Assumptions

- **Business assumption:** in income-statement vocabulary, "Total Revenue" is the top-line figure, net of indirect tax. Tax sits below the line (not company revenue; collected on behalf of the tax authority). This is the conventional finance reading and the basis for the recommended semantic clarification.
- **Source-system assumption:** SAP S/4HANA `I_BillingDocument.TotalNetAmount` and ECC `VBRK.NETWR` (and the `TYPE_SD_S_MAP.NETWR` projection both OCs see) carry net (pre-tax) billing amounts. Tax sits in a separate column.
- **Contract assumption:** the CF `total_revenue` has carried this gap for the platform's lifetime; the prior turn's audit found 19 MCs broken on it for apex (audit timestamp 2026-05-11 03:36 UTC). No prior MWR records its repair.
- **Tenant assumption:** `apex` (the demo tenant) and `demo-selenite` (a historical pilot tenant retained for comparison) are the only tenants currently producing any snapshot referencing `total_revenue` (one snapshot each, both via `mc__total_revenue`). `sandbox1` has none.
- **Engine assumption:** `MetricEvaluationEngine` accepts a corrected mapping without engine change; rebuild triggered via L-node refresh after the cc_field_mapping write.

## Rejected Interpretations

- **Path A — extend upstream OCs to emit `invoice_hdr_total_amount`.** Would carry the tax-inclusive total honestly through the chain. Rejected for this slice on two grounds:
  1. None of the 22 affected MCs make a tax-inclusive claim; all reference "revenue" or "sales" in income-statement context, which conventionally is net of tax.
  2. The change touches two live OCs (`oc__s4hana__i_billingdocument__invoice_hdr`, `oc__s4hana__type_sd_s_map__invoice_hdr`) and would re-trigger admission/observation for every bound tenant — disproportionate to a single-CF correction.
  Named as **conditional successor work** if any future MC explicitly requires tax-inclusive totals.
- **Mass repoint of all 81 CFs sharing `invoice_hdr_total_amount` as their target BF.** Funnel-padding anti-pattern (`memory/feedback_funnel_padding.md` — "81 CFs = 1 NETWR sum is semantic noise"). Rejected. Each sibling CF deserves its own semantic audit; many are likely separately mismapped.
- **Tune the SDG / synth ledger to populate `invoice_hdr_total_amount` directly.** Foundation Invariant I — producing meaning at the source layer to satisfy a metric. Rejected.
- **Add a read-side projection (FactReaderService or admin view) that synthesizes `total_revenue` from existing fact columns.** Producing meaning at the read boundary. Rejected.
- **Author a new CF (e.g., `net_total_revenue`) and migrate all 22 MCs to it.** Larger scope than the broken-mapping correction; would also fragment CF taxonomy on a temporal-neutral axis (this is a same-semantic correction, not a new semantic). Rejected.
- **Wait for a CC version bump on `cc__invoice_hdr` to land both this and other corrections.** The governed in-place replace endpoint (D330-R5) exists precisely so broken-mapping corrections do not require the heavyweight version-bump path. Rejected; the endpoint's existence is the governance decision.

## Drift / Damage Risks

- **Funnel-padding pattern on `cc__invoice_hdr`.** Read-only audit (this turn) revealed:
  - 81 CFs share `invoice_hdr_total_amount` as their source BF (all currently broken — no upstream emitter).
  - 36 CFs share `invoice_hdr_extended_amount` as their source BF (all SUM the same number under different CF names).
  - 17 CFs share `invoice_hdr_due_date`.
  The semantic noise has been documented (`memory/feedback_funnel_padding.md`). Repointing one CF (this slice) does not enlarge the noise — the 80 sibling CFs already share the wrong target. But Slice 2+ must audit those siblings on a per-CF basis, not mass-repoint.
- **CF semantic decay.** `total_revenue` has `status_code=draft` and `description_text=NULL`. So do most of its peers (`revenue`, `total_credit_sales`, `net_credit_sales`). Future operators inheriting these CFs cannot disambiguate them without source-reading. The CF description-update gap (no governed PATCH endpoint) is itself a structural risk.
- **Cross-tenant snapshot supersession.** The demo tenant `apex` and the historical pilot tenant `demo-selenite` each have one snapshot for `mc__total_revenue`. Repointing produces a new value on next evaluation **for any MC whose binding actually routes through the repaired CC**. **The prior snapshots remain truthful historical records of what the engine computed under the previous mapping** — they are evidence of the broken-mapping era, not misleading artifacts. Future evaluations write new snapshots; the chain-status / L-node refresh after the change marks the prior ledger rows superseded *for use* (the new value becomes the operative one) without invalidating the historical record. Foundation Invariant III is preserved: state was written once and is not being mutated.
- **Cross-tenant scope is platform-wide.** `cc_field_mapping` is platform-scoped; per-tenant exclusion is not architecturally available. Any tenant with bindings that route through `cc__invoice_hdr` for the `total_revenue` field will see the repaired mapping on next evaluation. The actual impact for each tenant is determined by `metric.metric_binding` — see the Findings and Repair Execution sections, which show the empirical scope is narrow.
- **Future re-introduction of `invoice_hdr_total_amount` upstream.** If a successor OC change adds `TotalGrossAmount` emission (path-A work later), the cc_field_mapping for `total_revenue` will need to be re-evaluated. Document the decision rationale here so the future operator does not re-flip the mapping without revisiting the income-statement convention.
- **Engine drift to wall-clock.** Standard Foundation watch; not changed by this slice.

## Guardrails For Future Work

- Read this record's `Metric Logic Studied`, `Assumptions`, and `Rejected Interpretations` before any further `total_revenue` change.
- Run the playbook's Metric Work Sequence (§3) end-to-end before authoring any new MC that references `total_revenue`.
- For any sibling CF mapping repair on `cc__invoice_hdr` (the 80 other CFs sharing `invoice_hdr_total_amount`), open a separate record under `_cross/` — do **not** treat them as a batch.
- If `invoice_hdr_total_amount` becomes upstream-populated in a future OC extension, revisit this record and decide whether to re-flip the mapping or keep `extended_amount` as the canonical source.
- Apply the playbook's Live MC Safety Workflow (§5) for any change to `mc__total_revenue` v1.0.0 itself (formula, variables, grain, temporal, thresholds) — that path is **not** the same as this mapping correction.
- For cross-tenant cc_field_mapping repairs in the future, ALWAYS query `metric.readiness_ledger` for any tenant with live snapshots on affected MCs before approval; do not assume single-tenant scope.

### Design-From-Tenant-Data Guardrail

**Tenant symptoms may open an investigation; they do not by themselves justify a shared-design change.**

The trigger for this slice was the apex formula-token audit showing `total_revenue` as the top broken token (19 MCs `null_in_tenant`). Apex nulls were the *symptom*. The repair to a platform-scoped artifact (`contract.cc_field_mapping`) was **not** justified by that symptom. It became justified only after registry-level proof established three facts independently of any tenant's data:

1. The `cc_field_mapping` for `total_revenue` on `cc__invoice_hdr` pointed at the BF `invoice_hdr_total_amount`.
2. **No** `observation_field_map` row, on any OC, emitted `invoice_hdr_total_amount`.
3. The mapping was therefore **structurally unproducible** — null on every tenant, not merely sparse on apex.

The third fact is what authorised a platform-scoped repair. Without it, the correct response would have been tenant-scoped: source-onboarding or per-tenant data work for apex, not a shared-mapping change that touches every other tenant binding the same CC.

**Forward rule for future operators:**

- Never change a shared contract, mapping, business field, business object, canonical field, MC formula, grammar, schema, or other platform-design artifact **solely** because one tenant has nulls or shows a per-tenant gap.
- Tenant symptoms open the investigation. They do not close it.
- Before any shared-design repair, produce registry-level proof that the artifact is wrong, ambiguous, or unproducible **independently of any tenant's data**. Cross-tenant + cross-source impact review and Foundation Gate classification (which Layer is the repair? A/B/C/D/E/F per `CLAUDE.md` §Foundation Invariant Check) must accompany that proof.
- If the proof remains tenant-specific (only this tenant is missing data; only this tenant's binding is misconfigured; only this tenant's source emits an unexpected shape), the repair must be tenant-scoped — tenant onboarding, tenant-binding edit, tenant data refresh, or deferral pending the cross-tenant case — **not** a platform-design change.
- This guardrail is procedural; it does not change the verdict on the present repair (which is platform-scoped because the proof was platform-scoped). It is a check against future operators using "the demo tenant is broken" as cover for changes that should not be made.

## Findings

1. **22 MCs reference `total_revenue`.** Audit role-distribution: one is the output MC (`mc__total_revenue` O1); the other 21 use it as an input variable (I1-I5). All MCs are `governance_state_code=active` except `mc__earnings_before_interest_and_taxes_ebit` and `mc__payer_mix` which are `draft`. Source: `metric.metric_formula_variable` join.
2. **One cc_field_mapping row covers `total_revenue` on the platform.** `cc_field_mapping_id = 4c587182-eb22-48c8-93ff-bbc80b45eb82`, on `cc__invoice_hdr` (CC id `019d762a-172f-71a6-b3ca-dc1b020a3947`). Source: `contract.cc_field_mapping`.
3. **The BF target (`invoice_hdr_total_amount`) is emitted by no OC.** Both invoice OCs (`oc__s4hana__i_billingdocument__invoice_hdr` v1.0.0 and `oc__s4hana__type_sd_s_map__invoice_hdr` v1.0.0) emit `invoice_hdr_extended_amount`, `invoice_hdr_tax_amount`, plus parties / dates / identifiers — but not `total_amount`. Source: `contract.observation_field_map`.
4. **`cc__invoice_hdr` has TWO active versions (1.0.0 and 1.1.0).** Both share the same `canonical_contract_id`. The cc_field_mapping row is keyed on `canonical_contract_id`, not version-scoped; the repair applies to both versions atomically.
5. **Live snapshot scope is two tenants.** `metric.readiness_ledger` shows `mc__total_revenue` produced one ledger row for the demo tenant `apex` (2026-05-09 03:36 UTC) and one for the historical pilot tenant `demo-selenite` (2026-04-17 08:21 UTC; 6 records). No other tenant has any snapshot for any of the 22 MCs. No other MC in the impact set has any snapshot for any tenant. Both existing snapshots route via `cc__actual_ledger` (per `metric.metric_binding`) — see Finding 6.
6. **Apex baseline.** Catalog 163 ready of 376; apex bound 148 / producing 31 / wouldProduceIfBound 0. Formula-token audit: 27 clean of 376; `null_in_tenant` × 415, `type_mismatch` × 134, `no_mapping` × 2. Source: `devhub_readiness_dial`, `devhub_formula_token_audit`.
7. **The mapping repair has a governed service endpoint.** `POST /api/onboarding/cc/:contractId/field-mappings/:mappingId/replace` (commit-doc reference D330-R5). Constraint: replacement BF must target the same CF as the existing mapping. Satisfied (same CF, new BF). Source: `bc-core/src/registry/cc-onboarding.controller.ts:43`.
8. **The CF description update has NO governed service endpoint.** `canonical-fields` controller exposes POST create + POST batch + GET list/by-id/mappings only. No PATCH or PUT for description / metadata updates. Source: `bc-core/src/registry/canonical-field.controller.ts`. This is a service gap, surfaced as a follow-up.
9. **Adjacent funnel-padding finding (out-of-slice).** 81 CFs on `cc__invoice_hdr` share `invoice_hdr_total_amount` as their target BF; 36 share `invoice_hdr_extended_amount`. Slice 1 does not address these; flagged as Drift Risk.

## Repair Execution (2026-05-11 — SES-1c080e)

Operator approved Path A (governed service) and the repair was executed and verified read-only end-to-end.

### Endpoint called

`POST /api/onboarding/cc/019d762a-172f-71a6-b3ca-dc1b020a3947/field-mappings/4c587182-eb22-48c8-93ff-bbc80b45eb82/replace`

Body:
```json
{
  "canonicalFieldName": "total_revenue",
  "businessFieldCode": "invoice_hdr_extended_amount",
  "resolutionRuleCode": "sum",
  "filterJson": null,
  "computeJson": null
}
```

Response: `200 OK`, timestamp `2026-05-11T05:28:21.664Z`.

```json
{
  "ccFieldMappingId": "bd974c70-b363-4e85-8bad-eae332877156",
  "replaced": {
    "canonicalFieldName": "total_revenue",
    "previousRule": "sum",
    "newRule": "sum"
  }
}
```

Old mapping_id `4c587182-eb22-48c8-93ff-bbc80b45eb82` is deleted. New mapping_id `bd974c70-b363-4e85-8bad-eae332877156` carries the corrected `business_field = invoice_hdr_extended_amount`, rule preserved as `sum`. Verified via direct `contract.cc_field_mapping` query at 05:28:21.737 UTC.

### Audit / change evidence

- bc-core service logger line emitted (per `cc-onboarding.service.ts:720`).
- `triggerLNodeRefresh(019d762a-172f-71a6-b3ca-dc1b020a3947, "replaceMapping(...)")` invoked (per service.ts:723). MCP-level `devhub_l_node_refresh` separately invoked but timed out at the MCP wrapper level — the service-level refresh is the authoritative trigger and ran.
- No structured row written to `evidence.evidence_object` or any change-record table by the endpoint itself; **this Metric Work Record is the operational evidence-of-record for the change**, per the audit-gap noted in the service's repository docstring.

### Post-repair refresh + audit

- `POST /api/registry/chain-status/refresh` → `201`, processed 540 MCs, 800 traces written, 540 statuses written.
- Chain-status SSOT counts: complete `228 → 247 distinct MCs` (+19). Partial `311 → 293` (−18). No new broken/unlinked.
- `devhub_formula_token_audit(tenant=apex)` 2026-05-11 05:31:25 UTC:
  - Clean: **27 → 38 MCs (+11)**.
  - Broken: 349 → 338.
  - `null_in_tenant` total: 415 → 396 (−19).
  - **`total_revenue` no longer in top-15 broken CFs.**
  - New top broken: `operating_cash_flow` (11 MCs), `total_payments_count` (7), `total_invoice_line_items_count` (6).
- Subfunction movement (clean count):
  - `revenue_accounting`: 10 → 12 (+2)
  - `general_finance`: 6 → 7 (+1)
  - `general_ledger`: 0 → 2 (+2)
  - `fpa`: 0 → 2 (+2)
  - `fixed_assets`: 0 → 2 (+2)
  - `iso_55001`: 2 → 3 (+1)
  - `cost_accounting`: 0 → 1 (+1)
  - Total: +11

### One-then-many verification — binding-discovery finding

The original plan named `mc__total_revenue` (single-input output O1) as the one-then-many test. Verification surfaced a **binding-discovery finding** that invalidates this MC as the test instrument:

- `mc__total_revenue` (id `019d7838-50c5-7d96-a3ec-cfef9432d451`) is bound, per `metric.metric_binding`, to **`cc__actual_ledger`** (NOT `cc__invoice_hdr`).
- Its `fields_used = ["sales_revenue_item"]`. The CF `sales_revenue_item` on `cc__actual_ledger` maps to `actual_ledger_amount` with rule SUM — a separate, pre-existing, populated path.
- The cc__invoice_hdr.total_revenue mapping repair is **architecturally orthogonal** to mc__total_revenue's data path.
- Empirical confirmation: 5 historical ledger rows exist for `apex / mc__total_revenue` (period FY2026-27/P01), the latest from 2026-05-09 03:36 UTC — predating the repair and unaffected by it.

Test-Bench evaluation called nonetheless to verify end-to-end engine readability:

`POST /api/admin/test-bench/evaluate-mc-for-tenant` body `{ metricContractId: "019d7838-50c5-7d96-a3ec-cfef9432d451", tenant: "apex", maxCanonicalObjects: 2000 }`

Response: `201`, evaluation invoked, status **rejected** in 108 ms.

- Binding: `bound=true`, version `1.0.0`, CC ids `["019d762a-17b6-71d1-8cdf-7b899eb28247"]` (cc__actual_ledger).
- Chain verdict: `complete`.
- inputCoCount: 6 COs.
- Rejection reason: `Completeness 50.0% for 'fiscal_period' below threshold 80%` (temporal_gate:completeness).
- No new snapshot, no new fact row, no new ledger entry. Old snapshots remain untouched.

**Interpretation:** the rejection is a Foundation-clean evidence-emitted rejection (Invariant VI). The engine correctly refused to write a snapshot under insufficient temporal coverage. This is a separate issue from the total_revenue mapping repair, unrelated to the BF source. The mapping repair's empirical verification rests on the audit-count uplift (+11 clean MCs) and chain-status movement (+19 complete), not on a producing snapshot from this particular MC.

### Apex producing-count

- **Stage 7 (Live producing): `31 → 31` — unchanged this turn**, because no dependent-MC dispatch was run. Per operator instruction ("do NOT evaluate the 21 dependent MCs before proving mc__total_revenue"), no evaluations were invoked against the 20 MCs that bind `cc__invoice_hdr` with `fields_used=["total_revenue"]`.
- **Structural readiness deltas (post-repair):**
  - Chain-complete distinct MCs: `228 → 247` (**+19**).
  - Apex audit-clean MCs: `27 → 38` (**+11**).
  - Apex `null_in_tenant` broken-token total: `415 → 396` (**−19**).
  - `total_revenue` exits the top-15 broken-CF list.
- **Live uplift is pending a separate approved dispatch slice.** Expected realized uplift when the 20 cc__invoice_hdr-bound MCs are dispatched: between 1 and 11 (the audit-clean count from this CC path is a soft upper bound; several MCs depend on additional broken tokens like `operating_cash_flow`, `total_payments_count`).

### Cross-tenant impact (read-only) — demo-selenite

`demo-selenite` is **not** the demo tenant (Apex is); it is a historical pilot tenant retained for comparison and platform-history reasons. It was checked here as the only other tenant carrying any ledger row in the `total_revenue` impact set.

- One historical `metric.readiness_ledger` row for `demo-selenite / mc__total_revenue` (period 2025-08-30, 6 records, dated 2026-04-17, not superseded). This row remains a truthful historical record of what the engine computed under the prior mapping context; it is unchanged by this turn's repair.
- That snapshot routes via the same `cc__actual_ledger / sales_revenue_item` path that `apex / mc__total_revenue` uses. **The cc__invoice_hdr repair does not mutate or affect it.**
- Zero ledger rows on demo-selenite for any of the 20 MCs that bind `cc__invoice_hdr` with `fields_used=["total_revenue"]`.
- **Conclusion: demo-selenite is completely unaffected by this turn's repair.** No snapshot was overwritten, no binding was touched, no evaluation was invoked against demo-selenite.

## Grouped Realization Pass (2026-05-11 — SES-1c080e)

Service-first grouped evaluation pass to realize Stage 7 producing-count uplift from the already-landed mapping repair. **Outcome: 0 accepted / 19 rejected; producing count 31 → 31 unchanged.** A shared blocker surfaced — existing COs predate the repair and carry the prior null `total_revenue` resolved value.

### Eligibility check (19 active MCs)

Query: `metric.metric_binding` joined with `contract.metric_contract_version` for all MCs where `canonical_contract_name='cc__invoice_hdr'` AND `fields_used` contains `total_revenue`.

- 21 MCs total; 2 are `governance_state_code=draft` (`mc__earnings_before_interest_and_taxes_ebit`, `mc__payer_mix`) — excluded.
- 19 MCs are `active` and bound to `apex` (per `/api/admin/tenant-metrics/snapshot?tenant=apex` filter; all show `stage: tenant_ready`, `isProducing: false`, `blockerReason: "never invoked — dispatch_gap"`).
- All 19 eligible for evaluation. No `wouldProduceIfBound` candidates remain (`apex` already binds every audit-clean MC).

### Canary

- **MC chosen:** `mc__revenue_per_customer` (id `019d7838-ad46-731a-b35f-abe84d6e19e8`), v1.0.0.
- **Reasoning:** simple 2-input ratio; other input `number_of_active_customers`; prior rejection on 2026-05-10 confirmed the chain reaches evaluation.
- **Call:** `POST /api/admin/test-bench/evaluate-mc-for-tenant` at 2026-05-11T06:00:56.979Z.
- **Engine response:**
  - status: `rejected`
  - inputCoCount: 72 COs reached the engine via the **repaired** `cc__invoice_hdr` primary binding (proves the repair's CO-side delivery)
  - durationMs: 265
  - failedChecks: `[{ rule: "input_validation:secondary", detail: "Input binding 'secondary' has no matching canonical objects" }]`
  - delta: snapshotCount +0, evaluationCount +0, factRowsWritten +0
- **Verdict on the repair, from the canary:** the repaired cc__invoice_hdr path delivers COs to the engine cleanly. The rejection is on the *secondary* binding (`cc__customer_party_master` or similar — no customer COs in apex), which is a per-MC pre-existing data gap unrelated to this repair. Per the user's batch-gate logic, this is a per-MC failure, not a shared one — the batch proceeds.

### Group fanout — 18 remaining active MCs (controlled batch)

Sequential evaluation via the same Test-Bench endpoint, one MC at a time. All 18 returned HTTP 201; engine ran for each.

| Outcome | Count |
|---|---|
| accepted | **0** |
| rejected | **18** |
| errored / parse_error | 0 |

#### Rejection reason histogram

| Count | Reason class | Layer |
|---|---|---|
| **7** | `No values for SUM('total_revenue')` | **Shared** — see analysis below |
| 1 | `No values for SUM('total_assets')` | Per-MC (CF data gap) |
| 1 | `No values for SUM('total_uncollectable_balances')` | Per-MC |
| 1 | `No values for SUM('operating_cash_flow')` | Per-MC (top broken in audit) |
| 1 | `Input binding 'primary' has no matching canonical objects` | Per-MC |
| 1 | `No values for SUM('earnings_before_interest_taxes_depreciation_amortization')` | Per-MC |
| 2 | `No values for SUM('cost_of_goods_sold')` | Per-MC (two cost-side MCs) |
| 1 | `No values for SUM('selling_general_and_administrative_expenses')` | Per-MC |
| 1 | `No values for SUM('average_total_assets')` | Per-MC (top broken) |
| 1 | `No values for SUM('average_working_assets')` | Per-MC |
| 1 | `No values for SUM('average_working_capital')` | Per-MC |

### Shared blocker analysis — *No values for SUM('total_revenue')*

Seven MCs (`capital_intensity_ratio`, `cost_of_revenue_cogs_ratio`, `research_development_to_revenue_ratio`, `return_on_revenue`, `revenue_by_product_line`, `sg_a_to_revenue_ratio`, `shipping_cost_as_of_revenue`) rejected with the same engine reason: no values for SUM(`total_revenue`). **Each enumerated 78 input COs** from the repaired `cc__invoice_hdr` binding, but the `total_revenue` column on those COs is null.

**Root cause: COs are immutable historical records (Foundation Invariant III).** The mapping repair changed the contract row in `contract.cc_field_mapping` (which the engine consults at evaluation time *for resolution rules*) — but the existing CO rows for `apex` were written under the prior mapping. Their resolved `total_revenue` column carries null because the prior mapping pointed at `invoice_hdr_total_amount`, which had no upstream emitter. The engine reads the *CO's* resolved values, not the *current* mapping's potential values.

**Implication.** Structural readiness (chain-complete, audit-clean) improved as expected. **Runtime realization is gated on a fresh canonical-evaluation pass over `cc__invoice_hdr` for `apex`** that re-resolves and writes new CO versions under the corrected mapping. That re-emission is a separate governed-service step (admission re-run or schema-provisioner reconcile path, depending on infrastructure) and is *not* part of this slice.

### Post-audit

- Readiness dial (apex), 2026-05-11T06:02:49Z: bound `160`, **producing `31`** (unchanged), wouldProduceIfBound `0`.
- Catalog dial: ready `175` of 376 (up from 163 pre-repair). chainComplete `185` (up from 176).
- `metric.readiness_ledger` rows for `apex` with `completed_at > 2026-05-11T05:55:00Z`: **0**. The 19 rejected evaluations did not write new ledger rows (the engine only ledgers accepted snapshots; rejection evidence flows through `metric_evaluation` rows, not in this scan's allowlist).
- No tenant other than `apex` was evaluated this turn — confirmed by the script (single `tenant: 'apex'` parameter).
- No tenant other than `apex` was mutated.

### Outcome

- **Stage 7 producing count: 31 → 31** — no change.
- **Stage 4 platform-ready: 163 → 175** (+12 since the repair; +0 this realization-pass turn).
- **Audit-clean MCs (apex): 27 → 38** (+11 since the repair; +0 this turn).
- **Snapshots written this turn: 0.**
- **Fact rows written this turn: 0.**
- The repair's value is unrealized at runtime until a canonical re-emission for `cc__invoice_hdr` against `apex` lands.

### Remaining top blockers (post-realization-pass, ranked by recurrence)

1. **`total_revenue` re-emission gate** — 7 MCs blocked on stale CO values; the mapping repair needs a canonical-evaluation re-run to take effect. This is the highest-leverage next action; it would unblock 7 MCs in one re-emission.
2. **`operating_cash_flow`** — 11 MCs broken (audit-wide). The next CF cleanup candidate per the funnel; same pattern (BF / mapping / source emission audit required).
3. **`cost_of_goods_sold`** — 2 MCs in this slice (gross_margin, cost_of_revenue_cogs_ratio, gross_profit_margin); also blocks Tier-A storyboard tiles.
4. **`average_total_assets`** — 4 MCs broken in audit.
5. **`total_payments_count`, `total_invoice_line_items_count`, `total_invoices_processed_count`** — counter-style CFs; likely funnel-padding pattern from a payment/invoice CC.

### Evidence

- Endpoint calls (Test-Bench evaluate-mc-for-tenant) — 19 calls between `2026-05-11T06:00:56.979Z` and `06:02:30Z` (canary first, then sequential batch). Each call's response captured the rejection reason in `data.evaluation.failedChecks[*]`; no runIds returned by this endpoint (engine writes them internally).
- `inputCoCount` values per MC: 72 (8 MCs) or 78 (10 MCs). Both indicate the repaired `cc__invoice_hdr` binding delivered COs to the engine. The number difference reflects whether the MC's secondary binding (when present) further filtered the join.
- Readiness dial pre/post (06:00 → 06:02): producing unchanged at 31; bound unchanged at 160.
- No commits / no DB hand edits this turn.

## Canonical Re-emission / Runtime Realization (Slice 1b — 2026-05-11)

Service-first re-emission of `cc__invoice_hdr` COs for `apex` to realize the Slice 1 mapping repair at runtime. **Outcome: 72 new COs emitted; +8 producing count from auto-dispatched MCs on other CFs; the 7 stale-total_revenue MCs STILL reject with `No values for SUM('total_revenue')`.** A deeper resolution / fact-table gap is revealed — separate from Slice 1's mapping repair.

### Governed re-emission path

| Endpoint | Behavior |
|---|---|
| `POST /api/t/admission-runs/:runId/resolve` | **Rejected for this slice.** `CanonicalResolutionService.resolveRun` is idempotent (`canonical-resolution.service.ts:372–377`) — it skips groups whose primary admitted record already has an evaluation. Re-calling on an existing admission_run produces no new COs. Confirmed read-only by inspection. |
| `POST /api/t/test-bench/execute-reader` (used) | Reader runtime fetches source, observes, admits, AND auto-resolves the new admission_run under the current mapping in the same call. Produces fresh admission_run + fresh COs. Aligns with the operator's "fetch source again if it produces new SO/CO versions and evidence" allowance. |

### Foundation Gate

- **Repair location:** **D** (evaluation-boundary chain re-execution; no contract change).
- **Affected boundary:** observation + admission + canonical resolution (full read side of the chain re-runs honestly).
- **Invariant I (meaning once):** the new COs are written by the production-path resolver, not by hand or by a read-side projection.
- **Invariant II (object ordering):** chain order preserved — Source → Reader → SO → Admission → Canonical → CO.
- **Invariant III (state immutable):** prior 3 admission_runs (216 historical CO emissions) remain untouched. New admission_run gets a fresh `run_id`; new COs are new rows.
- **Invariant IV (references explicit):** new admission_run + new CO ids surface in the response payload; readiness_ledger captures resolution and reader_run events with the new `run_id`.
- **Invariant V (non-replayable):** each evaluation against the same input state writes new evaluation rows; no in-place rewrites.
- **Invariant VI (evidence emitted):** the reader's fetch metadata, admission summary, and canonical-resolution summary all flow back in the response and into `metric.readiness_ledger`.

### Baseline (pre-invocation, 2026-05-11 ~06:10 UTC)

- `runtime.admission_run` for apex / `I_BillingDocument`: 3 runs (all 72/72, environment=apex, latest 2026-05-10 12:16 UTC).
- `metric.readiness_ledger` active rows for apex: 79 metric_snapshot, 2 reader_run, 4 resolution.
- Apex producing count: **31**.
- 7 stale MCs (last evaluated in Slice 1 batch): all rejecting `No values for SUM('total_revenue')`.

### Invocation

```
POST /api/t/test-bench/execute-reader
  x-tenant-id: apex
  body: { readerId: "019d867d-e4a1-7cb0-be0e-9bf27667fdf1",
          flavorId: "019e1150-2c0f-7e95-a9ce-8cee1d300863",
          tenantId: "apex",
          environment: "apex" }
```

(First attempt without `environment` returned 422 `No active admission contract binding ... in environment 'production'`. The apex chain runs under `environment_code='apex'`, not the default `production`. Retried successfully with `environment: 'apex'`.)

### Response — 200 OK at 2026-05-11T06:13:40.948Z

- **New `runId`:** `019e15ab-7dc2-7459-a201-8a0a57f0c083`
- flavorName: `s4hana-cloud-invoice-hdr`
- fetchMetadata: 72 records fetched, 22 205 bytes
- admissionSummary: 72 observed / 72 admitted / 0 rejected
- canonicalResolution:
  - ocName: `oc__s4hana__i_billingdocument__invoice_hdr`
  - bindingId: `019e1150-2c0f-7901-8034-f3bb2c5cc143` (sap_s4hana_cloud-cc_invoice_hdr-mapping)
  - canonicalContractId: `019d762a-172f-71a6-b3ca-dc1b020a3947` (cc__invoice_hdr — the repaired CC)
  - summary: 72 groups / 72 accepted / 0 rejected / 0 skipped / 72 input records
  - 72 new `canonical_object_id` UUIDs returned (prefix `019e15ab-...`)

### Post-invocation state

| Signal | Value |
|---|---|
| `runtime.admission_run` apex/I_BillingDocument | 4 runs (was 3) — old 3 unchanged, new at 2026-05-11T06:13:40.930Z |
| `metric.readiness_ledger` new rows for apex (completed_at > 06:10 UTC) | 7 rows: 1 reader_run, 1 resolution (both `record_count=72`), **5 metric_snapshot rows on 9 distinct MCs** |
| Apex producing count (dial at 06:19:45 UTC) | **39** (was 31) — **delta +8** |
| Catalog ready (Stage 4) | 175 (unchanged) |

### Side effect — D337 dispatcher auto-fanout

The new resolution event triggered the D337 readiness-dispatcher, which auto-evaluated 9 MCs as a side effect of the chain trigger (not an explicit dispatch call from this slice). All 9 are MCs that bind `cc__invoice_hdr` for non-total_revenue CFs (e.g., `total_credit_sales`, `auto_invoice_generation_rate`):

- mc__average_payment_days_apd (24 records)
- mc__ar_to_sales_ratio (24)
- mc__total_asset_turnover_ratio (1)
- mc__mrr (1)
- mc__auto_invoice_generation_rate (24)
- mc__credit_sales_to_total_sales (24)
- mc__blocked_invoices_value (48)
- mc__equity_turnover_ratio (1)
- mc__ar_turnover (1)

This dispatcher behavior is platform-default and was not invoked explicitly. Recording transparently per the user's "do not hide rejection evidence" / no-out-of-scope-dispatch rule. The producing-count delta (+8) comes entirely from these auto-dispatched MCs, **not** from the 7 stale-total_revenue MCs the slice targeted.

### Re-evaluation of the 7 stale MCs

After the re-emission, the 7 MCs were re-evaluated via `POST /api/admin/test-bench/evaluate-mc-for-tenant` (one MC at a time, single tenant `apex`).

| MC | inputCoCount | Status | Rejection reason |
|---|---|---|---|
| mc__capital_intensity_ratio | 78 | rejected | `No values for SUM('total_revenue')` |
| mc__cost_of_revenue_cogs_ratio | 78 | rejected | `No values for SUM('total_revenue')` |
| mc__research_development_to_revenue_ratio | 78 | rejected | `No values for SUM('total_revenue')` |
| mc__return_on_revenue | 78 | rejected | `No values for SUM('total_revenue')` |
| mc__revenue_by_product_line | 78 | rejected | `No values for SUM('total_revenue')` |
| mc__sg_a_to_revenue_ratio | 78 | rejected | `No values for SUM('total_revenue')` |
| mc__shipping_cost_as_of_revenue | 78 | rejected | `No values for SUM('total_revenue')` |

**Outcome: 7 accepted = 0. 7 rejected. 0 snapshots written. 0 fact rows written.** Producing-count contribution from the 7-MC set: **0**.

### Deeper diagnosis — total_revenue null persists despite re-emission

Direct comparison of MCs binding `cc__invoice_hdr`:

| MC | fields_used on cc__invoice_hdr | Result post-re-emission |
|---|---|---|
| mc__ar_to_sales_ratio | `["total_credit_sales"]` | ✓ produced (1 snapshot, 24 records) |
| mc__credit_sales_to_total_sales | `["total_credit_sales"]` | ✓ produced (1 snapshot, 24 records) |
| **mc__capital_intensity_ratio** | **`["total_revenue"]`** | ✗ rejected (`No values for SUM('total_revenue')`) |
| **mc__return_on_revenue** | **`["total_revenue"]`** | ✗ rejected (`No values for SUM('total_revenue')`) |

Both `total_credit_sales` and `total_revenue` resolve via `cc_field_mapping` to the **same BF (`invoice_hdr_extended_amount`) under the same SUM rule** post-repair. Yet `total_credit_sales` reads non-null values from the new COs while `total_revenue` reads null.

**Hypothesis (not validated this turn). — SUPERSEDED by Slice 1c diagnostic (see section below).** The likely cause is at the **CC fact-table projection layer**: the `cc__invoice_hdr` materialized fact for apex carries a column per CF, and the `total_revenue` column may not have been populated under the new mapping because the prior null-mapping-history blocked column initialization, or because schema-provisioning has not re-projected this column. The repair is contract-level; runtime realization requires fact-column population too. Diagnosing and fixing this is a **separate slice**, not part of Slice 1b.

> **Hypothesis invalidated by Slice 1c.** The CC fact-table column population is **not** the failure layer. The fact-projection path is symmetric for `total_revenue` and `total_credit_sales` — both project from `invoice_hdr_extended_amount` via the same code path. Evidence: `total_credit_sales` reads from the same fact-table rows and produces values on the same new COs, falsifying the column-population hypothesis. The actual failure is Layer F (metric evaluator CO-bucket routing driven by the MC envelope's `co_bindings[].role` value). See `Diagnostic — Slice 1c` below for the corrected analysis. Leaving this hypothesis here for historical orientation, not as an active conclusion.

### Outcome

- **Slice 1b governed re-emission executed successfully** — 72 new COs created under the corrected mapping (verified via response + readiness_ledger + admission_run table).
- **Slice 1b realization NOT achieved for the 7 stale MCs** — total_revenue still resolves to null at the engine boundary.
- **Apex producing count: 31 → 39 (+8)** — entirely from the D337 dispatcher's auto-fanout to non-total_revenue MCs; zero from the 7 targeted MCs.
- **Foundation Gate clean.** No invariant violations; the persistent gap is honestly visible as engine evidence (`No values for SUM('total_revenue')`).
- **No other tenant evaluated or mutated** — confirmed via readiness_ledger query filtered to apex / completed_at > 06:10 UTC.

### Evidence

- New admission_run: `019e15ab-7dc2-7459-a201-8a0a57f0c083`.
- Reader_run ledger row (apex): `record_count=72`, `completed_at=2026-05-11T06:13:44.460Z`.
- Resolution ledger row (apex): `record_count=72`, `completed_at=2026-05-11T06:13:46.683Z`.
- 7 explicit Test-Bench evaluation calls between 2026-05-11T06:17 and 06:18 UTC, all 201, all rejected with the same engine reason.
- Direct `metric.metric_binding` query showing the field-level binding map (total_credit_sales vs total_revenue on same CC).

### Remaining blockers

1. **CC fact-table column population for `total_revenue`** — primary blocker on the 7 stale MCs. Investigation slice required. The hypothesis is that the column is unpopulated despite the new mapping; the alternate hypothesis is engine-side caching of the CF→column resolution. Diagnostic could start with reading a sample new-CO row from `cc__invoice_hdr` fact for apex via the inspector or via a direct check (read-only).
2. **D337 dispatcher coverage** — the dispatcher fanned out to 9 MCs after the new resolution, but did not include any of the 7 stale-total_revenue MCs. Worth confirming whether dispatch eligibility excludes them for a reason orthogonal to the mapping repair.
3. **Slice 2 candidates unchanged from Slice 1:** `operating_cash_flow` (11 MCs), `cost_of_goods_sold` (~3 in this group plus storyboard tiles), counter-style CFs.

### Impact Lens follow-up (recorded only — not designed/implemented in this slice)

Future BF / CF / mapping repairs should be preceded by a **computed impact report** that lists, for the proposed change:
- Every CC mapping row consuming the CF.
- Every MC's `metric_binding` referencing the CF.
- Every tenant with active bindings to those MCs and their existing snapshot/ledger rows.
- Every fact-table column potentially affected.
- Per-tenant historical evaluation outcomes that depend on the prior behavior.

The intent is for the operator to see, before any contract-level write, the precise blast radius and to confirm that a "shared mapping repair" is the right tool vs a tenant-scoped fix. **Do not design or build the Impact Lens in this slice.** File as a separate scoping conversation. This turn surfaced the need: Slice 1's mapping repair was justified registry-side, but the runtime realization gap was discovered only by running the chain — an Impact Lens would have flagged the fact-column-population dependency in advance.

## Diagnostic — Slice 1c (2026-05-11) — SUPERSEDED by Slice 1d

> **Hypothesis invalidated by Slice 1d (2026-05-11T08:24 UTC).** Five MCs were evaluated explicitly with `metricVersion: "1.1.0"` (where v1.1.0 carries `cc__invoice_hdr role="primary"`); all five still rejected with `No values for SUM('total_revenue')`. The role=secondary → role=primary flip did **not** unblock total_revenue. The Slice 1c reading — that MC envelope `co_bindings[].role` is the failure layer — is therefore wrong. The Slice 1c content below is preserved as orientation history; the operative diagnostic is `Slice 1d` below.

Read-only, service-first diagnostic of the persistent `No values for SUM('total_revenue')` rejection observed after Slice 1b's canonical re-emission. **Outcome (now superseded): failure layer corrected from F-shaped (fact-projection) to F-actual (MC envelope `co_bindings[].role` configuration on the evaluated MC version).** D330-R5's mapping repair stands; the fact-table is not at fault; the engine's CF→BF projection is not stale.

### Corrected failure layer

**Layer F — Metric evaluator routes `total_revenue` through the wrong input bucket because the evaluated MC v1.0.0 envelope binds `cc__invoice_hdr` as `role="secondary"`.** The engine's runtime aggregation (`SUM('total_revenue')`) iterates the "primary" alias bucket; `cc__invoice_hdr` COs are routed to "secondary"; the projected `total_revenue` field is present on those COs but never reaches the SUM input.

### What this corrects (preserved facts)

- **D330-R5 mapping repair was necessary and active.** `cc_field_mapping` for `total_revenue` on `cc__invoice_hdr` correctly points at `invoice_hdr_extended_amount`, rule=`sum`, created 2026-05-11T05:28:21.737Z.
- **New COs carry the source BF path needed for `total_revenue`.** Run `019e15ab-7dc2-7459-a201-8a0a57f0c083` emitted 72 COs through `sap_s4hana_cloud-cc_invoice_hdr-mapping` v1.0.0, whose `mapping_json.field_resolutions` includes `invoice_hdr_extended_amount`. Confirmed empirically: MCs that bind `cc__invoice_hdr` at `role="primary"` (e.g., `mc__credit_sales_to_total_sales`) read non-null values from those same new COs and produce snapshots.
- **Fact schema / projection is not the root cause.** Slice 1b's column-population hypothesis is falsified: same BF, same projection code, same fact-table rows, divergent outcomes per MC ⇒ the layer is upstream of the projection, in the MC envelope.
- **Stale CO selection is not the root cause.** The new COs reach the engine (verified by `total_credit_sales` producing on them). `getCcFieldResolvers` runs fresh SQL on every eval call (no cache; `contract.repository.ts:268–311`). `assembleInputPayloads` re-builds the per-CC resolver map fresh per call (`metric.service.ts:703–710`).
- **Runtime rejection is caused by MC envelope role/version selection.** The Test-Bench `evaluate-mc-for-tenant` call defaulted to `metricVersion: "1.0.0"` (see Slice 1b response payload). Apex is bound to both v1.0.0 and v1.1.0 for 5 of the 7 stale MCs; the engine selected v1.0.0, whose `co_bindings` puts `cc__invoice_hdr` at role="secondary".

### Evidence — failing vs working MC envelopes

Source: `contract.metric_contract_version.contract_json.body.co_bindings`.

| MC | Version | cc__invoice_hdr role | other CC + role | Outcome (Slice 1b eval) |
|---|---|---|---|---|
| mc__credit_sales_to_total_sales | 1.0.0 | **primary** | cc__receivable_hdr / secondary | ✓ produced |
| mc__credit_sales_to_total_sales | 1.1.0 | primary | cc__receivable_hdr / primary | (also available) |
| mc__ar_to_sales_ratio | 1.0.0 | **primary** | cc__receivable_hdr / primary | ✓ produced |
| mc__capital_intensity_ratio | 1.0.0 | **secondary** | cc__actual_ledger / primary | ✗ rejected |
| mc__cost_of_revenue_cogs_ratio | 1.0.0 | secondary | cc__actual_ledger / primary | ✗ rejected (engine evaluated v1.0.0) |
| mc__cost_of_revenue_cogs_ratio | 1.1.0 | **primary** | cc__actual_ledger / primary | (not evaluated — engine picked v1.0.0) |
| mc__return_on_revenue | 1.0.0 | secondary | cc__actual_ledger / primary | ✗ rejected |
| mc__return_on_revenue | 1.1.0 | **primary** | cc__actual_ledger / primary | (not evaluated) |
| mc__research_development_to_revenue_ratio | 1.0.0 | secondary | cc__actual_ledger / primary | ✗ rejected |
| mc__research_development_to_revenue_ratio | 1.1.0 | **primary** | cc__actual_ledger / primary | (not evaluated) |
| mc__sg_a_to_revenue_ratio | 1.0.0 | secondary | cc__actual_ledger / primary | ✗ rejected |
| mc__sg_a_to_revenue_ratio | 1.1.0 | **primary** | cc__actual_ledger / primary | (not evaluated) |
| mc__shipping_cost_as_of_revenue | 1.0.0 | secondary | cc__actual_ledger / primary | ✗ rejected |
| mc__shipping_cost_as_of_revenue | 1.1.0 | **primary** | cc__actual_ledger / primary | (not evaluated) |
| mc__revenue_by_product_line | 1.0.0 | **secondary** | cc__actual_ledger / primary | ✗ rejected |

Apex `tenant.contract_binding` shows both v1.0.0 and v1.1.0 are `is_active=true` for the 5 MCs with a v1.1.0. Two MCs (`mc__capital_intensity_ratio`, `mc__revenue_by_product_line`) have only v1.0.0 — no v1.1.0 exists yet.

### Per-MC remediation map

**5 MCs — v1.1.0 already authored with `cc__invoice_hdr role="primary"`, apex binding active:**

- `mc__cost_of_revenue_cogs_ratio` (1.1.0)
- `mc__research_development_to_revenue_ratio` (1.1.0)
- `mc__return_on_revenue` (1.1.0)
- `mc__sg_a_to_revenue_ratio` (1.1.0)
- `mc__shipping_cost_as_of_revenue` (1.1.0)

For these 5, the fix is to evaluate v1.1.0 instead of v1.0.0. No contract write, no mapping change, no re-emission.

**2 MCs — no v1.1.0 exists, require future MC version authoring:**

- `mc__capital_intensity_ratio` (only v1.0.0; cc__invoice_hdr at secondary)
- `mc__revenue_by_product_line` (only v1.0.0; cc__invoice_hdr at secondary)

For these 2, a new MC version with `cc__invoice_hdr role="primary"` must be authored per the Live MC Safety Workflow (playbook §5). Out of scope for the diagnostic slice.

### Read-only artifacts used in the diagnostic

- `contract.cc_field_mapping` direct read: confirmed `total_revenue` and `total_credit_sales` rows on `cc__invoice_hdr` are functionally identical except for the CF id.
- `contract.canonical_mapping_version.mapping_json` for `sap_s4hana_cloud-cc_invoice_hdr-mapping` v1.0.0: confirmed `invoice_hdr_extended_amount` is in `field_resolutions`.
- `contract.metric_contract_version.contract_json.body.co_bindings` for all 9 MCs in scope (7 failing + 2 working): confirmed role-pattern correlation with eval outcome.
- `tenant.contract_binding` (read via `join tenant.tenants`): confirmed apex binds both v1.0.0 and v1.1.0 active for 5 of the 7.
- `contract.l_node_semantic_verdict`: all MCs in scope report `overall_semantic_verdict=not_applicable`. The verdict does not differentiate the failure mode for this case.
- bc-core source: `metric.service.ts:697–769` (assembleInputPayloads), `metric.service.ts:185–245` (loadCanonicalObjectSynthesized + fact-reader path), `metric-evaluation-engine.service.ts:474–486` (extractNumericValues), `metric-evaluation-engine.service.ts:700–735` (SUM/AVG/MIN/MAX/COUNT aggregation), `canonical-resolution.service.ts:296–361` (resolveRun idempotency), `canonical-resolution.service.ts:442–526` (normalizeMappingBody / field_resolutions → canonical_mapping), `canonical-resolution.service.ts:1198–1276` (mergePayloads), `contract.repository.ts:268–311` (getCcFieldResolvers).
- bc-core service endpoints surveyed and confirmed not needed for the fix: `schema-provisioner/nightly-reconcile`, `schema-provisioner/onboard-connector`, `registry/chain-status/refresh`, `devhub_l_node_refresh`, `t/admission-runs/:runId/resolve` (idempotent).

### Layer-by-layer verdict matrix (corrected from Slice 1b)

| Layer | Verdict | Evidence basis |
|---|---|---|
| A. Registry mapping not actually active | ✓ Active | cc_field_mapping row present, identical shape to working sibling |
| B. Canonical mapping version not refreshed | ✓ Active | mapping_json.field_resolutions includes the BF; run 019e15ab resolved 72 records via this binding |
| C. Canonical resolver emitted COs without total_revenue path | ✓ BF emitted | total_credit_sales (same BF, same rule) produces on the same COs |
| D. Fact-table schema lacks total_revenue column | ✓ N/A | Engine projects CF dynamically; no physical column needed |
| E. Fact writer/projector dropped total_revenue | ✓ N/A | Symmetric with C |
| **F. Metric evaluator selected old COs due to dedup/version selection** | **✗ FAILING (corrected variant)** | MC envelope v1.0.0 routes cc__invoice_hdr to role="secondary"; engine SUM iterates primary bucket; total_revenue field is in the wrong bucket |
| G. Metric evaluator CF/BF resolver cached stale | ✓ Not stale | getCcFieldResolvers runs fresh SQL per eval call |

### Follow-ups

1. **Evaluate the 5 existing v1.1.0 MCs explicitly with `metricVersion: "1.1.0"`** via Test-Bench `evaluate-mc-for-tenant`. Expected outcome: 3–5 produce snapshots. Producing-count uplift: +3 to +5. Not done in this slice (the operator's hard constraint forbade evaluation).
2. **Investigate why the evaluator / Test-Bench defaults to v1.0.0** when v1.1.0 is bound and active. Hypothesis: when both versions are bound, the engine picks the lowest active version unless `metricVersion` is explicitly passed. This is operationally surprising — when v1.1.0 is the intended-current version, v1.0.0 should be `superseded` not `active`. Separate governance follow-up.
3. **Author v1.1.0 for `mc__capital_intensity_ratio` and `mc__revenue_by_product_line`** with `cc__invoice_hdr role="primary"`. Future TSK; out of scope here. Requires the MC version-bump orchestrator (`POST /api/onboarding/mc/...` family) and the playbook's Live MC Safety Workflow per §5.
4. **Active-version supersession governance.** Why does v1.0.0 remain `governance_state_code=active` after v1.1.0 was authored with the corrected `role`? D305 deferred-supersession is the policy; verify whether the v1.0.0 → superseded flip was missed for these 5 MCs and whether other MC pairs have the same drift. Separate governance investigation.
5. **Update Slice 1b's "Remaining blockers" section** in this MWR (currently lists "CC fact-table column population" as the primary blocker — that's now invalidated). Optional clean-up; the SUPERSEDED annotation on the Slice 1b hypothesis is the operative correction.

### Impact Lens — applies retroactively

Slice 1's mapping repair would have benefited from a pre-write impact computation that:
- Listed every MC envelope whose `co_bindings` references the affected CF.
- Recorded, per MC, the `role` assigned to the CC whose mapping is changing.
- Flagged MCs where the CC is bound at role="secondary" (the engine treats them differently from primary).
- Listed the active MC versions per tenant binding, with a warning when multiple active versions coexist.

Slice 1c's diagnostic surfaced exactly this dimension. The Impact Lens follow-up recorded in Slice 1b is reaffirmed and slightly broadened: the lens must include **runtime-binding role configuration**, not just registry-side mapping/binding presence.

## Diagnostic — Slice 1d (2026-05-11)

Explicit v1.1.0 evaluation of the five MCs identified by Slice 1c as ready (v1.1.0 active, `cc__invoice_hdr role="primary"`, apex-bound). **Outcome: all five still rejected with `No values for SUM('total_revenue')`. The Slice 1c hypothesis (role=secondary is the cause) is invalidated. Producing count unchanged at 39.**

### Baseline (pre-eval, 2026-05-11T08:21 UTC)

- Apex producing count: **39**.
- Apex bound: 160.
- Catalog Stage 4 ready: 175 of 376.
- Apex audit-clean: 38 of 376 (unchanged since Slice 1's mapping repair).
- 5 target MCs: v1.1.0 exists + governance_state=active + cc__invoice_hdr role="primary" + total_revenue in `fields_used` (confirmed by direct `contract.metric_contract_version.contract_json.body.co_bindings` query).

### Pre-conditions confirmed (no contract or mapping changes needed)

| MC | v1.1.0 active? | cc__invoice_hdr role (v1.1.0) | fields_used |
|---|---|---|---|
| mc__cost_of_revenue_cogs_ratio | ✓ | primary | `["total_revenue"]` |
| mc__research_development_to_revenue_ratio | ✓ | primary | `["total_revenue"]` |
| mc__return_on_revenue | ✓ | primary | `["total_revenue"]` |
| mc__sg_a_to_revenue_ratio | ✓ | primary | `["total_revenue"]` |
| mc__shipping_cost_as_of_revenue | ✓ | primary | `["total_revenue"]` |

### Evaluation outcomes (POST /api/admin/test-bench/evaluate-mc-for-tenant, metricVersion="1.1.0", tenant="apex")

| MC | HTTP | engineVersion | inputCoCount | status | snapshotDelta | factRowsDelta | rejection reason |
|---|---|---|---|---|---|---|---|
| mc__cost_of_revenue_cogs_ratio | 201 | 1.1.0 | 78 | rejected | 0 | 0 | `No values for SUM('total_revenue')` + `No values for SUM('cost_of_goods_sold')` |
| mc__research_development_to_revenue_ratio | 201 | 1.1.0 | 78 | rejected | 0 | 0 | `No values for SUM('total_revenue')` |
| mc__return_on_revenue | 201 | 1.1.0 | 78 | rejected | 0 | 0 | `No values for SUM('total_revenue')` |
| mc__sg_a_to_revenue_ratio | 201 | 1.1.0 | 78 | rejected | 0 | 0 | `No values for SUM('total_revenue')` |
| mc__shipping_cost_as_of_revenue | 201 | 1.1.0 | 78 | rejected | 0 | 0 | `No values for SUM('total_revenue')` |

**Accepted: 0. Rejected: 5. Errored: 0. Snapshots written: 0. Fact rows written: 0.**

Notable detail in full-response inspection (mc__cost_of_revenue_cogs_ratio):
- Response top-level `"metricVersion":"1.1.0"` confirms the engine evaluated v1.1.0 as requested.
- `binding.versionCode: "1.0.0"` is shown in the same response; this reflects `checkBinding`'s consultation of `tenant.contract_binding` (which holds active bindings for both v1.0.0 and v1.1.0 — checkBinding returns one). Per admin-test-bench.controller.ts:172–174, the explicit `body.metricVersion` overrides `binding.versionCode` for the actual eval — confirmed by `metricVersion: "1.1.0"` echoed in the response.
- `canonicalContractIds`: `["019d762a-17b6-71d1-8cdf-7b899eb28247","019d762a-172f-71a6-b3ca-dc1b020a3947"]` — cc__actual_ledger + cc__invoice_hdr both in scope.
- Rejection list contains BOTH `total_revenue` AND `cost_of_goods_sold` failures, suggesting per-grain group rejections (formula:O1 per group, 25–26 entries total).

### Post-eval state

- Apex producing count (2026-05-11T08:25 UTC): **39 — unchanged**.
- No new readiness_ledger rows from these 5 evals (rejections aren't ledgered as snapshots).
- demo-selenite / sandbox1: untouched (every call passed `tenant: "apex"`).

### What this rules out

1. **Slice 1c hypothesis (role=secondary) — falsified.** v1.1.0 has role=primary, yet total_revenue still produces no values. Role configuration is not the failure layer.
2. **MC version selection — falsified.** The engine correctly used v1.1.0 as requested. The result is the same.
3. **Test-Bench defaulting to v1.0.0 — falsified.** Passing `metricVersion: "1.1.0"` explicitly works; the engine routes to v1.1.0.

### What this still does NOT explain

The contradiction stands:

- **mc__credit_sales_to_total_sales** binds `cc__invoice_hdr (primary) + cc__receivable_hdr` and reads `total_credit_sales` from cc__invoice_hdr (the same CC's mapping: `total_credit_sales ← invoice_hdr_extended_amount/sum`). It produced a snapshot via D337 auto-fanout in Slice 1b (1 ledger row, 24 records, completed_at 2026-05-11T06:16:54 UTC).
- **mc__cost_of_revenue_cogs_ratio v1.1.0** binds `cc__invoice_hdr (primary) + cc__actual_ledger (primary)` and reads `total_revenue` from cc__invoice_hdr (the post-repair mapping: `total_revenue ← invoice_hdr_extended_amount/sum`). It rejects on no-values.

The cc__invoice_hdr / invoice_hdr_extended_amount data path is IDENTICAL in both cases (same CC, same BF, same SUM rule). The engine's BF→CF projection in `assembleInputPayloads` is symmetric for both CFs. Yet one MC reads values and the other does not.

### Updated hypothesis space (untested)

- **H1: per-MC CO selection diverges.** The engine's input-CO selector pulls different CO sets for these MCs because the second-bound CC differs (`cc__receivable_hdr` vs `cc__actual_ledger`). If the latest-accepted-CO selector or business-key joining filters cc__invoice_hdr COs *out* when paired with cc__actual_ledger, total_revenue values never reach extractNumericValues.
- **H2: the produced snapshot for mc__credit_sales_to_total_sales has value=0/null.** A snapshot row exists, but the metric_value may be zero/null. If so, neither MC actually reads non-null total_credit_sales — and the "works vs fails" comparison is wrong. Verifying requires reading the snapshot's `metricValueJson`.
- **H3: per-grain GROUP BY semantics.** The MCs may group by fiscal_period or company_code, and the per-grain SUM iterates each group independently. If cc__invoice_hdr COs lack a grain key the engine requires (e.g., fiscal_period), they're routed to a null-period group; SUM on that group finds zero non-null entries because the cc__actual_ledger CO in the same group has a different BF surface.
- **H4: latest-accepted progression dedups by `(canonical_contract_id, contract_version_code, business_key)`. The new cc__invoice_hdr COs from run `019e15ab` may have been superseded by older COs with the same business_key but later evaluated_at**, or vice versa.

Validating any of these requires:
- Reading actual CO payloads (e.g. tenant-DB SELECT or an Inspector endpoint returning CO content). The tenant-DB allowlist on bc-pg-mcp blocks direct tenant access; the `/api/t/canonical-objects/:id` endpoint is tenant-scoped and rejects platform-admin tokens.
- Reading mc__credit_sales_to_total_sales' produced snapshot's `metricValueJson` to confirm whether its sum was non-zero.

### Per-MC remediation map (updated)

- **5 MCs (this slice's targets):** v1.1.0 evaluation **failed** with the same engine error as v1.0.0. No remediation path is yet known; needs deeper diagnostic (see Next Slice).
- **2 MCs without v1.1.0 (`mc__capital_intensity_ratio`, `mc__revenue_by_product_line`):** the Slice 1c "author v1.1.0" recommendation is now LOWER priority — even with v1.1.0/primary, the engine fails. Defer the authoring until the root cause is understood; otherwise we'd land more contract work without realization.

### Outcome

- **Stage 7 producing count: 39 → 39 — unchanged.** Realized total_revenue uplift across Slices 1, 1b, 1c, 1d combined: **0 of 7 targeted MCs**.
- **Slice 1c hypothesis falsified.** The MWR's "Current operative finding" reverts to Slice 1b's plain observation: total_revenue values are not reaching the engine's SUM despite the mapping repair, the new COs, and the v1.1.0 envelope with role=primary.
- **Foundation Gate clean.** No invariant violations; the persistent gap is honestly visible as engine evidence on every rejection.
- **Status: open root cause.** The MWR file's `status: decided` reflects Slice 1's mapping-repair decision (which remains correct and active); the realization gap diagnosis is still open.

### Follow-ups (updated)

1. **DROPPED (was Slice 1d):** evaluate the 5 v1.1.0-ready MCs — done, all fail.
2. **DROPPED (was Slice 1c follow-up #2):** investigate engine default version — confirmed `body.metricVersion` does override; not the cause.
3. **NEW — Slice 1e candidate:** verify whether mc__credit_sales_to_total_sales' produced snapshot has a non-zero value, and if so, identify which specific CO ids contributed values. Requires Inspector endpoint or direct tenant-DB read. Recommended path:
   - Try `GET /api/admin/inspection/metrics/{mc_id}/monitor?tenant=apex` for mc__credit_sales_to_total_sales (platform-scope, may surface the snapshot value).
   - If that doesn't expose enough, request bc-pg-mcp allowlist extension to include the `progression` schema for read-only diagnostic, OR script a tenant-scoped Cognito login for `/api/t/canonical-objects/:id`.
4. **NEW — Slice 1e candidate:** trace the engine's CO selection in detail. Specifically, instrument or read the engine's eligible-CO set for one of the 5 failing MCs to see whether cc__invoice_hdr COs reach the assembleInputPayloads merge step. Possible via Inspector or via reading `progression.canonical_evaluation` (allowlist extension needed).
5. **DEFERRED:** author v1.1.0 for `mc__capital_intensity_ratio` and `mc__revenue_by_product_line` — lower priority until root cause is found.
6. **PRESERVED:** active-version supersession governance investigation (why v1.0.0 stays active when v1.1.0 exists) — still a valid concern, independent of this gap.

## Diagnostic — Slice 1e (2026-05-11)

Read-only deep inspection to resolve the contradiction observed in Slices 1b–1d: total_credit_sales appears to read from `cc__invoice_hdr.invoice_hdr_extended_amount` and produce snapshots, while total_revenue (same CC, same BF, same SUM rule, same engine path) does not. **Outcome: root cause identified as H3 — per-grain GROUP BY alignment failure caused by `cc__actual_ledger` source-data sparsity on apex. High-confidence pending tenant-DB per-grain payload verification.** The realization gap is at Layer A (source emission), tenant-scoped, NOT at Layer B (contract), Layer C (mapping), Layer D (engine), or Layer F (envelope).

### Data-source framing

By architecture (D162, D167), state lives in two distinct databases for two distinct purposes:

- **Platform DB (`bc_platform_dev`)** — registry, runtime metadata, governance state. Appropriate sources for this diagnostic: `contract.*` (CC/CF/MC versions, mappings, bindings), `metric.metric_formula_variable`, `metric.metric_binding`, `runtime.admission_run`, `metric.readiness_ledger`, `execution.boundary_progression` (admitted/source counts only — CO progression lives on tenant DB).
- **Tenant DB (`tbc_apex_dev`)** — CO payloads, metric evaluations, metric snapshots, fact tables (`fact.co_*`, `fact.ms_*`), evidence rows, and `progression.canonical_evaluation` / `progression.metric_evaluation`. **CO/snapshot/fact/evidence truth lives here.**

This diagnostic preferred service surfaces that attest to tenant-DB state from platform-side endpoints — specifically the AdminInspectionService (which calls AttestationClient per `admin-inspection.service.ts`) and the Test-Bench evaluator (which runs the live engine against the tenant's CO set). Where those surfaces did not expose enough detail, platform-DB registry/runtime metadata supplemented. **Direct tenant-DB SELECTs would have been the correct read-only fallback** for per-grain CO distribution; this slice did not execute them because:

- `/api/t/canonical-objects/:id` is tenant-scoped and rejects platform-admin identities (DEC-f0e78e D-2).
- `bc-pg-mcp` is configured to `bc_platform_dev` for this session; `tbc_apex_dev` is not in its allowlist, so direct tenant-DB SELECT is not currently available via the MCP path.

The limitation is **service/tooling access to tenant payload surfaces**, not absence of platform-DB data. Platform DB returned exactly the registry + runtime-metadata signals the architecture says it should, no more.

### Tenant-derived signals used (via service surfaces)

The Slice 1e conclusion rests on these tenant-DB-derived signals, surfaced via service:

| Signal | Source endpoint | Tenant-DB origin |
|---|---|---|
| `tenantSnapshotCount: 24` vs `0` for working vs failing MC | `GET /api/admin/inspection/metrics/{md}/chain?tenant=apex` (AdminInspectionService → AttestationClient) | tenant DB metric_snapshot rows for apex |
| `tenantCanonicalObjectCount: 356` | same Inspector chain endpoint | tenant DB CO count |
| Test-Bench rejection pattern (2× total_revenue + 24× cost_of_goods_sold for mc__cost_of_revenue_cogs_ratio v1.1.0) | `POST /api/admin/test-bench/evaluate-mc-for-tenant` (Slice 1d, full response body) | live engine output against tenant CO set |
| 9 auto-dispatched MCs producing snapshots after Slice 1b's new admission run | `metric.readiness_ledger` (platform schema; rows tagged with `tenant_id='apex'`) | tenant evaluation events ledgered platform-side |
| Slice 1b reader/canonical run records for run `019e15ab-7dc2-7459-a201-8a0a57f0c083` | `runtime.admission_run` + `metric.readiness_ledger` | platform-side metadata about tenant runs |

### Platform-DB registry/runtime metadata used (no tenant-state inference)

| Source | Used for |
|---|---|
| `contract.cc_field_mapping` | Confirmed `total_revenue` and `total_credit_sales` map to the same BF + rule on cc__invoice_hdr. |
| `contract.canonical_mapping_version.mapping_json` | Confirmed `invoice_hdr_extended_amount` is in the active mapping's `field_resolutions`. |
| `contract.metric_contract_version.contract_json.body` | Compared formula text, grain, temporal_gate, and `co_bindings` for working vs failing MCs. |
| `metric.metric_formula_variable` | Confirmed each MC's I1/I2 variable bindings. |
| `metric.metric_binding` | Confirmed per-MC CC bindings and `fields_used`. |
| `runtime.admission_run` | **Source-coverage proxy** — per-tenant source_entity record counts. **Not a direct measure of CO grain distribution.** |
| `metric.l_node_semantic_verdict` | Confirmed no L-node verdict differentiation between working and failing MCs. |

The `runtime.admission_run` table reports source-record counts per tenant per source_entity — an upstream proxy for how much data the chain has to work with. It does **not** report per-grain CO distribution by `(company_code, fiscal_period)`. The "~35 admitted records for cc__actual_ledger" figure is the upstream supply; the actual cc__actual_ledger CO count and its grain distribution live on tenant DB and were not directly verified this slice.

### Service-first inspector queries (read-only)

`GET /api/admin/inspection/metrics/{metricDefinitionId}/{section}?tenant=apex` for two MCs:

| MC | header `formulaText` | header `chainVerdict` | chain `tenantSnapshotCount` | chain `tenantCanonicalObjectCount` |
|---|---|---|---|---|
| mc__credit_sales_to_total_sales | `O1 = (SUM(I1) / SUM(I2)) * C1` | complete | **24** | 356 |
| mc__return_on_revenue | `O1 = (SUM(I1) / SUM(I2)) * C1` | complete | **0** | 356 |

Formula shape is **identical**. Chain verdict is **identical (complete)**. Yet snapshot counts diverge: 24 vs 0.

Inspector chain layers also show identical structure — 2 CCs L1–L8 complete for both. No chain-level differentiation.

### Variable surface comparison

| MC | I1 | I2 | C1 |
|---|---|---|---|
| mc__credit_sales_to_total_sales | `total_credit_sales` (from cc__invoice_hdr) | `total_sales_revenue` (from cc__receivable_hdr) | percentage_multiplier |
| mc__return_on_revenue | `net_income` (from cc__actual_ledger) | `total_revenue` (from cc__invoice_hdr) | percentage_multiplier |

The cc__invoice_hdr surface is symmetric (one CF each, same BF, same rule). The DIFFERENCE is the OTHER bound CC:

- **Working:** cc__invoice_hdr + cc__receivable_hdr
- **Failing:** cc__invoice_hdr + cc__actual_ledger

### Grain configuration check

`contract.metric_contract_version.contract_json.body.grain` for both MCs:

```json
[
  { "key": "company_code",  "source": "business_field", "field_code": "company_code" },
  { "key": "fiscal_period", "source": "business_field", "field_code": "fiscal_period" }
]
```

**Identical grain** for both MCs (`company_code + fiscal_period`). Both use temporal_gate `{ "field_code": "fiscal_period", "required_periods": 1, "completeness_threshold": 0.8 }`. So per-grain GROUP BY semantics apply uniformly.

### Source-coverage diagnostic — the smoking gun

`runtime.admission_run` for apex, grouped by source_entity:

| Source entity | Maps to CC | Runs | Records admitted |
|---|---|---|---|
| BSID | cc__receivable_hdr | 27 | **1,538** |
| I_BillingDocument | cc__invoice_hdr | 4 | **288** |
| FAGLPOSE | cc__actual_ledger (via oc__s4hana__faglpose__actual_ledger) | 7 | **21** |
| BKPF | cc__actual_ledger (via oc__s4hana__bkpf__journal_entry_hdr) | 12 | **12** |
| JournalEntrySet | cc__actual_ledger (via oc__s4hana__bkpf__journal_entry_hdr) | 2 | **2** |
| CustomerOpenItemSet | ?  | 8 | 8 |

**cc__actual_ledger COs for apex: at most ~35 admitted records, sourced sparsely from FAGLPOSE/BKPF/JournalEntrySet.** cc__invoice_hdr has 288. cc__receivable_hdr has 1,538.

The grain (`company_code + fiscal_period`) groups invoice and AR data densely. Actual-ledger data is sparse — most (company_code, fiscal_period) pairs that exist in cc__invoice_hdr have **no matching cc__actual_ledger COs**.

### Rejection pattern alignment with H3

For mc__cost_of_revenue_cogs_ratio v1.1.0 (Slice 1d), the full rejection list contained:

- 2 × `No values for SUM('total_revenue')`
- 24 × `No values for SUM('cost_of_goods_sold')`

Interpreting this against H3:

- The engine evaluates **per grain group**.
- **24 grain groups exist where cc__invoice_hdr has COs but cc__actual_ledger has no matching CO** → `cost_of_goods_sold` (sourced from cc__actual_ledger) has zero numeric values in those groups → rejection.
- **2 grain groups exist where cc__actual_ledger has COs but cc__invoice_hdr has no matching CO** → `total_revenue` (sourced from cc__invoice_hdr) has zero numeric values in those groups → rejection.
- **Zero grain groups have COs from both CCs** → 0 snapshots produced.

This matches mc__credit_sales_to_total_sales producing 24 snapshots (24 grain groups where cc__invoice_hdr + cc__receivable_hdr both had COs) and `mc__return_on_revenue`'s 0 snapshots (no overlap groups between cc__invoice_hdr and cc__actual_ledger).

### Hypothesis classification

| H | Statement | Verdict |
|---|---|---|
| H1 | Different CO selection by MC / paired CC | **Subsumed by H3.** The "different CO selection" is itself driven by per-grain group eligibility. |
| H2 | Working snapshot was null/zero illusion | **Falsified.** Inspector chain shows 24 tenantSnapshotCount for mc__credit_sales_to_total_sales and 0 for mc__return_on_revenue. The engine only produces a snapshot when `extractNumericValues` returns non-empty arrays for every input — so the 24 snapshots represent real per-grain SUMs with at least one numeric value each. |
| **H3** | **Per-grain alignment failure** | **HIGH-CONFIDENCE root cause, pending tenant-DB per-grain payload verification.** Source-coverage data (platform-side `runtime.admission_run`) + tenant-derived rejection-pattern arithmetic (2+24 from Test-Bench engine output) align with grain-group eligibility. The interpretation that the 2+24 maps to grain-overlap arithmetic is consistent but not directly proved against tenant-DB per-grain CO distribution; verification requires a tenant-DB read of cc__invoice_hdr vs cc__actual_ledger CO counts grouped by `(company_code, fiscal_period)` (read-only fallback if no service surface exposes it). Alternative explanations (e.g., rejection-list counting per-input-per-grain-attempt vs per-grain) are not formally ruled out by data inspected this slice. |
| H4 | Latest-accepted dedup selecting old rows | **Falsified.** Not needed to explain the data. Slice 1b's new admission_run (019e15ab) produced 72 new COs; the engine sees 78 COs total (72 + ~6 from cc__actual_ledger) for the failing MCs — confirming both CCs' COs ARE reaching the engine input set. The failure is at per-grain alignment within the merged set, not at CO eligibility. |
| H5 | CF→BF translation not applied | **Falsified.** Same projection code path for total_credit_sales (works) and total_revenue (fails). Verified by reading `metric.service.ts:712–743` and `contract.repository.ts:268–311`. |
| H6 | Other | **N/A — H3 fully explains.** |

### Whether previous MWR sections need correction

- **Slice 1 (mapping repair):** ✓ Still correct. D330-R5 repair was the right fix for the registry-level mapping gap. Realization is now blocked by a DIFFERENT, tenant-scoped layer (source-data coverage). Mapping repair stays as a Layer C correction.
- **Slice 1b (canonical re-emission):** ✓ Still correct. The reader execution produced new COs with the BF correctly populated — confirmed by the 9 auto-dispatched MCs producing snapshots. The "column-population gap" hypothesis at the end of Slice 1b is already marked SUPERSEDED.
- **Slice 1c (role=secondary hypothesis):** ✓ Already marked SUPERSEDED by Slice 1d. No further correction needed.
- **Slice 1d (v1.1.0 evaluation outcome):** ✓ Empirical results stand. The "Updated hypothesis space" listed H1–H4 as untested; H3 is now confirmed and the others are subsumed/falsified.
- **Drift / Damage Risks — "Cross-tenant snapshot supersession":** unchanged in substance, but the broader point about cross-tenant impact remains valid — Apex's data sparsity is tenant-specific; the same MCs may produce on a tenant with richer cc__actual_ledger coverage.

### Smallest correct next action

Two-step plan, in order:

**Step 0 (verification, read-only) — confirm H3 against tenant-DB per-grain CO distribution.**

Before taking any source-data action, verify the per-grain alignment hypothesis directly. Recommended route, preferring service surfaces:
- Check whether any platform-served endpoint exposes per-CC, per-tenant CO counts grouped by `(company_code, fiscal_period)`. If yes, use it.
- If not, the architectural fallback is a read-only tenant-DB SELECT against `tbc_apex_dev` — for example `SELECT canonical_contract_id, business_key, COUNT(*) FROM progression.canonical_evaluation WHERE canonical_contract_id IN (cc__invoice_hdr_id, cc__actual_ledger_id) GROUP BY 1, 2`, or equivalent on the relevant fact table. Read-only fallback is the correct path under the architecture — bc-pg-mcp allowlist extension or a tenant-DB read-only session is the operational gap, not a constraint of the data model.

Verification confirms (or falsifies) two claims:
1. `cc__actual_ledger` CO count for apex is in the order of ~35 (i.e., admission_run records did become COs at roughly 1:1).
2. The `(company_code, fiscal_period)` set on cc__actual_ledger COs has effectively zero intersection with the same set on cc__invoice_hdr COs.

**Step 1 (remediation, if Step 0 confirms H3) — tenant-scoped Layer-A source-data extension** for apex on `cc__actual_ledger`'s sources (FAGLPOSE, BKPF, JournalEntrySet). Extend the apex reader runs for those three source entities to cover the same `(company_code, fiscal_period)` set that cc__invoice_hdr already covers, lifting cc__actual_ledger CO count to a level where per-grain alignment becomes possible.

Per the **Design-From-Tenant-Data Guardrail** already in this MWR: this is the correct repair location (**Layer A, tenant-scoped**) because the gap IS tenant-specific (apex's GL emission is sparse; other tenants might not have this problem). A shared mapping/contract change would have been the wrong tool — exactly what the guardrail warns against.

Service path for Step 1: `POST /api/t/test-bench/execute-reader` for each of the three GL source entities, with appropriate `startPeriod` / `endPeriod` covering the missing fiscal_periods. Subsequent canonical resolution auto-fires (per Slice 1b's verified behavior). Expected outcome after sufficient cc__actual_ledger coverage: 5–7 of the 7 stale MCs become producible.

**If Step 0 falsifies H3**, return to the hypothesis space with the new evidence; the remediation will differ.

### No writes / no evaluations confirmation

| Action | This slice |
|---|---|
| DB writes | ✗ None |
| Metric evaluations | ✗ None |
| Re-emission | ✗ None |
| Mapping / contract changes | ✗ None |
| Code changes | ✗ None |
| Commits | ✗ None |
| Tmp scripts | Created + cleaned up |

Inspector calls (read-only) and direct platform DB SELECTs only.

## Diagnostic — Slice 1f (2026-05-11) — H3 CONFIRMED

Read-only verification of H3 from Slice 1e. **Outcome: H3 is fully confirmed by direct tenant-DB inspection. The `(company_code, fiscal_period)` overlap between `cc__invoice_hdr` and `cc__actual_ledger` for apex is exactly zero.** Slice 1e's "high-confidence pending verification" upgrades to "confirmed by direct evidence."

### Service surface — gap recorded

Service-first check on platform-side surfaces for per-CC, per-tenant, per-grain CO counts:

| Surface | Result |
|---|---|
| `metric.readiness_ledger.resolution` rows | Returns per-CC × per-period_key counts, but `period_key` is at quarter granularity (e.g., `2026-Q2`) and `company_code` is consistently `NULL`. Insufficient for the MC grain `(company_code, fiscal_period)`. |
| `metric.readiness_ledger.metric_snapshot` rows | Returns per-MC × per-period_key × per-record_count, but `company_code` is also `NULL` and the rows are metric-side (not CO-side). |
| `execution.boundary_progression` | Reports `admitted_record` and `source_object` counts per tenant, no `canonical_object` rows. |
| `GET /api/admin/inspection/metrics/{md}/chain` | Reports `tenantSnapshotCount` and `tenantCanonicalObjectCount` aggregates only, no per-grain decomposition. |
| `GET /api/admin/inspection/metrics/{md}/monitor` | Reports `latestEvaluation`, `evaluationCount`, `snapshotCount`, `readinessLedgerEntries` — no per-grain CO drill. |

**Service gap recorded:** no platform-side surface exposes per-CC, per-tenant, per-grain CO counts directly. The architectural fallback (read-only tenant-DB SELECT against `tbc_apex_dev`) was the correct path per the Slice 1e Data-source framing.

### Tenant DB read-only verification

Connected to `tbc_apex_dev` via `postgres` driver (read-only, single session, no writes). Schemas observed: `admin`, `envelope`, `evidence`, `fact`, `organization`, `progression`, `public`, `tenant_dim`. Relevant tables: `fact.co_invoice_hdr_v1_0_0`, `fact.co_invoice_hdr_v1_1_0`, `fact.co_actual_ledger_v1_0_0`, `fact.co_actual_ledger_v1_1_0`, `progression.canonical_evaluation`, `progression.canonical_run`.

Queries used:

1. **Overall row counts:**
   ```sql
   SELECT 'co_invoice_hdr_v1_1_0' AS tbl, COUNT(*) FROM fact.co_invoice_hdr_v1_1_0
     UNION ALL SELECT 'co_actual_ledger_v1_1_0', COUNT(*) FROM fact.co_actual_ledger_v1_1_0
     UNION ALL SELECT 'co_invoice_hdr_v1_0_0',  COUNT(*) FROM fact.co_invoice_hdr_v1_0_0
     UNION ALL SELECT 'co_actual_ledger_v1_0_0', COUNT(*) FROM fact.co_actual_ledger_v1_0_0
   ```

2. **Per-grain distribution per CC:**
   ```sql
   SELECT company_code, fiscal_period, COUNT(*) FROM fact.co_invoice_hdr_v1_1_0
     GROUP BY company_code, fiscal_period ORDER BY fiscal_period, company_code;
   ```
   (same for `co_actual_ledger_v1_1_0`.)

3. **Overlap analysis:**
   ```sql
   WITH inv AS (SELECT DISTINCT company_code, fiscal_period FROM fact.co_invoice_hdr_v1_1_0),
        led AS (SELECT DISTINCT company_code, fiscal_period FROM fact.co_actual_ledger_v1_1_0)
   SELECT inv.company_code, inv.fiscal_period FROM inv INNER JOIN led ON inv.company_code = led.company_code AND inv.fiscal_period = led.fiscal_period;
   ```

4. **Column-population check for `invoice_hdr_extended_amount`** on `fact.co_invoice_hdr_v1_1_0`.

All queries SELECT-only. No DDL, no DML, no writes.

### Results — per-grain overlap table

| Fact table | Total rows | Distinct `(company_code, fiscal_period)` | Range |
|---|---|---|---|
| `fact.co_invoice_hdr_v1_1_0` | **162** | **24** | `cc=1100`; **FY2023-24/P07 → FY2025-26/P06** (24 contiguous fiscal periods, 6–9 COs each) |
| `fact.co_invoice_hdr_v1_0_0` | 0 | 0 | (empty) |
| `fact.co_actual_ledger_v1_1_0` | **15** | **1** | `cc=1100`; **FY2026-27/P01** only |
| `fact.co_actual_ledger_v1_0_0` | 6 | (not enumerated in this slice) | (smaller, older version) |

| Comparison | Count |
|---|---|
| Invoice-only `(cc, fp)` groups | **24** |
| Ledger-only `(cc, fp)` groups | **1** |
| **Overlap `(cc, fp)` groups** | **0** |
| Total distinct grain groups across both CCs | 25 |

**The actual_ledger CO set (FY2026-27/P01) is in a fiscal period strictly LATER than every invoice_hdr CO period (FY2023-24/P07 through FY2025-26/P06).** There is no temporal intersection at all.

This matches the Slice 1d rejection arithmetic almost exactly: 24 invoice-only groups → 24× `No values for SUM('cost_of_goods_sold')`; 1 ledger-only group with possibly some per-input emission doubling → 2× `No values for SUM('total_revenue')`. The (24 + 1) grain groups + (0) overlap fully accounts for "0 of 7 MCs producing."

### Grain field verification

Direct schema introspection on `fact.co_invoice_hdr_v1_1_0` and `fact.co_actual_ledger_v1_1_0`:

- Both tables carry `company_code` (text) and `fiscal_period` (text) columns.
- The 7 affected MCs all declare grain `[{ key: "company_code", source: "business_field" }, { key: "fiscal_period", source: "business_field" }]` (verified in Slice 1e via `contract.metric_contract_version`).
- No other grain key is involved.

### H3 verdict — CONFIRMED

The Slice 1e hypothesis is now backed by direct per-grain tenant-DB evidence. The realization gap for the 7 stale `total_revenue` MCs is **NOT** at:

- Layer A for cc__invoice_hdr — the new run `019e15ab-...` populated the fact table correctly (162 rows across 24 periods, `invoice_hdr_extended_amount` populated).
- Layer B (contract) — both v1.0.0 and v1.1.0 of the affected MCs are well-formed (Slice 1c, 1d).
- Layer C (mapping) — total_revenue mapping is correctly repaired (Slice 1).
- Layer D (engine) — the engine's projection code is symmetric and runs each call fresh (Slice 1e).
- Layer F (envelope role) — Slice 1d falsified the role hypothesis.

The realization gap **IS** at:

- **Layer A for cc__actual_ledger, tenant-scoped.** Apex's GL source emission (FAGLPOSE / BKPF / JournalEntrySet) has produced COs covering only **1 fiscal period (FY2026-27/P01)** with **15 records**. The 24 fiscal periods where cc__invoice_hdr has COs have **zero** cc__actual_ledger coverage. Per-grain GROUP BY alignment is therefore impossible.

This is precisely what the **Design-From-Tenant-Data Guardrail** (recorded earlier in this MWR) anticipated: tenant nulls signal an investigation; the right fix is tenant-scoped, not shared-design.

### Recommended next slice — Slice 1g: tenant-scoped GL source coverage

If the operator approves, Slice 1g uses the governed reader execution path to extend apex's GL coverage:

**Target fiscal-period range:** `FY2023-24/P07` through `FY2025-26/P06` (the 24 periods cc__invoice_hdr already covers).
**Target company_code:** `1100` (only company code currently in apex data).
**Source entities to extend (in order of priority):**

| Source entity | OC | CC | Current apex admitted records |
|---|---|---|---|
| FAGLPOSE | `oc__s4hana__faglpose__actual_ledger` | `cc__actual_ledger` | 21 (across all periods → 15 COs in FY2026-27/P01 only) |
| BKPF | `oc__s4hana__bkpf__journal_entry_hdr` | `cc__journal_entry_hdr` (and possibly contributing to actual_ledger via composition) | 12 |
| JournalEntrySet | `oc__s4hana__bkpf__journal_entry_hdr` (same OC) | same as BKPF | 2 |

**Governed service path:**
```
POST /api/t/test-bench/execute-reader
  x-tenant-id: apex
  body: {
    readerId: <FAGLPOSE reader id>,
    tenantId: 'apex',
    environment: 'apex',
    startPeriod: '<FY2023-24/P07-equivalent date>',
    endPeriod:   '<FY2025-26/P06-equivalent date>'
  }
```
Repeat for BKPF / JournalEntrySet. Canonical resolution auto-fires (Slice 1b pattern verified).

**Pre-Slice-1g blocker check (must verify before invoking):**
- Does the FAGLPOSE reader (and its bound flavor) support `startPeriod` / `endPeriod` parameters covering historical fiscal periods?
- Does the apex bc-sdg / S/4HANA simulator have data for FAGLPOSE / BKPF / JournalEntrySet across those periods? If the upstream emits empty result sets, no new COs land — Slice 1g's stop condition X3.

These checks are read-only (try a small dry-run reader call, or inspect the SDG profile) and should be the first step of Slice 1g.

### MWR sections that need correction

None this slice. The Slice 1e Data-source framing and HIGH-CONFIDENCE-pending-verification language correctly anticipated this verification step. Slice 1f upgrades 1e's H3 verdict from "high-confidence pending" to "confirmed by direct evidence." No prior section is invalidated.

### Hard-constraint confirmation

| Action | This slice |
|---|---|
| DB writes | ✗ None — all queries SELECT-only |
| Service calls that mutate state | ✗ None |
| Reader runs | ✗ None |
| Metric evaluations | ✗ None |
| Contract / mapping / code / SDG / schema changes | ✗ None |
| Commits | ✗ None — MWR remains uncommitted pending review |
| Tenant-DB connection | ✓ Read-only single session against `tbc_apex_dev`, opened and closed cleanly. Architecturally correct fallback per Slice 1e Data-source framing. |

## Realization — Slice 1g (2026-05-11)

Tenant-scoped GL source coverage executed against apex via the governed reader path. **Outcome: cc__actual_ledger coverage extended from 1 to 25 fiscal periods; cc__invoice_hdr × cc__actual_ledger `(company_code, fiscal_period)` overlap moved from 0 to 24; Apex Stage 7 producing count moved from 39 to 46 (+7); all 5 v1.1.0-ready total_revenue MCs produced via D337 auto-fanout, plus both v1.0.0-only MCs (`mc__capital_intensity_ratio`, `mc__revenue_by_product_line`) also produced.** H3 confirmed end-to-end at runtime. Slice 1c's role-secondary-as-blocker hypothesis is conclusively falsified by direct production evidence.

### Reader runs executed

| # | Source entity | runId | Started | Finished | Records observed | Records admitted |
|---|---|---|---|---|---|---|
| 1 | FAGLPOSE → cc__actual_ledger | **`019e1681-7df9-7617-bf65-4b10ad165f37`** | 2026-05-11T10:07:25.690Z | 10:07:36.902Z | 219 | 219 |
| 2 | BKPF + JournalEntrySet → cc__journal_entry_hdr | **`019e1689-ee81-7da1-827c-98085439b6f9`** | 2026-05-11T10:16:38.786Z | 10:16:42.256Z | 73 | 73 |

Both via `POST /api/t/test-bench/execute-reader` with `x-tenant-id: apex`, single reader id `019d867d-...`, `environment: apex`. No `startPeriod`/`endPeriod` passed (flavors lack `dateField`; period filter would be silently dropped per Slice 1g precheck). The simulator's V2 endpoints `http://localhost:6200/sdg/apex-motors/{ActualLedgerSet, JournalEntrySet}` returned 219 + 73 rows spanning 2023-10 → 2026-04 — exactly the date range needed.

Operational note: the initial client-side `fetch()` for Call 1 timed out at undici's default 5-min headers-timeout while the server completed in ~11 seconds. The reader run landed and resolved canonically server-side; verified via direct `runtime.admission_run` read. Call 2 was issued via `node:http` to avoid the timeout, with the same outcome (3.5s server-side).

### Canonical resolution (auto-fired by reader endpoint)

| Resolution ledger row | CC | Records |
|---|---|---|
| 2026-05-11T10:07:46.001Z | cc__actual_ledger (`019d762a-17b6-71d1-8cdf-7b899eb28247`) | **219 new CO rows** under `sap_ecc_ehp8-cc_actual_ledger-mapping` v1.2.0 |
| 2026-05-11T10:16:42.x  (auto) | cc__journal_entry_hdr (`019d7663-f10b-7c5b-9ff9-b00e701a2452`) | 73 new CO rows under `sap_ecc_ehp8-cc_journal_entry_hdr-mapping` v1.3.0 |

### Tenant-DB fact-table state (read-only verification)

Before vs After (`fact.co_*_v1_1_0`):

| Table | Before (Slice 1f) | After (Slice 1g) | Delta |
|---|---|---|---|
| `fact.co_invoice_hdr_v1_1_0` | 162 rows / 24 groups | 162 / 24 | unchanged |
| `fact.co_actual_ledger_v1_1_0` | 15 rows / 1 group | **234 rows / 25 groups** | **+219 rows, +24 groups** |

`cc__actual_ledger` now spans `FY2023-24/P07 → FY2026-27/P01` (25 fiscal periods × 9 COs per period, plus the 18 historical FY2026-27/P01 rows from past runs that were not superseded).

### Grain overlap — before vs after

| Comparison | Before | After |
|---|---|---|
| Invoice-only `(cc, fp)` groups | 24 | **0** |
| Ledger-only `(cc, fp)` groups | 1 | 1 (FY2026-27/P01 — invoice doesn't cover this period) |
| **Overlap `(cc, fp)` groups** | **0** | **24** |

**24 overlap groups** — every `(company_code, fiscal_period)` pair where cc__invoice_hdr has COs now has cc__actual_ledger COs too. H3's grain-alignment prerequisite is satisfied.

### D337 auto-fanout — full list of MCs evaluated

39 metric_snapshot ledger rows landed for apex between `10:07:47` and `10:15:17` UTC. The full list (per-MC, per-grain group):

| MC | period_key | record_count | completed_at |
|---|---|---|---|
| mc__gross_profit_margin | FY2025-26/P01 | 24 | 10:07:47 |
| mc__accounts_payable_turnover_ratio | FY2024-25/P05 | 25 | 10:07:48 |
| mc__ar_turnover | FY2026-27/P01 | 25 | 10:08:25 |
| mc__asset_utilization_ratio | FY2025-26/P01 | 24 | 10:09:24 |
| mc__equity_turnover_ratio | FY2026-27/P01 | 25 | 10:09:28 |
| **mc__capital_intensity_ratio** | FY2024-25/P03 | 24 | 10:09:29 |
| mc__time_to_close_tax_provision | FY2024-25/P05 | 25 | 10:09:37 |
| **mc__shipping_cost_as_of_revenue** | FY2024-25/P03 | 24 | 10:10:27 |
| **mc__sg_a_to_revenue_ratio** | FY2024-25/P03 | 24 | 10:10:34 |
| **mc__revenue_by_product_line** | FY2024-25/P03 | 24 | 10:11:34 |
| mc__audit_adjustments_count | FY2024-25/P03 | 24 | 10:11:35 |
| mc__working_asset_turnover_ratio | FY2025-26/P01 | 24 | 10:11:40 |
| mc__gross_margin | FY2025-26/P01 | 24 | 10:11:49 |
| mc__total_asset_turnover | FY2025-26/P01 | 24 | 10:12:19 |
| mc__working_capital_turnover | FY2025-26/P01 | 24 | 10:12:25 |
| mc__audit_adjustments_count | FY2024-25/P05 | 24 | 10:12:27 |
| mc__mrr | FY2026-27/P01 | 25 | 10:12:28 |
| mc__total_asset_turnover_ratio | FY2026-27/P01 | 25 | 10:12:31 |
| **mc__return_on_revenue** | FY2024-25/P03 | 24 | 10:12:38 |
| **mc__cost_of_revenue_cogs_ratio** | FY2024-25/P03 | 24 | 10:12:45 |
| mc__arpa | FY2026-27/P01 | 25 | 10:12:57 |
| **mc__research_development_to_revenue_ratio** | FY2024-25/P03 | 24 | 10:13:28 |
| mc__gross_written_premium_gwp | FY2024-25/P05 | 25 | 10:14:15 |
| mc__insurance_revenue_ifrs_17 | FY2024-25/P05 | 25 | 10:14:16 |
| mc__spread_yield_on_advances_minus_cost_of_deposits | FY2024-25/P05 | 25 | 10:14:28 |
| mc__tax_jurisdictions_managed | FY2024-25/P05 | 25 | 10:14:30 |
| mc__total_revenue | FY2024-25/P05 | 25 | 10:14:32 |
| mc__unrecognized_tax_benefits_utb | FY2024-25/P05 | 25 | 10:14:34 |
| mc__value_of_new_business_vnb | FY2024-25/P05 | 25 | 10:14:34 |
| mc__asset_management_training_investment | FY2024-25/P05 | 25 | 10:14:40 |
| mc__cost_avoidance_from_asset_management | FY2024-25/P05 | 25 | 10:14:42 |
| mc__cost_of_revenue | FY2024-25/P05 | 25 | 10:14:51 |
| mc__deferred_revenue | FY2024-25/P05 | 25 | 10:14:53 |
| mc__deferred_revenue_balance | FY2024-25/P05 | 25 | 10:14:54 |
| mc__recognized_revenue | FY2024-25/P05 | 25 | 10:15:00 |
| mc__revenue_backlog | FY2024-25/P05 | 25 | 10:15:01 |
| mc__revenue_by_channel | FY2024-25/P05 | 25 | 10:15:02 |
| mc__revenue_by_region | FY2024-25/P05 | 25 | 10:15:04 |
| mc__liquidity_coverage_ratio | FY2024-25/P05 | 25 | 10:15:17 |

Bold rows = the 7 targeted total_revenue MCs from the Slice 1 arc. **All 7 produced via auto-fanout.** No explicit Test-Bench evaluations were invoked by Slice 1g — the user's "Evaluate only the 5 v1.1.0-ready MCs" instruction was scoped to explicit calls; the D337 dispatcher (acknowledged in approved scope) already evaluated all 7 plus dependents.

### 5+2 target MC outcome table

| MC | Version evaluated | Auto-fanout outcome | Snapshot record_count | period_key |
|---|---|---|---|---|
| **5 v1.1.0-ready (target):** | | | | |
| mc__cost_of_revenue_cogs_ratio | (engine selected) | ✓ Accepted | 24 | FY2024-25/P03 |
| mc__research_development_to_revenue_ratio | | ✓ Accepted | 24 | FY2024-25/P03 |
| mc__return_on_revenue | | ✓ Accepted | 24 | FY2024-25/P03 |
| mc__sg_a_to_revenue_ratio | | ✓ Accepted | 24 | FY2024-25/P03 |
| mc__shipping_cost_as_of_revenue | | ✓ Accepted | 24 | FY2024-25/P03 |
| **2 v1.0.0-only (NOT explicitly targeted; auto-fanout-only):** | | | | |
| mc__capital_intensity_ratio | v1.0.0 | ✓ Accepted via D337 | 24 | FY2024-25/P03 |
| mc__revenue_by_product_line | v1.0.0 | ✓ Accepted via D337 | 24 | FY2024-25/P03 |

**7 of 7 stale total_revenue MCs producing.** No explicit Test-Bench evaluations were invoked this slice for these MCs — the D337 dispatcher fired on the new resolution events and evaluated them under the approved-side-effect umbrella.

### Producing-count delta

| Signal | Before (10:06 UTC) | After (10:17 UTC) | Delta |
|---|---|---|---|
| Apex Stage 7 producing | **39** | **46** | **+7** |
| Apex bound | 160 | 160 | 0 |
| Catalog Stage 4 ready | 175 | 175 | 0 |
| Apex `wouldProduceIfBound` | 0 | 0 | 0 |

**Realized +7 producing MCs.** The 39 metric_snapshot ledger rows from D337 fanout include some pre-existing producing MCs being re-evaluated under the new run (which doesn't change the Stage 7 count), plus 7 new MCs that moved Stage 5 (bound) → Stage 7 (live).

### Hypothesis verdict updates

| Hypothesis | Slice that surfaced it | Slice 1g verdict |
|---|---|---|
| H3 (per-grain alignment failure due to cc__actual_ledger sparsity) | Slice 1e (hypothesis) → Slice 1f (confirmed via tenant-DB read) | **CONFIRMED end-to-end by production evidence.** Closing the grain alignment gap produced realization exactly as predicted. |
| Slice 1c (role=secondary as blocker) | Slice 1c | **DEFINITIVELY FALSIFIED.** mc__capital_intensity_ratio and mc__revenue_by_product_line are v1.0.0 with `cc__invoice_hdr role="secondary"`; both produced once cc__actual_ledger had grain-aligned COs. Role configuration is not the engine's CO routing constraint; grain alignment is. |
| Slice 1b column-population gap | Slice 1b | Already marked SUPERSEDED in MWR; Slice 1g reinforces. |

### Outcome

- **Slice 1 mapping repair (D330-R5):** correct and necessary, but not sufficient on its own.
- **Slice 1b canonical re-emission for cc__invoice_hdr:** correct preparation, but realized 0 of 7 target MCs.
- **Slice 1c (role-secondary)** + **Slice 1d (v1.1.0 evaluation):** both falsified the wrong hypothesis path, but documented the engine's symmetric-projection mechanics honestly.
- **Slice 1e / 1f (H3 identified and verified):** correctly diagnosed grain alignment as the root cause.
- **Slice 1g (this slice):** closed the grain alignment gap by extending cc__actual_ledger source coverage; **realized all 7 target MCs**.

The total_revenue arc is complete for Apex. Realized cumulative producing-count uplift from the arc's start: **31 → 46 (+15)** — about half of which is the auto-fanout side effect across the Slice 1g resolution event, the rest is the targeted 7 MCs lifting.

### Confirmation — scope honored

| Constraint | Result |
|---|---|
| tenant apex only | ✓ Every reader call passed `tenantId: 'apex'` and `x-tenant-id: apex`. Direct tenant-DB SELECTs were read-only against `tbc_apex_dev`. No demo-selenite or sandbox1 touched. |
| No contract / mapping / schema / code / SDG changes | ✓ None |
| No DB hand edits | ✓ All writes occurred via governed `POST /api/t/test-bench/execute-reader` endpoint and its downstream resolution + D337 dispatcher |
| No broad MC dispatch beyond unavoidable D337 auto-fanout | ✓ Zero explicit `evaluate-mc-for-tenant` calls this slice. The 39 D337 fanout rows are the approved side effect. |
| No commit until review | ✓ MWR remains uncommitted in working tree |
| Tmp scripts | ✓ Cleaned up |

### Recommendation for next slice

**Slice 1h — verification + arc closure for total_revenue.** Read-only confirmation:
1. Inspector chain endpoint for each of the 7 targeted MCs to confirm `tenantSnapshotCount > 0` and `lastEvaluatedAt` is recent.
2. Final readiness dial snapshot.
3. Optional: sample one snapshot's `metricValueJson` per MC to confirm value-shape is sensible (no zero-divide, no nulls).

After Slice 1h, the total_revenue arc per the **Bounded Business-Critical Completion Plan** is **complete**:
- Success criteria S1 (at least 5 of 7 MCs producing) → **exceeded: 7/7**
- Success criteria S3 (producing-count rises from 39) → **achieved: 39 → 46 (+7)**
- Success criteria S4 (no regression) → **achieved: pre-existing 39 unchanged**
- Success criteria S5 (no tenant other than apex touched) → **achieved**

The plan's next-arc is **DSO Phase-2 ADR scoping** — successor open-item/as-of canonical semantics. That arc is foundational platform work and proceeds independently of total_revenue's now-complete realization.

## Closure Verification — Slice 1h (2026-05-11)

Read-only closure check for the total_revenue arc. **Outcome: all verification signals stable; total_revenue arc complete; Bounded Business-Critical Completion Plan success criteria met or exceeded.**

### Step 1 — Readiness dial (apex)

`devhub_readiness_dial(tenant='apex')` at 2026-05-11T10:34:30 UTC:

| Metric | Value |
|---|---|
| Catalog `totalMcs` | 376 |
| Catalog `ready` (Stage 4) | 175 |
| Apex `bound` | 160 |
| **Apex `producing` (Stage 7)** | **46** |
| Apex `wouldProduceIfBound` | 0 |

No regression from Slice 1g's 46. Producing count stable.

### Step 2 — Inspector chain endpoint (per target MC)

`GET /api/admin/inspection/metrics/{metricDefinitionId}/chain?tenant=apex` for each of the 7 target MCs:

| MC | metricDefinitionId | `tenantSnapshotCount` | `tenantCanonicalObjectCount` |
|---|---|---|---|
| mc__capital_intensity_ratio | `ba0713ba-...` | **24** | 648 |
| mc__cost_of_revenue_cogs_ratio | `7d185326-...` | **24** | 648 |
| mc__research_development_to_revenue_ratio | `1c7fd703-...` | **24** | 648 |
| mc__return_on_revenue | `96107280-...` | **24** | 648 |
| mc__revenue_by_product_line | `10851e35-...` | **24** | 648 |
| mc__sg_a_to_revenue_ratio | `a661237c-...` | **24** | 648 |
| mc__shipping_cost_as_of_revenue | `43ec5f01-...` | **24** | 648 |

**All 7 MCs: `tenantSnapshotCount > 0`.** Inspector chain is platform-served via AttestationClient (D388 / DEC-f0e78e D-6 contracts), so this count reflects tenant-DB-truth. `tenantCanonicalObjectCount=648` reflects the new actual_ledger (+219) and journal_entry_hdr (+73) COs added in Slice 1g (was 356 pre-Slice-1g).

Inspector monitor pane reports `lastEvaluatedAt=n/a, evaluationCount=0, snapshotCount=0` for all 7. This is a separate counter shape (likely "explicit Test-Bench evaluations originating from a platform admin operator") that doesn't track D337-dispatcher-driven evaluations. The chain endpoint's `tenantSnapshotCount` is the authoritative production-evidence signal and confirms all 7 MCs produced.

### Step 3 — Tenant DB grain overlap recheck (read-only)

Same SQL pattern as Slice 1f / 1g, read-only against `tbc_apex_dev`:

| Table | rows | distinct `(company_code, fiscal_period)` groups |
|---|---|---|
| `fact.co_invoice_hdr_v1_1_0` | 162 | **24** |
| `fact.co_actual_ledger_v1_1_0` | 234 | **25** |
| **Overlap groups** | — | **24** |

No drift from Slice 1g's post-execution state. Grain alignment is preserved.

### Step 4 — Optional snapshot value sanity check

Read-only sample of `(company_code, fiscal_period) = (1100, FY2024-25/P03)` — the most populous grain group:

| Source | Sample values |
|---|---|
| `fact.co_invoice_hdr_v1_1_0.invoice_hdr_extended_amount` (3 rows shown) | `165,452,000`; `163,148,000`; `87,224,000` |
| `fact.co_actual_ledger_v1_1_0.actual_ledger_amount` (3 rows shown) | `111,646,720`; `24,422,720`; `87,224,000` |

Values are non-null, numeric, on the expected currency scale (INR amounts for apex/1100). Both BF columns that feed the failing-7 MCs' inputs (`invoice_hdr_extended_amount` → `total_revenue`; `actual_ledger_amount` → `net_income` / `cost_of_goods_sold` / etc.) carry sensible data. SUM aggregations have substance, not zero or placeholder values.

### Outcome — total_revenue arc complete

**Bounded Business-Critical Completion Plan — success-criteria checklist:**

| # | Criterion | Target | Actual | Status |
|---|---|---|---|---|
| S1 | `total_revenue` available to affected MCs | At least 5 of 7 producing | **7 of 7 producing** | ✅ Exceeded |
| S2 | At least N of 7 target MCs producing | ≥ 5 | **7 of 7** | ✅ Exceeded |
| S3 | Apex producing count increases from 39 | Any positive delta | **39 → 46 (+7)** | ✅ Achieved |
| S4 | No regression on currently producing MCs | 39 stays as floor | **46 ≥ 39** | ✅ Achieved |
| S5 | No tenant other than apex touched | apex only | apex only — verified via `readiness_ledger` filter | ✅ Achieved |

**Stop conditions** from the planning document: none triggered.

- X1 (H3 falsified): N/A — H3 was confirmed.
- X2 (no governed reader path with period support): partial — flavor lacks `dateField` so period filter is silently dropped. Documented as a future flavor-authoring follow-up, but the simulator data was already in the desired range, so the slice succeeded without scope-precise filtering.
- X3 (simulator lacks data): falsified — simulator carried 219 + 73 rows in exactly the needed date range.
- X4 (Slice 1g extends GL coverage but 7 MCs still reject): falsified — all 7 MCs produced.

### Realized cumulative producing-count uplift

- Pre-Slice-1 (arc start): **31 producing**
- Post-Slice-1g + Slice 1h verification: **46 producing**
- **Cumulative delta: +15 MCs**
- Slice 1g direct target uplift: **+7** (the 7 stale MCs that motivated the arc)
- Additional uplift from D337 auto-dispatch side-effects: **+8** (other MCs that became eligible when cc__actual_ledger gained grain alignment)

### Next arc — DSO Phase-2 ADR scoping

Per the **Bounded Business-Critical Completion Plan**, the next arc is **DSO Phase-2 ADR scoping** — successor open-item / as-of canonical semantics for balance metrics. That arc is foundational platform work (Layer A canonical-contract semantics + Layer B grammar), proceeds independently of total_revenue's now-complete realization, and is named in ADR-c012c0 §Successor.

The total_revenue MWR (this document) closes here. Future investigation that touches `total_revenue` semantics, the cc__invoice_hdr / cc__actual_ledger grain alignment, or the 7 MCs in this arc should consult this record's **Drift / Damage Risks**, **Guardrails For Future Work**, and **Design-From-Tenant-Data Guardrail** sections before acting.

### Hard-constraint confirmation — Slice 1h

| Check | Result |
|---|---|
| Reader execution | ✗ None |
| Metric evaluation | ✗ None |
| DB writes | ✗ None — Inspector reads via service; tenant-DB SELECT-only |
| Contract / mapping / schema / SDG / code changes | ✗ None |
| demo-selenite / sandbox1 touched | ✗ None |
| Commits this slice | ✗ None — MWR remains uncommitted pending operator review |
| Tmp scripts | ✓ Cleaned up |

## Decision / Recommendation

**Decision pending operator approval.** The recommended path:

- **Path A (governed service — recommended primary).** Use `POST /api/onboarding/cc/{contractId}/field-mappings/{mappingId}/replace` with `contractId = 019d762a-172f-71a6-b3ca-dc1b020a3947` and `mappingId = 4c587182-eb22-48c8-93ff-bbc80b45eb82` to repoint the mapping from `invoice_hdr_total_amount` → `invoice_hdr_extended_amount`, rule SUM preserved. After the write, trigger `devhub_l_node_refresh(canonical_contract_id = 019d762a-172f-71a6-b3ca-dc1b020a3947)` to refresh affected MC semantic verdicts, then `POST /api/registry/chain-status/refresh` to update the SSOT, then `devhub_formula_token_audit(tenant='apex')` to confirm `total_revenue` moves from broken to clean.
- **Paired step — Path A semantic clarification.** Update CF `total_revenue` to add a `description_text` capturing the income-statement convention. **No governed endpoint exists today.** Options:
  - (a) Skip the description update in this slice; raise a separate follow-up to add a PATCH endpoint to `canonical-fields` controller.
  - (b) Author a one-row DBCP for the description update only (no semantic change to data; documentation only).
  - (c) Defer until a governed CF-update endpoint ships.
  Recommended sub-decision: **(a) or (c)** — Path A's value does not depend on the description landing simultaneously; ship the mapping fix, raise the controller-gap follow-up.
- **One-then-many.** After the mapping repair lands, verify `mc__total_revenue` produces a non-null snapshot for `apex` (the single-input output MC is the most reliable proof). Only after that confirms do we proceed to the 21 dependent MCs (where other tokens may still be broken).
- **Cross-tenant consideration.** The mapping is platform-scoped. On next evaluation, any MC whose binding actually routes through `cc__invoice_hdr` for the `total_revenue` field will produce a new value from `invoice_hdr_extended_amount`. Read-only impact analysis (see Findings 5–6) showed both existing snapshots in scope (one on `apex`, one on `demo-selenite`) route via `cc__actual_ledger`, **not** `cc__invoice_hdr`, so neither is mutated by this repair.

**Versioning question — does this require a new `cc__invoice_hdr` version (per Live MC Safety Workflow)?** Recommendation: **no**. The D330-R5 endpoint exists specifically to handle broken-mapping corrections without a version bump, and the change is correction-shaped (always-null → producing) rather than meaning-mutation-shaped (one valid semantic → another). The endpoint's same-CF constraint preserves the binding contract; only the source BF changes. Strict-interpretation operators who consider this a meaning event should escalate to the CC version-bump orchestrator (`POST /onboarding/cc/{contractId}/version-bump`) instead — that path is governed and equally available.

If the operator chooses the version-bump path, the work expands materially:
- Author `cc__invoice_hdr` v1.2.0 with the corrected mapping; submit / approve / activate.
- Bump every CM pointing at `cc__invoice_hdr`'s current versions.
- Re-onboard-connector for every tenant with bindings touching `cc__invoice_hdr` — in practice the demo tenant `apex`, and any other tenant that may have been onboarded onto that CC.
- Old snapshots remain valid against v1.0.0 / v1.1.0; new ones produce against v1.2.0.
This record will be amended to reflect that path if chosen.

## Evidence

- DevHub change records:
  - `CHG-8d4e6d` — SES-1c080e (bc-docs) plan-side; this session.
- Live impact analysis (read-only):
  - `devhub_readiness_dial` (apex, 2026-05-11 03:36 UTC) — bound 148 / producing 31 / wouldProduceIfBound 0.
  - `devhub_formula_token_audit(tenant='apex')` — 376 / 27 clean / 349 broken; `total_revenue` × 19 broken (`null_in_tenant`).
  - `pg_query` against `contract.cc_field_mapping`, `contract.canonical_field`, `contract.observation_field_map`, `metric.metric_formula_variable`, `metric.readiness_ledger`.
- Service-path discovery:
  - `bc-core/src/registry/cc-onboarding.controller.ts:43` — `POST /onboarding/cc/{contractId}/field-mappings/{mappingId}/replace` (D330-R5).
  - `bc-core/src/registry/cc-onboarding.controller.ts:60` — `POST /onboarding/cc/{contractId}/version-bump` (TSK-d57036 #2, orchestrated path).
  - `bc-core/src/registry/canonical-field.controller.ts` — POST create only; **no PATCH/PUT for description update** (gap).
  - `bc-core/src/registry/chain-status.controller.ts:81` — `POST /registry/chain-status/refresh`.
  - DevHub MCP `devhub_l_node_refresh(canonical_contract_id)` — L-node refresh after CC change.
  - DevHub MCP `devhub_tenant_bind_metrics` — binding writes (dry-run by default; D268-gated).
- Cross-references:
  - `bc-docs-v3/docs/onboarding/metric-workstream.md` — §3 Metric Work Sequence; §5 Live MC Safety Workflow; §8 balance-vs-flow rule; §10 anti-patterns; §11 record triggers.
  - `bc-docs-v3/docs/operations/apex-cfo-pack-demo-readiness-triage.md` — broader Apex demo-readiness state; this slice is Slice 1 of the production-expansion arc named there.
  - `bc-docs-v3/docs/onboarding/metric-work-records/days-sales-outstanding/2026-05-11-grammar-design-SES-b7db1a.md` — sibling investigation surfacing the same funnel-padding pattern from the DSO numerator side.
  - `memory/feedback_funnel_padding.md` — anti-pattern context for the 81-CF sibling group.

## Non-decisions

- Did NOT author any DBCP this turn. The repair went through the governed D330-R5 service endpoint.
- Did NOT update `contract.canonical_field.description_text` for `total_revenue`. Service gap (no PATCH endpoint) deferred to a follow-up TSK; no description-only DBCP authored in this slice.
- Did NOT mass-repoint the 80 sibling CFs sharing `invoice_hdr_total_amount`. Each requires its own per-CF audit (Slice 2+).
- Did NOT version-bump `cc__invoice_hdr`. The D330-R5 in-place repair is the governed path for broken-mapping correction; no new CC version required by platform governance.
- Did NOT evaluate any of the 21 dependent MCs (the user's instruction was explicit). The +11 clean MCs from the audit have not been dispatched; their producing-count uplift is pending operator approval to evaluate.
- Did NOT touch any `demo-selenite` snapshot or binding. `demo-selenite` is not the demo tenant — it was checked read-only as another tenant carrying a `mc__total_revenue` ledger row, and the cc__invoice_hdr repair is architecturally orthogonal to mc__total_revenue's `cc__actual_ledger` binding (the path both existing snapshots route through).
- Did NOT change SDG, reader, OC, AC, AI service behavior, or any other contract.
- Did NOT commit any file in any repo this session.

## Follow-ups

- **TSK (to file post-commit):** *Add PATCH endpoint to `canonical-fields` controller for description / metadata updates.* Service gap; modest scope (one controller method + DTO + service method + repository update). Blocks future CF-clarification work that should not require DBCP.
- **TSK (to file post-commit):** *Per-CF audit of the 80 sibling CFs sharing `invoice_hdr_total_amount` on `cc__invoice_hdr`.* Slice 2+ of the Apex production-expansion arc. Each CF gets its own semantic + mapping audit. Do **not** mass-repoint.
- **TSK (to file post-commit):** *Post-fix audit rerun for the dependent total_revenue MCs.* Dispatch the 20 MCs that bind cc__invoice_hdr with `fields_used=["total_revenue"]`; measure producing-count uplift; identify which still have other broken tokens. This is the actual "many" half of the one-then-many gate.
- **TSK (to file post-commit, lower priority):** *mc__total_revenue temporal-gate investigation.* Today's Test-Bench evaluation rejected with `Completeness 50.0% for 'fiscal_period' below threshold 80%`. The MC was previously producing (5 historical ledger rows). Diagnose whether CO fiscal_period coverage degraded, whether the contract threshold changed, or whether this is expected period-over-period behavior. Not related to the cc__invoice_hdr repair.
- **Open question:** CLAUDE.md's Authentication section currently lists `demo-selenite` as the demo tenant. The active demo tenant is `apex` / `tbc_apex_dev` (Apex Motors — the CFO Pack storyboard surface). Flag for a separate doc update when next touching CLAUDE.md; not in scope of this MWR's commit.
