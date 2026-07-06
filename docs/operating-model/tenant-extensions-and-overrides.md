---
id: tenant-extensions-and-overrides
order: 14.5
title: "Tenant Extensions and Overrides"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, sources-and-the-catalog, connectors-and-readers, admission-and-observation, canonical-evaluation, metric-evaluation, action-evaluation, tenancy-and-binding]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Contract Grammar, Three-level governance section
  - Sources and the Catalog
  - Connectors and Readers
  - Tenancy and Binding, Contract Binding section
governing_adrs:
  - DEC-771baf (Tenant database architecture; ownership boundary)
  - DEC-2c79c8 (Per-tenant SQL isolation)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-97bb94 (N:1 SO to CO multi-source canonical evaluation)
errata_referenced:
  - FND-ERR-004
v2_sources: []
---

# Tenant Extensions and Overrides

## Scope

This chapter defines the per-family extension surface through which a tenant introduces bounded variation against platform-governed contracts and against the platform Source Catalog. It defines the bounded variation principle that all tenant extensions obey, the inventory of extension surfaces, the tenant-scoped Source Catalog extension that records custom source tables and custom source fields observed in a tenant's connected systems, the Source Contract tenant-field declaration surface, the Admission Contract rule extension surface, the Observation Contract custom-field mapping surface, the Metric Contract threshold parameter surface, the Intervention Contract action parameter surface, the common constraints that apply across every extension surface, and the failure modes that arise when an extension claim falls outside the permitted surface.

This chapter does not redefine the contract grammar, the three-level governance model, the Contract Binding artifact, the Source Catalog, the runtime acts at the four boundaries, the relational schema that holds extension records, or the API surface for extension administration. It also does not define the tenant Connection artifact; Connectors and Readers defines Connection, and this chapter references Connection only where extension claims must resolve to a tenant-connected Source System version.

This chapter operates one level below Tenancy and Binding. Tenancy and Binding defines Contract Binding as the bounded mechanism. This chapter defines what specifically may vary, per contract family and catalog surface, on the bounded surface that the relevant master schema permits.

**Governing source.** Foundation; The Contract Grammar; Tenancy and Binding; Sources and the Catalog; Connectors and Readers.

## Bounded Variation Principle

Tenant extensions are bounded. Six extension surfaces exist (the per-surface inventory follows in the next section); each carries the same six bounding rules below per its governing schema.

| Property | Rule |
|---|---|
| Surface declared by governing schema | Each contract family's master schema or catalog-extension schema declares the set of fields that the Tenant Override layer may parameterize. The set is closed; variation outside it is not admissible. |
| Platform-declared content is preserved | An extension cannot remove a platform-declared field, rule, mapping, or threshold. It can only add to or parameterize the platform-declared content where the governing schema permits. |
| Validation logic is platform-declared | Tenant extensions parameterize platform-declared logic. They do not introduce new validation, resolution, formula, or trigger logic. |
| Extensions are versioned | A contract-family extension is recorded against a specific platform contract version. A Source Catalog extension is recorded against a specific Source System version and the tenant Source Contract version that declares the extension field. |
| Extensions are tenant-scoped | Extensions are recorded in the tenant database. The platform contract registry and platform Source Catalog are not modified by a tenant act. |
| Extensions are bounded by the gate set | Extensions pass through the same Quality Gates as platform authoring acts where the governing schema declares gate applicability. Extensions do not bypass quality treatment. |

Extensions widen what the tenant can observe or parameterize. They do not widen what the platform-declared contract permits. The platform-declared shape of authoritative state remains intact.

**Governing source.** The Contract Grammar; Tenancy and Binding; Quality Gates and Chain Integrity.

## Extension Surface Inventory

Six extension surfaces exist. One active contract family has no tenant extension surface.

| Surface | Family or catalog area | Tenant artifact | What the surface admits |
|---|---|---|---|
| Source Catalog extension | Source Catalog | Tenant-scoped catalog extension record | Custom source tables and custom source fields observed in a tenant's connected systems but not present in the platform Source Catalog entry for that Source System version |
| Source Contract tenant-field declaration | Source Contract | Contract Binding for the Source Contract version, paired with the Source Catalog extension | Structural declaration that a tenant-scoped source field exists, marked with the Source Contract `z_extension` flag and tied to the tenant Source Catalog extension entry |
| Admission rule extension | Admission Contract | Contract Binding for the Admission Contract version | Additional structural, field-level, or record-level rules permitted by the Admission Contract version's declared extension set |
| Observation custom-field mapping | Observation Contract | Contract Binding for the Observation Contract version | Mappings from Business Field declarations to tenant-extension source fields registered in the Source Catalog extension and declared on the bound Source Contract surface |
| Metric threshold parameter | Metric Contract | Contract Binding for the Metric Contract version | Tenant-specific threshold values for the parameterized thresholds the Metric Contract version declares |
| Intervention action parameter | Intervention Contract | Contract Binding for the Intervention Contract version | Tenant-specific action parameters declared as extensible by the Intervention Contract version, including the assignee mapping defined in Tenancy and Binding |

| Family | Tenant extension surface | Reason |
|---|---|---|
| Canonical Contract | None | Canonical meaning is platform-governed. Per Foundation, canonical resolution is one platform-declared act and is not tenant-parameterizable. Canonical Mapping versions are platform-governed alongside Canonical Contract versions. |

The set of admissible extension claims for each surface is declared in the relevant family's master schema, the tenant catalog-extension schema, and the Contract Schemas reference. This chapter describes the surface; the governing schema declares the exact claims.

**Governing source.** The Contract Grammar; Sources and the Catalog; Contract Schemas reference.

## Source Catalog Extensions

The platform Source Catalog records the observable source structure of each Source System version as governed by Sources and the Catalog. A tenant's connected instance of a Source System may carry tenant-added source tables or source fields that the platform Source Catalog entry does not record. The Source Catalog extension is the tenant-scoped artifact that records those additions.

**Purpose.** The Source Catalog extension records tenant-instance source structure that supplements the platform Source Catalog entry for the relevant Source System version. The extension exists so that Source Contract tenant-field declarations and Observation Contract custom-field mappings have governed source-side references.

**Scope.** A Source Catalog extension is recorded per tenant per Source System version. It admits two artifact types: extension tables and extension fields. Extension tables are tables present in the tenant instance but not in the platform Source Catalog entry. Extension fields are fields present on platform-cataloged tables that are not in the platform Source Catalog entry, or fields on extension tables.

**Behavior.** The extension entry references the platform Source Catalog entry it extends. Each extension table or extension field carries the same descriptive attributes the platform Source Catalog records for its own entries so that subsequent Source Contract and Observation Contract Bindings have a stable, governed reference. The runtime treats extension entries as source-field references only after the tenant Source Contract Binding declares the field as a tenant-scoped extension through the Source Contract `z_extension` surface.

**Constraints.**

- An extension does not modify a platform Source Catalog entry. It adds tenant-scoped entries that reference the platform entry.
- An extension does not introduce a new Source System or Source System version. It extends the structure observable within an existing platform-cataloged Source System version.
- An extension's entries are not authoritative for any other tenant. Each tenant maintains its own extension under the same Source System version.
- An extension does not relax the platform Source Catalog's verification rules for platform-cataloged entries. Platform entries remain governed by Sources and the Catalog.
- A Source Catalog extension entry is not sufficient by itself for admission validation. A bound Source Contract version must also declare the field as a tenant-scoped extension where the Source Contract master schema permits it.

**Failure modes.** An extension that asserts a Source System or Source System version not present in the platform Source Catalog is rejected. An extension that asserts a table or field already declared in the platform Source Catalog entry is rejected as a duplicate, not silently merged. An Observation Contract custom-field mapping that references an extension entry the relevant tenant has not registered is rejected at Binding creation. A mapping that references a Source Catalog extension entry not declared through the bound Source Contract tenant-field surface is rejected.

**Interactions.** The Source Catalog extension is referenced by the Source Contract tenant-field declaration surface and by the Observation Contract custom-field mapping surface defined later in this chapter. Connections defined in Connectors and Readers do not change behavior because of an extension; the extension is observed metadata, not a runtime adapter parameter.

**Governing source.** Sources and the Catalog; The Contract Grammar; DEC-771baf; current tenant-schema ADRs.

## Source Contract Tenant-Field Declarations

The Source Contract governs structural declaration of admitted source state. The Contract Grammar defines each Source Contract field entry with a `z_extension` flag. This chapter treats that flag as the governed bridge between tenant Source Catalog extensions and admission structural validation.

**Purpose.** A Source Contract tenant-field declaration marks a tenant-scoped source field as structurally admissible for the tenant, without modifying the platform Source Contract version.

**Scope.** Source Contract tenant-field declarations are carried on the Contract Binding for the relevant Source Contract version. The declaration references a tenant Source Catalog extension entry and records that the field is admitted under the Source Contract's `z_extension` surface. The declaration is available only where the Source Contract master schema permits tenant extension fields.

**Behavior.** At admission, structural validation uses the platform Source Contract version plus the tenant Source Contract Binding's declared extension fields. Platform-declared fields retain their platform-governed status. Tenant-declared fields are admitted only for the tenant and only for the Source System version named by the Source Catalog extension.

**Constraints.**

- A tenant-field declaration does not modify the platform Source Contract body.
- A tenant-field declaration cannot replace or rename a platform-declared field.
- A tenant-field declaration must reference a registered Source Catalog extension entry for the same tenant and Source System version.
- A tenant-field declaration does not authorize canonical meaning or Business Field mapping by itself. Observation Contract custom-field mapping declares that later source-to-business reference.

**Failure modes.** A tenant-field declaration that references no Source Catalog extension entry is rejected. A declaration that duplicates a platform-declared Source Contract field is rejected. A declaration against a Source Contract version whose master schema does not permit tenant extension fields is rejected. A declaration against a superseded Source Contract version is rejected for new Binding creation unless a governed historical-use exception exists.

**Interactions.** Observation Contract custom-field mappings may reference tenant-declared Source Contract extension fields. Admission rule extensions may reference those fields only after both the Source Catalog extension and Source Contract tenant-field declaration exist.

**Governing source.** The Contract Grammar; Sources and the Catalog; Tenancy and Binding; Contract Schemas reference.

## Admission Contract Rule Extensions

The Admission Contract governs runtime validation at the admission boundary per Admission and Observation. Each Admission Contract version's master schema declares whether and where tenant rule extensions are admissible.

**Purpose.** A tenant adds rules to the platform-declared Admission Contract within the contract version's declared extension set, so that the tenant's admission boundary applies tenant-specific validation alongside the platform-declared rules.

**Scope.** Rule extensions are carried on the Contract Binding for the relevant Admission Contract version. The set of admissible rule classes and the parameter surface for each class are governed by the Admission Contract version's master schema. The rule extension does not introduce rule classes that the master schema does not declare.

**Behavior.** At admission, the Reader applies platform-declared Admission Contract rules first, then the tenant rule extensions declared on the active Binding, in the order the contract version's master schema specifies. Extension rules participate in the same per-record outcome accounting and the same batch threshold evaluation as platform-declared rules. The Admission Run records platform-declared and extension rule outcomes uniformly.

**Constraints.**

- A rule extension does not relax, downgrade, or remove a platform-declared rule. It adds rules within the declared extension set.
- A rule extension does not change the admission sequence or the batch threshold evaluation order defined by Admission and Observation.
- A rule extension does not introduce validation that bypasses the per-record outcome categories declared by the Admission Contract grammar.
- A rule extension's outcomes are recorded in the same Evidence emitted by the admission act. A separate proof artifact for extension rules is not introduced.

**Failure modes.** A rule extension that asserts a rule outside the master schema's declared extension set is rejected at Binding creation. A rule extension that names a field absent from the Observation Contract's declared field set, absent from the platform Source Catalog, or absent from the tenant Source Catalog extension and Source Contract tenant-field declaration is rejected. A rule extension that downgrades or removes a platform-declared rule is rejected.

**Interactions.** Admission rule extensions interact with Observation custom-field mappings. A rule extension may reference a custom-mapped field only when the relevant Observation Contract Binding maps that field for the same tenant.

**Governing source.** Admission and Observation; The Contract Grammar; Contract Schemas reference.

## Observation Contract Custom-Field Mappings

The Observation Contract governs how validated source data is selected and represented as Source Object content per Admission and Observation. Each Observation Contract version's master schema declares whether tenant custom-field mappings are admissible and the bounded surface they may occupy.

**Purpose.** A tenant maps Business Field declarations to source fields recorded in the platform Source Catalog or in the tenant's Source Catalog extension, where the Observation Contract version declares the field as tenant-mappable. Custom-field mappings make tenant-instance source structure visible to admission as governed Business Field values without modifying the platform-declared Observation Contract body.

**Scope.** Custom-field mappings are carried on the Contract Binding for the relevant Observation Contract version. The mapping surface is bounded. The master schema declares which Business Fields admit tenant mappings, and the mapping must reference a source field present in either the platform Source Catalog entry or both the tenant Source Catalog extension and bound Source Contract tenant-field declaration for the relevant Source System version.

**Behavior.** At admission, after platform-declared rule application and observation-age enforcement, the Reader applies the platform-declared field map and the tenant custom-field mappings declared on the active Observation Contract Binding. The emitted Source Object carries Business Field values populated from both sources of mapping. The Source Object's shape conforms to the platform-governed observation schema; tenant mappings populate fields the schema declares, not fields the schema does not declare.

**Constraints.**

- A custom-field mapping does not introduce Business Fields that the Observation Contract does not declare. The Business Field set is platform-governed.
- A custom-field mapping does not override a platform-declared mapping. Where the master schema permits both a platform default and a tenant override for the same Business Field, the master schema declares precedence; the tenant cannot redefine that precedence.
- A custom-field mapping does not perform business composition across Source Objects. Multi-source composition is the canonical evaluation boundary's responsibility per DEC-97bb94 and FND-ERR-004.
- A custom-field mapping's referenced source field must be observable through a Connection that the tenant has registered for the same Source System version.
- A custom-field mapping to a tenant extension field requires both a Source Catalog extension entry and a Source Contract tenant-field declaration.

**Failure modes.** A custom-field mapping that names a Business Field outside the Observation Contract's declared mappable set is rejected at Binding creation. A custom-field mapping that references a source field absent from both the platform Source Catalog entry and the tenant Source Catalog extension is rejected. A custom-field mapping that references a tenant Source Catalog extension entry without a Source Contract tenant-field declaration is rejected. A custom-field mapping that conflicts with a platform-declared mapping in a way the master schema does not permit is rejected.

**Interactions.** Custom-field mappings interact with the Source Catalog extension, Source Contract tenant-field declarations, and Admission rule extensions.

**Governing source.** Admission and Observation; Sources and the Catalog; The Contract Grammar; DEC-97bb94; FND-ERR-004.

## Metric Contract Threshold Parameters

The Metric Contract governs the metric evaluation act per Metric Evaluation. Each Metric Contract version declares zero or more parameterized thresholds whose values a tenant may set on the Contract Binding.

**Purpose.** A tenant supplies threshold values for the parameterized thresholds the Metric Contract version declares, so that tenant-specific bands, alert levels, or classification cut-points apply at metric evaluation without changing the platform-declared formula or grain.

**Scope.** Threshold parameters are carried on the Contract Binding for the relevant Metric Contract version. The set of parameterizable thresholds and each threshold's allowed value range, type, and direction are declared in the Metric Contract version's master schema. Variation outside that surface is not admissible.

**Behavior.** At metric evaluation, the Metric Evaluator applies the platform-declared formula and grain, then classifies the resulting value using the threshold values resolved from the active Binding. The emitted Metric Snapshot records the classification outcome and references the applied Metric Contract version. The Metric Evaluation Run and proof records preserve the Binding reference and threshold parameters applied. The formula and grain are platform-governed and not tenant-parameterizable.

**Constraints.**

- A threshold parameter does not change the formula. The formula is part of the Metric Contract body and is platform-governed.
- A threshold parameter does not change the grain. The grain is part of the Metric Contract body and is platform-governed.
- A threshold parameter does not introduce new classification categories. The category set is declared by the Metric Contract version.
- A threshold parameter's value must satisfy the master schema's declared range, type, and direction. Inverting a band's direction is not admissible unless the master schema explicitly permits it.

**Failure modes.** A threshold parameter that asserts a value outside the master schema's declared range is rejected at Binding creation. A threshold parameter that asserts a category the Metric Contract does not declare is rejected. A threshold parameter set against a Metric Contract version that declares no parameterized thresholds is rejected.

**Interactions.** Threshold parameters interact with Intervention Contract action parameters when the Intervention Contract is triggered by Metric Snapshot classification. The trigger uses the classification outcome the Metric Snapshot records, which reflects the tenant's threshold parameters through the Binding and proof references.

**Governing source.** Metric Evaluation; The Contract Grammar; Contract Schemas reference.

## Intervention Contract Action Parameters

The Intervention Contract governs the action-creation and outcome-resolution acts per Action Evaluation. Each Intervention Contract version declares zero or more parameterizable action attributes whose values a tenant may set on the Contract Binding.

**Purpose.** A tenant supplies values for the parameterizable action attributes the Intervention Contract version declares, so that tenant-specific assignee resolution, severity, due-date offset, or other declared parameters apply at action-creation and outcome-resolution without changing the platform-declared trigger or terminal-state set.

**Scope.** Action parameters are carried on the Contract Binding for the relevant Intervention Contract version. The set of parameterizable attributes is declared by the Intervention Contract version's master schema. The assignee mapping defined in Tenancy and Binding is the canonical example of an action parameter.

**Behavior.** At action-creation, the Action Evaluator consults the active Binding's action parameters when constructing the Action Object's creation-time payload. At outcome-resolution, the Action Evaluator consults the parameters that govern the outcome path the Intervention Contract declares for the resolved terminal state. Parameter values applied at each act are recorded in the corresponding Evidence.

**Constraints.**

- An action parameter does not modify the Intervention Contract's trigger condition. The trigger is part of the contract body and is platform-governed.
- An action parameter does not introduce or remove terminal-state categories. The terminal-state set is declared by the Intervention Contract.
- An action parameter does not change the Action Object's set-once attributes after creation. Per Action Evaluation, action-creation attributes are terminal once written.
- An action parameter does not extend Action Evaluation's two-act surface. The Intervention Contract governs action-creation and outcome-resolution; tenant parameters do not introduce additional governed acts.

**Failure modes.** An action parameter that asserts an attribute the Intervention Contract does not declare as parameterizable is rejected at Binding creation. An action parameter that asserts a value outside the master schema's declared range or that names an assignee outside the contract's declared role categories is rejected. An action parameter update applied after an Action Object has been emitted under a prior parameter value does not retroactively modify that Action Object; the prior parameter value remains recorded on the prior Action Object's creation-time Evidence.

**Interactions.** Action parameters interact with Metric Contract threshold parameters when an Intervention Contract is triggered by Metric Snapshot classification, and with the assignee-resolution mechanism defined in Tenancy and Binding when the parameter is the assignee mapping.

**Governing source.** Action Evaluation; The Contract Grammar; Tenancy and Binding; Contract Schemas reference.

## Common Constraints

The following constraints apply uniformly across every extension surface defined above. They restate the bounded variation principle in operational terms.

| Constraint | Operational form |
|---|---|
| Governing schema is the surface | An extension claim is admissible only if the relevant family master schema or catalog-extension schema declares the surface. The Contract Schemas reference is the authoritative inventory of declared contract-family surfaces. |
| Platform-declared content is preserved | An extension cannot remove or redefine platform-declared fields, rules, mappings, formulas, grains, triggers, or terminal states. |
| No new governed logic | Extensions parameterize existing platform-declared logic. They do not introduce new validation, resolution, formula, or trigger logic. |
| Versioned to a contract version or Source System version | A contract-family extension is recorded against a specific platform contract version. A Source Catalog extension is recorded against a specific Source System version and tenant Source Contract declaration. Supersession does not silently advance the extension. |
| Tenant-scoped storage | Extension records live in the tenant database under the schemas declared by the active tenant-schema ADRs. The platform contract registry and platform Source Catalog are not modified. |
| Quality treatment | Extensions pass through the gate set the governing schema declares applicable. Quality treatment is identical for tenant extension authoring acts and platform authoring acts where the governing schema declares overlap. |
| Authoritative state shape is unchanged | The shape of Source Objects, Canonical Objects, Metric Snapshots, and Action Objects emitted by the platform-governed acts remains as the contract grammar declares. Extensions widen what the tenant observes or parameterizes, not what the platform-declared shape permits. |

**Governing source.** The Contract Grammar; Tenancy and Binding; Quality Gates and Chain Integrity.

## Failure Modes

Extension authoring acts that fall outside the bounded surface are rejected at the act that introduces them, not silently absorbed and then surfaced at a later boundary act. The rejection patterns are uniform.

| Failure | Detection point | Treatment |
|---|---|---|
| Extension claim outside the governing schema's declared surface | Binding creation or Source Catalog extension creation | Rejected with the offending claim named. The Binding or extension is not persisted. |
| Extension references a non-existent platform contract version | Binding creation | Rejected. The Binding cannot bind to a contract version that the platform registry does not record. |
| Extension references a Source Catalog entry the tenant has not registered | Binding creation for Source Contract tenant-field declarations or Observation Contract custom-field mappings | Rejected. The tenant's Source Catalog extension must contain the referenced entry first. |
| Extension references a tenant field not declared through the bound Source Contract surface | Binding creation for Observation Contract custom-field mappings or Admission rule extensions | Rejected. Tenant extension fields require both Source Catalog extension metadata and Source Contract tenant-field declaration. |
| Extension downgrades, removes, or redefines platform-declared content | Binding creation | Rejected. Platform-declared content is not modifiable through the Tenant Override layer. |
| New extension Binding targets a superseded contract version | Binding creation | Rejected unless a governed historical-use exception explicitly permits the binding. Existing Bindings continue to resolve to their explicit version. |
| Extension applied retroactively against previously emitted authoritative state | Update of an existing Binding | The update is recorded going forward. Authoritative state already emitted under the prior parameter values is not modified. |

The failure modes are recorded as governance events in the tenant-side change record for the Binding or extension. Authoritative state already emitted is not mutated by an extension authoring failure.

**Governing source.** The Contract Grammar; Tenancy and Binding; The Object Model.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Authority Model: The Authority Model
- Sources and the Catalog: Sources and the Catalog
- Connectors and Readers: Connectors and Readers
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Action Evaluation: Action Evaluation
- Tenancy and Binding: Tenancy and Binding
- Quality Gates and Chain Integrity: Quality Gates and Chain Integrity
- Data Model and Schema
- API Surface
- DEC-771baf: Tenant database architecture and one-way dependency
- DEC-f02230: Tenant DB schema organization
- DEC-2c79c8: Per-tenant SQL isolation
- DEC-97bb94: N:1 SO to CO multi-source canonical evaluation
- FND-ERR-004: Multi-source composition at canonical evaluation, not admission
- Contract Schemas reference
- Decisions: ADR Registry
