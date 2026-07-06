---
title: "Phase 1 bulk BF semantic remediation — operational SOP"
task: TSK-9515d5
date: 2026-05-15
status: plan
type: sop-plan
authority: DEC-a49413
related:
  - DEC-a49413   # §11 BF SDA-trust predicate; §12 BF semantic remediation
  - DEC-a17d0f   # SDA umbrella authority
  - DEC-804874   # D366 participant-trust substrate
  - 4cdad6a      # bc-core: audit-suggest-standard-ref-coverage.mjs (read-only coverage audit)
  - 6a53c5a      # bc-core: StandardFieldService.suggestStandardRef + GET /api/business-fields/:id/suggest-standard-ref
  - c074a2a      # bc-core: §12 remediateBfSemantics + repo.updateBfSemanticsWithAuditTx
---

# Phase 1 Bulk BF Semantic Remediation — Operational SOP

**Status:** plan, awaiting operator approval.
**Scope:** one-off operational procedure. Not a contract change. The §12 contract (DEC-a49413 v5) is unchanged.
**Implementation:** deferred. This SOP must be filed and approved before the bulk script (`bc-core/scripts/bulk-remediate-bf-semantics.mjs`) is authored.

---

## 1. Purpose and authority

**Purpose.** Acquire SDA §11 trust evidence for the largest defensible cohort of legacy-certified OAGIS business fields — those with exactly one HIGH-confidence `standardRef` candidate from the read-only provenance audit — by invoking the existing single-BF §12 remediation endpoint sequentially, one BF per atomic transaction, with full audit capture.

**Authority chain.**
- **DEC-a49413 §11** — BF SDA-evidence read predicate. Defines the §11 trust set: `status_code='certified' AND EXISTS certification_record with action_code IN ('certify', 'remediate_bf_semantics')`. The cohort below is the complement of §11-trusted within OAGIS.
- **DEC-a49413 §12** — Post-certify BF semantic metadata remediation. Single governed write path. Atomic UPDATE of four columns (`semantic_family`, `unit_type_code`, `definition_standard`, `standard_ref`) plus INSERT of one `remediate_bf_semantics` certification_record. No override path. G1–G8 evaluated against projected post-update row; any failure refuses the row.
- **DEC-a17d0f** — SDA umbrella authority. Primitive certification semantics; non-overridable G5/G6/G7/G8.
- **DEC-804874 / D366** — participant trust substrate. BF trust feeds BO Gate 4 which feeds MC activation. **BF semantic remediation does not trigger any L-node refresh.** D366's `LNodeSemanticService` operates on canonical fields and metric contracts, not on business fields; Phase 1 writes touch BF metadata only, so no L-node verdict recomputation is invoked, scheduled, or required as part of this SOP.

**Operational artifacts.**
- Read-only coverage audit script: `bc-core/scripts/audit-suggest-standard-ref-coverage.mjs` (commit `4cdad6a`). Replicates the suggestion logic in-process; no writes.
- Provenance suggestion service: `StandardFieldService.suggestStandardRef(fieldId)` and `GET /api/business-fields/:fieldId/suggest-standard-ref` (commit `6a53c5a`). Read-only; no writes.
- Single-BF remediation endpoint: `POST /api/business-fields/:fieldId/remediate-semantics` (commit `c074a2a`). Atomic UPDATE+INSERT; no override.

**Canary baseline.** `invoice_hdr_total_amount` was the single-BF §12 canary (SES-594568). It is **already remediated** with `standardRef='https://www.oagidocs.org/docs/invoice-header#total-amount'` and is therefore **excluded** from this cohort by the §11 evidence filter. It serves as the visual gold standard for what a successful Phase 1 row looks like post-write.

---

## 2. Cohort definition

A BF is in the Phase 1 cohort iff **all** of the following hold:

1. `business_field.status_code = 'certified'`
2. `business_field.definition_standard = 'OAGIS'`
3. No row in `contract.certification_record` with `primitive_type='business_field'`, `primitive_id=field_id`, and `action_code IN ('certify','remediate_bf_semantics')` (i.e. no §11 evidence yet).
4. `suggestStandardRef(fieldId)` returns **exactly one** candidate, and that candidate's `confidence = 'high'`.
5. The BF's `(representation_term, data_type)` maps to a row in the frozen derivation table (§3) **other than** the excluded rows (`Amount`, `Quantity`, `Number`).

