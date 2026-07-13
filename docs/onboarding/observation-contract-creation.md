---
id: observation-contract-creation
order: 56
title: "Observation Contract Creation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-evaluation-boundaries, business-vocabulary, sources-and-the-catalog, admission-and-observation, business-field-and-business-object-onboarding, source-and-admission-contract-creation, ai-gates, ai-trust-and-verification, data-model-and-schema, api-surface]
governing_sources:
  - The Contract Grammar
  - Admission and Observation
  - Business Vocabulary
  - AI Gates
governing_adrs:
  - DEC-d72560 (D301 Two-vocabulary model; OC operates in source-side BF vocabulary)
  - DEC-9d1f4b (D327 Shared dimension normalization across the chain)
governing_sops:
  - legacy-v2-archive/docs/sops/oc-creation-sop.md
errata_referenced: []
v2_sources:
  - sops/oc-creation-sop.md
diagrams: []
---

# Observation Contract Creation

## Scope

This chapter records the governed sequence by which an Observation Contract (OC) is created. The OC is the Reader's complete execution plan: it names the source tables to read, the fields of business interest, the join semantics across tables, the record identity rules, the deduplication policy, and the JSON Schema of the Source Object the Reader produces. The chapter names the prerequisites (active SC and AC pairs; approved Business Object; certified Business Fields), the seven body keys an OC declares, the twelve quality checks the OC validation gate enforces, the AI-assisted field mapping path with confidence-band routing, the field mapping confirmation step that triggers backflow into the BF-SF alias table, the secondary-OC pattern for multi-table or multi-source coverage of one BO, and the Z-field discovery feedback loop. It records the boundary between OC creation and the Reader (which references the OC) plus the Canonical Contract (which translates the OC's BF vocabulary into CF vocabulary). It records the as-built drift between the procedure and the platform's current OC state.

This chapter does not redefine the contract grammar's two-vocabulary model (The Contract Grammar; DEC-d72560), the admission and observation runtime acts (Admission and Observation), the BF and BO registries (Business Vocabulary; Business Field and Business Object Onboarding), or the SC and AC pair the OC references (Source and Admission Contract Creation).

**Governing source.** outline.md §4.6; The Contract Grammar.

## What the Procedure Produces

| Artifact | Persistent store | Created by |
|---|---|---|
| Observation Contract identity | `contract.observation_contract` | Step 8 |
| Observation Contract version 1.0.0 (active) | `contract.contract_version` (with `category: observation`) | Step 8 |
| Observation field mappings | `contract.observation_field_map` | Step 8 (derived from OC body field_mappings) |
| Backflow into BF-SF alias table | `contract.business_field_alias` (provenance `confirmed`) | Step 6 confirmation surface |

One OC governs the observation of one Business Object from one Source Version (CR-OC-001). A BO that needs observation from multiple source systems requires one OC per system. A BO whose fields span multiple source tables in one system uses join semantics or secondary OCs as recorded in this chapter.

**Governing source.** The Contract Grammar.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | OC mutations are `@PlatformOnly()` JWT-guarded |
| Approved Business Object with certified Business Fields | The OC's `field_mappings[].business_field_code` references certified BFs that are composed into the referenced BO |
| Active Source Contract and Admission Contract pairs for every source table the OC references | The OC's `source_references[]` cite active SC and AC version identifiers; draft or archived SC and AC are rejected at gate check 3 |
| Source Catalog populated with the source tables and fields the OC will reference | The catalog's `source.source_object` and `source.source_field` are the substrate the SC declares against; the OC reads field declarations through SC, not through the catalog directly |
| AI verification surface reachable | AI-assisted field mapping calls the maker-checker-gate envelope; absence of the surface forces manual mapping with explicit drift recording |

A precondition that fails is not bypassed; the prerequisite is fixed before OC creation runs.

**Governing source.** The Contract Grammar; Source and Admission Contract Creation; AI Gates.

## The Two-Vocabulary Model and the OC

