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

*Design note · proposed 2026-11-24, revision 7, amendment 1 (2026-11-24, after landing at bc-docs c948683c) · nothing in this note has been built or run. Its database changes are a proposal: they need the owner's explicit yes under the Database Change Protocol before any migration is written.*

Evidence base, read at these heads on 2026-11-24: bc-db `origin/main` 18d6884, bc-core `origin/main` df47ce00 (the served engine), bc-demo `origin/main` 428ab310, bc-admin `origin/main` 6267a64, bc-docs `origin/main` 96487a5. Live rows were read read-only on `bc_platform_dev` on 2026-11-24 with the read-only database tool. Paths in bc-core are under `src/` unless shown otherwise.

Revision 2 follows two later rulings of the owner (section 2). Revision 1 let each test choose its own months; that is withdrawn. Revision 3 folds in the auditor's boundary as design rules (section 3.5). Revision 4 records the owner's settlement of the seven open questions as rules S1 to S7 (section 14) and lists the database changes for his yes (section 16). Revision 5 adds the owner's ruling that a test uses what customers use: the same arithmetic and the same versions (section 3.6). Revision 6 fixes the four blocking findings of the auditor's second reply (bc-external-audit `docs/RESPONSE-Codex-gen-3a7aae-02-open-repeatable-demo-tests-design-rev-2026-11-24.md`, commit 331d0fb7, CHANGES REQUIRED, reviewed at head c71519c5) under the owner's "Yes, fix all four". It also adds the owner's principle of one demo world per source type (DECISIONS b13068d5; section 3.7). Revision 7 answers the auditor's third reply (bc-external-audit `docs/RESPONSE-Codex-gen-3a7aae-03-open-repeatable-demo-tests-round3-2026-11-24.md`, commit ce0facd0). That reply closes findings 1, 2 and 4 and keeps finding 3 blocking. Revision 7 changes only the time-gate evidence (5.2 item 4, E12, E13) and adds the reply's implementation notes as boundaries (section 3.8). The auditor's answer is ACCEPTED WITH BOUNDARY: bc-external-audit `docs/RESPONSE-Codex-gen-3a7aae-01-open-repeatable-demo-tests-design-2026-11-24.md`, commit 504b5bd0, reviewed at head 88b0c35d. It accepts the design direction only; no database change, landing or onboarding follows from it.

**Amendment 1** follows the owner's ruling that the platform is system-agnostic (DECISIONS bf0101cf, 22:21 IST; bc-docs `docs/overview/structural-differentiators.md:54-58`). A metric is proven once, on any demo world; a source mapping is proven per source type in a separate design (section 3.7). It:

- removes canonical-version equality and every source-type dimension from the metric's approval gate;
- keeps the canonical versions a test read as evidence only;
- folds in fixes 1, 2, 3, 6 and 8 of the independent Foundation check;
- names four separate design acts (section 15);
- restates section 16 with the builder's grounded shapes and marks what differs from the owner's two database yeses (8558dc9f, 0bfc5aa4).

## 1. The problem in plain words

To be approved, a metric version must give the same answers as the demo world. Today the platform fixes, once per version, the months on which this is shown. The choice is made by hand, and a version cannot be tested again on the same records.

That is what happened to **customer invoice volume** (metric contract `fe91c450`, version `b9357731`, state `audit_pending`):

- Its declared months are FY2026-27 P01 to P04 for KAVERI-IN (declaration `f41bcda2`, 4 cells, read live).
- The platform's answers matched the demo world's own answers in all four: 60, 58, 62 and 67 (proof pin `00f5f597`, comparison `match`, read live).
- The proof was still refused, correctly. The metric counts only documents whose type is "customer invoice", and none of the four months holds a credit memo, so that rule was never put to the test (check w10, coverage).
- The demo world holds credit memos in other months. Its canonical records hold 2,714 distinct invoices for KAVERI-IN over 41 fiscal periods, FY2023-24 P01 to FY2026-27 P05, and 30 of them are not customer invoices (read live from `demo.co_cc_das36_v5_1_0`, which keeps one copy per world binding since 0081, so 5,428 rows).

The owner's answer: no one chooses months. Every test covers every month the world holds data for. A test can be repeated at any time. Every result is kept.

## 2. The owner's rulings

Recorded in barecount-devhub branch `claude/operator-review-content`, `artifacts/operator-review/DECISIONS-workflow-review.md`, the entries of commits 98190a23, afbe5758, dd311fe2, 32202aea, fc92dd64, 752c345c, cd335caa and b13068d5.

1. **Tests are open, repeatable and all kept** (20:05 IST). Every test is kept, pass or fail. Approval names the test it relies on. A re-check is allowed at any time, also after approval. Before approval, at least one passing test must exercise every rule of the definition. A failed test flags the metric: a person decides, and nothing switches off by itself. It also opens a ticket and applies a lock. The metric list gains a Tests column.
2. **Every test covers every month the demo world holds data for** (afbe5758). The owner: "Instead of adding functions/actions let us make it mandatory to select all months available in demo world. Simple." Asked whether he means the months the world holds data for or the months it has handed over: "every month the world holds data for". So there is no choosing of months, no test on part of them, and 0076's rule of one declaration per version stays.
3. **In a disagreement the documents decide** (dd311fe2): "agree, documents decide. update the design". On a mismatch, each side lists the documents it counted. A person opens the differing documents in Odoo and judges them against the owner's plain-language definition. The judgement is recorded, and either side, the engine or the world, may be the one fixed.

4. **The seven open questions, settled as recommended** (32202aea, recorded 2026-11-24 20:40 IST: "Yes, as recommended"). They are rules S1 to S7 in section 14.
5. **A test uses what customers use: the same arithmetic and the same versions** (fc92dd64, recorded 2026-11-24 20:50 IST). The owner: "add the arithmetic fix to the design. Also demo must switch to latest version (like customers forced to) otherwise they will differ". These are rules A1 to A4 and V1 to V6 in section 3.6. The owner confirmed the Chief's reading (752c345c, recorded 20:52 IST): "yes, that's what I meant".
6. **One demo world per type of source system** (b13068d5, recorded 21:18 IST). The owner: "fundamentally we should WILL be doing one demo world or similer for each type of source system once." Amendment 1 places this principle in the mapping proof, not in the metric test (section 3.7).
7. **The platform is system-agnostic: a metric is proven once; a source mapping is proven per source type** (bf0101cf, recorded 22:21 IST). The owner: "I think something is slightly off. You are missing subtle foundation limit (and our core differentiator) that platform is system agnostic." On the Chief's correction (two proofs), the owner: "agree, amend the design." Fixes 1, 2, 3, 6 and 8 of the independent Foundation check are folded in. Fix 7 and the builder's item 6 (the source-type table) fall away. Fixes 4 and 5, the observation-to-source-contract declaration gap and the mapping proof are separate design acts. The amended database shapes need the owner's database yes again before the builder restarts.

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

**Proposal.** The world declares its own months, the same way it hands over its answers: a **world-month manifest**, derived and sealed from the frozen source (rule B7). One immutable row per (world binding, legal entity, fiscal period) is worked out on the frozen bench by a committed, reviewed, read-only query. Its two definitions (rule B7), settled by the owner (rule S5, 32202aea):

