---
id: ai-gates
order: 30
title: "AI Gates"
status: drafting
authority: authoritative
depends_on: [foundation-overview, the-authority-model, operating-model-overview, evidence-and-lineage, audit-and-activity-logging, ai-architecture, ai-agents]
governing_sources:
  - Foundation
  - The Authority Model
  - Operating Model
  - Evidence and Lineage
  - Audit and Activity Logging
  - AI Architecture
  - AI Agents
governing_adrs:
  - DEC-c06f41 (Spine expansion to eight sections plus home; this chapter exists in the AI section)
  - DEC-804874 (D366 L-node semantic gate at session close; consumes the cc-field-audit triplet's verdict; the one hard close-blocker that depends on AI)
  - DEC-bebaec (Chain Status SSOT; the chain-completeness gate substrate that runs alongside the AI gate but does not consume AI verdicts)
errata_referenced: []
v2_sources: []
diagrams: []
---

# AI Gates

## Scope

This chapter records how AI verdicts cross from bc-ai into bc-core's gate substrate, in their as-built state at the time of writing: the verdict response shape every triplet returns, the routing semantics in `{green, amber, red}` that calling services consume, the per-route policy bc-core applies when consuming a verdict, the L-node semantic gate per DEC-804874 that is the one hard close-blocker depending on AI verdicts, the failure-handling posture when bc-ai is unavailable, and the persistence boundaries between bc-ai's verdict trail and bc-core's gate-state record.

This chapter sits between AI Agents and AI Trust and Verification. AI Agents records what agents exist; this chapter records what their verdicts mean to bc-core's gates; AI Trust and Verification records the cross-family discipline that gives the verdicts their trust posture.

This chapter does not redefine the maker-checker-gate triplet pattern (deferred to AI Architecture), the agent inventory (deferred to AI Agents), the model substrate (deferred to Bedrock and Inference Profiles), the trust ladder (deferred to AI Trust and Verification), the chain-status SSOT that runs alongside but separate from the AI gate (deferred to Quality Gates and Chain Integrity in Operating Model), or the per-tenant accept-and-reject trail (deferred to AI Usage Visibility). The chapter records the verdict shape and the consumption posture; the gate authority over runtime decisions is owned by Quality Gates and Chain Integrity.

**Governing source.** AI Architecture; AI Agents; Audit and Activity Logging; outline.md §4.4.

## The Verdict Response Shape

Every maker-checker-gate triplet returns a structured response. The response is a Pydantic model defined at `bc-ai/app/agents/base.py`; the persisted shape is the `PipelineResult` model. The response carries:

| Field | Purpose |
|---|---|
| `maker_result` | The maker's structured output (the candidate decision, classification, mapping, or recommendation) plus the maker's confidence |
| `checker_result` | The checker's structured output (the agreement-or-disagreement signal) plus the checker's confidence |
| `gate_result` | The gate's structured output (the final verdict the calling service consumes) plus the gate's confidence and reasoning |
| `routing` | The final routing decision in `{green, amber, red, not_applicable}` |
| `combined_confidence` | A scalar combining the three confidences per the gate's policy |
| `evidence_id` | The identifier of the evidence row the orchestrator wrote to bc-ai's local SQLite |

The HTTP response shape that calling services receive includes the gate's structured output (the verdict), the routing decision, the combined confidence, plus the maker's structured output as a `suggestion` field (so the calling service can surface the candidate to a human reviewer if the routing is amber) and the checker's structured output as a `validation` field. The exact response shape lives at `bc-ai/main.py`; the chapter records the conceptual fields and routes the per-call serialization to the source.

A `not_applicable` routing is recorded when bc-ai is unreachable or when the orchestrator's deterministic pre-filter returned a definitive answer that did not require the model call. `not_applicable` is distinct from `red`: a red routing means the AI evaluated and rejected the candidate; a `not_applicable` routing means the AI did not evaluate. Calling services apply different policies to the two.

**Governing source.** `bc-ai/app/agents/base.py`; `bc-ai/main.py`; AI Architecture.

## Routing Semantics

The routing decision is a recommendation, not a binding verdict. The act records the routing; the calling service decides what to do with it. Routing thresholds default to:

| Routing | Default threshold | Calling-service interpretation |
|---|---|---|
| `green` | Combined confidence at or above 0.85 with no checker disagreement | The candidate may proceed without human review; the calling service writes the candidate to its own state |
| `amber` | Combined confidence between 0.60 and 0.84, or a checker disagreement that the gate did not resolve | The candidate is queued for human review; the calling service writes the candidate to a review queue rather than to its authoritative state |
| `red` | Combined confidence below 0.60, or a gate explicit-rejection routing | The candidate is rejected; the calling service does not write the candidate; the rejection is recorded for the operator |
| `not_applicable` | bc-ai unreachable, deterministic pre-filter returned a definitive answer, or the act's policy was bypassed | The calling service applies its own policy: fail closed, fail open with explicit `verificationStatus: 'unverified'`, or skip the verification with a recorded reason |

The gate is allowed to override the threshold-derived routing when its structured output explicitly asserts a different routing. The cc-field-audit triplet uses the override: when the audit detects a change to a CC field's mapping, the gate forces `red` regardless of the combined confidence (the audit's policy is to require human approval for any mapping change rather than relying on confidence). The override mechanism lives in `bc-ai/app/pipeline/orchestrator.py`; the per-act override policy lives in the gate class.

