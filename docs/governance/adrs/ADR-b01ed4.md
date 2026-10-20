---
uid: DEC-b01ed4
title: "The deterministic gate must predict evaluation: green means the spec assembles against the active grain CC, and every closed-set value is canonical at observation, in filters and at runtime"
description: "Sibling of DEC-6e951e for the whole class of a passing hard gate. One shared evaluability decision (the evaluator's own spec assembly, no data read) used by chain status, certification, activation and runtime; closed-value-set conformance (no direct mapping of raw source values onto a closed-set concept; filter and code literals within the canonical set); fail-closed red; a class sweep; the payment_status value map as the instance."
status: decided
date: 2026-10-20T12:53:25.446Z
project: bc-core
domain: metrics
subdomain: mcf/chain-status
focus: integrity-gate
amends:
  - DEC-92f709
---

# The deterministic gate must predict evaluation: green means the spec assembles against the active grain CC, and every closed-set value is canonical at observation, in filters and at runtime

## Context

The hard gate currently approximates evaluability with BCF-existence checks and never compares literals with closed value sets. So it reports green for metrics that refuse at spec assembly, and for metrics that silently match nothing and return a confident 0. Making the evaluator's own spec assembly the single evaluability predicate, and enforcing closed-set conformance where meaning enters (observation) and where it is consumed (metric literals), closes the class by rule instead of by instance.

## Grounding (2026-10-20 at bc-core origin/main and the platform DB)

The deterministic gate is meant to be primary and hard (DEC-92f709). Today it **passes metrics that cannot evaluate, or that evaluate wrongly.** DEC-6e951e D4 closes the currency case; this ADR closes the rest of the class.

