---
metric: 19 MCs reference canonical_field operating_cash_flow
metric_version: n/a
tenant: apex
source_system: sap_ecc
work_type: rejection-investigation
session_uid: SES-524cdc
date: 2026-05-11
status: deferred
related_commits:
  - 1a5dcfd  # docs(demo): refresh apex CFO pack triage after revenue arc
related_tasks: []
related_adrs:
  - DEC-1db1c7  # D401 — Open-item / as-of canonical semantics (proposed)
  - DEC-c012c0  # D400 — Metric Contract grammar v1.1 (proposed)
related_change_records:
  - CHG-9b61c9                  # SES-524cdc plan-side
repair_location: A+C (possibly B if MC rebind path chosen)
affected_boundary: canonical_evaluation
foundation_gate: passed
---

# Operating cash flow production gap — cross-metric investigation — 2026-05-11

> **This record is orientation memory, not contract authority.** Canonical sources (`contract.canonical_mapping`, `contract.cc_field_mapping`, `contract.metric_binding`, evidence rows) win on conflict.

## Summary

Audit-top broken CF on apex: `operating_cash_flow` (11 MCs `null_in_tenant`). Discovery reveals the gap is **structural, not tenant-specific**: `cc__gaap_cash_flow` v1.0.0 is registered as the target CC for `operating_cash_flow` (and 22 sibling CFs) but has **zero `canonical_mapping` rows** — no OC-to-CC chain exists. Same finding for `cc__gaap_income_statement` (0 mappings, 32 CFs) and `cc__ifrs_balance_sheet` (0 mappings, 5 CFs). These three "reporting CCs" are CC shells in the registry without upstream chains. The output MC `mc__operating_cash_flow` produces today via a different path (computed from cc__actual_ledger components), but the 18 input-consuming MCs cannot resolve their direct-lookup binding. **This is a Layer A + Layer C platform-wide gap, not a Layer A tenant-data gap.** Per the Design-From-Tenant-Data Guardrail, the right repair is a shared-architecture decision, not a tenant-scoped data extension. Discovery-only this session; no writes; awaiting operator direction on which of three named paths to take.

## Foundation Gate Result

- **Repair location:** **A + C** (source emission for cash-flow-statement entity + canonical_mapping authoring). **B may join** if the MC envelope rebind path is chosen (Path 1B below).
- **Affected boundary:** `canonical_evaluation` — the engine fetches operating_cash_flow via cc__gaap_cash_flow's CO set, which is empty for every tenant because there's no upstream chain to populate it.
- **Six-invariant pre-check:**
  - I (meaning-once): no source-layer or read-layer compensation proposed. The fix is contract-level.
  - II (object ordering): no boundary reorder.
  - III (state immutable): new chain rows (OC, canonical_mapping); existing artifacts untouched.
  - IV (references explicit): once the chain is built, selected CO ids surface in inputReferencesJson at metric eval.
  - V (non-replayable): engine produces new evaluations against the new chain; replay deterministic.
  - VI (evidence emitted): canonical_mapping rejections + admission rejections emit explicit names.
- **Why not other layers:**
  - A (source / SDG) is part of the gap — but the bc-sdg simulator already emits FAGLPOSE journal-entry data (verified in Slice 1g; 219 records covering FY2023-24/P07 → FY2026-27/P01). No SDG tuning required for the data side; the issue is whether/how the platform projects FAGLPOSE rows into cc__gaap_cash_flow.
  - B (contract semantics) — CF `operating_cash_flow` is well-defined as a number (currency); the cc__gaap_cash_flow CC envelope is registered. The B work, if any, is MC envelope rebinding (Path 1B).
  - C (mapping / binding) is the dominant work site: author canonical_mapping rows AND/OR repoint MC bindings.
  - D (evaluation boundary) — engine code is fine; existing mechanics handle the new chain once it's built.
  - E (storage / projection) — fact tables for cc__gaap_cash_flow will be schema-provisioned once the chain is built. No E-layer change beyond standard onboarding.
  - F (read model / diagnostics) — none.
- **Override?** none.

## Metric Logic Studied

