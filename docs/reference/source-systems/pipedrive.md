---
uid: SRC-e6a1c5
slug: pipedrive
title: "Pipedrive"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: crm
subdomain: pipedrive
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developers.pipedrive.com/docs/api/v1
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/pipedrive.md
---

# Pipedrive

This page records BareCount's source-admission posture for Pipedrive. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Pipedrive REST; no Pipedrive OAuth 2.0 helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `pipedrive-rest-v2` — REST API v2 with v1 fallback only for the leads/notes/files endpoints not yet migrated.
- `pipedrive-webhook` — push notifications.

---

## 3. What BareCount Admits

### 3.1 Metadata

Pipeline definitions (names, stages, stage order, probability percentages); custom field schemas for deals, persons, organizations, products; activity type definitions (call, meeting, email, task, custom); lead label and lead source definitions; product fields and variation structures.

### 3.2 Business data

| Entity | Domain |
|---|---|
| Deals | Revenue pipeline — value, currency, stage, win/loss status, expected close date |
| Persons | Contact master |
| Organizations | Account master |
| Activities | Sales engagement — calls, meetings, emails, tasks tied to deals/persons/orgs |
| Products | Product catalog with multi-currency prices and variations |
| Leads | Pre-pipeline qualification |
| Notes | HTML-formatted text attached to entities |

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

- v2 (primary): `https://api.pipedrive.com/api/v2/`
- v1 (legacy, sunset Jul 31 2026): `https://api.pipedrive.com/v1/`
- Per-company: `https://{company-domain}.pipedrive.com/api/v2/` is also accepted for company-bound integrations.

### 6.2 Auth

- **OAuth 2.0** (preferred for marketplace apps): authorization code flow → access + refresh tokens.
- **API token** (Settings → Personal preferences → API): single static token per user. Use only for single-tenant internal integrations.

### 6.3 Pagination and incrementality

v2 uses cursor-based pagination (`cursor` + `next_cursor`). Incremental admission via `update_time` filter on the search endpoints.

### 6.4 Webhooks

Configured per integration. Verification via signature header. Events: `*.added`, `*.updated`, `*.deleted` for major entities.

### 6.5 Rate limits

| Limit | Value |
|---|---|
| Per second | 80 (across the company) |
| Per minute | vendor-defined company-level quota |
| Throttle | HTTP 429 with `Retry-After` |

Custom field operations and bulk endpoints have their own sub-limits.

---

## 7. Customer-Side Onboarding

1. Customer authorises BareCount via OAuth 2.0 marketplace flow (preferred) or generates an API token (single-tenant).
2. BareCount stores access + refresh tokens (or API token) and the company domain.
3. Customer ensures BareCount integration is on Lite plan or higher (no Free tier exists; trial accounts are temporary).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'pipedrive'`
- `company_domain`
- `auth.method: 'oauth2_pipedrive_authorization_code' | 'api_token'`
- `auth.credential_ref`

Smoke test: `GET /api/v2/users/me` → confirms auth + company.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Pipedrive REST executor** — v2-first with v1 fallback only for not-yet-migrated endpoints (leads, notes, files).
2. **OAuth 2.0 helper + API token method** — both auth methods for the executor.
3. **Cursor-pagination handling** for v2.
4. **Webhook receiver** with signature verification.
5. **v1 sunset deadline (Jul 31 2026)** — must validate no executor code references v1 paths past that date for in the readiness baseline-migrated endpoints.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Pipedrive Developers | https://developers.pipedrive.com/ |
| API v2 docs | https://developers.pipedrive.com/docs/api/v1/getting-started |
| OAuth 2.0 | https://pipedrive.readme.io/docs/marketplace-oauth-authorization |
| Webhooks | https://pipedrive.readme.io/docs/guide-for-webhooks |
| Predecessor — legacy v2 archive Pipedrive reference | legacy-v2/reference/sources/pipedrive.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
