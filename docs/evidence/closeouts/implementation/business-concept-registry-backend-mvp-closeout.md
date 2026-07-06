---
uid: business-concept-registry-backend-mvp-closeout
title: Business Concept Registry — backend MVP close-out
description: Close-out note for the Business Concept Registry backend MVP. Records the milestone (backend MVP complete; UI/productization remains), the final live Registry state on `bc_platform_dev`, the cert/provenance summary, the architecture completed across F1–F5 / B6–B10b, the live proofs completed for Entity / BusinessConcept / Characteristic, and the explicit non-goals and remaining work. Documentation only — no code, no DB writes, no implementation follows from it. status accepted.
status: accepted
date: 2026-05-23
project: bc-docs
domain: contracts
subdomain: catalog
focus: lifecycle
---

# Business Concept Registry — backend MVP close-out

> **What this is.** The **close-out note** for the Business Concept Registry
> backend MVP. The backend is complete: authoring, AI panel evidence, low-risk
> auto-issuance, high-risk operator confirm, governed `draft → active`
> publication, the immutable-characteristic atom model with a supersession
> safety-net, the F5 read HTTP surface, and the provenance-inspection read all
> ship in `main` and have a live end-to-end proof on `bc_platform_dev`. What
> remains is UI / productization. This is a **design note, not an ADR**;
> `status: accepted`. No code, no DB writes, no implementation follows from it.

## 1. Milestone

**The BCF Business Concept Registry backend MVP is complete. UI / productization remains.**

