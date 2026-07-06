---
title: "Pass 1 — Grammar Artifact Register (read-only)"
session: SES-594568
date: 2026-05-12
status: read-only
type: planning-pass
authority: Foundation (locked)
related:
  - docs/foundation/the-contract-grammar.md
  - docs/foundation/the-evaluation-boundaries.md
  - docs/foundation/the-authority-model.md
  - docs/foundation/the-object-model.md
---

# Pass 1 — Grammar Artifact Register

**Read-only.** No code change. No DBCP. No ADR drafted. No service renamed.

Output of Pass 1 of the plan-for-the-plan. Inventories the twelve grammar artifacts that Foundation names (The Contract Grammar §Artifact classification), at register level for the eleven non-Metric artifacts and at depth for the Metric Contract artifact. The depth pass explicitly maps **logical Metric Contract** (as Foundation describes it) versus **physical Metric Contract** (how bc-core currently spreads it across tables and services).

The fold (Metric Contract formalization = formula + input contracts + self-demonstration as one body; completeness gates `active` promotion) is the operating principle. This pass does not propose the fold; it inventories the surface against which the fold will be evaluated in Passes 2-4.

---

## 1. Foundation locks (cited, not restated)

- **Four evaluation boundaries** (Admission, Canonical, Metric, Action) — locked by FND-ERR-006.
- **Twelve grammar artifacts** — six active contract families, one supporting schema, three primitives, one provisional, one retired. The Contract Grammar §Artifact classification.
- **Three-rung authority ladder** (Foundation / ADR+Errata / Descriptive). The Authority Model.
- **Five governance states** (`draft → review → approved → active → superseded`). The Contract Grammar §Lifecycle.
- **Six invariants**; Invariant III (immutability on publish) and Invariant VI (synchronous proof emission) govern all body-schema changes the fold will touch. The Invariants.
- **Master shape authority** lives in DB table `contract.contract_meta_schema`; v2 docs at `legacy-v2/docs/system/foundation/contract-schemas/*` are reference copies regenerated from DB.

The Pass does not extend these locks; it reads against them.

---

## 2. Register — eleven artifacts at register level

The Metric Contract gets its own section (§3) at depth. The other eleven are registered with five facts each.

### 2.1 Source Contract

| Facet | Value |
|---|---|
| Status | Active contract family |
| `$contract` | `barecount/source/v1` |
| Master shape authority | `contract.contract_meta_schema` rows where `category_code='source'`, `meta_version=1` (6,011 chars) |
| Physical surface (bc-core) | `contract.source_contract`, `contract.source_contract_version`, `contract.source_contract_approval` |
| Governance | `governance.state` lifecycle. Body governance: D245 (SC body purity), D253 (structural completeness) |
| Boundary it governs | Admission (as structural reference; Admission Contract validates against it) |
| Reference doc | `legacy-v2/.../contract-schemas/source-v1.md` |

### 2.2 Admission Contract

| Facet | Value |
|---|---|
| Status | Active contract family |
| `$contract` | `barecount/admission/v1` |
| Master shape authority | `contract_meta_schema` `category_code='admission'`, `meta_version=1` (8,339 chars) |
| Physical surface | `contract.admission_contract`, `contract.admission_contract_version`, `contract.admission_contract_approval` |
| Governance | D244 |
| Boundary it governs | Admission (declares validation rules, identity semantics, rejection policy) |
| Reference doc | `legacy-v2/.../contract-schemas/admission-v1.md` |

### 2.3 Observation Contract

| Facet | Value |
|---|---|
| Status | Active contract family |
| `$contract` | `barecount/observation/v1` |
| Master shape authority | `contract_meta_schema` `category_code='observation'` (7,949 chars, 66 keys, 25 governance tags all fixed) |
| Physical surface | `contract.observation_contract`, `contract.observation_contract_version`, `contract.observation_contract_approval`, `contract.observation_field_map` |
| Governance | DEC-0e3c64, DEC-136a23, DEC-1edaaa; FND-ERR-001, FND-ERR-002 |
| Boundary it governs | Admission (field selection from Source Contract to business vocabulary) |
| Reference doc | `legacy-v2/.../contract-schemas/observation-v1.md` |

### 2.4 Canonical Contract

| Facet | Value |
|---|---|
| Status | Active contract family |
| `$contract` | `barecount/canonical/v1` |
| Master shape authority | `contract_meta_schema` `category_code='canonical'` (9,028 chars, 71 keys, 26 governance tags all fixed) |
| Physical surface | `contract.canonical_contract`, `contract.canonical_contract_version`, `contract.canonical_contract_approval` |
| Governance | DEC-97bb94, FND-ERR-004; D244, D245 |
| Boundary it governs | Canonical (produces Canonical Objects from N Source Objects) |
| Reference doc | `legacy-v2/.../contract-schemas/canonical-v1.md` |

### 2.5 Intervention Contract

| Facet | Value |
|---|---|
| Status | Active contract family |
| `$contract` | `barecount/intervention/v1` |
| Master shape authority | `contract_meta_schema` `category_code='intervention'` (7,444 chars, 55 keys, 23 governance tags; D244/D250/D253) |
| Physical surface | `contract.intervention_contract`, `contract.intervention_contract_version`, `contract.intervention_contract_approval` |
| Governance | D244, D250, D253 |
| Boundary it governs | Action (produces Action Objects from N Metric Snapshots) |
| Reference doc | `legacy-v2/.../contract-schemas/intervention-v1.md` |

### 2.6 Canonical Mapping (supporting schema)

| Facet | Value |
|---|---|
| Status | Active supporting schema |
| `$contract` | `barecount/mapping_binding/v1` (legacy name) |
| Master shape authority | `contract_meta_schema` (renamed from `mapping-binding-v1.json` in 2026-04-02 cleanup) |
| Physical surface | `contract.canonical_mapping`, `contract.canonical_mapping_version`, `contract.cc_field_mapping` (1,659 rows live) |
| Governance | DEC-136a23 |
| Boundary it governs | Canonical (binds Business Fields to Canonical Fields at canonical evaluation; per Canonical Contract version) |
| Reference doc | (no dedicated *.md; defined within `the-contract-grammar.md` §Supporting schema) |

### 2.7 Business Object — primitive

| Facet | Value |
|---|---|
| Status | Active primitive |
| Master shape authority | Primitive specification + DDL (`contract.business_object`); no envelope, no contract_meta_schema row |
| Physical surface | `contract.business_object` (202 rows; per earlier inventory). DDL-enforced (no JSON Schema) |
| Governance | D162, D255, D301 (CF split); SDA Phase 1 admission gates (G1, G2a, G2b, G3, G4, G5, G6, G7, G8) where applicable per primitive type. The "admission" mechanism is SDA-4 endpoints — **a primitive-admission process, not an authoritative evaluation boundary** |
| Boundary it governs | None directly. Referenced by Canonical Contracts (one CC per BO) |
| Reference doc | `legacy-v2/.../contract-schemas/business-object-v1.md` |

### 2.8 Business Field — primitive

| Facet | Value |
|---|---|
| Status | Active primitive |
| Master shape authority | Primitive specification + DDL (`contract.business_field`) |
| Physical surface | `contract.business_field` (7,062 rows; 8 SDA-4-admitted, ~6,771 legacy-admitted; per Binding Evidence Trace MWR finding). DDL-enforced |
| Governance | D112, D162, D255, DEC-d72560 (BF/CF split); SDA-4 admission lifecycle for new admissions |
| Boundary it governs | None directly. Referenced by Observation Contracts (`observation_field_map`) and Canonical Mappings (`cc_field_mapping.business_field_id`) |
| Reference doc | `legacy-v2/.../contract-schemas/business-field-v1.md` |

### 2.9 Canonical Field — primitive

