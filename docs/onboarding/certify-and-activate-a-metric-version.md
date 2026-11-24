---
id: certify-and-activate-a-metric-version
order: 53.6
title: "Certify and activate a metric version"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "Send an approved, realized version to certification, open a run, record the panel's decision and certify it active."
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

# Certify and activate a metric version

*DevGuide · task guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW026 Certify a Metric

## Chapter 1. Overview

This chapter describes the one task of this guide and its place in onboarding a metric. A metric publisher sends an approved, realized version to certification (it becomes audit pending), opens a certification run on the exact package, lets the certification panel decide, and certifies: the version becomes active. There is no certified state between audit pending and active.

### What the guide covers

This section lists the acts of the task in order.

- Request certification (step 1), then prove on the demo world (task guide F, steps 6 to 13).
- Read the chain status and the eligibility (steps 2 and 3).
- Open a certification run and record the panel's decision (steps 4 and 5).
- Certify and activate (step 6).
- Read back (step 7).

### Where it sits

This section describes when the task is needed, what must exist before it and what it leaves.

- Step 1 is needed after realize (task guide E) and before the demo world's dry evaluation (task guide F, step 5).
- Steps 2 to 7 are needed after the proof is carried over (task guide F, step 12).
- It leaves: an active, current metric contract version in the Metric Catalog, its member realized by it.

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run.

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once, before the first step.

### Roles

This section states the roles the task needs.

- `mcf_publisher`, held literally, for request, run, decision and certify (these doors also check it in the handler).
- `operator` or `platform_admin` for the chain read.

### What must exist

This section lists what must exist first.

- An active framework policy (409 otherwise at request and certify).
- A registered audit roster and a current authority pin (the decision refuses otherwise); the roster is registered with the command `/api/commands/calibrate-certification-roster/…` (`mcf_publisher`; its `do` calls paid vendors): the operator's, not this guide's.

**Next:** Chapter 3, Certify and activate a metric version.

## Chapter 3. Certify and activate a metric version

This chapter describes the steps of the task, in order. Every write of this task is a certification act under a desk grant.

> **Important.** Use the trial (`dryRun: true`) of request certification and certify before each real call. The first real certify is the owner's.

### Steps

#### Step 1. Request certification

Request certification: the version moves from approved to audit pending and is sent to the metric audit.

**Actor:** metric publisher (`mcf_publisher`), held literally (`registry/mcf/mcf-request-audit.controller.ts:104`, checked again at `:112`). **Grant:** desk grant (live write).

**Inputs:** The version approved (task guide D) and realized (task guide E).

- **CLI (planned):** `bc version request-certification --version <mcv-uid> --cohort <code> [--trial]`. Trial: yes: the body field `dryRun` (bc-core 1100)
- **API (today):** `POST /api/mcf/metric-contract-versions/:mcvUid/request-audit` (`mcf-request-audit.controller.ts:103`, HTTP 200). Body: `cohortCode`; optional `rationaleText`, `idempotencyKey`, `dryRun` (boolean; true for a trial).
- **Writes:** `mcf.certification_record`, `metric_audit.request_outbox`, `metric_audit.transition_evidence`, the version's state. On `computable:false` only one `metric_audit.request_preflight_disposition` row; the state does not move.
- **Failure modes:** 403 "mcf_publisher role required for requestAudit"; 400 "cohortCode is required"; 409 "no active mcf framework_policy row".; 409 a lost race or a state no longer approved (a draft surfaces here); 422 the declaration-level lifecycle gate.; **200 with `computable:false`** (`refused_no_operative_realization` or `refused_not_v3_computable`): a refusal: the version did not move. The door description says so; the route still answers 200 (gap G32).
- **Note:** Request certification before the demo world's dry evaluation and proof: they read only an audit-pending version (task guide F, step 5).
- **Next:** Task guide F, step 6 (then step 2 here)

#### Step 2. Read the chain status

Read the version's chain status; certify judges it again in its own act.

**Actor:** operator or platform administrator (`registry/mcf/mcv-chain-status.controller.ts:52`). **Grant:** free (read).

**Inputs:** Step 1 (audit pending).

