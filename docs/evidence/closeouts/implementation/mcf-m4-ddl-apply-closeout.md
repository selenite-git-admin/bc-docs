---
uid: mcf-m4-ddl-apply-closeout
title: MCF M4 Lifecycle Certification — Live DDL Apply Closeout
description: Closeout for the MCF M4 Lifecycle Certification live DDL apply against bc_platform_dev on 2026-05-27. Applied docker/redesign/06-mcf-lifecycle-certification.sql (DDL pinned at bc-core PR #107 / e34408c; sha256 de03ee941b09e018b96bdc89b52e1fb4656c799df5c7570a2d9e1c8c8a0cc067) under explicit operator approval per CLAUDE.md Database Change Protocol. Dry-run all 8 numbered checks + 6 amendment-state hard-gates PASS; psql exit 0 inside BEGIN/COMMIT whole-file transaction wrapper per §12.6 atomicity discipline. Initial post-apply verifier exited 10 due to two test-helper/mock bugs (synthetic helper used invalid 'mcf-m4-verifier-v1' hash_algorithm_version with digit in middle segment violating `^mcf-[a-z-]+-v[0-9]+$`; MockMcfHashComputer returned 'mock-1.0.0' violating same regex). Both fixed via bc-core PR #108 (verifier helper → 'mcf-verifier-v1'; mock → 'mcf-mock-v1' with production guard updated to detect mcf-mock-* + legacy mock-* defense-in-depth). Final post-apply verifier 14/14 PASS; integration spec 7/7 PASS against live DB with BCCORE_INTEGRATION_DB=1. Live state: 10 mcf.* tables (8 prior + 2 new M4-shipped), all empty; 1 contract.framework_policy mcf row (mcf_v1 / 1.0.0); 2 contract.operator_confirm_rule mcf rows (both action_code='require_operator_confirm'); operator_confirm_rule.action_code CHECK regression-asserted unchanged; M3 + cert-amendment substrate intact. M4 service code live but operationally dormant — no real MCF metric contracts authored (panel substrate is M5/M11; not in M4 scope). Evidence artifacts committed to bc-core via PR #109 (5 files: 3 dry-run + 2 post-apply; 8 earlier dev-cycle / diagnostic artifacts excluded). M5 panel substrate is next blocked gate.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m4-ddl-apply-closeout
---

# MCF M4 Lifecycle Certification — Live DDL Apply Closeout

## 1. What landed

The MCF M4 Lifecycle Certification / Transition Authority DDL was applied live against `bc_platform_dev` on **2026-05-27**, completing the M4 substrate arc. The DDL ships two new M4-owned `mcf.*` tables (`metric_publication_eligibility_result` + `metric_cert_writer_idempotency`), 4 indexes, 3 seed rows (2 `operator_confirm_rule` + 1 `framework_policy`), and 10 COMMENT annotations. M3 + cert-amendment substrate stays applied throughout (no DROP/RECREATE; no touches to `mcf.certification_record`, the M3 state-transition trigger, or shared CHECK constraints).

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/06-mcf-lifecycle-certification.sql` |
| Pinned at | bc-core PR #107 / commit `e34408c` (HEAD of `main` at apply time) |
| DDL sha256 | `de03ee941b09e018b96bdc89b52e1fb4656c799df5c7570a2d9e1c8c8a0cc067` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + M4 DBCP (`bc-docs-v3 3983530` — 29 patches over `78c7f74`) + M3 cert-amendment closeout (`bc-docs-v3 60efd9d`) |
| Operator approval | Explicit "Approve apply" in conversation per CLAUDE.md Database Change Protocol |
| Verifier+mock fix | bc-core PR #108 / commit `ed322d6` (merged before final 14/14 PASS) |
| Evidence PR | bc-core PR #109 (5 audit artifacts: 3 dry-run + 2 post-apply; 8 dev-cycle / diagnostic artifacts excluded) |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m4-dry-run.mjs` | **exit 0** — 8/8 numbered checks + 6/6 amendment-state hard-gates PASS; DDL sha256 captured at `mcf-m4-dry-run-2026-05-27T04-37-59-453Z.planned-sql.sha256.txt` |
| Live apply | `psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f docker/redesign/06-mcf-lifecycle-certification.sql` | **exit 0** — inside `BEGIN;...COMMIT;` whole-file transaction wrapper (per §12.6 atomicity discipline, mirrors M3 cert-amendment §9.4): 2 CREATE TABLE + 4 CREATE INDEX + 3 INSERT seeds + 10 COMMENT |
| Initial post-apply verifier | `node scripts/mcf-m4-post-apply-verification.mjs` | **exit 10** — 2 test-helper/mock bugs surfaced (see §4.1); fixed via PR #108 |
| Final post-apply verifier (after PR #108) | same | **exit 0** — 14/14 checks PASS |
| Integration spec (after PR #108) | `BCCORE_INTEGRATION_DB=1 vitest run …integration.spec.ts` | **7/7 PASS** against live DB |

### 2.1 Dry-run 8-check summary (all PASS)

**Numbered checks:**
1. `mcf` schema present
2. All 8 `mcf.*` tables present (M2 + M3 + cert-amendment)
3. `mcf.metric_publication_eligibility_result` absent (clean slate)
4. `mcf.metric_cert_writer_idempotency` absent (clean slate)
5. `contract.framework_policy` has no `scope_code='mcf'` rows (clean slate for M4 seed)
6. `contract.operator_confirm_rule` has no `scope='mcf'` rows (clean slate for M4 seeds)
7. DDL parse + statement counts + BEGIN/COMMIT pair + scope-discipline (`alterTable=0`, `createOrReplaceFunction=0`, `dropConstraint=0`)
8. DDL sha256 captured for drift detection

**Amendment-state hard-gates (per §14.1 / R-15 — REFUSE TO PROCEED if any fails):**
- #2a `mcf.certification_record` exists (M3 cert-amendment applied)
- #2b M3 trigger body reads from `mcf.certification_record` (exactly 1 occurrence; 0 occurrences of `contract.certification_record`)
- #2c `mcf.metric_supersession.fk_mcs_cert` targets `mcf.certification_record`
- #3a `contract.framework_policy_scope_code_chk` admits `'mcf'`
- #3b `contract.operator_confirm_rule_scope_chk` admits `'mcf'`
- #3c `contract.operator_confirm_rule_transition_chk` admits `'active_to_superseded'`

Plus regression check #3d: `contract.operator_confirm_rule_action_chk` UNCHANGED (enforcement-action enum only; no MCF cert action codes per §10.5).

### 2.2 Post-apply 14-check summary (final run after PR #108: all PASS)

**Structural (1–7):**
1. `mcf.metric_publication_eligibility_result`: 10 columns + 2 CHECKs (`mper_pe_check_code_chk`, `mper_verdict_code_chk`) + 2 FKs (`fk_mper_mcv`, `fk_mper_cert` → `mcf.certification_record`) + 3 indexes
2. `mcf.metric_cert_writer_idempotency`: 6 columns + single-column PK on `idempotency_key` (per F-9 / P-9) + 1 CHECK (`mcwi_status_chk`) + 1 index on `(status, updated_at)`
3. `contract.framework_policy` has 1 row with `policy_uid='mcf_v1'`, `policy_version='1.0.0'`, `scope_code='mcf'`
4. `contract.operator_confirm_rule` has 2 rows with `scope='mcf'`: `mcf_metric_transition_approved_to_active` (`approved_to_active`) + `mcf_metric_supersede_active_to_superseded` (`active_to_superseded`); both `action_code='require_operator_confirm'` (per P-27 / §10.5 enforcement-directive semantic correction)
5. `operator_confirm_rule.action_code` CHECK **UNCHANGED** — regression check confirms the 3-element enforcement-action enum (`require_operator_confirm` / `route_to_operator_review` / `block`) is preserved; no MCF cert action codes leaked into this column
6. All 10 `mcf.*` tables empty (M2 + M3 + cert-amendment + M4)
7. M3 + cert-amendment substrate intact (regression): M3 trigger body still references `mcf.certification_record`; `fk_mcs_cert` still targets `mcf.certification_record`; shared CHECKs still admit `'mcf'` / `'active_to_superseded'`

**Behavioral (8–13) — tx-rolled-back synthetic-row exercises:**

| # | Path | Expectation | Actual |
|---|---|---|---|
| 8 | INSERT PE result (no cert) | succeeds | succeeds, rolled back |
| 9 | INSERT PE result with invalid `pe_check_code='PE-MC-99-invalid'` | rejected by `mper_pe_check_code_chk` (specific constraint name asserted per PR #108) | rejected with exact constraint name |
| 10 | INSERT PE result with invalid `verdict_code='MAYBE'` | rejected by `mper_verdict_code_chk` (specific constraint name asserted per PR #108) | rejected with exact constraint name |
| 11 | INSERT idempotency row with valid `status='pending'` | succeeds | succeeds, rolled back |
| 12 | INSERT idempotency with invalid `status='frobnicated'` | rejected by `mcwi_status_chk` (specific constraint name asserted per PR #108) | rejected with exact constraint name |
| 13 | INSERT PE result with bogus `certification_record_id` UUID | rejected by `fk_mper_cert` FK (specific FK name asserted per PR #108) | rejected with exact FK name |

**Cleanup (14):**

14. All 10 `mcf.*` tables empty after verifier (test rows wrapped in transactions + `throw new Error('__rollback__')`)

### 2.3 Integration spec 7-test summary (all PASS, post-PR #108)

Per DBCP §14.4 / §18.1, the integration spec at `bc-core/src/registry/mcf/mcf-cert-writer.service.integration.spec.ts` exercises the live DB with `BCCORE_INTEGRATION_DB=1`:

1. Full lifecycle: draft → review → approved → active end-to-end via service; M3 trigger flips `is_current=TRUE` on the activating MCV; PE result rows carry non-null `certification_record_id` (cert-before-PE-rows F-2/P-2)
2. is_current flip + demotion: second activation on same MC demotes the first; `isCurrentDemoted` (B2 fix per PR #107 review) surfaces the demoted MCV uid
3. Archived `policyVersion` rejection: `InvalidInputError` thrown before tx opens; no MC row created
4. Idempotency commit visibility: row persisted as `status='committed'` with the correct `result_json`
5. Idempotency cache-hit: second call with same key + same action returns cached result; only 1 MC ever created
6. Idempotency mismatched-action: `IdempotencyKeyReuseError` thrown
7. Idempotency stuck-pending takeover via atomic CAS (per §11.6) using compressed `TINY_IDEMPOTENCY_OPTS` (200 ms threshold)

### 2.4 Independent confirm (separate `node + postgres` query)

| Metric | Value |
|---|---|
| `mcf.metric_publication_eligibility_result` exists | true |
| `mcf.metric_cert_writer_idempotency` exists | true |
| `contract.framework_policy` mcf rows | 1 (`mcf_v1` / `1.0.0` / `scope_code=mcf` / `adr_ref=DEC-c3e57f` / eligible_operations `[metric_create, metric_transition, metric_supersede]`) |
| `contract.operator_confirm_rule` mcf rows | 2 (both `action_code='require_operator_confirm'`, `rationale_required=true`) |
| `operator_confirm_rule.action_code` CHECK | UNCHANGED — `('require_operator_confirm','route_to_operator_review','block')` |
| `mcf.*` table count | 10 (was 8; +2 for M4-shipped tables) |
| All 10 `mcf.*` table row counts | 0 each |

All counts and definitions match the DDL specification and the verifier output from an independent query path.

## 3. Evidence

Audit artifacts committed to bc-core via [PR #109](https://github.com/selenite-git-admin/bc-core/pull/109) under `scripts/audit-output/`:

**Basis-of-apply dry-run** (run immediately before psql apply, 04:37:59 UTC):
- `mcf-m4-dry-run-2026-05-27T04-37-59-453Z.summary.md`
- `mcf-m4-dry-run-2026-05-27T04-37-59-453Z.precondition.jsonl`
- `mcf-m4-dry-run-2026-05-27T04-37-59-453Z.planned-sql.sha256.txt` (DDL sha256 = `de03ee94…`; pins what was applied for future drift detection)

**Final successful post-apply verifier** (after PR #108 merge, 05:01:04 UTC):
- `mcf-m4-post-apply-2026-05-27T05-01-04-658Z.summary.md`
- `mcf-m4-post-apply-2026-05-27T05-01-04-658Z.evidence.jsonl`

**Excluded from the evidence PR:** 8 earlier dev-cycle / diagnostic artifacts — 4 pre-apply dry-run iterations (03:23 / 03:38 / 04:03 / 04:24); 1 post-apply dry-run (04:52, exit 8 by design since the clean-slate gate correctly fails post-apply); 1 initial failed post-apply verifier (04:39, exit 10 — described in §4.1 as the diagnostic that surfaced the bugs PR #108 fixed); 2 patch-branch verifier runs (04:46 / 04:58, pre-merge of PR #108). Same exclusion discipline as M3 PR #106 (which excluded `01:42` / `01:47` in favor of the `01:58` basis-of-apply) and M3 PR #104 (which excluded `14:03` / `14:06` / `14:30` in favor of the `14:51` basis-of-apply).

The post-apply summary contains the full per-check JSON for downstream audit. The DDL hash file (`.planned-sql.sha256.txt`) pins what was applied for future drift detection.

Integration test evidence is **not committed as a separate artifact** (vitest doesn't emit JSON output by default for this spec). The 7/7 PASS result is recorded in §2.3 above; reproducible via `BCCORE_INTEGRATION_DB=1 vitest run src/registry/mcf/mcf-cert-writer.service.integration.spec.ts` against `bc_platform_dev` post-apply.

## 4. Operational observations

### 4.1 Initial post-apply verifier failure + PR #108 root-cause and fix

The first post-apply verifier run after psql apply exited **10**, with verifier checks #8 and #13 failing and checks #9 / #10 / #12 passing **for the wrong reason** (false-positives). Diagnosis surfaced two related but distinct bugs:

**Bug 1 — verifier helper invalid `hash_algorithm_version`** (`scripts/mcf-m4-post-apply-verification.mjs`):
The `setupSyntheticApprovedMcv` helper inserted a parent MC with `hash_algorithm_version = 'mcf-m4-verifier-v1'`. The M2 substrate CHECK `mc_hash_algorithm_version_chk` requires the regex `^mcf-[a-z-]+-v[0-9]+$` — the digit `4` in `m4` violates the `[a-z-]+` middle segment (the segment forbids digits). The INSERT failed, propagating a generic `"check constraint"` error message that the loose-pattern assertions in checks #9 / #10 / #12 / #13 matched **falsely** — they were satisfied by the wrong constraint firing, not the intended one. The M3 cert-amendment verifier had correctly used `mcf-amendment-verifier-v1` (letters/hyphens only); the M4 verifier copy-paste introduced the `m4` regression.

**Bug 2 — `MockMcfHashComputer` value violates same substrate CHECK** (`src/registry/mcf/mcf-hash-computer.mock.ts`):
The mock returned `hashAlgorithmVersion = 'mock-1.0.0'`. This value also violates `^mcf-[a-z-]+-v[0-9]+$` (wrong prefix `mock-` not `mcf-`; wrong version format `1.0.0` not `-v[0-9]+`). Any integration test calling `approveForActivation` against the live substrate would have failed at the parent MC hash UPDATE — but the integration spec hadn't run yet (gated on `BCCORE_INTEGRATION_DB=1`). The substrate exposed the latent bug that unit tests (mocking the DB) couldn't catch.

Bug 2 created a design tension: the substrate CHECK required `mcf-*`, but the production guard rejected `startsWith('mock-')`. A string can't satisfy both. PR #108 resolved this by:
- Changing mock to return `'mcf-mock-v1'` (substrate-compatible)
- Updating production guard to detect `startsWith('mcf-mock-') || startsWith('mock-')` (new marker + defense-in-depth against any legacy `mock-*` values that may exist)

PR #108 also tightened the verifier's false-pass assertions to require the SPECIFIC intended constraint names (`mper_pe_check_code_chk` for #9, `mper_verdict_code_chk` for #10, `mcwi_status_chk` for #12, `fk_mper_cert` for #13) — the original loose `msg.includes('check constraint')` pattern is no longer accepted.

**After PR #108 merge** (commit `ed322d6` on bc-core main), the post-apply verifier exits 0 (14/14 PASS) and the integration spec passes 7/7 against the live DB. The substrate itself was correct throughout; only the test-helper + mock needed adjustment to be substrate-compatible.

### 4.2 BEGIN/COMMIT atomicity discipline — successfully validated again

Mirroring the M3 cert-amendment apply, the M4 DDL is wrapped in `BEGIN;...COMMIT;` for whole-file atomicity (per DBCP §12.6). With `ON_ERROR_STOP=1` at the psql layer, this guarantees that all M4-shipped objects (tables + indexes + seeds + comments) commit together or roll back together. The apply succeeded cleanly on the first attempt; no partial-apply scenario was triggered. The 3 seed INSERTs (2 `operator_confirm_rule` + 1 `framework_policy`) were correctly admitted by the post-cert-amendment shared CHECKs.

### 4.3 Substrate-vs-mock incompatibility as a forward design pattern

The Bug 2 episode (§4.1) reveals a generalizable design tension worth recording: **mock implementations that need to be exercised against live substrate must produce values that satisfy substrate CHECKs**, while still being detectable as mocks by application-layer guards. The pattern PR #108 adopted — substrate-compatible mock marker prefix (`mcf-mock-*`) plus a guard that detects both new and legacy markers — is the recommended approach for any future MCF mock that needs live-DB integration testing. Future hash-computer implementations from M7/M8 will use real algorithm prefixes (e.g. `mcf-formula-v1`, `mcf-package-v1`) that automatically bypass the guard.

### 4.4 Operational observations from M2/M3/M3-amendment carry over

The carry-over observations from `mcf-m2-ddl-apply-closeout.md` §4, `mcf-m3-ddl-apply-closeout.md` §4, and `mcf-m3-cert-amendment-apply-closeout.md` §4 — psql client at `C:\Program Files\PostgreSQL\18\bin\psql.exe`, bc-postgres MCP schema-cache lag, PowerShell `.env`-sourcing pattern, `information_schema.triggers` row-count nuance, BEGIN/COMMIT atomicity validated, pre-amendment trigger body snapshot pattern (M3 only) — all still hold without change.

## 5. What stays closed

- **M5 panel substrate** — next blocked gate. The Metric Authoring Panel substrate (M5) consumes M4 cert-writer service and PE result substrate; cannot start until operator authorizes.
- **M7 (formula AST canonicalization)** — M4 ships `McfHashComputer` interface; the production implementation that produces real `formula_intent_hash` / `variable_binding_set_hash` / `filter_set_hash` / `identity_tuple_hash` is M7's deliverable. Until M7 lands, only `MockMcfHashComputer` is wired (substrate-compatible per §4.3; production guard blocks accidental use in `NODE_ENV='production'` per §7.5).
- **M8 (package signature)** — same pattern as M7 for `package_signature_hash`.
- **M9 + M10 (self-verification fixture + verifier engine)** — gated on M7/M8.
- **M11 (Metric Authoring Panel implementation)** — gated on M5.
- **M12 (Metric Publication Panel)** — gated on M11.
- **M14 (publication REST endpoint) + M15 (supersession endpoint)** — gated on M12.
- **MCF metric contract authoring** — substrate is empty; no production rows in any of the 10 `mcf.*` tables. The M4 service exists and works against synthetic rows (verified via integration spec) but is operationally dormant until M11+ wire it to real authoring flows.
- **`bc-postgres` MCP write access** — unchanged. `allow_write: false` confirmed across this session. The psql apply used the operator's own `DATABASE_URL` credential, not bc-postgres MCP.
- **BCF data** — `concept_registry.*` and other BCF substrate untouched. M4's seeds extended shared `contract.framework_policy` + `contract.operator_confirm_rule` with `scope='mcf'` rows (admissible per the M3 cert-amendment's shared CHECK extensions); BCF rows are unaffected by these additions.
- **M4 DDL further changes** — none. The merged PR #107 design + DBCP held; no amendments needed at dry-run or post-apply. The post-apply verifier-helper + mock issues (§4.1) were test-infrastructure bugs, not substrate bugs; PR #108 patched them without DDL changes.
- **Idempotency cleanup cron script** (`scripts/mcf-idempotency-cleanup.mjs` per DBCP §11.6) — deferred. M4 service supports the stuck-pending takeover path (CAS in `tryReclaimStuckPending`) so the cleanup script is not blocking; can ship as a follow-up.

## 6. MCF substrate arc — running tally

| Gate | Artifact | Date | State after |
|---|---|---|---|
| M1 — ADR | DEC-c3e57f / D422 (`bc-docs-v3/docs/adrs/ADR-c3e57f.md`) | 2026-05-26 | Authority locked |
| M2 — Identity substrate (DDL) | bc-core PR #101 / `92a9056` | 2026-05-26 | Code on main |
| M2 — Identity substrate (apply) | bc-core PR #102 / `mcf-m2-ddl-apply-closeout.md` | 2026-05-26 | 5 mcf tables live + empty |
| M3 — Lifecycle preflight | bc-docs-v3 `9e472cb` | 2026-05-26 | 13 decisions framed |
| M3 — Lifecycle DBCP | bc-docs-v3 `3147bd4` patched by `938fb0f` | 2026-05-26 | Q1 LOCKED + 5 clarity fixes |
| M3 — Lifecycle substrate (DDL) | bc-core PR #103 / `1a9796d` | 2026-05-26 | Code on main |
| M3 — Lifecycle substrate (apply) | bc-core PR #104 / `mcf-m3-ddl-apply-closeout.md` | 2026-05-26 | 7 mcf tables live + empty; 7 triggers attached |
| M3/M4 — Cert substrate correction preflight | bc-docs-v3 `637e667` | 2026-05-26 | 10 blockers enumerated; Option C accepted |
| M3 — Cert-amendment DBCP | bc-docs-v3 `78c7f74` patched by `06d369c` | 2026-05-26 | 11 operator approvals (O-Amendment-1..O-Amendment-11) |
| M3 — Cert-amendment (DDL) | bc-core PR #105 / `b059b18` | 2026-05-27 | Code on main |
| M3 — Cert-amendment (apply) | bc-core PR #106 / `mcf-m3-cert-amendment-apply-closeout.md` | 2026-05-27 | 8 mcf tables live + empty; trigger redirected; supersession FK redirected; shared CHECKs additively extended; action_code unchanged |
| M4 — Lifecycle certification DBCP rewrite | bc-docs-v3 `d9bae5a` patched by `3983530` | 2026-05-27 | 29 patches (P-1..P-29); 13 operator approvals (O-1..O-13) |
| M4 — Lifecycle certification (DDL) | bc-core PR #107 / `e34408c` | 2026-05-27 | Code on main |
| M4 — Verifier+mock substrate fix | bc-core PR #108 / `ed322d6` | 2026-05-27 | Code on main; verifier 14/14 + integration 7/7 PASS |
| **M4 — Lifecycle certification (apply)** | **bc-core PR #109 + this doc** | **2026-05-27** | **10 mcf tables live + empty; 2 new M4 tables shipped; 1 framework_policy + 2 operator_confirm_rule mcf seeds; action_code unchanged; service code + integration tests live; operationally dormant pending M5+ panel** |

The MCF substrate arc is structurally + behaviorally consistent through the M4 apply. The M4 service layer (`McfCertWriterService`) is live and verified end-to-end against the live substrate via the integration spec. **The M4 substrate gate is closed.**

## 7. Recommended next gate

Per DBCP §17 / M4 non-responsibilities (§16) and the overall MCF arc, the next operator-authorized gate options are (in dependency order):

1. **M5 — Metric Authoring Panel substrate preflight** (docs-only): identify the schema + service needs for the M11 panel that consumes M4 cert-writer service. M5 is the natural downstream consumer; until it lands, M4 is operationally dormant.
2. **M7 — Formula AST canonicalization preflight** (docs-only): the real implementation of `McfHashComputer.computeAllForApproval` for the 3 formula-related hashes (`formulaIntentHash`, `variableBindingSetHash`, `filterSetHash`). Until M7 ships, only `MockMcfHashComputer` is available (and blocked from production by the §7.5 guard).
3. **M8 — Package signature preflight** (docs-only): the real implementation for `packageSignatureHash` + `identityTupleHash`. Often co-developed with M7.
4. **Idempotency cleanup cron script** (small, infrastructure-only): `scripts/mcf-idempotency-cleanup.mjs` per DBCP §11.6 — deletes `rolled_back` rows >30 days old; promotes stuck `pending` rows >5 min to `rolled_back`. Service supports the takeover path so this is non-blocking; can ship anytime.

This closeout does **NOT** open any of these.

## Document verification

- **Apply event captured** — DDL source, sha256, target DB, authority chain (DBCP + M3 cert-amendment closeout), operator approval pattern.
- **All apply steps recorded** with exit codes — dry-run exit 0 / live psql exit 0 / initial verifier exit 10 (with §4.1 root-cause arc) / final verifier exit 0 (14/14) / integration spec 7/7.
- **All 14 post-apply checks PASS** — itemized in §2.2, including 6 behavioral synthetic-row exercises + 1 regression assertion that `operator_confirm_rule.action_code` CHECK is unchanged.
- **All 7 integration tests PASS** — itemized in §2.3, including full lifecycle + is_current demotion + archived-policy rejection + idempotency commit/cache-hit/mismatch/stuck-pending takeover.
- **Independent confirm captured** (§2.4) — separate `node + postgres` query path validates structural + content claims.
- **Operational observations preserved** (§4) — initial verifier failure root cause + PR #108 fix arc; BEGIN/COMMIT atomicity re-validated; substrate-vs-mock design tension recorded as forward pattern.
- **No code changes, no further DDL, no row writes.** This doc only.
- **Closed gates restated** (§5) — M5 panel substrate + M7/M8 hash implementations + downstream all blocked pending operator authorization.
- **MCF substrate arc tally updated** (§6) — 15 gates from M1 ADR through M4 apply. The M4 substrate gate is closed.
