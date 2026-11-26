---
uid: structured-group-design
title: The structured metric group, concept-grounded (design)
description: "Design for TSK-09855b, revision 2. It implements the draft Foundation amendment on concept grounding (bc-docs PR 276, revision 5) and replaces the free-form group template with typed tables: group version parts by role, the event input, age bands, the breakdown set and its versions, and the derived-group inputs. It extends the typed member layer, defines the per-role reachability checks as database routines, the five directory commands with their refusal codes, the proof cases, the sweep plan for all 143 groups from live reads, and the database proposal for the owner's yes. Revision 2 applies the owner's rulings of 2026-11-26 (barecount-devhub 060d5328) and the red team of revision 1. Nothing is built."
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

*Design note, revision 2, 2026-11-26. Nothing in it is built, recorded or written. Counts were read live from `bc_platform_dev` on 2026-11-26 (read-only). Re-read them before acting.*

**Revision 2.** Applies the owner's rulings recorded in barecount-devhub `artifacts/operator-review/DECISIONS-workflow-review.md`, branch `claude/operator-review-content`, commit `060d5328`, entry "Successor rule corrected, and the group design's three questions":

- (1) A new definition version gets a new metric contract plus a `mcf.metric_supersession` record; the directory member carries the metric's lasting identity (sections 2.13, 4.2, 4.4, 7).
- (2) The review that opens a group is the owner's, recorded as a desk grant; one grant may open a named batch of groups (sections 2.11, 4.1).
- (3) Grounded parts, including a derived definition's inputs and period offsets, live only on the group version (sections 2.7, 2.12; the duplicate member columns are listed for retirement).
- (4) The two Recognition Event groups are archived with no replacement; the Customer Invoice Line Item recognition overlap is a sweep item (section 7).

It also applies the red team of revision 1: a group-version successor command (4.2), derived groups classed by output grain (7), a `linear_combination` derivation (2.2, 2.7), the three groups whose class differs from v1's (7), the identity marker (3), active currency concepts only (9), the four ADR-952faa time classes and a unit by FK (2.2), an optional open model (2.2), the segment concept (5), a date-only check (3), and the dim_country note (9). Section 11's three questions are answered and removed.

**Revision 2, later rulings** (same file and branch): `1ef2d04e`, a governed top-N share derivation (2.2, 2.7, 7); `53e9659c` (1), derived group versions pin exact input definition versions and move only on purpose, with a read-only check (2.7, 3); `53e9659c` (2), the country's currency stays out of this design (9). No question is open.

## 0. Authority and inputs

| Input | Exact reference |
|---|---|
| The authority | The draft amendment, bc-docs PR 276, head `e4c98821`, `docs/governance/proposals/foundation-amendment-concept-grounded-metrics.md` (revision 5, amended to the same rulings). Section numbers below written "A§n" point into it. |
| The owner's rulings | barecount-devhub `claude/operator-review-content` `060d5328` (above), and the earlier entries the amendment cites. |
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
| Anchors | 69 groups; all 69 are active concepts on the grain with `data_type = 'date'`; every group version agrees with its group |
| Class | 3 group versions (all v1) carry a class different from their group's: section 7 |
| Member layer | `member_version` 2 rows; `_discriminator` 2; `_direct_input` 2; `_dependency` 0; `_constant` 0 |
| Member columns that repeat group parts | `member.measure_concept_id`, `member.discriminator_json` (NOT NULL), `member.derivation_json`; `member_version.grain_entity_id` and `grain_entity_version_id` (both NOT NULL) |
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

### 2.2 `metric_directory.group_version_grammar` (new, 1:1, 14 columns)

The typed parameters of a group version (A§3.2, A§3.3).

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | PK; FK `(group_version_uid, class_code)` and FK `(group_version_uid, grain_entity_id)` to two new unique indexes on `group_version` |
| `class_code` | text | no | `base` or `derived` |
| `grain_entity_id` | uuid | no | composite FK with the next column; for `derived`, the output grain |
| `grain_entity_version_id` | uuid | no | `entity_version` |
| `measure_kind_code` | text | yes | `entity_count`, `count_distinct`, `sum` |
| `time_class_code` | text | no | the four ADR-952faa D-1 values: `instantaneous`, `flow_per_period`, `stock_at_period_end`, `cumulative_to_date`; a CHECK, the same as `member_version_interpretation.temporality_class_code` in 0085 |
| `open_model_code` | text | yes | `gross_binary`, `residual` |
| `derivation_code` | text | yes | `ratio`, `percentage_of_total`, `delta`, `linear_combination`, `top_n_share` |
| `top_n_count` | integer | yes | 1 to 1000; set exactly when `derivation_code = 'top_n_share'` |
| `reporting_anchor_kind_code` | text | yes | `input_anchor`, `evaluation_point` |
| `unit_type_code` | text | no | FK `master.master_unit_type`, as 0085's interpretation row |
| `canonicalization_version` | text | no | `bc-directory-group-canonicalization-v2` |
| `created_at`, `created_by_name` | | no | |

