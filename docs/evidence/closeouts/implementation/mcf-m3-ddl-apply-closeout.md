---
uid: mcf-m3-ddl-apply-closeout
title: MCF M3 Lifecycle / Immutability Substrate — Live DDL Apply Closeout
description: Closeout for the MCF M3 Lifecycle / Immutability Substrate live DDL apply against bc_platform_dev on 2026-05-26. Applied docker/redesign/05-mcf-lifecycle-substrate.sql (DDL pinned at bc-core PR #103 / 1a9796d; sha256 b858e6532e2ed948f91609885a519f5bd8588a50530feac347ce07b86dc2d33a) under explicit operator approval per CLAUDE.md Database Change Protocol. Dry-run all 8 preconditions PASS; psql exit 0; post-apply verifier all 14 checks PASS including positive + negative trigger exercises (state-graph forward-only, hash NOT-NULL gate, child-table immutability when parent past-draft). Two new mcf tables (metric_contract_revision, metric_supersession), 7 trigger functions, 7 triggers — all live and empty. Evidence artifacts committed to bc-core via PR #104. M3 substrate is operationally dormant until M4 cert writer / lifecycle transition authority ships. No BCF data touched, no MCF metric contracts created, no certification rows written.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m3-apply-closeout
---

# MCF M3 Lifecycle / Immutability Substrate — Live DDL Apply Closeout

## 1. What landed

The MCF M3 Lifecycle / Immutability Substrate DDL was applied live against `bc_platform_dev` on **2026-05-26**, immediately following the M2 apply closeout (`mcf-m2-ddl-apply-closeout.md`). The substrate (2 new tables + 7 trigger functions + 7 triggers + indexes + comments under the existing `mcf` schema) is now physically present and behaviorally validated — both correct paths and rejected paths were exercised by the post-apply verifier.

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` |
| Pinned at | bc-core PR #103 / commit `1a9796d` (HEAD = origin/main) |
| DDL sha256 | `b858e6532e2ed948f91609885a519f5bd8588a50530feac347ce07b86dc2d33a` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + M3 DBCP design doc `metric-context-framework-m3-lifecycle-substrate-dbcp.md` (`3147bd4` patched by `938fb0f`) |
| Q1 decision | `approved` state is **LOCKED** — no descriptive mutation; only the approved→active state transition itself is permitted |
| Operator approval | Explicit "Approved, apply M3 live DDL to local bc_platform_dev" in conversation per CLAUDE.md Database Change Protocol |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m3-dry-run.mjs` | **exit 0** — 8/8 preconditions PASS (M2 substrate present, M3 tables absent, M3 functions absent, M3 triggers absent, cert table columns present, DDL parse + counts + hash, schema-qualification audit) |
| Live apply | `psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f docker/redesign/05-mcf-lifecycle-substrate.sql` | **exit 0** — 34 statements executed (7 CREATE FUNCTION + 2 CREATE TABLE + 6 CREATE INDEX (incl. 2 UNIQUE) + 7 CREATE TRIGGER + 12 COMMENT) |
| Post-apply verify | `node scripts/mcf-m3-post-apply-verification.mjs` | **exit 0** — 14/14 checks PASS |

### 2.1 Post-apply 14-check summary (all PASS)

**Structural (1–7):**
1. `mcf.metric_contract_revision` present with 9 columns
2. `mcf.metric_supersession` present with 11 columns
3. 5 CHECK constraints present (`mcr_revision_kind_chk`, `mcr_revision_seq_chk`, `mcs_correction_class_chk`, `mcs_different_mc_chk`, `mcs_rationale_min_length_chk`)
4. 6 FK constraints present (1 on `metric_contract_revision` + 5 on `metric_supersession` including the cross-schema `fk_mcs_cert` → `contract.certification_record`)
5. 6 new indexes present (3 on `metric_contract_revision` + 3 on `metric_supersession`)
6. 7 trigger functions present (`fn_mcv_state_transition_check`, `fn_mc_active_immutability_check`, `fn_mcv_descriptive_immutability_check`, `fn_mvb_active_immutability_check`, `fn_mfc_active_immutability_check`, `fn_mcdr_active_immutability_check`, `fn_mcv_revision_emit`)
7. 7 triggers attached (3 on `metric_contract_version`, 1 on `metric_contract`, 3 on child tables `metric_variable_binding` / `metric_filter_clause` / `metric_computed_dimension_ref`)

**Behavioral (8–13) — positive + negative trigger exercises:**

| # | Path | Expectation | Actual |
|---|---|---|---|
| 8 | INSERT `metric_contract_version` with `governance_state_code = 'draft'` | succeeds | succeeds |
| 9 | INSERT `metric_contract_version` with `governance_state_code = 'active'` | rejected — "new rows must start at draft" | rejected with exact message |
| 10 | UPDATE state `draft → review` | succeeds | succeeds |
| 11 | UPDATE state `draft → approved` (skip review) | rejected — "invalid mcf state transition" | rejected with exact message |
| 12 | UPDATE state `review → approved` without parent hashes | rejected — "requires all 6 hash columns NOT NULL on parent" | rejected with exact message |
| 13 | DELETE child `metric_variable_binding` row when parent version state = `approved` | rejected — "cannot be modified or deleted when parent version is in state approved" | rejected with exact message |

**Cleanup (14):**

14. All 7 `mcf.*` tables empty after verifier (test rows wrapped in a transaction and rolled back; substrate left clean for downstream)

### 2.2 Independent confirm (separate `bc-postgres pg_query`)

| Metric | Value |
|---|---|
| `mcf.*` tables | 7 |
| `mcf.*` trigger functions | 7 |
| Distinct triggers on `mcf.*` | 7 (raw 11 rows in `information_schema.triggers` — multi-event triggers like `BEFORE INSERT OR UPDATE OF` are listed once per event) |
| Total rows across all 7 `mcf.*` tables | 0 |

All counts match the DDL specification and the verifier output from an independent query path.

## 3. Evidence

Audit artifacts committed to bc-core via [PR #104](https://github.com/selenite-git-admin/bc-core/pull/104) under `scripts/audit-output/`:

- `mcf-m3-dry-run-2026-05-26T14-51-09-700Z.summary.md` + `.precondition.jsonl` + `.planned-sql.sha256.txt`
- `mcf-m3-post-apply-2026-05-26T14-56-10-757Z.summary.md` + `.evidence.jsonl`

The post-apply summary contains the full per-check JSON for downstream audit. The DDL hash file (`.planned-sql.sha256.txt`) pins what was applied for future drift detection.

**Excluded from the evidence PR:** three earlier dry-run runs from 14:03 / 14:06 / 14:30 (same calendar day, generated during the PR #103 implementation session before this apply gate opened). They are pre-apply experimentation, not the basis-of-apply. The audit trail points cleanly to the single 14:51:09 → 14:56:10 pair that authorized this apply.

## 4. Operational observations

The operational observations from the M2 closeout (`mcf-m2-ddl-apply-closeout.md` §4) — psql client at `C:\Program Files\PostgreSQL\18\bin\psql.exe`, bc-postgres MCP schema-cache lag, PowerShell `.env`-sourcing pattern — all carried over without change. Two new observations:

### 4.1 Verifier transaction discipline (positive property)

The post-apply verifier uses a transactional INSERT-then-ROLLBACK pattern for its trigger exercises (#8–#13). Verifier check #14 confirms all 7 `mcf.*` tables are empty *after* the verifier runs, proving the rollback is clean. This is a useful property to preserve for future substrate verifiers — the script can be re-run any number of times against an empty substrate without leaving state behind.

### 4.2 Multi-event triggers — `information_schema.triggers` row count

`mcf` has 7 distinct triggers but `SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_schema='mcf'` returns 11, because multi-event triggers (`BEFORE INSERT OR UPDATE OF ...` and `BEFORE UPDATE OR DELETE ON ...`) are listed once per event manipulation:

| Trigger | Events | Rows |
|---|---|---|
| `trg_mcf_mcv_state_transition` | INSERT, UPDATE OF governance_state_code | 2 |
| `trg_mcf_mc_active_immutability` | UPDATE | 1 |
| `trg_mcf_mcv_descriptive_immutability` | UPDATE | 1 |
| `trg_mcf_mcv_revision_emit` | UPDATE | 1 |
| `trg_mcf_mvb_active_immutability` | UPDATE, DELETE | 2 |
| `trg_mcf_mfc_active_immutability` | UPDATE, DELETE | 2 |
| `trg_mcf_mcdr_active_immutability` | UPDATE, DELETE | 2 |
| **Total** | | **11 rows / 7 distinct names** |

Future verifiers and chain audits should query `COUNT(DISTINCT trigger_name)` when asserting "7 triggers attached", not raw row count.

## 5. What stays closed

- **MCF M4** — cert writer service + lifecycle transition authority (the operational layer that produces `contract.certification_record` rows with `action_code = 'metric_transition'` and `from_state_code = 'approved'` / `to_state_code = 'active'`). Until M4 ships, no metric contract version can legitimately reach `active` — the state-transition trigger will reject the approved→active UPDATE because the required cert row does not exist.
- **MCF metric contract authoring** — no rows in any `mcf.*` table. The M3 substrate is structurally and behaviorally validated against synthetic-then-rolled-back rows only.
- **Step-4-bis BCF enrichment** for Metrics 3 + 6 — independent workstream, not opened by this apply.
- **bc-postgres MCP write access** — `allow_write: false` confirmed across this session. The psql apply used the operator's own `DATABASE_URL` credential, not bc-postgres MCP.
- **M3 DDL further changes** — none. The merged PR #103 design held; no amendments were needed in dry-run or post-apply.
- **`contract.metric_contract*` / `metric.metric_binding`** — legacy tables remain historical-only per D422 Decision 2; M3 added no FK to them.

## 6. MCF substrate arc — running tally

| Gate | Artifact | Date | State after |
|---|---|---|---|
| M1 — ADR | DEC-c3e57f / D422 (`bc-docs-v3/docs/adrs/ADR-c3e57f.md`) | 2026-05-26 | Authority locked |
| M2 — Identity substrate (DDL) | bc-core PR #101 / `92a9056` | 2026-05-26 | Code on main; not applied |
| M2 — Identity substrate (apply) | bc-core PR #102 / bc-docs-v3 `mcf-m2-ddl-apply-closeout.md` | 2026-05-26 | 5 mcf tables live + empty |
| M3 — Lifecycle preflight | bc-docs-v3 `9e472cb` | 2026-05-26 | 13 decisions framed |
| M3 — Lifecycle DBCP (design) | bc-docs-v3 `3147bd4` patched by `938fb0f` | 2026-05-26 | Q1 LOCKED + 5 clarity fixes |
| M3 — Lifecycle substrate (DDL) | bc-core PR #103 / `1a9796d` | 2026-05-26 | Code on main; not applied |
| **M3 — Lifecycle substrate (apply)** | **bc-core PR #104 + this doc** | **2026-05-26** | **7 mcf tables live + empty; 7 triggers attached; substrate dormant pending M4** |

Two same-day apply gates (M2 + M3) caps the MCF substrate landing arc through M3. The 8 of 10 representative metrics from the BCF-to-MCF readiness handoff (`bc-docs-v3 1d73308` §6) now have substrate to be authored into, and the lifecycle guarantees needed to author them safely are now enforced at the database layer.

## 7. Recommended next gate

Per the apply-gate conversation, two distinct next tracks exist:

1. **MCF M4 — cert writer service + lifecycle transition authority.** The substrate-level layer that produces `contract.certification_record` rows for `metric_create` (at intake → draft, service-only) and `metric_transition` (at approved → active, substrate-checked by `trg_mcf_mcv_state_transition`). Until M4 ships, no version can reach `active`. This is the **next functional MCF gate** — without it, M3 sits dormant.
2. **Step-4-bis BCF enrichment** for Metrics 3 + 6 — broadens the first metric authoring batch from 8 to 10 of the 10 representative metrics. Independent of M4; parallelizable.

This closeout does **NOT** open either gate. The choice is operator-controlled.

## Document verification

- **Apply event captured** — DDL source, sha256, target DB, authority, operator approval pattern.
- **All three apply steps recorded** with exit codes — dry-run / live psql / post-apply verifier all exit 0.
- **All 14 post-apply checks PASS** — itemized in §2.1, including the 6 positive + negative trigger exercises and the rollback-cleanup property.
- **Independent confirm captured** (§2.2) — 7 tables / 7 functions / 7 distinct triggers / 0 rows via a separate `pg_query` path.
- **Operational observations preserved** (§4) — verifier rollback discipline, multi-event trigger row counts in `information_schema.triggers`.
- **No code changes, no further DDL, no row writes.** This doc only.
- **Closed gates restated** (§5) — M4 + MCs + Step-4-bis + bc-postgres write + DDL amendments + legacy `contract.metric_contract*` all stay closed.
