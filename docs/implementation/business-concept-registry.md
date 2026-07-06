---
uid: business-concept-registry
title: The BareCount Business Concept Registry
description: The BareCount business-vocabulary identity model — one governed registry of (entity, property) Business Concepts. Adopted by DEC-02f5a9 (Business Concept Registry).
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: architecture
---

# The BareCount Business Concept Registry

> **Adoption status — adopted by DEC-02f5a9.**
> This model is **adopted** as the platform's vocabulary identity model by
> DEC-02f5a9 (Business Concept Registry; D414), which
> supersedes DEC-a17d0f and the Business Object / Business Field / Canonical
> Field vocabulary model. Sections 1–10 below are the adopted model. The
> Foundation Contract Grammar, Object Model, and Evaluation Boundaries chapters
> are amended to reflect it; the BF/BO/CF primitives persist physically until
> the greenfield cutover DEC-02f5a9 §6 decides. Schema, the versioning unit,
> and the governed vocabulary content remain forward-design items (§13).

## What this is

A consolidation of an architecture design dialogue into one
coherent model — **adopted by DEC-02f5a9** (Business Concept Registry). It
defines a single governed structure for the platform's business vocabulary —
the **Business Concept Registry** — that replaces the three-primitive split
(Business Object / Business Field / Canonical Field) plus the Canonical Mapping
that binds them. The split persists physically until the greenfield cutover
(DEC-02f5a9 §6).

It is a **conceptual** design: model and reasoning only. Schema and migration
specifics are decided by DEC-02f5a9 and its follow-on DBCPs, not here.

---

## 1. Purpose

BCF is the governance discipline for the platform's business vocabulary. The
vocabulary itself — the *thing* BCF governs — had been modeled as
three primitive identities (Business Object, Business Field, Canonical Field)
joined by a Canonical Mapping. That split, together with free-text
`object_class` on Business Field and standards used as the structural
authority, produced an identity model in which two failures are *possible*:

- **duplicate concepts** — two vocabulary identities for one meaning;
- **merged concepts** — one identity silently spanning two meanings.

Both are violations of Foundation **Invariant I — meaning is evaluated once**.
For a platform whose trust promise is *one canonical meaning per business
concept*, a vocabulary model that merely *detects* these after the fact is
insufficient: a duplicate that reaches `active` produces irreversible
historical damage.

This proposal replaces the split with **one registry**. Every entry is a
business concept identified as `entity.property`. Duplication and merging
become **structurally impossible**, not detected. The trust promise becomes a
property of the registry's structure — not of standards-conformance.

## 2. The core model

Three constructs:

```
Entity
  - a globally governed, role-bearing business concept
  - simple, or composite / dependent
  - may carry identity-bearing properties (composite entities)

Property
  - belongs to exactly one entity
  - kind: value | reference
      reference → points to another entity; carries a role: (role, target-entity)
      value     → carries representation / type / unit / semantic metadata
  - identity_role: identity_bearing | descriptive

Business Concept
  - the addressable, observable unit of vocabulary
  - identity = entity.property
  - the unit the contracts chain references
```

Illustrative concepts:

```
customer.credit_limit               — value property
invoice.customer                    — reference property (role: bill-to), descriptive
order_line.product                  — reference property, identity-bearing
inventory_position.quantity_on_hand — value property of a composite entity
employee.department                 — reference property → Department
```

## 3. Identity

A concept's identity is exactly **`entity.property`** — two levels. Nothing
else disambiguates a concept.

- **Entities are globally unique by ID** — a surrogate identifier. Entity
  *names* need not be globally unique; the **canonical name must be
  self-disambiguating in its own wording** (`Employment Position` vs
  `Market Position`), never disambiguated by a namespace prefix. The registry
  forces a genuine concept distinction to be *named* at definition time.
- **Family is classification, not identity.** A family / owner-domain / tags
  layer (`entity.family`, `entity.owner_domain`, `entity.tags`) exists for
  navigation and stewardship. It does **not** participate in concept identity.
  An entity is the same concept regardless of how it is filed.

## 4. Entities

**An entity is a role-bearing business concept — not a physical thing.**
`Customer`, `Supplier`, `Vendor`, `Payer`, `ShipToParty` are distinct entities
even when one real-world organization or person appears under several roles.
Their properties, constraints, lifecycle, and business meaning differ.
Reconciling that the same legal party is both a customer and a supplier is
**tenant data**, handled at the binding layer — never collapsed in the
vocabulary. This prevents over-normalizing vocabulary around physical-world
identity instead of business role.

