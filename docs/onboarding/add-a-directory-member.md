---
id: add-a-directory-member
order: 53.2
title: "Add a directory member"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "Register one metric's directory member and its first member version, the entry a metric proposal starts from."
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

# Add a directory member

*DevGuide · task guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW008 Register Metrics in the Directory

## Chapter 1. Overview

This chapter describes the one task of this guide and its place in onboarding a metric. A directory member is one metric as the directory states it: its group, code and name, what it measures, and its first member version (definition, formula intent, temporal and output intent, decision evidence, inputs).

### What the guide covers

This section lists the acts of the task in order.

- Read the existing members (step 1).
- Register the member from its specification (step 2).
- Read it back (step 3).

### Where it sits

This section describes when the task is needed, what must exist before it and what it leaves.

- Needed once for every new metric; after the bc-db 0079 reset there are no members, so every metric starts here.
- Before it: a group with a current group version (task guide B (Add a directory family and group)) and every business concept the member names, active (task guide A (Onboard a business concept)).
- It leaves: a member with a v1 member version, not yet linked to any contract. The proposal of task guide D (Author and approve a metric contract) starts from it.

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run.

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once, before the first step.

### Roles

This section states the roles the task needs.

- `operator` or `platform_admin` (`metric-directory.controller.ts:180`). Since bc-core 1097 (served) each role must be held literally: there is no administrator pass (gap G13, guide 1).

### Environment

This section states where the task runs.

- Development only, platform scope. No door of this task has a dry run (gap G10).

### What must exist

This section lists what must exist first and the read that shows it.

- The group, with a current group version (task guide B, step 2).
- The grain entity and each concept named, active with an active version: `devhub_bcf_read_entity`, `devhub_bcf_read_concept`, or the registry reads of task guide A, step 1.

### How to write the definition

This section states the writing rule for the two text fields of a member version (owner ruling, 2026-11-24, DECISIONS content ca0514a1).

- **`definition_text`** is plain business language, two or three sentences, for a reader who knows the business and not the platform. Say what is counted or measured, what is left out, and which date places it in a period. Use no codes, concept ids, function names or operators.
- **`formula_intent_text`** holds the exact technical rule: the operation and its operand, the grain, every filter with its concept and governed value, the counting basis (for example row count, not count distinct), and the temporal shape and anchor.
- Every rule in the definition must also be in the formula intent, and the two must not disagree. The definition says the rule in words; the formula intent says it exactly.
- Both fields are frozen into the member version. A changed definition is a new member version, never an edit (gap G19: today no door writes it).

Example, customer invoice volume:

- *definition_text:* "The number of customer invoices posted in the period. Each invoice counts once. Customer payments and credit notes are not counted. The period is taken from the invoice's posting date."
- *formula_intent_text:* "count(temporal_anchor) over Customer Invoice where document type code = customer_invoice; one row per invoice document (row count, not count distinct); period_aggregate by fiscal period of the posting date".

**Next:** Chapter 3, Add a directory member.

## Chapter 3. Add a directory member

This chapter describes the steps of the task, in order. Step 2 is a live write and needs a desk grant.

### Steps

#### Step 1. Read the existing members

Read the existing members, to avoid a duplicate code.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** free (read).

**Inputs:** Nothing.

- **CLI (planned):** `bc directory member list [--group <id>]` and `bc directory member show <uid>`. Trial: not needed (read only)
- **API (today):** `GET /api/metric-directory/members/lenses` (`metric-directory.controller.ts:529`); `GET /api/metric-directory/members?groupId=<id>` (`:517`); `GET /api/metric-directory/members/:memberUid/detail` (`:604`).
- **Writes:** nothing (read only)
- **Failure modes:** 403 without one of the two roles.; The detail of an unknown member answers HTTP 200 with null, not 404.
- **Note:** bc-db 0079 deleted every member on 2026-11-24, so today the lists are empty and every metric starts with a new member; the codes of the deleted members are free again.
- **Next:** step 2

#### Step 2. Register the member from its specification

Register the member and its first member version from its specification.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** desk grant (live write).

**Inputs:** A group with a current group version and a family with a current family version (task guide B (Add a directory family and group), step 2); the group's grain entity active with an active version; every business concept named (the measure, each discriminator) active with an active version (task guide A (Onboard a business concept)).

- **CLI (planned):** `bc directory member add --group <id> --code <code> --name <text> --from-spec <file>`. Trial: none (no dry run on this door)
- **API (today):** `POST /api/metric-directory/members/from-spec` (`metric-directory.controller.ts:386`, HTTP 201), the door the Workflows board names. Body: `group_id`, `member_code`, `display_name`, `definition_text`, `formula_intent_text`, `temporal_intent` (object), `output_intent` (object), `decision_evidence_refs` (non-empty list) required; `measure_concept_id`, `representation_code` (default `amount`), `discriminator_predicates` (list of `concept_id`, `values`, `operator_code` `eq` only) optional. The class and grain come from the group.
- **Writes:** `metric_directory.member` (with its feasibility state), `metric_directory.member_version` and its child tables (direct inputs, constants, discriminators, dependencies) (`member-versioning.service.ts:225-270`), in one transaction.
- **Failure modes:** 400 for each missing or malformed field (for example "definition_text and formula_intent_text are required non-empty strings", "temporal_intent must be a JSON object").; 400 "group … has no current Group Version — author one before creating members" (`metric-directory.service.ts:1052`); 400 the family has no current version (`:1053`).; 400 "group …'s grain entity … has no ACTIVE, non-archived version — it is not authoring-ready"; 400 "concept(s) absent or not active (no version to reference)".; 400 "operator_code '…' is not permitted — Directory §6 discriminators are select-only".; 409 "an active member already exists for (group, member_code)".; A failure of the commit-time checks of the version rolls everything back and is not mapped to a status.
- **Note:** Write `definition_text` and `formula_intent_text` by the rule in Chapter 2, How to write the definition.
- **Note:** The lower door `POST /api/metric-directory/members` (`metric-directory.controller.ts:356`) takes the whole member version written by hand (direct inputs, constants, dependencies). It refuses `realized_metric_contract_uid` ("no longer accepted at member creation"); `from-spec` ignores that field. A member is linked to its contract later (task guide E (Link a directory member to its contract)).
- **Note:** Important: a member whose concepts are not ready is not refused: it is recorded as blocked (`bcf_gap`) and the door answers 201. Read the answer's feasibility state; a blocked member cannot go on until the concept is onboarded and the member re-checked (`POST /api/metric-directory/members/:memberUid/feasibility-reeval`, `metric-directory.controller.ts:798`).
- **Next:** step 3

