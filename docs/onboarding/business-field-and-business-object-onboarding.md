---
id: business-field-and-business-object-onboarding
order: 53
title: "Business Field and Business Object Onboarding"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, business-vocabulary, sources-and-the-catalog, source-registration, ai-gates, ai-trust-and-verification, data-model-and-schema]
governing_sources:
  - Business Vocabulary
  - The Contract Grammar
  - AI Gates
governing_adrs:
  - DEC-f66378 (D292 BO-scoped BF naming; D290 standards-sourced BFs; D294 five shared dimensions are absorbed into this ADR's body)
governing_sops:
  - legacy-v2/docs/sops/bf-bo-onboarding-sop.md
  - legacy-v2/docs/sops/bf-sf-alias-sop.md
errata_referenced: []
v2_sources:
  - sops/bf-bo-onboarding-sop.md
  - sops/bf-sf-alias-sop.md
diagrams: []
---

# Business Field and Business Object Onboarding

## Scope

This chapter records the governed sequence by which Business Fields (BFs) and Business Objects (BOs) are admitted to the platform vocabulary from authoritative external standards (OAGIS as the primary tier; ISO 20022, XBRL, IFRS, and UN/CEFACT as secondary tiers; BareCount Standard as the last resort tier). It names the derivation rules that map a standard's structure to BFs and BOs, the BO-scoped naming discipline (DEC-f66378) and its five shared dimension exceptions, the certification and approval gates each artifact passes, and the BF to source-field alias table that later Observation Contracts consume. It records the boundary between vocabulary onboarding and the contract families that consume the vocabulary. It records the as-built drift between the procedure and the platform's current vocabulary state.

This chapter does not redefine the BF and BO taxonomy itself (Business Vocabulary), the contract families that bind BOs (Source and Admission Contract Creation, Observation Contract Creation, Canonical Contract Creation, Metric Contract Creation), the AI maker-checker-gate envelope (AI Gates), or the source catalog the alias table refers to (Sources and the Catalog).

**Governing source.** outline.md §4.6; Business Vocabulary.

## What the Procedure Produces

A complete vocabulary onboarding produces three classes of artifact plus an alias trail per BF.

| Artifact | Persistent store | Created by |
|---|---|---|
| Certified Business Field | `contract.business_field` | Step 3 of the per-domain run |
| Approved Business Object with composition | `contract.business_object` plus `contract.business_object_field` | Step 5 of the per-domain run |
| BF-to-source-field alias | `contract.business_field_alias` | The alias procedure (Steps A1-A2) |
| Standard provenance trail | `business_field.source_standard`, `business_field.standard_ref`, `business_object.source_standard`, `business_object.standard_ref` | Steps 1-5 |

Every BF and BO carries a `source_standard` value identifying the tier it was sourced from; the value is one of `oagis`, `iso_20022`, `xbrl_gaap`, `ifrs`, `uncefact`, `bc_standard`, or `computed` (for output BFs that later Metric Contracts produce). The chapter governs the first six values; the `computed` value is governed by Metric Contract Creation.

**Governing source.** Business Vocabulary; The Contract Grammar.

## Prerequisites

| Precondition | Why it is required |
|---|---|
| Cognito authenticated session for a platform actor | Vocabulary mutations are `@PlatformOnly()` JWT-guarded |
| Standard source data is loaded in MongoDB or available as an extract | OAGIS lives in `seed_oagis_components`; ISO 20022 lives in `seed_iso20022`; XBRL lives in `seed_xbrl_gaap`; new tier-2 standards arrive as JSON or XSD extracts |
| BF and BO endpoints are reachable | `GET /api/business-fields?limit=1` and `GET /api/business-objects?limit=1` return 200 |
| AI verification surface is reachable | The certification and approval gates call AI verification; absence of the surface forces unverified-status admission with explicit drift recording |
| The five shared dimension list is current | `company_code`, `currency_code`, `language_code`, `country_code`, `unit_of_measure` are the only BFs admissible without a BO prefix (D294 in the v2 SOP shorthand; the policy is recorded in DEC-f66378's body) |

The procedure is the same regardless of caller. Bulk programmatic loads call the same endpoints the bc-admin UI calls; the gates are enforced at the service layer, not at the UI.

**Governing source.** Business Vocabulary; AI Gates.

## BO Derivation Rules from a Standard

The OAGIS source structures the platform's primary tier. Each OAGIS Noun (Invoice, PurchaseOrder, etc.) carries one or more Components (Header, Line, SubLine, Schedule). The platform's BO derivation maps one Component to one BO, not one Noun to one BO.

The mapping rules are explicit:

| Rule | Form | Example |
|---|---|---|
| One Component is one BO | A multi-component Noun produces multiple BOs, one per Component | `invoice-header` becomes BO `invoice_hdr`; `invoice-line` becomes BO `invoice_line` |
| Single-component Nouns produce one BO without an infix | The Noun slug is the BO name | `party-master` becomes BO `party_master` |
| Multi-component Nouns use an infix | `hdr` for header, `line` for line, `sub` for sub-line | `purchase_order_hdr`, `purchase_order_line` |
| BO display name is the OAGIS Component title | Verbatim from the standard | "Purchase Order Header" |
| BO definition is the OAGIS Component description | Verbatim from the standard; no `inferBO()` heuristics | From `comp.description` |
| BO `source_standard` is `oagis` | Always for OAGIS-derived BOs | |
| BO `standard_ref` is the Noun slug | The full provenance | `purchase-order` |
| BO `industry_code` is `universal` unless domain-specific | OAGIS Nouns are cross-industry by default | |
| BO `function_code` and `subfunction_code` come from the Noun's domain mapping | Remapped to BareCount's master taxonomy | |
| BO `tier_code` is `basic` by default | `derived` only when the Noun description names a derivation source | |
| Header-to-Line relations are `composes` edges in `business_object_relation` | Metadata only; cross-BO joins are handled by metric contracts that bind multiple CCs | |

The one-Component-to-one-BO rule has four reasons. ERP source systems store headers and lines in separate tables (SAP `VBRK` and `VBRP`); one canonical contract maps one source table to one BO. Header-level metrics (Invoice Count) and line-level metrics (Average Line Amount) compute at different grains; separate BOs preserve grain boundaries. OAGIS Nouns can carry multiple Components; flattening them produces oversized objects with mixed grain. Metric contracts that need both header and line data bind to both canonical contracts; no special join logic is needed.

**Governing source.** Business Vocabulary.

## BF Derivation Rules from a Standard

Each OAGIS Component carries scalar and complex fields. The platform's BF derivation admits scalar fields only and assigns BO-scoped names.

The naming rules are explicit per DEC-f66378:

| Rule | Form | Example |
|---|---|---|
| BF name is `{noun}_{infix}_{oagis_field_name}` | BO-scoped, globally unique | `invoice_hdr_total_amount` |
| Single-component Nouns omit the infix | `{noun}_{oagis_field_name}` | `party_master_tax_identifier` |
| Maximum length is 64 characters | DTO regex constraint; abbreviate the noun slug if exceeded | `haz_mat_ship_doc_hdr_...` |
| ISO 11179 decomposition splits BF into object_class plus property | `object_class` is the BO name; `property` is the OAGIS field slug | `object_class=invoice_hdr`, `property=total_amount` |

The BO-scoped naming rule has one reason: OAGIS shares CCT (Core Component Type) field names across Nouns. `total_amount` appears in Invoice and PurchaseOrder. Without disambiguation, a metric contract that binds both BOs cannot tell which `total_amount` it is consuming. BO-scoped names eliminate the ambiguity at the platform vocabulary layer.

The shared dimension exceptions are five and only five (D294 in the v2 SOP shorthand; the list is recorded directly in DEC-f66378's body):

| Shared BF | Reason for the exception |
|---|---|
| `company_code` | Universal grain dimension; metric evaluation requires identical company across COs |
| `currency_code` | ISO 4217 lookup code; same meaning everywhere |
| `language_code` | ISO 639 lookup code; same meaning everywhere |
| `country_code` | ISO 3166 lookup code; same meaning everywhere |
| `unit_of_measure` | UN/CEFACT lookup code; same meaning everywhere |

A BF that the procedure considers shareable must be a universal dimension or lookup code that carries identical semantics across all BOs. A BF that could be measured, summed, or that represents a BO-specific attribute is not shareable; it is BO-scoped.

The metadata rules are explicit:

| Field | Source |
|---|---|
| `definition` | The OAGIS field `description`, verbatim; no `inferBF()` heuristics |
| `data_type` | The OAGIS field `data_type` (string, number, date, etc.) |
| `representation_term` | The OAGIS field `representation_term` (Amount, Code, Identifier, etc.) |
| `semantic_role` | The OAGIS field `semantic_role` (identifier, measure, dimension, temporal, descriptor) |
| `pii_classification` | Default `none`; AI PII classifier runs at certification (gate 7) |
| `source_standard` | `oagis` for OAGIS-derived BFs |
| `standard_ref` | `{noun_slug}/{component_slug}/{field_slug}` |

**Governing source.** Business Vocabulary; The Contract Grammar.

## BF Certification Gate

A BF moves from `draft` to `certified` when all of the following pass at `POST /api/business-fields/{id}/certify`:

| Check | What is validated |
|---|---|
| Name | Non-null, unique, snake_case (`/^[a-z][a-z0-9_]*$/`) |
| Definition | Non-null and not a placeholder; the gate rejects `TBD`, `TODO`, `placeholder` per the platform's no-placeholder discipline |
| Object Class | Non-null |
| Property | Non-null |
| Representation Term | From the controlled vocabulary: Amount, Code, Date, DateTime, Identifier, Indicator, Name, Number, Percent, Quantity, Rate, Text |
| Data Type | From the controlled vocabulary: string, number, integer, date, timestamp, boolean, code |
| PII Classification | Non-null; if the candidate is `none`, the AI PII classifier at `POST /api/ai/suggest/bf-pii-classify` runs; if AI classifies the BF as PII, the BF is updated and certification is held until human confirmation |
| Semantic Dedup | AI maker-checker-gate compares the candidate against existing certified BFs (same `object_class`, similar `property`, same `data_type`); a `red` verdict blocks certification and returns the duplicate's identifier |
| BO-Scoped Naming | When the BF will compose into a BO, its name is BO-scoped (`{bo_prefix}_{oagis_field}`) unless it is one of the five shared dimensions |

A standards-sourced BF (where `source_standard` is non-null) with all nine checks passing is auto-certified. An AI spot-check runs asynchronously per batch; the active sample rate belongs to implementation configuration or the governing SOP. A BareCount-originated BF (no standard provenance) requires explicit human review at certification.

**Governing source.** Business Vocabulary; AI Gates.

## BO Approval Gate

A BO moves from `draft` to `approved` when all of the following pass at `POST /api/business-objects/{id}/approve`:

| Check | What is validated |
|---|---|
| Domain taxonomy | `industry_code`, `function_code`, `subfunction_code` are all populated |
| Minimum composition | At least one `identifier` role, one `dimension` role, one `temporal` role; at least one `is_business_key`; at least four fields total |
| Tier validity | If `tier_code` is `derived`, at least one `derives_from` relation exists in `business_object_relation` |
| Semantic dedup | AI maker-checker-gate compares the BO against existing approved BOs by name and definition; field-overlap dedup is disabled because OAGIS shares CCT field names across Nouns and the overlap creates false positives |
| AI verification | The CR-BO-007 verification (entity coherence, role distribution, naming consistency, duplicate detection, domain alignment, tier validation) returns a non-red verdict |
| All BFs certified | Every BF in the composition has `status: certified` |
| No shared observation BFs | Every BF in the composition is BO-scoped except the five shared dimensions (D294 in the v2 SOP shorthand; the policy is recorded in DEC-f66378's body) |

A non-shared BF that appears in two approved BOs fails the seventh check; the second BO is held in `draft` until the BF is renamed BO-scoped or moved to one BO only.

**Governing source.** Business Vocabulary; AI Gates.

## BF-to-Source-Field Alias Procedure

A certified BF carries a registry of source-system aliases in `contract.business_field_alias`. The alias table answers the question: when an observation contract maps source fields to BFs, which source field name in this system corresponds to this BF?

The alias procedure runs in two levels.

### Level 1: Vocabulary Alias Population

For a given source system (typically SAP), the procedure populates the alias table from three inputs:

| Input | Provenance code | Confidence |
|---|---|---|
| Hardcoded SAP_PATTERNS dictionary (legacy) | `dictionary` | High; migrated from `field-mapping.service.ts` |
| BF-driven enrichment per BO | `dictionary` | High when name plus description plus type all align; medium otherwise |
| Standards cross-reference (where the standard publishes a SAP equivalent) | `seed` | Highest; rare because OAGIS-to-SAP cross-references are sparse |

The procedure is BF-first: for each BF in a target BO, the procedure asks "what is this BF called in this source system?" rather than asking "which BF does this source field map to?" The BF-first orientation matches the demand-pull chain (metric demand drives BF resolution drives source field discovery).

A row in `contract.business_field_alias` carries `(field_id, system_type_code, source_field_name, provenance_code)` and is unique on `(system_type_code, source_field_name)` and on `(field_id, system_type_code)`.

### Level 2: OC-Level Mapping with Backflow

When an observation contract is created (Observation Contract Creation), each confirmed `field_mappings[]` entry triggers a write back to `contract.business_field_alias` with `provenance_code: confirmed`. The backflow (D299 in the v2 SOP shorthand for the alias-table backflow rule) enriches Level 1 for future observation contracts that reference the same BF in the same system. Confirmation is the trust upgrade; aliases that originate from the OC layer carry stronger provenance than `dictionary` aliases.

The alias table is informational. The observation contract's `field_mappings[]` is the contractual binding; the alias table is the AI's hint database for the suggestion engine.

**Governing source.** Business Vocabulary; Observation Contract Creation; Sources and the Catalog.

## Track A: Manual Plus AI

The bc-admin UI at `/business-definitions/register` presents the OAGIS seed by domain. The actor browses Nouns, expands a Noun to view its Components and fields, toggles fields on or off (excluding integration fields like Extension, MetadataReference, SecurityClassification, ActionCode), and clicks Create BFs plus BO. The service auto-creates BFs from the selected fields, runs auto-certification on the standards-sourced batch, auto-creates the BO with the inferred composition, runs AI verification (CR-BO-007), and presents the verdict for human approval.

The actor reviews the AI verdict, fixes any red findings, re-verifies, and approves. After approval, the actor optionally adds `business_object_relation` rows for `composes` (parent-to-child), `relates_to` (peer association), and `derives_from` (derived-to-basic).

**Governing source.** Business Vocabulary.

## Track B: Programmatic

The same endpoints serve agent-driven onboarding. The bulk BF endpoint (`POST /api/business-fields/bulk`) and the bulk certification endpoint (`POST /api/business-fields/bulk-certify`) honor the D268 one-then-many discipline: the first item in the batch passes the full certification gate; if it fails, the entire batch is rejected. Subsequent items are admitted in sequence with per-item dedup checks.

Bulk BO creation (`POST /api/business-objects/bulk`) honors the same discipline. Field references inside the BO composition use `field_name` rather than `field_id`; the service resolves the name to the certified BF identifier via the unique index. A reference to a BF that does not exist or is not certified rejects the BO creation with an explicit error naming the missing BF.

The two tracks call the same service layer (`BusinessDefinitionService`); the gates are enforced at the service, not at the UI. There are no service-layer shortcuts that bypass the gates for programmatic callers.

**Governing source.** Business Vocabulary; AI Gates.

## Quality Gates

The procedure enforces three classes of gate.

| Class | Where enforced | What it checks |
|---|---|---|
| BF certification (CR-QG-001) | `POST /api/business-fields/{id}/certify` | Nine checks listed above |
| BO approval (CR-QG-002) | `POST /api/business-objects/{id}/approve` | Seven checks listed above |
| Alias validation (AL-QG-001) | `PATCH /api/business-fields/{id}/aliases` or the bulk-alias surface | BF exists, system type valid, source field exists, no duplicate at system level, no duplicate at BF level, provenance valid |

A row that lands in any of the three tables (`business_field`, `business_object`, `business_field_alias`) without passing the corresponding gate is in the table but is not the platform's authoritative content; the audit substrate flags it for review.

**Governing source.** Business Vocabulary; AI Gates.

## Boundary with Other Onboarding Chapters

| Chapter | Consumes from this chapter | Does not consume |
|---|---|---|
| Canonical Field Seeding | Nothing directly; canonical fields are metric-vocabulary, not source-vocabulary | The BF taxonomy; CFs are the metric-side counterpart |
| Source and Admission Contract Creation | Nothing directly; SC and AC operate on the source catalog, not on the BF or BO registry | |
| Observation Contract Creation | Certified BFs (for `field_mappings[].business_field_code`); approved BOs (for `business_object_code` selection); the alias table (for AI-assisted mapping suggestions) | The source catalog itself; OC reads it via SC references |
| Canonical Contract Creation | Approved BOs (for `business_object_code` selection); certified BFs (via BO composition); the BO `tier_code` (to set evaluation tier) | The alias table; CC operates on BO composition only |
| Metric Contract Creation | Computed output BFs (registered by MC creation with `source_standard: computed`); cited BFs through CC field selection | The alias table; MC operates on CF names, not BF names |
| Multi-Standard Onboarding | The same procedure with tier-2 and tier-3 source standards (ISO 20022, XBRL, IFRS, BC Standard) | OAGIS-specific Noun-to-BO rules; tier-2 standards have their own structural mapping rules |

**Governing source.** Canonical Field Seeding; Observation Contract Creation; Canonical Contract Creation; Metric Contract Creation; Multi-Standard Onboarding.

## Drift Inventory

| Drift item | Form |
|---|---|
| `inferBF` heuristics deprecated | Earlier versions of the service used `inferBF()` to synthesize BF names from field descriptions when the OAGIS metadata was sparse. The heuristic produced circular definitions and wrong amount-field assignments in historical data. The procedure forbids it; cleanup of historical rows is queued |
| `business_field.source_aliases` JSONB column dropped | The platform moved aliases from a JSONB column on `business_field` to the dedicated `contract.business_field_alias` table (D299 in the v2 SOP shorthand). The drop is complete in the schema; any code or query that still references the JSONB column is failing closed |
| Auto-certification spot-check is asynchronous | The AI spot-check fires after the bulk-certify call returns. A spot-check that flags a previously auto-certified BF results in a follow-up review row, not an automatic decertification |
| Tier-2 standards loading is partial | OAGIS is loaded; ISO 20022 is partially loaded (the readiness-baseline ISO 20022 subset); XBRL US GAAP is loaded as reference for metric naming validation but no BFs are derived from it; IFRS and UN/CEFACT have not been onboarded as BF-and-BO sources. The procedure supports them; the data has not been loaded |
| Domain coverage is incomplete | Domain completion varies by function; the audit substrate reports per-domain BO and BF counts on demand |

**Governing source.** Business Vocabulary; Audit and Activity Logging.

## Governing Decisions

| Decision | Scope in this chapter |
|---|---|
| DEC-f66378 | Establishes BO-scoped BF naming and the five shared dimension exceptions; absorbs the policy that BFs and BOs are sourced from authoritative standards rather than from metric formulas (D290 in the v2 SOP shorthand), the BO-scoping rule itself (D292), and the shared dimension list (D294) |

The `business_field_alias` table (D299) and the standards-sourced provenance discipline (D290) are governance points referenced in the v2 SOP without standalone ADR files; their record lives in the SOP plus this chapter. New ADR files for these may be filed if the policies are restated outside the v2 SOP.

**Governing source.** Decisions: ADR Registry.

## References

- Business Vocabulary
- The Contract Grammar
- Sources and the Catalog
- Source Registration
- AI Gates
- AI Trust and Verification
- Canonical Field Seeding
- Observation Contract Creation
- Canonical Contract Creation
- Metric Contract Creation
- Multi-Standard Onboarding
- Data Model and Schema
- DEC-f66378: BO-scoped BF naming and shared dimension list
- legacy-v2/docs/sops/bf-bo-onboarding-sop.md (predecessor SOP)
- legacy-v2/docs/sops/bf-sf-alias-sop.md (predecessor SOP)
- outline.md §4.6: Onboarding




