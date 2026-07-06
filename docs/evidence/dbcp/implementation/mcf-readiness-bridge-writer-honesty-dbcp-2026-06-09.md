---
title: "Track 1 DBCP — MCF-Readiness Bridge + Writer-Verdict Honesty"
status: proposed
date: 2026-06-09
project: bc-core
domain: metrics
subdomain: metrics/mcf-materialization
focus: governance
governing_decision: DEC-7ab22b
related:
  - DEC-7ab22b / D436 (S3 lock — MCF-materialized metrics governed by MCF M13/M14)
  - study mcf-materialized-metric-readiness-visibility-study-2026-06-09.md (D429 Step-5 check-5)
  - D305 (chain_status SSOT) · D391 MLS-14 · HA-1/D426 (MCF zero-legacy-reads)
artifact_kind: change-proposal (design-only; NO DDL / NO schema change)
---

# Track 1 DBCP — MCF-Readiness Bridge + Writer-Verdict Honesty

> **Design-only.** This document proposes a code + read-model change governed under DBCP
> discipline. It is **not** a database change: **no DDL, no schema change, no DB writes,
> no tenant binding, no runtime evaluation.** Implementation is a separate, explicitly-approved PR.
> Governing decision: **DEC-7ab22b (D436)** — MCF-materialized metrics are governed by MCF
> M13/M14 evidence; legacy readiness reports `MCF-governed / legacy-readiness N/A`.

## 0. Problem (recap)
The D429 Step-5 writer materialized ARPI into a legacy `contract.metric_contract` row
(`98ae46ed…`, `metric_definition_id IS NULL`, active) that has **no `contract.chain_status`
row and no `l_node_semantic_verdict`**, while the writer returns a **hardcoded
`chainVerdict:"complete"`**. Per the study, this is an **evidence-emission / visibility gap**,
not an ungated activation. Two honesty defects to fix: (a) the writer claims a legacy verdict it
never computed; (b) legacy readiness consumers render the row as missing/0/broken (and a bulk
D305 refresh would render it **false-RED** via the wrong L1–L8 registry — S1 probe).

## 1. Writer response honesty
**File:** `bc-core/src/registry/mcf/mcf-arpi-materialization-writer.service.ts`
- **Remove** the hardcoded `chainVerdict:'complete'` from `MaterializeArpiResult` (current type at
  ~`:66-77`) and from the success return (~`:145-153`).
- **Return instead** a `readinessMode:'mcf-governed'` discriminator plus a *minimal* evidence
  reference the writer already holds (no new reads): `sourceMcvUid`, and the Guard-A-read
  `mcvGovernanceStateCode` / `mcvIsCurrent`. Example shape (illustrative, not code):
  `{ ..., readinessMode:'mcf-governed', mcfEvidenceRef:{ sourceMcvUid, mcvGovernanceStateCode, mcvIsCurrent, note:'mcf-step5-writer' } }`.
- The writer **does not** claim or compute a legacy chain verdict. Full evidence resolution is the
  bridge's job (read-side), keeping the writer minimal and honest (Foundation Invariant VI).
- **Consumer note:** the only consumer of `MaterializeArpiResult` is
  `mcf-arpi-materialization.controller.ts` (held endpoint). Response shape changes from
  `{chainVerdict}` to `{readinessMode, mcfEvidenceRef}`; document in the controller's ApiResponse.

## 2. Read-only MCF readiness bridge
**New read-only service:** `McfReadinessBridgeService`
(`bc-core/src/registry/mcf/mcf-readiness-bridge.service.ts`) — SELECT-only; **never** writes
`contract.chain_status`, `mcf.*`, or any table.
- **Detection (is this an MCF-materialized metric?):** a `contract.metric_contract` row qualifies iff
  `metric_definition_id IS NULL` **AND** its active version's
  `contract_json.header.lineage[]` contains an entry with `note='mcf-step5-writer'`. The source MCF
  MCV uid is that entry's `from_contract_id` (the writer stamps `from_contract_id = sourceMcvUid`).
- **Resolution (read-only, mcf.*):** from the MCV uid resolve and surface —
  - **Source MCV state:** `mcf.metric_contract_version` → `governance_state_code`, `is_current`.
  - **M13 PE ledger:** `mcf.metric_publication_eligibility_result` (cert NULL = M13 phase; cert SET = M14
    phase) → per-check `pe_check_code` + `verdict_code` summary (total / pass / operator_review).
  - **Verifier:** `mcf.metric_self_verification_result` → `verdict_code`, `stale_fixture_flag`,
    package-hash match.
  - **M14 activation cert:** `mcf.certification_record` (`action_code='metric_transition'`) for the MCV.
- **Output DTO (illustrative):**
  `{ readinessMode:'mcf-governed', legacyReadiness:'N/A', sourceMcvUid, mcvState, mcvIsCurrent,
     m13:{checks,total,pass,operatorReview}, verifier:{verdict,stale}, m14:{activationCertId,transitionAt},
     evidenceLinks:[…] }`.
- **Reuses** the existing read primitives where possible (`McfReadService`, the MCF evidence reads
  the agent mapped); adds no write path.

## 3. UI / API / read-model behaviour
- **Read-model:** the metric-readiness read path (`MetricReadinessService` /
  `chain-status.service.ts:534-561` funnel list) currently `LEFT JOIN`s `chain_status` → MCF-materialized
  rows COALESCE to 0/empty and read as "broken/missing." **Change (read-model only):** detect
  MCF-materialized rows (NULL def + lineage note) and return `readinessMode:'mcf-governed'` +
  `legacyReadiness:'N/A'` + evidence links, **instead of** 0/broken. No `chain_status` row is written.
- **API:** readiness / chain-status responses gain a `readinessMode` field; consumers branch on it.
- **bc-admin** (Metric Readiness `/catalog/metrics/readiness` + funnel): render an **"MCF-governed"**
  badge + evidence links (to the MCF MCV + activation cert), **not** a red/broken/incomplete state.

## 4. Test plan
1. **ARPI row** (`98ae46ed…`) → bridge returns `readinessMode:'mcf-governed'` with the live MCF evidence
   (mocked unit + one integration over the existing mcf.* rows; read-only).
2. **Writer** → spec asserts the result carries `readinessMode:'mcf-governed'` and **no**
   `chainVerdict:'complete'`.
3. **Regression:** a legacy `metric_definition`-backed metric → still uses D305 `chain_status`
   (the bridge activates **only** for NULL-def + lineage-note rows).
4. **No-write guard:** source-guard test greps `mcf-readiness-bridge.service.ts` for
   `INSERT/UPDATE/chain_status/upsert` — must be absent (SELECT-only).

## 5. Explicit exclusions
- **No `chain_status` synthesis** (Reject Option A — would false-RED per S1).
- **No schema change / no DDL.**
- **No tenant binding / no runtime evaluation / no fact writes.**
- **No Track 2 gate-wiring changes** (ContractService / MlsModule / `chainStatusService` DI untouched —
  that is a separate planned investigation).

## 6. Rollback
All changes are additive/behavioural (a writer return-shape change + a new read-only service + a
read-model branch). **Rollback = revert the implementing commit.** No data migration, no DDL, nothing
to un-apply. The writer is already-executed-once for ARPI; the return-shape change affects only the
held controller's future responses.

## 7. Sequencing & gates
- This is the **design DBCP**. Implementation is a **separate approved PR** (gates: tsc baseline,
  eslint `--max-warnings 0`, targeted vitest incl. the 4 tests above, build; SHA-pinned merge; held until
  approval).
- **Precondition:** none beyond DEC-7ab22b (locked). Independent of Track 2.

## 8. Open items
- **OI-T1-1:** choose the integration point for the read-model branch — extend `MetricReadinessService`
  vs a dedicated `GET /api/mcf/materialized-readiness/:metricContractId`. Recommend extending
  `MetricReadinessService` so existing readiness consumers transparently get `readinessMode`.
- **OI-T1-2:** confirm the exact bc-admin readiness/funnel components that must branch on `readinessMode`
  (read-only UI survey at implementation time).
