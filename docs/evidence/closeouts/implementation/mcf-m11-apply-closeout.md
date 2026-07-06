---
uid: mcf-m11-apply-closeout
title: MCF M11 Reservoir Ingestion Substrate — Apply Closeout
description: Closeout of the MCF M11 Reservoir Ingestion substrate apply gate (DBCP 42f702b). Records the impl PR #120 squash merge (d8f1068), the small-DDL apply via psql ON_ERROR_STOP=1 (atomic BEGIN → CREATE TABLE → CREATE INDEX × 3 → COMMENT → COMMIT), the post-apply verifier failure at T17-01-42 (root cause — writer-side JSONB double-encoding bug; substrate sound), the JSONB writer-encoding patch PR #121 (squash merge ea76cba) that replaced JSON.stringify(payload) + $N::jsonb with object-direct $N::jsonb across the verifier helper + ReservoirIngestionService.insertCandidate + the operator-direct CLI, the clean post-apply verifier pass at T17-13-58 (15/15 PASS), the evidence PR #122 squash merge (c359dc8) staging only the canonical artifact set (dry-run T16-58-37 + post-apply T17-13-58 — failed T17-01-42 explicitly excluded), and the final live DB state (17 mcf.* tables / all 0 rows / M11 substrate live + dormant / BCF 24 panel + 1 rejection log untouched). Records the M9 M1 / M-M5-1 verifier-fix pattern reapplied for the JSONB double-encoding RCA. Records the M11 substrate as substrate-side complete + writer-side correct + dormant, ready for M12 panel implementation. Discipline confirmed throughout: no reservoir data ingested, no M12/M13/M14 gates opened, no metric contracts / fixtures / results / panel runs created, BCF preserved.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m11-apply-closeout
---

# MCF M11 Reservoir Ingestion Substrate — Apply Closeout

## 1. Scope and grounding

This document closes the MCF M11 Reservoir Ingestion substrate apply gate. The gate sequence followed the established M5 / M9 / M10 pattern: impl PR → small-DDL apply → post-apply verifier → evidence PR → closeout. A mid-gate writer-side RCA + patch was inserted between the failed first verifier run and the clean second verifier run; this closeout documents that explicitly so the audit trail names both the failure mode and the fix.

