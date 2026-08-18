---
id: metric-evaluation
order: 11
title: "Metric Evaluation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, canonical-evaluation]
governing_sources:
  - Platform P02 Contract Registry (Metric Contract dossier)
  - The Contract Grammar, Metric Contract section
  - The Evaluation Boundaries, Metric evaluation boundary section
governing_adrs:
  - DEC-29c324 (N:1 Metric Contract to Canonical Contract cardinality)
  - DEC-771baf (Tenant database architecture and run scope)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-0d5b39 (Evaluator umbrella — Canonical/Metric/Action Evaluators as distinct boundary acts; Runner/Evaluator machine split)
  - DEC-0f3e57 (Secondary metrics — metric-over-metric-snapshot descriptive DAG; composite runtime)
  - DEC-483f1e (The General Metric Runtime — substrate-driven, shape-dispatch; later expansion)
errata_referenced:
  - FND-ERR-003
v2_sources:
  - system/platform/P02-contract-registry/metric-contract/index.md
  - system/platform/P02-contract-registry/metric-contract/01-specification.md
  - system/foundation/contract-schemas/metric-v1.md
---

# Metric Evaluation

## Scope

This chapter defines the runtime components and execution behavior at the metric evaluation boundary under the current Foundation execution model. It describes the Metric Evaluator and the tenant-scoped Metric Evaluation Run; defines how the Metric Contract is applied at runtime; defines how the Metric Contract's `metric_binding` is interpreted at runtime; defines deterministic formula application over Canonical Field values; defines the readiness gate and threshold classification at the level authorized by the current contract grammar; defines the evaluation sequence that produces one Metric Snapshot together with Evidence and Lineage; and defines the tenant-scoped run record that preserves invocation outcomes. It distinguishes contract authority from runtime application so that governed contract shape and operational behavior are not conflated. It does not redefine the contract grammar (The Contract Grammar), the metric evaluation boundary as an execution-model concept (The Evaluation Boundaries), the canonical evaluation components that produce Canonical Objects (Canonical Evaluation), tenant-scoped binding records (Tenancy and Binding), the full relational schema (Data Model and Schema), or the API surface for evaluator operations (API Surface).

The **Metric Evaluator** is one of the three boundary machines under the Evaluator umbrella (Canonical, Metric, Action — DEC-0d5b39); each is an independently invoked Foundation boundary act, and the umbrella is a naming convenience that never collapses the boundaries. A primary metric evaluation act consumes one or more Canonical Object versions and emits one Metric Snapshot. A **secondary** metric evaluation act — a Metric Snapshot whose Lineage references other Metric Snapshots — is a **descriptive** directed acyclic graph (DEC-0f3e57) and already has an **operative composite computation and progression/fact-persistence path** (the composite evaluator; `progression.metric_evaluation` + the `fact.ms_*` projection). It is **not** a deferred runtime — but it is **not yet proof-complete**: it emits no governed Lineage, and its upstream references are latest-accepted values plus Metric Contract UIDs rather than exact Metric Snapshot identities (the E6 / FND-R2-1 gap). See Secondary metric evaluation. Broader shape-dispatch expansion is governed by DEC-483f1e.

## Runtime inventory

Metric evaluation uses one platform-scoped runtime component and one tenant-scoped execution record.

| Component | Role | Scope | Persistent store |
|---|---|---|---|
| Metric Evaluator | Platform runtime that applies one Metric Contract version to one evaluation target and produces one Metric Snapshot | Platform | Platform-scoped service definition |
| Metric Evaluation Run | Per-invocation tenant execution record for one metric evaluation act | Tenant | Tenant metric-run store defined by current tenant-schema ADRs and Data Model and Schema |

The Metric Evaluator is governed centrally and reused across tenants. Metric Evaluation Run is tenant-scoped under DEC-771baf. Under the current Foundation model, one evaluator invocation corresponds to one evaluation act for one resolved target and therefore to at most one emitted Metric Snapshot.

## Metric Evaluator

**Purpose.** The Metric Evaluator is the platform runtime component that applies one Metric Contract version to one evaluation target to produce one Metric Snapshot together with its Evidence and Lineage.

