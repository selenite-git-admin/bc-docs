---
uid: bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp
title: BCF/MCF Evidence Boundary + contract.* Schema Retirement DBCP
description: Strategic planning DBCP for resolving the BCF↔MCF authoring-substrate boundary. The generic `contract.*` schema currently holds BCF authoring evidence (24 panel_output_record + 23 calibration_event + 3,531 certification_record + 1 authoring_panel_rejection_log + 3 framework_policy rows) AND is the FK target for 5 inbound `mcf.*` FKs declared by M5 §5's D-M5-B hybrid-composition decision. The no-synthetic hard rule + the operator's directive that "MCF evidence belongs in `mcf.*`" + the architectural principle that BCF authoring evidence belongs in a BCF-owned schema (currently 0 tables — `bcf.*` does not yet exist) together require either (a) renaming `contract.*` to `bcf.*` + breaking the 5 cross-schema MCF→BCF FKs by giving MCF its own panel-output root, OR (b) keeping `contract.*` as a shared neutral evidence ledger AND amending the hard rule to permit MCF writes to it as a substrate-enforced atomicity exception. This DBCP enumerates current state, classifies every row, maps the 9-FK chain on `contract.panel_output_record`, surfaces the architectural conflict between M5 §5 D-M5-B (hybrid composition) and the new no-synthetic + MCF-evidence-isolation hard rules, and presents 4 migration options with operator decisions D1..D11. **NOT EXECUTED. This is a strategic planning artifact only — no DDL, no DML, no FK changes, no row mutation. Tenant DBs (`tbc_{slug}_dev`) are explicitly out of scope. Legacy `metric.*` retirement (1241 metric_definition + ~15k other rows) is explicitly out of scope unless separately authorized.** Relationship to bc-core PR #133: that PR's dry-run script may still merge as inventory/snapshot tooling, but the apply gate stays paused until this boundary question is resolved (see §11 for sequencing). The DBCP's recommendation is **Option A — create a BCF-owned schema (`bcf.*`) for authoring evidence and migrate the 3,553 authority-bearing BCF rows out of generic `contract.*`**. Ownership clarity beats short-term DDL minimization; the alternative Option B (adding a `framework_code` column to keep BCF/MCF rows sharing `contract.*`) is a patch, not a true boundary, and is preserved in this DBCP only as a documented-but-rejected compromise. Option A phases are A1 (create `bcf.*` evidence tables) → A2 (migrate authority-bearing rows) → A3 (update writers/readers) → A4 (retire/freeze generic `contract.*` evidence tables) → A5 (revisit M5/M12/M12.5 FK assumptions so MCF does not depend on `contract.panel_output_record`). No first real M12 panel run until the evidence boundary is resolved.
status: draft
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp
---

# BCF/MCF Evidence Boundary + `contract.*` Schema Retirement DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> Generic `contract.*` tables today hold BCF authoring evidence and synthetic/smoke rows, AND are the FK target for 5 inbound MCF FKs (`mcf.metric_authoring_panel_run`, `mcf.certification_record`, `mcf.metric_contract_revision`, `mcf.metric_publication_eligibility_result`, `mcf.metric_supersession`). Under the new no-synthetic + MCF-evidence-isolation hard rules, where should BCF authoring evidence + MCF authoring evidence live? What happens to the existing 3,579 `contract.*` authoring-substrate rows?

### 1.2 In scope

- Read-only inventory of 5 `contract.*` tables (`panel_output_record`, `authoring_panel_rejection_log`, `calibration_event`, `certification_record`, `framework_policy`)
- Cross-schema FK dependency analysis (9 inbound FKs on `contract.panel_output_record.panel_run_uid`)
- Classification of every row in scope as one of: BCF authority-bearing / synthetic-smoke debt / shared policy / unrelated chain infrastructure
- Architectural conflict surfacing between M5 §5 D-M5-B (hybrid composition decision) and the operator's new hard rules
- 4 migration options with trade-offs
- Operator decisions D1..D11 to authorize the chosen path
- Relationship to bc-core PR #133 (cleanup dry-run; the apply gate's go/no-go depends on this DBCP's resolution)
- Sequencing recommendation across PR #133 dry-run merge / PR #133 apply gate / first real M12 panel run / M12.5 first materialization / M13 first evaluation / M14 opening

### 1.3 Explicit non-scope

- ❌ **Tenant result databases `tbc_{slug}_dev`** — all per-tenant analytical substrate (snapshots, fact tables, evaluation results, MLS-15..MLS-25 tenant-side state) lives in tenant DBs per D162-D167 and is **out of scope**. No tenant DB connection is opened by any planning probe in this DBCP. The platform DB (`bc_platform_dev`) is the only DB inventoried.
- ❌ **Legacy `metric.*` schema retirement** — the 16,820 rows in `metric.*` (1241 `metric_definition` + 1216 `metric_formula` + 1133 `metric_binding` + 905 `readiness_ledger` + 1659 `mls_state` + 3317 `mls_state_event` + etc.) including the 2 active AR pilot KPIs (`ar_growth_rate`, `revenue_collection_rate`) are **explicitly preserved and out of scope** unless the operator separately authorizes a `metric.*` retirement gate alongside the M17 tenant-runtime migration per the M12 implementation closeout §9.
- ❌ **No DDL** — no `CREATE TABLE`, `DROP TABLE`, `ALTER TABLE`, `CREATE SCHEMA`, FK redirection, or any DDL change of any kind. This DBCP is planning only.
- ❌ **No DML** — no row mutation. `bc-postgres` MCP stayed `allow_write=false` throughout the inventory probes.
- ❌ **No M11 / M12 / M12.5 / M13 / M14 runs** — operational gates remain closed.

## 2. Authority

