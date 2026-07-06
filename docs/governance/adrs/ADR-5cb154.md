---
uid: DEC-5cb154
title: "M12 Panel Composition v3 + Transport-Agnostic Envelope Harvest + Pre-Adoption Canary Policy"
description: "Pin Maker=Claude Opus 4.7, Checker=GPT-5.5 + Structured Output strict, Judge=Claude Sonnet 4.6. Engine boundary accepts envelopes via tool_use OR text JSON, both flow through AJV + per-role gates + D441. Persist parser_warnings unconditionally. Adopt pre-adoption canary policy. Accept 2-vendor diversity with documented rationale."
status: decided
date: 2026-06-15T12:58:59.978Z
project: bc-core
domain: mcf
subdomain: metric-authoring-panel
focus: governance
---

# M12 Panel Composition v3 + Transport-Agnostic Envelope Harvest + Pre-Adoption Canary Policy

## Context

F1+F2+F3 under TSK-08461b proved the panel envelope protocol assumed uniform vendor tool_choice honoring. Bedrock DeepSeek V3.2 produced semantically-correct envelopes as inline message text rather than tool input, and the F1 observability promise was invisible in persisted transcripts (parser_warnings stripped by projection guard). Live panel 80cce671 against the regression specimen produced Checker OPERATOR_REVIEW silently, masked by 2-of-3 quorum APPROVE_FOR_DRAFT. Three root causes: (1) protocol-vs-model mismatch (a vendor was seated without canary), (2) transport conflated with structure (engine discards valid output because of channel bias), (3) consensus dominance over silent dissent. This ADR fixes (1) by reverting Checker to GPT-5.5 + adding Structured Output strict + reverting Judge to Sonnet 4.6, fixes (2) by making the engine accept both tool_use and text-JSON transports through the same validator, and addresses observability via unconditional parser_warnings projection. Consensus redesign deferred to a separate ADR.

# Context

## Failure trail

TSK-08461b shipped three fixes intended to make the M12 Metric Authoring Panel's Checker role reliable:

