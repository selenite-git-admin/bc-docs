---
id: business-vocabulary
order: 8.5
title: "Business Vocabulary"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, sources-and-the-catalog, business-concept-registry]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The BareCount Business Concept Registry (the model)
governing_adrs:
  - DEC-02f5a9 (Business Concept Registry — supersedes BO/BF/CF and Canonical Mapping identity; D414)
  - DEC-61850f (Business Concept Registry adoption)
superseded_adrs:
  - DEC-aa6251 (D255 BO and BF as Contract Primitives)
  - DEC-616e02 (D103 Business Object Model)
  - DEC-d72560 (D301 Canonical Field as 3rd Contract Primitive)
  - DEC-f66378 (D292 BO-Scoped BF Composition)
  - DEC-683cf3 (BO tiers basic vs derived)
  - DEC-9a5dc0 (CF Boundary)
errata_referenced: []
v2_sources: []
word_target: 2200
---

# Business Vocabulary

> **This chapter teaches the current model.** The platform's business vocabulary is the **Business
> Concept Registry** (Entity / Property / Business Concept), adopted by DEC-02f5a9 and DEC-61850f. The
> earlier three-primitive model — Business Field, Business Object, Canonical Field, joined by a Canonical
> Mapping — is **superseded**. The deep model lives in *The BareCount Business Concept Registry*
> (`implementation/business-concept-registry.md`); this chapter is the operating-model view of it. Where a
> BF/BO/CF **table** is still named in an onboarding procedure, it is a **binding mechanism** at the chain
> boundary, not a vocabulary identity — see *What Survives* below.

## Scope

This chapter defines the platform's internal business vocabulary — what a business concept *is*, how it is
identified, and the discipline that admits one. It states the model an author works with (Entity, Property,
Business Concept), the single identity rule, the two failure modes the registry makes structurally
impossible, how the retired primitives map onto the registry, the BCF/MCF boundary, the role of standards,
and the certification substrate that admits a concept.

This chapter does not redefine the registry's deep model (*The Business Concept Registry* owns that), the
contract grammar that references concepts (*The Contract Grammar*), the Source Catalog observed fields come
from (*Sources and the Catalog*), or canonical evaluation runtime behavior (*Canonical Evaluation*).

**Governing source.** Foundation; The Business Concept Registry; The Contract Grammar.

## The Model

The vocabulary is one governed registry. Three constructs:

| Construct | What it is |
|---|---|
| **Entity** | A globally governed, **role-bearing** business concept — `Customer`, `Supplier`, `Invoice`, `Inventory Position`. Simple, or composite (identity = an ordered/named set of identity-bearing properties). Not a physical thing: `Customer` and `Supplier` are distinct entities even when one real party plays both roles. |
| **Property** | Belongs to exactly one entity. `kind = value` (a scalar — `credit_limit`, `balance`) or `reference` (points to another entity, carries a role — `invoice.bill_to → Customer`). `identity_role = identity_bearing | descriptive`. |
| **Business Concept** | The addressable, observable unit of vocabulary. **Identity = `entity.property`.** This is the unit the contract chain references. |

The entity graph *is* nothing more than the set of reference-properties. A property term decomposes into a
**characteristic** (`credit limit`, `balance`, `status`) and a **representation term** (`amount`, `date`,
`code`, `quantity`, `count`, `indicator`, `identifier`, `text`) — the representation set is a small closed
list, seeded from ISO 11179 then owned.

## Identity

A concept's identity is exactly **`entity.property`** — two levels, nothing else.

- **Entities are globally unique by ID** (a surrogate). Entity *names* need not be globally unique, but a
  canonical name must be **self-disambiguating in its own wording** (`Employment Position` vs
  `Market Position`) — never disambiguated by a namespace prefix.
- **Family / owner-domain / tags are classification, not identity.** An entity is the same concept
  regardless of how it is filed.

## The Two Failure Modes the Registry Governs

The registry exists to make two Invariant-I violations **structurally impossible**, not merely detected:

- **Synonyms** (many names, one meaning — `credit_limit` / `credit_cap` / `credit_ceiling`). Guarantee:
  identity is `(entity, property)`, unique by construction (`UNIQUE(entity_id, property_id)`) — a second
  concept for the same identity cannot be created.
- **Homonyms / false unifiers** (one name, many meanings — `Invoice` = AR + AP; `Account` = customer vs GL;
  `Position` = employment vs market). Guarantee: globally unique entity IDs with **forced-distinct
  definitions** — a coarse name cannot silently merge two concepts.

The mechanism is **structure**, not after-the-fact detection. A duplicate that reached `active` would be
irreversible historical damage (Invariant III), so detection would be too late.

## How the Retired Primitives Map

The prior model is superseded, not merely renamed. The mapping, for readers coming from older procedures:

| Retired primitive | Registry equivalent |
|---|---|
| **Business Object** | ≈ **Entity** (a role-bearing concept; the old free-text `object_class` becomes the Entity — a governed reference, not a string) |
| **Business Field** | ≈ **Business Concept** (`entity.property`, value or reference) |
| **Canonical Field** | ≈ **Business Concept** — there is no separate canonical-side identity; one concept serves both sides |
| **Canonical Mapping (as identity binding BF↔CF)** | **Eliminated** — with one concept there is no BF↔CF identity to bind. Canonical Mapping as *transformation* content (unit/type/reduction) survives in the chain / MCF. |
| **`basic` vs `derived` BO tiers** | Not an identity axis; a value that arrives stored is a BCF property, a value the platform computes is an MCF metric (see below) |

