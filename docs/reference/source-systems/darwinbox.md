---
uid: SRC-d2f6b1
slug: darwinbox
title: "Darwinbox"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: hcm
subdomain: darwinbox
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://api-docs.darwinbox.com/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/darwinbox.md
---

# Darwinbox

This page records BareCount's source-admission posture for Darwinbox. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor; no Darwinbox auth helper; no customer engagement; no Darwinbox technology-partnership relationship yet established.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `darwinbox-rest` — REST API once gated access is granted per customer.

---

## 3. What BareCount Admits

### 3.1 Metadata

Company / business unit hierarchy, departments, designations; grades and bands, office locations; pay components (salary structure definitions); custom sections and fields (text, dropdown, checkbox, number, rating); leave policies, attendance policies, shift definitions.

### 3.2 Business data

| Domain | Data |
|---|---|
| Core HR | Employee profiles, dependents, assets, education, employment history |
| Attendance | Clock-in/out (biometric, GPS, geofencing), shifts, timesheets, overtime |
| Leave | Balances, requests, approvals, holiday calendars |
| Payroll | Payslips, salary structures, tax computations, statutory deductions |
| Performance | Goals, appraisal cycles, 360-degree feedback, ratings |
| Recruitment | Job requisitions, candidate profiles, interview schedules, offers |
| Learning | Course assignments, completions, skill assessments |
| Expenses | Claims, approval workflows |

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

### 6.1 API surface

REST API — covers core HR, attendance, leave, payroll, performance, recruiting, learning, expenses (per the customer's enabled module set).

### 6.2 Authentication

OAuth 2.0 client credentials issued by Darwinbox during the enablement process. Specifics are documented in `api-docs.darwinbox.com` once the customer has access; not entirely public.

### 6.3 Endpoints

Base URL pattern: `https://{customer-instance}.darwinbox.in/api/` (or `darwinbox.com` for non-IN tenants).

### 6.4 Pagination and incrementality

Pagination supported on list endpoints. Incremental admission via `modified_since` parameter where exposed.

### 6.5 Rate limits

Not publicly documented. Darwinbox enforces fair-use; HTTP 429 expected on excess.

---

## 7. Customer-Side Onboarding

1. Customer engages Darwinbox integrations team (`integrationsteam@darwinbox.in`) to enable API access for their instance.
2. Darwinbox issues OAuth 2.0 credentials to the customer.
3. Customer scopes the credentials to read-only modules.
4. Customer signs PII data-flow agreement with BareCount.
5. Hand BareCount: instance URL, OAuth credentials, list of enabled modules.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'darwinbox'`
- `instance_url`
- `auth.method: 'oauth2_darwinbox_client_credentials'`
- `auth.credential_ref`
- `enabled_modules[]`
- `pii_policy_ref`

Smoke test: a small employee-list call confirming auth.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Darwinbox REST executor**.
2. **Darwinbox OAuth 2.0 client credentials** auth method.
3. **Darwinbox technology-partnership status** — pursue when customer count justifies; would streamline customer enablement.
4. **Public API documentation gaps** — Darwinbox docs are partially gated; per-customer onboarding may surface schemas that need catalogue auto-discovery.
5. **PII data-flow agreement template** for HCM sources (shared with Workday HCM, SuccessFactors, BambooHR, greytHR, Zoho People).

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Darwinbox API documentation (gated) | https://api-docs.darwinbox.com/ |
| Darwinbox product | https://darwinbox.com/ |
| Predecessor — legacy v2 archive Darwinbox reference | legacy-v2/reference/sources/darwinbox.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
