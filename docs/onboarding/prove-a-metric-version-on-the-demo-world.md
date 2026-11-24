---
id: prove-a-metric-version-on-the-demo-world
order: 53.5
title: "Prove a metric version on the demo world"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-contract-grammar, the-evaluation-boundaries, the-authority-model, onboarding-overview]
description: "Prove one approved metric contract version against the demo world's own values and record it as Demoed."
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

# Prove a metric version on the demo world

*DevGuide · task guide · drafted 2026-11-24 · read only: nothing in this guide was run.*

Workflow on the board: PW029 Demo a Metric Version, DW008 Work Out Expected Values from the World, DW004 Serve the World, PW100 Prepare the Demonstration Data

## Chapter 1. Overview

This chapter describes the one task of this guide and its place in onboarding a metric. The demo world is only the independent proof source: it works out its own expected values from its own records, apart from the platform, and hands them over. The platform then evaluates the version on the same world and records the match. The metric itself is onboarded to the Metric Catalog by the other guides.

### What the guide covers

This section lists the acts of the task in order.

- Pin the version on the world label (step 1).
- The demo world works out and hands over its values (steps 2 and 3).
- Declare the cells to prove (step 4).
- Request certification (step 5, task guide G).
- Serve the world, admit, stop the world (steps 6 to 8).
- Resolve, evaluate without writing, record the proof (steps 9 to 11).
- Carry the proof over and read the Demoed record (steps 12 and 13).

### Where it sits

This section describes when the task is needed, what must exist before it and what it leaves.

- Needed once for every metric version, after it is approved and realized and before it is certified.
- It leaves: a handed-over answer sheet, a declaration, admitted and resolved records under the current binding, one proof pin, one Demoed record, and the world stopped.
- After bc-db 0079 (applied 2026-11-24) no hand-over, custody, proof pin or metric contract remains: every metric starts this guide from step 1.

> **Note.** Evidence base: served engine bc-core 83b37959 (main, served since 2026-11-24 08:1x IST), which carries 1097 (role guard: each role held literally, no administrator pass), 1098 (world identity), 1099 (pins per binding) and 1100 (the G1 proof, the declaration door, world scope, trials on request certification and certify, door descriptions). bc-core paths are under `src/`. Nothing in this guide was run.

**Next:** Chapter 2, Before you begin.

## Chapter 2. Before you begin

This chapter describes the conditions to check once, before the first step.

### Roles and logins

This section states the roles and the five logins the task needs.

- `mcf_publisher` for the declaration and request certification. Since bc-core 1097 (served) each role must be held literally: there is no administrator pass (gap G13, guide 1).
- Five acts run outside the served engine with their own login, each supplied by the operator from Secrets Manager and never put in an argument: hand-over (`bc_demo_world_handover`), admit (`bc_demo_loader`), resolve (`bc_demo_resolver`), prove (`bc_demo_prover`), carry over (`bc_demoed_bridge_writer`) (gap G7).

### Engine head

This section states which engine the task needs.

- The served engine 83b37959 carries the P01-P04 label, custody by world code, the resolver world filter, the world-scoped reads and the declaration door.
- Still needed: the metric's own pin on the P01-P04 label (G5), an engine landing and a serve move for each new version (gap G9, guide 1).

### Environment

This section states where the task runs.

- Development only, `bc_platform_dev`: every outside command checks the database name and refuses a production name. Run commands in a login shell on the Mac.
- The answer sheet runs on a frozen read-only bench copy of the Odoo database `v3_lc5`, not on the served world.

> **Important.** No database apply, live act, host change or credential write without a recorded operator grant. Never stop a program by a name pattern.

**Next:** Chapter 3, Prove a metric version on the demo world.

## Chapter 3. Prove a metric version on the demo world

This chapter describes the steps of the task, in order. The order is fixed by the code: the version must be audit pending before the dry evaluation and the proof.

### Steps

#### Step 1. Pin the version on the world label

Name the version on the demo world: pin the metric's version on the world label that evaluates FY2026-27 P01-P04.

**Actor:** engine change (no role), reviewed by the auditor. **Grant:** engine code through the auditor, then the serve move under a desk grant.

**Inputs:** The new metric contract uid and the version's raw `version_code` (for example `v1`), from task guide D, step 5.

- **CLI (planned):** `bc world pin --label <label> --version <mcv-uid>` (planned, needs gap G5). Trial: none (no door)
- **API (today):** **No door: a code change per metric.** One line appended to `PLANE_METRIC_VERSION_BINDINGS` in `src/database/plane/plane-metric-version-binding.ts` (`:53-66`). The label `kaveri-demo-v3lc5-v2-p01-p04` has no metric entry at the served head.
- **Writes:** engine code only; then a serve move.
- **Failure modes:** "no governed metric-version binding for demo world '…'" and "demo world '…' binds no version for metric contract …" (`plane-metric-version-binding.ts:154, 163`), raised by the dry evaluation and the proof; not mapped to a status.; The pin is usable only when the package is sealed and the version is audit pending, active or superseded (`plane-metric-version-binding.ts:177-180, 200-203`).
- **Note:** The manifest still pins three contracts that bc-db 0079 deleted (a11a88f4, 01a19aec, e6438795); reads under those labels now refuse (gap G16).
- **Next:** step 2

#### Step 2. Work out the expected values

The demo world works out its own values for the version (the answer sheet) on its frozen bench, apart from the platform.

**Actor:** the demo world (bc-demo); no platform role. **Grant:** free (no platform write); the manifest, query and sheet land in bc-demo by its own review.

**Inputs:** A manifest naming `world_binding_id`, `world_code`, `study_csv` and `entries` (each with `metric_contract_uid`, `metric_version`, `legal_entity_code`, `currency_code`, `query_path`, `periods`); the query and its study row rated L4; all committed. The only committed manifest names e6438795, deleted by 0079: a new one is needed for the new contract.

- **CLI (planned):** `bc world sheet work-out --manifest <path> --bench <container> --dump-sha256 <hex>`. Trial: the work-out writes only a local file
- **API (today):** `python3 ops/answer-sheet/run_sheet.py <manifest> --bench-container <name> --bench-dump-sha256 <64 hex> --out <name>.sheet.json` (bc-demo `ops/answer-sheet/run_sheet.py:118-125`); each query runs inside `BEGIN READ ONLY` (`:71`).
- **Writes:** the sheet file only.
- **Failure modes:** Refused, exit 1: uncommitted (`:53`, `:55`); HEAD moved (`:90`); study row not L4 (`:96`); a query that fails or is not one row and one column (`:74`, `:77`); a value that is not decimal (`:79`); a bad dump hash (`:128`); provenance (`provenance.py:60-74`).
- **Next:** step 3

#### Step 3. Hand the values over

The demo world hands its values over to the platform, then the hand-over is verified.

**Actor:** the demo world's own login `bc_demo_world_handover` (the operator supplies it). **Grant:** desk grant (live write with the demo world's credential).

**Inputs:** Step 2 committed on bc-demo main; the sheet names the current binding e32071a8 and world code `kaveri-demo-v3lc5`.

