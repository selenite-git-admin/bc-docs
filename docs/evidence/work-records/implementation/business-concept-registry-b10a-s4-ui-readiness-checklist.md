---
uid: business-concept-registry-b10a-s4-ui-readiness-checklist
title: Business Concept Registry — B10a-S4 UI-readiness checklist
description: B10a-S4 UI-readiness checkpoint. Audits the backend / API / read surfaces that exist after B10a (S1 design, S2 implementation, S3 live proof) against what a first operator UI for Registry authoring and publication needs. Classifies each surface as available now, service-only (needs an HTTP surface), missing-blocker, or missing-fast-follow. Documentation only — no code, no implementation. status accepted.
status: accepted
date: 2026-05-22
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# Business Concept Registry — B10a-S4 UI-readiness checklist

> **What this is.** The **B10a-S4 UI-readiness checkpoint** — a documentation
> audit, not an implementation. B10a is complete: S1 (design), S2 (the bc-core
> publication path, merged `8c22ff5`), S3 (the live proof — Entity
> `Sales Order Line` and BusinessConcept `Unit Price` published `draft → active`).
> The Registry now has a real published lifecycle to expose. This note audits
> what backend / API / read surfaces already exist, what is missing, and what
> blocks a first operator UI for Registry authoring and publication. It is a
> **design note, not an ADR**; `status: accepted` — operator review-back applied
> 2026-05-22 (the provenance-inspection read hardened to a class-C blocker on the
> confirm action). No code, no DB writes, no implementation follows from it.

## 1. Scope and grounding

Grounded against: the accepted B10 implementation design; the B10a-S2
implementation; the B10a-S3 live proof; the F5 read-surface slice plan; the live
bc-core registry controllers/services; and the current active Registry state —
Entity `Sales Order Line` **active**, BusinessConcept `Unit Price` **active**,
Characteristic `lead time` **draft**.

The checklist classifies every surface a first operator UI needs:

| Code | Meaning |
|---|---|
| **A** | **Available now** — an HTTP endpoint exists and is usable by a UI. |
| **B** | **Service-only** — the read/logic exists in an in-process service (F5) but has **no HTTP surface**; a UI cannot reach it. |
| **C** | **Missing — blocker** — does not exist and must be built before a first UI is meaningful. |
| **D** | **Missing — fast-follow** — does not exist; a first UI can ship without it. |
| **B10b** | Deferred to B10b (characteristic publication). |

## 2. The current HTTP surface

Three BCF Registry controllers exist, **all `@PlatformOnly()`, all POST** — the
write / action surface. There is **no GET / read endpoint** in the BCF Registry
surface, and `concept-registry/` (F5) has **no controller at all**.

| Endpoint | Purpose |
|---|---|
| `POST /api/bcf/registry-authoring-runs` | B6 authoring run — submit an inline candidate (createEntity / createBusinessConcept / createCharacteristic) |
| `POST /api/bcf/registry-shape-certifications/confirm` | F4-v2 high-risk authoring operator-confirm (characteristic) |
| `POST /api/bcf/registry-publications` | B10a publication request (phase 1) |
| `POST /api/bcf/registry-publications/confirm` | B10a publication operator-confirm (phase 2) |

**F5 `RegistryReadService`** exists with the full v1 read method set (resolve /
list entities, concepts, characteristics, representation terms, aliases,
supersessions) — but it is an **in-process service only**. Its HTTP controller
is **F5-S2, deferred**. This is the single largest UI-readiness gap.

## 3. The checklist

### 3.1 Candidate / draft queues

| Surface | State | Class |
|---|---|---|
| List draft Entities awaiting publication | F5 `listEntities({ lifecycleState: 'draft' })` exists; no HTTP | **B** |
| List draft BusinessConcepts awaiting publication | F5 lists concepts only **per entity** (`listConceptsForEntity`); no global concept list, no HTTP | **C** (small new F5 method + HTTP) |
| List draft Characteristics awaiting publication | Characteristic publication is B10b | **B10b** |

### 3.2 Publication actions

| Surface | State | Class |
|---|---|---|
| Request publication | `POST /api/bcf/registry-publications` | **A** |
| Confirm publication | `POST /api/bcf/registry-publications/confirm` | **A** |
| Inspect the `awaiting_operator_confirm` outcome | Returned synchronously by the request POST | **A** (single-session flow) |
| Idempotent resume / already-published behaviour | The service Fork-ii returns `published` / `already_published` | **A** |
| A persisted, re-listable "pending publication" queue | Phase 1 writes **nothing** (no cert, no row) — the awaiting state is ephemeral | **D** — a single-session request→confirm UI works without it; an async pending queue is a fast-follow |

### 3.3 Provenance inspection

A meaningful operator-confirm UI must let the operator **see the evidence**
before confirming a high-risk publication. None of this is HTTP-reachable today.

| Surface | State | Class |
|---|---|---|
| Authoring panel output (`panel_output_record`) | In DB; the B4a controller is **write-only** (bc-ai → bc-core); no read endpoint | **C** |
| Authoring certification record | In DB (`certification_record`); no read endpoint | **C** |
| Publication certification record | In DB; no read endpoint | **C** |
| Operator rationale | In `certification_record.gate_results_json.operator_confirm.rationale_text`; needs the cert read | **C** |
| `draft → active` transition provenance | `from_state_code` / `to_state_code` on the publication cert (B10a-S2); needs the cert read | **C** |

#### Hard blocker — the evidence bundle gates the confirm action

This is a **hard UI rule, not a recommendation**: **a first operator UI must not
expose a high-risk confirm action (publication confirm, or any operator-confirm)
as enabled unless it can render the relevant evidence bundle.** An
operator-confirm without visible evidence is a rubber-stamp, which defeats the
governed-publication intent (B10 guardrail; Invariant VI — evidence is emitted
and inspected, not assumed).

The **evidence bundle** must include, at minimum:

- the **target object** identity and its **current lifecycle state**;
- a summary of the **original authoring `panel_output_record`** (verdict,
  classification / checklist answers where applicable, grounding result);
- the **authoring `certification_record`**;
- the **pending / intended publication transition** — explicitly `draft → active`;
- after confirm: the **publication `certification_record`**;
- after confirm: the **operator rationale** and **`confirmed_by_sub`**;
- the **`from_state_code` / `to_state_code`** of the publication cert.

**Sequencing rule.** A UI **may** ship the active Registry browse / read
surfaces (§3.4) earlier — a read-only browse needs no evidence bundle. But it
**must not** present the confirm action as enabled until the
provenance-inspection read exists and the evidence bundle can be rendered. The
provenance-inspection read is therefore a **hard class-C blocker for the confirm
action** — non-negotiable, not a fast-follow.

### 3.4 Active Registry reads

| Surface | State | Class |
|---|---|---|
| Active Entities | F5 `listEntities()` (active-only default); no HTTP | **B** |
| Active BusinessConcepts | F5 `resolveConcept` / `listConceptsForEntity`; no global active-concept list; no HTTP | **C** (global list + HTTP) |
| Derived display label for a concept (e.g. `Unit Price`) | A concept has **no name column** — identity is `(entity, characteristic, representation term)`. A label must be **derived** | **C** — a small display-label projection (derivation rule), but a concept list of bare UUIDs is unusable |
| Structural identity fields (entity / characteristic / representation term) | F5 `resolveConcept` assembles the `entity.property` view; no HTTP | **B** |
| Active-only defaults | F5 `resolveLifecycleScope` — active-only by default, explicit opt-in for other states (F5 plan D4) | **A** (behaviour) — surfaced once F5-S2 lands |

### 3.5 Operator-review / rejected-candidate visibility

| Surface | State | Class |
|---|---|---|
| What exists | A non-APPROVE B6 panel run is parked — the `panel_output_record` (`verdict_code` REJECT / OPERATOR_REVIEW) **is** the evidence (B6 D2 — no rejection-log row) | — |
| What is missing | An HTTP read to list `panel_output_record`s by verdict | **D** |
| Blocks a first UI? | **No.** Publication acts on already-APPROVE'd `draft` objects; rejected-candidate visibility is an *authoring*-UI concern, not a *publication*-UI blocker | **D — fast-follow** |

### 3.6 Auth / permissions