The OC operates in source-side vocabulary only. Its `field_mappings[]` use BF names (`business_field_code`) on one side and source field codes (`source_field`) on the other. The OC does not reference Canonical Field names; that translation happens at the Canonical Contract via `cc_field_mapping`. The contract chain enforces the separation:

```
OC.field_mappings[].business_field_code
  = CC.field_selection[] entry              (consumed by CC)
  = CC.resolved_schema.properties key       (consumed by CC)
  = business_field.name                     (in the BF registry)
```

A field mapping that uses a CF name on the BF side is a chain violation; the gate check 4 rejects it because the name does not exist in the BF registry.

**Governing source.** The Contract Grammar; Canonical Contract Creation.

## Body Keys an OC Declares

The OC body has seven keys (CR-OC-002), all required, all fixed:

| Body key | Form | Decision type |
|---|---|---|
| `source_version_id` | The Source Version identifier from the catalog | Selection |
| `business_object_code` | The approved BO this OC observes for | Selection |
| `source_references[]` | Array of `{source_object_id, sc_version_id, ac_version_id}`, one per source table | Auto from SC and AC registries |
| `join_semantics[]` | Array of join declarations for multi-table OCs; empty for single-table | Decision (PK/FK domain knowledge) |
| `field_mappings[]` | Array of source-field to Business Field mapping entries, including the mapping rule | Decision (AI-assisted) |
| `identity_semantics` | Object with `identity_fields[]`, `scope`, `deduplication`, `timestamp_field` | Semi-auto from source PK |
| `so_schema` | JSON Schema for the Source Object output | Auto from field_mappings and identity_fields |

A partial body that omits any of the seven keys is rejected at gate check 11 (structural completeness). The OC is all-or-nothing on its body shape.

**Governing source.** The Contract Grammar.

## Step 1: Select the Business Object

The actor browses approved BOs in the registry and selects the target. The OC will observe data for this BO. The actor records the BO's `business_object_code` and its certified BF composition; the BFs are the targets the OC's field_mappings will populate.

**Governing source.** Business Vocabulary.

## Step 2: Select the Source System Version

The actor selects the registered Source Version from the catalog. The OC's `source_version_id` records this selection.

**Governing source.** Sources and the Catalog.

## Step 3: Identify Source Tables

The actor identifies which source tables in the selected version contain data for the selected BO. The decision requires source-system domain knowledge: knowing that SAP AR data lives in BSID and BSAD, AP data lives in BKPF plus BSEG, and so on. For each identified table, the actor verifies an active SC-and-AC pair exists; missing pairs are created via Source and Admission Contract Creation before the OC procedure proceeds.

**Governing source.** Source and Admission Contract Creation.

## Step 4: Define Join Semantics (Multi-Table Only)

For a single-table OC, `join_semantics[]` is empty. For a multi-table OC, the actor declares one join entry per table relationship:

| Field | Form |
|---|---|
| `left_table`, `right_table` | The two source table codes |
| `join_keys[]` | Array of `{left, right}` field-name pairs |
| `join_type` | `inner` or `left` |
| `role_per_table` | `header`, `line_item`, `reference`, or `lookup` |

The decision requires PK/FK knowledge. The OC does not infer joins; the actor declares them.

**Governing source.** Admission and Observation.

## Step 5: Map Source Fields to Business Fields

This is the OC's core decision. For each BF in the BO's composition, the actor identifies the corresponding source field. Three modes are admissible:

**AI-assisted (recommended for new mappings).** The actor calls `POST /api/ai/suggest/oc-field-mapping` with the BO composition and the source table fields. The AI maker-checker-gate envelope returns suggestions with confidence scores. The Field Mapping Confidence Gate (CR-QG-OC-002) routes the suggestions:

| Confidence | Action |
|---|---|
| At or above 0.90 | Auto-accept |
| 0.70 to 0.89 | Suggested with review flag; human confirms |
| Below 0.70 | Rejected; the actor maps manually or leaves the BF unmapped |
| No match | Unmapped; the BF is either not sourced from this table, or has no source equivalent |

