---
id: sources-and-the-catalog
order: 8
title: "Sources and the Catalog"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model]
governing_sources:
  - Platform P01 Source Catalog
governing_adrs:
  - DEC-1918d0 (D162 database rules)
  - DEC-69f09e (D148 naming conventions)
errata_referenced: []
v2_sources:
  - system/platform/P01-source-catalog/index.md
  - system/platform/P01-source-catalog/source-provider/
  - system/platform/P01-source-catalog/source-system/
  - system/platform/P01-source-catalog/source-version/
  - system/platform/P01-source-catalog/source-module/
  - system/platform/P01-source-catalog/source-table/
  - system/platform/P01-source-catalog/source-field/
  - system/platform/P01-source-catalog/catalog-verification/
diagrams:
  - DG-catalog-hierarchy
---

# Sources and the Catalog

## Scope

This chapter defines the Source Catalog, the platform-scoped registry of observable external source structure. It names the six catalog hierarchy entities from Source Provider through Source Field, defines the lifecycle that applies to catalog entities, describes system-type classification, and defines catalog verification and source discovery. It distinguishes catalog authority from contract authority so that observable structure, governed selection, and admission behavior are not conflated. It does not define Reader runtime behavior (Admission and Observation), tenant-scoped connections and bindings (Tenancy and Binding), the full relational schema for catalog tables (Data Model and Schema), or the API surface through which catalog entries are read and mutated (API Surface).

## Catalog inventory

The Source Catalog consists of six hierarchy entities and one auxiliary verification record. The six hierarchy entities describe observable source structure. The verification record preserves review activity performed against catalog entities.

| Component | Role | Persistent store |
|---|---|---|
| Source Provider | Organization or vendor that authors one or more source systems | `source.source_provider` |
| Source System | Named software system offered by one provider | `source.source_system` |
| Source Version | Specific version or flavor of a source system | `source.source_version` |
| Source Module | Functional grouping within a source version | `source.source_module` |
| Source Table | Observable data-bearing structure within a source module | `source.source_object` |
| Source Field | Observable data element within a Source Table | `source.source_field` |
| Catalog Verification | Append-only review log for catalog entities | `operations.catalog_verification_log` |

The catalog is platform-scoped. It records what source structure the platform knows about. It does not record which catalog entries a tenant has connected or activated. Tenant-scoped connection and binding records reference catalog entries without duplicating them (Tenancy and Binding).

## Catalog hierarchy

![Source Catalog Hierarchy · six tiers from Source Provider through Source Field, with the auxiliary Catalog Verification log. Each child references exactly one parent.](/docs/assets/diagrams/DG-catalog-hierarchy.svg)

The six hierarchy entities compose by strict parent-child reference.

```
Source Provider
  └── Source System
        └── Source Version
              └── Source Module
                    └── Source Table
                          └── Source Field
```

Each child references exactly one parent. Cross-tier reference skipping is not permitted. A Source Table references its Source Module, not its Source Version directly. A Source Field references its Source Table, not its Source Module.

The catalog and the contract grammar meet at clearly separated points.

| Relationship | Rule |
|---|---|
| Source Contract to catalog | A Source Contract references source structure through `source_system_version_id`, `module_code`, and `table_code` as defined in the Source Contract section of The Contract Grammar. |
| Admission Contract to catalog | An Admission Contract references a Source Contract, not catalog entities directly. |
| Observation Contract to catalog | An Observation Contract selects from the Source Contract body; it does not redefine catalog hierarchy. |
| Reader runtime to catalog | Runtime components may scope execution to catalog entities, but runtime behavior is defined in Admission and Observation rather than here. |

## Catalog entity lifecycle

Catalog entities use a lifecycle distinct from the contract lifecycle defined in the Lifecycle and deprecation policy section of The Contract Grammar. The states in this section apply only to Source Provider, Source System, Source Version, Source Module, Source Table, and Source Field. They do not apply to contract versions, whose `governance.state` is `draft`, `review`, `approved`, `active`, or `superseded`.

| State | Meaning | Transition rule |
|---|---|---|
| `registered` | Known to the platform but not yet approved for governed use | Initial state after discovery, import, or manual registration |
| `approved` | Reviewed and approved for use in governed contract authoring | Promoted from `registered` through governance review |
| `deprecated` | Still preserved, but no longer preferred for new governed use | Promoted from `approved` when a replacement or newer structure exists |
| `archived` | Preserved for historical reference and excluded from default active views | Terminal catalog state |

Catalog lifecycle and contract lifecycle interact, but they are not interchangeable. A contract version may remain `active` while the underlying catalog entity is `deprecated` for future authoring. Historical records remain readable under both models.

## Catalog entities

