---
uid: mcf-m7-m8-apply-closeout
title: MCF M7/M8 Formula AST Storage + Trigger Amendment — Live DDL Apply Closeout
description: Closeout for the MCF M7/M8 Formula AST + Hash/Signature Authority live DDL apply against bc_platform_dev on 2026-05-27. Applied docker/redesign/07-mcf-formula-ast-storage.sql (DDL pinned at bc-core PR #110 / 91f83ee; sha256 c9d4203d9b8f6e2ffeb24adf7b3e139a91ca84dd42b47404443f679bf9e0fa00) under explicit operator approval per CLAUDE.md Database Change Protocol. Realizes the substrate side of the M7/M8 combined DBCP (62ec707) — adds the canonical AST storage column formula_ast_canonical_json (jsonb NOT NULL with placeholder default) on mcf.metric_contract_version + amends mcf.fn_mcv_descriptive_immutability_check per §13.2.1 (now 3 IFs: pure state-only permit / approved+superseded Q1 lock / review-or-mixed AST identity-bearing rejection). Both changes commit atomically inside one BEGIN/COMMIT per §13.2.1 + §17.2. Dry-run all 8 preconditions PASS including 3 HARD-GATEs (M4 substrate present + column absent + trigger un-amended); psql exit 0; pre-amendment trigger body captured to rollback-safety snapshot (1860 chars, mirrors M3 cert-amendment discipline). Post-apply verifier 9/9 PASS — 3 structural (column shape + L-3 tightened JSON deep-equal default match + trigger body amendment with 8 occurrences of formula_ast_canonical_json) + 5 behavioral synthetic-MCV exercises (draft permit / review reject / approved Q1 lock / mixed state+AST reject / state-only transition permit) + 1 cleanup discipline. Live state: 10 mcf.* tables, all empty; M4 seeds intact (1 mcf framework_policy + 2 mcf operator_confirm_rule); BCF concept_registry.* untouched. M7/M8 service code live but operationally dormant — no real MCF metric contracts authored (panel substrate is M5/M11; not in M7/M8 scope). 6 basis-of-apply artifacts committed to bc-core via PR #111 (4 dry-run + 2 post-apply; explicitly staged, no bulk-add). M5 panel substrate, M9 fixture substrate, M10 verifier engine remain closed and not evidenced — those are subsequent operator-authorized gates.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m7-m8-apply-closeout
---

# MCF M7/M8 Formula AST Storage + Trigger Amendment — Live DDL Apply Closeout

## 1. What landed

The MCF M7/M8 Formula AST + Hash/Signature Authority substrate DDL was applied live against `bc_platform_dev` on **2026-05-27**, completing the substrate side of the M7/M8 arc. The DDL ships ONE new column on `mcf.metric_contract_version` (`formula_ast_canonical_json jsonb NOT NULL` with placeholder default) and amends the M3 descriptive-immutability trigger function `mcf.fn_mcv_descriptive_immutability_check` per DBCP §13.2.1 (3 IFs: pure state-only permit / approved+superseded Q1 lock / review-or-mixed AST identity-bearing rejection). Both changes commit atomically inside one `BEGIN/COMMIT` whole-file transaction wrapper.

M3 + cert-amendment + M4 substrate stay applied throughout (no DROP/RECREATE; no touches to `mcf.certification_record`, the M3 state-transition trigger, FK constraints, or shared CHECK constraints).

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/07-mcf-formula-ast-storage.sql` |
| Rollback source | `bc-core/docker/redesign/07-mcf-formula-ast-storage-rollback.sql` |
| Pinned at | bc-core PR #110 / commit `91f83ee` (HEAD of `main` at apply time) |
| DDL sha256 | `c9d4203d9b8f6e2ffeb24adf7b3e139a91ca84dd42b47404443f679bf9e0fa00` |
| Rollback sha256 | `2122b67efe46d192d0d3d2f0390555f193e354a1e76c7ba9924db22c15e6e412` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + M7/M8 DBCP (`bc-docs-v3 62ec707` — 4 patch rounds: initial → 11-patch review → 8-patch re-review → 3-patch final + M-1/M-2/M-3 post-impl review patch in PR #110) + M4 apply closeout (`bc-docs-v3 c2bc3fc`) |
| Operator approval | Explicit "Operator authorizes merge of bc-core PR #110…" → "Open the M7/M8 small-DDL apply gate" → pre-authorized apply in same prompt per CLAUDE.md Database Change Protocol |
| Evidence PR | bc-core PR #111 (6 basis-of-apply artifacts: 4 dry-run + 2 post-apply; explicitly staged, no bulk-add from `scripts/audit-output/`) |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m7-m8-dry-run.mjs` | **exit 0** — 8/8 checks PASS including 3 HARD-GATEs; DDL sha256 + pre-amendment trigger body captured |
| Live apply | `cat docker/redesign/07-mcf-formula-ast-storage.sql \| docker exec -i bc-postgres psql -U barecount -d bc_platform_dev -v ON_ERROR_STOP=1` | **exit 0** — inside `BEGIN;...COMMIT;` whole-file transaction wrapper (per §13.2.1 + §17.2 atomicity discipline): `BEGIN → ALTER TABLE → CREATE FUNCTION → COMMENT → COMMIT` |
| Post-apply verifier | `node scripts/mcf-m7-m8-post-apply-verification.mjs` | **exit 0** — 9/9 checks PASS |

### 2.1 Dry-run 8-check summary (all PASS)

**Numbered checks:**
1. M4 substrate prereq — all 10 `mcf.*` tables present (HARD-GATE)
2. `mcf.metric_contract_version.formula_ast_canonical_json` ABSENT — clean slate (HARD-GATE)
3. M3 trigger `fn_mcv_descriptive_immutability_check` body does NOT yet enumerate `formula_ast_canonical_json` — clean slate for amendment (HARD-GATE)
4. All 10 MCF tables empty — no rows would be affected by DEFAULT backfill
5. Pre-amendment trigger body captured for rollback safety (1860 chars → `.pre-amendment-trigger-body.sql`, mirrors M3 cert-amendment discipline)
6. Forward DDL parse + statement counts + BEGIN/COMMIT pair: 1 `ALTER TABLE` + 1 `CREATE OR REPLACE FUNCTION` + 1 `COMMENT ON COLUMN` + 0 `CREATE TABLE` + 0 `INSERT`
7. Rollback DDL parse + precondition guard + matching drop + trigger restore: 1 `DO/RAISE` + 1 `CREATE OR REPLACE FUNCTION` + 1 `DROP COLUMN` + BEGIN/COMMIT
8. DDL sha256 captured for drift detection (forward + rollback)

### 2.2 Post-apply 9-check summary (all PASS)

**Structural (1–3):**
1. `mcf.metric_contract_version.formula_ast_canonical_json` present (jsonb NOT NULL)
2. `formula_ast_canonical_json` DEFAULT deep-equals DDL placeholder per L-3 tightened check (parses the `pg_get_expr` output's JSON body and deep-equals against `{"kind":"placeholder","reason":"created_before_m7_apply"}` rather than substring-matching — divergent defaults like `{"kind":"placeholder","extra":"x"}` would now FAIL)
3. M3 trigger body enumerates `formula_ast_canonical_json` with **8 occurrences** (enumerated set in 1st IF + third-IF disjuncts + RAISE messages) — matches §13.2.1 expected structure

**Behavioral (4–8) — synthetic-MCV `BEGIN;...ROLLBACK;` exercises:**

4. UPDATE-only-formula_ast on `draft` row → **PERMITTED** (default RETURN NEW path; drafts may freely mutate AST)
5. UPDATE-only-formula_ast on `review` row → **REJECTED** (third IF first disjunct: `OLD.state='review' AND AST changed`)
6. UPDATE-only-formula_ast on `approved` row → **REJECTED** (second IF Q1 lock: `OLD.state IN ('approved','superseded')`)
7. UPDATE state + formula_ast simultaneously on draft→review → **REJECTED** (third IF second disjunct: `OLD.state IS DISTINCT FROM NEW.state AND AST changed` — the previously-missed case from B-NEW-1 review patch)
8. UPDATE state-only (no AST change) on draft→review → **PERMITTED** (first IF: all listed columns including the NEW `formula_ast_canonical_json` unchanged)

**Cleanup (9):**

9. All MCF tables empty after verifier completes — `BEGIN;...ROLLBACK;` discipline preserved across all 5 behavioral exercises

## 3. Live state recap (post-apply)

### 3.1 What's now live

| Surface | Change |
|---|---|
| `mcf.metric_contract_version.formula_ast_canonical_json` | NEW column — `jsonb NOT NULL DEFAULT '{"kind":"placeholder","reason":"created_before_m7_apply"}'::jsonb` |
| `mcf.fn_mcv_descriptive_immutability_check` body | AMENDED — 3 IFs covering 3 semantic roles per §13.2.1 |
| Drizzle schema `metric-contract-version.ts` | Mirrors the column with byte-matching default expression per §13.4 |
| `bc-core/src/registry/mcf/` services | LIVE: `FormulaCanonicalizationService` + `PackageSignatureService` + `McfHashComputerCoordinator` (3 new) + `mcf-jcs.ts` utility (RFC 8785 JCS) |
| `McfHashComputer` interface | WIDENED — `ComputeAllForApprovalInput` now REQUIRES both `metricContractUid` AND `metricContractVersionUid` per D-M7-10 input-only widening |
| `McfCertWriterService.approveForActivation` | Extended: `lockMcvAndAssertState` SELECTs `formula_ast_canonical_json` under FOR UPDATE; new `assertNonPlaceholderAst` guard rejects placeholder AST BEFORE hash compute per §12.5.1 / O-10 |
| `MockMcfHashComputer` signature | Updated to match widened interface (body still ignores `metricContractVersionUid`) |
| Algorithm version constant | `MCF_HASH_ALGORITHM_VERSION = 'mcf-hash-v1'` per D-M7-9 |
| Golden anchors | Hardcoded sha256 constants per L-1 forever-lock; M-2 patch eliminated tautology |
| Production guard | Preserved — rejects `mcf-mock-*` and legacy `mock-*` prefixes when `NODE_ENV=production` |

### 3.2 Independent bc-postgres MCP read-only confirmation (`allow_write=false`)

| Check | Result |
|---|---|
| `formula_ast_canonical_json` column present | **true** |
| Column data type | `jsonb` |
| Column nullable | `NO` |
| M3 trigger amended | **true** |
| Trigger body mentions of `formula_ast_canonical_json` | **8** (enumerated set + third-IF disjuncts + RAISE error messages) |
| 10 `mcf.*` table row counts | `0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0 / 0` |
| `contract.framework_policy` scope=mcf rows | **1** (`mcf_v1` — M4 seed intact) |
| `contract.operator_confirm_rule` scope=mcf rows | **2** (M4 seeds intact) |
| BCF `concept_registry.*` | **untouched** — 11 tables present; `business_concept` 10 rows; `entity` 2 rows |

### 3.3 What remains empty / closed

- All 10 `mcf.*` tables remain at **0 rows** — no real MCF metric contracts authored. The new column's placeholder DEFAULT exists for any future DEFAULT-backfilled row, but no such row exists.
- The service-side placeholder-AST guard in `McfCertWriterService.approveForActivation` would reject any MCV that reached `review → approved` carrying the placeholder, providing defense-in-depth alongside the trigger amendment.
- M4 seeded rows in `contract.framework_policy` + `contract.operator_confirm_rule` are intact (regression-asserted via separate read).
- BCF data untouched throughout the apply (the DDL strictly modifies `mcf.metric_contract_version` and the `mcf.fn_mcv_descriptive_immutability_check` function; no `concept_registry.*` reference).

## 4. Operational observations (new this session)

### 4.1 Combined column-add + trigger-replace atomicity validated

The whole-file `BEGIN;...COMMIT;` wrapper successfully committed two heterogeneous DDL operations together:
1. `ALTER TABLE mcf.metric_contract_version ADD COLUMN formula_ast_canonical_json jsonb NOT NULL DEFAULT ...`
2. `CREATE OR REPLACE FUNCTION mcf.fn_mcv_descriptive_immutability_check() RETURNS TRIGGER AS $$ ... $$ LANGUAGE plpgsql`

This is a meaningful step beyond the M3 cert-amendment pattern (which combined `CREATE TABLE` + `ALTER TABLE` + `CREATE OR REPLACE FUNCTION` of a *different* trigger) because the new column NAME is referenced inside the replaced function body (in the enumerated set and the third-IF disjuncts). A partial apply that committed the column without amending the trigger would leave a substrate enforcement gap (the trigger wouldn't catch identity-bearing AST mutation at review state); a partial apply that committed the trigger amendment without the column would fail validation at run-time (the trigger's `OLD.formula_ast_canonical_json` reference would not resolve). The atomic wrapper prevents both partial states.

### 4.2 L-3 tightened JSON deep-equal default check validated against live `pg_get_expr` output

The post-apply verifier's check #2 was tightened in the M-2/M-3 review-patch round (commit `d3969e6` on PR #110) from substring-only matching (`expr.includes('placeholder')`) to true JSON deep-equality. This is the **first time** the tightened check ran against a real `pg_get_expr` result — it correctly extracted the JSON body via `^\s*'(.*)'::jsonb\s*$/s` regex, `JSON.parse`d it, sort-keyed both sides, and deep-equaled against the expected placeholder object. A divergent default like `{"kind":"placeholder","reason":"created_before_m7_apply","extra":"x"}` would now fail this check (the original substring version would have passed).

### 4.3 Third-IF behavioral verification: rejection of mixed state+AST mutation

Check #7 of the post-apply verifier exercised the previously-missed `draft → review + AST change` case that the B-NEW-1 review patch added to §13.2.1's third IF. The synthetic-MCV `BEGIN;...ROLLBACK;` exercise constructed a draft MCV with a valid AST, then attempted a single UPDATE that simultaneously transitioned governance state to `review` AND mutated `formula_ast_canonical_json`. The trigger raised `check_violation` with the expected error message ("formula_ast_canonical_json is identity-bearing and cannot change at state=draft nor in the same UPDATE as a state transition (per MCF §4.6; M7/M8 DBCP §13.2.1). Use supersession."). This confirms the third IF's second disjunct fires as designed — supersession discipline is now substrate-enforced for the mixed-mutation pathway, not just service-side.

## 5. Evidence artifacts (committed to bc-core via PR #111)

**6 basis-of-apply artifacts** explicitly staged from `bc-core/scripts/audit-output/` (no bulk-add):

| # | File | Bytes | Purpose |
|---|---|---|---|
| 1 | `mcf-m7-m8-dry-run-2026-05-27T08-17-45-961Z.summary.md` | 3807 | Human-readable dry-run verdict (8/8 PASS) |
| 2 | `mcf-m7-m8-dry-run-2026-05-27T08-17-45-961Z.precondition.jsonl` | 2698 | Machine-readable per-check JSONL evidence |
| 3 | `mcf-m7-m8-dry-run-2026-05-27T08-17-45-961Z.planned-sql.sha256.txt` | 287 | Forward + rollback DDL byte fingerprints |
| 4 | `mcf-m7-m8-dry-run-2026-05-27T08-17-45-961Z.pre-amendment-trigger-body.sql` | 2384 | Live pre-amendment trigger body snapshot for rollback safety (1860-char `pg_get_functiondef` output) |
| 5 | `mcf-m7-m8-post-apply-2026-05-27T08-19-05-855Z.summary.md` | 3144 | Human-readable post-apply verifier verdict (9/9 PASS) |
| 6 | `mcf-m7-m8-post-apply-2026-05-27T08-19-05-855Z.evidence.jsonl` | 2991 | Machine-readable per-check JSONL evidence |

All other untracked files in `scripts/audit-output/` (M3/M4/D408/D409/D418 audits) were deliberately **excluded** from staging per the M3/M4 evidence-PR pattern.

## 6. What stays closed (subsequent gates — not evidenced here)

| Gate | Status |
|---|---|
| **M5 panel substrate** | CLOSED — gated on M7/M8 (now unblocked at substrate level) + separate operator authorization. NOT evidenced by this closeout. |
| **M9 fixture substrate** | CLOSED — gated on M5 + separate operator authorization. NOT evidenced. |
| **M10 verifier engine** | CLOSED — gated on M9 + separate operator authorization. NOT evidenced. |
| **M11 / M12 panel impls** | CLOSED — gated on M5 + M9 + M10. NOT evidenced. |
| **M14 / M15 REST endpoints** | CLOSED — gated on M11. NOT evidenced. |
| **Real MCF metric contracts** | CLOSED — substrate accepts authoring, but no panel exists. NOT evidenced. |
| **BCF data changes** | CLOSED — untouched throughout this arc. NOT evidenced. |
| **M7/M8 algorithm bump (v2)** | CLOSED — `mcf-hash-v1` is the forever-locked bundle per DBCP §12.4 unless an ADR-governed change requires bump. NOT evidenced. |

## 7. Source-of-truth references

- DBCP: `bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md` (`62ec707`)
- Preflight: `bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-preflight.md` (`454bfeb`)
- ADR: `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422)
- M4 apply closeout: `bc-docs-v3/docs/implementation/mcf-m4-ddl-apply-closeout.md` (`c2bc3fc`)
- M3 cert-amendment closeout: `bc-docs-v3/docs/implementation/mcf-m3-cert-amendment-apply-closeout.md` (`60efd9d`)
- Implementation PR: bc-core #110 (squash `91f83ee`)
- Evidence PR: bc-core #111
- DDL sha256: `c9d4203d9b8f6e2ffeb24adf7b3e139a91ca84dd42b47404443f679bf9e0fa00`
- Rollback sha256: `2122b67efe46d192d0d3d2f0390555f193e354a1e76c7ba9924db22c15e6e412`

## 8. Discipline summary

- ✅ Apply executed under explicit operator pre-authorization in the prompt requesting the apply gate
- ✅ Whole-file `BEGIN/COMMIT` atomicity per §13.2.1 + §17.2 (column add + trigger amendment commit together)
- ✅ Pre-amendment trigger body captured for rollback safety per §13.2.1
- ✅ Post-apply verifier 9/9 PASS independently confirmed via bc-postgres MCP (`allow_write=false`)
- ✅ NO bc-core source changes in evidence PR (audit artifacts only)
- ✅ NO further DDL apply or rollback this session
- ✅ NO real MCF metric contracts created
- ✅ NO BCF touches
- ✅ NO M5/M9/M10 gates opened — those remain closed and not evidenced
- ✅ M7/M8 substrate is now **live** and **dormant**; M5 panel substrate is next blocked gate awaiting separate operator authorization