**Seed-driven (for known source systems).** The Seed Catalog carries pre-configured mappings for well-known systems (SAP, Salesforce, Oracle); the OC consumes them as starting suggestions and the actor confirms.

**Manual (fallback).** The actor inspects each source field's name, type, and description and assigns the BF mapping by domain judgment.

For each accepted mapping, the actor selects the normalization rule. Not every BF requires a mapping; a BF that is not sourced from the selected source system is left unmapped, and the later CC decides which mapped fields to select.

**Shared dimension naming.** When mapping source fields to the five shared dimensions (`company_code`, `currency_code`, `language_code`, `country_code`, `unit_of_measure`), the OC uses whichever BF name exists in the BO composition. The CC normalizes shared dimensions in its field_selection per DEC-9d1f4b, so the OC-to-CC field overlap remains consistent regardless of which variant the OC uses.

**Governing source.** AI Gates; Business Vocabulary.

## Step 6: Confirm Mappings (Triggers Backflow)

Confirmed mappings are submitted to `POST /api/field-mapping/confirm` with the accepted set:

```
POST /api/field-mapping/confirm
{
  "confirmedMappings": [
    {
      "sourceFieldId": "<UUID>",
      "businessFieldId": "<UUID>",
      "sourceFieldName": "BUKRS",
      "businessFieldName": "invoice_hdr_company_code"
    }
  ]
}
```

The confirm endpoint builds the observation schema (projectedFields, standardFields, fieldMap) and writes back to `contract.business_field_alias`: for each confirmed mapping, the endpoint resolves the source system type and creates an alias row with `provenance_code: confirmed` if one does not exist for the BF and system pair. The backflow enriches the BF-SF alias substrate for future OCs that map the same BF in the same source system.

**Governing source.** Business Field and Business Object Onboarding.

## Step 7: Define Identity Semantics and SO Schema

The actor declares record identity:

| Field | Form |
|---|---|
| `identity_fields[]` | Source field codes that uniquely identify a record (typically the source table PK) |
| `scope` | `per_table` or `cross_table` |
| `deduplication` | `latest_by_timestamp`, `first_seen`, or `reject` |
| `timestamp_field` | The source field carrying the record timestamp (for `latest_by_timestamp`) |

Identity fields are semi-auto: the SC declares key markers, and the OC creation surface pre-populates `identity_fields[]` from those markers. The actor reviews and confirms.

The `so_schema` is auto-generated from field_mappings plus identity_fields. Properties are the union of all source fields referenced; required fields are identity fields plus key source fields; types derive from SC field type declarations. The actor does not author `so_schema` directly.

**Governing source.** Admission and Observation.

## Step 8: Assemble, Validate, and Activate

The actor assembles the full `barecount/observation/v1` envelope (header plus body) and submits to `POST /api/contracts` with `category: observation`. The OC validation gate (CR-QG-OC-001) runs all twelve checks below. On pass, the actor follows the contract lifecycle: submit for review, approve, then activate through the version lifecycle endpoints. `submit` alone does not make the version active.

**Governing source.** The Contract Grammar.

## Quality Gates

The OC validation gate enforces twelve checks at version submission.

| # | Check |
|---|---|
| 1 | BO exists and is approved |
| 2 | Source version exists in the catalog |
| 3 | Every `source_references[].sc_version_id` and `ac_version_id` references active contracts |
| 4 | Every `field_mappings[].business_field_code` references a certified BF |
| 5 | Every mapped BF is composed into the referenced BO via `business_object_field` |
| 6 | Every `field_mappings[].source_field` exists in the SC's declared field list |
| 7 | No two `field_mappings[]` map to the same `business_field_code` |
| 8 | Every `identity_semantics.identity_fields[]` exists as a source field in at least one referenced table |
| 9 | Every `join_semantics[].join_keys` references fields that exist in the respective source tables |
| 10 | `so_schema.properties` keys equal the union of source fields referenced in `field_mappings[]` and `identity_semantics.identity_fields[]` |
| 11 | Structural completeness: all seven body keys present with valid values |
| 12 | Meta-schema validation: contract JSON conforms to `barecount/observation/v1` |

