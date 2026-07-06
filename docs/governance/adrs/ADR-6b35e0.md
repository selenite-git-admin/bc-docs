---
uid: DEC-6b35e0
title: "Source vocabulary discipline at the Metric Contract boundary"
description: "MC filter clauses must not bind to source-system-specific document codes such as SAP BLART, SHKZG, etc. Source codes belong at OC via a code_lookup value-map; MC filters bind to canonical concepts with canonical value sets. document_type_code is diagnostic, not strategic-filter. Existing cleared_invoice_amount remains active but transitional pending a canonical-event successor."
status: decided
date: 2026-06-13T07:00:38.058Z
project: bc-core
domain: mcf
subdomain: metric-contract-semantics
focus: governance
---

# Source vocabulary discipline at the Metric Contract boundary

## Context

The BareCount evaluation chain has six boundaries: Source → Reader → SO → Canonical Resolution → CO → MC → Snapshot. Foundation Invariant I requires meaning be produced once, at the canonical evaluation boundary. The CLAUDE.md cross-system portability hard rule (also D430 §10) requires that the same MC must onboard a second source system through the binding layer (C) without MC edits.

During B1a Finance Package v0 (2026-06-11..2026-06-13), two filtered metrics surfaced an asymmetry:

1. `cleared_invoice_amount` was M14-activated (MC `2bda5252-5648-4e78-bcfd-6f8e3f98e155`, MCV `57ea07d0-120d-484b-a099-fd43fdb008fe`) with filters `document_type_code='DR'` (a SAP BLART source literal, bound to BC `f10afed1-499f-4cb8-9582-02067db6eb4b` on Customer Invoice grain) AND `clearing_date IS NOT NULL`. This is the first and only MC in the substrate carrying any filter clauses (ARPI and billing_volume carry zero).

