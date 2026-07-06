---
uid: business-concept-registry-ui-mvp-planning
title: Business Concept Registry — operator console MVP planning
description: Planning note for the first BCF Registry operator console MVP. Defines user / job, screens, hard UI rules (provenance gate, characteristic semantic-finality), backend surface mapping to existing bc-core endpoints, non-goals, acceptance criteria, and the UI-S1..UI-S5 implementation sequence. Records the finding that the current backend is sufficient for the MVP — no read/action gap remains. Documentation only — no code, no DB writes, no implementation follows from it. status accepted.
status: accepted
date: 2026-05-23
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# Business Concept Registry — operator console MVP planning

> **What this is.** A **planning note**, not an implementation. The Business
> Concept Registry backend MVP is complete
> (`business-concept-registry-backend-mvp-closeout.md`); this note defines the
> first operator console UI that surfaces it. It is a **design note, not an
> ADR**; `status: proposed` — held for operator review before commit and
> before any UI implementation slice opens. No code, no DB writes, and no
> implementation follow from it.

## 1. Grounding

- the accepted close-out —
  `business-concept-registry-backend-mvp-closeout.md`
- the accepted **B10a-S4 UI-readiness checklist** —
  `business-concept-registry-b10a-s4-ui-readiness-checklist.md`
  (the four class-C read blockers it identified are now all closed; the
  hard-gate-on-confirm rule it pinned down still stands)
- the accepted **B10 implementation design** —
  `business-concept-registry-b10-implementation-design.md`
- **ADR DEC-26b6e2 — Immutable Characteristic Atoms** — `docs/adrs/ADR-26b6e2.md`
- the live bc-core endpoints in `main` at `404331d`:
  - `RegistryReadController` — `GET /api/bcf/registry/*` (F5-S2)
  - `RegistryProvenanceController` —
    `GET /api/bcf/registry/provenance/publication/:subjectKind/:registryId`
  - `RegistryPublicationController` —
    `POST /api/bcf/registry-publications` and `/confirm`
  - all `@PlatformOnly()`

## 2. MVP user and job

**User:** a BareCount platform operator (bc-admin scope), the same role that
issued the operator-confirm on the B10a / B10b live proofs.

**Jobs the operator does in the MVP:**

1. **Browse active Registry vocabulary** — see what is governed and active
   right now (Entities, BusinessConcepts, Characteristics), and look at the
   structural identity of any one of them.
2. **Find work to do** — see which draft Registry objects are eligible to be
   published, and which are not (and why).
3. **Inspect evidence before acting** — for any object in scope, open the
   publication evidence bundle and read the authoring panel verdict, the
   authoring cert, the governing policy, and (once published) the publication
   cert and the operator-confirm block.
4. **Publish a draft object through the governed confirm** — request →
   review the evidence → confirm. For a draft Characteristic, additionally
   affirm semantic finality.
5. **Verify after publishing** — see the object flip to `active`, see the
   publication cert that authorized the flip, and see the evidence bundle
   close with `semanticFinality.affirmed = true` for a published
   characteristic.

This is a **publication / inspection** UI. Authoring (creating a new
candidate Entity / BusinessConcept / Characteristic) is **not** part of the
MVP; see §6.

## 3. MVP screens

Six screens. Two are list-shaped, three are detail-shaped, one is a modal /
flow. Every screen is read-only except the publish flow, which is a
two-step governed action delegating to the existing C5 + F3 plumbing.

### 3.1 Registry browse (list)

Three tabs — Entities, BusinessConcepts, Characteristics — each a paginated
list with simple filters. Active-only by default; a "lifecycle" facet lets
the operator switch to `draft` / `superseded`. Every row shows a derived
human label, never a bare UUID.

- **Entities tab** — canonical name, family code, owner domain, lifecycle.
- **BusinessConcepts tab** — derived `displayLabel`
  (`entity · characteristic (representation term)` for a value concept;
  `entity · referenceRole → targetEntity` for a reference concept), kind,
  identity role, lifecycle.
- **Characteristics tab** — term, definition, lifecycle.

### 3.2 Draft publication queue (list)

A focused view of "what is eligible to publish right now". A union of three
lists, each filtered to `lifecycleState = 'draft'` and grouped by subject
kind. Each row links to the object detail page (§3.3) where the evidence
bundle is rendered.

This view is intentionally **derived from the F5 reads** — there is no
backend "pending publication queue" today (the awaiting-confirm state is
ephemeral; see §5 of the UI-readiness checklist). The MVP queue is a
live read of draft objects, not a persisted work-list.

### 3.3 Object detail page