A version that fails any check stays in `draft`; the actor revises and resubmits. The gate does not selectively pass; it passes all twelve or it fails.

**Governing source.** The Contract Grammar; Quality Gates and Chain Integrity.

## Multi-OC Architecture per BO

A BO often spans multiple source tables. A single OC binds fields from one source table, or from a joined set declared by `join_semantics[]`. Fields in additional tables require additional OCs for the same BO. The chapter records three reasons:

| Reason | Example |
|---|---|
| Fields live in different tables | `invoice_hdr_total_amount` lives in VBRK; `invoice_hdr_gl_account_identifier` lives in BSEG |
| The same BO is observed from multiple source systems | One OC per system (SAP and Oracle each get their own OC for the same BO) |
| Different source versions have different table structures | SAP ECC and S/4HANA may need separate OCs for the same BO |

Secondary OCs append the source table to the name to disambiguate: `oc__{system}__{bo}` is the primary OC; `oc__{system}__{bo}__{table}` is the secondary OC.

The CC resolution layer aggregates Source Objects from all OCs for a BO. When multiple OCs produce overlapping BFs, the CC `resolution_rules[]` (CC declares them; see Canonical Contract Creation) determine the canonical value. The OC does not declare resolution; it declares observation.

**Governing source.** Canonical Contract Creation.

## The Z-Field Discovery Feedback Loop

A Z-field is a source field the Reader discovers at runtime that is not in the OC's `field_mappings[]`. The Reader reports the Z-field. The platform reviews the report and routes the Z-field through one of three paths:

| Disposition | Action |
|---|---|
| Promote to standard (platform-wide) | Register a new BF, add it to the BO composition, add it to the OC field_mappings (new OC version), add it to the CC field_selection (new CC version) |
| Keep as tenant Z-field | The tenant adds it via `contract_binding.extensions_json.z_field_mappings[]`; no OC or CC version change |
| Ignore | Add to `contract_binding.override_json.ignored_fields[]`; the Reader suppresses future discovery reporting for this field |

The triage uses signals: multi-tenant demand, frequency of appearance in Source Objects, PII presence, technical or debug nature, and emptiness rate. The platform does not promote a Z-field that no metric will consume; the demand-pull discipline applies here too.

**Governing source.** Admission and Observation; Tenancy and Binding.

## Boundary with Other Onboarding Chapters

| Chapter | Relationship |
|---|---|
| Source and Admission Contract Creation | Provides the active SC and AC pairs the OC references in `source_references[]` |
| Business Field and Business Object Onboarding | Provides the certified BFs and approved BO the OC consumes in `field_mappings[]` and `business_object_code`; the BF-SF alias table that the AI mapping suggestions consult |
| Canonical Field Seeding | Independent at the OC layer; the OC operates in BF vocabulary only |
| Canonical Contract Creation | Consumes the OC's `field_mappings[].business_field_code` set; the CC's `field_selection[]` overlaps the OC's mapped BFs |
| Reader Creation | The Reader Flavor binds the OC at runtime; a Reader without an active OC cannot execute Admission Runs |
| MC Chain Integrity | Treats an OC with `field_mappings[]` gaps (a CC field with no source mapping) as an L4 chain gap |

**Governing source.** Source and Admission Contract Creation; Business Field and Business Object Onboarding; Canonical Contract Creation; Reader Creation.

## Sign Indicator Pattern (Unsigned Source Tables)

Some source tables store amounts unsigned, with a separate indicator field carrying the debit/credit direction (e.g. SAP ECC sub-ledger tables BSID/BSAD/BSIK/BSAK use `SHKZG` where `S` = debit, `H` = credit). When the OC maps such a table, the indicator field is declared with a special role so the CCv2 resolver can apply sign correction at the canonical boundary.

The OC field_mapping entry for the indicator field uses:

| Property | Value |
|---|---|
| `role` | `sign_indicator` |
| `transform` | `direct` |
| `transform_params` | `{ "credit_value": "H" }` |
| `business_concept_id` | The `debit_credit_code` concept on the grain entity |
| `representation_term` | `code` |
| `data_type` | `string` |

The sign indicator field is **not projected** to the Canonical Object. It is resolver metadata: the CCv2 resolver reads it, and when the indicator value equals `credit_value`, negates all `representation_term: "amount"` value fields in the CO payload. This satisfies Invariant I (meaning evaluated once at the canonical boundary) — the metric layer receives correctly-signed amounts and does not need to know about source-system sign conventions.

Source tables that store signed amounts (e.g. SAP ACDOCA Universal Journal with `HSL`/`TSL`) do not declare a sign_indicator mapping. The resolver passes amounts through as-is.

**Governing source.** [SAP ECC — Sign Handling](../reference/source-systems/sap-ecc/contracts.md); The Contract Grammar; Canonical Contract Creation.

## Drift Inventory

| Drift item | Form |
|---|---|
| OC v1 to v2 schema migration | The chapter describes `barecount/observation/v1` with `business_field_code`. The platform has migrated to `barecount/observation/v2` which uses `business_concept_id` (BCF concept identity), `representation_term`, `role`, `transform`, and `transform_params`. A full chapter rewrite for v2 is pending |
| AI-assisted mapping confidence calibration drifts over time | Source-system field metadata changes; the AI's suggestion confidence reflects the metadata at suggestion time. A re-suggestion after a Seed Catalog enrichment may produce different scores |
| Backflow into the alias table is one-directional | Alias rows tagged `confirmed` are the OC's confirmation trail. Aliases tagged `dictionary` (from prior bulk migrations) are not upgraded to `confirmed` until an OC explicitly confirms them |
| Z-field discovery is reactive | The Reader reports Z-fields when it sees them at runtime. A tenant whose Reader never executes against a particular table never reports Z-fields for that table; the discovery surface is event-driven, not exhaustive |
| Multi-OC architecture coordination | When a BO has multiple OCs, the integrity surface aggregates field_mappings from all OCs to determine BF coverage. A new OC that maps a previously-unmapped BF improves the BO's chain status; a deactivated OC may regress it |
| OC versioning during Z-field promotion | A Z-field promotion requires a new OC version (the field is added to `field_mappings[]`). The new version supersedes the prior; the prior remains in the version history but is no longer active |

**Governing source.** Admission and Observation; Tenancy and Binding; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-d72560 | Establishes the two-vocabulary model; the OC operates in source-side BF vocabulary only |
| DEC-9d1f4b | Establishes shared dimension normalization; this chapter records the OC's freedom to use either the shared name or a BO-scoped variant for shared dimensions, with the CC normalizing on the CC side |

The OC family-level governance (CR-OC-001 through CR-OC-011, twelve quality checks at CR-QG-OC-001, AI confidence routing at CR-QG-OC-002) is recorded in `legacy-v2-archive/docs/sops/oc-creation-sop.md` and in `legacy-v2-archive/docs/system/foundation/contract-requirements-v1.md`. New ADR files for the family-level rules may be filed if the policies are restated outside the v2 location.

**Governing source.** Decisions: ADR Registry.

## References

- The Contract Grammar
- Admission and Observation
- Business Vocabulary
- Sources and the Catalog
- Source Registration
- Business Field and Business Object Onboarding
- Source and Admission Contract Creation
- Canonical Field Seeding
- Canonical Contract Creation
- Metric Contract Creation
- Reader Creation
- MC Chain Integrity
- AI Gates
- AI Trust and Verification
- Tenancy and Binding
- Quality Gates and Chain Integrity
- Data Model and Schema
- API Surface
- DEC-d72560: Canonical Field as 3rd contract primitive (two-vocabulary model)
- DEC-9d1f4b: Shared dimension normalization
- legacy-v2-archive/docs/sops/oc-creation-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding



