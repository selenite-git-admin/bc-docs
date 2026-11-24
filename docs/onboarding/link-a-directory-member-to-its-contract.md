---
id: link-a-directory-member-to-its-contract
order: 53.4
title: "Link a directory member to its contract (realize)"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "Link a directory member to the approved metric contract version that is what it means."
governing_sources:
  - The Contract Grammar
  - The Authority Model
  - The Evaluation Boundaries
governing_adrs:
  - DEC-79b62f (the Foundation gate: the repair locations and the four questions)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Link a directory member to its contract (realize)

*DevGuide · task guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW081 Realize a Directory Member

## Chapter 1. Overview

This chapter describes the one task of this guide and its place in onboarding a metric. A platform operator records which approved or active metric contract version is what a directory member means. Certification refuses a version with no operative realization, so realize is the required link between approve and request certification.

### What the guide covers

This section lists the acts of the task in order.

- Read the candidates (step 1).
- Realize the member (step 2).
- Read back (step 3).

### Where it sits

This section describes when the task is needed, what must exist before it and what it leaves.

- Needed once for every new metric version, after approve and before request certification.
- The order is fixed: realize refuses a draft (`metric-directory.service.ts:2196`), and request certification answers `computable:false` for a version with no realization. So: approve, then realize, then request certification.
- It leaves: one operative realization for the member. The record is append-only.

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run.

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once, before the first step.

### Roles

This section states the roles the task needs.

- `operator` or `platform_admin` (`metric-directory.controller.ts:180`). Since bc-core 1097 (served) each role must be held literally: there is no administrator pass (gap G13, guide 1).

### Environment

This section states where the task runs.

- Development only. No door of this task has a dry run (gap G10).

> **Note.** The order approve, realize, request certification is proven on a restore by bc-core PR 1100 (served since 2026-11-24 in 83b37959): `src/registry/mcf/__tests__/g1-approve-realize-request-order.restore.integration.spec.ts` takes a fresh draft to audit pending through the separate doors and shows a draft refused at realize and at request certification. It calls the controller handlers directly inside one program (not over HTTP) and does not reach certify (gap G1).

**Next:** Chapter 3, Link a directory member to its contract (realize).

## Chapter 3. Link a directory member to its contract (realize)

This chapter describes the steps of the task, in order. Step 2 is a live write and needs a desk grant.

> **Important.** Do not use the composed advance for a new version: it refuses a version with no realization before it approves (`metric-audit-workflow.service.ts:409-413`), and it is a command-line program only, with no HTTP door.

### Steps

#### Step 1. Read the candidates

Read the realization candidates of the member: the contract versions that carry its uid, with their state.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** free (read).

**Inputs:** The member uid; the version approved (task guide D (Author and approve a metric contract), step 6).

- **CLI (planned):** `bc directory candidates --member <uid>`. Trial: not needed (read only)
- **API (today):** `GET /api/metric-directory/members/:memberUid/realization-candidates` (`metric-directory.controller.ts:839`). Each row: `metric_contract_version_uid`, `governance_state_code`, `realizable` (approved or active), `is_operative`.
- **Writes:** nothing (read only)
- **Failure modes:** None: an unknown member answers an empty list.
- **Note:** An empty list means the proposal carried no `directory_member_uid` (task guide D, step 1).
- **Next:** step 2

#### Step 2. Realize the member

Realize the member: tie its current member version to the exact approved contract version.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** desk grant (live write).

**Inputs:** Step 1 shows the version `realizable`. The member's grain and family placement agree with the contract.

- **CLI (planned):** `bc directory realize --member <uid> --version <mcv-uid> --authority <ref> --rationale <text>`. Trial: none (no dry run on this door)
- **API (today):** `PATCH /api/metric-directory/members/:memberUid/realize` (`metric-directory.controller.ts:687`, HTTP 200). Body: `metric_contract_version_uid` (the exact version), `authority_ref`, `rationale`; optional `metric_contract_uid` as a cross-check.
- **Writes:** `metric_directory.realization_event` (`realization.service.ts:96`); the operative pointer `metric_directory.realization_operative` is kept by a database trigger.
- **Failure modes:** 400 "MCV … state '…' is not realizable (needs approved|active)" (`metric-directory.service.ts:2196`): approve first.; 400 the required fields; 404 "member … not found"; 400 "has no current Member Version"; 400 version not found or its contract archived; 400 cross-check mismatch.; 409 with the database message for a trigger refusal (grain mismatch, state not assertable, one operative realization per member) (`:1897-1899`).; `realization_classification_mismatch` when the version's function and subfunction differ from the member's family: not mapped to a status.
- **Next:** step 3

