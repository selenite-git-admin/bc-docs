---
uid: metric-context-framework-m3-certification-target-amendment-dbcp
title: MCF M3 — Certification-Target Amendment DBCP
description: Database Change Protocol design for the MCF M3 amendment that redirects MCF's certification target from the BCF-shared contract.certification_record to a new per-framework mcf.certification_record sibling table, per the 7 accepted D-Correction operator decisions on the certification substrate correction preflight (637e667). Specifies the exact mcf.certification_record table schema (25 columns, 9 CHECK constraints, 5 indexes, 1 cross-schema FK to contract.panel_output_record), the M3 trigger function ALTER (CREATE OR REPLACE FUNCTION redirecting only the cert FROM clause in fn_mcv_state_transition_check), the mcf.metric_supersession.fk_mcs_cert FK DROP/ADD redirect (safe — 0 existing rows), 3 additive shared CHECK extensions (framework_policy.scope_code += 'mcf'; operator_confirm_rule.scope += 'mcf'; operator_confirm_rule.transition += 'active_to_superseded'; operator_confirm_rule.action_code unchanged per D-Correction-4), Drizzle impact (1 new schema file + 3 file updates), single-file DDL apply order (13 steps), forward-only discipline (no rollback per D-Correction-3 — M3 substrate live + dormant + 0 cert writes attempted), companion rollback DDL for emergency-only use, 8-precondition dry-run + 15-check post-apply verifier (with positive + negative behavioral exercises through the amended trigger), 10 operator approvals required before implementation PR opens. M3 substrate stays applied throughout the amendment (CREATE OR REPLACE FUNCTION + ALTER TABLE DROP/ADD CONSTRAINT + CREATE TABLE new sibling — no DROP/RECREATE). M4 implementation remains BLOCKED until this amendment ships and the M4 DBCP is rewritten around mcf.certification_record. Doc-only design; no DDL applied; no bc-core schema edited; no MCF metric contracts created; no certification rows written.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m3-cert-amendment
---

# MCF M3 — Certification-Target Amendment DBCP

## 1. Scope and grounding

### 1.1 Purpose

The Database Change Protocol design for the MCF M3 amendment that resolves the certification-substrate mismatch identified by the correction preflight (`bc-docs-v3 637e667`). M3 substrate is live; 7 of the 7 D-Correction operator decisions have been accepted; the amendment redirects MCF's certification target from BCF-shared `contract.certification_record` to a new per-framework `mcf.certification_record` sibling table, with small additive CHECK extensions on the shared `framework_policy` + `operator_confirm_rule` tables.

This DBCP is **docs-only**. No DDL is applied. No bc-core source files are edited. No MCF metric contracts are created. No certification rows are written. This document is the spec that an operator-authorized M3 amendment implementation PR will later commit to bc-core, and that a subsequent Database Change Protocol session will later apply to `bc_platform_dev`.

### 1.2 Relationship to prior gates

