---
uid: bcf-evidence-schema-phase-a1-dbcp
title: BCF Evidence Schema — Phase A1 DBCP (bcf.* schema + 4 evidence tables; substrate design only)
description: Phase A1 planning DBCP under the operator-authorized Option A path from `bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` (merged at bc-docs-v3 main `6f8cc159f6f21b6170c3d3195df616a1aa567348`). Designs the new `bcf.*` schema and 4 evidence tables (`bcf.panel_output_record`, `bcf.authoring_panel_rejection_log`, `bcf.calibration_event`, `bcf.certification_record`) as 1:1 column-shape mirrors of their `contract.*` counterparts plus two additive substrate-enforced HR1 no-synthetic CHECKs. **SUBSTRATE DESIGN ONLY.** No DDL is applied by this DBCP. No data is migrated. No FK is redirected. No writer is flipped. No bc-core source is edited. No `mcf.*` substrate is touched. No tenant `tbc_{slug}_dev` database is connected to. No `metric.*` row is affected. Phase A2 (3,568-row authority-bearing migration), Phase A3 (writer/reader flip), Phase A4 (freeze/retire `contract.*` evidence tables), and Phase A5 (MCF FK reconsideration + M12 writer flip) are explicitly out of scope of this DBCP and each requires its own separately authorized planning gate. The parent DBCP merged D1..D11 (recorded in `bcf-mcf-evidence-boundary-operator-decisions-d1-d11.md`); this Phase A1 DBCP introduces its own narrower D1..D11 covering only the substrate creation. PR #133 (bc-core dry-run scripts) is not edited by this DBCP and its apply gate remains paused per parent D9. The full column shape of each target table is captured in §4 from a read-only `bc-postgres` MCP probe (`allow_write=false`) and serves as the parity-probe baseline for the separately authored Phase A1 apply DBCP.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a1-substrate-design
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A1 DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> Under the operator-authorized Option A from the boundary DBCP (`6f8cc15`), what is the exact substrate design — schema name, table shapes, column inventory, CHECK constraints, indexes, FK strategy — for the new `bcf.*` evidence schema that Phase A2 will migrate authority-bearing BCF rows into?

### 1.2 In scope

- Schema name decision (`bcf`)
- Target table list (4: `panel_output_record`, `authoring_panel_rejection_log`, `calibration_event`, `certification_record`)
- 1:1 column-shape mirror strategy (column name + type + nullability + default + position from each `contract.*` counterpart)
- CHECK constraint mirror strategy (all 26 existing `contract.*` CHECKs preserved on the `bcf.*` counterparts; constraint names re-prefixed `bcf_`)
- Additive substrate-enforced HR1 no-synthetic CHECK on `bcf.panel_output_record` and `bcf.certification_record` (NOT present in `contract.*`)
- Index mirror strategy (all 20 existing `contract.*` indexes preserved on `bcf.*`; partial-unique `uq_certification_record__registry_dedup` preserved as `uq_bcf_certification_record__registry_dedup`)
- FK strategy (3 intra-`bcf.*` FKs declared at table creation; cross-schema FKs from `mcf.*` and `contract.intake_queue` to `contract.panel_output_record` left untouched in Phase A1 — those belong to Phase A5)
- Migration boundary specifying exactly where Phase A1 ends and Phase A2/A3/A4/A5 begin
- Schema-shape parity probe specification (the comparison that the future Phase A1 apply gate must pass before declaring "A1 ships")
- Risk register, operator decisions D1..D11, test/evidence plan, rollback plan

### 1.3 Explicit non-scope

- ❌ **No DDL apply.** No `CREATE SCHEMA`, no `CREATE TABLE`, no `CREATE INDEX`, no `ALTER ... ADD CONSTRAINT`, no `COMMENT ON`. This DBCP only describes what those statements will eventually look like; the apply itself is a separately operator-authorized follow-up DBCP.
- ❌ **No DML.** No row migration, no `INSERT INTO bcf.*`, no `UPDATE`, no `DELETE`. Phase A2 owns row migration.
- ❌ **No writer/reader flip.** BCF authoring writers continue to write to `contract.*` during Phase A1. Phase A3 owns the writer/reader cutover.
- ❌ **No FK redirect from `mcf.*` to `bcf.*` or to a new `mcf.metric_authoring_panel_output_record`.** Phase A5 owns this.
- ❌ **No `contract.*` evidence table freeze or retire.** Phase A4 owns this.
- ❌ **No bc-core source edit.** No service code change, no Drizzle schema change, no migration file generated.
- ❌ **No `mcf.*` substrate touched.** All 17 `mcf.*` tables remain at 0 rows; no schema change.
- ❌ **No tenant `tbc_{slug}_dev` database connection.** This DBCP only references the platform DB (`bc_platform_dev`).
- ❌ **No `metric.*` schema change.** Legacy `metric.*` retirement is reserved for the M17 tenant-runtime gate.
- ❌ **No PR #133 edit.** PR #133 stays untouched. Its apply gate remains paused per parent D9 (Phase A1+A2 designs must both be operator-authorized before apply can run).
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** Operational gates remain closed. M14 remains CLOSED.
- ❌ **No `framework_policy` placement.** Parent D7 deferred this to a separate gate. The 3 `contract.framework_policy` rows continue functioning in `contract.*` during Phase A1.

## 2. Authority

| Artifact | Location | Authority for |
|---|---|---|
| Parent boundary DBCP (Option A chosen) | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` | Option A target architecture; 5-phase migration plan; A1..A5 gate sequence |
| Parent decision record (D1..D11 verdicts) | `docs/implementation/bcf-mcf-evidence-boundary-operator-decisions-d1-d11.md` @ same PR | D2=A; D4=ACCEPT (Phase A1+A2 design authorization); D6=ACCEPT (5-phase sequence); D7=DEFER (framework_policy); D8/D9 (PR #133 sequencing) |
| Hard rules HR1..HR5 | parent DBCP §5 | Substrate constraints enforced by this design |
| Predecessor cleanup DBCP | `docs/implementation/bcf-authoring-test-row-cleanup-dbcp.md` @ bc-docs-v3 main `0f42662` | The 11-row smoke debt that PR #133 will retire from `contract.*` BEFORE Phase A2 row migration |
| Live DB shape inventory (this DBCP §4) | `bc-postgres` MCP `allow_write=false` probes against `bc_platform_dev` @ 2026-05-28 post-PR #11 merge | The byte-exact column / CHECK / index / FK inventory that the new `bcf.*` tables must mirror |

## 3. Current state of the platform DB (read-only inventory)

This inventory is the post-PR #11-merge snapshot. All numbers verified via `bc-postgres` MCP with `allow_write=false` against `bc_platform_dev` on 2026-05-28T16:06+.

| Schema | Tables | Total rows (relevant) | Status under Option A |
|---|---|---|---|
| `bcf.*` | **0** | n/a (DOES NOT EXIST) | This DBCP designs the schema creation |
| `contract.*` evidence cluster | 4 (panel_output_record, authoring_panel_rejection_log, calibration_event, certification_record) | **24 + 1 + 23 + 3531 = 3,579** | A1 leaves these accepting BCF writes; A3 flips writers; A4 freezes/retires |
| `contract.framework_policy` | 1 | 3 | Untouched by Phase A1..A5 (parent D7 deferred) |
| `contract.*` other (chain infrastructure) | many | ~127,000 | Out of scope; different concern from authoring evidence |
| `mcf.*` | 17 | **0** (all tables empty) | Untouched by Phase A1; Phase A5 will add `mcf.metric_authoring_panel_output_record` and redirect 5 cross-schema FKs |
| `metric.*` (legacy) | 16 | ~16,820 | Out of scope (D11) |
| Tenant `tbc_{slug}_dev` | n/a | n/a | Out of scope (D10) |

**Inbound FK closure on `contract.panel_output_record.panel_run_uid` (9 FKs, all RESTRICT)** — unchanged from parent DBCP §3.7. Phase A1 does NOT alter any of these. Phase A5 will replace the 5 from `mcf.*`. The 3 from `contract.*` evidence (rejection_log / calibration_event / certification_record) become irrelevant after Phase A4 retire and are replaced by 3 intra-`bcf.*` FKs created by THIS Phase A1 design.

## 4. Target schema design — `bcf.*` (the 4 tables)

### 4.1 Schema identity

- Schema name: **`bcf`**
- Owner: same role as `contract.*` schema (platform-DB superuser at apply time; documented separately in the Phase A1 apply DBCP)
- `COMMENT ON SCHEMA bcf` proposed: *"Business Concept Framework authoring evidence. Houses BCF panel run records, rejection logs, calibration events, and certification records previously held in contract.*. See bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md."*

### 4.2 `bcf.panel_output_record` (13 columns; mirror of `contract.panel_output_record`)

Column shape (column / type / nullable / default):

| # | Column | Type | Nullable | Default |
|---|---|---|---|---|
| 1 | `panel_run_uid` | `uuid` | NO | `gen_random_uuid()` |
| 2 | `stage_code` | `text` | NO | — |
| 3 | `prompt_version` | `text` | NO | — |
| 4 | `model_identity_json` | `jsonb` | NO | — |
| 5 | `agent_outputs_json` | `jsonb` | NO | — |
| 6 | `input_hash` | `text` | NO | — |
| 7 | `verdict_code` | `text` | NO | — |
| 8 | `verdict_payload_json` | `jsonb` | NO | `'{}'::jsonb` |
| 9 | `grounding_check_result` | `text` | NO | — |
| 10 | `quarantined` | `boolean` | NO | `false` |
| 11 | `sampling_status` | `text` | NO | — |
| 12 | `policy_version` | `text` | NO | — |
| 13 | `created_at` | `timestamptz` | NO | `now()` |

Primary key: `(panel_run_uid)`.

CHECK constraints (5 mirrored from `contract.panel_output_record` + 1 NEW for HR1):

| # | Constraint name (bcf.*) | Clause | Source |
|---|---|---|---|
| 1 | `bcf_panel_output_record_stage_code_chk` | `stage_code IN ('authoring','publication','lifecycle_audit')` | mirror |
| 2 | `bcf_panel_output_record_grounding_chk` | `grounding_check_result IN ('pass','quarantined')` | mirror |
| 3 | `bcf_panel_output_record_quarantine_mirror_chk` | `quarantined = (grounding_check_result = 'quarantined')` | mirror |
| 4 | `bcf_panel_output_record_sampling_chk` | `sampling_status IN ('not_sampled','sampled_for_calibration','sample_routed_to_operator')` | mirror |
| 5 | `bcf_panel_output_record_reject_defect_code_chk` | `verdict_code <> 'REJECT' OR (verdict_payload_json ? 'defect_code' AND (verdict_payload_json ->> 'defect_code') IN ('DEF_PLACEHOLDER','DEF_RATIONALE','DEF_BOILERPLATE','IDENT_NAME_SPLITTER','IDENT_SOURCE_SUFFIX_LEAK','IDENT_TAUTOLOGICAL','PROV_FABRICATED','STRUCT_TYPE_INCOHERENT','STRUCT_FAMILY_UNIT_MISSING'))` | mirror |
| 6 | **`bcf_panel_output_record_no_synthetic_provider_chk`** | `(model_identity_json -> 'maker' ->> 'provider') NOT IN ('synthetic','replay','mock','canned')` | **NEW — substrate-enforces HR1** |

Indexes (4 mirrored, with `bcf_` prefix):

| # | Index name (bcf.*) | Definition |
|---|---|---|
| 1 | `bcf_panel_output_record_pkey` | UNIQUE on `(panel_run_uid)` (implicit via PK) |
| 2 | `idx_bcf_panel_output_record_policy` | btree on `(policy_version, created_at)` |
| 3 | `idx_bcf_panel_output_record_stage` | btree on `(stage_code, created_at)` |
| 4 | `idx_bcf_panel_output_record_quarantined` | btree on `(created_at) WHERE quarantined = true` |

### 4.3 `bcf.authoring_panel_rejection_log` (15 columns; mirror of `contract.authoring_panel_rejection_log`)

| # | Column | Type | Nullable | Default |
|---|---|---|---|---|
| 1 | `rejection_log_id` | `uuid` | NO | `gen_random_uuid()` |
| 2 | `scope_code` | `text` | NO | — |
| 3 | `primitive_type` | `text` | NO | — |
| 4 | `primitive_id` | `uuid` | NO | — |
| 5 | `panel_run_uid` | `uuid` | NO | — |
| 6 | `defect_code` | `text` | NO | — |
| 7 | `rationale_text` | `text` | NO | — |
| 8 | `policy_version` | `text` | NO | — |
| 9 | `decided_at` | `timestamptz` | NO | — |
| 10 | `override_state` | `text` | NO | `'open'::text` |
| 11 | `override_decided_by_sub` | `text` | YES | — |
| 12 | `override_decided_at` | `timestamptz` | YES | — |
| 13 | `override_to_state` | `text` | YES | — |
| 14 | `override_rationale_text` | `text` | YES | — |
| 15 | `created_at` | `timestamptz` | NO | `now()` |

PK: `(rejection_log_id)`. UNIQUE: `(panel_run_uid)`.

CHECKs (7 mirrored from `contract.authoring_panel_rejection_log`, all with `bcf_` prefix):

| # | Constraint name (bcf.*) | Clause |
|---|---|---|
| 1 | `bcf_authoring_panel_rejection_log_scope_code_chk` | `scope_code IN ('bf_bo','cf','mapping')` |
| 2 | `bcf_authoring_panel_rejection_log_primitive_type_chk` | `primitive_type IN ('business_field','business_object','canonical_field')` |
| 3 | `bcf_authoring_panel_rejection_log_defect_code_chk` | `defect_code IN ('DEF_PLACEHOLDER','DEF_RATIONALE','DEF_BOILERPLATE','IDENT_NAME_SPLITTER','IDENT_SOURCE_SUFFIX_LEAK','IDENT_TAUTOLOGICAL','PROV_FABRICATED','STRUCT_TYPE_INCOHERENT','STRUCT_FAMILY_UNIT_MISSING')` |
| 4 | `bcf_authoring_panel_rejection_log_rationale_text_chk` | `char_length(rationale_text) > 0` |
| 5 | `bcf_authoring_panel_rejection_log_override_state_chk` | `override_state IN ('open','manual_override_applied','expired')` |
| 6 | `bcf_authoring_panel_rejection_log_override_to_state_chk` | `override_to_state IS NULL OR override_to_state = 'draft'` |
| 7 | `bcf_authoring_panel_rejection_log_manual_override_chk` | `override_state <> 'manual_override_applied' OR (override_decided_by_sub IS NOT NULL AND override_decided_at IS NOT NULL AND override_to_state IS NOT NULL AND char_length(override_rationale_text) >= 40)` |

Indexes (5 mirrored):

| # | Index name (bcf.*) | Definition |
|---|---|---|
| 1 | `bcf_authoring_panel_rejection_log_pkey` | UNIQUE on `(rejection_log_id)` |
| 2 | `bcf_authoring_panel_rejection_log_panel_run_uid_uniq` | UNIQUE on `(panel_run_uid)` |
| 3 | `idx_bcf_authoring_panel_rejection_log_defect` | btree on `(defect_code, created_at)` |
| 4 | `idx_bcf_authoring_panel_rejection_log_primitive` | btree on `(primitive_type, primitive_id, created_at)` |
| 5 | `idx_bcf_authoring_panel_rejection_log_open` | btree on `(created_at) WHERE override_state = 'open'` |

### 4.4 `bcf.calibration_event` (13 columns; mirror of `contract.calibration_event`)

| # | Column | Type | Nullable | Default |
|---|---|---|---|---|
| 1 | `calibration_event_uid` | `uuid` | NO | `gen_random_uuid()` |
| 2 | `panel_run_uid` | `uuid` | NO | — |
| 3 | `ai_verdict_code` | `text` | NO | — |
| 4 | `sample_routed_to_operator` | `boolean` | NO | — |
| 5 | `operator_decision_code` | `text` | YES | — |
| 6 | `operator_decision_at` | `timestamptz` | YES | — |
| 7 | `operator_decision_rationale_text` | `text` | YES | — |
| 8 | `downstream_signal_code` | `text` | YES | — |
| 9 | `downstream_signal_at` | `timestamptz` | YES | — |
| 10 | `downstream_signal_ref` | `text` | YES | — |
| 11 | `policy_version` | `text` | NO | — |
| 12 | `created_at` | `timestamptz` | NO | `now()` |
| 13 | `updated_at` | `timestamptz` | NO | `now()` |

PK: `(calibration_event_uid)`. UNIQUE: `(panel_run_uid)`.

CHECKs (4 mirrored):

| # | Constraint name (bcf.*) | Clause |
|---|---|---|
| 1 | `bcf_calibration_event_op_decision_chk` | `operator_decision_code IS NULL OR operator_decision_code IN ('confirm','override','n_a_not_sampled')` |
| 2 | `bcf_calibration_event_op_decision_paired_chk` | `(operator_decision_code IS NULL) = (operator_decision_at IS NULL)` |
| 3 | `bcf_calibration_event_downstream_signal_chk` | `downstream_signal_code IS NULL OR downstream_signal_code IN ('supersession','reversal','no_signal','n_a')` |
| 4 | `bcf_calibration_event_downstream_signal_paired_chk` | `(downstream_signal_code IS NULL) = (downstream_signal_at IS NULL)` |

Indexes (4 mirrored):

| # | Index name (bcf.*) | Definition |
|---|---|---|
| 1 | `bcf_calibration_event_pkey` | UNIQUE on `(calibration_event_uid)` |
| 2 | `bcf_calibration_event_panel_run_uniq` | UNIQUE on `(panel_run_uid)` |
| 3 | `idx_bcf_calibration_event_policy` | btree on `(policy_version, created_at)` |
| 4 | `idx_bcf_calibration_event_pending_decision` | btree on `(sample_routed_to_operator, operator_decision_code) WHERE sample_routed_to_operator = true AND operator_decision_code IS NULL` |

### 4.5 `bcf.certification_record` (27 columns; mirror of `contract.certification_record`)

| # | Column | Type | Nullable | Default |
|---|---|---|---|---|
| 1 | `certification_record_id` | `uuid` | NO | `gen_random_uuid()` |
| 2 | `primitive_type` | `text` | YES | — |
| 3 | `primitive_id` | `uuid` | YES | — |
| 4 | `action_code` | `text` | NO | — |
| 5 | `from_state_code` | `text` | YES | — |
| 6 | `to_state_code` | `text` | YES | — |
| 7 | `is_archived_after` | `boolean` | YES | — |
| 8 | `gate_results_json` | `jsonb` | NO | `'{}'::jsonb` |
| 9 | `advisory_verdicts_json` | `jsonb` | NO | `'[]'::jsonb` |
| 10 | `override_gate_code` | `text` | YES | — |
| 11 | `override_rationale_text` | `text` | YES | — |
| 12 | `override_followup_task_uid` | `text` | YES | — |
| 13 | `certifier_sub` | `text` | NO | — |
| 14 | `certifier_role_at_action` | `text` | NO | — |
| 15 | `certifier_email` | `text` | YES | — |
| 16 | `supersedes_primitive_id` | `uuid` | YES | — |
| 17 | `created_at` | `timestamptz` | NO | `now()` |
| 18 | `panel_run_uid` | `uuid` | YES | — |
| 19 | `prompt_version` | `text` | YES | — |
| 20 | `model_identity_json` | `jsonb` | YES | — |
| 21 | `input_hash` | `text` | YES | — |
| 22 | `policy_version` | `text` | YES | — |
| 23 | `sampling_status` | `text` | YES | — |
| 24 | `grounding_check_result` | `text` | YES | — |
| 25 | `governance_scope` | `text` | YES | — |
| 26 | `subject_kind` | `text` | YES | — |
| 27 | `target_registry_id` | `uuid` | YES | — |

PK: `(certification_record_id)`.

CHECKs (10 mirrored + 1 NEW for HR1):

| # | Constraint name (bcf.*) | Clause | Source |
|---|---|---|---|
| 1 | `bcf_certification_record_primitive_type_chk` | `primitive_type IS NULL OR primitive_type IN ('canonical_field','business_field','business_object')` | mirror |
| 2 | `bcf_certification_record_action_code_chk` | `action_code IN (28 enum values)` — verbatim from `contract.certification_record_action_code_chk` | mirror |
| 3 | `bcf_certification_record_governance_scope_chk` | `governance_scope IS NULL OR governance_scope = 'registry'` | mirror |
| 4 | `bcf_certification_record_subject_kind_chk` | `subject_kind IS NULL OR subject_kind IN ('entity','business_concept','characteristic','alias','supersession_proposal')` | mirror |
| 5 | `bcf_certification_record_scope_action_chk` | governance_scope×action_code paired enum | mirror |
| 6 | `bcf_certification_record_row_shape_chk` | non-registry vs registry mutual-exclusion row shape | mirror |
| 7 | `bcf_certification_record_nf1_all_or_none_chk` | the 7 NF1 fields all-NULL-or-all-NOT-NULL | mirror |
| 8 | `bcf_certification_record_override_chk` | override fields all-NULL-or-all-set-with-≥40-char-rationale | mirror |
| 9 | `bcf_certification_record_sampling_chk` | `sampling_status IS NULL OR sampling_status IN ('not_sampled','sampled_for_calibration','sample_routed_to_operator')` | mirror |
| 10 | `bcf_certification_record_grounding_chk` | `grounding_check_result IS NULL OR grounding_check_result IN ('pass','quarantined')` | mirror |
| 11 | **`bcf_certification_record_no_synthetic_provider_chk`** | `model_identity_json IS NULL OR (model_identity_json -> 'maker' ->> 'provider') NOT IN ('synthetic','replay','mock','canned')` | **NEW — substrate-enforces HR1** |

Indexes (7 mirrored):

| # | Index name (bcf.*) | Definition |
|---|---|---|
| 1 | `bcf_certification_record_pkey` | UNIQUE on `(certification_record_id)` |
| 2 | `idx_bcf_certification_record_action` | btree on `(action_code, created_at DESC)` |
| 3 | `idx_bcf_certification_record_certifier` | btree on `(certifier_sub, created_at DESC)` |
| 4 | `idx_bcf_certification_record_panel_run` | btree on `(panel_run_uid) WHERE panel_run_uid IS NOT NULL` |
| 5 | `idx_bcf_certification_record_primitive` | btree on `(primitive_type, primitive_id, created_at DESC)` |
| 6 | `idx_bcf_certification_record_target_registry` | btree on `(target_registry_id) WHERE target_registry_id IS NOT NULL` |
| 7 | `uq_bcf_certification_record__registry_dedup` | UNIQUE on `(panel_run_uid, subject_kind, action_code) WHERE governance_scope = 'registry'` |

## 5. Hard boundary rules (restated; from parent DBCP §5)

These remain in force for Phase A1 and every downstream phase:

- **HR1** — No synthetic / mock / replay / canned data written to persistent substrate. **Phase A1 substrate-enforces HR1 on the new `bcf.*` tables via the two additive `bcf_*_no_synthetic_provider_chk` CHECKs in §4.2 and §4.5.** Existing `contract.*` tables do NOT carry this CHECK today; they continue to permit pre-existing rows (including the one known violation that PR #133 will retire).
- **HR2** — MCF evidence belongs in `mcf.*`. Phase A1 does not change MCF substrate; Phase A5 will.
- **HR3** — Future MCF metric authority events must NOT write to generic `contract.*` authoring tables. Phase A1 does not change MCF behaviour; Phase A5 will retarget the M12 writer.
- **HR4** — Tenant result DBs are separate and out of scope. Phase A1 only touches the platform DB (`bc_platform_dev`).
- **HR5** — Mocks only inside unit tests or SAVEPOINT-rolled-back integration tests. Phase A1 introduces no test code; future Phase A1 apply DBCP will follow this rule.

## 6. FK strategy

### 6.1 Intra-`bcf.*` FKs declared in Phase A1 (3 FKs)

| Source table | Source column | Target | ON DELETE | Mirror of |
|---|---|---|---|---|
| `bcf.authoring_panel_rejection_log` | `panel_run_uid` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | `contract.fk_authoring_panel_rejection_log__panel_run` |
| `bcf.calibration_event` | `panel_run_uid` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | `contract.fk_calibration_event__panel_run` |
| `bcf.certification_record` | `panel_run_uid` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | `contract.fk_certification_record__panel_run` |

Constraint names: `fk_bcf_authoring_panel_rejection_log__panel_run`, `fk_bcf_calibration_event__panel_run`, `fk_bcf_certification_record__panel_run`.

### 6.2 Cross-schema FKs Phase A1 does NOT touch

| Source FK | Source schema | Target | Phase A1 disposition |
|---|---|---|---|
| `fk_intake_queue__panel_run` | `contract.intake_queue` | `contract.panel_output_record` | UNCHANGED — `contract.intake_queue` is contract-chain infrastructure (out of authoring-evidence scope per §1.3) |
| `fk_mcf_cert_panel_run` | `mcf.certification_record` | `contract.panel_output_record` | UNCHANGED — Phase A5 retarget |
| `fk_mapr_panel_run` | `mcf.metric_authoring_panel_run` | `contract.panel_output_record` | UNCHANGED — Phase A5 retarget |
| `fk_mcr_panel_run` | `mcf.metric_contract_revision` | `contract.panel_output_record` | UNCHANGED — Phase A5 retarget |
| `fk_mper_panel_run` | `mcf.metric_publication_eligibility_result` | `contract.panel_output_record` | UNCHANGED — Phase A5 retarget |
| `fk_mcs_panel_run` | `mcf.metric_supersession` | `contract.panel_output_record` | UNCHANGED — Phase A5 retarget |

**Rationale.** Phase A1 is purely additive. Touching the 5 `mcf.* → contract.*` FKs in A1 would couple A1 to A5 timing and bypass the operator-authorized 5-phase sequencing. The 3 existing intra-`contract.*` evidence FKs (rejection_log / calibration_event / certification_record → panel_output_record) also remain in place during A1 because `contract.*` writers stay live until Phase A3.

### 6.3 No `bcf.* → contract.*` cross-schema FK introduced

Phase A1 does NOT add any `bcf.* → contract.*` FK. The two clusters operate independently from the moment `bcf.*` exists. This is intentional — coupling `bcf.*` evidence to `contract.panel_output_record` would defeat the boundary the parent DBCP established.

## 7. No-synthetic rule (HR1 substrate enforcement)

Phase A1 introduces a substrate-enforced HR1 CHECK on the two `bcf.*` tables that carry `model_identity_json`:

```
CHECK (
  model_identity_json IS NULL OR
  (model_identity_json -> 'maker' ->> 'provider') NOT IN
    ('synthetic','replay','mock','canned')
)
```

(`bcf.panel_output_record` has `model_identity_json NOT NULL` so the `IS NULL` branch is unreachable there; on `bcf.certification_record` the column is nullable and the `IS NULL` branch is required to admit pre-NF1 rows.)

This CHECK does NOT exist on the corresponding `contract.*` tables today. Implications:

1. **Phase A2 must validate source rows BEFORE migration.** Any `contract.*` row whose `model_identity_json -> 'maker' ->> 'provider'` is `synthetic` (or `replay`/`mock`/`canned`) would be rejected by `bcf.*` on INSERT. Phase A2 design must include an explicit pre-migration validation gate that counts such rows and either retires them via PR #133 apply or surfaces them to the operator. Current count: 1 (the smoke `21023aa1` cert that PR #133 will retire).
2. **Smoke retirement ordering becomes binding.** PR #133 apply MUST run before Phase A2. This is consistent with the parent DBCP §13 step 8 sequencing and parent D9.
3. **Writer-side compliance.** BCF authoring writers (the `RegistryAuthoringOrchestrator` and related code paths) must not emit `provider IN ('synthetic','replay','mock','canned')` for any row destined for `bcf.*` (post-Phase A3 cutover). Phase A3 will surface this requirement; the substrate CHECK is the backstop.

The CHECK is intentionally placed on the `model_identity_json` field rather than as a writer-side guard so it survives any future writer rewrite, library change, or direct DB intervention.

## 8. Relationship to existing `contract.*`

Phase A1 leaves the 4 existing `contract.*` evidence tables fully operational. During Phase A1 and through to Phase A3 cutover:

- BCF authoring writers continue to INSERT into `contract.panel_output_record` and friends. Phase A1 does NOT redirect any writer.
- The 9-FK closure on `contract.panel_output_record.panel_run_uid` is intact.
- The 3 framework_policy rows in `contract.framework_policy` continue to serve both BCF and MCF runtime policy probes (parent D7 deferred).
- The new `bcf.*` tables stay empty (zero rows in all 4) throughout Phase A1.
- No reader on `contract.*` is redirected.

In short: Phase A1 ADDS the new schema without REMOVING or REWIRING the existing one. The two clusters coexist for the duration of A1, A2 (data migration), and A3 (writer/reader flip). Phase A4 is the first phase that touches the `contract.*` evidence tables (freeze or retire).

## 9. Migration boundary to A2/A3/A4/A5

The "Phase A1 ships" line is crisp:

> Phase A1 has shipped IFF the new `bcf.*` schema exists with exactly 4 tables (`panel_output_record`, `authoring_panel_rejection_log`, `calibration_event`, `certification_record`), each at 0 rows, with the column shape, CHECK constraints, indexes, and intra-`bcf.*` FKs specified in §4 and §6.1; AND no `contract.*` row, column, constraint, or index has been altered; AND no `mcf.*` row, column, constraint, or index has been altered.

| Phase | Begins | Ends | Owned by |
|---|---|---|---|
| A1 (this DBCP) | When the Phase A1 apply gate is operator-authorized and executed | When the post-apply parity probe (§12.3) returns all-PASS | This DBCP for design; a separate "Phase A1 apply DBCP" for execution |
| A2 | After A1 ships AND PR #133 apply has retired the 11 smoke rows (per parent D9 sequencing) | When all 3,568 authority-bearing BCF rows have been INSERTed into `bcf.*` and parity probes pass | A separate Phase A2 design DBCP (not authored by this gate) |
| A3 | After A2 ships AND operator-authorized cutover window agreed | When BCF writers INSERT exclusively into `bcf.*` and BCF readers SELECT exclusively from `bcf.*` for a soak window (operator-defined; min 7 days) | A separate Phase A3 design DBCP |
| A4 | After A3 ships AND soak period passes | When the 4 `contract.*` evidence tables are either frozen (writes blocked) or DROPped | A separate Phase A4 design DBCP |
| A5 | After A4 ships | When `mcf.metric_authoring_panel_output_record` exists, the 5 `mcf.* → contract.*` FKs are redirected to `mcf.* → mcf.*`, M5 §5 1:1 composition rule is updated, and the M12 writer flips its INSERT target | A separate Phase A5 design DBCP |

Phase A1 does NOT pre-authorize any of A2..A5. Each is its own gate. Each requires its own design DBCP, operator authorization, apply gate, and closeout.

## 10. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Schema-shape drift between `bcf.*` and `contract.*` (one column type mismatch breaks Phase A2 INSERT...SELECT migration) | MEDIUM | HIGH | Pre-apply parity probe per column against `information_schema.columns` baseline pinned in §4; Phase A1 apply DBCP includes byte-by-byte column comparison |
| R2 | CHECK constraint not faithfully copied (enum drift, paired-null logic mis-spelled) | MEDIUM | HIGH | Pre-apply diff via `pg_get_constraintdef()` for every constraint; recorded as a sha256 fingerprint in the Phase A1 apply DBCP |
| R3 | Index parity gap (e.g. missing partial UNIQUE `uq_bcf_certification_record__registry_dedup`) causes silent BCF dedup failure after Phase A3 cutover | MEDIUM | MEDIUM | Pre-apply: index inventory diff against `contract.*` baseline; post-apply: re-list bcf.* indexes and assert 1:1 mapping |
| R4 | New `bcf_*_no_synthetic_provider_chk` CHECK rejects legitimate post-PR #133-apply BCF authority rows | LOW | HIGH | Pre-Phase-A2 probe: `SELECT count(*) FROM contract.panel_output_record WHERE (model_identity_json->'maker'->>'provider') IN ('synthetic','replay','mock','canned')` must equal 0 BEFORE Phase A2 runs; today 1 (smoke `21023aa1`); equals 0 after PR #133 apply |
| R5 | `gen_random_uuid()` default requires `pgcrypto` extension; absence breaks `CREATE TABLE` | LOW | LOW | Pre-apply: confirm `pgcrypto` present via `SELECT 1 FROM pg_extension WHERE extname = 'pgcrypto'` (already in use for `contract.*` so confirmed present) |
| R6 | `bcf` schema name collides with an existing schema in `bc_platform_dev` | LOW | LOW | Pre-apply: `SELECT count(*) FROM information_schema.schemata WHERE schema_name = 'bcf'` must equal 0; today 0 (parent DBCP §3.1 confirmed) |
| R7 | Single-transaction DDL apply fails part-way (e.g. transient connection failure) | LOW | MEDIUM | Phase A1 apply DBCP wraps the full CREATE SCHEMA + 4 CREATE TABLE + indexes + CHECKs + 3 FKs in one transaction; ROLLBACK on any error |
| R8 | Operator-readable error: future maintainer mistakes empty `bcf.*` for a legacy dead schema and DROPs it before A2 ships | LOW | MEDIUM | `COMMENT ON SCHEMA bcf` and `COMMENT ON TABLE bcf.<each>` documenting "A2-pending; do not drop"; cross-reference parent DBCP path in comment text |
| R9 | Phase A1 apply runs before PR #133 apply, leaving the synthetic-smoke row alive in `contract.*` and forcing it to migrate in A2 | LOW | LOW | Phase A1 apply does NOT migrate any row. The synthetic-smoke row stays in `contract.*` until PR #133 apply retires it. Phase A2 design (separate gate) is responsible for the smoke-retirement-before-migration ordering check |
| R10 | A future schema-shape change to `contract.*` (after A1 ships, before A2) breaks parity | MEDIUM | MEDIUM | Lock window: between Phase A1 apply and Phase A2 apply, ANY `contract.*` evidence-cluster schema change requires re-running the Phase A1 parity probe and amending the Phase A1 closeout |
| R11 | The new no-synthetic CHECK on `bcf.*` invents a substrate convention the operator hasn't approved | LOW | LOW | D5 below makes this an explicit operator decision; operator may choose to omit it and rely on writer-side enforcement of HR1 instead |
| R12 | `bcf.*` schema with empty tables drifts forever (Phase A2 never authorized; substrate is dead) | LOW | LOW | Phase A1 apply DBCP includes a rollback path (`DROP SCHEMA bcf CASCADE` safely removes the empty substrate). If A2 is not authorized within an operator-defined window, A1 can be reverted |

## 11. Operator decisions (D1..D11)

| # | Decision | Default proposal | Operator must confirm |
|---|---|---|---|
| **D1** | Accept Phase A1 substrate-only scope (no data migration, no FK redirect, no writer/reader flip, no `mcf.*` substrate change, no bc-core source edit, no PR #133 edit) | ACCEPT | Y / N |
| **D2** | Schema name = `bcf` (per parent DBCP terminology) | ACCEPT | Y / N |
| **D3** | Target tables = 4 (`panel_output_record`, `authoring_panel_rejection_log`, `calibration_event`, `certification_record`); 1:1 mirror of `contract.*` table names | ACCEPT | Y / N |
| **D4** | Column-shape strategy = 1:1 mirror of `contract.*` counterparts (name + type + nullability + default + position match exactly; §4) | ACCEPT | Y / N |
| **D5** | Add two NEW substrate-enforced HR1 CHECKs (`bcf_panel_output_record_no_synthetic_provider_chk` and `bcf_certification_record_no_synthetic_provider_chk`) not present in `contract.*` | ACCEPT (additive HR1 enforcement) — or REJECT if operator prefers writer-side enforcement only | A / R |
| **D6** | CHECK constraint strategy = mirror all 26 existing `contract.*` CHECKs with `bcf_` constraint name prefix, plus the two D5 additions | ACCEPT | Y / N |
| **D7** | Index strategy = mirror all 20 existing `contract.*` indexes with `bcf_` index name prefix; preserve partial-UNIQUE `uq_bcf_certification_record__registry_dedup` semantics | ACCEPT | Y / N |
| **D8** | FK strategy = 3 intra-`bcf.*` FKs declared at table creation (rejection_log / calibration_event / certification_record → panel_output_record, all ON DELETE RESTRICT); no cross-schema FK touched in A1 | ACCEPT | Y / N |
| **D9** | Confirm Phase A1 is DDL-design-only in this DBCP. No DDL is applied here. The Phase A1 apply DBCP is a SEPARATE follow-up gate | ACCEPT | Y / N |
| **D10** | Authorize a Phase A1 apply DBCP authoring next (the apply DBCP will include single-transaction CREATE SCHEMA + 4 CREATE TABLE + 20 CREATE INDEX + 26 CHECK + 3 FK + 2 new HR1 CHECK + `COMMENT ON SCHEMA bcf` + 4 `COMMENT ON TABLE`; with sha256-pinned DDL and post-apply parity probes per §12.3) | ACCEPT (authorize apply DBCP authoring) | Y / N |
| **D11** | Tenant DBs (`tbc_{slug}_dev`), legacy `metric.*`, `mcf.*` substrate, `contract.*` chain infrastructure, PR #133, M11/M12/M12.5/M13 invocation, M14 opening all remain OUT OF SCOPE for Phase A1 | ACCEPT | Y / N |

## 12. Test / evidence plan

### 12.1 Pre-apply probes (executed by the Phase A1 apply DBCP author before any DDL is synthesized)

Read-only `bc-postgres` MCP probes (`allow_write=false`):

1. Schema availability: `SELECT count(*) FROM information_schema.schemata WHERE schema_name = 'bcf'` → expect **0**.
2. Extension availability: `SELECT count(*) FROM pg_extension WHERE extname = 'pgcrypto'` → expect **1**.
3. Synthetic-row count on source — both `contract.panel_output_record` and `contract.certification_record` (the two `contract.*` tables that carry `model_identity_json` and that `bcf.*` substrate-enforces HR1 on per §4.2 + §4.5):
   ```sql
   SELECT 'contract.panel_output_record' AS table_name, count(*) AS n
     FROM contract.panel_output_record
     WHERE (model_identity_json->'maker'->>'provider')
           IN ('synthetic','replay','mock','canned')
   UNION ALL
   SELECT 'contract.certification_record', count(*)
     FROM contract.certification_record
     WHERE (model_identity_json->'maker'->>'provider')
           IN ('synthetic','replay','mock','canned')
   ```
   Both counts must equal **0** before Phase A2 runs. Today: `contract.panel_output_record` = **0**; `contract.certification_record` = **1** (the smoke `21023aa1` cert that PR #133 apply retires). After PR #133 apply, both equal 0.
4. `contract.*` evidence row counts (Phase A1 baseline): panel_output_record = 24; authoring_panel_rejection_log = 1; calibration_event = 23; certification_record = 3531.
5. `mcf.*` row count: 0 across all 17 tables.
6. Column-shape inventory of all 4 `contract.*` evidence tables (this DBCP §4 is the pinned baseline).
7. CHECK constraint inventory of all 4 `contract.*` evidence tables (pinned; see Appendix-equivalent §4 sub-sections).
8. Index inventory of all 4 `contract.*` evidence tables (pinned; see §4 sub-sections).
9. FK inventory inbound to `contract.panel_output_record` (9 FKs, pinned in §3 + parent DBCP §3.7).

### 12.2 Apply (separate Phase A1 apply DBCP)

Not authored here. The apply DBCP will:

- Synthesize the DDL as one transaction (CREATE SCHEMA bcf → 4 CREATE TABLE → 20 CREATE INDEX → 26 mirrored CHECKs + 2 HR1 CHECKs → 3 intra-`bcf.*` FKs → COMMENTs).
- Compute a sha256 fingerprint of the planned DDL and pin it for replay parity.
- Wrap apply in a single transaction; ROLLBACK on any error.

### 12.3 Post-apply parity probes (executed by the Phase A1 apply DBCP closeout)

All probes are read-only:

1. `SELECT count(*) FROM bcf.<each>` → 0 for all 4 tables.
2. Column-by-column diff between `bcf.*` and `contract.*` counterparts via `information_schema.columns`: column_name + data_type + is_nullable + column_default + ordinal_position must match exactly (modulo the schema prefix).
3. CHECK constraint diff via `pg_get_constraintdef()`: for each `contract.*` CHECK there must exist a `bcf.*` CHECK with byte-equivalent clause text (constraint name differs by `bcf_` prefix). Plus 2 additional `bcf_*_no_synthetic_provider_chk` CHECKs present.
4. Index diff via `pg_indexes`: 20 `bcf.*` indexes correspond 1:1 to 20 `contract.*` indexes by definition (modulo schema/name prefix); partial-UNIQUE `uq_bcf_certification_record__registry_dedup` present with `governance_scope = 'registry'` predicate.
5. FK diff: 3 intra-`bcf.*` FKs present, each ON DELETE RESTRICT, each targeting `bcf.panel_output_record(panel_run_uid)`. 0 `bcf.* → contract.*` cross-schema FKs.
6. `COMMENT ON SCHEMA bcf` present and non-empty.
7. `COMMENT ON TABLE bcf.<each>` present and non-empty for all 4 tables.
8. `contract.*` evidence row counts unchanged (24 / 1 / 23 / 3531).
9. `mcf.*` row counts unchanged (0 across all 17 tables).
10. 9 inbound FKs on `contract.panel_output_record` unchanged.

A single failed probe blocks Phase A1 closeout. The Phase A1 apply gate ROLLBACK option remains live until all 10 probes return PASS.

## 13. Rollback plan

### 13.1 Mid-apply rollback (during the future Phase A1 apply gate)

Single-transaction wrap. Any error during `CREATE SCHEMA bcf … COMMIT` triggers automatic transaction ROLLBACK. No partial state persists. No `contract.*` change because Phase A1 does not modify `contract.*`. No `mcf.*` change.

### 13.2 Post-apply rollback (after Phase A1 ships but before Phase A2 begins)

If Phase A2 design is not authorized within the operator-defined window (or if Phase A1 substrate proves wrong for a reason discovered between apply and A2), the entire `bcf.*` schema can be removed with:

```sql
DROP SCHEMA bcf CASCADE;
```

Safety: `bcf.*` tables are empty by design throughout Phase A1; no row is lost. The 3 intra-`bcf.*` FKs are dropped by CASCADE. No cross-schema FK targets `bcf.*` (parent DBCP forbids this), so no `contract.*` or `mcf.*` constraint is affected.

The rollback is operator-authorized; it is NOT executed by Phase A1 closeout automatically.

### 13.3 Documentation rollback

`git revert <commit>` on the Phase A1 DBCP commit (this file) removes the planning artifact. Purely additive; no other file affected by this commit.

### 13.4 What rollback does NOT touch

- `contract.*` evidence tables and their rows
- `contract.framework_policy` rows
- `mcf.*` substrate
- `metric.*` legacy schema
- Any tenant `tbc_{slug}_dev` database
- PR #133 (untouched by this DBCP and untouched by rollback)
- bc-core source

## 14. Explicit non-scope statement (repeated for clarity)

This DBCP is **NOT** the Phase A1 apply gate. That is a separately authorized follow-up DBCP that will include the synthesized DDL, sha256 fingerprint, single-transaction wrapper, and the §12.3 parity probe execution.

This DBCP is **NOT** Phase A2, A3, A4, or A5. Row migration, writer/reader flip, `contract.*` retire/freeze, and MCF FK reconsideration are each their own gate.

This DBCP is **NOT** the policy/governance placement gate for `contract.framework_policy` (parent D7 deferred).

This DBCP does **NOT** authorize PR #133 apply. Parent D9 keeps it paused until Phase A1 + A2 designs are both accepted.

This DBCP does **NOT** authorize any bc-core source edit.

This DBCP does **NOT** touch tenant DBs. Substrate-enforced via separate connections (`DATABASE_URL` vs `TENANT_DATABASE_URL`).

This DBCP does **NOT** alter `mcf.*`, `metric.*`, `contract.framework_policy`, or any `contract.*` chain table.

This DBCP does **NOT** open M14.

## 15. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 |
| No DDL applied | ✓ |
| No DML applied | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| `bc-postgres` MCP `allow_write=false` throughout (column / CHECK / index / FK shape probes only) | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No tenant `tbc_{slug}_dev` DB connection opened | ✓ |
| PR #133 not modified | ✓ |
| No-synthetic hard rule respected (this DBCP designs the substrate enforcement; does not retire existing synthetic) | ✓ |

## 16. Sequencing recommendation

Under the parent DBCP's authorized Option A path, the gate ladder is:

1. **This DBCP (Phase A1 design)** → operator reviews §11 D1..D11.
2. **Operator authorization of D1..D11** in writing.
3. **Phase A1 apply DBCP authored** — synthesizes the DDL, computes sha256, includes §12 probes.
4. **Phase A1 apply gate executed** — single transaction; post-apply parity probes (§12.3); closeout doc.
5. **Phase A2 DBCP authored** — design for 3,568-row authority-bearing migration; explicitly excludes the synthetic-smoke debt.
6. **PR #133 apply gate executed** — retires the 11 smoke rows from `contract.*` (per parent D9 sequencing; must run BEFORE Phase A2).
7. **Phase A2 apply gate executed** — 3,568-row INSERT...SELECT into `bcf.*`; parity probes; closeout.
8. **Phase A3 DBCP + apply** — BCF writer/reader cutover.
9. **Phase A4 DBCP + apply** — freeze or retire `contract.*` evidence tables.
10. **Phase A5 DBCP + apply** — `mcf.metric_authoring_panel_output_record` creation; 5 mcf→contract FKs redirected to mcf→mcf; M5 §5 1:1 composition rule updated; M12 writer flipped.
11. **M12 first-real-panel-run DBCP** — separately authored; M12 writer now targets `mcf.metric_authoring_panel_output_record`.
12. **M12 first real panel run** — operator-authorized.
13. **M12.5 first materialization** — operator-authorized.
14. **M13 first evaluation** — operator-authorized.
15. **M14 opening** — after M13 first evaluation closes.

Phase A1 is step 4 in this ladder. Phase A1 design (this DBCP) is step 1. Everything below step 4 is downstream of Phase A1 and not authorized by Phase A1's planning gate.

---

**End of DBCP. NOT EXECUTED. Operator authorization on §11 D1..D11 required before the Phase A1 apply DBCP is authored.**
