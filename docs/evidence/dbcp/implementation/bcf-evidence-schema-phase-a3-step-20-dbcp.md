---
uid: bcf-evidence-schema-phase-a3-step-20-dbcp
title: BCF Evidence Schema — Phase A3.5 / §14 step 20 DBCP (bcf.cert write-once trigger DDL + W4b/W5/R6/R5/R4-cert atomic flip; atomic-pair with Phase A3 apply per D11(δ))
description: Phase A3.5 / §14 step 20 design DBCP for the atomic-pair slice required by the corrected Phase A3 DBCP §12 D11(δ) (bc-docs-v3 main `21aa442`). Per the PR #144 finding, standalone Phase A3 apply is forbidden because the contract.cert → contract.panel FK breaks once W1 (panel writer) cuts over to bcf. This DBCP designs the step 20 slice that closes the gap: (i) ships the `trg_certification_record_target_registry_id_guard` equivalent on `bcf.certification_record` (DDL); (ii) flips the F3a / F6α joint-defer set (W4b `writeRegistryShapeRow` + W5 `stampTargetRegistryId` + R6 `registry-publication.service.ts` unconditional + R5 `certification-verifier.service.ts` default-flip + R4 cert-read per-shape) to bcf.certification_record; (iii) verifies the W1 → W4b FK relationship resolves within the bcf cluster post-flip. Step 20 ships atomically alongside Phase A3 apply per the (δ.1) or (δ.2) apply model. **NOT EXECUTED.** This DBCP authorizes design only; the bc-core implementation PR is a separately operator-authorized follow-up. **No DDL applied, no DML applied, no Phase A3 apply, no rollback executed, no tenant DB connection, no M11/M12/M12.5/M13 invocation. M14 stays CLOSED.** Operator stance ADR DEC-7f9597 / D423 honoured — schema-boundary clarity restored end-to-end via this slice; rollback discipline preserved via the combined-apply envelope.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a3-step-20-trigger-and-deferral-flip
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A3.5 / §14 step 20 DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> Under the operator-authorized D11(δ) resolution locked at bc-docs-v3 main `21aa442` (Phase A3 DBCP correction PR #16 post-PR-#144 finding), what is the exact design — DDL specification, code-routing flip set, apply model, test/evidence plan, rollback envelope — for the §14 step 20 slice that closes the contract.cert → contract.panel FK breakage by (a) shipping the write-once trigger equivalent on `bcf.certification_record`, (b) flipping the entire F3a / F6α joint-defer set (W4b + W5 + R6 + R5 + R4-cert) from contract.cert to bcf.cert, and (c) restoring writer-side FK integrity by resolving the W1 → W4b panel→cert path entirely within the bcf cluster?

### 1.2 In scope

- **DDL design** — the `trg_certification_record_target_registry_id_guard` equivalent on `bcf.certification_record`: trigger function shape, trigger name, idempotency model, precondition (bcf.cert exists), no changes to contract.* triggers, no cross-schema FK.
- **Code-routing flip set** — atomic flip of W4b `writeRegistryShapeRow` + W5 `stampTargetRegistryId` + R6 `registry-publication.service.ts` (UNCONDITIONAL) + R5 `certification-verifier.service.ts` (default flip unless exemption) + R4 cert-read path (per-shape resolution).
- **Atomic-pair apply model** per D11(δ): (δ.1) single combined deploy/apply event OR (δ.2) explicitly ordered same-window gate with NO Registry publication permitted between events.
- **Test/evidence plan** — static import lockfile extension; trigger existence verification; trigger behavior test in SAVEPOINT-rolled-back transaction; Registry publication integration smoke now expected to pass without FK violation; pre/post DB invariants.
- **Combined rollback plan** per merged DBCP §9.4 update: pre-rollback guards verify A3 + step 20 BOTH applied (or neither); post-rollback assertions include step 20 DDL revert and code-routing revert; bcf.* and contract.* rows preserved; pre-A4 only.
- **Risk register R1..R8** covering partial apply / trigger mismatch / split-brain / Registry publication between events in δ.2 / accidental cross-schema FK / accidental contract.* write post-step20 / rollback after A4.
- **Operator decisions D1..D7** including apply-model choice (δ.1 vs δ.2), authorization for later bc-core DDL/code PR authoring, confirmation of standalone-A3-apply prohibition, A4/A5 / tenant DB / M-series prohibitions.
- Authorization to author the bc-core implementation PR(s) in a follow-up; that PR's apply gate is a SEPARATE operator authorization gated on D11(δ) + (δ.1 / δ.2) selection.

### 1.3 Explicit non-scope

- ❌ **No DDL applied.** This DBCP designs the trigger; the apply gate is a separately operator-authorized follow-up.
- ❌ **No DML applied.** No row mutation on `bcf.*`, `contract.*`, `mcf.*`, `concept_registry.*`, or any tenant DB.
- ❌ **No bc-core code change.** Authoring the implementation PR is a SEPARATE follow-up operator authorization.
- ❌ **No standalone Phase A3 apply.** Forbidden per bc-docs-v3 main `21aa442` § §3.5 + §11 R9 + §12 D11(δ) + §14 step 18 + §16.
- ❌ **No `contract.*` triggers modified.** Step 20 adds a trigger to bcf.cert only; the existing trigger on contract.cert remains in place until A4 freeze/retire owns its removal.
- ❌ **No cross-schema FK.** Per Phase A3 DBCP §6.4 + R10, no FK from `bcf.*` to non-`bcf.*` is added. The step 20 design restores writer-side FK integrity by relocating both the parent (panel) AND the child (Registry-shape cert) writes to bcf — never by adding a cross-schema FK.
- ❌ **No `contract.*` row deletion.** Phase A4 owns freeze/retire.
- ❌ **No `bcf.*` row mutation.** Step 20 is DDL + code-routing; no row writes during the DBCP design or its apply gate (the apply gate verifies the new trigger fires correctly via SAVEPOINT-rolled-back tests, not by committing rows).
- ❌ **No `mcf.*` / `metric.*` / `concept_registry.*` touch.**
- ❌ **No `mcf.*` FK retarget.** Phase A5 owns.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** HR4 substrate-enforced.
- ❌ **No PR #133 / PR #140 / PR #141 / PR #142 / PR #143 / PR #144 re-touch.**
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M14 remains CLOSED.
- ❌ **No re-litigation of Option A.** `bcf.*` is the locked target; `concept_registry.*` is BCR vocabulary and remains untouched.
- ❌ **No bc-admin / bc-portal UI changes.** No HTTP API contract changes.

## 2. Authority

| Artifact | Location | Authority for |
|---|---|---|
| Boundary DBCP (Option A) | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` | Option A target; 5-phase ladder; §13 sequencing |
| Phase A1 substrate-design DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-dbcp.md` @ bc-docs-v3 main `70beeb7` | `bcf.*` column / CHECK / index / FK shape; HR1 substrate enforcement |
| Phase A1 apply DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-apply-dbcp.md` @ bc-docs-v3 main `cdc6efa` | Apply-gate pattern (env-gate + sha256 + single-tx + post-apply assertions) |
| Phase A2 migration DBCP | `docs/implementation/bcf-evidence-schema-phase-a2-migration-dbcp.md` @ bc-docs-v3 main `36acb27` | Insert-copy semantics; byte-pinned rows; 3,568 authority rows migrated |
| Phase A3 cutover DBCP (original) | `docs/implementation/bcf-evidence-schema-phase-a3-writer-reader-cutover-dbcp.md` @ bc-docs-v3 main `d06eeba` | W1..W3 + W4a writer flip; R1..R8 reader flip minus F6α joint-defer subset |
| **Phase A3 DBCP correction (PR #16; D11(δ) locked)** | `docs/implementation/bcf-evidence-schema-phase-a3-writer-reader-cutover-dbcp.md` @ bc-docs-v3 main `21aa442` | §3.5 BLOCKING FINDING; §11 R9 extended; §12 D11(δ) locks atomic-pair apply with this step 20 slice; §14 step 18 BLOCKED; §16 forbids standalone A3 apply |
| Phase A3 implementation (PR #141) | bc-core main `5f7f8fe` | W1..W3 + W4a flip + R1..R8 flip minus F6α joint-defer subset; armed-but-not-applied |
| Phase A3 spec hygiene (PR #142) | bc-core main `e0bdbc6` | panel fixture imports flipped to bcf in 3 integration specs |
| Phase A3 apply/rollback scripts (PR #143) | bc-core main `0a34817` | Post-apply evidence script + rollback verifier (env-gated; standalone-A3 envelope; needs `--mode=*-combined` extension per merged DBCP §9.4) |
| Phase A3 harness repair (PR #144) | bc-core main `68cee3f` | `framework-approval.test-harness.ts` factory + dotenv imports; uncovered the FK finding via live SAVEPOINT-isolated test execution |
| Contract.cert trigger source | `bc-core/docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:188-226` | Authoritative shape for the bcf.cert mirror trigger — function body + trigger declaration |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) @ bc-docs-v3 main `cdc6efa` | Schema-boundary clarity, rollback discipline, operator authorization on mutating gates |
| Hard rules HR1..HR5 | parent boundary DBCP §5 | Substrate constraints step 20 design must respect |
| bc-core anchor (step 20 implementation base) | main `68cee3f0be421bbeaca6f0db23ec5201558facb7` (post-PR-#144 merge) | Code-routing flip targets the step 20 implementation PR will modify |
| bc-docs-v3 anchor (this DBCP base) | main `21aa4422a7cad27e1879eca935024f39e9708aa0` (post-PR-#16 merge) | Governance artifact with D11(δ) locked |

## 3. Problem statement (reproduced from corrected DBCP §3.5)

### 3.1 Failure mode that step 20 closes

Per the merged Phase A3 DBCP correction at bc-docs-v3 main `21aa442` §3.5:

| Step | Action | Substrate landing |
|---|---|---|
| 1 | W1 `PanelOutputRecordRepository.create()` writes a new panel row | `bcf.panel_output_record` (cutover per PR #141) |
| 2 | W4b `CertificationRecordWriteRepository.writeRegistryShapeRow()` writes a Registry-shape cert referencing that `panel_run_uid` | `contract.certification_record` (DEFERRED per F3a / D11(a)) |
| 3 | DB enforces `fk_certification_record__panel_run` (contract.cert.panel_run_uid → contract.panel_output_record.panel_run_uid) | FK lookup in `contract.panel_output_record` |
| 4 | Lookup fails — the panel row is in `bcf.panel_output_record`, not `contract.panel_output_record` | **FK violation; W4b INSERT rejected; production regression on every Registry publication** |

### 3.2 How step 20 closes the gap

Step 20 relocates BOTH the Registry-shape cert writer (W4b) AND its BCR completion-stamp (W5) AND the Registry-shape cert readers (R6 unconditional; R5 default; R4 per-shape) to `bcf.certification_record`. After step 20:

- W1 writes panel to `bcf.panel_output_record`.
- W4b writes Registry-shape cert to `bcf.certification_record`.
- `bcf.certification_record` has its own FK `fk_bcf_certification_record__panel_run` → `bcf.panel_output_record(panel_run_uid)` (added by Phase A1; verified by Phase A1 apply assertion #211).
- FK lookup resolves cleanly within the bcf cluster.
- W5 stamps `target_registry_id` on the bcf-side cert; the new bcf.cert write-once trigger (this step 20's DDL deliverable) enforces the same born-null + single-stamp semantics that contract.cert had.
- R6 reads Registry-shape certs from bcf.cert and finds the W4b-written rows.

The cross-schema dependency is eliminated entirely. No cross-schema FK is added; the cluster separation invariant (R10 / Phase A3 §6.4 / dry-run probe #9) is preserved.

### 3.3 Why W1 cannot revert (option α from D11)

Per D11(δ) lock, option (α) — keep W1 on contract during A3 — is documented as functionally equivalent but reduces A3 to a near-no-op (rejection-log + calibration only). (δ) is preferred for governance clarity: A3 cutover code remains intact; step 20 ships the dependency that A3 lacks; the two apply atomically.

## 4. §14 step 20 deliverables (per merged DBCP §14 step 20)

### 4.1 DDL — `bcf.certification_record` write-once trigger

**Trigger function:** `bcf.tg_certification_record_target_registry_id_guard()`

Mirrors `contract.tg_certification_record_target_registry_id_guard()` at `bc-core/docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:193-219`. Same body (BEFORE INSERT OR UPDATE; rejects Registry-shape rows born with non-null target_registry_id; rejects UPDATE if target_registry_id already non-null; rejects UPDATE if anything other than target_registry_id changed via `to_jsonb(NEW) - 'target_registry_id'` comparison). Only differences: namespace `bcf.` instead of `contract.`; error messages reference the bcf substrate.

**Trigger name:** `trg_certification_record_target_registry_id_guard` (same name as contract-side). PostgreSQL trigger names are scoped to their table; using the same trigger name on `bcf.certification_record` does not collide with the same-named trigger on `contract.certification_record`.

**Trigger declaration:**
```sql
CREATE TRIGGER trg_certification_record_target_registry_id_guard
  BEFORE INSERT OR UPDATE ON bcf.certification_record
  FOR EACH ROW EXECUTE FUNCTION bcf.tg_certification_record_target_registry_id_guard();
```

**Idempotency model:** `CREATE OR REPLACE FUNCTION` + `DROP TRIGGER IF EXISTS` + `CREATE TRIGGER` (matches the contract.cert pattern). Re-applying the DDL is safe.

**Precondition:** `bcf.certification_record` exists (verified by Phase A1 apply at `2026-05-29T02-11-41-745Z`; assertion #207 / probe `bcf_certification_record_exists`).

**Hash anchor (sha256 of planned DDL text):** to be computed by the implementation PR's dry-run script and pinned into the apply gate (mirrors Phase A1 / Phase A2 sha256 chain semantics).

**No changes to contract.* triggers.** The contract.cert trigger remains operational until A4 freeze/retire owns its disposition. During the A3 + step 20 apply window, both triggers coexist; the contract.cert trigger guards the historical rows still in contract.cert (no new INSERTs target contract.cert post-flip), and the bcf.cert trigger guards the W4b + W5 writes that now land in bcf.cert.

### 4.2 Code-routing flip set (F3a / F6α joint-defer set fully relocated)

| Path | File | Pre-step-20 routing | Post-step-20 routing |
|---|---|---|---|
| **W4b** | `src/registry/framework-approval/repositories/certification-record.write.repository.ts` (symbol `writeRegistryShapeRow()`) | contract.certification_record (DEFERRED per F3a) | **bcf.certification_record** |
| **W5** | `src/registry/concept-registry/repositories/certification-stamp.repository.ts` (`stampTargetRegistryId`) | contract.certification_record (DEFERRED per F3a) | **bcf.certification_record** |
| **R6** | `src/registry/registry-authoring-panel/registry-publication.service.ts` (`governanceScope='registry'` filter at line 395-400) | contract.certification_record (DEFERRED per F6α UNCONDITIONAL) | **bcf.certification_record** |
| **R5** | `src/registry/concept-registry/certification-verifier.service.ts` (`verify` by `certificationRecordId` at line 151) | contract.certification_record (DEFERRED per F6α LIKELY) | **bcf.certification_record** (default flip; explicit exemption only if cutover-implementation inventory proves the file never resolves Registry-shape cert IDs) |
| **R4-cert** | `src/registry/registry-authoring-panel/registry-provenance.read-repository.ts` (symbol `findRegistryCert()`) | contract.certification_record (DEFERRED per F6α per-shape) | **bcf.certification_record** (default; the per-shape evaluation may record continued dual-shape contract.cert reads if the cutover-PR's reader-exposure inventory proves a Registry-shape vs other-shape split is required) |

**Mechanics:** Drizzle import flip — `certificationRecord` symbol re-routed from `database/schema/contract` to `database/schema/bcf` in each file. The step 20 implementation PR carries the diff. The W4a + W4b SPLIT alias pattern from PR #141 in `certification-record.write.repository.ts` collapses back to a single `bcf`-side import once W4b joins W4a on bcf.

**Module-boundary lock:** the C5 sole-writer pattern (per PR #141 §4.2 + PR #144 test-harness factory) is preserved — the W4b flip is internal to `framework-approval/`, not crossing the boundary.

### 4.3 Post-step-20 W1 → W4b panel-cert relationship

After step 20:
- W1 inserts new panel rows → `bcf.panel_output_record` (panel_run_uid_X).
- W4b inserts Registry-shape cert → `bcf.certification_record` (panel_run_uid_X referenced).
- FK `fk_bcf_certification_record__panel_run` enforces `bcf.cert.panel_run_uid → bcf.panel_output_record(panel_run_uid)`.
- Lookup resolves within the bcf cluster. **No FK violation. Production regression closed.**

This restores the writer-side FK integrity that the corrected DBCP §3.5 / §11 R9 / §12 D11(δ) identified as broken under standalone A3 apply.

## 5. Atomic-pair apply model (per merged DBCP §14 step 20)

D11(δ) locks the apply model: A3 + step 20 ship as a single combined operational gate. The merged DBCP correction enumerates two acceptable operational shapes; this DBCP's D1 selects between them.

### 5.1 (δ.1) Single atomic deploy — RECOMMENDED

A3 cutover code (already merged at bc-core main `68cee3f`) + step 20 DDL + step 20 code flip ship in **one deploy event**. One apply gate. One post-apply evidence capture.

| Property | Value |
|---|---|
| Number of operational gates | 1 |
| Deployment events | 1 |
| Registry publications between deploys | N/A (no inter-deploy gap exists) |
| Post-apply evidence script | combined: §8 step-20-post-apply or extended Phase A3 post-apply with step 20 invariants |
| Rollback envelope | combined (per merged DBCP §9.4) |

### 5.2 (δ.2) Explicitly ordered same-window — ACCEPTABLE

A3 cutover code deploys; § 14 step 20 DDL applies and step 20 code flip deploys in the **same operational window** with **NO Registry publication permitted between events**. Operator-supervised (e.g., publication gates locked closed for the duration of the window).

| Property | Value |
|---|---|
| Number of operational gates | 2 (A3 apply gate + step 20 apply gate, ordered) |
| Deployment events | 2 (A3 deploy + step 20 deploy) |
| Registry publications between deploys | **FORBIDDEN — operator-enforced** |
| Window length | Minimised; operator-decided based on deployment infrastructure |
| Post-apply evidence script | 2 captures (A3 post-apply + step 20 post-apply); both required for the window to close |
| Rollback envelope | combined (per merged DBCP §9.4); rolling back A3 alone is not a valid state |

### 5.3 Standalone A3 apply explicitly forbidden

Per merged DBCP §3.5 / §11 R9 / §12 D11(δ) / §14 step 18 / §16: no operational shape that applies A3 alone is permitted. This DBCP affirms the forbidden status — step 20 is the missing dependency that A3 needs to be apply-safe.

## 6. DDL design

### 6.1 Trigger function `bcf.tg_certification_record_target_registry_id_guard()`

Mirrors `contract.tg_certification_record_target_registry_id_guard()` body verbatim with namespace substitution. Conceptual SQL (final form pinned by implementation PR's sha256):

```sql
CREATE OR REPLACE FUNCTION bcf.tg_certification_record_target_registry_id_guard()
  RETURNS trigger AS $$
BEGIN
  IF TG_OP = 'INSERT' THEN
    IF NEW.governance_scope = 'registry' AND NEW.target_registry_id IS NOT NULL THEN
      RAISE EXCEPTION
        'bcf.certification_record: a Registry-shape row must be inserted with target_registry_id NULL — F3 stamps it on completion (DEC-02f5a9; Phase A3 step 20 DBCP).';
    END IF;
    RETURN NEW;
  END IF;

  -- TG_OP = 'UPDATE'
  IF OLD.target_registry_id IS NOT NULL THEN
    RAISE EXCEPTION
      'bcf.certification_record.target_registry_id is write-once — it is already set (certification_record_id=%).',
      OLD.certification_record_id;
  END IF;

  IF (to_jsonb(NEW) - 'target_registry_id') IS DISTINCT FROM (to_jsonb(OLD) - 'target_registry_id') THEN
    RAISE EXCEPTION
      'bcf.certification_record is append-only — the only permitted UPDATE is the one-time target_registry_id stamp (certification_record_id=%).',
      OLD.certification_record_id;
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

### 6.2 Trigger declaration

```sql
DROP TRIGGER IF EXISTS trg_certification_record_target_registry_id_guard
  ON bcf.certification_record;

CREATE TRIGGER trg_certification_record_target_registry_id_guard
  BEFORE INSERT OR UPDATE ON bcf.certification_record
  FOR EACH ROW EXECUTE FUNCTION bcf.tg_certification_record_target_registry_id_guard();
```

### 6.3 Idempotency model

- `CREATE OR REPLACE FUNCTION` — re-creating the function is safe.
- `DROP TRIGGER IF EXISTS` + `CREATE TRIGGER` — re-creating the trigger is safe; the trigger binding can be re-bound to the (possibly updated) function.
- Apply gate runs the DDL inside a single transaction; re-runs against the same anchor are no-ops modulo the timestamp.

### 6.4 Precondition

`bcf.certification_record` table exists. Verified at Phase A1 apply at `2026-05-29T02-11-41-745Z` (PR #135 evidence). The implementation PR's dry-run probes confirm pre-apply.

### 6.5 No changes to `contract.*` triggers

The existing `trg_certification_record_target_registry_id_guard` on `contract.certification_record` remains operational. It continues to guard the historical rows in contract.cert (which receive no new INSERTs post-step-20; only the existing pre-A3 row population). Phase A4 owns the eventual freeze/retire of the contract.cert trigger alongside the contract.cert table.

### 6.6 No cross-schema FK

Cluster separation invariant preserved. The post-step-20 W4b → bcf.cert path FKs the panel_run_uid to `bcf.panel_output_record` via the existing `fk_bcf_certification_record__panel_run` (Phase A1; verified by A1 apply assertion #211). No new FK from bcf to non-bcf is introduced.

## 7. Test/evidence plan

### 7.1 Static import lockfile extension

The Phase A3 import lockfile (`scripts/bcf-phase-a3-import-lockfile.mjs`; 13 assertions per merged Phase A3 DBCP §8.1) is extended for step 20:

| New / updated assertion | Scope |
|---|---|
| W4b `writeRegistryShapeRow` import flipped to bcf | Production source — `.insert(certificationRecordContract)` inside `writeRegistryShapeRow()` must flip to the bcf-side `certificationRecord` symbol (the W4a+W4b dual-alias pattern from PR #141 collapses to a single bcf-side import once W4b joins W4a on bcf) |
| W5 `stampTargetRegistryId` import flipped to bcf | Production source — `.update(certificationRecord)` at line 48 must target the bcf-side symbol |
| R6 `registry-publication.service.ts` import flipped to bcf | Production source — `.from(certificationRecord)` at line 395 must target the bcf-side symbol |
| R5 `certification-verifier.service.ts` import flipped to bcf (default; explicit exemption record allowed) | Production source — `.from(certificationRecord)` at line 151 must target bcf unless the implementation PR's reader-exposure inventory records an exemption |
| R4 cert-read path flipped to bcf (per-shape; closeout doc records final treatment) | Production source — the `.from(certificationRecord)` site inside `findRegistryCert()`; the per-shape evaluation result is closeout-documented |
| Step 20 documented exception list size: **exactly 0** (the F3a / F6α joint-defer set is fully flipped) | Documented exception list — A3's 2-site exception (W4b + W5) is eliminated by step 20 |

The implementation PR ships an updated lockfile (or a new step 20-specific lockfile) that enforces these assertions.

### 7.2 Trigger existence verification

A post-apply probe verifies the trigger is installed on bcf.certification_record:

```sql
SELECT count(*) FROM information_schema.triggers
WHERE trigger_schema = 'bcf'
  AND event_object_table = 'certification_record'
  AND trigger_name = 'trg_certification_record_target_registry_id_guard';
-- Expected: 1
```

A second probe verifies the function exists:

```sql
SELECT count(*) FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE n.nspname = 'bcf' AND p.proname = 'tg_certification_record_target_registry_id_guard';
-- Expected: 1
```

### 7.3 Trigger behavior test (SAVEPOINT-rolled-back)

Three behavior assertions, run inside a SAVEPOINT-rolled-back transaction (no durable rows):

1. **INSERT with target_registry_id non-null on Registry-shape row** — must RAISE EXCEPTION. (Caller catches and rolls back; assertion passes.)
2. **UPDATE on already-stamped target_registry_id** — must RAISE EXCEPTION. (Caller catches and rolls back; assertion passes.)
3. **UPDATE on something other than target_registry_id** — must RAISE EXCEPTION. (Caller catches and rolls back; assertion passes.)
4. **UPDATE on target_registry_id (NULL → non-NULL one-time)** — must SUCCEED. (Caller commits the savepoint, then rolls back the outer transaction.)

These tests verify the trigger function body mirrors the contract.cert behavior verbatim. Implementation PR ships them as a new integration spec or extends an existing spec.

### 7.4 Registry publication integration smoke now expected to pass

The PR #144-merged `registry-authoring.integration.spec.ts` smoke (which currently FAILs with `fk_certification_record__panel_run` violation) is expected to PASS post-step-20. The implementation PR re-runs the smoke as evidence (SAVEPOINT-rolled-back per the documented sentinel pattern; Δ DB state = 0 verified post-test).

### 7.5 Pre/post DB invariants

Pre-step-20-apply (post-A3-merge baseline at bc-core main `68cee3f`):
- `bcf.*` panel/rej/cal/cert: 19 / 0 / 19 / 3530
- `contract.*` panel/rej/cal/cert: 19 / 0 / 19 / 3530
- `mcf.certification_record`: 0 rows, and no MCF tables structurally related to step 20 are touched (HR2 substrate-enforced; `mcf.*` writes remain confined to existing MCF authority paths)
- `concept_registry.*` total rows: 68
- Synthetic counts: 0 / 0 / 0 / 0
- Cross-schema FKs from bcf.*: 0
- bcf.cert write-once trigger present: NO (added by step 20)

Post-step-20-apply expected:
- All row counts unchanged (DDL + code-routing only; no row mutation)
- bcf.cert write-once trigger present: YES (`count(*) = 1` via probe in §7.2)
- bcf.cert function present: YES (`count(*) = 1` via probe in §7.2)
- Cross-schema FKs from bcf.*: still 0
- Step 20 import lockfile: PASS (all 5 new / updated assertions PASS)
- Pre-existing Phase A3 import lockfile: still PASS (the 2 documented exception sites collapse to 0 post-step-20; the lockfile is updated correspondingly)

### 7.6 Combined-apply evidence script

The implementation PR ships `scripts/bcf-evidence-schema-phase-a3-step-20-post-apply.mjs` (or extends the existing Phase A3 post-apply script with an `--include-step-20` flag) that captures:
- Trigger + function existence (§7.2)
- Trigger behavior verification (§7.3 in SAVEPOINT-rolled-back transactions)
- Integration smoke result (§7.4 — PASS expected)
- DB invariants (§7.5)
- Step 20 import lockfile result (§7.1)

Env-gate mirrors Phase A1 / A2 / A3 patterns: `BCCORE_BCF_PHASE_A3_STEP_20_APPLY_CONFIRM=I_HAVE_REVIEWED_APPLY_<ts>`.

## 8. Rollback plan

### 8.1 Combined rollback model (per merged DBCP §9.4)

A3 + step 20 rollback unwinds BOTH slices. Partial-apply state is not a valid starting point for rollback (per merged DBCP §9.4 update).

**Rollback action** = `git revert <step-20-implementation-PR-squash-commit-sha>` AND `git revert <PR-#141-A3-cutover-PR-squash-commit-sha>` (or the equivalent atomic-revert PR that bundles both reverts) AND a DDL revert for the bcf.cert write-once trigger.

### 8.2 Pre-rollback guards (combined)

The combined rollback verifier (extension of `scripts/bcf-evidence-schema-phase-a3-rollback.mjs` per merged DBCP §9.4; new mode `--mode=pre-rollback-combined`) checks:

| Guard | Code | Description |
|---|---|---|
| 1 | `a3_step_20_rollback_phase_a4_not_shipped` | `contract.*` BCF evidence tables are writable; no A4 freeze trigger / REVOKE detected |
| 2 | `a3_step_20_rollback_contract_rows_intact` | `contract.*` row counts unchanged from post-A2 baseline (19/0/19/3530) plus any W4b inserts that landed pre-step-20 (operationally bounded; should be 0 if step 20 shipped atomically with A3) |
| 3 | `a3_step_20_rollback_bcf_rows_present` | `bcf.*` rows present and not deleted (rollback does NOT delete bcf.*) |
| 4 | `a3_step_20_rollback_both_or_neither_applied` | A3 cutover code + step 20 DDL + step 20 code routing have all been applied; partial-apply state is invalid |
| 5 | `a3_step_20_rollback_env_gate_present` | `BCCORE_BCF_PHASE_A3_STEP_20_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_<ts>` env var set |

### 8.3 Post-rollback assertions (combined)

After the operator's manual `git revert` + DDL revert:

| # | Probe | Expected |
|---|---|---|
| 1 | `step_20_writer_imports_reverted_to_contract` | W4b + W5 import paths revert to contract; (W1..W3 + W4a revert via the A3 revert) |
| 2 | `step_20_reader_imports_reverted_to_contract` | R6 + R5 + R4-cert revert to contract; (R1..R3 + R7 + R8 + R4-panel revert via the A3 revert) |
| 3 | `bcf_cert_trigger_dropped` | `trg_certification_record_target_registry_id_guard` on bcf.certification_record absent (DDL revert applied) |
| 4 | `bcf_cert_function_dropped` | `bcf.tg_certification_record_target_registry_id_guard` function absent |
| 5 | `bcf_rows_preserved` | bcf.* row counts unchanged from pre-rollback (rollback does NOT delete bcf rows) |
| 6 | `contract_rows_preserved` | contract.* row counts unchanged (no rows added or removed by rollback; W4b inserts that landed during the apply window remain — they're now orphaned post-revert because W4b stops writing to contract, but the historical rows are intact) |
| 7 | `contract_cert_trigger_unchanged` | The contract-side `trg_certification_record_target_registry_id_guard` is still operational (this DBCP did not modify it) |
| 8 | `mcf_and_concept_registry_untouched` | mcf.* + concept_registry.* untouched |

### 8.4 Pre-A4 only

Per merged DBCP §9.1 + §9.4: A3 + step 20 rollback is valid only while `contract.*` retains the A2-migrated rows and is writable. Once A4 freezes `contract.*`, A3 + step 20 rollback is no longer meaningful (the application cannot route writes back to `contract.*` because the substrate no longer accepts them). A4 DBCP will own its own restore plan.

### 8.5 bcf.* rows preserved

A3 + step 20 rollback restores code routing + drops the bcf.cert trigger. It does **not** delete bcf.* rows. The 3,568 A2-migrated rows + any post-A3-apply bcf-side writes remain in place.

### 8.6 contract.* rows preserved

A3 + step 20 rollback does **not** delete contract.* rows. Any rows that landed in contract.cert via W4b during a partial-apply window (which should be 0 under δ.1 single-deploy; bounded by the operator-supervised window under δ.2) remain in place — they're orphaned post-rollback but not destroyed.

## 9. Risk register

| # | Risk | Mitigation |
|---|---|---|
| R1 | **Partial apply** — A3 cutover code deployed but step 20 not applied (or vice versa) → contract.cert FK violation on every Registry publication during the window | (δ.1) single-deploy: no inter-deploy gap exists. (δ.2) ordered same-window: operator-supervised gate locks Registry publication closed. Combined-apply rollback verifier (§8.2 guard #4) refuses rollback from partial-apply state |
| R2 | **Trigger mismatch from contract version** — the bcf.cert trigger function body diverges from the contract.cert source | DDL design (§6.1) mirrors `contract.tg_certification_record_target_registry_id_guard()` verbatim except namespace + error message. Implementation PR's dry-run script computes sha256 of the planned DDL text and pins it against the apply gate; any drift fails the apply |
| R3 | **Reader/writer split-brain** — a reader (R5/R4-cert) flips to bcf while a writer (W4b/W5) stays on contract (or vice versa) | Step 20 implementation PR flips the entire F6α joint-defer set atomically in a single commit; lockfile (§7.1) asserts the post-step-20 state with `Step 20 documented exception list size: 0` |
| R4 | **Registry publication between events in δ.2** — if (δ.2) ordered same-window is chosen and a publication slips through between A3 apply and step 20 apply | Operator-enforced publication gate. The step 20 deliverables list (§4) explicitly notes the requirement. Implementation PR's apply gate documentation reiterates the constraint. **(δ.1) single-deploy eliminates this risk entirely and is preferred** |
| R5 | **Accidental cross-schema FK** — the step 20 implementation PR introduces a contract → bcf FK (or vice versa) → violates cluster separation | Implementation PR's CI lockfile + the existing R10 cross-schema-FK-zero invariant probe (Phase A3 dry-run probe #9; post-apply probe #210) detect any cross-schema FK and fail the gate |
| R6 | **Accidental contract.* write after step 20** — a writer left pointing at contract.cert after step 20 cutover continues to create rows the readers (now on bcf.cert) cannot see | Lockfile (§7.1) `Step 20 documented exception list size: exactly 0` — any remaining contract-side BCF cert write site fails the lockfile. The R2 (Phase A3 §11 R2) writer split-brain pattern still applies; step 20 just expands the no-split-brain scope to include W4b + W5 |
| R7 | **Rollback after A4** — operator attempts A3 + step 20 rollback after A4 has shipped, expecting routing-back-to-contract to work; in reality contract.* is frozen | Combined-apply rollback guard #1 (`a3_step_20_rollback_phase_a4_not_shipped`) refuses rollback if A4 freeze artifacts are detected. A4 DBCP must own its own restore plan |
| R8 | **Tenant DB leakage** — implementation PR's CI inadvertently connects to a tenant DB | HR4 substrate-enforced (mirror of A1/A2/A3 pattern: `TENANT_DATABASE_URL=` cleared at invocation; only `DATABASE_URL` opened) |
| R9 | **Trigger fires unexpectedly on the 3,530 A2-migrated rows** — when the bcf.cert trigger is created on a table that already contains rows, future UPDATEs against those historical rows must satisfy the trigger's append-only rule | The 3,530 A2-migrated Registry-shape rows already have `target_registry_id` populated (they're historical post-stamp rows). The trigger's UPDATE branch correctly recognizes these as already-stamped and rejects re-stamping (its intended behavior). No false rejections. Verified by §7.3 trigger behavior assertion #2 |
| R10 | **HR1 substrate CHECK skew** — the bcf.cert no-synthetic CHECK (Phase A1 substrate) remains binding across the W4b flip | Lockfile (§7.1) preserved. HR1 substrate CHECK fires defense-in-depth on any synthetic payload routed to bcf.cert post-step-20 (mirror of Phase A3 §7.4) |

## 10. Operator decisions

| # | Decision | Recommended | Options |
|---|---|---|---|
| **D1** | **Apply model — δ.1 single-deploy or δ.2 ordered same-window** | **δ.1 single-deploy** — eliminates R4 (Registry publication between events) entirely; one apply gate; cleanest governance trail | (δ.1) single-deploy / (δ.2) ordered same-window with operator-enforced publication gate |
| **D2** | Authorize later **bc-core DDL/code PR authoring** (not execution) | **YES** | YES (the implementation PR can be authored; merge gate is SEPARATE operator authorization) / NO (re-scope) |
| **D3** | Confirm **no standalone A3 apply** | **YES** | YES (forbidden per merged DBCP §3.5 / §11 R9 / §12 D11(δ) / §14 step 18 / §16) / NO (re-scope — would require unwinding the merged DBCP correction) |
| **D4** | Confirm **no A4 / A5 work in step 20** | **YES** | YES (A4 owns contract freeze/retire; A5 owns MCF FK retarget) / NO (re-scope) |
| **D5** | Confirm **no tenant DB work** | **YES** | YES (HR4 substrate-enforced) / NO (re-scope) |
| **D6** | Confirm **M14 remains CLOSED** | **YES** | YES (M14 stays CLOSED throughout step 20) / NO (re-scope) |
| **D7** | Confirm **R4-cert per-shape resolution + R5 default-flip semantics** | **YES** — R5 default-flip unless implementation inventory exempts; R4-cert per-shape resolution documented in closeout doc | YES / NO (re-scope) |

## 11. Hard rule mapping (HR1..HR5)

| Rule | Step 20 coverage |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | Substrate CHECKs on `bcf.certification_record` (added by A1) continue to reject synthetic-provider INSERTs after the W4b/W5 flip. The new bcf.cert write-once trigger is an additional defense-in-depth layer (write-once on target_registry_id; append-only on everything else) |
| **HR2** — MCF evidence belongs in `mcf.*` | Step 20 does not write to `mcf.*` or `contract.*` from MCF paths. `mcf-cert-writer.service.ts` already targets `mcf.certification_record`; step 20 does not modify it |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.panel_output_record` / `calibration_event` / `certification_record` | Step 20 eliminates the F3a documented exception (W4b Registry-shape cert writes to contract.cert) by flipping W4b to bcf.cert. Post-step-20, the `contract.certification_record` receives ZERO new BCF authority writes. HR3 substance fully achieved (no MCF authority leakage; no BCF authority leakage either) |
| **HR4** — tenant result DBs are separate and out of scope | Implementation PR's CI scripts use `TENANT_DATABASE_URL=` env-var clearing (mirror of A1/A2/A3 pattern); only `DATABASE_URL` (platform DB) is opened. Tenant DB connection count post-apply = 0 |
| **HR5** — production path; no mocks | All step 20 work targets the production code path. Trigger DDL applies to the live bcf.certification_record substrate. Mocks remain confined to unit-test isolation |
| **Stance ADR DEC-7f9597 / D423** | Schema-boundary clarity restored end-to-end via the W4b/W5/R6/R5/R4-cert flip. Rollback discipline preserved via combined-apply envelope (§8). Operator authorization for mutating gates: this DBCP authorizes DESIGN only; the implementation PR's apply gate is SEPARATE. Tenant-results isolation: HR4 substrate-enforced |

## 12. Sequencing + anchor set

Under the merged Option A + corrected D11(δ) path, step 20 slots in immediately after the merged Phase A3 implementation chain:

1. ~~Boundary DBCP merged~~ — bc-docs-v3 main `6f8cc15`.
2. ~~Phase A1 / A2 chain~~ — completed.
3. ~~Phase A3 cutover DBCP (PR #15 + PR #16 correction)~~ — bc-docs-v3 main `21aa442`.
4. ~~Phase A3 implementation chain (PR #141 + #142 + #143 + #144)~~ — bc-core main `68cee3f`.
5. **This DBCP (Phase A3.5 / §14 step 20 design)** — operator reviews §9 R1..R10 + §10 D1..D7.
6. **Operator authorization of D1..D7** in writing.
7. **bc-core PR — step 20 implementation** — authored separately; opens with the bcf.cert trigger DDL + F3a/F6α joint-defer set flip + lockfile extension + post-apply evidence script + combined-rollback verifier extension; merged after independent review.
8. **Combined dry-run execution** — operator-authorized; verifies pre-apply substrate state + step 20 import-lockfile + trigger absence (expected before apply).
9. **Combined-apply gate execution** (δ.1 single-deploy OR δ.2 ordered same-window) — operator-authorized; ships A3 cutover code + step 20 DDL + step 20 code flip atomically; captures combined post-apply evidence per §7.6.
10. **Phase A3 + step 20 closeout doc** — `bcf-evidence-schema-phase-a3-step-20-closeout.md` on bc-docs-v3; records R5 / R4 final inclusion decisions + integration smoke pass evidence.
11. **Phase A4 DBCP + apply** — freeze or retire `contract.*` evidence tables (including the contract.cert trigger).
12. **Phase A5 DBCP + apply** — `mcf.metric_authoring_panel_output_record` creation; 5 mcf→contract FKs redirected; M12 writer flipped.
13. **M-series gates** — separately authored per existing Phase A3 §14 step 23-27 sequencing.

This DBCP authorizes step 7. Steps 8..10 each require their own operator instruction at their respective gates.

## 13. Discipline assertions (this DBCP-author session)

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — DBCP file lands only in bc-docs-v3 |
| No DDL applied | ✓ — DDL designed only |
| No DML applied | ✓ |
| No Phase A3 apply executed | ✓ — gated on D11(δ) atomic-pair model + future operator authorization |
| No M11 / M12 / M12.5 / M13 / M14 invocation | ✓ |
| No `mcf.*` touched | ✓ |
| No `metric.*` touched | ✓ |
| No `contract.*` row mutation | ✓ |
| No `bcf.*` row mutation | ✓ |
| No `concept_registry.*` touched | ✓ |
| No tenant `tbc_{slug}_dev` DB connection | ✓ |
| No PR #141 / #142 / #143 / #144 re-touch | ✓ |
| No PR #15 / #16 re-touch (DBCP correction already shipped at `21aa442`) | ✓ |
| Operator stance ADR DEC-7f9597 / D423 honoured | ✓ |
| Source DDL anchor (`contract.tg_certification_record_target_registry_id_guard()`) read from authoritative location (`bc-core/docker/redesign/migrations/20260521-phase-a-bucket-1-governance-scope-alignment.sql:188-226`) | ✓ |
| Read-only inspection of merged Phase A3 DBCP `21aa442` for §3.5 / §11 R9 / §12 D11(δ) / §14 step 18+20 anchors | ✓ |

## 14. Out-of-scope re-statement

This DBCP is **NOT** Phase A4 / A5 / M-series.

This DBCP does **NOT** authorize bc-core code execution. Authoring the implementation PR is a separately operator-authorized follow-up (step 7 of §12).

This DBCP does **NOT** authorize merging the implementation PR. The implementation PR's merge gate is SEPARATE operator authorization with apply-gate evidence on the table.

This DBCP does **NOT** authorize any source `contract.*` row deletion. A4 owns freeze/retire.

This DBCP does **NOT** authorize any `bcf.*` row mutation. Step 20 is DDL + code-routing only.

This DBCP does **NOT** authorize MCF FK changes. A5 owns retarget.

This DBCP does **NOT** authorize standalone Phase A3 apply. Per the merged Phase A3 DBCP correction at `21aa442` §3.5 / §11 R9 / §12 D11(δ) / §14 step 18 / §16, standalone A3 apply is forbidden. Step 20 is the atomic-pair partner that closes the apply-readiness gap.

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** alter `mcf.*`, `metric.*`, `concept_registry.*`, or any out-of-A3-scope `contract.*` substrate.

This DBCP does **NOT** open M14.

This DBCP does **NOT** open the first real M12 panel run.

---

**End of DBCP. NOT EXECUTED. Operator authorization on §10 D1..D7 required before the bc-core step 20 implementation PR authoring opens.**