- **The source population.** A month counts as "the world holds data" when the demo world has **posted accounting entries** in it for the company. On the frozen bench that means at least one Odoo `account_move` with `state = 'posted'` for the company, of any move type.
- **The period and calendar mapping.** An entry's accounting date (`account_move.date`, the date the study's working-outs already use, `customer-invoice-volume-first-working.sql` lines 1-5) maps to the legal entity's fiscal period through its declared calendar (KAVERI-IN: IN-APR-MAR-MONTHLY).

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
- under lock L1 (section 8, rule S2), no failed test of this version that a person has not yet resolved;
- the arithmetic of the cited test matches what the serving runtime uses at the act (A2).

The canonical contract versions the test read are recorded as evidence (V6). They do not gate approval: the metric reads only canonical vocabulary, so a pass holds for every source (section 3.7).

All of these sit in **one shared gate** that the database applies on every route to active or current (rule G1, section 3.6).

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
- **B8. A corrected world answer is out of scope here.** It would be a superseding hand-over that keeps the old answer. Its custody, its current-answer selection and its proof-currency rules need their own design and the owner's own database yes (section 15; rule S4).
- **B9. Ticket recoverable; records decide.** A ticket is created, recoverably, for each failed result. The immutable result and resolution decide the flag and the lock, never the ticket's status.
- **B10. L1 and an active version.** As L1 stood in revision 3, it did not constrain a version that was already active when a re-check failed. The owner settled this: L1 applies to an active version too (rule S2).

### 3.6 A test uses what customers use

**Owner-confirmed** (fc92dd64; the reading confirmed in 752c345c). Revision 6 makes the rules complete, as the auditor's second reply requires (gen-3a7aae-02, findings 1, 2 and 4).

**Grounding: the arithmetic.** The demo proof and a tenant evaluation share one engine call, `runEngine` (bc-core `boundary/governed-metric-evaluation.service.ts`; the dry evaluation at :332-341, the tenant act at :386-388). The arithmetic is chosen by each running program:

- `selectEngine` (:324-325) runs `FormulaExecutionEngineV3` when the program's numeric profile is `scaled-decimal-int-v1`, and the legacy `FormulaExecutionEngine` otherwise.
- The profile is read once, when each program starts, from the environment variable `BCCORE_NUMERIC_PROFILE` (`config/metric-runtime.config.ts:26, 45-53`, `registerAs`), through the single fail-closed getter `numericProfileOf` (:41-43). An absent value means scaled; only the literal `binary64-v1` selects the rollback (:32-38). So within one running program the profile cannot change.
- The demo proof command and the served bc-core are separate running programs, so they can differ.
- Today nothing records which arithmetic a proof ran with. The pin records only `engine_build_id` (`demo.metric_proof_pin`, 14 columns, read live).
- A tenant evaluation adds its profile report to the run's lineage only under the scaled profile (`boundary/governed-metric-persistence.adapter.ts:475-487`; "Absent under binary64-v1"), so tenant history cannot show which setting the served runtime uses.

**Rules: the arithmetic.** The authority is **the serving runtime's own value at the act** (finding 2, option "use the actual serving runtime's value").

This option is the simplest sound one. The profile is fixed for the life of a running program (`registerAs` at start). So the program that performs an act knows, with certainty and without any liveness proof, the arithmetic it would serve with. A startup record would have to be tied to a live instance and build and proven at each comparison, which adds a table, a staleness rule and a race, and still answers less directly. Revision 5's `metric_audit.served_numeric_profile_event` and its check w11 are therefore dropped.

- **A1. Recorded on the run.** The proof pin is extended, not paralleled: `demo.metric_proof_pin` gains `numeric_profile_code`, written by the emit from the value the proving program's own `numericProfileOf` returned for that evaluation. Each test result copies it from the pin, never from the caller, together with `engine_class_code`. A CHECK pairs the two (`scaled-decimal-int-v1` with `formula_engine_v3`, `binary64-v1` with `formula_engine_v2`), as `selectEngine` pairs them.
- **A2. The approval compares with its own value.** The admit acts run inside the served bc-core (`registry/mcf/mcf-admit.controller.ts:62-63, 123-124`). Each compares the cited test's profile with its own `numericProfileOf`, then records what it saw in a new `metric_audit.transition_evidence.served_numeric_profile_code` column. The database's shared gate (G1) refuses when the two differ: condition `c18_test_arithmetic_not_served`.
- **A3. Serving compares with its own value.** Every tenant evaluation act (`GovernedMetricEvaluationService.evaluate`, :343, before `runEngine` at :388) reads, without evaluating, whether the version it serves has a passed, complete test with **its own** profile. If not, the act records a refusal `arithmetic_not_tested` and writes no new snapshot, through the existing recorded-refusal path (`refuseDefect`, as at :362). Snapshots already written stay readable. So a profile change stops changed arithmetic from serving new values until a fresh test under it passes. The Tests column shows "re-check due (arithmetic)".
- **A4. The Demoed record records the arithmetic.** It does not judge the serving setting: the writer runs in the proof command's program, which is not the serving program. The pin's profile reaches the test result (A1). Approval (A2) and serving (A3), which run in the serving program, decide.

Required tests (fixtures):

- **(a)** The serving program starts before the test with the scaled profile; a scaled test passes; the admit is accepted.
- **(b)** The test runs first and the serving program starts afterwards, scaled; the admit is accepted. The two orderings give the same answer, because no startup record is read.
- **(c)** The serving program restarts from scaled to `binary64-v1` after activation. Every tenant evaluation of that version records `arithmetic_not_tested` and writes no snapshot. The admit of any version tested only under scaled is refused with c18. A `binary64-v1` re-check that passes restores evaluation.

Consequence, stated plainly: `binary64-v1` is the explicit rollback (`metric-runtime.config.ts:5-13`). Under A3, a rollback holds back new values of every metric until each one is re-checked under it.

**The versions, amended** (bf0101cf). A metric reads only canonical vocabulary (`docs/overview/structural-differentiators.md:54-58`). So which canonical contract version produced the records is a property of the **source mapping**, not of the metric, and it is proven by the mapping proof (section 3.7), not by the metric's approval. Revision 6's rules V3 (two-way canonical equality at approval), V4 ("re-check due" on a canonical supersession) and V5 (the tenant route for canonical inputs in a test), and condition c19, are **removed** from the metric's gate.

What stays:

- **V1. A re-check runs on the current metric version.** A re-check of an active metric names its current active version, never an older pin (`boundary/metric-spec-loader.ts:110` takes the world label's pinned version today; the test names the version instead, E17).
- **V2. A candidate is tested itself.** Before approval, the candidate version itself is tested.
- **V6. The canonical inputs are recorded as evidence only** (Foundation VI, evidence of context):
  - The evaluation act emits the role-keyed set of canonical inputs it read: `grain` (`boundary/co-candidate-reader.ts:337-346`), `schedule_event` (`boundary/metric-evaluation-orchestrator.service.ts:340-360`) and `field_declarations` (`boundary/metric-spec-loader.ts:266-268`).
  - Each entry names the canonical contract by `canonical_contract_id` and `version_code`, the key of `contract.canonical_contract_version` (primary key `(canonical_contract_id, version_code)`, read live).
  - The demo side records it in `demo.metric_proof_input`, which gains `canonical_contract_id` (5.2 item 7). The platform side copies it into `mcf.metric_version_demo_test_cc_version` (5.1 item 2b), so the record can be read without `demo.*`.
  - The writer refuses a set with a missing role or a duplicate role. A test whose set omits the `schedule_event` input of a schedule metric is refused as malformed evidence (a fixture).
  - **The record does not gate approval.** It shows which canonical versions the passing test read.

**Grounding kept for the separate design act on canonical selection** (section 15): cc-das36 has two `active` versions, 3.0.0 and 4.0.0 (`contract.canonical_contract_version`, read live). A tenant takes the newest by a rule that lives only in code (`pickGrainCc` with `newestVersion`, `boundary/co-candidate-reader.ts:137-155`). The demo world label pins 5.1.0 (`pending_provisioning`). Customer invoice volume's only proof ran on 5.1.0.

**Rule G1: one shared gate at every route to active or current** (finding 4). Every route that can make a version `active` or current, read at bc-core df47ce00 and on the live trigger:

| Route | Where | Today | Under this design |
|---|---|---|---|
| Admit (`audit_pending → active`) | `admitMetric`, `mcf-cert-writer.service.ts:2907, 2945-2993` | Customer-current: the trigger sets `is_current` | gated by G1 |
| Readmit a corrected version (`audit_pending → active`) | `readmitCorrectedMetric`, :3026, 3062-3141; route `mcf-admit.controller.ts:123-154`; also `metric-audit-workflow.service.ts:263` | Customer-current | gated by G1 |
| Direct activation (`approved → active`) | `activateMetric`, :2602-2612, throws `DirectActivationRetiredError`; its body `activateMetricInTx` (:2500-2540) has no caller (searched at df47ce00); the live trigger has no `approved → active` edge | Unreachable | gated by G1 anyway, should the edge ever reopen |
| Restore after corruption (`superseded → active`) | `restoreCorruptedMetric`, :4285-4335; route `mcf-mcv-restore.controller.ts:62` | Refused by the database: the live trigger has no `superseded → active` edge | gated by G1 anyway |
| Supersession | `supersedeMetricInTx`, :3368-3395 | Moves only the predecessor `active → superseded`. The successor must already be `active` and current (`validateSupersedeLockedRows`), so it reached that state through admit or readmit | no new current; nothing to gate |
| A direct change of the current pointer | `mcf.metric_contract_version.is_current` | The live trigger `trg_mcf_mcv_state_transition` fires only `BEFORE INSERT OR UPDATE OF governance_state_code`, and sets `is_current` itself on `audit_pending → active`. The served login holds column `UPDATE` on `is_current` (read live), so a direct pointer write would bypass it. No bc-core code writes it (searched at df47ce00). | gated by G1: the trigger is widened to `UPDATE OF governance_state_code, is_current` |

The gate is one new function, `mcf.fn_customer_current_gate_refusal(uuid)`. It returns the named refusals:

- c16: Demoed and current;
- c17: an unresolved failed test;
- c18: the arithmetic.

Revision 6's c19 (the canonical input set) and its per-source-type rule are removed by amendment 1.

`mcf.fn_mcv_state_transition_check` calls it on **every** transition whose new state is `active` and on every change of `is_current` from false to true, and refuses when the list is not empty. `metric_audit.fn_intrinsic_decision_refusal` keeps c1 to c15 and appends the same function's list, so one body serves both. A route that writes neither the state nor the pointer cannot make a version current, so no route escapes the gate.

**Placement in the trigger.** The live body returns early when the state does not change (`IF OLD.governance_state_code = NEW.governance_state_code THEN RETURN NEW;`, read live). The shared gate sits before that return (3.8).

### 3.7 System-agnostic: two proofs

The owner's ruling (bf0101cf) separates two proofs:

1. **The metric is right.** A metric binds Business Concepts, never source fields, and reads only canonical vocabulary (`docs/overview/structural-differentiators.md:54-58`). So it is proven **once, on any demo world**. A passing, complete test holds for every customer on every source system while that metric version is unchanged. This design is that proof. It has no source-type dimension: one Tests count per version, one approval rule, no per-source row.
2. **The source mapping is right.** For each source type, does the source's canonical contract version produce correct canonical records from that source's documents? This is proven per source type, on that type's demo world, under the owner's principle of one demo world per source type, built once per type (b13068d5). It is a **separate check in a separate design**, out of scope here (section 15).

Fix 7 of the Foundation check and the builder's item 6 fall away with this. The planned platform table of source type to demo world would have duplicated `demo.foundry_world_binding_connection.source_system` (read live: `odoo` on every connection of binding `e32071a8`), and its seeded row would have been a write outside a governed act.

### 3.8 Implementation boundaries from the auditor's third reply

The third reply (gen-3a7aae-03, commit ce0facd0) closes findings 1, 2 and 4 at the design level and gives these notes. They bind the implementation:

- **Canonical inputs (finding 1).** Two fixtures are required at implementation:
  - a test whose set omits the `schedule_event` dependency of a schedule metric is refused;
  - (amendment 1: the concurrent canonical activation fixture belonged to c19, which is removed; it moves to the canonical-selection design act, section 15.)
- **Serving arithmetic (finding 2).** A rollback to `binary64-v1` holds back new values of every metric until each is re-checked under it (rule A3). This is an explicit implementation boundary, not an accident.
- **The shared gate (finding 4).** The live trigger body returns early when the state does not change: `IF OLD.governance_state_code = NEW.governance_state_code THEN RETURN NEW;` (`mcf.fn_mcv_state_transition_check`, read live). An update of `is_current` alone takes that path. So the shared gate (G1) is placed **before** any same-state early return, and a direct pointer update is checked.
- **Source types (amended).** The metric test has no source-type dimension (3.7). The tenant-to-source-type mapping and shared observation contracts belong to the mapping proof's design, which must fail closed on them before any source type is claimed as mapped correctly.

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

**Status: a proposal for the owner's yes.** It is smaller than revision 1. No declaration rule is relaxed. Proposed as two bc-db forward migrations, numbers to be confirmed at authoring: **0082** for the demo side (`demo`), applied first, and **0083** for the platform side (`mcf`, `metric_audit`), applied second. On 2026-11-24 the highest merged migration is 0081, the only open bc-db pull request that claims a number is #177 (0073), and no bc-db branch carries a file numbered 0082 or higher. Each would be proven on an owner- and grant-faithful restore of a fresh read-only dump, including the served-login vectors, and applied only through the governed runner under a recorded desk grant. Rules followed: ISO 11179 names (DEC-69f09e), at most 20 columns, foreign keys on every in-plane reference, no JSONB for queryable data, indexes in the same migration (DEC-1918d0).

**Removed from revision 1:** choosing cells per test, the record-before-run check (w6b), tests on part of the months, the change of the answer-sheet match to inclusion, dropping `uq_metric_version_demoed_declaration_mcv`, the `void` verdict, and accepting `active` in the declaration guard.

### 5.1 The platform-side changes (migration 0083, applied second)

1. **The world-months check** (3.2): the commit check and w3 also require the declared cells to equal the world's declared months for the declared legal entity. A new read-only definer function `mcf.fn_demoed_declaration_covers_world_months(uuid)` is called as its owner, like the 0075 predicates.
2. **`mcf.metric_version_demo_test_result`**: one immutable row per test, 14 columns.

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
   | `numeric_profile_code` | text NOT NULL | copied from the pin by the routine (rule A1) |
   | `engine_class_code` | text NOT NULL | paired with the profile by a CHECK (rule A1) |


   **Same act as the pin** (Foundation fix 3). The result is written by the same proof command act that emits the pin, before the command returns, never by a later act:
   - the emit runs as `bc_demo_prover` (0078:79) and the writer as `bc_demoed_bridge_writer` (0076:365), two logins, so the two cannot share one database transaction;
   - the command reports success only when both exist;
   - a read lists every pin without a result (E18). Such a pin is completed by the same command, given that pin: the routine records the verdict from the preserved pin and never evaluates again.

   CHECKs tie the columns to the verdict. The version is reached through the declaration, so it is not stored twice. The table is immutable (update, delete and truncate are refused by the 0065 trigger function). No login holds INSERT; only the routine in item 5 writes it. SELECT goes to `bc_platform_runtime`.
2b. **`mcf.metric_version_demo_test_cc_version`** (5 columns: uid; result FK; `proof_input_role_code`; `canonical_contract_id`; `version_code`; a composite FK to `contract.canonical_contract_version (canonical_contract_id, version_code)`, cross-schema; UNIQUE on result and role). The role-keyed canonical inputs the test read, as **evidence only** (V6). Nothing gates on it.
3. **`mcf.metric_version_demo_test_result_element`** (7 columns: uid, result FK, `element_kind_code`, `element_ref_text`, `covered_flag`, `witness_count`, `witness_digest`; UNIQUE on result, kind and ref): the coverage elements of a passed test with **partial** coverage, which are lost today when w10 refuses. A complete test keeps its elements in `mcf.demoed_bridge_coverage_element`, as today. Same immutability and grants.
4. **`mcf.metric_version_demo_test_failure_resolution`**: the person's judgement of one failed test (section 7), 9 columns:
   - uid;
   - result FK, **UNIQUE**;
   - `corrected_side_code`: `engine`, `world` or `both`;
   - `engine_document_list_sha256` and `world_document_list_sha256`: the two lists the judgement compared;
   - `directory_member_uid_text`: the directory member whose definition was the yardstick, as text (the builder's grounded shape);
   - `judgement_text`: at least 40 characters, naming the differing documents and why;
   - `resolved_by_name`;
   - `resolved_at`, set by the database.

   An insert guard requires the result to be `failed`. Immutable. INSERT goes to `bc_platform_runtime` through a command (E10). The lock is released by this row, never by the ticket's status: `support.ticket` is a mutable working table (status and `updated_at`, bc-core `database/schema/support/ticket.ts:22,35`), and a lock must rest on an immutable record (Invariant III).
5. **One writer for every outcome**: `mcf.fn_record_demo_test_result(p_mcv, p_pin, …)`, SECURITY DEFINER, owned by `bc_schema_owner`, EXECUTE only to the existing producer login `bc_demoed_bridge_writer`. It keeps the inputs and the cross-plane read of `mcf.fn_record_demoed_bridge` (0076:337-353) and every one of its structural and identity checks w0 to w8 in their order (0076:364-483; rule B4), with these changes:
   - w4 no longer requires `match` (0076:433); every other w4 condition stays. The outcome is the verdict: `mismatch` is recorded as **failed** (`value_mismatch`, with the count of differing cells) only after w5 to w8 hold **and** the mismatch-safe hand-over predicate (5.2 item 6) holds. If that predicate fails, the act is refused and no result is written (rule B3);
   - w9 (`demo.fn_pin_answer_sheet_refusal`, unchanged) applies to a matched pin only;
   - the declared cells cover **one company** (w3's one-legal-entity rule, 0076:408-411, kept; rule S7);
   - w10 (0076:496-508): when partial, the test is recorded as **passed, partial**, with its elements, and no Demoed record is written; when complete, the 0076 write block (0076:510-535) writes the Demoed record, its elements, its provenance (writer version `fn_record_demoed_bridge-v2`, which the provenance check `^fn_record_demoed_bridge-v[0-9]+$` at 0076:309 accepts) and its `current` attestation, and then the result row naming it;
   - every other refusal still writes nothing.

   EXECUTE on `mcf.fn_record_demoed_bridge` (v1) is revoked from `bc_demoed_bridge_writer` in the same transaction that installs the new routine, so that one routine alone writes Demoed records and the two are never callable together (rule B4).
6. **The lock, L1, and the shared gate G1** (rules S2, G1):
   - A new function `mcf.fn_customer_current_gate_refusal(uuid)` returns c16 to c18 (3.6). The gate is called before the trigger's same-state early return.
   - `metric_audit.fn_intrinsic_decision_refusal` keeps c1 to c15 byte for byte and appends that list. c16 moves into the shared function. The live body is pinned by its md5 in the precondition, the way 0076 pinned it (0076:69-72).
   - `mcf.fn_mcv_state_transition_check` is replaced with two added rules, its other edges and gates copied byte for byte and pinned by md5:
     - any transition whose new state is `active`, and any change of `is_current` from false to true, is refused while the shared gate's list is not empty;
     - any change of state of a version with an unresolved failed test is refused (section 8).
   - The trigger `trg_mcf_mcv_state_transition` is recreated as `BEFORE INSERT OR UPDATE OF governance_state_code, is_current`.
6b. **Demoed only while no failure is open and the engine was never found wrong** (Foundation fix 2). `mcf.fn_demoed_record_qualifies` (0076:544-562) is replaced: it also returns false while the version has a `failed` result with no resolution, and after any resolution with `corrected_side_code` `engine` or `both`.
7. **Grants**: SELECT on the new tables to `bc_platform_runtime`; INSERT on the resolution table only. bc-core `tools/grant-drift/bc-platform-runtime-grants.tsv` (lines 124-134 record the 0076 grants) is updated in the same landing. The rollback is refused while any result, element or resolution row exists.

Amendment 1 removes from this side: c19, the canonical input fingerprint on the result and on the transition evidence, the source type on the result, and the source-type table.

### 5.2 The demo-side changes (migration 0082, applied first)

1. **The world's declared months**: `demo.world_binding_data_period` (6 columns: uid; `world_binding_id` FK; `legal_entity_id` FK; `period_label`; `answer_sheet_handover_id` FK to `demo.answer_sheet_handover`; `declared_at`), UNIQUE on binding, legal entity and period, and immutable. The months come in through the existing hand-over, `demo.fn_hand_over_answer_sheet` (0075:223), in a **v2** answer-sheet format that adds a months section. Format v1 is unchanged. The months are written **once per binding**: a second hand-over that carries months for a binding that already has them is refused. The file bytes, hash, locator, who and when stay on the hand-over row and are not copied.
2. **A mismatch is recorded.** The two emit routines (0078) are replaced so that, when every structural check holds, a value difference records the run, the evaluation, one snapshot row per cell (its value beside its custody reference), its Evidence and Lineage, and a pin with `comparison_outcome = 'mismatch'`. The structural checks are: a declared legal entity, custody for every cell, the cells equal to the scope, one current world binding, and lineage present. A cell with no custody row still raises. The evaluation status and the Evidence outcome for a mismatch are to be fixed at authoring. The matched path is unchanged.
3. **A re-check on unchanged records: R2** (rule B1; the auditor: R1 "would silently narrow" the owner's ruling). The per-act key becomes the caller-given `run_id` of `demo.metric_run`, unique per run. `uq_demo_metric_run__act` and the guard at 0078:224-229 and 445-450 change accordingly. A re-check on the same engine and the same records is a distinct act that gives a new run, a new pin and a new result (Invariant V allows this; it never reconstructs an earlier act). The former option R1 (re-check only after the engine build changed) is dropped.
4. **Each cell's candidates and why each was counted or rejected** (rules B5, B6; findings 3 of rounds 2 and 3; Foundation fix 6): `demo.ms_snapshot_candidate`, which replaces revision 5's `demo.ms_snapshot_member`. It has 14 columns, within the limit of 20:
   - uid;
   - `metric_snapshot_id` FK to `demo.ms_snapshot`, or `metric_snapshot_ccy_id` FK to `demo.ms_snapshot_ccy`: exactly one of the two, by a CHECK. It fixes the cell, the evaluation, the run and, through the proof input, the world binding;
   - `canonical_contract_id` and `version_code`: the canonical contract version that produced the record, named **explicitly**;
   - `co_store_code`: a locator only, never the source of the contract's identity;
   - the canonical record id and its content hash. No FK is possible across the per-version stores;
   - the source-document identity;
   - `candidate_disposition_code`: `counted`, `rejected_time_gate`, `rejected_filter` or `rejected_missing_input`;
   - `rejecting_rule_ref_text`: the gate shape for `rejected_time_gate`; the first failing clause for `rejected_filter`; NULL when counted;
   - `other_rules_passed_flag`: for a `rejected_time_gate` row, NOT NULL. It is the engine's own verdict, in the same evaluation act, on every other row filter of the spec for this candidate (E13). NULL on other rows. A CHECK ties it to the disposition;
   - `other_rule_failed_ref_text`: when that flag is false, the first clause the engine reports failing; NULL otherwise;
   - `contribution_amount`, set for a sum.

   UNIQUE on (cell reference, store code, canonical record id): one row per candidate and cell. So a record of month B appears as `counted` under its own cell and as `rejected_time_gate` under the cell of month A. The rows are written by the emit in the same transaction, from the evaluation act's own record of each candidate (E13), never from a later read. The set's hash goes into the cell's Evidence.
5. **A corrected world answer: out of scope** (rule B8). It needs its own design and the owner's own database yes (section 15).
6. **The mismatch-safe hand-over predicate** (rule B3): a new read-only definer function, `demo.fn_pin_handed_over_expected_cells_refusal(uuid)`. For a pin of either outcome it proves each expected cell, its value, its metric and version, and its world binding came from the world's own hand-over. It uses the membership, world-binding and custody-set-hash checks of `demo.fn_pin_answer_sheet_refusal` (0075:413-476), without that function's first `match` gate. It does not judge the engine's values; the routine compares those separately.
7. **`demo.metric_proof_input` gains `canonical_contract_id`** (10 to 11 columns; Foundation fix 6, V6). The existing row of pin `00f5f597` keeps it NULL: an immutable row is never rewritten. The emits refuse NULL on every new row. The role and store checks widen as in section 16.

## 6. What changes in the engine (bc-core), at every enforcement point

| # | Where | Change |
|---|---|---|
| E1 | `registry/mcf/demoed-declaration/declare-demoed-version.command.ts` (header :1-22) | Unchanged in shape (one per version). Its `check` reports the new database refusal `declared_cells_not_world_months`; the body's description (:64) says "every month the world holds data for". |
| E2 | `registry/mcf/demoed-declaration/demoed-declaration-refusals.ts` | Maps the new refusal. |
| E3 | `registry/mcf/bridge-record-writer.ts:94`, `demoed-evidence-bridge-cli.ts` | Call `mcf.fn_record_demo_test_result`; read the verdict it returns. |
| E4 | `registry/mcf/demoed-evidence-bridge.service.ts` (step 5 :369-382; reconcile :16-18) | A hollow or partial test is no longer refused before the routine; it is recorded as passed, partial. "Reconcile, never replay" stays, keyed by the pin. |
| E5 | `registry/mcf/demoed-bridge-writer-refusal.ts` | Maps the new routine's refusals and verdicts. |
| E6 | The demo proof command (proof guide step 11) | On a mismatch pin, record the failed result instead of stopping. |
| E7 | `registry/mcf/mcf-cert-writer.service.ts:1047-1058` (`assertCandidateDemoedInTx`, used by `admitMetric` at :2973-2974) | Under L1, a sibling check names an open failure before the database's c17 does. |
| E8 | `database/plane/plane-world-evaluation-coordinate.ts:40-52`, with `plane-cc-version-binding.ts:37`, `plane-metric-version-binding.ts` and `plane-world-identity.ts` | The world label's dates must be every month the world holds data for: for Kaveri, 41 period-end dates. This is one label per world binding, not one per test. |
| E9 | Ticket on failure (new; rule B9) | After a failed result, open a ticket through `SupportService.createTicket` with `entity_type = 'mcf.metric_version_demo_test_result'` and the result uid. The record comes first and the ticket second, and the ticket is recoverable. A read lists every failed result without a ticket, and an idempotent "open the ticket for this failed test" command can be run again until each has one. `boundary/boundary-ticket.service.ts:26-40` is fire-and-forget and never throws, which is not enough. The flag and the lock are read from the result and the resolution only. |
| E10 | Resolve a failure (new command) | Writes the resolution (5.1 item 4) after the documents are judged (section 7), with its written reason; comments on the ticket and closes it. Held by the owner or whoever approves metrics (rule S3): the admit route's role, `mcf_publisher` (`registry/mcf/mcf-admit.controller.ts:62-63`). |
| E11 | Reads: `registry/mcf/mcf-read.service.ts:512-530` (the list behind `GET /api/mcf/metric-contracts`, `mcf-publication-eligibility.controller.ts:30,70`) and `GET /api/mcf/metric-contract-versions/:mcvUid/demoed-claim` (`demoed-evidence-bridge.controller.ts:83`) | One set-based read of each current version's test counts and open failure with its ticket id; the claim read lists every test. Reads never evaluate. |
| E12 | **Coverage checker v3** (`demoed-coverage-checker.ts:125-134, 294-308`; rule B5) | Needed before any `period_aggregate` metric can pass w10 under the all-months rule. v3 consumes **only** the evaluation's emitted evidence (`demo.ms_snapshot_candidate`, 5.2 item 4), never an inferred outside row and never its own filter test. A cell's time-gate element is covered only when that cell has: at least one `counted` candidate (inside); and at least one `rejected_time_gate` candidate in the same partition whose emitted `other_rules_passed_flag` is **true** (outside). That flag is the emitted "other rules passed" fact tied to that candidate and cell. The element records the cell and the identities of both. **Negative fixtures:** (a) two declared months, an evaluation in which no candidate was rejected by the time gate, refused as complete; (b) **the dual rejection**: for cell P01, the only outside candidate is a credit memo of P02. It is rejected by the month gate **and** by the document-type rule (`other_rules_passed_flag` false, `other_rule_failed_ref_text` the customer-invoice clause), so it is not a witness and the element is uncovered. A customer invoice of P02 with the flag true then covers it (the paired positive). w10 keeps requiring `demoed-coverage-v2` or later (0076:499-502) and complete coverage for a Demoed record, so v3 needs no database change. The owner's rule 5 stands. |
| E13 | The evaluation's candidate record (finding 3) | See "How the act judges the other rules on a time-rejected candidate" below the table. |
| E14 | `boundary/governed-metric-evaluation.service.ts:324-341` (the demo dry evaluation) and the proof command | Hand the emit the profile `numericProfileOf` returned for this evaluation (rule A1), and the role-keyed canonical input set it read, as evidence (V6). |
| E15 | `boundary/governed-metric-evaluation.service.ts:343-388` (tenant evaluation) | Before `runEngine`, read whether the version has a passed, complete test with this program's profile; if not, record `arithmetic_not_tested` through the recorded-refusal path and write no snapshot (rule A3). |
| E16 | `registry/mcf/mcf-cert-writer.service.ts`, admit (:2945-2993) and readmit (:3062-3141) | Compare the cited test's profile with its own and write `served_numeric_profile_code` into the transition evidence; name c17 and c18 before the database does (rule A2). No canonical-set comparison (amendment 1). |
| E17 | `boundary/metric-spec-loader.ts:109-119` on the demo plane | A test names the metric version it proves (the current active one for a re-check, the candidate before approval) instead of taking the world label's pin (V1, V2). The canonical inputs are those of the demo world's binding, recorded as evidence (V6). |
| E18 | A read of pins without a result (Foundation fix 3) | Lists every proof pin with no test result, so the proof command can complete it from the preserved pin. Reads never evaluate. |
| E19 | Flag after an engine-wrong resolution (Foundation fix 1) | The list read (E11) keeps the version flagged "engine wrong, withdrawal due" from a resolution with `corrected_side_code` `engine` or `both` until the version leaves `active`. |

**How the act judges the other rules on a time-rejected candidate (E13).** At bc-core df47ce00:

- **Where the time gate runs.** The time gate of a `period_aggregate` metric runs in the enumeration: `scopeCandidatesToPeriod` (`boundary/co-candidate-reader.ts:159-164`) or `scopeCandidatesToAnchorRange` (:183-200), called from `enumerateOnPlane` (:392-406). It returns only the kept rows, so a time-rejected candidate never reaches the engine.
- **Where the filters run.** The row filters run inside the engine, through `evaluateGrainGroup` (`boundary/governed-metric-runtime.ts:897-907`). There `buildSectionA` (:904) builds each row's `filter_inputs` from the CO payload (:631-645), and `engine.execute(spec.ast, sectionA, …, spec.filterClauses)` applies the clauses (:905):
  - in the legacy engine, `applyFilterClauses` (`registry/mcf/formula-execution.engine.ts:801-821`) keeps a row when `rowSatisfiesAllClauses` (:838-845) holds, clause by clause through `evaluateClauseAgainstRow` (:857);
  - in v3, `applyTypedFilters` (`registry/mcf/formula-execution-engine-v3.ts:405-414`) keeps a row when every clause passes `clauseMatchesRow` (:418-430).
- **The change.** Each engine gains one public classifier, `classifyRowsByFilters(rows, filterClauses)`. It returns, per row, whether all `where` and `pre_filter` clauses hold and the first clause that fails, in declared order. It calls the **same** private predicate the engine's own filtering calls (`rowSatisfiesAllClauses` / `evaluateClauseAgainstRow` in the legacy engine, `clauseMatchesRow` in v3). The existing filtering is rewritten to call the classifier, so there is one predicate per engine, not a second implementation.
- **The act.** The enumeration returns its time-rejected candidates beside the kept ones, each with the cell it was rejected from. In the same evaluation act, after the value is computed, `buildSectionA` builds rows for those candidates and the classifier judges them. The verdict and the first failing clause go into `other_rules_passed_flag` and `other_rule_failed_ref_text`. Kept rows rejected by a filter get `rejected_filter` from the same classifier.
- **The computed value does not change.** The classifier only reads rows; its output never enters `engine.execute` on the kept rows (:905), which stays as it is. In v3 the classifier must not add to the numeric-profile report: neither the filter typing record (`recordFilterTyping`) nor the downgrade labels. So the profile report and the value of the evaluation are byte for byte what they are today. This is fixed by a test that compares the value and the report with and without the classifier call.
- **No later inference.** The checker reads the emitted flag. It never re-applies a clause and never infers an outside row (Foundation VI).

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
- Under Invariant VI the list must be emitted by the evaluation itself: `demo.ms_snapshot_candidate` (5.2 item 4) and E13.

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

The coherent route is a superseding hand-over that keeps the old answer and records the new one, with the resolution as its reason. Its custody, its selection of the current answer and its proof-currency rules need a separate design and the owner's own database yes (rule B8). This design does not cover them. The owner settled it (rule S4): it is not built now. The first time the documents show the world wrong, work stops and the correction is designed then, keeping the old answer.

## 8. The flag, the ticket and the lock

**The flag.** A version is flagged while it has a failed test with no resolution. After a resolution that says the engine was wrong (`corrected_side_code` `engine` or `both`), the flag **stays** until the version leaves `active`, shown as "engine wrong, withdrawal due" (Foundation fix 1). From that resolution on, the version is no longer Demoed (5.1 item 6b), so it cannot be approved again. The flag is computed from the records when they are read; nothing stores it.

**The ticket.** One per failed test, in the platform's support tickets (bc-admin `/platform/tickets/:ticketId`, `components/AppRouter.tsx:297-298`). It names the metric, version and test, and the differing cells with both values, and later holds the two document lists. The ticket's status never releases the lock.

**The lock: L1, settled** (rule S2, 32202aea). While a version has a failed test with no resolution:

- **Nobody may approve it.** c17 refuses the `audit_pending → active` flip.
- **Nobody may change it.** The state-transition trigger refuses any change of state of that version. This holds also for a version that is **already active** when a re-check fails.
- **Customers keep seeing its values.** Nothing switches off by itself.
- **More tests may run**, and a new, corrected version may be authored.

When the resolution records that the engine was wrong, the version is withdrawn through an existing door. For a never-admitted `audit_pending` version that door is withdraw-retire (0080:17-19). For an active version, the existing exits are the edges `active → superseded` (by a corrected version) and `active → audit_blocked` (`mcf.fn_mcv_state_transition_check`, read live). Which of the two the engine-wrong case uses is named at implementation.

The flag and the lock are read only from the immutable result and resolution, never from the ticket's status (rule B9).

*Considered and not chosen:* L2 (also refuse new tenant bindings of the flagged version), L3 (also mark its values "under review" to tenants) and L4 (stop serving; ruled out by the owner's "no automatic switch-off").

## 9. The Tests column

**Screen.** The bc-admin **Metric Catalog** page, `src/pages/MetricCatalogPage.tsx`, route `catalog/metrics` (`components/AppRouter.tsx:203`). It reads `GET /api/mcf/metric-contracts` (`src/api/mcf-catalog.ts:67-70`). Its columns today (header comment and lines 193-249) are Metric ID, Metric Name, Function, Sub-function, Type, Description, Declaration chain and State. **Tests** goes between Declaration chain and State.

**What it shows**, for the metric's current version. There is one count per version, with no source-type dimension (3.7):

| Records | Cell shows |
|---|---|
| no test | "No tests" |
| only passed | "3 passed", with a small mark "covers every rule" when one passed test had complete coverage |
| an open failure | "4 passed, 1 failed" with a flag that links to the ticket (`/platform/tickets/:ticketId`) |
| failures, all resolved, the world found wrong | "4 passed, 1 failed (resolved)", with no flag |
| a resolution found the engine wrong, version still active | "engine wrong, withdrawal due", with a flag (Foundation fix 1) |
| no passed test under the serving arithmetic | "3 passed, re-check due (arithmetic)", with a flag (rule A3) |

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

- Step 6 inputs (:158): a current Demoed record from a passed test with complete coverage and, under L1, no unresolved failed test.
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

**The versions (amended).** The test proves the metric on whatever canonical contract version the Kaveri world's binding provides (cc-das36 5.1.0 today) and records it as evidence (V6). Whether 5.1.0 or 4.0.0 is the version customers resolve, and whether the Odoo mapping produces correct records under it, is not a question for the metric's approval. It belongs to the canonical-selection and mapping-proof designs (section 15). The owner's earlier open choice for this use is withdrawn.

**What the test then exercises.** The document-type rule can pass and exclude rows: 30 of the 2,714 invoices are not customer invoices, all in FY2023-24 to FY2025-26 (read live). **But under coverage v2 the time-gate element is uncovered when every month is declared (section 4), so w10 refuses this test until checker v3 (E12) is served.** E12 is therefore on the first use's critical path.

## 13. Foundation gate

Rewritten by amendment 1 (Foundation fix 8) for everything added since revision 4. The four answers are given per repair. The locations are DEC-79b62f's: A source and admission boundary, B contract semantics, C mapping and binding, D evaluation implementation, E storage and projection, F read model and diagnostics.

| Repair | Location | Why here, not above | Why not below | Design or execution act (DEC-c48b0f) |
|---|---|---|---|---|
| The declaration covers every month the world holds data for; the world declares its months (3.1, 3.2) | B, enforced at E | A is sound: the world's records and hand-over are correct; the defect is what the platform declares about the proof | A label or a reader that hides months would compensate | Design act: the declaration's scope |
| Every test result kept, a mismatch recorded, the result in the same act as the pin (3.3, 5.1 item 2, 5.2 item 2) | E | The evaluation (D) is correct; it is its record that is missing | A detector reading logs would infer, not emit (VI) | Design act: a missing record |
| The same arithmetic (A1 to A4) | D, with its evidence at E | The contract (B) does not choose arithmetic; the evaluation does, per program | A read-side comparison alone could not stop serving | Design act: the arithmetic was never recorded or compared |
| Per-cell candidate evidence with the engine's own other-rules verdict (E12, E13) | D, emitted at E | The rule (B) is stated; the evaluation did not emit what it rejected | A checker re-applying clauses would be a second implementation (VI) | Design act: a missing emission |
| The shared gate on every route to active or current (G1) | E | Admission (A) and the contract (B) do not decide currency | Each route checking for itself would leave gaps | Design act: one gate declared once |
| Not Demoed while a failure is open or after an engine-wrong resolution; the flag kept until withdrawal (5.1 item 6b, section 8) | B, enforced at E and surfaced at F | Demoed is a semantic claim about the version (B) | Hiding the version in a read model only would leave the claim standing | Design act: the claim's conditions |
| Canonical inputs recorded as evidence, not a gate (V6, 3.7) | E | The metric reads canonical vocabulary only (B); which source produced the records is a C question | Gating the metric on canonical versions would be lower-layer compensation for an unproven mapping (C) | Design act at C, named separately (section 15) |
| The documents decide a disagreement (section 7) | F for the lists, B for the judgement's yardstick | The yardstick is the owner's definition (B), not either calculation | Neither calculation may overrule the other | Design act: who settles |

**Invariants kept.**

- **III, all state is immutable.** Every new record is append-only. A re-check is a new run, a resolution a new row. The one-declaration rule and the existing proof input row (left NULL) are unchanged.
- **IV, all references are explicit.** The approval names the Demoed record; the result names its pin and record; candidate rows name the canonical contract and version explicitly, and the store code is only a locator.
- **V, evaluation is non-replayable.** Each test is its own evaluation with its own pin. Completing a pin without a result records a verdict from the preserved pin and never evaluates again.
- **VI, evidence is emitted, not inferred.** The verdict, the mismatch, the candidates with their dispositions, the arithmetic and the canonical inputs are emitted by the acts that produced them.

## 14. Settled questions

The owner settled the seven open questions as recommended (barecount-devhub `claude/operator-review-content`, DECISIONS commit 32202aea, recorded 2026-11-24 20:40 IST: "Yes, as recommended"). Each is now a rule of this design.

- **S1. Anyone on the team may run a re-check.** A re-check only reads and records, at any time (R2, rule B1). The actor is always recorded (`recorded_by_name`). Any platform team role may call the re-check command, and the producer login alone writes the result (5.1 item 5).
- **S2. Lock L1, also on an active version.** While a failure is unresolved, nobody may approve or change that version, including a version customers already use. Customers keep seeing its values. If the documents show the engine was wrong, the version is withdrawn through an existing door (section 8; 5.1 item 6).
- **S3. The owner, or whoever approves metrics, judges the documents** and records the resolution with a written reason (`judgement_text`, at least 40 characters; E10).
- **S4. A corrected world answer is not built now.** The first time the documents show the world wrong, work stops and the correction is designed then, keeping the old answer (7.4, rule B8).
- **S5. A world month is a month in which the demo world has posted accounting entries.** Months with zero qualifying documents for the metric are included and tested (3.2).
- **S6. Approval names one passing test: the one that exercised every rule.** That is the test whose passed result carries complete coverage and the Demoed record the approval names (3.4).
- **S7. One company per test.** A world with several companies gets no full-world claim until its route is designed (rule B7; section 15).

Also settled:

- **Rules A1 to A4 are owner-confirmed** (fc92dd64, confirmed in 752c345c). Of V1 to V6, amendment 1 keeps V1, V2 and V6 (as evidence only) and removes V3 to V5 from the metric's gate (bf0101cf).
- **The principle of one demo world per source type** (b13068d5) governs the mapping proof, not the metric test (3.7).

Open for the owner: his database yes again for the amended shapes (section 16), before the builder restarts (bf0101cf).

## 15. Out of scope, known limits, and what was not grounded

**Coverage v2 limits, recorded and not changed:**

- `computed_dimension` and `conditional_branch` elements are always uncovered ("not derivable", `demoed-coverage-checker.ts:25, 352-354`), so a metric with a computed dimension or a `case` node can never reach complete coverage.
- `grain_partition` needs two or more legal entities among the proven cells (:24, :330), while w3 allows one legal entity per declaration (0076:408-411, R3: one proof pin covers one legal entity). A metric scoped by legal entity can never be complete today. For a world with several legal entities, "every month for every legal entity" also meets this one-legal-entity rule. Kaveri has one legal entity.
- A time gate other than `period_aggregate` or `as_of` is uncovered.

**Out of scope:**

- A corrected world answer (a superseding hand-over): its custody, current-answer selection and proof-currency rules need a separate design and the owner's own database yes (rule B8).
- A route for worlds with several legal entities: the writer covers one legal entity, and no full-world coverage is claimed through one entity's pin (rule B7; rule S7).
- **The mapping proof, per source type.** It asks whether a source's canonical contract version produces correct canonical records, on that source type's demo world. The owner's principle is one demo world per source type, built once per type (b13068d5), and the first customer of a new type may help, as a commercial matter (cd335caa). It is a separate check in a separate design (bf0101cf). Building a world for a new type belongs to it.

**Separate design acts, named here and not designed** (bf0101cf):

- **Canonical selection (Foundation fix 4).** Which canonical contract version customers resolve is chosen by a rule that lives only in code. cc-das36 has two `active` versions, 3.0.0 and 4.0.0 (read live), and the tenant reader takes the newest (`boundary/co-candidate-reader.ts:137-155`). Why separate: it is a C-layer declaration (a governed selection, or tenant bindings that name the version), and it affects every metric, not only tests. Its concurrency fixture moves there from 3.8.
- **Tenant arithmetic recorded (Foundation fix 5).** A tenant evaluation adds its profile report to the lineage only under the scaled profile (`boundary/governed-metric-persistence.adapter.ts:475-487`, "Absent under binary64-v1"). Every tenant evaluation should record its `numeric_profile_code`. Why separate: it changes the tenant evaluation record, not the test.
- **Observation contracts name their source contract.** `contract.observation_contract.source_contract_id` exists but is NULL on all 17 rows (12 live; read live). Why separate: it is a declaration gap at A/C that the mapping proof needs, not the metric test.
- **The mapping proof itself**, above.

**Not grounded in this design:**

- how the enumeration and the engine will return their rejected candidates: today both return only what they keep (E13);
- that `invoice_number` equals Odoo's `account_move.name` (7.2);
- the bench's own month range (the bench was not restored here; 41 periods is the canonical records' count);
- the decision head and certificates of `b9357731` (12);
- the allowed values of `support.ticket.category_code` (the `support` schema is not readable with the tool used);
- the status the demo emit should record for a mismatch (5.2 item 2).

## 16. Database changes for the owner's yes

Two bc-db forward migrations. The numbers are **to be confirmed** at authoring against bc-db `main` and the open pull requests. The demo side is **0082** and applies first; the platform side is **0083** and applies second. On 2026-11-24 the highest merged migration is 0081, the only open pull request that claims a number is #177 (0073), and no bc-db branch carries a file numbered 0082 or higher.

Each follows the Database Change Protocol and the bc-db conventions:

- authored once as a forward migration with its header contract and rollback;
- proven on an owner- and grant-faithful restore of a fresh read-only dump, including the served-login vectors;
- applied only through the governed runner under a separate recorded desk grant;
- ISO 11179 names (DEC-69f09e);
- at most 20 columns per table, foreign keys on every in-plane reference (a cross-schema FK to `contract.canonical_contract_version` is allowed), no JSONB for queryable data, and indexes in the same migration (DEC-1918d0).

The existing rows stay as they are, apart from the rows these changes add. The last column compares each row with the owner's two database yeses:

- **8558dc9f**, "Yes to both": PR 271 section 16 at head 100d4e55;
- **0bfc5aa4**, "yes to all five shape changes".

**Amendment 1 needs his yes again** for every row not marked "as said yes" (bf0101cf).

**0082, demo side (`demo`), applies first**

| Table or routine | Change | Reason | Versus the yes |
|---|---|---|---|
| `demo.world_binding_data_period` (6 columns, FK to `demo.answer_sheet_handover`) | add | The world declares, through its own hand-over, every month in which it has posted accounting entries. | shape 3 as said yes; **awaiting a renewed yes** for "once per binding", added in amendment 1 |
| `demo.fn_hand_over_answer_sheet` (0075) | alter | Accept a v2 answer-sheet format with a months section; v1 unchanged; months written once per binding. | shape 3 as said yes (through the existing hand-over); **awaiting a renewed yes** for the v2 months format, named in amendment 1 |
| `demo.fn_emit_demo_proof_period_v5` and `demo.fn_emit_demo_proof_v5` (0078) | alter | Record a mismatch as a run with a `mismatch` pin instead of raising; write each cell's candidates with their disposition, explicit canonical contract and version, and the other-rules verdict; write the pin's numeric profile and one proof-input row per canonical role, refusing a NULL canonical contract on new rows. | changed in amendment 1 (fix 6: explicit canonical contract and version on candidates; NULL refused on new inputs) |
| `demo.uq_demo_metric_run__act` and the emits' per-act guard | alter | Key a run by the caller-given `run_id`, so a re-check can run at any time. | as said yes (0bfc5aa4, smaller fix) |
| `demo.ms_snapshot_candidate` (14 columns) | add | Each cell's candidates and why each was counted or rejected; exactly one of `demo.ms_snapshot` / `demo.ms_snapshot_ccy`; canonical contract and version explicit, store code a locator only; record id and content hash; the engine's own other-rules verdict on a time-rejected candidate. | changed in amendment 1 (fix 6 adds `canonical_contract_id` and `version_code`; shape 4 otherwise as said yes) |
| `demo.fn_pin_handed_over_expected_cells_refusal(uuid)` | add | Prove a mismatched pin's expected values are the world's own hand-over. | as said yes |
| `demo.metric_proof_pin` (14 to 15 columns) | alter (add `numeric_profile_code`) | Record the arithmetic each proof ran with, beside the engine build it already records. | as said yes |
| `demo.metric_proof_input` (10 to 11 columns) | alter (add `canonical_contract_id`; widen `ck_metric_proof_input_role`, `_rows`, `_store`) | Name the canonical contract explicitly (the pin `00f5f597` row stays NULL; new rows refuse NULL); allow the `field_declarations` role and the stores of every canonical version a world binding provides. | shape 2 and the widened checks as said yes; **awaiting a renewed yes** for refusing a NULL canonical contract on new rows, added in amendment 1 |

**0083, platform side (`mcf`, `metric_audit`), applies second**

| Table or routine | Change | Reason | Versus the yes |
|---|---|---|---|
| `mcf.metric_version_demo_test_result` (14 columns) | add | Every test's verdict, pass or fail, one row per proof run, with its arithmetic; written in the same command act as the pin. | changed in amendment 1 (16 to 14: canonical fingerprint and source type removed) |
| `mcf.metric_version_demo_test_cc_version` (5 columns; composite FK to `contract.canonical_contract_version`) | add | The role-keyed canonical inputs the test read, as evidence only. | changed in amendment 1 (shape 1 as said yes; it no longer gates approval) |
| `metric_audit.transition_evidence` (15 to 16 columns) | alter (add `served_numeric_profile_code`) | The approval records the arithmetic it saw at the act. | changed in amendment 1 (`canonical_input_set_sha256` removed) |
| `mcf.metric_version_demo_test_result_element` (7 columns) | add | The coverage elements of a pass that did not exercise every rule. | as said yes |
| `mcf.metric_version_demo_test_failure_resolution` (9 columns; member reference as text) | add | The person's judgement of a failure from the documents, which releases the lock. | as said yes (member reference as text, 0bfc5aa4) |
| `mcf.fn_demoed_declaration_covers_world_months(uuid)` | add | The declared cells equal every month the world holds data for. | as said yes |
| `mcf.fn_metric_version_demoed_declaration_has_cells()` (0076 commit check) | alter | Also require the world-month set, beside the kept answer-sheet equality. | as said yes |
| `mcf.fn_record_demo_test_result(…)` | add | One writer for every outcome: keeps w0-w8; records failures, partial passes, the arithmetic and the canonical inputs (refusing a missing or duplicate role); writes the Demoed record only on a complete pass. | changed in amendment 1 (no source type; canonical inputs as evidence) |
| `mcf.fn_record_demoed_bridge(…)` (0076 writer) | revoke EXECUTE | One writer only; revoked in the same transaction as the new one is installed. | as said yes |
| `mcf.fn_customer_current_gate_refusal(uuid)` | add | The one shared gate: Demoed and current, no unresolved failure, served arithmetic (c16 to c18). | changed in amendment 1 (c19 and the per-source-type rule removed) |
| `mcf.fn_demoed_record_qualifies(uuid, uuid)` (0076) | alter | Not Demoed while a failure is open, or after a resolution that found the engine wrong. | **new in amendment 1** (Foundation fix 2) |
| `metric_audit.fn_intrinsic_decision_refusal(uuid)` | alter | Keep c1 to c15 and append the shared gate's list, so admit and the trigger apply one body. | as said yes |
| `mcf.fn_mcv_state_transition_check()` | alter | Apply the shared gate on every transition to active and every `is_current` change to true, **before** the same-state early return; refuse any change of state while a failure is unresolved. | as said yes (the placement is the auditor's boundary, 3.8) |
| `mcf.trg_mcf_mcv_state_transition` | alter (recreate) | Fire also on `UPDATE OF is_current`, so a direct pointer write cannot bypass the gate. | as said yes |
| Grants to `bc_platform_runtime` and `bc_demoed_bridge_writer` | add / revoke | SELECT on the new tables, INSERT on the resolution only, EXECUTE on the new writer only. | as said yes |

**Removed by amendment 1** (said yes to, no longer built):

- the platform table of source type to demo world (shape 6, 0bfc5aa4);
- condition c19 and the two-way canonical set comparison at approval;
- `canonical_input_set_sha256` on the test result and on the transition evidence;
- `source_system_code` on the test result.
