---
uid: DEC-cff0cf
title: "ABC = Autonomous Business Chain — deterministic orchestrator over governed factories + bounded retrieval-first reasoning panel"
description: "Defines ABC as the autonomous reasoning + orchestration surface closing the gap between BCF (vocabulary) and MCF (metric). Orchestrator runs deterministic FSM over CEE / Harness / CAS / BCF panel / MCF panel; Panel is a bounded retrieval-first Maker/Checker/Judge sub-surface for chain-shape decisions per (metric × source_family). Includes prompt-caching NFR. Filed as proposed."
status: decided
date: 2026-06-16T15:20:36.417Z
decided_date: 2026-06-17
project: bc-core
domain: platform
subdomain: chain-engines
focus: governance
---

# ABC = Autonomous Business Chain — deterministic orchestrator over governed factories + bounded retrieval-first reasoning panel

## Context

D445 / D446 / D447 cover apply, verify, and doctrine for sequencing but do not name who decides chain shape per source family. The Track B FSCM session (SES-9184c0, 2026-06-16) surfaced this concretely: a multi-table SC v1.1 was grammar-refused; the alternative (new SCMG SC) is a chain-shape modeling decision with cross-source-family implications that should live as governance artefact, not as session-level notes. Two earlier framings were rejected during design (ABC as one-shot panel — too narrow; ABC as free-form agent loop — breaks replayability). Synthesis: orchestrator + bounded reasoning sub-surface. Drafted across 11 held packets in SES-9184c0; filed proposed for Phase 0 hand-emulation pilot against ≥ 3 specimens including non-SAP rotation.

# ABC = Autonomous Business Chain — deterministic orchestrator over governed factories + bounded retrieval-first reasoning panel

## Context

The platform ships three locked chain-engine ADRs:
- **DEC-1fa08f / D445** — Chain Audit Service (CAS): read-only verifier, 5-mode lifecycle gating.
- **DEC-739e23 / D446** — Chain Enrichment Engine (CEE): planner-only over harness governed-apply; deterministic; never authors human-judgment content.
- **DEC-e01fcf / D447** — Chain enrichment doctrine: 8 principles, R(M) partition rule, source-identity placement, halt vocabulary, topological order.

Together these cover **apply**, **verify**, and **doctrine for sequencing**. They do not name **who decides chain shape per source family** — i.e. who reasons about whether a metric is observable from a given ERP, which source surfaces must be governed-contracted, which BCs are R(M) vs O(M), and what amendment ladder unblocks a missing chain.

In the Track B / FSCM `disputed_invoice_count` work (SES-9184c0, 2026-06-16), that gap surfaced concretely:
- The original repair plan would have hand-authored an SC + AC + OC amendment chain, treating reasoning as a session-level note.
- Rung 1 then discovered `source-v1.schema.json` is "one SC per source table" — the proposed multi-table v1.1 shape is grammar-refused.
- The natural alternative (`sc__sap_scmg_case_status` as a new SC) is not a mechanical patch; it is a chain-shape modelling decision with cross-source-family implications.
- Hand-authoring the choice consumes the reasoning that the platform should preserve as governance artefact.

This is the work ABC owns. ABC sits between BCF Panel (business vocabulary decisions) and MCF Panel (metric contract decisions), and reasons about **chain shape per `(metric × source_family)` pair**.

Two earlier framings were considered and rejected during this session:
- **"ABC Panel" as a single reasoning surface that emits one decision and halts** — rejected because a panel that stops at "missing BC" is a smarter CAS, not autonomy. The chain must run to completion or to an explicit halt.
- **"ABC Agent" as a free-form SDK-style tool-using LLM loop** — rejected because it breaks replayability at the orchestration seam, fights every governance lock D446 / D447 introduced, and creates two LLM contexts (orchestrator + factory) reasoning about the same gap with no protocol.

The synthesis: ABC is an **orchestrator with a bounded reasoning sub-surface** — deterministic where mutation happens; LLM-backed only where contextual judgement is genuinely required.

## Decision

Adopt **ABC = Autonomous Business Chain**, with the following two-part structure:

- **ABC Orchestrator** — a deterministic finite-state control loop with an append-only run journal. Reads gap state from `mcf.chain_enrichment_plan`, `contract.chain_status`, `mcf.chain_audit_evidence`, and the ABC run journal itself. Advances FSM transitions via typed dispatch rules. Calls governed factories (CEE / Harness / CAS / BCF panel / MCF panel) with typed DTOs. Halts on a finite stop vocabulary. **No LLM at the loop layer.**
- **ABC Panel** — a bounded retrieval-first Maker / Checker / Judge reasoning surface, invoked by the orchestrator only when contextual or domain judgement is required. Inputs are a typed context pack (see §"Context-pack contract"). Outputs are a structured chain decision conforming to a closed YAML shape with citations + confidence bands. The panel never writes contract substrate, never authors operator-only content, never reasons outside its context pack.

### Locked decisions

| D | Topic | Choice |
|---|---|---|
| **D1** | ABC composition | **ABC Orchestrator (deterministic FSM + run journal)** + **ABC Panel (bounded reasoning sub-surface)** — together, not separately. Either alone fails the autonomy goal |
| **D2** | Orchestrator class | Deterministic finite-state machine. Plain TypeScript at loop layer. **No LLM at the orchestration seam.** FSM transitions are typed rules over the run journal + substrate snapshot hash + CAS evidence |
| **D3** | Panel formation | **Option D — retrieval-first then Maker / Checker / Judge.** Four phases per panel invocation: Retrieval (typed evidence bundle assembly), Maker (chain shape proposal from cited evidence), Checker (adversarial verification against substrate citations + grammar schemas + Foundation invariants + D447 stops), Judge (synthesis per D447 §D7) |
| **D4** | Context-pack contract | Closed typed input set: target_metric, mc_body (if exists), source_family registry entry, current SC/AC/OC/CC bodies (hashed), BCF concept snapshot (hashed), recent CAS findings, prior ABC decisions, source reference docs (cited), Foundation + ADR doctrine (pinned), the specific `gap_class` + `gap_context`. Closed output YAML shape per the design discussion §6 |
| **D5** | Confidence model | **5 bands:** `deterministic` (substrate + grammar), `well-grounded` (cited reference + substrate cross-check), `inferred_from_pattern`, `operator_judgment_required`, `not_decidable_with_current_evidence`. **Halt threshold: `well-grounded` minimum** for any output section the orchestrator's next deterministic step depends on |
| **D6** | Stop vocabulary | 17 finite-state stop codes, all checkable from run journal + substrate hash + CAS evidence (no LLM-judgement stops at orchestration layer). See §"Stop conditions" |
| **D7** | Source-capability verdict vocabulary (v0) | **3 verdicts** at `platform_source_capability.verdict` — closed enum: `supported_directly`, `supported_with_amendment`, `not_observable`. v0 output MUST reject any other value at this field. The labels `supported_with_tenant_extension` and `supported_via_external_source` appeared in earlier same-day drafts of this ADR and have been **RETIRED as v0 verdicts** (they led to the Foundation tenant-scope leak the same-day correction addressed). Tenant-extension and external-source possibilities are surfaced only under `future_enablement_paths[]` with a different field (`path_kind`) and different vocabulary (`tenant_extension`, `external_source`, verb-free) — see §"ABC output contract". `not_observable` is a **first-class terminal success state** — forced universality is forbidden (Foundation Invariant VI). Final acceptance still operator-confirmed |
| **D8** | Boundary commitments (negative space) | Nine rules that prevent CEE overreach + panel authoring of operator-only content + BCF/MCF authority erosion. See §"Boundary commitments" |
| **D9** | Cross-repo execution + caching | **bc-core-owned panel; optional bc-ai transport** (Pattern A-like; aligns with the MCF M12 precedent, NOT the BCF B6 delegation pattern). bc-core owns the orchestrator, the Maker/Checker/Judge role prompts, context-pack assembly, role sequencing, output schema validation, the scoring rubric, the run journal, citation tracking, and stop-code emission. bc-ai (if used at all) is a model transport / vendor gateway only — it MUST NOT own ABC doctrine, prompts, schema, or decisions. Cache layout follows the 4-slot model from the held caching packet §1, owned and emitted by bc-core; bc-ai cache passthrough is optional follow-up, not a prerequisite. **ABC implementation must be cache-aware from day one.** Source-family literals forbidden in Slot 1 + Slot 2; enforced bc-core-side by CI |
| **D10** | Promotion path | `proposed` ADR (this document) → Phase 0 hand-emulation on 3+ specimens → Phase 1 prompt-only panel → Phase 2 retrieval-assisted panel → ADR promoted `proposed` → `decided` only after pilot conditions §"Promotion path" pass |