#### Step 3. Read back

Read back that the member is realized by the version.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** free (read).

**Inputs:** Step 2.

- **CLI (planned):** `bc directory candidates --member <uid>`. Trial: not needed (read only)
- **API (today):** Step 1's read (`is_operative` true); `GET /api/metric-directory/members/realized` (`metric-directory.controller.ts:523`).
- **Writes:** nothing (read only)
- **Failure modes:** None.
- **Note:** A wrong link is never edited: withdraw it with `PATCH /api/metric-directory/members/:memberUid/realization/revoke` (`metric-directory.controller.ts:762`) or replace it with `PATCH …/realization/supersede` (`metric-directory.controller.ts:741`), both with `authority_ref` and `rationale` and a desk grant.
- **Note:** Important: nothing stops revoking the realization of a version that is already audit pending; certify then refuses `c5_no_operative_realization` (gap G31).
- **Next:** Back to guide 1, step 7

**Next:** Chapter 4, Troubleshooting, if a step refused.

## Chapter 4. Troubleshooting

This chapter lists the refusals most likely in this task, by code or message, with what to do. Every step lists its full set of failure modes.

| refusal | step | do |
|---|---|---|
| 400 "… state 'draft' is not realizable (needs approved\|active)" | 2 | Approve first (task guide D, step 6). |
| Candidate list empty | 1 | The proposal carried no member uid; read the proposal. |
| 400 "has no current Member Version" | 2 | The member has no version (task guide C). |
| 409 "grain mismatch" or "state … not assertable" | 2 | The member's grain differs from the contract's, or the state is wrong. |
| `realization_classification_mismatch` | 2 | The version's function and subfunction differ from the member's family. |
| Composed advance: "the MCV has no operative realization" | chapter 3 | Use the separate doors: realize, then request certification. |

**Next:** Chapter 5, Command reference.

## Chapter 5. Command reference

This chapter lists the command of each step (planned: none exists until the tool is built) and the request it makes today. "none" in the trial column means the engine has no dry run for that door at the served head.

| step | command | request | who | approval | trial |
|---|---|---|---|---|---|
| 1 | `bc directory candidates --member <uid>` | `GET /api/metric-directory/members/:memberUid/realization-candidates` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | free | not needed (read only) |
| 2 | `bc directory realize --member <uid> --version <mcv-uid> --authority <ref> --rationale <text>` | `PATCH /api/metric-directory/members/:memberUid/realize` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | desk grant | none (no dry run on this door) |
| 3 | `bc directory candidates --member <uid>` | Step 1's read | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | free | not needed (read only) |

**Next:** Appendix A, Known gaps.

## Appendix A. Known gaps for this task

This appendix lists the gaps found in this task, each with the smallest fix and its kind. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

### G1. The circular order (approve before realize) (closed)

- **What:** The composed advance refuses before approving when the version has no realization, while realize needs an approved version. Answered by bc-core PR 1100, now served (83b37959): on a restore, approve, then realize, then request certification takes a fresh draft to audit pending through the separate doors. The proof is gated and does not run in CI.
- **Smallest fix:** Done for the engine: keep the restore proof as the guard of the order. The tool calls the three doors in that order and never the composed advance.
- **Kind:** none left (record only); the tool calls the three doors in order

### G31. Revoking a realization of a version in audit is not stopped

- **What:** No bc-core check refuses revoking the realization of an audit-pending version (none found); certify then refuses `c5_no_operative_realization`.
- **Smallest fix:** Refuse the revoke, or state it on the door.
- **Kind:** engine code (auditor)

### G10. No trial on realize (part)

- **What:** No dry run on realize, revoke or supersede at the served head.
- **Smallest fix:** A rolled-back `dryRun` through the realization writer.
- **Kind:** engine code (auditor)

### G11. Doors not fully described (part)

- **What:** Realize is described (bc-core 1100); revoke, supersede, the candidates and realized reads stay undescribed; `realization_classification_mismatch` has no status.
- **Smallest fix:** Describe them; map the refusal to 409 or 422.
- **Kind:** engine code (auditor)
