---
id: business-field-and-business-object-onboarding
order: 53
title: "Onboard a business concept"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "Add one entity, business concept or characteristic to the business concepts registry, so a directory group or member can name it."
governing_sources:
  - The Contract Grammar
  - The Authority Model
  - The Evaluation Boundaries
governing_adrs:
  - DEC-79b62f (the Foundation gate: the repair locations and the four questions)
  - DEC-02f5a9 (Business Concept Registry; supersedes the BO/BF/CF vocabulary)
  - DEC-61850f (Business Concept Registry adoption)
  - DEC-ffee4e (BCF panels run in-process in bc-core; calibration-locked roster)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Onboard a business concept

*DevGuide · task guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW064 Author Business Concepts, PW065 Publish Business Concepts, PW005 Manage Business Concepts

## Chapter 1. Overview

This chapter describes the one task of this guide and its place in onboarding a metric. A business concept is a named, governed meaning in the business concepts registry: an entity (what a row is about), a business concept (`entity.property`) or a characteristic (a reusable kind of value). One of two makers shapes it (the authoring panel, or the operator directly with no AI); then one confirm chain certifies and writes it.

### What the guide covers

This section lists the acts of the task in order.

- Check what already exists (step 1).
- Run the authoring panel, or use the direct maker (step 2).
- Read the verdict (step 3).
- For a run sent to review: adopt or set aside (step 4).
- Confirm a high-risk act (step 5).
- Publish a draft (step 6).
- Read back (step 7).

### Where it sits

This section describes when the task is needed, what must exist before it and what it leaves.

- Needed when a metric's grain entity or an input concept is not in the registry, or not active.
- Why it comes before the directory: `POST /api/metric-directory/members/from-spec` refuses a member whose concepts are absent or not active (400, `metric-directory.service.ts:976-987`), and a group's grain entity must have an active version (`:957-967`).
- It leaves: the entity, concept or characteristic active, one panel record per run, and certification records naming who authorized each write and why.
- A clean panel approval of an entity or business concept is active at once; a characteristic always lands in draft and is published separately (step 6).

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run.

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once, before the first step.

### Roles

This section states the roles the task needs.

- `platform_admin` (the direct makers, the review queue, adopt, set aside) and the literal `operator` (every confirm, including adopt and publication confirm); the panel run and publication take either.
- So the session's sign-in needs both roles (gap G23). Since bc-core 1097 (served) each role must be held literally: there is no administrator pass (gap G13, guide 1).

### Environment

This section states where the task runs.

- Development only; bc-core on 3100 runs the panel inside itself (DEC-ffee4e). An active `registry` framework policy must exist, or every maker and confirm refuses.
- No business concepts door has a dry run at the served head (gap G10).

### The model

This section states where the model of a business concept is written; this chapter is the procedure that admits one.

- [Business Concept Registry](../implementation/business-concept-registry.md): what an entity, a business concept and a characteristic are.
- This chapter replaces the earlier "Business Concept Authoring (BCF)" chapter under the same file id; its history is in git.

**Next:** Chapter 3, Onboard a business concept.

## Chapter 3. Onboard a business concept

This chapter describes the steps of the task, in order. Steps 2, 4, 5 and 6 write the shared registry and need a desk grant.

> **Important.** Every confirm records a certification with its reason verbatim. Write 40 characters or more of real reason; padding is refused after trimming.

### Steps

#### Step 1. Check what already exists

Find out whether the entity, business concept or characteristic already exists and is active.

**Actor:** any platform-scoped sign-in (no role on the read doors, `registry-read.controller.ts:46-160`). **Grant:** free (read).

**Inputs:** A name, or an entity id.

- **CLI (planned):** `bc concept find --entity-name <text>`, `bc concept find --characteristic <text>`, `bc concept show <concept-id>`. Trial: not needed (read only)
- **API (today):** `GET /api/bcf/registry/entities?q=<text>` (`concept-registry/registry-read.controller.ts:53`; active only unless `includeAllStates`); `GET /api/bcf/registry/entities/:entityId` (`:59`) and `.../:entityId/concepts` (`:70`); `GET /api/bcf/registry/concepts/:conceptId` (`:95`, active only); `GET /api/bcf/registry/characteristics?q=<text>` (`:133`).
- **Writes:** nothing (read only)
- **Failure modes:** 404 "Entity … not found"; 404 "Active concept … not found" (a draft concept answers 404 here).; 400 on any query field the door does not declare (the global pipe refuses unknown fields).
- **Note:** The concept list has no name search: list the entity's concepts and match the characteristic term.
- **Note:** When everything the metric names exists and is active, stop here: nothing is onboarded (guide 1, step 3).
- **Next:** step 2

