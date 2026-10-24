---
uid: DEC-7dca63
title: "Extend observed-never-converted currency to the GL / journal-entry-line chain (cc-x13pb) so the per-LE DSO evaluates through the governed evaluator — amends DEC-6e951e"
description: "Amends DEC-6e951e (not supersede): extends its observe→project currency pattern + fail-closed gate from the Customer-Invoice chain to the GL chain cc-x13pb carrying the DSO family, so receivable_days_sales_outstanding + its local_currency amount upstreams stop failing MC_DEFECT_LOCAL_CURRENCY_MISSING and validate governed vs LC5. No BareCount FX."
status: proposed
date: 2026-10-24T17:07:48.420Z
project: bc-core
domain: metrics
subdomain: metric-contract/currency
focus: grammar
---

# Extend observed-never-converted currency to the GL / journal-entry-line chain (cc-x13pb) so the per-LE DSO evaluates through the governed evaluator — amends DEC-6e951e

## Context

DEC-6e951e (decided 2026-10-20) already resolves the multi-currency fork — BareCount never converts (DEC-7bccf6); option B plus the source's own booked local-currency amount — and already decides a fail-closed currency gate at runtime, lifecycle/certification/activation, read-model freshness and authoring (its D4 a–d). So there is NO fresh A-vs-B-vs-C decision to make; re-deciding it would re-open locked doctrine. The genuine residual, surfaced during the per-LE DSO prove-one (TSK-17a8bf), is that DEC-6e951e scoped its observe (D1) and project (D2) acts to the Customer-Invoice chain (oc-3kgrr / cc-das36). The General-Ledger chain that actually carries the DSO family — journal_entry_line, grain CC cc-x13pb — projects no currency field in either 2.0.0 or 3.0.0, so MetricEvaluationOrchestrator fails closed with MC_DEFECT_LOCAL_CURRENCY_MISSING for the DSO and its amount upstreams (both declared aggregation_currency_code='local_currency'). The per-LE DSO is therefore only provable today by SQL recompute, never through BareCount's own governed mechanism — the real blocker to a governed-evaluator Validated-vs-LC5 verdict. This amendment extends DEC-6e951e's observe→project pattern to the GL chain. DESIGN ONLY; it authorizes no build, OC/CC authoring, activation or live act. Grounded 2026-10-24 at bc-docs origin/main c327c94; governing authority DEC-ffbc24/D673.

## Decision

This **amends DEC-6e951e** (decided 2026-10-20) and does **not** supersede it. DEC-6e951e resolves the currency fork (no BareCount FX; option B + source-booked local currency) and decides a fail-closed currency gate at runtime, lifecycle, read-model and authoring (its D4 a–d), but scopes its projection acts (D1 observe, D2 project) to the Customer-Invoice chain (oc-3kgrr / cc-das36). The General-Ledger chain that carries the DSO family — `journal_entry_line`, grain CC `cc-x13pb` — projects no currency field in 2.0.0 or 3.0.0, so the governed evaluator fails closed with `MC_DEFECT_LOCAL_CURRENCY_MISSING` for `receivable_days_sales_outstanding` and its amount upstreams (`receivable_billed_amount`, `receivable_control_balance`, both `aggregation_currency_code='local_currency'`). This amendment extends DEC-6e951e's observe→project pattern to the GL chain so the DSO family evaluates governed and can be Validated-vs-LC5.

**D1 (GL). Observe currency on the journal-entry-line (repair A; mirror DEC-6e951e D1).** A new OC version on the GL chain observes the source's document currency, company currency and booked company-currency amount — Odoo `account.move.line` exposes `currency_id`, `company_currency_id`, `amount_currency` (document) and `balance` (company). ISO 4217 codes are dereferenced through two separate, explicitly named secondary `res.currency` legs (`currency_id`→`id`, `company_currency_id`→`id`), each pinned and resolving exactly one code, never one conjunctive join (DEC-ea4523 (3), DEC-0a187d) — exactly as DEC-6e951e D1. An unresolvable key is a recorded refusal. **Precondition:** if the GL OC does not yet observe the source company/currency keys, the Layer-A observation fix (a new OC version that fetches them) comes first, per DEC-ffbc24 §4 sequencing; this amendment does not presume the GL OC already fetches them.

**D2 (GL). Project currency on cc-x13pb (repair B; mirror DEC-6e951e D2).** A new major `cc-x13pb` version projects `currency_code` (document) and `local_currency_code` (company), plus the source-booked company-currency amount field(s) the DSO upstreams consume. `local_currency_code` must equal the row's resolved LE functional currency; a mismatch is a recorded `local_currency_mismatch` refusal, per DEC-6e951e. **As-of caveat (Codex gen-e5fc38-01):** the DEC-4aa1ff D10 posting-date-as-of resolution is NOT yet implemented — `local-currency-cross-check.ts` checks the LE's **current** functional currency, and the as-of revision is pending `TSK-739801`. Until D10 lands, any interim single-LE / time-invariant proof must carry the **current-not-as-of** evidence label and **refuse** a historically changed functional currency; the as-of form is an execution dependency on TSK-739801, not a claim this ADR presumes. Local-currency aggregation never spans LEs (DEC-4aa1ff D5).

**D3. Policy of the DSO family (the semantic design act).** The two amount upstreams KEEP `aggregation_currency_code='local_currency'`: they aggregate the source's own booked company-currency amount — no FX (DEC-7bccf6). The DSO ratio itself stays `not_applicable` (a days figure, not a currency amount). The alternative — flipping the upstreams to `document_currency` or `single_currency_required` — is **REJECTED**: it changes the metric's declared meaning (a per-currency or single-currency receivable balance is not the DSO family's meaning) and is lower-layer compensation for the missing projection. GL-line sign semantics (debit/credit → signed `balance`) are a declared meaning, proven against source rows through the LC5 seam before any re-author, not assumed (mirror DEC-6e951e).

**D4. The fail-closed gate is unchanged and already decided.** DEC-6e951e D4 (runtime refuses; lifecycle/cert/activation refuse; read-model freshness; authoring refuses) governs this chain too. This amendment adds **no** new gate: it supplies the CC projection the existing gate **requires**. Supplying the projection **targets** moving the GL chain off `MC_DEFECT_LOCAL_CURRENCY_MISSING` toward green — it is not, by itself or by this proposed ADR, a green/Validated-vs-LC5 verdict. The execution unit must still prove, before any green or Validated-vs-LC5 claim: the observed fields; two unique `res.currency` code resolutions; the source-booked signed amount and its sign; per-row currency presence and per-row LE-equality of `local_currency_code`; and the evaluator + lifecycle gates passing. No amber-advisory path is introduced.

## Invariants engaged

- **I — meaning produced once at its boundary:** currency is observed at the observation boundary, never converted at a lower layer.
- **VI — evidence emitted, not inferred:** no FX inference; the source's own booked company-currency figure is authoritative.

Consistent with DEC-7bccf6 and DEC-6e951e.

## Foundation gate (DEC-79b62f)

1. **Why location B (CC projection), with an A precondition?** The GL grain CC must project currency; `account.move.line` exposes it at source, so the primary gap is the projection (B). If the GL OC does not yet observe currency, the A fix (new OC version) precedes it (D1 precondition).
2. **Why not an upper layer alone?** The currency semantics (observe-never-convert; per-row validity) are already fully specified by DEC-6e951e / DEC-7bccf6. This is their application to a second chain, not a new semantic at A.
3. **Why not a lower layer?** Flipping the upstreams to `not_applicable`/`single_currency_required`, or summing blind, is lower-layer compensation that changes metric meaning — refused (D3).
4. **Design act or execution act (DEC-c48b0f)?** The general obligation (any currency-denominated MC's grain CC must project the field its policy needs) is already decided (DEC-6e951e D4(d)). The DESIGN ACT this amendment names is the SEMANTIC call — that the GL/DSO receivable upstreams take the `local_currency` source-booked policy (not document/single) and the GL-line sign meaning — and the choice to extend projection scope to the GL chain by a recorded amendment rather than silent execution.

## Scope and status

Scope: the GL / `journal_entry_line` chain (`cc-x13pb`) and the DSO family (`receivable_days_sales_outstanding` + its two amount upstreams). It does **not** re-open DEC-6e951e's decided fork or gate, and authorizes no build, OC/CC authoring, activation or live act — each keeps its own SOP rail + review + operator gate. **Status: proposed**; it is additive (amends, not supersedes); DEC-6e951e stays decided. Ratification is the operator's recorded grant.

## References

DEC-6e951e (observed-never-converted currency + fail-closed gate — the ADR this amends); DEC-7bccf6 (no platform FX; source-booked amount authoritative); DEC-f4b2b0 / D495 (aggregation_currency policies); DEC-ea4523 (3) + DEC-0a187d (secondary observation legs / code dereference); DEC-4aa1ff (LE functional currency D10; no cross-LE aggregation D5); DEC-ffbc24 §4 (Layer-A observation sequencing); Foundation `the-invariants.md` I, VI; TSK-17a8bf (the `MC_DEFECT_LOCAL_CURRENCY_MISSING` blocker this closes).
