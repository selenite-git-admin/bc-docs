---
uid: SRC-f3a6b9
slug: gep
title: "GEP SMART"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: procurement
subdomain: gep
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://api.gep.com/gep-smart/gep-rest-apis
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/gep.md
---

# GEP SMART

This page records BareCount's source-admission posture for GEP SMART. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

No reader executor; no GEP-Azure JWT auth helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate: `gep-smart-rest` — REST against the gated API surface.

---

## 3. What BareCount Admits

### 3.1 Metadata

Organisation entities, supplier master records, category taxonomy (UNSPSC / custom, up to 5 levels); user and role definitions, catalog item definitions, workflow / approval rule definitions; contract templates and clause libraries.

### 3.2 Business data

| Domain | Objects |
|---|---|
| Requisitions | PR headers, line items, approval status, cost centre allocation |
| Purchase Orders | PO headers, line items, delivery schedules, receipts, status lifecycle |
| Invoices | Invoice headers, line items, PO matching results, payment status |
| Contracts | Contract headers, terms, clauses, milestones, compliance status |
| Sourcing Events | RFx events, bid responses, evaluation scorecards, award decisions |
| Spend Analytics | Classified spend records, spend cube dimensions |
| Suppliers | Profiles, onboarding status, performance scorecards, risk assessments |
| Savings Tracking | Savings projects, negotiated / realised savings, cost avoidance |

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

Tenant-specific: `https://<tenant>.api.gepsmart.com/` or `api.gep.com` umbrella with tenant query parameters. Specifics provided during onboarding.

### 6.2 Auth

JWT with **client certificate** (mTLS) — Azure-based. Customer provisions BareCount as an Azure AD app registration with cert-based auth, or GEP issues a tenant-specific cert.

### 6.3 Pagination and incrementality

Documented in gated portal. Standard offset / cursor pagination. Incremental admission via `modified_since` filters.

### 6.4 GEP QUANTUM Agentic Integration

200+ pre-built connectors with AI-powered data mapping. Where applicable, BareCount could potentially admit data **via QUANTUM connectors** rather than directly via the REST API — but this is a per-customer decision and may have its own licensing.

---

## 7. Customer-Side Onboarding

1. Customer engages GEP onboarding to provision API access for BareCount.
2. Customer registers BareCount as an Azure AD app with cert-based auth, or GEP issues a tenant-specific cert.
3. Hand BareCount: tenant URL, client certificate, scopes / module access.

---

## 8. BareCount-Side Onboarding

Connection profile: `system_type_code: 'gep_smart'`; `tenant_url`; `auth.method: 'azure_jwt_mtls'`; `auth.credential_ref` (client cert). Smoke test: a small list call against an activated module.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **mTLS / client cert auth** — not yet a first-class method on `ResolvedCredentials` (shared with SAP S/4 cloud gap).
2. **Azure JWT-with-cert helper** — distinct from generic OAuth client credentials.
3. **GEP REST executor** — gated documentation makes per-tenant schema discovery important.
4. **QUANTUM connector path** — alternative admission path; needs evaluation.
5. **Schema-discovery dependency** — admission contract design largely per-customer until BareCount has GEP partnership status.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| GEP REST APIs (gated) | https://api.gep.com/gep-smart/gep-rest-apis |
| GEP product | https://www.gep.com/software/gep-smart |
| Predecessor — legacy v2 archive GEP reference | legacy-v2/reference/sources/gep.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
