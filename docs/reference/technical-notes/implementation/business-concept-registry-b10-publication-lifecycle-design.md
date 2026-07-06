---
uid: business-concept-registry-b10-publication-lifecycle-design
title: Business Concept Registry — B10 publication / lifecycle design note
description: Pre-design note for B10 — Registry publication and lifecycle. Records the source-of-authority findings before implementation begins so draft -> active publication for Registry objects is designed deliberately, not inferred from the draft rows the F-phase and F4-v2 proofs left behind. Locks seven non-negotiable design inputs (F3 sole write path, governed activation transition, no in-place mutation of active meaning, publication provenance, F5 active-only defaults, the unbindable lead time draft, characteristic flatness) and frames eight open decisions D1-D8. A design gate, not an implementation ticket. Accepted 2026-05-22 as a source-of-authority guardrail, not the final B10 implementation design.
status: accepted
date: 2026-05-22
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# Business Concept Registry — B10 publication / lifecycle design note

> **What this is.** A **pre-design** note for **B10 — Registry publication and
> lifecycle**. It is opened deliberately *before* B10 implementation so that
> `draft → active` publication for Registry objects is **designed**, not
> inferred from the draft rows the F-phase and the F4-v2 live proof left behind.
> It records the source-of-authority findings, locks seven non-negotiable design
> inputs, and frames eight open decisions (D1–D8) for the B10 design gate. It is
> a **design note, not an ADR**, and a **design gate, not an implementation
> ticket** — it specifies nothing to build; it scopes what B10 must decide. It
> elaborates DEC-02f5a9 (D414) and builds on the accepted F1 / F3 / F5 and
> F4-v2 notes. `status: accepted` — operator review-back 2026-05-22, accepted as
> a source-of-authority guardrail. **No code, no DDL, no activation.**

## Scope

B10 owns the **publication / lifecycle** layer of the Business Concept Registry
— the governed transition that moves a `draft` Registry object to an active,
bindable state, and the lifecycle rules around it. This note is the pre-design
record: it states the findings and the decisions B10 must resolve. It does
**not** design the transition, author code, or activate anything. F1 (forward
design), F2 (schema), F3 (authoring service), F5 (read surface), and F4-v2
(vocabulary expansion) are all `accepted` and shipped; B10 is the next layer and
the **recommended next gate**.

## 1. Why a pre-design gate — the source-of-authority findings

The F-phase build and the F4-v2 live proof have produced **real `draft`
Registry rows** — a panel-authored characteristic (`lead time`) and the entity /
concept proof artifacts. There is, today, **no governed way to publish them**:
F3's operation set names a "lifecycle transition" for entities and concepts, but
the publication *semantics* — what the active state means, what authority a
transition needs, what provenance it stamps — are undecided. B10 must decide
them deliberately.

The specific risk this gate exists to prevent: **publication being inferred from
a raw `lifecycle_state` write** rather than designed as a governed act. The F3
design note is explicit that the database does not stop this —

> "the F2 meaning-immutability trigger deliberately permits `lifecycle_state`
> updates, so nothing at the database layer stops a stray raw lifecycle write —
> only the sole-write-path discipline does." — F3 authoring-service design §1

— so the discipline must be **designed into B10**, not assumed to exist.

### The central warning

**`lifecycle_state = 'active'` is an implementation state — a column value. It
is *not*, by itself, sufficient publication authority.** An object is
authoritatively published only when a **governed B10 transition** has moved it
there, with the evidence and provenance of that transition recorded (L2, L4). A
row that reads `active` without a governed publication transition behind it is
an unpublished object wearing a published flag — and because the database
permits the column write, that state is reachable by accident or by a stray
path. B10 must therefore make **the governed transition, not the column value,
the definition of "published"**. Any B10 design, diagnostic, or query that
treats `lifecycle_state = 'active'` as proof of publication authority is wrong
by construction.

## 2. Hard locks — non-negotiable inputs to B10 design

These seven are **locked** before B10 design begins. B10 designs *within* them;
it does not reopen them.

