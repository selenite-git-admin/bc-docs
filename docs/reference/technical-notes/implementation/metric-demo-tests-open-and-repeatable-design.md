---
uid: metric-demo-tests-open-and-repeatable-design
title: Repeatable tests of a metric version on the demo world, over every month the world holds data for (design)
description: "Design for the owner's rulings of 2026-11-24: every test of a metric version covers every month the demo world holds data for; tests can be repeated at any time and every result is kept, pass or fail; approval names a passing test; a failed test flags the metric, opens a ticket and applies a lock; in a disagreement the source documents decide, and either side may be the one fixed. Proposes the bc-db, bc-core, bc-demo and bc-admin changes; nothing is built."
status: reviewing
authority: reference
date: 2026-11-24
project: bc-docs
domain: metrics
subdomain: metric-lifecycle/demoed
focus: design
governing_adr: DEC-79b62f
---

# Repeatable tests of a metric version on the demo world

*Design note · proposed 2026-11-24, revision 3 · nothing in this note has been built or run. Its database changes are a proposal: they need the owner's explicit yes under the Database Change Protocol before any migration is written.*

Evidence base, read at these heads on 2026-11-24: bc-db `origin/main` 18d6884, bc-core `origin/main` df47ce00 (the served engine), bc-demo `origin/main` 428ab310, bc-admin `origin/main` 6267a64, bc-docs `origin/main` 96487a5. Live rows were read read-only on `bc_platform_dev` on 2026-11-24 with the read-only database tool. Paths in bc-core are under `src/` unless shown otherwise.

Revision 2 follows two later rulings of the owner (section 2). Revision 1 let each test choose its own months; that is withdrawn. Revision 3 folds in the auditor's boundary as design rules (section 3.5). The auditor's answer is ACCEPTED WITH BOUNDARY: bc-external-audit `docs/RESPONSE-Codex-gen-3a7aae-01-open-repeatable-demo-tests-design-2026-11-24.md`, commit 504b5bd0, reviewed at head 88b0c35d. It accepts the design direction only; no database change, landing or onboarding follows from it.

## 1. The problem in plain words

To be approved, a metric version must give the same answers as the demo world. Today the platform fixes, once per version, the months on which this is shown. The choice is made by hand, and a version cannot be tested again on the same records.

That is what happened to **customer invoice volume** (metric contract `fe91c450`, version `b9357731`, state `audit_pending`):

- Its declared months are FY2026-27 P01 to P04 for KAVERI-IN (declaration `f41bcda2`, 4 cells, read live).
- The platform's answers matched the demo world's own answers in all four: 60, 58, 62 and 67 (proof pin `00f5f597`, comparison `match`, read live).
- The proof was still refused, correctly. The metric counts only documents whose type is "customer invoice", and none of the four months holds a credit memo, so that rule was never put to the test (check w10, coverage).
- The demo world holds credit memos in other months. Its canonical records hold 2,714 distinct invoices for KAVERI-IN over 41 fiscal periods, FY2023-24 P01 to FY2026-27 P05, and 30 of them are not customer invoices (read live from `demo.co_cc_das36_v5_1_0`, which keeps one copy per world binding since 0081, so 5,428 rows).

The owner's answer: no one chooses months. Every test covers every month the world holds data for. A test can be repeated at any time. Every result is kept.

## 2. The owner's rulings

Recorded in barecount-devhub branch `claude/operator-review-content`, `artifacts/operator-review/DECISIONS-workflow-review.md`, the last three entries (commits 98190a23, afbe5758, dd311fe2).

1. **Tests are open, repeatable and all kept** (20:05 IST). Every test is kept, pass or fail. Approval names the test it relies on. A re-check is allowed at any time, also after approval. Before approval, at least one passing test must exercise every rule of the definition. A failed test flags the metric: a person decides, and nothing switches off by itself. It also opens a ticket and applies a lock. The metric list gains a Tests column.
2. **Every test covers every month the demo world holds data for** (afbe5758). The owner: "Instead of adding functions/actions let us make it mandatory to select all months available in demo world. Simple." Asked whether he means the months the world holds data for or the months it has handed over: "every month the world holds data for". So there is no choosing of months, no test on part of them, and 0076's rule of one declaration per version stays.
3. **In a disagreement the documents decide** (dd311fe2): "agree, documents decide. update the design". On a mismatch, each side lists the documents it counted. A person opens the differing documents in Odoo and judges them against the owner's plain-language definition. The judgement is recorded, and either side, the engine or the world, may be the one fixed.

Open, for the owner: who may run a re-check, and what the lock holds (sections 8 and 14).

## 3. The model

### 3.1 The declaration: every month, once per version

Each version keeps **one** declaration, as bc-db 0076 has it (`uq_metric_version_demoed_declaration_mcv`, 0076:121). Revision 2 adds one rule: the declared cells must be **every month the demo world holds data for**, for each of its legal entities. The declaration is still written once, before any proof, and it cannot change.

### 3.2 What "every month the world holds data for" means, and where it is read

**It is not declared anywhere today.** The demo plane has no table that states a world's months:

- the demo schema's 38 tables, read live, include the world (`demo.synthetic_world`), its bindings, its legal entities and their calendars (`demo.fiscal_calendar_config`: calendar code and effective dates only), but no period range;
- the world labels in bc-core code (`database/plane/plane-world-evaluation-coordinate.ts:40-52`) state the dates one proof evaluates, not the months the world holds.

The months can be seen in three places:

1. **The frozen bench**, the read-only copy of the Odoo database (pg_dump sha256 `d0a33f41…`). This is the world itself. The study notes that its data ends 2026-08-31 (bc-demo `…/sql/customer-invoice-volume-workings-2026-11-23.out`, last line).
2. **The admitted source records** under the world's current binding (the `demo.so_sc_*` stores; `demo.so_admission_version.world_binding_id`).
3. **The canonical records** (above: 41 periods for KAVERI-IN). These are an output of the platform, which is under test, so they cannot define the months.