| Gate | Role | Commit / status |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority | `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (locked) |
| MCF M3 DBCP | Original substrate design; §3.12 D-12 "REUSE" reversed by this amendment | `3147bd4 + 938fb0f` |
| M3 implementation PR #103 | Substrate code merged | `1a9796d` |
| M3 DDL apply | Substrate live; 7 mcf.* tables; 7 triggers; 0 rows | bc-core `a6a3e64` + bc-docs-v3 `mcf-m3-ddl-apply-closeout.md` (`d1f67d0`) |
| M3 evidence PR #104 | Audit artifacts merged | `a6a3e64` |
| MCF M4 DBCP (patched) | Cert-reuse design; §3.19 D-19 reversed by this amendment via the correction preflight | `e56fc7e` |
| Cert substrate correction preflight | Discovery + option set + 7 accepted D-Correction decisions | `637e667` |
| **This amendment DBCP** | The substrate fix specifying mcf.certification_record + trigger + FK + shared CHECK extensions | this document |

### 1.3 What this DBCP is and is not

| | This DBCP |
|---|---|
| Is | The complete column-level + constraint-level + index-level + trigger-body specification for the M3 amendment |
| Is | The Drizzle impact spec, DDL apply sequence, verifier design, and risk assessment |
| Is | The formal resolution of the 7 D-Correction decisions accepted from the correction preflight |
| Is not | An M3 substrate rollback — substrate stays applied throughout (per D-Correction-3) |
| Is not | An M4 DBCP rewrite — that's a subsequent gate after this amendment lands (per D-Correction-2) |
| Is not | A bc-core implementation — implementation PR is the next gate |
| Is not | A DDL apply — separate operator-authorized DCP session |
| Is not | A reorganization of contract.metric_contract* or any legacy MC table |
| Is not | A BCF-arc design — coordination with BCF arc is light-touch per D-Correction-7; additive shared CHECK extensions are BCF-neutral |

### 1.4 Source documents consumed

| Source | Role | Commit / location |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority; lifecycle states; cert reuse principle | `ADR-c3e57f.md` |
| MCF M3 DBCP §3.12 D-12 + §6.3 + §5.3 | The D-12 reversal target; the live trigger body to ALTER; the live FK to redirect | `metric-context-framework-m3-lifecycle-substrate-dbcp.md` (`3147bd4 + 938fb0f`) |
| MCF M3 apply closeout | M3 substrate live state | `mcf-m3-ddl-apply-closeout.md` (`d1f67d0`) |
| MCF M4 DBCP §3.19 D-19 + §9 + §10 | The D-19 reversal target (downstream — M4 DBCP rewrite is a separate gate) | `metric-context-framework-m4-lifecycle-certification-dbcp.md` (`e56fc7e`) |
| Cert substrate correction preflight | The 7 D-Correction decisions accepted by operator | `metric-context-framework-m3-m4-cert-substrate-correction-preflight.md` (`637e667`) |
| Live `contract.certification_record` Drizzle schema | Sibling-table column shape reference (mcf.certification_record mirrors essential columns, drops 2) | `bc-core/src/database/schema/contract/certification-record.ts` |
| Live `contract.framework_policy` Drizzle schema | CHECK to extend additively | `bc-core/src/database/schema/contract/framework-policy.ts` |
| Live `contract.operator_confirm_rule` Drizzle schema | 2 CHECKs to extend additively | `bc-core/src/database/schema/contract/operator-confirm-rule.ts` |
| M3 lifecycle DDL | The exact trigger function body to ALTER + the exact FK constraint to redirect | `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` |

### 1.5 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — read-only this session |
| No DDL applied or drafted in bc-core | ✓ — design-only |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No certification rows written | ✓ — substrate stays empty |
| No legacy MC migration or reorganization | ✓ |
| No M4 DBCP edits this gate | ✓ — D-Correction-2 keeps M4 rewrite separate |
| No BCF data touched | ✓ |
| No M3 substrate rollback | ✓ per D-Correction-3 |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |
| M4 implementation remains blocked | ✓ — until (1) this amendment DDL applies + verifies AND (2) M4 DBCP is rewritten around `mcf.certification_record` |

### 1.6 Patch history (post-review)

| Patch | Finding | Where patched | Resolution |
|---|---|---|---|
| P-Amendment-1 | M-1 partial-apply risk on shared `contract.*` CHECK ALTERs | §9.1, new §9.4 | DDL wrapped in `BEGIN; ... COMMIT;` so a mid-flight failure rolls back the entire amendment atomically. `ON_ERROR_STOP=1` is no longer presented as sufficient by itself. |
| P-Amendment-2 | L-6 whole-file atomicity not explicitly enumerated as a risk | §13.1 new R-13 | New risk + mitigation pointing at the transaction wrapper |
| P-Amendment-3 | L-1 `mcf_cert_nf1_all_or_none_chk` 6-field divergence from BCF's 7-field NF1 undocumented | §4.3 | Explanatory note added — MCF requires `policy_version` for every cert (NOT NULL); BCF allowed legacy rows to have NULL `policy_version` |
| P-Amendment-4 | L-2 §8 text-vs-table mismatch | §8 | Wording corrected to "1 new file + 4 updates" |
| P-Amendment-5 | L-3 §12 check #6 substring inspection brittle | §12.1 | Tightened to exact occurrence counts (1 occurrence of new FROM, 0 of old FROM) |
| P-Amendment-6 | L-5 §11.1 check #8 missing explicit total | §11.1 | Explicit minimum total = 17 statements stated |
| P-Amendment-7 | L-4 §10 rollback preconditions are comments only | §10.1 | Preamble extended to enforced `DO $$ ... RAISE EXCEPTION ... END $$;` guard blocks for emergency rollback safety |
| P-Amendment-8 | L-7 §15.3 evidence-PR file list missing closeout doc | §15.3 | Closeout doc + audit artifacts file list added |

No substantive design changes in this patch round. All 7 D-Correction operator decisions preserved verbatim. Option C, sibling cert table, M3 trigger target redirect, supersession FK redirect, 3-and-only-3 shared CHECK extensions, `operator_confirm_rule.action_code` unchanged, no M3 rollback — all preserved.

---

## 2. Accepted correction decisions (D-Correction-1..D-Correction-7)

Operator decisions accepted per the correction preflight (`637e667`); this amendment implements them verbatim.

| # | Decision | Operator answer | This DBCP realizes |
|---:|---|---|---|
| D-Correction-1 | Option A (extend shared cert) vs B (full sibling) vs C (hybrid) | **C — hybrid** | New `mcf.certification_record` sibling (per Option C cert sibling); shared framework_policy + operator_confirm_rule extended additively (per Option C shared grammar) |
| D-Correction-2 | Combine M3 amendment DBCP + M4 DBCP rewrite into one doc, or keep separate | **Separate** | This DBCP covers only the M3 amendment; M4 DBCP rewrite is the next-next gate |
| D-Correction-3 | M3 rollback vs forward amendment | **Forward only; no rollback** | DDL uses `CREATE OR REPLACE FUNCTION` + `ALTER TABLE DROP/ADD CONSTRAINT` + `CREATE TABLE`; M3 substrate stays applied; companion rollback DDL is emergency-only |
| D-Correction-4 | Shared CHECK extension scope | **Extend only**: `framework_policy.scope_code` + `operator_confirm_rule.scope` + `operator_confirm_rule.transition`. **Do NOT change** `operator_confirm_rule.action_code` | DDL ships 3 CHECK ALTERs; `operator_confirm_rule.action_code` enum stays at 3 enforcement-action values (per its correct semantics) |
| D-Correction-5 | `mcf.certification_record` ownership boundary | **M3 amendment ships it** | This DBCP defines the table; the M3 amendment implementation PR ships the CREATE TABLE + Drizzle schema; the M3 trigger ALTER points at it |
| D-Correction-6 | M4 DBCP rewrite later fixes operator_confirm_rule.action_code semantic misuse | **Yes** | Out of scope for this DBCP; M4 DBCP rewrite (next-next gate) will correct §10 misuse |
| D-Correction-7 | BCF arc coordination for shared CHECK extensions | **Light-touch noted; additive extensions accepted** | This DBCP proceeds; BCF arc maintainer notified by operator (or operator wears both hats); no BCF DBCP required for additive enum extensions that don't break any existing BCF row |

---

## 3. Current live M3 substrate state and rollback non-requirement

### 3.1 Live state (per M3 apply closeout `d1f67d0`)

| Asset | State |
|---|---|
| `mcf` schema | present in `bc_platform_dev` |
| `mcf.metric_contract` (17 cols, 0 rows) | identity-bearing parent |
| `mcf.metric_contract_version` (15 cols, 0 rows) | descriptive body + lifecycle column |
| `mcf.metric_variable_binding` (13 cols, 0 rows) | child |
| `mcf.metric_filter_clause` (9 cols, 0 rows) | child |
| `mcf.metric_computed_dimension_ref` (9 cols, 0 rows) | child |
| `mcf.metric_contract_revision` (9 cols, 0 rows) | M3-shipped audit |
| `mcf.metric_supersession` (11 cols, 0 rows) | M3-shipped; **FK fk_mcs_cert currently REFERENCES `contract.certification_record(certification_record_id)`** |
| 7 trigger functions in `mcf` schema | all live |
| 7 triggers attached on mcf.* tables | all live |
| `mcf.fn_mcv_state_transition_check()` | live function; **cert-lookup section queries `FROM contract.certification_record`** (lines 113-127 of `05-mcf-lifecycle-substrate.sql`) — this is what this amendment ALTERs |

### 3.2 Why rollback is not required

Per D-Correction-3:

1. **No M3 substrate row writes have ever occurred.** All 7 mcf tables verifiably contain 0 rows. The M3 trigger's cert lookup at `→ active` has never executed against real data because no service exists to write certs.
2. **Forward amendment touches no committed data.** The amendment changes:
   - The trigger function body (idempotent ALTER via `CREATE OR REPLACE FUNCTION`)
   - One FK constraint target on a table with 0 rows (safe DROP/ADD CONSTRAINT)
   - Three CHECK enums via additive ALTER (every existing row in `contract.framework_policy` + `contract.operator_confirm_rule` satisfies the extended enum because the extension is a strict superset)
   - Adds one new table (`mcf.certification_record`) that doesn't yet exist
3. **DROP/RECREATE would be operationally worse.** Rolling back M3 means DROP 7 triggers + DROP 7 functions + DROP 2 M3 tables, then re-apply with amended definitions. More substrate churn, more apply gates, more risk windows. Forward amendment is strictly less work for strictly less risk.

### 3.3 Companion rollback DDL is shipped, but for emergency-only use

A `05a-mcf-cert-amendment-rollback.sql` companion ships (per §10) as documentation of the reverse path. It is **not the recommended cleanup path** under normal operation. If post-apply verification reveals a problem, the standard response is forward-fix (a follow-up amendment), not rollback to the pre-amendment shape.

---

## 4. `mcf.certification_record` table design

### 4.1 Purpose

Per MCF M3 D-12 reversed (per D-Correction-1 Option C): MCF certification rows live in their own per-framework sibling table, isolated from BCF's `contract.certification_record` row-shape constraints. The sibling carries only MCF-shape rows; CHECK enums are tight to MCF semantics; row-shape complexity that BCF Phase A had to introduce (legacy XOR Registry) is not inherited.

### 4.2 Column specification (25 columns)

The sibling mirrors `contract.certification_record` for shared audit columns + drops 2 BCF-specific columns (`governance_scope`, `target_registry_id`) that aren't needed in a per-framework cert table.

| # | Column | Type | Constraints | Notes |
|---:|---|---|---|---|
| 1 | `certification_record_id` | uuid | NOT NULL PRIMARY KEY DEFAULT `gen_random_uuid()` | Stable identifier |
| 2 | `primitive_type` | text | NOT NULL CHECK (`= 'metric_contract_version'`) | Single-value enum — no other type writes here |
| 3 | `primitive_id` | uuid | NOT NULL | The MCV uid the cert authorizes (action target) |
| 4 | `action_code` | text | NOT NULL CHECK (3-element enum) | `metric_create` / `metric_transition` / `metric_supersede` |
| 5 | `from_state_code` | text | NULL allowed; CHECK couples to action_code via §4.3 | `NULL` for metric_create; `'approved'` for metric_transition; `'active'` for metric_supersede |
| 6 | `to_state_code` | text | NOT NULL; CHECK couples to action_code via §4.3 | `'draft'` for metric_create; `'active'` for metric_transition; `'superseded'` for metric_supersede |
| 7 | `is_archived_after` | boolean | NULL allowed | `NULL` = cert is active authority; non-NULL would indicate archival |
| 8 | `gate_results_json` | jsonb | NOT NULL DEFAULT `'{}'::jsonb` | PE-MC-1..PE-MC-10 panel results summary; full per-PE-MC detail lives in `mcf.metric_publication_eligibility_result` (M4-shipped) |
| 9 | `advisory_verdicts_json` | jsonb | NOT NULL DEFAULT `'[]'::jsonb` | Panel-emitted non-blocking advisories |
| 10 | `override_gate_code` | text | NULL allowed; CHECK couples with the override triplet via §4.3 | Operator override target gate code; only set for emergency activations / supersessions that bypass a REJECT verdict |
| 11 | `override_rationale_text` | text | NULL allowed; CHECK requires `char_length >= 40` when set | Operator override rationale |
| 12 | `override_followup_task_uid` | text | NULL allowed | Operator follow-up task UID (DevHub TSK-* or similar) |
| 13 | `certifier_sub` | text | NOT NULL | Cognito sub of certifier (panel-actor sub for panel-driven; operator JWT sub for operator-confirmed) |
| 14 | `certifier_role_at_action` | text | NOT NULL CHECK (3-element enum) | `'panel'` / `'operator'` / `'system'` |
| 15 | `certifier_email` | text | NULL allowed | Optional certifier email (PII; nullable; service may populate from JWT context) |
| 16 | `supersedes_primitive_id` | uuid | NULL allowed; CHECK couples to action_code via §4.3 | Set only when `action_code = 'metric_supersede'`; references the predecessor MCV uid |
| 17 | `created_at` | timestamptz | NOT NULL DEFAULT `now()` | |
| 18 | `panel_run_uid` | uuid | NULL allowed; FK to `contract.panel_output_record(panel_run_uid)` ON DELETE RESTRICT | Panel run this cert references (NULL for operator-initiated re-certs / direct supersessions) |
| 19 | `prompt_version` | text | NULL allowed | From panel context |
| 20 | `model_identity_json` | jsonb | NULL allowed | Three-model identity per panel run |
| 21 | `input_hash` | text | NULL allowed | Panel workbench fingerprint |
| 22 | `policy_version` | text | NOT NULL | Active `mcf` framework_policy version this cert binds to (e.g. `'1.0.0'`); service-layer validates against an ACTIVE framework_policy row at write time (M4 service responsibility, not this DBCP) |
| 23 | `sampling_status` | text | NULL allowed; CHECK 3-element enum | From panel sampling decision |
| 24 | `grounding_check_result` | text | NULL allowed; CHECK 2-element enum | PE-MC-1 no-fabrication outcome (`'pass'` / `'quarantined'`) |
| 25 | `subject_kind` | text | NOT NULL CHECK (3-element enum) | `'metric_contract_version'` / `'metric_publication'` / `'metric_supersession'` (corresponds to action_code by §4.3) |

**Dropped from contract.certification_record:**
- `governance_scope` — single-table (always implicitly `'mcf'`); no need to store
- `target_registry_id` — BCF Registry Model A specific; not applicable to MCF

### 4.3 CHECK constraints (9 total)

| # | Name | Definition |
|---|---|---|
| 1 | `mcf_cert_primitive_type_chk` | `CHECK (primitive_type = 'metric_contract_version')` — single-value enum |
| 2 | `mcf_cert_action_code_chk` | `CHECK (action_code IN ('metric_create', 'metric_transition', 'metric_supersede'))` |
| 3 | `mcf_cert_subject_kind_chk` | `CHECK (subject_kind IN ('metric_contract_version', 'metric_publication', 'metric_supersession'))` |
| 4 | `mcf_cert_certifier_role_chk` | `CHECK (certifier_role_at_action IN ('panel', 'operator', 'system'))` |
| 5 | `mcf_cert_sampling_chk` | `CHECK (sampling_status IS NULL OR sampling_status IN ('not_sampled','sampled_for_calibration','sample_routed_to_operator'))` — mirror of BCF cert |
| 6 | `mcf_cert_grounding_chk` | `CHECK (grounding_check_result IS NULL OR grounding_check_result IN ('pass','quarantined'))` — mirror of BCF cert |
| 7 | `mcf_cert_state_transition_chk` | Couples action_code to from/to state pair:<br>`CHECK ((action_code = 'metric_create' AND from_state_code IS NULL AND to_state_code = 'draft') OR (action_code = 'metric_transition' AND from_state_code = 'approved' AND to_state_code = 'active') OR (action_code = 'metric_supersede' AND from_state_code = 'active' AND to_state_code = 'superseded'))` |
| 8 | `mcf_cert_supersedes_chk` | `CHECK ((action_code = 'metric_supersede' AND supersedes_primitive_id IS NOT NULL) OR (action_code <> 'metric_supersede' AND supersedes_primitive_id IS NULL))` — supersedes set IFF supersession action |
| 9 | `mcf_cert_override_chk` | Same all-or-nothing pattern as BCF cert: `CHECK ((override_gate_code IS NULL AND override_rationale_text IS NULL AND override_followup_task_uid IS NULL) OR (override_gate_code IS NOT NULL AND char_length(override_rationale_text) >= 40 AND override_followup_task_uid IS NOT NULL))` |

**Optional 10th CHECK (recommended but operator-decidable):** `mcf_cert_nf1_all_or_none_chk` mirroring BCF's NF1 invariant but with **6 panel-attestation fields** (panel_run_uid, prompt_version, model_identity_json, input_hash, sampling_status, grounding_check_result) rather than BCF's 7. Recommendation: ship this CHECK; it matches BCF's discipline pattern and prevents partial NF1 population that would weaken audit. Operator confirms in **O-Amendment-2** below.

**Why 6 fields and not BCF's 7 (deliberate divergence — P-Amendment-3):** BCF's `certification_record_nf1_all_or_none_chk` includes `policy_version` as the 7th field because legacy pre-Phase-A BCF rows could have NULL `policy_version`. In MCF, `policy_version` is `NOT NULL` for every cert (per §4.2 row 22 — every M4 cert binds to an active `mcf` framework_policy version). Therefore `policy_version` is outside the NF1 all-or-none bundle in MCF: it is required independently. The 6 panel-attestation fields remain all-or-none per BCF discipline (operator-direct certs set all 6 to NULL; panel-driven certs set all 6 non-NULL).

### 4.4 FK constraint (1 total)

| Name | Definition | ON DELETE |
|---|---|---|
| `fk_mcf_cert_panel_run` | `panel_run_uid → contract.panel_output_record(panel_run_uid)` | `RESTRICT` |

This is a cross-schema FK (mcf → contract). Drizzle modeling follows the same DDL-only pattern as `mcf.metric_supersession.fk_mcs_cert` — Drizzle declares the column as plain `uuid`, the FK lives only in DDL.

### 4.5 Indexes (5 total)

| # | Name | Type | Definition | Purpose |
|---|---|---|---|---|
| 1 | `idx_mcf_cert_lookup` | non-unique | `(primitive_id, action_code, created_at DESC)` | **Critical**: supports the M3 state-transition trigger's `SELECT EXISTS` lookup at `→ active` — `WHERE primitive_id = ? AND action_code = 'metric_transition' AND ...` |
| 2 | `idx_mcf_cert_certifier` | non-unique | `(certifier_sub, created_at DESC)` | Audit query: "all certs by this operator" |
| 3 | `idx_mcf_cert_action_at` | non-unique | `(action_code, created_at DESC)` | Audit query: "all metric_transition certs in last 30 days" |
| 4 | `idx_mcf_cert_panel_run` | partial | `(panel_run_uid) WHERE panel_run_uid IS NOT NULL` | Audit query: "what cert came out of this panel run?" |
| 5 | `idx_mcf_cert_supersedes` | partial | `(supersedes_primitive_id) WHERE supersedes_primitive_id IS NOT NULL` | Audit query: "what cert superseded this MCV?" |

### 4.6 COMMENT annotations

| Target | Content (summary) |
|---|---|
| `mcf.certification_record` (TABLE) | "Per-framework MCF certification ledger (sibling to contract.certification_record per M3 amendment / D-Correction-1 Option C). One row per MCF authority-bearing act: metric_create at intake, metric_transition at approved→active, metric_supersede at active→superseded. Append-only by service convention. Columns mirror contract.certification_record minus governance_scope (single-table) and target_registry_id (BCF Registry-specific). CHECK constraints are tight to MCF semantics — no row-shape XOR complexity. Cross-schema FK to contract.panel_output_record(panel_run_uid) lives in DDL only (Drizzle column is plain uuid)." |
| `mcf.certification_record.primitive_type` (COLUMN) | "Single-value enum: 'metric_contract_version'. CHECK constraint enforces. No other primitive type writes to this table." |
| `mcf.certification_record.action_code` (COLUMN) | "3-element MCF enum: 'metric_create' / 'metric_transition' / 'metric_supersede'. Coupled to from/to state pairs via mcf_cert_state_transition_chk." |
| `mcf.certification_record.subject_kind` (COLUMN) | "3-element MCF enum: 'metric_contract_version' (for metric_create) / 'metric_publication' (for metric_transition) / 'metric_supersession' (for metric_supersede)." |
| `mcf.certification_record.supersedes_primitive_id` (COLUMN) | "Predecessor MCV uid. Required when action_code='metric_supersede'; rejected otherwise per mcf_cert_supersedes_chk. Poly-ref (no DB-level FK); service-layer enforces lookup against mcf.metric_contract_version." |
| `mcf.certification_record.panel_run_uid` (COLUMN) | "Panel run this cert references. Nullable for operator-initiated certs. FK to contract.panel_output_record(panel_run_uid) lives in DDL; Drizzle column is plain uuid." |
| `mcf.certification_record.policy_version` (COLUMN) | "Active mcf framework_policy version this cert binds to. Service-layer validates against contract.framework_policy WHERE scope_code='mcf' AND (effective_to IS NULL OR effective_to > now()) — see M4 DBCP §6.8 (post-rewrite)." |
| `mcf.certification_record.is_archived_after` (COLUMN) | "Cert archival flag. NULL = active authority cert. The M3 state-transition trigger reads this via WHERE clause `is_archived_after IS NOT TRUE` (NULL treated as 'not archived')." |

Approximate enumerated comment count: 2 COMMENT ON TABLE (one for the sibling + one for the existing M3 metric_supersession to reflect FK redirect) + 7 COMMENT ON COLUMN. Minimum for the verifier's count check.

---

## 5. M3 trigger amendment

### 5.1 What changes

Only the cert-lookup section of `mcf.fn_mcv_state_transition_check()` changes. All other branches (INSERT validation, forward-only state graph, hash NOT-NULL gate at `→ approved`, supersession check at `→ superseded`, `is_current` discipline) are unchanged.

### 5.2 Trigger function body (full ALTER via CREATE OR REPLACE FUNCTION)

The amendment ships the full `CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check() RETURNS TRIGGER AS $$ ... $$ LANGUAGE plpgsql;` — Postgres idempotent ALTER pattern. The body is identical to the live function (per `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` lines 65-164) **except for one single change** in the cert-lookup section:

```sql
-- approved → active: matching cert must exist (with primitive_type guard)
IF NEW.governance_state_code = 'active' THEN
  SELECT EXISTS (
    SELECT 1 FROM mcf.certification_record cr   -- CHANGED: was contract.certification_record
    WHERE cr.primitive_type  = 'metric_contract_version'
      AND cr.primitive_id    = NEW.metric_contract_version_uid
      AND cr.action_code     = 'metric_transition'
      AND cr.from_state_code = 'approved'
      AND cr.to_state_code   = 'active'
      AND (cr.is_archived_after IS NOT TRUE)
  ) INTO has_active_cert;

  IF NOT has_active_cert THEN
    RAISE EXCEPTION 'mcf state transition to active requires a metric_transition cert (primitive_type=metric_contract_version) for version %', NEW.metric_contract_version_uid
      USING ERRCODE = 'check_violation';
  END IF;

  -- is_current discipline (unchanged)
  UPDATE mcf.metric_contract_version
    SET is_current = FALSE
    WHERE metric_contract_uid = OLD.metric_contract_uid
      AND metric_contract_version_uid <> OLD.metric_contract_version_uid
      AND is_current = TRUE;
  NEW.is_current := TRUE;
