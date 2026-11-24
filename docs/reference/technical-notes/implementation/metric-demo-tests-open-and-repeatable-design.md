---
uid: metric-demo-tests-open-and-repeatable-design
title: Open, repeatable tests of a metric version on the demo world (design)
description: "Design for the owner's ruling of 2026-11-24: proof months are not locked to a metric version. Each test on the demo world records its months before it runs, every test is kept, approval names the test it relies on, a re-check is allowed at any time, and a failed test flags the metric, opens a ticket and applies a lock. Proposes the bc-db, bc-core, bc-demo and bc-admin changes; nothing is built."
status: proposed
date: 2026-11-24
project: bc-docs
domain: metrics
subdomain: metric-lifecycle/demoed
focus: design
governing_adr: DEC-79b62f
---

# Open, repeatable tests of a metric version on the demo world

*Design note · proposed 2026-11-24 · nothing in this note has been built or run. Database changes in it are a proposal: they need the owner's explicit yes under the Database Change Protocol before any migration is written.*

Evidence base, read at these heads on 2026-11-24: bc-db `origin/main` 18d6884, bc-core `origin/main` df47ce00 (the served engine), bc-demo `origin/main` 428ab310, bc-admin `origin/main` 6267a64, bc-docs `origin/main` 96487a5. Live rows were read read-only on `bc_platform_dev` on 2026-11-24 with the read-only database tool. Paths in bc-core are under `src/` unless shown otherwise.

## 1. The problem in plain words

To be approved, a metric version must be shown to give the same answers as the demo world for a set of months. Today the platform fixes that set of months once, for good, for each version. Nothing can be added later. If the months chosen first do not exercise every rule of the metric, the only way out today is a new version of the metric, even though the metric itself is right.

That is what happened to **customer invoice volume** (metric contract `fe91c450`, version `b9357731`, state `audit_pending`):

- Its months are FY2026-27 P01 to P04 for KAVERI-IN (declaration `f41bcda2`, 4 cells, read live).
- The platform's answers matched the demo world's own answers in all four: 60, 58, 62 and 67 (proof pin `00f5f597`, comparison `match`, read live).
- The proof was still refused, correctly: the metric counts only documents whose type is "customer invoice", and none of the four months holds a credit memo, so that rule was never put to the test (check w10, coverage).
- Credit memos do exist in FY2025-26 P11 and P12. But the months of version `b9357731` are locked, so those two months cannot be added.

The owner's answer: the months must not be locked. Tests become open and repeatable, and every test is kept.

## 2. The owner's rules

Recorded 2026-11-24 20:05 IST (barecount-devhub branch `claude/operator-review-content`, `artifacts/operator-review/DECISIONS-workflow-review.md`, last entry, commit 98190a23). In his words: "I think locking months is a bad design. In fact we should keep them open/configurable and should allow multiple tests at any point of time. Re-check kind of." On the shape the Chief put to him: "agree, flag on failure, write the design."

The rules this design implements:

1. The months (cells) of a test are chosen and recorded **before** the test runs. Nobody picks months after seeing the numbers.
2. Every test is kept forever, pass or fail. Nothing is deleted or overwritten.
3. Approval (certification) names the test it relies on.
4. A re-check is allowed at any time, also after approval. Each re-check is a new recorded test.
5. Before approval, at least one passing test must exercise every rule of the definition. This is the coverage rule that check w10 of checker `demoed-coverage-v2` applies today; it was right and it stays.
6. A failed test **flags** the metric. A person decides what happens; nothing switches the metric off by itself. A failed test opens a ticket and applies a lock. What the lock holds is proposed in section 7 and is **open** for the owner.
7. The metric list gains a **Tests** column, for example "3 passed", or "4 passed, 1 failed" shown as a flag that links to the ticket.

Open, for the owner: who may run a re-check (section 12).

## 3. The model

### 3.1 What a test is

A **test** is four things, in this order:

1. **The choice.** A person records which cells the test covers: the demo world, the legal entity and the periods (and the currency, for a per-currency metric). The record carries the version's frozen content identity and the time, set by the database. Once recorded it cannot change.
2. **The demo world's answers.** The demo world has worked out and handed over its own value for each chosen cell. A cell handed over once serves every later test of that cell; the hand-over is not repeated.
3. **The run.** The platform evaluates the version on the demo world for exactly the chosen cells and compares each value with the demo world's value. The run must start after the choice was recorded.
4. **The verdict.** One record, written once, says how the test ended:
   - **passed**: every value matched. The record also says whether the test exercised every rule (coverage complete or partial).
   - **failed**: at least one value differed. This is the case that flags the metric.
   - **void**: the test could not be judged as recorded (for example, the run did not cover exactly the chosen cells, or started before the choice was recorded). It is kept with its reason and flags nothing.

