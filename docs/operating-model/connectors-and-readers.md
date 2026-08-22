---
id: connectors-and-readers
order: 8.8
title: "Connectors and Readers"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, the-evaluation-boundaries, business-vocabulary, sources-and-the-catalog]
governing_sources:
  - Foundation (scope and non-negotiability)
  - Platform P05 Runtime Definitions
governing_adrs:
  - DEC-136a23 (Reader Observation Schema dual-layer)
  - DEC-1edaaa (One Observation Contract per system per Reader — amended to per source entity by DEC-0d5b39)
  - DEC-771baf (Tenant database architecture; Connection placement amended by DEC-81cd26)
  - DEC-0d5b39 (Reader anchored to one Registry Entity; source-agnostic; Flavor=(source_system,scenario); Connector via Connection.connector_id; Reader-definition / Runner-machine split)
  - DEC-81cd26 (Connection configuration platform-held; reverses D163)
  - DEC-ecd55c (Connection tenant ownership; credentials in external secret-management surface)
  - DEC-02f5a9 (Business Concept Registry supersedes Business Object / Business Field / Canonical Field identity)
errata_referenced:
  - FND-ERR-002
v2_sources:
  - system/platform/P05-runtime-definitions/connector/index.md
  - system/platform/P05-runtime-definitions/reader/index.md
word_target: 3500
---

# Connectors and Readers

## Scope

This chapter defines the platform's adapter inventory: Connector, Reader, Reader Flavor, Reader Binding, Reader Observation Binding, and Connection. It defines the UniBAT pattern under which a Reader is anchored to one Business Concept Registry Entity as the Universal Business-Aware Transactions Reader — the architectural innovation that makes the platform source-system-agnostic on input and business-aware on output. It defines the platform-scoped governance of these artifacts, and the Connection whose configuration is platform-held and tenant-owned with credentials external.

This chapter defines the Reader as a **governed definition**, not as a runtime machine. Per DEC-0d5b39 the machine that executes a Reader is the **Runner** (the admission machine named in The Runtime Ecosystem); the Reader supplies the governed definition and per-source specialization the Runner executes. This chapter does not define the runtime act of admission, the application of Admission Contract or Observation Contract per record, the Source Object emission sequence, or the tenant-scoped Admission Run — those belong to Admission and Observation. It does not define source-system structure (Sources and the Catalog) or tenant binding more broadly (Tenancy and Binding); it defines only the Connection artifact specifically. It uses the **Business Concept Registry** vocabulary (a Business Concept and its properties, `entity.property`); the former Business Object / Business Field / Canonical Field identity is superseded (DEC-02f5a9) and is not restated as live doctrine.

**Governing source.** Foundation; The Contract Grammar; Sources and the Catalog; DEC-0d5b39.

## Adapter Inventory

The platform recognizes six adapter artifacts. Five are platform-scoped and governed centrally; the Connection is platform-held in configuration and tenant-owned in authority, with credentials held externally.

| Adapter | Role | Scope | Persistent store |
|---|---|---|---|
| Connector | Technical capability to reach a source system over a declared protocol; reached at runtime through `Connection.connector_id` | Platform | `runtime.connector` and supporting protocol tables |
| Reader | Registry-Entity-anchored admission **definition** (`admitted_entity_id`; one non-archived Reader per Entity, across draft and active) implementing the UniBAT pattern; executed by the Runner | Platform | `runtime.reader` |
| Reader Flavor | Source specialization identified by `(source_system, scenario)` — one active Flavor per `(reader, source_system, scenario)`; a Flavor reads **many** entities. The governing Connector-resolution authority is the Connection (`connector_id`); the retained `reader_flavor.connector_id`/`connection_id` columns are current compatibility substrate, not a governing edge (retirement decided DEC-0d5b39 D3, not yet implemented — TSK-ccc82c) | Platform | `runtime.reader_flavor` |
| Reader Binding | Platform-governed **per-entity Admission-Contract binding** at two levels — flavor-specific `(reader, flavor, source_entity, environment)` and reader-level fallback `(reader, source_entity, environment)` with `flavor_id IS NULL` (resolver selects flavor-specific first). `reader_binding.source_contract_id` carries an **admission-contract id** (historical column name); `(source_contract_id, version_code)` is the effective AC version pin (source-filter design v4) | Platform | `runtime.reader_binding` |
| Reader Observation Binding | Platform-governed **per-entity Observation-Contract pin**, coordinate `(reader, flavor, source_entity, environment)` → `(observation_contract_id, version_code)` — the declaration a given admission run executes under (the deprecated `reader_flavor.observation_contract_id` is retired, 0 rows) | Platform | `runtime.reader_observation_binding` |
| Connection | Access record naming the Connector (`connector_id`, the runtime Connector-resolution edge); **configuration platform-held** in `runtime.connection`, **tenant-owned** by tenant identity, **credentials external** (secret reference only on the record) | Platform-held config, tenant-owned | Platform `runtime.connection` + external secret store |

