---
uid: SRC-b4c8d6
slug: linkedin-ads
title: "LinkedIn Ads"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: advertising
subdomain: linkedin
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://learn.microsoft.com/en-us/linkedin/marketing/overview
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/linkedin-ads.md
---

# LinkedIn Ads

This page records BareCount's source-admission posture for LinkedIn Ads. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no LinkedIn OAuth 2.0 helper; no Marketing Developer Platform approval; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `linkedin-ads-rest`, `linkedin-ads-analytics`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Ad account definitions; campaign group structures; campaign configurations; creative definitions; conversion rule definitions; audience segment definitions (matched audiences, DMP segments, predictive audiences, lookalikes); Lead Gen Form schemas; ad targeting facet catalog.

### 3.2 Business data

| Domain | Observations |
|---|---|
| Delivery | Impressions, reach, frequency, average dwell time, sends (messaging), opens |
| Engagement | Clicks, social actions (likes, comments, shares, follows), CTR, engagement rate |
| Video | Video views, completions, quartile completions |
| Spend | Total spend, CPC, CPM, cost per lead, cost per conversion |
| Conversions | External website conversions, post-click/post-view, one-click leads, conversion values |
| Leads | Lead Gen Form responses (submitted fields, timestamps, associated campaign/creative) |
| Revenue Attribution | CRM leads, pipeline value, revenue (Conversions API attributed metrics) |
| Demographics | Performance by company size, job function, job title, industry, seniority, country, region |

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

### 6.1 Endpoints

Base URL: `https://api.linkedin.com/rest/`. **`LinkedIn-Version` header mandatory** on every call (`YYYYMM`).

### 6.2 Auth

OAuth 2.0 (3LO) — customer consents per ad account. Required scopes: `r_ads`, `r_ads_reporting`, `r_basicprofile` (where applicable).

### 6.3 Pagination and incrementality

`start` + `count` (max 100) + `pageToken`. Incremental admission via `dateRange` start/end on analytics endpoints; campaign / creative metadata via `lastModified` filter.

### 6.4 Analytics endpoint

`GET /rest/adAnalytics?q=analytics&pivot=...&timeGranularity=DAILY&dateRange=...&campaigns=...`. Pivots: `CAMPAIGN`, `CREATIVE`, `CAMPAIGN_GROUP`, `MEMBER_COMPANY_SIZE`, etc.

### 6.5 Rate limits

Per-app + per-account daily limits. HTTP 429.

---

## 7. Customer-Side Onboarding

1. **BareCount prerequisite**: Marketing Developer Platform approval (one-time gate).
2. Customer authorises BareCount via OAuth 2.0 consent.
3. Customer's BareCount integration receives access tokens for the ad accounts in scope.
4. Hand BareCount: ad account IDs, OAuth tokens.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'linkedin_ads'`; `ad_account_ids[]`; `auth.method: 'oauth2_linkedin'`; `auth.credential_ref`; `linkedin_version` — pinned monthly release. Smoke test: `GET /rest/adAccounts/{id}` with the version header.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Marketing Developer Platform approval** — gate before any live admission.
2. **LinkedIn OAuth 2.0 (3LO)** auth method.
3. **`LinkedIn-Version` header pinning + monthly migration** — admission contract declares version; framework needs upgrade process.
4. **Analytics pivot model** — admission contract specifies pivot dimensions; canonical mapping handles pivot-aware aggregation.
5. **Lead Gen Form schemas** — per-customer custom forms; admission contract auto-discovery.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| LinkedIn Marketing API overview | https://learn.microsoft.com/en-us/linkedin/marketing/overview |
| API versioning | https://learn.microsoft.com/en-us/linkedin/marketing/versioning |
| OAuth 2.0 (3LO) | https://learn.microsoft.com/en-us/linkedin/shared/authentication/authorization-code-flow |
| Ad Analytics | https://learn.microsoft.com/en-us/linkedin/marketing/integrations/ads-reporting/ads-reporting |
| Predecessor — legacy v2 archive LinkedIn Ads reference | legacy-v2/reference/sources/linkedin-ads.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
