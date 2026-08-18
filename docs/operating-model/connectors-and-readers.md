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
  - DEC-0d5b39 (Reader anchored to one Registry Entity; source-agnostic; Reader-definition / Runner-machine split; Connection authority)
  - DEC-81cd26 (Connection configuration platform-held; reverses D163)
  - DEC-ecd55c (Connection tenant ownership; credentials in external secret-management surface)
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

This chapter defines the Reader as a **governed definition**, not as a runtime machine. Per DEC-0d5b39 the machine that executes a Reader is the **Runner** (the admission machine named in The Runtime Ecosystem); the Reader supplies the governed definition and per-source specialization the Runner executes. This chapter does not define the runtime act of admission, the application of Admission Contract or Observation Contract per record, the Source Object emission sequence, or the tenant-scoped Admission Run — those belong to Admission and Observation. It does not define source-system structure (Sources and the Catalog) or tenant binding more broadly (Tenancy and Binding); it defines only the Connection artifact specifically.

**Governing source.** Foundation; The Contract Grammar; Sources and the Catalog; DEC-0d5b39.

## Adapter Inventory

The platform recognizes six adapter artifacts. Five are platform-scoped and governed centrally; the Connection is platform-held in configuration and tenant-owned in authority, with credentials held externally.

| Adapter | Role | Scope | Persistent store |
|---|---|---|---|
| Connector | Technical capability to reach a source system over a declared protocol | Platform | `runtime.connector` and supporting protocol tables |
| Reader | Registry-Entity-anchored admission **definition** implementing the UniBAT pattern; executed by the Runner | Platform | `runtime.reader` |
| Reader Flavor | Reader variant bound to one Connector and one source-system version context; Observation Contracts bind per source entity (see Reader Observation Binding) | Platform | `runtime.reader_flavor` |
| Reader Binding | Platform-governed **Admission-Contract binding** for an execution context — despite its historical column name, `reader_binding.source_contract_id` carries an **admission-contract id**; the pair `(source_contract_id, version_code)` is the effective AC version pin (substrate fact, source-filter design v4) | Platform | `runtime.reader_binding` |
| Reader Observation Binding | Platform-governed **Observation-Contract pin** per `(reader, flavor, environment, source entity)` — the declaration a given admission run executes under | Platform | `runtime.reader_observation_binding` |
| Connection | Access record for a Reader Flavor; **configuration platform-held** in `runtime.connection`, **tenant-owned** by tenant identity, **credentials external** (secret reference only on the record) | Platform-held config, tenant-owned | Platform `runtime.connection` + external secret store |

Connector, Reader, Reader Flavor, and both bindings are governed centrally and reused across tenants. The Connection's configuration is platform-held in `runtime.connection` (DEC-81cd26, reversing D163) and tenant-owned through the tenant identity; it carries only a credential reference, and the credentials themselves live in the external secret-management surface (DEC-ecd55c). No platform-side artifact carries tenant credentials.

**Binding resolution (source-filter design v5–v12, TSK-a83188).** An admission run resolves its governing chain **once, before any fetch**, from the exact context `(reader, flavor, environment, source entity)`: the Observation binding is the four-way exact row (exactly one, active); the **effective Admission Contract** is selected flavor-specific first, with a reader-level (`flavor_id IS NULL`) row as the only fallback, exactly one at the winning level; the Observation Contract's AC pair must equal the effective AC pair, and its SC pair must equal the effective AC version's declared parent pair. Any missing, ambiguous, inactive, or mismatched coordinate is a **chain-integrity refusal of the whole invocation** — there is no table-name fallback, no first-match selection, and no scenario/configuration substitute. The resolved context (all pairs, the winning level, and the normalized filter digest) travels with the run into Evidence and Lineage.

**Governing source.** Platform P05 Runtime Definitions; DEC-0d5b39; DEC-81cd26; DEC-ecd55c.

## Connector

**Purpose.** A Connector declares the technical capability to reach a source system over a defined protocol.

**Scope.** A Connector covers protocol family, supported authentication methods, capability metadata, and provenance describing how the connector definition was authored or curated. It does not cover source-system structure, Business Field selection, validation rules, or business meaning.

**Behavior.** A Connector is registered with a connector code, protocol family, authentication-method support, capability flags, and provenance. The Runner invokes a Connector to obtain a transport channel to a source system; the Connector returns observed records as raw protocol-shaped payload. The Reader Flavor names the Connector that a given admission act uses.

**Constraints.**

- A Connector provides reachability only.
- A Connector does not declare Admission Contract rules.
- A Connector does not declare Observation Contract mappings.
- A Connector does not define identity semantics for admitted records.
- A Connector carries no tenant credentials; the Connection supplies a resolved credential to the Connector at invocation, and the credential itself is held in the external secret store.

**Failure modes.**

- If an endpoint is unreachable, the Connector returns a transport error and the invocation terminates without producing Source Objects.
- If authentication fails, the Connector returns an authentication error and the invocation terminates; failure is recorded on the Admission Run.
- If a protocol error occurs (malformed response, version mismatch), the Connector returns the error and the invocation terminates; failure is recorded on the Admission Run.
- Connector failures are recorded as operational Evidence per the rejection semantics defined in Admission and Observation.

**Interactions.** The Connector is invoked by the Runner at admission time, using the Connector named by the Reader Flavor. The Connection resolves the credential the Runner supplies to the Connector at invocation.

**Governing source.** Platform P05 Runtime Definitions, Connector dossier; The Contract Grammar.

## Reader

**Purpose.** A Reader is the platform's governed **admission definition** for one Business Concept Registry Entity, implementing the UniBAT pattern (Universal Business-Aware Transactions Reader). It is the definition the **Runner** (the admission machine) executes; the Reader does not itself perform runtime work.

**Scope.** A Reader defines the admission for one Business Concept Registry Entity: which Connector reaches the source, which Admission and Observation Contracts govern validation, mapping, and identity, and the specialization (through its Flavors) the Runner applies. The runtime act sequence — Source Object emission, Evidence and Lineage, the Admission Run — is performed by the Runner and defined in Admission and Observation. A Reader defines nothing beyond the Source Object boundary: not canonical evaluation, metric evaluation, or action evaluation.

**Behavior.** A Reader is registered with a reader code, the Business Concept Registry Entity it admits (`admitted_entity_id`), and references to the Connector and contract artifacts that govern it. At invocation the **Runner** executes the Reader's definition per the act sequence in Admission and Observation: it obtains records via the Connector, applies the governed Admission Contract for validation, applies the governed Observation Contract (pinned per source entity through the Reader Observation Binding) for mapping and identity composition, emits a Source Object with per-record Evidence and per-object Lineage for each admitted transaction, records Evidence only for refused records (no Lineage is assigned to a record that was not admitted), and writes the tenant-scoped Admission Run. Where Foundation attributes an admission act to "the Reader," it names this Reader-governed act the Runner performs; the naming split (DEC-0d5b39) changes no admission-boundary rule.

**Constraints.**

- A Reader admits one Business Concept Registry Entity — one non-archived Reader per Entity (DEC-0d5b39). A second Entity requires a second Reader. A Reader carries no source system; source specialization lives in its per-source Flavors, and `function_code`/`subfunction_code` are non-identity classification.
- A Reader's definition does not admit fields not declared by the governed Observation Contract.
- A Reader does not define Canonical Contract logic.
- A Reader definition, once executed, does not modify previously emitted Source Objects.
- A Reader carries governed contract content as-is. The Runner does not downgrade a blocking validation rule to a warning at runtime, override default actions, or introduce undeclared validation logic.

**Failure modes.**

- If the governed Observation Contract is missing or unresolved at invocation, the Runner records the unavailability on the Admission Run and admission is paused.
- If the Reader's referenced contract artifacts have inconsistent versions (for example, a Reader Binding pointing at an Admission Contract version whose parent Source Contract the Observation Contract does not bind to), the Runner rejects the invocation before record processing.
- If a Reader is executed outside a governed Reader Binding, the Runner rejects the invocation; ad-hoc admission is not admissible.

**Interactions.** A Reader is bound to one or more Reader Flavors that specialize it for specific source-system contexts. At admission, the Runner executes the Reader against a Reader Binding that names the effective Admission Contract version and the execution context, with the Observation Contract pinned per source entity through the Reader Observation Binding. The outputs (Source Objects, Evidence, Lineage, Admission Run) are consumed by the canonical evaluation boundary and by tenant-side reporting.

**Governing source.** Platform P05 Runtime Definitions, Reader dossier; DEC-0d5b39; The Contract Grammar; The Evaluation Boundaries.

## The UniBAT Pattern

The Reader is the platform's central architectural innovation. The acronym names what the pattern asserts: Universal Business-Aware Transactions Reader. Each term carries a structural commitment. The pattern governs the admission the Runner performs; where the terms below say "the Reader admits," they name the Reader-governed act the Runner executes.

**Universal.** A single Reader pattern covers any source system. The pattern does not specialize per database vendor, per file format, or per protocol. Specialization happens in the Connector (protocol) and the Reader Flavor (source-system version), not in the Reader definition itself. The Reader's governed responsibilities, sequence, and failure modes are the same regardless of whether the source is an ECC landscape, an OData endpoint, a REST API, a CSV file, or a database table.

**Business-Aware.** The admission act emits Source Objects whose payload is keyed by Business Field codes, not by source-system field names. The translation from source field paths to Business Field codes happens at the act of admission under the governed Observation Contract. The platform's subsequent layers (Canonical Evaluation, Metric Evaluation, Action Evaluation) read Business-Aware payload, not source-shaped payload. The source system's schema, naming, or representation choices do not bleed into the platform's authoritative state.

**Transactions.** Admission handles one transaction at a time. A transaction is a record that the source system identifies as one business event (an invoice, a journal entry, an inventory movement). Each admitted transaction becomes one Source Object. The act does not bundle multiple transactions into one object, and it does not split one transaction across multiple objects. The transaction is the admission unit.

**Reader.** The Reader defines admission of state. It does not define derivation of new values or aggregates. The platform separates admission from canonical evaluation deliberately: admission preserves what the source system declared; canonical evaluation applies the governed Canonical Contract to derive business meaning. A Reader definition (or a Runner executing it) that performs canonical resolution is incorrect under the execution model.

The UniBAT pattern differs structurally from conventional ETL connectors and data integration platforms. ETL connectors couple to source schema and rewrite records as part of the integration path; consuming layers read the rewritten shape. The UniBAT Reader admits records under an Admission Contract that validates them and an Observation Contract that translates source paths to Business Field codes; the platform's subsequent layers read the Business-Aware shape directly. Data integration platforms typically use schema-on-read with implicit semantics; the UniBAT Reader uses schema-on-write under explicit governed contracts.

The pattern's three structural consequences:

| Consequence | Effect |
|---|---|
| Source-system portability | Migrating a source system replaces the Connector and adds or replaces a Reader Flavor; the Source Contract, Observation Contract, and Canonical Contract continue to apply unchanged because the Business-Aware identifiers persist |
| No transformation step | The platform does not maintain a separate transformation layer between source observation and canonical evaluation; the Observation Contract carries the binding rules and the governed Canonical Contract carries the canonical resolution |
| Audit traceability | Every Business Field value on a Source Object is traceable to a source field path through the governed Observation Contract version pinned, per source entity, by the Reader Observation Binding at admission time |

**Constraints.**

- Admission produces one transaction per Source Object.
- Admission does not bundle, split, or alter transactions.
- Source Objects are keyed by Business Field codes, not by source-system field names.
- A Reader definition, or a Runner executing it, that violates any of the four UniBAT terms is incorrect under the execution model.

**Failure modes.**

- If admission modifies record shape, later chapters describe the boundary error: the Source Object payload does not match the governed Observation Contract output and the Canonical Contract cannot resolve it.
- If admission bundles multiple transactions into one Source Object, the cardinality at the canonical boundary becomes incorrect and metric grain alignment fails.
- If admission emits Source Objects with source-shaped keys, subsequent Canonical Contract resolution fails and Canonical Object emission is rejected.

**Governing source.** The Contract Grammar; The Evaluation Boundaries; Business Vocabulary; DEC-0d5b39.

## Reader Flavor

**Purpose.** A Reader Flavor binds one Reader to one Connector and one source-system version context, and carries the per-source-entity Observation Contract pins (through the Reader Observation Binding) that produce the runtime-ready specialization the Runner invokes.

**Scope.** A Reader Flavor covers the source-system version it admits, the Connector that reaches that version, the per-source-entity Observation Contract bindings that map to Business Fields for that version, and the derived runtime configuration the Runner applies during admission. It does not cover tenant credentials (those resolve through the Connection from the external secret store) or the effective Admission Contract version (that is named by the Reader Binding).

**Behavior.** A Reader Flavor is registered with a flavor code, a Reader reference, a Connector reference, and a source-system version reference; its Observation Contract pins are held per source entity in the Reader Observation Binding. The platform may pre-compute a derived runtime configuration from the governed Observation Contract for a given source entity; that configuration is the Reader Flavor's runtime copy for that entity and is regenerated from the governed source when the pinned Observation Contract version changes.

**Constraints.**

- A Reader Flavor binds to exactly one Reader.
- A Reader Flavor binds to exactly one Connector.
- A Reader Flavor binds Observation Contracts **per source entity** via `reader_observation_binding`; one Flavor observes many entities, each under its own Observation Contract pin. This amends the former one-Observation-Contract-per-Flavor reading of DEC-1edaaa (see DEC-0d5b39 and DEC-17112b). No single Observation Contract is identified directly on the Flavor.
- A Reader Flavor's runtime copy is derived from the governed Observation Contract and is not independently edited.
- A Reader Flavor does not declare validation rules or canonical translations independently of its bound contracts.

**Failure modes.**

- If a Flavor's pinned Observation Contract version (for a source entity) is superseded, the Reader Observation Binding continues to reference the named version. Adopting the superseding version requires a tracked authoring act on the binding. The Runner does not silently re-bind to a superseding version (Invariant IV).
- If a Reader Flavor's bound Connector becomes unavailable at invocation, the admission act records the unavailability and pauses pending Connector availability.
- If a Reader Flavor's runtime copy diverges from the governed Observation Contract (for example, due to manual edit of the runtime copy), the divergence is detected at admission-act validation and the runtime copy is regenerated from the governed source.

**Interactions.** A Reader Flavor is the runtime-ready specialization the Runner selects (through a Reader Binding) at admission. The Connection resolves the credential the Runner supplies to the Flavor's Connector at invocation. The dual-layer arrangement governed by DEC-136a23 and recorded as FND-ERR-002 holds at the Flavor's runtime copy: the governed Observation Contract is the single source of truth; the Flavor's runtime copy is a derived operational artifact.

**Governing source.** DEC-136a23; DEC-1edaaa; DEC-0d5b39; Platform P05 Runtime Definitions; The Contract Grammar.

## Reader Binding

**Purpose.** A Reader Binding records which governed contract versions the Runner applies for a specific admission invocation context, naming the Reader Flavor, the effective Admission Contract version, and the execution context.

**Scope.** A Reader Binding covers the platform-governed runtime binding from a Reader Flavor to one effective Admission Contract version and one execution context. It does not cover tenant-side configuration; tenant-side variation lives on the Connection or on Contract Bindings, both described in Tenancy and Binding.

**Behavior.** A Reader Binding is registered with a binding code, a Reader Flavor reference, an effective Admission Contract version reference (carried, for historical reasons, in `source_contract_id` — see the inventory note), and an execution context (the schedule, mode, and run parameters that govern when admission acts run). The Runner invokes admission against a Reader Binding; the Binding identifies which governed contract versions are applied.

