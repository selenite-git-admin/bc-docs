---
uid: DEC-02f5a9
title: "Business Concept Registry: vocabulary identity model and greenfield rebuild"
description: "Adopt the BareCount Business Concept Registry as the vocabulary identity model; greenfield rebuild of the vocabulary-referencing contract chain; supersedes DEC-a17d0f."
status: decided
date: 2026-05-21T04:37:59.419Z
project: platform
domain: contracts
subdomain: semantic-vocabulary
focus: architecture
supersedes: DEC-a17d0f
---

# Business Concept Registry: vocabulary identity model and greenfield rebuild

## Context

The Business Context Framework (DEC-149ab2, D411) is the AI-assisted governance
discipline for the platform's business vocabulary. BCF governs the vocabulary;
it never defined the vocabulary's *identity model* — what makes two entries the
same concept or two different concepts. That model was implied, never stated:
three separate primitives (Business Object, Business Field, Canonical Field), a
Canonical Mapping binding Business Fields to Canonical Fields, free-text
`object_class` on Business Field, and external standards used as the structural
authority.

That implied model permits two failures: **duplicate concepts** (two identities
for one meaning) and **merged concepts** (one identity spanning two meanings).
Both violate Foundation Invariant I — meaning is evaluated once. For a platform
whose trust promise is *one canonical meaning per business concept*, a duplicate
that reaches `active` is irreversible historical damage.

DEC-a17d0f (the Semantic Definitions Authority) addressed the same drift with a
standing authority: a certification lifecycle and deterministic gates (G2a
exact-identity, G2b normalized-form, G10 Meaning-once) that **detect** collisions
at authoring time. Detection is necessary but not sufficient — a gate guards a
failure mode that remains *reachable*. The trust promise requires the failure to
be **structurally impossible**, not merely **detected**.

A 2026-05-21 first-principles redesign produced the BareCount Business Concept
Registry, filed as the proposal `docs/implementation/business-concept-registry.md`.
A three-layer platform-alignment survey measured the distance from the current
platform to that model. This ADR adopts the Registry as governing architecture
and decides the migration.

## Decision

This ADR is **decided** — governing architecture, not a proposal.

### §1 Adopt the BareCount Business Concept Registry

The platform adopts the model in `business-concept-registry.md` §§1–10 as the
single vocabulary identity model.

- **Three constructs.** *Entity* — a globally governed, role-bearing business
  concept. *Property* — belongs to exactly one entity. *Business Concept* — the
  addressable, observable unit of vocabulary.
- **Concept identity is exactly `entity.property`** — two levels. Nothing else
  disambiguates a concept. Entities are globally unique by surrogate ID; entity
  *names* need not be globally unique, but each canonical name must be
  self-disambiguating in its own wording, never namespace-prefixed.
- **Family is classification, not identity.** Family / owner-domain / tags exist
  for navigation and stewardship; they do not participate in concept identity.
  An entity is the same concept regardless of how it is filed.
- **An entity is a role-bearing business concept**, not a physical thing.
  `Customer`, `Supplier`, `Payer` are distinct entities even when one real-world
  party appears under several roles. Reconciling that the same party plays
  several roles is tenant data at the binding layer, never collapsed in the
  vocabulary.
- **A property is `value` or `reference`.** A value property is a scalar
  carrying representation / type / unit / semantic metadata. A reference
  property points to another entity and carries a `(role, target-entity)` pair.
  Every property carries `identity_role` ∈ {`identity_bearing`, `descriptive`}.
- **Composite / dependent entity identity is represented by its
  identity-bearing properties** — an ordered or named set of identity-bearing
  properties (value or reference). The identity-reference graph is acyclic.
- **Standards are evidence and candidate source, never identity authority.** A
  standard contributes provenance ("this concept traces to standard X"),
  candidate vocabulary for recognition at onboarding, and one bounded content
  contribution (the closed representation-term set, seeded from ISO 11179). It is
  never the authority for identity.
- **BCF governs observable concepts; MCF governs computed metrics.** The
  boundary is *who computes the value*: a value that arrives stored is a BCF
  Business Concept; a value the platform computes over grain, time, filter, and
  formula is an MCF metric. Grain is structural — a metric's grain is a typed
  reference to a Registry entity, not free text.

### §2 Collapse the three primitives

The Contract Grammar's three vocabulary primitives collapse into the Registry:

- **Business Field and Canonical Field collapse into one Business Concept.** The
  source-side / canonical-side vocabulary split (DEC-d72560, partially preserved
  by DEC-a17d0f) is removed. There is one concept registry.
- **Business Object becomes Entity.** The object class *is* the entity — a
  governed reference, not the free-text `object_class` string on Business Field.
- **The Canonical Mapping identity layer is eliminated.** With one concept there
  is no source-side / canonical-side identity to bind.
- **Field-resolution logic survives where it is genuinely real.** Type coercion,
  unit conversion, reduction over grain, and temporal interpretation remain
  authored content within the Observation and Canonical Contracts wherever
  grain, unit, and reduction are real. What is eliminated is Canonical Mapping
  as an *identity* mapping, not the resolution logic.

### §3 Identity is structural, not detected

Identity guarantees move from detection to structure — the substantive
replacement of DEC-a17d0f's gate model:

- **Synonyms** (many names, one meaning) are blocked by construction: identity
  is `(entity, property)`, `UNIQUE(entity_id, property_id)`. A second concept
  for the same identity cannot be created. Replaces gates G2a and G2b.
- **Homonyms / false unifiers** (one name, many meanings) are forced into
  explicit separation by distinct entity / property IDs and definitions; they
  cannot silently share identity. Replaces the Meaning-once detection role of
  gate G10.

The AI Context Authoring Panel is therefore not a duplicate checker; it is a
concept-placement assistant operating *inside* a structurally-governed surface.
It assists framing; it does not own identity. AI remains advisory, never
authority — DEC-a17d0f §5's principle is retained, its mechanism replaced.

### §4 Greenfield rebuild — ID-only references, no compatibility shim

The vocabulary-referencing contract chain is rebuilt greenfield against the
Registry, with **ID-only Registry references** and **no compatibility shim**.
Reasoning:

- Collapsing the Canonical Mapping identity layer (§2) leaves the existing
  mapping layer with no home in the new model. Old mappings cannot be *kept* —
  only discarded. Greenfield is the *consequence* of the adopted model, not a
  separate decision.
- A name-string compatibility shim — resolving old contracts' name-string
  references to Registry concept IDs at read time — resolves them onto a
  vocabulary this ADR declares untrustworthy. That is lower-layer compensation
  for an upper-layer semantic gap, forbidden by the Foundation invariant gate. A
  shim is the corruption preserved, not a fix.
- Rewriting the frozen reference content of finalized contract versions in place
  would violate Invariant III.

**Precondition.** This greenfield decision is valid because the platform is
pre-production: demo tenant, synthetic / SDG data, no tenured customer, no
customer-relied-upon historical evidence. After a production tenant relies on
the old chain, discard would require a separate historical-preservation ADR.

### §5 The cleavage plane

The greenfield rebuild discards and re-authors along this locked plane:

| Layer | Disposition |
|---|---|
| Source registration / seed catalogs | Survive — source knowledge and candidate inputs |
| Source Contract / Admission Contract | Survive — source-reality contracts; reference source fields, not vocabulary |
| Observation Contract family | Survives |
| Existing Observation Contract versions | Re-author against Registry Business Concepts |
| Metric definitions / knowledge (the KPI catalog) | Survive as knowledge — only the binding to concepts is rebuilt |
| Canonical Contract | Discard + re-author against the Registry |
| Metric Contract | Discard + re-author against the Registry |
| Canonical Mapping / `cc_field_mapping` / metric binding / identity mappings | Discard |
| Runtime evidence under discarded or re-authored contract versions | Retired from the active demo chain; regenerated after cutover (§6) |

**Observation Contract — explicit.** The Observation Contract family *survives*:
binding a source field to a concept remains a real admission / observation act.
Existing OC versions are *re-authored* because their `observation_field_map`
binding target changes from `Business Field` to `Business Concept`. Only the
target vocabulary changes; the source→concept binding act is unchanged.

A source field is not vocabulary — it is bound to a concept at the admission
boundary — so Source and Admission Contracts survive untouched.

### §6 Coordinated cutover

- **Runtime evidence.** Runtime evidence evaluated under discarded or
  re-authored contract versions is retired from the active demo chain and
  regenerated after cutover. Whether raw admitted Source Objects are discarded
  or retained as pre-cutover audit artifacts is a cutover-procedure decision;
  they are not carried forward as active evidence under the new chain. Evidence
  carried forward while its governing contract is discarded would be orphaned —
  a violation of Invariants IV and VI.