| Authority | Reference |
|---|---|
| ADR | `bc-docs-v3/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422) |
| Preflight | `bc-docs-v3/docs/implementation/metric-context-framework-m11-reservoir-ingestion-preflight.md` (`79142b6`) |
| DBCP | `bc-docs-v3/docs/implementation/metric-context-framework-m11-reservoir-ingestion-dbcp.md` (`42f702b`) |
| Impl PR | bc-core PR #120 — squash commit `d8f106888b4349b3754945024e5064125b108bec` |
| Patch PR | bc-core PR #121 — squash commit `ea76cba740aa50cd6ea840d8d8f92f05f6eaa864` |
| Evidence PR | bc-core PR #122 — squash commit `c359dc8a047639510f42c39aa780e3b248140d54` |
| Forward DDL sha256 | `b7e3f7edcdb8af6f84a154c354571c6f37bd1d5639faabe80d2797b477545239` |
| Rollback DDL sha256 | `733173692b7a41031fa7946b818f862d6d6a09f355e06bec0486a7d9f30befc5` |

## 2. Apply sequence

### 2.1 Impl PR #120 squash merge (`d8f1068`)

PR #120 shipped the M11-B substrate + `ReservoirIngestionService` + 3 source adapters + co_bindings strip helper + CLI + dry-run + post-apply verifier scripts + 54 unit tests + DDL forward/rollback. NO DB APPLY in this PR.

- Branch: `mcf-m11-reservoir-ingestion`
- Files: 18 (2 DDL + 1 Drizzle schema + 1 index.ts + 6 service-layer TS + 4 spec files + 3 mjs scripts + 1 types)
- +2922 / -0
- Patched twice pre-merge: L1–L6 review patches + M1 (tx API consistency) + M2 (LENGTH → char_length byte-match)
- bc-core main after merge: `d8f106888b4349b3754945024e5064125b108bec`

### 2.2 Pre-apply dry-run (Step 1) — `2026-05-27T16-58-37-730Z`

Command:

```bash
node scripts/mcf-m11-dry-run.mjs
```

Result: **exit 0 / 8 checks PASS / 4 HARD-GATEs clear.** Artifact captured the forward + rollback DDL sha256 (above).

### 2.3 Small-DDL apply (Step 2.1)

Command (authorized verbatim per operator instruction):

```bash
cat docker/redesign/11-mcf-reservoir-ingestion.sql | docker exec -i bc-postgres psql -U barecount -d bc_platform_dev -v ON_ERROR_STOP=1
```

Result: **exit 0.** Atomic trace exactly as expected:

```
BEGIN
CREATE TABLE
CREATE INDEX
CREATE INDEX
CREATE INDEX
COMMENT
COMMIT
```

Post-apply substrate live: `mcf.metric_authoring_intake_queue` with 14 columns / 6 CHECK + 1 PK + 1 UNIQUE + 3 indexes / no FK / no trigger, all byte-matched against the DBCP §5.5 spec via `pg_get_constraintdef()`.

### 2.4 Post-apply verifier first attempt (Step 2.3) — `2026-05-27T17-01-42-701Z` — EXCLUDED FROM EVIDENCE

Command:

```bash
node scripts/mcf-m11-post-apply-verification.mjs
```

Result: **exit 8 (FAIL).** 13/15 checks PASS; checks #11 + #12 (`top-level co_bindings REJECTED` + `nested co_bindings REJECTED`) FAILED.

**These artifacts are intentionally EXCLUDED from the evidence PR #122** (canonical evidence is the post-patch clean run, §2.6 below). The failed run is preserved on the bc-core filesystem under `scripts/audit-output/mcf-m11-post-apply-2026-05-27T17-01-42-701Z.*` as local-only forensic data but is not committed to git history.

#### 2.4.1 Root cause analysis

Empirical probes confirmed the substrate `maiq_co_bindings_rejection_chk` regex CHECK is correct and fires when invoked against a JSONB OBJECT:

```sql
SELECT '{"co_bindings":["x"]}'::jsonb::text ~ '"co_bindings"\s*:'  -- true
```

And inserting an object via `postgres-js`:

```js
await sql.unsafe('... $N::jsonb', [{co_bindings: ['x']}])
-- raises: violates check constraint "maiq_co_bindings_rejection_chk"
```

The bug was writer-side. When you pre-stringify (`JSON.stringify(obj)`) and pass the resulting string to `$N::jsonb` or `${value}::jsonb`, postgres-js auto-JSON-encodes the **already-stringified** value again, producing a JSONB **STRING** value rather than a JSONB **OBJECT**:

| Writer path | `jsonb_typeof` | CHECK fires? |
|---|---|---|
| literal `'{"co_bindings":[...]}'::jsonb` | `object` | ✅ yes |
| param OBJECT `[obj]` + `$N::jsonb` | `object` | ✅ yes |
| param STRING `[JSON.stringify(obj)]` + `$N::jsonb` | **`string`** | ❌ **no (bug)** |

The text serialization of a JSONB STRING (e.g. `"{\"co_bindings\":[\"x\"]}"`) escapes the inner quotes, breaking the regex pattern `"co_bindings"\s*:` which requires literal unescaped quotes around the key.

**Impact**: without the patch, all three M11 ingest paths (verifier helper + service + CLI) stored JSONB strings instead of objects, silently bypassing the substrate's Layer-1 last-line-of-defense for `co_bindings` rejection. Layer 2 (service-side recursive strip) + Layer 3 (post-strip assert) still functioned, but the substrate CHECK was effectively disabled by the writer-side encoding bug.

**Why M5/M9/M10 did not hit this**: prior MCF substrates use `tx.execute(sql\`...${object}\`)` with **objects** passed directly (no pre-stringify) — they hit the working path. M11 was the first MCF gate to use `JSON.stringify(payload)` then cast to `::jsonb`, which surfaces postgres-js's double-encoding behavior.

### 2.5 Patch PR #121 squash merge (`ea76cba`)

PR #121 fixed the writer-side encoding in 3 files + added 1 RCA regression-guard test. **NO substrate change, NO rollback.**

- Branch: `mcf-m11-jsonb-encoding-fix`
- Files: 4 (verifier helper + service `insertCandidate` + CLI + service spec)
- +52 / -9
- bc-core main after merge: `ea76cba740aa50cd6ea840d8d8f92f05f6eaa864`

Patch shape across all 3 writer paths (verifier / service / CLI):

| Before | After |
|---|---|
| `${JSON.stringify(value)}::jsonb` | `${value}::jsonb` |
| `JSON.stringify(payload), ... $N::jsonb` | `payload, ... $N::jsonb` |

Regression guard test in `reservoir-ingestion.service.spec.ts`:

> *"passes provenance + normalized_candidate_json as JS OBJECTS to ${value}::jsonb (not pre-stringified) — Step-2 RCA regression guard"*

Asserts `insertCall.params[2]` and `insertCall.params[7]` are `typeof 'object'` AND `!== 'string'`. This locks the fix in against future regressions.

### 2.6 Post-apply verifier clean pass (Step 2.3 post-patch) — `2026-05-27T17-13-58-856Z`

Same command, against the same already-applied substrate (no re-apply, no rollback):

```bash
node scripts/mcf-m11-post-apply-verification.mjs
```

Result: **exit 0 / 15/15 PASS.** All 5 structural + 9 SAVEPOINT-protected behavioral + 1 cleanup checks green.

| # | Check | Type | Result |
|---|---|---|---|
| 1 | 14 cols + 6 CHECKs byte-matched via `pg_get_constraintdef()` | structural | PASS |
| 2 | UNIQUE `uq_maiq_reservoir_entry` present | structural | PASS |
| 3 | 3 non-PK/UNIQUE indexes present | structural | PASS |
| 4 | NO FK (substrate-leaf design) | structural | PASS |
| 5 | NO trigger (status mutability intentional) | structural | PASS |
| 6 | valid INSERT succeeds | behavioral | PASS |
| 7 | duplicate insert-then-dup own-seed pattern REJECTED by UNIQUE | behavioral | PASS |
| 8 | invalid `reservoir_name` REJECTED | behavioral | PASS |
| 9 | invalid `reservoir_confidence_band` REJECTED | behavioral | PASS |
| 10 | invalid `status_code` REJECTED | behavioral | PASS |
| 11 | top-level `co_bindings` REJECTED by regex CHECK | behavioral | PASS (post-patch) |
| 12 | nested `co_bindings` REJECTED by regex CHECK | behavioral | PASS (post-patch) |
| 13 | `co_bindings_stripped_flag = FALSE` REJECTED | behavioral | PASS |
| 14 | rejected status with NULL reason REJECTED | behavioral | PASS |
| 15 | all 17 mcf.* tables empty after verifier | cleanup | PASS |

### 2.7 Evidence PR #122 squash merge (`c359dc8`)

PR #122 staged exactly 5 canonical artifacts and intentionally excluded the failed pre-patch artifacts.

- Branch: `mcf-m11-apply-evidence` (rebased onto `ea76cba` for clean merge)
- Files staged:
  - `scripts/audit-output/mcf-m11-dry-run-2026-05-27T16-58-37-730Z.summary.md`
  - `scripts/audit-output/mcf-m11-dry-run-2026-05-27T16-58-37-730Z.precondition.jsonl`
  - `scripts/audit-output/mcf-m11-dry-run-2026-05-27T16-58-37-730Z.planned-sql.sha256.txt`
  - `scripts/audit-output/mcf-m11-post-apply-2026-05-27T17-13-58-856Z.summary.md`
  - `scripts/audit-output/mcf-m11-post-apply-2026-05-27T17-13-58-856Z.evidence.jsonl`
- Files explicitly EXCLUDED: `mcf-m11-post-apply-2026-05-27T17-01-42-701Z.*` (failed pre-patch run, see §2.4)
- +313 / -0
- bc-core main after merge: `c359dc8a047639510f42c39aa780e3b248140d54`

## 3. Final live DB state

Confirmed via independent `bc-postgres` MCP read-only probe after PR #122 merge:

| Probe | Result |
|---|---|
| `mcf.metric_authoring_intake_queue` exists | **true** |
| `mcf.metric_authoring_intake_queue` rowcount | **0** |
| All 17 mcf.* tables sum rowcount | **0** |
| `contract.panel_output_record` (BCF) rowcount | **24** (preserved) |
| `contract.authoring_panel_rejection_log` (BCF) rowcount | **1** (preserved) |

**M11 substrate is live and dormant.** The 16 prior mcf.* tables (M2 → M10) carry 0 rows; the new M11 table carries 0 rows; BCF (24 panel + 1 rejection log) is untouched.

### 3.1 17 mcf.* tables (post-M11 count)

| Gate | Tables added | Cumulative |
|---|---|---|
| M2 | 5 (`metric_contract`, `metric_contract_version`, `metric_variable_binding`, `metric_filter_clause`, `metric_computed_dimension_ref`) | 5 |
| M3 | 2 (`metric_contract_revision`, `metric_supersession`) | 7 |
| M4 | 3 (`certification_record`, `metric_publication_eligibility_result`, `metric_cert_writer_idempotency`) | 10 |
| M5 | 4 (`metric_authoring_panel_run`, `metric_authoring_panel_transcript`, `workspace_tool_allowlist`, `evidence_source_allowlist`) | 14 |
| M9 | 1 (`metric_self_verification_fixture`) | 15 |
| M10 | 1 (`metric_self_verification_result`) | 16 |
| **M11** | **1 (`metric_authoring_intake_queue`)** | **17** |

## 4. Substrate shape (M11 only)

`mcf.metric_authoring_intake_queue` per DBCP §5.5 + apply-time confirmation:

| Constraint | Definition (per `pg_get_constraintdef()`) |
|---|---|
| `maiq_reservoir_name_chk` | `CHECK ((reservoir_name = ANY (ARRAY['seed_metrics'::text, 'metric_definition'::text, 'operator_direct'::text])))` |
| `maiq_confidence_band_chk` | `CHECK ((reservoir_confidence_band = ANY (ARRAY['high'::text, 'medium'::text, 'low'::text])))` |
| `maiq_status_code_chk` | `CHECK ((status_code = ANY (ARRAY['pending'::text, 'consumed_by_panel'::text, 'rejected'::text, 'superseded'::text])))` |
| `maiq_co_bindings_rejection_chk` | `CHECK ((NOT ((normalized_candidate_json)::text ~ '"co_bindings"\s*:'::text)))` |
| `maiq_co_bindings_stripped_flag_chk` | `CHECK ((co_bindings_stripped_flag = true))` |
| `maiq_rejected_status_requires_reason_chk` | `CHECK (((status_code <> 'rejected'::text) OR ((status_reason_text IS NOT NULL) AND (char_length(status_reason_text) >= 20))))` |
| `uq_maiq_reservoir_entry` | UNIQUE `(reservoir_name, reservoir_entry_id)` |

Plus 1 PK on `intake_queue_uid` and 3 non-PK / non-UNIQUE indexes (`idx_mcf_maiq_status`, `idx_mcf_maiq_reservoir_name`, `idx_mcf_maiq_ingested_at`). NO FK; NO trigger.

## 5. 3-layer co_bindings enforcement (post-patch)

| Layer | Where | Mechanism | Verified by |
|---|---|---|---|
| 1 | Substrate (DDL) | `maiq_co_bindings_rejection_chk` JSONB regex matches `"co_bindings"\s*:` at any nesting level in the JSONB text serialization | Post-apply verifier #11 + #12 (PASS) |
| 2 | Service (TypeScript) | `stripCoBindings()` recursive removal helper at every nesting level (case-sensitive on exact key) | Unit tests in `co-bindings-strip.spec.ts` (14 tests) |
| 3 | Service (TypeScript) | `assertCoBindingsStripped()` post-strip JSON re-serialize regex check; throws `CoBindingsLeakError` | Unit tests in `co-bindings-strip.spec.ts` + regression guard in `reservoir-ingestion.service.spec.ts` |

The Step-2 RCA + PR #121 patch restored Layer 1 to functioning state for all three writer paths (verifier helper, `ReservoirIngestionService.insertCandidate`, operator-direct CLI). The regression guard test in PR #121 locks the writer-side encoding pattern in.

## 6. Discipline confirmation (gate boundary)

- ✅ NO reservoir data ingested — substrate is dormant; `mcf.metric_authoring_intake_queue` rowcount is 0
- ✅ NO real MCF metric contracts created — all 17 mcf.* tables 0 rows
- ✅ NO fixtures / results / panel runs created — substrate-side only
- ✅ NO M12 / M13 / M14+ work — gates remain closed
- ✅ NO BCF data touched — `contract.panel_output_record` preserved at 24 rows, `contract.authoring_panel_rejection_log` preserved at 1 row
- ✅ NO Mongo connection attempts — verifier check #4 reads env vars only; check #5 is filesystem inspection
- ✅ `bc-postgres` MCP `allow_write=false` throughout the gate
- ✅ Apply was authorized verbatim by operator via the `docker exec -i bc-postgres psql ... ON_ERROR_STOP=1` command form

## 7. M9 M1 / M-M5-1 pattern reapplied

This gate exercised the established MCF verifier-fix pattern for the third time:

| Gate | Verifier-fix incident | Pattern applied |
|---|---|---|
| M5 (M-M5-1) | post-apply verifier needed SAVEPOINT protection on behavioral exercises; introduced verifier-fix patch + re-run | `mcf-m11-post-apply-verification.mjs` ships SAVEPOINT-protected from the start |
| M9 (M1) | golden vector hash was tautologically computed via the same primitives as SUT; introduced hardcoded literal sha256 captured via one-off script | `mcf-m11-post-apply-verification.mjs` uses `pg_get_constraintdef()` byte-match, not SUT-primitive recomputation |
| **M11 (this gate)** | post-apply verifier exposed writer-side JSONB double-encoding via postgres-js auto-JSON-stringify of `$N::jsonb` params; substrate sound, writer-side bug in 3 files | PR #121 patches all 3 writer paths to pass objects directly; adds regression-guard test that asserts param types are objects, not strings; **no DDL change, no rollback** |

The lesson generalizes: **post-apply verifiers expose real production bugs that unit tests cannot, because the substrate-side discipline only fires when the wire-protocol parameter encoding matches the column type the constraint operates on.** Pre-apply unit testing of the writer-side, even with a fake tx, cannot catch this without round-tripping through real postgres-js + Postgres.

## 8. Next gate

M12 — Metric Authoring Panel implementation. Gated on:
- M11 substrate live + dormant ✅ (this closeout)
- M12 amendment to add `mcf.metric_authoring_panel_run.consumed_intake_queue_uid` + FK back to `mcf.metric_authoring_intake_queue(intake_queue_uid)` — owned by M12 DBCP per M11 DBCP §3.1 + §4.2

M11 + M12 combined enables the first content-flow milestone: real reservoir-attributed panel runs.

## 9. What stays closed

| | |
|---|---|
| M11 substrate post-rollback restoration | NOT attempted — substrate is correct; only writer-side needed fixing |
| M12 panel implementation | CLOSED until M12 DBCP gate is opened |
| M13 PE-MC evaluator | CLOSED |
| M14+ | CLOSED |
| Real MCF metric contracts | CLOSED — substrate remains empty pending M12 + operator ingestion runs |
| Real intake-queue rows | CLOSED — operator manually invokes `ReservoirIngestionService` / CLI when ready |
| BCF data changes | CLOSED — 24 BCF panel + 1 rejection log preserved across the entire MCF M11 arc |