**Proposal.** The world declares its own months, the same way it hands over its answers: a **world-month manifest**, derived and sealed from the frozen source (rule B7). One immutable row per (world binding, legal entity, fiscal period) is worked out on the frozen bench by a committed, reviewed, read-only query. Before authoring, the design must define two things:

- **The source population.** Which Odoo records count as "the world holds data" for a month. The auditor warns that "posted accounting entry" may be narrower than "every month the world holds data for" (reply gen-3a7aae-01).
- **The period and calendar mapping.** How a record's date maps to the legal entity's fiscal period (KAVERI-IN: IN-APR-MAR-MONTHLY).

The manifest includes every month with world data, **including months with zero qualifying documents for a given metric**: for a count, such a month expects 0. It is written through the world's own hand-over login and a definer routine that takes the committed file's bytes, like `demo.fn_hand_over_answer_sheet` (0075). The platform then checks against it and never infers the months from its own records. An alternative, reading the months at check time from the admitted source records (place 2), needs no new table, but it infers the months from surrounding state, and each source has its own store.

**Where the check sits.** In two places, both in 0076's own functions, so that both enforcement points hold the same rule:

- the declaration's commit check, `mcf.fn_metric_version_demoed_declaration_has_cells` (0076:268-292): the declared cell set must equal the handed-over answer-sheet set (kept) **and** the world-month set for the same binding and legal entity;
- check w3 in the writer routine (0076:396-415), where the answer-sheet equality is checked again: the same added condition, named `w3_declaration_world_months`.

Check w8 (0076:468-483) keeps the exact equality of the pin's cells with the declared cells (rule B2).

Because the answer-sheet match stays an equality against the union of every hand-over (0076:239-264 with `demo.fn_answer_sheet_cells`, 0075:487-501), the demo world must hand over every month too. All three sets then equal one another: the world's months, the answer sheet and the declaration.

### 3.3 A test, and a re-check

A **test** is one proof run of the version over its declared cells, with its verdict recorded:

- **passed**: every value matched. The record says whether the test exercised every rule (coverage complete or partial).
- **failed**: at least one value differed. This flags the metric.

A refusal of the act itself (a wrong caller, a pin that does not exist, the wrong version) is not a test and writes nothing, as today.

A **re-check** is a new test on the same declaration: a new proof run with its own pin and its own verdict. Nothing earlier is touched. It can be run on an `audit_pending` or `active` version; the writer already accepts both (0076:384).

A test that passed with complete coverage also writes a **Demoed record** (`mcf.demoed_evidence_bridge` with its provenance), as today. The routine already writes each new record over the current head (0076:510-519).

### 3.4 How approval cites a test

The activation act already names the Demoed record it relied on (`metric_audit.transition_evidence.demoed_evidence_bridge_uid`, 0076:325-331). That record's provenance names the declaration (0076:295-310), and the new test result names the record (5.1 item 2). Approval therefore names its test with no new column. The approval act's needs:

- a Demoed record of this exact version whose proof still reads current (unchanged: `mcf-cert-writer.service.ts:1047-1058`; c16 at 0076:845);
- under lock option L1 or stronger (section 8), no failed test of this version that a person has not yet resolved.

### 3.5 Design rules from the auditor's boundary

These rules bind the implementation. Each restates a boundary in the auditor's reply gen-3a7aae-01 (bc-external-audit commit 504b5bd0).

- **B1. Re-check at any time (R2).** A re-check is a fresh evaluation act. It emits its own immutable run, pin, result and evidence, also when its inputs are unchanged, and it never reconstructs an earlier act or rewrites its verdict. A failed value comparison is a **test result**. A malformed or unauthorised act stays a **refusal**, with no test result. One immutable declaration per version is kept.
- **B2. Three sets agree; w8 stays exact.** The declaration's commit check and w3 compare the declared cell set with both the world-month set and the handed-over answer-sheet set. w8 keeps exact pin-to-declaration cell equality.
- **B3. A mismatch-safe hand-over check.** `demo.fn_pin_answer_sheet_refusal` rejects every non-`match` pin at its first gate (0075:422-424), so it is not used unchanged for a mismatch. A new mismatch-safe hand-over and custody predicate proves that each expected cell, its value, its metric and version, and its world binding came from the world's own hand-over. The engine's differing result is compared separately. Without this, a failed test and its flag could rest on an unverified expected value.
- **B4. One writer, old path revoked atomically.** The single writer keeps the present w0-w8 structural and identity checks. EXECUTE on the old writer is revoked in the same transaction that installs the new one.
- **B5. Coverage v3: the time gate is witnessed per cell.** For a particular cell, a row from another declared month may serve as the outside-period witness only if all three hold:
  - it is in the same partition;
  - it passes the other eligibility rules;
  - the evaluation of that cell actually excluded it by its time gate.

  The checker records the cell and the identities of both the inside and the excluded witnesses. A paired negative test shows the element uncovered when no such exclusion occurred. Rows in two different months of the union of declared cells do not prove the gate. w10 keeps requiring complete coverage for a Demoed record. A partial pass is recorded without one. Computed dimensions, conditional branches and some partition cases stay uncovered, so all months alone cannot certify those shapes.
- **B6. Document custody on both sides.**
  - The engine's list of counted documents comes from its own evaluation act.
  - The world's list is derived independently on the frozen bench from reviewed, committed query bytes. Neither its values nor its membership come from the evaluator or its contract-generation path, which keeps it compatible with ADR-025bfc T4.
  - Both lists and their hashes are bound to the exact cell, run, world binding, source-document identity and, for sums, each document's contribution amount.
  - The mapping from Odoo documents to canonical documents is proven before any set difference is used.
