---
uid: SRC-a4c6e9
slug: zoho-books
title: "Zoho Books"
description: "Zoho Books admission research: REST API v3 over OAuth 2.0 (Zoho Accounts, data-center-specific endpoints) as the candidate access path; permissibility per customer/plan is a clearance decision against the governed authority objects, not asserted here."
type: source-systems
status: published
domain: accounting
subdomain: zoho
focus: governance
authority_role: projection        # D526 Amendment 1 — projection, not an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. Requires governed evidence. ---
proof_status: designed            # NO governed evidence object exists; no reader executor, no simulator profile, no customer engagement (see evidence.md)
proof_scope_refs: []              # governed source-proof-scope UID — none
source_realization_refs: []       # governed source-realization-package UID — none
audit_decision_refs: []           # signed audit-decision UID — none (no realization audit run for Zoho Books)
# --- exact governed reference coordinates — authority is the REFERENCED object, not these strings; ⧗ = capability/registration pending ---
source_registry_ref: null         # SRC registry UID + exact provider/system/edition (⧗ pending source-registration)
reader_flavor_versions: []        # exact reader-flavor version UID + digest — none exists (candidate labels in §2 are labels only)
catalog_root: null                # source-catalog snapshot / mapping-root digest (⧗ pending)
contract_set_ref: null            # SC/AC/OC/CC version-set UID or contract-set digest (⧗ pending)
admission_contract_versions: []   # AC version UIDs realized against Zoho Books — none authored (see contracts.md)
official_research_refs: []        # structured {source, version, retrieved_at, digest} per official citation (⧗ digest capture pending — G3 capability gate)
last_verified_at: 2026-07-13
official_docs_url: https://www.zoho.com/books/api/v3/introduction/
system_type_code: zoho_books      # label; authority = source_registry_ref
reader_flavors: []                # no flavor exists — see §2; candidate labels only
catalog_ref: catalog.md           # human link; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendments 1/2/3)
supersedes: docs/reference/source-systems/zoho-books.md
---

# Zoho Books

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions (D525). `proof_status` below is **evidence maturity,
> not an audit verdict**. Reference narrative is here; concrete artifacts are referenced via the sibling files
> under [Docket Contents](#docket-contents).

Zoho Books is Zoho Corporation's cloud accounting product (part of the Zoho Finance suite). It exposes a
**REST API v3** authenticated via **OAuth 2.0 on Zoho Accounts**, with **data-center-specific endpoints** (the
same customer account lives in exactly one Zoho data center, and both the API base URL and the OAuth token
endpoint are DC-specific). Every API request is scoped by an `organization_id` — a customer may operate
multiple organizations under one Zoho account. BareCount researches the REST API v3 as the **candidate access
path**; webhooks (API-managed and workflow-rule) are a candidate change-notification supplement. Which path is
permissible for a given customer/plan is a **clearance decision** made against the governed authority objects
(see §4.A), not asserted here.

This docket restructures the prior flat reference page (`zoho-books.md`) into the
**DEC-8570d4 (D526)** docket shape. All vendor facts below were re-verified against official zoho.com
documentation on 2026-07-13; anything not officially sourceable is marked ⧗ pending.

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / commercial / technical / gaps), onboarding runbooks, references, changelog |
| [contracts.md](contracts.md) | Contracts authored against Zoho Books (none yet) + candidate contract-pattern notes |
| [catalog.md](catalog.md) | Zoho Books API-module catalog footprint (invoices, bills, journals, chart of accounts, contacts, …) |
| [onboarding-log.md](onboarding-log.md) | Dated onboarding-execution log |
| [evidence.md](evidence.md) | Proof entries — none; no simulator coverage; first-hand pending |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1).

**Evidence maturity — `designed`** as of 2026-07-13. Evidence maturity requires *governed* evidence; none
exists for Zoho Books, so no maturity above `designed` can be projected.

- **No reader executor exists** for the Zoho Books REST API v3, and **no Zoho OAuth 2.0 helper** with
  multi-data-center token support exists in bc-core.
- **No simulator coverage.** Unlike SAP ECC, there is no bc-sdg simulator profile for Zoho Books — there is
  not even ungoverned historical background to record (see [evidence.md](evidence.md)).
