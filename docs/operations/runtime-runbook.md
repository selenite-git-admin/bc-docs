---
title: "Runtime Runbook"
description: "Operator procedures for the runtime spine: services, nightly cycle, campaigns, chain status, value audit, tickets, webhooks, SDG datasets, backup and recovery."
authority: authoritative
domain: operations
status: active
date: 2026-07-03
refs:
  - type: decision
    label: "DEC-9c0da7 (D481) — Runtime Doctrine (authority)"
  - type: doc
    label: "runtime-operations.md — operating doctrine + Retirement Register"
---

# Runtime Runbook

Operator procedures for the runtime spine built under DEC-9c0da7 (D481), gates R0–R8. Doctrine (what the pieces mean) lives in `runtime-operations.md`; this chapter is *how to run it*.

All `/api/t/*` calls need `Authorization: Bearer <admin JWT>` + `x-tenant-id: <slug>`. Platform calls need only the JWT. Get a token via the DevHub MCP tool `devhub_get_cognito_token` (app: admin).

## 1. Services

| Service | Start | Port | Notes |
|---|---|---|---|
| DevHub (MCP backbone) | `cd barecount-devhub && npm run dev` | 4000 | start first, keep running |
| Postgres | `cd bc-core && docker compose up -d` | 5435 | platform + tenant DBs |
| bc-core | `cd bc-core && npm run start:dev` | 3100 | SWC watch; full restart on module change |
| bc-admin | `cd bc-admin && npm run dev` | 3010 | Vite HMR |
| SDG sap-ecc sim | `npx tsx src/simulators/sap-ecc/odata-server.ts --months 12 --seed 42` (in bc-sdg) | 6100 | deterministic; see §8 |

## 2. Nightly cycle (scheduler)

Off by default. Enable with env `BC_SCHEDULER_ENABLED=1` on bc-core; runs at 02:00 (`@Cron('0 2 * * *')`): run reconcile → scheduled admissions (`BC_SCHEDULE_ADMISSION_READERS` = comma-separated `readerId:flavorId` pairs) → nightly campaign → chain-status refresh → value audit. Scheduled admission is watermark-gated: each fetch starts after the per-entity `progression.reader_watermark` mark, so re-runs fetch only deltas.

## 3. Admission (manual)

```
POST /api/t/readers/{readerId}/execute
{ "flavorId": "...", "environment": "dev", "tenantId": "<slug>", "dryRun": false }
```
- 422 "No active admission contract binding … in environment 'production'" → pass `environment: 'dev'`.
- A completed run emits `admission_run_completed` to the outbox; watermarks advance only on success.
- Watermark state: `GET /api/t/runtime-console/watermarks` or the bc-admin Events & Webhooks page.

## 4. Evaluation campaigns

Launch (bc-admin Runtime Console page, or API):
```
POST /api/t/metric-evaluation-campaigns
{ "scopeKind": "all" | "metrics" | "subfunction", "metricContractUids": [...], "subfunctionCode": "accounts_payable",
  "periodStartDate": "2026-05-01", "periodEndDate": "2026-05-31", "legalEntityCode": "*",
  "defaultReaderId": "<uuid>", "readerIdBySubfunction": { "accounts_payable": "<uuid>" },
  "triggerModeCode": "manual" | "test", "environmentCode": "dev" }
```
- `mode:test` is a chained dry-run: computes and reports, persists **nothing** (no snapshots, no evidence, no watermark movement). Composites and filter/grouping metrics honest-refuse as `unsupported` in test mode (v1 limitation) — they evaluate normally in `manual` mode.
- DAG-ordered (base before composite), deferred inputs retried in-campaign (attempt 2), idempotent per (campaign, metric, period), resumable.
- Status: `GET /api/t/metric-evaluation-campaigns/{campaignId}` (campaign + per-run outcomes) or `GET /api/t/runtime-console/campaigns`.
- Re-evaluation never rewrites history: newer accepted evaluations supersede **on read**.

Measured runtime envelopes are preserved in [Runtime Retirement Register Evidence](../evidence/ledgers/operations/runtime-retirement-register.md). This runbook carries the invocation and recovery procedure; fresh measurements belong in the evidence ledger, not in the runbook body.

## 5. Chain status

- Summary: `GET /api/registry/mcf/chain-status/summary` → verdict counts (green/amber/red).
- Detail: `GET /api/registry/mcf/chain-status?verdict=red` → per-MCV checks (bindings_resolve, grain_cc_active, pe_current, self_verification).
- Recompute (explicit act): `POST /api/registry/mcf/chain-status/refresh`.
- UI: bc-admin → Metric Readiness. DevHub: `devhub_chain_status` (refresh: true to recompute).
- `amber: pe_current` = publication-eligibility drift vs the current evaluator — diagnostic only; publication history is never re-adjudicated. **Red blocks DevHub session close** (override requires ≥40-char rationale and spawns a follow-up task).

## 6. Value audit

- Declared relations (platform): `GET/POST /api/registry/mcf/audit-relations` (sum_equals, sum_equals_constant, ratio_of; relations reference metric CONTRACTS, so they survive re-mints).
- Run for a period (explicit act): `POST /api/t/metric-value-audit/run?period=FY2026-27%2FP02`.
- Verdicts: `GET /api/t/runtime-console/audit-verdicts?period=...` or the bc-admin Value Audit page.
- A FAIL raises a boundary ticket via the event spine. `insufficient_data` is honest — never coerced; investigate missing snapshots before rerunning.

## 7. Tickets, events, webhooks

- Tickets: bc-admin Tickets page or `GET /api/support/tickets`. Governed-engine failures/deferrals auto-raise tickets (R2 router). Triage: resolve the cause, then PATCH the ticket; do not bulk-close without an archive (see the R5 sweep pattern).
- Event outbox: `GET /api/t/runtime-console/events?eventType=metric_run_completed`. `consumerAcksJson` shows which consumers processed each event.
- Webhook endpoints (platform registry): `GET/POST/DELETE /api/admin/webhook-endpoints` — HMAC-signed via `secretRef` (an ENV VAR NAME, never a raw secret). Deliveries + dead letters: `GET /api/t/runtime-console/webhook-deliveries`. A `dead_letter` row means 3 attempts failed — fix the receiver, then re-emit by re-running the producing act.

## 7b. WORM evidence archive

Every evidence object is also archived to `s3://barecount-evidence-worm-dev/evidence/{tenant}/{type}/{evidenceId}.json` (Object Lock, COMPLIANCE-mode 30-day default retention — objects are undeletable until retention expires, verified by a denied delete). Env-gated on bc-core: `BC_EVIDENCE_S3_BUCKET` (unset = off) + `BC_EVIDENCE_AWS_PROFILE` (pins SDK creds on dev machines where a machine-level AWS_PROFILE points at another account; unset in production — instance roles). The RDS rows remain authoritative; the S3 copy carries contentHash/prevContentHash so the chain verifies independently. Archive failures warn-log and never block a boundary act.

## 8. SDG datasets (dev source)

- Current dataset: `GET http://localhost:6100/admin/dataset` (datasetId = `sap-ecc-s{seed}-m{months}-v{version}`, per-table coverage + posting-date ranges). History: `/admin/datasets`.
- Regenerate (explicit act): `POST http://localhost:6100/admin/regenerate {"seed":42,"months":12}`.
- **Regenerating a sim that live readers point at changes source reality.** Admitted history is immutable (fine), but subsequent delta fetches will diverge. For load/what-if datasets, start a second instance: `--port 6198 --months 48` — never regen the instance bound to pilot1 mid-cycle.

## 9. Backup and recovery (local dev)

Backup both DBs (run from bc-core, uses `.env` creds):
```
docker exec -t $(docker ps -qf name=postgres) pg_dump -U barecount -d bc_platform_dev -Fc > backup/bc_platform_dev_$(date +%Y%m%d).dump
docker exec -t $(docker ps -qf name=postgres) pg_dump -U barecount -d tbc_pilot1_dev -Fc > backup/tbc_pilot1_dev_$(date +%Y%m%d).dump
```
Restore with `pg_restore -d <db> <dump>`. Production backup/DR (RDS snapshots, PITR) is an R8 operator item — see the decision list in the program report.

## 9b. Admission load test (harness + evidence pointer)

Admission load-test measurements, including the retired per-row path and the DEC-4472ca batch-write path, are preserved in [Runtime Retirement Register Evidence](../evidence/ledgers/operations/runtime-retirement-register.md). Rerun recipe: use the isolated load-test tenant and load-test reader, regenerate datasets via the simulator volume knobs, compare typed payloads against the simulator source, and record fresh measurements in the evidence ledger.

Crash recovery (sessions): `devhub_session_boot` surfaces orphans → read plan + checkpoints → resume or close. Runtime recovery: stale `running` rows are finalized `abandoned` by the run reconciler (nightly step 1); campaigns are resumable by relaunching with the same scope/periods (idempotent per metric×period).

## 10. Known limitations (v1)

- Dry-run refuses composites and filter/grouping metrics (`unsupported`) — real campaigns evaluate them.
- Cross-entity runtime read (CB-008 credit-limit family) still deferred.
- The legacy metric-readiness funnel (DataReadinessPage) is frozen-broken pending TSK-937981.
- Rate limiting is not implemented in bc-core — production ingress must front it (ALB/WAF or an approved throttler dependency).