END IF;
```

All other branches preserved verbatim:
- INSERT path forcing `'draft'` start
- Forward-only state graph
- `review → approved` hash NOT-NULL check on parent
- `active → superseded` supersession-row + active-successor check (joins `mcf.metric_supersession`, not the cert table directly)

### 5.3 Why CREATE OR REPLACE FUNCTION is safe

- The trigger function exists in pg_proc; replacing it preserves the trigger attachment (no DROP TRIGGER + CREATE TRIGGER cycle).
- The trigger function body is queried only when the trigger fires; the live trigger fires on `BEFORE INSERT OR UPDATE OF governance_state_code` on `mcf.metric_contract_version`. The table has 0 rows; no inflight fires can be interrupted.
- The ALTER is atomic — Postgres holds an exclusive lock on the function during replace; concurrent fires would block briefly but the substrate has no fires.

### 5.4 Verifier validation

The post-apply verifier (§12 check #6) confirms the function body now references `mcf.certification_record` and not `contract.certification_record` via `pg_get_functiondef('mcf.fn_mcv_state_transition_check'::regproc::oid)` text inspection.

---

## 6. Supersession FK amendment

### 6.1 What changes

The FK on `mcf.metric_supersession.certification_record_id` currently references `contract.certification_record(certification_record_id)`. The amendment redirects it to `mcf.certification_record(certification_record_id)`.

### 6.2 ALTER DDL

```sql
-- DROP existing FK (safe: 0 rows in mcf.metric_supersession; no FK validation needed)
ALTER TABLE mcf.metric_supersession
  DROP CONSTRAINT fk_mcs_cert;