#### Step 3. Read the member back

Read the member back: its version, its inputs and its feasibility state.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** free (read).

**Inputs:** Step 2 (the member uid in the answer).

- **CLI (planned):** `bc directory member show <uid>`. Trial: not needed (read only)
- **API (today):** `GET /api/metric-directory/members/:memberUid/detail` (`metric-directory.controller.ts:604`; view `metric_directory.v_member_knowledge`).
- **Writes:** nothing (read only)
- **Failure modes:** HTTP 200 with null for an unknown member.
- **Note:** No door adds a second member version to a member that has one: `POST /api/metric-directory/members/:memberUid/version` (`metric-directory.controller.ts:651`) authors an absent v1 only and refuses "already has a current Member Version" (gap G19). A changed meaning is a new member today.
- **Note:** The derivation check `validateDerivation` (`metric-directory.service.ts:2204`) runs only from `PATCH members/:memberUid/derivation`, which refuses (409) every member that already has a version, so it is not reached for a new member (gap G20).
- **Next:** Back to guide 1, step 5

**Next:** Chapter 4, Troubleshooting, if a step refused.

## Chapter 4. Troubleshooting

This chapter lists the refusals most likely in this task, by code or message, with what to do. Every step lists its full set of failure modes.

| refusal | step | do |
|---|---|---|
| 400 "has no current Group Version" | 2 | Author the group version (task guide B, step 2); 29 live groups need it. |
| 400 "concept(s) absent or not active" | 2 | Onboard or activate the concept (task guide A), then register. |
| 400 "grain entity … has no ACTIVE, non-archived version" | 2 | The grain entity is not ready in the registry (task guide A). |
| 201 with the member blocked (`bcf_gap`) | 2 | Onboard the missing concept, then ask for the re-check (`feasibility-reeval`). |
| 400 "operator_code … not permitted" | 2 | Use `eq` or leave the field out. |
| 409 "an active member already exists" | 2 | Read that member (step 1) and use it. |
| 400 "realized_metric_contract_uid is no longer accepted" | 2 | Leave the field out; the member is linked to its contract later (task guide E). |
| 400 "already has a current Member Version" | 3 | No door adds a second member version (G19). |

**Next:** Chapter 5, Command reference.

## Chapter 5. Command reference

This chapter lists the command of each step (planned: none exists until the tool is built) and the request it makes today. "none" in the trial column means the engine has no dry run for that door at the served head.

| step | command | request | who | approval | trial |
|---|---|---|---|---|---|
| 1 | `bc directory member list [--group <id>]` and `bc directory member show <uid>` | `GET /api/metric-directory/members/lenses` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | free | not needed (read only) |
| 2 | `bc directory member add --group <id> --code <code> --name <text> --from-spec <file>` | `POST /api/metric-directory/members/from-spec` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | desk grant | none (no dry run on this door) |
| 3 | `bc directory member show <uid>` | `GET /api/metric-directory/members/:memberUid/detail` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | free | not needed (read only) |

**Next:** Appendix A, Known gaps.

## Appendix A. Known gaps for this task

This appendix lists the gaps found in this task, each with the smallest fix and its kind. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

### G19. No door adds a second member version

- **What:** `POST members/:memberUid/version` authors an absent v1 only (`metric-directory.service.ts:1996`); no door records a successor version of a member, so a changed meaning cannot be recorded on the same member.
- **Smallest fix:** A successor-version door that supersedes the current member version.
- **Kind:** engine code (auditor); a database change if the version table needs one (owner's yes; not established)

### G20. The derivation check is not reached for a new member

- **What:** `validateDerivation` (`metric-directory.service.ts:2204`) runs only from `PATCH members/:memberUid/derivation`, which refuses every member with a version (409); it checks concepts as not archived, not as active. Guide 1 said every input is checked as active with no cycle: wrong for the create doors.
- **Smallest fix:** Run the same check on the version's inputs and dependencies at creation.
- **Kind:** engine code (auditor)

### G21. Two member doors that check differently

- **What:** `from-spec` checks that concepts are active and ignores a stray `realized_metric_contract_uid`; the plain door refuses that field but does not check the concepts inside `version.direct_inputs` and `version.discriminators`.
- **Smallest fix:** One rule on both doors.
- **Kind:** engine code (auditor)

### G10. No trial on the directory doors (part)

- **What:** No dry run on the member doors at the served head.
- **Smallest fix:** A rolled-back `dryRun` that also runs the commit-time checks.
- **Kind:** engine code (auditor)

### G11. Doors not fully described (part)

- **What:** The plain member door and the detail read are described (bc-core 1100); `from-spec` (the intended door), the version door, the derivation door and the lens reads stay undescribed.
- **Smallest fix:** Describe them.
- **Kind:** engine code (auditor)
