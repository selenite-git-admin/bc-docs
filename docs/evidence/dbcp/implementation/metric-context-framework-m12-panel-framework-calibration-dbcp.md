---
uid: metric-context-framework-m12-panel-framework-calibration-dbcp
title: MCF M12 — Panel-Framework Calibration DBCP (decision α — build the approval-capable panel)
description: Authoritative governance DBCP converting the read-only calibration investigation arising from the first-real-M12 OPERATOR_REVIEW outcome (`panel_run_uid 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`, intake `4d849778-3989-4caf-8a71-7d44b782d98e`, bc-core PR #168 merge `16cf3781`) into an explicit locked-decision-α path forward. Records the current truth that all three M12 vendor adapters (`anthropic-agent.adapter.ts`, `openai-agent.adapter.ts`, `google-agent.adapter.ts`) at bc-core merge `16cf3781` are PROVENANCE-ONLY SCAFFOLDING that satisfies PR #28 §4.2 + D2 + D4 + §11.1-§11.5 but does NOT implement the M12 panel logic. Adapters hardcode `verdict_code = 'OPERATOR_REVIEW'`, `tool_calls = []`, `claims = []`; do not load the role prompt files at `src/registry/mcf/prompts/m12-panel-{maker,checker,moderator}.v1.md`; do not parse structured verdicts from LLM output; do not request structured output; do not implement multi-turn tool-calling loops. No production `PanelToolSurface` implementation exists — only the empty-stub `makeMinimalToolSurfaceStub()` in `scripts/mcf-m12-first-real-run.mjs:500-516`. Consequence: M12 CANNOT produce `APPROVE_FOR_DRAFT` under any candidate; M12.5 / M13 / M14 are blocked indefinitely until the panel is built. Locks decision α — build the approval-capable panel — and rejects β (document-and-pause) and γ (re-scope to advisory-only). Specifies the nine-item must-fix + should-fix + nice-to-have fix set (F1 prompt loading; F2 structured-output requests; F3 verdict/claim/tool_call parsing; F4 production `PanelToolSurface`; F5 multi-turn tool loops; F6 consensus fail-closed on zero-claim APPROVE; F7 `all_operator_review` labeling; F8 Google token budget; F9 evidence rerun gate). Specifies the eight-PR sequence: PR-G1 this DBCP, PR-C1 production PanelToolSurface, PR-C2 adapter rewrites, PR-C3 consensus hardening, PR-E1 new intake evidence, PR-G2 fresh first-real-M12 authorization, PR-E2 calibrated evidence run, PR-G3 (only if PR-E2 returns APPROVE_FOR_DRAFT) M12.5 next-gate DBCP. Locks gating contract: no M12 retry until F1-F5 implemented + proven; no M12.5 / M13 / M14 invocation until PR-E2 returns APPROVE_FOR_DRAFT. **NOT EXECUTED** — docs-only governance DBCP. No code, no DB, no provider calls, no `runPanel()`, no writer, no M12.5 / M13 / M14, no metric contract, no rollback, no tenant DB, no substrate mutation, no new intake row, no fresh authorization beyond this DBCP itself.
status: proposed
date: 2026-05-30
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-panel-framework-calibration
supersedes:
superseded_by:
---

# MCF M12 — Panel-Framework Calibration DBCP (decision α)

## 1. Scope

### 1.1 Question this DBCP answers

> The first real M12 panel run (`panel_run_uid 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`) executed end-to-end with three real vendor providers and produced consensus verdict `OPERATOR_REVIEW`. The disposition record (`metric-context-framework-m12-first-real-run-disposition.md`, PR #31 merge `42f74fc9`) accepted that outcome as terminal and deferred any refined-candidate retry behind a panel-framework calibration follow-up (`metric-context-framework-m12-panel-framework-calibration-followup.md`). A read-only investigation against bc-core merge `16cf3781` then revealed that all three vendor adapters are provenance-only scaffolding — they hardcode `verdict_code = 'OPERATOR_REVIEW'` and do not implement verdict parsing, structured output, tool calling, or prompt loading. The current M12 cannot produce `APPROVE_FOR_DRAFT` under any candidate. Three architectural paths exist: (α) build the approval-capable panel; (β) document the scaffolding state and pause MCF authoring indefinitely; (γ) re-scope M12 to operator-assisted advisory commentary, superseding DEC-c3e57f / D422 in part. Which path does the operator authorize, and what is the required fix set, sequencing, gating contract, and risk envelope?

### 1.2 In scope

- Current-truth statement about the M12 implementation state at bc-core merge `16cf3781`
- Architectural decision lock — α / β / γ — with reasoning
- The nine-item required fix set F1–F9 (must-fix blockers F1–F5; should-fix correctness F6–F7; nice-to-have F8; evidence-rerun gate F9)
- The eight-PR sequencing — PR-G1 (this DBCP) → PR-C1 → PR-C2 → PR-C3 → PR-E1 → PR-G2 → PR-E2 → conditional PR-G3
- The gating contract that locks M12 retry behind F1–F5 + F9 and locks M12.5 / M13 / M14 behind PR-E2's `APPROVE_FOR_DRAFT`
- The risk register R1–R10
- The standing gate state
- The hard-rule mapping (HR1–HR5 + DEC-7f9597 + DEC-ebf0b4 / D268)
- Explicit non-execution confirmation

### 1.3 Explicit non-scope

- ❌ No code is authored or modified by this DBCP — bc-core stays at merge `16cf3781`
- ❌ No `runPanel()` invocation
- ❌ No standalone writer invocation
- ❌ No M12.5 / M13 / M14 invocation
- ❌ No provider API calls
- ❌ No metric contract creation
- ❌ No rollback
- ❌ No tenant DB touch
- ❌ No substrate mutation (`bc_platform_dev` may be queried read-only only)
- ❌ No new M11 intake row (PR-E1 is forward-looking; this DBCP does not author it)
- ❌ No fresh first-real-M12 authorization beyond authorizing the calibration arc itself (PR-G2 is forward-looking; this DBCP does not author it)
- ❌ No bc-core PR opening or commit
- ❌ No supersession of DEC-c3e57f / D422 — decision α preserves the existing MCF architecture; β and γ are explicitly rejected
- ❌ No M16 / M17 / M18 migration scope — those gates are separately governed (MCF Legacy Bridge `mcf-legacy-bridge.md`)
- ❌ No refined-candidate-retry commitment — PR-E1 deliberately reuses the same candidate (`overdue_invoice_count`) to isolate framework effects from candidate effects
- ❌ No commitment to a fix-arc completion date — this DBCP locks the SCOPE, not the schedule

## 2. Authority anchors

| Anchor | Reference | Role in this DBCP |
|---|---|---|
| PR #28 deferred prerequisites DBCP | bc-docs-v3 main `55bc4759` | Original scope of the adapter implementation (provenance round-trip; NOT verdict parsing) — explains why the current adapters are correctly scoped to PR #28 yet insufficient for approval-capable M12 |
| PR #29 first-real-M12 authorization DBCP | bc-docs-v3 main `a18d6e3c` | Single-use authorization that produced `panel_run 9a462e6c-...`; CONSUMED |
| MCF-ERR-001 (PR #30) | bc-docs-v3 main `3926d021` | Verdict-to-intake-status correction governing PR #29 — preserves operator-side single-use rule |
| PR #168 first-real-M12 execution evidence (amended) | bc-core main `16cf3781` | Provenance-verified panel run; verdict `OPERATOR_REVIEW`; substrate state at investigation anchor |
| PR #31 disposition + calibration follow-up | bc-docs-v3 main `42f74fc9` | Deferred refined-candidate retry behind framework investigation; investigation outputs are the inputs to this DBCP |
| M12 authoring panel DBCP | `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` | Original M12 design — verdict semantics, consensus contract, tool surface; consequences in §4 of this DBCP |
| M12.5 materialization DBCP | `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` | Downstream consumer of M12 output; stays gated under decision α until PR-E2 returns APPROVE_FOR_DRAFT |
| MCF bridge ADR | `docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) | Architectural foundation preserved by decision α; β and γ would supersede portions of D422 |
| Stance ADR | `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) | Operator authorization discipline applied to every gate in this calibration arc |
| Session discipline ADR | `docs/adrs/ADR-ebf0b4.md` (DEC-ebf0b4 / D268) | "One-then-many" / "prove before scaling" — anchors decision α's "build before retry" gate |
| MCF Legacy Bridge | `docs/operating-model/mcf-legacy-bridge.md` | M11 → M12 → M12.5 → M13 → M14 lifecycle; legacy `metric.metric_definition` path remains available during the calibration window |

## 3. Current truth (read-only investigation findings at bc-core merge `16cf3781`)

### 3.1 What worked (provenance-only scaffolding satisfies PR #28)

- First-real-M12 execution is **complete** and closed as terminal `OPERATOR_REVIEW` per PR #31 disposition.
- That run **proved** the three-vendor real provider/provenance plumbing:
  - 3 distinct vendor `vendor_request_id` values captured across `{anthropic, openai, google}`
  - Per-role `prompt_hash` + `raw_response_hash` chains captured
  - Latency + usage + model_id + finish_reason captured per role
  - Orchestrator → writer outer-tx path proven (HR2)
  - `contract.panel_output_record` A4 freeze preserved (HR3)
  - Tenant DB untouched (HR4)
  - Production COMMIT path proven (HR5)
- That run **does NOT prove** approval-capable panel behavior:
  - Vendor narrative reasoning was approving across all 3 roles (verbatim quotes preserved in `mcf.metric_authoring_panel_transcript.transcript_payload_json` for `panel_run_uid 9a462e6c-...` and reproduced in PR #31 calibration follow-up §3.2)
  - Structured `verdict_code` returned `OPERATOR_REVIEW` on all 3 roles
  - Per-role `claim_count = 0`, `tool_call_count = 0`
  - Consensus correctly aggregated three OPERATOR_REVIEW → consensus OPERATOR_REVIEW with `operator_review_reason = mixed_verdicts` (algorithmic catchall; not behaviorally wrong but cosmetically misleading)
  - `mcf.metric_contract` Δ = 0; `mcf.metric_contract_version` Δ = 0

### 3.2 What does not work yet (the gap PR #28 deferred)

The current adapter implementation at bc-core merge `16cf3781`:

| # | Finding | Citation |
|---|---|---|
| **T1** | All three vendor adapters **HARDCODE** `verdict_code = 'OPERATOR_REVIEW'` in `buildOkResult()` | `anthropic-agent.adapter.ts:225`, `openai-agent.adapter.ts:216`, `google-agent.adapter.ts:216` |
| **T2** | All three adapters **HARDCODE** `tool_calls: []` and `claims: []` regardless of LLM response | Same lines, same files |
| **T3** | All three adapters use a 5-line **dumbed-down inline prompt** that does not enumerate the verdict vocabulary, request structured JSON, enumerate the tool surface, or instruct claim-level grounding | `anthropic-agent.adapter.ts:127-136`, `openai-agent.adapter.ts:125-134`, `google-agent.adapter.ts:121-130` |
| **T4** | The role prompt files **exist on disk but are never loaded by code** | `src/registry/mcf/prompts/m12-panel-{maker,checker,moderator}.v1.md` exist; `grep -r m12-panel-.*v1.md src/` returns zero hits |
| **T5** | No code in `src/registry/mcf/` **parses a verdict from LLM text** | `grep -rE "parse.*verdict\|extract.*verdict\|verdict.*from.*response" src/registry/mcf/ --include="*.ts"` returns no panel-related matches |
| **T6** | No code in bc-core **implements `PanelToolSurface`** for production | `grep -rn "implements PanelToolSurface\|class.*PanelToolSurface\|: PanelToolSurface =" src --include="*.ts" | grep -v ".spec.ts"` returns zero hits |
| **T7** | The only `PanelToolSurface` implementation is the **empty stub** in the execution script | `scripts/mcf-m12-first-real-run.mjs:500-516` `makeMinimalToolSurfaceStub()` returns empty `payload: {}` for all 10 tools |
| **T8** | No adapter passes a `tools` parameter to its vendor SDK; no adapter implements a multi-turn tool-calling loop | `anthropic-agent.adapter.ts:103-107`, `openai-agent.adapter.ts:101-105`, `google-agent.adapter.ts:97-101` — all single-turn `messages.create` / `chat.completions.create` / `generateContent` |
| **T9** | The consensus algorithm collects `empty_claims` (line 36 of `panel-consensus.ts`; populated at `metric-authoring-panel.service.ts:399`) but **never reads it** in `computeConsensus()` | `panel-consensus.ts:57-119` — branches on `completed`, `verdict_code`, `defect_code`, `grounding_check_passed`; never on `empty_claims` |
| **T10** | Grounding-check passes **vacuously** when `claims = []` — the loop at `panel-grounding-check.ts:50` does not iterate; violations stay empty; `passed: true` | `panel-grounding-check.ts:41-60` |
| **T11** | The hardcoded `verdict_code = 'OPERATOR_REVIEW'` is **tested as intended behavior**, not as a placeholder | `anthropic-agent.adapter.spec.ts:96` — `expect(result.transcript.verdict_code).toBe('OPERATOR_REVIEW')` — no TODO, no FIXME, no future-marker comment |
| **T12** | `APPROVE_FOR_DRAFT` paths are exercised in tests only via **synthetic fixture data** (manually-constructed `consensus_payload_json`); no real-LLM code path produces it | `metric-authoring-materialization.service.integration.spec.ts:75+` constructs `verdict_code: 'APPROVE_FOR_DRAFT'` inline |
| **T13** | Gemini Moderator output truncated at `finish_reason: length`; `DEFAULT_MAX_OUTPUT_TOKENS = 1024` at `model-defaults.ts:90`; Gemini reports `totalTokenCount = 1205` vs `input(185) + output(136) = 321` — ~884-token gap consistent with Gemini thinking-token accounting | `model-defaults.ts:90`; `google-agent.adapter.ts:97-101` |
| **T14** | The schema enum for `operator_review_reason` lacks `all_operator_review` — the consensus algorithm correctly routes the unanimous-OPERATOR_REVIEW case into the `mixed_verdicts` catchall (cosmetic only, not a behavior bug) | `panel-payload.schema.json:64-70`; `panel-consensus.ts:113-118` |

### 3.3 Architectural consequence

Under the current adapter implementation at bc-core merge `16cf3781`:

- **M12 cannot produce `APPROVE_FOR_DRAFT` under any candidate.** No combination of candidate refinement, BCF enrichment, prompt-version bump, or tool-surface enrichment can reach `APPROVE_FOR_DRAFT` while T1 + T11 + T12 hold — the verdict is hardcoded.
- **M12.5 is blocked indefinitely.** M12.5's `APPROVE_FOR_DRAFT` precondition (`metric-authoring-materialization.service.ts:364-368`) returns `MaterializationPreconditionError` for any mapr produced by current adapters.
- **M13 / M14 are blocked downstream of M12.5.**
- **`mcf.metric_contract` / `mcf.metric_contract_version` cannot be populated** through the MCF pipeline at present. Legacy `metric.metric_definition` writes via `POST /api/metric-catalog/definitions` continue to function (per MCF Legacy Bridge); they are not affected.
- **PR #28 was correctly scoped.** The DBCP scoped the adapter work to provenance round-trip + provenance keys + service/API-only rule (§4.2 + D2 + D4 + §11.1-§11.5). The DBCP did not require verdict parsing, prompt loading, structured-output requests, or tool-calling loops. The adapter implementation at bc-core merge `16cf3781` is consistent with PR #28 — it is insufficient for approval-capable M12 because PR #28 did not specify approval-capable M12.

## 4. Locked decision α — build the approval-capable panel

### 4.1 Decision

**The operator locks decision α: BUILD the real approval-capable M12 panel before any retry, and DO NOT downgrade scope.**

Specifically:

- **α.1** The required fix set F1–F5 (§5.1 below) MUST be implemented and proven before any new M12 panel run is authorized against any candidate. PR-E1 + PR-G2 + PR-E2 (§6 below) sequence enforces the gate.
- **α.2** The "Decision α — build" path is chosen over:
  - **β (document-and-pause)** — REJECTED. β would freeze the MCF authoring pipeline at its current scaffolding state and route all future metric authoring through the legacy `POST /api/metric-catalog/definitions` endpoint indefinitely. The MCF Legacy Bridge anticipates a coexistence window, not a permanent MCF retirement. β would functionally undo the MCF arc (PR #28 through PR #168) by accepting that MCF cannot produce metric contracts.
  - **γ (re-scope to advisory)** — REJECTED. γ would re-scope M12 to "operator-assisted draft authoring" where the panel provides advisory commentary on operator-authored proposals (operator writes `CandidateProposal`; panel's verdict is overridable). γ requires a new ADR superseding portions of DEC-c3e57f / D422, which would shift MCF away from the "AI consensus constitutes Framework Approval" stance recorded in the MCF Requirements §1.3. The operator chooses not to make that architectural concession now.
- **α.3** The current scaffolding (bc-core merge `16cf3781`) MUST NOT be treated as sufficient for M12.5 invocation. Any code path or operator action that would invoke M12.5 against the current adapter output is forbidden by this DBCP regardless of other operator authorizations until PR-E2 returns APPROVE_FOR_DRAFT.
- **α.4** No refined-candidate retry will be authored until the calibrated framework is proven by PR-E2. PR-E1 deliberately re-uses the same candidate (`overdue_invoice_count`) so that the PR-E2 outcome isolates framework effects from candidate effects. Once the framework is proven approval-capable, refined-candidate work becomes a separate stream.

### 4.2 What α preserves

- **MCF architecture stance** — MCF owns the full MC lifecycle including the `metric_contract` artifact (per `mcf.metric_contract`, `mcf.metric_contract_version`, and the 17 MCF substrate tables). The M12.5 gate continues to be the first writer of `metric_contract` and only on `APPROVE_FOR_DRAFT`.
- **PR #28 provenance contract** — the existing provenance keys (`vendor_request_id`, `prompt_hash`, `raw_response_hash`, `latency_ms`, `usage`, `status`, etc.) survive the F1–F5 adapter rewrite unchanged. F1–F5 ADD verdict parsing + tool calling + prompt loading on top of, not in place of, the existing provenance contract.
- **PR #29 + MCF-ERR-001 verdict-to-intake-status mapping** — the verdict-aware semantics (APPROVE → pending then M12.5 transitions; OPERATOR_REVIEW → pending; REJECT_DEFECT → rejected) survive unchanged.
- **PR #31 disposition** — `panel_run 9a462e6c-...` remains terminal OPERATOR_REVIEW for intake `4d849778-...`. Future M12 attempts under the calibrated framework use NEW intake rows.
- **MCF Legacy Bridge** — legacy `POST /api/metric-catalog/definitions` remains the active metric-authoring path during the calibration window. The Sunset header continues to advise deprecation; HTTP 410 transition stays at M17.

### 4.3 What α explicitly does NOT do

- **Does NOT lower the M12 panel's responsibility scope** — the M12 panel under α remains the authoritative consensus computation over three vendor verdicts. It does NOT become advisory.
- **Does NOT supersede DEC-c3e57f / D422** — the MCF bridge ADR remains intact.
- **Does NOT change the M12 authoring panel DBCP design** — the consensus payload shape, verdict vocabulary, tool surface contract, and grounding-check algorithm survive unchanged.
- **Does NOT change the M12.5 / M13 / M14 design** — they stay gated behind APPROVE_FOR_DRAFT.
- **Does NOT change MCF requirements §1.3** (AI consensus constitutes Framework Approval).
- **Does NOT introduce new substrate** — F1–F5 are code-only; no DDL.

## 5. Required fix set

### 5.1 Must-fix blockers (none of these can be skipped to reach APPROVE_FOR_DRAFT)

| # | Fix | Touches | Why a blocker |
|---|---|---|---|
| **F1** | **Adapters load + interpolate the role prompts** from `src/registry/mcf/prompts/m12-panel-{maker,checker,moderator}.v1.md` at `buildPrompt()` time. Replace the 5-line inline prompts with the full prompt-file content + intake metadata interpolation. Add a prompt-loader helper (read-once at adapter construction or cached at module level). | `anthropic-agent.adapter.ts:127-136`, `openai-agent.adapter.ts:125-134`, `google-agent.adapter.ts:121-130`; new prompt-loader module | Vendors cannot produce structured verdicts without being told to. The current prompt asks for "a single concise paragraph" of free-form prose. The full prompt files describe the verdict vocabulary, tool surface, claim-grounding rule, and structured-output contract. |
| **F2** | **Adapters request structured JSON output** matching `TranscriptPayloadV1` shape. Per-vendor mechanism: Anthropic — tool-based structured output via JSON schema; OpenAI — `response_format: { type: "json_schema", json_schema: { name, schema, strict: true } }`; Google — `responseMimeType: 'application/json'` + `responseSchema`. Schema source MUST be the existing `panel-payload.schema.json` or a per-role subset thereof. | Same 3 adapters; possibly a new helper that compiles `panel-payload.schema.json` into per-vendor structured-output configs | Without structured output, the LLM emits prose. The current adapter accepts prose because it discards verdict info anyway. After F1 instructs the LLM, F2 enforces the response shape so the parser in F3 has stable input. |
| **F3** | **Adapters parse `verdict_code`, `defect_code`, `claims`, `tool_calls`, `reasoning_trace`** from the LLM's structured response. Validate against `TranscriptPayloadV1` types + `panel-payload.schema.json` enums. On parse failure: emit `status_code: 'completed_with_verdict'` if at least verdict_code is parseable; emit `status_code: 'vendor_failure'` otherwise. Per-role agent transcripts now carry the parsed structured fields, not hardcoded defaults. | `buildOkResult()` in all 3 adapters | Without parsing, the verdict is hardcoded regardless of what F1 + F2 deliver. F3 is the actual elimination of the OPERATOR_REVIEW hardcoding. |
| **F4** | **Production `PanelToolSurface` implementation** that reads from `concept_registry.*` (BCF) via existing BCF read services, exposes evidence search/retrieve against the `mcf.evidence_source_allowlist` allowlist, exposes `source_reality.summarize` against tenant-side reader output (read-only), exposes `kpi_catalog.read_intent` against legacy `metric.metric_definition` (non_citable: true), and exposes `mc.identity_probe` against `mcf.metric_contract`. New module(s) under `src/registry/mcf/` or `src/registry/`. Wire into `panel-agent-factory.ts` or `metric-authoring-panel.service.ts` so the runtime tool surface is the production implementation, not the script's empty stub. | New file(s); `panel-agent-factory.ts`; `metric-authoring-panel.service.ts` | Even if F1–F3 elicit structured verdicts and claim/tool-call attempts, the vendors have no data to ground claims against without a working tool surface. F4 enables F5. |
| **F5** | **Multi-turn tool-calling loops** in each adapter. When the LLM emits a tool call, dispatch to `PanelToolSurface`, capture the response, append to the LLM conversation, repeat until the LLM emits a final structured response with no further tool calls (or hits a turn-budget). Per-vendor mechanism: Anthropic — `tool_use` messages with `tool_result` responses; OpenAI — `tool_calls` with `tool` role responses; Google — function calling with response parts. Capture each tool call in `transcript_payload_json.tool_calls` per `TranscriptPayloadV1` shape. | Each adapter's `run()` method becomes a state machine; new turn-budget config in `model-defaults.ts` or `RoleAgentInput` | Without multi-turn loops, the LLM either doesn't request tool calls (single-shot prompt) or requests them once and then has no mechanism to receive results. F5 is the structural change from one-shot to conversation. |

### 5.2 Should-fix correctness improvements (same arc, separate PR)

| # | Fix | Touches | Why same arc |
|---|---|---|---|
| **F6** | **Consensus fail-closed when any APPROVE_FOR_DRAFT transcript has zero claims or zero grounded support.** Update `computeConsensus()` to read the existing `empty_claims` field and route to `OPERATOR_REVIEW` with `operator_review_reason: 'approve_without_claims'` for any role whose verdict is `APPROVE_FOR_DRAFT` AND `empty_claims === true`. Adds the new `operator_review_reason` value to `panel-payload.schema.json`, `panel-payload.types.ts`, and `panel-consensus.ts`. Closes the silent-correctness risk identified at T9. | `panel-consensus.ts:57-119`; `panel-payload.types.ts:24-31`; `panel-payload.schema.json:58-74` | Without F6, a future bug or prompt change that emits APPROVE_FOR_DRAFT with zero claims would silently pass grounding and reach M12.5. F6 makes the consensus algorithm match the grounding-check intent. |
| **F7** | **Add `operator_review_reason: 'all_operator_review'`** to disambiguate from `mixed_verdicts`. Update the consensus algorithm to set the new reason when all 3 verdicts are `OPERATOR_REVIEW`. Schema + type + algorithm update. Cosmetic-clarity improvement; does NOT change consensus behavior. | Same files as F6 | Same-arc because it's the same schema + types + consensus changes; reviewing F6 + F7 together is more efficient than separately. |

### 5.3 Nice-to-have (separable)

| # | Fix | Touches | Separable because |
|---|---|---|---|
| **F8** | **Raise / fix Google Moderator max-output-tokens.** Increase `DEFAULT_MAX_OUTPUT_TOKENS` for the Google adapter (and possibly per-role override capability) to 4096 or 8192 to accommodate Gemini's thinking-token accounting. Possibly introduce per-vendor or per-role overrides in `model-defaults.ts`. | `model-defaults.ts:90`; possibly `panel-agent-factory.ts` for per-role config | Separable from F1–F5 because under the current adapter (no verdict parsing), token budget does not affect the OPERATOR_REVIEW outcome. F8 becomes urgent the moment F3 lands and Moderator truncation starts causing parse failures. Ship in PR-C2 or as a follow-up at the operator's discretion. |

### 5.4 Evidence-rerun gate (separately operator-authorized)

| # | Fix | Touches | Gate semantics |
|---|---|---|---|
| **F9** | **Require a post-fix evidence rerun before any refined-candidate retry or M12.5 attempt.** PR-E2 (§6) is the rerun. It re-uses the same candidate (`overdue_invoice_count`) and a NEW M11 intake row (PR-E1) under a FRESH first-real-M12 authorization DBCP (PR-G2). The rerun's verdict is the gating signal:<br/>• If `APPROVE_FOR_DRAFT` → calibration validated; M12.5 next-gate DBCP authoring authorized as a separate operator-authorized track.<br/>• If `OPERATOR_REVIEW` → calibration insufficient or candidate genuinely uncertain; operator decides between further framework investigation, refined-candidate retry, or accepting OPERATOR_REVIEW as steady-state.<br/>• If `REJECT_DEFECT` → calibration found a genuine defect; defect code surfaces the issue. | New script + new intake row PR + new authorization DBCP | The rerun MUST use the same candidate to isolate framework effects. Refined-candidate retry is a separate stream that opens after F9 returns APPROVE_FOR_DRAFT. F9 is the trust-gate for M12.5. |

## 6. Sequencing — eight PRs

The fix arc decomposes into eight PRs across bc-docs-v3 (governance) and bc-core (code + evidence). Each PR is independently operator-authorized; later PRs depend on earlier PRs landing.

| # | PR | Repo | Purpose | Approximate scope | Depends on |
|---|---|---|---|---|---|
| **PR-G1** | This DBCP | bc-docs-v3 | Lock decision α + fix set + sequencing + gating contract | ~600 lines docs | None |
| **PR-C1** | Production `PanelToolSurface` | bc-core | F4 — tool-surface implementation that reads from `concept_registry.*` + evidence + tenant-side source-reality + `mcf.metric_contract` for `mc.identity_probe`. Per-tool unit tests. Wired into `panel-agent-factory.ts`. **NO adapter changes.** | ~400-600 lines code + tests | PR-G1 merged |
| **PR-C2** | Adapter rewrites | bc-core | F1 + F2 + F3 + F5 — load prompts; request structured output; parse verdict / claims / tool_calls / reasoning_trace; implement multi-turn tool-calling loop per vendor. F8 (Google token budget) included in same PR. Per-adapter unit tests + integration tests against the PR-C1 tool surface. | ~800-1200 lines code + tests; **largest PR in the arc** | PR-C1 merged |
| **PR-C3** | Consensus hardening | bc-core | F6 + F7 — consensus algorithm uses `empty_claims`; adds `approve_without_claims` + `all_operator_review` to schema + type + algorithm. Per-case unit tests + integration tests. | ~150 lines code + tests | PR-C2 merged |
| **PR-E1** | New M11 intake evidence | bc-core | New intake row for the rerun candidate (`overdue_invoice_count` reused). Mirrors PR #167 pattern. Adapter for `operator_direct` reservoir with a new timestamp-anchored `reservoir_entry_id`. | ~150 lines script + evidence | PR-C3 merged |
| **PR-G2** | Fresh first-real-M12 authorization DBCP | bc-docs-v3 | Mirrors PR #29 pattern. Binds the new intake uid + new bc-core SHA (post PR-C3) + new env-gate literal. Single-use. | ~300 lines docs | PR-E1 merged |
| **PR-E2** | Calibrated M12 evidence run | bc-core | Invokes `runPanel()` against the new intake under the calibrated framework. Captures evidence including parsed verdict, claims, tool_calls per role. | ~500 lines script + evidence | PR-G2 merged (and authorization env-gate consumed) |
| **PR-G3** | **Conditional** — M12.5 next-gate DBCP | bc-docs-v3 | **Only authored if PR-E2 returns `APPROVE_FOR_DRAFT`.** Authorizes the first M12.5 materialization against the PR-E2 mapr. | ~300 lines docs | PR-E2 returned APPROVE_FOR_DRAFT |

### 6.1 Gating contract

- **No M12 retry until F1–F5 implemented AND proven** — PR-E2 is the proof.
- **No M12.5 / M13 / M14 invocation until PR-E2 returns `APPROVE_FOR_DRAFT`** — PR-G3 is the unlock gate.
- **No refined-candidate work until PR-E2 returns a terminal verdict** under the calibrated framework. Refined-candidate work is a separate stream that opens after F9; this DBCP does not author it.
- **No `mcf.metric_contract` row is created in this arc** until PR-G3 authorizes M12.5 and an operator-authorized M12.5 invocation occurs. Until then, `mcf.metric_contract = 0` and `mcf.metric_contract_version = 0`.

### 6.2 Per-PR operator authorization

Each PR-G* DBCP carries a per-gate operator authorization clause per the DEC-7f9597 stance. PR-C1 / PR-C2 / PR-C3 are bc-core code PRs requiring operator-authorization on the PR description (the standard bc-core review path). PR-E1 / PR-E2 are evidence-capture PRs gated by their preceding authorization DBCPs.

## 7. Risk register

| # | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **R1** | F2 vendor-specific structured-output APIs evolve faster than expected; per-vendor implementation diverges | medium | medium | Pin SDK versions in `package.json`; integration tests against pinned versions; document the structured-output mechanism per vendor in PR-C2 |
| **R2** | F4 production `PanelToolSurface` implementation exposes a side-effect path that bypasses HA-4 (BCF read-only discipline) | low | high | Code review focus on HA-4 in PR-C1; ToolNotAllowlistedError + read-only DB role enforcement; unit tests confirm no write attempts; integration tests confirm no DDL/DML |
| **R3** | F5 multi-turn tool-calling loops introduce timeout / cost-ceiling cases not covered by current single-turn logic | medium | medium | Existing timeout machinery (`callWithTimeout`) reused per turn; cost-ceiling guard at the loop level; per-vendor turn-budget cap in `RoleAgentInput`; PR-C2 unit tests for timeout / budget-exhaustion paths |
| **R4** | F1 prompt files diverge from `TranscriptPayloadV1` schema as types evolve | low | medium | F2 binds the LLM output to `panel-payload.schema.json`; schema is the single source of truth; prompt files reference the schema; CI lint can later verify prompt files mention the same enum tokens the schema declares |
| **R5** | PR-E2 returns `OPERATOR_REVIEW` again under the calibrated framework; calibration insufficient or candidate genuinely uncertain | medium | medium-high | F9 gating contract anticipates this — operator decides between further framework investigation, refined-candidate retry, or accepting OPERATOR_REVIEW as steady-state per PR-E2's outcome. The calibration arc does NOT assume PR-E2 will return APPROVE_FOR_DRAFT; it assumes PR-E2 will produce a meaningful signal regardless of verdict. |
| **R6** | PR-E2 returns `REJECT_DEFECT` with a defect code; candidate `overdue_invoice_count` was acceptable to the scaffolding but rejected by the calibrated framework | low | low | Defect code surfaces the issue; operator decides whether to refine the candidate or investigate the calibrated framework's rejection criterion. Defect-rejection is a healthy signal that the framework calibration is producing meaningful verdicts. |
| **R7** | F4 tool surface exposes `mc.identity_probe` and surfaces existing mcf metric contracts in a way that biases the LLM toward false-positive identity collisions | low | medium | `mc.identity_probe` returns deterministic hash-comparison only; the schema at `panel-tool-surface.types.ts:64` specifies `identity_tuple_hash` input; no fuzzy matching; PR-C1 unit tests cover the deterministic path |
| **R8** | Adapter rewrite (PR-C2) breaks existing test infrastructure that depended on the hardcoded OPERATOR_REVIEW output | high | low | T11 confirms the hardcoded behavior is currently tested; PR-C2 MUST update those tests in the same commit. Test changes are isolated to `panel-agents/*.spec.ts` and `metric-authoring-panel.service.spec.ts`. |
| **R9** | Google thinking-token accounting changes between SDK versions; F8 token-budget value becomes stale | medium | low | PR-C2 documents the token-budget rationale; future SDK upgrades treat token-budget as a config knob; reasonable upper bound (8192) prevents most truncation regardless of thinking-token mechanics |
| **R10** | Calibration arc duration extends beyond what the operator anticipated; legacy `POST /api/metric-catalog/definitions` becomes the de-facto authoring path for an extended period | medium | low | This DBCP locks SCOPE, not SCHEDULE. The MCF Legacy Bridge `mcf-legacy-bridge.md` anticipates a coexistence window; no fixed cutover date; HTTP 410 transition stays at M17. Legacy path continues to work throughout the arc. |

## 8. Standing gate state

### 8.1 Pre-DBCP (current state)

| Item | State |
|---|---|
| bc-docs-v3 main | `42f74fc9` (after PR #31) |
| bc-core main | `16cf3781` (after PR #168) |
| First-real-M12 execution | COMPLETE (verdict OPERATOR_REVIEW; `panel_run 9a462e6c-...`) |
| PR #28 §9 / D8 condition 7 | DISCHARGED |
| PR #29 §8.1 A4 success criterion | SATISFIED |
| PR #29 §6 single-use authorization | CONSUMED |
| Intake `4d849778-...` | substrate `pending`; operator-side TERMINAL per PR #31 |
| MCF-ERR-001 | ADOPTED |
| M12.5 / M13 / M14 | BLOCKED |
| `mcf.metric_contract` | 0 rows |
| `mcf.metric_contract_version` | 0 rows |
| M12 panel framework state | Provenance-only scaffolding; cannot produce APPROVE_FOR_DRAFT under any candidate |
| Calibration follow-up | OPEN per PR #31 (status `proposed`, tag `mcf-framework-calibration`) |

### 8.2 Post-DBCP (this PR merges)

| Item | State |
|---|---|
| bc-docs-v3 main | advances by one squash commit |
| bc-core main | UNCHANGED at `16cf3781` |
| Decision α | LOCKED |
| F1–F9 | SCOPED and SEQUENCED |
| PR-C1 / PR-C2 / PR-C3 | AUTHORIZED to be authored (bc-core code PRs) — operator authorization on each PR description per standard bc-core review |
| PR-E1 / PR-G2 / PR-E2 | FORWARD-LOOKING; not authored by this DBCP |
| PR-G3 | CONDITIONAL on PR-E2 returning APPROVE_FOR_DRAFT |
| M12 first-real-run unlock gate | CLOSED (single use spent per PR #31); any future M12 attempt requires PR-G2 + new intake (PR-E1) |
| M12.5 / M13 / M14 | BLOCKED (unchanged) |
| `mcf.metric_contract` / `mcf.metric_contract_version` | 0 (unchanged) |
| Calibration follow-up | TRANSITIONS from "investigation scope only" to "decision α LOCKED + fix arc SCOPED" — closure remains conditional on the arc completing per §7 of the follow-up |
| Legacy `POST /api/metric-catalog/definitions` | OPEN (unchanged); Sunset header behavior unchanged |
| `metric.metric_definition` writes | continue to work via legacy POST during the calibration window |

### 8.3 Post-arc (after PR-E2 if APPROVE_FOR_DRAFT)

| Item | State |
|---|---|
| F1–F5 | IMPLEMENTED and PROVEN |
| F9 | DISCHARGED |
| Calibration follow-up | CLOSED (status `implemented`) |
| Operator authorization for M12.5 next-gate DBCP (PR-G3) | UNBLOCKED |
| `mcf.metric_contract` | Still 0 UNTIL PR-G3 authorizes M12.5 and an operator-authorized M12.5 invocation occurs |
| M12 panel framework | Approval-capable; can produce APPROVE_FOR_DRAFT / OPERATOR_REVIEW / REJECT_DEFECT based on real LLM consensus over real BCF/evidence grounding |
| MCF architecture stance | OPERATIONALLY TRUE (was: aspirationally true while adapters were scaffolding) |

## 9. Hard-rule mapping + non-execution confirmation

### 9.1 Hard-rule mapping

| Rule | Application here |
|---|---|
| **HR1 (real vendor calls only)** | This DBCP authors no code and invokes no vendor APIs. Future PR-C2 maintains HR1 — adapter rewrites continue to call real provider SDKs; the existing provenance-keys contract from PR #28 §11.4 survives unchanged. |
| **HR2 (writer reached via orchestrator outer tx)** | Unchanged; future PR-C2 + PR-C3 do not touch the writer path. |
| **HR3 (no `contract.*` writes)** | Unchanged; A4 freeze preserved throughout the arc. |
| **HR4 (no tenant DB touch)** | Unchanged; F4 production `PanelToolSurface` reads from PLATFORM `concept_registry.*` and `mcf.metric_contract` only. F4's `source_reality.summarize` reads from tenant-side reader OUTPUT (already in platform-side substrate), not the tenant DB directly. PR-C1 unit tests + integration tests enforce. |
| **HR5 (production COMMIT path)** | Unchanged; future PR-E2 runs under the production COMMIT path per the M12 orchestrator. |
| **DEC-7f9597 / D423 (operator authorization per gate)** | Applied to every PR in §6 — this DBCP authorizes the calibration arc as a whole; each subordinate PR carries its own operator authorization (PR-C1 / PR-C2 / PR-C3 on the PR description per standard bc-core review; PR-G2 + PR-G3 as separate operator-authorized DBCPs; PR-E1 + PR-E2 as evidence-capture PRs gated by their preceding authorization DBCPs). |
| **DEC-ebf0b4 / D268 (session discipline; one-then-many; prove before scaling)** | The calibration arc IS the application of D268 to the first-real-M12 outcome. PR-E2 is the "prove ONE before scaling" gate that precedes any refined-candidate retry. The arc deliberately reuses the same candidate (`overdue_invoice_count`) to isolate framework effects from candidate effects per the D268 discipline. |

### 9.2 Explicit non-execution confirmation

| Item | Status |
|---|---|
| M12 rerun | ❌ NOT EXECUTED |
| `runPanel()` invocation | ❌ NONE |
| Standalone writer invocation | ❌ NONE |
| Provider API calls (Anthropic / OpenAI / Google) | ❌ NONE |
| M12.5 / M13 / M14 invocation | ❌ NONE |
| Metric contract created | ❌ `mcf.metric_contract` Δ = 0, `mcf.metric_contract_version` Δ = 0 |
| Rollback | ❌ NONE |
| Tenant DB touch | ❌ NONE — read-only `pg_query` against `bc_platform_dev` for substrate re-verification only |
| Substrate mutation | ❌ NONE |
| bc-core code change | ❌ NONE — bc-core stays at `16cf3781` |
| bc-docs-v3 docs change | ✅ This PR authors one new doc; no existing docs modified |
| New M11 intake row | ❌ NOT AUTHORED here — PR-E1 forward-looking |
| Fresh first-real-M12 authorization (PR-G2) | ❌ NOT AUTHORED here — forward-looking |
| M12.5 next-gate DBCP (PR-G3) | ❌ NOT AUTHORED here; conditional on PR-E2 outcome |
| Refined-candidate retry commitment | ❌ NONE — explicitly deferred behind F9 + PR-E2 |
| Supersession of DEC-c3e57f / D422 | ❌ NONE — decision α preserves the existing MCF architecture |
| Lowering of M12 scope to advisory | ❌ NONE — γ explicitly rejected |
| MCF architecture revision | ❌ NONE — MCF still owns the full MC lifecycle |
| Out-of-scope work (M16 / M17 / M18 migration) | ❌ NONE — those gates separately governed |

## 10. References

- `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` — M12 design (verdict semantics, consensus contract, tool surface)
- `docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` — M12.5 design (APPROVE_FOR_DRAFT precondition, `markConsumedByPanel` ownership)
- `docs/implementation/metric-context-framework-m12-deferred-prereqs-dbcp.md` (PR #28; bc-docs-v3 main `55bc4759`) — provenance-only adapter scope that the current adapters correctly satisfy
- `docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md` (PR #29; bc-docs-v3 main `a18d6e3c`) — single-use authorization (CONSUMED)
- `docs/implementation/metric-context-framework-m12-first-real-run-disposition.md` (PR #31; bc-docs-v3 main `42f74fc9`) — operator's terminal disposition of `panel_run 9a462e6c-...`
- `docs/implementation/metric-context-framework-m12-panel-framework-calibration-followup.md` (PR #31) — 7-thread investigation scope that this DBCP closes by locking decision α
- `docs/errata/MCF-ERR-001.md` (PR #30; bc-docs-v3 main `3926d021`) — verdict-to-intake-status correction
- `docs/operating-model/mcf-legacy-bridge.md` — MCF coexistence window during the calibration arc
- `docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) — MCF bridge ADR, preserved by decision α
- `docs/adrs/ADR-7f9597.md` (DEC-7f9597 / D423) — operator authorization stance
- `docs/adrs/ADR-ebf0b4.md` (DEC-ebf0b4 / D268) — session discipline; "one-then-many"
- bc-core PR #168 merge `16cf3781` — first-real-M12 execution evidence
- bc-core PR #167 merge `0e5e501d` — first real M11 intake evidence
- bc-core PR #161 merge `a0fee4e9` — M12 panel service / orchestrator O1 Adapter
- bc-core PR #164 merge `4298e0a8` + PR #166 merge `a48d429a` — vendor adapter wiring (provenance-only per PR #28)
- bc-core `src/registry/mcf/panel-agents/{anthropic,openai,google}-agent.adapter.ts` — current adapter implementations (provenance-only scaffolding)
- bc-core `src/registry/mcf/prompts/m12-panel-{maker,checker,moderator}.v1.md` — role prompt files currently unused by code
- bc-core `src/registry/mcf/panel-consensus.ts` — consensus algorithm
- bc-core `src/registry/mcf/panel-grounding-check.ts` — grounding-check algorithm
- bc-core `src/registry/mcf/panel-payload.types.ts` — `TranscriptPayloadV1` + `ConsensusPayloadV1` shapes
- bc-core `src/registry/mcf/panel-payload.schema.json` — schema source for F2 structured-output
- bc-core `src/registry/mcf/panel-tool-surface.types.ts` — `PanelToolSurface` interface (10 tools)
- bc-core `src/registry/mcf/metric-authoring-panel.service.ts:259-266` — consensus + grounding invocation site
- bc-core `src/registry/mcf/metric-authoring-materialization.service.ts:364-368` — M12.5 `APPROVE_FOR_DRAFT` precondition
- bc-core `scripts/mcf-m12-first-real-run.mjs:500-516` — current empty-stub tool surface
