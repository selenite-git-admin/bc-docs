---
uid: DEC-a8e8fc
title: "CC declares posting_date_field; canonical resolution enriches payload with fiscal_period + fiscal_year"
description: "Every CC declares posting_date_field (which canonical field carries fiscal-anchor date). Canonical resolution calls FiscalCalendarService.resolve(posting_date) and stamps fiscal_period + fiscal_year onto the payload. Metric grain uses source=business_field for fiscal_period — no engine special-casing."
status: implemented
subdomain: fiscal-calendar
focus: canonical-enrichment
date: 2026-04-20T12:10:23.906Z
project: bc-core
domain: contracts
migrated_from: legacy v2 archive
---

# CC declares posting_date_field; canonical resolution enriches payload with fiscal_period + fiscal_year

## Context

Fiscal_period is a per-CO attribute determined by posting_date. Canonical resolution has tenant context and access to FiscalCalendarService; reader and engine do not. Stamp there, not in grain. Engine then treats it as plain business_field.

## Problem

Fiscal_period must be a per-CO attribute determined by the CO's posting_date resolved against the tenant's fiscal calendar (D364). Today no mechanism exists to produce this: neither the reader nor the canonical resolution service stamps it, and the engine cannot resolve it because it lacks tenant context and calendar config.

Result: the grain slot `{key:"fiscal_period", source:"evaluation_period"}` was a workaround that conflated the concept and led to the D363 bug.

## Decision

Fiscal period is stamped **at canonical resolution time**, as a derived business field on the canonical payload. The engine then treats it as an ordinary `source: business_field` grain slot.

### 1. CC body gains `posting_date_field`

A new required field on the canonical contract body:

```
"posting_date_field": "receivable_hdr_posting_date"
```

Semantics:
- References a canonical field declared in the CC's `resolved_schema`.
- That field must be of date/timestamp type.
- Holds the **fiscal-anchoring date** — the date whose fiscal period the metric result will be tagged with.
- For accounting domains: SAP BUDAT equivalent (posting date, not document date BLDAT).
- For non-accounting domains (Salesforce opportunities etc.): whatever field carries the fiscal-anchor date (`close_date`, `booking_date`, `transaction_date`). The contract term remains `posting_date_field`; per-domain docs note equivalents.

### 2. CC onboarding validates it

In `cc-onboarding.service.ts`:

- Check `posting_date_field_declared`: required, non-empty.
- Check `posting_date_field_in_schema`: must resolve to a field in `resolved_schema` with type in {string (date/datetime), timestamp}.
- Warn if the canonical field is named ambiguously (e.g. ends with `document_date` — hint that it may be BLDAT not BUDAT). Not a block; authors can override with an explicit confirmation flag.

### 3. Canonical resolution enriches the payload

In `canonical-resolution.service.ts`, after merging the group payload and before creating the CO:

```
const postingDateFieldName = cc.body.posting_date_field;
const postingDateValue = payload[postingDateFieldName];
const entity = payload.legal_entity_code ?? payload.company_code ?? '*';
const periodInfo = fiscalCalendarService.resolve(tenantId, entity, postingDateValue);

payload.fiscal_period = periodInfo.period_label;
payload.fiscal_year   = periodInfo.fiscal_year;
```

Errors:
- If `postingDateValue` is null/missing → reject group with `missing_posting_date` evidence (same pattern as other required-field rejections).
- If FiscalCalendarService has no config for tenant/entity → reject group with `no_fiscal_calendar` evidence, generate operator ticket.

The added fields become part of the stored CO `canonicalPayloadJson` and are indistinguishable from native canonical fields to the engine.

### 4. Metric grain authoring becomes trivial

Before (broken):
```
grain: [
  { key: "company_code",  source: "business_field", field_code: "company_code" },
  { key: "fiscal_period", source: "evaluation_period" }     // wrong
]
```

After:
```
grain: [
  { key: "company_code",  source: "business_field", field_code: "company_code" },
  { key: "fiscal_period", source: "business_field", field_code: "fiscal_period" }
]
```

Engine changes: **none**. The source-aware engine shipped in D363 Phase 1 / PR #3 handles this naturally.

### 5. What `source: evaluation_period` shrinks to

Retained in the spec but rare:
- Forecast / target metrics — the period being forecasted is not in the source data.
- As-of / aging metrics — compute-evaluator's `date_diff_as_of` (D330) takes `evaluation_period` as its anchor; this is a compute-rule context, not a grain-stamping mechanism.
- Standalone snapshot tags where a metric has no document date.

The D363 onboarding warn gate keeps flagging `{key != "evaluation_period", source: "evaluation_period"}` — that stays valid. Phase 2 migration moves all 778 MCs / 56 CCs from the legacy shape to `source: business_field, field_code: "fiscal_period"`.

## Scope

**IN:**
- Add `posting_date_field` to CC body schema + envelope builder.
- cc-onboarding validations (declared + in-schema + warn on likely-BLDAT naming).
- canonical-resolution.service.ts enrichment step.
- Unit tests: enrichment happy path, missing posting_date, missing calendar config, entity fallback.

**OUT:**
- Platform calendar infra — D364.
- Engine source-awareness — D363 Phase 1 (already shipped in PR #3).
- Phase 2 migration of the 778 MCs / 56 CCs — tracked on TSK-53edc3 once D364 + D365 are decided.

## Consequences

- Posting-date semantics match SAP / enterprise finance intuition — low friction for finance users.
- Late arrivals and backdated corrections land in the right period automatically (document date wins, not observation time).
- Multi-entity group consolidation works because each CO carries its own `legal_entity_code` and thus resolves against its own calendar.
- Scheduler stays a pure cron — zero fiscal semantics.
- Seed data audit required: several existing CCs currently point `receivable_hdr_document_date_time` (BLDAT-equivalent). Phase 2 migration must correct these to posting-date-equivalent fields.

## Alternatives considered

- **Stamp in reader, not canonical resolution:** readers are source-shape; they don't know tenant calendar semantics. Rejected.
- **Stamp in engine:** engine has no tenant context and no calendar access. Rejected.
- **Stamp in MC grain slot with a new `source: "derived_from_posting_date"`:** adds engine complexity for no benefit vs. a pre-engine canonical enrichment. Rejected.
- **Source-system fiscal_period (SAP MONAT+GJAHR):** ties our semantics to SAP's fiscal_year_variant and breaks for non-SAP sources. Rejected.

## References

- Depends on D364 (FiscalCalendarService).
- Replaces the "evaluation_period is default for fiscal grain" assumption in D363.
- Aligns with SAP BUDAT semantics (T001.PERIV fiscal_year_variant on company_code).
- Surfaced by user during SES-2ea1f7 course-correction of D363 PR #3: "FY should be determined by the date on the document".
