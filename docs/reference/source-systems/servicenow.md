---
uid: SRC-b8e2d4
slug: servicenow
title: "ServiceNow"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: itsm
subdomain: servicenow
focus: governance
proof_status: designed
last_verified_at: 2026-04-28
official_docs_url: https://www.servicenow.com/docs/bundle/xanadu-api-reference/page/build/applications/concept/api-rest.html
reader_flavors: []
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/servicenow.md
---

# ServiceNow

This page records BareCount's source-admission posture for ServiceNow. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `designed`.

Architecture documented; no reader executor for ServiceNow REST APIs; no ServiceNow OAuth 2.0 helper; no customer engagement.

---

## 2. Reader Flavor Binding

Empty list. Candidate flavors when scoped:

- `servicenow-table-api` — generic Table API for arbitrary table reads (`/api/now/table/{table}`).
- `servicenow-aggregate-api` — Aggregate API for aggregated metrics (count, sum) on tables.
- `servicenow-import-set` — for bulk historical loads where Table API rate-limits become a constraint.

---

## 3. What BareCount Admits

### 3.1 Metadata

CI class hierarchy and attributes via CMDB schema; `sys_class_name` taxonomy; SLA definitions (`contract_sla`); assignment groups (`sys_user_group`); service catalog item definitions (`sc_cat_item`); choice lists, dictionary entries (`sys_dictionary`); knowledge base structures.

### 3.2 Business data

| Domain | Tables |
|---|---|
| Incident Management | `incident` |
| Problem Management | `problem` |
| Change Management | `change_request` |
| Service Catalog | `sc_request`, `sc_req_item`, `sc_task` |
| CMDB | `cmdb_ci`, `cmdb_ci_server`, `cmdb_ci_service`, `cmdb_rel_ci` |
| Asset Management | `alm_asset`, `alm_hardware` |
| Knowledge | `kb_knowledge` |
| Users / Groups | `sys_user`, `sys_user_group`, `sys_user_grmember` |
| SLA Tracking | `task_sla`, `contract_sla` |
| GRC | `sn_compliance_policy`, `sn_risk_risk` |
| SecOps | `sn_si_incident`, `sn_vul_vulnerability` |

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

### 6.1 ServiceNow REST APIs

| API | Purpose |
|---|---|
| Table API | Generic record CRUD on any table |
| Aggregate API | Aggregated reads (count, sum, avg) |
| Import Set API | Bulk record inserts (less relevant for read-only admission) |
| Attachment API | File metadata + download |

### 6.2 Endpoints

Base URL and table endpoints use the vendor REST namespace. Per-table reads use OData-like `sysparm_query`, `sysparm_fields`, `sysparm_limit`, and `sysparm_offset` parameters.

### 6.3 Auth

| Method | Use |
|---|---|
| OAuth 2.0 | Recommended; auth code or client credentials |
| Basic Auth | Service account user + password |
| Mutual TLS | Enterprise scenarios |

### 6.4 Pagination and incrementality

`sysparm_limit` and `sysparm_offset` for vendor-defined paging. Incremental admission via `sys_updated_on` filter in `sysparm_query` (e.g. `sysparm_query=sys_updated_on>=javascript:gs.minutesAgo(60)`).

### 6.5 Rate limits and TPS

Per-instance transactions-per-second (TPS) budget — varies by edition. HTTP 429 with `Retry-After`. Rate-limit rules can be administrator-configured for specific REST endpoints.

---

## 7. Customer-Side Onboarding

1. Customer creates a service account user (e.g. `barecount.svc`) with `itil` role.
2. Allocates one paid Fulfiller licence to the user.
3. Configures ACLs to restrict field-level reads as appropriate.
4. Creates an OAuth Application Registry entry for BareCount (System OAuth → Application Registry).
5. Hand BareCount: instance URL, OAuth client ID/secret, service-account credentials.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'servicenow'`
- `instance_url`
- `auth.method: 'oauth2_servicenow_password' | 'oauth2_servicenow_client_credentials' | 'basic'`
- `auth.credential_ref`
- `licensed: true` — informational

Smoke test: `GET /api/now/table/incident?sysparm_limit=1`.

---

## 9. Verified Coverage

**Nothing.**

---

## 10. Known Gaps

1. **ServiceNow REST executor** with `sysparm_*` query parameter handling.
2. **OAuth 2.0** auth methods (multiple flows).
3. **Licence-cost advisory** — BareCount onboarding must surface the Fulfiller licence requirement before the customer starts the integration.
4. **TPS-aware throttling** with `Retry-After` honour.
5. **CMDB class hierarchy traversal** — observations may need to walk `sys_class_path` to handle CI inheritance.
6. **Custom tables / scoped apps** — customer-customised tables require auto-discovery.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| ServiceNow REST API | https://www.servicenow.com/docs/bundle/xanadu-api-reference/page/build/applications/concept/api-rest.html |
| Table API | https://www.servicenow.com/docs/bundle/xanadu-api-reference/page/integrate/inbound-rest/concept/c_TableAPI.html |
| Aggregate API | https://www.servicenow.com/docs/bundle/xanadu-api-reference/page/integrate/inbound-rest/concept/c_AggregateAPI.html |
| OAuth | https://www.servicenow.com/docs/bundle/xanadu-platform-administration/page/administer/security/concept/c_OAuthApplications.html |
| Predecessor — legacy v2 archive ServiceNow reference | legacy-v2/reference/sources/servicenow.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
