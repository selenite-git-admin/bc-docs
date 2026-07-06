---
uid: DEC-d7e7a0
title: "Platform date_dim + per-entity tenant fiscal calendar + FiscalCalendarService"
description: "Authoritative tenant fiscal calendar stack: platform date_dim + per-entity tenant.fiscal_calendar_config + optional fiscal_period_boundary + FiscalCalendarService resolver. Replicates SAP fiscal_year_variant mental model — tenant-aware, per-legal-entity, variant-capable."
status: implemented
subdomain: fiscal-calendar
focus: stack-architecture
date: 2026-04-20T12:09:45.103Z
project: bc-core
domain: tenants
migrated_from: legacy v2 archive
---

# Platform date_dim + per-entity tenant fiscal calendar + FiscalCalendarService

## Context

Platform needs one authoritative, tenant-aware fiscal calendar stack. Per-entity scope handles multi-country groups. Regular variant stays cheap; 4-4-5 and custom are fully expressive. Source-system or engine-derived approaches both rejected.

## Problem

The platform has no authoritative fiscal calendar. Metric evaluation today either:

- Reads a "fiscal_period" field from the source payload that's actually a posting date (root cause of D363).
- Derives a period by truncating `CO.evaluatedAt` to YYYY-MM — ignores tenant calendar semantics (India FY Apr–Mar vs US FY Jan–Dec), ignores per-entity variation (multi-country groups), ignores 4-4-5 retail calendars.

Neither is correct. Fiscal period is a **tenant-level configuration**, not an engine-derived value and not a source-owned value.

## Decision

Three tables + one service. All designed so `FiscalCalendarService.resolve(tenantId, legal_entity_code, date) → {fiscal_year, period_number, period_label, period_start, period_end}` is the only path to a fiscal period anywhere in the platform.

### `platform.date_dim`

Platform-wide authoritative date dimension (PBI-style). Seeded once covering 2000-01-01 through 2100-12-31 (~36,525 rows). Immutable reference data. Schema:

```
date               DATE PRIMARY KEY
iso_year           INT  NOT NULL
iso_month          INT  NOT NULL
iso_quarter        INT  NOT NULL
iso_week           INT  NOT NULL    -- ISO 8601 week
iso_weekday        INT  NOT NULL    -- 1=Mon … 7=Sun
year_month_str     TEXT NOT NULL    -- '2025-04'
year_quarter_str   TEXT NOT NULL    -- '2025-Q2'
year_week_str      TEXT NOT NULL    -- '2025-W17'
day_of_year        INT  NOT NULL
```

Tenant-agnostic. Every tenant resolves against the same rows — zero drift risk. Extendable later with `is_weekend`, `iso_holiday_code`, etc. when needed.

### `tenant.fiscal_calendar_config`

One row per (tenant × legal entity × effective range). Primary driver of fiscal period semantics for a given tenant/entity.

```
tenant_id               UUID  NOT NULL
legal_entity_code       TEXT  NOT NULL     -- maps to company_code in SAP-like systems; '*' = tenant default
variant_code            TEXT  NOT NULL     -- 'regular' | '4-4-5' | '4-5-4' | '5-4-4' | 'custom'
fiscal_year_start_month INT   NOT NULL     -- 1-12; India=4, US=1, UK=4, Japan=4
fiscal_year_start_day   INT   DEFAULT 1    -- usually 1; some retail calendars use a specific weekday
naming_scheme           TEXT  NOT NULL     -- 'calendar' (FY2025) | 'split' (FY2025-26)
period_count            INT   NOT NULL     -- 12 (monthly), 4 (quarterly), 13 (52-week), 52 (weekly)
period_label_pattern    TEXT  NOT NULL     -- e.g. 'FY{fy}/P{pp:02}' → 'FY2025-26/P01'
effective_from          DATE  NOT NULL
effective_to            DATE               -- NULL = currently active
primary key (tenant_id, legal_entity_code, effective_from)
```

Effective-dating means tenants can change fiscal year variants (regulatory shift, restructure) without losing historical semantics.

Per-entity scope is critical for group consolidation: a US parent with India + Japan subsidiaries has three different fiscal calendars active simultaneously.

`legal_entity_code = '*'` acts as the tenant default when a specific entity has no row.

### `tenant.fiscal_period_boundary`

Populated only for `variant_code IN ('4-4-5', '4-5-4', '5-4-4', 'custom')`. For `'regular'`, periods are computed from config without row-level storage.

```
tenant_id           UUID  NOT NULL
legal_entity_code   TEXT  NOT NULL
fiscal_year         INT   NOT NULL
period_number       INT   NOT NULL      -- 1..period_count
period_start_date   DATE  NOT NULL
period_end_date     DATE  NOT NULL
period_label        TEXT  NOT NULL
primary key (tenant_id, legal_entity_code, fiscal_year, period_number)
```

Retail 4-4-5 and custom calendars need explicit boundary storage because the period endpoints aren't derivable from a simple `start_month + month offset` computation.

### `FiscalCalendarService`

Tenant-scoped NestJS service injected from the tenant data plane. Cached per (tenant, entity, fiscal_year) — a tenant's calendar changes rarely.

```
resolve(tenantId, legalEntityCode, date)
  → { fiscal_year, period_number, period_label, period_start, period_end }

currentPeriod(tenantId, legalEntityCode, asOf = now)
  → same shape

listPeriods(tenantId, legalEntityCode, from, to)
  → period[]   // used by reports / scheduler's "run for each period in range"
```

Resolution algorithm:

1. Look up the active `fiscal_calendar_config` row for `(tenant, entity, date)` — effective-dated.
2. If no entity-specific row, fall back to `legal_entity_code = '*'` (tenant default).
3. If `variant_code = 'regular'`: compute period from `date` + `fiscal_year_start_month` arithmetic.
4. Else: look up in `fiscal_period_boundary`.
5. Format `period_label` via `period_label_pattern`.

Error on no config: explicit failure with a clear message telling the operator to complete tenant onboarding. Never silently guess.

## Scope

**IN:**
- DDL for the three tables.
- Seed script for `platform.date_dim` (range 2000-01-01 → 2100-12-31).
- `FiscalCalendarService` implementation (regular + boundary-table branches).
- Unit tests: regular variant computation, boundary-table variant lookup, effective-dating, entity fallback, missing-config error.
- Onboarding UI stub: Organization page captures fiscal_year_start_month + naming_scheme + period_count + variant.

**OUT (separate ADRs):**
- Canonical-resolution payload enrichment with fiscal_period — D365.
- Scheduler integration — scheduler remains a dumb cron; calendar service is called by consumers (canonical resolution, reports, UI), not by the scheduler.
- Calendar-exception handling (non-working days, fiscal adjustments, period-end accruals) — future, out of scope for v1.

## Consequences

- Group-consolidation tenants work natively because each legal entity has its own calendar.
- Regular variant (99% of tenants) costs zero row-level storage.
- Retail / custom variants are fully expressive via boundary rows.
- Same posting date → same fiscal period across runs (idempotent).
- `source: evaluation_period` in grain no longer the default fiscal path — narrows to forecast/target and as-of metrics.

## Alternatives considered

- **Tenant-scoped date_dim:** would duplicate 36k rows per tenant. Zero benefit. Rejected.
- **Compute from config only, no boundary table:** blocks 4-4-5 and custom variants, which several existing retail customers need. Rejected.
- **Source-system fiscal_period:** would tie our fiscal semantics to SAP's fiscal_year_variant and break for non-SAP sources. Rejected.
- **Engine-computed (my prior `deriveEvaluationPeriod`):** truncates CO.evaluatedAt to YYYY-MM. Wrong for the reasons above. Already reverted from PR #3.

## References

- Surfaced by user during SES-2ea1f7 course-correction of D363 PR #3.
- Replicates SAP's fiscal_year_variant (`T009` table) + company_code binding (`T001.PERIV`).
- Aligns with Power BI / Analysis Services `Date` dimension patterns.
- D365 layers posting_date enrichment on top.