**Exclusions (explicit).**
- Multiple-HIGH BFs — disambiguation requires operator choice; deferred to Phase 2.
- MEDIUM candidates — single signal only; defer to Phase 3 with mandatory spot-rate ≥10%.
- LOW candidates — none exist in the current corpus; reserved.
- No-candidate BFs — seed gap (`no_crosswalk`) or property-shape mismatch (`no_field_match`); defer to Phase 4 (seed enrichment) or manual authoring.
- `measure-currency` and `measure-quantity` families — G6 requires a `unit_type_code` that this cohort has no clean signal for; defer to Phase 1b after a unit-resolution playbook lands.
- Any BF whose locally-replayed `evaluateProjectedBfGates` predicts a failure — skipped before the network call; logged.

**Indicative size.** Audit run on 2026-05-15 returned 1,946 HIGH (391 multi-HIGH, so 1,555 single-HIGH). Subtracting Amount/Quantity exclusions yields the live Phase 1 size, which the script recomputes at run start.

---

## 3. Frozen derivation table (Phase 1 only)

`definitionStandard` is fixed at `OAGIS`. `standardRef` is the single HIGH candidate from `suggestStandardRef`. The remaining two columns are derived as below.

> **Source-of-truth alignment.** This table is derived from the live SDA enum in `bc-core/src/registry/semantic-definitions/profiles.ts` (`SEMANTIC_FAMILY_ENUM`) and the G6 compatibility matrix in `bc-core/src/registry/semantic-definitions/gates.ts` (`DEFAULT_FAMILY_COMPATIBILITY`) **as of 2026-05-15**. If either changes — a family added, a `compatible_data_types` or `compatible_unit_types` widened or narrowed — this SOP must be revalidated against the new shape before another bulk run.

### Phase 1 included mappings

| representation_term | data_type | semanticFamily | unitTypeCode | Audit flag | Phase 1 disposition |
|---|---|---|---|---|---|
| Identifier | `string` | `identifier` | `null` | — | included |
| Code | `string` | `code` | `null` | — | included |
| Name | `string` | `name` | `null` | — | included |
| Text | `string`, `text` | `text` | `null` | — | included |
| Date | `date` | `date` | `null` | — | included |
| DateTime | `timestamp` | `datetime` | `null` | — | included |
| Percent | `number` | `measure-percent` | `percentage` | — | included |
| Rate | `number` | `measure-ratio` | `ratio` | `rate_as_ratio=true` | included |

The `Rate → measure-ratio` mapping is a deliberate semantic projection: the SDA enum has no `measure-rate` family today, and `measure-ratio` is the closest compatible family in G6 (`compatible_data_types=['number']`, `compatible_unit_types=['ratio']`). Every row emitted under this mapping carries `audit.flags.rate_as_ratio=true` in its JSONL line so it can be re-examined if/when an explicit rate family is introduced.

### Phase 1 deferred and refused

| representation_term | data_type | Reason | Disposition |
|---|---|---|---|
| Indicator | `boolean` | No live SDA family for boolean indicators (`indicator` is not in `SEMANTIC_FAMILY_ENUM`). | **deferred — needs SDA enum extension** |
| Identifier | `code` | G6 `compatible_data_types` for `identifier` is `['string']`; `code` violates G6. | **deferred — data-shape mismatch** |
| Code | `code` | G6 `compatible_data_types` for `code` is `['string']`; `code` violates G6. | **deferred — data-shape mismatch** |
| Amount | `number`, `currency` | `measure-currency` requires `unit_type_code` from the G6 currency list; Phase 1 has no clean signal for which currency unit applies. | **deferred — Phase 1b (unit-resolution playbook)** |
| Quantity | `number`, `integer` | `measure-count` requires `unit_type_code='count'`; cohort has no clean signal for which count unit applies. | **deferred — Phase 1b** |
| Number | `number`, `integer` | Ambiguous representation term; no defensible family selection. | **refused — no derivation** |
| anything else | — | `(representation_term, data_type)` pair not in either table above. | **excluded with `result='no_derivation_rule'`** |
| any row whose final `(family, data_type, unit_type_code)` triple fails G6 | — | Local replay of `DEFAULT_FAMILY_COMPATIBILITY` predicts G6 failure. | **excluded before POST with `result='dry_run_gate_failed'`** |