-- ADD redirected FK
ALTER TABLE mcf.metric_supersession
  ADD CONSTRAINT fk_mcs_cert
    FOREIGN KEY (certification_record_id)
    REFERENCES mcf.certification_record(certification_record_id)
    ON DELETE RESTRICT;
```

### 6.3 Safety

- `mcf.metric_supersession` has 0 rows (verified at M3 apply closeout; verified again at M4 implementation pre-read).
- The new FK target `mcf.certification_record` is created earlier in the same DDL apply (per §9 step 1), so the target exists before the FK ADD.
- No data migration needed because no existing cert references in `contract.certification_record` are valid MCF references (the M3 supersession FK was structurally a dangling pointer — it could reference a cert id but the cert table wouldn't accept MCF-shape rows in the first place, so no real reference has ever been written).

### 6.4 Verifier validation

The post-apply verifier (§12 check #5) confirms `mcf.metric_supersession.fk_mcs_cert` now references `mcf.certification_record` via `pg_constraint` query joining on `confrelid` to resolve the referenced table.

---

## 7. Shared policy/rule CHECK amendments

Per D-Correction-4: extend exactly three CHECKs additively. `operator_confirm_rule.action_code` CHECK is NOT changed (its 3-element enum is correctly typed; the M4 DBCP §10 misuse is a documentation bug to fix in the M4 rewrite).

### 7.1 `framework_policy.scope_code` extension

**Current** (live in bc_platform_dev):

```sql
CHECK (scope_code IN ('bf_bo','cf','mapping','all','registry'))
```

**Amendment:**

```sql
ALTER TABLE contract.framework_policy
  DROP CONSTRAINT framework_policy_scope_code_chk;

ALTER TABLE contract.framework_policy
  ADD CONSTRAINT framework_policy_scope_code_chk
    CHECK (scope_code IN ('bf_bo','cf','mapping','all','registry','mcf'));
```

**Safety:** Additive — every existing row has `scope_code` in the original 5-element subset, which is a strict subset of the new 6-element enum. Validation succeeds for all existing rows.

### 7.2 `operator_confirm_rule.scope` extension

**Current:**

```sql
CHECK (scope IN ('bf','bo','cf','mapping','any','registry'))
```

**Amendment:**

```sql
ALTER TABLE contract.operator_confirm_rule
  DROP CONSTRAINT operator_confirm_rule_scope_chk;

ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_scope_chk
    CHECK (scope IN ('bf','bo','cf','mapping','any','registry','mcf'));
```

**Safety:** Additive.

### 7.3 `operator_confirm_rule.transition` extension

**Current:**

```sql
CHECK (transition IN ('intake_to_draft','draft_to_review','review_to_approved','approved_to_active','any'))
```

**Amendment:**

```sql
ALTER TABLE contract.operator_confirm_rule
  DROP CONSTRAINT operator_confirm_rule_transition_chk;

ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_transition_chk
    CHECK (transition IN ('intake_to_draft','draft_to_review','review_to_approved','approved_to_active','active_to_superseded','any'));