Connector, Reader, Reader Flavor, and both bindings are governed centrally and reused across tenants. The Connection's configuration is platform-held in `runtime.connection` (DEC-81cd26, reversing D163) and tenant-owned through the tenant identity; it names the Connector via `connector_id`, carries only a credential reference, and the credentials themselves live in the external secret-management surface (DEC-ecd55c). No platform-side artifact carries tenant credentials.

**Single Connector topology (DEC-0d5b39 D2/D3).** The Connector is reached through **`Connection.connector_id`** — the one runtime Connector-resolution **authority**. DEC-0d5b39 D3 **decides** the retirement of the independent Flavor-to-Connector edge; the platform substrate has **not** completed it — `reader_flavor.connector_id` and `connection_id` remain live columns still written by the reader-authoring service, tracked for removal under TSK-ccc82c. This chapter treats `Connection.connector_id` as the sole governing authority and the flavor columns as current compatibility substrate pending that retirement.

**Binding resolution (source-filter design v5–v12, TSK-a83188).** An admission run resolves its governing chain **once, before any fetch**, from the exact context `(reader, flavor, environment, source entity)`: the Observation binding is the four-way exact row (exactly one, active); the **effective Admission Contract** (`reader_binding`) is selected flavor-specific first, with a reader-level (`flavor_id IS NULL`) row as the only fallback, exactly one at the winning level; the Observation Contract's AC pair must equal the effective AC pair, and its SC pair must equal the effective AC version's declared parent pair. Any missing, ambiguous, inactive, or mismatched coordinate is a **chain-integrity refusal of the whole invocation** — there is no table-name fallback, no first-match selection, and no scenario/configuration substitute. The resolved context (all pairs, the winning level, and the normalized filter digest) travels with the run into Evidence and Lineage.

**Governing source.** Platform P05 Runtime Definitions; DEC-0d5b39; DEC-81cd26; DEC-ecd55c.

## Connector

**Purpose.** A Connector declares the technical capability to reach a source system over a defined protocol.

**Scope.** A Connector covers protocol family, supported authentication methods, capability metadata, and provenance describing how the connector definition was authored or curated. It does not cover source-system structure, Business Concept selection, validation rules, or business meaning.

**Behavior.** A Connector is registered with a connector code, protocol family, authentication-method support, capability flags, and provenance. At runtime the Connector is resolved through the invoking Connection's `connector_id`; the **Runner** invokes the resolved Connector to obtain a transport channel, and the Connector returns observed records as raw protocol-shaped payload.

**Constraints.**

- A Connector provides reachability only.
- A Connector does not declare Admission Contract rules.
- A Connector does not declare Observation Contract mappings.
- A Connector does not define identity semantics for admitted records.
- A Connector carries no tenant credentials; the Connection names the Connector and supplies a resolved credential to it at invocation, and the credential itself is held in the external secret store.

**Failure modes.**

- If an endpoint is unreachable, the Connector returns a transport error and the invocation terminates without producing Source Objects.
- If authentication fails, the Connector returns an authentication error and the invocation terminates; failure is recorded on the Admission Run.
- If a protocol error occurs (malformed response, version mismatch), the Connector returns the error and the invocation terminates; failure is recorded on the Admission Run.
- Connector failures are recorded as operational Evidence per the rejection semantics defined in Admission and Observation.

**Interactions.** The Connector is resolved through the invoking **Connection** (`connector_id`) and invoked by the **Runner** at admission time. The Connection resolves the credential the Runner supplies to the Connector at invocation. The governing Connector authority is the Connection, not the Flavor; the retained `reader_flavor.connector_id` column is compatibility substrate pending retirement (TSK-ccc82c).

**Governing source.** Platform P05 Runtime Definitions, Connector dossier; DEC-0d5b39; The Contract Grammar.

## Reader

**Purpose.** A Reader is the platform's governed **admission definition** for one Business Concept Registry Entity, implementing the UniBAT pattern (Universal Business-Aware Transactions Reader). It is the definition the **Runner** (the admission machine) executes; the Reader does not itself perform runtime work.

**Scope.** A Reader defines the admission for one Business Concept Registry Entity: which Admission and Observation Contracts govern validation, mapping, and identity (per source entity), and the specialization (through its Flavors) the Runner applies. The runtime act sequence — Source Object emission, Evidence and Lineage, the Admission Run — is performed by the Runner and defined in Admission and Observation. A Reader defines nothing beyond the Source Object boundary: not canonical evaluation, metric evaluation, or action evaluation.

**Behavior.** A Reader is registered with a reader code and the Business Concept Registry Entity it admits (`admitted_entity_id`). At invocation the **Runner** executes the Reader's definition per the act sequence in Admission and Observation: it resolves the Connector through the Connection, obtains records, applies the governed Admission Contract (`reader_binding`, per source entity) for validation, applies the governed Observation Contract (`reader_observation_binding`, per source entity) for mapping and identity composition, emits a Source Object with per-record Evidence and per-object Lineage for each admitted transaction, records Evidence only for refused records (no Lineage is assigned to a record that was not admitted), and writes the tenant-scoped Admission Run. Where Foundation attributes an admission act to "the Reader," it names this Reader-governed act the Runner performs; the naming split (DEC-0d5b39) changes no admission-boundary rule.

**Constraints.**

- A Reader admits one Business Concept Registry Entity — one non-archived Reader per Entity, across draft and active (`admitted_entity_id`; `uq_reader__active_entity WHERE archived_at IS NULL`; DEC-0d5b39). A second Entity requires a second Reader. The Reader is *anchored to* an Entity, never "grained" (grain is reserved for Canonical/Metric Contracts). A Reader carries no source system; source specialization lives in its Flavors and per-entity bindings; `function_code`/`subfunction_code` are non-identity classification.
- A Reader's definition does not admit fields not declared by the governed Observation Contract.
- A Reader does not define Canonical Contract logic.
- A Reader definition, once executed, does not modify previously emitted Source Objects.
- A Reader carries governed contract content as-is. The Runner does not downgrade a blocking validation rule to a warning at runtime, override default actions, or introduce undeclared validation logic.

**Failure modes.**

- If the governed Observation Contract for a source entity is missing or unresolved at invocation, the Runner records the unavailability on the Admission Run and admission is paused.
- If the Reader's per-entity bindings have inconsistent versions (for example, a `reader_binding` Admission Contract whose parent Source Contract the entity's Observation Contract does not bind to), the Runner rejects the invocation before record processing.
- If a Reader is executed outside a governed Reader Binding, the Runner rejects the invocation; ad-hoc admission is not admissible.

**Interactions.** A Reader is specialized by one or more Reader Flavors, each identified by `(source_system, scenario)`. At admission, the Runner executes the Reader against the per-entity `reader_binding` (effective Admission Contract version + source entity + environment) and the per-entity `reader_observation_binding` (Observation Contract version), resolving the Connector through the Connection. The outputs (Source Objects, Evidence, Lineage, Admission Run) are consumed by the canonical evaluation boundary and by tenant-side reporting.

**Governing source.** Platform P05 Runtime Definitions, Reader dossier; DEC-0d5b39; The Contract Grammar; The Evaluation Boundaries.

## The UniBAT Pattern

The Reader is the platform's central architectural innovation. The acronym names what the pattern asserts: Universal Business-Aware Transactions Reader. Each term carries a structural commitment. The pattern governs the admission the Runner performs; where the terms below say "the Reader admits," they name the Reader-governed act the Runner executes.

**Universal.** A single Reader pattern covers any source system. The pattern does not specialize per database vendor, per file format, or per protocol. Specialization happens in the Connector (protocol, resolved through the Connection) and the Reader Flavor (`(source_system, scenario)`), not in the Reader definition itself. The Reader's governed responsibilities, sequence, and failure modes are the same regardless of whether the source is an ECC landscape, an OData endpoint, a REST API, a CSV file, or a database table.

**Business-Aware.** The admission act emits Source Objects whose payload is keyed by **Business Concept property identifiers** (`entity.property` in the Business Concept Registry), not by source-system field names. The translation from source field paths to Registry properties happens at the act of admission under the governed Observation Contract. The platform's subsequent layers (Canonical Evaluation, Metric Evaluation, Action Evaluation) read Business-Aware payload, not source-shaped payload. The source system's schema, naming, or representation choices do not bleed into the platform's authoritative state.

**Transactions.** Admission handles one transaction at a time. A transaction is a record that the source system identifies as one business event (an invoice, a journal entry, an inventory movement). Each admitted transaction becomes one Source Object. The act does not bundle multiple transactions into one object, and it does not split one transaction across multiple objects. The transaction is the admission unit.

**Reader.** The Reader defines admission of state. It does not define derivation of new values or aggregates. The platform separates admission from canonical evaluation deliberately: admission preserves what the source system declared; canonical evaluation applies the governed Canonical Contract to derive business meaning. A Reader definition (or a Runner executing it) that performs canonical resolution is incorrect under the execution model.

The UniBAT pattern differs structurally from conventional ETL connectors and data integration platforms. ETL connectors couple to source schema and rewrite records as part of the integration path; consuming layers read the rewritten shape. The UniBAT Reader admits records under an Admission Contract that validates them and an Observation Contract that translates source paths to Business Concept property identifiers; the platform's subsequent layers read the Business-Aware shape directly. Data integration platforms typically use schema-on-read with implicit semantics; the UniBAT Reader uses schema-on-write under explicit governed contracts.

The pattern's three structural consequences:

| Consequence | Effect |
|---|---|
| Source-system portability | A source-system migration preserves the governed **Business Concept identity** and a compatible downstream Canonical Contract. It generally requires **new Source Contract, Admission Contract, and Observation Contract versions** (and new bindings) whenever source shape, validation, selection, or mapping changes — the Source Contract is specific to a source table/API shape and source-system version, and the Observation Contract binds source paths. Portability is stability of Business Concept identity and downstream compatible authority, **not** unchanged contracts |
| No transformation step | The platform does not maintain a separate transformation layer between source observation and canonical evaluation; the Observation Contract carries the binding rules and the governed Canonical Contract carries the canonical resolution |
| Audit traceability | Every Business Concept property value on a Source Object is traceable to a source field path through the governed Observation Contract version pinned, per source entity, by the Reader Observation Binding at admission time |

**Constraints.**

- Admission produces one transaction per Source Object.
- Admission does not bundle, split, or alter transactions.
- Source Objects are keyed by Business Concept property identifiers, not by source-system field names.
- A Reader definition, or a Runner executing it, that violates any of the four UniBAT terms is incorrect under the execution model.

**Failure modes.**

- If admission modifies record shape, later chapters describe the boundary error: the Source Object payload does not match the governed Observation Contract output and the Canonical Contract cannot resolve it.
- If admission bundles multiple transactions into one Source Object, the cardinality at the canonical boundary becomes incorrect and metric grain alignment fails.
- If admission emits Source Objects with source-shaped keys, subsequent Canonical Contract resolution fails and Canonical Object emission is rejected.

**Governing source.** The Contract Grammar; The Evaluation Boundaries; Business Vocabulary; DEC-0d5b39.

## Reader Flavor

**Purpose.** A Reader Flavor is a Reader's source specialization identified by `(source_system, scenario)`. It carries the per-source-entity Observation Contract pins (through the Reader Observation Binding) that produce the runtime-ready specialization the Runner invokes. The governing Connector-resolution authority is the Connection (`connector_id`), not the Flavor.

**Scope.** A Reader Flavor covers the `(source_system, scenario)` it specializes and the per-source-entity Observation Contract bindings that map to Business Concept properties for that source. It does not cover the Connector (resolved through the Connection), tenant credentials (resolved through the Connection from the external secret store), or the effective Admission Contract version (named by the Reader Binding, per source entity).

**Behavior.** A Reader Flavor is registered with a flavor code, a Reader reference, a `source_system`, and a `scenario` (default `default`); its Observation Contract pins are held per source entity in the Reader Observation Binding. The platform may pre-compute a derived runtime configuration from the governed Observation Contract for a given source entity; that configuration is the Reader Flavor's runtime copy for that entity and is regenerated from the governed source when the pinned Observation Contract version changes.

**Constraints.**

