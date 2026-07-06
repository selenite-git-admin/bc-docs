---
id: action-evaluation
order: 12
title: "Action Evaluation"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-contract-grammar, the-evaluation-boundaries, the-authority-model, metric-evaluation]
governing_sources:
  - Platform P02 Contract Registry (Intervention Contract dossier)
  - The Contract Grammar, Intervention Contract section
  - The Evaluation Boundaries, Action evaluation boundary section
  - The Object Model, Action Object section
governing_adrs:
  - DEC-771baf (Tenant database architecture and run scope)
  - DEC-f02230 (Tenant DB schema organization)
v2_sources:
  - system/platform/P02-contract-registry/intervention-contract/index.md
  - system/platform/P02-contract-registry/intervention-contract/01-specification.md
  - system/foundation/contract-schemas/intervention-v1.md
---

# Action Evaluation

## Scope

This chapter defines the runtime components and execution behavior at the action evaluation boundary under the Foundation execution model. It describes the Action Evaluator and the tenant-scoped Action Evaluation Run; defines how the Intervention Contract is applied at runtime; defines the action-creation act that emits one Action Object together with Evidence and Lineage; defines the outcome-resolution act that, while the closure window is open, sets the preserved Action Object's terminal-state attributes and emits supplementary Evidence and Lineage; defines the closure window and the Action Object's terminal-state lifecycle, including forced closure at window elapse; and defines the boundary between platform-governed action evaluation and external operational follow-up. It distinguishes contract authority from runtime application so that governed contract shape and operational behavior are not conflated. It does not redefine the contract grammar (The Contract Grammar), the action evaluation boundary as an execution-model concept (The Evaluation Boundaries), the metric evaluation components that produce Metric Snapshots (Metric Evaluation), tenant-scoped binding records (Tenancy and Binding), the full relational schema (Data Model and Schema), or the API surface for evaluator operations (API Surface).

This chapter follows the authoritative Foundation reading in which action evaluation comprises two governed acts under one Intervention Contract: an action-creation act that emits one Action Object bound at creation time to one or more Metric Snapshots, and an outcome-resolution act that, while the closure window remains open, applies the governed evaluation model to the preserved Metric Snapshot references and sets the Action Object's terminal-state attributes (resolved outcome and resolution timestamp). Per the Action Object section of The Object Model, an Action Object's terminal state is recorded on the Action Object itself; the set-once nature of those attributes does not introduce arbitrary mutation of the progression-object payload, which remains immutable. Each governed act also emits Evidence and Lineage as supplementary proof per the Proof emission at every boundary section of The Evaluation Boundaries. Activation modes and tenant binding surfaces named by the Intervention Contract grammar are acknowledged at the body-element level but are not operationally expanded here beyond what the Intervention Contract section of The Contract Grammar and the Action evaluation boundary section of The Evaluation Boundaries authorize. Operational execution of the action itself is external to the platform.

## Runtime inventory

Action evaluation uses one platform-scoped runtime component and one tenant-scoped execution record.

| Component | Role | Scope | Persistent store |
|---|---|---|---|
| Action Evaluator | Platform runtime that applies one Intervention Contract version to one evaluation target and either emits one Action Object (action-creation act) or sets the preserved Action Object's terminal-state attributes (outcome-resolution act); each act also emits Evidence and Lineage | Platform | Platform-scoped service definition |
| Action Evaluation Run | Per-invocation tenant execution record for one action evaluation act, recording which act type the invocation performed | Tenant | Tenant action-run store defined by governing tenant-schema ADRs and Data Model and Schema |

The Action Evaluator is governed centrally and reused across tenants. Action Evaluation Run is tenant-scoped under DEC-771baf. Under the Foundation model, one evaluator invocation corresponds to one act of one declared type and therefore to one Run record.

## Action Evaluator

**Purpose.** The Action Evaluator is the platform runtime component that applies one Intervention Contract version to one evaluation target. The act type is fixed at invocation: action-creation emits one Action Object; outcome-resolution sets the preserved Action Object's terminal-state attributes and emits supplementary Evidence and Lineage.