| Surface | State | Class |
|---|---|---|
| Platform-only endpoints | All three BCF Registry controllers carry `@PlatformOnly()` | **A** |
| Operator identity capture | `@CurrentUser()` → `user.userId` (the Cognito sub) → `confirmedBySub` on the cert; captured server-side from the JWT | **A** |
| What the UI must enforce / display | Use a **platform-scope** token (bc-admin scope); send **no** `x-tenant-id` header; display the operator identity on the confirm act; mirror the **≥ 40-char rationale** floor (server-enforced by the confirm DTO `@MinLength`) client-side for UX | **A** (server-enforced; UI mirrors) |

### 3.7 Missing backend surfaces — consolidated

| Surface to build | Why | Class |
|---|---|---|
| **F5-S2 — the F5 HTTP read controller** | Exposes active + draft list/resolve reads for entities and concepts — §3.1, §3.4 depend on it | **C — blocker** |
| **Panel / cert provenance-inspection read** | Renders the §3.3 evidence bundle — a **hard gate on the confirm action**: the confirm must not be enabled in the UI without it | **C — hard blocker** |
| **Global draft / active BusinessConcept list** | F5 lists concepts only per-entity; a UI needs a registry-wide concept list (a small new F5 method, then HTTP) | **C — blocker** |
| **Concept display-label projection** | A concept has no name; a derivation rule (e.g. characteristic term, or `entity.characteristic`) is needed so the UI shows labels, not UUIDs | **C — blocker** (small) |
| Rejected / operator-review candidate list | An authoring-UI surface, not a publication blocker | **D — fast-follow** |
| Persisted pending-publication queue | The awaiting state is ephemeral; single-session confirm works without it | **D — fast-follow** |
| Draft-Characteristic queue + characteristic publication | Characteristic publication is B10b | **B10b** |

## 4. Blockers for a first operator UI

The write / action / auth surface is **complete** — request, confirm, idempotent
resume, platform scoping, and operator-identity capture all exist (§3.2, §3.6).
**Every blocker is on the read side.** Four items, all class **C**:

1. **F5-S2** — the F5 HTTP read controller (active + draft entity/concept reads).
2. The **panel / cert provenance-inspection read** endpoint — a **hard gate on
   the confirm action** (§3.3): a first UI must not present any high-risk
   confirm as enabled until it can render the evidence bundle. Active browse /
   read surfaces may ship earlier; the confirm action may not.
3. A **global BusinessConcept list** (a small F5 method + HTTP) — F5 lists
   concepts only per-entity today.
4. The **concept display-label projection** — a derivation rule.

Items 1 and 3 are naturally one slice (F5-S2, extended with a global concept
list). Item 4 folds into that read surface as a projection. Item 2 is a
distinct, governance-important read.

## 5. Recommended sequencing (for the B10b / UI track to confirm)

This note recommends, but does not open, the following:

- **F5-S2 (+ global concept list + the display-label projection)** — one
  bc-core slice: the HTTP read controller for active/draft entities and
  concepts. Unblocks §3.1 and §3.4.
- **The provenance-inspection read** — one bc-core slice: a `@PlatformOnly()`
  read that, given a draft object or a `panelRunUid`, returns the authoring
  `panel_output_record` + the authoring/publication `certification_record`s +
  the operator-confirm block. Unblocks §3.3.
- With those two slices, a first operator UI for **Entity / BusinessConcept
  publication** is buildable. The B10 implementation design's **B10a-S4**
  position already named F5-S2 as a B10 dependency; this checklist pins it down.
- The fast-follows (§3.5, the pending-publication queue) and the B10b
  characteristic surfaces are explicitly out of the first-UI critical path.

## Status

`accepted` — the B10a-S4 UI-readiness checkpoint, opened and accepted 2026-05-22.
Operator review-back applied: the provenance-inspection read is hardened to a
**hard class-C blocker on the confirm action** (§3.3) — a first operator UI must
not present any high-risk confirm as enabled until it can render the evidence
bundle. Finding: the B10a write/action/auth surface is complete;
the entire **read** surface for a UI is missing its HTTP exposure — four class-C
blockers, all read-side (F5-S2, the provenance-inspection read, a global concept
list, the concept display-label projection). No code, no DB writes, and no
implementation follow from this note.
