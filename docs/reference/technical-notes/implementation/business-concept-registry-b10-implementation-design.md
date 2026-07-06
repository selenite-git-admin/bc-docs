---
uid: business-concept-registry-b10-implementation-design
title: Business Concept Registry — B10 publication / lifecycle implementation design
description: Implementation design for B10 — Registry publication and lifecycle. Resolves decisions D1-D10 against the accepted B10 pre-design guardrail and the live F1/F2/F3/F5 and F4-v2 code. Recommends publication as a governed high-risk draft -> active F3 transition reusing the registry_transition action code (no DDL for Entity/BusinessConcept). D5 amended 2026-05-22 (ADR DEC-26b6e2, Immutable Characteristic Atoms): active Characteristics are immutable semantic atoms — no characteristic_version; a published characteristic is corrected by supersession to a new Characteristic with lineage. Design only — no code, no DDL, no activation. status accepted.
status: accepted
date: 2026-05-22
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# Business Concept Registry — B10 publication / lifecycle implementation design

> **What this is.** The **implementation design** for **B10 — Registry
> publication and lifecycle**. It resolves the ten decisions D1–D10 against the
> accepted B10 pre-design guardrail
> (`business-concept-registry-b10-publication-lifecycle-design.md`,
> `status: accepted`) and the live F1 / F2 / F3 / F5 and F4-v2 code. It is a
> **design note, not an ADR**, and **design only** — no code, no DDL, no DB
> writes, no activation. It elaborates DEC-02f5a9 (D414). `status: accepted` —
> operator review-back 2026-05-22. The guardrail note remains the accepted
> source-of-authority input; this note is its implementation counterpart, kept
> as a separate file so each note's `status` stays honest (the guardrail is
> `accepted`; this design is `accepted`).

## Scope

B10 designs the governed transition that moves a `draft` Registry object to a
published, bindable state, and the lifecycle rules around it. This note states
*what to build*; the build is later, sliced, gated work (§D10). It is bounded by
the seven guardrail locks and the eighth lock (D5 must be resolved) — all
honoured below.

## 1. Findings from the live code

The exploration of the live bc-core Registry code establishes the build surface:

- **F3 already has the entity / concept transition methods.**
  `RegistryAuthoringService.transitionEntityLifecycle(entityId, toState, auth)`
  and `transitionBusinessConceptLifecycle(conceptId, toState, auth)` exist, are
  cert-gated, and update `lifecycle_state` on the anchor. **Entity and
  BusinessConcept publication needs no new F3 method and no new schema.**
- **F3 has no characteristic transition method.** `registerCharacteristic`
  creates a `characteristic` row at `draft`; there is no
  `transitionCharacteristicLifecycle`. B10 must add it.
- **`registry_transition` already exists** — in the `certification_record`
  `action_code` CHECK (28-value list), in the TS `RegistryActionCode` set, and
  in `REGISTRY_OP`. It is classified **high-risk** by `classifyRegistryRiskTier`
  (only `registry_create` / `registry_add_version` are low-risk). The two F3
  transition methods already use it.
- **The five-state lifecycle** — `draft, review, approved, active, superseded`
  — is a DB CHECK on `entity`, `business_concept`, and `characteristic`
  (default `draft`). It lives on the **anchor** rows; `entity_version` /
  `business_concept_version` carry no lifecycle state.
- **`certification_record` carries `from_state_code` / `to_state_code`** (free
  text) — already shaped to record a lifecycle transition.
- **Characteristic is flat** — no `characteristic_version`, no
  `characteristic_supersession`. The current rows: 24 `active` seed
  characteristics, 1 `draft` (`lead time`); 1 `draft` entity; 1 `draft`
  business concept.

## 2. Decisions D1–D10 — recommendations

### D1 — Publication vocabulary

**Recommendation.** Do **not** introduce a new lifecycle state or a `published`
value. Reuse the existing `active` lifecycle state. **"Publication" is the name
of the governed transition (`draft → active`)** — the *act* — not a state.

- `lifecycle_state = 'active'` is the **lifecycle state** (an implementation
  fact, a column value).
- **"Published" is the governed-authority concept** — an object is published
  only when a governed B10 transition produced its `active` state, evidenced by
  a `certification_record`. The guardrail's central warning holds: the cert, not
  the column, is the authority.
- The five-state CHECK (`draft/review/approved/active/superseded`) is unchanged
  — **no DDL to the lifecycle enum.** B10 v1 uses the single `draft → active`
  transition; `review` / `approved` remain valid CHECK values but are unused for
  Registry objects in v1 (reserved).

### D2 — Scope

**Recommendation.** B10 v1 covers the three lifecycle-bearing, draft-bearing
objects: **Entity, BusinessConcept, Characteristic.** **RepresentationTerm and
Alias are explicitly out of scope** — representation terms are a closed
F2-seeded set (no F3 path, no publication lifecycle), and aliases are governed
metadata created within their target's governance act (no independent
publication lifecycle).

### D3 — Risk tier, AI participation, approval

| Sub | Recommendation |
|---|---|
| **D3a — risk tier** | Publication is **high-risk for all three object types.** Publication makes an object authoritative and bindable — inherently high-risk. Keep `registry_transition` high-risk; do **not** reclassify it low-risk. |
| **D3b — AI participation** | **No AI panel at publication in B10 v1.** Publication is not a re-judgement of meaning — the authoring panel already judged the object. The publication cert *references* the original authoring `panel_run_uid` as evidence; no new panel run, no new prompts. AI participation in publication is out of B10 v1 scope. |
| **D3c — operator-confirm** | **Mandatory for all three object types.** High-risk (D3a) routes through the C5 operator-confirm fork; the operator confirm is the human publication authority — the F4-v2 pattern. |

### D4 — Provenance

**Recommendation.** Publication provenance is the `certification_record` row —
the **existing shape, no new columns, no DDL**:

| Field | Value |
|---|---|
| `action_code` | **`registry_transition`** (reused — already in the DB CHECK; high-risk). A dedicated `registry_publish` code is the considered alternative but costs a CHECK migration for no provenance gain — `to_state_code` already discriminates. |
| `subject_kind` | `entity` / `business_concept` / `characteristic` |
| `governance_scope` | `registry` |
| `from_state_code` / `to_state_code` | `draft` / `active` |
| `target_registry_id` | the **id of the published object** — F3 `stampRegistryTarget` write-once-stamps it, marking the cert consumed and linking cert → object |
| `panel_run_uid` | the **original authoring `panel_run_uid`** (D3b). B10 resolves it by reading the object's authoring cert (`target_registry_id = object id`, `governance_scope = 'registry'`). The `certification_record` registry CHECK requires `panel_run_uid IS NOT NULL`, so the authoring run is the evidence chain. |
| operator subject | `gate_results_json.operator_confirm.confirmed_by_sub` (+ `certifier_sub`) |
| rationale | `gate_results_json.operator_confirm.rationale_text` — **reuse the F4-v2 shape verbatim** |
| timestamp | `gate_results_json.operator_confirm.confirmed_at` + the row `created_at` |
| source draft version | for entity / concept, the `active_version_id` at publication time, recorded in `gate_results_json` |

The dedup index `uq_certification_record__registry_dedup` `(panel_run_uid,
subject_kind, action_code) WHERE governance_scope = 'registry'` makes one
authoring panel run authorise exactly one publication per object — the authoring
cert is `(…, registry_author_vocabulary)` and the publication cert is
`(…, registry_transition)`, distinct keys, no collision.

One TS-only change: the pair `(registry_transition, characteristic)` must be
added to `REGISTRY_ACTION_SUBJECT_COMPAT` (the action/subject pairing matrix) —
the DB `action_code` and `subject_kind` CHECKs already permit both values
independently; only the TS compat matrix needs the pair. **No DDL.**

### D5 — Characteristic flatness / versioning — the central decision

> **Amended 2026-05-22 — ADR DEC-26b6e2 (D415), *Immutable Characteristic
> Atoms*.** This section originally recommended **Option 2 — add
> `concept_registry.characteristic_version`**, by analogy to the Entity /
> BusinessConcept versioning model. Operator review-back found the analogy
> unsound and reversed the decision. The original recommendation and its
> `characteristic_version` migration shape are **withdrawn**; the accepted
> decision is **Option B — immutable semantic atoms**, recorded below. §D10
> (slice plan), §3 (source-of-authority check) and F4-v2 §12 are amended to
> match. Nothing in B10a depends on the reversed decision — B10a publishes
> only Entity + BusinessConcept — so no shipped work is affected.

