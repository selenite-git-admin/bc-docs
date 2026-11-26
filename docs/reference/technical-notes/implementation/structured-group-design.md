---
uid: structured-group-design
title: The structured metric group, concept-grounded (design)
description: "Design for TSK-09855b. It implements the draft Foundation amendment on concept grounding (bc-docs PR 276, revision 4) and replaces the free-form group template with typed tables: group version parts by role, the event input, age bands, the breakdown set and its versions, and the derived-group inputs. It extends the typed member layer, defines the per-role reachability checks as database routines, the four directory commands with their refusal codes, the proof cases, the sweep plan for all 143 groups from live reads, and the database proposal for the owner's yes. Nothing is built."
status: drafting
authority: reference
date: 2026-11-26
project: bc-docs
domain: metrics
subdomain: metric-directory/group
focus: design
governing_adr: DEC-79b62f
---

# The structured metric group, concept-grounded

*Design note, revision 1, 2026-11-26. Nothing in it is built, recorded or written. Counts were read live from `bc_platform_dev` on 2026-11-26 (read-only). Re-read them before acting.*

## 0. Authority and inputs

| Input | Exact reference |
|---|---|
| The authority | The draft amendment, bc-docs PR 276, head `11a9b034`, `docs/governance/proposals/foundation-amendment-concept-grounded-metrics.md` (revision 4). Section numbers below written "A§n" point into it. |
| The auditor's requirements | bc-external-audit `docs/RESPONSE-Codex-gen-52eda8-01-concept-grounded-metrics-2026-11-26.md`, point 5 and the ADR-set paragraph (origin/main `f28c72da`). |
| The records design it builds on | bc-docs PR 275, head `e63d0c1f`, `metric-records-design.md`; its migrations 0085, 0086 and 0087 are bc-db PR 200. 0088 is planned there. |
| The directory chapter | `docs/operating-model/metric-directory.md` (sections 5 and 6, corrected by A§3.4). |
| The engine | bc-core origin/main `762fb59c`: `src/registry/metric-directory/` (`metric-directory.service.ts`, `member-versioning.service.ts`, `metric-directory.controller.ts`), `src/boundary/governed-selection.ts`, `src/boundary/metric-variable-resolver.ts`, `src/common/formula/as-of-schedule-declaration.ts`. |

If this design and the amendment disagree, the amendment wins and this design is corrected.

## 1. What is there today (live)

| Fact | Value |
|---|---|
| Groups / group versions | 143 / 114; 29 groups have no version |
| `group` columns | 11; `template_json jsonb NOT NULL` |
| `group_version` columns | 15; `grain_entity_id` and `temporal_anchor_concept_id` with no FK; `template_json jsonb` NULL |
| `template_json` keys | `kind` 140, `op` 113, `temporal_gate_shape` 49, `closing_concept_id` 11, `note` 1 |
| Anchors | 69 groups; all 69 are active date concepts on the grain; every group version agrees with its group |
| Member layer | `member_version` 2 rows; `_discriminator` 2; `_direct_input` 2; `_dependency` 0; `_constant` 0 |
| Live members | 1 (Customer Invoice Count, under `ci_invoice_volume`) |
| Group mutation routes | `PATCH groups/:groupId/temporal-anchor` and `/temporal-gate` rewrite the group row and its JSON, guarded only by `assertNoGovernedGroupVersion` |

The member children are already immutable (`fn_reject_mutation`) and insert-only inside their version's transaction (`fn_child_finalize_guard`). This design follows the same pattern for every new table.

## 2. The typed tables

### 2.1 Rules for every new table

- UPDATE, DELETE and TRUNCATE are refused (`fn_reject_mutation`, and a statement-level TRUNCATE trigger as in 0085-I).
- Group version children are inserted only in the transaction that creates their group version (`fn_child_finalize_guard`). Breakdown entries likewise, with their set version.
- `created_at timestamptz NOT NULL`, `created_by_name text NOT NULL`.
- Every concept reference is a pair `(*_concept_id, *_concept_version_id)` with a composite FK to `concept_registry.business_concept_version (concept_id, concept_version_id)`, as `fk_disc_bcv` does. Every entity reference is a pair with a composite FK to `entity_version (entity_id, entity_version_id)`, as `fk_di_ev` does.
- SELECT is granted to `bc_platform_runtime`. INSERT goes only through the directory commands' writer.
- No JSONB anywhere. Every table is under 20 columns.

