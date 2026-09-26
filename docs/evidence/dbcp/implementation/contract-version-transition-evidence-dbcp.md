---
uid: contract-version-transition-evidence-dbcp
title: Contract-Version Transition Evidence (Inv VI) — Design and DBCP
description: Design act for TSK-56c689 under proposed ADR DEC-fbc085 (D627). No platform record captures contract-version governance transitions today, so this declares a platform-plane evidence home. Two append-only tables, contract.canonical_contract_version_transition and contract.observation_contract_version_transition, are written by a trigger in the same transaction as the state change and refuse any change whose cause is undeclared. The three dead tenant-plane EvidenceService injections are deleted, and a class rule with an architecture gate covers every governed state column. PROPOSED — NOT APPLIED. No DDL, no DML, no serve move.
status: draft
date: 2026-09-26
project: bc-docs
domain: contracts
subdomain: governance
focus: evidence
---

# Contract-Version Transition Evidence (Inv VI) — Design and DBCP

**Status:** proposed. **Not applied.** Nothing is created, altered or written until the operator gives an explicit yes and the committed-DBCP apply gate runs.
**ADR:** DEC-fbc085 (D627), proposed. **Task:** TSK-56c689. **Plan:** PLN-31c4a1 (Platform Readiness), now on the critical path in front of 7c-c (TSK-e75f1d).
**Trigger for this act:** Codex RESPONSE gen-e90cd0-02, finding R2. Codex will not clear an evidence-free live lifecycle for 7c-c. That lifecycle activates cc-dh5d9 1.6.0 and supersedes CC 1.5.0 and OC 1.2.0 for tenant Kaveri.

## 1. Problem

bc-core #830 (merged 8cc52c7d) found three `@Optional() evidenceService: EvidenceService | null` injections. SWC erases their token to `Object`, so the dependency has been `null` since at least 2026-04-07. It left them dead and baselined in `src/__architecture__/optional-erased-token.baseline.json`, bound to TSK-56c689:

| Class | Index | Call sites (origin/main 8cc52c7d) | Evidence types |
|---|---|---|---|
| `ContractService` | 7 | `contract.service.ts:424, 704, 984, 1145` → helper `:1169` | `bulk_governance_transition`, `validation`, `governance_transition`, `compatibility_check` |
| `ConnectionService` | 3 | `connection.service.ts:207, 273` → helper `:334` | `connection_status_change`, `connection_check` |
| `ReaderService` | 4 | `reader.service.ts:316, 358` (lineage), `:584` → helpers `:642, :653` | `bound_to` lineage, `admission_run` |

Injecting it for real is not an option. `EvidenceService` → `EvidenceRepository` → `TENANT_DATA_DB` is tenant data-plane and implicitly request-scoped, so injecting it bubbles request scope into about 30 platform providers and controllers, and every platform contract route returns 500 outside tenant scope.

**Even when these calls were alive, they did not meet Invariant VI.** For example, `recordEvidence` in `contract.service.ts:1161-1172`:
- ran **after** the state write had committed, outside its transaction;
- was **fire-and-forget**, with `?.catch(... logger.warn)` swallowing the error;
- wrote into **whichever tenant database the request was scoped to**, although a contract-version transition is a platform act.

A transition could therefore commit with no evidence, and evidence could land in an unrelated tenant. Restoring the calls would restore that defect, so this document does not propose it.

## 2. Read-only grounding (2026-09-26)

Code: bc-core `origin/main` 8cc52c7d. Database: `bc_platform_dev` on 127.0.0.1:5435 (PostgreSQL 17.11), every query inside `BEGIN READ ONLY; … COMMIT;`. No write was issued.

### 2.1 How a contract-version transition is written today

