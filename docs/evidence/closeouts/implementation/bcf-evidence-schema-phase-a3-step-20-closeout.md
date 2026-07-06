---
uid: bcf-evidence-schema-phase-a3-step-20-closeout
title: BCF Evidence Schema — Phase A3 + §14 step 20 combined-apply closeout
description: Closeout record for the completed Phase A3 + §14 step 20 atomic-pair ship event per D11(δ) δ.1 (single combined deploy/apply). Anchors the merged governance artifacts (PR #15/#16/#17), the merged bc-core implementation + dry-run + apply evidence (PR #145/#146/#147), the substrate final state (bcf.cert write-once trigger LIVE; contract.cert trigger preserved), and the final R4/R5/R6 treatment (F3a/F6α joint-defer set fully flipped to bcf). Records that the W1→W4b cross-schema FK violation exposed by bc-core PR #144 is closed (the bcf.cert FK chain resolves entirely within the bcf cluster). **NOT EXECUTED.** This is a docs-only closeout; the substrate apply already happened at apply-ts `2026-05-29T09-24-54-689Z`. **No DDL applied, no DML applied, no tenant DB connection, no M-series invocation. M14 stays CLOSED. A4 not started.**
status: implemented
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a3-step-20-closeout
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A3 + §14 step 20 combined-apply closeout

## 1. Scope

### 1.1 Question this doc answers

> The combined Phase A3 + §14 step 20 apply per D11(δ) δ.1 (single combined deploy/apply) was executed at apply-ts `2026-05-29T09-24-54-689Z`. What is the final ship record — substrate state, code routing, evidence anchor chain, failure-mode closure, scope discipline, rollback status, and next-gate handoff?

### 1.2 In scope

- **Ship record** — what landed at substrate + code + governance layers under the atomic-pair apply.
- **Final F3a/F6α joint-defer set treatment** — R4 cert-read, R5 verify-by-id, R6 Registry-shape filter all flipped to bcf; no continued contract-side reads on the BCF cert evidence paths.
- **Evidence anchor chain** — governance + code + dry-run + apply + post-apply, byte-pinned by sha256 across the combined-apply gate.
- **Substrate final state** — bcf.cert write-once trigger LIVE; contract.cert trigger preserved; row counts unchanged; cross-schema FK invariant intact.
- **Failure-mode closure** — the W1→W4b cross-schema FK violation that bc-core PR #144 exposed under standalone A3 apply is closed.
- **Scope discipline assertions** — no row mutation; no tenant DB; no M-series invocation; M14 CLOSED; no A4/A5 work.
- **Rollback status** — rollback NOT executed; combined envelope available pre-A4.
- **Next-gate handoff** — Phase A4 DBCP authoring as separate operator-authorized governance gate.

### 1.3 Explicit non-scope

- ❌ **No DDL applied by this closeout.** The trigger DDL was applied by `scripts/bcf-evidence-schema-phase-a3-step-20-apply.mjs` under a separately operator-authorized gate at apply-ts `2026-05-29T09-24-54-689Z`. This closeout doc records that event; it does not re-apply it.
- ❌ **No DML applied.** No row mutation on `bcf.*` / `contract.*` / `mcf.*` / `concept_registry.*` / any tenant DB.
- ❌ **No bc-core code change.** The closeout is bc-docs-v3 docs-only.
- ❌ **No further bc-core PR.** PR #145 / #146 / #147 are merged; no follow-up bc-core PR is opened by this closeout.
- ❌ **No `contract.*` row deletion.** Phase A4 owns freeze/retire.
- ❌ **No `mcf.*` / `metric.*` / `concept_registry.*` touch.**
- ❌ **No `mcf.*` FK retarget.** Phase A5 owns.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** HR4 substrate-enforced.
- ❌ **No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 re-touch.**
- ❌ **No PR #15 / #16 / #17 re-touch.**
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M14 remains CLOSED.
- ❌ **Phase A4 / A5 NOT started.** Phase A4 DBCP authoring is a separate operator-authorized governance gate.
- ❌ **No rollback executed.** Combined rollback envelope remains available pre-A4 if operator authorization arrives.
- ❌ **No bc-admin / bc-portal UI changes.** No HTTP API contract changes.

## 2. Authority anchor chain

| Layer | Artifact | SHA |
|---|---|---|
| Governance — boundary | Boundary DBCP (Option A) | bc-docs-v3 main `6f8cc15` |
| Governance — Phase A1 | A1 substrate-design DBCP | bc-docs-v3 main `70beeb7` |
| Governance — Phase A1 apply | A1 apply DBCP | bc-docs-v3 main `cdc6efa` |
| Governance — Phase A2 | A2 migration DBCP | bc-docs-v3 main `36acb27` |
| Governance — Phase A3 original | A3 cutover DBCP (PR #15) | bc-docs-v3 main `d06eeba` |
| Governance — Phase A3 correction | A3 correction DBCP (PR #16; D11(δ) locked) | bc-docs-v3 main `21aa442` |
| Governance — Step 20 design | Step 20 DBCP (PR #17) | bc-docs-v3 main `b0bd475` |
| Code — Phase A1 substrate | bcf.* schema + 28 CHECKs + 16 indexes + 3 intra-bcf FKs | bc-core main (Phase A1 apply, 2026-05-29T02-11-41-745Z) |
| Code — Phase A2 migration | 3,568 authority rows from contract.* → bcf.* | bc-core main (Phase A2 apply) |
| Code — Phase A3 implementation | W1..W4a + R1..R8 (minus F6α joint-defer subset) cutover | bc-core main `5f7f8fe` (PR #141) |
| Code — Phase A3 spec hygiene | panel fixtures flipped to bcf in 3 integration specs | bc-core main `e0bdbc6` (PR #142) |
| Code — Phase A3 apply/rollback scripts | dry-run + post-apply + rollback verifier | bc-core main `0a34817` (PR #143) |
| Code — Phase A3 harness repair + FK finding | framework-approval.test-harness factory; uncovered W1→W4b FK violation | bc-core main `68cee3f` (PR #144) |
| Code — Step 20 implementation | bcf.cert trigger DDL synth + W4b/W5/R6/R5/R4-cert flips + verifier extensions | bc-core main `9cb3ce0` (PR #145) |
| Evidence — Step 20 dry-run | sha256 pin + 6/6 read-only probes | bc-core main `45da6e1` (PR #146) |
| Evidence — Combined apply + post-apply | 8/8 apply assertions + 20/20 post-apply assertions; bcf.cert trigger LIVE | bc-core main `781660b` (PR #147) |
| Stance ADR | DEC-7f9597 / D423 | bc-docs-v3 `docs/adrs/ADR-7f9597.md` |
| Stance D11(δ) lock | Phase A3 correction §12 D11(δ) | bc-docs-v3 main `21aa442` |

## 3. What shipped

### 3.1 The atomic-pair under D11(δ) δ.1

The merged Phase A3 DBCP correction (PR #16, `21aa442`) §12 D11(δ) locked the apply model: **standalone Phase A3 apply is FORBIDDEN; A3 must apply atomically with §14 step 20.** The operator selected (δ.1) single combined deploy/apply (RECOMMENDED).

The atomic-pair ship event landed at `bc_platform_dev` apply-ts `2026-05-29T09-24-54-689Z` as a single coherent operational gate:

| Slice | Deliverable | Landing |
|---|---|---|
| **Phase A3 code routing** | W1..W3 + W4a writer flip + R1..R3 + R4-panel + R7 + R8-panel reader flip (per PR #141) | bc-core main (already armed since `5f7f8fe`); ship event activated |
| **Step 20 DDL** | `bcf.tg_certification_record_target_registry_id_guard()` function + `trg_certification_record_target_registry_id_guard` trigger on `bcf.certification_record` BEFORE INSERT OR UPDATE | applied by `scripts/bcf-evidence-schema-phase-a3-step-20-apply.mjs` in single transaction; sha256-pinned `13502ba12aa0e5db1f1dd4531d21ba426b8d8d98fd0b521601803532057ce223` |
| **Step 20 code routing** | W4b `writeRegistryShapeRow()` + W5 `stampTargetRegistryId()` + R6 `registry-publication.service.ts` + R5 `certification-verifier.service.ts` + R4-cert `findRegistryCert()` all flipped to bcf | bc-core main (armed since `9cb3ce0`); ship event activated |
| **Combined post-apply evidence** | 20/20 assertions PASS via `--include-step-20`; lockfile 16/16 PASS | captured at post-apply-ts `2026-05-29T09-25-03-144Z` |
| **Evidence governance anchor** | apply + post-apply artifacts committed | bc-core main `781660b` (PR #147) |

### 3.2 bcf.cert write-once trigger now LIVE

The bcf-side trigger function + trigger declaration mirror the contract-side trigger byte-for-byte with namespace substitution only:

| Element | Source mirror | bcf-side |
|---|---|---|
| Function name | `contract.tg_certification_record_target_registry_id_guard()` | `bcf.tg_certification_record_target_registry_id_guard()` |
| INSERT branch | rejects Registry-shape rows born with non-null `target_registry_id` | identical |
| UPDATE write-once branch | rejects if `OLD.target_registry_id IS NOT NULL` | identical |
| UPDATE append-only branch | rejects if any column other than `target_registry_id` changed (via `(to_jsonb(NEW) - 'target_registry_id') IS DISTINCT FROM (to_jsonb(OLD) - 'target_registry_id')`) | identical |
| Trigger name | `trg_certification_record_target_registry_id_guard` (table-scoped in PostgreSQL; no collision with contract-side) | identical name; bound to different table |
| Trigger declaration | `BEFORE INSERT OR UPDATE ON contract.certification_record FOR EACH ROW` | `BEFORE INSERT OR UPDATE ON bcf.certification_record FOR EACH ROW` |
| Language | `plpgsql` | `plpgsql` |

Authoritative source: `bc-core/docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:188-226`. The bcf-side DDL is in `bc-core/scripts/bcf-evidence-schema-phase-a3-step-20-ddl.mjs` (PR #145).

### 3.3 F3a / F6α joint-defer set fully relocated

The 5-cell joint-defer set (W4b + W5 + R6 + R5 + R4-cert) — identified in the Phase A3 DBCP §5.2 (F3a) and tightened in the F6α review pass — is now fully flipped to bcf:

| Cell | File | Pre-step-20 | Post-step-20 |
|---|---|---|---|
| **W4b** | `src/registry/framework-approval/repositories/certification-record.write.repository.ts` (`writeRegistryShapeRow()`) | `contract.certification_record` (DEFERRED per F3a / D11(a)) | **`bcf.certification_record`** (W4a+W4b dual-alias pattern collapsed to single bcf import) |
| **W5** | `src/registry/concept-registry/repositories/certification-stamp.repository.ts` (`stampTargetRegistryId()`) | `contract.certification_record` (DEFERRED per F3a) | **`bcf.certification_record`** |
| **R6** | `src/registry/registry-authoring-panel/registry-publication.service.ts` (`governanceScope='registry'` filter) | `contract.certification_record` (DEFERRED per F6α UNCONDITIONAL) | **`bcf.certification_record`** (UNCONDITIONAL flip) |
| **R5** | `src/registry/concept-registry/certification-verifier.service.ts` (`verify` by `certificationRecordId`) | `contract.certification_record` (DEFERRED per F6α LIKELY) | **`bcf.certification_record`** (default flip; **no exemption** taken — cutover-implementation inventory found none required) |
| **R4-cert** | `src/registry/registry-authoring-panel/registry-provenance.read-repository.ts` (`findRegistryCert()` Registry-shape cert read) | `contract.certification_record` (DEFERRED per F6α per-shape) | **`bcf.certification_record`** (per-shape evaluation found no shape-split requirement; both panel + cert reads land on bcf) |

The `R8` SPLIT in `src/registry/intake-queue.repository.ts` is preserved as designed: `intakeQueue` lives on `contract.*` (it is NOT a BCF cert), only the panel side was flipped to bcf in Phase A3.

The post-step-20 documented-exception list size for BCF cert evidence paths is **exactly 0** — enforced by the import lockfile's global grep assertion in `scripts/bcf-phase-a3-import-lockfile.mjs`.

## 4. Final R4 / R5 / R6 treatment

### 4.1 R4 cert-read — flipped to bcf (per-shape evaluation)

**Decision:** R4 `findRegistryCert()` in `registry-provenance.read-repository.ts` flipped to `bcf.certification_record`. The per-shape evaluation called for in Step 20 DBCP §4.2 R4-cert cell + §10 D7 found **no shape-split requirement**:

- Registry-shape certs are born on bcf.cert post-W4b flip (W4b is the only writer for `governance_scope='registry'` rows).
- Legacy-shape certs live on bcf.cert post-A2 migration (the 3,530 historical authority rows + post-A3 W4a inserts).

Both shapes resolve from bcf.cert; no continued dual-shape contract-side reads are required. The R4 import now reads `certificationRecord, panelOutputRecord` from a single bcf-side import (panel + cert both on bcf).

### 4.2 R5 — flipped to bcf (default; no exemption used)

**Decision:** R5 `verify` by `certificationRecordId` in `certification-verifier.service.ts` flipped to `bcf.certification_record`. The cutover-implementation inventory called for in Step 20 DBCP §4.2 R5 cell + §10 D7 found **no exemption requirement**:

- The verifier resolves Registry-shape cert IDs that are now born on bcf.cert via the flipped W4b.
- Legacy `submit_for_review` certs already live on bcf.cert via Phase A2 migration.

R5 reads bcf.cert in all cases. The exemption mechanism (allowed under the DBCP for narrowly justified continued contract-side reads) is **not used**.

### 4.3 R6 — flipped to bcf (UNCONDITIONAL)

**Decision:** R6 `governanceScope='registry'` filter in `registry-publication.service.ts` flipped to `bcf.certification_record` UNCONDITIONALLY. This matches the W4b writer flip — Registry-shape certs written by W4b land on bcf.cert, so the corresponding reader must follow unconditionally to avoid split-brain.

## 5. Evidence anchors

| Anchor | SHA / timestamp | Scope |
|---|---|---|
| **PR #145** — Step 20 implementation | bc-core main `9cb3ce0` | DDL synthesis module + dry-run/apply/post-apply/rollback verifier extensions + W4b/W5/R6/R5/R4-cert code flips + new SAVEPOINT-rolled-back trigger behavior integration spec + 4 test-fixture flips |
| **PR #146** — Dry-run + sha256 pin | bc-core main `45da6e1` | Dry-run timestamp `2026-05-29T09-09-03-957Z`; 4 artifacts including planned-ddl.sql + sha256.txt + evidence.jsonl + summary.md; 6/6 pre-apply probes PASS |
| **PR #147** — Combined apply + post-apply | bc-core main `781660b` | Apply timestamp `2026-05-29T09-24-54-689Z`; post-apply timestamp `2026-05-29T09-25-03-144Z`; 5 artifacts (precondition + apply evidence + apply summary + post-apply evidence + post-apply summary); 8/8 apply assertions PASS; 20/20 post-apply assertions PASS; lockfile 16/16 PASS |
| **PR #17** — Step 20 DBCP | bc-docs-v3 main `b0bd475` | Governance authority for the step 20 design (DDL design + code-routing flip set + atomic-pair apply model + test/evidence plan + combined rollback plan + risk register R1..R10 + operator decisions D1..D7) |
| **PR #16** — Phase A3 DBCP correction | bc-docs-v3 main `21aa442` | D11(δ) lock; standalone Phase A3 apply FORBIDDEN |
| **PR #15** — Phase A3 original DBCP | bc-docs-v3 main `d06eeba` | F3a / F6α joint-defer set definition; pre-correction baseline |
| **Apply sha256 pin** | `13502ba12aa0e5db1f1dd4531d21ba426b8d8d98fd0b521601803532057ce223` | Byte-equivalence between dry-run and apply gates; verified before DDL execution |
| **Substrate apply** | `bc_platform_dev` apply-ts `2026-05-29T09-24-54-689Z` | bcf.cert write-once trigger LIVE; 3-statement DDL in single transaction |

## 6. Substrate final state

Verified post-apply via `bc-postgres` MCP read-only queries (captured by PR #147's evidence + independently re-verified at closeout-authoring time):

### 6.1 Trigger / function inventory

| Schema | Object | Status | Notes |
|---|---|---|---|
| `bcf` | `tg_certification_record_target_registry_id_guard` function | **PRESENT (1)** | LIVE since apply-ts `2026-05-29T09-24-54-689Z` |
| `bcf` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for INSERT | **PRESENT** | BEFORE FOR EACH ROW |
| `bcf` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for UPDATE | **PRESENT** | BEFORE FOR EACH ROW |
| `contract` | `tg_certification_record_target_registry_id_guard` function | **PRESERVED (1)** | unchanged by step 20 DDL |
| `contract` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for INSERT | **PRESERVED** | BEFORE FOR EACH ROW; pre-A4 |
| `contract` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for UPDATE | **PRESERVED** | BEFORE FOR EACH ROW; pre-A4 |

### 6.2 Row counts (Δ=0 across the combined apply)

| Table | Rows | Δ vs post-A2 baseline |
|---|---|---|
| `bcf.panel_output_record` | **19** | 0 |
| `bcf.authoring_panel_rejection_log` | **0** | 0 |
| `bcf.calibration_event` | **19** | 0 |
| `bcf.certification_record` | **3530** | 0 |
| `contract.panel_output_record` | **19** | 0 |
| `contract.authoring_panel_rejection_log` | **0** | 0 |
| `contract.calibration_event` | **19** | 0 |
| `contract.certification_record` | **3530** | 0 |
| `mcf.certification_record` | **0** | 0 |

The combined apply introduced **only the bcf trigger function + trigger declaration**. Zero row mutations across all monitored tables. The DDL was structurally a CREATE FUNCTION + CREATE TRIGGER pair, not a row-touching operation.

### 6.3 Cross-schema FK invariant (R10)

| Invariant | Value |
|---|---|
| FKs from `bcf.*` → non-`bcf.*` | **0** |

R10 cluster separation invariant intact. The 3 bcf-internal FKs (`fk_bcf_authoring_panel_rejection_log__panel_run`, `fk_bcf_calibration_event__panel_run`, `fk_bcf_certification_record__panel_run`) all target `bcf.panel_output_record`. No bcf→contract / bcf→mcf / bcf→concept_registry FK exists or was introduced.

### 6.4 Lockfile

`node scripts/bcf-phase-a3-import-lockfile.mjs` → **16/16 PASS** post-apply. Documented exception list size for BCF cert evidence paths: **exactly 0**.

## 7. Failure-mode closure

### 7.1 The W1→W4b cross-schema FK violation (closed)

Per the merged Phase A3 DBCP correction §3.5 (which itself reproduces the bc-core PR #144 live integration test discovery), the pre-step-20 standalone Phase A3 apply failure mode was:

| Step | Action | Pre-step-20 substrate landing |
|---|---|---|
| 1 | W1 `PanelOutputRecordRepository.create()` writes a panel row | `bcf.panel_output_record` (Phase A3 cutover) |
| 2 | W4b `CertificationRecordWriteRepository.writeRegistryShapeRow()` writes a Registry-shape cert referencing that `panel_run_uid` | `contract.certification_record` (DEFERRED per F3a / D11(a)) |
| 3 | DB enforces `fk_certification_record__panel_run` (contract.cert.panel_run_uid → contract.panel_output_record.panel_run_uid) | FK lookup in `contract.panel_output_record` |
| 4 | Lookup fails — panel row is in `bcf.panel_output_record`, not `contract.panel_output_record` | **FK violation; W4b INSERT rejected; production regression on every Registry publication** |

### 7.2 Post-combined-apply substrate path

After the combined apply, the W1→W4b chain resolves entirely within the bcf cluster:

| Step | Action | Post-combined-apply substrate landing |
|---|---|---|
| 1 | W1 `PanelOutputRecordRepository.create()` writes a panel row | `bcf.panel_output_record` |
| 2 | W4b `CertificationRecordWriteRepository.writeRegistryShapeRow()` writes a Registry-shape cert referencing that `panel_run_uid` | **`bcf.certification_record`** (post-step-20 flip) |
| 3 | DB enforces `fk_bcf_certification_record__panel_run` (bcf.cert.panel_run_uid → bcf.panel_output_record.panel_run_uid) | FK lookup in `bcf.panel_output_record` |
| 4 | Lookup resolves cleanly within the bcf cluster | **No FK violation. Production regression closed.** |

Additionally, the bcf.cert write-once trigger now enforces the born-null + write-once + append-only invariants on bcf.cert with the same DDL behavior the contract-side trigger had previously enforced on contract.cert. W5 `stampTargetRegistryId()` performs the legitimate NULL → non-NULL one-time stamp; no other UPDATE is permitted.

### 7.3 Cross-schema dependency eliminated

The cross-schema dependency (bcf-side panel → contract-side cert + contract-side trigger) is eliminated entirely. No cross-schema FK was added (per the R10 invariant); instead, both the parent (panel) and the child (Registry-shape cert) writes now land on bcf, restoring writer-side FK integrity within the cluster.

## 8. Scope discipline

| Discipline rule | Status |
|---|---|
| No row mutation introduced by the combined apply | ✓ all 9 row counts Δ=0 vs pre-apply baseline |
| No `contract.*` row deletion | ✓ A4 owns; not touched |
| No `bcf.*` row mutation by the DDL | ✓ DDL is function + trigger declaration only |
| No tenant DB connection | ✓ TENANT_DATABASE_URL guard enforced in apply + post-apply scripts |
| No M-series invocation | ✓ M11 / M12 / M12.5 / M13 not invoked |
| **M14 stays CLOSED** | ✓ |
| No A4 work | ✓ contract.* freeze/retire is a separate operator-authorized gate |
| No A5 work | ✓ mcf FK retarget is a separate operator-authorized gate |
| HR1 — no synthetic / mock / replay / canned data | ✓ bcf substrate CHECKs + new write-once trigger enforce defense-in-depth |
| HR2 — MCF evidence belongs in `mcf.*` | ✓ mcf.* untouched; mcf.certification_record = 0 |
| HR3 — MCF metric authority events do not write to generic `contract.*` | ✓ no MCF authority leakage; BCF authority leakage to contract.* eliminated by W4b flip |
| HR4 — tenant result DBs separate | ✓ no tenant DB connection opened |
| HR5 — production paths; no mocks | ✓ apply + post-apply hit production code paths; mocks confined to unit + SAVEPOINT-rolled-back integration tests |
| DEC-7f9597 / D423 stance ADR | ✓ honoured — operator authorization on mutating gate; rollback discipline preserved; substrate-boundary clarity restored end-to-end |

## 9. Rollback status

### 9.1 Rollback NOT executed

The combined apply succeeded (exit code 0; 8/8 apply assertions PASS; 20/20 post-apply assertions PASS; lockfile 16/16 PASS). Rollback was not executed and not required.

### 9.2 Combined rollback envelope (available pre-A4)

The combined rollback envelope remains available if operator authorization arrives pre-A4:

| Step | Action |
|---|---|
| **Pre-rollback-combined verification** | `BCCORE_BCF_PHASE_A3_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_2026-05-29T09-24-54-689Z node scripts/bcf-evidence-schema-phase-a3-rollback.mjs --mode=pre-rollback-combined` — runs 4 base guards + #320 "A3 cutover code + step 20 DDL both applied or both absent"; expected ALL PASS in current state |
| **Operator-driven rollback action** | (a) `git revert <PR #145 squash sha 9cb3ce0>` on bc-core main to revert W4b/W5/R6/R5/R4-cert code routing AND the rollback verifier extensions; (b) `DROP TRIGGER trg_certification_record_target_registry_id_guard ON bcf.certification_record;` + `DROP FUNCTION bcf.tg_certification_record_target_registry_id_guard();` to revert step 20 DDL |
| **Post-rollback-combined verification** | `BCCORE_BCF_PHASE_A3_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_2026-05-29T09-24-54-689Z node scripts/bcf-evidence-schema-phase-a3-rollback.mjs --mode=post-rollback-combined` — runs 7 base assertions + #330 bcf trigger dropped + #331 bcf function dropped + #332 contract trigger preserved |

**Pre-A4 only.** Once Phase A4 ships a contract.* freeze/REVOKE, the rollback guard #1 (`a3_step_20_rollback_phase_a4_not_shipped`) refuses the rollback because writes can no longer route back to contract.*. Phase A4 DBCP will own its own restore plan.

### 9.3 Row preservation on rollback (informational)

Per the merged Step 20 DBCP §8.5 / §8.6 and the merged Phase A3 correction §9.4: bcf.* rows are PRESERVED across any future combined rollback; contract.* rows are also PRESERVED. The rollback is not row-destructive.

## 10. Next gate

### 10.1 Phase A4 DBCP authoring

The next operator-authorized governance gate is **Phase A4 DBCP authoring** — design for `contract.*` freeze/retire. This is a SEPARATE operator authorization. Phase A4 is not started by this closeout.

Phase A4 scope (per the merged boundary DBCP and the Phase A3 DBCP §14 sequencing) covers, among other things:

- Decision on freeze vs retire for each of the 4 `contract.*` BCF evidence tables (panel_output_record, authoring_panel_rejection_log, calibration_event, certification_record).
- Disposition of the `contract.tg_certification_record_target_registry_id_guard` trigger and function alongside the contract.cert table.
- Rollback boundary: once A4 ships, the combined Phase A3 + step 20 rollback envelope is no longer valid; A4 owns its own restore plan.
- Operational sequencing relative to any continuing Registry publication traffic.

### 10.2 Phase A5 (downstream)

Phase A5 (MCF FK retarget; M12 writer flip) follows Phase A4. Separate operator-authorized governance gate.

### 10.3 M-series (downstream)

M-series gates (M14 in particular) remain CLOSED throughout. M14 is gated on the metric-authoring lifecycle and is not opened by this closeout or any Phase A4/A5 gate.

## 11. Hard rule mapping (HR1..HR5)

| Rule | Closeout-time status |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | bcf substrate CHECKs (Phase A1) + new bcf.cert write-once trigger (step 20 apply) now enforce defense-in-depth. Probe #208 (no synthetic in bcf) PASS; probe #209 (no synthetic in contract) PASS |
| **HR2** — MCF evidence belongs in `mcf.*` | mcf.certification_record = 0; mcf.* untouched; no MCF authority leakage |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.*` | The F3a documented exception (W4b Registry-shape cert writes to contract.cert) is eliminated by the W4b flip. Post-combined-apply, `contract.certification_record` receives ZERO new BCF authority writes. HR3 substance fully achieved (no MCF authority leakage; no BCF authority leakage either) |
| **HR4** — tenant result DBs separate | TENANT_DATABASE_URL guard enforced in apply + post-apply scripts; only DATABASE_URL opened; tenant DB connection count throughout the combined apply = 0 |
| **HR5** — production path; no mocks | Combined apply hits production code path; bcf.cert write-once trigger applies to live bcf.certification_record substrate. Mocks confined to unit + SAVEPOINT-rolled-back integration tests |
| **Stance ADR DEC-7f9597 / D423** | Schema-boundary clarity restored end-to-end via the combined apply. Rollback discipline preserved via combined envelope (§9). Operator authorization for mutating gates: combined apply was operator-authorized at apply-ts `2026-05-29T09-24-54-689Z`. Tenant-results isolation: HR4 substrate-enforced |

## 12. Sequencing record

The complete ship sequence under D11(δ) δ.1:

1. ✓ Boundary DBCP merged — bc-docs-v3 main `6f8cc15`
2. ✓ Phase A1 substrate-design + apply DBCPs merged — bc-docs-v3 main `70beeb7` + `cdc6efa`
3. ✓ Phase A1 substrate applied — bc_platform_dev (2026-05-29T02-11-41-745Z)
4. ✓ Phase A2 migration DBCP merged — bc-docs-v3 main `36acb27`
5. ✓ Phase A2 migration applied — 3,568 authority rows migrated
6. ✓ Phase A3 cutover DBCP (PR #15) merged — bc-docs-v3 main `d06eeba`
7. ✓ Phase A3 implementation (PR #141) merged — bc-core main `5f7f8fe`
8. ✓ Phase A3 spec hygiene (PR #142) merged — bc-core main `e0bdbc6`
9. ✓ Phase A3 apply/rollback scripts (PR #143) merged — bc-core main `0a34817`
10. ✓ Phase A3 SAVEPOINT-safety investigation + harness repair (PR #144) — bc-core main `68cee3f`; **uncovered the W1→W4b FK violation**
11. ✓ Phase A3 DBCP correction (PR #16; D11(δ) lock) merged — bc-docs-v3 main `21aa442`
12. ✓ §14 step 20 DBCP authoring (PR #17) merged — bc-docs-v3 main `b0bd475`
13. ✓ §14 step 20 implementation (PR #145) merged — bc-core main `9cb3ce0`
14. ✓ §14 step 20 dry-run + sha256 pin (PR #146) merged — bc-core main `45da6e1`
15. ✓ **Combined Phase A3 + §14 step 20 apply per D11(δ) δ.1 executed** — apply-ts `2026-05-29T09-24-54-689Z`
16. ✓ Combined post-apply evidence captured — post-apply-ts `2026-05-29T09-25-03-144Z`
17. ✓ Combined apply evidence (PR #147) merged — bc-core main `781660b`
18. ✓ **This closeout doc** — bc-docs-v3
19. ⏸ Phase A4 DBCP authoring — SEPARATE operator-authorized governance gate
20. ⏸ Phase A5 DBCP authoring — SEPARATE operator-authorized governance gate (post-A4)
21. ⏸ M-series gates (M14 in particular) — remain CLOSED

## 13. Discipline assertions (this closeout-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ closeout file lands only in bc-docs-v3 |
| No DDL applied | ✓ closeout is docs-only; DDL was applied in the separately operator-authorized combined-apply gate |
| No DML applied | ✓ |
| No bc-core PR opened by this closeout | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| No `mcf.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No `bcf.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No tenant `tbc_{slug}_dev` DB connection | ✓ |
| No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 re-touch | ✓ |
| No PR #15 / #16 / #17 re-touch | ✓ |
| Phase A4 not started | ✓ |
| Phase A5 not started | ✓ |
| Rollback not executed | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured | ✓ |
| Read-only `bc-postgres` MCP verification for substrate state at closeout-authoring time | ✓ (allow_write=false; read-only) |

## 14. Out-of-scope re-statement

This closeout doc is **NOT** Phase A4 / A5 / M-series.

This closeout doc does **NOT** authorize bc-core code execution.

This closeout doc does **NOT** authorize merging any bc-core PR; PR #145 / #146 / #147 are already merged.

This closeout doc does **NOT** authorize any source `contract.*` row deletion. A4 owns freeze/retire.

This closeout doc does **NOT** authorize any further `bcf.*` row mutation. The combined-apply ship event is COMPLETE; further substrate change requires a separately operator-authorized governance + apply gate.

This closeout doc does **NOT** authorize MCF FK changes. A5 owns retarget.

This closeout doc does **NOT** touch tenant DBs.

This closeout doc does **NOT** alter `mcf.*`, `metric.*`, `concept_registry.*`, or any `contract.*` substrate.

This closeout doc does **NOT** open M14.

This closeout doc does **NOT** initiate the first real M12 panel run.

---

**End of closeout. Phase A3 + §14 step 20 ship event RECORDED. Next operator-authorized gate: Phase A4 DBCP authoring.**
