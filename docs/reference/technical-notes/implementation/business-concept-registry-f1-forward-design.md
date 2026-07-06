---
uid: business-concept-registry-f1-forward-design
title: Business Concept Registry — F1 forward-design note
description: F1 forward-design note resolving the three items DEC-02f5a9 left open — composite-entity identity representation, the versioning unit, and the governed vocabulary content. The buildable-detail layer for Phase F items F2 (schema DBCP) and F3 (authoring service).
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: architecture
---

# Business Concept Registry — F1 forward-design note

> **What this is.** Phase F item **F1** of the BCF build plan. DEC-02f5a9
> (Business Concept Registry, D414) decided the conceptual model but explicitly
> left three items undecided — its Decision boundary, and
> `business-concept-registry.md` §13: composite-entity identity representation,
> the versioning unit, and the initial governed vocabulary content. This note
> resolves them at the buildable level. It is a **design note, not an ADR** — it
> elaborates DEC-02f5a9, it changes none of its architectural decisions. Locked
> 2026-05-21 with the operator's three amendments; `accepted` 2026-05-21 after
> review-back. Cited by Phase F items **F2** (schema DBCP) and
> **F3** (authoring service), which build against it.

## Scope

This note covers exactly the three F1 items. It does not author the schema DDL
(that is F2, a separate operator-approved DBCP) or the authoring service (F3).
It states the design those implement.

## 1. Composite-entity identity representation (F1.1)

**Identity is a named, derived set — never positional.**

- A composite entity's business identity is the set of its **identity-bearing
  properties**, each named by its property role (`order`, `product`,
  `line_number`). Position carries no meaning; a canonical serialization order
  exists for display and hashing, but identity is by the named set.
- The identity is **derived, not stored twice.** Every property already carries
  `identity_role ∈ {identity_bearing, descriptive}`. The entity's identity *is*
  the `identity_bearing` subset of its properties.

**`identity_bearing` means structural / grain identity — not "identifies a record."**

This is the load-bearing distinction. Two notions must not be confused:

| Notion | Carried by | Example |
|---|---|---|
| A property whose *value* identifies a record | representation term `identifier` | `Customer.customer_number` |
| A property that participates in the entity's *structural identity / grain* | `identity_role = identity_bearing` | `Order Line.order → Sales Order` |

`identity_role = identity_bearing` is the **second** notion only.
`Customer.customer_number` has representation term `identifier` but
`identity_role = descriptive` — it identifies Customer records, it does not make
`Customer` a composite entity.

Consequences:

- **Simple entity** = **zero** structural identity-bearing properties. Its
  identity is its surrogate `entity_id`; it may carry a descriptive natural-key
  identifier. `Customer`, `Product`, `Sales Order` are simple entities.
- **Composite / dependent entity** = **one or more** structural identity-bearing
  properties. It is grained on — exists only in the context of — other entities
  or value parts. `Order Line` (grain `Sales Order` × `Product` × `line_number`),
  `Inventory Position` (grain `Material` × `Warehouse` × `Batch`).

**The identity-reference graph is acyclic.** A composite entity's
identity-bearing *reference* properties point at other entities; that graph is a
DAG, enforced at write time. Circular structural identity is unresolvable.

**Surrogate vs business identity.** Every entity carries a surrogate `entity_id`
(DEC-02f5a9 §3) — the system reference key contracts and the chain resolve
against. The identity-bearing property set is the *business* identity (the
natural key / grain) and is what supersession watches (§2).

## 2. The versioning unit (F1.2)

**Two nested versioning units: the Entity (outer) and the Business Concept
(inner).** Each carries two identifiers:

| Construct | Stable semantic identity | Immutable version |
|---|---|---|
| Entity | `entity_id` | `entity_version_id` |
| Business Concept (`entity.property`) | `concept_id` | `concept_version_id` |

**Change taxonomy:**

- **Meaning-bearing change → new semantic identity.** A new `entity_id` or
  `concept_id`, linked to the prior by **supersession lineage**.
  - *Entity* meaning-bearing change = a change to its identity-bearing property
    set (its grain). New `entity_id`.
  - *Concept* meaning-bearing change = a change to a property's characteristic,
    representation term, type, unit, or semantic role. New `concept_id`.
- **Descriptive change → new version under the same identity.** A change to
  definition prose, examples, or provenance produces a new `entity_version_id` /
  `concept_version_id` under a **stable** `entity_id` / `concept_id`. References
  remain semantically valid — the meaning did not change.
- Every change produces a new immutable version (Invariant III — nothing is
  mutated in place). Meaning-bearing changes additionally mint a new semantic
  identity.

**Entity supersession carries its concepts.** A concept's identity is
`(entity_id, property_id)`; a new `entity_id` re-identifies the entity's concepts
under it, with supersession lineage. A concept cannot outlive its entity. This is
correct, not churn: when `Inventory Position` regrains from `(Material,
Warehouse)` to `(Material, Warehouse, Batch)`, `quantity_on_hand` genuinely means
something different — quantity-per-batch, not per-warehouse — so it is a
different concept.

**Cascade is a governance proposal, not an auto-activation.** Entity supersession
cascades *up* the identity DAG — if entity B is superseded and entity A's
identity references B, A must re-point, which is itself an A identity change. The
acyclic constraint guarantees the cascade terminates. But the cascade **creates
governance work / re-point proposals for operator confirmation** — it does not
silently auto-activate replacement entities.

**Audit pins versions; resolution resolves identity.** Contracts and runtime
evidence **pin the `*_version_id`** they evaluated against — immutable, for
non-replayable audit (Invariants V, VI). Authoring and the resolution layer work
with the `*_id` (semantic identity) and resolve to the currently-active version.
This is the dual-mode ID-only reference model F1 chooses under DEC-02f5a9 §4.

Entities and concepts both follow the Foundation five-state lifecycle and
Invariant III immutability.

## 3. Governed vocabulary content (F1.3)

Three governed vocabularies. This note locks each one's **shape** and
**governance rule**; the exact enumerations are data-seeding work downstream of
F1, except the closed representation-term list, proposed below.

| Vocabulary | Shape | Governance |
|---|---|---|
| Representation term | **Closed** | Additions require a governance act; a DB CHECK enforces the set |
| Property characteristic | **Governed-open** | Grows through the authoring panel — panel proposes, operator confirms; the synonym check tests new terms against the governed set |
| Entity | **Governed-open** | Entities registered through the authoring panel; seed catalogs (OAGIS nouns, etc.) are *candidate* source, never identity authority (DEC-02f5a9 §1) |

**The vocabularies are binding, not advisory.** Registry authoring is a
*selection* from them: a value concept references a `characteristic` and a
`representation_term` that already exist in the governed sets (FK-enforced),
and an identity-bearing term outside the governed vocabulary must be
governed-added before it can be used — identity is chosen from the governed
vocabulary, never free-typed. Definitions and citations are explanatory prose;
they never determine identity (§2).

**Representation-term v1 — proposed, reviewable.** Seeded from ISO 11179. The
following is the **proposed v1 set**; the exact list is **reviewable before F2
turns it into a DB CHECK constraint**:

`amount, code, count, date, date_time, duration, identifier, indicator, measure,
name, percentage, quantity, rate, ratio, text`

**Seed sources at greenfield.** The property-characteristic vocabulary is
seeded through curated review using direct standards and domain evidence — the
OAGIS catalog (`bc_seed.seed_oagis_components`) as primary citation evidence,
ISO 11179 and other compliance standards as supporting citations — with the
legacy Business Field / Canonical Field catalog used only as a coverage hint,
never as naming, definition, or identity authority. The entity vocabulary is
likewise authored through the panel from direct standards and domain evidence;
the legacy Business Object catalog and the seed catalogs are candidate /
coverage input only. [Sharpened 2026-05-21 by the F4 evidence-posture review —
see `business-concept-registry-f4-governed-vocabulary-seed-design.md` §4.]

**Aliases / synonyms are first-class governed metadata.** Each entity and each
property-characteristic carries a governed set of **aliases** — known alternate
names for the same concept. This is what bounds the AI panel's synonym work: the
panel tests a candidate term against the governed terms **and their governed
aliases** — a bounded lookup, not an unbounded similarity search. An alias is
added through the same governance act as the term it attaches to. This
operationalises the synonym guarantee of DEC-02f5a9 §3 and
`business-concept-registry.md` §6, and the bounded-panel intent of
`business-concept-registry.md` §10.

## 4. What F2 and F3 implement

**F2 — Registry schema DBCP** must provide:

- An `entity` representation: stable `entity_id`, immutable `entity_version_id`,
  five-state lifecycle, supersession lineage.
- A `property` representation belonging to exactly one entity: `kind`
  (value | reference); `identity_role` (identity_bearing | descriptive, in the
  structural-grain sense of §1); characteristic; representation term; and value
  metadata (type / unit / semantic) for value properties, or `(role,
  target_entity)` for reference properties.
- A `business_concept` semantic identity = `(entity_id, property_id)` with
  `UNIQUE(entity_id, property_id)` (DEC-02f5a9 §3); stable `concept_id`;
  immutable `concept_version_id`; lifecycle; supersession lineage.
- A `representation_term` closed-set CHECK (the §3 v1 list, F2-review-locked).
- An `alias` structure — first-class governed aliases for entity names and
  property-characteristic terms.
- The identity-reference-graph acyclicity constraint.

**F3 — Registry authoring service** must enforce:

- Structural identity at write time — synonyms blocked by
  `UNIQUE(entity_id, property_id)`; homonyms forced into distinct IDs and
  definitions (DEC-02f5a9 §3).
- The §2 change taxonomy — a meaning-bearing change mints a new semantic identity
  with lineage; a descriptive change mints a new version under the stable
  identity.
- The acyclic identity-DAG check.
- Entity-supersession cascade as operator-facing governance proposals, never
  auto-activation.
- Vocabulary governance — closed representation-term enforcement; governed-open
  characteristic and entity additions via panel proposal + operator confirm;
  alias governance.

## Status

`accepted` 2026-05-21 — operator review-back complete; two citation fixes
applied (the alias paragraph and the dual-mode-reference wording). The three F1
locks change no DEC-02f5a9 decision — they fill its explicit "does not decide"
gaps. F2 is authored next as a DBCP packet for operator approval before any DDL.