The Registry now offers a real published lifecycle to expose to operators. Every
backend capability the B10a-S4 UI-readiness checklist named as a class-A
prerequisite for a first operator UI is in `bc-core` `main` at commit
`404331d` (`BCF B10b-S3 — characteristic publication path + provenance read
extension`, PR #86), grounded against the merged authoring chain in `bc-ai`
`main` at commit `0598999` (`BCF B6 F4-v2-S3 — registry-authoring panel
authors characteristics`, PR #17). No remaining backend-architecture
blocker is known for a first operator UI.

## 2. Grounding

This note is grounded against, and does not restate, the following accepted /
decided documents that already carry the authoritative reasoning:

- the accepted **B10 pre-design guardrail** —
  `business-concept-registry-b10-publication-lifecycle-design.md`
- the accepted **B10 implementation design** (B10a/B10b split, UI checkpoints) —
  `business-concept-registry-b10-implementation-design.md`
- the accepted **B10a-S4 UI-readiness checklist** —
  `business-concept-registry-b10a-s4-ui-readiness-checklist.md`
- **ADR DEC-26b6e2 — Immutable Characteristic Atoms** — `docs/adrs/ADR-26b6e2.md`
- the accepted **B10b-S1 DBCP design** —
  `business-concept-registry-b10b-characteristic-supersession-dbcp-design.md`
- the F4-v2 vocabulary-expansion design and the Vocabulary Evidence Framework /
  Admission Checklist notes
- the live state of `bc_platform_dev` on `bc-postgres` (port 5435) on 2026-05-23

## 3. Final live Registry state — `bc_platform_dev`

| Subject kind | Term / canonical name | Registry id | Lifecycle |
|---|---|---|---|
| Entity | `Sales Order Line` | `e974a6cd-8df9-4411-b3e6-ab26cd28fe71` | **active** |
| BusinessConcept | `Sales Order Line · unit price (amount)` | `f66642ad-92b7-4026-a3f6-8179837bf5c3` | **active** |
| Characteristic | `lead time` | `407a6582-08a9-4c7a-ace1-1faa215d770a` | **active** |

No object is archived. The supersession safety-net tables exist and are empty
across all three subject kinds (`concept_registry.characteristic_supersession`,
`business_concept_supersession`, `entity_supersession` — all 0 rows).

## 4. Cert / provenance summary

Six Registry-scope rows in `contract.certification_record` carry the entire
governance history of the three published objects — one authoring cert and
one publication cert per object — emitted by C5 against panel evidence
produced by the bc-ai registry-authoring panel:

| Subject | `action_code` | from → to | Target | `panel_run_uid` | Cert id |
|---|---|---|---|---|---|
| entity | `registry_create` | n/a | `e974a6cd…` | `ea823899-6c2d-44e5-8347-4e6d1155e038` | `45d5d756-906c-4dc0-be62-45b6652cc8d0` |
| business_concept | `registry_create` | n/a | `f66642ad…` | `ccfb6ff7-bbcf-4159-8f44-bb8a92bf7867` | `4e2028d1-330c-4f09-9169-1353c303e75a` |
| characteristic | `registry_author_vocabulary` | n/a | `407a6582…` | `00e7517a-0e4c-419b-9372-b73544545ab0` | `404ac530-5e33-44f7-9dc3-9d810cb3d4d3` |
| entity | `registry_transition` | `draft → active` | `e974a6cd…` | `ea823899-…` | `6ab6be07-2d82-496e-b64d-4ea363b5b1cb` |
| business_concept | `registry_transition` | `draft → active` | `f66642ad…` | `ccfb6ff7-…` | `0f999280-c486-4a30-8535-0ffc6fd148cc` |
| characteristic | `registry_transition` | `draft → active` | `407a6582…` | `00e7517a-…` | `ea2628fb-bd44-4f16-92ad-ee364a7af2d7` |

All three publication certs carry `from_state_code='draft'`,
`to_state_code='active'`, and re-use the original authoring `panel_run_uid` —
the publication cert is issued against the object's original authoring panel
evidence (B10 implementation design D4), not a fresh panel run. C5 verified
the operator confirm on every high-risk action; the characteristic publication
cert additionally records the operator's **semantic-finality affirmation**
required by ADR DEC-26b6e2 — its existence is the affirmation evidence (the
confirm endpoint refuses without `semanticFinalityAffirmed: true`, so a cert
can only exist if the operator affirmed).

## 5. Architecture completed

The backend MVP closes out the following capability set. Each item is shipped
in `bc-core` `main` at or before `404331d` and exercised by the live proofs in
§6; this list is a navigation aid, not a redefinition of the design notes that
authoritatively describe each capability.

- **F1 / F2 — Registry data model** (entity / business_concept /
  characteristic, the F2 version units, alias and representation_term tables,
  the supersession tables).
- **F3 — RegistryAuthoringService** (write boundary): `createEntity` /
  `addEntityVersion` / `transitionEntityLifecycle`; `createBusinessConcept` /
  `addBusinessConceptVersion` / `transitionBusinessConceptLifecycle`;
  `registerCharacteristic` / `transitionCharacteristicLifecycle` /
  `supersedeCharacteristic`. Every write runs under a verified
  `RegistryAuthorization` against a C5-issued Registry-shape cert.
- **F4-v2 — Vocabulary admission**: representation-term grammar, alias model,
  Vocabulary Admission Checklist M1-M10, mechanical pre-flight checks and the
  characteristic-term grammar.
- **F5-S2 — Registry read HTTP surface**: `RegistryReadService` +
  `RegistryReadController` (active-only by default for entity / concept;
  `includeAllStates` opt-in for authoring / provenance contexts).
- **B6 Track 2 — Registry-Authoring Panel** (bc-ai service): per-entry-point
  contracts (createEntity / createBusinessConcept / createCharacteristic),
  evidence classes, deterministic checks ahead of LLM, three-vendor model
  identity recorded on every panel run, grounding-check, sampling pipeline.
- **C5 — FrameworkApprovalService** (cert issuance / confirm boundary):
  `issueRegistryShapeCertification`,
  `confirmRegistryShapeCertification`, `findIssuedRegistryShapeCert`. Subject-
  kind / action-code compatibility matrix, risk-tier classification, deemed-
  approval block, operator-confirm block, the high-risk lock on
  `registry_transition` and `registry_author_vocabulary`, the Fork-ii
  idempotent-resume contract.
- **B10a — Publication path (entity / business_concept)**:
  `RegistryPublicationService` / `Controller`. Two-phase
  `requestPublication` → `awaiting_operator_confirm` →
  `completePublicationConfirm` → F3 `transition*Lifecycle`. Server-resolved
  authoring `panel_run_uid` (never client-supplied), explicit
  `draft → active` transition provenance on the publication cert, Fork-ii
  idempotent resume against stamped / unstamped certs.
- **B10b — Characteristic path under the immutable-atom model** (ADR
  DEC-26b6e2): `concept_registry.characteristic_supersession` table,
  partial-unique `uq_characteristic_term_live` excluding superseded /
  archived rows, F3 `transitionCharacteristicLifecycle` (`draft → active`
  v1) + `supersedeCharacteristic`, publication path extension with operator
  **semantic-finality affirmation** required server-side, provenance read
  extended to characteristic.
- **Provenance-Inspection Read**: `RegistryProvenanceService` /
  `Controller`. `GET
  /api/bcf/registry/provenance/publication/:subjectKind/:registryId` returns
  the publication evidence bundle — target identity, intended transition,
  authoring cert + panel-output summary, publication cert (when present),
  governing policy, semantic-finality requirement/status, and the
  `confirmActionEnabled` boolean a UI binds the confirm action to.

## 6. Live proofs completed

End-to-end proofs against `bc_platform_dev`, each from request through
operator confirm to the F3 lifecycle write, with the publication cert
inspectable through the provenance read:

| # | Subject | Date | Cert | Notes |
|---|---|---|---|---|
| 1 | Entity `Sales Order Line` | 2026-05-22 | `6ab6be07-…` | B10a-S3 — first live publication on the Registry |
| 2 | BusinessConcept `Sales Order Line · unit price (amount)` | 2026-05-22 | `0f999280-…` | B10a-S3 — concept binds to characteristic `unit price` |
| 3 | Characteristic `lead time` | 2026-05-23 | `ea2628fb-…` | B10b-S4 — first live characteristic publication under the immutable-atom model |

The Characteristic proof exercises the semantic-finality affirmation: Phase A
request returned `awaiting_operator_confirm`, the provenance bundle reported
`semanticFinality {required: true, affirmed: false}` and
`confirmActionEnabled: true`, and Phase B confirm with
`semanticFinalityAffirmed: true` flipped the bundle to
`{required: true, affirmed: true}` and the characteristic lifecycle to
`active`. No supersession row was created (the immutable-atom safety-net is in
place but not yet exercised — there is no real correction case to drive it).

## 7. Explicit non-goals (deliberate — out of MVP)

This close-out is for the **backend** MVP. The following are deliberately
**not** in scope and are not blockers on the milestone:

- **Operator UI** — the first operator console for Registry authoring and
  publication. The B10a-S4 UI-readiness checklist names the surfaces it
  binds to; all class-A surfaces it requires are shipped.
- **Review queues** — server-side queues / projections for
  awaiting-confirm work, by subject kind, by risk tier, by submitter.
- **Evidence browser UX** — a renderer for the authoring panel
  transcript, the checklist answers, the grounding citations, the
  model-identity block (the data is fully exposed in the provenance
  bundle; the UX over it is not).
- **Retry / resume UX** — the Fork-ii idempotent-resume contract is
  exercised by the service; an operator-facing affordance for resuming a
  half-completed confirm is UI work, not backend.
- **Search / filtering** — Registry list endpoints expose simple
  filters; full-text, faceted, and semantic search across active /
  draft / superseded vocabulary is productization work.
- **Alias / localization productization** — the F4-v2 alias and
  language-tag model is implemented; bulk authoring of aliases, the
  per-language display picker, and the operator workflow for resolving
  alias conflicts are not.
- **Industry-specific vocabulary flow** — the global / industry-scoped
  classification path in the Vocabulary Admission Checklist is supported
  by the panel; industry-bound seeding workflows and the per-industry
  governance overlay are future work.
- **Live supersession proof** — the immutable-atom supersession path is
  implemented (B10b-S2 migration + F3 `supersedeCharacteristic`) but has
  not been exercised end-to-end. It should be proven when, and only
  when, a real correction case arises; manufacturing a synthetic
  correction to prove the path would itself violate the supersession
  governance rationale (corrections require a real semantic reason).

## 8. Final backend status

**No known backend-architecture blocker remains for a first operator UI.**

The B10a-S4 UI-readiness checklist's class-A surfaces are shipped; its class-C
gate (provenance-inspection read with semantic-finality status) is shipped and
verified against live data. A first UI **must** still use the provenance
bundle's `confirmActionEnabled` and (for characteristic) the
`semanticFinality.required` / `affirmed` block before enabling any confirm
action — the server enforces both gates independently, but the UI should not
present an enabled confirm action without rendering the evidence bundle that
authorizes it.

## 9. Reference — repository HEADs at close-out

- **bc-core** `main`: `404331d` — `BCF B10b-S3: characteristic publication
  path + provenance read extension (#86)`
- **bc-ai** `main`: `0598999` — `BCF B6 F4-v2-S3: registry-authoring panel
  authors characteristics (bc-ai) (#17)`
- **bc-docs-v3** `main`: `589a07d` — `docs(bcf): close out the Business
  Concept Registry backend MVP`, on top of `ba8ab37` —
  `docs(b10b): accept B10b-S1 immutable-characteristic / supersession DBCP
  design`

## 10. Cleanup status

Recorded for completeness — these are the local-environment and repository
hygiene actions that bracket the close-out, not architectural decisions.

- **Local Postgres consolidated to a single instance** — PR #84
  (`chore: single-instance local Postgres — bc-postgres on 5435 with
  bc_platform_dev`, merged into `bc-core` `main` as `e7a0de6`).
  `bc_platform_dev` lives on `bc-postgres` port `5435`; the legacy
  `bc-core` dual-Postgres dev arrangement is retired. All B10b-S2
  migration application and B10a/B10b live proofs ran against this
  single instance.
- **BCF arc feature branches deleted from `bc-core` `origin`** — 18
  squash-merged branches removed after the close-out commit:
  the six `bcf-phase-a-bucket-1-*` branches, `bcf-f2-concept-registry-schema`,
  `bcf-f3-dbcp`, `bcf-f3-slice1`–`slice6`, `bcf-f4-s2-config-fix`,
  `bcf-f4-s2-cp-context`, `bcf-f5-s1-registry-read-surface`, and
  `bcf-b8-calibration-event-ingest`. Each was already squash-merged to
  `main` via its PR; the deletion removes only the now-redundant ref.
  The arc-final branches (`b10b-s2-…`, `b10b-s3-…`,
  `single-instance-local-postgres`, `bcf-provenance-inspection-read`,
  `feat/b10a-s2-registry-publication`) were `--delete-branch`-ed at merge
  time.
- **Non-BCF unmerged branches intentionally left untouched on
  `bc-core` `origin`** — `claude/d369-m22c-per-tenant-bucket`,
  `claude/d382-d383-execution`,
  `claude/ses-932d96-tenant-monitor-endpoint`, and
  `cleanup-bc-platform-dev-naming`. These are not part of this arc and
  not confirmed merged; their owners decide their fate.
- **bc-core remote branch count after cleanup** — five:
  `origin/main` plus the four non-BCF branches above.
- **`bc-docs-v3` and `bc-ai` branch hygiene** — `bc-docs-v3` has no open
  PRs and no arc remnants. `bc-ai` has one pre-existing open PR (#13
  `BCF B6(a): seed_bundle input-context plumbing`, created
  `2026-05-21`) that pre-dates and is orthogonal to this close-out; left
  open for its author.
