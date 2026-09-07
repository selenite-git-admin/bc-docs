---
id: business-field-and-business-object-onboarding
order: 53
title: "Business Concept Authoring (BCF)"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, business-vocabulary, business-concept-registry, ai-gates, ai-trust-and-verification, data-model-and-schema]
governing_sources:
  - The BareCount Business Concept Registry (the model)
  - Business Vocabulary
  - AI Gates
governing_adrs:
  - DEC-02f5a9 (Business Concept Registry — supersedes BO/BF/CF vocabulary; D414)
  - DEC-61850f (Business Concept Registry adoption)
  - DEC-ffee4e (D483 — BCF panels run in-process in bc-core; calibration-locked roster)
superseded_adrs:
  - DEC-f66378 (D292 BO-scoped BF naming; five shared dimensions)
errata_referenced: []
v2_sources: []
word_target: 2200
---

# Business Concept Authoring (BCF)

> **This chapter replaces "Business Field and Business Object Onboarding."** The BF/BO/CF vocabulary and
> its standards-derivation / BO-scoped-naming ceremony are **superseded** by the Business Concept Registry
> (DEC-02f5a9, DEC-61850f). This chapter is the governed procedure for authoring **business concepts** —
> Entities, Business Concepts (`entity.property`), and their Characteristics — into the `concept_registry`.
> The file id is retained for link stability. The **model** (what a concept *is*) lives in
> *The BareCount Business Concept Registry*; this chapter is the **procedure** for admitting one.

## Scope

This chapter records the governed sequence by which a business concept is authored into the registry: the
two maker routes (the in-process AI panel and the operator-direct surface), the recommendation artifact each
produces, the operator-confirm gate for high-consequence acts, and the certification-and-write chain that
makes a concept `active`. It names the authoring actions the registry supports (concept authoring,
characteristic admission, entity- and concept-version amendment, correction, orphan repair) and the
supersession rule that distinguishes an amendment from a new entity.

This chapter does not redefine the registry model (*The Business Concept Registry* — Entity / Property /
Business Concept, identity `entity.property`, the two structurally-impossible failure modes), the AI
maker-checker-moderator envelope (*AI Gates*), or **source-field binding** — binding a tenant's source
fields to concepts happens at the admission/observation boundary and is authored in *Observation Contract
Creation* and *Canonical Contract Creation*, not here. A source field is not vocabulary.

**Governing source.** The Business Concept Registry; Business Vocabulary; AI Gates.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Recommendation artifact (the shaped candidate + evidence) | `bcf.panel_output_record` | The maker route (panel or operator-direct) |
| Registry-shape certification (C5) | `bcf.certification_record` | The confirm act |
| Active Entity / Business Concept / Characteristic (F3 write) | `concept_registry.*` | The post-confirm executor |

A business concept's identity is `entity.property`; concepts are `value` or `reference` kind, and
`identity_bearing` or `descriptive`. `active` concepts are immutable (Invariant III).

**Governing source.** The Business Concept Registry.

## Prerequisites

| Precondition | Why |
|---|---|
| Cognito-authenticated platform actor | Registry mutations are `@PlatformOnly()` JWT-guarded |
| The target Entity exists (or is being authored in the same act) | A Business Concept is `entity.property`; the property attaches to a governed Entity |
| Source citation(s) for the concept | Standards/source are **evidence** (no-fabrication rule), never identity authority — a concept carries structured citations |
| bc-core BCF surface reachable | The panel run and confirm endpoints are in-process in bc-core (DEC-ffee4e); no external bc-ai service |

**Governing source.** The Business Concept Registry §9; AI Gates.

## The Two Maker Routes

A concept candidate is shaped by exactly one of two makers; both produce a recommendation artifact in
`bcf.panel_output_record` that the **same** confirm chain consumes.

| Route | When | What runs |
|---|---|---|
| **AI panel (B6)** | Default suggestion / placement assistance | `POST /api/bcf/registry-authoring-runs` — the in-process Maker / Checker / Moderator panel (roster calibration-locked by DEC-ffee4e). Produces an AI-consensus recommendation. Historically the panel path locks a new concept to `kind=value` + `descriptive`. |
| **Operator-direct** | Authoring **identity-bearing** value concepts or **reference** concepts (which the panel path does not mint) | No LLM runs — the **operator is the maker**. The artifact carries `provenanceKind: 'operator-direct'`. It lives in the same `panel_output_record` table but must not be read as a panel run. |

The panel is a **concept-placement assistant, not a duplicate checker** — identity uniqueness is guaranteed
by the registry's *structure* (`UNIQUE(entity_id, property_id)` + forced-distinct entity definitions), not
by the panel. The panel assists framing within a governed surface; it does not own identity.

**Governing source.** The Business Concept Registry §10; AI Gates; DEC-ffee4e.

## The Confirm-and-Write Gate

A recommendation does not write to the registry by itself. High-consequence acts (e.g. `createCharacteristic`)
park as `awaiting_operator_confirm`. The operator completes the act:

```
POST /api/bcf/registry-shape-certifications/confirm
{ panelRunUid, subjectKind, actionCode, rationale }   // rationale ≥ 40 chars
```