- **The choke point.** `ContractService.transitionState` (`contract.service.ts:838-993`) is the path for activate, supersede, review, approve and draft. It calls `ContractVersionRepository.updateVersionState` (`contract-version.repository.ts:92-112`), which runs `UPDATE … SET governance_state_code = $new`. That is an **in-place update**, and it runs on `this.db` (autocommit) unless the caller passes an executor. A canonical activation runs `activateCanonicalUnderLock` (`:1010-1035`, advisory lock + `markForSupersession` + update) in one transaction.
- **A second writer.** `ContractAnalyticsRepository.bulkTransition` (`contract-analytics.repository.ts:244-273`) runs a bulk `UPDATE … SET governance_state_code`. It is exposed by `ContractController.bulkTransition` (`contract.controller.ts:127-133`).
- **A third writer with no caller.** `ContractVersionRepository.processExpiredTransitions` (`:164-178`) is the D305 deferred supersession. Nothing in `src/` calls it.
- **Callers of `activateVersion` / `supersedeVersion`:**
  - `contract.controller.ts:290, 302`;
  - `provisioning-readiness.service.ts:120`, the pending_provisioning → active leg (controller and scheduler);
  - `publish-chain.service.ts:147, 152`;
  - `author-observation-chain.service.ts:295, 380`;
  - `register-source-stack.service.ts:211`;
  - `mcf-arpi-materialization-writer.service.ts:233`.

### 2.2 Is there an existing platform record that already meets Inv VI?

| Candidate | Append-only? | Written at the transition, same tx? | Covers contract-version governance transitions? | Verdict |
|---|---|---|---|---|
| `contract.*_contract_version` (governance_state_code, created_at, supersede_after) | No: `trg_cv_immutable` freezes only `contract_json` and `version_code` once active/superseded; the state is overwritten | — | Only the current state; `supersede_after` is a scheduling marker | **No** |
| `contract.{canonical,observation,source}_contract_approval` | No trigger (mutable) | Not on the transition path | 0 rows in each | **No** |
| `contract.certification_record` | Frozen, all DML rejected (Phase A4) | — | Legacy BCF | **No** |
| `bcf.certification_record` | Guarded | Yes, for BCF | BCF primitives only (business_field, canonical_field, registry concept/entity/characteristic) | **No** (wrong subject) |
| `metric_audit.transition_evidence` | Yes (`fn_reject_mutation`) | Yes, for MCF | MCF only: FK to the metric-contract version and a certification record; 385 rows, last 2026-08-03 | **No** (wrong subject) |
| `operations.activity_log` | No trigger (mutable) | No | Generic JSON; 2 rows (`tenant_provisioned`) | **No** |
| `schema_provisioner.provisioning_command_transition` | Yes | Yes, for provisioning commands | The provisioning **command** after activation, not the governance act; 24 rows | **No** (it records a consequence, not the act) |
| `runtime.connection_tenant_assignment_event` | Yes | Yes | Only connection → tenant assignment | **No**, but it is **the pattern** to follow |
| `runtime.admission_run_disposition` | Yes | Yes (reader operator disposition) | Only an operator disposition of an admission run | **No**, but it is **the pattern** to follow |

**Conclusion: option (a), ratifying an existing record, is not available.** Contract-version governance transitions have **no** platform-plane record. The only fact that survives is the current state. Option (b) applies: declare the home.

## 3. Foundation Invariant Check

1. **Why this location (E, storage of the governance record, emitted at the write):** the transition *is* the state write. Recording the evidence in the same database and transaction as that write is the only place where it is emitted rather than inferred.
2. **Why not an upper layer (A/B):** the lifecycle grammar (`governanceMachine`, the D430/D431 activation gates, D575 pending_provisioning) is declared and is not in dispute. What is missing is the declaration of *where the act's evidence lives*. That is the design act itself, not compensation for a semantic gap.
3. **Why not a lower layer:** the only working evidence mechanism, the tenant `EvidenceService`, belongs to another plane and is request-scoped (§1). No working platform-plane mechanism is being bypassed. Existing primitives are reused (`infrastructure.fn_reject_mutation`, the `fn_mcv_revision_emit` trigger-emit pattern, and the `connection_tenant_assignment_event` column pattern).
4. **Design act or execution act (DEC-c48b0f):** a **design act**. It declares the platform-plane governance-evidence boundary and a class rule. The architecture gate is the enforcement net for the class; the declaration is the act.

