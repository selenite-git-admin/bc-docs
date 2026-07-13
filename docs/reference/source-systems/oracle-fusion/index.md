---
uid: SRC-1b8e5a
slug: oracle-fusion
title: "Oracle Fusion Cloud ERP"
description: "Oracle Fusion Cloud ERP admission research: candidate access paths (REST API for Financials, BICC bulk extract) under Oracle's cloud service terms; permissibility per customer/release is a clearance decision against the governed authority objects, not asserted here."
type: source-systems
status: published
domain: enterprise-erp
subdomain: oracle
focus: governance
authority_role: projection        # D526 Amendment 1 — projection, not an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. Requires governed evidence. ---
proof_status: designed            # NO evidence of any kind exists — no executor, no simulator profile, no customer engagement. Promote only when a governed proof-scope/evidence object is minted.
proof_scope_refs: []              # governed source-proof-scope UID — none
source_realization_refs: []       # governed source-realization-package UID — none
audit_decision_refs: []           # signed audit-decision UID — none (no realization audit run for Fusion)
# --- exact governed reference coordinates — authority is the REFERENCED object, not these strings; ⧗ = capability/registration pending ---
source_registry_ref: null         # SRC registry UID + exact provider/system/release (⧗ pending source-registration)
reader_flavor_versions: []        # exact reader-flavor version UID + digest (⧗ pending; slugs below are labels only)
catalog_root: null                # source-catalog snapshot / mapping-root digest (⧗ pending)
contract_set_ref: null            # SC/AC/OC/CC version-set UID or contract-set digest (⧗ pending)
admission_contract_versions: []   # AC version UIDs realized against Fusion — none authored (see contracts.md)
official_research_refs: []        # structured {source, version, retrieved_at, digest} per official citation (⧗ digest capture pending — 3rd capability gate)
last_verified_at: 2026-07-13
official_docs_url: https://docs.oracle.com/en/cloud/saas/financials/
system_type_code: oracle_fusion   # label; authority = source_registry_ref
reader_flavors:
  - oracle-fusion-rest-v1         # label (candidate); authority = reader_flavor_versions[]
  - oracle-fusion-bicc            # label (candidate); authority = reader_flavor_versions[]
catalog_ref: catalog.md           # human link; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendments 1/2/3)
supersedes: docs/reference/source-systems/oracle-fusion.md
---

# Oracle Fusion Cloud ERP

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions (D525). `proof_status` below is **evidence maturity,
> not an audit verdict**. Reference narrative is here; concrete artifacts are referenced via the sibling files
> under [Docket Contents](#docket-contents).

Oracle Fusion Cloud ERP is Oracle's SaaS-only cloud ERP suite (Financials, Procurement, Project Management, and companion modules). Unlike on-premise ERPs, there is no customer-managed database or transport layer: data access is through Oracle-published surfaces — the **REST API for Financials** (and sibling module APIs) and the **BI Cloud Connector (BICC)** bulk-extract facility — and the underlying table shapes are publicly documented in Oracle's **Tables and Views for Financials** reference. Oracle applies **mandatory quarterly updates** (release labels such as 25C, 25D) to every customer pod. BareCount researches the REST API and BICC as **candidate access paths**; which path is permissible for a given customer/subscription is a **clearance decision** made against the governed authority objects (see §4.A), not asserted here.

No Oracle-specific admission-stance ADR exists yet (the SAP analogue is D384). Until one is decided, this docket records official research only; no access path is characterized as sanctioned or excluded.

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / commercial / technical / gaps), onboarding runbooks, references, changelog |
| [contracts.md](contracts.md) | Contracts authored against Fusion + candidate OC design notes (signed dual-column amounts, XLA subledger flow) |
| [catalog.md](catalog.md) | Fusion Financials table/resource catalog footprint (GL_JE_LINES-class tables, REST resources, BICC data stores) |
| [onboarding-log.md](onboarding-log.md) | Dated onboarding-execution log |
| [evidence.md](evidence.md) | Proof entries — none exist; no simulator coverage; first-hand pending |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1).