- **The three primitive identity surfaces** (Business Object, Business Field,
  Canonical Field) are retired or compatibility-wrapped during cutover; physical
  table disposition is a later DBCP.
- **Cutover is sequenced, not an immediate wipe.** The Registry is built —
  tables and authoring — alongside the running existing chain; the
  vocabulary-referencing contracts are re-authored against it; evidence is
  regenerated; then, as the final cutover step, the old vocabulary-referencing
  chain and its evidence are retired from active use together. The existing
  chain keeps the demo tenant alive until the switch.
- **The greenfield window is now** (§4 Precondition). Greenfield is cheap while
  the platform is pre-production and expensive after the first real tenant
  onboards; the cutover should not be deferred.

## Supersession

This ADR **supersedes DEC-a17d0f** (Semantic Definitions Authority).

DEC-a17d0f built a standing authority around the three-primitive model and a
detection-based identity mechanism (gates G2a, G2b, G10). This ADR replaces
both: the three primitives collapse into the Registry (§2), and identity becomes
structural rather than detected (§3).

Carried forward in principle: a single standing authority for vocabulary
identity; lifecycle and supersession discipline; provenance as evidence; AI as
advisory, never authority. Replaced: the three primitives; the detection gates;
the separate six-state primitive certification lifecycle (Registry concepts
follow the Foundation five-state lifecycle); Canonical Mapping governance; the
SDA storage model and the `/api/semantic-definitions/*` surface.

DEC-a17d0f Phase 0 (the read-only projection shipped on bc-core@cb4b972) is
mooted by the greenfield rebuild. DEC-b7affa (D404), which amended DEC-a17d0f
with gate G11, is mooted with it — the structural model has no detection gates.
DEC-a17d0f had itself superseded DEC-5017fe and DEC-d72560; those remain
superseded, and DEC-d72560's source-side / canonical-side vocabulary split is
now fully collapsed.

On filing, DEC-a17d0f's status flips `decided → superseded` with `superseded_by`
set to this ADR, in the same change set.

## Authorized follow-on amendments

This ADR is the governing decision. It does **not** itself rewrite the
Foundation chapters. It **authorizes and requires** the following follow-on
edits, each as a separate commit:

- **`docs/foundation/the-contract-grammar.md`** — remove the three primitives
  (Business Object, Business Field, Canonical Field) and the Canonical Mapping
  supporting schema as an identity mapping; introduce the
  Entity / Property / Business Concept model; retarget the Observation Contract
  `observation_field_map` from "one Business Field" to "one Business Concept";
  retarget Canonical Contract `field_selection` and Metric Contract
  `metric_binding` to Business Concepts; make metric grain a typed Entity
  reference; update `governing_adrs` frontmatter.
- **`docs/foundation/the-object-model.md`** — redefine Business Object as Entity
  (a role-bearing concept, simple or composite).
- **`docs/foundation/the-evaluation-boundaries.md`** — terminological alignment
  only; the four evaluation boundaries are unchanged.
- **BCF requirements and the BCF build plan**
  (`docs/implementation/business-context-framework-build-plan.md`) — collapse
  the three BF / BO / CF scopes to the one Registry; add a registry-substrate
  phase and a cutover phase.
- **Any ADR references that still assume BF / BO / CF as separate identity
  primitives** — reconciled to the Registry model.

Until those edits land, the affected chapters carry stale text; this ADR is the
authority over them from its decided date.

## Options Considered

**Option A — Retain the three-primitive model and DEC-a17d0f's detection
gates.** Rejected: detection is insufficient. A duplicate that passes a gate or
reaches `active` is irreversible; the trust promise requires structural
impossibility.

**Option B — Adopt the Registry, migrate frozen contract references in place.**
Rejected: rewriting the reference content of finalized contract versions
violates Invariant III.

**Option C — Adopt the Registry, keep a name-string compatibility shim for
existing contracts.** Rejected: the shim resolves old references onto a
vocabulary declared untrustworthy — lower-layer compensation for an upper-layer
semantic gap, forbidden by the Foundation gate; and a permanent tax on every
read path.

