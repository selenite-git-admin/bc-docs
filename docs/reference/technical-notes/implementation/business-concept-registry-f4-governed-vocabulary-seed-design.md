---
uid: business-concept-registry-f4-governed-vocabulary-seed-design
title: Business Concept Registry — F4 governed-vocabulary seed design note
description: Design note for Phase F item F4 — the one-time governed-vocabulary seed of the property-characteristic vocabulary through the single F3 certification exemption. Locks v1 scope (characteristics only), the seed-content review packet, the curated-evidence posture, idempotency and rollback, and a three-slice build plan. Accepted 2026-05-21 after operator review.
status: accepted
date: 2026-05-21
project: bc-docs
domain: contracts
subdomain: catalog
focus: architecture
---

# Business Concept Registry — F4 governed-vocabulary seed design note

> **What this is.** Phase F item **F4** of the BCF build plan — the design for
> the one-time governed-vocabulary seed. F4 populates the initial
> property-characteristic vocabulary through the single F3 certification
> exemption (`RegistryAuthoringService.seedGovernedVocabulary`). It is a
> **design note, not an ADR** — it elaborates DEC-02f5a9 and builds on the
> accepted F1 forward-design note and the accepted F3 authoring-service design
> note. F4 carries **no DBCP** — it changes no schema; the `characteristic`
> table already exists from the F2 migration. `status: accepted` — the eight
> D1–D8 decisions of §7 were locked on operator review-back 2026-05-21; the
> note was reviewed against the F3 exemption register and accepted 2026-05-21.

## Scope

This note covers the F4 seed boundary, the seed-content review gate, and the
F4 build slice plan. It does not author the seed list, the seed runner, or the
execution — those are F4 build-time work, sequenced after this note is
accepted. F4 depends on F2 (the `concept_registry` schema) and on F3
(`RegistryAuthoringService`); both are merged. The build-plan §16.5 graph
shows `F2 → F4`; in practice F4 also depends on F3, because the seed runs
*through* `seedGovernedVocabulary` (§2). F4 changes no DEC-02f5a9 / F1 / F3
decision; it elaborates them.

## 1. F4 scope and non-scope

**F4 bootstraps the first governed vocabulary of the Concept Registry.** A
governed vocabulary is **binding, not advisory** — it is the set Registry
authoring *selects from*. A value concept's characteristic is chosen from the
governed `characteristic` set (FK- and CHECK-enforced by F2); a characteristic
outside the governed vocabulary must be governed-added — panel proposal +
operator approval — before any concept can reference it. F4 establishes that
**initial** characteristic vocabulary; the panel grows it thereafter
(governed-open). F4 is therefore not "seeding some terms" — it bootstraps the
governed constraint that makes Registry authoring a disciplined selection
rather than free-text entry.

**In scope — the property-characteristic vocabulary.** F4 v1 seeds
`concept_registry.characteristic` rows: the bounded set of governed
property-characteristic terms the BCF authoring panel's synonym check tests
against. Nothing else.

**Non-scope, and why:**

- **Representation terms — already done in F2.** The F2 migration seeds all 15
  ISO-11179 representation terms (`representation_term`, `added_by = 'f2-seed'`),
  and the closed set is enforced by the foreign key from
  `business_concept.representation_term` — not a CHECK enum. The F3 design note
  §1 states it plainly: the representation-term set "is seeded directly in the
  F2 migration SQL and never passes through F3 at all." F4 does nothing here.
- **Entities — cert-gated, never seeded.** An entity is a structured governed
  object — immutable versions, a five-state lifecycle, an identity-bearing
  property set, supersession lineage. Authoring one is a governance act and
  stays cert-gated through `createEntity` and, in service, the authoring panel.
  The F3 exemption register names exactly one thing, the characteristic seed;
  it does not name entities. F1 §3 is explicit: entities are "registered
  through the authoring panel; seed catalogs (OAGIS nouns, etc.) are *candidate*
  source, never identity authority."