- **B7. The world-month manifest.**
  - It is derived and sealed from the frozen source, including months with world data but zero qualifying documents for the metric.
  - Its exact source population and its period and calendar mapping are defined before authoring.
  - The manifest, the hand-over, the declaration, the proof scope and the world evaluation coordinates must agree for the same binding and legal entity.
  - The writer covers one legal entity, so a world with several legal entities needs a separately designed route. No full-world coverage is claimed through one entity's pin.
- **B8. A corrected world answer is out of scope here.** It would be a superseding hand-over that keeps the old answer. Its custody, its current-answer selection and its proof-currency rules need their own design and the owner's own database yes (section 15).
- **B9. Ticket recoverable; records decide.** A ticket is created, recoverably, for each failed result. The immutable result and resolution decide the flag and the lock, never the ticket's status.
- **B10. L1 and an active version.** L1 does not constrain a version that is already active when a re-check fails. The owner settles that consequence before any lock is built (section 14).

## 4. What exists today

Read at bc-db 18d6884 and bc-core df47ce00.

| Where | What it does today | Effect on this design |
|---|---|---|
| `mcf.metric_version_demoed_declaration` (0076:110-130) | One immutable declaration per version, cells equal to the answer sheet (0076:280). | **Kept.** One rule is added (3.2). |
| `mcf.fn_record_demoed_bridge` (0076:337-537) | Every refusal is raised before any write (0076:335-336). | A failed or partial test leaves no record; rule 1 needs one. |
| The demo proof emit `demo.fn_emit_demo_proof_period_v5` / `demo.fn_emit_demo_proof_v5` (0078:220, 0078:441) | A cell that differs from the world's value raises: "Demoed is emitted only on a full match". | A **value mismatch** writes nothing at all. `demo.metric_proof_pin` already allows `comparison_outcome = 'mismatch'` (`ck_demo_proof_pin_outcome`, read live), but no routine writes it. |
| The emit's per-act key (0078:224-229, 0078:445-450) and the live unique index `uq_demo_metric_run__act` on `demo.metric_run (metric_contract_id, metric_version, demo_world_version, consumed_co_digest_sha256)` | Refuses a second proof of the same version on the same world over the same canonical records. | **A re-check on unchanged records is refused today.** This blocks rule 1 (re-check at any time); see 5.6. |
| Coverage checker v2, `registry/mcf/demoed-coverage-checker.ts` | The time-gate witness needs eligible rows "outside the window", and a row is outside only if it is in **no** declared cell (`classifyScopeRows`, :125-134, `outWindow = !inCell && …` at :131; `temporalElement` :294-308). | **When every month is declared, no row is outside, so the time-gate element of every `period_aggregate` metric is uncovered and w10 refuses every such test.** See 6, E12. |
| Pin-side hand-over check `demo.fn_pin_answer_sheet_refusal` (0075:413-476) | Checks each proof cell by membership in a hand-over under the proof's own binding; returns `answer_sheet_pin_absent` for a non-matching pin (0075:422-424). | Kept; it applies to matched pins only. |
| Expected values `demo.oracle_custody` | One immutable value per (world code, metric, version, legal entity, period) (`uq_demo_oracle_custody_cell`, read live); a second hand-over of a cell is refused (`answer_sheet_cell_occupied`, 0075:400). | Re-checks reuse the same expected values (`demo.ms_snapshot` has no unique index on the custody reference, read live). **A corrected world answer for the same version cannot be handed over** (section 7). |
| The proof's records: `demo.ms_snapshot` (columns: snapshot, evaluation, legal entity, period, custody reference, `result_decimal`), `demo.metric_proof_input` (`co_row_count`, `lineage_set_sha256`), the evaluation's Evidence (content hash over the cells, 0078:247-253) | The proof keeps each cell's value and a digest of the records it consumed. | **It does not record which documents each cell counted** (section 7). |

## 5. What changes in the database (proposal)

**Status: a proposal for the owner's yes.** It is smaller than revision 1. No declaration rule is relaxed. Proposed as two bc-db forward migrations, numbers to be confirmed at authoring: **0082** for the platform side (`mcf`, `metric_audit`) and **0083** for the demo side (`demo`). On 2026-11-24 the highest merged migration is 0081, the only open bc-db pull request that claims a number is #177 (0073), and no bc-db branch carries a file numbered 0082 or higher. Each would be proven on an owner- and grant-faithful restore of a fresh read-only dump, including the served-login vectors, and applied only through the governed runner under a recorded desk grant. Rules followed: ISO 11179 names (DEC-69f09e), at most 20 columns, foreign keys on every in-plane reference, no JSONB for queryable data, indexes in the same migration (DEC-1918d0).

**Removed from revision 1:** choosing cells per test, the record-before-run check (w6b), tests on part of the months, the change of the answer-sheet match to inclusion, dropping `uq_metric_version_demoed_declaration_mcv`, the `void` verdict, and accepting `active` in the declaration guard.

### 5.1 The 0082 changes (platform side)