**Evidence maturity — `designed`** as of 2026-07-13. Evidence maturity requires *governed* evidence; none exists for Oracle Fusion — and, unlike SAP ECC, there is **no ungoverned background either**: no reader executor has been built, no bc-sdg simulator profile exists for Fusion, and no customer or vendor instance has ever been touched. See [evidence.md](evidence.md).

- **Zero validation of any kind.** No REST call, no BICC extract, no OAuth token exchange has been executed by BareCount against any Fusion instance, real or simulated.
- Promotion to `shape_tested` requires a **minted governed proof-scope/evidence object** with `proof_scope_refs[]` / `source_realization_refs[]` populated; `first_hand_proven` requires a real-instance entity/scope-specific governed evidence entry — **never** a whole-system promotion of "Oracle Fusion."
- Zero-claims rule (D385): until a real Fusion instance has produced metric snapshots end-to-end, **no external "we work with Oracle Fusion" claim may be made.**

**Audit decision — none.** No source-realization audit (D525) has been run for Oracle Fusion; `audit_decision_refs[]` is empty. PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit substrate against an exact realization package; this docket would only ever render such a decision as a labelled "derived projection" with its governed UID/digest, never as its own authority.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `oracle-fusion-rest-v1` (candidate) | Fusion REST API (`/fscmRestApi/resources/11.13.18.05/{resource}`) | — (not built) | — |
| `oracle-fusion-bicc` (candidate) | BICC data-store extract → object storage (CSV + manifest) | — (not built) | — |

Both flavors are **candidate labels only** — no executor exists for either, and `reader_flavor_versions[]` is empty. The REST flavor is the expected first build (row-level reads, delta by query filter); the BICC flavor is the expected path for initial historical loads.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts (segments, value sets, hierarchies); business units; ledgers and ledger sets; currencies and exchange rates; lookup values; suppliers and customers; tax configuration; items and categories; organisations; project structures. Table/column shapes come from the public **Tables and Views for Financials** reference (release-versioned, e.g. 25D) and from the REST `describe` surface. Stored as Tier 5/6 entries in the Source Catalog — see [catalog.md](catalog.md).

### 3.2 Business data

Posted business records from Fusion Financials tables as documented in the Tables-and-Views reference — GL journal batches/headers/lines (`GL_JE_BATCHES`/`GL_JE_HEADERS`/`GL_JE_LINES`-class), account balances, Subledger Accounting entries (`XLA_*`-class), AP invoices and payments, AR transactions and receipts, fixed assets, cash management, procurement, and projects. Admitted via the REST API (row-level) or BICC extract output (bulk CSV). Cataloged in [catalog.md](catalog.md).

Fusion differs from classic on-premise ERPs in that the customer never has direct SQL access to these tables: the "object" BareCount observes is a REST resource or a BICC data store (view object) **over** the documented table, not the table itself. Canonical resolution does the same job either way; only the binding differs.

---

