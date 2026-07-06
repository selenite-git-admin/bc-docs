---
id: the-governed-selection
order: 9
title: "The Governed Selection"
status: drafting
authority: authoritative
depends_on: [the-invariants, the-object-model, the-evaluation-boundaries]
governing_sources:
  - Foundation §5.5 (references; governed selection)
  - Foundation §6 (metric evaluation)
  - The Invariants — Invariant IV (governed selection artifact, reserved → defined here)
governing_adrs:
  - DEC-c4c742 (defining the governed selection artifact)
  - DEC-83fda0 (Route B — the as-of/state selection that motivated this definition)
errata_referenced: []
v2_sources: []
---

# The Governed Selection

## Scope

This chapter defines the governed selection — the artifact Invariant IV reserves for resolving, by a declared and versioned rule, which authoritative object versions a reference names. The Invariants establish that every reference identifies a specific version (Invariant IV), and that a governed selection artifact, if introduced, must itself be versioned and must record its resolved target in Lineage. This chapter introduces that artifact. It defines what a governed selection is, the state-as-of-a-point class of question that requires it, its shape, the guarantees it holds, and where it sits relative to the object model and the evaluation boundaries.

This chapter does not redefine the metric boundary (The Evaluation Boundaries) or the Metric Snapshot (The Object Model). It defines the selection a metric evaluation performs over its inputs.

**Governing source.** The Invariants — Invariant IV; The Evaluation Boundaries; Foundation §5.5.

## What a governed selection is

**Definition.** A governed selection is a declared, versioned rule that, given a selection parameter, resolves from the immutable authoritative-object set the specific object versions that constitute a named state, and records the resolved set in Lineage. It is performed once, at an evaluation boundary, as the input-selection of an evaluation act. Its result is an immutable, recorded object version.

A fixed binding (Invariant IV) names one version directly. A governed selection names — by rule rather than by enumeration — the version or versions a reference resolves to, and is admissible only because the rule is governed, the rule is versioned, and the resolved set is recorded. It is the single construction under which "which versions does this reference name" may be answered by a rule rather than a literal without violating referential explicitness.

**Consequence.** "Which objects constitute this state" is answered deterministically and on the record. The answer is fixed at the evaluation that produced it, carried in Lineage, and read thereafter. It does not change based on when or how a reader resolves it.

## Why the model requires it

The object progression is event-native. Each authoritative object records something that occurred: an admission, a canonical evaluation, a metric snapshot. A flow metric selects the objects whose event falls within a declared window and aggregates them; the window is a property of the objects.

A **state-at-P** — a balance, a stock, an outstanding position, an aging band — is not such an object and not such a window. It is the derived consequence of every state-changing event up to a selection point P: the position at P is what remains once all events effective at or before P are accounted for. No single object carries it; it is read by selecting the objects that, at P, still constitute it.

The model must produce this class without violating its invariants, and the naive constructions all do violate them. Invariant IV names them as disallowed: resolving to a read-time head value, inferring a result from time without a declared rule, or running an unrepresented query. Each is the same error — answering a question about P from ungoverned knowledge-time state. The governed selection is the construction that answers it from the declared rule and the stamped facts instead.

**Governing source.** The Problem; The Invariants — Invariant IV; Foundation §6.

## The shape of a governed selection

A governed selection declares three elements.

| Element | Rule |
|---|---|
| Selection parameter | The point P for the state, together with any other governed inputs. The parameter is supplied to the evaluation act as a declared input. It is never the system clock and never resolved at read time. |
| Predicate | A declared rule over the candidate objects' stamped fields — their effective times and other immutable attributes — and the parameter. The predicate references stamped values only; it performs no read-time resolution and no calendar resolution at evaluation. A position predicate compares an object's closing effective time to P; an age predicate compares P minus an object's anchor effective time to a band. |
| Resolved set | The immutable object versions that satisfy the predicate at P. The resolved set is the artifact's output and is what the evaluation records. |

The predicate is total over the candidate set and deterministic: the same rule version, the same parameter, and the same candidate object versions resolve the same set.

**Governing source.** The Invariants — Invariant IV; The Object Model.

## Guarantees

A governed selection holds the following, each an invariant applied to selection.

| Invariant | Applied to the governed selection |
|---|---|
| I. Meaning once | The selection is performed once, at the evaluation boundary, as the input-selection of an evaluation act. Reads and consumers do not perform it; they read the recorded result. |
| III. Immutable | The recorded result of an evaluation is never altered. |
| IV. Explicit reference | The selection rule is itself a versioned artifact; an evaluation names the rule version it applied. The resolved set — which object versions were selected at P — is recorded in Lineage. |
| V. Non-replayable | An evaluation of (rule version, parameter) produces exactly one result version. Evaluating the same rule version and parameter again, when more facts are known, is a distinct act producing a distinct version. Audit reads the version it requires; it does not rerun the selection to reconstruct a past result. |
| VI. Evidence emitted | The resolved set is emitted as evidence with the evaluation, not inferred afterward. If no record of a selection exists, the selection did not occur. |

The disallowed behaviors of Invariant IV hold by construction. Membership in a state at P is derived from the predicate applied to stamped facts at P. It is never read from a stored status. A stored status reflects the moment it was written — knowledge time — and using it to answer a question about an arbitrary P silently misclassifies every other P. The governed selection carries no such value; it derives membership each time it is evaluated, from the dates the objects carry.

**Governing source.** The Invariants; The Evaluation Boundaries.

## Relationship to the object model and the boundaries

