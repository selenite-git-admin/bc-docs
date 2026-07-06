---
uid: SRC-a7b2c5
slug: google-ads
title: "Google Ads"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: advertising
subdomain: google
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developers.google.com/google-ads/api/docs/release-notes
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/google-ads.md
---

# Google Ads

This page records BareCount's source-admission posture for Google Ads. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Google Ads OAuth 2.0 helper; no developer-token approval; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate: `google-ads-rest-v23`, `google-ads-grpc-v23`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Campaign structures (campaigns, ad groups, ad group ads, extensions, labels); audience definitions (remarketing lists, custom audiences, combined audiences, customer match lists); keyword and targeting criteria (keywords, placements, topics, demographics, locations); bidding strategy configurations and budget allocations; conversion action definitions and attribution models; account hierarchy (MCC structure, customer client links); asset definitions (images, videos, text assets, sitelinks, callouts).

### 3.2 Business data

| Domain | Objects |
|---|---|
| Campaign Performance | Impressions, clicks, conversions, cost, CTR, CPC, conversion rate, conversion value |
| Search | Search terms, keyword performance, quality scores, auction insights, search impression share |
| Display | Placement performance, topic targeting, managed placement metrics, viewability |
| Video / YouTube | Video views, view rate, earned actions, YouTube engagement metrics |
| Shopping | Product performance, product groups, Shopping campaign metrics |
| Audiences | Audience segment performance, remarketing list metrics |
| Geographic | Geographic performance by country/region/city/metro |
| Conversions | Conversion actions, conversion values, assisted conversions, attribution paths |
| Budget & Billing | Account budgets, campaign budget utilisation |
| Change History | Account change events, timestamps, authors |

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

### 6.1 API surfaces

| Surface | Use |
|---|---|
| Search API (REST + gRPC) | The primary integration surface — query reports + entity reads |
| Mutation API | Create/update entities (write) — out of scope for read-only admission |
| Streaming reports | Long-running paginated responses for large reports |

### 6.2 Endpoints

REST: `https://googleads.googleapis.com/v23/customers/{customer_id}/...`. gRPC: same versioned namespace.

### 6.3 Auth

OAuth 2.0 user-consent flow:
1. Customer authorises BareCount with `https://www.googleapis.com/auth/adwords` scope.
2. BareCount receives access + refresh tokens.
3. Calls include `developer-token` + `login-customer-id` (MCC) + `customer-id` (target account) headers.

### 6.4 Query language — GAQL

Google Ads Query Language — SQL-like:
```
SELECT campaign.id, campaign.name, metrics.impressions, metrics.clicks
FROM campaign
WHERE segments.date DURING LAST_30_DAYS
```

The executor builds GAQL from admission contract field-list + filter.

### 6.5 Pagination and incrementality

`page_token` cursor on `search`; `searchStream` returns chunks until exhausted. Incremental admission via `segments.date` filter (per-day granularity) plus `LAST_X_DAYS` macros.

### 6.6 Rate limits

Per-developer-token quota plus per-account QPM. HTTP 429 with `RETRY_AFTER` on excess. Quotas can be increased on request.

---

## 7. Customer-Side Onboarding

1. **BareCount-side prerequisite**: developer token approved by Google for production access (one-time).
2. Customer authorises BareCount via OAuth 2.0 consent flow.
3. Customer adds BareCount's MCC as a manager link (or links via BareCount's MCC).
4. Hand BareCount: customer ID(s), OAuth tokens.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'google_ads'`; `customer_ids[]` (target accounts); `mcc_id` (login customer); `auth.method: 'oauth2_google'`; `auth.credential_ref`; `developer_token_ref` — BareCount-wide platform credential. Smoke test: GAQL `SELECT customer.id FROM customer LIMIT 1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Google Ads developer token approval** — gate before any live admission.
2. **OAuth 2.0 helper** with Google's consent flow.
3. **GAQL builder + executor** — REST and/or gRPC.
4. **Streaming response handling** for large reports.
5. **Annual major-version migration** — admission contracts must declare API version, with a process for upgrading.
6. **MCC structure modeling** — customer accounts under BareCount's MCC; canonical mapping must distinguish.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Google Ads API release notes | https://developers.google.com/google-ads/api/docs/release-notes |
| Authentication | https://developers.google.com/google-ads/api/docs/oauth/overview |
| GAQL reference | https://developers.google.com/google-ads/api/docs/query/overview |
| Developer token | https://developers.google.com/google-ads/api/docs/get-started/dev-token |
| Predecessor — legacy v2 archive Google Ads reference | legacy-v2/reference/sources/google-ads.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