**Recommendation: Option B — an active Characteristic is an immutable semantic
atom.** Publication freezes a characteristic's `(term, definition)` as its
authoritative meaning. An active characteristic's `term` and `definition` are
**never edited in place and never versioned**. A characteristic that needs
correction is **superseded by a new Characteristic**, with explicit lineage.

**Why the versioning analogy fails.** F1 §2's change taxonomy — "a descriptive
(definition-prose) change produces a new version under the stable identity" —
is defined for the **two** versioning units F1 names: the Entity and the
BusinessConcept. Both have a *structural* identity (the Entity's
identity-bearing property set; the BusinessConcept's `(entity, characteristic,
representation term)` tuple) that the definition prose sits *around*. A
**Characteristic has no structural identity.** Its `term` is a label that does
not by itself pin meaning — "lead time *of what, measured how*?" — and its
`definition` is the disambiguating, meaning-constituting content. For a
semantic atom **the definition is the meaning.** F1 §2 itself treats the
characteristic as meaning-bearing: changing *which characteristic* a concept
binds is a meaning-bearing change that mints a new concept identity. A unit
that is a meaning-bearing input to other objects' identity cannot have its own
meaning quietly revised under a stable id.

The withdrawn Option 2 (`characteristic_version`) fails on two counts:

- **It cannot distinguish an editorial fix from a meaning-bearing
  redefinition.** Both would route through `addCharacteristicVersion`. For an
  atom, a definition change is frequently meaning-bearing — and the model has no
  gate that catches it.
- **"No cascade" is a governance bypass, not a benefit.** Under versioning,
  binding concepts keep pointing at the stable `characteristic_id`; advancing
  `active_version_id` silently re-binds every consuming concept to a new meaning
  with **no concept-level re-authoring or re-certification.** That is meaning
  drift under a stable reference — it fails Invariant I (meaning is evaluated
  once, at its boundary) and the spirit of Invariant III (no historical
  rewrite: a concept's resolved meaning would change without the concept being
  re-evaluated).

**Option B — the immutable-atom model.**

- **Publication freezes the atom.** A `draft → active` publication makes
  `(term, definition)` the authoritative, immutable meaning. After publication
  the row's `term` and `definition` are never mutated in place and never
  versioned.
- **Correction is supersession.** A wrong active characteristic is `superseded`
  and a **new Characteristic** (new `characteristic_id`) carries the corrected
  `(term, definition)`, authored through the normal governed F4-v2 / F3 path. A
  `concept_registry.characteristic_supersession` record links predecessor →
  successor — parity with `entity_supersession` /
  `business_concept_supersession`.
- **The supersession records a `correction_class`** — `editorial` (the
  denotation is unchanged; a typo / clarity fix) or `meaning_bearing` (the
  denotation changed). This is audit metadata on a **single authority** — it is
  **not** a second, non-authoritative definition layer. (A "definition-revision
  annotation" was considered and rejected: dual authority is exactly the
  ambiguity a governed registry exists to remove.)
- **Existing BusinessConcepts stay bound to the predecessor.** They were
  authored and certified against that meaning; that binding remains
  historically correct. A concept **adopts the successor** only through a
  **governed new `business_concept_version`** that re-binds it — so a
  characteristic meaning change always re-enters concept-level governance,
  rather than rewriting concept meaning silently.
- **`term` re-use after supersession.** The `characteristic.term` uniqueness
  constraint becomes a **partial unique** scoped to non-superseded (and
  non-archived) rows, so a successor characteristic may carry the same `term`
  as the predecessor it corrects.
- **Publication requires an explicit operator affirmation of semantic
  finality.** Because publication is an immutability commitment, the
  characteristic publication confirm must capture an explicit operator
  affirmation that the meaning is final. *If a characteristic is not stable
  enough to be immutable, it is not ready to be published* — it stays `draft`
  (drafts are freely mutable).

**Consistency.** Option B aligns characteristics with the rest of the
vocabulary: `representation_term` is already a closed immutable-atom set, and
the F4-v2 alias model already assumes one `characteristic_id` = one meaning
(versioning would make a synonym ambiguous across versions). Entities and
concepts remain versioned because they have structural identity; characteristics
do not — the asymmetry is principled, not arbitrary.

**B10b scope — no `characteristic_version`.** Characteristic publication is
still blocked until B10b, but B10b's prerequisite DBCP is now **additive**, not
a versioning restructure:

- a `concept_registry.characteristic_supersession` table (mirrors
  `entity_supersession`) carrying the predecessor / successor ids, the
  `correction_class`, and the authorizing `certification_record_id`;
- the `characteristic.term` uniqueness constraint changed to a **partial
  unique** excluding `superseded` (and archived) rows;
- F3 `transitionCharacteristicLifecycle(characteristicId, toState, auth)` (D6)
  and a characteristic supersession-authoring path.

The flat `characteristic` row is **unchanged** — `term` and `definition` stay
on it; there is **no `definition` relocation and no data migration** of the
existing rows. **Characteristic publication is blocked until this DBCP is
accepted and applied (B10b).** An active characteristic must not exist without
a defined, Invariant-III-safe correction path — and under Option B that path is
supersession, which B10b delivers.

### D6 — F3 / B10 write surface

**Recommendation.** Follow the established per-object F3 pattern — do **not**
introduce a generic `transitionRegistryLifecycle`.

- **F3:** reuse `transitionEntityLifecycle` / `transitionBusinessConceptLifecycle`;
  **add `transitionCharacteristicLifecycle(characteristicId, toState, auth)`**
  (mirrors the existing two; uses `(registry_transition, characteristic)`).
- **A new B10 orchestration service — `RegistryPublicationService`** — mirrors
  the F4-v2 two-phase `completeHighRiskConfirm` flow:
  - *Phase 1* — input `{ subjectKind, registryId, rationale }` + operator from
    `@CurrentUser`; resolve the object's authoring `panel_run_uid` (D4); call
    C5 `issueRegistryShapeCertification({ subjectKind, actionCode:
    'registry_transition', panelRunUid, … })` → high-risk → `operator_confirm_required`
    → return `awaiting_operator_confirm`. **No cert, no transition yet.**
  - *Phase 2* — operator confirm → C5 `confirmRegistryShapeCertification` →
    F3 `transition*Lifecycle(registryId, 'active', auth)` → return `published`.
- **Output contract** — a `RegistryPublicationOutcome` union:
  `awaiting_operator_confirm` / `published` / `already_published` /
  `not_publishable` / `not_issued`.
- **Certification verification** — unchanged: F3's `transition*Lifecycle`
  already verifies the `registry_transition` cert via `CertificationVerifier`.
- **Idempotency / retry (Fork-ii, reused from F4-v2-S2b)** — if the cert issued
  but the F3 transition did not land, the resume path finds the cert and reads
  the object's `lifecycle_state`: already `active` → `already_published`
  (no-op); still `draft` → resume the transition.
- **Pre-state guard** — publication is valid **only `draft → active`**. The B10
  service rejects a publish call when the object is not `draft`:
  `active` → `already_published`; `review` / `approved` → `not_publishable`
  (reserved states, not a v1 path); `superseded` or `archived_at` set →
  `not_publishable` (a clean error — a retired object cannot be published).
- **Confirm seam** — the B10 confirm reuses the operator-confirm pattern;
  whether it shares `POST /api/bcf/registry-shape-certifications/confirm`
  (dispatching by `action_code`: `registry_author_vocabulary` → post-confirm
  `registerCharacteristic`; `registry_transition` → post-confirm transition) or
  uses a publication-specific confirm endpoint is a B10a-S2 build detail; the
  dispatch-by-action_code option avoids endpoint proliferation.

### D7 — F5 read behaviour

**Recommendation — confirmed, no behavioural change.**

- F5 list reads keep the **active-only default** (`resolveLifecycleScope`);
  `draft` / admin reads use the existing explicit `lifecycleState` /
  `includeAllStates` opt-in. No F5 default changes.
- **Concept authoring sees only `active`** — the context builder calls
  `listCharacteristics()` (active-only). Unchanged. A newly published object
  becomes bindable precisely *because* B10 moved it to `active`.
- Admin / draft reads ("list drafts awaiting publication") compose from the
  existing `lifecycleState: 'draft'` filter — no new F5 *method* is required,
  though a convenience aggregator is optional. **The HTTP exposure of F5 reads
  (F5-S2, currently deferred) becomes a B10 dependency** (§D9).

### D8 — Existing draft objects

The three `draft` proof artifacts do **not** publish through one path — the
B10a / B10b split (§D5, §D10) governs them separately. **Nothing is published
now; this note is design only.**

- **Entity `Sales Order Line`** and **BusinessConcept `Unit Price`** are the
  **B10a proof candidates.** Entity and BusinessConcept already carry versioning
  and the F3 transition methods, so B10a publishes them with **no new schema** —
  `transitionEntityLifecycle(…, 'active')` and
  `transitionBusinessConceptLifecycle(…, 'active')`, each operator-confirmed.
- **Characteristic `lead time`** **remains `draft`** — it is **not** a B10a
  candidate. It cannot be published until **B10b** delivers the
  characteristic-supersession DBCP (D5, amended) and the characteristic
  publication path — and then only after the operator affirms its semantic
  finality (D5). `lead time` stays `draft` for the whole of B10a.

Each of the three has an authoring `certification_record`
(`target_registry_id` = its id) carrying the authoring `panel_run_uid` — the
evidence chain D4 needs. (The 24 F4-v1 *seed* characteristics are already
`active`; the seed exemption created no publication debt.) All three are
**legitimate proof artifacts** — correct, well-formed `draft` rows — and each
remains `draft` until its gate (B10a for the entity / concept, B10b for the
characteristic) lands **and** a publication transition is explicitly run.

### D9 — UI implications (backend surfaces only)

The minimum backend the future operator UI needs — B10 defines the surfaces,
not the UI:

| UI need | Backend surface |
|---|---|
| List drafts awaiting publication | F5 `list*({ lifecycleState: 'draft' })` via HTTP (**F5-S2**) |
| Inspect panel output / checklist / cert chain | a read joining object → authoring `certification_record` → `panel_output_record` |
| Confirm a high-risk action | the operator-confirm endpoint (the existing seam) |
| Publish a draft Registry object | the B10 publication endpoint — `POST /api/bcf/registry-publications` (phase 1) |
| View active Registry vocabulary | F5 `listCharacteristics()` / `listEntities()` via HTTP (**F5-S2**) |
| View rejected / operator-review candidates | `panel_output_record` reads filtered by `verdict_code` |

**F5-S2 (the deferred HTTP read controller) is promoted to a B10 dependency.**

### D10 — Slice plan

B10 delivers in **two phases — B10a and B10b** — so the value of B10a ships
without waiting on the B10b characteristic-publication work:

- **B10a — Entity + BusinessConcept publication.** No new schema; reuses F3's
  existing `transition*Lifecycle` methods and C5's high-risk fork. **B10a is
  useful and safe on its own** — it makes the Registry's entities and business
  concepts publishable and is complete without any characteristic capability.
- **B10b — Characteristic publication (immutable-atom model).** The additive
  `characteristic_supersession` DBCP (D5, amended — **no `characteristic_version`**),
  F3 `transitionCharacteristicLifecycle`, and only then the characteristic
  publication path. B10b is the whole of the D5 resolution, and characteristic
  publication is blocked until B10b lands (§D5).

| Slice | Content | Gate |
|---|---|---|
| **B10-S1** | This implementation design note. | Operator review-back accepts D1–D10. |
| **B10a-S2** | bc-core **Entity + BusinessConcept** publication path — `RegistryPublicationService` (two-phase + Fork-ii resume), the controller, the `registry_transition` wiring, reusing F3's `transitionEntityLifecycle` / `transitionBusinessConceptLifecycle` + C5's high-risk fork. **Zero new schema.** One bc-core PR. | PR review (tsc, eslint, vitest). |
| **B10a-S3** | Live proof — publish `Sales Order Line` and `Unit Price`, each operator-confirmed. | Operator opens the run gate. |
| **B10a-S4** | **UI-readiness checkpoint — Entity + BusinessConcept.** Confirm the backend surfaces the operator UI needs for entity / concept publication: the draft queue, the publication-confirm seam, provenance (panel / cert chain) inspection, and the active Registry reads for entity / concept. **UI implementation may begin after B10a-S4 — it does not wait for B10b.** | Checklist review. |
| **B10b-S1** | **Immutable-characteristic / supersession DBCP design** — the `concept_registry.characteristic_supersession` table shape, the `characteristic.term` partial-uniqueness rule (excluding `superseded` / archived rows), the `correction_class` (`editorial` / `meaning_bearing`) field, and the F3 impact. **No `characteristic_version`; the flat `characteristic` row is unchanged** — no `definition` relocation, no data migration. | Operator review-back. |
| **B10b-S2** | **Supersession + partial-unique migration / F3 support** — the DBCP packet (forward / revert migration, Drizzle mirror) for `characteristic_supersession` and the `term` partial-unique constraint; F3 `transitionCharacteristicLifecycle` and the characteristic supersession-authoring path. | DBCP packet review + apply gate. |
| **B10b-S3** | **Characteristic publication path** — `transitionCharacteristicLifecycle` wired into `RegistryPublicationService` with the operator semantic-finality affirmation (D5); characteristic provenance extended into the provenance-inspection read. | PR review. |
| **B10b-S4** | **Live proof — publish `lead time`.** Publishable **only after the operator confirms the characteristic's semantic finality** (D5); operator-confirmed `draft → active`. | Operator opens the run gate. |

The bc-core contract leads; no slice starts before its gate. **B10a (S2–S4) is
independent of B10b and ships first** — and **UI implementation may begin after
B10a-S4 without waiting for B10b.** B10b (S1–S4) follows; **B10b remains required
before `lead time` (the draft characteristic) can be published.** The
characteristic UI-readiness check (the draft-characteristic queue, characteristic
supersession-lineage inspection, the active-characteristic read surfaces) is a
light delta on B10a-S4 once B10b-S4 lands — a follow-on, not a numbered slice.

## 3. Source-of-authority check

B10 honours all eight guardrail locks: F3 stays the sole write path (L1; B10
calls F3, adds one F3 method); publication is a governed F3 transition, not a
raw write (L2); `active` is a state, the cert is the authority (L3); active
meaning is never mutated in place — D5 (Option B, amended) makes characteristic
correction a supersession to a new Characteristic with lineage, never an
in-place edit and never a version bump (L4); full provenance is recorded in the existing
`certification_record` shape (L5); F5 active-only defaults are unchanged (L6);
the three drafts stay `draft` until explicitly published (L7); D5 is resolved,
not left open (L8).

**F1 alignment — no amendment due (D5 amended).** D5 (Option B) keeps F1 §2's
versioning model **exactly as written**: F1 §2 names *two* nested versioning
units — the Entity and the BusinessConcept — and Option B adds no third. A
Characteristic is **not** a versioning unit; it is an immutable semantic atom.
F1 §2 therefore needs no amendment. (The withdrawn D5 Option 2 would have
introduced `characteristic_version` as a third versioning unit and required an
F1 §2 amendment; that action is **cancelled** with the reversal.) F4-v2 §12's
deferred open question — "is a characteristic a vocabulary atom rather than a
structured object?" — is **resolved here in favour of the atom**, and F4-v2 §12
is amended to record that resolution.

No Foundation invariant and no ADR is contradicted; DEC-02f5a9 is unchanged.
The D5 reversal is recorded as ADR **DEC-26b6e2 (D415)** — *Immutable
Characteristic Atoms* — which corrects this note's D5 and resolves F4-v2 §12.

## Status

`accepted` — operator review-back 2026-05-22. A B10 implementation design
resolving D1–D10 against the accepted B10 pre-design guardrail and the live
F1 / F2 / F3 / F5 and F4-v2 code.

> **Amendment — 2026-05-22 — D5 reversed (ADR DEC-26b6e2 / D415, *Immutable
> Characteristic Atoms*).** D5 originally recommended characteristic versioning
> (`concept_registry.characteristic_version`). Operator review-back found the
> Entity/Concept versioning analogy unsound for a semantic atom and reversed it.
> The accepted decision is **Option B — active Characteristics are immutable
> semantic atoms**: publication freezes `(term, definition)`; correction is by
> supersession to a new Characteristic with lineage (`characteristic_supersession`,
> `correction_class`); no `characteristic_version`. §D5, §D10, §3, §D8 and the
> frontmatter are amended accordingly; B10b is re-sliced (S1–S4). The note
> stays `status: accepted` as an erratum to an accepted design. **No B10a work
> is affected** — B10a publishes only Entity + BusinessConcept.

The central recommendations: publication is a governed high-risk `draft →
active` F3 transition reusing `registry_transition` (**B10a** — no DDL, Entity +
BusinessConcept); and **characteristic publication is blocked** until the
additive `concept_registry.characteristic_supersession` DBCP (D5, amended) is
accepted and applied (**B10b**). UI implementation may begin after B10a-S4. No
code, no DDL, no DB writes, and no activation follow from this note.
