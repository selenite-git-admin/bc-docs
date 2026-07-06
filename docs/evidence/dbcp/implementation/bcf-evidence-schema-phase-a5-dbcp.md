---
uid: bcf-evidence-schema-phase-a5-dbcp
title: BCF Evidence Schema — Phase A5 DBCP (mcf→contract FK retarget + M12 writer flip; M14 unblock preparation)
description: Phase A5 design DBCP for the disposition of the 5 cross-schema `mcf.*` → `contract.panel_output_record` foreign keys (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`) and the first-real-MCF-authority-writer (M12) code path, after the completed Phase A4 F4+C2 freeze ship event at apply-ts `2026-05-29T11-21-03-131Z` (bc-docs-v3 main `757071a`; bc-core main `6a8a67a`). Enumerates the substrate state post-A4 (4 `contract.*` BCF evidence tables FROZEN by 12 deny-write triggers + 4 functions; `contract.cert` born-null/write-once trigger + function DROPPED per C2; `bcf.cert` write-once trigger LIVE; bcf + contract rows 19/0/19/3530 each; `mcf.certification_record` = 0; `mcf.*` panel_run_uid columns all NULL; 5 mcf→contract FKs preserved unchanged); the four candidate retarget mechanics (single-tx-atomic / phased-per-FK / event-trigger-deferred / shadow-with-cutover); the four candidate M12 writer flip approaches (greenfield writer / extend M4 path / dedicated M12 service / progressive enable); the recommended single-tx-atomic + greenfield-M12-writer strategy; the M14 unblock decision (Option α prepare-only vs Option β include-unblock-conditions); the inventory required to inform operator decisions; the test/evidence plan; the rollback envelope with explicit A5 cliff; the risk register R1..R12 and operator decisions D1..D12. **NOT EXECUTED.** This DBCP authorizes design only; the bc-core implementation PR is a separately operator-authorized follow-up. **No DDL applied, no DML applied, no Phase A5 apply, no rollback executed, no tenant DB connection, no M-series invocation. M14 stays CLOSED. M12 writer NOT activated.** Operator stance ADR DEC-7f9597 / D423 honoured — operator authorization on mutating gates; rollback discipline preserved; substrate-boundary clarity maintained.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: bcf-evidence-schema-phase-a5-mcf-fk-retarget-and-m12-writer-flip
supersedes:
superseded_by:
---

# BCF Evidence Schema — Phase A5 DBCP (mcf→contract FK retarget + M12 writer flip; M14 unblock preparation)

## 1. Scope

### 1.1 Question this DBCP answers

> The Phase A4 F4+C2 freeze shipped at apply-ts `2026-05-29T11-21-03-131Z`, anchored in evidence at bc-core main `6a8a67a` (PR #150) and closed out at bc-docs-v3 main `757071a` (PR #20). The 4 `contract.*` BCF evidence tables are now structurally frozen by 12 deny-write triggers + 4 functions; the `contract.cert` born-null/write-once trigger + function are DROPPED per D5 C2; the `bcf.cert` write-once trigger is preserved LIVE; bcf + contract row counts remain at 19/0/19/3530 each. Five cross-schema `mcf.*` → `contract.panel_output_record` FKs (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`) still reference the frozen `contract.panel_output_record` — A4 explicitly deferred their retarget to A5. What is the correct Phase A5 disposition for (a) the 5 cross-schema mcf→contract FKs (retarget mechanics + post-retarget verification + rollback envelope), (b) the M12 first-real-MCF-authority-writer code path (writer flip approach + smoke gating), and (c) the M14 unblock decision (does A5 merely prepare the M14 gate or propose unblock conditions), given that mcf.* rows are currently 0 and `bcf.panel_output_record` has the same 19 `panel_run_uid` values as `contract.panel_output_record` (full overlap)?

### 1.2 In scope

- **Inventory of the current substrate state post-A4** — bcf.* + contract.* + mcf.* row counts; the 12 contract.* deny-write triggers + 4 deny-write functions LIVE; the dropped contract.cert born-null/write-once trigger + function; the LIVE bcf.cert write-once trigger; the 9 inbound FKs on `contract.panel_output_record` (3 intra-contract sibling + 1 contract.intake_queue + 5 cross-schema mcf→contract); the panel_run_uid overlap (19 / 19 / 19 = full overlap).
- **Inventory of source-code references** — production source files (`src/registry/`), test specs, scripts (`scripts/`), and migration SQL (`docker/redesign/migrations/`) that reference `contract.panel_output_record` from mcf-side child tables — to detect any hidden reader/writer code path that would break under FK retarget.
- **FK retarget mechanics options** — single-transaction atomic retarget of all 5 FKs / phased per-FK retarget / event-trigger-deferred retarget with online checkpoint / shadow-with-cutover model.
- **M12 writer flip options** — greenfield writer (new mcf-targeted service) / extend M4 path (re-host M4 logic on mcf substrate) / dedicated M12 service (clean separation; lifecycle owned by M-series) / progressive enable (feature-flag-gated rollout per metric or tenant).
- **M14 unblock decision** — Option α prepare-only (A5 = pure FK retarget + M12 writer code path; M14 unblock is a separate gate); Option β include-unblock-conditions (A5 designs M14 unblock prerequisites + smoke evidence + observation criteria).
- **Recommendation** — operator-presented; preserves A4 freeze invariants; retains the contract.* read-only archive; clears the boundary DBCP A5 obligation; respects M-series gate discipline.
- **Verification plan** — A4 freeze invariant probes (12 deny-write triggers + 4 functions present; rows unchanged); FK inventory before/after (5 mcf FKs targeting bcf post-retarget); panel_run_uid overlap probe; M12 writer dry-run probe (read-only DB introspection of expected writer SQL shape).
- **Rollback envelope** — A5 pre-rollback / post-rollback verifier; explicit cliff at first real M12 panel run; combined A4 + A5 rollback impossibility once mcf.* has rows that have no contract.* counterpart.
- **Risk register R1..R12** + **operator decisions D1..D12**.
- **Test/evidence plan** — static lockfile extension; DB FK inventory + row-count invariants; no synthetic data; no tenant DB; M12 writer smoke only if explicitly authorized later.
- **Relationship to first real M12 panel run** — what remains after A5 before the first real run; what evidence must be captured before the run.
- Authorization to author the bc-core implementation PR(s) in a follow-up; that PR's apply gate is a SEPARATE operator authorization.

