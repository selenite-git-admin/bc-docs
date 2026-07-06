---
id: chain-completeness-and-verdict
order: 15.5
title: "Chain Completeness and Verdict"
status: drafting
authority: authoritative
depends_on: [the-authority-model, the-contract-grammar, the-object-model, business-vocabulary, contract-chain-assembly, quality-gates-and-chain-integrity, sources-and-the-catalog, connectors-and-readers, admission-and-observation, canonical-evaluation, metric-evaluation, metric-catalog, tenancy-and-binding]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Authority Model
  - The Contract Grammar
  - Contract Chain Assembly
  - Quality Gates and Chain Integrity
  - Metric Evaluation
governing_adrs:
  - DEC-bebaec (Chain Completeness SSOT; Definition of Complete plus persisted chain status)
  - DEC-bef347 (Structural Completeness; required body keys per contract family)
errata_referenced: []
v2_sources: []
---

# Chain Completeness and Verdict

## Scope

This chapter defines chain completeness as the platform's locked answer to the question "can this metric compute against its sources." It defines the per-variable seven-link resolution chain that each Metric Contract input variable must traverse, the per-contract structural and governance checks that each contract on the chain must satisfy, the end-to-end checks that bind variable-level and contract-level results into a single chain verdict, the chain verdict set the platform recognizes, the persisted chain-status store that holds the verdict per Metric Contract version as a single source of truth, the separate tenant/source readiness record that answers whether a tenant Source System can feed that complete chain for a selected readiness read, the version model under which chain status is computed (single active per contract with a transition window), the read-only nature of the chain integrity check, and the boundary that separates chain integrity from runtime act outcomes.

This chapter does not redefine the contract grammar (The Contract Grammar), the contract chain itself (Contract Chain Assembly), the runtime acts at the four boundaries (Admission and Observation through Action Evaluation), the Quality Gates that govern authoring acts (Quality Gates and Chain Integrity governs gate execution), the metric catalog lifecycle (Metric Catalog), or the relational storage layout for the chain-status persisted store.

The chain integrity check is read-only. It does not produce authoritative state. It does not run as part of the four boundary acts. It is consulted by metric activation gates and by tenant-facing readiness reads, and it is computed by a registry-side service whose rebuild is event-driven on contract authoring acts. Per Foundation, the platform's authoritative state is produced only at the four evaluation boundaries; chain status is platform governance metadata about whether those boundaries can produce authoritative state, not a fifth boundary.

**Governing source.** Foundation; The Contract Grammar; Contract Chain Assembly; DEC-bebaec.

## Definition of Complete

The platform's definition of complete has three orthogonal layers. The first two layers determine the global chain verdict for one Metric Contract version. The third layer determines tenant/source readiness against a globally complete chain.

| Layer | Scope | What it checks |
|---|---|---|
| Per-variable resolution chain (L1-L7) | Each Metric Contract input variable | The variable resolves through seven explicit links from formula identifier to a registered source field, with each link governed by the relevant contract or catalog record. |
| Per-contract checks (C1-C5) | Each contract on the chain that the variable traverses | The contract exists, is governance-active, has the required body keys, has passed its quality gates, and has its bindings populated. |
| Tenant/source readiness check (E3) | Each tenant Source System combination for a Metric Contract version | A specific tenant Source System has the active set of contracts and reader binding required for live evaluation. |

The layers are independent failure axes. A variable may pass L1-L7 while a per-contract check fails on the same chain (for example, a variable that resolves end-to-end but whose Canonical Contract version has been governance-archived). A contract may pass all per-contract checks while a variable that depends on it fails L1-L7 (for example, a Canonical Contract version that is fully active but whose Canonical Field mapping for one specific variable is missing). Tenant/source readiness is evaluated after the global chain verdict; it does not change the global Metric Contract version verdict.

**Governing source.** DEC-bebaec; The Contract Grammar; Contract Chain Assembly.

## The L1-L7 Variable Resolution Chain

Every Metric Contract input variable must traverse seven explicit links. A break at any link means the metric cannot evaluate that variable.

| Link | Resolution claim | Governed by |
|---|---|---|
| L1 | A Canonical Field is registered under the variable's field name. | Business Vocabulary; Canonical Field registry |
| L2 | The Canonical Field is mapped to a Business Field for the relevant Canonical Contract version, recorded in the Canonical Contract's field-mapping body. | The Contract Grammar (Canonical Contract section) |
| L3 | The Business Field exists in the Canonical Contract version's resolved schema. The match is exact; suffix matches and partial matches are not admissible. | The Contract Grammar; Business Vocabulary |
| L4 | The Business Field is mapped to a source field through the Observation Contract's field-mapping body. The aggregation is over every Observation Contract bound to the relevant Business Object, not the first Observation Contract that resolves. | Admission and Observation; The Contract Grammar (Observation Contract section) |
| L5 | An Admission Contract version covers the source table that supplied the L4 mapping. The check is per source field, not per Canonical Contract; the Admission Contract for the specific source table providing the L4 mapping is the contract that must be active. | Admission and Observation; The Contract Grammar (Admission Contract section) |
| L6 | The Observation Contract names a Reader that is governance-active and bound. | Connectors and Readers |
| L7 | The source field on the chain is registered in the Source Catalog. This is a governance gate; the chain trace records the catalog reference for audit. | Sources and the Catalog |

Computed Business Fields (Business Fields whose value derives from other Business Fields, not from a source field) traverse L1 through L3 normally and record L4 as resolved with the source-field reference set to the computed sentinel value. Computed Business Fields are an explicit case in the resolution chain, not a bypass.

The chain is per-variable per Canonical Contract version, since the same variable may resolve differently against different Canonical Contract versions of the same canonical model. The chain trace persists the variable's resolution per (Metric Contract version, variable, Canonical Contract version) so that supersession of any contract on the chain produces a new trace under the new version, while prior traces remain readable.

**Governing source.** Contract Chain Assembly; The Contract Grammar; Sources and the Catalog; Admission and Observation; Connectors and Readers; DEC-bebaec.

## Per-Contract Checks

Each contract on the chain must satisfy five governance and structural checks.

| Check | Claim | Governed by |
|---|---|---|
| C1 | The contract exists in the registry and is not archived. | The Contract Grammar; The Authority Model |
| C2 | The contract's governance state is `active`, or the contract is within the transition window established when a successor was activated. | The Contract Grammar; version model below |
| C3 | The contract carries the required body keys for its family per DEC-bef347 (Structural Completeness). Required keys vary by contract family and are governed by the family's master schema. | DEC-bef347; The Contract Grammar |
| C4 | The contract has passed the Quality Gates that the family declares applicable at activation. The gate verdicts are read from the gate-result records on the contract version; this chapter does not re-evaluate gates. | Quality Gates and Chain Integrity |
| C5 | The contract's bindings are populated. For Canonical Contracts, every Business Field declared in the field-selection body has a Canonical Field mapping. For Metric Contracts, every formula variable is bound to a registered Canonical Field through the metric's Canonical Object bindings. | The Contract Grammar (Canonical Contract section, Metric Contract section) |

The five per-contract checks are read against the contract's registry record. They are not re-derived from primary contract content at chain-status computation time; they consume the governance and gate-result records that the contract authoring acts produced.

**Governing source.** The Contract Grammar; The Authority Model; DEC-bef347; Quality Gates and Chain Integrity.

## End-to-End Chain Checks

Three end-to-end checks aggregate per-variable, per-contract, and tenant/source readiness results.

| Check | Claim | Persisted grain |
|---|---|---|
| E1 | Every Metric Contract input variable passes L1-L7 with zero broken links. | Metric Contract version |
| E2 | Every grain Canonical Field declared by the Metric Contract has a Canonical Field mapping in every Canonical Contract bound by the Metric Contract. The check is per (grain Canonical Field, bound Canonical Contract) pair, not per metric. | Metric Contract version |
| E3 | At least one tenant Source System combination has the active set required for live evaluation: an active Source Contract, an active Admission Contract, an active Observation Contract, a bound Reader, and field-mapping records that resolve the chain's source-side claims. | Tenant, Source System, Metric Contract version |

