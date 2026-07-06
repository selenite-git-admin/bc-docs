---
uid: SRC-c8d3e1
slug: asana
title: "Asana"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: project-management
subdomain: asana
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developers.asana.com/reference/rest-api-reference
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/asana.md
---

# Asana

This page records BareCount's source-admission posture for Asana. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Asana REST; no Asana OAuth 2.0 helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavor when scoped:

- `asana-rest-v1` — primary integration surface.
- `asana-events` — push notifications via Webhooks API.

---

## 3. What BareCount Admits

### 3.1 Metadata

Workspace and organisation definitions; team structures and membership; project templates and configurations; custom field definitions and enum options; tag definitions, section structures within projects; user profiles and role assignments.

### 3.2 Business data

| Domain | Objects |
|---|---|
| Task Management | Tasks, Subtasks, Task dependencies, Task memberships |
| Project Management | Projects, Sections, Project memberships, Project statuses |
| Portfolio Management | Portfolios, Portfolio memberships, Portfolio items |
| Goals & Strategy | Goals, Goal relationships, Time periods |
| Collaboration | Stories (comments / activity), Attachments |
| Time & Effort | Time tracking entries (actual time logged per task) |
| Reporting | Status updates, Project briefs |
| Custom Data | Custom fields (text, number, enum, multi_enum, date, people) |

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

### 6.1 Endpoint

Base URL: `https://app.asana.com/api/1.0/`.

### 6.2 Auth

| Method | Use |
|---|---|
| Personal Access Token (PAT) | Single-user, single-tenant; `Authorization: Bearer <PAT>` |
| OAuth 2.0 | Multi-tenant marketplace |
| Service Account (Enterprise+) | Service-account integrations on E+ |

### 6.3 Pagination and incrementality

`limit` + `offset` (max limit 100). Cursor-style: response includes `next_page.offset` for continuation. Incremental admission via `modified_since` query parameter.

### 6.4 Events vs Webhooks

- **Events** — pull-based: `GET /events?resource={gid}&sync={token}` returns events since last sync.
- **Webhooks** — push-based: `POST /webhooks` to subscribe; receives X-Hook-Signature HMAC-signed callbacks.

Webhooks are preferred for delta admission; Events are useful as a poll-based fallback.

### 6.5 Rate limits

Vendor-defined per-user-per-minute limit. HTTP 429 with `Retry-After`.

---

## 7. Customer-Side Onboarding

1. Customer authorises BareCount via OAuth 2.0 marketplace flow (preferred) or creates a PAT (Profile → My Apps → Personal Access Token).
2. Customer scopes BareCount to specific workspaces.
3. Hand BareCount: workspace GIDs in scope, OAuth tokens (or PAT).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'asana'`
- `workspace_gids[]`
- `auth.method: 'oauth2_asana' | 'pat'`
- `auth.credential_ref`

Smoke test: `GET /api/1.0/users/me`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Asana REST executor** with `next_page.offset` continuation handling.
2. **OAuth 2.0 + PAT** auth methods.
3. **Webhook receiver** with HMAC signature verification.
4. **Events fallback** when webhooks aren't available.
5. **Custom field discovery** — per workspace; the catalogue must auto-discover.
6. **Java SDK deprecation** — confirm BareCount does not depend on the deprecated SDK.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Asana REST API reference | https://developers.asana.com/reference/rest-api-reference |
| Authentication | https://developers.asana.com/docs/authentication |
| Webhooks | https://developers.asana.com/docs/webhooks |
| Events | https://developers.asana.com/docs/events |
| Predecessor — legacy v2 archive Asana reference | legacy-v2/reference/sources/asana.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