Invariant III: the new rows are immutable, and the version row's state keeps its existing semantics. Invariant IV: each row references its version through an explicit composite FK. Invariant V: the rows are never re-derived. Invariant VI: the evidence is emitted by the act, in its transaction.

## 4. Design

### 4.1 Scope (narrow)

- **In:** `contract.canonical_contract_version` and `contract.observation_contract_version`. These are the two families the 7c-c lifecycle touches (activate CC 1.6.0 through pending_provisioning → active; supersede CC 1.5.0; supersede OC 1.2.0).
- **Baselined under the class gate (§4.6), each with a follow-up task:**
  - source, admission and ai contract versions (`governance_state_code`);
  - intervention contract versions (`status_code`);
  - `runtime.connection.connection_status`;
  - reader-binding bind and re-point (`bindContextBinding` / `flipContextBindings`);
  - admission-run completion (`completeAdmissionRun`).
- **Out:** tenant-plane evidence; MCF (it has its own `metric_audit.transition_evidence`); BCF (`bcf.certification_record`); any backfill.

### 4.2 Tables (proposed DDL, NOT APPLIED)

There is one table per family so that each carries a real composite FK (D162 rule 3). A single polymorphic table with no FK was rejected (§6). Each table has 13 columns (≤ 20) and uses ISO 11179 names.

```sql
-- 02-platform-tables/contract/NN-contract-version-transition.sql  (proposed; applied only after the operator's yes)
CREATE TABLE contract.canonical_contract_version_transition (
  canonical_contract_version_transition_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  canonical_contract_id   uuid        NOT NULL,
  version_code            text        NOT NULL,
  from_state_code         text        NULL,        -- NULL only when a version is born past 'draft'
  to_state_code           text        NOT NULL,
  transition_cause_code   text        NOT NULL,
  authenticated_subject   text        NULL,        -- Cognito sub when the writer has one
  request_correlation_id  text        NULL,
  rationale_text          text        NULL,
  contract_json_sha256    text        NOT NULL,    -- the exact bytes (jsonb text form) that were transitioned
  db_principal_name       text        NOT NULL DEFAULT session_user,
  transaction_id          xid8        NOT NULL DEFAULT pg_current_xact_id(),
  recorded_at             timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT fk_canonical_contract_version_transition_version
    FOREIGN KEY (canonical_contract_id, version_code)
    REFERENCES contract.canonical_contract_version (canonical_contract_id, version_code) ON DELETE RESTRICT,
  CONSTRAINT canonical_contract_version_transition_cause_check CHECK (transition_cause_code IN
    ('governed_request','provisioning_readiness','authoring_chain','bulk_transition','operator_sql')),
  CONSTRAINT canonical_contract_version_transition_rationale_check CHECK (
    transition_cause_code <> 'operator_sql' OR length(coalesce(rationale_text,'')) >= 40),
  CONSTRAINT canonical_contract_version_transition_sha_check CHECK (contract_json_sha256 ~ '^[0-9a-f]{64}$')
);
CREATE INDEX idx_canonical_contract_version_transition_version
  ON contract.canonical_contract_version_transition (canonical_contract_id, version_code, recorded_at);
CREATE TRIGGER trg_canonical_contract_version_transition_append_only
  BEFORE UPDATE OR DELETE ON contract.canonical_contract_version_transition
  FOR EACH ROW EXECUTE FUNCTION infrastructure.fn_reject_mutation();
-- observation_contract_version_transition: identical shape, keyed by observation_contract_id.
```

### 4.3 Emission (a trigger in the same transaction, fail-closed)

