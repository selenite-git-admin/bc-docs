---
uid: metric-context-framework-m12-first-real-run-disposition
title: MCF M12 — First-Real-Run Disposition (intake 4d849778, panel_run 9a462e6c, verdict OPERATOR_REVIEW)
description: Governance disposition record for the first real M12 panel run. Records the operator's acceptance of the OPERATOR_REVIEW verdict as terminal for intake `4d849778-3989-4caf-8a71-7d44b782d98e` (panel_run_uid `9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`). Confirms first-real-M12 execution is complete and PR #28 §9 / D8 condition 7 is discharged. Confirms the OPERATOR_REVIEW verdict satisfies first-real-M12 execution evidence per PR #29 §8.1 (A4 success criterion) but does NOT unlock M12.5 — M12.5's `APPROVE_FOR_DRAFT` precondition is unmet; `mcf.metric_contract` / `mcf.metric_contract_version` deltas remain 0. Confirms the intake row stays at `pending` per the code-true verdict-aware mapping (per MCF-ERR-001), and the operator's single-use authorization (PR #29 §6 item 6) is consumed governance-side notwithstanding the substrate's `pending` status. States the rule for any future M12 attempt against this candidate or any other: NEW `reservoir_entry_id` + NEW intake row evidence PR + FRESH authorization DBCP. Records the operator's decision to defer any refined-candidate retry pending the panel-framework calibration investigation scoped in `metric-context-framework-m12-panel-framework-calibration-followup.md`. **NOT EXECUTED** — docs-only governance disposition. No DDL, no DML, no provider calls, no `runPanel()` invocation, no writer standalone invocation, no M12.5 / M13 / M14 invocation, no metric contract created, no rollback, no tenant DB touch, no substrate mutation.
status: implemented
date: 2026-05-30
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m12-first-real-run-disposition
supersedes:
superseded_by:
---

# MCF M12 — First-Real-Run Disposition

## 1. Scope

### 1.1 Question this doc answers

> The first real M12 panel run (`panel_run_uid 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`) was executed against intake `4d849778-3989-4caf-8a71-7d44b782d98e` under PR #29 authorization and produced consensus verdict `OPERATOR_REVIEW`. PR #29 §8.2 (now governed by MCF-ERR-001) gives the operator two disposition paths: refine and retry with a new intake, OR accept the OPERATOR_REVIEW as terminal for this intake. Which did the operator choose, what is the resulting standing state, and what governance rule applies to any future M12 attempt?

### 1.2 In scope

- The operator's disposition decision for intake `4d849778-...` and `panel_run 9a462e6c-...`
- The standing state of M12 / M12.5 / M13 / M14 after this disposition
- The intake-row status interpretation under the code-true verdict-aware mapping (per MCF-ERR-001)
- The single-use-authorization accounting for PR #29
- The rule for any future first-real-M12-style attempt
- The pointer to the panel-framework calibration follow-up investigation that gates any refined-candidate retry

### 1.3 Explicit non-scope

- ❌ No re-execution of M12 by this disposition
- ❌ No `MetricAuthoringPanelService.runPanel()` invocation
- ❌ No `M12PanelRunWriterService` standalone invocation
- ❌ No provider (Anthropic / OpenAI / Google) API calls
- ❌ No M12.5 / M13 / M14 invocation
- ❌ No metric contract creation
- ❌ No rollback
- ❌ No tenant DB touch
- ❌ No DDL, no DML, no substrate mutation
- ❌ No bc-core code change
- ❌ No amendment to PR #29 DBCP (the PR #29 DBCP correction is the responsibility of a separate follow-up bc-docs PR per MCF-ERR-001 `target_resolution`)
- ❌ No new authorization DBCP for any future M12 attempt
- ❌ No commitment to a refined-candidate retry — refined-candidate retry is explicitly deferred behind the panel-framework calibration investigation
- ❌ No commitment to a panel-framework code change in bc-core — the calibration follow-up is investigation scope only

## 2. Authority anchors

| Anchor | Reference |
|---|---|
| PR #29 first-real-M12 authorization DBCP | bc-docs main `a18d6e3c` (`docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md`) |
| PR #30 errata MCF-ERR-001 | bc-docs main `3926d021` (`docs/errata/MCF-ERR-001.md`) |
| PR #28 deferred prerequisites DBCP | bc-docs main `55bc4759` |
| PR #167 first real M11 intake row evidence | bc-core main `0e5e501d`; intake uid `4d849778-3989-4caf-8a71-7d44b782d98e` |
| PR #168 first real M12 execution evidence (amended per MCF-ERR-001) | bc-core main `16cf3781` |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) |
| MCF bridge ADR | `docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) |
| M12 authoring panel DBCP | `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` |
| M12.5 materialization DBCP | `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` |
| Session discipline | ADR DEC-ebf0b4 / D268 (one-then-many; independent verification; no shortcuts) |

## 3. Disposition decision

**The operator accepts `OPERATOR_REVIEW` as the terminal outcome for intake `4d849778-3989-4caf-8a71-7d44b782d98e`.**

This is the second of the two disposition paths PR #29 §8.2 contemplates:

> "Operator reviews the mapr + transcripts to decide whether to author a new intake row with refined candidate content, OR accept the OPERATOR_REVIEW as the terminal outcome for this intake."

The operator's reasoning, recorded for the record:

1. **First-real-M12 execution is proven.** The panel ran end-to-end with three real distinct vendor providers (`{anthropic, openai, google}`), each producing per-role transcripts with `prompt_hash` / `raw_response_hash` / `vendor_request_id` provenance. The trust path that PR #29 D8 condition 7 required is exercised.
2. **The candidate `overdue_invoice_count` is not the bottleneck.** Read-only inspection of the three transcripts (read against `mcf.metric_authoring_panel_transcript` for `panel_run_uid 9a462e6c-...`) showed all three roles producing approving prose:
   - Maker (anthropic / `claude-haiku-4-5`): "technically sound and operationally ready for M12 intake … Conditional recommendation: approve for D8 condition 7 evidence run"
   - Checker (openai / `gpt-4o-mini`): "well-defined and aligns with standard accounting practices … appears suitable for the first-real M12 evidence run"
   - Moderator (google / `gemini-flash-latest`): "fundamentally sound, highly standardized utility … aligns cleanly with M12 behavioral expectations" (truncated mid-sentence at `finish_reason: length`)
3. **The structured `verdict_code` field nevertheless returned `OPERATOR_REVIEW` on all three roles.** Each role recorded zero `tool_calls` and zero `claims`. The consensus algorithm aggregated three OPERATOR_REVIEW tokens into the consensus OPERATOR_REVIEW. The `grounding_check_passed: true` field is vacuously satisfied because there were zero claims to ground.
4. **The bottleneck is the panel framework, not the candidate.** Authoring a refined candidate now would burn another M12 run with the same prompt-engineering / tool-surface failure mode and likely produce a second OPERATOR_REVIEW. Per D268's "one-then-many" rule, the right next step is to investigate the framework before scaling. The investigation is scoped in `metric-context-framework-m12-panel-framework-calibration-followup.md`.

## 4. Standing state after disposition

### 4.1 M12 gate

- **Execution**: COMPLETE. First-real-M12 ran end-to-end with real provider trust path.
- **Substrate evidence written by the run** (read-only verified at this disposition):
  | Table | Count after run | Δ from pre-run baseline |
  |---|---|---|
  | `bcf.panel_output_record` | 21 | +1 |
  | `mcf.metric_authoring_panel_run` | 2 | +1 |
  | `mcf.metric_authoring_panel_transcript` | 6 | +3 |
  | `contract.panel_output_record` (A4 frozen) | 19 | 0 |
  | `mcf.metric_authoring_intake_queue` | 1 | 0 (row count; status verdict-aware) |
  | `mcf.metric_contract` | 0 | 0 |
  | `mcf.metric_contract_version` | 0 | 0 |
  | `mcf.workspace_tool_allowlist` | 10 | 0 |
  | `mcf.evidence_source_allowlist` | 6 | 0 |
- **PR #28 §9 / D8 condition 7 (first-real-M12 execution evidence)**: ✅ DISCHARGED
- **PR #29 §8.1 success criterion (A4 — any terminal verdict via real trust path)**: ✅ SATISFIED

### 4.2 M12.5 gate

- **Status**: BLOCKED (unchanged).
- **Reason**: M12.5's read predicate is `consensus_payload_json->>'verdict_code' = 'APPROVE_FOR_DRAFT'`. For `panel_run 9a462e6c-...`, that predicate evaluates `false` (verdict is `OPERATOR_REVIEW`). M12.5 has no eligible mapr to materialize.
- **`mcf.metric_contract` Δ**: 0. **`mcf.metric_contract_version` Δ**: 0. No metric contract was created. M12.5 is the first gate that may create either, and only for `APPROVE_FOR_DRAFT`. This disposition does not unlock M12.5.

### 4.3 M13 / M14 gates

- **Status**: BLOCKED (unchanged). Downstream of M12.5.

### 4.4 Intake row `4d849778-...` status

- **Substrate state**: `status_code = 'pending'`. This is correct under the code-true M12 verdict-aware mapping per MCF-ERR-001:
  - `APPROVE_FOR_DRAFT` → M12 leaves `pending`; M12.5 transitions to `consumed_by_panel` later (not invoked here)
  - **`OPERATOR_REVIEW` → M12 leaves `pending`; M12.5 stays gated** ← this run's case
  - `REJECT_DEFECT` → M12 transitions to `rejected`
- **Operator-side disposition**: TERMINAL. Notwithstanding the substrate's `pending` status, the operator's governance-side acceptance of OPERATOR_REVIEW as terminal closes this intake to further M12 attempts. The substrate's `pending` state is a code-true M12 contract artifact, not a re-entry license.
- **Single-use authorization (PR #29 §6 item 6)**: CONSUMED. The operator's PR #29 attestation was bound to exactly one M12 run. That run executed. The attestation is exhausted regardless of verdict and regardless of substrate state.

### 4.5 Future M12 attempt rule

Per PR #29 §8.3 + A5 (preserved by MCF-ERR-001):

- Any future M12 attempt MUST use a **new `reservoir_entry_id`** (the M11 substrate uniqueness constraint is `(reservoir_name, reservoir_entry_id)`).
- The attempt MUST be evidenced by a **new bc-core M11 intake row PR** mirroring the PR #167 pattern.
- The attempt MUST be authorized by a **fresh bc-docs authorization DBCP** mirroring the PR #29 pattern. PR #29 is single-use; it does not authorize subsequent runs.
- Additionally, per this disposition's deferment clause (§3 reason 4), **no refined-candidate retry will be initiated until the panel-framework calibration investigation (`metric-context-framework-m12-panel-framework-calibration-followup.md`) reaches a closeout state with bc-core code-change recommendations applied**, or until the operator separately and explicitly waives that deferment.

## 5. Standing gate state summary (after this disposition)

| Gate | State |
|---|---|
| PR #28 §9 / D8 condition 7 (first-real-M12 execution evidence) | DONE |
| PR #29 §8.1 success criterion (A4 — terminal verdict via real trust path) | SATISFIED |
| PR #29 §6 operator-side single-use authorization | CONSUMED |
| MCF-ERR-001 (verdict-to-intake-status correction governing PR #29) | ADOPTED |
| Intake `4d849778-...` | substrate `pending`; operator-side TERMINAL |
| M12 first-real-run unlock gate | CLOSED (single use spent) |
| M12.5 materialization gate | BLOCKED (`APPROVE_FOR_DRAFT` precondition unmet) |
| M13 / M14 | BLOCKED (downstream of M12.5) |
| `mcf.metric_contract` | 0 rows |
| `mcf.metric_contract_version` | 0 rows |
| PR #29 DBCP amendment (per MCF-ERR-001 `target_resolution`) | NOT AUTHORED (separate follow-up bc-docs PR; out of scope for this disposition) |
| Panel-framework calibration follow-up | OPEN per `metric-context-framework-m12-panel-framework-calibration-followup.md` |
| bc-docs main | `3926d021` (after PR #30) |
| bc-core main | `16cf3781` (after PR #168) |

## 6. Hard rule compliance

- **HR1 (real vendor calls only)** — proven by PR #168 evidence: 3 distinct vendor `vendor_request_id` values + per-role `prompt_hash` / `raw_response_hash` chains; three-vendor distinctness `{anthropic, openai, google}` verified at runtime.
- **HR2 (writer reached via orchestrator outer tx)** — proven by PR #161 + PR #162.
- **HR3 (no `contract.*` writes)** — `contract.panel_output_record` Δ = 0 (A4 freeze preserved).
- **HR4 (no tenant DB touch)** — proven by PR #168 evidence + this disposition operates against `bc_platform_dev` read-only only.
- **HR5 (production COMMIT path)** — proven by PR #168 evidence (mapr + mapt + bcf rows persisted; no rollback).
- **DEC-7f9597 / D423** — operator authorization recorded via PR #29 env-gate; this disposition is the operator-side closure of that authorization.
- **DEC-ebf0b4 / D268 (session discipline)** — this disposition applies the "one-then-many" rule: prove the first run, inspect it independently, fix the framework before scaling. Refined-candidate retry is explicitly deferred behind the calibration follow-up.

## 7. Verification (read-only)

This disposition was authored alongside an inline read-only substrate re-verification at `bc_platform_dev`. Eleven invariants confirmed (read-only `pg_query`):

```
bcf.panel_output_record                      = 21      ✅
contract.panel_output_record (A4 frozen)     = 19      ✅
mcf.metric_authoring_panel_run               = 2       ✅
mcf.metric_authoring_panel_transcript        = 6       ✅
mcf.metric_authoring_intake_queue            = 1       ✅
mcf.metric_contract                          = 0       ✅
mcf.metric_contract_version                  = 0       ✅
mcf.workspace_tool_allowlist                 = 10      ✅
mcf.evidence_source_allowlist                = 6       ✅
intake 4d849778-... status_code              = pending ✅
panel_run 9a462e6c-... verdict_code          = OPERATOR_REVIEW ✅
```

No drift since PR #168 execution. No mutations performed by this disposition.

## 8. References

- `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` — M12 design (Step 8 + outcome table + D-M12-8)
- `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` — M12.5 design (APPROVE_FOR_DRAFT precondition + `markConsumedByPanel` ownership)
- `docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md` (PR #29) — single-use authorization for `panel_run 9a462e6c-...`
- `docs/errata/MCF-ERR-001.md` (PR #30) — verdict-to-intake-status correction governing PR #29
- `docs/implementation/metric-context-framework-m12-panel-framework-calibration-followup.md` (this PR) — investigation scope that gates any refined-candidate retry
- `docs/operating-model/mcf-legacy-bridge.md` — M11 → M12 → M12.5 → M13 → M14 lifecycle
- bc-core PR #168 — first-real-M12 execution evidence; `panel_run_uid 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`; verdict `OPERATOR_REVIEW`; merge SHA `16cf3781`
- bc-core PR #167 — first real M11 intake row evidence; intake uid `4d849778-3989-4caf-8a71-7d44b782d98e`; merge SHA `0e5e501d`
- bc-core `src/registry/mcf/metric-authoring-panel.service.ts` (PR #161 merge `a0fee4e9`) — M12 panel service
- bc-core `src/registry/mcf/metric-authoring-materialization.service.ts` (PR #126 merge `49ebd3c2`) — M12.5 materialization service