| Facet | Value |
|---|---|
| Status | Active primitive |
| Master shape authority | Primitive specification + DDL (`contract.canonical_field`) |
| Physical surface | `contract.canonical_field` (3,097 rows, all in `status_code='draft'`; per Binding Evidence Trace MWR). DDL-enforced |
| Governance | DEC-d72560 (CF as third primitive; D301); per CLAUDE.md memory, "CF certification is unimplemented Phase 1-side." SDA admission gates exist for BF/BO but not yet for CF |
| Boundary it governs | None directly. Referenced by Metric Contract `variables[].field_code` and `co_bindings[].fields_used[]`; produced by Canonical Mapping (`cc_field_mapping`) |
| Reference doc | `legacy-v2/.../contract-schemas/canonical-field-v1.md` |

### 2.10 AI Contract — provisional family

| Facet | Value |
|---|---|
| Status | Provisional contract family. Not in execution spine |
| `$contract` | `barecount/ai/v1` (provisional) |
| Master shape authority | Provisional meta-schema (`legacy-v2/.../schemas/ai-v1.json`); not yet in `contract.contract_meta_schema` as active |
| Physical surface | None active in execution spine. AI-assisted behavior occurs at advisory/surface layers (Conversation surface per Dual-Layer Interaction Model). Closely related: `metric.metric_formula_verification` (dual-AI cross-check audit, 3 rows live), `runtime.l_node_semantic_verdict` (L-Node AI verdicts per DEC-804874) |
| Governance | Provisional. Promotion to active requires an ADR (per The Contract Grammar §Provisional family) declaring the evaluation boundary it governs, composition with Canonical/Metric Contracts, and proof emission requirements |
| Boundary it governs | None until activated. Operates only on the Conversation surface today |
| Reference doc | The Contract Grammar §Provisional family |

### 2.11 Extraction Contract — retired family

| Facet | Value |
|---|---|
| Status | Retired contract family (D069) |
| Master shape authority | Historical only. Schema marked `_status: retired` in 2026-04-02 cleanup |
| Physical surface | Historical Extraction Contracts may exist as preserved artifacts. Not in active execution spine |
| Governance | D069 (retirement decision) |
| Boundary it governs | None |
| Reference doc | The Contract Grammar §Retired family |

---

## 3. Metric Contract — depth pass

The fold lives in this artifact. Depth analysis follows.

### 3.1 Logical Metric Contract (per Foundation)

Foundation describes the Metric Contract as a single grammar artifact with:

- **Envelope**: 4 top-level keys (`$contract`, `version`, `header`, `body`).
- **Header**: 16 required keys shared across families (identity, ownership, governance state, lineage, bindings).
- **Body**: 9 required keys — `input_type`, `formula`, `variables[]`, `co_bindings[]`, `temporal_gate`, `unit`, `direction_code`, `thresholds[]`, `grain[]`.
- **Governance**: five-state lifecycle (`draft → review → approved → active → superseded`); immutable on `active`.
- **Boundary governed**: metric evaluation boundary (produces Metric Snapshots from N Canonical Object versions).
- **Cardinality**: one MC may reference N Canonical Contracts (FND-ERR-003, DEC-29c324).

**Total declared body keys**: 9. **Total declared envelope/header/body keys**: 67 per the DSO example in `legacy-v2/.../contract-schemas/metric-v1.md`.

The body description in The Contract Grammar §Metric Contract is non-exhaustive: "declares metric identity, formula expression, referenced Canonical Contract versions through `metric_binding`, grain alignment, required parameters, evaluation timing, result shape and units, and admissible comparison operations." This phrasing **does not exclude** extending the body with self-demonstration elements; the test of whether the fold requires Foundation amendment versus only ADR amendment is whether `system/foundation/contract-schemas/metric-v1.md` (the v2 reference) is structurally bound by `additionalProperties: false` on the body. **Finding**: it is. v2 metric-v1.md §3 declares `additionalProperties: false`. Any body-key extension requires a meta-schema update in `contract.contract_meta_schema` (governed by the Authority Model via ADR) and propagation through the reference docs.