### ABC Run Request

Every ABC orchestrator invocation is driven by a typed run request. Specimen labels like `disputed_invoice_count × SAP FSCM` or `disputed_invoice_count × Zoho Books` used elsewhere in this ADR (and across the held packets) are **shorthand for a typed `abc_run_request`, not free-form labels**. The canonical shape:

```yaml
abc_run_request:
  target_metric:
    metric_name: string
    metric_intent: string
    stage: seed | draft_mcv | active_mcv
    seed_metric_id: optional
    mcv_uid: optional
  source_family:
    provider: string         # e.g. "sap", "oracle", "zoho", "intuit", "external"
    product: string          # e.g. "s4hana_fscm", "fusion_ar", "books", "quickbooks_online"
    version_or_api: optional # e.g. "v3", "2024-11", "ECC6"
  tenant_context:            # optional; when absent, run scope is platform-level
    tenant_id: optional
    tenant_source_config_ref: optional      # pointer to tenant's source-config artefact
    custom_field_registry_ref: optional     # pointer to tenant's custom-field manifest
    external_source_refs: optional          # list of external systems the tenant uses for joins
  requested_scope:
    decide_source_capability: boolean
    propose_chain_path: boolean
    do_not_write: true       # ABC invocations never authorise mutation
```

The request is the orchestrator's typed input contract. Three properties follow:

1. **Target × source × tenant** is the run identity. Two runs differ if any element differs. Specimen #2 (Zoho Books) showed that without `tenant_context`, the source-capability verdict cannot be fully resolved when tenant configuration controls observability (custom dispute fields).
2. **`tenant_context` is contextual only in v0; it does not authorise tenant-scoped contract modelling.** Per Foundation, tenant-scoped variation lives at the Contract Binding layer (`the-contract-grammar.md` line 311 — Tenant Override "cannot remove platform-declared fields or modify platform-declared rules"; line 313 — "Tenant customization occurs only at the Contract Binding layer"). Contract Binding is a grammar instance, not an authoritative object (`the-object-model.md` line 226). ABC v1 has no factory wired to Contract Binding authoring; the Non-goals section reserves tenant-scope reasoning to a future ADR. In v0, the panel may **observe** that `tenant_context` would change the picture, but **cannot emit a proceed verdict that depends on Contract Binding authoring or external-source onboarding**. When `tenant_context` is provided in v0, the panel records it for analytic colour only; it does not authorise the orchestrator to dispatch toward any tenant-scoped factory. The panel records the absence as `tenant_context_unknown` (or `tenant_context_observed_advisory` when present-but-non-routable) in the run journal.
3. **`requested_scope.do_not_write` is fixed `true`.** ABC never authorises substrate writes. The orchestrator records decisions; governed factories (Harness, BCF/MCF panels via their own confirm surfaces) write under operator authorisation.

### ABC Orchestrator — the loop

```
read target_metric_uid
  ↓
load substrate_snapshot_hash + run_journal_state
  ↓
classify_gap(substrate, run_journal) → gap_class
  ↓
if gap_class ∈ {sc_missing, ac_missing, oc_missing, oc_not_applyable,
                cc_field_selection_incomplete, mc_authorship_required,
                cas_verdict_red, value_map_authorship_pending}
   → call deterministic factory (CEE / Harness / CAS) via typed DTO
if gap_class = chain_shape_semantic
   → assemble context_pack → call ABC Panel → record decision
   → advance per orchestrator_next_action emitted by panel
if gap_class = bcf_concept_missing_for_rm
   → call BCF Panel via existing /api/ai/suggest/registry-authoring
if gap_class = mc_authorship_required AND chain_complete
   → call MCF Panel
if gap_class ∈ stop_set → halt with stop_reason
if gap_class = none AND CAS green AND MC active → terminal_green_metric_ready
  ↓
write run_journal entry (one row per FSM transition)
  ↓
loop until terminal or stop
```

The classifier is plain code. Each transition is a typed rule with a single dispatch target.

### ABC Panel — Option D phases

| Phase | Scope | Allowed outputs | Forbidden outputs |
|---|---|---|---|
| **Retrieval** | Assemble typed evidence bundle from substrate (cheap reads, hashable), doctrine (static, pinned), source-family reference docs (dynamic, citation-required) | Typed evidence bundle with citation tuples on every claim | Inventing citations; substituting general knowledge for cited reference |
| **Maker (Chain Architect)** | Propose chain shape — required surfaces, R(M) / O(M) BCs, SC/AC/OC amendment plan options (typically α' / α'' / α'''), OC body intent (without authoring `value_map` content), source-capability verdict | Proposal with explicit per-section confidence | Authoring `value_map` / `canonical_value_set` / `semantic_role` content; choosing between operator-decision options without halt |
| **Checker (Source + Grammar)** | Adversarially verify Maker output — substrate citations hashable; grammar validation against `source-v1.schema.json` + `admission-v1.schema.json` + `observation-v2.schema.json`; Foundation Invariants I, IV, VI; D447 §P5, §P8; vendor citation strength | Verdict per Maker claim; confidence downgrades on weak citation | Inventing source evidence Maker did not cite; overriding the Maker's structural finding (escalates to Judge) |
| **Judge (Doctrine)** | Synthesise per D447 §D7 — emit `orchestrator_next_action` from a closed set; attach citations + confidence breakdown; emit `stop_reason` if any output section below threshold | Final structured decision; routing decision for the orchestrator | Authoring operator-only content; overriding Foundation invariants; inventing new halt vocabulary |