#### Step 2. Run the authoring panel

Run the business concepts authoring panel on one candidate (entity, business concept, reference concept or characteristic).

**Actor:** `platform_admin` or `operator` (`registry/bcf/panel/registry-authoring-run.controller.ts:28`). **Grant:** desk grant (a clean approval writes the registry and, for an entity or a business concept, activates it in the same call).

**Inputs:** An active registry framework policy; for a concept, its home entity (and for a reference concept the target entity); evidence (a source label and the cited text). About 35 to 90 seconds; do not restart bc-core while a run is in flight.

- **CLI (planned):** `bc concept author --op <createEntity|createBusinessConcept|createReferenceConcept|createCharacteristic> --name <text> --definition <text> --function <code> [--entity <id>] --evidence-source <text> --evidence-text <text>`. Trial: none (no dry run on any business concepts door at the served head)
- **API (today):** `POST /api/bcf/registry-authoring-runs` (`registry-authoring-run.controller.ts:29`, HTTP 200). Body: `operation`, `candidateRef`, `businessFunctionCode`, `proposedName`, `definition`, `candidateEvidence` (`sourceLabel`, `citedText`); `targetEntityId` for the two concept operations; `referenceTargetEntityId`, `referenceRole`, `identityRole` for a reference concept.
- **Writes:** always `bcf.panel_output_record`; on a clean approval also `bcf.certification_record` and the registry rows (`concept_registry.entity` or `business_concept` and their versions), then the move to active. A characteristic is high risk: only the panel row is written and the answer is `awaiting_operator_confirm`.
- **Failure modes:** 400 `bcf_precheck_duplicate_concept`, `bcf_precheck_duplicate_characteristic` (it already exists).; 400 "`<op>` requires targetEntityId" and the reference-concept field refusals.; 409 "F3 name conflict"; 422 identity cycle; 422 unverified certification.; 503 "no active registry framework_policy"; 503 `registry authoring panel (in-process) failed` (a vendor or seat outage: nothing reached the registry).
- **Note:** The answer's `kind` says what comes next: `authored` (done, active: go to step 7); `authored_activation_pending` (step 6); `awaiting_operator_confirm` (step 5); `parked` (step 4); `not_issued` (read the reason).
- **Note:** The direct maker, with no AI, writes only a recommendation that step 5 confirms: `POST /api/bcf/registry/concepts/authoring-recommendations` and `POST /api/bcf/registry/characteristics/admission-recommendations` (role `platform_admin`; rationale of at least 40 characters). It is the route for identity-bearing value concepts and reference concepts, which the panel does not make (bc-docs onboarding chapter).
- **Next:** step 3

#### Step 3. Read the verdict

Read the panel's verdict and its evidence.

**Actor:** any platform-scoped sign-in (no role on the read doors, `registry-read.controller.ts:46-160`). **Grant:** free (read).

**Inputs:** The `panelRunUid` from step 2.

- **CLI (planned):** `bc concept run show <panel-run-uid>`. Trial: not needed (read only)
- **API (today):** `GET /api/bcf/registry-panel-runs/:panelRunUid` (`registry/bcf/panel/registry-panel-run-read.controller.ts:32`); the evidence behind a publication: `GET /api/bcf/registry/provenance/publication/:subjectKind/:registryId` (`registry-provenance.controller.ts:40`).
- **Writes:** nothing (read only)
- **Failure modes:** 400 not a uuid; 404 "No panel_output_record resolves panel run …".
- **Next:** step 4

#### Step 4. Review: adopt or set aside

For a run the panel sent to review, adopt the maker's draft or set the run aside, with a written reason.