E1 binds variable-level results into a metric-level verdict. E2 verifies grain coverage independent of variable resolution because grain may be declared on Canonical Fields that the metric does not name as input variables. E3 verifies whether a tenant Source System combination can produce the Canonical Objects the metric requires for the selected readiness read. E3 is a tenant/source readiness result; it is not folded into the global `contract.chain_status` verdict.

**Governing source.** DEC-bebaec; The Contract Grammar; Connectors and Readers; Admission and Observation.

## Chain Verdict

The platform recognizes four chain verdicts. The verdict is computed per Metric Contract version and recorded in the persisted chain-status store.

| Verdict | Condition | Operational meaning |
|---|---|---|
| `complete` | E1 and E2 hold, and no L1-L7 break or C1-C5 failure applies. | The Metric Contract version is structurally ready. A tenant/source readiness record is still required before live evaluation can proceed for a specific tenant Source System. |
| `partial` | At least one input variable breaks at L4, L5, L6, or L7, and no L1-L3 break or `unlinked` condition applies. | The chain is structurally sound at the contract level (L1-L3 pass) but source-side wiring or catalog registration is incomplete. The fix is data, mapping, reader, or source-catalog authoring, not metric formula revision. |
| `broken` | At least one input variable breaks at L1, L2, or L3, or a C1-C5 per-contract failure blocks a traversed contract. | The contract chain itself has a structural or governance problem that contract revision, activation, or quality-gate remediation must address. |
| `unlinked` | The Metric Contract's Canonical Object bindings reference Canonical Contracts that do not exist in the registry. | The metric is not connected to the chain at all and cannot be evaluated until its bindings are repaired. |

The verdict reading is hierarchical: `unlinked` overrides `broken`, `broken` overrides `partial`, and `partial` overrides `complete`. A metric whose chain has both L2 breaks and L5 breaks is `broken`, not `partial`, because the structural break is the more fundamental gap.

The verdict is the authoritative platform-chain readiness signal for one Metric Contract version. It is consumed by the metric activation gate, by chain-status governance reports, and by tenant/source readiness reads as the platform-chain prerequisite.

**Governing source.** DEC-bebaec; Metric Evaluation.

## Persisted Chain Status

Per DEC-bebaec, chain status is held in persisted records that together form the platform's single source of truth for chain readiness.

| Record | Grain | Content |
|---|---|---|
| Chain trace | Per (Metric Contract version, input variable, Canonical Contract version) | The L1-L7 result for every variable in every Metric Contract version, with the provenance of each resolved link (which Observation Contract, which Admission Contract, which Reader, which source field). |
| Chain status | Per Metric Contract active version | Aggregated variable counts (complete, partial, broken), the E2 grain check result, per-contract check results, and the resulting global chain verdict. |
| Tenant/source readiness | Per (tenant, Source System, Metric Contract version) | The E3 live-source check result for a specific tenant Source System combination, with references to the Source Contract, Admission Contract, Observation Contract, Reader Binding, and source-side field mappings that make live evaluation possible. |

The chain-status records are platform registry metadata. They are not tenant runtime state and they are not part of the proof chain. The tenant/source readiness record is tenant-scoped governance metadata; it is still not runtime proof, and it does not replace admission, canonical evaluation, or metric evaluation Run records.

Reads against the global chain-status store return the persisted Metric Contract version verdict. Reads against tenant/source readiness return the persisted E3 result for a specific tenant Source System combination. Neither read triggers a rebuild at read time. Rebuild of the persisted stores is event-driven on contract authoring acts (contract activation, Canonical Contract field-mapping changes, Observation Contract field-mapping changes, reader binding changes) and is also available on-demand through a governance endpoint. Stale reads between an authoring act and the next rebuild are an operational concern of the rebuild discipline, not a correctness concern of the chain definition.

The deprecated stateless integrity check that earlier sessions used to compute chain status from scratch is not the source of truth. The platform records the persisted stores as the SSOT and treats any other computation as an independent cross-check, useful for audit but not authoritative.

**Governing source.** DEC-bebaec; The Authority Model.

