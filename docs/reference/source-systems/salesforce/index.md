---
uid: SRC-a3c7e1
slug: salesforce
title: "Salesforce"
description: "Salesforce admission research: candidate access paths (REST API / Bulk API 2.0 / Change Data Capture) under Salesforce's per-edition API entitlement model; permissibility per customer/edition is a clearance decision against the governed authority objects, not asserted here."
type: source-systems
status: published
domain: crm
subdomain: salesforce
focus: governance
authority_role: projection        # D526 Amendment 1 — projection, not an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. Requires governed evidence. ---
proof_status: designed            # downgraded from shape_tested — no governed evidence object exists; simulator run is ungoverned historical background (see evidence.md). Promote only when a governed proof-scope/evidence object is minted.
proof_scope_refs: []              # governed source-proof-scope UID — none yet
source_realization_refs: []       # governed source-realization-package UID — none yet
audit_decision_refs: []           # signed audit-decision UID — none (no realization audit run for Salesforce yet)
# --- exact governed reference coordinates — authority is the REFERENCED object, not these strings; ⧗ = capability/registration pending ---
source_registry_ref: null         # SRC registry UID + exact provider/system/edition (⧗ pending source-registration)
reader_flavor_versions: []        # exact reader-flavor version UID + digest (⧗ pending; slugs below are labels only)
catalog_root: null                # source-catalog snapshot / mapping-root digest (⧗ pending)
contract_set_ref: null            # SC/AC/OC/CC version-set UID or contract-set digest (⧗ pending)
admission_contract_versions: []   # AC version UIDs realized against Salesforce — none authored (see contracts.md)
official_research_refs: []        # structured {source, version, retrieved_at, digest} per official citation (⧗ digest capture pending — 3rd capability gate)
last_verified_at: 2026-07-13
official_docs_url: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/
system_type_code: salesforce      # label; authority = source_registry_ref
reader_flavors:
  - salesforce-rest-v66           # label; authority = reader_flavor_versions[]
catalog_ref: catalog.md           # human link; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendments 1/2/3)
supersedes: docs/reference/source-systems/salesforce.md   # flat v3 page — superseded and removed by this docket migration
---