- **CLI (planned):** `bc world sheet hand-over --commit <sha> --sheet <path>`, then `bc world sheet verify <handover-uid>`. Trial: none for the hand-over; `verify` is read only
- **API (today):** `python3 ops/answer-sheet/handover.py hand-over <commit> <path>` (bc-demo `handover.py:83-96`), which calls `demo.fn_hand_over_answer_sheet` (bc-db `0075:223`); then `handover.py verify <handover-uid>` (`:99-129`).
- **Writes:** `demo.answer_sheet_handover`, `demo.answer_sheet_cell`, `demo.oracle_custody` or `demo.oracle_custody_ccy`.
- **Failure modes:** `answer_sheet_caller_refused`; `answer_sheet_file_sha256_mismatch`; `answer_sheet_binding_absent`; `answer_sheet_binding_superseded`; `answer_sheet_world_code_mismatch`; `answer_sheet_value_not_decimal_string`; `answer_sheet_class_not_l4`; `answer_sheet_le_unknown`; `answer_sheet_cell_duplicate`; `answer_sheet_cell_occupied` (bc-db `0075:240-400`). The script prints "refused by the database" and exits 1.
- **Note:** bc-db 0079 deleted the only earlier hand-over (aeb45b59) with all custody: every new contract needs its own hand-over (gap G8).
- **Note:** The hand-over does not check that the metric contract exists: a wrong uid is caught only at the declaration (gap G15).
- **Next:** step 4

#### Step 4. Declare what the version must prove

Declare what the version must prove: its demo world and exactly the handed-over cells.

**Actor:** metric publisher (`mcf_publisher`) (`declare-demoed-version.command.controller.ts:22`). **Grant:** free for the check; desk grant for the declaration (live write).

**Inputs:** The version approved or audit pending, with a computed package snapshot (bc-db `0076:179-186`); step 3 done for the same metric and version.

- **CLI (planned):** `bc version declare-demoed --version <mcv-uid> --world kaveri-demo-v3lc5 --cells <file> --rationale <text> [--trial]`. Trial: yes: `POST …/check` (judged by the database, rolled back)
- **API (today):** `POST /api/commands/declare-demoed-version/check` (200), `POST /api/commands/declare-demoed-version/do` (201; 409 on a refusal), `GET …/status?metric_contract_version_uid=` and `GET …/verify?reference=`. Body: `metric_contract_version_uid`, `demo_world_version_code` (the world code, not a label), `cells` (`legal_entity_id`, `period_label`, `currency_code`), `rationale_text` (40 or more), optional `expected_package_signature_hash`.
- **Writes:** `mcf.metric_version_demoed_declaration`, `mcf.metric_version_demoed_declared_cell`, in one transaction.
- **Failure modes:** Codes (409 on `do`, `allowed:false` on `check`): `declaration_version_unknown`, `declaration_package_not_frozen`, `declaration_package_hash_mismatch`, `declaration_version_state`, `declaration_world_unknown`, `declared_cell_legal_entity_unknown`, `declared_cells_mixed_grid`, `declaration_has_no_cells`, `declared_cells_not_answer_sheet`, `declaration_already_exists`, `declaration_rationale_short`.
- **Note:** The declaration must exist before the proof is carried over (`w3_declaration`, bc-db `0076:401`). The table's comment says it is written before any proof, but the routine does not compare the times; declaring before the proof is this guide's order.
- **Next:** step 5

#### Step 5. Request certification (hand-off)

Request certification now (task guide G (Certify and activate a metric version), step 1), then come back to step 6.

