---
uid: SRC-b6e2f3
slug: monday
title: "Monday.com"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: project-management
subdomain: monday
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developer.monday.com/api-reference/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/monday.md
---

# Monday.com

This page records BareCount's source-admission posture for Monday.com. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no GraphQL executor for Monday's API; no Monday OAuth 2.0 helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `monday-graphql-v2` — primary integration surface; API-Version-aware GraphQL client.
- `monday-webhook` — push notifications for item/column/update events.

---

## 3. What BareCount Admits

### 3.1 Metadata

Boards (id, name, board_kind, state, workspace_id, permissions); columns per board (id, title, type, settings_str); groups (id, title, color, position); workspaces; account-level info (id, name, plan, tier, slug).

### 3.2 Business data

| Object | Description |
|---|---|
| Items | Board rows: id, name, state, created_at, updated_at, column_values, group, creator |
| Subitems | Nested child items linked to a parent |
| Updates | Comments / notes on items |
| Activity logs | Board-level audit trail (event type, entity, user, timestamp) |
| Tags | Cross-board categorisation labels |
| Assets | Files uploaded to items |
| Users | User directory |

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

### 6.1 GraphQL endpoint

`POST https://api.monday.com/v2`. Headers:
- `Authorization: <token>` (note: Monday uses bare token, not `Bearer <token>`)
- `API-Version: 2026-01` (or current monthly release)
- `Content-Type: application/json`

Body: standard GraphQL `{ "query": "...", "variables": {...} }`.

### 6.2 Complexity-based rate limiting

Each query is assigned a complexity score based on the depth + breadth of the response. Complexity budget per minute:

| Plan | Complexity budget per minute |
|---|---|
| Free | vendor-defined complexity budget |
| Pro | vendor-defined complexity budget |
| Enterprise | vendor-defined complexity budget, configurable by plan |

The executor must sample query complexity (Monday returns the cost in the response `extensions.complexity` block) and back off when approaching the budget.

### 6.3 Pagination

GraphQL `items_page` connection: `cursor` + `limit` (max 500). The executor must walk the cursor.

### 6.4 Incrementality

`items_by_column_values` filtered on `updated_at` — most flexible. Or webhook-driven for realtime.

### 6.5 Webhooks

Configured per board. POST to BareCount endpoint with payload + signature header.

---

## 7. Customer-Side Onboarding

1. Customer authorises BareCount via OAuth 2.0 marketplace flow (preferred) or generates a Personal API token (Profile → Developer → My Access Tokens).
2. Hand BareCount: API token, list of board IDs in scope.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'monday'`
- `auth.method: 'oauth2_monday' | 'personal_token'`
- `auth.credential_ref`
- `boards_in_scope[]` — board IDs
- `api_version` — pinned monthly release the executor targets

Smoke test: GraphQL `query { me { id name } }`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **GraphQL executor** — first GraphQL executor in BareCount; new pattern.
2. **Complexity-budget tracking** — read `extensions.complexity` from each response and back off.
3. **API-Version pinning + monthly upgrade cadence** — admission contract should declare which API version it targets; framework needs a process for monthly updates.
4. **Webhook receiver** with signature verification.
5. **Cursor-pagination handling** for `items_page`.
6. **Custom column types** — Monday columns are typed but customer-customised; admission contract auto-discovery via `boards.columns.settings_str`.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Monday.com API reference | https://developer.monday.com/api-reference/ |
| API versioning | https://developer.monday.com/api-reference/docs/api-versioning |
| Authentication | https://developer.monday.com/api-reference/docs/authentication |
| Webhooks | https://developer.monday.com/api-reference/docs/webhooks |
| Predecessor — legacy v2 archive Monday reference | legacy-v2/reference/sources/monday.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