This runs `FrameworkApprovalService.confirmRegistryShapeCertification` → the registry-authoring
post-confirm executor → the F3 writer (`RegistryAuthoringService`), which performs the actual
`concept_registry` write. So the chain is: **recommendation → C5 certification → F3 write.** No write occurs
without the confirm; the confirm records who authorized it and why (the ≥40-char rationale is the governed
justification).

**Governing source.** AI Gates; The Authority Model.

## The Authoring Actions

The registry-authoring surface supports a fixed set of actions, each a recommendation family that resolves
through the same confirm-and-write gate:

| Action | What it authors / changes |
|---|---|
| **Concept authoring** | A new Business Concept (`entity.property`), value or reference, identity-bearing or descriptive |
| **Characteristic admission** | A new governed characteristic term (the property's characteristic half; representation terms are a closed set) — high-consequence, parks for operator confirm |
| **Entity-version amendment** | A change to an entity that is a **supersession** (see below) |
| **Concept-version amendment** | A governed change to a concept version |
| **Correction** | Shape / reference / entity correction of an existing registry row (governed, not a hand-edit) |
| **Orphan repair** | Governed repair of orphaned registry rows |

Each action names its `subjectKind` + `actionCode` at the confirm call. Corrections and repairs are governed
acts through the same gate — the registry is never hand-edited.

**Governing source.** The Business Concept Registry; AI Gates.

## Supersession Rule (amend vs. new entity)

- Changing an entity's **identity-bearing** property set is **supersession** — a new entity (e.g. changing
  `Inventory Position`'s identity from `(Material, Warehouse)` to `(Material, Warehouse, Batch)` changes its
  grain).
- Adding a **descriptive** property is **additive** — non-superseding (e.g. `Customer.loyalty_tier`).

Supersession never retroactively invalidates a contract version that already references the prior concept;
historical references stay addressable (Invariant III).

**Governing source.** The Business Concept Registry §7.

## What the Chain Consumes

Downstream chapters reference the authored concepts — they do not re-author vocabulary:

| Chapter | Consumes |
|---|---|
| Observation Contract Creation | Concepts as `field_mappings[]` targets (source field → business concept); the binding is the OC's job, per-source |
| Canonical Contract Creation | The Entity a Canonical Contract declares (`business_object_code` names an Entity under DEC-02f5a9) and its concepts in `field_selection[]` |
| Metric Contract Creation | Concepts as formula inputs; grain as a **typed reference to a registry Entity** (MCF cannot declare an incoherent grain) |

**Legacy binding tables.** The `contract.business_field` / `contract.business_object` / canonical-field
tables persist physically until the greenfield cutover (DEC-02f5a9 §6) and still carry OC/CC
`field_selection` binding. Where an onboarding chapter names them, that is a **binding mechanic**, not a
vocabulary identity — the identity is the registry concept authored here.

**Governing source.** Observation Contract Creation; Canonical Contract Creation; Metric Contract Creation.

## Quality Gates

| Gate | Where | What it enforces |
|---|---|---|
| Structural identity | Registry schema | `UNIQUE(entity_id, property_id)`; globally-unique entity IDs; acyclic identity-reference graph (a composite entity's identity references form a DAG) |
| Placement (advisory) | AI panel (B6) | Existing entity vs new? existing property vs new? synonym of a governed term? disciplined definition? evidence (not authority) for the source reference? |
| Operator confirm | `registry-shape-certifications/confirm` | High-consequence acts require an operator confirm with a ≥40-char rationale before the F3 write |

The irreversible-uniqueness guarantee is **structural**, not detective — a duplicate cannot be created, so
there is no after-the-fact cleanup of a duplicate that reached `active`.

**Governing source.** The Business Concept Registry §6, §10; AI Gates.

## Drift Inventory

| Drift item | Form |
|---|---|
| Panel path kind/identity lock | The B6 panel path historically minted only `value` + `descriptive` concepts; identity-bearing and reference concepts are authored through the operator-direct surface (paired with the extended S1 validator) |
| Legacy BF/BO/CF tables persist | The `contract.business_field` / `business_object` / canonical-field tables are physically present until the greenfield cutover (DEC-02f5a9 §6); they serve binding, not identity |
| Predecessor chapter | This chapter previously documented BF/BO onboarding (standards-derivation, BO-scoped naming, the five shared dimensions, the BF-to-source-field alias table). That ceremony is superseded; its record remains in the ADR registry and the archived v2 SOPs |

**Governing source.** The Business Concept Registry; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-02f5a9 | Adopts the Business Concept Registry; supersedes the BO/BF/CF model this chapter formerly taught |
| DEC-61850f | Business Concept Registry adoption |
| DEC-ffee4e | BCF panels run in-process in bc-core; the maker/checker/moderator roster is calibration-locked |

The superseded DEC-f66378 (BO-scoped BF naming, five shared dimensions) is retained in the ADR registry for
historical continuity.

**Governing source.** Decisions: ADR Registry.

## References

- The BareCount Business Concept Registry (`implementation/business-concept-registry.md`) — the model
- Business Vocabulary
- The Object Model
- The Contract Grammar
- AI Gates
- AI Trust and Verification
- Observation Contract Creation
- Canonical Contract Creation
- Metric Contract Creation
- Data Model and Schema
- DEC-02f5a9: Business Concept Registry
- DEC-61850f: Business Concept Registry adoption
- DEC-ffee4e: In-process BCF panels; calibration-locked roster
