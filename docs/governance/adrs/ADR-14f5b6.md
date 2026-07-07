---
uid: DEC-14f5b6
title: "Measurement semantics for amount and quantity Business Concepts — currency is row-data, vocabulary declares the dependency"
description: "Amount-role BCs are classed monetary (mandatory currency-context sibling reference) vs fixed_unit (unit field, never ISO 4217); quantity BCs require UOM context; engine enforces mixed-currency refusal at PE-MC against mcv.aggregation_currency_code. Schema columns DBCP-deferred per DEC-a6258b precedent."
status: decided
date: 2026-07-06T15:15:20.761Z
project: bc-core
domain: contracts
subdomain: vocabulary/measurement-context
focus: schema
---

# Measurement semantics for amount and quantity Business Concepts — currency is row-data, vocabulary declares the dependency

## Context

The currency-mixed-sums pitfall is GAP-CONFIRMED on pilot1 (TSK-e2a32b) and every future amount metric inherits whatever this decision says — deciding before further amount-metric authoring is the cheapest point of intervention. The three-layer split (vocabulary declares the dependency, binding resolves it, engine enforces it) is the only shape that satisfies Invariant I (meaning evaluated once at its boundary): currency denomination is observed per row, the dependency between an amount and its denomination field is vocabulary-stable across sources, and refusal/conversion is evaluation-time behavior. Mirrors two locked precedents: DEC-61850f (role-conditional mandatory metadata at admission) and DEC-a6258b (grammar decision now, schema DBCP deferred). Quantities get the same treatment because the three-way-match metrics (billed vs ordered vs received quantities) are the next family exposed to silent unit mixing.

## Decision

Context. The BCF audit (SES-f08fa5, barecount-devhub/.claude/bcf-audit-2026-07-06.md gap G2) measured: 82 of 88 amount-role Business Concepts carry unit NULL with no currency-context declaration of any kind, and every quantity-representation BC (ordered/delivered quantity across GR/PO/SO Lines, Production Run) has neither a unit nor a UOM sibling concept. This is the vocabulary end of the GAP-CONFIRMED currency-mixed-sums pitfall (TSK-e2a32b): every live amount metric sums EUR+INR document amounts raw, masked on pilot1 only by SDG emitting wrbtr==dmbtr. The six amount BCs that DO carry a unit carry 'days'/'hours' — durations, a different measurement class conflated into the same NULL-unit convention.

Decision (five rules, grammar-level; schema application deferred to a DBCP):

1. **Currency is row-level observation data, never concept-level vocabulary.** A monetary amount's denomination varies per document/row; stamping an ISO 4217 code into business_concept.unit would assert a fact the vocabulary cannot know (Invariant I — meaning evaluated once, at the right boundary). The `unit` column is therefore RESERVED for fixed-unit measures (days, hours, percent, ratio) and is FORBIDDEN from ever carrying a currency code.

2. **Amount-role BCs are classed** `monetary` or `fixed_unit`. A `monetary` BC MUST declare a currency-context dependency: an explicit reference to the sibling currency-code dimension BC on the same entity that gives each row's denomination (e.g. Supplier Invoice × net amount → Supplier Invoice × currency code). A `fixed_unit` BC MUST populate `unit`. Admission gate: an amount-role candidate that declares neither is refused (mirror of the DEC-61850f `bc_strategic_role_missing_canonical_value_set` rule).

3. **Quantity-representation BCs MUST declare UOM context**: either a reference to a UOM dimension BC on the same entity (the governed atom `unit of measure code` already exists, currently zero-use) or a fixed `unit` where the quantity is genuinely dimensionless (counts). Same admission-gate mechanics.

4. **Engine enforcement lives at D, not B.** PE-MC (joint with TSK-e2a32b): a period_aggregate over a `monetary` variable binding MUST either (a) group by / filter to a single currency, (b) declare governed conversion into `mcv.aggregation_currency_code` via the Currency Exchange Rate substrate, or (c) refuse with a typed error (`mixed_currency_aggregation`). The vocabulary declaration (rule 2) is what makes this gate computable — the binding layer resolves the amount concept's declared currency-context concept to the CC field that carries each row's denomination.

5. **Schema application is a DBCP, not this ADR** (DEC-a6258b precedent — grammar decision now, implementation deferred): proposed columns `measure_class` (monetary | fixed_unit | quantity_uom | dimensionless) and `context_concept_id` (FK, nullable) on concept_registry.business_concept_version; backfill wave over the 88 amount + 9 quantity BCs through the governed version-amendment path (which itself waits on the BCV-amendment recommendation surface, TSK-f4a163 coordination). Until the DBCP lands, the admission gate applies to NEW candidates via the panel rubric, and the backfill is tracked on TSK-8219f1.

Explicitly rejected: (a) ISO 4217 in the unit field — false vocabulary-level assertion of row-level fact; (b) leaving context declaration entirely to the CC layer — the CC can only bind what the vocabulary declares, and cross-source portability (same MC, second source) requires the dependency to be source-agnostic vocabulary, not per-contract convention; (c) converting amounts at admission/observation — reads/admission do not evaluate (boundary-independent rules); conversion is metric-evaluation work against the declared aggregation currency.
