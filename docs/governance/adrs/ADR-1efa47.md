---
uid: DEC-1efa47
title: "Grain key-source mismatch: fiscal_period vs evaluation_period must be disambiguated"
description: "Grain slot `{key:\"fiscal_period\",source:\"evaluation_period\"}` conflates business calendar period with engine runtime context — engine silently reads payload[key] and emits dates as if they were fiscal periods. Proposed: rename keys, enforce source in engine, add onboarding gate."
status: superseded
subdomain: evaluation-engine
focus: grain-semantics
date: 2026-04-20T11:21:48.423Z
project: bc-core
domain: contracts
migrated_from: legacy v2 archive
---

# Grain key-source mismatch: fiscal_period vs evaluation_period must be disambiguated

## Context

Root cause of date-as-fiscal-period bug in demo-selenite AR Turnover snapshots. Authoring, engine, and gate all need fixing — any single-layer fix leaves the foot-gun open. Raised as proposed ADR for user review before implementation.

## Problem

The metric contract (MC) and canonical contract (CC) envelopes allow a grain entry of the form
`{ "key": "fiscal_period", "source": "evaluation_period" }`.

This is semantically broken:

- **`fiscal_period`** means a business calendar period identifier — `FY2025/04`, `2025-P01`, `004/2025`, etc. It is sourced from the posting itself (e.g. SAP `GJAHR` + `MONAT`). Correct declaration: `source: business_field, field_code: <fiscal_period_field>`.
- **`evaluation_period`** means the time window the engine is evaluating for (e.g. "as of 2025-04-30"). It is set by the engine / scheduler context (`ComputeContext.evaluationPeriod`), not present in the source data.

Observed on bc-portal Monitor (SES-7c28ea/SES-163a9b) for demo-selenite Accounts Receivable Turnover Ratio (MC 019d7650-…): `businessKey` comes back as `{ company_code: "1000", fiscal_period: "2025-04-28" }`. The value is a calendar date, not a fiscal period. The grain declaration labelled it `fiscal_period` but set `source: evaluation_period`; the engine ignored `source` and naïvely read `payload.fiscal_period`, which upstream code (likely reader or canonical resolution) was populating with `BUDAT`/`BLDAT`.

## Root cause

Three linked defects:

1. **Authoring** — current MC/CC envelopes use `fiscal_period` as the grain key while declaring `source: evaluation_period`, which is incoherent. The key must match the source.
2. **Engine does not honor `source`** — `metric-evaluation-engine.service.ts:879` `groupInputsByGrain` reduces grain to `string[]` of keys and does `payload[k]`. It never branches on `source`.
3. **No validation gate** — CC/MC onboarding does not reject `key=fiscal_period` with `source=evaluation_period`, nor does it reject a business-term key with context-only source.

## Decision

Fix all three layers. No partial fix — any one alone leaves foot-guns.

### 1. Canonical grain semantics (contract)

Two, and only two, legal shapes for a grain slot:

```
{ "key": "<business_term>", "source": "business_field", "field_code": "<canonical_field_name>" }
{ "key": "evaluation_period",  "source": "evaluation_period" }
```

Rules:
- If `source=business_field`, `field_code` is mandatory and must resolve to a canonical field declared in the CC schema.
- If `source=evaluation_period`, `key` MUST be literally `"evaluation_period"` — no other label permitted. The engine will stamp `envelope.evaluationPeriod` into `businessKey.evaluation_period`. The stored format is the existing `ComputeContext.evaluationPeriod` convention (YYYY-MM or YYYY-Qn).
- A grain may have 0 or 1 `evaluation_period` slot, and N `business_field` slots.

### 2. Engine enforcement

`groupInputsByGrain` and `extractBusinessKey` must:
- Take the full `GrainItem[]` (not `string[]`).
- For `business_field` slots: read `payload[field_code]`.
- For `evaluation_period` slot: take `envelope.evaluationPeriod` (already wired elsewhere in metric.service.ts) and stamp it into `businessKey.evaluation_period`. Never read it from payload.
- If a `business_field` slot's `field_code` is missing from a payload, the row goes into the `_null_` bucket and is reported in `rejectedGroups`.

### 3. Onboarding gate (CR-QG-GRAIN-SEMANTICS)

Add a blocker gate on `mc-onboarding` and `cc-onboarding`:
- Reject any grain item where `source=evaluation_period` and `key != "evaluation_period"`.
- Reject any grain item where `source=business_field` and `field_code` is missing or not in CC schema.
- Reject the reserved label `"fiscal_period"` with `source=evaluation_period` explicitly (common past mistake).

### 4. Data migration

- Scan all existing MC / CC versions. For each grain slot with `source=evaluation_period`, rename the key to `"evaluation_period"` and bump version. For each with `source=business_field` and no `field_code`, flag for manual repair.
- For the specific Accounts Receivable Turnover Ratio case and its siblings — authoring decision: did we *want* the fiscal posting period (a business field) or the evaluation window (engine context)? Likely the former. The canonical payload needs a real `fiscal_period` field (sourced from `GJAHR+MONAT` in SAP, equivalent elsewhere) and the grain should point at it.
- Existing `metric_snapshot` rows whose `businessKey.fiscal_period` is actually a date should be marked deprecated, not mutated — immutable per platform rules. Re-evaluation with the corrected grain produces new snapshots.

## Consequences

- **Breaking for every existing MC/CC with `source=evaluation_period`**: all such envelopes must be re-authored. Scope depends on how many. A migration script should list affected contracts.
- **bc-portal Monitor Value tab** is unaffected: it already renders whatever dimensions the businessKey contains. Once the engine emits a correct `evaluation_period` and/or correct `fiscal_period`, the existing per-dimension filter UI shows them correctly (see SES-163a9b).
- **Chain completeness (D305)**: L4/L6 checks for grain-supporting fields will need to include the real `fiscal_period` source field; today the chain check already knows about `source=evaluation_period` slots — `chain-status.service.ts:681` short-circuits them. That stays correct.
- **Compute evaluator**: already expects `ComputeContext.evaluationPeriod` in YYYY-MM / YYYY-Qn. No change needed there; it just needs the engine to actually populate it from a correct grain slot.

## Alternatives considered

- *Leave keys free-form, trust authors.* Rejected — current state proves authors conflate the two, and the engine's silent fallthrough masks the error until data hits the UI.
- *Only fix the engine, leave data.* Rejected — silent semantic drift between engine and stored snapshots; future queries would disagree on whether `businessKey.fiscal_period` is a date or a period id.
- *Only fix onboarding, migrate existing.* Rejected — without engine enforcement, drift recurs the first time someone hand-edits an envelope.

## References

- Discovered: SES-932d96 (Monitor wiring) → SES-7c28ea (per-grain hero) → SES-163a9b (multi-dim filters) — user-caught in bc-portal Value tab when filter dropdown listed 21 "fiscal_period" values that were clearly dates.
- Related: ADR-c0290f (metric evaluation engine, grain-aware).
- Related: D305 chain completeness SSOT — grain completeness check.