Checks. `base`: measure kind set; derivation and reporting anchor kind NULL. `derived`: derivation and reporting anchor kind set; measure kind and open model NULL. Both classes declare a time class and a unit. `open_model_code` may be set only when the class is `base` and `time_class_code = 'stock_at_period_end'`; it is NULL for a stock that is not an open item (a snapshot read as of P). A `closing` part requires `gross_binary`; an event input requires `residual`; with `open_model_code` NULL neither is allowed. The unit: `entity_count` and `count_distinct` need `count`; a `sum` of an amount whose context is a currency code needs `currency`.

**Linear combination.** `linear_combination` is the sum of its operands, each with a declared sign (2.7): `profitability_subtotals`, `free_cash_flow_metrics` and `working_capital_metrics` read, by name, as this. An input may itself be a derived group version, so a margin is a `ratio` whose numerator is a `linear_combination`. All operands share one unit and one currency partition (A§3.8).

**Top-N share** (owner, `1ef2d04e`). `top_n_share` is the share of the N largest partitions of one input in that input's total: the sum of the N largest values of the input partitioned by its `rank_by` concept, divided by the input's total, at P. N is the typed `top_n_count`. Its parts:

- **One input**, role `ranked_input` (2.7): a base `sum` or `entity_count` definition version, `flow_per_period` or `stock_at_period_end`, offset 0.
- **The ranking concept**, part role `rank_by` (2.3): a reference concept on the input group version's grain, with no step (for example the Customer Invoice `customer` reference), present in the input group version's breakdown set. The input's metric contract must partition by it (A§3.5).
- **Ties and gaps.** Partitions are ranked by value, largest first; equal values are ordered by the ranking key, ascending, so the N are always the same. The `unmatched` partition (A§3.7) is in the total and never ranked. Fewer than N partitions is not a refusal: all of them are taken, and the partition count is emitted as evidence (Invariant VI).
- **Unit and currency.** The output unit is `percentage` or `ratio`. A monetary input must be one currency partition or pin (A§3.8).

The ranking is declared here and done once by the evaluation of the metric contract; a member never ranks records. `ar_customer_concentration_derived` and `ap_supplier_concentration_derived` are expressed this way.

### 2.3 `metric_directory.group_version_part` (new, 11 columns)

The semantic references, one row per role (A§3.1). Single-valued roles have ordinal 1.

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | FK `group_version_grammar` |
| `role_code` | text | no | `measure`, `context`, `period_anchor`, `closing`, `age_anchor`, `axis`, `reporting_anchor`, `rank_by` |
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

PK `(group_version_uid, band_code)`. A deferred trigger refuses overlapping bands and refuses bands unless the grammar is `stock_at_period_end` and an `age_anchor` part exists.

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

### 2.7 `metric_directory.group_version_derived_input` (new, 8 columns)

The inputs of a derived group version (A§3.3). Owner ruling (3) of `060d5328`: a derived definition's inputs and period offsets live only here, on the group version that each definition pins.

| Column | Type | Null | Key or check |
|---|---|---|---|
| `group_version_uid` | uuid | no | FK `group_version_grammar`, class `derived` |
| `input_role_code` | text | no | `numerator`, `denominator`, `ranked_input`, or `operand_` plus a slug |
| `input_member_version_uid` | uuid | no | composite FK with the next column to a new unique index `member_version (member_version_uid, group_version_uid)` |
| `input_group_version_uid` | uuid | no | the input member version's group version; must be grounded |
| `period_offset_count` | integer | no | default 0; −60 to 0 |
| `operand_sign` | smallint | yes | −1 or +1, no default; set exactly when the derivation is `linear_combination` |
| `created_at`, `created_by_name` | | no | |

PK `(group_version_uid, input_role_code)`. `ratio` and `percentage_of_total` need exactly `numerator` and `denominator`; `delta` needs two operands; `linear_combination` needs two or more operands; `top_n_share` needs exactly one `ranked_input`.

**Input pins** (owner, `53e9659c` (1)). The row pins an exact input definition version. A new version of that input moves nothing: the derived group version stays on the old input until it is moved on purpose, by a successor version (4.2) that pins the new one. The read-only check `fn_derived_input_superseded_pin` (section 3) lists the derived group versions pinned to a replaced input. Moving them is one batch under the owner's group grant (4.1). The D7 dependency source (DEC-b5c7ff) becomes this table, read through the member version's pinned group version.

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
| `event_kind_code` | text | no | `owner_opened`, `first_member_proven` |
| `operator_grant_id` | text | yes | the desk grant's `grant_id`; set exactly for `owner_opened` |
| `operator_grant_text_sha256` | text | yes | the grant's `text_sha256`, CHECK `^[0-9a-f]{64}$`; set exactly with the id |
| `member_version_uid` | uuid | yes | FK `member_version`; set exactly for `first_member_proven` |
| `demoed_result_uid` | uuid | yes | FK `mcf.metric_version_demoed_result`; set exactly for `first_member_proven` |
| `created_at`, `created_by_name` | | no | |