**Governing source.** `bc-ai/app/pipeline/orchestrator.py`; `bc-ai/app/agents/cc_field_audit.py`.

## bc-core's Gate Consumption

bc-core consumes AI verdicts through the `BcAiClient` service at `bc-core/src/registry/semantic/bc-ai-client.service.ts`. The client carries seven invocation methods: `invokeCcFieldAudit`, `invokeFieldMapper`, `invokeChainAuditor`, `invokeMetricTracer`, `invokeMetricVerifier`, `invokeSourceVerifier`, and `invokeTableVerifier`. Each method posts to the corresponding bc-ai endpoint and parses the response.

Of the seven invocation methods, only `invokeCcFieldAudit` is wired into a governed bc-core gate at the time of writing. The wiring lives in `bc-core/src/registry/semantic/l-node-semantic.service.ts`: when the L-node semantic verifier processes a node check that the deterministic compatibility filter returned `inconclusive` for, the verifier calls `invokeCcFieldAudit`, persists the agent's verdict to `contract.l_node_semantic_trace`, and rolls the per-trace verdict up into the per-MC `contract.l_node_semantic_verdict` row.

The other six invocation methods are defined and tested but are not wired into a governed gate. Direct callers (operator-driven verification through bc-admin pages, ad-hoc bulk runs, the housekeeping `registry-refresh` agent's metadata sweep) invoke them and consume the verdicts inline; the verdicts do not feed a bc-core gate that runs at a boundary act. AI Agents records this as drift; the integration of the remaining triplets into governed gates is queued.

**Governing source.** `bc-core/src/registry/semantic/bc-ai-client.service.ts`; `bc-core/src/registry/semantic/l-node-semantic.service.ts`; AI Agents.

## The L-Node Semantic Gate

The L-node semantic gate per DEC-804874 is the one hard close-blocker that depends on AI verdicts. The gate runs at session close: `devhub_session_close` consults `contract.l_node_semantic_verdict` rows on bc-core's platform database whose `computedAt` falls within the session's window; if any verdict reached `red` during the session, close is blocked unless `self_audit_json.l_node_override` is supplied with a rationale of at least 40 characters. The gate is enforced in DevHub's session-close handler; its detail is in Audit and Activity Logging.

The L-node semantic verdict the gate consults is rolled up from per-trace verdicts the L-node semantic verifier wrote during the session. Each trace row records which agent produced which verdict; the rollup is per metric contract and per metric version code, not per CC field. The rollup carries per-level verdicts for the seven L-node levels (L1 through L7 plus an L8 reserved for future use) plus an `overallSemanticVerdict` field. The trace and the rollup live in two tables in the `contract` schema:

| Table | Primary key | What it stores |
|---|---|---|
| `contract.l_node_semantic_trace` | (mc_uid, mv_code, cf_code, variable_code, l_node_code, agent_flow_id) | Per-agent verdict per level per CC field per variable per metric contract; carries verdict, confidence, agent_flow_id, agent response payload as JSON |
| `contract.l_node_semantic_verdict` | (mc_uid, mv_code) | Per-MC rollup with per-level verdicts and the overall verdict |

The gate's authority is structural: it depends on the per-MC rollup being present and not red. The gate does not consult bc-ai's evidence trail directly; bc-core has already pulled and persisted the per-trace and per-verdict rows by the time the gate runs.

**Governing source.** DEC-804874; `bc-core/src/database/schema/contract/l-node-semantic-verdict.ts`; `bc-core/src/database/schema/contract/l-node-semantic-trace.ts`; `bc-core/src/registry/semantic/l-node-semantic.service.ts`; Audit and Activity Logging.

## Failure Handling

When bc-ai is unavailable, bc-core's `BcAiClient.invoke` returns a structured failure rather than raising. The structured failure carries `verdict: 'not_applicable'`, an error message, and a detail JSON; the calling service decides what to do.

The L-node semantic verifier's policy on `not_applicable` is to record the trace row with `verdict: 'not_applicable'` and roll the per-MC rollup up to `not_applicable` for the affected level. The gate at session close treats `not_applicable` as not-red; close is not blocked. The discipline is fail-open at the gate but record-the-outage in the trace: the trace is the durable record that AI verification did not run, so the operator can re-run the verification later when bc-ai is reachable, and the auditor reading the trace can see that the verdict was unverified rather than verified-and-passed.

The CLAUDE.md guidance reinforces the discipline: "Never skip AI verification silently; if bc-ai is down, record the outage and proceed with `verificationStatus: 'unverified'`." The implementation follows this: the outage is recorded as `not_applicable` rather than silently skipped, and the calling service's `verificationStatus` field surfaces the unverified state to consuming services.

The fail-open posture is a deliberate choice. AI verification is governance; it is not the primary correctness substrate. The runtime proof chain (Operating Model: Evidence and Lineage) and the chain status SSOT (DEC-bebaec) are the primary correctness substrates. Fail-closed on AI verification would block the platform on a non-correctness gate; the platform chooses to record-and-proceed instead.

**Governing source.** `bc-core/src/registry/semantic/bc-ai-client.service.ts`; `bc-core/src/registry/semantic/l-node-semantic.service.ts`; CLAUDE.md.

## Persistence Boundary

AI verdicts persist in three places. The persistence boundary is asymmetric and worth recording per pattern 86 (persistence-claim precision):

| Substrate | Where it lives | Authority |
|---|---|---|
| Triplet evidence (per-flow maker, checker, gate outputs plus combined confidence and routing) | bc-ai local SQLite (`evidence` and `draft_evidence` tables) | bc-ai produces; bc-core does not read |
| Per-trace AI verdict (per agent invocation per level per CC field per variable per MC) | bc-core platform database (`contract.l_node_semantic_trace`) | bc-core's L-node semantic verifier writes; DevHub reads (via `devhub_l_node_audit`) |
| Per-MC AI verdict rollup | bc-core platform database (`contract.l_node_semantic_verdict`) | bc-core's L-node semantic verifier writes; DevHub reads at session close per DEC-804874 |

bc-ai's evidence trail is not pushed to bc-core's database. bc-core captures only the verdict per trace row, not the maker output, the checker output, or the gate output. A reader who wants the full verdict trail (the prompt, the maker's reasoning, the checker's signal, the gate's structured output) reads bc-ai's local SQLite. A reader who wants the per-MC verdict status reads bc-core's `l_node_semantic_verdict` table. A reader who wants the gate decision at session close reads DevHub's `change_records.report_json.discipline_audit` (when the operator supplied the audit) plus the `l_node_override` rationale (when an override was supplied per DEC-804874).

The asymmetric persistence is intentional. bc-ai is the verdict producer; bc-core is the verdict consumer; DevHub is the gate-state authority. Replicating bc-ai's full evidence trail into bc-core would couple the two services tightly and would duplicate the proof material the platform has chosen to keep close to its producer. AI Trust and Verification owns the trust ladder; this chapter records the gate consumption.

**Governing source.** `bc-ai/app/db/schema.sql`; `bc-core/src/database/schema/contract/l-node-semantic-trace.ts`; `bc-core/src/database/schema/contract/l-node-semantic-verdict.ts`; `barecount-devhub/src/db.js`; AI Trust and Verification.

## Failure Modes

| Cause | System response |
|---|---|
| bc-ai unreachable when bc-core invokes a triplet | `BcAiClient.invoke` returns `{verdict: 'not_applicable', error, detailJson}`; the L-node semantic verifier records a trace row with `verdict: 'not_applicable'`; the L-node gate at session close treats `not_applicable` as not-red; close is not blocked; the outage is durably recorded in the trace |
| Triplet returns `red` for a CC field mapping change | The gate forces red regardless of confidence (cc-field-audit policy); the L-node trace records red; the L-node rollup records red for the affected level; session close is blocked unless an override rationale of 40+ characters is supplied per DEC-804874 |
| Triplet returns `amber` | The L-node trace records amber; the L-node rollup is amber for the level; session close is not blocked (only red blocks); the operator decides whether to address the amber state in a subsequent session |
| Triplet returns `green` | The L-node trace records green; the L-node rollup is green for the level; the gate does not block |
| L-node trace write fails (database unreachable mid-session) | The verifier raises; the calling code path's caller must handle; the L-node rollup is not updated; the gate at session close consults whatever rollup state is current and treats absence as not-red |
| L-node rollup is partially populated (some levels green, some amber, some absent) | The gate's overall-verdict computation rolls up per its policy; the gate does not require every level to be green; AI Trust and Verification owns the per-level rollup discipline |
| Override rationale supplied is shorter than 40 characters | DevHub's `devhub_session_close` rejects the override; close is blocked until a longer rationale is supplied |
| Operator supplies a fabricated override rationale | The override is accepted (the system cannot detect dishonest text); the override is recorded in the change record; the auditor agent's subsequent review may flag the override as concerning if the rationale does not match the session's other state |

**Governing source.** `bc-core/src/registry/semantic/`; `barecount-devhub/src/`; DEC-804874.

## Drift Inventory

Per pattern 69, gaps between the design intent recorded above and the current state are surfaced explicitly.

| Gap | Severity | Detail |
|---|---|---|
| Only `cc-field-audit` is wired into a governed bc-core gate | Open | The other six BcAiClient invocation methods are defined but not wired into a gate that runs at a boundary act; the integration is queued |
| The trust ladder is implicit, not explicit in the schema | Open | No `trust_level` column on `l_node_semantic_trace` or `l_node_semantic_verdict`; the trust posture (deterministic-passed, single-AI-passed, cross-family-passed, human-approved) is implicit in the routing plus the agent_flow_id; AI Trust and Verification records the ladder; the schema does not |
| No automated check that a triplet's maker and checker are from different families | Open | Cross-family discipline is enforced at act registration through the model registry's per-role provider field; a future act that registers a same-family pairing is not caught by an automated assertion |
| The L-node gate fails open on infrastructure outage | Low | When bc-core or Cognito or the audit endpoint is unreachable at session close, the gate fails open; this is a deliberate choice to prevent infrastructure outage from becoming a governance failure, but it means the gate is not airtight against deliberate infrastructure-disabling attempts |
| Override rationale is not validated for content | Open | DevHub validates the rationale length (40+ characters) but not the content; an operator can supply a fabricated rationale and the override succeeds; the auditor agent may flag the override but the auditor is advisory |
| AI verdict aging policy is not declared | Open | An L-node semantic verdict that was green a month ago and has not been re-verified may have drifted; no aging policy or re-verification cadence is encoded; AI Trust and Verification records this |
| The L-node trace does not link to the bc-ai evidence row | Low | The trace records the agent_flow_id and the verdict but not the bc-ai `evidence_id`; a reader cannot follow the trace into bc-ai's full evidence trail without the agent_flow_id plus the timestamp; cross-substrate linking is queued |

**Governing source.** AI Architecture; AI Trust and Verification; AI Agents.

## Boundaries with Adjacent Chapters

| Adjacent surface | Where it lives | Why it is not this chapter |
|---|---|---|
| AI Architecture | AI section | Owns the maker-checker-gate triplet pattern. This chapter records the verdict response shape and the consumption posture; AI Architecture records the pattern |
| AI Agents | AI section | Owns the agent inventory. This chapter records that one of the twelve triplets is gate-consumed; AI Agents records the inventory |
| AI Trust and Verification | AI section | Owns the cross-family discipline and the trust ladder. This chapter records the verdict consumption; AI Trust and Verification records the trust posture each verdict carries |
| AI Usage Visibility | AI section | Owns the tenant-facing transparency surface. This chapter records that bc-ai logs per-call; AI Usage Visibility records the broader visibility gap including per-tenant accept-and-reject |
| Quality Gates and Chain Integrity | Operating Model | Owns the gate authority over runtime decisions. This chapter records that AI verdicts feed bc-core's L-node semantic gate; Quality Gates records the gate's authority over chain completeness |
| Evidence and Lineage | Operating Model | Owns the runtime proof chain at the four boundary acts. This chapter records that AI verdicts are governance, not runtime proof; Evidence and Lineage records the proof commitment |
| Audit and Activity Logging | Implementation section | Owns the operational governance trail substrate including the change record discipline at session close. This chapter records the L-node gate's consumption; Audit and Activity Logging records the substrate |

**Governing source.** Operating Model; Implementation; outline.md §4.4.

## Governing Decisions

| Decision | Title | AI gate impact |
|---|---|---|
| DEC-c06f41 | Spine expansion to eight sections plus home | The AI Gates chapter exists in the AI section per DEC-c06f41 |
| DEC-804874 | D366 L-node semantic gate at session close | The L-node semantic gate is the one hard close-blocker that depends on AI verdicts; this ADR is the chapter's central governing decision |
| DEC-bebaec | Chain Status SSOT | The chain-completeness gate substrate runs alongside the AI gate but does not consume AI verdicts; the chapter routes the chain-completeness concern to Quality Gates and Chain Integrity in Operating Model |

**Governing source.** The Authority Model.

## References

- AI Architecture
- AI Agents
- Bedrock and Inference Profiles
- AI Trust and Verification
- AI Usage Visibility
- Audit and Activity Logging
- Evidence and Lineage
- DEC-c06f41: Spine expansion to eight sections plus home
- DEC-804874: L-node semantic gate (D366)
- DEC-bebaec: Chain Status SSOT
- outline.md §4.4: AI
- Decisions: ADR Registry

