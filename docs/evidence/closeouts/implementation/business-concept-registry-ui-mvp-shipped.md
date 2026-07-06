---
uid: business-concept-registry-ui-mvp-shipped
title: Business Concept Registry — operator console MVP shipped
description: Close-out note for the Business Concept Registry operator console MVP. Records UI-S1 planning → UI-S5 polish completion through a single arc; the final registry state on `bc_platform_dev`; the cert-backed authority discipline the UI enforces; the BF/BO non-touch boundary; and the next major design program (the BF/BO retirement plan). Companion to `business-concept-registry-backend-mvp-closeout.md` (the backend close-out). Documentation only — no code, no DB writes, no implementation follows from it. status accepted.
status: accepted
date: 2026-05-24
project: bc-docs
domain: contracts
subdomain: catalog
focus: ui
---

# Business Concept Registry — operator console MVP shipped

> **What this is.** The **close-out note** for the BCF Registry operator
> console MVP. UI-S1 (planning) → UI-S5 (polish + verification) all
> shipped; the operator can drive the full governed publication lifecycle
> through the UI alone. Companion to
> `business-concept-registry-backend-mvp-closeout.md` (the backend
> close-out, commit `589a07d`) and to **ADR DEC-65dc86 / D416** (the
> sunset declaration — BCF forward, BF/BO legacy compatibility). This is
> a **design note, not an ADR**; `status: accepted`. No code, no DB
> writes, no implementation follows from it.

## 1. Milestone

**The BCF Business Concept Registry has its first operator console MVP. The full backend lifecycle is reachable through the UI alone.**

An operator with a platform-scope Cognito token can now browse all
governed Registry vocabulary, find draft objects eligible for
publication, inspect the full evidence bundle before any high-risk
action, and complete a governed `draft → active` publication — with no
direct API call and no `psql`. The UI mirrors the server's gates
(`confirmActionEnabled`, rationale ≥40 chars, semantic-finality
affirmation for Characteristic per ADR DEC-26b6e2) so an operator
never sees an action the server would reject.

This close-out follows the same shape as the backend MVP close-out: it
records the arc, the final state, and the explicit non-goals — it does
not re-decide anything.

## 2. The arc