| # | Lock | Grounding |
|---|---|---|
| **L1** | **F3 remains the sole Registry write path.** Every `concept_registry` write — including a publication / lifecycle transition — goes through `RegistryAuthoringService`. No raw `INSERT` / `UPDATE`, no F5 write, no second path. | F3 design §1; F5 plan §1, §5 |
| **L2** | **Activation / publication is a governed transition, not a raw lifecycle update.** `draft → active` is a state-changing F3 operation subject to the F3 §1 authorization rule — not a bare column write. | F3 design §1; §1 above |
| **L3** | **Active authoritative meaning must not be mutated in place.** Invariant III — all state is immutable. A correction to an *active* object is a new immutable version (descriptive) or a new semantic identity with supersession lineage (meaning-bearing), never an in-place edit. | Invariant III (`the-invariants.md`); F1 §2 |
| **L4** | **Publication records its provenance.** Evidence, actor identity, the certification / gate record, and the operator rationale are recorded for a publication act — emitted, not inferred (Invariant VI). | Invariant VI; F3 design §5; F4-v2 §11 |
| **L5** | **F5 active-only defaults remain.** List reads default to active-only; a `draft` object is returned only under an explicit `includeAllStates` / `lifecycleState` opt-in. A `draft` Registry object must not leak into concept authoring. | F5 plan §4, D4 |
| **L6** | **The `draft` `lead time` characteristic stays unbindable until B10 deliberately activates it.** F5 exposes only `active` characteristics to the concept panel; `lead time` is `draft` and correctly invisible to binding until a governed B10 activation. | F4-v2 §6, V4; F5 plan §4 |
| **L7** | **Characteristics are currently flat, unversioned vocabulary rows.** `concept_registry` versions `entity` and `business_concept` (each with a `*_supersession` table); it does **not** version `characteristic`. B10 must explicitly decide whether the flat model is acceptable for an activatable, correctable vocabulary, or whether `characteristic_version` / `characteristic_supersession` is required first. | F4-v2 §12; F1 §3; observed schema |

## 3. Grounding

B10 design is bounded by, and must stay consistent with:

- **Foundation invariants** — III (immutable state — no historical rewrite),
  IV (explicit references), V (non-replayable evaluation), VI (evidence emitted,
  not inferred). `the-invariants.md` is authoritative; a B10 design that fails
  any of these is invalid regardless of utility.
- **The Authority Model** (`the-authority-model.md`) — B10 is a descriptive-layer
  implementation note; it may not introduce or redefine an invariant, and it may
  not override an ADR. It elaborates DEC-02f5a9.
- **DEC-02f5a9 (D414)** — the Business Concept Registry decision; B10 changes
  none of it.
- **BCF requirements** (`business-context-framework-requirements.md`) — the
  governing requirement set B10 publication must satisfy.
- **F1 forward design** — the entity / concept versioning units, the Foundation
  five-state lifecycle, the meaning-bearing vs descriptive change taxonomy.
- **F3 authoring-service design** — the sole-write-path rule, the
  external-authorization model, provenance stamping.
- **F5 read-surface plan** — active-only defaults, the explicit opt-in for other
  states.
- **F4-v2 vocabulary-expansion note** — the `draft`-born characteristic (§6,
  V4), the `lead time` live proof (§11), and the characteristic-versioning open
  question (§12).

## 4. Decisions B10 must resolve

Each is **open** — recorded here, decided at the B10 design gate.

**D1 — Publication vocabulary.** What is the published / authoritative state
called — `active`, `published`, `certified`, or another term — and how does it
map onto the existing `concept_registry.lifecycle_state` column and the
Foundation five-state lifecycle (F1 §2)? Today characteristics carry `draft` and
`active`; F3 and F4-v2 speak of `draft → active`. B10 must lock one term and
confirm it means the same thing across entity, concept, and characteristic, and
across F3 and F5 — rather than letting the active state be named or interpreted
differently in different places.