## `break_summary_json.reason_code` — extensibility surface for semantic causes

The chain status row's `break_summary_json` is a structured jsonb payload. Its readiness-baseline content is aggregated per-link break counts (for example, the count of variables broken at L4, L7, etc.). The four-verdict enum (`complete | partial | broken | unlinked`) is stable and is the authoritative readiness signal; the verdict is not extended.

Per DEC-952faa (D386) and DEC-ebb3cd (D387), `break_summary_json` is also the documented surface for **structured semantic causes**, carried as a `reason_code` string field. The cause ride alongside the aggregated counts; the field is non-exhaustive and additive, so future causes can be added without verdict-enum churn or schema migration. Readiness-baseline state of the planned reason codes:

| Reason code | Source | Trigger | Readiness-baseline status |
|---|---|---|---|
| `semantic_class_mismatch` | DEC-952faa D-2 | An existing chain-complete Metric Contract version fails the `temporality_kind` ↔ formula primitive compatibility gate at chain-status refresh time. | Authoring-time gate ships in D386 Stage 1 (TSK-9a0d7b, completed). The refresh-time integration that surfaces this `reason_code` into `break_summary_json` is **not yet implemented**; it depends on a separate scanner task that has not been filed. The reason name appears in authoring-rejection error messages in the readiness baseline, but it is not written to `break_summary_json` by `ChainStatusService`. |
| `proof_degraded` | DEC-ebb3cd D-1 | A Metric Contract version's contributing tenant progression rows carry `proof_status='degraded'` (one or more proof writes failed during the act). | `proof_status` is persisted on tenant progression rows in D387 Stage 1 (TSK-3d7c4f, completed). The chain-status integration that reads `proof_status` and writes `reason_code='proof_degraded'` is **deferred** under TSK-296271 because `ChainStatusService` is platform-DB scoped and reading tenant progression rows from it would breach the platform/tenant DB one-way-dependency invariant (DEC-771baf, DEC-f02230). Three alternative integration designs are recorded on TSK-296271; none is selected in the readiness baseline, and no `proof_degraded` reason code is emitted by the chain-status compute path. |

In Stage-1 ground truth, `break_summary_json` written by `ChainStatusService` contains aggregated break counts only; no `reason_code` value is emitted in the readiness baseline. Documenting the extensibility surface in this chapter locks the contract so that the future scanners and integration paths emit the same field name and the same reason-code values, regardless of which integration design TSK-296271 ultimately selects. Readers that consume `break_summary_json` should treat `reason_code` as an optional, non-exhaustive string field.

**Governing source.** DEC-bebaec (the verdict taxonomy is stable); DEC-952faa D-2 and DEC-ebb3cd D-1 (the reason_code values and their triggers); TSK-296271 (the deferred D387 integration design).

## Version Model and Transition Window

Per DEC-bebaec, the version model that chain integrity computes against is single-active with a transition window.

| Property | Rule |
|---|---|
| Steady state | At most one version per contract is governance-active at any time. The chain trace and chain status are computed against this active version. |
| Transition activation | When a new version is activated, the prior active version receives a transition expiry timestamp 48 hours forward. Both versions are governance-active during the transition window. |
| During transition | The chain trace is computed against both active versions independently. The chain-status store carries an entry per active version; consumers see both verdicts and can route to the correct version at runtime. |
| End of transition | The expired prior version is auto-superseded at the registered transition expiry. The chain-status record for the expired version is no longer reported as active after the next rebuild, but the historical chain trace and status record remain readable. |
| Enforcement | The single-active rule is enforced at the application layer through the activation discipline, not at the database constraint level. The relaxation supports the transition window without requiring a temporary constraint suspension. |

The transition window prevents the operational hazard of strict single-active enforcement (no co-existence permitted, so version migrations require synchronized cuts) and the correctness hazard of unrestricted multi-active versions (chain status ambiguous between versions). Forty-eight hours is the platform-declared window; the value is governance-recorded on DEC-bebaec rather than declared per Metric Contract.

The version model interacts with the per-contract C2 check: a contract is governance-active for the purpose of C2 if its governance state is `active` or if it is within its transition window. Outside the transition window, only the `active` state satisfies C2.

