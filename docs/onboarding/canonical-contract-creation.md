---
id: canonical-contract-creation
order: 57
title: "Canonical Contract Creation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-evaluation-boundaries, business-vocabulary, canonical-evaluation, business-field-and-business-object-onboarding, canonical-field-seeding, observation-contract-creation, fiscal-time-and-temporal-gates, data-model-and-schema, api-surface]
governing_sources:
  - The Contract Grammar
  - Canonical Evaluation
  - Business Vocabulary
  - Fiscal Time and Temporal Gates
governing_adrs:
  - DEC-d72560 (D301 CC translates BF vocabulary to CF vocabulary via cc_field_mapping)
  - DEC-9d1f4b (D327 Shared dimension normalization in field_selection)
  - DEC-9361cd (D302 cc_field_mapping; one BF to many CFs with filters; canonical uniqueness)
  - DEC-35b34b (D335 Aggregation authority; metric formulas own aggregation; cc_field_mapping rules become documentary)
governing_sops:
  - legacy-v2/docs/sops/cc-creation-sop.md
errata_referenced: []
v2_sources:
  - sops/cc-creation-sop.md
diagrams: []
---

# Canonical Contract Creation

## Scope

This chapter records the governed sequence by which a Canonical Contract (CC) is created. The CC defines the universal shape of a Canonical Object (CO): the field selection from the Business Object's BF composition, the dimensional grain that gives a CO its identity, the resolution rules that handle multi-source field conflicts, the resolved JSON Schema for CO output, the semantic rules that enforce business-level invariants, and the temporal gate that schedules canonical evaluation. The chapter names the prerequisites (approved Business Object; certified BFs; registered Canonical Fields; recommended active OC for chain verification), the eight body keys a CC declares, the thirteen quality checks the CC validation gate enforces, the BF-to-CF mapping step (DEC-d72560) that translates source vocabulary into metric vocabulary, the shared dimension normalization rule (DEC-9d1f4b), and the Canonical Mapping construct that wires OCs to a CC for a given source system. It records the CC versioning and impact-cascade rules. It records the boundary between CC creation and the Metric Contract that consumes CO bindings. It records the as-built drift between the procedure and the platform's current CC state.

This chapter does not redefine the canonical evaluation runtime act (Canonical Evaluation), the contract grammar's two-vocabulary model (The Contract Grammar; DEC-d72560), the BF and BO registries (Business Vocabulary), the CF registry (Canonical Field Seeding), or the Observation Contract that feeds the CC at runtime via Canonical Mapping (Observation Contract Creation).

**Governing source.** outline.md §4.6; The Contract Grammar.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Canonical Contract identity | `contract.canonical_contract` | Step 8 |
| Canonical Contract version 1.0.0 (active) | `contract.contract_version` (with `category: canonical`) | Step 8 |
| BF-to-CF mappings | `contract.cc_field_mapping` | Step 4b |
| Canonical Mapping (per OC, per source system) | `contract.canonical_mapping` plus `contract.canonical_mapping_version` | The CM creation surface (separate, after CC and OC both exist) |

One CC governs one Business Object (CR-CC-001). All tenants sharing that BO get the same CC. Tenant customization happens at `contract_binding`, not at the CC.

**Governing source.** The Contract Grammar.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | CC mutations are `@PlatformOnly()` JWT-guarded |
| Approved BO with certified BFs | The CC's `field_selection[]` references certified BFs composed into the BO |
| Registered Canonical Fields for every BF the CC will map | The CC's `cc_field_mapping` entries reference `canonical_field_id`; the onboarding service does not auto-create CFs |
| Active OC for at least one source system (recommended) | A CC without an OC cannot produce COs; the CC plus OC plus Canonical Mapping triangle is the minimum operational set |
| AI verification surface reachable (for AI-assisted resolution rule heuristics) | Resolution rule generation from BF semantic roles uses the maker-checker-gate envelope where helpful |

The CC can be created without an OC; `field_selection[]` derives from the BO's field composition, not from OC. But the CC cannot be fully chain-verified without an OC. The recommended order is OC first, then CC, then Canonical Mapping; that order produces the chain in the same shape it will run.

**Governing source.** The Contract Grammar; Canonical Field Seeding; Observation Contract Creation.

## The CC as Translator

The CC is the translator between two vocabularies. It consumes BF names (source vocabulary, from OC `field_mappings[].business_field_code`) and produces CF names (metric vocabulary, consumed by MC `variables[].field_code`):

```
OC.field_mappings[].business_field_code    (source-side; BFs come in)
  = CC.field_selection[] entry              (THIS CONTRACT selects which BFs form the CO)
  = business_field.name                     (BF registry as source of truth)

CC.cc_field_mapping                         (THIS CONTRACT translates BF to CF)
  -> canonical_field.field_name             (CF registry)
  = MC.variables[].field_code               (MC binds formula variables to these)
```

Every entry in `field_selection[]` is a certified BF composed into the referenced BO. Every BF in `field_selection[]` has exactly one `cc_field_mapping` entry that maps it to a registered Canonical Field. The CC creation service validates both halves of the translator.

**Governing source.** The Contract Grammar; Canonical Field Seeding.

## Body Keys a CC Declares

The CC body has eight keys (CR-CC-002), all required, all fixed:

| Body key | Form | Decision type |
|---|---|---|
| `business_object_code` | The approved BO this CC governs | Selection |
| `evaluation_tier` | `1` for primary CC (from SOs) or `2` for derived CC (from preceding COs) | Auto from BO `tier_code` |
| `grain[]` | Dimensional identity declarations: `business_field` source or `evaluation_period` source | Decision (domain knowledge) |
| `field_selection[]` | BF names from the BO composition that compose the CO | Semi-auto (default all; optional exclude) |
| `resolution_rules[]` | Per-field rule for handling multi-source conflicts (`sum`, `average`, `latest`, `earliest`, `assert_equal`, `prefer_source`) | Semi-auto (heuristic from BF semantic role; human reviews) |
| `resolved_schema` | JSON Schema for CO output | Auto from BFs in field_selection plus their data types |
| `semantic_rules[]` | Business-level validation constraints (required_field, field_range, field_pattern, field_enum, cross_field, business_invariant) | Decision (optional) |
| `temporal_gate` | Object with `schedule.cron`, `schedule.timezone`, optional `readiness_gate`, `lookback_window` | Decision (evaluation schedule) |

A CC body that omits any of the eight keys is rejected at gate check 10 (structural completeness).

**Governing source.** The Contract Grammar; Canonical Evaluation.

## Grain: The Key Decision

Grain declares dimensional identity. Two COs with the same grain values and the same evaluation period are the same canonical observation; the grain is the CO's identity (CR-CC-004). Grain has two sources:

| Source | Meaning |
|---|---|
| `business_field` | A BF value carried into the CO (e.g., `company_code`) |
| `evaluation_period` | Platform evaluation period metadata (e.g., `fiscal_period`) |

Grain progresses from finer (source) to coarser (metric) through the chain:

| Layer | Grain |
|---|---|
| SC and AC | Source table primary key |
| OC | Identity semantics (may dedup) |
| CC | Business grain (coarser; aggregated from line items) |
| MC | Metric grain (same or coarser than CC) |

Grain reduction happens at CC via `resolution_rules[]`. Line-level amounts sum into a period total; company code asserts equal across the lines that compose a period.

Common grain patterns:

| BO Type | Typical grain | Why |
|---|---|---|
| Transaction header (invoice, PO, payment) | `company_code + fiscal_period` | Metrics aggregate by company by period |
| Transaction line (invoice line, PO line) | `company_code + fiscal_period + document_number` | Line-level detail within a document |
| Master data (vendor, customer, material) | `entity_identifier` | One CO per master record (no period) |
| Balance (GL balance, AR aging) | `company_code + account_code + fiscal_period` | Balance by account by period |

**Governing source.** Canonical Evaluation; The Contract Grammar.

## Resolution Rules

When multiple SOs contribute to the same CO grain (two observations of the same company in the same period), each field may arrive with different values. Resolution rules declare what to do.

| Rule | Use | Example |
|---|---|---|
| `sum` | Additive measures (amounts, quantities, counts) | Sum all invoice amounts in the period |
| `average` | Rate measures (percentages, ratios) | Average discount across invoices |
| `latest` | Temporal fields | Use the most recent document date |
| `earliest` | First-occurrence fields | Use the earliest creation date |
| `assert_equal` | Dimension and identity fields | All SOs must agree on company code |
| `prefer_source` | One source is authoritative | Take the value from the first SO in admission order |

The default rule per semantic role is heuristic and reviewed by the actor:

| BF semantic role | Default rule |
|---|---|
| `identifier` | `assert_equal` |
| `dimension` | `assert_equal` |
| `measure` | `sum` |
| `temporal` | `latest` |
| `descriptor` | `prefer_source` |

The heuristic covers the common cases. Domain judgment overrides where needed.

Per DEC-35b34b, the cc_field_mapping `resolution_rule_code` becomes documentary at the runtime layer; the metric formula owns the authoritative aggregation. The CC's resolution rules remain the contract's declared intent for the canonical evaluation step that produces the CO; the metric engine reconciles aggregation at metric evaluation. The chapter records both layers because both are operative: CC resolution is the canonical evaluation discipline; metric formula aggregation is the metric evaluation discipline.

**Governing source.** Canonical Evaluation; Metric Evaluation; The Contract Grammar.

## Shared Dimension Normalization (DEC-9d1f4b)

The five shared dimensions (`company_code`, `currency_code`, `language_code`, `country_code`, `unit_of_measure`) use their shared BF name in `field_selection[]`, `resolved_schema`, `grain`, and `resolution_rules[]`. The BO-scoped variants (e.g., `receivable_hdr_company_code`) are not used at the CC layer.

The reason is grain matching across multi-CC metrics. A metric that binds both `cc__receivable_hdr` and `cc__invoice_hdr` needs one grain key (`company_code`) that resolves identically across both. If each CC used its BO-scoped variant, the metric engine could not match grain keys across COs from different BOs.

The CC onboarding service automatically replaces BO-scoped variants of shared dimensions with their shared names when deriving `field_selection[]` from BO composition. Manual CC creation in the bc-admin UI uses the shared names directly.

**Governing source.** The Contract Grammar; Canonical Evaluation.

## Step 1 to Step 4: Select BO, Define Grain, Select Fields, Define Resolution Rules

The actor selects an approved BO (Step 1), defines `grain[]` from domain knowledge (Step 2), starts with all BFs in `field_selection[]` and optionally excludes (Step 3), and assigns resolution rules from the semantic-role heuristic with overrides (Step 4).

For grain fields, the resolution rule is `assert_equal` with `on_conflict: quarantine` or `on_conflict: log`; the grain dimensions are identical across SOs by definition, and a conflict on a grain dimension is a chain integrity violation that the CC declares its response to.

**Governing source.** The Contract Grammar.

## Step 4b: Define BF-to-CF Mapping

For each BF in `field_selection[]`, the actor declares the corresponding Canonical Field name in `cc_field_mapping`:

| BF (source vocabulary) | Resolution rule | CF (metric vocabulary) |
|---|---|---|
| `receivable_hdr_amount` | `sum` | `accounts_receivable_balance` |
| `receivable_hdr_customer_code` | `assert_equal` | `customer_identifier` |
| `invoice_hdr_total_amount` | `sum` | `total_revenue` |

For each mapping, the actor verifies the CF exists (`GET /api/canonical-fields?fieldName={cf_name}` returns a row); a missing CF is a prerequisite failure routed back to Canonical Field Seeding. The actor sets `resolution_rule_code` (`sum`, `latest`, `assert_equal`, `count_distinct`, `count_where_not_null`).

The mapping must be semantically coherent. The chapter records four common semantic mismatches that pass structural validation but break metric evaluation:

| BF | CF | Rule | Issue |
|---|---|---|---|
| `receivable_hdr_amount` (number) | `accounts_receivable_balance` (currency) | `sum` | Correct |
| `receivable_hdr_fiscal_year` (code) | `average_accounts_receivable_balance` (currency) | `count_distinct` | Wrong: fiscal year is not a balance amount |
| `receivable_hdr_due_date` (date) | `payment_receipt_date` (date) | `latest` | Correct |
| `receivable_hdr_amount` (number) | `number_of_invoices_paid` (count) | `count_where_not_null` | Acceptable only when the BF is used as an existence signal, not as the amount |

The heuristic is: if the CF name implies a measure (balance, amount, revenue), the BF is numeric and the rule is `sum`, `average`, or `latest`. If the CF name implies a count, the rule is `count_distinct` or `count_where_not_null` on a stable identifier BF, not on a random field. Filling the mapping just to satisfy a chain integrity check (R11) without semantic coherence silently produces wrong metric values; the MC Chain Integrity chapter governs the diagnostic that catches this.

**Governing source.** Canonical Field Seeding; The Contract Grammar; MC Chain Integrity.

## Step 5: Auto-Generate Resolved Schema

The `resolved_schema` is auto-generated from `field_selection[]` and BF data types. Properties are one per field with type derived from BF `data_type`. Required fields are grain fields plus BFs marked `is_required: true` in BO composition. Type mapping: BF `number` to JSON Schema `number`, BF `string` to `string`, BF `date` to `string` with `format: "date"`, etc. The actor does not author `resolved_schema` directly.

**Governing source.** The Contract Grammar.

## Step 6: Define Semantic Rules (Optional)

Semantic rules are business-level validation constraints applied at canonical evaluation. The categories are:

| Category | Form |
|---|---|
| `required_field` | Field must not be null in the CO |
| `field_range` | Numeric bounds (e.g., `net_amount >= 0`) |
| `field_pattern` | Regex validation (e.g., company code format) |
| `field_enum` | Allowed values |
| `cross_field` | Cross-field invariants (e.g., `net_amount <= gross_amount`) |
| `business_invariant` | Complex business rules |

The array can be empty. Adding rules later requires a new CC version.

**Governing source.** Canonical Evaluation.

## Step 7: Define Temporal Gate

The temporal gate declares when canonical evaluation runs and how it determines readiness:

| Field | Form |
|---|---|
| `schedule.cron` | Cron expression for evaluation cadence |
| `schedule.timezone` | IANA timezone (`UTC`, `Asia/Kolkata`) |
| `readiness_gate.strategy` | `wait_for_all`, `wait_for_quorum`, `best_effort` (Tier 2 only) |
| `readiness_gate.dependencies[]` | Upstream CC names to wait for (Tier 2 only) |
| `readiness_gate.timeout` | Max wait before proceeding (Tier 2 only) |
| `lookback_window` | ISO 8601 duration declaring how far back to look for SOs (`P1M`, `P1D`) |

Tier 1 CCs do not require a `readiness_gate`. Tier 2 CCs (derived; consume preceding COs) require `readiness_gate.strategy` per gate check 8.

**Governing source.** Fiscal Time and Temporal Gates.

## Step 8: Assemble, Validate, Activate

The actor assembles the `barecount/canonical/v1` envelope (header plus body) and submits to `POST /api/contracts` with `category: canonical`. The CC validation gate runs all thirteen checks below. On pass, the actor follows the contract lifecycle: submit for review, approve, then activate through the version lifecycle endpoints. `submit` alone does not make the version active.

**Governing source.** The Contract Grammar.

## Quality Gates

The CC validation gate enforces thirteen checks at version submission.

| # | Check |
|---|---|
| 1 | BO exists and is approved |
| 2 | No other active CC for the same BO (CR-CC-001) |
| 3 | Every `field_selection[]` entry is a certified BF composed into the referenced BO |
| 4 | Every grain key with `source: "business_field"` has a matching `field_code` in `field_selection[]` |
| 5 | Every grain field has an `assert_equal` resolution rule |
| 6 | Every `resolution_rules[].field_code` exists in `field_selection[]` |
| 7 | `resolved_schema.properties` keys equal `field_selection[]`; `required` includes grain fields; types match BF data types |
| 8 | If `evaluation_tier = 2`, `temporal_gate.readiness_gate` is populated |
| 9 | Every `semantic_rules[].field` exists in `field_selection[]` |
| 10 | Structural completeness: all eight body keys present |
| 11 | Meta-schema validation: contract JSON conforms to `barecount/canonical/v1` |
| 12 | `cc_field_mapping` coverage: every BF in `field_selection[]` has exactly one mapping; no orphans, no duplicates |
| 13 | `cc_field_mapping` semantic coherence: BF `semantic_role` and CF `unit_type_code` are compatible (warning, not block; human review recommended) |

A version that fails any structural check stays in `draft`. A check 13 warning surfaces as a warning attached to the CC; it does not block activation but is recorded for review by the MC Chain Integrity sweep.

**Governing source.** The Contract Grammar; Quality Gates and Chain Integrity.

## Canonical Mapping: Wiring OC to CC

The CC defines the CO shape. The Canonical Mapping (CM) defines which sources feed it. Without a CM, the canonical evaluator cannot resolve Source Objects into Canonical Objects.

The CM creation runs after both OC and CC exist for the same BO. One CM per (CC, source system) pair; multiple source systems mean multiple CMs feeding one CC.

The CM Onboarding service automates field overlap computation:

```
POST /api/onboarding/cm/preview
{
  "canonical_contract_id": "<cc-uuid>",
  "observation_contract_id": "<oc-uuid>"
}
```

The preview returns:

| Field | Form |
|---|---|
| `overlap[]` | BF names present in both OC `field_mappings[]` and CC `field_selection[]` |
| `unmappedCcFields[]` | CC fields with no OC source (gap) |
| `unmappedOcFields[]` | OC fields not in CC (acceptable; CC does not need all OC fields) |
| `checks[]` | Validation results |

```
POST /api/onboarding/cm/create
{
  "canonical_contract_id": "<cc-uuid>",
  "observation_contract_id": "<oc-uuid>"
}
```

The create endpoint produces `canonical_mapping` plus `canonical_mapping_version` (v1.0.0, active) and auto-derives `field_resolutions` from the overlap.

The CM has its own invariant set:

| Invariant | Rule |
|---|---|
| CM-INV-001 | One active mapping per (CC, source system) pair |
| CM-INV-002 | Platform-scoped; no `tenant_id` |
| CM-INV-003 | `mapping_json` is the authoritative source for field resolution |
| CM-INV-004 | At least one field overlaps between OC and CC |
| CM-INV-005 | All CC grain fields are in the overlap |
| CM-INV-006 | Immutable past `draft`; new version for changes |
| CM-INV-007 | Targets a specific CC version; CC upgrade may invalidate mapping |

**Governing source.** Canonical Evaluation.

## CC Versioning and Impact Cascade

When a CC is updated, the change affects preceding Observation/Canonical Mapping contracts and later Metric Contracts contracts.

| Change | New CC version | Breaking |
|---|---|---|
| Add field to `field_selection` | Yes | Non-breaking (additive) |
| Remove field from `field_selection` | Yes | Breaking (later MC may reference it) |
| Change grain | Yes | Breaking (CO identity changes) |
| Change resolution rule for a field | Yes | Non-breaking (same CO shape, different values) |
| Add semantic rule | Yes | Non-breaking (stricter validation) |
| Change temporal gate schedule | Yes | Non-breaking (timing only) |

Removing a field is blocked while any active MC references it. Changing grain rebuilds all CMs for the CC and reviews all bound MCs (MC grain is the same as or coarser than CC grain).

**Governing source.** The Contract Grammar; Quality Gates and Chain Integrity.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Business Field and Business Object Onboarding | Provides the approved BO and certified BF composition the CC consumes |
| Canonical Field Seeding | Provides the registered CFs the `cc_field_mapping` references |
| Observation Contract Creation | Provides the OC whose `field_mappings[]` are the source-side input the Canonical Mapping wires to this CC |
| Metric Contract Creation | Consumes the CC via `co_bindings[]`; the MC's `fields_used[]` references CFs produced by this CC's `cc_field_mapping` |
| MC Chain Integrity | Catches semantic incoherence in `cc_field_mapping` (the warning at check 13) and the runtime aggregation drift covered by DEC-35b34b |

**Governing source.** Business Field and Business Object Onboarding; Canonical Field Seeding; Observation Contract Creation; Metric Contract Creation; MC Chain Integrity.

## Drift Inventory

| Drift item | Form |
|---|---|
| `cc_field_mapping` resolution rules are documentary | Per DEC-35b34b, the metric engine no longer honors `resolution_rule_code` at runtime; metric formulas own aggregation. The CC still declares the rules as the canonical-evaluation discipline, but the rules' authority at metric evaluation is the formula, not the CC. Operators reading the CC must understand the two-layer aggregation model |
| Semantic coherence check is a warning, not a block | Gate check 13 surfaces semantic mismatches as warnings. A CC with a check 13 warning activates and produces COs; the warning is recorded for review by MC Chain Integrity. A future enhancement may promote check 13 to a block per ADR queue |
| AI-assisted resolution rule heuristic accuracy | The semantic-role heuristic is good for the common cases but mis-classifies the long tail. The actor reviews and overrides; the chapter does not assume the heuristic is correct |
| Tier 2 readiness gate completeness | Tier 2 CCs require `readiness_gate.strategy`, but the `dependencies[]` array may be incomplete in the as-built data; some Tier 2 CCs declare implicit dependencies via convention (cc_name pattern matching) rather than explicit declaration. The convention is being deprecated; explicit dependencies are required |
| CM creation is a separate procedure | The CM is governed in this chapter (because it is logically part of CC), but its creation surface is independent. A CC without a CM does not produce COs; the chain status reports an L4 mapping gap |

**Governing source.** Canonical Evaluation; Metric Evaluation; MC Chain Integrity; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-d72560 | Establishes CC as the translator between BF (source) and CF (metric) vocabularies; the `cc_field_mapping` is the platform's record of the translation |
| DEC-9d1f4b | Establishes shared dimension normalization; the CC uses shared names in `field_selection`, `resolved_schema`, `grain`, and `resolution_rules` |
| DEC-9361cd | Establishes `cc_field_mapping` as one BF to many CFs with optional filters; canonical uniqueness invariant |
| DEC-35b34b | Establishes that metric formulas own aggregation; `cc_field_mapping.resolution_rule_code` becomes documentary at the runtime layer |

**Governing source.** Decisions: ADR Registry.

## References

- The Contract Grammar
- Canonical Evaluation
- Metric Evaluation
- Business Vocabulary
- Business Field and Business Object Onboarding
- Canonical Field Seeding
- Observation Contract Creation
- Metric Contract Creation
- MC Chain Integrity
- Fiscal Time and Temporal Gates
- Quality Gates and Chain Integrity
- Data Model and Schema
- API Surface
- DEC-d72560: Canonical Field as 3rd contract primitive
- DEC-9d1f4b: Shared dimension normalization
- DEC-9361cd: cc_field_mapping (1-to-many with filters)
- DEC-35b34b: Aggregation authority
- legacy-v2/docs/sops/cc-creation-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding


