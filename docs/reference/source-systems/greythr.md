---
uid: SRC-a3f7c1
slug: greythr
title: "greytHR"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: hcm
subdomain: greythr
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://api-docs.greythr.com/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/greythr.md
---

# greytHR

This page records BareCount's source-admission posture for greytHR. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for greytHR REST; no greytHR auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `greythr-rest-v2` — primary integration surface.

---

## 3. What BareCount Admits

### 3.1 Metadata

Organisational structure (departments, locations, divisions, cost centres); designations and grades, employee categories; pay components (basic, HRA, DA, allowances, deductions); leave types, attendance policies, shift definitions; List of Values (LOV — banks, branches, relation types, identity codes).

### 3.2 Business data

| Domain | Objects |
|---|---|
| Employee master | Profiles, addresses, bank details, family, identity documents, assets |
| Attendance | Daily muster, swipe data, attendance summaries |
| Leave | Balances (by year), transactions (applied / approved / rejected) |
| Payroll | Monthly salary statements, hand-entry items, salary revisions, loans, pay periods |
| Statutory compliance | PF, ESI, PT, TDS, LWF deductions, Form 16 |
| Documents | Employee document categories and files |

### 3.3 Out of scope

- Performance review content (ratings, goals) — not exposed via public API.
- Recruitment / applicant tracking — not exposed via public API.
- Biometric device raw feeds — only surfaced swipe data.

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

Base URL: `https://api.greythr.com/v2/`. Tenant scoping via `X-Greythr-Domain` header (customer's greytHR subdomain).

### 6.2 Auth

API key issued from Settings → API Settings, sent as `Authorization: Bearer <key>` (or `X-API-Key` per documentation; verify per tenant).

### 6.3 Pagination and incrementality

`page` + `size` parameters. Incremental admission via `modified_after` parameter where supported; otherwise full snapshot + diff.

### 6.4 Rate limits

Not publicly published. HTTP 429 with `Retry-After`.

---

## 7. Customer-Side Onboarding

1. Customer confirms Enterprise plan or has purchased the API add-on.
2. Customer generates API key in Settings → API Settings, scoped to read-only.
3. Customer signs PII data-flow agreement with BareCount.
4. Hand BareCount: greytHR subdomain, API key.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'greythr'`
- `tenant_subdomain`
- `auth.method: 'greythr_api_key'`
- `auth.credential_ref`
- `pii_policy_ref`

Smoke test: `GET /v2/employees?size=1` confirming auth + tenant.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **greytHR REST executor**.
2. **API key auth** method in `CredentialResolverService` (header-based, simple).
3. **Customer plan-gating onboarding check** — onboarding flow must verify Enterprise / API add-on before activation.
4. **PII data-flow agreement template** for HCM sources (shared).
5. **Statutory module versioning** — Indian payroll statutory schemas evolve (Form 16, PF/ESI changes); admission contract must track which year's schema applies.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| greytHR API docs | https://api-docs.greythr.com/ |
| greytHR product | https://www.greythr.com/ |
| Predecessor — legacy v2 archive greytHR reference | legacy-v2/reference/sources/greythr.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
