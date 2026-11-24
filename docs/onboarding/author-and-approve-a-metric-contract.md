---
id: author-and-approve-a-metric-contract
order: 53.3
title: "Author and approve a metric contract"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "Turn one directory member into an approved metric contract version: proposal, panel, draft, approval."
governing_sources:
  - The Contract Grammar
  - The Authority Model
  - The Evaluation Boundaries
governing_adrs:
  - DEC-79b62f (the Foundation gate: the repair locations and the four questions)
  - DEC-89db41 (the old metric corpus is input only; nothing in it carries trust into a new metric)
  - DEC-fa9424 (referenced by the authoring procedure)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Author and approve a metric contract

*DevGuide · task guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW103 Propose a Metric, PW027 Draft a Metric, PW084 Review a Metric Draft

## Chapter 1. Overview

This chapter describes the one task of this guide and its place in onboarding a metric. A metric author turns one directory member into a proposal; the authoring panel (maker, checker, judge) drafts a contract from it; a metric publisher records the reviewed draft as a contract version and approves it.

### What the guide covers

This section lists the acts of the task in order.

- Record the proposal (step 1).
- Check before spending (step 2).
- Run the panel (step 3).
- Read the verdict and check the draft (step 4).
- Record the draft (step 5).
- Approve the version (step 6).

### Where it sits

This section describes when the task is needed, what must exist before it and what it leaves.

- Needed once for every new metric, after its directory member exists (task guide C (Add a directory member)).
- Nothing from the old corpus carries trust into the new contract (DEC-89db41): the seed and old content only fill the candidate.
- It leaves: an approved contract version with a frozen package, not yet linked to its member (task guide E (Link a directory member to its contract)) and not yet sent to certification.

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run.

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once, before the first step.

### Roles

This section states the roles the task needs.

- `mcf_author` (steps 1 to 4) and `mcf_publisher` (steps 5 and 6). Since bc-core 1097 (served) each role must be held literally: there is no administrator pass (gap G13, guide 1).

### Environment

This section states where the task runs.

- Development only. The paid panel calls real vendors; the roster is locked by calibration and changing a model needs the operator's sign-off.

### What must exist

This section lists what must exist first and the read that shows it.

- The directory member with a current member version: `GET /api/metric-directory/members/:memberUid/detail`.
- Optionally, the maker envelope the directory would give: `GET /api/metric-directory/members/:memberUid/envelope` (`metric-directory.controller.ts:845`, `operator` or `platform_admin`).

**Next:** Chapter 3, Author and approve a metric contract.

## Chapter 3. Author and approve a metric contract

This chapter describes the steps of the task, in order. Steps 1 to 5 are free draft acts; step 6 is a live write.

> **Important.** Approve has no trial (gap G10). The first real approve is the owner's.

### Steps

#### Step 1. Record the proposal

Record the metric proposal from the directory member.

**Actor:** metric author (`mcf_author`, `registry/mcf/mcf-intake.controller.ts:46`). **Grant:** free (draft act).

**Inputs:** The directory member uid (task guide C (Add a directory member)); the candidate name, description and normalized candidate filled from the seed and old content (guide 1, steps 1 and 2).

- **CLI (planned):** `bc metric propose --member <uid> --name <text> --description <text> --candidate <file>`. Trial: none (no dry run on this door)
- **API (today):** `POST /api/mcf/intakes` (`mcf-intake.controller.ts:45`, HTTP 201). Body: `candidate_name`, `candidate_description_text`, `normalized_candidate_json` (no `co_bindings`), `directory_member_uid`; optional `reservoir_confidence_band`, `reservoir_provenance_source_json`. Answer: `intake_queue_uid`.
- **Writes:** `mcf.metric_authoring_intake_queue` (the member uid is kept with the proposal and stamped on the contract at step 5).
- **Failure modes:** 422 "intake rejected by reservoir filters" with the summary.; 400 body validation; 403 role.; 410 Gone on `POST /api/mcf/intakes/from-seed`: starting from a seed alone is retired (DEC-fa9424).
- **Note:** Important: the door does not reuse a proposal: every request makes a new one (`operator-direct-adapter.ts:40`), and it does not check that the member exists (gap G22). Read `GET /api/mcf/intakes` first; turn an extra one away with `PATCH /api/mcf/intakes/:intakeQueueUid/reject` (a reason of 20 or more characters).
- **Next:** step 2

#### Step 2. Check before spending

Check, before any vendor is paid, every refusal the panel run would meet.

**Actor:** metric author (`mcf_author`). **Grant:** free (trial).

**Inputs:** Step 1 (the proposal uid).