**Actor:** route `platform_admin` (`registry/bcf/adjudication/panel-operator-adjudication.controller.ts:57, 89, 121`); adopting also needs the literal `operator` role (`framework-approval.service.ts:284-289`). **Grant:** free to read the queue; desk grant to adopt (it records a certification) or to set aside (a write-once mark).

**Inputs:** A run with the verdict OPERATOR_REVIEW; a reason of at least 40 characters after trimming.

- **CLI (planned):** `bc concept review list`, `bc concept adopt --run <uid> --rationale <text>`, `bc concept set-aside --run <uid> --code <code> --note <text>`. Trial: none (no dry run)
- **API (today):** Queue: `GET /api/bcf/review-queue` (`:56`). Adopt: `POST /api/bcf/registry-panel-operator-adjudications` (`:88`), body `panelRunUid`, `adoptRole` (`maker`), `actionCode`, `subjectKind`, `rationale`. Set aside: `POST /api/bcf/registry-panel-runs/:panelRunUid/disposition` (`:120`), body `dispositionCode`, `dispositionNoteText`.
- **Writes:** Adopt: a new `bcf.panel_output_record` and one `bcf.certification_record` (not the registry: step 5 writes it). Set aside: the disposition columns of `bcf.panel_output_record`.
- **Failure modes:** 400 not OPERATOR_REVIEW; 400 the maker's draft missing or not approved; 400 the review reason does not name a maker and checker disagreement; 400 the request does not match the maker's draft.; 400 a reason under 40 characters after trimming; 400 "not found or already disposed — dispositions are write-once".; 403 "BCF C5-HR: only the operator role may confirm a high-risk Registry-shape certification".
- **Note:** Important: an adopted `createEntity` cannot be completed today: step 5 parks it and no door finishes it (gap G25). Author the entity again with a fresh run.
- **Next:** step 5

#### Step 5. Confirm the high-risk act

Confirm a high-risk act: a new characteristic, a direct-maker recommendation or an adoption.

**Actor:** `operator` only (`registry/bcf/panel/registry-shape-certification-confirm.controller.ts:39`, checked again in `framework-approval.service.ts:284-289`). **Grant:** desk grant (a certification and a registry write).

**Inputs:** The `panelRunUid` from step 2 (`awaiting_operator_confirm`), the direct maker's answer or step 4's adoption; the run still approved, not quarantined; the active registry policy version equal to the run's.

- **CLI (planned):** `bc concept confirm --run <uid> --subject <kind> --action <code> --rationale <text>`. Trial: none (no dry run)
- **API (today):** `POST /api/bcf/registry-shape-certifications/confirm` (`registry-shape-certification-confirm.controller.ts:40`, HTTP 200). Body: `panelRunUid`, `subjectKind` (for example `characteristic`), `actionCode` (for example `registry_author_vocabulary`), `rationale`.
- **Writes:** `bcf.certification_record` (operator-confirmed, the reason kept verbatim), then the registry row: a characteristic (always in draft) or a business concept and its version (activated).
- **Failure modes:** 403 "BCF C5-HR: only the operator role may confirm a high-risk Registry-shape certification".; 400 "BCF C5-HR: the operator-confirm rationale must be at least 40 characters" (counted after trimming, `framework-approval.service.ts:294-298`).; 400 a subject kind or action code that is not a registry pair; 409 name conflict.; 200 `not_issued` with `panel_record_not_found`, `panel_stage_mismatch`, `grounding_quarantined`, `verdict_not_approved`, `policy_version_mismatch` (run the panel again), `registry_policy_not_found`.
- **Next:** step 6

#### Step 6. Publish the draft

Publish a draft: always for a characteristic, and for an entity or concept that step 2 left `authored_activation_pending`.

**Actor:** route `platform_admin` or `operator` (`registry/bcf/panel/registry-publication.controller.ts:34, 47`); the confirm also needs the literal `operator` role. **Grant:** free for the request (it writes nothing); desk grant for the confirm (a certification and the move to active).

**Inputs:** The object in draft, not archived, with its authoring certification; for a characteristic, its meaning final.