1. **Green does not mean evaluable.**
   - `mcv-chain-status.service.ts` `judgeBindingsResolve` checks only that bound and filter-clause concepts **exist and are active in BCF**. It never checks that they are **projected in the active grain CC**, which is what the evaluator's spec assembly (`MetricSpecLoader`) requires.
   - TSK-e5d962 (Metric's readiness probe, 2026-10-19): **34 of 66** metrics are chain-status GREEN, yet none can evaluate. The causes: filter concepts not projected (23), group-by concepts not stamped (2), bound concepts on no active CC field (16).
   - Instance: `credit_note_volume` was GREEN while its filter concept 2785db5b is projected nowhere, so it refused at spec assembly (TSK-ce2a06).
2. **A closed-set value can be non-canonical, and the filter silently matches nothing.**
   - BCF concepts with a `canonical_value_set` (e.g. 0a860227 Customer Invoice status: `{open, in-dispute, paid, partially-paid, written-off}`) are mapped from source fields with **`direct`**, so the CO carries Odoo's raw values (`not_paid`, `partial`, `in_payment`, `paid`, `reversed`, …).
   - A metric filtering `= 'partially-paid'` matches nothing and returns a **confidently wrong 0** that evaluates "complete" and passes every gate (`partially_paid_invoice_count`, TSK-23f9ba).
   - **The class, measured:** **7 active OC mappings** put raw values directly onto closed-set concepts:
     - oc-3kgrr 1.1.0, 1.3.0 and 1.4.0 `payment_state`, and oc-jbpz8 1.0.0 `payment_state`;
     - oc-gc8eb 1.0.0 `account_type` and `internal_group`;
     - oc-vg0zn 1.3.0 `state`. `posted_journal_entry_count` is right only because Odoo's `posted` equals the canonical value.
   - Nothing compares filter or formula code literals with the concept's canonical set.
3. **Amber and stale do not block** (DEC-6e951e D4b/c, adopted here for the whole class).

## Decision

**G1. One evaluability decision, shared, like the D626 parity pattern.**
- The **same pure function the evaluator uses to assemble a metric spec** is the evaluability predicate: bindings and filter concepts resolved against the **active grain CC's** field selection, group-by and stamped fields, temporal anchor and currency field (DEC-6e951e). It reads no tenant data and triggers no evaluation.
- It is called by chain status (a new check `spec_assembles`), certification, activation and the runtime.
- **Inputs (Codex gen-f015aa-01):**
  - the **exact MCV version being judged**: certifying a candidate must never assemble the currently active MCV by accident; the loader takes the version explicitly;
  - the selected active grain CC and its stamped fields;
  - the filter bindings;
  - the group-by count and columns;
  - the temporal gate and anchor;
  - the currency field and policy (DEC-6e951e);
  - the fiscal-LE gate (DEC-4aa1ff, TSK-1ec1a7).
- **Pure compositions** (metric-input-only formulas, D467) keep their no-grain-CC path. G1 uses a composition-aware assembly that checks each upstream input's own G1 status, because the current assembler refuses formulas that resolve to no CO-field variable.
- **GREEN requires it to pass.** A metric that would refuse at spec assembly can never be green. This closes TSK-e5d962 and TSK-ce2a06 as a class.

**G2. Closed-value-set conformance at every boundary** (Inv-I: meaning is produced once, at observation).
- **(a) Observation.** An OC mapping onto a concept with a `canonical_value_set` must be a **`code_lookup`** whose `value_map` targets are ⊆ that set, with `unmapped_policy: reject`. This is the root guard: a raw source vocabulary never reaches a CO as if it were canonical (the document_type_code lesson, now a rule).
  - **The uniform rule (refined per Codex gen-f015aa-01):** a source independently shown to emit the canonical vocabulary is declared with an **explicit identity `code_lookup`** (each canonical value maps to itself). It is never `direct`.
  - So `direct` onto a closed-set concept is refused at OC authoring and activation (`direct_mapping_onto_closed_set`), and correctness never rests on a coincidence (as with oc-vg0zn `posted`).
- **(b) Metric.** Every filter literal, and every formula code literal compared to a closed-set concept, must be ∈ that concept's canonical set. This is refused at MC authoring and reported red by chain status (`literal_outside_canonical_set`).
- **(c) Runtime.** Before filtering, the runtime validates every selected CO's closed-set values against the set. A value outside it is a recorded refusal, never a silent non-match.
  - This also covers **historical COs created under older `direct` mappings**: a new OC mapping does not repair old rows, so they are refused, not mis-counted.
  - A row refused at observation (`reject`) cannot be "rescued" later by a metric filter.
- **A canonical value with no source equivalent** (e.g. `written-off`, `in-dispute` on Odoo invoices) is **source-unsupported**. A metric filtering on it, on a source that cannot produce it, is reported `vacuous:value_not_produced_by_source`, **never** as a validated 0.
  - That verdict is allowed **only** when the source's vocabulary for the field is established (the declared source enumeration) **and** the value map's coverage of it is complete.
  - An **unknown** source value is a refusal, not evidence of absence.

**G3. Fail-closed and fresh.** A failing G1 or G2 check is **red** and blocks certification, activation and evaluation. Freshness is DEC-6e951e D4(c), one mechanism shared by both ADRs: the lifecycle acts **recompute** G1, G2 and the currency predicate at the point of use, and the persisted chain-status row carries a dependency fingerprint. An absent, old or mismatched fingerprint reads as `stale` and is never green.

**G4. Class sweep (execution, after the terms grant).** Re-run G1 and G2 over every active MCV and OC.
- **Expected hits:**
  - the 34 TSK-e5d962 metrics;
  - `credit_note_volume`;
  - the payment_status family (`partially_paid_invoice_count`, `written_off_invoice_count`, `write_off_rate`, `paid_customer_invoice_count__tacorr_86d399ee`);
  - the oc-jbpz8 `payment_state`;
  - the oc-gc8eb `account_type` / `internal_group`;
  - the oc-vg0zn `state` mappings.
- **Remediation is per family, through new OC and CC versions plus metric re-declarations on the SOP rails:**
  - one-then-many;
  - an approved family package per family;
  - no bulk chain generation.

**G5. Instance: the Customer Invoice payment-status value map.** It rides the **DEC-6e951e oc-3kgrr version**, so there is one OC version and one fresh admission. This is the proposed `code_lookup` onto 0a860227:
- `not_paid → open`
- `partial → partially-paid`
- `paid → paid`
- `in_payment → paid` ⚠ meaning point 1
- `reversed → (no canonical value)` ⚠ meaning point 2
- `invoicing_legacy → reject`

`unmapped_policy: reject`. `in-dispute` and `written-off` have **no Odoo source value**: their metrics are source-unsupported on Odoo (G2), not 0.

## Foundation (DEC-79b62f)

1. **Location:**
   - **A/C:** OC mapping conformance is where non-canonical meaning enters.
   - **B:** MC literals.
   - **F/D:** chain status must be the evaluator's own decision, not a parallel approximation.
2. **Not upper:** the BCF concepts and their closed sets are correct, and the sources faithfully report their own vocabulary. The **mapping** and the **checks** are wrong.
3. **Not lower:** a runtime remap of raw values, a "contains" filter or a guessed synonym would be lower-layer compensation. The rule is enforced where the meaning is declared.
4. **Design act** (DEC-c48b0f): declare the conformance and parity rules. The sweep and the per-family fixes are execution acts.

**Invariants:**
- **I:** canonical meaning is produced once, at observation.
- **IV:** values are explicit references into the declared set.
- **VI:** "green", "complete" and "0" are emitted only when true; a non-produced value is reported as such, never inferred as 0.

## Needs an operator decision (meaning, for G5)

1. **`in_payment` → `paid`?** Odoo `in_payment` means a payment is registered but not yet bank-reconciled; from the receivable's side the customer has paid. Recommended: yes.
2. **`reversed`** (the invoice was fully reversed by a credit note) has no canonical status value. Either:
   - (a) add a canonical value `reversed` to 0a860227 through the governed BCF amendment (recommended); or
   - (b) leave it unmapped, so such rows are refused and must be excluded by filter upstream.
3. **Confirm** that metrics on `written-off` / `in-dispute` are reported **source-unsupported on Odoo** (not 0, not validated). Recommended: yes.

## Relationship

Sibling of DEC-6e951e (it shares the D4c staleness mechanism). It extends DEC-92f709 (the deterministic gate is primary) to the accuracy class. It closes TSK-e5d962, TSK-ce2a06 and TSK-23f9ba by rule. The DEC-4aa1ff fiscal-LE gate (TSK-1ec1a7) becomes one more G1 input: the legal entity is resolvable.
