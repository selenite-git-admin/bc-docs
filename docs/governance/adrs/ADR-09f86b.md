---
uid: DEC-09f86b
title: "M12 Metric Authoring Panel — Judge role + Exhibit-ID abstraction + admissibility-scoped retrieval (replaces Moderator-as-witness shape)"
description: "Replace symmetric three-witness panel with Maker→Checker→Judge. Introduce platform-owned exhibit IDs at every model-facing boundary so raw provider tool_call_id strings never reach an LLM. Judge has admissibility-scoped read-only retrieval; verdict must cite admissible sources."
status: implemented
date: 2026-06-01T08:27:12.255Z
project: bc-core
domain: mcf
subdomain: metric-authoring-panel
focus: role-architecture
---

# M12 Metric Authoring Panel — Judge role + Exhibit-ID abstraction + admissibility-scoped retrieval (replaces Moderator-as-witness shape)

## Context

Across seven calibration panel runs (7890d35d → e128c510) the dominant residual failure was role-contract confusion: every role currently does witness work (tool calls + claims with citations) AND judge work (verdict, peer interpretation, consensus computation). Each prompt or model tightening closed one shape and immediately exposed a different shape of the same class. Failures generalised across vendors and model versions — Maker=Gemini Flash/Pro/Opus, Moderator=Opus/Gemini Pro/GPT-5.5, Checker=GPT-5.5/DeepSeek V3.2 all showed it. Separating Class 1 (mechanical drift at deterministic boundaries — addressable as plumbing) from Class 2 (role-contract confusion — only addressable architecturally) reveals that further patching of the current panel is in diminishing-returns territory for Class 2. The courtroom architecture (Maker = proposer / author; Checker = independent re-deriver — no claims of its own; Judge = reads the docket and rules) gives each role a single coherent responsibility. Combined with platform-owned exhibit IDs so raw provider tool_call_id values never reach any model, this eliminates entire failure families (cross-role borrowing, vendor-specific format chaos, ordinal miscount, alias regex sprawl) by construction rather than by prompt discipline.

## Context

The M12 panel runs three roles in sequence: Maker → Checker → Moderator. Each role's current contract conflates witness work (tool calls, claim emission with citations) and judge work (verdict, reasoning, peer interpretation). This worked while calibrating with strong models on simple metrics; it has not survived contact with real intake under varied lineups.

### Failure sequence (panel runs 7890d35d → e128c510, May 31 – Jun 1 2026)

1. **Maker = Gemini Flash → Pro → Opus.** Gemini Flash/Pro showed weak/inconsistent metric synthesis; Opus stabilised the role but introduced a stochastic ordinal miscount (`bcf_reachability_check#3` cited when only 1 such call was made).
2. **Moderator = Opus → Gemini Pro → GPT-5.5.** Opus violated three-vendor distinctness. Gemini fabricated `toolu_…`-shaped citation IDs unrelated to any real tool call. GPT-5.5 introduced a new alias family (`<tool>#<role>_<N>`) and produced the dominant violation in the meta-claim run.
3. **Checker = GPT-5.5 → DeepSeek V3.2.** GPT-5.5 stable but introduced cross-role ID borrowing; DeepSeek expanded the pattern by copying Maker's normalized claim shape verbatim including the audit `_raw` field.
4. **Mechanical drift (citation format, field names, fence extraction, ordinal counts).** Addressable at deterministic boundaries; eight progressive boundary rules (alias normalizer, broadened resolver, peer-context redaction including nested payloads, parser `statement→claim_text` alias, AJV error visibility, Checker prompt shape discipline) each closed one specific surface and immediately exposed a different surface of the same family.
5. **Role-confusion failures recurred under every lineup.** DeepSeek-as-Checker today emitted tool-grounded `claim_text` values with EMPTY `supporting_tool_call_ids` (run e128c510). The discipline correctly described claim shape but didn't prevent omission of citations — because the Checker's job is genuinely confused between "emit verified facts" and "perform verification."

