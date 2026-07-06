---
id: tenancy-and-binding
order: 14
title: "Tenancy and Binding"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, sources-and-the-catalog, connectors-and-readers, admission-and-observation, canonical-evaluation, metric-evaluation, action-evaluation, evidence-and-lineage]
governing_sources:
  - The Contract Grammar, Three-level governance section
  - Sources and the Catalog
  - Connectors and Readers
  - Action Evaluation, Assignee resolution mechanism deferred to Ch 13 section
governing_adrs:
  - DEC-771baf (Tenant database architecture; platform-tenant one-way dependency)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-2c79c8 (Per-tenant SQL isolation)
  - DEC-bd5492 (Sentinel-based privacy erasure; referenced in deferrals)
v2_sources:
  - system/tenant/T01-boundary-data/index.md
  - system/tenant/T02-record-data/index.md
  - system/tenant/T03-evidence-lineage/index.md
  - system/tenant/T04-connections/index.md
  - system/tenant/T05-execution-runs/index.md
  - system/tenant/T06-operational/index.md
---

# Tenancy and Binding

## Scope

This chapter defines tenancy as the platform's runtime ownership and isolation model and Contract Binding as the bounded mechanism through which tenants customize platform-governed contracts. It defines the tenant-platform ownership boundary established by DEC-771baf, the three-level governance model recapped from the Three-level governance section of The Contract Grammar, the Contract Binding artifact, the Connection artifact's tenant-owned dimension, the assignee-resolution mechanism deferred by Action Evaluation, the proof-retention-policy artifact deferred by Evidence and Lineage, and the tenant-scoped storage that holds Run records, proof, Bindings, and Connections.

This chapter does not redefine the contract grammar, the Source Catalog, the runtime components that consume tenant-scoped artifacts at the four boundaries, the proof chain, the relational schema for tenant storage, or the API surface for tenant administration. Data Model and Schema owns exact schema and table names. API Surface owns tenant administration endpoints. Tenant Extensions and Overrides owns per-family extension surfaces that are broader than Contract Binding.

This chapter follows the current authoritative Foundation reading in which contracts are platform-governed and tenant customization occurs only through the Tenant Override layer described in The Contract Grammar. The specific overridable surfaces of each contract family are governed by the family master schemas in the Contract Schemas reference and by the relevant platform dossiers. This chapter describes Binding as the bounded mechanism, not as a per-field override catalog.

**Governing source.** DEC-771baf; The Contract Grammar; Sources and the Catalog; Connectors and Readers; Action Evaluation; Evidence and Lineage.

## Tenancy Inventory

Tenancy uses one platform-scoped registration record and four tenant-scoped artifact classes.

| Artifact | Role | Scope | Persistent store |
|---|---|---|---|
| Tenant identity | Platform-scoped registration of a tenant and the tenant database it owns | Platform | Platform-scoped tenant registry; exact location governed by Data Model and Schema |
| Contract Binding | Tenant-scoped record that pairs a platform contract version with bounded tenant variation | Tenant | Tenant binding store defined by current tenant-schema ADRs and Data Model and Schema |
| Connection | Tenant-scoped record that pairs a platform Connector and a Source System catalog entry with tenant-specific access configuration | Tenant | Tenant connection store defined by current tenant-schema ADRs and Data Model and Schema |
| Tenant execution and proof records | Per-invocation Run records and Evidence and Lineage emitted by boundary acts | Tenant | Tenant execution and proof stores defined by current tenant-schema ADRs and Data Model and Schema |
| Tenant operational state | Tenant self-description and operational metadata referenced by tenant-scoped behavior | Tenant | Tenant operational store defined by current tenant-schema ADRs and Data Model and Schema |

Tenant identity is the only artifact recorded in the platform database. Every other tenant artifact is held in the tenant database governed by DEC-771baf.

**Governing source.** DEC-771baf; DEC-f02230; DEC-2c79c8; Data Model and Schema.

## Tenant Database Scope and Ownership Boundary

DEC-771baf establishes the tenancy ownership boundary. The boundary is one-directional and exclusive.

| Ownership concern | Rule |
|---|---|
| Contracts | Platform owns all contracts. The platform contract registry is the sole authoritative source of contract identity, version, and body. No tenant artifact substitutes for a contract. |
| Catalog entries | Platform owns the Source Catalog. Tenant artifacts reference catalog entries; they do not replicate or modify them. |
| Tenant data | The tenant owns all data produced by, recorded for, or persisted in its own tenant database, including Run records, Evidence and Lineage, Source Objects, Canonical Objects, Metric Snapshots, Action Objects, Connections, and Contract Bindings. |
| Cross-tenant reads | The platform does not contact a tenant database for tenant-state reads at runtime. A tenant database is accessed only by its tenant's own runtime activity and by tenant-authorized administrative paths. |
| Direction of dependency | Tenant runtime resolves platform-governed contracts, Connectors, and catalog entries at admission and evaluation time and depends on those platform definitions for every governed act. Tenant-owned data is not written back into platform-owned outputs, and platform runtime does not read tenant state to produce platform-level outputs. |

Per DEC-771baf, the platform never reads tenant state to produce platform-level outputs. Per DEC-f02230 and its active tenant-schema amendments, the tenant database is organized into schemas that govern the storage of tenant artifacts. Exact schema names and table identifiers are described in Data Model and Schema.

**Governing source.** DEC-771baf; DEC-f02230; DEC-2c79c8; Sources and the Catalog; Data Model and Schema.

## Three-Level Governance Recap

The Three-level governance section of The Contract Grammar declares the governance model that controls how contracts may change. This chapter operationalizes only the third level.

| Level | Artifact | Governs | Scope |
|---|---|---|---|
| Master Shape | Meta-schema per family | Shape of the family: keys, types, governance tags, and validation rules | Platform-locked. Changes require an ADR. |
| Platform Instance | Contract version | A specific governed contract in the family | Platform-locked once `active`. Changes produce new versions. |
| Tenant Override | Contract Binding | Tenant-scoped variation against a specific contract version | Tenant-scoped. Cannot remove platform-declared fields or modify platform-declared rules. |

The Tenant Override layer is the only level a tenant participates in. Master Shape changes and Platform Instance changes are platform acts recorded under their own governance. Contract Binding is the tenant act through which a tenant adopts a specific contract version with permitted variation.

**Governing source.** The Contract Grammar; The Authority Model.

## Contract Binding

The Contract Binding is the tenant-scoped artifact that pairs one tenant with one platform contract version under bounded variation.

**Purpose.** A Contract Binding records that a specific tenant has adopted a specific contract version and carries the tenant's bounded variation against that version.

**Behavior.** A Binding identifies the tenant, identifies the platform contract version it binds to, and records any tenant-permitted variation in dedicated bounded fields of the Binding record. Runtime components consume the Binding alongside the contract version when applying the contract to tenant data. The contract version remains the authoritative source of platform-declared shape and rules.

**Bounded variation.** Per the Three-level governance section of The Contract Grammar, a Binding cannot remove platform-declared fields and cannot modify platform-declared rules. The set of permitted variations for each contract family is governed by the family's master schema and is recorded against the Binding in dedicated fields. Variation outside that set is rejected at Binding creation.

**Cardinality.** One tenant may hold N Contract Bindings, one per platform contract version the tenant has adopted. One contract version may be bound by N tenants independently. Each Binding references exactly one contract version.

**Versioning.** A new contract version requires a new Binding for any tenant that adopts it. Previous Bindings continue to apply to previously emitted authoritative state under the prior version. Bindings are not retroactively rebound to a newer contract version.

**Constraints.**

- A Binding does not extend the contract's shape beyond what the family master schema permits.
- A Binding does not introduce new validation, resolution, formula, or trigger logic. It parameterizes existing platform-declared logic within the bounded surface.
- A Binding is not modified to retroactively alter authoritative state previously produced under it.

**Failure modes.** Binding creation that asserts variation outside the permitted surface is rejected. A Binding whose referenced contract version is superseded does not silently follow the supersession. The tenant continues to operate against the originally bound version until a new Binding is created.

**Governing source.** The Contract Grammar; The Object Model; Contract Schemas reference.

## Connection

Connection is the tenant-scoped adapter artifact defined in Connectors and Readers. This chapter describes only the tenancy dimension: tenant ownership, tenant cardinality, and tenant-administered lifecycle. Connectors and Readers governs the artifact's purpose, behavior, Reader Flavor compatibility rule, constraints, and failure modes.

**Tenant ownership.** A Connection's credentials and access configuration are tenant-owned per DEC-771baf. Platform-side adapter artifacts do not carry tenant credentials. Connection is the only adapter artifact that does. Credential material is held in the platform's secret-management surface and referenced from the Connection record; the Connection record itself does not preserve credential values.

**Tenant cardinality.** One tenant may hold N Connections, one per Source System version the tenant has connected. A tenant may hold multiple Connections to the same Source System when the tenant has connected to multiple Source Versions of that system. One platform Connector may be referenced by N Connections across N tenants and N Source Versions independently.

**Tenant-administered lifecycle.** Connection lifecycle covers creation, configuration update, credential rotation, and retirement. Each lifecycle event is recorded as a tenant-side change event capturing what changed and when. Credential rotation overwrites authentication material; the prior credential is not retained, only the change event itself. Connection retirement is terminal. Admission acts that reference a retired Connection terminate as Connector-resolution failures per Connectors and Readers.

**Governing source.** Connectors and Readers; Sources and the Catalog; DEC-771baf; current tenant-schema ADRs.

## Assignee Resolution From the Assignee Pool

Per the Action-creation act section of Action Evaluation, the Action Evaluator records the assignee pool resolved against the active Intervention Contract version and defers the mechanism that picks a specific owner from that pool to this chapter. The mechanism is a property of the tenant's Contract Binding for the relevant Intervention Contract.

**Purpose.** The Contract Binding for an Intervention Contract carries a tenant-defined mapping from each role in the Contract's `assignee_pool` to one or more candidate owners under that role. At action-creation time, the Action Evaluator consults the Binding's mapping and records a specific owner on the emitted Action Object.

**Bounded surface.** The mapping is bounded by the active Intervention Contract version's assignee pool. A Binding may map only roles the Contract declares, and the candidate owners listed under each role are tenant-defined. The Binding cannot introduce roles that the Contract does not declare and cannot assign an owner outside the candidates declared in the Binding for the relevant role.

**Recorded outcome.** The specific owner identified at action-creation time is recorded on the emitted Action Object as part of the creation-time payload. The mapping from role to candidate owners is recorded on the Binding. The resolution from candidates to a specific owner is recorded as part of the action-creation Evidence.

**Constraints.**

- A Binding does not modify the Intervention Contract's `assignee_pool` declaration. The pool's role categories remain platform-governed; only the candidate owners under each role are tenant-defined.
- A Binding does not change the assigned owner of a previously emitted Action Object. The owner is set at action-creation time.
- A Binding's mapping update applies only to subsequent action-creation acts, not to Action Objects already emitted under prior mappings.

**Governing source.** The Contract Grammar; Action Evaluation; Evidence and Lineage; Contract Schemas reference.

## Proof Retention Policy

Per the Retention and Invariant VI section of Evidence and Lineage, retention of Evidence and Lineage is governed at the storage layer. Retention configuration is deferred to this chapter. Proof retention is a tenant-scoped operational policy artifact, not a Contract Binding.

**Purpose.** A tenant declares a proof retention policy that governs how long Evidence and Lineage records remain available on the authoritative evidence chain before retention treatment applies. The policy is a tenant-scoped record held in the tenant's operational store.

**Behavior.** The retention policy declares retention duration per proof artifact class and per source boundary act class where the tenant elects differentiated retention. The storage layer applies the declared retention policy to tenant-scoped proof records held in the tenant database. Ordinary retention treatment preserves proof or archives it to a governed storage location with its reference status recorded. Ordinary retention does not remove, rewrite, or mutate Evidence or Lineage.

**Relationship to Invariant VI.** Per the Retention and Invariant VI section of Evidence and Lineage, audit readability depends on preserved proof being available through the authoritative evidence chain or through a governed archive reference that the chain records. A retention policy may move proof to a governed archive while preserving its reference. If proof becomes unavailable to audit reads, the platform no longer treats the act as authoritatively proved for audit. The retention policy does not change the act's emission status; it changes the audit-readability status of preserved proof over time.

**Privacy-erasure exception.** Privacy erasure is not ordinary retention. If a privacy-erasure obligation applies, DEC-bd5492 governs the sentinel-based erasure path. That path records the governed erasure event and preserves the fact of the erasure decision without representing erased material as still audit-readable proof.

**Constraints.**

- The retention policy does not modify Evidence or Lineage records in place. Both proof object types are immutable.
- The retention policy does not authorize silent removal of proof records. Any non-readability outcome requires a governed archive reference or a governed erasure event.
- The retention policy does not extend the audit window beyond what preserved proof or governed archive references support.
- The retention policy is tenant-scoped. The platform may impose a minimum retention floor governed by Compliance treatment.

**Governing source.** Evidence and Lineage; The Object Model; DEC-bd5492; current tenant-schema ADRs.

## Tenant-Scoped Storage

The tenant database holds the artifacts that earlier chapters introduced as tenant-scoped. The mapping below is conceptual. Exact schema and table names live in Data Model and Schema and current tenant-schema ADRs.

| Artifact class | Source chapter | Tenant ownership |
|---|---|---|
| Source Object, Canonical Object, Metric Snapshot, Action Object | Admission and Observation through Action Evaluation | Per-tenant authoritative state produced at the four evaluation boundaries |
| Evidence Object and Lineage Object | Evidence and Lineage | Per-tenant proof chain emitted at proof-emitting acts |
| Admission Run, Canonical Evaluation Run, Metric Evaluation Run, Action Evaluation Run | Admission and Observation through Action Evaluation | Per-invocation tenant execution records |
| Contract Binding | Contract Binding section of this chapter | Per-tenant bound contract versions with bounded variation, including the assignee-pool mapping for Intervention Contract bindings |
| Connection | Connectors and Readers; Connection section of this chapter | Per-tenant access records to Source System versions |
| Proof retention policy | Proof Retention Policy section of this chapter | Per-tenant retention configuration applied at the storage layer to Evidence and Lineage |
| Tenant operational state | This chapter | Per-tenant self-description and operational metadata |

Storage isolation is governed by DEC-2c79c8 and DEC-f02230. The platform does not read tenant artifacts to produce platform-level outputs. Tenant-administered acts operate against the tenant's own database under tenant authorization, not under platform-direct access.

**Governing source.** DEC-771baf; DEC-f02230; DEC-2c79c8; Admission and Observation; Canonical Evaluation; Metric Evaluation; Action Evaluation; Evidence and Lineage.

## References

- The Object Model: Authoritative progression objects
- The Contract Grammar: Three-level governance
- The Authority Model: The Authority Model
- Sources and the Catalog: Sources and the Catalog
- Connectors and Readers: Connectors and Readers
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Action Evaluation: Action Evaluation
- Evidence and Lineage: Evidence and Lineage
- Data Model and Schema
- API Surface
- DevHub and Governance
- ISO 27001 Conformance
- SOC 2 Conformance
- DEC-771baf: Tenant database architecture and one-way dependency
- DEC-f02230: Tenant DB schema organization
- DEC-2c79c8: Per-tenant SQL isolation
- DEC-bd5492: Sentinel-based privacy erasure
- Contract Schemas reference
- Decisions: ADR Registry
