---
id: add-a-directory-family-and-group
order: 53.1
title: "Add a directory family and group"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "Reuse or add the directory family and group a new metric's member is placed in, and author a missing group version."
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

# Add a directory family and group

*DevGuide · task guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW080 Manage Metric Families

## Chapter 1. Overview

This chapter describes the one task of this guide and its place in onboarding a metric. A family is the theme a metric belongs to (function, subfunction, theme). A group sits under a family and fixes the grain (the entity one row of the metric is about), the class (base or derived) and a template. Every directory member is placed in one group.

### What the guide covers

This section lists the acts of the task in order.

- Read the families and groups, and pick one (step 1).
- Check that the group has a current group version, and author it when absent (step 2).
- Add a family only when none fits (step 3).
- Add a group only when none fits (step 4).

### Where it sits

This section describes when the task is needed, what must exist before it and what it leaves.

- Needed when a new metric's member must be placed and no existing group fits, or the chosen group has no current version.
- Before it: the grain entity exists in the business concepts registry (task guide A (Onboard a business concept) when it does not).
- It leaves: a group with a current group version, ready to hold members (task guide C (Add a directory member)).
- Today 49 families and 143 groups exist (bc-db 0079 kept them), so the usual outcome is to reuse and add nothing, after the version check of step 2.

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run.

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once, before the first step.

### Roles

This section states the roles the task needs.

- `operator` or `platform_admin` on every door (`metric-directory.controller.ts:180`); no door has its own role. Since bc-core 1097 (served) each role must be held literally: there is no administrator pass (gap G13, guide 1).

### Environment

This section states where the task runs.

- Development only, on the platform scope (`@PlatformOnly`, `metric-directory.controller.ts:178`): no tenant header.
- No door of this task has a dry run at the served head (gap G10). The read before each write is the only check.

### What must exist

This section lists what must exist first and the read that shows it.

- For a group: its family with a current family version (every family made by step 3 has one), and its grain entity (`devhub_bcf_read_entity`, or the registry read of task guide A).

**Next:** Chapter 3, Add a directory family and group.

## Chapter 3. Add a directory family and group

This chapter describes the steps of the task, in order. Each write is a live write on the shared database and needs a desk grant.

### Steps

#### Step 1. Read the families and groups

Read the families and groups, and pick one if it fits the metric.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** free (read).

**Inputs:** Nothing. A family is identified by function, subfunction and theme; a group within its family by its group code.

- **CLI (planned):** `bc directory family list` and `bc directory group list [--family <id>]`. Trial: not needed (read only)
- **API (today):** `GET /api/metric-directory/families` (`metric-directory.controller.ts:505`, active families only); `GET /api/metric-directory/families/coverage-v2` (`:535`); `GET /api/metric-directory/groups?familyId=<id>` (`:511`).
- **Writes:** nothing (read only)
- **Failure modes:** 403 without one of the two roles.
- **Note:** The bc-db 0079 reset kept every family, group and their versions; it deleted only the members. Reuse is the usual outcome.
- **Next:** step 2

#### Step 2. Check the group's version, author it if absent

Decide whether the chosen group has a current group version; when it has none, author its first version.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** free for the check; desk grant to author the version (live write).

**Inputs:** The group id from step 1. The family has a current family version, the group has a grain entity and the class base or derived.

- **CLI (planned):** `bc directory group version --group <id>`. Trial: none (no dry run on this door)
- **API (today):** `POST /api/metric-directory/groups/:groupId/version` (`metric-directory.controller.ts:677`, HTTP 200, no body; service `authorGroupVersionForExistingGroup`, `metric-directory.service.ts:2120`). The same door for a family: `POST /api/metric-directory/families/:familyId/version` (`metric-directory.controller.ts:667`).
- **Writes:** `metric_directory.group_version` (the missing v1 only, a faithful copy of the group row).
- **Failure modes:** 404 "group … not found or archived".; 409 "group … already has a current Group Version … this surface authors an ABSENT v1 only" (`metric-directory.service.ts:2143`).; 400 "group …'s family has no current Family Version"; 400 class not base or derived; 400 "has no grain_entity_id".
- **Note:** Important: 29 of the 143 live groups have no current group version (read on 2026-11-24). A member cannot be added to such a group: the member door refuses "group … has no current Group Version — author one before creating members" (`metric-directory.service.ts:1052`). Appendix B lists the 29.
- **Note:** The list reads of step 1 do not show whether a group has a current version (gap G18); until a door shows it, the check is a read-only database query of `metric_directory.fn_current_group_version(group_id)`.
- **Next:** step 3