The repeating pattern — fix one shape, expose a different shape of the same class — is the signature of a structural role-contract problem, not a series of independent prompt bugs.

### Two failure classes, separated

| Class | Examples | Right home |
|---|---|---|
| **Class 1 — Mechanical drift at deterministic boundaries** | citation format chaos, field-name drift, fence extraction, ordinal alias resolution, schema validation | Deterministic boundary rules (existing — keep and extend) |
| **Class 2 — Role-contract confusion** | Moderator emits own claims with own citations; Checker emits both verification AND its own claim citations; downstream roles see and copy peer real IDs | Role-shape redesign (this ADR) |

Boundary work is load-bearing and stays. This ADR is exclusively about Class 2.

### Relationship to prior ADRs

- **DEC-7f9597 (D423 — three-vendor symmetric panel)**: the three-vendor structural rule and the lineup configurability stay. The Moderator-as-witness shape it locked in is the specific element this ADR reshapes. Status of DEC-7f9597 not flipped to `superseded`; it remains the structural authority for the three-vendor invariant.
- **DEC-32a56e (D424 — context-judge principle)**: the principle ("rules are valid at deterministic system boundaries; rules are not valid as semantic judges") stays as authoritative. D424's Phase 2 v1 design (a fourth-role context judge stacked on top of the existing Moderator) is replaced by this ADR's Judge role, which replaces (not stacks atop) the Moderator. Status of DEC-32a56e not flipped to `superseded`; the principle remains the authority.

## Decision

### Role architecture: Maker → Checker → Judge

**Maker (proposer).** Largely unchanged. Loads its prompt, calls BCF / evidence tools, synthesizes a `proposal_payload`, emits `claims[]` grounded in its own tool calls. The Maker is the only role that emits `claims[]`.

**Checker (independent re-deriver).** Reshaped:

- Same closed tool surface, same independent re-derivation responsibility.
- **Drops `claims[]` from its output.** Its verification work IS its `tool_calls` audit trail (typed) and its `verification_payload.cross_check_vs_maker` (typed boolean comparisons: `grain_match`, `formula_ast_match`, `variable_bindings_match`, `temporal_gate_match`, etc.) plus `verification_payload.independent_proposal`.
- Cross-proposal observations live in `cross_check_vs_maker` only. Tool-grounded facts that back the cross-check are observable via the Checker's `tool_calls` (the model called the tool; the response is auditable). No symmetric witness/judge confusion.
- Rationale: the Checker is not a second proposer — it's an independent verifier. Asking a verifier to ALSO produce its own asymmetric claim corpus is the original sin. Removing `claims[]` from Checker output makes the role contract a single thing.

**Judge (replaces Moderator).** New role contract:

- **No witness-class tool calls.** The Judge does not search BCF, does not query evidence corpora for new facts, does not produce primary discovery. That work belongs to Maker and Checker.
- **HAS a closed, read-only retrieval surface** against allowlisted internal authority and evidence sources. Distinct in shape from the witness tool surface: returns existing, persisted, admissibility-classified records by ID or by tightly-scoped admissibility query. Produces no new substantive findings.
- **The Judge reads the full docket exclusively through model-facing exhibit IDs** (`maker.exhibit.N`, `checker.exhibit.N`, `peer_<role>.exhibit.N`). Raw provider `tool_call_id` values (`toolu_…`, `tooluse_…`, `call_…`, `gemini_fc_…`) are platform-internal audit metadata. They are persisted on `mcf.metric_authoring_panel_tool_call` for audit replay and substrate-side joins, but they are NOT exposed to the Judge's verdict-generation context. The exhibit-ID abstraction applies symmetrically to the Judge's docket-reading as it does to Maker's/Checker's own tool-result handoffs and peer-context views.
- Multi-turn allowed (retrieval-only), bounded by retrieval-call budget. Conceptually: "court library access" rather than "investigator field work."
- Single LLM family per turn; no claim emission; no exhibit emission of its own.

### Exhibit-ID abstraction

