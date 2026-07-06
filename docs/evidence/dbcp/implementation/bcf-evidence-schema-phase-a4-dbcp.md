---
uid: bcf-evidence-schema-phase-a4-dbcp
title: BCF Evidence Schema — Phase A4 DBCP (contract.* BCF evidence freeze/retire after combined A3 + step 20 ship)
description: Phase A4 design DBCP for the disposition of the 4 `contract.*` BCF evidence tables (panel_output_record, authoring_panel_rejection_log, calibration_event, certification_record) after the completed Phase A3 + §14 step 20 atomic-pair ship event (bc-docs-v3 main `5757936`; bc-core main `781660b`). Enumerates the substrate state (bcf.cert write-once trigger LIVE; contract.cert trigger preserved; bcf.* + contract.* row counts 19/0/19/3530 each; no bcf→contract FKs; 9 inbound FKs on `contract.panel_output_record` of which 5 are cross-schema mcf→contract pending A5 retarget); the four candidate dispositions (FREEZE / RETIRE-DROP / READ-ONLY-ARCHIVE / HYBRID); the recommended HYBRID strategy gated on A5 sequencing; the inventory required to inform the operator decision; the test/evidence + rollback plan; the risk register R1..R10 and operator decisions D1..D10. **NOT EXECUTED.** This DBCP authorizes design only; the bc-core implementation PR is a separately operator-authorized follow-up. **No DDL applied, no DML applied, no Phase A4 apply, no rollback executed, no tenant DB connection, no M-series invocation. M14 stays CLOSED. A5 NOT started.** Operator stance ADR DEC-7f9597 / D423 honoured — operator authorization on mutating gates; rollback discipline preserved; substrate-boundary clarity maintained.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a4-contract-evidence-freeze-or-retire
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A4 DBCP (contract.* BCF evidence freeze/retire)

## 1. Scope

### 1.1 Question this DBCP answers

> The Phase A3 + §14 step 20 atomic-pair shipped under D11(δ) δ.1 at apply-ts `2026-05-29T09-24-54-689Z`, anchored in evidence at bc-core main `781660b` (PR #147) and closed out at bc-docs-v3 main `5757936` (PR #18). The 4 `contract.*` BCF evidence tables (`panel_output_record`, `authoring_panel_rejection_log`, `calibration_event`, `certification_record`) now hold preserved duplicate rows (19 / 0 / 19 / 3530) with no new BCF authority writes routing to them. The `contract.tg_certification_record_target_registry_id_guard` trigger and function remain present on `contract.certification_record`. What is the correct Phase A4 disposition for these 4 tables — FREEZE (deny-write triggers + REVOKE), RETIRE-DROP (drop the tables and their triggers/function), READ-ONLY-ARCHIVE (temporary preservation for historical audit), or HYBRID (per-table strategy) — given that 9 inbound FKs reference `contract.panel_output_record` (3 intra-contract sibling + 1 contract.intake_queue + 5 cross-schema mcf→contract pending A5 retarget) and that A5 is the next-after-A4 gate that retargets the mcf FKs?

### 1.2 In scope

- **Inventory of the current substrate state** — bcf.* + contract.* + mcf.* row counts; bcf.* + contract.* trigger/function state; the 9 inbound FKs to `contract.panel_output_record`; the zero inbound FKs to the other 3 contract.* BCF evidence tables; the `contract.certification_record` trigger/function presence.
- **Inventory of source-code references** — production source files (`src/registry/`), test specs, scripts (`scripts/`), and migration SQL (`docker/redesign/migrations/`) that reference the 4 contract.* BCF evidence tables — to detect any hidden reader/writer that would break under freeze/retire.
- **Disposition options** — FREEZE (deny-write triggers + role REVOKE), RETIRE-DROP (DROP TABLE CASCADE-controlled), READ-ONLY-ARCHIVE (read-grant-only without delete), HYBRID (per-table strategy).
- **Recommendation** — operator-presented; gated on A5 sequencing for `contract.panel_output_record` because 5 cross-schema mcf→contract FKs reference it.
- **Test/evidence plan** — static grep lockfile extension; DB FK inventory probe; write-denial integration test inside SAVEPOINT rollback; post-apply row-count invariants; bcf writer path remains active; no MCF FK changes.
- **Combined-rollback impact** — once A4 ships, the combined Phase A3 + §14 step 20 rollback envelope is no longer valid (writes cannot route back to contract.*); A4 owns its own restore plan.
- **A4-vs-A5 boundary** — A5 owns MCF FK retarget; A4 must not touch mcf FKs; A4 either defers `contract.panel_output_record` disposition until A5 ships, or selects a freeze-only strategy that does not require FK changes.
- **Risk register R1..R10** + **operator decisions D1..D10**.
- Authorization to author the bc-core implementation PR(s) in a follow-up; that PR's apply gate is a SEPARATE operator authorization.

### 1.3 Explicit non-scope

- ❌ **No DDL applied.** This DBCP designs the freeze/retire; the apply gate is a separately operator-authorized follow-up.
- ❌ **No DML applied.** No row mutation on `bcf.*` / `contract.*` / `mcf.*` / `concept_registry.*` / any tenant DB.
- ❌ **No bc-core code change.** Authoring the implementation PR is a SEPARATE follow-up operator authorization.
- ❌ **No combined Phase A3 + §14 step 20 rollback executed.** That envelope remains available pre-A4-apply. A4-apply changes that.
- ❌ **No MCF FK retarget.** Phase A5 owns. A4 must not modify the 5 cross-schema mcf→contract FKs.
- ❌ **No A5 work.** A5 design is a separate operator-authorized governance gate.
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M14 remains CLOSED.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** HR4 substrate-enforced.
- ❌ **No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 re-touch.**
- ❌ **No PR #15 / #16 / #17 / #18 re-touch.**
- ❌ **No re-litigation of Option A.** `bcf.*` is the locked target; `concept_registry.*` is BCR vocabulary and remains untouched.
- ❌ **No bc-admin / bc-portal UI changes.** No HTTP API contract changes.

## 2. Authority anchor chain

| Artifact | Location | Authority for |
|---|---|---|
| **Boundary DBCP (Option A)** | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` (PR #11) | Option A target; 5-phase ladder; A4 sits in the §13 sequencing as the contract.* freeze/retire phase |
| Phase A1 substrate-design DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-dbcp.md` @ bc-docs-v3 main `70beeb7` | `bcf.*` column / CHECK / index / FK shape; HR1 substrate enforcement |
| Phase A1 apply DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-apply-dbcp.md` @ bc-docs-v3 main `cdc6efa` | Apply-gate pattern (env-gate + sha256 + single-tx + post-apply assertions) |
| Phase A2 migration DBCP | `docs/implementation/bcf-evidence-schema-phase-a2-migration-dbcp.md` @ bc-docs-v3 main `36acb27` | Insert-copy semantics; byte-pinned rows; 3,568 authority rows migrated to bcf.* with contract.* duplicates preserved |
| Phase A3 cutover DBCP (original) | `docs/implementation/bcf-evidence-schema-phase-a3-writer-reader-cutover-dbcp.md` @ bc-docs-v3 main `d06eeba` (PR #15) | W1..W3 + W4a writer flip; R1..R8 reader flip minus F6α joint-defer subset |
| Phase A3 DBCP correction (D11(δ) locked) | `docs/implementation/bcf-evidence-schema-phase-a3-writer-reader-cutover-dbcp.md` @ bc-docs-v3 main `21aa442` (PR #16) | §3.5 BLOCKING FINDING; §11 R9 extended; §12 D11(δ) locks atomic-pair apply with step 20; §14 step 18 BLOCKED; §16 forbids standalone A3 apply |
| Phase A3.5 / §14 step 20 DBCP | `docs/implementation/bcf-evidence-schema-phase-a3-step-20-dbcp.md` @ bc-docs-v3 main `b0bd475` (PR #17) | Step 20 DDL design + code-routing flip set + atomic-pair apply model + combined rollback plan |
| Phase A3 + §14 step 20 closeout | `docs/implementation/bcf-evidence-schema-phase-a3-step-20-closeout.md` @ bc-docs-v3 main `5757936` (PR #18) | Ship event record; substrate final state; F3a/F6α joint-defer set fully flipped; rollback NOT executed; **A4 is the next gate** |
| Phase A3 implementation (PR #141) | bc-core main `5f7f8fe` | W1..W3 + W4a flip + R1..R8 flip minus F6α joint-defer subset |
| Phase A3 spec hygiene (PR #142) | bc-core main `e0bdbc6` | panel fixture imports flipped to bcf in 3 integration specs |
| Phase A3 apply/rollback scripts (PR #143) | bc-core main `0a34817` | Post-apply evidence script + rollback verifier extensions |
| Phase A3 harness repair + FK finding (PR #144) | bc-core main `68cee3f` | framework-approval test-harness factory; uncovered the W1→W4b FK violation |
| Step 20 implementation (PR #145) | bc-core main `9cb3ce0` | DDL synth + W4b/W5/R6/R5/R4-cert flips + verifier extensions |
| Step 20 dry-run + sha256 pin (PR #146) | bc-core main `45da6e1` | sha256 `13502ba12aa0e5db1f1dd4531d21ba426b8d8d98fd0b521601803532057ce223` binding |
| Combined apply + post-apply (PR #147) | bc-core main `781660b` | apply-ts `2026-05-29T09-24-54-689Z`; bcf.cert trigger LIVE |
| **bc-docs-v3 anchor (this DBCP base)** | bc-docs-v3 main `575793640ddfba4a7cfc5039bcdcdfbf3125efcf` (post-PR-#18 merge) | Governance audit trail with full A3 + step 20 ship loop closed |
| bc-core anchor (A4 implementation base) | bc-core main `781660b2bbfdbda90d99ef56add7a4b85acba577` | Code state the future A4 implementation PR will modify |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) | Schema-boundary clarity, rollback discipline, operator authorization on mutating gates |
| Hard rules HR1..HR5 | parent boundary DBCP §5 | Substrate constraints A4 design must respect |

## 3. Current substrate state (verified live)

### 3.1 Row counts

Verified via `bc-postgres` MCP read-only queries at A4-DBCP-authoring time:

| Table | Rows | Notes |
|---|---|---|
| `bcf.panel_output_record` | **19** | A2-migrated authority rows |
| `bcf.authoring_panel_rejection_log` | **0** | A2 baseline; no historical rejections |
| `bcf.calibration_event` | **19** | A2-migrated authority rows |
| `bcf.certification_record` | **3530** | A2-migrated authority rows |
| `contract.panel_output_record` | **19** | duplicate preserved post-A2 |
| `contract.authoring_panel_rejection_log` | **0** | duplicate preserved post-A2 |
| `contract.calibration_event` | **19** | duplicate preserved post-A2 |
| `contract.certification_record` | **3530** | duplicate preserved post-A2 |
| `mcf.certification_record` | **0** | M-series CLOSED; no MCF authority writes yet |

bcf.* and contract.* row counts are byte-pinned siblings under the Phase A2 migration's insert-copy semantics. No new BCF authority writes route to contract.* post-A3 + step 20 (the F3a / F6α joint-defer set is fully flipped per PR #18 §3.3).

### 3.2 Trigger / function inventory

| Schema | Object | Status |
|---|---|---|
| `bcf` | `tg_certification_record_target_registry_id_guard` function | **PRESENT (LIVE since apply-ts `2026-05-29T09-24-54-689Z`)** |
| `bcf` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for INSERT (BEFORE) | **PRESENT** |
| `bcf` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for UPDATE (BEFORE) | **PRESENT** |
| `contract` | `tg_certification_record_target_registry_id_guard` function | **PRESERVED (1)** — pre-A4; A4 owns disposition |
| `contract` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for INSERT (BEFORE) | **PRESERVED** — pre-A4; A4 owns disposition |
| `contract` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for UPDATE (BEFORE) | **PRESERVED** — pre-A4; A4 owns disposition |

The 3 other contract.* BCF evidence tables (`panel_output_record`, `authoring_panel_rejection_log`, `calibration_event`) have NO triggers in the `contract` schema (verified by `information_schema.triggers` query at A4-DBCP-authoring time).

### 3.3 FK inventory (the disposition-blocking finding)

**Inbound FKs targeting `contract.panel_output_record` (9 total)**:

| Direction | FK name | Source | Target | Notes |
|---|---|---|---|---|
| intra-contract | `fk_authoring_panel_rejection_log__panel_run` | `contract.authoring_panel_rejection_log` | `contract.panel_output_record` | sibling FK |
| intra-contract | `fk_calibration_event__panel_run` | `contract.calibration_event` | `contract.panel_output_record` | sibling FK |
| intra-contract | `fk_certification_record__panel_run` | `contract.certification_record` | `contract.panel_output_record` | sibling FK |
| contract→contract | `fk_intake_queue__panel_run` | `contract.intake_queue` | `contract.panel_output_record` | the R8 SPLIT preserves intake_queue on contract; FK preserves the panel reference |
| **cross-schema (mcf→contract)** | `fk_mcf_cert_panel_run` | `mcf.certification_record` | `contract.panel_output_record` | **A5 retarget scope** |
| **cross-schema (mcf→contract)** | `fk_mapr_panel_run` | `mcf.metric_authoring_panel_run` | `contract.panel_output_record` | **A5 retarget scope** |
| **cross-schema (mcf→contract)** | `fk_mcr_panel_run` | `mcf.metric_contract_revision` | `contract.panel_output_record` | **A5 retarget scope** |
| **cross-schema (mcf→contract)** | `fk_mper_panel_run` | `mcf.metric_publication_eligibility_result` | `contract.panel_output_record` | **A5 retarget scope** |
| **cross-schema (mcf→contract)** | `fk_mcs_panel_run` | `mcf.metric_supersession` | `contract.panel_output_record` | **A5 retarget scope** |

**Inbound FKs targeting `contract.authoring_panel_rejection_log`, `contract.calibration_event`, `contract.certification_record`**: **ZERO each**. Verified by `pg_constraint` query at A4-DBCP-authoring time.

### 3.4 Cross-schema FK invariant (R10) state

| Check | Value |
|---|---|
| FKs from `bcf.*` → non-`bcf.*` | **0** (R10 intact since Phase A1) |
| FKs from `mcf.*` → `contract.*` | **5** (the 5 mcf→contract FKs above; A5 will retarget these to `bcf.panel_output_record`) |

The bcf cluster separation invariant is intact. The mcf→contract cross-schema dependency exists by design pre-A5 and is **out of A4 scope**.

### 3.5 Code-routing state (post step 20)

Per the merged step 20 closeout (PR #18) §3.3 + §6.4:

- W1..W3 + W4 (W4a + W4b combined) + W5 all write to bcf.*
- R1..R8 readers all read from bcf.* with the documented R8 SPLIT preserving `intakeQueue` on contract (intake_queue is NOT a BCF cert; only its panel-side reference is on bcf)
- F3a / F6α joint-defer set fully flipped to bcf
- Documented exception list size for BCF cert evidence paths = **0**
- Lockfile 16/16 PASS post-step-20

## 4. Disposition options

### 4.1 Option F1 — FREEZE all 4 contract.* BCF evidence tables

Add a **deny-write trigger** to each of the 4 contract.* BCF evidence tables that RAISE EXCEPTION on any INSERT / UPDATE / DELETE. Optionally REVOKE write privileges from the application role(s).

| Property | Value |
|---|---|
| **DDL surface** | 4 new functions + 4 new triggers (BEFORE INSERT OR UPDATE OR DELETE FOR EACH STATEMENT or FOR EACH ROW); optional GRANT/REVOKE |
| **Inbound FK impact** | FKs continue to resolve against the existing rows; no FK changes |
| **Row preservation** | All rows preserved (read-only) |
| **A5 sequencing dependency** | None — freeze works pre-A5 because no DROP is required |
| **Rollback path** | DROP TRIGGER + DROP FUNCTION; rollback restores writable state |
| **Tradeoff** | Tables remain in the schema indefinitely; storage cost; visible to readers; trigger maintenance burden |

### 4.2 Option F2 — RETIRE-DROP all 4 contract.* BCF evidence tables

`DROP TABLE contract.certification_record`, `DROP TABLE contract.calibration_event`, `DROP TABLE contract.authoring_panel_rejection_log`, `DROP TABLE contract.panel_output_record` (last). Drop the contract-side trigger + function alongside contract.certification_record (CASCADE or explicit DROP TRIGGER + DROP FUNCTION). Optionally `DROP SCHEMA contract IF EMPTY` if the schema has no remaining objects (it does — `contract` schema houses many other contract artifacts; **DROP SCHEMA is OUT OF SCOPE**).

| Property | Value |
|---|---|
| **DDL surface** | 4 DROP TABLE statements (in FK-aware order: cert/cal/rej before panel) + 1 DROP TRIGGER + 1 DROP FUNCTION |
| **Inbound FK impact** | **BLOCKING for `contract.panel_output_record`** — 5 cross-schema mcf→contract FKs reference it; DROP fails until A5 retargets them. The 1 intake_queue FK also references it; intake_queue would need to be considered |
| **Row preservation** | None — all rows destroyed |
| **A5 sequencing dependency** | **`contract.panel_output_record` DROP requires A5 retarget of 5 mcf FKs + retarget or removal of the 1 intake_queue FK** |
| **Rollback path** | None practical — restoring dropped tables requires the Phase A2 migration's pre-A2 backup OR a custom restore from `scripts/bcf-authoring-test-row-cleanup-restore.mjs` (PR #133 backup pattern); risky |
| **Tradeoff** | Cleanest end state; smallest storage; no trigger maintenance; but blocking on A5 + irreversible |

### 4.3 Option F3 — READ-ONLY-ARCHIVE (no triggers; REVOKE only)

REVOKE all write privileges (INSERT, UPDATE, DELETE) from the application role(s) on the 4 contract.* BCF evidence tables. Optionally `ALTER TABLE … SET (toast_tuple_target = …)` or similar storage-optimization hints. Leave triggers in place (or drop them — see D5).

| Property | Value |
|---|---|
| **DDL surface** | REVOKE statements; optional ALTER TABLE for storage hints |
| **Inbound FK impact** | None — FKs continue to resolve |
| **Row preservation** | All rows preserved |
| **A5 sequencing dependency** | None |
| **Rollback path** | GRANT back the write privileges |
| **Tradeoff** | Weaker than F1 (REVOKE bypassed if a superuser-owned migration runs; trigger gives DB-level enforcement). REVOKE is per-role; freeze trigger is global |

### 4.4 Option F4 — HYBRID per-table strategy (RECOMMENDED for design discussion)

Apply F1 FREEZE to all 4 contract.* BCF evidence tables in A4. Defer DROP of all 4 tables to a post-A5 phase (which the boundary DBCP labels A4.5 or absorbs into A6; **out of A4 scope**). The hybrid breaks down as:

| Table | A4 disposition | Post-A5 disposition (out of A4 scope) |
|---|---|---|
| `contract.authoring_panel_rejection_log` | FREEZE (deny-write trigger; 0 inbound FKs so DROP is structurally safe but deferred for consistency with the panel table) | DROP after A5 |
| `contract.calibration_event` | FREEZE (deny-write trigger; 0 inbound FKs) | DROP after A5 |
| `contract.certification_record` | FREEZE (deny-write trigger; 0 inbound FKs; existing born-null/write-once trigger COEXISTS with new deny-write trigger OR is replaced by the deny-write trigger — D5) | DROP after A5 (with cleanup of trigger + function if not already removed) |
| `contract.panel_output_record` | FREEZE (deny-write trigger; 9 inbound FKs — 3 intra-contract + 1 intake_queue + 5 mcf cross-schema) | DROP after A5 retargets the 5 mcf FKs AND A5 (or follow-on phase) removes the intake_queue FK OR repoints it to bcf.panel_output_record |

This is RECOMMENDED for design because it (a) immediately freezes BCF authority writes to contract.* (catching any hidden writer), (b) preserves rows for historical audit / restore window, (c) defers DROP to after A5 when the mcf FK constraint is resolved, (d) keeps the combined Phase A3 + step 20 rollback envelope clean to revert to (rollback can DROP the deny-write triggers without DROPping the rows).

### 4.5 Recommendation matrix

| Option | Pre-A5 safe? | Row preservation | Reversible? | Recommendation |
|---|---|---|---|---|
| F1 FREEZE all 4 | ✓ yes | ✓ yes | ✓ yes (DROP TRIGGER) | strong candidate; recommended for D1 |
| F2 RETIRE-DROP all 4 | ✗ no — blocks on `contract.panel_output_record`'s 5 mcf FKs | ✗ no | ✗ no (without restore) | NOT recommended pre-A5; consider only post-A5 |
| F3 READ-ONLY-ARCHIVE (REVOKE) | ✓ yes | ✓ yes | ✓ yes (GRANT back) | weaker than F1 (no DB-level enforcement against superuser writes); not recommended |
| F4 HYBRID (F1 now; DROP post-A5) | ✓ yes | ✓ yes (until post-A5 DROP) | ✓ yes (pre-DROP phase) | RECOMMENDED design pattern; same A4 surface as F1 with explicit post-A5 plan documented |

**Recommendation: Operator selects F1 or F4 in D1.** The recommended HYBRID (F4) is functionally identical to F1 in the A4 surface — the only difference is whether the documentation commits to a post-A5 DROP phase. Both close BCF authority writes to contract.*; both preserve rows; both are reversible.

**F2 (RETIRE-DROP) is NOT recommended pre-A5** because `contract.panel_output_record` cannot be dropped until A5 retargets the 5 mcf cross-schema FKs (and the intake_queue FK is addressed).

**F3 (READ-ONLY-ARCHIVE) is NOT recommended** because trigger-based deny-write is structurally stronger than REVOKE (a superuser-owned migration can bypass REVOKE; cannot bypass a BEFORE trigger).

## 5. Required inventory (informing the operator decision)

### 5.1 Inbound FKs to the 4 contract.* BCF evidence tables

Verified live at A4-DBCP-authoring time (§3.3 above):

- `contract.panel_output_record`: **9 inbound FKs** (3 intra-contract sibling + 1 intake_queue + 5 cross-schema mcf)
- `contract.authoring_panel_rejection_log`: **0 inbound FKs**
- `contract.calibration_event`: **0 inbound FKs**
- `contract.certification_record`: **0 inbound FKs**

### 5.2 Remaining source-code imports/readers/writers of contract.* BCF evidence tables (post step 20)

Static grep against `bc-core/src/` at A4-DBCP-authoring time:

| File | Import | Disposition |
|---|---|---|
| `src/registry/framework-calibration/bcf-b8-calibration-event-ingest.spec.ts` | `import { calibrationEvent } from '../../database/schema/contract'` (line 16) | **HYGIENE GAP** — this test spec was not flipped during step 20 (the 3 integration specs that PR #145 flipped did not include this B8 ingest spec). Pre-existing failure on baseline (per PR #145 review); flipping this fixture is a hygiene item the A4 implementation PR should fold in (no functional impact on substrate state) |

All other production source files under `src/registry/` import BCF evidence symbols from bcf, not contract. Documented exception list size for BCF cert evidence paths = 0 (verified by the post-step-20 lockfile). The R8 SPLIT (`intakeQueue` from contract) is preserved as designed — `intake_queue` is NOT a BCF evidence table.

### 5.3 Audit-output / restore scripts that intentionally reference contract.* BCF evidence tables

Static grep against `bc-core/scripts/` at A4-DBCP-authoring time:

| Script class | Reference type | A4 disposition |
|---|---|---|
| `bcf-evidence-schema-phase-a2-*.mjs` (4 scripts) | Phase A2 migration source-of-truth references contract.* as the **source** for the insert-copy migration | **HISTORICAL** — these scripts implemented A2; references are descriptive of past state. No A4 modification needed |
| `bcf-evidence-schema-phase-a3-*.mjs` (5 scripts incl. step 20 trio) | Phase A3 / step 20 references contract.* for pre/post assertion baselines (#204-#207, #218-#219, etc.) | **EVIDENCE** — these references continue to be useful post-A4 freeze (the assertion semantics shift from "contract.* unchanged" to "contract.* still-frozen-and-unchanged"). Minor wording updates may be needed |
| `bcf-evidence-schema-phase-a1-*.mjs` (3 scripts) | Phase A1 references contract.* for cross-schema FK invariant probe | **HISTORICAL** — A1 is closed; references are descriptive of pre-A1 state |
| `bcf-authoring-test-row-cleanup-restore.mjs` (PR #133 restore pattern) | references `contract.panel_output_record` = 24, `contract.authoring_panel_rejection_log` = 1, `contract.calibration_event` = 23, `contract.certification_record` = 3531 (pre-A2 baseline; the 24/1/23/3531 row counts predate the A2 migration which left contract.* at 19/0/19/3530 after the authority rows moved to bcf) | **HISTORICAL** — this restore script is for PR #133 cleanup pre-A3 and operates on pre-A2 row counts. Post-A4 freeze, this restore script becomes inapplicable (it cannot run against frozen tables). Operator decision D6 covers whether to retire this script alongside A4 |
| `mcf-m3` through `mcf-m13` scripts (post-apply / dry-run / cert-amendment) | reference `contract.panel_output_record` for cross-schema FK invariant checks (the 5 mcf→contract FKs) | **PRE-A5** — these references will remain valid until A5 retargets the mcf FKs; A4 must not modify these scripts (A5 owns their disposition) |
| `docker/redesign/migrations/*.sql` (44 historical migration files) | reference contract.* BCF evidence tables in their DDL (CREATE TABLE / ALTER TABLE / etc.) | **HISTORICAL** — migration files are the substrate's evolution history. A4 does not modify these. A4 adds a NEW migration file for the freeze DDL |

### 5.4 PR #133 restore implications

`scripts/bcf-authoring-test-row-cleanup-restore.mjs` (per §5.3 above) is a restore script for PR #133's test-row cleanup. It operates on pre-A2 row counts (24/1/23/3531) and is designed to UNDO a test-row cleanup. Post-A2, the contract.* row counts are 19/0/19/3530 — the 5/1/4/1 difference reflects the test rows that were removed by PR #133's cleanup.

The implications for A4:
- The restore script's reference to contract.* is **descriptive** (it documents the pre-A2 row counts as the restore target).
- Post-A4 freeze, the script cannot execute (the deny-write trigger would reject the restore INSERTs).
- Operator decision D6 covers whether to (a) retire the script alongside A4 (delete it; PR #133 cleanup is closed), or (b) document the script as historical evidence without retiring.

**A4 does not modify this script. A4's implementation PR can include a separate hygiene commit retiring it if D6 chooses retirement.**

### 5.5 Contract.cert trigger / function disposition

The `contract.tg_certification_record_target_registry_id_guard()` function + `trg_certification_record_target_registry_id_guard` trigger on `contract.certification_record` (BEFORE INSERT OR UPDATE FOR EACH ROW) currently enforce born-null + write-once + append-only invariants on `contract.certification_record`.

Post-A4 (under F1/F4 FREEZE) options for the contract trigger:

| Option | Description |
|---|---|
| **C1** — **COEXIST** | Leave the existing born-null/write-once trigger in place; ADD a new deny-write trigger that fires first (BEFORE INSERT OR UPDATE OR DELETE). The deny-write trigger rejects all DML before the existing trigger fires. Existing trigger becomes operationally inert |
| **C2** — **REPLACE** | DROP the existing born-null/write-once trigger and function; ADD a deny-write trigger only |
| **C3** — **MIXED** | DROP the existing trigger; keep the function (in case a future code path wants to share it); ADD a deny-write trigger |

Operator decision **D5** covers this. Recommended: **C2 REPLACE** because (a) the deny-write trigger semantically supersedes the born-null/write-once trigger (no writes are permitted at all, so the more restrictive sub-invariants are moot), (b) cleaner end state, (c) the existing trigger DROP is reversible by re-applying the source DDL.

## 6. DDL design

### 6.1 Deny-write trigger function pattern (per table)

```sql
CREATE OR REPLACE FUNCTION contract.tg_<table>_deny_write()
  RETURNS trigger AS $$
BEGIN
  RAISE EXCEPTION
    'contract.<table> is frozen (Phase A4 ship at <apply-ts>; bc-docs-v3 <closeout-sha>) — all DML rejected. BCF authority writes now route to bcf.<table>. Pre-A5 rollback envelope: see bcf-evidence-schema-phase-a4-rollback.mjs --mode=pre-rollback.';
END;
$$ LANGUAGE plpgsql;
```

Bound on each contract.* BCF evidence table as `BEFORE INSERT OR UPDATE OR DELETE ON contract.<table> FOR EACH STATEMENT EXECUTE FUNCTION contract.tg_<table>_deny_write()`.

(FOR EACH STATEMENT is cheaper than FOR EACH ROW and sufficient for deny-write semantics — the trigger fires once per statement, RAISES, and aborts.)

### 6.2 Contract.cert existing trigger disposition (per D5)

Under recommended **C2 REPLACE**:
- `DROP TRIGGER IF EXISTS trg_certification_record_target_registry_id_guard ON contract.certification_record;`
- `DROP FUNCTION IF EXISTS contract.tg_certification_record_target_registry_id_guard();`
- Then the new deny-write trigger + function above is the only trigger on `contract.certification_record`.

### 6.3 Idempotency

`CREATE OR REPLACE FUNCTION` + `DROP TRIGGER IF EXISTS` + `CREATE TRIGGER`. Re-apply is safe (mirrors Phase A1 / step 20 idempotency pattern).

### 6.4 Statement count

Under F1/F4 + C2:
- 4 × CREATE OR REPLACE FUNCTION (one per table, deny-write)
- 4 × DROP TRIGGER IF EXISTS (one per table; idempotent)
- 4 × CREATE TRIGGER (one per table)
- 1 × DROP TRIGGER IF EXISTS (contract.cert existing trigger)
- 1 × DROP FUNCTION IF EXISTS (contract.cert existing function)

**Total: 14 statements** (single transaction).

Under F4 with C1 COEXIST:
- 4 × CREATE OR REPLACE FUNCTION (deny-write)
- 4 × DROP TRIGGER IF EXISTS
- 4 × CREATE TRIGGER (deny-write)
- 0 × contract.cert existing trigger modifications

**Total: 12 statements** (single transaction; existing contract.cert trigger preserved alongside new deny-write trigger).

### 6.5 No bcf.* changes

The bcf.* substrate is unchanged by A4. The bcf.cert write-once trigger remains LIVE. bcf.* writers continue to operate.

### 6.6 No mcf.* / concept_registry.* changes

mcf.* is A5 scope. concept_registry.* is BCR vocabulary and out of A4 scope.

### 6.7 No cross-schema FK introduction or removal

A4 does not modify any FK. The 9 inbound FKs on `contract.panel_output_record` (incl. the 5 cross-schema mcf→contract FKs) remain in place.

## 7. Test/evidence plan

### 7.1 Static import lockfile extension

`scripts/bcf-phase-a3-import-lockfile.mjs` (16/16 PASS post-step-20) is extended with new A4 assertions:

| New assertion | Scope |
|---|---|
| A4 DDL synthesis module declares 4 deny-write triggers (one per contract.* BCF evidence table) | Structural check on the implementation PR's DDL synthesis module |
| A4 DDL synthesis module does NOT modify bcf.* triggers | Structural check |
| A4 DDL synthesis module does NOT modify mcf.* objects | Structural check |
| A4 DDL synthesis module does NOT add cross-schema FKs | Structural check |
| (per D5 selection: under C2) A4 DDL synthesis module drops contract.cert existing trigger + function | Structural check |
| `scripts/bcf-authoring-test-row-cleanup-restore.mjs` retired (per D6 selection) | Optional structural check if D6 = retire |
| `bcf-b8-calibration-event-ingest.spec.ts` test-fixture flipped to bcf (per §5.2 hygiene gap) | Optional structural check |

### 7.2 DB FK inventory probe

A pre-apply read-only probe verifies the 9 inbound FKs to `contract.panel_output_record` are unchanged from §3.3 baseline:

```sql
SELECT count(*)::int AS n
FROM pg_constraint c
JOIN pg_class t ON t.oid = c.conrelid
JOIN pg_namespace tn ON tn.oid = t.relnamespace
JOIN pg_class rt ON rt.oid = c.confrelid
JOIN pg_namespace rn ON rn.oid = rt.relnamespace
WHERE c.contype = 'f'
  AND rn.nspname = 'contract'
  AND rt.relname = 'panel_output_record';
-- Expected: 9
```

A second probe verifies the cross-schema mcf→contract FK count:

```sql
SELECT count(*)::int AS n
FROM pg_constraint c
JOIN pg_class t ON t.oid = c.conrelid
JOIN pg_namespace tn ON tn.oid = t.relnamespace
JOIN pg_class rt ON rt.oid = c.confrelid
JOIN pg_namespace rn ON rn.oid = rt.relnamespace
WHERE c.contype = 'f'
  AND tn.nspname = 'mcf'
  AND rn.nspname = 'contract';
-- Expected: 5
```

Both probes are read-only and run pre-apply + post-apply.

### 7.3 Write-denial integration test (SAVEPOINT-rolled-back)

A new integration spec (gated on `BCCORE_INTEGRATION_DB=1`) attempts INSERT/UPDATE/DELETE against each of the 4 contract.* BCF evidence tables inside a SAVEPOINT-rolled-back transaction. Each attempt must RAISE EXCEPTION (deny-write trigger fires). Pre/post row counts verified Δ=0.

### 7.4 Post-freeze row-count invariants

`bcf-evidence-schema-phase-a4-post-apply.mjs` (new) captures:

| # | Probe | Expected |
|---|---|---|
| 1 | `bcf.*` row counts unchanged | 19 / 0 / 19 / 3530 |
| 2 | `contract.*` row counts unchanged | 19 / 0 / 19 / 3530 |
| 3 | `mcf.certification_record` unchanged | 0 |
| 4 | 4 contract deny-write triggers present | per table |
| 5 | (per D5 C2 selection) contract.cert existing trigger + function ABSENT | 0 / 0 |
| 6 | bcf.cert write-once trigger STILL PRESENT (unchanged by A4) | 1 / 2 rows |
| 7 | No cross-schema FK from bcf.* added | 0 |
| 8 | 9 inbound FKs to contract.panel_output_record unchanged | 9 |
| 9 | 5 cross-schema mcf→contract FKs unchanged | 5 |
| 10 | Static lockfile passes (extended with A4 assertions) | PASS |

### 7.5 BCF writer path remains active (smoke test)

Post-freeze, a SAVEPOINT-rolled-back smoke test exercises the W1..W5 + R1..R8 path against bcf.* and confirms no contract.* write attempts occur. This is the same SAVEPOINT pattern used by the existing 4 integration specs.

### 7.6 No MCF FK changes

A pre-apply + post-apply assertion verifies `pg_constraint` shows zero changes to mcf-related FKs. A5 will modify these; A4 must not.

## 8. Rollback plan

### 8.1 A4 rollback envelope

`scripts/bcf-evidence-schema-phase-a4-rollback.mjs --mode=pre-rollback` (new) checks:

| Guard | Description |
|---|---|
| #1 `a4_rollback_phase_a5_not_shipped` | Verify A5 has NOT shipped. Post-A5, the 5 mcf→contract FKs are retargeted to bcf.panel_output_record; an A4 rollback (which restores contract.* writability) cannot un-retarget those FKs without additional A5 rollback. **Mark this guard FAIL if A5 has shipped — operator decides whether to manually un-retarget mcf FKs first or accept the split state** |
| #2 `a4_rollback_contract_rows_intact` | Verify contract.* row counts unchanged (19/0/19/3530); if a rogue write made it through pre-freeze (impossible given lockfile + bcf.cert trigger but a guard for paranoid evidence) |
| #3 `a4_rollback_bcf_rows_present` | Verify bcf.* row counts (19/0/19/3530); rollback does NOT delete bcf rows |
| #4 `a4_rollback_env_gate_present` | Env-gate `BCCORE_BCF_PHASE_A4_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_<ts>` |
| #5 `a4_rollback_bcf_cert_trigger_unchanged` | Verify bcf.cert write-once trigger still LIVE (A4 didn't touch it) |

### 8.2 A4 rollback action (operator-driven)

Under F1/F4 + C2:

1. `DROP TRIGGER IF EXISTS trg_contract_panel_output_record_deny_write ON contract.panel_output_record;`
2. `DROP TRIGGER IF EXISTS trg_contract_authoring_panel_rejection_log_deny_write ON contract.authoring_panel_rejection_log;`
3. `DROP TRIGGER IF EXISTS trg_contract_calibration_event_deny_write ON contract.calibration_event;`
4. `DROP TRIGGER IF EXISTS trg_contract_certification_record_deny_write ON contract.certification_record;`
5. `DROP FUNCTION IF EXISTS contract.tg_panel_output_record_deny_write();`
6. `DROP FUNCTION IF EXISTS contract.tg_authoring_panel_rejection_log_deny_write();`
7. `DROP FUNCTION IF EXISTS contract.tg_calibration_event_deny_write();`
8. `DROP FUNCTION IF EXISTS contract.tg_certification_record_deny_write();`
9. (per D5 C2 selection) Re-create the original contract.cert born-null/write-once trigger + function by re-applying the source DDL from `docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:188-226`

### 8.3 Post-rollback assertions

`scripts/bcf-evidence-schema-phase-a4-rollback.mjs --mode=post-rollback`:

| # | Assertion | Expected |
|---|---|---|
| 1 | 4 contract deny-write triggers absent | 0 each |
| 2 | 4 contract deny-write functions absent | 0 each |
| 3 | (per D5 C2 selection) contract.cert original trigger + function restored | 1 / 1 |
| 4 | contract.* row counts unchanged (19/0/19/3530) | preserved |
| 5 | bcf.* row counts unchanged (19/0/19/3530) | preserved |
| 6 | bcf.cert write-once trigger STILL PRESENT (unaffected by A4 rollback) | 1 / 2 rows |
| 7 | No mcf.* FK changes | unchanged |
| 8 | Cross-schema FK from bcf.* still = 0 | 0 |

### 8.4 Combined Phase A3 + step 20 rollback envelope IS NO LONGER VALID post-A4-apply

This is the central rollback policy change: once A4 ships, writes can no longer route back to contract.* (the deny-write triggers fire). The combined Phase A3 + step 20 rollback (`bcf-evidence-schema-phase-a3-rollback.mjs --mode=*-combined`) refused under guard #1 (`a3_step_20_rollback_phase_a4_not_shipped`) as soon as A4 ships. **Operator must perform A4 rollback FIRST if a combined Phase A3 + step 20 rollback becomes necessary post-A4.**

### 8.5 Row preservation

A4 rollback does NOT delete rows. bcf.* and contract.* rows are preserved across A4 rollback. The 9 inbound FKs are unchanged. mcf FKs are unchanged.

## 9. Relationship to Phase A5

### 9.1 A5 scope (out of A4 scope)

Phase A5 owns:
- Retarget the 5 cross-schema mcf→contract FKs (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`) to reference `bcf.panel_output_record` instead of `contract.panel_output_record`.
- M12 writer flip (the first real MCF authority writer that writes to `mcf.panel_output_record` / equivalent).
- M14 unblock decision (if A5 design clears the path).

### 9.2 A4 must not touch A5 scope

- A4 must not modify the 5 mcf→contract FKs.
- A4 must not modify mcf.* table structure, triggers, or functions.
- A4 must not invoke M11 / M12 / M12.5 / M13 / M14.

### 9.3 Post-A4 → A5 handoff

After A4 ships:
- contract.* BCF evidence tables are FROZEN (deny-write triggers fire on any DML).
- contract.* rows preserved (read-only historical archive).
- bcf.cert write-once trigger LIVE.
- bcf.* writers/readers fully operational.
- A5 DBCP authoring is the next operator-authorized governance gate.

### 9.4 First real M12 panel run remains gated

The first real M12 panel run (M-series gate) remains blocked until A5 (or whichever phase the boundary DBCP assigns) ships. A4 does not unblock M12.

## 10. Risk register

| # | Risk | Mitigation |
|---|---|---|
| **R1** | **Hidden contract.* writer not caught by step 20 lockfile** — a code path that writes to contract.* BCF evidence (e.g., a script, a migration, a one-off cleanup, a developer terminal session) hits the deny-write trigger and raises | Pre-apply read-only inventory grep (§5.2 + §5.3). Post-apply integration smoke (§7.5) exercises the W1..W5 + R1..R8 path. The deny-write trigger's RAISE message includes a clear pointer to the A4 ship event so the caller can diagnose |
| **R2** | **Cross-schema FK violation when contract.panel_output_record is FROZEN** — INSERT into mcf.cert (or any of the 5 mcf→contract FK-bearing tables) would normally need a parent row in contract.panel_output_record; if mcf is writing post-M12 unblock, the FK lookup still resolves because FROZEN preserves rows | A4 selects FREEZE (not DROP); rows preserved; FK lookups continue to resolve. M12 remains gated until A5. R10 cluster separation invariant unchanged |
| **R3** | **PR #133 restore script breaks** — `bcf-authoring-test-row-cleanup-restore.mjs` references pre-A2 row counts and would re-INSERT into contract.* tables; A4 freeze rejects these inserts | Operator decision D6 covers retirement. If D6 = retire, the script is deleted in the implementation PR. If D6 = preserve as historical, document that it cannot run post-A4 |
| **R4** | **Premature DROP** — operator selects F2 (RETIRE-DROP) pre-A5 | F2 explicitly NOT recommended for pre-A5 (§4.5). DROP of contract.panel_output_record blocks on 5 mcf FKs anyway. Apply gate refuses if the operator attempts F2 disposition pre-A5 |
| **R5** | **Accidental DML against contract.* rows pre-freeze** — between A3 + step 20 ship and A4 apply, a stray write could mutate contract.* row counts; A4 pre-apply baseline check (#207 in PR #147 post-apply) verified `surplus=0` at apply-ts but the window remains open until A4 freeze | Pre-apply guard verifies contract.* row counts match baseline (19/0/19/3530); A4 apply refuses if drift detected |
| **R6** | **Rollback ambiguity after freeze** — combined Phase A3 + step 20 rollback no longer valid post-A4 (per §8.4); operator may mis-sequence rollback | A4 rollback guards document the constraint explicitly; rollback verifier output names the required sequence; operator stance ADR DEC-7f9597 / D423 reinforces operator-authorized gate discipline |
| **R7** | **Cross-schema FK regression** — A4 implementation PR inadvertently adds a bcf→contract or contract→bcf FK | A4 DDL is function + trigger only (§6.4); no FK statements. Post-apply assertion #7 verifies cross-schema FK from bcf.* = 0 |
| **R8** | **Trigger function namespace collision** — a function name like `contract.tg_panel_output_record_deny_write` could collide with a future migration | Use distinct namespace-qualified naming (`contract.tg_<table>_deny_write`); A4 DDL synthesis module is the single source of truth; lockfile asserts the names |
| **R9** | **MCF M-series accidentally invoked** — A4 implementation PR's scripts inadvertently call mcf-m* scripts | A4 implementation PR's scripts MUST NOT import or invoke mcf-m* scripts. Lockfile + CI grep can detect this |
| **R10** | **HR4 violation — tenant DB connection** — A4 apply script accidentally opens tenant DB | Mirror Phase A1/A2/A3/step20 pattern: `TENANT_DATABASE_URL=` cleared at invocation; HR4 substrate-enforced |

## 11. Hard rule mapping (HR1..HR5)

| Rule | A4 coverage |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | A4 deny-write triggers protect contract.* from any future writes including synthetic ones. bcf.* substrate CHECKs + bcf.cert write-once trigger continue to enforce HR1 on the live writer path |
| **HR2** — MCF evidence belongs in `mcf.*` | A4 does not touch mcf.*. The 5 cross-schema mcf→contract FKs remain in place (A5 scope) |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.*` | A4 deny-write triggers reject ANY DML to contract.* BCF evidence tables, including hypothetical MCF authority leakage. HR3 substance now structurally enforced at substrate level |
| **HR4** — tenant result DBs separate | A4 apply script mirrors Phase A1/A2/A3/step20 pattern with TENANT_DATABASE_URL guard; tenant DB connection count post-apply = 0 |
| **HR5** — production path; no mocks | A4 deny-write triggers apply to the live contract.* substrate. Mocks remain confined to unit + SAVEPOINT-rolled-back integration tests |
| **Stance ADR DEC-7f9597 / D423** | Schema-boundary clarity reinforced via freeze (contract.* permanently non-writable). Rollback discipline preserved via A4 rollback envelope. Operator authorization for mutating gates: A4 apply is SEPARATE operator authorization |

## 12. Sequencing + anchor set

Under the merged Option A boundary DBCP, A4 slots in immediately after the merged Phase A3 + step 20 atomic-pair ship + closeout:

1. ~~Boundary DBCP merged~~ — bc-docs-v3 main `6f8cc15` (PR #11).
2. ~~Phase A1 substrate-design + apply DBCPs merged~~ — bc-docs-v3 main `70beeb7` + `cdc6efa`.
3. ~~Phase A1 substrate applied~~ — bc_platform_dev (2026-05-29T02-11-41-745Z).
4. ~~Phase A2 migration DBCP + apply~~ — 3,568 authority rows migrated.
5. ~~Phase A3 cutover DBCP (PR #15) merged~~ — bc-docs-v3 main `d06eeba`.
6. ~~Phase A3 implementation chain (PR #141 + #142 + #143 + #144)~~ — bc-core main `68cee3f`.
7. ~~Phase A3 DBCP correction (PR #16; D11(δ) lock) merged~~ — bc-docs-v3 main `21aa442`.
8. ~~§14 step 20 DBCP (PR #17) merged~~ — bc-docs-v3 main `b0bd475`.
9. ~~Step 20 implementation (PR #145) merged~~ — bc-core main `9cb3ce0`.
10. ~~Step 20 dry-run + sha256 pin (PR #146) merged~~ — bc-core main `45da6e1`.
11. ~~Combined Phase A3 + §14 step 20 apply executed~~ — apply-ts `2026-05-29T09-24-54-689Z`.
12. ~~Combined apply + post-apply evidence (PR #147) merged~~ — bc-core main `781660b`.
13. ~~Phase A3 + §14 step 20 closeout (PR #18) merged~~ — bc-docs-v3 main `5757936`.
14. **This DBCP (Phase A4 design)** — operator reviews §10 R1..R10 + §13 D1..D10.
15. **Operator authorization of D1..D10** in writing.
16. **bc-core PR — A4 implementation** — authored separately; opens with the freeze DDL + apply/rollback scripts + lockfile extension + post-apply evidence script + (per D6) PR #133 restore script retirement; merged after independent review.
17. **A4 dry-run execution** — operator-authorized; sha256 pin emitted.
18. **A4 apply gate execution** — operator-authorized; ships freeze DDL atomically; captures post-apply evidence.
19. **A4 closeout doc** — `bcf-evidence-schema-phase-a4-closeout.md` on bc-docs-v3; records freeze ship event + records that combined Phase A3 + step 20 rollback envelope is no longer valid.
20. **Phase A5 DBCP + apply** — `mcf.*` FK retarget; M12 writer flip; M14 unblock decision.
21. **M-series gates** — separately authored.

This DBCP authorizes step 16 (A4 implementation PR authoring). Steps 17..19 each require their own operator instruction.

## 13. Operator decisions

| # | Decision | Recommended | Options |
|---|---|---|---|
| **D1** | **Disposition strategy — F1 / F2 / F3 / F4** | **F4 HYBRID** (F1 freeze surface now; explicit post-A5 DROP plan documented) | F1 freeze-all / F2 retire-drop-all (NOT recommended pre-A5) / F3 read-only-archive (REVOKE; not recommended) / F4 hybrid (recommended) |
| **D2** | Authorize **bc-core A4 implementation PR authoring** (not execution) | **YES** | YES (implementation PR can be authored; merge gate is SEPARATE operator authorization) / NO (re-scope) |
| **D3** | Confirm **no A5 work in A4** | **YES** | YES (A5 owns mcf FK retarget) / NO (re-scope) |
| **D4** | Confirm **no tenant DB work** | **YES** | YES (HR4 substrate-enforced) / NO (re-scope) |
| **D5** | **contract.cert existing trigger disposition — C1 / C2 / C3** | **C2 REPLACE** (DROP existing born-null/write-once trigger + function; deny-write trigger only) | C1 COEXIST / C2 REPLACE / C3 MIXED (drop trigger, keep function) |
| **D6** | **PR #133 restore script (`bcf-authoring-test-row-cleanup-restore.mjs`) retirement** | **RETIRE** (delete in A4 implementation PR; PR #133 cleanup is closed) | RETIRE / PRESERVE (document inapplicable post-A4) |
| **D7** | **Test-fixture hygiene for `bcf-b8-calibration-event-ingest.spec.ts`** (the residual contract-side calibrationEvent import per §5.2) | **FLIP** (include in A4 implementation PR's hygiene commit) | FLIP / DEFER (separate hygiene PR) |
| **D8** | Confirm **M14 remains CLOSED** | **YES** | YES (M14 stays CLOSED throughout A4) / NO (re-scope) |
| **D9** | Confirm **the combined Phase A3 + §14 step 20 rollback envelope becomes invalid post-A4-apply** and operator accepts this rollback policy change | **YES** | YES (A4 owns its own rollback plan; pre-A4 combined rollback envelope is no longer valid post-A4-apply) / NO (re-scope — would require unwinding A4) |
| **D10** | **Statement count under chosen D1+D5** | follows D1 + D5 | F4 + C2 → 14 statements; F4 + C1 → 12 statements; F1 + C2 → 14; F1 + C1 → 12 |

## 14. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 |
| No DDL applied | ✓ — DDL designed only |
| No DML applied | ✓ |
| No Phase A4 apply executed | ✓ — gated on D1..D10 + future operator authorization |
| No Phase A3 + step 20 rollback executed | ✓ — that envelope remains intact pre-A4-apply |
| No A5 work started | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No `bcf.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No tenant `tbc_{slug}_dev` DB connection | ✓ |
| No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 re-touch | ✓ |
| No PR #15 / #16 / #17 / #18 re-touch | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured | ✓ |
| `bc-postgres` MCP `allow_write` used read-only only (FK inventory + trigger inventory + row counts) | ✓ |
| Inventory grep of `bc-core/src/` + `bc-core/scripts/` + `bc-core/docker/redesign/migrations/` for contract.* BCF evidence references performed read-only at A4-DBCP-authoring time | ✓ |

## 15. Out-of-scope re-statement

This DBCP is **NOT** Phase A5 / M-series.

This DBCP does **NOT** authorize bc-core code execution. Authoring the A4 implementation PR is a separately operator-authorized follow-up (step 16 of §12).

This DBCP does **NOT** authorize merging the A4 implementation PR.

This DBCP does **NOT** authorize any `contract.*` row deletion. The freeze preserves rows; only post-A5 DROP (out of A4 scope) deletes them.

This DBCP does **NOT** authorize MCF FK changes. A5 owns retarget.

This DBCP does **NOT** authorize `concept_registry.*` changes.

This DBCP does **NOT** authorize `mcf.*` writes.

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** open M14.

This DBCP does **NOT** unblock the first real M12 panel run.

This DBCP does **NOT** modify bcf.* (writer path or trigger or substrate).

---

**End of DBCP. NOT EXECUTED. Operator authorization on §13 D1..D10 required before the bc-core A4 implementation PR authoring opens.**