- A Reader Flavor is identified by `(source_system, scenario)`; **exactly one active Flavor per `(reader, source_system, scenario)`** (`uq_reader_flavor__active_scenario`; DEC-0d5b39 topology P-F1…P-F8).
- The governing Connector-resolution authority for a Flavor is the **Connection** (`connector_id`), not the Flavor. DEC-0d5b39 D3 decides retirement of the Flavor→Connector edge; the retained `reader_flavor.connector_id`/`connection_id` columns are current compatibility substrate (still written by the authoring service), tracked for removal under TSK-ccc82c, and carry no governing authority.
- A Reader Flavor binds Observation Contracts **per source entity** via `reader_observation_binding`; one Flavor observes **many** entities, each under its own Observation Contract pin. This amends the former one-Observation-Contract-per-Flavor reading of DEC-1edaaa (see DEC-0d5b39 and DEC-17112b). No single Observation Contract is identified directly on the Flavor (the deprecated `reader_flavor.observation_contract_id` is retired, 0 rows).
- A Reader Flavor's runtime copy is derived from the governed Observation Contract and is not independently edited.
- A Reader Flavor does not declare validation rules or canonical translations independently of its bound contracts.

**Failure modes.**

- If a Flavor's pinned Observation Contract version (for a source entity) is superseded or non-active, the Reader Observation Binding continues to reference the named version (pin immutability; no silent rebind, Invariant IV), and the resolver **refuses** the invocation as fail-closed (`oc_inactive`) until a governed successor Observation-Contract binding is installed. Adopting the superseding version requires a tracked authoring act on the binding; the Runner never executes superseded OC content.
- If the Connector resolved through the invoking Connection is unavailable at invocation, the admission act records the unavailability and pauses pending Connector availability.
- If a Reader Flavor's runtime copy diverges from the governed Observation Contract (for example, due to manual edit of the runtime copy), the divergence is detected at admission-act validation and the runtime copy is regenerated from the governed source.

**Interactions.** A Reader Flavor is the `(source_system, scenario)` specialization the Runner selects at admission, carrying the per-entity Observation Contract pins. The Connector and credential are resolved through the Connection at invocation. The dual-layer arrangement governed by DEC-136a23 and recorded as FND-ERR-002 holds at the Flavor's runtime copy: the governed Observation Contract is the single source of truth; the Flavor's runtime copy is a derived operational artifact.

**Governing source.** DEC-136a23; DEC-1edaaa; DEC-0d5b39; Platform P05 Runtime Definitions; The Contract Grammar.

## Reader Binding

**Purpose.** A Reader Binding records the governed **per-source-entity Admission Contract version** the Runner applies for a specific admission context, at either of two coordinates: **flavor-specific** `(reader, flavor, source_entity, environment)` or the **reader-level fallback** `(reader, source_entity, environment)` with `flavor_id IS NULL`. The resolver loads both and selects flavor-specific first, reader-level second.

**Scope.** A Reader Binding covers the platform-governed binding to one effective Admission Contract version at either coordinate: the **flavor-specific** binding `(reader, flavor, source_entity, environment)` and the **reader-level fallback** `(reader, source_entity, environment)` with null `flavor_id`. It does not cover tenant-side configuration; tenant-side variation lives on the Connection or on Contract Bindings, both described in Tenancy and Binding.

**Behavior.** A Reader Binding is registered with a reader reference, a `source_entity`, an `environment_code`, and an effective Admission Contract version reference (carried, for historical reasons, in `source_contract_id` — see the inventory note). The **flavor reference is present only for a flavor-specific row and is null for the reader-level fallback row**. At most one active binding per `(reader, source_entity, environment, flavor)` and per `(reader, source_entity, environment)`. The Runner invokes admission against the resolved Reader Binding for the exact context, selecting the flavor-specific row first and the reader-level fallback second; the Binding identifies which governed Admission Contract version is applied.

**Constraints.**

- A Reader Binding is unique-active at one of two coordinates: flavor-specific `(reader, flavor, source_entity, environment)` (`uq_reader_binding_active_flavor`) or the reader-level fallback `(reader, source_entity, environment)` with null `flavor_id` (`uq_reader_binding_active_reader`). The fallback row carries no Flavor.
- A Reader Binding references exactly one effective Admission Contract version.
- A Reader Binding does not rewrite governed contract content; it records which version is applied for the coordinate.
- A Reader Binding is platform-governed. Tenant-specific access configuration (credential reference, environment URLs, rotation windows) is not on the Reader Binding; it is on the Connection.

**Failure modes.**