> **Scope of §4–§6 (D526 Amendment 1).** Official, general research only — Oracle policy and the requirements any
> customer must satisfy. **No** tenant names, contracts, credentials, endpoints, approvals, or legal conclusions:
> those are governed-substrate objects referenced by pseudonymous UID/digest from onboarding-log.md / evidence.md.
> Retrieval date + digest for each official source are pinned in [References](#9-references) (⧗ digest TODO).

## 4. Legal & Licensing

### 4.A Platform Plane — Oracle legal & licensing (general)

> **Researched conditions — NOT clearance conclusions.** Nothing here is "sanctioned" or "banned" by BareCount
> assertion. Each condition holds only as supported by a **version-exact** official Oracle source (recorded in
> `official_research_refs[]` with retrieval date + exact version + content digest — ⧗ digest capture pending,
> 3rd capability gate) and, at runtime, by an exact-release **Platform Source Access Policy** plus the customer's
> **Tenant Source Authorization** (deferred governed authority objects). Which path is permissible for a given
> customer/subscription is a **clearance decision** made against those objects — not asserted here. This is
> assurance research, not legal advice.

**4.A.1 Access surfaces under Oracle's cloud service terms (researched, pending exact-version verification).**
Oracle publishes the REST APIs and BICC as documented product surfaces of the Fusion Cloud Applications
subscription. Candidate paths BareCount researches:
- **REST API for Financials** (and sibling module APIs) — Oracle-published, documented per release ([REST API for Oracle Fusion Cloud Financials](https://docs.oracle.com/en/cloud/saas/financials/25d/farfa/index.html)).
- **BICC bulk extract** — Oracle's documented facility for exporting bulk data from Fusion Applications to object storage or UCM ([Creating a Business Intelligence Cloud Extract](https://docs.oracle.com/en/cloud/saas/applications-common/26b/biacc/creating-a-business-intelligence-cloud-extract.pdf)).
- Whether either surface, used by a third-party processor on the customer's behalf, is within the customer's subscription terms (Oracle Fusion Cloud Service agreements/Service Descriptions) is a **customer/Oracle determination** verified per engagement — ⧗ version-exact Service Description review pending.
- Paths BareCount does **not** research: direct database access (not offered on Fusion SaaS), screen-scraping, or any undocumented interface.

**4.A.2 Documentation copyright vs citation.** Oracle's public documentation (docs.oracle.com) is
vendor-copyrighted. BareCount cites it by URL + version + retrieval date (and digest, ⧗ pending) — it does not
reproduce it. Catalog seeds derived from the Tables-and-Views reference are provisional provenance, not copies
(see [catalog.md](catalog.md)).

**4.A.3 Read vs write-back.** BareCount reads only today. Fusion REST APIs also expose write operations; if an
Action Engine ever creates Fusion documents, the customer's subscription terms and Oracle's API policies for
write access must be resolved in the customer contract before activation.

**4.A.4 Quarterly-update support model (researched).** Oracle applies **mandatory quarterly updates** to Fusion
Cloud Applications (release labels 25C, 25D, 26A, …); per-release What's New readiness documents are published
per module (e.g. [Financials 25C](https://docs.oracle.com/en/cloud/saas/readiness/erp/25c/fins25c/index.html),
[Financials 25D](https://docs.oracle.com/en/cloud/saas/readiness/erp/25d/fins25d/index.html)). There is no
customer option to remain on an old release long-term; any BareCount realization must therefore be verified
against a moving release baseline. Exact update-policy document + retrieval date + digest ⧗ pending.

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)

What **any** Fusion customer must have/authorize before connection (stated generically — no named tenant, no
actual approval; those live in the governed substrate):
- **Vendor entitlement**: an active Oracle Fusion Cloud Applications subscription covering the modules in scope (Financials at minimum); BICC access requires the appropriate provisioning on the customer pod.
- **Licensing posture**: whether a dedicated integration user or additional API/extract usage carries subscription consequences is a **customer/Oracle determination**, not a BareCount conclusion — verify against the customer's ordering documents and Oracle's Service Descriptions.
- **Scope authorization**: internal approval to expose the selected modules/objects (GL/AP/AR/FA/PO entities) to an external processor.
- **Contractual/security approvals** that must exist (MSA/DPA/Order-Form/security-review) — referenced generically; the actual executed documents are governed-substrate objects, never recorded here.
- **Residency / retention / subprocessor** considerations for the customer's data leaving their Fusion pod (pod region, extract-storage location, BareCount as processor/subprocessor).
- **Customer-side authorizer roles**: the identity-domain administrator (Confidential Application + integration user), the subscription owner (API/extract usage sign-off), and the data/security approver for scope.

---

## 5. Commercial

General access-model and volume guidance (official/planning research; no tenant-specific commercial terms).

### 5.1 Customer access models

| Model | Path | Cost (Oracle) | Volume suitability |
|---|---|---|---|
| **REST API** | Fusion pod, OAuth via the instance's identity domain | Included surface of the subscription; any usage consequence is a customer/Oracle determination | Low–medium; row-level reads, delta by query filter |
| **BICC extract** | Fusion pod → OCI Object Storage / UCM | BICC is a documented Fusion facility; storage/egress costs are a customer/Oracle determination | High (bulk historical loads) |

Cost/permissibility per path is a **customer/Oracle determination** verified against the governed authority
objects (§4.A), not a BareCount conclusion.

### 5.2 Volume considerations

| Scenario | Typical volume | Candidate model |
|---|---|---|
| Initial historical load | 1M–100M records | BICC full extract |
| Daily delta admission | 1K–100K/day | REST query-filter polling or BICC incremental extract |
| Realtime/near-realtime | 100–10K/hour | REST polling (business-events trigger ⧗ unresearched officially) |

---

## 6. Technical

### 6.A Platform Plane — Oracle technical (general)

#### 6.1 Protocol

REST/JSON. Base path convention `https://<host>/fscmRestApi/resources/11.13.18.05/<resource>`; the resource
version `11.13.18.05` is stable across releases, and Oracle is introducing newer **v1 resources** under
`/api/boss/data/objects/.../v1/` for selected objects (per the [26B Quick Start](https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/Quick_Start.html)).
Collections return a default range size of 25; `describe` endpoints expose resource shape. Field selection,
expansion, and query filtering are per-resource — exact parameter dialect (⧗ per-resource verification pending
against the release-exact REST reference).

#### 6.2 Authentication

Per Oracle's REST documentation, Fusion REST APIs sit behind an Oracle Web Services Manager multi-token policy
supporting **Basic authentication over SSL, SAML 2.0 bearer, JWT in the HTTP header, and OAuth 2.0**; Oracle
recommends OAuth 2.0, and the newer v1 resources require an OAuth token from **OCI Identity and Access
Management (IAM)** (the identity domain associated with the Fusion instance; formerly standalone IDCS). OAuth
setup is via a **Confidential Application** in that identity domain with client-credentials (2-legged), JWT
assertion, or authorization-code (3-legged) flows ([Configure OAuth Using Oracle IDCS or IAM](https://docs.oracle.com/en/cloud/saas/sales/faaps/Configure_OAuth_Using_Oracle_IDCS_or_IAM.html),
[Configure OAuth Using the Fusion Applications Identity Domain](https://docs.oracle.com/en/cloud/saas/applications-common/24c/oaext/configure-oauth.html)).

Gap: no OCI-IAM OAuth client-credentials helper exists in `CredentialResolverService` (§8).

#### 6.3 Throughput / limits

Oracle does not publish explicit per-minute REST rate limits for Fusion; effective constraints are pod capacity
and fair use. Specific numeric limits previously noted in research (BICC per-view extract timeout, identity
trust-object caps) are ⧗ **pending official re-verification** — treat as unknown until a version-exact source is
pinned.

#### 6.4 Delta strategy

- REST: query-filter by date attributes (e.g. last-update date) — per-resource attribute availability ⧗ verification pending.
- BICC: documented **full and incremental** extract modes per data store.
- ERP Business Events (event-driven push) appear in Oracle's REST surface (`erpintegrations`-class resources) — ⧗ officially unresearched as a delta trigger; listed in §8.

#### 6.5 Schema discovery

Two official public surfaces, requiring no customer system: the **Tables and Views for Financials** reference
(release-exact table/column documentation, e.g. [25D edition](https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/index.html),
[GL_JE_LINES](https://docs.oracle.com/en/cloud/saas/financials/24a/oedmf/gljelines-22720.html)) and the REST
**describe** endpoint per resource. BICC additionally exposes its enabled data stores (view objects) per
offering ([BICC extract guide](https://docs.oracle.com/en/cloud/saas/applications-common/20b/biacc/get-started.html)).
See [catalog.md](catalog.md) for the seed footprint and its provisional-provenance status.

#### 6.6 Known semantics (design notes — verify per realization)

- **Subledger Accounting (XLA) → GL flow.** Subledger transactions (AP/AR/FA/…) are accounted by the **Create Accounting** process into subledger journal entries (XLA), then summarized and transferred/posted to General Ledger via the Post Subledger Journal Entries / Journal Import path ([Using Subledger Accounting, 25D](https://docs.oracle.com/en/cloud/saas/financials/25d/fausl/using-subledger-accounting.pdf)). A GL-balance metric and a subledger-detail metric therefore observe **different layers** of the same economics — the binding must name which layer.
- **Signed dual-column amounts.** Fusion GL journal lines carry separate debit and credit amount columns rather than an unsigned amount + sign indicator (contrast SAP `SHKZG`) — see [contracts.md](contracts.md) for the candidate OC pattern (⧗ column-level verification against the release-exact Tables-and-Views pages pending).
- **Flexfields.** Fusion uses key flexfields (e.g. the accounting flexfield / chart-of-accounts segments) and descriptive flexfields (customer-defined attribute columns). Per-customer flexfield configuration changes effective field semantics and must be verified per realization — never assumed from the seed catalog.

### 6.B Tenant Connection Plane — customer technical prerequisites (general)

What **any** Fusion customer must set up before a connection can be tested (general requirements; the
step-by-step execution runbook is §7, and concrete endpoints/accounts/results live only in the governed
substrate):
- **Customer-side setup**: a Confidential Application in the identity domain linked to the Fusion instance (REST path), and/or BICC access provisioned with the required offerings' data stores enabled (extract path).
- **Service account & minimum permissions**: a dedicated integration user with **read-only** job roles/privileges scoped to exactly the modules/objects in the agreed scope — no broader. Exact minimum role set per module ⧗ research pending.
- **Endpoint / network allow-listing**: the Fusion pod REST endpoint is public HTTPS; customer-side IP-allow-listing or an agreed extract-storage bucket (OCI Object Storage/UCM) as applicable.
- **Offerings/modules enabled**: only the Financials (and agreed sibling-module) resources/data stores in scope.
- **Connection-test & first-chain proof requirement**: token acquisition + one resource `describe` + one single-row read (REST), or one single-data-store extract (BICC), must pass before reader activation; a first governed chain run (SO→CO→MS) is the acceptance bar.
- **Release/customization verification**: confirm the pod's exact quarterly release (e.g. 25D) and the customer's flexfield/customization posture that alters standard field semantics (see [catalog.md](catalog.md) — universality is release-scoped).

---

## 7. Onboarding Runbooks

Execution history of these runbooks is logged in [onboarding-log.md](onboarding-log.md). **No run has ever been
executed** — these are designed procedures, unvalidated.

### 7.1 Customer-side — REST API path

1. **Confirm subscription scope.** Active Fusion Cloud Applications subscription covering the modules in scope.
2. **Create a Confidential Application** in the OCI IAM identity domain linked to the Fusion instance; configure the OAuth grant (client credentials for server-to-server) and scope.
3. **Create/designate an integration user** in Fusion with read-only job roles for the modules in scope; associate with the OAuth application per Oracle's OAuth configuration guide.
4. **Provision the credential via the approved secret-ingress mechanism (never person-to-person).** The customer submits the OAuth client secret (or certificate) through the governed secret store, which returns a `credential_ref` + receipt. Hand BareCount only the **pod base URL, the `credential_ref`, the OAuth scope, and the list of in-scope resources** — **never the raw secret.** No raw secret enters Git, a ticket, chat, email, the docket, or an audit artifact.

### 7.2 Customer-side — BICC extract path

1. Provision BICC access on the pod and enable the agreed offerings' data stores.
2. Configure the extract target (OCI Object Storage bucket or UCM) and schedule (full, then incremental).
3. Grant BareCount read access to the extract target via the governed secret-ingress mechanism (`credential_ref` + receipt — same rule as §7.1 step 4; never a raw secret).

### 7.3 BareCount-side

Per-tenant connection profile in `tbc_{slug}_dev`:

- `system_type_code: 'oracle_fusion'`
- `endpoint_url` (pod base URL)
- `auth.method: 'oauth2_client_credentials_oci'` (⧗ method not yet implemented — §8)
- `auth.credential_ref` — reference to a secret provisioned via the governed secret-ingress mechanism (yielding the `credential_ref` + receipt). Raw secrets never enter the DB, Git, tickets, chat, email, the docket, or any audit artifact — only the `credential_ref`.
- `module_scopes[]` — in-scope resources/data stores.

Smoke test: acquire token, `GET` one resource `describe`, then one single-row read — before activating any reader.

---

## 8. Known Gaps

1. **No self-service free/dev Fusion instance is known to be available** for platform engineering — no official Oracle source offering one has been found (⧗ unverified negative). Consequence: all current design is **documentation-driven only**; nothing has been executed against any Fusion instance.
2. **REST executor** — not built (Fusion path conventions, query-filter dialect, describe-driven shape checks).
3. **OCI IAM OAuth client-credentials helper** in `CredentialResolverService` — not built.
4. **BICC executor** — not built (drive extract job, admit CSV output + manifest from object storage).
5. **ERP Business Events** as a near-realtime delta trigger — officially unresearched.
6. **Quarterly-release feature drift** — new resources/attributes land each quarter; the catalog must be re-verified per release (see §4.A.4).
7. **Numeric limits re-verification** — BICC extract timeout, identity trust-object caps, POST batch limits previously noted in research lack pinned version-exact sources.
8. **Minimum read-only role set** per Financials module — not yet researched to the privilege level.
9. **No Oracle admission-stance ADR** (SAP analogue: D384) — needed before any clearance decision can exist.

---

## 9. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| Predecessor flat page (restructured into this docket) | `oracle-fusion.md` |
| Companion docket — SAP ECC | [sap-ecc/index.md](../sap-ecc/index.md) |
| REST API for Oracle Fusion Cloud Financials (25D) | https://docs.oracle.com/en/cloud/saas/financials/25d/farfa/index.html |
| REST API Quick Start (26B — base path, multi-token auth policy, v1 resources) | https://docs.oracle.com/en/cloud/saas/financials/26b/farfa/Quick_Start.html |
| Tables and Views for Financials (25D) | https://docs.oracle.com/en/cloud/saas/financials/25d/oedmf/index.html |
| Tables and Views — GL_JE_LINES | https://docs.oracle.com/en/cloud/saas/financials/24a/oedmf/gljelines-22720.html |
| Creating a Business Intelligence Cloud Extract (BICC, 26B) | https://docs.oracle.com/en/cloud/saas/applications-common/26b/biacc/creating-a-business-intelligence-cloud-extract.pdf |
| BICC get-started (enabled data stores by offering) | https://docs.oracle.com/en/cloud/saas/applications-common/20b/biacc/get-started.html |
| Configure OAuth Using Oracle IDCS or IAM | https://docs.oracle.com/en/cloud/saas/sales/faaps/Configure_OAuth_Using_Oracle_IDCS_or_IAM.html |
| Configure OAuth Using the Fusion Applications Identity Domain (24C) | https://docs.oracle.com/en/cloud/saas/applications-common/24c/oaext/configure-oauth.html |
| Using Subledger Accounting (25D) | https://docs.oracle.com/en/cloud/saas/financials/25d/fausl/using-subledger-accounting.pdf |
| Financials 25C What's New (quarterly readiness) | https://docs.oracle.com/en/cloud/saas/readiness/erp/25c/fins25c/index.html |
| Financials 25D What's New (quarterly readiness) | https://docs.oracle.com/en/cloud/saas/readiness/erp/25d/fins25d/index.html |
| Oracle Fusion Cloud Service Descriptions | https://www.oracle.com/contracts/docs/oracle-fusion-cloud-service-desc-1843611.pdf |

## 10. Changelog

- **2026-07-13** — authored `oracle-fusion/` docket per **DEC-8570d4 (D526)**, restructuring the flat `oracle-fusion.md` page into the docket shape (mirroring the accepted `sap-ecc/` exemplar). Re-verified core facts against official Oracle documentation (REST base path + multi-token auth policy, OCI IAM OAuth via Confidential Application, Tables-and-Views 25D, BICC extract guide, 25C/25D quarterly readiness, XLA subledger→GL flow). Facts from prior research lacking a version-exact official source (numeric limits, business-events trigger, OAuth scope strings) downgraded to ⧗ pending. `proof_status: designed`; no evidence of any kind exists.