```sql
CREATE FUNCTION contract.fn_contract_version_transition_emit() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE
  fam   text := TG_ARGV[0];                                  -- 'canonical' | 'observation'
  cause text := nullif(current_setting('bc.transition_cause', true), '');
BEGIN
  IF TG_OP = 'UPDATE' AND OLD.governance_state_code IS NOT DISTINCT FROM NEW.governance_state_code THEN
    RETURN NEW;                                              -- not a transition
  END IF;
  IF TG_OP = 'INSERT' AND NEW.governance_state_code = 'draft' THEN
    RETURN NEW;                                              -- birth in draft is not a transition
  END IF;
  IF cause IS NULL THEN
    RAISE EXCEPTION 'contract-version transition %.% % -> % refused: no declared transition cause (DEC-fbc085, Inv VI)',
      TG_TABLE_NAME, NEW.version_code, CASE WHEN TG_OP='UPDATE' THEN OLD.governance_state_code END,
      NEW.governance_state_code USING ERRCODE = 'check_violation';
  END IF;
  EXECUTE format('INSERT INTO contract.%I (%I, version_code, from_state_code, to_state_code, transition_cause_code,
                    authenticated_subject, request_correlation_id, rationale_text, contract_json_sha256)
                  VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)', fam || '_contract_version_transition', fam || '_contract_id')
  USING (to_jsonb(NEW) ->> (fam || '_contract_id'))::uuid, NEW.version_code,
        CASE WHEN TG_OP = 'UPDATE' THEN OLD.governance_state_code END, NEW.governance_state_code, cause,
        nullif(current_setting('bc.transition_subject', true), ''),
        nullif(current_setting('bc.transition_correlation_id', true), ''),
        nullif(current_setting('bc.transition_rationale', true), ''),
        encode(sha256(convert_to(NEW.contract_json::text, 'UTF8')), 'hex');
  RETURN NEW;
END $$;

CREATE TRIGGER trg_canonical_contract_version_transition_emit
  AFTER INSERT OR UPDATE OF governance_state_code ON contract.canonical_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.fn_contract_version_transition_emit('canonical');
CREATE TRIGGER trg_observation_contract_version_transition_emit
  AFTER INSERT OR UPDATE OF governance_state_code ON contract.observation_contract_version
  FOR EACH ROW EXECUTE FUNCTION contract.fn_contract_version_transition_emit('observation');
```

Properties:
- **Emitted, not inferred.** The row commits or rolls back with the state change. A refused activation, such as a failed D430/D431 gate or a lock re-check throw, leaves no row. A committed one always leaves exactly one.
- **Fail-closed.** A writer that did not declare a cause cannot change the state. This covers the bulk endpoint, archived scripts, the uncalled `processExpiredTransitions` if it is ever revived, and hand SQL: operator SQL must declare `operator_sql` with a rationale of at least 40 characters.
- **Content binding.** `contract_json_sha256` pins the exact contract body at the moment of transition. That matters for `approved → pending_provisioning → active`, because a non-active version's `contract_json` is still mutable before activation.
- **Plane.** The record lives in the platform DB, in the same schema as its subject. It is never written by tenant-scoped code and never needs a request scope.

### 4.4 Writer changes (bc-core, one PR)

1. `ContractVersionRepository.updateVersionState(…, exec?, context)`:
   - runs `SELECT set_config('bc.transition_cause', $cause, true)` (plus subject, correlation id and rationale) and the UPDATE in **one transaction**;
   - uses `exec` when the caller is already inside one (`activateCanonicalUnderLock`, the `runFenced` authoring fence), and otherwise opens `this.db.transaction(...)`.
   - The same applies to `ContractAnalyticsRepository.bulkTransition` (cause `bulk_transition`, subject from the request).