### 2.2 `metric_directory.group_version_grammar` (new, 1:1, 12 columns)

The typed parameters of a group version (A§3.2, A§3.3).

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | PK; FK `(group_version_uid, class_code)` and FK `(group_version_uid, grain_entity_id)` to two new unique indexes on `group_version` |
| `class_code` | text | no | `base` or `derived` |
| `grain_entity_id` | uuid | no | composite FK with the next column |
| `grain_entity_version_id` | uuid | no | `entity_version` |
| `measure_kind_code` | text | yes | `entity_count`, `count_distinct`, `sum` |
| `time_class_code` | text | yes | `flow`, `stock_as_of` (ADR-952faa master) |
| `open_model_code` | text | yes | `gross_binary`, `residual` |
| `derivation_code` | text | yes | `ratio`, `percentage_of_total`, `delta` |
| `reporting_anchor_kind_code` | text | yes | `input_anchor`, `evaluation_point` |
| `canonicalization_version` | text | no | `bc-directory-group-canonicalization-v2` |
| `created_at`, `created_by_name` | | no | |

Checks. `base`: measure kind and time class set; derivation and reporting anchor kind NULL. `derived`: derivation and reporting anchor kind set; measure kind, time class and open model NULL. `open_model_code` is set exactly when `time_class_code = 'stock_as_of'`.

### 2.3 `metric_directory.group_version_part` (new, 11 columns)

The semantic references, one row per role (A§3.1). Single-valued roles have ordinal 1.

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | FK `group_version_grammar` |
| `role_code` | text | no | `measure`, `context`, `period_anchor`, `closing`, `age_anchor`, `axis`, `reporting_anchor` |
| `part_ordinal` | smallint | no | ≥ 1; = 1 unless `axis` |
| `concept_id`, `concept_version_id` | uuid | no | the target concept version |
| `step_reference_concept_id`, `step_reference_concept_version_id` | uuid | yes | the grain's reference concept version |
| `step_target_entity_id`, `step_target_entity_version_id` | uuid | yes | the target entity version |
| `created_at`, `created_by_name` | | no | |

PK `(group_version_uid, role_code, part_ordinal)`. The four step columns are all NULL or all set. A step is allowed only on `axis` and `period_anchor`. The target concept of a step is the part's own concept, so a step names exactly the three pinned versions of A§3.7.

### 2.4 `metric_directory.group_version_age_band` (new, 7 columns)

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | FK `group_version_grammar` |
| `band_code` | text | no | slug pattern of 0085-H |
| `lower_day_count` | integer | no | ≥ 0 |
| `upper_day_count` | integer | yes | NULL is open-ended; else > `lower_day_count` |
| `band_ordinal` | smallint | no | unique per group version |
| `created_at`, `created_by_name` | | no | |

PK `(group_version_uid, band_code)`. A deferred trigger refuses overlapping bands and refuses bands unless the grammar is `stock_as_of` and an `age_anchor` part exists.

### 2.5 `metric_directory.group_version_event_input` (new, 1:1, 16 columns)

The separately pinned event-grain canonical input for a residual group (A§3.7).

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | PK; FK `group_version_grammar` |
| `event_entity_id`, `event_entity_version_id` | uuid | no | `entity_version` |
| `canonical_contract_id` | uuid | no | composite FK with the next column to `contract.canonical_contract_version` |
| `canonical_contract_version_code` | text | no | |
| `grain_reference_concept_id`, `_version_id` | uuid | no | reference on the event entity, target the grain |
| `grain_key_concept_id`, `_version_id` | uuid | no | the grain's identity concept |
| `event_date_concept_id`, `_version_id` | uuid | no | a date on the event entity |
| `anchor_date_concept_id`, `_version_id` | uuid | no | a date on the grain |
| `anchor_sign` | smallint | no | −1 or +1; no default (DEC-45200d (1)) |
| `created_at`, `created_by_name` | | no | |

The anchor amount is the group's `measure` part. The table exists only when `open_model_code = 'residual'` (deferred check both ways).

### 2.6 `metric_directory.group_version_event_leg` (new, 9 columns)

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | FK `group_version_event_input` |
| `leg_ordinal` | smallint | no | ≥ 1 |
| `key_concept_id`, `key_concept_version_id` | uuid | no | reference on the event entity, target the grain |
| `amount_concept_id`, `amount_concept_version_id` | uuid | no | amount on the event entity |
| `leg_sign` | smallint | no | −1 or +1 |
| `created_at`, `created_by_name` | | no | |

