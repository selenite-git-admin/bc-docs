---
uid: mcf-m9-apply-closeout
title: MCF M9 Self-Verification Fixture Substrate — Live DDL Apply Closeout
description: Closeout for the MCF M9 Self-Verification Fixture Substrate live DDL apply against bc_platform_dev on 2026-05-27. Applied docker/redesign/09-mcf-fixture-substrate.sql (DDL pinned at bc-core PR #115 squash cd31cb1; sha256 70e0952522edcabc651e16dc89181efe748ba7f3df0cd113824f6ad06df30bf8) under explicit operator approval per CLAUDE.md Database Change Protocol. Realizes D-M9-B single mcf-owned fixture registry table per M9 DBCP (bc-docs-v3 620e11d) with all 9 operator approvals O-M9-1..O-M9-9. Substrate change ALL IN ONE NEW TABLE — mcf.metric_self_verification_fixture (16 columns; 12 constraints — 1 PK + 3 intra-mcf FK fk_msvf_mc/fk_msvf_mcv/fk_msvf_panel_run all ON DELETE RESTRICT + 7 CHECK 5 sha256-format + 1 algo-version regex + 1 rationale-length ≥40 + 1 UNIQUE on (metric_contract_version_uid, self_verification_fixture_hash)) + 3 indexes (lookup-by-mcv, lookup-by-bound-package-hash, lookup-by-panel-run) + 1 trigger function mcf.fn_msvf_immutability_check + 1 trigger attachment trg_msvf_immutability BEFORE UPDATE OR DELETE (M3/M5-style unconditional reject post-INSERT per operator design constraint). Five hashes per fixture row formula_intent_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash (3 M7/M8 snapshots) + self_verification_fixture_hash (NEW M9; sha256 over canonical Section A+B+C JCS bytes) + bound_package_signature_hash (snapshot at fixture-bind time per §12.7 stale-fixture rule). Authoring boundary panel-only per D-M9-4 (panel_run_uid NOT NULL FK to mcf.metric_authoring_panel_run). Algorithm version mcf-hash-v1 reused per D-M9-A1 (M7/M8 forever-lock bundle). Dry-run all 8 preconditions PASS including 4 HARD-GATEs (M5+M7/M8 prereq + new table absent + trigger/function absent + 14 mcf.* tables empty) + DDL sha256 capture. psql exit 0 inside BEGIN/COMMIT whole-file transaction wrapper per §12.2 (BEGIN → CREATE TABLE → 3× CREATE INDEX → CREATE FUNCTION → CREATE TRIGGER → COMMENT → COMMIT). Post-apply 13-check verifier exit 0 / 13/13 PASS ON FIRST ATTEMPT — no verifier-fix patch cycle needed (the M1 byte-match + L2 3-FK-coverage + SAVEPOINT-protection improvements shipped in PR #115 cf9ba74 from the start, avoiding the M5-style false-negative recovery cycle that consumed an extra cycle in M5 apply). 7 CHECK predicates byte-matched against pg_get_constraintdef() per DBCP §15.2 (no multi-line CHECKs — semantic-equivalence carve-out from M5 §15.4 not needed). All 3 FKs behaviorally probed for rejection (mc + mcv + panel_run). All 5 negative assertions SAVEPOINT-wrapped from the start. Live state post-apply 15 mcf.* tables (10 pre-M5 + 4 M5 + 1 new M9), all empty; mcf.fn_msvf_immutability_check function present; trg_msvf_immutability trigger attached; 5 hash format CHECK predicates all byte-equal to expected pg_get_constraintdef() text; existing 24 contract.panel_output_record BCF rows + 1 contract.authoring_panel_rejection_log BCF row + M4 seeds + M5 mcf_v1.panel_discipline policy + M3/M7 triggers all UNTOUCHED. M9 substrate now LIVE and DORMANT — substrate accepts panel-attested fixture authoring but no panel exists; M9-engine impl PR (DBCP §18.1 items 5-8 — computeSelfVerificationFixtureHash helper + fixture-structural-check.service C-FX-1..C-FX-11 engine) + M10 verifier engine + M11 ingestion + M12 panel implementation are the next REQUIRED gates. 5 basis-of-apply artifacts committed to bc-core via PR #116 (3 dry-run + 2 post-apply); 4 stale intermediate dry-runs from pre-merge verification rounds (T12-01/T12-08/T12-20/T12-29) deliberately excluded per evidence discipline. No real MCF metric contracts authored. No fixture rows authored. No BCF touches. No M9-engine implementation. No M10/M11/M12 gates opened.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m9-apply-closeout
---

# MCF M9 Self-Verification Fixture Substrate — Live DDL Apply Closeout

## 1. What landed

The MCF M9 Self-Verification Fixture Substrate DDL was applied live against `bc_platform_dev` on **2026-05-27**, completing the substrate side of the M9 arc. The DDL ships **1 new mcf-owned table** (`mcf.metric_self_verification_fixture`), **3 indexes** (lookup-by-mcv, lookup-by-bound-package-hash, lookup-by-panel-run), **1 trigger function + attachment** (`mcf.fn_msvf_immutability_check` + `trg_msvf_immutability` BEFORE UPDATE OR DELETE — M3/M5-style unconditional UPDATE/DELETE reject post-INSERT per operator design constraint), and **1 COMMENT ON TABLE**.

The new table carries **16 columns** + **12 constraints** (1 PK + 3 intra-mcf FK on ON DELETE RESTRICT + 7 CHECK + 1 UNIQUE), and **5 hashes per row**:
- `formula_intent_hash` (M7/M8 snapshot)
- `variable_binding_set_hash` (M7/M8 snapshot)
- `grain_filter_temporal_dimension_signature_hash` (M7/M8 snapshot)
- `self_verification_fixture_hash` (NEW M9; sha256 over canonical Section A+B+C JCS bytes)
- `bound_package_signature_hash` (snapshot of `mcf.metric_contract.package_signature_hash` at fixture-bind time per §12.7 stale-fixture rule)

Algorithm version `mcf-hash-v1` reused per D-M9-A1 (M7/M8 forever-lock bundle). Authoring boundary panel-only per D-M9-4 (`panel_run_uid NOT NULL` FK to `mcf.metric_authoring_panel_run`).

M2 + M3 + M4 + M5 + M7/M8 substrate stays applied throughout (no DROP/RECREATE; no touches to existing mcf.* tables; no changes to BCF `concept_registry.*` or to existing `contract.panel_output_record` 24 BCF rows + 1 `contract.authoring_panel_rejection_log` row).

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/09-mcf-fixture-substrate.sql` |
| Rollback source | `bc-core/docker/redesign/09-mcf-fixture-substrate-rollback.sql` |
| Pinned at | bc-core PR #115 / squash commit `cd31cb1` (HEAD of `main` at apply time) |
| DDL sha256 | `70e0952522edcabc651e16dc89181efe748ba7f3df0cd113824f6ad06df30bf8` |
| Rollback sha256 | `04fb86a034f5d85549c51921f04294197686b44ad47343842d6d6c407724ebac` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + M9 preflight (`bc-docs-v3 686afc3`) + M9 DBCP (`bc-docs-v3 620e11d` — operator-accepted D-M9-1..D-M9-8, O-M9-1..O-M9-9) |
| Operator approval | Explicit "Approved, apply M9 fixture substrate" in conversation per CLAUDE.md Database Change Protocol |
| Verifier baseline | bc-core PR #115 cf9ba74 (post-M1/L2 patches; SAVEPOINT + 7-CHECK byte-match + 3-FK rejection shipped from start) — no verifier-fix patch cycle needed |
| Evidence PR | bc-core PR #116 (5 basis-of-apply artifacts: 3 dry-run + 2 post-apply; 4 stale intermediate dry-runs from pre-merge verification rounds excluded with rationale) |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m9-dry-run.mjs` | **exit 0** — 8/8 PASS; DDL sha256 captured. (Per DBCP §14: no pre-amendment artifact needed because M9 apply only CREATEs new objects — no UPDATE to revert, unlike M5 which snapshot `mcf_v1` policy for jsonb-subtract safety.) |
| Live apply | `cat docker/redesign/09-mcf-fixture-substrate.sql \| docker exec -i bc-postgres psql -U barecount -d bc_platform_dev -v ON_ERROR_STOP=1` | **exit 0** — inside `BEGIN;...COMMIT;` whole-file transaction wrapper (per §12.2 + M3-cert-amendment + M5 + M7/M8 atomicity pattern): BEGIN → CREATE TABLE → 3 CREATE INDEX → CREATE FUNCTION → CREATE TRIGGER → COMMENT → COMMIT |
| Post-apply verifier | `node scripts/mcf-m9-post-apply-verification.mjs` | **exit 0** — **13/13 PASS on first attempt** (basis-of-apply evidence) |

### 2.1 Dry-run 8-check summary (all PASS)

**4 HARD-GATEs + 4 advisory:**

1. M5 + M7/M8 substrate prereq — 14 mcf.* tables + `formula_ast_canonical_json` column + `mcf.metric_authoring_panel_run` present (HARD-GATE)
2. `mcf.metric_self_verification_fixture` does NOT yet exist (HARD-GATE — clean slate)
3. `mcf.fn_msvf_immutability_check` + `trg_msvf_immutability` do NOT yet exist (HARD-GATE — clean slate)
4. All 14 mcf.* tables empty (HARD-GATE — no real rows would orphan)
5. FK targets present: mc + mcv + mapr (advisory regression on M2/M5)
6. M9 doc-bug awareness — M4 inline comment at `06-mcf-lifecycle-certification.sql:179` incorrectly attributes `mcf.metric_self_verification_result` to M9 (informational only; non-blocking per DBCP §11.4; M10 DBCP will correct per D-M9-8)
7. Forward DDL parse + statement counts (1 CREATE TABLE + 3 CREATE INDEX + 1 CREATE FUNCTION + 1 CREATE TRIGGER + 0 ALTER + 0 UPDATE + 1 COMMENT + BEGIN/COMMIT)
8. DDL + rollback sha256 captured

### 2.2 Post-apply 13-check summary (all PASS on first attempt)

**Structural (1–5):**

1. `mcf.metric_self_verification_fixture` — 16 cols + 7 CHECKs byte-matched against `pg_get_constraintdef()` per DBCP §15.2 (5 sha256 format + 1 algo-version regex + 1 rationale-length) — per M1 patch; no multi-line CHECKs so semantic-equivalence carve-out from M5 §15.4 not needed
2. 3 intra-mcf FKs active (`fk_msvf_mc` + `fk_msvf_mcv` + `fk_msvf_panel_run`) all ON DELETE RESTRICT
3. UNIQUE `uq_msvf_mcv_fixture_hash` on `(metric_contract_version_uid, self_verification_fixture_hash)` present
4. 3 non-PK / non-UNIQUE indexes present (`idx_mcf_msvf_mcv` + `idx_mcf_msvf_bound_package_hash` + `idx_mcf_msvf_panel_run`)
5. Trigger function `mcf.fn_msvf_immutability_check` + `trg_msvf_immutability` BEFORE UPDATE OR DELETE attached

**Behavioral (6–12) — SAVEPOINT-protected synthetic-row exercises:**

6. Synthetic 4-row prereq insert chain succeeds (`contract.panel_output_record` + `mcf.metric_authoring_panel_run` + `mcf.metric_contract` + `mcf.metric_contract_version`) per DBCP §15.5
7. Valid fixture INSERT succeeds (all 5 hashes + algorithm-version + rationale CHECKs pass)
8. UPDATE fixture → REJECTED by trigger (immutable)
9. DELETE fixture → REJECTED by trigger (immutable)
10. Duplicate `(mcv_uid, fixture_hash)` → REJECTED by `uq_msvf_mcv_fixture_hash` UNIQUE
11. **All 3 FK rejections (mc + mcv + panel_run) all REJECTED** by respective FK constraints (widened per L2 patch — covers all 3 FKs symmetrically)
12. Short rationale (< 40 chars) → REJECTED by `msvf_rationale_min_length_chk`

**Cleanup (13):**

13. All 15 mcf.* tables empty after verifier (rollback discipline preserved across all 7 behavioral SAVEPOINT exercises)

## 3. Live state post-apply

Verified via independent bc-postgres MCP read-only query (`allow_write=false`):

| Aspect | Value | Status |
|---|---|---|
| `mcf.metric_self_verification_fixture` exists | **true** | ✓ M9 table created |
| `mcf.fn_msvf_immutability_check` function exists | **true** | ✓ M9 function present |
| `trg_msvf_immutability` trigger exists | **true** | ✓ M9 trigger attached |
| Total `mcf.*` tables | **15** | ✓ pre-M9 14 + 1 new M9 |
| `mcf.metric_self_verification_fixture` row count | **0** | ✓ substrate dormant |
| Total MCF row count (all 15 tables) | **0** | ✓ substrate empty throughout |
| FK count on new table | **3** | ✓ all intra-mcf, ON DELETE RESTRICT |
| CHECK count on new table | **7** | ✓ all 7 predicates byte-match expected |
| Index count on new table (incl. PK + UNIQUE) | **5** | ✓ 1 PK + 1 UNIQUE + 3 explicit |
| `contract.panel_output_record` BCF rows | **24** | ✓ untouched |
| `contract.authoring_panel_rejection_log` BCF row | **1** | ✓ untouched |

All 7 CHECK predicates byte-equal to expected `pg_get_constraintdef()` text:
- `msvf_formula_intent_hash_fmt_chk` → `CHECK ((formula_intent_hash ~ '^sha256:[0-9a-f]{64}$'::text))`
- `msvf_variable_binding_set_hash_fmt_chk` → `CHECK ((variable_binding_set_hash ~ '^sha256:[0-9a-f]{64}$'::text))`
- `msvf_grain_filter_temporal_dim_sig_hash_fmt_chk` → `CHECK ((grain_filter_temporal_dimension_signature_hash ~ '^sha256:[0-9a-f]{64}$'::text))`
- `msvf_self_verification_fixture_hash_fmt_chk` → `CHECK ((self_verification_fixture_hash ~ '^sha256:[0-9a-f]{64}$'::text))`
- `msvf_bound_package_signature_hash_fmt_chk` → `CHECK ((bound_package_signature_hash ~ '^sha256:[0-9a-f]{64}$'::text))`
- `msvf_hash_algorithm_version_chk` → `CHECK ((hash_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'::text))`
- `msvf_rationale_min_length_chk` → `CHECK ((length(rationale_text) >= 40))`

## 4. Operational observations

### 4.1 No verifier-fix patch cycle needed (M-M5-1 lesson absorbed)

The M5 apply hit a SAVEPOINT-related false-negative in check #11 (sequential negative assertions inside one `sql.begin(tx)` caused cascade tx-abort — verifier reported `delete_rejected=false unique_rejected=false` even though the substrate was correct). M5 needed an extra patch cycle (PR #113) to wrap each negative assertion in `tx.savepoint()`.

The M9 impl PR (#115) **shipped SAVEPOINT-protection from the start** plus L2 widened-FK coverage and M1 7-CHECK predicate byte-match — three improvements that all proved out on first apply attempt:

- All 5 negative assertions (#8 UPDATE / #9 DELETE / #10 duplicate UNIQUE / #11 3-FK rejections / #12 short rationale) ran independently in their own SAVEPOINTs without cascade-abort
- All 7 CHECK predicates byte-matched against `pg_get_constraintdef()` (catches silent regex weakening that name-only checks would miss)
- All 3 FK rejections (mc + mcv + panel_run) probed symmetrically inside the widened #11

**Outcome:** post-apply verifier exit 0 / 13/13 PASS on first attempt; no patch-PR cycle; clean evidence pair.

### 4.2 No pre-state snapshot needed for M9

M5 dry-run produced an extra artifact — the pre-extension `mcf_v1.consensus_requirement_json` snapshot — because M5 apply included an UPDATE statement that mutated existing data (jsonb-merge adding `panel_discipline`). The snapshot was needed for rollback safety (so jsonb-subtract reversion could be verified to restore the exact pre-extension shape).

M9 apply contains **no UPDATE statements** — only CREATE TABLE / CREATE INDEX / CREATE FUNCTION / CREATE TRIGGER / COMMENT. The rollback DDL drops everything M9 created without needing to know prior state. So the M9 dry-run does NOT produce a pre-state snapshot, and the evidence PR ships **5 artifacts** (vs M5's 6).

### 4.3 DDL sha256 stability across CRLF normalization

The DDL sha256 captured pre-PR-merge (`cdd0bba...` forward, `5d032ab...` rollback) differed from the apply-time sha256 (`70e0952...` forward, `04fb86a...` rollback) due to Windows CRLF line-ending normalization on the post-merge git checkout (per the `LF will be replaced by CRLF the next time Git touches it` warnings during commits). The DDL text postgres executes is functionally identical — only line endings differ. The canonical hashes for this apply are the post-checkout `70e0952...` / `04fb86a...` values, recorded in the dry-run `.planned-sql.sha256.txt` artifact.

**Future improvement (out of M9 scope):** add a `.gitattributes` rule to force LF on `docker/redesign/*.sql` so sha256 is stable across Windows checkouts. Filed as a parked observation; not required for M9 to land.

### 4.4 M4 doc-bug informational flag (per D-M9-8)

The dry-run check #6 surfaces the M4 inline comment at `bc-core/docker/redesign/06-mcf-lifecycle-certification.sql:179` that incorrectly attributes `mcf.metric_self_verification_result` to M9. The bug is informational only — non-blocking by inspection per DBCP §11.4 — and per D-M9-8 will be corrected in the M10 DBCP (since `mcf.metric_self_verification_result` is the M10 table, not M9). M9 substrate has zero FK references back to the M4-commented column.

### 4.5 Substrate dormancy

M9 substrate is now **live and dormant**. The 1 new table accepts panel-attested fixture INSERTs (`panel_run_uid NOT NULL` FK enforced; rationale ≥40 chars enforced; 5 hash format CHECKs enforced; immutability trigger active), but no fixture exists. Fixture authoring requires:
- **M11** reservoir ingestion service to feed the panel intake queue
- **M12** Metric Authoring Panel implementation to author fixtures via panel runs
- **M10** verifier engine to execute fixtures against packages (reuses M9-shipped C-FX engine per DBCP §11.1)
- **M9-engine impl PR** to ship the C-FX engine + `computeSelfVerificationFixtureHash()` helper (DBCP §18.1 items 5-8; deferred from PR #115)

Until all four downstream pieces land, the substrate stays dormant — the substrate constraints provide the guard rails, but the row flow does not begin.

## 5. Artifact pointers

### 5.1 bc-core evidence PR

**PR #116** — `artifacts(mcf): M9 apply — dry-run PASS + post-apply 13-check PASS`

5 artifacts committed:
- `scripts/audit-output/mcf-m9-dry-run-2026-05-27T12-49-23-533Z.summary.md`
- `scripts/audit-output/mcf-m9-dry-run-2026-05-27T12-49-23-533Z.precondition.jsonl`
- `scripts/audit-output/mcf-m9-dry-run-2026-05-27T12-49-23-533Z.planned-sql.sha256.txt`
- `scripts/audit-output/mcf-m9-post-apply-2026-05-27T12-52-58-662Z.summary.md`
- `scripts/audit-output/mcf-m9-post-apply-2026-05-27T12-52-58-662Z.evidence.jsonl`

### 5.2 Stale intermediate dry-runs excluded

4 pre-merge verification rounds produced their own dry-run artifacts:
- `T12-01-27-424Z` — initial impl verification (during PR #115 construction)
- `T12-08-14-630Z` — PR review verification
- `T12-20-50-540Z` — M1/L2 patch verification (during PR #115 re-review)
- `T12-29-33-693Z` — re-review verification

These are **deliberately excluded** from the evidence PR per operator scope *"Do not bulk-stage `scripts/audit-output/`"*. Only the canonical session-of-apply pair (T12-49 dry-run + T12-52 post-apply) is staged. The intermediate runs were verification scaffolding for PR review; the apply session is the basis-of-record.

### 5.3 bc-core substrate commit

- **Squash commit:** `cd31cb1f1ac5fb8caac6244ed207fda91c9ac7e5` (`cd31cb1`)
- **Subject:** `feat(mcf): M9 Fixture Substrate — metric self-verification fixture registry (NO DB APPLY) (#115)`
- **Merged at:** 2026-05-27T12:36:45Z

## 6. What stays closed after M9 apply

| | |
|---|---|
| M9 substrate code | ✓ live on bc-core main `cd31cb1` |
| M9 DDL applied to `bc_platform_dev` | ✓ live + verified + dormant |
| M9 evidence PR | open (PR #116) — separate operator merge |
| **M9-engine impl PR** (DBCP §18.1 items 5-8) | **REQUIRED before M10 DBCP** |
| M10 deterministic verifier service + `mcf.metric_self_verification_result` substrate | CLOSED — gated on M9-engine + M9 substrate |
| M11 reservoir ingestion | CLOSED — separate gate |
| M12 Metric Authoring Panel implementation | CLOSED — gated on M5 + M7 + M9 + M10 + M11 |
| M13 PE-MC evaluator | CLOSED — gated on M5 + M7 + M9 + M10 |
| Real MCF metric contracts | CLOSED — substrate stays empty |
| Real fixture rows | CLOSED — substrate stays empty (panel-only authoring requires M12) |
| BCF data changes | CLOSED — 24 BCF panel rows + 1 rejection log row untouched throughout |
| M4 DBCP doc-bug correction | DEFERRED to M10 DBCP per D-M9-8 (non-blocking per DBCP §11.4) |
| §19.13 Q37 minimum-fixture-coverage per formula class | OPEN — not a M9 dependency |
| §12.9 conditional fixture mutability | DEFERRED — M9 enforces stricter unconditional immutability per operator design constraint (see R-M9-7); future post-M13 amendment may relax |
| D-M9-C fixture-pack envelope | DEFERRED — revisit if Q37 lands |
| MCF defect-code v2 taxonomy | CLOSED — v1 pinned |
| MCF hash algorithm v2 bump | CLOSED — `mcf-hash-v1` forever-locked unless ADR-governed change |

## 7. M9-engine reminder (before M10)

**The M9 arc is not complete until the M9-engine impl PR lands.** Per DBCP §18.1 items 5-8 (deferred by PR #115 per operator's narrower substrate-only scope) + DBCP §11.1 (M10 verifier reuses M9 C-FX engine), the next M9-arc gate must ship:

1. `bc-core/src/registry/mcf/package-signature.service.ts` — extend with `computeSelfVerificationFixtureHash()` method per DBCP §6.4 (single-bundle `mcf-hash-v1`; reuses `mcf-jcs.ts`)
2. `bc-core/src/registry/mcf/package-signature.service.spec.ts` — golden-vector + canonicalization-determinism unit tests
3. `bc-core/src/registry/mcf/fixture-structural-check.service.ts` — C-FX-1..C-FX-11 engine per DBCP §7.4
4. `bc-core/src/registry/mcf/fixture-structural-check.service.spec.ts` — 11 positive + 11 negative tests per check

After M9-engine merges, the M10 DBCP gate can be opened (M10 verifier engine will reuse the M9-shipped C-FX engine).

## 8. Sequencing summary

```
M2 (live, evidenced, closed)     ─┐
M3 (live, evidenced, closed)      │
M4 (live, evidenced, closed)      │
M5 (live, evidenced, closed)      ├─ Substrate baseline (pre-M9)
M7/M8 (live, evidenced, closed)  ─┘
                                     │
M9 substrate impl PR #115           ─┤
M9 substrate apply + post-verify    ─┤
M9 evidence PR #116                 ─┤ ← THIS CLOSEOUT marks the END
                                       of M9 substrate sub-arc
M9-engine impl PR                   ─┐
                                     ├─ M9 full arc (REQUIRED before M10)
M9-engine merge                     ─┘
                                     │
M10 DBCP                            ─┐
M10 impl + apply + evidence          │
M10 closeout                         │
                                     ├─ M10–M13 downstream
M11/M12/M13 (in parallel sequence)   │
                                    ─┘
```

## 9. Operator discipline confirmation

This closeout commits no code or data. Everything substantive (DDL, scripts, evidence artifacts) is in bc-core. This doc records what landed.

- **No fixture rows authored** ✓
- **No real MCF metric contracts** ✓
- **No BCF data touches** ✓ (24 BCF panel rows + 1 rejection log row untouched throughout)
- **No M9-engine implementation** in this apply session ✓ (deferred to follow-up gate)
- **No M10/M11/M12 gates opened** ✓

M9 substrate is now **live and dormant** on `bc_platform_dev`. The next operator-authorized gate is **M9-engine impl PR**.
