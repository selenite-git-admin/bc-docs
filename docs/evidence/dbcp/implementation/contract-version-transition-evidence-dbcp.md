---
uid: contract-version-transition-evidence-dbcp
title: Contract-Version Transition Evidence (Inv VI) — Design and DBCP
description: Design act for TSK-56c689 under proposed ADR DEC-fbc085 (D627), successor 1 (answers Codex gen-1afb60-01 F1–F4). No platform record captures contract-version governance transitions, so this declares a platform-plane evidence home. Two append-only tables, contract.canonical_contract_version_transition and contract.observation_contract_version_transition, are written only by a SECURITY DEFINER emitter trigger, owned by a NOLOGIN role, in the same transaction as the state change. The transition context is declared inside the writing statement and reset before and after every statement. Direct INSERT, metadata override, UPDATE, DELETE and TRUNCATE are refused. A prototype corpus passes, and three prove-red variants fail as expected, in a throwaway PostgreSQL 17.11 container. The dead tenant-plane EvidenceService calls are deleted. A class rule and a specified catalog gate come with task-bound baseline entries. PROPOSED — NOT APPLIED. No DDL, no DML, no serve move.
status: draft
date: 2026-09-26
project: bc-docs
domain: contracts
subdomain: governance
focus: evidence
---

# Contract-Version Transition Evidence (Inv VI) — Design and DBCP

**Status:** proposed, successor 1. **Not applied.** Nothing is created, altered or written on any live or served database until the operator gives an explicit yes and the committed-DBCP apply gate runs.

| | |
|---|---|
| ADR | DEC-fbc085 (D627), proposed |
| Task | TSK-56c689 |
| Plan | PLN-31c4a1 (Platform Readiness), critical path before 7c-c (TSK-e75f1d) |
| Review | Codex `gen-1afb60`. 01 → RESPONSE 01, CHANGES REQUIRED F1–F4. This successor answers every finding (§10). |
| Origin | Codex RESPONSE gen-e90cd0-02, finding R2. Codex will not clear an evidence-free 7c-c lifecycle (activate cc-dh5d9 1.6.0; supersede CC 1.5.0 and OC 1.2.0 for tenant Kaveri). |

## 1. Problem

bc-core #830 (merged 8cc52c7d) left three `@Optional() evidenceService: EvidenceService | null` injections dead. SWC erases their token, so they have been `null` since at least 2026-04-07, a date derived from the source (SWC builder 978e3e55). #830 baselined them and bound them to TSK-56c689:

| Class | Index | Call sites (8cc52c7d) | Evidence types |
|---|---|---|---|
| `ContractService` | 7 | `contract.service.ts:424, 704, 984, 1145` → helper `:1161-1172` | `bulk_governance_transition`, `validation`, `governance_transition`, `compatibility_check` |
| `ConnectionService` | 3 | `connection.service.ts:207, 273` → helper `:334` | `connection_status_change`, `connection_check` |
| `ReaderService` | 4 | `reader.service.ts:316, 358` (lineage), `:584` → helpers `:642, :653` | `bound_to` lineage, `admission_run` |

Injecting `EvidenceService` for real is rejected. It is tenant data-plane and request-scoped (`TENANT_DATA_DB`), so it would bubble request scope into about 30 platform providers, and every platform contract route would return 500 outside tenant scope.

Restoring the calls is rejected too. Even while alive, the helpers were fire-and-forget: they ran **after** the state write, outside its transaction, with errors swallowed (`?.catch(warn)`), and they wrote into whichever tenant database the request happened to be scoped to.

## 2. Read-only grounding (2026-09-26)

Code: bc-core `origin/main` 8cc52c7d. Database: `bc_platform_dev` on 127.0.0.1:5435 (PostgreSQL 17.11), every query inside `BEGIN READ ONLY; … COMMIT;`, with no write issued. Codex reproduced the catalog facts independently (RESPONSE gen-1afb60-01, "Grounding").

### 2.1 How the version state is written today