- **F1 (PR #290)** — adapter-side observability: when the Stage 2 envelope fails to parse, synthesize a ParseSuccess with `verdict_code='OPERATOR_REVIEW'` and a `parser_warnings[0].warning_code='envelope_schema_violation'` so the silent OPERATOR_REVIEW becomes observable. Helper `buildEnvelopeSchemaViolationResult` added; tests pass.
- **F2 (PR #291)** — JSON Schema tightening: `verification_payload` declared top-level required, and inside it `independent_proposal` + `cross_check_vs_maker` both AJV-required, with `cross_check_vs_maker` declaring four typed fields (formula_ast_match, bindings_match, grain_match: boolean; differences: string[]).
- **F3 (PR #291)** — Checker prompt strengthening: dedicated "Final-response envelope discipline" section, allowed-keys table, JSON skeleton, load-bearing language on the verification_payload mandate.

**Live validation outcome** — panel `80cce671-36f7-45ba-b862-4380a8aecdd9` against the regression specimen `a-track-paid-customer-invoice-count-v2-2026-06-15`, 254s wall-clock, HTTP 201:

| Role | Vendor / Model | Verdict | claim_count | tool_call_count | submit_envelope tool called |
|---|---|---|---|---|---|
| Maker | Anthropic Opus 4.7 | APPROVE_FOR_DRAFT | 7 | 8 | yes |
| **Checker** | **Bedrock DeepSeek V3.2** | **OPERATOR_REVIEW** | **0** | **8 (all BCF discovery)** | **no** |
| Judge | OpenAI GPT-5.5 | APPROVE_FOR_DRAFT | 0 | 0 | yes |

Top-level consensus: APPROVE_FOR_DRAFT (2-of-3 quorum), `grounding_check_passed=true`, `grounding_violations=[]`.

**Root cause from persisted transcript** (Checker transcript_uid `9fa0f23c-911d-45e0-814c-4fce398231b7`): DeepSeek V3.2 produced semantically complete envelope content — `verification_payload` appears at reasoning_trace text position 1106, `cross_check_vs_maker` at position 7162, both sub-blocks present and correct — but emitted as inline text in `reasoning_trace[0].reasoning_text` rather than as `submit_checker_envelope` tool input. The model never called the envelope tool; F2's AJV gate had no tool input to validate; F3's prompt produced the right output in the wrong location.

**F1 observability gap** — persisted Checker transcript shows `has_parser_warnings_key=false`, `has_verification_payload_key=false`. The `buildEnvelopeNotSubmittedResult` helper (which should fire on the tool-absent path) either does not execute in production OR its `parser_warnings` field is dropped by the projection at `panel-payload.parser.ts:524` (`...(parsed.parsed.parser_warnings.length > 0 ? { parser_warnings: parsed.parsed.parser_warnings } : {})`). The promised observability is invisible in the live record.

## The deeper failure

Three protocol assumptions were embedded in the F1/F2/F3 design that did not hold:

1. **Uniform vendor honoring of `tool_choice` forcing.** The two-stage adapter forces `tool_choice` on Stage 2 expecting all three vendors to honor it strictly. Anthropic Opus does. OpenAI GPT-5.5 does. Bedrock DeepSeek V3.2 does not — it produces the envelope as message text content despite the forcing. This is a knowable model property that was not pre-adoption-tested.

2. **Transport conflated with structure.** The envelope's structural correctness is enforced by AJV + per-role shape gates (`validateCheckerShape`) + D441 guards. None of these care whether the JSON arrived via tool_use input or message text. By treating tool_use as the only acceptable transport, the adapter discards perfectly valid structured output because of channel bias.

3. **Consensus dominance over silent dissent.** A 2-of-3 quorum where the Checker silently degrades to OPERATOR_REVIEW reports APPROVE_FOR_DRAFT to the operator with no signal that the verification leg failed. If the operator had trusted the API response top-level verdict without inspecting per-role detail, M12.5 materialization would have proceeded against substrate that had not been independently verified.

# Decision

## D1 — Panel composition v3

| Role | Vendor | Model | Rationale |
|---|---|---|---|
| Maker | Anthropic | Claude Opus 4.7 | Unchanged. Highest-discipline tool_use honoring observed in the failing panel (claim_count=7, 8 tool calls, submit_maker_envelope called reliably). |
| Checker | OpenAI | GPT-5.5 | Reverts to former seat-holder (documented 6/0 success per `model-defaults.ts:18,61`). OpenAI honors `tool_choice` strictly. Independent-vendor verification-side, preserves Anthropic-OpenAI error-detection diversity. |
| Judge | Anthropic | Claude Sonnet 4.6 | Synthesizer role (0 tool calls in live panel — Judge reads Maker + Checker transcripts and renders verdict). Sonnet 4.6 is cheaper + faster than Opus while preserving Anthropic's strict tool_choice discipline. No canary required (same vendor as Maker). |

Replaces the current `{anthropic-opus, bedrock-deepseek, openai-gpt55}` composition documented in `bc-core/src/registry/mcf/panel-agents/model-defaults.ts`. The DeepSeek V3.2 Checker seat is vacated.

## D2 — Engine-boundary envelope harvest (transport-recoverable, not transport-equivalent)

The contract transport for the M12 panel envelope is the role's `submit_{role}_envelope` tool input. That is what every adapter prompts for, what every Stage 2 nudge forces, and what every passing canary must produce. The engine does NOT treat alternative transports as equivalent.

When (and only when) the tool_use branch is empty, the adapter performs a **recoverable** harvest: a brace-balanced scan of the assistant message text extracts the outermost JSON object and submits it to the SAME `parseEnvelopeFromToolInput` validator — same AJV schema, same per-role shape gate (`validateMakerShape` / `validateCheckerShape` / `validateJudgeShape`), same D441 source-literal guard. Acceptance is gated on passing all three exactly as the tool_use path is. A text-encoded payload that fails any gate is rejected the same way a tool_use payload would be.

Two non-negotiables on the recoverable path:

1. **No structural relaxation.** The AJV schema and per-role gates run with the same strict configuration as the tool_use path. The recoverable harvest widens the *intake*, not the *bar*.
2. **Always record `envelope_submitted_via_text`.** Every envelope harvested from text — pass or fail at the validator — records `parser_warning.warning_code='envelope_submitted_via_text'` on the persisted transcript. Warnings compose: a text payload that also fails the validator records `envelope_submitted_via_text` *plus* `envelope_schema_violation`. The transport-degradation signal is independent of and orthogonal to the structural-failure signal; both must remain visible to operators.

The five terminal outcomes per adapter:

| Stage 2 result | AJV + per-role + D441 | Outcome | parser_warnings |
|---|---|---|---|
| tool_use present | pass | ParseSuccess (contract transport) | — |
| tool_use present | fail | OPERATOR_REVIEW | `envelope_schema_violation` |
| tool_use absent + text JSON extracted | pass | ParseSuccess (recoverable transport, observable) | `envelope_submitted_via_text` |
| tool_use absent + text JSON extracted | fail | OPERATOR_REVIEW | `envelope_submitted_via_text` + `envelope_schema_violation` |
| tool_use absent + text not extractable | n/a | OPERATOR_REVIEW | `envelope_not_submitted_via_tool` |

The framing is **engine-as-boundary, transport-strict-but-recoverable**: the engine enforces structural correctness through the same gates regardless of where the envelope arrived, but it discriminates between *contract* and *recoverable* transports in the observability record. Transports are not equivalent; structural correctness is the only equivalence that exists.

## D3 — Unconditional `parser_warnings` projection

Drop the `parsed.parsed.parser_warnings.length > 0 ? ... : {}` guard at `panel-payload.parser.ts:524`. Always project `parser_warnings` (as `[]` when empty) so the field's presence in persisted transcripts is invariant. Eliminates the F1 observability gap discovered in the live panel — the projection cannot decide to omit a field that operators rely on for failure diagnosis.

## D4 — OpenAI Structured Output upgrade for Checker

For the OpenAI Checker, layer Structured Output (`response_format: {type: "json_schema", strict: true}`) on top of the existing `tool_choice` forcing. OpenAI's strict structured output is **grammar-constrained decoding** — sampling is gated by a finite-state machine built from the JSON Schema, so the model cannot emit syntactically invalid or schema-violating output. This is strictly stronger than `tool_choice` forcing (which is behavioral, not structural).

Belt-plus-suspenders: `tool_choice` enforces *which tool gets called*; `response_format` enforces *what shape the output takes*. Together they make the OpenAI Checker unfailable on the envelope axis short of complete API outage.

Anthropic Maker and Anthropic Judge continue using `tool_choice` forcing only — Anthropic does not currently expose grammar-constrained decoding. They are the second-strongest tier.

## D5 — Pre-adoption model canary policy

Before any model is seated in the M12 panel — Maker, Checker, or Judge — a canary must be run and the outcome documented in a seat-change ADR. Required:

- N=10 invocations against the live panel prompt for the target role (`m12-panel-{role}.v1.md`) and the live `submit_{role}_envelope` tool schema.
- Identical message context to a real Stage 2 finalization round (Stage 1 BCF investigation pre-completed; finalization nudge appended).
- Measurements:
  - **tool_call_rate** — fraction of invocations where the model called `submit_{role}_envelope`. Required: at least 9 of 10.
  - **envelope_completeness** — fraction of submitted envelopes passing AJV + per-role shape gate. Required: 10 of 10.
  - **observed parser_warnings** — any warning code emitted on the path.
- A failing canary blocks the seat. A passing canary is referenced in the ADR that authorizes the seat.

The current vacating of DeepSeek V3.2 is the negative case study: the model was seated without this canary, and the discipline gap was not visible until live M12 panels degraded silently for multiple production runs.

## D6 — Vendor diversity trade-off

This composition uses **two vendors** (Anthropic x 2, OpenAI x 1), relaxing the earlier three-vendor rule documented in `model-defaults.ts:76`. The relaxation is intentional and justified:

- The three-vendor rule existed for (a) outage resilience and (b) error-detection diversity.
- (a) is structurally weaker than designed: the Maker is a single point of failure regardless. If Anthropic is down, no Maker means no panel run. Adding a third vendor to the Judge seat does not change the outage exposure because Maker fails first.
- (b) is preserved by the Checker. Under D425 Phase 2, the Checker is the **independent re-deriver**; the Judge is a **synthesizer** that reads Maker + Checker transcripts (0 tool calls in the live panel). Error-detection diversity that matters is Maker vs Checker, not Checker vs Judge. Cross-vendor (Anthropic vs OpenAI) is preserved on that axis.

Risk accepted: Anthropic API outage takes down both Maker and Judge simultaneously, halting panel runs until vendor recovery. This is judged acceptable for governed authoring traffic which is not real-time.

# Out of scope (explicit non-bundle)

The following are deliberately not addressed in this ADR. Each is a real concern; folding them in would dilute the decision and bloat the implementation PR:

- **Maker grounding-check defect** — orthogonal failure mode observed in prior sessions. Separate task, separate ADR if a structural fix is needed.
- **Consensus quorum redesign** — the 2-of-3 dominance over silent Checker dissent is a real governance issue but it is a *consensus rule* concern, not a *protocol transport* concern. Belongs in a separate ADR on consensus design (options: require unanimity for APPROVE_FOR_DRAFT; auto-downgrade to OPERATOR_REVIEW on any role degrade; surface dissent as `operator_review_reason`).
- **Delta-diff Checker shape** — instead of the Checker emitting a full envelope with its own `independent_proposal` + `cross_check_vs_maker`, it could emit a typed delta diff against the Maker's proposal. Smaller surface, harder to drift. Architectural alternative for a future ADR.
- **MCP-server framing of the panel engine** — wrapping `submit_{role}_envelope` in an MCP server does not change which transport hits the model; MCP is tool discovery, not tool enforcement. Considered and rejected as out of scope.

# Implementation plan (high-level, separate PRs)

The implementation is sequenced to ship a load-bearing change quickly, then layer the strongest guarantee, then institutionalize the policy. Each phase is its own PR with its own SHA-pinned merge.

**Phase 1 — engine-boundary harvest + projection fix + composition swap (one PR).**
- Add `parseEnvelopeFromAssistantText(text, role)` pure helper. Brace-balanced JSON extraction; delegates to `parseEnvelopeFromToolInput`; emits `parser_warning.envelope_submitted_via_text` on success.
- Wire three vendor adapters (`anthropic-agent.adapter.ts`, `bedrock-agent.adapter.ts`, `openai-agent.adapter.ts`) to the four-outcome flow in D2.
- Drop the `length > 0` projection guard at `panel-payload.parser.ts:524`.
- Update `model-defaults.ts` constants: `DEFAULT_CHECKER_MODEL='gpt-5.5-2026-04-23'` (or current snapshot), `DEFAULT_JUDGE_MODEL='claude-sonnet-4-6'`. Adjust per-role `MAX_OUTPUT_TOKENS` if the new models need different budgets.
- Live proof gate: re-run M12 against `a-track-paid-customer-invoice-count-v2-2026-06-15`. Required green: Checker `verdict_code='APPROVE_FOR_DRAFT'`, Checker transcript has `verification_payload` key, no `envelope_schema_violation` warning.

**Phase 2 — OpenAI Structured Output upgrade (separate PR).**
- Add `response_format: {type: "json_schema", strict: true}` to the OpenAI Checker Stage 2 call, alongside existing `tool_choice` forcing.
- Transform `CHECKER_ENVELOPE_PARAMETERS` from `envelope-tool.ts` into the OpenAI `json_schema` shape (add `name`, `schema`, `strict` wrapper).
- Live proof gate: re-run M12; confirm Checker outcome unchanged or improved.

**Phase 3 — pre-adoption canary policy doc (separate PR).**
- Author `bc-docs-v3/docs/onboarding/m12-panel-model-canary-procedure.md` documenting D5.
- Reference from `model-defaults.ts` header comment.

**Phase 4 — DeepSeek V3.2 retirement and bc-ai composition reconciliation (separate task).**
- Audit `bc-ai` for other panel uses of DeepSeek V3.2 (per `task #782 bc-ai Path A DeepSeek Converse client`). Decide retain/retire per use.
- This is downstream cleanup; not blocking the M12 fix.

# Verification

The decision is considered verified when:

1. A live M12 panel against the regression specimen `a-track-paid-customer-invoice-count-v2-2026-06-15` produces Checker `verdict_code='APPROVE_FOR_DRAFT'` from GPT-5.5 *and* the persisted Checker transcript contains `verification_payload.cross_check_vs_maker` with all four typed fields populated.
2. A negative test (e.g. a Checker prompt deliberately designed to produce envelope-text fallback) produces `parser_warning.envelope_submitted_via_text` in the persisted transcript — proving the engine-boundary harvest fires *and* is observable.
3. The canary procedure document is referenced by `model-defaults.ts` and the canary results for each of Maker/Checker/Judge seats are recorded in this ADR's verification appendix.
4. ChainStatus, M14 activation gate, M12.5 materialization preflight, and PE-MC evaluator behavior are unchanged. The fix is strictly contained to the panel-engine boundary.

# Rollback

- Phase 1 rollback: revert the SHA-pinned merge commit. The two-stage adapter falls back to current tool_use-only behavior, the DeepSeek V3.2 Checker resumes silent degradation, the failure mode returns. Acceptable as a temporary state if a defect is found in the new harvest path.
- Phase 2 rollback: revert the OpenAI structured-output wiring. Checker falls back to tool_choice-only (still GPT-5.5). No degrade in correctness — only in defense-in-depth.
- Phase 3 rollback: the canary policy document is procedural. Reversion is removing the doc; substrate is unaffected.

# References

- TSK-08461b — M12 structured-output defect remediation (parent task)
- PR #290 (commit e07c8b9) — F1 adapter observability (shipped, live-unproven)
- PR #291 (commit df46925) — F2 schema tighten + F3 prompt strengthen (shipped, live-disproven)
- Panel `80cce671-36f7-45ba-b862-4380a8aecdd9` — live validation FAILURE evidence (this ADR's primary motivation)
- Panel `a4f726d4-adb9-45bf-b09c-5f6ff7c4621d` — pre-F1/F2/F3 baseline failure
- Held investigation report: `bc-core/scripts/audit-output/tsk-08461b-m12-structured-output-defect-investigation-held-2026-06-15.md`
- DEC-09f86b (D425 Phase 2) — M12 Maker-Checker-Judge shape + Exhibit-ID abstraction (PROPOSED, not superseded by this ADR — this ADR adopts the shape and specifies models within it)
- DEC-c3e57f / D422 — Foundational MCF (decided) — the M-track authority cited by CLAUDE.md
- Foundation Invariants — `bc-docs-v3/docs/foundation/the-invariants.md` (B-layer change per repair-location classification)
- `bc-core/src/registry/mcf/panel-agents/model-defaults.ts` — current composition source (to be updated in Phase 1)
- `bc-core/src/registry/mcf/panel-agents/panel-envelope-finalization.ts` — F1 helper module (extended in Phase 1)
- `bc-core/src/registry/mcf/panel-agents/panel-payload.parser.ts:524` — projection guard to be removed in Phase 1