**Behavior.** At invocation, the Evaluator resolves the Metric Contract referenced by its evaluation target, interprets the Contract's `metric_binding` to determine the referenced Canonical Contract versions and Canonical Field names the formula consumes, evaluates whether the declared temporal gate is satisfied, gathers the Canonical Object versions required by the binding, applies the formula deterministically over the gathered Canonical Field values, classifies the result against the governed thresholds, emits the act's Metric Snapshots, and writes Evidence, per-evaluation-act Lineage (per DEC-ebb3cd D-2), and the Metric Evaluation Run at the same act.

**Constraints.**
- The Evaluator does not read Source Objects directly.
- The Evaluator does not modify a previously emitted Metric Snapshot.
- The Evaluator does not produce metric values outside the metric evaluation boundary.
- The Evaluator does not treat read-time or dashboard computation as authoritative metric evaluation.
- Secondary metric-chain execution is performed by the composite evaluator (see Secondary metric evaluation), a distinct act from this primary single-target path; the two are never collapsed.

**Failure modes.** Evaluator failures decompose into gate failures, input-resolution failures, formula-evaluation failures, and classification failures. A gate failure records a terminal gated outcome on the Run and emits no Metric Snapshot. An input-resolution or formula-evaluation failure records a terminal failed outcome on the Run and emits no Metric Snapshot. A classification failure records a terminal failed outcome on the Run and emits no Metric Snapshot when the governed threshold structure cannot be applied to the computed result.

**Governing source.** P02 Metric Contract dossier; the Metric evaluation boundary section of The Evaluation Boundaries.

## Metric Contract application

The Metric Contract referenced by an evaluation target governs metric evaluation at runtime. the Metric Contract section of The Contract Grammar defines the responsibility of the Metric Contract and names the body elements it declares: identity, formula expression, referenced Canonical Contract versions through `metric_binding`, grain alignment, required parameters, evaluation timing, result shape and units, and admissible comparison operations. The exact body schema lives in the Contract Schemas reference and the P02 Metric Contract dossier. This section describes runtime application order and effect. It does not redefine the schema.

| Runtime application step | Runtime behavior |
|---|---|
| Metric identity resolution | The Evaluator resolves the Metric Contract identity and confirms that the Contract version is active. |
| Gate application | The Evaluator applies the declared temporal gate to determine whether the evaluation act is eligible to proceed for the current target and period. Gate behavior is described in the Temporal gate and readiness section. |
| Binding interpretation | The Evaluator interprets `metric_binding` to identify the referenced Canonical Contract versions and the Canonical Field names the formula consumes from each. |
| Grain alignment | The Evaluator applies the Contract's declared grain to determine the identity of the Metric Snapshot being produced. Any aggregation required to align contributing Canonical Object versions to that grain occurs within the single evaluation act. |
| Input gathering | The Evaluator gathers the Canonical Object versions required by `metric_binding` for the resolved target and period. Per FND-ERR-003 and DEC-29c324, a single metric evaluation act may read N Canonical Object versions across N referenced Canonical Contract versions. |
| Required parameters | The Evaluator confirms that all required parameters declared by the Contract are bound before formula application. Missing required parameters terminate the evaluation. |
| Formula application | The Evaluator applies the declared formula deterministically over the bound Canonical Field values. Formula semantics are described in the Formula application section. |
| Threshold classification | The Evaluator classifies the formula result against the thresholds governed by the active Metric Contract version. Classification semantics are described in the Threshold classification section. |

The Evaluator applies the Metric Contract as governed. It does not override the formula at runtime, substitute alternative comparison operators, or introduce undeclared parameters.

**Governing source.** the Metric Contract section of The Contract Grammar; Contract Schemas reference; P02 Metric Contract dossier.

## Interpreting `metric_binding` at runtime

The active Metric Contract version carries `metric_binding` as part of its governed body. The binding declares which Canonical Contract versions the metric reads from and which Canonical Field names participate in the formula. the Metric Contract section of The Contract Grammar names the binding as `metric_binding`. The exact binding schema lives in the Contract Schemas reference and the P02 dossier.

| Runtime application step | Runtime behavior |
|---|---|
| Binding resolution | The Evaluator resolves the `metric_binding` declared on the active Metric Contract version. |
| Canonical Contract version reference | For each binding entry, the Evaluator identifies the referenced Canonical Contract version and the role of its Canonical Object versions in the formula. |
| Canonical Field consumption | The Evaluator identifies the Canonical Field names consumed by the formula from each referenced Canonical Contract version. Canonical Fields are the metric-side input vocabulary; the Source-side Business Field to Canonical Field binding was applied earlier at the canonical evaluation boundary. |
| Coverage check | The Evaluator confirms that every formula variable bound to a Canonical Field name has a corresponding `metric_binding` entry. |