## The BCF / MCF Boundary

**BCF governs observable concepts; MCF governs computed metrics.** The line is *who computes it*:

- A value that arrives **stored** — even if the source system derived it internally — is a **BCF property**
  (`invoice.net_amount`).
- A value the **platform** computes over grain, time, filters, and formula is an **MCF metric**
  (`days_sales_outstanding`, `gross_margin_rate`).

**Grain is structural.** A metric's grain *is* the composite entity it measures over. In MCF, grain is a
**typed reference to a registry entity**, not a free-text parameter — so an incoherent grain cannot be
declared. (This replaces the old "five shared-dimension Business Fields" device: cross-concept grain keys
such as legal entity or currency are entities/properties referenced through the registry and reconciled at
the binding layer, not special shared fields.)

## The Role of Standards

Standards (OAGIS, ISO 20022, US-GAAP / XBRL, IFRS, …) play exactly two roles plus one bounded content
contribution — and are **never identity authority**:

- **Provenance evidence** — "this concept traces to standard X" satisfies the no-fabrication rule.
- **Candidate source / recognition** — a seed catalog to *suggest* vocabulary and *recognize* a tenant's
  source fields at onboarding.
- **One bounded content contribution** — the closed representation-term set, seeded from ISO 11179 then
  owned.

"Standards-compliant" is a claim about traceability, not correctness; the correctness property is the
registry's internal one-meaning-per-concept. You cannot be governed by mutually-contradictory standards —
that impossibility is the proof standards are not the authority.

## The Role of the AI Panel

With identity made structural, the authoring panel is **not a duplicate checker** — it is a
**concept-placement assistant**: given a candidate, is this an existing entity or a new one? an existing
property or a new one? is a proposed term a synonym of a governed term? is the definition disciplined? is
the standard/source reference evidence (not authority)? — admit, reject, or route to operator review. The
irreversible-uniqueness guarantee comes from the registry's **structure**, not from the panel. The panel
assists framing within a governed surface; **it does not own identity.** (Since D483 the panel runs
in-process in bc-core; see AI Gates.)

## Certification Lifecycle

A concept passes the Foundation five-state lifecycle before it is admissible to contract authoring, and
`active` concepts are immutable (Invariant III):

| State | Meaning | Next |
|---|---|---|
| `proposed` | Registered with provenance, not yet reviewed | `reviewing`, `withdrawn` |
| `reviewing` | Under review against the certification gate set | `certified`, `proposed`, `withdrawn` |
| `certified` | Admissible to contract authoring | `superseded` |
| `superseded` | A newer concept replaces it for new authoring; historical references stay addressable | terminal |
| `withdrawn` | Rejected before certification | terminal |

**Supersession rule.** Changing an entity's **identity-bearing** property set is supersession — a new
entity. Adding a **descriptive** property is additive — non-superseding. Supersession never retroactively
invalidates a contract version that already references the prior concept.

The governed certification substrate — the panel-output record, certification record, framework policy,
calibration and phase state, and the intake / rejection-log services — is unchanged by the model switch: it
governs *whatever* the vocabulary is, and it stands.

## What Survives (and why onboarding procedures still name BF/BO/CF tables)

The model switch does **not** invalidate, and explicitly preserves:

- the four **evaluation boundaries** (admission, canonical, metric, action);
- the **active contract families** — Source, Admission, Observation, Canonical, Intervention — other than
  the vocabulary primitives;
- the five-state **lifecycle, versioning, and immutability**;
- **source-field binding at the chain boundary** — the admission / observation boundary binds a tenant's
  source fields to concepts. A source field is *not* vocabulary. The legacy
  `contract.business_field` / `contract.business_object` / canonical-field tables **persist physically**
  until the greenfield cutover (DEC-02f5a9 §6) and still carry OC/CC `field_selection` binding. So where an
  onboarding chapter says "select the Business Field" or "the Business Object code," the **mechanics remain
  valid for binding** — but the *semantic identity* of what is being bound is the registry concept, not the
  legacy row.
- **transformation logic** — unit conversion, type coercion, reduction over grain, temporal interpretation
  — wherever grain / unit / reduction are genuinely real. It remains authored content, in the chain or MCF.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-02f5a9 | Adopts the Business Concept Registry; supersedes the BO/BF/CF three-primitive model and Canonical Mapping identity |
| DEC-61850f | Business Concept Registry adoption |

The superseded decisions (DEC-aa6251, DEC-616e02, DEC-d72560, DEC-f66378, DEC-683cf3, DEC-9a5dc0) are
retained in the ADR registry for historical continuity; contract versions authored under them stay
addressable.

**Governing source.** Decisions: ADR Registry.

## References

- The BareCount Business Concept Registry (`implementation/business-concept-registry.md`) — the deep model
- Foundation: Scope and Non-Negotiability
- The Object Model
- The Contract Grammar
- The Evaluation Boundaries
- Sources and the Catalog
- Canonical Evaluation
- AI Gates
- DEC-02f5a9: Business Concept Registry
- DEC-61850f: Business Concept Registry adoption