### Rules

- A `(representation_term, data_type)` pair not in the **Phase 1 included** table → row excluded with `result='no_derivation_rule'`. No guesses, no fallbacks.
- `Number` is always refused. It carries no semantic signal sufficient to pick a family.
- The table is **frozen for this cohort run**. Any change requires a follow-up SOP note for the next phase.
- BF `data_type` widening (e.g. allowing `Identifier+code` BFs to pass G6) is **out of scope for Phase 1** — that is a structural BF edit, blocked by the certified-row immutability rule.
- Indicator/boolean BFs are deferred pending an SDA enum decision (separate ADR or DEC slice); they will not appear in any Phase 1 JSONL row beyond `result='deferred_no_family'`.

---

## 4. Run protocol

**Concurrency.** 1 (sequential). Auditability beats throughput; the cohort is small enough.

**Modes.**
- `--mode=dry-run` (default): for each cohort row, derive payload, call read-only `suggestStandardRef`, locally replay `evaluateProjectedBfGates`. Emit one JSONL line. **No network POST.**
- `--mode=apply`: repeat dry-run logic; only on local pass does the script POST to the §12 endpoint.

**Apply phasing (mandatory cadence).**

| Step | `PHASE1_MAX_APPLY` | Operator action between steps |
|---|---:|---|
| Dry-run | (n/a — full cohort) | Review 30 random rows; 30/30 required to proceed (§6) |
| Apply 25 | 25 | Review **100% of JSONL output**; confirm cert_record_id and post-state for all 25 |
| Apply 250 | 250 | Sample 30 random successes; spot-check semantic correctness |
| Apply remainder | unbounded | Sample 50 random successes post-completion (§6) |

**Resume behavior.** The script checks `hasSdaCertification(fieldId)` and `definition_standard` at the top of each row, not at script start. A BF that became §11-trusted between ticks is skipped with `result='already_trusted'`. Re-running an interrupted apply naturally resumes.

**Drift guard (amended 2026-05-15 post run-1 to allow staged-apply shrinkage).** Apply mode refuses to run unless a prior dry-run JSONL is supplied via `--from-dryrun=<path>`. The contract is now **no new unreviewed live cohort members**, not strict set equality:

- **Block on EXPANSION.** If the live cohort contains any `fieldId` that does not appear in the dry-run with `result='dry_run_ok'`, refuse with exit 4. This means a new candidate BF entered the cohort since the dry-run and has not been operator-reviewed.
- **Allow SHRINKAGE.** `dry_run_ok` `fieldIds` that are missing from the live cohort are tolerated. Each successful remediation acquires §11 evidence and removes that row from the cohort; staged apply runs therefore naturally shrink it. Other legitimate reasons a row leaves the cohort: independent certification path, status change to `deprecated` / `withdrawn`, definition_standard change off OAGIS.
- **Why this is still safe.** The per-row §11 recheck (immediately before each POST) catches any row that left the cohort for a non-trust reason: the recheck returns `false` (no §11 evidence), the local-gate replay would still run, and any anomaly surfaces as `local_gate_failed` and halts the run.
- **Operational shape.** The script prints a "DRIFT GUARD REPORT" block with four counts before deciding: `live cohort count`, `dry_run_ok count`, `trusted / removed since dry-run` (allowed), `unexpected live additions` (blocks if non-zero). The `--preflight-only` flag re-runs this report without env/token requirements and without entering the POST loop, exit 0 on accept / exit 4 on block.

If unexpected live additions appear, the operator must re-run dry-run to review the new candidates and produce a fresh JSONL before any further apply.

The earlier strict-equality wording is superseded: it caused legitimate staged-apply phasing (run-1 → run-2 → run-3 from the same dry-run) to fail at the cohort gate after each successful run. The shrinkage-tolerant rule preserves the original guarantee that no unreviewed row reaches a POST.

**Pacing.** Log a progress line every 50 rows. No artificial sleep between rows; the §12 endpoint sequencing is the natural rate limit.

---

## 5. Audit output

**JSONL path.** `bc-core/scripts/audit-output/phase1-bf-remediation-{mode}-{ISO8601}.jsonl`. One line per processed BF.

**Per-row schema.**

```json
{
  "ts": "2026-05-15T18:42:11.412Z",
  "fieldId": "...",
  "name": "actual_ledger_action_code",
  "objectClass": "actual_ledger",
  "before": {
    "definitionStandard": "OAGIS",
    "standardRef": null,
    "semanticFamily": null,
    "unitTypeCode": null
  },
  "proposed": {
    "definitionStandard": "OAGIS",
    "standardRef": "https://www.oagidocs.org/docs/actual-ledger#action-code",
    "semanticFamily": "code",
    "unitTypeCode": null
  },
  "provenance": {
    "noun": "actual-ledger",
    "componentSlug": "actual-ledger",
    "fieldSlug": "action-code",
    "sourceVersion": "10.12",
    "evidence": {
      "crosswalkMatch": true,
      "descriptionMatch": true,
      "propertyMatch": true,
      "derivedBfNameMatch": true
    }
  },
  "dryRunGates": { "verdict": "pass", "gates": [ /* G1..G8 verdicts */ ] },
  "mode": "apply",
  "httpStatus": 200,
  "result": "success",
  "certificationRecordId": "cr-...",
  "error": null
}
```

**Result values.** `success`, `dry_run_ok`, `already_trusted`, `no_derivation_rule`, `excluded_phase1b_unit`, `deferred_no_family`, `deferred_data_shape`, `dry_run_gate_failed`, `endpoint_422`, `endpoint_5xx`, `skipped_drift_guard`.

**Summary CSV.** Written at end of run to `audit-output/phase1-bf-remediation-{mode}-{ISO8601}-summary.csv`:
- per-result row counts
- per-`objectClass` success rate
- top 10 error messages with counts
- run duration, average latency per POST

**Retention.** JSONL outputs and `pg_dump` snapshots are retained for **90 days** under `bc-core/scripts/audit-output/`. Older artifacts may be archived to S3 (`s3://barecount-dev-artifacts/phase1-bf-remediation/`) and pruned from local disk per existing repo discipline; the index file `audit-output/INDEX.md` records what moved where.

---

## 6. QA

### Pre-apply (mandatory)
- Operator picks **30 random rows** from the dry-run JSONL.
- For each: open `standardRef` in browser, confirm OAGIS field matches BF semantics; confirm `semanticFamily` and `unitTypeCode` are correct; confirm before/proposed deltas look right.
- **Acceptance: 30/30.** Any error → halt; debug the derivation table, suggestion service, or seed; do not enter apply mode.

### Apply 25 (run 1)
- Operator reviews **100% of JSONL output** (25 lines).
- Confirms `result='success'` and a non-null `certificationRecordId` on every line.
- Spot-reads two `certification_record` rows directly in pg to verify `from_state_code='certified'`, `to_state_code='certified'`, `action_code='remediate_bf_semantics'`, and `gate_results_json` is populated.

### Apply 250 (run 2)
- Operator samples **30 random successes** from this run's JSONL.
- Semantic spot-check per the pre-apply protocol.
- **Acceptance: ≥29/30.** Below threshold → halt and file defect.

### Apply remainder (run 3)
- Operator samples **50 random successes** post-completion.
- **Acceptance: ≥49/50** correct. Below threshold → halt Phase 1, file defect, do not roll back yet.

### Canary baseline assertion (mandatory pre-flight)
- The script asserts at start of every run (dry-run and apply):
  - `business_field.field_id` for `invoice_hdr_total_amount` resolves.
  - `hasSdaCertification(fieldId) === true`.
  - `business_field.definition_standard = 'OAGIS'`.
  - `business_field.standard_ref = 'https://www.oagidocs.org/docs/invoice-header#total-amount'`.
- Any assertion failure → abort the run before processing any cohort row. A regression on the canary is a stop-the-world signal.

---

## 7. Halt criteria

The script halts (exits non-zero, flushes JSONL, prints last successful `fieldId`) on any of:

- **3 consecutive 5xx** responses from the §12 endpoint.
- **5 consecutive 422** with the **same** gate failure (suggests a derivation-table or gate bug, not row-by-row mismatch).
- **Endpoint p50 latency > 2 s** over a 50-row trailing window (bc-core health, not cohort issue).
- **Any pre-apply sample error** during the 30/30 pre-apply review (operator-driven halt; not script-driven).
- **Canary baseline assertion failure** (§6).

Resume after halt is the same as resume after interrupt: re-run with the same dry-run input; the §11 evidence check at row start skips successes.

---

## 8. Rollback / correction

**Forward-only correction. No automatic rollback.**

- Each row is an independent atomic transaction. A wrong row remains as a recorded `remediate_bf_semantics` ledger entry. It is **corrected** by a **second** `remediate_bf_semantics` call against the same BF with the right payload. The §11 trust predicate is satisfied by *any* matching ledger row, so trust persists across corrections; the audit trail gains a second row.
- **No `withdraw_bf_semantics` action_code in Phase 1.** The `certification_record.action_code` CHECK constraint is not extended. If a systemic bug forces a mass reset, that becomes a future DBCP under its own ADR; do not pre-build it.
- **Snapshot strategy.** Operator takes `pg_dump --schema=contract --table=business_field --table=certification_record` immediately before each apply run (3 snapshots total: pre-25, pre-250, pre-remainder). Snapshots retained 90 days.
- **Restore from `pg_dump`** is **break-glass only** under an explicit DBCP with operator approval. It is not part of the normal flow and not invoked for individual wrong rows.

---

## 9. Hard boundaries (restated)

- ❌ **No metric promotion** in this phase.
- ❌ **No CF row changes.**
- ❌ **No direct SQL writes.** Every column change goes through the §12 endpoint.
- ❌ **No MEDIUM, multi-HIGH, no-candidate rows** in the cohort.
- ❌ **No `measure-currency` or `measure-quantity`** rows in Phase 1 (deferred to Phase 1b).
- ❌ **No fabricated standardRefs** — every row carries an evidence-traced suggestion from `seed_oagis_components`.
- ❌ **No override path** — any single G1–G8 failure refuses the row; the script does not retry with weakened payloads.
- ❌ **No tenant DB touches** — BF metadata is platform-scope.

---

## 10. Expected blast radius

| Surface | Effect |
|---|---|
| `contract.business_field` (cohort rows) | 4 columns populated; `status_code` unchanged |
| `contract.certification_record` | +1 row per success (upper bound: live cohort size) |
| §11 trust predicate | +N BFs become SDA-trusted (N = successful applies) |
| BO Gate 4 (D407 v4 §11) | BOs whose only remaining gap was these BFs unblock |
| `metric.*`, `progression.*`, `fact.*` | **No change.** Reads do not trigger evaluation (Foundation Boundary-Independent Rule 2) |
| D366 L-node verdicts (`contract.l_node_semantic_verdict`) | **No change.** L-node compute is CF/MC-scoped; BF semantic remediation does not invoke or schedule any L-node refresh |
| Existing snapshots | **No change.** |
| CFs and MCs | **No change.** Out of scope |
| Tenant runtime | **No change.** |

---

## 11. Next artifact

Implementation script `bc-core/scripts/bulk-remediate-bf-semantics.mjs`. The script's header will reference this SOP by relative path, the audit script commit (`4cdad6a`), and `DEC-a49413 §12`. Authoring deferred until this SOP is approved by the operator.

---

## 12. Cross-references

- `bc-docs-v3/docs/adrs/ADR-a49413.md` §11, §12
- `bc-docs-v3/docs/adrs/ADR-a17d0f.md` (SDA umbrella)
- `bc-docs-v3/docs/adrs/ADR-804874.md` (D366 participant trust)
- `bc-core/scripts/audit-suggest-standard-ref-coverage.mjs` (commit `4cdad6a`)
- `bc-core/src/registry/standard-field.service.ts::remediateBfSemantics` (commit `c074a2a`)
- `bc-core/src/registry/standard-field.service.ts::suggestStandardRef` (commit `6a53c5a`)
- Canary record: SES-594568, BF `invoice_hdr_total_amount`
