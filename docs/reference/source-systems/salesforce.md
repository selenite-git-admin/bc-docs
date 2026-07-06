---
uid: SRC-a3c7e1
slug: salesforce
title: "Salesforce"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: crm
subdomain: salesforce
focus: governance
proof_status: shape_tested
last_verified_at: 2026-04-28
official_docs_url: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/
reader_flavors:
  - salesforce-rest-v66
admission_contract_versions: []
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/salesforce.md
---

# Salesforce

This page records BareCount's source-admission posture for Salesforce. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `shape_tested`.

The `SfdcRestExecutor` (`bc-core/src/boundary/reader-runtime/executors/sfdc-rest.executor.ts`) has unit-test coverage (`sfdc-rest.executor.spec.ts`) validating REST API protocol handling — pagination, SOQL query encoding, OAuth bearer auth.

What is **not** yet verified for `first_hand_proven` status:
- A real (anonymised) customer Salesforce org has produced metric snapshots through the BareCount chain end-to-end.

Salesforce is a strong candidate for `first_hand_proven` once a production-tenant case exists.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `salesforce-rest-v66` | Salesforce REST API v66.0 | `SfdcRestExecutor` | — (not yet pinned) |

Future candidate flavors:
- `salesforce-bulk-v2` — Bulk API 2.0 for historical loads (up to 150M records / 24h rolling).
- `salesforce-cdc` — Change Data Capture event stream for delta admission.

---

## 3. What BareCount Admits

### 3.1 Metadata

sObject (table) definitions and field metadata via Describe API; custom object and custom field definitions (including formula fields, roll-up summaries); picklist values, record types, and dependent picklist mappings; object relationships (lookup, master-detail, external lookup, indirect lookup); field-level security and sharing rules; validation rules and formula field definitions (read-only); named credentials, connected app configurations.

### 3.2 Business data

| Domain | Objects | Notes |
|---|---|---|
| Sales | Account, Contact, Lead, Opportunity, OpportunityLineItem, Product2, PricebookEntry, Quote, QuoteLineItem | Full pipeline lifecycle |
| Service | Case, CaseComment, Solution, Entitlement, ServiceContract, WorkOrder | Service Cloud objects |
| Marketing | Campaign, CampaignMember | Campaign attribution |
| Commerce | Order, OrderItem | Commerce lifecycle |
| Platform | User, Profile, PermissionSet, RecordType | Identity and access |
| Activities | Task, Event, EmailMessage | Engagement history |
| Custom | Any custom objects | Discovered via Describe Global |

CDC streaming via the Event Bus provides real-time delta admission for standard and custom objects (subscribe to `/data/ChangeEvents` or per-object channels like `/data/AccountChangeEvent`). Events include field-level change details with header metadata. Requires Enterprise+ edition.

Bulk API 2.0 supports up to **150 million records per 24-hour rolling period** with automatic batching.

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

### 6.1 REST API v66.0

| Aspect | Detail |
|---|---|
| Base URL | `https://{instance}.my.salesforce.com/services/data/v66.0/` |
| Query | SOQL via `query/?q=<SOQL>` |
| SObject CRUD | `sobjects/{Name}/{Id}` |
| Auth | OAuth 2.0 (Bearer token) |
| Pagination | `nextRecordsUrl` field on response |

### 6.2 Bulk API 2.0

| Aspect | Detail |
|---|---|
| Endpoint | `services/data/v66.0/jobs/query` |
| Limit | 150M records / 24h rolling |
| Mode | Submit query job → poll → retrieve CSV in chunks (vendor-defined chunk size) |
| Auto-batching | Yes |

### 6.3 Change Data Capture

| Aspect | Detail |
|---|---|
| Channel | `/data/ChangeEvents` (all objects) or `/data/{Object}ChangeEvent` |
| Protocol | CometD over HTTPS |
| Header | `changeType`, `commitTimestamp`, `transactionKey` |
| Edition | Enterprise+ |

### 6.4 Authentication

OAuth 2.0 via Connected App:
1. Customer creates Connected App in Setup → App Manager.
2. Configures OAuth scopes (`api`, `refresh_token`, `offline_access`).
3. Customer authorises BareCount via OAuth 2.0 user-agent or web-server flow → BareCount receives access + refresh tokens.
4. Tokens scoped to one Salesforce org.

JWT Bearer flow also supported for headless integrations.

### 6.5 SOQL

SOQL is Salesforce's query language — SQL-like but with relationship traversal:
```
SELECT Id, Name, Account.Name FROM Opportunity WHERE CloseDate >= :TODAY
```

The executor builds SOQL from admission contract field-list + filter.

---

## 7. Customer-Side Onboarding

1. In Setup → App Manager, create a **Connected App** for BareCount.
2. Configure OAuth scopes: `api`, `refresh_token`, `offline_access`. CDC scenarios additionally need `chatter_api`.
3. Set IP relaxation as appropriate (relaxed enforcement for cloud BareCount; stricter for VPN-fronted deployments).
4. Customer authorises BareCount via OAuth flow.
5. Hand BareCount: instance URL, OAuth client ID, organization ID.

---

## 8. BareCount-Side Onboarding

Connection profile:
- `system_type_code: 'salesforce'`
- `instance_url`
- `org_id`
- `auth.method: 'oauth2_salesforce_authorization_code' | 'oauth2_salesforce_jwt_bearer'`
- `auth.credential_ref`

Smoke test: `GET /services/data/v66.0/sobjects/`, then a small SOQL `SELECT Id FROM Account LIMIT 1`.

---

## 9. Verified Coverage

**No real customer Salesforce org has been admitted end-to-end through the BareCount chain.** Internal unit-test coverage exists; this is shape-test, not first-hand customer proof.

When a production scenario lands, this section will list verified objects and the anonymised customer reference.

---

## 10. Known Gaps

1. **OAuth 2.0 web-server flow handler** — current `SfdcRestExecutor` assumes a token in the credential resolver; the customer-onboarding redirect flow is not yet wired into bc-admin.
2. **Bulk API 2.0 executor** — separate from REST executor; CSV-chunked download.
3. **CDC event-stream subscriber** — CometD long-poll receiver.
4. **Metadata API path** — Describe Global + Describe sObject for catalogue auto-population per customer org.
5. **API call budget instrumentation** — admission contracts should declare expected daily API call count vs the customer's edition limit.
6. **Production-tenant proof** for §9 promotion to `first_hand_proven`.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Salesforce REST API | https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/ |
| Bulk API 2.0 | https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/ |
| Change Data Capture | https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/ |
| OAuth 2.0 | https://help.salesforce.com/s/articleView?id=sf.remoteaccess_authenticate.htm |
| API Limits | https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/ |
| Predecessor — legacy v2 archive Salesforce reference | legacy-v2/reference/sources/salesforce.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