1. **The world-months check** (3.2): the commit check and w3 also require the declared cells to equal the world's declared months for the declared legal entity. A new read-only definer function `mcf.fn_demoed_declaration_covers_world_months(uuid)` is called as its owner, like the 0075 predicates.
2. **`mcf.metric_version_demo_test_result`**: one immutable row per test, 12 columns.

   | Column | Type | Rule |
   |---|---|---|
   | `metric_version_demo_test_result_uid` | uuid | primary key |
   | `metric_version_demoed_declaration_uid` | uuid NOT NULL | FK to the version's declaration; many results per declaration; indexed |
   | `demo_metric_proof_pin_ref` | uuid NOT NULL | the run's proof pin, **UNIQUE** (one verdict per run); a cross-plane reference with no FK, the pattern of `mcf.demoed_evidence_bridge.demo_metric_proof_pin_ref` |
   | `test_verdict_code` | text NOT NULL | `passed` or `failed` |
   | `verdict_reason_code` | text NULL | NULL when passed; `value_mismatch` when failed |
   | `mismatched_cell_count` | integer NULL | at least 1 when failed |
   | `coverage_checker_version` | text NULL | set when passed |
   | `coverage_verdict_code` | text NULL | `complete` or `partial` when passed |
   | `demoed_evidence_bridge_uid` | uuid NULL | FK, UNIQUE; set exactly when passed with complete coverage |
   | `writer_routine_version` | text NOT NULL | `fn_record_demo_test_result-v1` |
   | `recorded_by_name` | text NOT NULL | the actor |
   | `recorded_at` | timestamptz NOT NULL | set by the database |

   CHECKs tie the columns to the verdict. The version is reached through the declaration, so it is not stored twice. The table is immutable (update, delete and truncate are refused by the 0065 trigger function). No login holds INSERT; only the routine in item 5 writes it. SELECT goes to `bc_platform_runtime`.
3. **`mcf.metric_version_demo_test_result_element`** (7 columns: uid, result FK, `element_kind_code`, `element_ref_text`, `covered_flag`, `witness_count`, `witness_digest`; UNIQUE on result, kind and ref): the coverage elements of a passed test with **partial** coverage, which are lost today when w10 refuses. A complete test keeps its elements in `mcf.demoed_bridge_coverage_element`, as today. Same immutability and grants.
4. **`mcf.metric_version_demo_test_failure_resolution`**: the person's judgement of one failed test (section 7), 9 columns:
   - uid;
   - result FK, **UNIQUE**;
   - `corrected_side_code`: `engine`, `world` or `both`;
   - `engine_document_list_sha256` and `world_document_list_sha256`: the two lists the judgement compared;
   - `directory_member_uid`: FK to `metric_directory.member`, whose definition was the yardstick;
   - `judgement_text`: at least 40 characters, naming the differing documents and why;
   - `resolved_by_name`;
   - `resolved_at`, set by the database.

   An insert guard requires the result to be `failed`. Immutable. INSERT goes to `bc_platform_runtime` through a command (E10). The lock is released by this row, never by the ticket's status: `support.ticket` is a mutable working table (status and `updated_at`, bc-core `database/schema/support/ticket.ts:22,35`), and a lock must rest on an immutable record (Invariant III).
5. **One writer for every outcome**: `mcf.fn_record_demo_test_result(p_mcv, p_pin, …)`, SECURITY DEFINER, owned by `bc_schema_owner`, EXECUTE only to the existing producer login `bc_demoed_bridge_writer`. It keeps the inputs and the cross-plane read of `mcf.fn_record_demoed_bridge` (0076:337-353) and every one of its structural and identity checks w0 to w8 in their order (0076:364-483; rule B4), with these changes:
   - w4 no longer requires `match` (0076:433); every other w4 condition stays. The outcome is the verdict: `mismatch` is recorded as **failed** (`value_mismatch`, with the count of differing cells) only after w5 to w8 hold **and** the mismatch-safe hand-over predicate (5.2 item 6) holds. If that predicate fails, the act is refused and no result is written (rule B3);
   - w9 (`demo.fn_pin_answer_sheet_refusal`, unchanged) applies to a matched pin only;
   - w10 (0076:496-508): when partial, the test is recorded as **passed, partial**, with its elements, and no Demoed record is written; when complete, the 0076 write block (0076:510-535) writes the Demoed record, its elements, its provenance (writer version `fn_record_demoed_bridge-v2`, which the provenance check `^fn_record_demoed_bridge-v[0-9]+$` at 0076:309 accepts) and its `current` attestation, and then the result row naming it;
   - every other refusal still writes nothing.

   EXECUTE on `mcf.fn_record_demoed_bridge` (v1) is revoked from `bc_demoed_bridge_writer` in the same transaction that installs the new routine, so that one routine alone writes Demoed records and the two are never callable together (rule B4).