### 1.3 Explicit non-scope

- ❌ **No DDL applied.** This DBCP designs the FK retarget + M12 writer flip; the apply gate is a separately operator-authorized follow-up.
- ❌ **No DML applied.** No row mutation on `bcf.*` / `contract.*` / `mcf.*` / `concept_registry.*` / any tenant DB.
- ❌ **No bc-core code change.** Authoring the implementation PR is a SEPARATE follow-up operator authorization.
- ❌ **No Phase A4 rollback executed.** The A4 rollback envelope remains available pre-A5-apply. **A5-apply changes that — A5-apply invalidates A4 rollback.**
- ❌ **No `contract.*` row mutation.** Even if A4 rollback were executed first, A5 does not mutate contract.* rows.
- ❌ **No `bcf.*` row mutation.** A5 retargets FKs and prepares writer code; no rows are inserted/updated/deleted on bcf.*.
- ❌ **No M11 / M12 / M12.5 / M13 invocation.** M12 writer code is implemented; not invoked.
- ❌ **M14 remains CLOSED.** A5 either prepares the gate (Option α) or designs unblock conditions (Option β) — but does not open M14.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** HR4 substrate-enforced.
- ❌ **No first real M12 panel run.** That is a SEPARATE operator-authorized post-A5 gate.
- ❌ **No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 / #148 / #149 / #150 re-touch.**
- ❌ **No PR #15 / #16 / #17 / #18 / #19 / #20 re-touch.**
- ❌ **No re-litigation of Option A.** `bcf.*` is the locked target; `concept_registry.*` is BCR vocabulary and remains untouched.
- ❌ **No bc-admin / bc-portal UI changes.** No HTTP API contract changes (M-series gates remain CLOSED).
- ❌ **No post-A5 DROP slice.** The F4 HYBRID post-A5 DROP of `contract.*` BCF evidence tables is a SEPARATE post-A5 governance gate (per Phase A4 DBCP §6).

## 2. Authority anchor chain

