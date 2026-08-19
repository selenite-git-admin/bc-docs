---
id: the-runtime-ecosystem
order: 8.9
title: "The Runtime Ecosystem"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-evaluation-boundaries, the-object-model, the-contract-grammar, connectors-and-readers, business-vocabulary]
governing_sources:
  - Foundation (scope and non-negotiability)
  - Platform P05 Runtime Definitions
governing_adrs:
  - DEC-0d5b39 (The Reader Model and the Runtime Ecosystem)
  - DEC-01bd6b (Runtime Orchestration)
---

# The Runtime Ecosystem

## Scope

This chapter is the **cross-cutting map** of the platform's execution layer and the **machine-versus-artifact taxonomy** that layer uses. It names the runtime **machines** — the Runner and the Evaluator umbrella (the Canonical, Metric, and Action Evaluators) — and the **artifacts** they operate through (Connector, Connection, Reader and its Flavors), executing over the Contract chain.

This chapter is a navigational map and taxonomy only. It **inherits, and does not restate,** the six invariants (The Invariants), the four evaluation boundaries and their boundary-independent rules (The Evaluation Boundaries), and the object set (The Object Model). It **delegates** all normative behavior to its owning chapters: adapter artifacts to Connectors and Readers; admission behavior to Admission and Observation; canonical, metric, and action acts to their evaluation chapters; and orchestration to the Runtime Orchestration ADR (DEC-01bd6b). It does not govern any claim those chapters own. The Operating Model entry point remains Operating Model Overview; this chapter is not a second entry point.

**Governing source.** Foundation; DEC-0d5b39; DEC-01bd6b; Platform P05 Runtime Definitions.

## The two tracks

The platform is two chains, decoupled by design and coupled only at execution:

- The **source track** — Connection, Connector, Source Contract, Admission Contract. Its grain is the source (systems, source entities, source versions).
- The **business track** — Observation Contract, Canonical Contract, Metric Contract, Intervention Contract, and the storage projection of the authoritative objects. Its grain is business meaning.

The runtime ecosystem is where the two tracks execute. It is bounded **above** by authoring and governance (which mints the definitions and contracts it executes, including the Business Concept Registry entities) and **below** by consumption (which reads the facts, metrics, and action objects it produces).

## Machines versus artifacts

The core distinction this chapter owns is between the **definitions** (governed artifacts) and the **machines** (engines that execute them).

**Artifacts (definitions).** The Connector (protocol capability), the Connection (the tenant-owned access record for a source instance), and the Reader (anchored to one Business Concept Registry Entity) with its per-source Flavors and per-entity Admission- and Observation-Contract bindings. Their governance is owned by Connectors and Readers; this chapter only places them on the map.

**Machines (engines).**

- The **Runner** — the admission engine. It drives Readers: it resolves the governing chain once before any fetch, reaches the source through the Connector and Connection, admits records under the Admission and Observation Contracts, and emits Source Objects with their Evidence, Lineage, and Admission Run. The Reader is the Runner's governed *definition*; the Runner is the *machine*. This Reader/Runner naming split is introduced by DEC-0d5b39 as net-new modeling; Foundation attributes the admission act to the Reader, and the split does not change any admission-boundary rule.
- The **Evaluator (umbrella)** — an umbrella term for three distinct boundary machines the platform already names: the **Canonical Evaluator**, the **Metric Evaluator**, and the **Action Evaluator**. Each is an independently invoked Foundation boundary act with its own contract, inputs, gates, synchronous Evidence and Lineage, and Run record. One act produces exactly one progression-object version. Shared code or deployment must not merge boundaries; the umbrella is a naming convenience, never a collapse of the four-boundary model.

## The four-boundary spine and the derivation DAG (map level)

The runtime executes the full four-boundary spine: **Admission** (Source Contract / Admission Contract / Observation Contract → Source Object) → **Canonical** (Canonical Contract → Canonical Object) → **Metric** (Metric Contract → Metric Snapshot) → **Action** (Intervention Contract → Action Object). Metric Snapshots and Action Objects are authoritative progression objects, not consumption.

**Secondary Metric Snapshots** (a Metric Snapshot whose Lineage references other Metric Snapshots) form a **descriptive** directed acyclic graph of metric dependencies. The graph is descriptive only: traversal reads preserved Lineage and never triggers recomputation; a changed upstream yields a new forward evaluation act, never an in-place recompute. A secondary act selects fixed upstream Snapshot versions and records them in its Lineage; the Metric Evaluator does not implicitly invoke upstream acts. The detailed grammar is owned by the secondary-metric governance (DEC-0f3e57) and the Object Model. There is no secondary Canonical Object: the Canonical boundary input is Source-Objects-only.

## Orchestration (pointer)

Two axis-orchestrators drive the machines, loosely coupled by preserved progression data rather than control: the **Admission Orchestrator** on the source axis (source cycles that coordinate N Admission Runs) and the **Evaluation Orchestrator** on the metric/group/sub-function axis (governed, version-pinned, command-triggered evaluation). Reads never trigger evaluation. The Reader is the orchestration unit for neither. The full model — pull and push admission, governed selection, trigger discipline, and Action invocation — is owned by the Runtime Orchestration ADR (DEC-01bd6b).

## Scope seam: platform definitions, tenant execution

Definitions — Connector, Reader, Reader Flavor, and the platform Reader Bindings — are **platform-scoped**. **Connection configuration is platform-held** (in the platform registry), **tenant-owned** through the tenant identity, with **credentials external** (the secret-management surface), per DEC-81cd26 and DEC-ecd55c. Execution artifacts — Admission Runs, the progression objects, Evidence, and Lineage — are **tenant-scoped**. Platform Reader Bindings (which contract versions a reader applies) are distinct from tenant Contract Bindings (which contracts a tenant uses).

`fact.*` tables are a **storage projection** of the four progression-object classes (for example, `fact.ms_*` projects Metric Snapshots); they are not a fifth authoritative object class. The authoritative objects are the Source Object, Canonical Object, Metric Snapshot, and Action Object, with their Evidence and Lineage.

## Program backlog (non-authoritative)

Open implementation and reconciliation work for the runtime ecosystem is tracked in a **non-authoritative, revisioned program-control ledger** maintained outside this documentation. That ledger records and sequences work; it holds no doctrine, and this pointer does not delegate authority to it.

## References

- The Invariants; The Evaluation Boundaries; The Object Model; The Contract Grammar (inherited by citation).
- Operating Model Overview; Connectors and Readers; Admission and Observation; Canonical Evaluation; Metric Evaluation; Action Evaluation (owning chapters for the delegated behavior).
- DEC-0d5b39 (The Reader Model and the Runtime Ecosystem); DEC-01bd6b (Runtime Orchestration).