### Context-pack contract

Typed inputs per panel invocation:

| Element | Source | Notes |
|---|---|---|
| `target_metric` | `mcf.seed_metric` row | Includes `formula_hint`, `function_code`, `subfunction_code` |
| `target_metric_mc_body` (if exists) | `metric.metric_contract_version` | Authoritative R(M) source when present |
| `source_family` registry entry | `source.source_system` | Capability flags, registered Reader bindings |
| `current_sc_bodies` for source_family | `contract.source_contract_version` (active + draft) | Verbatim bodies + content_hash |
| `current_ac_bodies` for source_family | `contract.admission_contract_version` (same scope) | Same |
| `current_oc_bodies` for source_family | `contract.observation_contract_version` (same scope) | Same |
| `current_cc_bodies` for affected CC | `contract.canonical_contract_version` | Where relevant |
| `bcf_concept_snapshot` | `concept_registry.*` (active, non-archived, candidate entities) | Hashed |
| `cas_findings_recent` for target | `mcf.chain_audit_evidence` | Most recent verdict per applicable mode |
| `foundation_doctrine` | Foundation chapters + D447 + D446 + D445 + D431 + D441 | Static; pinned by hash |
| `source_reference_docs` | Operator-curated knowledge base (SAP Help, Oracle docs, Zoho API docs, OAGIS, ISO 20022) | **Citation tuple required on every reference** |
| `prior_abc_decisions` | ABC run journal (when persistence ships) | Drift / repeat-blocker detection |
| `gap_class` + `gap_context` | Orchestrator FSM state | Bounds panel scope to one gap class per invocation |

**Negative evidence is real evidence.** Searches that return "no native dispute mechanism found in Zoho API" are recorded with their own citation tuple. The panel must support emitting `not_observable` from cited absence — see D7.

### ABC output contract

Per invocation, the panel returns a structured decision conforming to the YAML shape pinned in the held design discussion §6 (combining consolidation §7 fields with `orchestrator_next_action`, `orchestrator_next_action_args`, content_pack_hash, and per-role summaries). Required sections (each may be empty):

- `platform_source_capability` — **single platform-level verdict**, hard-typed enum:

  ```yaml
  platform_source_capability:
    verdict: supported_directly | supported_with_amendment | not_observable   # closed enum
    confidence: <band from D5>
    citation: <citation tuple, optional>
  ```

  These are the **only** values v0 accepts at `platform_source_capability.verdict`. The labels `supported_with_tenant_extension` and `supported_via_external_source` MUST NOT appear here; they were retired as v0 verdicts (see D7) and have no place in this field. The orchestrator routes only on this verdict. When `verdict = not_observable` with confidence ≥ `well-grounded`, the orchestrator emits `terminal_not_observable`. Final acceptance still operator-confirmed.

- `future_enablement_paths[]` — **advisory list, NOT routable by ABC v0.** Each entry names a path that would change the platform verdict if wired in a future ADR. Hard-typed entry shape:

  ```yaml
  future_enablement_paths:
    - path_kind: tenant_extension | external_source   # closed enum, intentionally distinct from `verdict`
      current_status: out_of_v0_scope                  # constant in v0
      required_future_design: <one-sentence description of the future ADR/wiring needed>
      not_routable_by_abc_v0: true                     # constant in v0; runtime assertion
      rationale: <why this path could enable the metric>
      preconditions: [<preconditions that must hold before the path is reachable>]
      operator_decision_class: out_of_v0
  ```

  **Field discipline:**
  - `path_kind` is a closed enum **distinct from `platform_source_capability.verdict`**. Its values (`tenant_extension`, `external_source`) intentionally do NOT carry a `supported_with_` prefix — they are path classifications, not verdicts.
  - `current_status` is the constant `out_of_v0_scope` in v0. Future ABC versions may introduce other values (e.g. `wired_in_v_n`).
  - `required_future_design` names the work that would have to land first (e.g. "Contract Binding authoring factory + tenant value_map authority surface"; "Secondary source-system registration + external-source contract chain").
  - `not_routable_by_abc_v0: true` is a **runtime assertion** the orchestrator may check before dispatch. Any code path attempting to route on a `future_enablement_paths[]` entry fires the assertion and the dispatch is blocked.

  The orchestrator does not dispatch a factory call based on `future_enablement_paths[]`; the panel surfaces them as analytic colour for an operator decision. Example:

  ```yaml
  platform_source_capability:
    verdict: not_observable
    confidence: well-grounded
    citation: <vendor_doc_tuple>
  future_enablement_paths:
    - path_kind: tenant_extension
      current_status: out_of_v0_scope
      required_future_design: Contract Binding authoring factory + tenant value_map authority surface
      not_routable_by_abc_v0: true
      rationale: Vendor exposes a tenant-extensible custom-field surface that a
                 configured tenant could use to emit dispute evidence
      preconditions:
        - Contract Binding-layer authoring wiring (out of ABC v1 scope; future ADR)
        - Per-tenant configuration manifest
        - Tenant value_map authoring under tenant authority
      operator_decision_class: out_of_v0
    - path_kind: external_source
      current_status: out_of_v0_scope
      required_future_design: Secondary source-system registration + external-source contract chain
      not_routable_by_abc_v0: true
      rationale: An external helpdesk / CRM dispute system could carry the
                 evidence and join to invoices via a documented key
      preconditions:
        - Secondary source-system registration under existing source-onboarding
        - External-source contract chain authored separately
      operator_decision_class: out_of_v0
  ```

  **Replaces the per-tenant-segmented `source_capability` shape used in earlier drafts.** Per Foundation (`the-contract-grammar.md` §Three-level governance; `the-dual-layer-interaction-model.md` §AI Interaction With The Trust Surface), ABC cannot emit a proceed verdict whose execution depends on Contract Binding authoring or external-source onboarding in v0. The split shape — different field, verb-free vocabulary, explicit `not_routable_by_abc_v0: true` flag — lets the panel surface those future paths honestly without giving any reader a textual surface that could be mistaken for a routable verdict.
- `required_source_surfaces[]` — tables / objects / endpoints + `declared_in_current_sc` bool + citation
- `required_bcs[]` — concept_id + role (`identity` / `predicate` / `temporal`)
- `optional_bcs[]` — same shape
- `sc_amendment_plan` — option enumeration with grammar-compliance verdict
- `ac_amendment_plan` — depends on SC choice
- `oc_authoring_plan` — `source_references[]` + `field_mappings[]` (intent only on `value_map`)
- `value_map_decision` — per `code_lookup` entry: intent + `authorship_status`
- `stop_reason` — from the closed vocabulary in §"Stop conditions"
- `confidence_breakdown` — per-section band
- `provenance` — cited substrate rows + cited files + cited doctrine sections + cited vendor docs + cited prior decisions
- `orchestrator_next_action` — closed enum: `call_cee` | `call_bcf` | `call_mcf` | `call_harness` | `call_cas` | `halt_operator_decision` | `halt_operator_content` | `terminal_not_observable` | `halt_platform_grammar_amendment_required` | `halt_repeat_blocker`
- `orchestrator_next_action_args` — typed DTO for the chosen factory

