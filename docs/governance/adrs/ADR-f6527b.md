---
uid: DEC-f6527b
title: "Currency normalization for metrics — canonical FX rate store + normalize_currency policy"
description: "Currency normalization for metrics — canonical FX rate store + normalize_currency policy"
status: decided
date: 2026-07-08T00:58:42.295Z
project: bc-core
domain: metrics
subdomain: metric-contract/currency
focus: architecture
---

# Currency normalization for metrics — canonical FX rate store + normalize_currency policy

## Context

No rationale recorded.

## Decision

CONTEXT. DEC-f4b2b0/D495 (aggregation-currency declaration) is implemented: every amount metric declares an aggregation_currency policy, PE-MC-16 enforces it, and the runtime partitions by currency_code (document_currency — all 111 active MCVs backfilled). DEC-f4b2b0 §D5 explicitly DEFERRED the harder half — converting amounts into a single reporting currency at a declared FX rate — to "a follow-up ADR when consolidation/group-level metrics are built." This is that ADR. It locks the DESIGN; implementation is deferred (see below).

Grounded in a read-only end-to-end trace (SES-8b31e0) of the Exchange Rate Reader (executors cite "D011" but the real locked ADR is DEC-b10dad, nickname D043, status implemented; companion DEC-6a1b47 is the convergence proof — the "D011" citation in the executors is stale and should be corrected to DEC-b10dad/D043). Trace findings that shape this decision:
- DEC-b10dad locks the reader NORTH-SIDE ONLY: one Exchange Rate Reader, three flavors (ECB SDMX / Open Exchange Rates / FRED), admission only; "south-side (canonical evaluation, metrics, actions) is not the reader's concern." Multi-source convergence = source-shape → canonical-shape convergence, NOT a runtime provider arbitration/blend engine.
- There is NO usable rate store today. Observed rates land in progression.admission (metadata; rate key stored null) + a raw source-shape table fact.so_<ecb_exr_code>_v1_0_0 IN A TENANT DB, keyed by the SDMX source key, and only if provisioned. The canonical FX objects and the gold "FX Rate" contract are DEFINED but never populated — canonical resolution is a permanent no-op (0 mapping rows). Nothing is queryable by (base, quote, rate_date, rate_type, source).
- Tenant model is mostly absent: no FX provider preference; no functional currency; org_profile.reporting_currency_code exists (D368) but the platform never reads it. Only one reader-level ECB admission binding exists (no per-flavor OER/FRED contracts — a DEC-b10dad conformance gap).
- Nothing converts amounts today (no normalize_currency).

PROBLEM. To report a metric in a single reporting/presentation currency — for group/consolidated reporting, or simply to honor a jurisdiction's convention (e.g. India books a foreign-currency transaction at the invoice/transaction-date spot rate under Ind AS 21) — the platform must convert document-currency amounts at the correct rate-date using observed rates. Today it cannot: there is no queryable rate store, no conversion policy, and no tenant currency/provider model. The moment real multi-currency data arrives (SDG FX realism, TSK-72a0a7) this becomes load-bearing.

FOUNDATION GATE. This spans four repair locations; each is the correct home and no lower layer can compensate:
- A (source reality / reference data): the observed FX rates must land in a queryable canonical/global rate entity. Today they exist only as raw per-tenant source rows — not a usable reference surface.
- B (contract semantics): the MC grammar has no way to declare "convert to currency X at rate-date basis Y." Invariant I requires currency-conversion meaning to be declared at the metric boundary, not inferred downstream.
- C (binding): which reporting currency, which FX provider, and (via the accounting-standard binding) which rate-date basis are per-tenant/entity bindings.
- D (evaluation): a governed normalize_currency derivation resolves the rate and applies it, emitting evidence.
Why not compensate lower: patching the evaluator (D) to guess a rate, or the read model (F) to convert, without the canonical rate store (A) and the MC declaration (B) is exactly the lower-layer compensation the invariants forbid.

DECISION.

