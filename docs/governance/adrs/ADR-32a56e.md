---
uid: DEC-32a56e
title: "MCF M12 Context Judge — semantic grounding via LLM, not regex"
description: "Replace regex/substring semantic grounding in the M12 panel with a context-judge LLM call that evaluates Maker APPROVE claims per-claim against cited tool evidence. Rules at deterministic boundaries only. Vendor-pluggable; v1 uses an already-configured reliable vendor. Four-phase migration; no big-bang."
status: decided
date: 2026-06-01T02:44:12.995Z
project: platform
domain: metrics
subdomain: mcf-m12-grounding
focus: architecture
---

# MCF M12 Context Judge — semantic grounding via LLM, not regex

## Context

2026-06-01 audit established that rules are valid at deterministic system boundaries but cannot pretend to be semantic judges. The existing panel-grounding-check.ts mixes the two: structural ID resolution (boundary, stays) with semantic substring/token overlap (judgment, moves to LLM). Panel run 4702aed7 demonstrated the failure mode — orchestrator returned grounding_violations=[] while the AI Checker independently identified Maker's claim_3 citing the wrong reachability tool. The rule-based platform validation was weaker than the AI verification it was supposed to gate. Context judge restores the framework's "AI panel works on context" intent without throwing away the legitimate rule surfaces (schema, F6 empty-claims, defect registry, materialization eligibility). v1 ships Maker-APPROVE-only to make the first metric path possible without quadrupling vendor cost.

## 1. Principle

```
Rules are valid at deterministic system boundaries.
Rules are not valid as semantic judges.
Semantic grounding must be evaluated from context.
```

This is the governing rule for the M12 metric authoring panel and for the framework as a whole. It does not get its own ADR; it lives at the top of this one and applies wherever an MCF subsystem decides between a rule and an AI judgment.

## 2. What stays deterministic in MCF

Boundary gates that decide structural questions remain rule-based:

- **Schema shape gates** (`panel-payload.schema.json` + AJV validation) — does the persisted payload have the expected fields and types?
- **Auth / role gates** (Cognito JWT + role catalog) — is the caller permitted to invoke the surface?
- **3-vendor distinctness** (`metric-authoring-panel.service.ts: assertDistinctVendors`) — does the panel construction use three distinct vendors as required?
- **No-empty-claims-on-APPROVE guard** (`panel-consensus.ts` F6 fail-closed) — if a role emitted APPROVE_FOR_DRAFT, did it also emit at least one claim? Empty claims with APPROVE downgrade to OPERATOR_REVIEW.
- **Defect-code registry membership** (`MCF_DEFECT_REGISTRY_V1` + `assertMcDefectCode` + parser coercion) — is the emitted defect_code in the closed registry? Unknown values coerce to OPERATOR_REVIEW with a structured `ParserWarning`.
- **Materialization eligibility checks** (M12.5 readiness) — structural checks before materialization: schema valid, claims non-empty on APPROVE, no `parser_warnings` requiring operator review, and (after this ADR) judge says all Maker APPROVE claims grounded.
- **Tool-surface read/write boundaries** (`ProductionPanelToolSurface`) — which 10 tools are exposed; only `RegistryReadService` / evidence allowlist queries; no writes; no raw SQL.

None of these claim to interpret the meaning of a claim. They check structure, identity, membership, presence.

## 3. What the context judge replaces

The current `panel-grounding-check.ts` mixes two responsibilities, only one of which is its job:

- **Structural**: "does this claim's `supporting_tool_call_ids` resolve to real tool calls in the role's `tool_calls` array?" — this is a boundary check and stays as a structural ref-existence test.
- **Semantic**: "do the cited tool responses actually contain evidence for the claim text?" — this is a meaning judgment and must move out of regex/substring code.

Specifically, the judge replaces:

- **Regex / positional alias grounding** (`panel-grounding-check.ts: resolveToolCallReference`) — `(call|tool_call|tc|tool_code|tool)_(\d+)$` and friends. The judge reads the claim and decides which cited evidence actually supports it; format mismatches are not part of meaning.
- **Multi-token substring grounding** (`panel-grounding-check.ts: validateLoosePath`) — three distinct 5+ char tokens appearing in the same tool response is statistical text overlap, not semantic support.
- **Prompt instructions that teach models platform alias mechanics** — Checker / Moderator prompts no longer carry explanations of how positional or name+ord aliasing works. The judge handles resolution; the panel reasons from context.

## 4. Judge responsibility

For each claim the judge evaluates, it answers four questions in order:

1. **What fact does the claim assert?** — read `claim_text`, identify the substantive assertion (e.g. *"Customer Invoice owns the due_date concept"*, *"the document_number concept supports COUNT DISTINCT"*).
2. **Which tool call(s) are cited?** — read `supporting_tool_call_ids`; resolve them against the role's `tool_calls` array in context, not via regex.
3. **What did those tool calls actually establish?** — read the cited tool's `request_json` + `response_json`. What does the evidence demonstrate?
4. **Does the evidence support the claim?** — does the cited response substantively demonstrate the fact in (1)? If not, name the gap.

The judge does NOT decide consensus. It does NOT classify defect codes. It does NOT re-derive the proposal. Per-claim grounded / not-grounded only.

## 5. Minimal first implementation

The judge ships in v1 evaluating Maker `APPROVE_FOR_DRAFT` claims only.

- **Why Maker only**: the materialization path runs from Maker's `proposal_payload`. If Maker's claims are not grounded, materialization cannot proceed regardless of Checker / Moderator state. Getting Maker grounding right is the first metric blocker.
- **Why APPROVE only**: OPERATOR_REVIEW and REJECT_DEFECT verdicts route to operators by definition. Judging their claims later is useful for inspector context, not gating.
- **Why not all roles in v1**: scope. Three-role judging triples or quadruples vendor cost and adds latency before we know the judge is delivering value.
- **Out of scope for this ADR**: no M12.5 / M13 / M14 changes. The materialization preflight call site that consumes the judge result is described here so reviewers see what gates change, but the code path is updated in the implementation PR, not in this ADR.

## 6. Judge interface

Input:

```ts
{
  role: 'maker';                          // v1 — maker only
  claim_text: string;                     // the claim's text
  cited_tool_call_ids: string[];          // model-emitted, any format
  tool_calls: Array<{                     // canonical, full role tool_calls
    tool_call_id: string;
    tool_code: string;
    request_json: Record<string, unknown>;
    response_json: Record<string, unknown>;
    error: { code: string; message: string } | null;
  }>;
  proposal_payload?: Record<string, unknown>;  // optional excerpt for context
}
```

Output:

```ts
{
  grounded: boolean;
  resolved_tool_call_ids: string[];       // judge's resolution of cited ids
  reasoning_text: string;                 // one paragraph, judge's read
  unsupported_reason_code:
    | null
    | 'no_cited_evidence'
    | 'cited_evidence_unrelated'
    | 'cited_evidence_contradicts'
    | 'judge_uncertain';
  correction_suggestion: string | null;   // if grounded=false, what would close the gap
}
```

The judge is a pure read; it never writes to BCF, evidence, or contract substrate.

## 7. Vendor binding

Vendor-pluggable. The judge is one more LLM call — its vendor binding is configuration, not architecture.

- **v1 may use an already-configured reliable vendor** (one of Anthropic / OpenAI / Google already wired for Maker / Checker / Moderator).
- **A fourth independent vendor is a future hardening option**, not a v1 requirement.

Tradeoff comparison for v1:

| Option | Pro | Con |
|---|---|---|
| Same vendor as Moderator (Anthropic Opus) | Lowest config delta; high quality; same context-window patterns we've already calibrated | Binds judge availability to Moderator availability |
| Cheapest reliable configured vendor (e.g. Gemini Flash) | Lowest cost; fast | Risk: reasoning depth on tight claim/evidence semantic comparisons |
| Dedicated fourth vendor (later) | Vendor-independent from the panel roster | Appropriate for production hardening, not v1; postpone until we see judge behavior in real runs |

The v1 vendor decision is an implementation detail; this ADR does not lock it. The implementation PR records the chosen vendor with rationale.

## 8. Failure semantics

The judge has four ways to fail to ground a claim. All four route to OPERATOR_REVIEW:

- **Judge timeout** → claim treated as ungrounded; consensus emits `operator_review_reason = 'judge_unavailable'`.
- **Malformed judge output** → ungrounded; reason `judge_unavailable`.
- **Judge vendor failure** → ungrounded; reason `judge_unavailable`.
- **Judge uncertainty** (`unsupported_reason_code = 'judge_uncertain'`) → ungrounded; reason `judge_uncertain`.

Invariant — the materialization-safety guarantee:

> **Never allow APPROVE_FOR_DRAFT when the judge has not successfully grounded all Maker APPROVE claims.**

If the judge can't decide, the answer is operator review, not silent approval.

## 9. Persistence / evidence

Per-claim judge results persist alongside the role transcripts. Schema sketch:

```
mcf.metric_authoring_grounding_judge_result
  panel_run_uid               UUID         FK → mcf.metric_authoring_panel_run
  role                        text         'maker' in v1
  claim_id                    text         the claim's id within the role's claims array
  grounded                    boolean
  resolved_tool_call_ids      jsonb        array of tool_call_id strings
  reasoning_text              text
  unsupported_reason_code     text         nullable; closed enum
  correction_suggestion       text         nullable
  judge_model_identity        jsonb        vendor / model_id / version / latency_ms
  computed_at                 timestamptz
```

Visibility:

- **M12.5 materialization preflight** queries this table; materialization is blocked if any Maker APPROVE claim has `grounded = false`.
- **Inspector / Catalog UI** surfaces the judge's reasoning per claim, so operators reviewing OPERATOR_REVIEW outcomes see exactly which claims failed grounding and why.

The exact column shape is an implementation choice; the structural requirement is: per-claim, with reasoning, queryable from materialization preflight.

## 10. Prompt cleanup implications

When the judge ships, the following prompt content goes away (in the same PR or the immediately-following PR):

- **Alias-resolution mechanics sections** in `m12-panel-checker.v1.md` and `m12-panel-moderator.v1.md` — these only existed because the regex resolver leaked through. With the judge owning resolution-in-context, the panel doesn't need to know.
- **Convergence truth tables** (*"if X / Y / Z then APPROVE_FOR_DRAFT"*) in Checker and Moderator prompts — convergence emerges from honest reasoning over context, not from prompt-encoded rules.

What stays:

- Role intent and responsibilities (Maker proposes; Checker independently verifies; Moderator computes consensus over peers).
- Context responsibilities (use the tool surface; cite tool calls in claims; restate-the-intake belongs in `proposal_payload`, not `claims`).
- Boundary constraints (closed defect taxonomy, no fabrication, no name binding, the closed tool set).

## 11. Migration plan

Four phases. No big-bang.

- **Phase 1 (this ADR)** — design lock. No code changes. PR opens; review; merge to mark `decided`.
- **Phase 2 (implementation)** — implement the judge alongside the existing grounding check. Both run on every panel call. Judge result persists. Consensus continues to consume the existing grounding check; the judge runs as observation. Calibrate against the existing check's pass/fail pattern. Monitor: where does the judge disagree with the substring check, and which is correct?
- **Phase 3 (gate switch)** — M12.5 materialization preflight starts trusting the judge result instead of the regex grounding check. Consensus computation moves to the judge. The regex check stays in code as a diagnostic / fallback observation, not a gating signal.
- **Phase 4 (cleanup)** — delete `panel-grounding-check.ts` substring logic and positional alias regex. Keep only the structural ref-existence test ("does the cited id exist as a `tool_call_id` at all?" — this is structural, not semantic). Remove the Checker / Moderator alias-resolution prompt sections and convergence truth tables (per §10) at this phase if not already removed earlier.

Each phase ships as its own PR with end-to-end run evidence.

## 12. Open questions

Tracked here so the implementation PR can close them:

- **Exact judge prompt**: prompt design is an implementation question. Skeleton: *"Read the claim, the cited tool calls, the evidence in each cited response. Decide whether the evidence supports the claim. Output JSON per the schema."* Iteration belongs in Phase 2 calibration.
- **Vendor binding for v1**: decision deferred to implementation PR (per §7).
- **Batch all Maker claims vs one call per claim**: tradeoff — one call per claim is cleaner per-claim reasoning and easier debugging; batched is cheaper and faster. v1 likely batched; revisit after Phase 2 observation.
- **Later judging of Checker / Moderator claims**: deferred to Phase 5 or beyond. Not needed for first metric; useful for inspector richness.

## Non-goals (explicit)

To keep this ADR practical and aimed at the first real metric:

- This ADR does not introduce a fourth panel vendor; v1 uses an already-configured one.
- This ADR does not redesign the panel's three-role structure (Maker / Checker / Moderator) — those roles and their prompts stay.
- This ADR does not change M12.5 materialization, M13 PE-MC evaluation, or M14 publication. It only specifies what materialization will trust once the judge ships.
- This ADR does not create a hidden rule engine inside the judge prompt; the judge reads context and decides, it does not enumerate cases.
- This ADR is not a broad-architecture rewrite of MCF. It locks the grounding-check decision and nothing else.