- **CLI (planned):** `bc concept publish --subject <entity|business_concept|characteristic> --id <uuid> --rationale <text> [--final]`. Trial: the request (`POST /api/bcf/registry-publications`) is the nearest check: it writes nothing
- **API (today):** Request: `POST /api/bcf/registry-publications`, body `subjectKind`, `registryId`. Confirm: `POST /api/bcf/registry-publications/confirm`, body `subjectKind`, `registryId`, `rationale` (40 characters or more after trimming), `semanticFinalityAffirmed` (`true` required for a characteristic).
- **Writes:** `bcf.certification_record` (draft to active) and the `lifecycle_state` of the entity, business concept or characteristic.
- **Failure modes:** 400 "BCF B10b-S3: confirming a characteristic publication requires semanticFinalityAffirmed=true".; 200 `not_publishable` with `registry_object_not_found`, `object_archived`, `state_not_draft` (already active), `authoring_certification_not_found`.; 403 and 400 as in step 5.
- **Next:** step 7

#### Step 7. Read back

Read back: the entity, concept or characteristic is active, with the certifications behind it.

**Actor:** any platform-scoped sign-in (no role on the read doors, `registry-read.controller.ts:46-160`). **Grant:** free (read).

**Inputs:** Steps 2 to 6.

- **CLI (planned):** `bc concept show <id>`. Trial: not needed (read only)
- **API (today):** The reads of step 1 (`GET /api/bcf/registry/concepts/:conceptId` answers only for an active concept); `GET /api/bcf/registry/provenance/publication/:subjectKind/:registryId`.
- **Writes:** nothing (read only)
- **Failure modes:** 404 when the concept is not active yet.
- **Next:** Back to guide 1, step 3

**Next:** Chapter 4, Troubleshooting, if a step refused.

## Chapter 4. Troubleshooting

This chapter lists the refusals most likely in this task, by code or message, with what to do. Every step lists its full set of failure modes.

| refusal | step | do |
|---|---|---|
| 400 `bcf_precheck_duplicate_concept` or `_characteristic` | 2 | It already exists: use it (step 1). |
| 409 "F3 name conflict" | 2, 5 | The name is live: use the existing one. |
| 503 `registry authoring panel (in-process) failed` | 2 | A vendor or seat outage; nothing reached the registry. Record it and run again later. |
| `parked`, verdict OPERATOR_REVIEW | 2 | Step 4. |
| `awaiting_operator_confirm` | 2 | Step 5 with `characteristic` and `registry_author_vocabulary`. |
| `authored_activation_pending` | 2 | Step 6. |
| 403 "only the operator role may confirm" | 4, 5, 6 | The sign-in lacks the literal `operator` role (G23). |
| 400 rationale "at least 40 characters" | 4, 5, 6 | Write 40 or more characters of real reason. |
| `not_issued` `policy_version_mismatch` | 5, 6 | The policy changed since the run: run the panel again. |
| `parked` after adopting a `createEntity` | 4, 5 | No door completes it (G25): author the entity again. |
| 400 "requires semanticFinalityAffirmed=true" | 6 | Pass `semanticFinalityAffirmed: true` once the meaning is final. |
| A directory member recorded as blocked (`bcf_gap`) | guide 1, step 5 | A concept it names is not active: finish this guide for it. |

**Next:** Chapter 5, Command reference.

## Chapter 5. Command reference

This chapter lists the command of each step (planned: none exists until the tool is built) and the request it makes today. "none" in the trial column means the engine has no dry run for that door at the served head.

