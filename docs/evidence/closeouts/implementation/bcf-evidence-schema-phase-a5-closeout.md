---
uid: bcf-evidence-schema-phase-a5-closeout
title: BCF Evidence Schema — Phase A5 mcf→bcf FK retarget closeout
description: Closeout record for the completed Phase A5 ship event at apply-ts `2026-05-29T13-07-48-822Z`. The 5 cross-schema mcf→contract FKs (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`) have been retargeted to `bcf.panel_output_record(panel_run_uid)` (F1 single-tx atomic per D1; 10 statements per D10); ON DELETE RESTRICT / ON UPDATE NO ACTION preserved; inbound FKs to `contract.panel_output_record` reduced from 9 to 4 (3 intra-contract sibling + 1 `contract.intake_queue` retained per D8); inbound cross-schema on `bcf.panel_output_record` grew from 0 to 5; R10 cluster separation invariant intact; A4 freeze invariants preserved (12 contract.* deny-write triggers + 4 functions LIVE; contract.cert born-null DROPPED; bcf.cert write-once LIVE); all row counts unchanged (bcf/contract 19/0/19/3530 each; mcf.cert 0; mcf.* panel_run_uid rows 0 across all 5 tables). Records the D5 rollback-policy state change: **Phase A4 rollback envelope is NOW INVALID post-A5**; A5 rollback must perform FIRST if combined A4+A5 rollback is ever required. A5 rollback envelope remains available pre-first-M12-run only (cliff predicate guard #700; current state is outcome A — M12 never ran). M12 writer remains skeleton-only and throws `M12NotImplementedError`. M14 remains CLOSED. **First real M12 panel run NOT AUTHORIZED.** **NOT EXECUTED.** This is a docs-only closeout; the substrate apply already happened at apply-ts `2026-05-29T13-07-48-822Z`. **No DDL applied, no DML applied, no rollback executed, no tenant DB connection, no M-series invocation.** Operator stance ADR DEC-7f9597 / D423 honoured.
status: implemented
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a5-mcf-fk-retarget-closeout
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A5 mcf→bcf FK retarget closeout

## 1. Scope

### 1.1 Question this doc answers

> The Phase A5 ship event (F1 single-tx mcf→bcf FK retarget per operator decision D1 accepted at PR #21 merge) was executed at apply-ts `2026-05-29T13-07-48-822Z`, anchored in evidence at bc-core main `153c46d` (PR #152 dry-run + sha256 pin) and `99edc1b` (PR #153 apply + post-apply evidence). The 5 cross-schema `mcf.* → contract.panel_output_record` FKs are now retargeted to `bcf.panel_output_record(panel_run_uid)`. The Phase A4 rollback envelope is NO LONGER VALID per D5. What is the final ship record — substrate state, rollback-policy state change, evidence anchor chain, M12 writer status, scope discipline, and next-gate handoff?

### 1.2 In scope

- **Ship record** — what landed at substrate + governance + evidence layers under the A5 retarget.
- **Substrate final state** — 5 mcf→bcf FKs LIVE; 5 mcf→contract FKs DROPPED; inbound FKs on contract.panel reduced 9→4 with `contract.intake_queue` retained (D8); inbound cross-schema on bcf.panel grew 0→5; R10 cluster separation intact; A4 freeze invariants preserved; bcf/contract/mcf row counts unchanged.
- **Evidence anchor chain** — governance + implementation + dry-run + apply + post-apply, sha256-pinned across the A5 apply gate.
- **D5 rollback-policy state change** — Phase A4 rollback envelope NO LONGER VALID post-A5; A5 rollback must perform FIRST if combined rollback ever required.
- **A5 rollback envelope status** — available pre-first-M12-run only (cliff predicate guard #700); current state is outcome (A).
- **M12 writer status** — skeleton-only; throws `M12NotImplementedError`; no runtime invocation path.
- **M14 status** — CLOSED per D9.
- **Scope discipline assertions** — no row mutation; no tenant DB; no M-series invocation; no first real M12 run.
- **Next-gate handoff** — M14/M12 governance decision is a SEPARATE operator-authorized governance gate; required evidence before first real M12 run.

### 1.3 Explicit non-scope

- ❌ **No DDL applied by this closeout.** The FK retarget DDL was applied by `scripts/bcf-evidence-schema-phase-a5-apply.mjs` under a separately operator-authorized gate at apply-ts `2026-05-29T13-07-48-822Z`. This closeout records that event; it does not re-apply it.
- ❌ **No DML applied.** No row mutation on `bcf.*` / `contract.*` / `mcf.*` / `concept_registry.*` / any tenant DB.
- ❌ **No bc-core code change.** The closeout is bc-docs-v3 docs-only.
- ❌ **No further bc-core PR.** PR #21 / #151 / #152 / #153 are merged; no follow-up bc-core PR is opened by this closeout.
- ❌ **No A5 rollback executed.** Apply succeeded; A5 rollback envelope remains dormant (available pre-first-M12-run if operator authorization arrives).
- ❌ **No Phase A4 rollback executed or attempted.** Phase A4 rollback envelope is INVALID post-A5 per D5.
- ❌ **No M12 invocation.** M12 writer skeleton remains untouched; throws on any invocation.
- ❌ **No M14 unblock.** M14 remains CLOSED per D9.
- ❌ **No first real M12 panel run.** That is a SEPARATE post-M14-unblock operator-authorized gate per D6.
- ❌ **No post-A5 DROP slice (F4 HYBRID roadmap).** Per A4 closeout §6.3 + locked D11: deferred to separate post-A5 governance gate.
- ❌ **No `contract.intake_queue` FK modification.** Retained per D8.
- ❌ **No `mcf.*` / `metric.*` / `concept_registry.*` row touch.**
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** HR4 substrate-enforced.
- ❌ **No PR #151 / #152 / #153 re-touch.**
- ❌ **No PR #15 / #16 / #17 / #18 / #19 / #20 / #21 re-touch.**
- ❌ **No bc-admin / bc-portal UI changes.**

## 2. Authority anchor chain

| Layer | Artifact | SHA |
|---|---|---|
| Governance — Boundary DBCP (Option A) | PR #11 | bc-docs-v3 main `6f8cc15` |
| Governance — Phase A3 original DBCP | PR #15 | bc-docs-v3 main `d06eeba` |
| Governance — Phase A3 correction (D11(δ)) | PR #16 | bc-docs-v3 main `21aa442` |
| Governance — Step 20 DBCP | PR #17 | bc-docs-v3 main `b0bd475` |
| Governance — Phase A3 + step 20 closeout | PR #18 | bc-docs-v3 main `5757936` |
| Governance — Phase A4 DBCP (D1..D10) | PR #19 | bc-docs-v3 main `dbc0378` |
| Governance — Phase A4 closeout | PR #20 | bc-docs-v3 main `757071a` |
| **Governance — Phase A5 DBCP (D1..D12)** | **PR #21** | **bc-docs-v3 main `1d631d7`** |
| Code — Phase A3 cutover | PR #141 | bc-core main `5f7f8fe` |
| Code — Phase A3 spec hygiene | PR #142 | bc-core main `e0bdbc6` |
| Code — Phase A3 apply/rollback scripts | PR #143 | bc-core main `0a34817` |
| Code — Phase A3 harness repair + FK finding | PR #144 | bc-core main `68cee3f` |
| Code — Step 20 implementation | PR #145 | bc-core main `9cb3ce0` |
| Evidence — Step 20 dry-run | PR #146 | bc-core main `45da6e1` |
| Evidence — Step 20 combined apply + post-apply | PR #147 | bc-core main `781660b` |
| Code — Phase A4 implementation (F4+C2) | PR #148 | bc-core main `ebfb61a` |
| Evidence — Phase A4 dry-run + sha256 pin | PR #149 | bc-core main `0f3093b` |
| Evidence — Phase A4 apply + post-apply | PR #150 | bc-core main `6a8a67a` |
| **Code — Phase A5 implementation** | **PR #151** | **bc-core main `0d382f3`** |
| **Evidence — Phase A5 dry-run + sha256 pin** | **PR #152** | **bc-core main `153c46d`** |
| **Evidence — Phase A5 apply + post-apply** | **PR #153** | **bc-core main `99edc1b`** |
| Apply event | combined-A3+step20 apply | apply-ts `2026-05-29T09-24-54-689Z` |
| Apply event | Phase A4 apply | apply-ts `2026-05-29T11-21-03-131Z` |
| Apply event | Phase A4 post-apply | post-apply-ts `2026-05-29T11-21-13-074Z` |
| Apply event | A5 dry-run | dry-run-ts `2026-05-29T12-51-13-686Z` |
| **Apply event** | **A5 apply (this closeout's anchor)** | **apply-ts `2026-05-29T13-07-48-822Z`** |
| Apply event | A5 post-apply | post-apply-ts `2026-05-29T13-07-57-405Z` |
| sha256 pin | A5 retarget DDL byte-equivalence | `9113b098d8428aef4b7eb1d075d7572c66902709ecc28b34644e27442e8be634` |
| Stance ADR | DEC-7f9597 / D423 | bc-docs-v3 `docs/adrs/ADR-7f9597.md` |
| Operator decisions D1..D12 | accepted at PR #21 merge | F1 / YES / W1 / α / INVALIDATE / separate-gate / FK+M12-assertions / retain / YES / 10 / defer / separate |

## 3. Phase A5 ship event

The Phase A5 ship event landed at `bc_platform_dev` apply-ts `2026-05-29T13-07-48-822Z` as a single operator-authorized DDL gate.

### 3.1 What shipped

| Slice | Deliverable | Landing |
|---|---|---|
| **Phase A5 DDL — F1 single-tx atomic** | 5 × `ALTER TABLE mcf.<child> DROP CONSTRAINT <old_fk>` + 5 × `ALTER TABLE mcf.<child> ADD CONSTRAINT <same_fk> FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT ON UPDATE NO ACTION` | applied by `scripts/bcf-evidence-schema-phase-a5-apply.mjs` in single transaction; sha256-pinned `9113b098d8428aef4b7eb1d075d7572c66902709ecc28b34644e27442e8be634` |
| Total statements | **10** (matches D10) | single transaction; exit code 0 |
| Pre-apply guards | 3/3 PASS (#510-512) | recorded in PR #153 precondition |
| Apply assertions | 10/10 PASS (#600-609) | recorded in PR #153 evidence |
| Post-apply assertions | 10/10 PASS (#620-629) | recorded in PR #153 |

### 3.2 Operator decisions D1..D12 final implementation

| # | Decision | Selection | Implementation evidence |
|---|---|---|---|
| D1 | FK retarget mechanics | **F1 single-tx atomic** | DDL emits 10 statements wrapped in single `sql.begin()` block in apply script |
| D2 | Authorize bc-core implementation PR authoring | YES | PR #151 (merged at `0d382f3`) |
| D3 | M12 writer flip approach | **W1 greenfield M12 writer service** | `src/registry/metric-authoring/m12-panel-run-writer.service.ts` skeleton at PR #151 |
| D4 | M14 unblock policy | **α prepare-only** | M14 stays CLOSED; M12 writer not wired to controller/scheduler/queue |
| D5 | A4 rollback validity post-A5 ship | **INVALIDATE** | bc-core A4 rollback verifier guard #300 fails post-A5; recorded in PR #153 + this closeout §4 |
| D6 | First real M12 run authorization | **separate gate** | M12 writer throws `M12NotImplementedError`; no runtime invocation path |
| D7 | Pre-A5 lockfile extension scope | **(b) FK + M12 writer table-identifier assertions** | `bcf-phase-a3-import-lockfile.mjs` extended at PR #151; 41/41 PASS |
| D8 | `contract.intake_queue` FK disposition | **retain** | Verified live: 1 inbound FK still present on `contract.panel_output_record` from `contract.intake_queue` |
| D9 | M14 stays CLOSED through A5 | YES | preserved throughout; no `BCCORE_M14_OPEN` env-gate |
| D10 | Statement count for A5 DDL | **10** | verified by runtime enumeration at apply gate + DDL synthesis unit test |
| D11 | Post-A5 DROP slice (F4 HYBRID roadmap) | **defer to post-A5 gate** | No DROP TABLE / DROP CONSTRAINT for contract.* BCF evidence in A5 |
| D12 | M12 writer SAVEPOINT smoke timing | **separate post-A5 authorization** | No `BCCORE_INTEGRATION_DB=1` execution; only unit tests run |

## 4. Substrate final state

Verified live via `bc-postgres` MCP read-only queries at closeout-authoring time:

### 4.1 mcf→bcf FKs LIVE (post-A5)

| FK name | Child table | Parent | On delete | On update |
|---|---|---|---|---|
| `fk_mcf_cert_panel_run` | `mcf.certification_record` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | NO ACTION |
| `fk_mapr_panel_run` | `mcf.metric_authoring_panel_run` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | NO ACTION |
| `fk_mcr_panel_run` | `mcf.metric_contract_revision` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | NO ACTION |
| `fk_mper_panel_run` | `mcf.metric_publication_eligibility_result` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | NO ACTION |
| `fk_mcs_panel_run` | `mcf.metric_supersession` | `bcf.panel_output_record(panel_run_uid)` | RESTRICT | NO ACTION |

All 5 FK names preserved across the retarget. ON DELETE RESTRICT and ON UPDATE NO ACTION preserved verbatim.

### 4.2 mcf→contract FKs DROPPED (post-A5)

| Substrate | Pre-A5 | Post-A5 | Δ |
|---|---|---|---|
| mcf→contract FKs (count) | 5 | **0 (DROPPED)** | -5 |

The 5 old mcf→contract FKs with names matching A5 retarget targets no longer exist; the FK identity (constraint name) was preserved by per-FK DROP-then-ADD swap pair within the single transaction.

### 4.3 contract.* still FROZEN (A4 freeze preserved)

| Substrate | Status |
|---|---|
| `contract.tg_panel_output_record_deny_write()` function | **PRESENT (LIVE; A4 freeze preserved)** |
| `contract.tg_authoring_panel_rejection_log_deny_write()` function | **PRESENT (LIVE)** |
| `contract.tg_calibration_event_deny_write()` function | **PRESENT (LIVE)** |
| `contract.tg_certification_record_deny_write()` function | **PRESENT (LIVE)** |
| `contract.*` deny-write functions (count) | **4** |
| `contract.*` deny-write trigger rows | **12** (4 tables × 3 events INSERT/UPDATE/DELETE; BEFORE FOR EACH STATEMENT) |
| `contract.tg_certification_record_target_registry_id_guard()` function | **0 (DROPPED per A4 C2; preserved)** |
| `contract.trg_certification_record_target_registry_id_guard` trigger rows | **0 (DROPPED per A4 C2; preserved)** |

### 4.4 bcf.cert write-once trigger still LIVE

| Substrate | Status | Notes |
|---|---|---|
| `bcf.tg_certification_record_target_registry_id_guard()` function | **PRESENT (1; LIVE)** | unchanged by A5 |
| `bcf.trg_certification_record_target_registry_id_guard` trigger | **2 rows (INSERT + UPDATE; BEFORE)** | unchanged by A5 |

### 4.5 Row counts unchanged

| Table | Rows | Δ vs pre-A5 baseline |
|---|---|---|
| `bcf.panel_output_record` | **19** | 0 |
| `bcf.authoring_panel_rejection_log` | **0** | 0 |
| `bcf.calibration_event` | **19** | 0 |
| `bcf.certification_record` | **3530** | 0 |
| `contract.panel_output_record` | **19** | 0 (FROZEN archive) |
| `contract.authoring_panel_rejection_log` | **0** | 0 (FROZEN archive) |
| `contract.calibration_event` | **19** | 0 (FROZEN archive) |
| `contract.certification_record` | **3530** | 0 (FROZEN archive) |
| `mcf.certification_record` | **0** | 0 |
| `mcf.metric_authoring_panel_run` (panel_run_uid not null) | **0** | 0 |
| `mcf.metric_contract_revision` (panel_run_uid not null) | **0** | 0 |
| `mcf.metric_publication_eligibility_result` (panel_run_uid not null) | **0** | 0 |
| `mcf.metric_supersession` (panel_run_uid not null) | **0** | 0 |

The A5 apply introduced only DDL (5 DROP CONSTRAINT + 5 ADD CONSTRAINT). Zero row mutations across all monitored tables.

### 4.6 FK topology delta (the central A5 invariant)

| Check | Pre-A5 | Post-A5 | Δ |
|---|---|---|---|
| Inbound FKs to `contract.panel_output_record` | 9 | **4** | **-5** |
| Cross-schema inbound on `bcf.panel_output_record` | 0 | **5** | **+5** |
| Cross-schema mcf→contract FKs | 5 | **0** | **-5** |
| Cross-schema mcf→bcf FKs | 0 | **5** | **+5** |
| Cross-schema FKs from `bcf.*` → non-`bcf.*` | **0** | **0** | 0 (R10 cluster separation invariant intact) |
| `contract.intake_queue` FK present on `contract.panel_output_record` | 1 | **1** | 0 (D8 retained) |

The 4 remaining inbound FKs on `contract.panel_output_record` are:
- 3 intra-contract sibling FKs (`fk_authoring_panel_rejection_log__panel_run`, `fk_calibration_event__panel_run`, `fk_certification_record__panel_run`)
- 1 contract.intake_queue FK (`fk_intake_queue__panel_run`) — **retained per D8**

## 5. D5 rollback-policy state change

### 5.1 Phase A4 rollback envelope: NOW INVALID

**As of apply-ts `2026-05-29T13-07-48-822Z`, the Phase A4 rollback envelope is NO LONGER VALID.** This is the central rollback-policy state change recorded by D5 operator acceptance + materialized by the A5 apply event.

Mechanically:
- Pre-A5, the bc-core A4 rollback verifier (`bcf-evidence-schema-phase-a4-rollback.mjs --mode=pre-rollback`) passed all 5 guards including #300 `a4_rollback_phase_a5_not_shipped`.
- Post-A5, guard #300 **fails** because the 5 mcf FKs no longer target `contract.panel_output_record` — restoring `contract.*` writability does NOT restore the FK topology.
- A4 rollback alone cannot un-retarget the 5 mcf FKs.

### 5.2 Operator must perform A5 rollback FIRST if combined A4+A5 rollback ever required post-A5

If a combined Phase A4 + Phase A5 rollback later becomes necessary, the required sequence is:

1. **Operator-authorized A5 rollback** (pre-first-M12-run window only):
   ```
   BCCORE_BCF_PHASE_A5_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_2026-05-29T13-07-48-822Z \
     TENANT_DATABASE_URL= node scripts/bcf-evidence-schema-phase-a5-rollback.mjs --mode=pre-rollback
   ```
   5 pre-rollback guards verify safety (#700 cliff predicate + #701 A4 freeze intact + #702 bcf rows present + #703 env-gate + #704 bcf.cert unchanged).
2. **Operator-driven DDL rollback action**:
   - DROP 5 mcf→bcf FKs
   - ADD 5 mcf→contract FKs with original parent + RESTRICT/NO ACTION semantics
3. **Operator-authorized A5 post-rollback verification**:
   ```
   BCCORE_BCF_PHASE_A5_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_2026-05-29T13-07-48-822Z \
     TENANT_DATABASE_URL= node scripts/bcf-evidence-schema-phase-a5-rollback.mjs --mode=post-rollback
   ```
   8 post-rollback assertions verify the retarget was reverted correctly.
4. **Only after A5 rollback completes**, the Phase A4 rollback envelope becomes valid again (guard #300 `a4_rollback_phase_a5_not_shipped` now PASSes).
5. **Then** the operator may invoke Phase A4 rollback per `scripts/bcf-evidence-schema-phase-a4-rollback.mjs --mode=pre-rollback` followed by operator-driven contract.* DDL restore.

### 5.3 A5 rollback envelope: AVAILABLE pre-first-M12-run only

The A5 rollback envelope itself remains available **only pre-first-M12-run** because:
- Guard #700 `a5_rollback_no_post_a5_mcf_rows` refuses if any mcf.* row references a panel_run_uid not present in `contract.panel_output_record`.
- Today: all 5 mcf.* panel_run_uid columns hold 0 rows; M12 writer is skeleton-only; outcome (A) per DBCP §7.4.
- Once M12 writes a new panel_run_uid to bcf.panel_output_record + a child row in mcf.*, that panel_run_uid will NOT exist in contract.panel_output_record (the contract.* tables are frozen by A4 deny-write triggers and accept no new INSERTs). A5 rollback that re-points the FK to contract.panel_output_record would fail FK validation on the orphaned mcf row — outcome (C) per DBCP §7.4.

Three rollback outcomes per DBCP §7.4:
- **(A) M12 has never run post-A5** → clean rollback. **← Today's live state.**
- **(B) M12 ran with only original 19 panel_run_uids** → clean rollback (those panel_run_uids exist in both bcf + contract by A2 byte-pinning).
- **(C) M12 ran with new panel_run_uids** → BLOCKED; row-destructive cleanup OR force-rollback-with-data-loss envelope required (operator-authorized; not authored in A5 base scope; deferred per DBCP §7.4 final).

### 5.4 Combined Phase A3 + step 20 rollback envelope: STILL INVALID

The combined Phase A3 + step 20 rollback envelope was already invalidated by Phase A4 apply per D9 (recorded in Phase A4 closeout PR #20 §5). A5 ship does not change that state — combined A3+step20 rollback remains INVALID. Any rollback chain back to pre-A3 would require:
1. A5 rollback first (cliff outcome A or B only)
2. Then A4 rollback
3. Then the combined A3 + step 20 rollback

## 6. F4 HYBRID post-A5 DROP roadmap

Per Phase A4 closeout §6 + locked D11: the F4 HYBRID post-A5 DROP slice for the 4 `contract.*` BCF evidence tables is **deferred to a separate post-A5 governance gate**. A5 does not perform any DROP TABLE / DROP CONSTRAINT for contract.* BCF evidence (verified live: row counts and trigger inventory both unchanged on the contract side).

The post-A5 DROP slice becomes structurally possible only after A5 retargets the 5 mcf→contract FKs to mcf→bcf — that condition is now met by this A5 apply, **but the actual DROP work is not in A5 scope.** It is gated on:
- Stable M12 traffic observation
- Operator authorization for the DROP gate (separate DBCP, separate authorization)
- Disposition of the remaining `contract.intake_queue` FK on `contract.panel_output_record` (D8 retained intake_queue, so DROP of `contract.panel_output_record` would require an additional retarget or DROP for that FK)

## 7. Evidence anchors

| Anchor | SHA / timestamp | Scope |
|---|---|---|
| **PR #21** — Phase A5 DBCP | bc-docs-v3 main `1d631d7` | Governance authority for the A5 design (10-stmt FK retarget; D1..D12 operator decisions) |
| **PR #151** — Phase A5 implementation | bc-core main `0d382f3` | 5 new scripts (DDL synth + dry-run + apply + post-apply + rollback verifier); lockfile extension 41/41 PASS; M12 greenfield writer skeleton; 16/16 unit tests PASS |
| **PR #152** — Phase A5 dry-run + sha256 pin | bc-core main `153c46d` | Dry-run timestamp `2026-05-29T12-51-13-686Z`; 4 artifacts (planned-ddl.sql + sha256.txt + evidence.jsonl + summary.md); 5/5 pre-apply probes PASS |
| **PR #153** — Phase A5 apply + post-apply | bc-core main `99edc1b` | Apply timestamp `2026-05-29T13-07-48-822Z`; post-apply timestamp `2026-05-29T13-07-57-405Z`; 5 artifacts (precondition + apply evidence + apply summary + post-apply evidence + post-apply summary); 10/10 apply assertions PASS; 10/10 post-apply assertions PASS |
| **Apply sha256 pin** | `9113b098d8428aef4b7eb1d075d7572c66902709ecc28b34644e27442e8be634` | Byte-equivalence binding between dry-run and apply gates; verified before DDL execution at apply-ts |
| **Substrate apply** | `bc_platform_dev` apply-ts `2026-05-29T13-07-48-822Z` | 10-statement F1 single-tx FK retarget DDL |

## 8. Scope discipline

| Discipline rule | Status |
|---|---|
| No row mutation introduced by A5 apply | ✓ all 13 row counts Δ=0 vs pre-A5 baseline |
| No `contract.*` DDL or DML | ✓ A5 DDL targets only mcf.* child tables (DROP/ADD CONSTRAINT only); contract.panel referenced as old parent in DROP statements (no contract.* mutation) |
| No `bcf.*` DDL beyond FK REFERENCES clause | ✓ A5 adds 5 inbound FKs to bcf.panel_output_record via mcf-side ALTER statements; no DDL targets bcf.* tables/functions/triggers |
| No FK changes outside the 5 retarget pair | ✓ `contract.intake_queue` FK retained (D8); 3 intra-contract sibling FKs unchanged |
| No tenant DB connection | ✓ TENANT_DATABASE_URL guard enforced across all A5 scripts |
| No M-series invocation | ✓ M11 / M12 / M12.5 / M13 not invoked; M12 writer skeleton throws on invocation |
| **M14 stays CLOSED** | ✓ (per D9; no `BCCORE_M14_OPEN` env-gate) |
| No first real M12 panel run | ✓ writer code unchanged; mcf.* panel_run_uid rows = 0 |
| A5 rollback NOT executed | ✓ apply succeeded; rollback envelope dormant (outcome A available) |
| Phase A4 rollback NOT executed (and now INVALID) | ✓ per D5 |
| HR1 — no synthetic / mock / replay / canned data | ✓ A5 DDL is FK retarget; no row insertion; deny-write triggers on contract.* structurally enforce HR1 going forward |
| HR2 — MCF evidence belongs in `mcf.*` | ✓ mcf.* FKs now reference the BCF substrate; semantic alignment achieved |
| HR3 — MCF metric authority events do not write to generic `contract.*` | ✓ A4 deny-write triggers structurally enforce; M12 writer skeleton imports bcf-side anchor; never references contract.* |
| HR4 — tenant result DBs separate | ✓ no tenant DB connection opened |
| HR5 — production paths; no mocks | ✓ A5 retarget applies to live contract→bcf FK topology |
| DEC-7f9597 / D423 stance ADR | ✓ honoured — operator authorization on mutating gate; rollback discipline preserved (A5 envelope pre-M12-run; A4 envelope INVALIDATED) |

## 9. Next-gate handoff: M14/M12 governance decision

### 9.1 What A5 does NOT do

A5 prepares the M12/M14 gate but does NOT open it. Per locked D4 (α prepare-only) + D6 (separate gate) + D9 (M14 stays CLOSED through A5) + D12 (M12 SAVEPOINT smoke separate authorization):
- **M14 remains CLOSED.**
- **M12 writer code path is implemented but NOT invoked.** The greenfield writer at `src/registry/metric-authoring/m12-panel-run-writer.service.ts` throws `M12NotImplementedError` on any invocation.
- **First real M12 panel run is NOT AUTHORIZED.**

### 9.2 Next operator-authorized gate

The **M14/M12 governance decision** is a SEPARATE operator-authorized governance gate. It is NOT part of Phase A5 scope and NOT performed by this closeout.

A reasonable structure for that gate:
1. **M14 unblock DBCP** authoring on bc-docs-v3 (governance design).
2. **Operator decision** on M14 unblock conditions (e.g. M12 SAVEPOINT smoke + reader smoke + observation period).
3. **M12 SAVEPOINT smoke gate** (per locked D12): run the M12 writer inside a SAVEPOINT, verify FK + downstream consumer semantics, ROLLBACK, no committed mutation.
4. **M12 reader smoke gate**: verify downstream consumers can read mcf.* without leakage to contract.*.
5. **M14 unblock apply** (operator-authorized): open M14 governance gate.
6. **First real M12 panel run** authorization (separate operator gate; the cliff-crossing event).

None of these steps are in A5 scope. They are referenced for context.

### 9.3 Required evidence before first real M12 panel run

Per Phase A5 DBCP §10.2, the eventual authorization of the first real M12 panel run requires:
1. Live FK inventory verifying 5 mcf→bcf FKs **— met by this closeout** (§4.1).
2. Live trigger inventory verifying 12 contract.* deny-write triggers + 4 functions LIVE **— met by this closeout** (§4.3).
3. Live row inventory verifying bcf/contract row counts unchanged **— met by this closeout** (§4.5).
4. **M12 writer SAVEPOINT smoke evidence** — NOT YET CAPTURED (separate post-A5 authorization per D12).
5. **M12 reader smoke evidence** — NOT YET CAPTURED.
6. **A clean operator-authorized M14 unblock gate run** — NOT YET CAPTURED.

A5 ship event + A5 closeout doc + bc-core PR evidence chain (PR #151/#152/#153) together compose the "infrastructure-ready" predicate (items 1-3 above). First-real-run authorization requires the additional items 4-6 (separate operator gates).

### 9.4 A5 rollback validity window narrows over time

The A5 rollback validity window is **today** at outcome (A) (clean rollback possible). Once M12 SAVEPOINT smoke runs, the rollback validity remains (the smoke runs inside a SAVEPOINT and rolls back; no committed mcf.* writes). Once the first real M12 panel run lands, the rollback window narrows:
- If the run uses one of the original 19 panel_run_uids → outcome (B) (still clean).
- If the run uses a new panel_run_uid → outcome (C) (BLOCKED; force-rollback-with-data-loss envelope required).

In practice, the M12 writer is expected to generate new panel_run_uids; the (C) cliff materializes at first real M12 run for any non-replay scenario.

## 10. Hard rule mapping (HR1..HR5)

| Rule | Closeout-time status |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | bcf substrate CHECKs + bcf.cert write-once trigger + contract.* deny-write triggers all enforce HR1 (synthetic-provider writes structurally rejected on bcf.*; ALL writes structurally rejected on contract.*). A5 added no synthetic data; the M12 writer skeleton throws on invocation |
| **HR2** — MCF evidence belongs in `mcf.*` | mcf.certification_record = 0; mcf.* row count remain at baseline; A5 design retargets mcf.* FKs to the BCF substrate per the boundary DBCP (Option A) |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.*` | A4 deny-write triggers structurally enforce HR3 at substrate level. M12 writer skeleton imports bcf-side panel anchor; never imports contract.* (lockfile assertion + unit test) |
| **HR4** — tenant result DBs separate | TENANT_DATABASE_URL guard enforced in all A5 scripts; tenant DB connection count = 0 throughout A5 ship sequence |
| **HR5** — production path; no mocks | A5 retarget applied to live `bc_platform_dev` substrate. Mocks confined to unit + SAVEPOINT-rolled-back integration tests |
| **Stance ADR DEC-7f9597 / D423** | Schema-boundary clarity reinforced via FK retarget (mcf authority now references bcf substrate). Rollback discipline preserved via A5 rollback envelope (available outcome A pre-M12-run). Operator authorization for mutating gates: A5 apply was operator-authorized at apply-ts `2026-05-29T13-07-48-822Z` |

## 11. Sequencing record

The complete A1 → A2 → A3 → step 20 → A4 → A5 chain under the merged Option A boundary DBCP:

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
14. ✓ Phase A4 DBCP (PR #19; D1..D10) merged — bc-docs-v3 main `dbc0378`
15. ✓ Phase A4 implementation (PR #148) merged — bc-core main `ebfb61a`
16. ✓ Phase A4 dry-run + sha256 pin (PR #149) merged — bc-core main `0f3093b`
17. ✓ Phase A4 apply executed — apply-ts `2026-05-29T11-21-03-131Z`
18. ✓ Phase A4 post-apply evidence captured — post-apply-ts `2026-05-29T11-21-13-074Z`
19. ✓ Phase A4 apply + post-apply evidence (PR #150) merged — bc-core main `6a8a67a`
20. ✓ Phase A4 closeout (PR #20) merged — bc-docs-v3 main `757071a`
21. ✓ **Phase A5 DBCP (PR #21; D1..D12) merged** — bc-docs-v3 main `1d631d7`
22. ✓ **Phase A5 implementation (PR #151) merged** — bc-core main `0d382f3`
23. ✓ **Phase A5 dry-run + sha256 pin (PR #152) merged** — bc-core main `153c46d`
24. ✓ **Phase A5 apply executed** — apply-ts `2026-05-29T13-07-48-822Z`
25. ✓ **Phase A5 post-apply evidence captured** — post-apply-ts `2026-05-29T13-07-57-405Z`
26. ✓ **Phase A5 apply + post-apply evidence (PR #153) merged** — bc-core main `99edc1b`
27. ✓ **This Phase A5 closeout doc** — bc-docs-v3
28. ⏸ M14 unblock DBCP authoring — SEPARATE operator-authorized governance gate (next)
29. ⏸ M12 writer SAVEPOINT smoke gate — gated on operator authorization (per D12)
30. ⏸ M12 reader smoke gate — gated on writer smoke evidence
31. ⏸ M14 unblock apply — gated on smoke evidence + separate operator authorization
32. ⏸ First real M12 panel run — gated on M14 unblock + separate operator authorization
33. ⏸ Post-A5 DROP slice (F4 HYBRID roadmap per Phase A4 closeout §6 + D11) — gated on stable M12 operation + separate governance gate

## 12. Discipline assertions (this closeout-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — closeout file lands only in bc-docs-v3 |
| No DDL applied | ✓ — closeout is docs-only; DDL was applied in the separately operator-authorized A5 apply gate at apply-ts `2026-05-29T13-07-48-822Z` |
| No DML applied | ✓ |
| No A5 rollback executed | ✓ |
| No Phase A4 rollback executed (and now INVALID per D5) | ✓ |
| No combined Phase A3 + step 20 rollback executed (still INVALID per D9) | ✓ |
| No bc-core PR opened by this closeout | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| No `mcf.*` row touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ (deny-write triggers would have rejected any attempt) |
| No `bcf.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No tenant `tbc_{slug}_dev` DB connection | ✓ |
| No first real M12 panel run | ✓ (M12 writer skeleton untouched; throws on invocation) |
| No PR #15 / #16 / #17 / #18 / #19 / #20 / #21 re-touch | ✓ |
| No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 / #148 / #149 / #150 / #151 / #152 / #153 re-touch | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured | ✓ |
| `bc-postgres` MCP `allow_write` used read-only only for substrate verification at closeout-authoring time | ✓ |

## 13. Out-of-scope re-statement

This closeout doc is **NOT** Phase A6 / M14 unblock / M-series.

This closeout doc does **NOT** authorize bc-core code execution.

This closeout doc does **NOT** authorize merging any bc-core PR; PR #151 / #152 / #153 are already merged.

This closeout doc does **NOT** authorize any `contract.*` row deletion. The deny-write triggers reject DELETE; future cleanup would require Phase A4 rollback (now INVALID per D5; would require A5 rollback first) + a separate row-mutation gate.

This closeout doc does **NOT** authorize any further `bcf.*` row mutation. The A5 retarget is COMPLETE; further substrate change requires a separately operator-authorized governance + apply gate.

This closeout doc does **NOT** authorize M12 writer invocation. The greenfield service throws `M12NotImplementedError` on any invocation per D3 + D6.

This closeout doc does **NOT** authorize the M14 unblock gate. M14 stays CLOSED per D9. M14 unblock is a separate operator-authorized governance gate.

This closeout doc does **NOT** authorize the first real M12 panel run. Per D6, that requires a separate post-M14-unblock authorization.

This closeout doc does **NOT** authorize the post-A5 DROP slice (F4 HYBRID roadmap per A4 closeout §6.3 + D11). Deferred to separate post-A5 governance gate.

This closeout doc does **NOT** touch tenant DBs.

This closeout doc does **NOT** alter `mcf.*`, `metric.*`, `concept_registry.*`, or any further `contract.*` substrate beyond what was applied at apply-ts `2026-05-29T13-07-48-822Z`.

This closeout doc does **NOT** open M14.

This closeout doc does **NOT** initiate the first real M12 panel run.

This closeout doc does **NOT** execute A5 rollback.

This closeout doc does **NOT** validate the Phase A4 rollback envelope. That envelope is **INVALID** per D5.

This closeout doc does **NOT** validate the combined Phase A3 + step 20 rollback envelope. That envelope is **INVALID** per D9 (Phase A4 closeout PR #20 §5).

---

**End of closeout. Phase A5 mcf→bcf FK retarget ship event RECORDED. Next operator-authorized gate: M14/M12 governance decision (separate operator authorization).**
