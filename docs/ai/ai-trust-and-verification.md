---
id: ai-trust-and-verification
order: 31
title: "AI Trust and Verification"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, the-dual-layer-interaction-model, operating-model-overview, audit-and-activity-logging, ai-architecture, ai-agents, ai-gates]
governing_sources:
  - Foundation
  - The Dual-Layer Interaction Model
  - The Authority Model
  - Operating Model
  - Audit and Activity Logging
  - AI Architecture
  - AI Agents
  - AI Gates
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the AI section)
  - DEC-804874 (D366 L-node semantic gate; the trust ladder anchors at this gate's behavior)
  - DEC-ebf0b4 (D268 Session Discipline and Data Integrity; the auditor is one node on the trust ladder)
errata_referenced: []
v2_sources: []
diagrams: []
---

# AI Trust and Verification

## Scope

This chapter records the platform's trust posture toward AI verdicts in the readiness baseline: the cross-family discipline that pairs a maker from one model family with a checker from a different family, the implicit trust ladder a verdict moves through (deterministic-passed, single-AI-passed, cross-family-passed, human-approved), the verdict aging concern that the platform has not yet addressed, the auditor's place on the ladder as a session-level rather than runtime-level verifier, the Dual-Layer Interaction Model that locates AI participation on the Conversation surface rather than the Trust surface, and the gaps the chapter records as drift.

This chapter sits between AI Gates and AI Usage Visibility. AI Gates records the verdict consumption; this chapter records what each verdict's trust posture is worth. AI Usage Visibility records the tenant-facing transparency surface that exposes the trust posture to end users.

This chapter does not redefine the maker-checker-gate triplet pattern (deferred to AI Architecture), the agent inventory (deferred to AI Agents), the model substrate or per-provider client detail (deferred to Bedrock and Inference Profiles), the verdict consumption posture (deferred to AI Gates), or the tenant-facing transparency surface (deferred to AI Usage Visibility). The chapter records the trust ladder; it does not enumerate which agents produce which trust level in the readiness baseline (that is per-agent detail in AI Agents).

**Governing source.** AI Architecture; AI Gates; outline.md §4.4.

## Why Cross-Family Verification

A single-model verdict can encode the model family's systematic biases without an independent counter-check. The biases come from a model's training data, its alignment regime, its tokenizer, and the family's collective tuning history; two models from the same family share enough of these to fail to surface each other's biases. A cross-family pair (a Gemini maker plus a Claude checker, or vice versa) does not eliminate bias; it surfaces disagreement when the two families' biases diverge on a candidate, which is a signal the calling service can act on.

The platform's target discipline is that governed AI acts run as maker-checker-gate triplets (per AI Architecture) and that the maker and checker come from different families. Current registry grounding only partially realizes that target: seven triplets pair Gemini makers with direct-Anthropic checkers; four pair Gemini makers with Gemini checkers; `field-map` pairs direct-Anthropic maker and checker. The pairing is per-act and fixed at act registration; AI Architecture's drift inventory records the current same-family pairings and the absence of an automated assertion.

The cross-family commitment is not absolute. The chapter records two carve-outs:

| Carve-out | Where it applies | Why it is permitted |
|---|---|---|
| KPI decomposition uses direct Anthropic Haiku Maker A, Sonnet Maker B, and Haiku moderator calls | `app/kpi/decompose.py` | The act is operator-driven and the moderator's role is reconciliation rather than cross-family disagreement; the verdict surfaces in bc-admin's AI Log tab (when the tab's data hooks land) for human review rather than feeding a governed gate. The act's trust posture is dual-model-with-moderator, lower than cross-family-passed |
| KPI Assistant uses a single Claude Haiku 4.5 call | `app/kpi_assistant/orchestrator.py` | The act is operator-driven and tenant-driven and does not feed a governed gate. The Q-and-A surface returns the answer plus a confidence score; the calling user reads with awareness that the answer is single-model |

Both carve-outs are recorded explicitly. AI Usage Visibility records that the bc-admin surfaces should expose the trust posture (cross-family-verified, single-model, etc.) so users can read the answer with awareness; the surface is queued.

**Governing source.** `bc-ai/app/agents/`; `bc-ai/app/kpi/decompose.py`; `bc-ai/app/kpi_assistant/orchestrator.py`; AI Architecture; AI Usage Visibility.

## The Implicit Trust Ladder

A verdict moves through a sequence of trust levels as the platform applies more verification to it. The ladder is implicit in the readiness baseline: no schema column records the trust level; the level is implicit in the verdict's provenance (which agents produced it, which gates approved it, which humans accepted it). The chapter names the ladder so that future schema work can encode it explicitly.

| Level | What it means | Where the platform records it in the readiness baseline |
|---|---|---|
| Unverified | No AI verdict has been computed; the candidate is the maker's output or the operator's input | Default state for new candidates; no `verificationStatus` column is set |
| Deterministic-passed | A rule-based pre-filter (the compatibility filter at `bc-core/src/registry/semantic/compatibility-filter.service.ts`) returned a definitive answer that did not require an AI call | The L-node trace records `verdict: 'green'` or `'red'` with `agent_flow_id: 'compatibility-filter'`; the verdict is durably recorded but did not consume AI |
| Single-AI-passed | A single AI act (a single maker, no checker) returned a verdict; the verdict is single-model | KPI decomposition's per-Maker output before reconciliation; KPI Assistant's answer; verdicts that the platform consumes inline without persisting (operator-driven verification surfaces) |
| Cross-family-passed | A maker-checker-gate triplet returned a green or amber verdict; the maker and the checker came from different model families and the gate combined them | The L-node trace records the verdict with the agent's `flow_id`; the model registry's per-role provider field encodes the cross-family pairing |
| Human-approved | A human reviewer approved an amber or red verdict, or a session-close override was supplied with a 40+ character rationale per DEC-804874 | The override rationale lives in DevHub's change record (`change_records.report_json.l_node_override`); human review on amber items lives in bc-ai's `review_queue` table; bc-core does not have a per-CC `human_approved_at` column |

The ladder is durable in the trace and in the verdict tables, but it is not addressable as a single field. A reader who wants to ask "is this CC field's mapping cross-family-passed?" must read the per-trace `agent_flow_id` and the model registry's per-role provider field, then infer the trust level from the pairing. A future hardening would surface the trust level as an explicit column on the verdict; the drift inventory records this.

**Governing source.** `bc-core/src/registry/semantic/compatibility-filter.service.ts`; `bc-core/src/registry/semantic/l-node-semantic.service.ts`; `bc-ai/app/db/schema.sql`; AI Gates.

## Verdict Aging

A verdict is computed against a specific maker, checker, and gate version, against a specific input, and against the model registry configuration recorded for that act. The platform does not declare a verdict aging policy in the readiness baseline: a preserved green verdict is read as green until re-verification records a different result, regardless of whether the agent's prompt has been updated, the model has been swapped, the input has changed, or the source substrate the verdict relies on has shifted.

The drift inventory records this. Three dimensions of staleness exist:

| Aging dimension | What stales | Mitigation queued |
|---|---|---|
| Agent-prompt staleness | An agent's prompt is updated; the verdict was computed against the old prompt | Re-verification cadence per agent (every N days, or on-prompt-change); not yet declared |
| Model staleness | The model registry swaps the maker, checker, or gate model (a Bedrock inference profile is replaced; an Anthropic API model version reaches end-of-life) | Re-verification on registry change; not yet declared |
| Input staleness | The candidate the verdict was computed against has been edited since (the CC field mapping has been updated; the metric definition has been amended) | Re-verification on input change is partially in place (the L-node verifier re-runs on demand) but the cadence is operator-driven, not automated |

The session-close gate per DEC-804874 consults the rollup at session close; a stale rollup is read as not-red and lets the close proceed. A reader who wants high-confidence current state runs `devhub_l_node_refresh` before consulting the verdict; the refresh re-invokes the L-node semantic verifier against current state. The refresh discipline is in CLAUDE.md but is operator-driven; AI Trust and Verification records the policy gap.

**Governing source.** `bc-core/src/registry/semantic/l-node-semantic.service.ts`; `barecount-devhub/src/`; CLAUDE.md.

## The Auditor as a Trust Node

The session governance auditor (per AI Agents) is one node on the trust ladder. The auditor reviews session conduct against the session-discipline rules per DEC-ebf0b4; its verdict (`pass`, `concerns`, `fail`) is a trust signal about the session's adherence to the discipline. The auditor's verdict is advisory at the time of writing: a `fail` verdict records into DevHub's `process_audit` table but does not block session close.

The auditor sits at session-level, not runtime-level. A green verdict from the auditor says the session followed the discipline; it does not say the session's runtime-level verdicts were correct. The two dimensions are independent: a session can follow the discipline while one of its runtime AI verdicts is wrong, and a session can violate the discipline while its runtime AI verdicts are all correct. The chapter records the two as separate trust nodes; AI Gates owns the runtime-level gate posture.

The auditor's cross-family posture is asymmetric. The auditor uses Gemini 2.5 Pro; the runtime triplets that the auditor reviews use a mix of Gemini, Anthropic API direct, and Bedrock-served models. A session's runtime verdicts are produced by one set of model families; the auditor verifies the session's adherence to discipline using a different family. This is a deliberate cross-family pattern at the audit level; the chapter records the pattern but does not enumerate per-payload prompt detail (deferred to AI Agents).

**Governing source.** `bc-ai/app/auditor/`; AI Agents; DEC-ebf0b4.

## Foundation: AI Lives on the Conversation Surface

The Dual-Layer Interaction Model declares two surfaces: a Conversation surface (advisory, ephemeral, where AI participation lives) and a Trust surface (authoritative, immutable, where the proof chain lives). AI verdicts run on the Conversation surface. The platform's authoritative state (Source Objects, Canonical Objects, Metric Snapshots, Action Objects, plus their Evidence and Lineage rows) is produced at the four governed boundary acts and is owned by Operating Model: Evidence and Lineage; AI does not produce authoritative state.

Where AI verdicts feed the Trust surface (the L-node semantic gate at session close per DEC-804874), the verdict is a recorded input that governs the Trust surface's gates; the Trust surface's authoritative state remains produced by the four boundary acts. The gate consumes the AI verdict to decide whether to admit further authoritative state, but the gate does not write Evidence; the boundary act writes Evidence.

The asymmetry is the central commitment of the trust posture. AI is a verification surface; AI is not the authority. A reader who is uncertain about a verdict can fall back to the boundary act's Evidence and Lineage; the proof chain is preserved regardless of the AI verdict's trust level. The Dual-Layer Interaction Model is the binding architectural authority for this commitment; the chapter records the commitment and routes to Foundation.

**Governing source.** The Dual-Layer Interaction Model; Operating Model: Evidence and Lineage; AI Gates.

## Failure Modes

| Cause | System response |
|---|---|
| The maker and checker happen to be from the same model family for an act | No automated assertion catches this; the act runs and produces a verdict that is single-family-passed rather than cross-family-passed; the trust level is silently lower than the chapter prescribes; mitigated only by code review |
| A verdict is consumed at session close with stale state | The L-node gate reads the persisted rollup; staleness is not detected; the gate may admit a session whose verification is stale; operator-driven `devhub_l_node_refresh` is the mitigation |
| The auditor's `fail` verdict is recorded but session close proceeds | The advisory posture is by design; auditing is governance, not runtime gating; the operator reviews the verdict in a subsequent action |
| KPI decomposition's two Makers agree but the Moderator disagrees | The verdict is `disputed`; the act surfaces the dispute; no automated retry; the operator reviews |
| A human approver supplies a fabricated override rationale | The override is accepted (length-only check per DEC-804874); the auditor agent's review may flag the override as concerning if the rationale does not match the session's other state; the platform cannot detect dishonest text |
| The model registry swaps a model and prior verdicts are not re-verified | The trust ladder records the verdict as cross-family-passed against the registered pairing at the time of recording; staleness against the new registry state is not detected |

**Governing source.** `bc-ai/app/agents/`; `bc-core/src/registry/semantic/`; AI Architecture; AI Gates.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| Trust ladder is implicit, not encoded as a schema column | Open | No `trust_level` column on `l_node_semantic_trace`, `l_node_semantic_verdict`, or any verdict-bearing table; the level is inferred from the verdict's provenance |
| Cross-family discipline is not runtime-enforced | Open | A future act that registers a same-family maker-checker pairing is not caught by an automated assertion; mitigated only by code review at registration time |
| Verdict aging policy is not declared | Open | No re-verification cadence per agent, per model, or per input change; stale verdicts are read as current; operator-driven re-evaluation through `devhub_l_node_refresh` is the only mitigation |
| Auditor is advisory only | Open | A `fail` verdict records but does not block session close; only the L-node semantic gate per DEC-804874 is a hard close-blocker |
| Override rationale is length-checked, not content-checked | Open | An operator can supply a fabricated 40+ character rationale and the override succeeds; the platform cannot detect dishonest text |
| KPI decomposition and KPI Assistant are not cross-family-verified | Low | The carve-outs are explicit (operator-driven, not feeding a governed gate); the trust posture is single-model or single-family-with-moderator; future hardening to cross-family is queued |
| Model registry swaps do not trigger re-verification | Low | When the registry swaps a maker, checker, or gate model, prior verdicts continue to be read as current; the platform does not invalidate the prior verdicts |
| Trust ladder is not surfaced to tenants | Open | bc-portal does not expose the trust posture; bc-admin's AI tabs are platform-admin-only and the data hooks are disabled; AI Usage Visibility records the broader surface gap |

**Governing source.** AI Architecture; AI Gates; AI Usage Visibility; CLAUDE.md.

## Boundaries with Adjacent Chapters

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| AI Architecture | AI section | Owns the maker-checker-gate triplet pattern. This chapter records why the cross-family pairing is the discipline; AI Architecture records the pattern |
| AI Agents | AI section | Owns the agent inventory. This chapter records the trust ladder; AI Agents records which agents produce which trust level in the readiness baseline |
| AI Gates | AI section | Owns the verdict consumption posture. This chapter records the trust posture; AI Gates records what bc-core does with the verdict |
| AI Usage Visibility | AI section | Owns the tenant-facing transparency surface. This chapter records the implicit trust ladder; AI Usage Visibility records the surface that should expose the trust level to users |
| The Dual-Layer Interaction Model | Foundation | Owns the architectural commitment that AI runs on the Conversation surface and not the Trust surface. This chapter records the commitment; Foundation owns it |
| Evidence and Lineage | Operating Model | Owns the runtime proof chain. This chapter records that AI verdicts are governance, not runtime proof; Evidence and Lineage records the proof commitment |
| Quality Gates and Chain Integrity | Operating Model | Owns the gate authority over runtime decisions. This chapter records that the L-node gate consumes AI verdicts; Quality Gates records the gate's authority |
| Audit and Activity Logging | Implementation section | Owns the operational governance trail. This chapter records the auditor's place on the trust ladder; Audit and Activity Logging records the substrate that captures the auditor's verdicts |

**Governing source.** Foundation; Operating Model; Implementation; outline.md §4.4.

## Governing Decisions

| Decision | Title | AI trust impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The AI Trust and Verification chapter exists in the AI section per DEC-c06f41 |
| DEC-804874 | D366 L-node semantic gate at session close | The trust ladder anchors at this gate's behavior; the override mechanism (40+ character rationale) is the platform's human-approved trust node at session close |
| DEC-ebf0b4 | D268 Session Discipline and Data Integrity (ten rules) | The auditor verifies session conduct against these rules; the auditor is one node on the trust ladder, distinct from runtime-level verifiers |

**Governing source.** The Authority Model.

## References

- AI Architecture
- AI Agents
- Bedrock and Inference Profiles
- AI Gates
- AI Usage Visibility
- Audit and Activity Logging
- The Dual-Layer Interaction Model
- Evidence and Lineage
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-804874: L-node semantic gate (D366)
- DEC-ebf0b4: Session Discipline and Data Integrity (D268)
- outline.md §4.4: AI
- Decisions: ADR Registry

