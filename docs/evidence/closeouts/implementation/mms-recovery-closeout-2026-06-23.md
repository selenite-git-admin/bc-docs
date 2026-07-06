---
title: MMS Recovery — Closeout Checkpoint (2026-06-23)
description: Final-state checkpoint after PCIC v2 activation. Records the recovery chain (verifier v2 + evidence-state fingerprint + DDL 15 + Publication Review + Metric Activation), active catalog (5 metrics), one remaining stuck MCV, and deferred cleanup before BCF waves resume.
status: closed
authority: implementation-checkpoint
date: 2026-06-23
project: bc-docs-v3
domain: mcf
subdomain: m13-publication-review
focus: recovery-closeout
governing_adr: DEC-2411e4
related_adrs: [DEC-c3e57f]
---

# MMS Recovery — Closeout Checkpoint (2026-06-23)

The end-to-end MMS recovery sequence triggered by R3 (filter-clause verifier repair) is complete. PCIC v2 is live on the platform metric catalog. This checkpoint records the final state so subsequent work — BCF waves first — can resume without carrying hidden MMS ambiguity.

## 1. Active metric catalog (after PCIC v2 activation)

| MCV UID | mc_name | version | governance | is_current |
|---|---|---|---|---|
| `ac960286-…` | average_revenue_per_invoice | v1 | active | true |
| `81ba6735-…` | billing_volume | v1 | active | true |
| `57ea07d0-…` | cleared_invoice_amount | v1 | active | true |
| `0511925f-…` | invoice_processing_cycle_time | v1 | active | true |
| `db3e1bd0-051b-401f-8278-e3cd84e622a7` | **paid_customer_invoice_count_v2** | v1 | active | true |

- 5 active/current MCVs total (was 4 pre-recovery).
- PCIC v2 activation cert: `edfe5c90-73d1-41b8-9a05-872827870f9c` (`mcf.certification_record`, `action_code=metric_transition`, `approved → active`, `policy_version=1.0.0`).
- 12 activation PE rows under `verifier_version=mcf-m14-v2`, cert-linked, carrying `evidence_state_fingerprint=sha256:6c8df6b39…` (matches the Publication Review evidence set).

## 2. Recovery chain

| Step | Artifact | Outcome |
|---|---|---|
| 1 | PR [bc-core#355](https://github.com/selenite-git-admin/bc-core/pull/355) — `mcf-verifier-v2` engine bump | filter clauses now applied during fixture playback (DEC-2411e4 / D450) |
| 2 | Governed fixture append for PCIC v2 | fixture `e027b024-fd4e-4305-ab81-8641d863c0f6` |
| 3 | M10 self-verification under v2 | verifier_result `ea3a3ca4-b48d-4b04-bb9f-8231d840ba37` — `pass`, `stale_fixture_flag=false`, `bound_package_signature_hash_at_run=sha256:fc71b74f…` |
| 4 | PR [bc-core#356](https://github.com/selenite-git-admin/bc-core/pull/356) — `evidence_state_fingerprint` cache axis (DEC-2411e4 §4 amendment) | M13 cache key widened to 6 axes; cache invalidates on fixture/verifier evidence change |
| 5 | DDL 15 applied to `bc_platform_dev` | `idx_mcf_mper_mcv_check_eval_pkg_chain` dropped, `idx_mcf_mper_mcv_check_eval_pkg_chain_evidence` created with 6-axis partial unique index |
| 6 | bc-core restarted from runtime worktree `c63db8ed` | clean code path now serves all traffic |
| 7 | Publication Review re-eval (`POST /api/mcf/metric-contracts/dd2567a4-…/evaluate-pe-mc`) | cache miss (`retry_mode=false`), 12 fresh `mcf-m13-v6` PE rows, PE-MC-10 PASS via verifier_result `ea3a3ca4`, MCV `review → approved` |
| 8 | Metric Activation (`POST /api/mcf/metric-contract-versions/db3e1bd0-…/activate`) | MCV `approved → active`, cert `edfe5c90`, 12 `mcf-m14-v2` PE rows |

Substrate audit chain preserved (Invariant V): 48 PE rows total for PCIC v2 MCV — 12 v5 (NULL fp) + 12 prior v6 (NULL fp) + 12 fresh v6 (with fp) + 12 m14-v2 (with fp, cert-linked). No row deletions.

## 3. Remaining known MMS issue

- **Billing Cycle Time** stuck at the R4 Chain Delta / CC-OC Delta diagnosis from the prior runtime-recovery inventory. Not unblocked by this recovery sequence (the v2 verifier + evidence-fp fix addressed PE-MC-10's filter-evaluation gap, which was PCIC's failure mode; Billing Cycle Time's blocker is upstream chain-declaration coverage).
- Not blocking BCF waves; deferred to a separate diagnosis cycle.

## 4. Deferred cleanup

| Item | State |
|---|---|
| Dirty Layer 2 worktree `C:\MyProjects\bc-core` | Untouched; 511 working-tree status lines (Layer 2 semantic renames + intermixed Layer 2c/d artifacts). Authored on `f83ac2b7` and now diverges from `origin/main` (`c63db8ed`); reconciliation requires resolving conflicts on the evaluator service + spec files where Layer 2 renames overlap with merged PR #355/#356 changes. |
| bc-docs-v3 uncommitted artifacts | 12 modified ADRs + 16+ untracked design/plan/implementation docs (including `ADR-2411e4.md` itself, this closeout doc, and the prior session's design packets). To be committed in a focused docs batch — `status: decided` on ADR-2411e4 must not change. |
| Layer 3 compatibility-names migrations | Deferred — inventory exists (`mms-layer3-compatibility-names-inventory-2026-06-23.md`); no execution started. |
| Cluster G prompt rewrite | Deferred — plan exists (`mms-layer1-cluster-g-prompt-regression-plan-2026-06-22.md`); separate regression-test gate required before applying. |

## 5. Operational state

- **bc-core runtime**: PID 29912, `node --enable-source-maps C:\MyProjects\bc-core-runtime\dist\main`, started from worktree `C:\MyProjects\bc-core-runtime` at SHA `c63db8ed`, healthy (`/api/health` 200), uptime since 07:00 IST.
- **Dirty worktree**: `C:\MyProjects\bc-core` at `f83ac2b7 [main]` — untouched; uncommitted Layer 2 work preserved verbatim.
- **Worktrees registered**:
  ```
  C:/MyProjects/bc-core          f83ac2b7 [main]              ← dirty Layer 2, untouched
  C:/MyProjects/bc-core-runtime  c63db8ed (detached HEAD)     ← bc-core (PID 29912) serves from here
  ```
- **DDL state**: `mcf.idx_mcf_mper_mcv_check_eval_pkg_chain_evidence` present in `bc_platform_dev`; rollback file available at `docker/redesign/15R-mcf-m13-pe-mc-evidence-fingerprint-index-rollback.sql`.

## 6. Recommendation

- **Resume BCF waves next.** The runtime substrate (verifier engine + cache key + DDL + cert) is now consistent and tested end-to-end via PCIC v2 activation. BCF wave work has no semantic dependency on the deferred Layer 2 reconciliation.
- **Do not mix BCF wave work with dirty Layer 2 reconciliation.** Layer 2 has its own conflict-resolution surface against PR #355/#356 hunks; bundling it with BCF would conflate two unrelated review/merge surfaces and amplify risk. Reconcile Layer 2 in a focused future batch (after BCF waves settle or in parallel under a separate worktree).
