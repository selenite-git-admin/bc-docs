---
uid: DEC-f83b8a
title: "Source Specification Framework — 5-Dimensional Classification for Source Tables"
description: "5-dimensional source table classification: Volume, Velocity, Veracity, Data Pattern, Criticality — turns the source catalog into a classified structural reference"
status: implemented
subdomain: source-classification
focus: 5d-source-spec
date: 2026-04-05T07:33:04.545Z
project: bc-core
domain: sources
refs:
  - type: decision
    uid: DEC-9dce29
    label: "D282: Metric 5D Classification (symmetric counterpart)"
  - type: decision
    uid: DEC-7c4c39
    label: "Source Catalog Status Lifecycle"
  - type: decision
    uid: DEC-552ddd
    label: "Separate catalog_status and verification_status"
  - type: decision
    uid: DEC-586ccb
    label: "F06 Service Catalog — SVS 4-stage pipeline"
migrated_from: legacy v2 archive
---

# Source Specification Framework — 5-Dimensional Classification for Source Tables

## Context

The metric specification framework (D282/DEC-9dce29) proved that flat classification kills programmatic usability. The 1,241 finance metrics went from an opaque list to a filterable, routable, renderable Metric Store once every metric carried a 5D signature (Purpose, Shape, Temporality, Precision, Impact).

Source tables face the same structural problem. The source catalog holds 21,000+ tables across SAP ECC, S/4HANA On-Premise, and S/4HANA Cloud — with no semantic classification beyond `business_function` at the module level. At the table level, the only semantic flag is `object_type_code` (table/view/endpoint/dataset/sobject), which is structural, not semantic.

**What this means in practice:**

- bc-admin Source Catalog cannot filter "show me all master data tables" vs "transactional tables"
- AI verification (SVS pipeline, DEC-586ccb) has no structured dimensions to validate against — just freeform description matching
- Reader design requires knowing data volatility and volume, but this is tribal knowledge today
- The SVS pipeline calculates relevance scores at verification time but does not persist them
- Trust chain has no formal mechanism to propagate source data quality to downstream metric precision

The 3V framework from Big Data (Volume, Velocity, Veracity) provides a proven, well-understood vocabulary for data characterization. Extended with Data Pattern (what kind of data) and Business Criticality (how important), it forms a 5D classification that mirrors the metric framework symmetrically.

## Decision

Every source table (`source_object`, being renamed to `source_table` per D229) in BareCount must be classified across 5 orthogonal dimensions. All 5 columns live on the `source_object` table only — not on `source_system`, `source_field`, or any other tier.

## The 5 Dimensions

### 1. Volume — how much data does this table hold?

| Code | Row Range | Extraction Implication | Example |
|---|---|---|---|
| `small` | < 10K rows | Full extract every run | T001 (Company Codes), T077D (Customer Account Groups) |
| `medium` | 10K – 1M rows | Full or incremental, either works | KNA1 (Customers), LFA1 (Vendors) |
| `large` | 1M – 100M rows | Incremental/CDC mandatory | BKPF (Accounting Document Headers), VBAK (Sales Orders) |
| `massive` | 100M+ rows | Partitioned extraction, batch scheduling | BSEG (Accounting Line Items), CDPOS (Change Documents) |

**Why it matters:** Volume directly determines extraction strategy. A `massive` table cannot use full-extract without overloading the source system. Reader batch size, partitioning strategy, and scheduling windows all derive from this single code.

### 2. Velocity — how fast does the data change?

| Code | Change Pattern | Reader Strategy | Example |
|---|---|---|---|
| `static` | Never or rarely changes (config, codes) | Full extract on schedule (weekly/monthly) | T001 (Company Codes), TCURR config |
| `slow_change` | Changes infrequently (master data updates) | CDC or timestamp-based incremental | KNA1 (Customers), MARA (Materials) |
| `transactional` | New rows constantly, rarely updated | Append-optimized CDC, watermark-based | BKPF (Postings), VBAK (Sales Orders) |
| `streaming` | Real-time event flow | Near-real-time CDC or event subscription | CDHDR (Change Documents), IDoc logs |

**Why it matters:** Velocity determines the observation contract's temporality and the reader's scheduling strategy. A `static` table needs a simple periodic reader. A `streaming` table needs CDC or event-driven admission. Mismatching velocity with reader strategy is the most common source of stale data.

### 3. Veracity — how trustworthy is this data?

| Code | Trust Level | Downstream Impact | Example |
|---|---|---|---|
| `authoritative` | Source of truth, audit-grade | Can feed `precision: final` metrics | SAP FI postings (BKPF/BSEG), GL balances |
| `reliable` | Accurate but not audit-grade | Can feed `precision: final` with caveats | CRM opportunity amounts, HR headcount |
| `approximate` | Estimates, projections, user-entered | Caps downstream metrics at `precision: flash` | Budget forecasts, manual journal entries |
| `unverified` | Unknown quality, newly onboarded | Cannot feed metrics until verified | Any newly registered table before validation |

**Why it matters:** This is the trust chain bridge between source 5D and metric 5D. A canonical contract built on an `approximate` source table cannot produce a `precision: final` metric — the veracity ceiling propagates upward through the contract chain. This makes data quality an explicit, enforceable constraint rather than an assumption.

**Trust chain propagation rule:**

```
source.veracity → observation contract trust → canonical evaluation trust → metric.precision

authoritative  → can produce → final
reliable       → can produce → final (with audit note)
approximate    → capped at   → flash
unverified     → blocked     → no metric production
```

### 4. Data Pattern — what kind of data is this?

| Code | Description | Contract Shape Implication | Example |
|---|---|---|---|
| `master_data` | Core business entities, slowly changing dimensions | Identity + attributes, SCD Type 2 tracking | KNA1 (Customers), MARA (Materials), LFA1 (Vendors) |
| `transactional` | Business events, append-mostly | Event records with timestamps, immutable after posting | BKPF (Accounting Docs), VBAK (Sales Orders), EKKO (Purchase Orders) |
| `configuration` | System settings, customizing tables | Key-value or small lookup, rarely changes | T001 (Company Codes), T077D (Account Groups) |
| `reference` | External reference data, not owned by the source system | Read-only, version-stamped | TCURR (Exchange Rates), country codes, tax tables |
| `log` | System activity records, operational metadata | Append-only, temporal, high volume | CDHDR/CDPOS (Change Documents), SM21 (System Log) |
| `aggregate` | Pre-computed summaries or materialized views | Derived data, may have freshness lag | SAP BW queries, summary tables, reporting views |

**Why it matters:** Data pattern determines reader design and contract shape. Master data needs SCD tracking. Transactional data needs append-optimized admission. Configuration tables need simple full-extract. Mixing patterns within a single reader flavor is a design error.

### 5. Business Criticality — how important is this table to the business?

| Code | Definition | Governance Implication | Example |
|---|---|---|---|
| `critical` | Core financial/operational data, regulatory scope | AI verification mandatory, priority onboarding, tighter SLAs | BKPF (Postings), BSEG (Line Items), ACDOCA (Universal Journal) |
| `standard` | Important business data, not regulatory | Standard onboarding flow, normal governance | VBAK (Sales Orders), EKKO (Purchase Orders) |
| `auxiliary` | Supporting/reference data, nice-to-have | Deferred onboarding, lighter governance | Custom Z-tables, staging tables, temp tables |

**Why it matters:** Criticality routes attention. In a catalog of 21,000 tables, you need to know which 500 matter most. Critical tables get AI verification first, tighter monitoring, and priority in the onboarding queue. Auxiliary tables can wait.

## 5D Source Table Matrix

Every source table checks a box in each dimension:

| Table | Volume | Velocity | Veracity | Data Pattern | Criticality |
|---|---|---|---|---|---|
| BKPF (Accounting Doc Header) | `massive` | `transactional` | `authoritative` | `transactional` | `critical` |
| BSEG (Accounting Line Items) | `massive` | `transactional` | `authoritative` | `transactional` | `critical` |
| KNA1 (Customer Master) | `medium` | `slow_change` | `reliable` | `master_data` | `standard` |
| T001 (Company Codes) | `small` | `static` | `authoritative` | `configuration` | `critical` |
| TCURR (Exchange Rates) | `small` | `slow_change` | `authoritative` | `reference` | `standard` |
| CDHDR (Change Documents) | `massive` | `streaming` | `authoritative` | `log` | `auxiliary` |
| ZTMP_REPORT (Custom Z-table) | `medium` | `slow_change` | `approximate` | `aggregate` | `auxiliary` |

## Operational Patterns (derived from 5D codes)

### 1. Reader Strategy (Volume x Velocity)

| Volume \ Velocity | static | slow_change | transactional | streaming |
|---|---|---|---|---|
| small | Full extract, weekly | Full extract, daily | Full extract, hourly | Overkill — treat as transactional |
| medium | Full extract, weekly | Incremental (timestamp) | CDC (watermark) | CDC (watermark) |
| large | Full extract, monthly | CDC mandatory | CDC mandatory | CDC + partitioning |
| massive | Full extract, quarterly | CDC + partitioning | CDC + partitioning | Event-driven + partitioning |

### 2. Trust Chain Filter (Veracity → Metric Precision)

| Source Veracity | Max Metric Precision | Display Treatment |
|---|---|---|
| `authoritative` | `final` | Clean |
| `reliable` | `final` | Audit note footnote |
| `approximate` | `flash` | "Preliminary" watermark |
| `unverified` | Blocked | No metric production |

### 3. Onboarding Priority (Criticality x Veracity)

| Criticality \ Veracity | authoritative | reliable | approximate | unverified |
|---|---|---|---|---|
| `critical` | Onboard first, full governance | Onboard first, verify soon | Flag for data quality review | Block until verified |
| `standard` | Normal queue | Normal queue | Normal queue | Normal queue |
| `auxiliary` | Deferred | Deferred | Deferred | Lowest priority |

## Known Collisions to Watch

1. **Transactional + Static**: A table described as transactional but marked static means stale data is being treated as live events. Reject this combination during AI verification.
2. **Massive + Streaming**: This is the hardest combination — requires partitioned CDC with careful backpressure. Flag for architecture review during onboarding.
3. **Approximate + Critical**: High-criticality data with low veracity is a risk. AI verification should flag this as an anomaly requiring human review.
4. **Log + Critical**: System logs are almost never critical for business metrics. If marked critical, verify it's actually transactional data misclassified as log.

## Schema Changes

Add 5 columns to `source.source_object`:

```sql
ALTER TABLE source.source_object
  ADD COLUMN volume_code TEXT NOT NULL DEFAULT 'medium',
  ADD COLUMN velocity_code TEXT NOT NULL DEFAULT 'slow_change',
  ADD COLUMN veracity_code TEXT NOT NULL DEFAULT 'unverified',
  ADD COLUMN data_pattern_code TEXT NOT NULL DEFAULT 'master_data',
  ADD COLUMN criticality_code TEXT NOT NULL DEFAULT 'standard';
```

**Defaults rationale:**
- `volume: medium` — safe middle ground, doesn't trigger extreme extraction strategies
- `velocity: slow_change` — conservative, won't miss changes
- `veracity: unverified` — every table starts untrusted until AI or human classifies it
- `data_pattern: master_data` — most common pattern in enterprise systems
- `criticality: standard` — avoids both false urgency and neglect

No shape-specific parameter columns needed (unlike metric 5D). Source classification is categorical only — no per-dimension configuration payloads.

## AI Classification

Same pipeline as D282 metric classification:

1. **Classifier**: Gemini 2.5 Flash (cross-family from Bedrock Haiku/Sonnet used elsewhere)
2. **Input**: table name, description, field names, module context, system type
3. **Output**: 5 codes per table
4. **Scale**: ~4,968 registered source objects (current), expandable to 21,000+ as seed catalog imports continue
5. **Verification**: Cross-check with source system documentation and field patterns (e.g., a table with `ERDAT`/`ERZET` fields is likely transactional)

## Symmetry with Metric 5D (D282)

| Aspect | Metric 5D (D282) | Source 5D (D284) |
|---|---|---|
| Target table | `metric_definition` | `source_object` |
| Classifies | Platform output (what we produce) | Platform input (what we consume) |
| Dimensions | Purpose, Shape, Temporality, Precision, Impact | Volume, Velocity, Veracity, Data Pattern, Criticality |
| Bridge dimension | Precision (how much to trust the output) | Veracity (how much to trust the input) |
| Classification method | AI (Gemini 2.5 Flash) | AI (Gemini 2.5 Flash) |
| Scale | 1,241 metrics (finance complete) | ~4,968 registered tables |
| Drives | Visualization, alerting, trust filters | Reader design, scheduling, onboarding priority |
| Parameter columns | 4 (bucket_config, window_days, reset_boundary, granularity) | 0 (categorical only) |

## What This Does NOT Replace

| Existing field | Disposition |
|---|---|
| `object_type_code` (table/view/endpoint/dataset/sobject) | **Stays** — structural type, orthogonal to 5D semantic classification |
| `catalog_status` (registered/approved/deprecated/archived) | **Stays** — governance lifecycle, not classification |
| `verification_status` (unverified/verified/disputed/manually_verified/rejected) | **Stays** — AI verification result, not data trust level |
| `validation_status` (not_validated/validated) | **Stays** — runtime proof of data flow, not classification |
| `business_function` on `source_module` | **Stays** — coarse functional grouping at module level |

## Options Considered

### Option A: 3V only (Volume, Velocity, Veracity) — rejected

The Big Data 3V's are necessary but insufficient. They characterize the data but don't tell you what kind of data it is (transactional vs master vs config) or how important it is (critical vs auxiliary). Without Data Pattern, reader design still relies on tribal knowledge. Without Criticality, onboarding has no prioritization axis.

### Option B: 6D with Integration Complexity — rejected

Integration Complexity (`simple`/`moderate`/`complex`) was considered as a system-level dimension. Rejected because it's subjective and transient — a system is complex for the first onboarding, but once a mature reader/driver exists, subsequent tenants using the same system type are trivial. It's not an intrinsic property of the source system.

### Option C: 5D on source_object (chosen)

Volume + Velocity + Veracity + Data Pattern + Criticality. All on `source_object`. Categorical only (no parameter columns). Symmetric with metric 5D. Covers the gaps without over-engineering.

## Consequences

### Positive

- Source catalog becomes semantically searchable (filter by data pattern, criticality, etc.)
- Reader design becomes data-driven instead of tribal knowledge
- Trust chain has an explicit, enforceable mechanism (veracity → precision ceiling)
- AI verification gets structured axes to validate against
- Onboarding prioritization becomes deterministic (criticality x veracity matrix)
- bc-admin Source Catalog UI can expose meaningful filters and drill-downs
- Symmetric 5D framework across inputs and outputs creates a coherent platform vocabulary

### Negative

- 5 new columns on source_object adds schema width (but well within the 20-column rule — source_object currently has ~15 columns)
- AI classification of ~4,968 tables requires a batch run (but proven at 1,241 metrics in D282)
- Defaults must be chosen carefully — wrong defaults create a false sense of classification

### Risks

- **Stale classification**: Source tables can change character over time (a table might start as `small` and grow to `massive`). Mitigation: re-classify on major version changes or during periodic catalog review.
- **AI misclassification**: AI may struggle with ambiguous tables (e.g., SAP custom Z-tables with no documentation). Mitigation: `unverified` veracity default + human review flag for low-confidence classifications.
- **Over-reliance on classification**: 5D codes should inform decisions, not automate them blindly. Reader design should always be reviewed by a human before activation.
