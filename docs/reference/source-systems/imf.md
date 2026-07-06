---
uid: SRC-c9f4a6
slug: imf
title: "International Monetary Fund (IMF)"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: reference-data
subdomain: macro
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://data.imf.org/en/Resource-Pages/IMF-API
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-b10dad   # D043 — Exchange Rate Reader Architecture (IMF SDR is a candidate flavor)
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/imf.md
---

# International Monetary Fund (IMF)

This page records BareCount's source-admission posture for International Monetary Fund (IMF). It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

What this means concretely:

- Reader architecture mapped (per D043, IMF SDR is a candidate flavor of `exchange_rate_reader`; non-currency datasets would use other readers).
- No executor built for IMF SDMX 2.1 or 3.0 surfaces.
- No customer or internal data flow exercised.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `exchange-rate-reader-imf-sdr` — daily SDR valuation (per D043 multi-flavor model).
- `macro-indicator-reader-imf-weo` — World Economic Outlook biannual release.
- `macro-indicator-reader-imf-ifs` — International Financial Statistics monthly/quarterly.
- `macro-indicator-reader-imf-bop` — Balance of Payments quarterly.
- `trade-statistics-reader-imf-dot` — Direction of Trade Statistics monthly bilateral trade.
- `commodity-price-reader-imf-pcps` — Primary Commodity Price System monthly.

A new SDMX-2.1/3.0 executor would underlie all of these (separate from `EcbSdmxExecutor`, since the dataflow shapes differ).

---

## 3. What BareCount Would Admit

### 3.1 Metadata

| Category | Description |
|---|---|
| Countries and areas | 190 member countries plus country groups (Advanced Economies, EMDE, G7, G20, ASEAN) |
| Indicators | Thousands across datasets (GDP, CPI, exchange rates, reserves, trade, debt, etc.) |
| Datasets (dataflows) | 30+ structured datasets organised by topic |
| Dimensions | SDMX dimension codes per dataset (FREQ, REF_AREA, INDICATOR, COUNTERPART_AREA, SECTOR, etc.) |
| Codelists | Enumerated valid values per dimension (ISO country, indicator, frequency) |
| Publication schedule | Dataset-specific (WEO biannual, BOP quarterly, DOT monthly, PCPS monthly, SDR daily) |

### 3.2 Business data — priority datasets

| Dataset | Frequency | BareCount domain | Priority |
|---|---|---|---|
| SDR exchange rates | Daily | `currency/exchange_data` | P1 |
| `IFS` International Financial Statistics | M, Q, A | `macro/financial_statistics` | P1 |
| `PCPS` Primary Commodity Price System | M | `macro/commodity_prices` | P1 |
| `WEO` World Economic Outlook | A (biannual) | `macro/economic_outlook` | P2 |
| `BOP` Balance of Payments | Q, A | `macro/balance_of_payments` | P2 |
| `DOT` Direction of Trade | M, Q, A | `macro/trade_statistics` | P3 |
| `GFS` Government Finance Statistics | A | `macro/government_finance` | P3 |
| `FSI` Financial Soundness Indicators | Q | `macro/financial_soundness` | P3 |

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

### 6.1 IMF Data Portal SDMX API (primary)

The IMF reference page distinguishes the relevant SDMX-based systems:

| System | Endpoint | Purpose |
|---|---|---|
| Data portal (SDMX 2.1) | `https://data.imf.org/api/sdmx/v1/` | Data queries, SDMX-REST 1.x, SDMX-ML 2.1 |
| Data portal (SDMX 3.0) | `https://data.imf.org/api/sdmx/v2/` | Data queries, SDMX-REST 2.x, SDMX-ML 3.0, SDMX-JSON 2.0 |
| SDMX Central (structures) | `https://sdmxcentral.imf.org/ws/public/sdmxapi/rest` (2.1) and `/sdmx/v2` (3.0) | Structure/metadata only |

The legacy `dataservices.imf.org` endpoint is **decommissioned** — do not use.

### 6.2 Query patterns

SDMX 2.1:
```
GET https://data.imf.org/api/sdmx/v1/data/{dataflowId}/{key}?startPeriod={start}&endPeriod={end}
```

SDMX 3.0:
```
GET https://data.imf.org/api/sdmx/v2/data/dataflow/IMF/{dataflowId}/{version}/{key}?c[startPeriod]={start}&c[endPeriod]={end}
```

`{key}` is a dot-separated dimension filter (`{FREQ}.{REF_AREA}.{INDICATOR}…`). Use `+` for multi-value, omit a position for "all values."

### 6.3 SDR endpoints (special case)

- Daily SDR valuation: `https://www.imf.org/external/np/fin/data/rms_sdrv.aspx`
- SDR rates per currency: `https://www.imf.org/external/np/fin/data/rms_five.aspx`
- Via IFS: indicator `ENDE_XDC_SDR_RATE`

The SDR basket is a periodically reviewed official composition; verify currency weights from IMF documentation during onboarding.

### 6.4 DataMapper API (simplified WEO access)

```
GET https://www.imf.org/external/datamapper/api/v1/{indicator}/{country}
```

JSON, no auth, scope limited to DataMapper datasets (primarily WEO).

---

## 7. Customer-Side Onboarding

None. IMF data is public; would be pre-loaded once readers are built.

---

## 8. BareCount-Side Onboarding

When the IMF executor exists, no per-tenant configuration is needed — IMF flavors would be platform-wide like ECB. Customer activation just binds their tenant to the platform-wide IMF SO streams they care about.

---

## 9. Verified Coverage

**Nothing.** No IMF executor exists; no IMF data has been admitted.

---

## 10. Known Gaps

1. **SDMX 2.1 / 3.0 executor** — separate from `EcbSdmxExecutor` (different envelope shape, 3.0 uses SDMX-JSON).
2. **DataMapper executor** — small REST adapter for WEO simplified queries.
3. **Attribution discipline at admission** — provenance must include IMF dataset ID + access timestamp to satisfy attribution requirement.
4. **Dataset-specific admission contracts** — each dataset (`IFS`, `WEO`, `BOP`, …) has its own dimension shape and would need a flavor-specific AC.
5. **Rate-limit handling** — informal limit (~10 req / 5s); the executor needs adaptive throttling.
6. **vendor-defined series-per-response cap** — query strategy must avoid hitting this for broad pulls.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Exchange Rate Reader Architecture (D043) | legacy-v2/docs/decisions/ADR-DEC-b10dad.md (pending v3 reconciliation) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| IMF Data Portal | https://data.imf.org |
| IMF API page | https://data.imf.org/en/Resource-Pages/IMF-API |
| IMF SDMX Central | https://sdmxcentral.imf.org/ |
| SDMX Central API Guide | https://dsbb.imf.org/content/pdfs/IMFSDMXCentralWebServicesGuide.pdf |
| IMF DataMapper API | https://www.imf.org/external/datamapper/api/help |
| IMF Terms of Use | https://www.imf.org/external/terms.htm |
| SDR daily valuation | https://www.imf.org/external/np/fin/data/rms_sdrv.aspx |
| Predecessor — legacy v2 archive IMF reference | legacy-v2/reference/sources/imf.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