**Behavior.** At invocation, the Evaluator resolves the Intervention Contract referenced by its evaluation target, identifies the act type for the invocation (action-creation or outcome-resolution), and applies the Contract body elements relevant to that act type. For an action-creation act, the Evaluator gathers the referenced Metric Snapshot versions, evaluates whether the trigger conditions and activation mode authorize creation, records declared intent, and emits one Action Object together with Evidence and per-object Lineage. For an outcome-resolution act, the Evaluator confirms that the closure window remains open for a preserved Action Object, applies the evaluation model to the preserved Metric Snapshot references recorded on that Action Object at creation time, sets the resolved-outcome and resolution-timestamp attributes on the preserved Action Object once, and emits supplementary Evidence and Lineage at the same act.

**Constraints.**
- The Evaluator does not modify the Action Object's creation-time payload (declared intent, referenced Metric Snapshot versions, applied Intervention Contract version, baseline binding timestamp).
- The Evaluator sets the Action Object's terminal-state attributes (resolved outcome, resolution timestamp, forced-closure marker) at most once per Action Object.
- The Evaluator does not rebind a preserved Action Object to newer Metric Snapshot versions.
- The Evaluator does not introduce a Metric Snapshot reference at outcome resolution that was not recorded on the Action Object at creation time.
- The Evaluator does not reassign an already-recorded terminal-state attribute by reading updated metric state.
- The Evaluator does not execute the action itself; operational execution is external to the platform (the Action Evaluator does not execute the action section).
- The Evaluator does not permit an Action Object to remain in a non-terminal state after the closure window has elapsed; forced closure is recorded on the Action Object via the same set-once attributes (the Closure window and Action Object lifecycle section).

**Failure modes.** Evaluator failures decompose into trigger-evaluation failures, input-resolution failures, and outcome-comparison failures. A trigger-evaluation failure terminates the action-creation act with no Action Object emitted. An input-resolution failure (for example, a referenced Metric Snapshot version cannot be resolved) terminates either act type with no progression-object emission and no terminal-state attributes set. An outcome-comparison failure during outcome-resolution records the failure as Evidence against the preserved Action Object; the terminal-state attributes are not set under a failed comparison, and the Action Object remains eligible for a subsequent resolution attempt while the closure window remains open or for forced closure at window elapse.

**Governing source.** P02 Intervention Contract dossier; the Action evaluation boundary section of The Evaluation Boundaries.

## Intervention Contract application

The Intervention Contract referenced by an evaluation target governs action evaluation at runtime. the Intervention Contract section of The Contract Grammar defines the responsibility of the Intervention Contract and names the body elements it declares: activation mode, trigger conditions, assignee pool, closure window, and evaluation model for outcome resolution against preserved snapshots. The exact body schema lives in the Contract Schemas reference and the P02 Intervention Contract dossier. This section describes how each body element is applied at runtime; specific act sequences are described in the Action-creation act section and the Outcome-resolution act section.

| Body element | Runtime application |
|---|---|
| Activation mode | Determines whether an action-creation act is authorized at runtime. The Evaluator confirms that the mode declared by the active Contract version permits the invocation source for the act. |
| Trigger conditions | Govern whether one or more Metric Snapshot versions satisfy the conditions under which an Action Object may be created. The Evaluator evaluates trigger conditions at the start of an action-creation act before any Action Object is emitted. |
| Assignee pool | Declares the role categories that may own an emitted Action Object. The Evaluator records the assigned owner on the emitted Action Object. The pool is resolved against the active Contract version at action-creation time and is not modified after emission. |
| Closure window | Bounds the period during which an emitted Action Object may remain non-terminal. The Evaluator uses the closure window to determine eligibility for outcome resolution and to record forced closure when the window elapses without resolution. |
| Evaluation model | Governs the comparison applied during the outcome-resolution act. The Evaluator applies the declared comparison logic against the preserved Metric Snapshot references and the snapshot referenced by the outcome-resolution act, and records the outcome as Evidence against the preserved Action Object. |

Each of these elements is part of the Intervention Contract body. None is treated here as a separate contract family or independent governed artifact; each follows the governance and version rules of the Intervention Contract version that carries it.

The Evaluator applies the Intervention Contract as governed. It does not introduce trigger conditions, override the evaluation model, or extend the closure window at runtime.