### Boundary commitments

The nine negative-space rules that hold the architecture together. Each is enforced by code + CI test + audit.

| # | Rule | Effect |
|---|---|---|
| **B1** | CEE never carries source-family knowledge | CEE planner version stays single-track. No `cee-sap-vN`, no `cee-zoho-vN`. CEE is source-agnostic forever |
| **B2** | CEE never computes R(M) from source observability | CEE's R(M) sources are exactly two: MC body (authoritative) or ABC pre-MC R(M) lock (when MC absent). CEE refuses to plan if neither is present |
| **B3** | CEE never decides source-capability verdict | The five verdicts (`supported_directly` etc.) live only on ABC decisions |
| **B4** | ABC Orchestrator does not free-form call tools | FSM transitions are typed rules; factory calls carry typed DTOs validated against factory schemas |
| **B5** | ABC Panel does not author `canonical_value_set` / `value_map` / `semantic_role` content, and does not resolve BC ambiguity between candidate concepts | Mirrors D447 §D7 one layer up. Panel emits structured halt; operator authors content or resolves ambiguity |
| **B6** | ABC never bypasses governed services | All factory calls go through existing governed HTTP surfaces. No special DB privileges; no direct mutation of `contract.*` / `concept_registry.*` / `mcf.*` |
| **B7** | Harness remains the single contract writer | ABC does not author contract row content via free text. Harness applies governed packets |
| **B8** | CAS remains the read-only verifier | ABC reads CAS findings; ABC never authors CAS evidence; CAS continues to gate M13 / M14 unconditionally |
| **B9** | BCF Panel and MCF Panel retain authoritative ownership of their respective decision domains | BCF Panel owns business-concept vocabulary decisions (entity / characteristic / BC / canonical_value_set authoring evidence). MCF Panel owns metric-contract decisions (formula AST, grain, filters, variable bindings). ABC routes to each via existing governed surfaces (e.g. `/api/ai/suggest/registry-authoring`); ABC never substitutes its own judgement for BCF or MCF outputs |

These rules apply at the orchestration layer too — not only at the panel. The orchestrator code itself must not carry source-family literals (the prompt anti-regression principle extends to TypeScript constants).

### Stop conditions (finite-state)

17 closed codes. All checkable from run journal + substrate snapshot hash + CAS evidence + panel decision. No LLM-judgement stops at orchestration layer.

