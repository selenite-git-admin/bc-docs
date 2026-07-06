---
id: canonical-evaluation
order: 10
title: "Canonical Evaluation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, admission-and-observation]
governing_sources:
  - Platform P02 Contract Registry (Canonical Contract dossier)
  - The Contract Grammar, Canonical Contract section
  - The Contract Grammar, Canonical Mapping section
  - The Evaluation Boundaries, Canonical evaluation boundary section
governing_adrs:
  - DEC-97bb94 (N:1 Source Object to Canonical Object cardinality)
  - DEC-136a23 (Canonical Mapping)
  - DEC-771baf (Tenant database architecture and run scope)
  - DEC-f02230 (Tenant DB schema organization)
errata_referenced:
  - FND-ERR-004
v2_sources:
  - system/platform/P02-contract-registry/canonical-contract/index.md
  - system/platform/P02-contract-registry/canonical-contract/01-specification.md
  - system/platform/P02-contract-registry/canonical-contract/02-architecture.md
  - system/foundation/contract-schemas/canonical-v1.md
  - system/foundation/contract-schemas/schemas/canonical-mapping-v1.json
---

# Canonical Evaluation

## Scope

This chapter defines the runtime components and execution behavior at the canonical evaluation boundary under the current Foundation execution model. It describes the Canonical Evaluator and the tenant-scoped Canonical Evaluation Run; defines how the Canonical Contract and Canonical Mapping are applied at runtime; defines the readiness gate at the level authorized by the current contract grammar; defines the evaluation sequence that produces a Canonical Object together with Evidence and Lineage; and defines the tenant-scoped run record that preserves invocation outcomes. It distinguishes contract authority from runtime application so that governed contract shape and operational behavior are not conflated. It does not redefine the contract grammar (The Contract Grammar), the canonical evaluation boundary as an execution-model concept (The Evaluation Boundaries), the admission components that produce Source Objects (Admission and Observation), tenant-scoped binding records (Tenancy and Binding), the full relational schema (Data Model and Schema), or the API surface for evaluator operations (API Surface).

This chapter follows the current authoritative Foundation reading in which canonical evaluation consumes Source Objects and emits Canonical Objects. Broader derivative patterns, if introduced later by ADR adoption, require corresponding updates to the Foundation spine before they become authoritative here.

## Runtime inventory

Canonical evaluation uses one platform-scoped runtime component and one tenant-scoped execution record.

| Component | Role | Scope | Persistent store |
|---|---|---|---|
| Canonical Evaluator | Platform runtime that applies a Canonical Contract version and Canonical Mapping version to one or more Source Objects to produce one Canonical Object version | Platform | Platform-scoped service definition |
| Canonical Evaluation Run | Per-invocation tenant execution record for canonical evaluation outcomes | Tenant | Tenant canonical-run store defined by current tenant-schema ADRs and Data Model and Schema |

The Canonical Evaluator is governed centrally and reused across tenants. Canonical Evaluation Run is tenant-scoped under DEC-771baf. The run record preserves the operational result of invoking platform-governed evaluation logic against tenant-held Source Objects.

## Canonical Evaluator

**Purpose.** The Canonical Evaluator is the platform runtime component that applies a Canonical Contract version and the corresponding Canonical Mapping version to one or more Source Objects to produce one Canonical Object version together with its Evidence and Lineage.

**Behavior.** At invocation, the Evaluator resolves the Canonical Contract referenced by its evaluation target, resolves the Canonical Mapping version associated with that Contract version, gathers the Source Objects required by the Contract, evaluates whether the declared temporal gate is satisfied, applies field selection, mapping, resolution rules, and semantic rules over the gathered inputs, emits one Canonical Object per evaluation act, and writes Evidence, per-object Lineage, and the Canonical Evaluation Run at the same act.

