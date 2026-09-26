---
uid: contract-version-transition-evidence-dbcp
title: Contract-Version Transition Evidence (Inv VI) — Design and DBCP
description: Design act for TSK-56c689 under proposed ADR DEC-fbc085 (D627), successor 2 (answers Codex gen-1afb60-01 F1–F4 and gen-1afb60-02 F2/F4/F5 plus the Q5/Q6 rulings). No platform record captures contract-version governance transitions, so this declares a platform-plane evidence home. Two append-only tables, contract.canonical_contract_version_transition and contract.observation_contract_version_transition, are written only by a SECURITY DEFINER emitter trigger, owned by a NOLOGIN role, in the same transaction as the state change. Each write declares its EXACT target transitions (family, contract id, version, to-state) as one-shot keys inside the writing statement; a row whose exact key is absent is refused, so compound statements are attributed per row or refused, never misattributed. Direct INSERT, metadata override, UPDATE, DELETE and TRUNCATE are refused. The prototype corpus T1–T15 passes, and five prove-red variants fail as expected, in a throwaway PostgreSQL 17.11 container. The database part of D575 W6-P (a least-privilege served login that owns neither the contract schema nor its tables) is a prerequisite of the dependent lifecycle. The dead tenant-plane EvidenceService calls are deleted. A class rule and a specified catalog gate come with task-bound baseline entries. PROPOSED — NOT APPLIED. No DDL, no DML, no serve move.
status: draft
date: 2026-09-26
project: bc-docs
domain: contracts
subdomain: governance
focus: evidence
---

# Contract-Version Transition Evidence (Inv VI) — Design and DBCP

**Status:** proposed, successor 2. **Not applied.** Nothing is created, altered or written on any live or served database until the operator gives an explicit yes and the committed-DBCP apply gate runs.

| | |
|---|---|
| ADR | DEC-fbc085 (D627), proposed |
| Task | TSK-56c689 |
| Plan | PLN-31c4a1 (Platform Readiness), critical path before 7c-c (TSK-e75f1d) |
| Review | Codex `gen-1afb60`. 01 → RESPONSE 01, CHANGES REQUIRED F1–F4. 02 → RESPONSE 02, CHANGES REQUIRED F2/F4/F5, with F1 (ordinary roles) and F3 supported; Q5 and Q6 ruled. This successor answers every open item (§10). |
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

### 4.2 Producer and privilege boundary (F1, Q5)

| Object | Owner | Who may write | Notes |
|---|---|---|---|
| `contract.{canonical,observation}_contract_version_transition` | `bc_schema_owner` (NOLOGIN, exists, no members) | INSERT: **only** `bc_contract_evidence_emitter`. No ordinary principal holds any write privilege | `REVOKE ALL … FROM PUBLIC`; SELECT for the served login and `chain_auditor_readonly` |
| `bc_contract_evidence_emitter` | — | NOLOGIN, **new role** (D6); no members | holds only: USAGE on `contract`, INSERT on the two tables, SELECT on the two version tables (for the guard's cross-check) |
| `contract.fn_contract_version_transition_emit()` | `bc_contract_evidence_emitter` | trigger only; no PUBLIC EXECUTE | `SECURITY DEFINER`, `SET search_path = pg_catalog` |
| `contract.fn_contract_version_transition_guard()` (BEFORE INSERT on the evidence tables) | — | — | refuses unless `current_user = bc_contract_evidence_emitter`, `pg_trigger_depth() >= 2`, and the version's current state equals `to_state_code`. Re-derives principal, transaction id and time |
| append-only trigger | — | — | `BEFORE UPDATE OR DELETE OR TRUNCATE … FOR EACH STATEMENT` → `infrastructure.fn_reject_mutation()` |

**Owner and recovery boundary (F4 correction).**
- The owner, `bc_schema_owner`, **deliberately keeps** its inherent table-owner privileges: DDL, trigger enable/disable, and GRANT. That is the recovery/migration authority.
- It is NOLOGIN and has **no members**. It is reached only by superuser `SET ROLE` inside a separately authorized migration or recovery act, which is a HALT/evidence-gap disposition (§8).
- Even for the owner, the append-only trigger refuses UPDATE, DELETE and TRUNCATE while it is enabled (T11). The owner can disable it; that is the recovery authority, and the gate detects it.
- The gate therefore checks **effective** privileges and **membership** for every *ordinary* principal (§4.7), not a flat grant list. The owner is expected to hold privileges; nobody else may hold them or inherit them.

**Q5 ruling (Codex RESPONSE 02): the database part of W6-P is a prerequisite of the dependent 7c-c lifecycle.**

Today the served login `barecount` is a superuser (`rolsuper = t`). It **owns** `contract.{canonical,observation,source,admission}_contract_version` and the `contract` schema itself (READ ONLY catalog, 2026-09-26; no role memberships exist). The restricted-producer boundary therefore does not bind the served process until the following hold. Each is proved on the clone (§8) and then live, before 7c-c:

1. **Login.** The served bc-core process connects as a **non-superuser** login, without `BYPASSRLS` or `REPLICATION`.
2. **Membership.** That login is not a member, directly or inherited, of `bc_schema_owner`, `bc_contract_evidence_emitter`, any superuser role, or the owner of any object below.
3. **Ownership.**
   - The version tables and the evidence tables are owned by `bc_schema_owner`, not by the served login: a table owner can `DISABLE TRIGGER`.
   - The `contract` schema is owned by a NOLOGIN owner, not by the served login: a schema owner can `DROP SCHEMA … CASCADE`.
   - The emitter function is owned by `bc_contract_evidence_emitter`.
4. **Refusals the served login must hit.** `SET ROLE` to the owner or emitter, `ALTER TABLE … DISABLE TRIGGER`, `SET session_replication_role = replica`, direct INSERT/UPDATE/DELETE/TRUNCATE on evidence, and calling the emitter are all refused (T9, T14).
5. **Separate authority.** Privileged migration/recovery authority stays separate: superuser, or `bc_schema_owner` via `SET ROLE`, each only within a separately authorized act.

This is the database-capability slice of TSK-1a240c (W6-P). The AWS and OS parts of that task are not pulled in. The live apply of the slice is its own DBCP and operator gate, owned with W6-P. No exception is claimed and no grant is inferred.

### 4.3 Context declaration: exact-target, one-shot keys (F2)

Every writer names the **exact** transitions it performs, inside the writing statement, as an uncorrelated sub-select (one init-plan):

```sql
UPDATE contract.canonical_contract_version SET governance_state_code = $to
 WHERE canonical_contract_id = $id AND version_code = $v
   AND (SELECT contract.fn_declare_transition_context('canonical',
          jsonb_build_array(jsonb_build_object('id', $id, 'version', $v, 'to', $to)),
          $cause, $actor_kind, $subject, $correlation, $rationale));
```

**Semantics:**
- **Key.** Each declared target is a key `family|contract_id|version|to_state`, carrying its **own immutable context**: cause, actor kind, subject, correlation id, rationale. The whole set is bound to `statement_timestamp()|pg_current_xact_id()`, and a set from any other top-level statement is treated as absent.
- **Conflicts refused.** Declaring the same key twice in one statement is refused, even with the same or a different context.
- **Exact key required.** The emitter emits only for a row whose **exact** key (including its to-state) is present. It uses **that key's** context, then removes the key (one-shot). An undeclared row, even a sibling in the same statement, is refused.
- **Consume.** An AFTER-STATEMENT trigger removes the family's unused keys. A declared-but-unused key therefore cannot authorize a later statement that shares the statement timestamp (inside a DO block or function).
- **Bulk.** There is no wildcard. The writer declares every exact target in one declaration, which is the bounded shared context Codex allows. `bulkTransition` becomes: `SELECT … FOR UPDATE` the target keys, then one UPDATE restricted to exactly those keys with one declaration.
- **Compound statements** (data-modifying CTEs, nested writes): every emitted row is attributed from its own exact key, or the statement is refused. **Never misattributed.** Proved:
  - T13a: two declared same-family CTEs, each attributed correctly;
  - T13b: an undeclared sibling CTE, refused;
  - T13c: declared cross-family CTEs, each attributed correctly;
  - T13d: a conflicting declaration, refused;
  - T13e: a key for another to-state, refused;
  - T13f: a leftover key in a DO block, refused.

  bc-core itself issues no compound transition statements; this is the database guarantee for any writer.
- **Limit.** Declared contexts live in one custom setting, so a very large bulk (thousands of targets) is bounded by setting size. The code PR caps bulk at a stated maximum per statement.

**Actor kinds** (CHECK on the evidence row; all are writer assertions, not authentication):

| actor_kind | cause(s) | required fields |
|---|---|---|
| `authenticated_http` | `governed_request`, `bulk_transition` | subject (the Cognito sub bc-core verified) and `request_correlation_id` |
| `service_system` | `provisioning_readiness`, `authoring_chain` | subject = the declared component |
| `operator_sql` | `operator_sql` | subject and rationale ≥ 40 characters |

### 4.4 Writers (bc-core code PR)

1. **Repository.**
   - `ContractVersionRepository.updateVersionState(…, exec, context: TransitionContext)` embeds its one exact-target declaration in the UPDATE (§4.3).
   - `ContractAnalyticsRepository.bulkTransition(…, context)` first runs `SELECT … FOR UPDATE` on the exact targets, in the same transaction, then runs one UPDATE restricted to those keys with one declaration listing all of them, capped per statement.
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

**Rule (DEC-fbc085 point 7).** Every platform-plane governed lifecycle state surface must emit an append-only, same-transaction record through a restricted producer. That producer fails closed on any row whose exact transition was not declared. Platform acts never use the tenant-plane `EvidenceService`.

**Gate:** a bc-core `src/__architecture__/` spec, run against the CI database built from the DDL set.

1. **Surface enumeration.**
   - Automatic: base tables in schema `contract` with a column `governance_state_code`, or `status_code` on a `*_version` table.
   - Declared, by exact catalog coordinate: `runtime.connection.connection_status`; `runtime.reader_binding` and `runtime.reader_observation_binding` (bind/unbind rows); `runtime.admission_run.run_status`. Note the column is **`run_status`**; the service field `status` maps to it (`reader.repository.ts` → `runStatus`, `src/database/schema/runtime/reader.ts`).
   - A declared coordinate that **does not exist** in the catalog turns the gate **red**; it is never silently skipped.
   - A new matching surface that is neither covered nor baselined turns the gate red.
2. **Coverage (catalog)** for each covered surface:
   - emit trigger enabled (`tgenabled IN ('O','A')`; red on `D`/`R`), with events exactly AFTER ROW INSERT + UPDATE OF the state column, and the correct family argument;
   - emitter owned by `bc_contract_evidence_emitter`, `prosecdef`, `search_path=pg_catalog`, with no EXECUTE for PUBLIC or any ordinary principal;
   - consume trigger present;
   - INSERT guard present;
   - append-only trigger including TRUNCATE;
   - FK to the version table;
   - evidence tables and version tables owned by `bc_schema_owner`, and schema `contract` owned by a NOLOGIN role.
3. **Effective privilege (not a flat grant list)**, for every **ordinary** principal: the served login(s), `bc_tenant_runtime`, `bc_tenant_owner`, `chain_auditor_readonly` and the `bc_audit_*` logins, taken from an explicit principal registry in the spec.
   - Must not be superuser, `BYPASSRLS` or `REPLICATION`.
   - Must not be a member, including inherited, of `bc_schema_owner`, the emitter or any object owner.
   - `has_table_privilege` for INSERT/UPDATE/DELETE/TRUNCATE/TRIGGER/REFERENCES on evidence tables must be false; TRIGGER/TRUNCATE on version tables must be false.
   - No EXECUTE on the emitter.
   - The owner `bc_schema_owner` is the one deliberate exception: expected to hold owner privileges and to have no members.
4. **Behaviour.** The §5 corpus runs in CI against the same database.
5. **Baseline** (SHRINK-ONLY; every entry has a real task id):

   | Surface (exact catalog coordinate) | Task |
   |---|---|
   | `contract.source_contract_version.governance_state_code`, `contract.admission_contract_version.governance_state_code` | TSK-f5c69f |
   | `contract.ai_contract_version.governance_state_code` | TSK-0f4037 |
   | `contract.intervention_contract_version.status_code` | TSK-9f42ef |
   | `runtime.connection.connection_status` | TSK-c21423 |
   | `runtime.reader_binding`, `runtime.reader_observation_binding` | TSK-fa4d71 |
   | `runtime.admission_run.run_status` | TSK-af45a4 |

   The gate goes red on: a missing task id; a stale or resolved entry; a nonexistent declared coordinate; a new uncovered surface; a disabled, replica-only or wrong-event emitter; a wrong family argument; a removed guard or removed TRUNCATE protection; or an ordinary principal gaining a privilege or membership.
6. **#830.** The #830 dependency-baseline removal (§4.4 item 3) is separate and closes none of these debts.

## 5. Evidence so far: prototype corpus (NOT a migration rehearsal)

| | |
|---|---|
| Artifact | `contract-version-transition-evidence-prototype.sql` (this directory). Hash in the gen-1afb60 successor message |
| Transcript | `contract-version-transition-evidence-prototype-run-2026-09-26.txt` |
| Engine | throwaway `postgres:17.11-alpine` (`sha256:b0f9560a…52b24`), `--network none`. The runner waits for final TCP readiness (`pg_isready -h 127.0.0.1`, avoiding the init-server race Codex hit). The container **and its anonymous volume** are removed after each run. bc-postgres is never touched |
| Roles | the corpus runs as a **non-superuser LOGIN** `served_app`, modelling the W6-P posture. The scaffold version tables are owned by `bc_schema_owner`. T10/T11 use superuser `SET ROLE` to exercise the emitter and the owner |

Result: **ALL PASS** (exit 0).

| Test | Proves |
|---|---|
| T1 | undeclared UPDATE refused |
| T2 | the 7c-c sequence across both families: exact attribution, order by `transition_seq`, digest representation |
| T3 | A declared then B undeclared in one transaction → refused; the same in one DO block → refused |
| T4 | a declaration from an earlier statement authorizes nothing later; savepoint rollback restores nothing usable |
| T5 | rollback leaves 0 rows; same-state UPDATE and draft INSERT emit 0 and need no declaration |
| T6 | non-draft INSERT: undeclared refused; declared emits one birth row |
| T7 | refused: invalid cause; `authenticated_http` without correlation id; short operator rationale; missing subject |
| T8 | bulk: one declaration naming both exact targets → 2 rows; a key covering only one of two rows → refused |
| T13a–f | compound/F2: two same-family CTEs each correctly attributed (committed-then-checked, rolled back); an undeclared sibling CTE refused; cross-family CTEs each correctly attributed; a conflicting double declaration refused; a key for another to-state refused; a leftover declared-but-unused key in a DO block refused |
| T15 | F5, both families: row 1 **actually emits** (precondition proved: the evidence identity sequence advances by exactly 2, one committed-then-rolled-back emission plus one failing), then row 2 fails at emission. Afterwards: 0 evidence rows and 0 state changes |
| T9 | the served login cannot: insert/alter/delete/truncate evidence; call the emitter; `SET ROLE` emitter or owner; `DISABLE TRIGGER` on version or evidence tables (not owner); set `session_replication_role` |
| T14 | effective privileges and inherited membership for every ordinary principal (catalog) |
| T12 | principal derived from the writing login |
| T10 | even the emitter role cannot insert outside the trigger |
| T11 | the owner is refused DELETE/TRUNCATE by the append-only trigger |

**Prove-red** (variants generated from the committed file; each must fail):

| Variant | Change | Result |
|---|---|---|
| A | consume trigger removed | T13f leftover key authorizes a later statement → red |
| B | guard removed | T10 forged insert succeeds → red |
| C | TRUNCATE not rejected | T11 → red |
| D | statement-wide context (any declared key authorizes any row, first context used): the successor-1 class of defect | red at T13e (a key declared for another to-state authorizes the row). Under D, the T8 and T13b outcomes depend on row order, which is exactly why exact keys are required |
| F | failing row ordered first | T15's precondition check detects that no successful emission preceded the failure → red |

**Limits:**
- the version tables are stand-ins, not a restored `bc_platform_dev`;
- no bc-core code, no pooling, no real served login;
- mechanism evidence only; **not** the pre-live rehearsal of §8.

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
| One context per statement (successor 1: declaration sets session fields, the last declaration wins) | 02-F2: compound statements misattribute or inherit; reproduced by Codex and by prove-red D |
| A GUC set by a separate statement, transaction-local | F2: it leaks to later statements; reproduced by Codex, and by T3/T4 without the reset |
| Invoker emitter + served INSERT grant | F1: fabrication possible |
| `PG_CONTEXT` string match as the only guard (the ctae style) | Weaker than privilege; kept only as a secondary idea, not used |

## 8. Sequencing and gates (F3, Q5, Q6)

**Prerequisite.** The database-capability slice of W6-P (§4.2, Q5). It has its own DBCP and operator gate, is owned with TSK-1a240c, and is proved on the clone and then live **before** the dependent 7c-c lifecycle.

**Pre-live, all on an isolated restored clone. No live gate is requested until this is complete and accepted.**
1. **Build and pin:**
   - the bc-core code PR;
   - the DDL + rollback files (`docker/redesign/02-platform-tables/…`, `schema_migration_event` record);
   - the role + ownership script (emitter role; ownership of the version tables, evidence tables and `contract` schema moved to NOLOGIN owners; the served login demoted per W6-P);
   - the rehearsal driver.

   Each is pinned by commit and sha256, and the composition by the combined serve-move head (TSK-4636d8).
2. **Restore** a named clone of `bc_platform_dev`. Record the pre-state: cc-dh5d9 and OC states, triggers, owners, role, membership and grant inventory, `schema_migration_event` head.
3. **Apply** role, ownership and DDL to the **clone only**. Record the post-state (catalog gate green).
4. **Run** the composed build against the clone **as the actual least-privilege served login**:
   - the §5 corpus on the real tables;
   - the bc-core integration tests: A-then-B, two actors, nested and rolled-back service calls, pooled connection reuse, missing request identity, invalid cause, non-draft INSERT;
   - the 7c-c lifecycle through the served API, expecting exactly the T2 rows;
   - proof of the process's effective identity and privileges (T9/T14 against the real login);
   - receipts bound to exact identities.
5. **Submit** the exact package to Codex for acceptance.

**Live, only after acceptance, each gate separately (Q6: accepted in principle as a deliberately fail-closed compatibility window):**

6. **W6-P database slice live** (its own gate).
7. **DDL + role apply** (operator's yes, D5, committed-DBCP gate), **before** the code serve. The window is an **operational interruption**: every CC/OC state write is refused until step 8.
   - **Controlled at the window:**
     - the served pid runs no scheduler (`BC_SCHEDULER_ENABLED` absent);
     - no in-flight HTTP transition, authoring run (`runtime.chain_authoring_run`) or owner-worker command touching CC/OC state;
     - no operator script;
     - state baselined before and after.
   - **Demonstrated:** the old code's refusal is proved in the clone rehearsal (step 4 runs the old served build against the applied schema). Live, no synthetic transition or disposable row is created; any transition attempted during the window is observed refused, with state unchanged.
8. **Combined serve move** (EXECUTION CLEARED + the operator's exact grant).
9. **7c-c execution request**, with the receipts.

**Rollback:**
- **Before any live transition row exists:** revert the code; drop the triggers, functions and tables; drop the role (operator yes).
- **After rows exist:** disabling or dropping emission is an **explicit HALT/evidence-gap disposition** with its own exact authority. The rows are retained and the gate stays red.
- **No automatic evidence-free fallback.** A code-only revert while the trigger is present fails closed.

## 9. Sizing

| Unit | Content | Size |
|---|---|---|
| DDL + role + rollback + DBCP apply kit | 2 tables, 1 role, 4 new functions, 10 triggers (emit, reset, consume, guard, append-only × 2 families), 2 indexes, grants; the prototype's Part 1 is the shape | ~200 lines SQL |
| bc-core code PR | context type + threading (repositories ×2, `transitionState`, 6 service callers, 3 controller routes), W3 + dead-call deletion, baseline shrink | ~300 LOC |
| Tests + gate | real-DB integration (throwaway tenant/clone), catalog + behaviour gate, prove-red | ~450 LOC |
| Clone rehearsal + package | §8 steps 1–5 | part of TSK-4636d8 |

About 2 working days of build, plus review rounds. No new npm dependency.

## 10. Reconciliation with Codex

| Finding | Resolution |
|---|---|
| 01-F1 / 02-F1 + Q5 | ordinary-role mechanism (§4.2) reproduced by Codex. Q5: the W6-P database-capability slice is a stated prerequisite, with the exact ownership, membership and refusal list, including schema ownership |
| 01-F2 / 02-F2 | exact-target one-shot keys with their own contexts; conflicts refused; undeclared siblings refused; consume per family; no wildcard bulk. T13a–f + prove-red D (§4.3) |
| 01-F3 / 02 Q6 | clone rehearsal and acceptance before any live gate; window treated as an operational interruption with writer control and refusal demonstration (§8) |
| 01-F4 / 02-F4 | `run_status` corrected; a nonexistent coordinate goes red; owner recovery privileges reconciled; an effective-privilege and membership predicate for ordinary principals (§4.2, §4.7) |
| 02-F5 | T15 replaces T8's planning-time failure: a real emission precedes the failure (sequence-proved), both families, prove-red F |
| ADR point 8 | aligned with §6's bounded current-catalog and source-derived claim |

## 11. Operator decisions requested

- **D1.** Option (b): a new platform-plane home.
- **D2.** Per-family tables.
- **D3.** Fail-closed for all writers, including operator SQL with a declared rationale.
- **D4.** A narrow first unit with the task-bound baseline.
- **D6.** A new NOLOGIN role `bc_contract_evidence_emitter`.
- **D7.** Per the Codex Q5 ruling: the W6-P **database-capability slice** (non-superuser served login; version tables, evidence tables and the `contract` schema owned by NOLOGIN owners) is a prerequisite of 7c-c. It gets its own DBCP, owned with TSK-1a240c.
- **D5.** A later "yes" to apply the DDL + role live (§8 step 6), after the accepted clone rehearsal. **Not requested now.**