- **CLI (planned):** `bc chain status --version <mcv-uid>`. Trial: the read is the check
- **API (today):** `GET /api/registry/mcf/chain-status/candidate/:mcvUid` (any state, including audit pending; read-only; answers `basis: 'fresh_judge_candidate'`, `persisted: false`). Totals: `GET /api/registry/mcf/chain-status/summary`.
- **Writes:** nothing (read only)
- **Failure modes:** 400 not a uuid; 404 "judgeCandidate: MCV … not found".
- **Note:** `POST /api/registry/mcf/chain-status/refresh` re-judges active versions only, not an audit-pending one (gap G30); certify re-judges the chain inside its own transaction and refuses unless green.
- **Next:** step 3

#### Step 3. Read certification eligibility

Read on what basis the version can be certified (EXACT, REPRODUCIBLE or NONE).

**Actor:** `mcf_author`, `mcf_publisher` or `platform_admin` (`mcf-reproducibility-reproof.controller.ts:75`). **Grant:** free (read).

**Inputs:** Step 1.

- **CLI (planned):** `bc version eligibility --version <mcv-uid>`. Trial: the read is the check
- **API (today):** `GET /api/mcf/metric-contract-versions/:mcvUid/certification-eligibility` (`mcf-reproducibility-reproof.controller.ts:74`).
- **Writes:** nothing (read only)
- **Failure modes:** NONE is an answer, not a status; an unknown uuid string is a database error not mapped to a status.
- **Next:** step 4

#### Step 4. Open a certification run

Open a certification run bound to the exact package that was assessed.

**Actor:** metric publisher (`mcf_publisher`), held literally (`mcf-reproducibility-reproof.controller.ts:99, 134`). **Grant:** desk grant (certification).

**Inputs:** Step 3 eligible; `packageSnapshotDigest` and `closureRoot` from the answer of step 1; `methodologyDigest` and `gatePolicyVersion` from the current authority pin (`metric_audit.intrinsic_authority_pin`), which no HTTP door reads (gap G28).

- **CLI (planned):** `bc version certification-run open --version <mcv-uid>`. Trial: none (step 3 is the nearest check)
- **API (today):** `POST /api/mcf/metric-contract-versions/:mcvUid/certification-runs` (`mcf-reproducibility-reproof.controller.ts:97`, HTTP 201). Body: `packageSnapshotDigest`, `closureRoot`, `methodologyDigest`, `gatePolicyVersion`.
- **Writes:** `metric_audit.audit_run`, `metric_audit.audit_run_event`.
- **Failure modes:** 403 without the literal role; 422 "<field> is required — a run binds the exact assessed coordinates"; `not_certification_eligible` (not mapped to a status).; The door does not check the version's state (gap G29); the decision does.
- **Next:** step 5

#### Step 5. Record the panel's decision

The certification panel decides on the run.

**Actor:** metric publisher (`mcf_publisher`), held literally (`mcf-certification-panel-decision.controller.ts:46, 88`). **Grant:** desk grant (certification; calls paid vendors).

**Inputs:** Step 4; the version audit pending; a registered audit roster and a current authority pin.

- **CLI (planned):** `bc version certification-run decide --version <mcv-uid> --run <uid> --basis <EXACT_SNAPSHOT|EXACT_REPROOF|REPRODUCIBLE>`. Trial: none
- **API (today):** `POST /api/mcf/metric-contract-versions/:mcvUid/certification-runs/:runUid/panel-decision` (`mcf-certification-panel-decision.controller.ts:44`, HTTP 201). Body: `basis`.
- **Writes:** `metric_audit.decision`, the report rows, the run's completion.
- **Failure modes:** 422 with a code: `subject_not_audit_pending`, `run_not_found`, `run_subject_mismatch`, `run_closed`, `panel_already_attached`, `no_registered_roster`, `no_current_authority_pin`, `basis_not_evidenced`.; 422 "basis is required and must be one of …"; a later governed refusal 422 with `refusalClass`, `stage` and `failedSeat`; any other later failure 500.
- **Next:** step 6

#### Step 6. Certify and activate

Certify and activate: the version goes from audit pending to active. Certified and active are one act.