- **Zero validation against a real Zoho Books organization.** No customer or vendor-trial instance has
  produced admissions through the BareCount chain.
- Promotion to `shape_tested` requires a **minted governed proof-scope/evidence object** with
  `proof_scope_refs[]` / `source_realization_refs[]` populated; `first_hand_proven` requires a real-instance
  entity/scope-specific governed evidence entry — **never** a whole-system promotion of "Zoho Books."
- Zero-claims rule (D385): until a real Zoho Books organization has produced metric snapshots end-to-end,
  **no external "we work with Zoho Books" claim may be made.**

**Audit decision — none.** No source-realization audit (D525) has been run for Zoho Books;
`audit_decision_refs[]` is empty. PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit substrate
against an exact realization package; this docket would only ever render such a decision as a labelled
"derived projection" with its governed UID/digest, never as its own authority.

---

## 2. Reader Flavor Binding

**Empty (`reader_flavors: []`)** — no reader flavor is registered or built for Zoho Books. No executor,
no flavor version, no AC binding. The labels below are **candidate names only** for when the work is scoped;
they carry no registry identity:

| Candidate flavor (label only) | Target | Executor | AC version |
|---|---|---|---|
| `zoho-books-rest-v3` | Zoho Books REST API v3 (DC-specific base URL, `organization_id` scoping) | — (not built) | — |
| `zoho-books-webhook` | Push notifications on entity changes (API-managed webhooks / workflow rules) | — (not built) | — |

---

## 3. What BareCount Admits

Candidate admission scope via the REST API v3 — design intent, not yet realized by any contract
(see [contracts.md](contracts.md)).

### 3.1 Metadata

Chart of Accounts (account types, codes, parent accounts); tax configurations; currencies and exchange
rates; organization settings (fiscal year, base currency, time zone); user and role definitions; item
catalog; contact classifications (customer, vendor); payment terms. Cataloged as pending entries in the
Source Catalog — see [catalog.md](catalog.md).

### 3.2 Business data

Posted business records via REST API v3 modules — **invoices, bills, journals (manual journal entries),
chart of accounts, contacts** as the core set; plus estimates, sales orders, purchase orders, expenses,
customer/vendor payments, credit notes, vendor credits, bank transactions per the official API module
list. Admitted via paginated REST reads (`page`/`per_page`, `page_context.has_more_page`). Cataloged in
[catalog.md](catalog.md).

Zoho Books has no customer-visible table layer — the "object" we observe is the **API module resource**
(its documented JSON shape), not a database table. Canonical resolution does the same job either way; only
the binding differs.

---

