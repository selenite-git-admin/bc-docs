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
  - DEC-1edaaa (One Observation Contract per system per Reader)
  - DEC-771baf (Tenant database architecture; tenant-scoped Connection)
errata_referenced:
  - FND-ERR-002
v2_sources:
  - system/platform/P05-runtime-definitions/connector/index.md
  - system/platform/P05-runtime-definitions/reader/index.md
word_target: 3500
---

# Connectors and Readers

## Scope

This chapter defines the platform's adapter inventory: Connector, Reader, Reader Flavor, Reader Binding, and Connection. It defines the UniBAT pattern under which Readers operate as the Universal Business-Aware Transactions Reader, the architectural innovation that makes the platform source-system-agnostic on input and business-aware on output. It defines the platform-scoped governance of Connector and Reader artifacts and the tenant-scoped Connection that carries credentials.

This chapter does not define the runtime act of admission, the application of Admission Contract or Observation Contract per record, the Source Object emission sequence, or the tenant-scoped Admission Run. Those belong to Admission and Observation. This chapter does not define source-system structure (Sources and the Catalog) or tenant binding more broadly (Tenancy and Binding); it defines only the Connection artifact specifically.

**Governing source.** Foundation; The Contract Grammar; Sources and the Catalog.

## Adapter Inventory

The platform recognizes five adapter artifacts. Four are platform-scoped and governed centrally; one is tenant-scoped and carries access credentials.

| Adapter | Role | Scope | Persistent store |
|---|---|---|---|
| Connector | Technical capability to reach a source system over a declared protocol | Platform | `runtime.connector` and supporting protocol tables |
| Reader | Business-Object-oriented admission component implementing the UniBAT pattern | Platform | `runtime.reader` |
| Reader Flavor | Reader variant bound to one Connector, one Observation Contract, and one source-system version context | Platform | `runtime.reader_flavor` |
| Reader Binding | Platform-governed binding from a Reader Flavor to a Source Contract version and execution context | Platform | `runtime.reader_binding` |
| Connection | Tenant-scoped credentials and access record for a Reader Flavor against a tenant-owned source system | Tenant | Tenant connection store |

Connector, Reader, Reader Flavor, and Reader Binding are governed centrally and reused across tenants. The Connection is tenant-scoped under DEC-771baf and carries credentials and per-tenant access configuration; the platform-side artifacts do not carry tenant credentials.

**Governing source.** Platform P05 Runtime Definitions; DEC-771baf.

## Connector

**Purpose.** A Connector declares the technical capability to reach a source system over a defined protocol.

**Scope.** A Connector covers protocol family, supported authentication methods, capability metadata, and provenance describing how the connector definition was authored or curated. It does not cover source-system structure, Business Field selection, validation rules, or business meaning.

**Behavior.** A Connector is registered with a connector code, protocol family, authentication-method support, capability flags, and provenance. The platform invokes a Connector to obtain a transport channel to a source system; the Connector returns observed records to the Reader as raw protocol-shaped payload.

**Constraints.**

- A Connector provides reachability only.
- A Connector does not declare Admission Contract rules.
- A Connector does not declare Observation Contract mappings.
- A Connector does not define identity semantics for admitted records.
- A Connector is not tenant-scoped; tenant credentials live on the Connection.

**Failure modes.**

- If an endpoint is unreachable, the Connector returns a transport error and the invocation terminates without producing Source Objects.
- If authentication fails, the Connector returns an authentication error and the invocation terminates; failure is recorded on the Admission Run.
- If a protocol error occurs (malformed response, version mismatch), the Connector returns the error and the invocation terminates; failure is recorded on the Admission Run.
- Connector failures are recorded as operational Evidence per the rejection semantics defined in Admission and Observation.

**Interactions.** The Connector is invoked by the Reader at admission time. The Connection supplies credentials to the Connector at invocation. The Reader Flavor names the Connector that its admission acts use.

**Governing source.** Platform P05 Runtime Definitions, Connector dossier; The Contract Grammar.

## Reader

**Purpose.** A Reader is the platform runtime component that performs admission for a Business Object family against a declared source system, implementing the UniBAT pattern (Universal Business-Aware Transactions Reader).

**Scope.** A Reader covers the admission orchestration for one Business Object family: Connector access, Admission Contract validation, Observation Contract mapping, Source Object emission, and Admission Run recording. It does not cover canonical evaluation, metric evaluation, action evaluation, or any operation that produces objects beyond the Source Object.

**Behavior.** A Reader is registered with a reader code, the Business Object family it admits, and references to the Connector and contract artifacts that govern it. At invocation time, the Reader coordinates the act sequence defined in Admission and Observation: it obtains records via the Connector, applies the governed Admission Contract for validation, applies the governed Observation Contract for mapping and identity composition, emits Source Objects together with Evidence and Lineage, and writes the tenant-scoped Admission Run.

**Constraints.**

- A Reader admits one Business Object family. A second family requires a second Reader.
- A Reader does not infer fields not declared by the governed Observation Contract.
- A Reader does not apply Canonical Contract logic.
- A Reader does not modify previously emitted Source Objects.
- A Reader applies governed contract content as-is. It does not downgrade a blocking validation rule to a warning at runtime, override default actions, or introduce undeclared validation logic.

**Failure modes.**

- If the governed Observation Contract is missing or unresolved at invocation, the Reader records the unavailability on the Admission Run and admission is paused.
- If the Reader's referenced contract artifacts have inconsistent versions (for example, a Reader Binding pointing at a Source Contract version that the Observation Contract does not bind to), the runtime rejects the invocation before record processing.
- If the Reader is invoked outside a governed Reader Binding, the runtime rejects the invocation; ad-hoc admission is not admissible.

**Interactions.** A Reader is bound to one or more Reader Flavors that specialize it for specific source-system contexts. At admission, a Reader is invoked against a Reader Binding that names the Source Contract version and the execution context. The Reader's outputs (Source Objects, Evidence, Lineage, Admission Run) are consumed by the canonical evaluation boundary and the Admission Run is consumed by tenant-side reporting.

**Governing source.** Platform P05 Runtime Definitions, Reader dossier; The Contract Grammar; The Evaluation Boundaries.

## The UniBAT Pattern

The Reader is the platform's central architectural innovation. The acronym names what the pattern asserts: Universal Business-Aware Transactions Reader. Each term carries a structural commitment.

**Universal.** A single Reader pattern covers any source system. The pattern does not specialize per database vendor, per file format, or per protocol. Specialization happens in the Connector (protocol) and the Reader Flavor (source-system version), not in the Reader itself. The Reader's responsibilities, sequence, and failure modes are the same regardless of whether the source is SAP ECC, an OData endpoint, a REST API, a CSV file, or a database table.

**Business-Aware.** The Reader emits Source Objects whose payload is keyed by Business Field codes, not by source-system field names. The translation from source field paths to Business Field codes happens at the act of admission under the governed Observation Contract. The platform's subsequent layers (Canonical Evaluation, Metric Evaluation, Action Evaluation) read Business-Aware payload, not source-shaped payload. The source system's schema, naming, or representation choices do not bleed into the platform's authoritative state.

**Transactions.** The Reader admits one transaction at a time. A transaction is a record that the source system identifies as one business event (an invoice, a journal entry, an inventory movement). Each admitted transaction becomes one Source Object. The Reader does not bundle multiple transactions into one object, and it does not split one transaction across multiple objects. The transaction is the admission unit.

**Reader.** The Reader admits state. It does not derive new values or compute aggregates. The platform separates admission from canonical evaluation deliberately: admission preserves what the source system declared; canonical evaluation applies the governed Canonical Contract to derive business meaning. A Reader that performs canonical resolution is incorrect under the execution model.

The UniBAT pattern differs structurally from conventional ETL connectors and data integration platforms. ETL connectors couple to source schema and transform records as part of the ingestion path; consuming layers read the transformed shape. The UniBAT Reader admits records under a Source Contract that names them by Business Field code and an Observation Contract that translates source paths to those codes; the platform's subsequent layers read the Business-Aware shape directly. Data integration platforms typically use schema-on-read with implicit semantics; the UniBAT Reader uses schema-on-write under explicit governed contracts.

The pattern's three structural consequences:

| Consequence | Effect |
|---|---|
| Source-system portability | Migrating a source system replaces the Connector and Reader Flavor; the Source Contract, Observation Contract, and Canonical Contract continue to apply unchanged because the Business-Aware identifiers persist |
| No transformation step | The platform does not maintain a separate transformation layer between source observation and canonical evaluation; the Observation Contract carries the binding rules and the Canonical Mapping carries the canonical translation |
| Audit traceability | Every Business Field value on a Source Object is traceable to a source field path through the governed Observation Contract version pinned by the Reader Binding at admission time |

**Constraints.**

- The Reader admits one transaction per Source Object.
- The Reader does not bundle, split, or alter transactions.
- The Reader emits Source Objects keyed by Business Field codes, not by source-system field names.
- A Reader implementation that violates any of the four UniBAT terms is incorrect under the execution model.

**Failure modes.**

- If a Reader implementation modifies record shape during admission, later chapters describe the boundary error: the Source Object payload does not match the governed Observation Contract output and Canonical Evaluation cannot apply the Canonical Mapping.
- If a Reader bundles multiple transactions into one Source Object, the cardinality at the canonical boundary becomes incorrect and metric grain alignment fails.
- If a Reader emits Source Objects with source-shaped keys, subsequent Canonical Mapping lookups fail and Canonical Object emission is rejected.

**Governing source.** The Contract Grammar; The Evaluation Boundaries; Business Vocabulary.

## Reader Flavor

**Purpose.** A Reader Flavor binds one Reader to one Connector, one Observation Contract, and one source-system version context, producing the runtime-ready specialization that admission acts invoke.

**Scope.** A Reader Flavor covers the source-system version it admits, the Connector that reaches that version, the Observation Contract that maps to Business Fields for that version, and the derived runtime configuration that the Reader applies during admission. It does not cover tenant credentials (those are on the Connection) or the Source Contract version (that is named by the Reader Binding).

**Behavior.** A Reader Flavor is registered with a flavor code, a Reader reference, a Connector reference, an Observation Contract reference, and a source-system version reference. The platform may pre-compute a derived runtime configuration from the governed Observation Contract; that configuration is the Reader Flavor's runtime copy and is regenerated from the governed source when the Observation Contract version changes.

**Constraints.**

- A Reader Flavor binds to exactly one Reader.
- A Reader Flavor binds to exactly one Connector.
- A Reader Flavor binds to exactly one Observation Contract version. Per DEC-1edaaa, one governed Observation Contract per system per Reader.
- A Reader Flavor's runtime copy is derived from the governed Observation Contract and is not independently edited.
- A Reader Flavor does not declare validation rules or canonical translations independently of its bound contracts.

**Failure modes.**

- If a Reader Flavor's bound Observation Contract version is superseded, the Flavor continues to reference the named version. Adopting the superseding Observation Contract version requires registering a new Reader Flavor or governance-updating this Flavor through a tracked authoring act. The runtime does not silently re-bind the Flavor to a superseding version (Invariant IV).
- If a Reader Flavor's bound Connector becomes unavailable at invocation, the admission act records the unavailability and pauses pending Connector availability.
- If a Reader Flavor's runtime copy diverges from the governed Observation Contract (for example, due to manual edit of the runtime copy), the divergence is detected at admission-act validation and the runtime copy is regenerated from the governed source.

**Interactions.** A Reader Flavor is the runtime-ready specialization that a Reader Binding selects at admission. The Connection supplies credentials for the Flavor's Connector at invocation. The dual-layer arrangement governed by DEC-136a23 and recorded as FND-ERR-002 holds at the Flavor's runtime copy: the governed Observation Contract is the single source of truth; the Flavor's runtime copy is a derived operational artifact.

**Governing source.** DEC-136a23; DEC-1edaaa; Platform P05 Runtime Definitions; The Contract Grammar.

## Reader Binding

**Purpose.** A Reader Binding records which governed contract versions the runtime applies for a specific admission invocation context, naming the Reader Flavor, the Source Contract version, and the execution context.

**Scope.** A Reader Binding covers the platform-governed runtime binding from a Reader Flavor to one Source Contract version and one execution context. It does not cover tenant-side configuration; tenant-side variation lives on the Connection or on Contract Bindings, both described in Tenancy and Binding.

