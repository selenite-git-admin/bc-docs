---
uid: SRC-f2a8b5
slug: manageengine
title: "ManageEngine ServiceDesk Plus"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: itsm
subdomain: manageengine
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.manageengine.com/products/service-desk/sdpod-v3-api/SDPOD-V3-API.html
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/manageengine.md
---

# ManageEngine ServiceDesk Plus

This page records BareCount's source-admission posture for ManageEngine ServiceDesk Plus. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for SDP REST v3; no ManageEngine auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `manageengine-sdp-cloud-v3` — REST against ServiceDesk Plus Cloud.
- `manageengine-sdp-onprem` — same protocol, on-premise endpoint with VPN / IP-allowlist plumbing.

---

## 3. What BareCount Admits

### 3.1 Metadata

Categories, subcategories, item definitions; technician groups and support groups; SLA definitions and escalation rules; CI Types and CMDB schema definitions.

### 3.2 Business data

| Domain | Objects |
|---|---|
| Incident / Request Management | Requests, worklogs, tasks, approvals, notes |
| Problem Management | Problems, analyses, associated requests |
| Change Management | Changes, change plans, approvals |
| CMDB | Configuration items, CI relationships |
| Asset Management | Assets, software licences |
| Contract Management | Contracts, renewals, associated assets |
| Purchase Management | Purchase orders, line items, vendors |

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

| Deployment | Base URL |
|---|---|
| Cloud (region-specific) | `https://sdpondemand.manageengine.com/api/v3/` (US), `.eu`, `.in`, `.com.au`, `.com.cn` |
| On-premise | `https://<your-server>:8080/api/v3/` |

### 6.2 Content type

`Content-Type: application/vnd.manageengine.sdp.v3+json` is mandatory for v3 — vanilla `application/json` is rejected.

### 6.3 Auth

- **Cloud**: OAuth 2.0 via Zoho Accounts (region-aware, similar to other Zoho products).
- **On-premise**: API authentication token in `authtoken` header or as query parameter.

### 6.4 Pagination and incrementality

`list_info` query parameter as JSON: `{"row_count": 100, "start_index": 1}`. Incremental admission via `last_updated_time` filter.

### 6.5 Rate limits

Cloud: per-organisation throttling; HTTP 429. On-premise: bounded by server capacity, not enforced limits.

---

## 7. Customer-Side Onboarding

1. **Cloud**: customer authorises BareCount via Zoho Accounts OAuth (region-appropriate).
2. **On-premise**: customer generates an API authentication token for a service-account technician with read-only permissions.
3. Network access: cloud is direct HTTPS; on-premise needs VPN or IP allowlist.
4. Hand BareCount: API base URL (region-specific or on-prem), API token (on-prem) or OAuth tokens (cloud).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'manageengine_sdp'`
- `deployment: 'cloud' | 'onprem'`
- `region` (cloud only)
- `endpoint_url` (on-prem)
- `auth.method: 'oauth2_zoho_authorization_code' | 'manageengine_authtoken'`
- `auth.credential_ref`

Smoke test: `GET /api/v3/requests?list_info={"row_count":1}` with the v3 content-type.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **ManageEngine REST v3 executor** with v3 content-type and `list_info` JSON pagination.
2. **OAuth 2.0 (Zoho Accounts)** — shared helper with Zoho Books / Zoho CRM / Zoho People.
3. **API token auth** for on-premise.
4. **Cloud vs on-prem** routing — connection profile must capture deployment type and region.
5. **CMDB schema discovery** — CI types are customer-defined; admission contract auto-discovery.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| ServiceDesk Plus Cloud v3 API | https://www.manageengine.com/products/service-desk/sdpod-v3-api/SDPOD-V3-API.html |
| On-premise API guide | https://www.manageengine.com/products/service-desk/help/adminguide/api/getting-started.html |
| Predecessor — legacy v2 archive ManageEngine reference | legacy-v2/reference/sources/manageengine.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