### Source Provider

**Purpose.** A Source Provider identifies an organization or vendor that authors one or more source systems.

**Parent-child relationship.** Top of the hierarchy. No parent. One Source Provider is the parent of N Source Systems.

**Key attributes.** Provider code, display name, provider classification, optional support metadata, and catalog lifecycle state.

**Status lifecycle.** Catalog entity lifecycle defined in the Catalog entity lifecycle section.

**Disallowed behaviors.**
- A Source System is created without a Source Provider parent reference.
- Two distinct Source Providers share the same provider code.
- Provider identity is silently rewritten after downstream catalog entities have been approved.

**Governing source.** P01 source-provider dossier.

### Source System

**Purpose.** A Source System identifies a named software system offered by one provider.

**Parent-child relationship.** Parent: Source Provider. Children: Source Versions.

**Key attributes.** System code, display name, `system_type_code`, optional function or industry classification, and catalog lifecycle state.

**Status lifecycle.** Catalog entity lifecycle defined in the Catalog entity lifecycle section.

**Disallowed behaviors.**
- A Source System is created without a Source Provider parent reference.
- `system_type_code` is modified after governed downstream use has been established without a governance act.
- The same Source System is registered under two distinct Source Providers without explicit differentiation.

**Governing source.** P01 source-system dossier; the System-type classification section for `system_type_code`.

### Source Version

**Purpose.** A Source Version identifies a specific version or flavor of a Source System.

**Parent-child relationship.** Parent: Source System. Children: Source Modules.

**Key attributes.** Version code, label, release window or flavor metadata, compatibility notes, and catalog lifecycle state.

**Status lifecycle.** Catalog entity lifecycle defined in the Catalog entity lifecycle section.

**Disallowed behaviors.**
- A Source Module is created without a Source Version parent reference.
- A Source Contract references a Source Version that remains in `registered` state.
- The same version code appears under incompatible Source Systems without explicit differentiation.

**Governing source.** P01 source-version dossier.

### Source Module

**Purpose.** A Source Module identifies a functional grouping within a Source Version.

**Parent-child relationship.** Parent: Source Version. Children: Source Tables.

**Key attributes.** Module code, label, optional functional-domain classification, descriptive notes, and catalog lifecycle state.

**Status lifecycle.** Catalog entity lifecycle defined in the Catalog entity lifecycle section.

**Disallowed behaviors.**
- A Source Table is created without a Source Module parent reference.
- Module code is reused across incompatible Source Versions without differentiation.
- A Source Module is archived while approved Source Tables beneath it remain the preferred authoring target for active governed use.

**Governing source.** P01 source-module dossier.

### Source Table

**Purpose.** A Source Table identifies an observable data-bearing structure within a Source Module. The structure may correspond to a database table, view, extractable record set, or API endpoint represented in a table-like form. The relational table is named `source.source_object`; documentation, UI, and API surfaces use "Source Table."

**Parent-child relationship.** Parent: Source Module. Children: Source Fields.

**Key attributes.** Table code, label, optional identity notes such as observed primary key or business-key hints, descriptive metadata, and catalog lifecycle state.

**Status lifecycle.** Catalog entity lifecycle defined in the Catalog entity lifecycle section.

**Disallowed behaviors.**
- A Source Table is created without a Source Module parent reference.
- A Source Contract references a Source Table that remains in `registered` state.
- Identity metadata recorded for a Source Table is silently rewritten after governed authoring depends on it.

**Governing source.** P01 source-table dossier.

### Source Field

**Purpose.** A Source Field identifies an observable data element within a Source Table.

**Parent-child relationship.** Parent: Source Table. Terminal leaf of the hierarchy.

**Key attributes.** Field code, label, recorded type, nullability, optional key participation, optional standards metadata, `z_extension` flag where applicable, and catalog lifecycle state.

**Status lifecycle.** Catalog entity lifecycle defined in the Catalog entity lifecycle section.

**Disallowed behaviors.**
- A Source Field is created without a Source Table parent reference.
- A Source Contract includes a field whose catalog entry remains in `registered` state.
- A standard field is reclassified as a Z-extension, or a Z-extension as standard, without governance.

**Governing source.** P01 source-field dossier.

## System-type classification

Each Source System carries a `system_type_code` that classifies the system by functional category, for example `erp`, `crm`, `hrms`, `itsm`, `mes`, `wms`, `data_warehouse`, or `event_stream`.

| Rule | Effect |
|---|---|
| Classification is on Source System, not Source Provider | One provider may offer multiple system types. The classification belongs to the system being cataloged. |
| Classification is governed metadata | Changes require governance once downstream catalog authoring or published contracts depend on the system. |
| Classification informs authoring and review context | Catalog discovery, template selection, and reviewer defaults may use `system_type_code`. Runtime admission rejection remains governed by the Admission Contract. |