- **CLI (planned):** `bc metric author --proposal <uid> --check`. Trial: yes: this step is the trial; it writes nothing and calls no vendor
- **API (today):** `POST /api/commands/run-metric-authoring-panel/check` (`registry/mcf/metric-authoring/metric-panel-run.command.controller.ts:49`, HTTP 200). Body: `intake_queue_uid`, `maker_source` (`paid` or `supplied`), optional `allow_retry`, `supplied_maker`. Read `allowed` and `refusals` in the answer.
- **Writes:** nothing
- **Failure modes:** Named refusals inside the 200 answer: `intake_not_found`, `intake_status_conflict`, `panel_retry_refused`, `duplicate_proposal_in_flight`, `seat_not_buildable`, `vendor_diversity_violated`, and the supplied-maker shape refusals.; 400 validation; 403 role.
- **Note:** For a maker written by the session (`supplied`), `POST /api/mcf/authoring/validate-envelope` (`mcf-authoring-validate.controller.ts:47`, `mcf_author`) checks the envelope itself and answers `eligible`, `blockers`, `advisories`.
- **Next:** step 3

#### Step 3. Run the authoring panel

Run the authoring panel once on the proposal: the maker drafts the contract, the checker and the judge review it.

**Actor:** metric author (`mcf_author`). **Grant:** free (draft act; it spends the paid vendor budget on the paid route).

**Inputs:** Step 2 clean. About 30 to 60 seconds per seat; do not restart bc-core while it runs.

- **CLI (planned):** `bc metric author --proposal <uid> [--maker paid|supplied]`. Trial: step 2
- **API (today):** `POST /api/commands/run-metric-authoring-panel/do` (`metric-panel-run.command.controller.ts:70`, HTTP 201), same body as step 2. The plain door is `POST /api/mcf/panel-runs` (`mcf-panel-run.controller.ts:52`, body `intake_queue_uid`).
- **Writes:** `mcf.metric_authoring_panel_run`, `mcf.metric_authoring_panel_transcript`, `bcf.panel_output_record`; the proposal is marked used by the panel.
- **Failure modes:** 409 with the named refusals of step 2.; 502 when a seat cannot be set up (seat, vendor and model named; nothing recorded).; A seat that fails while running is recorded as OPERATOR_REVIEW and the call still answers 201.
- **Next:** step 4

#### Step 4. Read the verdict and check the draft

Read the verdict and ask whether the run can be recorded as a draft.

**Actor:** metric author (`mcf_author`). **Grant:** free (read and trial).

**Inputs:** Step 3 (the panel run uid).

- **CLI (planned):** `bc metric panel-run show <uid>` and `bc metric draft --panel-run <uid> --check`. Trial: yes: the preflight is the trial of step 5
- **API (today):** `GET /api/mcf/panel-runs/:panelRunUid` (`mcf-panel-run.controller.ts:198`; the verdict is APPROVE_FOR_DRAFT, OPERATOR_REVIEW or REJECT_DEFECT); `POST /api/mcf/panel-runs/:panelRunUid/materialization-preflight` (`:216`, HTTP 200; answer `eligible`, `blockers`).
- **Writes:** nothing
- **Failure modes:** 404 "panel_run … not found".; Blockers inside the 200 answer: `panel_run_not_found`, `verdict_is_<v>_not_APPROVE_FOR_DRAFT`, `prior_materialization_exists`, and the fixture, temporal, formula grammar, binding and identity blockers.
- **Next:** step 5

#### Step 5. Record the draft

Record the reviewed draft as a metric contract and its first version, in the draft state.

**Actor:** metric publisher (`mcf_publisher`, `registry/mcf/mcf-materialization.controller.ts:33`). **Grant:** free (draft act).

**Inputs:** Step 4 eligible.

- **CLI (planned):** `bc metric draft --panel-run <uid>`. Trial: step 4 (the preflight)
- **API (today):** `POST /api/mcf/panel-runs/:panelRunUid/materialize` (`mcf-materialization.controller.ts:32`, HTTP 201). Body optional: `note`, `near_duplicate_override`, `supersedes_predecessor`, `declared_metric_contract_uid`, `declared_expectation`. Answer: `metric_contract_uid`, `metric_contract_version_uid`.
- **Writes:** the metric contract and its draft version, `mcf.metric_self_verification_fixture`, the draft certification record, bindings and filters; the proposal marked used.
- **Failure modes:** 409 `materialization_precondition_failed` with the failed check in the message (`mcf-materialization.controller.ts:109-110`).; Not mapped to a status: an unknown proposal, a consensus failing its schema, a failed fixture check, a missing framework policy, a duplicate metric name.
- **Next:** step 6

#### Step 6. Approve the version

Approve the version: the publication checks run and, when all pass, the version goes from draft to approved and its package is frozen.