One page per subject kind, accessed by id from §3.1 or §3.2.

- Header: derived display label, subject kind, current lifecycle.
- Identity block — the F5 read projection:
  - **Entity** — canonical name, definition, family / owner.
  - **BusinessConcept** — entity, characteristic, representation term,
    data type, unit, semantic role (value); or reference role + target
    entity (reference). The `displayLabel` is the F5 derivation, never a
    raw UUID.
  - **Characteristic** — term, definition. (No version, no structural
    sub-identity — characteristic is the immutable atom per ADR
    DEC-26b6e2.)
- Provenance panel (§3.4), inlined.
- Publish action (§3.5), enabled only under the §4 hard rules.

### 3.4 Evidence bundle / provenance panel

A renderable view of the publication evidence bundle returned by
`GET /api/bcf/registry/provenance/publication/:subjectKind/:registryId`.

- Status badge: `ready_for_publication_confirm` /
  `missing_authoring_evidence` / `already_published` / `not_publishable`
  (+ `notPublishableReason`).
- Intended transition — always `draft → active`.
- Authoring evidence — the panel `verdict_code`, the checklist
  summary (where applicable — characteristic carries `M1..M10`), the
  grounding result, the cited sources, the model identity (maker /
  checker / moderator), the authoring cert id + operator-confirm block.
- Governing policy uid + version.
- Semantic-finality block (characteristic only) — `required: true` and
  the current `affirmed` value.
- Publication cert (if present) — id, `from_state_code`,
  `to_state_code`, operator sub, operator rationale,
  `confirmed_at`.