The 19 MCs referencing `operating_cash_flow` span 3 subfunctions:
- **cash_flow_management** (10 MCs): mc__capital_expenditure_capex_coverage_ratio, mc__cash_flow_from_operations_to_sales_ratio, mc__cash_flow_margin_ratio, mc__cash_flow_per_employee, mc__cash_flow_to_capital_expenditures_ratio, mc__cash_flow_to_revenue_ratio, mc__cash_flow_to_shareholder_equity_ratio, mc__cash_reinvestment_ratio, mc__net_income_to_operating_cash_flow_ratio, mc__operating_cash_flow_per_share, mc__operational_cash_to_capital_expenditure_ratio
- **treasury** (5 MCs): mc__available_cash_flow, mc__cash_conversion_ratio, mc__net_debt_to_cash_flow_ratio, mc__operating_cash_flow (output), mc__operating_cash_flow_ratio, mc__treasury_management_efficiency
- **capital_structure_optimization** (1 MC): mc__cash_flow_to_debt_ratio
- **accounts_receivable** (1 MC): mc__cash_conversion_efficiency
- **cash_flow_management** (mc__cash_conversion_ratio variant) — already counted

Formula shape (sampled): every consuming MC is a ratio with `operating_cash_flow` as the numerator (I1, usually) and a second binding for the denominator (capital expenditures, revenue, equity, debt, etc.). The output MC `mc__operating_cash_flow` is a compute: `net_income + depreciation_and_amortization + change_in_working_capital`.

## Registry Diagnosis

| Artifact | State |
|---|---|
| CF `operating_cash_flow` | Registered, `status_code='draft'`, subfunction `accounts_receivable`, currency-number input. No description text. |
| Sibling CF `cash_flow_from_operations` | Registered, subfunction `treasury`, description: *"The cash generated from a company's core business operations."* Both CFs exist; no consolidation. |
| `cc_field_mapping` for `operating_cash_flow` | **1 row**: `cc__gaap_cash_flow.gaap_cashflow_operating_net`, rule `sum`, no filter, no compute. BF type `number`. |
| BF `gaap_cashflow_operating_net` | Registered, status `draft`. **Zero `observation_field_map` rows emit this BF** — no OC produces it. |
| Alternative cash-flow BFs that ARE certified | `ifrs_cash_flows_from_used_in_operating_activities`, `ifrs_cash_flows_from_used_in_financing_activities`, `ifrs_cash_flows_from_used_in_investing_activities`, plus XBRL/BC variants. **None emitted by any OC either.** |
| `cc__gaap_cash_flow` v1.0.0 | `governance_state_code='active'`. **0 `canonical_mapping` rows.** 23 `cc_field_mapping` rows aspire to it. **No upstream chain.** |
| Sibling reporting CCs | `cc__gaap_income_statement` v1.0.0 — 0 mappings, 32 CFs. `cc__ifrs_balance_sheet` v1.0.0 — 0 mappings, 5 CFs. Same pattern. |
| Production-chain CCs (for contrast) | `cc__actual_ledger` v1.1.0 — 1 mapping, 385 CFs. `cc__invoice_hdr` v1.1.0 — 2 mappings, 152 CFs. `cc__receivable_hdr` v1.1.0 — 1 mapping, 118 CFs. **All have upstream chains.** |

**The gap pattern:** the platform has a family of "reporting-shaped CCs" (GAAP cash flow, GAAP income statement, IFRS balance sheet) that exist as binding targets in the metric_binding graph but have **no canonical_mapping rows** wiring them to any upstream OC. Many CFs aspire to be sourced from these CCs, but the chain is unbuilt.

## Runtime Realization Check

Tenant DB `tbc_apex_dev` is expected to have either NO fact tables for these CCs (if schema-provisioner skips empty CCs) OR empty fact tables (if it provisions on the CC registration alone). Not verified this session — read-only inspection would confirm but is not load-bearing for the diagnosis. The structural gap (no canonical_mapping rows) means no COs can be produced for cc__gaap_cash_flow under any tenant; this is platform-wide, not apex-specific.

## Impact Lens — affected MC bindings vs current production

Among the 19 MCs that reference `operating_cash_flow`:

- **`mc__operating_cash_flow` (output, draft)** — binds `cc__actual_ledger` with `fields_used=["net_income", "depreciation_and_amortization", "change_in_working_capital"]`. **COMPUTES the value.** Currently producing for apex (1 metric_snapshot ledger row, FY2026-27/P01) — verified in Slice 1g D337 fanout.
- **18 input-consuming MCs** — all bind `cc__gaap_cash_flow` with `fields_used=["operating_cash_flow"]` (direct lookup, not compute). All blocked by the missing upstream chain.

Cross-CC binding patterns (the second-CC each MC binds, indicating their other inputs):

- `cc__actual_ledger` (5 MCs use it for net_income / net_debt / total_liabilities / net_sales_revenue) — production-chain ready
- `cc__ifrs_balance_sheet` (4 MCs use it for capital_expenditures) — **same gap** as cc__gaap_cash_flow (0 mappings)
- `cc__gaap_income_statement` (1 MC for operating_profit) — **same gap**
- `cc__commercial_invoice_hdr` (2 MCs for total_debt_balance, total_treasury_costs) — chain exists
- `cc__invoice_hdr` (1 MC for total_revenue) — chain exists
- `cc__receivable_hdr` (1 MC for total_sales_revenue) — chain exists

**Even if cc__gaap_cash_flow is fixed**, 5 MCs additionally depend on `cc__ifrs_balance_sheet` (also unbuilt) and 1 on `cc__gaap_income_statement` (also unbuilt). The cluster is interlocked.

## Three Repair Paths

### Path 1A — Build the cc__gaap_cash_flow chain properly

Author:
- New OC `oc__s4hana__faglpose__gaap_cash_flow` (or similar) mapping FAGLPOSE journal-entry rows aggregated by GAAP cash-flow category → BFs that cc__gaap_cash_flow expects
- `canonical_mapping` for cc__gaap_cash_flow
- Possibly new BFs if existing ones aren't sufficient (e.g., distinguishing operating vs investing vs financing flows requires aggregation logic — GL accounts mapped to cash-flow categories via a category-mapping table)
- Schema-provision the cc__gaap_cash_flow fact table
- Bind to apex
- Verify

**Scope:** comparable to DEC-1db1c7 Slice 1.x (open-item CC family) — a multi-step authoring arc with non-trivial mapping decisions (cash-flow categorization rules from GL chart of accounts).

**Pros:** Foundation-clean. The cc__gaap_cash_flow CC carries its proper semantic — direct lookup of "company's operating cash flow as of period end" from cash-flow-statement-shaped data.

**Cons:** Largest scope. Requires (a) GL account → cash-flow-category mapping rules, (b) aggregation logic at admission/observation, (c) possibly new BFs. Generalizes naturally to cc__gaap_income_statement + cc__ifrs_balance_sheet (3 reporting CCs need the same treatment).

### Path 1B — Repoint 18 MCs to cc__actual_ledger via compute mapping

Add a `compute` mapping on `cc__actual_ledger` for `operating_cash_flow` that mirrors the output MC's formula (net_income + depreciation_and_amortization + change_in_working_capital). Then version-bump the 18 input-consuming MCs to rebind their `operating_cash_flow` input from `cc__gaap_cash_flow` → `cc__actual_ledger`.

**Scope:** 1 compute mapping authoring + 18 MC version bumps (per playbook §5 Live MC Safety Workflow).

**Pros:** No new CC chain needed. Reuses existing cc__actual_ledger production chain. Single source of truth for operating_cash_flow (the compute formula).

**Cons:** Couples 18 MCs to cc__actual_ledger architecturally — they no longer bind their "intended" cash-flow-statement CC. CFO Pack storyboard's "cash flow" tiles would be semantically sourced from GL, not from a cash-flow statement. Foundation-clean (no SDG tuning, no read compensation, computes from real data), but **less faithful to the storyboard's "cash flow statement" framing**. Also doesn't address the parallel cc__gaap_income_statement + cc__ifrs_balance_sheet gaps that block other MCs.

### Path 1C — Hybrid: compute-from-actual-ledger now; reporting CCs later

