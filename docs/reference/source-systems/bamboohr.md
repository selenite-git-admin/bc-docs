---
uid: SRC-c1e5a9
slug: bamboohr
title: "BambooHR"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: hcm
subdomain: bamboohr
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://documentation.bamboohr.com/docs
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/bamboohr.md
---

# BambooHR

This page records BareCount's source-admission posture for BambooHR. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for BambooHR REST; no BambooHR OAuth 2.0 helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `bamboohr-rest-v1.2` — primary integration surface.
- `bamboohr-webhook` — push notifications.

---

## 3. What BareCount Admits

### 3.1 Metadata

Employee field definitions and types (`GET /v1/meta/fields`); table definitions and field schemas (`GET /v1/meta/tables`); custom field definitions (company-specific); list field options (dropdowns, employment statuses, departments, locations); time-off policy and benefit plan definitions.

### 3.2 Business data

| Domain | Data |
|---|---|
| Employee Records | Demographics, employment details, org hierarchy, custom fields |
| Time Off | Requests, balances, accruals, policy assignments |
| Time Tracking | Timesheet entries, clock records, break data (meal/rest break policies added Feb 2026) |
| Benefits | Plan enrolments, deductions, dependents, ACA status |
| Compensation | Pay rates, pay history, bonus, commission |
| Hiring / ATS | Job summaries, applications, applicant statuses |
| Performance | Goals, goal status, assessments |
| Training | Training records, completion, due dates |

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

Base URL: `https://api.bamboohr.com/api/gateway.php/{companyDomain}/v1/` (or `/v1.2/`).

### 6.2 Auth

| Method | Use |
|---|---|
| API key + HTTP Basic | Legacy, single-tenant; key as username, `x` as password |
| OAuth 2.0 | Multi-tenant marketplace (replaces deprecated OpenID Connect) |

### 6.3 Pagination and incrementality

- v1: `start` + `limit` (max 250).
- v1.2 employees: cursor-based pagination.
- Incremental: `lastChanged` query parameter on supported endpoints; `Custom Reports` for arbitrary date ranges.

### 6.4 Webhooks

Configurable per company. POST to BareCount endpoint with payload + signature.

### 6.5 Rate limits

Documented as "reasonable use." HTTP 429 with `Retry-After`. No published per-minute limits.

---

## 7. Customer-Side Onboarding

1. Customer creates an API key (Settings → API Keys) or authorises via OAuth 2.0 marketplace flow.
2. Customer creates a service account user with read-only role for the data BareCount needs.
3. Hand BareCount: company domain, API key (or OAuth tokens).
4. Customer signs PII data-flow agreement.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'bamboohr'`
- `company_domain`
- `auth.method: 'api_key' | 'oauth2_bamboohr'`
- `auth.credential_ref`
- `pii_policy_ref`

Smoke test: `GET /v1/employees/directory` returns the directory.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **BambooHR REST executor** with v1.2 cursor pagination on the new employees endpoint.
2. **API key auth + OAuth 2.0** support.
3. **Webhook receiver** with signature verification.
4. **Custom Reports executor** — for arbitrary data shapes that go beyond standard endpoints.
5. **OpenID Connect deprecation (Apr 2025)** — confirm executor never references the OIDC path.
6. **PII data-flow agreement template** for HRIS sources (shared with Workday HCM, SuccessFactors).

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| BambooHR API documentation | https://documentation.bamboohr.com/docs |
| BambooHR OAuth 2.0 | https://documentation.bamboohr.com/docs/oauth-20 |
| BambooHR webhooks | https://documentation.bamboohr.com/reference/webhooks |
| Predecessor — legacy v2 archive BambooHR reference | legacy-v2/reference/sources/bamboohr.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