- The boolean `confirmActionEnabled` (the UI never recomputes it; it
  binds the action's enabled state to this value).

### 3.5 Publication confirm flow

A modal / step initiated from §3.3 when `confirmActionEnabled = true`.

- Step A — re-render the evidence bundle in confirm context (the
  operator must see what they are authorizing).
- Step B — rationale capture, a single textarea with client-side
  validation mirroring the server `@MinLength(40)` rule and a live
  character count.
- **Characteristic-only step C** — an explicit checkbox
  *"I affirm the term and definition are semantically final
  (ADR DEC-26b6e2)"*. The submit button is disabled until checked.
  The checked state is the `semanticFinalityAffirmed: true` value on
  the confirm payload. (Server independently refuses the confirm
  without this flag; the UI rule mirrors the server, it does not
  replace it.)
- Submit — `POST /api/bcf/registry-publications/confirm`. On
  `published` the modal closes and the detail page re-fetches the
  provenance bundle (§3.6). On `already_published` the modal closes
  and shows the existing publication cert. On `not_publishable` /
  `not_issued` the modal stays open with the failure reason.

The phase-1 `POST /api/bcf/registry-publications` is run **before** the
modal opens (a single-session request → review → confirm flow). The
operator never sees `awaiting_operator_confirm` as a screen — it is the
implicit transition between Step A's render and Step B's input.

### 3.6 Post-publication cert / provenance view

After Step B succeeds, the operator stays on the object detail page
(§3.3) and its provenance panel (§3.4) re-renders against the just-issued
publication cert. Status badge flips to `already_published`,
`publicationCertification` populates, the operator-confirm block becomes
visible, and (for characteristic) `semanticFinality.affirmed` flips to
`true`.

No new page — the MVP cert view IS the provenance panel post-confirm.

## 4. Required UI rules (hard, not preferences)

These are server-enforced; the UI mirrors them so an operator never sees
an action that the server would reject.

1. **The confirm action is never enabled without a rendered evidence
   bundle.** The UI must call the provenance read, render the bundle,
   and bind the confirm action's enabled state to `confirmActionEnabled`
   from the response. This is the B10a-S4 §3.3 hard rule.
2. **For a Characteristic confirm, additionally require
   `semanticFinality.required = true` and explicit operator affirmation
   in the UI** (the §3.5 Step C checkbox). The submit button stays
   disabled until checked; the payload carries
   `semanticFinalityAffirmed: true`.
3. **Display labels everywhere — never a bare UUID** where a derived
   label exists. The F5 reads return `displayLabel` for concepts;
   entity canonical names and characteristic terms are direct
   columns. UUIDs are exposed only in evidence-detail views (cert ids,
   panel run uid) where the audit identity is the point.
4. **`lifecycle_state = 'active'` alone is not publication authority.**
   A list or detail page must not present an object as "published" by
   lifecycle state alone — the publication cert (with `from_state_code`
   / `to_state_code` and the operator-confirm block) is the
   authoritative publication artifact, rendered in the provenance
   panel.
5. **No characteristic supersession authoring in the MVP.** The
   supersession path is implemented in the backend but is not part of
   the MVP UI (see §6). Should an operator open a published
   characteristic, no "Supersede" action is offered.
6. **Rationale length floor mirrored client-side.** The server requires
   `@MinLength(40)` on the confirm rationale; the UI shows a live
   character count and disables submit below 40.
7. **Platform-scope token; no `x-tenant-id`.** Every Registry endpoint
   is `@PlatformOnly()`. The UI must send a platform token and **no**
   tenant header; the operator identity comes from the JWT
   (server-side `@CurrentUser().userId`).

## 5. Backend surface mapping

Every MVP screen / action maps to an existing bc-core endpoint at
`main` `404331d`. No new endpoint is required for the MVP.

| Screen / action | Endpoint(s) | Notes |
|---|---|---|
| §3.1 Browse — Entities tab | `GET /api/bcf/registry/entities` | F5-S2; active-only default, `lifecycleState=draft` / `includeAllStates=true` opt-ins; `q`, `familyCode`, `ownerDomain` filters; keyset pagination |
| §3.1 Browse — BusinessConcepts tab | `GET /api/bcf/registry/concepts` | F5-S2 registry-wide list; returns `ConceptListView` with derived `displayLabel`; `kind`, `identityRole` filters |
| §3.1 Browse — Characteristics tab | `GET /api/bcf/registry/characteristics` | F5-S2; `q` filter for term search |
| §3.2 Draft queue — Entities row | `GET /api/bcf/registry/entities?lifecycleState=draft` | Same list endpoint, filtered |
| §3.2 Draft queue — Concepts row | `GET /api/bcf/registry/concepts?lifecycleState=draft` | Same list endpoint, filtered |
| §3.2 Draft queue — Characteristics row | `GET /api/bcf/registry/characteristics?lifecycleState=draft` | Same list endpoint, filtered |
| §3.3 Entity detail | `GET /api/bcf/registry/entities/:id?includeAllStates=true` | `includeAllStates=true` so a draft entity resolves |
| §3.3 BusinessConcept detail (active) | `GET /api/bcf/registry/concepts/:conceptId` | Active anchor only |
| §3.3 BusinessConcept detail (draft) | `GET /api/bcf/registry/concept-versions/:conceptVersionId` | Resolves any state including draft |
| §3.3 Characteristic detail | `GET /api/bcf/registry/characteristics/:id` | Flat row — no version |
| §3.4 Provenance panel | `GET /api/bcf/registry/provenance/publication/:subjectKind/:registryId` | Full evidence bundle incl. `confirmActionEnabled`, `semanticFinality` |
| §3.5 Publish — phase 1 (request) | `POST /api/bcf/registry-publications` | Body: `{subjectKind, registryId}`; returns `awaiting_operator_confirm` or a terminal outcome |
| §3.5 Publish — phase 2 (confirm) | `POST /api/bcf/registry-publications/confirm` | Body: `{subjectKind, registryId, rationale}` (+ `semanticFinalityAffirmed: true` for characteristic); operator sub injected server-side from JWT |
| §3.6 Post-publication view | re-fetch §3.4 | No new endpoint — the provenance bundle re-renders against the just-issued publication cert |

**Backend gap analysis: none for the MVP.** All four class-C blockers
the B10a-S4 UI-readiness checklist identified are closed. The two
class-D fast-follows it identified (a persisted pending-publication
queue; a rejected-candidate visibility surface) remain fast-follows and
are deliberately not part of the MVP (§6).

## 6. Non-goals

Out of scope for this MVP — recorded explicitly so a UI slice does not
quietly grow them. Each is a defensible follow-on, none is a blocker on
shipping the MVP.

- **No Registry authoring UI** — no "create Entity / BusinessConcept /
  Characteristic" flow. Authoring already runs through the B6
  registry-authoring panel and the
  `POST /api/bcf/registry-authoring-runs` /
  `POST /api/bcf/registry-shape-certifications/confirm` endpoints; an
  operator-facing UI for it is a separate gate. The MVP exercises the
  artifacts the existing authoring flow produces.
- **No tenant UI.** The Registry is platform scope (`@PlatformOnly()`);
  the MVP is a bc-admin (platform) console. No `x-tenant-id`, no
  per-tenant view.
- **No characteristic supersession UI.** Supersession is implemented in
  the backend (B10b-S2) but has not been exercised end-to-end; a UI
  for it should not lead the live proof. When a real correction case
  arises, supersession opens its own UI gate.
- **No bc-ai prompt / panel configuration UI.** Panel prompts, the
  Vocabulary Admission Checklist version, the model roster are
  authored as code / config in `bc-ai`; an operator UI for editing
  them is out of scope.
- **No migration / admin DB tooling.** No DDL surface, no manual cert
  surgery, no seed re-loader. The DBCP path stays in code review.
- **No rejected-candidate browser, no persisted pending-publication
  queue, no search across superseded vocabulary.** All three are
  listed in the B10a-S4 checklist as class-D fast-follows; the MVP
  can ship without them.
- **No metrics / readiness / chain status surfaces.** The MVP is
  Registry-only. Metric readiness (D316) etc. ships in its own UI
  surface.

## 7. MVP acceptance criteria

The MVP is acceptable when:

1. The operator can browse active Entities, BusinessConcepts, and
   Characteristics with derived display labels (no bare UUIDs in
   list rows).
2. The operator can open a draft publication queue and see every
   `draft` Entity / BusinessConcept / Characteristic eligible for
   publication.
3. The operator can open the evidence bundle for any object in scope,
   and the bundle correctly reports `confirmActionEnabled` and (for
   characteristic) `semanticFinality.required`.
4. The operator can complete a governed publication for an Entity, a
   BusinessConcept, and a Characteristic — request, evidence review,
   confirm, success — entirely through the UI, with zero direct API or
   `psql` use.
5. The characteristic publish flow requires the §3.5 Step C
   semantic-finality checkbox to be checked before submit, and posts
   `semanticFinalityAffirmed: true`.
6. After publish, the operator sees the publication cert
   (`from_state_code='draft'`, `to_state_code='active'`, operator sub,
   rationale) in the provenance panel without leaving the object
   detail page.
7. The UI never offers a confirm action without first rendering the
   evidence bundle (rule §4.1) and never offers a Characteristic
   confirm without the affirmation checkbox (rule §4.2).

## 8. Recommended implementation sequence

Five slices. Each opens as its own gate, with its own review.

- **UI-S1 — this planning note.** Accept this document; lock the
  screens, the rules, and the backend mapping. No UI code.
- **UI-S2 — static route / component skeleton.** Build the
  routes for §3.1 / §3.2 / §3.3, with mocked data and the §3.4
  panel as a static component. No API calls. The goal is the
  navigation, the layout, and the rule-of-six-screens working
  in isolation.
- **UI-S3 — read-only browse / detail / provenance.** Wire the
  F5 reads (`/api/bcf/registry/*`) and the provenance read
  (`/api/bcf/registry/provenance/*`). All confirm actions stay
  disabled — there is no §3.5 yet. This slice can ship to
  `bc_platform_dev` and an operator can browse the three
  live-active objects and the live provenance bundles.
- **UI-S4 — publication request / confirm flow with hard
  gates.** Build §3.5 and §3.6. Enable the confirm action only
  through `confirmActionEnabled`; add the Step C affirmation
  for characteristic. End-to-end test: a hypothetical fresh
  draft object goes from §3.2 → publish → §3.6 in one session.
- **UI-S5 — polish + live verification.** Empty states,
  error states, loading skeletons, the rationale character
  count and the affirmation checkbox copy review,
  accessibility pass on the confirm flow. Live verification:
  the operator publishes a real draft object end-to-end
  through the UI (not the API).

## 9. Backend sufficiency finding

**The current backend is sufficient for this MVP. No new read or
action endpoint is required.**

The four read blockers the B10a-S4 UI-readiness checklist identified
(F5-S2 entity / concept reads; a global concept list; characteristic
reads; the provenance-inspection read) are all closed in `bc-core`
`main` at `404331d`. `ConceptListView` and `ResolvedConcept` carry the
derived `displayLabel` the checklist named as the fourth blocker;
characteristic reads were folded in alongside the B10b publication
path. The publication request / confirm pair and the platform-scope
guard are unchanged.

A small fast-follow surface (rejected-candidate browser, persisted
pending-publication queue) remains class-D in the checklist — the MVP
deliberately does not depend on either.

## Status

`accepted` — operator review-back applied 2026-05-23: all ten acceptance
checks (operator-console framing; evidence-bundle hard gate; explicit
distinction of browse / publication / authoring / supersession UIs with
authoring + supersession deferred out of MVP; `active` as display only
with cert as authority; Characteristics included under immutable-atom
semantics; concrete endpoint mapping; honest gap call-out; tenant / AI /
admin / migration UIs out of scope; sequenced without opening
implementation) passed against the draft as filed. The recommended next
gate is **UI-S2 — the static route / component skeleton**; UI-S2 opens
no backend changes and makes no live API calls. This note is the UI-S1
artifact.