**Constraints.**
- The Evaluator does not infer Canonical Field values not declared by the governed Canonical Contract and Canonical Mapping.
- The Evaluator does not modify a previously emitted Canonical Object version.
- The Evaluator does not apply Metric Contract logic.
- The Evaluator does not admit Source Objects.
- The Evaluator does not treat previously emitted Canonical Objects as canonical-boundary inputs in this chapter's authoritative scope.

**Failure modes.** Evaluator failures decompose into gate failures, input-resolution failures, schema-conformance failures, and semantic-rule failures. A gate failure records a terminal gated outcome on the Run and emits no Canonical Object. An input-resolution or schema-conformance failure records a terminal failed outcome on the Run and emits no Canonical Object. A semantic-rule failure records Evidence for the failed rule; whether a Canonical Object is emitted depends on the rule's declared severity.

**Governing source.** P02 Canonical Contract dossier; the Canonical evaluation boundary section of The Evaluation Boundaries.

## Canonical Contract application

The Canonical Contract referenced by an evaluation target governs canonical evaluation at runtime. the Canonical Contract section of The Contract Grammar defines the responsibility of the Canonical Contract and names its eight body keys. The exact body schema lives in the Contract Schemas reference and the P02 Canonical Contract dossier. This section describes runtime application order and effect. It does not redefine the schema.

| Runtime application step | Runtime behavior |
|---|---|
| Business Object resolution | The Evaluator resolves `business_object_code` to the governed Business Object and confirms that the Contract is active for that Business Object. |
| Evaluation tier interpretation | The Evaluator reads `evaluation_tier` as part of the governed Contract body. Under the current authoritative Foundation model, canonical evaluation executes Tier 1 semantics: Source Objects are the admissible input class. |
| Grain resolution | The Evaluator applies `grain[]` to identify the dimensional identity of the Canonical Object being produced. Grain identity determines which Source Objects compose into the same Canonical Object. |
| Input gathering | The Evaluator gathers the Source Objects required by the Contract for the resolved grain identity. Per FND-ERR-004 and DEC-97bb94, a single canonical evaluation act may consume N Source Objects across N Source Contracts to produce one Canonical Object version. |
| Field selection | The Evaluator applies `field_selection[]` to determine which Canonical Fields must be populated in the emitted Canonical Object. |
| Resolution | The Evaluator applies `resolution_rules[]` to reduce one or more mapped Business Field inputs into one resolved value per selected Canonical Field. Resolution semantics are described in the Resolution rules at runtime section. |
| Schema conformance | The Evaluator verifies that the resolved Canonical Object payload conforms to `resolved_schema`. Evaluations that fail schema conformance do not emit a Canonical Object. |
| Semantic evaluation | The Evaluator applies `semantic_rules[]` over the resolved payload. Semantic-rule outcomes are recorded as Evidence; rule severity governs whether the Canonical Object is emitted. |
| Gate application | The Evaluator applies `temporal_gate` to determine whether the evaluation act is eligible to proceed for the current target and input interval. Gate behavior is described in the Temporal gate and readiness section. |

The Evaluator applies the Canonical Contract as governed. It does not override governed rule actions, downgrade a blocking semantic rule at runtime, or introduce undeclared resolution logic.

**Governing source.** the Canonical Contract section of The Contract Grammar; Contract Schemas reference; P02 Canonical Contract dossier.

## Canonical Mapping application

The Canonical Mapping referenced by the active Canonical Contract version governs the field-level binding from Source-side Business Fields to Canonical-side Canonical Fields. the Supporting schema: Canonical Mapping section of The Contract Grammar defines the Canonical Mapping as a governed and versioned supporting schema. The exact mapping body schema lives in the Contract Schemas reference and the P02 dossier.

| Runtime application step | Runtime behavior |
|---|---|
| Mapping resolution | The Evaluator resolves the Canonical Mapping version associated with the active Canonical Contract version. |
| Per-field binding | For each mapping entry, the Evaluator binds one or more input Business Field values carried on Source Objects to one Canonical Field declared by the Canonical Contract. Where a single Canonical Field is sourced from multiple Business Fields, the entry records the admissible reduction basis. |
| Coverage check | The Evaluator confirms that every Canonical Field declared in `field_selection[]` has a corresponding mapping entry. |

