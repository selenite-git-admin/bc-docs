---
uid: SRC-c4d9e6
slug: atlassian-jira
title: "Atlassian Jira"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: project-management
subdomain: atlassian
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/atlassian-jira.md
---

# Atlassian Jira

This page records BareCount's source-admission posture for Atlassian Jira. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for Jira Cloud REST; no Atlassian OAuth 2.0 (3LO) helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `atlassian-jira-platform-v3` — issues, fields, search (JQL), workflows, projects.
- `atlassian-jira-agile-v1` — boards, sprints, backlogs.
- `atlassian-jira-webhook` — push notifications.

---

## 3. What BareCount Admits

### 3.1 Metadata

Project definitions; issue type schemes and definitions (standard + custom); workflow definitions (statuses, transitions, rules, conditions, validators, post-functions); status categories and statuses; priority schemes; screen schemes; custom field definitions and option sets (`customfield_XXXXX`); board configurations (columns, constraints, estimation); sprint definitions; notification + permission schemes.

### 3.2 Business data

Issues — the primary work object: summary, description (ADF), assignee, reporter, status, priority, labels, components, fix versions, time tracking, story points, epic link, parent, subtasks, attachments, comments, watchers; sprints; boards; worklogs (time entries per issue); changelogs (field-level audit trail); components; versions; comments; issue links (typed relationships); attachments (metadata).

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

Cloud base: `https://<your-domain>.atlassian.net/rest/api/3/` (platform v3) and `/rest/agile/1.0/` (agile).

### 6.2 Auth

| Method | Use |
|---|---|
| OAuth 2.0 (3LO) | Multi-tenant marketplace integrations |
| API token + Basic Auth | Single-tenant; token from Atlassian account → Email + Token as Basic credentials |
| Forge runtime | Atlassian-hosted apps (mandatory for new Marketplace submissions per Sep 2025) |

### 6.3 JQL — query language

Jira's primary query language. Filter syntax: `project = "FOO" AND status != Done AND updated >= -7d`. The executor builds JQL from admission contract field-list + filter.

### 6.4 Pagination and incrementality

Search endpoints: `startAt` + `maxResults` (max 100). Incremental admission via JQL `updated >= ?` filter. Changelog endpoint provides field-level history per issue.

### 6.5 Webhooks

Configurable per integration; Atlassian-managed signing for OAuth-based webhooks; static secret for token-based.

### 6.6 Rate limits

Cloud: dynamic, cost-based. HTTP 429 with `Retry-After`. The executor must implement adaptive backoff. Avoid bursty traffic patterns.

---

## 7. Customer-Side Onboarding

1. Customer authorises BareCount via OAuth 2.0 marketplace flow (preferred) or generates an API token (Atlassian account → Security → API tokens).
2. Customer scopes BareCount to specific projects via `read:jira-work` scope or project-level permissions.
3. Hand BareCount: site URL, OAuth client + tokens (or email + API token).

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'atlassian_jira'`
- `site_url`
- `auth.method: 'oauth2_atlassian_3lo' | 'api_token_basic'`
- `auth.credential_ref`
- `projects[]` — projects in scope

Smoke test: `GET /rest/api/3/myself` confirms auth.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Jira REST executor** with JQL builder + pagination + ADF text handling.
2. **OAuth 2.0 (3LO)** auth method.
3. **API token + Basic auth** method.
4. **Webhook receiver** with signature verification.
5. **Custom field discovery** — `customfield_*` IDs vary per tenant.
6. **ADF (Atlassian Document Format)** text rendering — issue descriptions and comments are ADF; canonical resolution must extract plain text.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Jira Cloud REST API v3 | https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/ |
| Agile REST API | https://developer.atlassian.com/cloud/jira/software/rest/intro/ |
| OAuth 2.0 (3LO) | https://developer.atlassian.com/cloud/jira/platform/oauth-2-3lo-apps/ |
| API tokens | https://id.atlassian.com/manage-profile/security/api-tokens |
| Predecessor — legacy v2 archive Atlassian Jira reference | legacy-v2/reference/sources/atlassian-jira.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
