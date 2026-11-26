---
uid: metric-records-design
title: The metric records design, meaning on the definition version, evaluation on the contract version, and proof facts as governed records (design)
description: "Design for the owner's rulings of 2026-11-25: behaviour is code, values are records. The directory definition version owns a metric's declared meaning (name, plain definition, interpretation with direction, unit and decimals, FAQ facts); the catalog contract version owns only evaluation and references the exact definition version it realizes; the per-world proof facts now kept as code lists in bc-core become governed records with a second-proof path; each snapshot value records a preliminary or final mark. Platform side only. Customer Invoice Count is written again through it. Nothing is built."
status: drafting
authority: reference
date: 2026-11-25
project: bc-docs
domain: metrics
subdomain: metric-catalog/records
focus: design
governing_adr: DEC-79b62f
---

# The metric records design

*Design note · proposed 2026-11-25, revision 6 (2026-11-26) · nothing in this note has been built or run. The owner gave the database yes for migration authoring on 2026-11-25 (section 12). Each migration is proven on an owner- and grant-faithful restore before review, and every live apply needs its own recorded grant.*

**Revision 6 (2026-11-26).** This revision records what the build settled and applies the owner's rulings of 2026-11-26 (barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md`, branch `claude/operator-review-content`, commits 8ea9083e and 6e4a8803). What changed:
- **Package v4 is dropped** (6e4a8803). The package stays v3, with `thresholds_digest` over NULL. The reference is sealed by the immutable `mcf.mcv_realized_member_version` row, which is written before the metric contract version, carries the definition's content hash and is required at commit. An audit decision or certification that names a metric contract version therefore pins exactly one definition. Package v4 would have rippled through the audit records and about 27 engine files to restate the same fact. Sections 3.5, 4, 8, 9 and 11 are updated.
- **Successor-version rule** (6e4a8803). A new definition version is realized by a successor version of the same metric contract, not by a new metric contract, because `mc_name` equals `member_code` and is unique among live metric contracts. Customer Invoice Count's fresh start is the owner's exception (section 12, item 1): its old metric contract 8e8a6f28 is archived first. Section 4.1 is updated.
- **The output-binding unit equality check is dropped** (6e4a8803), because it compares two vocabularies (for example `USD` or `rows` against `count` or `currency`). The unit-currency coherence check stays (4.3).
- **A new subsection, 4.4,** lists what the build settled, each point cited to its migration header.
- **Vocabulary** (8ea9083e): the prose says "metric contract" where it said "calculation". "Definition" stays.
- 0086 is kept as the auditor accepted it, after the owner's repetition check (8ea9083e).
- The status stays `drafting`.