Because `metric_binding` is part of the Metric Contract body, it follows the governance and version rules of the Metric Contract version that carries it. It is not treated here as a separate contract family or independent governed artifact.

**Governing source.** the Metric Contract section of The Contract Grammar; Contract Schemas reference; P02 Metric Contract dossier.

## Formula application

The Metric Contract's formula declares deterministic computation over bound Canonical Field values. The same input set under the same Contract version produces the same numeric result.

| Formula concern | Runtime behavior |
|---|---|
| Variable binding | Each formula variable is bound to a Canonical Field value gathered from the Canonical Object versions identified by `metric_binding`. |
| Grain alignment aggregation | Where the Metric Contract grain is coarser than the contributing Canonical Object grains, the required aggregation occurs before symbolic computation. |
| Symbolic computation | The Evaluator applies the formula's symbolic operations to the bound and aggregated input values. |
| Result production | The Evaluator produces one numeric result for the evaluation act. The result type and unit conform to the Contract's declared result shape and units. |

Formula evaluation is the only operation that produces a Metric Snapshot's numeric value. Surface-layer or read-time computations against Canonical Objects do not produce authoritative metric values.

## Temporal gate and readiness

The Metric Contract's temporal gate declares when an evaluation act is eligible to proceed. Under the current Foundation contract grammar, this chapter defines the gate by runtime effect rather than by enumerating a full operational sub-schema. Exact field-level realization, where present in the Contract Schemas reference or active ADR refinements, must remain consistent with the Metric Contract grammar before it is treated as authoritative documentation.

| Gate concern | Runtime effect |
|---|---|
| Evaluation eligibility | The gate determines when an evaluation target may be considered for execution. |
| Input completeness | The gate determines what completeness conditions must hold over the gathered Canonical Object versions before evaluation proceeds. |
| Period coverage | The gate determines what evaluation period must be covered by the gathered inputs. |
| Gated disposition | When the gate is not satisfied, the Run records a terminal gated outcome and no Metric Snapshot is emitted. |

Subsequent evaluation acts are independent. A gated outcome does not retract previously emitted Metric Snapshots, and a later successful evaluation produces a new Metric Snapshot.

## Threshold classification

The Metric Contract declares the threshold structure applied to each emitted Metric Snapshot. Under the current Foundation contract grammar, this chapter defines threshold classification by runtime effect rather than by enumerating sub-schema fields. The exact threshold structure lives in the Contract Schemas reference.

| Classification concern | Runtime effect |
|---|---|
| Direction | The Contract declares which direction of the result is favorable. The Evaluator uses that direction to interpret comparisons against the governed threshold boundaries. |
| Band assignment | The Evaluator classifies the formula result into one of the governed bands declared by the active Metric Contract version. |
| Recorded outcome | The classification outcome is preserved on the emitted Metric Snapshot. Subsequent reads of the Snapshot return the recorded outcome; classification is not recomputed at read time. |

Threshold classification is part of the emitted Metric Snapshot. It is not produced by surface layers and is not modifiable after emission.

## Evaluation sequence

Each Metric Evaluator invocation executes a fixed sequence at the metric evaluation boundary. The sequence is ordered and non-skippable.

| Step | Action | Governing authority |
|---|---|---|
| 1 | The Evaluator resolves the active Metric Contract version for the evaluation target | Metric Contract |
| 2 | The Evaluator applies the temporal gate and confirms that the evaluation act is eligible to proceed | Metric Contract |
| 3 | The Evaluator interprets `metric_binding` and gathers the Canonical Object versions required for the resolved target and period | Metric Contract |
| 4 | The Evaluator binds formula variables to Canonical Field values, aligns grain as required, and applies the formula deterministically | Metric Contract |
| 5 | The Evaluator classifies the formula result against the governed thresholds | Metric Contract |
| 6 | The Evaluator emits the act's Metric Snapshots together with one act-level Evidence and one act-level Lineage referencing the consumed Canonical Object versions and the applied Metric Contract version. Per DEC-ebb3cd D-2, lineage cardinality is per evaluation act (not per emitted snapshot); per-snapshot identities are preserved through the lineage record's reference set so that downstream readers can walk evaluation → snapshots without paying linear lineage cost. | Object Model (The Object Model); Invariant VI; DEC-ebb3cd D-2 |
| 7 | The Evaluator writes the tenant-scoped Metric Evaluation Run with applied governed versions, input references, evaluation outcome, and proof references | DEC-771baf; DEC-f02230; Data Model and Schema |