#### Step 3. Add a family

Add a family, only when no family fits.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** desk grant (live write on the shared database).

**Inputs:** A function and subfunction that exist in the master list (`master.master_subfunction`); a theme code not yet used for that pair.

- **CLI (planned):** `bc directory family add --function <slug> --subfunction <slug> --theme <code> [--decision <text>] [--rationale <text>] [--priority now|next|later]`. Trial: none (no dry run on this door)
- **API (today):** `POST /api/metric-directory/families` (`metric-directory.controller.ts:187`, HTTP 201). Body: `function_slug`, `subfunction_slug`, `theme_code` (required); `decision_text`, `rationale_text`, `priority_code` (optional, default `later`).
- **Writes:** `metric_directory.family` and its first `metric_directory.family_version`, in one transaction (`metric-directory.service.ts:685-715`).
- **Failure modes:** 400 "function_slug, subfunction_slug, and theme_code are required non-empty strings".; 400 "family write references an unknown row" (an unknown function and subfunction pair).; 400 "family write violates a constraint" (for example a bad `priority_code`).; 409 "an active family already exists for (function, subfunction, theme)" (`metric-directory.service.ts:2555`).; Any other database failure is not mapped to a status.
- **Next:** step 4

#### Step 4. Add a group

Add a group, only when no group of the family fits.

