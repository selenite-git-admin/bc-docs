---
uid: DEC-db1c63
title: "Metric as Data Product — KPI Output tab with consumable endpoints and AI activation metadata"
description: "Metrics get an Output tab exposing consumable API endpoints and AI activation metadata, turning KPIs from registry objects into self-documenting data products."
status: decided
subdomain: data-product
focus: metric-output-tab
date: 2026-03-16
project: bc-admin
domain: database
refs:
  - type: decision
    label: "D080"
authority: authoritative
migrated_from: legacy v2 archive
---


# Metric as Data Product — KPI Output tab with consumable endpoints and AI activation metadata

## Context

1. Metrics are immutable, addressable, versioned objects — they already behave like data products. The Output tab makes this explicit.
2. AI activation requires structured, discoverable metadata. Without it, AI agents must be hand-coded per metric. With it, any metric is programmatically consumable.
3. The same component serves both admin (platform documentation) and portal (tenant consumption), reducing duplication.
4. Positions BareCount metrics as consumable APIs, not just internal computation — aligns with the commercial model where KPIs are the core value proposition.
5. Self-documenting endpoints reduce integration support burden — BI teams can self-serve.

# D080: Metric as Data Product

## Context
KPI/Metric contracts define computation logic (CO bindings, formula, temporal gate, thresholds) but the output — the metric snapshot — has no self-documenting surface. Consumers (BI tools, data engineers, AI agents) must reverse-engineer how to consume a metric. This makes metrics registry objects rather than data products.

## Decision

### Each KPI gets an "Output" tab on its detail page
The Output tab treats the metric snapshot as a **consumable data product** — self-documenting, API-ready, AI-activatable.

### Output tab contents

| Section | Platform (bc-admin) | Tenant (bc-portal) |
|---------|--------------------|--------------------|
| **Output Schema** | Snapshot field definitions (value, unit, period, band, CO refs, evidence ref) | Same |
| **API Endpoints** | Endpoint list with `x-tenant-id` placeholder | Endpoints with tenant ID pre-filled |
| **Request Example** | Curl/fetch template — schema only | Live example, copy-pasteable |
| **Response Example** | Sample JSON from snapshot schema | Actual latest response |
| **Result Table** | — (no tenant data access) | Latest snapshots: value, period, band, delta |
| **Timeline** | — | Historical snapshot trend |
| **Consumer Guide** | Polling, webhook, freshness, temporal gate | Same + export (CSV/JSON) |
| **AI Activation Card** | Structured metadata: input COs, formula type, direction, thresholds, dependencies | Same |

### Reusable component

```
MetricOutputTab
├── props: { contractId, tenantId?, mode: 'platform' | 'tenant' }
├── OutputSchema        (shared)
├── EndpointReference   (shared — adds x-tenant-id when tenantId provided)
├── RequestResponse     (shared — live when tenant, schema-only when platform)
├── ResultTable         (tenant mode only)
├── TimelineChart       (tenant mode only)
└── AIActivationCard    (shared)
```

Single component source, imported by bc-admin with `mode='platform'` and bc-portal with `mode='tenant'`.

### AI Activation metadata structure

```json
{
  "contractId": "metric-dso-v1",
  "displayName": "Days Sales Outstanding",
  "domain": "finance",
  "subdomain": "ar",
  "direction": "lower_is_better",
  "unit": "days",
  "temporalGate": "monthly",
  "inputCOs": ["ar-open-items", "ar-cleared-items"],
  "formula": "sum(open_amount) / (sum(revenue_last_90d) / 90)",
  "thresholds": { "excellent": 30, "good": 45, "atRisk": 60, "poor": 90 },
  "endpoints": {
    "latest": "GET /api/metric-snapshots?contractId={id}&limit=1",
    "timeline": "GET /api/metric-snapshots/timeline?contractId={id}",
    "perContract": "GET /api/metric-snapshots/latest-per-contract"
  },
  "dependencies": ["metric-revenue-run-rate-v1"]
}
```

An AI agent reading this knows: what the metric measures, what data feeds it, how to call it, how to interpret the result, and what other metrics it depends on.


## Options Considered

N/A

## Implications

1. **Decouples value from dashboards** — Tenant gets value from metrics even if no charts are built. The snapshot IS the product.
2. **Subscription gating** — Pricing tiers can gate which metrics a tenant can consume (per KPI or per domain entitlement).
3. **Composability** — Secondary metrics show their dependency DAG. AI can walk upstream.
4. **API documentation** — Output tab doubles as living API docs for each metric.
5. **Portal 2.0** — The tenant-mode Output tab is a natural fit for Portal 2.0's data product UX.

## Consequences

N/A