Three consequences follow from this sequence.

1. A formula-evaluation failure or a missing required parameter does not produce a Metric Snapshot.
2. A gated outcome at step 2 prevents emission. The Run records the gated outcome; no Metric Snapshot is emitted.
3. A successful evaluation produces one new Metric Snapshot. Prior Metric Snapshots are not modified or retracted.

## Evidence and Lineage at metric evaluation

Metric evaluation attempts proof emission at the same boundary act that produces the Metric Snapshot. Per DEC-ebb3cd the attempt is best-effort: an Evidence-write failure is caught and logged rather than rolling back the act. **As-built note:** the decided `proof_status` durability marker is **not yet** a column on `progression.metric_evaluation` (no such column at the inspected head), and the orchestrator's catch block only logs the failure. Treat `proof_status` as decided durability *doctrine* (DEC-ebb3cd), not live behavior, until the column and its wiring land.

| Proof artifact | Scope at metric evaluation | Purpose |
|---|---|---|
| Evidence | Per evaluation act | Records validation outcome, boundary context, applied versions, and disposition. One Evidence per evaluation act regardless of how many Metric Snapshots the act produced. |
| Lineage | Per evaluation act | Records direct references from the act to the consumed Canonical Object versions and the applied Metric Contract version. Per DEC-ebb3cd D-2 the cardinality is per-act (not per-snapshot); the snapshot identities emitted by the act are referenced through the lineage record's reference set so that per-snapshot provenance is preserved without lineage row inflation. |

Readers that walk lineage to reason about specific Metric Snapshots use the lineage record's snapshot reference set; they do not assume one lineage record per snapshot. Run-level operational references may exist for diagnostics or reporting; they do not replace the per-act Lineage record as the authoritative reference surface.

## Metric Evaluation Run

The Metric Evaluation Run is the tenant-scoped execution record for one Evaluator invocation at the metric evaluation boundary. Under the current Foundation model, one invocation corresponds to one evaluation act. The Run is tenant-scoped under DEC-771baf and is held in the tenant database.

| Property | Value |
|---|---|
| Scope | Tenant |
| Store class | Tenant metric-run store in the progression-oriented tenant execution layer |
| Initiated by | Evaluator invocation against one evaluation target |
| Records | Metric Contract version applied, interpreted `metric_binding`, gathered Canonical Object references, gate outcome, formula result, classification outcome, and references to emitted proof |
| Lifecycle | Queued or running state followed by a terminal outcome state (`emitted`, `gated`, or `failed`) |
| Retention | Append-only operational history |

DEC-771baf governs tenant ownership of execution data. DEC-f02230 and its active tenant-schema amendments govern where tenant execution records live structurally. This chapter therefore defines the Metric Evaluation Run semantically and operationally; Data Model and Schema defines exact schema and table names.

The Metric Evaluation Run is an operational record. It is authoritative for run accounting and invocation history. It does not replace Metric Snapshots, Evidence, or Lineage as the authoritative outcome of metric evaluation.

## Secondary metric evaluation (composite runtime)

A secondary Metric Snapshot is a Metric Snapshot whose Lineage references other Metric Snapshots — a **descriptive** DAG of metric dependencies (DEC-0f3e57). Traversal reads preserved Lineage and never triggers recomputation (Invariant V); a changed upstream yields a new forward evaluation act, never an in-place recompute (Invariant III).

The **computation and progression/fact-persistence path is operative today**, not deferred. The composite evaluator (`CompositeMetricEvaluationService`, routed by `MetricEvaluationOrchestrator`) resolves each declared upstream input **scoped to an exact fiscal period** (`as_of_period_end` / `period_matched` read the evaluation period; `prior_period_end` reads the immediately preceding period and fails closed — DEFER upstream — when no snapshot exists), applies the governed composite formula, and — via `GovernedMetricPersistenceAdapter.commitEvaluation` — inserts one `progression.metric_evaluation` row, the `fact.ms_*` projection rows, and finalizes the `metric_run`. This computation/persistence path is supported by the mounted code and its focused tests; the `fact.ms_*` table count and the existence of `evidence.lineage_object` are substrate *shape*, not evidence that a proof chain executes.

