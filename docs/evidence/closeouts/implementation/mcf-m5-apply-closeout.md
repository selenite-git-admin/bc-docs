---
uid: mcf-m5-apply-closeout
title: MCF M5 Panel Substrate — Live DDL Apply Closeout
description: Closeout for the MCF M5 Panel Substrate live DDL apply against bc_platform_dev on 2026-05-27. Applied docker/redesign/08-mcf-panel-substrate.sql (DDL pinned at bc-core PR #112 / 1ff695b; sha256 18e1af9c443781e92eb87a0a29dc7d337ff3d0675a18f37207ac775ab7d09d28) under explicit operator approval per CLAUDE.md Database Change Protocol. Realizes D-M5-B hybrid composition per M5 DBCP (bc-docs-v3 00435c0) with all 10 operator approvals O-M5-1..O-M5-10. Substrate change: 4 new mcf-owned tables (mcf.metric_authoring_panel_run + mcf.metric_authoring_panel_transcript + mcf.workspace_tool_allowlist + mcf.evidence_source_allowlist; ~30 columns total), 7 indexes (3 CREATE INDEX + 4 CREATE UNIQUE INDEX), 1 trigger function (mcf.fn_mapt_immutability_check) + 1 trigger attachment (trg_mapt_immutability BEFORE UPDATE OR DELETE), 3 deferred FK activations (fk_mcr_panel_run + fk_mper_panel_run + fk_mcs_panel_run → contract.panel_output_record per M3 cert-amendment precedent), 1 in-place jsonb-merge UPDATE on contract.framework_policy mcf_v1 adding panel_discipline sub-key (preserves existing consensus keys). Transcript FK target = mcf.metric_authoring_panel_run per M-M5-1 patch — substrate-enforces MCF-only attachment, blocking transcript-orphan to BCF / non-MCF panel runs. Dry-run all 8 preconditions PASS including 4 HARD-GATEs (M7/M8 prereq, new tables absent, new FKs absent, policy clean) + pre-extension policy snapshot captured for rollback safety. psql exit 0 inside BEGIN/COMMIT whole-file transaction wrapper per §14.2 atomicity discipline. Initial post-apply verifier (2026-05-27T10-39-03-405Z) exited 13 due to test-methodology bug in check #11 — multiple negative assertions ran sequentially in one sql.begin(tx) block; once the UPDATE raised check_violation, postgres aborted the entire tx so subsequent DELETE + UNIQUE returned 'transaction aborted' rather than the trigger/UNIQUE rejection messages, producing false-negatives. Substrate correctness confirmed independently via SAVEPOINT-protected docker exec psql test (TEST1 DELETE / TEST2 UPDATE / TEST3 duplicate INSERT all rejected with exact expected error messages). Verifier patched via bc-core PR #113 (SAVEPOINT-wrap each negative assertion; merged as 10e8b95). Clean post-apply rerun from main 10e8b95 (2026-05-27T10-47-51-470Z) exit 0 / 14/14 PASS. Live state post-apply: 14 mcf.* tables (10 prior + 4 new M5), all empty; mcf_v1 policy carries new panel_discipline sub-key with 5 fields (workbench_fingerprint_algorithm_name='mcf-workbench-fp', _version='v1', defect_code_registry_version='v1', transcript_retention_policy.retention_mode='indefinite', allowlist_version_pinning.{tool,evidence_source}_allowlist_mode='active_at_run_time'); existing consensus keys (models_required=3, agreement_threshold=2, models=[maker,checker,moderator]) preserved; M4 seeds intact; BCF concept_registry.* + contract.panel_output_record 24 BCF rows + contract.authoring_panel_rejection_log all untouched. M5 substrate now LIVE and DORMANT — substrate accepts panel-attested authoring but no panel exists; M11 ingestion + M12 panel implementation are next blocked gates. 6 basis-of-apply artifacts committed to bc-core via PR #114 (4 dry-run + 2 clean post-apply; initial-failed post-apply at 10-39 + intermediate review dry-run at 10-24 deliberately excluded). No real MCF metric contracts authored. No BCF touches. No M9/M10/M11+ gates opened.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m5-apply-closeout
---

# MCF M5 Panel Substrate — Live DDL Apply Closeout

## 1. What landed

The MCF M5 Panel Substrate DDL was applied live against `bc_platform_dev` on **2026-05-27**, completing the substrate side of the M5 arc. The DDL ships **4 new mcf-owned tables** (`mcf.metric_authoring_panel_run` + `mcf.metric_authoring_panel_transcript` + `mcf.workspace_tool_allowlist` + `mcf.evidence_source_allowlist`), **7 indexes** (3 `CREATE INDEX` + 4 `CREATE UNIQUE INDEX`), **1 trigger function + attachment** (`mcf.fn_mapt_immutability_check` + `trg_mapt_immutability` BEFORE UPDATE OR DELETE), **3 deferred FK activations** (`fk_mcr_panel_run` + `fk_mper_panel_run` + `fk_mcs_panel_run` → `contract.panel_output_record(panel_run_uid)` ON DELETE RESTRICT — matches live `fk_mcf_cert_panel_run` precedent wired by M3 cert-amendment), and **1 in-place jsonb-merge UPDATE** on `contract.framework_policy mcf_v1` adding the `panel_discipline` sub-key.

The transcript FK target is `mcf.metric_authoring_panel_run` (NOT `contract.panel_output_record`) per the M-M5-1 review patch — substrate now enforces MCF-only attachment so transcripts cannot orphan to BCF or non-MCF panel runs.

M2 + M3 + M4 + M7/M8 substrate stays applied throughout (no DROP/RECREATE; no touches to existing mcf.* tables apart from the 3 FK activations; no changes to BCF `concept_registry.*` or to existing `contract.panel_output_record` 24 BCF rows).

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/08-mcf-panel-substrate.sql` |
| Rollback source | `bc-core/docker/redesign/08-mcf-panel-substrate-rollback.sql` |
| Pinned at | bc-core PR #112 / squash commit `1ff695b` (HEAD of `main` at apply time) |
| DDL sha256 | `18e1af9c443781e92eb87a0a29dc7d337ff3d0675a18f37207ac775ab7d09d28` |
| Rollback sha256 | `81b5401c1456f28a9c428c7d64bbc36fdf291ecac6015848a5b75bcf27476724` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + M5 preflight (`bc-docs-v3 6e46d77`) + M5 DBCP (`bc-docs-v3 00435c0` — operator-accepted D-M5-1..D-M5-10) |
| Operator approval | Explicit "Approved, apply M5 panel substrate" in conversation per CLAUDE.md Database Change Protocol |
| Verifier patch | bc-core PR #113 / commit `10e8b95` (post-apply check #11 SAVEPOINT-wrap fix) — merged before clean-evidence rerun |
| Evidence PR | bc-core PR #114 (6 basis-of-apply artifacts: 4 dry-run + 2 clean post-apply; initial-failed post-apply + intermediate review-session dry-run excluded with rationale) |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m5-dry-run.mjs` | **exit 0** — 8/8 PASS; DDL sha256 captured; pre-extension `mcf_v1.consensus_requirement_json` snapshot saved for rollback safety per §16.3 |
| Live apply | `cat docker/redesign/08-mcf-panel-substrate.sql \| docker exec -i bc-postgres psql -U barecount -d bc_platform_dev -v ON_ERROR_STOP=1` | **exit 0** — inside `BEGIN;...COMMIT;` whole-file transaction wrapper (per §14.2 + M3-cert-amendment + M7/M8 atomicity pattern): BEGIN → 4 CREATE TABLE → 7 CREATE INDEX → CREATE FUNCTION → CREATE TRIGGER → 3 ALTER TABLE → UPDATE 1 → 4 COMMENT → COMMIT |
| Initial post-apply verifier | `node scripts/mcf-m5-post-apply-verification.mjs` | **exit 13** — check #11 false-negative (see §4.1 below); substrate confirmed correct via independent test |
| Verifier-fix PR #113 | bc-core impl PR + merge | `5c6362f` → merged squash `10e8b95` (SAVEPOINT-wrap fix on `scripts/mcf-m5-post-apply-verification.mjs` check #11 only) |
| Clean post-apply verifier (from main `10e8b95`) | same script post-fix | **exit 0** — **14/14 PASS** (basis-of-apply evidence) |

### 2.1 Dry-run 8-check summary (all PASS)

**4 HARD-GATEs + 4 advisory:**

1. M7/M8 substrate prereq — all 10 mcf.* tables + `formula_ast_canonical_json` column present (HARD-GATE)
2. None of 4 new M5 tables exist (HARD-GATE — clean slate)
3. 3 deferred FKs absent + `fk_mcf_cert_panel_run` regression present (HARD-GATE)
4. `mcf_v1.consensus_requirement_json` does NOT yet contain `panel_discipline` (HARD-GATE — clean slate for in-place UPDATE)
5. All MCF tables empty (advisory)
6. `contract.panel_output_record` present (FK target); 24 BCF rows recorded as untouched (advisory)
7. Forward DDL parse + statement counts (4 CREATE TABLE + 7 indexes = 3+4 per M-M5-2 + 1 fn + 1 trg + 3 FK ALTERs + 1 policy UPDATE + 4 COMMENT + BEGIN/COMMIT)
8. DDL sha256 + pre-extension policy snapshot captured

### 2.2 Clean post-apply 14-check summary (all PASS, from main `10e8b95`)

**Structural (1–8):**

1. `mcf.metric_authoring_panel_run` — 8 cols + 3 CHECKs (2 byte-match + 1 semantic-equivalence on multi-line all-or-none per §15.4 M-M5-3) + 1 FK to `contract.panel_output_record` + 2 indexes
2. `mcf.metric_authoring_panel_transcript` — 6 cols + 1 CHECK + 1 FK to `mcf.metric_authoring_panel_run` (per M-M5-1) + 1 UNIQUE + 1 index + trigger attached
3. `mcf.workspace_tool_allowlist` — 6 cols + 1 CHECK + 2 UNIQUE indexes
4. `mcf.evidence_source_allowlist` — 6 cols + 1 CHECK + 2 UNIQUE indexes
5. 3 deferred FKs active (`fk_mcr_panel_run` + `fk_mper_panel_run` + `fk_mcs_panel_run`) all targeting `contract.panel_output_record(panel_run_uid)`
6. `fk_mcf_cert_panel_run` STILL present (regression on M3 cert-amendment)
7. `mcf_v1.consensus_requirement_json` extended in-place; pre-extension keys preserved (`models_required=3`, `agreement_threshold=2`, `models=[maker,checker,moderator]`) + new `panel_discipline` with 5 sub-keys
8. Trigger function `mcf.fn_mapt_immutability_check` + `trg_mapt_immutability` BEFORE UPDATE OR DELETE attached

**Behavioral (9–13) — SAVEPOINT-protected synthetic-row exercises:**

9. 1:1 composition INSERT (contract row + mapr row) succeeds + rolls back
10. mapr INSERT without contract row → REJECTED by `fk_mapr_panel_run`
11. Transcripts INSERT + UPDATE/DELETE/UNIQUE rejections (3 negative assertions each in own SAVEPOINT per M-M5-1 verifier patch; trigger rejects UPDATE + DELETE; `uq_mapt_run_role` rejects duplicate)
12. Transcript orphan (contract row exists, no mapr) → REJECTED by `fk_mapt_panel_run` (substrate-enforces MCF-only attachment per M-M5-1)
13. PE-result INSERT with bogus `panel_run_uid` → REJECTED by `fk_mper_panel_run`

**Cleanup (14):**

14. All 14 MCF tables empty after verifier completes (rollback discipline preserved across all 5 behavioral exercises)

## 3. Live state recap (post-apply)

### 3.1 What's now live

| Surface | Change |
|---|---|
| `mcf.metric_authoring_panel_run` | NEW — 8 cols; 1:1 PK FK to `contract.panel_output_record`; workbench fingerprint hash + reservoir-provenance fields (per addendum guardrail #6, nullable until M11) + reservoir all-or-none CHECK |
| `mcf.metric_authoring_panel_transcript` | NEW — 6 cols; FK to `mcf.metric_authoring_panel_run` per M-M5-1; UNIQUE `(panel_run_uid, model_role_code)`; append-only via trigger |
| `mcf.workspace_tool_allowlist` | NEW — versioned MCF tool registry; `effective_from`/`effective_to`; partial UNIQUE active-per-code |
| `mcf.evidence_source_allowlist` | NEW — versioned MCF evidence source registry (mirrors tool allowlist) |
| `mcf.fn_mapt_immutability_check` + `trg_mapt_immutability` | NEW — unconditional UPDATE/DELETE reject on transcript rows per D-M5-8 / MCF §11.3 + Invariant V |
| `fk_mcr_panel_run` on `mcf.metric_contract_revision` | NEW — activates deferred FK to `contract.panel_output_record` |
| `fk_mper_panel_run` on `mcf.metric_publication_eligibility_result` | NEW — activates deferred FK to `contract.panel_output_record` |
| `fk_mcs_panel_run` on `mcf.metric_supersession` | NEW — activates deferred FK to `contract.panel_output_record` |
| `contract.framework_policy mcf_v1` `consensus_requirement_json` | EXTENDED in-place via jsonb merge — adds `panel_discipline` sub-key with 5 fields (algorithm name/version, registry version, transcript retention, allowlist pinning); existing consensus keys preserved |
| Drizzle schemas | LIVE: 4 new files in `bc-core/src/database/schema/mcf/` + 3 modified (comment-only updates documenting new FKs per cross-schema-DDL-only repo convention) |

### 3.2 Independent bc-postgres MCP read-only confirmation (`allow_write=false`)

| Check | Result |
|---|---|
| 4 M5 tables present | **4** ✅ |
| 3 deferred FKs present | **3** ✅ |
| Transcript FK target | **`mcf.metric_authoring_panel_run`** ✅ (M-M5-1 verified live) |
| `mcf_v1.consensus_requirement_json.panel_discipline` present | **true** ✅ |
| Algorithm version pinned | **`v1`** ✅ |
| All 14 MCF tables row counts | **0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0** ✅ (10 prior empty + 4 new empty) |
| M4 seeded `contract.framework_policy` scope=mcf rows | **1** (`mcf_v1`) ✅ intact |
| M4 seeded `contract.operator_confirm_rule` scope=mcf rows | **2** ✅ intact |
| BCF `concept_registry.*` | **untouched** — `business_concept` 10 rows; `entity` 2 rows |
| `contract.panel_output_record` rows (BCF) | **24** untouched |
| `contract.authoring_panel_rejection_log` CHECKs | **untouched** — `scope_code` / `primitive_type` / `defect_code` BCF-specific enums preserved (no MCF extension per D-M5-7) |

### 3.3 What remains empty / closed

- All 14 `mcf.*` tables remain at **0 rows** — no real MCF metric contracts authored, no panel runs, no transcripts, no allowlist seed rows
- 4 new tables created but empty (substrate accepts authoring, no service writes yet)
- The new `panel_discipline` policy sub-key carries algorithm/registry/retention/allowlist metadata used by M12 (which doesn't yet exist)
- BCF `contract.authoring_panel_rejection_log` BCF-specific CHECKs untouched per D-M5-7 (MCF defect detail lives in `mcf.metric_authoring_panel_run.consensus_payload_json` instead)
- `contract.panel_output_record.verdict_payload_json` defect-code CHECK untouched per D-M5-7

## 4. Operational observations (new this session)

### 4.1 Initial post-apply verifier #11 false-negative + substrate independent-verification path

The initial post-apply verifier (`2026-05-27T10-39-03-405Z`) exited 13. Check #11 reported `update_rejected=true delete_rejected=false unique_rejected=false`. Root cause: the original implementation ran all 3 negative assertions (UPDATE, DELETE, duplicate-INSERT) sequentially inside ONE `sql.begin(async (tx) => {...})` block. When the first negative (UPDATE) raised `check_violation`, postgres marked the tx as failed; subsequent DELETE + duplicate-INSERT returned **"current transaction is aborted, commands ignored until end of transaction block"** — NOT the trigger/UNIQUE rejection messages the script's `try/catch` substring checks expected.

The substrate was correct. Confirmed via SAVEPOINT-protected docker exec psql test that ran the same 3 assertions each in their own SAVEPOINT scope:

```
TEST1_PASS: DELETE rejected with check_violation (mcf.metric_authoring_panel_transcript transcript_uid=... is immutable; DELETE rejected (per DBCP M5 §13 + Invariant V))
TEST2_PASS: UPDATE rejected with check_violation (... is immutable; UPDATE rejected ...)
TEST3_PASS: duplicate role INSERT rejected with unique_violation (duplicate key value violates unique constraint "uq_mapt_run_role")
```

This pattern (independent SAVEPOINT-protected verification when the verifier surfaces a tx-aborted false-negative) is a reusable diagnostic recipe for future negative-test verifier failures. **Reference for future apply gates: when a verifier reports negative-test false-negatives, run the same assertions in SAVEPOINT-isolated DO blocks via docker exec psql before deciding whether the substrate is faulty.**

### 4.2 Verifier-fix landed before evidence regeneration

Verifier-fix PR #113 (SAVEPOINT-wrap on check #11; isolated `tx.savepoint(...)` around each of the 3 negative assertions; captures actual rejection messages in `recordCheck` details for stronger audit evidence) merged as `10e8b95` before the clean post-apply rerun. The clean post-apply (`2026-05-27T10-47-51-470Z`) ran from main `10e8b95` and exited 0 with 14/14 PASS. The evidence PR (#114) therefore ships the **clean** post-apply artifacts as basis-of-evidence, with the initial-failed run deliberately excluded and the exclusion rationale documented in both the evidence PR body and this closeout's §1 table.

### 4.3 jsonb-merge in-place policy extension validated against live policy

The policy extension via `consensus_requirement_json || '{"panel_discipline": {...}}'::jsonb` correctly preserved the 3 pre-existing top-level keys (`models_required`, `agreement_threshold`, `models`) and added `panel_discipline` as a new top-level key. Post-apply verifier check #7 asserts both — preserved keys at expected values AND new key with all 5 sub-keys at expected values — all PASS. The `UPDATE 1` row count in the psql output confirms exactly one row mutated (the seeded `mcf_v1 / 1.0.0` policy).

## 5. Evidence artifacts (committed to bc-core via PR #114)

**6 basis-of-apply artifacts** explicitly staged from `bc-core/scripts/audit-output/` (no bulk-add):

| # | File | Bytes | Purpose |
|---|---|---|---|
| 1 | `mcf-m5-dry-run-2026-05-27T10-36-44-698Z.summary.md` | — | Human-readable dry-run verdict (8/8 PASS) |
| 2 | `mcf-m5-dry-run-2026-05-27T10-36-44-698Z.precondition.jsonl` | — | Machine-readable per-check JSONL |
| 3 | `mcf-m5-dry-run-2026-05-27T10-36-44-698Z.planned-sql.sha256.txt` | — | Forward + rollback DDL byte fingerprints |
| 4 | `mcf-m5-dry-run-2026-05-27T10-36-44-698Z.pre-extension-policy.json` | — | Pre-extension `mcf_v1.consensus_requirement_json` snapshot for rollback safety per DBCP §16.3 |
| 5 | `mcf-m5-post-apply-2026-05-27T10-47-51-470Z.summary.md` | — | **Clean post-apply** 14/14 PASS verdict (rerun from main `10e8b95` post verifier-fix) |
| 6 | `mcf-m5-post-apply-2026-05-27T10-47-51-470Z.evidence.jsonl` | — | Machine-readable per-check JSONL |

**Deliberately excluded:**

- Initial post-apply run `2026-05-27T10-39-03-405Z` (exit 13 due to verifier methodology bug; superseded by clean rerun after PR #113)
- Intermediate dry-run `2026-05-27T10-24-38-765Z` (review-session diagnostic dry-run, not the apply-session basis-of-apply)
- All other untracked files in `scripts/audit-output/` (M3/M4/M7-M8/D408/D409/D418 artifacts)

## 6. What stays closed (subsequent gates — not evidenced here)

| Gate | Status |
|---|---|
| **M9 fixture substrate** | CLOSED — parallel-eligible per build plan (no M5 dependency); gated on operator authorization |
| **M10 deterministic verifier service** | CLOSED — gated on M9 |
| **M11 reservoir ingestion service** | CLOSED — gated on M5 (now unblocked at substrate level) + operator authorization |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M5 + M7 + M10 + M11 |
| **M13 PE-MC evaluator** | CLOSED — gated on M5 + M7 + M9 + M10 |
| **M14 / M15 publication / supersession paths** | CLOSED — gated on M4 + M5 + M13 |
| **M16 / M17 operator console** | CLOSED — gated on M12 + M14 |
| **Real MCF metric contracts** | CLOSED — substrate accepts panel-attested authoring but no panel exists; M11 + M12 must ship first |
| **BCF data changes** | CLOSED — untouched throughout MCF arc |
| **`contract.authoring_panel_rejection_log` extensions** | CLOSED per D-M5-7 — table stays BCF-specific by architectural choice |
| **`contract.panel_output_record.verdict_payload_json` defect-code CHECK extension** | CLOSED per D-M5-7 |
| **NF1 tightening on `mcf.certification_record`** | DEFERRED per D-M5-10 — no NF1 change in M5; future amendment if operator selects production tightening |
| **MCF defect-code v2 taxonomy** | CLOSED — v1 registry pinned via `mcf_v1.consensus_requirement_json.panel_discipline.defect_code_registry_version='v1'`; v2 requires policy bump |
| **MCF tool/evidence allowlist v1 seed rows** | CLOSED — M5 ships only the substrate; specific tool/source list is M12 |

## 7. Source-of-truth references

- DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m5-panel-substrate-dbcp.md` (`00435c0`)
- Preflight: `bc-docs-v3/docs/implementation/metric-context-framework-m5-panel-substrate-preflight.md` (`6e46d77`)
- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422)
- M7/M8 apply closeout: `bc-docs-v3/docs/implementation/mcf-m7-m8-apply-closeout.md` (`6b3ffb2`)
- M4 apply closeout: `bc-docs-v3/docs/implementation/mcf-m4-ddl-apply-closeout.md` (`c2bc3fc`)
- M3 cert-amendment closeout: `bc-docs-v3/docs/implementation/mcf-m3-cert-amendment-apply-closeout.md` (`60efd9d`)
- Implementation PR: bc-core #112 (squash `1ff695b`)
- Verifier-fix PR: bc-core #113 (squash `10e8b95`)
- Evidence PR: bc-core #114
- DDL sha256: `18e1af9c443781e92eb87a0a29dc7d337ff3d0675a18f37207ac775ab7d09d28`
- Rollback sha256: `81b5401c1456f28a9c428c7d64bbc36fdf291ecac6015848a5b75bcf27476724`

## 8. Discipline summary

- ✅ Apply executed under explicit operator approval per CLAUDE.md DCP
- ✅ Whole-file `BEGIN/COMMIT` atomicity per §14.2 (all 6 steps commit together)
- ✅ Pre-extension policy snapshot captured for rollback safety per §16.3
- ✅ Post-apply verifier 14/14 PASS independently confirmed via bc-postgres MCP (`allow_write=false`)
- ✅ Initial verifier false-negative diagnosed + substrate independently verified via SAVEPOINT-protected docker exec psql test
- ✅ Verifier-fix landed before evidence regeneration; clean basis-of-apply produced from merged main
- ✅ NO bc-core source changes in evidence PR (audit artifacts only)
- ✅ NO further DDL apply or rollback this session
- ✅ NO real MCF metric contracts created
- ✅ NO BCF touches
- ✅ NO M9 / M10 / M11+ gates opened
- ✅ M5 substrate is now **live** and **dormant**; M11 reservoir ingestion service + M12 Metric Authoring Panel implementation + M9 fixture substrate are next blocked gates awaiting separate operator authorization