| step | command | request | who | approval | trial |
|---|---|---|---|---|---|
| 1 | `bc concept find --entity-name <text>`, `bc concept find --characteristic <text>`, `bc concept show <concept-id>` | `GET /api/bcf/registry/entities?q=<text>` | any platform-scoped sign-in (no role on the read doors, `registry-read.controller.ts:46-160`) | free | not needed (read only) |
| 2 | `bc concept author --op <createEntity\|createBusinessConcept\|createReferenceConcept\|createCharacteristic> --name <text> --definition <text> --function <code> [--entity <id>] --evidence-source <text> --evidence-text <text>` | `POST /api/bcf/registry-authoring-runs` | `platform_admin` or `operator` (`registry/bcf/panel/registry-authoring-run.controller.ts:28`) | desk grant | none (no dry run on any business concepts door at the served head) |
| 3 | `bc concept run show <panel-run-uid>` | `GET /api/bcf/registry-panel-runs/:panelRunUid` | any platform-scoped sign-in (no role on the read doors, `registry-read.controller.ts:46-160`) | free | not needed (read only) |
| 4 | `bc concept review list`, `bc concept adopt --run <uid> --rationale <text>`, `bc concept set-aside --run <uid> --code <code> --note <text>` | Queue: `GET /api/bcf/review-queue` | route `platform_admin` (`registry/bcf/adjudication/panel-operator-adjudication.controller.ts:57, 89, 121`); adopting also needs the literal `operator` role (`framework-approval.service.ts:284-289`) | free to read the queue; desk grant to adopt | none (no dry run) |
| 5 | `bc concept confirm --run <uid> --subject <kind> --action <code> --rationale <text>` | `POST /api/bcf/registry-shape-certifications/confirm` | `operator` only (`registry/bcf/panel/registry-shape-certification-confirm.controller.ts:39`, checked again in `framework-approval.service.ts:284-289`) | desk grant | none (no dry run) |
| 6 | `bc concept publish --subject <entity\|business_concept\|characteristic> --id <uuid> --rationale <text> [--final]` | Request: `POST /api/bcf/registry-publications`, body `subjectKind`, `registryId`. Confirm: `POST /api/bcf/registry-publications/confirm`, body `subjectKind`, `registryId`, `rationale` | route `platform_admin` or `operator` (`registry/bcf/panel/registry-publication.controller.ts:34, 47`); the confirm also needs the literal `operator` role | free for the request | the request (`POST /api/bcf/registry-publications`) is the nearest check |
| 7 | `bc concept show <id>` | The reads of step 1 | any platform-scoped sign-in (no role on the read doors, `registry-read.controller.ts:46-160`) | free | not needed (read only) |

**Next:** Appendix A, Known gaps.

## Appendix A. Known gaps for this task

This appendix lists the gaps found in this task, each with the smallest fix and its kind. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

### G23. The routes and the certificate writer disagree on roles

- **What:** Adopt is `platform_admin` on the route but the service needs the literal `operator`; the confirm is `operator` only; the direct makers are `platform_admin` only.
- **Smallest fix:** State the real rule on the routes (name `operator` on adopt, or both roles).
- **Kind:** engine code (auditor); the sign-in itself is a credential act (owner)

### G24. The DevHub concept search sends a field bc-core refuses

- **What:** `devhub_bcf_search_concept` sends `representationTerm`, which the concept list query does not declare, so bc-core answers 400; there is no name search on concepts.
- **Smallest fix:** Drop the field in DevHub, or add `representationTerm` and `q` to the concept list query.
- **Kind:** DevHub code (normal lane), or engine code (auditor)

### G25. An adopted createEntity cannot be completed

- **What:** After adopt records the certification, the confirm parks `createEntity` (`registry-authoring-orchestrator.service.ts:404-415`); no door finishes it.
- **Smallest fix:** Add the `createEntity` branch, with activation, to the confirm's completion.
- **Kind:** engine code (auditor)

### G26. A mislabelled resume answer

- **What:** A resumed confirm answers `authoredSubject: 'characteristic'` for any subject (`registry-authoring-orchestrator.service.ts:254-261`).
- **Smallest fix:** Take the subject from the certification.
- **Kind:** engine code (auditor)

### G27. Workflows board rows that do not match the code

- **What:** PW065.01 points at the review queue, not the drafts awaiting publication; PW065.07 is marked as needing no approval but is a live certification; PW065.06 and PW005.05 are still parked though the served engine does what they ask.
- **Smallest fix:** Correct those rows on the board.
- **Kind:** DevHub data (normal lane)

### G10. No trial on the business concepts doors (part)

- **What:** No dry run on any writing door in `registry/bcf`, `concept-registry` or `framework-approval` at the served head.
- **Smallest fix:** A rolled-back `dryRun` on the panel run, adopt, confirm and publication confirm.
- **Kind:** engine code (auditor)

### G11. Doors not fully described (part)

- **What:** The business concepts doors have summaries but no roles or refusals in their descriptions; bc-core 1100 described none of them.
- **Smallest fix:** Describe them.
- **Kind:** engine code (auditor)