**As-built proof gaps (this is more than E6).** The composite path is **not** proof-complete:

- It **emits no governed Lineage.** `commitEvaluation` writes no `evidence.lineage_object` row — its comment labels `input_references_json.selection` as "Lineage," but there is **no `createLineage` call** anywhere on the composite / orchestrator / persistence-adapter path. After commit it attempts only a run-level Evidence record (`EvidenceService.createEvidence`). A real per-evaluation-act Lineage record is required by Invariants IV/VI and DEC-ebb3cd D-2 and is an outstanding platform gap (**TSK-6b1810**).
- **Upstream references are not snapshot identities (E6 / FND-R2-1).** Resolution selects `WHERE metric_contract_id = <upstream MC> AND fiscal_period = <period> AND status = 'accepted' ORDER BY evaluated_at DESC LIMIT 1` and stores the upstream **Metric Contract UID** in `selection.resolved` — the *latest-accepted value* for that MC and period, not the exact consumed **Metric Snapshot** (`metric_evaluation_id`). This weakens Invariant IV (references explicit).

**E6 closure is therefore two-part:** (a) select and retain the exact consumed `metric_evaluation_id` values (not latest-accepted), and (b) persist them in a real per-evaluation governed Lineage record alongside the emitted snapshot identity. Until both land, the composite path is an operative computation **without a governed proof chain** — its current upstream references must not be called fixed snapshots, and its state must not be called persisted or period-exact Lineage.

**Later expansion.** The general, substrate-driven, shape-dispatch metric runtime is governed by DEC-483f1e; this chapter records the current composite computation path and its proof gaps, not that expansion.

**Governing source.** DEC-0f3e57; DEC-483f1e; DEC-ebb3cd; The Object Model (Metric Snapshot); The Evaluation Boundaries.

## Chapter boundaries

This chapter has defined the Metric Evaluator, runtime application of the Metric Contract and its `metric_binding`, deterministic formula application over Canonical Field values, the temporal-gate runtime effect, threshold classification, the ordered evaluation sequence, the per-evaluation-act proof attempt (Evidence; governed Lineage per DEC-ebb3cd D-2 where wired), the tenant-scoped Metric Evaluation Run, and the operative secondary-metric composite computation path with its outstanding proof-chain gaps. Under the current Foundation authoritative reading a primary metric evaluation act consumes Canonical Object versions and emits one Metric Snapshot; a secondary act computes over upstream metric values (its exact-snapshot Lineage is not yet wired — TSK-6b1810). It has deferred:

- Broader shape-dispatch expansion of the metric runtime (DEC-483f1e) beyond the current composite runtime, and the E6/FND-R2-1 exact-consumed-Snapshot-ID repair (Secondary metric evaluation) — the composite secondary runtime itself is operative, not deferred.
- Action evaluation and Action Object emission (Action Evaluation).
- Tenant-scoped binding records that pair a Metric Contract with environment-specific configuration (Tenancy and Binding).
- Relational schema details and exact persistent-store names for runtime and tenant execution records (Data Model and Schema).
- API endpoints and administrative workflows for evaluator operations (API Surface).

Subsequent chapters describe how Metric Snapshots participate in action evaluation and how Evidence and Lineage accumulate as the authoritative proof chain.

## References

- Platform P02 Contract Registry: Metric Contract dossier
- The Object Model: The Object Model
- the Metric Contract section of The Contract Grammar: Metric Contract
- the Metric evaluation boundary section of The Evaluation Boundaries: Metric evaluation boundary
- Canonical Evaluation: Canonical Evaluation
- Action Evaluation: Action Evaluation
- Tenancy and Binding: Tenancy and Binding
- Data Model and Schema
- API Surface
- DEC-29c324: N:1 Metric Contract to Canonical Contract cardinality (Decisions)
- DEC-771baf: Tenant database architecture and run scope (Decisions)
- DEC-f02230: Tenant DB schema organization (Decisions)
- FND-ERR-003: N:1 Metric cardinality (Errata)
- Contract Schemas reference
- Decisions: ADR Registry
- Errata: Errata Ledger
