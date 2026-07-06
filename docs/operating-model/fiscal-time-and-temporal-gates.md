---
id: fiscal-time-and-temporal-gates
order: 15
title: "Fiscal Time and Temporal Gates"
status: drafting
authority: authoritative
depends_on: [the-contract-grammar, the-object-model, sources-and-the-catalog, admission-and-observation, canonical-evaluation, metric-evaluation, tenancy-and-binding]
governing_sources:
  - Foundation (scope and non-negotiability)
  - The Contract Grammar, Canonical Contract section
  - Canonical Evaluation
  - Metric Evaluation
  - Tenancy and Binding
governing_adrs:
  - DEC-d7e7a0 (Platform date dim plus per-entity tenant fiscal calendar plus FiscalCalendarService)
  - DEC-a8e8fc (Canonical Contract declares posting-date field; canonical resolution enriches payload)
  - DEC-1efa47 (Grain key-source mismatch; fiscal period must be a business field)
errata_referenced: []
v2_sources: []
---

# Fiscal Time and Temporal Gates

## Scope

This chapter defines fiscal time as a platform runtime concept. It defines fiscal period as a per-Canonical-Object attribute determined by a posting date resolved against the tenant's fiscal calendar per legal entity, the calendar stack that holds the resolution rules (platform date dim, tenant fiscal calendar configuration per legal entity, optional fiscal period boundary table, and the resolver service), the Canonical Contract declaration of which canonical field carries the posting date, the canonical resolution enrichment that stamps fiscal period and fiscal year onto the Canonical Object payload, the metric grain treatment under which fiscal period is consumed as a plain canonical field, the boundary that separates fiscal time from observation time and from scheduler invocation time, and the failure modes that arise when any of these elements is misaligned.

This chapter does not redefine the contract grammar (The Contract Grammar), the Canonical Object (The Object Model), the canonical evaluation act (Canonical Evaluation), the metric evaluation act (Metric Evaluation), the relational storage layout for date-dim or fiscal-calendar tables, or the tenant database structure (Tenancy and Binding). The acts at the four boundaries remain governed by their own chapters; this chapter governs the fiscal-time content those acts produce and consume.

This chapter follows DEC-d7e7a0 for the calendar stack architecture, DEC-a8e8fc for the canonical-resolution enrichment path, and DEC-1efa47 for the disambiguation of fiscal time from runtime invocation context.

**Governing source.** Foundation; The Contract Grammar; Canonical Evaluation; Metric Evaluation; Tenancy and Binding.

## Fiscal Period Definition

Fiscal period is a per-Canonical-Object attribute. The value of fiscal period for a Canonical Object is determined by the posting date carried on the Canonical Object's canonical payload, resolved against the tenant's fiscal calendar configuration for the relevant legal entity.

| Property | Rule |
|---|---|
| Granularity | Per Canonical Object. Each Canonical Object carries exactly one fiscal period, one fiscal year, and one fiscal period number, all stamped at canonical resolution time. |
| Anchor | The posting date declared by the Canonical Contract as the fiscal anchor for that Canonical Contract version. The canonical field that holds the posting date is named in the Canonical Contract body per DEC-a8e8fc. |
| Resolver input | The posting date value carried on the pre-emission Canonical Object payload, the tenant identity, and the legal entity identifier carried on the Canonical Object. |
| Resolver authority | The tenant's fiscal calendar configuration for the named legal entity, governed by the calendar stack section below. |
| Output | Three attributes stamped on the Canonical Object payload: fiscal period (the resolved period label), fiscal year (the resolved fiscal year label), and fiscal period number (the resolved integer period ordinal within the fiscal year, the resolver's `period_number`). The fiscal period number exists so that as-of, balance, and cumulative-to-date metrics can compare the stamped `(fiscal_year, period_number)` ordinal of one Canonical Object against another without re-resolving the calendar at metric evaluation (DEC-83fda0). The period ordinal is the calendar-authoritative within-year order; the period count per year is a per-calendar property (4, 12, 13, or 52 per DEC-d7e7a0), so the ordinal — not a derived month or quarter — is the portable comparison key. |

Fiscal period is determined at canonical resolution and recorded on the Canonical Object. It is not re-resolved at metric evaluation. It is not re-resolved on read. The Canonical Object carries the resolved values for the lifetime of the object.

**Governing source.** The Object Model; Canonical Evaluation; DEC-a8e8fc; DEC-1efa47.

## The Calendar Stack

The calendar stack holds the rules required to resolve a posting date to a fiscal period for a tenant and legal entity. The stack has four components governed by DEC-d7e7a0.

| Component | Scope | Purpose |
|---|---|---|
| Platform date dim | Platform | Authoritative date table seeded across the platform's supported date range. Holds calendar attributes (calendar year, calendar month, ISO week, weekday) that do not depend on tenant context. |
| Tenant fiscal calendar configuration | Tenant, per legal entity | Declares the fiscal year start, the period structure (regular, 4-4-5, or custom), and the fiscal year naming convention for a specific legal entity within the tenant. |
| Tenant fiscal period boundary | Tenant, per legal entity, optional | Holds explicit period boundary dates for non-regular structures (4-4-5 retail calendars, custom calendars with irregular period lengths). Not required for regular fiscal years. |
| FiscalCalendarService resolver | Platform service consumed by tenant runtime | Receives posting date, tenant identity, and legal entity identifier. Returns fiscal period and fiscal year. Composes the date dim, the fiscal calendar configuration, and the optional period boundary table. |

The stack is hierarchical. Platform date dim provides calendar facts. Tenant fiscal calendar configuration interprets those facts under the tenant's fiscal year semantics for one legal entity. Tenant fiscal period boundary, when present, overrides regular-variant period derivation with explicit boundaries. The FiscalCalendarService applies the hierarchy in resolver order.

A tenant may hold multiple fiscal calendar configurations, one per legal entity. Multi-country groups carry distinct fiscal year semantics per legal entity (for example, an Indian legal entity with April-to-March fiscal years and a U.S. legal entity with January-to-December fiscal years under the same tenant). The legal entity carried on the Canonical Object selects the configuration the resolver consults.

**Governing source.** DEC-d7e7a0; Tenancy and Binding; The Contract Grammar.

## Posting Date Field Declaration

Per DEC-a8e8fc, every Canonical Contract version declares which canonical field holds the posting date. The declaration is a body element of the Canonical Contract; it is not inferred from naming conventions and is not derived at runtime.

| Property | Rule |
|---|---|
| Location | A body field of the Canonical Contract version that names the canonical field holding the posting date for the Canonical Object the contract produces. |
| Cardinality | Exactly one canonical field per Canonical Contract version is named as the posting-date anchor. A contract version that does not name a posting-date field cannot participate in fiscal-time enrichment. |
| Type discipline | The named canonical field carries a date or timestamp type. Free-form text fields are not admissible as posting-date anchors. |
| Variation across versions | A Canonical Contract version that supersedes an earlier version may name a different canonical field as posting-date anchor. The supersession does not retroactively re-anchor previously emitted Canonical Objects. |

The Canonical Contract author selects the posting-date field per the business semantics of the canonical model. For accounting-derived Canonical Objects the posting date is the booking date (the SAP BUDAT-equivalent or its analog in other ERP source systems). For non-accounting Canonical Objects whose evaluation requires a fiscal anchor, the author names the field that carries the fiscal-anchor date.

A Canonical Contract version that does not declare a posting-date field produces Canonical Objects without a fiscal anchor. Metrics that require fiscal time over Canonical Objects from such a contract version cannot resolve fiscal period. Whether this is admissible depends on the metric's grain declaration; metrics that include fiscal period in their grain reject the contract version's Canonical Objects at metric evaluation precondition.

**Governing source.** The Contract Grammar; The Object Model; DEC-a8e8fc.

## Canonical Resolution Enrichment

Canonical evaluation enriches the Canonical Object payload with the resolved fiscal period and fiscal year at the moment the Canonical Object is produced. The enrichment is part of the canonical evaluation act per Canonical Evaluation; this section describes the fiscal-time content of the enrichment and its placement.

| Step | Action |
|---|---|
| 1 | The canonical evaluation act resolves the source state under the active Canonical Contract version and produces the unenriched Canonical Object payload. |
| 2 | The act reads the posting date from the canonical field named on the Canonical Contract version's posting-date declaration. |
| 3 | The act invokes FiscalCalendarService.resolve with the posting date, the tenant identity, and the legal entity identifier carried on the Canonical Object. |
| 4 | The resolver returns fiscal period, fiscal year, and fiscal period number. |
| 5 | The act stamps fiscal period, fiscal year, and fiscal period number onto the Canonical Object payload as additional canonical-field values, identical in structure to fields produced by direct canonical mapping. |
| 6 | The Canonical Object is emitted with the enrichment in place. The per-Canonical-Object Lineage records the resolver invocation as part of the canonical evaluation act's proof. |

The enrichment is not a separate act. It is part of the canonical evaluation act's runtime, performed before Canonical Object emission. A failure to resolve the posting date is a canonical evaluation failure; the partial Canonical Object is not emitted.

The enrichment runs at canonical resolution because canonical resolution is the boundary that has tenant context, has access to the calendar stack, and is the first place in the contract chain where the Canonical Contract's posting-date declaration is known. The Reader does not have business semantics and does not enrich; the metric engine receives the Canonical Object as authoritative state and does not re-resolve.

**Governing source.** Canonical Evaluation; The Object Model; DEC-a8e8fc.

## Metric Grain Treatment

Per DEC-1efa47, metric grain treats fiscal period as a plain canonical field. The metric engine does not special-case fiscal period; the metric grain declaration names the canonical field that carries fiscal period (the field stamped by canonical resolution enrichment), and the engine reads it like any other canonical field.

| Property | Rule |
|---|---|
| Grain key | The grain entry that captures fiscal period names a canonical field source. The source value is `business_field` (per the contract grammar's grain vocabulary), referencing the canonical field stamped at canonical resolution. The source is not `evaluation_period` and is not derived from runtime invocation context. |
| Engine behavior | The metric engine groups Canonical Objects by the grain canonical field's value and aggregates per group. Fiscal period is one such grain dimension when the metric declares it. |
| Mismatch detection | A grain entry that names fiscal period as its key but declares a source other than `business_field` is rejected at Metric Contract authoring as a grain key-source mismatch per DEC-1efa47. |
| Engine special-cases | None. The engine does not infer fiscal period from posting date at evaluation. The engine does not truncate evaluation timestamps to derive a period. The engine does not consult the calendar stack at evaluation. |

The engine consumes the canonical resolution enrichment. It does not perform the resolution. The separation prevents the failure mode in which the engine derives fiscal period from a date field interpreted under unknown calendar semantics.

**Governing source.** Metric Evaluation; The Contract Grammar; DEC-1efa47.

## Boundary: What Fiscal Period Is Not

The chapter's central distinction is that fiscal period is a property of the Canonical Object, determined by the posting date and the tenant calendar, and not a property of any other concept that has been confused with it.

| Concept | Relation to fiscal period |
|---|---|
| Canonical Object emission timestamp | Records when canonical evaluation produced the Canonical Object. Not a fiscal anchor. A Canonical Object produced at evaluation time may carry fiscal period values from any prior period the source posting date resolves to. |
| Source observation timestamp | Records when the Reader observed the source record. Not a fiscal anchor. The observation timestamp does not determine fiscal period. |
| Scheduler invocation time | Records when an invocation was triggered by an external scheduler. Not a fiscal anchor. Scheduler is a dumb cron mechanism for invocation timing; it does not determine fiscal period for any Canonical Object the invocation produces. |
| Source field literal named "GJAHR" or equivalent | A source-system fiscal year field. Not a substitute for resolved fiscal year. The source-system fiscal year reflects the source system's calendar, which may differ from the tenant's calendar for the same legal entity. The platform resolves fiscal year via the calendar stack, not by reading a source-system field directly into the canonical fiscal year. |
| Generic "evaluation_period" runtime context | Not a fiscal period source. Per DEC-1efa47, conflating the two led to dates being emitted as fiscal periods. The grain entry whose key is fiscal period names a canonical field source, not an evaluation context source. |

The boundary applies uniformly. A canonical evaluation that infers fiscal period from a non-posting-date source violates the discipline. A metric engine that derives fiscal period from invocation context violates the discipline. A scheduler that announces a "current period" to the runtime violates the discipline.

**Governing source.** DEC-1efa47; The Object Model; Canonical Evaluation; Metric Evaluation.

## Constraints

The constraints below apply uniformly to fiscal-time handling at canonical evaluation and metric evaluation.

| Constraint | Operational form |
|---|---|
| Fiscal period is per-Canonical-Object | Each Canonical Object carries exactly one fiscal period, one fiscal year, and one fiscal period number, stamped at canonical resolution. |
| Resolution is one-shot at canonical evaluation | The resolver is consulted once per Canonical Object at canonical evaluation. Subsequent reads consume the stamped values and do not re-resolve. |
| Posting-date field is a body element of the Canonical Contract | The declaration is governed and versioned with the Canonical Contract per The Contract Grammar. It is not a separate governed artifact. |
| Calendar configuration is per legal entity | A tenant may hold multiple fiscal calendar configurations, one per legal entity. The legal entity carried on the Canonical Object selects the configuration the resolver consults. |
| Engine does not resolve fiscal time | The metric engine consumes fiscal period as a canonical field. It does not call the resolver. It does not infer fiscal period from any other field. |
| Scheduler does not author fiscal time | Scheduler invocation is dumb cron. It does not communicate fiscal context to runtime acts. |
| Supersession does not re-anchor prior Canonical Objects | A new Canonical Contract version that names a different posting-date field applies only to Canonical Objects produced under that new version. Canonical Objects emitted under prior versions retain their stamped fiscal period and fiscal year as recorded. |

**Governing source.** Canonical Evaluation; Metric Evaluation; The Contract Grammar; DEC-d7e7a0; DEC-a8e8fc; DEC-1efa47.

## Failure Modes

Fiscal-time failures arise at the act that depends on resolved values. The act records the failure and does not produce authoritative state under unresolved or inconsistent fiscal time.

| Failure | Detection point | Treatment |
|---|---|---|
| Canonical Contract version does not declare a posting-date field, but a metric grain that consumes its Canonical Objects requires fiscal period | Metric evaluation precondition | Rejected. The metric does not evaluate over Canonical Objects from the contract version, and the metric evaluation Run records the missing posting-date declaration as the rejection reason. |
| Posting-date field's value is null or unparsable on a specific Canonical Object | Canonical evaluation enrichment | The Canonical Object is not emitted. The canonical evaluation Run records the failure with the offending field and the reason. |
| Tenant has no fiscal calendar configuration for the legal entity carried on the Canonical Object | Canonical evaluation enrichment, FiscalCalendarService resolver | The Canonical Object is not emitted. The resolver returns a missing-configuration outcome; the canonical evaluation Run records the failure. |
| Tenant's fiscal calendar configuration declares a non-regular variant but the fiscal period boundary table is missing | Canonical evaluation enrichment, FiscalCalendarService resolver | The Canonical Object is not emitted. The resolver returns a missing-boundary outcome; the canonical evaluation Run records the failure and names the legal entity. |
| Posting date falls outside the platform date dim's seeded range | Canonical evaluation enrichment, FiscalCalendarService resolver | The Canonical Object is not emitted. The resolver returns an out-of-range outcome; the canonical evaluation Run records the failure. The platform date dim range is a configuration concern of the calendar stack. |
| Metric Contract grain entry names fiscal period as key with source other than business field | Metric Contract authoring | Rejected at authoring per DEC-1efa47. The Contract is not persisted with the mismatched grain entry. |
| Engine receives a Canonical Object without stamped fiscal period and the metric grain requires it | Metric evaluation precondition | The Canonical Object is excluded from the metric's evaluation set. The metric evaluation Run records the exclusion count. |
| Source-system fiscal year field is read directly into the canonical fiscal year without calendar-stack resolution | Canonical Mapping authoring or Canonical Contract authoring | Rejected at authoring as a violation of the boundary discipline. Canonical fiscal year is produced by the resolver, not by direct mapping from a source field. |

Failures at this boundary are recorded as runtime outcomes on the canonical evaluation Run and the metric evaluation Run. They are not silently absorbed. Per the platform's general discipline, an act that cannot resolve fiscal time does not emit authoritative state under guessed or defaulted values.

**Governing source.** Canonical Evaluation; Metric Evaluation; The Contract Grammar; DEC-d7e7a0; DEC-a8e8fc; DEC-1efa47.

## Substrate Boundary — Canonical Reporting Period vs Source-Attested Posting Period Code

The fiscal-time concept partitions into three substrate layers. Confusing the layers is a meaning-drift hazard under Foundation Invariant I (meaning is evaluated once). This section establishes the naming and substrate-boundary discipline that prevents the drift, and it is the governing reference for any candidate BCF characteristic that touches a period concept.

| Layer | Concept | Provenance | Authority | Substrate location | BCF characteristic? |
|---|---|---|---|---|---|
| A | Canonical reporting period | BareCount-derived at canonical resolution by FiscalCalendarService from posting date plus tenant fiscal calendar plus legal entity | Authoritative for all reporting, grouping, and period-close metrics | Resolver-stamped on the Canonical Object payload; consumed by the metric engine via a grain entry whose source is `business_field` per DEC-1efa47 | No — owned by canonical resolution and the metric engine, not by BCF |
| B | Source-attested posting period code | A source system stamps the document with a period code at posting time (for example SAP MONAT plus GJAHR, Oracle GL_JE_HEADERS.PERIOD_NAME, NetSuite postingPeriod, QuickBooks ReportingPeriod) | Not authoritative for canonical reporting. Admissible only as diagnostic, control, or source-reconciliation substrate | Source field admitted through Reader, Admission Contract, Observation Contract, and Canonical Contract field selection; optionally surfaced as a BCF characteristic if a metric demands it | Admissible with strict naming and definition discipline (below) |
| C | Tenant fiscal calendar configuration | Tenant runtime configuration per legal entity per DEC-d7e7a0 (regular, 4-4-5, or custom variants; optional `tenant.fiscal_period_boundary` table) | Drives the Layer A resolver | `tenant.fiscal_calendar_config` per tenant; `master.dim_fiscal_calendar` as the platform shared dimension | No — runtime configuration, not contracted substrate |

### Naming discipline

The bare label `fiscal period` MUST NOT be used as a BCF characteristic name. It collides with the Layer A concept this chapter defines and would document a meaning-drift hazard at the BCF substrate layer. A characteristic admitted as `fiscal period` is unable to declare whether it carries Layer A authoritative reporting period or Layer B source-attested period, and invites metric authors to bind it as a `business_field` grain key under the wrong semantic.

The name `posting period code` is reserved for the Layer B BCF characteristic, admissible only when a downstream metric demands source-attested period for reconciliation or source-control purposes. Acceptable alternatives are `accounting period code` and `source posting period code`. The label MUST carry the `code` qualifier (matching the code, string, or dimension shape) and a source-attestation marker (`posting`, `accounting`, or `source`) to differentiate it from Layer A.

### Layer B definition discipline

If a Layer B BCF characteristic is later admitted, the definition MUST:

1. State the source-attested origin: "the period code the source system stamps on the document at posting time."
2. Declare non-authority for canonical reporting: "NOT the platform-derived canonical reporting period; see canonical reporting period in this chapter for that."
3. List source vocabulary examples as evidence only: SAP MONAT plus GJAHR, Oracle GL_JE_HEADERS.PERIOD_NAME, NetSuite postingPeriod, QuickBooks ReportingPeriod.
4. Frame admissible use cases: source-reconciliation metrics ("does our canonical reporting period match what the source said?"), source-period-state control checks ("is this period locked at the source?"), NEVER period-grouped reporting.
5. Be silent on canonical-period derivation. The canonical path is owned at this chapter, not at the BCF characteristic definition. A Layer B characteristic that describes the canonical resolver's behaviour is a definition defect, not a Layer B characteristic.

### The general rule

The boundary that fiscal time exposes generalises: **BCF characteristics declare source-attested fields — values carried into the Canonical Object via the source mapping path (Reader, Admission Contract, Observation Contract, Canonical Contract field selection from source). Resolver-stamped enrichment outputs (fields the canonical resolver computes from canonical context such as posting date plus tenant calendar plus legal entity) live at the Canonical Contract and canonical-resolution boundary, not at BCF.** A Layer A candidate fails the BCF admission test as a category error; a Layer B candidate succeeds only when a metric demands the source-attested value AND the naming and definition discipline above is satisfied.

The general rule is the operational form of Invariant I at the BCF boundary: meaning is produced at the boundary that owns the concept, not at a peer surface that compensates.

**Governing source.** This chapter; DEC-d7e7a0; DEC-a8e8fc; DEC-1efa47; BCF vocabulary evidence framework (`bc-docs-v3/docs/implementation/business-concept-registry-vocabulary-evidence-framework.md`); Foundation Invariants.

## References

- Foundation: Scope and Non-Negotiability
- The Object Model: The Object Model
- The Contract Grammar: The Contract Grammar
- Sources and the Catalog: Sources and the Catalog
- Admission and Observation: Admission and Observation
- Canonical Evaluation: Canonical Evaluation
- Metric Evaluation: Metric Evaluation
- Tenancy and Binding: Tenancy and Binding
- DEC-d7e7a0: Platform date dim plus per-entity tenant fiscal calendar plus FiscalCalendarService
- DEC-a8e8fc: Canonical Contract declares posting-date field; canonical resolution enriches payload
- DEC-1efa47: Grain key-source mismatch; fiscal period is a business field
- Business Concept Registry — Vocabulary Evidence Framework: BCF admission discipline and substrate-boundary §11 amendment (`bc-docs-v3/docs/implementation/business-concept-registry-vocabulary-evidence-framework.md`)
- Foundation: The Invariants — Invariant I (meaning is evaluated once)
- Decisions: ADR Registry
