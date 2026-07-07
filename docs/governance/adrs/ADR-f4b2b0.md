---
uid: DEC-f4b2b0
title: "Aggregation-currency declaration for amount metrics"
description: "Every amount metric must declare its aggregation-currency basis; PE-MC must enforce single-currency aggregation or explicit multi-currency policy"
status: decided
date: 2026-07-06T13:10:05.608Z
project: bc-core
domain: metrics
subdomain: metric-contract/currency
focus: grammar
---

# Aggregation-currency declaration for amount metrics

## Context

Three-way-corroborated research (Codex 47 rows + Gemini 38 rows + Claude verified 24 claims) confirmed currency-mixed aggregation as the #2 platform risk after sign semantics. Live probe on pilot1 showed 642 EUR + 1,074 INR COs on the same slice, with SUM producing a meaningless mixed total. The gap is masked only by SDG wrbtr==dmbtr. Foundation gate analysis places the fix at repair location B (contract grammar) — the MC must declare currency semantics; lower layers cannot compensate for an underspecified contract. The three-policy design (document_currency / single_currency_required / local_currency) covers the spectrum from per-currency reporting through fail-safe enforcement to pre-normalized amounts, with a safe default and a clear extension path for consolidation.

## Problem

All 85 active metrics whose formula includes a SUM over a currency-typed variable currently aggregate across mixed currencies. On pilot1, 642 EUR COs and 1,074 INR COs sit on the same AR slice; `ar_balance = SUM(gross_amount)` produces a single number that adds euros to rupees. This is masked today **only** because the SDG emits `wrbtr == dmbtr` (document currency equals local currency in every row). The moment real multi-currency data arrives — or the SDG gains FX realism (TSK-72a0a7) — every amount metric silently produces a meaningless total.

**Scope:** this gap affects every MC whose formula contains `aggregate(sum, variable_ref)` where the bound variable's `representation_term` is `amount` or `currency`. On the current corpus that is ~60 of 85 active metrics (all balance, turnover, aging-bucket, and invoiced-amount families).

## Foundation Gate

**Repair location: B (Contract Semantics)**

1. **Why B?** The MC grammar has no vocabulary slot for declaring which currency basis a metric aggregates in. The formula AST's type system knows about `currency` as a representation term (currency×currency is rejected, currency×number is permitted) but never asks *which* currency. This is a semantic gap in the contract grammar itself — Invariant I (meaning evaluated once) requires that currency semantics be declared at the metric boundary, not inferred or patched downstream.

2. **Why not C–F?** The PE-MC evaluator (D) sums blindly because no MC (B) tells it to partition or filter by currency. The CC (C) carries `currency_code` as a passthrough field in `resolved_schema`, not as a grain key. Patching D to `GROUP BY currency_code` is compensation for an underspecified B. Patching E (fact tables) or F (read models) is even further from the source of meaning.

3. **Why not A?** Source observation is correct. OC maps WAERS→currency_code faithfully. The raw data carries the information; the metric layer doesn't use it.

## Decision

### D1: MC grammar extension — `aggregation_currency` declaration

Every MC whose formula aggregates a currency-typed variable MUST declare an `aggregation_currency` policy in a new top-level MC body field. Three policy values:

| Policy | Meaning | PE-MC behavior |
|--------|---------|----------------|
| `document_currency` | Metric aggregates per currency as-is; each currency produces a separate metric value | PE-MC adds `currency_code` to the partition keys (alongside fiscal_period and any grouping dimensions). Result is per-currency. |
| `single_currency_required` | Metric requires all COs in scope to share one currency; mixed populations are a defect | PE-MC asserts single currency in the resolved set; if >1 currency found, the run produces `MC_DEFECT_MIXED_CURRENCY` (analogous to existing defect codes). |
| `local_currency` | Metric aggregates in the tenant's local/functional currency; requires a local-currency amount field on the CO | PE-MC binds to the local-currency variable (mapped from DMBTR/HSL at OC). Structurally prevents mixing because amounts are already normalized. Requires OC/CC to project a `local_currency_amount` field. |

**Default for new metrics:** `single_currency_required` (fail-safe — forces the author to confront currency if the population is mixed).

**Backfill for existing 85 metrics:** `document_currency` with `currency_code` added as a computed grouping dimension. This preserves current behavior (the SDG is single-currency per legal entity) while making the per-currency split explicit. Downstream consumers (metric snapshots, dashboards) must handle the per-currency grain.

### D2: CC `currency_code` promoted to grouping-eligible field

CC `resolved_schema` already carries `currency_code`. No CC change needed — the field is available for MC `computed_dims` binding. The MC grammar extension (D1) is what makes it semantically meaningful.

### D3: PE-MC enforcement

The PE-MC evaluator gains a pre-aggregation currency check:

- Read the MC's `aggregation_currency` policy.
- `document_currency`: inject `currency_code` into the partition keys before aggregation.
- `single_currency_required`: scan the resolved set's `currency_code` values; if >1 distinct value, emit `MC_DEFECT_MIXED_CURRENCY` and halt (no partial result).
- `local_currency`: resolve the local-currency variable binding; if the bound field is NULL or absent on any CO, emit `MC_DEFECT_LOCAL_CURRENCY_MISSING`.

### D4: SDG realism dependency (not blocking)

TSK-72a0a7 (SDG FX realism) will make `wrbtr ≠ dmbtr` on cross-currency documents, exercising this gate. The ADR does not depend on SDG changes — the grammar and enforcement land first; SDG realism validates them.

### D5: OC/CC local-currency projection (deferred)

The `local_currency` policy requires OC to map DMBTR→`local_currency_amount` and CC to project it. This is a Phase 2 extension — not needed for the `document_currency` or `single_currency_required` policies that cover the immediate corpus. Deferred to a follow-up ADR when consolidation/group-level metrics are built.

## Implementation sequence

1. **Grammar:** Add `aggregation_currency` field to the MC body schema (mcf.metric_contract_version table, panel evaluation, preflight checks).
2. **PE-MC:** Implement the three-policy pre-aggregation check in `governed-metric-runtime.ts`.
3. **Preflight:** `devhub_metric_preflight` Layer-2 advisory: warn when an amount metric lacks `aggregation_currency`.
4. **Backfill:** Update all 85 active MCVs with `aggregation_currency: 'document_currency'` + add `currency_code` computed_dim binding.
5. **Panel:** PE-MC-12 authoring panel prompts for currency policy on amount metrics.

## Conformance

- **Invariant I (meaning evaluated once):** Currency semantics are now declared at the MC boundary, not left to downstream interpretation.
- **Invariant II (object ordering fixed):** No change — currency partitioning adds dimensions but doesn't alter ordering.
- **Invariant IV (explicit references):** The MC explicitly references its currency policy; no implicit assumption that amounts share a currency.
- **Invariant VI (evidence emitted):** `MC_DEFECT_MIXED_CURRENCY` is evidence of a violation, not a silent skip.

## What this does NOT solve

- **Consolidation/group-level currency** (EUR+INR→USD at a declared rate): requires FX-rate reference data, a `normalize_currency` derivation function, and the `local_currency` policy. That is a separate, larger design problem — this ADR establishes the grammar slot it will plug into.
- **Sign semantics** (TSK-04e6df): orthogonal — amounts can be correctly currency-partitioned but still sign-incorrect if SHKZG is unhandled.
- **Historical FX rates**: the `local_currency` policy uses pre-converted amounts from the source (DMBTR), not a BareCount-maintained rate table. Rate-based conversion is out of scope.
