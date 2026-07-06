---
uid: DEC-7f2e73
title: "MCF Reference-Stamping — edge-resolved reference attributes on the Canonical Object (customer-axis Component A)"
description: "A reference property (e.g. Customer Invoice → Customer) is resolved and stamped on the Canonical Object at the canonical evaluation boundary — mirroring the D365 fiscal_period stamp — giving metrics a typed, stamped reference to read. The legal predicate for reference-dimension grouping (CB-008 Component B) and cross-entity binding (Component C)."
status: decided
date: 2026-06-30T07:14:01.805Z
project: bc-core
domain: contracts
subdomain: contracts/canonical
focus: reference-stamping
---

# MCF Reference-Stamping — edge-resolved reference attributes on the Canonical Object (customer-axis Component A)

## Context

See decision text below.

## Context

The customer-axis metric family (CB-008: top-N concentration, per-customer aging, credit-limit utilization) is blocked because MCF has no reference-dimension or cross-entity capability. The scope doc (docs/implementation/metric-context-framework-reference-dimension-cross-entity-scope-2026-06-30.md) decomposed it into Components A–D; D (secondary-metric DAG) shipped (DEC-0f3e57/D467). This ADR is **Component A**: the canonical prerequisite that makes B and C legal.

Verified live (SES-b64bfa): the canonical resolver (`src/boundary/canonical-resolution.service.ts` → `resolveGroup` → `mergePayloads`) performs dumb `source_field → canonical_field` extraction with ZERO reference awareness. A `reference`-kind Business Concept's value is stamped as a raw key, not a typed reference. `KUNNR` (the SAP customer key) is not even observed in the Customer Invoice OC, and `cc__customer_invoice_arpi_slice` has no customer field. The Business Concept Registry supports `kind='reference'` (with `referenceRole` + `targetEntityId`), and the canonical-v2 schema permits a reference-kind BC in `field_selection` (it only forbids `canonical_value_set` on it) — but nothing consumes the reference semantics during resolution. The reference→OC→CC→CO stamping path is unbuilt platform-wide.

## Decision (edge-resolved, mirroring D365 fiscal_period stamping)

A reference becomes a stamped Canonical Object attribute exactly the way `fiscal_period` does (D365: posting_date resolved via the tenant calendar, then stamped on the CO by an enrich step before evaluation). Three pieces:

1. **OC widening (repair A).** Observe the source customer key as a `field_mappings` entry binding `KUNNR → invoice→customer reference BC`.
2. **CC field_selection (repair B).** Select that reference BC as a canonical field (e.g. `bill_to_customer`). No CC-body schema change — the reference target lives on the BC (`targetEntityId`), and the canonical-v2 schema already permits the entry.
3. **Resolver enrich (repair D).** A new `enrichReferences()` step in `resolveGroup` (mirroring the D365 fiscal enrich, ~lines 1078–1114), run after `mergePayloads` and before evaluation: for each `field_selection` entry whose BC `kind='reference'`, stamp the resolved **target-entity identity** onto the merged payload **with reference semantics** — a structured attribute `{ canonical_field, target_entity_id, identity_value }`, not a bare key. The CO payload (`canonicalPayloadJson`, flat JSON) holds it; no DB schema change.

## Amendment (SES-b64bfa, 2026-06-30) — Component-A resolver enrich is NOT required (grounded in the actual Foundation text)

Re-grounding §3 against `docs/foundation/the-invariants.md` Invariant IV (lines 105–116, read directly) corrects the mechanism: **piece 3 (the resolver `enrichReferences()` step) is unnecessary for the customer-axis case; a resolver change is deferred.**

- **Invariant IV governs references to AUTHORITATIVE OBJECTS** (SO / CO / Metric Snapshot / AO): "Every reference to an authoritative object identifies its type, its identity, and its version." **Customer is an Entity, not an authoritative object** — so the invoice→customer *entity* edge is not itself the Invariant-IV reference.
- The Invariant-IV reference is **invoice CO → customer CO** (both authoritative objects). Per the text, such a reference is resolved by a **Governed Selection** — "a declared, versioned rule that resolves the object versions a reference names, **recording the resolved set in Lineage**" (Invariant IV, reference-mode table, row 2). That happens **at the metric boundary (Component C)**, not at canonical resolution.
- Therefore Component A only needs the invoice CO to carry the **customer identity value** as a stamped immutable attribute. `KUNNR` *is* that identity value, so binding a **reference-kind BC** (kind=reference, target=Customer) in the OC field_mapping + CC field_selection is sufficient: `mergePayloads` already stamps the value, and the reference semantics live on the BC (consumed by Component C's governed selection). **No `enrichReferences()` resolver step.**
- The original §3 enrich (a structured `{target_entity_id, identity_value}` stamp) is only warranted in the **translation case** where the source key ≠ the target identity (an external lookup is needed). Deferred until such a case exists.

**Revised Component-A mechanism:** (1) reference-correction surface → `56a5f975` becomes descriptive/bill_to; (2) OC observes `KUNNR → reference BC`; (3) CC selects it as `bill_to_customer`; (4) mapping binding maps `KUNNR → bill_to_customer`. The real capability work is making the contract-chain gates (D430/D431 identity gates) accept a reference-kind BC end-to-end — **not** a resolver build. Invariant I (canonical meaning once) is satisfied by stamping the identity at the canonical boundary; Invariant IV (the explicit CO→CO reference) is satisfied at the metric boundary by Component C's governed selection recording the resolved customer CO version in Lineage.

## Why edge-resolved (not value-key) — Foundation grounding

- **Invariant I (meaning evaluated once, at the canonical boundary).** "This invoice belongs to customer X" is canonical meaning. The value-key shortcut (observe `KUNNR` as a plain value) stamps a raw key with no semantics, forcing every metric to interpret it at read time (Invariant I violation) and duplicating the Customer-entity identity model. Edge-resolved stamps a typed reference the Governed Selection reads directly (Component B group-by) and Component C joins to the Customer CO on. (`KUNNR` *is* the customer's identity value, so the resolution is trivial — the weight is stamping it AS a reference.)
- **The Object Model §Canonical Object:** a CO is produced at the canonical boundary by applying one CC, stamping the resolved values of the BCs it binds. A reference BC is just another bound BC; the resolver must learn to stamp its resolved target identity.
- **The Governed Selection:** a grouping/join key is admissible iff it is a stamped immutable attribute on the CO — which this produces.

## Reference-correction prerequisite

The invoice→customer reference `56a5f975` was authored `identity_bearing/role=customer`, but the Business Concept Registry doc models `invoice.customer` as **descriptive/role=bill_to** (TSK-3790bb). The correct edge must be wired into the contracts. The two cert-minting correction surfaces are value-concept only — there is no reference-correction surface (the mechanism gap). This ADR's first implementation step is therefore to add a reference-correction recommendation surface (operator-direct, mints the registry_supersede cert for a reference successor, parallel to the value shape-correction), then supersede `56a5f975 → descriptive/bill_to`.

## Scope boundaries

IN: the reference-stamping mechanism (OC observe → CC select → resolver enrich → stamped reference attribute) + the reference-correction surface. The stamped reference is a same-entity attribute on the invoice CO carrying the target customer identity.
OUT (separate ADRs): Component B (reference-dimension grouping — group-by/top-N over the stamped reference) and Component C (cross-entity binding — read the Customer CO joined by the stamped reference). The RUNTIME cross-entity read of the Customer CO is Component C. CB-009 (source-not-observed) is unrelated.

## Foundation gate

Repair location A (OC observation of KUNNR) + B (the CC declares a reference field) + D (the resolver stamps it). Invariant I is the binding constraint — the reference is canonical meaning, produced once at the canonical boundary, never resolved at the metric boundary. Invariant IV/VI: the stamped reference is explicit and recorded; the metric reads it, never the join. No lower-layer (E/F) compensation. Mirrors the existing, Foundation-clean D365 fiscal_period stamp.
