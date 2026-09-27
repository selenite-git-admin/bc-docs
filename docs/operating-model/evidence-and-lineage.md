---
id: evidence-and-lineage
order: 13
title: "Evidence and Lineage"
status: drafting
authority: authoritative
depends_on: [the-object-model, the-evaluation-boundaries, admission-and-observation, canonical-evaluation, metric-evaluation, action-evaluation]
governing_sources:
  - The Object Model, Orthogonal proof objects section
  - The Evaluation Boundaries, Proof emission at every boundary section
  - Foundation §8 (evidence and lineage)
governing_adrs:
  - DEC-771baf (Tenant database architecture and run scope)
  - DEC-f02230 (Tenant DB schema organization)
  - DEC-2c79c8 (Per-tenant SQL isolation; evidence tables in tenant schemas)
  - DEC-ebb3cd (Evidence and lineage write semantics — D387: best-effort + proof_status; per-evaluation lineage cardinality). For metric evaluation its best-effort rule and `proof_status` marker are replaced by DEC-48d222; it still governs the boundaries not yet brought to the atomic posture
  - DEC-48d222 (D578: atomic proof for metric evaluation — Evidence and Lineage join the Snapshot transaction; WORM archive best-effort)
  - DEC-09fb2f (D575: tenant evidence-chain immutability and runtime identity separation)
  - DEC-fbc085 (platform-plane evidence home for contract-version governance transitions)
  - DEC-3016e4 (the fiscal-calendar window a metric proof's scope is checked against is half-open)
v2_sources:
  - system/platform/P07-evidence-lineage/index.md
  - system/platform/P07-evidence-lineage/evidence-service/index.md
  - system/platform/P07-evidence-lineage/lineage-service/index.md
  - system/foundation/patent/sections/section-08.md
---

# Evidence and Lineage

## Scope

This chapter defines the runtime treatment of the platform's two proof object types under the Foundation execution model. It consolidates the proof-emission behavior described per boundary in Admission and Observation through Action Evaluation into one treatment of Evidence and Lineage. It defines per-act emission discipline, the per-record specialization at the admission boundary, the relationship of proof emission to once-per-act evaluation, the proof chain that supports audit, the audit consumption discipline, and the retention rule that operationalizes Invariant VI. It distinguishes the two proof object types from progression objects so that proof emission and authoritative state are not conflated. It does not redefine the Object Model (The Object Model), the per-boundary contract grammar (The Contract Grammar), the evaluation boundaries themselves (The Evaluation Boundaries), the runtime components that emit proof (Admission and Observation through Action Evaluation), the relational schema for proof storage (Data Model and Schema), or the API surface for proof consumption (API Surface).

This chapter follows the authoritative Foundation reading in which Evidence and Lineage are immutable, append-only proof object types emitted synchronously with the proof-emitting act they describe.

The durability contract now differs by boundary (section Proof durability):
- **Metric evaluation is atomic** (DEC-48d222, D578). The act's Evidence and Lineage are written in the Metric Snapshot's own tenant transaction. If they cannot be written, the snapshot is not recorded: no proof, no record.
- **The other boundaries remain best-effort** per DEC-ebb3cd (D387) until their own governed units bring them to the atomic posture.
- **The `proof_status` marker is retired.** DEC-ebb3cd's durable `proof_status` marker exists in no schema, platform or tenant; the proof is read from the preserved records themselves.

Cryptographic chaining and privacy-erasure mechanisms named in the broader ADR corpus are not operationally expanded here beyond what the Orthogonal proof objects section of The Object Model and the Proof emission at every boundary section of The Evaluation Boundaries authorize. Their full runtime treatment requires corresponding updates to the Foundation spine before they become authoritative here.

## Proof artifact inventory

The platform produces two proof object types at every proof-emitting evaluation-boundary act and at the small set of additional governed acts named in the Proof emission at every boundary section of The Evaluation Boundaries. Both proof object types are tenant-scoped under DEC-771baf and held in the tenant database. Neither carries business meaning; neither participates in progression ordering.

| Proof object | Role | Scope | Persistent store |
|---|---|---|---|
| Evidence Object | Records that a proof-emitting act occurred, what was referenced, under what conditions, and with what outcome | Tenant | Tenant evidence store defined by current tenant-schema ADRs and Data Model and Schema |
| Lineage Object | Records explicit reference relationships established at a proof-emitting act | Tenant | Tenant lineage store defined by current tenant-schema ADRs and Data Model and Schema |

Both proof object types are immutable and append-only per the Evidence Object section of The Object Model and the Lineage Object section of The Object Model. They are not modified after emission; corrections take the form of new acts that produce new proof. DEC-2c79c8 isolates the proof storage tables per tenant. DEC-f02230 governs the tenant schema in which they reside.

## Evidence Object at runtime

The Evidence Object records that a proof-emitting act occurred and what its outcome was.

| Evidence concern | Runtime effect |
|---|---|
| Emission act | Evidence is emitted synchronously with the act it describes: a progression-object emission, a record-level outcome at admission, or a governed action outcome-resolution act against a preserved Action Object. For metric evaluation the write is part of the act's transaction (DEC-48d222); at the boundaries still on DEC-ebb3cd it is best-effort, and a failed write does not roll back the act. |
| Recorded content | The Evidence record captures evaluation type, inputs, outputs, evaluation context, outcome, and timestamp per the Evidence Object section of The Object Model. The exact record schema lives in the Contract Schemas reference and the relevant tenant-schema ADRs. |
| Immutability | Evidence is not modified after emission. A correction is a new act that produces a new Evidence record. Retention policy may apply to historical Evidence; modification does not. |
| Coverage | Every proof-emitting act emits at least one Evidence record. Acts that do not produce a new progression object, such as rejected admissions and action outcome resolution, still emit Evidence describing the act. Whether a given act's proof is present is read from the preserved Evidence and Lineage records, never from a marker. |

Evidence describes the act. It does not influence later evaluation. It is read by audit and by operational consumers; it is not consumed as evaluation input by subsequent boundary acts.

## Lineage Object at runtime

The Lineage Object records explicit reference relationships established at a proof-emitting act.

| Lineage concern | Runtime effect |
|---|---|
| Emission act | Lineage is emitted at the same act that establishes the reference relationship: at the act that produces a new progression object, or at any governed act that establishes a new explicit reference under the Proof emission at every boundary section of The Evaluation Boundaries. |
| Recorded scope | Lineage records direct references only: produced object to its input progression objects, produced object to the contract versions applied, or preserved object to the newly established governed reference. It does not compute transitive dependency graphs. |
| Immutability | Lineage is not modified after emission. A correction is a new act that produces new Lineage. Lineage is not rebuilt from logs after a gap. |
| Inference rule | The platform does not infer Lineage from context, derive references from execution traces, or treat surrounding state as evidence of a reference relationship. A reference that is not recorded as Lineage is not authoritatively established. |

Per the Lineage Object section of The Object Model, deeper traversal of the dependency graph is constructed from preserved direct edges by the reader. The platform does not maintain a transitive index.

## Proof durability

### Metric evaluation: atomic proof (DEC-48d222, D578)

- **Transaction.** A metric evaluation writes its Metric Snapshot rows, one `metric_evaluated` Evidence record and one `evaluated_by` Lineage record in the **same tenant transaction**. If the proof cannot be written, the whole act rolls back and no snapshot is recorded.
- **Exactly one proof pair per evaluation.** Two partial unique indexes in every tenant's evidence schema enforce it:
  - `uq_evidence_object__metric_eval_proof_subject`: one Evidence per `metric_evaluation_proof:<evaluation>` subject;
  - `uq_lineage_object__evaluated_by_target`: one `evaluated_by` Lineage per evaluation.
- **WORM archive.** Only the publication of the S3 WORM archive copy remains best-effort.

### Boundaries still on DEC-ebb3cd (D387)

Admission, canonical evaluation and action evaluation still emit proof best-effort, per DEC-ebb3cd, until their own governed units bring them to the atomic posture:
- a failed proof write does not roll back the act;
- a missing proof write is **not** inferred or reconstructed: the preserved records are the only proof, and an act without them is not authoritatively proved.

### The retired `proof_status` marker

DEC-ebb3cd recorded proof durability as a `proof_status` column (`complete` / `partial` / `degraded` / `NULL`) on the progression row. No such column exists in any platform or tenant schema: D578 retired it for metric evaluation, and it was never realized elsewhere. The chain-status integration it anticipated (`proof_degraded`) is therefore moot. Readers do not look for the marker.

### Immutability and runtime identity (DEC-09fb2f, D575)

- **Ownership and privileges.** In every tenant database, the evidence schema, its three tables and the `prevent_mutation` trigger function are owned by `bc_tenant_owner`. The served runtime login `bc_tenant_runtime` holds INSERT and SELECT only, and no EXECUTE on the trigger function.
- **Triggers.** BEFORE UPDATE/DELETE triggers refuse any change, **including by the owner**. The trigger has no bypass branch.
- **Served identity.** Since the 2026-09-27 serve move, the served process connects to tenant databases only as `bc_tenant_runtime` and to the platform only as `bc_platform_runtime`. Neither login is a superuser or holds a membership, so the process that emits proof cannot rewrite it.
- **Identity receipt.** A metric proof written in the `e6b.lineage.v2` format carries the session identity that wrote it. A proof is qualified only when that writer was `bc_tenant_runtime`, not a superuser and not a row-level-security bypasser.

### Reading a metric proof: the proof projection

The strength of a metric evaluation's proof is **derived at read time** from the preserved records by a read-only projection keyed on the Metric Snapshot. It never writes, never triggers evaluation, and never infers proof into existence. It evaluates in stages, and the first failing stage decides the outcome:

| Stage | What it checks | Failure outcome |
|---|---|---|
| Availability, existence | The snapshot, its evaluation, and the Evidence and Lineage recomputed from the evaluation's identity | `unavailable`, `missing` |
| Version and internal consistency | The lineage format version; tenant, identities, singletons and the recorded checks | `unsupported_version`, `mismatch` |
| Scope (v2) | The scope is identical in Evidence and Lineage and names the snapshot's period. The governed fiscal-calendar row was in effect at the as-of: the window is **half-open** `[effective_from, effective_to)` (DEC-3016e4), so the boundary day is outside | `mismatch` |
| Caller scope | The metric contract, period, legal entity and calendar the caller expects | `out_of_scope` |
| Version branch | A v1 proof has no scope and no identity receipt | `unqualified_legacy` |
| Identity receipt (v2) | The writer was `bc_tenant_runtime` and not privileged | `unqualified_identity` |
| Establishable | Every check could be established (for example, canonical-object period membership) | `unqualified_unverifiable` |
| Qualified | A positive conjunction: v2 and every check `passed` | `qualified` |

### Platform-plane governance evidence (DEC-fbc085)

Proof also exists on the platform plane:
- A contract version's governance-state transition (for example `active → superseded`) writes an append-only transition record through a trigger **in the same transaction** as the transition, attributed to the database principal and the request.
- The records are owned by `bc_schema_owner` and written only through the emitter trigger. The served platform login `bc_platform_runtime` holds neither UPDATE nor DELETE on them.
- This is the platform counterpart of the tenant evidence chain. It is governance evidence about contracts, not tenant proof objects.

## Per-act emission across the four boundaries

Proof emission cardinality varies by boundary because the boundaries differ in act granularity. Admission operates on batches of records and emits per-record proof for each record outcome. Canonical and metric evaluation each emit one progression object per act and emit per-act proof. Action evaluation has two governed act types with distinct proof-emission profiles.

| Boundary | Evidence emitted | Lineage emitted |
|---|---|---|
| Admission (Admission and Observation) | One Evidence record per per-record outcome (`admitted`, `quarantine`, `warn`, `log`, `block`); plus one act-level Evidence describing batch outcome where applicable | One Lineage record per emitted Source Object; rejected records emit no Lineage because no Source Object is emitted |
| Canonical evaluation (Canonical Evaluation) | One per-act Evidence recording gate, resolution, schema-conformance, and semantic-rule outcomes | One Lineage per emitted Canonical Object recording references to consumed Source Objects, applied Canonical Contract version, and applied Canonical Mapping version |
| Metric evaluation (Metric Evaluation) | Exactly one per-act `metric_evaluated` Evidence recording gate, formula, classification and scope outcomes, written in the snapshot transaction (DEC-48d222) | Exactly one `evaluated_by` Lineage **per evaluation act**, in the same transaction, recording references to the consumed Canonical Objects (or, for a composite, the consumed upstream Metric Snapshots) and the applied Metric Contract version. Per DEC-ebb3cd D-2 the cardinality is per-act, not per-snapshot: the snapshot identities emitted by the act are referenced through the lineage record's `toObjects` set. |
| Action-creation (the Action-creation act section of Action Evaluation) | One per-act Evidence recording the action-creation outcome, applied Intervention Contract version, declared intent, recorded assignee pool, and trigger evaluation result | One Lineage per emitted Action Object recording references to the consumed Metric Snapshot versions and the applied Intervention Contract version |
| Outcome-resolution (the Outcome-resolution act section of Action Evaluation) | One supplementary Evidence recording the comparison outcome, applied evaluation model, the preserved Metric Snapshot references the model was applied to, and the resolution disposition (`resolved` or `force_closed`) | One supplementary Lineage recording the explicit reference relationship between the outcome-resolution act and the applied Intervention Contract version. No new Metric Snapshot reference is recorded. |

Two consequences follow.

1. The cardinality of proof emitted at an act matches the cardinality of the authoritative outcome that the act establishes. An admission act that operates on N records emits N per-record Evidence outcomes; a canonical evaluation act that produces one Canonical Object emits one act-level Evidence and one Lineage.
2. Proof emission accompanies the act even when no new progression object is emitted. Rejected admissions emit Evidence without Lineage; outcome resolution emits supplementary Evidence and Lineage against a preserved Action Object without emitting a new progression object.

## The proof chain

Evidence and Lineage together form the proof chain for each authoritative object and for each proof-emitting act.

| Proof requirement | Object used | Result |
|---|---|---|
| Demonstrate that a boundary act occurred | Evidence Object | Boundary type, context, outcome, and timestamp are preserved. |
| Demonstrate what the boundary act referenced | Lineage Object | Direct references between produced and consumed objects, or other governed direct references established by the act, are preserved. |
| Demonstrate ancestry across acts | Evidence and Lineage together | The full chain from a current authoritative object back to its admitted source records is read by traversing preserved direct edges. |

The proof chain is preserved on the authoritative evidence chain, the storage substrate that holds the platform's tenant-scoped Evidence and Lineage records. The substrate is governed by tenant-schema ADRs and described in detail in Data Model and Schema. Tamper-detection mechanisms applied at the storage layer are operational properties of the substrate; their specific mechanisms are not enumerated here beyond what the Orthogonal proof objects section of The Object Model authorizes.

The proof chain does not replicate authoritative state. It records that authoritative state was produced, what it referenced, and under what governed contract version. Progression objects remain the carriers of business meaning; the proof chain is the carrier of audit-grade provenance.

## Audit consumption discipline

Audit reads the preserved proof chain. It does not reconstruct missing proof from surrounding state.

| Audit operation | Permitted | Behavior |
|---|---|---|
| Read an Evidence record for a known boundary act | Yes | The Evidence record is returned as preserved state. |
| Read Lineage records for a known authoritative object | Yes | Direct edges from the object are returned as preserved state. |
| Traverse the proof chain by following preserved direct edges | Yes | The reader composes deeper ancestry from preserved direct edges. The platform does not maintain a transitive index. |
| Reconstruct missing Evidence from application logs, surrounding state, or replayed operations | No | Per the Evidence Object section of The Object Model, the platform does not treat reconstructed records as authoritative proof. |
| Re-evaluate inputs to verify a recorded outcome | No | Per the Read access does not trigger evaluation section of The Evaluation Boundaries, read access does not trigger evaluation. Audit reads preserved proof and preserved progression objects; it does not re-enter any boundary. |
| Modify Evidence or Lineage to correct a recorded value | No | Per the Evidence Object section of The Object Model and the Lineage Object section of The Object Model, both proof object types are immutable. Corrections take the form of new acts. |

Audit therefore answers two distinct questions from preserved state alone: did this act occur (Evidence), and what did it reference (Lineage). Anything an audit reader cannot answer from preserved proof is treated as not authoritatively established; the platform does not synthesize missing proof under any circumstance.

## Retention and Invariant VI

Retention of Evidence and Lineage is governed at the storage layer. Retention policy may apply over time. The execution-model status of an act, however, is determined by whether proof exists on the authoritative evidence chain, not by retention configuration.

| Retention rule | Effect on authoritative status |
|---|---|
| Evidence and Lineage are emitted with the act | Per the Proof emission at every boundary section of The Evaluation Boundaries, the Orthogonal proof objects section of The Object Model, DEC-48d222 (metric evaluation: in the act's transaction) and DEC-ebb3cd (other boundaries: best-effort), the act is authoritatively proved when its preserved Evidence and Lineage records exist. For a metric evaluation, the proof projection reports how strong that proof is. |
| Retention policy preserves Evidence and Lineage over a declared period | The act remains authoritatively proved while its preserved proof records exist. |
| Retention policy ages Evidence or Lineage out of the authoritative evidence chain | Per the Orthogonal proof objects section of The Object Model and Invariant VI, the platform does not treat the act as authoritatively proved for audit. Consumers observe aged-out proof as the absence of preserved Evidence and Lineage records; nothing is rewritten on the progression row. |
| Storage failure removes Evidence or Lineage outside retention policy | The same rule applies. Recovery that restores the preserved proof records restores authoritative auditability; reconstruction that synthesizes new records does not. |

Invariant VI therefore governs audit authority through preserved proof. The platform emits proof at the act. Audit reads what the authoritative evidence chain preserves. Missing proof is not inferred, replayed, or reconstructed into authoritative status.

## Chapter boundaries

This chapter has consolidated Evidence and Lineage as the platform's two proof object types under the current Foundation reading: per-act emission discipline, the per-record specialization at the admission boundary, the proof chain that links progression objects across boundaries, the audit consumption discipline that reads preserved proof and never reconstructs, and the retention rule that operationalizes Invariant VI. It has deferred:

- Cryptographic chaining of Evidence records and runtime mechanisms for tamper detection, pending ADR adoption against Foundation.
- Sentinel-based privacy erasure that extends the Evidence chain for personal-data nullification, pending Foundation update.
- Tenant-scoped binding records that pair retention policy with environment-specific configuration (Tenancy and Binding).
- Relational schema details and exact persistent-store names for proof storage (Data Model and Schema).
- API endpoints and administrative workflows for proof consumption and export (API Surface).
- Compliance use of the proof chain for ISO 27001 and SOC 2 conformance (ISO 27001 Conformance and SOC 2 Conformance).

Subsequent chapters describe how the proof chain is consumed by tenant-scoped surfaces and the platform construction that hosts the storage substrate.

## References

- the Evidence Object section of The Object Model: Evidence Object
- the Lineage Object section of The Object Model: Lineage Object
- the The proof chain section of The Object Model: The proof chain
- the Proof emission at every boundary section of The Evaluation Boundaries: Proof emission at every boundary
- the Read access does not trigger evaluation section of The Evaluation Boundaries: Read access does not trigger evaluation
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Action Evaluation: Action Evaluation
- Tenancy and Binding: Tenancy and Binding
- Data Model and Schema
- API Surface
- ISO 27001 Conformance
- SOC 2 Conformance
- DEC-771baf: Tenant database architecture and run scope (Decisions)
- DEC-f02230: Tenant DB schema organization (Decisions)
- DEC-2c79c8: Per-tenant SQL isolation; evidence tables in tenant schemas (Decisions)
- DEC-ebb3cd: Evidence and Lineage write semantics (D387) (Decisions)
- DEC-48d222: Atomic proof for metric evaluation (D578) (Decisions)
- DEC-09fb2f: Tenant evidence-chain immutability and runtime identity separation (D575) (Decisions)
- DEC-fbc085: Platform-plane evidence home for contract-version governance transitions (Decisions)
- DEC-3016e4: Fiscal-calendar window is half-open (Decisions)
- Foundation: Evidence and lineage specification
- Contract Schemas reference
- Decisions: ADR Registry
- Errata: Errata Ledger