The Canonical Mapping is platform-scoped. Tenant variation does not modify it. Binding-level variation, where permitted elsewhere in the contract model, cannot remove platform-declared mapped fields or alter governed mapping rules.

**Governing source.** the Supporting schema: Canonical Mapping section of The Contract Grammar; DEC-136a23; Contract Schemas reference; P02 Canonical Contract dossier.

## Resolution rules at runtime

The Canonical Contract's `resolution_rules[]` declares deterministic reduction across multiple mapped Business Field inputs. The same input set under the same Contract version produces the same resolved Canonical payload.

| Resolution semantics | Effect when multiple candidate Business Field inputs contribute to one Canonical Field |
|---|---|
| Aggregation | The reduction combines numeric inputs into one resolved value. |
| Selection by ordering | The reduction selects one input value by a declared ordering such as greatest admissible timestamp or earliest key. |
| Selection by source preference | The reduction selects one input value according to declared preference among contributing Source Contracts or Source Object classes. |
| Equality assertion | The reduction asserts that all candidate inputs are equal. Disagreement is recorded as an evaluation failure. |
| Conflict policy | When the declared rule does not produce a unique outcome, the field's declared conflict policy applies. |

The Canonical Object payload emitted at the end of evaluation contains exactly one resolved value per Canonical Field declared in `field_selection[]`. The payload structurally matches `resolved_schema`.

## Temporal gate and readiness

The Canonical Contract's `temporal_gate` declares when an evaluation act is eligible to proceed. Under the current Foundation contract grammar, this chapter defines the gate by runtime effect rather than by a full operational scheduler schema. Exact field-level realization, where present in the Contract Schemas reference or active ADR refinements, must remain consistent with the Canonical Contract grammar before it is treated as authoritative documentation.

| Gate concern | Runtime effect |
|---|---|
| Evaluation eligibility | The gate determines when an evaluation target may be considered for execution. |
| Readiness conditions | The gate determines what upstream readiness conditions must hold before evaluation proceeds. |
| Input interval | The gate determines which admissible input interval is in scope for the evaluation act. |
| Gated disposition | When the gate is not satisfied, the Run records a terminal gated outcome and no Canonical Object is emitted. |

Subsequent evaluation acts are independent. A gated outcome does not retract previously emitted Canonical Objects, and a later successful evaluation produces a new Canonical Object version.

## Evaluation sequence

Each Canonical Evaluator invocation executes a fixed sequence at the canonical evaluation boundary. The sequence is ordered and non-skippable.

| Step | Action | Governing authority |
|---|---|---|
| 1 | The Evaluator resolves the active Canonical Contract version and Canonical Mapping version for the evaluation target | Canonical Contract; Canonical Mapping |
| 2 | The Evaluator applies `temporal_gate` and confirms that the evaluation act is eligible to proceed | Canonical Contract |
| 3 | The Evaluator gathers Source Objects for the resolved grain identity and admissible input interval | Canonical Contract |
| 4 | The Evaluator applies `field_selection[]`, the Canonical Mapping, and `resolution_rules[]` to produce a resolved payload | Canonical Contract; Canonical Mapping |
| 5 | The Evaluator verifies the resolved payload against `resolved_schema` and applies `semantic_rules[]` | Canonical Contract |
| 6 | The Evaluator emits one Canonical Object together with Evidence and per-object Lineage referencing the consumed Source Objects and applied governed versions | Object Model (The Object Model); Invariant VI |
| 7 | The Evaluator writes the tenant-scoped Canonical Evaluation Run with applied governed versions, input references, evaluation outcome, and proof references | DEC-771baf; DEC-f02230; Data Model and Schema |

Three consequences follow from this sequence.

1. A record that fails schema conformance or a blocking semantic rule does not produce a Canonical Object.
2. A gated outcome at step 2 prevents emission. The Run records the gated outcome; no Canonical Object is emitted.
3. A successful evaluation produces a new Canonical Object version. Prior Canonical Object versions are not modified or retracted.

