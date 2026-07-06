---
uid: metric-context-framework-m10-self-verification-result-preflight
title: MCF M10 Self-Verification Result Substrate + Verifier Engine Preflight
description: Docs-only preflight framing the M10 Deterministic Verifier Service gate per build plan §M10. M10 ships the result-substrate side of the fixture/verifier pair (mcf.metric_self_verification_result append-only ledger per Invariant V + MCF §17.1) plus a deterministic verifier service that consumes M9 fixtures, executes packages against Section A inputs applying Section C resolver configs, and emits pass/fail/structural_reject verdicts per MCF §12.6. Activates the fk_mper_verification_result FK on mcf.metric_publication_eligibility_result.satisfying_verification_result_uid (deferred since M4 per D-16). Folds in the M4 DBCP doc-bug correction per D-M9-8 (M4 inline comment at 06-mcf-lifecycle-certification.sql:179 incorrectly attributes mcf.metric_self_verification_result to M9; corrected inline via COMMENT ON COLUMN UPDATE in M10 DDL). Reuses M9 FixtureStructuralCheckService.runStructuralChecks + PackageSignatureService.computeSelfVerificationFixtureHash + M9 substrate columns (self_verification_fixture_hash, bound_package_signature_hash); no duplicate implementation. Algorithm-versioned mcf-verifier-v1 (separate bundle from mcf-hash-v1; verifier is a different algorithm class). Recommendation M10-A — append-only ledger + JSONB diff trace + synchronous NestJS-injectable verifier service with deps.tx (matches M5/M9 service pattern). 10 D-M10-* operator decisions enumerated. Docs-only. No bc-core edits. No DDL. No data writes. No M11/M12/M14+ work.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m10-self-verification-result-preflight
---

# MCF M10 Self-Verification Result Substrate + Verifier Engine Preflight

## 1. Scope and grounding

Frame the M10 Deterministic Verifier Service gate per build plan §M10. M10 closes the fixture/verifier pair: M9 ships the operator-asserted fixture body + structural-check engine; M10 ships the verifier that executes packages against fixtures and the append-only result ledger that PE-MC-10 cites.

This is **docs-only preflight**. No DBCP. No DDL. No bc-core edits. No M11/M12/M14+ work.

### 1.1 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ read-only |
| No DDL applied or drafted | ✓ |
| No real MCF metric contracts | ✓ substrate empty post-M9 apply |
| No fixture rows | ✓ — fixture substrate dormant |
| No M11 ingestion / M12 panel implementation | ✓ downstream |
| No BCF data touches | ✓ |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

### 1.2 Source documents (referenced from prior context — not re-read here)

- ADR DEC-c3e57f / D422 (MCF M1 foundational)
- MCF requirements §12.6 (verifier behavior — 6-step pipeline ending in pass / fail / structural_reject); §12.7 (stale-fixture rule); §13 PE-MC-10 (cites the satisfying verification result); §17.1 (`mcf.metric_self_verification_result` is **append-only per Invariant V; one row per execution**)
- MCF build plan §M10 (verifier service + result substrate; T-shirt L; primary risk "underbuilding the verifier")
- M9 DBCP `bc-docs-v3 620e11d` §6.4 (computeSelfVerificationFixtureHash helper) + §7.4 (C-FX-1..C-FX-11 engine) + §11.1 (M10 reuses M9 engine) + §11.4 (M4 doc-bug)
- M9 closeout `bc-docs-v3 17669ba` (live state: 15 mcf.* tables, fixture substrate live + dormant; M9 engine merged at bc-core PR #117 / `bcc5705`)
- Live `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` column comment at `bc-core/docker/redesign/06-mcf-lifecycle-certification.sql:179` ← M4 doc-bug location

---

## 2. Current live substrate and code state

After bc-core `bcc5705` + bc-docs-v3 `17669ba`:

| | |
|---|---|
| bc-core main | `bcc5705` (M9 engine merged) |
| bc-docs-v3 main | `17669ba` (M9 apply closeout) |
| `mcf.*` tables | **15 present, all 0 rows** (10 pre-M5 + 4 M5 + 1 new M9) |
| `mcf.metric_self_verification_fixture` | LIVE; dormant; substrate-enforced format/uniqueness/immutability discipline |
| `mcf.fn_msvf_immutability_check` + `trg_msvf_immutability` | LIVE |
| M9 hash helper `computeSelfVerificationFixtureHash(body)` | LIVE on `PackageSignatureService` (PR #117 `bcc5705`) |
| M9 C-FX engine `FixtureStructuralCheckService.runStructuralChecks(context, body)` | LIVE (PR #117 `bcc5705`) |
| M4 deferred FK `fk_mper_verification_result` on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` | DEFERRED — column FK-less; service-layer validation per M4 DBCP |
| M4 inline comment at `06-mcf-lifecycle-certification.sql:179` | known doc-bug: says "FK deferred until M9 ships"; should read "M10" |
| BCF | untouched (10 BC + 2 entity + 24 `contract.panel_output_record` rows + 1 `contract.authoring_panel_rejection_log` row) |

---

## 3. Why M10 is next

| Reason | Detail |
|---|---|
| **Closes the fixture/verifier pair** | M9 substrate + engine are live but dormant; no verifier means no `pass` verdict for PE-MC-10 to cite. M10 makes the M9 substrate actually-useful. |
| **Unblocks PE-MC-10 (M13)** | PE-MC-10 reads `mcf.metric_self_verification_result` rows. Without M10, no result rows exist for the evaluator to consume. |
| **Activates the M4 deferred FK** | `fk_mper_verification_result` has been awaiting M10's table to exist. M10 ships the target table + activates the FK in the same DDL. |
| **Folds in the M4 doc-bug correction (per D-M9-8)** | The M4 inline comment correction is co-located with the FK activation — same DDL line touches it. |
| **Build-plan sequencing** | M10 inputs = M9 (per build plan §M10 lines 252-263). M9 is complete; M10 is the natural next gate. |
| **Substrate-only gate (substrate + service)** | T-shirt size L per build plan; smaller than M11/M12 (XL). Substrate + verifier ship together per M9 substrate-first precedent? Or split? — open question (see D-M10-A1 below). |

---

## 4. M10 ownership boundary

### 4.1 M10 MUST own

| # | Deliverable |
|---|---|
| 1 | `mcf.metric_self_verification_result` table (per MCF §17.1 + build plan §M10; append-only per Invariant V; one row per execution) |
| 2 | Verdict enum CHECK constraint: `verdict_code IN ('pass', 'fail', 'structural_reject')` |
| 3 | Algorithm version CHECK regex (same convention as M2/M9: `^mcf-[a-z-]+-v[0-9]+$`); pinned to `mcf-verifier-v1` in v1 |
| 4 | FK to `mcf.metric_self_verification_fixture(fixture_uid)` (intra-mcf; Drizzle) |
| 5 | Hash format CHECK on `bound_package_signature_hash_at_run` (sha256 regex; matches M9 pattern) |
| 6 | Indexes per query patterns (lookup-by-fixture, lookup-by-mcv, lookup-by-verdict, lookup-by-executed-at) |
| 7 | Activation of `fk_mper_verification_result` on `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` → `mcf.metric_self_verification_result(verification_result_uid)` (deferred since M4 per D-16) |
| 8 | `COMMENT ON COLUMN` UPDATE correcting the M4 doc-bug (per D-M9-8) |
| 9 | Verifier service — `MetricSelfVerificationService.verifyFixture(fixtureUid, deps)` (pure NestJS-injectable; deps.tx) executing the 6-step §12.6 pipeline |
| 10 | Reuse of M9's `FixtureStructuralCheckService.runStructuralChecks` for step 4 (C-FX re-validation) and `PackageSignatureService.computeSelfVerificationFixtureHash` for step 2 (fixture lookup by hash) |
| 11 | Execution engine — per-AST-kind handlers for all 9 kinds in `formula-canonicalization.service.ts` `NODE_KINDS` set (variable_ref / literal / aggregate / arithmetic / comparison / case / window / time_anchor_resolution / bucket_assign) |
| 12 | Reproducibility-test pattern — golden-vector verdicts per AST kind |
| 13 | Dry-run + post-apply verifier scripts (mirroring M9 pattern) |

### 4.2 M10 MUST NOT own

| # | Out-of-scope | Belongs to |
|---|---|---|
| 1 | Fixture authoring path | **M12** Metric Authoring Panel |
| 2 | Reservoir ingestion of fixture proposals | **M11** |
| 3 | PE-MC-10 evaluator (the consumer of result rows) | **M13** |
| 4 | Publication path | **M14** |
| 5 | Real MCF metric contracts / real fixtures / real verification runs | M12+M11+operator (substrate stays empty) |
| 6 | BCF data | NEVER in MCF gates |
| 7 | Operator-console fixture-run UI | **M16** |
| 8 | Async-queue verifier infrastructure | Future amendment if performance demands (sync v1 per D-M10-5) |

---

## 5. Relationship to M9 fixture substrate and engine

### 5.1 What M10 reads from M9 substrate

| M9 column | Used by M10 for |
|---|---|
| `mcf.metric_self_verification_fixture.fixture_uid` | PK to look up fixture body |
| `mcf.metric_self_verification_fixture.self_verification_fixture_hash` | Alternative lookup key (matches DBCP §15.2 #7 pattern) |
| `mcf.metric_self_verification_fixture.bound_package_signature_hash` | §12.6 step 3 stale-fixture check input |
| `mcf.metric_self_verification_fixture.section_a_inputs_json` | §12.6 step 5 execution input |
| `mcf.metric_self_verification_fixture.section_b_expected_output_json` | §12.6 step 6 expected output |
| `mcf.metric_self_verification_fixture.section_c_resolver_config_json` | §12.6 step 5 resolver config |
| `mcf.metric_self_verification_fixture.metric_contract_version_uid` | Loads MCV context for C-FX re-check |
| `mcf.metric_contract.package_signature_hash` (current value) | §12.6 step 3 stale-fixture comparison |

### 5.2 What M10 reuses from M9 engine

| M9 service / method | Reused by M10 at |
|---|---|
| `FixtureStructuralCheckService.runStructuralChecks(context, body)` | §12.6 step 4 (re-validate C-FX-1..C-FX-11 at verifier time) — no duplicate implementation |
| `FixtureStructuralCheckService.validateFixture(mcvUid, body, deps)` | Alternative entry point if M10 prefers full-pipeline call (loader + checks) |
| `PackageSignatureService.computeSelfVerificationFixtureHash(body)` | Re-hash at verifier time for stable-binding cross-check (defense in depth) |
| `FormulaCanonicalizationService.computeFormulaIntentHash(mcvUid, deps)` + `computeVariableBindingSetHash` + `computeFilterSetHash` | Cross-check at verifier time that the package's contributing hashes still match the fixture's snapshots |
| `PackageSignatureService.computePackageSignatureHash(mcvUid, contrib, deps)` | Current package hash for stale-fixture comparison |

**No duplicate engine implementation in M10.** M10 verifier orchestrates M9-shipped services + adds the execution engine + the result-row writer.

### 5.3 What M10 adds (genuinely new code)

- `MetricSelfVerificationService` (orchestrator + result writer)
- `FormulaExecutionService` or equivalent — the per-AST-kind execution engine (9 kinds)
- Resolver-fixture-config interpreter (applies Section C `fiscal_calendar` / `bucket_specs` / `derived_grain_params` to runtime — fixture-scoped, not tenant-bound)
- Tolerance + null-match comparator (Section B `output.tolerance` + `output.null_match_policy`)
- Diff-trace builder (per-row diff JSONB on `fail` verdict)

---

## 6. Result substrate design options

### 6.1 Per §17.1 — substrate is append-only per Invariant V

The MCF §17.1 spec is explicit: *"`mcf.metric_self_verification_result` — Per-(fixture, package_signature_hash, verifier_version) deterministic verification record: verdict (`pass` | `fail` | `structural_reject`), per-row diff trace if fail, reject reason if structural_reject, executed-at timestamp, verifier algorithm version. Per §12.6; **append-only per Invariant V; one row per execution**; cited by `mcf.metric_publication_eligibility_result` rows for PE-MC-10."*

This **locks the append-only ledger shape** by spec. The "latest-result cache" alternative (M10-B below) is excluded by §17.1.

### 6.2 M10-A — append-only ledger + JSONB diff trace + sync verifier (RECOMMENDED)

Single new table `mcf.metric_self_verification_result`:

| Column | Type | Notes |
|---|---|---|
| `verification_result_uid` | uuid PK | `gen_random_uuid()` |
| `fixture_uid` | uuid NOT NULL | FK to `mcf.metric_self_verification_fixture(fixture_uid)` ON DELETE RESTRICT |
| `metric_contract_uid` | uuid NOT NULL | denormalized for query efficiency (matches M9 pattern) |
| `metric_contract_version_uid` | uuid NOT NULL | denormalized; FK to `mcf.metric_contract_version` |
| `verdict_code` | text NOT NULL | CHECK IN (`'pass'`, `'fail'`, `'structural_reject'`) |
| `verdict_payload_json` | jsonb NOT NULL | per-row diff trace (on `fail`); reject reason + offending check (on `structural_reject`); `{}` (on `pass`) |
| `bound_package_signature_hash_at_run` | text NOT NULL | snapshot of MC's `package_signature_hash` at verifier run time; sha256 format CHECK |
| `fixture_bound_package_signature_hash` | text NOT NULL | snapshot from fixture row at run time (for stale-fixture audit) |
| `stale_fixture_flag` | boolean NOT NULL | true when fixture_bound ≠ at_run; verdict_code = `structural_reject` + reason `stale_fixture` |
| `verifier_algorithm_version` | text NOT NULL | `mcf-verifier-v1`; CHECK matches `^mcf-[a-z-]+-v[0-9]+$` (matches M2/M9 convention) |
| `executor_identity_text` | text NOT NULL | service identity (hostname + service version) for forensic audit |
| `executed_at` | timestamptz NOT NULL DEFAULT now() | execution timestamp |
| `execution_duration_ms` | integer NOT NULL | wall-clock ms; useful for performance analysis |

**12 columns** under D162 20-column max. **3 intra-mcf FKs** (fixture / mc / mcv). UNIQUE index on `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` — deterministic verdict per (fixture, package-hash-at-run, verifier-version); prevents accidental duplicate writes (idempotency at substrate level).

**JSONB diff trace** for v1:
- On `pass`: `verdict_payload_json = {}`
- On `fail`: `{ "diff_rows": [...], "tolerance_used": ..., "null_match_policy_used": ... }`
- On `structural_reject`: `{ "reason": "stale_fixture" | "c_fx_<N>_<defect_code>", "defects": [...] }` (defects array reuses M9 `FixtureDefect[]` shape)

**Append-only via service-side discipline** (no trigger needed — service inserts only; no UPDATE/DELETE codepaths). Could add an M3/M5-style unconditional-immutability trigger as defense-in-depth if operator requests (open D-M10-9).

### 6.3 M10-B — latest-result cache + JSONB diff trace

REJECTED — contradicts §17.1's explicit "append-only per Invariant V; one row per execution".

### 6.4 M10-C — ledger + structured child diff rows

M10-A PLUS a `mcf.metric_self_verification_result_diff_row` child table for per-row diff entries (one child row per diff-row in the trace).

**Pros:** Per-diff-row queryability (e.g. "show all verification results where the diff includes a specific grain_keys value"); avoids JSONB size pressure for very large diffs.

**Cons:** Extra table; extra FK; M9 already commits to JSONB for Section A/B/C (consistency favors JSONB for the diff trace too); per-diff-row queries are rare (operators inspect a specific verification result row by uid, not query across diffs).

**Defer.** A child diff-row table can be added in a future amendment if operator queries demand it. JSONB for v1 matches M9's substrate JSONB pattern.

---

## 7. Diff trace / runtime evidence options

| Option | Pro | Con |
|---|---|---|
| **JSONB `verdict_payload_json`** (M10-A choice) | Matches M9 JSONB pattern; one column; flexible schema | No per-row queryability without JSONB operators |
| **Structured child rows** (M10-C deferred) | Per-row queryability | Extra table; size pressure low in practice |
| **Hybrid: JSONB summary + child rows for large diffs** | Best of both | Complexity for v1; schema split logic |

**Recommendation: JSONB for v1 per D-M10-3.** Service-side JSON-schema validation at write time (per M5 `consensus_payload_json` rationale); deeper indexing deferred until operator queries demand it.

---

## 8. Verifier execution model options

### 8.1 Sync service with `deps.tx` (M5/M9 pattern) — RECOMMENDED

```typescript
class MetricSelfVerificationService {
  async verifyFixture(
    fixtureUid: string,
    deps: { tx: Tx },
  ): Promise<{ verdict_code: 'pass' | 'fail' | 'structural_reject'; verification_result_uid: string }> {
    // §12.6 6-step pipeline; emits one mcf.metric_self_verification_result row
  }
}
```

**Pros:** Matches M9/M5 service convention; testable via fake tx; M12 panel calls inline; idempotency via UNIQUE constraint at substrate.

**Cons:** Long-running verifications block the caller's tx. Mitigation: M10 verifier should complete in <1s for typical formulas (per build plan T-shirt L); slow path is a M12 panel UX problem, not a substrate problem.

### 8.2 Async queue (event-driven)

Verifier consumes from a queue table or message bus; emits result asynchronously.

**Pros:** Non-blocking caller; supports batch verification (e.g. re-verify all fixtures after `mcf-verifier-v2` bump).

**Cons:** Adds queue infrastructure; complicates idempotency; M12 panel needs polling/streaming for verdict; not needed for v1.

**Defer.** Sync v1 per D-M10-5; async amendment if performance demands.

---

## 9. Stale-fixture behavior

Per MCF §12.6 step 3 + §12.7 stale-fixture rule:

1. Verifier reads fixture by `self_verification_fixture_hash`
2. Verifier reads MC's current `package_signature_hash`
3. **If fixture.bound_package_signature_hash ≠ MC.package_signature_hash** → verifier returns `verdict_code = 'structural_reject'` with `reason = 'stale_fixture'`, sets `stale_fixture_flag = true`, emits result row
4. PE-MC-10 (M13) sees the `structural_reject` and routes to OPERATOR_REVIEW

**M10 substrate stores BOTH hashes** (`fixture_bound_package_signature_hash` snapshot + `bound_package_signature_hash_at_run`) so the post-hoc audit can confirm the stale-fixture path was correctly taken.

**Operator response to stale-fixture:** author a new fixture against the new package_signature_hash (per M9 D-M9-5 supersession discipline — new `fixture_uid`; no re-author-in-place). Old fixture remains addressable; its old verification results remain addressable; the new fixture gets its own verification results.

**No substrate-side restart / no re-evaluate.** PE-MC-10 simply waits for a fresh `pass` verdict against the current package_signature_hash.

---

## 10. M4 doc-bug correction (per D-M9-8)

### 10.1 The bug

`bc-core/docker/redesign/06-mcf-lifecycle-certification.sql:179` says:

```sql
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.satisfying_verification_result_uid IS
  'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK deferred until M9 ships (D-16). Nullable + FK-less until then; service-layer validation when the table exists.';
```

**"FK deferred until M9 ships" is wrong** — `mcf.metric_self_verification_result` is the M10 table, not M9. M9 ships `mcf.metric_self_verification_fixture`.

### 10.2 Fold-in into M10 DDL

Per D-M9-8: fold the correction into M10 DDL. M10 DDL adds (after activating the FK):

```sql
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.satisfying_verification_result_uid IS
  'PE-MC-10 only: the mcf.metric_self_verification_result row that satisfied this check. FK fk_mper_verification_result activated by M10 (per DBCP M10 §10). Per MCF §13 PE-MC-10 + §17.1 result substrate.';
```

Same atomic transaction as the FK activation. Clean fix.

### 10.3 Alternative

Standalone correction amendment (separate DDL apply). **Rejected** — cleanest to do inline with the FK activation since both touch the same column comment.

---

## 11. Recommendation

**M10-A** — Append-only ledger + JSONB diff trace + sync NestJS-injectable verifier service per build plan §M10 + MCF §17.1.

| Aspect | Decision |
|---|---|
| Table | `mcf.metric_self_verification_result` |
| Shape | append-only ledger (per §17.1 spec lock) |
| Column count | ~12 columns (under D162 20-column max) |
| Hash columns | 2 sha256-format columns (`bound_package_signature_hash_at_run` + `fixture_bound_package_signature_hash`) |
| FKs | 3 intra-mcf (fixture / mc / mcv); all ON DELETE RESTRICT |
| UNIQUE | `(fixture_uid, verifier_algorithm_version, bound_package_signature_hash_at_run)` — substrate-side idempotency |
| Diff trace | JSONB `verdict_payload_json` (consistency with M9 Section A/B/C JSONB pattern; child-row escalation deferred) |
| Verdict | text CHECK IN (`pass`, `fail`, `structural_reject`) |
| Algorithm version | `mcf-verifier-v1` separate bundle from `mcf-hash-v1` (verifier is a different algorithm class) |
| Execution model | sync service with `deps.tx` (matches M9 pattern); async queue deferred |
| Stale-fixture | verifier emits `structural_reject` with reason `stale_fixture`; substrate stores both hashes for audit |
| FK activation | `fk_mper_verification_result` inline in M10 DDL |
| M4 doc-bug | inline `COMMENT ON COLUMN` UPDATE in M10 DDL (per D-M9-8) |
| Verifier service | `MetricSelfVerificationService.verifyFixture(fixtureUid, deps)` |
| Execution engine | per-AST-kind handlers covering all 9 kinds from `NODE_KINDS` |
| Reproducibility | golden-vector verdicts per AST kind (positive + negative pair) |

---

## 12. Risks and stop conditions

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-M10-1 | **Underbuilding the verifier** — ships handling ratio metrics but fails on windowed / computed-dimension / bucket-assign | Medium (per build plan §M10 primary risk) | Coverage check: every AST kind in `NODE_KINDS` has positive + negative tests; reproducibility-test discipline (same input → same verdict across executors) |
| R-M10-2 | **Tolerance + null-match policy under-specified** — Section B declares them per-fixture but verifier needs platform defaults | Medium | M10 impl PR ships platform defaults table per type/unit (mirrors §19.13 Q38 open question; v1 sets sensible defaults; future amendment if needed) |
| R-M10-3 | **Diff trace JSONB size pressure** — very large fixture diffs balloon `verdict_payload_json` | Low | Operator-facing fixtures are bounded (panel UI caps Section A row count); pathological cases route to truncated-trace + escape hatch; child-row amendment available if Q-style queries emerge |
| R-M10-4 | **Stale-fixture race** — between fixture read and MC read, package_signature_hash mutates | Very low (substrate immutability) | `mcf.metric_contract` is immutable post-cert per M3 trigger; race window doesn't exist in practice; M10 verifier reads MC under same tx for snapshot consistency |
| R-M10-5 | **Algorithm-version bump compatibility** — `mcf-verifier-v2` re-runs may differ from `v1` on same fixture/package | Medium (forward-looking) | UNIQUE on `(fixture, package_hash, verifier_version)` admits one row per verifier-version pair; v2 emits new rows; v1 rows remain addressable per Invariant V append-only |
| R-M10-6 | **Sync verifier blocks panel UX** under slow formulas | Low | v1 sync per D-M10-5; if perf issue emerges with real fixtures, async-queue amendment ships post-M12 |
| R-M10-7 | **Cross-AST node verifier semantics drift** — different deployments produce different verdicts | Medium | Algorithm version bundle marker forever-locks v1 behavior; reproducibility test pattern locks behavior; ADR-governed change for v2 |

### Stop conditions

- §19.13 Q38 (tolerance + null-match policy defaults) lands before M10 DBCP → may reshape Section B handling (low likelihood; defaults are operationally choosable)
- §19.13 Q40 (fixture retention) lands → may add `archived_at` column to fixture substrate (out of M10 scope; M9 deferred)
- M11 ingestion DBCP opens first → unlikely to conflict (M11 writes to intake queue, not to results)

---

## 13. Operator decisions needed before M10 DBCP can open

| # | Decision |
|---|---|
| **D-M10-1** | ACCEPT M10-A — append-only ledger + JSONB diff trace + sync verifier (per build plan §M10 + §17.1) over M10-B (cache; spec-rejected) and M10-C (with child diff rows; defer) |
| **D-M10-2** | Result row column inventory — confirm ~12 columns per §6.2; specifically `executor_identity_text` + `execution_duration_ms` (forensic value) — keep, add, drop? |
| **D-M10-3** | Diff trace format — JSONB `verdict_payload_json` for v1; defer structured child-row table to future amendment |
| **D-M10-4** | Algorithm version bundle marker — `mcf-verifier-v1` (separate from `mcf-hash-v1`; recommended) vs reuse `mcf-hash-v1` (would conflate hash bundle + verifier bundle; not recommended) |
| **D-M10-5** | Verifier execution model — sync NestJS-injectable service with `deps.tx` (matches M5/M9 pattern); async queue deferred to future amendment |
| **D-M10-6** | Stale-fixture handling — verifier emits `structural_reject` with reason `stale_fixture` per §12.6 step 3 (recommended); substrate stores both hashes (`fixture_bound_package_signature_hash` + `bound_package_signature_hash_at_run`) for forensic audit |
| **D-M10-7** | FK activation `fk_mper_verification_result` — inline in M10 DDL alongside the new table CREATE (atomic) |
| **D-M10-8** | M4 doc-bug correction — fold inline into M10 DDL via `COMMENT ON COLUMN` UPDATE; correction reads "FK fk_mper_verification_result activated by M10 (per DBCP M10 §10)" |
| **D-M10-9** | Append-only enforcement — service-side discipline (recommended; matches §17.1 "append-only" + M4 cert writer pattern) vs M3/M5-style substrate immutability trigger (defense-in-depth; adds DDL complexity) |
| **D-M10-10** | Reproducibility test pattern — golden-vector verdicts per AST kind (one positive + one negative per kind from `NODE_KINDS`); 9 AST kinds × 2 = 18 minimum reproducibility tests + property-based cross-checks |
| **D-M10-A1** | Combined DBCP shape — single M10 DBCP covering substrate + verifier service + 9 AST execution handlers + reproducibility tests (recommended; matches M9 combined DBCP shape) vs split into M10-substrate + M10-engine PRs (mirrors M9 split) |

---

## 14. Recommended next gate

Combined M10 DBCP per D-M10-A1 (single document) covering:
- Substrate table design (§5.6 DDL sketch)
- 6-step verifier pipeline detail (§12.6 implementation per AST kind)
- M9 reuse mechanics (no duplicate implementation)
- FK activation atomicity
- M4 doc-bug correction inline
- Dry-run + post-apply verifier scripts (mirror M9 pattern)
- Algorithm version + reproducibility test plan
- Test plan for all 9 AST kinds + tolerance + null-match comparator

**Suggested filename:** `metric-context-framework-m10-self-verification-result-dbcp.md`

**Suggested PR title for impl PR (NO DB APPLY):** `feat(mcf): M10 Self-Verification Result Substrate + Verifier Service (NO DB APPLY)`

Sequencing per established M9 pattern:
1. M10 DBCP → operator review → operator-accepted decisions D-M10-1..D-M10-10
2. M10 implementation PR (NO DB APPLY)
3. M10 small-DDL apply gate (separate operator-authorized session)
4. M10 evidence PR + bc-docs-v3 closeout

**Substrate-first sequencing option** (mirrors M9 PR #115 substrate vs PR #117 engine split): operator may choose to split M10 impl into M10-substrate (DDL + Drizzle + scripts) and M10-engine (verifier service + execution handlers + reproducibility tests) PRs. Single PR is recommended for M10 because the verifier service is the gate's defining capability (per build plan §M10) and shipping substrate-only delays unblocking PE-MC-10 (M13). But the split is operationally available if the operator prefers smaller PRs.

---

## 15. What stays closed

| | |
|---|---|
| M10 DBCP | not opened by this preflight |
| M10 impl PR | pending DBCP |
| M10 DDL apply | pending impl PR |
| M10 evidence PR | pending apply |
| **M11 reservoir ingestion** | CLOSED — separate gate (parallel-eligible to M10) |
| **M12 Metric Authoring Panel implementation** | CLOSED — gated on M5 + M7 + M9 + M10 + M11 |
| **M13 PE-MC evaluator** | CLOSED — gated on M5 + M7 + M9 + M10 |
| **M14+** | CLOSED |
| **Real MCF metric contracts** | CLOSED |
| **Real fixtures + verification results** | CLOSED |
| **BCF data changes** | CLOSED — 24 BCF panel + 1 rejection log untouched throughout |
| **Async-queue verifier infrastructure** | DEFERRED — sync v1 per D-M10-5 |
| **Per-diff-row child table** | DEFERRED — JSONB v1 per D-M10-3 (M10-C path) |
| **M9 fixture substrate amendments** | CLOSED — M9 arc complete |
| **MCF defect-code v2 taxonomy** | CLOSED — v1 pinned |
| **MCF hash algorithm v2 bump** (`mcf-hash-v1` forever-lock) | CLOSED unless ADR-governed change |
| **MCF verifier algorithm v2 bump** (`mcf-verifier-v1` forever-lock) | CLOSED at v1 ship; future ADR-governed |
