---
uid: DEC-a5b226
title: "GL-account classification is a mandatory, shape-triggered source-onboarding step (DERIVE-vs-DECLARE); account code/prefix is not a valid derive"
description: "Make GL-account classification (trade/tax_statutory/other) a mandatory, shape-triggered, conditional source-onboarding step with a DERIVE-vs-DECLARE rule, serving the 7-metric receivable+payable trade family; account code/prefix is not a valid derive classifier."
status: proposed
date: 2026-10-14T07:45:30.474Z
project: bc-core
domain: contracts
subdomain: source-onboarding
focus: mandatory shape-triggered GL-account classification onboarding step with derive-vs-declare
related_adrs: [DEC-c46354, DEC-2a6176, DEC-fa7c63, DEC-c48b0f]
---

# GL-account classification is a mandatory, shape-triggered source-onboarding step (DERIVE-vs-DECLARE); account code/prefix is not a valid derive

## Context

The GL-account-classification step (trade / tax_statutory / other) that classify_by_binding (DEC-c46354/D515) and the trade-metric family consume is ABSENT from every onboarding SOP — source-registration.md, source-and-admission-contract-creation.md, tenant-onboarding.md, reader-creation.md all carry effectively no classification step (Chief live grep; Architect re-confirmed). The classification mechanism is fail-closed (DEC-c46354 D4b: a missing classification refuses resolution, never infers), so a GL-bearing source onboarded without it either hard-fails or gets coarsely template-seeded and silently produces wrong numbers. This is the DSO ~0.35% over-count root pattern (TSK-6c12ac / DEC-2a6176), and it propagates across a 7-metric trade/non-trade family (receivable + payable): receivable_days_sales_outstanding, receivable_control_balance, receivable_billed_amount, days_payable_outstanding, dpo_to_supplier_term_ratio, overdue_payables_amount, overdue_payables_count.

Mechanism grounded (bc-core origin/main). DERIVE = an OC-declared single-field code_lookup value_map (ccv2-canonical-resolver applyCodeLookup; concept-source-reference.ts:45 states transforms are SINGLE-FIELD only — a classification needing multiple raw fields cannot be expressed). DECLARE = classify_by_binding + tenant.gl_account_classification_binding + contract.gl_account_classification_default (DEC-c46354), seeded from platform defaults and confirmed/overridden at source-onboarding via the FSV review, provenance-stamped, fail-closed.

No current defect — this is future-proofing (2026-10-14). The investigation that surfaced this gap (the DSO trade-scope, DEC-2a6176) was pinned against the ADMITTED LC5 facts and found NO defect: the admitted receivable population is a single trade account (Odoo id 53); the tax-receivable account (id 62) is defined but UNPOSTED, so it was never in any trade-metric numerator, and the receivable/payable_subtype facet premise is false in LC5 — DEC-2a6176 was reversed/withdrawn (no fix). This ADR is therefore adopted NOT to fix a present defect but as the general A-boundary home for classification whenever a FUTURE source actually exercises the trade/non-trade asymmetry. Platform's Foundation flag is the standing reason: admission strips the journal / move-origin, so a source that does post a non-trade receivable/payable cannot be scoped at a lower layer and would need exactly this governed admission-time classification. The facet + binding substrate (TSK-aefc76) and the engine leg (TSK-86a70d) therefore stand down UNBUILT and are authored only when such a source arrives.

Foundation self-check (DEC-79b62f). (1) Why this location? A (the admission DERIVE value_map) and/or B+C (the facet declaration + the DECLARE binding) — classification enters at the source/admission boundary where the source meaning is admitted. (2) Why not an upper layer? The trade-scope meanings are already decided (DEC-fa7c63 D-1 for receivables); this realizes them per-source, it does not re-decide them. (3) Why not a lower layer? A metric-layer account filter or a raw-account-id/account-code filter is lower-layer compensation; classification belongs at admission (DERIVE from a governed native classifier) or the governed binding (DECLARE), never a raw identifier. (4) Design or execution act? A design act (DEC-c48b0f): the missing onboarding declaration — how each GL-bearing source's accounts are classified — is named and made a mandatory, shape-triggered step; the per-source value_maps and binding rows are execution. Chief co-signs.

## Decision

D1 — SHAPE-TRIGGERED, CONDITIONAL. The GL-account-classification step is MANDATORY iff the source's admission shape declares a GL-account-bearing concept (a journal-entry-line grain carrying account_type_code / ledger_account_identifier). A source without that concept (CRM, HR, support) never triggers it and is skipped cleanly. The trigger is the PRESENCE of the declared concept, not a manual source-kind flag — it cannot be forgotten and the requirement is derived from the declared shape (Invariant IV), self-consistent with the fail-closed rule (classified metrics only bind to GL-account concepts).

D2 — DERIVE-vs-DECLARE, per source and per classification facet. DERIVE where the source carries the distinction in ONE governed native field expressible as a code_lookup value_map (declare the value_map from that field to the canonical classification; no human declaration, no binding rows). DECLARE where the source does not (the classify_by_binding binding, seeded from defaults and confirmed at source-onboarding via the FSV review). Every facet the source's shape requires must resolve as DERIVE (value_map declared) or DECLARE (binding rows present), or the source fails closed and cannot reach classified-metric evaluation.

D3 — Account CODE / PREFIX is NOT a valid DERIVE classifier. Mapping accounts to a classification by their account code or code-prefix is the raw-account-id path (the T2 prohibition — no lower-layer compensation on a raw identifier) and is source-convention-dependent (a syntactic accident of a chart's numbering, not source-independent meaning, Invariant I). A DERIVE value_map is valid only over a GOVERNED native CLASSIFIER field (e.g. a native account-type / account-nature selection). Where only the code/prefix distinguishes, the path is DECLARE (the governed per-account binding), never a code-prefix value_map.

D4 — The step, and its enforcement. DOCS: add the step to source-registration.md and source-and-admission-contract-creation.md (and tenant-onboarding.md where tenant FSV overrides apply). PLATFORM: wire the fail-closed gate so a GL-bearing source cannot reach classified-metric evaluation until classification is resolved per-facet (DEC-c46354 D4b posture).

D5 — Relationships. Extends DEC-c46354/D515 (the classify_by_binding mechanism and its facets) and the generalization anticipated by its D6; realizes DEC-fa7c63 D-1 (the receivable trade-scope). DEC-2a6176 (the DSO-specific receivable_subtype facet) was REVERSED/withdrawn on 2026-10-14 — its trade-scope over-count does not exist in the admitted LC5 data (see the no-current-defect note in Context); the facet/binding it described is retained conceptually as the FUTURE DECLARE substrate under THIS ADR's general rule, authored only when a real source exercises the asymmetry, and is NOT built now. Does not supersede DEC-c46354 or DEC-fa7c63. Status proposed; Chief co-signs the design act; apply of any DECLARE DB substrate and any decided-status flip remain operator-gated.

## Status

Proposed. Chief co-signed the design act (derive-vs-declare, shape-triggered, conditional classification step). The per-source mechanism selection (DERIVE vs DECLARE) and the DSO-specific sub-case are governed by DEC-2a6176 as amended; this ADR sets the general rule. Decided-status flip and any DB-substrate apply remain operator-gated.