## Evidence and Lineage at canonical evaluation

Canonical evaluation emits proof at the same boundary act that produces the Canonical Object. Proof is not deferred.

| Proof artifact | Scope at canonical evaluation | Purpose |
|---|---|---|
| Evidence | Per evaluation act and per rule outcome | Records validation outcome, boundary context, applied versions, and disposition |
| Lineage | Per emitted Canonical Object | Records direct references from the Canonical Object to the consumed Source Objects, the applied Canonical Contract version, and the applied Canonical Mapping version |

Run-level operational references may exist for diagnostics or reporting, but they do not replace per-object Lineage for emitted Canonical Objects.

## Canonical Evaluation Run

The Canonical Evaluation Run is the tenant-scoped execution record for one Evaluator invocation at the canonical evaluation boundary. The Run is tenant-scoped under DEC-771baf and is held in the tenant database.

| Property | Value |
|---|---|
| Scope | Tenant |
| Store class | Tenant canonical-run store in the progression-oriented tenant execution layer |
| Initiated by | Evaluator invocation against an evaluation target |
| Records | Canonical Contract version applied, Canonical Mapping version applied, gathered input references, gate outcome, resolution outcome, schema-conformance outcome, semantic-rule outcomes, and references to emitted proof |
| Lifecycle | Queued or running state followed by a terminal outcome state (`emitted`, `gated`, or `failed`) |
| Retention | Append-only operational history |

DEC-771baf governs tenant ownership of execution data. DEC-f02230 and its active tenant-schema amendments govern where tenant execution records live structurally. This chapter therefore defines the Canonical Evaluation Run semantically and operationally; Data Model and Schema defines exact schema and table names.

The Canonical Evaluation Run is an operational record. It is authoritative for run accounting and invocation history. It does not replace Canonical Objects, Evidence, or Lineage as the authoritative outcome of canonical evaluation.

## Chapter boundaries

This chapter has defined the Canonical Evaluator, runtime application of the Canonical Contract and Canonical Mapping, deterministic resolution semantics, the temporal-gate runtime effect, the ordered evaluation sequence, per-object proof emission, and the tenant-scoped Canonical Evaluation Run, all under the current Foundation authoritative reading in which canonical evaluation consumes Source Objects and emits Canonical Objects. It has deferred:

- Derivative Canonical Object behavior beyond the current Foundation scope, pending Foundation update.
- Metric evaluation and Metric Snapshot emission (Metric Evaluation).
- Tenant-scoped binding records that pair a Canonical Contract with environment-specific configuration (Tenancy and Binding).
- Relational schema details and exact persistent-store names for runtime and tenant execution records (Data Model and Schema).
- API endpoints and administrative workflows for evaluator operations (API Surface).

Subsequent chapters describe how Canonical Object versions participate in metric evaluation and how Evidence and Lineage accumulate as the authoritative proof chain.

## References

- Platform P02 Contract Registry: Canonical Contract dossier
- The Object Model: The Object Model
- the Canonical Contract section of The Contract Grammar: Canonical Contract
- the Supporting schema: Canonical Mapping section of The Contract Grammar: Canonical Mapping
- the Canonical evaluation boundary section of The Evaluation Boundaries: Canonical evaluation boundary
- Admission and Observation: Admission and Observation
- Metric Evaluation: Metric Evaluation
- Tenancy and Binding: Tenancy and Binding
- Data Model and Schema
- API Surface
- DEC-97bb94: N:1 Source Object to Canonical Object cardinality (Decisions)
- DEC-136a23: Canonical Mapping (Decisions)
- DEC-771baf: Tenant database architecture and run scope (Decisions)
- DEC-f02230: Tenant DB schema organization (Decisions)
- FND-ERR-004: N:1 Source-to-Canonical cardinality (Errata)
- Contract Schemas reference
- Decisions: ADR Registry
- Errata: Errata Ledger