**Governing source.** the Intervention Contract section of The Contract Grammar; Contract Schemas reference; P02 Intervention Contract dossier.

## Action-creation act

The action-creation act is the IC-governed act that emits one Action Object bound to one or more Metric Snapshots. Each invocation of the act executes a fixed sequence at the action evaluation boundary. The sequence is ordered and non-skippable.

| Step | Action | Governing authority |
|---|---|---|
| 1 | The Evaluator resolves the active Intervention Contract version for the evaluation target | Intervention Contract |
| 2 | The Evaluator confirms that the activation mode declared by the Contract authorizes the invocation source for an action-creation act | Intervention Contract |
| 3 | The Evaluator gathers the candidate Metric Snapshot versions and evaluates the trigger conditions | Intervention Contract |
| 4 | The Evaluator records declared intent, the assignee pool resolved against the active Contract version, the referenced Metric Snapshot versions, and the closure window applicable to the emitted Action Object. The mechanism that picks a specific owner from the recorded pool is governed by tenant binding and is described in Tenancy and Binding. | Intervention Contract |
| 5 | The Evaluator emits one Action Object together with Evidence and per-object Lineage referencing the consumed Metric Snapshot versions and the applied Intervention Contract version | Object Model (The Object Model); Invariant VI |
| 6 | The Evaluator writes the tenant-scoped Action Evaluation Run with applied governed version, input references, evaluation outcome, and proof references | DEC-771baf; DEC-f02230; Data Model and Schema |

Three consequences follow from this sequence.

1. A trigger-evaluation failure or an unauthorized invocation source at step 2 or step 3 does not produce an Action Object. The Run records the terminal outcome.
2. The Metric Snapshot versions referenced at step 5 are fixed at creation time. Subsequent metric evaluation does not retroactively rebind the emitted Action Object.
3. A successful action-creation act produces exactly one Action Object. Prior Action Objects are not modified or retracted.

## Outcome-resolution act

The outcome-resolution act is the IC-governed act that, while the closure window remains open, applies the governed evaluation model to the preserved Metric Snapshot references recorded on a preserved Action Object and sets the Action Object's terminal-state attributes. The act does not produce a new progression object and does not introduce any Metric Snapshot reference that was not recorded at action creation. Each invocation of the act executes a fixed sequence at the action evaluation boundary. The sequence is ordered and non-skippable.

| Step | Action | Governing authority |
|---|---|---|
| 1 | The Evaluator resolves the active Intervention Contract version associated with the preserved Action Object | Intervention Contract |
| 2 | The Evaluator confirms that the closure window for the preserved Action Object remains open and that no terminal-state attributes have already been set | Intervention Contract |
| 3 | The Evaluator gathers the preserved Metric Snapshot references recorded on the Action Object at creation time. No additional Metric Snapshot reference is introduced. | Intervention Contract; the Action evaluation boundary section of The Evaluation Boundaries |
| 4 | The Evaluator applies the governed evaluation model to those preserved references, classifying the recorded snapshot state under the Contract's declared comparison logic | Intervention Contract |
| 5 | The Evaluator sets the resolved-outcome and resolution-timestamp attributes on the preserved Action Object. The set is exactly once per Action Object; the creation-time payload is not modified. | Object Model (the Action Object section of The Object Model); the Action evaluation boundary section of The Evaluation Boundaries |
| 6 | The Evaluator emits supplementary Evidence recording the comparison outcome and supplementary Lineage recording the explicit reference relationship between the resolution act and the applied Intervention Contract version | Object Model (The Object Model); the Proof emission at every boundary section of The Evaluation Boundaries |
| 7 | The Evaluator writes the tenant-scoped Action Evaluation Run with applied governed version, input references, comparison outcome, and proof references | DEC-771baf; DEC-f02230; Data Model and Schema |

Four consequences follow from this sequence.

