---
uid: DEC-26b6e2
title: "Immutable Characteristic Atoms"
description: "Active Characteristics are immutable semantic atoms — no characteristic_version; correction is by supersession. Reverses B10 D5."
status: decided
date: 2026-05-22T15:31:39.733Z
project: bc-docs
domain: contracts
subdomain: semantic-vocabulary
focus: lifecycle
---

# Immutable Characteristic Atoms

## Context

B10 D5 originally recommended characteristic versioning by analogy to the Entity and BusinessConcept versioning model. Review found the analogy unsound. F1 section 2's change taxonomy — a descriptive (definition-prose) change yields a new immutable version under a stable identity — is defined for the two versioning units F1 names, the Entity and the BusinessConcept. Both have a structural identity (the Entity's identity-bearing property set; the BusinessConcept's (entity, characteristic, representation term) tuple) that the definition prose sits around. A Characteristic has no structural identity: its term is a label that does not by itself pin meaning ('lead time of what, measured how?'), and its definition is the disambiguating, meaning-constituting content. For a semantic atom the definition IS the meaning. F1 section 2 itself treats the characteristic as meaning-bearing — changing which characteristic a concept binds mints a new concept identity.

Versioning a characteristic fails on two counts. First, it cannot distinguish an editorial fix from a meaning-bearing redefinition — both route through addCharacteristicVersion — and for an atom a definition change is frequently meaning-bearing. Second, the 'no cascade' property (binding concepts keep pointing at the stable characteristic_id) is a governance bypass: advancing active_version_id silently re-binds every consuming concept to a new meaning with no concept-level re-authoring or re-certification — meaning drift under a stable reference, failing Invariant I (meaning is evaluated once, at its boundary) and the spirit of Invariant III (no historical rewrite — a concept's resolved meaning would change without the concept being re-evaluated).

F4-v2 section 12 had explicitly left this open as a deliberate future question — 'is a characteristic a vocabulary atom rather than a structured object?'. The immutable-atom model resolves it in favour of the atom. It is consistent with representation_term, already a closed immutable-atom vocabulary, and with the F4-v2 alias model, which assumes one characteristic_id equals one meaning (versioning would make a synonym ambiguous across versions). DEC-02f5a9 is unchanged; no Foundation invariant is contradicted.

## Decision

Active Characteristics in the Business Concept Registry are immutable semantic atoms. Publication — the governed draft -> active transition — freezes a characteristic's (term, definition) as its authoritative meaning. An active characteristic's term and definition are never edited in place and never versioned: there is no concept_registry.characteristic_version table and the characteristic row stays flat.

A published characteristic that needs correction is superseded by a new Characteristic — a new characteristic_id carrying the corrected (term, definition), authored through the normal governed F4-v2 / F3 path. A concept_registry.characteristic_supersession record links predecessor -> successor and records a correction_class: 'editorial' (the denotation is unchanged — a typo or clarity fix) or 'meaning_bearing' (the denotation changed). The correction_class is audit metadata on a single authority; it is NOT a second, non-authoritative definition layer (a definition-revision annotation was considered and rejected — dual authority is precisely the ambiguity a governed registry exists to remove). The characteristic.term uniqueness constraint becomes a partial unique excluding superseded (and archived) rows, so a successor may carry the same term as the predecessor it corrects.

Existing BusinessConcepts remain bound to the predecessor characteristic — that binding is historically correct, the meaning they were authored and certified against. A concept adopts the successor only through a governed new business_concept_version that re-binds it, so a characteristic meaning change always re-enters concept-level governance. Characteristic publication requires an explicit operator affirmation of semantic finality: if a characteristic is not stable enough to be immutable, it is not ready to be published and stays draft.

This reverses the B10 publication / lifecycle implementation design's original D5 recommendation (Option 2 — add concept_registry.characteristic_version). Entities and BusinessConcepts remain versioned because they have a structural identity that survives definition-prose revision; Characteristics do not, so the asymmetry is principled.

## Consequences

- **No silent meaning drift** under a stable `characteristic_id` — a published characteristic's meaning is fixed; it cannot be quietly re-pointed by an advancing version.
- **Active BusinessConcepts remain historically stable** — they stay bound to the characteristic meaning they were certified against.
- **Correcting a characteristic can require new BusinessConcept versions** for the concepts that should adopt the successor — the blast radius of a semantic correction is surfaced and routed through governance rather than hidden by a no-cascade rebind.
- **B10b's prerequisite migration is smaller and additive** — a `characteristic_supersession` table, a partial-unique constraint on `term`, and `transitionCharacteristicLifecycle` — not a `characteristic_version` restructuring; there is no `definition` relocation and no data migration of existing characteristic rows.
- **The operator must affirm semantic finality** before a characteristic is published.

## Relationship to prior decisions

This decision corrects decision **D5** of the B10 publication / lifecycle implementation design note (`business-concept-registry-b10-implementation-design.md`) — a design note, not an ADR — and resolves the open question recorded in F4-v2 §12 (`business-concept-registry-f4-v2-vocabulary-expansion-design.md`). It does not supersede any ADR: **DEC-02f5a9** (the vocabulary identity model) stands unchanged, and no Foundation invariant is contradicted. Both affected design notes are amended in the same change set and retain `status: accepted` as errata to accepted designs.
