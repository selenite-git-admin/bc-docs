---
uid: metric-context-framework-m14-unblock-apply-dbcp
title: MCF — M14 unblock apply DBCP (Option α writer-activation-only; first-real-run remains gated)
description: Subordinate DBCP for the M14 unblock apply gate per locked D6 of the MCF M14/M12 governance DBCP (bc-docs-v3 main `6d20c8d` / PR #23). Designs the operator-authorized apply gate that flips M14 from CLOSED to OPEN under Option α semantics: M14 OPEN authorizes the M12 writer to be invocable at runtime entry points but does NOT authorize the first real M12 panel run (that remains a separate D7-gated operator authorization with its own env-gate, cliff-crossing event, and post-run evidence requirements). Substrate state pre-apply: A4 freeze invariants preserved (12 contract.* deny-write triggers + 4 functions LIVE; contract.cert C2 DROPPED; bcf.cert write-once LIVE); A5 retarget complete (5 mcf→bcf FKs LIVE; 5 mcf→contract FKs DROPPED); bcf/contract rows 19/0/19/3530 each; mcf.* panel_run_uid rows 0 across all 5 retargeted tables (cliff predicate guard #700 PASSes; outcome A preserved); M12 writer real-body landed at bc-core main `f1a5992` (PR #154) but unwired from any runtime entry point; M12 writer SAVEPOINT smoke completed at bc-core main `b729a35` (PR #155; 19/19 PASS); M12 reader smoke completed at bc-core main `9620db7` (PR #156; 17/17 PASS); E1-E7 evidence MET per M14/M12 governance DBCP §5. Enumerates the apply mechanics (3 options M1/M2/M3); env-gate + operator confirmation string; 11 pre-unblock guards (G1..G11) covering E1-E7 + writer body + smoke evidence + cliff state + M14 currently CLOSED; "M14 open" operational meaning (wiring scope; what remains forbidden until D7); 7 post-unblock verifications (V1..V7); rollback/close mechanics (reverse path; outcome A preservation invariant); first-real-M12-run handoff specification per locked D7 (subordinate gate); risk register R1..R10; operator decisions D1..D8. **NOT EXECUTED.** This DBCP authorizes design only; the M14 unblock apply gate execution is a separately operator-authorized follow-up. **No DDL applied, no DML applied, no `BCCORE_M14_OPEN` set, no M14 unblock, no M12 invocation, no first real M12 panel run, no tenant DB connection, no rollback executed.** Operator stance ADR DEC-7f9597 / D423 honoured — operator authorization required on every mutating gate (including M14 unblock and first real M12 panel run as separate gates); A5 rollback envelope outcome (A) preserved through this DBCP authoring.
status: draft
date: 2026-05-29
project: bc-docs
domain: contracts
subdomain: governance
focus: mcf-m14-unblock-apply-writer-activation-only
supersedes:
superseded_by:
---

# MCF — M14 unblock apply DBCP

## 1. Scope

### 1.1 Question this DBCP answers

> Per locked D6 of the MCF M14/M12 governance DBCP (bc-docs-v3 main `6d20c8d` / PR #23), the M14 unblock apply gate is the subordinate gate that flips M14 from CLOSED to OPEN. Per locked D2 (α writer activation only), M14 unblock authorizes the M12 writer to be invocable at runtime but does NOT authorize the first real M12 panel run (that is a separate D7-gated event). Evidence pre-conditions E1-E7 are all MET as of bc-core main `9620db7` (PR #156 reader smoke). What is the apply-gate design — mechanics, env-gate, pre-unblock guards, "M14 open" operational semantics, post-unblock verification, rollback/close path, and the handoff specification for the subordinate first-real-M12-run gate — under Option α prepare-only?

### 1.2 In scope

- **Substrate inventory post-PR-#156** — 5 mcf→bcf FKs LIVE; 12 contract.* deny-write triggers + 4 functions LIVE; contract.cert C2 DROPPED state preserved; bcf.cert write-once LIVE; bcf/contract rows 19/0/19/3530 each; mcf.* panel_run_uid rows 0 (outcome A preserved); M12 writer real-body LIVE at bc-core main but unwired.
- **M14 unblock apply mechanics** — 3 options (M1 NestJS module registration / M2 controller wiring / M3 env-gated runtime invocation) under Option α writer-activation-only.
- **Env-gate + operator confirmation string** — `BCCORE_M14_UNBLOCK_CONFIRM=I_HAVE_REVIEWED_M12_WRITER_REAL_BODY_<m12-writer-real-body-merge-ts>_AND_SMOKE_<reader-smoke-ts>`.
- **Pre-unblock guards G1..G11** — E1-E7 + writer body + writer SAVEPOINT smoke + reader smoke + cliff state + M14 currently CLOSED.
- **"M14 open" operational meaning** — what code/config/wiring changes; what remains FORBIDDEN until first-real-run gate (D7).
- **Post-unblock verification V1..V7** — M14 OPEN state visible; writer still not invoked at runtime (between unblock and first-real-run); mcf.* rows still 0; cliff predicate still PASSes.
- **Rollback/close behavior** — reverse the unblock if first-real-run is deferred indefinitely or if operator decides to re-close before any real run; A5 rollback outcome (A) preservation invariant.
- **First real M12 run handoff** — specification for the subordinate D7 gate: env-gate, pre-run substrate checks, post-run evidence, cliff-crossing warning.
- **Risk register R1..R10** + **operator decisions D1..D8**.
- Authorization to author the bc-core M14 unblock apply implementation in a follow-up; that PR's apply gate is a SEPARATE operator authorization.

### 1.3 Explicit non-scope

- ❌ **No DDL applied.** This DBCP designs the M14 unblock; the apply gate execution is a separately operator-authorized follow-up.
- ❌ **No DML applied.** No row mutation on `bcf.*` / `contract.*` / `mcf.*` / any tenant DB.
- ❌ **No bc-core code change.** Authoring the M14 unblock implementation PR is a SEPARATE follow-up operator authorization.
- ❌ **No `BCCORE_M14_OPEN` set.** M14 stays CLOSED throughout this DBCP authoring.
- ❌ **No M14 unblock executed.** The apply gate execution is a separately operator-authorized gate.
- ❌ **No M12 invocation.** Writer remains unwired; no runtime entry point activated.
- ❌ **No first real M12 panel run.** That is a SEPARATE D7 operator-authorized gate per the M14/M12 governance DBCP §8.
- ❌ **No M12.5 / M13 / downstream M-series invocation.** Per M14/M12 governance D13 OUT OF SCOPE.
- ❌ **No tenant DB connection.** Per M14/M12 governance D12 OUT OF SCOPE.
- ❌ **No A5 rollback executed.** A5 rollback envelope remains AVAILABLE at outcome (A).
- ❌ **No A4 rollback executed.** A4 rollback envelope is INVALID per A5 D5.
- ❌ **No combined Phase A3 + step 20 rollback executed.** INVALID per D9.
- ❌ **No PR #11 / #12 / #13 / #14 / #15 / #16 / #17 / #18 / #19 / #20 / #21 / #22 / #23 re-touch.**
- ❌ **No PR #141..#156 re-touch.**
- ❌ **No synthetic / mock / replay / canned data writes.** HR1 substrate-enforced.
- ❌ **No bc-admin / bc-portal UI changes.**

## 2. Authority anchor chain

| Artifact | Location | Authority for |
|---|---|---|
| Boundary DBCP (Option A) | `docs/implementation/bcf-mcf-evidence-boundary-and-contract-schema-retirement-dbcp.md` @ bc-docs-v3 main `6f8cc15` (PR #11) | Schema-boundary design; M-series ownership of mcf.* substrate |
| **MCF M14/M12 governance DBCP (D1..D14)** | `docs/implementation/metric-context-framework-m14-m12-governance-dbcp.md` @ bc-docs-v3 main `6d20c8d` (PR #23) | D2 α writer activation only; D6 M14 unblock apply (THIS DBCP is the subordinate); D7 first real M12 run (subordinate to THIS DBCP); D8 C1 accept cliff; D9 W1 real-body PR |
| Phase A5 closeout | `docs/implementation/bcf-evidence-schema-phase-a5-closeout.md` @ bc-docs-v3 main `2792c36` (PR #22) | Substrate state post-A5; outcome (A) cliff status |
| Phase A4 closeout | `docs/implementation/bcf-evidence-schema-phase-a4-closeout.md` @ bc-docs-v3 main `757071a` (PR #20) | A4 freeze invariants (12 deny-write triggers + 4 functions) |
| Phase A5 apply + post-apply evidence | bc-core main `99edc1b` (PR #153) | A5 apply-ts `2026-05-29T13-07-48-822Z` |
| **MCF M12 writer real-body** | bc-core main `f1a5992` (PR #154) | W1 real-body of `M12PanelRunWriterService.writePanelRun()`; 24/24 unit tests PASS; lockfile 50/50 PASS |
| **MCF M12 writer SAVEPOINT smoke** | bc-core main `b729a35` (PR #155) | Substrate-level smoke evidence: BEGIN/SAVEPOINT/ROLLBACK pattern; 19/19 PASS; substrate Δ=0 |
| **MCF M12 reader smoke** | bc-core main `9620db7` (PR #156) | Reader-path discipline evidence: 17/17 PASS; E1-E7 + cross-schema grants verified |
| **bc-docs-v3 anchor (this DBCP base)** | bc-docs-v3 main `6d20c8dbe5b0ab09603f929596e5053f6c1a2d9a` (post-PR-#23 merge) | Governance authority for subordinate M14 unblock apply gate |
| bc-core anchor (subordinate M14 unblock impl PR base) | bc-core main `9620db7be776809d37cbf7333b22b0355e5ba040` | Code state the future M14 unblock impl PR will modify |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) | Operator authorization on every mutating gate; rollback discipline |
| Hard rules HR1..HR5 | Boundary DBCP §5 | Substrate constraints this design must respect |

## 3. Current substrate state (verified live)

### 3.1 Post-A5 + M12 writer real-body + smoke evidence state

| Substrate / artifact | Live state |
|---|---|
| 5 mcf→bcf FKs (`fk_mcf_cert_panel_run` + `fk_mapr_panel_run` + `fk_mcr_panel_run` + `fk_mper_panel_run` + `fk_mcs_panel_run`) | LIVE; all RESTRICT/NO ACTION |
| 5 mcf→contract FKs | DROPPED (A5) |
| `contract.*` deny-write functions | 4 LIVE (A4 freeze preserved) |
| `contract.*` deny-write triggers | 12 LIVE (A4 freeze preserved) |
| `contract.cert` born-null trigger + function | 0 / 0 (DROPPED per A4 C2; preserved) |
| `bcf.cert` write-once function | 1 LIVE |
| `bcf.cert` write-once trigger rows | 2 LIVE (INSERT + UPDATE) |
| `bcf.panel_output_record` rows | 19 |
| `contract.panel_output_record` rows | 19 |
| `mcf.*` panel_run_uid rows (5 retargeted tables) | 0 (each) |
| `mcf.certification_record` rows | 0 |
| M12 writer real-body | LIVE at bc-core main `9620db7` |
| M12 writer runtime entry points (controller / scheduler / queue listener) | NONE — service is unwired |
| M14 governance gate | CLOSED |
| M12 writer SAVEPOINT smoke evidence | LANDED at bc-core main `b729a35`; 19/19 PASS |
| M12 reader smoke evidence | LANDED at bc-core main `9620db7`; 17/17 PASS |
| A5 rollback envelope | AVAILABLE; outcome (A) preserved |
| Phase A4 rollback envelope | INVALID per A5 D5 |
| Combined Phase A3 + step 20 rollback envelope | INVALID per D9 |

### 3.2 Evidence pre-conditions E1-E7 status

| # | Evidence | Source | Status |
|---|---|---|---|
| E1 | Live FK inventory (5 mcf→bcf FKs with RESTRICT/NO ACTION) | Phase A5 closeout PR #22 + reader smoke #901 + #910 | ✓ MET |
| E2 | Live trigger inventory (12 contract.* deny-write triggers + 4 functions LIVE; contract.cert C2 DROPPED; bcf.cert write-once LIVE) | Phase A5 closeout PR #22 + reader smoke #906-#908 | ✓ MET |
| E3 | Live row inventory baseline | Phase A5 closeout PR #22 + reader smoke #900 + #903-#905 | ✓ MET |
| E4 | M12 writer SAVEPOINT smoke evidence | bc-core PR #155 (19/19 PASS) | ✓ MET |
| E5 | M12 reader smoke evidence | bc-core PR #156 (17/17 PASS) | ✓ MET |
| E6 | Cross-schema grants verified | bc-core PR #156 reader smoke #909 (`has_table_privilege` = true) | ✓ MET |
| E7 | Operator decision on rollback cliff treatment | M14/M12 governance DBCP D8 (C1 accept + C2 deferred) | ✓ MET |

**All 7 evidence pre-conditions MET.** M14 unblock apply gate is structurally ready.

## 4. M14 unblock apply mechanics

### 4.1 Three options for M14 unblock implementation

| Option | Description | Pros | Cons |
|---|---|---|---|
| **M1 NestJS module registration only** | Register `M12PanelRunWriterService` in a NestJS module (e.g. `MetricAuthoringModule`); service becomes available via DI but no new runtime entry point is wired | Minimal change; service callable from any module that imports it; no new HTTP/scheduler/queue surface | Service is technically invocable from any wired-in caller; relies on D7 first-run gate for actual invocation discipline |
| M2 controller wiring | M1 + add a guarded controller endpoint (e.g. `POST /api/mcf/m12/panel-runs` with operator-auth guard) | Provides an HTTP surface for the first real run | Adds new HTTP attack surface BEFORE first real run authorized; couples M14 unblock with HTTP discipline |
| M3 env-gated runtime invocation | M1 + a wrapper that checks `BCCORE_M14_OPEN` env-var at runtime before allowing `writePanelRun()` to proceed | Runtime gate enforces M14 state; safest | Requires writer code modification (re-introduces a refusal path); contradicts the D9 W1 no-feature-flag policy at PR #23 |

**Recommendation: M1 NestJS module registration only.** Aligns with locked D9 W1 (no feature flag), D2 α writer activation only, and D6 separate first-real-run gate. The writer becomes invocable via DI but is not actually called from any wired-in caller until the D7 first-real-run gate ships.

### 4.2 What the M1 implementation PR adds (operator-readable)

The subordinate M14 unblock implementation PR (gated on this DBCP merge) adds:
1. A NestJS module declaration (e.g. `MetricAuthoringModule` at `src/registry/metric-authoring/metric-authoring.module.ts`) that registers `M12PanelRunWriterService` as a provider.
2. The module is imported into the application root module (e.g. `AppModule`).
3. **No new controllers, no new schedulers, no new queue listeners, no new HTTP routes.** The writer is reachable only through future DI consumers — which are gated on the D7 first-real-run gate's implementation.

The M14 unblock apply gate runs:
- A pre-unblock script that verifies G1..G11 (per §5) read-only against the live substrate + repo state.
- The operator-authorized merge of the M14 unblock implementation PR (the NestJS module registration).
- A post-unblock script that verifies V1..V7 (per §7) read-only.

The apply gate does NOT execute DDL/DML on the platform DB. The "apply" is a code merge + read-only verification.

### 4.3 Env-gate + operator confirmation string

Per stance ADR DEC-7f9597 / D423: the apply gate is operator-authorized via env-gate.

```
BCCORE_M14_UNBLOCK_CONFIRM=I_HAVE_REVIEWED_M12_WRITER_REAL_BODY_<bc-core-pr-154-merge-ts>_AND_SMOKE_<reader-smoke-ts>
```

The two timestamps bind the apply authorization to:
- PR #154 merge-ts (`2026-05-29T13:54:32Z` — bc-core M12 writer real-body merge)
- PR #156 reader smoke-ts (`2026-05-29T15-09-14-306Z`)

The literal env-gate value for this apply gate is therefore:
```
BCCORE_M14_UNBLOCK_CONFIRM=I_HAVE_REVIEWED_M12_WRITER_REAL_BODY_2026-05-29T13-54-32Z_AND_SMOKE_2026-05-29T15-09-14-306Z
```

**Note:** the exact PR #154 merge-ts is recorded in the M14/M12 governance gate ship chain (current state §15 of PR #23). The operator confirms the value at apply time by reading the bc-core git log.

## 5. Pre-unblock guards G1..G11

The pre-unblock script (`scripts/mcf-m14-unblock-pre-check.mjs` — subordinate implementation PR) verifies all 11 guards as read-only checks. Apply gate refuses to merge the implementation PR if any guard fails.

| # | Guard | Predicate |
|---|---|---|
| G1 | `e1_e7_evidence_met` | All 7 evidence anchors merged: PR #22 (A5 closeout) + PR #154 (writer real-body) + PR #155 (SAVEPOINT smoke) + PR #156 (reader smoke); recorded in this DBCP §3.2 |
| G2 | `m12_writer_real_body_merged` | bc-core main contains `M12PanelRunWriterService` class with `writePanelRun()` method that does NOT throw `M12NotImplementedError` (lockfile assertion at bc-core main `f1a5992`+) |
| G3 | `m12_writer_savepoint_smoke_merged` | bc-core main has commit `b729a35` or descendant; smoke evidence JSONL present with 19/19 PASS |
| G4 | `m12_reader_smoke_merged` | bc-core main has commit `9620db7` or descendant; reader smoke evidence JSONL present with 17/17 PASS |
| G5 | `mcf_panel_run_uid_rows_zero_across_all_5_retargeted_tables` | Count of `panel_run_uid IS NOT NULL` rows in mcf.metric_authoring_panel_run + mcf.metric_authoring_panel_transcript + mcf.certification_record + mcf.metric_contract_revision + mcf.metric_publication_eligibility_result + mcf.metric_supersession = 0 (cliff predicate guard #700 PASSes; outcome A intact) |
| G6 | `a5_rollback_outcome_a_preserved` | Inferred from G5 + presence of 5 mcf→bcf FKs (LIVE) + bcf.panel rows ≥ 19 |
| G7 | `m14_currently_closed` | `BCCORE_M14_OPEN` env-var NOT set in the current shell environment (the apply gate cannot run if M14 is already OPEN) |
| G8 | `a4_freeze_invariants_intact` | 12 contract.* deny-write triggers + 4 functions LIVE; contract.cert C2 DROPPED state preserved; bcf.cert write-once LIVE |
| G9 | `a5_topology_intact` | 5 mcf→bcf FKs LIVE; 0 mcf→contract FKs |
| G10 | `m12_writer_not_yet_wired_to_runtime_entry_point` | Static grep: no `@Controller`, no `@Cron`, no `@Scheduled`, no `@MessagePattern`, no `@EventPattern` on the M12 writer service file pre-apply |
| G11 | `env_gate_value_matches_expected_pattern` | `BCCORE_M14_UNBLOCK_CONFIRM` env-var matches `^I_HAVE_REVIEWED_M12_WRITER_REAL_BODY_<ts>_AND_SMOKE_<ts>$` |

If any guard fails, the apply gate refuses to proceed. The operator must address the failing guard before re-attempting.

## 6. "M14 open" operational meaning

Once M14 is OPEN (per Option α), the following is true at the runtime layer:

### 6.1 What changes (under M1)

- `M12PanelRunWriterService` is registered as a NestJS DI provider via `MetricAuthoringModule`.
- The service can be `@Inject()`-ed into any other service or controller that imports `MetricAuthoringModule`.
- The writer real-body is reachable through DI.
- A post-unblock state probe verifies M14 is visibly OPEN (e.g. by inspecting the NestJS application's loaded module list or the lockfile assertions about `MetricAuthoringModule` presence).

### 6.2 What remains FORBIDDEN until D7 first-real-run gate

| Forbidden | Reason |
|---|---|
| Invocation of `writePanelRun()` against the live platform DB | First real M12 panel run is a separate D7-gated operator-authorized event; substrate cliff crossing materializes only on COMMIT |
| Setting `BCCORE_M12_FIRST_REAL_RUN_CONFIRM` env-gate | That env-gate authorizes the D7 gate; not part of M14 unblock |
| Wiring the writer to a controller / scheduler / queue listener | Adds a runtime trigger surface; not authorized by M14 unblock (Option α covers writer activation only) |
| Tenant DB connection | Per M14/M12 governance D12 OUT OF SCOPE; tenant rollout is a separate downstream chain |
| M12.5 materialization invocation | Per M14/M12 governance D13 OUT OF SCOPE; downstream M-series gate |
| M13 PE-MC evaluator invocation | Per M14/M12 governance D13 OUT OF SCOPE; downstream M-series gate |
| Any `contract.*` DML | A4 deny-write triggers structurally reject |

### 6.3 What stays the same

- bcf.* substrate unchanged
- contract.* substrate FROZEN (A4 freeze preserved)
- mcf.* substrate row counts unchanged (rows = 0 across all 5 retargeted tables until D7 gate fires)
- A5 rollback envelope outcome (A) preserved
- All hard rules HR1..HR5 + DEC-7f9597 / D423 honoured

## 7. Post-unblock verification V1..V7

After the apply gate completes and the M14 unblock implementation PR is merged + the operator restarts services with the new code, the post-unblock verifier runs read-only checks:

| # | Verification | Predicate |
|---|---|---|
| V1 | `m14_open_state_visible` | A read-only probe confirms the `MetricAuthoringModule` is registered (e.g. a health endpoint returns it in module list, or a static lockfile assertion confirms the module declaration) |
| V2 | `m12_writer_di_resolvable` | A separate operator-authorized health probe confirms `M12PanelRunWriterService` is resolvable via DI without throwing |
| V3 | `m12_writer_not_invoked_at_runtime` | `mcf.metric_authoring_panel_run` panel_run_uid rows = 0; mcf.* rows unchanged from pre-unblock baseline (writer is registered but not called by any wired-in consumer between M14 unblock and the D7 gate) |
| V4 | `mcf_substrate_rows_unchanged` | All 5 retargeted mcf.* tables still 0 panel_run_uid rows |
| V5 | `cliff_predicate_still_passes` | A5 rollback envelope guard #700 (`a5_rollback_no_post_a5_mcf_rows`) still PASSes |
| V6 | `first_real_m12_run_still_not_authorized` | `BCCORE_M12_FIRST_REAL_RUN_CONFIRM` env-var NOT set (separate D7 gate) |
| V7 | `a4_freeze_invariants_preserved` | 12 deny-write triggers + 4 functions LIVE; contract.cert C2 DROPPED; bcf.cert write-once LIVE |

## 8. Rollback / re-close M14 before first-real-run

If the operator decides to re-close M14 before any first real run (e.g. for additional smoke evidence, deferred rollout, or governance review), the reverse path is:

### 8.1 Mechanics

1. Operator-authorized revert of the M14 unblock implementation PR (the NestJS module registration removal).
2. Restart services without the M12 writer registered.
3. Re-run pre-unblock guards G1..G11 — G7 should now PASS again (M14 CLOSED).
4. Optional: re-run post-close verifier to confirm `MetricAuthoringModule` is no longer registered.

### 8.2 Outcome (A) invariant

**As long as no first real M12 panel run has COMMITted between M14 unblock and re-close, A5 rollback outcome (A) is preserved.** The mcf.* panel_run_uid rows remain 0; cliff predicate guard #700 continues to PASS; the A5 rollback envelope remains available without resorting to outcome (C) force-rollback-with-data-loss.

### 8.3 Once first real M12 run COMMITs

After the D7 gate fires and the first real M12 panel run commits (with a fresh panel_run_uid landing in `bcf.panel_output_record` + `mcf.metric_authoring_panel_run`), the A→C cliff materializes (per Phase A5 DBCP §7.4 and M14/M12 governance DBCP §9). Re-closing M14 at that point does NOT restore outcome (A) — the cliff is one-way per locked D8 C1 accept.

## 9. First real M12 panel run handoff (subordinate D7 gate)

The first real M12 panel run is a SEPARATE operator-authorized gate per locked D7 of the M14/M12 governance DBCP. This DBCP enumerates the handoff specification — the D7 gate's own DBCP authoring is a separate follow-on.

### 9.1 D7 gate env-gate

```
BCCORE_M12_FIRST_REAL_RUN_CONFIRM=I_HAVE_REVIEWED_M14_UNBLOCK_<m14-unblock-ts>
```

The env-gate binds first-real-run authorization to the operator-authorized M14 unblock event timestamp.

### 9.2 D7 gate pre-run substrate checks

The D7 gate's pre-run verifier (subordinate to D7's own DBCP) MUST confirm:
- M14 is OPEN (V1 from §7 still PASSes)
- Writer is registered + DI-resolvable (V2 still PASSes)
- mcf.* panel_run_uid rows still 0 (V3 still PASSes; cliff predicate intact pre-run)
- A4 freeze invariants intact (V7 still PASSes)
- Operator-authorized env-gate value matches expected pattern

### 9.3 D7 gate post-run evidence (per M14/M12 governance §11 P1..P7)

After the first real M12 panel run COMMITs, the operator captures:
- **P1** — bcf.panel_output_record row count incremented by 1 (was 19; now 20)
- **P2** — mcf.metric_authoring_panel_run panel_run_uid rows incremented by 1 (was 0; now 1)
- **P3** — All 5 mcf→bcf FK constraints validated successfully
- **P4** — contract.* deny-write triggers did NOT fire during the run
- **P5** — bcf.cert write-once trigger did NOT fire (M12 writes panel-run only, not cert)
- **P6** — Downstream consumer reads work: SELECT + JOIN returns the new row
- **P7** — Audit trail records the run (panel_run_uid + operator identity + run-ts)

### 9.4 D7 gate cliff-crossing warning

**The first real M12 panel run is the cliff-crossing event.** As of COMMIT:
- A5 rollback envelope outcome transitions from (A) clean to (C) BLOCKED.
- Guard #700 (`a5_rollback_no_post_a5_mcf_rows`) FAILs.
- A5 rollback alone cannot revert without row-destructive cleanup or operator-authorized force-rollback-with-data-loss envelope (deferred per locked D8 C2).
- Combined Phase A4 + Phase A5 rollback requires A5 force-rollback-with-data-loss envelope to be authored + executed FIRST.

**This is a one-way ratchet.** Operator should review the D7 gate's authorization with full awareness of the cliff materialization.

## 10. Risk register R1..R10

| # | Risk | Mitigation |
|---|---|---|
| R1 | M14 unblocked but M12 writer accidentally invoked at runtime before D7 gate | NestJS module registration alone does not invoke; no controller/scheduler/queue listener wired (G10 + V3); D7 gate's own pre-run checks add a second layer |
| R2 | Operator confuses M14 unblock with D7 first-real-run authorization | Separate env-gates (`BCCORE_M14_UNBLOCK_CONFIRM` vs `BCCORE_M12_FIRST_REAL_RUN_CONFIRM`); separate DBCPs; separate apply gates; documented at every level |
| R3 | M14 unblock implementation PR ships wiring that activates the writer | Lockfile assertion on `M12PanelRunWriterService` file: no `@Controller`, no `@Cron`, no `@Scheduled`, no `@MessagePattern`, no `@EventPattern` decorators (already present at PR #154 lockfile); new `MetricAuthoringModule` file lockfile assertions to be added: no controller registration, no scheduler registration |
| R4 | M14 stays OPEN indefinitely without a first-real-run gate | Re-close path per §8 is available; outcome (A) preserved as long as no real run COMMITs; operator can defer first-real-run indefinitely without consuming the cliff |
| R5 | M14 unblock fails because evidence E1-E7 anchors drift | G1..G11 are read-only checks against live substrate + commit history; if any anchor changes (e.g. a smoke evidence PR gets reverted), the corresponding guard FAILs and the apply gate refuses |
| R6 | Operator forgets to re-run pre-unblock checks after a substrate change | Pre-unblock script is mandatory before the M14 unblock implementation PR can be merged; the apply gate is operator-authorized but the guards are enforcement |
| R7 | M14 unblock occurs while `BCCORE_M14_OPEN` was previously set in some other shell | G7 verifies the CURRENT shell does not have `BCCORE_M14_OPEN` set; the apply gate's verification is per-invocation |
| R8 | Re-close M14 before first-real-run loses any evidence | Re-close mechanics in §8 explicitly preserve outcome (A) invariant; no evidence is lost (PR merges + reverts are preserved in git history) |
| R9 | First-real-run gate fires accidentally during M14 unblock window | D7 gate has its own env-gate (`BCCORE_M12_FIRST_REAL_RUN_CONFIRM`); the M14 unblock apply gate does NOT set or unset that env-var |
| R10 | M14 unblock authorizes more than intended (e.g. M12.5 / M13 wiring) | Lockfile assertions on the M14 unblock implementation PR will restrict scope to `MetricAuthoringModule` registration + `M12PanelRunWriterService` provider declaration only; M12.5 / M13 modules remain unregistered |

## 11. Operator decisions D1..D8

| # | Decision | Options | Recommendation |
|---|---|---|---|
| D1 | M14 unblock mechanics | M1 NestJS module registration / M2 controller wiring / M3 env-gated runtime invocation | **M1 NestJS module registration only** |
| D2 | Authorize bc-core M14 unblock implementation PR authoring after this DBCP merges | YES / NO | **YES** (gated on this DBCP merge) |
| D3 | Authorize the M14 unblock apply gate execution after the implementation PR merges | YES / NO | **YES** (subordinate gate; separate operator authorization at apply time) |
| D4 | Authorize the D7 first-real-run gate DBCP authoring after M14 unblock completes | YES / NO | **YES** (gated on M14 unblock closeout) |
| D5 | First-real-run gate model | per-run operator authorization / batch after first real run / unrestricted | **per-run operator authorization** (mirrors M14/M12 governance D11) |
| D6 | C2 force-rollback-with-data-loss envelope DBCP authoring timing | author now (pre-first-real-run) / defer until needed | **defer until needed** (per M14/M12 governance D8 default; C1 accept) |
| D7 | M14 re-close authorization model (if needed before first-real-run) | per-event operator authorization / standing approval | **per-event operator authorization** |
| D8 | M14 unblock apply gate post-close requirements (if re-closed before first-real-run) | post-close evidence script + re-merge of evidence anchors / lightweight | **post-close evidence script** (mirrors apply gate pre-unblock guards G1..G11 in reverse) |

## 12. Hard rule mapping (HR1..HR5)

| Rule | This-DBCP-time status |
|---|---|
| **HR1** — no synthetic / mock / replay / canned data in persistent substrate | This DBCP designs only the NestJS module registration; no synthetic data path is enabled or considered. M12 writer real-body enforces HR1 by requiring real `model_identity_json.maker.provider` values (substrate CHECK rejects synthetic) |
| **HR2** — MCF evidence belongs in `mcf.*` | A5 retarget achieved this structurally; M12 writer real-body writes to mcf.* via bcf.* anchor; M14 unblock does not change substrate routing |
| **HR3** — MCF metric authority events MUST NOT write to generic `contract.*` | A4 deny-write triggers structurally enforce; M12 writer real-body never imports contract.* (lockfile + unit test); M14 unblock does not enable any contract.* write path |
| **HR4** — tenant result DBs separate | Tenant scope OUT OF SCOPE per M14/M12 governance D12; no tenant DB connection in M14 unblock implementation or apply gate |
| **HR5** — production path; no mocks | M14 unblock targets the live `bc_platform_dev` runtime registration; mocks confined to unit tests |
| **DEC-7f9597 / D423** | Every mutating gate is operator-authorized: M14 unblock apply (this DBCP's subordinate gate) + D7 first-real-run gate + re-close gate. A5 rollback outcome (A) preservation invariant honoured pre-first-real-run |

## 13. Standing gate state target (post-M14-unblock-apply)

| Gate | Pre-M14-unblock | Target post-M14-unblock | Target post-first-real-run (D7) |
|---|---|---|---|
| M14 | CLOSED | **OPEN (writer activation only per α)** | OPEN |
| M12 writer code | LANDED (PR #154) | LANDED + REGISTERED via `MetricAuthoringModule` | LANDED + REGISTERED + INVOKED at least once |
| M12 panel runs executed | 0 | 0 (cliff predicate still PASSes) | **≥1 (first real run COMMITted)** |
| `bcf.panel_output_record` rows | 19 | 19 | **20** (or more) |
| `mcf.metric_authoring_panel_run` panel_run_uid rows | 0 | 0 | **1** (or more) |
| A5 rollback envelope outcome | (A) AVAILABLE | (A) AVAILABLE — preserved | **(C) BLOCKED** unless C2 envelope invoked |
| Phase A4 rollback envelope | INVALID per A5 D5 | INVALID | INVALID |
| `contract.*` BCF evidence | FROZEN | FROZEN | FROZEN |
| Phase A5 substrate | APPLIED | APPLIED | APPLIED |

## 14. Sequencing record

The complete A1 → A2 → A3 → step 20 → A4 → A5 → MCF M14/M12 → M14 unblock chain:

1-27. ✓ Phase A1..A5 chain complete (per A5 closeout §11 items 1-26 + items 27-30).
28. ✓ MCF M14/M12 governance DBCP (PR #23) merged — bc-docs-v3 main `6d20c8d`
29. ✓ MCF M12 writer real-body (PR #154) merged — bc-core main `f1a5992`
30. ✓ MCF M12 writer SAVEPOINT smoke (PR #155) merged — bc-core main `b729a35`
31. ✓ MCF M12 reader smoke (PR #156) merged — bc-core main `9620db7`
32. ⏸ **MCF M14 unblock apply DBCP (THIS DOC)** — pending operator merge
33. ⏸ MCF M14 unblock implementation PR (bc-core) — gated on this DBCP merge + separate operator authorization
34. ⏸ MCF M14 unblock apply gate execution — gated on implementation PR merge + separate operator authorization
35. ⏸ MCF M14 unblock closeout (bc-docs-v3) — records M14 OPEN state
36. ⏸ MCF M12 first real panel run authorization DBCP (bc-docs-v3) — gated on M14 unblock complete + D4
37. ⏸ MCF M12 first real panel run execution + evidence PR (bc-core) — the cliff-crossing event; outcome A→C transition
38. ⏸ MCF M12 first real panel run closeout (bc-docs-v3) — records the first-real-run event + post-run evidence
39. ⏸ Optional: C2 force-rollback-with-data-loss envelope DBCP (bc-docs-v3; per locked D8 C2 + this DBCP D6) — gated on operator decision
40. ⏸ Subsequent M12 runs (per locked D11 per-run operator gate)
41. ⏸ M12.5 materialization + M13 PE-MC evaluator (out of scope per M14/M12 governance D13)
42. ⏸ Post-A5 DROP slice (F4 HYBRID roadmap; out of scope; gated on stable M12 operation)
43. ⏸ Tenant DB rollout (out of scope per M14/M12 governance D12)

## 15. Out-of-scope re-statement

This DBCP does **NOT** apply DDL.

This DBCP does **NOT** apply DML.

This DBCP does **NOT** modify bc-core code.

This DBCP does **NOT** set `BCCORE_M14_OPEN`.

This DBCP does **NOT** execute the M14 unblock apply gate — that is a SEPARATE operator authorization after the M14 unblock implementation PR is merged.

This DBCP does **NOT** invoke M12.

This DBCP does **NOT** authorize the first real M12 panel run — that is a SEPARATE D7 operator gate per §9 + locked D4.

This DBCP does **NOT** authorize the C2 force-rollback-with-data-loss envelope authoring — that remains DEFERRED per locked D6.

This DBCP does **NOT** authorize the M12.5 / M13 / downstream M-series gates — OUT OF SCOPE per M14/M12 governance D13.

This DBCP does **NOT** touch tenant DBs.

This DBCP does **NOT** alter `bcf.*`, `contract.*`, `mcf.*`, `metric.*`, or `concept_registry.*` substrate.

This DBCP does **NOT** initiate any synthetic / mock / replay / canned data writes.

This DBCP does **NOT** execute A5 rollback or any prior phase rollback.

---

**End of DBCP. M14 unblock apply gate design RECORDED. Next operator-authorized gate: MCF M14 unblock implementation PR authoring on bc-core (subordinate per locked D2 of this DBCP).**