2. `ContractService.transitionState` gains a **required** `context: { cause; subject?; correlationId? }`, threaded from `activateVersion`, `supersedeVersion`, `submitForReview`, `approveVersion` and `revertToDraft`. Callers:

   | Caller | Cause |
   |---|---|
   | Controllers | `governed_request`, with the Cognito sub and request id |
   | `provisioning-readiness.service` | `provisioning_readiness` |
   | `publish-chain`, `author-observation-chain`, `register-source-stack`, `mcf-arpi-materialization-writer` | `authoring_chain` |

   TypeScript makes a missing cause a compile error. The database makes it a refusal.
3. Delete `evidenceService` and the `recordEvidence`/`recordLineage` helpers and calls from `ContractService`, `ConnectionService` and `ReaderService`. Delete the unused `EvidenceService` imports. Shrink `optional-erased-token.baseline.json` to `entries: []`. The evidence types being removed:
   - `validation` and `compatibility_check` are read-model diagnostics, not governance acts, so they get no replacement;
   - `governance_transition` and `bulk_governance_transition` are replaced by §4.3;
   - the connection and reader types go onto the class baseline (§4.6) with follow-up tasks.
4. Inventory INSERT paths for canonical/observation versions that create a version in a state other than `draft`. Each such path must declare `authoring_chain`, or the insert is refused. This inventory is a required first step of the PR.

### 4.5 Proof required before 7c-c (the composed-build proof Codex asked for)

The following runs against a real database: a throwaway tenant plus a restored clone, never bc-postgres live, following the zero-residue test rule.