# Salesforce

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions (D525). `proof_status` below is **evidence maturity,
> not an audit verdict**. Reference narrative is here; concrete artifacts are referenced via the sibling files
> under [Docket Contents](#docket-contents).

Salesforce is a multi-tenant SaaS CRM platform. Data lives in **sObjects** (standard and custom objects) exposed through versioned platform APIs: the **REST API** (SOQL query + sObject resources), **Bulk API 2.0** (asynchronous high-volume query jobs), and **Change Data Capture** (near-real-time change events). BareCount researches these as **candidate access paths**. API access is a per-edition entitlement (Enterprise/Unlimited/Performance/Developer include it; Professional requires a purchased add-on; lower editions have none — [official article](https://help.salesforce.com/s/articleView?id=000385436&language=en_US&type=1)). Which path is permissible for a given customer/edition is a **clearance decision** made against the governed authority objects (see §4.A), not asserted here.

Salesforce releases three seasonal versions per year (Spring / Summer / Winter), each incrementing the API version (e.g. v65.0 = Winter '26, v66.0 = Spring '26, v67.0 = Summer '26 — [official mapping](https://help.salesforce.com/s/articleView?id=000386929&language=en_US&type=1)). Reader bindings must pin an exact API version and be re-verified across releases.

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / commercial / technical / gaps), onboarding runbooks, references, changelog |
| [contracts.md](contracts.md) | Contracts authored against Salesforce + the soft-delete / currency OC patterns |
| [catalog.md](catalog.md) | Salesforce sObject catalog footprint (Opportunity, Account, Contact, …) |
| [onboarding-log.md](onboarding-log.md) | Dated onboarding-execution log |
| [evidence.md](evidence.md) | Proof entries — bc-sdg simulator coverage (ungoverned background); first-hand pending |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1).

**Evidence maturity — `designed`** as of 2026-07-13. Evidence maturity requires *governed* evidence; none exists for Salesforce yet, so no maturity above `designed` can be projected. **This is a downgrade from the flat page's `shape_tested`:** no governed evidence object (UID/digest) was ever minted for that claim.

- **Ungoverned historical background (not a maturity claim):** the REST executor (`bc-core/src/boundary/reader-runtime/executors/sfdc-rest.executor.ts`) has unit-test coverage (`sfdc-rest.executor.spec.ts`) and BareCount operates an internal Salesforce **simulator profile** in `bc-sdg` (`src/simulators/salesforce/rest-server.ts`, port 6110, standard Salesforce REST JSON shapes + SOQL endpoint + 15/18-char ID format). Together these prove **conformance to the declared simulator profile — not Salesforce itself**, and they are **not governed evidence objects** (no UID/digest). They cannot lift `proof_status` on their own. See [evidence.md](evidence.md).
- **Zero validation against a real Salesforce org.** No customer connected app or real-org API session has produced admissions through the BareCount chain.
- Promotion to `shape_tested` requires a **minted governed proof-scope/evidence object** with `proof_scope_refs[]` / `source_realization_refs[]` populated; `first_hand_proven` requires a real-instance entity/scope-specific governed evidence entry — **never** a whole-system promotion of "Salesforce."
- Zero-claims rule (D385): until a real Salesforce org has produced metric snapshots end-to-end, **no external "we work with Salesforce" claim may be made.**

**Audit decision — none.** No source-realization audit (D525) has been run for Salesforce; `audit_decision_refs[]` is empty. PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit substrate against an exact realization package; this docket would only ever render such a decision as a labelled "derived projection" with its governed UID/digest, never as its own authority. `shape_tested` does **not** imply PASS.

---

## 2. Reader Flavor Binding

| Flavor (label) | Target | Executor | AC version |
|---|---|---|---|
| `salesforce-rest-v66` | Salesforce REST API v66.0 (Spring '26) | `SfdcRestExecutor` | — (not yet built for a real org) |

Exact reader-flavor **version UIDs are pending** (`reader_flavor_versions: []` in frontmatter) — the slugs here are labels only. Future candidate flavor labels:

- `salesforce-bulk-v2` — Bulk API 2.0 for historical loads.
- `salesforce-cdc` — Change Data Capture event stream for delta admission.

The simulator-shaped reader binding used in prior ungoverned testing is the same REST flavor configured against the bc-sdg simulator endpoint. The first real Salesforce org will require a customer-side connected app (or External Client App) authorization.

---

## 3. What BareCount Admits

### 3.1 Metadata

sObject and field metadata via the Describe resources: [Describe Global](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_describeGlobal.htm) enumerates all objects in the org; [sObject Describe](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm) returns full field-level metadata (types, picklist values, relationships, child relationships), with `If-Modified-Since` conditional-request support for change detection. Custom objects and custom fields are first-class in the same metadata surface. Stored as entries in the Source Catalog — see [catalog.md](catalog.md).

### 3.2 Business data

Records from Salesforce sObjects, admitted via SOQL over the REST API or Bulk API 2.0 query jobs:

| Domain | Objects | Notes |
|---|---|---|
| Sales | Account, Contact, Lead, Opportunity, OpportunityLineItem, Product2, PricebookEntry, Quote, QuoteLineItem | Deal lifecycle |
| Service | Case, CaseComment, Entitlement, ServiceContract, WorkOrder | Service Cloud objects |
| Marketing | Campaign, CampaignMember | Campaign attribution |
| Commerce | Order, OrderItem | Order lifecycle |
| Platform | User, Profile, PermissionSet, RecordType | Identity and access context |
| Activities | Task, Event | Engagement history |
| Custom | Any custom objects (`__c`) | Discovered per-org via Describe Global |

Unlike an on-premise ERP, the "object" observed is a **semantic platform object** already: the sObject model is the vendor's own API-level schema, per-org extensible. Canonical resolution does the same job either way; only the binding differs.

---

> **Scope of §4–§6 (D526 Amendment 1).** Official, general research only — Salesforce policy and the requirements
> any customer must satisfy. **No** tenant names, contracts, credentials, endpoints, approvals, or legal
> conclusions: those are governed-substrate objects referenced by pseudonymous UID/digest from
> onboarding-log.md / evidence.md. Retrieval date + digest for each official source are pinned in
> [References](#9-references) (⧗ digest TODO).

## 4. Legal & Licensing

### 4.A Platform Plane — Salesforce legal & licensing (general)

> **Researched candidate paths and conditions — NOT clearance conclusions.** Nothing here is "sanctioned" or
> "banned" by BareCount assertion. Each condition holds only as supported by a **version-exact** official
> Salesforce source (recorded in `official_research_refs[]` with retrieval date + exact version + content
> digest — ⧗ digest capture pending, 3rd capability gate) and, at runtime, by an exact-release **Platform Source
> Access Policy** plus the customer's **Tenant Source Authorization** (deferred governed authority objects,
> AuditHub/bc-core-owned). Which path is permissible for a given customer/edition is a **clearance decision**
> made against those objects — not asserted here. This is assurance research, not legal advice.

**4.A.1 API access is a per-edition entitlement (researched).** Per the official
[editions-with-API-access article](https://help.salesforce.com/s/articleView?id=000385436&language=en_US&type=1):
Enterprise, Unlimited, Performance, and Developer editions include API access by default; **Professional Edition
requires purchasing the Web Services API product** (the "Additional API Calls" product does *not* enable API
access for Professional); Group/Essentials and lower editions have no API access and no add-on path — an
edition upgrade is required. Whether a specific customer's org has the entitlement is a per-realization
verification, not assumed.

**4.A.2 API request allocations (researched, current numbers).** Per the official
[limits quick reference](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm):
Enterprise (and Professional-with-API) orgs get **100,000 calls/24h base + 1,000 per Salesforce user license**
(+ purchased API Call Add-Ons); Unlimited/Performance get **100,000 base + 5,000 per license**; Developer
Edition **15,000/24h**; Full Sandbox **5,000,000/24h**. REST, SOAP, Bulk API, and Bulk API 2.0 calls count
against the same aggregate org-level allocation. BareCount readers consume a shared customer resource —
scheduling must budget against the org's allocation (§8 gap: budget instrumentation).

**4.A.3 Read vs write-back.** BareCount reads only today. Any future write-back (Action Engine creating or
updating Salesforce records) changes the integration's contractual posture and must be resolved in the customer
contract and a fresh clearance decision before activation.

**4.A.4 Data residency / infrastructure (researched, ⧗ exact source pending).** Salesforce operates orgs on
its own infrastructure and on **Hyperforce** (Salesforce on public-cloud regions). Residency and processing-
location consequences for a customer's data are org-specific and must be verified per realization against
current official Salesforce trust/compliance documentation (⧗ exact version-pinned source to be captured in
`official_research_refs[]`). No residency conclusion is asserted here.

**4.A.5 Release cadence (researched).** Three seasonal releases per year (Spring / Summer / Winter), each with a
new API version ([official API-version ↔ release mapping](https://help.salesforce.com/s/articleView?id=000386929&language=en_US&type=1)).
Older API versions remain callable for an extended deprecation window, but reader bindings pin an exact version
and must be re-verified on the customer's release upgrade schedule.

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)

What **any** Salesforce customer must have/authorize before connection (stated generically — no named tenant, no
actual approval; those live in the governed substrate):

- **Vendor entitlement**: an edition with API access (Enterprise/Unlimited/Performance/Developer) or the
  Professional-Edition Web Services API purchase (§4.A.1).
- **Integration identity**: a dedicated integration user with the **API Enabled** permission and read-only
  object/field access scoped to exactly the agreed objects — profile/permission-set design is the customer's
  control surface. Whether that identity requires a paid license (or an Integration User license) is a
  customer/Salesforce determination, not a BareCount conclusion.
- **Scope authorization**: internal approval to expose the selected objects/fields (including any custom
  objects) to an external processor, expressed through OAuth scopes on the connected app plus the integration
  user's profile/permission sets.
- **Contractual/security approvals** that must exist (MSA/DPA/Order-Form/security-review) — referenced
  generically; the actual executed documents are governed-substrate objects, never recorded here.
- **Residency / retention / subprocessor** considerations for the customer's data leaving their Salesforce org
  (including Hyperforce region specifics, §4.A.4).
- **Customer-side authorizer roles**: the Salesforce admin (connected-app / External Client App creation,
  integration user, permission sets, IP allow-listing), the Salesforce contract owner (edition/API entitlement
  and any licensing sign-off), and the data/security approver for scope.

---

## 5. Commercial

General access-model and volume guidance (official/planning research; no tenant-specific commercial terms).

### 5.1 Customer access models

| Model | Path | Cost (Salesforce) | Volume suitability |
|---|---|---|---|
| **REST API (SOQL)** | Any API-enabled edition | Included in API-enabled editions; allocation shared org-wide (§4.A.2) | Low–medium; polling deltas |
| **Bulk API 2.0** | Any API-enabled edition | Same aggregate allocation; up to 150M records/24h ([official limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_bulkapi.htm)) | High (historical loads) |
| **Change Data Capture** | Enterprise, Performance, Unlimited, Developer ([official](https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/cdc_intro.htm)); event allocations apply | Event allocations are edition/add-on dependent — a customer/Salesforce determination | Near-real-time deltas |

Cost/permissibility per path is a **customer/Salesforce determination** verified against the governed authority
objects (§4.A), not a BareCount conclusion.

### 5.2 Volume considerations

| Scenario | Typical volume | Recommended model |
|---|---|---|
| Initial historical load | 100K–150M records | Bulk API 2.0 query jobs |
| Daily delta admission | 1K–100K/day | REST SOQL filtered on `SystemModstamp` |
| Near-real-time | continuous | Change Data Capture subscription |

---

## 6. Technical

### 6.A Platform Plane — Salesforce technical (general)

#### 6.1 Protocol

Versioned HTTPS REST API ([developer guide](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/); current GA v67.0 / Summer '26). JSON payloads. SOQL via `GET /services/data/vXX.X/query/?q=<SOQL>`; results are paginated — up to 2,000 records per response with a `nextRecordsUrl` cursor for the next page. A SOAP API exists but BareCount's researched path is REST.

The REST executor (`SfdcRestExecutor`) handles:

1. OAuth 2.0 bearer-token authorization header on every request.
2. SOQL query building from the admission-contract field list + filter, with URL encoding.
3. Paginated query loop following `nextRecordsUrl` until `done: true`.
4. Standard Salesforce REST JSON envelope (`totalSize`, `done`, `records[]` with `attributes` metadata).

**Bulk API 2.0** ([developer guide](https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/)): submit a query job (`POST /services/data/vXX.X/jobs/query`), poll job state, retrieve CSV results in server-defined chunks. Salesforce batches internally per 10,000 records, up to **150 million records per rolling 24-hour period** ([official limits](https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_bulkapi.htm)). No Bulk executor is built yet (§8).

#### 6.2 Authentication

OAuth 2.0 via a customer-side connected app (or its successor packaging, External Client Apps). Researched server-to-server flows:

- **[Client Credentials Flow](https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_client_credentials_flow.htm&language=en_US)** — consumer key + secret exchanged for an access token, executed as a designated integration ("execution") user. Simplest headless path; secret custody is the critical control.
- **[JWT Bearer Flow](https://help.salesforce.com/s/articleView?language=en_US&id=sf.remoteaccess_oauth_jwt_flow.htm)** — client posts an RSA-SHA256–signed JWT against a pre-uploaded X.509 certificate; no shared secret crosses the wire. Preferred for automated integrations.
- Authorization-code (web-server) flow — user-interactive consent variant; handler not yet wired (§8).

Tokens are scoped to one org. All credential material moves **only via the governed secret-ingress mechanism** (§7).

#### 6.3 Throughput / allocations

Org-wide aggregate API allocation per §4.A.2 — the reader shares it with every other integration the customer
runs. `Sforce-Limit-Info` response headers report consumption. The executor does not yet implement allocation-
aware backoff (§8).

#### 6.4 Delta strategy

- SOQL `$filter`-equivalent: `WHERE SystemModstamp > :last_watermark` (audit fields `CreatedDate`, `LastModifiedDate`, `SystemModstamp`).
- **Change Data Capture** ([developer guide](https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/cdc_intro.htm)): near-real-time change events for record create/update/delete/undelete on `/data/ChangeEvents` (all enabled objects) or per-object channels (e.g. `/data/AccountChangeEvent`); subscribe via CometD or the Pub/Sub API. Available in Enterprise, Performance, Unlimited, and Developer editions; event allocations apply. No subscriber built yet (§8).
- Soft deletes: see 6.6.

#### 6.5 Schema discovery

[Describe Global](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_describeGlobal.htm) + [sObject Describe](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm) yield the complete per-org object/field inventory, including custom objects and fields — schema discovery needs no customer-specific documentation, only an authorized API session. `If-Modified-Since` supports cheap metadata change detection. Standard-object baseline definitions come from the official [Object Reference](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/) — see [catalog.md](catalog.md).

#### 6.6 Known semantics

- **Soft delete (`IsDeleted`)**: deleted/merged records go to the recycle bin with `IsDeleted = true`; the standard Query resource excludes them, [QueryAll](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_queryall.htm) includes them (until recycle-bin purge). An OC over a Salesforce object must declare its deletion-visibility stance — see [contracts.md](contracts.md).
- **Multi-currency orgs**: amount fields carry the record's `CurrencyIsoCode`; cross-currency aggregation is a canonical-boundary concern, never a reader-side conversion (⧗ exact official multi-currency citation pending in `official_research_refs[]`).
- **Record types**: one physical sObject can carry multiple business record types (`RecordTypeId`) with distinct picklist/page semantics — discrimination belongs at the canonical/binding layer, not in metric contracts.
- **Field-level security shapes reads**: Describe results and query field access reflect the integration user's profile/permission sets — an under-permissioned integration user silently narrows the observable schema. Catalog verification must run under the production integration identity (⧗ exact official citation pending).

#### 6.7 Network plumbing

SaaS — HTTPS to the customer's My Domain endpoint (`https://{myDomain}.my.salesforce.com`); no VPN or customer-network ingress required. Customer-side login IP ranges / IP relaxation settings on the connected app govern where the integration may authenticate from.

### 6.B Tenant Connection Plane — customer technical prerequisites (general)

What **any** Salesforce customer must set up before a connection can be tested (general requirements; the
step-by-step execution runbook is §7, and concrete endpoints/accounts/results live only in the governed
substrate):

- **Customer-side setup**: create a **connected app** (or External Client App) for BareCount with the required OAuth flow enabled (client credentials with a designated execution user, or JWT bearer with an uploaded X.509 certificate) and minimal OAuth scopes (`api`; `refresh_token`/`offline_access` only if the chosen flow needs them).
- **Service account & minimum permissions**: a dedicated integration user with **API Enabled** and read-only object/field permissions scoped to exactly the agreed objects — no broader. Field-level security must expose the agreed fields to this user (6.6).
- **Endpoint / network allow-listing**: My Domain URL known; connected-app IP relaxation / trusted IP ranges configured for BareCount's egress addresses.
- **Objects/fields to enable**: only the sObjects/fields in the agreed scope (including named custom objects).
- **Connection-test & first-chain proof requirement**: Describe Global reachability + one `SELECT Id FROM <object> LIMIT 1` SOQL read must pass before reader activation; a first governed chain run (SO→CO→MS) is the acceptance bar.
- **Release/customization verification**: confirm the org's current release/API version, installed managed packages, and custom fields/record types that alter standard-object semantics (see [catalog.md](catalog.md) — the standard-object baseline is per-org extensible, so catalog verification is per-realization).

---

## 7. Onboarding Runbooks

Execution history of these runbooks is logged in [onboarding-log.md](onboarding-log.md).

### 7.1 Customer-side

1. **Verify API entitlement.** Edition must include API access (§4.A.1); Professional Edition requires the Web Services API purchase.
2. **Create the connected app / External Client App** in Setup with the agreed OAuth flow: client-credentials (designate the integration execution user) or JWT bearer (upload the X.509 certificate).
3. **Create a dedicated integration user** with API Enabled and read-only permission sets scoped to the agreed objects/fields.
4. **Configure network controls**: IP relaxation / trusted ranges for BareCount egress.
5. **Provision the credential via the approved secret-ingress mechanism (never person-to-person).** The customer submits the connected-app consumer secret (client-credentials flow) or the JWT signing certificate's private key (JWT bearer flow) through the governed secret store, which returns a `credential_ref` + receipt. Hand BareCount only the **My Domain URL, org ID, consumer key, and the `credential_ref`** — **never the raw secret or private key.** No raw secret enters Git, a ticket, chat, email, the docket, or an audit artifact.

### 7.2 BareCount-side

Per-tenant connection profile in `tbc_{slug}_dev`:

- `system_type_code: 'salesforce'`
- `instance_url` (My Domain)
- `org_id`
- `api_version` (pinned, e.g. `v66.0`)
- `auth.method: 'oauth2_client_credentials' | 'oauth2_jwt_bearer'`
- `auth.credential_ref` — reference to a secret provisioned via the governed secret-ingress mechanism (yielding the `credential_ref` + receipt). Raw secrets never enter the DB, Git, tickets, chat, email, the docket, or any audit artifact — only the `credential_ref`.
- `objects[]` — list of agreed sObjects we may query.

Smoke test: `GET /services/data/vXX.X/sobjects/` (Describe Global), then `SELECT Id FROM Account LIMIT 1` before activating the reader.

---

## 8. Known Gaps

1. **Real-org end-to-end** — no real Salesforce org exercised; governed evidence object never minted (the blocking gap for any maturity promotion).
2. **OAuth server-to-server flow handlers** — `SfdcRestExecutor` assumes a resolved bearer token; client-credentials and JWT-bearer token acquisition are not yet first-class in the credential resolver.
3. **Bulk API 2.0 executor** — job submit/poll/CSV-chunk retrieval path not built.
4. **CDC event-stream subscriber** — CometD or Pub/Sub API (gRPC) receiver not built.
5. **Describe-driven catalog auto-population** — per-org Describe Global + sObject Describe into the Source Catalog.
6. **API allocation budget instrumentation** — admission contracts should declare expected daily call count vs the org's allocation; `Sforce-Limit-Info` not yet read.
7. **External Client Apps migration watch** — Salesforce is evolving connected-app packaging; onboarding language must track the official successor guidance.
8. **Multi-currency + FLS official citations** — pin version-exact sources for 6.6 semantics in `official_research_refs[]`.

---

## 9. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| Predecessor flat page (removed by this docket migration; in git history at base `caeac53`) | `salesforce.md` |
| Salesforce REST API Developer Guide | https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/ |
| Bulk API 2.0 Developer Guide | https://developer.salesforce.com/docs/atlas.en-us.api_asynch.meta/api_asynch/ |
| Bulk API limits & allocations | https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_bulkapi.htm |
| API request limits & allocations | https://developer.salesforce.com/docs/atlas.en-us.salesforce_app_limits_cheatsheet.meta/salesforce_app_limits_cheatsheet/salesforce_app_limits_platform_api.htm |
| Editions with API access | https://help.salesforce.com/s/articleView?id=000385436&language=en_US&type=1 |
| API version ↔ release mapping | https://help.salesforce.com/s/articleView?id=000386929&language=en_US&type=1 |
| OAuth 2.0 Client Credentials Flow | https://help.salesforce.com/s/articleView?id=xcloud.remoteaccess_oauth_client_credentials_flow.htm&language=en_US |
| OAuth 2.0 JWT Bearer Flow | https://help.salesforce.com/s/articleView?language=en_US&id=sf.remoteaccess_oauth_jwt_flow.htm |
| Change Data Capture Developer Guide | https://developer.salesforce.com/docs/atlas.en-us.change_data_capture.meta/change_data_capture/cdc_intro.htm |
| sObject Describe (REST) | https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_sobject_describe.htm |
| QueryAll / soft-delete semantics | https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/resources_queryall.htm |
| Standard Object Reference | https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/ |

## 10. Changelog

- **2026-07-13** — authored `salesforce/` docket folder per **DEC-8570d4 (D526)**, mirroring the accepted `sap-ecc/` exemplar. **`proof_status` downgraded `shape_tested` → `designed`**: the flat page's claim rested on executor unit tests + the bc-sdg simulator, which are ungoverned historical background (no governed evidence UID/digest) and cannot establish maturity — see [evidence.md](evidence.md). All exact governed coordinates null/pending; reader-flavor slugs retained as labels. Official facts re-verified against developer.salesforce.com / help.salesforce.com (API v67.0 Summer '26 current; per-edition entitlement and allocations; OAuth client-credentials + JWT bearer; Bulk 2.0 150M/24h; CDC editions). The flat `salesforce.md` is removed by this docket migration (in git history at base `caeac53`).