| Slice | Status | Artifact |
|---|---|---|
| **UI-S1** — planning note (six screens, seven hard rules, 14-row endpoint mapping, backend-sufficiency finding) | accepted | bc-docs-v3 `58f67db` — `business-concept-registry-ui-mvp-planning.md` |
| **UI-S2** — static skeleton; Business Concepts as new primary nav group; five routes; fixture data | merged | bc-admin `31dbcd3` (PR #7) |
| **UI-S3** — live F5-S2 + provenance reads; no POST | merged | bc-admin `302377c` (PR #8) |
| **UI-S4a** — author fresh draft Characteristic `cycle time` through canonical B6 path (for UI-S4b specimen) | done | bc-platform_dev `7042ca4f-…` (draft) |
| **UI-S4b** — first UI write gate; `usePublicationRequest` + `usePublicationConfirm`; live-published `cycle time` end-to-end through the UI | merged | bc-admin `a394f3a` (PR #9); publication cert `2dc0d5f9-…` |
| **UI-S5** — polish (shared loading/error/empty primitives; copy tightening; A11y on publish flow; Phase 1 skip when bundle already says `already_published`); read-only operator journey verification; this close-out + screenshot pack | merged | bc-admin PR `bcf-ui-s5-polish-and-verify` (this gate); screenshot pack in `docs/assets/screenshots/bcf-ui-mvp/` |

## 3. Final Registry state — `bc_platform_dev`

Captured pre-and-post the UI-S5 read-only journey (identical):

| Subject kind | Term / canonical name | Registry id | Lifecycle |
|---|---|---|---|
| Entity | `Sales Order Line` | `e974a6cd-8df9-4411-b3e6-ab26cd28fe71` | **active** |
| BusinessConcept | `Sales Order Line · unit price (amount)` | `f66642ad-92b7-4026-a3f6-8179837bf5c3` | **active** |
| Characteristic | `lead time` | `407a6582-08a9-4c7a-ace1-1faa215d770a` | **active** (B10b-S4 — published via API) |
| Characteristic | `cycle time` | `7042ca4f-f188-4f35-8a3b-84c01599606b` | **active** (UI-S4b — **published via UI**) |

Cert / supersession counts: 4 `registry_transition` certs, 26 active
characteristics (including the 24 seeded), 0 supersession rows across
all three subject kinds. No object archived.

## 4. The UI is backed by cert/provenance authority — not lifecycle state alone

This is the load-bearing UI discipline. **No screen in the operator
console presents an object as "published" or enables a confirm action
purely on the basis of `lifecycle_state = 'active'`.** Authority always
flows from the `certification_record`:

- Each detail page footer carries the literal rule:
  *"Lifecycle `<state>` is display only — the publication cert in the
  evidence panel is the authority for 'published' status (UI-S1 §4.4,
  ADR DEC-65dc86)"*.
- The Submit enable rule is `bundle.confirmActionEnabled` (computed
  server-side from the certs), **never** `lifecycleState === 'draft'`.
- Characteristic publication additionally requires
  `semanticFinality.required === true` AND the operator's Step C
  affirmation checkbox (ADR DEC-26b6e2). The server independently
  enforces the affirmation; the UI mirror prevents the operator from
  submitting a request the server would refuse.
- The "Already published" banner and the post-publication provenance
  panel render the actual cert id, the `from_state_code` /
  `to_state_code`, and the operator-confirm block — visible audit
  trail, not just a status word.

## 5. BF/BO untouched — legacy compatibility holds

Across all five UI slices, **zero BF/BO files were modified**, and the
"Business Chain" nav group still renders and links exactly as before.
This is the operative discipline of **ADR DEC-65dc86 / D416**: BF/BO is
legacy compatibility, the BCF Registry is the forward model, but
deletion is a later dedicated program. The UI MVP follows that
boundary literally — every list, every detail page, every contract
binding that BF/BO backs in the production pipeline still works.

## 6. UI-S5 — polish summary

UI-S5 made the console **usable**, not merely working:

- **Shared loading / error / empty primitives** lifted to
  `business-concepts/_shared.tsx`; browse and detail render identically;
  the queue keeps its inline variants (which live inside the table-card
  shell, not as standalone cards).
- **A11y — publish-flow focus**: modal `aria-live="polite"` on the
  status region; `aria-live="assertive"` on the failure banner;
  `aria-describedby` on the affirmation checkbox; `aria-describedby` on
  the rationale textarea pointing at the live character counter;
  `aria-label` on the Submit button covering pending state; `aria-hidden`
  on every decorative icon; `role="tab"` + `aria-selected` on the three
  browse tabs; `role="tablist"` on their container; `role="status"` +
  `role="alert"` + `aria-busy` on the shared loading / error primitives.
- **Phase 1 skip on already-published** — when the bundle already says
  `already_published`, the modal does not fire the Phase 1 preflight
  POST. The same sky banner renders from the bundle alone. Saves a
  round-trip on read-only inspections of published objects and lets
  the UI-S5 read-only journey complete with zero `/api/*` POSTs.
- **Copy tightening** — Submit button label gains a screen-reader
  variant ("Publishing — please wait"); rationale counter copy
  unchanged but now linked via `aria-describedby`; banner phrasing kept
  consistent across phase 1 / confirm-failure paths.

## 7. UI-S5 — read-only journey verification

Live operator journey, driven from a real browser through Playwright,
against the running stack (`bc-core` :3100, `bc-admin` :3010,
`bc-postgres` :5435). 10 PNGs in `docs/assets/screenshots/bcf-ui-mvp/`:

| File | Captures |
|---|---|
| `01-nav-business-concepts.png` | Business Concepts nav group visible alongside Source / Business Chain / Canonical / Metric Chain |
| `02-browse-entities.png` | Registry browse — Entities tab |
| `03-browse-concepts.png` | Registry browse — Business Concepts tab |
| `04-browse-characteristics.png` | Registry browse — Characteristics tab (`cycle time` and `lead time` both ACTIVE) |
| `05-empty-facet.png` | Empty lifecycle facet (`superseded` — none exist; facet remains visible) |
| `06-detail-entity.png` | Entity detail — `Sales Order Line` with full provenance |
| `07-detail-concept.png` | BusinessConcept detail — `unit price` with structural identity + provenance |
| `08-detail-characteristic.png` | Characteristic detail — `lead time` with semantic-finality affirmed banner + operator-confirm rationale |
| `09-publication-queue.png` | Publication queue (zero drafts at this moment) |
| `10-modal-already-published.png` | Already-published modal state on `cycle time` (sky banner, Submit disabled, no Phase 1 POST fired) |

**Network discipline.** Across the full journey:
- Total `/api/*` POSTs: **0** (Phase 1 skip on already-published).
- Total POSTs: 2 (both Cognito login required for auth).
- Total `/api/bcf/*` GETs: 17 (the read surface working as designed).

**DB sanity.** Pre-journey and post-journey snapshots are identical
across all seven metrics (active entity count, concept count,
characteristic count, registry_transition certs, three supersession
row counts). No state change.

**Esc-dismiss.** Verified — Escape closes the modal when not pending
(Radix Dialog default; preserved by the `onInteractOutside` guard
that only blocks during pending).

## 8. What this MVP deliberately does not do

Repeat from UI-S1 §6, recorded here for the close-out:

- **No Registry authoring UI** — author through the existing B6
  endpoints (`POST /api/bcf/registry-authoring-runs` +
  `/api/bcf/registry-shape-certifications/confirm`). UI-S4a exercised
  this path via curl-equivalent; an operator-facing authoring UI is a
  separate future gate.
- **No tenant UI** — Registry is platform scope.
- **No characteristic / concept / entity supersession UI** — the
  backend supports it (B10b-S2 + the supersession tables); a UI is
  not yet warranted. When the first real correction case arises, that
  opens its own gate.
- **No bc-ai prompt / panel configuration UI**.
- **No migration / admin DB tooling**.
- **No rejected-candidate browser, no persisted pending-publication
  queue, no search across superseded vocabulary** — all listed as
  class-D fast-follows in the B10a-S4 UI-readiness checklist; the MVP
  ships without them.

## 9. Next major design program

**The BF/BO retirement plan** (per ADR DEC-65dc86 §6). Not a single PR
— a multi-stage program with its own design gates:

1. complete dependency inventory (FK + code + UI + docs + ops),
2. per-table data-migration strategy (7,072 BFs → BusinessConcepts;
   203 BOs → Entities, both through BCF governed authoring),
3. rebind plans for `canonical_contract`, `cc_field_mapping`,
   `observation_field_map`, `runtime.reader`,
4. compatibility windows for tenants,
5. validation proofs (chain integrity, metric snapshot equivalence)
   before each retirement step,
6. rollback rules per stage,
7. explicit operator gates between stages.

No BF/BO row is dropped, no BF/BO table is renamed, no FK is broken
until that program completes its stage-by-stage validation. The
operator console MVP — now shipped — is the prerequisite that lets
operators do work in the BCF model without losing the BF/BO surfaces
they depend on day-to-day during the migration.

## 10. Reference — repository HEADs at MVP close-out

- **bc-core** `main`: `404331d` — `BCF B10b-S3: characteristic
  publication path + provenance read extension (#86)` (backend
  unchanged since the backend MVP close-out)
- **bc-ai** `main`: `0598999` — `BCF B6 F4-v2-S3: registry-authoring
  panel authors characteristics (bc-ai) (#17)`
- **bc-admin** `main`: `a394f3a` — UI-S4b first UI write gate; UI-S5
  polish to land on top
- **bc-docs-v3** `main`: this commit on top of the sunset ADR
  `a23e450` (`DEC-65dc86 / D416`) and the backend close-out cleanup
  amendment `b0f3fcf`
