---
id: metric-contract-creation
order: 58
title: "Metric Contract Creation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, metric-catalog, metric-evaluation, canonical-field-seeding, canonical-contract-creation, business-field-and-business-object-onboarding, fiscal-time-and-temporal-gates, ai-gates, data-model-and-schema]
governing_sources:
  - The Contract Grammar
  - Metric Evaluation
  - Metric Catalog
  - Fiscal Time and Temporal Gates
governing_adrs:
  - DEC-d72560 (D301 MC variables bind to CF names; canonical-vocabulary)
  - DEC-c0290f (D315 Metric evaluation engine; formula-driven aggregation; grain-aware GROUP BY)
  - DEC-9d1f4b (D327 Shared dimension normalization in grain)
  - DEC-35b34b (D335 Aggregation authority; metric formulas own aggregation)
  - DEC-ecec75 (D068 One MC per KPI; metric architecture)
governing_sops:
  - legacy-v2/docs/sops/mc-creation-sop.md
errata_referenced: []
v2_sources:
  - sops/mc-creation-sop.md
diagrams: []
---

# Metric Contract Creation

## Scope

This chapter records the governed sequence by which a Metric Contract (MC) is created. The MC binds a metric definition's formula to real Canonical Object fields and produces governed Metric Snapshots. The chapter names the prerequisites (registered metric definition; active CCs for every required BO; registered CFs with cc_field_mapping coverage), the nine body keys an MC declares, the variable binding rule that names CFs (DEC-d72560), the role uniqueness rule for multi-CC bindings (DEC-35b34b), the constant-value rule for engine-readable formula constants, the sixteen quality checks the MC validation gate enforces, the AI-assisted variable binding path, the output BF registration step (with `source_standard: computed`), the temporal gate completeness threshold, the metric DAG pattern for secondary metrics that consume preceding metric outputs, and the end-to-end chain trace from the MC back to source tables. It records the boundary between MC creation and the metric evaluation runtime act. It records the as-built drift between the procedure and the platform's current MC state.

This chapter does not redefine the metric catalog (Metric Catalog), the metric evaluation runtime (Metric Evaluation), the CF registry (Canonical Field Seeding), or the CC the MC binds (Canonical Contract Creation).

**Governing source.** outline.md §4.6; The Contract Grammar.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Metric Contract identity | `contract.metric_contract` | Step 9 |
| Metric Contract version 1.0.0 (active) | `contract.contract_version` (with `category: metric`) | Step 9 |
| Output BFs (computed) | `contract.business_field` (with `source_standard: computed`) | Step 4 |
| CO bindings | `metric.metric_binding` | Step 5 (derived from MC body co_bindings) |

The MC is the last contract in the chain. Every upstream layer (BF, BO, OC, CC, CF, cc_field_mapping) is in place before the MC creation runs with valid variable bindings.

**Governing source.** The Contract Grammar; Metric Catalog.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | MC mutations are `@PlatformOnly()` JWT-guarded |
| Registered metric definition with formula and variables | The MC's `formula` and `variables[]` come from the definition; an unregistered metric has no formula to bind |
| Active CCs for every required BO | The MC's `co_bindings[].canonical_contract` references active CCs |
| Registered CFs and CC `cc_field_mapping` coverage | Every input variable's `field_code` is a registered CF, and each bound CC has `cc_field_mapping` entries producing the consumed CFs |

The fourth precondition is the chain prerequisite. An MC cannot be created with an input variable that does not resolve to a registered CF, and the CF must be produced by at least one bound CC's `cc_field_mapping`.

**Governing source.** Metric Catalog; Canonical Field Seeding; Canonical Contract Creation.

## The Variable Binding Rule (DEC-d72560)

The metric definition's formula carries variables with business-concept names. With DEC-d72560, those names are Canonical Field names, not Business Field names.

```
MC.variables[].field_code MUST be a registered Canonical Field name
```

