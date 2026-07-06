---
uid: SRC-f2d097
slug: world-bank
title: "World Bank Open Data"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: reference-data
subdomain: development
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/world-bank.md
---

# World Bank Open Data

This page records BareCount's source-admission posture for World Bank Open Data. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor built; no admission has occurred. The API surface is simple (REST + JSON, no auth) so the build cost is small once prioritised.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `world-bank-reader-wdi` — World Development Indicators (source ID 2, the flagship flagship indicator compilation).
- Additional flavors per source (`ids` for International Debt Statistics, `governance` for Worldwide Governance Indicators, `gender` for Gender Statistics, etc.) as use cases emerge.

All flavors emit the same SO structure: development indicator observation (country, indicator code, year, value, unit). Domain: `development/macro_indicators`.

---

## 3. What BareCount Would Admit

### 3.1 Metadata

| Category | Description |
|---|---|
| Countries and regions | 200+ economies with ISO 3166-1 codes, region, income level, lending type, capital, coordinates |
| Indicators | large coded indicator catalog with structured naming (`NY.GDP.MKTP.CD` = GDP, current US$) |
| Topics | 21 thematic groups (Economy, Poverty, Education, Health, etc.) |
| Sources | 42+ data source catalogues (WDI, IDS, Doing Business, Gender Statistics, etc.) |
| Income levels | High, Upper middle, Lower middle, Low |
| Lending types | IBRD, IDA, Blend |

### 3.2 Business data — priority indicators

| Code | Name | Domain |
|---|---|---|
| `NY.GDP.MKTP.CD` | GDP, current US$ | Economy |
| `NY.GDP.PCAP.CD` | GDP per capita, current US$ | Economy |
| `NY.GDP.MKTP.KD.ZG` | GDP growth, annual % | Economy |
| `FP.CPI.TOTL.ZG` | Inflation, consumer prices, annual % | Economy |
| `NE.TRD.GNFS.ZS` | Trade, % of GDP | Trade |
| `BX.KLT.DINV.WD.GD.ZS` | Foreign direct investment, net inflows, % of GDP | Finance |
| `SL.UEM.TOTL.ZS` | Unemployment, % of total labour force | Labour |
| `SP.POP.TOTL` | Total population | Demographics |
| `SP.URB.TOTL.IN.ZS` | Urban population, % of total | Demographics |
| `SP.DYN.LE00.IN` | Life expectancy at birth, years | Health |

### 3.3 Indicator coding convention

Three-part structure:

- **Prefix** — subject area (`NY` national accounts, `SP` social/population, `FP` financial/prices, `SE` education, `SH` health, `SI` social inclusion).
- **Middle** — specific subject (`GDP`, `POP`, `CPI`).
- **Suffix** — unit/modifier (`CD` current US$, `KD` constant US$, `ZS` % of total, `ZG` growth rate).

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

### 6.1 Indicators API v2 (primary)

| Attribute | Value |
|---|---|
| Base URL | `https://api.worldbank.org/v2/` |
| Protocol | REST over HTTPS |
| Auth | None |
| Default format | XML — use `?format=json` for JSON |
| Rate limits | None formal; generous |
| Pagination | `page` and `per_page` (default 50, max `per_page=32500`) |
| Max URL length | vendor-defined URL length limits |
| Max indicators per call | 60 (semicolon-separated) |
| Languages | `en`, `es`, `fr`, `ar`, `zh` |

### 6.2 Key endpoints

```
GET /v2/country?format=json&per_page=300
GET /v2/indicator?format=json&per_page=1000
GET /v2/country/{code}/indicator/{indicator_code}?format=json
GET /v2/country/all/indicator/{indicator_code}?format=json&date=2010:2023
GET /v2/topic/{topic_id}/indicator?format=json
GET /v2/source/{source_id}/indicator?format=json
```

### 6.3 Useful query parameters

| Parameter | Purpose |
|---|---|
| `date` | Year or range (`2020`, `2010:2023`) |
| `MRV` | Most-recent N values |
| `MRNEV` | Most-recent N non-empty values |
| `gapfill` | Back-fill gaps with `MRV` |
| `frequency` | `Y`, `M`, `Q` |
| `source` | Filter by source ID |
| `format` | `json` (use this) or `xml` |
| `per_page` | Vendor-defined maximum |

### 6.4 JSON response shape

Two-element array: `[0]` = pagination metadata (`page`, `pages`, `per_page`, `total`, `lastupdated`), `[1]` = data array. The executor must handle this dual-element shape.

---

## 7. Customer-Side Onboarding

None. World Bank data is fully public.

---

## 8. BareCount-Side Onboarding

Pre-loaded platform-wide once the reader exists. No per-tenant configuration.

---

## 9. Verified Coverage

**Nothing.** No reader, no admission.

---

## 10. Known Gaps

1. **REST executor with World Bank JSON-array shape handling** — BareCount has no generic REST executor in the readiness baseline; SAP DM and World Bank both need one (different shapes).
2. **`lastupdated` metadata propagation** — provenance must capture this so canonical resolution can detect data revisions.
3. **Bulk historical loader** — for initial seeding, CSV bulk download from Data Catalog is more efficient than walking the full indicator catalog across country history via API; design a one-shot bulk path.
4. **Indicator catalogue selection policy** — admitting the full indicator catalog is wasteful; need a scoped admission contract listing the indicators BareCount actually consumes.
5. **Refresh strategy** — WDI is updated annually with quarterly interim updates; the reader must align with this cadence.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Open Data Portal | https://data.worldbank.org/ |
| Developer overview | https://datahelpdesk.worldbank.org/knowledgebase/articles/889386-developer-information-overview |
| API v2 documentation | https://datahelpdesk.worldbank.org/knowledgebase/articles/889392-about-the-indicators-api-documentation |
| API basic call structures | https://datahelpdesk.worldbank.org/knowledgebase/articles/898581-api-basic-call-structures |
| Data Catalog | https://datacatalog.worldbank.org/ |
| Indicator coding system | https://datahelpdesk.worldbank.org/knowledgebase/articles/201175-how-does-the-world-bank-code-its-indicators |
| Terms of Use | https://data.worldbank.org/summary-terms-of-use |
| Predecessor — legacy v2 archive World Bank reference | legacy-v2/reference/sources/world-bank.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