Entities are **simple** or **composite / dependent**. A composite entity's
identity is an **ordered or named set of identity-bearing properties**:

```
Order Line          identity = { order → Sales Order, product → Product, line_number (value) }
Inventory Position  identity = { material → Material, warehouse → Warehouse, batch → Batch }
```

The identity-reference graph must be **acyclic** — a composite entity's
identity-bearing references form a DAG; circular identity is unresolvable.

## 5. Properties

A property **belongs to exactly one entity**. An entity may collect properties
contributed by many business functions — `Customer` carries finance,
sales, and service properties alike; entities are not function-owned.

- **kind = value | reference.** A *value* property is a scalar (`base_salary`).
  A *reference* property points to another entity and carries a **role**:
  a reference-property is `(role, target-entity)`. **The entity graph is
  nothing more than the set of reference-properties.** A single entity may
  hold several reference-properties to the same target in different roles
  (`invoice.bill_to → Customer`, `invoice.ship_to → Customer`).
- **identity_role = identity_bearing | descriptive.** Not every reference is
  identity-bearing: `order_line.order` is identity-bearing; `invoice.customer`
  is descriptive. Identity-bearing properties (value or reference) define a
  composite entity's identity (§4).
- **Property terms are governed vocabulary.** A property decomposes into a
  *characteristic* (`credit limit`, `balance`, `status`) and a *representation
  term* (`amount`, `date`, `code`, `quantity`, `count`, `indicator`,
  `identifier`, `text`). Representation terms are a **small closed set** — the
  one place a standard contributes genuine *content*: the set is seeded from
  ISO 11179's, then owned. Governing the property-term vocabularies is what
  keeps the AI's synonym check **bounded** — it tests a proposed term against a
  few hundred governed words, never against the full concept space.

## 6. The two failure modes the registry governs

The registry exists to make two distinct failures **structurally impossible**:

- **Synonyms** — many names, one meaning (`credit_limit` / `credit_cap` /
  `credit_ceiling`). Guarantee: identity is `(entity, property)` and unique by
  construction — `UNIQUE(entity_id, property_id)` — a second concept for the
  same identity cannot be created.
- **Homonyms / false unifiers** — one name, many meanings (`Invoice` = AR + AP;
  `Account` = customer account + GL account; `Position` = employment + market).
  Guarantee: globally unique entity *IDs* with **forced-distinct definitions** —
  a coarse name cannot silently merge two concepts; the registry compels the
  operator to define them apart.

Both are Invariant I violations. The mechanism is **structure**, not
detection. The AI does not carry these guarantees (§10).

## 7. Lifecycle and versioning

Entities and concepts follow the Foundation five-state lifecycle; `active`
artifacts are immutable (Foundation Invariant III).

**Supersession rule.** Changing an entity's **identity-bearing** property set
is **supersession** — a new entity. Adding a **descriptive** property to any
entity is **additive** — non-superseding. (Changing `Inventory Position`'s
identity from `(Material, Warehouse)` to `(Material, Warehouse, Batch)` changes
its grain — a different entity. Adding `Customer.loyalty_tier` leaves
`Customer` untouched.)

**Open forward-design item.** The precise *unit* of versioning —
entity-level vs concept-level lifecycle and their interaction — is not settled
here. The supersession rule above is its spine; forward-design must state it
outright.

## 8. The BCF / MCF boundary

**BCF governs observable concepts; MCF governs computed metrics.** The line is
**who computes it**:

- A value that arrives **stored** — even if the source system derived it
  internally — is a **BCF property** (`invoice.net_amount`).
- A value the **platform** computes over grain, time, filters, and formula is
  an **MCF metric** (`days_sales_outstanding`, `gross_margin_rate`).

**Grain is structural.** A metric's grain *is* the (composite) entity it
measures over — `quantity_on_hand` is grained at `Inventory Position`, not
vaguely at `Material`. In MCF, grain therefore becomes a **typed reference to a
registry entity**, not a free-text parameter — MCF cannot declare an
incoherent grain.

## 9. The role of standards

Standards (OAGIS, ISO 20022, US-GAAP / XBRL, IFRS, …) play exactly two roles,
plus one bounded content contribution:

- **Provenance evidence** — "this concept traces to standard X" satisfies the
  no-fabrication rule.
- **Candidate source / recognition** — a seed catalog the framework draws on to
  *suggest* vocabulary and to *recognize* a tenant's source fields at
  onboarding.
- **One bounded content contribution** — the closed representation-term set
  (§5) is seeded from ISO 11179's, then owned.

Standards are **never identity authority.** You cannot be structurally
governed by mutually-contradictory standards — that impossibility is the proof.
The registry *references* standards; it is not *defined* by them.
"Standards-compliant" is a claim about traceability, not about correctness; the
correctness property is the registry's internal one-meaning-per-concept.

## 10. The role of the AI panel

With identity made structural, the Context Authoring Panel is **not a duplicate
checker.** It is a **concept-placement assistant.** Given a candidate it
proposes: is this an existing entity or a new one? an existing property of that
entity or a new one? is a proposed new term a synonym of a governed term? is
the definition disciplined? is the standard/source reference evidence (not
authority)? — admit, reject, or route to operator review.

The irreversible-uniqueness guarantee comes from the **registry's structure**
(§6) — not from embeddings, not from name matching, not from a standard. The
AI assists framing within a governed surface; **it does not own identity.**

## 11. Conflict with current Foundation

This model **conflicted with the pre-DEC-02f5a9 Foundation Contract Grammar and
BCF Requirements.** DEC-02f5a9 adopted it; it replaces:

- **BO / BF / CF as three separate primitive identities** → one
  Entity / Property / Business Concept model. ("Business Object" ≈ Entity;
  "Business Field" and "Canonical Field" ≈ Business Concept.)
- **Canonical Mapping as an *identity* mapping between BF and CF** → eliminated.
  With one concept there is no BF↔CF identity to bind. Canonical Mapping as
  *transformation* content survives (§12).
- **Business Field `object_class` as free text** → the Entity. The object class
  *is* the entity — a governed reference, not a string.
- **Standards as identity authority** → standards demoted to evidence and
  candidate source (§9).
- **Parts of the BCF Requirements** — Chapter 2 (three scopes), Chapters 12–15
  (per-scope BF / BO / CF / mapping / coherence), and Chapter 16 Deferral D2:
  "BF/CF collapse" and "BO necessity" cease to be open questions —
  DEC-02f5a9 resolves them.

This is the explicit conflict surface. **DEC-02f5a9 is the decision that
accepted this model; the Foundation Contract Grammar, Object Model, and
Evaluation Boundaries chapters are amended to reflect it.**

## 12. What survives

This model does **not** invalidate, and explicitly preserves:

- the four **evaluation boundaries** (admission, canonical, metric, action);
- the **active contract families** — Source, Admission, Observation, Canonical,
  and Intervention Contracts — other than the vocabulary primitives;
- the Foundation **five-state lifecycle, versioning, and immutability**
  (Invariant III);
- **authoring records** and the audit trail;
- the **BCF panel / calibration / governance substrate** — `panel_output_record`,
  `certification_record`, `framework_policy`, `calibration_event`,
  `phase_state`, and the Framework-Approval / intake / rejection-log / N30
  services. That machinery governs *whatever* the vocabulary is; it stands.
- **source-field binding at the chain boundary** — the admission / observation
  boundary binds a tenant's source fields to concepts; that is the chain's job
  and is unchanged. A source field is not vocabulary.
- **transformation logic** — unit conversion, type coercion, reduction over
  grain, temporal interpretation — wherever grain / unit / reduction are
  genuinely real. It remains authored content, in the chain or in MCF.

## 13. Forward

**Forward-design items — resolved.** The representation of composite-entity
identity, the precise versioning unit (§7), and the initial governed content of
the entity / property-characteristic / representation-term vocabularies are
resolved in the F1 forward-design note
(`business-concept-registry-f1-forward-design.md`).

**The three-layer platform-alignment survey (completed).** It measured the
distance from the platform to this model, across:

1. the **Foundation Contract Grammar** — whether it defined entity / property /
   concept, or only BO / BF / CF; the genuine delta vs the isomorphic parts;
2. **bc-core** — the `business_field` / `business_object` / `canonical_field`
   schema and services;
3. **every chain reference to BF / BO / CF** — OC and CC field selections,
   Canonical Mapping, MC variable bindings — the migration's true blast radius.

The survey measured distance to this model; it did not renegotiate it. Its
output, with this document, fed **DEC-02f5a9**.

DEC-02f5a9 accepted this model. It is the adopted
vocabulary identity model — see the Adoption status callout above — and the
Foundation chapters are being amended to reflect it.