**Governing source.** DEC-bebaec; The Contract Grammar; The Authority Model.

## Read-Only Validation

The chain integrity check is read-only across every dimension that matters.

| Dimension | Operational form |
|---|---|
| No mutation of authoritative state | The check does not produce, modify, or replace Source Objects, Canonical Objects, Metric Snapshots, or Action Objects. |
| No mutation of contract content | The check reads contract registry records as governance authored them. It does not amend, repair, or re-derive contract bodies. |
| No mutation of proof | The check does not emit Evidence or Lineage. The proof chain is a runtime concern; chain integrity is a registry concern. |
| Rebuild is event-driven, not act-driven | The chain-status persisted store rebuilds when contract authoring acts change the chain's content. It does not rebuild as a side effect of admission, canonical evaluation, metric evaluation, or action evaluation. |
| Reads do not trigger recomputation | A read of the chain-status persisted store returns the persisted verdict without invoking a fresh computation. |

The read-only discipline is the architectural reason chain integrity is not a fifth evaluation boundary. The four evaluation boundaries produce authoritative state. Chain integrity describes whether the boundaries can produce that state; it does not produce state itself.

**Governing source.** Foundation; The Object Model; DEC-bebaec.

## Boundary: What Chain Integrity Is Not

Three concepts have been confused with chain integrity in earlier readings. The boundary makes each distinction explicit.

| Concept | Relation to chain integrity |
|---|---|
| Quality Gates at authoring acts | Quality Gates evaluate authoring acts and produce gate verdicts on contract versions. Chain integrity reads the gate verdicts as a per-contract check (C4); it does not re-evaluate gates. The gate is the authoring concern; chain integrity is the assembled-chain concern. |
| Tenant runtime telemetry | Tenant runtime telemetry counts admission outcomes, evaluation invocations, and similar runtime acts at the tenant scope. Chain integrity is platform registry metadata about contract chain readiness. The two stores are separate; the runtime telemetry store is not the chain-integrity SSOT and the chain-integrity store is not runtime telemetry. |
| Per-act preconditions | Each runtime act has its own precondition discipline (subscription consultation, contract version resolution, fiscal calendar resolution). The act may consult chain status as one input among many, but the act's success or failure is recorded on the runtime Run record, not on the chain-status store. Chain status is the readiness reading at registry scope; the Run record is the outcome reading at runtime scope. |

The boundaries are uniform. An act that mutates state under chain integrity authority violates the discipline. A read that derives runtime telemetry from chain status confuses scopes. A Quality Gate re-evaluation done as part of chain status overlaps the authoring act's responsibility.

**Governing source.** Foundation; Quality Gates and Chain Integrity; DEC-bebaec.

## Constraints

The constraints below apply uniformly to chain integrity computation, persistence, and consumption.

| Constraint | Operational form |
|---|---|
| One source of truth | The persisted chain-status store is the single source of truth for global chain readiness. The tenant/source readiness store is the single source of truth for E3 readiness at tenant Source System grain. Other computations are independent cross-checks; they do not override either SSOT. |
| Per Metric Contract version | The global verdict is recorded per Metric Contract version. Supersession does not silently advance the verdict; the new version receives its own chain trace and chain status entry. |
| Tenant/source readiness is separate | E3 is recorded per tenant Source System combination. A complete global chain does not imply that every tenant Source System is ready, and a ready tenant Source System does not change the global chain verdict. |
| Read-only at runtime | Runtime acts read chain status and tenant/source readiness; they do not write to either store. The persisted stores are updated only by the chain-status service in response to contract authoring events or on-demand rebuild. |
| No bypass of authoring | A chain-status update is the consequence of a governed authoring act. There is no path to update chain status without the originating authoring act being recorded. |
| Definition is locked | The L1-L7 chain, the C1-C5 per-contract checks, the E1-E3 end-to-end checks, and the four-verdict set are governed by DEC-bebaec. Changes to the definition are governance acts under that ADR's supersession discipline, not session-by-session interpretations. |
| Computed Business Fields are explicit | A computed Business Field records L4 as resolved with the source-field reference set to the computed sentinel value. The chain trace distinguishes source-field-resolved variables from computed-field-resolved variables; the verdict treats both as resolved. |

