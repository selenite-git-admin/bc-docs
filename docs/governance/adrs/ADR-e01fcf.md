---
uid: DEC-e01fcf
title: "Chain enrichment doctrine — autonomous sequencing across BCF / SC / AC / OC / CC / MC / CAS / PE-MC"
description: "Topological order, required-vs-optional dependency rule, source-identity rule, and human-judgment halt vocabulary that govern the Chain Enrichment Engine across all contract families. Generalizes seven locks from the FSCM dispute review (2026-06-16) into platform doctrine."
status: decided
date: 2026-06-16T08:38:54.992Z
project: bc-core
domain: platform
subdomain: chain-engines
focus: governance
---

# Chain enrichment doctrine — autonomous sequencing across BCF / SC / AC / OC / CC / MC / CAS / PE-MC

## Context

Operator advice 2026-06-16: required-vs-optional prerequisites is now core CEE behavior and must not live only in .claude/. CEE v0/v0.1 ships SC + AC modes; OC / CC / MC / BCF modes are imminent. Without explicit doctrine, every future CEE mode re-derives sequencing + dependency rules from first principles across Foundation + 13 ADRs.

# Chain enrichment doctrine — autonomous sequencing across BCF / SC / AC / OC / CC / MC / CAS / PE-MC

## Context

CEE v0 (DEC-739e23 / D446) ships one mode (`source_contract_gap_plan`); CEE v0.1 added `admission_contract_gap_plan` (PR #305, 2026-06-16). The natural successor modes — for OC, CC, MC, BCF — are imminent. Before any of those ship, the platform needs an explicit rule for:

1. **What order** the chain enrichment engine must walk when serving a target metric.
2. **What blocks** the engine and what is merely advisory.
3. **Where source-system identity tokens** (`PSTAT`, `BLART`, `UDM_CASE_GUID`, `BUKRS`, …) belong — and where they emphatically do not belong.
4. **What CEE may emit autonomously** vs. what halts for operator judgment.
5. **How required-vs-optional partitioning** is derived per-metric.

Until now these rules have lived implicitly in:
- The Foundation chapters (`bc-docs-v3/docs/foundation/`) — Invariants I–VI, the four boundaries, the boundary-independent rules.
- Six reader/source ADRs (DEC-e7a4f5, DEC-d785d4, DEC-f1565d, DEC-5fd322, DEC-136a23, DEC-129417).
- D445 (CAS), D446 (CEE), D431 (BCF Registry), D441 (source-literal guard).
- The CLAUDE.md Foundation Invariant Check.

The FSCM `disputed_invoice_count` review (SES 2026-06-16) made the implicit explicit. The operator's PSTAT clarification (PSTAT stays a source token; canonical concept is `Customer Invoice × status = in-dispute`) forced a doctrine review across the ADR set; no contradictions were found, but the synthesis was nowhere written down. This ADR records the synthesis as standing governance so future CEE modes (OC, CC, MC, BCF) and future tenant onboarding sessions inherit it without re-deriving from first principles every time.

Operator advice (2026-06-16): "Required vs optional prerequisites is now core CEE behavior. That should not live only in `.claude/`."

## Decision

Adopt the eight-principle Chain Enrichment Doctrine as platform doctrine for all CEE modes (current + future) and all CEE-adjacent governance (CAS, harness, M12/M13/M14 lifecycle).

### Eight load-bearing principles

| # | Principle | Source |
|---|---|---|
| P1 | Foundation governs sequence; the chain engines obey it. | `foundation/the-invariants.md` Invariant II; `foundation/the-evaluation-boundaries.md` |
| P2 | BCF is upstream vocabulary; not a contract family. | DEC-02f5a9 / D431 |
| P3 | Topological order is fixed: BCF → SC → AC → OC → CC → MC → CAS pre_m13 → PE-MC → release. Mode-by-mode strict-superset extensible. | DEC-739e23 / D446 + PR #305/#307/#309 pattern |
| P4 | Required vs optional dependency rule is **metric-driven**: R(M) = MC `metric_binding.variables[].business_concept_id` ∪ formula AST variables (transitively to their BCs) ∪ grain Entity's `identity_bearing` property's BC. O(M) = everything else. CEE blocks only on R(M). | New (this ADR) |
| P5 | Source identity / plumbing tokens stay in SC / AC / OC. They become canonical BCs **only** when a metric explicitly needs source-system lifecycle analytics distinct from canonical state. The OC's `transform = code_lookup` (D441 §1.4) is the canonical-strategic derivation path. | DEC-e7a4f5 + D441 + Invariant I |
| P6 | Diagnostic enrichments (`semantic_role = diagnostic`) are deferable. They live in the soft `field_affinity` layer (ADR-136a23), not in the chain-blocking layer. | DEC-136a23 |
| P7 | CEE never authors `canonical_value_set`, BC identity, `semantic_role`, formula intent, or `transform_params.value_map`. These halt with `held_operator_judgment_required` and a structured decision request. | DEC-739e23 Rules-2 |
| P8 | No lower-layer compensation for upper-layer semantic gaps. SDG / fact rows / read filters / OC mappings cannot be tuned to satisfy a metric whose contract is underspecified. The fix lives at the layer of the gap. | Invariant I + CLAUDE.md Foundation Invariant Check |

### Locked sub-decisions

| D | Topic | Choice |
|---|---|---|
| **D1** | Topological order | `BCF → SC → AC → OC → CC → MC → CAS pre_m13 → PE-MC → M14`. Forward-only, strict-superset extensible. |
| **D2** | R(M) derivation | **MC-derived when MC body exists (authoritative):** `metric_binding.variables[].business_concept_id` ∪ formula AST variable refs ∪ grain Entity's identity property's BC. Deterministic; no operator input. **Pre-MC fallback (when no MC body exists yet, e.g. seed metric → OC v1 critical path):** R(M) is derived from `target_seed_metric.formula_hint` (or equivalent seed-side formula) **plus operator-locked critical-path BCs**. The pre-MC R(M) is recorded on the CEE plan with provenance `pre_mc_lock` and the operator-supplied lock manifest. Once the MC ships, the MC-derived R(M) is authoritative and supersedes; drift between pre-MC lock and MC-derived R(M) is recorded as `r_m_promotion_drift` (advisory, not blocking — the MC author has the final say on R(M) at promotion time). |
| **D3** | OC-emission gate when O(M) BCs missing | **YES, CEE may emit OC v(N+1) packet** provided every BC in R(M) is registered AND the proposed OC's `field_mappings[]` covers R(M). Absent O(M) BCs recorded on the same plan UID with `optional_oc_diagnostic_mapping_deferred` advisory status. ADR anchors: DEC-5fd322 + DEC-136a23 + DEC-f1565d + Invariants II/VI. |
| **D4** | Source identity placement | Source tokens (`PSTAT`, `BLART`, `BUKRS`, `UDM_CASE_GUID`, etc.) stay in SC.`fields[]` + AC field rules + OC `field_mappings[].source_field`. They become canonical BCs **only** when an MC's R(M) explicitly requires source-system lifecycle analytics. Otherwise they are derived into existing canonical BCs via OC `code_lookup` per D441. |
| **D5** | New CEE blocking statuses | Storage layer (`chain_enrichment_plan.status_code`) extends with seven new blocking statuses + two advisory `optional_*_deferred` + one `held_operator_judgment_required` — full list in §"Recommended CEE blocking statuses" below. Each addition is a strict superset of the current v0.1 set per the PR #307 widening pattern. |
| **D6** | Foundation gate compliance | Every CEE-emitted packet states its repair-location classification (A–F) and answers the three pre-action questions (CLAUDE.md). Cross-family doctrine fix lives at location B (contract semantics / governance grammar). |
| **D7** | Human-judgment halt vocabulary + Harness apply contract | CEE halts on (i) authoring `canonical_value_set` content, (ii) resolving BC ambiguity, (iii) assigning `semantic_role`, (iv) rewriting formula intent, (v) authoring `transform_params.value_map` or `unmapped_policy`. Emits structured decision request; operator authors; CEE re-plans. **Harness apply contract (L3 lock, 2026-06-16):** Harness APPLY refuses any OC packet whose `field_mappings[]` contains a `transform = code_lookup` entry with empty or missing `transform_params.value_map`. CEE may emit a plan whose `harness_packet_json` is marked **`proposed_not_applyable`** with `requires_operator_value_map: true` and a structured `decision_request` enumerating the affected `field_mappings[].source_field` entries; but CEE must NOT stamp such a packet as applyable, and Harness must NOT accept it on APPLY mode. Operator authors the `value_map` and `unmapped_policy`; CEE re-plans; the re-emitted packet is `proposed_applyable`. **Empty-value_map skeleton bodies are forbidden in any OC apply path.** This rule is the OC-family analog of the existing C5 confirm precondition (operator authorship of canonical content before substrate write). |
| **D8** | Diagnostic-vs-strategic semantic_role assignment | Operator-only. CEE never picks `semantic_role`. New BCs that capture source-narrative explanations carry `diagnostic`; canonical-strategic concepts carry `amount` / `temporal` / `dimension` / `status` / `identity`. |

### Topological order — current and planned CEE modes

| # | Stage | CEE mode | Status today | What blocks the next stage |
|---|---|---|---|---|
| 1 | BCF prereq | (planned) `bcf_concept_gap_plan` or operator-direct | not shipped | ≥1 BC in R(M) absent |
| 2 | SC | `source_contract_gap_plan` | v0 shipped | SC missing fields required by AC |
| 3 | AC | `admission_contract_gap_plan` | v0.1 shipped (PR #305) | AC inconsistent with SC fields |
| 4 | OC | (planned) `observation_contract_gap_plan` | not shipped | R(M) BC absent / value_set incomplete |
| 5 | CC | (planned) `canonical_contract_gap_plan` | not shipped | active-OC union doesn't cover R(M) |
| 6 | MC | (planned) `metric_contract_gap_plan` | not shipped | CC.field_selection missing R(M) BC |
| 7 | CAS | `pre_m13_audit` | v1.1 shipped (PR #302) | FAIL / OPERATOR_REVIEW |
| 8 | PE-MC | M13 evaluator | shipped | PE-MC failure |
| 9 | M14 | Operator-gated activation | shipped | — |

### Recommended CEE blocking statuses (additive; strict-superset of PR #309)

| Status | Layer | Action |
|---|---|---|
| `blocked_bcf_prerequisites_missing` | BCF | Halt; emit `bcf_concept_gap` decision request |
| `blocked_parent_sc_missing` | SC | Halt (standardize wording — currently implied) |
| `blocked_parent_ac_missing` | AC | Halt |
| `blocked_oc_mapping_concepts_missing` | OC | Halt; emit `oc_field_mapping_gap` decision request |
| `blocked_oc_canonical_value_set_missing` | OC / BCF | Halt; route to operator-only BCF supersession |
| `blocked_cc_field_selection_missing` | CC | Halt |
| `blocked_mc_binding_incomplete` | MC | Halt |
| `optional_bcf_enrichment_deferred` | BCF | **Does not block** — advisory |
| `optional_oc_diagnostic_mapping_deferred` | OC | **Does not block** — advisory |
| `held_operator_judgment_required` | any | Halt; emit structured decision request |

Each subsequent CEE mode's vocabulary widening (mode_code, target_kind_code, status_code) extends `chain_enrichment_plan` CHECK constraints as a forward-only strict superset (PR #307 pattern).

### Pre-MC R(M) lock — FSCM critical path (operator-locked manifest, 2026-06-16)

Per D2's pre-MC fallback rule, the in-flight FSCM critical path for `disputed_invoice_count` operates under this operator-locked R(M) manifest until the MC is authored:

| R(M) element | BC concept_id | Justification |
|---|---|---|
| `Customer Invoice × document_number` (identity) | `40433e4f-...` | Invoice identity-bearing property — required to count distinct invoices |
| `Customer Invoice × status` | `0a860227-...` | The status whose value `in-dispute` defines the predicate. `canonical_value_set` already contains `in-dispute`. |
| `Customer Invoice × posting_date` | `338c601a-...` | **Conditional R(M) — included only if the authored OC's `identity_semantics` or the downstream CC's `temporal_gate` requires it as identity / time anchor.** Default treatment is O(M) (deferred). The OC author makes the call at OC body authoring time and records the choice in the plan's `pre_mc_r_m_manifest`. |

Out of R(M) (in O(M) — deferred, not blocking):

- `Customer Invoice × dispute reason code` (Tier 1 BCF enrichment, independent PR)
- Any `Dispute Case` entity or `case_id` BC (never canonical unless a future MC explicitly requires it)
- `dispute opened at` temporal (Tier 2 — deferred until first metric needs it)
- `disputed amount` amount (Tier 2)

This manifest is recorded on the CEE plan as `pre_mc_r_m_manifest_json` with provenance `operator_lock_2026-06-16`. When the MC ships, CEE compares MC-derived R(M) against this manifest; any drift is recorded as `r_m_promotion_drift` (advisory).

## Foundation gate

**Repair location:** **B** (contract semantics / governance grammar).

This ADR introduces a doctrine artifact, not a new contract artifact. It governs how the existing CEE artifact family is composed across upstream/downstream artifacts and how its packet vocabulary expands. The doctrine itself is governance grammar.

**Why not D (evaluation boundary implementation):** No evaluation engine change. The doctrine governs which packets CEE may emit, not what any evaluator does.

**Why not F (read model / diagnostics):** The new CEE status codes participate in lifecycle gating, not in diagnostic display. They block / advise the chain enrichment loop directly.

**Three pre-action answers:**

1. **Why here?** "Required vs optional prerequisites" is core CEE behavior with no current home. The synthesis lives implicitly across Foundation + 13 ADRs but is nowhere named as a single rule. Without this ADR, every future CEE mode (BCF, OC, CC, MC) must re-derive the partition from first principles.
2. **Why not upper layers?** No grammar change to contract artifacts. The doctrine references existing grammar (OC `field_mappings`, MC `metric_binding`, BCF `business_concept_id`) and existing CEE mode shape (target_kind, status_code). It does not author new fields in any contract body.
3. **Why not lower layers?** No evaluation change. The eligible-vs-deferred partition is computed by reading the target MC's body; no evaluator behavior changes.

## Options considered

### Option A — Adopt the doctrine as an ADR (recommended; chosen)

Locks the topological order, required/optional rule, source-identity rule, and human-judgment halt vocabulary as platform doctrine. Subsequent CEE mode work (OC, CC, MC, BCF) inherits the rules.

| Pros | Cons |
|---|---|
| One governed source of truth; future CEE modes don't re-derive | Adds an ADR; some lock-in if future learning contradicts a principle |
| Anchors the FSCM `disputed_invoice_count` decision in standing governance, not session-scoped notes | — |
| Reduces re-litigation cost across tenant onboarding sessions | — |
| Codifies the operator's PSTAT clarification beyond FSCM | — |

### Option B — Keep the doctrine in `.claude/` only

Continue to reference the doctrine doc as session-scoped working authority. Promote later if/when more CEE modes ship.

| Pros | Cons |
|---|---|
| No ADR ceremony today | Future sessions may re-derive or contradict the doctrine; operator advice ("not just `.claude/`") not followed |
| Faster path to OC v1 ladder | Each future CEE mode must re-read the synthesis; risk of drift |

### Option C — Embed in CLAUDE.md as a new section

Add a "Chain Enrichment Doctrine" section to CLAUDE.md instead of authoring an ADR.

| Pros | Cons |
|---|---|
| Always loaded in session context | CLAUDE.md is operational, not architectural; mixes session protocol with governance grammar; ADR registry loses the record |

**Decision:** **Option A.** Operator advice + doctrine scope are both broader-than-FSCM. ADR registry is the right home.

## Risks

1. **Doctrine over-application** — operators may apply the partition rule to non-chain governance (e.g., tenant binding flow) where the BCF→…→MC topology doesn't fit. Mitigation: the doctrine is scoped to "the chain enrichment loop"; tenant binding is governed separately (D446 §Rules-3).
2. **R(M) derivation drift** — if the MC body grammar evolves (e.g., a new `metric_binding` shape), the R(M) derivation rule must be updated in the same ADR cycle. Mitigation: cross-link this ADR to D431 (BCF) and D446 (CEE); any change to either triggers a re-read.
3. **`semantic_role = diagnostic` overload** — operators may tag canonical-strategic concepts as `diagnostic` to keep them out of R(M). Mitigation: semantic_role assignment is operator-only and audited; CAS v1.2 (planned) will include a walker that flags `diagnostic` BCs that appear in active MC `metric_binding`.
4. **Strict-superset enforcement requires DB CHECK widen with each new mode** — the PR #305/#307/#309 pattern is operator-heavy. Mitigation: standardize the apply-runner pattern; consider a meta-migration that opens the CHECK to a controlled enum referenced from a master table (separate proposal, not in scope here).
5. **OC packet emission with O(M) gaps may surprise downstream consumers** — if CC/MC bind to the same OC later, optional BC absence resurfaces. Mitigation: CAS pre_m13_audit C2 walker (already in v1.1) detects "active-OC union does not cover CC.field_selection" — the gate already exists at the audit layer.

## References

- OC v1 critical-path ladder (doctrine-aligned, 6 PRs): `.claude/oc-v1-critical-path-ladder-doctrine-aligned-2026-06-16.md`
- OC v1 FSCM planning packet: `.claude/oc-v1-fscm-planning-packet-held-2026-06-16.md` (D4 = Option D under doctrine)
- BCF prereq packet: `.claude/bcf-prereq-fscm-dispute-planning-packet-held-2026-06-16.md` (D1 = Tier 0 critical path under doctrine)
- Foundation: `bc-docs-v3/docs/foundation/the-invariants.md`
- Foundation: `bc-docs-v3/docs/foundation/the-evaluation-boundaries.md`
- Foundation: `bc-docs-v3/docs/foundation/the-contract-grammar.md`
- DEC-e7a4f5 — Readers are domain-bound, not source-bound
- DEC-d785d4 — Reader → BO/Entity FK; SO shape enforcement
- DEC-f1565d — Multi-table executor; reader observes, no joins/transforms
- DEC-5fd322 — OC is the central design-time artifact
- DEC-136a23 — OC stays reader-scoped; field_affinity is sharing layer
- DEC-129417 — Reader per-subfunction with system flavors
- DEC-1fa08f / D445 — Chain Audit Service (CAS) v1.1
- DEC-739e23 / D446 — Chain Enrichment Engine (CEE) v0.1
- DEC-02f5a9 / D431 — Business Concept Registry (BCF)
- DEC-46ff0a / DEC-61850f / DEC-6b35e0 — D441 source-literal guard
- DEC-ebf0b4 / D268 — Session discipline / one-then-many
- DEC-bebaec / D305 — chain_status SSOT
- AC v1 ladder milestone: `bc-docs-v3/docs/implementation/ac-v1-ladder-milestone-2026-06-16.md`
- CAS / CEE design packet: `bc-docs-v3/docs/implementation/chain-engines-design-packet-2026-06-15.md`

## Consequences

- The OC v1 FSCM ladder (6 PRs) ships under this doctrine; the BCF Wave 3-C prerequisite batch is no longer on the critical path.
- Future CEE modes (OC, CC, MC, BCF) inherit the topological order + R(M) partition + halt vocabulary without re-derivation.
- The CLAUDE.md "Foundation Invariant Check" section remains the authority for the gate process; this ADR is the authority for the chain-enrichment-specific application of that gate.
- The `.claude/doctrine-autonomous-chain-sequencing-2026-06-16.md` file is retired upon ADR filing; the ADR text becomes canonical.
- The `.claude/adr-draft-chain-enrichment-doctrine-2026-06-16.md` file is retired upon ADR filing; superseded by the auto-generated `bc-docs-v3/docs/adrs/ADR-{shortUid}.md`.
- The seven new CEE blocking statuses and two advisory statuses are reserved here; their DDL extension still ships per-mode via the PR #307 pattern (one widen migration per CEE mode rung).