> **Scope of §4–§6 (D526 Amendment 2).** Official, general research only — Zoho policy and the requirements
> any customer must satisfy. **No** tenant names, contracts, credentials, endpoints, approvals, or legal
> conclusions: those are governed-substrate objects referenced by pseudonymous UID/digest from
> onboarding-log.md / evidence.md. Retrieval date + digest for each official source are pinned in
> [References](#9-references) (⧗ digest capture pending per G3).

## 4. Legal & Licensing

### 4.A Platform Plane — Zoho legal & licensing (general)

> **Researched conditions — NOT clearance conclusions.** Nothing here is "sanctioned" or "banned" by
> BareCount assertion. Each condition holds only as supported by a **version-exact** official Zoho source
> (recorded in `official_research_refs[]` with retrieval date + exact version + content digest — ⧗ digest
> capture pending, G3 capability gate) and, at runtime, by an exact-edition **Platform Source Access Policy**
> plus the customer's **Tenant Source Authorization** (deferred governed authority objects). Which access is
> permissible for a given customer/plan is a **clearance decision** made against those objects — not asserted
> here. This is assurance research, not legal advice.

**4.A.1 API terms of use (researched, pending exact-version pin).** Zoho publishes API usage terms and
per-plan API entitlements as part of the Zoho Books API documentation and the general Zoho API/terms-of-service
corpus. The API is a documented, officially supported integration surface (unlike scraping); the exact
terms-of-use document version applicable to third-party read access has **not yet been pinned** into
`official_research_refs[]` — ⧗ pending.

**4.A.2 Per-plan API entitlements (researched, official numbers).** API call quotas are a function of the
customer's Zoho Books **plan** ([API introduction](https://www.zoho.com/books/api/v3/introduction/)):
Free 1,000 calls/day; Standard 2,000/day; Professional 5,000/day; Premium 10,000/day; Elite 10,000/day;
Ultimate 10,000/day — per organization. A customer's plan therefore directly bounds admission cadence; this
is a vendor entitlement fact, not a BareCount clearance.

**4.A.3 Read vs write-back.** BareCount reads only today. OAuth scopes are declared per operation
(`ZohoBooks.<module>.READ` vs `.CREATE`/`.UPDATE`/`.DELETE`/`.ALL`); a read-only integration requests
`.READ` scopes exclusively. If an Action Engine ever writes back into Zoho Books, the write scopes and any
plan/terms consequences must be resolved before activation.

**4.A.4 Data-center residency model (researched).** A Zoho account resides in exactly one of eight data
centers (US, EU, India, Australia, Japan, Canada, Saudi Arabia, China), each with its own API and Zoho
Accounts domain ([API introduction](https://www.zoho.com/books/api/v3/introduction/),
[OAuth Multi DC](https://www.zoho.com/accounts/protocol/oauth/multi-dc.html)). Residency is determined by
where the customer's account was created; BareCount must call the customer's DC — data does not leave its
DC by BareCount's choice of endpoint.

**4.A.5 Deprecation / version policy.** The current API version is **v3**. Zoho has not published a
sunset date for v3 in the API documentation reviewed; a formal deprecation/versioning policy statement has
**not been located as a version-exact official source** — ⧗ pending. (The previously cited
`/books/api/v3/multi-dc/` page now returns 404 — an example of why version-exact pins matter; the
authoritative multi-DC reference is now the Zoho Accounts OAuth documentation.)

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)

What **any** Zoho Books customer must have/authorize before connection (stated generically — no named
tenant, no actual approval; those live in the governed substrate):

- **Vendor entitlement**: an active Zoho Books subscription; the plan determines the daily API quota
  (§4.A.2) and therefore feasible admission cadence.
- **OAuth client**: a registered client in the customer's Zoho Developer Console (server-based for the
  authorization-code flow, or a self client for backend-only access) — created under the customer's
  account, in the customer's data center.
- **Scope authorization**: internal approval to grant the specific read scopes
  (`ZohoBooks.invoices.READ`, `ZohoBooks.bills.READ`, `ZohoBooks.journals.READ`, …) to an external
  processor — the consent screen makes the grant explicit and scope-bounded.
- **Contractual/security approvals** that must exist (MSA/DPA/security-review) — referenced generically;
  the actual executed documents are governed-substrate objects, never recorded here.
- **Residency / retention / subprocessor** considerations: the customer's data center (§4.A.4) determines
  which regional endpoints BareCount calls; retention and subprocessor terms are customer-contract matters.
- **Customer-side authorizer roles**: the Zoho Books organization admin (OAuth consent, user/role
  administration), the subscription owner (plan/entitlement questions), and the data/security approver
  for scope.

---

## 5. Commercial

General access-model and volume guidance (official/planning research; no tenant-specific commercial terms).
Subscription pricing, add-ons, and any per-tenant cost are customer/vendor determinations captured only in
governed onboarding evidence, never here.

### 5.1 Customer access models

| Model | Path | Cost (Zoho) | Volume suitability |
|---|---|---|---|
| **REST API v3 polling** | OAuth 2.0 + DC-specific REST endpoints | Included in subscription; daily quota is plan-tied (§4.A.2) | Bounded by plan quota (1,000–10,000 calls/day) |
| **Webhooks (push)** | API-managed webhooks or workflow-rule webhooks | Included; workflow-rule webhooks limited (max 500 triggers/day per help docs) | Change-notification supplement, not a bulk path |

### 5.2 Volume considerations

At 200 records per page (documented default pagination size), a 10,000-call/day plan bounds a full-day
admission at roughly 2M records/day theoretical ceiling — but the 100 calls/min/organization threshold and
concurrency caps (§6.3) make sustained bulk reads slower in practice. Initial historical loads on Free/
Standard plans (1,000–2,000 calls/day) require multi-day windows or plan discussion. These are planning
figures derived from the official limits, not tested throughput.

---

## 6. Technical

### 6.A Platform Plane — Zoho technical (general)

#### 6.1 Protocol

REST API **v3**, JSON payloads, HTTPS only. Root endpoint `https://www.zohoapis.com/books/v3` (US DC).
Every request **must carry `organization_id`** (query parameter), obtainable via `GET /organizations`.
Data-center-specific base URLs ([API introduction](https://www.zoho.com/books/api/v3/introduction/)):

| Region | Base URI |
|---|---|
| United States | `https://www.zohoapis.com/books/v3/` |
| Europe | `https://www.zohoapis.eu/books/v3/` |
| India | `https://www.zohoapis.in/books/v3/` |
| Australia | `https://www.zohoapis.com.au/books/v3/` |
| Japan | `https://www.zohoapis.jp/books/v3/` |
| Canada | `https://www.zohoapis.ca/books/v3/` |
| Saudi Arabia | `https://www.zohoapis.sa/books/v3/` |
| China | `https://www.zohoapis.com.cn/books/v3/` |

**Pagination:** `page` + `per_page` query parameters; responses carry a `page_context` object with `page`,
`per_page`, and `has_more_page` ([pagination doc](https://www.zoho.com/books/api/v3/pagination/)). Lists
are "paginated to 200 items by default" per the official doc; a documented **maximum** `per_page` value was
not located — ⧗ pending.

#### 6.2 Authentication

OAuth 2.0 on **Zoho Accounts** ([OAuth doc](https://www.zoho.com/books/api/v3/oauth/)):

- **Flows**: authorization-code (web consent) and **self client** (backend-only; grant token generated in
  the developer console, no redirect URI).
- **Grant token**: valid **2 minutes** (exchange promptly).
- **Access token**: valid **1 hour**, bound to the granted scopes.
- **Refresh token**: does not expire unless revoked; **maximum 20 refresh tokens per user** — crossing the
  limit silently deletes the oldest (an operational hazard for long-lived integrations).
- **Endpoints are DC-specific**: `{Accounts_URL}/oauth/v2/auth` and `{Accounts_URL}/oauth/v2/token`, where
  `Accounts_URL` is e.g. `https://accounts.zoho.com` (US), `https://accounts.zoho.eu` (EU),
  `https://accounts.zoho.in` (India). Multi-DC use of one client ID must be **enabled per client** in the
  developer console; the `/oauth/v2/auth` response carries `location` and `accounts-server`, and the token
  response carries `api_domain` — the authoritative DC-discovery mechanism
  ([Multi DC Support](https://www.zoho.com/accounts/protocol/oauth/multi-dc.html)).
- **Scopes**: `ZohoBooks.<module>.<CREATE|READ|UPDATE|DELETE|ALL>` (e.g. `ZohoBooks.invoices.READ`).

#### 6.3 Throughput (official numbers)

Per [API introduction](https://www.zoho.com/books/api/v3/introduction/):

| Limit | Value |
|---|---|
| Per-minute | **100 requests/min per organization** (error code 44, HTTP 429) |
| Daily — Free | 1,000 calls/day (error code 45, HTTP 429) |
| Daily — Standard | 2,000 calls/day |
| Daily — Professional | 5,000 calls/day |
| Daily — Premium / Elite / Ultimate | 10,000 calls/day |
| Concurrent — Free | 5 simultaneous calls (error code 1070, HTTP 429) |
| Concurrent — paid plans | 10 simultaneous calls (soft limit) |

Any future executor needs quota-aware scheduling (per-organization daily budget) and 429 backoff keyed on
error codes 44/45/1070.

#### 6.4 Delta strategy

- A `last_modified_time` list filter was described in prior BareCount research as the incremental-admission
  mechanism, but was **not confirmed in the official pagination/module documentation reviewed on
  2026-07-13** — ⧗ pending per-module verification against the official API reference before any AC relies
  on it.
- Webhooks as change notification: API-managed webhooks (`/settings/webhooks`) support entity events,
  custom headers, retry policies, and **signature verification via a configured secret key (12–50
  alphanumeric characters)** ([webhooks API doc](https://www.zoho.com/books/api/v3/webhooks/)).
  Workflow-rule webhooks are also available via the automation UI (1 webhook per workflow rule; max 500
  webhook triggers/day per the official help/KB). Webhooks supplement — never replace — read-based
  reconciliation.

#### 6.5 Schema discovery

No customer-side metadata endpoint equivalent to OData `$metadata`. Schema discovery is via the **official
API documentation** (per-module JSON shape reference and downloadable OpenAPI documents, e.g.
`invoices.yml`, linked from the module pages). Catalog seeding therefore proceeds from the published API
reference without touching any customer organization — see [catalog.md](catalog.md).

#### 6.6 Network plumbing

Pure SaaS: HTTPS from BareCount to the customer's DC-specific `zohoapis.*` endpoint. No customer-side
network setup, VPN, or IP allow-listing is required by Zoho for API access (customer-side egress policy
permitting). No on-premise component.

#### 6.7 Known semantics (design notes, ⧗ pending contract-time verification)

- **Organization scoping**: every read is per-organization; multi-org customers require per-org
  enumeration and per-org quota budgeting.
- **Accrual vs cash basis**: Zoho Books reports (Balance Sheet, P&L, Trial Balance) can be rendered on an
  accrual or cash **report basis** — a read-time projection over the same underlying documents
  ([Zoho guide](https://www.zoho.com/books/guides/difference-between-cash-accounting-and-accrual-accounting.html)).
  BareCount admits the underlying transactional documents (basis-neutral); any basis semantics belong at
  the canonical/metric boundary, never baked into admission. Exact per-report basis behavior ⧗ pending
  verification during contract authoring.
- **Credit documents are entity-typed, not sign-flagged**: credit notes / vendor credits are separate API
  modules rather than sign-indicator fields on one table (contrast SAP `SHKZG`). Directional semantics are
  a canonical-boundary concern — see [contracts.md](contracts.md).

### 6.B Tenant Connection Plane — customer technical prerequisites (general)

What **any** Zoho Books customer must set up before a connection can be tested (general requirements; the
step-by-step execution runbook is §7, and concrete org IDs/credentials/results live only in the governed
substrate):

- **OAuth client / self-client creation**: register a client in the customer's Zoho Developer Console
  (in the customer's DC); for backend-only access, a self client with console-generated grant tokens.
- **Minimum OAuth scopes**: read-only scopes for exactly the agreed modules
  (`ZohoBooks.invoices.READ`, `ZohoBooks.bills.READ`, `ZohoBooks.journals.READ`,
  `ZohoBooks.chartofaccounts.READ`, `ZohoBooks.contacts.READ`) — no `.ALL`, no write operations.
- **Organization ID selection**: enumerate via `GET /organizations`; agree which organization(s) are in
  scope; each in-scope org is a separate connection coordinate with its own quota budget.
- **Credential provisioning via governed secret-ingress ONLY**: the OAuth client secret and refresh token
  are submitted through the governed secret store, which returns a `credential_ref` + receipt. Hand
  BareCount only the **DC/region, organization ID(s), and the `credential_ref`** — **never the raw
  secret.** No raw secret enters Git, a ticket, chat, email, the docket, or an audit artifact.
- **Connection-test & first-chain proof requirement**: `GET /organizations` against the correct DC + one
  in-scope module list with `per_page=1` must pass before reader activation; a first governed chain run
  (SO→CO→MS) is the acceptance bar.
- **Plan/edition + customization verification**: confirm the exact plan (quota, §4.A.2), the regional
  edition (e.g. India-edition GST modules alter the module surface), and any custom fields that extend the
  documented module shapes — universality of the published API shape is edition-scoped (see
  [catalog.md](catalog.md)).

---

## 7. Onboarding Runbooks

Execution history of these runbooks is logged in [onboarding-log.md](onboarding-log.md). No execution has
occurred yet.

### 7.1 Customer-side

1. **Confirm plan and DC.** Identify the Zoho Books plan (daily API quota) and the data center hosting the
   account (the Accounts URL used to sign in indicates the DC).
2. **Create the OAuth client** in the Zoho Developer Console — server-based client (authorization-code
   flow) or self client (backend-only), in the customer's DC.
3. **Authorize read scopes.** Grant only the agreed `.READ` scopes for the in-scope modules via the
   consent flow (or console-generated grant token for a self client; grant tokens expire in 2 minutes).
4. **Select organizations.** Confirm which `organization_id`(s) are in scope.
5. **Provision credentials via the approved secret-ingress mechanism (never person-to-person).** The
   customer submits the client secret + refresh token through the governed secret store, which returns a
   `credential_ref` + receipt. Hand BareCount only the **DC/region, organization ID(s), and
   `credential_ref`** — **never the raw secret.**

### 7.2 BareCount-side

Per-tenant connection profile in `tbc_{slug}_dev`:

- `system_type_code: 'zoho_books'`
- `region` — one of `us`, `eu`, `in`, `au`, `jp`, `ca`, `sa`, `cn` (drives both API base URL and Accounts
  token endpoint)
- `organization_id` (or list, for multi-org tenants)
- `auth.method: 'oauth2_zoho'` (authorization-code or self-client provenance)
- `auth.credential_ref` — reference to a secret provisioned via the governed secret-ingress mechanism
  (yielding the `credential_ref` + receipt). Raw secrets never enter the DB, Git, tickets, chat, email,
  the docket, or any audit artifact — only the `credential_ref`.

Smoke test: refresh an access token against the region's Accounts endpoint, `GET /organizations`, then one
in-scope module list with `per_page=1`, before activating any reader.

---

## 8. Known Gaps

1. **Zoho OAuth 2.0 helper** with per-DC token + API endpoints and refresh-token lifecycle management
   (including the 20-refresh-tokens-per-user eviction hazard). The single most important Zoho-specific
   complexity.
2. **REST executor** with `organization_id` propagation, DC-aware base URL, and pagination via
   `page_context.has_more_page`.
3. **Quota-aware admission scheduling** — per-organization daily budget by plan; 429 backoff keyed on
   error codes 44/45/1070. Free/Standard plans cannot sustain high-frequency polling.
4. **Delta mechanism verification** — `last_modified_time` (or equivalent) filter support must be
   confirmed per module against the official API reference (⧗, see §6.4).
5. **Webhook receiver** with secret-key signature verification (API-managed webhooks) — design pending.
6. **Multi-org tenants** — connection profile must enumerate organizations and budget quota per org.
7. **India-edition GST modules** (GSTR-1/3B/2B) — regional module surface not yet cataloged or verified
   against official docs (⧗).
8. **Official-source digest capture** (`official_research_refs[]`) — G3 capability gate; all citations
   below are URL + retrieval date only until digests land.

---

## 9. References

All official sources retrieved 2026-07-13; content digests ⧗ pending (G3).

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| Zoho Books API v3 — Introduction (base URLs, org scoping, rate limits) | https://www.zoho.com/books/api/v3/introduction/ |
| Zoho Books API v3 — OAuth 2.0 (flows, token lifetimes, scopes) | https://www.zoho.com/books/api/v3/oauth/ |
| Zoho Accounts — OAuth Multi DC Support | https://www.zoho.com/accounts/protocol/oauth/multi-dc.html |
| Zoho Books API v3 — Pagination | https://www.zoho.com/books/api/v3/pagination/ |
| Zoho Books API v3 — Webhooks (settings/webhooks, secret-key signatures) | https://www.zoho.com/books/api/v3/webhooks/ |
| Zoho Books Help/KB — workflow-rule webhooks | https://www.zoho.com/us/books/kb/automation/create-webhook.html |
| Zoho guide — cash vs accrual accounting | https://www.zoho.com/books/guides/difference-between-cash-accounting-and-accrual-accounting.html |
| Predecessor — flat v3 reference page | `zoho-books.md` |

Note: the previously referenced `https://www.zoho.com/books/api/v3/multi-dc/` URL returns 404 as of
2026-07-13; the Zoho Accounts Multi DC page above is the current official reference.

## 10. Changelog

- **2026-07-13** — initial `zoho-books/` docket authored per **DEC-8570d4 (D526 + Amendments 1/2/3)**,
  restructuring the flat `zoho-books.md` reference page into the docket shape
  (four-quadrant §4/§6, projection banners, exact-coordinate frontmatter). Official vendor facts
  re-verified against zoho.com on 2026-07-13: per-plan daily quotas, per-minute and concurrency limits with
  error codes, OAuth token lifetimes and the 20-refresh-token cap, DC-specific endpoints, webhook
  signature-secret mechanism. The flat page's `last_modified_time` delta claim and `per_page` max-200 claim
  were **not** re-confirmed from official sources and are downgraded to ⧗ pending. `proof_status: designed`
  unchanged.