- **Aliases — out of v1 (D6).** Aliases are first-class governed metadata
  (F1 §3), but they are not in the F3 exemption register and
  `seedGovernedVocabulary` has no alias path. Seeding aliases would require an
  **explicit F3 design-note amendment** to widen the exemption register — the
  F3 note states that adding an entry "is itself a governance act — a
  design-note amendment." Not now. Aliases are added later through the
  cert-gated `registerAlias` operation once the panel is in service.
- **Business concepts and lifecycle transitions** — cert-gated authoring acts,
  not vocabulary; not F4.

The distinction that draws the line: a **characteristic is a flat vocabulary
entry** — a `(term, definition)` pair carrying no structural identity, no
references, no grain — which is why it, and only it, is a safe pre-panel seed.
Entities, concepts, and aliases carry governed structure or governed
relationships, and must pass the full certification path.

## 2. The characteristic-only exemption — and why it is not a synonym-control exemption

The F3 authoring-service design note §1 names **exactly one** exemption from
the certification requirement: "the F4 governed-vocabulary seed, the one-time
initial population of the seed `characteristic` rows."
`RegistryAuthoringService.seedGovernedVocabulary` is the single non-verifying
entry point on the service — it issues no `CertificationVerifier.verify()`
call. That is the whole of the exemption.

**The exemption is from certification only — never from synonym control.**
`seedGovernedVocabulary` still calls
`NameConflictChecker.assertCharacteristicTermAvailable` for every term. The two
controls answer different questions and only one of them can be waived at
greenfield:

- **Certification** proves that an external governed *approval* occurred — the
  panel judged placement, Framework Approval recorded a `certification_record`.
  At greenfield, before the panel is in service for vocabulary, that approval
  path does not yet exist for characteristics. F4 substitutes **operator review
  of the seed content** (the review packet, §3) for it. This is what the
  exemption waives.
- **Synonym control** is a **structural invariant** of the registry
  (DEC-02f5a9 §3) — a normalized term resolves to one concept. It must hold for
  every characteristic regardless of how the row entered. A seed that
  introduced a normalized-duplicate term would corrupt the very synonym
  baseline the panel is later asked to test against. It cannot be waived, and
  F4 does not waive it.

The seed path is also **confined to characteristic inserts** — entities,
concepts, aliases, representation terms, and lifecycle transitions do not
travel it. The exemption admits no caller, no environment flag, and no runtime
role; it is a build-time seed method, and that is its entire surface.

## 3. The seed-content review packet

F4 carries **no DBCP** (D7) — it changes no schema. In a DBCP's place, the
seed **content** is reviewed as a data artifact before execution. This review
is not optional bookkeeping: the characteristic vocabulary *is* the bounded set
the panel's synonym check tests against, so noise admitted here propagates into
every downstream synonym judgment. The review packet is the governance act that
substitutes for panel judgment at greenfield (§2).

The packet is a structured artifact. For **each** proposed characteristic it
carries:

- **term** — the characteristic term as it will be stored in
  `characteristic.term`.
- **definition** — the `definition` text (a `NOT NULL` column); a genuine
  definition of the property-characteristic, not a restatement of the term.
- **normalized form** — `normalizeName(term)` (trim → collapse `[\s_-]+` to a
  single space → lowercase); the value the synonym check compares on. Listed so
  the reviewer can confirm normalized-uniqueness by inspection.
- **source / evidence / derivation** — which candidate evidence informed the
  term (a named BF/CF catalog field, an ISO 11179 characteristic, a source /
  seed catalog entry, or hand-authored) and the curation reasoning. Candidate
  evidence is *named*; it is not authority (§4).
- **duplicate / synonym review notes** — for any term that is close to another
  (seed-internal, or against an already-present `characteristic` row), the
  reviewer's note: why both are kept distinct, or that one was dropped or
  merged. The packet must demonstrate the list is normalized-unique.
- **final operator approval status** — per-term and packet-level: the explicit
  operator sign-off that gates F4-S3 execution.

The packet is reviewed and operator-approved **before** the execution gate
(F4-S3). The seed runner and data file additionally receive normal PR review
(F4-S2). An unreviewed or partially-reviewed packet does not execute.

## 4. Seed-source posture — the authority hierarchy

The F4 seed is **authored, not imported**. Three tiers, in strict order of
authority:

1. **The BareCount Concept Registry is the authority.** F4 authors BareCount
   characteristic terms — it does not "seed from OAGIS" or "seed from ISO." The
   Registry owns the final term, its definition, and its identity.
2. **External standards and the `bc_seed` Mongo seed catalogs are
   citation/reference evidence** — consulted in curation, never source
   authority. The **primary** F4 candidate-evidence source is
   **`bc_seed.seed_oagis_components`** — the OAGIS 10.12 catalog, read directly
   from MongoDB at field level (`name`, `representation_term`, `semantic_role`,
   `description`, `cardinality`, `source_url`). Secondary, as citation only:
   **ISO 11179** (the formation discipline / MDR pattern — not term authority);
   **UN/CEFACT CCTS / Core Component Library** where available; **ISO 20022**
   only where a property-level message element directly supports a term;
   **XBRL / IFRS** mostly reporting-concept evidence (Phase G metric /
   canonical), cited only where one directly supports a property characteristic.
3. **Legacy `contract.business_field` / `business_object` / `canonical_field`
   are coverage hints only** — downstream artifacts of the BF/BO/CF model
   DEC-02f5a9 supersedes, wrongly formed for the Registry. They may hint that a
   concept appears in onboarded data; they are **never** evidence for naming,
   definition, or identity, and frequency within them is replication, not
   correctness. They are not imported.

A term becomes a governed characteristic only by passing the curation step and
the operator review packet (§3) — the authority is the Registry's governed
authoring act, not any catalog or standard. The v1 list is **deliberately
bounded** (D8) — a clean synonym-check baseline, not an exhaustive import; the
vocabulary is governed-*open* and the panel grows it after Phase B. F4 seeds
the floor, not the ceiling.

This posture supersedes the earlier "seeded from BF/CF" framing; §7's
"BF/CF → characteristic extraction" implementation question is resolved by it —
`bc_seed.seed_oagis_components` is the candidate-evidence locus, BF/CF demoted
to coverage hint. (§4 sharpened 2026-05-21 by the evidence-posture review.)

## 5. Idempotency and rollback posture

**Idempotency.** `seedGovernedVocabulary` is strict by design — a run that
meets an already-present term throws, and its single transaction rolls back
whole. F4 does not weaken that. Idempotency is the **runner's** responsibility
(D4): the runner queries existing `characteristic` terms, normalizes both
sides, pre-filters out terms already present, and passes only genuinely-new
terms to `seedGovernedVocabulary` — so an all-present re-run is a clean no-op.
The runner also pre-de-duplicates its own input on normalized form (the service
catches intra-seed collisions within its one transaction; the runner catches
them earlier and reports them more legibly). The service stays strict — a
genuine collision among new terms remains a loud error, never a silent skip.

**Lifecycle of seeded rows (D5).** Seeded characteristics become `active` — a
reviewed seed *is* the in-service governed vocabulary, so `active` is its
correct state. The implementation is a **one-line literal**:
`seedGovernedVocabulary` sets `lifecycleState: 'active'` on its
`insertCharacteristic` call. It is **not** a new field on
`SeedGovernedVocabularyInput`, **not** a change to
`VocabularyRepository.insertCharacteristic`, and **not** a caller-supplied
parameter. The `active` state is hardcoded inside the one exempt seed method;
no caller can request a lifecycle state, so **no general lifecycle bypass is
created**. The change is confined to the F4 seed path, as D5 requires.

**Rollback.** The `characteristic` table carries no append-only trigger, so its
rows are physically deletable — but only safely within the **greenfield
window**: before any `business_concept.characteristic_id` references a seeded
row, and before the panel is in service. In that window a mistaken seed is
reversible by an operator-approved delete keyed on the seed's `created_by` tag.
Once real authoring begins, rollback is **soft only** — `archived_at`
(D162 rule 8) or a lifecycle transition — never delete; governed history is
immutable (Invariant III). F4 therefore runs **once, in the greenfield window,
before the Phase B panels go live**. The review packet (§3) is what makes the
list correct before it runs; there is no revert migration because F4 is not a
migration.

## 6. Slice plan

