---
uid: DEC-7bccf6
title: "Retire platform-computed FX conversion — the source's own booked conversion is authoritative"
description: "Platform never converts currency: retire normalize_currency + the canonical FX store as conversion authority; the source's own booked local-currency amount (WRBTR/DMBTR pattern) is authoritative; D495 policies survive; ECB-as-reference and group-reporting consolidation left explicitly open"
status: decided
date: 2026-07-30T03:43:11.270Z
project: platform
domain: metrics
subdomain: currency
focus: doctrine
supersedes: DEC-f6527b
---

# Retire platform-computed FX conversion — the source's own booked conversion is authoritative

## Context

A platform-computed conversion produces a figure that contradicts the customer's audited books — the exact failure mode BareCount exists to remove — and violates Invariant I (meaning produced once at its boundary) and Invariant VI (evidence emitted, not inferred) by manufacturing meaning at a lower layer to compensate for a semantic the source already resolved. The feature was never load-bearing: the canonical FX store has resolved to 0 mapping rows since inception, org_profile.reporting_currency_code was never read by any code path, and the only functioning multi-currency policy (D495 local_currency) already consumes the source's pre-converted amount. Retirement removes rate-source governance, rate versioning and rate-date-basis selection (which diverges across Ind AS 21 / IAS 21 / ASC 830) at no loss of current capability. The obligation correctly shifts to admission: sources expose both amounts, as every real ERP already does.

## Decision

Operator decision 2026-07-30. **BareCount does not convert currency.** The platform-provided FX conversion capability designed under DEC-f6527b (D502) — a platform-global canonical FX rate store plus a `normalize_currency` aggregation policy with a rate-date selector — is RETIRED as wrong in principle, not merely deferred.

WHAT IS RETIRED
1. `normalize_currency` as an aggregation-currency policy (platform re-derives an amount in a currency the source never booked).
2. The canonical FX rate store as a CONVERSION authority (the keyed rate entity + gold FX contract that today resolve to a permanent no-op, 0 mapping rows).
3. Any read of `org_profile.reporting_currency_code` as an instruction to convert (it is a disclosure attribute, not a conversion trigger; the platform never read it anyway).

WHAT REMAINS AUTHORITATIVE (unchanged, and now the only path)
The SOURCE system's own booked conversion. Every ERP maintains its own rate table (SAP TCURR, Odoo `res.currency.rate`, BC Currency Exchange Rates) and, when a foreign-currency document posts, stores BOTH the document-currency amount AND the company/local-currency amount plus the rate applied (SAP WRBTR/DMBTR/WAERS/KURSF; Odoo `amount_currency`/`balance`/`currency_id`/`company_currency_id`). That local-currency amount is an IMMUTABLE HISTORICAL FACT of the customer's books — it does not change when rates move. DEC-f4b2b0 (D495) survives intact: `document_currency`, `single_currency_required`, and `local_currency` remain the aggregation policies, and `local_currency` "uses pre-converted amounts from the source, not a BareCount-maintained rate table."

RATIONALE
Re-deriving a converted amount would produce a number that CONTRADICTS the customer's audited books — the precise failure BareCount exists to eliminate ("the moment a CFO realises she no longer has to negotiate truth"). It also violates the execution model: meaning is produced once at its boundary (Invariant I) and evidence is emitted, not inferred (Invariant VI); a platform-side conversion is meaning manufactured at a lower layer to compensate for a semantic the source already resolved. Empirical support: the rate store has been a no-op since inception, the reporting-currency field was never read, and the only working multi-currency policy already consumes source-side conversion. Retiring the feature removes rate-source governance, rate versioning, rate-date-basis selection (Ind AS 21 / IAS 21 / ASC 830 divergence) and a standing correctness risk, in exchange for nothing that is currently used.

SOURCE OBLIGATION (what this pushes onto admission, and is correct there)
A source must expose, per monetary row: document currency code, document-currency amount, company/local-currency amount, company currency code, and the posting date. A source that cannot supply its own local-currency amount limits its metrics to `document_currency` (per-currency partition) or `single_currency_required` — it does NOT trigger platform conversion. Mixed-currency aggregation without a declared policy remains the Class-C defect (DEC-31dc55).

EXPLICITLY OPEN (not decided here; must not be silently resolved by this retirement)
(a) ECB/RBI reference rates as NON-AUTHORITATIVE data — deviation/diagnostic use ("booked rate deviates N% from reference"), disclosure, and independent cross-check. The ECB source is already catalogued and shape_tested; retiring conversion does not retire reference data.
(b) Cross-entity / group-reporting consolidation into a currency no entity booked in. The customer's ERP has no opinion about BareCount's group currency, but the platform must not invent one unilaterally either. If group reporting is ever in scope it needs its own ADR naming the authority, the rate basis, and the disclosure obligation — it is NOT inherited from this decision.
(c) Whether `aggregation_currency_code` should gain an explicit `not_applicable`/`source_booked` label now that `normalize_currency` is gone.