```

**Safety:** Additive. The new value `'active_to_superseded'` is generic enough to serve any future framework with a supersession path — not MCF-specific.

### 7.4 `operator_confirm_rule.action_code` — NOT CHANGED

Per D-Correction-4: the existing CHECK `action_code IN ('require_operator_confirm','route_to_operator_review','block')` is the correct enforcement-action enum for the operator_confirm_rule's purpose. The M4 DBCP §10 mis-populated this column with cert action codes (`'metric_transition'`, `'metric_supersede'`); that's a documentation bug to fix in the M4 DBCP rewrite (per D-Correction-6), not a substrate gap.

This DBCP **does not touch** `operator_confirm_rule_action_chk`. The post-apply verifier (§12 check #10) confirms this CHECK is unchanged (regression check).

---

## 8. Drizzle impact

**Scope: 1 new file + 4 updates** (corrected per P-Amendment-4).

### 8.1 New file

| File | Purpose | Approximate lines |
|---|---|---|
| `bc-core/src/database/schema/mcf/certification-record.ts` | Drizzle pgTable for `mcf.certification_record`; 25 columns + 9 CHECKs (or 10 with NF1 if O-Amendment-2 accepts) + 5 indexes; cross-schema FK to `contract.panel_output_record` in DDL only (Drizzle column is plain uuid) | ~120 |

### 8.2 Updated files (4 total)

| File | Change |
|---|---|
| `bc-core/src/database/schema/mcf/index.ts` | Add `export { certificationRecord } from './certification-record';` |
| `bc-core/src/database/schema/mcf/metric-supersession.ts` | Update the existing cross-schema FK comment (currently: "Cross-schema FKs are DDL-only"). Add note that fk_mcs_cert now targets `mcf.certification_record` per M3 amendment. Drizzle column for certificationRecordId stays `.notNull()` plain uuid (DDL-only FK pattern preserved). |
| `bc-core/src/database/schema/contract/framework-policy.ts` | Update `framework_policy_scope_code_chk` CHECK to include `'mcf'` |
| `bc-core/src/database/schema/contract/operator-confirm-rule.ts` | Update `operator_confirm_rule_scope_chk` CHECK to include `'mcf'`; update `operator_confirm_rule_transition_chk` CHECK to include `'active_to_superseded'`. **DO NOT** change `operator_confirm_rule_action_chk`. |

### 8.3 Drizzle CHECK mirror discipline

Drizzle declares CHECK constraints as text expressions inside `check('name', sql\`...\`)`. The mirrors in `framework-policy.ts` + `operator-confirm-rule.ts` must match the live DDL exactly post-amendment. The post-apply verifier (§12 check #7-#9) reads the live constraint definitions via `pg_get_constraintdef` and asserts they include the new values.

### 8.4 No other Drizzle changes

- `mcf/metric-contract.ts` — unchanged
- `mcf/metric-contract-version.ts` — unchanged
- `mcf/metric-variable-binding.ts` — unchanged
- `mcf/metric-filter-clause.ts` — unchanged
- `mcf/metric-computed-dimension-ref.ts` — unchanged
- `mcf/metric-contract-revision.ts` — unchanged
- `mcf/pg-schema.ts` — unchanged (`mcfSchema` export already exists)
- All other contract/* and metric/* schemas — unchanged

---

## 9. DDL apply sequence

### 9.1 Single-file DDL

The amendment ships as `bc-core/docker/redesign/05a-mcf-cert-amendment.sql` (numeric suffix `05a` keeps it sequenced after `05-mcf-lifecycle-substrate.sql` without renumbering). The **entire file is wrapped in `BEGIN; ... COMMIT;`** so all 8 statement-groups commit atomically or roll back atomically (per P-Amendment-1 + §9.4 atomicity discipline). `ON_ERROR_STOP=1` is also required at apply time but is **not sufficient by itself** for whole-file atomicity — see §9.4 for the rationale. Statement order:

```sql
-- ============================================================================
-- MCF M3 Certification-Target Amendment — bc_platform_dev
-- (per cert substrate correction preflight 637e667; D-Correction-1..D-Correction-7 ACCEPTED)
--
-- Forward amendment to M3: introduces mcf.certification_record sibling table;
-- redirects mcf.fn_mcv_state_transition_check() cert lookup; redirects
-- mcf.metric_supersession.fk_mcs_cert FK; extends 3 shared CHECK enums.
-- M3 substrate stays applied throughout.
--
-- Whole-file transaction wrapper (P-Amendment-1): every statement below must
-- commit together or roll back together. The amendment touches BCF-shared
-- contract.framework_policy + contract.operator_confirm_rule CHECK constraints;
-- a partial apply (e.g. DROP succeeds, ADD fails) would leave shared substrate
-- in a worse state than pre-amendment. The transaction wrapper prevents that.
-- See §9.4.
-- ============================================================================

BEGIN;

-- Step 1: CREATE TABLE mcf.certification_record (25 cols, 9-10 CHECKs)
CREATE TABLE mcf.certification_record (
  certification_record_id uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  primitive_type text NOT NULL,
  primitive_id uuid NOT NULL,
  action_code text NOT NULL,
  from_state_code text,
  to_state_code text NOT NULL,
  is_archived_after boolean,
  gate_results_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  advisory_verdicts_json jsonb NOT NULL DEFAULT '[]'::jsonb,
  override_gate_code text,
  override_rationale_text text,
  override_followup_task_uid text,
  certifier_sub text NOT NULL,
  certifier_role_at_action text NOT NULL,
  certifier_email text,
  supersedes_primitive_id uuid,
  created_at timestamptz NOT NULL DEFAULT now(),
  panel_run_uid uuid,
  prompt_version text,
  model_identity_json jsonb,
  input_hash text,
  policy_version text NOT NULL,
  sampling_status text,
  grounding_check_result text,
  subject_kind text NOT NULL,
  CONSTRAINT mcf_cert_primitive_type_chk
    CHECK (primitive_type = 'metric_contract_version'),
  CONSTRAINT mcf_cert_action_code_chk
    CHECK (action_code IN ('metric_create','metric_transition','metric_supersede')),
  CONSTRAINT mcf_cert_subject_kind_chk
    CHECK (subject_kind IN ('metric_contract_version','metric_publication','metric_supersession')),
  CONSTRAINT mcf_cert_certifier_role_chk
    CHECK (certifier_role_at_action IN ('panel','operator','system')),
  CONSTRAINT mcf_cert_sampling_chk
    CHECK (sampling_status IS NULL OR sampling_status IN ('not_sampled','sampled_for_calibration','sample_routed_to_operator')),
  CONSTRAINT mcf_cert_grounding_chk
    CHECK (grounding_check_result IS NULL OR grounding_check_result IN ('pass','quarantined')),
  CONSTRAINT mcf_cert_state_transition_chk
    CHECK (
      (action_code = 'metric_create'      AND from_state_code IS NULL AND to_state_code = 'draft') OR
      (action_code = 'metric_transition'  AND from_state_code = 'approved' AND to_state_code = 'active') OR
      (action_code = 'metric_supersede'   AND from_state_code = 'active'   AND to_state_code = 'superseded')
    ),
  CONSTRAINT mcf_cert_supersedes_chk
    CHECK (
      (action_code = 'metric_supersede' AND supersedes_primitive_id IS NOT NULL) OR
      (action_code <> 'metric_supersede' AND supersedes_primitive_id IS NULL)
    ),
  CONSTRAINT mcf_cert_override_chk
    CHECK (
      (override_gate_code IS NULL AND override_rationale_text IS NULL AND override_followup_task_uid IS NULL) OR
      (override_gate_code IS NOT NULL AND char_length(override_rationale_text) >= 40 AND override_followup_task_uid IS NOT NULL)
    ),
  -- Optional 10th CHECK per O-Amendment-2 recommendation: NF1 all-or-nothing
  CONSTRAINT mcf_cert_nf1_all_or_none_chk
    CHECK (
      (panel_run_uid IS NULL AND prompt_version IS NULL AND model_identity_json IS NULL
       AND input_hash IS NULL AND sampling_status IS NULL AND grounding_check_result IS NULL)
      OR
      (panel_run_uid IS NOT NULL AND prompt_version IS NOT NULL AND model_identity_json IS NOT NULL
       AND input_hash IS NOT NULL AND sampling_status IS NOT NULL AND grounding_check_result IS NOT NULL)
    ),
  CONSTRAINT fk_mcf_cert_panel_run
    FOREIGN KEY (panel_run_uid)
    REFERENCES contract.panel_output_record(panel_run_uid)
    ON DELETE RESTRICT
);

-- Step 2: Indexes on mcf.certification_record (5 indexes)
CREATE INDEX idx_mcf_cert_lookup
  ON mcf.certification_record (primitive_id, action_code, created_at DESC);
CREATE INDEX idx_mcf_cert_certifier
  ON mcf.certification_record (certifier_sub, created_at DESC);
CREATE INDEX idx_mcf_cert_action_at
  ON mcf.certification_record (action_code, created_at DESC);
CREATE INDEX idx_mcf_cert_panel_run
  ON mcf.certification_record (panel_run_uid)
  WHERE panel_run_uid IS NOT NULL;
CREATE INDEX idx_mcf_cert_supersedes
  ON mcf.certification_record (supersedes_primitive_id)
  WHERE supersedes_primitive_id IS NOT NULL;

-- Step 3: Redirect M3 trigger function (CREATE OR REPLACE FUNCTION; idempotent)
-- The body is identical to the live function (05-mcf-lifecycle-substrate.sql lines 65-164)
-- EXCEPT the FROM clause in the cert-lookup section changes from
-- 'contract.certification_record' to 'mcf.certification_record'.
CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check()
RETURNS TRIGGER AS $$
DECLARE
  parent_mc record;
  has_active_cert boolean;
  successor_state text;
  successor_is_current boolean;
BEGIN
  -- [INSERT validation, forward-only state graph, hash check at →approved
  --  — IDENTICAL to live function body, omitted from this design sketch for brevity;
  --  implementation PR ships the full function body verbatim]
  -- ...
  IF NEW.governance_state_code = 'active' THEN
    SELECT EXISTS (
      SELECT 1 FROM mcf.certification_record cr   -- ← THE ONLY CHANGE
      WHERE cr.primitive_type  = 'metric_contract_version'
        AND cr.primitive_id    = NEW.metric_contract_version_uid
        AND cr.action_code     = 'metric_transition'
        AND cr.from_state_code = 'approved'
        AND cr.to_state_code   = 'active'
        AND (cr.is_archived_after IS NOT TRUE)
    ) INTO has_active_cert;
    -- [error raise + is_current discipline — IDENTICAL to live function]
    -- ...
  END IF;
  -- [active → superseded check — IDENTICAL to live function]
  -- ...
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Step 4: Redirect mcf.metric_supersession.fk_mcs_cert FK target
ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_cert;
ALTER TABLE mcf.metric_supersession
  ADD CONSTRAINT fk_mcs_cert
    FOREIGN KEY (certification_record_id)
    REFERENCES mcf.certification_record(certification_record_id)
    ON DELETE RESTRICT;

-- Step 5: Extend contract.framework_policy.scope_code CHECK (additive)
ALTER TABLE contract.framework_policy DROP CONSTRAINT framework_policy_scope_code_chk;
ALTER TABLE contract.framework_policy
  ADD CONSTRAINT framework_policy_scope_code_chk
    CHECK (scope_code IN ('bf_bo','cf','mapping','all','registry','mcf'));

-- Step 6: Extend contract.operator_confirm_rule.scope CHECK (additive)
ALTER TABLE contract.operator_confirm_rule DROP CONSTRAINT operator_confirm_rule_scope_chk;
ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_scope_chk
    CHECK (scope IN ('bf','bo','cf','mapping','any','registry','mcf'));

-- Step 7: Extend contract.operator_confirm_rule.transition CHECK (additive)
ALTER TABLE contract.operator_confirm_rule DROP CONSTRAINT operator_confirm_rule_transition_chk;
ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_transition_chk
    CHECK (transition IN ('intake_to_draft','draft_to_review','review_to_approved','approved_to_active','active_to_superseded','any'));

-- Step 8: COMMENT ON TABLE / ON COLUMN annotations
COMMENT ON TABLE mcf.certification_record IS
  'Per-framework MCF certification ledger (sibling to contract.certification_record per M3 amendment / D-Correction-1 Option C). One row per MCF authority-bearing act: metric_create at intake, metric_transition at approved→active, metric_supersede at active→superseded. Append-only by service convention.';
COMMENT ON TABLE mcf.metric_supersession IS
  'Predecessor → successor edges per MCF requirements §10.5 + ADR DEC-c3e57f (D422). Per M3 amendment (DEC-pending / cert substrate correction): certification_record_id FK target redirected from contract.certification_record to mcf.certification_record. correction_class_code: editorial | meaning_bearing.';
-- [COMMENT ON COLUMN statements per §4.6 — full enumeration in implementation PR]

COMMIT;

-- ============================================================================
-- End of M3 cert-amendment DDL. Whole file wrapped in BEGIN/COMMIT per §9.4
-- atomicity discipline (P-Amendment-1).
-- ============================================================================
```

### 9.2 Why this order

1. **Table before indexes** — indexes reference their owning table
2. **Table before FK redirect** — the new FK target must exist before the ALTER ADD CONSTRAINT
3. **Trigger ALTER before FK redirect** — the trigger and FK both reference `mcf.certification_record`; either order would work since neither writes any row at apply time, but trigger-first follows the dependency-resolution discipline of M3's original DDL
4. **Shared CHECK extensions after MCF substrate** — keeps "MCF substrate first, then cross-framework infrastructure" ordering consistent with M2 + M3
5. **COMMENTs last** — documentation; no functional dependency

### 9.3 Idempotency at the DDL layer

- `CREATE TABLE mcf.certification_record` — not idempotent; re-apply against an already-applied DB errors on duplicate. Dry-run precondition #2 confirms absence before apply.
- `CREATE INDEX` — not idempotent for these (no `IF NOT EXISTS` for safety against accidental name collisions); dry-run confirms.
- `CREATE OR REPLACE FUNCTION` — idempotent.
- `ALTER TABLE ... DROP CONSTRAINT` — not idempotent (fails if constraint absent); dry-run confirms constraint is present.
- `ALTER TABLE ... ADD CONSTRAINT` — not idempotent (fails if constraint with same name already exists).
- `COMMENT ON ...` — idempotent (re-COMMENT replaces).

### 9.4 Apply atomicity discipline (per P-Amendment-1)

**The amendment DDL MUST be wrapped in `BEGIN; ... COMMIT;`.** This is non-negotiable for this amendment because it touches BCF-shared `contract.*` CHECK constraints.

#### 9.4.1 Why `ON_ERROR_STOP=1` alone is not sufficient

`psql -v ON_ERROR_STOP=1` causes psql to exit on the first statement error. It does NOT, by itself, prevent earlier statements from committing. With Postgres default autocommit (one statement = one transaction), the apply sequence behaves as follows without an explicit transaction wrapper:

1. Step 1 (`CREATE TABLE mcf.certification_record`) — commits independently
2. Step 2 (`CREATE INDEX` × 5) — each commits independently
3. Step 3 (`CREATE OR REPLACE FUNCTION`) — commits independently
4. Step 4 (`ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_cert`) — commits independently
5. Step 4 (`ALTER TABLE mcf.metric_supersession ADD CONSTRAINT fk_mcs_cert ...`) — independent

If step 4 ADD fails (e.g., a typo in the new constraint definition slipped through review), `mcf.metric_supersession` is left **with no FK on `certification_record_id`**. Re-running the apply would error on step 1 (table already exists), forcing a manual cleanup before retry.

Worse, for the shared `contract.*` CHECK extensions (steps 5/6/7):

- Step 5 DROP succeeds → `contract.framework_policy` loses its `scope_code` CHECK
- Step 5 ADD fails (e.g., typo) → table is left **without the CHECK** — BCF behavior is now silently looser than designed

A BCF row violating the original CHECK could then be INSERTed undetected, corrupting BCF substrate. This is the production-risk concern that motivated P-Amendment-1.

#### 9.4.2 What `BEGIN; ... COMMIT;` guarantees

With the entire file wrapped in one transaction:

- All 8 statement-groups commit together at `COMMIT;` or roll back together at any in-flight `ERROR`
- Postgres holds the necessary locks across the whole transaction (briefly)
- Concurrent readers see the pre-amendment state until `COMMIT;`; then see the post-amendment state
- A failure at any step leaves the substrate exactly as it was pre-apply — no partial-state corruption

The amendment is small enough that whole-file atomicity is cheap: ~8 statement-groups; no long-running data migration; no large index builds (the new indexes are on an empty table).

#### 9.4.3 What this DOES NOT guarantee

- **DDL drift from prior runs:** if the script is partially applied by a previous attempt that wasn't transaction-wrapped (or via a different process), the dry-run preconditions (§11.1) catch that and abort before re-apply. Dry-run is the safety net for pre-apply state.
- **Replication slot issues:** Postgres replication lag during a long transaction can affect downstream replicas. Not applicable to `bc_platform_dev` (single-instance).
- **Concurrent DDL deadlocks:** any other DDL session executing concurrently against `contract.framework_policy` or `contract.operator_confirm_rule` could deadlock with this transaction. Apply discipline: no other DDL sessions during M3 amendment apply (per CLAUDE.md Database Change Protocol — one operator-authorized DCP at a time).

#### 9.4.4 Operator note

The transaction wrapper is a forward fix; it is not retrofitted to M2 or M3 original DDL apply gates. Those gates were forward-creates only (no ALTERs to pre-existing shared tables) and the M2 + M3 apply succeeded cleanly. Future MCF amendments that touch shared `contract.*` tables should adopt the same `BEGIN; ... COMMIT;` discipline.

---

## 10. Rollback story (emergency-only per D-Correction-3)

Per D-Correction-3, **forward amendment is the recommended discipline**. A rollback DDL is shipped as `bc-core/docker/redesign/05a-mcf-cert-amendment-rollback.sql` for emergency use only. Standard remediation for any post-apply issue is a follow-up forward fix.

### 10.1 Rollback DDL

```sql
-- Reverse order from §9.1. Wrapped in BEGIN/COMMIT for atomicity (mirrors §9.4).
--
-- Pre-conditions ENFORCED via DO/RAISE EXCEPTION guards (P-Amendment-7):
--   - mcf.certification_record has 0 rows (no MCF certs written since amendment)
--   - mcf.metric_supersession has 0 rows (no MCF supersessions since amendment)
--   - No framework_policy row exists with scope_code='mcf'
--   - No operator_confirm_rule row exists with scope='mcf'
-- The guard block aborts the transaction with a clear error if any precondition
-- fails. Operator must clear MCF state before rollback or accept the amendment.

BEGIN;

-- Step 0: ENFORCED pre-condition guards (rollback aborts if any condition fails)
DO $$
DECLARE
  cert_count integer;
  supersession_count integer;
  mcf_policy_count integer;
  mcf_rule_count integer;
BEGIN
  SELECT COUNT(*) INTO cert_count FROM mcf.certification_record;
  IF cert_count > 0 THEN
    RAISE EXCEPTION 'rollback aborted: mcf.certification_record has % row(s); clear MCF certs before rollback', cert_count;
  END IF;

  SELECT COUNT(*) INTO supersession_count FROM mcf.metric_supersession;
  IF supersession_count > 0 THEN
    RAISE EXCEPTION 'rollback aborted: mcf.metric_supersession has % row(s); clear before rollback', supersession_count;
  END IF;

  SELECT COUNT(*) INTO mcf_policy_count
    FROM contract.framework_policy WHERE scope_code = 'mcf';
  IF mcf_policy_count > 0 THEN
    RAISE EXCEPTION 'rollback aborted: contract.framework_policy has % row(s) with scope_code=mcf; clear before rollback', mcf_policy_count;
  END IF;

  SELECT COUNT(*) INTO mcf_rule_count
    FROM contract.operator_confirm_rule WHERE scope = 'mcf';
  IF mcf_rule_count > 0 THEN
    RAISE EXCEPTION 'rollback aborted: contract.operator_confirm_rule has % row(s) with scope=mcf; clear before rollback', mcf_rule_count;
  END IF;
END $$;

-- Step 1: Revert COMMENTs to pre-amendment text
COMMENT ON TABLE mcf.metric_supersession IS
  'Predecessor → successor edges per MCF requirements §10.5 + ADR DEC-c3e57f (D422).';
-- (mcf.certification_record COMMENT will drop with the table)

-- Step 2: Revert operator_confirm_rule.transition CHECK
ALTER TABLE contract.operator_confirm_rule DROP CONSTRAINT operator_confirm_rule_transition_chk;
ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_transition_chk
    CHECK (transition IN ('intake_to_draft','draft_to_review','review_to_approved','approved_to_active','any'));

-- Step 3: Revert operator_confirm_rule.scope CHECK
ALTER TABLE contract.operator_confirm_rule DROP CONSTRAINT operator_confirm_rule_scope_chk;
ALTER TABLE contract.operator_confirm_rule
  ADD CONSTRAINT operator_confirm_rule_scope_chk
    CHECK (scope IN ('bf','bo','cf','mapping','any','registry'));

-- Step 4: Revert framework_policy.scope_code CHECK
ALTER TABLE contract.framework_policy DROP CONSTRAINT framework_policy_scope_code_chk;
ALTER TABLE contract.framework_policy
  ADD CONSTRAINT framework_policy_scope_code_chk
    CHECK (scope_code IN ('bf_bo','cf','mapping','all','registry'));

-- Step 5: Revert mcf.metric_supersession.fk_mcs_cert FK target
ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_cert;
ALTER TABLE mcf.metric_supersession
  ADD CONSTRAINT fk_mcs_cert
    FOREIGN KEY (certification_record_id)
    REFERENCES contract.certification_record(certification_record_id)
    ON DELETE RESTRICT;

-- Step 6: Restore original M3 trigger function body
-- (Implementation PR captures the pre-amendment function definition and ships it here verbatim)
CREATE OR REPLACE FUNCTION mcf.fn_mcv_state_transition_check()
RETURNS TRIGGER AS $$
DECLARE
  parent_mc record;
  has_active_cert boolean;
  successor_state text;
  successor_is_current boolean;
BEGIN
  -- [Pre-amendment body — FROM clause reverted to contract.certification_record]
  -- ...
END;
$$ LANGUAGE plpgsql;

-- Step 7: DROP the new sibling table (indexes drop with it)
DROP TABLE IF EXISTS mcf.certification_record;

COMMIT;
```

### 10.2 Rollback safety guards

The rollback DDL **enforces** each pre-condition via the `DO $$ ... RAISE EXCEPTION ... END $$;` guard block at Step 0 (per P-Amendment-7). If any row exists in MCF cert/supersession or any MCF policy/rule has been seeded, the guard block raises `EXCEPTION` and the entire transaction rolls back — no rollback statements execute. The operator sees a clear error naming which precondition failed and the row count. Per CLAUDE.md Database Change Protocol, rollback execution is itself a substrate-change session requiring explicit operator approval.

The guard pattern is the deliberate alternative to comment-only preconditions (which a careless operator could ignore). Code-enforced preconditions cannot be bypassed at execution time.

---

## 11. Dry-run verifier requirements

### 11.1 Script: `scripts/mcf-m3-cert-amendment-dry-run.mjs`

Mirrors M3 dry-run pattern. ~8 preconditions:

| # | Check | Pass criterion |
|---:|---|---|
| 1 | M2 + M3 substrate present (7 mcf.* tables; 7 triggers attached; 7 trigger functions) | YES |
| 2 | `mcf.certification_record` ABSENT (clean slate for amendment apply) | YES |
| 3 | `mcf.metric_supersession.fk_mcs_cert` currently references `contract.certification_record` (pre-amendment state) | YES |
| 4 | `mcf.fn_mcv_state_transition_check()` function body currently references `FROM contract.certification_record` (pre-amendment state, via `pg_get_functiondef` text inspection) | YES |
| 5 | `contract.framework_policy_scope_code_chk` does NOT include `'mcf'` (pre-amendment) | YES |
| 6 | `contract.operator_confirm_rule_scope_chk` does NOT include `'mcf'` (pre-amendment) | YES |
| 7 | `contract.operator_confirm_rule_transition_chk` does NOT include `'active_to_superseded'` (pre-amendment) | YES |
| 8 | DDL file parses; statement counts match expected — **minimum total: 17 statements** (1 CREATE TABLE + 5 CREATE INDEX + 1 CREATE OR REPLACE FUNCTION + 2 ALTER ... DROP/ADD CONSTRAINT for FK + 6 ALTER ... DROP/ADD CONSTRAINT for 3 CHECKs + ≥2 COMMENT); PLUS the BEGIN; / COMMIT; transaction-wrapper pair per §9.4. DDL sha256 captured. | YES |

The dry-run also captures the **pre-amendment function definition** (via `pg_get_functiondef`) to a snapshot artifact, so the rollback DDL's Step 6 has the verbatim body to restore.

### 11.2 Output artifacts

- `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.summary.md`
- `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.precondition.jsonl`
- `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.planned-sql.sha256.txt`
- `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.pre-amendment-trigger-body.sql` (snapshot for rollback)

---

## 12. Post-apply verifier requirements

### 12.1 Script: `scripts/mcf-m3-cert-amendment-post-apply-verification.mjs`

15 checks (mirror M3 verifier pattern).

**Structural (1–10):**

| # | Check | Pass criterion |
|---:|---|---|
| 1 | `mcf.certification_record` table present with 25 columns | YES |
| 2 | 10 CHECK constraints on `mcf.certification_record` (or 9 if O-Amendment-2 declined NF1) | YES |
| 3 | 5 indexes on `mcf.certification_record` (idx_mcf_cert_lookup, idx_mcf_cert_certifier, idx_mcf_cert_action_at, idx_mcf_cert_panel_run, idx_mcf_cert_supersedes) | YES |
| 4 | FK `fk_mcf_cert_panel_run` present → `contract.panel_output_record(panel_run_uid)` | YES |
| 5 | `mcf.metric_supersession.fk_mcs_cert` now references `mcf.certification_record` (NOT `contract.certification_record`) — via pg_constraint join on confrelid | YES |
| 6 | `mcf.fn_mcv_state_transition_check()` body now references `mcf.certification_record`. Via `pg_get_functiondef` text inspection: **exactly 1 occurrence** of the literal `FROM mcf.certification_record` AND **exactly 0 occurrences** of the literal `FROM contract.certification_record`. The exact-count assertion (per P-Amendment-5) is tighter than substring-only inspection — it detects any unexpected second reference (e.g. a forgotten test artifact or a comment-string referencing the old target). | YES |
| 7 | `contract.framework_policy_scope_code_chk` now admits `'mcf'` (via pg_get_constraintdef text inspection) | YES |
| 8 | `contract.operator_confirm_rule_scope_chk` now admits `'mcf'` | YES |
| 9 | `contract.operator_confirm_rule_transition_chk` now admits `'active_to_superseded'` | YES |
| 10 | `contract.operator_confirm_rule_action_chk` UNCHANGED — still the 3-element enum (regression check per D-Correction-4) | YES |

**Behavioral (11–14) — synthetic-row exercises wrapped in BEGIN/ROLLBACK:**

| # | Check | Pass criterion |
|---:|---|---|
| 11 | INSERT into `mcf.certification_record` with valid metric_create row succeeds (positive) | YES |
| 12 | INSERT with invalid action_code (`'random_value'`) rejected by `mcf_cert_action_code_chk` (negative) | YES |
| 13 | End-to-end positive: synthetic mcv at `'approved'` + matching metric_transition cert INSERTed in `mcf.certification_record` → UPDATE mcv state to `'active'` SUCCEEDS (proves the amended trigger reads the sibling) | YES |
| 14 | End-to-end negative: synthetic mcv at `'approved'` + NO matching cert → UPDATE mcv state to `'active'` REJECTED with "mcf state transition to active requires a metric_transition cert" (proves the amended trigger still enforces) | YES |

**Cleanup (15):**

| # | Check | Pass criterion |
|---:|---|---|
| 15 | All 7 mcf.* M2/M3 tables + `mcf.certification_record` empty after verifier (test rows wrapped in BEGIN/ROLLBACK) | YES |

### 12.2 Why behavioral check #13 + #14 are critical

The structural checks (#1-#10) prove the substrate shape is correct. The behavioral checks (#13-#14) prove the M3 trigger's cert lookup **actually finds rows in the sibling table** (#13) and **actually rejects when none exists** (#14). These are the load-bearing assertions for the entire correction: did the trigger ALTER work end-to-end? Without them, a typo in the function body's FROM clause would pass #1-#10 but break the substrate's behavior.

### 12.3 Output artifacts

- `scripts/audit-output/mcf-m3-cert-amendment-post-apply-{ts}.summary.md`
- `scripts/audit-output/mcf-m3-cert-amendment-post-apply-{ts}.evidence.jsonl`

---

## 13. Risks and mitigations

| # | Risk | Severity | Mitigation |
|---:|---|---|---|
| R-1 | Trigger function ALTER mid-flight failure leaves substrate inconsistent | Low | `psql -v ON_ERROR_STOP=1` aborts on first error; partial state is impossible inside a single `CREATE OR REPLACE FUNCTION` statement (it's atomic) |
| R-2 | Shared CHECK extension breaks existing BCF rows | Very low | Additive extensions — every existing value is in the extended enum. Pre-flight rejection impossible. |
| R-3 | FK redirect leaves dangling references | Impossible | `mcf.metric_supersession` has 0 rows; no FK validation work needed |
| R-4 | New `mcf.certification_record.fk_mcf_cert_panel_run` FK to `contract.panel_output_record` fails because panel_output_record doesn't exist | Impossible | `contract.panel_output_record` is BCF-shipped + live; verified in the Drizzle import path in `bc-core/src/database/schema/contract/certification-record.ts` |
| R-5 | BCF arc coordination delay holds up the amendment | Low | Per D-Correction-7, additive extensions are BCF-neutral and accepted as light-touch; no separate BCF DBCP gate required |
| R-6 | Drizzle CHECK mirror in `framework-policy.ts` + `operator-confirm-rule.ts` falls out of sync with live DDL | Medium | Verifier check #7-#9 reads `pg_get_constraintdef` text and asserts the live CHECK admits the new values; deviation = test failure. Implementation PR includes integration test that round-trips an `'mcf'`-scope INSERT |
| R-7 | Behavioral verifier check #13 setup is non-trivial (needs synthetic mcv with all 6 hash columns populated) | Low | Mirrors M3 post-apply verifier check #11; same setup helper pattern; `MockMcfHashComputer`-equivalent fixture values used (no actual hash algorithm needed for this verifier; just non-NULL values that satisfy the M3 trigger's hash NOT-NULL gate) |
| R-8 | Behavioral verifier check #14 might pass by accident if the trigger throws for unrelated reasons | Low | Verifier asserts the specific error message text contains "requires a metric_transition cert" to distinguish |
| R-9 | M3 trigger function body has 100+ lines; ALTER must preserve all branches verbatim except the one FROM clause | Medium | Implementation PR diffs the new function body against the live function (via `pg_get_functiondef` capture in the dry-run) line-by-line; only one line should differ (the FROM clause); any other diff is a typo and aborts the PR |
| R-10 | Rollback DDL Step 6 needs the verbatim pre-amendment function body | Low | Dry-run script captures the live function definition to `pre-amendment-trigger-body.sql` artifact; rollback PR includes the captured body |
| R-11 | Operator approvals enumerated in §14 turn out to require BCF arc sign-off the operator did not anticipate | Low | D-Correction-7 explicit "light-touch" stance; operator may proceed unilaterally; if BCF arc later objects, the additive extensions can be reversed (they don't gate any BCF behavior) |
| R-12 | The optional 10th CHECK (mcf_cert_nf1_all_or_none_chk) creates friction for operator-direct certs that legitimately have no panel context | Low | Operator-direct certs set all 6 NF1 fields to NULL (panel_run_uid, prompt_version, model_identity_json, input_hash, sampling_status, grounding_check_result); the all-NULL branch satisfies the CHECK. `policy_version` is outside the NF1 bundle (always NOT NULL) — see §4.3 P-Amendment-3 note. Tested in unit test for the M4 service rewrite (later gate) |
| **R-13** | **Whole-file atomicity / partial-apply risk on BCF-shared CHECK ALTERs (per P-Amendment-2).** The amendment ships 6 `ALTER TABLE ... DROP/ADD CONSTRAINT` statements against `contract.framework_policy` + `contract.operator_confirm_rule`. Without an explicit transaction wrapper, a mid-flight failure (e.g. typo in a new CHECK expression, transient lock contention) would leave Postgres in autocommit mode with one DROP succeeded and its matching ADD failed — BCF-shared substrate left without the CHECK. `ON_ERROR_STOP=1` alone does not prevent this. | Medium | DDL wrapped in `BEGIN; ... COMMIT;` per §9.4 (P-Amendment-1). Whole-file rollback on any in-flight error. Post-apply verifier (§12 checks #7-#10) confirms all CHECK extensions present + the unchanged `operator_confirm_rule_action_chk` regression-asserted. Emergency rollback DDL (§10) is itself transaction-wrapped + `DO $$ ... RAISE EXCEPTION ... END $$;`-guarded (P-Amendment-7); used only if the transaction wrapper itself fails unexpectedly (e.g. database crash mid-COMMIT). |

### 13.1 Stop conditions

The M3 amendment implementation PR (next gate) STOPS and re-frames if:

- Dry-run reveals `mcf.fn_mcv_state_transition_check()` body differs from the design's expected pre-amendment body (would mean M3 was patched out-of-band)
- Dry-run reveals `mcf.metric_supersession` has rows (would mean MCF authoring happened despite the substrate being dormant — investigate before applying)
- The optional NF1 CHECK turns out to conflict with intended operator-direct cert shape (operator override per O-Amendment-2)

---

## 14. Operator approvals required before implementation PR

Before the M3 amendment implementation PR is opened, the operator approves:

| # | Approval item |
|---:|---|
| O-Amendment-1 | Confirm `mcf.certification_record` 25-column shape (§4.2) |
| O-Amendment-2 | Confirm 9 CHECK constraints **OR** 10 with NF1 (optional all-or-nothing per §4.3 last note) |
| O-Amendment-3 | Confirm 5 indexes (§4.5) including the critical `idx_mcf_cert_lookup` for trigger hot path |
| O-Amendment-4 | Confirm cross-schema FK `fk_mcf_cert_panel_run` to `contract.panel_output_record` (Drizzle DDL-only pattern preserved) |
| O-Amendment-5 | Confirm M3 trigger ALTER scope — **only the cert-lookup FROM clause changes**, all other branches preserved verbatim; PR-level diff verification per R-9 |
| O-Amendment-6 | Confirm supersession FK redirect via DROP/ADD CONSTRAINT (safe — 0 rows) |
| O-Amendment-7 | Confirm 3 shared CHECK extensions (additive, BCF-neutral); `operator_confirm_rule_action_chk` NOT changed |
| O-Amendment-8 | Confirm Drizzle changes (1 new file + 3 file updates per §8.2) |
| O-Amendment-9 | Confirm DDL apply order (§9.1) + forward-only discipline (rollback DDL ships as companion but is emergency-only per D-Correction-3) |
| O-Amendment-10 | Confirm 15-check post-apply verifier (§12) including behavioral exercises #13 + #14 that prove the amended trigger reads the sibling end-to-end |
| O-Amendment-11 | Confirm next gate: M3 amendment implementation PR (DDL + Drizzle + dry-run + post-apply verifier; **NO DB APPLY**) |

---

## 15. Recommended next gate

### 15.1 Recommendation: M3 amendment implementation PR in bc-core (NO DB APPLY)

**Next gate: open the M3 amendment implementation PR.** Branch from `bc-core` main (currently `a6a3e64`). Deliverables:

| Layer | Files |
|---|---|
| DDL forward | `bc-core/docker/redesign/05a-mcf-cert-amendment.sql` (per §9.1) |
| DDL rollback | `bc-core/docker/redesign/05a-mcf-cert-amendment-rollback.sql` (per §10) |
| Drizzle new | `bc-core/src/database/schema/mcf/certification-record.ts` |
| Drizzle updates | `bc-core/src/database/schema/mcf/index.ts` (re-export); `bc-core/src/database/schema/mcf/metric-supersession.ts` (comment update); `bc-core/src/database/schema/contract/framework-policy.ts` (CHECK update); `bc-core/src/database/schema/contract/operator-confirm-rule.ts` (2 CHECK updates) |
| Dry-run | `bc-core/scripts/mcf-m3-cert-amendment-dry-run.mjs` (8 preconditions + pre-amendment trigger body capture) |
| Post-apply verifier | `bc-core/scripts/mcf-m3-cert-amendment-post-apply-verification.mjs` (15 checks) |

PR title (suggested): `feat(mcf): M3 cert-target amendment — mcf.certification_record sibling + trigger ALTER + FK redirect + shared CHECK extensions (NO DB APPLY)` (mirrors PR #103 naming).

PR body should explicitly state:
- DDL hash captured
- 8 dry-run preconditions PASS expected (against pre-amendment substrate)
- 15 post-apply checks PASS expected (post-amendment); behavioral checks #13 + #14 prove the amended trigger reads the sibling end-to-end
- Forward-only per D-Correction-3; rollback DDL ships as emergency-only companion
- M4 implementation remains BLOCKED until (1) this amendment DDL applies + verifies AND (2) M4 DBCP is rewritten around `mcf.certification_record`

### 15.2 Subsequent gate: M3 amendment DDL apply

After the implementation PR merges, a separate operator-authorized session applies the DDL to `bc_platform_dev`. Standard DCP discipline:
1. Pre-apply dry-run → 8/8 PASS
2. STOP for explicit operator approval
3. `psql -v ON_ERROR_STOP=1 -f docker/redesign/05a-mcf-cert-amendment.sql`
4. Post-apply verifier → 15/15 PASS

### 15.3 Subsequent gate: M3 amendment evidence PR

Mirrors PR #102 / PR #104 pattern — audit artifacts under `scripts/audit-output/` + closeout doc on bc-docs-v3 main. Specific file list (per P-Amendment-8):

| Layer | File |
|---|---|
| Apply audit (bc-core) | `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.summary.md` |
| Apply audit (bc-core) | `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.precondition.jsonl` |
| Apply audit (bc-core) | `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.planned-sql.sha256.txt` |
| Apply audit (bc-core) | `scripts/audit-output/mcf-m3-cert-amendment-dry-run-{ts}.pre-amendment-trigger-body.sql` (rollback safety snapshot) |
| Apply audit (bc-core) | `scripts/audit-output/mcf-m3-cert-amendment-post-apply-{ts}.summary.md` |
| Apply audit (bc-core) | `scripts/audit-output/mcf-m3-cert-amendment-post-apply-{ts}.evidence.jsonl` |
| Closeout doc (bc-docs-v3) | `docs/implementation/mcf-m3-cert-amendment-ddl-apply-closeout.md` (mirrors `mcf-m3-ddl-apply-closeout.md` `d1f67d0` style: provenance + apply outcome + 15-check summary + independent confirm + operational observations + held-closed list + MCF substrate arc tally update) |

The evidence PR is bc-core; the closeout doc commits directly to bc-docs-v3 main (mirroring M2/M3 closeout pattern). Both go in the same operator-authorized session immediately after the apply succeeds.

### 15.4 Then: M4 DBCP rewrite (next-next gate)

Per D-Correction-2 + D-Correction-6: after the M3 amendment applies + verifies, the M4 DBCP is rewritten around `mcf.certification_record`:
- D-19 reversed (per-framework sibling confirmed; no governance_scope column)
- §9 cert column matrix rewritten for the sibling's 25-column shape
- §10 seed rows corrected (operator_confirm_rule.action_code semantic correction; scope='mcf' / transition values; framework_policy scope_code='mcf')
- §14 dry-run + verifier assumptions updated for the new substrate state

### 15.5 What stays closed in this DBCP

| | Status |
|---|---|
| M3 amendment implementation PR | Operator authorizes next; not opened by this DBCP |
| M3 amendment DDL apply | Pending implementation PR |
| M3 amendment evidence PR | Pending apply |
| **M4 DBCP rewrite** | Pending M3 amendment apply + verifier PASS (per D-Correction-2) |
| **M4 implementation PR** | BLOCKED until M3 amendment + M4 DBCP rewrite (per discipline assertions §1.5) |
| M4 DDL apply / M4 evidence PR | Blocked |
| M5+ gates (panel substrate, formula AST, package signature, fixture, verifier, panel impl, etc.) | All downstream of M4; blocked |
| MCF metric contract authoring | Blocked |
| BCF data touches | None |
| `bc-postgres` MCP `allow_write` widening | None |
| bc-core code edits this DBCP gate | None |
| M3 substrate rollback | NOT executed (per D-Correction-3) |

---

## Document verification

- **All 15 required sections present** (§1 Scope and grounding; §2 Accepted correction decisions; §3 Current live M3 state + rollback non-requirement; §4 mcf.certification_record table design; §5 M3 trigger amendment; §6 Supersession FK amendment; §7 Shared policy/rule CHECK amendments; §8 Drizzle impact; §9 DDL apply sequence; §10 Rollback story; §11 Dry-run verifier requirements; §12 Post-apply verifier requirements; §13 Risks and mitigations; §14 Operator approvals; §15 Recommended next gate).
- **All 7 D-Correction decisions resolved** in §2 with explicit operator answers + how this DBCP realizes each.
- **25-column mcf.certification_record table spec** complete in §4.2.
- **9 (or 10 with NF1) CHECK constraints** enumerated in §4.3.
- **5 indexes** enumerated in §4.5 including the critical hot-path index for the trigger.
- **M3 trigger ALTER scope** explicit (§5.2): one FROM clause changes; all other branches preserved verbatim; PR-level diff verification enforced per R-9.
- **Supersession FK redirect** specified (§6.2) with safety rationale (§6.3).
- **3 additive shared CHECK extensions** specified (§7.1-§7.3); `operator_confirm_rule.action_code` explicitly NOT changed (§7.4).
- **Drizzle impact** scoped (§8): 1 new file + 3 file updates.
- **DDL apply sequence** with full SQL sketches (§9.1) including the trigger ALTER skeleton.
- **Rollback DDL** specified with pre-condition guards (§10.1-§10.2); emergency-only per D-Correction-3.
- **8-precondition dry-run** (§11) including pre-amendment trigger body capture for rollback.
- **15-check post-apply verifier** (§12) including critical behavioral exercises #13 + #14 that prove end-to-end trigger correctness.
- **12 risks documented** (§13) with mitigations; 3 stop conditions enumerated (§13.1).
- **11 operator approvals** (§14) gating the implementation PR.
- **Next gate** clearly specified (§15.1) with subsequent gate sequence (§15.2-§15.4).
- **No code changes, no DDL applied, no MCF metric contracts created, no certification rows written, no bc-core file edits, no M4 DBCP edits, no BCF data touched.** Doc-only design commit to bc-docs-v3 main.
- **M3 substrate stays applied** — no rollback (per D-Correction-3); forward amendment only.
- **M4 implementation remains BLOCKED** until M3 amendment applies + M4 DBCP is rewritten around `mcf.certification_record`.