Stage 1: Apply Path 1B now to unblock the 12-13 producing MCs that depend ONLY on operating_cash_flow + a ready CC (cc__actual_ledger, cc__invoice_hdr, cc__receivable_hdr). Stage 2: Author the cc__gaap_cash_flow + cc__gaap_income_statement + cc__ifrs_balance_sheet chains properly when reporting fidelity becomes important (e.g., for an SEC-style filing demo).

**Pros:** Fast wins now; correct architecture later. Phase 1 unblocks the demo-leverage MCs.

**Cons:** Two stages of churn. Stage 2 MC re-rebinding required.

### Path 1D — Defer

Cash-flow-statement metrics are not in the cut-down 15-minute demo flow recommended in the triage refresh (Section 13). Meera's M9 working-capital tile is producible via mc__working_capital_turnover (already producing). Defer the operating_cash_flow arc until the storyboard owner asks for cash-flow-statement narrative specifically.

## Recommendation

**Path 1D (defer) is the recommended posture for the current demo cycle.** Per the triage refresh:
- The 30-minute demo collapses to a 15-minute Meera + Anil flow.
- Treasury angle (M9–M11) is partially supported by mc__operating_cash_flow (the output MC itself, which produces via cc__actual_ledger compute), mc__working_capital_turnover, mc__liquidity_coverage_ratio, mc__total_treasury_costs — these can carry the working-capital narrative.
- The 18 input-consuming MCs are not on the critical demo path. Most are sophisticated CFO ratios that wouldn't survive the cut-down flow anyway.

**If the operator wants to push producing count past 46 this cycle, Path 1B is the smallest provable step:**
- 1 compute mapping (cc__actual_ledger.operating_cash_flow ← net_income + D&A + ΔWC) — requires verifying engine supports `compute` rule shape for cash-flow components.
- 18 MC version bumps (per playbook §5 Live MC Safety Workflow). Apex-only tenant binding update for each.
- Estimated realized uplift: 8–12 MCs (the ones whose second binding is cc__actual_ledger, cc__invoice_hdr, or cc__receivable_hdr — those CCs are production-ready). The 6 MCs whose second binding is cc__ifrs_balance_sheet or cc__gaap_income_statement stay blocked.

**Path 1A is correct long-term but is a multi-session arc** — out of scope for a single slice. It also generalizes to the parallel CCs.

## Rejected Interpretations

- **"Tenant-scoped data extension for apex on FAGLPOSE will fix it" (Slice 1g pattern).** Rejected — the FAGLPOSE data IS already extended (Slice 1g landed 219 ActualLedger rows + 73 JournalEntry rows). The gap is upstream of source coverage: cc__gaap_cash_flow has no OC-to-CC chain at all. More source data doesn't help an unbuilt chain.
- **"D330-R5 single-row mapping repair like total_revenue."** Rejected — total_revenue's repair was a wrong-target BF on an existing mapping. operating_cash_flow's CC has NO mappings, not a wrong one. D330-R5 doesn't apply.
- **"Read-side computation in FactReaderService or admin endpoint."** Foundation Invariant I — meaning produced at the boundary, not the read layer. Rejected.
- **"SDG tuning to populate cc__gaap_cash_flow directly."** Foundation Invariant I — meaning at source layer. Rejected.
- **"In-place edit on the existing CC envelope to point at a different BF source."** Invariant III. Rejected.
- **"Author a new CF named `operating_cash_flow_computed` and point only the 18 input-consuming MCs at it."** Fragments the CF taxonomy on a non-temporal axis (computed vs direct). The CF semantic is the same; only the *source* differs. Rejected; prefer Path 1B which keeps CF identity intact and repoints at the source layer.

## Drift / Damage Risks

