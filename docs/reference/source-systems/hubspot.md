---
uid: SRC-b7d2f4
slug: hubspot
title: "HubSpot"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: crm
subdomain: hubspot
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developers.hubspot.com/docs/api-reference/latest/overview
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/hubspot.md
---

# HubSpot

This page records BareCount's source-admission posture for HubSpot. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for HubSpot REST; no HubSpot OAuth 2.0 / Private App helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `hubspot-rest-v3` — current REST API v3.
- `hubspot-search` — CRM Search API for filtered queries with sort.
- `hubspot-webhook` — push notifications.

---

## 3. What BareCount Admits

### 3.1 Metadata

Object definitions and property schemas via Properties API; pipeline and stage definitions; owner and team assignments; custom object schemas and custom property definitions; association type definitions; form definitions and field configurations.

### 3.2 Business data

| Domain | Objects |
|---|---|
| CRM Core | Contacts, Companies, Deals, Tickets |
| Sales | Line Items, Products, Quotes, Meetings, Calls, Tasks |
| Marketing | Forms, Marketing Emails, Lists, Campaigns |
| Service | Tickets, Knowledge Base Articles, Feedback Submissions |
| Commerce | Products, Line Items, Quotes, Carts |
| Activities (Engagements) | Notes, Emails, Calls, Meetings, Tasks |
| Custom | Custom Objects (schema auto-discovered) |

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

### 6.1 Versioning

| Surface | Status |
|---|---|
| `/crm/v3/...` | Current numeric versioning |
| `/{date}/...` (e.g. `/2026-03/`) | New date-based versioning rolling out per resource |

The executor must support both styles per-resource. Resources migrate independently.

### 6.2 Auth

| Method | Use |
|---|---|
| Private App access tokens | Single-tenant integrations (most direct customers) |
| OAuth 2.0 | Multi-tenant marketplace apps |

Private App tokens are static, scoped, and tenant-bound. OAuth tokens require refresh.

### 6.3 Pagination, search, filters

- List endpoints: `limit` (max 100) + `after` cursor.
- CRM Search API: POST `/crm/v3/objects/{type}/search` — supports filter groups, sort, paginated results (vendor-defined result-window limit requiring filter splitting for broad pulls).
- Incremental admission: filter on `hs_lastmodifieddate`.

### 6.4 Webhooks

Subscription via app settings. HMAC verification (`X-HubSpot-Signature-V2`). Events: `contact.creation`, `contact.propertyChange`, `deal.creation`, etc.

### 6.5 Rate limits

| Limit | Value |
|---|---|
| Private App | 110 req / 10s |
| OAuth app | 100 req / 10s per portal |
| Daily | vendor-defined daily call limit by subscription and add-on |
| Throttle | HTTP 429 with `Retry-After` |

---

## 7. Customer-Side Onboarding

1. Customer creates a Private App in Settings → Integrations → Private Apps.
2. Configures scopes: `crm.objects.contacts.read`, `crm.objects.deals.read`, etc.
3. Generates the access token and shares with BareCount.
4. (Or uses BareCount's marketplace OAuth flow.)

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'hubspot'`
- `portal_id`
- `auth.method: 'private_app_token' | 'oauth2_hubspot'`
- `auth.credential_ref`

Smoke test: `GET /crm/v3/objects/contacts?limit=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **HubSpot REST executor** with versioning-aware path handling (numeric v3 vs date-based).
2. **Private App token + OAuth** auth methods — both needed.
3. **CRM Search API executor** for filtered + sorted reads beyond simple list.
4. **Webhook receiver** with HMAC verification.
5. **Lists API v3 migration** — confirm executor never references v1 endpoint (sunset April 30 2026).
6. **Custom object discovery** — Properties API per object type.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| HubSpot API overview | https://developers.hubspot.com/docs/api-reference/latest/overview |
| Private Apps | https://developers.hubspot.com/docs/api/private-apps |
| OAuth 2.0 | https://developers.hubspot.com/docs/api/oauth-quickstart-guide |
| CRM Search API | https://developers.hubspot.com/docs/api/crm/search |
| Webhooks | https://developers.hubspot.com/docs/api/webhooks |
| Predecessor — legacy v2 archive HubSpot reference | legacy-v2/reference/sources/hubspot.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
