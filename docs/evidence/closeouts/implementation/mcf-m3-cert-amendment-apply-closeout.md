---
uid: mcf-m3-cert-amendment-apply-closeout
title: MCF M3 Certification-Target Amendment — Live DDL Apply Closeout
description: Closeout for the MCF M3 certification-target amendment live DDL apply against bc_platform_dev on 2026-05-27. Applied docker/redesign/05a-mcf-cert-amendment.sql (DDL pinned at bc-core PR #105 / b059b18; sha256 c1fe3fc1f17160c20f8c9f96941954ff48df5ddb59b03efbbb876e7eb59bbd64) under explicit operator approval per CLAUDE.md Database Change Protocol. Realizes the 7 accepted D-Correction operator decisions from the cert substrate correction preflight (637e667) — Option C hybrid: per-framework mcf.certification_record sibling + additive shared CHECK extensions (framework_policy.scope_code += 'mcf'; operator_confirm_rule.scope += 'mcf'; operator_confirm_rule.transition += 'active_to_superseded'; action_code unchanged per D-Correction-4). Dry-run all 8 preconditions PASS; psql exit 0 inside BEGIN/COMMIT whole-file transaction wrapper per §9.4 atomicity discipline; post-apply verifier all 15 checks PASS including end-to-end positive #13 (sibling cert exists → approved→active SUCCEEDS) + negative #14 (no cert → rejected with exact error message). Live state: 8 mcf.* tables (7 prior + new certification_record); M3 trigger redirected to sibling; supersession FK redirected; shared CHECKs additively extended; operator_confirm_rule.action_code regression-asserted unchanged; all 8 mcf tables empty. Evidence artifacts committed to bc-core via PR #106 (6 files: 4 dry-run + 2 post-apply; 8 earlier dev-cycle artifacts from PR #105 development correctly excluded). M3 substrate stays applied throughout amendment per D-Correction-3 (forward-only; CREATE OR REPLACE FUNCTION + ALTER TABLE DROP/ADD CONSTRAINT + CREATE TABLE new sibling — no DROP/RECREATE). M4 implementation remains BLOCKED until M4 DBCP is rewritten around mcf.certification_record per D-Correction-2 / D-Correction-6 — next gate.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m3-cert-amendment-apply-closeout
---

# MCF M3 Certification-Target Amendment — Live DDL Apply Closeout

## 1. What landed

The MCF M3 certification-target amendment DDL was applied live against `bc_platform_dev` on **2026-05-27**, resolving the Foundation Governance Substrate mismatch that halted M4 implementation per the cert substrate correction preflight. The amendment introduces a new `mcf.certification_record` per-framework sibling table, redirects the M3 state-transition trigger's cert lookup target, redirects the supersession FK, and additively extends 3 shared CHECK enums on `contract.framework_policy` + `contract.operator_confirm_rule`. M3 substrate stays applied throughout (no rollback; no DROP/RECREATE).

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/05a-mcf-cert-amendment.sql` |
| Pinned at | bc-core PR #105 / commit `b059b18` (HEAD = origin/main) |
| DDL sha256 | `c1fe3fc1f17160c20f8c9f96941954ff48df5ddb59b03efbbb876e7eb59bbd64` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + correction preflight (`bc-docs-v3 637e667`) + amendment DBCP (`bc-docs-v3 06d369c` — 8 P-Amendment patches over 78c7f74) |
| 7 D-Correction decisions | All ACCEPTED — Option C hybrid; forward-only; sibling cert + shared CHECK extensions only for scope/transition (not action_code) |
| Operator approval | Explicit "Approved, apply M3 cert-amendment" in conversation per CLAUDE.md Database Change Protocol |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m3-cert-amendment-dry-run.mjs` | **exit 0** — 8/8 preconditions PASS; pre-amendment trigger body captured to rollback safety artifact per P-Amendment-7 |
| Live apply | `psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f docker/redesign/05a-mcf-cert-amendment.sql` | **exit 0** — inside `BEGIN;...COMMIT;` whole-file transaction wrapper (P-Amendment-1 / §9.4 atomicity): 1 CREATE TABLE + 5 CREATE INDEX + 1 CREATE FUNCTION + 8 ALTER TABLE (4 DROP/ADD pairs: FK redirect + 3 CHECK extensions) + 11 COMMENT |
| Post-apply verify | `node scripts/mcf-m3-cert-amendment-post-apply-verification.mjs` | **exit 0** — 15/15 checks PASS |

### 2.1 Post-apply 15-check summary (all PASS)

**Structural (1–10):**
1. `mcf.certification_record` present with 25 columns
2. 10 CHECK constraints present (incl. NF1 all-or-none on 6 panel-attestation fields — deliberate divergence from BCF's 7-field NF1 per §4.3 P-Amendment-3 since MCF requires `policy_version` independently)
3. 5 indexes present (incl. `idx_mcf_cert_lookup` for trigger hot path)
4. `fk_mcf_cert_panel_run` → `contract.panel_output_record` (cross-schema FK in DDL only per existing mcf/metric-supersession discipline)
5. `mcf.metric_supersession.fk_mcs_cert` REDIRECTED to `mcf.certification_record` (was `contract.certification_record`)
6. Trigger body: **exactly 1** occurrence of `FROM mcf.certification_record` AND **exactly 0** occurrences of `FROM contract.certification_record` (per P-Amendment-5 tightened assertion)
7. `contract.framework_policy_scope_code_chk` now admits `'mcf'` (additive)
8. `contract.operator_confirm_rule_scope_chk` now admits `'mcf'` (additive)
9. `contract.operator_confirm_rule_transition_chk` now admits `'active_to_superseded'` (additive)
10. `contract.operator_confirm_rule_action_chk` **UNCHANGED** — regression check confirms the 3-element enforcement-action enum is preserved per D-Correction-4 (M4 DBCP §10 misuse will be fixed in the M4 DBCP rewrite, not as a substrate change)

**Behavioral (11–14) — tx-rolled-back end-to-end exercises:**

| # | Path | Expectation | Actual |
|---|---|---|---|
| 11 | INSERT valid `metric_create` cert | succeeds | succeeds, rolled back |
| 12 | INSERT with invalid `action_code='random_invalid_action'` | rejected by `mcf_cert_action_code_chk` | rejected with exact error message |
| 13 | Synthetic mcv at `'approved'` + matching `metric_transition` cert in `mcf.certification_record` → UPDATE state to `'active'` | **SUCCEEDS** (proves amended trigger reads sibling) | succeeds, rolled back |
| 14 | Synthetic mcv at `'approved'` + NO cert → UPDATE state to `'active'` | **REJECTED** with `"requires a metric_transition cert"` | rejected with exact message |

**Cleanup (15):**
15. All 8 `mcf.*` tables empty after verifier (test rows wrapped in transactions + `throw new Error('__rollback__')`)

### 2.2 Independent confirm (separate `bc-postgres pg_query`)

| Metric | Value |
|---|---|
| `mcf.certification_record` exists | true |
| `fk_mcs_cert` target | `mcf.certification_record` |
| Trigger body new-FROM count | 1 (exactly) |
| Trigger body old-FROM count | 0 (exactly) |
| `framework_policy_scope_code_chk` | includes `'mcf'` |
| `operator_confirm_rule_scope_chk` | includes `'mcf'` |
| `operator_confirm_rule_transition_chk` | includes `'active_to_superseded'` |
| `operator_confirm_rule_action_chk` | UNCHANGED — `('require_operator_confirm','route_to_operator_review','block')` |
| `mcf` table count | 8 (was 7; +1 for `certification_record`) |
| All 8 mcf tables row count | 0 each |

All counts and definitions match the DDL specification and the verifier output from an independent query path.

## 3. Evidence

Audit artifacts committed to bc-core via [PR #106](https://github.com/selenite-git-admin/bc-core/pull/106) under `scripts/audit-output/`:

- `mcf-m3-cert-amendment-dry-run-2026-05-27T01-58-04-106Z.summary.md` + `.precondition.jsonl` + `.planned-sql.sha256.txt` + `.pre-amendment-trigger-body.sql` (rollback safety snapshot per P-Amendment-7)
- `mcf-m3-cert-amendment-post-apply-2026-05-27T02-00-21-493Z.summary.md` + `.evidence.jsonl`

**Excluded from the evidence PR:** 8 earlier dev-cycle artifacts from the PR #105 development cycle — two dry-run runs at `01:42:44` (initial verification during PR #105 dev) and `01:47:04` (re-run during PR #105 pre-merge review). They are pre-apply experimentation, not the basis-of-apply. Same exclusion discipline as M3 PR #104 (which excluded `14:03` / `14:06` / `14:30` in favor of the `14:51` basis-of-apply).

The post-apply summary contains the full per-check JSON for downstream audit. The DDL hash file (`.planned-sql.sha256.txt`) pins what was applied for future drift detection. The pre-amendment trigger body snapshot supports the emergency rollback DDL per DBCP §10 (forward-only is the standard discipline; rollback is documented + guarded but emergency-only).

## 4. Operational observations

### 4.1 BEGIN/COMMIT atomicity discipline — successfully validated

This is the first MCF amendment that touched BCF-shared `contract.*` CHECK constraints. The whole-file `BEGIN; ... COMMIT;` wrapper inside the DDL file (per DBCP §9.4 + P-Amendment-1) was the deliberate safeguard against partial-apply state on `framework_policy` and `operator_confirm_rule`. The apply succeeded cleanly; no partial-apply scenario was triggered. The pattern is now established for future MCF amendments that touch shared substrate.

`ON_ERROR_STOP=1` at the psql layer + `BEGIN;...COMMIT;` inside the DDL file together guarantee atomicity. Neither alone is sufficient.

### 4.2 Pre-amendment trigger body capture (rollback safety)

The dry-run script captures the verbatim pre-amendment function definition (via `pg_get_functiondef('mcf.fn_mcv_state_transition_check'::regproc::oid)`) to a `.pre-amendment-trigger-body.sql` artifact before any apply. This is the first time the MCF arc has adopted this snapshot pattern. The captured body is the exact text the emergency rollback DDL (Step 6 of `05a-mcf-cert-amendment-rollback.sql`) would restore. Future MCF amendments that ALTER trigger functions should adopt the same snapshot discipline.

### 4.3 Behavioral verifier (untested-until-apply) worked first time

The post-apply verifier's behavioral checks #13 + #14 use a synthetic mcv setup helper (`setupSyntheticApprovedMcv`) that INSERTs a parent MC with all 6 hash columns populated (via deterministic placeholder values matching the M2 CHECK regexes), then walks state from `'draft'` → `'review'` → `'approved'`. The helper had not been exercised end-to-end before this apply (the M3 PR #105 review noted this as LOW finding L-2). The helper worked first time at apply: both #13 (positive: cert exists → activation succeeds) and #14 (negative: no cert → activation rejected with the exact `"requires a metric_transition cert"` message) passed. The verifier design is validated.

### 4.4 Operational observations from M2/M3 carry over

The carry-over observations from `mcf-m2-ddl-apply-closeout.md` §4 and `mcf-m3-ddl-apply-closeout.md` §4 — psql client at `C:\Program Files\PostgreSQL\18\bin\psql.exe`, bc-postgres MCP schema-cache lag, PowerShell `.env`-sourcing pattern, `information_schema.triggers` row-count nuance — all still hold without change.

## 5. What stays closed

- **M4 DBCP rewrite** — next gate. The M4 DBCP at `bc-docs-v3 e56fc7e` references `contract.certification_record` throughout §9 + §10 and assumes `governance_scope='mcf'`. It must be rewritten around `mcf.certification_record` (per D-Correction-2 + D-Correction-6) before M4 implementation can re-open. The rewrite also fixes the §10 semantic confusion between `operator_confirm_rule.action_code` (enforcement directive) and `cert.action_code` (act being authorized) per D-Correction-6.
- **M4 implementation** — still blocked. After M4 DBCP rewrite ships, M4 implementation PR can open against the new design.
- **M5+ downstream** — panel substrate, formula AST, package signature, fixture, verifier, panel impl — all depend on M4.
- **MCF metric contract authoring** — substrate is empty; no rows in `mcf.*` (including `mcf.certification_record`).
- **`bc-postgres` MCP write access** — unchanged. `allow_write: false` confirmed across this session. The psql apply used the operator's own `DATABASE_URL` credential, not bc-postgres MCP.
- **BCF data** — `concept_registry.*` and other BCF substrate untouched. Shared `contract.framework_policy` + `contract.operator_confirm_rule` were extended additively (every existing BCF row satisfies the new CHECKs).
- **M3 amendment DDL further changes** — none. The merged PR #105 design + DBCP held; no amendments needed at dry-run or post-apply.

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
| **M3 — Cert-amendment (apply)** | **bc-core PR #106 + this doc** | **2026-05-27** | **8 mcf tables live + empty; trigger redirected; supersession FK redirected; shared CHECKs additively extended; action_code unchanged** |

The MCF substrate arc is structurally + behaviorally consistent through the cert-amendment apply. The Foundation gate violation that halted M4 implementation is **resolved at the substrate layer**.

## 7. Recommended next gate

Per the correction preflight `637e667` §8 sequencing + D-Correction-2:

1. **M4 DBCP rewrite** (docs-only) — substantive rewrite of `metric-context-framework-m4-lifecycle-certification-dbcp.md` (currently at `e56fc7e`, blocked design). Specific edits:
   - D-19: reverse "REUSE" to "PER-FRAMEWORK SIBLING — confirms M3 amendment"
   - §9: rewrite cert column matrix for `mcf.certification_record`'s 25-column shape (no `governance_scope`; no `target_registry_id`)
   - §10: correct `operator_confirm_rule.action_code` semantic misuse per D-Correction-6 (the column takes enforcement directives, not cert action codes); fix seed `transition` values to underscore notation; confirm `scope='mcf'` admissible after this amendment landed
   - §14: dry-run + verifier assumptions updated for the new substrate state (M4 dry-run can now check that `mcf.certification_record` exists, that shared CHECK extensions are in place, etc.)
2. **M4 implementation PR** — per the rewritten DBCP; mirrors M2 PR #101 + M3 PR #103 pattern (NO DB APPLY)
3. **M4 DDL apply** — separate operator-authorized DCP session
4. **M4 evidence PR** — mirrors PR #102 + PR #104 + PR #106 pattern

This closeout does **NOT** open any of these.

## Document verification

- **Apply event captured** — DDL source, sha256, target DB, authority chain (preflight + DBCP + 7 D-Correction decisions), operator approval pattern.
- **All three apply steps recorded** with exit codes — dry-run / live psql / post-apply verifier all exit 0.
- **All 15 post-apply checks PASS** — itemized in §2.1, including 4 behavioral end-to-end exercises + 1 regression assertion that `operator_confirm_rule.action_code` CHECK is unchanged.
- **Independent confirm captured** (§2.2) — separate `pg_query` path validates structural + content claims.
- **Operational observations preserved** (§4) — BEGIN/COMMIT atomicity validated, pre-amendment trigger body snapshot pattern adopted, behavioral verifier validated end-to-end first time.
- **No code changes, no further DDL, no row writes.** This doc only.
- **Closed gates restated** (§5) — M4 DBCP rewrite + M4 implementation + downstream all blocked pending operator authorization.
- **MCF substrate arc tally updated** (§6) — 11 gates from M1 ADR through M3 cert-amendment apply.
