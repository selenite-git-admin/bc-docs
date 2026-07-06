---
uid: bcf-evidence-schema-phase-a3-writer-reader-cutover-dbcp
title: BCF Evidence Schema — Phase A3 Writer/Reader Cutover DBCP (contract.* → bcf.*; code-routing design; no DDL/DML; no freeze; pre-A4 rollback only)
description: Phase A3 design DBCP for cutting the BCF authoring/cert/calibration writer + reader code paths over from `contract.*` to `bcf.*`. The substrate already exists (Phase A1 applied at bc-core `2026-05-29T02-11-41-745Z`); the rows already exist in both schemas (Phase A2 applied at bc-core `2026-05-29T04-33-48-487Z`; insert-copy preserved `contract.*`). A3's job is the **code-routing flip** — Drizzle schema imports, repository targets, controller surfaces — moving 4 BCF evidence tables' writer/reader access from `contract.panel_output_record` / `contract.authoring_panel_rejection_log` / `contract.calibration_event` / `contract.certification_record` to the bcf.* siblings. **No DDL, no DML, no source-row deletion, no freezing of contract.* tables — Phase A4 owns those.** Writers go first; readers follow in the same or subsequent PR per D3/D4. The duplication of authority rows in `contract.*` and `bcf.*` is operationally tolerated for the A3→A4 window; readers continue to see the same data (rows are byte-identical per A2 byte-equivalence assertion #205) regardless of which schema they read from, which makes the cutover semantically safe. Rollback is restoring writer/reader routing to `contract.*` and is **pre-A4 only** — once A4 freezes/retires `contract.*`, A3 rollback is no longer meaningful (A4 DBCP will own its own restore plan). **NOT EXECUTED.** This DBCP does NOT apply code changes, does NOT migrate rows, does NOT delete `contract.*` rows, does NOT touch `mcf.*` / `metric.*` / `concept_registry.*` / tenant DBs, does NOT execute rollback, does NOT invoke M11/M12/M12.5/M13. M14 remains CLOSED. PR #133 cleanup apply already executed at `2026-05-29T04-06-36-221Z`; this DBCP does not re-touch it. Operator stance ADR DEC-7f9597 / D423 honoured throughout — schema-boundary clarity is the entire point; no synthetic re-introduction through any new writer; rollback discipline preserved.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a3-code-routing
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A3 Writer/Reader Cutover DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> Under the operator-authorized Option A path with Phase A1 substrate live (bcf.* schema + 4 tables + CHECKs + indexes + FKs at bc-core `2026-05-29T02-11-41-745Z`) and Phase A2 row migration complete (3,568 authority-bearing rows live in `bcf.*` at bc-core `2026-05-29T04-33-48-487Z`; original `contract.*` rows preserved), what is the exact writer/reader code-routing design — which production source files cutover, in which order, under which test/evidence gates, with which rollback envelope, and with which downstream-phase boundary preservation — for moving the BCF authoring / cert / calibration code paths from `contract.*` to `bcf.*` without changing DDL, without writing/deleting any row, and without crossing into A4 freeze territory?

### 1.2 In scope

- **Item 1 — Inventory.** Per-table writer + reader census of the 4 BCF evidence tables in bc-core production source (excluding tests, scripts, audit-output).
- **Item 2 — Classification.** Each usage labelled: writer-to-cutover / reader-to-cutover / historical-audit-dual-read / contract-chain-infrastructure-out-of-A3-scope.
- **Item 3 — Cutover strategy.** Writers-first then readers; default target `bcf.*`; no new writes to `contract.*` for BCF evidence post-A3; no deletion or freezing of `contract.*` (A4 owns).
- **Item 4 — Backward-compatibility window.** Duplication of authority rows in `contract.*` and `bcf.*` is tolerated until A4; dual-read / read-fallback policy decided in D5; new BCF authority writes to `contract.*` forbidden post-A3.
- **Item 5 — Test/evidence plan.** Static grep / source inventory (lockfile-style); unit + integration tests; dry-run verification; post-apply DB invariants (no new rows in `contract.*` from BCF writer paths after A3 apply).
- **Item 6 — Rollback plan.** Pre-A4 only; restore writer/reader routing to `contract.*`; do not delete `bcf.*` rows; post-A4 rollback explicitly out of scope.
- **Item 7 — Relationship to downstream phases.** A4 owns freeze/retire of `contract.*`; A5 owns MCF FK retarget + M12 writer flip; A3 must not change MCF FKs; A3 must not open first real M12 panel run; A3 must not open M14.
- **Item 8 — Risk register R1..R12.**
- **Item 9 — Operator decisions D1..D11.**
- Authorization to author a bc-core implementation PR in a follow-up that ships the code changes; that PR's apply gate is a SEPARATE operator authorization.

### 1.3 Explicit non-scope

- ❌ **No code change in bc-core.** This DBCP is a docs-only design artifact; the bc-core implementation PR is a separately operator-authorized follow-up.
- ❌ **No DML apply.** No INSERT / UPDATE / DELETE against `bcf.*`, `contract.*`, `mcf.*`, `metric.*`, `concept_registry.*`, or any tenant DB.
- ❌ **No DDL.** No CREATE / ALTER / DROP. No new triggers, no new CHECKs, no new indexes, no schema changes. (The bcf.* substrate from A1 is reused as-is; if A3 design finds a substrate gap, it is surfaced as a Risk + Decision rather than papered over.)
- ❌ **No `contract.*` row deletion.** A3 is code-routing only; rows in `contract.*` remain untouched (A4 owns freeze/retire).
- ❌ **No `bcf.*` row deletion.** A2 apply put the rows there; A3 does not modify them.
- ❌ **No `mcf.*` FK retarget.** Phase A5 owns the 5 mcf→contract FK redirects.
- ❌ **No `mcf.*` / `metric.*` / `concept_registry.*` write.** A3 reads at most.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** Substrate-enforced via env-var separation.
- ❌ **No PR #133 re-touch.** PR #133 cleanup apply already executed at `2026-05-29T04-06-36-221Z` (PR #138 evidence at `bac8c99`); A3 does not modify, re-run, or restore.
- ❌ **No rollback executed.** This DBCP DESIGNS the pre-A4 rollback envelope; it does not run it.
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M14 remains CLOSED.
- ❌ **No first real M12 panel run.** A3 does not open the M12 writer for the first real run (that is a separate DBCP after A5).
- ❌ **No re-litigation of Option A.** `bcf.*` is the locked target; `concept_registry.*` is BCR vocabulary and remains untouched.
- ❌ **No bc-admin / bc-portal UI changes.** No HTTP API contract changes (controllers retain the same routes; only their internal repository target flips).

## 2. Authority

| Artifact | Location | Authority for |
|---|---|---|
| Boundary DBCP (Option A) | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` | Option A target; 5-phase ladder; §13 sequencing |
| D1-D11 decision record | `docs/implementation/bcf-mcf-evidence-boundary-operator-decisions-d1-d11.md` @ bc-docs-v3 main `70beeb7` | D2=A; D4=Phase A1+A2 design authorization |
| Phase A1 substrate-design DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-dbcp.md` @ bc-docs-v3 main `70beeb7` | `bcf.*` column / CHECK / index / FK shape; HR1 substrate enforcement |
| Phase A1 apply DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-apply-dbcp.md` @ bc-docs-v3 main `cdc6efa` | Apply-gate pattern (env-gate + sha256 + single-tx + post-apply assertions) |
| Phase A2 migration DBCP | `docs/implementation/bcf-evidence-schema-phase-a2-migration-dbcp.md` @ bc-docs-v3 main `36acb27` | Insert-copy semantics; byte-pinned rows; duplication-window justification |
| Phase A1 apply evidence | bc-core main `09035b8` (PR #135) | `bcf.*` substrate live, 4 tables empty (pre-A2) |
| Phase A2 apply evidence | bc-core main `837ce0c` (PR #140) | 3,568 authority rows live in `bcf.*`; `contract.*` preserved; byte-equivalence confirmed |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) @ bc-docs-v3 main `cdc6efa` | Schema-boundary clarity is non-reducible; no-synthetic enforcement preserved across writer flip; rollback discipline preserved |
| Hard rules HR1..HR5 | parent DBCP §5 | Substrate constraints A3 design must respect |
| Live source inventory (this DBCP §4) | `bc-core` main `837ce0c` — Drizzle INSERT/UPDATE/DELETE grep + `from .../database/schema/contract` import grep | Definitive writer/reader census |
| Live DB shape (this DBCP §3) | `bc-postgres` MCP `allow_write=false` probes against `bc_platform_dev` @ 2026-05-29 post-PR-#140-merge | Row-count baselines; no-synthetic post-A2 state |

## 3. Current state (read-only baseline; live-verified)

All counts verified via `bc-postgres` MCP with `allow_write=false`.

### 3.1 Repo + DB anchors

| Anchor | Value |
|---|---|
| bc-core main | `837ce0c7eddf8a1ad78de541b34b7c054acddd3f` (post-PR-#140 merge) |
| bc-docs-v3 main | `36acb27b3d48c4de668647aa1777ef50cc919846` (post-PR-#14 merge) |
| Phase A1 apply timestamp | `2026-05-29T02-11-41-745Z` (verdict APPLY PASS) |
| Phase A2 apply timestamp | `2026-05-29T04-33-48-487Z` (verdict APPLY PASS; 3,568 rows migrated) |
| PR #133 cleanup apply timestamp | `2026-05-29T04-06-36-221Z` (11 smoke rows retired) |

### 3.2 Row counts (`contract.*` and `bcf.*`; post-A2)

| Table | `contract.*` rows | `bcf.*` rows | Duplication? |
|---|---|---|---|
| `panel_output_record` | 19 | 19 | YES — A2 insert-copy preserved both |
| `authoring_panel_rejection_log` | 0 | 0 | NO authority rows on either side |
| `calibration_event` | 19 | 19 | YES — A2 insert-copy preserved both |
| `certification_record` | 3,530 | 3,530 | YES — A2 insert-copy preserved both |
| **Total** | **3,568** | **3,568** | — |

Byte-equivalence between source and target was assertion #205 of A2 apply, verdict PASS (panel + cal + cert all row-for-row identical). A3 cutover semantics rely on this: readers cutover from `contract.*` to `bcf.*` cannot observe different values because the underlying rows are byte-identical.

### 3.3 Synthetic-row enforcement state (HR1 binding)

| Probe | Result | Authority |
|---|---|---|
| `bcf.panel_output_record` synthetic-provider count | 0 | A2 assertion #207 + post-merge re-probe @ PR #140 |
| `bcf.certification_record` synthetic-provider count | 0 | A2 assertion #207 + post-merge re-probe @ PR #140 |
| `contract.panel_output_record` synthetic-provider count | 0 | PR #133 cleanup retired 5 smoke panel rows |
| `contract.certification_record` synthetic-provider count | 0 | PR #133 cleanup retired the 1 synthetic-smoke cert `21023aa1…` |
| `bcf_panel_output_record_no_synthetic_provider_chk` CHECK | PRESENT | A1 substrate |
| `bcf_certification_record_no_synthetic_provider_chk` CHECK | PRESENT | A1 substrate |

The HR1 substrate CHECKs on `bcf.panel_output_record` and `bcf.certification_record` will reject any synthetic-provider row at INSERT — A3 writer cutover does NOT relax this; if the cutover-PR mistakenly routes a synthetic-payload INSERT, the CHECK fires and the writer fails closed.

### 3.4 Substrate parity claim (bcf.* shape matches contract.*)

Phase A1 design DBCP locked column-for-column parity for the 4 BCF evidence tables across `bcf.*` vs `contract.*` (PK, types, NOT NULL, CHECKs, FKs, indexes, COMMENTs). The byte-equivalence assertion #205 in A2 apply confirmed the parity at the data level by copying rows row-for-row without translation.

**Known parity gap (R9 / D11):** The DB trigger `trg_certification_record_target_registry_id_guard` exists on `contract.certification_record` — created by `docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:221-226` as part of Phase A Bucket-1 governance scope-alignment (DEC-02f5a9 / D414) — but was NOT replicated on `bcf.certification_record` by Phase A1 (A1 substrate scope = schema + tables + CHECKs + indexes + FKs + COMMENTs only; `bc-core/scripts/bcf-evidence-schema-phase-a1-ddl.mjs` contains ZERO `CREATE TRIGGER` statements). A3 design originally handled this via the F3a deferral pair (W4b + W5 stay on `contract.cert` until §14 step 20 ships the trigger and flips both paths atomically) — see §4.5 + D11(a). **However, see §3.5 below: bc-core PR #144 live integration testing discovered that the F3a deferral is INSUFFICIENT.** The contract.cert → contract.panel FK breaks because the parent panel writer (W1) cuts over to bcf in A3. Phase A3 apply is BLOCKED until §14 step 20 ships atomically alongside.

### 3.5 PR #144 LIVE INTEGRATION FINDING — F3a as designed is NOT apply-safe (BLOCKING)

**Discovered by:** bc-core PR #144 (integration test harness repair) at HEAD `4cde72eed389fb3af2ff82c6f63722e33f930143` on 2026-05-29.

**Failure mode (reproduced live; see PR #144 evidence):**

When the `registry-authoring.integration.spec.ts` smoke runs against bc_platform_dev with the Phase A3 cutover code active (PR #141 merged + PR #142 spec hygiene + sentinel-rollback isolation envelope), it fails with:

```
Error: insert or update on table "certification_record" violates foreign key constraint
       "fk_certification_record__panel_run"
Detail: Key (panel_run_uid)=(1a91cb08-...) is not present in table "panel_output_record".
```

This replicates the exact production behavior that Phase A3 apply would exhibit on every Registry publication:

| Step | Action | Substrate landing |
|---|---|---|
| 1 | W1 `PanelOutputRecordRepository.create()` writes a new panel row | `bcf.panel_output_record` (cutover per PR #141) |
| 2 | W4b `CertificationRecordWriteRepository.writeRegistryShapeRow()` writes a Registry-shape cert referencing that `panel_run_uid` | `contract.certification_record` (DEFERRED per F3a / D11(a)) |
| 3 | DB enforces `fk_certification_record__panel_run` (contract.cert.panel_run_uid → contract.panel_output_record.panel_run_uid) | FK lookup in `contract.panel_output_record` |
| 4 | Lookup fails — the panel row is in `bcf.panel_output_record`, not `contract.panel_output_record` | **FK violation; W4b INSERT rejected; production regression** |

**Root cause:** The Phase A3 DBCP §12 D11(a) joint-deferral design assumed the contract.cert → contract.panel FK relationship would continue to hold during the A3→step-20 window. It does not. The W1 cutover makes the FK target empty for any new write — the W4b → W5 transactional coupling can't even be reached because W4b itself FK-fails on the first INSERT.

**Implication for apply readiness:**

Phase A3 apply gate (§14 step 18) is **BLOCKED**. Standalone Phase A3 apply would break every Registry publication in production. Either:
- (α) Expand the F3a deferral set to include W1 (panel writer) → effectively defer the entire panel substrate cutover, defeating A3's primary purpose, OR
- (β) Add a cross-schema FK contract.cert → bcf.panel via DDL → out of A3 "no DDL" scope, requires re-authorization + creates an operational dependency that A4 freeze must un-thread, OR
- (γ) Drop fk_certification_record__panel_run → DDL change; loses substrate-level integrity, OR
- (δ) **Defer Phase A3 apply until §14 step 20 ships atomically alongside A3 — single combined apply gate (RECOMMENDED).** The merged A3 cutover code remains "armed but not deployed/applied". §14 step 20 work is authored and reviewed in parallel. The two slices apply atomically as one operational event — never deploy A3 cutover alone in production.

**Operator decision locked: resolution (δ).** See §12 D11 (updated) for resolution-set details and §14 (updated) for sequencing implications.

**Discipline trail:** PR #144 harness repair surfaced this finding via live SAVEPOINT-isolated test execution; Δ DB state from the failing test runs was 0 (sentinel-rollback worked exactly as documented). No production state was perturbed. The finding is documented in PR #144's PR body + commit message. This DBCP correction (the current edit) is the authoritative governance-artifact record.

## 4. Writer/reader inventory (Item 1)

Source inventory performed by:
- `from '<path>/database/schema/contract'` import grep across `bc-core/src/` (filtered to runtime source; tests and scripts excluded).
- `.insert(<table>)` / `.update(<table>)` / `.delete(<table>)` Drizzle grep against the 4 BCF evidence tables.

### 4.1 `contract.panel_output_record`

| Path | File | Class / function | Op |
|---|---|---|---|
| **Writer (sole, production)** | `src/registry/panel-output-record.repository.ts` | `PanelOutputRecordRepository.create()` | INSERT |
| **Reader** | `src/registry/framework-approval/repositories/panel-output-record.read.repository.ts` | `PanelOutputRecordReadRepository` (read-only sibling) | SELECT |
| **Reader** | `src/registry/framework-calibration/calibration-event.read.repository.ts` | `CalibrationEventReadRepository.aggregate()` — reads `quarantined` flag for C10/N30 calibration aggregate | SELECT |
| **Reader** | `src/registry/registry-authoring-panel/registry-provenance.read-repository.ts` | `ProvenanceReadRepository` — D414 provenance inspection (authoring evidence) | SELECT |
| **Reader** | `src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts` | `RegistryAuthoringOrchestratorService` — reads `panel_output_record` at line 281 (corrected per PR #15 review F1: file does NOT import the Drizzle `certificationRecord` symbol; it shuttles `certificationRecordId` values through service calls only) | SELECT |
| **Reader** | `src/registry/intake-queue.repository.ts` | `IntakeQueueRepository` — reads `panel_output_record` at line 275 (added per PR #15 review F2). The file ALSO reads `contract.intake_queue` which is out-of-A3-scope BCF C8 substrate (see §4.6); only the panel_output_record read flips in A3. | SELECT |
| **Controller (HTTP surface)** | `src/registry/panel-output-record.controller.ts` | API exposure | — |
| **Service** | `src/registry/panel-output-record.service.ts` | Orchestration | — |
| **Module** | `src/registry/panel-output-record.module.ts` | DI wiring | — |
| **Test-only writers (excluded from A3 cutover scope, but must update imports)** | `src/registry/registry-authoring-panel/registry-authoring-orchestrator.integration.spec.ts`<br/>`src/registry/concept-registry/registry-shape-issuance.integration.spec.ts`<br/>`src/registry/concept-registry/registry-authoring.integration.spec.ts` | Direct `.insert(panelOutputRecord)` for test setup | INSERT |

### 4.2 `contract.authoring_panel_rejection_log`

| Path | File | Class / function | Op |
|---|---|---|---|
| **Writer (SOLE per operator lock)** | `src/registry/framework-approval/repositories/rejection-log.write.repository.ts` | `RejectionLogWriteRepository.writeIfAbsent()` + `applyManualOverride()` | INSERT (ON CONFLICT DO NOTHING) + UPDATE |
| **Reader** | `src/registry/framework-approval/repositories/rejection-log.read.repository.ts` | `RejectionLogReadRepository.findOpen(limit)` | SELECT |
| **Controller (HTTP surface)** | `src/registry/framework-approval/rejection-log.controller.ts` | Operator-override action | — |
| **Service** | `src/registry/framework-approval/framework-approval.service.ts` | Calls writer on `kind='rejected'` branch | — |

**Module boundary lock** (R12 anchor): the writer is forbidden from being imported outside `src/registry/framework-approval/` per `bcf-c5-governance-state-sole-writer.spec.ts` import-boundary lockfile. A3 cutover must preserve this lock — the FORBIDDEN_OUTSIDE_BOUNDARY list is updated to point at the bcf-side Drizzle symbol, not loosened.

### 4.3 `contract.calibration_event`

| Path | File | Class / function | Op |
|---|---|---|---|
| **Writer (sole, production)** | `src/registry/framework-calibration/calibration-event.write.repository.ts` | `CalibrationEventWriteRepository.create()` | INSERT (ON CONFLICT DO NOTHING idempotent on `panel_run_uid`) |
| **Reader** | `src/registry/framework-calibration/calibration-event.read.repository.ts` | `CalibrationEventReadRepository.aggregate()` — rolling 30-day + all-time calibration counts | SELECT |
| **Service** | `src/registry/framework-calibration/calibration-sampling.service.ts` | Sampling-policy orchestration | — |
| **Module** | `src/registry/framework-calibration/framework-calibration.module.ts` | DI wiring | — |

### 4.4 `contract.certification_record`

| Path | File | Class / function | Op |
|---|---|---|---|
| **Writer (BCF-side; A3 cutover scope per F3a split)** | `src/registry/framework-approval/repositories/certification-record.write.repository.ts` | `CertificationRecordWriteRepository.writeBcfProducedRow()` (line 143) + `writeOperatorAuthoredRow()` (line 184) — 2 of 3 INSERT sites in the file flip to `bcf.certification_record` | INSERT |
| **Writer (BCF-side; A3 DEFERRED per F3a split)** | `src/registry/framework-approval/repositories/certification-record.write.repository.ts` | `CertificationRecordWriteRepository.writeRegistryShapeRow()` (line 264) — Registry-shape cert creator. Invoked from production at `framework-approval.service.ts:203` + `:495`. Rows born here are UPDATEd by the W5 BCR completion-stamp by `certificationRecordId`; the two paths are transactionally coupled and MUST defer together until the bcf.cert write-once trigger ships. Stays pointed at `contract.certification_record` during A3. | INSERT |
| **Writer (BCR-side completion stamp; A3 DEFERRED per F3a split)** | `src/registry/concept-registry/repositories/certification-stamp.repository.ts` | `CertificationStampRepository.stampTargetRegistryId()` — one-time `target_registry_id` NULL→non-NULL UPDATE. Stays pointed at `contract.certification_record` during A3; joint cutover with `writeRegistryShapeRow` per §14 step 20. | UPDATE |
| **Reader** | `src/registry/registry-authoring-panel/registry-provenance.read-repository.ts` | `ProvenanceReadRepository` — D414 provenance inspection (reads `certificationRecord` at line 179) | SELECT |
| **Reader** | `src/registry/concept-registry/certification-verifier.service.ts` | `CertificationVerifierService` — BCR cert verification (reads `certificationRecord` at line 151) | SELECT |
| **Reader** | `src/registry/registry-authoring-panel/registry-publication.service.ts` | Publication-time cert lookup (reads `certificationRecord` at line 395, filtered by `governanceScope='registry'`) | SELECT |
| **Test-only writer** | `src/registry/concept-registry/registry-authoring.integration.spec.ts` | Direct `.insert(certificationRecord)` for test setup | INSERT |

**Note (per PR #15 review F1):** `registry-authoring-orchestrator.service.ts` was previously misclassified as a cert reader. The file shuttles `certificationRecordId` values through service calls but does NOT import the Drizzle `certificationRecord` symbol nor `.from()` the cert table. Its actual contract-table dependency is `panel_output_record` (line 281); it is captured in §4.1 as a panel reader, not here.

**Reader-side joint defer (F3a + F6α):** Under F3a, `writeRegistryShapeRow` (W4b) continues to INSERT Registry-shape certs into `contract.certification_record` during A3. Under F6α, the cert readers split into three tiers based on production-regression risk: (i) **R6 (`registry-publication.service.ts`) is UNCONDITIONALLY in the joint-defer set** — its line 398-400 query filters `governanceScope='registry'` and reads Registry-shape certs exclusively; flipping R6 while W4b stays on `contract.cert` produces immediate publication-flow regression. (ii) **R5 (`certification-verifier.service.ts`) is LIKELY in the joint-defer set** — BCR cert verification typically resolves Registry-shape certs by `certificationRecordId` and would return "not found" for W4b-born rows under partial flip; the A3 cutover-PR's reader-exposure inventory records the final inclusion decision (default = defer with the slice). (iii) **R4 (`registry-provenance.read-repository.ts`) is per-shape** — reads mixed cert shapes; the cutover-PR records whether to flip or defer based on the inventory. All three (or whichever subset the inventory records) flip jointly with W4b + W5 in §14 step 20.

### 4.5 BCR completion-stamp + Registry-shape cert creator cross-cutting case (architectural finding; F3a deferral pair)

`CertificationStampRepository.stampTargetRegistryId()` (line 48 of `certification-stamp.repository.ts`) lives under `src/registry/concept-registry/repositories/` and performs the one-time `NULL → non-NULL` UPDATE that closes a Registry-shape authorization. The cross-schema write into `contract` is intentional under F2 (the F2 coexistence rule forbids a cross-schema FK, not a read or write).

**The cert ROW is BCF evidence** — the framework-approval-side writer creates it; A2 copied it to `bcf.certification_record`; under A3 new BCF writes COULD route there. The **stamp** (BCR completing its part) must target the same row.

**Constraint:** The write-once trigger `trg_certification_record_target_registry_id_guard` exists on `contract.certification_record` (created by `docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:221-226`); Phase A1 substrate creation did NOT replicate this trigger onto `bcf.certification_record` (A1 scope = tables + CHECKs + indexes + FKs + COMMENTs only; `bc-core/scripts/bcf-evidence-schema-phase-a1-ddl.mjs` contains ZERO `CREATE TRIGGER` statements).

**Transactional coupling with `writeRegistryShapeRow` (W4b):** Registry-shape cert rows are CREATED by `CertificationRecordWriteRepository.writeRegistryShapeRow()` (line 264 of `certification-record.write.repository.ts`; invoked from production at `framework-approval.service.ts:203` + `:495`). Rows born there with `target_registry_id=NULL` are UPDATEd by the stamp (W5) by `certificationRecordId` (the stamp accepts an outer `tx` and is invoked from `registry-authoring.service.ts:991`). The two paths form a writer pair: if `writeRegistryShapeRow` flipped to `bcf.cert` but the stamp stayed on `contract.cert`, the stamp UPDATE would target `contract.cert` and find no matching row → `NotFoundException` thrown at `registry-authoring.service.ts:1000-1002` for every post-A3 Registry-shape cert → production regression.

**Implication:** If A3 cutover moves `writeRegistryShapeRow()` to `bcf.cert` without also moving `stampTargetRegistryId()`, production breaks. If it moves BOTH without the write-once trigger on `bcf.cert`, the substrate-level write-once guarantee is lost during A3→A4 window. Adding the trigger is DDL — out of A3 scope per §1.3.

**D11 resolution (a) = F3a deferral pair (RECOMMENDED):** Both `writeRegistryShapeRow` (W4b) AND `stampTargetRegistryId` (W5) DEFER together. They continue to write to / UPDATE `contract.certification_record` during A3. Joint cutover in §14 step 20 (a separate DDL + code slice) after the write-once trigger ships on `bcf.cert`. This preserves production behavior AND substrate guarantees AND A3's no-DDL discipline.

### 4.6 Cross-schema reads NOT on A3 cutover list

These are reads that touch `contract.*` but are NOT among the 4 BCF evidence tables; they remain pointed at `contract.*` (out of A3 scope):

| Reader | Reads | Why out of A3 |
|---|---|---|
| `src/registry/mcf/mcf-cert-writer.service.ts` | `contract.framework_policy` (active policy validation) | Out of A3 — `framework_policy` is BCF A8 substrate, not in the 4 BCF evidence tables. A5 owns MCF↔framework-policy retarget if needed. |
| `src/registry/framework-calibration/phase-state.write.repository.ts` | `contract.phase_state` | Out of A3 — different substrate (BCF A14 phase-state tracker). |
| `src/registry/framework-approval/repositories/phase-state.read.repository.ts` | `contract.phase_state` | Out of A3 — same as above. |
| `src/registry/framework-approval/repositories/operator-confirm-rule.repository.ts` | `contract.operator_confirm_rule` | Out of A3 — BCF A9 substrate. |
| `src/registry/framework-approval/repositories/framework-policy.repository.ts` | `contract.framework_policy` | Out of A3 — BCF A8 substrate. |
| `src/registry/intake-queue.repository.ts` | `contract.intake_queue` | Out of A3 — BCF C8 substrate. **Note (per PR #15 review F2):** the file ALSO reads `contract.panel_output_record` at line 275; that read IS in A3 cutover scope (captured in §4.1 + §5.2 R8). The `intake_queue` read alone is out of A3. |
| `src/registry/chain-status.service.ts` | `contract.chain_status` / `contract.chain_trace` | Out of A3 — D305 chain SSOT. |

These substrates may move to `bcf.*` in a future phase; that is NOT in A3 scope. The boundary DBCP §13 ladder may add them as a separate phase (e.g. A3.5 for non-evidence BCF substrate) — flagged as out-of-A3 only.

## 5. Classification (Item 2)

### 5.1 Writers to cut over (5 production paths; W4 split into W4a flip + W4b defer per F3a)

| # | Repository file | Tables written | A3 action |
|---|---|---|---|
| W1 | `src/registry/panel-output-record.repository.ts` | panel_output_record | Drizzle import flip: `panelOutputRecord` from `database/schema/contract` → `database/schema/bcf` |
| W2 | `src/registry/framework-calibration/calibration-event.write.repository.ts` | calibration_event | Same — Drizzle import flip |
| W3 | `src/registry/framework-approval/repositories/rejection-log.write.repository.ts` | authoring_panel_rejection_log | Same — Drizzle import flip; sole-writer boundary lockfile updated |
| W4a | `src/registry/framework-approval/repositories/certification-record.write.repository.ts` | certification_record | **A3 cutover scope per F3a split.** Drizzle import flip applies to 2 of the file's 3 INSERT sites: `writeBcfProducedRow()` (line 143) + `writeOperatorAuthoredRow()` (line 184). Both flip to `bcf.certification_record` atomically. |
| W4b | `src/registry/framework-approval/repositories/certification-record.write.repository.ts` | certification_record | **A3 DEFERRED per F3a split.** `writeRegistryShapeRow()` (line 264) — the 3rd INSERT site — stays pointed at `contract.certification_record`. Tightly coupled to W5 (rows born here are UPDATEd by `stampTargetRegistryId` by `certificationRecordId`); both must flip together in §14 step 20 after the bcf.cert write-once trigger ships. Documented in §6.3 lockfile exception list. |
| W5 | `src/registry/concept-registry/repositories/certification-stamp.repository.ts` | certification_record (UPDATE) | **A3 DEFERRED per D11(a) + F3a split.** Stamp continues to UPDATE `contract.certification_record` until the write-once trigger ships on `bcf.certification_record`. Jointly cut over with W4b in §14 step 20 to preserve production behavior + substrate write-once guarantee. |

### 5.2 Readers to cut over (8 production paths; R7 reclassified + R8 added per PR #15 review F1/F2)

| # | Repository / service file | Tables read | A3 action |
|---|---|---|---|
| R1 | `src/registry/framework-approval/repositories/panel-output-record.read.repository.ts` | panel_output_record | Drizzle import flip |
| R2 | `src/registry/framework-calibration/calibration-event.read.repository.ts` | calibration_event + panel_output_record (`quarantined`) | Drizzle import flip |
| R3 | `src/registry/framework-approval/repositories/rejection-log.read.repository.ts` | authoring_panel_rejection_log | Drizzle import flip |
| R4 | `src/registry/registry-authoring-panel/registry-provenance.read-repository.ts` | panel_output_record + certification_record | Panel-read path: Drizzle import flip. Cert-read path: **per-shape evaluation per F6α** — cutover-PR's reader-exposure inventory records flip-vs-defer based on Registry-shape exposure; defers with §14 step 20 if recorded as Registry-shape-coupled. |
| R5 | `src/registry/concept-registry/certification-verifier.service.ts` | certification_record | **LIKELY DEFERRED per F6α** — BCR cert verification by ID would miss W4b-born Registry-shape rows under partial flip. Cutover-PR's reader-exposure inventory records the final decision (default = defer with §14 step 20). |
| R6 | `src/registry/registry-authoring-panel/registry-publication.service.ts` | certification_record (filtered by `governanceScope='registry'`) | **UNCONDITIONALLY DEFERRED per F6α** — R6 reads Registry-shape certs exclusively via the `governanceScope='registry'` filter at lines 398-400; flipping R6 while W4b stays on `contract.cert` produces immediate publication-flow regression. Joint cutover with W4b + W5 in §14 step 20. |
| R7 | `src/registry/registry-authoring-panel/registry-authoring-orchestrator.service.ts` | **panel_output_record** (line 281) — corrected per PR #15 review F1 (file does NOT import the Drizzle `certificationRecord` symbol; it shuttles `certificationRecordId` values through service calls only) | Drizzle import flip |
| R8 | `src/registry/intake-queue.repository.ts` | **panel_output_record** (line 275) — added per PR #15 review F2 (file ALSO reads `contract.intake_queue` which is out of A3 scope; only the panel_output_record read flips) | Drizzle import flip |

### 5.3 Historical / audit dual-read candidates

**Recommended: NONE.** A2 byte-equivalence makes dual-read unnecessary; any reader can switch to `bcf.*` atomically with its writer counterpart and observe identical data. Dual-read introduces split-brain risk (R1) without benefit because there is no version skew between the two schemas (rows are byte-identical and A3 writes flip atomically per W1..W3 + W4a; the F3a / F6α joint-defer set W4b + W5 + R6 + (likely R5) + (per-shape R4) stays on `contract.cert` and is not in scope for dual-read either).

D5 leaves the operator the choice of allowing dual-read; the recommended D5 answer is "NO dual-read".

### 5.4 Out-of-A3-scope contract-chain infrastructure

| Substrate | Status under A3 |
|---|---|
| `contract.framework_policy` (BCF A8) | Untouched; readers stay pointed at `contract.*` |
| `contract.phase_state` (BCF A14) | Untouched; readers stay pointed at `contract.*` |
| `contract.operator_confirm_rule` (BCF A9) | Untouched |
| `contract.intake_queue` (BCF C8) | Untouched |
| `contract.chain_status` / `contract.chain_trace` (D305) | Untouched |
| `concept_registry.*` (BCR vocabulary) | Untouched (Option A lock) |
| `mcf.*` (MCF substrate) | Untouched (A5 owns FK retarget) |
| `metric.*` (metric chain) | Untouched |
| tenant `tbc_{slug}_dev` DBs | Untouched (HR4) |
| DB triggers / CHECKs / FKs on `contract.*` | Untouched (no DDL) |

### 5.5 Controllers (HTTP surface preserved)

| Controller | A3 action |
|---|---|
| `src/registry/panel-output-record.controller.ts` | NO route changes; internal repository targets flip via W1 |
| `src/registry/framework-approval/rejection-log.controller.ts` | NO route changes; internal repository targets flip via W3 |

Public HTTP API contracts (route, request shape, response shape) MUST NOT change. bc-admin / bc-portal consumers see no change.

## 6. Cutover strategy (Item 3)

### 6.1 Writers-first then readers (W1..W3 + W4a → R1..R8; W4b + W5 DEFERRED per F3a)

Writers flip first. Once W1..W3 + W4a are routed to `bcf.*`:
- New `bcf.panel_output_record` / `bcf.authoring_panel_rejection_log` / `bcf.calibration_event` rows land in `bcf.*` only (`contract.*` no longer receives writes for those 3 tables).
- New BCF-produced + operator-authored cert rows (W4a paths) land in `bcf.certification_record` only.
- **Registry-shape cert rows (W4b path) continue to land in `contract.certification_record`** until §14 step 20 (F3a deferred).
- **W5 BCR completion-stamp continues to UPDATE `contract.certification_record`** until §14 step 20 (F3a deferred).
- A2 insert-copy already populated `bcf.*` with the historical 3,568 rows.
- Readers still pointing at `contract.*` for the 3 flipped tables see frozen-as-of-A2 data; they MISS new writes there.

Readers flip second (same PR or next PR per D4):
- Once R1..R3 + R7 + R8 are routed to `bcf.*` (panel + rejection + calibration paths), they see both the A2-migrated historical rows and the post-A3-writer-cutover new rows.
- For R4 / R5 / R6 (cert readers): F6α specifies the joint-defer membership: **R6 is unconditional** (reads Registry-shape certs exclusively via `governanceScope='registry'` filter at `registry-publication.service.ts:398-400`; flipping R6 while W4b stays on `contract.cert` is immediate publication-flow regression — joint defer with §14 step 20). **R5 is likely** (BCR cert verification by ID would miss W4b-born rows under partial flip; cutover-PR reader-exposure inventory records the final decision — default defer). **R4 is per-shape** (reads mixed cert shapes; cutover-PR inventory records flip vs defer). The deferred subset cutovers jointly with W4b + W5 in §14 step 20.

### 6.2 Default target `bcf.*`

For the 4 BCF evidence tables, the post-A3 routing is unambiguously `bcf.*`. No conditional routing, no fallback, no environment switch.

### 6.3 No new writes to `contract.*` for BCF evidence post-A3 (with documented F3a exceptions)

After W1..W3 + W4a ship, no BCF authoring / calibration / rejection-log write and no BCF-produced or operator-authored cert write may target `contract.*`. The cutover-PR's CI must include a static check (lockfile-style grep against the production source tree) asserting that:
- No `from '../database/schema/contract'` import remains in the W1, W2, W3, W4a writer code paths.
- No `.insert(panelOutputRecord)` / `.insert(authoringPanelRejectionLog)` / `.insert(calibrationEvent)` against the contract-side Drizzle symbols exists in production source.
- For `certificationRecord`: **two specific sites** may legitimately remain pointed at `contract.certification_record` during A3 (F3a documented exceptions), and ONLY those two:
  - **W4b**: `CertificationRecordWriteRepository.writeRegistryShapeRow()` at `certification-record.write.repository.ts:264` — `.insert(certificationRecord)` against the contract-side symbol.
  - **W5**: `CertificationStampRepository.stampTargetRegistryId()` at `certification-stamp.repository.ts:48` — `.update(certificationRecord)` against the contract-side symbol.

These 2 documented EXCEPTIONS (F3a split, both deferred together) are tracked in the lockfile's allowed-exception list with a follow-up tracking task linking to §14 step 20. They cutover together as a single later slice after the bcf.cert write-once trigger ships. The lockfile FAILS the cutover-PR if any other contract-side BCF write site (insert OR update) appears in production source, or if the W4b/W5 exception list grows beyond these 2 sites.

### 6.4 No deletion / freezing of `contract.*` (A4 owns)

`contract.panel_output_record` / `authoring_panel_rejection_log` / `calibration_event` / `certification_record` rows remain in place after A3. The tables remain writable at the DB level. The application-level discipline is that no NEW writes target them for the 3 panel/rejection/calibration tables and the W4a cert paths — which is enforced by W1..W3 + W4a import flip + the §6.3 static check. The W4b INSERTs + W5 UPDATEs are documented F3a / F6α exceptions that continue to land in `contract.certification_record` until §14 step 20.

The actual table freeze (e.g. `REVOKE INSERT/UPDATE/DELETE` from the platform DB role, or a row-deny trigger) is Phase A4's concern. A3 does not require it because the application no longer issues the writes.

### 6.5 Per-table cutover sequencing within the writers-first PR

| Order | Symbol | Why this order |
|---|---|---|
| 1 | `panelOutputRecord` (W1) | Root entity; no incoming FKs from W2/W3/W4 |
| 2 | `calibrationEvent` (W2) | FK to `panel_output_record(panel_run_uid)`; W1 already cutover |
| 3 | `authoringPanelRejectionLog` (W3) | FK to `panel_output_record(panel_run_uid)`; W1 already cutover |
| 4 | `certificationRecord` (W4) | FK to `panel_output_record(panel_run_uid)` (NF1 path); W1 already cutover |

The order matters only at the level of the cutover-PR build sequence (and integration tests) — at runtime all 4 writers compose into the same transaction envelope when called within a single panel-run ingest. The cutover-PR's diff lists changes in this order for review clarity.

## 7. Backward-compatibility window (Item 4)

### 7.1 `contract.*` and `bcf.*` duplication until A4

The duplication is intentional and tolerated. Phase A2's byte-equivalence assertion #205 guarantees that any reader switching between `contract.*` and `bcf.*` observes identical row data. The cutover is therefore semantically safe at any single instant — there is no version skew to reconcile.

Post-A3 writer cutover, the schemas diverge:
- `bcf.*` receives all new BCF writes.
- `contract.*` retains only the A2-migrated historical rows (frozen-as-of-A2).

After this divergence begins, the `contract.*` BCF evidence tables are read-stale and should not be queried for live operational state — they remain in place purely as a rollback / audit anchor until A4.

### 7.2 Dual-read / read-fallback policy (D5 decision required)

**Recommended (D5 answer = NO):** No dual-read. The 8 reader paths (R1..R8) flip to `bcf.*` in the cutover-PR (same PR or staged-PR per D4), MINUS the F6α joint-defer subset — R6 (unconditional) + R5 (likely) + R4 (per-shape) — which stays on `contract.cert` alongside W4b + W5 until §14 step 20. See §12 D11 for the joint-defer set composition.

**Alternative (D5 answer = YES, scoped):** Allow dual-read for a defined window (e.g. 1 release cycle), with the reader querying `bcf.*` first and falling back to `contract.*` if the row is missing. This is NOT recommended because:
- A2 byte-equivalence makes the fallback dead code (rows that exist in `contract.*` post-A2 also exist in `bcf.*`).
- Fallback obscures the cutover boundary and makes the rollback envelope murkier.
- A4 freeze becomes harder to verify if the application is allowed to read `contract.*`.

If D5=YES is operator-chosen, the fallback policy must specify: per-reader scope (which of R1..R8, excluding the F6α joint-defer subset which has no fallback semantics under F3a), window duration (release count or wall-clock), removal trigger (event after which the fallback path is deleted from the source tree).

### 7.3 Forbid new BCF authority writes to `contract.*` post-A3

Enforced by:
- **Application-level**: §6.3 lockfile-style static check on the cutover-PR (CI must FAIL if a `.insert(panelOutputRecord)` / etc. against the contract-side Drizzle symbol remains in production source).
- **Test-level**: a new spec `bcf-a3-no-contract-bcf-writes.spec.ts` greps the production source tree and asserts no writes to the 4 contract-side BCF evidence Drizzle symbols (exception: BCR completion-stamp W5 if D11 defers).

**Not enforced at the DB level in A3** (that is A4's job via DB-side write-deny). A3 ships application discipline; A4 hardens it at the substrate.

### 7.4 No-synthetic guard remains binding

The HR1 substrate CHECKs on `bcf.panel_output_record` and `bcf.certification_record` continue to reject synthetic-provider INSERTs after A3 writer cutover. No A3 work relaxes HR1.

The cutover-PR's integration tests must include at least one negative test that confirms: a writer with a synthetic payload, routed through the new bcf.*-target import path, fails with the HR1 CHECK violation. This is the same defense-in-depth that A2 inherited from A1.

## 8. Test/evidence plan (Item 5)

### 8.1 Static grep / source inventory (lockfile)

A new file `bc-core/scripts/bcf-phase-a3-import-lockfile.mjs` (or test-only equivalent) runs as part of the cutover-PR CI and asserts:

| Assertion | Scope |
|---|---|
| `from '../database/schema/contract'` does NOT appear in W1, W2, W3, W4a writer code paths | Production writer source |
| `panelOutputRecord` Drizzle symbol from contract is NOT imported in W1, R1..R8 (includes corrected R7 + added R8 per PR #15 review F1/F2) | Production source — covers all 1 writer + 5 readers of the panel table |
| `authoringPanelRejectionLog` Drizzle symbol from contract is NOT imported in W3, R3 | Production source |
| `calibrationEvent` Drizzle symbol from contract is NOT imported in W2, R2 | Production source |
| `.insert(panelOutputRecord)` / `.insert(authoringPanelRejectionLog)` / `.insert(calibrationEvent)` against contract-side symbols does NOT appear in production source | Excludes tests, scripts, audit-output |
| `.insert(certificationRecord)` against contract-side symbol: **ONLY** the W4b `writeRegistryShapeRow` site (line 264 of `certification-record.write.repository.ts`) may remain — F3a documented exception | Until §14 step 20 ships |
| `.update(certificationRecord)` against contract-side symbol: **ONLY** the W5 BCR completion-stamp site (line 48 of `certification-stamp.repository.ts`) may remain — F3a / D11(a) documented exception | Until §14 step 20 ships |
| Allowed-exception list size: **exactly 2 sites** (W4b + W5), both tightly coupled; tracked for joint cutover | Documented exception list |
| Module-boundary lock for `RejectionLogWriteRepository` continues to enforce import-only-within `framework-approval/` (with the bcf-side symbol) | `bcf-c5-governance-state-sole-writer.spec.ts` extension |
| Static scan of reader paths R1..R8 confirms no fallback / dual-read code path against contract-side BCF Drizzle symbols (D5 = NO recommended) | Production reader source |

### 8.2 Unit + integration tests

- **Unit tests:** existing `*.spec.ts` for W1..W3 + W4a + R1..R8 (excluding F6α joint-defer subset members: W4b, W5, R6 definitely; R5 likely; R4 per-shape) re-targeted to the bcf-side Drizzle symbols. No new test logic — the import path is the only change for the flipped subset.
- **Integration tests:** existing `*.integration.spec.ts` likewise re-targeted. The 3 integration specs that currently insert into `contract.panel_output_record` for test setup (per §4.1 row) update to insert into `bcf.panel_output_record`.
- **New negative test:** synthetic-payload through bcf.* writer fails with HR1 CHECK violation (defense-in-depth confirmation).
- **New positive test:** end-to-end BCF authoring run for non-Registry-shape paths (W1 → W2 + W3 + W4a composition) lands all rows in `bcf.*`; no new rows in `contract.*` outside the F3a documented W4b INSERT + W5 UPDATE exceptions.

### 8.3 Dry-run verification (cutover-PR pre-apply gates)

The bc-core cutover-PR's CI must include a dry-run script (e.g. `bcf-evidence-schema-phase-a3-dry-run.mjs`) that performs read-only verification:

| Probe | Code | Description |
|---|---|---|
| 1 | `a3_repo_anchor` | bc-core HEAD == post-PR-#140 anchor or later |
| 2 | `a3_substrate_present` | `bcf.*` schema + 4 tables present |
| 3 | `a3_a2_rows_present` | `bcf.*` row counts == 19 / 0 / 19 / 3530 (post-A2 baseline) |
| 4 | `a3_no_new_writes_to_contract` | (deferred to post-apply) |
| 5 | `a3_drizzle_imports_lockfile` | Static grep returns 0 contract-side imports in W1..W3 + W4a + R1..R8 (excluding F6α joint-defer set: W4b + W5 + R6 definitely; R5 likely; R4 per-shape) |
| 6 | `a3_no_dual_read_unless_d5_yes` | If D5=NO, static grep confirms no fallback code paths exist |
| 7 | `a3_no_synthetic_in_target` | `bcf.*` synthetic-provider count == 0/0 (HR1 binding) |
| 8 | `a3_substrate_parity` | `bcf.*` shape matches `contract.*` (CHECKs / indexes / FKs present per A1 anchor) |
| 9 | `a3_no_contract_freeze_yet` | `contract.*` BCF evidence tables still writable at DB level (A4 owns freeze; A3 verifies the freeze has NOT happened) |
| 10 | `a3_no_mcf_fk_change` | `mcf.*` FK shape unchanged from post-A2 baseline (A5 owns retarget) |

Exit codes mirror the A2 dry-run pattern (0 = PASS / 30 = BLOCKED-FOR-APPLY / 1..29 = inventory FAIL).

### 8.4 Post-apply DB invariants (cutover-PR apply gate evidence)

After the cutover-PR's first runtime cycle in the target environment (operator-authorized apply), an evidence script (`bcf-evidence-schema-phase-a3-post-apply.mjs`) probes:

| # | Probe | Expected |
|---|---|---|
| 200 | `bcf.panel_output_record` total rows | ≥ 19 (A2 baseline + new writes post-A3) |
| 201 | `bcf.calibration_event` total rows | ≥ 19 |
| 202 | `bcf.authoring_panel_rejection_log` total rows | ≥ 0 |
| 203 | `bcf.certification_record` total rows | ≥ 3,530 |
| 204 | `contract.panel_output_record` total rows | exactly 19 (no new writes from BCF path) |
| 205 | `contract.calibration_event` total rows | exactly 19 |
| 206 | `contract.authoring_panel_rejection_log` total rows | exactly 0 |
| 207 | `contract.certification_record` total rows | exactly 3,530 + N where N counts ONLY the documented F3a exception rows: W4b `writeRegistryShapeRow` INSERTs (Registry-shape; new rows that legitimately add to count) + W5 `stampTargetRegistryId` UPDATEs (no row-count change; only `target_registry_id` populated on existing rows); no other new INSERTs from any BCF path |
| 208 | `bcf.*` synthetic-provider count | 0/0 (HR1 still binding) |
| 209 | `contract.*` synthetic-provider count | 0/0 |
| 210 | Cross-schema FKs from `bcf.*` to non-`bcf.*` | 0 |
| 211 | `mcf.*` total rows | 0 (HR2 untouched) |
| 212 | `concept_registry.*` total rows | 68 (untouched) |
| 213 | Standing MCF indexes | both present |
| 214 | `contract.*` BCF tables writable at DB level | TRUE (A4 freeze has NOT happened) |

### 8.5 No new rows in `contract.*` from BCF writer paths

Probes #204..#207 are the operational measurement of §6.3. If probes #204..#206 exceed the post-A2 baseline by even one row, OR if probe #207 grows by anything other than the documented F3a exceptions (W4b `writeRegistryShapeRow` INSERTs into `contract.certification_record`; W5 `stampTargetRegistryId` UPDATEs which do not add rows), the cutover-PR is BLOCKED at the apply gate.

## 9. Rollback plan (Item 6)

### 9.1 Pre-A4 only

A3 rollback is valid only while `contract.*` retains the A2-migrated rows and is writable. Once A4 freezes `contract.*` (REVOKE / row-deny trigger / table drop, per A4 design), A3 rollback is no longer meaningful — the application cannot route writes back to `contract.*` because the substrate no longer accepts them. A4 DBCP will own its own restore plan.

The rollback script must include a pre-rollback guard that verifies:
| Guard | Code | Description |
|---|---|---|
| 1 | `a3_rollback_phase_a4_not_shipped` | `contract.*` BCF evidence tables are writable; no A4 freeze trigger / REVOKE detected |
| 2 | `a3_rollback_contract_rows_intact` | `contract.*` row counts unchanged from post-A2 baseline (19/0/19/3530) |
| 3 | `a3_rollback_bcf_rows_present` | `bcf.*` rows present and not deleted (rollback does NOT delete bcf.*) |
| 4 | `a3_rollback_env_gate_present` | `BCCORE_BCF_PHASE_A3_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_<ts>` env var set |

### 9.2 Restore writer/reader routing to `contract.*`

Rollback is `git revert` of the cutover-PR's squash commit. Specifically:
- W1..W3 + W4a revert their Drizzle import back to `contract.*` (W4b + W5 stayed on `contract.*` during A3 per F3a / F6α; not part of A3 rollback).
- R1..R8 revert their Drizzle import back to `contract.*` MINUS the F6α joint-defer subset that stayed on `contract.*` during A3 (R6 unconditional + R5 likely + R4 per-shape; not part of A3 rollback).
- The §6.3 import-lockfile check is removed by the revert.
- Module boundary lock for `RejectionLogWriteRepository` reverts its FORBIDDEN_OUTSIDE_BOUNDARY list.
- bc-admin / bc-portal consumers see no change (HTTP API contracts unchanged across cutover or rollback).

### 9.3 Do NOT delete `bcf.*` rows

A3 rollback restores routing only. The 3,568 A2-migrated rows in `bcf.*` remain in place. After rollback, the `bcf.*` rows become frozen-as-of-A2-migration (no new writes), and the substrate continues to enforce HR1 CHECKs.

A separate (Phase A2-owned) rollback exists for deleting `bcf.*` rows; that is the existing `bcf-evidence-schema-phase-a2-rollback.mjs` env-gated by `BCCORE_BCF_PHASE_A2_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_2026-05-29T04-33-48-487Z`. A3 rollback does NOT compose with or trigger that script; they are independent envelopes.

### 9.4 Post-A4 rollback explicitly out of scope

A4 will own its own restore plan. Until A4 DBCP is authored, the post-A4 rollback path is undefined. The A3 rollback script's guard #1 enforces this — once A4 ships, A3 rollback is a no-op (it fails at the guard rather than attempting a routing flip that cannot land writes anywhere).

**Updated post-PR #144 finding (D11(δ) atomic-pair apply model):** Because standalone A3 apply is now forbidden (§3.5 / R9 updated / D11(δ)), the rollback envelope must account for the **combined A3 + §14 step 20 apply**, not standalone A3 only. Specifically:
- **Pre-rollback guards** must verify that BOTH A3 cutover code and §14 step 20 work have applied (or that neither has) — partial-apply state is not a valid starting point for A3 rollback.
- **Post-rollback assertions** for a combined-apply rollback include the §14 step 20 reversion: W4b + W5 + R6 (+ R5/R4 if flipped) revert to contract.cert imports; the bcf.cert write-once trigger is dropped via revert of the step 20 DDL slice.
- The existing `scripts/bcf-evidence-schema-phase-a3-rollback.mjs` rollback verifier (env-gated by `BCCORE_BCF_PHASE_A3_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_<ts>`) must be extended (in a separate hygiene PR before the combined apply gate) to accept a `--mode=pre-rollback-combined` / `--mode=post-rollback-combined` to cover the atomic-pair envelope. Until then, the existing pre/post-rollback modes apply ONLY to the standalone-A3 envelope, which is now forbidden — so the rollback script in main is effectively dormant until extended.

### 9.5 Rollback verification (post-rollback assertions)

After A3 rollback:
| # | Probe | Expected |
|---|---|---|
| 300 | W1..W3 + W4a import paths point at `contract.*` (W4b stayed on `contract.*` during A3 per F3a; out of revert scope) | TRUE (per git diff against post-apply commit) |
| 301 | R1..R8 import paths point at `contract.*` (the F6α joint-defer subset R6 + likely R5 + per-shape R4 stayed on `contract.*` during A3; out of revert scope) | TRUE |
| 302 | `bcf.*` row counts | unchanged from post-A2 baseline (19/0/19/3530) |
| 303 | `contract.*` row counts | unchanged from post-A2 baseline (19/0/19/3530) — A3 cutover did not change them, and rollback does not change them |
| 304 | `bcf.*` substrate CHECKs / FKs / indexes | still present (HR1 unchanged) |
| 305 | Module-boundary lock for `RejectionLogWriteRepository` | restored to contract-side symbol |
| 306 | `mcf.*` / `concept_registry.*` | untouched |

## 10. Relationship to downstream phases (Item 7)

### 10.1 A4 owns freeze/retire of `contract.*`

Phase A4 will design and execute:
- Application-side: nothing (A3 already removed application writes).
- DB-side: REVOKE INSERT/UPDATE/DELETE from the platform DB role on the 4 BCF evidence tables, or install a row-deny trigger that rejects writes (operator-decided in A4 DBCP).
- Eventually: DROP the 4 tables (after A4 burn-in window + operator authorization).

A3 does NONE of this. A3 verifies that A4 freeze has NOT happened (probe #9 / #214 / rollback guard #1).

### 10.2 A5 owns MCF FK retarget + M12 writer flip

Phase A5 will:
- Retarget the 5 mcf→contract FKs to point at `bcf.*` (or remove them if Option A locks mcf-cluster separation).
- Flip the M12 writer (`MetricAuthoringPanelService` / equivalent) from `contract.*` to `mcf.*` panel substrate (per M12 design, not BCF design).

A3 does NONE of this. A3 verifies the 5 mcf→contract FKs are unchanged (probe #10).

### 10.3 A3 must not change MCF FKs

Static check: A3 cutover-PR's diff must NOT touch any `mcf.*` Drizzle schema file or any FK declaration referencing `contract.*` from `mcf.*`. The PR review gate fails if the diff includes `src/database/schema/mcf/` paths.

### 10.4 A3 must not open first real M12 panel run

M12 first real panel run is a separately operator-authorized gate that opens after M14 evaluation chain is ready (sequencing per parent boundary DBCP §13 step 19+). A3 does not invoke M12 panel run; the cutover-PR's test plan uses canned test fixtures (existing integration spec inputs), not first-real-run inputs.

### 10.5 A3 must not open M14

M14 remains CLOSED throughout A3. The cutover-PR adds NO M14-opening code, NO M14-publication-eligibility activation, NO M14 evaluator wiring. If M14 surfaces in the diff, the PR review gate fails.

## 11. Risk register (Item 8)

| # | Risk | Mitigation |
|---|---|---|
| R1 | **Reader double-counting during duplication window.** A reader inadvertently aggregating both schemas would inflate counts. | A2 byte-equivalence + A3 cutover means readers point at exactly ONE schema at any time (D5 = NO dual-read recommended). The §6.3 lockfile blocks an accidental dual-aggregation pattern. |
| R2 | **Writer split-brain between `contract.*` and `bcf.*`.** A writer left pointing at `contract.*` after A3 cutover would create rows the readers (now on `bcf.*`) cannot see. | W1..W3 + W4a atomic cutover in a single PR; §8.1 lockfile asserts ZERO production writer imports of contract-side BCF symbols outside the 2 documented F3a exception sites (W4b `writeRegistryShapeRow` INSERT + W5 BCR-stamp UPDATE, both deferred per F3a / D11(a) until §14 step 20). |
| R3 | **Stale reader still querying `contract.*` after cutover.** Symmetric of R2 — a reader left pointing at `contract.*` misses new bcf-targeted writes. | R1..R8 atomic cutover (same PR or staged per D4) MINUS the F6α joint-defer subset (R6 unconditional; R5 likely; R4 per-shape) that legitimately remains on `contract.*` until §14 step 20; §8.1 lockfile + §8.3 probe #5. |
| R4 | **Accidental A4-style freeze/delete sneaking into A3.** A `REVOKE`, row-deny trigger, or DROP on `contract.*` would convert A3 into A3+A4 and break A3 rollback. | §1.3 explicit non-scope + §8.3 probe #9 / §8.4 probe #214 verify no A4 freeze artifacts present. PR review gate fails on DDL diff. |
| R5 | **Accidental MCF FK or M-series work sneaking into A3.** A diff touching `src/database/schema/mcf/` or any M11/M12/M12.5/M13/M14 wiring would cross phase boundaries. | §10.3 / §10.5 explicit prohibition + PR review gate on diff paths. |
| R6 | **Rollback after A4 ambiguity.** Operator runs A3 rollback after A4 has shipped, expecting routing-back-to-`contract.*` to work; in reality `contract.*` is frozen. | §9.1 rollback guard #1 + §9.4 explicit out-of-scope statement; A4 DBCP must own its own restore plan. |
| R7 | **Tenant DB leakage.** A3 cutover-PR's CI or post-apply probe inadvertently connects to a tenant DB. | HR4 env-guard substrate-enforced (same pattern as A1/A2 scripts: `TENANT_DATABASE_URL=` cleared at invocation; only `DATABASE_URL` opened). |
| R8 | **Synthetic / mock / replay / canned rows reappearing through writer path.** A bug in the cutover-PR routes a test-payload (synthetic provider) into production-tagged writes. | HR1 substrate CHECKs on `bcf.panel_output_record` + `bcf.certification_record` reject at INSERT (defense-in-depth); §8.2 new negative test confirms the CHECK fires. |
| R9 | **BCR completion-stamp write-once trigger absent on `bcf.certification_record`, AND tight transactional + reader-side coupling spanning W4b + W5 + R4/R5/R6, AND (PR #144 finding) cross-schema FK breakage that makes the original F3a deferral NOT apply-safe.** Phase A1 did not create `trg_certification_record_target_registry_id_guard` on the bcf-side substrate. Writer-side coupling: W4b → W5 round-trip via `certificationRecordId`. Reader-side coupling (F6α): R6 unconditional + R5 likely + R4 per-shape per Registry-shape exposure. **NEW FINDING (PR #144, 2026-05-29):** the original F3a / F6α deferral set is **INSUFFICIENT**. The missing dependency is W1 (panel writer location). `contract.certification_record.panel_run_uid` has FK `fk_certification_record__panel_run` → `contract.panel_output_record(panel_run_uid)`. Under A3 cutover, W1 writes new panel rows to `bcf.panel_output_record` — but W4b (DEFERRED per F3a) continues to INSERT Registry-shape certs into `contract.certification_record` referencing those bcf-side panel_run_uids. The FK lookup fails in `contract.panel_output_record` (empty for new uids) → W4b INSERT REJECTED at the substrate level **before** the W5 stamp's transactional coupling matters. The risk is therefore not just reader-side miss; it is writer-side FK failure on every Registry publication in the A3→step-20 window. | **DEFERRED via D11(δ) — STANDALONE A3 APPLY FORBIDDEN.** The original D11(a) joint-defer set (W4b + W5 + R6 + R5 + R4-cert on contract) is insufficient because the panel writer (W1) cuts over to bcf, breaking the contract.cert → contract.panel FK for any new write. **New resolution (δ) locked:** Phase A3 apply is BLOCKED until §14 step 20 ships atomically alongside A3 as a single combined apply gate. §14 step 20 must include the bcf.cert write-once trigger DDL + atomic flip of W4b + W5 + R6 (+ R5 default + R4 per-shape). The merged A3 cutover code remains armed but not deployed/applied. Standalone A3 apply forbidden by §3.5 / D11(δ) / §14 step 18 (updated). |
| R10 | **DB trigger / CHECK / FK skew between `contract.*` and `bcf.*`.** Beyond R9, other triggers may exist on `contract.*` evidence tables that Phase A1 did not replicate. | Pre-cutover read-only audit: enumerate all DB-level objects (triggers, CHECKs, FKs, indexes) on the 4 `contract.*` BCF evidence tables and confirm 1:1 parity with `bcf.*`. Surface gaps as additional D-decisions before the cutover-PR ships. |
| R11 | **Drizzle schema files for `bcf.*` may not yet exist.** If `src/database/schema/bcf/panel-output-record.ts` (etc.) does not exist as a sibling to `src/database/schema/contract/panel-output-record.ts`, the cutover-PR cannot land an import flip. | The cutover-PR's first commit is "add bcf-side Drizzle schemas" (no behavior change — pure substrate ORM mapping). Subsequent commits in the same PR flip the writer/reader imports. PR review can review the substrate mapping in isolation. |
| R12 | **Module-boundary lock loosening.** `bcf-c5-governance-state-sole-writer.spec.ts` enforces import-boundary on `RejectionLogWriteRepository`; cutover-PR must update its FORBIDDEN_OUTSIDE_BOUNDARY list without weakening the lock. | §8.1 lockfile + §8.2 spec re-targeting; PR review checks the spec's import-allowlist before/after diff. |

## 12. Operator decisions (Item 9)

| # | Decision | Recommended | Options |
|---|---|---|---|
| **D1** | Confirm A3 is **code-routing design only** at this DBCP stage. | **YES** | YES (this DBCP authorizes design; bc-core implementation PR is a SEPARATE follow-up authorization) / NO (re-scope) |
| **D2** | Authorize later **bc-core implementation PR authoring** (not execution). | **YES** | YES (the cutover-PR can be authored; merge gate is SEPARATE operator authorization) / NO (re-scope) |
| **D3** | **Writer cutover style.** | **Atomic single-PR** (W1..W3 + W4a in one PR with mandatory atomic-flip semantics; W4b deferred per F3a — joint cutover with W5 in §14 step 20) | Atomic single-PR / Feature-flag staged (writers gated behind `BCCORE_BCF_WRITER_TARGET=bcf` env var, default-off then default-on) |
| **D4** | **Reader cutover style.** | **Same PR as writers** (R1..R8 atomically with W1..W3 + W4a, MINUS the F6α joint-defer subset R6 unconditional + R5 likely + R4 per-shape — those defer to §14 step 20 alongside W4b + W5) | Same PR / Subsequent PR after writers ship (writers + readers share a release; readers lag writers by ≤ 1 release cycle) / Feature-flag staged |
| **D5** | **Temporary dual-read / fallback** allowed Y/N. | **NO** | NO (atomic flip; no fallback code path) / YES, scoped (specify per-reader scope + window + removal trigger) |
| **D6** | Confirm **no `contract.*` freeze/delete in A3**. | **YES** | YES / NO (re-scope into A3+A4 — NOT recommended; A4 is its own DBCP with operator gate) |
| **D7** | Confirm **no MCF FK retarget in A3**. | **YES** | YES / NO (re-scope — NOT recommended; A5 owns) |
| **D8** | Confirm **no tenant DB work**. | **YES** | YES / NO (re-scope — NOT recommended; tenant DBs are HR4-isolated) |
| **D9** | Confirm **no M-series invocation; M14 remains CLOSED**. | **YES** | YES / NO (re-scope — NOT recommended) |
| **D10** | Confirm **rollback validity window is pre-A4 only**. | **YES** | YES / NO (re-scope — would require A4 DBCP to spec post-A4 restore path before A3 ships) |
| **D11** | **W4b + W5 + reader-side coordination joint deferral, AND (PR #144 finding 2026-05-29) cross-schema FK breakage that makes the original F3a/F6α deferral NOT apply-safe.** The original analysis covered write-once trigger absence (R9) + W4b→W5 transactional coupling + R6/R5/R4-cert reader-side coupling. PR #144 live integration testing discovered an additional dependency: W1 cutover relocates new panel rows to `bcf.panel_output_record`, but W4b's INSERT into `contract.certification_record` carries a `panel_run_uid` FK to `contract.panel_output_record` — the lookup fails for every new uid, blocking the W4b INSERT at the substrate level. | **Defer joint set = W4b + W5 + R6 + R5 + R4-cert** until §14 step 20 ships atomically alongside A3 as a SINGLE combined apply gate. **STANDALONE A3 APPLY FORBIDDEN** by §3.5 / R9 (updated) / §14 step 18 (updated). | (δ) **F3a + F6α + PR #144 finding — Defer Phase A3 apply until §14 step 20 ships atomically alongside A3.** Resolution (a) [original D11 recommendation] is now KNOWN-INVALID because the cross-schema FK breakage from R9-extended makes W4b INSERT FK-fail before the W5 stamp coupling matters. The merged A3 cutover code remains armed but not deployed/applied. §14 step 20 is authored and reviewed in parallel; the two slices apply atomically as one operational event. §14 step 20 must ship: (i) bcf.cert write-once trigger DDL (`trg_certification_record_target_registry_id_guard` equivalent on `bcf.certification_record`); (ii) W4b `writeRegistryShapeRow` Drizzle flip to bcf.certification_record; (iii) W5 `stampTargetRegistryId` Drizzle flip to bcf.certification_record; (iv) R6 `registry-publication.service.ts` flip to bcf.certification_record (UNCONDITIONAL per F6α); (v) R5 `certification-verifier.service.ts` default flip unless cutover-implementation inventory proves exemption; (vi) R4 cert-read path per-shape resolution (records final treatment in closeout doc). **RECOMMENDED — LOCKED by operator decision post-PR #144.** Preserves production behavior end-to-end (writer-side FK integrity restored because the cert now FKs to bcf.panel where W1 writes; W4b → W5 stamp integrity; R6 publication-confirm lookup), A3's no-DDL discipline (DDL is in step 20, not A3), and substrate write-once guarantee.<br/>(a) ~~Original recommendation: defer W4b + W5 + R6 + R5 + R4-cert; W1 cuts over alone in A3.~~ **NOT APPLY-SAFE per §3.5 / R9 (updated) / PR #144 finding.** The original assumption — that the contract.cert → contract.panel FK relationship would continue to hold during the A3→step-20 window — is false. RETIRED.<br/>(b) Ship the bcf.cert trigger as a DDL micro-slice inside A3 — relaxes A3 "no DDL" scope; functionally equivalent to (δ) but framed as a single phase rather than a paired-atomic gate. Acceptable alternative if the operator prefers single-phase governance.<br/>(c) Cutover W4b + W5 + R6 without the trigger — loses write-once enforcement during the window; substrate-level guarantee returns when A4 ships the trigger. **NOT RECOMMENDED.**<br/>(α) Expand F3a deferral to keep W1 (panel writer) on contract during A3 — reduces A3 cutover to essentially the rejection-log + calibration paths only; panel substrate never actually cuts over until step 20 anyway. Functionally equivalent to (δ) operationally; (δ) is preferred for governance clarity. |

## 13. Hard rule mapping (HR1..HR5)

| Rule | A3 coverage |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | Substrate CHECKs on `bcf.panel_output_record` + `bcf.certification_record` continue to reject synthetic-provider INSERTs after writer cutover (binding; §7.4 + §8.4 probe #208). A3 negative test confirms the CHECK fires for synthetic payloads routed through the new writer (§8.2). |
| **HR2** — MCF evidence belongs in `mcf.*` | A3 does not write to `mcf.*` or `contract.*` from MCF paths. `mcf-cert-writer.service.ts` already targets `mcf.certification_record`; A3 does not modify it. §10.2 / §10.3 explicitly prohibit MCF FK changes. |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.panel_output_record` / `calibration_event` / `certification_record` | A3 enforces HR3 cleanly for `contract.panel_output_record` + `contract.calibration_event` after W1 + W2 cutover (no new BCF writes from the application). For `contract.certification_record`, A3 cuts over the BCF-produced + operator-authored cert paths (W4a: `writeBcfProducedRow` + `writeOperatorAuthoredRow`); the documented F3a / D11(a) / F6α exception is that `writeRegistryShapeRow` (W4b) continues to INSERT Registry-shape BCF-produced cert rows into `contract.certification_record` during A3, paired with `stampTargetRegistryId` (W5) UPDATEs that stamp `target_registry_id` on those same rows. This temporary, operationally-bounded exception preserves production behavior and the existing write-once trigger guarantee on `contract.cert` until §14 step 20 ships the equivalent trigger on `bcf.cert` and flips W4b + W5 (+ R6 + likely R5 + per-shape R4 per F6α). **No MCF metric authority rows are written to `contract.*` at any point** — `mcf-cert-writer.service.ts:834` already targets `mcf.certification_record`, not `contract.certification_record`. HR3's substance (no MCF authority leakage into generic contract evidence tables) is preserved throughout A3 and beyond. |
| **HR4** — tenant result DBs are separate and out of scope | Cutover-PR's CI scripts use `TENANT_DATABASE_URL=` env-var clearing (mirror of A1/A2 pattern); only `DATABASE_URL` (platform DB) is opened. Tenant DB connection count post-apply = 0 (§8.4 implicit). |
| **HR5** — production path; no mocks | All A3 work targets the production code path. Mocks remain confined to unit-test isolation. The MCF service's `mock-` hash-algorithm production guard (per `mcf-cert-writer.service.ts` §7.5 P-3) continues to apply unchanged. |
| **Stance ADR DEC-7f9597 / D423** | Schema-boundary clarity is the entire point of A3 (writer/reader routing made unambiguous). No-synthetic enforcement preserved across the writer flip via HR1 CHECKs. Rollback discipline preserved via pre-A4-only envelope + atomic git revert. Operator authorization for mutating gates: this DBCP authorizes DESIGN only; the cutover-PR's merge gate is SEPARATE. Tenant-results isolation: HR4 substrate-enforced. |

## 14. Sequencing + anchor set

Under the merged Option A path, A3 slots in at step 15 of the boundary DBCP §13 ladder:

1. ~~Boundary DBCP merged~~ — bc-docs-v3 main `6f8cc15`.
2. ~~Operator authorization D1..D11~~ — `70beeb7`.
3. ~~Phase A1 substrate-design DBCP merged~~ — `70beeb7`.
4. ~~Phase A1 apply DBCP merged~~ — `cdc6efa`.
5. ~~Phase A1 scripts merged (PR #134)~~ — bc-core `61f2e02`.
6. ~~Phase A1 dry-run executed~~ — `2026-05-29T02-00-51-885Z`.
7. ~~Phase A1 apply executed~~ — APPLY PASS at `2026-05-29T02-11-41-745Z`; PR #135 evidence at bc-core `09035b8`.
8. ~~Phase A2 migration DBCP merged~~ — bc-docs-v3 `36acb27` (PR #14).
9. ~~Phase A2 scripts merged (PR #136)~~ — bc-core `e07f2b1`.
10. ~~PR #133 cleanup execution-prep hygiene (PR #137)~~ — bc-core `85a93d5`.
11. ~~PR #133 cleanup apply executed~~ — `2026-05-29T04-06-36-221Z`; PR #138 evidence at bc-core `bac8c99`.
12. ~~Phase A2 dry-run re-run (post-#133)~~ — DRY-RUN PASS at `2026-05-29T04-20-27-749Z`; PR #139 evidence at bc-core `ac059e9`.
13. ~~Phase A2 apply executed~~ — APPLY PASS at `2026-05-29T04-33-48-487Z`; PR #140 evidence at bc-core `837ce0c`.
14. **This DBCP (Phase A3 cutover design)** — operator reviews §11 R1..R12 + §12 D1..D11.
15. **Operator authorization of D1..D11** in writing.
16. **bc-core PR — Phase A3 cutover scripts + Drizzle bcf.* schema files + writer/reader import flip** — authored separately; opens with bcf.* Drizzle schemas in commit 1 (no behavior change) + writer/reader flip in commit 2 + tests + dry-run/post-apply scripts; merged after independent review.
17. **Phase A3 dry-run execution** — operator-authorized; verifies §8.3 probes; produces evidence artifacts.
18. **Phase A3 apply gate execution** — ~~operator-authorized; cutover-PR merged + first production runtime cycle observed; §8.4 post-apply assertions evidence.~~ **BLOCKED per §3.5 / R9 (updated) / D11(δ) (PR #144 finding 2026-05-29).** Standalone A3 apply is forbidden because the contract.cert → contract.panel FK breaks once W1 cuts over to bcf. Phase A3 apply is rescheduled as part of step 20-combined atomic apply (renumbered: see step 19+ below).
19. **Phase A3 closeout doc** — `bcf-evidence-schema-phase-a3-cutover-closeout.md` on bc-docs-v3. Closeout is authored AFTER the combined atomic apply succeeds (not after standalone A3, which is forbidden).
20. **§14 step 20 work (authored + reviewed in parallel with PR #144 finding; ships atomically alongside A3 apply per D11(δ)):**
    - (i) **DDL** — adds `trg_certification_record_target_registry_id_guard` to `bcf.certification_record` (mirrors the contract.cert trigger from `docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:221-226`).
    - (ii) **Code — F6α joint-defer set flipped atomically:**
      - **W4b (`writeRegistryShapeRow`)** Drizzle flip to `bcf.certification_record`.
      - **W5 (`stampTargetRegistryId`)** Drizzle flip to `bcf.certification_record`.
      - **R6 (`registry-publication.service.ts`)** Drizzle flip to `bcf.certification_record` — UNCONDITIONAL per F6α.
      - **R5 (`certification-verifier.service.ts`)** default flip; explicit exemption only if cutover-implementation inventory proves the file never resolves Registry-shape cert IDs.
      - **R4 (`registry-provenance.read-repository.ts`)** cert-read path per-shape resolution; flipped, partially flipped (Registry-shape only), or explicitly recorded as continuing dual-shape `contract.cert` reads based on the implementation inventory.
    - (iii) **Post-apply verification** — confirms all flipped writer paths land in `bcf.cert` with write-once enforcement active; R6-style Registry-shape reads (`governanceScope='registry'` filter) successfully retrieve freshly-stamped rows from `bcf.cert`; W1 → W4b FK relationship resolves within `bcf.*` cluster (no cross-schema FK violation).
    - (iv) **Closeout doc** records the final R5 / R4 inclusion decision and any residual `contract.cert` BCF read paths.

    **APPLY MODEL — atomic-pair (locked):** A3 cutover code (already merged) + §14 step 20 work apply as a **single combined operational gate**. No Registry publication may occur between A3 cutover code deployment and §14 step 20 deployment. Two acceptable operational shapes:
    - **(δ.1) Single atomic deploy** — A3 cutover code + step 20 DDL + step 20 code flip ship in one deploy event; one apply gate; one post-apply evidence capture.
    - **(δ.2) Explicitly ordered same-window** — A3 cutover code deploys; § 14 step 20 DDL applies and step 20 code flip deploys in the same operational window with NO Registry publication permitted between events (publication gates locked closed; operator-supervised).

    **Standalone A3 apply explicitly forbidden** per §3.5 / D11(δ).
21. **Phase A4 DBCP + apply** — freeze or retire `contract.*` evidence tables.
22. **Phase A5 DBCP + apply** — `mcf.metric_authoring_panel_output_record` creation; 5 mcf→contract FKs redirected; M12 writer flipped.
23. **M12 first real panel run DBCP** — separately authored.
24. **M12 first real panel run** — operator-authorized.
25. **M12.5 first materialization** — operator-authorized.
26. **M13 first evaluation** — operator-authorized.
27. **M14 opening** — after M13 first evaluation closes.

This DBCP authorizes step 16. Steps 17..19 each require their own operator instruction at their respective gates. Step 20 is an A3 follow-up (DDL slice) gated by D11 deferred resolution.

## 15. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 |
| No DDL applied | ✓ |
| No DML applied | ✓ |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| `bc-postgres` MCP `allow_write=false` throughout (read-only DB probes for §3 baselines) | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No `bcf.*` row mutation | ✓ |
| No tenant `tbc_{slug}_dev` DB connection opened | ✓ |
| PR #133 not modified | ✓ (cleanup apply already executed at `2026-05-29T04-06-36-221Z`; not re-touched) |
| No rollback executed | ✓ |
| No PR #140 re-touch | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured | ✓ |
| Source inventory derived from live bc-core main `837ce0c` Drizzle import grep + INSERT/UPDATE/DELETE grep | ✓ |
| Read-only DB probes against `bc_platform_dev` for §3 row-count baselines | ✓ |
| F1 + F2 + F3a hygiene patch applied per PR #15 review (R7 reclassification to panel reader; R8 intake-queue panel-reader added; W4 split into W4a flip + W4b defer; F3a writer-pair joint defer; §3.4 R-reference corrected R8→R9; cert reader R4/R5/R6 coordination flag added; §4.5 / §5.1 / §5.2 / §6.1 / §6.3 / §8.1 / §11 R9 / §12 D11 / §14 step 20 / §16 consistency updates) | ✓ |
| F4 + F5 + F6α sweep patch applied per second PR #15 review (F4: 16 stale `W1..W4` / `R1..R7` / `W5-only` cross-references swept across §5.3 / §6.4 / §7.2 ×2 / §8.2 ×2 / §8.3 probe #5 / §8.4 probe #207 / §8.5 / §9.2 / §9.5 probes #300/#301 / §11 R2/R3 / §12 D3/D4. F5: §13 HR3 narrative corrected — no longer falsely claims zero BCF-produced cert writes to `contract.cert` post-A3; HR3's spirit preserved via documented W4b/W5 F3a exception bound. F6α: §12 D11 RECOMMENDED tightened to explicit joint-defer set W4b + W5 + R6 unconditional + R5 likely + R4 per-shape; §14 step 20 + §11 R9 + §4.5 + §5.2 + §6.1 + §16 aligned to reflect reader-side coupling) | ✓ |
| PR #144 FK finding correction patch applied (2026-05-29; this edit): bc-core PR #144 integration test harness repair discovered via live SAVEPOINT-isolated test execution that the original F3a / D11(a) deferral set is NOT apply-safe because the contract.cert → contract.panel FK breaks once W1 cuts over to bcf (panel rows in bcf, cert FK looks in contract → violation on every Registry publication). Updated §3.5 (new BLOCKING FINDING section), §11 R9 (extended mitigation), §12 D11 (resolution (a) retired as known-invalid; new resolution (δ) recommended and locked: defer A3 apply until §14 step 20 ships atomically alongside; standalone A3 apply forbidden), §14 step 18 (BLOCKED), §14 step 20 (atomic-pair apply model explicit; W4b + W5 + R6 + R5 + R4 cutover requirements enumerated), §9.4 (rollback envelope must account for combined apply; rollback verifier needs `--mode=*-combined` extension), §16 (added to non-authorized list). No production state was perturbed by PR #144 (Δ DB state = 0; sentinel-rollback worked). Phase A3 apply readiness: BLOCKED until §14 step 20 work is authored and reviewed | ✓ |

## 16. Out-of-scope re-statement

This DBCP is **NOT** Phase A4 / A5 / M-series.

This DBCP does **NOT** authorize bc-core code execution. Authoring the implementation PR is a separately operator-authorized follow-up (step 16 of §14).

This DBCP does **NOT** authorize merging the implementation PR. The cutover-PR's merge gate is SEPARATE operator authorization with apply-gate evidence (§8.3 + §8.4) on the table.

This DBCP does **NOT** authorize any source `contract.*` row deletion. A4 owns freeze/retire.

This DBCP does **NOT** authorize any `bcf.*` row mutation. A3 is code-routing only.

This DBCP does **NOT** authorize MCF FK changes. A5 owns retarget.

This DBCP does **NOT** authorize the W4b `writeRegistryShapeRow` cutover OR the W5 BCR completion-stamp cutover OR the cutover of reader R6 (`registry-publication.service.ts`; unconditionally joint-deferred per F6α). D11(δ) / F3a / F6α + PR #144 finding-corrected resolution defers the joint set **W4b + W5 + R6 (unconditional) + R5 (likely) + R4 (per-shape)** together until a separate DDL + code slice (§14 step 20) ships atomically alongside A3 as a single combined apply gate (the bcf.cert write-once trigger DDL + the joint-defer set flip). The cutover-PR's reader-exposure inventory records the final R5 / R4 inclusion decisions.

This DBCP does **NOT** authorize **standalone Phase A3 apply.** Per §3.5 / R9 updated / D11(δ) (PR #144 finding 2026-05-29), standalone A3 apply would break every Registry publication post-deploy because the contract.cert → contract.panel FK fails when W1 has cut over to bcf. Phase A3 apply is BLOCKED until §14 step 20 work is authored, reviewed, and ready to apply atomically alongside A3 as the single combined operational gate.

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** alter `mcf.*`, `metric.*`, `concept_registry.*`, or any out-of-A3-scope `contract.*` substrate.

This DBCP does **NOT** open M14.

This DBCP does **NOT** open the first real M12 panel run.

---

**End of DBCP. NOT EXECUTED. Operator authorization on §12 D1..D11 required before the bc-core cutover-PR authoring opens.**