**Option D — Adopt the Registry, greenfield rebuild, ID-only references, no shim
(chosen).** The mapping collapse leaves no home for old mappings; greenfield is
the model's consequence. A pre-production platform on synthetic data has no
relied-upon history, so the discard does not violate Invariant III.

## Consequences

### Positive

- Duplication and merging become structurally impossible, not detected — the
  trust promise becomes a property of Registry structure.
- One registry replaces three primitives plus a mapping layer.
- Standards are correctly demoted; "standards-compliant" becomes a traceability
  claim, not a correctness claim.
- The AI panel's synonym check becomes bounded (a governed term set) and
  tractable.
- MCF grain becomes a typed entity reference — an incoherent grain cannot be
  declared.
- The greenfield decision removes the compatibility-shim debt entirely.

### Negative

- Re-authoring the Observation Contract versions, Canonical Contracts, and
  Metric Contracts is real work — the Data Seeding and Build Order procedure,
  re-run against the Registry. This work is unavoidable under the Registry model
  regardless; greenfield removes the *shim* cost on top of it.
- The greenfield window is open only while the platform is pre-production;
  deferral raises the cost.
- bc-core schema work is substantial. The three primitive identity surfaces are
  retired or compatibility-wrapped during cutover; physical table disposition is
  a later DBCP.
- Forward-design items remain open (next section).

### Risks

- **Cutover coordination.** Mitigated: the cutover is sequenced, the golden
  snapshot is the rollback, and greenfield rebuilds have precedent (D323, the
  D373 v3 cutover).
- **The Registry must be built before the rebuild can begin.** Mitigated: the
  existing chain keeps the demo alive during Registry construction; the discard
  is the final step.
- **Scope creep into MCF.** Mitigated: the BCF / MCF boundary is explicit (§1).

## Implementation status

Nothing is built. The Registry is a design document; this ADR makes its model
governing and decides the migration strategy. Following it: the BCF build plan
gains a registry-substrate phase and a cutover phase; DBCPs for the registry
tables and for the disposition of the three primitive tables are authored
separately, each operator-approved before any DDL.

## Decision boundary

**Decides:**

- Adopt the BareCount Business Concept Registry as the platform vocabulary
  identity model.
- Concept identity is `entity.property`; family is classification, not identity.
- Entity is a role-bearing business concept; a property is `value` or
  `reference`.
- Composite / dependent entity identity is represented by its identity-bearing
  properties.
- Business Field and Canonical Field collapse into one Business Concept
  registry; Business Object becomes Entity; the Canonical Mapping identity layer
  is eliminated.
- Field-resolution logic survives where grain, unit, reduction, and type
  coercion are genuinely real.
- Standards are evidence and candidate sources, never identity authority.
- BCF governs observable concepts; MCF governs computed metrics.
- Greenfield rebuild, ID-only Registry references, no compatibility shim.
- Coordinated cutover: the old chain keeps the demo alive until the Registry and
  re-authored contracts are ready; the old vocabulary-referencing chain and its
  evidence are then retired from active use together.
- Supersession of DEC-a17d0f.
- The scope of authorized follow-on amendments.

**Does not decide:**

- The registry table DDL and the disposition of the three primitive tables
  (separate operator-approved DBCPs).
- The representation of composite-entity identity at schema level.
- The precise versioning unit (entity-level vs concept-level lifecycle).
- The initial governed content of the entity / property-characteristic /
  representation-term vocabularies.
- The cutover sequencing detail (build-plan work).
- The bc-ai panel's prompt and model specifics.
- The line-level amendment text for the three Foundation chapters.

## References

- `docs/implementation/business-concept-registry.md` — the adopted model.
- DEC-a17d0f — Semantic Definitions Authority (superseded by this ADR).
- DEC-149ab2 (D411) — Business Context Framework.
- DEC-d72560 — Business Field / Canonical Field split (already superseded by
  DEC-a17d0f; fully collapsed here).
- DEC-b7affa (D404) — gate G11 amendment to DEC-a17d0f (mooted with the
  supersession).
- `docs/foundation/the-contract-grammar.md`, `the-object-model.md`,
  `the-evaluation-boundaries.md` — authorized follow-on amendments.
- `docs/foundation/the-invariants.md` — Invariants I, III, IV, VI.
- `docs/implementation/business-context-framework-build-plan.md` — gains the
  registry-substrate and cutover phases.