Every tool call carries two IDs:

| ID | Format | Visibility |
|---|---|---|
| `tool_call_id` | Raw provider (`toolu_…`, `tooluse_…`, `call_…`, `gemini_fc_…`) | Platform-internal: audit, persistence, deduplication. **Never reaches any model — not Maker, not Checker, not Judge.** |
| `exhibit_id` | `{role}.exhibit.{N}` (e.g. `maker.exhibit.3`), 1-indexed, sequential per role per run | All model-facing surfaces |

Where the model sees exhibit IDs:

- Its own multi-turn tool result loop: results returned to the model are labeled by `exhibit_id`, never by raw `tool_call_id`.
- Peer docket: the existing `peer_<role>_call_<N>` labels generalize to the unified `peer_<role>.exhibit.<N>` format.
- Its own grounding citations: `supporting_exhibit_refs: ["maker.exhibit.3"]` (the field name changes from `supporting_tool_call_ids` to `supporting_exhibit_refs` — the response schema reflects this as a renamed canonical field, with a documented alias for backward compatibility).

Platform-side:

- The `mcf.metric_authoring_panel_tool_call` substrate (today inside the transcript JSONB) gets extracted into a relational table with two indexed columns: `tool_call_id` (raw, audit) and `exhibit_id` (role-scoped string). Mapping is first-class data, not a sidecar in-memory structure.
- Grounding check resolves `supporting_exhibit_refs → exhibit_id → ToolCallEntry` directly. The existing alias resolver (`call_N`, `tool_call_id_N`, `<vendor_name>_<N>`, role-prefix-strip) becomes a deprecated legacy fallback for back-compat with already-persisted transcripts.

What this eliminates:

| Failure family | Before | After |
|---|---|---|
| Cross-vendor citation format chaos | 4+ raw ID formats per panel run | 1 format (`role.exhibit.N`) per panel run |
| Cross-role borrowing | "Real" `toolu_…` IDs in peer docket → copied as own | `peer_maker.exhibit.1` in peer docket → can't be a valid own citation (not in own exhibit namespace) |
| Ordinal miscount | `bcf_reachability_check#3` ambiguous (ordinal within tool_code subset) | `maker.exhibit.7` unambiguous |
| Vendor-specific alias regex sprawl | Resolver grew patterns each new vendor | Resolver becomes legacy-only |

### Admissibility classification (closed taxonomy)

Every retrievable record carries an admissibility class. The Judge's holding must cite sources by class and ID.

| Admissibility class | Source type | Authority weight | Examples |
|---|---|---|---|
| `bcf_semantic_authority` | BCF registry — **active rows only** | Highest for metric-semantic questions | `bcf.entity[entityId=…, lifecycleState=active, archived_at IS NULL]`, `bcf.business_concept[…, lifecycleState=active]`, `bcf.reachability[fromId=…, toId=…]` |
| `framework_authority` | MCF grammar, schemas, ADRs, DBCPs, foundation rules | Highest for framework/contract questions | `m12-response-schema-v2`, `DEC-32a56e`, `the-invariants.md`, `mcf-defect-registry-v1` |
| `case_evidence` | Maker/Checker exhibits from the docket | Material for the specific intake | `maker.exhibit.N`, `checker.exhibit.N`, claim records, proposal_payload field values |
| `diagnostic_evidence` | Prior panel runs for this candidate (or same reservoir_entry_id) | Contextual; informational, not binding | `mcf.metric_authoring_panel_run[panel_run_uid=…]` and joined transcripts |
| `context_evidence` | Operator-attached context, override records, change records | Binding when operator-attested; contextual otherwise | `operator_context_text`, `self_audit_json.l_node_override`, `change_record` rows |
| `external_internet` | Public web | **EXCLUDED by default.** Not in allowlist. Adding it requires explicit ADR amendment with operator approval, threat model, and rate/cost controls. | n/a |

### Retrieval layer — closed tool surface

The Judge's tool surface is small, closed, and read-only:

| Tool | Purpose | Returns admissibility class |
|---|---|---|
| `judge.read_bcf_entity({entity_id})` | Look up a BCF entity by ID | `bcf_semantic_authority` (only if active + not archived; else `inadmissible_archived`) |
| `judge.read_bcf_business_concept({concept_id})` | Look up a BCF concept by ID | `bcf_semantic_authority` (same active gate) |
| `judge.search_bcf({query, family?, domain?})` | Bounded search across active BCF rows. Requires either `family` or `domain` filter in v1. Returns at most N (~20) matches; metadata only. | `bcf_semantic_authority` |
| `judge.read_framework_source({kind, uid})` | Look up ADR / DBCP / foundation doc / schema by UID | `framework_authority` |
| `judge.read_panel_run({panel_run_uid})` | Look up a prior panel run (consensus + transcripts) for this reservoir_entry_id | `diagnostic_evidence` |
| `judge.read_change_record({ref_uid})` | Look up override records, operator notes for this intake / reservoir_entry_id | `context_evidence` |
| `judge.read_exhibit({role, exhibit_id})` | Re-read a Maker/Checker exhibit from the docket (already in context; this is for citation discipline) | `case_evidence` |

Every retrieval call is logged into the Judge's transcript (`judge_retrieval_trace`) so the audit chain shows what was reviewed.

### Judge output schema (citation-bound)

```jsonc
{
  // ───── Substance ─────
  "findings_of_fact": [
    {
      "fact_id": "f1",
      "fact_text": "≥ 40 chars",
      "supporting_sources": [
        { "class": "case_evidence", "ref": "maker.exhibit.1" },
        { "class": "bcf_semantic_authority", "ref": "bcf.entity:e3963e45-…" }
      ]
    }
  ],
  "issues_considered": [
    { "issue_id": "i1", "issue_text": "≥ 40 chars", "resolution_text": "≥ 40 chars" }
  ],
  "materiality_assessment": {
    "threshold_met": true,
    "rationale_text": "≥ 80 chars"
  },

  // ───── Holding ─────
  "holding": "APPROVE_FOR_DRAFT | OPERATOR_REVIEW | REJECT_DEFECT",
  "holding_rationale_text": "≥ 80 chars",
  "holding_relied_upon_sources": [
    { "class": "case_evidence", "ref": "maker.exhibit.1" },
    { "class": "bcf_semantic_authority", "ref": "bcf.entity:e3963e45-…" },
    { "class": "framework_authority", "ref": "DEC-32a56e" }
  ],

  // ───── Audit chain ─────
  "sources_reviewed": [
    { "class": "case_evidence", "ref": "maker.exhibit.1", "retrieved_via": "context_docket" },
    { "class": "bcf_semantic_authority", "ref": "bcf.entity:e3963e45-…", "retrieved_via": "judge.read_bcf_entity" },
    { "class": "framework_authority", "ref": "DEC-32a56e", "retrieved_via": "judge.read_framework_source" }
  ],

  // ───── Compat / legacy ─────
  "verdict_code": "APPROVE_FOR_DRAFT | OPERATOR_REVIEW | REJECT_DEFECT",
  "tie_break_rationale_text": "≥ 40 chars"
}
```

### Citation discipline rules (deterministic boundary, enforced by validator before persistence)

These are deterministic gates, not Judge judgment. They fire after the Judge emits its output:

1. **Every `holding_relied_upon_sources` entry MUST appear in `sources_reviewed`.** No silent reliance on un-retrieved sources.
2. **Every `sources_reviewed` entry MUST appear in `judge_retrieval_trace`.** No claims of having retrieved what wasn't retrieved.
3. **`holding == "APPROVE_FOR_DRAFT"` requires ≥1 `bcf_semantic_authority` AND ≥1 `case_evidence` in `holding_relied_upon_sources`.**
4. **`holding == "REJECT_DEFECT"` requires ≥1 `framework_authority` in `holding_relied_upon_sources`.**
5. **`OPERATOR_REVIEW` requires ≥1 cited source of any class.**
6. **Every cited `ref` MUST resolve at retrieval-replay time.** An archived or non-existent reference fails closed.
7. **`external_internet` class value is rejected.** Hard constraint; not configurable in v1.

