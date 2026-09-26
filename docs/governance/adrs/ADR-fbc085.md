---
uid: DEC-fbc085
title: "Platform-plane evidence home for contract-version governance transitions (Inv VI): an append-only transition record written by a trigger in the same transaction"
description: "Canonical/observation contract-version state changes emit an append-only contract.{family}_contract_version_transition row from a DB trigger in the same transaction, fail-closed on a missing declared cause; the dead tenant-plane EvidenceService calls in Contract/Connection/Reader services are deleted; a class rule and an architecture gate cover every governed state column"
status: proposed
date: 2026-09-26T07:49:02.301Z
project: bc-core
domain: contracts
subdomain: contracts/governance
focus: evidence
---

# Platform-plane evidence home for contract-version governance transitions (Inv VI): an append-only transition record written by a trigger in the same transaction

## Context

Grounded read-only on 2026-09-26 (bc-core origin/main 8cc52c7d; bc_platform_dev in BEGIN READ ONLY):
- No existing platform record captures contract-version governance transitions. The state is UPDATEd in place (`contract-version.repository.ts` updateVersionState; `contract-analytics.repository.ts` bulkTransition). `trg_cv_immutable` freezes only `contract_json` and `version_code`. The `*_contract_approval` tables hold 0 rows, are mutable and have no writer on the transition path.
- `contract.certification_record` is frozen (deny-all). `bcf.certification_record` records BCF registry primitives. `metric_audit.transition_evidence` is MCF-only (FK to the MCV). `operations.activity_log` is mutable, generic JSON with 2 rows. `schema_provisioner.provisioning_command_transition` is append-only but records provisioning commands, not the governance act.
- Ratification (option a) is therefore not available.

Rejected alternatives:
- Restoring the tenant EvidenceService: it bubbles request scope into about 30 platform providers and 500s every platform contract route, it is the wrong plane, and it was never same-transaction.
- Reusing MCF, BCF or activity tables: wrong subject, FK and mutability.
- One polymorphic table without an FK: breaks D162 rule 3.
- An application-only insert: it does not guard the class, because bulk, script and hand-SQL writers bypass it.

The trigger-plus-declared-cause design reuses proven patterns: `mcf.fn_mcv_revision_emit` (trigger-emitted history), `runtime.connection_tenant_assignment_event` (append-only, subject and correlation id), `runtime.admission_run_disposition` (a same-transaction operator disposition) and `infrastructure.fn_reject_mutation`. The scope is narrowed to the two families the 7c-c lifecycle touches; the rest is baselined under the class gate.

## Decision

Design act for TSK-56c689 (Invariant VI: evidence is emitted, not inferred). Full design, grounding and DBCP: bc-docs docs/evidence/dbcp/implementation/contract-version-transition-evidence-dbcp.md.

1. **Evidence home (platform plane).** Each governance-state change of a canonical or observation contract version is recorded in an append-only table in the same `contract` schema and database as the version it describes: `contract.canonical_contract_version_transition` and `contract.observation_contract_version_transition`. There is one table per family so that each has a real composite foreign key `(…_contract_id, version_code)` to its version table (D162 rule 3).

2. **Emitted, not inferred.** An `AFTER INSERT OR UPDATE OF governance_state_code` row trigger on the version table writes the transition row. On UPDATE it fires only when the state actually changes; on INSERT only when a version is born in a state other than `draft`. The row therefore commits or rolls back with the state change itself, with no reconstruction afterwards. It records:
   - from/to state;
   - a declared cause code;
   - the authenticated subject and request correlation id, when the writer has them;
   - the DB principal;
   - the transaction id;
   - the SHA-256 of `contract_json` as it was at the transition.

3. **Fail-closed on an undeclared cause.** The writer declares the cause with transaction-local settings (`set_config('bc.transition_cause', …, true)`, plus the subject, the correlation id and, for operator SQL, a rationale of at least 40 characters) in the same transaction as the UPDATE. If the cause is missing or not in the CHECK list, the trigger raises, and the state change is refused. No path can change these states without evidence: the governed service path, bulk transition, scripts and hand SQL all have to declare a cause.

4. **Append-only.** UPDATE and DELETE on the transition tables are rejected by the existing `infrastructure.fn_reject_mutation()`, the same pattern as `runtime.connection_tenant_assignment_event`.

5. **Writers.** `ContractVersionRepository.updateVersionState` and `ContractAnalyticsRepository.bulkTransition` run the context `set_config` and the UPDATE in one transaction, opening one when the caller passes no executor. `ContractService.transitionState` carries a required cause and an optional actor, and each caller names its cause (governed request, provisioning readiness, authoring chain, bulk transition).

6. **Dead calls deleted.** The three dead `EvidenceService` injections (ContractService #7, ConnectionService #3, ReaderService #4) and their fire-and-forget `recordEvidence`/`recordLineage` helpers are deleted, and the #830 baseline shrinks to empty. Restoring them is rejected: even while they were alive, they wrote to the TENANT data plane after the state write, outside its transaction, with errors swallowed. They never met Inv VI.

7. **Class rule.** Any platform-plane column that carries a governed lifecycle state (`governance_state_code`, `status_code` on a governed version) must have its transitions emitted by an append-only, same-transaction record that fails closed on an undeclared cause. Evidence for platform acts never goes through the tenant-plane EvidenceService. It is enforced by a bc-core architecture gate that reads the catalog: every such table must carry the emit trigger. The gate starts with a SHRINK-ONLY baseline naming source/admission/ai/intervention contract versions, connection status, reader-binding re-point and admission-run completion, each bound to a follow-up task.

8. **No backfill.** Transitions from at least 2026-04-07 until the trigger is applied have no evidence, and none before that met Inv VI either. The gap is disclosed, not reconstructed.

9. **Sequencing.**
   1. The code PR (declares causes; harmless without the trigger) lands in the combined serve move.
   2. The DDL is applied after the operator's yes, through the committed-DBCP gate.
   3. A clone rehearsal proves one row per transition, rollback leaves none, a missing cause refuses, UPDATE/DELETE is refused, and the arch gate goes red on removal.
   4. Only then does the 7c-c lifecycle (activate cc-dh5d9 1.6.0, supersede CC 1.5.0 and OC 1.2.0) run.