- **The three reporting CCs (cc__gaap_cash_flow, cc__gaap_income_statement, cc__ifrs_balance_sheet) form a cluster.** Repairing one doesn't unblock all dependent MCs because many cross-bind two reporting CCs. The full cluster repair is a Phase-2-shape arc, not a single slice.
- **Path 1B couples 18 MCs to cc__actual_ledger.** A future change to cc__actual_ledger's GL structure (e.g., new chart of accounts, different account-to-category mapping) would silently affect all 18 metrics. Mitigation: every cc__actual_ledger change must surface this MWR and the compute mapping for review.
- **The compute formula (net_income + D&A + ΔWC) is an indirect approximation of operating cash flow.** True operating cash flow includes working-capital adjustments at line-item granularity; the compute approximates them as an aggregate. For analyst-grade reporting, this is acceptable but imprecise. Document the approximation in the compute mapping body so future operators can challenge the meaning.
- **The 23 CFs that aspire to cc__gaap_cash_flow but have only 1 mapping pointing at the empty CC are funnel-padding-vulnerable.** A future operator might mass-repoint them to cc__actual_ledger compute mappings, repeating the funnel-padding anti-pattern. Per the Design-From-Tenant-Data Guardrail in the total_revenue MWR, mass-repointing for symptom suppression is forbidden. Each CF deserves its own semantic audit.

## Guardrails For Future Work

- Read this record's Registry Diagnosis and the Three Repair Paths before any change to cc__gaap_cash_flow, cc__gaap_income_statement, or cc__ifrs_balance_sheet.
- For any of the 19 MCs referencing operating_cash_flow, apply the playbook's Live MC Safety Workflow (§5) on version bumps. The compute formula choice (Path 1B) is a meaning decision — new MC version, not in-place edit.
- Before authoring Path 1A's canonical_mapping for cc__gaap_cash_flow, verify the source signal: SAP FAGLPOSE/BSEG has GL line-item rows with account_code; the cash-flow-category mapping (operating vs investing vs financing) requires either (a) account-classification reference data (chart of accounts) or (b) explicit cash-flow-category tags in source.
- If Path 1A or 1B is approved, file a corresponding MWR per playbook §11 (new-MC or version-bump trigger applies to the 18 MCs touched).
- Surface this record's "cluster" framing to whoever scopes cc__gaap_income_statement and cc__ifrs_balance_sheet work — the three reporting CCs are interlocked.

## Findings