PK `(group_version_uid, leg_ordinal)`. Unique `(group_version_uid, key_concept_version_id, amount_concept_version_id)`: no repeated pair. At least one leg (deferred check).

### 2.7 `metric_directory.group_version_derived_input` (new, 6 columns)

The input slots of a derived group (A§3.3).

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | FK `group_version_grammar`, class `derived` |
| `input_role_code` | text | no | `numerator`, `denominator`, or `operand_` plus a slug |
| `input_group_version_uid` | uuid | no | FK `group_version` |
| `period_offset_count` | integer | no | default 0; −60 to 0 |
| `created_at`, `created_by_name` | | no | |

PK `(group_version_uid, input_role_code)`. `ratio` needs exactly `numerator` and `denominator`; `delta` needs two operands; `percentage_of_total` needs `numerator` and `denominator`. The offset lives here, not on the member's dependency: it is the group's shape, shared by every sibling (A§3.3 lists it in the group grammar).

### 2.8 `metric_directory.group_version_constant_slot` (new, 5 columns)

`group_version_uid` (FK grammar, class `derived`), `constant_role_code` (slug), `value_type_code` (`integer`, `decimal_string`, `boolean`, `date`), `created_at`, `created_by_name`. PK `(group_version_uid, constant_role_code)`. A member supplies the value (2.12).

### 2.9 `metric_directory.group_version_breakdown_set_version` (new, 8 columns)

| Column | Type | Null | Key or check |
|---|---|---|---|
| `breakdown_set_version_uid` | uuid | no | PK |
| `group_version_uid` | uuid | no | FK `group_version_grammar` |
| `set_version_number` | integer | no | ≥ 1; unique with the group version |
| `supersedes_breakdown_set_version_uid` | uuid | yes | FK self, same group version; unique |
| `content_hash` | text | no | over its entries |
| `authority_ref_text` | text | no | |
| `created_at`, `created_by_name` | | no | |

Number 1 has no predecessor; every later number has exactly one.

### 2.10 `metric_directory.group_version_breakdown` (new, 10 columns)

`group_version_breakdown_id` uuid PK; `breakdown_set_version_uid` FK; `breakdown_ordinal` smallint; `concept_id`, `concept_version_id`; the four step columns of 2.3; `created_at`. Unique `(breakdown_set_version_uid, concept_version_id, step_reference_concept_version_id)` with NULLs not distinct. Each set version holds its whole list; nothing is inherited from the previous set version.

### 2.11 `metric_directory.group_version_gate_event` (new, 9 columns)

Records the gated step (section 4.1). State is read from events, never cached.

| Column | Type | Null | Key or check |
|---|---|---|---|
| `gate_event_uid` | uuid | no | PK |
| `group_version_uid` | uuid | no | FK `group_version_grammar` |
| `event_kind_code` | text | no | `reviewed`, `first_member_proven` |
| `member_version_uid` | uuid | yes | FK `member_version`; set for `first_member_proven` |
| `demoed_result_uid` | uuid | yes | FK `mcf.metric_version_demoed_result`; set for `first_member_proven` |
| `reviewer_name` | text | no | must differ from the group version's `created_by_name` |
| `authority_ref_text` | text | no | |
| `created_at`, `created_by_name` | | no | |

Unique `(group_version_uid, event_kind_code)`. The insert trigger checks that the member version pins this group version, that the Demoed result's verdict is a pass, and that its metric contract version realizes that member version (via 0086-A).

### 2.12 The member layer, extended (no parallel tables)

| Table | Change |
|---|---|
| `member_version_discriminator` (live, 6 columns) | add `group_version_uid uuid` and `axis_ordinal smallint`, both NULL for the 2 live rows; composite FK `(group_version_uid, 'axis', axis_ordinal)` to `group_version_part` (through a stored role column `axis_role_code text` fixed to `axis`, 9 columns). A trigger requires `group_version_uid` to equal the member version's, and `concept_version_id` to equal the axis part's. Value rows come from Unit V (`member_version_discriminator_value`, A§6.4); `governed_values_json` is NULL for new rows. |
| `member_version_age_band` (new, 5 columns, named in A§6.3) | `member_version_uid` PK FK; `group_version_uid`, `band_code`, composite FK to `group_version_age_band`; `created_at`. At most one band per member version. It is a typed temporal choice, not an axis (A§3.4). |
| `member_version_dependency` (live, 3 columns) | add `group_version_uid uuid` (4 columns); composite FK `(group_version_uid, role_code)` to `group_version_derived_input`. A trigger requires the input member version to pin the slot's `input_group_version_uid`. The D7 dependency source becomes this table (DEC-b5c7ff amendment). |
| `member_version_constant` (live, 4 columns, 0 rows) | replace `value_json` with `integer_value bigint`, `decimal_value numeric`, `boolean_value boolean`, `date_value date` (7 columns); exactly one set, matching `value_type`; `text` removed from `value_type`. Role and type must equal a group constant slot. |
| `member_version_direct_input` (live) | not written for a member under a grounded group version; finalize refuses it. The grounded parts have one home, the group version, which the member pins (DEC-1918d0 rule 4). The 2 live rows stay as history. This narrows A§6.3 (section 11, question 2). |

**Finalize.** `fn_member_version_finalize` gains, for a member under a grounded group version: every discriminator names an axis of that version; at most one band; every constant slot is filled; a derived member has one dependency per input slot; and the records design's interpretation row is present, with `temporality_class_code` mapped from the group (`flow` to `flow_per_period`; `stock_as_of` to `stock_at_period_end` or `instantaneous`) and `unit_type_code` from the measure (`entity_count` and `count_distinct` to `count`; `sum` to the measure's unit or `currency`). This activates the records design's check 3.8.2.

**Retired.** `group.template_json` and `group_version.template_json` become NULL-only for new rows. `member.measure_concept_id` and the two PATCH routes of section 1 are retired. `member_version.temporal_intent_json` and `output_intent_json` are written by the command as the canonical projection of the group grammar, and finalize refuses any other value, until a later migration drops them (section 7).

### 2.13 The metric contract side

| Table | Change |
|---|---|
| `mcf.mcv_breakdown_set_pin` (new, 4 columns) | `metric_contract_version_uid` PK FK; `breakdown_set_version_uid` FK; `created_at`, `created_by_name`. Insert-only, in the contract version's transaction. |
| `mcf.metric_computed_dimension_ref` (live, 10 columns) | add `group_version_breakdown_id uuid` NULL, FK (11 columns). A trigger requires the entry to belong to the pinned set version, and its concept version to equal `source_business_concept_version_id`. |

`mcf.metric_contract_version` (19 columns until 0088) gets no new column.

## 3. The per-role reachability checks

Routines in `metric_directory`, `STABLE`, `search_path` pinned. Each returns a set of refusal codes, empty when the row passes. The insert triggers of 2.3 to 2.10 call them and refuse with the first code and the full list.