Unique `(group_version_uid, event_kind_code)`. The grant id is not unique: owner ruling (2) of `060d5328` lets one grant open a named batch of groups, so one grant may appear on many rows. The insert trigger checks that the member version pins this group version, that the Demoed result's verdict is a pass, and that its metric contract version realizes that member version (via 0086-A).

**Why a typed pair and not an existing home.** The grant lives on the desk (bc-exchange), not in `bc_platform_dev`; the platform records the citation. `mcf.certification_record` does not fit: its `primitive_type` CHECK allows only `metric_contract_version` and its `action_code` CHECK only metric and audit acts. The pair follows the live precedent `infrastructure.fixture_reset_event (operator_grant_id, operator_grant_text_sha256)`, with the same hex CHECK. The free-text reviewer name of revision 1 is removed.

### 2.12 The member layer, extended (no parallel tables)

| Table | Change |
|---|---|
| `member_version_discriminator` (live, 6 columns) | add `group_version_uid uuid` and `axis_ordinal smallint`, both NULL for the 2 live rows; composite FK `(group_version_uid, 'axis', axis_ordinal)` to `group_version_part` (through a stored role column `axis_role_code text` fixed to `axis`, 9 columns). A trigger requires `group_version_uid` to equal the member version's, and `concept_version_id` to equal the axis part's. Value rows come from Unit V (`member_version_discriminator_value`, A§6.4). `governed_values_json` is NOT NULL today; G2-1 drops the NOT NULL, and a CHECK requires it NULL on every row with `group_version_uid` set. |
| `member_version_age_band` (new, 5 columns, named in A§6.3) | `member_version_uid` PK FK; `group_version_uid`, `band_code`, composite FK to `group_version_age_band`; `created_at`. At most one band per member version. It is a typed temporal choice, not an axis (A§3.4). |
| `member_version_dependency` (live, 3 columns, 0 rows) | not written for a member under a grounded group version; finalize refuses it. A derived definition's inputs and offsets are on the group version (2.7), owner ruling (3). No column is added. |
| `member_version_constant` (live, 4 columns, 0 rows) | replace `value_json` with `integer_value bigint`, `decimal_value numeric`, `boolean_value boolean`, `date_value date` (7 columns); exactly one set, matching `value_type`; `text` removed from `value_type`. Role and type must equal a group constant slot. A constant's value is the member's selection, as an axis value is. |
| `member_version_direct_input` (live) | not written for a member under a grounded group version; finalize refuses it. The grounded parts have one home, the group version, which the member pins (DEC-1918d0 rule 4; owner ruling (3)). The 2 live rows stay as history. |

**Finalize.** `fn_member_version_finalize` gains, for a member under a grounded group version: every discriminator names an axis of that version; at most one band; every constant slot is filled; no dependency or direct input row; and the records design's interpretation row is present, with `temporality_class_code` equal to the grammar's `time_class_code` and `unit_type_code` equal to the grammar's. This activates the records design's check 3.8.2.

**Retired: the member columns that repeat group parts** (owner ruling (3)). Each is a second home for a grounded part.

| Column | Today | Until M-G3 | M-G3 |
|---|---|---|---|
| `member.measure_concept_id` | nullable, FK `business_concept` (not a version) | NULL for every new member | drop |
| `member.discriminator_json` | NOT NULL | G2 drops the NOT NULL; NULL for every new member | drop |
| `member.derivation_json` | nullable | NULL for every new member | drop |
| `member_version.grain_entity_id`, `grain_entity_version_id` | NOT NULL, composite FK `entity_version` | written by the command equal to the grammar's grain; finalize refuses any other value | drop |
| `member_version.temporal_intent_json`, `output_intent_json` | NOT NULL | written as the canonical projection of the grammar; finalize refuses any other value | drop |
| `member_version_dependency`, `member_version_direct_input` | live tables | not written under a grounded group version | drop once D7 and the gate read the group version |

Also retired: `group.template_json` and `group_version.template_json` become NULL-only for new rows, and the two PATCH routes of section 1 are retired. The readers of every column above move before M-G3.

### 2.13 The metric contract side

| Table | Change |
|---|---|
| `mcf.mcv_breakdown_set_pin` (new, 4 columns) | `metric_contract_version_uid` PK FK; `breakdown_set_version_uid` FK; `created_at`, `created_by_name`. Insert-only, in the contract version's transaction. |
| `mcf.metric_computed_dimension_ref` (live, 10 columns) | add `group_version_breakdown_id uuid` NULL, FK (11 columns). A trigger requires the entry to belong to the pinned set version, and its concept version to equal `source_business_concept_version_id`. |

`mcf.metric_contract_version` (19 columns until 0088) gets no new column.

**Successors on the metric contract side** (owner ruling (1) of `060d5328`, replacing the same-metric-contract part of ruling 6e4a8803). A new definition version is realized by a **new metric contract**, joined to its predecessor by a `mcf.metric_supersession` record. The directory member carries the metric's lasting identity. Reason, read live: `mcs_different_mc_chk` refuses a supersession whose predecessor and successor metric contract are the same, and a metric contract's identity is frozen once past draft. The same holds for a new breakdown pin on a metric contract past draft (4.4).

## 3. The per-role reachability checks

Routines in `metric_directory`, `STABLE`, `search_path` pinned. Each returns a set of refusal codes, empty when the row passes. The insert triggers of 2.3 to 2.10 call them and refuse with the first code and the full list.

| Routine | Checks |
|---|---|
| `fn_concept_version_usable(concept_version_id)` | the concept is `active` and not archived; the version is its `active_version_id` at authoring |
| `fn_part_reach(grain_entity_id, concept_version_id, step…)` | no step: the concept's `entity_id` equals the grain. Step: the reference concept is `kind = 'reference'`, its `entity_id` is the grain, its `target_entity_id` is the step target entity; the part concept's `entity_id` is the step target entity. Never two steps. |
| `fn_check_measure_part` | `count_distinct`: a reference concept on the grain. `sum`: `representation_term` in (`amount`, `quantity`, `measure`) and `context_concept_id` set (currency or unit). `entity_count`: no measure part, and the grain has an active concept with `identity_role = 'identity_bearing'`. |
| `fn_check_context_part` | the concept equals the measure version's `context_concept_id` |
| `fn_check_date_part` (period anchor, closing, age anchor, reporting anchor, event dates) | `data_type = 'date'` (A§3.9; all 69 live anchors are `date`); `semantic_role = 'temporal'`; reachable as above. `period_anchor` is required for `flow_per_period` and `cumulative_to_date`, and for `stock_at_period_end` with `gross_binary` it is the date the record is open from; `closing` and `age_anchor` need `stock_at_period_end`; `closing` needs `gross_binary` |
| `fn_check_axis_part` | `representation_term = 'code'`; reachable; a declared value source (Unit V: `enumerated` with at least one value row, or `master`) |
| `fn_check_breakdown` | a code concept as an axis, or a reference concept on the grain; reachable |
| `fn_check_event_input` | the grain reference and every leg key are reference concepts on the event entity whose `target_entity_id` is the grain; the grain key is an `identity_bearing` concept on the grain; event date on the event entity; leg amounts are amounts on the event entity with the same `context_concept_id` as the measure |
| `fn_check_derived_input` | the input member version pins the input group version, which is grounded; the input's unit and currency partition agree with the other inputs (A§3.8); the anchor rule of A§3.3: if all inputs share one period anchor version, `reporting_anchor_kind_code = 'input_anchor'` and a `reporting_anchor` part equals it; otherwise `evaluation_point` is allowed |
| `fn_check_rank_part` | `top_n_share` only: the concept is `kind = 'reference'`, its `entity_id` is the `ranked_input`'s grain (not the output grain), no step; it is an entry of a breakdown set version of the input group version |
| `fn_derived_input_superseded_pin()` | read-only diagnostic, not a gate: returns each derived group version of a group that is not archived, with a `group_version_derived_input` row whose `input_member_version_uid` has a successor (`member_version.supersedes_version_uid` names it), and that successor. It reads rows only; it never evaluates and never moves a pin |
| `fn_group_version_grammar_finalize` | deferred, at commit: the grammar row exists for every group version created after the migration; all parts pass; the role set is complete for the class and measure kind; the content hash covers the grammar and every child |
| `fn_realization_grammar_check(member_version_uid, metric_contract_version_uid)` | A§3.5 role by role: grain entity version; measure kind and concept version against the aggregation operator and measure variable; time class and anchor against the temporal gate kind and anchor role; open test (closing role, or the schedule's every part including `anchor_sign`); band bounds and age anchor against the `age_band` gate; axis concept version and values against the governed selection; breakdown set version pinned and every partition in it; derived inputs, offsets and constants. Called from `fn_realization_event_guard` on assert |

A bare FK proves a row exists. These routines prove the row is eligible for its role.

**The identity marker.** Two live columns mark identity, and they disagree on 39 active concepts: 31 are `identity_bearing` without `semantic_role = 'identity'` (24 references, 7 values), and 8 values carry `semantic_role = 'identity'` while `descriptive`. This design reads `business_concept.identity_role = 'identity_bearing'`, because the engine does: the canonical resolver takes a grain's identity from it (bc-core `src/boundary/ccv2-canonical-resolver.service.ts`), and the BCF validator refuses `semantic_role = 'identity'` on a `descriptive` concept (`src/registry/bcf/panel/recommendation.validator.ts`), so the 8 are inconsistent rows for the concept hygiene work, not a second rule. Grains used by groups with no `identity_bearing` concept: Tax Return, Financial Close, GL Account Reconciliation, Performance Obligation, Debt Instrument and Hedge Instrument (6), and Cost Center, which becomes a slice (section 7).

## 4. The commands

All are under `/api/metric-directory`. Every refusal returns HTTP 409 or 422 with `{ code, field, value, allowed }`, so a CLI can act on the code. Writes are one transaction. A retried request with the same `request_key` returns the first result.

### 4.1 Create a group (the gated step)

`POST groups` with the family, group code, class, grain entity version, the grammar, the parts, bands, event input, derived inputs, constant slots and the first breakdown set. It writes the group, its v1, all children and breakdown set version 1.

The group version is then **pending**. Siblings are refused until two gate events exist:
1. `owner_opened`: the owner's review, recorded as a desk grant (owner ruling (2) of `060d5328`). `POST groups/:groupId/versions/:gv/gate-events` carries the grant id, its text sha256 and the group codes the grant names; the command refuses a group version whose group code is not among them. One grant may open a named batch of groups in the sweep. Codex has no role here (grant ead781aa).
2. `first_member_proven`: the first member is authored (the existing member and version commands), its metric contract is authored and passes its Demoed proof on the metric lane, and the event names that Demoed result.

Every grounded group version passes its own gate, a successor version (4.2) included; a batch grant may name successor versions too.

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
| `GRP_DERIVATION_NOT_EXPRESSIBLE` | the derived group's arithmetic is none of the five derivations (2.2) |
| `GRP_TOPN_COUNT_INVALID` | `top_n_count` missing or outside 1 to 1000 for `top_n_share`, or set for another derivation |
| `GRP_TOPN_INPUT_INVALID` | not exactly one `ranked_input`; the input is not a base `sum` or `entity_count`, not `flow_per_period` or `stock_at_period_end`, has an offset, or has more than one currency |
| `GRP_TOPN_RANK_INELIGIBLE` | the `rank_by` concept is not a reference on the input's grain, has a step, or is not in the input group version's breakdown set |
| `GRP_GATE_GRANT_INVALID` | no grant id, a malformed text sha256, or the grant does not name this group |
| `GRP_GATE_PROOF_INVALID` | the member, the Demoed verdict or the realization does not match |

### 4.2 Version a group (successor)

`POST groups/:groupId/versions` with `supersedes_version_uid` and the whole grammar, parts, bands, event input, derived inputs, constant slots and first breakdown set, as in 4.1. It writes group version n+1 in the same group, superseding n. The live `fk_group_version_supersedes_same_anchor` (`(group_id, supersedes_version_uid)`) already keeps the predecessor in the same group, and `uq_group_version_supersedes` already refuses a fork. The new version is pending until its own gate (4.1). Existing member versions keep pinning n; a member moves by a new member version that pins n+1, and that new definition version is realized by a new metric contract with a `mcf.metric_supersession` record (2.13).

The sweep needs it: every grounded v2 in section 7 is a successor of an ungrounded v1, and the live member under `ci_invoice_volume` is re-placed under its v2.

| Code | Meaning |
|---|---|
| `GV_NOT_CURRENT` | the supersedes target is not the group's latest version |
| `GV_OTHER_GROUP` | the supersedes target belongs to another group |
| `GV_UNCHANGED` | the content hash equals the predecessor's |
| `GV_CLASS_CHANGED` | the class differs from the group's `class_code` |
| `GV_GRAIN_CHANGED` | the grain entity differs from the group's: re-pointing is a new group plus an archive (4.5) |
| `GRP_ARCHIVED` | the group is archived |
| all the part codes of 4.1 | `GRP_CLASS_PARTS` to `GRP_DERIVATION_NOT_EXPRESSIBLE` |

### 4.3 Add a sibling member (a mechanical metric act)

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
| `MEM_INPUT_GIVEN` | the request names inputs or offsets: they are the group version's (2.7) |
| `MEM_DIRECTION_INVALID`, `MEM_DEFINITION_MISSING` | direction not in the master, or no rationale; empty definition |

### 4.4 Version a breakdown set

`POST groups/:groupId/versions/:gv/breakdown-sets` with the whole list. It writes set version n+1, superseding n. No member version changes. A metric contract version's pin is written with it and never changes. A metric that wants the new breakdown gets a new metric contract pinning set n+1, joined to the old one by a `mcf.metric_supersession` record (2.13).

Codes: `BRK_NOT_CURRENT` (the supersedes target is not the latest set), `BRK_UNCHANGED` (same content hash), `BRK_ROLE_INELIGIBLE`, `BRK_REACH_NOT_ON_GRAIN`, `BRK_REACH_BAD_STEP`, `BRK_IS_CURRENCY` (currency and unit are not breakdowns, A§3.6), `GRP_ARCHIVED`.

### 4.5 Archive

`PATCH groups/:groupId/archive` with a reason. It sets `archived_at`; the code stays reserved (0085-H, 0085-I). Re-pointing a grain is a new group plus this archive (A§5 item 4).

Codes: `GRP_HAS_LIVE_MEMBERS` (archive the members first), `GRP_IS_INPUT` (a live derived group version names it as an input), `GRP_ALREADY_ARCHIVED`.

## 5. Base and derived grammar, worked through

All on Customer Invoice unless stated. "CI" is Customer Invoice.

| Metric | Group grammar | Parts | Member |
|---|---|---|---|
| Invoice count | base, `entity_count`, `flow_per_period`, unit `count` | `period_anchor` invoice date | no axis, no band |
| Invoiced amount | base, `sum`, `flow_per_period`, unit `currency` | `measure` invoice amount; `context` its currency code; `period_anchor` invoice date | no axis. The metric contract partitions by currency, or a sibling member pins one currency by an axis on the currency code (master value source) |
| Open AR at P | base, `sum`, `stock_at_period_end`, `residual`, unit `currency` | `measure` invoice amount; `context` currency; `age_anchor` due date; event input: Receivable Application, its canonical contract version, grain key the CI identity, event date the application date, anchor date the invoice date, `anchor_sign` +1; legs: debit leg key with amount −1, credit leg key with amount +1 | the total member: no band |
| Aging buckets | the same group as open AR | bands `d0_30`, `d31_60`, `d61_90`, `d91_plus` | one sibling per band, e.g. `d31_60` |
| DSO | derived, `ratio`, `instantaneous`, unit `days`, reporting anchor `evaluation_point`; output grain Legal Entity | inputs `numerator` = the open AR total member version, `denominator` = the invoiced amount member version (`flow_per_period`, 365 days ending P); constant slot `days_in_period`, integer | constant 365; no dependency rows (the inputs are the group version's). Both input metric contracts partition by `issuing_legal_entity` and by currency |
| Period-over-period change | derived, `delta`, `flow_per_period`, unit `count`, reporting anchor `input_anchor` = invoice date | inputs `operand_current` (offset 0) and `operand_prior` (offset −1), both the invoice count member version | nothing to select |
| Gross profit | derived, `linear_combination`, `flow_per_period`, unit `currency`, reporting anchor `input_anchor`; output grain Legal Entity | inputs `operand_revenue` (+1) and `operand_cost_of_sales` (−1), each a `sum` member version partitioned by the legal entity reference and by currency | nothing to select |
| Distinct customers invoiced | base, `count_distinct`, `flow_per_period`, unit `count` | `measure` the CI `customer` reference; `period_anchor` invoice date | no axis |
| Invoices for customers in segment X | base, `entity_count`, `flow_per_period`, unit `count` | `period_anchor` invoice date; `axis` 1 = a Customer segment code concept (not yet created), step: CI `customer` reference version, Customer entity version, the segment concept version | selects X |

Three facts from the live reads bear on these. The Receivable Application amounts have no currency context, so open AR waits on a concept act (`GRP_EVENT_INVALID` today). Customer has no segment concept at all (its code concepts are country, currency, industry, payment terms, status and territory), so segment X waits on a concept act that creates one with an enumerated value source; until then it is refused at reach, not at value source. The invoice amounts on CI carry a context, so invoiced amount fits now.

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

Classified from live reads on 2026-11-26. Rules, in order: a test fixture or probe is a test leftover; a grain that is wrong in meaning is mis-pointed; a grain on the owner's list of 15 is a non-countable split (A§8.1); a derived group is classed by its output grain; a base group with no anchor needs a date; the rest fit.

**Output grain.** A derived group's grain is its output grain (A§3.3): each input is evaluated at it, through a breakdown that reaches it. Only 8 derived groups sit on Legal Entity, and all 8 are in the owner's list. The other 52 sit on a record grain (Customer Invoice, Asset, and so on), which would make each value a per-record ratio. A grain is never changed in place, so each of these is re-pointed: a new group on the output grain, and the old group archived with its code reserved (4.5; A§5 item 4). 49 of them are classed here; the 3 on Tax Return, Financial Close and GL Account Reconciliation stay in the owner's split and are re-pointed in the same way once their base inputs exist. Legal Entity is the output grain where an input grain has a reference to it; 11 such references sit on 10 entities.

| Class | Base | Derived | Total | Of which, no version | Disposition |
|---|---|---|---|---|---|
| Fits | 61 | 0 | 61 | 14 | grounded v2 by the successor command (4.2), or v1 where there is none; 11 carry `closing_concept_id` in JSON, which becomes a `closing` part with `gross_binary` |
| Needs a date | 14 | 0 | 14 | 0 | all on Customer Invoice or Supplier Invoice: declare the period anchor, or `stock_at_period_end` with a closing part or an event input |
| Derived, re-point, Legal Entity reachable | 0 | 27 | 27 | 3 | on Customer Invoice, Customer Invoice Line Item, Customer Payment, Journal Entry, Journal Entry Line, Supplier Invoice and Tax Line: a new group on Legal Entity with a declared reporting anchor (A§3.3); archive the old |
| Derived, re-point, Legal Entity not reachable | 0 | 22 | 22 | 10 | on Asset, Bank Account, Budget, Contract, Debt Instrument, GL Account, Hedge Instrument, Maintenance Order, Performance Obligation, Product and Supplier Invoice Line: a concept act first (a reference to Legal Entity on the input grain), or another output grain the sweep names; then as the row above |
| Mis-pointed | 2 | 0 | 2 | 2 | Recognition Event is employee recognition. Archived with no replacement (owner ruling (4) of `060d5328`) |
| Non-countable split | 4 | 11 | 15 | 0 | A§8.1: 6 wait for identity concepts (Tax Return, Financial Close, GL Account Reconciliation); 8 Legal Entity groups stay derived; `cost_center_master` becomes a breakdown on the Journal Entry Line `cost_center` reference and is archived |
| Test leftover | 2 | 0 | 2 | 0 | archive `zz_trackA_cefa537` and `je_line_grain_probe`; codes stay reserved |
| **Total** | **83** | **60** | **143** | **29** | |

**The three groups whose class differs from v1's.** The group row and its template kind agree with each other; v1 does not.

| Group | Group class (template kind) | v1 class | Disposition |
|---|---|---|---|
| `ar_customer_concentration_derived` | derived (`derivation`) | base | `top_n_share` (2.2), ranked by the Customer Invoice `customer` reference; re-pointed with the derived class to Legal Entity (Customer Invoice has a Legal Entity reference) |
| `ap_supplier_concentration_derived` | derived (`derivation`) | base | the same, ranked by the Supplier Invoice supplier reference |
| `collections_overdue_base` | base (`aggregation`) | derived | grounded v2 as `base` (it needs a date, above); v1 stays as history |

The successor command refuses a class different from the group's (`GV_CLASS_CHANGED`), so no v2 can carry v1's error forward. None of the three has a member.

**The derived arithmetic.** Of the 60 derived groups, 36 carry `op` `ratio`, 9 `derivation`, 1 `formula` and 14 none. `ratio` maps to `ratio` or `percentage_of_total`. The 10 with `derivation` or `formula` (the 8 on Legal Entity, plus `capital_investment_metrics` on Asset and `ap_discount_capture` on Supplier Invoice) declare `ratio` or `linear_combination` fresh. Of the 14 with none (9 on Customer Invoice, 5 on Supplier Invoice), 12 read as ratios or percentages by name and the 2 concentration groups are `top_n_share`.

**Recognition overlap (sweep item, owner ruling (4)).** Two Customer Invoice Line Item groups, `revenue_line_recognition` (count) and `revenue_recognition_amounts` (sum), both with no version and no member, overlap the Revenue Recognition Line groups `revenue_recognition_line_counts` and `revenue_recognition_line_amounts`. The sweep decides each: archive as a duplicate, or ground it with a meaning that differs from the Revenue Recognition Line pair and say how.

**Concept acts before the sweep.** Of the 61 that fit, 26 are `sum` groups whose grain has no amount concept with a currency or unit context. They sit on 13 entities (Journal Entry Line 7, Asset 4, GL Account 3, Tax Line 2, Bank Account 2, and one each on Debt Instrument, Hedge Instrument, Contract, Maintenance Order, Performance Obligation, Product, Revenue Recognition Line and Budget). They would be refused with `GRP_SUM_NO_CONTEXT`. Each needs a concept act on the business concept path first. 16 base groups have no `op` in their template, so their measure kind is declared fresh; the 14 derived groups with none are above.

**Order.** (1) Concept acts: identity concepts on 6 entities (the owner's 3, plus Performance Obligation, Debt Instrument and Hedge Instrument, whose 9 groups otherwise meet `GRP_COUNT_NO_IDENTITY` or an ungrounded input; section 3), contexts on 13, references to Legal Entity where the sweep re-points to it, the Customer segment concept if wanted, value sources through Unit V. (2) Archive the 2 leftovers, the 2 mis-pointed groups and `cost_center_master`. (3) Ground the base groups family by family, Finance first, then re-point the derived groups on top of them. Every change goes through the commands of section 4, never a row edit. Groups whose members differ only by measure are split at this step. The owner opens each batch by one grant (4.1). (4) The one live member, Customer Invoice Count, is re-placed by a new member version under the grounded `ci_invoice_volume` v2; that new definition version is realized by a new metric contract with a `mcf.metric_supersession` record from the current one (2.13).

## 8. The unit order and the migrations

| # | Unit | Migrations |
|---|---|---|
| 1 | The decision unit: the grounding ADR together with DEC-45200d, FND-ERR-010 or the next free, and the Foundation text edits (owner's landing go) | none |
| 2 | This design | none |
| 3 | Unit V, typed allowed values, with its measured ripple of 39 bc-core files that read `canonical_value_set` and 2 that read `governed_values_json` | **M-V**: value rows, value source, the masters' freeze triggers, `member_version_discriminator_value` |
| 4 | The schema | **M-G1**: the group tables and routines. **M-G2**: the member and contract extensions, finalize, the realization check. **M-G3**, after readers move: drop the retired columns |
| 5 | The sweep (section 7) | none: commands only |

**Numbers.** bc-db origin/main ends at 0084. Open PR 200 (head `ae4d7287`) holds 0085, 0086, 0087 and 0089. The records design plans 0088 and tenant 0008. Open PRs 177 and 111 hold 0073 and 0039. So each migration takes the next free number at authoring, 0090 or later today, after checking open bc-db PRs.

## 9. The database proposal (for the owner's database yes)

| # | Object | Change | Rollback |
|---|---|---|---|
| V-1 | `concept_registry.business_concept_value` (new) | concept version FK, value code, label; insert-only | drop, before any member selects a value |
| V-2 | `concept_registry.value_master` (new) | names a master table and key column; 2 rows: `master.dim_currency.currency_code`, `master.dim_country.alpha2` | drop with V-3 |
| V-3 | `business_concept_version` (12 columns) | add `value_source_code` (`enumerated`, `master`) and `value_master_id` FK (14); set the 27 active currency and 4 active country code concepts to `master` through new concept versions, never in place; the 2 superseded currency concepts get no new version | drop columns before V-4 has rows |
| V-4 | `metric_directory.member_version_discriminator_value` (new) | exactly one of `concept_value_id`, `currency_code` (FK `dim_currency`), `country_alpha2` (FK `dim_country`); trigger matches the value source | drop before any new member |
| V-5 | `master.dim_currency`, `master.dim_country` | freeze triggers: refuse an UPDATE of `currency_code`, `decimal_places`; of `alpha2`, `alpha3`, `numeric_code`; refuse DELETE and TRUNCATE | drop triggers |

*Note on V-5.* `master.dim_country.currency_code` stays out of this design: no freeze and no FK (owner, `53e9659c` (2); no bc-core reader today). If a metric ever needs a country's currency, it gets its own dated record (`effective_from` / `effective_to`, FK to `master.dim_currency`); nothing is added until such a reader exists.

| G1-1 | `group_version`, `member_version` | unique `(group_version_uid, class_code)` and `(group_version_uid, grain_entity_id)` on `group_version`; unique `(member_version_uid, group_version_uid)` on `member_version` (for 2.7) | drop indexes |
| G1-2 | 2.2 to 2.11 (10 tables) | create, with FKs, checks, immutability, TRUNCATE refusal, finalize guards, grants | drop all, valid only before any grounded group version exists |
| G1-3 | section 3 routines | create, with the insert triggers that call them | drop |
| G1-4 | `fn_group_version_grammar_finalize` | deferred constraint trigger on `group_version` for rows created after the migration | drop trigger |
| G1-5 | `group`, `group_version` | `template_json` becomes nullable on `group`; a new row with non-NULL `template_json` is refused | restore NOT NULL only if no NULL row exists |
| G2-1 | `member_version_discriminator`, `_constant`, `member` | columns of 2.12; drop NOT NULL on `member_version_discriminator.governed_values_json`, with a CHECK that it is NULL where `group_version_uid` is set; drop NOT NULL on `member.discriminator_json`; `value_json` dropped (0 rows) | re-add `value_json` and the NOT NULLs (valid while no NULL row exists), drop new columns, before any new row |
| G2-2 | `member_version_age_band` (new) | 2.12 | drop before any row |
| G2-3 | `fn_member_version_finalize` | the 2.12 rules | restore as after 0085 |
| G2-4 | `mcf.mcv_breakdown_set_pin` (new); `mcf.metric_computed_dimension_ref` | 2.13 | drop, before any pin |
| G2-5 | `metric_directory.fn_realization_event_guard` | call `fn_realization_grammar_check` on assert for a grounded member version | restore as after 0086 |
| G3-1 | later | drop `group.template_json`, `group_version.template_json`, `member.measure_concept_id`, `member.discriminator_json`, `member.derivation_json`, `member_version.grain_entity_id`, `grain_entity_version_id`, `temporal_intent_json`, `output_intent_json`, and the tables `member_version_dependency` and `member_version_direct_input` (old values kept in an evidence file with a sha256 per value, as 0088-B) | re-add and restore from the evidence file |
| Backfill | none | no migration writes directory data; the sweep uses the commands | |

Each migration is proven on an owner- and grant-faithful restore of a fresh read-only dump, with `bc_platform_runtime` vectors and the six proof cases, never on live. Each live apply needs its own recorded grant.

## 10. Foundation gate (DEC-79b62f)

1. **Why this location?** B for the grammar, which was a missing declaration. E for the typed tables that hold it. The routines guard E against the B rule.
2. **Why not an upper layer?** A does not declare a metric's shape. The concept gaps found here (identity concepts on 6 entities, contexts on 13, references to Legal Entity, a segment concept, value sources) are fixed in the registry by concept acts, not compensated in groups.
3. **Why not a lower layer?** A lint or an evaluation-time check (D, F) would be a net. The live member layer, `governed-selection.ts`, the resolver and the DEC-45200d schedule declaration are extended, not bypassed. Reads never trigger evaluation.
4. **Design or execution act?** A design act, named in the amendment, its ADR, FND-ERR-010 and TSK-09855b.

Invariants: III (every new table is insert-only; masters frozen); IV (every reference is a pinned version; no current set is read); I (members select, never classify, sign or age); VI (matched and unmatched counts emitted).

## 11. Open questions for the owner

None open. Revision 1's three questions are answered by the owner (barecount-devhub `060d5328`): the review that opens a group is the owner's, by a desk grant that may cover a batch (2.11, 4.1); grounded parts live only on the group version (2.7, 2.12); the two Recognition Event groups are archived with no replacement (7). Revision 2's question on concentration is answered by `1ef2d04e`: a governed top-N share (2.2).