**Governing source.** DEC-bebaec; The Authority Model; Foundation.

## Failure Modes

Chain integrity failure modes are classifications of break in the chain, not failures of the integrity check itself. Each failure is recorded on the chain trace (per variable) and aggregated into the chain status (per Metric Contract version). Tenant/source readiness failures are recorded on the tenant/source readiness record.

| Failure | Where it surfaces | Verdict effect |
|---|---|---|
| Canonical Field absent for a variable's field name | L1 | Variable contributes a `broken` count; verdict moves to `broken`. |
| Canonical Contract field mapping missing for a Canonical Field | L2 | Variable contributes a `broken` count; verdict moves to `broken`. |
| Business Field not present in the Canonical Contract version's resolved schema (suffix match attempted, exact match required) | L3 | Variable contributes a `broken` count; verdict moves to `broken`. |
| Observation Contract field mapping missing for a Business Field | L4 | Variable contributes a `partial` count; verdict moves to `partial` if no L1-L3 break exists. |
| Admission Contract not active for the source table providing the L4 mapping | L5 | Variable contributes a `partial` count. |
| Reader not bound or not active on the relevant Observation Contract | L6 | Variable contributes a `partial` count. |
| Source field absent from the Source Catalog | L7 | Variable contributes a `partial` count; the chain trace records the missing catalog reference for governance follow-up. |
| Contract version archived or governance-inactive outside the transition window | C1 or C2 | Per-contract failure; contracts that are inputs to L1-L7 propagate the failure to variables that depend on them. |
| Required body keys missing per DEC-bef347 | C3 | Per-contract failure recorded on the contract; chain trace marks the contract as not-complete for the variable. |
| Quality Gate verdict missing or red on the contract version | C4 | Per-contract failure; the chain trace records the gate verdict reference. |
| Bindings incomplete (Canonical Contract field-selection without Canonical Field mapping; Metric Contract variables without Canonical Object bindings) | C5 | Per-contract failure; for Metric Contracts this surfaces as `unlinked` if the bindings reference non-existent Canonical Contracts. |
| Grain Canonical Field lacks Canonical Contract field mapping in a bound Canonical Contract | E2 | Aggregate end-to-end failure; the verdict cannot be `complete` even if E1 passes for input variables. |
| No tenant Source System has the full active SC, AC, OC, Reader, and field-mapping set | E3 | Tenant/source readiness failure. The global chain verdict is unchanged; the tenant/source readiness record is not ready for the affected tenant Source System combination. |
| Metric Contract's Canonical Object bindings reference Canonical Contracts not in the registry | C5; surfaced as verdict | The verdict is `unlinked`, dominating other classifications. |
| Stale chain status read between an authoring act and the next rebuild | Operational concern of the rebuild discipline | The persisted store is updated on the next event-driven or on-demand rebuild. Stale reads are not silently treated as fresh; the platform's rebuild discipline records the staleness window. |

The failure-mode table is the platform's read of chain breaks. A chain integrity result records the failure classification, the link or check at which it was detected, and the provenance reference (Canonical Field identifier, Canonical Contract version, Observation Contract reference, Admission Contract reference, Reader reference, source field reference) so that authoring acts can address the specific break the verdict reflects.

**Governing source.** DEC-bebaec; DEC-bef347; The Contract Grammar; Quality Gates and Chain Integrity.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- The Authority Model: The Authority Model
- Business Vocabulary: Business Vocabulary
- Contract Chain Assembly: Contract Chain Assembly
- Quality Gates and Chain Integrity: Quality Gates and Chain Integrity
- Sources and the Catalog: Sources and the Catalog
- Connectors and Readers: Connectors and Readers
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Metric Catalog: Metric Catalog
- Tenancy and Binding: Tenancy and Binding
- DEC-bebaec: Chain Completeness SSOT; Definition of Complete plus persisted chain status
- DEC-bef347: Structural Completeness; required body keys per contract family
- Decisions: ADR Registry