### Response schema as strict, versioned contract

Schema-strict + explicitly-versioned alias list:

- Canonical field names declared in `m12-response-schema-v2.json`: `verdict_code`, `defect_code`, `reasoning_text`, `claims[].claim_text`, `claims[].supporting_exhibit_refs`, `proposal_payload`, `verification_payload`, `judge_payload` (new).
- Aliases that the parser accepts are **declared in the schema**, not hidden in a normalizer. Today's working aliases (`claim → claim_text`, `statement → claim_text`, `supporting_tool_call_ids → supporting_exhibit_refs`) become documented entries in the schema's alias table, version-bound to v2.
- Any field NOT in canonical-or-documented-alias set is a schema violation. Fail closed.
- Prompt includes `"respond per the m12-response-schema-v2 contract"` so models see the contract version they're held to.
- New vendor drift requiring a new alias → schema version bump (v2 → v3), documented, ADR-tracked. No silent normalizer growth.

### Citation existence vs semantic support — refining D424

The operator-stated refinement is adopted as the durable rule:

> **Citation existence is deterministic. Semantic support is judgment.**

| Question | Adjudicator |
|---|---|
| "Does this `supporting_exhibit_ref` resolve to a real exhibit in this role's tool_calls?" | Deterministic — the grounding check (exhibit-ID lookup). Fails closed. |
| "Does the cited tool response contain at least one ≥4-char claim_text token?" (strict path) | Deterministic — substring scan. Useful as a heuristic guard. |
| "Does the cited evidence MATERIALLY support the claim?" | Judgment — the Judge's `materiality_assessment`. |

The deterministic gate stays as today's strict/loose policy. The Judge's `materiality_assessment` is a higher-confidence semantic layer ON TOP of the gate. The Judge cannot accept a claim whose citation fails the deterministic existence check. The Judge CAN demote a claim whose citation passes existence but whose substance the Judge finds materially insufficient. Demotion produces OPERATOR_REVIEW, not REJECT_DEFECT.

This formalizes the existing `approve_with_loose_grounding` policy as one specific case of the broader materiality framing: loose-grounding IS the deterministic gate's signal that semantic judgment is required, and the Judge is the role that exercises it.

## Consequences

**Adapter changes.** Every vendor adapter (Anthropic, OpenAI, Google, Bedrock) translates `exhibit_id ↔ tool_call_id` at the tool-result handoff boundary. ~50 LoC per adapter. Existing tests cover the contract; specs need extension for exhibit-ID round-trip.