F4 is T-shirt **M**. Three slices, each its own gate.

### F4-S1 — Seed-content artifact (no code)

Curate the v1 characteristic list from BF/CF, ISO 11179, and source-catalog
candidate evidence (§4). Author, per characteristic, the six packet fields of
§3 — term, definition, normalized form, source / evidence / derivation,
duplicate / synonym review notes, and approval status — and confirm the list is
normalized-unique. **Output:** the seed-content review packet. **Gate:** the
operator approves the packet content as a data artifact.

### F4-S2 — Seed runner + data file + tests (one PR)

The **runtime-context decision** is settled in this slice (see §7): either
import `RegistryAuthoringModule` into `AppModule` if the existing seed CLI
requires it, or stand up a seed-only Nest context / module if that avoids
unnecessary global wiring — whichever is the narrowest clean context. Add the
data file (the F4-S1-approved list) and `src/registry/seed/seed-governed-vocabulary.ts`
— the runner: the normalized pre-filter (D4), a dry-run mode, and verification
output. Apply the one-line `lifecycleState: 'active'` change to
`seedGovernedVocabulary` (D5). Unit-test the pre-filter against a mocked
service. **Output:** one bc-core PR, carrying the build-plan §13 trailers.
**Gate:** normal PR review (ESLint / typecheck / vitest).

### F4-S3 — Operator-gated execution

Run the seed against **`bc_platform_dev` only** — never prod, never tenant DBs
— exactly as the F2 and F3 DDL gates were run. **Post-condition checks:** the
seeded row count matches the approved packet; every seeded row has
`lifecycle_state = 'active'`; the characteristic name-space is normalized-unique;
the seed's `created_by` tag is present on every row. **Gate:** the operator
opens the execution gate.

## 7. Decisions locked and remaining implementation questions

### Decisions locked (operator review-back, 2026-05-21)

| # | Decision |
|---|---|
| **D1** | v1 scope = **characteristics only**. No representation terms (F2-seeded), no entities (cert-gated), no aliases. |
| **D2** | **Curated, operator-reviewed** seed list only. BF/CF, ISO 11179, and source catalogs are candidate evidence — not a mechanical import. |
| **D3** | Delivery is the **TypeScript seed path through `RegistryAuthoringService.seedGovernedVocabulary`**. No raw SQL inserts for characteristics — a raw write would bypass the F3 single-writer rule and the synonym check. |
| **D4** | **Runner-side idempotency** — normalize and pre-filter already-present rows; the service stays strict. |
| **D5** | Seeded characteristics become **`active`**, through the F4 seed path only — a one-line `lifecycleState: 'active'` literal inside `seedGovernedVocabulary`. No new input field, no general lifecycle bypass. |
| **D6** | **Aliases out of v1.** Adding aliases to the exemption register requires an explicit F3 design-note amendment; not now. |
| **D7** | **No DBCP.** A **seed-content review packet** (§3) as a data artifact is required before execution. |
| **D8** | **Deliberately bounded** v1 list. The panel grows the governed-open vocabulary later. |

### Remaining implementation questions

Resolved at the named slice, not here:

- **Runtime context (F4-S2).** Import `RegistryAuthoringModule` into
  `AppModule`, or stand up a seed-only Nest context / module — pick the
  narrowest clean context. `RegistryAuthoringModule` is presently **not**
  imported by `AppModule`; this note deliberately does **not** hard-lock the
  `AppModule` import, so that F4-S2 can avoid unnecessary global wiring if a
  seed-only context is cleaner.
- **BF/CF → characteristic extraction (F4-S1).** Confirm what in the live
  `contract` BF/CF schema constitutes a "characteristic" — the precise
  candidate-evidence mapping that feeds the curation.
- **v1 list size (F4-S1).** The bounded term count, settled by the curation
  and fixed by the review packet.

## Status

`accepted` — operator review-back 2026-05-21 locked the eight D1–D8 decisions
and the characteristic-only, curated-evidence posture; the note was reviewed
against the F3 exemption register and accepted 2026-05-21. The F4 build — S1
seed-content artifact, then S2 runner, then S3 operator-gated execution —
proceeds on the operator's go.