D1 — CANONICAL/GLOBAL FX RATE STORE. Define a queryable canonical FX rate entity keyed (base_currency_code, quote_currency_code, rate_date, rate_type, source, version). Populate it by fixing the currently-no-op canonical convergence so the ECB/OER/FRED reader's admitted observations resolve into this one canonical shape (DEC-6a1b47's convergence, made real). SCOPE = PLATFORM-GLOBAL: FX rates are shared reference data, not tenant-owned — this resolves the current inconsistency where global-scope providers write into a tenant DB. Tenants REFERENCE the global store; a tenant may supply PROPRIETARY rates as an additional source (same keyed shape, source='tenant:<slug>'), which take precedence for that tenant when its provider preference selects them.

D2 — PER-FLAVOR ADMISSION CONTRACTS. Author OER- and FRED-specific admission/source contracts (today only the ECB contract is bound reader-level, so OER/FRED validate against ECB's shape). Closes the DEC-b10dad conformance gap ("each flavor has its own source-specific admission contract") and is a prerequisite for honest multi-source convergence.

D3 — TENANT/ENTITY CURRENCY MODEL. Capture per legal-entity: functional/local currency, reporting/presentation currency (wire the existing but-unread org_profile.reporting_currency_code, D368), and FX SOURCE PREFERENCE (which provider — ECB/OER/FRED/proprietary). The accounting STANDARD binding (Multi-Standard Onboarding) supplies the default rate-date basis; the tenant does not free-choose the rate-date rule.

D4 — normalize_currency MC POLICY + DERIVATION. Add a 4th aggregation_currency policy value, normalize_currency, alongside document_currency / single_currency_required / local_currency. A metric with this policy declares (a) a target currency (usually the entity reporting currency, resolved via D3) and (b) a RATE-DATE SELECTOR. A governed normalize_currency derivation at the CC/evaluation layer (D) resolves the rate from the D1 store by (base, quote, rate_date, rate_type, source, version) and converts, emitting lineage. The rate-date selector is NOT a free toggle — it is constrained by (accounting standard x metric temporal semantic):

| Rate-date selector | Applies to | Metric shape | Standard basis (Ind AS 21 / IAS 21 / ASC 830 agree in shape) |
|---|---|---|---|
| transaction | initial recognition of the transaction | period FLOW (revenue, invoiced amount) | spot at transaction/invoice date |
| closing | re-translation of MONETARY items at period end | as-of BALANCE (AR/AP balance, aging, DSO base) | closing rate at reporting date; unrealized FX gain/loss |
| settlement | realization on payment | realized/collection metrics | spot at settlement date; realized FX gain/loss |
| average | period-average convention (e.g. P&L) | flow metrics under an averaging convention | period average rate |

CONFORMANCE (invariants).
- I (meaning once): the MC declares its target currency + rate-date basis at the metric boundary; conversion is not inferred downstream.
- III (immutable): FX rates are immutable, versioned facts; a corrected/restated rate is a new version, prior versions coexist (supports audit + restatement).
- IV (explicit references): a converted value references its rate by (base, quote, rate_date, rate_type, source, version) — never "latest".
- VI (evidence emitted): the normalize_currency derivation emits lineage recording which rate row(s) it used; a missing rate is MC_DEFECT_RATE_UNAVAILABLE, not a silent skip.

WHAT THIS DOES NOT SOLVE.
- FX gain/loss as its own metric family (realized/unrealized) — orthogonal; this ADR provides the rate substrate it would use.
- Intraday/real-time rates — daily reference rates only.
- The accounting treatment of remeasurement (posting FX gain/loss to the ledger) — a source-system concern, not a metric concern.

IMPLEMENTATION — DEFERRED. Not built now: today's corpus is single-currency per legal entity (document_currency is correct) and there is no multi-currency data to exercise conversion. Implementation begins when EITHER real multi-currency data lands (SDG FX realism TSK-72a0a7, making wrbtr != dmbtr) OR a consolidation/group-reporting requirement is scheduled. Sequence when it does: D1 canonical rate store + convergence -> D2 per-flavor contracts -> D3 tenant currency model -> D4 grammar + derivation + rate-date selector. This ADR is the locked design those steps implement.

RELATIONSHIP. Extends DEC-f4b2b0 §D5 (does not supersede it — the document_currency/single_currency_required/local_currency policies remain; normalize_currency is additive). Consumes the reader locked by DEC-b10dad/D043 (making its canonical south-side real). Hygiene follow-up: correct the ecb-sdmx/oer-api/fred-api executors' stale "D011" citation to DEC-b10dad/D043.
