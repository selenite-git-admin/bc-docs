---
uid: metric-records-design
title: The metric records design, meaning on the definition version, evaluation on the contract version, and proof facts as governed records (design)
description: "Design for the owner's rulings of 2026-11-25: behaviour is code, values are records. The directory definition version owns a metric's meaning (name, plain definition, interpretation with direction, the five dimensions, unit and decimals, FAQ facts); the catalog contract version owns only evaluation and references the exact definition version it realizes; the per-world proof facts now kept as code lists in bc-core become governed records with a second-proof path; each evaluation records a preliminary or final mark. Platform side only. Customer Invoice Count is written again through it. Nothing is built."
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

*Design note · proposed 2026-11-25, revision 1 · nothing in this note has been built or run. Its database rows (section 9) are a proposal and **need the owner's database yes** under the Database Change Protocol before any migration is written.*

**Rulings it implements** (barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md`, branch `claude/operator-review-content`): proof facts out of engine code (7e6abc25); the code-versus-records principle (865747ae); rename to Customer Invoice Count (79fd49b7) by option B (b70e28c0); the catalog references the directory (8c72c819); FAQ upkeep after certification (ee5354f7); open months as is (2af2bb2d); direction on the definition, Customer Invoice Count neutral, certification held (de6d1fd8); platform side only (bd5d3ba0); write the first metric again (8e7b0bf6). The owner also asked, through the Chief on 2026-11-25, that the five-dimension classification (ADR-9dce29) be a first-class part of the definition, not an optional tag.

**Evidence base, read on 2026-11-25:**
- bc-core `origin/main` 762fb59c;
- bc-db `origin/main` 29b2134;
- bc-docs `origin/main` 41cc7df;
- the auditor's view, bc-external-audit `docs/RESPONSE-Codex-gen-30fd6a-01-engine-code-vs-records-2026-11-25.md` ("the auditor's list" below);
- the two reviews, barecount-devhub `artifacts/chief/old-designs-review-metric-params-2026-11-25.md` (its 30 platform-side fields are cited as "field #n") and `artifacts/chief/portal-metric-needs-review-2026-11-25.md`;
- live rows, read only, on `bc_platform_dev`.

In this note, `core:` means bc-core `src/` at 762fb59c.

## 1. The problem

Three facts about the first metric show the gap.

- **Meaning has two homes.** The directory member MDM-11fab0 and both its versions are named "Customer Invoice Volume". The catalog contract 8e8a6f28 is named "Customer Invoice Count" (`mcf.metric_contract.display_name`, read live). The tenant detail read returns the contract version's generated `description_text` as the description (`core:tenant-views/beyond-metrics.service.ts:251`), and the realization projection returns it as `definition_text` (`core:registry/mcf/mcf-realization-projection.service.ts:65`, `-v2.service.ts:115`).
- **The name cannot move to the next version.** `metric_directory.fn_member_frozen_guard` refuses any change to `member.display_name` while a current member version exists (read live). The supersede door copies the member row's name into each new version (`core:registry/metric-directory/member-version-supersede.ts:73,104`; `metric-directory.service.ts:2111`), and the name is inside the member version's content hash (`member-versioning.service.ts:140`).
- **Each new metric needs an engine change.** The world label, its evaluation dates, its canonical contract pins and its metric pins are four append-only code lists in `core:database/plane/`. The first Demoed run needed PR 1108, an engine-hold grant, an auditor landing and a serve move.

Two facts correct the starting picture:
- **The sealed package holds no meaning text.** Both live package snapshots contain neither "description" nor the metric's name (`mcf.mcv_package_snapshot.canonical_package_bytes`, read live), and `core:registry/mcf/mcf-package-v3.ts` hashes no description. The package also holds **no reference** to the definition version it realizes. What it does hash is `thresholds_digest` (`mcf-package-v3.ts:586`, from `mcv.threshold_json`, `mcf-package-input.build.ts:111`).
- **The months already have a governed home.** `demo.world_binding_data_period` holds the 41 months of binding e32071a8 (FY2023-24/P01 to FY2026-27/P05, read live), written once by the hand-over routine (bc-db 0082).

## 2. The principle applied

The owner's test (865747ae): a change that alters platform behaviour is **code**, independently reviewed; a value declared under already governed behaviour is a **record**. A selection that changes authority (which world counts as truth) is a versioned record behind a recorded owner act.

Every record in this design keeps the Foundation:
- exact version pins, never "current";
- no change to an existing pin; a change is a successor record;
- restricted writers, append-only history;
- every proof records the exact records it used;
- the code-era lists are backfilled as frozen first records, and old and new readers are checked to agree before reads switch.

## 3. The definition version owns meaning

The directory member version (`metric_directory.member_version`) already holds the name, the plain definition, the exact rule, the grain, the temporal intent and the output intent, all inside its content hash. This design adds what the old designs had and the current model lost, and removes every second home.

### 3.1 The name

**Rule:** the member version's `display_name` is the metric's name. Every reader reads the name from a member version: the current one for a directory screen, the exact pinned one for a contract or a proof.

- **Supersede takes the name from the act, not the member row.** `readSupersedeHead` stops returning the member row's name; the supersede input carries `displayName`, defaulting to the previous version's name, never the member row's. This is option B (b70e28c0): code only.
- **`member.display_name` becomes the registration label.** It stays frozen by `fn_member_frozen_guard` and is kept as history. No screen reads it.
- **Readers to move:** `directory-lens-projection.service.ts:51`, `metric-directory.service.ts:2016,2372,2467,2557` (the 2467/2557 envelope builders take the name of the version they build from), and the tenant reads (section 7).
- **The catalog label retires.** `mcf.metric_contract.display_name` is no longer written, and `PATCH /api/mcf/metric-contracts/:uid/display-name` (`core:registry/mcf/mcf-metric-rename.controller.ts:57`) is retired. Existing values stay as history.

### 3.2 The plain definition

`member_version.definition_text` is the one plain definition. Three second homes retire:
- **`mcv.description_text`** is no longer written for a new contract version (section 4); readers that used it read the definition version through the reference.
- **The mutable `metric_directory.member_knowledge`** (`definition_text`, `rationale_text`; 0 rows for MDM-11fab0) and its route `PATCH members/:memberUid/knowledge` (`metric-directory.controller.ts:555`) retire: meaning that can change without a new version breaks Invariant III.
- **The meaning fields of `mcf.metric_knowledge_profile`** (`definition_summary`, `definition_context`, `drivers_json`, `related_metric_names_json`, `stakeholders_json`, `search_tags_json`) are no longer written. The live row for 8e8a6f28 carries the generated text "finance / billing — Customer Invoice Volume" in `drivers_json`.

### 3.3 The interpretation: direction with its rationale

The definition version declares a **direction** from a governed list and a **rationale** in plain words, inside the content hash. A change of direction is a new definition version.

| Code | Label | Meaning |
|---|---|---|
| `higher_is_better` | Higher is better | exists in `master.master_metric_direction` |
| `lower_is_better` | Lower is better | exists |
| `target_is_optimal` | Within a target band | exists; the label is relabelled, the code kept so history reads the same |
| `neutral` | Neutral | **new**: the value describes activity; neither direction is good in itself |

- **What tenants own, later:** the target and band values a direction of `target_is_optimal` needs (bd5d3ba0).
- **D053 is superseded in one clause.** ADR-0b3c08 line 33 lists metric direction as a tenant override. That clause is superseded by a new ADR that fixes direction on the definition, consistent with ADR-8f09d9 (`direction_code` "fixed", line 139). The rest of D053 is unchanged.
- **The legacy home retires.** `metric.metric_definition.direction_code` has 0 rows (read live) and is never read again.

### 3.4 The five dimensions (ADR-9dce29), first-class

Each dimension is meaning, declared once per definition version, mandatory before approval (`docs/operating-model/metric-catalog.md`, "Five-Dimensional Classification"), from its governed master (read live):

| Dimension | Governed set (live master) | What today's intents already carry | Placement |
|---|---|---|---|
| Purpose | `master_metric_purpose`: performance, efficiency, operational, predictive, diagnostic, reference | nothing | new declared code |
| Shape | `master_metric_shape`: scalar, distribution, time_series, ratio_pair | `output_intent_json` carries value type and dimension kind (`integer`, `count`), not the shape | new declared code; its parameters (bucket set, granularity) are declared only when the engine evaluates a non-scalar shape |
| Temporality | `master_metric_temporality`: point_in_time, period, rolling, cumulative | `temporal_intent_json.shape_code` (`period_aggregate`) and its params (`period_type`) carry the evaluation form | new declared code, checked against the temporal intent (below); `window_days` and `reset_boundary` stay in the temporal intent's params, never copied |
| Precision | `master_metric_precision`: flash, final | nothing | new declared code: the precision the metric is meant to reach (section 6 reconciles it with each evaluation's mark) |
| Impact | `master_metric_impact`: financial, time, quality, volume, risk, compliance, satisfaction | nothing | new declared code |

- **No duplication with the intents.** The temporal intent is the evaluation form; the temporality code is the reader's class. They are not two copies of one value: an authoring check (code) refuses a temporality code that its temporal intent's shape cannot produce. This follows the compatibility-table approach of ADR-952faa P2.4. The finer kind of ADR-952faa D-1 (a balance at a point, or an amount over a period) is already carried by the temporal intent's shape (`as_of` versus `period_aggregate`), so it gets no column.
- **The derived patterns stay code.** The Trust Filter (precision × impact, the "Preliminary" watermark), the Visualization Engine (shape × purpose) and Alerting Logic (temporality × purpose) are behaviour that reads the codes; none is stored per metric (ADR-9dce29: "a rendering rule, not stored per-metric"). Alerting is tenant work, later. ADR-9dce29's collision rules (for example: refuse `reference` with `flash`) become authoring checks.
- **A doc to correct.** `metric-catalog.md` lists example values (`monetary`, `exact`, `cash` and others) that are not in the live masters. The masters are the governed sets; that chapter's table is corrected with this design.

### 3.5 Unit, decimals and value format: one home

- **The unit:** a code from `master.master_unit_type` (11 codes, `count` among them; read live), declared on the definition version. Today `output_intent_json.unit_code` is null for both versions of MDM-11fab0. The next output-intent schema refuses a `unit_code` key, so the unit has one home.
- **Display decimals:** 0 to 6 for a non-money unit. For `currency` the places are derived from the resolved currency, never declared (ADR-b1e9eb rule 1b).
- **The rounding mode** (half up, once, on the final value) is evaluation, on the contract (ADR-b1e9eb rule 3). The contract rounds to the definition's decimals through its exact reference (section 4).
- **The value format** (unit label, scale, currency symbol) is code reading the unit, the decimals and the contract's currency semantics. No format field is stored.

This places on the definition what the proposed ADR-b1e9eb placed on the contract version. ADR-b1e9eb is amended by the new ADR before it is decided.

### 3.6 Tags and data classification: not justified now

The seed reservoir's search synonyms and balanced-scorecard perspective (field #19), and a data classification or SOX-critical flag (field #30), have no platform reader and no rule that would use them. Neither is added. Open question 6 asks the owner.

### 3.7 Where the new fields live

`metric_directory.member_version` already has 24 columns (read live), over the 20-column rule (DEC-1918d0 rule 6). The new fields therefore go in one new 1:1 child, `metric_directory.member_version_interpretation`, written in the same transaction as its version. It is covered by the version's content hash (a new directory schema version of the hash payload, `member-versioning.service.ts:130-160`) and by `children_set_digest`. Versions made before it (05d067b2, d49b1b25) have no row; readers show "not declared". They are never backfilled, since their hashes are fixed.

## 4. The contract version owns only evaluation

A metric contract version keeps what evaluation needs: formula AST, bindings, filters, grain, temporal gate, currency semantics, rounding and numeric profile. It **references** the definition version it realizes:

- **Two new columns** on `mcf.metric_contract_version`: `realized_member_version_uid` (FK to the member version) and `realized_member_content_hash` (checked equal to that version's `content_hash`). Both are required on a new version and never change.
- **The package records the reference.** A new package version (v4, code) hashes `{member_version_uid, content_hash}` into the package signature. It drops `thresholds_digest`, since thresholds are tenant-owned. No snapshot column is added: `mcv_package_snapshot` already has 35 columns, so the reference lives in the package bytes and signature only.
- **The realization record.** `metric_directory.realization_event` keeps the directory's acts (assert, supersede, revoke: which contract the directory counts). A new assert must name the version the contract's column names. The column says what a contract evaluates; the event says whether the directory currently counts it.
- **Supersede never moves a realization.** Today `supersedeMemberVersion` revokes the old realization and asserts it on the new member version (`metric-directory.service.ts:2104-2120`). An assert needs the contract version in `approved` or `active` (`fn_realization_event_guard`, read live: "interim: approved|active"), so a move is refused while the contract is `audit_pending`. Under this design a contract version keeps the definition version it was authored from (Invariant IV); a new definition version is realized by a new contract version. The move, and the refusal, go away.
- **Retired from new contract versions:** `description_text`, `owner_json`, `threshold_json`, `tags` (the last three are NULL on both live versions), the catalog `display_name` (section 3.1), and the meaning fields of the knowledge profile (section 3.2).
- **Currency for a non-money unit.** `aggregation_currency_code` must be `not_applicable` when the referenced unit is not `currency` (ADR-b1e9eb rule 2). The value is already allowed (`mcv_aggregation_currency_chk`, read live); a check on insert enforces the coherence. Both live versions carry `document_currency` on a count.

**Not moved here:** `mcv.function_code` and `subfunction_code` duplicate the family's function and subfunction (field #5). Open question 7.

## 5. Proof facts as governed records

### 5.1 What the four code lists hold today

| Code list (`core:database/plane/`) | Holds | Rule today |
|---|---|---|
| `plane-world-identity.ts:51-56` | label → world code and world binding | append-only; a changed identity is a new label |
| `plane-world-evaluation-coordinate.ts:41-68` | label → legal entities and as-of dates | append-only; the 41 dates of the world-months label match the declared months |
| `plane-cc-version-binding.ts:26-40` | label → {canonical contract name → version} | the whole entry frozen; also the fan-out exclusion `isPlanePinnedCcVersion` (`:98`), read by `schema-provisioner/contract-activation.service.ts` |
| `plane-metric-version-binding.ts:68-85` | label → {metric contract uid → version code} | frozen at the key; disjoint keys may be added; one version per (metric, binding) (`:89-120`); usable only sealed and in `audit_pending`, `active` or `superseded` (`:196-223`) |

They are read by 17 files outside the folder (for example `boundary/metric-spec-loader.ts`, `boundary/demo-metric-contract-pin-reader.ts`, `boundary/ccv2-canonical-resolver.service.ts`, `registry/mcf/demo-declaration-gate.ts`). Each read is synchronous today.

### 5.2 The records

Four tables in the `demo` schema, each immutable after insert, each written only by its own `SECURITY DEFINER` routine, and each row carrying `declared_by_name`, `declared_at` and `authority_ref_text`:

| Record | Key and content | Rule from the auditor's list |
|---|---|---|
| `demo.world_label` | `world_label_code`, the world (`synthetic_world_id`), its binding (`world_binding_id`, NULL only for a backfilled label that names none) | a label resolves to one physical world and one binding; a changed identity is a new label |
| `demo.world_label_evaluation_point` | label, legal entity, as-of date | each as-of date's fiscal period, on the legal entity's declared calendar, must be a declared month of the label's binding (`demo.world_binding_data_period`); a new label's set must equal the declared months |
| `demo.world_label_cc_pin` | label, canonical contract (`contract.canonical_contract`), version code | exact version; the version must have an immutable declaration (`pending_provisioning`, `active` or `superseded`); a pin never changes; a disjoint canonical contract may be added (open question 3) |
| `demo.world_label_metric_pin` | label, exact `metric_contract_version_uid`, optional `supersedes_metric_pin_id` | exact version, sealed and usable at the act; one live pin per (metric, binding); a new version of the same metric on the same binding is a **declared successor pin**, and the earlier pin stays for the proofs that used it |

**The behaviour stays code.** Reading the records, refusing a missing or incompatible pin by name with no fallback to the global current version, the sealed-and-usable predicate, the tenant fan-out exclusion and the calendar check are all code. The readers become one loader that reads the records of the act's label once, in the act's snapshot. The proof writes the ids of the label, point and pin rows it used into its evidence.

**Who writes what:**

| Act | Writer | Authority |
|---|---|---|
| Declare a world label | `demo.fn_declare_world_label` | **owner act**: it selects the world that counts as truth (865747ae point 3) |
| Declare its evaluation points | the same routine, in the same call | owner act |
| Pin a canonical contract version | `demo.fn_pin_world_cc_version` | owner act for a new label; a metric act for a disjoint addition (open question 3) |
| Pin a metric version, or declare a successor pin | `demo.fn_pin_world_metric_version` | a metric act under standing grant ead781aa |

### 5.3 Backfill: the code lists as frozen first records

One migration writes the six labels of the code lists at 762fb59c as first records, each with `authority_ref_text` naming the file, line and commit:
- `ar-balance-demo`, `ar-balance-demo-v2`, `kaveri-demo-v3lc5`;
- `kaveri-demo-v3lc5-v2`, `kaveri-demo-v3lc5-v2-p01-p04`, `kaveri-demo-v3lc5-v2-world-months`.

The metric pins are backfilled as exact version uids. These are resolved from the contract uid and the version code, so a pin whose contract no longer exists (`e6438795`, deleted by bc-db 0079) is recorded with no version uid and marked unusable. `ar-balance-demo-v2` has no `demo.synthetic_world` row (read live); it is recorded with no world.

**The agreement check before reads switch:** a test runs the old code reader and the new record reader over every label in the lists, and requires equal answers, including equal refusals. Only then do reads switch. The code lists are then deleted in a reviewed change.

### 5.4 The second-proof path: cells against the declared months

The world's months are written once per binding. A v2 hand-over on a binding that has months is refused (`answer_sheet_months_already_declared`, 0082:370-375).

**Read, not run:** format v1 is still accepted on such a binding (0082:296-307; the months check applies to v2 only). Its cells are checked against the months only later, at the Demoed declaration (`mcf.fn_demoed_declaration_covers_world_months`, 0083:122-150).

**Design:** a format v3, "cells against declared months", which:
- requires the binding to already have its months;
- refuses at hand-over any cell whose (legal entity, period) is not a declared month;
- refuses a sheet that does not cover every declared month for each (metric, version) it carries.

Every v1 rule (hashes, custody, the L4 class, the occupied-cell refusal) applies unchanged. A second metric, or a new version of the first, then needs only metric acts:
1. author and seal the version;
2. pin it on the binding's world-months label;
3. hand over its v3 cells;
4. declare;
5. run.

There is no engine change and no new label.

## 6. The open-period mark: per-evaluation evidence

The precision on the definition (section 3.4) says what the metric is meant to reach. Each evaluation records what it **did** reach, as evidence (Invariant VI), never on the definition:

- **`final`** when the definition's precision is `final`, the evaluated period has ended at the evaluation's as-of instant, and no source object it read is capped.
- **`preliminary`** otherwise, with one or more reason codes:

| Reason code | When |
|---|---|
| `open_period` | the as-of instant falls inside the period. The engine already resolves the period at the as-of (`core:boundary/metric-evaluation-orchestrator.service.ts:205,255`); no closed-period rule exists today (2af2bb2d) |
| `declared_flash` | the definition's precision is `flash` |
| `source_veracity_cap` | a source object read has veracity `approximate` (ADR-f83b8a Trust Chain Filter) |

**System-agnostic.** Veracity belongs to the source side, `source.source_object.veracity_code` (305 rows, all `authoritative`, read live), never to the definition. The cap is code applied to the sources an evaluation actually read. It never gates a metric's definition or its proof, and a second source type brings its own veracity with its own mapping. ADR-f83b8a says `unverified` blocks metric production; whether that refuses the evaluation or marks it is open question 4.

**Where it is recorded:** one row per evaluation beside `progression.metric_evaluation` (the tenant databases; `core:database/schema/progression.ts:140`) and beside `demo.metric_evaluation` for demo runs. A later accounting close (books closed by the tenant) is a tenant fact and a later design. How a tenant screen shows the mark is also later.

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
| The five dimensions | none | **new** |
| Unit, decimals, value format | none | **new:** unit and decimals as records; the format by code |
| Governance status | the portal infers it | **new read:** `governance_state_code` |
| Demoed status | no read | **new:** the latest `mcf.metric_version_demoed_result` (verdict and coverage) of the served version |
| FAQ, customer audience | no read | **new:** entries of the referenced member version with `audience_code = 'customer'`; contract-side limitations stay platform-only (FAQ design, section 7) |
| Open-period mark | none (`BeyondSnapshot`, `:40-49`) | **new:** the mark and its reasons per value |
| Values per month | returned | exists |

## 8. Commands and records

**Commands (behaviour, code, independently reviewed):**

| Command | State |
|---|---|
| Author a definition version, taking the name, interpretation, dimensions, unit and decimals from the act | extend `POST members/:memberUid/version` and `/version/supersede` |
| Author a contract version from an exact definition version, recording the reference, with package v4 | extend the authoring route and the draft-writing service |
| The authoring checks: dimension sets, temporality against temporal intent, ADR-9dce29 collisions, unit against currency, unit algebra (ADR-b1e9eb Annex A) | new |
| Declare a world label and its evaluation points (owner act) | new routine |
| Pin a canonical contract version; pin a metric version or a successor pin | new routines |
| Hand over cells against declared months (format v3) | change to `demo.fn_hand_over_answer_sheet` |
| The record loader for proof facts, with the agreement check | new, replaces the four code lists |
| Record the per-evaluation mark | new, in the engine |
| The tenant reads of section 7 | extend |
| Rename the catalog label; edit member knowledge | **retired** |

**Records (values, under governed behaviour):** definition versions and their interpretation; contract versions and their reference; world labels, points and pins; answer sheets and months; Demoed declarations and results; FAQ entries; evaluation marks; the masters (direction, unit, the five dimensions, mark reasons).

## 9. The database proposal — needs the owner's database yes

**Numbering:** bc-db migrations 0085 to 0087 and tenant migration 0008, **to be confirmed**. The highest merged is 0084. No open bc-db PR (177, 115, 111, 102, 89, 199) carries a file at 0085 or above.

| # | Migration | What | Change | Why |
|---|---|---|---|---|
| 1 | 0085 | `master.master_metric_direction` | add row `neutral`; relabel `target_is_optimal` "Within a target band" (code kept) | the ruled list (de6d1fd8) |
| 2 | 0085 | `metric_directory.member_version_interpretation` (new, about 13 columns) | `member_version_uid` (PK, FK); `direction_code` (FK); `direction_rationale_text`; `purpose_code`, `shape_code`, `temporality_code`, `precision_code`, `impact_code` (each an FK to its master); `unit_type_code` (FK); `display_decimal_count` (0-6; NULL only for `currency`); `created_by_name`; `created_at`. All NOT NULL except as noted; no update, delete or truncate; covered by `children_set_digest`; SELECT and INSERT for `bc_platform_runtime` | meaning on the definition (3.3-3.5); `member_version` is already at 24 columns |
| 3 | 0085 | `metric_directory.member_version_faq_entry` | widen `ck_member_version_faq_entry_intent` (0084:187) from `temporal_intent`, `output_intent` to add `interpretation` | the direction entry cites the interpretation |
| 4 | 0086 | `mcf.metric_contract_version` | add `realized_member_version_uid` (FK) and `realized_member_content_hash`, required on insert, immutable, the hash checked; refuse a non-NULL `description_text` on insert; drop `owner_json`, `threshold_json`, `tags` (NULL on both live rows; the package reader moves first); a check that a non-currency unit has `not_applicable`; index on `realized_member_version_uid`. Columns 19 → 18 | the explicit reference (section 4); rule 6 |
| 5 | 0086 | `mcf.metric_contract` | refuse a non-NULL `display_name` on insert; existing values kept | one name home (3.1) |
| 6 | 0087 | `demo.world_label`, `demo.world_label_evaluation_point`, `demo.world_label_cc_pin`, `demo.world_label_metric_pin` (new) | the four records of 5.2, their routines and grants, immutability triggers, the calendar and months checks, one live pin per (metric, binding) with successor pins; indexes by label and by metric version | proof facts out of engine code (7e6abc25) |
| 7 | 0087 | the same four tables | backfill the six labels of 762fb59c as frozen first records (5.3) | the auditor's list: backfill before reads switch |
| 8 | 0087 | `demo.fn_hand_over_answer_sheet` | add format v3, cells against declared months (5.4); v1 and v2 unchanged | the second-proof path |
| 9 | 0087 | `master.master_evaluation_mark_reason` (new) and `demo.metric_evaluation_mark` (new) | the three reason codes; one mark row per demo evaluation (mark code, reason codes as rows, not JSONB) | the open-period mark (6) |
| 10 | tenant 0008 | `progression.metric_evaluation_mark` (new) | the same mark per tenant evaluation | the open-period mark (6) |

Each migration is proven on an owner- and grant-faithful restore of a fresh read-only live dump, including `bc_platform_runtime` vectors, never on live. The live apply needs a separate recorded grant.

## 10. The first metric, written again

The first metric is retired as history and written again; nothing is deleted (Invariant III).

1. **Land the code and the migrations** above (rows 1-9; row 10 is not needed for the Demoed run).
2. **Retire 950f3ebd** by the existing withdraw-retire act (as for b9357731, `mcf.withdrawn_version_retirement`), under standing grant ead781aa and the owner's ruling 8e7b0bf6. Its Demoed result 670bda65, declaration de6e03f8 and FAQ entries stay as history. Revoke its realization event f5936579 by the directory's revoke act. Contract 8e8a6f28 is archived, as fe91c450 was.
3. **Definition v3 of MDM-11fab0** supersedes d49b1b25, which stays as history (the member keeps its identity):
   - name "Customer Invoice Count";
   - definition text carried from v2 and re-read;
   - direction `neutral`, with the rationale "The count describes billing activity; more or fewer invoices is neither good nor bad without a target the customer sets.";
   - unit `count`, 0 decimals.
4. **The five dimensions, for the owner's confirmation:**

   | Dimension | Proposed | Reason |
   |---|---|---|
   | Purpose | `operational` | it says what is happening in billing; ADR-9dce29 puts an invoice count under operational |
   | Shape | `scalar` | one number per legal entity and period |
   | Temporality | `period` | invoices posted in the fiscal period; agrees with `period_aggregate` |
   | Precision | `final` | it is meant to be exact on posted records; an open month is marked `preliminary` per evaluation (6) |
   | Impact | `volume` | throughput: ADR-9dce29 puts an invoice count under volume |

5. **A fresh contract** is authored from v3. It records v3's uid and content hash, has `aggregation_currency_code = not_applicable`, has no description, thresholds, owner or tags, and is sealed under package v4. Its realization is asserted at `approved`, then it goes to audit.
6. **Proven again through the second-proof path:**
   - pin the new version on the label `kaveri-demo-v3lc5-v2-world-months` (a new metric uid, a disjoint key);
   - hand over its 41 cells in format v3 on binding e32071a8;
   - declare, run, and record the Demoed result.
7. **The FAQ carried forward**, each entry checked against v3 (FAQ design 2.5):
   - the five customer facts on d49b1b25 (ee5354f7, 2af2bb2d) are carried as new rows that name their source and cite v3's own elements;
   - a new fact cites the interpretation: why the count is neutral.
8. **Then certify** (held by de6d1fd8 until here).

## 11. Foundation gate (DEC-79b62f)

1. **Why this location.** The fix is at **B**, contract semantics: what a definition version declares (interpretation, dimensions, unit) and that a contract references it. It is also at **C**, binding: the world, coordinate and pin facts are declarations of which versions a world proves. The mark is at **D**, the evaluation emits its own evidence (Invariant VI).
2. **Why not an upper layer.** A (source and admission) is not involved. Meaning is source-agnostic, and veracity stays on the source side, applied per evaluation (6).
3. **Why not a lower layer.** Fixing names at the read model (F) or copying text at storage (E) would be compensation. The second homes being retired are exactly such copies (database rule 4). No working implementation is bypassed: the code lists' behaviour is kept, as records plus one loader, checked to agree.
4. **Design act or execution act.** A **design act**, with these declarations named:
   - the interpretation and the five dimensions on the definition version;
   - the definition reference on the contract version and in its package;
   - the storage home of DEC-3f6b1b's per-world binding (left open by that ADR);
   - the per-evaluation mark.

   It needs a new ADR that settles them, supersedes the direction clause of D053, amends the proposed ADR-b1e9eb's placement of unit and decimals, and moves ADR-9dce29's storage home from `metric.metric_definition` to the member version.

**Foundation amendment flagged, not bypassed.** `the-contract-grammar.md:208,210` says a Metric Contract declares "thresholds, and unit semantics" and "result shape and units". This design keeps the unit on the contract by explicit reference to the definition version, and moves thresholds to tenant records. Both need a grammar amendment through the Foundation's own procedure before the code lands.

## 12. Open questions for the owner

1. **A new contract or a new version.** Author the fresh contract as a new contract uid, as the precedent did (fe91c450 to 8e8a6f28), or as v2 of 8e8a6f28 under a successor pin (5.2)? The note assumes a new uid for the first metric.
2. **The neutral rationale wording** in step 3, and the five-dimension values in step 4.
3. **Canonical pins on an existing label.** May a disjoint canonical contract pin be added to an existing label by a metric act, as metric pins may? The code rule today freezes the whole entry; the auditor's list states the disjoint rule for metric pins only.
4. **`unverified` sources:** refuse the evaluation, or mark it `preliminary`?
5. **The old columns.** Drop `member.realized_metric_contract_uid` (NULL on the one live member) and, after reads switch, `mcf.metric_contract.display_name` and `mcv.description_text`, or keep them as history? This note keeps them.
6. **Tags and data classification** (3.6): add them now or later?
7. **Function on the contract.** `mcv.function_code` and `subfunction_code` duplicate the family's: move to the definition in this design or a later one?

## 13. What was not grounded

- **No proof yet:** no migration, routine or code path in this note has been written or run. The v1 hand-over on a binding with months is accepted by reading 0082, not by a run.
- **Tenant databases were not read:** `progression.metric_evaluation` was read in code only, because the read tool reaches `bc_platform_dev` only.
- **Engine shapes:** whether the engine evaluates any shape other than `scalar` today was not checked. Until it does, the authoring check admits `scalar` only.
- **Reason codes:** whether the withdraw-retire act accepts a reason code for "written again under the records design" was not checked.
- **Revocation state:** whether the realization revoke is allowed while 950f3ebd is `audit_pending` was not checked; `fn_realization_event_guard` was read for the assert branch only.
- **Column counts:** the column count of the four new demo tables and the exact routine signatures are left to the builder, within the 20-column rule.
- **The code-list readers:** the 17 reader files were listed, not read one by one.