| Routine | Checks |
|---|---|
| `fn_concept_version_usable(concept_version_id)` | the concept is `active` and not archived; the version is its `active_version_id` at authoring |
| `fn_part_reach(grain_entity_id, concept_version_id, step…)` | no step: the concept's `entity_id` equals the grain. Step: the reference concept is `kind = 'reference'`, its `entity_id` is the grain, its `target_entity_id` is the step target entity; the part concept's `entity_id` is the step target entity. Never two steps. |
| `fn_check_measure_part` | `count_distinct`: a reference concept on the grain. `sum`: `representation_term` in (`amount`, `quantity`, `measure`) and `context_concept_id` set (currency or unit). `entity_count`: no measure part, and the grain has an active concept with `semantic_role = 'identity'`. |
| `fn_check_context_part` | the concept equals the measure version's `context_concept_id` |
| `fn_check_date_part` (period anchor, closing, age anchor, reporting anchor, event dates) | `data_type` in (`date`, `timestamp`); `semantic_role = 'temporal'`; reachable as above. `closing` and `age_anchor` need `stock_as_of`; `period_anchor` needs `flow`; `closing` needs `gross_binary` |
| `fn_check_axis_part` | `representation_term = 'code'`; reachable; a declared value source (Unit V: `enumerated` with at least one value row, or `master`) |
| `fn_check_breakdown` | a code concept as an axis, or a reference concept on the grain; reachable |
| `fn_check_event_input` | the grain reference and every leg key are reference concepts on the event entity whose `target_entity_id` is the grain; the grain key is an identity concept on the grain; event date on the event entity; leg amounts are amounts on the event entity with the same `context_concept_id` as the measure |
| `fn_check_derived_input` | the input group version is grounded; the anchor rule of A§3.3: if all inputs share one period anchor version, `reporting_anchor_kind_code = 'input_anchor'` and a `reporting_anchor` part equals it; otherwise `evaluation_point` is allowed |
| `fn_group_version_grammar_finalize` | deferred, at commit: the grammar row exists for every group version created after the migration; all parts pass; the role set is complete for the class and measure kind; the content hash covers the grammar and every child |
| `fn_realization_grammar_check(member_version_uid, metric_contract_version_uid)` | A§3.5 role by role: grain entity version; measure kind and concept version against the aggregation operator and measure variable; time class and anchor against the temporal gate kind and anchor role; open test (closing role, or the schedule's every part including `anchor_sign`); band bounds and age anchor against the `age_band` gate; axis concept version and values against the governed selection; breakdown set version pinned and every partition in it; derived inputs, offsets and constants. Called from `fn_realization_event_guard` on assert |

A bare FK proves a row exists. These routines prove the row is eligible for its role.

## 4. The commands

All are under `/api/metric-directory`. Every refusal returns HTTP 409 or 422 with `{ code, field, value, allowed }`, so a CLI can act on the code. Writes are one transaction. A retried request with the same `request_key` returns the first result.

### 4.1 Create a group (the gated step)

`POST groups` with the family, group code, class, grain entity version, the grammar, the parts, bands, event input, derived inputs, constant slots and the first breakdown set. It writes the group, its v1, all children and breakdown set version 1.

The group is then **pending**. Siblings are refused until two gate events exist:
1. `reviewed`: one review of the group version by a named reviewer who is not its author (`POST groups/:groupId/versions/:gv/gate-events`).
2. `first_member_proven`: the first member is authored (the existing member and version commands), its metric contract is authored and passes its Demoed proof on the metric lane, and the event names that Demoed result.

| Code | Meaning |
|---|---|
| `GRP_CODE_TAKEN` | the code is held by any group, archived or not (0085-H) |
| `GRP_CODE_PATTERN` | not a slug |
| `GRP_GRAIN_INACTIVE` | the entity or its version is not active |
| `GRP_CLASS_PARTS` | a part, parameter or child not allowed for the class or measure kind, or a required one missing |
| `GRP_CONCEPT_UNUSABLE` | a concept archived, inactive, or not at its active version |
| `GRP_REACH_NOT_ON_GRAIN` | the concept is not on the grain and no step is given |
| `GRP_REACH_BAD_STEP` | the step's reference, target entity or target concept do not line up |
| `GRP_ROLE_INELIGIBLE` | wrong kind, type, representation or semantic role for the role |
| `GRP_SUM_NO_CONTEXT` | a `sum` measure without a currency or unit context |
| `GRP_COUNT_NO_IDENTITY` | `entity_count` on a grain with no identity concept |
| `GRP_AXIS_NO_VALUE_SOURCE` | an axis concept with no value source |
| `GRP_BANDS_INVALID` | overlap, bad bounds, or no age anchor |
| `GRP_EVENT_INVALID` | event entity, contract, keys, dates, legs or a sign invalid; repeated leg pair |
| `GRP_DERIVED_INPUT_INVALID` | an input not grounded, a wrong slot set, or an offset out of range |
| `GRP_ANCHOR_RULE` | the declared reporting anchor breaks A§3.3 |
| `GRP_GATE_REVIEWER_IS_AUTHOR` | review by the author |
| `GRP_GATE_PROOF_INVALID` | the member, the Demoed verdict or the realization does not match |

### 4.2 Add a sibling member (a mechanical metric act)

`POST groups/:groupId/members` with the member code, the axis values, an optional band, constants, the name, the plain definition, and the direction with its rationale (records design 0085-B). The unit and temporality class come from the group. It writes the member, its version, the interpretation row, discriminators with their value rows, the band and constants.

| Code | Meaning |
|---|---|
| `GRP_PENDING` | the group version has not passed its gate |
| `GRP_ARCHIVED` | the group is archived |
| `MEM_CODE_TAKEN`, `MEM_CODE_PATTERN` | member code taken or not a slug |
| `MEM_AXIS_UNKNOWN` | the axis ordinal is not on the group version |
| `MEM_VALUE_NOT_GOVERNED` | a value not in the axis's value rows or master, or a master row inactive |
| `MEM_SELECTION_DUPLICATE` | a sibling already has the same axis values and band |
| `MEM_BAND_UNKNOWN` | the band is not on the group version |
| `MEM_CONSTANT_INVALID` | a slot unfilled, or a value of the wrong type |
| `MEM_DEPENDENCY_INVALID` | a derived member's input is not a member of the slot's input group version |
| `MEM_DIRECTION_INVALID`, `MEM_DEFINITION_MISSING` | direction not in the master, or no rationale; empty definition |

### 4.3 Version a breakdown set

`POST groups/:groupId/versions/:gv/breakdown-sets` with the whole list. It writes set version n+1, superseding n. No member version changes. A metric contract that wants the new breakdown needs a new metric contract version pinning set n+1.

Codes: `BRK_NOT_CURRENT` (the supersedes target is not the latest set), `BRK_UNCHANGED` (same content hash), `BRK_ROLE_INELIGIBLE`, `BRK_REACH_NOT_ON_GRAIN`, `BRK_REACH_BAD_STEP`, `BRK_IS_CURRENCY` (currency and unit are not breakdowns, A§3.6), `GRP_ARCHIVED`.

### 4.4 Archive

`PATCH groups/:groupId/archive` with a reason. It sets `archived_at`; the code stays reserved (0085-H, 0085-I). Re-pointing a grain is a new group plus this archive (A§5 item 4).

Codes: `GRP_HAS_LIVE_MEMBERS` (archive the members first), `GRP_IS_INPUT` (a live derived group version names it as an input), `GRP_ALREADY_ARCHIVED`.

## 5. Base and derived grammar, worked through

All on Customer Invoice unless stated. "CI" is Customer Invoice.

| Metric | Group grammar | Parts | Member |
|---|---|---|---|
| Invoice count | base, `entity_count`, `flow` | `period_anchor` invoice date | no axis, no band |
| Invoiced amount | base, `sum`, `flow` | `measure` invoice amount; `context` its currency code; `period_anchor` invoice date | no axis. The metric contract partitions by currency, or a sibling member pins one currency by an axis on the currency code (master value source) |
| Open AR at P | base, `sum`, `stock_as_of`, `residual` | `measure` invoice amount; `context` currency; `age_anchor` due date; event input: Receivable Application, its canonical contract version, grain key the CI identity, event date the application date, anchor date the invoice date, `anchor_sign` +1; legs: debit leg key with amount −1, credit leg key with amount +1 | the total member: no band |
| Aging buckets | the same group as open AR | bands `d0_30`, `d31_60`, `d61_90`, `d91_plus` | one sibling per band, e.g. `d31_60` |
| DSO | derived, `ratio`, reporting anchor `evaluation_point`; output grain Legal Entity | slots `numerator` = the open AR group version, `denominator` = an invoiced revenue group version (`flow`, 365 days ending P); constant slot `days_in_period`, integer | dependencies on the open AR total member and the invoiced amount member; constant 365. Both input metric contracts partition by `issuing_legal_entity` and by currency |
| Period-over-period change | derived, `delta`, reporting anchor `input_anchor` = invoice date | slots `operand_current` (offset 0) and `operand_prior` (offset −1), both on the invoice count group version | both dependencies on the invoice count member |
| Distinct customers invoiced | base, `count_distinct`, `flow` | `measure` the CI `customer` reference; `period_anchor` invoice date | no axis |
| Invoices for customers in segment X | base, `entity_count`, `flow` | `period_anchor` invoice date; `axis` 1 = Customer segment code, step: CI `customer` reference version, Customer entity version, the segment concept version | selects X |

Three facts from the live reads bear on these. The Receivable Application amounts have no currency context, so open AR waits on a concept act (`GRP_EVENT_INVALID` today). The Customer dimension codes have no value set, so segment X waits on Unit V or a concept act (`GRP_AXIS_NO_VALUE_SOURCE` today). The invoice amounts on CI carry a context, so invoiced amount fits now.

## 6. The proof cases

Design requirements against wrong values (auditor point 5), not a live metric act. Each is one test on an owner- and grant-faithful restore.

| Case | Input | Expected | What enforces it |
|---|---|---|---|
| Partial payment | invoice 1,000; payment 400 dated before P | open AR 600; a `gross_binary` group gives 1,000 only where declared | the event input and legs; `fn_realization_grammar_check` equates the schedule |
| Reversal | payment 400 and its reversal, both before P | 1,000. A contract whose leg sign or anchor sign differs is refused at realization | `anchor_sign`, `leg_sign`, the realization check, the schedule hash (DEC-45200d) |
| One-step fan-out | a CI customer key matching two Customer records at P | the evaluation is refused, never doubled | the step is a lookup to at most one record (A§3.7); the evaluator's refusal, with a test |
| No matching reference | a CI with no Customer record | counts in the total; matches no segment; falls in `unmatched`; matched and unmatched counts emitted | A§3.7; evidence (Invariant VI) |
| Mixed-currency sum | INR and USD invoices, no partition or pin | refused; with a currency partition, two values | `GRP_SUM_NO_CONTEXT` at authoring; the A§3.8 evaluation refusal |
| Derived period offset | `delta`, offsets 0 and −1 on one input | value at P minus value one period earlier; refused if the input metric contract declares no period | `group_version_derived_input`; the realization check reads the input contract's calendar context |

## 7. The sweep plan for the 143 groups

Classified from live reads on 2026-11-26. Rules, in order: a test fixture or probe is a test leftover; a grain that is wrong in meaning is mis-pointed; a grain on the owner's list of 15 is a non-countable split (A§8.1); a base group with no anchor, or a derived group with no declared anchor, needs a date; the rest fit.

| Class | Base | Derived | Total | Of which, no version | Disposition |
|---|---|---|---|---|---|
| Fits | 61 | 2 | 63 | 14 | grounded v2 (or v1) through `POST groups` successor; 11 carry `closing_concept_id` in JSON, which becomes a `closing` part |
| Needs a date | 14 | 47 | 61 | 13 | base: declare the period anchor, or `stock_as_of` with closing or event input; derived: declare the reporting anchor (A§3.3) |
| Mis-pointed | 2 | 0 | 2 | 2 | Recognition Event is employee recognition. Archive both; the family already has Revenue Recognition Line counts and amounts (question 3) |
| Non-countable split | 4 | 11 | 15 | 0 | A§8.1: 6 wait for identity concepts (Tax Return, Financial Close, GL Account Reconciliation); 8 Legal Entity groups stay derived; `cost_center_master` becomes a breakdown on the Journal Entry Line `cost_center` reference and is archived |
| Test leftover | 2 | 0 | 2 | 0 | archive `zz_trackA_cefa537` and `je_line_grain_probe`; codes stay reserved |
| **Total** | **83** | **60** | **143** | **29** | |

**Concept acts before the sweep.** Of the 63 that fit, 26 are `sum` groups whose grain has no amount concept with a currency or unit context. They sit on 13 entities (Journal Entry Line 7, Asset 4, GL Account 3, Tax Line 2, Bank Account 2, and one each on Debt Instrument, Hedge Instrument, Contract, Maintenance Order, Performance Obligation, Product, Revenue Recognition Line and Budget). They would be refused with `GRP_SUM_NO_CONTEXT`. Each needs a concept act on the business concept path first. 30 groups have no `op` in their template, so their measure kind is declared fresh.

**Order.** (1) Concept acts: identity concepts on 3 entities, contexts on 13, value sources through Unit V. (2) Archive the 4 leftovers and mis-pointed groups and `cost_center_master`. (3) Ground the groups family by family, Finance first. Every change goes through the commands of section 4, never a row edit. Groups whose members differ only by measure are split at this step. The one live member is re-placed by a new member version under the grounded `ci_invoice_volume` v2.

## 8. The unit order and the migrations

| # | Unit | Migrations |
|---|---|---|
| 1 | The decision unit: the grounding ADR together with DEC-45200d, FND-ERR-010 or the next free, and the Foundation text edits (owner's landing go) | none |
| 2 | This design | none |
| 3 | Unit V, typed allowed values, with its measured ripple of 39 bc-core files that read `canonical_value_set` and 2 that read `governed_values_json` | **M-V**: value rows, value source, the masters' freeze triggers, `member_version_discriminator_value` |
| 4 | The schema | **M-G1**: the group tables and routines. **M-G2**: the member and contract extensions, finalize, the realization check. **M-G3**, after readers move: drop the retired columns |
| 5 | The sweep (section 7) | none: commands only |

**Numbers.** bc-db origin/main ends at 0084. Open PR 200 holds 0085 to 0087. The records design plans 0088 and tenant 0008. Open PRs 177 and 111 hold 0073 and 0039. So each migration takes the next free number at authoring, 0089 or later today, after checking open bc-db PRs.

## 9. The database proposal (for the owner's database yes)

| # | Object | Change | Rollback |
|---|---|---|---|
| V-1 | `concept_registry.business_concept_value` (new) | concept version FK, value code, label; insert-only | drop, before any member selects a value |
| V-2 | `concept_registry.value_master` (new) | names a master table and key column; 2 rows: `master.dim_currency.currency_code`, `master.dim_country.alpha2` | drop with V-3 |
| V-3 | `business_concept_version` (12 columns) | add `value_source_code` (`enumerated`, `master`) and `value_master_id` FK (14); set the 29 currency and 4 country code concepts to `master` through new concept versions, never in place | drop columns before V-4 has rows |
| V-4 | `metric_directory.member_version_discriminator_value` (new) | exactly one of `concept_value_id`, `currency_code` (FK `dim_currency`), `country_alpha2` (FK `dim_country`); trigger matches the value source | drop before any new member |
| V-5 | `master.dim_currency`, `master.dim_country` | freeze triggers: refuse an UPDATE of `currency_code`, `decimal_places`; of `alpha2`, `alpha3`, `numeric_code`; refuse DELETE and TRUNCATE | drop triggers |
| G1-1 | `group_version` | unique `(group_version_uid, class_code)` and `(group_version_uid, grain_entity_id)` | drop indexes |
| G1-2 | 2.2 to 2.11 (10 tables) | create, with FKs, checks, immutability, TRUNCATE refusal, finalize guards, grants | drop all, valid only before any grounded group version exists |
| G1-3 | section 3 routines | create, with the insert triggers that call them | drop |
| G1-4 | `fn_group_version_grammar_finalize` | deferred constraint trigger on `group_version` for rows created after the migration | drop trigger |
| G1-5 | `group`, `group_version` | `template_json` becomes nullable on `group`; a new row with non-NULL `template_json` is refused | restore NOT NULL only if no NULL row exists |
| G2-1 | `member_version_discriminator`, `_dependency`, `_constant` | columns of 2.12; `value_json` dropped (0 rows) | re-add `value_json`, drop new columns, before any new row |
| G2-2 | `member_version_age_band` (new) | 2.12 | drop before any row |
| G2-3 | `fn_member_version_finalize` | the 2.12 rules | restore as after 0085 |
| G2-4 | `mcf.mcv_breakdown_set_pin` (new); `mcf.metric_computed_dimension_ref` | 2.13 | drop, before any pin |
| G2-5 | `metric_directory.fn_realization_event_guard` | call `fn_realization_grammar_check` on assert for a grounded member version | restore as after 0086 |
| G3-1 | later | drop `group.template_json`, `group_version.template_json` (old values kept in an evidence file with a sha256 per value, as 0088-B), `member.measure_concept_id`, `member_version.temporal_intent_json`, `output_intent_json` | re-add and restore from the evidence file |
| Backfill | none | no migration writes directory data; the sweep uses the commands | |

Each migration is proven on an owner- and grant-faithful restore of a fresh read-only dump, with `bc_platform_runtime` vectors and the six proof cases, never on live. Each live apply needs its own recorded grant.

## 10. Foundation gate (DEC-79b62f)

1. **Why this location?** B for the grammar, which was a missing declaration. E for the typed tables that hold it. The routines guard E against the B rule.
2. **Why not an upper layer?** A does not declare a metric's shape. The concept gaps found here (3 identity concepts, 13 contexts, value sources) are fixed in the registry by concept acts, not compensated in groups.
3. **Why not a lower layer?** A lint or an evaluation-time check (D, F) would be a net. The live member layer, `governed-selection.ts`, the resolver and the DEC-45200d schedule declaration are extended, not bypassed. Reads never trigger evaluation.
4. **Design or execution act?** A design act, named in the amendment, its ADR, FND-ERR-010 and TSK-09855b.

Invariants: III (every new table is insert-only; masters frozen); IV (every reference is a pinned version; no current set is read); I (members select, never classify, sign or age); VI (matched and unmatched counts emitted).

## 11. Open questions for the owner

1. **The gate review.** Who gives the one review that opens a new group: the owner, or a named reviewer controller? Codex is excluded from metric acts (grant ead781aa).
2. **One home for grounded parts.** The draft's sketch (A§6.3) puts them on `member_version_direct_input`. This design keeps them only on the group version, which each member pins, so they cannot drift. Agree?
3. **The two Recognition Event groups.** Archive them with no replacement, since the family already holds Revenue Recognition Line counts and amounts?