**Task guide:** [Certify and activate a metric version, step 1](certify-and-activate-a-metric-version.md#step-1)

**Actor:** metric publisher (`mcf_publisher`). **Grant:** desk grant (live write).

**Inputs:** The version approved and realized (task guide E).

- **CLI (planned):** `bc version request-certification --version <mcv-uid> --cohort <code>`. Trial: see task guide G, step 1
- **API (today):** `POST /api/mcf/metric-contract-versions/:mcvUid/request-audit` (task guide G, step 1).
- **Writes:** see task guide G, step 1
- **Failure modes:** "its state is 'approved'; requires a sealed metric contract version in audit_pending, active or superseded" at steps 10 and 11 when this step is skipped.
- **Note:** Important: the dry evaluation and the proof read only a version that is audit pending, active or superseded (`USABLE_MCV_STATES`, `plane-metric-version-binding.ts:177`), and carrying the proof over needs audit pending or active (bc-db `0076:384-386`). So certification is requested before the dry evaluation, not after the proof. Guide 1 had this order wrong.
- **Next:** step 6

#### Step 6. Serve the demo world

Serve the demo world (it is stopped by default).

**Actor:** demo operator. **Grant:** desk grant (cloud act).

**Inputs:** AWS access to the box `i-0944d13adbafaa542`.

- **CLI (planned):** `bc world serve` (and `bc world status`). Trial: `status` is read only
- **API (today):** `~/bc-stack/odoo.sh up` (`:44-55`); `~/bc-stack/odoo.sh status` (`:65-69`).
- **Writes:** nothing on the platform; starts the instance, the serve and the forward to 127.0.0.1:8100.
- **Failure modes:** Exit 69 when the old `socat` relay holds :8100 (`:45`); exit 70 when the instance or the serve does not start or :8100 does not answer 200 (`:46-55`).
- **Next:** step 7

#### Step 7. Admit the source records

Admit the world's source records under the world's current binding.

**Actor:** operator, as `bc_demo_loader`. **Grant:** desk grant (live write; ruled to run as it is).

**Inputs:** Step 6; the reader id; the binding e32071a8 (no sealed admission version for it yet, read 2026-11-24).

- **CLI (planned):** `bc demo admit --reader <uuid> --binding <uuid>`. Trial: none
- **API (today):** Governed command outside the served engine: `node dist/database/demo-loader/demo-so-admission-cli.js --reader <uuid> --world-binding <uuid>` (`src/database/demo-loader/demo-so-admission-cli.ts:22-26, 63-80`); credential from `DEMO_LOADER_DATABASE_URL`.
- **Writes:** `demo.so_*`, `demo.so_admission_version`, `demo.admission` (through the demo admission routines).
- **Failure modes:** Missing or bad option (`demo-so-admission-cli.ts:57-71`); binding declares no connection; `DemoLoaderCredentialAbsentError`; `DemoLoaderIdentityError`. Exit 0 sealed, 2 rejections recorded, 1 error, 3 cleanup failed.
- **Next:** step 8

#### Step 8. Stop the demo world

Stop the demo world: nothing after admission reads it.

**Actor:** demo operator. **Grant:** free under the grant of step 6.

**Inputs:** Step 7 done; no other admission in hand.

- **CLI (planned):** `bc world stop`. Trial: `bc world status`
- **API (today):** `~/bc-stack/odoo.sh down` (`:56-64`).
- **Writes:** nothing on the platform; closes the forward, stops the serve and the instance.
- **Failure modes:** Exit 71 unless the instance is stopped and nothing listens on :8100 (`:62-63`); a foreign listener is never stopped.
- **Next:** step 9

#### Step 9. Resolve into canonical objects

Resolve the admitted records into canonical objects, reading only this world's binding.

**Actor:** operator, as `bc_demo_resolver`. **Grant:** desk grant (live write; ruled to run as it is).

**Inputs:** Step 7. The served engine carries the world filter of bc-core 1098.

- **CLI (planned):** `bc demo resolve --contract <name> --label <label> --binding <uuid>`. Trial: none
- **API (today):** Governed command: `node dist/demo-resolve/demo-resolve-cli.js <opts.json>` (`src/demo-resolve/demo-resolve-cli.ts`); options `expectedPlatformDb`, `demoWorldVersion`, `canonicalContractName`, and the required `worldBindingId`, checked against the label's declared binding (`plane-world-identity.ts:84-97`).
- **Writes:** the canonical object store (`demo.co_cc_das36_v5_1_0`), `demo.canonical_evaluation`, evidence and lineage.
- **Failure modes:** Option required; production database; a database other than `expectedPlatformDb`; not exactly one contract by name; `DemoWorldBindingError`. Not mapped to a status.
- **Note:** Important: not run, read only. The canonical store has a unique index on legal entity and invoice number (bc-db `0060:532`), and bc-db 0079 kept its 2714 rows from the superseded binding a6c55fa8 over the same connection. A resolve of the same invoices under e32071a8 may write nothing, so the proof would have nothing to read (gap G14). Probe read-only before the real run.
- **Next:** step 10

#### Step 10. Evaluate without writing

Evaluate the version on the demo world without writing, and compare with the handed-over values.

**Actor:** any session with the platform login (outside command). **Grant:** free (trial).

**Inputs:** Steps 1, 3, 5 (audit pending) and 9.

- **CLI (planned):** `bc demo evaluate --trial --version <mcv-uid> --label <label>`. Trial: yes: the whole command is a trial
- **API (today):** Governed command, read only by design: `node dist/boundary/e3-demo-plane-dry-eval-cli.js <opts.json>` (`src/boundary/e3-demo-plane-dry-eval-cli.ts`); options `expectedPlatformDb`, `evidenceOutPath`, `demoWorldVersion`, `metricContractUid`.
- **Writes:** nothing on the database; the evidence file.
- **Failure modes:** "dry-eval refused: no governed custody for metric …" (step 3 missing); a legal entity with no custody; no fiscal period; the pin refusals of step 1; a wrong or production database.
- **Note:** The read of canonical objects is scoped to the act's or the label's binding (bc-core 1100, `plane-world-read-scope.ts`, `fact-reader.service.ts`), so the rows of the superseded binding are not read (gap G3, closed).
- **Next:** step 11

#### Step 11. Record the proof

Record the proof: evaluate, compare with the demo world's values, and pin the match.

**Actor:** operator, as `bc_demo_prover`. **Grant:** desk grant (proof pin; ruled to run as it is).

**Inputs:** Steps 3, 5, 9 and a clean step 10.

- **CLI (planned):** `bc demo prove --version <mcv-uid> --label <label> --scope <file>`. Trial: none on the command; step 10 is its trial
- **API (today):** Governed command: `node dist/boundary/demo-commit-cli.js <opts.json>` (`src/boundary/demo-commit-cli.ts`); options `expectedPlatformDb`, `metricContractUid`, `demoWorldVersion`, `engineBuildId`, `scope` (`legalEntityCode`, `asOfDate`). It calls `demo.fn_emit_demo_proof_period_v5` (bodies of bc-db 0078).
- **Writes:** `demo.metric_run`, `demo.metric_evaluation`, `demo.ms_snapshot`, evidence, lineage, `demo.metric_proof_pin`, `demo.metric_proof_input`.
- **Failure modes:** Empty or partial scope, a cell not in the grid; no current binding or more than one; nothing under the current binding ("no 5.1.0 CO row traces to the current world binding"); world mismatch; cells that do not match custody; "a proof already exists" (bc-db `0078:126-228`). Not mapped to a status; exit 1.
- **Next:** step 12

#### Step 12. Carry the proof over

Carry the proof over: record that this version is Demoed.

**Actor:** operator, as `bc_demoed_bridge_writer`. **Grant:** desk grant (live write; ruled to run as it is).

**Inputs:** Steps 4, 5 and 11; the proof pin id.

- **CLI (planned):** `bc version carry-proof --version <mcv-uid> --proof-pin <uuid> --rationale <text>`. Trial: none
- **API (today):** Governed command: `node dist/registry/mcf/demoed-evidence-bridge-cli.js <opts.json>` (`src/registry/mcf/demoed-evidence-bridge-cli.ts`); options `mcvUid`, `demoProofPinRef`, `actor`, `rationale` (40 or more), `confirmDatabase`, `receiptOutPath`. The HTTP route `POST /api/mcf/metric-contract-versions/:mcvUid/demoed-bridge` refuses by design: 403 `bridge_authoring_cli_only`.
- **Writes:** `mcf.demoed_evidence_bridge`, `mcf.demoed_bridge_coverage_element`, `mcf.demoed_bridge_provenance`, `mcf.demoed_bridge_proof_attestation`.
- **Failure modes:** Service: `bridge_writer_absent`, `b1_subject_state`, `b1_snapshot_not_computed`, `b2_proof_not_current`, `b3_mc_hash_drift`, `b3_package_not_frozen_before_proof`, `b5_coverage_insufficient`.; Database (bc-db `0076:366-507`): `w2_subject`, `w3_declaration`, `w3_declaration_answer_sheet`, `w4_pin`, `w6_order` (the package snapshot after the proof run), `w7_world`, `w8_cells`, `w9_handover`, `w10_coverage`. Exit 2 on a refusal.
- **Note:** `b2_proof_not_current` reads the pin of the label that declares the proof's binding (bc-core 1100; gap G4, closed); before 1100 it read the world code's pin and refused a version pinned only on the P01-P04 label.
- **Next:** step 13

#### Step 13. Read the Demoed record

Read whether the version is Demoed.

**Actor:** any platform-scoped sign-in (no role on the route). **Grant:** free (read).

**Inputs:** Step 12.

- **CLI (planned):** `bc version demoed <mcv-uid>`. Trial: not needed (read only)
- **API (today):** `GET /api/mcf/metric-contract-versions/:mcvUid/demoed-claim` (`demoed-evidence-bridge.controller.ts:83-103`).
- **Writes:** nothing (read only)
- **Failure modes:** 400 not a uuid; 422 or 409 on a service refusal. A version that is not Demoed answers 200 NOT_DEMOED_AT_VERSION.
- **Next:** Back to guide 1, step 10

**Next:** Chapter 4, Troubleshooting, if a step refused.

## Chapter 4. Troubleshooting

This chapter lists the refusals most likely in this task, by code or message, with what to do. Every step lists its full set of failure modes.

| refusal | step | do |
|---|---|---|
| "binds no version for metric contract" | 1, 10, 11 | The version is not pinned on the label: engine change (G5). |
| "its state is 'approved'; requires … audit_pending, active or superseded" | 10, 11 | Request certification first (step 5). |
| `answer_sheet_binding_superseded`, `answer_sheet_binding_absent` | 3 | Hand over against the current binding e32071a8. |
| `answer_sheet_cell_occupied` | 3 | These cells are handed over already; a new version needs its own sheet. |
| `answer_sheet_class_not_l4` or "not L4" | 2, 3 | Rate the study row L4 in bc-demo first. |
| `declared_cells_not_answer_sheet` | 4 | Declare exactly the handed-over cells (same metric uid and version). |
| `declaration_world_unknown` | 4 | Use the world code `kaveri-demo-v3lc5`, not a label. |
| Few or no rows written by the resolve | 9 | Probably the unique invoice index against the kept rows (G14): stop, do not retry. |
| "dry-eval refused: no governed custody" | 10 | Step 3 is missing (no handed-over value for this cell). |
| "no 5.1.0 CO row traces to the current world binding" | 11 | Nothing resolved under e32071a8 (step 9, G14). |
| "a proof already exists" | 11 | A proof is recorded once: carry the existing pin over. |
| `DemoLoaderCredentialAbsentError`, `bridge_writer_absent` | 7, 12 | The operator supplies the act's login (G7). |
| 403 `bridge_authoring_cli_only` | 12 | Use the governed command, never the HTTP route. |
| `b1_subject_state`, `w2_subject` | 12 | Request certification first (step 5). |
| `w3_declaration` | 12 | Declare first (step 4). |
| `b2_proof_not_current` | 12 | The proof is not the current one for the label that pins the version; prove again on that label. |
| `w6_order` | 12 | The package snapshot came after the proof run: a new proof is needed. |
| `w8_cells`, `b5_coverage_insufficient`, `w10_coverage` | 12 | Prove the full declared scope. |
| odoo.sh exit 69, 70 or 71 | 6, 8 | 69: the old relay holds :8100; 70: start or HTTP check failed; 71: not confirmed stopped. |

**Next:** Chapter 5, Command reference.

## Chapter 5. Command reference

This chapter lists the command of each step (planned: none exists until the tool is built) and the request it makes today. "none" in the trial column means the engine has no dry run for that door at the served head.

| step | command | request | who | approval | trial |
|---|---|---|---|---|---|
| 1 | `bc world pin --label <label> --version <mcv-uid>` (planned, needs gap G5) | **No door: a code change per metric.** One line appended to `PLANE_METRIC_VERSION_BINDINGS` in `src/database/plane/plane-metric-version-binding.ts` | engine change (no role), reviewed by the auditor | engine code through the auditor, then the serve move under a desk grant | none (no door) |
| 2 | `bc world sheet work-out --manifest <path> --bench <container> --dump-sha256 <hex>` | `python3 ops/answer-sheet/run_sheet.py <manifest> --bench-container <name> --bench-dump-sha256 <64 hex> --out <name>.sheet.json` | the demo world (bc-demo); no platform role | free | the work-out writes only a local file |
| 3 | `bc world sheet hand-over --commit <sha> --sheet <path>`, then `bc world sheet verify <handover-uid>` | `python3 ops/answer-sheet/handover.py hand-over <commit> <path>` | the demo world's own login `bc_demo_world_handover` (the operator supplies it) | desk grant | none for the hand-over; `verify` is read only |
| 4 | `bc version declare-demoed --version <mcv-uid> --world kaveri-demo-v3lc5 --cells <file> --rationale <text> [--trial]` | `POST /api/commands/declare-demoed-version/check` | metric publisher (`mcf_publisher`) (`declare-demoed-version.command.controller.ts:22`) | free for the check; desk grant for the declaration | yes |
| 5 | `bc version request-certification --version <mcv-uid> --cohort <code>` | `POST /api/mcf/metric-contract-versions/:mcvUid/request-audit` | metric publisher (`mcf_publisher`) | desk grant | see task guide G, step 1 |
| 6 | `bc world serve` (and `bc world status`) | `~/bc-stack/odoo.sh up` | demo operator | desk grant | `status` is read only |
| 7 | `bc demo admit --reader <uuid> --binding <uuid>` | Governed command outside the served engine: `node dist/database/demo-loader/demo-so-admission-cli.js --reader <uuid> --world-binding <uuid>` | operator, as `bc_demo_loader` | desk grant | none |
| 8 | `bc world stop` | `~/bc-stack/odoo.sh down` | demo operator | free under the grant of step 6 | `bc world status` |
| 9 | `bc demo resolve --contract <name> --label <label> --binding <uuid>` | Governed command: `node dist/demo-resolve/demo-resolve-cli.js <opts.json>` | operator, as `bc_demo_resolver` | desk grant | none |
| 10 | `bc demo evaluate --trial --version <mcv-uid> --label <label>` | Governed command, read only by design: `node dist/boundary/e3-demo-plane-dry-eval-cli.js <opts.json>` | any session with the platform login (outside command) | free | yes |
| 11 | `bc demo prove --version <mcv-uid> --label <label> --scope <file>` | Governed command: `node dist/boundary/demo-commit-cli.js <opts.json>` | operator, as `bc_demo_prover` | desk grant | none on the command; step 10 is its trial |
| 12 | `bc version carry-proof --version <mcv-uid> --proof-pin <uuid> --rationale <text>` | Governed command: `node dist/registry/mcf/demoed-evidence-bridge-cli.js <opts.json>` | operator, as `bc_demoed_bridge_writer` | desk grant | none |
| 13 | `bc version demoed <mcv-uid>` | `GET /api/mcf/metric-contract-versions/:mcvUid/demoed-claim` | any platform-scoped sign-in (no role on the route) | free | not needed (read only) |

**Next:** Appendix A, Known gaps.

## Appendix A. Known gaps for this task

This appendix lists the gaps found in this task, each with the smallest fix and its kind. Kinds: engine code goes through the auditor; a database change needs the owner's yes; a credential is the owner's; a desk grant is a recorded grant.

### G2. The declaration door is served; one refusal has no code

- **What:** bc-core 1100, served since 2026-11-24, adds the declaration command with a database-judged `check` trial over the tables, checks and insert grant of bc-db 0076. One database refusal (`0076:215`, cells outside the declaration's transaction) has no code and is thrown on.
- **Smallest fix:** Add the one missing code.
- **Kind:** engine code (auditor)

### G3. World scope, part 1: the dry evaluation's read (closed)

- **What:** Before bc-core 1100 the read of canonical objects had no world scope, so the superseded binding's rows were read too. 1100, served since 2026-11-24, scopes it to the act's or the label's binding.
- **Smallest fix:** None left (record only).
- **Kind:** engine code (done in bc-core 1100)

### G4. World scope, part 2: reading a proof back by its pin (closed)

- **What:** Before bc-core 1100 the proof was read against the world code's pin, not the label's, which also made carrying the proof over refuse `b2_proof_not_current`. 1100, served since 2026-11-24, reads the label that declares the proof's binding.
- **Smallest fix:** None left (record only).
- **Kind:** engine code (done in bc-core 1100)

### G5. A metric is named on the world only by a code change

- **What:** Each version is pinned on a world label in code (`src/database/plane/plane-metric-version-binding.ts`); the P01-P04 label pins no metric at the served head.
- **Smallest fix:** First metric: append its pin once the contract and version exist, in an engine landing. Before the batches: the pin as governed data (TSK-3a1e3c).
- **Kind:** engine code (auditor) now; engine code and a database change (owner's yes) for the batches

### G7. Five acts run outside the served engine

- **What:** Hand-over, admit, resolve, prove and carry over are governed commands, each with its own login that the served engine refuses to start with.
- **Smallest fix:** Ruled: the tool calls them as they are, each with its own approval mark; it never reads a secret.
- **Kind:** credential (owner: who holds each login for a session); tool wiring

### G8. The hand-over again, for every new contract

- **What:** bc-db 0079 deleted the only hand-over (aeb45b59) and all custody; the committed bc-demo manifest names the deleted e6438795. Custody is unique per world, metric, version, legal entity and period (bc-db `0051:201`).
- **Smallest fix:** For each new contract the demo world adds its query and study row, works out the sheet and hands it over (steps 2 and 3). Whether the ~900 already have L4 study rows is not established.
- **Kind:** bc-demo content (its own review) and a credential act

### G14. The resolve under the current binding may meet the kept canonical rows

- **What:** A unique index on legal entity and invoice number (bc-db `0060:532`, live) and 2714 kept rows from a6c55fa8 over the same connection: a resolve of the same invoices under e32071a8 may write nothing. Read, not run.
- **Smallest fix:** First a read-only probe (count the admitted invoices whose legal entity and number already exist in the store); if they collide, the owner decides on a bc-db forward migration or another design act.
- **Kind:** database change (owner's yes), after a probe

### G15. The hand-over does not check the metric contract exists

- **What:** bc-db 0075 reads no `mcf` table; a wrong uid is caught only at the declaration.
- **Smallest fix:** The planned `bc world sheet hand-over` reads the version first.
- **Kind:** tool code

### G16. Pins of deleted contracts remain in code

- **What:** `PLANE_METRIC_VERSION_BINDINGS` still pins a11a88f4, 01a19aec and e6438795, all deleted by 0079; the file is append-only.
- **Smallest fix:** None for the path; those labels now refuse.
- **Kind:** none (record only)

### G10. No trial on most acts of this task (part)

- **What:** No dry run on the hand-over, admit, resolve, prove or carry over. Trials that exist: the work-out, the declaration `check`, the dry evaluation, request certification `dryRun`.
- **Smallest fix:** File each one by one; the tool marks each "no dry run".
- **Kind:** engine code (auditor)
