---
uid: metric-context-framework-m14-m12-governance-dbcp
title: MCF — M14/M12 governance DBCP (M14 unblock + M12 writer activation + first real panel run)
description: Governance design for the M14 unblock + M12 writer activation + first-real-M12-panel-run authorization sequence after the completed Phase A5 ship event at apply-ts `2026-05-29T13-07-48-822Z` (bc-docs-v3 main `2792c36` via PR #22; bc-core main `99edc1b` via PR #153). Enumerates the substrate state post-A5 (5 mcf→bcf FKs LIVE; contract.* BCF evidence FROZEN by A4 deny-write triggers; contract.cert born-null DROPPED per C2; bcf.cert write-once LIVE; bcf/contract rows 19/0/19/3530 each; mcf.cert + mcf.* panel_run_uid rows all 0; M12 writer skeleton throws `M12NotImplementedError`); the M14 unblock options (U1 single-shot / U2 staged / U3 per-tenant / U4 per-metric); the evidence requirements before M14 can open (E1..E7); the M12 writer SAVEPOINT smoke gate design; the M12 reader smoke gate design; the first-real-M12-panel-run authorization gate (the cliff-crossing event from outcome A→C per A5 DBCP §7.4); the rollback cliff treatment options (C1 accept / C2 force-rollback-with-data-loss envelope / C3 deferrable dual-FK / C4 pre-cliff snapshot); the M12 writer activation path; the post-run evidence requirements (P1..P7); the risk register R1..R12; the operator decisions D1..D14. **NOT EXECUTED.** This DBCP authorizes design only; the M12 writer real-body implementation PR is a separately operator-authorized follow-up; the M12 writer SAVEPOINT smoke gate is a separate operator-authorized gate; the M12 reader smoke gate is a separate operator-authorized gate; the M14 unblock apply gate is a separate operator-authorized gate; the first real M12 panel run is a separate operator-authorized gate. **No DDL applied, no DML applied, no M12 invocation, no M14 unblock, no first real M12 panel run, no tenant DB connection.** Operator stance ADR DEC-7f9597 / D423 honoured — operator authorization required on every mutating gate; rollback discipline preserved (A5 rollback envelope outcome A today); substrate-boundary clarity maintained.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: mcf-m14-m12-governance-and-first-real-panel-run
supersedes:
superseded_by:
---

# MCF — M14/M12 governance DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> The Phase A5 mcf→bcf FK retarget shipped at apply-ts `2026-05-29T13-07-48-822Z`, anchored in evidence at bc-core main `99edc1b` (PR #153) and closed out at bc-docs-v3 main `2792c36` (PR #22). The 5 cross-schema FKs now reference `bcf.panel_output_record(panel_run_uid)`; the M12 writer skeleton at `src/registry/metric-authoring/m12-panel-run-writer.service.ts` throws `M12NotImplementedError` on any invocation; M14 remains CLOSED per operator decisions D4 (α prepare-only) + D6 (separate first-run gate) + D9 (M14 stays CLOSED through A5) + D12 (M12 SAVEPOINT smoke separate authorization). What is the governance design for the M14 unblock + M12 writer activation + first-real-M12-panel-run sequence — including the unblock conditions, required evidence, the writer SAVEPOINT smoke gate, the reader smoke gate, the first-real-run authorization, the rollback cliff treatment (the A→C transition per A5 DBCP §7.4), the M12 writer real-body activation path, the post-run evidence requirements, the risk register, and the operator decisions to lock?

### 1.2 In scope

- **Substrate inventory post-A5** — 5 mcf→bcf FKs LIVE; 5 mcf→contract FKs DROPPED; A4 freeze invariants preserved; contract.cert C2 DROPPED; bcf.cert write-once LIVE; bcf/contract rows 19/0/19/3530; mcf.cert 0; mcf.* panel_run_uid rows 0 across all 5 tables; A5 rollback envelope outcome (A).
- **M14 unblock design** — four options (U1 single-shot / U2 staged / U3 per-tenant / U4 per-metric); recommended option; mechanics + evidence binding.
- **Evidence requirements before M14 can open (E1..E7)** — what evidence the operator must see + accept before authorizing M14 unblock.
- **M12 writer SAVEPOINT smoke gate** — design (S1 mechanics); env-gate; assertions; rollback semantics; evidence emitted; what it does NOT do.
- **M12 reader smoke gate** — design (R1 mechanics); env-gate; assertions; read-only enforcement; evidence emitted.
- **First real M12 panel run authorization gate** — design; cliff-crossing event semantics; evidence emitted; post-run verification; ROLLBACK option (within the run only).
- **Rollback cliff treatment (the A→C transition)** — four options (C1 accept / C2 force-rollback-with-data-loss envelope / C3 deferrable dual-FK / C4 pre-cliff snapshot); recommended; consequences enumerated.
- **M12 writer activation path** — how the skeleton becomes callable (W1 real-body PR; W2 feature-flag-gated rollout); operator-authorization sequence.
- **M14 semantics** — what M14 unblock authorizes: (α) writer activation only / (β) writer activation + first real run permission. Recommended: α.
- **Post-run evidence requirements (P1..P7)** — what evidence the operator must capture after the first real run, and what must be verified independently.
- **Risk register R1..R12.**
- **Operator decisions D1..D14.**
- **Hard-rule mapping HR1..HR5.**
- **Sequencing record + standing gate state target.**
- Authorization to author the subordinate DBCPs in follow-ups (M12 writer real-body implementation; M12 SAVEPOINT smoke gate; M12 reader smoke gate; M14 unblock apply gate; first real M12 panel run authorization). Each subordinate DBCP's apply gate is a SEPARATE operator authorization.

### 1.3 Explicit non-scope

- ❌ **No DDL applied.** This DBCP designs the M14/M12 governance; the M12 writer real-body implementation + smoke gates + M14 unblock + first real run are separately operator-authorized follow-ups.
- ❌ **No DML applied.** No row mutation on `bcf.*` / `contract.*` / `mcf.*` / `metric.*` / `concept_registry.*` / any tenant DB.
- ❌ **No bc-core code change.** Authoring the M12 writer real-body PR is a SEPARATE follow-up operator authorization.
- ❌ **No M11 invocation.** M11 (panel-input ingestion) remains as currently structured; not part of this DBCP scope.
- ❌ **No M12 invocation.** The skeleton throws `M12NotImplementedError`; no runtime invocation path.
- ❌ **No M12.5 invocation.** M12.5 (materialization + legacy bridge per CLAUDE.md MCF section) is downstream of first real M12 run; not in this DBCP scope.
- ❌ **No M13 invocation.** M13 (PE-MC evaluator) remains gated.
- ❌ **No M14 unblock.** M14 stays CLOSED throughout this DBCP authoring; the unblock apply gate is a SEPARATE operator authorization.
- ❌ **No first real M12 panel run.** The cliff-crossing authorization is a SEPARATE operator gate.
- ❌ **No A5 rollback executed.** A5 rollback envelope remains dormant (outcome A available).
- ❌ **No A4 rollback executed.** A4 rollback envelope is INVALID per D5 (Phase A5 closeout PR #22 §5).
- ❌ **No combined Phase A3 + step 20 rollback executed.** INVALID per D9.
- ❌ **No tenant `tbc_{slug}_dev` DB connection.** Tenant scope deferred; out of this DBCP scope.
- ❌ **No synthetic / mock / replay / canned data writes.** HR1 substrate-enforced.
- ❌ **No `concept_registry.*` touch.**
- ❌ **No bc-admin / bc-portal UI changes.**
- ❌ **No PR #11 / #12 / #13 / #14 / #15 / #16 / #17 / #18 / #19 / #20 / #21 / #22 re-touch.**
- ❌ **No PR #141 / #142 / #143 / #144 / #145 / #146 / #147 / #148 / #149 / #150 / #151 / #152 / #153 re-touch.**
- ❌ **No post-A5 DROP slice (F4 HYBRID roadmap).** Deferred per A4 closeout §6 + A5 D11; orthogonal to M14/M12 governance.

## 2. Authority anchor chain

| Artifact | Location | Authority for |
|---|---|---|
| **Boundary DBCP (Option A)** | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` (PR #11) | Schema-boundary design; M-series ownership of mcf.* substrate |
| **Phase A5 DBCP (D1..D12)** | `docs/implementation/bcf-evidence-schema-phase-a5-dbcp.md` @ bc-docs-v3 main `1d631d7` (PR #21) | D4 α prepare-only; D6 separate first-run gate; D9 M14 CLOSED through A5; D12 M12 SAVEPOINT smoke separate authorization |
| **Phase A5 closeout** | `docs/implementation/bcf-evidence-schema-phase-a5-closeout.md` @ bc-docs-v3 main `2792c36` (PR #22) | Substrate state post-A5; D5 rollback-policy state change recorded; M12 writer skeleton status; first real M12 run NOT authorized |
| Phase A4 DBCP + closeout | bc-docs-v3 main `dbc0378` (PR #19) + `757071a` (PR #20) | A4 freeze invariants (12 deny-write triggers + 4 functions); contract.cert C2 DROPPED state; F4 HYBRID roadmap deferred |
| Phase A5 implementation | bc-core main `0d382f3` (PR #151) | M12 greenfield writer skeleton at `src/registry/metric-authoring/m12-panel-run-writer.service.ts`; A5 scripts; lockfile extension |
| Phase A5 dry-run + sha256 pin | bc-core main `153c46d` (PR #152) | sha256 `9113b098...` |
| Phase A5 apply + post-apply evidence | bc-core main `99edc1b` (PR #153) | apply-ts `2026-05-29T13-07-48-822Z`; post-apply-ts `2026-05-29T13-07-57-405Z`; 5 mcf→bcf FKs LIVE |
| MCF M12 authoring panel DBCP | `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` (pre-existing) | M12 panel orchestration semantics (independent of A-series substrate migration) |
| MCF M5 panel substrate DBCP | `docs/implementation/metric-context-framework-m5-panel-substrate-dbcp.md` (pre-existing) | mcf.metric_authoring_panel_run shape; FK design original |
| **bc-docs-v3 anchor (this DBCP base)** | bc-docs-v3 main `2792c362b3c93d1b565ac5ce3de980ef866ee41c` (post-PR-#22 merge) | Governance audit trail with full A1..A5 chain closed |
| bc-core anchor (subordinate implementation PR bases) | bc-core main `99edc1b11e440617c438e56eb6d859a8036a230d` | Code state the future M12 writer real-body PR will modify |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) | Operator authorization on every mutating gate; rollback discipline; substrate-boundary clarity |
| Hard rules HR1..HR5 | Boundary DBCP §5 | Substrate constraints this design must respect |

## 3. Current substrate state (verified live post-A5)

### 3.1 FK topology (post-A5)

| Check | Live |
|---|---|
| mcf→contract FKs | 0 (DROPPED by A5) |
| mcf→bcf FKs | 5 (LIVE; all RESTRICT/NO ACTION) |
| Inbound FKs to `contract.panel_output_record` | 4 (3 intra-contract sibling + 1 contract.intake_queue per A5 D8) |
| Cross-schema inbound on `bcf.panel_output_record` | 5 |
| Cross-schema FKs from `bcf.*` → non-`bcf.*` | 0 (R10 cluster separation intact) |

### 3.2 Trigger / function inventory (post-A5)

| Substrate | Status |
|---|---|
| `contract.*` deny-write functions (LIVE) | 4 (A4 freeze preserved) |
| `contract.*` deny-write trigger rows (LIVE) | 12 (4 tables × 3 events INSERT/UPDATE/DELETE) |
| `contract.cert` born-null trigger + function | 0 (DROPPED per A4 C2; preserved) |
| `bcf.cert` write-once trigger + function | 1 / 2 trigger rows INSERT+UPDATE (LIVE; preserved) |

### 3.3 Row counts (post-A5)

| Table | Rows |
|---|---|
| `bcf.panel_output_record` | 19 |
| `bcf.authoring_panel_rejection_log` | 0 |
| `bcf.calibration_event` | 19 |
| `bcf.certification_record` | 3530 |
| `contract.panel_output_record` | 19 |
| `contract.authoring_panel_rejection_log` | 0 |
| `contract.calibration_event` | 19 |
| `contract.certification_record` | 3530 |
| `mcf.certification_record` | 0 |
| `mcf.metric_authoring_panel_run` (panel_run_uid not null) | 0 |
| `mcf.metric_contract_revision` (panel_run_uid not null) | 0 |
| `mcf.metric_publication_eligibility_result` (panel_run_uid not null) | 0 |
| `mcf.metric_supersession` (panel_run_uid not null) | 0 |

### 3.4 M12 writer + governance gate status

| Check | Status |
|---|---|
| M12 writer service file | `src/registry/metric-authoring/m12-panel-run-writer.service.ts` (skeleton at bc-core main `99edc1b`) |
| M12 writer `writePanelRun()` invocation | throws `M12NotImplementedError` (per PR #151 D3 W1) |
| M12 writer wired to controller / scheduler / queue | NO |
| M14 governance gate | CLOSED (per A5 D9) |
| A5 rollback envelope | AVAILABLE pre-first-M12-run only (outcome A today; cliff predicate guard #700) |
| Phase A4 rollback envelope | INVALID per A5 D5 |
| Combined A3 + step 20 rollback envelope | INVALID per A4 D9 |

## 4. M14 unblock design

### 4.1 Four options for M14 unblock mechanics

| Option | Description | Pros | Cons |
|---|---|---|---|
| **U1 single-shot** | M14 opens fully on operator authorization; first real M12 panel run permitted immediately | Simplest gate; one operator decision | Couples M14 unblock with first-run authorization; no smoke evidence between them; rollback cliff materializes immediately |
| **U2 staged unblock** | M14 opens for guarded smoke (SAVEPOINT writer smoke + reader smoke) only; first real run is a SEPARATE post-smoke operator-authorized gate | Preserves discipline; aligns with A5 D4 α prepare-only + D6; smoke evidence binds first-run authorization; rollback cliff materializes only at first-run gate | Two-step gate; longer authorization runway |
| U3 per-tenant rollout | M14 unblocked per-tenant individually | Allows graduated rollout | Tenant scope deferred per operator scope item §1.3; not currently applicable |
| U4 per-metric rollout | M14 unblocked per-metric (feature-flag gated) | Allows graduated metric rollout | Adds feature-flag infrastructure; couples M14 with feature-flag governance; defers cliff materialization without reducing it |

**Recommendation: U2 staged unblock.** Aligns with established Phase A-series gate discipline; one operator decision per gate; smoke evidence binds the first-run authorization; rollback cliff materializes at a single explicit moment.

### 4.2 What M14 unblock authorizes — α vs β

| Option | Description |
|---|---|
| **α writer activation only** | M14 unblock authorizes the M12 writer to be invocable at runtime (replaces `throw M12NotImplementedError` with real body); first real M12 panel run is a SEPARATE operator-authorized gate |
| β writer activation + first real run | M14 unblock authorizes both writer activation AND first real M12 panel run on the same operator decision |

**Recommendation: α writer activation only.** Mirrors A5 D4 α prepare-only + D6 separate first-run gate; preserves the cliff materialization at a single explicit operator decision.

### 4.3 Pre-conditions for M14 unblock (operator-readable)

Before the M14 unblock apply gate can run, the operator must have authored, reviewed, and merged:
1. **M12 writer real-body implementation PR** (subordinate to this DBCP per §10).
2. **M12 writer SAVEPOINT smoke evidence PR** (subordinate per §6).
3. **M12 reader smoke evidence PR** (subordinate per §7).

After those land, the M14 unblock apply gate becomes runnable under operator-authorized env-gate.

## 5. Evidence requirements before M14 can open

| # | Evidence | Source | Status today |
|---|---|---|---|
| E1 | Live FK inventory: 5 mcf→bcf FKs with RESTRICT/NO ACTION | bc-postgres MCP read-only query | **MET** (Phase A5 closeout §4.1) |
| E2 | Live trigger inventory: 12 contract.* deny-write triggers + 4 functions LIVE; contract.cert C2 DROPPED state preserved; bcf.cert write-once LIVE | bc-postgres MCP read-only query | **MET** (Phase A5 closeout §4.3-4.4) |
| E3 | Live row inventory baseline: bcf 19/0/19/3530; contract 19/0/19/3530; mcf.* 0 | bc-postgres MCP read-only query | **MET** (Phase A5 closeout §4.5) |
| E4 | M12 writer SAVEPOINT smoke evidence: probe panel_run_uid + child rows written + rolled back; FK semantics verified; no committed mutation | Future SAVEPOINT smoke gate per §6 | **NOT YET CAPTURED** |
| E5 | M12 reader smoke evidence: downstream consumer SELECT queries return expected mcf.* shape; no contract.* fall-back; FK joins work | Future reader smoke gate per §7 | **NOT YET CAPTURED** |
| E6 | Cross-schema grants verified: mcf.* tables have SELECT on bcf.panel_output_record (FK validation requires the SELECT grant) | bc-postgres MCP read-only `information_schema.role_table_grants` query | **NOT YET PROBED** |
| E7 | Operator decision on rollback cliff treatment recorded | This DBCP §9 + operator selection at PR merge | **TO BE LOCKED** by this DBCP |

E1-E3 are met. E4-E5 require separate operator-authorized smoke gates. E6 is read-only and may be probed at any time. E7 is decided at this DBCP's merge.

## 6. M12 writer SAVEPOINT smoke gate design

### 6.1 Purpose

Verify that the M12 writer code path (post real-body replacement) correctly writes to bcf.panel_output_record + mcf.metric_authoring_panel_run + downstream MCF children — with FK validation succeeding against the post-A5 mcf→bcf topology — and that the contract.* deny-write triggers would reject any misroute. **No committed mutation.** All writes happen inside a SAVEPOINT and are ROLLED BACK.

### 6.2 Mechanics (S1)

```
BEGIN;
  SAVEPOINT m12_writer_smoke;
  -- Use one of the existing 19 panel_run_uids in bcf.panel_output_record
  -- (so the FK references resolve against existing rows; no cliff-crossing).
  -- The probe panel_run_uid is read from bcf.panel_output_record at runtime.
  --
  -- The M12 writer service invocation:
  --   m12Writer.writePanelRun({
  --     panelRunUid: <one-of-the-19>,
  --     workbenchFingerprintHash: 'sha256:<probe-hex64>',
  --     ...probe payload...
  --   });
  --
  -- The real-body writer (post-W1 activation) INSERTs:
  --   mcf.metric_authoring_panel_run  (1 row; FK to bcf.panel_output_record)
  --   mcf.metric_authoring_panel_transcript  (3 rows; FK to mapr)
  --
  -- Assertions inside the SAVEPOINT:
  --   #800 mcf.metric_authoring_panel_run row count incremented by 1
  --   #801 FK fk_mapr_panel_run resolves (no orphan row)
  --   #802 contract.* deny-write triggers did NOT fire (verified by attempting
  --        a SAVEPOINT-protected INSERT into contract.panel_output_record and
  --        catching the RAISE EXCEPTION)
  --   #803 No INSERT into contract.* during writer execution (audit log probe)
  ROLLBACK TO SAVEPOINT m12_writer_smoke;
  -- Verify no committed state remains:
  --   #810 mcf.metric_authoring_panel_run row count Δ=0 vs pre-smoke baseline
ROLLBACK;
```

The smoke runs inside a SAVEPOINT inside a transaction; the outer `ROLLBACK` discards the transaction. No committed mutation reaches bcf.* or mcf.*.

### 6.3 Env-gate

```
BCCORE_MCF_M12_SAVEPOINT_SMOKE_CONFIRM=I_HAVE_REVIEWED_A5_APPLY_2026-05-29T13-07-48-822Z
```

The env-gate references the A5 apply timestamp because the smoke depends on the post-A5 FK topology being LIVE.

### 6.4 What the smoke does NOT do

- ❌ Does NOT invoke M14 unblock (M14 stays CLOSED through smoke).
- ❌ Does NOT commit any mutation.
- ❌ Does NOT cross the A5 rollback cliff (the probe panel_run_uid is one of the 19 existing; outcome (B) at most if committed; smoke ROLLBACKs so outcome stays (A)).
- ❌ Does NOT verify production M12 orchestration semantics (panel agents, consensus, etc.); only writer-substrate-semantics.
- ❌ Does NOT write to contract.* (HR3 substrate-enforced + writer code structurally rejects).
- ❌ Does NOT touch tenant DBs.

### 6.5 Evidence emitted

- `scripts/audit-output/mcf-m12-writer-savepoint-smoke-<ts>.evidence.jsonl` — assertion records
- `scripts/audit-output/mcf-m12-writer-savepoint-smoke-<ts>.summary.md` — human-readable verdict
- Post-smoke independent live read confirming substrate Δ=0

## 7. M12 reader smoke gate design

### 7.1 Purpose

Verify that the downstream MCF reader code paths correctly read `mcf.*` (post-A5 topology) without falling back to `contract.*` for cert/panel-run data. **No mutation; pure read-only.**

### 7.2 Mechanics (R1)

```
-- Reader-side SELECT queries against mcf.* tables, joining to bcf.* via the
-- new mcf→bcf FK chain. Verify each downstream reader returns the expected
-- shape and respects the FK topology.
--
-- Probes:
--   #900 mcf.metric_authoring_panel_run reader returns 0 rows
--        (mcf.* panel_run_uid rows = 0 today; M12 has not run)
--   #901 mcf.certification_record reader returns 0 rows (mcf.cert = 0)
--   #902 No reader code path references `contract.panel_output_record`
--        for cert/panel-run data (lockfile-style static grep)
--   #903 Cross-schema SELECT grants verified: mcf.* tables have SELECT
--        privilege on bcf.panel_output_record (E6 evidence)
--   #904 FK chain integrity: simulated mcf row with one of the 19 existing
--        panel_run_uids would FK-validate against bcf.panel_output_record
--        (without inserting; using EXPLAIN or constraint introspection)
```

### 7.3 Env-gate

```
BCCORE_MCF_M12_READER_SMOKE_CONFIRM=I_HAVE_REVIEWED_A5_APPLY_2026-05-29T13-07-48-822Z
```

### 7.4 What the reader smoke does NOT do

- ❌ No DDL/DML; pure SELECT.
- ❌ No M12 writer invocation; reader-side only.
- ❌ No M14 unblock authorization implied.
- ❌ No tenant DB connection.

### 7.5 Evidence emitted

- `scripts/audit-output/mcf-m12-reader-smoke-<ts>.evidence.jsonl`
- `scripts/audit-output/mcf-m12-reader-smoke-<ts>.summary.md`

## 8. First real M12 panel run authorization gate

### 8.1 Purpose

Authorize the **first real M12 panel run** — the cliff-crossing event. This is a SEPARATE operator-authorized gate that materializes the A→C transition in the A5 rollback envelope (per Phase A5 DBCP §7.4 + Phase A5 closeout §5.3).

### 8.2 Pre-conditions

| # | Pre-condition | Source |
|---|---|---|
| 1 | M14 unblock apply gate completed | Subordinate per §4 |
| 2 | M12 writer real-body implementation merged + activated | Subordinate per §10 |
| 3 | M12 writer SAVEPOINT smoke evidence PR merged | Subordinate per §6 |
| 4 | M12 reader smoke evidence PR merged | Subordinate per §7 |
| 5 | E6 cross-schema grants verified | Read-only probe |
| 6 | Operator decision on rollback cliff treatment recorded + accepted (per §9) | This DBCP |
| 7 | Audit trail infrastructure ready (post-run evidence requirements per §11) | Subordinate or existing |
| 8 | Operator authorization of this gate | Per stance ADR DEC-7f9597 |

### 8.3 Mechanics

- Operator-authorized invocation of the M12 writer real-body with real panel-run inputs.
- A new `panel_run_uid` is generated for the run.
- The writer COMMITs to bcf.panel_output_record + mcf.metric_authoring_panel_run + mcf.metric_authoring_panel_transcript (3 rows) per the M12 DBCP semantics.
- Post-run independent verifier runs (per §11 P1..P7).
- **The cliff is crossed.** A5 rollback validity drops from outcome (A) to outcome (C) immediately.

### 8.4 Env-gate

```
BCCORE_MCF_M12_FIRST_REAL_RUN_CONFIRM=I_HAVE_REVIEWED_M14_UNBLOCK_<m14-unblock-ts>
```

The env-gate binds first-real-run authorization to the operator-authorized M14 unblock event timestamp.

### 8.5 Rollback semantics within the run

- The writer wraps its DML in a single transaction.
- If any step inside the transaction fails (FK violation, RAISE EXCEPTION from a trigger, etc.), the entire run rolls back.
- This intra-run rollback is mechanically equivalent to "the run never happened"; the A5 rollback envelope outcome remains (A).
- **Only a COMMIT crosses the cliff.**

### 8.6 What the gate does NOT do

- ❌ Does NOT authorize subsequent M12 panel runs (each may require its own evidence; or batch authorization may be permitted post-first-run; operator decision D11 below).
- ❌ Does NOT authorize M12.5 materialization (separate downstream gate).
- ❌ Does NOT authorize M13 PE-MC evaluator (separate downstream gate).
- ❌ Does NOT touch tenant DBs.

## 9. Rollback cliff treatment (the A→C transition)

The first real M12 panel run commits a new panel_run_uid to `bcf.panel_output_record` + a child row in `mcf.metric_authoring_panel_run`. That panel_run_uid does NOT exist in `contract.panel_output_record` (contract.* is FROZEN by A4 deny-write triggers; accepts no INSERTs). The A5 rollback envelope cliff (per Phase A5 DBCP §7.4) materializes:

- Pre-first-run: outcome (A) — A5 rollback clean.
- Post-first-run: outcome (C) — A5 rollback BLOCKED by guard #700 unless force-rollback-with-data-loss envelope is invoked.

### 9.1 Four treatment options

| Option | Description | Pros | Cons |
|---|---|---|---|
| **C1 accept the cliff** | Once first real M12 run lands, A5 rollback is BLOCKED indefinitely. No force-rollback envelope is authored. | Simplest; aligns with M-series being a one-way ratchet | No rollback path; high commitment from operator at first-real-run authorization |
| C2 force-rollback-with-data-loss envelope | Author a separate post-cliff contingency DBCP that defines a row-destructive rollback (DELETE mcf.* panel_run_uid rows; then run A5 rollback) | Provides an emergency unwind path | Row-destructive; operator decision on data-loss vs preserve-A5-state at the unwind moment |
| C3 deferrable dual-FK | Add the 5 mcf→contract FKs back alongside mcf→bcf, but DEFERRABLE INITIALLY DEFERRED; writer enforces dual-target consistency by writing the same panel_run_uid to both contract.panel_output_record (via bypassing deny-write triggers somehow) and bcf.panel_output_record | Theoretically allows graceful rollback | Requires bypassing A4 deny-write triggers (defeats A4 freeze purpose); semantically incompatible with the Option A boundary DBCP; **REJECTED — violates HR3** |
| C4 pre-cliff snapshot | Before authorizing first real run, snapshot bcf.panel_output_record + mcf.* state to S3 or a separate snapshot table; rollback restores from snapshot | Allows rollback restoration without row-destructive cleanup | Adds snapshot infrastructure; snapshot stale immediately after first run; deferred to C2 if rollback needed |

**Recommendation: C1 accept the cliff (default) + author C2 force-rollback-with-data-loss envelope as a SEPARATE post-M14-open contingency DBCP authored only if operator decides to preserve a rollback path.**

**C3 is REJECTED.** It would require the M12 writer to bypass A4 deny-write triggers, which structurally violates HR3 (MCF authority writes must NOT route to generic contract.*).

C4 is plausible but adds infrastructure complexity without changing the fundamental cliff topology; deferred to C2-equivalent envelope authoring if needed.

### 9.2 Consequence of C1 (recommended default)

- A5 rollback becomes BLOCKED once first real M12 run lands.
- Phase A4 rollback was already INVALID per D5.
- Combined Phase A3 + step 20 rollback was already INVALID per D9.
- **The substrate is effectively at a one-way ratchet from the first real M12 run forward.**

This is consistent with the boundary DBCP (Option A) intent: MCF authority lives in mcf.* / bcf.* permanently post-A5; rollback to contract.* is governance-end-of-life from this point.

## 10. M12 writer activation path

### 10.1 W1 real-body PR (recommended)

Replace `throw new M12NotImplementedError('writePanelRun')` in `src/registry/metric-authoring/m12-panel-run-writer.service.ts` with the real M12 writer body per the M12 DBCP (`metric-context-framework-m12-authoring-panel-dbcp.md`) and per A5 DBCP §5.2:

```ts
public async writePanelRun(input: M12PanelRunInput): Promise<...> {
  return this.db.transaction(async (tx) => {
    // 1. INSERT bcf.panel_output_record (panel anchor)
    await tx.insert(panelOutputRecord).values({ ... });
    // 2. INSERT mcf.metric_authoring_panel_run (MCF-specific extension; FK to bcf)
    await tx.insert(metricAuthoringPanelRun).values({ ... });
    // 3. INSERT 3 × mcf.metric_authoring_panel_transcript (per-model verdicts)
    await tx.insert(metricAuthoringPanelTranscript).values([{...}, {...}, {...}]);
    // 4. No contract.* writes (HR3 + structural deny-write triggers)
    return { panelRunUid: input.panelRunUid };
  });
}
```

The W1 PR is subordinate to this DBCP. It is gated on:
- This DBCP merge
- Separate operator authorization for the implementation PR
- The W1 PR's own apply gate (separate operator authorization) — although in this case "apply" = `npm run start:dev` of the modified service (no DDL/DML); the actual cliff-crossing happens at the first-real-run gate per §8.

### 10.2 W2 feature-flag-gated rollout (alternative)

Add a feature-flag check inside the writer body:
```ts
if (!featureFlag('mcf.m12.writer.enabled')) {
  throw new M12NotImplementedError('writePanelRun (feature flag disabled)');
}
```

The flag is operator-controlled at runtime; allows fine-grained gradual rollout.

**Recommendation: W1 real-body PR (no feature flag).** M14 unblock + first-real-run gate already provide the operator control; an additional feature flag adds runtime ambiguity without adding governance value.

## 11. Post-run evidence requirements

After the first real M12 panel run COMMITs, the operator must capture:

| # | Evidence | Verifier |
|---|---|---|
| P1 | `bcf.panel_output_record` row count incremented by 1 (was 19; now 20) | bc-postgres MCP read-only |
| P2 | `mcf.metric_authoring_panel_run` row count incremented by 1 (was 0; now 1) | bc-postgres MCP read-only |
| P3 | All 5 mcf→bcf FK constraints validated successfully (no `RAISE EXCEPTION` from FK enforcement) | post-run script + pg_stat / log inspection |
| P4 | contract.* deny-write triggers did NOT fire during the run (no `RAISE EXCEPTION` from deny-write triggers; verified by audit log + pg_stat_user_functions count for `contract.*_deny_write` functions) | post-run script + pg_stat |
| P5 | `bcf.cert` write-once trigger did NOT fire (M12 writes panel-run only; does NOT write cert; cert is written by M12.5 materialization downstream) | post-run script |
| P6 | Downstream consumer reads work: SELECT against mcf.metric_authoring_panel_run + JOIN to bcf.panel_output_record returns the new row | post-run script |
| P7 | Audit trail records the run: panel_run_uid + operator identity + apply-ts + sha256 of input payload | bc-core audit module (subordinate; may require its own implementation if not present) |

### 11.1 Independent post-run verifier

`scripts/mcf-m12-first-real-run-post-verify.mjs` — read-only verifier mirroring P1..P7 as a separate script process (analogous to A5 post-apply verifier). Env-gated by `BCCORE_MCF_M12_FIRST_REAL_RUN_POST_VERIFY_CONFIRM=I_HAVE_REVIEWED_FIRST_REAL_RUN_<run-ts>`.

### 11.2 Run identity binding

The post-run evidence includes:
- `panel_run_uid` (the new UUID)
- Apply timestamp
- sha256 of writer input payload (for reproducibility / audit)
- Operator identity (from env-gate)

## 12. Risk register R1..R12

| # | Risk | Mitigation |
|---|---|---|
| R1 | M12 writer real-body has a bug; first real run produces incorrect mcf.* shape | M12 writer SAVEPOINT smoke gate catches semantic bugs before commit; W1 PR is reviewed; unit tests for the real body required as part of W1 implementation |
| R2 | M12 writer accidentally writes to contract.* | A4 deny-write triggers structurally reject; writer code never imports contract.* symbols (lockfile assertion at PR #151); SAVEPOINT smoke verifies |
| R3 | First real run crosses the A→C cliff before operator is ready | First-real-run gate is operator-authorized and SEPARATE from M14 unblock; operator decision D6 + α prepare-only ensures gate discipline |
| R4 | Force-rollback envelope needed but not authored | C1 accepts the cliff as default; C2 envelope is deferred to separate contingency DBCP if operator decides to preserve rollback path |
| R5 | Cross-schema grants not configured; mcf.* readers can't SELECT bcf.panel_output_record | E6 evidence probe runs read-only check; if missing, operator-authorized GRANT statement is required before M14 unblock |
| R6 | M12.5 materialization not ready when M14 unblocks | M14 unblock per α only authorizes M12 writer activation; M12.5 + M13 remain gated independently |
| R7 | First real run runs but fails verification | Post-run independent verifier catches; rollback to pre-run state via row-destructive cleanup is required (C2 envelope post-cliff); high cost; operator decision at gate authorization |
| R8 | M12 writer SAVEPOINT smoke leaks committed state | Smoke explicitly wraps in BEGIN; SAVEPOINT; ROLLBACK TO; ROLLBACK; outer ROLLBACK discards all; assertion #810 verifies Δ=0 post-smoke |
| R9 | Reader smoke catches no issues because all mcf.* tables are empty | Reader smoke probes the FK chain integrity + grant verification independently of row contents; structural verification, not data verification |
| R10 | M14 unblock authorized prematurely | Pre-conditions E1-E7 explicit; all 7 must be met + accepted by operator at M14 unblock gate authorization |
| R11 | Tenant rollout pressure overrides discipline | Tenant scope explicitly deferred per §1.3; tenant onboarding requires its own separate DBCP chain |
| R12 | Operator confuses M14 unblock with first-real-run authorization | Option α (recommended) explicitly separates the two; PR descriptions + commit body Findings reinforce the separation |

## 13. Operator decisions D1..D14

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | M14 unblock mechanics | U1 single-shot / U2 staged / U3 per-tenant / U4 per-metric | **U2 staged** |
| D2 | M14 unblock semantics | α writer activation only / β writer activation + first real run | **α writer activation only** |
| D3 | Authorize M12 writer real-body implementation PR (subordinate) | YES / NO | **YES** (gated on this DBCP merge) |
| D4 | Authorize M12 writer SAVEPOINT smoke gate authoring + execution (subordinate) | YES / NO | **YES** (gated on M12 writer real-body PR merge) |
| D5 | Authorize M12 reader smoke gate authoring + execution (subordinate) | YES / NO | **YES** (gated on M12 writer SAVEPOINT smoke evidence merge) |
| D6 | Authorize M14 unblock apply gate authoring (subordinate) | YES / NO | **YES** (gated on writer + reader smoke evidence both merged) |
| D7 | Authorize first real M12 panel run gate authoring (subordinate) | YES / NO | **YES** (gated on M14 unblock apply complete) |
| D8 | Rollback cliff treatment | C1 accept / C2 force-rollback envelope authored / C3 deferrable dual-FK / C4 pre-cliff snapshot | **C1 accept + C2 envelope authored as SEPARATE post-M14-open contingency DBCP only if operator decides to preserve rollback path** |
| D9 | Writer activation path | W1 real-body PR / W2 feature-flag-gated | **W1 real-body PR** |
| D10 | Post-run evidence script authoring | YES (P1..P7 in separate verifier script) / NO (rely on writer-emitted evidence only) | **YES (separate verifier per §11.1)** |
| D11 | Subsequent M12 runs (post-first-run) authorization model | per-run operator gate / batch authorization / unrestricted | **per-run operator gate** until C2 envelope authored or operator chooses otherwise |
| D12 | Tenant DB rollout | OUT OF SCOPE | **OUT OF SCOPE — DEFERRED** |
| D13 | M12.5 + M13 + downstream M-series gates | OUT OF SCOPE for this DBCP | **OUT OF SCOPE — separate downstream DBCPs** |
| D14 | M14 stays CLOSED through this DBCP authoring | YES / NO | **YES** |

## 14. Hard rule mapping (HR1..HR5)

| Rule | This-DBCP-time status |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | This DBCP designs gates that preserve HR1: SAVEPOINT smoke writes a probe but rolls back; first real run writes real metric data; M14 unblock authorizes only the runtime path |
| **HR2** — MCF evidence belongs in `mcf.*` | A5 retarget achieved this structurally; M12 writer skeleton imports mcf-side; M12 writer real-body writes mcf.* and bcf.panel_output_record (the BCF anchor) |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.*` | A4 deny-write triggers structurally enforce; M12 writer skeleton + real-body never reference contract.*; C3 option rejected for HR3 violation |
| **HR4** — tenant result DBs separate | Tenant scope OUT OF SCOPE per D12; no tenant DB connection in any subordinate gate |
| **HR5** — production path; no mocks | M12 writer real-body uses real Drizzle symbols + real DB connection; SAVEPOINT smoke uses real DB with rollback; mocks confined to unit tests |
| **DEC-7f9597 / D423** | Every subordinate gate (M12 real-body PR / SAVEPOINT smoke / reader smoke / M14 unblock / first real run / post-run verify) requires separate operator authorization |

## 15. Standing gate state (target post-M14-unblock-apply + post-first-real-run)

| Gate | Pre-M14-unblock | Target post-M14-unblock | Target post-first-real-run |
|---|---|---|---|
| M14 | CLOSED | **OPEN (writer activation only per α)** | OPEN |
| M12 writer | SKELETON (throws) | **REAL-BODY ACTIVE (per W1)** | REAL-BODY ACTIVE |
| M12 panel runs executed | 0 | 0 | **≥1 (first real run committed)** |
| `bcf.panel_output_record` rows | 19 | 19 | **20** (or more) |
| `mcf.metric_authoring_panel_run` rows | 0 | 0 | **1** (or more) |
| A5 rollback envelope | AVAILABLE (outcome A) | AVAILABLE (outcome A) | **BLOCKED (outcome C)** unless C2 envelope invoked |
| Phase A4 rollback envelope | INVALID per D5 | INVALID | INVALID |
| Combined A3+step20 rollback envelope | INVALID per D9 | INVALID | INVALID |
| contract.* BCF evidence | FROZEN | FROZEN | FROZEN |
| Phase A5 substrate | APPLIED | APPLIED | APPLIED |

## 16. Sequencing record

The complete A1 → A2 → A3 → step 20 → A4 → A5 → M14/M12 chain:

1-26. ✓ Phase A1..A5 chain complete (per A5 closeout §11 items 1-26).
27. ✓ Phase A5 closeout (PR #22) merged — bc-docs-v3 main `2792c36`
28. ⏸ **MCF M14/M12 governance DBCP (THIS DOC)** — pending operator merge
29. ⏸ M12 writer real-body implementation PR (bc-core) — gated on this DBCP merge + separate operator authorization
30. ⏸ M12 writer SAVEPOINT smoke gate execution + evidence PR (bc-core) — gated on D4
31. ⏸ M12 reader smoke gate execution + evidence PR (bc-core) — gated on D5
32. ⏸ M14 unblock apply DBCP (bc-docs-v3) — gated on D6 + smoke evidence merged
33. ⏸ M14 unblock apply execution + evidence PR (bc-core) — gated on M14 unblock apply DBCP merge + separate operator authorization
34. ⏸ M14 unblock closeout (bc-docs-v3) — records M14 OPEN state
35. ⏸ First real M12 panel run authorization DBCP (bc-docs-v3) — gated on D7 + M14 unblock complete
36. ⏸ First real M12 panel run execution + evidence PR (bc-core) — the cliff-crossing event; outcome A→C transition
37. ⏸ First real M12 panel run closeout (bc-docs-v3) — records the first-real-run event + post-run evidence
38. ⏸ Optional: force-rollback-with-data-loss envelope DBCP (bc-docs-v3; per D8 C2) — gated on operator decision to preserve rollback path
39. ⏸ Post-first-real-run subsequent gates (per D11) — per-run authorization or batch authorization per operator decision
40. ⏸ M12.5 materialization + M13 PE-MC evaluator + M-series downstream gates — separate downstream DBCPs (out of this DBCP scope)
41. ⏸ Post-A5 DROP slice (F4 HYBRID roadmap per A4 closeout §6 + A5 D11) — orthogonal; gated on stable M12 operation + separate governance gate
42. ⏸ Tenant DB rollout — separate DBCP chain (out of this DBCP scope per D12)

## 17. Out-of-scope re-statement

This DBCP does **NOT** apply DDL.

This DBCP does **NOT** apply DML.

This DBCP does **NOT** modify bc-core code.

This DBCP does **NOT** authorize the M12 writer real-body implementation PR's apply — that is a SEPARATE operator authorization gated on this DBCP merge.

This DBCP does **NOT** invoke M12.

This DBCP does **NOT** unblock M14.

This DBCP does **NOT** authorize first real M12 panel run.

This DBCP does **NOT** execute A5 rollback or any prior phase rollback.

This DBCP does **NOT** author the M12.5 / M13 / downstream M-series DBCPs.

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** alter `bcf.*`, `contract.*`, `mcf.*`, `metric.*`, or `concept_registry.*` substrate.

This DBCP does **NOT** initiate any synthetic / mock / replay / canned data writes.

This DBCP does **NOT** author the post-A5 DROP slice (F4 HYBRID roadmap; deferred per A4 closeout §6.3 + A5 D11).

This DBCP does **NOT** author the force-rollback-with-data-loss envelope (C2 deferred to separate post-M14-open contingency DBCP only if operator decides).

---

**End of DBCP. M14/M12 governance design RECORDED. Next operator-authorized gate: M12 writer real-body implementation PR authoring (subordinate per D3).**
