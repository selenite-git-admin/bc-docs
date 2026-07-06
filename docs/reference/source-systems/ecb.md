---
uid: SRC-a1d8e3
slug: ecb
title: "ECB Exchange Rates"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: reference-data
subdomain: currency
focus: governance
proof_status: shape_tested
last_verified_at: 2026-04-28
official_docs_url: https://data.ecb.europa.eu/help/api/data
reader_flavors:
  - exchange-rate-reader-ecb
admission_contract_versions: []
governing_adrs:
  - DEC-b10dad   # D043 — Exchange Rate Reader Architecture (one reader, multiple flavors)
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/ecb.md
---

# ECB Exchange Rates

This page records BareCount's source-admission posture for ECB Exchange Rates. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `shape_tested`.

The `EcbSdmxExecutor` (`bc-core/src/boundary/reader-runtime/executors/ecb-sdmx.executor.ts`) has unit-test coverage (`ecb-sdmx.executor.spec.ts`) validating SDMX 2.1 XML parsing, dimension extraction, and SO emission. Public ECB endpoint reachability is exercised in tests.

What is **not** yet verified for `first_hand_proven` status:
- A real (anonymised) customer scenario where ECB rates have been admitted, canonical-resolved, and consumed by a metric snapshot end-to-end through a production tenant chain.

ECB is a strong candidate to be the first source page promoted to `first_hand_proven`, since the reader is built and the source is public — the gap is just one production consumption case with §9 evidence.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `exchange-rate-reader-ecb` | ECB SDMX 2.1 EXR data flow | `EcbSdmxExecutor` | — (not yet pinned to a numbered AC) |

Per D043, the `exchange_rate_reader` has multiple flavors (`ecb`, `oer`, `fred`, candidate `imf_sdr`, candidate `rbi`). All flavors emit the same SO structure (`exchange_rate_observation`: currency pair, rate, date, source authority); flavor-specific admission contracts handle protocol differences.

---

## 3. What BareCount Admits

### 3.1 Metadata

Currency pair definitions (EUR/USD, EUR/GBP, EUR/JPY, etc.); SDMX dimension codes (FREQ, CURRENCY, CURRENCY_DENOM, EXR_TYPE, EXR_SUFFIX); publication-schedule metadata.

### 3.2 Business data

Daily reference exchange rates (EUR base, ~30 currencies); historical exchange rate series (back to inception per series); published by ECB at ~16:00 CET each working day. Domain: `currency/exchange_data`.

---

## 4. Legal & Licensing

Vendor licensing, access-tier, rate-limit, pricing, and contractual terms are not maintained as static facts in v4.

During source onboarding, verify:

- customer entitlement for the selected API or interface
- whether a dedicated service identity requires a paid license
- whether read-only extraction is permitted under the customer contract
- rate-limit, concurrency, and data-egress constraints that affect reader scheduling

Record the verified terms in the onboarding evidence for that tenant and source. This page may name the admission stance, but it must not be treated as vendor-license advice.

---

## 5. Commercial

No static commercial estimate is maintained here.

Capture customer-specific subscription, add-on, service-account, API, connector, egress, partnership, or infrastructure costs during onboarding evidence review.

---

## 6. Technical

### 6.1 SDMX 2.1 REST API (primary)

| Attribute | Value |
|---|---|
| Base URL | `https://data-api.ecb.europa.eu/service/data/EXR/` |
| Format | SDMX 2.1 (XML) |
| Auth | None |
| Rate limit | None (reasonable use) |
| Publication | ~16:00 CET each working day |

### 6.2 Query pattern

```
GET https://data-api.ecb.europa.eu/service/data/EXR/{FREQ}.{CURRENCY}.{CURRENCY_DENOM}.{EXR_TYPE}.{EXR_SUFFIX}
```

For EUR-base daily spot rates: `D.{currency}.EUR.SP00.A`.

Date range filtering via `?startPeriod=YYYY-MM-DD&endPeriod=YYYY-MM-DD`.

### 6.3 Executor handling

`EcbSdmxExecutor` parses the SDMX 2.1 XML envelope, walks `<generic:Series>` and `<generic:Obs>` nodes, extracts the dimension tuple and observation value, and emits one `RunObservationItem` per series-observation. Provenance includes the source URL and fetch timestamp.

---

## 7. Customer-Side Onboarding

**None.** ECB data is public. No customer admin action is required.

---

## 8. BareCount-Side Onboarding

ECB is pre-loaded. The `exchange-rate-reader-ecb` flavor is registered in the seed registry; admission is triggered by the daily scheduler. No per-tenant configuration is needed.

When a customer activates currency-conversion features, their tenant binds to the platform-wide ECB SO stream — they do not need their own ECB connection profile.

---

## 9. Verified Coverage

**No real customer scenario yet exercised end-to-end through a production tenant chain.** Unit tests cover the executor against the public ECB endpoint; this is shape-test coverage, not first-hand customer proof.

When the first customer's metric uses ECB-admitted rates in a production canonical resolution, this section will be updated with: which currency pairs were exercised, the date range, and the anonymised tenant reference.

---

## 10. Known Gaps

1. **Production-tenant proof** — see §9.
2. **Refresh-time tolerance** — the daily scheduler must accommodate ECB's ~16:00 CET publication; no ECB-specific lateness alert is wired.
3. **Series-discontinuation detection** — when ECB retires a currency (e.g. legacy ECU rates), the reader should mark the series stale rather than silently emit no observations.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Exchange Rate Reader Architecture (D043) | legacy-v2/docs/decisions/ADR-DEC-b10dad.md (pending v3 reconciliation) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| ECB Data Portal | https://data.ecb.europa.eu/ |
| ECB Data API documentation | https://data.ecb.europa.eu/help/api/data |
| ECB euro reference exchange rates | https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html |
| SDMX 2.1 technical standard | https://sdmx.org/?page_id=5008 |
| Predecessor — legacy v2 archive ECB reference | legacy-v2/reference/sources/ecb.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
