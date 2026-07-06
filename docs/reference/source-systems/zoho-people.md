---
uid: SRC-d5f9b3
slug: zoho-people
title: "Zoho People"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: hcm
subdomain: zoho
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.zoho.com/people/api/overview.html
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/zoho-people.md
---

# Zoho People

This page records BareCount's source-admission posture for Zoho People. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Zoho People REST; no Zoho OAuth 2.0 helper with multi-region support (shared gap with Zoho Books / Zoho CRM); no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `zoho-people-rest` — form-based REST API.
- `zoho-people-webhook` — push notifications via workflow rules.

---

## 3. What BareCount Admits

### 3.1 Metadata

Departments, designations, locations; custom forms and custom field definitions; employee statuses and employment types; shift configurations and leave type definitions; roles and permission profiles; organisation settings.

### 3.2 Business data

| Domain | Data |
|---|---|
| Employees | Personal details, employment details, job history, reporting hierarchy, compensation |
| Attendance | Check-in / check-out, regularisation, shift overrides, overtime |
| Leave | Requests, approvals, balances, leave type allocations |
| Timesheets | Time logs, jobs, projects, clients, billable / non-billable hours |
| Performance | Appraisal cycles, self / manager / peer reviews, competency ratings |
| Goals | Goal definitions, key results, progress tracking |
| Cases | HR queries / tickets, SLA tracking, resolution status |

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

### 6.1 Region-specific base URLs (8 data centres)

Same pattern as Zoho Books / Zoho CRM:

| Region | Base URL |
|---|---|
| US | `https://people.zoho.com/people/api/` |
| EU | `https://people.zoho.eu/people/api/` |
| India | `https://people.zoho.in/people/api/` |
| Australia | `https://people.zoho.com.au/people/api/` |
| Japan | `https://people.zoho.jp/people/api/` |
| Canada | `https://people.zoho.ca/people/api/` |
| Saudi Arabia | `https://people.zoho.sa/people/api/` |
| China | `https://people.zoho.com.cn/people/api/` |

### 6.2 Form-based pattern

Zoho People organises records by **form** — every entity (employee, leave, attendance, etc.) is a form, and reads/writes use form-specific endpoints:
```
GET /forms/{formLinkName}/getRecords
GET /forms/{formLinkName}/getRecordByID/{id}
```

Custom forms (built by the customer) are admitted via the same endpoints with the customer's form link name.

### 6.3 Auth

OAuth 2.0 (shared with Zoho Books / Zoho CRM): authorization code flow, region-specific token endpoint.

### 6.4 Pagination and incrementality

`sIndex` + `limit` (max 200). Incremental admission via `modifiedTime` filter on form records.

### 6.5 Rate limits

Per-minute threshold limits (~100 req/min/org typical). Daily limits apply but are typically generous for HCM volume.

---

## 7. Customer-Side Onboarding

1. Customer registers a Zoho API Console application (region-appropriate).
2. Configures scopes: `ZohoPeople.employee.READ`, `ZohoPeople.attendance.READ`, etc.
3. OAuth consent flow → BareCount receives access + refresh tokens.
4. Customer signs PII data-flow agreement.
5. Hand BareCount: tokens, region, list of forms in scope.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'zoho_people'`
- `region`
- `auth.method: 'oauth2_zoho_authorization_code'` (shared with Zoho Books / Zoho CRM)
- `auth.credential_ref`
- `forms_in_scope[]`
- `pii_policy_ref`

Smoke test: `GET /forms/employee/getRecords?limit=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Shared Zoho OAuth 2.0 helper** with multi-region (consolidates with Zoho Books and Zoho CRM gaps — one helper serves all three).
2. **Form-based REST executor** with `formLinkName` routing.
3. **Custom form discovery** — admission contract design must enumerate which forms (standard + custom) are in scope.
4. **PII data-flow agreement template** for HCM sources (shared).
5. **Webhook receiver**.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Zoho People API overview | https://www.zoho.com/people/api/overview.html |
| OAuth 2.0 | https://www.zoho.com/people/api/auth.html |
| Forms reference | https://www.zoho.com/people/api/forms.html |
| Predecessor — legacy v2 archive Zoho People reference | legacy-v2/reference/sources/zoho-people.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
