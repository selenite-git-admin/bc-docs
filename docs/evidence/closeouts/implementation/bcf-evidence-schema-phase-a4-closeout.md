---
uid: bcf-evidence-schema-phase-a4-closeout
title: BCF Evidence Schema — Phase A4 F4+C2 freeze closeout
description: Closeout record for the completed Phase A4 (F4 HYBRID freeze + C2 REPLACE) ship event at apply-ts `2026-05-29T11-21-03-131Z`. `contract.*` BCF evidence tables (panel_output_record, authoring_panel_rejection_log, calibration_event, certification_record) are FROZEN by 4 deny-write trigger functions + 12 deny-write trigger rows (4 tables × INSERT/UPDATE/DELETE BEFORE FOR EACH STATEMENT); `contract.certification_record` born-null/write-once trigger + function DROPPED per D5 C2; `bcf.certification_record` write-once trigger preserved LIVE; row counts unchanged; 9 inbound FKs to `contract.panel_output_record` preserved; 5 cross-schema mcf→contract FKs preserved (A5 retarget scope). Records the D9 rollback-policy state change: as of A4 apply-ts, the combined Phase A3 + §14 step 20 rollback envelope is NO LONGER VALID. A4 rollback envelope remains available pre-A5. F4 HYBRID post-A5 DROP roadmap deferred to A5/post-A5 governance. M14 stays CLOSED. A5 NOT STARTED. **NOT EXECUTED.** This is a docs-only closeout; the substrate apply already happened at apply-ts `2026-05-29T11-21-03-131Z`. **No DDL applied, no DML applied, no rollback executed, no tenant DB connection, no M-series invocation.** Operator stance ADR DEC-7f9597 / D423 honoured.
status: implemented
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a4-freeze-closeout
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A4 F4+C2 freeze closeout

## 1. Scope

### 1.1 Question this doc answers

> The Phase A4 freeze (F4 HYBRID surface + C2 REPLACE per operator decisions D1 + D5 accepted at PR #19 merge) was executed at apply-ts `2026-05-29T11-21-03-131Z`, anchored in evidence at bc-core main `0f3093b` (PR #149 dry-run + sha256 pin) and `6a8a67a` (PR #150 apply + post-apply evidence). The 4 `contract.*` BCF evidence tables are now structurally frozen by deny-write triggers; the `contract.certification_record` born-null/write-once trigger + function are DROPPED per C2. The combined Phase A3 + §14 step 20 rollback envelope is NO LONGER VALID per D9. What is the final ship record — substrate state, rollback-policy state change, evidence anchor chain, F4 HYBRID post-A5 roadmap status, scope discipline, and next-gate handoff?

### 1.2 In scope

- **Ship record** — what landed at substrate + code + governance + evidence layers under the A4 freeze.
- **Substrate final state** — 4 contract.* deny-write functions LIVE; 12 deny-write trigger rows LIVE (4 tables × INSERT/UPDATE/DELETE); contract.cert born-null/write-once trigger + function DROPPED per C2; bcf.cert write-once trigger preserved LIVE; row counts unchanged; FK topology preserved.
- **Evidence anchor chain** — governance + implementation + dry-run + apply + post-apply, sha256-pinned across the A4 apply gate.
- **D9 rollback-policy state change** — combined Phase A3 + §14 step 20 rollback envelope NO LONGER VALID post-A4; A4 rollback must perform FIRST if combined rollback ever required.
- **A4 rollback envelope status** — available pre-A5 (5 cross-schema mcf→contract FKs preserved → guard #300 `a4_rollback_phase_a5_not_shipped` would PASS).
- **F4 HYBRID post-A5 DROP roadmap** — deferred to A5/post-A5 governance.
- **Scope discipline assertions** — no row mutation; no tenant DB; no M-series invocation; M14 CLOSED; A5 NOT STARTED.
- **Next-gate handoff** — Phase A5 DBCP authoring as separate operator-authorized governance gate.

### 1.3 Explicit non-scope

- ❌ **No DDL applied by this closeout.** The freeze DDL was applied by `scripts/bcf-evidence-schema-phase-a4-apply.mjs` under a separately operator-authorized gate at apply-ts `2026-05-29T11-21-03-131Z`. This closeout doc records that event; it does not re-apply it.
- ❌ **No DML applied.** No row mutation on `bcf.*` / `contract.*` / `mcf.*` / `concept_registry.*` / any tenant DB.
- ❌ **No bc-core code change.** The closeout is bc-docs-v3 docs-only.
- ❌ **No further bc-core PR.** PR #19 / #148 / #149 / #150 are merged; no follow-up bc-core PR is opened by this closeout.
- ❌ **No A4 rollback executed.** Apply succeeded; A4 rollback envelope remains dormant (available pre-A5 if operator authorization arrives).
- ❌ **No combined Phase A3 + §14 step 20 rollback executed.** That envelope is **NO LONGER VALID** per D9 + A4 apply effect.
- ❌ **No `contract.*` row deletion.** The deny-write triggers reject DELETE alongside INSERT and UPDATE; rows are preserved as the read-only historical archive.
- ❌ **No `mcf.*` / `metric.*` / `concept_registry.*` touch.** mcf.* untouched; the 5 cross-schema mcf→contract FKs remain unchanged (A5 retarget scope).
- ❌ **No A5 work.** A5 design is a separate operator-authorized governance gate.
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M14 remains CLOSED.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** HR4 substrate-enforced.
- ❌ **No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 / #148 / #149 / #150 re-touch.**
- ❌ **No PR #15 / #16 / #17 / #18 / #19 re-touch.**
- ❌ **No bc-admin / bc-portal UI changes.**

## 2. Authority anchor chain

| Layer | Artifact | SHA |
|---|---|---|
| Governance — Boundary DBCP (Option A) | PR #11 | bc-docs-v3 main `6f8cc15` |
| Governance — Phase A3 original DBCP | PR #15 | bc-docs-v3 main `d06eeba` |
| Governance — Phase A3 correction (D11(δ)) | PR #16 | bc-docs-v3 main `21aa442` |
| Governance — Step 20 DBCP | PR #17 | bc-docs-v3 main `b0bd475` |
| Governance — Phase A3 + step 20 closeout | PR #18 | bc-docs-v3 main `5757936` |
| **Governance — Phase A4 DBCP (D1..D10)** | **PR #19** | **bc-docs-v3 main `dbc0378`** |
| Code — Phase A3 cutover | PR #141 | bc-core main `5f7f8fe` |
| Code — Phase A3 spec hygiene | PR #142 | bc-core main `e0bdbc6` |
| Code — Phase A3 apply/rollback scripts | PR #143 | bc-core main `0a34817` |
| Code — Phase A3 harness repair + FK finding | PR #144 | bc-core main `68cee3f` |
| Code — Step 20 implementation | PR #145 | bc-core main `9cb3ce0` |
| Evidence — Step 20 dry-run | PR #146 | bc-core main `45da6e1` |
| Evidence — Step 20 combined apply + post-apply | PR #147 | bc-core main `781660b` |
| **Code — Phase A4 implementation (F4+C2)** | **PR #148** | **bc-core main `ebfb61a`** |
| **Evidence — Phase A4 dry-run + sha256 pin** | **PR #149** | **bc-core main `0f3093b`** |
| **Evidence — Phase A4 apply + post-apply** | **PR #150** | **bc-core main `6a8a67a`** |
| Apply event | combined-A3+step20 apply | apply-ts `2026-05-29T09-24-54-689Z` |
| Apply event | A4 dry-run | dry-run-ts `2026-05-29T11-09-43-405Z` |
| **Apply event** | **A4 apply (this closeout's anchor)** | **apply-ts `2026-05-29T11-21-03-131Z`** |
| Apply event | A4 post-apply | post-apply-ts `2026-05-29T11-21-13-074Z` |
| sha256 pin | A4 freeze DDL byte-equivalence | `6905973983bbf2836ff4ca8972136fb46c29079b329d37bb15f06a4ff60f885a` |
| Stance ADR | DEC-7f9597 / D423 | bc-docs-v3 `docs/adrs/ADR-7f9597.md` |
| Operator decisions D1..D10 | accepted at PR #19 merge | F4 HYBRID / YES / YES / YES / C2 REPLACE / RETIRE / FLIP / YES / YES / 14 statements |

## 3. Phase A4 F4+C2 freeze shipped

The Phase A4 freeze ship event landed at `bc_platform_dev` apply-ts `2026-05-29T11-21-03-131Z` as a single operator-authorized DDL gate.

### 3.1 What shipped

| Slice | Deliverable | Landing |
|---|---|---|
| **Phase A4 DDL — F4 surface** | 4 × `contract.tg_<table>_deny_write()` functions + 4 × `DROP TRIGGER IF EXISTS` + 4 × `CREATE TRIGGER` (BEFORE INSERT OR UPDATE OR DELETE FOR EACH STATEMENT) | applied by `scripts/bcf-evidence-schema-phase-a4-apply.mjs` in single transaction; sha256-pinned `6905973983bbf2836ff4ca8972136fb46c29079b329d37bb15f06a4ff60f885a` |
| **Phase A4 DDL — C2 REPLACE** | 1 × `DROP TRIGGER IF EXISTS trg_certification_record_target_registry_id_guard ON contract.certification_record` + 1 × `DROP FUNCTION IF EXISTS contract.tg_certification_record_target_registry_id_guard()` | applied in same single transaction as the F4 surface (atomicity preserved) |
| Total statements | **14** (matches D10) | single transaction; exit code 0 |
| Apply assertions | 10/10 PASS (#200-#209) | recorded in PR #150 |
| Post-apply assertions | 10/10 PASS (#220-#229) | recorded in PR #150 |

### 3.2 Operator decisions D1..D10 final implementation

| # | Decision | Selection | Implementation evidence |
|---|---|---|---|
| D1 | Disposition strategy | **F4 HYBRID** | DDL emits F4 freeze surface (deny-write triggers); post-A5 DROP roadmap deferred (§6) |
| D2 | Authorize bc-core implementation PR authoring | YES | PR #148 (merged at `ebfb61a`) |
| D3 | No A5 work | YES | 5 cross-schema mcf→contract FKs unchanged (verified live); rollback verifier guard #300 `a5_not_shipped` is the gate boundary |
| D4 | No tenant DB | YES | TENANT_DATABASE_URL guard in all A4 scripts; tenant DB connection count = 0 |
| D5 | contract.cert trigger disposition | **C2 REPLACE** | Statements 13 + 14 DROPPED the existing born-null/write-once trigger + function (verified live: 0/0) |
| D6 | PR #133 restore script retirement | RETIRE | `scripts/bcf-authoring-test-row-cleanup-restore.mjs` deleted at PR #148 merge |
| D7 | `bcf-b8-calibration-event-ingest.spec.ts` test-fixture flip | FLIP | calibrationEvent import flipped to bcf at PR #148 merge |
| D8 | M14 CLOSED | YES | preserved throughout |
| D9 | Combined Phase A3 + step 20 rollback envelope invalid post-A4-apply | YES (operator-accepted) | recorded in apply summary; recorded in this closeout §5 |
| D10 | Statement count F4+C2 | **14** | verified by live introspection at apply gate |

## 4. Substrate final state

Verified live via `bc-postgres` MCP read-only queries at closeout-authoring time:

### 4.1 contract.* BCF evidence FROZEN

| Substrate | Status |
|---|---|
| `contract.tg_panel_output_record_deny_write()` function | **PRESENT (LIVE)** |
| `contract.tg_authoring_panel_rejection_log_deny_write()` function | **PRESENT (LIVE)** |
| `contract.tg_calibration_event_deny_write()` function | **PRESENT (LIVE)** |
| `contract.tg_certification_record_deny_write()` function | **PRESENT (LIVE)** |
| `contract.*` deny-write functions (any) | **4** (per BCF evidence table) |
| `contract.*` deny-write triggers (`information_schema.triggers` rows) | **12** (4 tables × 3 events: INSERT/UPDATE/DELETE) |
| Trigger timing | BEFORE FOR EACH STATEMENT |
| Trigger action | RAISE EXCEPTION (rejects all DML) |

The 12 deny-write trigger rows enumerate as:

| Schema | Table | Trigger | Event | Timing |
|---|---|---|---|---|
| contract | panel_output_record | trg_contract_panel_output_record_deny_write | INSERT | BEFORE |
| contract | panel_output_record | trg_contract_panel_output_record_deny_write | UPDATE | BEFORE |
| contract | panel_output_record | trg_contract_panel_output_record_deny_write | DELETE | BEFORE |
| contract | authoring_panel_rejection_log | trg_contract_authoring_panel_rejection_log_deny_write | INSERT | BEFORE |
| contract | authoring_panel_rejection_log | trg_contract_authoring_panel_rejection_log_deny_write | UPDATE | BEFORE |
| contract | authoring_panel_rejection_log | trg_contract_authoring_panel_rejection_log_deny_write | DELETE | BEFORE |
| contract | calibration_event | trg_contract_calibration_event_deny_write | INSERT | BEFORE |
| contract | calibration_event | trg_contract_calibration_event_deny_write | UPDATE | BEFORE |
| contract | calibration_event | trg_contract_calibration_event_deny_write | DELETE | BEFORE |
| contract | certification_record | trg_contract_certification_record_deny_write | INSERT | BEFORE |
| contract | certification_record | trg_contract_certification_record_deny_write | UPDATE | BEFORE |
| contract | certification_record | trg_contract_certification_record_deny_write | DELETE | BEFORE |

### 4.2 contract.cert born-null/write-once trigger + function DROPPED (D5 C2)

| Substrate | Pre-A4 | Post-A4 | Δ |
|---|---|---|---|
| `contract.tg_certification_record_target_registry_id_guard()` function | present (1) | **0 (DROPPED)** | C2 |
| `contract.trg_certification_record_target_registry_id_guard` trigger | 2 rows (INSERT + UPDATE) | **0 (DROPPED)** | C2 |

The deny-write trigger (`trg_contract_certification_record_deny_write`) semantically supersedes the dropped born-null/write-once trigger: no writes are permitted at all, so the more restrictive sub-invariants (born-null on Registry-shape INSERT; write-once on target_registry_id UPDATE; append-only on non-target column UPDATE) are moot.

### 4.3 bcf.cert write-once trigger still LIVE (untouched)

| Substrate | Status | Notes |
|---|---|---|
| `bcf.tg_certification_record_target_registry_id_guard()` function | **PRESENT (1; LIVE)** | unchanged by A4 |
| `bcf.trg_certification_record_target_registry_id_guard` trigger | **2 rows (INSERT + UPDATE; BEFORE FOR EACH ROW)** | unchanged by A4 |

The bcf.cert write-once trigger remains operational and continues to enforce born-null + write-once + append-only invariants on the live writer path (W4b INSERT and W5 stampTargetRegistryId UPDATE).

### 4.4 Row counts unchanged

| Table | Rows | Δ vs pre-A4 baseline | Notes |
|---|---|---|---|
| `bcf.panel_output_record` | **19** | 0 | unchanged |
| `bcf.authoring_panel_rejection_log` | **0** | 0 | unchanged |
| `bcf.calibration_event` | **19** | 0 | unchanged |
| `bcf.certification_record` | **3530** | 0 | unchanged |
| `contract.panel_output_record` | **19** | 0 | preserved (frozen archive) |
| `contract.authoring_panel_rejection_log` | **0** | 0 | preserved (frozen archive) |
| `contract.calibration_event` | **19** | 0 | preserved (frozen archive) |
| `contract.certification_record` | **3530** | 0 | preserved (frozen archive) |
| `mcf.certification_record` | **0** | 0 | unchanged (M-series CLOSED) |

The A4 apply introduced only DDL (trigger functions + trigger declarations + 1 DROP TRIGGER + 1 DROP FUNCTION). Zero row mutations across all 9 monitored tables.

### 4.5 FK topology preserved

| Check | Value | Notes |
|---|---|---|
| Inbound FKs to `contract.panel_output_record` | **9** | preserved (3 intra-contract + 1 contract.intake_queue + 5 cross-schema mcf→contract) |
| Cross-schema mcf→contract FKs | **5** | preserved unchanged — **A5 retarget scope** |
| Cross-schema FKs from `bcf.*` → non-`bcf.*` | **0** | R10 cluster separation invariant intact |

A4 added no FKs. A4 dropped no FKs. The 5 cross-schema `mcf.*` → `contract.panel_output_record` FKs (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`) remain intact pre-A5 retarget.

## 5. D9 rollback-policy state change

### 5.1 Combined Phase A3 + §14 step 20 rollback envelope: NOW INVALID

**As of apply-ts `2026-05-29T11-21-03-131Z`, the combined Phase A3 + §14 step 20 rollback envelope is NO LONGER VALID.** This is the central rollback-policy state change recorded by D9 operator acceptance + materialized by the A4 apply event.

Mechanically:
- Pre-A4, writes could route back to `contract.*` BCF evidence tables via `git revert` of PR #141 + DROP of bcf trigger.
- Post-A4, writes **cannot** route back to `contract.*` — the 12 deny-write trigger rows reject any INSERT/UPDATE/DELETE with `RAISE EXCEPTION`.
- The combined Phase A3 + §14 step 20 rollback verifier (`bcf-evidence-schema-phase-a3-rollback.mjs --mode=*-combined`) refuses under guard #1 `a3_step_20_rollback_phase_a4_not_shipped` (post-A4, A4 has shipped, so the inverted guard predicate fails).

### 5.2 Operator must perform A4 rollback FIRST if combined rollback ever required post-A4

If a combined Phase A3 + §14 step 20 rollback later becomes necessary, the required sequence is:

1. **Operator-authorized A4 rollback**:
   ```
   BCCORE_BCF_PHASE_A4_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_2026-05-29T11-21-03-131Z \
     TENANT_DATABASE_URL= node scripts/bcf-evidence-schema-phase-a4-rollback.mjs --mode=pre-rollback
   ```
   5 pre-rollback guards verify safety (#300 `a5_not_shipped` + #301 `contract_rows_intact` + #302 `bcf_rows_present` + #303 `env_gate_present` + #304 `bcf_cert_trigger_unchanged`).
2. **Operator-driven DDL rollback action**:
   - DROP 4 contract deny-write triggers
   - DROP 4 contract deny-write functions
   - Re-create contract.cert born-null/write-once trigger + function from source DDL line 188-226 of `docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql`
3. **Operator-authorized A4 post-rollback verification**:
   ```
   BCCORE_BCF_PHASE_A4_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_2026-05-29T11-21-03-131Z \
     TENANT_DATABASE_URL= node scripts/bcf-evidence-schema-phase-a4-rollback.mjs --mode=post-rollback
   ```
   8 post-rollback assertions (deny-write triggers + functions DROPPED; contract.cert born-null trigger + function RESTORED; rows preserved; bcf.cert trigger preserved; mcf FKs unchanged).
4. **Only after A4 rollback completes**, the combined Phase A3 + step 20 rollback envelope becomes valid again (guard #1 `a3_step_20_rollback_phase_a4_not_shipped` now PASSes).
5. **Then** the operator may invoke the combined Phase A3 + step 20 rollback per the merged Phase A3 + step 20 closeout (bc-docs-v3 main `5757936` / PR #18) §9.4.

### 5.3 A4 rollback envelope: AVAILABLE pre-A5

The A4 rollback envelope itself remains available pre-A5 because:
- The 5 cross-schema mcf→contract FKs are preserved (verified live: 5; guard #300 `a4_rollback_phase_a5_not_shipped` would PASS).
- bcf.* rows preserved across A4 rollback (rows are not row-destructive on rollback).
- contract.* rows preserved (deny-write triggers are dropped; the underlying frozen rows remain).

Once Phase A5 retargets the 5 mcf→contract FKs to `bcf.panel_output_record`, guard #300 will FAIL because the FKs no longer point at contract — an A4 rollback that restores contract.* writability cannot un-retarget them. **A5 ship time is the cliff for A4 rollback validity.**

## 6. F4 HYBRID post-A5 DROP roadmap

Per operator decision D1 = F4 HYBRID (recorded in PR #19 merge), the A4 surface is identical to F1 freeze but commits to a documented post-A5 DROP roadmap. The post-A5 DROP slice is **explicitly deferred to A5/post-A5 governance** and is **NOT executed by this closeout** or by any prior gate.

### 6.1 Why post-A5 DROP is blocked pre-A5

`DROP TABLE contract.panel_output_record` is structurally blocked pre-A5 because the 5 cross-schema mcf→contract FKs reference it. PostgreSQL would refuse the DROP with foreign-key-constraint error unless `CASCADE` is used — but `CASCADE` would silently delete cross-schema FKs without A5 governance, which is forbidden by the boundary DBCP + A5 ownership.

### 6.2 Future post-A5 DROP slice (out of A4 scope)

When A5 retargets the 5 cross-schema mcf→contract FKs to `bcf.panel_output_record`, the post-A5 DROP slice becomes structurally possible. The proposed table disposition (deferred to A5/post-A5 governance — operator decisions still required):

| Table | A4 disposition (current) | Post-A5 disposition (deferred) |
|---|---|---|
| `contract.authoring_panel_rejection_log` | FROZEN (deny-write trigger) | DROP candidate (0 inbound FKs; safe to drop after A5) |
| `contract.calibration_event` | FROZEN (deny-write trigger) | DROP candidate (0 inbound FKs; safe to drop after A5) |
| `contract.certification_record` | FROZEN (deny-write trigger; C2 born-null DROPPED) | DROP candidate (0 inbound FKs; safe to drop after A5) |
| `contract.panel_output_record` | FROZEN (deny-write trigger) | **DROP gated on A5 + intake_queue FK disposition** (5 mcf FKs retargeted by A5; 1 intake_queue FK still references it — must be addressed by A5 or follow-on phase) |

A5 (or a follow-on phase the boundary DBCP assigns) will own the post-A5 DROP slice authoring + apply + closeout.

### 6.3 Current A4 surface remains valid indefinitely pre-DROP

The deny-write trigger surface (F4) is operationally stable. There is no time pressure to DROP — the freeze + preserved rows constitute a working historical archive indefinitely. Post-A5 DROP is a future cleanup, not a correctness requirement.

## 7. Evidence anchors

| Anchor | SHA / timestamp | Scope |
|---|---|---|
| **PR #19** — Phase A4 DBCP | bc-docs-v3 main `dbc0378` | Governance authority for the A4 design (4 disposition options F1/F2/F3/F4; D1..D10 operator decisions) |
| **PR #148** — Phase A4 implementation | bc-core main `ebfb61a` | 5 new scripts (DDL synthesis + dry-run + apply + post-apply + rollback verifier); lockfile extension 25/25 PASS; D6 PR #133 restore retirement; D7 bcf-b8 fixture flip |
| **PR #149** — Phase A4 dry-run + sha256 pin | bc-core main `0f3093b` | Dry-run timestamp `2026-05-29T11-09-43-405Z`; 4 artifacts (planned-ddl.sql + sha256.txt + evidence.jsonl + summary.md); 7/7 pre-apply probes PASS |
| **PR #150** — Phase A4 apply + post-apply | bc-core main `6a8a67a` | Apply timestamp `2026-05-29T11-21-03-131Z`; post-apply timestamp `2026-05-29T11-21-13-074Z`; 5 artifacts (precondition + apply evidence + apply summary + post-apply evidence + post-apply summary); 10/10 apply assertions PASS; 10/10 post-apply assertions PASS |
| **Apply sha256 pin** | `6905973983bbf2836ff4ca8972136fb46c29079b329d37bb15f06a4ff60f885a` | Byte-equivalence binding between dry-run and apply gates; verified before DDL execution at apply-ts |
| **Substrate apply** | `bc_platform_dev` apply-ts `2026-05-29T11-21-03-131Z` | 14-statement F4+C2 freeze DDL in single transaction |

## 8. Scope discipline

| Discipline rule | Status |
|---|---|
| No row mutation introduced by A4 apply | ✓ all 9 row counts Δ=0 vs pre-A4 baseline |
| No `contract.*` row deletion | ✓ deny-write triggers reject DELETE; preserved rows remain |
| No `bcf.*` row mutation | ✓ A4 DDL targets only contract.* objects |
| No FK changes | ✓ A4 DDL adds no FKs; drops no FKs; 9 inbound FKs on contract.panel + 5 cross-schema mcf→contract preserved |
| No tenant DB connection | ✓ TENANT_DATABASE_URL guard enforced across all A4 scripts |
| No M-series invocation | ✓ M11 / M12 / M12.5 / M13 not invoked |
| **M14 stays CLOSED** | ✓ (per D8) |
| No A5 work | ✓ 5 cross-schema mcf→contract FKs unchanged (verified live) |
| A4 rollback NOT executed | ✓ apply succeeded; rollback envelope dormant |
| HR1 — no synthetic / mock / replay / canned data | ✓ A4 deny-write triggers now structurally reject any future synthetic DML on contract.* |
| HR2 — MCF evidence belongs in `mcf.*` | ✓ mcf.* untouched; mcf.certification_record = 0 |
| HR3 — MCF metric authority events do not write to generic `contract.*` | ✓ deny-write triggers structurally enforce HR3 at substrate level for all 3 DML verbs |
| HR4 — tenant result DBs separate | ✓ no tenant DB connection opened |
| HR5 — production paths; no mocks | ✓ A4 deny-write triggers apply to live contract.* substrate |
| DEC-7f9597 / D423 stance ADR | ✓ honoured — operator authorization on mutating gate; rollback discipline preserved (A4 rollback envelope available pre-A5) |

## 9. A5 relationship

### 9.1 A5 owns the next mutating gate

Phase A5 owns:
- Retarget the 5 cross-schema mcf→contract FKs (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`) from `contract.panel_output_record` to `bcf.panel_output_record`.
- M12 writer flip (the first real MCF authority writer).
- M14 unblock decision (if A5 design clears the path).
- Optional: post-A5 DROP slice for the 4 contract.* BCF evidence tables (per F4 HYBRID roadmap, §6).

### 9.2 A4 NOT STARTED → A5 boundary preserved

A4 must not touch A5 scope. Verified by:
- 5 cross-schema mcf→contract FKs unchanged (count = 5; verified live).
- No `mcf.*` modifications (lockfile assertion in PR #148 `bcf-phase-a3-import-lockfile.mjs`).
- M-series gates not invoked.

### 9.3 Post-A4 → A5 handoff state

After A4 ships:
- contract.* BCF evidence tables are FROZEN (deny-write triggers reject all DML).
- contract.* rows preserved (read-only historical archive).
- contract.cert born-null/write-once trigger + function DROPPED (D5 C2).
- bcf.cert write-once trigger LIVE.
- bcf.* writers/readers fully operational.
- 5 cross-schema mcf→contract FKs preserved (A5 retarget scope).
- A4 rollback envelope available pre-A5.
- Combined Phase A3 + step 20 rollback envelope INVALID (per D9).
- **Phase A5 DBCP authoring is the next operator-authorized governance gate.**

### 9.4 First real M12 panel run remains gated

The first real M12 panel run (M-series gate) remains blocked until A5 (or whichever phase the boundary DBCP assigns) ships. A4 does not unblock M12.

## 10. Hard rule mapping (HR1..HR5)

| Rule | Closeout-time status |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | bcf substrate CHECKs + bcf.cert write-once trigger + **new A4 deny-write triggers on contract.*** all enforce HR1 (synthetic-provider writes structurally rejected on bcf.*; ALL writes structurally rejected on contract.*) |
| **HR2** — MCF evidence belongs in `mcf.*` | mcf.certification_record = 0; mcf.* untouched; no MCF authority leakage |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.*` | A4 deny-write triggers structurally enforce HR3 at substrate level for ALL 3 DML verbs (INSERT/UPDATE/DELETE) on ALL 4 contract.* BCF evidence tables. Post-A4, `contract.*` BCF evidence tables receive ZERO new DML of any kind |
| **HR4** — tenant result DBs separate | TENANT_DATABASE_URL guard enforced in all A4 scripts; tenant DB connection count = 0 throughout A4 |
| **HR5** — production path; no mocks | A4 deny-write triggers apply to live `bc_platform_dev` substrate. Mocks confined to unit + SAVEPOINT-rolled-back integration tests |
| **Stance ADR DEC-7f9597 / D423** | Schema-boundary clarity reinforced via freeze (contract.* permanently non-writable post-A4). Rollback discipline preserved via A4 rollback envelope (available pre-A5). Operator authorization for mutating gates: A4 apply was operator-authorized at apply-ts `2026-05-29T11-21-03-131Z` |

## 11. Sequencing record

The complete A1 → A2 → A3 → step 20 → A4 chain under the merged Option A boundary DBCP:

1. ✓ Boundary DBCP merged — bc-docs-v3 main `6f8cc15` (PR #11)
2. ✓ Phase A1 substrate-design + apply DBCPs merged
3. ✓ Phase A1 substrate applied — `bc_platform_dev` (2026-05-29T02-11-41-745Z)
4. ✓ Phase A2 migration DBCP + apply — 3,568 authority rows migrated
5. ✓ Phase A3 cutover DBCP (PR #15) merged
6. ✓ Phase A3 implementation chain (PR #141 + #142 + #143 + #144) merged
7. ✓ Phase A3 DBCP correction (PR #16; D11(δ) lock) merged
8. ✓ §14 step 20 DBCP (PR #17) merged
9. ✓ Step 20 implementation (PR #145) merged
10. ✓ Step 20 dry-run + sha256 pin (PR #146) merged
11. ✓ Combined Phase A3 + §14 step 20 apply executed — apply-ts `2026-05-29T09-24-54-689Z`
12. ✓ Combined apply + post-apply evidence (PR #147) merged
13. ✓ Phase A3 + §14 step 20 closeout (PR #18) merged
14. ✓ **Phase A4 DBCP (PR #19; D1..D10) merged** — bc-docs-v3 main `dbc0378`
15. ✓ **Phase A4 implementation (PR #148) merged** — bc-core main `ebfb61a`
16. ✓ **Phase A4 dry-run + sha256 pin (PR #149) merged** — bc-core main `0f3093b`
17. ✓ **Phase A4 apply executed** — apply-ts `2026-05-29T11-21-03-131Z`
18. ✓ **Phase A4 post-apply evidence captured** — post-apply-ts `2026-05-29T11-21-13-074Z`
19. ✓ **Phase A4 apply + post-apply evidence (PR #150) merged** — bc-core main `6a8a67a`
20. ✓ **This Phase A4 closeout doc** — bc-docs-v3
21. ⏸ Phase A5 DBCP authoring — SEPARATE operator-authorized governance gate (next)
22. ⏸ Phase A5 implementation + dry-run + apply + closeout — gated on A5 DBCP
23. ⏸ Post-A5 DROP slice (F4 HYBRID roadmap) — gated on A5 ship
24. ⏸ M-series gates (M14 in particular) — remain CLOSED until A5 design unblocks

## 12. Discipline assertions (this closeout-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — closeout file lands only in bc-docs-v3 |
| No DDL applied | ✓ — closeout is docs-only; DDL was applied in the separately operator-authorized A4 apply gate at apply-ts `2026-05-29T11-21-03-131Z` |
| No DML applied | ✓ |
| No A4 rollback executed | ✓ |
| No combined Phase A3 + step 20 rollback executed | ✓ (envelope is INVALID per D9; could not execute even if attempted) |
| No bc-core PR opened by this closeout | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ (deny-write triggers would have rejected any attempt) |
| No `bcf.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No tenant `tbc_{slug}_dev` DB connection | ✓ |
| No PR #15 / #16 / #17 / #18 / #19 re-touch | ✓ |
| No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 / #148 / #149 / #150 re-touch | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured | ✓ |
| `bc-postgres` MCP `allow_write` used read-only only for substrate verification at closeout-authoring time | ✓ |

## 13. Out-of-scope re-statement

This closeout doc is **NOT** Phase A5 / M-series.

This closeout doc does **NOT** authorize bc-core code execution.

This closeout doc does **NOT** authorize merging any bc-core PR; PR #148 / #149 / #150 are already merged.

This closeout doc does **NOT** authorize any `contract.*` row deletion. The deny-write triggers reject DELETE; future cleanup would require A4 rollback (to drop the triggers) + a separate row-mutation gate.

This closeout doc does **NOT** authorize any further `bcf.*` row mutation. The A4 freeze is COMPLETE; further substrate change requires a separately operator-authorized governance + apply gate.

This closeout doc does **NOT** authorize MCF FK changes. A5 owns retarget.

This closeout doc does **NOT** authorize the post-A5 DROP slice. A5 / post-A5 governance owns.

This closeout doc does **NOT** touch tenant DBs.

This closeout doc does **NOT** alter `mcf.*`, `metric.*`, `concept_registry.*`, or any further `contract.*` substrate beyond what was applied at apply-ts `2026-05-29T11-21-03-131Z`.

This closeout doc does **NOT** open M14.

This closeout doc does **NOT** initiate the first real M12 panel run.

This closeout doc does **NOT** execute A4 rollback.

This closeout doc does **NOT** validate the combined Phase A3 + step 20 rollback envelope. That envelope is **INVALID** per D9.

---

**End of closeout. Phase A4 F4+C2 freeze ship event RECORDED. Next operator-authorized gate: Phase A5 DBCP authoring.**