A test that passed and exercised every rule also writes a **Demoed record** (the existing `mcf.demoed_evidence_bridge` with its provenance), exactly as today. That record is what approval cites.

### 3.2 How approval cites tests

The activation act already names the Demoed record it relied on (`metric_audit.transition_evidence.demoed_evidence_bridge_uid`, bc-db 0076:325-331), and the Demoed record's provenance row names the declaration it checked (`mcf.demoed_bridge_provenance.metric_version_demoed_declaration_uid`, 0076:295-310). In this design the declaration **is** the test, so approval already names its test through that chain. No new column is needed for rule 3.

Approval needs, at the act:

- a Demoed record of this exact version whose proof still reads current (unchanged: `mcf-cert-writer.service.ts:1047-1058`, c16 at 0076:845);
- that record comes from a passed test with complete coverage (rule 5; unchanged in substance, since only such a test writes a Demoed record);
- under lock option L1 or stronger (section 7): no failed test of this version that a person has not yet resolved.

### 3.3 Re-check after approval

A re-check is simply a new test. It can be recorded on an `active` version, which today's declaration guard refuses (0076:179 accepts only `approved` and `audit_pending`; this design adds `active`). Its verdict is kept like any other:

- A passing re-check adds to the count and, if complete, writes a new Demoed record that supersedes the current head (the routine already supersedes, 0076:510-519).
- A failed re-check flags the version, opens a ticket and applies the lock. It never undoes an approval and never stops values being served: the owner ruled out any automatic switch-off, and 0076 already holds that Demoed is historical and is never undone (0076:11).

## 4. What exists today, and where months are locked

Read at bc-db 18d6884 and bc-core df47ce00.

| Where | What it does today | Why it locks or blocks a second test |
|---|---|---|
| `mcf.metric_version_demoed_declaration`, constraint `uq_metric_version_demoed_declaration_mcv` (0076:121) | One declaration per version. | A second set of months for the same version is refused. |
| Table comment (0076:127-130) | "A wrong declaration is corrected only by a new version." | States the lock. |
| `mcf.fn_demoed_declaration_matches_answer_sheet` (0076:239-264), used at commit (0076:280) and in w3 (0076:412) | The declared cells must **equal** every cell the demo world has handed over for this metric and version. | `demo.fn_answer_sheet_cells` (0075:487-501) returns the union of all hand-overs under the world's current binding. A second hand-over (P11, P12) makes the union six cells, so the existing four-cell declaration fails w3 from then on, and a six-cell declaration is refused by the unique constraint. |
| `mcf.fn_record_demoed_bridge`, w3 (0076:396-415) | Reads "the" declaration of the version by version uid. | Assumes one row. A plain `SELECT … INTO` with several rows takes one of them silently, so the unique constraint cannot be dropped while this routine is callable. |
| w8 (0076:468-483) | The proof's cells must be set-equal to that one declaration's cells. | Tied to the single declaration. |
| w6 (0076:456-461) | The package was frozen before the proof run. | Does **not** compare the declaration's time with the run. The table comment says the declaration comes first, but nothing checks it (also noted in the proof guide, step 4). Rule 1 needs this check. |
| A refusal in the routine | Every refusal is raised before any write (0076:335-336). | A failed or partial test leaves no record in the database. Rule 2 needs a record on every outcome. |
| The demo proof emit, `demo.fn_emit_demo_proof_period_v5` and `demo.fn_emit_demo_proof_v5` (bc-db 0078:220, 0078:441) | A cell whose value differs from the demo world's raises: "Demoed is emitted only on a full match". | A **value mismatch**, the one outcome that matters most, writes nothing at all. `demo.metric_proof_pin` already allows `comparison_outcome = 'mismatch'` (constraint `ck_demo_proof_pin_outcome`, read live), but no routine writes it. |
| bc-core `demoed-declaration/declare-demoed-version.command.ts:21` | "A declaration is immutable and one per version … a wrong one is corrected only by a new version." `readState` (lines 199-206) returns one declaration; the status text (148-150) says "the declaration is final". | The command and its read assume one. |
| bc-core `demoed-declaration/demoed-declaration-refusals.ts:35` | Maps the unique constraint to `declaration_already_exists`. | The refusal code of the lock. |
| bc-core `demoed-evidence-bridge.service.ts:369-382` | Step 5 refuses a hollow proof (`b5_coverage_insufficient`) before the routine. | A hollow test is refused, not recorded. |
| bc-core `database/plane/plane-world-evaluation-coordinate.ts:40-52` | A world label fixes the dates a proof evaluates (`kaveri-demo-v3lc5-v2-p01-p04` = 2026-04-30 to 2026-07-31). Labels are append-only code. | A new set of cells needs a new label through a reviewed code change. Not a lock on the version, but a cost on every new grid (section 6, E8). |

What already works and is kept:

- **Expected values per cell.** `demo.oracle_custody` holds one immutable value per (world, metric, version, legal entity, period) (`uq_demo_oracle_custody_cell`; the per-currency table likewise, read live). A cell handed over once serves every later test; a second hand-over of the same cell is refused (`answer_sheet_cell_occupied`, 0075:400). Proof snapshots reference custody rows without a uniqueness limit (`demo.ms_snapshot` has no unique index on `oracle_custody_id`, read live), so many tests can reuse one expected value.
- **The pin-side hand-over check** `demo.fn_pin_answer_sheet_refusal` (0075:413-476) checks each cell of the proof by **membership**: its custody row is a handed-over cell of this metric and version, from a hand-over under the proof's own world binding, and the pin's custody-set hash is worked out again and must equal the stored one. It does not compare with the union of all hand-overs, so it already accepts a test on any subset of handed-over cells. It returns `answer_sheet_pin_absent` for a non-matching pin (0075:422-424), so it applies to passed tests only.
- **Many proofs per version.** `demo.metric_proof_pin` is unique only per evaluation (`uq_demo_proof_pin_evaluation`, read live).
- **Demoed records supersede.** The routine writes each new Demoed record over the current head (0076:510-519); the activation check reads every record, not only the head (`demoed-activation-record.ts:66-82`).
- **Proof currency.** The attestation act appends a new `current` or `not_current` row each time it runs (`demoed-evidence-bridge.service.ts:429-470`), never a replay.

## 5. What changes in the database (proposal)

**Status: proposal for the owner's yes.** One bc-db forward migration, proposed number **0082, to be confirmed** at authoring: on 2026-11-24 the highest merged migration is 0081, the only open bc-db pull request claiming a number is #177 (0073), and no bc-db branch carries a file numbered 0082 or higher. It would be proven on an owner- and grant-faithful restore of a fresh read-only dump, including the served-login vectors, and applied only through the governed runner under a recorded desk grant. Rules followed: ISO 11179 names (DEC-69f09e), at most 20 columns, foreign keys on every reference inside the plane, no JSONB for queryable data, indexes in the same migration (DEC-1918d0).

### 5.1 The test record: the existing declaration, opened up

The two existing tables stay and keep their names, so the existing row `f41bcda2` becomes the first test of customer invoice volume with no data change. Renaming them to `…_demo_test` is possible, but it would touch every 0076 routine and the bc-core command for no change in meaning; it is left as an option for the owner.

