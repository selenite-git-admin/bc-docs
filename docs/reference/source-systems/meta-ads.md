---
uid: SRC-a3f7e2
slug: meta-ads
title: "Meta Ads"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: advertising
subdomain: meta
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developers.facebook.com/docs/marketing-api
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/meta-ads.md
---

# Meta Ads

This page records BareCount's source-admission posture for Meta Ads. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no Meta OAuth 2.0 helper; no Meta App Review approval; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidates: `meta-ads-rest`, `meta-ads-insights`.

---

## 3. What BareCount Admits

### 3.1 Metadata

Ad Account configuration (currency, timezone, business association, spending limits); campaign structure definitions (campaign > ad set > ad hierarchy); campaign objectives and optimisation goals; audience definitions (custom, lookalike, saved); Pixel and Conversions API event configurations; Ad Creative assets (image hashes, video IDs, creative specs); product catalog schemas and feed configurations.

### 3.2 Business data

| Domain | Objects |
|---|---|
| Campaign Management | Campaigns, Ad Sets, Ads, Ad Creatives |
| Performance Metrics | Impressions, Reach, Clicks, CTR, CPC, CPM, Frequency |
| Spend and Budget | Spend, Daily Budget, Lifetime Budget, Budget Remaining |
| Conversions | Actions, Action Values, Cost Per Action, Conversions (pixel/CAPI events) |
| Revenue Attribution | Purchase ROAS, Website Purchase ROAS, Action Values by type |
| Audience | Custom Audiences, Lookalike Audiences, Audience size estimates |
| Creative Performance | Creative-level metrics, asset breakdowns (dynamic creative) |
| Catalog / Commerce | Product Catalog items, product sets, product-level ad performance |

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

Base URL: `https://graph.facebook.com/v22.0/` (or current major). All endpoints under `act_{ad_account_id}/...`.

### 6.2 Auth

OAuth 2.0 via Facebook Login for Business. Long-lived tokens (60 days) refreshable. App access tokens for system-level calls.

### 6.3 Insights API

The Insights API is the analytics surface:
```
GET /v22.0/act_{id}/insights?fields=impressions,clicks,spend,actions
   &time_range={since,until}
   &level=campaign|adset|ad
   &breakdowns=...
   &date_preset=last_30d
```

Async report jobs are required for large-volume historical pulls (`GET /act_{id}/insights?async=true`).

### 6.4 Pagination and incrementality

Cursor-based: `paging.cursors.after`. Incremental via `time_range` filter; combined with `time_increment=1` for daily granularity.

### 6.5 Rate limits

Per-app + per-ad-account hourly limits. HTTP 429 + headers (`X-Business-Use-Case-Usage`, `X-App-Usage`) for proactive backoff.

---

## 7. Customer-Side Onboarding

1. **BareCount prerequisite**: Meta App Review approval for Advanced Access (one-time gate).
2. Customer authorises BareCount via Facebook Login for Business consent.
3. Customer assigns Business Manager roles (Ads Reading) to BareCount's Business Manager.
4. Hand BareCount: ad account IDs, OAuth tokens, Business Manager ID.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'meta_ads'`; `ad_account_ids[]`; `business_manager_id`; `auth.method: 'oauth2_meta_facebook_login_business'`; `auth.credential_ref`; `api_version` — pinned major version. Smoke test: `GET /v22.0/act_{id}` returns the ad account.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Meta App Review approval** — gate before any live admission.
2. **Facebook Login for Business OAuth 2.0** auth method with long-lived token refresh.
3. **Meta Insights API executor** — async-job pattern for large historical pulls.
4. **Async report polling** — submit job, poll, retrieve.
5. **Major-version migration** — admission contract declares version; framework needs ~2-year upgrade cadence.
6. **Conversion attribution** — pixel + CAPI events; canonical mapping must distinguish click-through, view-through, and CAPI-attributed.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Meta Marketing API | https://developers.facebook.com/docs/marketing-api |
| Insights API | https://developers.facebook.com/docs/marketing-api/insights |
| App Review | https://developers.facebook.com/docs/app-review |
| Facebook Login for Business | https://developers.facebook.com/docs/facebook-login/facebook-login-for-business |
| Predecessor — legacy v2 archive Meta Ads reference | legacy-v2/reference/sources/meta-ads.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