- If the Admission Contract version named by the Reader Binding is superseded or otherwise non-active, the Binding continues to reference the named (pinned) version — pin immutability holds and the Runner never silently rebinds to a superseding version (Invariant IV). But the resolver requires the effective AC (and its parent SC, and the entity's OC) version `governance_state_code` to be **active** and **refuses** any non-active/superseded version: the invocation **fails closed** until a governed successor binding is installed. The Runner never executes superseded contract content.
- If, for the resolved context, the per-entity Observation Contract does not satisfy the AC/SC pair equalities named in Binding Resolution, the Runner rejects the invocation; the inconsistency is recorded as a chain-integrity failure.
- If no active binding exists for the exact `(reader, flavor, source_entity, environment)` (or its reader-level fallback), the Runner refuses the whole invocation; there is no first-match substitute.

**Interactions.** A Reader Binding is one coordinate the Runner resolves at invocation. At invocation, the Runner resolves the Flavor `(source_system, scenario)`, the per-entity `reader_binding` (effective Admission Contract version), and the per-entity `reader_observation_binding` (Observation Contract version), and resolves the Connector and credential through the Connection. Together, these define one fully bound admission act.

**Governing source.** Platform P05 Runtime Definitions; DEC-0d5b39; The Contract Grammar; Contract Chain Assembly.

## Connection

**Purpose.** A Connection is the access record naming the Connector (`connector_id`, the runtime Connector-resolution edge) — **configuration platform-held** in `runtime.connection`, **tenant-owned** through the tenant identity, with **credentials external** in the secret-management surface (only a credential reference is on the record) — that authorizes reaching a tenant-owned source system.

**Scope.** A Connection covers the Connector reference (`connector_id`), the credential reference, environment-specific access URLs or hostnames, rotation windows, and per-tenant access constraints (rate limits, allowed time windows). It does not cover the platform-side Connector definition (that is the Connector artifact) or any contract content. It never holds credential material.

**Behavior.** A Connection is registered with a connection code, the Connector it names (`connector_id`), the tenant identity that owns it, a credential reference (the credentials themselves are held in the platform's external secret-management surface, never on the Connection record), and the per-tenant access configuration. At admission invocation, the Runner resolves the Connection for the invoking tenant and context, resolves the Connector through `connector_id`, resolves the credential reference against the external secret store, and supplies the resolved credential to the Connector.

**Constraints.**

- A Connection's configuration is platform-held in `runtime.connection` (DEC-81cd26, reversing D163) and tenant-owned by tenant identity; credentials are external in the secret-management surface (DEC-ecd55c). Platform-side artifacts (Connector, Reader, Flavor, Binding) do not carry tenant credentials, and neither does the Connection record — it carries only a reference.
- A Connection names exactly one Connector (`connector_id`) and authorizes reaching one tenant-owned source system. Multi-Connector or multi-tenant bundles are separate Connections.
- A Connection does not declare validation rules, mapping rules, or contract content. It declares Connector reference and access only.
- A Connection's credential material is not preserved on the Connection record; only a credential reference is recorded.

**Failure modes.**

- If a Connection's credential reference resolves to expired credentials, Connector authentication fails at invocation; failure is recorded on the Admission Run and the tenant is notified through the platform's tenant-facing channels (defined in Tenancy and Binding).
- If a Connection is missing for the invoking tenant and context, the Runner rejects the invocation; admission cannot proceed without a Connection.
- If a Connection's per-tenant access configuration would block invocation (rate limit exceeded, outside allowed window), the Runner records the block and the invocation is held until the configuration permits proceeding.

**Interactions.** The Connection participates at admission invocation: it names the Connector (`connector_id`), resolves the credential reference against the external secret store, and supplies the resolved credential to the Connector through the Runner. Connection lifecycle (creation, rotation, retirement) is part of tenant onboarding and ongoing tenant-side governance, described in Tenancy and Binding. The external secret store itself is described in Security Operations.

**Governing source.** DEC-81cd26; DEC-ecd55c; DEC-0d5b39; Platform P05 Runtime Definitions; Tenancy and Binding.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Runtime Ecosystem: The Runtime Ecosystem
- Business Vocabulary: Business Vocabulary
- Sources and the Catalog: Sources and the Catalog
- Contract Chain Assembly: Contract Chain Assembly
- Admission and Observation: Admission and Observation
- Tenancy and Binding: Tenancy and Binding
- Platform P05 Runtime Definitions