- `mcf.metric_version_demoed_declaration` (7 columns, unchanged):
  - **drop** `uq_metric_version_demoed_declaration_mcv`; **add** `idx_metric_version_demoed_declaration_mcv` on `(metric_contract_version_uid)`;
  - insert guard (0076:167-197): also accept state `active` (re-check after approval). The content-identity check (hash = the version's frozen snapshot) and the database-set time stay;
  - the immutability triggers stay (no update, delete or truncate);
  - new table comment: one row per test; many per version; immutable; written before its run.
- `mcf.metric_version_demoed_declared_cell` (5 columns): unchanged. Cells only in the test's own transaction, one grid per test, a declared demo legal entity.
- The commit check (0076:268-292): replace the equality with **inclusion**. A new `mcf.fn_demoed_declaration_within_answer_sheet(uuid)` is true when the test has at least one cell and every cell is among `demo.fn_answer_sheet_cells(world, metric, version)`. The equality function is dropped once nothing calls it.

### 5.2 The verdict of every test (new)

`mcf.metric_version_demo_test_result`: one immutable row per judged test, 12 columns.

| Column | Type | Rule |
|---|---|---|
| `metric_version_demo_test_result_uid` | uuid | primary key |
| `metric_version_demoed_declaration_uid` | uuid NOT NULL | FK to the test; **UNIQUE**: a test is judged once, a re-check is a new test |
| `demo_metric_proof_pin_ref` | uuid NULL | the run's proof pin; a cross-plane reference with no FK, the same pattern as `mcf.demoed_evidence_bridge.demo_metric_proof_pin_ref` |
| `test_verdict_code` | text NOT NULL | `passed`, `failed` or `void` |
| `verdict_reason_code` | text NULL | NULL when passed; `value_mismatch` when failed; the named check when void (for example `w6b_run_before_test`, `w8_cells`) |
| `mismatched_cell_count` | integer NULL | at least 1 when failed; NULL otherwise |
| `coverage_checker_version` | text NULL | set when passed |
| `coverage_verdict_code` | text NULL | `complete` or `partial` when passed; NULL otherwise |
| `demoed_evidence_bridge_uid` | uuid NULL | FK, UNIQUE; set exactly when passed with complete coverage (the Demoed record this test wrote) |
| `writer_routine_version` | text NOT NULL | `fn_record_demo_test_result-v1` |
| `recorded_by_name` | text NOT NULL | the actor |
| `recorded_at` | timestamptz NOT NULL | set by the database |

CHECKs tie the columns to the verdict (for example, `failed` needs `value_mismatch` and a count; `passed` with `complete` needs the Demoed record uid). The version is reached through the test, so it is not stored twice. Immutable (update, delete and truncate refused, the 0065 trigger function). No login holds INSERT; only the routine in 5.4 writes it. SELECT to `bc_platform_runtime`.

`mcf.metric_version_demo_test_result_element`: the coverage elements of a **passed test with partial coverage**, 7 columns (`…_element_uid`, result uid FK, `element_kind_code`, `element_ref_text`, `covered_flag`, `witness_count`, `witness_digest`; UNIQUE on result, kind and ref). These are the elements that today are lost when w10 refuses. A complete test keeps its elements where they are kept today (`mcf.demoed_bridge_coverage_element`), so no element is stored twice. Same immutability and grants.

### 5.3 The resolution of a failure (new)

`mcf.metric_version_demo_test_failure_resolution`: a person's recorded decision on one failed test, 6 columns: `…_resolution_uid`, result uid (FK, **UNIQUE**: a failure is resolved once), `resolution_code`, `resolved_by_name`, `resolution_rationale_text` (at least 40 characters), `resolved_at` (set by the database). An insert guard requires the result's verdict to be `failed`. Immutable.

Proposed resolution codes, for the owner to confirm: `metric_corrected_by_new_version` (the definition was wrong; a corrected version follows), `demo_world_corrected` (the demo world's answer was wrong; a new world follows), `test_set_up_wrong` (for example, the wrong cells were handed over). Releasing the lock is this row, never the ticket's status: `support.ticket` is a mutable working table (status and `updated_at`, bc-core `database/schema/support/ticket.ts:22,35`), and a lock must rest on an immutable record (Invariant III).

### 5.4 The writer: one routine for every outcome

A new SECURITY DEFINER routine `mcf.fn_record_demo_test_result(p_test uuid, p_pin uuid, …)`, owned by `bc_schema_owner`, EXECUTE only to the existing producer login `bc_demoed_bridge_writer`. It takes the **test uid** explicitly instead of looking up "the" declaration. Its other inputs are those of `mcf.fn_record_demoed_bridge` (0076:337-353). It keeps the one reviewed cross-plane read.

Checks, in order. A refusal of the act itself writes nothing, as today. A judged outcome writes exactly one result row.

| Check | Outcome when it fails |
|---|---|
| w0 writer, w1 input (0076:364-375) | refused, nothing written |
| t1: the test exists and has no result yet | refused |
| w2 subject: state `audit_pending` or `active`, frozen snapshot equals the given hash, package-identity guard on (0076:377-394) | refused |
| w3: the test binds this content identity and one legal entity (0076:396-411) | refused |
| w4: the pin exists, its run completed, and the caller's values are the pin's own (0076:417-439; the `match` requirement moves to the verdict) | refused |
| w5 identity (0076:441-454) | refused |
| w6 order: snapshot before the run (0076:456-461) | **void**, `w6_order` |
| **w6b (new)**: the test's `declared_at` is before the run's `started_at` (rule 1) | **void**, `w6b_run_before_test` |
| w7 world (0076:463-466) | **void**, `w7_world` |
| w8: the pin's cells are set-equal to **this test's** cells, one grid (0076:468-483) | **void**, `w8_cells` |
| t2: every cell of the test is still within the handed-over cells (5.1) | **void**, `t2_not_handed_over` |
| pin outcome `mismatch` (needs 5.5) | **failed**, `value_mismatch`, with the count of differing cells |
| w9 hand-over, for a match (0076:485-494) | **void**, `w9_handover` |
| w10 coverage (0076:496-508) | **passed** with `partial`, elements recorded (5.2); no Demoed record |
| all hold | **passed** with `complete`; writes the Demoed record, its elements, its provenance (naming this test) and its `current` attestation exactly as the 0076 write block does (0076:510-535), then the result row naming it |

The provenance row keeps its writer check (`^fn_record_demoed_bridge-v[0-9]+$`, 0076:309), so the new routine writes `fn_record_demoed_bridge-v2` there. The rule "only one routine writes a Demoed record" stays.

**Retiring the old routine, in the same migration.** `mcf.fn_record_demoed_bridge` (v1) finds the declaration by version uid (0076:397-399). With several tests per version it would silently take one of them. The migration therefore revokes its EXECUTE from `bc_demoed_bridge_writer`, or drops it, in the same transaction that drops the unique constraint. The two must never be live apart.

`mcf.fn_demoed_record_qualifies` (0076:544-562) already joins the declaration through the provenance row, so it is correct for many tests and is unchanged.

### 5.5 A mismatch must be recorded on the demo plane

Today a mismatch raises inside the emit (0078:220, 0078:441) and leaves nothing behind. The proposal: replace `demo.fn_emit_demo_proof_period_v5` and `demo.fn_emit_demo_proof_v5` so that, when every structural check holds (declared legal entity, a custody row exists for every cell, the cells set-equal to the scope, one current world binding, lineage present), a value difference no longer raises. Instead the routine records the run, the evaluation, one snapshot row per cell (its own value beside its custody reference, so the expected value can be read), its Evidence and Lineage, and a pin with `comparison_outcome = 'mismatch'`. A missing custody row (a cell not handed over) still raises: that is not a test of the metric. The evaluation status and the Evidence outcome for a mismatch are to be fixed at authoring; the matched path is unchanged byte for byte.

A mismatch pin can never become Demoed: w4 and the pin-side check both require `match` (0076:433, 0075:422).

### 5.6 The lock in the database (depends on the owner's choice, section 7)

Under option L1 or stronger: a new condition **c17** `c17_unresolved_failed_demo_test` in `metric_audit.fn_intrinsic_decision_refusal`. It refuses when any test of this version has a `failed` result with no resolution row. It is added the way 0076 added c16: c1 to c16 are copied byte for byte from the live body, pinned by its md5 in the precondition (0076:69-72). The flip trigger already refuses `audit_pending → active` when that list is not empty (0076:38-39).

### 5.7 Grants and gates

- `bc_platform_runtime`: keeps SELECT and INSERT on the two declaration tables (0076:881); gets SELECT on the three new tables and INSERT on the resolution table only.
- `bc_demoed_bridge_writer`: EXECUTE on the new routine only.
- bc-core `tools/grant-drift/bc-platform-runtime-grants.tsv` (lines 124-134 record the 0076 grants) is updated in the same landing.
- Rollback: refuses while any test result, element or resolution row exists, or while any version holds more than one declaration.

## 6. What changes in the engine (bc-core), at every enforcement point

| # | Where | Change |
|---|---|---|
| E1 | `registry/mcf/demoed-declaration/declare-demoed-version.command.ts` (header :1-22, `status` :145-152, `readState` :199-206) | Becomes "record a test": many per version; `status` lists every test with its verdict; `active` allowed; the "final" and "new version" wording goes. The rolled-back database trial stays the way `check` judges. |
| E2 | `registry/mcf/demoed-declaration/demoed-declaration-refusals.ts:35` | `declaration_already_exists` goes; `declared_cells_not_answer_sheet` becomes `declared_cell_not_handed_over`. |
| E3 | `registry/mcf/bridge-record-writer.ts:94` and `demoed-evidence-bridge-cli.ts` | Call `mcf.fn_record_demo_test_result` with the test uid; the CLI takes `--test <uid>`. |
| E4 | `registry/mcf/demoed-evidence-bridge.service.ts` (step 5 :369-382; reconcile :16-18) | A hollow or partial test is no longer refused before the routine; it is recorded (passed, partial). "Reconcile, never replay" stays, keyed by the test: a test that already has a result returns it and writes nothing. |
| E5 | `registry/mcf/demoed-bridge-writer-refusal.ts` | Maps the new act refusals (`t1_…`) and reads the verdict the routine returns. |
| E6 | The demo proof command (proof guide step 11) | On a mismatch pin, record the failed result (E3) instead of stopping. |
| E7 | `registry/mcf/mcf-cert-writer.service.ts:1047-1058` (`assertCandidateDemoedInTx`, used by `admitMetric` at :2973-2974) | Under L1 or stronger, a sibling check that names the open failure before the database's c17 does. |
| E8 | `database/plane/plane-world-evaluation-coordinate.ts:40-52` with `plane-cc-version-binding.ts:37`, `plane-metric-version-binding.ts` and `plane-world-identity.ts` | Each new grid needs a new world label (append-only code, a reviewed landing). For the first use, one new label (section 10). **Later option**, not in this design: the proof run takes its dates from the test record, so a test needs no code change. |
| E9 | Ticket on failure (new) | After a failed result, open a ticket through `SupportService.createTicket` with `entity_type = 'mcf.metric_version_demo_test_result'` and `entity_id` = the result uid. The record comes first and the ticket second: if the ticket cannot be opened, the flag still shows and an idempotent "open the ticket for this failed test" command can be run again. `boundary/boundary-ticket.service.ts:26-40` is fire-and-forget and never throws; that is not enough for a lock, so this ticket gets its own command. |
| E10 | Resolve a failure (new command) | Writes `mcf.metric_version_demo_test_failure_resolution`; check, do and verify, like the other commands. On success it comments on the ticket and closes it. |
| E11 | Reads: `registry/mcf/mcf-read.service.ts:512-530` (`foldListChainRollups`, the list behind `GET /api/mcf/metric-contracts`, `mcf-publication-eligibility.controller.ts:30,70`) and `GET /api/mcf/metric-contract-versions/:mcvUid/demoed-claim` (`demoed-evidence-bridge.controller.ts:83`) | One set-based read of each current version's test counts and its open failure with the ticket id. The claim read lists every test. Reads never evaluate. |

`demoed-at-version.ts` and `demoed-activation-record.ts` read Demoed records through `mcf.fn_demoed_record_qualifies` and need no change. Request certification does not read the Demoed gate (no reference in `registry/mcf/request-audit-outcome.ts`), so it is unchanged.

## 7. The flag, the ticket and the lock

**The flag.** A version is flagged while it has a failed test with no resolution. It is computed from the records whenever it is read; nothing is stored as a flag.

**The ticket.** One ticket per failed test in the platform's support tickets (bc-admin `/platform/tickets/:ticketId`, `components/AppRouter.tsx:297-298`). It says which metric, version and test, which cells differed, and its two values for each. People discuss and track the fix on the ticket. The ticket's status never releases the lock.

**The lock: OPEN for the owner.** What a failed test holds until a person records a resolution:

| Option | What it holds | What it does not stop |
|---|---|---|
| **L1 (recommended)** | No new approval (activation) of the flagged version (c17, 5.6). | Serving the values of an already active version; a new, corrected version (the cure is never blocked); more tests. |
| L2 | L1, plus no new tenant binding of the flagged version. | Values already served to bound tenants. |
| L3 | L2, plus the version's values are shown to tenants marked "under review". | Serving the values. |
| L4 (ruled out) | Stops serving the version. | Listed only to rule it out: the owner ruled out any automatic switch-off. |

For an active version that fails a re-check, L1 holds nothing new, because the version is already approved. The owner may want L2 for that case. Where a tenant binding is refused under L2 was not located in this design (section 13).

## 8. The Tests column

**Screen.** The bc-admin **Metric Catalog** page: `src/pages/MetricCatalogPage.tsx`, route `catalog/metrics` (`components/AppRouter.tsx:203`). It lists the live governed metric contracts from `GET /api/mcf/metric-contracts` (`src/api/mcf-catalog.ts:67-70`). Its columns today, after the header comment and lines 193-249: Metric ID, Metric Name, Function, Sub-function, Type, Description, Declaration chain, State. **Tests** goes between Declaration chain and State.

**What it shows**, for the metric's current version:

| Records | Cell shows |
|---|---|
| no test | "No tests" |
| only passed | "3 passed"; a small mark "covers every rule" when at least one passed test had complete coverage |
| an open failure | "4 passed, 1 failed" with a flag; the flag links to the ticket (`/platform/tickets/:ticketId`) |
| failures, all resolved | "4 passed, 1 failed (resolved)" with no flag |
| void tests | not counted in the cell; listed on the metric's page |

A count-pill filter "Flagged" sits beside the existing State and Declaration chain filters. The metric's detail page (`src/pages/MetricDetailPage.tsx`, route `catalog/metrics/governed/:metricContractUid`) lists every test: cells, time recorded, verdict, coverage, the Demoed record it wrote, and the ticket. The new list fields are added to `McfMetricContract` (`src/api/mcf-catalog.ts:14`). Verdict labels come from a master hook, not a hard-coded list (coding standard 14).

## 9. What changes in the two onboarding guides

**Prove a metric version on the demo world** (`docs/onboarding/prove-a-metric-version-on-the-demo-world.md`):

- Overview, "It leaves" (:47): one or more tests, each with its verdict; a Demoed record from a passed, complete test.
- Step 1 (:89): a world label per grid until E8's later option exists.
- Steps 2 and 3 (:104, :118): work out and hand over only the cells not handed over before; a handed-over cell serves every later test.
- Step 4 (:134-146) becomes **Record a test**: many per version; the cells are any handed-over cells; recorded before the run, now enforced (w6b). The note at :146 ("the routine does not compare the times") becomes the rule.
- Steps 10 to 12 (:223-264): the run is for one named test; step 12 becomes **Record the test's verdict**, written for pass, fail or void, with the new codes in its failure modes.
- Step 13 (:267): read the test list and the Demoed record.
- New section **Re-check**: steps 4 to 13 at any time, also after approval; what a failure does (flag, ticket, lock); how a person resolves it.
- Troubleshooting (:283-306): `answer_sheet_cell_occupied` (:292) now reads "already handed over; record a test on it, no new hand-over needed"; `declaration_already_exists` goes; `w3_declaration` (:303) becomes "record a test first"; add `w6b_run_before_test` and `value_mismatch`.
- Appendix A, G8 (:367): the hand-over is again needed for every new contract, but no longer for a new set of months.

**Certify and activate a metric version** (`docs/onboarding/certify-and-activate-a-metric-version.md`):

- Step 6 inputs (:158): a current Demoed record from a passed, complete test, and (under L1 or stronger) no unresolved failed test.
- Step 6 failure modes (:163) and troubleshooting (:198): add `c17_unresolved_failed_demo_test` with its cure (resolve the failure, or correct the metric in a new version).
- Step 7 (:166-175): the read-back shows the tests and the one the approval relied on.

## 10. Customer invoice volume as the first use

Subject: metric contract `fe91c450-bb04-4823-a0b7-8f7e4fa16682`, version `b9357731-91e3-4e99-b294-1987ce29bbec` (`v1`, `audit_pending`), world `kaveri-demo-v3lc5`, current binding `e32071a8`, legal entity KAVERI-IN.

**Test 1, already on record.** Declaration `f41bcda2` (FY2026-27 P01 to P04) was recorded at 2026-11-24 12:09:19 UTC. The run of pin `00f5f597` started at 12:42:49 UTC, so w6b holds. Once 0082 is applied, its verdict is recorded by the new routine as a new act on today's records, not a rebuilt past result: expected **passed, partial** (the document-type rule not exercised).

**Test 2, six cells.** FY2025-26 P11 and P12 plus FY2026-27 P01 to P04. What it needs:

1. **The demo world's own values for P11 and P12. They do not exist yet.** The study's two working-outs cover FY2026-27 P01 to P05 only (bc-demo `sources/odoo19ee/demos/auto-components-in/design/metric-coverage/finance/sql/customer-invoice-volume-workings-2026-11-23.out`; the study `customer_invoice_volume-fe91c450.md`, "The working-outs (L4)"). Both working-outs are to be run for FY2025-26 P11 and P12 on the frozen bench (pg_dump sha256 `d0a33f41…`, read-only restore), agreed and added to the study as L4.
2. **A hand-over of those two cells only**: a new manifest and sheet under `ops/answer-sheet/sheets/`, made with `run_sheet.py` (its manifest lists periods with their dates, `run_sheet.py:17,99-107`), committed through a reviewed bc-demo pull request, then handed over with `handover.py` (README, "The path"). P01 to P04 are not handed over again; their custody serves test 2.
3. **A world label for the six dates** (E8): KAVERI-IN at 2026-02-28, 2026-03-31, 2026-04-30, 2026-05-31, 2026-06-30 and 2026-07-31 on the IN-APR-MAR-MONTHLY calendar, with the metric's pin on it. The name is to be chosen at the landing.
4. **Record test 2** (E1) before the run, then the dry evaluation, the proof and the verdict (E3).
5. The rule this test must exercise: by the proof session's live read of the canonical records under binding `e32071a8` (SES-40374d, 2026-11-24, not re-read here), P11 holds 62 invoices and 1 credit memo and P12 holds 71 invoices and 1 credit memo. The document-type rule can therefore both pass and exclude rows, which is what coverage v2 asks of a filter rule (`demoed-coverage-checker.ts:20-23, 250-260`). If the values match, test 2 is expected to pass with complete coverage and write the Demoed record that the approval then names.

The world rebuild and the new-version route are set aside by the owner's ruling.

## 11. Foundation gate

**1. Why this location.** Location **B, contract semantics, enforced at E**: the meaning of the Demoed declaration (what a version must prove, and that one fixed scope is all it may ever prove). The declaration's own definition (0076:127-130) fixes one scope per version. That is the defect the owner named. It is repaired by redefining the declaration as one test of many, enforced where 0076 enforced it: constraints, the definer routine and the c-checks (E). The Tests column (F) only surfaces records.

**2. Why not an upper layer.** A, the source and admission boundary, is correct: the demo world's records, its admission and its per-cell hand-over (0075) are sound and already accumulate. Nothing there is underspecified; the defect is in what the platform declares about the proof.

**3. Why not a lower layer.** A fix at C to F would be compensation: a new metric version only to change months (copying an unchanged definition), a world label that hides cells, or a reader that ignores the w10 refusal. Each would bypass a working mechanism. This design keeps the routine, its checks, the Demoed record, the attestation and c16, and changes only the single-scope assumption.

**4. Design act or execution act (DEC-c48b0f).** A **design act**: the declaration's definition is wrong (one per version, equal to all hand-overs) and is missing a rule (the test is recorded before its run). The flag, the ticket and the Tests column are a net, not the fix; they come after the design act.

**Invariants kept, and how.**

- **III, all state is immutable.** Every new record is append-only: a test, its verdict, its elements and its resolution are never updated or deleted (the 0065 trigger function). A re-check is a new test. A resolution is a new row, never an edit of the failure. Lifting the one-per-version rule keeps the old row as it is; it removes the reason to make a new version for months.
- **V, evaluation is non-replayable.** Each test runs its own evaluation and gets its own proof pin. Test 1's verdict is recorded from the run that happened, read from its preserved pin, not by running it again. The demo world's expected values are records that are compared, never part of the evaluation.
- **VI, evidence is emitted, not inferred.** Today a failed or partial test leaves no record, so its outcome could only be inferred from a command receipt outside the database. Under this design the verdict, the reason and the coverage elements are written by the act itself, and a mismatch is emitted on the demo plane with its Evidence and Lineage (5.5).
- **IV, all references are explicit.** Approval names the Demoed record; the record's provenance names the test; a verdict names its pin; a ticket names its verdict.

## 12. Open questions

1. **Who may run a re-check** (the owner's open point). Options: the metric publisher (`mcf_publisher`), who records tests today; a separate role for checking; any of several roles, with the actor always recorded; a scheduled re-check run by the platform. Recording a test and judging it are separate acts, so the two can be given to different people.
2. **What the lock holds:** L1, L2 or L3 (section 7).
3. **Who may resolve a failure**, and whether the three proposed resolution codes are the right ones (5.3).
4. Whether approval should name **every** passed, complete test, or one (this design: one, through the Demoed record; every other test stays on record and on screen).
5. Whether a **void** test should show in the Tests column (this design: on the metric's page only).
6. Whether to rename the declaration tables to `…_demo_test` (5.1).

## 13. Out of scope, and known limits

- **Coverage v2 limits**, recorded here and not changed:
  - `computed_dimension` and `conditional_branch` elements are always uncovered in v2 ("not derivable", `demoed-coverage-checker.ts:25, 352-354`), so a metric with a computed dimension or a `case` node can never reach complete coverage, however many tests it has.
  - `grain_partition` needs at least two legal entities among the proven cells (`demoed-coverage-checker.ts:24, 330`), while w3 allows one legal entity per test (0076:408-411, R3: one proof pin covers one legal entity). So a metric scoped by legal entity can never be complete today. Customer invoice volume is not scoped by legal entity.
  - A temporal gate other than `period_aggregate` or `as_of` is uncovered.
- A coverage checker v3, and tests across several legal entities.
- The proof run taking its dates from the test record (E8, later option).
- Expected values are unique per (world code, metric, version, legal entity, period) (`uq_demo_oracle_custody_cell`). A new binding of the same world code that gives a different answer for a cell already handed over cannot hand it over again. This is not changed here.
- **Not grounded in this design:** the tenant-binding enforcement point for lock option L2; the allowed values of `support.ticket.category_code` (the `support` schema is not readable with the read-only tool used here); the evaluation and Evidence status the demo emit should record for a mismatch (5.5).