2. `cleared_customer_payment_amount` was intended as a literal-only DR→DZ variation. The M12 panel instead proposed a Customer Payment grain metric using `status='cleared'` (canonical lifecycle vocabulary on Customer Payment's status BC `5c105543`, whose definition explicitly lists canonical codes: received, in-clearing, cleared, returned, reversed). The Maker's reasoning called this "the BCF-canonical translation of BLART='DZ' restricted to the cleared lifecycle state." The proposal is NOT advanced past panel state pending this decision.

A read-only Foundation audit (2026-06-13) found:

- **Grammar layer for value translation** lives at OC `field_mappings.transform='code_lookup'`, but `transform_params` shape is unspecified in `observation-v2.schema.json` — the grammar stub exists, the value-map authoring surface does not.
- **CC layer** carries `concept_id` per field but has no `canonical_value_set` semantic rule and no flag distinguishing strategic-filter from diagnostic-only concepts.
- **MC layer** has no PE-MC sensor for source-vocabulary literals. PE-MC-11 checks concept-identity coverage (D439) but not literal content. cleared_invoice_amount passed PE-MC-9 and PE-MC-11 cleanly because the gates have no semantic sensor for "literal is source-shaped."
- **Active `document_type_code` BC** (`f10afed1`, minted 2026-06-13 in B1a P0) hard-codes SAP BLART vocabulary inside its canonical-concept definition ("e.g. SAP BLART discriminating invoice-side records (DR) from payment-side (DZ, DG) on the same cleared-item surface (BSAD/BSAK)").
- **Customer Payment has no CC.** PE-MC-11(i) determinism check would fail for any Customer Payment metric before any source-vocabulary question.
- **B1a slice plan §4** explicitly chose source-literal authoring as scope-driven, not principled: "the invoice-vs-payment distinction is METRIC semantics → MC filter_clauses" with the alternative "OC-grammar slice-predicate extension (real option, but a contract-grammar DBCP — out of B1a scope)."

**Cross-system portability test fails for cleared_invoice_amount:** a second source system (Oracle Fusion, NetSuite) cannot reproduce this MC without either an MC edit (forbidden) or fabricating a `'DR'` value from a non-SAP reader (lower-layer compensation, forbidden).

## Decision

**MC filter clauses must not bind directly to source-system-specific document codes** such as SAP `BLART`, `SHKZG`, or analogous classifiers in other source systems. Translation from source values to canonical values belongs at the OC layer via a `code_lookup` value-map mechanism. The MC layer declares numeric assertions over canonical concepts and canonical values.

Six specific rules:

1. **Source codes** (e.g. `BLART='DR'`) may appear in OC `field_mappings` as the source vocabulary the reader observes, and in OC `code_lookup` value-maps as input keys. They may NOT appear as MC `filter_clauses[].literal_value_json`.

2. **Canonical MC filter literals** must come from a canonical value set declared at the CC layer (`canonical_value_set` semantic rule — schema extension pending). Example: `receivable_event_kind ∈ {customer_invoice, customer_payment, credit_memo, debit_memo}` — canonical names, source-agnostic.

3. **`document_type_code`** (BC `f10afed1`) is to be reclassified as `semantic_role='diagnostic'` once the BCF `semantic_role` field ships (TSK below). Diagnostic BCs may be queried for audit/observability but may not be used in MC `filter_clauses[].bound_business_concept_id`.

4. **OC `transform='code_lookup'`** receives a parameter shape: `value_map` (source value → canonical value) plus `unmapped_policy ∈ {reject, diagnostic_only}`. The CO emitted by canonical evaluation carries the translated canonical value; the MC filters on that.

5. **New PE gate** (PE-MC-12 or PE-MC-11 extension) detects MC filter clauses that bind to BCs with `semantic_role='diagnostic'` OR use literal values not present in the bound BC's CC-declared `canonical_value_set`. Verdict: REJECT with `mc_filter_uses_diagnostic_bc` or `mc_filter_uses_source_vocabulary`.

6. **Existing `cleared_invoice_amount`** remains operationally active. It is annotated as **Foundation-transitional**. It will be superseded by `cleared_customer_invoice_amount_v2` via the metric-mcv-rebind service once the canonical `receivable_event_kind` BC and the OC `code_lookup` parameter shape exist. The current M14 cert is preserved as the PR-C technical proof of filter materialization (which it correctly is — the materialization grammar shipped correctly; this ADR addresses WHAT the substrate stores, not WHETHER it stores it). No retroactive supersession or archival.

7. **`cleared_customer_payment_amount` panel proposal** (panel_run `ccc85a3b-14e8-4486-8933-5ece1d184df9`) is retained as a design signal validating the Maker's BCF-canonical intuition. NOT advanced to M12.5/M13/M14. Will be re-authored once Customer Payment OC + CC exist.

## Consequences

**Accepted:** Pause Finance Package filtered-metric authoring until the substrate ships: BCF `semantic_role` field, OC `code_lookup` parameter shape, PE-MC-12 gate, canonical `receivable_event_kind` BC, Customer Payment OC/CC. Slower B1a throughput over the next sessions. The first source-vocabulary metric (cleared_invoice_amount) remains in production with a transitional marker until its successor lands.

**Avoided:** A second source-vocabulary metric propagating the misalignment. Cross-system portability claim collapsing the first time a non-SAP source system is onboarded. Hand-litigation of "source vs canonical" on every future filtered metric.

**Not affected:** Filter-clause materialization grammar (PR-C, merged at f318099) — that is mechanically correct and durable. `cleared_invoice_amount`'s operational behavior — it remains active and continues to compute when runtime is invoked. ARPI, billing_volume, and all other zero-filter metrics — unaffected.

## Rejected alternatives

- **Continue source-literal authoring with explicit waiver** — Sets precedent every next metric inherits; hollows the portability claim.
- **Auto-translate at engine runtime** — Boundary violation; meaning produced at evaluation, not at the metric boundary.
- **Forbid all literals in MC filters** — Too restrictive; `clearing_date IS NOT NULL` is a legitimate canonical literal.
- **Allow source-OR-canonical, choose per metric** — Once one MC uses source vocabulary, the cross-system property is gone.

## Follow-up

Six new tasks track the implementation; none ships before this ADR reaches `decided`. Plus scope extensions to TSK-f9910a (seed-author surface) and TSK-05bd03 (contract-successor planner). Task UIDs filed in the same DevHub session as this decision record.

## References

- `bc-docs-v3/docs/foundation/the-invariants.md` (I, IV)
- `bc-docs-v3/docs/foundation/the-evaluation-boundaries.md` (boundary-independent rules)
- `bc-docs-v3/docs/foundation/the-contract-grammar.md` (§Metric Contract responsibilities)
- ADR-a6258b (D430 — concept-identity at CC); ADR-4a17e0 (D431 — author-time O↔C consistency); ADR-1002c9 (D439 — PE-MC-11 policy)
- B1a slice plan: `bc-core/scripts/audit-output/b1a-cleared-item-slice-plan-2026-06-12.md` (§4 source-literal authoring as scope-driven decision)
- PR-C packet: `bc-core/scripts/audit-output/m12.5-filter-clause-materialization-packet-2026-06-13.md`
- Substrate evidence: MC `2bda5252-5648-4e78-bcfd-6f8e3f98e155`, MCV `57ea07d0-120d-484b-a099-fd43fdb008fe`, 2 active `mcf.metric_filter_clause` rows with source-literal `'DR'`; panel_run `ccc85a3b-14e8-4486-8933-5ece1d184df9` (Customer Payment grain proposal with canonical `status='cleared'`)
- Session note: `bc-core/scripts/audit-output/b1a-p1c-2-cleared-customer-payment-amount-pause-2026-06-13.md`
