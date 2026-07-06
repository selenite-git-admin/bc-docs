---
title: M13 Publication Review — Evidence-State Fingerprint Design (2026-06-23)
description: Smallest-correct-change design for closing the Publication Review idempotency-cache gap surfaced during R3 Step 3 — PE rows fail to refresh after fixture-append because the cache key doesn't include latest fixture / verifier_result state. Adds an `evidence_state_fingerprint` axis paralleling the existing `chain_state_fingerprint`. No code patch yet.
status: draft
authority: implementation-design
date: 2026-06-23
project: bc-docs-v3
domain: mcf
subdomain: m13-publication-review
focus: idempotency-cache-extension
governing_adr: DEC-2411e4
related_adrs: [DEC-c3e57f]
amendment_to: DEC-2411e4
---

# M13 Publication Review — Evidence-State Fingerprint Design

## 0. Scope and non-goals

**Scope:** design the smallest correct change to `metric-publication-eligibility-evaluator.service.ts` so a fresh fixture-append (with a new verifier_result) properly invalidates the M13 idempotency cache and forces a fresh Publication Review evaluation. PE-MC-10 must read the post-append fixture + verifier_result on the next call. v1 evidence rows remain immutable.

**Non-goals:** no code patch in this batch. No DDL changes executed. No PE row deletion. No `force` override. No PR.

This is an implementation-level design follow-up to ADR DEC-2411e4 / D450 (the v1→v2 verifier bump). The verifier-engine half landed in PR #355; this is the evaluator-cache half of the same evidence-refresh repair.

## 1. Problem statement (one-paragraph)

R3 Step 3 confirmed that the v1→v2 verifier engine produces the correct verdict (PASS for PCIC v2's semantic-equivalent fixture body), and that the fixture-append flow correctly writes a new fixture row + new `mcf-verifier-v2` PASS verifier_result alongside the preserved v1 fail row. But the subsequent Publication Review re-evaluation hit the M13 idempotency cache and returned the prior R1 batch's 12 PE rows verbatim with `retry_mode: true`. PE-MC-10 in those cached rows still references the v1 fail evidence. The M13 evaluator's idempotency tuple — `(mcv_uid, evaluator_version, current_package_signature_hash, chain_state_fingerprint, all 12 PE rows present)` — has no axis covering the latest fixture/verifier_result state, so the cache cannot detect that downstream evidence has changed. Result: substrate is in a correct state (v2 PASS evidence exists) but PE rows are stale and Metric Activation is blocked.

## 2. Current code paths (read-only review)

### 2.1 `findExistingEvaluation` — the cache lookup (`metric-publication-eligibility-evaluator.service.ts:584-633`)

```sql
SELECT pe_result_uid, pe_check_code, verdict_code, evaluated_at
FROM mcf.metric_publication_eligibility_result
WHERE metric_contract_version_uid = ${mcvUid}
  AND verifier_version = ${evaluatorVersion}
  AND COALESCE(evidence_json->>'current_package_signature_hash', '') = ${packageSignatureHash}
  AND COALESCE(evidence_json->>'chain_state_fingerprint', '') = ${chainStateFingerprint}
ORDER BY evaluated_at DESC, pe_result_uid DESC
```

After de-duplication by `pe_check_code` (latest evaluated_at wins), if all 12 codes are present → return cached UIDs+verdicts → `buildIdempotentRetryResult` writes nothing and returns `retry_mode: true`.

**Gap:** the WHERE clause omits fixture/verifier evidence axes that PE-MC-5 and PE-MC-10 actually depend on.

### 2.2 PE-MC-10 inputs (lines 1502-1552)

```ts
const fixture = ctx.fixtures[0];                              // latest fixture (ORDER BY created_at DESC)
const vr = await this.readLatestVerifierResult(tx, fixture.fixture_uid);
const ok =
  vr.verdict_code === 'pass' &&
  vr.stale_fixture_flag === false &&
  vr.bound_package_signature_hash_at_run === currentPackageHash;
```

**PE-MC-10's effective inputs:**
- `fixture.fixture_uid` (latest fixture for MCV)
- `vr.verification_result_uid` (latest verifier_result for that fixture)
- `vr.verdict_code` (pass / fail / structural_reject)
- `vr.stale_fixture_flag`
- `vr.bound_package_signature_hash_at_run`
- `vr.verifier_algorithm_version` (signal-only — surfaced in `m10_verifier_version` of verdict_signals)
- `currentPackageHash` (already in the cache tuple)

### 2.3 PE-MC-5 (`runPeMc5SelfVerificationFixtureStructuralCheck`, line ~1240)

Per the `evaluatorInputsHash` composition at line 1264: `['PE-MC-5', fixture.fixture_uid, result.passed]` — depends on `fixture.fixture_uid` (the structural check is deterministic given the immutable fixture body).

**PE-MC-5 also depends on the latest fixture state**, like PE-MC-10.

### 2.4 Fixture selection (lines 738-751)

```sql
SELECT fixture_uid, ...
FROM mcf.metric_self_verification_fixture
WHERE metric_contract_version_uid = ${mcvUid}
ORDER BY created_at DESC, fixture_uid DESC
LIMIT 1
```

So fixture-append (which creates a new fixture row with later `created_at`) DOES become the "latest" fixture on the next fresh evaluation. The substrate selection logic is correct; it's only the cache check that fails to notice.

### 2.5 `computeChainStateFingerprintInner` (lines 876-912)

```ts
const tuple: JcsValue = [
  'mcf-m13-chain-state-fingerprint-v1',
  ccProjection,             // CC declarations projection
  ocConceptIds,             // OC concept IDs (sorted)
  ocSourceRefsProjection,   // OC source refs projection
  bindingStates,            // BCF binding lifecycle states
];
```

The chain_state_fingerprint covers CC + OC + BCF state. **It does not cover fixture or verifier_result tables.** This is by design — PR-2 added it specifically to handle CC/OC declarations changing, not fixture evidence.

### 2.6 PE row evidence stamping (`composePeRowInputs`, lines 1849-1890)

Every PE row's `evidence_json` includes:
- `check_code`, `evaluator_version`, `evaluator_inputs_hash`
- `current_package_signature_hash`
- `chain_state_fingerprint`
- `verdict_signals` (per-check)
- `ran_at`
- `superseded_by_stale_package_change` (only if predecessors exist)

**The chain fingerprint is stamped on every row** so `findExistingEvaluation` can match later. Same pattern needs to apply to a new evidence fingerprint.

### 2.7 Stale-predecessor detection (`readStalePredecessorPeRowUids`, lines 1810-1845)

```sql
WHERE ...
  AND (
    COALESCE(evidence_json->>'current_package_signature_hash', '') <> ${packageSignatureHash}
    OR COALESCE(evidence_json->>'chain_state_fingerprint', '') <> ${chainStateFingerprint}
  )
```

Stale rows are detected by OR-ing both axes. Any new axis must be OR'd here too so historical PE rows are correctly flagged as stale predecessors when fresh rows write.

### 2.8 Substrate uniqueness — the partial unique index

Per the comment at line 1867-1869: index `idx_mcf_mper_mcv_check_eval_pkg_chain` (DDL file 14 per the comment trail) keys on `(metric_contract_version_uid, pe_check_code, evaluator_version, current_package_signature_hash, chain_state_fingerprint)` with a partial predicate. **This is critical**: if we add a new axis without widening the index, the evaluator's INSERT of fresh PE rows under a new evidence fingerprint will conflict with cached rows at the substrate level (same 5-tuple, different proposed 6-tuple → duplicate). DDL extension is therefore required.

## 3. Design — `evidence_state_fingerprint` axis

### 3.1 Definition

Add a new SHA-256 fingerprint computed per evaluation from the inputs that PE-MC-5 and PE-MC-10 read but the current cache tuple omits.

**Recommended inputs (in JCS-canonical tuple order):**

```ts
[
  'mcf-m13-evidence-state-fingerprint-v1',
  ctx.fixtures.length === 0 ? null : ctx.fixtures[0].fixture_uid,
  // latest verifier_result for the latest fixture (null if no fixture or no result)
  vr?.verification_result_uid ?? null,
  vr?.verifier_algorithm_version ?? null,
  vr?.verdict_code ?? null,
  vr?.bound_package_signature_hash_at_run ?? null,
  vr?.stale_fixture_flag ?? null,
]
```

Hash: `sha256:${createHash('sha256').update(canonicalize(tuple)).digest('hex')}`.

Sentinel-on-error pattern mirrors `computeChainStateFingerprint`: if the read fails, produce a deterministic per-MCV sentinel so the cache stays consistent without polluting unrelated MCVs.

**Why these 7 inputs:**
- `version-tag` (`mcf-m13-evidence-state-fingerprint-v1`): forward-compat versioning of the fingerprint algorithm itself, paralleling `mcf-m13-chain-state-fingerprint-v1`.
- `latest_fixture_uid`: covers PE-MC-5 + PE-MC-10's fixture selection. Changes when fixture-append writes a new fixture.
- `latest_verifier_result_uid` for that fixture: catches the case where the verifier runs again on the SAME fixture and produces a different result (rare but possible if a verifier algorithm bump happens between runs and the fixture body is unchanged).
- `verifier_algorithm_version`: distinguishes v1 vs v2 evidence rows for the same fixture.
- `verdict_code`: distinguishes pass/fail/structural_reject.
- `bound_package_signature_hash_at_run`: catches the case where a fixture-time package signature mismatches the current MCV package signature (the `stale_fixture_flag` should already cover this, but stamping the value is cheap and aids forensic inspection).
- `stale_fixture_flag`: explicit signal for whether the verifier flagged the fixture as stale; affects PE-MC-10's PASS condition.

### 3.2 Why a separate fingerprint (not folded into chain)

**Concerns are semantically distinct:**
- `chain_state_fingerprint` covers **registry-side declarations** (CC / OC / BCF) — read via `McfChainDeclarationReader` against the contract/concept-registry substrate. Changes when authors edit declarations.
- `evidence_state_fingerprint` covers **substrate-side evidence** in `mcf.metric_self_verification_*` — written by the M10 verifier as a side-effect of materialization or fixture-append. Changes when the operator appends a fixture or the verifier reruns.

**Independent change cadence:**
- Chain fingerprint changes are infrequent and operator-authored.
- Evidence fingerprint changes happen automatically when the engine bumps or fixtures append.

**Independent observability:**
- Folding them into one fingerprint would lose the ability to inspect which axis changed when a re-evaluation happens. Two named fingerprints in `evidence_json` give clearer audit traces.

**Independent index extension cost:**
- Both are stored as `evidence_json->>'key'` and can be added to the partial unique index independently. Folding doesn't save schema work.

**Recommendation: separate field.**

### 3.3 Code changes (in 4 places in `metric-publication-eligibility-evaluator.service.ts`)

| Location | Change |
|---|---|
| **`evaluateInTx` orchestration** (around lines 430-456) | After `computeChainStateFingerprint`, compute `evidenceStateFingerprint`. Pass through to `findExistingEvaluation` and `runFirstEvaluation`. |
| **`findExistingEvaluation`** (lines 584-633) | Add `evidenceStateFingerprint` parameter; add `AND COALESCE(evidence_json->>'evidence_state_fingerprint', '') = ${evidenceStateFingerprint}` to the WHERE clause. |
| **`composePeRowInputs`** (lines 1849-1890) | Stamp `evidence_state_fingerprint: evidenceStateFingerprint` into every PE row's `evidence_json` (alongside the existing `chain_state_fingerprint`). |
| **`readStalePredecessorPeRowUids`** (lines 1810-1845) | Add `OR COALESCE(evidence_json->>'evidence_state_fingerprint', '') <> ${evidenceStateFingerprint}` to the OR-chain so stale predecessors are flagged when evidence axis drifts. |

**New private method:** `computeEvidenceStateFingerprint(tx, ctx, currentPackageHash): Promise<string>` — pattern mirrors `computeChainStateFingerprint`. Reads `ctx.fixtures[0]` and calls `readLatestVerifierResult` (already exists). Includes the try/catch sentinel pattern.

Estimated production-code surface: ~50 lines (one new method + 4 small additions). No changes to PE-MC-10's verdict logic itself — it stays read-only against the substrate.

### 3.4 DDL change — widen the partial unique index

**Required.** The substrate enforces 5-tuple uniqueness; without widening, fresh PE row INSERTs after fixture-append would collide with existing rows (same MCV/check/eval/package/chain).

**Target DDL** (in the next-numbered substrate migration file, e.g. `docker/redesign/migrations/d4XX-mcf-pe-result-evidence-state-fingerprint.sql`):

```sql
-- Drop the existing 5-tuple index.
DROP INDEX IF EXISTS mcf.idx_mcf_mper_mcv_check_eval_pkg_chain;

-- Create the 6-tuple index. Partial predicate (e.g. WHERE certification_record_id IS NULL or
-- equivalent — preserve the existing partial condition verbatim) is unchanged.
CREATE UNIQUE INDEX idx_mcf_mper_mcv_check_eval_pkg_chain_evidence
ON mcf.metric_publication_eligibility_result (
  metric_contract_version_uid,
  pe_check_code,
  verifier_version,
  (evidence_json->>'current_package_signature_hash'),
  (evidence_json->>'chain_state_fingerprint'),
  (evidence_json->>'evidence_state_fingerprint')
) WHERE /* existing partial predicate verbatim */;
```

Pre-existing PE rows have NULL `evidence_json->>'evidence_state_fingerprint'`. COALESCE-to-empty in the matching query treats them as a distinct bucket — the new evaluator runs treat them as "stale predecessors" (different evidence fingerprint axis), which is correct.

**Migration safety:**
- Drop+create can run in a single migration; the table is normally small and indexed lookups are not in the hot path during deployment.
- An `IF EXISTS` on the drop makes the migration idempotent.
- Concurrent INSERTs during drop+create are a real concern only in a production cluster with active evaluator traffic — for the bc_platform_dev / single-instance pattern, brief window is acceptable. For production, the index can be rebuilt via `CREATE INDEX CONCURRENTLY` + swap.

**No DDL changes to columns or constraints** — only the partial index expression changes.

### 3.5 Reader behavior (already correct)

The latest-PE-rows query for activation reads (`mcf-read.service.ts:readLatestPeRowsAtPublicationReviewVersion`, per the Layer 2b batch) already selects the latest row per `(MCV, pe_check_code)` by `evaluated_at DESC`. After the fix lands and the evaluator writes fresh PE rows, those become the "latest" for their `pe_check_code` and PE-MC-10 reports PASS. No reader-side change required.

## 4. Test plan

### 4.1 Engine + evaluator unit tests (extend `metric-publication-eligibility-evaluator.service.spec.ts`)

| # | Case | Assertion |
|---:|---|---|
| 1 | **Cached rows reused when evidence fingerprint is unchanged** | After two consecutive evaluations with no substrate change, second call returns `retry_mode: true` with same `pe_result_uids` — confirms cache still works for true retries. |
| 2 | **Cached rows discarded when fixture appends** | After appending a new fixture (with new verifier_result), evaluation returns `retry_mode: false`, writes 12 fresh PE rows, and stamps the new evidence fingerprint. Old rows remain immutable in substrate as stale predecessors. |
| 3 | **PE-MC-10 reads new v2 PASS result** | In the fixture-append scenario, the fresh PE-MC-10 row's `verdict_code = PASS`, `verdict_signals.fixture_uid` references the new fixture, `verdict_signals.verifier_result_uid` references the new v2 result, `verdict_signals.m10_verifier_version = 'mcf-verifier-v2'`. |
| 4 | **Stale predecessors recorded** | The fresh PE rows' `evidence_json.superseded_by_stale_package_change` includes the 12 prior PE row UIDs (the v6/v1-evidence rows from before the append). |
| 5 | **Evidence fingerprint distinct from chain fingerprint** | Inspect a fresh PE row: `evidence_json.evidence_state_fingerprint` and `evidence_json.chain_state_fingerprint` are present, both SHA-256 hex strings, and not equal (they're computed over different inputs). |
| 6 | **Cache axis composition** | `findExistingEvaluation` invoked with mismatched evidence fingerprint returns `null` even when MCV/eval/package/chain match. |
| 7 | **No-fixture / no-verifier-result fingerprints** | When `ctx.fixtures.length === 0` or no verifier_result exists, the fingerprint uses null-sentinel values deterministically and PE-MC-10 still produces REJECT with the existing error signals. |

### 4.2 Integration test (new MCV fixture in `metric-publication-eligibility-evaluator.service.integration.spec.ts`)

End-to-end replay of the PCIC v2 sequence against the docker substrate:
1. Materialize an MCV with one filter clause + one fixture body.
2. Run Publication Review under `mcf-verifier-v1` → PE-MC-10 REJECT (or under v2 with intentionally-filter-failing data → REJECT).
3. Append a new fixture body (semantic-equivalent, different identifiers) with v2 engine running.
4. Confirm new verifier_result row is PASS.
5. Run Publication Review again → fresh PE rows written, PE-MC-10 PASS, old rows preserved.

### 4.3 Substrate-side index test

Add a DDL-level test (or extend an existing schema-lock test) that asserts:
- The widened index exists with the 6-tuple key.
- Attempting to INSERT two PE rows with the same 5-tuple but DIFFERENT evidence fingerprint succeeds (proving the partial uniqueness now keys on the 6th axis).
- Attempting to INSERT two PE rows with the same 6-tuple fails (proving the partial uniqueness still enforces idempotency within an unchanged evidence axis).

## 5. ADR amendment vs new ADR

**Recommendation: ADR amendment to DEC-2411e4 / D450.**

Rationale:
- This is the evaluator-cache half of the same evidence-refresh repair. The verifier-engine half (PR #355) landed under DEC-2411e4; the cache-axis follow-up is the same architectural concern.
- The blast radius is small (one service, ~50 LoC + one substrate migration).
- A new ADR is heavier than warranted; an amendment section in DEC-2411e4 (or a thin successor DEC if the operator prefers stricter lineage) captures the design without over-formalizing.

**Amendment content (one paragraph + a Decision Update section in `ADR-2411e4.md`):**

> §4 Amendment — 2026-06-23: R3 Step 3 surfaced a follow-up gap. The v1→v2 verifier-engine bump correctly writes v2 evidence rows alongside immutable v1 rows, but the M13 Publication Review evaluator's idempotency cache (`findExistingEvaluation`) keys on a 5-tuple that omits the latest fixture/verifier_result state. After fixture-append, the cache returns prior PE rows that still reference the old v1 verifier_result, blocking PE-MC-10 from reflecting the new v2 PASS evidence. Extension: add an `evidence_state_fingerprint` axis to the cache tuple, stamped on every PE row's `evidence_json`, computed from latest fixture + latest verifier_result + verdict_code + verifier_algorithm_version + bound_package_signature_hash + stale_fixture_flag. Mirror the existing `chain_state_fingerprint` pattern. Widen the substrate partial unique index to include the new axis. Update the readStalePredecessorPeRowUids OR-chain. Implementation surface ~50 LoC + one DDL migration. Design document: `bc-docs-v3/docs/implementation/mms-publication-review-evidence-fingerprint-design-2026-06-23.md`.

If the operator prefers a successor ADR (`DEC-XXXXXX / D-next` supersedes-strict-amend-pointer to DEC-2411e4), the design content is identical; only the registry framing changes.

## 6. Alternatives considered

| # | Alternative | Verdict |
|---:|---|---|
| 1 | Fold evidence state into existing `chain_state_fingerprint` | **Rejected** — conflates registry-side declarations with substrate-side evidence; loses observability on which axis changed; doesn't reduce schema work. |
| 2 | Add a `force_re_evaluate` request parameter to the M13 endpoint | **Rejected** — operator-override surface invites misuse; doesn't solve the design gap structurally; would be needed even after a "proper" fix in operator workflows where evidence changes without operator awareness. |
| 3 | Out-of-band SQL DELETE of cached PE rows | **Rejected** — violates Foundation III; not a sustainable mechanism. |
| 4 | Per-check fingerprint axes (different cache key per PE check) | **Rejected** — too granular; the current single-chain-fingerprint pattern collapses the inputs of all chain-sensitive checks into one axis, and one evidence fingerprint serves the same role for evidence-sensitive checks (PE-MC-5 + PE-MC-10). |
| 5 | Restructure M13 to read evidence freshly inside the cache-check itself | **Rejected** — much larger refactor; conflicts with the "PE rows are the authoritative cache" pattern that PR-2 chain-state extension established. The fingerprint-axis pattern is the established idiom. |

## 7. Risk and rollback

**Risks:**
- Migration timing: dropping/recreating the partial unique index briefly relaxes uniqueness on the table. For a single-instance dev/staging cluster this window is acceptable; for production, use `CREATE INDEX CONCURRENTLY` + atomic swap.
- Pre-existing rows lack `evidence_state_fingerprint` in their evidence_json. The new evaluator runs treat them as stale predecessors (correct), and they remain present per Foundation III. The widened partial unique index treats their NULL fingerprint as a distinct bucket.
- Fingerprint version tag (`mcf-m13-evidence-state-fingerprint-v1`) reserves room for future evolution (e.g., a v2 that also covers computed dimension references). Not strictly necessary in v1 of the fingerprint algorithm.

**Rollback:**
- Code revert: straightforward — remove the 4 additions and the new method.
- Schema rollback: re-create the original 5-tuple index. The new evidence_state_fingerprint columns in JSON are harmless if left in place after schema rollback (they're just keys in `evidence_json` that nothing reads).
- Data: no rows deleted. v1 evidence and v6/v5 PE rows remain immutable.

## 8. Out of scope

- **`having` clause support** — already deferred to a future v3 verifier; no impact on PE-MC-10's cache logic.
- **Multi-fixture PE checks** — current PE-MC-5 + PE-MC-10 read only the latest fixture. Future MCF iterations may want to evaluate against multiple fixtures (e.g., cross-fixture invariants); not in this design's scope.
- **Tenant-scoped verifier evidence** — the substrate keeps verifier_result table at platform scope; future tenant-runtime extensions are out of scope.

## 9. Implementation plan (when authorized)

1. **Author ADR amendment** to DEC-2411e4 (or new successor DEC if operator prefers stricter lineage).
2. **DDL migration**: drop old partial unique index; create new 6-tuple partial unique index. Schema-lock test.
3. **Service code**: add `computeEvidenceStateFingerprint` method; thread it through `evaluateInTx` → `findExistingEvaluation` → `composePeRowInputs` → `readStalePredecessorPeRowUids`.
4. **Unit tests**: extend `metric-publication-eligibility-evaluator.service.spec.ts` with the 7 cases in §4.1.
5. **Integration test**: extend the integration spec with the end-to-end replay in §4.2.
6. **Schema-lock test**: extend `metric-publication-eligibility-result.spec.ts` (or equivalent) with the 6-tuple index assertion.
7. **PR**: open as draft, gate on operator review of the ADR amendment + the migration timing window.
8. **Post-merge live recovery for PCIC v2**: re-run Publication Review against MCV `db3e1bd0…` — under the widened cache logic, cache misses on the now-different evidence fingerprint → fresh PE rows written → PE-MC-10 PASS → Metric Activation becomes eligible (operator-gated).

Estimated total surface: ~70-90 LoC across 1 service + 1 DDL migration + 1-2 spec files. Smaller than the v2 engine PR.

## 10. Explicit no-execution statement

This document is design and recommendation only. No file in `bc-core/src` was edited. No DDL was executed. No migration was authored. No PR was opened. The PCIC v2 MCV `db3e1bd0…` remains in `review` state with the cached PE rows from the prior R1 batch; the v2 PASS verifier_result `ea3a3ca4…` and the new fixture `e027b024…` are in substrate as written by R3 Step 3.

Implementation requires operator authorization plus selection between ADR amendment vs new successor DEC.