| Artifact | Location | Authority for |
|---|---|---|
| **Boundary DBCP (Option A)** | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` (PR #11) | Option A target; 5-phase ladder; A5 sits as the FK retarget + M12 writer flip phase |
| Phase A1 substrate-design DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-dbcp.md` @ bc-docs-v3 main | `bcf.*` column / CHECK / index / FK shape; HR1 substrate enforcement |
| Phase A1 apply DBCP | `docs/implementation/bcf-evidence-schema-phase-a1-apply-dbcp.md` @ bc-docs-v3 main | Apply-gate pattern (env-gate + sha256 + single-tx + post-apply assertions) |
| Phase A2 migration DBCP | `docs/implementation/bcf-evidence-schema-phase-a2-migration-dbcp.md` @ bc-docs-v3 main | Byte-pinned insert-copy; 3,568 authority rows migrated; panel_run_uid value overlap preserved |
| Phase A3 cutover DBCPs (original + correction) | `docs/implementation/bcf-evidence-schema-phase-a3-writer-reader-cutover-dbcp.md` @ bc-docs-v3 main | W1..W3 + W4a writer flip; R1..R8 reader flip; D11(δ) atomic-pair lock with step 20 |
| Phase A3 + §14 step 20 closeout | `docs/implementation/bcf-evidence-schema-phase-a3-step-20-closeout.md` @ bc-docs-v3 main `5757936` (PR #18) | Combined A3+step20 apply event; F3a/F6α joint-defer set fully flipped |
| **Phase A4 DBCP (D1..D10)** | `docs/implementation/bcf-evidence-schema-phase-a4-dbcp.md` @ bc-docs-v3 main `dbc0378` (PR #19) | F4 HYBRID disposition; C2 REPLACE on contract.cert trigger; D9 combined-rollback-invalidation policy; A5 retarget scope explicit |
| **Phase A4 closeout** | `docs/implementation/bcf-evidence-schema-phase-a4-closeout.md` @ bc-docs-v3 main `757071a` (PR #20) | Ship event record; substrate final state; D9 rollback-policy state change recorded; F4 HYBRID post-A5 DROP roadmap deferred; **A5 is the next gate** |
| Phase A4 implementation (PR #148) | bc-core main `ebfb61a` | 5 new scripts (DDL synth + dry-run + apply + post-apply + rollback verifier); lockfile 25/25 PASS; D6 retirement; D7 fixture flip |
| Phase A4 dry-run + sha256 pin (PR #149) | bc-core main `0f3093b` | dry-run timestamp + sha256 `6905973983bbf2836ff4ca8972136fb46c29079b329d37bb15f06a4ff60f885a` |
| Phase A4 apply + post-apply (PR #150) | bc-core main `6a8a67a` | apply-ts `2026-05-29T11-21-03-131Z`; post-apply-ts `2026-05-29T11-21-13-074Z`; 10/10 apply + 10/10 post-apply PASS |
| **bc-docs-v3 anchor (this DBCP base)** | bc-docs-v3 main `757071ac684964dbd2986dab4c7384d963a962cd` (post-PR-#20 merge) | Governance audit trail with full A1..A4 ship loop closed; A5 is the next gate |
| bc-core anchor (A5 implementation base) | bc-core main `6a8a67a11e77751f7ad3e71a7d0ebadc8f5e2f2a` | Code state the future A5 implementation PR will modify |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) | Schema-boundary clarity, rollback discipline, operator authorization on mutating gates |
| Hard rules HR1..HR5 | parent boundary DBCP §5 | Substrate constraints A5 design must respect |

## 3. Current substrate state (verified live post-A4)

### 3.1 Row counts

Verified via `bc-postgres` MCP read-only queries at A5-DBCP-authoring time:

| Table | Rows | Notes |
|---|---|---|
| `bcf.panel_output_record` | **19** | A2-migrated authority rows; live BCF writer continues to write here post-A3 |
| `bcf.authoring_panel_rejection_log` | **0** | A2 baseline; no historical rejections |
| `bcf.calibration_event` | **19** | A2-migrated authority rows |
| `bcf.certification_record` | **3530** | A2-migrated authority rows |
| `contract.panel_output_record` | **19** | FROZEN archive; 12 deny-write triggers reject all DML |
| `contract.authoring_panel_rejection_log` | **0** | FROZEN archive |
| `contract.calibration_event` | **19** | FROZEN archive |
| `contract.certification_record` | **3530** | FROZEN archive (C2 born-null trigger DROPPED; deny-write trigger LIVE) |
| `mcf.certification_record` | **0** | M-series CLOSED; no MCF authority writes yet |
| `mcf.metric_authoring_panel_run` | **0** (rows referencing panel_run_uid) | M-series CLOSED |
| `mcf.metric_contract_revision` | **0** (rows referencing panel_run_uid) | M-series CLOSED |
| `mcf.metric_publication_eligibility_result` | **0** (rows referencing panel_run_uid) | M-series CLOSED |
| `mcf.metric_supersession` | **0** (rows referencing panel_run_uid) | M-series CLOSED |

`bcf.panel_output_record` and `contract.panel_output_record` share **full panel_run_uid overlap** (19 / 19 / 19 INTERSECT = 19) — verified by INTERSECT query. This means the 5 cross-schema mcf→contract FKs could be retargeted to bcf without any FK-referent value mismatch even if mcf.* had rows today (mcf.* has 0 rows today, so retarget is mechanically trivial).

### 3.2 Trigger / function inventory post-A4

| Schema | Object | Status |
|---|---|---|
| `bcf` | `tg_certification_record_target_registry_id_guard` function | **PRESENT (LIVE)** |
| `bcf` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for INSERT (BEFORE FOR EACH ROW) | **PRESENT** |
| `bcf` | `trg_certification_record_target_registry_id_guard` trigger on `certification_record` for UPDATE (BEFORE FOR EACH ROW) | **PRESENT** |
| `contract` | `tg_panel_output_record_deny_write` function | **PRESENT (LIVE, A4-installed)** |
| `contract` | `tg_authoring_panel_rejection_log_deny_write` function | **PRESENT (LIVE, A4-installed)** |
| `contract` | `tg_calibration_event_deny_write` function | **PRESENT (LIVE, A4-installed)** |
| `contract` | `tg_certification_record_deny_write` function | **PRESENT (LIVE, A4-installed)** |
| `contract` | `trg_contract_<table>_deny_write` triggers (4 tables × 3 events INSERT/UPDATE/DELETE; BEFORE FOR EACH STATEMENT) | **12 PRESENT (LIVE, A4-installed)** |
| `contract` | `tg_certification_record_target_registry_id_guard` function | **0 (DROPPED by A4 C2)** |
| `contract` | `trg_certification_record_target_registry_id_guard` trigger | **0 (DROPPED by A4 C2)** |

### 3.3 FK inventory (the A5 retarget scope)

**Inbound FKs targeting `contract.panel_output_record` (9 total)**:

| Direction | FK name | Source | Target column → Target column | Notes |
|---|---|---|---|---|
| intra-contract | `fk_authoring_panel_rejection_log__panel_run` | `contract.authoring_panel_rejection_log.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | sibling FK on FROZEN archive |
| intra-contract | `fk_calibration_event__panel_run` | `contract.calibration_event.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | sibling FK on FROZEN archive |
| intra-contract | `fk_certification_record__panel_run` | `contract.certification_record.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | sibling FK on FROZEN archive |
| contract→contract | `fk_intake_queue__panel_run` | `contract.intake_queue.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | the R8 SPLIT preserves intake_queue on contract; FK preserved post-A4; **out of A5 scope** |
| **cross-schema (mcf→contract)** | `fk_mcf_cert_panel_run` | `mcf.certification_record.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | **A5 retarget scope (ON DELETE RESTRICT, ON UPDATE NO ACTION)** |
| **cross-schema (mcf→contract)** | `fk_mapr_panel_run` | `mcf.metric_authoring_panel_run.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | **A5 retarget scope (ON DELETE RESTRICT, ON UPDATE NO ACTION)** |
| **cross-schema (mcf→contract)** | `fk_mcr_panel_run` | `mcf.metric_contract_revision.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | **A5 retarget scope (ON DELETE RESTRICT, ON UPDATE NO ACTION)** |
| **cross-schema (mcf→contract)** | `fk_mper_panel_run` | `mcf.metric_publication_eligibility_result.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | **A5 retarget scope (ON DELETE RESTRICT, ON UPDATE NO ACTION)** |
| **cross-schema (mcf→contract)** | `fk_mcs_panel_run` | `mcf.metric_supersession.panel_run_uid` | `contract.panel_output_record.panel_run_uid` | **A5 retarget scope (ON DELETE RESTRICT, ON UPDATE NO ACTION)** |

**Cross-schema FKs from `bcf.*` → non-`bcf.*`: 0** (R10 cluster separation invariant intact; A5 must preserve).

### 3.4 Post-A5 expected FK inventory

After A5 retarget, the inbound FKs on `contract.panel_output_record` reduce from 9 to **4** (3 intra-contract sibling + 1 contract.intake_queue); the 5 cross-schema mcf→contract FKs are replaced by 5 cross-schema **mcf→bcf** FKs (same FK names, same on-delete/on-update semantics, retargeted parent table only).

## 4. Phase A5 disposition design

A5 has two coupled deliverables and one decision:

1. **D-A — FK retarget** (mechanics for moving the 5 mcf→contract FKs to mcf→bcf)
2. **D-B — M12 writer flip** (the first-real-MCF-authority-writer code path that lands rows in mcf.* referencing bcf.panel_output_record)
3. **D-C — M14 unblock decision** (does A5 include unblock conditions, or only prepare the gate?)

### 4.1 D-A: FK retarget mechanics — four options

| Option | Description | Pros | Cons |
|---|---|---|---|
| **F1 single-tx atomic** | `BEGIN; ALTER TABLE mcf.<child> DROP CONSTRAINT <fk>; ALTER TABLE mcf.<child> ADD CONSTRAINT <fk> FOREIGN KEY (panel_run_uid) REFERENCES bcf.panel_output_record(panel_run_uid) ON DELETE RESTRICT ON UPDATE NO ACTION; ... [×5]; COMMIT;` All 5 FKs retargeted in one transaction | Simplest verification (single commit point); no intermediate inconsistent state; aligns with A4 single-tx pattern | Single lock window holds all 5 mcf table ACCESS EXCLUSIVE locks briefly — but mcf.* is empty today, so the window is microseconds |
| F2 phased per-FK | One commit per FK retarget; 5 separate transactions | Per-FK error isolation; easier ad-hoc rollback at the per-FK level | 5 verification gates; intermediate state where some FKs point to contract and some to bcf; harder to reason about partial-failure recovery |
| F3 event-trigger-deferred | Use `SET CONSTRAINTS DEFERRED` (only valid if FKs are DEFERRABLE — they are NOT today) | Theoretically allows in-flight validation across writes | Requires upstream change to make FKs DEFERRABLE first (a separate DDL gate); not currently applicable |
| F4 shadow-with-cutover | Add new mcf→bcf FKs alongside (with different names); cut over writer; later drop the old mcf→contract FKs | Allows independent verification; minimal window | Requires NEW FK names (governance churn); requires writer code to write panel_run_uid satisfying both FKs simultaneously — not feasible with cross-schema reference (the value must satisfy both bcf and contract simultaneously, which it does today only because of A2 byte-pinning; any new bcf-only panel_run_uid would violate contract FK) |

**Recommendation: F1 single-tx atomic.** Mechanics:
- Each FK retarget = 2 SQL statements (DROP CONSTRAINT + ADD CONSTRAINT with bcf parent).
- 5 FKs × 2 statements = **10 statements minimum**; plus optional pre-/post-tx verification probes (covered in §7).
- Atomicity guarantees: either all 5 FKs retarget or none do.
- Mcf.* is empty today → ACCESS EXCLUSIVE lock window is microseconds; no row revalidation cost.

### 4.2 D-B: M12 writer flip — four options

| Option | Description | Pros | Cons |
|---|---|---|---|
| **W1 greenfield M12 writer** | New `MetricAuthoringPanelRunWriter` service that writes mcf.metric_authoring_panel_run (and downstream mcf.* rows) referencing bcf.panel_output_record | Clean separation; correctness-by-construction; no leakage to contract.* (deny-write triggers would catch any leak); aligns with HR3 | Requires new service authoring + tests; longer implementation runway |
| W2 extend M4 path | Re-host `createMetricDraft()` logic on mcf substrate; flip its target tables | Re-uses tested code | Risk of dual-write paths during transition; tight coupling to M4 lifecycle; deny-write triggers would NOT save a misrouted M4 path because M4 today writes to mcf-side already; the leakage risk is via panel_run_uid references not target tables |
| W3 dedicated M12 service | Standalone service with its own lifecycle, instrumentation, and gate (M12 owns its writer) | Cleanest M-series boundary; future M12.5 and M13 can extend it | Same authoring runway as W1; effectively equivalent for A5 scope |
| W4 progressive enable | Feature-flag-gated rollout (per metric, per tenant, or per panel) | Allows safe rollout under M12.5 | M12 is not running yet (M14 CLOSED) — progressive enable has no rollout to gate yet |

**Recommendation: W1 greenfield M12 writer** (effectively equivalent to W3; the distinction is naming). Mechanics:
- New service at `src/registry/metric-authoring/m12-panel-run-writer.service.ts` (or equivalent).
- Writes: `mcf.metric_authoring_panel_run` (panel_run_uid + panel metadata) → `mcf.certification_record` + `mcf.metric_contract_revision` + `mcf.metric_publication_eligibility_result` + `mcf.metric_supersession` (each referencing the new mcf.metric_authoring_panel_run.panel_run_uid via the 5 newly retargeted FKs).
- Service is implementation-complete but **NOT invoked at any runtime entry point until M14 unblocks**.
- Smoke gate: write 1 panel_run_uid + child rows inside a SAVEPOINT, verify FK integrity, ROLLBACK; record evidence; do not commit.

### 4.3 D-C: M14 unblock decision — two options

| Option | Description | Pros | Cons |
|---|---|---|---|
| **α prepare-only** | A5 = FK retarget + M12 writer code path; M14 unblock is a SEPARATE operator-authorized governance gate (a follow-on phase, e.g., A6 or a step-by-step M14 unblock DBCP) | Maintains gate discipline; one decision per gate; aligns with all prior phase pattern; allows separate evidence for M14 unblock | M14 stays CLOSED indefinitely until that separate gate runs |
| β include-unblock-conditions | A5 designs M14 unblock prerequisites + smoke evidence + observation criteria; M14 unblock decision is OPERATOR-GATED inside this DBCP (operator can decide YES/NO at A5 time) | Faster path to M14 open if operator chooses | Couples FK retarget decision with M14 unblock decision; mixes governance concerns; harder to roll back independently |

**Recommendation: Option α prepare-only.** Mechanics:
- A5 ships FK retarget + M12 writer code.
- M14 remains CLOSED.
- A separate post-A5 governance gate (DBCP authoring + operator decision) is required to open M14 — that gate's required evidence is enumerated in §11 below as a reference, not as A5 scope.

## 5. Proposed Phase A5 DDL (under F1 + W1 + α)

### 5.1 FK retarget DDL (10 statements)

```sql
-- A5 FK retarget: 5 mcf→contract → mcf→bcf
-- Single transaction; all-or-none.

BEGIN;

-- 1: fk_mcf_cert_panel_run
ALTER TABLE mcf.certification_record DROP CONSTRAINT fk_mcf_cert_panel_run;
ALTER TABLE mcf.certification_record
  ADD CONSTRAINT fk_mcf_cert_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES bcf.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT ON UPDATE NO ACTION;

-- 2: fk_mapr_panel_run
ALTER TABLE mcf.metric_authoring_panel_run DROP CONSTRAINT fk_mapr_panel_run;
ALTER TABLE mcf.metric_authoring_panel_run
  ADD CONSTRAINT fk_mapr_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES bcf.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT ON UPDATE NO ACTION;

-- 3: fk_mcr_panel_run
ALTER TABLE mcf.metric_contract_revision DROP CONSTRAINT fk_mcr_panel_run;
ALTER TABLE mcf.metric_contract_revision
  ADD CONSTRAINT fk_mcr_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES bcf.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT ON UPDATE NO ACTION;

-- 4: fk_mper_panel_run
ALTER TABLE mcf.metric_publication_eligibility_result DROP CONSTRAINT fk_mper_panel_run;
ALTER TABLE mcf.metric_publication_eligibility_result
  ADD CONSTRAINT fk_mper_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES bcf.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT ON UPDATE NO ACTION;

-- 5: fk_mcs_panel_run
ALTER TABLE mcf.metric_supersession DROP CONSTRAINT fk_mcs_panel_run;
ALTER TABLE mcf.metric_supersession
  ADD CONSTRAINT fk_mcs_panel_run
  FOREIGN KEY (panel_run_uid)
  REFERENCES bcf.panel_output_record(panel_run_uid)
  ON DELETE RESTRICT ON UPDATE NO ACTION;

COMMIT;
```

**Statement count: 10.** Operator decision D10 (statement count lock).

### 5.2 M12 writer code (no DDL — only TypeScript)

A5 implementation PR adds:
- `src/registry/metric-authoring/m12-panel-run-writer.service.ts` (or equivalent naming) — the greenfield writer.
- Unit tests covering: writer-to-mcf semantics; FK references to bcf.panel_output_record; rejection of write paths that target contract.* (deny-write trigger structural enforcement).
- SAVEPOINT-rolled-back integration test demonstrating: panel_run_uid + child row written; FKs validate against bcf; ROLLBACK; no committed mutation.
- **No runtime invocation.** The writer is implementation-only until M14 unblocks.

### 5.3 Interaction with frozen contract.*

A5 design respects A4 freeze invariants:
- A5 does NOT execute any DML on contract.* (the 12 deny-write triggers would reject any attempt; A5 doesn't try).
- A5 does NOT execute any DDL on contract.* (no ALTER, no DROP).
- A5 DROPs and re-ADDs FKs on mcf.* child tables; the parent table (`contract.panel_output_record` → `bcf.panel_output_record`) changes but no parent table is mutated.
- Pre-A5 verification: contract.* row counts unchanged; 12 deny-write triggers + 4 functions present; contract.cert DROPPED state preserved.
- Post-A5 verification: same checks, plus 5 mcf→bcf FKs present (with same names as the dropped mcf→contract FKs), 0 mcf→contract FKs remaining.

## 6. Verification design

### 6.1 Pre-apply guards (5 required)

| # | Guard | Predicate |
|---|---|---|
| #500 | `a5_pre_apply_phase_a4_shipped` | 12 contract.* deny-write triggers + 4 functions LIVE; contract.cert born-null trigger + function DROPPED (count=0); `bcf.cert` write-once trigger LIVE |
| #501 | `a5_pre_apply_mcf_to_contract_fks_present` | 5 cross-schema mcf→contract FKs exist with expected names + on-delete + on-update semantics |
| #502 | `a5_pre_apply_panel_run_uid_overlap` | INTERSECT of `contract.panel_output_record.panel_run_uid` and `bcf.panel_output_record.panel_run_uid` = full overlap (count of contract = count of intersect; no orphan that would FK-violate post-retarget) |
| #503 | `a5_pre_apply_mcf_panel_run_uid_rows_zero_or_overlap` | All mcf.* panel_run_uid values (if any) exist in bcf.panel_output_record (so retarget cannot violate referential integrity) |
| #504 | `a5_pre_apply_env_gate_present` | `BCCORE_BCF_PHASE_A5_APPLY_CONFIRM=I_HAVE_REVIEWED_DRY_RUN_<dry-run-ts>` env var present (matching pinned dry-run ts) |

### 6.2 Post-apply assertions (10 required)

| # | Assertion | Predicate |
|---|---|---|
| #600 | `mcf_to_bcf_fks_present` | 5 mcf→bcf FKs exist with original names (`fk_mcf_cert_panel_run`, `fk_mapr_panel_run`, `fk_mcr_panel_run`, `fk_mper_panel_run`, `fk_mcs_panel_run`) referencing `bcf.panel_output_record(panel_run_uid)` ON DELETE RESTRICT ON UPDATE NO ACTION |
| #601 | `mcf_to_contract_fks_absent` | 0 cross-schema FKs from `mcf.*` → `contract.*` |
| #602 | `contract_panel_inbound_fks_reduced_to_4` | Inbound FKs to `contract.panel_output_record` = 4 (3 intra-contract sibling + 1 contract.intake_queue); was 9 pre-A5 |
| #603 | `bcf_panel_inbound_fks_now_5` | 5 inbound cross-schema FKs to `bcf.panel_output_record` (the retargeted mcf FKs) |
| #604 | `bcf_cross_schema_fks_unchanged` | Cross-schema FKs from `bcf.*` to non-`bcf.*` = 0 (R10 cluster separation invariant intact) |
| #605 | `contract_deny_write_triggers_unchanged` | 12 contract.* deny-write triggers + 4 functions LIVE (A4 freeze preserved) |
| #606 | `contract_cert_born_null_unchanged_dropped` | contract.cert born-null trigger + function count = 0 (A4 C2 state preserved) |
| #607 | `bcf_cert_write_once_unchanged_live` | bcf.cert write-once trigger LIVE; function count = 1 |
| #608 | `row_counts_unchanged` | bcf 19/0/19/3530; contract 19/0/19/3530; mcf.cert 0; all mcf.* panel_run_uid rows Δ=0 |
| #609 | `m14_still_closed` | M-series gates state unchanged (governance-level check; no runtime M-series invocation) |

### 6.3 M12 writer smoke (read-only DB introspection)

Pre-apply: confirm writer code exists at expected path; node --check passes; unit tests pass.
Post-apply: SAVEPOINT-rolled-back integration test verifies writer code references bcf.* tables and FKs validate against bcf.panel_output_record. **Test rolls back; no committed mutation.**

## 7. Rollback envelope

### 7.1 Pre-rollback guards (5)

| # | Guard | Predicate |
|---|---|---|
| #700 | `a5_rollback_no_post_a5_mcf_rows` | All mcf.* rows referencing panel_run_uid must have corresponding contract.panel_output_record.panel_run_uid value (the rollback cliff: if M12 has written rows with panel_run_uid values that don't exist in contract.*, rollback would violate referential integrity) |
| #701 | `a5_rollback_phase_a4_freeze_intact` | 12 contract.* deny-write triggers + 4 functions LIVE; contract.cert DROPPED state preserved |
| #702 | `a5_rollback_bcf_panel_rows_present` | bcf.panel_output_record has rows (rollback cannot proceed against empty parent table for FK pre-validation) |
| #703 | `a5_rollback_env_gate_present` | `BCCORE_BCF_PHASE_A5_ROLLBACK_CONFIRM=I_HAVE_REVIEWED_APPLY_<apply-ts>` env var present |
| #704 | `a5_rollback_bcf_cert_trigger_unchanged` | bcf.cert write-once trigger LIVE (rollback must not touch it) |

### 7.2 Operator-driven rollback DDL

Mirror of §5.1 but reversed: DROP the 5 mcf→bcf FKs + ADD the 5 mcf→contract FKs with original parent. Single transaction.

### 7.3 Post-rollback assertions (8)

`mcf_to_contract_fks_present` (5) + `mcf_to_bcf_fks_absent` (0) + `contract_panel_inbound_fks_restored_to_9` + `bcf_panel_inbound_fks_back_to_0` + `bcf_cross_schema_fks_unchanged` (0) + `contract_deny_write_triggers_unchanged` (12+4) + `bcf_cert_write_once_unchanged_live` + `row_counts_unchanged`.

### 7.4 A5 rollback cliff

**A5 rollback validity has a cliff at the first real M12 panel run.** Once M12 writes a new panel_run_uid to bcf.panel_output_record + a child row in mcf.*, that panel_run_uid will NOT exist in contract.panel_output_record (because contract.* is frozen and accepts no DML). At that point:
- The mcf.* child row's panel_run_uid is in bcf.panel_output_record (valid).
- That same panel_run_uid is NOT in contract.panel_output_record.
- A5 rollback that re-points the FK to contract.panel_output_record would fail FK validation on the orphaned mcf row.

Three rollback outcomes:
- **(A) M12 has never run post-A5**: rollback works clean.
- **(B) M12 has run, but only with panel_run_uids that existed before A4** (i.e., the original 19): rollback works clean (those panel_run_uids exist in both bcf + contract by A2 byte-pinning).
- **(C) M12 has run with new panel_run_uids** (the realistic post-M14-unblock scenario): rollback would require **row-destructive cleanup** of orphan mcf rows OR a "force-rollback-with-data-loss" envelope (operator-authorized; not in A5 base scope).

**Recommendation: A5 base rollback supports (A) and (B); guard #700 explicitly detects (C) and refuses.** A "force-rollback-with-data-loss" envelope is deferred to a separate post-M12-unblock contingency DBCP, not authored in A5.

### 7.5 A4 rollback validity post-A5 ship

**A4 rollback is INVALIDATED once A5 ships.** A4 rollback would restore the contract.* born-null trigger + drop deny-write triggers + leave contract.* writable. But post-A5, mcf.* FKs point at bcf, not contract — so restoring contract.* writability does not restore the FK topology. **Any combined A4+A5 rollback must perform A5 rollback FIRST (per §7.1-7.4 above), then A4 rollback** (per bc-core `bcf-evidence-schema-phase-a4-rollback.mjs --mode=pre-rollback` / `--mode=post-rollback`).

This is the **A5 ship-time materialization of the A4 closeout cliff** (Phase A4 closeout doc §5.3): once A5 ships, A4 rollback alone cannot restore the FK topology.

## 8. Test + evidence plan

### 8.1 Static + structural checks
- Static grep lockfile extension (`bcf-phase-a3-import-lockfile.mjs` or successor) asserting: 5 mcf→bcf FK declarations in DDL; 0 mcf→contract FK declarations; M12 writer service references bcf.* table identifiers; no M12 writer reference to contract.* tables (defensive against trigger-rejected misroutes).
- `node --check` on all new TypeScript and JS scripts.
- DDL synth module unit tests covering 10 statements.

### 8.2 Live DB verification (read-only via bc-postgres MCP)
- FK inventory pre-apply: 5 mcf→contract FKs; 9 inbound on contract.panel; 0 inbound on bcf.panel (cross-schema).
- FK inventory post-apply: 5 mcf→bcf FKs; 4 inbound on contract.panel; 5 inbound on bcf.panel (cross-schema).
- Row count invariant: bcf 19/0/19/3530; contract 19/0/19/3530; mcf.cert 0; mcf.* panel_run_uid rows Δ=0.
- Trigger inventory unchanged: 12 contract.* deny-write triggers + 4 functions LIVE; contract.cert born-null DROPPED state preserved; bcf.cert write-once LIVE.

### 8.3 No synthetic data
A5 apply does not write any rows. The SAVEPOINT-rolled-back smoke test writes a probe row + child, validates FK semantics, ROLLBACK; no committed mutation. **HR1 is preserved.**

### 8.4 No tenant DB
TENANT_DATABASE_URL guard in all A5 scripts (mirror of A4 pattern). HR4 substrate-enforced.

### 8.5 M12 writer smoke
Only if explicitly authorized by operator post-A5 apply. Even when authorized:
- Read-only smoke first: writer code introspection (parse SQL, verify table identifiers).
- SAVEPOINT smoke second: write probe row, validate FK + trigger behavior, ROLLBACK.
- No committed runtime M12 invocation until M14 unblock gate operator-authorized.

## 9. M14 unblock decision (Option α recommended)

### 9.1 What A5 does about M14
- A5 prepares the gate: M12 writer code path exists; FK topology supports mcf→bcf references; deny-write triggers protect contract.*.
- A5 does NOT open M14.
- A5 does NOT invoke M12 at any runtime entry point.

### 9.2 M14 unblock prerequisites (reference for the separate gate)
For a future M14 unblock governance gate to clear, these conditions would need evidence:
1. A5 shipped (FK retarget + M12 writer code in place).
2. M12 writer smoke under SAVEPOINT verified.
3. Reader path smoke verified (downstream consumers can read mcf.* without leakage to contract.*).
4. Observation period evidence on a controlled cohort (operator-defined: shadow run vs cutover vs progressive enable).
5. Rollback plan refreshed (M14 unblock has its own rollback envelope; A5 rollback may or may not be relevant depending on M12 row state).
6. Operator decision on M14 opening conditions.

These are listed for context. **They are not A5 scope.**

## 10. Relationship to first real M12 panel run

### 10.1 What remains after A5 before first real M12 run

| Gate | Status post-A5-ship | Required for first real M12 run |
|---|---|---|
| A5 FK retarget | DONE | Required |
| M12 writer code | DONE (implementation-complete; not invoked) | Required |
| M12 writer SAVEPOINT smoke | NOT EXECUTED (separate operator authorization) | Required (smoke evidence) |
| M12 reader path smoke | NOT EXECUTED (separate operator authorization) | Required (reader evidence) |
| M14 unblock decision | NOT EXECUTED (Option α: separate gate) | Required (M14 must open) |
| Observation period evidence | NOT EXECUTED (depends on M14 unblock model) | Optional / operator-defined |

### 10.2 What evidence must be captured before first real M12 run

The first real M12 panel run is **not** A5 scope. For its eventual authorization, the operator + governance owner will require:
- Live FK inventory verifying 5 mcf→bcf FKs.
- Live trigger inventory verifying 12 contract.* deny-write triggers + 4 functions LIVE.
- Live row inventory verifying bcf/contract row counts unchanged.
- M12 writer SAVEPOINT smoke evidence (probe panel_run_uid written + child rows validated + rolled back).
- M12 reader smoke evidence (downstream consumer reads mcf.* without contract.* fall-back).
- A clean operator-authorized M14 unblock gate run.

A5 ship event + A5 closeout doc + bc-core PR evidence chain together compose the "infrastructure-ready" predicate; first-real-run authorization is a separate predicate.

## 11. Risk register R1..R12

| # | Risk | Mitigation |
|---|---|---|
| R1 | Single-tx FK retarget under load contention | mcf.* is empty today; ACCESS EXCLUSIVE locks for microseconds; operator-authorized maintenance window optional but not required |
| R2 | panel_run_uid value mismatch between bcf and contract | byte-pinned A2 migration preserves overlap; guard #502 explicitly verifies INTERSECT = full overlap pre-apply |
| R3 | A4 rollback validity loss post-A5 ship | designed in: §7.5 documents the materialization; bc-core A4 rollback verifier already has guard #300 `a4_rollback_phase_a5_not_shipped` (added by PR #148) |
| R4 | Combined A4+A5 rollback complexity | mitigated by §7.4 cliff documentation + 3 rollback outcomes (A) / (B) / (C); operator-authorized force-rollback-with-data-loss deferred to separate DBCP |
| R5 | M12 writer references wrong table (contract.* instead of bcf.*) | static grep lockfile extension catches; deny-write triggers catch any committed misroute at runtime; SAVEPOINT smoke catches under test |
| R6 | M14 unblock too early | Option α: M14 unblock is a separate gate; A5 does not open it |
| R7 | Race condition during FK retarget | single transaction; mcf.* empty; no concurrent DML possible (M14 CLOSED) |
| R8 | Cross-schema grant model breaks under retarget | verify pre-apply: bcf role + grant model accommodates mcf children (mcf already has cross-schema grants to read bcf.panel_output_record per current FK design; A5 verifies no grant changes required) |
| R9 | A4 deny-write triggers conflict with A5 | A5 does no DML on contract.*; A5 does no DDL on contract.*; FK retarget is DDL on mcf.* child tables only; no conflict |
| R10 | R10 cluster separation violated (bcf→non-bcf FK introduced) | guard #604: cross-schema FKs from bcf.* to non-bcf.* must remain 0; A5 adds only inbound FKs to bcf, not outbound |
| R11 | mcf.* schema not present (hypothetical drift) | A1 created bcf; mcf.* tables exist independently as part of M-series substrate; verify pre-apply with table presence probe |
| R12 | First real M12 run accidentally invoked during A5 implementation | A5 implementation is code-only at runtime entry points; no scheduler / cron / queue trigger invokes M12; M14 stays CLOSED |

## 12. Operator decisions D1..D12

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | FK retarget mechanics | F1 single-tx atomic / F2 phased per-FK / F3 deferred / F4 shadow | **F1 single-tx atomic** |
| D2 | Authorize bc-core implementation PR authoring after this DBCP merges | YES / NO | **YES** |
| D3 | M12 writer flip approach | W1 greenfield / W2 extend M4 / W3 dedicated service / W4 progressive enable | **W1 greenfield** (effectively W3-equivalent) |
| D4 | M14 unblock policy | α prepare-only / β include-unblock-conditions | **α prepare-only** |
| D5 | A4 rollback validity post-A5 ship | INVALIDATE / preserve-via-force-envelope | **INVALIDATE** (force envelope deferred to separate DBCP) |
| D6 | First real M12 panel run authorization model | separate gate / inline with M14 unblock / inline with A5 | **separate gate** (post-M14-unblock; post-A5) |
| D7 | Pre-A5 lockfile extension scope | (a) FK assertions only / (b) FK + M12 writer table-identifier assertions / (c) FK + M12 + reader path assertions | **(b) FK + M12 writer table-identifier assertions** |
| D8 | `contract.intake_queue` FK disposition | retain / retarget-to-bcf | **retain** (intake_queue is contract-side governance; out of A5 scope) |
| D9 | M14 stays CLOSED through A5 ship + closeout | YES / NO | **YES** |
| D10 | Statement count for A5 DDL | exact number | **10** (5 FKs × 2 ALTER statements) |
| D11 | Post-A5 DROP slice (F4 HYBRID roadmap) | author in A5 / defer to post-A5 gate | **defer to post-A5 gate** (per A4 closeout §6.3) |
| D12 | M12 writer SAVEPOINT smoke timing | inline with A5 apply / separate post-A5 authorization | **separate post-A5 authorization** |

## 13. Hard rule mapping (HR1..HR5)

| Rule | A5 design status |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | A5 apply writes ZERO rows. SAVEPOINT smoke writes a probe + rolls back. M12 writer code is implementation-only until M14 unblock; even then, M12 writes real metric authority panel-run rows, not synthetic |
| **HR2** — MCF evidence belongs in `mcf.*` | A5 design retargets mcf.* FKs to bcf.* parents; mcf.* IS where the M12 writer writes (per its semantic purpose: MCF authority lifecycle) |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.*` | enforced structurally by A4 deny-write triggers; A5 design has no contract.* write paths; lockfile static-grep extension catches any drift |
| **HR4** — tenant result DBs separate | TENANT_DATABASE_URL guard in all A5 scripts; no tenant DB connection opened during A5 implementation, apply, or rollback |
| **HR5** — production path; no mocks | A5 FK retarget targets live bc_platform_dev; SAVEPOINT smoke uses real tables with ROLLBACK; mocks confined to unit + SAVEPOINT-rolled-back integration tests |
| **Stance ADR DEC-7f9597 / D423** | Operator authorization required on mutating gates: A5 apply, A5 rollback, M14 unblock, first real M12 panel run — each is a separate operator gate. Rollback discipline preserved with explicit cliff documentation (§7.4). Substrate-boundary clarity maintained: mcf→bcf FKs after A5; contract.* frozen archive preserved |

## 14. Standing gate state (target post-A5-ship)

| Gate | Pre-A5 | Target post-A5 |
|---|---|---|
| M14 | CLOSED | CLOSED (Option α) |
| Phase A4 substrate | APPLIED at `2026-05-29T11-21-03-131Z` | preserved (unchanged) |
| `contract.*` BCF evidence tables | STRUCTURALLY FROZEN | preserved STRUCTURALLY FROZEN |
| `contract.cert` born-null trigger + function | DROPPED per C2 | preserved DROPPED |
| `bcf.cert` write-once trigger | LIVE | preserved LIVE |
| 5 mcf→contract FKs | PRESENT | **REPLACED by 5 mcf→bcf FKs** (same names; same on-delete/on-update semantics) |
| Inbound FKs to `contract.panel_output_record` | 9 (3 intra + 1 intake + 5 mcf) | **4** (3 intra + 1 intake) |
| Inbound FKs to `bcf.panel_output_record` (cross-schema) | 0 | **5** (the retargeted mcf FKs) |
| Cross-schema FKs from `bcf.*` → non-`bcf.*` | 0 | **0 (R10 cluster separation invariant intact)** |
| M12 writer code path | NOT EXISTING | EXISTS (implementation-only; not invoked) |
| Combined Phase A3 + step 20 rollback envelope | INVALID per D9 | preserved INVALID |
| A4 rollback envelope | AVAILABLE pre-A5 | **INVALIDATED** (per D5; A4 rollback cannot restore FK topology) |
| A5 rollback envelope | not yet authored | **AVAILABLE pre-first-M12-run** (per §7) |
| First real M12 panel run | not authorized | not authorized |
| Tenant DB connection | none | none |

## 15. Sequencing record

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
21. ⏸ **Phase A5 DBCP authoring (THIS DOC)** — pending operator merge
22. ⏸ Phase A5 implementation PR — gated on A5 DBCP merge + separate operator authorization
23. ⏸ Phase A5 dry-run + sha256 pin — gated on A5 implementation PR merge + separate operator authorization
24. ⏸ Phase A5 apply — gated on A5 dry-run + separate operator authorization
25. ⏸ Phase A5 post-apply evidence + closeout — gated on A5 apply
26. ⏸ M12 writer SAVEPOINT smoke — gated on A5 ship + separate operator authorization
27. ⏸ M12 reader smoke — gated on writer smoke + separate operator authorization
28. ⏸ M14 unblock governance gate (separate DBCP per Option α) — gated on smoke evidence + separate operator authorization
29. ⏸ First real M12 panel run — gated on M14 unblock + separate operator authorization
30. ⏸ Post-A5 DROP slice (F4 HYBRID roadmap per Phase A4 closeout §6) — gated on stable M12 operation + separate governance gate

## 16. Out-of-scope re-statement

This DBCP does **NOT** apply DDL.

This DBCP does **NOT** apply DML.

This DBCP does **NOT** modify bc-core code.

This DBCP does **NOT** authorize the bc-core A5 implementation PR's apply gate — that is a SEPARATE operator authorization after the implementation PR is merged.

This DBCP does **NOT** authorize first real M12 panel run.

This DBCP does **NOT** authorize M14 unblock — A5 is Option α prepare-only.

This DBCP does **NOT** authorize the post-A5 DROP slice (F4 HYBRID roadmap; per A4 closeout §6.3).

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** alter `bcf.*`, `contract.*`, `mcf.*`, `metric.*`, or `concept_registry.*` substrate.

This DBCP does **NOT** invoke M-series.

This DBCP does **NOT** execute Phase A4 rollback or combined Phase A3 + step 20 rollback.

This DBCP does **NOT** initiate any synthetic / mock / canned data writes.

---

**End of DBCP. Phase A5 design RECORDED. Next operator-authorized gate: Phase A5 bc-core implementation PR authoring.**