6. **The lock** (depends on the owner's choice, section 8). Under L1 or stronger, a new condition **c17** `c17_unresolved_failed_demo_test` goes in `metric_audit.fn_intrinsic_decision_refusal`, added the way 0076 added c16: c1 to c16 copied byte for byte from the live body and pinned by its md5 in the precondition (0076:69-72). The flip trigger already refuses `audit_pending → active` while the list is not empty (0076:38-39).
7. **Grants**: SELECT on the new tables to `bc_platform_runtime`; INSERT on the resolution table only. bc-core `tools/grant-drift/bc-platform-runtime-grants.tsv` (lines 124-134 record the 0076 grants) is updated in the same landing. The rollback is refused while any result, element or resolution row exists.

What is left of the revision-1 0082: items 2 to 7, minus the `void` verdict; plus item 1, which is new.

### 5.2 The 0083 changes (demo side)

1. **The world's declared months**: `demo.world_binding_data_period` (5 columns: uid; `world_binding_id` FK; `legal_entity_id` FK; `period_label`; `declared_at`), UNIQUE on binding, legal entity and period, and immutable. Its writer is a definer routine for the world's hand-over login (`bc_demo_world_handover`, 0075), taking a committed file's bytes, as `demo.fn_hand_over_answer_sheet` does.
2. **A mismatch is recorded.** The two emit routines (0078) are replaced so that, when every structural check holds, a value difference records the run, the evaluation, one snapshot row per cell (its value beside its custody reference), its Evidence and Lineage, and a pin with `comparison_outcome = 'mismatch'`. The structural checks are: a declared legal entity, custody for every cell, the cells equal to the scope, one current world binding, and lineage present. A cell with no custody row still raises. The evaluation status and the Evidence outcome for a mismatch are to be fixed at authoring. The matched path is unchanged.
3. **A re-check on unchanged records: R2** (rule B1; the auditor: R1 "would silently narrow" the owner's ruling). The per-act key becomes a caller-given act uid, unique per run. `uq_demo_metric_run__act` and the guard at 0078:224-229 and 445-450 change accordingly. A re-check on the same engine and the same records is a distinct act that gives a new run, a new pin and a new result (Invariant V allows this; it never reconstructs an earlier act). The former option R1 (re-check only after the engine build changed) is dropped.
4. **The documents each cell counted** (rule B6): `demo.ms_snapshot_member` (6 columns: uid; `metric_snapshot_id` FK, which fixes the cell, the evaluation, the run and, through the proof input, the world binding; the canonical record id; the source-document identity; `counted_flag`; `contribution_amount`, set for a sum). It is written by the emit in the same transaction, from the evaluation act's own list of members (E13), never from a later read. The set's hash goes into the cell's Evidence.
5. **A corrected world answer: out of scope** (rule B8). It needs its own design and the owner's own database yes (section 15).
6. **The mismatch-safe hand-over predicate** (rule B3): a new read-only definer function, `demo.fn_pin_handed_over_expected_cells_refusal(uuid)`. For a pin of either outcome it proves each expected cell, its value, its metric and version, and its world binding came from the world's own hand-over. It uses the membership, world-binding and custody-set-hash checks of `demo.fn_pin_answer_sheet_refusal` (0075:413-476), without that function's first `match` gate. It does not judge the engine's values; the routine compares those separately.

## 6. What changes in the engine (bc-core), at every enforcement point

| # | Where | Change |
|---|---|---|
| E1 | `registry/mcf/demoed-declaration/declare-demoed-version.command.ts` (header :1-22) | Unchanged in shape (one per version). Its `check` reports the new database refusal `declared_cells_not_world_months`; the body's description (:64) says "every month the world holds data for". |
| E2 | `registry/mcf/demoed-declaration/demoed-declaration-refusals.ts` | Maps the new refusal. |
| E3 | `registry/mcf/bridge-record-writer.ts:94`, `demoed-evidence-bridge-cli.ts` | Call `mcf.fn_record_demo_test_result`; read the verdict it returns. |
| E4 | `registry/mcf/demoed-evidence-bridge.service.ts` (step 5 :369-382; reconcile :16-18) | A hollow or partial test is no longer refused before the routine; it is recorded as passed, partial. "Reconcile, never replay" stays, keyed by the pin. |
| E5 | `registry/mcf/demoed-bridge-writer-refusal.ts` | Maps the new routine's refusals and verdicts. |
| E6 | The demo proof command (proof guide step 11) | On a mismatch pin, record the failed result instead of stopping. |
| E7 | `registry/mcf/mcf-cert-writer.service.ts:1047-1058` (`assertCandidateDemoedInTx`, used by `admitMetric` at :2973-2974) | Under L1 or stronger, a sibling check names an open failure before the database's c17 does. |
| E8 | `database/plane/plane-world-evaluation-coordinate.ts:40-52`, with `plane-cc-version-binding.ts:37`, `plane-metric-version-binding.ts` and `plane-world-identity.ts` | The world label's dates must be every month the world holds data for: for Kaveri, 41 period-end dates. This is one label per world binding, not one per test. |
| E9 | Ticket on failure (new; rule B9) | After a failed result, open a ticket through `SupportService.createTicket` with `entity_type = 'mcf.metric_version_demo_test_result'` and the result uid. The record comes first and the ticket second, and the ticket is recoverable. A read lists every failed result without a ticket, and an idempotent "open the ticket for this failed test" command can be run again until each has one. `boundary/boundary-ticket.service.ts:26-40` is fire-and-forget and never throws, which is not enough. The flag and the lock are read from the result and the resolution only. |
| E10 | Resolve a failure (new command) | Writes the resolution (5.1 item 4) after the documents are judged (section 7); comments on the ticket and closes it. |
| E11 | Reads: `registry/mcf/mcf-read.service.ts:512-530` (the list behind `GET /api/mcf/metric-contracts`, `mcf-publication-eligibility.controller.ts:30,70`) and `GET /api/mcf/metric-contract-versions/:mcvUid/demoed-claim` (`demoed-evidence-bridge.controller.ts:83`) | One set-based read of each current version's test counts and open failure with its ticket id; the claim read lists every test. Reads never evaluate. |
| E12 | **Coverage checker v3** (`demoed-coverage-checker.ts:125-134, 294-308`; rule B5) | Needed before any `period_aggregate` metric can pass w10 under the all-months rule. The time-gate element is witnessed **per cell**. A row from another declared month is that cell's outside witness only if it is in the same partition, passes the other eligibility rules, and was actually excluded by that cell's time gate in the evaluation (read from the evaluation's own member record, 5.2 item 4). The element records the cell and the identities of both witnesses. A paired negative test shows the element uncovered when no such exclusion is recorded. w10 keeps requiring `demoed-coverage-v2` or later (0076:499-502) and complete coverage for a Demoed record, so v3 is accepted without a database change. This changes how one element is witnessed, not the w10 rule; the owner's rule 5 stands. |
| E13 | The proof's member list | The evaluation hands the emit the canonical records each cell counted (5.2 item 4). Whether the dry evaluation exposes them today was **not grounded** (section 15). |

`demoed-at-version.ts` and `demoed-activation-record.ts` read Demoed records through `mcf.fn_demoed_record_qualifies` (0076:544-562) and need no change. Request certification does not read the Demoed gate (no reference in `registry/mcf/request-audit-outcome.ts`).

## 7. In a disagreement, the documents decide

### 7.1 The rule

When a test fails, neither calculation outranks the other. The engine's value and the world's value are each a count or a sum of **documents**. The disagreement is settled by those documents:

1. **Both sides list the documents they counted**, for each differing cell.
2. **The lists are compared.** The documents on one list and not the other are the difference.
3. **A person opens each differing document in Odoo** (the world's own system) and judges it against the owner's plain-language definition of the metric in the Metric Directory (the member's definition, for example MDM-11fab0 for customer invoice volume).
4. **The judgement is recorded** in the failure resolution (5.1 item 4): which documents, the definition used, why, and which side is fixed. The ticket carries the discussion; the resolution carries the decision.
5. **Either side may be the one fixed.** If the engine (or the contract) is wrong, the fix is a new metric version, or an engine change, followed by a new test. If the world's answer is wrong, the fix is a corrected working-out in the study and a corrected hand-over, followed by a new test. Both may be wrong.

### 7.2 Can each side list its documents today?

**The engine: not from its own records.**

- The proof keeps each cell's value (`demo.ms_snapshot.result_decimal`), the count of records it consumed and a digest of their lineage (`demo.metric_proof_input.co_row_count`, `lineage_set_sha256`), and an Evidence hash over the cells (0078:247-253). It keeps no list of the documents each cell counted.
- The canonical records themselves are kept and readable, with `invoice_number`, `posting_date`, `fiscal_period` and `document_type_code` (columns of `demo.co_cc_das36_v5_1_0`, read live).
- The coverage checker already classifies them per exact cell and per declared rule (`demoed-coverage-checker.ts:125-134, 250-260`), so a per-cell list can be read today. But that list mirrors the engine's rules (`clauseHolds`, :215); it is not the engine's own record of what it counted.
- Under Invariant VI the list must be emitted by the evaluation itself: 5.2 item 4 and E13.

**The world: no.**

- Each working-out returns exactly one number: the runner refuses anything but "one row with one column" (bc-demo `ops/answer-sheet/run_sheet.py:19-20, 75-77`), and the customer invoice volume query is a `count(*)` (`…/sql/customer-invoice-volume-first-working.sql`).
- Proposal: beside each working-out, a committed **list query** with the same conditions that returns the documents (Odoo `account_move` id, name, date, type, state), run by a new list mode of the runner on the same frozen bench, inside `BEGIN READ ONLY`, with its output committed with its hashes.
- Assumption to confirm: the engine's `invoice_number` is Odoo's `account_move.name`, so the two lists can be joined.

**Binding the lists (rule B6).** Both lists, and their hashes, are bound to the exact cell, the run, the world binding, each source document's identity and, for a sum, each document's contribution amount. The engine's list comes from its own evaluation act (5.2 item 4). The world's list comes from reviewed, committed query bytes on the frozen bench, and neither its values nor its membership come from the evaluator or its contract-generation path (ADR-025bfc T4). **The mapping from Odoo documents to canonical documents is proven before any set difference is used.** Until it is proven, the two lists are shown side by side and no document is called "missing" from either.

### 7.3 The world's guards today, and the gap they leave

The demo world's answers are guarded by:

- **The frozen bench.** A read-only restore of one Odoo pg_dump, identified by its sha256 (`d0a33f41…`), restored with `default_transaction_read_only=on`; every query runs inside `BEGIN READ ONLY` (`run_sheet.py:66-71`).
- **No AI and no BareCount object.** The runner "reads no BareCount database or object, calls no model and generates no SQL" (`run_sheet.py:5-7`).
- **L4 only.** Only a study row rated L4, meaning two independent working-outs that agree, is accepted (`run_sheet.py:26, 93-95`). For customer invoice volume the two agree for FY2026-27 P01 to P05 (`…/sql/customer-invoice-volume-workings-2026-11-23.out`).
- **Reviewed commits and hashes.** Every input is read from the committed HEAD, never the working tree (`run_sheet.py:22-25, 83-91`). The sheet is merged through a reviewed bc-demo pull request before it is handed over. The database hashes the bytes and records who handed what over and when (0075; bc-demo `ops/answer-sheet/README.md`, "The path" and "Two hashes").

**The gap.** All of these guard against a wrong copy, a changed query or an invented value. None guards against a **shared misreading of the definition**: two working-outs, and the engine's contract, can all read "customer invoice" the same wrong way and agree. The study itself records one limit: its two working-outs come from two models of one family (study `customer_invoice_volume-fe91c450.md`, "The working-outs (L4)"). Only the documents, read against the owner's own words, settle such a case. That is why section 7.1 asks a person to judge them, and why a test that passes is still open to a later re-check.

### 7.4 A world-side fix cannot be handed over today (out of scope)

Expected values are one immutable row per (world code, metric, version, legal entity, period) (`uq_demo_oracle_custody_cell`, read live), and a second hand-over of a cell is refused (0075:400). So a corrected world answer for the same version cannot be recorded today.

The coherent route is a superseding hand-over that keeps the old answer and records the new one, with the resolution as its reason. Its custody, its selection of the current answer and its proof-currency rules need a separate design and the owner's own database yes (rule B8). This design does not cover them. Until then, a world-side fix needs a new metric version or a new world code. The route is an owner question (section 14).

## 8. The flag, the ticket and the lock

**The flag.** A version is flagged while it has a failed test with no resolution. The flag is computed from the records when they are read; nothing stores it.

**The ticket.** One per failed test, in the platform's support tickets (bc-admin `/platform/tickets/:ticketId`, `components/AppRouter.tsx:297-298`). It names the metric, version and test, and the differing cells with both values, and later holds the two document lists. The ticket's status never releases the lock.

**The lock, OPEN for the owner.** What a failed test holds until a person records a resolution:

| Option | What it holds | What it does not stop |
|---|---|---|
| **L1 (recommended)** | No new approval (activation) of the flagged version (c17). | Serving an active version's values; a new, corrected version; more tests. |
| L2 | L1, plus no new tenant binding of the flagged version. | Values already served to bound tenants. |
| L3 | L2, plus the version's values are shown to tenants marked "under review". | Serving the values. |
| L4 (ruled out) | Stops serving the version. | Listed only to rule it out: the owner ruled out any automatic switch-off. |

**L1 and an already active version (OPEN, rule B10).** L1 does not constrain a version that is already active when a re-check fails: it holds nothing new, because the version is already approved. The flag and the ticket still show. The owner settles this consequence before any lock is built: accept it, or choose L2 or L3 for that case. Where a tenant binding would be refused under L2 was not located (section 15).

Whatever the choice, the flag and the lock are read only from the immutable result and resolution, never from the ticket's status (rule B9).

## 9. The Tests column

**Screen.** The bc-admin **Metric Catalog** page, `src/pages/MetricCatalogPage.tsx`, route `catalog/metrics` (`components/AppRouter.tsx:203`). It reads `GET /api/mcf/metric-contracts` (`src/api/mcf-catalog.ts:67-70`). Its columns today (header comment and lines 193-249) are Metric ID, Metric Name, Function, Sub-function, Type, Description, Declaration chain and State. **Tests** goes between Declaration chain and State.

**What it shows**, for the metric's current version:

| Records | Cell shows |
|---|---|
| no test | "No tests" |
| only passed | "3 passed", with a small mark "covers every rule" when one passed test had complete coverage |
| an open failure | "4 passed, 1 failed" with a flag that links to the ticket (`/platform/tickets/:ticketId`) |
| failures, all resolved | "4 passed, 1 failed (resolved)", with no flag |

A count-pill filter "Flagged" sits beside the State and Declaration chain filters. The detail page (`src/pages/MetricDetailPage.tsx`, route `catalog/metrics/governed/:metricContractUid`, `AppRouter.tsx:204`) lists every test: time, verdict, coverage, the Demoed record it wrote, the ticket and the resolution. The new list fields go on `McfMetricContract` (`src/api/mcf-catalog.ts:14`). Verdict labels come from a master hook, not a hard-coded list (coding standard 14).

## 10. What changes in the two onboarding guides

**Prove a metric version on the demo world** (`docs/onboarding/prove-a-metric-version-on-the-demo-world.md`):

- Step 1 (:89): the world label holds every month the world holds data for.
- Step 2 (:104): the study works out **every month** for the metric (cost, section 11).
- Step 3 (:118): hand over every month.
- Step 4 (:134-146): declare every month; the new refusal `declared_cells_not_world_months`.
- Steps 10 to 12 (:223-264): step 12 becomes **Record the test's verdict**, written for a pass or a failure, with the new codes in its failure modes.
- Step 13 (:267): read the tests and the Demoed record.
- A new section, **Re-check**: steps 10 to 13 at any time, also after approval.
- A new section, **When a test fails**: the flag, the ticket, the lock, the two document lists and the judgement (section 7).
- Troubleshooting (:283-306): add `declared_cells_not_world_months` and `value_mismatch`.

**Certify and activate a metric version** (`docs/onboarding/certify-and-activate-a-metric-version.md`):

- Step 6 inputs (:158): a current Demoed record from a passed test with complete coverage and, under L1 or stronger, no unresolved failed test.
- Step 6 failure modes (:163) and troubleshooting (:198): add `c17_unresolved_failed_demo_test`, cured by a resolution, or by correcting the metric in a new version.
- Step 7 (:166-175): the read-back shows the tests and the one the approval relied on.

## 11. The cost: every month, for every metric

**The values do not come out automatically.** What runs today:

- **The periods are listed by hand.** The runner reads them from the manifest: "periods[]: {period_label, date_from, date_to}" for each entry (`run_sheet.py:16-17`). It runs the query once per listed period (`run_sheet.py:99-108`). Nothing works out the period list from the bench.
- **Once a metric's query exists, more months cost nothing to work out.** The query takes the dates and the company as variables (`customer-invoice-volume-first-working.sql`, header lines 1-5). Listing 41 periods instead of 4 yields 41 values with no new working-out.
- **The second working-out is not run by the runner.** The runner runs one `query_path` per entry (`run_sheet.py:96-108`). The second, independent working-out and the comparison of the two, which make a row L4, are a study act done for each metric. For customer invoice volume that was done for five months only (`…-workings-2026-11-23.out`).

So, for every metric, the study must run its second working-out over every month and record the agreement before the hand-over. The answer sheet grows from a few cells to every month: 41 for Kaveri today. A small runner change would remove most of the hand work: build the period list from the world's declared months (5.2 item 1) and run both working-outs, comparing them. This change is proposed, not designed here.

## 12. Customer invoice volume as the first use

**Why a fresh version.** Declaration `f41bcda2` covers 4 months and is immutable and one per version (0076:121), so version `b9357731` can never be declared over every month.

**The exit (grounded).** bc-db 0080 is applied live (`mcf.withdrawn_version_retirement` exists, read live). Its door is `POST /api/mcf/metric-contract-versions/:metricContractVersionUid/withdraw-retire` (bc-core `registry/mcf/mcf-mcv-withdraw-retire.controller.ts:53,60-61`, role `mcf_publisher`).

0080's record guard (0080:17-19) requires:

- the version to be audit_pending and not current;
- no active or current child;
- a decision-stream head that is NULL or PASS;
- no admit certificate;
- an unarchived parent;
- no unarchived directory member realized to the parent;
- a recorded desk grant (0080:15-16).

Read live for `b9357731`: `audit_pending`, `is_current` false, the parent's only version, the parent not archived, and no unarchived member realized to `fe91c450` (count 0). The decision head and the certificates were not read here; the door re-checks them.

**What the exit does.** A withdrawal record must commit with its parent **archived** in the same transaction (0080:24-25, item 5a). So the fresh version is a fresh metric contract and version, authored again from directory member MDM-11fab0. The same was done after the 0079 reset (bc-demo study `customer_invoice_volume-fe91c450.md`, "Why there is a second trace"). The old contract, version, declaration and pin stay on record.

**The steps.**

1. Withdraw-retire `b9357731`, under a recorded desk grant.
2. Author and approve the fresh contract and version from MDM-11fab0 (the metric guides).
3. In the study, run both working-outs for every month the world holds data for and record their agreement as L4. By the canonical records, that is FY2023-24 P01 to FY2026-27 P05, 41 periods for KAVERI-IN; the world's own declaration (5.2 item 1) decides.
4. Hand over all of them under the new contract uid.
5. Add a world label with the 41 period-end dates, and the metric's pin on it (E8).
6. Declare the 41 cells, then evaluate, prove and record the verdict.
7. Request certification, run the panel, and approve, naming the test.

**What the test then exercises.** The document-type rule can pass and exclude rows: 30 of the 2,714 invoices are not customer invoices, all in FY2023-24 to FY2025-26 (read live). **But under coverage v2 the time-gate element is uncovered when every month is declared (section 4), so w10 refuses this test until checker v3 (E12) is served.** E12 is therefore on the first use's critical path.

## 13. Foundation gate

**1. Why this location.** **B, contract semantics, enforced at E.** The defect is in what the Demoed declaration means, which today is a hand-chosen scope. The repair defines it as the world's full months, checked where 0076 checks the declaration. The test record, the mismatch record and the judgement are evidence the act emits (E). The Tests column (F) only surfaces records.

**2. Why not an upper layer.** At A, the world's records, its admission and its hand-over (0075) are sound. The one addition at the source, the world declaring its own months, is the world stating a fact about itself; it compensates for nothing.

**3. Why not a lower layer.** A fix below would be compensation: a new version only to change months, a label that hides months, or a reader that ignores w10. This design keeps the routine, its checks, the Demoed record, the attestation and c16, and keeps 0076's one-declaration rule.

**4. Design act or execution act (DEC-c48b0f).** **Design acts**:

- the declaration's scope ("every month the world holds data for");
- the missing record of a failed test;
- the missing record of which documents were counted;
- the missing rule for who settles a disagreement (the documents).

The flag, the ticket and the Tests column are a net, not the fix. Checker v3 (E12) is an execution-plane correction of how one coverage element is witnessed, needed because the new declaration removes the old witness population.

**Invariants kept, and how.**

- **III, all state is immutable.** Every new record is append-only. A re-check is a new run, and a resolution is a new row. The one-declaration rule is unchanged. A world-side fix would be a superseding row, never an overwrite (7.4).
- **IV, all references are explicit.** The approval names the Demoed record; the test result names its pin and its record; the resolution names its failure, its two document lists and the directory member used.
- **V, evaluation is non-replayable.** Each test is its own evaluation with its own pin. A re-check is a distinct act, never a reconstruction of an earlier one (5.2 item 3). The world's values are compared, never used in a calculation.
- **VI, evidence is emitted, not inferred.** Today a failed or partial test leaves no record, and no side keeps the documents it counted. Under this design the verdict, the elements, the mismatch and the per-cell documents are written by the acts themselves, and the world's months are declared by the world rather than inferred from the platform's records.

## 14. Open questions

The auditor's reply leaves four owner decisions open: the runner role, the lock extent, the resolution authority and the corrected-answer route.

1. **Who may run a re-check**: the metric publisher (`mcf_publisher`); a separate checking role; any of several roles, always recorded; or a scheduled re-check.
2. **What the lock holds**: L1, L2 or L3 (section 8).
3. **L1 and an already active version**: L1 does not constrain a version that is already active when a re-check fails. Accept that, or choose L2 or L3 for that case (section 8, rule B10).
4. **Who judges the documents and records the resolution.**
5. **The route for a corrected world answer**: a superseding hand-over (its own design and database yes), a new metric version, or a new world code (7.4).
6. **The world-month manifest's source population**: which records make "the world holds data" for a month (3.2, rule B7). Months with zero qualifying documents for a metric are included either way.
7. Whether approval names one passing test (this design) or every passing test.

Settled since revision 2: re-check at any time (R2; 5.2 item 3, rule B1).

## 15. Out of scope, known limits, and what was not grounded

**Coverage v2 limits, recorded and not changed:**

- `computed_dimension` and `conditional_branch` elements are always uncovered ("not derivable", `demoed-coverage-checker.ts:25, 352-354`), so a metric with a computed dimension or a `case` node can never reach complete coverage.
- `grain_partition` needs two or more legal entities among the proven cells (:24, :330), while w3 allows one legal entity per declaration (0076:408-411, R3: one proof pin covers one legal entity). A metric scoped by legal entity can never be complete today. For a world with several legal entities, "every month for every legal entity" also meets this one-legal-entity rule. Kaveri has one legal entity.
- A time gate other than `period_aggregate` or `as_of` is uncovered.

**Out of scope:**

- A corrected world answer (a superseding hand-over): its custody, current-answer selection and proof-currency rules need a separate design and the owner's own database yes (rule B8).
- A route for worlds with several legal entities: the writer covers one legal entity, and no full-world coverage is claimed through one entity's pin (rule B7).

**Not grounded in this design:**

- whether the engine's dry evaluation exposes the canonical records each cell counted (E13);
- that `invoice_number` equals Odoo's `account_move.name` (7.2);
- the bench's own month range (the bench was not restored here; 41 periods is the canonical records' count);
- the decision head and certificates of `b9357731` (12);
- where a tenant binding would be refused under L2;
- the allowed values of `support.ticket.category_code` (the `support` schema is not readable with the tool used);
- the status the demo emit should record for a mismatch (5.2 item 2).
