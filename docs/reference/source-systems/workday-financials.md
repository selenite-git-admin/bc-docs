---
uid: SRC-w4d001
slug: workday-financials
title: "Workday Financial Management"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: draft
domain: enterprise-erp
subdomain: workday
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://community.workday.com/api-reference
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/workday-financials.md
---

# Workday Financial Management

This page records BareCount's source-admission posture for Workday Financial Management. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented from public references; no reader executor; no Workday auth helper (Integration System User credentials, OAuth 2.0); no customer engagement.

This page is `status: draft` (rather than `published`) — the v2 source was a stub and the v3 content has not been validated against a real Workday tenant.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `workday-rest` — Workday REST API (modern surface, growing coverage).
- `workday-soap` — SOAP web services (full coverage; mature, production-grade for many integrations).
- `workday-raas` — Reports-as-a-Service custom report execution for arbitrary data shapes.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of Accounts (Accounting Worktag); ledgers and ledger periods; companies (legal entities); cost centres / business units / programmes / projects (worktags); currencies and exchange rates; supplier and customer master records; tax authorities and codes.

### 3.2 Business data

| Domain | Workday objects |
|---|---|
| General Ledger | Journal Source, Journal Lines, Accounting Worktag |
| Accounts Payable | Supplier Invoices, Supplier Invoice Adjustments, Supplier Payments |
| Accounts Receivable | Customer Invoices, Customer Payments |
| Procurement | Purchase Orders, Receipts |
| Cash | Bank Accounts, Bank Statements |
| Fixed Assets | Asset Records, Depreciation |
| Projects | Project Plans, Project Transactions |

Workday's universal pattern: business objects are queried via SOAP `Get_*` operations or REST endpoints (where available); RaaS custom reports cover anything not in the public API surface.

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
| REST API | Modern surface, growing coverage; per-resource OAuth 2.0 |
| SOAP web services | Full coverage; ISU credentials with WS-Security UsernameToken |
| RaaS (Reports-as-a-Service) | Custom report executed via authenticated URL; output JSON/XML/CSV |

For Financials specifically, **RaaS is often the most pragmatic** path because it covers any custom report a customer's Finance team has already built.

### 6.2 Authentication

- **OAuth 2.0** for REST: requires Workday-issued client ID/secret per tenant; refresh-token flow.
- **WS-Security UsernameToken** for SOAP: ISU username + password, scoped to a tenant URL.
- **RaaS basic auth** for custom report URLs: ISU credentials.

### 6.3 Endpoints

REST base: `https://<tenant-host>.workday.com/ccx/api/v1/<service>/`
SOAP endpoints: `https://<tenant-host>.workday.com/ccx/service/<tenant>/<Service>/<version>`
RaaS reports: `https://<tenant-host>.workday.com/ccx/service/customreport2/<tenant>/<owner>/<report-name>?format=json`

### 6.4 Pagination and incrementality

REST: cursor pagination per resource. SOAP: `Response_Filter` with `Page` + `Count`. RaaS: report-driven.

For incremental admission: Workday objects expose a `Last_Updated_Date` parameter; admission contract sets the watermark.

---

## 7. Customer-Side Onboarding

1. Customer's Workday administrator creates an **Integration System User (ISU)** for BareCount.
2. Assigns a domain security policy with **read-only access** to the modules in scope.
3. (For OAuth 2.0 REST path) Registers a Workday-issued OAuth client and shares client ID/secret.
4. (For SOAP / RaaS) Provides ISU credentials and tenant URL.
5. (For RaaS) Customer's Finance team builds custom reports for the data shapes BareCount needs and shares the report URLs.
6. Hand BareCount: tenant host, tenant name, ISU credentials and/or OAuth client credentials, list of authorised RaaS report URLs.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'workday_financials'`
- `tenant_host`, `tenant_name`
- `auth.method: 'workday_oauth2' | 'workday_isu_basic'`
- `auth.credential_ref`
- `raas_reports[]` — list of authorised report URLs

Smoke test: `GET /ccx/api/v1/common/v1/workers?limit=1` (REST) or a small `Get_Companies` SOAP call.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **v2 source page was a stub.** This v3 page is drafted from public references; needs cold-read by someone with first-hand Workday integration experience.
2. **Workday OAuth 2.0 helper** in `CredentialResolverService`.
3. **WS-Security UsernameToken signing** for SOAP — not in the readiness baseline in `CredentialResolverService`.
4. **SOAP executor** — BareCount has no SOAP executor in the readiness baseline.
5. **RaaS report adapter** — admit JSON/XML/CSV from customer-defined report URLs.
6. **Worktag model** — Workday's flexible accounting dimensions need careful canonical mapping per customer.
7. **First-hand verification** — no real Workday tenant has been observed.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion source page | [Workday HCM](workday-hcm.md) |
| Workday Community API reference | https://community.workday.com/api-reference |
| Reports-as-a-Service overview | https://community.workday.com/sites/default/files/file-hosting/restapi/index.html |
| Predecessor — legacy v2 archive Workday Financials reference | legacy-v2/reference/sources/workday-financials.md (stub) |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