A variable named `accounts_receivable_balance` is valid because `accounts_receivable_balance` exists in the `canonical_field` table and is produced by at least one CC's `cc_field_mapping`. A variable named `receivable_hdr_amount` is invalid because that name is a BF (source vocabulary), not a CF (metric vocabulary).

**Output variables (role: `output`)** are also registered, but as computed BFs and CFs:

| Field | Form |
|---|---|
| `source_standard` | `computed` (not from any external standard) |
| `object_class` | The metric short name (e.g., `dso`) |
| `property` | The output variable property (e.g., `days`) |
| Naming | `{metric_short_name}_{property}` (e.g., `dso_days`) |
| BO composition | None; computed BFs stand alone |

The output BF name is the platform's record that a metric produced a computed value. Downstream metrics in a metric DAG can bind to preceding MC's output BF.

**Governing source.** The Contract Grammar; Metric Evaluation.

## Body Keys an MC Declares

The MC body has nine keys (CR-MC-002), all required:

| Body key | Form | Decision type |
|---|---|---|
| `input_type` | `primary` (all inputs are CO fields) or `secondary` (any input is an upstream metric output) | Auto |
| `formula` | Object with `text` carrying the parseable formula expression | Auto from metric definition |
| `variables[]` | Array of `{var_code, role, field_code, description, value (for constants)}` entries | Decision (AI-assisted binding) |
| `co_bindings[]` | Array of `{canonical_contract, role, fields_used[]}`; one entry per bound CC; unique role per entry when binding multiple CCs | Auto from variable bindings; role is human-named |
| `temporal_gate` | Object with `required_periods`, `field_code`, `completeness_threshold` | Decision |
| `unit` | Output unit (e.g., `days`, `percent`, `currency`) | Auto from metric definition |
| `direction_code` | `lower-is-better`, `higher-is-better`, `target-is-optimal` | Auto from metric definition |
| `thresholds[]` | Four bands: `excellent`, `good`, `warning`, `critical`; each with `op`, `value`, `tenant_overridable` | Semi-auto (seed catalog values; human reviews) |
| `grain[]` | Metric grain; always explicit per CR-MC-008 | Decision (typically matches primary CC grain) |

A partial body that omits any of the nine keys is rejected at gate check 13.

**Governing source.** The Contract Grammar.

## Step 1 to Step 2: Select Metric Definition and Identify Required CCs

The actor selects an enriched metric definition from the metric catalog (Step 1) and identifies which CCs the formula consumes (Step 2). The mapping requires understanding the metric's business meaning: `total_receivables` indicates the AR receivable header BO, `net_credit_sales` indicates the billing document BO. The actor verifies CCs exist for each required BO; missing CCs are created via Canonical Contract Creation before the MC procedure proceeds.

**Governing source.** Metric Catalog; Canonical Contract Creation.

## Step 3: Bind Variables to CF Names

For each input variable, the actor finds the Canonical Field in the relevant CC's `cc_field_mapping` that matches the variable's semantic intent.

| Variable | CC | CF (field_code) | Source BF (in cc_field_mapping) |
|---|---|---|---|
| `I1` (total receivables) | `cc__receivable_hdr` | `accounts_receivable_balance` | `receivable_hdr_amount` |
| `I2` (net credit sales) | `cc__invoice_hdr` | `total_revenue` | `invoice_hdr_total_amount` |

AI-assisted binding (recommended) calls `POST /api/ai/suggest/mc-variable-binding` with the variable list and the available CC `cc_field_mapping` CFs; the maker-checker-gate envelope returns suggestions with confidence scores routed by CR-QG-MC-002 (auto-bind at or above 0.90, review 0.70 to 0.89, reject below 0.70). Manual binding inspects each CC's `cc_field_mapping` and matches by semantic meaning.

**Constants (role: `constant`)** carry a numeric `value` directly per the engine's read path. The variable's `field_code` may be a stable identifier (`constant_percentage_multiplier`, `constant_days_in_period`) for traceability; no CF registration is required for constants. The chapter records the constant rule as a check (CR-QG-MC-001 #16): every constant variable has a numeric `value` field, or a `field_code` that parses as a numeric literal. A missing value produces a `No values for 'C1'` rejection at evaluation time.

**Governing source.** AI Gates; The Contract Grammar; Metric Evaluation.

## Step 4: Register Output BFs

For each output variable (role: `output`), the actor registers a BF with `source_standard: computed`:

```
POST /api/business-fields
{
  "name": "dso_days",
  "definition": "Days Sales Outstanding (average collection period in days)",
  "function": "finance",
  "objectClass": "dso",
  "property": "days",
  "representationTerm": "Number",
  "dataType": "number",
  "piiClassification": "none",
  "sourceStandard": "computed"
}
```

The output BF is then certified via `POST /api/business-fields/{id}/certify`. The certification gate skips the semantic dedup and BO-scoped naming checks for computed BFs; the other seven checks apply.

**Governing source.** Business Field and Business Object Onboarding.

## Step 5: Build CO Bindings

The actor groups variables by the CC each binds to. For each CC, the actor records the CFs consumed in `fields_used[]`. When the MC binds two or more CCs, each `co_bindings[]` entry has a unique `role` value; per DEC-35b34b, the metric engine uses `role` as the alias key when routing CO payloads to formula variables. Duplicate roles collapse into a single alias and only the last CC's COs reach the formula.

```
"co_bindings": [
  { "canonical_contract": "cc__receivable_hdr", "role": "ar_source",      "fields_used": ["accounts_receivable_balance"] },
  { "canonical_contract": "cc__invoice_hdr",    "role": "billing_source", "fields_used": ["total_revenue"] }
]
```

Single-CC metrics use `role: "primary"`; no collision risk. Multi-CC metrics use descriptive roles (`ar_source`, `billing_source`, `accrual_source`) per the metric's semantics.

**Governing source.** Metric Evaluation.

## Step 6: Define Grain

MC grain is always explicit per CR-MC-008; it is never inherited from the CC. The grain typically matches the primary CC's grain:

```
"grain": [
  { "key": "company_code",   "source": "business_field",    "field_code": "company_code" },
  { "key": "fiscal_period",  "source": "evaluation_period" }
]
```

The MC may be coarser than the CC (a quarterly MC from a monthly CC) but never finer. For secondary metrics (`input_type: secondary`), grain may differ from preceding metrics within the same constraint.

The grain references shared dimensions by their shared names (`company_code`, not `ar_receivable_hdr_company_code`) per DEC-9d1f4b. The metric engine matches grain keys across COs from different BOs only when the names align.

**Governing source.** The Contract Grammar; Metric Evaluation.

## Step 7: Set Thresholds

The actor declares four bands of threshold classification:

| Band | Form |
|---|---|
| `excellent` | The best band; `op` follows direction (`lte` for lower-is-better, `gte` for higher-is-better) |
| `good` | Acceptable performance |
| `warning` | Concern threshold |
| `critical` | Alert threshold; `tenant_overridable: false` (the critical band is fixed) |

Threshold values come from the seed catalog where the metric definition carries them; the actor reviews and adjusts. The seed catalog's thresholds reflect industry baselines; the platform's MCs may tighten or loosen them per business judgment.

**Governing source.** Metric Catalog.

## Step 8: Set Temporal Gate

The temporal gate declares the completeness threshold for evaluation:

| Field | Form |
|---|---|
| `required_periods` | How many periods of CO data are required (typically `1`) |
| `field_code` | The field that carries the period identifier (e.g., `fiscal_period`) |
| `completeness_threshold` | Percentage of expected COs that must arrive before evaluation fires |

The completeness threshold matrix:

| Threshold | When |
|---|---|
| 100% | SOX-critical metrics; audit-facing KPIs (must have all source data) |
| 95% (default) | Most operational metrics (tolerates minor lag) |
| 80% to 90% | Directional or trending metrics (useful with partial data) |
| 50% to 79% | Early-warning or monitoring metrics (approximate signal beats no signal) |

The decision factors are: how many source systems contribute COs, whether the metric supports compliance or operations, whether partial evaluation is misleading, and whether the direction is sensitive to under-counting (a partial DSO can look artificially low).

**Governing source.** Fiscal Time and Temporal Gates; Metric Evaluation.

## Step 9: Assemble, Validate, Activate

The actor assembles the `barecount/metric/v1` envelope (header plus body) and submits to `POST /api/contracts` with `category: metric`. The MC validation gate runs all sixteen checks. On pass, the actor follows the contract lifecycle: submit for review, approve, then activate through the version lifecycle endpoints.

**Governing source.** The Contract Grammar.

## Quality Gates

The MC validation gate enforces sixteen checks at version submission.

| # | Check |
|---|---|
| 1 | Metric definition exists |
| 2 | Formula parseable (balanced parens, valid operators) |
| 3 | Every var_code in `formula.text` has a matching `variables[]` entry |
| 4 | Every `variables[]` entry is referenced in `formula.text` |
| 5 | Every input variable's `field_code` exists in the canonical_field table |
| 6 | Every output variable's `field_code` exists as a CF with `role: output` or as a computed BF |
| 7 | Every `co_bindings[].canonical_contract` references an active CC |
| 8 | Every `co_bindings[].fields_used[]` entry is a CF produced by the bound CC's `cc_field_mapping` |
| 9 | Every input variable's `field_code` appears in at least one `co_bindings[].fields_used[]` |
| 10 | Grain keys are valid; business_field grain references a BF that exists in at least one bound CC |
| 11 | Thresholds: exactly four bands; `op` consistent with `direction_code`; values monotonic |
| 12 | `input_type` consistent: `primary` if all bindings are CCs; `secondary` if any binding is an upstream MC |
| 13 | Structural completeness: all nine body keys present |
| 14 | Meta-schema validation: contract JSON conforms to `barecount/metric/v1` |
| 15 | Unique binding roles: when `co_bindings.length > 1`, every `role` is unique |
| 16 | Constants have value: every `variables[]` entry with `role: constant` has a numeric `value` field, or a `field_code` that parses as a numeric literal |

A version that fails any check stays in `draft`.

**Governing source.** The Contract Grammar; Metric Evaluation; Quality Gates and Chain Integrity.

## Metric DAGs: Secondary Metrics

A metric that consumes another metric's output is a secondary metric. The pattern:

```
MC: DSO  -> output BF/CF: dso_days
MC: DIO  -> output BF/CF: dio_days
MC: DPO  -> output BF/CF: dpo_days
MC: CCC  -> inputs: dso_days + dio_days - dpo_days
            input_type: secondary
            co_bindings reference preceding MCs (not CCs)
```

For secondary metrics:

| Field | Form |
|---|---|
| `input_type` | `secondary` |
| Input variable `field_code` | A preceding MC's output BF (or CF) |
| `co_bindings[].canonical_contract` | The upstream MC name (not a CC name) |
| Temporal gate | Waits for upstream Metric Snapshots, not COs |

Creation order: primary metrics first (DSO, DIO, DPO), then the secondary (CCC) that consumes their outputs.

**Governing source.** Metric Evaluation; The Contract Grammar.

## End-to-End Chain Trace

After MC creation and activation, the actor traces the full chain back to source tables:

```
MC variables (CF names)
  -> CC cc_field_mapping (CF -> BF)
  -> BO composition (BF in BO)
  -> OC field_mappings (BF -> source field)
  -> SC declared fields
  -> Source Catalog source.source_field
```

Every input variable resolves to a source field through this path. A break at any link is an L1 to L7 chain gap; the MC Chain Integrity chapter governs the diagnostic that classifies and remediates each break class.

**Governing source.** Chain Completeness and Verdict; MC Chain Integrity.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Metric Registration | Provides the registered metric definition the MC binds |
| Canonical Field Seeding | Provides the registered CFs the variables reference |
| Canonical Contract Creation | Provides the active CCs and `cc_field_mapping` the bindings consume |
| Business Field and Business Object Onboarding | Provides the BFs the preceding BO compositions carry; provides the certification surface for output computed BFs |
| MC Chain Integrity | Diagnoses and remediates MCs whose end-to-end chain breaks at any layer; consumes the MC's `variables[]`, `co_bindings[]`, and grain to evaluate twelve problem classes |
| Reader Creation | Independent at the MC layer; the Reader executes the OC, not the MC; the MC operates on COs that exist after canonical evaluation |

**Governing source.** Metric Registration; Canonical Field Seeding; Canonical Contract Creation; MC Chain Integrity.

## Drift Inventory

| Drift item | Form |
|---|---|
| Constants seed schema not yet extended | The seed catalog does not yet carry a `formula.constants` map per metric document; constant values are sourced from a curated map at `bc-core/src/registry/seed/d329-constants.ts` (the KNOWN_CONSTANTS map) at MC creation time. The later contract is that MC creation propagates the constant value into `contract_json.body.variables[].value` |
| AI-assisted binding accuracy | Variable-to-CF binding is the MC's core decision. The AI suggestion is only as good as the variable description plus the CF metadata. Sparse or generic descriptions produce low-confidence suggestions that the actor must resolve manually |
| Multi-CC role naming convention | Multi-CC bindings require unique roles. The chapter recommends descriptive roles (`ar_source`, `billing_source`); the platform does not enforce a vocabulary, only uniqueness. Inconsistent naming across MCs is recorded for review |
| Threshold review cadence | Thresholds reflect business judgment that may evolve. The platform supports new MC versions for threshold changes, but the cadence of re-review (annual? quarterly?) is not declared by this chapter and is owned by the metric stewardship in Operations chapters as they are drafted |
| Engine vs CC aggregation | Per DEC-35b34b, metric formulas own aggregation and `cc_field_mapping.resolution_rule_code` becomes documentary. An MC author reads the CC's resolution rules as the canonical-evaluation discipline; the actual metric value comes from the formula at metric evaluation. The two-layer model is the as-built; documentation that asserts CC rules govern metric values is stale |

**Governing source.** Metric Evaluation; Canonical Evaluation; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-d72560 | Establishes that MC variables bind to CF names (canonical vocabulary); BF names are not admissible as input variable field_codes |
| DEC-c0290f | Establishes the metric evaluation engine; formulas drive aggregation; grain-aware GROUP BY; the engine reads `variable.value` directly for constants |
| DEC-9d1f4b | Establishes shared dimension normalization in grain; metric grain uses shared BF names for cross-CC matching |
| DEC-35b34b | Establishes that metric formulas own aggregation; `cc_field_mapping.resolution_rule_code` becomes documentary; the role uniqueness rule per multi-CC binding |
| DEC-ecec75 | Establishes one MC per KPI as the metric architecture |

**Governing source.** Decisions: ADR Registry.

## References

- The Contract Grammar
- Metric Evaluation
- Metric Catalog
- Metric Registration
- Canonical Field Seeding
- Canonical Contract Creation
- Business Field and Business Object Onboarding
- MC Chain Integrity
- Chain Completeness and Verdict
- Fiscal Time and Temporal Gates
- AI Gates
- Quality Gates and Chain Integrity
- Data Model and Schema
- DEC-d72560: Canonical Field as 3rd contract primitive
- DEC-c0290f: Metric evaluation engine
- DEC-9d1f4b: Shared dimension normalization
- DEC-35b34b: Aggregation authority
- DEC-ecec75: One MC per KPI
- legacy-v2/docs/sops/mc-creation-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding



