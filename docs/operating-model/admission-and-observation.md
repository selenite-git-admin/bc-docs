---
id: admission-and-observation
order: 9
title: "Admission and Observation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, sources-and-the-catalog, connectors-and-readers]
governing_sources:
  - Foundation (scope and non-negotiability)
  - Platform P05 Runtime Definitions
  - The Contract Grammar, Admission Contract section
  - The Contract Grammar, Observation Contract section
  - The Evaluation Boundaries, Admission boundary section
governing_adrs:
  - DEC-136a23 (Reader Observation Schema dual-layer)
  - DEC-97bb94 (N:1 SO to CO multi-source canonical evaluation)
  - DEC-771baf (Tenant database architecture and admission-run scope)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-0d5b39 (Reader-definition / Runner-machine split; admission machine verbs are the Runner’s)
  - DEC-02f5a9 (Business Concept Registry supersedes Business Field / Business Object / Canonical Field identity)
errata_referenced:
  - FND-ERR-002
  - FND-ERR-004
v2_sources:
  - system/platform/P05-runtime-definitions/admission-run/index.md
  - system/foundation/contract-schemas/admission-v1.md
  - system/foundation/contract-schemas/observation-v1.md
---

# Admission and Observation

## Scope

This chapter defines the runtime act of admission. It defines how the Admission Contract and Observation Contract are applied by the Runner to records observed from the source, the ordered admission sequence that produces Source Objects together with Evidence and Lineage, the rejection semantics that record outcomes for records the contracts do not admit, the tenant-scoped Admission Run that preserves invocation outcomes, and the boundary clarification that the admission act admits and observes but does not interpret canonical meaning.

Admission is performed by the **Runner** — the admission machine (DEC-0d5b39) that executes the Reader’s governed definition. Throughout this chapter the runtime acts (validate, re-evaluate the source filter, map, compose identity, emit, write the Run) are the Runner’s; the Reader supplies the governed definition the Runner executes, and the admission-boundary rules are unchanged by the naming split. The chapter uses the Business Concept Registry vocabulary (`entity.property`); the former Business Field identity is superseded (DEC-02f5a9).

This chapter does not define the Reader inventory itself; Connector, Reader, Reader Flavor, Reader Binding, Reader Observation Binding, and Connection are defined in Connectors and Readers. This chapter does not redefine the contract grammar (The Contract Grammar), the admission boundary as an execution-model concept (The Evaluation Boundaries), the catalog (Sources and the Catalog), tenant binding generally (Tenancy and Binding), the relational schema (Data Model and Schema), or the API surface for reader operations (API Surface).

**Governing source.** Foundation; The Contract Grammar; The Evaluation Boundaries; Connectors and Readers.

## Admission Contract Application

The Admission Contract governs runtime validation at the admission boundary. The Contract Grammar defines the Admission Contract's responsibility. The exact body fields used by the runtime are governed by the Contract Schemas reference and Platform P05 Runtime Definitions. This section describes application order and effect; it does not redefine the schema.

| Runtime application step | Runtime behavior |
|---|---|
| Structural checks | The Runner evaluates the governed structural validation surface before any field-level or record-level rule execution. Records that fail structural checks do not proceed to later validation steps. |
| Field-level rules | The Runner evaluates governed field rules for each declared field on structurally valid records. |
| Record-level rules | The Runner evaluates governed cross-field rules on records that passed prior steps. |
| Observation-age enforcement | The Runner evaluates the governed freshness rule for records that remain eligible after prior validation. |
| Batch threshold evaluation | The Runner aggregates per-record outcomes and applies the governed batch disposition rule before Source Object emission. |

Validation order is fixed. Structural validation occurs first. Field-level and record-level validation occur only on surviving records. Batch threshold evaluation occurs before Source Object emission so that final batch disposition is known before authoritative objects are created.

The Runner applies the Admission Contract as governed. It does not override default actions, downgrade a blocking rule to a warning at runtime, or introduce undeclared validation logic; the Reader definition it executes carries the governed content unchanged.

**Governing source.** the Admission Contract section of The Contract Grammar; Contract Schemas reference; Platform P05 Runtime Definitions.

## Source-Filter Re-evaluation (row selection)

When the governing Observation Contract declares a `source_filter` (The Contract Grammar; source-filter design v1–v12, TSK-a83188), the Runner re-evaluates the filter **after Admission Contract record validation and before Observation Contract field mapping and Source Object emission**. The connector's pushdown of the same predicate is a derived fetch optimization only; the admission-time re-evaluation is the enforcement authority, so a connector that returns out-of-slice records produces refusals, never admissions.

- A record that fails the filter is a **`source_filter_mismatch`** — a recorded **per-record refusal** through the standard rejection surfaces, not silent exclusion and not run telemetry.
- Evaluation is two-valued: a null or absent field fails every value predicate (`eq`, `ne`, `in`, `not_in`); only `is_set` / `is_not_set` address presence.
- Rejection Evidence and emitted Source Object Lineage carry the **applied coordinates** — the OC, effective AC, and parent SC version pairs of the resolved context plus the normalized filter digest — so every admitted or refused record is traceable to the exact declaration that governed it.

## Observation Contract Application

The Observation Contract governs how validated source data is selected and represented as Source Object content. The Contract Grammar defines the Observation Contract as the governed source of field selection and preserved Source Object shape. The exact runtime body fields are governed by the Contract Schemas reference and Platform P05 Runtime Definitions. This section describes runtime use.

| Runtime application step | Runtime behavior |
|---|---|
| Source-context resolution | The Runner resolves the governed source context required by the Observation Contract and its bound Source Contract. Resolution covers non-semantic context (lookup tables, master-data references) named by the contract; it does not perform business composition across Source Objects. Multi-Source-Object composition is the canonical evaluation boundary's responsibility, governed by DEC-97bb94 and FND-ERR-004. |
| Field mapping | The Runner applies the governed field map from source fields to Business Concept property values (`entity.property`). |
| Identity composition | The Runner applies the governed identity semantics to form Source Object identity for each admitted record. |
| Source Object shape | The emitted Source Object conforms to the governed observation schema. |

The Observation Contract remains the authoritative mapping source. Runtime copies or precomputed forms exist only as derived operational artifacts (per the Reader Flavor dual-layer arrangement defined in Connectors and Readers).

Tenant variation does not modify the governed Observation Contract. Binding-level variation, where permitted elsewhere in the contract model, cannot remove platform-declared mapped fields or alter governed mapping rules.

### Reader Observation Schema Dual-Layer

The `FND-ERR-002` entry records the dual-layer mapping arrangement governed by DEC-136a23.

| Layer | Location | Authority | Purpose |
|---|---|---|---|
| Governed mapping | Observation Contract | Authoritative | Versioned, immutable mapping and shape definition |
| Runtime copy | Reader Flavor derived configuration | Derived | Precomputed form used by the Runner during admission |

The runtime copy is generated from the governed Observation Contract. It is not independently edited. Reactivation or regeneration replaces the derived copy from the governed source.

**Governing source.** the Observation Contract section of The Contract Grammar; DEC-136a23; FND-ERR-002; Connectors and Readers; Contract Schemas reference; Platform P05 Runtime Definitions.

## Admission Sequence

Each admission invocation — the Runner executing a Reader against its governed bindings — executes a fixed admission sequence. The sequence is ordered and non-skippable.

| Step | Action | Governing authority |
|---|---|---|
| 1 | The Connector reaches the source system and returns observed records | Connectors and Readers |
| 2 | The Runner applies Admission Contract structural checks | Admission Contract |
| 3 | The Runner applies Admission Contract field-level, record-level, and observation-age validation | Admission Contract |
| 4 | The Runner re-evaluates the governing Observation Contract `source_filter` (the authoritative enforcement, after AC validation and before OC mapping); a record outside the slice is a `source_filter_mismatch` — an Evidence-only per-record refusal (no Source Object, no Lineage). Connector pushdown of the same predicate is a derived fetch optimization only | Observation Contract; source-filter design v1–v12 |
| 5 | The Runner applies Observation Contract mapping and identity composition to records that remain eligible for admission | Observation Contract |
| 6 | The Runner computes batch-level outcome thresholds and final batch disposition | Admission Contract |
| 7 | The Runner emits Source Objects for records whose final disposition permits admission, and emits per-record Evidence and per-object Lineage — Lineage only for emitted Source Objects (refused records emit Evidence only, FND-1) | The Object Model and The Evaluation Boundaries |
| 8 | The Runner writes the tenant-scoped Admission Run with outcome counts, applied governed versions, and run-level references | DEC-771baf; DEC-f02230; Data Model and Schema |

Two consequences follow from this sequence.

1. A record that fails structural or rule validation does not produce a Source Object.
2. A batch-level rejection occurs before Source Object emission. The runtime does not revoke already-emitted Source Objects.

**Governing source.** The Object Model; The Evaluation Boundaries; Connectors and Readers.

## Rejection Semantics

Rejection at admission is a recorded outcome, not the absence of a trace. Rejected observations emit **Evidence only — never Lineage** (Lineage is emitted per emitted Source Object; a record that was not admitted has no Source Object and receives no Lineage, FND-1). Rejected observations contribute to run totals. Source Object emission depends on final per-record and batch-level disposition.

| Outcome | Source Object emitted | Evidence emitted | Run effect |
|---|---|---|---|
| `admitted` | Yes | Yes | Counted toward admitted total |
| `quarantine` | No | Yes | Counted toward quarantine total |
| `warn` | Yes | Yes | Counted toward warn total |
| `log` | Yes | Yes | Counted toward log total |
| `block` | No | Yes | Counted toward blocked total |

Batch-level threshold handling does not retract previously emitted objects because threshold evaluation precedes emission. When the governed batch disposition is equivalent to rejecting the batch, the run preserves Evidence for the batch outcome and no Source Objects are emitted for records withheld by that final disposition.

**Governing source.** The Object Model; The Evaluation Boundaries.

## Evidence and Lineage at Admission

Admission emits proof at the same boundary act that produces Source Objects. Proof is not deferred.

| Proof artifact | Scope at admission | Purpose |
|---|---|---|
| Evidence | Per observed record and per relevant batch outcome | Records validation outcome, boundary context, and disposition |
| Lineage | Per emitted Source Object | Records direct references from the emitted Source Object to the governed contract versions and direct admission context used at admission |

Run-level operational references may exist for diagnostics or reporting, but they do not replace per-object Lineage for admitted Source Objects.

**Governing source.** The Object Model; The Evaluation Boundaries; Evidence and Lineage.

## Admission Run

Admission Run is the tenant-scoped execution record for one admission invocation (the Runner executing a Reader) at the admission boundary.

| Property | Value |
|---|---|
| Scope | Tenant |
| Store class | Tenant admission-run store in the progression-oriented tenant execution layer |
| Initiated by | Admission invocation against a governed Reader Binding |
| Records | Reader reference, Flavor reference, governed contract versions applied, per-record outcome counts, batch disposition, and run-level references to emitted proof |
| Lifecycle | Queued or running state followed by a terminal outcome state |
| Retention | Append-only operational history |

DEC-771baf governs tenant ownership of execution data. DEC-f02230 and its active tenant-schema amendments govern where tenant execution records live structurally. This chapter therefore defines the Admission Run semantically and operationally; Data Model and Schema defines exact schema and table names.

The Admission Run is an operational record. It is authoritative for run accounting and invocation history. It does not replace Source Objects, Evidence, or Lineage as the authoritative outcome of admission.

**Governing source.** DEC-771baf; DEC-f02230; The Authority Model.

## Reader Does Not Interpret

Admission — the Runner executing a Reader — admits and observes. It does not resolve business meaning. Canonical interpretation begins only at the canonical evaluation boundary.

| Admission does | Admission does not |
|---|---|
| Apply Admission Contract validation | Apply Canonical Contract resolution |
| Apply Observation Contract field selection and identity rules | Reconcile cross-source business meaning |
| Emit Source Objects | Emit Canonical Objects |
| Emit Evidence and Lineage for admission | Modify Source Objects after emission |
| Write Admission Run | Rewrite governed contract content at runtime |

An admission act (a Runner executing a Reader) that performs canonical resolution is incorrect under the execution model.

**Governing source.** The Object Model; The Evaluation Boundaries; Canonical Evaluation.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Evaluation Boundaries: The Evaluation Boundaries
- The Authority Model: The Authority Model
- Sources and the Catalog: Sources and the Catalog
- Connectors and Readers: Connectors and Readers
- Canonical Evaluation: Canonical Evaluation
- Evidence and Lineage: Evidence and Lineage
- Tenancy and Binding: Tenancy and Binding
- Platform P05 Runtime Definitions
