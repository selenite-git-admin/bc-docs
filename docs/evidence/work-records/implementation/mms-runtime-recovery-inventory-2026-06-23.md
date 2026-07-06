---
title: MMS Runtime Recovery Inventory (2026-06-23)
description: Read-only snapshot of MCF / MMS substrate state on bc_platform_dev. Inventories every Metric Contract + Metric Contract Version + their Publication Eligibility / Self-Verification / Intake status. Classifies each non-active MCV and maps it to the appropriate Recovery Track route. No substrate mutated.
status: draft
authority: implementation-inventory
date: 2026-06-23
project: bc-docs-v3
domain: mms
subdomain: runtime-recovery
focus: inventory
supersedes: []
---

# MMS Runtime Recovery Inventory

## 0. Scope, method, non-goals

**Scope:** read-only snapshot of `bc_platform_dev`'s `mcf.*` substrate via the bc-postgres MCP. Covers Metric Contracts (MC), Metric Contract Versions (MCV), Publication Eligibility check rows, self-verification fixtures + results, intake queue, supersession ledger.

**Method:** parameterized `SELECT` queries against `mcf.metric_contract`, `mcf.metric_contract_version`, `mcf.metric_publication_eligibility_result`, `mcf.metric_self_verification_fixture`, `mcf.metric_self_verification_result`, `mcf.metric_authoring_intake_queue`, `mcf.metric_supersession` joined on key UIDs. No HTTP calls (service health not verified — see §6).

**Non-goals:** no DB writes, no Publication Review run, no Metric Activation run, no materialization, no code/prompt edits, no PR.

---

## 1. Portfolio summary

| Status | Count |
|---|---:|
| **Active MCs** (governance_state_code = `active`, is_current = true) | **4** |
| **Non-active MCs** (governance_state_code = `review`, is_current = false) | **4** of which: |
| &nbsp;&nbsp;— Intentionally abandoned (parent MC archived) | 2 |
| &nbsp;&nbsp;— Genuinely stuck on Publication Review | 2 |
| **Approved-but-not-active** | 0 |
| **Draft** | 0 |
| **Formal supersession ledger rows** (`mcf.metric_supersession`) | **0** — no operator has triggered the M15 supersession flow yet |
| **Intake queue rows** | 12 — see §4 |

---

## 2. Active MCs — current portfolio (4)

All 4 are healthy. Note the **evaluator-version stratification**: each MC's active MCV was finalized under a different Publication Review evaluator version (v2 → v3 → v4 → v6). Per D-M13-9 the older versions are immutable; new evaluations would stamp v6. None require re-evaluation; the older versions remain valid evidence.

| Display name | mc_name | MC uid | MCV uid | Active under | PE summary | Self-verify | Classification |
|---|---|---|---|---|---|---|---|
| **Average Revenue per Invoice** (ARPI) | `average_revenue_per_invoice` | `7453d4dc…` | `ac960286…` | `mcf-m13-v2` + `mcf-m14-v1` | 20 rows, 18 PASS / 2 OPR | 1 pass | HEALTHY_ACTIVE |
| **Billing Volume** | `billing_volume` | `1f142962…` | `81ba6735…` | `mcf-m13-v3` + `mcf-m14-v2` | 22 rows, 20 PASS / 2 OPR | 1 pass | HEALTHY_ACTIVE |
| **Cleared Invoice Amount** | `cleared_invoice_amount` | `2bda5252…` | `57ea07d0…` | `mcf-m13-v4` + `mcf-m14-v2` | 22 rows, 20 PASS / 2 OPR | 1 pass | HEALTHY_ACTIVE |
| **Invoice Processing Cycle Time** (IPCT) | `invoice_processing_cycle_time` | `a4412f05…` | `0511925f…` | `mcf-m13-v6` + `mcf-m14-v2` | 36 rows, 32 PASS / 1 REJ / 3 OPR | 1 pass | HEALTHY_ACTIVE — current-generation evidence |

**Observations:**
- IPCT `a4412f05…` is the newest active MC (2026-06-21). Its MCV holds 36 PE rows because it accumulated re-evaluations across both Publication Review (under v6) and Metric Activation (under mcf-m14-v2). The 1 REJ + 3 OPR rows are historical evidence; the activation succeeded under PASS-equivalent verdict aggregation.
- ARPI (`7453d4dc…`) has a separate non-active sibling MC `4c1c7f89…` that was created on 2026-06-11 via the rebind flow and later abandoned (parent archived). See §3.

---

## 3. Non-active MCVs — classification table (4)

| Display name | MC uid | MCV uid | Parent archived? | PE summary | Self-verify | Classification | Recovery route |
|---|---|---|:---:|---|---|---|---|
| **Average Revenue per Invoice** (ARPI rebind) | `4c1c7f89…` | `e121613c…` | **YES** | 11 rows, 9 PASS / 1 REJ / 1 OPR (mcf-m13-v3) | 1 pass | **INTENTIONAL_ABANDONED** | none needed — already abandoned via the MCV-abandon flow (archived parent MC frees the derived `mc_name`; the original ARPI active MC `7453d4dc…` continues to be the live ARPI) |
| **Invoice Processing Cycle Time** (predecessor) | `82545316…` | `bb033fcf…` | **YES** | 12 rows, 10 PASS / 1 REJ / 1 OPR (mcf-m13-v6) | 1 fail + 1 pass (append) | **INTENTIONAL_ABANDONED** | none needed — operator already abandoned via the abandon flow and re-intaken via operator-direct intake `30afc7dd…` which produced the active IPCT MC `a4412f05…` |
| **Billing Cycle Time** | `37b7e70a…` | `995f90e3…` | NO | 12 rows, 9 PASS / **2 REJ** / 1 OPR (mcf-m13-v6) | **1 fail** | **STUCK_PUBLICATION_REVIEW** + **NEEDS_OPERATOR_DECISION** | inspect the 2 REJ reasons + the verifier failure payload to choose between **R2 Append Fixture**, **R3 Verifier Repair**, **R4 Chain Delta / CC-OC Delta**, **R6 Abandon**, **R7 Restart from Draft**, or **R8 Semantic Supersession** — see §5 |
| **Paid Customer Invoice Count v2** | `dd2567a4…` | `db3e1bd0…` | NO | 12 rows, 10 PASS / **1 REJ** / 1 OPR (mcf-m13-**v5**) | **1 fail** | **NEEDS_RE_EVALUATION** + **STUCK_PUBLICATION_REVIEW** | first **R1 Re-evaluate** under current `mcf-m13-v6` (the v5 REJ may dissipate under newer evaluator logic) — if still REJ, then choose R2 / R3 / R6 / R7 / R8 per the residual REJ reasons |

### 3.1 Why the two `INTENTIONAL_ABANDONED` items aren't drift

Both `4c1c7f89…` and `82545316…` have `archived_at IS NOT NULL` on their parent MC row. This is the canonical signal that the operator invoked `McfMcvAbandonController.abandon` — which soft-archives the parent MC, freeing the derived `mc_name` for re-use, while leaving the MCV row immutably in its `review` state under the archived parent (per the controller's documented "MCV row is NEVER mutated" contract). These are *audit relics*, not stuck candidates. No recovery action is appropriate.

### 3.2 Why the two `STUCK_PUBLICATION_REVIEW` items need operator attention

Both `Billing Cycle Time` and `Paid Customer Invoice Count v2` have:
- Their parent MC **not** archived (so they were never abandoned)
- A Publication Review evaluation that produced at least one REJ verdict
- A self-verification result with `verdict_code = 'fail'`
- A `consumed_by_panel` intake row (so they came through the standard intake → panel → materialize → review pipeline correctly)

These are exactly the cases the Recovery Track was designed for. They are the only two genuine stuck candidates in the substrate.

---

## 4. Intake queue snapshot

12 intake rows total. 7 are `consumed_by_panel` (mapped to the 8 MCs above; one MC has no intake reference because it's the rebind successor `4c1c7f89…`). **5 remain `pending`:**

| Intake uid | candidate_name | reservoir | Ingested | Notes |
|---|---|---|---|---|
| `c77b07c3…` | `invoice_processing_cycle_time` | `operator_direct` | 2026-06-21 12:15 | Created 45 minutes BEFORE the operator-direct intake `30afc7dd…` that produced the live IPCT MC. **Possible duplicate** that was abandoned in favor of the second operator-direct attempt; awaits operator decision (R6 Abandon or leave pending). |
| `21a0b151…` | `paid_customer_invoice_count` | `seed_metrics` | 2026-06-15 02:20 | The v1 candidate (preceded the v2 that's currently stuck). Operator pivoted to v2; v1 intake remains pending unconsumed. **Likely candidate for R6 Abandon** if v2 path is the right one. |
| `a058ec0a…` | `invoice_dispute_rate` | `seed_metrics` | 2026-06-14 16:04 | New seed candidate awaiting panel run. |
| `55296a83…` | `cleared_customer_payment_amount` | `seed_metrics` | 2026-06-13 06:28 | New seed candidate awaiting panel run. |
| `a4424f9c…` | `average_days_to_collect` | `seed_metrics` | 2026-06-11 06:21 | New seed candidate awaiting panel run. |

The 3 `seed_metrics` rows (`a058ec0a…`, `55296a83…`, `a4424f9c…`) are the obvious **forward-motion candidates** — fresh seed candidates that have not yet been run through the M12 / Metric Draft Review panel.

---

## 5. Per-stuck-candidate recovery route map

### 5.1 Billing Cycle Time (`37b7e70a…` / MCV `995f90e3…`)

- Already evaluated under current `mcf-m13-v6`
- PE: 2 REJ + 1 OPR (out of 12) — confirmed Publication-Review blocker, not stale
- Self-verify: 1 fail under `mcf-verifier-v1`
- Intake: `65808332…` consumed (provenance clean)

**Diagnostic sequence (operator-gated):**
1. Read the 2 REJ rows' `evidence_json` to identify which checks (PE-MC-N codes) failed and why
2. Read the verifier-result payload at `mcf.metric_self_verification_result` for the fixture-fail signal
3. Decision tree:
   - REJ reason = fixture-mismatch + self-verify fail → **R2 Append Fixture** (the fixture was wrong; engine extension may have enabled a corrected fixture pattern)
   - REJ reason = chain-resolution / binding fail → **R4 Chain Delta / CC-OC Delta** (a CC or OC needs author work first)
   - REJ reason = duplicate-intent / semantic-collision → **R8 Semantic Supersession** (this metric supersedes an existing active MC under semantic-class rules)
   - REJ reason = grounding / provenance fail → **R5 BCF Admission** (a referenced business concept is missing or not active)
   - Operator concludes metric is wrong-shape → **R6 Abandon** (frees the name; can re-intake under a different shape)
   - Operator concludes mathematical / temporal-gate restructuring needed → **R7 Restart from Draft** (rebind from same intake but with corrected approach)

### 5.2 Paid Customer Invoice Count v2 (`dd2567a4…` / MCV `db3e1bd0…`)

- Evaluated under **stale** `mcf-m13-v5` — current evaluator is `mcf-m13-v6`
- PE: 1 REJ + 1 OPR (out of 12) — may dissipate under v6
- Self-verify: 1 fail under `mcf-verifier-v1`
- Intake: `3bd77357…` consumed (provenance clean)

**Diagnostic sequence (operator-gated):**
1. **R1 Re-evaluate** under `mcf-m13-v6` first — this is the cheapest move and may clear the v5 REJ with no further action
2. If after R1 the rejection persists, proceed with the same decision tree as §5.1
3. Self-verify failure under `mcf-verifier-v1` may or may not clear under v6 re-evaluation — separate from the Publication Review verdict path

**Note:** because R1 only re-runs the Publication Review evaluation under the bumped evaluator version, it's a low-risk read-mostly action. The Foundation Invariant III preserves the old v5 PE rows; the new v6 rows are added alongside.

---

## 6. Service health (not verified this session)

Per operator scope ("do not restart services unless explicitly needed for read-only HTTP checks"), bc-core and bc-admin HTTP health were **not** probed. The DB-only inventory above is sufficient for stuck-candidate identification. If the operator wishes to verify HTTP-tier health, run:

```bash
curl http://localhost:3100/health         # bc-core
curl http://localhost:3010                # bc-admin
```

(No action taken in this session.)

---

## 7. Pending operator decisions

| # | Item | Decision needed |
|---:|---|---|
| 1 | `Billing Cycle Time` recovery route | Read the REJ + verifier-fail payloads → choose R2/R3/R4/R5/R6/R7/R8 (R1 won't help; already at v6) |
| 2 | `Paid Customer Invoice Count v2` recovery route | First **R1 Re-evaluate** under v6 (operator-gated); then decide post-result |
| 3 | Duplicate IPCT operator-direct intake `c77b07c3…` | Either R6 Abandon as a known duplicate, or leave pending if there's a reason it was kept |
| 4 | Stale v1 intake `21a0b151…` (`paid_customer_invoice_count`) | R6 Abandon if v2 is the chosen path |
| 5 | Three fresh seed intakes (`invoice_dispute_rate`, `cleared_customer_payment_amount`, `average_days_to_collect`) | Schedule M12 / Metric Draft Review panel runs whenever the operator is ready to expand the active portfolio |

---

## 8. Recommendation — what can be safely executed next session

### 8.1 SAFE to execute (operator-gated, read-mostly or low-risk)

1. **Read the REJ + verifier-fail payloads for both stuck candidates** (`Billing Cycle Time` and `Paid Customer Invoice Count v2`). Read-only `SELECT ... evidence_json, verdict_payload_json ...` via bc-postgres. Outcome: identifies which Recovery Track route applies.
2. **R1 Re-evaluate `Paid Customer Invoice Count v2` under `mcf-m13-v6`.** Calls `POST /api/mcf/metric-contracts/:uid/evaluate-publication-eligibility` (semantic alias) or the legacy `evaluate-pe-mc` path. Writes new PE rows under v6; preserves old v5 rows under Foundation III. Low risk.

### 8.2 OPERATOR-GATED (decision required first)

3. Any of R2 / R3 / R4 / R5 / R6 / R7 / R8 for `Billing Cycle Time` — requires REJ payload inspection (step 1) before route selection.
4. Same recovery routes for `Paid Customer Invoice Count v2` if R1 doesn't clear the REJ.
5. R6 Abandon for the 2 candidate duplicate / stale intakes (`c77b07c3…`, `21a0b151…`).
6. New panel runs for the 3 pending seed candidates (`invoice_dispute_rate`, `cleared_customer_payment_amount`, `average_days_to_collect`).

### 8.3 EXPLICITLY OUT-OF-SCOPE per operator's session locks

- M13 / Publication Review run
- M14 / Metric Activation run
- Materialization runs
- BCF wave
- CC / OC authoring
- Code edits
- Prompt edits
- PR creation

These were locked off at session open and remain locked.

---

## 9. Recommended next concrete action (single step)

**Read the REJ + verifier-fail payloads for both stuck candidates** to enable route-selection in a subsequent batch. This is purely a `SELECT` and surfaces the exact evidence text the operator needs to choose R2 / R3 / R4 / etc.

Suggested query:

```sql
SELECT mcv.metric_contract_version_uid, mc.display_name,
       per.pe_check_code, per.verdict_code,
       per.verifier_version,
       per.evidence_json
FROM mcf.metric_publication_eligibility_result per
JOIN mcf.metric_contract_version mcv USING (metric_contract_version_uid)
JOIN mcf.metric_contract mc USING (metric_contract_uid)
WHERE mc.display_name IN ('Billing Cycle Time','Paid Customer Invoice Count v2')
  AND per.verdict_code IN ('REJECT','OPERATOR_REVIEW')
ORDER BY mc.display_name, per.pe_check_code;
```

Plus the symmetric query against `mcf.metric_self_verification_result` for the failing verifier payloads.

No write. No execution. No service restart. Operator-gated whether to run.

---

## 10. Explicit no-execution statement

This document is inventory and recommendation only. No DB row was written, no MCV mutated, no Publication Review / Metric Activation invoked, no code edited, no PR opened. The two stuck MCVs (`Billing Cycle Time` and `Paid Customer Invoice Count v2`) remain in their current `review` state with no MCF substrate changes from this session.

Awaiting operator decision on which stuck candidate to recover first, and which recovery route (R1 / R2 / R3 / R4 / R5 / R6 / R7 / R8) to authorize.
