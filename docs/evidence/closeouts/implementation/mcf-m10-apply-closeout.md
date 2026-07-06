---
uid: mcf-m10-apply-closeout
title: MCF M10 Self-Verification Result Substrate + Verifier Engine — Live DDL Apply Closeout
description: Closeout for the MCF M10 Self-Verification Result Substrate + Verifier Engine live DDL apply against bc_platform_dev on 2026-05-27. Applied docker/redesign/10-mcf-self-verification-result.sql (DDL pinned at bc-core PR #118 squash d635bbe; sha256 4aebef4ec3a85212c066047879604ef3a55459d003c148a8fb95e59c5f731921) under explicit operator approval per CLAUDE.md Database Change Protocol. Realizes M10-A (append-only ledger + JSONB diff trace + sync verifier service) per M10 DBCP (bc-docs-v3 ea8b708) with all 11 operator approvals O-M10-1..O-M10-11. Substrate change ALL IN ONE NEW TABLE — mcf.metric_self_verification_result (13 columns; 10 constraints — 1 PK + 3 intra-mcf FK fk_msvr_fixture/fk_msvr_mc/fk_msvr_mcv all ON DELETE RESTRICT + 5 CHECK verdict-enum + 2 sha256-fmt + algo-version regex + non-negative-duration + 1 UNIQUE on fixture_uid+verifier_algorithm_version+bound_package_signature_hash_at_run for substrate-side idempotency) + 4 indexes (lookup-by-fixture / mcv / verdict / executed_at) + 1 trigger function mcf.fn_msvr_immutability_check + 1 trigger attachment trg_msvr_immutability BEFORE UPDATE OR DELETE (M3/M5/M9-style unconditional reject post-INSERT per D-M10-9 evidence-grade defense-in-depth) + 1 FK activation fk_mper_verification_result on mcf.metric_publication_eligibility_result.satisfying_verification_result_uid → mcf.metric_self_verification_result(verification_result_uid) per D-M10-7 (deferred since M4 per D-16) + 1 COMMENT ON COLUMN UPDATE correcting M4 doc-bug per D-M10-8 (previously "FK deferred until M9 ships" now "FK fk_mper_verification_result activated by M10"). Verifier service MetricSelfVerificationService.verifyFixture executing §12.6 6-step pipeline; reuses M9 FixtureStructuralCheckService.runStructuralChecks + M9 PackageSignatureService.computeSelfVerificationFixtureHash + M7/M8 FormulaCanonicalizationService for current package hash recomputation. Algorithm version mcf-verifier-v1 per D-M10-4. Dry-run all 8 preconditions PASS including 4 HARD-GATEs (M9 prereq + new table absent + trigger/fn absent + FK activation absent) + DDL sha256 capture. psql exit 0 inside BEGIN/COMMIT whole-file transaction wrapper per §15.2 (BEGIN → CREATE TABLE → 4× CREATE INDEX → CREATE FUNCTION → CREATE TRIGGER → ALTER TABLE → 2× COMMENT → COMMIT). Post-apply 16-check verifier exit 0 / 16/16 PASS ON FIRST ATTEMPT — no verifier-fix patch cycle needed (the SAVEPOINT-protection + 5-CHECK byte-match + 3-FK widened rejection patterns shipped from start per M9 M-M5-1/M1/L2 lessons absorbed, avoiding the M5-style false-negative recovery cycle). All 5 CHECK predicates byte-matched against pg_get_constraintdef() per DBCP §15.2. All 3 FKs behaviorally probed for rejection (mc + mcv + fixture per the M9 L2 widened-FK pattern). All 9 negative assertions SAVEPOINT-wrapped. Live state post-apply 16 mcf.* tables (10 pre-M5 + 4 M5 + 1 M9 + 1 new M10), all empty; mcf.fn_msvr_immutability_check function present; trg_msvr_immutability trigger attached; fk_mper_verification_result active on mper column; M4 column comment corrected to accurate "FK fk_mper_verification_result activated by M10" wording; 5 hash format CHECK predicates + 1 algo-version regex CHECK + 1 verdict-enum CHECK + 1 duration-non-negative CHECK all byte-equal to expected pg_get_constraintdef() text; existing 24 contract.panel_output_record BCF rows + 1 contract.authoring_panel_rejection_log BCF row + M4 seeds + M5 mcf_v1.panel_discipline policy + M3/M7 triggers + M9 fixture substrate all UNTOUCHED. M10 substrate now LIVE and DORMANT — substrate accepts verification result INSERTs but no fixtures exist for the verifier service to verify; M11 ingestion + M12 panel implementation + M13 PE-MC evaluator are now UNBLOCKED as separate gates (NOT opened by this apply). 5 basis-of-apply artifacts committed to bc-core via PR #119 (3 dry-run + 2 post-apply); 2 stale intermediate dry-runs from pre-merge verification rounds (T14-56 PR construction + T15-01 PR review) deliberately excluded per evidence discipline. No real MCF metric contracts authored. No fixture rows authored. No verification result rows authored. No BCF touches. No M11/M12/M13/M14+ gates opened.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m10-apply-closeout
---

# MCF M10 Self-Verification Result Substrate + Verifier Engine — Live DDL Apply Closeout

## 1. What landed

The MCF M10 Self-Verification Result Substrate + Verifier Engine DDL was applied live against `bc_platform_dev` on **2026-05-27**, completing the substrate side of the M10 arc and closing the substrate chain M2→M10. The DDL ships **1 new mcf-owned table** (`mcf.metric_self_verification_result`), **4 indexes** (lookup-by-fixture / mcv / verdict / executed_at), **1 trigger function + attachment** (`mcf.fn_msvr_immutability_check` + `trg_msvr_immutability` BEFORE UPDATE OR DELETE — M3/M5/M9-style unconditional UPDATE/DELETE reject post-INSERT per D-M10-9 evidence-grade defense-in-depth), **1 FK activation** (`fk_mper_verification_result` on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` → `mcf.metric_self_verification_result(verification_result_uid)` ON DELETE RESTRICT; deferred since M4 per D-16), **1 COMMENT ON COLUMN UPDATE** correcting the M4 doc-bug per D-M10-8 (previously *"FK deferred until M9 ships"* — now *"FK fk_mper_verification_result activated by M10..."*), and **1 COMMENT ON TABLE** on the new result table.

The new table carries **13 columns** + **10 constraints** (1 PK + 3 intra-mcf FK ON DELETE RESTRICT + 5 CHECK + 1 UNIQUE for substrate-side idempotency):
- **Verdict CHECK enum:** `pass` / `fail` / `structural_reject` per MCF §12.6
- **2 sha256-format hashes:** `bound_package_signature_hash_at_run` (MC's current hash at verifier run time) + `fixture_bound_package_signature_hash` (snapshot from fixture row at run time) — both stored for stale-fixture forensic audit per D-M10-6
- **Algorithm version:** `mcf-verifier-v1` per D-M10-4 (separate bundle from `mcf-hash-v1`; verifier is a different algorithm class)
- **UNIQUE `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)`** — at most one row per triple; substrate-side idempotency for verifier retries

**Verifier service code** (`MetricSelfVerificationService`, `FormulaExecutionEngine`, `ResolverFixtureConfigInterpreter`, `OutputComparator`) merged earlier in bc-core PR #118 at squash `d635bbe`. Reuses M9 `FixtureStructuralCheckService.runStructuralChecks` (no duplicate C-FX engine) + M9 `PackageSignatureService.computeSelfVerificationFixtureHash` (no duplicate hash machinery). 4 new M10 classes cover the §12.6 6-step pipeline + 9 NODE_KINDS execution + Section C resolver interpretation + tolerance/null-match comparison.

M2 + M3 + M4 + M5 + M7/M8 + M9 substrate stays applied throughout (no DROP/RECREATE; no touches to existing mcf.* tables apart from the FK activation + comment correction on `mcf.metric_publication_eligibility_result`; no changes to BCF `concept_registry.*` / `contract.panel_output_record` / `contract.authoring_panel_rejection_log`).

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/10-mcf-self-verification-result.sql` |
| Rollback source | `bc-core/docker/redesign/10-mcf-self-verification-result-rollback.sql` |
| Pinned at | bc-core PR #118 / squash commit `d635bbe` (HEAD of `main` at apply time) |
| DDL sha256 | `4aebef4ec3a85212c066047879604ef3a55459d003c148a8fb95e59c5f731921` |
| Rollback sha256 | `06a3108d031585d166972a3f0ca8c68f9c553e8433452848247d5d50f4f4bd49` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + M10 preflight (`bc-docs-v3 60930fa`) + M10 DBCP (`bc-docs-v3 ea8b708` — operator-accepted D-M10-1..D-M10-10 + D-M10-A1; operator approvals O-M10-1..O-M10-11) |
| Operator approval | Explicit "Approved, apply M10 self-verification result substrate" in conversation per CLAUDE.md Database Change Protocol |
| Evidence PR | bc-core PR #119 (5 basis-of-apply artifacts: 3 dry-run + 2 post-apply; 2 stale intermediate dry-runs from pre-merge verification rounds excluded with rationale) |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m10-dry-run.mjs` | **exit 0** — 8/8 PASS; DDL sha256 captured |
| Live apply | `cat docker/redesign/10-mcf-self-verification-result.sql \| docker exec -i bc-postgres psql -U barecount -d bc_platform_dev -v ON_ERROR_STOP=1` | **exit 0** — inside `BEGIN;...COMMIT;` whole-file transaction wrapper (per §15.2 + M3-cert-amendment + M5 + M7/M8 + M9 atomicity pattern): BEGIN → CREATE TABLE → 4 CREATE INDEX → CREATE FUNCTION → CREATE TRIGGER → ALTER TABLE → 2 COMMENT → COMMIT |
| Post-apply verifier | `node scripts/mcf-m10-post-apply-verification.mjs` | **exit 0** — **16/16 PASS on first attempt** (basis-of-apply evidence) |

### 2.1 Dry-run 8-check summary (all PASS)

**4 HARD-GATEs + 4 advisory:**

1. M9 substrate prereq — all 15 mcf.* tables incl. `metric_self_verification_fixture` (HARD-GATE)
2. `mcf.metric_self_verification_result` does NOT yet exist (HARD-GATE — clean slate)
3. `mcf.fn_msvr_immutability_check` + `trg_msvr_immutability` do NOT yet exist (HARD-GATE — clean slate)
4. `fk_mper_verification_result` does NOT yet exist (HARD-GATE — clean slate; FK activation pending)
5. All 15 mcf.* tables empty (advisory)
6. FK targets present: fixture + mc + mcv + mper (advisory regression on M2/M4/M9)
7. Forward DDL parse + statement counts (1 CREATE TABLE + 4 CREATE INDEX + 1 CREATE FUNCTION + 1 CREATE TRIGGER + 1 ALTER TABLE + 1 COMMENT ON COLUMN + 1 COMMENT ON TABLE + BEGIN/COMMIT)
8. DDL + rollback sha256 captured

### 2.2 Post-apply 16-check summary (all PASS on first attempt)

**Structural (1–6):**

1. `mcf.metric_self_verification_result` — 13 cols + 5 CHECKs **byte-matched against `pg_get_constraintdef()`** per DBCP §18.2 (verdict-enum + 2 sha256-fmt + algo-version regex + non-negative-duration); no multi-line CHECKs so semantic-equivalence carve-out not needed
2. 3 intra-mcf FKs active (`fk_msvr_fixture` + `fk_msvr_mc` + `fk_msvr_mcv`) all ON DELETE RESTRICT
3. UNIQUE `uq_msvr_fixture_version_pkg_hash` present
4. 4 non-PK / non-UNIQUE indexes present (`idx_mcf_msvr_fixture` + `idx_mcf_msvr_mcv` + `idx_mcf_msvr_verdict` + `idx_mcf_msvr_executed_at`)
5. Trigger function `mcf.fn_msvr_immutability_check` + `trg_msvr_immutability` BEFORE UPDATE OR DELETE attached
6. `fk_mper_verification_result` activated on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid → mcf.metric_self_verification_result(verification_result_uid)` ON DELETE RESTRICT

**Behavioral (7–15) — SAVEPOINT-protected synthetic-row exercises:**

7. 5-row synthetic prereq insert chain succeeds (`contract.panel_output_record` + `mcf.metric_authoring_panel_run` + `mcf.metric_contract` + `mcf.metric_contract_version` + `mcf.metric_self_verification_fixture`)
8. Valid result row INSERT succeeds (all 5 hashes + algorithm-version + duration CHECKs pass)
9. UPDATE result row → REJECTED by `trg_msvr_immutability` (immutable)
10. DELETE result row → REJECTED by `trg_msvr_immutability` (immutable)
11. Duplicate `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` → REJECTED by `uq_msvr_fixture_version_pkg_hash` UNIQUE
12. **3-FK widened rejection** (per M9 L2 pattern): bogus mc → `fk_msvr_mc` rejection; bogus mcv → `fk_msvr_mcv` rejection; bogus fixture → `fk_msvr_fixture` rejection
13. Invalid `verdict_code` (e.g. `'unknown'`) → REJECTED by `msvr_verdict_code_chk`
14. Bad hash format → REJECTED by `msvr_bound_pkg_hash_at_run_fmt_chk`
15. Negative `execution_duration_ms` (`-1`) → REJECTED by `msvr_duration_non_negative_chk`

**Cleanup (16):**

16. All **16 mcf.* tables empty** after verifier (rollback discipline preserved across all 9 behavioral SAVEPOINT exercises)

## 3. Live state post-apply

Verified via independent bc-postgres MCP read-only query (`allow_write=false`):

| Aspect | Value | Status |
|---|---|---|
| `mcf.metric_self_verification_result` exists | **true** | ✓ M10 table created |
| `mcf.fn_msvr_immutability_check` function exists | **true** | ✓ M10 function present |
| `trg_msvr_immutability` trigger exists | **true** | ✓ M10 trigger attached |
| `fk_mper_verification_result` FK active | **true** | ✓ M4-deferred FK activated by M10 |
| M4 column comment corrected | **true** | ✓ now reads *"FK fk_mper_verification_result activated by M10 (per DBCP M10 §12 + DBCP M10 ea8b708). Per MCF §13 PE-MC-10 + §17.1 result substrate."* |
| Total `mcf.*` tables | **16** | ✓ pre-M10 15 + 1 new M10 |
| `mcf.metric_self_verification_result` row count | **0** | ✓ substrate dormant |
| FK count on new table | **3** | ✓ all intra-mcf, ON DELETE RESTRICT |
| CHECK count on new table | **5** | ✓ all 5 predicates byte-match expected |
| Index count on new table (incl. PK + UNIQUE) | **6** | ✓ 1 PK + 1 UNIQUE + 4 explicit |
| `contract.panel_output_record` BCF rows | **24** | ✓ untouched |
| `contract.authoring_panel_rejection_log` rows | **1** | ✓ untouched |

## 4. FK activation outcome

The M4-deferred `fk_mper_verification_result` is now **ACTIVE**:

```text
ALTER TABLE mcf.metric_publication_eligibility_result
  ADD CONSTRAINT fk_mper_verification_result
  FOREIGN KEY (satisfying_verification_result_uid)
  REFERENCES mcf.metric_self_verification_result(verification_result_uid)
  ON DELETE RESTRICT;
```

Activation was metadata-only (both source and target tables had 0 rows pre-apply). Post-apply, future PE-MC-10 INSERTs into `mcf.metric_publication_eligibility_result` will validate `satisfying_verification_result_uid` against `mcf.metric_self_verification_result(verification_result_uid)` at the substrate level.

This unblocks **M13 PE-MC evaluator** — M13 service code can now write PE-MC-10 rows citing a satisfying verification result with substrate-enforced referential integrity.

## 5. M4 doc-bug correction outcome (per D-M9-8 + D-M10-8)

The M4 inline column comment at `bc-core/docker/redesign/06-mcf-lifecycle-certification.sql:179` had a documented doc-bug: it said *"FK deferred until M9 ships"* but `mcf.metric_self_verification_result` is the **M10** table (not M9).

The M10 DDL Step 5 atomically corrected this via `COMMENT ON COLUMN` UPDATE:

**Pre-correction (live before M10 apply):**
```text
'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK deferred until M9 ships (D-16). Nullable + FK-less until then; service-layer validation when the table exists.'
```

**Post-correction (live after M10 apply — independently verified via `col_description`):**
```text
'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK fk_mper_verification_result activated by M10 (per DBCP M10 §12 + DBCP M10 ea8b708). Per MCF §13 PE-MC-10 + §17.1 result substrate.'
```

The correction landed atomically with the FK activation in the same `BEGIN/COMMIT` (per DBCP §13.3 + §15.2 Step ordering). No standalone amendment needed.

## 6. Operational observations

### 6.1 No verifier-fix patch cycle needed (M-M5-1 + M9 M1/L2 lessons absorbed)

M5 apply hit a SAVEPOINT-related false-negative in check #11 (sequential negative assertions inside one `sql.begin(tx)` caused cascade tx-abort). M5 needed PR #113 to wrap each negative assertion in `tx.savepoint()`. M9 absorbed that lesson and shipped SAVEPOINT-protection from the start (proved on M9 apply).

**M10 absorbed three lessons** from prior gates and shipped from the start:
- **SAVEPOINT-protection** (per M-M5-1) — each negative assertion in its own savepoint
- **CHECK predicate byte-match** (per M9 M1 patch) — `EXPECTED_CHECK_PREDICATES` const + per-CHECK byte-equality assertion; catches silent regex weakening
- **3-FK widened rejection** (per M9 L2 patch) — symmetric per-FK rejection probes (mc + mcv + fixture all probed)

**Outcome:** post-apply verifier exit 0 / 16/16 PASS on first attempt; no patch-PR cycle; clean evidence pair.

### 6.2 DDL sha256 stability across CRLF normalization (same as M5/M9)

The DDL sha256 captured pre-PR-merge differed from the apply-time sha256 due to Windows CRLF line-ending normalization on the post-merge git checkout. The DDL text postgres executes is functionally identical — only line endings differ. The canonical hashes for this apply are `4aebef4...` (forward) / `06a3108...` (rollback) as the file exists on main `d635bbe` at apply time. Parked observation: future `.gitattributes` rule could force LF on `docker/redesign/*.sql` for sha256 stability across Windows checkouts; out of M10 scope.

### 6.3 FK activation safety on empty tables

`mcf.metric_publication_eligibility_result` had 0 rows pre-apply. `mcf.metric_self_verification_result` had 0 rows (just-created). FK activation was metadata-only — no existing row needed validation. Future INSERTs into mper will be validated.

### 6.4 Substrate-side idempotency design proven correct

Post-apply check #11 confirmed the UNIQUE `uq_msvr_fixture_version_pkg_hash` rejects duplicate `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` triples. The M10 verifier service's catch-and-SELECT pattern (per DBCP §6.3 + L2 review patch) relies on this UNIQUE to provide idempotent retry semantics — confirmed substrate-side.

### 6.5 Substrate dormancy

M10 substrate is now **live and dormant**. The result table accepts verification result INSERTs (substrate constraints enforce verdict enum + hash format + algorithm version + duration non-negativity + UNIQUE idempotency + intra-mcf FK integrity + append-only immutability), but the verifier service has no fixtures to verify. Full flow requires:
- **M11** reservoir ingestion to feed the panel intake queue
- **M12** Metric Authoring Panel implementation to author fixture rows via panel runs
- **M10 verifier invocation** by M12 panel service path (against authored fixtures)
- **M13** PE-MC evaluator to consume the resulting `mcf.metric_self_verification_result` rows for PE-MC-10

The M10 substrate + verifier engine are READY. The downstream gates (M11/M12/M13) are now **UNBLOCKED** as separate gates.

## 7. Artifact pointers

### 7.1 bc-core evidence PR

**PR #119** — `artifacts(mcf): M10 apply — dry-run PASS + post-apply 16-check PASS`

5 artifacts committed:
- `scripts/audit-output/mcf-m10-dry-run-2026-05-27T15-18-24-136Z.summary.md`
- `scripts/audit-output/mcf-m10-dry-run-2026-05-27T15-18-24-136Z.precondition.jsonl`
- `scripts/audit-output/mcf-m10-dry-run-2026-05-27T15-18-24-136Z.planned-sql.sha256.txt`
- `scripts/audit-output/mcf-m10-post-apply-2026-05-27T15-22-28-456Z.summary.md`
- `scripts/audit-output/mcf-m10-post-apply-2026-05-27T15-22-28-456Z.evidence.jsonl`

### 7.2 Stale intermediate dry-runs excluded

2 pre-merge verification rounds produced their own dry-run artifacts:
- `T14-56-21-553Z` — PR construction verification (during PR #118 build-out)
- `T15-01-22-181Z` — PR review verification

These are **deliberately excluded** from the evidence PR per operator scope *"Do not bulk-stage `scripts/audit-output/`. Exclude stale/intermediate dry-runs from PR construction/review."* Only the canonical session-of-apply pair (T15-18 dry-run + T15-22 post-apply) is staged.

### 7.3 bc-core substrate + verifier commits

- **Squash commit:** `d635bbebb3a0fcbcd406bcd3415722e975537875` (`d635bbe`) — substrate DDL + Drizzle schema + 4 verifier services + 4 specs + dry-run + post-apply scripts (combined per D-M10-A1)
- **Subject:** `feat(mcf): M10 self-verification result substrate + verifier service (NO DB APPLY) (#118)`
- **Merged at:** 2026-05-27T15:09:36Z

## 8. What stays closed after M10 apply

| | |
|---|---|
| M10 substrate code | ✓ live on bc-core main `d635bbe` |
| M10 verifier engine + services | ✓ live (256 MCF tests passing) |
| M10 DDL applied to `bc_platform_dev` | ✓ live + verified + dormant |
| M10 evidence PR | open (PR #119) — separate operator merge |
| **M11 reservoir ingestion** | UNBLOCKED — separate gate (NOT opened by this apply) |
| **M12 Metric Authoring Panel implementation** | UNBLOCKED — separate gate (NOT opened by this apply) |
| **M13 PE-MC evaluator** | UNBLOCKED — separate gate (NOT opened by this apply); M10 result substrate + activated FK ready for M13 to consume |
| **M14+** | CLOSED — gated on M13 |
| Real MCF metric contracts | CLOSED — substrate stays empty |
| Real fixtures + verification results | CLOSED — substrate stays empty (M11+M12 required to write) |
| BCF data changes | CLOSED — 24 BCF panel rows + 1 rejection log row untouched throughout |
| M4 DBCP doc-bug | ✓ RESOLVED — corrected inline by M10 DDL Step 5 per D-M9-8 + D-M10-8 |
| **M9 + M10 arc complete** | ✓ both substrates live; verifier engine live |
| §19.13 Q37 minimum-fixture-coverage per formula class | OPEN — not a M10 dependency |
| §19.13 Q38 tolerance + null-match defaults | OPEN — M10 v1 ships sensible defaults; future amendment if needed |
| §19.13 Q40 fixture retention | OPEN — not a M10 dependency |
| Async-queue verifier infrastructure | DEFERRED per D-M10-5 — sync v1 sufficient |
| Per-diff-row child table | DEFERRED per D-M10-3 — JSONB v1 sufficient |
| MCF defect-code v2 taxonomy | CLOSED — v1 pinned |
| MCF hash algorithm v2 bump | CLOSED — `mcf-hash-v1` forever-locked unless ADR-governed change |
| MCF verifier algorithm v2 bump | CLOSED — `mcf-verifier-v1` forever-locked unless ADR-governed change |

## 9. Sequencing summary

```
M2 (live, evidenced, closed)     ─┐
M3 (live, evidenced, closed)      │
M4 (live, evidenced, closed)      │
M5 (live, evidenced, closed)      ├─ Substrate baseline (pre-M9/M10)
M7/M8 (live, evidenced, closed)   │
M9 (live, evidenced, closed)     ─┘
                                     │
M10 substrate + verifier impl PR #118 ─┤
M10 substrate apply + post-verify     ─┤
M10 evidence PR #119                  ─┤ ← THIS CLOSEOUT
                                          marks the END
                                          of the M10 substrate-side arc
                                     │
M11 / M12 / M13 (in parallel sequence) — unblocked as separate gates
                                       ─┘
```

## 10. Discipline confirmation

This closeout commits no code or data. Everything substantive (DDL, scripts, evidence artifacts, services) is in bc-core. This doc records what landed.

- **No result rows authored** ✓ — `mcf.metric_self_verification_result` has 0 rows
- **No fixture rows authored** ✓ — `mcf.metric_self_verification_fixture` has 0 rows
- **No real MCF metric contracts** ✓ — all 16 mcf.* tables empty
- **No BCF data touches** ✓ — 24 BCF panel + 1 rejection log untouched throughout
- **No M11/M12/M13/M14+ gates opened** ✓ — these are UNBLOCKED but explicitly not opened by this apply

M10 substrate is now **live and dormant** on `bc_platform_dev`. The substrate chain M2→M10 is complete. M11 / M12 / M13 are the next operator-authorized gates.
