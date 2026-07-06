---
uid: SRC-e7b3c9
slug: freshservice
title: "Freshservice"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: itsm
subdomain: freshworks
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://api.freshservice.com/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/freshservice.md
---

# Freshservice

This page records BareCount's source-admission posture for Freshservice. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Freshservice REST; no Freshworks auth helper (shared with [Freshsales](freshsales.md) gap); no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `freshservice-rest-v2` — primary integration surface.
- `freshservice-webhook` — push notifications via workflow rules.

---

## 3. What BareCount Admits

### 3.1 Metadata

Ticket field definitions (`/api/v2/ticket_form_fields`); agent, group, department, role structures; SLA policy definitions and escalation rules; service catalog item definitions and category trees; asset type schemas; custom field schemas per entity type.

### 3.2 Business data

| Domain | Entities |
|---|---|
| Incident Management | Tickets, conversations, time entries, satisfaction ratings |
| Problem Management | Problems, associated changes, known error records |
| Change Management | Changes, change notes, planning fields, approvals |
| Release Management | Releases, release notes, associated changes |
| Asset Management | Assets, asset types, relationships, software installations |
| CMDB | Configuration items, CI types, CI relationships |
| Service Catalog | Service items, categories, requested items |
| People | Agents, requesters, departments, groups |
| Contracts | Contracts, vendors, purchase orders, products |

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

Base URL: `https://<domain>.freshservice.com/api/v2/`.

### 6.2 Auth

| Method | Use |
|---|---|
| API key | Single-tenant; key as username, `X` as password (Basic auth) |
| OAuth 2.0 | Multi-tenant marketplace (shared with Freshsales) |

### 6.3 Pagination and incrementality

`page` + `per_page` (max 100). Incremental admission via `updated_since` filter on tickets, `updated_at` on most other entities.

### 6.4 Webhooks

Workflow Automator can post to BareCount endpoints. Event types: `ticket.create`, `ticket.update`, `change.create`, `release.create`, etc.

### 6.5 FSBT — Freshservice Business Transactions

The FSBT APIs (Jan 2026) provide a unified transaction view across business object events (ticket lifecycle, asset moves, change executions). Useful for cross-domain admission.

---

## 7. Customer-Side Onboarding

1. Customer creates an API key (Profile → API Settings) or authorises via OAuth 2.0 marketplace flow.
2. Customer creates a service-account agent with read-only role for the modules in scope.
3. Hand BareCount: domain, API key (or OAuth tokens).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'freshservice'`
- `domain` (e.g. `acme.freshservice.com`)
- `auth.method: 'api_key' | 'oauth2_freshworks'`
- `auth.credential_ref`

Smoke test: `GET /api/v2/agents/me`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Freshservice REST executor** with per-edition rate-limit awareness.
2. **Freshworks shared OAuth 2.0 helper** (covers Freshsales + Freshservice).
3. **Webhook receiver**.
4. **FSBT API** — admission contract design for cross-domain business transactions.
5. **CMDB schema discovery** — asset type custom fields per tenant.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Freshservice API docs | https://api.freshservice.com/ |
| Freshservice OAuth 2.0 | https://developers.freshworks.com/freshservice-suite/api/#oauth |
| Webhooks | https://api.freshservice.com/#webhooks |
| Predecessor — legacy v2 archive Freshservice reference | legacy-v2/reference/sources/freshservice.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