**Actor:** metric publisher (`mcf_publisher`, `registry/mcf/mcf-publication-eligibility.controller.ts:120`). **Grant:** desk grant (live write; the first real run is the owner's).

**Inputs:** Step 5. The door takes the contract uid and acts on its newest version in draft, review, approved or active (`mcf-read.service.ts:1198-1208`).

- **CLI (planned):** `bc version approve --contract <uid>`. Trial: none: "M13 evaluate dryRun is not implemented" (`metric-publication-eligibility-evaluator.service.ts:466-474`)
- **API (today):** `POST /api/mcf/metric-contracts/:metricContractUid/evaluate-publication-eligibility` (alias `evaluate-pe-mc`) (`mcf-publication-eligibility.controller.ts:119`), no body. Results: `GET /api/mcf/metric-contracts/:metricContractUid/publication-eligibility-status` (`:108`).
- **Writes:** `mcf.metric_publication_eligibility_result`, the certification records and the version's state, the contract's hash seal, `mcf.mcv_package_snapshot`.
- **Failure modes:** 404 "no active metric_contract_version for metric_contract …" (the message says active; the door looks at draft, review, approved and active).; Failing checks leave the version at review, the failing checks named in the answer (not an error status); fix by a new draft, never in place.; Not mapped to a status: a wrong-state or precondition error of the evaluator.
- **Next:** Back to guide 1, step 6

**Next:** Chapter 4, Troubleshooting, if a step refused.

## Chapter 4. Troubleshooting

This chapter lists the refusals most likely in this task, by code or message, with what to do. Every step lists its full set of failure modes.

| refusal | step | do |
|---|---|---|
| 410 "Seed-primary intake creation is retired" | 1 | Propose from the member (`directory_member_uid`). |
| Two proposals for one member | 1 | The door does not reuse; reject the extra one with a reason (G22). |
| 422 "intake rejected by reservoir filters" | 1 | Correct the candidate (confidence, text, no `co_bindings`). |
| `intake_status_conflict`, `duplicate_proposal_in_flight`, `panel_retry_refused` | 2, 3 | Read the latest run; run again only with `allow_retry` where the rule allows. |
| `seat_not_buildable`, `vendor_diversity_violated`, 502 | 2, 3 | A seat or vendor setting: the operator's. |
| `eligible:false` blockers | 4 | Fix the cause; run the panel again (step 3). |
| 409 `materialization_precondition_failed` | 5 | Read the failed check; run the panel again when fixed. |
| Version left at review | 6 | Read the failing checks (`publication-eligibility-status`); make a new draft. |

**Next:** Chapter 5, Command reference.

## Chapter 5. Command reference

This chapter lists the command of each step (planned: none exists until the tool is built) and the request it makes today. "none" in the trial column means the engine has no dry run for that door at the served head.

| step | command | request | who | approval | trial |
|---|---|---|---|---|---|
| 1 | `bc metric propose --member <uid> --name <text> --description <text> --candidate <file>` | `POST /api/mcf/intakes` | metric author (`mcf_author`, `registry/mcf/mcf-intake.controller.ts:46`) | free | none (no dry run on this door) |
| 2 | `bc metric author --proposal <uid> --check` | `POST /api/commands/run-metric-authoring-panel/check` | metric author (`mcf_author`) | free | yes |
| 3 | `bc metric author --proposal <uid> [--maker paid\|supplied]` | `POST /api/commands/run-metric-authoring-panel/do` | metric author (`mcf_author`) | free | step 2 |
| 4 | `bc metric panel-run show <uid>` and `bc metric draft --panel-run <uid> --check` | `GET /api/mcf/panel-runs/:panelRunUid` | metric author (`mcf_author`) | free | yes |
| 5 | `bc metric draft --panel-run <uid>` | `POST /api/mcf/panel-runs/:panelRunUid/materialize` | metric publisher (`mcf_publisher`, `registry/mcf/mcf-materialization.controller.ts:33`) | free | step 4 (the preflight) |
| 6 | `bc version approve --contract <uid>` | `POST /api/mcf/metric-contracts/:metricContractUid/evaluate-publication-eligibility` | metric publisher (`mcf_publisher`, `registry/mcf/mcf-publication-eligibility.controller.ts:120`) | desk grant | none |

**Next:** Appendix A, Known gaps.

## Appendix A. Known gaps for this task

This appendix lists the gaps found in this task, each with the smallest fix and its kind. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

### G22. The proposal door neither reuses nor checks the member

- **What:** `POST /api/mcf/intakes` makes a new proposal on every call and only stores the member uid. Guide 1 said a duplicate returns the existing proposal: wrong for this door.
- **Smallest fix:** Answer with the existing pending proposal for the same member, and refuse an unknown member.
- **Kind:** engine code (auditor)

### G10. No trial on approve (part)

- **What:** Approve has no dry run at the served head; the evaluator refuses one by name.
- **Smallest fix:** A read-only run of the 16 publication checks, or a rolled-back `dryRun` through the evaluator.
- **Kind:** engine code (auditor)

### G11. Doors not fully described (part)

- **What:** The proposal, preflight, draft and approve doors are described (bc-core 1100); `validate-envelope`, the member envelope and the read doors stay undescribed; approve's 404 message says active while it acts on draft to active.
- **Smallest fix:** Describe them; correct the message.
- **Kind:** engine code (auditor)
