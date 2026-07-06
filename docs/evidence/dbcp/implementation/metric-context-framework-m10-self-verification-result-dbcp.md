---
uid: metric-context-framework-m10-self-verification-result-dbcp
title: MCF M10 Self-Verification Result Substrate + Verifier Engine DBCP
description: Combined design-blueprint for MCF gate M10 (Deterministic Verifier Service + Result Substrate) per operator-accepted preflight decisions D-M10-1..D-M10-10 + D-M10-A1 (preflight 60930fa). Realizes M10-A — append-only ledger + JSONB diff trace + sync NestJS-injectable verifier service with deps.tx — per build plan §M10 + MCF §17.1 substrate spec + §12.6 verifier pipeline. Substrate change ALL IN ONE NEW TABLE — mcf.metric_self_verification_result (13 columns; 10 constraints — 1 PK + 3 intra-mcf FK fk_msvr_fixture/fk_msvr_mc/fk_msvr_mcv all ON DELETE RESTRICT + 5 CHECK 1 verdict-enum + 2 sha256-format + 1 algo-version regex + 1 non-negative-duration + 1 UNIQUE on (fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run) for substrate-side idempotency) + 4 indexes (lookup-by-fixture, lookup-by-mcv, lookup-by-verdict, lookup-by-executed-at) + 1 trigger function mcf.fn_msvr_immutability_check + 1 trigger attachment trg_msvr_immutability BEFORE UPDATE OR DELETE (M3/M5-style unconditional reject post-INSERT per D-M10-9 evidence-grade defense-in-depth). PLUS 1 FK activation (fk_mper_verification_result on mcf.metric_publication_eligibility_result.satisfying_verification_result_uid → mcf.metric_self_verification_result(verification_result_uid); deferred since M4 per D-16) + 1 COMMENT ON COLUMN UPDATE correcting the M4 doc-bug per D-M9-8. New service MetricSelfVerificationService.verifyFixture(fixtureUid, deps) executing the §12.6 6-step pipeline; reuses M9 FixtureStructuralCheckService.runStructuralChecks (no duplicate C-FX engine) + M9 PackageSignatureService.computeSelfVerificationFixtureHash (no duplicate hash machinery) + M7/M8 FormulaCanonicalizationService + PackageSignatureService for current-package hash recomputation. New FormulaExecutionEngine in M10 implementing per-AST-kind handlers for all 9 NODE_KINDS (variable_ref / literal / aggregate / arithmetic / comparison / case / window / time_anchor_resolution / bucket_assign) per build plan §M10 acceptance criteria. New ResolverFixtureConfigInterpreter applying Section C runtime configs (fiscal_calendar / bucket_specs / derived_grain_params). New OutputComparator with per-fixture tolerance + null-match policy semantics. JSONB diff trace per D-M10-3 (structured child rows deferred). Algorithm version mcf-verifier-v1 per D-M10-4 (separate bundle from mcf-hash-v1; verifier is a different algorithm class). 11 operator approvals (O-M10-1..O-M10-11). All atomic inside one BEGIN/COMMIT per §15 + M3/M5/M7-M8/M9 atomicity pattern. Rollback file with row-count precondition guard refusing reverse if result rows exist + reverses FK activation + restores M4 inline comment + drops trigger/function/table in safe order. Dry-run verifier plan (8 checks; 4 HARD-GATEs). Post-apply verifier plan (16 checks; 6 structural + 9 behavioral SAVEPOINT-protected synthetic-row exercises per M-M5-1 verifier-fix discipline + 1 cleanup). Unit/integration test plan: golden-vector verdicts per AST kind (positive + negative pairs for 9 kinds = 18 tests minimum) + property-style cross-checks per D-M10-10 + tolerance/null-match comparator unit tests + idempotency integration test + stale-fixture rejection integration test. Recommended next gate: M10 implementation PR (NO DB APPLY) shipping substrate + verifier service + FormulaExecutionEngine + ResolverFixtureConfigInterpreter + OutputComparator + dry-run + post-apply verifier scripts. NO bc-core edits this session. NO DDL apply this session. NO data writes this session. NO real MCF metric contracts. NO fixture rows. NO BCF data touches. NO M11/M12/M14+ work.
status: draft
date: 2026-05-27
project: bc-docs
subdomain: catalog
focus: mcf-m10-self-verification-result-dbcp
---

# MCF M10 Self-Verification Result Substrate + Verifier Engine DBCP

## 1. Scope and grounding

Design the M10 substrate + verifier engine that closes the fixture/verifier pair. M9 shipped the fixture body + structural-check engine + hash helper; M10 ships the verifier that executes packages against fixtures and the append-only result ledger PE-MC-10 (M13) cites.

The substrate change ships in **one combined DBCP** per D-M10-A1 covering substrate + verifier service + execution engine + reproducibility tests. Implementation may split into M10-substrate + M10-engine PRs at operator discretion (mirrors M9 PR #115 / PR #117 split); the design here covers the whole M10 unit.

The substrate stays **dormant** post-apply: no result rows are written. Real verification runs require M11 ingestion + M12 panel + operator-driven fixture authoring + operator-driven verifier invocation.

### 1.1 Source documents consumed

| Source | Role |
|---|---|
| M10 preflight (`60930fa`) | Decision options + recommendations the operator accepted |
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority |
| MCF requirements §12.6 (verifier behavior) | 6-step pipeline ending in pass/fail/structural_reject |
| MCF requirements §12.7 (stale-fixture rule) | bound_package_signature_hash binding + stale check |
| MCF requirements §13 PE-MC-10 | Result row cited; satisfying_verification_result_uid FK target |
| MCF requirements §17.1 (per-MCV substrate) | "append-only per Invariant V; one row per execution" |
| MCF build plan §M10 | Verifier scope; T-shirt L; primary risk underbuilding verifier; coverage = all §7.2 AST kinds |
| M9 DBCP (`620e11d`) | §6.4 hash helper + §7.4 C-FX engine + §11.1 M10 reuse boundary + §11.4 M4 doc-bug |
| M9 closeout (`17669ba`) | Live state (15 mcf.* tables; M9 substrate live + dormant) |
| M9 engine (bc-core PR #117 / `bcc5705`) | FixtureStructuralCheckService + computeSelfVerificationFixtureHash live |
| Live `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` column | M4-shipped; FK-less; awaits M10 activation |
| Live `06-mcf-lifecycle-certification.sql:179` | M4 inline comment (doc-bug per D-M9-8) |
| Live `formula-canonicalization.service.ts` `NODE_KINDS` | 9 AST kinds the FormulaExecutionEngine must handle |

### 1.2 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits this session | ✓ — read-only |
| No DDL applied | ✓ — DBCP designs the substrate change; apply is a separate gate |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No fixture rows | ✓ — M9 substrate dormant |
| No verification results written | ✓ — substrate stays empty post-M10 apply |
| No BCF data touched | ✓ — 24 BCF panel + 1 rejection log untouched |
| No M11 / M12 / M14+ work | ✓ — downstream gates |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. Accepted operator decisions (D-M10-1..D-M10-10 + D-M10-A1)

| # | Decision | Locked |
|---|---|---|
| **D-M10-1** | ACCEPT M10-A — append-only ledger + JSONB diff trace + sync verifier service (per build plan §M10 + §17.1) | ACCEPTED |
| **D-M10-2** | Table shape includes `executor_identity_text` + `execution_duration_ms` for forensic value | ACCEPTED |
| **D-M10-3** | Diff trace JSONB for v1; structured child rows deferred | ACCEPTED |
| **D-M10-4** | Verifier algorithm marker = `mcf-verifier-v1` (separate bundle from `mcf-hash-v1`) | ACCEPTED |
| **D-M10-5** | Sync NestJS-injectable verifier service with `deps.tx`; async queue deferred | ACCEPTED |
| **D-M10-6** | Stale fixture produces `structural_reject` with reason `stale_fixture`; substrate stores both `fixture_bound_package_signature_hash` + `bound_package_signature_hash_at_run` | ACCEPTED |
| **D-M10-7** | Activate `fk_mper_verification_result` inline in M10 DDL (atomic with table CREATE) | ACCEPTED |
| **D-M10-8** | Fold M4 doc-bug correction inline via `COMMENT ON COLUMN` UPDATE | ACCEPTED |
| **D-M10-9** | Use substrate **append-only trigger** for `mcf.metric_self_verification_result` (UPDATE/DELETE rejected) — evidence-grade defense-in-depth | ACCEPTED |
| **D-M10-10** | Golden-vector verdict tests per AST kind (9 kinds × 2 positive+negative = 18 minimum) + property-style cross-checks | ACCEPTED |
| **D-M10-A1** | Combined DBCP covering substrate + verifier service; impl PR may still split if justified | ACCEPTED |

---

## 3. Current live substrate and code state

After bc-core `bcc5705` + bc-docs-v3 `60930fa`:

| | |
|---|---|
| bc-core main | `bcc5705` (M9 engine merged via PR #117) |
| bc-docs-v3 main | `60930fa` (M10 preflight) |
| `mcf.*` tables | **15 present, all 0 rows** |
| `mcf.metric_self_verification_result` | does NOT yet exist |
| `mcf.fn_msvr_immutability_check` / `trg_msvr_immutability` | does NOT yet exist |
| `fk_mper_verification_result` FK | DEFERRED — column live but FK-less |
| M4 inline comment at `06-mcf-lifecycle-certification.sql:179` | doc-bug present (says "M9"; should say "M10") |
| M9 fixture substrate + engine | LIVE; dormant |
| M9 services on bc-core | `FixtureStructuralCheckService` + `PackageSignatureService.computeSelfVerificationFixtureHash` |
| BCF | untouched (24 panel + 1 rejection log) |

### 3.1 FK target presence verified

| FK target | Status |
|---|---|
| `mcf.metric_self_verification_fixture(fixture_uid)` | LIVE (M9 substrate apply) |
| `mcf.metric_contract(metric_contract_uid)` | LIVE (M2) |
| `mcf.metric_contract_version(metric_contract_version_uid)` | LIVE (M2) |
| `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` column | LIVE (M4 substrate); awaiting FK activation |

---

## 4. M10 ownership boundary

### 4.1 M10 MUST own

| # | Deliverable | Location |
|---|---|---|
| 1 | `mcf.metric_self_verification_result` table (13 cols; per §5) | New DDL `10-mcf-self-verification-result-substrate.sql` |
| 2 | 5 CHECK constraints (verdict-enum + 2 sha256-format + 1 algo-version regex + 1 non-negative-duration) | Inline in CREATE TABLE |
| 3 | 1 UNIQUE on `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` | Inline |
| 4 | 3 intra-mcf FKs (fixture / mc / mcv) all ON DELETE RESTRICT | Inline |
| 5 | 4 indexes (lookup-by-fixture / mcv / verdict / executed_at) | CREATE INDEX |
| 6 | Append-only trigger function + attachment (`mcf.fn_msvr_immutability_check` + `trg_msvr_immutability`) per D-M10-9 | DDL §11 |
| 7 | FK activation `fk_mper_verification_result` per D-M10-7 | DDL §12 |
| 8 | `COMMENT ON COLUMN` UPDATE correcting M4 doc-bug per D-M10-8 | DDL §13 |
| 9 | `COMMENT ON TABLE` on new result table | DDL §13 |
| 10 | `MetricSelfVerificationService.verifyFixture(fixtureUid, deps)` (§12.6 6-step orchestrator) | New service `bc-core/src/registry/mcf/metric-self-verification.service.ts` |
| 11 | `FormulaExecutionEngine` (per-AST-kind handlers for 9 `NODE_KINDS`) | New service `bc-core/src/registry/mcf/formula-execution.engine.ts` |
| 12 | `ResolverFixtureConfigInterpreter` (Section C runtime application) | New service `bc-core/src/registry/mcf/resolver-fixture-config.interpreter.ts` |
| 13 | `OutputComparator` (tolerance + null-match policy) | New service `bc-core/src/registry/mcf/output-comparator.ts` |
| 14 | Reuse of M9 `FixtureStructuralCheckService.runStructuralChecks` (§12.6 step 4 C-FX re-check) — no duplicate implementation | Imported |
| 15 | Reuse of M9 `PackageSignatureService.computeSelfVerificationFixtureHash` (§12.6 step 2 fixture lookup cross-check) — no duplicate hash machinery | Imported |
| 16 | Drizzle schema + index.ts re-export | `bc-core/src/database/schema/mcf/metric-self-verification-result.ts` + `index.ts` |
| 17 | Dry-run + post-apply verifier scripts | `bc-core/scripts/mcf-m10-dry-run.mjs` + `mcf-m10-post-apply-verification.mjs` |
| 18 | Rollback DDL with row-count precondition guard | `10-mcf-self-verification-result-substrate-rollback.sql` |
| 19 | Unit tests: per-AST-kind execution + tolerance comparator + null-match policy | `*.spec.ts` for each new service |
| 20 | Integration tests: full §12.6 pipeline + stale-fixture path + idempotency | `metric-self-verification.service.integration.spec.ts` |

### 4.2 M10 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | Fixture authoring path | **M12** Metric Authoring Panel |
| 2 | Reservoir ingestion | **M11** |
| 3 | PE-MC-10 evaluator (consumer of result rows) | **M13** |
| 4 | Publication path | **M14** |
| 5 | Real fixture rows | substrate stays empty |
| 6 | Real verification results | substrate stays empty |
| 7 | Real MCF metric contracts | substrate stays empty |
| 8 | BCF data | NEVER in MCF gates |
| 9 | Operator-console UI | **M16** |
| 10 | Async-queue verifier infrastructure | Future amendment if performance demands (D-M10-5 deferred) |
| 11 | Per-diff-row child table | Future amendment (D-M10-3 deferred) |
| 12 | Duplicate C-FX engine implementation | NEVER — reuse M9 |
| 13 | Duplicate hash machinery | NEVER — reuse M9 + M7/M8 |
| 14 | Tolerance + null-match policy DEFAULTS catalog (per type/unit) | Future enhancement (§19.13 Q38 open); v1 ships sensible defaults |

---

## 5. Result table design: `mcf.metric_self_verification_result`

### 5.1 Column inventory (13 columns)

| Column | Type | NULL | Default | Notes |
|---|---|---|---|---|
| `verification_result_uid` | `uuid` | NOT NULL | `gen_random_uuid()` | PRIMARY KEY |
| `fixture_uid` | `uuid` | NOT NULL | — | FK to `mcf.metric_self_verification_fixture(fixture_uid)` |
| `metric_contract_uid` | `uuid` | NOT NULL | — | FK to `mcf.metric_contract(metric_contract_uid)`; denormalized for query efficiency |
| `metric_contract_version_uid` | `uuid` | NOT NULL | — | FK to `mcf.metric_contract_version(metric_contract_version_uid)`; denormalized |
| `verdict_code` | `text` | NOT NULL | — | CHECK IN (`'pass'`, `'fail'`, `'structural_reject'`) |
| `verdict_payload_json` | `jsonb` | NOT NULL | — | Per-verdict diff trace / defects / reject reason; shape per §9 |
| `bound_package_signature_hash_at_run` | `text` | NOT NULL | — | Snapshot of `mcf.metric_contract.package_signature_hash` at verifier run time; sha256 format CHECK |
| `fixture_bound_package_signature_hash` | `text` | NOT NULL | — | Snapshot of `mcf.metric_self_verification_fixture.bound_package_signature_hash` at run time (audit); sha256 format CHECK |
| `stale_fixture_flag` | `boolean` | NOT NULL | — | true when `fixture_bound ≠ at_run`; verdict_code = `structural_reject` with reason `stale_fixture` |
| `verifier_algorithm_version` | `text` | NOT NULL | — | `mcf-verifier-v1` per D-M10-4; CHECK matches `^mcf-[a-z-]+-v[0-9]+$` (M2/M9 convention) |
| `executor_identity_text` | `text` | NOT NULL | — | Service identity (hostname + service version) for forensic audit per D-M10-2 |
| `executed_at` | `timestamptz` | NOT NULL | `now()` | Execution timestamp |
| `execution_duration_ms` | `integer` | NOT NULL | — | Wall-clock ms; CHECK >= 0; useful for performance analysis per D-M10-2 |

**Total: 13 columns** (under D162 20-column max).

### 5.2 No archived_at / no soft-delete

Per D-M10-9 substrate append-only trigger + §17.1 "append-only per Invariant V":
- No `archived_at` column — append-only trigger blocks UPDATE
- No supersession via in-place mutation — new verifier runs emit new rows; old rows remain addressable
- Algorithm-version bump (`mcf-verifier-v2` in future) emits new rows under new version; v1 rows remain addressable per Invariant V

### 5.3 Constraint inventory (10 constraints)

| Constraint | Type | Definition |
|---|---|---|
| `msvr_pkey` | PRIMARY KEY | `(verification_result_uid)` |
| `fk_msvr_fixture` | FOREIGN KEY | `fixture_uid` → `mcf.metric_self_verification_fixture(fixture_uid)` ON DELETE RESTRICT |
| `fk_msvr_mc` | FOREIGN KEY | `metric_contract_uid` → `mcf.metric_contract(metric_contract_uid)` ON DELETE RESTRICT |
| `fk_msvr_mcv` | FOREIGN KEY | `metric_contract_version_uid` → `mcf.metric_contract_version(metric_contract_version_uid)` ON DELETE RESTRICT |
| `msvr_verdict_code_chk` | CHECK | `verdict_code IN ('pass','fail','structural_reject')` |
| `msvr_bound_pkg_hash_at_run_fmt_chk` | CHECK | `bound_package_signature_hash_at_run ~ '^sha256:[0-9a-f]{64}$'` |
| `msvr_fixture_bound_pkg_hash_fmt_chk` | CHECK | `fixture_bound_package_signature_hash ~ '^sha256:[0-9a-f]{64}$'` |
| `msvr_algorithm_version_chk` | CHECK | `verifier_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'` |
| `msvr_duration_non_negative_chk` | CHECK | `execution_duration_ms >= 0` |
| `uq_msvr_fixture_version_pkg_hash` | UNIQUE | `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` — substrate-side idempotency: at most one verdict per (fixture, verifier-version, package-hash-at-run) |

**Total: 10 constraints** = 1 PK + 3 FK + 5 CHECK + 1 UNIQUE.

### 5.4 Index inventory (4 indexes)

| Index | Definition | Purpose |
|---|---|---|
| `idx_mcf_msvr_fixture` | `(fixture_uid)` | Lookup all results for a fixture (PE-MC-10 + audit query) |
| `idx_mcf_msvr_mcv` | `(metric_contract_version_uid)` | Lookup all results for an MCV (operator console) |
| `idx_mcf_msvr_verdict` | `(verdict_code)` | Stats / dashboard queries (count by verdict) |
| `idx_mcf_msvr_executed_at` | `(executed_at)` | Chronological scan / retention queries |

(`uq_msvr_fixture_version_pkg_hash` UNIQUE constraint already provides the `(fixture, version, hash)` lookup index — no separate index needed.)

### 5.5 DDL

```sql
CREATE TABLE mcf.metric_self_verification_result (
  verification_result_uid                 uuid NOT NULL PRIMARY KEY DEFAULT gen_random_uuid(),
  fixture_uid                             uuid NOT NULL,
  metric_contract_uid                     uuid NOT NULL,
  metric_contract_version_uid             uuid NOT NULL,
  verdict_code                            text NOT NULL,
  verdict_payload_json                    jsonb NOT NULL,
  bound_package_signature_hash_at_run     text NOT NULL,
  fixture_bound_package_signature_hash    text NOT NULL,
  stale_fixture_flag                      boolean NOT NULL,
  verifier_algorithm_version              text NOT NULL,
  executor_identity_text                  text NOT NULL,
  executed_at                             timestamptz NOT NULL DEFAULT now(),
  execution_duration_ms                   integer NOT NULL,

  CONSTRAINT fk_msvr_fixture
    FOREIGN KEY (fixture_uid)
    REFERENCES mcf.metric_self_verification_fixture(fixture_uid)
    ON DELETE RESTRICT,

  CONSTRAINT fk_msvr_mc
    FOREIGN KEY (metric_contract_uid)
    REFERENCES mcf.metric_contract(metric_contract_uid)
    ON DELETE RESTRICT,

  CONSTRAINT fk_msvr_mcv
    FOREIGN KEY (metric_contract_version_uid)
    REFERENCES mcf.metric_contract_version(metric_contract_version_uid)
    ON DELETE RESTRICT,

  CONSTRAINT msvr_verdict_code_chk
    CHECK (verdict_code IN ('pass','fail','structural_reject')),

  CONSTRAINT msvr_bound_pkg_hash_at_run_fmt_chk
    CHECK (bound_package_signature_hash_at_run ~ '^sha256:[0-9a-f]{64}$'),

  CONSTRAINT msvr_fixture_bound_pkg_hash_fmt_chk
    CHECK (fixture_bound_package_signature_hash ~ '^sha256:[0-9a-f]{64}$'),

  CONSTRAINT msvr_algorithm_version_chk
    CHECK (verifier_algorithm_version ~ '^mcf-[a-z-]+-v[0-9]+$'),

  CONSTRAINT msvr_duration_non_negative_chk
    CHECK (execution_duration_ms >= 0),

  CONSTRAINT uq_msvr_fixture_version_pkg_hash
    UNIQUE (fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)
);

CREATE INDEX idx_mcf_msvr_fixture     ON mcf.metric_self_verification_result (fixture_uid);
CREATE INDEX idx_mcf_msvr_mcv         ON mcf.metric_self_verification_result (metric_contract_version_uid);
CREATE INDEX idx_mcf_msvr_verdict     ON mcf.metric_self_verification_result (verdict_code);
CREATE INDEX idx_mcf_msvr_executed_at ON mcf.metric_self_verification_result (executed_at);
```

(Append-only trigger DDL in §11; FK activation + M4 comment update in §12; COMMENT ON TABLE in §15 sequence.)

---

## 6. Verifier service design

### 6.1 Class shape

```typescript
// bc-core/src/registry/mcf/metric-self-verification.service.ts
export class MetricSelfVerificationService {
  constructor(
    private readonly structuralCheckService: FixtureStructuralCheckService,         // M9 reuse
    private readonly packageSignatureService: PackageSignatureService,              // M9 reuse + M7/M8
    private readonly formulaCanonicalizationService: FormulaCanonicalizationService, // M7/M8 reuse
    private readonly formulaExecutionEngine: FormulaExecutionEngine,                // NEW M10
    private readonly resolverFixtureConfigInterpreter: ResolverFixtureConfigInterpreter, // NEW M10
    private readonly outputComparator: OutputComparator,                            // NEW M10
  ) {}

  async verifyFixture(
    fixtureUid: string,
    deps: { tx: Tx },
  ): Promise<{
    verdict_code: 'pass' | 'fail' | 'structural_reject';
    verification_result_uid: string;
  }> {
    // §12.6 6-step pipeline:
    // 1. Load fixture body + bound hash
    // 2. Re-hash via M9 helper; cross-check stable binding
    // 3. Load MCV context + current package_signature_hash; STALE CHECK
    // 4. Re-run C-FX-1..C-FX-11 via M9 engine; STRUCTURAL CHECK
    // 5. Execute formula AST via FormulaExecutionEngine; APPLY resolver config
    // 6. Compare actual vs Section B via OutputComparator; EMIT result row
  }
}
```

### 6.2 §12.6 6-step pipeline detail

| Step | Action | Defect-emit condition |
|---|---|---|
| 1 | Load fixture row (Section A/B/C + `bound_package_signature_hash`) by `fixture_uid` | Fixture missing → throw `MissingFixtureError` (not a result row — caller bug) |
| 2 | Re-compute `computeSelfVerificationFixtureHash(body)`; assert equals stored `self_verification_fixture_hash` | Mismatch → throw `FixtureHashDriftError` (substrate corruption — impossible under append-only fixture immutability) |
| 3 | Load MCV context via `loadFixtureContext` (M9 helper); compute current `package_signature_hash` via M7/M8; compare to fixture's `bound_package_signature_hash` | Mismatch → emit `structural_reject` with reason `stale_fixture`; `stale_fixture_flag=true`; verdict_payload includes both hashes; **return early** |
| 4 | Run `structuralCheckService.runStructuralChecks(context, body)` | Any defect → emit `structural_reject` with reason `c_fx_failure`; verdict_payload includes M9 `FixtureDefect[]`; **return early** |
| 5 | Execute formula AST via `FormulaExecutionEngine.execute(ast, sectionA, sectionC, resolverConfig)` | Execution error → throw `ExecutionError` (formula AST should have been validated by M7/M8 + C-FX; reaching this branch indicates a deeper bug) |
| 6 | `outputComparator.compare(actualOutput, sectionB.output)` → diff trace | If match: emit `pass`; if mismatch: emit `fail` with diff_trace in verdict_payload |

### 6.3 Result row INSERT (substrate-side idempotency)

The UNIQUE constraint `uq_msvr_fixture_version_pkg_hash` ensures at most one row per `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)`. Verifier INSERT semantics:

- If no existing row → INSERT new row; return its UID
- If existing row → re-INSERT raises unique_violation; verifier catches + returns the existing row's UID (idempotent)

This makes `verifyFixture` safe to retry without producing duplicate results. The existing row's verdict (from the original execution) is authoritative; re-running the verifier produces the same verdict deterministically (per algorithm-version contract per D-M10-4).

### 6.4 Service registration (NestJS-injectable per D-M10-5)

Module wiring follows the existing MCF service pattern (direct import; no barrel). The 3 new services (`MetricSelfVerificationService`, `FormulaExecutionEngine`, `ResolverFixtureConfigInterpreter`, `OutputComparator` — actually 4 new) live alongside the existing M5/M7/M8/M9 services in `src/registry/mcf/`. Whether they're NestJS providers (declared in an MCF module) or pure ES classes is decided by the impl PR per existing convention; the operator scope item 5 says "Add services to the local MCF module/export pattern if one exists" — for MCF, none exists; direct-import convention applies.

---

## 7. Verdict semantics: pass / fail / structural_reject

| Verdict | When | Trigger | Diff trace? |
|---|---|---|---|
| `pass` | §12.6 step 6 — actual output matches Section B expected within declared tolerance + null-match policy | OutputComparator returns no mismatch | `verdict_payload_json = { "_runtime": {...} }` (runtime evidence only) |
| `fail` | §12.6 step 6 — actual output deviates from Section B beyond tolerance | OutputComparator returns mismatch | `verdict_payload_json = { "diff": {...} OR "diff_rows": [...], "tolerance_used", "null_match_policy_used", "_runtime" }` |
| `structural_reject` | §12.6 step 3 (stale) OR step 4 (C-FX failure) — fixture cannot be executed against current package | Stale-fixture or any C-FX-1..C-FX-11 defect | `verdict_payload_json = { "reason": "stale_fixture" \| "c_fx_failure", ... }` |

### 7.1 Pass verdict

The fixture's Section B expectation is satisfied. PE-MC-10 can cite this row to mark the metric eligible.

### 7.2 Fail verdict

The formula executed cleanly against Section A inputs but produced output that differs from Section B. The metric is not eligible (PE-MC-10 routes to OPERATOR_REVIEW per MCF §13). Diff trace gives the operator per-row visibility into the discrepancy.

### 7.3 Structural_reject verdict

The fixture cannot be executed at all — either because it's stale (package signature has moved on) or because C-FX detected a structural defect (Section A/B/C is internally inconsistent with the package). PE-MC-10 routes to OPERATOR_REVIEW; operator either authors a new fixture (stale case) or fixes the structural defect (C-FX case).

---

## 8. Stale-fixture behavior

### 8.1 Detection

Per §12.6 step 3 + §12.7:

```text
fixture = SELECT * FROM mcf.metric_self_verification_fixture WHERE fixture_uid = $1
mc = SELECT * FROM mcf.metric_contract WHERE metric_contract_uid = fixture.metric_contract_uid
mcv_current_pkg_hash = packageSignatureService.computePackageSignatureHash(mcv_uid, contributingHashes, deps)

IF fixture.bound_package_signature_hash <> mcv_current_pkg_hash THEN
  -- STALE — emit structural_reject and return
  INSERT INTO mcf.metric_self_verification_result (
    fixture_uid,
    metric_contract_uid,
    metric_contract_version_uid,
    verdict_code,
    verdict_payload_json,
    bound_package_signature_hash_at_run,      -- = mcv_current_pkg_hash
    fixture_bound_package_signature_hash,     -- = fixture.bound_package_signature_hash
    stale_fixture_flag,                        -- = TRUE
    verifier_algorithm_version,
    executor_identity_text,
    execution_duration_ms
  ) VALUES (..., 'structural_reject', '{"reason":"stale_fixture", ...}', ..., TRUE, ...)
END IF
```

### 8.2 Both hashes stored for audit

Per D-M10-6: the substrate carries BOTH `fixture_bound_package_signature_hash` (from the fixture row at run time) AND `bound_package_signature_hash_at_run` (the MC's current hash at run time). The `stale_fixture_flag` is a denormalized convenience equal to `fixture_bound != at_run`.

This gives post-hoc audit the ability to reconstruct exactly why a verdict was emitted, even if the fixture or MC has moved on since.

### 8.3 Operator response

Per M9 D-M9-5 supersession discipline: operator authors a NEW fixture (new `fixture_uid`) against the current `package_signature_hash`. Old fixture remains addressable; old verification results remain addressable per Invariant V. New fixture gets its own verification results. PE-MC-10 picks up the new `pass` verdict once it lands.

**No substrate-side restart.** No re-evaluate-existing-fixture path. New fixture = new path forward.

---

## 9. Diff trace JSONB contract

### 9.1 Per-verdict JSONB shape

```jsonc
// PASS
{
  "_runtime": {
    "ast_node_count_walked": 5,
    "section_a_row_count": 10,
    "section_b_cardinality": "one",
    "evaluation_duration_us": 1234
  }
}

// FAIL (single-value output)
{
  "diff": {
    "expected": { "value": 100, "is_null": false },
    "actual":   { "value": 99,  "is_null": false },
    "absolute_difference": 1,
    "relative_difference": 0.01,
    "exceeds_tolerance": true
  },
  "tolerance_used":     { "mode": "relative_epsilon", "value": 0.0001 },
  "null_match_policy_used": "strict",
  "_runtime": { ... }
}

// FAIL (rowset output)
{
  "diff_rows": [
    {
      "grain_keys": { "entity_uid": "e1" },
      "expected":   { "value": 50, "is_null": false },
      "actual":     { "value": 52, "is_null": false },
      "match": false,
      "delta": 2
    },
    {
      "grain_keys": { "entity_uid": "e2" },
      "expected":   { "value": 30, "is_null": false },
      "actual":     { "value": 30, "is_null": false },
      "match": true,
      "delta": 0
    }
  ],
  "summary": {
    "rows_total": 2,
    "rows_matched": 1,
    "rows_diffed": 1,
    "rows_only_in_expected": 0,
    "rows_only_in_actual": 0
  },
  "tolerance_used":     { ... },
  "null_match_policy_used": "strict",
  "_runtime": { ... }
}

// STRUCTURAL_REJECT — stale_fixture
{
  "reason": "stale_fixture",
  "fixture_bound_hash":   "sha256:abc...",
  "current_package_hash": "sha256:def...",
  "_runtime": { ... }
}

// STRUCTURAL_REJECT — c_fx_failure
{
  "reason": "c_fx_failure",
  "defects": [
    {
      "defect_code": "FIXTURE_DEFECT_GRAIN_KEYS_MISSING",
      "check_code": "C-FX-5",
      "message": "...",
      "payload": { ... }
    }
  ],
  "_runtime": { ... }
}
```

### 9.2 Substrate enforcement

`verdict_payload_json jsonb NOT NULL` — no JSON-schema CHECK at substrate level. Per-verdict JSON-schema validation deferred to the verifier service (matches M5 `consensus_payload_json` rationale + M9 `section_*_json` pattern). Schemas live in code (TS types co-located with the verifier service).

### 9.3 Size pressure mitigation

Section A is bounded by the panel UI; pathological diffs (e.g. 10k diff_rows) are unlikely. If size pressure emerges, the diff_rows array can be truncated with a `truncated: true` flag + `truncated_at_row: N` and the operator can re-query a specific grain via the M16 console (future). Child-row table escalation per D-M10-3 deferred.

---

## 10. Runtime evidence payload

The `_runtime` sub-key inside `verdict_payload_json` carries non-verdict evidence:

| Field | Purpose |
|---|---|
| `ast_node_count_walked` | Confirms the execution engine walked the full AST (sanity check) |
| `section_a_row_count` | Echoes input scale |
| `section_b_cardinality` | Echoes expected output shape |
| `evaluation_duration_us` | Microsecond-precision timing (complements column-level `execution_duration_ms`) |
| `engine_version_internal` | Internal engine sub-version (e.g. specific `FormulaExecutionEngine` git commit) for forensic recovery if `mcf-verifier-v1` bundle is later split into sub-bundles |

Runtime evidence is informational; it does not affect the verdict.

---

## 11. Append-only trigger design

### 11.1 Per D-M10-9 — substrate enforcement (defense in depth)

Per operator-locked D-M10-9, the result substrate uses a substrate-side trigger (NOT service-side discipline only) to enforce append-only per Invariant V. This matches the M5 transcript pattern + M9 fixture pattern.

### 11.2 Trigger function

```sql
CREATE OR REPLACE FUNCTION mcf.fn_msvr_immutability_check()
RETURNS TRIGGER AS $$
BEGIN
  -- Per DBCP M10 §11 + D-M10-9 + MCF §17.1 + Invariant V:
  -- self-verification result rows are immutable post-INSERT. The append-only
  -- ledger discipline is evidence-grade — UPDATE/DELETE attempts indicate
  -- either a service bug (verifier shouldn't ever rewrite a result) or
  -- malicious tampering with historical verdicts. Both are rejected
  -- unconditionally.
  --
  -- Mirrors mcf.fn_mapt_immutability_check (M5 transcript pattern) +
  -- mcf.fn_msvf_immutability_check (M9 fixture pattern). Same strict
  -- M3/M5/M9-style discipline.
  --
  -- If a result row is genuinely wrong (e.g. produced by a buggy verifier
  -- version), the correction path is: bump the algorithm version to
  -- mcf-verifier-v2 and emit new rows under v2; v1 rows remain addressable
  -- as historical truth per Invariant V.
  IF TG_OP = 'UPDATE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_result verification_result_uid=% is immutable; UPDATE rejected (per DBCP M10 §11 + Invariant V)', OLD.verification_result_uid
      USING ERRCODE = 'check_violation';
  END IF;
  IF TG_OP = 'DELETE' THEN
    RAISE EXCEPTION 'mcf.metric_self_verification_result verification_result_uid=% is immutable; DELETE rejected (per DBCP M10 §11 + Invariant V)', OLD.verification_result_uid
      USING ERRCODE = 'check_violation';
  END IF;
  RETURN NULL;
END;
$$ LANGUAGE plpgsql;
```

### 11.3 Trigger attachment

```sql
CREATE TRIGGER trg_msvr_immutability
BEFORE UPDATE OR DELETE ON mcf.metric_self_verification_result
FOR EACH ROW EXECUTE FUNCTION mcf.fn_msvr_immutability_check();
```

### 11.4 Behavioral verification

Post-apply verifier (§18) exercises UPDATE and DELETE attempts; each rejected with the expected error message. SAVEPOINT-protected per M-M5-1 recipe.

---

## 12. FK activation: `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid`

### 12.1 Per D-M10-7 — inline in M10 DDL

```sql
ALTER TABLE mcf.metric_publication_eligibility_result
  ADD CONSTRAINT fk_mper_verification_result
  FOREIGN KEY (satisfying_verification_result_uid)
  REFERENCES mcf.metric_self_verification_result(verification_result_uid)
  ON DELETE RESTRICT;
```

### 12.2 Safety of activation on empty tables

`mcf.metric_publication_eligibility_result` is empty (M4 substrate, dormant). FK activation on empty source + empty target is metadata-only — no existing row needs validation. Constraint takes effect at next INSERT (none expected in M10 scope).

### 12.3 Post-M10 FK landscape

| Source table | Column | FK | Target |
|---|---|---|---|
| `mcf.metric_publication_eligibility_result` | `satisfying_verification_result_uid` | `fk_mper_verification_result` (NEW M10) | `mcf.metric_self_verification_result(verification_result_uid)` |

All M4-deferred FKs are now activated (M5 activated 3 panel_run FKs; M10 activates this verification_result FK).

---

## 13. M4 doc-bug correction (per D-M10-8)

### 13.1 Pre-correction comment

```sql
-- 06-mcf-lifecycle-certification.sql:179 (live state):
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.satisfying_verification_result_uid IS
  'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK deferred until M9 ships (D-16). Nullable + FK-less until then; service-layer validation when the table exists.';
```

### 13.2 Post-correction comment (M10 DDL)

```sql
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.satisfying_verification_result_uid IS
  'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK fk_mper_verification_result activated by M10 (per DBCP M10 §12 + DBCP M10 620e11d). Per MCF §13 PE-MC-10 + §17.1 result substrate.';
```

### 13.3 Atomicity

The COMMENT UPDATE ships in the same `BEGIN/COMMIT` transaction as the FK activation (per §15.2 step ordering). Either both land or both roll back.

---

## 14. Algorithm-version discipline

### 14.1 `mcf-verifier-v1` bundle (per D-M10-4)

Separate bundle from `mcf-hash-v1`. The verifier is a different algorithm class:
- `mcf-hash-v1`: covers JCS canonicalization + sha256 chain (M7/M8/M9 hash composition)
- `mcf-verifier-v1`: covers per-AST-kind execution semantics + tolerance comparator + null-match policy + diff-trace shape

A future bug fix to JCS canonicalization (e.g. `mcf-hash-v2`) does NOT necessarily require a verifier bump (the verifier reads hashes; if the hashes change shape, fixtures are re-hashed under v2; verifier semantics unchanged). Conversely, a future change to aggregate semantics (e.g. `mcf-verifier-v2`) does NOT require a hash bump.

Both bundles share the same regex `^mcf-[a-z-]+-v[0-9]+$` enforced at substrate.

### 14.2 v1 coverage

`mcf-verifier-v1` covers:

| Surface | Coverage |
|---|---|
| AST node kinds | All 9 `NODE_KINDS`: variable_ref / literal / aggregate / arithmetic / comparison / case / window / time_anchor_resolution / bucket_assign |
| Aggregate operators | `sum, avg, count, count_distinct, min, max, median, percentile` |
| Arithmetic operators | `plus, minus, multiply, divide, mod` |
| Comparison operators | `lt, lte, eq, gte, gt, neq` |
| Window operators | `lag, lead, moving_avg` |
| Tolerance modes | `absolute`, `relative_epsilon`, `exact` |
| Null-match policies | `strict`, `permissive_on_zero_denom` (extensible enum) |
| Resolver-fixture-config classes | `fiscal_calendar`, `bucket_specs`, `derived_grain_params` (per MCF §9.2) |

### 14.3 Forward compatibility

UNIQUE on `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` admits **one row per (fixture, version, package-hash) triple**. A future `mcf-verifier-v2` deployment can re-verify the same fixture and emit a NEW row under v2 without conflicting with the v1 row. PE-MC-10 (M13) decides which version's verdict to honor (typically the most recent compatible version; M13's design will lock this).

---

## 15. DDL apply sequence and rollback story

### 15.1 Forward DDL file

`bc-core/docker/redesign/10-mcf-self-verification-result-substrate.sql` (single file; whole-file `BEGIN/COMMIT` per M3/M5/M7-M8/M9 atomicity pattern).

### 15.2 Apply sequence (single transaction)

```sql
BEGIN;

-- ─── Step 1: CREATE mcf.metric_self_verification_result ─────────────────────
-- Per DBCP M10 §5. 13 columns; 10 constraints (1 PK + 3 FK + 5 CHECK + 1 UNIQUE).
CREATE TABLE mcf.metric_self_verification_result ( ... );

-- ─── Step 2: 4 indexes per query patterns ───────────────────────────────────
CREATE INDEX idx_mcf_msvr_fixture     ON mcf.metric_self_verification_result (fixture_uid);
CREATE INDEX idx_mcf_msvr_mcv         ON mcf.metric_self_verification_result (metric_contract_version_uid);
CREATE INDEX idx_mcf_msvr_verdict     ON mcf.metric_self_verification_result (verdict_code);
CREATE INDEX idx_mcf_msvr_executed_at ON mcf.metric_self_verification_result (executed_at);

-- ─── Step 3: Append-only trigger function + attachment ──────────────────────
-- Per DBCP M10 §11 + D-M10-9 — M3/M5/M9-style unconditional UPDATE/DELETE
-- reject post-INSERT; evidence-grade defense-in-depth.
CREATE OR REPLACE FUNCTION mcf.fn_msvr_immutability_check() ... ;
CREATE TRIGGER trg_msvr_immutability
BEFORE UPDATE OR DELETE ON mcf.metric_self_verification_result
FOR EACH ROW EXECUTE FUNCTION mcf.fn_msvr_immutability_check();

-- ─── Step 4: FK activation per D-M10-7 ──────────────────────────────────────
-- Activates the M4-deferred fk_mper_verification_result. Safe on empty
-- target (mcf.metric_publication_eligibility_result has 0 rows; new table
-- has 0 rows). Metadata-only; no existing row needs validation.
ALTER TABLE mcf.metric_publication_eligibility_result
  ADD CONSTRAINT fk_mper_verification_result
  FOREIGN KEY (satisfying_verification_result_uid)
  REFERENCES mcf.metric_self_verification_result(verification_result_uid)
  ON DELETE RESTRICT;

-- ─── Step 5: M4 doc-bug correction per D-M10-8 ──────────────────────────────
-- Replaces the misleading "FK deferred until M9 ships" with the accurate
-- "FK fk_mper_verification_result activated by M10" wording. Same atomic
-- transaction as the FK activation above.
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.satisfying_verification_result_uid IS
  'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK fk_mper_verification_result activated by M10 (per DBCP M10 §12). Per MCF §13 PE-MC-10 + §17.1 result substrate.';

-- ─── Step 6: COMMENT ON TABLE on new table ──────────────────────────────────
COMMENT ON TABLE mcf.metric_self_verification_result IS
  '... (full comment per §5.5)';

COMMIT;
```

### 15.3 Atomicity rationale

All 6 steps commit together or roll back together. Critical orderings:
- CREATE TABLE before CREATE INDEX (target must exist)
- CREATE TABLE before CREATE TRIGGER (target must exist)
- CREATE TABLE before ALTER TABLE ADD CONSTRAINT FK (FK target must exist)
- ALTER TABLE before COMMENT ON COLUMN (touches the same column; clean ordering)

### 15.4 Rollback DDL

`bc-core/docker/redesign/10-mcf-self-verification-result-substrate-rollback.sql`.

**Precondition guard** (refuses if substrate has been used):

```sql
DO $$
DECLARE
  result_count integer;
BEGIN
  SELECT COUNT(*) INTO result_count FROM mcf.metric_self_verification_result;
  IF result_count > 0 THEN
    RAISE EXCEPTION 'M10 rollback REFUSED: mcf.metric_self_verification_result has % rows. Drop rows first OR accept data loss with manual override.',
      result_count
      USING ERRCODE = 'check_violation';
  END IF;
END $$;
```

**Reversal sequence:**

```sql
BEGIN;

-- Step 1: Revert M4 comment to pre-M10 wording (defensive — restores known prior shape).
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.satisfying_verification_result_uid IS
  'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK deferred until M9 ships (D-16). Nullable + FK-less until then; service-layer validation when the table exists.';

-- Step 2: Drop FK activation.
ALTER TABLE mcf.metric_publication_eligibility_result
  DROP CONSTRAINT fk_mper_verification_result;

-- Step 3: Drop trigger + function.
DROP TRIGGER IF EXISTS trg_msvr_immutability ON mcf.metric_self_verification_result;
DROP FUNCTION IF EXISTS mcf.fn_msvr_immutability_check();

-- Step 4: Drop the table (indexes + constraints cascade).
DROP TABLE mcf.metric_self_verification_result;

COMMIT;
```

---

## 16. Drizzle impact

### 16.1 New Drizzle schema file

| File | Purpose |
|---|---|
| `bc-core/src/database/schema/mcf/metric-self-verification-result.ts` | Mirrors §5.5 DDL byte-equivalently |
| `bc-core/src/database/schema/mcf/index.ts` | Export `metricSelfVerificationResult` |

### 16.2 Drizzle FK foreignColumns — all intra-mcf

All 3 FKs target mcf tables; declared via `foreignKey()`:
- `fk_msvr_fixture` → `mcf.metric_self_verification_fixture(fixture_uid)` — import `metricSelfVerificationFixture`
- `fk_msvr_mc` → `mcf.metric_contract(metric_contract_uid)` — import `metricContract`
- `fk_msvr_mcv` → `mcf.metric_contract_version(metric_contract_version_uid)` — import `metricContractVersion`

The 4th FK (`fk_mper_verification_result`) is activated via DDL ALTER on an EXISTING table (`mcf.metric_publication_eligibility_result`); Drizzle schema for that table can optionally add the foreignKey declaration in its own schema file. Per M5 precedent (where FK activations on existing tables were added to the Drizzle files), the M10 impl PR will add this foreignKey to `metric-publication-eligibility-result.ts` to keep Drizzle in sync.

### 16.3 Byte-matching DDL discipline

Mirrors M5 §15.4 + M9 §13.4 — Drizzle template strings must byte-match DDL:
- Simple column DEFAULTs (`now()`, `gen_random_uuid()`) byte-match
- Simple CHECK predicates byte-match (all 5 M10 CHECKs are single-line)
- No multi-line CHECKs in M10 → no semantic-equivalence carve-out needed

### 16.4 No Drizzle changes for trigger / FK activation comment update

- Trigger function lives in DDL only (Drizzle has no first-class trigger support)
- M4 comment update is a `COMMENT ON COLUMN` UPDATE — not part of Drizzle schema
- FK activation on existing table is a Drizzle `foreignKey()` addition (per §16.2)

---

## 17. Dry-run verifier plan

### 17.1 Script

`bc-core/scripts/mcf-m10-dry-run.mjs` (mirrors M3/M4/M5/M7-M8/M9 dry-run pattern)

### 17.2 Checks (8 total)

| # | Check | HARD-GATE? |
|---|---|---|
| #1 | M9 substrate prereq — all 15 `mcf.*` tables present AND `mcf.metric_self_verification_fixture` present (M9 applied) | YES |
| #2 | `mcf.metric_self_verification_result` does NOT yet exist (clean slate) | YES |
| #3 | `mcf.fn_msvr_immutability_check` + `trg_msvr_immutability` do NOT yet exist (clean slate) | YES |
| #4 | `fk_mper_verification_result` does NOT yet exist (clean slate — confirms M10 hasn't half-applied) | YES |
| #5 | All 15 mcf.* tables empty (no real rows to orphan) | (no, advisory) |
| #6 | FK targets present: `mcf.metric_self_verification_fixture` + `mcf.metric_contract` + `mcf.metric_contract_version` + `mcf.metric_publication_eligibility_result` (regression check on M2/M4/M9) | (no, advisory) |
| #7 | DDL parse counts: 1 CREATE TABLE + 4 CREATE INDEX + 1 CREATE OR REPLACE FUNCTION + 1 CREATE TRIGGER + 1 ALTER TABLE ADD CONSTRAINT + 1 COMMENT ON COLUMN + 1 COMMENT ON TABLE + BEGIN/COMMIT | (no, parse failure = abort) |
| #8 | DDL sha256 (forward + rollback) captured | always pass; recording artifact |

### 17.3 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All checks PASS |
| 1 | DATABASE_URL not set |
| 2 | DDL file not found |
| 3-10 | Per-check failure |
| 20 | Hard-gate refused (M9 not applied OR partial M10 apply detected) |
| 21 | Unexpected error |

---

## 18. Post-apply verifier plan

### 18.1 Script

`bc-core/scripts/mcf-m10-post-apply-verification.mjs`

### 18.2 Checks (16 total — SAVEPOINT-protected from start per M-M5-1)

**Structural (1–6):**

| # | Check |
|---|---|
| #1 | `mcf.metric_self_verification_result` present with 13 cols + 5 CHECKs byte-matched via `pg_get_constraintdef()` (1 verdict-enum + 2 sha256-format + 1 algo-version regex + 1 non-negative-duration) — per M9 M1-patch byte-match discipline |
| #2 | 3 intra-mcf FKs active (`fk_msvr_fixture` + `fk_msvr_mc` + `fk_msvr_mcv`) all ON DELETE RESTRICT |
| #3 | UNIQUE `uq_msvr_fixture_version_pkg_hash` on `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` present |
| #4 | 4 non-PK/non-UNIQUE indexes present (`idx_mcf_msvr_fixture` + `idx_mcf_msvr_mcv` + `idx_mcf_msvr_verdict` + `idx_mcf_msvr_executed_at`) |
| #5 | Trigger function `mcf.fn_msvr_immutability_check` + `trg_msvr_immutability` BEFORE UPDATE OR DELETE attached |
| #6 | `fk_mper_verification_result` activated on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` → `mcf.metric_self_verification_result(verification_result_uid)` ON DELETE RESTRICT |

**Behavioral (7–15) — SAVEPOINT-protected synthetic-row exercises:**

| # | Check |
|---|---|
| #7 | Synthetic prereq chain INSERT succeeds: `contract.panel_output_record` + `mcf.metric_authoring_panel_run` + `mcf.metric_contract` + `mcf.metric_contract_version` + `mcf.metric_self_verification_fixture` (5-row prereq for the result row); rolls back |
| #8 | Valid result row INSERT succeeds (all 5 hashes/regex CHECKs + duration CHECK pass); captures inserted UID |
| #9 | (SAVEPOINT) UPDATE result row → REJECTED by `trg_msvr_immutability` |
| #10 | (SAVEPOINT) DELETE result row → REJECTED by `trg_msvr_immutability` |
| #11 | (SAVEPOINT) Duplicate (fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run) → REJECTED by `uq_msvr_fixture_version_pkg_hash` |
| #12 | (SAVEPOINT) Bogus `fixture_uid` (3-FK widened) → REJECTED by `fk_msvr_fixture`; bogus `metric_contract_uid` → `fk_msvr_mc`; bogus `metric_contract_version_uid` → `fk_msvr_mcv`. All 3 FK rejections in one widened check per L2-pattern from M9 |
| #13 | (SAVEPOINT) Invalid `verdict_code` (e.g. `'unknown'`) → REJECTED by `msvr_verdict_code_chk` |
| #14 | (SAVEPOINT) Bad hash format (e.g. `'not-sha256'`) → REJECTED by `msvr_bound_pkg_hash_at_run_fmt_chk` |
| #15 | (SAVEPOINT) Negative `execution_duration_ms` (e.g. `-1`) → REJECTED by `msvr_duration_non_negative_chk` |

**Cleanup (16):**

| # | Check |
|---|---|
| #16 | All 16 mcf.* tables empty after verifier (10 pre-M5 + 4 M5 + 1 M9 + 1 new M10); BCF 24+1 untouched |

### 18.3 Exit codes

| Exit | Meaning |
|---|---|
| 0 | All 16 checks PASS |
| 1 | DATABASE_URL not set |
| 3-18 | Per-check failure |
| 19 | Unexpected error |

---

## 19. Unit/integration test plan

### 19.1 Per-AST-kind execution tests (golden-vector per D-M10-10)

**18 minimum tests** = 9 AST kinds × (1 positive + 1 negative):

| AST kind | Positive | Negative |
|---|---|---|
| `variable_ref` | Resolves to bound binding's value | Unbound role → throw |
| `literal` | Returns literal value | Non-finite number → throw |
| `aggregate` (sum) | Sums rowset values | Wrong rowset type → throw |
| `arithmetic` (divide) | Computes division | Divide by zero → emit NaN or null per null_match_policy |
| `comparison` (gt) | Returns boolean | Type-mismatched operands → throw |
| `case` | First-true branch wins | No branch + no else → throw |
| `window` (moving_avg) | Computes windowed avg | Window beyond rowset → null/throw |
| `time_anchor_resolution` | Resolves anchor to date | Anchor missing → throw |
| `bucket_assign` | Assigns row to bucket | Value outside boundaries → throw or assign to "other" |

Plus aggregate-operator coverage: 8 aggregate ops × at least 1 test = 8 tests. Total minimum: **26 execution tests**.

### 19.2 Tolerance comparator tests

- `absolute` mode: within tolerance pass; beyond fail
- `relative_epsilon` mode: same
- `exact` mode: pass on exact equality only

### 19.3 Null-match policy tests

- `strict`: null ≠ non-null
- `permissive_on_zero_denom`: 0/0 → null treated as expected

### 19.4 Diff-trace builder tests

- Single-value output: `diff` key
- Rowset output: `diff_rows[]` + `summary`
- Stale fixture: `reason: stale_fixture` + both hashes
- C-FX failure: `reason: c_fx_failure` + defects array

### 19.5 Integration tests

`metric-self-verification.service.integration.spec.ts`:
- End-to-end `verifyFixture(fixture_uid, deps)` against in-memory fake tx
- Stale-fixture rejection path
- C-FX failure rejection path
- Successful execution path with passing verdict
- Successful execution path with failing verdict (diff trace)
- Idempotency: re-calling `verifyFixture` for same (fixture, version, hash) returns existing result UID (unique_violation caught + handled)

### 19.6 Property-style cross-checks per D-M10-10

- Determinism: same fixture + same package hash + same verifier version → same verdict + same payload bytes (canonical JSON ordering)
- Algorithm-version invariance: verifying under `mcf-verifier-v1` always produces the same verdict for the same (fixture, package_hash) regardless of executor instance
- Result row idempotency: re-running the verifier in 2 separate txs both lookup-existing

### 19.7 Test file inventory

| File | Tests |
|---|---|
| `metric-self-verification.service.spec.ts` | Unit: §12.6 6-step orchestration (mocked engine + comparator) |
| `formula-execution.engine.spec.ts` | 26+ per-AST-kind tests (§19.1) |
| `resolver-fixture-config.interpreter.spec.ts` | Per-class resolver config interpretation |
| `output-comparator.spec.ts` | Tolerance + null-match policy tests (§19.2 + §19.3) |
| `metric-self-verification.service.integration.spec.ts` | Integration tests (§19.5) |

---

## 20. Risks and mitigations

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M10-1 | **Underbuilding the verifier** — ships handling ratio metrics but fails on windowed / computed-dimension / bucket-assign | Medium (per build plan §M10 primary risk) | All 9 AST kinds have golden-vector tests; 8 aggregate ops have explicit tests; reproducibility-test discipline |
| R-M10-2 | **Tolerance + null-match policy defaults under-specified** — fixtures depend on platform defaults when fixture omits per-fixture override | Medium | M10 v1 ships sensible defaults (relative_epsilon=1e-6 for numbers; absolute=1 minor unit for currency; strict null-match); §19.13 Q38 may strengthen later |
| R-M10-3 | **Diff trace JSONB size pressure** for very large rowset diffs | Low | Section A bounded by panel UI; truncation flag + child-row escalation available if needed |
| R-M10-4 | **Stale-fixture race** between fixture and MC reads | Very low | `mcf.metric_contract` is immutable post-cert per M3; race window doesn't exist; verifier reads both under same tx for snapshot consistency |
| R-M10-5 | **Algorithm-version forward compatibility** — `mcf-verifier-v2` may produce different verdicts | Medium | UNIQUE admits one row per (fixture, version, hash); v2 emits new rows; v1 rows preserved per Invariant V; M13 decides which version to honor |
| R-M10-6 | **Sync verifier blocks panel UX** under slow formulas | Low | v1 sync per D-M10-5; async amendment available post-M12 if needed |
| R-M10-7 | **Substrate trigger over-rejection** of legitimate UPDATE/DELETE | Very low | M5 transcript + M9 fixture both use the same unconditional pattern; correction path is bump algorithm version + emit new row (not mutate existing) |
| R-M10-8 | **FK activation regression** — pre-existing PE-result rows could orphan | Very low (no rows) | `mcf.metric_publication_eligibility_result` is empty; activation is metadata-only |
| R-M10-9 | **Execution engine determinism** — floating-point semantics across executor architectures | Low | Use IEEE 754 throughout; document determinism contract; property-style tests catch non-determinism |
| R-M10-10 | **Service registration / NestJS module wiring drift** — service not visible to M12 panel | Low | Direct-import convention; existing M9 services use same pattern; M12 panel impl PR wires explicitly |

### 20.1 Stop conditions

- §19.13 Q38 (tolerance + null-match defaults) lands before M10 DBCP → may reshape v1 defaults; low likelihood
- §19.13 Q40 (fixture retention) lands → may add archival columns; out of M10 scope
- M11 ingestion DBCP opens first → unlikely conflict

---

## 21. Operator approvals for implementation PR (O-M10-1..O-M10-11)

Before the M10 implementation PR opens, the operator approves these 11 items:

| # | Approval item |
|---|---|
| **O-M10-1** | Confirm D-M10-1 (M10-A append-only ledger + JSONB diff trace + sync verifier service) |
| **O-M10-2** | Confirm `mcf.metric_self_verification_result` 13-column shape + 10 constraints (1 PK + 3 intra-mcf FK + 5 CHECK + 1 UNIQUE) + 4 indexes |
| **O-M10-3** | Confirm verdict_code CHECK enum (`pass`, `fail`, `structural_reject`); JSONB diff trace contract per §9 |
| **O-M10-4** | Confirm verifier algorithm version `mcf-verifier-v1` (separate bundle from `mcf-hash-v1`) |
| **O-M10-5** | Confirm substrate append-only trigger `fn_msvr_immutability_check` + `trg_msvr_immutability` (M3/M5/M9-style unconditional reject post-INSERT) per D-M10-9 |
| **O-M10-6** | Confirm FK activation `fk_mper_verification_result` inline in M10 DDL (atomic with table CREATE) per D-M10-7 |
| **O-M10-7** | Confirm M4 doc-bug correction folded inline via `COMMENT ON COLUMN` UPDATE per D-M10-8 |
| **O-M10-8** | Confirm verifier service design (§6) — `MetricSelfVerificationService.verifyFixture(fixtureUid, deps)` reusing M9 `FixtureStructuralCheckService` + `PackageSignatureService.computeSelfVerificationFixtureHash`; no duplicate engine |
| **O-M10-9** | Confirm FormulaExecutionEngine coverage of all 9 NODE_KINDS + 8 aggregate ops + 5 arithmetic ops + 6 comparison ops + 3 window ops |
| **O-M10-10** | Confirm test plan per §19 — minimum 26 per-AST-kind execution tests + tolerance/null-match tests + integration tests + property-style cross-checks per D-M10-10 |
| **O-M10-11** | Approve next gate: M10 implementation PR (NO DB APPLY) — may split into M10-substrate + M10-engine PRs at impl-time discretion per D-M10-A1 |

---

## 22. Recommended next gate

### 22.1 Recommendation: open M10 implementation PR (NO DB APPLY)

The implementation PR ships (combined per D-M10-A1; split optional):

**Substrate:**
1. `bc-core/docker/redesign/10-mcf-self-verification-result-substrate.sql` (forward DDL per §15.2)
2. `bc-core/docker/redesign/10-mcf-self-verification-result-substrate-rollback.sql` (rollback per §15.4)
3. `bc-core/src/database/schema/mcf/metric-self-verification-result.ts` (Drizzle per §16.1)
4. `bc-core/src/database/schema/mcf/index.ts` (re-export)
5. `bc-core/src/database/schema/mcf/metric-publication-eligibility-result.ts` (add `fk_mper_verification_result` foreignKey)
6. `bc-core/scripts/mcf-m10-dry-run.mjs` (8 checks per §17.2)
7. `bc-core/scripts/mcf-m10-post-apply-verification.mjs` (16 checks per §18.2 — SAVEPOINT-protected from start)

**Verifier service + engine:**
8. `bc-core/src/registry/mcf/metric-self-verification.service.ts` (orchestrator per §6)
9. `bc-core/src/registry/mcf/metric-self-verification.service.spec.ts` (unit tests)
10. `bc-core/src/registry/mcf/metric-self-verification.service.integration.spec.ts` (integration tests per §19.5)
11. `bc-core/src/registry/mcf/formula-execution.engine.ts` (per-AST-kind handlers per §14.2)
12. `bc-core/src/registry/mcf/formula-execution.engine.spec.ts` (26+ per-AST-kind tests per §19.1)
13. `bc-core/src/registry/mcf/resolver-fixture-config.interpreter.ts` (Section C runtime)
14. `bc-core/src/registry/mcf/resolver-fixture-config.interpreter.spec.ts` (tests)
15. `bc-core/src/registry/mcf/output-comparator.ts` (tolerance + null-match)
16. `bc-core/src/registry/mcf/output-comparator.spec.ts` (tolerance + null-match tests per §19.2 + §19.3)

**Suggested PR title:** `feat(mcf): M10 Self-Verification Result Substrate + Verifier Engine (NO DB APPLY)`

### 22.2 Sequencing per established pattern

1. M10 DBCP → operator review → 11 approvals O-M10-1..O-M10-11 ← **THIS DBCP**
2. M10 implementation PR (NO DB APPLY) — may split per D-M10-A1
3. M10 small-DDL apply gate (separate operator-authorized session)
4. M10 evidence PR + bc-docs-v3 closeout

### 22.3 What unblocks after M10

- **M11** reservoir ingestion — independent; parallel-eligible after M9
- **M12** Metric Authoring Panel — gated on M5 + M7 + M9 + M10 + M11
- **M13** PE-MC evaluator — gated on M5 + M7 + M9 + M10
- **M14** publication path
- **M16** operator console fixture-run UI — gated on M10

After M10 merges, the substrate chain M2→M10 is complete; the substrate is fully ready for M11+M12 to begin populating it.

---

## 23. What stays closed

| | |
|---|---|
| M10 impl PR | not opened by this DBCP |
| M10 DDL apply | pending impl PR |
| M10 evidence PR | pending apply |
| **M11 reservoir ingestion** | CLOSED — separate gate (parallel-eligible) |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M10 + M11 |
| **M13 PE-MC evaluator** | CLOSED — gated on M10 |
| **M14+** | CLOSED |
| **Real MCF metric contracts** | CLOSED |
| **Real fixtures + verification results** | CLOSED |
| **BCF data changes** | CLOSED — 24 BCF panel + 1 rejection log untouched throughout |
| **Async-queue verifier infrastructure** | DEFERRED per D-M10-5 |
| **Per-diff-row child table** | DEFERRED per D-M10-3 |
| **Tolerance + null-match defaults catalog** | DEFERRED — §19.13 Q38 open |
| **Fixture retention policy** | DEFERRED — §19.13 Q40 open |
| **M9 fixture substrate amendments** | CLOSED |
| **MCF defect-code v2 taxonomy** | CLOSED |
| **MCF hash algorithm v2 bump** | CLOSED — `mcf-hash-v1` forever-locked |
| **MCF verifier algorithm v2 bump** | CLOSED — `mcf-verifier-v1` forever-locked unless ADR-governed change |