**D2 — Scope.** Which Registry objects does the B10 slice cover — Entity,
Business Concept, Characteristic — and are Representation Term and Alias
explicitly out of scope? Representation terms are a *closed* set (F1 §3) and
aliases are governed metadata attached to the governance act of the term they
annotate (F1 §3). A candidate framing: **B10 covers the three lifecycle-bearing
objects (Entity, Business Concept, Characteristic) and excludes Representation
Term and Alias** — for the gate to confirm.

**D3 — Risk tier, AI participation, and approval.** Three *separate* questions —
they may resolve **differently per object type** (Entity, Business Concept,
Characteristic), and B10 must answer each independently rather than collapsing
them into one "high-risk?" decision:

- **D3a — Publication risk tier.** Is `draft → active` low-risk or high-risk
  under `classifyRegistryRiskTier`, **per object type**? Activating a
  characteristic (a governed-vocabulary term) may warrant a different tier than
  activating an entity or a business concept; B10 sets the tier for each
  object type explicitly.
- **D3b — AI participation.** May an AI panel participate in a publication
  decision, and if so, **purely as advisory evidence** or as a scored
  recommendation? Publication confirms an authoring judgement that was already
  made — the panel's role here is narrower than at authoring time, and may
  legitimately be *advisory-only* or *none at all*. B10 decides, and it may
  decide differently per object type.
- **D3c — Operator-confirm.** Is a C5 operator-confirm **mandatory** for a
  publication transition (as `registry_author_vocabulary` made it mandatory for
  F4-v2 authoring), and is it mandatory for *every* object type or only some?
  Publication makes an object *authoritative and bindable* — a strong argument
  for a mandatory operator-confirm — but this is a B10 decision, not an
  assumption.

B10 must also choose the `action_code`(s) for the transition (see D4).

**D4 — Evidence and provenance.** A publication act **must record a complete
provenance set** — emitted, not inferred (L4, Invariant VI). B10 decides *where*
each field is stamped, but the **set itself is a requirement**, not optional:

- **actor / operator subject** — the Cognito sub of the operator who published;
- **action code** — the publication `action_code` (see D3);
- **subject kind** — `entity` / `business_concept` / `characteristic`;
- **target registry id** — the id of the object being published;
- **source draft id / version** — the draft object, and its version where the
  object is versioned, that the publication transitioned *from*;
- **certification record id** — the governing `certification_record`;
- **rationale** — the operator's stated reason for publishing;
- **timestamp** — when the publication transition occurred;
- **panel_run_uid** — present **if** an AI panel participated (D3b); omitted
  otherwise.

Open for B10: which `subject_kind` / `action_code` the `certification_record`
carries; **where** the set is stamped — F3 stamps `certification_record_id` +
`panel_run_uid` on the *version* rows of entity and concept, but a characteristic
has no version row (L7), so B10 must decide the characteristic's provenance
home; and whether the rationale reuses the F4-v2 shape
(`certification_record.gate_results_json.operator_confirm.rationale_text`).

**D5 — Characteristic lifecycle.** Keep `characteristic` as a flat, unversioned
row, or introduce `characteristic_version` / `characteristic_supersession`
before activation is allowed? **Flatness is not harmless.** A flat row means an
*active* characteristic has **no Invariant-III-safe way to change** — entities
and concepts carry the immutable-version + supersession machinery that lets an
active object be corrected; a characteristic does not. The concrete question B10
must answer: **when an *active* characteristic's definition later needs
correction, what is the allowed path?** Invariant III (L3) forbids an in-place
edit, so B10 must pick — and fully specify — exactly one of:

- **supersede by a new characteristic** — mint a new `characteristic_id`, retire
  the old one with supersession lineage (the entity / concept pattern applied at
  the characteristic grain; every concept binding the old id must re-point);
- **add versioning** — introduce `characteristic_version` (and almost certainly
  `characteristic_supersession`) so a definition correction is a new immutable
  version under a stable `characteristic_id`, exactly as for entity / concept;