**Behavior.** A Reader Binding is registered with a binding code, a Reader Flavor reference, a Source Contract version reference, and an execution context (the schedule, mode, and run parameters that govern when admission acts run). The runtime invokes admission against a Reader Binding; the Binding identifies which governed contract versions are applied.

**Constraints.**

- A Reader Binding references exactly one Reader Flavor.
- A Reader Binding references exactly one Source Contract version.
- A Reader Binding does not rewrite governed contract content; it records which versions are applied.
- A Reader Binding is platform-governed. Tenant-specific access configuration (credentials, environment URLs, rotation windows) is not on the Reader Binding; it is on the Connection.

**Failure modes.**

- If the Source Contract version named by the Reader Binding is superseded, the Binding continues to reference the named version. The runtime applies the named (superseded) Source Contract version unless the binding is governance-updated to reference the superseding version. The runtime does not silently route invocations to a superseding version (Invariant IV).
- If the Reader Flavor's bound Observation Contract does not bind to the Source Contract version named by the Reader Binding, the runtime rejects the invocation; the inconsistency is recorded as a chain-integrity failure.
- If the execution context is invalid at invocation time (for example, the schedule has lapsed without a current window), the runtime records the lapse and the invocation is held until a valid context exists.

**Interactions.** A Reader Binding is the artifact that admission invocations name. At invocation, the Binding identifies the Reader Flavor, which identifies the Connector and the Observation Contract version; the Binding adds the Source Contract version and the execution context; the Connection adds tenant credentials. Together, these references define one fully bound admission act.

**Governing source.** Platform P05 Runtime Definitions; The Contract Grammar; Contract Chain Assembly.

## Connection

**Purpose.** A Connection is the tenant-scoped record of credentials and access configuration that authorizes a Reader Flavor's Connector to reach a tenant-owned source system.

**Scope.** A Connection covers tenant credentials, environment-specific access URLs or hostnames, rotation windows, and per-tenant access constraints (rate limits, allowed time windows). It does not cover the platform-side Connector definition (that is the Connector artifact), the Reader Flavor binding (that is the Reader Flavor artifact), or any contract content.

**Behavior.** A Connection is registered with a connection code, the Reader Flavor it authorizes, the tenant identity that owns the credentials, the credential reference (the credentials themselves are stored in the platform's secret-management surface, not on the Connection record), and the per-tenant access configuration. At admission invocation, the runtime resolves the Connection for the invoking tenant and Reader Flavor, retrieves credentials, and supplies them to the Connector.

**Constraints.**

- A Connection is tenant-scoped. Platform-side artifacts (Connector, Reader, Flavor, Binding) do not carry tenant credentials.
- A Connection authorizes one Reader Flavor against one tenant-owned source system. Multi-Flavor or multi-tenant credential bundles are separate Connections.
- A Connection does not declare validation rules, mapping rules, or contract content. It declares access only.
- A Connection's credentials are not preserved on the Connection record itself; only a credential reference is recorded.

**Failure modes.**

- If a Connection's credential reference resolves to expired credentials, the Connector authentication fails at invocation; failure is recorded on the Admission Run and the tenant is notified through the platform's tenant-facing channels (defined in Tenancy and Binding).
- If a Connection is missing for the invoking tenant and Reader Flavor, the runtime rejects the invocation; admission cannot proceed without a Connection.
- If a Connection's per-tenant access configuration would block invocation (rate limit exceeded, outside allowed window), the runtime records the block and the invocation is held until the configuration permits proceeding.

**Interactions.** The Connection participates at admission invocation, supplying credentials to the Connector. Connection lifecycle (creation, rotation, retirement) is part of tenant onboarding and ongoing tenant-side governance, described in Tenancy and Binding. The credential store itself is described in Security Operations.

**Governing source.** DEC-771baf; Platform P05 Runtime Definitions; Tenancy and Binding.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- Business Vocabulary: Business Vocabulary
- Sources and the Catalog: Sources and the Catalog
- Contract Chain Assembly: Contract Chain Assembly
- Admission and Observation: Admission and Observation
- Tenancy and Binding: Tenancy and Binding
- Platform P05 Runtime Definitions