**Actor:** operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`). **Grant:** desk grant (live write).

**Inputs:** A family with a current family version; the grain entity id (an existing entity; the door does not check that it is active); optionally a date-typed temporal anchor concept.

- **CLI (planned):** `bc directory group add --family <id> --code <code> --class base|derived --grain-entity <id> [--temporal-anchor <concept-id>] --template <file>`. Trial: none (no dry run)
- **API (today):** `POST /api/metric-directory/groups` (`metric-directory.controller.ts:269`, HTTP 201). Body: `family_id`, `group_code`, `class_code`, `template_json` (an object), `grain_entity_id` (required by the service, `metric-directory.service.ts:782`); `temporal_anchor_concept_id` (optional).
- **Writes:** `metric_directory.group` and its first `metric_directory.group_version`, in one transaction (`metric-directory.service.ts:779-815`).
- **Failure modes:** 400 "family_id, group_code, class_code, and template_json (an object) are required".; 400 "grain_entity_id is required — a governed Group Version (v1) is authored at create time" (`:782`).; 400 "family … has no current Family Version" (`:802`).; 400 an unknown family, grain or anchor reference; 400 a constraint (class not base or derived).; 409 "an active group already exists for (family_id, group_code)".
- **Next:** Back to guide 1, step 3

**Next:** Chapter 4, Troubleshooting, if a step refused.

## Chapter 4. Troubleshooting

This chapter lists the refusals most likely in this task, by code or message, with what to do. Every step lists its full set of failure modes.

| refusal | step | do |
|---|---|---|
| 403 | any | The sign-in lacks both roles; only the literal roles pass. |
| 409 "an active family already exists" | 3 | Reuse that family (step 1). |
| 400 "family write references an unknown row" | 3 | The function and subfunction pair is not in the master list; correct the slugs. |
| 400 "grain_entity_id is required" | 4 | Send the grain entity id. |
| 400 "has no current Family Version" | 4 | Author the family version (`POST families/:familyId/version`). |
| 409 "an active group already exists" | 4 | Reuse that group. |
| 400 "has no current Group Version" at the member step | 2 | Author the group version (step 2), then add the member. |

**Next:** Chapter 5, Command reference.

## Chapter 5. Command reference

This chapter lists the command of each step (planned: none exists until the tool is built) and the request it makes today. "none" in the trial column means the engine has no dry run for that door at the served head.

| step | command | request | who | approval | trial |
|---|---|---|---|---|---|
| 1 | `bc directory family list` and `bc directory group list [--family <id>]` | `GET /api/metric-directory/families` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | free | not needed (read only) |
| 2 | `bc directory group version --group <id>` | `POST /api/metric-directory/groups/:groupId/version` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | free for the check; desk grant to author the version | none (no dry run on this door) |
| 3 | `bc directory family add --function <slug> --subfunction <slug> --theme <code> [--decision <text>] [--rationale <text>] [--priority now\|next\|later]` | `POST /api/metric-directory/families` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | desk grant | none (no dry run on this door) |
| 4 | `bc directory group add --family <id> --code <code> --class base\|derived --grain-entity <id> [--temporal-anchor <concept-id>] --template <file>` | `POST /api/metric-directory/groups` | operator or platform administrator (class roles `operator`, `platform_admin`, `metric-directory.controller.ts:180`) | desk grant | none (no dry run) |

**Next:** Appendix A, Known gaps.

## Appendix A. Known gaps for this task

This appendix lists the gaps found in this task, each with the smallest fix and its kind. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

### G17. 29 kept groups have no current group version

- **What:** 29 of the 143 live groups have no current group version (read on 2026-11-24); a member cannot be added to any of them (`metric-directory.service.ts:1052`). Each meets the door's checks (family version, grain entity, class base or derived).
- **Smallest fix:** Author the v1 of a group through step 2 when a metric needs that group, or of all 29 in one batch; the owner decides which.
- **Kind:** desk grant (live writes); owner decision on the batch

### G18. The list reads do not show a group's version

- **What:** `GET families`, `GET groups` and `coverage-v2` do not say whether a current version exists, so step 1 cannot see G17.
- **Smallest fix:** Add the current version (or a flag) to the list answers.
- **Kind:** engine code (auditor)

### G10. No trial on the directory doors (part)

- **What:** No dry run on the family, group or group-version doors at the served head.
- **Smallest fix:** A `dryRun` that runs the transaction and rolls it back, as PR 1100 does for request certification and certify.
- **Kind:** engine code (auditor)

### G11. Doors not fully described (part)

- **What:** `POST families` and `POST groups` are described (roles, refusals, body; bc-core 1100); the version doors and the list reads stay undescribed.
- **Smallest fix:** Describe them.
- **Kind:** engine code (auditor)

## Appendix B. The 29 groups with no current group version

This appendix lists the 29 live groups that had no current group version when read on 2026-11-24 (a read-only database read of `metric_directory."group"` where `metric_directory.fn_current_group_version(group_id)` is null). Each has a family with a current version, a grain entity and the class base or derived, so step 2 of chapter 3 would accept it. A group leaves this list when its version is authored; read again before relying on it.

| function | subfunction | theme | group_code | class | group_id |
|---|---|---|---|---|---|
| finance | accounts_payable | ap_payment_and_dpo | `ap_discount_capture` | derived | `39357b0b-55b3-47e9-9d5c-9e6ec6b0117d` |
| finance | cost_accounting | cost_center_and_classification | `cost_line_amounts` | base | `f5036967-19db-4953-9c10-328711c9f932` |
| finance | cost_accounting | cost_center_and_classification | `cost_line_classification` | base | `559c5aed-73e8-4147-9c3d-24eb30e00a42` |
| finance | cost_accounting | cost_center_and_classification | `cost_structure_ratios` | derived | `5dc520f1-b710-41c9-951e-8912074e9863` |
| finance | cost_accounting | product_costing | `product_cost_variance_ratios` | derived | `58735f98-c2cd-42fb-957a-7012e04b5f69` |
| finance | fixed_assets | asset_value_and_depreciation | `asset_impairment_amounts` | base | `d6cbd40f-8409-42e2-b0fc-b2cced385a4f` |
| finance | fixed_assets | asset_value_and_depreciation | `asset_impairment_ratios` | derived | `55f4a415-ef9d-48a1-ac3e-938f8f2fa6a1` |
| finance | fixed_assets | asset_value_and_depreciation | `asset_revaluation_amounts` | base | `8bc46920-5842-467c-a3c5-06e7fb227bf6` |
| finance | fixed_assets | asset_value_and_depreciation | `asset_revaluation_ratios` | derived | `b75e2b95-f1d6-41f5-9c87-788b87095b95` |
| finance | general_ledger | gl_balance_sheet | `gl_balance_movement` | derived | `19e9bb5a-da8a-4f3d-b789-ab59b6baf9d7` |
| finance | general_ledger | journal_and_close_quality | `je_accrual_basis_counts` | base | `445e3064-f3ef-4c73-9034-15334d953714` |
| finance | general_ledger | journal_and_close_quality | `je_accrual_basis_ratios` | derived | `e40ab304-1aa4-4d16-a18a-05d1397b7de7` |
| finance | revenue_accounting | contract_lifecycle | `contract_lifecycle_ratios` | derived | `40771ab2-dbb0-43b9-a58e-5714ce3fffb2` |
| finance | revenue_accounting | contract_lifecycle | `contract_retention_ratios` | derived | `bb331e4b-3fff-4f91-bbde-59b04ec685ae` |
| finance | revenue_accounting | recurring_revenue | `contract_recurrence` | base | `ecd7f970-ddf2-40e7-89c3-91adf19dcea7` |
| finance | revenue_accounting | revenue_recognition | `recognition_event_line_counts` | base | `f6b720a7-0fbb-4854-baf1-2767783a7c5a` |
| finance | revenue_accounting | revenue_recognition | `recognition_event_revenue_amounts` | base | `06dd9ca2-0310-40d9-b23b-c9eece66059c` |
| finance | revenue_accounting | revenue_recognition | `revenue_line_recognition` | base | `fdd2bf53-3318-4235-a99d-382875b6c4dc` |
| finance | revenue_accounting | revenue_recognition | `revenue_recognition_amounts` | base | `1a6a34ed-22ce-4bac-aa38-f004bd8ac189` |
| finance | tax | input_tax_recovery | `input_tax_recovery_amounts` | base | `6e53464f-674f-4ef1-960f-9ec70db249df` |
| finance | tax | input_tax_recovery | `input_tax_recovery_counts` | base | `adc4e32e-19ef-4b52-8d8f-5b7a8edfa2d7` |
| finance | tax | input_tax_recovery | `input_tax_recovery_ratios` | derived | `40096d69-31c0-4bb2-952a-af1dd77d325e` |
| finance | tax | tax_liability_and_flows | `input_tax_amounts` | base | `c926ddb3-b225-4e3b-a023-4635666f225a` |
| finance | treasury | cash_receipts_and_payments | `bank_accounts` | base | `452ea3d6-9a61-4358-bd12-1b66a3d76afb` |
| finance | treasury | cash_receipts_and_payments | `cash_position_and_flows` | derived | `13422f13-bd6f-45a5-95ef-bb82d75bca82` |
| finance | treasury | debt_and_leverage | `debt_amounts` | base | `1791bef1-d103-4d75-b735-839612b4d56b` |
| finance | treasury | debt_and_leverage | `debt_leverage_ratios` | derived | `708b14b1-09bf-425e-85e1-4b61aea4f938` |
| finance | treasury | hedging | `hedge_amounts` | base | `9ecce835-9a55-4220-9149-25268264b351` |
| finance | treasury | hedging | `hedge_ratios` | derived | `bb55a7d0-a4c7-481f-8d71-faa3e848b646` |