1. The act does not emit a new progression object. The cardinality of progression objects emitted by the act is zero; the act sets the preserved Action Object's terminal-state attributes once and emits one supplementary Evidence Object plus one supplementary Lineage Object.
2. The act does not introduce a new Metric Snapshot reference. Per the Action evaluation boundary section of The Evaluation Boundaries, references are fixed at action-creation time and are not rebound. The Lineage emitted during the proof step records the resolution act's reference to the applied Intervention Contract version, not to a new metric input.
3. The Action Object's creation-time payload is not modified. Outcome resolution sets the terminal-state attributes (resolved outcome, resolution timestamp); it does not change declared intent, referenced Metric Snapshot versions, the applied Contract version, or the baseline binding timestamp.
4. Metric evaluation is not re-entered. The evaluation model classifies preserved metric state recorded on the Action Object; the outcome-resolution act does not invoke the metric evaluation boundary or produce a new Metric Snapshot.

## Closure window and Action Object lifecycle

The Action Object progresses to a terminal state. The platform does not permit open-ended, indefinitely pending, or retroactively closed Action Objects. Per the Action Object section of The Object Model, an Action Object's identity includes the outcome-resolution timestamp; the terminal-state attributes are recorded on the Action Object itself.

| Lifecycle concern | Runtime effect |
|---|---|
| Creation-time payload | Declared intent, referenced Metric Snapshot versions, applied Intervention Contract version, baseline binding timestamp, and the resolved assignee pool are recorded at creation time and are not modified thereafter. |
| Terminal-state attributes | The Action Object carries set-once attributes for resolved outcome and resolution timestamp. These attributes are unset at creation and may be set exactly once by an outcome-resolution act (the Outcome-resolution act section) or a forced-closure event (below). Once set, they are not modified. |
| Closure window | The window declared by the Intervention Contract bounds the maximum time during which the Action Object's terminal-state attributes may remain unset. The window is open from creation; an outcome-resolution act may run while the window is open. |
| Outcome resolution within the window | While the window is open, an outcome-resolution act may set the terminal-state attributes (resolved outcome, resolution timestamp) per the Outcome-resolution act section. After the attributes are set, the Action Object is in its terminal state. |
| Forced closure at window elapse | If the closure window elapses without the terminal-state attributes having been set, the Evaluator records forced closure on the Action Object via the same set-once attributes. The resolved-outcome attribute records the forced-closure marker; the resolution-timestamp attribute records the elapse moment. Forced closure also emits Evidence and Lineage. |
| Recorded non-closure | Per the Action Object section of The Object Model, the terminal-state attributes express non-closure explicitly when closure conditions are not met. The forced-closure marker is the canonical non-closure recording at window elapse. |

Set-once is the controlled lifecycle progression the Action Object section of The Object Model names ("Action Objects progress to a terminal state"). It is not arbitrary mutation of the progression-object payload, which remains immutable. The Action Object's terminal state is therefore readable on the Action Object itself; supplementary Evidence and Lineage emitted at the same act preserve the proof chain per the Proof emission at every boundary section of The Evaluation Boundaries.

## Evidence and Lineage at action evaluation

Action evaluation emits proof at each governed act. The proof artifacts emitted differ between the action-creation act and the outcome-resolution act.

| Act | Evidence | Lineage |
|---|---|---|
| Action-creation | One Evidence Object recording the action-creation outcome, applied Intervention Contract version, declared intent, recorded assignee pool, and trigger evaluation result | One Lineage Object per emitted Action Object recording references to the consumed Metric Snapshot versions and the applied Intervention Contract version |
| Outcome-resolution | One Evidence Object recording the comparison outcome, applied evaluation model, the preserved Metric Snapshot references the model was applied to, and the resolution disposition (resolved or forced closure) | One Lineage Object recording the explicit reference relationship between the resolution act and the applied Intervention Contract version. No new Metric Snapshot reference is recorded. |

Run-level operational references may exist for diagnostics or reporting, but they do not replace per-act Evidence or per-object Lineage for emitted or referenced Action Objects.

Per the Proof emission at every boundary section of The Evaluation Boundaries, both act types are governed acts that emit proof. The action-creation act emits a new progression object together with proof. The outcome-resolution act sets the preserved Action Object's terminal-state attributes per the Closure window and Action Object lifecycle section and emits supplementary proof at the same act; it does not emit a new progression object and does not introduce a new metric reference.

## Action Evaluation Run

The Action Evaluation Run is the tenant-scoped execution record for one Evaluator invocation at the action evaluation boundary. Under the Foundation model, one invocation corresponds to one act of one declared type. The Run records which act type the invocation performed and the act-specific outcome. The Run is tenant-scoped under DEC-771baf and is held in the tenant database.