**Schema changes.**
- New `m12-response-schema-v2.json` with canonical field names + documented alias table.
- New `judge-output-schema-v1.json` matching the Judge output structure above + post-emit citation validator (HA-8 analogous to today's HA-7 `assertConsensusPayloadShape`).
- `Checker` output schema loses `claims[]` (soft deprecation in v2; hard reject from v3).

**Substrate changes.**
- New `mcf.metric_authoring_panel_tool_call` (extracted from current JSONB blob into a relational table) with `(panel_run_uid, role, exhibit_id, tool_call_id, tool_code, …)` columns. Indexed both `exhibit_id` and `tool_call_id`. DBCP-tracked.
- New `judge_retrieval_trace` JSONB column on `mcf.metric_authoring_panel_run` for Judge audit chain.
- Persisted transcripts on existing rows continue to be readable under legacy resolver. New rows use exhibit IDs natively.

**New infrastructure.** `JudgeRetrievalService` — closed read-only service in `bc-core/src/registry/mcf/judge-retrieval/`. Implements the 7 retrieval tools listed above. Enforces the admissibility allowlist. Logs every call to `judge_retrieval_trace`. Returns admissibility-classified records or `inadmissible_*` codes (never raw inadmissible data).

**Consensus computation changes.**
- Today: vote arithmetic (3× APPROVE + grounding pass = APPROVE) with the `approve_with_loose_grounding` downgrade.
- After: the Judge's `holding` IS the consensus verdict. Maker/Checker verdicts are docket evidence for the Judge. `approve_with_loose_grounding` becomes a Judge-side input ("the strict gate flagged loose grounding; assess materiality") rather than a hard downgrade.

**Token cost.** Net neutral to slightly positive. Maker + Checker unchanged. Judge multi-turn retrieval bounded; estimated ~6–12k input tokens + ~2–4k output tokens; ~5–8 retrieval turns per typical case. Cheaper than today's Moderator with peer transcripts because the Judge doesn't redo Maker/Checker tool exploration — it spot-checks.

**Failure path.** If the Judge times out mid-retrieval loop or emits an output that fails the citation-discipline validator, the panel run resolves to OPERATOR_REVIEW with `operator_review_reason: judge_validation_failed` and a structured `judge_validation_errors[]` field. The retrieval trace is persisted regardless of validator outcome so post-failure debugging is possible.

**Migration.** Implementable as a parallel role. The existing Moderator code stays for one release cycle, deprecated. Service supports both modes via env var (`MCF_M12_USE_JUDGE_ROLE`). Existing persisted panel runs remain readable under legacy resolver semantics. First panel run on the new architecture is the durability proof.

**What this does NOT change.**
- The boundary citation normalizer.
- The peer-context redaction (generalized to exhibit IDs).
- The strict/loose grounding policy (re-framed as input to Judge materiality).
- The intake → panel-run substrate flow.
- M12.5 materialization (Judge's `holding == "APPROVE_FOR_DRAFT"` triggers it; otherwise identical).

## Open questions for operator decision before implementation

1. **Retrieval-call budget.** Hard cap on `judge_retrieval_trace.length`. Recommended: 12 per panel run, with `operator_review_reason: judge_retrieval_budget_exceeded` on overflow. Sized to allow looking up 3-4 BCF entities + 2-3 framework sources + a couple prior-run lookups without becoming an oracle.
2. **`judge.search_bcf` archive policy.** Recommended: filtered out at the retrieval layer; never returned to the Judge. Archived rows are not admissible authority for new metrics.
3. **Concurrent retrieval within one Judge turn.** Recommended: sequential in v1 — simpler audit trail; the Judge's turn budget is the real ceiling anyway.
4. **Judge vendor binding.** Three-vendor distinctness preserved. Proposed: Maker = Anthropic, Checker = Bedrock, Judge = OpenAI. Operator confirms.
5. **Checker `claims[]` deprecation path.** Soft (warning) for one release; hard (schema reject) from response-schema v3.
6. **`approve_with_loose_grounding` semantics under Judge.** Today: hard downgrade. Under Judge: input signal to Judge `materiality_assessment`, not a string-policy downgrade. Operator confirms this isn't policy weakening — the Judge can still demote loose-grounded approvals; it just does so via materiality finding rather than a string-policy match.

## Companion artifacts

- **Override evidence packet** for `customer_invoice_count` intake `64349d2a-c0ff-493c-b87c-bdacb2691542` — drafted, awaiting separate operator authorization to file via `devhub_change_record_save`. Override is one-shot, scoped to this intake, non-precedential, and conditioned on the Judge architecture landing before any second metric is overridden.

- **Follow-up tasks auto-spawned on override packet filing** (5):
  - `judge-architecture-pending` — implement Judge role per this ADR
  - `exhibit-id-pending` — implement exhibit-ID abstraction per this ADR
  - `judge-retrieval-layer-pending` — implement closed read-only JudgeRetrievalService + `judge_retrieval_trace` substrate + admissibility-classified retrieval outputs
  - `judge-durability-proof` — re-run `customer_invoice_count` on Judge architecture without override
  - `checker-claims-deprecation` — reshape Checker output schema (remove `claims[]`)