1. Each of draft→review→approved→pending_provisioning→active and active→superseded emits exactly one row, with the correct from/to state, cause, sha256 and transaction id.
2. A refused activation (for example a D430 drift) leaves the state unchanged and writes zero rows.
3. A transaction rolled back after the UPDATE leaves zero rows.
4. An UPDATE with no cause set is refused, and the state is unchanged. **Prove-red:** remove the `set_config` from the repository and the test fails.
5. UPDATE or DELETE on a transition row is refused.
6. `bulkTransition` over N versions emits N rows.
7. The architecture gate (§4.6) goes red when the emit trigger is dropped from either table, and red on a stale baseline entry.
8. The same checks run at the exact **composed served head** for the combined serve move TSK-4636d8 (#830 + #831 + #832 + this PR), in a clone rehearsal. Clone rehearsal of the 7c-c lifecycle must show the 1.6.0 activation (two rows: approved→pending_provisioning, then pending_provisioning→active), the 1.5.0 supersession and the OC 1.2.0 supersession. The rows must carry the expected causes.

### 4.6 Class rule and gate

**Rule (DEC-fbc085 point 7).** A platform-plane column that carries a governed lifecycle state must record each transition in an append-only record, written in the same transaction and fail-closed on an undeclared cause. Evidence for platform acts never goes through the tenant-plane `EvidenceService`.

**Gate.** A new bc-core `src/__architecture__/` catalog spec, run against the CI database built from the DDL set:
- enumerates platform tables that have `governance_state_code`, or `status_code` on a `*_version` table, plus a declared list of state-bearing runtime tables;
- asserts that each one carries an emit trigger whose target table has the append-only trigger.

The gate starts with a **SHRINK-ONLY** baseline in which each entry is bound to a task:

| Baselined subject | Follow-up |
|---|---|
| `contract.source_contract_version`, `contract.admission_contract_version` | extend §4.3 (same function, new family arg) |
| `contract.ai_contract_version` | same |
| `contract.intervention_contract_version` (`status_code`) | same, with its own column |
| `runtime.connection.connection_status` | connection status-transition record |
| reader-binding bind / re-point (`runtime` context bindings) | binding-transition record |
| `runtime.admission_run` completion (non-operator) | extend the `admission_run_disposition` pattern |

## 5. Disclosed gap (no backfill)

- **Durable, same-transaction evidence has never existed for any contract, connection or reader transition.** From at least 2026-04-07 until the §4.3 trigger is applied, the calls were not even attempted. Before 2026-04-07, the tenant-plane fire-and-forget writes described in §1 were the only attempt.
- This includes the Kaveri cc-dh5d9 history:
  - 1.0.0, 1.1.0, 1.2.0 and 1.4.0 are `superseded`;
  - 1.5.0 is `active`;
  - 1.3.0 and 1.6.0 are `approved`, per a READ ONLY query on 2026-09-26.
- The only surviving fact for these versions is their current state. `created_at` and `supersede_after` are not transition evidence.
- **Nothing is reconstructed.** A backfilled row would be inferred evidence, which Invariant VI forbids. Historical exposure is bounded only by the source-derived SWC date (978e3e55). It has not been forensically established for every deployment.

## 6. Alternatives considered

| Option | Why rejected |
|---|---|
| (a) Ratify an existing record | None exists (§2.2) |
| Restore `@Inject(EvidenceService)` | Wrong plane; bubbles request scope and 500s platform routes; was never same-transaction |
| Reuse `metric_audit.transition_evidence` / `bcf.certification_record` | Wrong subject: MCF/BCF FKs and guards |
| `operations.activity_log` | Mutable, generic JSON, no FK |
| One polymorphic `contract.contract_version_transition` without an FK | Breaks D162 rule 3 (FKs mandatory) |
| Insert from the application only, no trigger | Doesn't guard the class: bulk, script and hand-SQL writers bypass it |
| A generic platform `evidence` schema | Polymorphic subject; a larger design than 7c-c needs; can come later under the class rule |

## 7. Sizing

| Unit | Content | Size |
|---|---|---|
| DDL + DBCP apply kit | 2 tables, 1 function, 4 triggers, 2 indexes, grants (the trigger runs as the invoker, so the served login gets INSERT + SELECT and no UPDATE/DELETE; `chain_auditor_readonly` gets SELECT); `schema_migration_event` record; rollback file | ~120 lines SQL; half a day |
| bc-core code PR | repository tx+context (2 repos), `transitionState` context threading (6 callers + 3 controller routes), dead-call deletion in 3 services, baseline shrink, INSERT-path inventory | ~250 LOC changed |
| Tests + gate | real-DB integration (§4.5 1–6), catalog arch gate (§4.5 7), prove-red | ~300 LOC |
| Composed proof | clone rehearsal inside TSK-4636d8 (§4.5 8) | part of the serve-move package |

Total: about 1–1.5 working days of build, plus review rounds. No new npm dependency.

## 8. Sequencing and gates

1. **This ADR and design** are reviewed by Codex on a new `gen-` thread (Kind: design). The ADR stays `proposed` until that review accepts it.
2. **Code PR** (bc-core; standing-allowed as a draft PR). Without the trigger it is behaviour-neutral, apart from deleting dead calls and opening a transaction around the state update.
3. **Combined serve move TSK-4636d8** carries the PR. It needs the gen- EXECUTION CLEARED plus the operator's exact grant.
4. **DDL apply.** The operator's explicit "yes" to this DBCP, then the committed-DBCP apply gate. This comes **after** step 3, so the served code already declares causes when the fail-closed trigger lands. Applying the trigger first would refuse every transition until the serve.
5. **§4.5 proof** at the composed head and on the applied schema, in a clone rehearsal.
6. **7c-c execution request** to Codex, with the proof attached.

**Rollback.** Before any transition row exists: drop the triggers, the function and the tables. Afterwards: drop only the **emit** triggers, which stops emission and needs the operator's yes. The rows stay, because they are immutable evidence.

## 9. Operator decisions requested

- **D1.** Accept option (b), a new platform-plane home, over deleting the calls with no replacement.
- **D2.** Accept per-family tables, not one polymorphic table.
- **D3.** Accept **fail-closed** on an undeclared cause, including for operator hand SQL (`operator_sql` + rationale).
- **D4.** Accept the narrow scope (canonical + observation now) with the shrink-only class baseline.
- **D5.** A later "yes" to apply the DDL (§4.2–4.3) after the serve move. **Not requested now.**
