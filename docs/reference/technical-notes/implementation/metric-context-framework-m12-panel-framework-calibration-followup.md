---
uid: metric-context-framework-m12-panel-framework-calibration-followup
title: MCF M12 — Panel-Framework Calibration Follow-Up (investigation scope; tag mcf-framework-calibration)
description: Investigation scope for the panel-framework calibration follow-up arising from the first real M12 panel run (`panel_run_uid 9a462e6c-ce41-4ecb-aa51-cbac6c2b3990`, intake `4d849778-3989-4caf-8a71-7d44b782d98e`). Read-only transcript inspection of all three vendor roles (`anthropic / claude-haiku-4-5`, `openai / gpt-4o-mini`, `google / gemini-flash-latest`) revealed a systematic mismatch: all three roles produced approving narrative reasoning in their `reasoning_trace` but each returned `verdict_code = OPERATOR_REVIEW` in the structured output, with zero `tool_calls` and zero `claims` across all roles, and a vacuously-passing `grounding_check_passed: true`. The consensus algorithm correctly aggregated three OPERATOR_REVIEW tokens into consensus OPERATOR_REVIEW with `operator_review_reason = mixed_verdicts` (algorithmic catchall — actually all three agreed). This document scopes the investigation: prompt clarity for the structured verdict token; tool-use prompting; the execution-script tool-surface stub vs. a real BCF/evidence tool surface; Moderator output-token budgeting (`finish_reason: length`); the `operator_review_reason` label set; and what code/docs changes are required before any refined-candidate retry. **NOT EXECUTED** — investigation scope only. No code changes, no DB changes, no provider calls, no `runPanel()`, no M12.5 / M13 / M14, no metric contract, no rollback, no tenant DB, no substrate mutation. Status `proposed`; closes when the recommended code/docs changes have landed and a verification gate is defined.
status: proposed
date: 2026-05-30
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-framework-calibration
supersedes:
superseded_by:
---

# MCF M12 — Panel-Framework Calibration Follow-Up

> **Tag**: `mcf-framework-calibration`. Filed as bc-docs follow-up arising from `metric-context-framework-m12-first-real-run-disposition.md`. This is investigation scope, not a fix. The fix shape will be authored as one or more separately operator-authorized DBCPs / PRs once the investigation closes.

## 1. Scope

### 1.1 Question this doc answers

> The first real M12 panel run executed end-to-end with three real vendor providers and produced consensus verdict `OPERATOR_REVIEW`. Read-only transcript inspection revealed that all three vendors' narrative reasoning was approving, yet all three returned `verdict_code = OPERATOR_REVIEW` in their structured output, with zero `tool_calls` and zero `claims`. What does the panel framework need to investigate and likely change before any refined-candidate retry can plausibly reach `APPROVE_FOR_DRAFT`?

### 1.2 In scope

- The structured-output protocol for the M12 panel role outputs (`verdict_code`, `claims`, `tool_calls`, `reasoning_trace`, `defect_code`, `status_code`)
- The role prompts that drive the three panel agents (`anthropic-agent.adapter.ts`, `openai-agent.adapter.ts`, `google-agent.adapter.ts`)
- The `PanelToolSurface` runtime contract — 10 tool methods covering BCF read / evidence search / source-reality summarization / KPI catalog intent / MC identity probe
- The first-real-M12 execution script's minimal tool-surface stub (`scripts/mcf-m12-first-real-run.mjs` `makeMinimalToolSurfaceStub()`, lines 459-476 at bc-core merge `16cf3781`) and its interaction with the role prompts
- The Moderator's output-token budget and the `finish_reason: length` truncation observed in `panel_run 9a462e6c-...`
- The `operator_review_reason` label set in the M12 consensus algorithm — specifically the `mixed_verdicts` catchall semantics
- The consensus algorithm's behavior when all three roles return OPERATOR_REVIEW
- Whether the consensus payload's `candidate_proposal: {}` empty-object outcome under OPERATOR_REVIEW is correct or a missing-data symptom
- The boundary between "investigation outcome documented" and "code changes shipped" — the gating contract for any future M12 retry

### 1.3 Explicit non-scope

- ❌ No bc-core code change is performed by this document
- ❌ No fix is committed by this document; the investigation outcome will be authored as a separately operator-authorized DBCP / PR set
- ❌ No new M12 panel run authorization is granted by this document
- ❌ No refined-candidate retry is authored; refined-candidate retry is explicitly deferred behind the closure of this follow-up
- ❌ No M12.5 / M13 / M14 invocation
- ❌ No metric contract creation
- ❌ No rollback
- ❌ No tenant DB touch
- ❌ No substrate mutation
- ❌ No provider API calls
- ❌ No amendment to PR #29 DBCP (separately governed per MCF-ERR-001 `target_resolution`)
- ❌ No commitment to retry with the same candidate (`overdue_invoice_count`) vs a different candidate — that choice belongs to the post-investigation DBCP

## 2. Authority anchors

| Anchor | Reference |
|---|---|
| Disposition record | `docs/implementation/metric-context-framework-m12-first-real-run-disposition.md` (this PR) |
| First-real-M12 execution evidence | bc-core PR #168 merge `16cf3781` |
| MCF-ERR-001 (governs PR #29 verdict-to-intake-status correction) | `docs/errata/MCF-ERR-001.md` |
| M12 authoring panel DBCP | `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` |
| M12 panel service | bc-core `src/registry/mcf/metric-authoring-panel.service.ts` (PR #161 merge `a0fee4e9`) |
| M12 panel-agent adapters | bc-core `src/registry/mcf/panel-agents/{anthropic,openai,google}-agent.adapter.ts` (PR #164 `4298e0a8` + PR #166 `a48d429a`) |
| First-real-M12 execution script | bc-core `scripts/mcf-m12-first-real-run.mjs` (PR #168 merge `16cf3781`) |
| Session discipline | ADR DEC-ebf0b4 / D268 (one-then-many; independent verification; no shortcuts) |

## 3. Observed framework behavior (read-only evidence)

### 3.1 Per-role structured output (from `mcf.metric_authoring_panel_transcript` for `panel_run 9a462e6c-...`)

| Role | Vendor / Model | `verdict_code` | `defect_code` | `claim_count` | `tool_call_count` | `status_code` | Other |
|---|---|---|---|---|---|---|---|
| Maker | `anthropic / claude-haiku-4-5-20251001` | `OPERATOR_REVIEW` | null | 0 | 0 | `completed_with_verdict` | `finish_reason: stop`; 205 in / 200 out / 405 total tokens |
| Checker | `openai / gpt-4o-mini-2024-07-18` | `OPERATOR_REVIEW` | null | 0 | 0 | `completed_with_verdict` | `finish_reason: stop`; 170 in / 107 out / 277 total tokens |
| Moderator | `google / gemini-flash-latest` | `OPERATOR_REVIEW` | null | 0 | 0 | `completed_with_verdict` | **`finish_reason: length`**; 185 in / 136 out / **1205 total tokens** — truncated mid-sentence |

### 3.2 Per-role narrative reasoning (`reasoning_trace` excerpts; verbatim)

- **Maker**: *"As maker, I assess `overdue_invoice_count` as **technically sound and operationally ready for M12 intake**. The metric exhibits clear grain (invoice), well-defined filter logic (due_date < as_of_date AND payment_status NOT IN {paid, cancelled}), deterministic point-in-time semantics, and direct relevance to standard AR workflows—satisfying baseline authoring rigor. However, I flag two vendor-coordination items for the panel: (1) confirmation that payment_status cardinality and paid/cancelled definitions align across the three vendor systems, and (2) explicit handling of timezone and as_of_date interpretation to prevent cross-vendor aggregation drift. Conditional recommendation: **approve for D8 condition 7 evidence run** with vendor homologation on status enums and temporal anchoring completed prior to production handoff."*
- **Checker**: *"The candidate metric `overdue_invoice_count` is well-defined and aligns with standard accounting practices for managing accounts receivable. It accurately captures the count of invoices past their payment due date and unpaid as of a specific date, adhering to the necessary conditions for inclusion. The metric's calculation at the invoice grain and its use of a point-in-time approach ensures clarity and relevance for B2B finance teams monitoring their collection pipeline. Overall, it meets the requirements outlined in the operator context and **appears suitable for the first-real M12 evidence run**."*
- **Moderator**: *"As Moderator of the M12 metric authoring panel, I find the candidate `overdue_invoice_count` to be a **fundamentally sound, highly standardized utility** essential for B2B accounts receivable workflows. The proposed point-in-time logic—counting at the invoice grain where `due_date < as_of_date` and excluding `paid` or `cancelled` states—**aligns cleanly with M12 behavioral expectations and satisfies the D8 condition 7 requirements under PR #29 §4**. To ensure seamless tripartite vendor implementation, our primary focus during this review must be verifying that the `payment_status` ENUMs map consistently across all three"* — truncated.

### 3.3 Consensus payload (from `mcf.metric_authoring_panel_run.consensus_payload_json`)

```
verdict_code:              OPERATOR_REVIEW
defect_code:               null
operator_review_reason:    mixed_verdicts
grounding_check_passed:    true   (vacuous — zero claims)
grounding_violations:      []
candidate_proposal:        {}
prompt_version:            m12-panel-v1
panel_algorithm_version:   mcf-panel-v1
per_role_summary:          all three roles report verdict OPERATOR_REVIEW with claim_count 0 and tool_call_count 0
```

### 3.4 Tool-surface context

- The first-real-M12 execution script (`scripts/mcf-m12-first-real-run.mjs`) wires `makeMinimalToolSurfaceStub()` as the `PanelToolSurface` (lines 459-476). All 10 tool methods (`bcf.search_entity`, `bcf.search_business_concept`, `bcf.read_entity`, `bcf.read_business_concept`, `bcf.reachability_check`, `evidence.search`, `evidence.retrieve`, `source_reality.summarize`, `kpi_catalog.read_intent`, `mc.identity_probe`) return empty payloads.
- The three vendors made **zero** tool calls during the run. Whether they would have made tool calls if the surface were richer is **not known** from this evidence alone — they may not have been prompted to.

## 4. Investigation questions (seven threads)

### 4.1 Q1 — Why did each vendor's structured `verdict_code` return `OPERATOR_REVIEW` while their prose was approving?

- Is the role prompt explicit about when to set `APPROVE_FOR_DRAFT` vs `OPERATOR_REVIEW`?
- Is "conditional approval" (e.g., Maker's "approve for D8 condition 7 evidence run with vendor homologation on status enums and temporal anchoring") supposed to be `APPROVE_FOR_DRAFT` or `OPERATOR_REVIEW`?
- Does the prompt clarify that flagged-but-non-blocking concerns should still allow `APPROVE_FOR_DRAFT` (with caveats noted in `reasoning_trace`)?
- Are the JSON schemas given to each vendor for structured-output enforcement consistent across the three adapters, or do they differ in ways that bias the verdict?
- Could each vendor be defaulting to OPERATOR_REVIEW as a conservative "uncertain" fallback when uncertain about structured-output expectations?

### 4.2 Q2 — Why were `claim_count` and `tool_call_count` both zero across all three roles?

- Does the role prompt explicitly instruct the vendor to make `claims` (with backing tool_call references) before reaching a verdict?
- Is there a worked example in the prompt showing the claim → tool_call → grounded-claim flow?
- Is the tool-surface schema discoverable to the vendor (do the prompts enumerate the 10 PanelToolSurface methods and their signatures)?
- Could the empty-stub tool surface have been observed by vendors as "no useful tools available" and they declined to call any?
- Does the consensus algorithm have a code path that warns / penalizes / re-prompts when `claim_count == 0`? Should it?

### 4.3 Q3 — Is the first-real-M12 execution script's `makeMinimalToolSurfaceStub()` appropriate for any future approval-targeting attempt?

- The stub returns empty payloads for all 10 tool methods. This is correct for an evidence-capture-only first-real-M12 run that intentionally constrains scope to provenance proof.
- For any future M12 attempt that *targets* `APPROVE_FOR_DRAFT`, this stub is structurally inappropriate: vendors cannot ground claims against BCF if the BCF tools return empty payloads.
- Recommendation to validate: the next M12 attempt that targets APPROVE_FOR_DRAFT MUST wire a **real `PanelToolSurface` implementation** that reads from `concept_registry.*` (BCF) and the BCF-side evidence sources, not the empty stub. The empty stub should remain available for evidence-only runs (e.g., regression / smoke / provenance-recapture).
- Investigation should confirm whether bc-core has a production `PanelToolSurface` implementation today, and if not, scope its construction.

### 4.4 Q4 — Moderator output-token truncation (`finish_reason: length`)

- Moderator (`gemini-flash-latest`) hit `finish_reason: length` at 1205 total tokens, truncated mid-sentence ("`payment_status` ENUMs map consistently across all three" — sentence incomplete).
- Investigation: what is the Moderator's max-output-tokens budget in `model-defaults.ts` and the Google adapter? Is it set, or is it relying on Gemini's default?
- Even if the Moderator had been heading to `APPROVE_FOR_DRAFT`, the verdict token was not emitted before the truncation cut in.
- Recommendation to validate: max-output-tokens should be set sufficiently high (e.g., 2000-4000) to accommodate the full reasoning_trace + verdict + structured output, with a per-role budget reflecting the role's expected output complexity (Moderator's synthesis may need more tokens than Maker's initial proposal).

### 4.5 Q5 — Is `operator_review_reason = mixed_verdicts` the right label for all-three-OPERATOR_REVIEW?

- The M12 DBCP consensus algorithm (Step 6 / §5) defines the `operator_review_reason` label set: `{mixed_verdicts, grounding_check_failed, partial_transcripts, vendor_timeout, vendor_outage, cost_ceiling_exceeded, workspace_fingerprint_mismatch}`.
- The current implementation routes "not all-APPROVE and not all-REJECT" → `mixed_verdicts`. For this run all three roles agreed on OPERATOR_REVIEW; the label is technically the catchall but reads as misleading.
- Investigation: should the label set add `all_operator_review` (or similar) to distinguish unanimous-OPERATOR_REVIEW from genuinely mixed verdicts? Or should `mixed_verdicts` be renamed to `not_unanimous_approve_or_reject` to better describe what it actually means?
- This is a label-clarity question, not a behavior question. The consensus outcome is correct under either label; only the diagnostic readout improves.

### 4.6 Q6 — Should the consensus algorithm penalize `claim_count == 0` outcomes?

- A panel run where all three vendors produce zero claims has a vacuous `grounding_check_passed: true` — the grounding gate is unable to fail because there is nothing to ground.
- This represents a framework-failure mode (vendors did not formalize their reasoning into structured claims) rather than a correct OPERATOR_REVIEW.
- Investigation: should the consensus algorithm have a "minimum claim count" gate that flips the verdict to a distinct failure category when `claim_count == 0 AND verdict_code == APPROVE_FOR_DRAFT` (would have been the dangerous case — approve without evidence)? Should it warn when `claim_count == 0 AND verdict_code == OPERATOR_REVIEW` (the current case — punt without evidence)?
- A potential framework guard: `if SUM(per_role.claim_count) == 0 then operator_review_reason = 'panel_did_not_produce_claims' regardless of underlying verdict pattern` — surfaces the framework failure for what it is.

### 4.7 Q7 — What is the gating contract for any future M12 retry?

- The disposition (`metric-context-framework-m12-first-real-run-disposition.md` §4.5) defers any refined-candidate retry behind the closure of this follow-up.
- Investigation: what minimum set of code/docs changes must land before the operator authorizes the next M12 attempt? Candidate gating items:
  - (a) Role prompts updated to explicitly clarify APPROVE_FOR_DRAFT vs OPERATOR_REVIEW conditions
  - (b) Role prompts include the structured-output JSON schema with examples of well-formed `claims` and `tool_calls`
  - (c) Real `PanelToolSurface` implementation (BCF read + evidence search) replacing the empty stub for approval-targeting runs
  - (d) Moderator max-output-tokens raised + verified non-truncating on a representative prompt
  - (e) `operator_review_reason` label set extended or relabeled per Q5
  - (f) Consensus algorithm `claim_count == 0` guard per Q6
  - (g) An evidence-capture rerun of the same candidate (`overdue_invoice_count`) under the calibrated framework BEFORE any refined-candidate retry, to isolate framework-change effects from candidate-change effects
- The gating contract proposal goes into the follow-up's closeout DBCP; this document does not lock it.

## 5. Recommended next steps

| Step | Owner | Output |
|---|---|---|
| **5.1** Read `bc-core/src/registry/mcf/panel-agents/{anthropic,openai,google}-agent.adapter.ts` to inventory the actual role prompts, structured-output schemas, and model defaults at PR #166 `a48d429a`. | Investigator | A bc-docs read-only findings note documenting the prompt contents and structured-output schema, anchored to a SHA. |
| **5.2** Read `bc-core/src/registry/mcf/metric-authoring-panel.service.ts` Step 6 (consensus algorithm) and `panel-consensus.ts` to inventory the exact `operator_review_reason` routing logic. | Investigator | Same findings note as 5.1; consensus-logic section. |
| **5.3** Inventory whether a production `PanelToolSurface` exists in bc-core today (search for implementations other than the empty stub). | Investigator | Same findings note; tool-surface section. |
| **5.4** Synthesize the seven Q1-Q7 threads against the inventory in 5.1-5.3 and propose a calibration DBCP (or a small ADR proposing the calibration scope). | Investigator | A new bc-docs PR proposing the calibration DBCP / ADR. |
| **5.5** Operator decides the calibration scope and authorizes any subordinate bc-core code-change PRs. | Operator | Operator-authorized DBCP per the BareCount DBCP pattern. |
| **5.6** Subordinate bc-core PRs implement the calibration. | Implementer | Merged bc-core PRs with the framework changes. |
| **5.7** Evidence-capture rerun (same candidate, calibrated framework) — isolates framework effects from candidate effects. | Implementer | bc-core PR documenting the evidence-capture rerun outcome. |
| **5.8** Decide whether to proceed with refined-candidate retry, retry the same candidate, or accept the framework as sufficient for steady-state. | Operator | Decision recorded; this follow-up closes at this point. |

## 6. Hard rule compliance

- **HR1-HR5 + DEC-7f9597** — this investigation document neither invokes M-series services nor touches substrate. The hard rules apply trivially.
- **DEC-ebf0b4 / D268 (session discipline)** — this investigation IS the "one-then-many" rule's natural next step: one M12 run was proven; the rule says inspect-before-scaling. Refined-candidate retry is deferred behind this investigation.

## 7. Closure criteria

This follow-up closes when:

1. The findings note (Step 5.1-5.3) is authored and merged to bc-docs main
2. The calibration DBCP or ADR (Step 5.4) is authored, operator-approved, and merged
3. The subordinate bc-core code-change PRs (Step 5.6) are merged
4. The evidence-capture rerun (Step 5.7) is authored and merged with documented results
5. The operator records the disposition decision for any next M12 attempt (Step 5.8)

At closure, this document's `status` flips from `proposed` to `implemented` and the follow-up is retained as a historical record of how the framework was calibrated between the first-real-M12 run and the first successful APPROVE_FOR_DRAFT.

## 8. References

- `docs/implementation/metric-context-framework-m12-first-real-run-disposition.md` (this PR) — operator disposition of `panel_run 9a462e6c-...`
- `docs/implementation/metric-context-framework-m12-authoring-panel-dbcp.md` — M12 panel design + consensus algorithm
- `docs/implementation/metric-context-framework-m12-first-real-run-authorization-dbcp.md` (PR #29) — first-real-M12 authorization
- `docs/errata/MCF-ERR-001.md` (PR #30) — verdict-to-intake-status correction
- bc-core PR #168 merge `16cf3781` — first-real-M12 execution evidence
- bc-core PR #167 merge `0e5e501d` — first real M11 intake row evidence
- bc-core PR #164 merge `4298e0a8` + PR #166 merge `a48d429a` — vendor adapter wiring
- bc-core PR #161 merge `a0fee4e9` — M12 panel service / orchestrator O1 Adapter
- bc-core `src/registry/mcf/panel-agents/{anthropic,openai,google}-agent.adapter.ts`
- bc-core `src/registry/mcf/metric-authoring-panel.service.ts`
- bc-core `scripts/mcf-m12-first-real-run.mjs`
