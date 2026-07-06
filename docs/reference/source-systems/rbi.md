---
uid: SRC-5e8b12
slug: rbi
title: "Reserve Bank of India (RBI)"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: reference-data
subdomain: india-macro
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://data.rbi.org.in/DBIE/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-b10dad   # D043 — Exchange Rate Reader Architecture (RBI/FBIL is a candidate flavor)
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/rbi.md
---

# Reserve Bank of India (RBI)

This page records BareCount's source-admission posture for Reserve Bank of India (RBI). It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

What this means concretely:

- Architecture and access channels documented.
- No reader executor built. The multi-channel nature (CSV + JSON API + scraping) means a single executor will not suffice — each channel needs adaptation.
- No customer or internal data flow exercised.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `exchange-rate-reader-rbi` — INR reference rates, primary path via `data.gov.in` REST API; fallback via DBIE CSV or FBIL scrape.
- `monetary-policy-reader-rbi` — repo, reverse repo, MSF, bank rate, SDF rate, CRR, SLR.
- `banking-statistics-reader-rbi` — Weekly Statistical Supplement (WSS) parse plus DBIE bulk loads.

Per D043, the `rbi` flavor of `exchange_rate_reader` carries INR pairs. The non-currency readers are separate.

---

## 3. What BareCount Would Admit

### 3.1 Metadata

Currency pair definitions (USD/INR, EUR/INR, GBP/INR, JPY/INR); rate-type identifiers (FBIL benchmark, repo, CRR, SLR); publication-schedule metadata (daily exchange rates by 13:30 IST; bi-monthly MPC; weekly WSS); data series identifiers from DBIE.

### 3.2 Business data

| Category | Data | Frequency |
|---|---|---|
| Reference exchange rates | USD/INR, EUR/INR, GBP/INR, JPY/INR via FBIL | Daily by 13:30 IST, working days |
| FBIL benchmark rates | Overnight MIBOR, FBIL-SORR, T-bill yields | Daily |
| Monetary policy rates | Repo, reverse repo, MSF, bank rate, SDF | On MPC decision (bi-monthly) |
| Reserve ratios | CRR, SLR | On policy change |
| Inflation | CPI, WPI | Monthly |
| Money supply | M0, M1, M2, M3 | Weekly / fortnightly |
| Banking statistics | Aggregate deposits, bank credit, sectoral deployment | Weekly (WSS) / monthly |
| Balance of payments | Current account, capital account, forex reserves | Quarterly |
| Government securities | G-Sec yields, T-bill auctions, SDL valuations | Daily / weekly |

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

### 6.1 Access channels

| Channel | URL | Format | Auth | Programmatic |
|---|---|---|---|---|
| DBIE Portal | `https://data.rbi.org.in/DBIE/` | CSV, Excel, PDF | None | Manual download |
| RBI Statistics | `https://www.rbi.org.in/Scripts/Statistics.aspx` | HTML, PDF | None | Scraping |
| RBI Reference Rate Archive | `https://www.rbi.org.in/scripts/referenceratearchive.aspx` | HTML | None | Scraping |
| Weekly Statistical Supplement | `https://wss.rbi.org.in/` | HTML, PDF | None | Scraping |
| FBIL website | `https://www.fbil.org.in/` | HTML | None | Scraping (free, 7-day delayed) |
| FBIL API | Contact FBIL | JSON | Paid subscription | REST API |
| FBIL SFTP | Contact FBIL | CSV | Paid subscription | SFTP pull |
| `data.gov.in` API | `https://www.data.gov.in/apis/` | JSON | API key (free) | REST API |

### 6.2 Recommended approach (per channel)

1. **Exchange rates (priority):** `data.gov.in` API — free programmatic, JSON, key-required. Fall back to DBIE CSV for historical backfill or FBIL website scrape for gaps.
2. **Monetary policy rates:** scrape RBI press releases or DBIE CSV exports. Low frequency (~6 times/year) makes manual seeding viable initially.
3. **Banking statistics:** parse Weekly Statistical Supplement (vendor-defined table set, weekly). DBIE CSV bulk for historical.
4. **FBIL real-time (deferred):** if explicitly needed, FBIL API subscription is the most reliable path.

### 6.3 Comparison with ECB

| Dimension | ECB | RBI / FBIL |
|---|---|---|
| Programmatic API | SDMX REST (free, open) | No public REST from DBIE; `data.gov.in` for select datasets |
| Auth | None | None (DBIE), API key (`data.gov.in`), paid (FBIL API) |
| Format | SDMX XML | CSV / Excel (DBIE), JSON (`data.gov.in`), HTML (sites) |
| Real-time | Same-day (~16:00 CET) | Same-day (~13:30 IST via FBIL) |
| Base currency | EUR | INR |
| Complexity | Low | Medium (multi-channel) |

---

## 7. Customer-Side Onboarding

None. RBI / FBIL data is public.

The `data.gov.in` API key is generated by BareCount under its own developer account; not a per-customer credential.

---

## 8. BareCount-Side Onboarding

Same pattern as ECB — pre-loaded platform-wide once readers exist.

---

## 9. Verified Coverage

**Nothing.** No RBI executor; no admission has occurred.

---

## 10. Known Gaps

1. **No reader executor.** Three executors needed (`data.gov.in` REST, FBIL HTML scrape, WSS HTML/PDF parse) plus one CSV-bulk loader for DBIE historical backfill.
2. **Scraping fragility.** RBI website HTML structure changes break scrapers; need robust selectors plus alerting.
3. **FBIL terms** — redistribution constraints need explicit legal handling if BareCount ever consumes paid feed.
4. **Holiday calendar.** Indian banking holidays differ from ECB; the daily scheduler must consult the RBI calendar to distinguish "no rate in the readiness baseline" from "rate missing."
5. **DBIE URL change** (June 2024) — any old code or third-party dependency referencing `dbie.rbi.org.in` must be updated to `data.rbi.org.in/DBIE/`.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Exchange Rate Reader Architecture (D043) | legacy-v2/docs/decisions/ADR-DEC-b10dad.md (pending v3 reconciliation) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| DBIE Portal (current URL) | https://data.rbi.org.in/DBIE/ |
| RBI Statistics | https://www.rbi.org.in/Scripts/Statistics.aspx |
| RBI Reference Rate Archive | https://www.rbi.org.in/scripts/referenceratearchive.aspx |
| Weekly Statistical Supplement | https://wss.rbi.org.in/ |
| FBIL Reference Rates | https://www.fbil.org.in/ |
| `data.gov.in` Exchange Rates dataset | https://www.data.gov.in/catalog/exchange-rate-rupee-vis-vis-selected-currencies-world |
| `data.gov.in` API access | https://www.data.gov.in/apis/ |
| Predecessor — legacy v2 archive RBI reference | legacy-v2/reference/sources/rbi.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