- **alias / deprecate** — keep the flat row, deprecate the characteristic, and
  carry the corrected wording through the alias / localization layer rather than
  editing the term in place;
- **prohibit definition edits entirely** — make an active characteristic's
  definition immutable on activation, with **no** correction path — and accept
  the operational consequence that a wrong definition can only be deprecated,
  never fixed.

Each option carries a real cost; none is free, and "leave it flat with no
decision" silently selects the fourth option's consequence without owning it.
This is the **central unresolved issue** (§5) — **B10 cannot be accepted with
D5 open.**

**D6 — F5 / read behaviour.** Confirm — and B10 must not weaken — that: F5 list
reads default to active-only; `draft` / admin reads require an explicit
`includeAllStates` / `lifecycleState` argument; and concept authoring sees
**only `active`** characteristics. A newly activated object becomes visible to
concept binding precisely *because* B10 moved it to `active`; nothing else in F5
changes. B10 confirms this contract; it does not redesign F5.

**D7 — Existing live drafts.** Three `draft` Registry objects exist today, each
authored through the real governed path: Entity **`Sales Order Line`**, Business
Concept **`Unit Price`**, and Characteristic **`lead time`** (`lead time`
verified `draft` in the F4-v2-S4 proof). **These are legitimate proof artifacts
— not failed runs, not temporary test data, not trash to be cleaned up.** Each
was produced by the genuine panel → C5 → F3 path and is a correct, well-formed
`draft` Registry row; they are valuable precisely *because* they are real.

They **must remain `draft` / unpublished until B10 is accepted *and* a
publication transition is then explicitly run** for each. Two conditions, both
required: B10 being accepted does not activate them as a side effect, and no
path other than the governed B10 transition activates them at all. They are the
natural first activation candidates for a **B10 live proof**, *after* the design
is accepted. B10 design should confirm their exact `lifecycle_state` at design
time.

**D8 — Non-goals.** This note and the B10 *design* gate produce **no
implementation, no DB migration, no activation, no bc-ai prompt change, and no
new live run**. B10 implementation — the transition operation, any DBCP, any
panel participation — is sequenced *after* the B10 design is accepted, each
slice its own gate, in the same discipline F3, F5, and F4-v2 followed.

## 5. Source-of-authority conclusion

The current architecture is **on track**. F1–F5 and F4-v2 are internally
consistent: F3 is a clean sole-write-path with external authorization and
provenance stamping; F5 is a clean read-only projection with active-only
defaults; the F4-v2 live proof showed the panel → C5 → F3 governed path working
end to end. Nothing in B10 needs to *correct* the F-phase.

But B10 is a **real, authority-sensitive publication / lifecycle design gate** —
not a mechanical lifecycle-flag flip. Two facts make that true. First, the
database does not enforce publication discipline: `lifecycle_state` is a
writable column, and only the F3 sole-write-path rule stands between a governed
activation and a raw one (L1, L2, §1) — **`lifecycle_state = 'active'` is an
implementation state, never publication authority by itself** (§1, the central
warning). Second — and the **main unresolved issue** — **characteristic
flatness / versioning**. Entities and concepts carry
the immutable-version + supersession machinery that lets an *active* object be
corrected without violating Invariant III; a characteristic does not. Activation
makes an object authoritative; an authoritative object eventually needs
correction; a flat characteristic has no Invariant-III-safe correction path
today. B10 must resolve D5 — before, or as part of, making characteristics
activatable. That single decision is the substantive content of the B10 design
gate.

## Status

`accepted` — operator review-back 2026-05-22. **This note is accepted as a
pre-design / source-of-authority *guardrail* — it is not the final B10
implementation design.** It locks the seven §2 design inputs and the framing of
the eight §4 decisions; it does **not** decide D1–D8. The B10 *implementation*
design is a separate, later gate that resolves D1–D8 within these locks. The
seven §2 locks are now non-negotiable inputs to that gate; **D5 (characteristic
flatness / versioning) is the central unresolved issue, and B10 cannot be
accepted with it open.** No code, no DDL, and no activation follow from this
note.
