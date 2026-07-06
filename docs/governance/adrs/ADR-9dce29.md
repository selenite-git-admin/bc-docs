---
uid: DEC-9dce29
title: "Metric Specification Framework — 5-Dimensional Classification"
description: "5-dimensional metric classification: Purpose, Shape, Temporality, Precision, Impact — replaces weak categoryCode/typeCode"
status: implemented
subdomain: metric-architecture
focus: 5d-classification
date: 2026-04-04T17:28:41.598Z
project: bc-core
domain: metrics
supersedes: DEC-1e9fd1
foundation_doc: FND-msf001
migrated_from: legacy v2 archive
---

# Metric Specification Framework — 5-Dimensional Classification

## Context

The 1,241 finance metrics revealed that a flat category list cannot capture metric nature. Metrics differ in purpose (why), shape (what output), temporality (when valid), precision (trust level), and impact (business lever). Without this framework, metrics are a list of KPIs. With it, they become a data schema that tells the data team how to build and the business team how to consume.

This structure creates a **Metric Store** — a headless BI layer where every metric is programmatically filterable, routable, and renderable based on its 5D classification.

## Decision

Every metric in BareCount must be classified across 5 orthogonal dimensions. This replaces the weak categoryCode/typeCode fields with a rigorous specification that governs computation, storage, visualization, and alerting.

## The 5 Dimensions

### 1. Purpose — why does this metric exist?

| Code | Question | Example |
|---|---|---|
| `performance` | How are we doing? The scorecard. | EBITDA, Gross Margin, DPO |
| `efficiency` | How well are we using resources? | Cost per Invoice, Revenue per Employee |
| `operational` | What is happening right now? | Invoice Cycle Time, Invoices Processed |
| `predictive` | What will happen next? | Predicted DSO, Revenue Forecast |
| `diagnostic` | Why did it happen? | AR Aging, Error Rate Breakdown, Hold Reasons |
| `reference` | External authoritative value. | Credit Rating, SOFR, CPI, Sensex |

### 2. Shape — what does the output look like?

| Code | Description | Requires | Display |
|---|---|---|---|
| `scalar` | Single number | — | Big number tile with delta |
| `distribution` | Bucketed breakdown | `bucket_config` JSONB | Histogram / stacked bar |
| `time_series` | Value over time windows | `granularity` (daily/weekly/monthly) | Line / area chart |
| `ratio_pair` | Two values forming a ratio | — | Donut / comparison gauge |

### 3. Temporality — when is it valid?

| Code | Description | Best for | Requires |
|---|---|---|---|
| `point_in_time` | Snapshot at a moment | Balance sheet items (AP balance, inventory) | — |
| `period` | Aggregated over a window | Income statement items (revenue, expenses) | — |
| `rolling` | Moving window | Trend smoothing (90-day DSO, 30-day average) | `window_days` INTEGER |
| `cumulative` | Year/quarter/month-to-date | Progress vs annual goal | `reset_boundary` (ytd/qtd/mtd) |

**Warning:** Temporality is the most common source of data debt. If one department looks at Period (MTD) and another at Rolling (Last 30 Days), their numbers will never match.

### 4. Precision — how much to trust it?

| Code | Speed | Accuracy | Use |
|---|---|---|---|
| `flash` | High | Lower | Operational dashboards, real-time monitoring |
| `final` | Low | 100% | Board reporting, audited financials, regulatory submissions |

### 5. Impact — what business lever does it move?

| Code | What moves | Routes to | Example |
|---|---|---|---|
| `financial` | Money in/out | CFO | Revenue, EBITDA, Cost per Invoice |
| `time` | Speed/duration | Operations | DSO, Cycle Time, Close Days |
| `quality` | Accuracy/correctness | Process owner | Error Rate, First-Time Match Rate |
| `volume` | Throughput/quantity | Capacity planning | Invoices Processed, Transaction Count |
| `risk` | Exposure/probability | Risk committee | Concentration Risk, VaR |
| `compliance` | Regulatory adherence | Legal/audit | Filing Timeliness, SOX Compliance |
| `satisfaction` | Stakeholder sentiment | Relationship owner | Vendor Satisfaction, NPS |

## 5D Metric Definition Matrix

Every metric checks a box in each dimension:

| Metric | Purpose | Shape | Temporality | Precision | Impact |
|---|---|---|---|---|---|
| DSO (90-day) | efficiency | scalar | rolling | final | financial |
| System Uptime | operational | time_series | period | flash | quality |
| Project Backlog | diagnostic | distribution | point_in_time | flash | volume |
| Regulatory Gap | reference | scalar | point_in_time | final | compliance |
| Revenue Growth | performance | scalar | period | final | financial |
| AR Aging | diagnostic | distribution | point_in_time | final | risk |
| Predicted Cash Flow | predictive | time_series | rolling | flash | financial |
| Vendor Satisfaction | operational | scalar | period | final | satisfaction |

## Operational Patterns (derived from 5D codes)

### 1. Trust Filter (Precision x Impact)

High-impact metrics (financial, compliance) must be paired with `final` precision. If a `flash` + `financial` metric is displayed, the system renders a **"Preliminary"** watermark. This is a rendering rule, not stored per-metric.

| Impact | flash | final |
|---|---|---|
| financial | Watermark | Clean |
| compliance | Blocked | Clean |
| risk | Watermark | Clean |
| operational | Clean | Clean |

### 2. Visualization Engine (Shape x Purpose)

Dashboard layout auto-generated from codes:

| Shape + Purpose | Rendering |
|---|---|
| scalar + performance | Large KPI tile with delta arrow |
| distribution + diagnostic | Heatmap or treemap |
| time_series + predictive | Line chart with shaded confidence interval |
| ratio_pair + efficiency | Donut chart with comparison gauge |
| scalar + operational | Sparkline with real-time value |

### 3. Alerting Logic (Temporality x Purpose)

| Temporality + Purpose | Alert behavior |
|---|---|
| point_in_time + operational | Real-time threshold alert ("server is down now") |
| rolling + efficiency | Trend alert ("resource utilization sliding for 3 weeks") |
| period + performance | Period-end variance alert ("Q1 revenue missed target") |
| cumulative + performance | Progress alert ("YTD spend at 80% with 2 months remaining") |

## Known Collisions to Watch

1. **Diagnostic + Scalar**: Almost impossible to diagnose with a single number. Flag as "consider upgrading to Distribution shape" during metric definition.
2. **Volume vs Performance trap**: Volume (units produced) is not Performance (margin achieved). Separating them reveals if you hit volume targets but failed quality or efficiency.
3. **Reference + Flash**: Reference data from external authorities is always `final` by definition. Reject `flash` + `reference` combinations.

## Schema Changes

Add 5 columns to `metric_definition`:

```sql
ALTER TABLE metric.metric_definition
  ADD COLUMN purpose_code TEXT NOT NULL DEFAULT 'performance',
  ADD COLUMN shape_code TEXT NOT NULL DEFAULT 'scalar',
  ADD COLUMN temporality_code TEXT NOT NULL DEFAULT 'period',
  ADD COLUMN precision_code TEXT NOT NULL DEFAULT 'final',
  ADD COLUMN impact_code TEXT NOT NULL DEFAULT 'financial';
```

Shape-specific parameter columns:

```sql
ALTER TABLE metric.metric_definition
  ADD COLUMN bucket_config JSONB,          -- distribution shape: bucket definitions
  ADD COLUMN window_days INTEGER,          -- rolling temporality: e.g. 90
  ADD COLUMN reset_boundary TEXT,          -- cumulative: ytd|qtd|mtd
  ADD COLUMN granularity TEXT;             -- time_series: daily|weekly|monthly|quarterly
```

## What This Replaces

| Old field | Disposition |
|---|---|
| `categoryCode` (cost/quality/time/growth) | **Replaced** by `impact_code` |
| `typeCode` (measure/ratio/variance) | **Replaced** by `shape_code` |
| `compositionCode` (primary/derived/composite) | **Stays** — orthogonal, describes computation method |
| `directionCode` (higher/lower/target) | **Stays** — orthogonal, describes interpretation |

## Supersedes

- **D280** (DEC-1e9fd1): Observed Indicators. The `reference` purpose code replaces the proposed `observed` compositionCode.

## Framework Audit

The 5D matrix reveals catalog gaps:

- Too many Performance/Scalars? You have a scorecard but no engine room.
- Missing Predictive/Distributions? You know you're losing money but not which segments will leave next.
- Everything Point-in-Time? You see snapshots but miss the trend story.
- No Diagnostic metrics? You know what happened but never why.