- Predecessor DBCPs (architectural authority being reconciled):
  - `bc-docs-v3/docs/implementation/metric-context-framework-m5-panel-substrate-dbcp.md` (D-M5-B hybrid composition decision)
  - `bc-docs-v3/docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` (B1 review patch — `contract.panel_output_record` written by M12 per active FK + M5 §5 1:1 composition)
  - `bc-docs-v3/docs/implementation/bcf-authoring-test-row-cleanup-dbcp.md` (the 11-row smoke cleanup DBCP merged at bc-docs-v3 main `0f42662`; companion to bc-core PR #133)
- Operator hard rules (newly established):
  - No synthetic / mock / replay / canned data may be written to persistent substrate
  - MCF evidence belongs in `mcf.*`
  - Future MCF metric authority events must NOT write to generic `contract.panel_output_record`, `contract.calibration_event`, or generic `contract.certification_record`
  - Tenant result DBs are separate and out of scope
- Live DB state: verified via `bc-postgres` MCP read-only at DBCP-write time (see §3)

## 3. Current-state inventory (live-verified, read-only)

### 3.1 Schema landscape (platform DB)

| Schema | Tables | Purpose | Status |
|---|---|---|---|
| `mcf.*` | **17** | MCF metric authoring + certification + PE-MC substrate | code-live |
| `concept_registry.*` | **11** | BCF concept registry (entity / business_concept / characteristic / representation_term / etc.) | code-live |
| `contract.*` | many | Mixed: BCF authoring evidence + cross-framework policy registry + contract chain substrate (admission / canonical / observation / source / l_node / chain_status / etc.) | **DISPUTED** — the focus of this DBCP |
| `metric.*` | **16** | Legacy pre-MCF metric chain (preserved; out of scope) | legacy |
| `bcf.*` | **0** | **DOES NOT EXIST** — would need to be created if BCF authoring substrate moves to its own schema | not present |
| `governance.*` | **0** | DOES NOT EXIST — alternative shared-policy destination | not present |
| `policy.*` | **0** | DOES NOT EXIST — alternative shared-policy destination | not present |

### 3.2 `contract.panel_output_record` (24 rows; 9 inbound FKs)

| Cohort | n | `prompt_version` | `policy_version` | Window | Verdict mix | Classification |
|---|---|---|---|---|---|---|
| BCF registry-authoring (real) | **19** | `registry-authoring/v1.0` | `v1` | 2026-05-22 → 2026-05-26 | 17× APPROVE_FOR_DRAFT + 2× OPERATOR_REVIEW | **BCF authority-bearing** |
| BCF live smoke | 2 | `bcf-live-smoke/2026-05-20` | `v1` | 2026-05-20T15:13 (×2) | 1× APPROVE_FOR_DRAFT + 1× REJECT | **smoke debt** (per merged cleanup DBCP) |
| PR-10 smoke | 1 | `smoke-test-v0` | `smoke-test/pr10` | 2026-05-20T12:03 | 1× APPROVE_FOR_DRAFT | smoke debt |
| Context smoke | 1 | `v1.0` | `context-smoke/2026-05-20` | 2026-05-20T13:15 | 1× FAIL_QA_GATE | smoke debt |
| Roster smoke | 1 | `v1.0` | `bcf-roster-smoke/2026-05-20` | 2026-05-20T15:54 | 1× FAIL_QA_GATE | smoke debt |
| MCF panel runs | **0** | (would be `m12-panel-v1`) | (would be `1.0.0`) | n/a | n/a | **none yet — M12 has never operationally run** |

All 24 rows have `stage_code='authoring'`. None are at `stage_code='publication'` or `'lifecycle_audit'` (the other 2 CHECK-allowed values).

### 3.3 `contract.certification_record` (3,531 rows; 0 inbound FKs)

| Action / shape | n | Classification |
|---|---|---|
| `admit_bf_catalog` | 1,651 | BCF authority-bearing |
| `remediate_bf_semantics` | 1,396 | BCF authority-bearing |
| `demote_bf_catalog` | 388 | BCF authority-bearing |
| `mark_bf_correction_required` | 30 | BCF authority-bearing |
| `registry_transition` (govScope=registry) | 17 | BCF registry authority-bearing |
| `registry_create` (govScope=registry) | 12 | BCF registry authority-bearing |
| `submit_for_review` (business_field) | 9 (incl. 1 smoke `21023aa1`) | 8 BCF + **1 synthetic-provider smoke** |
| `certify` (business_field) | 8 | BCF authority-bearing |
| `admit_bf_from_candidate_import` | 8 | BCF authority-bearing |
| `registry_author_vocabulary` (govScope=registry) | 5 | BCF registry authority-bearing |
| `recertify_bf_catalog` | 4 | BCF authority-bearing |
| `submit_for_review` / `certify` / `remediate_description` (canonical_field) | 3 | BCF canonical field authority-bearing |

`primitive_type` distribution: 3,494 `business_field` + 34 NULL (registry transitions) + 3 `canonical_field`. **All non-NULL primitive_types are BCF-shape.** Zero MCF rows (M4 cert writer would write to `mcf.certification_record`, not `contract.*`).

### 3.4 `contract.calibration_event` (23 rows; 0 inbound FKs)

| Cohort | n | `policy_version` | `ai_verdict_code` | Classification |
|---|---|---|---|---|
| BCF registry-authoring | 18 | `v1` | APPROVE_FOR_DRAFT | BCF authority-bearing |
| BCF registry-authoring | 2 | `v1` | OPERATOR_REVIEW | BCF authority-bearing |
| BCF live-smoke REJECT | 1 | `v1` | REJECT | smoke debt |
| BCF live-smoke APPROVE | 1 | `v1` | APPROVE_FOR_DRAFT | smoke debt (mismatched APPROVE; paired with smoke panel `c6d85db6`) |
| Context smoke | 1 | `context-smoke/2026-05-20` | FAIL_QA_GATE | smoke debt |
| Roster smoke | 1 | `bcf-roster-smoke/2026-05-20` | FAIL_QA_GATE | smoke debt |

**All rows are BCF.** Zero MCF rows.

### 3.5 `contract.authoring_panel_rejection_log` (1 row; 0 inbound FKs)

| Cohort | n | Classification |
|---|---|---|
| BCF live-smoke REJECT (cohort C) | 1 | smoke debt (the only row in the table) |
| Real BCF authoring rejections | **0** | — |

The table is currently 100% smoke debt. Real BCF authoring runs (the 17 APPROVE_FOR_DRAFT + 2 OPERATOR_REVIEW from `registry-authoring/v1.0`) did not generate persistent rejection log rows during the 2026-05-22..2026-05-26 window.

### 3.6 `contract.framework_policy` (3 rows; multiple inbound FKs)

| `policy_uid` | `scope_code` | `effective_from` | `effective_to` | Classification |
|---|---|---|---|---|
| `bcf-bf-bo-scope1` | `bf_bo` | 2026-05-20 | NULL | BCF business-field/business-object policy |
| `mcf_v1` | `mcf` | 2026-05-27 | NULL | MCF policy |
| `bcf-registry-scope1` | `registry` | 2026-05-22 | NULL | BCF registry-authoring policy |

This is the **only `contract.*` row category that legitimately serves both BCF and MCF**. Both frameworks reference `policy_version='v1'` (or `mcf_v1`) for runtime CHECK enforcement; both `M5` and the new MCF M13/M12.5 services depend on this registry for their framework-policy probes.

### 3.7 FK dependency map on `contract.panel_output_record.panel_run_uid`

**9 inbound FKs, all RESTRICT:**

| FK constraint | Source table | Schema | Refs to smoke uids today |
|---|---|---|---|
| `fk_authoring_panel_rejection_log__panel_run` | `contract.authoring_panel_rejection_log` | contract | 1 |
| `fk_calibration_event__panel_run` | `contract.calibration_event` | contract | 4 |
| `fk_certification_record__panel_run` | `contract.certification_record` | contract | 1 |
| `fk_intake_queue__panel_run` | `contract.intake_queue` | contract | 0 (intake_queue empty) |
| `fk_mcf_cert_panel_run` | **`mcf.certification_record`** | **mcf** | 0 (table empty; M13 PR-2 enforces NULL cert id) |
| `fk_mapr_panel_run` | **`mcf.metric_authoring_panel_run`** | **mcf** | 0 (table empty; M12 never run) |
| `fk_mcr_panel_run` | **`mcf.metric_contract_revision`** | **mcf** | 0 (table empty) |
| `fk_mper_panel_run` | **`mcf.metric_publication_eligibility_result`** | **mcf** | 0 (table empty) |
| `fk_mcs_panel_run` | **`mcf.metric_supersession`** | **mcf** | 0 (table empty) |

**5 of 9 inbound FKs originate in `mcf.*`** — this is the cross-schema architectural inversion that the operator's hard rule conflicts with. The mcf.* tables are designed to point UP into `contract.panel_output_record` as the shared panel-run root.

`contract.certification_record`, `contract.calibration_event`, `contract.authoring_panel_rejection_log` each have **0 inbound FKs** (leaves).

## 4. Classification matrix

| Surface | Classification | Authority | What to do with it |
|---|---|---|---|
| `contract.panel_output_record` 19 `registry-authoring/v1.0` rows | **BCF authority-bearing** | BCF authoring outcomes from `RegistryAuthoringOrchestrator` real work 2026-05-22..2026-05-26 | **Preserve.** Belongs in BCF-owned schema if `bcf.*` is created; otherwise stays. |
| `contract.panel_output_record` 5 smoke rows | smoke debt | none | **Delete** per merged cleanup DBCP (PR #133 dry-run already captured precondition snapshot) |
| `contract.certification_record` 3,530 non-smoke rows | **BCF authority-bearing** | BCF cert ledger for business_field + canonical_field + registry transitions | **Preserve.** Belongs in BCF-owned schema; otherwise stays. |
| `contract.certification_record` 1 smoke row (`21023aa1`) | smoke debt (`provider:synthetic`) | none | **Delete** per merged cleanup DBCP |
| `contract.calibration_event` 19 non-smoke rows | **BCF authority-bearing** | BCF calibration audit | **Preserve.** Belongs in BCF-owned schema; otherwise stays. |
| `contract.calibration_event` 4 smoke rows | smoke debt | none | **Delete** per merged cleanup DBCP |
| `contract.authoring_panel_rejection_log` 1 smoke row | smoke debt | none | **Delete** per merged cleanup DBCP |
| `contract.framework_policy` 3 rows | **shared policy / configuration** | Cross-framework runtime policy registry | **Preserve at neutral location.** Either stays in `contract.*` re-cast as shared, or moves to `governance.*` / `policy.*` |
| Other `contract.*` chain tables (~127,000 rows: source / admission / canonical / observation / chain_status / chain_trace / mc_integrity_state / l_node_semantic_* / contract_release_note / mc_envelope_audit / etc.) | **Unrelated contract-chain infrastructure** (active pilot work D305, D366, D408, D409, SAP) | **Preserve untouched.** Different concern from BCF-vs-MCF authoring boundary; lives at the post-admission contract layer, not authoring layer |
| `mcf.*` 17 tables (0 rows) | **MCF substrate** | Already in correct schema | **No action** |
| `metric.*` 16 tables (~16,820 rows) | legacy + AR pilot KPIs | **Out of scope** per §1.3 | No action this DBCP |
| Tenant `tbc_{slug}_dev` DBs | tenant analytics | **Out of scope** per §1.3 | No action this DBCP |

## 5. Hard boundary rules (operator-locked, restated for runtime enforcement)

| # | Rule | Enforcement mechanism |
|---|---|---|
| HR1 | No synthetic / mock / replay / canned data written to persistent substrate | Writer-boundary `model_identity_json.*.provider NOT IN ('synthetic','replay','mock','canned')` CHECK; pre-execution audit; this DBCP retires the 1 known violation |
| HR2 | MCF evidence belongs in `mcf.*` | Service-side: M4 / M12 / M12.5 / M13 / M14 writers refuse to INSERT into `contract.*` authoring tables. Substrate-side: removal of FKs pointing `mcf.* → contract.panel_output_record` (Option A) OR explicit policy that `contract.panel_output_record` is a shared evidence ledger (Option B). (Option A chosen per §7; Option B retained only as rejected analysis.) |
| HR3 | Future MCF metric authority events must NOT write to generic `contract.panel_output_record` / `contract.calibration_event` / generic `contract.certification_record` | **DIRECTLY CONFLICTS with M5 §5 D-M5-B + M12 DBCP B1 review patch** which require `contract.panel_output_record` write. This DBCP must surface and resolve this conflict |
| HR4 | Tenant result DBs are separate and out of scope | Already substrate-enforced via separate DB connections (`DATABASE_URL` vs `TENANT_DATABASE_URL` per D162-D167) |
| HR5 | Mocks only inside unit tests or SAVEPOINT-rolled-back integration tests | Already locked at bcf-authoring-test-row-cleanup-dbcp §10 D9 |

## 6. The architectural conflict

The new hard rule HR3 directly contradicts two existing operator-accepted MCF design decisions:

### M5 §5 D-M5-B (hybrid composition; accepted)

> "KEEP `contract.panel_output_record` as the canonical panel-run identity (cross-framework shared substrate already exists and is structurally MCF-compatible per stage_code enum + 24 live BCF rows untouched); ADD 4 mcf-owned tables for MCF-specific panel discipline … with workbench fingerprint hash + reservoir-provenance fields … and 1:1 PK FK to contract.panel_output_record"

### M12 DBCP B1 review patch (accepted)

> "`contract.panel_output_record` is shared substrate that M12 MUST write to (per active FK `fk_mapr_panel_run` + M5 §5 1:1 composition)"
> "Per M5 §5 (1:1 composition) + active FK `fk_mapr_panel_run`, `contract.panel_output_record` MUST be written BEFORE `mcf.metric_authoring_panel_run`. M12 panel writes BOTH rows with the SAME `panel_run_uid`."

These were operator-accepted in earlier gates (D-M5-1..D-M5-10 + D-M12-1..D-M12-11). The hard rule HR3 retroactively disallows the M12 `contract.panel_output_record` write that M5 §5 made structurally mandatory.

**The conflict cannot be resolved without operator action.** Either:
1. The hard rule HR3 is amended to admit `contract.panel_output_record` as a shared neutral evidence ledger (preserving M5/M12 design)
2. OR the M5/M12 design is restructured (breaking the 5 cross-schema FKs and giving MCF its own panel-output root)

(Option A chosen per §7; Option B retained only as rejected analysis.)

## 7. Proposed target ownership model (4 options)

| Option | BCF authoring rows | MCF authoring rows | `contract.framework_policy` | DDL required | Migration shape |
|---|---|---|---|---|---|
| **A — Full BCF isolation** (RECOMMENDED) | Move to new `bcf.*` schema (4 new tables) | Stay in existing `mcf.*` substrate; MCF gets its own `mcf.metric_authoring_panel_output_record` root (NEW); 5 mcf→contract FKs deleted, 5 new mcf→mcf FKs added | Deferred — placement (`contract.*` vs `governance.*` vs `policy.*`) decided in a separate policy-placement gate per §11 D7 | MEDIUM: 1 new schema + 4 new tables in `bcf.*` + 1 new table + 5 FK redirects in `mcf.*` | Schema creation + data backfill + FK redirect + service code rewrite (M5/M12/M4/M13 services all touch panel_run_uid) |
| **B — `contract.*` re-cast as shared evidence ledger** (REJECTED) | Stay in `contract.*` but add `framework_code` CHECK column (`'bcf' | 'mcf' | 'shared'`) | Stay using existing M5 §5 1:1 composition with the same `contract.panel_output_record` root + the framework_code marker; M12 sets `framework_code='mcf'` on its panel_output_record write | Stay in `contract.framework_policy` (already cross-framework by design) | SMALL: 1 new column + 1 CHECK constraint per table; **no schema renames**, no FK redirects | Add column, backfill `framework_code='bcf'` on existing 24+23+3530+1 rows, amend writers |
| **C — Hybrid (BCF moves, MCF substrate-shared)** (REJECTED) | Move BCF authority-bearing rows to new `bcf.*`; keep `contract.panel_output_record` as the cross-framework root for MCF | MCF stays using `contract.panel_output_record` exactly as M5/M12 designed | Stay in `contract.framework_policy` | MEDIUM: 3-4 new `bcf.*` tables + data migration; `contract.*` retained for the root identity | Schema partial-rename + data backfill |
| **D — Cancel migration; live with the conflict** (REJECTED) | Stay in `contract.*` | Stay in `contract.*` per M5/M12 | Stay | NONE | No action; HR3 stays as aspirational and unenforced |

### Recommended target: **Option A** ("Full BCF isolation — create `bcf.*` schema")

Rationale:
- **Ownership clarity beats short-term DDL minimization.** A `framework_code` column (Option B) is a patch, not a true boundary — it leaves BCF and MCF rows physically commingled in the same table and depends on every reader honoring a filter discipline that has no substrate enforcement against accidental cross-framework reads. Option A puts each framework's evidence in a framework-owned schema, making the boundary visible at the table-name level and substrate-enforced by FK direction.
- **Honors HR2 and HR3 verbatim.** "MCF evidence belongs in `mcf.*`" + "no MCF writes to generic `contract.*` authoring tables" both read cleanly once MCF gets `mcf.metric_authoring_panel_output_record` as its own root and BCF authoring evidence has moved to `bcf.*`. No hard-rule amendment required; the rules stand as written.
- **Forces the M5 §5 + M12 design reconsideration that the hard rule implies.** D-M5-B's hybrid composition was a substrate-driven optimization made when only BCF authoring tables existed. With the new hard rules in force, the optimization is no longer viable — MCF should not be transitively coupled to a BCF root just because the BCF root existed first. Option A surfaces this reconsideration (Phase A5) rather than hiding it behind a column.
- **`framework_code` is rejected explicitly** so future contributors do not relitigate Option B. The column would still pass HR2/HR3 reads ("the row says MCF, so it's MCF evidence even though it lives in contract.*") but the operator's directive is that physical location of evidence is the boundary, not a label.
- **Cost is real but bounded.** Phases A1-A5 are sequential but tractable. Each phase has its own DBCP and gate; no big-bang migration. The 5 mcf→contract FKs are dropped + recreated as mcf→mcf in Phase A5; service code touches M5/M12/M4/M13 writers but not their core algorithms.
- **PR #133 cleanup infrastructure remains useful.** The dry-run script + 3 artifacts catalog the existing smoke debt at byte-fidelity. Under Option A, that catalog becomes part of the Phase A2 backfill provenance — the smoke rows are NOT migrated; the BCF authority-bearing rows are. The apply gate stays paused until Phase A1/A2 designs are accepted.

Option B's smaller DDL footprint is not a sufficient argument against the boundary-clarity gain of Option A. Options C and D are also rejected: C is partial and leaves MCF still depending on `contract.panel_output_record`; D abandons HR3 entirely.

## 8. Migration strategy (under Option B — REJECTED, kept for reference)

**Option B is rejected per §7.** This section is preserved so future contributors can see exactly what the framework_code-column compromise would have looked like and why the operator rejected it.

Brief shape (do not implement):
- Single small-DDL gate would have added `framework_code text NOT NULL DEFAULT 'bcf' CHECK (framework_code IN ('bcf','mcf'))` to 4 tables (`contract.panel_output_record`, `contract.authoring_panel_rejection_log`, `contract.calibration_event`, `contract.certification_record`).
- M12 writer would have been amended to set `framework_code='mcf'` on its panel_output_record insert.
- BCF authoring writer would have continued writing the DEFAULT 'bcf'.
- HR3 would have been amended to admit MCF writes IFF the row carries `framework_code='mcf'` AND `policy_version='mcf_v1'` AND a corresponding `mcf.*` row exists for the same `panel_run_uid`.

Why rejected: `framework_code` is a label, not a boundary. It leaves BCF and MCF rows physically commingled and depends on every reader honoring a filter discipline. The operator's directive is that physical location of evidence IS the boundary. See §7 Option A rationale.

## 9. Migration strategy (under Option A — RECOMMENDED)

Five sequential phases, each with its own DBCP and operator-authorized gate. No big-bang migration. The smoke debt (PR #133) is retired BEFORE Phase A1 so the migrated BCF rows are authority-bearing only.

### Phase A1 — create `bcf.*` evidence schema

Create the `bcf.*` schema and 4 new evidence tables with identical column structure to their current `contract.*` counterparts:

- `bcf.panel_output_record` — BCF authoring panel output evidence
- `bcf.authoring_panel_rejection_log` — BCF authoring rejection log
- `bcf.calibration_event` — BCF calibration audit
- `bcf.certification_record` — BCF cert ledger (business_field + canonical_field + registry)

Substrate-only DDL. No data movement. No FK redirects yet. Existing `contract.*` tables remain in place and continue to accept BCF writes — the new `bcf.*` tables stay empty during Phase A1.

### Phase A2 — migrate authority-bearing BCF rows from `contract.*` to `bcf.*`

Operator-authorized data migration. **Smoke-debt rows are NOT migrated** — they are retired separately by PR #133's apply gate before Phase A2 runs.

Per-table backfill:
- 19 `registry-authoring/v1.0` rows → `bcf.panel_output_record`
- 0 rows → `bcf.authoring_panel_rejection_log` (the 1 existing row is smoke)
- 19 BCF authority rows → `bcf.calibration_event` (the 4 other rows are smoke)
- 3,530 BCF authority rows → `bcf.certification_record` (the 1 other row is smoke)

Total authority-bearing migration: 3,568 rows. Single transaction or staged migration per per-table operator-authorized sub-gate.

Validation: after migration, `bcf.*` row counts equal the pre-migration `contract.*` non-smoke counts; `contract.*` rows remain in place (still readable by old code paths) but writers are flipped in Phase A3.

### Phase A3 — update BCF writers and readers to use `bcf.*`

Service-side code change. BCF `RegistryAuthoringOrchestrator` and related BCF authoring code paths flip their INSERT targets from `contract.*` to `bcf.*`. Read paths in BCF dashboards and audit consumers flip their SELECT targets similarly.

Cutover ordering: writers first (so new BCF authoring rows land in `bcf.*` immediately), readers second (after backfill validation in Phase A2 confirms parity). During the brief writer-only window, BCF dashboards may show stale `contract.*` data; this is acceptable for operator-tolerated downtime.

Test plan: unit tests assert BCF writers no longer reach `contract.*`; integration tests assert end-to-end BCF authoring round-trips via `bcf.*`.

### Phase A4 — retire or freeze old generic `contract.*` evidence tables

After Phase A3 cutover succeeds and a soak period (operator-defined; minimum 7 days) confirms no BCF code paths still touch the old `contract.*` tables, the operator authorizes:
- **Option 1 (freeze):** add a trigger or grant change that blocks INSERT/UPDATE on `contract.panel_output_record` / `contract.authoring_panel_rejection_log` / `contract.calibration_event` / `contract.certification_record`. Rows remain readable for historical audit; new writes are rejected. Lowest risk.
- **Option 2 (retire):** DROP the 4 tables. Requires all referencing FKs to be redirected (Phase A5) first.

Phase A4 does NOT decide between freeze and retire — that's a downstream operator choice once Phase A5 lands.

### Phase A5 — revisit M5/M12/M12.5 FK assumptions so MCF does not depend on `contract.panel_output_record`

The architectural reconsideration the new hard rules force. Concretely:
- Create `mcf.metric_authoring_panel_output_record` as MCF's own panel-run root (new table with the same column shape as `contract.panel_output_record`).
- Drop the 5 mcf→contract FKs (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`).
- Recreate them as mcf→mcf FKs pointing at the new MCF root.
- Update M5 §5 1:1 composition rule to compose `mcf.metric_authoring_panel_output_record` ↔ `mcf.metric_authoring_panel_run` (intra-mcf).
- Rewrite M12 panel service to write to `mcf.metric_authoring_panel_output_record` instead of `contract.panel_output_record`.
- Update M5 / M12 / M12.5 / M13 / M14 DBCPs to reflect the new boundary.

This phase is the most service-code-intensive of the five but the rewrite scope is bounded — the M12 writer's INSERT target changes, and the 5 mcf.* table FKs all retarget to the new root with the same `panel_run_uid` column shape.

Each phase has its own DBCP and operator-authorized gate. Estimated total effort: bounded but real; depends on operator authorization cadence. Substantially lower regression risk than a single big-bang migration. Substantially higher boundary clarity than Option B's framework_code patch.

## 10. Risk register

Risks R1, R5, R7, and R8 document rejected Option B/C/D paths for historical reasoning; they are not live recommendations. R2, R3, R4, and R6 apply to the recommended Option A path.

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| R1 | Operator chooses Option B; the framework_code amendment is interpreted as a loophole for future synthetic writes | LOW | MEDIUM | HR1 is enforced separately (`provider:'synthetic'` writer-boundary CHECK); framework_code is an orthogonal label, not a permission gate |
| R2 | Operator chooses Option A; the 5 mcf→contract FK redirects miss one (e.g. `fk_mcs_panel_run`) and leave a dangling reference | MEDIUM | HIGH | Each PR-A4 step has explicit FK-by-FK probe + post-apply verification; same M-series discipline as M13 PR-1 |
| R3 | M12 has never operationally run; we are reasoning about an unproven contract | HIGH | LOW | The M12 DBCP B1 review patch was explicit; M5 §5 D-M5-B is the authoritative substrate decision. The decision can be revisited cleanly before M12 first run |
| R4 | Real BCF authoring rows (the 19 + 18 + 2 = 39 authority-bearing rows) get accidentally caught by the cleanup if predicates are misapplied | LOW | HIGH | UID-based predicates per merged cleanup DBCP §3.1.1-§3.1.4 + sha256 fingerprint of planned DELETE prevent this. PR #133 dry-run already proved it |
| R5 | The 3,530 non-smoke BCF certs in `contract.certification_record` get conflated with the 0 MCF certs (which live in `mcf.certification_record`) | LOW | MEDIUM | Two separate tables with different FKs; primitive_type distribution is BCF-only. Option B's framework_code column makes the separation substrate-enforced going forward |
| R6 | `contract.framework_policy` 3-row registry gets fragmented (BCF + MCF + Registry move to 3 different schemas) and runtime policy probes break | MEDIUM | HIGH | Option B keeps the policy registry intact in `contract.framework_policy` (or recasts as `policy.framework_policy`); Option A makes this explicit (the separately deferred policy/governance placement DBCP per D7 with operator-supervised migration window) |
| R7 | M5 §5 D-M5-B accepted "no `contract.*` CHECK extensions" (per D-M5-7) — Option B adds a CHECK constraint that contradicts this | MEDIUM | MEDIUM | The contradiction must be surfaced and operator-resolved in §11 D5. Option B's CHECK is `framework_code IN ('bcf','mcf')` — bounded enum; not the kind of operator-unfriendly extension D-M5-7 forbade |
| R8 | The 19 `registry-authoring/v1.0` real BCF rows have `policy_version='v1'` (not `'bcf-registry-scope1'`); the framework_code label could conflict with policy version conventions | LOW | LOW | `policy_version` and `framework_code` are orthogonal — one is the policy registry key, the other is the framework owner. Backfill default of `'bcf'` is correct for these rows regardless of policy_version value |

## 11. Operator decisions (D1..D11)

| # | Decision | Default proposal | Operator must confirm |
|---|---|---|---|
| **D1** | Accept that HR3 ("no MCF writes to generic `contract.*` authoring tables") DIRECTLY CONFLICTS with M5 §5 D-M5-B + M12 DBCP B1 — and that the conflict cannot be resolved without choosing between amending HR3 or restructuring M5/M12 | ACCEPT (the conflict is documented in §6) | Y / N |
| **D2** | Choose target ownership model: **A (full BCF isolation — create `bcf.*` schema)** / B (rejected) / C (rejected) / D (rejected) | **A** | A / B / C / D |
| **D3** | ~~If Option B chosen: amend HR3 to admit `framework_code='mcf'` writes~~ **OBSOLETE** under Option A. HR3 stands as written; no amendment required because MCF no longer writes to `contract.*` once Phase A5 ships | OBSOLETE | n/a |
| **D4** | Authorize Phase A1 + A2 design (separate DBCP per phase): A1 creates `bcf.*` schema + 4 evidence tables; A2 migrates 3,568 authority-bearing BCF rows from `contract.*` to `bcf.*`. PR #133 apply gate stays paused until at least A1+A2 designs are accepted | ACCEPT | Y / N |
| **D5** | ~~If Option B chosen: M5 §5 D-M5-7 ("no `contract.*` CHECK extensions") is overridden~~ **OBSOLETE** under Option A. D-M5-7 stands as written — Option A does NOT extend `contract.*` CHECK constraints; it creates new `bcf.*` tables and (in Phase A5) retires the `contract.*` evidence tables entirely | OBSOLETE | n/a |
| **D6** | Authorize the 5-phase migration sequence (Phases A1..A5; each phase its own DBCP). Estimated bounded effort; each phase operator-authorized in isolation | ACCEPT | Y / N |
| **D7** | `contract.framework_policy` placement (stays in `contract.*` / moves to `governance.framework_policy` / moves to `policy.framework_policy`) is **DEFERRED** to a separate policy/governance placement DBCP — not bundled with the BCF authoring-evidence migration. The 3 framework_policy rows continue to function in `contract.*` during Phases A1..A5 | DEFER (separate gate) | Y / N |
| **D8** | bc-core PR #133 dry-run script: **may merge as inventory/snapshot tooling** if operator finds the dry-run + precondition snapshot useful; merge is not required for Option A to proceed (Phase A1 does not depend on PR #133) | MERGE PR #133 dry-run if desired; not required | Y / N (or N/A) |
| **D9** | bc-core PR #133 apply gate: **stays PAUSED** until Phase A1 + A2 designs are accepted. Apply executes against `contract.*` BEFORE Phase A2 migration (so smoke debt is retired before authority rows move) | PAUSE until post-A1+A2-design | Y / N |
| **D10** | Tenant result DBs (`tbc_{slug}_dev`) — explicit confirmation that they remain out of scope under this DBCP | OUT OF SCOPE | Y / N |
| **D11** | Legacy `metric.*` retirement — explicit confirmation that it remains out of scope under this DBCP; the 2 active AR pilot KPIs + ~16,818 supporting rows are preserved | OUT OF SCOPE | Y / N |

## 12. Relationship to bc-core PR #133

PR #133 contents:
- `scripts/bcf-authoring-test-row-cleanup-dry-run.mjs` (read-only; executed; PASS)
- `scripts/bcf-authoring-test-row-cleanup-apply.mjs` (authored; not executed)
- `scripts/bcf-authoring-test-row-cleanup-restore.mjs` (authored; not executed)
- 3 dry-run artifacts (precondition.jsonl + summary.md + planned-delete.sha256.txt)

**Recommendation under Option A:**
- ✅ **PR #133 dry-run may merge as inventory/snapshot tooling.** The precondition.jsonl is a byte-fidelity catalog of the 11 smoke rows; under Phase A2 it becomes useful provenance documenting which rows were NOT migrated to `bcf.*`. The apply + restore scripts are env-gated and cannot run accidentally. Merge is not required for Phase A1 to proceed.
- ⏸ **Pause the apply gate** until **Phase A1 + A2 designs are accepted** by the operator. The apply gate executes against `contract.*` (retiring smoke debt) BEFORE the Phase A2 migration moves the BCF authority-bearing rows. Sequencing: smoke retirement → then bcf.* schema creation → then authority-row migration.
- 🔧 **Optional pre-merge hygiene on PR #133:** the prior review (PR #133 review) flagged 3 minor diagnostic-clarity findings (HIGH-1 / MEDIUM-1 / LOW-1) in the apply + restore scripts. These are unrelated to this boundary DBCP and may be addressed in a small hygiene patch before PR #133 merges or in a follow-up.

**No first real M12 panel run** until the evidence boundary is resolved through at least Phase A5 (M12 writer flipped to `mcf.metric_authoring_panel_output_record`). The M12 first-real-panel-run DBCP authored separately must reflect the new MCF root, not `contract.panel_output_record`.

## 13. Sequencing recommendation

Under the recommended Option A, the gate sequence becomes:

1. **This DBCP (merged)** → operator reviews §11 D1..D11 in a follow-up gate.
2. **Operator authorization of D1..D11** in writing (D2=A, D4=ACCEPT Phase A1+A2 designs, D6=ACCEPT 5-phase sequence, D7=DEFER policy placement, D9=PAUSE PR #133 apply, D10=D11=OUT OF SCOPE).
3. **PR #133 dry-run merge** (optional per D8) — bc-core scripts + artifacts land on bc-core main as inventory/snapshot tooling. Not required for Phase A1.
4. **Optional: PR #133 hygiene patch** (the 3 diagnostic-clarity findings from the PR #133 review).
5. **Phase A1 DBCP authored + accepted** — `bcf.*` schema creation + 4 evidence table DDL. Substrate-only; no data movement; no FK redirects yet.
6. **Phase A1 apply gate** — `CREATE SCHEMA bcf; CREATE TABLE bcf.panel_output_record …; CREATE TABLE bcf.authoring_panel_rejection_log …; CREATE TABLE bcf.calibration_event …; CREATE TABLE bcf.certification_record …`. Standard M-series dry-run + post-apply pattern.
7. **Phase A2 DBCP authored + accepted** — backfill plan for 3,568 authority-bearing BCF rows from `contract.*` to `bcf.*`. Smoke debt explicitly excluded.
8. **PR #133 apply gate execution** — retires 11 smoke rows from `contract.*` before Phase A2 migration runs (ordering: smoke debt out → authority rows migrate).
9. **PR #133 closeout doc** — bcf-authoring-test-row-cleanup-closeout.md on bc-docs-v3.
10. **Phase A2 apply gate** — 3,568-row data migration. Operator-authorized per-table or single-transaction.
11. **Phase A3 DBCP + apply** — BCF writers/readers flipped from `contract.*` to `bcf.*`. Service-code change.
12. **Phase A4 DBCP + apply** — freeze or retire the now-unused `contract.*` evidence tables. Soak period before this gate.
13. **Phase A5 DBCP + apply** — create `mcf.metric_authoring_panel_output_record`, redirect 5 mcf→contract FKs to mcf→mcf, update M5/M12/M12.5/M13/M14 design docs, rewrite M12 writer.
14. **M12 first-real-panel-run DBCP** — separately authored after Phase A5 lands. M12 writer now targets `mcf.metric_authoring_panel_output_record`. Real vendor adapter wiring OR operator-authored payload path (synthetic/replay disallowed per no-synthetic hard rule).
15. **M12 first real panel run** — operator-authorized; writes 1 row to `mcf.metric_authoring_panel_output_record` + 1 row to `mcf.metric_authoring_panel_run`.
16. **M12.5 first materialization** — operator-authorized; runs against the M12 panel run output.
17. **M13 first evaluation** — operator-authorized; runs against the M12.5 materialized MCV.
18. **M14 opening** — after M13 first evaluation closes.

Total elapsed time depends on operator authorization cadence; technical work is bounded but real. The five-phase Option A sequence is substantially more upfront work than Option B's single-DDL gate, but yields physical-boundary clarity that Option B's framework_code label cannot match.

## 14. Explicit non-scope statement (repeated for clarity)

This DBCP is **NOT MCF closeout amendment** — M13 closeout (`mcf-m13-implementation-closeout.md`) and M12.5 closeout (`mcf-m12-5-implementation-closeout.md`) are already locked at bc-docs-v3 main `0f42662` and are NOT amended by this DBCP. They remain accurate descriptions of code-live state at the time of merge. Phase A5 will require companion amendments to those closeouts (or successor closeout docs) to reflect the M12 writer's new target (`mcf.metric_authoring_panel_output_record`), but that work belongs to the Phase A5 gate, not this planning DBCP.

This DBCP is **NOT tenant-results cleanup or migration** — all per-tenant analytical substrate in `tbc_{slug}_dev` databases is preserved untouched. No tenant DB connection is opened by any of the planning probes.

This DBCP is **NOT legacy `metric.*` retirement** — the 16,820 rows in `metric.*` including the 2 active AR pilot KPIs are explicitly preserved. Their retirement belongs to a separate gate alongside M17 tenant-runtime migration per the M12 implementation closeout §9.

This DBCP is **NOT contract-chain retirement** — `contract.source_contract`, `admission_contract`, `canonical_*`, `observation_*`, `chain_status`, `chain_trace`, `mc_integrity_state`, `l_node_semantic_*` (~127,000 rows of active dev/pilot infrastructure) are explicitly preserved.

This DBCP **does NOT authorize any DDL or DML** — it is a planning artifact only. Execution requires separate operator-authorized gates (Phase 1 DDL gate; PR #133 apply gate).

## 15. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 |
| No DDL applied | ✓ |
| No DML applied | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| `bc-postgres` MCP `allow_write=false` throughout | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No tenant `tbc_{slug}_dev` DB connection opened | ✓ |
| PR #133 not modified | ✓ |
| No-synthetic hard rule respected (this DBCP retires existing synthetic debt; does not write new synthetic) | ✓ |

## 16. Sequencing decision summary

| Gate | Status | Blocked by | Next action |
|---|---|---|---|
| This DBCP (bc-docs-v3 PR) | open for operator review | operator decisions D1..D11 | merge after authorization |
| PR #133 dry-run merge | optional; open | none (D8 = optional) | merge if operator finds inventory tooling useful |
| PR #133 hygiene patch (optional) | not yet authored | optional | author if operator agrees |
| Phase A1 DBCP (`bcf.*` schema creation) | not yet authored | operator authorization of D2=A + D4 + D6 | author + small-DDL gate (CREATE SCHEMA + 4 CREATE TABLE) |
| Phase A2 DBCP (3,568-row migration) | not yet authored | Phase A1 ships | author after A1 lands |
| PR #133 apply gate execution | paused | Phase A1 + A2 designs accepted (D9) | execute after both designs accepted; ordering: smoke retirement → then A2 migration |
| Phase A2 apply gate | not yet authored | PR #133 apply ships | author after smoke retired |
| Phase A3 DBCP (BCF writers/readers flip) | not yet authored | Phase A2 apply ships | author after migration validated |
| Phase A4 DBCP (freeze/retire old `contract.*` evidence tables) | not yet authored | Phase A3 ships + soak period | author after operator-defined soak (min 7 days) |
| Phase A5 DBCP (MCF FK reconsideration + M12 writer flip) | not yet authored | Phase A4 ships | author after `contract.*` evidence tables frozen/retired |
| Policy placement DBCP (`contract.framework_policy`) | not yet authored; deferred per D7 | separate gate; not blocking Phases A1..A5 | author when operator chooses to place policy registry |
| PR #133 closeout | not yet authored | apply gate execution | author after smoke retirement |
| M12 first-real-panel-run DBCP | not yet authored | Phase A5 ships | author after MCF FK retargeting |
| First real M12 panel run | gated | M12 DBCP execution | requires real vendor adapter OR operator-authored payload; synthetic/replay disallowed |
| M12.5 first materialization | gated | M12 first run | downstream |
| M13 first evaluation | gated | M12.5 first materialization | downstream |
| M14 opening | gated | M13 first evaluation | downstream |

---

**End of DBCP. NOT EXECUTED. Operator authorization on §11 D1..D11 required before any next gate opens.**
