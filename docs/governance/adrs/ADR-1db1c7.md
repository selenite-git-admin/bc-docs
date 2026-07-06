---
uid: DEC-1db1c7
title: "Open-item / as-of canonical semantics — temporal projection for balance metrics"
description: "Adopts a separate open-item canonical contract family pattern (cc__receivable_open_item etc.) as the primary mechanism for realistic balance-metric semantics. Layers on top of DEC-c012c0 (D400). Source-feasible today via SAP AUGDT/AUGBL fields. Mechanism B (clearing-by-supersession) deferred; Mechanism C (bitemporal in-place mutation) rejected on Foundation Invariant III."
status: superseded
date: 2026-05-11T10:55:36.906Z
project: platform
domain: metric
subdomain: canonical-semantics
focus: balance-metrics
superseded_by: DEC-83fda0
---

# Open-item / as-of canonical semantics — temporal projection for balance metrics

## Context

Today's receivable / payable / inventory canonical contracts (cc__receivable_hdr et al.) are append-only: every AR-debit posting becomes a CO; clearing produces no separate CO that nets the original. A posting_date ≤ anchor selector therefore returns cumulative-through-anchor, not open-at-anchor — mathematically distinct from realistic DSO/DPO/DIO numerators. ADR-c012c0 (D400) shipped grammar v1.1 for the flow side and deliberately omitted at_period_end so no MC could be authored against a semantic the engine cannot honestly evaluate. This successor ADR fills the upstream gap: a Layer A + Layer C decision that gives the engine a CC family whose COs ARE open positions (and a sibling family whose COs ARE cleared events). The source already emits the signal (bc-sdg CustomerOpenItemSet's AUGDT/AUGBL fields, probed 2026-05-11). Three candidates were evaluated; only one is Foundation-clean without engine complexity.


## Context

This ADR is the named successor to DEC-c012c0 (D400) "Metric Contract grammar v1.1 — per-variable temporal input selection." That ADR introduced `over_period` and `over_trailing_window` for flow-side temporal selection and deliberately omitted `at_period_end` because the upstream canonical contracts could not honestly produce open-at-anchor positions. This ADR resolves that upstream gap.

The Apex `total_revenue` realization arc (Slices 1–1h, completed 2026-05-11) proved the chain produces honest values end-to-end when source coverage is present. The Design-From-Tenant-Data Guardrail held — that arc's realization gap was tenant-data sparsity, repaired tenant-scoped. The remaining architectural debt is **balance-style canonical semantics**, which this ADR addresses.

**Source-feasibility check (2026-05-11):** bc-sdg's `CustomerOpenItemSet` V2 endpoint emits `AUGDT` (clearing date; null on open) and `AUGBL` (clearing document; null on open) alongside `BUDAT`, `BLDAT`, `KUNNR`, `DMBTR`, `WRBTR`, `BSCHL`, `KOART`, `BLART`, `ZFBDT`, `ZTERM`. The source carries the open/cleared distinction natively. The architectural decision is **how to project that signal into canonical state** without violating Foundation invariants.

## Decision

**Adopt Mechanism A — separate open-item canonical contract family — as the primary path for realistic DSO and the analogous balance metrics (DPO, DIO, inventory-on-hand, cash position).**

The new family pattern:

- **`cc__receivable_open_item`** — every CO is an open AR position. Carries customer, amount, currency, posting_date, due_date, business_key.
- **`cc__receivable_cleared_item`** — every CO is a cleared AR event. Carries customer, original-position business_key reference, clearing_date, clearing_document, amount.
- Equivalents later: `cc__payable_open_item` + `cc__payable_cleared_item` for AP; `cc__inventory_on_hand` + `cc__inventory_movement` for inventory.

The existing `cc__receivable_hdr` (and AP / inventory siblings) continue to serve append-only posting semantics. Legacy metrics that depend on cumulative posting (e.g., DSO v1.x) bind the legacy CC unchanged. DSO v2.0.0 (authored in a successor slice, not this ADR) will bind `cc__receivable_open_item` for the numerator.

### Required ADR-level statements

- **ADR-c012c0 remains valid and is NOT superseded by this ADR.** Both stand as a layered pair: ADR-c012c0 owns Metric Contract grammar v1.1 (flow-side temporal input selection grammar); this ADR owns upstream open-item canonical semantics. The supersession-pair rule (DEC-623f8f / D370) does not require flipping ADR-c012c0's status — neither replaces the other.
- **ADR-c012c0 provides temporal input-selection grammar for flow windows.** `over_trailing_window` etc. continue to apply to flow-side variables.
- **This successor ADR provides the upstream open-item canonical semantics needed for balance metrics.** The `at_period_end` selector (deliberately excluded from grammar v1.1) becomes admissible at the MC layer **only against CCs in this open-item family** — never against the legacy append-only CCs.
- **Realistic DSO is still not complete until `cc__receivable_open_item` is authored, provisioned, bound to apex, and DSO v2.0.0 is authored.** This ADR is the architectural enabler, not the implementation.
- **No SDG tuning, no read-model compensation, no fact-side computation, no in-place live-MC semantic mutation is allowed.** Foundation invariants I, III, VI are explicit firewalls.

### Mechanism analysis summary

| Mechanism | Verdict |
|---|---|
| **A — Separate open-item CC family** | **ADOPTED.** Foundation Invariant III preserved trivially. Engine code change is minimal. Categorical state (open vs cleared as separate CCs) is the clearest semantic for future operators. Generalizes naturally to AP and inventory. |
| **B — Clearing-by-supersession** | **DEFERRED, not chosen.** Invariant III preserved via versioning. Adds non-trivial engine complexity (supersession-chain traversal in CanonicalResolutionService + MetricEvaluationEngine). Per-tenant re-onboarding is heavier. Single-CC identity is conceptually appealing but doesn't outweigh engine-side cost. Kept available if a future constraint benefits from single-CC identity. |
| **C — Bitemporal effective_from / effective_to columns** | **REJECTED.** Bitemporal as classically defined requires mutating `effective_to` when a later clearing event arrives — violates Foundation Invariant III (state immutable). Workaround (emit new CO version) collapses into Mechanism B with worse ergonomics. Permanently rejected on Foundation grounds. |

The full mechanism comparison table, source-feasibility evidence, and 5-question scoping checklist live in the scoping draft at `barecount-devhub/.claude/adr-draft-open-item-as-of-canonical-semantics.md` and the DSO MWR's `Phase 2 Architecture Scoping` section (committed 2026-05-11 in `9f0ce57`).

### Foundation Gate

| Layer | Repair location |
|---|---|
| **A — Source / SDG** | No SDG tuning. The source already emits AUGDT/AUGBL (verified on bc-sdg `CustomerOpenItemSet`). |
| **B — Contract semantics** | Light. New CCs in the open-item family. ADR-c012c0's grammar v1.1 already declares `at_period_end` as a closed enum value; this ADR re-admits it via a future grammar minor bump or via engine-side acceptance against the open-item family — to be specified in DSO Phase-2 Slice 2 (DSO v2.0.0 authoring). |
| **C — Mapping / binding** | New `canonical_mapping` and `cc_field_mapping` rows for the new CCs. CF (`outstanding_receivables_amount`) gets a sibling mapping on the new CC; legacy mapping on `cc__receivable_hdr` stays. |
| **D — Evaluation boundary** | No engine code change. Existing CO selection mechanics work against the new CCs unchanged. |
| **E — Storage / projection** | Fact tables for new CCs provisioned via existing schema-provisioner path. No mutation of existing fact tables. |
| **F — Read model / diagnostics** | No semantic compensation at read layer. Inspector / Readiness Toolkit must learn to recognize the new CC family in chain-status counters and per-MC drill — small enhancement, no semantic risk. |

### Foundation invariants preserved (all six)

- **I — meaning produced once:** open/cleared distinction comes from source; no engine inference; no read-side projection.
- **II — object ordering:** Source → Reader → SO → Admission → Canonical → CO → Metric — unchanged.
- **III — state immutable:** every CO is a new row; nothing mutates. Open and cleared positions are separate COs in separate CCs.
- **IV — references explicit:** every selected open-AR CO id surfaces in `inputReferencesJson` at evaluation time.
- **V — non-replayable:** each evaluation produces a new `metric_evaluation_id`; replay yields identical `metricValueJson` against the same input state.
- **VI — evidence emitted:** rejections (e.g., "no open AR at anchor X for company_code Y") emit named evidence checks.

## Scope

### In scope (this ADR)

- Open-item CC family pattern as the architectural primitive.
- `cc__receivable_open_item` as the first implementation target (smallest provable step).
- Source-feasibility basis via SAP `AUGDT` / `AUGBL` fields (bc-sdg `CustomerOpenItemSet`).
- Evidence and lineage requirements: every selected open-AR CO id surfaces explicitly in `inputReferencesJson`; rejections emit named evidence checks.
- Generalization path to DPO (`cc__payable_open_item`), DIO (`cc__inventory_on_hand`), and the CCC (Cash Conversion Cycle) tile re-enablement once DSO v2 + DPO v2 + DIO v2 all produce under the same family pattern.

### Out of scope (separate slices / ADRs)

- DSO v2.0.0 authoring (DSO Phase-2 Slice 2).
- DPO v2 / DIO v2 / CCC tile re-enablement (DSO Phase-2 Slices 4–6).
- bc-sdg generator changes (none needed — source already emits the signal).
- bitemporal in-place mutation (permanently rejected on Foundation Invariant III).
- Clearing-by-supersession as primary path (deferred; single-CC-identity option for the future).
- Any implementation in this ADR — this is architectural authorization only.
- SDG tuning, read-model compensation, fact-side computation, in-place live-MC semantic mutation (all explicitly forbidden).

## Implementation arc (post-promotion)

| Slice | Goal | Repair location |
|---|---|---|
| 0 (scoping) | This ADR + DSO MWR Phase-2 Architecture Scoping section | Docs only |
| **1** | **Author + provision `cc__receivable_open_item` + its OC + canonical_mapping for apex; verify open-AR COs land in `fact.co_receivable_open_item_v1_0_0`** | **A + C** |
| 2 | Author DSO v2.0.0 binding `cc__receivable_open_item` (numerator) + `cc__invoice_hdr` trailing-90 (denominator). MC version-bump per playbook §5. | B |
| 3 | Optional: author `cc__receivable_cleared_item` for clearing-event analytics. Not blocking for DSO. | A + C |
| 4 | DPO v2.0.0 + `cc__payable_open_item` (mirror of Slices 1–2 for AP). | A + C + B |
| 5 | DIO v2.0.0 + `cc__inventory_on_hand`. | A + C + B |
| 6 | Re-enable CCC tile + CFO Pack storyboard §9 coherence assertion #2 once DSO + DPO + DIO all produce honest values. | F |
| 7 | Apex demo-readiness triage refresh — flip Tier-A DSO/DPO/CCC from RED to GREEN; restore M3 narration to real DSO. | demo workstream |

## Stop conditions

- **Y1** — Real SAP tenant data fails to emit `AUGDT`/`AUGBL`: halt; the source-feasibility check (done on bc-sdg) is necessary but not sufficient. Verify on every real-source onboarding.
- **Y2** — Engine cannot preserve Invariant IV under Mechanism A: halt and re-design grammar. (Not expected — Mechanism A is trivially compliant.)
- **Y3** — A mechanism requires in-place mutation of historical COs (Invariant III violation): reject that mechanism. **Already applied to Mechanism C in this scoping.**
- **Y4** — Storyboard owner demands DSO v2.0.0 before Mechanism A's Slice 1 lands: hard stop. The Collection Pressure rename + AR Aging WA fallback per the DSO MWR Demo Positioning is the demo-safe posture until Phase 2 completes.

## References

- DEC-c012c0 (D400) — Metric Contract grammar v1.1 — per-variable temporal input selection. **NOT superseded by this ADR; layered pair.**
- DSO MWR — `bc-docs-v3/docs/onboarding/metric-work-records/days-sales-outstanding/2026-05-11-grammar-design-SES-b7db1a.md` — §Phase 2 Architecture Scoping (committed 2026-05-11, `9f0ce57`).
- total_revenue MWR — `bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-11-total-revenue-production-gap-SES-1c080e.md` — proves the chain works end-to-end when source coverage is right; validates the Design-From-Tenant-Data Guardrail; closes the total_revenue arc (Slices 1–1h).
- ADR-c012c0 §Successor — three candidate mechanisms originally named.
- Scoping draft — `barecount-devhub/.claude/adr-draft-open-item-as-of-canonical-semantics.md` — full mechanism comparison table, source-feasibility probe evidence, and 5-question scoping checklist.
- Apex demo-readiness triage — `bc-docs-v3/docs/operations/apex-cfo-pack-demo-readiness-triage.md`.
- Foundation invariants — `bc-docs-v3/docs/foundation/the-invariants.md`.
- Metric Workstream Playbook — `bc-docs-v3/docs/onboarding/metric-workstream.md` §5 Live MC Safety Workflow, §10 anti-patterns, §11 record triggers.
- Source-feasibility evidence — bc-sdg `CustomerOpenItemSet` V2 endpoint at `http://localhost:6200/sdg/apex-motors/CustomerOpenItemSet`; fields include `AUGDT`, `AUGBL`, `BUDAT`, `BLDAT`, `KUNNR`, `DMBTR`, `WRBTR`, `BSCHL`, `KOART`, `BLART`, `ZFBDT`, `ZTERM` (probed 2026-05-11).

## Consequences

**Positive:**
- DSO, DPO, DIO, CCC become honestly authorable under Foundation invariants without SDG tuning, read-model compensation, or engine semantic changes.
- ADR-c012c0's grammar v1.1 firewall (excluding `at_period_end` against legacy CCs) is preserved; the new CC family is the principled re-admission path.
- Generalizes by inspection — same pattern applies to every balance domain.

**Negative / accepted costs:**
- Largest contract-surface change among the three candidates (2 new CCs + 2 OCs + canonical_mapping + cc_field_mapping per balance domain).
- Per-MC version bumps required to bind the new CC families (DSO v2, DPO v2, DIO v2).
- Mechanism A does not provide a single-CC-identity story; the open and cleared events live in separate CCs (intentional, but worth flagging for operators who would prefer Mechanism B's single-identity model).

**Risks (named for future operators):**
- Real SAP tenants whose extracts do not honestly emit AUGDT/AUGBL would silently produce "all open" or "all cleared" COs. Verify per-tenant during onboarding.
- Engine bind-resolution for MCs binding two CCs from the same family (`cc__receivable_open_item` + `cc__receivable_cleared_item`) must not double-count amounts. Mitigation: per-binding alias + per-binding filter, validated in DSO Phase-2 Slice 2.


