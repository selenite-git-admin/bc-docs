---
uid: DBCP-mcf-m12-first-real-run
title: MCF M12 first real panel-run DBCP
description: Subordinate DBCP designing the D7 first-real-run gate that produces the first real production M12 panel-run commit, crossing the A5 rollback cliff from outcome (A) into outcome (C).
status: proposed
date: 2026-05-29
project: bc-core
domain: implementation
subdomain: mcf
focus: governance
supersedes: null
superseded_by: null
---

# MCF M12 first real panel-run DBCP

Subordinate DBCP per locked D4 of the MCF M14 unblock apply DBCP (bc-docs-v3 main `2c56151` / PR #24).

Designs the operator-authorized **D7 first-real-run gate** that produces the first real production M12 panel-run COMMIT, crossing the A5 rollback envelope cliff from **outcome (A)** into **outcome (C)**.

**Authoring only. NOT EXECUTED.** No bc-core change. No tenant DB. No `writePanelRun` invocation. No first-real-run COMMIT.

---

## 1. Scope

### 1.1 Question

Under locked **D1 = M1 NestJS module registration only** + **D5 = per-run operator authorization** of PR #24, and given:

- M14 unblock implementation **MERGED** at bc-core main `98efc29` (PR #157)
- M14 unblock apply gate **EXECUTED** at apply-ts `2026-05-29T16-03-50-994Z` (PR #158 / bc-core main `e04950d`)
- M12 writer body LIVE and DI-resolvable via `MetricAuthoringModule`
- A5 rollback envelope at outcome (A); cliff predicate guard #700 PASSing

…**what panel-run input, env-gate, pre-run guards, run semantics, post-run evidence, abort rules, subsequent-run policy, and closeout requirements** must govern the first real production invocation of `M12PanelRunWriterService.writePanelRun(...)`?

### 1.2 In-scope

1. First-real-run authorization mechanics (env-gate, operator confirmation, per-run gate)
2. Pre-run guards P1..P11
3. Exact run semantics (panel-run input shape; bcf row creation; mcf write targets)
4. A5 cliff-crossing semantics (outcome A → outcome C)
5. Post-run verification PV1..PV8
6. Abort/failure rules
7. Subsequent-run policy
8. Closeout requirements after first real run
9. Operator decisions D1..D8 with recommendations

### 1.3 Non-scope

1. No bc-core source change in this DBCP (governance/design only).
2. No execution of the first real run.
3. No DDL applied.
4. No DML applied to mcf.* or bcf.* or contract.*.
5. No transaction opened against any DB.
6. No tenant DB connection of any kind. (HR4 negative-only; tenant scope OUT OF SCOPE per M14/M12 D12.)
7. No synthetic / mock / replay / canned data path (HR1).
8. No second/third real run authorized by this DBCP. Each subsequent run requires its own per-run operator authorization gate.
9. No C2 force-rollback / data-loss envelope DBCP (deferred per M14/M12 D8 default; covered separately when/if needed).
10. No M12.5 materialization. No M13 PE-MC evaluator. No M14 publication. Out of scope per PR #23 + PR #24.
11. No re-close of M14. Re-close requires a separate per-event operator authorization per PR #24 §8.
12. No automation of subsequent runs. No queue listeners. No HTTP routes. No schedulers.
13. No bc-portal / bc-admin / bc-ai change.
14. No production cron job.
15. No data backfill of mcf.* from contract.*. The A5 retarget already locked contract.* as FROZEN (A4 deny-write triggers).
16. No deletion of the 19 existing `bcf.panel_output_record` rows (A1 backfill anchor evidence).
17. No deletion or mutation of `mcf-m14-unblock-apply-2026-05-29T16-03-50-994Z.*` apply-gate evidence.

---

## 2. Authority anchor chain

1. **Stance ADR** — DEC-7f9597 / D423 (operator authorization required on every mutating gate)
2. **MCF M14/M12 governance DBCP** — bc-docs-v3 main `6d20c8d` (PR #23); D1..D14 locked
3. **MCF M14 unblock apply DBCP** — bc-docs-v3 main `2c56151` (PR #24); D1..D8 locked; D4 = YES authorize D7 first-real-run DBCP authoring
4. **M14 unblock implementation** — bc-core main `98efc29` (PR #157)
5. **M14 unblock apply evidence** — bc-core main `e04950d` (PR #158); apply-ts `2026-05-29T16-03-50-994Z`
6. **M12 writer real-body** — bc-core main `f1a5992` (PR #154)
7. **M12 writer SAVEPOINT smoke** — bc-core main `b729a35` (PR #155); 19/19 PASS at smoke-ts `2026-05-29T14-57-21-754Z`
8. **M12 reader smoke** — bc-core main `9620db7` (PR #156); 17/17 PASS at smoke-ts `2026-05-29T15-09-14-306Z`
9. **Phase A5 closeout** — bc-docs-v3 main `2792c36` (PR #22)
10. **Phase A5 apply evidence** — bc-core main `99edc1b` (PR #153)
11. **Phase A4 freeze** — contract.* deny-write triggers; bcf.* cert write-once guard

---

## 3. Substrate state pre-D7

Live verified via `bc-postgres` MCP at authoring-time:

| Substrate | Value | Verdict |
|---|---|---|
| mcf→bcf FKs | 5 (RESTRICT/NO ACTION) | ✓ |
| mcf→contract FKs | 0 (DROPPED by A5) | ✓ |
| contract.* deny-write functions LIVE | 4 | ✓ |
| contract.* deny-write trigger defs × events | 4 × 3 = 12 bindings | ✓ |
| `bcf.cert` write-once guard function + trigger | 1 + 1 LIVE | ✓ |
| `bcf.panel_output_record` rows | 19 | ✓ |
| `mcf.metric_authoring_panel_run` panel_run_uid rows | 0 | ✓ |
| `mcf.metric_authoring_panel_transcript` panel_run_uid rows | 0 | ✓ |
| `mcf.certification_record` panel_run_uid rows | 0 | ✓ |
| `mcf.metric_contract_revision` panel_run_uid rows | 0 | ✓ |
| `mcf.metric_publication_eligibility_result` panel_run_uid rows | 0 | ✓ |
| `mcf.metric_supersession` panel_run_uid rows | 0 | ✓ |
| `has_table_privilege(current_user, 'bcf.panel_output_record', 'SELECT')` | true | ✓ |
| M14 governance gate | **OPEN** (Option α writer-activation-only) | ✓ |
| A5 cliff predicate guard #700 (`a5_rollback_no_post_a5_mcf_rows`) | **PASSing** → outcome (A) preserved | ✓ |

### Evidence pre-conditions E1..E8 — status

- **E1** Live FK inventory — MET (A5 apply / PR #153)
- **E2** Live deny-write trigger + function inventory — MET (A4 apply / PR #19)
- **E3** Live row baseline — MET (A5 closeout + apply evidence)
- **E4** M12 writer SAVEPOINT smoke — MET (PR #155; 19/19 PASS)
- **E5** M12 reader smoke — MET (PR #156; 17/17 PASS)
- **E6** Cross-schema SELECT grant on `bcf.panel_output_record` — MET
- **E7** Operator decision on rollback cliff treatment — MET (M14/M12 D8 C1+C2)
- **E8** M14 unblock apply evidence — MET (PR #158; apply-ts `2026-05-29T16-03-50-994Z`; 11/11 G + 7/7 V PASS)

**All E1..E8 pre-conditions hold. D7 first-real-run gate is structurally ready.**

---

## 4. First-real-run apply mechanics

### 4.1 Mechanism

Single direct invocation of `M12PanelRunWriterService.writePanelRun(input)` from an **operator-authorized one-shot Node script** (`scripts/mcf-m12-first-real-run.mjs`). The script:

1. Validates env-gate against the locked PR #24 §9 pattern.
2. Validates HR4 guard (refuses to run if tenant DB env is present).
3. Runs pre-run guards P1..P11 (read-only SELECT + static-grep).
4. Constructs the canonical first-real-run input (see §6).
5. Resolves `M12PanelRunWriterService` via NestJS standalone application context (`NestFactory.createApplicationContext(AppModule)`), reusing the merged `MetricAuthoringModule` registration.
6. Invokes `writePanelRun(input)` exactly **once**.
7. On success, captures the returned `panelRunUid` and runs post-run verifications PV1..PV8.
8. Emits evidence JSONL + summary.

### 4.2 Why NOT add a controller / scheduler / queue listener

Locked D1 = M1 of PR #24 + D9 W1 of PR #23 forbid any runtime entry point wiring. The script invocation pattern is **explicit one-shot operator execution**, not a wired runtime path. This preserves Option α writer-activation-only discipline post-first-real-run.

### 4.3 Env-gate (locked pattern)

```
BCCORE_M12_FIRST_REAL_RUN_CONFIRM=I_HAVE_REVIEWED_M14_UNBLOCK_<m14-unblock-apply-ts>
```

Where `<m14-unblock-apply-ts>` MUST equal `2026-05-29T16-03-50-994Z` (the durable apply-ts merged at bc-core `e04950d` / PR #158).

**Canonical env-gate value for first-real-run:**

```
BCCORE_M12_FIRST_REAL_RUN_CONFIRM=I_HAVE_REVIEWED_M14_UNBLOCK_2026-05-29T16-03-50-994Z
```

The env-gate binds the operator's authorization to the durable M14 unblock apply evidence. A subsequent re-execution attempt with a different apply-ts is rejected.

### 4.4 Per-run authorization model

Per locked D3 (recommendation; this DBCP §11): **per-run operator authorization remains the default** (mirrors PR #24 D5 + PR #23 D11). Each subsequent run requires:

- A fresh env-gate of the same shape, OR
- A future subsequent-run authorization DBCP (not authored here)

No continuous-run authorization. No feature flag.

---

## 5. Pre-run guards P1..P11

The script MUST hard-fail at exit 17+ if any guard fails. No partial runs. No warn-and-proceed.

| # | Guard | Probe |
|---|---|---|
| P1 | M14 OPEN evidence present | `scripts/audit-output/mcf-m14-unblock-apply-2026-05-29T16-03-50-994Z.evidence.jsonl` exists + JSON record `code=1200 pass=true` |
| P2 | M14 unblock apply evidence anchored at expected SHA | `git ls-remote origin main` returns a commit reachable from `e04950d` (or local main == `e04950d` or later) |
| P3 | M12 writer DI-resolvable | NestJS standalone context resolves `M12PanelRunWriterService` instance from `MetricAuthoringModule` |
| P4 | M12 writer SAVEPOINT smoke evidence anchored | `scripts/audit-output/mcf-m12-writer-savepoint-smoke-2026-05-29T14-57-21-754Z.*` files exist |
| P5 | M12 reader smoke evidence anchored | `scripts/audit-output/mcf-m12-reader-smoke-2026-05-29T15-09-14-306Z.*` files exist |
| P6 | mcf.* panel_run_uid rows still 0 | SELECT sum across mapr/mapt/cert/mcr/mper/mcs = 0 |
| P7 | bcf.panel_output_record rows still 19 | SELECT COUNT(*) = 19 |
| P8 | A5 cliff predicate guard #700 still PASSes | Same as P6 expressed as `a5_rollback_no_post_a5_mcf_rows` invariant |
| P9 | A4 freeze invariants intact | 4 contract.* deny-write functions + 4 deny-write trigger definitions + 1 bcf.cert guard function + 1 bcf.cert guard trigger LIVE |
| P10 | HR4 guard: refuses to run if tenant DB env is present (fail-closed at exit 17 if so) | `process.env.TENANT_DATABASE_URL` is unset or empty |
| P11 | Env-gate value matches locked §4.3 pattern AND `<m14-unblock-apply-ts>` equals `2026-05-29T16-03-50-994Z` | Regex match + literal string equality |

---

## 6. Exact run semantics

### 6.1 Panel-run input

**Locked D1 (recommendation; this DBCP §11):** hand-crafted minimal canonical first-real-run input.

The input is constructed inline in the one-shot script (not loaded from disk) so the canonical first-real-run is auditable from source:

```ts
const FIRST_REAL_RUN_INPUT: M12PanelRunInput = {
  panelRunUid: crypto.randomUUID(),          // newly minted UUID
  workbenchFingerprint: <D7-defined>,        // operator-supplied or computed; see §6.3
  reservoir: { /* minimal valid reservoir */ },
  transcripts: [
    { modelRoleCode: 'maker',     /* ... */ },
    { modelRoleCode: 'checker',   /* ... */ },
    { modelRoleCode: 'moderator', /* ... */ },
  ],
};
```

The reservoir / transcript content shape conforms to `M12PanelRunInput` as declared in `src/registry/metric-authoring/m12-panel-run-writer.service.ts` and exercised by the SAVEPOINT smoke (PR #155). No synthetic / mock / replay markers (the writer's HR1 CHECK constraint at `bcf.panel_output_record` would reject any `model_identity_json.maker.provider` ∈ {`synthetic`, `replay`, `mock`, `canned`}).

### 6.2 bcf row creation policy

**Locked D2 (recommendation; this DBCP §11):** the writer **creates a NEW row** in `bcf.panel_output_record` with the freshly minted `panelRunUid`. The existing 19 A1 backfill rows are NOT reused — they are immutable historical authority anchors.

### 6.3 Expected writes

The writer wraps everything in `db.transaction(tx => ...)` (per `m12-panel-run-writer.service.ts:267+`). Inside the transaction:

| Table | Rows inserted | FK chain |
|---|---|---|
| `bcf.panel_output_record` | **1** (the panel-run anchor) | — |
| `mcf.metric_authoring_panel_run` | **1** | `panel_run_uid` → `bcf.panel_output_record.panel_run_uid` (FK `fk_mapr_panel_run`; RESTRICT/NO ACTION) |
| `mcf.metric_authoring_panel_transcript` | **3** (maker / checker / moderator) | `panel_run_uid` → `mcf.metric_authoring_panel_run.panel_run_uid` (FK `fk_mapt_panel_run`) |

**Total row delta on COMMIT: +1 / +1 / +3 = 5 rows across 3 tables.**

### 6.4 Other mcf.* tables — OUT OF SCOPE for first real run

The following 4 tables retain `panel_run_uid` rows = 0 after the first real run (their writes are owned by M12.5 / M13 / M14 publication paths, all of which remain OUT OF SCOPE per PR #23 + PR #24):

- `mcf.certification_record`
- `mcf.metric_contract_revision`
- `mcf.metric_publication_eligibility_result`
- `mcf.metric_supersession`

### 6.5 contract.* — STRUCTURALLY FORBIDDEN

The writer never imports `contract.*` symbols (lockfile-enforced; PR #156 reader smoke #911..#914). Any accidental write attempt would be **structurally rejected by the A4 deny-write triggers** (12 event-bindings across 4 contract.* evidence tables). HR3 + the A4 freeze are the dual structural backstop.

### 6.6 Tenant DB — explicitly excluded

The script never opens, references, or uses any tenant connection. HR4 guard P10 fail-closes if `TENANT_DATABASE_URL` env is present. The first real M12 panel run is a **platform-only** event against `bc_platform_dev` via `DATABASE_URL`.

---

## 7. A5 cliff-crossing semantics

### 7.1 Pre-COMMIT state — outcome (A)

Immediately before `tx.commit()`:

- 5 mcf→bcf FKs LIVE
- 5 mcf→contract FKs DROPPED
- 0 mcf.* panel_run_uid rows (across all 6 retargeted tables incl. transcript)
- A5 cliff predicate guard #700 PASSes
- A5 rollback envelope outcome: **(A) — full rollback to pre-A5 substrate possible**

### 7.2 The cliff-crossing event

`tx.commit()` returns successfully. At that exact moment:

- `bcf.panel_output_record` gains its 20th row (the new `panelRunUid`)
- `mcf.metric_authoring_panel_run` gains its 1st `panel_run_uid` row
- `mcf.metric_authoring_panel_transcript` gains its 1st, 2nd, 3rd `panel_run_uid` rows
- **A5 cliff predicate guard #700 begins FAILING** (`mcf_panel_run_uid_total` no longer 0)
- **A5 rollback envelope outcome flips: (A) → (C)** — A5 retarget rollback would now require either (C1) accept that the 1 mcf.* panel-run row is permanently bound to bcf only, or (C2) force-rollback-with-data-loss (DBCP not authored; deferred per M14/M12 D8 default)

### 7.3 One-way ratchet

The cliff-crossing is a **one-way ratchet**. No script in this DBCP makes outcome (A) reachable again post-COMMIT. The C2 force-rollback envelope DBCP is deferred per locked PR #24 D6.

### 7.4 What outcome (C) means in practice

- Forward path: continue normal M12 operation. Add more panel runs (each via per-run operator authorization). M12.5 / M13 / M14 publication paths can be designed and rolled in when authorized.
- Backward path: requires C2 DBCP authoring + separate operator authorization. Until then, outcome (C) is the standing state.

---

## 8. Post-run verifications PV1..PV8

The script captures PV1..PV8 immediately after `tx.commit()` returns successfully.

| # | Verification | Probe |
|---|---|---|
| PV1 | `bcf.panel_output_record` row delta = +1 | COUNT(*) = 20 (was 19) |
| PV2 | `mcf.metric_authoring_panel_run` row delta = +1 with `panel_run_uid = <new>` | SELECT WHERE panel_run_uid = <new> returns 1 |
| PV3 | `mcf.metric_authoring_panel_transcript` row delta = +3 with `panel_run_uid = <new>` | COUNT(*) WHERE panel_run_uid = <new> = 3; modelRoleCode set = {maker, checker, moderator} |
| PV4 | FK chain integrity | mapr.panel_run_uid → bcf.panel_run_uid resolves; mapt.panel_run_uid → mapr.panel_run_uid resolves for all 3 transcript rows |
| PV5 | No contract.* writes occurred | SELECT timestamps from contract.panel_output_record / contract.calibration_event / contract.authoring_panel_rejection_log / contract.certification_record show no new max(created_at); rows count unchanged from pre-run snapshot |
| PV6 | Other 4 mcf.* tables (cert / mcr / mper / mcs) panel_run_uid rows still 0 | SUM across the 4 = 0 |
| PV7 | M14 governance gate remains OPEN | Apply-ts evidence still durable; no re-close event |
| PV8 | Run identity binding | The `panelRunUid` returned from `writePanelRun` matches the inserted `bcf.panel_output_record.panel_run_uid` AND the inserted `mcf.metric_authoring_panel_run.panel_run_uid` AND all 3 transcript `panel_run_uid` values |

### 8.1 Cliff state probe (PV0 — diagnostic-only)

PV0 is informational, not a pass/fail gate:

- A5 cliff predicate guard #700 now FAILs (expected post-COMMIT)
- A5 rollback envelope outcome: **(C)**
- Standing state: **first real M12 panel run COMPLETED**

---

## 9. Abort / failure rules

### 9.1 Pre-run guard failure (P1..P11)

- Script hard-exits at exit code 17+ before any DB write.
- No `writePanelRun` invocation occurs.
- Substrate delta: zero.
- Outcome (A) preserved.
- No evidence files emitted (or, optionally, a `*.pre-run-fail.summary.md` file is emitted documenting which guard failed; no JSONL).

### 9.2 Transaction failure inside `writePanelRun`

- `db.transaction(...)` rolls back automatically on throw.
- Substrate delta: zero (no rows committed to bcf or mcf).
- Outcome (A) preserved.
- The script catches the throw, emits a `*.run-fail.summary.md` documenting the error class + message, and exits at non-zero code.
- No partial state. No orphan bcf row. No orphan mcf rows.

### 9.3 Post-COMMIT verification failure (PV1..PV8)

- COMMIT already succeeded. Cliff already crossed. Outcome (C) is now the standing state.
- The script emits the standard `*.evidence.jsonl` + `*.summary.md` with the FAILing PVn records.
- An out-of-band incident response is required to determine whether the cliff-crossed state is acceptable or whether C2 force-rollback envelope DBCP authoring must commence.
- Exit code non-zero.

### 9.4 Process kill / crash mid-`writePanelRun`

- If the process dies between `BEGIN` and `COMMIT`, PostgreSQL's automatic transaction abort rolls back the partial state.
- Substrate delta: zero. Outcome (A) preserved.
- If the process dies between `COMMIT` and the evidence file write, the cliff is crossed but evidence is incomplete. Recover by re-running pre/post substrate probes via `bc-postgres` MCP and authoring a `*.post-crash.summary.md` artifact documenting the actual mcf.* / bcf.* deltas.

---

## 10. Subsequent-run policy

**Locked D8 (recommendation; this DBCP §11):** per-run operator authorization remains the default.

Each subsequent run requires:

- A fresh env-gate of the same shape (the `<m14-unblock-apply-ts>` token is constant; PR #24 D5 binds authorization to that durable anchor — operators may re-authorize against the same anchor for each run).
- Pre-run guards P1..P11 re-checked (P6/P7/P8 now have updated baselines — see §10.1).
- Per-run evidence files emitted with the run's own apply-ts.

### 10.1 Baseline drift for runs 2..N

After run 1:

- P6 (mcf.* panel_run_uid rows still 0) → relaxed to "non-decreasing" (rows from prior runs are permanent)
- P7 (bcf.panel_output_record rows still 19) → relaxed to "monotonically increasing"
- P8 (A5 cliff predicate #700 PASSes) → expected to FAIL post-run-1; relaxed to informational

A separate subsequent-run policy DBCP (NOT authored here) may formalize these relaxed baselines.

### 10.2 No automation

No queue listener. No scheduler. No HTTP route. No cron. Each run is operator-initiated.

---

## 11. Operator decisions D1..D8 — recommendations

| # | Decision | Recommendation |
|---|---|---|
| **D1** | Panel-run input source | **Hand-crafted minimal canonical input** (constructed inline in the one-shot script). Rationale: source-auditable; matches PR #155 SAVEPOINT smoke shape; no fixture-file indirection. |
| **D2** | bcf.panel_output_record row policy | **Create NEW row.** Rationale: the 19 existing rows are immutable A1 backfill anchors. The first real M12 panel run mints its own panel_run_uid. |
| **D3** | Per-run authorization model | **Per-run operator authorization** (mirrors PR #24 D5 + PR #23 D11). |
| **D4** | C2 force-rollback / data-loss envelope timing | **Defer until needed** (per M14/M12 D8 default; C1 accept). Outcome (C) is the standing state post-first-real-run. |
| **D5** | Post-run evidence script timing | **Inline within the apply gate script** (single script does pre-run guards + run + post-run evidence). Rationale: evidence freshness; no race window between commit and evidence capture. |
| **D6** | Abort behavior on pre-run guard failure | **Hard fail before any DB write** (P1..P11). No warn-and-proceed. |
| **D7** | Transaction failure handling | **Roll back transaction; preserve outcome (A); no auto-retry.** Re-invocation is a fresh operator-authorized event. |
| **D8** | Subsequent-run policy | **Per-run operator authorization remains the default.** Continuous-run authorization is OUT OF SCOPE here; would require a separate DBCP. |

---

## 12. Hard rule mapping

- **HR1** — no synthetic / mock / replay / canned data. The first-real-run input has no `model_identity_json.maker.provider` in `{synthetic, replay, mock, canned}`; the `bcf.panel_output_record` CHECK constraint enforces this at the storage layer.
- **HR2** — MCF authority data lives in mcf.* anchored to bcf.* via the 5 A5 retargeted FKs.
- **HR3** — the M12 writer service body never imports contract.* (lockfile-enforced; reader smoke #911..#914).
- **HR4** — guard: refuses to run if tenant DB env is present (fail-closed at exit 17). The script is platform-only via `DATABASE_URL` to `bc_platform_dev`. No tenant DB connection of any kind.
- **HR5** — production path; no mocks of business logic. Unit/integration tests for the writer remain merged at PR #154 / #155; this is the first **production** invocation.
- **DEC-7f9597 / D423** — operator authorization required on every mutating gate. The env-gate `BCCORE_M12_FIRST_REAL_RUN_CONFIRM` is the authorization signal.

---

## 13. Risk register R1..R10

| # | Risk | Mitigation |
|---|---|---|
| **R1** | Operator runs the script without env-gate | Script exits at code 18 before any DB connection |
| **R2** | Stale env-gate value (wrong apply-ts) | P11 literal-equality check on `<m14-unblock-apply-ts>` rejects mismatched values |
| **R3** | Tenant DB env leaks into the process | HR4 guard P10 fail-closes at exit 17 before any DB connection |
| **R4** | Pre-run guard drift between authoring-time and run-time | P1..P11 re-checked at run-time against live substrate |
| **R5** | Cliff crossed accidentally during testing | Test/CI environment does NOT have the operator's env-gate value; script exits at code 18 in any non-production context |
| **R6** | Transaction failure mid-write produces orphan rows | `db.transaction(...)` PostgreSQL atomicity guarantees zero partial state |
| **R7** | Post-COMMIT verification fails | Evidence files still emitted; out-of-band incident response triggered; C2 DBCP authoring may be required |
| **R8** | Process crash between COMMIT and evidence file write | Recover via `bc-postgres` MCP probes + author `*.post-crash.summary.md` documenting actual deltas |
| **R9** | Subsequent run authorized incorrectly | D8 per-run gate model; each run is a separate operator-authorized event |
| **R10** | M14 re-close attempted before first real run | M14 re-close is a separate per-event operator authorization per PR #24 §8; preserves outcome (A) if no first-real-run COMMIT has occurred yet |

---

## 14. Standing gate state — target

| State element | Pre-D7 execution | Post-D7 execution (first-real-run COMMITted) | Subsequent-run policy |
|---|---|---|---|
| M14 governance gate | OPEN | OPEN (unchanged) | OPEN |
| M12 writer body | LIVE; DI-resolvable | LIVE; DI-resolvable | LIVE; DI-resolvable |
| `bcf.panel_output_record` rows | 19 | 20 | 20 + N |
| `mcf.metric_authoring_panel_run` panel_run_uid rows | 0 | 1 | 1 + N |
| `mcf.metric_authoring_panel_transcript` panel_run_uid rows | 0 | 3 | 3 + 3N |
| `mcf.{cert, mcr, mper, mcs}` panel_run_uid rows | 0 | 0 (M12.5+ out of scope) | 0 (until M12.5+) |
| A5 cliff predicate guard #700 | PASSing | FAILing (expected) | FAILing |
| A5 rollback envelope outcome | (A) | (C) — one-way ratchet | (C) |
| C2 force-rollback envelope DBCP | NOT AUTHORED | NOT AUTHORED (deferred per D4) | NOT AUTHORED |
| First-real-run authorization | NOT YET AUTHORIZED | EXECUTED | per-run |
| Tenant scope | OUT OF SCOPE | OUT OF SCOPE | OUT OF SCOPE |

---

## 15. Sequencing 1..N

Items 1–32 complete (M14/M12 governance DBCP + M14 unblock apply DBCP + M14 unblock implementation + M14 unblock apply gate execution lineage). Items 33–43 pending in this D7 lineage:

33. Operator review of this DBCP and locking of D1..D8.
34. Author bc-core `scripts/mcf-m12-first-real-run.mjs` per §4 + §5 + §8.
35. Lockfile extension with first-real-run script existence + shape assertions.
36. Unit/static tests for the one-shot script (env-gate parsing; pre-run guard structure; input shape conformance to `M12PanelRunInput`).
37. Open bc-core PR for the first-real-run script (DO NOT merge; DO NOT execute).
38. Operator review + authorization of the bc-core PR.
39. Operator-authorized squash merge of the bc-core PR.
40. Separate operator authorization to execute the first real run.
41. Execution of the first real run with the locked env-gate value.
42. Evidence PR opened against bc-docs-v3 / bc-core for the first-real-run artifacts.
43. Operator-authorized merge of the evidence PR + closeout.

Items 34–43 are **not in scope** for this DBCP. This file is governance/design only.

---

## 16. Closeout requirements after first real run

After the first-real-run COMMIT succeeds and evidence is captured + merged:

1. **Standing-state ledger update**: a one-line entry to be added to the next governance touchpoint (or to `metric-context-framework-m12-first-real-run-closeout.md` if authored) recording: apply-ts, panelRunUid, mergeCommit, bcf delta, mcf deltas, cliff state.
2. **C2 envelope status**: confirm the C2 force-rollback envelope DBCP remains deferred (per locked D4) — unless an incident response triggers earlier authoring.
3. **Subsequent-run posture**: confirm D8 per-run authorization is the operating mode. No automation.
4. **Lockfile**: the M14_UNBLOCK_ASSERTIONS block in `scripts/bcf-phase-a3-import-lockfile.mjs` remains stable. The first-real-run script existence may be added as a new assertion block in a subsequent PR.
5. **M12.5 / M13 / M14 readiness gate**: this is a separate downstream authorization track. No automatic activation post-first-real-run.

---

## 17. Out-of-scope re-statement

This DBCP **does not**:

- Modify bc-core source.
- Author the one-shot first-real-run script.
- Execute the first real run.
- Apply DDL or DML.
- Open a transaction against any DB.
- Touch tenant DBs in any way.
- Author the C2 force-rollback envelope DBCP.
- Author the subsequent-run policy DBCP.
- Author the M12.5 / M13 / M14 readiness gates.
- Re-close M14.
- Mutate the M14 unblock apply evidence (PR #158).

It only **designs** the D7 first-real-run gate so that the next operator-authorized step (item 34 in §15) has a complete blueprint.
