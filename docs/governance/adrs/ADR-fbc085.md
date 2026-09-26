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

2. **Emitted, not inferred, by one restricted producer.** The last `BEFORE INSERT OR UPDATE` row trigger on each version table (`trg_zz_<family>_contract_version_transition_emit`) calls `contract.fn_contract_version_transition_emit(family)`. This is a `SECURITY DEFINER` function (`search_path=pg_catalog`) owned by a new NOLOGIN role, `bc_contract_evidence_emitter`, which is the **only** holder of INSERT on the transition tables.
   - It fires on UPDATE only when the state actually changes, and on INSERT only when a version is born in a state other than `draft`. The row commits or rolls back with the state change.
   - Each row records: from/to state; the declared cause and actor kind; the subject and, for HTTP, the correlation id; the rationale for operator SQL; the SHA-256 of `contract_json` as PostgreSQL jsonb text (`pg-jsonb-text-utf8`); and an identity `transition_seq` (the emission order).
   - A BEFORE INSERT guard on the transition tables refuses any insert that is not from the emitter, from inside the version-table trigger. It cross-checks the version row as it stands before the write (`from_state`, or absent for a birth). It **re-derives** `db_principal_name`, `transaction_id` and `recorded_at` rather than taking them from the inserter.

3. **The declaration is carried by the row write itself.** There is no session state. Each governed version table has a transient column `transition_declaration_json` (`CHECK … IS NULL`). The writer sets it in the same UPDATE/INSERT that changes the state.
   - The emitter is the last BEFORE ROW trigger (`trg_zz_<family>_contract_version_transition_emit`, SECURITY DEFINER). It reads the value, NULLs it, and for a real transition requires a well-formed declaration (cause, actor_kind, subject, correlation, rationale only) before emitting.
   - A write without a value is refused, whatever came before it in the transaction, DO block, function or savepoint. A rolled-back write takes its value with it. The value never persists.
   - A bulk UPDATE's value covers exactly the rows that one statement writes. Compound statements attribute each row from its own write, or refuse an undeclared sibling.
   - The evidence FK is DEFERRABLE INITIALLY DEFERRED, so a birth is evidenced before its row is written and still checked at commit.
   - Actor kinds and required identity: `authenticated_http` needs the subject and correlation id; `service_system` needs the component subject; `operator_sql` needs the subject and a rationale of at least 40 characters. These are writer assertions, not authentication or authorization.

4. **Append-only, TRUNCATE included; least-privilege served identity is a prerequisite.**
   - `BEFORE UPDATE OR DELETE OR TRUNCATE … FOR EACH STATEMENT` uses `infrastructure.fn_reject_mutation()`.
   - No ordinary principal holds, or inherits, any write privilege, owner membership or emitter membership.
   - The NOLOGIN owner `bc_schema_owner` deliberately keeps its owner (recovery/migration) authority and has no members. Using it is an explicit HALT/evidence-gap disposition.
   - **Prerequisite (Codex Q5 ruling):** the database-capability slice of D575 W6-P (TSK-1a240c, executed as TSK-fa31e7), with its own DBCP and gate:
     - the served bc-core platform login (`bc_platform_runtime`) is non-superuser and owns neither the `contract` schema, the version tables, the evidence tables nor the emitter;
     - the served process holds **no superuser credential for the cluster**, including its tenant URL (W6).

     Today the served login is a superuser and owns all of these.

5. **Writers.**
   - `ContractVersionRepository.updateVersionState` and `ContractAnalyticsRepository.bulkTransition` set `transition_declaration_json` in the same UPDATE as the state.
   - `ContractService.transitionState` requires a `TransitionContext`: controllers pass the verified Cognito sub and the request id; readiness and authoring services pass `service_system`.
   - The uncalled `processExpiredTransitions` is deleted.
   - A writer inventory (application, scripts, hand SQL) is recorded in the DBCP.

6. **Dead calls deleted.** The three dead `EvidenceService` injections (ContractService #7, ConnectionService #3, ReaderService #4) and their fire-and-forget `recordEvidence`/`recordLineage` helpers are deleted, and the #830 baseline shrinks to empty. Restoring them is rejected: even while they were alive, they wrote to the TENANT data plane after the state write, outside its transaction, with errors swallowed. They never met Inv VI.

7. **Class rule.** Every platform-plane governed lifecycle state surface must emit an append-only, same-transaction record through a restricted producer that fails closed on an undeclared context. Evidence for platform acts never goes through the tenant-plane EvidenceService.
   - **Enforcement:** a bc-core catalog-plus-behaviour architecture gate (DBCP §4.7). It checks trigger presence, enablement, events and family argument; emitter ownership, definer status and search_path; the guard; the append-only trigger including TRUNCATE; the FK; and grants.
   - **Baseline:** SHRINK-ONLY, each entry task-bound:
     - source + admission versions: TSK-f5c69f;
     - ai: TSK-0f4037;
     - intervention: TSK-9f42ef;
     - connection status: TSK-c21423;
     - reader bindings: TSK-fa4d71;
     - admission-run completion (`runtime.admission_run.run_status`): TSK-af45a4.
   - A nonexistent declared coordinate turns the gate red. The gate checks effective privilege and membership for every ordinary principal.
   - The baseline is disclosed debt, not evidence.

8. **No backfill.**
   - No same-transaction platform record of CC/OC version transitions exists in the current `bc_platform_dev` catalog.
   - From at least 2026-04-07 (derived from the source) until apply, the dead calls were not even attempted. Before then, the only attempt was the fire-and-forget tenant-plane write.
   - This is a claim about the code and the current dev catalog, not a forensic claim about every historical deployment.
   - The gap is disclosed, not reconstructed.

9. **Sequencing.** Nothing goes live before a complete clone rehearsal is accepted.
   1. **Build and pin** the code, DDL, role and driver at the combined serve-move head.
   2. **Rehearse on a clone:** apply to an isolated restored clone; run the real-role negative corpus and the 7c-c lifecycle; submit the exact package to Codex.
   3. **Apply live, in this order, each under its own gate:**
      0. The W6-P database-capability slice.
      1. DDL + role (operator yes). The window before the serve is fail-closed: old code declares nothing, so transitions are refused, not evidence-free.
      2. The combined serve move.
      3. The 7c-c execution request.
   4. **Rollback:** after rows exist, disabling the emitter is a HALT disposition needing its own authority; there is no automatic evidence-free fallback.
   5. **Mechanism evidence to date:** a prototype corpus (T1–T17, including compound-statement, nested-lifetime and real-rollback tests) passes, with six prove-red variants, in a throwaway PostgreSQL 17.11 container (DBCP §5).
