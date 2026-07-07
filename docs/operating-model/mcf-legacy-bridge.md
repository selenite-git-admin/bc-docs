---
uid: mcf-legacy-bridge
title: MCF Legacy Bridge — Read-Fallback Policy + Sunset Semantics
description: Operating-model chapter introduced by MCF M12.5 PR-2 (per DBCP §12.2). Locks the canonical read-fallback policy between MCF authority (new MCF-authored metric contracts in `mcf.metric_contract` / `mcf.metric_contract_version`) and legacy metric corpus (`metric.metric_definition`) during the dual-authority transition window. The Sunset HTTP header on legacy `POST /api/metric-catalog/definitions` signals the deprecation date of legacy write paths but does not by itself block them. New read services authored after M12.5 closeout MUST implement the MCF-first lookup with legacy fallback; existing read services may continue to read legacy-only until their respective migration gates (M18+). M12.5 does not change `boundary/metric.service.ts`, `ReadinessLedgerService`, or `chain-status.service.ts`; tenant runtime MCF awareness ships M18+.
status: retired
date: 2026-05-28
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-legacy-bridge
---

# MCF Legacy Bridge — Read-Fallback Policy + Sunset Semantics

> **RETIRED 2026-07-03 (D481 register item 5, operator decision: "Legacy is not in use. If it is — it is wrong.").**
> The M17 transition executed early with the legacy corpus at 0 rows
> (`metric.metric_definition` empty): the legacy write endpoints return
> **HTTP 410 Gone** (bc-core PR #396) and the Sunset-header machinery is
> removed. No live read service ever implemented the dual-authority
> fallback — /beyond was built MCF-native (DEC-a1290e) — so the policy
> below is historical record of a transition window that closed without
> ever being exercised.

## Authority

- ADR: `bc-docs/docs/adrs/ADR-c3e57f.md` (DEC-c3e57f / D422)
- DBCP: `bc-docs/docs/implementation/metric-context-framework-m12-5-materialization-legacy-bridge-dbcp.md` (`52fb8bc`) §12.2 + §12.3

## Context

MCF M12.5 (materialization gate) closes the gap between "M12 panel approved a proposal" and "MCF authority now holds the metric contract." MCs authored via the MCF pipeline (M11 intake → M12 panel → M12.5 materialization) live in `mcf.metric_contract` / `mcf.metric_contract_version`. Legacy MCs authored via `POST /api/metric-catalog/definitions` continue to live in `metric.metric_definition`.

During the transition window, BOTH authorities can hold a metric for the same `metric_code`. Read services need a deterministic rule for which authority wins. This chapter locks that rule.

## Read-fallback policy (effective from M12.5 closeout)

1. When a read consumer asks for "MC by `metric_code` X", the canonical resolution order is:

   - **MCF authority** — `SELECT mc.metric_contract_uid FROM mcf.metric_contract mc WHERE mc.mc_name = ${metric_code}` AND there exists an `mcf.metric_contract_version mcv` row with `mcv.metric_contract_uid = mc.metric_contract_uid` AND `mcv.governance_state_code IN ('draft','review','approved','active')` (i.e. not `superseded`).
   - **Legacy fallback** — `SELECT md.metric_definition_id FROM metric.metric_definition md WHERE md.metric_name = ${metric_code}` only if MCF returned no rows.

2. If both authorities return a row for the same `metric_code`, **MCF wins**. Readers SHOULD log a `legacy_mc_shadowed_by_mcf` warning event for operator awareness; readers MUST return the MCF row.

3. New read services authored after M12.5 closeout MUST implement this fallback. Existing read services may continue to read legacy-only until their respective migration gates (M18+).

4. The `Sunset` header on `POST /api/metric-catalog/definitions` signals the legacy write path's deprecation date; the read-fallback policy stays in effect until ALL read services have migrated (no fixed date — driven by tenant runtime migration in M18+).

## Sunset HTTP header semantics

Per RFC 9745 (`Sunset` HTTP header):

- The legacy write endpoints (`POST /api/metric-catalog/definitions` + `POST /api/metric-catalog/definitions/upload`) return a `Sunset` header indicating the date at which the endpoint is scheduled for retirement.
- The header value is operator-procured via the env var `BCCORE_MCF_LEGACY_SUNSET_DATE` (e.g. `Wed, 31 Dec 2026 23:59:59 GMT`).
- If the env var is unset, the `Sunset` header is OMITTED (failsafe — better to omit than to ship a hardcoded date the operator hasn't agreed to).
- The header is advisory only. Legacy write endpoints continue to function normally — they do NOT return HTTP 410 in M12.5. The HTTP 410 transition is M17.

## What M12.5 does NOT change

| Surface | Status during M12.5 | Owning gate (future change) |
|---|---|---|
| `POST /api/metric-catalog/definitions` returns HTTP 410 | **Not in M12.5** — endpoint still accepts writes (Sunset header is advisory) | M17 |
| bc-admin Metric Lifecycle page migration to MCF | **Not in M12.5** | M16 (read) + M17 (write) |
| `boundary/metric.service.ts` MCF-aware reads | **Not in M12.5** — continues to read legacy MC corpus | M18+ |
| `ReadinessLedgerService` MCF fan-out | **Not in M12.5** | M18+ |
| `chain-status.service.ts` MCF-aware reporting | **Not in M12.5** | M18+ |
| Legacy `metric.metric_definition` data migration | **Not in M12.5** — corpus retained indefinitely | M19+ (if ever) |
| Legacy `metric.enrichment_job` decommission | **Not in M12.5** — enrichment becomes panel-side via tool calls | M17 or independent operator program |

## Caveats during the dual-authority window

- **Two writers, two corpora.** Operators using the legacy `POST` endpoint write to `metric.metric_definition`; operators using the MCF intake-panel-materialize sequence write to `mcf.metric_contract`. The read-fallback policy is the only thing that disambiguates which authority a read service returns.
- **No automatic migration.** MCF does NOT backfill `mcf.metric_contract` from `metric.metric_definition`. Each metric must be re-authored via the MCF pipeline.
- **No automatic shadowing.** MCF does NOT prevent the legacy `POST` from accepting a name that already exists in `mcf.metric_contract`. The `legacy_mc_shadowed_by_mcf` warning event is the only signal.
- **Tenant runtime is legacy-backed.** Until M18+, tenant runtime evaluation continues against the legacy corpus regardless of MCF state.

## See also

- M12.5 DBCP §12 — bridge contract specification
- `docs/onboarding/metric-registration.md` — operator runbook (M12.5 PR-2 added the MCF authoring flow section)
- `bc-core/src/registry/metric-definition.controller.ts` — Sunset header implementation
- `bc-core/.env.example` — `BCCORE_MCF_LEGACY_SUNSET_DATE` env var documentation