**Constraints.**

- A Reader Binding references exactly one Reader Flavor.
- A Reader Binding references exactly one effective Admission Contract version.
- A Reader Binding does not rewrite governed contract content; it records which versions are applied.
- A Reader Binding is platform-governed. Tenant-specific access configuration (credential reference, environment URLs, rotation windows) is not on the Reader Binding; it is on the Connection.

**Failure modes.**

- If the Admission Contract version named by the Reader Binding is superseded, the Binding continues to reference the named version. The Runner applies the named (superseded) version unless the binding is governance-updated to reference the superseding version. The Runner does not silently route invocations to a superseding version (Invariant IV).
- If the Flavor's pinned Observation Contract (for the source entity) does not satisfy the AC/SC pair equalities named in Binding Resolution, the Runner rejects the invocation; the inconsistency is recorded as a chain-integrity failure.
- If the execution context is invalid at invocation time (for example, the schedule has lapsed without a current window), the Runner records the lapse and the invocation is held until a valid context exists.

**Interactions.** A Reader Binding is the artifact that admission invocations name. At invocation, the Binding identifies the Reader Flavor, which identifies the Connector; the Observation Contract version is pinned per source entity through the Reader Observation Binding; the Binding adds the effective Admission Contract version and the execution context; the Connection resolves the credential. Together, these references define one fully bound admission act.

**Governing source.** Platform P05 Runtime Definitions; The Contract Grammar; Contract Chain Assembly.

## Connection

**Purpose.** A Connection is the access record for a Reader Flavor — **configuration platform-held** in `runtime.connection`, **tenant-owned** through the tenant identity, with **credentials external** in the secret-management surface (only a credential reference is on the record) — that authorizes a Reader Flavor's Connector to reach a tenant-owned source system.

**Scope.** A Connection covers the credential reference, environment-specific access URLs or hostnames, rotation windows, and per-tenant access constraints (rate limits, allowed time windows). It does not cover the platform-side Connector definition (that is the Connector artifact), the Reader Flavor binding (that is the Reader Flavor artifact), or any contract content. It never holds credential material.

**Behavior.** A Connection is registered with a connection code, the Reader Flavor it authorizes, the tenant identity that owns it, a credential reference (the credentials themselves are held in the platform's external secret-management surface, never on the Connection record), and the per-tenant access configuration. At admission invocation, the Runner resolves the Connection for the invoking tenant and Reader Flavor, resolves the credential reference against the external secret store, and supplies the resolved credential to the Connector.

**Constraints.**

- A Connection's configuration is platform-held in `runtime.connection` (DEC-81cd26, reversing D163) and tenant-owned by tenant identity; credentials are external in the secret-management surface (DEC-ecd55c). Platform-side artifacts (Connector, Reader, Flavor, Binding) do not carry tenant credentials, and neither does the Connection record — it carries only a reference.
- A Connection authorizes one Reader Flavor against one tenant-owned source system. Multi-Flavor or multi-tenant credential bundles are separate Connections.
- A Connection does not declare validation rules, mapping rules, or contract content. It declares access only.
- A Connection's credential material is not preserved on the Connection record; only a credential reference is recorded.

**Failure modes.**

- If a Connection's credential reference resolves to expired credentials, Connector authentication fails at invocation; failure is recorded on the Admission Run and the tenant is notified through the platform's tenant-facing channels (defined in Tenancy and Binding).
- If a Connection is missing for the invoking tenant and Reader Flavor, the Runner rejects the invocation; admission cannot proceed without a Connection.
- If a Connection's per-tenant access configuration would block invocation (rate limit exceeded, outside allowed window), the Runner records the block and the invocation is held until the configuration permits proceeding.

**Interactions.** The Connection participates at admission invocation, resolving the credential reference against the external secret store and supplying the resolved credential to the Connector through the Runner. Connection lifecycle (creation, rotation, retirement) is part of tenant onboarding and ongoing tenant-side governance, described in Tenancy and Binding. The external secret store itself is described in Security Operations.

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
