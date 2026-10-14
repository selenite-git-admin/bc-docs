---
uid: DEC-3926bf
title: "Kaveri sub-ledger admission-completeness: extend the observation (A) + canonical (C) projection to carry the catalogued sub-ledger fields; Metric Contracts unchanged"
description: "Kaveri sub-ledger admission-completeness: extend the observation (A) + canonical (C) projection to carry the catalogued sub-ledger fields; Metric Contracts unchanged"
status: proposed
date: 2026-10-14T09:50:44.785Z
project: bc-core
domain: contracts
subdomain: admission-projection
focus: sub-ledger projection-binding extension (A+C) for the Kaveri Wave-1 metrics; MCs unchanged
related_adrs: [DEC-c48b0f, DEC-fa7c63]
---

# Kaveri sub-ledger admission-completeness: extend the observation (A) + canonical (C) projection to carry the catalogued sub-ledger fields; Metric Contracts unchanged

## Context

Platform's Track-2 design (artifacts/platform/kaveri-subledger-admission-completeness/DESIGN-projection-extension-2026-10-14.md @52b93d08, sha256 20ea9f6e; Chief + Architect byte-verified), routed for the Foundation gate + ADR.

Problem (grounded, read-only): the AP aging/overdue/partner/term and AR overdue/concentration/paid/credit-term/write-off metrics cannot materialize on Kaveri because the sub-ledger surface is NULL across all admitted facts — on fact.so_sc_snedd_v1_0_0 (28,928 JE lines, the clean post-dump v3_lc5 load) partner_id, amount_residual, amount_currency, date_maturity, reconciled, account_code/name are 0/28,928 non-null; only the GL-balance surface is populated.

Root cause = a PROJECTION-BINDING gap at repair location A (observation/admission) + C (canonical projection), NOT a source gap and NOT a run-scope issue. (1) The source catalog HAS the fields: source.source_field registers partner_id/amount_residual/date_maturity/invoice_date/full_reconcile_id on account.move.line and partner_id/amount_residual/invoice_date/payment_state on account.move. (2) The active line OC d702580d (oc-h827j v1.1.0) body.field_mappings projects ONLY the 13 balance-surface fields; the sub-ledger fields are never declared; contract.observation_field_map is EMPTY for all 13 OCs (the projection lives in the OC contract_json.field_mappings + so_schema, and the flavor-level admission contract body is validation rules only). (3) The only run filter was a row filter (parent_state=posted), not a field filter — re-running the same contracts re-admits the same balance-only surface. So the fields are catalogued but never DECLARED in the projection.

Foundation gate (DEC-79b62f) — PASS. (1) Why A+C? The projection declaration is the gap: observation (A) under-selects and canonical (C) doesn't carry the fields. (2) Why not an upper layer? The source already catalogues the fields, so A/B (source contract) is not underspecified — CONDITIONAL on the LC5 value-population verify (catalogued does not equal populated; see the gating precondition D4). (3) Why not a lower layer? D/E/F cannot evaluate/store/read fields never admitted; a read-model or evaluator patch would be forbidden lower-layer compensation. (4) Design or execution act? DESIGN act (DEC-c48b0f): the projection never DECLARED the fields; a bare re-run would not fix it. Invariant check: no formulas tied to fact shape; the Metric Contracts already declare their semantic inputs (concepts: AR amount abe0d7d7, AP amount ae6e6528, maturity b63b335e, payment-term 9c4ac8e4, invoice/partner identifiers), so the sub-ledger surface enters via binding (C) and the MCs need NO edits (the onboard-through-binding-without-MC-edits discipline).

## Decision

D1 — Extend the OBSERVATION projection (repair A). Author new strict-backward versions of the line OC d702580d (oc-h827j) and the account.move header OC 45f8b60c, extending body.field_mappings + so_schema to project the catalogued sub-ledger fields: line — partner_id, amount_residual, amount_currency, date_maturity, reconciled/full_reconcile_id; header — partner_id, invoice_date, invoice_date_due, payment_state, amount_residual. Add matching admission-contract field_rules for the new fields where the AC requires them. The extension is additive (strict_backward per the OC compatibility_policy), so Invariants II/III hold (no reordering; new append-only versions). SOP: observation-contract-creation + source-and-admission-contract-creation.

D2 — Extend the CANONICAL projection + binding (repair C). Extend the canonical contract projection (co_cc_*) to carry the new fields as canonical characteristics, and bind the metric variables' concepts to them. This is the C half (co_cc_* currently has zero sub-ledger columns).

D3 — Metric Contracts UNCHANGED. The fields resolve through C-binding; the MCs already declare their semantic inputs, so no MC/formula edit is permitted or required (the new-source / onboard-through-binding rule).

D4 — GATING PRECONDITION (the Foundation gate's condition): the LC5 value-population verify (Demo owns, LC5 up, read-only) must confirm v3_lc5 actually POPULATES the fields (non-null partner_id/amount_residual/date_maturity/full_reconcile_id on asset_receivable lines; invoice_date/invoice_date_due/payment_state on out_invoice headers). Catalogued does not equal populated. If LC5 does NOT populate them, this A+C ruling does NOT hold — the gap is then upstream (source extraction/origin) and Track 2 STOPS pending that re-grounding.

D5 — DELIVERY GATING (not part of this design act). The admission run that follows is a tenant-plane LIVE WRITE (observe+admit from v3_lc5, superuser identity, reader d24f928a) and is OPERATOR-GRANT-GATED, pinned by a byte-precise manifest separately. In addition, the re-admission must SUPERSEDE the prior run's facts by explicit reference rather than double-admit — see the header-supersession ruling (bound to TSK-564901, the Invariant-IV world-stamp). So delivery is gated on: (a) the LC5 value-population verify (D4); (b) the operator admission grant; (c) the supersession mechanism (an explicit current-run / world reference; TSK-564901).

D6 — Header earlier-world contaminant. fact.so_sc_929yc headers are 100% pre-dump earlier-world (09-23 run 35d1c701 + 09-27 run 67512fe1; the 09-28 refresh admitted 0 — immutability refused it). Their supersession by a clean v3_lc5 re-admission is NOT automatic and is ruled separately (the header-supersession Foundation ruling, bound to TSK-564901); this ADR authorises the projection extension, not the contaminant retraction.

Status proposed; Chief-routed; Foundation-gated above. This is a governed contract act (new OC/AC/canonical versions) — authored through the SOP, reviewed, and proposed-until the operator decision grant. No build, no contract act, no run until the LC5 verify + the operator grant.

## Amendment 1 (2026-10-14) — numerator-concept dispositions; A+C scope narrowed to the predicate surface

Platform/Demo's numerator grounding (via Chief) refines this ADR's scope. The A+C projection extension is for the PREDICATE sub-ledger surface, NOT the metric numerators.

- AP numerator (concept ae6e6528) is ALREADY on an active canonical contract (8a1a1f1a) — NOT a gap and OUT of this ADR's A+C scope. The AP aging/overdue/partner/term metrics are blocked ONLY by their PREDICATE concepts (date_maturity, amount_residual, partner_id) — which are exactly the sub-ledger surface this ADR projects (A+C). So the AP block is predicate-only.

- AR numerator meaning ruling (Inv I; DEC-fa7c63 authoritative). The faithful standard "AR balance" = the OUTSTANDING (posted, net) receivable-control balance = concept bec557eb ("posted amount"), DEC-fa7c63 D-3 (stock_at_period_end) — already realized and validated 5/5 by receivable_control_balance. The AR numerator currently bound, abe0d7d7 (char b1621570, GROSS amount, document-level, tax-inclusive), is DEC-fa7c63 D-4's EXPLICITLY-DIFFERENT metric ("the gross of any not-yet-cleared invoice" / open-item face value), which D-4 says is "not silently redefined; its successor is a governed MCV act (U9.5)." THEREFORE the AR numerator is NOT a sub-ledger-line A+C gap: it is a C-level identity/meaning question — disposition pending the directory-intent + duplication check routed to Metric (MSG-84a9b8): (a) keep a distinct gross/open-item metric (own name+definition; needs a SEPARATE invoice-header gross+tax A+C, not the sub-ledger lines); (b) retire/supersede ar_balance (receivable_control_balance already serves the outstanding role; one-active-per-identity); or (c) rebind ar_balance to bec557eb (C-only) + reconcile one-active-identity. No silent rebind — any meaning change is a governed MCV act (D-4).

- SCOPE (narrowed): DEC-3926bf's A+C projection extension covers the PREDICATE sub-ledger fields only (line: partner_id, amount_residual, amount_currency, date_maturity, reconciled/full_reconcile_id; header: partner_id, invoice_date, invoice_date_due, payment_state, amount_residual). The AP/AR NUMERATORS are out of this A+C (AP already active; AR is a C-level identity/meaning question per above, or a separate gross-header A+C only under disposition (a)).