DEC-1918d0 (D162) governs this classification as a platform-scope attribute on `source_system`, not on `source_provider`.

## Catalog verification

Catalog verification is AI-assisted review of catalog entities. It evaluates the quality and plausibility of catalog entries without changing catalog status directly. Verification applies to Source Module, Source Table, and Source Field entries and records results in `operations.catalog_verification_log`.

| Property | Value |
|---|---|
| Scope | Source Module, Source Table, Source Field |
| Trigger | Manual review or scheduled verification run |
| Output | Verification log entry with verdict, confidence, rationale, and model identifier |
| Effect on catalog state | No direct state transition; review results inform governance promotion from `registered` to `approved` |
| Retention | Append-only; verification records are preserved as operational history |

Verification does not replace governance review. A positive verification result is evidence for review. Promotion to `approved` remains a separate governance act.

**Disallowed behaviors.**
- A catalog entity is promoted solely because a verification model returned a favorable verdict.
- A verification log entry is modified after emission.
- Verification coverage is assumed at a tier where review rules have not been defined.

## Source discovery

Source discovery registers new catalog entries from external inspection or curated registration. Discovery populates catalog entities into `registered` state. It does not admit observed business state and it does not produce Source Objects.

| Discovery pattern | Input | Typical effect |
|---|---|---|
| Curated catalog import | Pre-reviewed structural dataset for a known Source System or Source Version | Bulk registration of modules, tables, and fields |
| Schema scrape | Connector or inspection output from a live Source Version | Registration of tables and fields discovered from the inspected surface |
| Manual registration | Operator-authored entry through governed admin workflows | Registration at any catalog tier |

Discovery and admission are distinct acts. Discovery records what structure is known about a source. Admission is the evaluation boundary at which observed external state becomes a Source Object (the Admission boundary section of The Evaluation Boundaries).

## Catalog and contracts

The catalog records observable structure. Contracts govern what subset of that structure is used, how it is validated, and what authoritative state is produced at a boundary. These responsibilities are adjacent but distinct.

| Concern | Catalog authority | Contract authority |
|---|---|---|
| What source structure is known to exist | Records Provider, System, Version, Module, Table, and Field hierarchy | Not asserted directly |
| What source structure is eligible for governed authoring | Catalog lifecycle and review determine whether an entity is approved for use | Contracts may only reference approved structure |
| What structure is admitted at runtime | Not asserted directly | Source Contract, Admission Contract, and Observation Contract govern structural declaration, validation, and field selection |
| How field types and key semantics are used operationally | Records observed or registered structure metadata | Declares governed structural shape and admission rules |
| Version and status handling | Uses catalog entity lifecycle | Uses contract `governance.state` lifecycle from The Contract Grammar |

A Source Contract references catalog structure through `source_system_version_id`, `module_code`, and `table_code` as defined in the Source Contract section of The Contract Grammar. It does not restate the full catalog hierarchy. The Admission Contract references the Source Contract. The Observation Contract governs field selection from the Source Contract body. Runtime components consume these artifacts at the admission boundary described in Admission and Observation.

An observable field present in the catalog but absent from the active Source Contract and Observation Contract set is known structure, not admissible structure.

## Chapter boundaries

This chapter has defined the Source Catalog's six hierarchy entities, the catalog entity lifecycle, system-type classification, catalog verification, source discovery, and the distinction between catalog authority and contract authority. It has deferred:

- Reader runtime behavior and source-scoped execution (Admission and Observation).
- Tenant-scoped connection and binding records that reference catalog entries (Tenancy and Binding).
- Relational schema details, indexes, and constraints for catalog persistence (Data Model and Schema).
- API endpoints and mutation workflows for catalog administration (API Surface).

Subsequent chapters describe how catalog entries are consumed at runtime under the authority model established in Foundation.

## References

- Platform P01 Source Catalog: authoritative dossier set for the six hierarchy entities and verification procedure
- DEC-1918d0: D162 database rules (Decisions)
- DEC-69f09e: D148 naming conventions (Decisions)
- The Object Model: The Object Model
- the Source Contract section of The Contract Grammar: Source Contract
- the Admission Contract section of The Contract Grammar: Admission Contract
- the Observation Contract section of The Contract Grammar: Observation Contract
- the Admission boundary section of The Evaluation Boundaries: Admission boundary
- The Authority Model: The Authority Model
- Admission and Observation: Admission and Observation
- Tenancy and Binding: Tenancy and Binding
- Data Model and Schema
- API Surface
- Decisions: ADR Registry