**Revision 5 (2026-11-25).** This revision applies the owner's rulings of 2026-11-25 (barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md`, branch `claude/operator-review-content`, commit 9336dd8f) and the auditor's acceptance of revision 4 (bc-external-audit `docs/RESPONSE-Codex-gen-4fc3c9-02-metric-records-design-rev4-2026-11-25.md`). What changed:
- **The five ADR-9dce29 dimensions are dropped from the definition** (purpose, shape, temporality, precision, impact). No code reads them: the Chief checked bc-core, bc-admin and bc-portal. Their five columns, foreign keys, authoring checks and the temporality pair check are removed. `member_version_interpretation` has 8 columns (0085-B). The masters stay untouched. Section 3.4 now says the dimensions are deferred.
- **The ADR-952faa temporality class stays**, with all of 3.4.1 (the D-2 refusal at authoring, approval and activation) and its check against the temporal intent and gate shapes.
- **The per-value mark stays** (section 6). `declared_flash` is gone, and the final rule no longer reads a precision. The mark is `final` when the period has ended at the as-of and no consumed input is capped. `unverified` inputs are refused, not marked.
- **Row 0085-I also refuses TRUNCATE** on family and group (the auditor's one hardening item).
- **Section 10:** the first metric is declared direction neutral, with the rationale as written, class `flow_per_period`, unit `count`, 0 decimals. The five-dimension table is removed.
- **Section 12 is now "Owner decisions (2026-11-25)":** all five open questions are answered, and the database yes is recorded.
- **Section 11:** the new ADR marks ADR-9dce29's metric dimensions deferred.
- The status stays `drafting`.

**Revision 4 (2026-11-25).** This revision folds in the owner's family-and-group rulings of 2026-11-25 (barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md`, branch `claude/operator-review-content`, commits 44ebbd53 and dda73851). What changed:
- **The six family-and-group rules are adopted** (3.8). Masters stop at subfunction; families and groups stay versioned directory records, created only through the directory commands. Their codes become globally unique, follow a slug pattern and are never reused. Every family version states its question as a question. A group has no question. A metric's place is read only through its definition's pinned family and group versions. The 29 groups without a version get one before any metric is placed under them. No new master table.
- **The database rows** are added to migration 0085 (rows 0085-G to 0085-J, section 9.1), with their rollback.
- **The structured group is its own design** (TSK-09855b), written right after this one. This design adds one forward-compatible check: a definition must match its group's declared unit and time class, once the group declares them (3.8).
- **Two missing commands are named** (section 8): a family version successor, and a governed archive of a family and its groups.
- **Words for readers:** in prose, "definition" is the member version and "calculation" was the word for the metric contract version (revision 6 says "metric contract" instead; section 3). Technical names stay in backticks.
- The open questions stay five; none is added.

**Revision 3 (2026-11-25).** This revision applies the auditor's CHANGES REQUIRED (bc-external-audit `docs/RESPONSE-Codex-gen-4fc3c9-01-metric-records-design-2026-11-25.md`, commit a8f9b1e9, on head a6ad5c0f). What changed:
- **Temporality class (blocker 1).** The definition version declares ADR-952faa's four-valued class in a new column, `temporality_class_code`, inside the content hash. The class is checked against the temporal intent shape and the contract's gate shape, and against every aggregate node of the formula. D-2's class-to-primitive refusal holds at authoring and again at approval and activation. D-2 is not built for MCF today (3.4.1). (Revision 5 later removed the five-dimension code from this check.)
- **Unit and currency coherence after insert (blocker 2).** Coherence is one database function, checked when the reference row is written, on every later change to the contract version's currency semantics or formula, on every change to the parent contract's gate shape, and again at approval and activation. The reciprocal rule is added: a `currency` unit refuses `not_applicable`. `mc_name` has no guard today (read live), so it is frozen once a version of the contract has a reference row (4.2; rows 0086-A, 0086-H to 0086-J).
- **`unverified` inputs.** ADR-f83b8a's rule is followed: such an evaluation is refused. The owner later kept that rule (section 12).
- **The Foundation check is cited by its findings**, not by a path the auditor could not see (revision 2 note below).

It also applies two owner rulings of 2026-11-25:
- **Retired columns are dropped, not kept** (former open question 5). Keeping unused columns is bad design; their only values sit on wrongly formed metrics. The values are written verbatim into the migration's committed evidence file, readers move first, and migration 0088 drops the columns (4.2, 9.4).
- **Function and subfunction leave the contract** (former open question 7). Placement is declared meaning, owned by the directory; the contract reaches it only through its exact definition-version reference (3.8, 4.2).

**Revision 2 (2026-11-25).** This revision applies an independent Foundation check (opus steward, 2026-11-25) of revision 1 at bc-docs 6e7527d9. Its verdict was "ready after fixes", with 16 findings:
- one blocker: the amendment list was incomplete;
- nine major: a second home for the realization pair; the old realization left undefined at supersede; column drops that would rewrite what a v3 reproof reads; a veracity cap that read Source Objects past the fixed ordering; a canonical pin that was a value reference, not an exact foreign key; a backfill that hid the identity fallback and a months-check exemption; a successor pin that changed a code rule silently; an incomplete database table (including the second source of `mc_name`); and an unspecified mark grain, immutability and as-of instant;
- six minor: a read that pinned "latest"; "meaning" not marked as declared meaning; a stale baseline and file count; a revoke item that could be closed; the interpretation column count; and format v1 left open on a binding with months.

What changed:
- the amendment list is complete: ADR-8f09d9, ADR-952faa, the threshold clause of D053 and the grammar's Metric Directory Member section are named, and the grammar amendment text is exact (section 11);
- the contract's reference to its definition version lives in a 1:1 child table, and the realization event is tied to it by a composite foreign key, so the pair has one home (section 4);
- a superseded definition keeps its contract's realization until a new contract version realizes the new definition (section 4);
- `threshold_json`, `owner_json` and `tags` are kept and refuse new values, so the v3 package reproof reads its real history (section 4);
- the veracity cap is read from the evidence of the Canonical Object versions an evaluation consumed; carrying veracity there is a named prerequisite (section 6);
- canonical pins are exact foreign keys; the backfill records dead pins by text with a reason, exempts first records from the months checks in writing, and refuses the identity fallback (section 5);
- the successor pin is named as a rule change with its exact keys (section 5.2);
- the database proposal lists every table, column, constraint, routine and rollback (section 9);
- the mark is per snapshot value, immutable, with an end-of-day as-of (section 6);
- minor fixes: "declared metric meaning", the Demoed read, counts, the baseline, format v1, and the revoke item of section 13.

Re-reading the live rows for this revision found dead pins the check did not name. Three metric pins of `a11a88f4` and `01a19aec` name contracts that bc-db 0079 also deleted, and the canonical pin cc-das36 5.2.0 names a version that does not exist (read live). Section 5.3 records them.

**Rulings it implements** (barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md`, branch `claude/operator-review-content`): proof facts out of engine code (7e6abc25); the code-versus-records principle (865747ae); rename to Customer Invoice Count (79fd49b7) by option B (b70e28c0); the catalog references the directory (8c72c819); FAQ upkeep after certification (ee5354f7); open months as is (2af2bb2d); direction on the definition, Customer Invoice Count neutral, certification held (de6d1fd8); platform side only (bd5d3ba0); write the first metric again (8e7b0bf6). The owner's earlier request, through the Chief on 2026-11-25, to store the ADR-9dce29 classification on the definition was withdrawn in revision 5 (3.4).

**Evidence base, read on 2026-11-25:**
- bc-core `origin/main` 762fb59c;
- bc-db `origin/main` 6d4d703 (PR 199 merged; the change since 29b2134 touches no migration);
- bc-docs `origin/main` 41cc7df;
- the auditor's view, bc-external-audit `docs/RESPONSE-Codex-gen-30fd6a-01-engine-code-vs-records-2026-11-25.md` ("the auditor's list" below);
- the two reviews, barecount-devhub `artifacts/chief/old-designs-review-metric-params-2026-11-25.md` (its 30 platform-side fields are cited as "field #n") and `artifacts/chief/portal-metric-needs-review-2026-11-25.md`;
- the Foundation check of revision 1, and the auditor's reply on revision 2 (both above);
- live rows, routines and views, read only, on `bc_platform_dev`.

In this note, `core:` means bc-core `src/` at 762fb59c.

## 1. The problem

Three facts about the first metric show the gap.

- **Meaning has two homes.** The directory member MDM-11fab0 and both its versions are named "Customer Invoice Volume". The catalog contract 8e8a6f28 is named "Customer Invoice Count" (`mcf.metric_contract.display_name`, read live). The tenant detail read returns the contract version's generated `description_text` as the description (`core:tenant-views/beyond-metrics.service.ts:251`), and the realization projection returns it as `definition_text` (`core:registry/mcf/mcf-realization-projection.service.ts:65`, `-v2.service.ts:115`).
- **The name cannot move to the next version.** `metric_directory.fn_member_frozen_guard` refuses any change to `member.display_name` while a current member version exists (read live). The supersede door copies the member row's name into each new version (`core:registry/metric-directory/member-version-supersede.ts:73,104`; `metric-directory.service.ts:2111`), and the name is inside the member version's content hash (`member-versioning.service.ts:140`).
- **Each new metric needs an engine change.** The world label, its evaluation dates, its canonical contract pins and its metric pins are four append-only code lists in `core:database/plane/`. The first Demoed run needed PR 1108, an engine-hold grant, an auditor landing and a serve move.

Two facts correct the starting picture:
- **The sealed package holds no meaning text.** Both live package snapshots contain neither "description" nor the metric's name (`mcf.mcv_package_snapshot.canonical_package_bytes`, read live), and `core:registry/mcf/mcf-package-v3.ts` hashes no description. The package also holds **no reference** to the definition version it realizes. What it does hash is `thresholds_digest` (`mcf-package-v3.ts:586`, from `mcv.threshold_json`, `mcf-package-input.build.ts:111`), and an output unit taken from the output binding's `unit_code_snapshot` (`mcf-package-input.build.ts:107`).
- **The months already have a governed home.** `demo.world_binding_data_period` holds the 41 months of binding e32071a8 (FY2023-24/P01 to FY2026-27/P05, read live), written once by the hand-over routine (bc-db 0082). No other binding has months.

## 2. The principle applied

The owner's test (865747ae): a change that alters platform behaviour is **code**, independently reviewed; a value declared under already governed behaviour is a **record**. A selection that changes authority (which world counts as truth) is a versioned record behind a recorded owner act.

Every record in this design keeps the Foundation:
- exact version pins, never "current";
- no change to an existing pin; a change is a successor record;
- restricted writers, append-only history;
- every proof records the exact records it used;
- the code-era lists are backfilled as frozen first records, and old and new readers are checked to agree before reads switch.

## 3. The definition version owns declared metric meaning

**Words used in this note.** The **definition** is the directory member version (`metric_directory.member_version`). The **metric contract version** is `mcf.metric_contract_version`. A metric contract version realizes exactly one definition version.

In this note, "meaning" is the **declared metric meaning**: what a definition version says the metric is. It is never evaluated. Foundation meaning in the sense of Invariant I is evaluated once, at canonical evaluation, and nothing here moves or repeats that.

The directory member version (`metric_directory.member_version`) already holds the name, the plain definition, the exact rule, the grain, the temporal intent and the output intent, all inside its content hash. This design adds what the old designs had and the current model lost, and removes every second home.

### 3.1 The name

**Rule:** the member version's `display_name` is the metric's name. Every reader reads the name from a member version: the current one for a directory screen, the exact pinned one for a contract or a proof.

- **Supersede takes the name from the act, not the member row.** `readSupersedeHead` stops returning the member row's name; the supersede input carries `displayName`, defaulting to the previous version's name, never the member row's. This is option B (b70e28c0): code only.
- **`member.display_name` becomes the registration label.** It stays frozen by `fn_member_frozen_guard` and is kept as history. No screen reads it.
- **Readers to move:** `directory-lens-projection.service.ts:51`, `metric-directory.service.ts:2016,2372,2467,2557` (the 2467/2557 envelope builders take the name of the version they build from), and the tenant reads (section 7).
- **The catalog label retires.** `mcf.metric_contract.display_name` is no longer written, and `PATCH /api/mcf/metric-contracts/:uid/display-name` (`core:registry/mcf/mcf-metric-rename.controller.ts:57`) is retired. Its two live values go into the evidence file of migration 0088, which then drops the column (4.2).
- **`mcf.metric_contract.mc_name` is a code, not a name.** It is NOT NULL and holds `customer_invoice_volume` on both live contracts (read live); `v_member_realized` returns it as `realized_mc_name`. It stays as the contract's machine key. No screen shows it as a name. For a new contract version, an insert check requires the parent contract's `mc_name` to equal the `member_code` of the definition version it realizes, so the key has one source (the member's frozen code).

### 3.2 The plain definition

`member_version.definition_text` is the one plain definition. Three second homes retire:
- **`mcv.description_text`** is no longer written (section 4); readers that used it read the definition version through the reference. Its two live values go into evidence and the column is dropped (4.2).
- **The mutable `metric_directory.member_knowledge`** (`definition_text`, `rationale_text`, `formula_intent_text`; 0 rows, read live) and its route `PATCH members/:memberUid/knowledge` (`metric-directory.controller.ts:555`) retire: meaning that can change without a new version breaks Invariant III. Its guard today freezes only the definition and formula fields while a version exists, and leaves `rationale_text` mutable (`fn_member_knowledge_frozen_guard`, read live). The database refuses every new write from 0085 (row 0085-E); after the route and its readers are gone, 0088 drops the table, its guard and the view `v_member_knowledge` (row 0088-F).
- **The six meaning columns of `mcf.metric_knowledge_profile`** (`definition_summary`, `definition_context`, `drivers_json`, `related_metric_names_json`, `stakeholders_json`, `search_tags_json`) are no longer written. Both live rows carry values in them, for example the generated text "finance / billing — Customer Invoice Volume" in `drivers_json` for 8e8a6f28. The table has no trigger today (read live). From 0086 the database refuses new values (row 0086-G); 0088 writes the values into evidence and drops the six columns (row 0088-G).

### 3.3 The interpretation: direction with its rationale

The definition version declares a **direction** from a governed list and a **rationale** in plain words, inside the content hash. A change of direction is a new definition version.

| Code | Label | Meaning |
|---|---|---|
| `higher_is_better` | Higher is better | exists in `master.master_metric_direction` |
| `lower_is_better` | Lower is better | exists |
| `target_is_optimal` | Within a target band | exists; the label is relabelled, the code kept so history reads the same |
| `neutral` | Neutral | **new**: the value describes activity; neither direction is good in itself |

- **What tenants own, later:** the target and band values a direction of `target_is_optimal` needs, and the thresholds (bd5d3ba0).
- **Two clauses of D053 are superseded.** ADR-0b3c08 (D053, implemented) lists metric direction as a tenant override (line 33), and makes thresholds "platform defines, tenant tunes" (title and line 31). The new ADR supersedes both clauses: direction is fixed on the definition, and thresholds have no platform value (tenants own them). The rest of D053 is unchanged.
- **ADR-8f09d9 is amended.** ADR-8f09d9 (implemented) places `unit` and `direction_code` "fixed" on the metric contract body (lines 138-139). That is a second placement. The new ADR moves both to the definition version; the contract body carries them only by its exact reference (section 4).
- **The legacy home retires.** `metric.metric_definition.direction_code` has 0 rows (read live) and is never read again.

### 3.4 The five dimensions: deferred

The five dimensions of ADR-9dce29 (purpose, shape, temporality, precision, impact) are **not stored** on the definition version. The owner ruled this on 2026-11-25 (9336dd8f): no code reads them, as the Chief checked in bc-core, bc-admin and bc-portal.

- **The rule is the one of 3.6:** no field without a reader. ADR-9dce29's metric dimensions return only with a feature that reads them.
- **The derived patterns are not built:** the Trust Filter, the Visualization Engine and Alerting. Nothing here prepares for them.
- **The masters stay as they are.** Nothing is dropped or changed in them.
- **The ADR-952faa temporality class is not one of the five.** It stays (3.4.1).
- **A doc to mark.** `metric-catalog.md` requires the five-dimension classification before approval and lists example values that are not in the live masters. The new ADR marks that requirement deferred, and the chapter is marked the same way with this design.

### 3.4.1 The temporality class (ADR-952faa D-1, D-2), declared

ADR-952faa (decided) D-1 requires a four-valued class: `instantaneous`, `flow_per_period`, `stock_at_period_end`, `cumulative_to_date`. Its D-2 refuses, at authoring and at activation, a formula primitive that the class does not allow; for example, a stock must not accept a period SUM. This design keeps both.

**Rule:** the definition version declares the class as `temporality_class_code`, one of the four values, in `member_version_interpretation`, inside the content hash. A change of class is a new definition version.

**Why declared, not derived.** A derivation from the temporal intent shape and its params is not unambiguous:
- `as_of` and `point_in_time` fit both `instantaneous` and `stock_at_period_end`;
- `period_aggregate` is the shape of a period total, and also the shape of the wrong formula ADR-952faa was written to stop: a period SUM labelled as a balance.

A class derived from the evaluation form can never disagree with that form, so D-2's refusal would have nothing to refuse. The class must be stated apart from the formula, as an explicit declaration (Invariants I and IV). This is the design act D-1 names (DEC-c48b0f); the checks below are its enforcement, not a substitute for it.

**The checks** (code at authoring; the database function of row 0086-H as a backstop). The aggregate nodes of the MCF formula grammar are `aggregate` (ops `sum`, `avg`, `count`, `count_distinct`, `min`, `max`, `median`, `percentile`; `core:registry/mcf/formula-canonicalization.service.ts:83`) and `aggregate_as_of` (op `sum` only, DEC-45200d; `:584-587`). The gate shapes are the seven of `mcf.metric_contract.temporal_gate_shape_code` (`mc_temporal_gate_shape_chk`, read live). The rule applies to **every** aggregate node of the formula, so a ratio of two aggregates is checked leg by leg.

| Class | Temporal intent and gate shapes | Aggregate nodes allowed | Refused (D-2) |
|---|---|---|---|
| `instantaneous` | `instantaneous`, `point_in_time` | none bucketed by period | `aggregate_as_of`; any aggregate under a period, window or cumulative gate |
| `flow_per_period` | `period_aggregate`, `trailing_window`, `rolling_window` | `aggregate`, any op | `aggregate_as_of`; the `as_of`, `point_in_time`, `instantaneous` and `cumulative_to_date` gates |
| `stock_at_period_end` | `as_of`, `point_in_time` | `aggregate_as_of`; an `aggregate` under an `as_of` gate (the open-item balance) | any aggregate under `period_aggregate`, `trailing_window`, `rolling_window` or `cumulative_to_date`: the period SUM, COUNT, AVG, MIN or MAX of D-2 |
| `cumulative_to_date` | `cumulative_to_date` | `aggregate` with op `sum` | `aggregate_as_of`; any other op; any other gate |

- **The temporal intent shape** of the definition and the **gate shape** of the contract are checked against the class in the table above. A `rolling` window shape is carried by `flow_per_period`.
- **The MCF forms of D-3's primitives.** D-3 names `BALANCE_AS_OF` and `CUMULATIVE_SUM`. MCF expresses them as an `aggregate_as_of` node or an aggregate under an `as_of` gate, and as a `sum` under a `cumulative_to_date` gate. The new ADR records this mapping.
- **Two boundaries, as D-2 requires.** At authoring, the definition-version and contract-version commands refuse a mismatch, naming the class, the offending node or gate, and the allowed set. At approval (review to approved, where the approval snapshot seals the package) and at activation (audit pending to active), `fn_mcv_state_transition_check` calls the same function and refuses (row 0086-J). Approval is checked too, because the package is sealed there.

**What exists today** (bc-core 762fb59c, `git grep` for `temporality_kind`, `flow_per_period` and the primitive names; read live):
- D-1's column exists only on the legacy `metric.metric_definition.temporality_kind`, which has 0 rows; MCF never reads it.
- D-2 is **not implemented** for any authoring or activation path. The only code is a read-side Inspector check of class against code (`core:admin-inspection/temporality-compatibility.ts`, `semantic-checks.ts`), which reads the legacy table. Its header says the primitive table (`KIND_ALLOWED_PRIMITIVES`) is on an unmerged D386 branch, and `src/registry/temporality-kind.ts` does not exist on main.
- No MCF authoring route, seal or state transition refers to the class.

This design therefore builds D-2 for MCF for the first time.

### 3.5 Unit, decimals and value format: one home

- **The unit:** a code from `master.master_unit_type` (11 codes, `count` among them; read live), declared on the definition version. Today `output_intent_json.unit_code` is null for both versions of MDM-11fab0. The next output-intent schema refuses a `unit_code` key, so the unit has one home.
- **The output binding's unit snapshot is not a declaration.** Package v3 takes its output unit from the output binding's `unit_code_snapshot` (`mcf-package-input.build.ts:107`). The package stays v3 (4), so the snapshot is still what the package hashes. No unit equality check is made between the snapshot and the definition version: the two use different vocabularies (for example `USD` or `rows` against `count` or `currency`). The unit-currency coherence check stays (4.3).
- **Display decimals:** 0 to 6 for a non-money unit. For `currency` the places are derived from the resolved currency, never declared (ADR-b1e9eb rule 1b).
- **The rounding mode** (half up, once, on the final value) is evaluation, on the contract (ADR-b1e9eb rule 3). The contract rounds to the definition's decimals through its exact reference (section 4).
- **The value format** (unit label, scale, currency symbol) is code reading the unit, the decimals and the contract's currency semantics. No format field is stored.

This places on the definition what the proposed ADR-b1e9eb placed on the contract version. ADR-b1e9eb is amended by the new ADR before it is decided.

### 3.6 Tags and data classification: not justified now

The seed reservoir's search synonyms and balanced-scorecard perspective (field #19), and a data classification or SOX-critical flag (field #30), have no platform reader and no rule that would use them. Neither is added. The owner decided on 2026-11-25 that they come later (section 12).

### 3.7 Where the new fields live

`metric_directory.member_version` already has 24 columns (read live), over the 20-column rule (DEC-1918d0 rule 6). The new fields therefore go in one new 1:1 child, `metric_directory.member_version_interpretation` (8 columns), written in the same transaction as its version.

- **Content hash:** the hash payload gains the interpretation under a new canonicalization value, `bc-directory-intent-canonicalization-v3` (code, `member-versioning.service.ts:130-160`). Both live versions declare `-v2` (read live).
- **Children digest:** a new digest algorithm value, `pg-jsonb-set-digest-v2`, adds the interpretation row to the children set. Both live versions declare `pg-jsonb-set-digest-v1` (read live), and their digests stay as they are.
- **Finalize:** every new member version must declare `pg-jsonb-set-digest-v2` and must have its interpretation row, or `fn_member_version_finalize` refuses it.

Versions made before it (05d067b2, d49b1b25) have no row; readers show "not declared". They are never backfilled, since their hashes are fixed.

### 3.8 Placement is declared meaning, owned by the directory

Where a metric sits (function, subfunction, family, group) is part of what it means. The directory already owns it: function, then subfunction, then family, then group, then member. `metric_directory.family` carries `(function_slug, subfunction_slug)` with the foreign key `fk_family_subfunction` to `master.master_subfunction(parent_function, slug)` (read live: 49 families, 119 subfunctions).

**The placement is pinned, not looked up.** A family row can change, but a member version pins the exact family version: `member_version.family_version_uid` is NOT NULL, and `metric_directory.family_version` (with `function_slug`, `subfunction_slug` and its own content hash) is immutable (`trg_family_version_immutable`, read live). The family and group version references are inside the member version's content hash (`member-versioning.service.ts:128-138`). So a metric contract version reaches its placement by one exact path: its reference row (section 4), then the definition, then that definition's family and group versions. No live row is followed, so a later move of the family or the member cannot change what an old metric contract version reads.

MDM-11fab0's two versions both pin family version 5ecaa51a (finance, billing, theme `billing_health`, question "Are we billing completely, and how much?") and group version ec729ddc (`ci_invoice_volume`) (read live).

**Rule:** `mcv.function_code` and `subfunction_code` are a second home of the placement (field #5). Readers move to the pinned path, the values go into evidence, and migration 0088 drops both columns (4.2).

#### 3.8.1 The six family-and-group rules (owner, 2026-11-25)

The owner adopted six rules (dda73851). No new master table is added.

**1. Masters stop at subfunction.** Function and subfunction are masters. A family and a group are versioned directory records. They are created only through the directory commands `POST /api/metric-directory/families` and `POST /api/metric-directory/groups` (`metric-directory.controller.ts:187,269`), each of which writes the record and its first version in one transaction. A master list of families or groups would give placement two homes.

**2. Codes are globally unique, follow a slug pattern, and are never reused.**
- Today `family.theme_code` is unique only within its subfunction (`uq_family_theme_active` on `(function_slug, subfunction_slug, theme_code) WHERE archived_at IS NULL`), and `group.group_code` only within its family (`uq_group_code_active` on `(family_id, group_code) WHERE archived_at IS NULL`) (read live).
- The live data already meets the new rule: 49 families with 49 distinct theme codes, 143 groups with 143 distinct group codes, and no archived row in either (read live).
- **The slug pattern** is `^[a-z][a-z0-9]*(_[a-z0-9]+)*$`. One family and one group fail it: the test fixture `zz_trackA_cefa537` (finance, general ledger; decision "fixture decision"; one group, which has a version; no definition under it) (read live). The CHECK is therefore added `NOT VALID`: every new row is checked, the fixture is not. The fixture is archived by the new archive command (section 8); its code stays reserved.
- **"Never reused" is not a partial index.** A unique index `WHERE archived_at IS NULL` lets a new row take an archived code. The design uses a **full** unique index on the code alone, so an archived row keeps its code taken for good. A soft delete keeps the row (DEC-1918d0 rule 8), but a hard delete would free the code. `bc_platform_runtime` has no DELETE on either table today; only `bc_schema_owner` has (read live). A delete trigger refuses every DELETE, so no writer can free a code (row 0085-I). A reserved-code record was weighed and not chosen: it would be a second home for the code.
- The code is already frozen once a version exists: `fn_family_frozen_guard` and `fn_group_frozen_guard` refuse a change of `theme_code` or `group_code` on a record with a current version (read live).

**3. Every family version states the question the family answers, phrased as a question.**
- `family_version.decision_text` holds it; it is NOT NULL today. Of the 49 family versions, 17 end in "?". Of the other 32, 8 are empty strings and 24 are descriptive notes, among them the fixture (read live).
- **Where it is enforced.** The family create command and the family version successor command refuse a `decision_text` that does not end in "?" after trimming, naming the field. The database backstop is a CHECK on `family_version` (row 0085-J), added `NOT VALID` because the 32 rows predate it. `family_version` is immutable (`fn_reject_mutation`), so those rows are never checked again; every new version is.
- **The 32 are reworded as new family versions**, never edited in place and never by migration data. The successor carries the question in `decision_text`; the old note moves into `rationale_text`, after the rationale already there. Function, subfunction and theme code do not change; a move is a new family. This is a metric-directory act through the directory command (`docs/onboarding/add-a-directory-family-and-group.md`). There is no DB row hand-edit. Today there is no family version successor command: `POST families/:familyId/version` authors only an absent v1 (`metric-directory.controller.ts:719`). The successor command is new (section 8). The fixture is archived, not reworded, so 31 are reworded.
- **The family row stops being read for the question.** `family.decision_text` and `rationale_text` are frozen once a version exists (`fn_family_frozen_guard`), and every family has a version, so `PATCH families/:familyId` can no longer change them on any live family. The row and the version already disagree on 8 families: the row holds NULL where the version holds an empty string (read live). Readers that read the row's text, for example `metric-directory.service.ts:2156`, move to the current family version.

**4. A group has no question of its own.** The group answers part of its family's question. No question field is added to `group` or `group_version`.

**5. A metric's place is read only through its definition's pinned family and group versions.** The coherence check already exists as four foreign keys (read live):
- `fk_member_version_group`: `member_version (group_id, group_version_uid)` → `group_version (group_id, group_version_uid)`;
- `fk_member_version_group_family_pair`: `member_version (group_version_uid, family_version_uid)` → `group_version (group_version_uid, family_version_uid)`, so the definition's family version is the one its group version names;
- `fk_group_version_family`: `group_version (family_id, family_version_uid)` → `family_version (family_id, family_version_uid)`;
- `fk_family_subfunction`: `family (function_slug, subfunction_slug)` → `master.master_subfunction (parent_function, slug)`.

No new key is added.

**6. The groups without a version get one before any metric is placed under them.** 29 of the 143 groups have no group version; 114 group versions exist (read live). `member_version.group_version_uid` is NOT NULL, so no definition can be placed under a group without one today. Each of the 29 gets its v1 through `POST groups/:groupId/version` (`metric-directory.controller.ts:729`), a metric-directory act. None of the 29 is the fixture's group.

#### 3.8.2 The group's declared unit and time class: one forward-compatible check

The structured group has its own design, written right after this one (TSK-09855b, owner 44ebbd53). This design adds one rule only:

**Rule:** where a group version declares a unit or a time class, the definition version placed under it must declare the same unit (`unit_type_code`, 3.5) and the same temporality class (`temporality_class_code`, 3.4.1). The definition-version command refuses a mismatch, naming the group version, the field and both values.

Today no group version declares either field, so the check is inert: it passes every definition. It becomes active when the group design adds the fields, with no change to this design.

The group is the batch-authoring unit. A fill-a-group command and the structured template belong to TSK-09855b.

`group.template_json` (and `group_version.template_json`) is free-form JSONB today, against DB rule 1 (no JSONB for queryable data): 141 of 143 groups carry a non-empty template, in 24 distinct shapes (read live). Its fix is left to the group design.

## 4. The contract version owns only evaluation

A metric contract version keeps what evaluation needs: formula AST, bindings, filters, grain, temporal gate, currency semantics, rounding and numeric profile. It **references** the definition version it realizes.

- **The reference has one home: a 1:1 child.** `mcf.metric_contract_version` has 19 columns (read live), and 13 after 0088 (4.2). The reference still lives in a new child, `mcf.mcv_realized_member_version`, because it must never change while the parent row stays editable as a draft, and a child insert-only row gives it its own guard: the contract version (PK), the member version it realizes, and that version's content hash, checked equal. It is written in the same transaction as the contract version and never changes. A new contract version without it is refused at commit. The two live contract versions predate it and have no row; they are never backfilled.
- **The realization event is tied to it.** `metric_directory.realization_event` (12 columns, read live) already names both `member_version_uid` and `metric_contract_version_uid`. A composite foreign key from the event's `(metric_contract_version_uid, member_version_uid)` to the child's same pair (unique) makes an assert name the version the contract realizes, or fail. Revoke rows carry NULLs in both and are not checked. The key is added `NOT VALID`, because the three historic asserts (b8c8f904, 1687e443, f5936579; read live) predate the reference; every new row is checked.
- **The package stays v3** (owner, 6e4a8803; package v4 is dropped). It hashes no reference, and `thresholds_digest` stays, computed over NULL (4.2). The reference is sealed by this child row instead: it is immutable, written before the metric contract version, carries the definition's content hash, and is required at commit. An audit decision or certification that names a metric contract version therefore pins exactly one definition. Package v4 would have rippled through the audit records and about 27 engine files to restate the same fact. No snapshot column is added.
- **The directory's acts stay on the event.** `realization_event` keeps assert, supersede and revoke: which contract the directory counts. The child says what a contract evaluates; the event says whether the directory currently counts it.

### 4.1 When the definition is superseded

**Rule:** a contract version keeps the definition version it was authored from (Invariant IV). Superseding the definition never moves a realization. The directory **keeps counting the older contract version** until a successor version of the **same metric contract** realizes the new definition. A new definition version is never realized by a new metric contract: `mc_name` equals `member_code` and is unique among live metric contracts (3.1). The one exception is Customer Invoice Count's fresh start, the owner's ruling (section 12, item 1), where the old metric contract 8e8a6f28 is archived first (section 10).

Today `supersedeMemberVersion` revokes the old realization and asserts it again on the new member version (`metric-directory.service.ts:2104-2120`). That move goes away. It was also refused whenever the contract version was `audit_pending`, because an assert needs `approved` or `active` (`fn_realization_event_guard`, read live: "interim: approved|active").

How the records read it (each grounded in the live definition):
- **`realization_operative`** is a table of one row per operative assert, keyed by member version, maintained by `fn_realization_operative_maint` (insert on assert, delete on supersede or revoke; read live). After definition v4 supersedes v3, the v3 contract's operative row stays on v3. Nothing is deleted.
- **`v_member_realized`** today reads the operative row only for `fn_current_member_version(member)` (read live). After v4, it would show the member as not realized. It changes: it reads the one operative row (variant NULL) among **all** versions of the member, and adds two columns at the end, `realized_member_version_uid` and `realizes_current_definition_flag`. A screen can then say "counted: contract version X, which realizes definition v3; the current definition is v4".
- **At most one operative row per member** (variant NULL) holds by a new rule in `fn_realization_event_guard`: an assert is refused while another version of the same member has an operative row. The existing rule that an assert targets the current member version stays.
- **When a successor contract version realizes v4**, one command writes two explicit events in one transaction: first the revoke of the v3 contract's operative assert, then the assert on v4. Each is recorded; nothing is moved silently.

### 4.2 Second homes dropped (owner ruling, 2026-11-25)

The owner decided to drop the retired columns, not keep them unused: they exist only on wrongly formed metrics. History is kept as evidence, not as live columns (Invariant III).

**What is dropped** (live values read 2026-11-25):

| Table | Columns | Live values | Columns before → after |
|---|---|---|---|
| `mcf.metric_contract_version` | `description_text`, `owner_json`, `threshold_json`, `tags`, `function_code`, `subfunction_code` | 2 rows, both `audit_pending`. `owner_json`, `threshold_json` and `tags` are NULL on both; `description_text` holds generated text on both; both carry `finance` / `billing` | 19 → 13 |
| `mcf.metric_contract` | `display_name` (3.1) | set on both rows | 17 → 16 |
| `metric_directory.member` | `realized_metric_contract_uid` | NULL on the one member | 17 → 16 |
| `metric_directory.member_knowledge` | the whole table, with its route (3.2) | 0 rows | 6 → dropped |
| `mcf.metric_knowledge_profile` | the six meaning columns (3.2) | values on both rows | 15 → 9 |

**The order: readers move first, then the drop.**
1. **Code.** Every reader stops naming the columns. A name search of bc-core `src/` (tests and fixtures excluded) finds 73 files for the function codes, 125 for `description_text`, 30 for `owner_json`, 12 for `threshold_json`, 11 for `realized_metric_contract_uid` and 4 for `member_knowledge`. Many of these are other tables with the same column name, so the census of the true readers is the first task of the code change. A bc-core CI check then refuses any reference to the dropped columns of these tables.
2. **Database routines and views that name them** (read live) are replaced in 0088: `fn_mcv_descriptive_immutability_check`, `fn_mcv_revision_emit` and `fn_mcv_package_identity_immutability_check` (`mcf`); `fn_rre_record_insert_guard` and `fn_wvr_record_insert_guard` (`mcf`); `fn_legacy_pointer_freeze` and `fn_member_knowledge_frozen_guard` (`metric_directory`); and the views `mcf.mcv_live`, `metric_directory.v_member_realized` and `metric_directory.v_member_knowledge`.
3. **The drop**, by migration 0088, only after the code of step 1 is served. Until then the interim refusals of 0085-E, 0086-B, 0086-C and 0086-G keep new values out.

**The values go into evidence first.** The two `description_text` values, the two `display_name` values and the knowledge-profile meaning values are written verbatim into a committed evidence file of 0088, each with its row id and its sha256. The function codes go in too, with the family version each agrees with. Before it drops anything, the migration computes each sha256 again from the live row and refuses on any difference, so the file holds exactly what was dropped. It also asserts, and refuses otherwise:
- `owner_json`, `threshold_json`, `tags` and `member.realized_metric_contract_uid` are NULL on every row, and `member_knowledge` has no row;
- each contract version's `function_code` and `subfunction_code` equal the `function_slug` and `subfunction_slug` of the family version pinned by the member versions its realization events name. Both live versions carry finance and billing; family version 5ecaa51a, pinned by both versions of MDM-11fab0, says the same.

**The v3 package reproof reads the recorded NULL, never a live column.** Package v3 hashes `thresholds_digest` from `mcv.threshold_json` (`mcf-package-input.build.ts:111`, `thresholds: asArrayOrNull(mcv.threshold_json)`), and `loadPackageInputRows` selects `description_text` and `threshold_json` from the live row (`:126`). `exactness-reproof.service.ts:33`, `reproducibility-reproof.service.ts:42` and `demoed-evidence-bridge.service.ts:42` all go through these two functions, so one change covers all three:
- `loadPackageInputRows` stops selecting `description_text` and `threshold_json`;
- `buildPackageV3Input` sets `thresholds` to NULL, the value every v3 package was sealed with;
- a v3 reproof first checks that the snapshot's `thresholds_digest` equals the digest of NULL thresholds, and refuses the reproof by name if it does not.

Both live approval snapshots (950f3ebd, b9357731) carry `thresholds_digest` `sha256:74234e98…f982b90b`, computed from a NULL `threshold_json` (read live). Migration 0088 asserts the same equivalence: for every v3 package snapshot, `threshold_json` is NULL on its contract version and the snapshot's `thresholds_digest` equals that NULL digest. The package stays v3 and keeps `thresholds_digest` over NULL (section 4).

### 4.3 Coherence holds for the life of the version

**The rules** (ADR-b1e9eb rule 2, both ways):
- a unit other than `currency` requires `aggregation_currency_code = 'not_applicable'`;
- a `currency` unit refuses `not_applicable`; it requires one of `document_currency`, `single_currency_required` or `local_currency`.

All four values are already allowed (`mcv_aggregation_currency_chk`, read live). Both live versions carry `document_currency` on a count.

**Why a check at insert is not enough.** `fn_mcv_package_identity_immutability_check` (bc-core `docker/redesign/44-mcf-c5-intrinsic-admission.sql`; read live) freezes `aggregation_currency_code`, `formula_ast_canonical_json`, `threshold_json`, `grain_entity_version_id` and `version_code` only when the version is in, or entering, `approved`, `active`, `audit_pending`, `audit_blocked` or `superseded`, or has an approval snapshot. While the version is a draft or in review without a snapshot, these fields can change. The parent's `temporal_gate_shape_code` is frozen on the same terms (`fn_mc_active_immutability_check`). So a `count` draft could pass the insert check at `not_applicable` and later move to `document_currency`.

**The rule:** coherence is one database function, `mcf.fn_mcv_definition_coherence(metric_contract_version_uid)` (row 0086-H). It checks unit against currency (both ways), and the temporality class against the formula and the gate shape (3.4.1). It runs:
- when the reference row is inserted (0086-A);
- on any UPDATE of `aggregation_currency_code` or `formula_ast_canonical_json` of a version that has a reference row (0086-I);
- on any UPDATE of `temporal_gate_shape_code` of a contract that has such a version (0086-I);
- at review to approved and at audit pending to active (0086-J).

**`mc_name` can change today.** No trigger on `mcf.metric_contract` reads `mc_name`, and `fn_mc_active_immutability_check` does not freeze it (read live; no bc-core code updates it). Its equality with the member code is therefore checked at insert and kept: once any version of the contract has a reference row, any change to `mc_name` is refused (0086-I).

### 4.4 Settled while building (2026-11-25/26)

The migrations were written against this design. Each point below was a choice made at writing. The migration header (bc-db PR 200, `migrations/0085_*.sql` to `0087_*.sql`, branch worktree `0085-metric-definition-meaning`) names it for review.

- **Compatibility latch (0085-D).** The design refused format v1 of the children digest for every new definition version. The served bc-core 762fb59c writes only v1 versions with no interpretation row, so that refusal would break authoring the moment 0085 applies. v1 is now refused once any definition version has committed as v2.
- **Archived rows are exempt from the slug CHECK on update (0085-G).** A legacy non-slug family or group can be archived. Its code is still never reused, because the unique index has no WHERE.
- **A BEFORE INSERT slug trigger (0085-G, 0085-H).** `fn_directory_code_slug_guard` refuses a non-slug code on insert whatever `archived_at` holds, so an already-archived row cannot reserve one.
- **The FAQ interpretation-citation guard (0085-F).** A BEFORE INSERT trigger refuses an entry that cites the interpretation of a definition version with no interpretation row (`faq_interpretation_missing`).
- **The reference is written children-first (0086-A).** It is written before its metric contract version, in the same transaction, as every member-version child is. A guard refuses a reference to a version that already exists (`mcv_reference_late`). A deferred check at commit requires the reference. The interpretation row follows the same order, so its shape check runs at commit (0085-B).
- **Writers run only as `bc_schema_owner` (0087-E).** Until a dedicated writer login exists, the 0087 routines grant EXECUTE to no login, and a direct INSERT by any other role is refused, the superuser included.
- **SELECT on the records goes to `bc_demo_runtime` (0087, build note 1).** `bc_platform_runtime` has no USAGE on schema `demo` (the plane boundary, D575), so the demo records are read by the demo login. The mark-reason master goes to `bc_platform_runtime`, as every master.
- **Same-transaction is read from `xmin` (0087, build note 3).** A point with its label, a mark with its snapshot and a reason with its mark are checked by the parent row's `xmin` being an in-progress transaction id visible to this one.
- **One point per period on a new label (0087, build note 5).** A new label's binding must be a demo-plane binding with months, and the label has one point per legal entity and period.
- **The calendar comes from `demo.fiscal_calendar_config` (0087, build note 6).** It is the loader's governed declaration, with exactly one active row covering the date.
- **Format v1 is refused on a binding with months (0087).** The hand-over refuses it (`answer_sheet_v1_refused_months_declared`). The bc-demo tool relies on the routine's refusal and adds no check of its own (bc-demo PR 27).

## 5. Proof facts as governed records

### 5.1 What the four code lists hold today

| Code list (`core:database/plane/`) | Holds | Rule today |
|---|---|---|
| `plane-world-identity.ts:51-56` | label → world code and world binding (4 labels) | append-only; a changed identity is a new label; labels with no entry "keep the label as their world code and take their binding from the act" (`:47`) |
| `plane-world-evaluation-coordinate.ts:41-68` | label → legal entities and as-of dates (5 labels) | append-only; the 41 dates of the world-months label match the declared months |
| `plane-cc-version-binding.ts:26-40` | label → {canonical contract name → version} (6 labels) | the whole entry frozen; also the fan-out exclusion `isPlanePinnedCcVersion` (`:98`), read by `schema-provisioner/contract-activation.service.ts` |
| `plane-metric-version-binding.ts:68-85` | label → {metric contract uid → version code} (5 labels) | frozen at the key; disjoint keys may be added; one version per (metric, binding), but the same version may sit on several labels, and a label with no binding is compared with every label (`:89-120`); usable only sealed and in `audit_pending`, `active` or `superseded` (`:196-223`) |

They are imported by 31 files outside the folder: 17 code files and 14 tests (for example `boundary/metric-spec-loader.ts`, `boundary/demo-metric-contract-pin-reader.ts`, `boundary/ccv2-canonical-resolver.service.ts`, `registry/mcf/demo-declaration-gate.ts`). Each read is synchronous today.

### 5.2 The records

Four tables in the `demo` schema, each immutable after insert, each written only by its own `SECURITY DEFINER` routine, and each row carrying `declared_by_name`, `declared_at` and `authority_ref_text`. Their columns are in section 9 (rows 0087-A to 0087-D).

| Record | Key and content | Rule |
|---|---|---|
| `demo.world_label` | `world_label_code`; the world (`synthetic_world_id`); its binding (`world_binding_id`, FK to `demo.foundry_world_binding`); `binding_source_code`; `backfilled_flag` | a label resolves to one physical world and one binding, and the binding belongs to that world; a changed identity is a new label. A new label must declare both. **There is no fallback:** a label with no record is refused. Only a backfilled first record may say `binding_source_code = 'from_act'`, which writes today's fallback down as an explicit fact (5.3) |
| `demo.world_label_evaluation_point` | label, legal entity (`demo.dim_legal_entity`), as-of date | for a new label: each as-of date's fiscal period, on the legal entity's declared calendar, must be a declared month of the label's binding (`demo.world_binding_data_period`), and the label's set must equal the declared months. Points are declared only with their label, in one call. A backfilled label is exempt (5.3) |
| `demo.world_label_cc_pin` | label, and the exact canonical contract version as a composite FK `(canonical_contract_id, version_code)` to `contract.canonical_contract_version` (its primary key; read live) | exact version; the version must have an immutable declaration (`pending_provisioning`, `active` or `superseded`); one version per canonical contract per label; a pin never changes; a disjoint canonical contract may be added (decision 3, section 12) |
| `demo.world_label_metric_pin` | label, exact `metric_contract_version_uid` (FK), optional `supersedes_metric_pin_id` | exact version, sealed and usable at the act; the keys and the successor rule are below |

**The metric pin keys, exactly:**
- `(world_label_code, metric_contract_version_uid)` is unique: a label pins a version once.
- `supersedes_metric_pin_id` is unique where it is not NULL: a pin has at most one successor.
- Per (label, metric contract), the pins form one chain. The first names no predecessor. Every later pin must name the chain's head (the pin no other pin supersedes) and a later `version_seq` of the same metric contract. The routine checks this under a row lock on the `mcf.metric_contract` row, so two writers cannot fork the chain. No metric contract uid is copied onto the pin row.
- A **live** pin is a chain head. Across the labels of one binding, the live pins of one metric must all name the same version. The same version on several labels of one binding stays allowed, as today.
- Earlier pins stay for the proofs that used them. A proof names the pin row it used.

**This is a rule change, named.** It amends DEC-49b574 G2-B1:
- rule 1 ("frozen at the key") becomes: a pin row never changes, and a declared successor pin may follow it on the same label;
- rule 3 ("a metric still cannot hold two versions on one binding", `plane-metric-version-binding.ts:105-107`) becomes: a metric cannot hold two **live** versions on one binding.

The new ADR records both amendments (section 11).

**The behaviour stays code.** Reading the records, refusing a missing or incompatible pin by name with no fallback to the global current version, the sealed-and-usable predicate, the tenant fan-out exclusion and the calendar check are all code. The readers become one loader that reads the records of the act's label once, in the act's snapshot. The proof writes the ids of the label, point and pin rows it used into its evidence.

**Who writes what:**

| Act | Writer | Authority |
|---|---|---|
| Declare a world label | `demo.fn_declare_world_label` | **owner act**: it selects the world that counts as truth (865747ae point 3) |
| Declare its evaluation points | the same routine, in the same call | owner act |
| Pin a canonical contract version | `demo.fn_pin_world_cc_version` | owner act for a new label; a metric act for a disjoint addition (decision 3, section 12) |
| Pin a metric version, or declare a successor pin | `demo.fn_pin_world_metric_version` | a metric act under standing grant ead781aa |

The routines always write `backfilled_flag = false`. `bc_platform_runtime` has SELECT on the four tables and no INSERT; only the routines and the backfill migration write.

### 5.3 Backfill: the code lists as frozen first records

One migration writes the six labels of the code lists at 762fb59c as first records, each with `backfilled_flag = true` and `authority_ref_text` naming the file, line and commit:
- `ar-balance-demo`, `ar-balance-demo-v2`, `kaveri-demo-v3lc5`;
- `kaveri-demo-v3lc5-v2`, `kaveri-demo-v3lc5-v2-p01-p04`, `kaveri-demo-v3lc5-v2-world-months`.

**Identity, written explicitly** (read live: `demo.synthetic_world` holds `ar-balance-demo` and `kaveri-demo-v3lc5`; `demo.foundry_world_binding` holds a6c55fa8 and e32071a8, both of the Kaveri world):
- `kaveri-demo-v3lc5`: the Kaveri world, binding a6c55fa8;
- `kaveri-demo-v3lc5-v2`, `-p01-p04` and `-world-months`: the Kaveri world, binding e32071a8;
- `ar-balance-demo`: its own world, no binding, `binding_source_code = 'from_act'`;
- `ar-balance-demo-v2`: no world row exists, so no world, `binding_source_code = 'from_act'`, `unusable_reason_code = 'world_not_declared'`.

**Evaluation points:** 49 rows. That is 2 for `ar-balance-demo` (DEMO-US-EAST and DEMO-US-WEST at 2025-03-31), 1 each for `kaveri-demo-v3lc5` and `kaveri-demo-v3lc5-v2` (KAVERI-IN at 2026-08-31), 4 for `-p01-p04` and 41 for `-world-months`. `ar-balance-demo-v2` has none.

**The months exemption, written in the migration.** The months and set-equality checks cannot hold for the first records: binding a6c55fa8 has no months; `ar-balance-demo` has no binding; the `-p01-p04` and `-v2` points are a subset of e32071a8's 41 months, not equal to them. The check trigger therefore skips the months and set-equality checks when the point's label has `backfilled_flag = true`. The migration header states this exemption, names the six labels, and says no later label may carry the flag (the routines never write it). The world-months label's 41 points do equal the declared months; the migration asserts that once, as a probe.

**Canonical pins:** 7 rows. These are cc-das36 4.0.0 (`ar-balance-demo`), 5.0.0 (`ar-balance-demo-v2`), and 5.1.0 (`kaveri-demo-v3lc5`, `-p01-p04`, `-world-months`); and on `kaveri-demo-v3lc5-v2`, cc-apl 1.0.0 and cc-das36 5.2.0. **cc-das36 5.2.0 does not exist** in `contract.canonical_contract_version` (read live; the highest is 5.1.0). It cannot take the exact foreign key, so it is recorded as a dead pin (below).

**Metric pins:** 6 rows.
- Two are live versions, as exact uids: b9357731 (contract fe91c450, v1) on `-p01-p04`, and 950f3ebd (contract 8e8a6f28, v1) on `-world-months`.
- Four are dead, because bc-db 0079 deleted every metric contract and only fe91c450 and 8e8a6f28 exist now (read live). These are a11a88f4 v1 on `ar-balance-demo`; 01a19aec v1 on `kaveri-demo-v3lc5` and on `kaveri-demo-v3lc5-v2`; and e6438795 v1 on `kaveri-demo-v3lc5`.

**A dead pin references by text, with a reason.** It is recorded with its foreign key columns NULL and three text fields set: the contract (`unusable_metric_contract_uid_text` or `unusable_canonical_contract_name_text`), the version (`unusable_version_code_text`), and `unusable_reason_code` (`contract_absent` or `version_absent`). A CHECK allows this form only on a backfilled row, and allows exactly one of the two forms. The loader refuses a dead pin by name. It is never resolved to anything.

**The agreement check before reads switch:** a test runs the old code reader and the new record reader and requires equal answers, including equal refusals, at two levels:
- for every label in the lists, reader by reader;
- for labels absent from the lists (spec-only worlds, and any unknown label), act by act. Today the identity reader takes such a label as its own world code; the new loader refuses it. The test lists every caller that reads identity alone. It requires each act under an absent label to be refused by both, today at the coordinate or pin read and under the records at the label read. If any act succeeds today under an absent label, the test fails, and that difference is decided before reads switch.

Only then do reads switch. The code lists are then deleted in a reviewed change.

### 5.4 The second-proof path: cells against the declared months

The world's months are written once per binding. A v2 hand-over on a binding that has months is refused (`answer_sheet_months_already_declared`, 0082:370-375).

**Read, not run:** format v1 is still accepted on such a binding (0082:296-307; the months check applies to v2 only). Its cells are checked against the months only later, at the Demoed declaration (`mcf.fn_demoed_declaration_covers_world_months`, 0083:122-150).

**Design:** a format v3, "cells against declared months", which:
- requires the binding to already have its months;
- refuses at hand-over any cell whose (legal entity, period) is not a declared month;
- refuses a sheet that does not cover every declared month for each (metric, version) it carries.

The same migration **refuses a new v1 hand-over on a binding that has months**, so the refusal happens at hand-over instead of at the later declaration. Sheets already handed over are unchanged. v2 is unchanged.

Every v1 rule (hashes, custody, the L4 class, the occupied-cell refusal) applies to v3 unchanged. A second metric, or a new version of the first, then needs only metric acts:
1. author and seal the version;
2. pin it on the binding's world-months label (a first pin, or a successor pin, 5.2);
3. hand over its v3 cells;
4. declare;
5. run.

There is no engine change and no new label.

## 6. The open-period mark: per-value evidence

Each snapshot value records whether it is final or preliminary, as evidence (Invariant VI), never on the definition.

**Grain:** one mark per snapshot value. On the demo plane, a value is a row of `demo.ms_snapshot` or `demo.ms_snapshot_ccy` (legal entity, period label, and currency where it applies; read live). In a tenant, a value is a row of `progression.metric_snapshot_index` (`core:database/schema/progression.ts:172`). `demo.metric_evaluation` has no period column (read live), so the mark cannot be per evaluation.

**Immutability:** the mark is written in the same transaction as the snapshot value it marks, and never updated or deleted. A value that later becomes final is a **new evaluation** with its own snapshot and its own mark. The earlier preliminary mark stays.

**The as-of instant:** an as-of date D means the end of day D, inclusive, on the legal entity's calendar. A period whose last day is E has ended at the as-of when E ≤ D, and the evaluation ran after the end of D. So an evaluation at a period-end date, run after that day, is not marked `open_period`.

- **`final`** when the period has ended at the as-of (above) and no Canonical Object version it consumed carries a capped veracity. An `unverified` input is refused, not marked (below).
- **`preliminary`** otherwise, with one or more reason codes:

| Reason code | When |
|---|---|
| `open_period` | the as-of falls inside the period, by the rule above. The engine already resolves the period at the as-of (`core:boundary/metric-evaluation-orchestrator.service.ts:205,255`); no closed-period rule exists today (2af2bb2d) |
| `source_veracity_cap` | a Canonical Object version the evaluation consumed carries veracity `approximate` in its evidence (ADR-f83b8a Trust Chain Filter) |

**Veracity is read from the Canonical Object evidence, never from Source Objects.** A metric evaluation reads Canonical Objects only (the-contract-grammar.md, Metric Contract, disallowed behaviours: "A Metric Contract references raw Source Objects"). ADR-f83b8a propagates veracity "source → observation contract trust → canonical evaluation trust → metric.precision" (lines 82-91). So the cap is code that reads the veracity in the evidence of the CO versions the evaluation consumed.

**A named prerequisite.** Today veracity lives on `source.source_object.veracity_code` (305 rows, all `authoritative`, read live), and CO evidence does not carry it. Carrying it is a declaration at the canonical boundary: canonical evaluation records the lowest veracity of the Source Objects it consumed in its CO evidence (repair location A/C). It is part of this design's design act (section 11) and is built before the mark. Until it is built, no mark is written, and readers show "not marked". A guessed `final` is never written. It never gates a metric's definition or its proof, and a second source type brings its own veracity with its own mapping.

**`unverified` is refused, not marked.** ADR-f83b8a says `unverified` blocks metric production, and this design follows it. Once CO evidence carries veracity, an evaluation that consumed a CO version whose evidence carries `unverified` is refused, naming those CO versions. It writes no snapshot and no mark. Only `approximate` leads to a `preliminary` mark (`source_veracity_cap`). Marking an `unverified` value `preliminary` instead would change ADR-f83b8a's rule and need its amendment (decision 4, section 12).

**Where it is recorded:** `demo.metric_snapshot_mark` with its reasons in `demo.metric_snapshot_mark_reason` (platform), and `progression.metric_snapshot_mark` with `progression.metric_snapshot_mark_reason` (each tenant database). A later accounting close (books closed by the tenant) is a tenant fact and a later design. How a tenant screen shows the mark is also later.

## 7. Platform reads a tenant screen needs

The reads go through `/api/t/beyond/*` (`core:tenant-views/beyond-metrics.service.ts`). They admit only `is_current = true` and `governance_state_code = 'active'` (`:113-116`).

| Field | Today | This design |
|---|---|---|
| Stable ID | a loop index (`metricSeq`, `:159,169`) | **new:** `member.member_uid` (MDM-11fab0) |
| Contract version code | returned (`versionCode`, `:252`) | exists |
| Definition version code | not returned | **new:** `member_version.version_coordinate`, through the reference |
| Name | the contract's `display_name` (`:171,247`) | **changed:** the referenced definition version's name |
| Plain definition | `mcv.description_text` (`:251`) | **changed:** the referenced `definition_text` |
| Interpretation (direction and rationale) | none | **new** |
| Unit, decimals, value format | none | **new:** unit and decimals as records; the format by code |
| Governance status | the portal infers it | **new read:** `governance_state_code` |
| Demoed status | no read | **new:** the `mcf.metric_version_demoed_result` cited by the served version's certification (verdict and coverage, with its id); before certification, every result of that version, each with its id. Never "the latest" |
| FAQ, customer audience | no read | **new:** entries of the referenced member version with `audience_code = 'customer'`; contract-side limitations stay platform-only (FAQ design, section 7) |
| Open-period mark | none (`BeyondSnapshot`, `:40-49`) | **new:** the mark and its reasons per value |
| Values per month | returned | exists |

Every name, definition and interpretation a tenant reads comes from the definition version the served contract version references, even when a later definition version is current (4.1).

## 8. Commands and records

**Commands (behaviour, code, independently reviewed):**

| Command | State |
|---|---|
| Author a definition version, taking the name, interpretation, temporality class, unit and decimals from the act | extend `POST members/:memberUid/version` and `/version/supersede` |
| Author a contract version from an exact definition version, recording the reference; the package stays v3 | extend the authoring route and the draft-writing service |
| Realize a new definition: revoke the older contract's operative assert, then assert the new one, in one transaction | change to the realization command (4.1) |
| The authoring checks: temporality class against temporal intent and gate shape, ADR-952faa D-2 class against every aggregate node, unit against currency both ways, unit algebra (ADR-b1e9eb Annex A) | new |
| The group check: a definition matches its group version's declared unit and time class, inert until the group declares them (3.8.2) | new, in the definition-version command |
| Create a family or a group: refuse a code outside the slug pattern or already taken by any row, archived or not; for a family, refuse a `decision_text` that is not a question (3.8.1) | extend `POST families` and `POST groups` |
| Declare a family version successor: the question in `decision_text`, the old note moved to `rationale_text`; function, subfunction and theme code unchanged (3.8.1 rule 3) | new; today only an absent v1 can be authored |
| Author the absent v1 of a group version, for the 29 groups without one (3.8.1 rule 6) | exists, `POST groups/:groupId/version` |
| Archive a family and its groups; their codes stay reserved (3.8.1 rule 2, for the fixture) | new; no archive command exists for either today |
| ADR-952faa D-2 and unit-currency coherence again at approval and at activation, and on every later change to the fields they read (4.3) | new: one database function and the state-transition check |
| Declare a world label and its evaluation points (owner act) | new routine |
| Pin a canonical contract version; pin a metric version or a successor pin | new routines |
| Hand over cells against declared months (format v3); refuse v1 on a binding with months | change to `demo.fn_hand_over_answer_sheet` |
| The record loader for proof facts, with the agreement check | new, replaces the four code lists |
| Carry veracity on CO evidence (canonical boundary prerequisite) | new, before the mark |
| Record the per-value mark | new, in the engine |
| The tenant reads of section 7 | extend |
| Rename the catalog label; edit member knowledge | **retired** |

**Records (values, under governed behaviour):** family and group versions; definition versions and their interpretation; contract versions and their reference; world labels, points and pins; answer sheets and months; Demoed declarations and results; FAQ entries; snapshot marks; the masters (direction, unit, mark reasons).

## 9. The database proposal — the owner's database yes was given (2026-11-25)

**Numbering:** bc-db migrations 0085 to 0088 and tenant migration 0008, **to be confirmed** at writing time. The highest merged is 0084 and the highest tenant migration is 0007 (bc-db `origin/main` 6d4d703). The open bc-db PRs are 177, 115, 111, 102 and 89. Of these, only 177 (0073) and 111 (0039) carry a migration file.

**For every row:** each new table has no UPDATE, DELETE or TRUNCATE (an immutability trigger, as `fn_reject_mutation`) and grants SELECT to `bc_platform_runtime`. INSERT goes only through the named routine or the engine's named writer. Every timestamp is `timestamptz NOT NULL` and every `*_by_name` and `authority_ref_text` is `text NOT NULL`, unless a row says otherwise. Each migration has its `rollback/NNNN_*.rollback.sql`, and is proven on an owner- and grant-faithful restore of a fresh read-only live dump, including `bc_platform_runtime` vectors, never on live. The live apply needs a separate recorded grant.

### 9.1 Migration 0085: declared meaning on the definition version

| # | Object | Change | Why |
|---|---|---|---|
| 0085-A | `master.master_metric_direction` (`direction_code` PK, `label`, `description`, `sort_order`, `archived_at`) | insert `neutral` ("Neutral"); set the label of `target_is_optimal` to "Within a target band" (code kept) | the ruled list (de6d1fd8) |
| 0085-B | `metric_directory.member_version_interpretation` (new, 8 columns) | `member_version_uid uuid` PK, FK `member_version`; `direction_code text` FK `master_metric_direction`; `direction_rationale_text text`; `temporality_class_code text` CHECK in (`instantaneous`, `flow_per_period`, `stock_at_period_end`, `cumulative_to_date`), the CHECK form ADR-952faa D-1 names; `unit_type_code text` FK `master_unit_type`; `display_decimal_count smallint` NULL; `created_by_name`; `created_at`. All NOT NULL except `display_decimal_count`. CHECKs: `display_decimal_count` is 0 to 6 when `unit_type_code <> 'currency'` and NULL when it is `currency`. Insert guard `fn_child_finalize_guard` (only in the version's creating transaction); the insert trigger also refuses a class the version's temporal intent shape cannot carry (3.4.1) | 3.3, 3.5, 3.4.1; `member_version` has 24 columns |
| 0085-C | `metric_directory.fn_member_version_children_digest` | new algorithm value `pg-jsonb-set-digest-v2`: the v1 set plus the interpretation row; v1 unchanged for old versions | 3.7 |
| 0085-D | `metric_directory.fn_member_version_finalize` | compare `children_set_digest` by the row's declared algorithm; refuse a new version that declares `pg-jsonb-set-digest-v1`; refuse a new version with no interpretation row | 3.7 |
| 0085-E | `metric_directory.member_knowledge` | interim, until 0088-F: replace `fn_member_knowledge_frozen_guard` with a guard that refuses every INSERT and UPDATE ("retired: declared meaning lives on the member version"); the table has 0 rows | 3.2, Invariant III |
| 0085-F | `metric_directory.member_version_faq_entry` | widen `ck_member_version_faq_entry_intent` (0084:187) from `temporal_intent`, `output_intent` to add `interpretation` | the direction entry cites the interpretation |
| 0085-G | `metric_directory.family` | drop `uq_family_theme_active`; create `uq_family_theme_code` UNIQUE `(theme_code)`, with no WHERE clause; add `ck_family_theme_code_slug` CHECK (`theme_code ~ '^[a-z][a-z0-9]*(_[a-z0-9]+)*$'`) `NOT VALID` (the fixture `zz_trackA_cefa537` predates it). Precondition, else refuse: the 49 theme codes are distinct across all rows | 3.8.1 rule 2 |
| 0085-H | `metric_directory."group"` | drop `uq_group_code_active`; create `uq_group_group_code` UNIQUE `(group_code)`, with no WHERE clause; add `ck_group_group_code_slug` CHECK, the same pattern, `NOT VALID` (the fixture's group predates it). Precondition, else refuse: the 143 group codes are distinct across all rows | 3.8.1 rule 2 |
| 0085-I | `metric_directory.family`, `metric_directory."group"` | new triggers `trg_family_no_delete` and `trg_group_no_delete`, `BEFORE DELETE FOR EACH ROW EXECUTE FUNCTION metric_directory.fn_reject_mutation()`: a row is archived, never deleted, so its code is never freed. Plus TRUNCATE refusal on both tables (the auditor's hardening item: a row-level DELETE trigger does not intercept TRUNCATE): a statement-level `BEFORE TRUNCATE` trigger on each, or `REVOKE TRUNCATE` from every role but the owner; the proof on the restore exercises both statements | 3.8.1 rule 2 |
| 0085-J | `metric_directory.family_version` | add `ck_family_version_decision_question` CHECK (`btrim(decision_text) ~ '\?$' AND length(btrim(decision_text)) > 1`) `NOT VALID`: the 32 versions that predate it are immutable and never checked again; every new version is | 3.8.1 rule 3 |

**Rollback 0085:** valid only before any member version declares `pg-jsonb-set-digest-v2`; after that it is refused and a forward fix is used (Invariant III). It drops the interpretation table, restores the v1-only digest and finalize, restores the knowledge guard and the FAQ check, deletes `neutral` if no row references it, and restores the old label.

**Rollback 0085-G to J** (may run on its own, at any time before any family or group is archived): drops `ck_family_version_decision_question`, `trg_family_no_delete`, `trg_group_no_delete`, the TRUNCATE refusal of 0085-I (trigger or restored privilege), `ck_family_theme_code_slug` and `ck_group_group_code_slug`; drops `uq_family_theme_code` and `uq_group_group_code`; recreates `uq_family_theme_active` ON `(function_slug, subfunction_slug, theme_code) WHERE archived_at IS NULL` and `uq_group_code_active` ON `(family_id, group_code) WHERE archived_at IS NULL`, as they stand today (read live). Once any family or group is archived, it is refused: the partial indexes would let a new row take an archived code. A forward fix is used instead. The rollback deletes no family version, so a reworded family version stays.

### 9.2 Migration 0086: the contract references its definition version

| # | Object | Change | Why |
|---|---|---|---|
| 0086-A | `mcf.mcv_realized_member_version` (new, 5 columns) | `metric_contract_version_uid uuid` PK, FK `metric_contract_version`; `member_version_uid uuid` FK `metric_directory.member_version`; `member_content_hash text`; `created_by_name`; `created_at`; all NOT NULL. Unique `(metric_contract_version_uid, member_version_uid)`; index on `member_version_uid`. Insert trigger: `member_content_hash` equals that version's `content_hash`; the version has an interpretation row; `mcf.fn_mcv_definition_coherence` (0086-H) passes; the parent contract's `mc_name` equals the version's `member_code` | section 4, 3.1, 4.3 |
| 0086-B | `mcf.metric_contract_version` (19 columns until 0088) | a deferred constraint trigger refuses, at commit, a new contract version with no 0086-A row (the two live versions predate it). Interim, until 0088-C: a non-NULL `description_text`, `owner_json`, `threshold_json` or `tags` is refused on insert, and on update of a version that has a 0086-A row | 4, 4.2 |
| 0086-C | `mcf.metric_contract` | interim, until 0088-D: refuse a non-NULL `display_name` on insert; `mc_name` kept as the machine key (3.1) | one name home |
| 0086-D | `metric_directory.realization_event` | composite FK `(metric_contract_version_uid, member_version_uid)` → 0086-A's unique pair, `NOT VALID` (the three historic asserts predate it; revokes carry NULLs) | one home for the pair (4) |
| 0086-E | `metric_directory.fn_realization_event_guard` | add to the assert branch: refuse while another version of the same member has an operative row for the same variant. The current-version rule, the state rule and the revoke branch are unchanged | 4.1 |
| 0086-F | `metric_directory.v_member_realized` | the operative row is read among all versions of the member (variant NULL), not only the current one; append `realized_member_version_uid` and `realizes_current_definition_flag` | 4.1 |
| 0086-G | `mcf.metric_knowledge_profile` | interim, until 0088-G: a new trigger refuses a non-NULL `definition_summary`, `definition_context`, `drivers_json`, `related_metric_names_json`, `stakeholders_json` or `search_tags_json` on INSERT, and any change to them on UPDATE | 3.2 |
| 0086-H | `mcf.fn_mcv_definition_coherence(uuid)` (new, `STABLE`) | for a contract version with a 0086-A row, returns the refusal codes, or none: unit not `currency` with a currency semantics other than `not_applicable`; unit `currency` with `not_applicable`; a temporality class whose gate shape (from the parent `mcf.metric_contract`) or any aggregate node of `formula_ast_canonical_json` falls outside the 3.4.1 table (ADR-952faa D-2). Each code names the field, the value and the allowed set | 3.4.1, 4.3 |
| 0086-I | update guards on `mcf.metric_contract_version` and `mcf.metric_contract` (new triggers) | on the version: an UPDATE of `aggregation_currency_code` or `formula_ast_canonical_json` of a version with a 0086-A row is refused when 0086-H returns any code for the new row. On the contract: once any of its versions has a 0086-A row, an UPDATE of `mc_name` is refused, and an UPDATE of `temporal_gate_shape_code` is refused when 0086-H returns any code for one of those versions | 4.3 |
| 0086-J | `mcf.fn_mcv_state_transition_check` | add: at review to approved, and at audit pending to active, a version with a 0086-A row is refused when 0086-H returns any code. The other transitions and their certificate rules are unchanged | 3.4.1 (D-2 activation gate), 4.3 |

**Rollback 0086:** valid only before any 0086-A row exists. It drops the FK, the child table, 0086-H and the triggers, and restores the realization guard, `fn_mcv_state_transition_check` and the view as they stand before 0086 (read live).

### 9.3 Migration 0087: proof facts as records, the hand-over, the mark

| # | Object | Change | Why |
|---|---|---|---|
| 0087-A | `demo.world_label` (new, 9 columns) | `world_label_code text` PK; `synthetic_world_id uuid` NULL, FK `demo.synthetic_world`; `world_binding_id uuid` NULL, FK `demo.foundry_world_binding`; `binding_source_code text` CHECK in (`declared`, `from_act`); `backfilled_flag boolean`; `unusable_reason_code text` NULL, CHECK in (`world_not_declared`); `declared_by_name`; `declared_at`; `authority_ref_text`. CHECK: `backfilled_flag` or (`binding_source_code = 'declared'` and world and binding NOT NULL and `unusable_reason_code` NULL). Trigger: the binding's world equals `synthetic_world_id` | 5.2 |
| 0087-B | `demo.world_label_evaluation_point` (new, 7 columns) | `world_label_evaluation_point_id uuid` PK; `world_label_code` FK; `legal_entity_id uuid` FK `demo.dim_legal_entity`; `as_of_date date`; `declared_by_name`; `declared_at`; `authority_ref_text`. Unique `(world_label_code, legal_entity_id, as_of_date)`. Trigger: unless the label is backfilled, the period of `as_of_date` on the entity's calendar is a declared month of the label's binding; a deferred trigger checks that the label's set equals the declared months | 5.2, 5.3 |
| 0087-C | `demo.world_label_cc_pin` (new, 11 columns) | `world_label_cc_pin_id uuid` PK; `world_label_code` FK; `canonical_contract_id uuid` NULL and `version_code text` NULL, composite FK to `contract.canonical_contract_version` PK; `unusable_canonical_contract_name_text`, `unusable_version_code_text`, `unusable_reason_code` (each `text` NULL; reason CHECK in `version_absent`, `contract_absent`); `backfilled_flag boolean`; `declared_by_name`; `declared_at`; `authority_ref_text`. CHECK: exactly one form (FK pair, or the three text fields on a backfilled row). Unique `(world_label_code, canonical_contract_id)`. Trigger: a new pin's version is `pending_provisioning`, `active` or `superseded` | 5.2, 5.3 |
| 0087-D | `demo.world_label_metric_pin` (new, 11 columns) | `world_label_metric_pin_id uuid` PK; `world_label_code` FK; `metric_contract_version_uid uuid` NULL, FK `mcf.metric_contract_version`; `supersedes_metric_pin_id uuid` NULL, FK self; `unusable_metric_contract_uid_text`, `unusable_version_code_text`, `unusable_reason_code` (each `text` NULL; reason CHECK in `contract_absent`); `backfilled_flag boolean`; `declared_by_name`; `declared_at`; `authority_ref_text`. CHECK: exactly one form, as 0087-C. Unique `(world_label_code, metric_contract_version_uid)`; unique `supersedes_metric_pin_id` where NOT NULL; index on `metric_contract_version_uid`. Trigger (under a lock on the metric contract row): the chain rule and the one-live-version-per-binding rule of 5.2; a new pin is sealed and usable | 5.2 |
| 0087-E | `demo.fn_declare_world_label`, `demo.fn_pin_world_cc_version`, `demo.fn_pin_world_metric_version` (new) | `SECURITY DEFINER`, `search_path` pinned; write `backfilled_flag = false` only; EXECUTE for `bc_platform_runtime`; no direct INSERT grant on 0087-A to D | 5.2 |
| 0087-F | the four tables | backfill the six labels, 49 points, 7 canonical pins and 6 metric pins of 5.3 with `backfilled_flag = true`; the header states the months exemption; a probe asserts the world-months set equals the 41 declared months | 5.3 |
| 0087-G | `demo.fn_hand_over_answer_sheet` | add format v3 (5.4); refuse a new v1 sheet on a binding with months; v2 unchanged | 5.4 |
| 0087-H | `master.master_evaluation_mark_reason` (new, 5 columns) | `reason_code text` PK; `label text`; `description text`; `sort_order integer`; `archived_at timestamptz` NULL (the masters' pattern). Rows: `open_period`, `source_veracity_cap` | 6 |
| 0087-I | `demo.metric_snapshot_mark` (new, 8 columns) | `metric_snapshot_mark_id uuid` PK; `metric_evaluation_id uuid` FK `demo.metric_evaluation`; `metric_snapshot_id uuid` NULL, FK `demo.ms_snapshot`, unique; `metric_snapshot_ccy_id uuid` NULL, FK `demo.ms_snapshot_ccy`, unique; `mark_code text` CHECK in (`final`, `preliminary`); `as_of_date date`; `period_end_date date`; `created_at`. CHECK: exactly one snapshot FK. Insert only in the snapshot's own transaction | 6 |
| 0087-J | `demo.metric_snapshot_mark_reason` (new, 2 columns) | `metric_snapshot_mark_id uuid` FK 0087-I; `reason_code text` FK 0087-H; PK the pair. A deferred trigger on 0087-I: `preliminary` has at least one reason, `final` has none | 6 |

**Rollback 0087:** valid only before any non-backfilled row exists in 0087-A to D, any v3 sheet, and any mark. It drops the mark tables and master, the routines and the four tables, and restores the hand-over routine as at 6d4d703.

### 9.4 Migration 0088: drop the second homes (owner ruling, 2026-11-25)

**Applied only after** the bc-core change of 4.2 step 1 is served: no reader names a dropped column, and the v3 reproof reads the recorded NULL. The header names the served bc-core commit. The evidence file is committed with the migration (for example `evidence/0088/retired-values.json`, path confirmed at writing).

| # | Object | Change | Why |
|---|---|---|---|
| 0088-A | preconditions (assert, else refuse the whole migration) | `owner_json`, `threshold_json`, `tags` NULL on every contract version; `member.realized_metric_contract_uid` NULL on every member; `member_knowledge` has no row; each contract version's `function_code` and `subfunction_code` equal the `function_slug` and `subfunction_slug` of the family version of the member versions its realization events name (a version with no realization event is recorded in the evidence with its values and not compared); for every v3 package snapshot, its version's `threshold_json` is NULL and its `thresholds_digest` equals the digest of NULL thresholds (`sha256:74234e98…f982b90b` on both live snapshots) | 4.2 |
| 0088-B | the evidence file | holds verbatim, per row id with a sha256 per value: the 2 `mcv.description_text` values, the 2 `mcf.metric_contract.display_name` values, the six meaning columns of the 2 knowledge-profile rows, and the 2 rows of `function_code` and `subfunction_code`. The migration computes every sha256 again from the live rows and refuses on any difference | 4.2, Invariant III |
| 0088-C | `mcf.metric_contract_version` | drop `description_text`, `owner_json`, `threshold_json`, `tags`, `function_code`, `subfunction_code` (19 → 13 columns). Replace `fn_mcv_descriptive_immutability_check`, `fn_mcv_revision_emit` and `fn_mcv_package_identity_immutability_check` so they no longer name them; redefine `mcf.mcv_live` without them; remove the interim part of 0086-B | 4.2, 3.8 |
| 0088-D | `mcf.metric_contract` | drop `display_name` (17 → 16 columns); drop the 0086-C trigger | 3.1 |
| 0088-E | `metric_directory.member` | drop `realized_metric_contract_uid` (17 → 16 columns). Replace `fn_legacy_pointer_freeze`, `mcf.fn_rre_record_insert_guard` and `mcf.fn_wvr_record_insert_guard` so they no longer read it; redefine `v_member_realized` (as 0086-F) without it | 4.2 |
| 0088-F | `metric_directory.member_knowledge` | drop the table (6 columns, 0 rows), `fn_member_knowledge_frozen_guard` and the view `v_member_knowledge`; the route is already gone (step 1) | 3.2 |
| 0088-G | `mcf.metric_knowledge_profile` | drop the six meaning columns (15 → 9 columns); drop the 0086-G trigger | 3.2 |

**Rollback 0088:** re-adds every dropped column (nullable) and the `member_knowledge` table, restores each value from the evidence file after checking its sha256, and restores the routines, views and interim triggers as they stand after 0087. The served code does not name the columns, so re-adding them does not break it. Values written to them after a rollback are not covered by the evidence file.

### 9.5 Tenant migration 0008: the mark in each tenant database

| # | Object | Change | Why |
|---|---|---|---|
| T-A | `progression.metric_snapshot_mark` (new, 6 columns) | `metric_snapshot_id uuid` PK, FK `progression.metric_snapshot_index`; `metric_evaluation_id uuid` FK `progression.metric_evaluation`; `mark_code text` CHECK in (`final`, `preliminary`); `as_of_date date`; `period_end_date date`; `created_at`; immutable | 6 |
| T-B | `progression.metric_snapshot_mark_reason` (new, 2 columns) | `metric_snapshot_id uuid` FK T-A; `reason_code text`; PK the pair. A foreign key to the platform master is impossible across databases, so a CHECK lists the same two codes as 0087-H; a new reason code needs both a platform and a tenant migration. The same deferred reason rule as 0087-J | 6 |

**Rollback tenant 0008:** valid only before any mark row exists; it drops both tables.

## 10. The first metric, written again

The first metric is retired as history and written again; nothing is deleted (Invariant III).

1. **Land the code and the migrations** above (0085 to 0087, then 0088 once the readers have moved; tenant 0008 is not needed for the Demoed run). The directory acts of 3.8.1 (31 family version successors, 29 group v1 versions, the fixture's archive) follow 0085 and the new commands; the first metric does not wait on them. The canonical-boundary veracity prerequisite (section 6) lands before the mark is written.
2. **Retire 950f3ebd** by the existing withdraw-retire act (as for b9357731, `mcf.withdrawn_version_retirement`), under standing grant ead781aa and the owner's ruling 8e7b0bf6. Its Demoed result 670bda65, declaration de6e03f8 and FAQ entries stay as history. Revoke its realization event f5936579 by the directory's revoke act; the revoke branch checks no contract state, so it is allowed while 950f3ebd is `audit_pending` (section 13). Contract 8e8a6f28 is archived, as fe91c450 was.
3. **Definition v3 of MDM-11fab0** supersedes d49b1b25, which stays as history (the member keeps its identity):
   - name "Customer Invoice Count";
   - definition text carried from v2 and re-read;
   - direction `neutral`, with the rationale "The count describes billing activity; more or fewer invoices is neither good nor bad without a target the customer sets.";
   - unit `count`, 0 decimals;
   - temporality class `flow_per_period`: invoices counted in the period of their event. It agrees with the temporal intent `period_aggregate` and the `count` aggregate (3.4.1);
   - placement through family version 5ecaa51a (finance, billing, theme `billing_health`) and group version ec729ddc (3.8). The family version already states a question and the group already has a version, so no directory act of 3.8.1 has to come before v3.
4. **A fresh contract** is authored from v3. Its reference row names v3's uid and content hash. Its `mc_name` is `customer_invoice_volume`, the member's code. It has `aggregation_currency_code = not_applicable`, carries no description, thresholds, owner, tags, function or subfunction (those columns are dropped by 0088, 4.2), and is sealed under package v3, with `thresholds_digest` over NULL. Its realization is asserted at `approved` (no other version of the member has an operative row after step 2), then it goes to audit.
5. **Proven again through the second-proof path:**
   - pin the new version on the label `kaveri-demo-v3lc5-v2-world-months` (a new metric contract, so a first pin, not a successor);
   - hand over its 41 cells in format v3 on binding e32071a8;
   - declare, run, and record the Demoed result.
6. **The FAQ carried forward**, each entry checked against v3 (FAQ design 2.5):
   - the five customer facts on d49b1b25 (ee5354f7, 2af2bb2d) are carried as new rows that name their source and cite v3's own elements;
   - a new fact cites the interpretation: why the count is neutral.
7. **Then certify** (held by de6d1fd8 until here).

## 11. Foundation gate (DEC-79b62f)

1. **Why this location.** The fix is at **B**, contract semantics: what a definition version declares (interpretation, temporality class, unit, placement) and that a contract references it. It is also at **C**, binding: the world, coordinate and pin facts are declarations of which versions a world proves. The mark is at **D**: the evaluation emits its own evidence (Invariant VI).
2. **Why not an upper layer.** Declared meaning is source-agnostic, so A has no part in sections 3 to 5. The mark does depend on A/C: the veracity cap needs the canonical boundary to carry veracity in its CO evidence, as ADR-f83b8a's propagation rule says. This design names that as a declaration at the canonical boundary and a prerequisite (section 6). The evaluation only reads it. It does not reach past the Canonical Objects to Source Objects, and it does not compensate at D for the missing evidence: until the evidence exists, no mark is written.
3. **Why not a lower layer.** Fixing names at the read model (F) or copying text at storage (E) would be compensation. The second homes being retired are exactly such copies (database rule 4). No working implementation is bypassed: the code lists' behaviour is kept, as records plus one loader, checked to agree. Three behaviours change, and each is named, not hidden:
   - the successor pin amends DEC-49b574 G2-B1 rules 1 and 3 (5.2);
   - the identity fallback for labels with no entry is refused instead of reproduced, except where a first record writes it down explicitly (5.3);
   - a v1 hand-over on a binding with months is refused at hand-over (5.4).
4. **Design act or execution act.** A **design act**, with these declarations named:
   - the interpretation and the temporality class on the definition version;
   - the placement (function, subfunction, family, group) read only through the definition version's pinned family and group versions, with the existing foreign keys of 3.8.1 rule 5 as the coherence check;
   - the directory's code identity: a family theme code and a group code are globally unique, follow a slug pattern and are never reused (3.8.1 rule 2);
   - the family's question, declared on every family version (3.8.1 rule 3);
   - the group's declared unit and time class as an authoring check, inert until TSK-09855b declares them (3.8.2);
   - the definition reference on the contract version (sealed by its child row, not by the package);
   - the storage home of DEC-3f6b1b's per-world binding (left open by that ADR);
   - veracity carried on CO evidence at the canonical boundary;
   - the per-value mark.

   It needs a new ADR that settles them and amends or supersedes, by name:
   - **D053 (ADR-0b3c08):** supersede the direction clause (line 33) and the threshold clause (line 31: no platform thresholds; tenants own them);
   - **ADR-8f09d9:** move `unit` and `direction_code` (lines 138-139) from the contract body to the definition version, referenced by the contract;
   - **ADR-952faa:** amend D-1 and P2.4 (lines 46-57): the class is stored as `temporality_class_code` on the definition version, not as `temporality_kind` on `metric.metric_definition`; P2.4's pairing of class with temporality code is not stored; the class is checked against the temporal intent and gate shapes (3.4.1). Amend D-2 and D-3 (lines 59-102): the class-to-primitive refusal is stated in MCF terms (aggregate nodes and gate shapes, 3.4.1) and runs at authoring, at approval and at activation;
   - **ADR-b1e9eb (proposed):** move unit and decimals from the contract version to the definition version;
   - **ADR-9dce29:** mark its metric dimensions deferred: they return only with a feature that reads them (3.4); the requirement in `metric-catalog.md` is marked the same way;
   - **DEC-49b574 G2-B1:** amend rules 1 and 3 for successor pins (5.2);
   - **ADR-f83b8a:** state that the metric reads veracity from CO evidence;
   - **DEC-b5c7ff (D506):** families and groups stay versioned directory records, never masters; codes globally unique and never reused; the family question mandatory on every version.

   **The execution acts that follow, named.** Rewording the 31 family versions, authoring v1 for the 29 groups and archiving the fixture are **metric-directory acts** through the directory commands (`docs/onboarding/add-a-directory-family-and-group.md`). They are not migration data edits, and no row is hand-edited. Each act is a successor or a first version, so history is kept (Invariant III).

**Foundation amendment flagged, not bypassed.** Amend `the-contract-grammar.md:208` (drop "thresholds"; "unit semantics" become "unit by reference to the realized definition version") and `:210` ("metric identity" and "result shape and units" become "the exact realized definition version (uid, content_hash)"; add that reference as a body element). Amend the Metric Directory Member section (`:379-384`) to own declared meaning and be referenced by the MCF Metric Contract. The realized state stays derived from the realization relation and is never cached on the member (DEC-b5c7ff). These amendments go through the Foundation's own procedure before the code lands.

## 12. Owner decisions (2026-11-25)

The owner answered every open question on 2026-11-25 (barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md`, commit 9336dd8f). None remains open.

1. **A new metric contract, as the owner's exception.** The fresh contract is a new contract uid, as the precedent was (fe91c450 to 8e8a6f28), not a v2 of 8e8a6f28 under a successor pin. This is an exception to the successor-version rule of 4.1; 8e8a6f28 is archived first.
2. **The meaning as written.** The neutral rationale and the temporality class of section 10 stand. There are no five dimensions (3.4).
3. **Canonical pins on an existing label.** Yes: a metric act may add a disjoint canonical contract pin to an existing label, as it may for metric pins. Existing pins never change.
4. **The `unverified` rule is unchanged.** Such an evaluation is refused, with no snapshot and no mark (section 6).
5. **Tags and data classification come later** (3.6).
6. **The first metric is not held for the structured group design.** Its time and output intents stay JSON inside the content hash until a later definition version moves them to columns (TSK-09855b). The owner ruled that structure lives in columns, not JSONB.
7. **The database yes for migration authoring was given.** Each migration is proven on an owner- and grant-faithful restore of a fresh read-only live dump before review. Every live apply needs its own recorded grant.

Earlier decisions of 2026-11-25 stand (former questions 5 and 7, and the family-and-group rulings):
- the retired columns are dropped, with their values kept as evidence (4.2, 9.4);
- function and subfunction leave the contract and are read through the definition version's pinned family version (3.8);
- the six family-and-group rules (dda73851; 3.8.1);
- the structured group is its own design (44ebbd53; TSK-09855b; 3.8.2).

## 13. What was not grounded

- **No proof yet:** no migration, routine or code path in this note has been written or run. The v1 hand-over on a binding with months is accepted by reading 0082, not by a run.
- **Tenant databases were not read:** `progression.metric_evaluation` and `progression.metric_snapshot_index` were read in code only, because the read tool reaches `bc_platform_dev` only.
- **Reason codes:** whether the withdraw-retire act accepts a reason code for "written again under the records design" was not checked.
- **Revocation state (closed in revision 2):** the revoke branch of `fn_realization_event_guard` returns before any contract-state check (read live), so revoking f5936579 while 950f3ebd is `audit_pending` is allowed.
- **The code-list readers:** the 17 code files that import the lists were counted, not read one by one. Which of them read identity alone (5.3) is left to the agreement check.
- **The D-2 checks on real formulas:** only the two live formulas (`count` under `period_aggregate`) were read. The 3.4.1 table is checked against the grammar's node kinds and gate shapes, not against a stock or cumulative metric, since none exists today.
- **The readers of the dropped columns:** the file counts of 4.2 come from a name search; the true readers are listed by the code change.
- **Where the snapshot is written:** that the demo and tenant snapshot rows are written in one transaction with their evaluation, so the mark can share it, was not read in the engine code.
- **The family and group commands that 3.8.1 needs do not exist yet** (read at bc-core 762fb59c): there is no family version successor command and no archive command for a family or a group. `POST families/:familyId/version` and `POST groups/:groupId/version` author only an absent v1. Both new commands are code (section 8).
- **A test fixture is live in the directory:** family `zz_trackA_cefa537` with one group of the same code. Its codes fail the slug pattern and its decision is not a question. The CHECKs of 0085-G, H and J are `NOT VALID` for this reason, and the fixture is archived, not reworded. Who created it, and whether anything outside the directory reads it, was not checked (its `created_by_name` is NULL; read live).
- **The delete trigger's message:** `fn_reject_mutation` says the table is "append-only". On `family` and `group`, which allow governed UPDATEs, the message is not exact. Reusing it was weighed against a new function; a dedicated message may be chosen at writing time.
- **The rewording itself:** the questions for the 31 families are not written in this note. Each is a directory act with its own wording.
