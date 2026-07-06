---
uid: DBCP-mcf-m12-first-real-run-authorization
title: MCF M12 first-real-run authorization DBCP
description: Governance DBCP authorizing the single first real M12 panel run bound to intake_queue_uid 4d849778-3989-4caf-8a71-7d44b782d98e, bc-core anchor 0e5e501d6735f79670c0c0f769b4ac19c0ef50b9, and the operator-attested one-time env-gate BCCORE_M12_FIRST_REAL_RUN_CONFIRM. Discharges PR #28 §9 / D8 condition 7. Decision-only; no code execution; no DB mutation in this gate itself.
status: proposed
date: 2026-05-30
project: bc-core
domain: implementation
subdomain: mcf
focus: governance
supersedes: null
superseded_by: null
---

# MCF M12 first-real-run authorization DBCP

Discharges **PR #28 §9 / D8 condition 7** — the final remaining prerequisite for the first real M12 panel run.

Binds the run to:
- **Intake uid:** `4d849778-3989-4caf-8a71-7d44b782d98e` (PR #167 / `0e5e501d`-substrate-resident)
- **bc-core anchor:** `0e5e501d6735f79670c0c0f769b4ac19c0ef50b9` (post-PR-#167 main)
- **bc-docs-v3 anchor:** `55bc4759c5d182fe1afcfc1afb525b81af85d9e3` (pre-this-DBCP main)
- **One-time env-gate:** `BCCORE_M12_FIRST_REAL_RUN_CONFIRM` with literal value pinning intake uid + bc-core SHA
- **Operator attestation:** recorded below + in the subordinate execution PR commit body

**Decision-only.** No code execution. No DB mutation in this DBCP itself. The subordinate execution PR (the actual `runPanel()` invocation) is a separate operator-authorized event after this DBCP merges.

---

## 1. Scope / non-scope

### 1.1 In scope

- Authorizing the single first real M12 panel run bound to the binding tuple in §4.
- Defining the one-time env-gate value (§5) the execution script must match literally.
- Specifying the success criterion (any terminal panel verdict via the real trust path; §8).
- Defining outcome semantics for each terminal verdict (§8).
- Recording the operator authorization clause (§6).
- Forward-looking scope of the subordinate bc-core execution PR (§7) — NOT authoring it.

### 1.2 Non-scope (explicit)

1. No invocation of `MetricAuthoringPanelService.runPanel()` — that is the subordinate execution PR's job.
2. No invocation of `M12PanelRunWriterService.writePanelRun()` (standalone) or `.writePanelRunInTx()`.
3. No `M12.5` materialization / `M13` PE-MC / `M14` publication invocation.
4. No metric contract authored.
5. No new intake row created.
6. No mutation to the existing intake row `4d849778-3989-4caf-8a71-7d44b782d98e`.
7. No rollback executed.
8. No tenant DB touch.
9. No DDL.
10. **No DML in this DBCP itself.** All substrate mutations belong to the subordinate execution PR.
11. No bc-core source code change.
12. No re-litigation of PR #28 / PR #161-167 governance.
13. No authoring of the M12.5 / M13 / M14 next-gate DBCPs (those follow if/when `APPROVE_FOR_DRAFT` is achieved).

---

## 2. Authority anchor chain

| Anchor | Role | Reference |
|---|---|---|
| Stance ADR | Operator authorization gate | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) |
| M12 deferred prerequisites DBCP | Defines §4.1-§4.3 + D1-D8 + §11 enforcement | bc-docs-v3 main `55bc4759c5d182fe1afcfc1afb525b81af85d9e3` (PR #28) |
| M12 orchestrator O1 Adapter implementation | Trust-path code wiring | bc-core main `a0fee4e` (PR #161) |
| M12 orchestrator Adapter SAVEPOINT evidence | Live-rollback proof | bc-core main `9f74d9c` (PR #162); evidence-ts `2026-05-30T03-26-30Z` |
| MCF M12 allowlist seed evidence | D8 condition 4 (10 tools + 6 evidence sources) | bc-core main `d3609a85` (PR #163) |
| MCF M12 vendor adapter code wiring | D8 cond 5 code-shape half | bc-core main `4298e0a8` (PR #164) |
| MCF M12 vendor adapter real-API evidence | D8 cond 5 evidence-run half (3 real provider calls + 9-key provenance) | bc-core main `f9cd043e` (PR #165); evidence-ts `2026-05-30T05-44-19-897Z` |
| MCF M12 adapter defaults fix | D8 cond 5 production-readiness (M2 latency + M3 Google default) | bc-core main `a48d429a` (PR #166) |
| MCF M11 first real intake row | D8 cond 6 (single `operator_direct` row, `pending`) | bc-core main `0e5e501d` (PR #167); intake uid `4d849778-3989-4caf-8a71-7d44b782d98e` |
| bc-docs-v3 anchor (this DBCP base) | PR open anchor | `55bc4759` |
| bc-core anchor | Substrate + adapter state at authoring time | main `0e5e501d6735f79670c0c0f769b4ac19c0ef50b9` |

---

## 3. D8 conditions 1-6 — live verification at authoring time

| §9 condition | Required artefact | Status @ DBCP authoring |
|---|---|---|
| 1. This DBCP's parent (PR #28) merged at bc-docs-v3 | `55bc4759` containing PR #28 §9 / D8 / §11 | ✅ DONE |
| 2. PR #161 (orchestrator O1 Adapter impl) merged at bc-core | `a0fee4e` | ✅ DONE |
| 3. PR #162 (orchestrator Adapter SAVEPOINT evidence) merged at bc-core | `9f74d9c` | ✅ DONE |
| 4. Allowlist seed evidence merged at bc-core (≥10 tools + ≥6 evidence sources) | `d3609a85` (PR #163); substrate `workspace_tool_allowlist=10` + `evidence_source_allowlist=6` | ✅ DONE |
| 5. Vendor adapter verification evidence merged at bc-core (real API + 9-key provenance) | `4298e0a8` (PR #164 code) + `f9cd043e` (PR #165 evidence; 3/3 status=ok with full provenance) + `a48d429a` (PR #166 M2+M3 production fixes) | ✅ DONE |
| 6. First real M11 intake row evidence merged at bc-core | `0e5e501d` (PR #167); substrate `metric_authoring_intake_queue=1` with uid `4d849778-3989-4caf-8a71-7d44b782d98e`, `status_code='pending'`, `reservoir_name='operator_direct'`, `normalized_candidate_json jsonb_typeof='object'` | ✅ DONE |
| **7. Operator explicit per-run authorization** | This DBCP + the operator attestation clause in §6 | 🟢 **PROPOSED — this DBCP** |

After this DBCP merges, condition 7 transitions to ✅ DONE and the first-real-M12 unlock gate is OPEN for the subordinate execution PR.

---

## 4. The single run this DBCP authorizes — binding tuple

This DBCP authorizes **exactly one** invocation of `MetricAuthoringPanelService.runPanel(intakeUid, opts, deps)` against the specific binding tuple below.

| Field | Value |
|---|---|
| `intake_queue_uid` | `4d849778-3989-4caf-8a71-7d44b782d98e` |
| `bc_core_anchor_sha` | `0e5e501d6735f79670c0c0f769b4ac19c0ef50b9` (current bc-core main) |
| `bc_docs_v3_anchor_sha` | `<this DBCP's merge SHA — populated by the subordinate execution PR>` |
| `expected_substrate_state_pre_run` | `intake_queue=1, mapr=1, mapt=3, bcf.panel_output_record=20, contract.panel_output_record=19, workspace_tool_allowlist=10, evidence_source_allowlist=6, metric_contract=0, metric_contract_version=0` |
| `expected_workspace_fingerprint_inputs` | Derived from `(workspace_tool_allowlist where effective_to IS NULL, evidence_source_allowlist where effective_to IS NULL)` at run-time. The execution script captures the actual fingerprint into the evidence. |
| `expected_intake_row_status_at_run_start` | `pending` |
| `expected_intake_row_status_at_run_end` | `consumed_by_panel` (orchestrator HA-6 transition; applies regardless of terminal verdict) |
| `expected_mapr_delta` | `+1` (whichever the verdict, the orchestrator persists the mapr row via the O1 Adapter / writer chain) |
| `expected_mapt_delta` | `+3` (one transcript per role: maker / checker / moderator) |
| `expected_bcf_panel_output_record_delta` | `+1` (BCF anchor row written by `writePanelRunInTx`) |
| `expected_contract_panel_output_record_delta` | `0` (A4 freeze) |
| `expected_metric_contract_delta` | `0` (M12.5 not invoked here regardless of verdict) |

**Run uniqueness contract.** The orchestrator's "in-flight guard" (HA-6) ensures at most one panel run per `intake_queue_uid` at a time. The intake row transitions from `pending` → `consumed_by_panel` at the start of the run, preventing concurrent or duplicate attempts. If this authorized run aborts mid-execution (timeout, transaction rollback, process kill), the operator records the abort in the execution evidence and a fresh DBCP authorization is required for any retry — this authorization is NOT a standing license.

---

## 5. Env-gate definition — `BCCORE_M12_FIRST_REAL_RUN_CONFIRM`

### 5.1 Required literal value

The subordinate execution script MUST verify that `process.env.BCCORE_M12_FIRST_REAL_RUN_CONFIRM` matches the following literal **byte-for-byte**, failing closed otherwise:

```
BCCORE_M12_FIRST_REAL_RUN_CONFIRM=I_HAVE_REVIEWED_AND_AUTHORIZE_FIRST_REAL_M12_FOR_INTAKE_4d849778-3989-4caf-8a71-7d44b782d98e_ON_BC_CORE_0e5e501d6735f79670c0c0f769b4ac19c0ef50b9
```

### 5.2 Why this shape

- **Binds to the full intake uid** (no shortening) — prevents accidental authorization of a different intake row by typo or future intake addition
- **Binds to the full bc-core SHA** (no shortening) — pins the adapter family + orchestrator code state that was reviewed at authorization time
- **Operator-attestation prefix** (`I_HAVE_REVIEWED_AND_AUTHORIZE`) — forces the operator to type a phrase that semantically affirms review, not just a hash
- **Single literal** — no fuzzy matching; the comparison is strict equality

### 5.3 Shell portability

| Shell | Invocation example |
|---|---|
| Bash / Zsh | `BCCORE_M12_FIRST_REAL_RUN_CONFIRM=I_HAVE_REVIEWED_AND_AUTHORIZE_FIRST_REAL_M12_FOR_INTAKE_4d849778-3989-4caf-8a71-7d44b782d98e_ON_BC_CORE_0e5e501d6735f79670c0c0f769b4ac19c0ef50b9 TENANT_DATABASE_URL="" node scripts/mcf-m12-first-real-run.mjs` |
| PowerShell | `$env:BCCORE_M12_FIRST_REAL_RUN_CONFIRM = 'I_HAVE_REVIEWED_AND_AUTHORIZE_FIRST_REAL_M12_FOR_INTAKE_4d849778-3989-4caf-8a71-7d44b782d98e_ON_BC_CORE_0e5e501d6735f79670c0c0f769b4ac19c0ef50b9'; $env:TENANT_DATABASE_URL = ''; node scripts/mcf-m12-first-real-run.mjs` |

Hyphens inside the value are valid in both shells. No quoting is required for Bash (no spaces / special chars). PowerShell single-quoted string preserves the value literally.

### 5.4 Mismatch behavior

The execution script MUST `process.exit(>0)` immediately if `BCCORE_M12_FIRST_REAL_RUN_CONFIRM` is missing OR does not match the literal. Mismatch is treated as the operator NOT having authorized this specific run — no panel invocation, no DB connection, no provider API call.

---

## 6. Operator authorization clause

The operator records the following attestation when this DBCP is merged. It is also reproduced verbatim in the subordinate execution PR's commit body and in the execution evidence summary.

> **Operator authorization for first real M12 panel run.**
>
> I, the operator authoring this DBCP, attest that:
>
> 1. I have reviewed each of the merged prerequisite evidence PRs at the SHAs cited in §2: PR #28 (`55bc4759`), PR #161 (`a0fee4e`), PR #162 (`9f74d9c`), PR #163 (`d3609a85`), PR #164 (`4298e0a8`), PR #165 (`f9cd043e`), PR #166 (`a48d429a`), and PR #167 (`0e5e501d`).
> 2. I have inspected the substrate state described in §3 + §4 and confirm it matches the live values at authoring time.
> 3. I authorize a single invocation of `MetricAuthoringPanelService.runPanel(intakeUid='4d849778-3989-4caf-8a71-7d44b782d98e')` against bc-core main SHA `0e5e501d6735f79670c0c0f769b4ac19c0ef50b9` and the substrate state described above.
> 4. I accept the trust premise reaffirmed by PR #28 §11: the panel run must call real provider APIs via the approved `PanelAgentAdapter.run(...)` interface; no substitute, fixture, replay, or hand-authored content path is permitted; the run will emit per-role provenance per §11.4.
> 5. I accept that any terminal verdict (`APPROVE_FOR_DRAFT`, `OPERATOR_REVIEW`, `REJECT_DEFECT`) — produced via the real trust path with real adapter provenance — satisfies D8 condition 7 for THIS authorized run. Non-terminal failure modes (`VendorConfigurationError`, `vendor_timeout`, `vendor_failure`, `cost_ceiling_exceeded`) do NOT satisfy condition 7 and would require a fresh DBCP authorization for any retry.
> 6. I accept that this authorization is single-use; it is consumed by the subordinate execution PR's run regardless of verdict.

---

## 7. Subordinate execution PR scope (forward-looking; not authored by this DBCP)

After this DBCP merges, the operator separately authorizes a bc-core PR that performs the actual `runPanel()` invocation. This DBCP describes that PR's scope for transparency but does NOT author it.

### 7.1 What the execution PR will do

- New script `scripts/mcf-m12-first-real-run.mjs` (or successor name)
- Reads `BCCORE_M12_FIRST_REAL_RUN_CONFIRM` and matches against the §5.1 literal (fails closed on mismatch)
- Reads `TENANT_DATABASE_URL=""` shell prefix and tripsHR4 guard if non-empty
- Loads compiled `dist/registry/.../metric-authoring-panel.service.js` via `createRequire` + NestFactory bootstrap (mirroring PR #160 wiring shape, post-PR #161 O1 Adapter path)
- Constructs `PanelAgentFactoryImpl` from env (Anthropic + OpenAI + Google API keys from `.env`; OpenAI key sourced from `bc-ai/.env` at shell-eval time per the PR #165 pattern if still absent from `bc-core/.env`)
- Invokes `MetricAuthoringPanelService.runPanel('4d849778-3989-4caf-8a71-7d44b782d98e', opts, deps)` once
- Captures the resulting `mapr` row + 3 `mapt` rows + 1 `bcf.panel_output_record` row from the substrate post-run
- Emits evidence JSONL + summary.md under `scripts/audit-output/mcf-m12-first-real-run-<ts>.{evidence.jsonl,summary.md}`
- HARD requirement: 3 distinct vendor `vendor_request_id` values in mapt; `verdict_code` in `{APPROVE_FOR_DRAFT, OPERATOR_REVIEW, REJECT_DEFECT}`; `intake_queue.status_code` transitioned `pending` → `consumed_by_panel`
- Exit codes: 0=success / 1=HR4 trip / 2=env-gate mismatch / 3=runPanel threw / 4=verdict in non-terminal state / 5=substrate post-state mismatch / 6=unexpected error

### 7.2 What the execution PR will NOT do

- NOT invoke `M12.5` materialization (even if verdict=`APPROVE_FOR_DRAFT`)
- NOT invoke `M13` / `M14`
- NOT author a metric contract
- NOT mutate `bcf.panel_output_record` rows beyond the single new one
- NOT touch tenant DB
- NOT execute rollback (panel-side transaction rollback is the orchestrator's normal behavior on internal failure; that's not the same as the C-rollback envelope)

---

## 8. Outcome semantics

### 8.1 First-real-M12 success criterion

The success criterion for D8 condition 7 (this DBCP's purpose) is:

> **The panel ran through the real trust path with real adapter provenance, producing a terminal verdict.**

This is the same definition the operator accepted in §6 item 5. All three terminal verdicts satisfy the criterion. Non-terminal failure modes (timeouts, vendor errors, env-gate mismatch, HR4 trip) do not.

### 8.2 Per-verdict semantics

| Verdict | Authorization criterion | Downstream gate impact | Intake row status post-run |
|---|---|---|---|
| `APPROVE_FOR_DRAFT` | ✅ Satisfied | **M12.5 becomes invocable** on the resulting mapr row. M12.5 invocation is a SEPARATE next-gate DBCP (this DBCP does not authorize M12.5). | `consumed_by_panel` |
| `OPERATOR_REVIEW` | ✅ Satisfied | M12.5 stays gated (M12.5 read predicate `consensus_payload_json->>'verdict_code' = 'APPROVE_FOR_DRAFT'` returns 0). Operator reviews the mapr + transcripts to decide whether to author a new intake row with refined candidate content, OR accept the OPERATOR_REVIEW as the terminal outcome for this intake. | `consumed_by_panel` |
| `REJECT_DEFECT` | ✅ Satisfied | M12.5 stays gated. The mapr's `defect_code` records why; operator authors a new intake row (new `reservoir_entry_id`, new operator-direct or refined candidate) if a retry is desired. | `consumed_by_panel` |

### 8.3 Re-attempt path (per A5 / operator-locked decision)

The intake row uniqueness constraint is `(reservoir_name, reservoir_entry_id)`. Any future re-attempt MUST use a NEW `reservoir_entry_id` (the timestamp-anchored format used in PR #167 is convenient). The original intake row `4d849778-...` stays at `consumed_by_panel` permanently — it represents the historical first-real-M12 run regardless of verdict.

A re-attempt requires:
- A new operator-direct intake row evidence PR (mirroring PR #167 shape)
- A new first-real-M12 authorization DBCP binding to the new intake uid + current bc-core SHA (this DBCP cannot be reused — it is single-use per §6 item 6)

### 8.4 What happens if M12.5 next-gate is desired (verdict=APPROVE_FOR_DRAFT only)

The subordinate execution PR captures the mapr_uid + verdict in evidence. If the verdict is `APPROVE_FOR_DRAFT`, the operator may then author the **M12.5 materialization authorization DBCP** binding to that specific mapr_uid + the same bc-core SHA + a similar one-time env-gate. That M12.5 DBCP is NOT authored here.

---

## 9. Hard rule mapping

- **HR1** — no synthetic / mock / replay / canned data. The panel run uses real adapter calls (Anthropic + OpenAI + Google) via `PanelAgentAdapter.run(...)` per PR #28 §11.1; provenance keys per §11.4. This DBCP does NOT mutate substrate; HR1 applies to the subordinate execution PR.
- **HR2** — when the execution PR runs, the writer targets `mcf.*` via `bcf.*` anchor (post-A5 topology); orchestrator owns outer tx (PR #161). Unchanged by this DBCP.
- **HR3** — M12 writer body never imports `contract.*` (unchanged; lockfile-enforced).
- **HR4** — tenant DB OUT OF SCOPE. This DBCP touches no DB. The subordinate execution PR uses `TENANT_DATABASE_URL=""` shell prefix; orchestrator + writer connect only to `bc_platform_dev`.
- **HR5** — production path; this DBCP is the explicit operator authorization step required by PR #28 §9 / D8 / §11.6.
- **DEC-7f9597 / D423** — operator authorization required per gate. This DBCP IS the gate; merging it constitutes the authorization. The subordinate execution PR is a separate gate that the operator authorizes after this DBCP merges.

---

## 10. Risk register

| # | Risk | Mitigation |
|---|---|---|
| **R1** | Vendor outage during the panel run (one of Anthropic / OpenAI / Google rate-limits or returns 5xx) | Adapter `.run()` returns `status='error'`; orchestrator's consensus payload records the failure; panel completes with a non-terminal status. Per A4, this does NOT satisfy condition 7; a fresh DBCP authorization is required for retry. |
| **R2** | Vendor cost overrun during the panel run | Per PR #28 D2 + PR #166: conservative model tier + `DEFAULT_MAX_OUTPUT_TOKENS=1024`. Operator-authorized cost ceiling for the single run is roughly `~$0.001-0.01` for cost-bounded prompts; bound the script with `DEFAULT_VENDOR_TIMEOUT_MS=60_000` per vendor. |
| **R3** | Intake row already at `consumed_by_panel` before run start (race / prior partial attempt) | Orchestrator HA-6 in-flight guard catches this and refuses to start. The execution script's pre-run substrate check verifies `intake_queue.status_code='pending'` and exits cleanly if mismatch. |
| **R4** | Workspace fingerprint mismatch between authoring-time and run-time | If allowlist content changes between this DBCP authoring and the execution PR run, the fingerprint differs. Execution script captures the actual fingerprint in evidence; substrate audit can compare against the DBCP's expected inputs. Operator may either accept the new fingerprint (re-authorize via amended DBCP) or revert the allowlist change. |
| **R5** | Process termination mid-run (kill, network drop, host crash) | The orchestrator's outer transaction rolls back on uncommitted state. The intake row may be left at `consumed_by_panel` (the status transition is the first write inside the transaction per HA-6, so even on rollback the status revert depends on transaction boundary). Operator inspects substrate manually; if intake is stuck at `consumed_by_panel` with no mapr row, an operator-authorized DML reset to `pending` is needed before retry (separate DBCP). |
| **R6** | Verdict is `APPROVE_FOR_DRAFT` but the M12.5 read predicate cannot consume because the consensus_payload was malformed | M12.5 read at `metric-authoring-materialization.service.ts:364` performs explicit `verdict_code !== 'APPROVE_FOR_DRAFT'` rejection. If the verdict is APPROVE_FOR_DRAFT, M12.5 becomes invocable but is gated by a SEPARATE next-gate DBCP — operator decides whether to invoke. |
| **R7** | OpenAI API key still missing from bc-core/.env at execution time | Execution script source-loads OPENAI_API_KEY from `bc-ai/.env` at shell-eval (the PR #165 / PR #167 pattern) OR the operator copies the key. Either way the env-gate value validates against §5.1 first; if the key is missing, factory.makeChecker() throws VendorConfigurationError before any provider call, exiting cleanly per §7.1 exit code 3. |
| **R8** | Multiple operators attempt to invoke the execution script concurrently | Only one operator holds the env-gate literal at a time (it must be set in the invoking shell). Substrate's HA-6 in-flight guard catches concurrent attempts via the intake row status. |

---

## 11. Standing gate state

| State element | Pre-DBCP-merge (today) | Post-DBCP-merge | Post-subordinate-execution (verdict-independent) |
|---|---|---|---|
| Condition 7 of §9 / D8 | ⏳ PENDING | ✅ DONE | DONE (preserved) |
| First-real-M12-run gate | CLOSED | OPEN — subordinate execution PR may be authorized | OPEN (preserved); next-gate (M12.5) may follow if verdict was `APPROVE_FOR_DRAFT` |
| `BCCORE_M12_FIRST_REAL_RUN_CONFIRM` env-gate | not defined | defined per §5.1 | consumed (single-use) |
| `mcf.metric_authoring_intake_queue` | 1 (pending) | 1 (pending; unchanged) | 1 (consumed_by_panel) |
| `mcf.metric_authoring_panel_run` (mapr) | 1 (PR #160 placeholder) | 1 (unchanged) | **2** (+1 from this authorized run) |
| `mcf.metric_authoring_panel_transcript` (mapt) | 3 | 3 (unchanged) | **6** (+3 from this authorized run; maker/checker/moderator) |
| `bcf.panel_output_record` | 20 | 20 (unchanged) | **21** (+1 from this authorized run) |
| `contract.panel_output_record` (frozen by A4) | 19 | 19 (unchanged) | 19 (unchanged — A4 freeze) |
| `mcf.metric_contract` | 0 | 0 | 0 (M12.5 not invoked here; even on `APPROVE_FOR_DRAFT` verdict) |
| `mcf.metric_contract_version` | 0 | 0 | 0 (same) |
| M14 governance gate | OPEN | OPEN | OPEN (unaffected) |
| A5 rollback envelope outcome | (C) durable | (C) durable | (C) durable |
| C2 force-rollback envelope DBCP | NOT AUTHORED | NOT AUTHORED | NOT AUTHORED |
| bc-docs-v3 main | `55bc4759` | `<this DBCP's merge SHA>` | `<this DBCP's merge SHA>` |
| bc-core main | `0e5e501d` | `0e5e501d` (unchanged) | `<execution PR's merge SHA>` |

---

## 12. Out-of-scope re-statement

This DBCP does NOT:

- Apply DDL or DML against any DB.
- Invoke `MetricAuthoringPanelService.runPanel()` — that is the subordinate execution PR.
- Invoke `M12PanelRunWriterService.writePanelRun()` (standalone) or `.writePanelRunInTx()`.
- Invoke `M12.5` / `M13` / `M14` services.
- Author the M12.5 materialization authorization DBCP — that follows IF the panel verdict is `APPROVE_FOR_DRAFT` AND the operator chooses to materialize.
- Author the M13 PE-MC or M14 publication authorization DBCPs.
- Author the C2 force-rollback envelope DBCP.
- Author the subordinate bc-core execution PR.
- Touch any tenant DB.
- Mutate the existing intake row `4d849778-3989-4caf-8a71-7d44b782d98e`.
- Mutate PR #160's placeholder mapr row.
- Re-touch any merged A1-A5 / M14-unblock / first-real-run / O1-Adapter / SAVEPOINT-evidence / allowlist-seed / vendor-adapter / M11-intake PR.
- Change bc-core source code.
- Modify the env-gate literal value once this DBCP merges (the literal is fixed by §5.1; any change requires a successor DBCP).

It only **authorizes** the single specific panel run defined in §4 against the env-gate in §5, with the success criterion in §8 and the operator attestation in §6. The substrate mutation belongs to the subordinate execution PR.