- **The state column is overwritten in place.** `ContractService.transitionState` (`contract.service.ts:838-993`) → `ContractVersionRepository.updateVersionState` (`contract-version.repository.ts:92-112`), which runs `UPDATE … SET governance_state_code`. It uses autocommit `this.db` unless the caller passes an executor. Canonical activation goes through `activateCanonicalUnderLock` (`:1010-1035`: advisory lock + `markForSupersession` + update, in one transaction).
- **No history is kept.** `trg_cv_immutable` freezes only `contract_json` and `version_code` once a version is active or superseded.
- **Scheduled background state writers:** only `ProvisioningReadinessScheduler` (`@Cron */5`). It runs only when `BC_SCHEDULER_ENABLED=1`, which the live served pid does not have (#830 serve-move notes). This must be re-verified at every live window (§8).

### 2.2 Writer inventory for `contract.canonical_contract_version` and `contract.observation_contract_version` (F4)

| # | Writer | Kind | State effect | Under this design |
|---|---|---|---|---|
| W1 | `contract-version.repository.ts:92` `updateVersionState` | UPDATE | any transition (from `transitionState`, `activateCanonicalUnderLock`) | declares its context in the statement (§4.4) |
| W2 | `contract-analytics.repository.ts:244-273` `bulkTransition` (HTTP `contract.controller.ts:127`) | UPDATE (bulk) | category-wide from→to | declares `bulk_transition` once for the one statement |
| W3 | `contract-version.repository.ts:164` `processExpiredTransitions` | UPDATE | active→superseded | **no caller in `src/`**. It is deleted in the code PR; if ever revived, the trigger refuses it |
| W4 | `contract-version.repository.ts:34` `createVersion` (INSERT) | INSERT | callers pass `'draft'`: `contract.service.ts:740`, `mcf-arpi-materialization-writer.service.ts:226`; authoring/harness/seed callers go through `ContractService.createVersion` → `:740` | `draft` births emit nothing. The code PR adds a test that no application INSERT is born past `draft`; any future one must declare its context |
| W5 | `contract-version.repository.ts:151` `markForSupersession` | UPDATE `supersede_after` only | no state change | trigger is `UPDATE OF governance_state_code`, so it does not fire (proved: T5 same-state) |
| W6 | `scripts/finance-co-versions.js:339` (INSERT), `scripts/fix-oc-field-mappings.mjs:185` (UPDATE `contract_json`) | out-of-`src` scripts | the INSERT may be born non-draft | refused unless it declares `operator_sql` + rationale. The code PR lists both scripts in the README of the inventory test |
| W7 | Hand SQL (operator) | UPDATE / INSERT | any | must declare `operator_sql` + rationale ≥ 40 characters. This is a **writer assertion, not authorization**. The exact operator grant stays a separate gate (Codex Q2) |

`contract.repository.ts` UPDATEs (`:426, :700, :716`) touch the contract **header** tables (`f.sqlTable`), not the version tables.

### 2.3 Existing records considered for ratification: option (a) is not available

The details, with triggers and counts, are in successor 0 (bc-docs #70 @ d7b91123 §2.2):
- `*_contract_approval`: 0 rows, mutable;
- `contract.certification_record`: frozen;
- `bcf.certification_record`: BCF primitives only;
- `metric_audit.transition_evidence`: MCF-only FK;
- `operations.activity_log`: mutable;
- `schema_provisioner.provisioning_command_transition`: records provisioning commands, not the governance act.

The patterns reused here are `runtime.connection_tenant_assignment_event` (INSERT guard that overwrites principal/time; statement-level append-only trigger including TRUNCATE) and `infrastructure.fn_reject_mutation` (SECURITY DEFINER, `search_path=pg_catalog`).

## 3. Foundation Invariant Check

1. **Location E, emitted at the write.** The transition *is* the state write. Evidence emitted from OLD/NEW inside that write's transaction is emitted, not inferred (Codex Q1: "Yes in principle").
2. **Not an upper layer.** The lifecycle grammar (`governanceMachine`, D430/D431 gates, D575 pending_provisioning) is declared. What is missing is the declaration of where the act's evidence lives. That is the design act, not compensation.
3. **Not a lower layer.** The only working evidence mechanism (tenant `EvidenceService`) is another plane. No platform mechanism is bypassed; existing platform primitives are reused.
4. **Design act (DEC-c48b0f):** the platform-plane governance-evidence boundary and a class rule. The gate (§4.6) is the net.

Invariants: III (rows immutable, TRUNCATE included), IV (explicit composite FK per family), V (never re-derived), VI (emitted by the act, in its transaction, by the only permitted producer).

## 4. Design

### 4.1 Scope

- **First unit:** `contract.canonical_contract_version` and `contract.observation_contract_version`. These are the two families of the 7c-c lifecycle; Codex Q3 accepts this as a bounded first unit.
- **Not closed by this unit:** the broader evidence gap for connection, reader, source and admission. The baseline in §4.6 is **disclosed debt, not evidence**.

### 4.2 Producer and privilege boundary (F1)

| Object | Owner | Who may write | Notes |
|---|---|---|---|
| `contract.{canonical,observation}_contract_version_transition` | `bc_schema_owner` (NOLOGIN, exists) | INSERT: **only** `bc_contract_evidence_emitter`. No role has UPDATE, DELETE or TRUNCATE | `REVOKE ALL … FROM PUBLIC`; SELECT for the served login and `chain_auditor_readonly` |
| `bc_contract_evidence_emitter` | — | NOLOGIN, **new role** (DBCP D6); nobody is granted membership | holds only: USAGE on `contract`, INSERT on the two tables, SELECT on the two version tables (for the guard's cross-check) |
| `contract.fn_contract_version_transition_emit()` | `bc_contract_evidence_emitter` | trigger only (`RETURNS trigger` cannot be called directly); `REVOKE ALL … FROM PUBLIC` | `SECURITY DEFINER`, `SET search_path = pg_catalog`, fully qualified names |
| `contract.fn_contract_version_transition_guard()` (BEFORE INSERT on the evidence tables) | table owner | — | refuses unless `current_user = bc_contract_evidence_emitter` **and** `pg_trigger_depth() >= 2` (called from inside the version-table trigger) **and** the version's current state equals `to_state_code`. It **re-derives** `db_principal_name := session_user`, `transaction_id := pg_current_xact_id()` and `recorded_at := clock_timestamp()`; inserter-supplied values are discarded |
| append-only trigger | — | — | `BEFORE UPDATE OR DELETE OR TRUNCATE … FOR EACH STATEMENT EXECUTE FUNCTION infrastructure.fn_reject_mutation()` (the ctae pattern, TRUNCATE included) |
| `transition_seq bigint GENERATED ALWAYS AS IDENTITY` | — | — | an explicit value is refused without `OVERRIDING SYSTEM VALUE`, and the guard permits only the emitter anyway |

**Authority boundary, stated precisely:**
- **Ordinary writers** (any non-superuser login) cannot insert, alter, delete or truncate evidence. They cannot assume the emitter role, and they cannot call the emitter.
- **Owner and superuser** keep recovery authority. `ALTER TABLE … DISABLE TRIGGER`, `DROP`, `SET ROLE bc_contract_evidence_emitter` and `session_replication_role = replica` are all superuser/owner acts. The design does not claim to constrain them. The §4.6 gate detects a disabled, replica-only or missing trigger. Any use of that authority is an explicit HALT/evidence-gap disposition needing separate exact authority (§8).
- **Disclosed residual:** the live served login `barecount` is **a superuser today** (`pg_roles.rolsuper = t`). Until D575 W6-P (TSK-1a240c, a non-superuser platform login), the privilege boundary binds every non-superuser role but **not the served process itself**. The emitter remains the only *code* path, and the append-only trigger still refuses UPDATE/DELETE/TRUNCATE even for the owner (proved in T11). A superuser can still disable triggers. This is disclosed for Codex to rule on (Q5, §11). It is not claimed away.

### 4.3 Context declaration: operation-local, not transaction-local (F2)

The writer declares the context **inside the writing statement**, as an uncorrelated sub-select that PostgreSQL evaluates once as an init-plan:

```sql
UPDATE contract.canonical_contract_version SET governance_state_code = $to
 WHERE canonical_contract_id = $id AND version_code = $v
   AND (SELECT contract.fn_declare_transition_context($cause, $actor_kind, $subject, $correlation, $rationale));
```

- **`fn_declare_transition_context`** (invoker rights; EXECUTE revoked from PUBLIC and granted to the served login):
  - sets **every** field explicitly, clearing any omitted field, so nothing is inherited;
  - sets a binding `statement_timestamp() || '|' || pg_current_xact_id()`.
- **Reset:** a **BEFORE-STATEMENT** trigger on the version table clears all fields before the statement's init-plan runs. A context declared by any earlier statement, including a savepoint-restored one, is therefore gone.
- **Consume:** an **AFTER-STATEMENT** trigger clears them again once the statement's row triggers have run, including for zero-row statements.
- **The emitter refuses** unless a cause is present **and** the binding equals this statement and transaction.
- **Bulk:** one declaration covers exactly the one bulk statement: every row, and nothing after it.

**Actor kinds** (a CHECK on the evidence row; all are writer assertions, not authentication):

| actor_kind | cause(s) | required fields |
|---|---|---|
| `authenticated_http` | `governed_request`, `bulk_transition` | `actor_subject` (the Cognito sub that bc-core verified on the request) and `request_correlation_id`; a missing one is refused |
| `service_system` | `provisioning_readiness`, `authoring_chain` | `actor_subject` = the declared component (e.g. `bc-core:provisioning-readiness`) |
| `operator_sql` | `operator_sql` | `actor_subject` (operator identity text) and `rationale_text` ≥ 40 characters |

### 4.4 Writers (bc-core code PR)

1. **Repository.** `ContractVersionRepository.updateVersionState(…, exec, context: TransitionContext)` and `ContractAnalyticsRepository.bulkTransition(…, context)` embed the declaration in the UPDATE (§4.3). No separate `set_config` statement and no extra transaction are needed, because the context lives in the statement.
2. **Service.** `ContractService.transitionState` requires a `TransitionContext`: `{ cause, actorKind, subject, correlationId?, rationale? }`.
   - Controllers pass `authenticated_http` with `req.user.sub` and the request id. A missing sub or request id is refused before the write.
   - `provisioning-readiness.service` passes `service_system`/`provisioning_readiness`.
   - `publish-chain`, `author-observation-chain`, `register-source-stack` and `mcf-arpi-materialization-writer` pass `service_system`/`authoring_chain`.
3. **Dead code.**
   - W3 `processExpiredTransitions` is deleted.
   - The three dead `evidenceService` fields, their helpers and their calls are deleted, and the #830 baseline shrinks to `entries: []`.
   - Removing the #830 baseline entries is **separate** from the evidence debts in §4.6. It only removes a dead dependency and closes none of them.
4. **INSERT inventory test.** A test asserts that application version INSERTs pass `'draft'`, and lists W6.

### 4.5 Digest representation

`contract_json_sha256` is the SHA-256 of `convert_to(contract_json::text, 'UTF8')`: PostgreSQL's **jsonb output text**, which normalizes key order and spacing. It is **not** the request's original JSON bytes. Representation id: `pg-jsonb-text-utf8`. An independent check is `SELECT encode(sha256(convert_to(contract_json::text,'UTF8')),'hex')`. Prototype T2 asserts the digest of `{"b":1}` equals the sha256 of the literal text `{"b": 1}`.

### 4.6 Ordering

`transition_seq` (identity) is the **emission order**. Within one version, transitions are serialized by the version row's lock, so `(…_contract_id, version_code, transition_seq)` is unambiguous. Across concurrent transactions it is emission order, not commit order. `recorded_at` (clock_timestamp) and `transaction_id` are attributes, not ordering keys.

### 4.7 Class rule and gate (F4)

**Rule (DEC-fbc085 point 7).** Every platform-plane governed lifecycle state surface must emit an append-only, same-transaction record through a restricted producer that fails closed on an undeclared context. Platform acts never use the tenant-plane `EvidenceService`.

**Gate:** a bc-core `src/__architecture__/` catalog spec, run against the CI database built from the DDL set.

1. **Surface enumeration.**
   - Automatic: base tables with a column named `governance_state_code`, or `status_code` on a `*_version` table, in schema `contract`.
   - Declared: `runtime.connection.connection_status`, `runtime.reader_binding` / `runtime.reader_observation_binding` (bind/unbind), `runtime.admission_run.status`.
   - Any new matching surface that is neither covered nor baselined turns the gate red.
2. **Coverage checks** for each covered surface (catalog: `pg_trigger`, `pg_proc`, `pg_class`, `pg_constraint`, `information_schema.role_table_grants`):
   - an emit trigger is present with `tgenabled IN ('O','A')` (red on `D`, disabled, or `R`, replica-only);
   - its events are exactly AFTER ROW INSERT + UPDATE OF the state column;
   - it calls `contract.fn_contract_version_transition_emit` with the **correct family argument**;
   - the function is owned by `bc_contract_evidence_emitter`, is `prosecdef`, has `search_path=pg_catalog` and has no PUBLIC EXECUTE;
   - the reset and consume statement triggers are present;
   - the target table has the INSERT guard, and the append-only trigger includes TRUNCATE;
   - an FK to the version table exists;
   - only the emitter holds INSERT, and no role holds UPDATE/DELETE/TRUNCATE.
3. **Behaviour checks** (not only catalog): the §5 corpus runs in CI against the same database.
4. **Baseline** (SHRINK-ONLY; every entry carries a real task id):

   | Surface | Task |
   |---|---|
   | `contract.source_contract_version.governance_state_code`, `contract.admission_contract_version.governance_state_code` | TSK-f5c69f |
   | `contract.ai_contract_version.governance_state_code` | TSK-0f4037 |
   | `contract.intervention_contract_version.status_code` | TSK-9f42ef |
   | `runtime.connection.connection_status` | TSK-c21423 |
   | `runtime.reader_binding`, `runtime.reader_observation_binding` (bind / re-point) | TSK-fa4d71 |
   | `runtime.admission_run.status` (running → completed/failed) | TSK-af45a4 |

   The gate goes red on: a baseline entry without a task, a stale or resolved entry, a new uncovered surface, a disabled or wrong-event emitter, a wrong family argument, and a removed INSERT guard or removed TRUNCATE protection.

## 5. Evidence so far: prototype corpus (NOT a migration rehearsal)

| | |
|---|---|
| Artifact | `contract-version-transition-evidence-prototype.sql` (this directory), sha256 `b339bd5c19f393498722da62868faf011731c429878b3e80f3cc132d0b4f67d7` |
| Run transcript | `contract-version-transition-evidence-prototype-run-2026-09-26.txt`, sha256 `a8ab90d78afd28c494f0f44ca2e2967336454b522c61600b8ea7e542def4841a` |
| Engine | throwaway `postgres:17.11-alpine` (image `sha256:b0f9560a…52b24`), `--network none`, removed after the run. **bc-postgres was never touched.** |
| Roles | the corpus runs as a **non-superuser LOGIN** (`served_app`), which stands in for the post-W6-P served login. T10/T11 run as superuser `SET ROLE` to exercise the emitter role and the owner |

Result: **ALL PASS** (exit 0).

| Test | Proves |
|---|---|
| T1 | undeclared UPDATE refused; state unchanged |
| T2 | the 7c-c sequence: 1.6.0 approved→pending_provisioning→active (2 rows, ordered by seq), CC 1.5.0 active→superseded, OC 1.2.0 active→superseded (the observation family); actor per statement, no leak; digest representation |
| T3 | A declared, then B undeclared in **one transaction** → B refused; and the same inside **one DO block** → refused |
| T4 | a context declared by an **earlier statement** does not authorize a later one; after `ROLLBACK TO SAVEPOINT` nothing usable is restored |
| T5 | a rolled-back declared transition leaves 0 rows; a same-state UPDATE and a draft INSERT emit 0 |
| T6 | a non-draft INSERT: undeclared refused; declared emits exactly one birth row (`from_state_code` NULL) |
| T7 | refused, state unchanged: an invalid cause; `authenticated_http` with no correlation id; `operator_sql` with a rationale under 40 characters; a missing subject |
| T8 | bulk: one declaration → N rows; a mixed failure (one row errors) is atomic, with 0 rows and 0 state changes |
| T9 | served role: direct INSERT (fabricated states, hash, principal, txid, time), UPDATE, DELETE, TRUNCATE, calling the emitter, and `SET ROLE` emitter are all refused |
| T10 | even the INSERT-holding emitter role cannot insert outside the version-table trigger (guard) |
| T11 | owner: DELETE and TRUNCATE are refused by the append-only trigger |
| T12 | `db_principal_name` is derived from the writing session |

**Prove-red** (each control removed; the corpus must fail):

| Variant | Removed | Result |
|---|---|---|
| A | reset + consume statement triggers | T3's DO-block leak goes through → **red** |
| B | INSERT guard | T10's direct forged insert succeeds → **red** |
| C | TRUNCATE on the append-only trigger | T11 truncation succeeds → **red** |

**Limits:** the prototype uses stand-in version tables, not a restored `bc_platform_dev`. It does not exercise bc-core code, pooling or the real served login. It is mechanism evidence and **not** the pre-live rehearsal of §8.

## 6. Disclosed gap (no backfill; bounded claims)

- No same-transaction platform record of CC/OC version transitions exists in `bc_platform_dev` today. This was verified by the catalog and independently reproduced by Codex.
- From at least 2026-04-07, a date **derived from the source**, the dead calls were not even attempted. Before that, the only attempt was the fire-and-forget tenant-plane write described in §1.
- This is a statement about the code and the current dev catalog. It is **not** forensically established for every historical deployment.
- Surviving facts for cc-dh5d9: 1.0.0, 1.1.0, 1.2.0 and 1.4.0 are `superseded`; 1.5.0 is `active`; 1.3.0 and 1.6.0 are `approved`. `created_at` and `supersede_after` are not transition evidence.
- **Nothing is reconstructed.**

## 7. Alternatives considered

| Option | Why rejected |
|---|---|
| (a) Ratify an existing record | None exists (§2.3) |
| Restore `@Inject(EvidenceService)` | Wrong plane; request scope → 500s; never same-transaction |
| Application INSERT + deferred assertion trigger | Not required (Codex Q1). It needs the same producer restriction anyway, plus a second write path |
| One polymorphic table, no FK | D162 rule 3 |
| A GUC set by a separate statement, transaction-local | F2: it leaks to later statements; reproduced by Codex, and by T3/T4 without the reset |
| Invoker emitter + served INSERT grant | F1: fabrication possible |
| `PG_CONTEXT` string match as the only guard (the ctae style) | Weaker than privilege; kept only as a secondary idea, not used |

## 8. Sequencing and gates (F3)

**Pre-live, all on an isolated restored clone. No live gate is requested until this is complete and accepted.**
1. **Build and pin:**
   - the bc-core code PR (context threading, dead-call deletion, W3 deletion, inventory test, gate);
   - the DDL + rollback files (`docker/redesign/02-platform-tables/…`, `schema_migration_event` record);
   - the role script (emitter role, grants);
   - the rehearsal driver.

   Each is pinned by commit and sha256, and the composition by the combined serve-move head (TSK-4636d8: #830 + #831 + #832 + this PR).
2. **Restore** a named clone of `bc_platform_dev`. Record the pre-state:
   - cc-dh5d9 and OC version states;
   - the triggers on the version tables;
   - role and grant inventory;
   - `schema_migration_event` head.
3. **Apply** the role script and DDL to the **clone only**. Record the post-state (catalog gate green).
4. **Run** the composed build against the clone, as a **non-superuser** login (the W6-P posture) **and** as the current superuser (documenting the §4.2 residual):
   - the §5 corpus, re-expressed on the real tables;
   - the bc-core integration tests: A-then-B, two actors, nested and rolled-back service calls, pooled connection reuse, missing request identity, invalid cause, a non-draft INSERT;
   - the 7c-c lifecycle through the served API (1.6.0 activate → worker provision → readiness → active; supersede CC 1.5.0; supersede OC 1.2.0), expecting exactly the transition rows of T2 with the right causes and actors;
   - receipts bound to exact identities.
5. **Submit** the exact package to Codex for acceptance.

**Live, only after acceptance, each gate separately:**

6. **DDL + role apply** (operator's yes, D5, committed-DBCP gate). This goes **before** the code serve, so the window between the two is **fail-closed, not evidence-free**:
   - the old served code declares no context, so every CC/OC state change is **refused** until step 7;
   - nothing is lost, because a refused transition changes nothing.

   Pre-checks at the window: `BC_SCHEDULER_ENABLED` absent from the served pid (no background readiness writer), no in-flight authoring run, and the version-state snapshot recorded. Code-first is rejected: its window would be evidence-free, and the new code cannot run without the declaration function.
7. **Combined serve move** (EXECUTION CLEARED + the operator's exact grant). No synthetic probe transition is made; the first live transition is the 7c-c act.
8. **7c-c execution request**, with the §4 receipts.

**Rollback:**
- **Before any live transition row exists:** revert the code; drop the triggers, functions and tables; drop the role (operator yes).
- **After rows exist:** dropping or disabling the emit trigger is an **explicit evidence-gap / HALT disposition**. It needs its own exact authority. The rows are retained, and the gate stays red until the trigger is restored.
- **No automatic fallback** to an evidence-free lifecycle.
- A code-only revert while the trigger is present fails closed: transitions are refused.

## 9. Sizing

| Unit | Content | Size |
|---|---|---|
| DDL + role + rollback + DBCP apply kit | 2 tables, 1 role, 4 new functions, 10 triggers (emit, reset, consume, guard, append-only × 2 families), 2 indexes, grants; the prototype's Part 1 is the shape | ~200 lines SQL |
| bc-core code PR | context type + threading (repositories ×2, `transitionState`, 6 service callers, 3 controller routes), W3 + dead-call deletion, baseline shrink | ~300 LOC |
| Tests + gate | real-DB integration (throwaway tenant/clone), catalog + behaviour gate, prove-red | ~450 LOC |
| Clone rehearsal + package | §8 steps 1–5 | part of TSK-4636d8 |

About 2 working days of build, plus review rounds. No new npm dependency.

## 10. Reconciliation with Codex RESPONSE gen-1afb60-01

| Finding | Resolution |
|---|---|
| F1: append-only is not emission-only | §4.2: a definer emitter owned by a NOLOGIN role that is the sole INSERT holder; an INSERT guard (emitter + trigger depth + state cross-check + re-derived metadata); TRUNCATE rejected; grants specified; the owner/superuser recovery boundary stated; the superuser served-login residual disclosed. Proved: T9–T12, prove-red B and C |
| F2: transaction-local is not operation-local | §4.3: in-statement declaration, all fields explicit, statement/transaction binding, BEFORE-STATEMENT reset, AFTER-STATEMENT consume, actor kinds with required identity. Proved: T3, T4, T7, T8, prove-red A |
| F3: rehearsal after the live steps | §8: full clone rehearsal and acceptance before any live gate; DDL-before-serve with a fail-closed window and pre-checks; HALT rollback semantics |
| F4: baseline and gate underspecified | §2.2 writer inventory; §4.7 exact surfaces, task ids, catalog and behaviour checks, red conditions; the #830 baseline kept distinct |
| Additional coverage | same-state/draft zero (T5), birth record (T6), atomic mixed bulk (T8), both families (T2), ordering (§4.6), digest representation (§4.5) |

## 11. Operator decisions requested

- **D1.** Option (b): a new platform-plane home.
- **D2.** Per-family tables.
- **D3.** Fail-closed for all writers, including operator SQL with a declared rationale.
- **D4.** A narrow first unit with the task-bound baseline.
- **D6.** A new NOLOGIN role `bc_contract_evidence_emitter`.
- **D7.** Accept the §4.2 residual (superuser served login until W6-P TSK-1a240c) for the 7c-c act, or make W6-P a prerequisite. **Codex is asked to rule (Q5).**
- **D5.** A later "yes" to apply the DDL + role live (§8 step 6), after the accepted clone rehearsal. **Not requested now.**