| Stop code | Rule |
|---|---|
| `same_gap_repeat_under_substrate_hash` | Same `gap_class` for same `target_metric_uid` appears > **3** times in run journal within a window where substrate snapshot hash unchanged |
| `panel_confidence_below_well_grounded` | Latest panel decision has any section at `inferred_from_pattern` or below |
| `bcf_panel_cannot_decide` | BCF panel returned its own halt verdict |
| `mcf_panel_cannot_decide` | MCF panel halted at its own boundary |
| `operator_value_map_required` | Latest panel `value_map_decision.value_map_authorship_status = operator_authorship_pending` |
| `tenant_extension_out_of_scope` | Panel reasoning identified that the chain would be enabled by a tenant-scoped artefact (custom-field z_extension, tenant-defined value_map, or any other Contract Binding-layer artefact). Per Foundation (`the-contract-grammar.md` §Three-level governance; `the-object-model.md` line 226), tenant customisation lives only at the Contract Binding layer, which is a grammar instance — not an authoritative object — and is not wired in ABC v1 (see Non-goals). Halt routes to operator decision on whether the metric will be supported at all for this source family. **Replaces the earlier `tenant_value_map_required` code, which implied a wired tenant authoring path that does not yet exist.** |
| `external_source_out_of_scope` | Panel reasoning identified that the chain would be enabled by joining a secondary external source (e.g. helpdesk / CRM dispute system) that is not currently registered as `source.source_system`. Distinct from `source_system_registration_required` (which is about the **primary** `source_family` of the run request); this code names a **secondary external source** the operator would have to onboard before that path is reachable. Out of v0 routing scope; advisory only |
| `operator_canonical_value_set_required` | Panel flagged missing canonical_value_set on a BC in R(M) |
| `operator_semantic_role_required` | Panel reasoning depended on a new BC's `semantic_role` |
| `operator_bc_ambiguity_resolution_required` | Panel reasoning required choosing between two or more candidate BCs for the same role in R(M); operator must resolve identity per D447 §D7 |
| `source_evidence_unavailable` | Checker rejected Maker's source citations and Maker cannot recover with the available context pack |
| `source_system_registration_required` | The `abc_run_request.source_family` does not resolve to a registered `source.source_system` row on the platform. **This is a source-onboarding gap, not a chain-contract gap** — the platform has no current binding for this source family. Distinct from `source_evidence_unavailable` (which is about specific vendor doc retrieval). Halt routes to operator-direct source registration (out of ABC orchestrator's factory set) |
| `cas_fail_after_repair_attempt` | CAS returned `FAIL` or `OPERATOR_REVIEW` on the target on the iteration immediately following a factory write intended to repair the prior CAS finding |
| `terminal_not_observable` | Panel Judge emitted `not_observable_in_this_source = true` with confidence ≥ `well-grounded`; **terminal success state** |
| `platform_grammar_amendment_required` | Checker detected all Maker proposals would require a contract-grammar amendment (e.g. multi-table SC under source-v1) — **out of orchestrator scope**; halt for a separate ADR |
| `max_loop_iterations` | Total loop iterations for this target exceeded **30** (mirrors D446 Rules-6) |
| `green_metric_ready` | All applicable CAS modes return `PASS`, MC active, no open gaps; CAS produced an `M14-ready` verdict — **terminal success state** |

### Prompt caching and context budget — NFR

Per the held caching packet and cross-repo audit (both filed under `.claude/` in SES-9184c0):

#### Execution pattern

ABC is **bc-core-owned (Pattern A-like)**. bc-core hosts the orchestrator, the panel role prompts (Maker / Checker / Judge), context-pack assembly, role sequencing, output schema validation, the scoring rubric, the run journal, citation tracking, and stop-code emission. bc-ai (if used at all) is a model transport / vendor gateway only — it does **NOT** own ABC doctrine, prompts, schema, or decisions.

This aligns ABC with the **MCF M12 Pattern A precedent** (per-vendor adapter directly in bc-core), **NOT** the BCF B6 Pattern B (bc-ai owns vendor execution end-to-end). The realignment reflects ABC's substantial doctrinal surface — the 17-code closed stop vocabulary, the 8-field scoring rubric, the 3-verdict closed enum at `platform_source_capability.verdict` with two retired labels, the `future_enablement_paths[].path_kind` closed enum, Foundation Invariant I/IV/VI Checker checks, the retired-label discipline, source-family rotation discipline, output schema validation, and the run journal shape — which belongs to the platform team (bc-core), not the model-transport team (bc-ai).

Doctrine ownership at the model-transport layer would be a category error: a change to D448's halt vocabulary or closed enum would require a bc-ai PR, and the CI prompt anti-regression for forbidden source-family literals would run in the bc-ai pipeline rather than bc-core's. Per the original cross-repo audit's §1.4 caveat ("if ABC needs deterministic substrate access or grows its doctrinal surface, some shape of Pattern A may re-emerge"), Phase 0 and Phase 1 have matured ABC into Pattern A territory.

#### Cache layout (4-slot)

Required per panel role invocation:

| Slot | Content | TTL | Hierarchy position |
|---|---|---|---|
| **Slot 1** | Role prompt (Maker / Checker / Judge), output schema, confidence bands, stop vocabulary, source-capability verdict vocabulary, source-family-NEUTRAL examples | 1-hour | `system` (top) |
| **Slot 2** | Doctrine bundle — Foundation invariants, D447 sections, D446 Rules-1, D445 Two-Person Rule, schema excerpts for SC/AC/OC grammar checks | 1-hour | `system` (after Slot 1) |
| **Slot 3** | Source-family bundle — vendor schema doc excerpts for current `source_family`, source registry entry, capability matrix | 5-minute (or 1-hour batched) | `system` (after Slot 2) |
| **Slot 4** | Substrate snapshot + retrieval evidence — current SC/AC/OC/CC bodies, BCF snapshot, CAS findings, prior ABC decisions | 5-minute | `messages` (early user-turn) |
| **(L5)** | Per-invocation operator request + gap context + timestamps | **NOT cached** | `messages` (last user turn, post-breakpoint) |

#### Discipline locks

- **No source-family literals in Slot 1 + Slot 2.** CI prompt anti-regression test (forbidden-literal list: SAP / Oracle / Zoho / SCMG / PSTAT / BLART / BUKRS / UDM_* etc.) enforced.
- **Slot 1 must clear the model's minimum cacheable prefix size.** Opus 4.7 = 2048 tokens. Padding uses source-family-neutral doctrine text only.
- **Slot 3 is keyed per `source_family`.** Tenant-specific evidence is not cached at organisation scope (v1 is platform-scope only; tenant-scope deferred until workspace isolation is on the chosen provider path).
- **Slot 4 carries `substrate_snapshot_hash`.** Substrate writes invalidate the slot by hash mismatch — no stale read possible.
- **Content_hash on every slot.** bc-core computes; bc-ai validates that the assembled content matches.

#### Telemetry

Every ABC panel LLM call records: `cache_creation_input_tokens`, nested 5m / 1h breakdown, `cache_read_input_tokens`, `input_tokens`, `output_tokens`, role identity, `cache_breakpoint_layout`, `cache_slot_hit_map`, specimen_uid, source_family, target_metric_uid, substrate_snapshot_hash, panel_run_uid, model_id, provider_path, estimated_cost_usd. Recorded in the per-role transcript's `model_identity_json.usage` (JSONB; no DDL needed on the bc-core side).

#### Provider-path support (v1)

ABC v1 supported paths: **Anthropic direct API**, **Claude Platform on AWS**, **Microsoft Foundry**. Bedrock + Vertex acceptable with org-level cache-isolation caveat. OpenAI / Gemini / DeepSeek paths in the panel composition accept-and-ignore the cache directive (silent degrade per the audit §3.5).

#### v1 doesn't depend on workspace-isolated cache scope

Design assumes organisation-level cache isolation throughout. Workspace isolation (on Claude API / Claude Platform on AWS / Microsoft Foundry since 2026-02-05) is opportunistic, not a requirement.

### Specimen #1 — `disputed_invoice_count × SAP FSCM`

Per the held deferral packet §5 and the Phase 0 hand-emulation packet:

- **Target metric:** `disputed_invoice_count`
- **Source family:** SAP FSCM
- **Known surfaces:** UDM_DISPUTE (declared in SC v1.0.0), SCMG_T_CASE_ATTR (status carrier; not declared), UDM_DOC_REL (FI-AR linkage; off critical path)
- **Required decision:** what source surfaces must be governed-contracted and in what shape (one multi-table SC vs. multiple single-table SCs vs. Reader-side derivation) so the OC observes current dispute status truthfully

**Phase 0 hand-emulation outcome:** compound halt with `source_evidence_unavailable` + `operator_decision_among_sc_amendment_options`. Maker recommendation α' (mint new SC for SCMG carrier); Checker downgraded vendor-citation strength because session lacked SAP Help retrieval; Judge surfaced the halt honestly rather than letting the panel proceed under propagated assumptions.

**Track B repair status: parked.** The 5-rung repair ladder in the held packet does not execute. ABC must decide α' / α'' / α''' (or `not_observable`) before any manual repair runs. This ADR's pilot includes Specimen #1 as its first case (per §"Promotion path").

### Promotion path

| Phase | Description | Exit condition |
|---|---|---|
| **Phase 0 — hand-emulation** | Operator + Claude session hand-emulate the Retrieval → Maker → Checker → Judge loop on 3+ specimens, starting with Specimen #1 | Output YAML shape stable; confidence bands meaningful; halt vocabulary correctly applied across specimens; at least one specimen on a non-SAP source family (e.g. Zoho Books → likely `not_observable`, or Oracle → likely `supported_with_separate_oc`) |
| **Phase 1 — prompt-only panel** | bc-ai compositions for Maker / Checker / Judge implemented; context pack hand-assembled by orchestrator-side code; **no retrieval pass infrastructure yet** | Outputs match Phase 0 hand-emulated outputs ≥ 80% of the time; failures corrigible via prompt edits |
| **Phase 2 — retrieval-assisted panel** | Add Option D retrieval pass — RAG-like over vendor docs + substrate + prior decisions | Hallucination rate (Checker rejections for uncited claims) below threshold; retrieval pass produces cited evidence sufficient to ground Maker's claims |
| **Phase 3 — ADR promotion** | After Phase 1 + Phase 2 succeed on the pilot set | This ADR promoted from `proposed` to `decided`; substrate implementation ADR(s) begin |
| **Phase 4 — implementation ADR(s)** | Substrate (`mcf.abc_run_journal`, `mcf.abc_panel_decision` analogous to CAS pattern), controller, service, panel composition pinning | Out of scope for this ADR |

This ADR is filed as `proposed` only. It does not authorise Phase 1 implementation.

### Non-goals (explicit)

- **No code** authored by this ADR. Implementation is Phase 4.
- **No DB schema.** No `mcf.abc_*` tables. No DDL.
- **No panel composition pinning** beyond conceptual roles (Maker / Checker / Judge). Model IDs, temperatures, retry policies — deferred to implementation ADR.
- **No M12 / BCF prompt-cache retrofit.** Each is its own separate audit + ADR.
- **No Track B repair execution.** Track B stays parked per the deferral packet; ABC must decide before any rung runs.
- **No new CEE mode** (`canonical_contract_gap_plan`, `metric_contract_gap_plan`, `bcf_concept_gap_plan`). Future CEE modes wait for this ADR `decided`.
- **No tenant-scope reasoning.** ABC v1 is platform-scope only. Tenant-aware ABC is a future ADR (would also need workspace-isolated caching).
- **No bypass of operator authorship rules** for `value_map` / `canonical_value_set` / `semantic_role`. D447 §D7 remains authoritative.

## Foundation gate

**Repair location:** **B** (contract semantics / governance grammar).

This ADR introduces a new governance reasoning surface + a new orchestration surface — but no new contract artefact family, no evaluation-engine change. ABC consumes existing governance grammar (SC / AC / OC / CC / MC bodies, BCF concepts, CAS findings, D447 doctrine) and emits structured decisions + FSM transitions over the existing factory set.

**Why not D (evaluation boundary implementation):** No evaluator change. ABC reads + orchestrates; CEE / Harness / CAS / BCF / MCF behaviour is unchanged.

**Why not F (read model / diagnostics):** ABC participates in lifecycle gating (CEE consumes ABC's pre-MC R(M) lock; the orchestrator gates halts to operator). Governance, not diagnostic display.

**Three pre-action answers:**
1. **Why here?** Chain-shape reasoning per `(metric × source_family)` has no current home. D447 §D2 names a pre-MC R(M) lock as CEE input; ABC is *where that lock is produced*. The existing held-packet workflow is session-scoped and doesn't survive across sessions.
2. **Why not upper layers?** No grammar change to contract artefact families. ABC's outputs reference existing grammar; do not modify it.
3. **Why not lower layers?** No evaluation change. CEE / Harness / CAS keep current behaviour. ABC slots upstream as an authority CEE already accepts (D447 §D2 fallback rule).

## Risks

| Risk | Mitigation |
|---|---|
| **"Agent" framing creeps back** | Boundary commitments §B4 + CI test that orchestrator code contains no free-form LLM call paths |
| **Source-family knowledge creep into CEE** | Boundary commitments §B1-B3 + audit at every new CEE mode ADR |
| **Prompt anti-regression failure** | CI test mirrors M12 Maker-prompt anti-regression pattern (forbidden-literal list); periodic source-family rotation in pilot |
| **Citation drift across packets/sessions** | Specimen #1 already showed this; ADR makes citation tuples + content_hashes load-bearing. Every Maker claim cited; Checker hashes |
| **Replayability regression at orchestration seam** | D2 keeps loop deterministic; only Phase 2+ retrieval and panel reasoning carry LLM stochasticity, bounded by content_hash + run journal |
| **Slot 1/2 source-family leak invisibly drops cache hit rate** | CI anti-regression on slot templates + telemetry surfaces `cache_creation_input_tokens=0 AND cache_read_input_tokens=0` as warning |
| **Workspace isolation not yet on Bedrock** | v1 design assumes organisation-level isolation. Tenant-scope reasoning is out of v1 scope |
| **Hand-emulation pilot variance across sessions** | Closed YAML output shape pinned in §"ABC output contract"; sessions emit conforming YAML or halt |
| **Operator fatigue from frequent halts** | Halts are intentional. Each is a governance-grade decision point. Frequency is a feature; ABC's job is to say "this needs you" |
| **`not_observable` rejected by stakeholders who want fake universality** | Boundary commitment §B3 + D447 §P5 + Foundation Invariant VI. Honest "no" is a success, not a failure |

## Consequences

- **Track B FSCM repair remains parked** until ABC decides among α' / α'' / α''' / `not_observable` for Specimen #1.
- **No new CEE mode** (canonical / metric / bcf gap plans) ships before this ADR is `decided`. The existing CEE v0.2 (SC + AC + OC) suffices for Track B's critical path.
- **Cross-repo caching contract** from the held audit becomes the implementation reference for Phase 1 onward; ABC adopts cache-aware execution from day one.
- **M12 / BCF panel cache retrofit** is decoupled — each gets its own audit + ADR. Filed as follow-up tasks (§"Follow-up tasks" below).
- **`.claude/` held packets** authored across SES-9184c0 form ABC's design corpus. They are referenced by this ADR but not retired until Phase 1 implementation begins.
- **Foundation Invariants I, IV, VI** continue to apply at the boundaries ABC reasons over; ABC does not adjust them.

## Amendments

> **Amendment (2026-06-16, Specimen #2 finding).** Status remains `proposed`. Three focused refinements were applied after the Phase 0 hand-emulation of Specimen #2 (`disputed_invoice_count × Zoho Books`) revealed gaps that the original draft did not handle:
>
> 1. **Added §"ABC Run Request"** under "## Decision" — defines every ABC run as a typed `(target_metric × source_family × optional tenant_context)` triple with `do_not_write: true` lock. Specimen #2 surfaced that source-family-level reasoning is insufficient when tenant configuration governs observability.
> 2. **Refined `source_capability` output** in §"ABC output contract" — replaces the boolean `not_observable_in_this_source` with a per-segment object whose keys name tenant or configuration segments and whose values are verdicts from D7's 5-value vocabulary. Permits the Zoho-shape outcome: `{default_unconfigured: not_observable, tenant_with_custom_dispute_field: supported_with_tenant_extension, tenant_with_external_helpdesk: supported_via_external_source}`. The verdict vocabulary in D7 is unchanged; only the output shape is extended.
> 3. **Added two stop codes** to §"Stop conditions" (count 14 → 16, mirrored in D6): `tenant_value_map_required` (distinct from `operator_value_map_required` because tenant-defined source enums carry tenant authorship, not operator policy) and `source_system_registration_required` (a source-onboarding gap, distinct from the chain-contract `source_evidence_unavailable`).
>
> No locked decisions were retracted. D7's 5-verdict vocabulary, D8's nine boundary commitments, and D9's caching NFR are unchanged. The Specimen #2 finding is filed in full at `.claude/abc-specimen-2-zoho-disputed-invoice-count-held-2026-06-16.md`.

> **Amendment (2026-06-16, Foundation tenant-scope correction).** Status remains `proposed`. The earlier same-day amendment + Specimens #2/#3 stepped over a Foundation boundary by emitting `supported_with_tenant_extension`, `supported_via_external_source`, and `tenant_value_map_required` as if they were v0 proceed verdicts and stop codes routable by the ABC orchestrator. They are not. Per `the-contract-grammar.md` lines 86, 311, 313, tenant-scoped variation lives only at the Contract Binding layer; per `the-object-model.md` line 226, Contract Binding is a grammar instance, not an authoritative object; per `foundation-overview.md` line 112, no per-tenant override of Foundation invariants; per `the-authority-model.md` lines 38, 172, no lower-level silent override; per `the-dual-layer-interaction-model.md` lines 132–134 (load-bearing), AI does not write authoritative state outside governed authoring. The Non-goals section already reserved tenant-scope reasoning to a future ADR. Four focused edits restore coherence:
>
> 1. **§"ABC Run Request" property 2** rewritten — `tenant_context` is **contextual only in v0**; observing it cannot authorise tenant-scoped contract modelling. Foundation citations added.
> 2. **§D7 vocabulary classification** added — 5 verdicts retained; classified as **v0 proceed-class** (`supported_directly`, `supported_with_amendment`, `not_observable`) vs **v0 reserved/advisory** (`supported_with_tenant_extension`, `supported_via_external_source`). Reserved verdicts cannot be emitted as proceed verdicts in v0; they name real future enablement paths.
> 3. **§"ABC output contract" `source_capability` section** replaced by **`platform_source_capability`** (single platform-level verdict from the v0 proceed-class triple, the only verdict the orchestrator routes on) + **`future_enablement_paths[]`** (advisory list naming reserved verdicts with rationale + preconditions + `operator_decision_class: out_of_v0`, NOT routable by ABC v0). The earlier per-segment-tenant shape removed.
> 4. **§"Stop conditions"** — `tenant_value_map_required` (added in the previous same-day amendment) **replaced by `tenant_extension_out_of_scope`** (broader, honest about why v0 halts). **`external_source_out_of_scope` added** as new code, distinct from `source_system_registration_required` (primary source family vs secondary external system). Stop-code count 16 → 17. D6 updated.
>
> Locked decisions D1, D2, D3, D4, D5, D8, D9 unchanged. D7 vocabulary unchanged (only its v0 classification added). The nine Boundary commitments unchanged. The Non-goals "No tenant-scope reasoning" item unchanged — this amendment makes the rest of the ADR consistent with it. Specimens #2 and #3 hold-packets carry appended correction sections (originals preserved). Phase 0 remains valid under the corrected interpretation — all three specimens still produce honest halts; what changes is the classification of those halts. The correction packet is at `.claude/abc-foundation-tenant-scope-correction-held-2026-06-16.md`.

> **Amendment (2026-06-16, platform source capability vocabulary tightening).** Status remains `proposed`. Same-day follow-up to the Foundation tenant-scope correction. The prior correction split `source_capability` into `platform_source_capability` + `future_enablement_paths[]` but left the labels `supported_with_tenant_extension` and `supported_via_external_source` listed in D7 (as "v0 reserved / advisory") and used them as `kind:` values inside `future_enablement_paths[]`. That left a textual leak path — a reader scanning the YAML could see the same verb-shaped string in two places and infer it was a routable verdict. The Foundation citations rule out that interpretation, but the textual surface still permitted the mistake. Three focused edits remove the residual ambiguity:
>
> 1. **D7 row** — `platform_source_capability.verdict` is now a closed enum of exactly **3 verdicts**: `supported_directly`, `supported_with_amendment`, `not_observable`. v0 output MUST reject any other value at this field. The labels `supported_with_tenant_extension` and `supported_via_external_source` are **RETIRED as v0 verdicts** (mentioned in D7 only as historical reference so future readers understand why the field never carries them).
> 2. **§"ABC output contract" `platform_source_capability`** — hard-typed YAML schema with closed enum. Includes an explicit "MUST NOT appear here" line for the retired labels.
> 3. **§"ABC output contract" `future_enablement_paths[]`** — `kind:` field renamed to `path_kind:` (intentionally distinct from `verdict`); vocabulary changed to verb-free `tenant_extension` / `external_source` (no `supported_with_` prefix); three new required fields added — `current_status: out_of_v0_scope`, `required_future_design`, and `not_routable_by_abc_v0: true` (the last is a runtime assertion that blocks accidental dispatch).
>
> Locked decisions D1, D2, D3, D4, D5, D8, D9 unchanged. D6 stop-code count unchanged at 17. D7's semantic role (Source-capability verdict vocabulary) unchanged; only its v0 enumeration narrowed. The nine Boundary commitments unchanged. The Non-goals "No tenant-scope reasoning" item unchanged. Specimens #2 and #3 CORRECTION-section YAML re-emitted under the tightened shape (original §1–§13 / §1–§15 preserved verbatim). Phase 0 remains valid; the tightening narrows the output surface without changing what was retrieved, reasoned, or halted on in any specimen. Tightening packet at `.claude/abc-platform-source-capability-tightening-held-2026-06-16.md`.

> **Amendment (2026-06-16, Pattern A architecture correction).** Status remains `proposed`. The original cross-repo audit (`.claude/prompt-cache-cross-repo-audit-held-2026-06-16.md` §1.1) recommended **Pattern B** for ABC (bc-ai hosts vendor execution and panel composition) with an audit-time caveat at §1.4: *"if ABC needs deterministic substrate access or grows its doctrinal surface, some shape of Pattern A may re-emerge."* That caveat has matured. The work between the audit and this amendment — three prior D448 same-day amendments (ABC Run Request + segmented source_capability + 2 stop codes; Foundation tenant-scope correction; vocabulary tightening), the Phase 0 §8 scoring rubric, and the Phase 1 prompt-only replay — has built a doctrinal surface (17 stop codes; 8-field rubric; 3-verdict closed enum with 2 retired labels; closed `path_kind` enum; Foundation Invariant I/IV/VI Checker checks; retired-label discipline; source-family rotation discipline; output schema validation; run journal shape) that belongs to the platform team (bc-core), not the model-transport team (bc-ai).
>
> Three edits ratify the realignment:
>
> 1. **D9 row** rewritten — **bc-core-owned panel; optional bc-ai transport** (Pattern A-like; aligns with MCF M12 precedent). bc-core owns the orchestrator, Maker/Checker/Judge role prompts, context-pack assembly, role sequencing, output schema validation, scoring rubric, run journal, citation tracking, stop-code emission, and prompt-cache layout assembly. bc-ai (if used) is a transport pass-through only and MUST NOT own ABC doctrine, prompts, schema, or decisions.
> 2. **§"Prompt caching and context budget — NFR" §"Execution pattern"** rewritten — explicit Pattern A framing with doctrinal-surface justification and M12 precedent citation. Cache directive is injected bc-core-side; if bc-ai is used as transport, it forwards directives verbatim.
> 3. **§"Follow-up tasks" preamble** updated — FOLLOW-UP-1 (bc-ai cache passthrough) is **no longer a prerequisite for ABC**. It becomes an independent enhancement for non-ABC bc-ai-traversing callers. FOLLOW-UP-2 (M12) and FOLLOW-UP-3 (BCF B6) unchanged. The three follow-ups can ship in any order; none gates ABC.
>
> Locked decisions D1, D2, D3, D4, D5, D6, D7, D8 unchanged. D9 narrowed only in its execution-pattern framing (the 4-slot cache layout and source-family-literal forbiddance survive verbatim). The nine Boundary commitments unchanged; in fact B4 / B6 / B9 are strengthened by Pattern A. The Non-goals "No tenant-scope reasoning" item unchanged. The Phase 1 prompt-only replay aggregate result (24/24 PASS, no hard fails) is preserved — the simulation scored against the output schema, not against any specific transport pattern. The next real-LLM Phase 1 replay target shifts from **bc-ai compositions** to **bc-core-owned panel runner** (with optional bc-ai transport pass-through). Correction packet at `.claude/abc-pattern-a-architecture-correction-held-2026-06-16.md`.

> **Promotion to `decided` (2026-06-17).** Promoted to `decided` after ABC Phase 1 real-model replay and AI telemetry emitter live proof. This does not mean production implementation is complete; Phase 2 retrieval, batch mode, BCF integration, and Track B resume remain future work.
>
> Grounding evidence accepted at promotion: (a) PR series A–G merged with replay #4 producing 23/24 fields PASS, 0 hard fails, 0 schema validation failures, `aggregate_pass=true` against the 3 closeout specimens (SAP FSCM / Zoho Books / QuickBooks); (b) `ai_telemetry.ai_run_ledger` + `ai_call_ledger` substrate landed (PR #324) and emitter live-proven end-to-end via SES-838d44 with witness `run_uid=29c36745-f1a3-46a9-87a9-d5873d9f2ec1`, 1 run + 3 call rows, `run_kind='abc_replay'`, `run_scope='platform'`, `subject_kind_code=null`, `subject_uid=null`, `tenant_id=null`, `adr_refs` containing `DEC-cff0cf`, all D448 closed shapes (3-verdict / 17 stop-code / 8-confidence / closed `orchestrator_next_action`) preserved in the runtime output. No D448 vocabulary, schema, scoring rubric, or runtime composition was changed at promotion.
>
> Locked decisions D1–D9 unchanged; the nine Boundary commitments unchanged; the seventeen stop codes unchanged; the 3-verdict closed enum at `platform_source_capability.verdict` unchanged; the Non-goals "No tenant-scope reasoning" item unchanged. Status `decided` represents accepted platform governance, not implementation completeness. Promotion to `implemented` deferred; recorded follow-ups stand — Phase 2 retrieval-assisted panel, batch/throughput mode, BCF B6 integration, Track B chain repair resume, production runtime (HTTP controller / module / scheduled service), CAS-side substrate snapshot, and ABC reusable run-table.

## References

### Held packets (authored SES-9184c0, 2026-06-16)

- `.claude/track-b-abc-consolidation-held-2026-06-16.md` — original consolidation; superseded by this ADR for the §4 ABC framing; substrate findings in §1–§3 still authoritative
- `.claude/abc-orchestrator-pivot-addendum-held-2026-06-16.md` — orchestrator + bounded panel split; locked architecture
- `.claude/abc-panel-design-discussion-held-2026-06-16.md` — Option D + context pack + confidence model + failure modes + worked example
- `.claude/abc-panel-caching-and-context-budget-held-2026-06-16.md` — 4-slot cache layout + ADR language template
- `.claude/abc-specimen-1-fscm-hand-emulation-held-2026-06-16.md` — Phase 0 specimen #1 + citation-drift finding
- `.claude/abc-specimen-2-zoho-disputed-invoice-count-held-2026-06-16.md` — Phase 0 specimen #2 + source-capability variance finding (drove the 2026-06-16 amendment)
- `.claude/track-b-repair-deferral-abc-specimen-held-2026-06-16.md` — Track B parking + ABC specimen reframe
- `.claude/track-b-sc-ac-v1.1-repair-plan-held-2026-06-16.md` — parked repair ladder (banner refers to deferral)
- `.claude/sc-v1.1-sap-fscm-dispute-case-held-2026-06-16.md` — Rung 1 grammar finding (source-v1 one-table constraint)
- `.claude/oc-v1-pr6-fscm-held-blocker-packet-2026-06-16.md` — original substrate blocker
- `.claude/abc-adr-promotion-plan-held-2026-06-16.md` — promotion path (this ADR ratifies)
- `.claude/prompt-cache-cross-repo-audit-held-2026-06-16.md` — cross-repo caching audit; §"Smallest safe PR sequence" referenced as implementation guidance

### Authoritative ADRs

- DEC-1fa08f / D445 — Chain Audit Service
- DEC-739e23 / D446 — Chain Enrichment Engine
- DEC-e01fcf / D447 — Chain enrichment doctrine
- DEC-02f5a9 / D431 — Business Concept Registry (BCF)
- DEC-46ff0a / DEC-61850f / DEC-6b35e0 — D441 source-literal guard
- DEC-bebaec / D305 — chain_status SSOT
- DEC-804874 — D366 L-node verification (override pattern referenced)

### Foundation chapters

- `bc-docs-v3/docs/foundation/the-invariants.md`
- `bc-docs-v3/docs/foundation/the-evaluation-boundaries.md`
- `bc-docs-v3/docs/foundation/the-contract-grammar.md`

### External

- Anthropic prompt caching reference (fetched 2026-06-16) — `platform.claude.com/docs/en/build-with-claude/prompt-caching`

## Follow-up tasks — prompt caching (recorded; **not yet filed as DevHub tasks**)

These three follow-ups land in DevHub when this ADR is promoted from `proposed` to `decided` (or earlier if operator authorises caching retrofits independently). Recorded here in the ADR to keep the scope coupling visible.

**Note (per 2026-06-16 Pattern A architecture correction):** FOLLOW-UP-1 (bc-ai cache passthrough) is **no longer a prerequisite for ABC**. Under the corrected architecture, ABC's prompt-cache discipline is implemented in bc-core directly (per-vendor adapters inject `cache_control` at the bc-core call site — the MCF M12 pattern). FOLLOW-UP-1 becomes an independent enhancement for non-ABC vendor calls that traverse bc-ai (e.g. BCF B6, which remains Pattern B). FOLLOW-UP-2 (M12 retrofit) and FOLLOW-UP-3 (BCF B6 adoption) are unchanged. The three follow-ups can now ship in any order; none gates ABC.

- **FOLLOW-UP-1 — bc-ai cache passthrough foundation (Wave A from the cross-repo audit).** `AnthropicClient` + `BedrockClient` accept optional `cache_directive`; non-Anthropic clients accept-and-ignore + log; `AgentResult` + `evidence` schema extended with cache fields; `/api/ai/suggest/*` response envelope adds `cache_usage_per_role`. No behaviour change for callers that don't pass the directive. **Independent enhancement for non-ABC bc-ai-traversing callers.**
- **FOLLOW-UP-2 — MCF M12 Pattern A cache retrofit.** `AnthropicAgentAdapter` accepts cache directive at adapter input; cache stats persisted into `mcf.metric_authoring_panel_transcript.modelIdentityJson.usage` (JSONB; no DDL). Largest absolute spend on the platform; Maker Opus 4.7 with ~30K-50K tokens of stable prefix per run.
- **FOLLOW-UP-3 — BCF B6 Pattern B cache adoption.** `RegistryAuthoringPanelRequest.cacheDirective` added; `registry-authoring-panel.client.ts` populates content hashes; cache stats round-tripped via the same JSONB extension. Smaller per-call (BCF prompts shorter) but high call volume in authoring waves.

