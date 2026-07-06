---
id: the-contract-grammar
order: 5
title: "The Contract Grammar"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-object-model]
governing_sources:
  - Foundation F03 Contract Schemas (locked)
  - Foundation §2.2 (contract families)
  - Patent §1.3 (contract-governed execution)
governing_adrs:
  - DEC-0e3c64 (Observation Contract introduction)
  - DEC-136a23 (Reader Observation Schema, Canonical Mapping)
  - DEC-1edaaa (Observation Contract as first-class family)
  - DEC-29c324 (N:1 Metric Contract to Canonical Contract cardinality)
  - DEC-97bb94 (N:1 Source Object to Canonical Object cardinality)
  - DEC-d72560 (Business Field and Canonical Field split)
  - DEC-02f5a9 (Business Concept Registry — supersedes the BF/BO/CF vocabulary model)
errata_referenced:
  - FND-ERR-001
  - FND-ERR-002
  - FND-ERR-003
  - FND-ERR-004
v2_sources:
  - system/foundation/contract-schemas/index.md
  - system/foundation/contract-schemas/common-header.md
  - system/foundation/contract-schemas/source-v1.md
  - system/foundation/contract-schemas/admission-v1.md
  - system/foundation/contract-schemas/observation-v1.md
  - system/foundation/contract-schemas/canonical-v1.md
  - system/foundation/contract-schemas/metric-v1.md
  - system/foundation/contract-schemas/intervention-v1.md
  - system/foundation/contract-schemas/business-object-v1.md
  - system/foundation/contract-schemas/business-field-v1.md
  - system/foundation/contract-schemas/canonical-field-v1.md
diagrams:
  - DG-binding-chain
word_target: 5000
---

# The Contract Grammar

## Scope

This chapter defines the twelve grammar artifacts in the platform's contract-grammar taxonomy. Four of them — the three vocabulary primitives and the Canonical Mapping supporting schema — are superseded by the Business Concept Registry (DEC-02f5a9); the Artifact classification and Vocabulary sections state which artifacts govern and which persist only as the physical taxonomy retained until the greenfield cutover. The chapter classifies each artifact, defines the common envelope and header used by contract-family instances, describes the family-specific body shape each active family declares, and states the versioning, immutability, binding, and lifecycle rules that apply across the grammar. It does not describe contract storage in the database (Data Model and Schema), API validation and publication workflows (API Surface), or the runtime behavior of Readers and evaluators that apply these artifacts (Sources and the Catalog through Chain Completeness and Verdict).

## Artifact classification

The platform grammar taxonomy comprises twelve artifacts. Six are active contract families. One is a provisional family and one is retired. The remaining four — one supporting schema (Canonical Mapping) and three primitives (Business Object, Business Field, Canonical Field) — are superseded by the Business Concept Registry (DEC-02f5a9) and remain only as the physical taxonomy retained until the greenfield cutover. Together they define the grammar referenced by publication, binding, and boundary evaluation.

| Artifact | Classification | Status | Primary governing record | Active at runtime |
|---|---|---|---|---|
| Source Contract | Contract family | Active | Source family schema | Yes |
| Admission Contract | Contract family | Active | DEC-0e3c64 | Yes |
| Observation Contract | Contract family | Active | DEC-0e3c64, DEC-136a23, DEC-1edaaa | Yes |
| Canonical Contract | Contract family | Active | Canonical family schema | Yes |
| Metric Contract | Contract family | Active | DEC-29c324 | Yes |
| Intervention Contract | Contract family | Active | Intervention family schema | Yes |
| Canonical Mapping | Supporting schema | Superseded (DEC-02f5a9) | DEC-136a23 | Yes |
| Business Object | Primitive | Superseded (DEC-02f5a9) | Primitive specification | No |
| Business Field | Primitive | Superseded (DEC-02f5a9) | Primitive specification | No |
| Canonical Field | Primitive | Superseded (DEC-02f5a9) | DEC-d72560 | No |
| AI Contract | Provisional family | Provisional | Provisional AI schema | Not in execution spine |
| Extraction Contract | Retired family | Retired | D069 | No |

> **Vocabulary model superseded — DEC-02f5a9.** The three primitives (Business Object, Business Field, Canonical Field) and the Canonical Mapping supporting schema are superseded by the Business Concept Registry: one governed registry of `entity.property` Business Concepts replaces them. They persist physically until the greenfield cutover (DEC-02f5a9 §6); the Vocabulary section below states the governing model.

The `FND-ERR-001` entry documents the historical gap between this taxonomy and Foundation's earlier enumeration of contract families. The taxonomy in this chapter is the canonical v3 reading.

## Envelope and common structure

Each instance of an active contract family is represented as a JSON document with four top-level keys. The same envelope also applies to the provisional AI Contract. Envelope validation uses `additionalProperties: false` at the envelope level and at nested objects unless a family schema explicitly defines an extension point.

| Key | Type | Required | Purpose |
|---|---|---|---|
| `$contract` | string constant | Yes | Meta-schema identifier declaring family and schema version, for example `barecount/canonical/v1`. |
| `version` | string (semver) | Yes | Version of the published contract instance. This is distinct from the meta-schema version. |
| `header` | object | Yes | Common governance and identity metadata shared across families. |
| `body` | object | Yes | Family-specific declaration governed by the family's schema. |

The envelope applies to the six active contract families and to the provisional AI Contract. The vocabulary primitives — Business Object, Business Field, Canonical Field — do not use the envelope; until the greenfield cutover they are governed through primitive specifications and relational constraints rather than through JSON contract instances. Under DEC-02f5a9 they are superseded by the Business Concept Registry (see the Vocabulary section), which is likewise not an envelope-using contract family.

## Common header

The common header is shared by the six active contract families and by the provisional AI Contract. It contains sixteen direct keys. Each key is required. Tenant customization does not modify header fields. Tenant-specific variation is expressed through a separate Contract Binding record (the Three-level governance section).

| Key | Type | Purpose |
|---|---|---|
| `contract_id` | uuid | Matches the parent contract record primary key. Immutable. |
| `name` | slug | Stable machine name. Immutable after creation. |
| `display_name` | string | Human-readable contract name. |
| `category` | enum | One of `source`, `admission`, `observation`, `canonical`, `metric`, `intervention`, `ai`. |
| `kind` | string | Subtype within the family, for example `per_table` for a Source Contract. |
| `created_at` | ISO 8601 datetime | Publication timestamp. Immutable. |
| `owner` | object | Ownership metadata: `team`, `email`, `slack`, `oncall`. |
| `tags` | array of slug strings | Classification tags. |
| `description` | string | Contract purpose statement. |
| `domain` | string | Business domain, for example `finance` or `sales`. |
| `subdomain` | string | Business subdomain, for example `accounts_receivable`. |
| `tenant_scope` | object | Scope metadata: `scope`, `provider`, `variant`. |
| `governance` | object | Governance state and classification: `state`, `data_classification`, `pii`, `sox_critical`. |
| `compatibility_policy` | enum | Compatibility rule applied to this family instance. |
| `lineage` | array | Predecessor relationships declared by the contract. |
| `bindings` | array | Target relationships declared by the contract. |

Two header fields govern relationships between this contract and other artifacts.

| Field | Declares | Required elements |
|---|---|---|
| `lineage[]` | Predecessor dependencies | `from_contract_id`, `from_version`, `relation`, optional `note` |
| `bindings[]` | Target relationships | `target_contract_id`, `target_category`, `relation`, optional mapping reference, optional `note` |

`lineage[].relation` uses the enum `derives_from`, `extends`, `validates`, `maps_from`, `measures`, `responds_to`, or `references`.

`bindings[].relation` uses the enum `extracts_from`, `structured_by`, `validates`, `consumed_by`, `maps_from`, `measures`, `responds_to`, or `references`.

`governance.state` uses the DDL-enforced lifecycle `draft`, `review`, `approved`, `active`, or `superseded`. Legacy states such as `deprecated` and `retired` do not appear at the version level. Section 4.11 maps those legacy terms to the governing lifecycle.

## Active contract families

The six active contract families share the envelope and common header defined above. Each family declares a family-specific `body`. This section describes the grammar-level responsibility of each family. How each family is applied at runtime is described in the Operating Model chapters named in the relevant cross-reference.

### Source Contract

**Purpose.** A Source Contract declares the structural shape of one source table or API endpoint: field inventory, field types, primary key, and whether a field is a standard field or a tenant-scoped extension.

**Body elements.** The body declares six required keys: `table_code`, `label`, `source_system_version_id`, `module_code`, `fields[]`, and `primary_key[]`. Each `fields[]` entry declares `field_code`, `label`, `type`, `nullable`, and `z_extension`.

**Governs.** Structural declaration of admitted source state. Admission validation uses the Source Contract as the structural reference.

**Referenced by.** Admission Contracts for structural validation, Observation Contracts for field selection, and Canonical Contracts indirectly through Observation Contracts.

**Disallowed behaviors.**
- A Source Contract body includes validation rules, runtime configuration, or lifecycle state.
- A Source Contract declares fields that do not exist in the referenced source table or API endpoint.
- A Source Contract version is modified in place after publication to reflect a source-system schema change.

**Governing source.** Foundation; D245 (SC body purity); D253 (structural completeness).

### Admission Contract

**Purpose.** An Admission Contract declares the rules under which observed source state is admitted at the admission boundary: identity semantics, required fields, structural validation, temporal rules, and rejection policy.

**Body elements.** The body declares the referenced Source Contract, field-level required and nullable rules, business-key composition, observation timestamp discipline, and admissibility rules defining rejection versus warning behavior.

**Governs.** The admission evaluation boundary (The Evaluation Boundaries). Each admitted observation is validated against an Admission Contract at the boundary. Rejected observations emit Evidence but do not emit Source Objects.

**Referenced by.** Readers and admission services at runtime (Admission and Observation).

**Disallowed behaviors.**
- An Admission Contract declares canonical interpretation of admitted state.
- An Admission Contract is applied retroactively to previously admitted Source Objects.
- An Admission Contract version is modified after publication.

**Governing source.** Foundation.

### Observation Contract

**Purpose.** An Observation Contract declares field selection from a Source Contract to business-vocabulary fields and defines the resulting Source Object shape preserved at admission.

**Body elements.** The body declares the referenced Source Contract, `observation_field_map`, and the resulting `observation_schema`. Each `observation_field_map` entry binds one source field to one Business Concept together with role and nullability (DEC-02f5a9; formerly Business Field).

**Governs.** Field selection and business-vocabulary binding at admission. The Observation Contract is the governed source of this mapping. A denormalized runtime copy may appear on Reader Flavor artifacts, but the governed source remains the Observation Contract.

**Referenced by.** Readers at runtime (Admission and Observation) and Canonical Contracts through the shared business vocabulary.

**Disallowed behaviors.**
- An Observation Contract declares canonical evaluation logic.
- A runtime Reader Flavor diverges from the governed Observation Contract rather than being regenerated from it.
- An Observation Contract maps the same source field to multiple Business Concepts without a declared role distinction.

**Governing source.** DEC-0e3c64, DEC-136a23, DEC-1edaaa; FND-ERR-001 and FND-ERR-002.

### Canonical Contract

**Purpose.** A Canonical Contract declares the canonical form of one Entity (formerly Business Object; DEC-02f5a9): its grain, field selection, resolution rules across multiple Source Objects, resolved output schema, semantic rules, and temporal gate.

**Body elements.** The body declares eight required keys: `business_object_code`, `evaluation_tier`, `grain[]`, `field_selection[]`, `resolution_rules[]`, `resolved_schema`, `semantic_rules[]`, and `temporal_gate`. Under DEC-02f5a9 the `business_object_code` key names an Entity and `field_selection[]` references Business Concepts; the schema-level key naming is settled at the greenfield cutover.

**Governs.** The canonical evaluation boundary (The Evaluation Boundaries). Each Canonical Object emission applies one Canonical Contract at the boundary.

**Cardinality.** One Canonical Contract may reference N Source Contracts. One Canonical Object evaluation may consume N Source Objects. FND-ERR-004 and DEC-97bb94 supersede the earlier linear framing.

**Referenced by.** Metric Contracts for canonical inputs. Under DEC-02f5a9, field-level binding is to Business Concepts directly; the Canonical Mapping identity layer is superseded.

**Disallowed behaviors.**
- A Canonical Contract body includes runtime configuration, schedule-specific parameters, or tenant-specific values.
- A Canonical Contract is applied to admit Source Objects.
- A Canonical Contract is modified to retroactively alter a previously produced Canonical Object version.

**Governing source.** Foundation; DEC-97bb94 and FND-ERR-004; D244 and D245.

### Metric Contract

**Purpose.** A Metric Contract declares a numeric assertion over one or more Canonical Object versions: referenced Canonical Contracts, formula, grain, temporal gate, thresholds, and unit semantics.

**Body elements.** The body declares metric identity, formula expression, referenced Canonical Contract versions through `metric_binding`, grain alignment, required parameters, evaluation timing, result shape and units, and admissible comparison operations. Under DEC-02f5a9, Metric Contract inputs reference Business Concepts and the grain is a typed reference to a Registry entity.

**Governs.** The metric evaluation boundary (The Evaluation Boundaries). Each Metric Snapshot emission applies one Metric Contract at the boundary.

**Cardinality.** One Metric Contract may reference N Canonical Contracts. One Metric Snapshot evaluation may read N Canonical Object versions across those referenced contracts. FND-ERR-003 and DEC-29c324 supersede the earlier linear framing.

**Referenced by.** Intervention Contracts and secondary Metric Contracts.

**Disallowed behaviors.**
- A Metric Contract references raw Source Objects.
- A Metric Contract is used to produce metric values by read-time query rather than boundary evaluation.
- A Metric Contract is modified to change a historical Metric Snapshot value.

**Governing source.** Foundation; DEC-29c324 and FND-ERR-003.

### Intervention Contract

**Purpose.** An Intervention Contract declares the conditions under which an Action Object is created, the eligible Metric Snapshot references, the required threshold or comparison conditions, declared intent semantics, outcome resolution rules, and closure conditions.

**Body elements.** The body declares activation mode, trigger conditions, assignee pool, closure window, and evaluation model for outcome resolution against preserved snapshots.

**Governs.** The action evaluation boundary (The Evaluation Boundaries). Each Action Object emission applies one Intervention Contract at the boundary.

**Referenced by.** Operational surfaces that display and track actions (Action Evaluation and Frontend Experience). Operational execution of an action is external to the platform and does not modify the Action Object.

**Disallowed behaviors.**
- An Intervention Contract is modified to rebind an existing Action Object to newer Metric Snapshots.
- An Intervention Contract defines metric logic.
- An Intervention Contract permits open-ended actions with no closure condition.

**Governing source.** Foundation.

## Supporting schema: Canonical Mapping

> **Superseded — DEC-02f5a9.** Canonical Mapping as a Business-Field-to-Canonical-Field *identity* mapping is eliminated by the Business Concept Registry: with one Business Concept there is no source-side / canonical-side identity to bind. Field-resolution content (type coercion, unit conversion, reduction over grain, temporal interpretation) survives within the Observation and Canonical Contract bodies. The description below applies until the greenfield cutover (DEC-02f5a9 §6); new authoring does not create Canonical Mappings.

Canonical Mapping is a governed and versioned supporting schema. It is not a contract family, but it is part of the grammar because it binds field vocabularies across contract families.

**Purpose.** Canonical Mapping binds Source-side Business Fields to Canonical-side Canonical Fields. Observation Contracts declare the input Business Fields. Canonical Contracts declare the output Canonical Fields. Canonical Mapping records the field-level correspondence used by a specific Canonical Contract version.

**Body elements.** The body is a collection of `cc_field_mapping` entries. Each entry records the target Canonical Field, the source Business Field or reduction across multiple Business Fields, and the Canonical Contract version for which the mapping applies.

**Governs.** Field-level binding during canonical evaluation. Each Canonical Object version records the Canonical Mapping version applied. Mapping changes produce new Canonical Object versions going forward. They do not alter prior versions.

**Referenced by.** Canonical Contract versions. Metric Contracts reference Canonical Fields only and are not directly coupled to the mapping layer.

**Disallowed behaviors.**
- A Canonical Mapping is modified to retroactively change a prior Canonical Object's field values.
- A Canonical Mapping binds a Business Field to a Canonical Field outside the scope of the declared Canonical Contract version.

**Governing source.** DEC-136a23.

## Vocabulary: the Business Concept Registry

DEC-02f5a9 (Business Concept Registry) supersedes the earlier three-primitive vocabulary model. The platform's business vocabulary is one governed registry of Business Concepts — not three separate primitives (Business Object, Business Field, Canonical Field) joined by a Canonical Mapping.

| Construct | Role | Replaces |
|---|---|---|
| Entity | A globally governed, role-bearing business concept; simple, or composite / dependent | Business Object |
| Property | Belongs to exactly one entity; kind `value` or `reference`; `identity_role` `identity_bearing` or `descriptive` | (new) |
| Business Concept | The addressable, observable unit of vocabulary, identified as `entity.property` | Business Field and Canonical Field, collapsed into one concept |

Concept identity is exactly `entity.property` — two levels, unique by construction (`UNIQUE(entity_id, property_id)`); family is classification, not identity. Standards are evidence and candidate source, never identity authority. Contracts reference Business Concepts by identity. The Registry is versioned and governed; it is not a contract-family instance and does not use the contract envelope.

The earlier primitives and the Canonical Mapping identity layer are superseded. They persist physically until the greenfield cutover (DEC-02f5a9 §6); new authoring is against the Registry. The full model is `business-concept-registry.md`; DEC-02f5a9 is the governing decision.

## Provisional family: AI Contract

The AI Contract is a provisional family. A provisional meta-schema exists in the grammar inventory. The readiness baseline does not include an AI Contract in the execution spine.

**Scope of provisional status.** The family is declared so governance exists before first runtime use. It is not counted among the six active families for execution-spine purposes. The runtime chapters do not reference it.

**Promotion rule.** Promotion from provisional to active requires an ADR that declares the evaluation boundary the family governs, how it composes with Canonical or Metric Contracts already governing that boundary, and what Evidence and Lineage it emits.

**Current effect.** AI-assisted behavior may occur at advisory or surface layers. It does not produce authoritative objects under the execution model until the family is activated by governance.

**Governing source.** Provisional AI meta-schema in the v2 grammar inventory.

## Retired family: Extraction Contract

The Extraction Contract is a retired family. It governed an earlier extraction-oriented ingress model. That model has been superseded by the combined use of Source Contract, Admission Contract, and Observation Contract.

| Historical concern | Replacement artifact |
|---|---|
| Declaring expected source-table structure | Source Contract |
| Declaring admission-time validation rules | Admission Contract |
| Declaring field selection and business-vocabulary binding | Observation Contract |

New Extraction Contracts are not authored. Existing Extraction Contracts remain preserved as historical artifacts. They do not participate in the active execution spine.

**Governing source.** D069.

## Versioning and immutability on publish

Every contract family instance is identified by `contract_id` plus `version`. The following rules apply across the six active families and Canonical Mapping.

| Rule | Effect |
|---|---|
| Immutability on publish | A contract version in `governance.state == "active"` is immutable. Neither header nor body may be modified in place. |
| New versions for changes | Any change is expressed as a new version. The prior version remains preserved. |
| Version coexistence | Multiple versions may coexist. Authoritative objects remain bound to the version under which they were produced. |
| Semantic versioning | `MAJOR` indicates incompatible change, `MINOR` backward-compatible addition, `PATCH` backward-compatible correction. |

Contract version changes do not alter previously produced Canonical Objects, Metric Snapshots, or Action Objects. This is Invariant III applied to contract-governed evaluation.

## Three-level governance

Contract grammar is governed at three operationally distinct levels. A lower level cannot modify artifacts of a higher level.

| Level | Artifact | Governs | Scope |
|---|---|---|---|
| Master Shape | Meta-schema per family | Shape of the family: keys, types, governance tags, and validation rules | Platform-locked. Changes require an ADR. |
| Platform Instance | Contract version | A specific governed contract in the family | Platform-locked once `active`. Changes produce new versions. |
| Tenant Override | Contract Binding | Tenant-scoped extensions to a specific contract version | Tenant-scoped. Cannot remove platform-declared fields or modify platform-declared rules. |

This three-level model is recorded in D233. Tenant customization occurs only at the Contract Binding layer. Contracts themselves are platform-governed artifacts (D164).

![Binding Chain · field resolution path from a Source Table through the active contract families to a Metric Snapshot. The Observation Contract acts as a double bridge: it directs the Reader against the Source Contract and maps to Business Fields consumed by the Canonical Contract.](/docs/assets/diagrams/DG-binding-chain.svg)

*The diagram shows the pre-cutover binding chain. Under DEC-02f5a9 the binding target is the Business Concept, not the Business Field; the diagram is regenerated at the greenfield cutover.*

## Lifecycle and deprecation policy

The `governance.state` field in the common header uses a five-state linear lifecycle. Rollback does not occur within a version.

| State | Meaning | Entry rule |
|---|---|---|
| `draft` | Authoring in progress | Initial state on creation |
| `review` | Authoring complete and under review | Promoted from `draft` |
| `approved` | Review complete but not yet active | Promoted from `review` |
| `active` | In production use at the governed boundary | Promoted from `approved` at release time |
| `superseded` | Replaced by a later version of the same contract | Promoted from `active` when a newer version enters `active` |

Legacy terms such as `deprecated` and `retired` do not apply at the version level. Version-level replacement is represented by `superseded`. Family-level status is represented in the taxonomy in the Artifact classification section.

When a new version enters `active`, the prior version moves to `superseded`, and the new version records its predecessor in `lineage[]` through an appropriate relation such as `derives_from` or `extends`. Prior authoritative objects produced under the superseded version remain valid and readable as preserved state.

Family-level retirement occurs only through a governance act recorded as an ADR. D069 retired the Extraction Contract family. Family-level provisional status indicates a declared but not yet operational family, as with the AI Contract.

## Chapter boundaries

This chapter has defined the twelve grammar artifacts, the common envelope and header used by contract-family instances, the family-specific bodies of the six active families, the Business Concept Registry that supersedes the three vocabulary primitives and the Canonical Mapping supporting schema (DEC-02f5a9), and the versioning, governance, and lifecycle rules that apply across the grammar. It has deferred:

- Evaluation boundary semantics and once-only application rules (The Evaluation Boundaries).
- The authority model and ADR mechanism governing grammar change (The Authority Model).
- Per-family runtime behavior (Sources and the Catalog through Action Evaluation).
- Contract storage and the meta-schema table (Data Model and Schema).
- Contract publication and validation at the API boundary (API Surface).

## References

- Foundation: Contract families (earlier taxonomy; superseded by §4.1)
- Foundation F03 Contract Schemas: authoritative source for per-family body shapes
- Foundation Common Header: sixteen-key header shared across families
- Patent §1.3: Contract-governed execution
- FND-ERR-001: Observation Contract outside six-family Foundation list (Errata)
- FND-ERR-002: Observation Contract governed source versus Reader Flavor runtime copy (Errata)
- FND-ERR-003: N:1 Metric Contract to Canonical Contract cardinality (Errata)
- FND-ERR-004: N:1 Source Object to Canonical Object cardinality (Errata)
- DEC-0e3c64: Observation Contract introduction (Decisions)
- DEC-136a23: Reader Observation Schema and Canonical Mapping (Decisions)
- DEC-1edaaa: Observation Contract as first-class family (Decisions)
- DEC-29c324: N:1 Metric Contract to Canonical Contract (Decisions)
- DEC-97bb94: N:1 Source Object to Canonical Object (Decisions)
- DEC-d72560: Business Field and Canonical Field split (Decisions)
- DEC-02f5a9: Business Concept Registry — vocabulary identity model, supersedes the BF/BO/CF primitives (Decisions)
- Business Concept Registry: the adopted vocabulary identity model (docs/implementation/business-concept-registry.md)
- The Invariants: The Invariants
- The Object Model: The Object Model
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Runtime
- Action Evaluation: Intervention and Action
- Data Model and Schema
- API Surface
- Contract Schemas reference
- Decisions: ADR Registry
- Errata: Errata Ledger