1. **CF `operating_cash_flow` is registered** with no description, status `draft`, subfunction `accounts_receivable` (categorization quirk; semantically it's treasury). The sibling CF `cash_flow_from_operations` exists separately with a description; the platform has not consolidated them.
2. **One cc_field_mapping row** maps `operating_cash_flow` → `cc__gaap_cash_flow.gaap_cashflow_operating_net` with rule SUM.
3. **The BF `gaap_cashflow_operating_net`** is registered (status `draft`) but emitted by **zero observation_field_map rows**.
4. **`cc__gaap_cash_flow` v1.0.0 is `active` but has zero `canonical_mapping` rows.** The CC is a registry shell with no upstream chain.
5. **Same pattern for `cc__gaap_income_statement` and `cc__ifrs_balance_sheet`.** Three reporting CCs, all unbuilt.
6. **18 input-consuming MCs** bind `operating_cash_flow` via `cc__gaap_cash_flow` (direct lookup) — all blocked by the missing chain.
7. **1 output MC `mc__operating_cash_flow`** binds `cc__actual_ledger` and **computes** operating cash flow from net_income + D&A + ΔWC — this MC produces today (1 ledger row for apex).
8. **The audit's `null_in_tenant=11` count for operating_cash_flow** matches the apex-bound subset of the 18 direct-lookup MCs.
9. **bc-sdg simulator data is not the blocker.** FAGLPOSE journal-entry rows are available (verified in Slice 1g). The chain has not been authored, not the data missing.

## Decision / Recommendation

**Decision: Path 1D — DEFERRED for this demo cycle (2026-05-11).**

**Reason:** the operating_cash_flow gap is not a one-off CF patch. The diagnosis shows it is part of a 3-CC reporting cluster (`cc__gaap_cash_flow` + `cc__gaap_income_statement` + `cc__ifrs_balance_sheet`) where all three CCs are registered shells with zero `canonical_mapping` rows. A proper repair requires designing the financial-statement-shaped CC family (Path 1A) — comparable in scope to DEC-1db1c7 Mechanism A and likely deserving its own ADR. A short-circuit (Path 1B — compute mapping + 18 MC version bumps) would couple 18 MCs to `cc__actual_ledger` semantics and not address the parallel cc__ifrs_balance_sheet / cc__gaap_income_statement gaps; it trades architectural fidelity for incremental producing-count uplift that the demo does not need.

The Treasury angle in the cut-down 15-minute Meera + Anil demo flow is already supported by:
- `mc__operating_cash_flow` (output MC, producing via cc__actual_ledger compute)
- `mc__working_capital_turnover`
- `mc__liquidity_coverage_ratio`
- `mc__total_treasury_costs`
- `mc__fx_exposure_by_currency`, `mc__fx_gain_loss_impact_on_p_l`, `mc__hedge_effectiveness`

These give Meera the working-capital and FX narrative without needing the cash-flow-statement-shaped MCs.

**Follow-up:** revisit as a **reporting-CC cluster build**, not as a one-off CF patch. The three CCs (`cc__gaap_cash_flow`, `cc__gaap_income_statement`, `cc__ifrs_balance_sheet`) should be scoped as a unified architecture — comparable in shape to DEC-1db1c7 (open-item canonical semantics). A successor ADR (or a sub-arc of an existing ADR) would specify: (a) which source entity feeds the three CCs (FAGLPOSE + chart-of-accounts classification, or a separate reporting-shaped extract), (b) the per-CF cash-flow-category mapping rules, (c) the relationship to `cc__actual_ledger` (parallel CCs deriving from the same source vs CC-of-CCs aggregation).

**Not implemented this cycle:** Path 1A (full chain build), Path 1B (compute mapping + rebind), Path 1C (hybrid). All deferred.

## Evidence

- `devhub_readiness_dial(tenant='apex')` 2026-05-11T11:59 UTC: bound 160, **producing 46**, wouldProduceIfBound 0.
- `devhub_formula_token_audit(tenant='apex')` 2026-05-11T11:59 UTC: 376 / 38 clean / 338 broken. `operating_cash_flow` ranks #1 broken CF with `null_in_tenant=11`.
- `pg_query` against `contract.canonical_field`, `contract.cc_field_mapping`, `contract.business_field`, `contract.observation_field_map`, `contract.canonical_contract`, `contract.canonical_mapping`, `metric.metric_formula_variable`, `metric.metric_binding`. Read-only.
- Cluster reporting-CC finding (cc__gaap_cash_flow / cc__gaap_income_statement / cc__ifrs_balance_sheet all with 0 mappings) — recorded for future scoping conversations.

## Non-decisions

- Did NOT author any OC, CC, canonical_mapping, cc_field_mapping, MC version, or compute mapping.
- Did NOT execute any reader.
- Did NOT touch demo-selenite or sandbox1.
- Did NOT modify ADR-c012c0, ADR-1db1c7, or any prior MWR's substantive content.
- Did NOT write to any DB.
- Did NOT propose changes to bc-core engine, schema-provisioner, or any code.
- Did NOT propose changes to bc-sdg.
- Did NOT commit any file in any repo this session.

## Follow-ups

- **OPERATOR DECISION** on Path 1A vs 1B vs 1C vs 1D. Recommended: **1D (defer)** for the current demo cycle.
- **If Path 1B chosen:** verify engine supports the `compute` rule shape for multi-input cash-flow computation. Check `compute-evaluator.ts` for supported operation primitives. Pre-flight before authoring the compute mapping.
- **If Path 1A chosen:** scope the OC authoring + canonical_mapping authoring as a separate ADR-grade decision. The three reporting CCs (cash flow, income statement, balance sheet) deserve a unified architectural framing — possibly a separate ADR similar to DEC-1db1c7 but for financial-statement-shaped CCs.
- **Tier-A demo tiles for "cash flow"** in the storyboard — verify which tiles are sourced from these MCs vs computed differently. The triage refresh's Tier-A list already maps Treasury angle to surviving MCs (mc__operating_cash_flow output, mc__working_capital_turnover, mc__liquidity_coverage_ratio). No demo-side action needed today.
- **Repeat audit after any change** to confirm null_in_tenant count for operating_cash_flow drops.

(No `TSK-` UIDs filed this session; operator has visibility on each open path.)
