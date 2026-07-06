---
uid: SRC-d5f1a8
slug: jira-sm
title: "Jira Service Management"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: itsm
subdomain: atlassian
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://developer.atlassian.com/cloud/jira/service-desk/rest/api-group-servicedesk/
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/jira-sm.md
---

# Jira Service Management

This page records BareCount's source-admission posture for Jira Service Management. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for any of the three JSM surfaces; no Atlassian OAuth 2.0 helper (shared gap with Jira platform); no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `jira-sm-platform` — issues via Jira Platform REST v3 with ITSM issue types (Incident, Problem, Change, Service Request).
- `jira-sm-service-desk` — JSM Service Desk REST for service-desk-specific entities (requests, queues, SLAs, request types).
- `jira-sm-assets` — Assets REST API for CMDB objects.
- `jira-sm-operations-v2` — Operations REST API for alerts, on-call schedules, incident lifecycle.

---

## 3. What BareCount Admits

### 3.1 Metadata

Service desk definitions, request type definitions and groups; queue definitions, SLA metric definitions; workflow statuses and transitions, custom field definitions; issue type schemes (Incident, Problem, Change, Service Request); Assets object schemas, object types, and attribute definitions.

### 3.2 Business data

| ITSM practice | Jira issue type / object | Key data |
|---|---|---|
| Service Request Management | Service Request | Request type, requester, channel, SLA status, approvals |
| Incident Management | Incident | Severity, affected services, responders, timeline |
| Problem Management | Problem | Root cause, linked incidents, workarounds |
| Change Management | Change | Change type, risk assessment, approval chain |
| Assets / Configuration Items | Assets Objects | CI attributes, relationships, dependencies |
| On-call & Alerts (Operations API v2) | Alert, Schedule, Rotation | Alert routing, rotations, escalation paths |

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

| Surface | Base path |
|---|---|
| Platform v3 | `/rest/api/3/` |
| Service Desk | `/rest/servicedeskapi/` |
| Assets | `/jsm/assets/workspace/{workspaceId}/v1/` |
| Operations v2 | `/jsm/ops/api/v2/` |

All under `https://<your-domain>.atlassian.net`.

### 6.2 Auth

OAuth 2.0 (3LO) or API token + Basic Auth — same patterns as Atlassian Jira.

### 6.3 JQL + Service Desk filters

Service Desk endpoints add ITSM-specific filter parameters (`requestStatus`, `requestOwnership`, `requestTypeId`). Combined with JQL when querying via the Platform API.

### 6.4 Webhooks

Per-project configuration. Service Desk events (request created, status changed, SLA breached) plus Operations events (alert created, acknowledged, escalated).

### 6.5 Rate limits

Same as Jira Cloud — dynamic cost-based, HTTP 429 with `Retry-After`.

---

## 7. Customer-Side Onboarding

1. Same OAuth / API token setup as Atlassian Jira (often the same tenant).
2. Grant BareCount project-level access to JSM projects.
3. For Assets: grant access to specific Assets workspaces.
4. Hand BareCount: site URL, OAuth tokens (or API token), service desk IDs in scope.

---

## 8. BareCount-Side Onboarding

Connection profile (extends or shares Jira platform profile):
- `system_type_code: 'jira_sm'`
- `site_url`
- `service_desk_ids[]`
- `assets_workspaces[]`
- `auth.method`, `auth.credential_ref` — typically shared with `atlassian_jira` profile

Smoke test: `GET /rest/servicedeskapi/servicedesk` for service desk list.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **Three-surface executor** — Platform v3, Service Desk, Assets, Operations v2 each with slightly different conventions.
2. **Atlassian OAuth 2.0 / API token** auth (shared gap with Jira platform).
3. **Forge runtime** — if BareCount ever lists in the Atlassian Marketplace, it must be Forge-based (Connect EOS Dec 2026).
4. **Assets schema-aware admission** — Assets is custom-schema per tenant; admission contract design must enumerate object types.
5. **Operations v2 incident lifecycle** — newer API surface; canonical-mapping for alerts vs incidents needs careful design.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Companion source page | [Atlassian Jira](atlassian-jira.md) |
| JSM Service Desk REST | https://developer.atlassian.com/cloud/jira/service-desk/rest/api-group-servicedesk/ |
| Assets REST API | https://developer.atlassian.com/cloud/assets/rest/intro/ |
| Operations REST API v2 | https://developer.atlassian.com/cloud/jira/service-desk-ops/rest/v2/api-group-incidents/ |
| Forge | https://developer.atlassian.com/platform/forge/ |
| Predecessor — legacy v2 archive JSM reference | legacy-v2/reference/sources/jira-sm.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