| Property | Value |
|---|---|
| Scope | Tenant |
| Store class | Tenant action-run store in the progression-oriented tenant execution layer |
| Initiated by | Evaluator invocation against one evaluation target with one declared act type |
| Records | Intervention Contract version applied, declared act type, input references (Metric Snapshot versions for action-creation; preserved Action Object reference plus comparison input for outcome-resolution), evaluation outcome, and references to emitted proof |
| Lifecycle | Queued or running state followed by a terminal outcome state. Action-creation invocations terminate as `emitted` or `failed`. Outcome-resolution invocations terminate as `resolved`, `force_closed`, or `failed`. Action evaluation has no temporal or readiness gate, so no `gated` terminal state is emitted. |
| Retention | Append-only operational history |

DEC-771baf governs tenant ownership of execution data. DEC-f02230 and its active tenant-schema amendments govern where tenant execution records live structurally. This chapter therefore defines the Action Evaluation Run semantically and operationally; Data Model and Schema defines exact schema and table names.

The Action Evaluation Run is an operational record. It is authoritative for run accounting and invocation history. It does not replace Action Objects, Evidence, or Lineage as the authoritative outcome of action evaluation.

## Action Evaluator does not execute the action

The Action Evaluator emits Action Objects and accumulates proof against them. It does not execute the action that the Action Object represents. Operational execution is external to the platform.

| Action Evaluator does | Action Evaluator does not |
|---|---|
| Apply Intervention Contract trigger conditions, activation mode, assignee pool, closure window, and evaluation model | Execute the operational work that an Action Object directs |
| Emit one Action Object per action-creation act | Modify or replace an Action Object in response to external workflow state |
| Set the preserved Action Object's terminal-state attributes and emit supplementary Evidence and Lineage during an outcome-resolution act | Read external workflow status as authoritative resolution |
| Record forced closure when the closure window elapses | Permit an Action Object to remain non-terminal beyond the closure window |
| Write the Action Evaluation Run | Re-enter metric evaluation while resolving an outcome |

External operational systems consume the preserved Action Object as a directive. Their execution does not create, modify, or replace authoritative action state. Status from external systems is not preserved as authoritative platform state through this boundary; any preserved record of external status is a separate operational concern outside the action evaluation boundary's authority.

## Chapter boundaries

This chapter has defined the Action Evaluator, runtime application of the Intervention Contract's five body elements, the action-creation act that emits one Action Object, the outcome-resolution act that sets the preserved Action Object's terminal-state attributes and emits supplementary Evidence and Lineage, the closure window and the Action Object's set-once terminal-state lifecycle (including forced closure at window elapse), per-act proof emission, the tenant-scoped Action Evaluation Run, and the boundary between platform-governed action evaluation and external operational execution. It has deferred:

- Operational surfaces that display, assign, and track Action Objects (Frontend Experience).
- Tenant-scoped binding records that pair an Intervention Contract with environment-specific configuration, including assignee role substitution (Tenancy and Binding).
- Relational schema details and exact persistent-store names for runtime and tenant execution records (Data Model and Schema).
- API endpoints and administrative workflows for evaluator operations (API Surface).
- Compliance use of action proof chains (ISO 27001 Conformance and SOC 2 Conformance).

This chapter completes the four-boundary runtime treatment opened by Admission and Observation. Subsequent chapters describe the surfaces that consume preserved progression objects and proof, and the platform construction that hosts the runtime described here.

## References

- Platform P02 Contract Registry: Intervention Contract dossier
- the Action Object section of The Object Model: Action Object
- the Intervention Contract section of The Contract Grammar: Intervention Contract
- the Action evaluation boundary section of The Evaluation Boundaries: Action evaluation boundary
- the Proof emission at every boundary section of The Evaluation Boundaries: Proof emission at every boundary
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Tenancy and Binding: Tenancy and Binding
- Data Model and Schema
- API Surface
- Frontend Experience
- DEC-771baf: Tenant database architecture and run scope (Decisions)
- DEC-f02230: Tenant DB schema organization (Decisions)
- Contract Schemas reference
- Decisions: ADR Registry
- Errata: Errata Ledger
