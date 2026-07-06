---
id: runtime-retirement-register
title: "Runtime Retirement Register Evidence"
status: evidence
authority: evidentiary
source: runtime-operations.md
---

# Runtime Retirement Register Evidence

> Evidence note: This ledger preserves runtime measurement, operator-decision, and retirement-register details split out of Runtime Operations during the v4 documentation cleanup. It is evidence, not operating doctrine.

## NFR envelope (decided; built across R1–R8)

- Admission: 1M rows/extraction sustained (per-run batch writes, DEC-4472ca direction). **Measured: per-row path sustained 29 rows/s (91.6 min for 153k); batch writes (PR #399, 2026-07-04) sustain 2,505 rows/s on the identical extraction — 1M ≈ 6.7 min, NFR credible. TSK-ea6719 done.**
- Full-catalog campaign (~100 metrics × 1 period): ≤ 10 min wall-clock at pilot scale. **Measured 2026-07-03 (R8): 82 MCs × 1 period = 1.5 s; × 12 periods (984 runs) = 14.4 s, 0 failed/deferred — ~400× headroom.**
- Period close → read-ready: ≤ 1 h from last source admission.
- Evidence: per-run rows in RDS + detail on S3 WORM (DEC-20eefe / DEC-14592e); superseded snapshot data archives to S3, never bare-deleted.

## R8 operator decisions (2026-07-03)

Recorded verbatim from the post-program decision round:

| Item | Decision |
|---|---|
| S3 WORM evidence archive | **Approved — do next session** (Object-Lock bucket + bc-core writer hook; unblocks register item 11) |
| Edge rate limiting | ALB/WAF rules at deployment time; no in-app throttler dependency |
| Backup/DR | Manual pg_dump for dev (runbook §9); RDS snapshots + PITR + restore drill when the AWS environment is set up |
| Staging | Deferred until first external tenant commitment |
| 1M-row admission load test | **Approved — run now** (scratch sim + isolated load-test tenant) |
| :4200 full-scale SDG subsystem | **Delete now** (completes register item 19) |
| D231 quality backlog (3 plans) | Keep as standing backlog; pull opportunistically |
| Period read-readiness + DataReadinessPage (TSK-937981) | Next session |
| Legacy metric-catalog bridge | **Remove now** — operator: "Legacy is not in use. If it is — it is wrong." (register item 5) |

## Retirement Register

Retirement discipline (five steps per component, in order): **decide** (ADR names the successor; half-executed decisions are completed or formally reversed) → **freeze** (bc-qa guard rule ships in the same change) → **verify zero consumers** → **physically remove, with every referencing document updated in the same change** (a removal PR without its doc sweep does not merge) → **evidence** (removal commit cites the ADR; this register updated). Structures (code, empty tables, dead schemas) are removable; data that was ever authoritative is **archive-first to S3 WORM, never bare-deleted** (Invariant III).

The freeze mechanism is live: `bc-qa/audits/checks/check-frozen-imports.sh` (blocker for bc-core) fails any commit-time audit where a file outside the recorded consumer baseline imports a frozen module. Baselines live in `bc-qa/gates/frozen-registry.json`; shrinking a baseline is always allowed, growing one requires amending this register first.

| # | Component | State | Path | Owning gate | Status |
|---|---|---|---|---|---|
| 1 | OrchestratorService legacy chaining tail (legacy resolution + metric evaluation inside reader runs) | tail removed from orchestrator + reader-runtime; observation/admission body kept | done | R2 → R5 | **retired 2026-07-03** |
| 2 | canonical-resolution.service (canonical_mapping resolver) | superseded by DEC-acce2b; orchestrator/reader-runtime consumers removed; file + module wiring staged | frozen-imports guard live (bc-qa, blocker); remove file with test-bench rework | R5 → staged | frozen+guarded |
| 3 | metric.service / evaluation.service legacy evaluation paths | ticket hooks ported (R2); orchestrator consumer removed; files + envelope-backed repos staged | frozen-imports guard live; remove with test-bench rework | R5 → staged | frozen+guarded |
| 4 | IntegrityService | deprecated; 2 remaining uses (activation gates, per-MC views) | frozen-imports guard live; R6 repoints readiness UI, then remove | R3 → R6 | frozen+guarded |
| 5 | Legacy metric-catalog POST + Sunset bridge + MCF-wins read fallback | write endpoints 410 Gone (PR #396); Sunset machinery removed; no live read fallback existed (/beyond MCF-native); legacy corpus was 0 rows | done — M17 executed early per operator decision | R8 | **retired 2026-07-03** |
| 6 | ecosystem.config.cjs (pm2 residue) | deleted; CLAUDE.md Legacy-reference section removed in same change | done | R5 | **retired 2026-07-03** |
| 7 | envelope schema (13 tables, 0 rows) | DROPPED on tbc_pilot1_dev (all 13 tables verified 0 rows first); DDL SSOT section replaced with retirement marker; migration dec-9c0da7-retire-envelope-schema.sql | done — completes DEC-95687d M4.4 | R5 | **retired 2026-07-03** |
| 8 | contract.chain_status + contract.l_node_semantic_verdict (0 rows) | dead governance targets | DROPPED (dec-9c0da7-mcv-chain-status.sql); replaced by mcf.mcv_chain_status | R3 | **retired 2026-07-03** |
| 9 | contract.metric_contract legacy family | empty; historical-only per D422; frozen code (#3) still references it | drop rides with #2/#3 file removal — dropping tables under still-present code would turn frozen paths into 500s without the guard trail | R5 → staged | staged |
| 10 | fact.ms_ar_balance_v1 (stray pre-semver, 0 rows, pilot1) | DROPPED (same migration as #7) | done | R5 | **retired 2026-07-03** |
| 11 | Per-row evidence rows + fact-table evidence_hash columns | pre-D212 shape; DATA — archive-first requires S3 WORM | UNBLOCKED 2026-07-04: WORM bucket + archiver live (bc-core PR #397); task chain TSK-a2bd6a → d6ff3b → ccc806 can proceed archive-first | R5 → ready | staged (unblocked) |
| 12 | envelope.metric_run vs progression.metric_run duplication | fell with #7 | done | R5 | **retired 2026-07-03** |
| 13 | support.ticket noise backlog (6,186 pre-2026-07-02 open rows) | archived to jsonl.gz (verified row-count match), then bulk-closed with sweep attribution; 19 current tickets untouched | done | R2 → R5 | **done 2026-07-03** |
| 14 | CLAUDE.md D305 chain-status + D366 L-node sections; IntegrityService note | docs instructing trust in dead artifacts | rewritten with the R3 replacement (same change) | R3 | **done 2026-07-03** |
| 15 | DevHub session-close L-node gate (calls nonexistent endpoint) | dead gate, fails open every close | REPOINTED to GET /api/registry/mcf/chain-status?verdict=red — gate live again with real substrate | R3 | **done 2026-07-03** |
| 16 | bc-admin Metric Readiness page reading chain_status | REPOINTED to GET /api/registry/mcf/chain-status (full page rewrite); dead ChainStatusService + /registry/chain-status/* controller REMOVED from bc-core and devhub_chain_status repointed in the same change; l-node MCP tools removed | done | R3/R6 | **retired 2026-07-03 (R6)** |
| 17 | Stuck-proposed ADRs (implemented or absorbed) | D370 rule-4 violations | R0 sweep: DEC-5ea578/acce2b/f4e9a0 flipped 2026-07-03; remainder tracked by adr-audit | R0 | partially done |
| 18 | Agenda-ghost DevHub plans (8 active, no tasks, some pre-MCF) | stale planning artifacts | operator triage: archive or re-link | R5 | pending |
| 19 | SDG :4200 fastify multi-landscape server vs :6100 sap-ecc sim | verify-consumers DONE (R7): :4200/:6200 serve nothing; no live runtime.connection targets them; only refs are a doc-comment default + frozen test-bench files. :6100 is the live source and now carries the R7 dataset registry (/admin/dataset, /admin/datasets, POST /admin/regenerate; deterministic datasetId = seed+months+version). The :4200 subsystem is the dormant body of stale plan PLN-3ff708 — removal reverses a strategic ambition, so it goes to operator triage with item 18 | operator decision: reverse PLN-3ff708 and remove, or revive under the registry | R7 → operator | frozen (dormant) |
| 20 | metric-readiness controller/service + bc-admin DataReadinessPage (legacy readiness funnel) | DataReadinessPage REBUILT on GET /t/period-readiness (D481 §Period close; bc-core PR #398 + bc-admin PR #25); controller TRIMMED to its two live definitions-surface consumers (chain-detail, resolve-definition); broken funnel + 8 consumer-less endpoints REMOVED; detail page deleted | remainder (trimmed controller + service + useChainDetail/ChainReadinessJourney) rides the definitions-surface MCF migration | R8 follow-up → definitions migration | **mostly retired 2026-07-04** |