A metric that reports a state is two steps: a governed selection of the object set at P, then an aggregation over the resolved set. The selection is the input step; the aggregation is the formula. The result is an ordinary Metric Snapshot. The governed selection introduces no new object type; it is a contract-level mechanism exercised within metric evaluation.

The governed selection is performed at the metric boundary and is subject to the boundary-independent rules: it reads stamped state and does not trigger upstream evaluation, and it emits Evidence and Lineage with its result. The metric-grammar surface of the governed selection is the temporal-gate of a Metric Contract; the as-of and cumulative-to-date temporal-gate shapes are governed selections expressed in the metric grammar.

**Governing source.** The Object Model; The Evaluation Boundaries; The Contract Grammar.

## The reserved artifact, generalized

Invariant IV reserves the governed selection artifact in the context of resolving a single reference to a single version. The artifact defined here is the general form. Resolving one reference to one version by a governed rule is the degenerate case in which the resolved set has one member; resolving a state at P to the set of object versions that constitute it is the general case. Both are the same construction: a versioned rule resolves which object versions a reference names, and the resolved versions are recorded in Lineage. Defining the general form defines the reserved artifact; the single-version case is recovered by a predicate that resolves to one version.

**Governing source.** The Invariants — Invariant IV.

## Generalization to all metric selection

The worked examples in this chapter are state metrics — a balance, an outstanding position, an aging band — but the governed selection is not specific to state. Every metric, flow or state, is a governed selection over the candidate objects followed by an aggregation; the two differ only in the predicate. A flow metric's predicate is interval membership on an event time: the objects whose stamped event falls within the declared window or period. A state metric's predicate is openness relative to P: the objects open at P. Both are declared, versioned rules over stamped fields and the reporting point P; both record the resolved set in Lineage; both are forbidden read-time head values and unrepresented query shortcuts equally.

The governed selection is therefore the metric-selection primitive — one artifact, one predicate per the metric's declared temporal-gate shape — and a metric evaluation is one path: a governed selection, then an aggregation over the resolved set. The single-reference-to-single-version resolution of the section above, the per-shape selection of a flow or state metric here, and the single-version degenerate case are the same construction at different cardinalities over different predicates.

**Governing source.** The Invariants — Invariant IV; The General Metric Runtime (DEC-483f1e); DEC-c4c742.

## Knowledge time

A state at P is taken with the facts known at the moment of evaluation. Later evaluation of the same state at the same P, when more facts are known, is a distinct act under Invariant V and produces a distinct result version. The two results — selection point P under one knowledge-time record, and selection point P under a later knowledge-time record — both exist and are both preserved. Neither replaces the other.

The base model evaluates a state at the knowledge available when the evaluation runs. The accumulation of result versions across evaluations is the record of how the answer to "the state at P" was known over time; it is read, not reconstructed. A mechanism for querying a state at P under a chosen earlier knowledge-time record is not introduced here; the immutable record that would support it is a consequence of Invariant V regardless.

**Governing source.** The Invariants — Invariant V; Foundation §6.5.

## Constraints

| Constraint | Operational form |
|---|---|
| Parameter is a declared input | P and any other selection parameters are supplied to the evaluation act. The selection never reads the system clock or a read-time "current" value. |
| Predicate reads stamped facts only | The predicate compares the candidate objects' stamped effective times and immutable attributes to the parameter. It performs no resolution and no calendar lookup at evaluation. |
| Status is derived, never stored | Membership in a state at P is derived from the predicate. A stored status flag is not a source of as-of membership for any P other than the one at which it was written. |
| Rule is versioned | A change to the predicate or the candidate scope is a new rule version. An evaluation names the version it applied. |
| Resolved set is recorded | The object versions selected at P are emitted in Lineage with the result. Absent that record, the selection is treated as not having occurred. |
| Re-evaluation is a new version | Re-running a selection does not reproduce a prior result version; it produces a new one. Audit reads preserved results. |

**Governing source.** The Invariants.

## Failure modes

| Failure | Detection point | Treatment |
|---|---|---|
| A selection resolves membership from a stored status flag rather than from a predicate over stamped dates | Metric Contract authoring | Rejected. The flag answers a write-time status question; the selection must declare a predicate over stamped effective times. |
| The selection parameter is taken from the system clock or a read-time "current" value | Metric Contract authoring | Rejected. The parameter is a declared evaluation input; read-time head values are disallowed by Invariant IV. |
| The predicate resolves a fiscal or calendar value at evaluation rather than comparing stamped values | Metric evaluation | Rejected. The boundary does not resolve fiscal time; it compares stamped fields (consistent with the fiscal-time discipline). |
| The resolved set is not recorded in Lineage | Metric evaluation | The result is not authoritative. With no record of which objects were selected, the selection is treated as not having occurred (Invariant VI). |
| A past as-of result is recomputed for audit by re-running the selection against preserved inputs | Audit | Disallowed. Audit reads the preserved result version; it does not rerun the selection (Invariant V). |

**Governing source.** The Invariants; The Evaluation Boundaries.

## References

- The Invariants: Invariant IV (governed selection artifact), Invariant V (non-replayable), Invariant VI (evidence emitted)
- The Object Model: the Metric Snapshot
- The Evaluation Boundaries: the metric boundary; boundary-independent rules
- The Contract Grammar: the Metric Contract temporal-gate
- Fiscal Time and Temporal Gates (operating-model): stamped fiscal period; no calendar resolution at evaluation
- DEC-c4c742: defining the governed selection artifact
- DEC-83fda0: Route B — the as-of/state selection that motivated this definition