This is a Pass 4 implementation detail; recorded here so Pass 4 has the reference.

### 3.2 Physical Metric Contract (current bc-core implementation)

The single logical artifact is materially decomposed across at least 9 physical surfaces.

**Authority surface (contract envelope + body governance state):**

| Table | Role | Live count |
|---|---|---|
| `contract.metric_contract` | Identity row (one per logical MC) | 778 |
| `contract.metric_contract_version` | Versioned envelope body in `contract_json jsonb`; carries `governance_state_code`, `success_score`, `last_validated_at`, `supersede_after` | 1,020 (729 active, 289 draft, 2 superseded) |
| `contract.metric_contract_approval` | Approval ledger for governance state transitions | (count not queried) |
| `contract.contract_meta_schema` (category=metric) | Master shape authority (the JSON schema that validates `contract_json`) | 1 row, 8,745 chars, 67 keys, 28 governance tags |

**Decomposed body surface (rows in `metric.*` schema that mirror or supersede content of `contract_json.body`):**

| Table | Role | Live count |
|---|---|---|
| `metric.metric_formula` | Formula text + unit_type_code + maturity_code + version_seq + `is_current` flag. **NOTE: not bound by version_code; bound by metric_definition_id + version_seq. Decoupled from MC version lifecycle.** | 1,216 |
| `metric.metric_formula_variable` | Variable bindings: `var_code`, `role` (input/output/constant), `field_name`, `unit_type_code`, `sort_order`, `constant_value`. Bound to `metric_formula_id`, not directly to MC version | 4,226 |
| `metric.metric_formula_verification` | Dual-AI cross-check audit: `maker_a_*`, `maker_b_*`, `moderator_*`, `cross_validation`, `verdict_code` (`agree / reconciled / disputed / failed`). Bound to `metric_formula_id` | **3** (sparsely populated) |
| `metric.metric_binding` | MC ↔ CC binding rows (one per `co_bindings[]` entry): `metric_contract_id`, `canonical_contract_id`, `binding_role_code`, `fields_used[]`. Bound to MC, not to MC version | 1,133 |
| `metric.mc_dependency` | Secondary-metric chain dependency (when MC consumes another MC's output) | (count not queried) |
| `metric.metric_definition` | Metric catalog row carrying business identity (kpi_id, catalog_code, category, tier). FK target from `metric_contract.metric_definition_id` per D248/D249 | (count not queried) |
| `metric.readiness_ledger` | Runtime readiness rollup; not part of MC body | — |
| `contract.cc_field_mapping` | Canonical Mapping row (BF→CF binding for the bound CC). Indirectly referenced by MC via the CC's `fields_used[]` | 1,659 |

**Test/verification infrastructure (per DEC-cc8fd9 / D303; chain-pressure-test scope, NOT MC body):**

| Table | Role |
|---|---|
| `test_bench.scenario` | Chain test scenario: `tenant_slug`, `volume_target`, `contracts_json`, `expected_json`, `sdg_profile`. **Operates at admission→canonical→metric chain, not at MC body authoring** |
| `test_bench.run`, `run_step`, `run_metric` | Test run records with `expected_value_json`, `actual_value_json`, `variance_pct`, `verdict`, `invariant_results_json` per metric per run |

**Engine runtime services (read MC body, do not author it):**

| Service | Role |
|---|---|
| `src/boundary/metric-evaluation-engine.service.ts` | Runtime metric boundary executor. Includes `verifyAggregationInvariant` (SUM bounds, AVG bounds, MIN/MAX correctness with 1e-9 tolerance) — algebraic-invariant check at evaluation time |
| `src/registry/formula-audit.service.ts` (D315 Layer 1) | Static audit of all MC formulas: dead field refs, bare variables, field-not-in-bound-CC, duplicate formulas, missing components |

### 3.3 Logical-vs-physical divergences (findings)

Six divergences worth surfacing for Pass 2-4 analysis. Each is recorded as a finding, not yet as a proposed change.

**Finding 3.3.1 — Body decomposition is not Foundation-prescribed.** Foundation describes the MC body as a single declaration (9 keys). bc-core spreads it across `contract_json.body` (authoritative envelope), plus `metric.metric_formula`, `metric.metric_formula_variable`, `metric.metric_binding`. The `contract_json` is the governed source; the `metric.*` rows are derived (per D248). Whether the derivation runs from `contract_json` to `metric.*` consistently, or whether `metric.*` can drift independently, is a Pass 2 conformance question.

**Finding 3.3.2 — Formula authority is split.** `metric.metric_formula` carries `version_seq` + `is_current`, bound to `metric_definition_id`. This is **not the same versioning** as `contract.metric_contract_version.version_code` + `governance_state_code`. A formula can change `is_current` (decoupled from MC version) and a new MC version can be created without changing the formula. This is a real ambiguity: which artifact is authoritative for the formula content — the version-bound `contract_json` or the metric-definition-bound `metric_formula` row?

**Finding 3.3.3 — Verification audit is sparsely populated.** `metric.metric_formula_verification` exists with the right shape (dual-AI maker/checker/moderator + verdict) but carries only 3 rows live across 1,216 formulas. The audit infrastructure exists; its use is not enforced by lifecycle.

**Finding 3.3.4 — Active MC versions exist without verification.** 729 MC versions are in `governance.state='active'`. Three have `metric_formula_verification` rows. The remaining 726 are active without a recorded dual-AI cross-check. The fold's enforcement at `active` promotion would today block 726/729 (≈99.6%) of active MCs from re-entering `active` after the rule lands — a real migration concern recorded for Pass 5.

**Finding 3.3.5 — Self-demonstration elements (test cases + expected outputs) are absent from the MC body.** The 9 declared body keys (verified via `contract_meta_schema` `jsonb_path_query`) are: `input_type`, `formula`, `variables`, `co_bindings`, `temporal_gate`, `unit`, `direction_code`, `thresholds`, `grain`. No `demonstration[]` or `test_cases[]` body key exists. The fold's body extension is therefore genuinely missing, not present-but-overlooked.

**Finding 3.3.6 — `metric_formula_verification` audit columns may be partial substitute for run-evidence.** The fold separates "self-demonstration elements" (immutable body content) from "demonstration run evidence" (append-only proof). The existing `metric.metric_formula_verification` shape resembles the latter (dual-AI verdict per iteration). Whether it can be repurposed for the fold's run-evidence role, or whether a new evidence artifact is needed, is a Pass 4 question.

### 3.4 Onboarding-procedure surface (Metric Contract Creation)

`docs/onboarding/metric-contract-creation.md` declares the governed authoring sequence in 9 steps + 16 quality checks:

| Aspect | Current procedure |
|---|---|
| Body keys validated | 9 (matches Foundation; check 13 enforces structural completeness) |
| Quality checks at submission | 16 (structural, semantic, binding, threshold-shape) |
| Self-demonstration check | **None present** — no check enforces test cases or expected outputs |
| Activation path | "submit for review, approve, then activate through the version lifecycle endpoints" (Step 9) |
| Activation block condition | Failing any of the 16 checks keeps the version in `draft` (matches Foundation lifecycle) |

The 16 checks are deterministic structural checks (akin to G1-G8 for primitives). They are **necessary-but-not-sufficient** in the fold's framing: a Metric Contract passing all 16 checks is structurally well-formed but has not been demonstrated.

### 3.5 Governing ADRs (Metric Contract)

Confirmed present in `docs/adrs/`:

| DEC-UID | D-code | Scope |
|---|---|---|
| `DEC-29c324` | D021 | N:1 Metric Contract to Canonical Contract cardinality (FND-ERR-003) |
| `DEC-d72560` | D301 | Business Field / Canonical Field split; MC variables bind to CF names |
| `DEC-c0290f` | D315 | Metric evaluation engine; formula-driven aggregation; grain-aware GROUP BY; algebraic invariants |
| `DEC-cc8fd9` | D303 | E2E Chain Test Bench (tenant-publishes-to-platform); chain pressure-test scope |
| `DEC-35b34b` | D335 | Aggregation authority; metric formulas own aggregation; role uniqueness for multi-CC bindings |
| `DEC-9d1f4b` | D327 | Shared dimension normalization in grain |
| `DEC-ecec75` | D068 | One MC per KPI; metric architecture |
| `DEC-804874` | D366 | L-Node semantic verdict gate; AI-cross-check telemetry pattern at MC envelope |
| `DEC-c9e623` | D389 | Metric Lifecycle States (MLS) — 25-step activation ladder, MLS-14 gate |
| `DEC-d315ve` | — | (additional Metric-engine ADR; full scope TBD in Pass 2) |

D244 (DEC-a0e92e) is referenced in v2 metric-v1.md (Contract Requirements Correction + Master Shape) — confirmed in CLAUDE.md memory but its ADR file in v3 not directly verified in this pass; Pass 2 to confirm.

---

## 4. Cross-cutting findings

Two findings cut across multiple grammar artifacts and are recorded here, separate from per-artifact findings.

### 4.1 The SDA "certified" overclaim is a primitive-side concern, not a Metric Contract concern

The SDA Phase 1 work shipped admission gates (G1-G8) for BF (and partially BO/CF), an admission ledger (`contract.certification_record`), and a five-action lifecycle service. Its scope is **primitive admission into the controlled vocabulary** — what the Foundation calls "grammar primitives" governed through "primitive specifications and relational constraints" (The Contract Grammar §Envelope and common structure).

The word "certified" used in `business_field.status_code='certified'` overclaims because:

- It implies a Metric-Contract-equivalent verification stance (the user-facing intuition we hit in earlier turns).
- Foundation reserves authoritative-evaluation-act semantics for the four boundaries, not for primitive admission.
- The vocabulary collision with Metric Contract `governance.state='active'` (the actual completeness gate for a metric) is a rename concern.

Pass 5 will propose vocabulary alignment. Pass 1 records the finding without proposing a fix.

### 4.2 Test-bench (D303) scope is correctly chain-scoped; do not repurpose for Metric Contract self-demonstration

Reading `docs/adrs/ADR-cc8fd9.md` confirms test-bench is **chain-pressure-test** infrastructure operating end-to-end through the four evaluation boundaries on the qa-bench tenant. The `scenario.expected_json` and `run_metric.expected_value_json` columns superficially match the fold's "expected output" need, but the operational shape (full chain, tenant-side, SDG-driven source data, volume_target) is not the Metric Contract authoring-time shape.

Pass 4 will analyze whether any column-level reuse from test-bench tables is appropriate; the default posture is **the fold builds its own self-demonstration surface and test-bench keeps its chain-pressure-test scope**.

---

## 5. What Pass 1 deliberately did NOT do

- Did not propose any ADR, errata, or DBCP.
- Did not propose body-key additions to Metric Contract.
- Did not propose service renames, retirements, or repositioning.
- Did not propose a `governance.state` enforcement rule.
- Did not enumerate test-bench consumers (deferred to Pass 3).
- Did not read the eight v2 reference *.md files for the non-Metric artifacts (registered them via the v2 index instead; full reads deferred to per-artifact passes if they become needed).
- Did not inspect SDA Phase 1 service code (referenced findings from prior MWRs).
- Did not run the formula audit live (recorded its existence; output is a Pass 2 question).

---

## 6. Inputs to Pass 2

Pass 2 inherits this register and asks: for each artifact, does current implementation conform to Foundation's governance discipline? Specifically:

- Is the `governance.state` machine enforced structurally (DB CHECK + service guards) or by convention?
- Are the immutability-on-publish rules enforced at `active`?
- Do the master shape rows in `contract_meta_schema` match what the validation service (`ContractValidationService`) actually loads?
- Where does naming overclaim (the SDA "certified" finding; potentially others)?
- For Metric Contract specifically: do the decomposed physical surfaces stay consistent with `contract_json.body` (Finding 3.3.1, 3.3.2)?
- For Metric Contract activation: does promotion to `active` require structural validation only, or are runtime checks also required today?

The 9 grammar-artifact entries in §2 plus the depth analysis in §3 are the surface Pass 2 traverses.

---

## 7. Inputs to Pass 4

Pass 4 (Metric Contract fold-gap analysis) has Pass 1 to draw on for:

- The current 9 body keys (`input_type` through `grain`). Confirmed via `jsonb_path_query` on the live `contract_meta_schema` row.
- The decomposed physical surface (9 tables + 2 services). Listed in §3.2.
- The six divergences in §3.3 (each becomes a Pass 4 analysis input).
- The 16 onboarding quality checks in `metric-contract-creation.md` §Quality Gates. These are the floor; the fold extends them.
- The existing test infrastructure (test-bench at chain level, `metric_formula_verification` at dual-AI cross-check level, `verifyAggregationInvariant` at runtime). Pass 4 decides which can be reused, which is wrongly-scoped, which is missing.
- The migration concern from Finding 3.3.4: 726 of 729 active MCs have no `metric_formula_verification` row. Pass 4 must surface the migration path.

---

## 8. Open questions surfaced by Pass 1

Six questions for operator review before Pass 2 begins. None blocks Pass 2 startup; they are calibration points.

1. Foundation reading on Metric Contract body extensibility: Pass 1's read suggests an ADR alone suffices (the body description is non-exhaustive in `the-contract-grammar.md`, but `additionalProperties: false` in `metric-v1.md` requires a meta-schema update). Confirm this is the right reading before Pass 4 designs the body extension.

2. Vocabulary discipline: Pass 1 records the SDA "certified" overclaim and the recommendation to align `business_field.status_code` value with primitive-admission scope (e.g., rename in operator surfaces to "admitted-to-dictionary"). Confirm this discipline is part of Pass 5 scope.

3. Formula authority split (Finding 3.3.2): is `metric.metric_formula.is_current` intended to be the formula authority while `contract_json.body.formula` is the contract-bound copy, or vice versa? Determines whether Pass 4 proposes consolidation or leaves the split as designed.

4. Verification audit population (Finding 3.3.3 & 3.3.4): is the 3-row population of `metric_formula_verification` representative (early adoption), or is the table effectively unused (governance gap)? Determines whether Pass 4 treats it as foundation-to-extend or feature-to-redesign.

5. Pass 5 output shape: one integrated MWR covering all twelve artifacts, or one MWR per affected artifact? Pass 1's recommendation is integrated, given how Foundation organizes the grammar.

6. AI Contract activation: the provisional AI Contract is in Pass 1's register as not-in-execution-spine. The fold's "dual-AI cross-check" element (Finding 3.3.6) effectively *uses* AI cross-check as a Metric Contract completeness signal — does this constitute "AI participates in the execution spine"? If yes, AI Contract activation may need to be in scope; if no, the AI cross-check is advisory-only (Conversation surface) per the Dual-Layer Interaction Model. Determines whether Pass 5 needs to propose AI Contract activation or treat the dual-AI verdict as advisory.

---

## 9. Pass 1 boundaries honoured

- Read-only.
- No code change.
- No DBCP.
- No ADR drafted.
- No service renamed.
- No primitive admitted, demoted, or relabeled.
- No `governance.state` transition triggered.
- No test-bench scenario authored or run.
- Foundation chapters consulted are the nine in `docs/foundation/`. v2 schema reference is `legacy-v2/.../contract-schemas/`. Live state queried via read-only Postgres MCP.
- This MWR is the sole writable output of Pass 1.

---

**End of Pass 1 register.**