**Actor:** metric publisher (`mcf_publisher`), held literally (`registry/mcf/mcf-admit.controller.ts:63, 88`). **Grant:** desk grant (certification; the first real run is the owner's).

**Inputs:** A PASS decision (step 5); a current Demoed record of this exact version (task guide F, step 12); the chain green (judged inside the act).

- **CLI (planned):** `bc version certify --version <mcv-uid> [--trial]`. Trial: yes: the body field `dryRun` (bc-core 1100)
- **API (today):** `POST /api/mcf/metric-contract-versions/:mcvUid/admit` (`mcf-admit.controller.ts:62`, HTTP 200). Body optional: `idempotencyKey`, `rationaleText`, `dryRun` (boolean; true for a trial). The old direct activation answers 410 Gone (`mcf-publication-activation.controller.ts:24-39`).
- **Writes:** `mcf.certification_record` (admit), `metric_audit.transition_evidence` citing the decision, the chain and the Demoed record, `mcf.mcv_chain_status`, the version's state to active.
- **Failure modes:** 403 without the literal role; 409 "no active mcf framework_policy row"; 409 a lost race or no longer audit pending.; 422 the lifecycle gate; 422 "no effective decision"; 422 the decision is not PASS; 422 `demoed_absent` or the proof does not read current; 422 the chain "is '<verdict>', not green; cannot activate".; 422 "not intrinsic-decision-ready" with `c5_no_operative_realization` or `c16_not_demoed_or_unbound`.
- **Next:** step 7

#### Step 7. Read back

Read back: the version is active and current, the member is realized by it, and the Demoed record holds.

**Actor:** anyone with the read role of each door. **Grant:** free (read).

**Inputs:** Step 6.

- **CLI (planned):** `bc metric show --member <uid>`. Trial: not needed (read only)
- **API (today):** `GET /api/mcf/metric-contracts/:metricContractUid` (`mcf-publication-eligibility.controller.ts:90`; the version history with `governance_state_code` and `is_current`); `GET /api/metric-directory/members/:memberUid/realization-candidates` (`is_operative`); `GET /api/mcf/metric-contract-versions/:mcvUid/demoed-claim`.
- **Writes:** nothing (read only)
- **Failure modes:** 404 "metric contract … not found".
- **Next:** Back to guide 1, step 11

**Next:** Chapter 4, Troubleshooting, if a step refused.

## Chapter 4. Troubleshooting

This chapter lists the refusals most likely in this task, by code or message, with what to do. Every step lists its full set of failure modes.

| refusal | step | do |
|---|---|---|
| 200 `computable:false`, `refused_no_operative_realization` | 1 | A refusal: realize (task guide E), then request again. |
| 200 `computable:false`, `refused_not_v3_computable` | 1 | Read the reasons; a new draft is needed. |
| 422 "request_audit: … declaration-level gate" | 1 | Read the listed check; fix by a new version. |
| 409 a lost race, state no longer approved | 1 | Read the version's state; do not retry blindly. |
| 409 "no active mcf framework_policy row" | 1, 6 | The operator's: the framework policy. |
| 403 "requires the mcf_publisher role" | 1, 4-6 | The sign-in lacks the literal role (G13). |
| `not_certification_eligible` | 4 | Read step 3's reasons; record the exactness or reproducibility proof first. |
| `subject_not_audit_pending` | 5 | Request certification first (step 1). |
| `no_registered_roster`, `no_current_authority_pin` | 5 | The operator's: calibrate the roster and the pin. |
| 422 "no effective decision", "not PASS" | 6 | Decide (step 5); a non-PASS decision needs a new version. |
| 422 `demoed_absent` or the proof does not read current | 6 | Carry the proof over (task guide F, step 12); read the Demoed record. |
| 422 the chain is not green | 6 | Read step 2's details; fix by a new version. |
| 422 `c5_no_operative_realization` | 6 | The realization was revoked: realize again (task guide E). |
| 410 "Direct activation … is retired" | 6 | Certify with `admit`. |

**Next:** Chapter 5, Command reference.

## Chapter 5. Command reference

This chapter lists the command of each step (planned: none exists until the tool is built) and the request it makes today. "none" in the trial column means the engine has no dry run for that door at the served head.

| step | command | request | who | approval | trial |
|---|---|---|---|---|---|
| 1 | `bc version request-certification --version <mcv-uid> --cohort <code> [--trial]` | `POST /api/mcf/metric-contract-versions/:mcvUid/request-audit` | metric publisher (`mcf_publisher`), held literally (`registry/mcf/mcf-request-audit.controller.ts:104`, checked again at `:112`) | desk grant | yes |
| 2 | `bc chain status --version <mcv-uid>` | `GET /api/registry/mcf/chain-status/candidate/:mcvUid` | operator or platform administrator (`registry/mcf/mcv-chain-status.controller.ts:52`) | free | the read is the check |
| 3 | `bc version eligibility --version <mcv-uid>` | `GET /api/mcf/metric-contract-versions/:mcvUid/certification-eligibility` | `mcf_author`, `mcf_publisher` or `platform_admin` (`mcf-reproducibility-reproof.controller.ts:75`) | free | the read is the check |
| 4 | `bc version certification-run open --version <mcv-uid>` | `POST /api/mcf/metric-contract-versions/:mcvUid/certification-runs` | metric publisher (`mcf_publisher`), held literally (`mcf-reproducibility-reproof.controller.ts:99, 134`) | desk grant | none (step 3 is the nearest check) |
| 5 | `bc version certification-run decide --version <mcv-uid> --run <uid> --basis <EXACT_SNAPSHOT\|EXACT_REPROOF\|REPRODUCIBLE>` | `POST /api/mcf/metric-contract-versions/:mcvUid/certification-runs/:runUid/panel-decision` | metric publisher (`mcf_publisher`), held literally (`mcf-certification-panel-decision.controller.ts:46, 88`) | desk grant | none |
| 6 | `bc version certify --version <mcv-uid> [--trial]` | `POST /api/mcf/metric-contract-versions/:mcvUid/admit` | metric publisher (`mcf_publisher`), held literally (`registry/mcf/mcf-admit.controller.ts:63, 88`) | desk grant | yes |
| 7 | `bc metric show --member <uid>` | `GET /api/mcf/metric-contracts/:metricContractUid` | anyone with the read role of each door | free | not needed (read only) |

**Next:** Appendix A, Known gaps.

## Appendix A. Known gaps for this task

This appendix lists the gaps found in this task, each with the smallest fix and its kind. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

### G32. A refusal of request certification answers 200

- **What:** `computable:false` is still HTTP 200 at the served head; its helper `request-audit-outcome.ts` reads it as a refusal but no route calls it.
- **Smallest fix:** Answer 409 or 422 with the same body, or keep 200 and have the tool read the helper; the owner chooses.
- **Kind:** engine code (auditor)

### G28. No HTTP read of the authority pin

- **What:** Opening a run needs `methodologyDigest` and `gatePolicyVersion` from the current authority pin; no door reads it.
- **Smallest fix:** A read door, or let the open-run door take them from the pin.
- **Kind:** engine code (auditor)

### G29. Opening a run does not check the version's state

- **What:** The open-run door does not refuse a version that is not audit pending; the decision does.
- **Smallest fix:** Refuse unless audit pending.
- **Kind:** engine code (auditor)

### G30. The chain check covers active versions only

- **What:** `POST …/chain-status/refresh` re-judges active versions only; an audit-pending version is read through the candidate door and judged inside certify. The planned `bc chain check` has nothing to check for this task.
- **Smallest fix:** Drop the planned command, or add a check of one candidate; the owner decides.
- **Kind:** owner decision

### G10. No trial on certification (part)

- **What:** Request certification and certify have a `dryRun` since bc-core 1100 (served). Opening a run and the decision have none.
- **Smallest fix:** File the other two.
- **Kind:** engine code (auditor)

### G11. Doors not fully described (part)

- **What:** Request, certify, run, decision, eligibility and the chain doors are described (bc-core 1100); `not_certification_eligible` and evaluator errors have no status.
- **Smallest fix:** Map them to 422.
- **Kind:** engine code (auditor)
