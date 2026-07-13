---
uid: SRC-b4c92d
slug: sap-ecc
title: "SAP ECC"
description: "SAP ECC admission research: candidate access paths (Gateway-published OData, customer ABAP transport) under the SAP API Policy; permissibility per customer/release is a clearance decision against the governed authority objects, not asserted here."
type: source-systems
status: published
domain: enterprise-erp
subdomain: sap
focus: governance
authority_role: projection        # D526 Amendment 1 — projection, not an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. Requires governed evidence. ---
proof_status: designed            # Codex P0-2: downgraded from shape_tested — NO governed evidence object exists yet; the bc-sdg simulator run is ungoverned historical background (see evidence.md). Promote only when a governed proof-scope/evidence object is minted.
proof_scope_refs: []              # governed source-proof-scope UID — none yet
source_realization_refs: []       # governed source-realization-package UID — none yet
audit_decision_refs: []           # signed audit-decision UID — none (no realization audit run for ECC yet)
# --- exact governed reference coordinates (Codex P1-4) — authority is the REFERENCED object, not these strings; ⧗ = capability/registration pending ---
source_registry_ref: null         # SRC registry UID + exact provider/system/release (⧗ pending source-registration)
reader_flavor_versions: []        # exact reader-flavor version UID + digest (⧗ pending; slug below is a label only)
catalog_root: null                # source-catalog snapshot / mapping-root digest (⧗ pending)
contract_set_ref: null            # SC/AC/OC/CC version-set UID or contract-set digest (⧗ pending)
admission_contract_versions: []   # AC version UIDs realized against ECC — none authored (see contracts.md)
official_research_refs: []        # structured {source, version, retrieved_at, digest} per official citation (⧗ digest capture pending — 3rd capability gate)
last_verified_at: 2026-04-28
official_docs_url: https://help.sap.com/docs/SAP_ERP
system_type_code: sap_ecc         # label; authority = source_registry_ref
reader_flavors:
  - sap-ecc-odata-v2              # label; authority = reader_flavor_versions[]
catalog_ref: catalog.md           # human link; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-d2cdb9   # D384 — SAP API admission stance
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendments 1/2/3)
supersedes: legacy-v2-archive/docs/reference/sources/sap-ecc.md
---

# SAP ECC

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions (D525). `proof_status` below is **evidence maturity,
> not an audit verdict**. Reference narrative is here; concrete artifacts are referenced via the sibling files
> under [Docket Contents](#docket-contents).

SAP ECC (ERP Central Component) is SAP's classic on-premise ERP system. Unlike S/4HANA, ECC predates the CDS-view API layer and historically exposed data through transparent tables, BAPIs, RFCs, and DataSources. Under the **SAP API Policy** (DEC-d2cdb9 / D384) BareCount researches Gateway-published OData services (when available) and customer-initiated ABAP transport runs (Indirect Static Read) as **candidate access paths**; the ODP RFC delta interface is restricted for third-party use per SAP Note 3255746. Which path is permissible for a given customer/release is a **clearance decision** made against the governed authority objects (see §4.A), not asserted here.

SAP mainstream maintenance for ECC ends in **2027**; extended maintenance is available through **2030** at additional cost. Customers are expected to migrate to S/4HANA. BareCount supports ECC for the remaining maintenance window and recommends planning the S/4HANA migration path.

This page is governed by **DEC-d2cdb9 (D384)** — the same SAP API admission stance applies to ECC as to S/4HANA.

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / commercial / technical / gaps), onboarding runbooks, references, changelog |
| [contracts.md](contracts.md) | Contracts authored against ECC + the sign-indicator OC pattern |
| [catalog.md](catalog.md) | ECC transparent-table catalog footprint (BKPF/BSEG/BSID/BSAD, …) |
| [onboarding-log.md](onboarding-log.md) | Dated onboarding-execution log |
| [evidence.md](evidence.md) | Proof entries — bc-sdg simulator coverage; first-hand pending |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1).

**Evidence maturity — `designed`** as of 2026-04-28. Evidence maturity requires *governed* evidence; none exists for ECC yet, so no maturity above `designed` can be projected (Codex P0-2).

- **Ungoverned historical background (not a maturity claim):** the OData V2 executor (`bc-core/src/boundary/reader-runtime/executors/sap-odata-v2.executor.ts`) was exercised against the BareCount internal SAP ECC **simulator profile** at `bc-sdg` port 6100 (mimicking ECC OData V2 shapes — `/Date(epoch)/`, `__metadata`, `$skiptoken`, CSRF). This proved **conformance to the declared simulator profile — not SAP ECC itself**, and it is **not a governed evidence object** (no UID/digest). It cannot lift `proof_status` on its own. See [evidence.md](evidence.md).
- **Zero validation against a real SAP ECC tenant.** No customer Gateway service or ABAP transport run has produced admissions through the BareCount chain.
- Promotion to `shape_tested` requires a **minted governed proof-scope/evidence object** with `proof_scope_refs[]` / `source_realization_refs[]` populated; `first_hand_proven` requires a real-instance entity/scope-specific governed evidence entry — **never** a whole-system promotion of "SAP ECC."
- Zero-claims rule (D385): until a real ECC instance has produced metric snapshots end-to-end, **no external "we work with SAP ECC" claim may be made.**

**Audit decision — none.** No source-realization audit (D525) has been run for SAP ECC; `audit_decision_refs[]` is empty. PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit substrate against an exact realization package; this docket would only ever render such a decision as a labelled "derived projection" with its governed UID/digest, never as its own authority. `shape_tested` does **not** imply PASS.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `sap-ecc-odata-v2` | SAP ECC with SAP Gateway Foundation activated | `SapOdataV2Executor` | — (not yet built for real ECC) |

The simulator-shaped reader binding used in current testing is the same flavor configured against the bc-sdg simulator endpoint. The first real ECC tenant will require a real Communication Arrangement-equivalent setup on the customer's Gateway.

---

## 3. What BareCount Admits

### 3.1 Metadata

Classic ABAP Dictionary table field definitions: field names, data types (`CHAR`, `CURR`, `DEC`, `DATS`, etc.), key indicators, domain references, foreign-key relationships. Stored as Tier 5/6 entries in the Source Catalog — see [catalog.md](catalog.md).

### 3.2 Business data

Posted business records from ECC transparent tables — accounting documents (BKPF/BSEG/BSID/BSAD), purchase orders (EKKO/EKPO), material masters (MARA/MARC/MARD), goods movements (MSEG/MKPF), customer and vendor masters (KNA1/KNB1, LFA1/LFB1). Admitted via Gateway-published OData when activated, or as JSON output of a customer-initiated ABAP report run. Cataloged in [catalog.md](catalog.md).

ECC differs from S/4HANA in that it has **no CDS view layer**. The "object" we observe is the underlying transparent table (or its view), not a semantic CDS model. Canonical resolution does the same job either way; only the binding differs.

---

> **Scope of §4–§6 (D526 Amendment 1).** Official, general research only — SAP policy and the requirements any
> customer must satisfy. **No** tenant names, contracts, credentials, endpoints, approvals, or legal conclusions:
> those are governed-substrate objects referenced by pseudonymous UID/digest from onboarding-log.md / evidence.md.
> Retrieval date + digest for each official source are pinned in [References](#9-references) (⧗ digest TODO).

## 4. Legal & Licensing

### 4.A Platform Plane — SAP legal & licensing (general)

> **Researched candidate paths and conditions — NOT clearance conclusions (Codex P0-3).** Nothing here is
> "sanctioned" or "banned" by BareCount assertion. Each condition holds only as supported by a **version-exact**
> official SAP source (recorded in `official_research_refs[]` with retrieval date + exact version + content
> digest — ⧗ digest capture pending, 3rd capability gate) and, at runtime, by an exact-release **Platform Source
> Access Policy** plus the customer's **Tenant Source Authorization** (deferred governed authority objects,
> AuditHub/bc-core-owned). Which path is permissible for a given customer/release is a **clearance decision**
> made against those objects — not asserted here. This is assurance research, not legal advice.

**4.A.1 Access paths under the SAP API Policy (researched, pending exact-release verification).** The current
[SAP API Policy](https://help.sap.com/doc/sap-api-policy/latest/en-US/API_Policy_latest.pdf) distinguishes
Published APIs from non-published interfaces and restricts systematic/large-scale extraction to SAP-endorsed
pathways; it does **not** render every Gateway-published custom service or every ABAP extraction automatically
permitted. Candidate paths BareCount researches for ECC:
- **Gateway-published OData** (customer's SAP_GWFND add-on) — *where the service qualifies as a Published API* under the policy.
- **Customer-initiated ABAP report execution** under the customer's own licensed user — SAP's **Indirect Static Read** guidance ([Indirect Access guide](https://news.sap.com/wp-content/blogs.dir/1/files/Indirect_Access_Guide_for_SAP_Installed_Base.pdf)) is **conditional** and does not replace the customer's contract or a current clearance decision.
- **BTP Integration Suite iFlow** for customers running BTP alongside ECC.
- Paths BareCount does **not** use: ODP RFC modules (restricted per SAP Note 3255746), undocumented/non-Gateway direct table reads, scraping/screen-reading.

**4.A.2 Read vs write-back.** BareCount reads only today. If an Action Engine ever creates SAP documents, SAP **Digital Access** licensing considerations apply and must be resolved in the customer contract before activation.

**4.A.3 User types (a technical type, not a licence category).** SAP describes **Communication/Communications** users as a technical **user type** for machine access ([SAP technical-user guidance](https://help.sap.com/docs/ABAP_PLATFORM_NEW/ad77b44570314f6d8c3a8a807273084c/c548fea2a3784ab39a1ba5b1d69ccdcf.html)), distinct from a human Named user — **not, by itself, a commercial licence category.** Machine integrations should use a technical user type; any commercial-licensing consequence is a customer/SAP determination, not a BareCount conclusion.

**4.A.4 Maintenance/support horizon (researched).** Per SAP's [Business Suite 7 maintenance strategy](https://support.sap.com/en/release-upgrade-maintenance/maintenance-information/maintenance-strategy/s4hana-business-suite7.html3.html), ECC mainstream maintenance runs to 2027 with extended maintenance available thereafter at additional cost. Exact version + retrieval date + digest ⧗ pending. Bounds ECC-specific engineering investment.

Full SAP-side licensing research + public catalogue sources: [sap-licensing-reference.md](../sap-licensing-reference.md).

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)

What **any** ECC customer must have/authorize before connection (stated generically — no named tenant, no actual approval; those live in the governed substrate):
- **Vendor entitlement**: either an activated **SAP_GWFND** add-on (for the OData path) or an ABAP-capable licensed user (for the Indirect Static Read / transport path).
- **Licensing posture**: a technical (Communication-type) user available for machine access; any Digital Access licensing considerations resolved *only if* write-back is ever in scope. Commercial-licence consequences are a customer/SAP determination, not a BareCount conclusion.
- **Scope authorization**: internal approval to expose the selected modules/tables (FI/MM/SD entities) to an external processor.
- **Contractual/security approvals** that must exist (MSA/DPA/Order-Form/security-review) — referenced generically; the actual executed documents are governed-substrate objects, never recorded here.
- **Residency / retention / subprocessor** considerations for the customer's data leaving ECC.
- **Customer-side authorizer roles**: Basis (Gateway/service activation, user creation), the SAP licence owner (Communication User + Digital Access sign-off), and the data/security approver for scope.

---

## 5. Commercial

General access-model and volume guidance (official/planning research; no tenant-specific commercial terms).

### 5.1 Customer access models (post-Policy v.4/2026)

| Model | Path | Cost (SAP) | Volume suitability |
|---|---|---|---|
| **Gateway-published OData** | ECC + SAP_GWFND add-on | Requires SAP_GWFND (not universal on ECC); cost is a customer/SAP determination | Low–medium realtime |
| **Customer ABAP Transport (Indirect Static Read)** | ECC, no add-on required | No BareCount add-on; SAP cost/licensing is a customer/SAP determination | High (direct table read) |
| **BTP iFlow** | ECC + BTP subscription | Requires a BTP subscription; cost is a customer/SAP determination; ODP RFC (OHD/ODQ) delta interfaces restricted per SAP Note 3255746 | High |

Cost/permissibility per path is a **customer/SAP determination** verified against the governed authority objects (§4.A), not a BareCount conclusion. The previous v2 framing of "Named User Consultant Access" is dropped as a wrong-model access pattern.

### 5.2 Volume considerations

| Scenario | Typical volume | Recommended model |
|---|---|---|
| Initial historical load | 1M–100M records | ABAP Transport (one-shot full export) |
| Daily delta admission | 1K–100K/day | Gateway OData or daily ABAP Transport run |
| Realtime/near-realtime | 100–10K/hour | Gateway OData polling |

---

## 6. Technical

### 6.A Platform Plane — SAP technical (general)

#### 6.1 Protocol

OData V2 for Gateway-published services (V4 not generally available on classic ECC). JSON or XML payloads. `$top`/`$skip` pagination, `$inlinecount` for totals, `$filter` for incremental loads, CSRF token flow.

The V2 executor (`SapOdataV2Executor`) handles:

1. CSRF token fetch (`x-csrf-token: Fetch`) and echo on subsequent requests.
2. Paginated query loop with configurable batch size; auto-stops at 100 pages as a safety cap.
3. `$inlinecount=allpages` on the first page for totals.
4. SAP-specific `/Date(epochMs)/` decoding to ISO timestamps; `__metadata` and `__deferred` stripped.
5. SAP-specific headers (`sap-client`, `sap-language`, `Accept: application/json`).

#### 6.2 Authentication

Supported today via `CredentialResolverService`:

- **Basic Auth** (technical user + password over TLS) — common for on-prem.
- **Bearer token** (OAuth 2.0) — when an OAuth proxy is configured.

Gap: mTLS / X.509 client cert not yet a first-class method on `ResolvedCredentials`.

#### 6.3 Throughput

ECC Gateway services have per-system rate limits configurable by Basis. The executor does not yet implement adaptive backoff. Listed in §8 Known Gaps.

#### 6.4 Delta strategy

- `$filter` by date field (`BUDAT`, `CPUDT`, `LAEDA`).
- The DataSource **ODP RFC** delta interface is **restricted for third-party use** per SAP Note 3255746 (exact interface + authority named) — BareCount does not use it. This is the cited SAP restriction, not a BareCount conclusion.
- ABAP Transport export can carry a delta flag if the report logic implements it.

#### 6.5 Schema discovery

OData `$metadata` document at the service root yields entity types and key fields. Public catalogues (`leanx.eu`, `se80.co.uk`) cover ECC table definitions for catalogue seed without touching a customer system — see [catalog.md](catalog.md).

#### 6.6 Network plumbing

- Gateway services: HTTPS direct, IP-allowlist as needed.
- ABAP Transport: customer runs `ZBCNT_META_EXPORT` and uploads JSON via the agreed channel — no live BareCount-to-ECC connection required for this path.

### 6.B Tenant Connection Plane — customer technical prerequisites (general)

What **any** ECC customer must set up before a connection can be tested (general requirements; the step-by-step
execution runbook is §7, and concrete endpoints/accounts/results live only in the governed substrate):
- **Customer-side setup**: activate SAP_GWFND and the required OData service in `/IWFND/MAINT_SERVICE` (OData path), **or** import + run the BareCount ABAP transport under a licensed user (transport path).
- **Service account & minimum permissions**: a Communication-class technical user with **read-only** authorisations scoped to exactly the activated services/entities — no broader.
- **Endpoint / network allow-listing**: reachable Gateway HTTPS endpoint with IP-allowlisting (or BTP Cloud Connector); for the transport path, an agreed drop channel (S3/SFTP/signed URL).
- **Modules/entities to enable**: only the FI/MM/SD services/tables in the agreed scope.
- **Connection-test & first-chain proof requirement**: `/$metadata` reachability + one entity `$top=1` read must pass before reader activation; a first governed chain run (SO→CO→MS) is the acceptance bar.
- **Release/customization verification**: confirm the exact ECC release/support-package and any industry-extension/customizing that alters standard field semantics (see [catalog.md](catalog.md) — universality is release-scoped).

---

## 7. Onboarding Runbooks

Execution history of these runbooks is logged in [onboarding-log.md](onboarding-log.md).

### 7.1 Customer-side — Gateway-published OData path

1. **Verify Gateway availability.** SAP Gateway Foundation (`SAP_GWFND`) must be installed; this is **not** universal on ECC. Check with Basis.
2. **Activate the OData service** in `/IWFND/MAINT_SERVICE` for the entity BareCount needs (e.g. a custom CDS-View-equivalent or a SEGW-built service over the relevant tables).
3. **Create a technical (Communication-type) user** with read-only authorisations on the activated services.
4. **Choose network path**: direct VPN/IP allowlist, or BTP Cloud Connector if available.
5. **Provision the credential via the approved secret-ingress mechanism (never person-to-person).** The customer submits the technical-user secret through the governed secret store, which returns a `credential_ref` + receipt. Hand BareCount only the **endpoint URL, the `credential_ref`, and the list of activated services** — **never the raw secret.** No raw secret enters Git, a ticket, chat, email, the docket, or an audit artifact.

### 7.2 Customer-side — ABAP Transport path

1. Receive the BareCount-published transport (`ZBCNT_META_EXPORT` or business-data variant).
2. Import via STMS into a development client; promote to production after Basis review.
3. Run the report under a customer-licensed user — Indirect Static Read.
4. Send the JSON output to BareCount via the agreed channel (S3 dropbox, SFTP, signed URL).

### 7.3 BareCount-side

Per-tenant connection profile in `tbc_{slug}_dev`:

- `system_type_code: 'sap_ecc'`
- `endpoint_url`
- `auth.method: 'basic' | 'bearer'`
- `auth.credential_ref` — reference to a secret provisioned via the governed secret-ingress mechanism (yielding the `credential_ref` + receipt). Raw secrets never enter the DB, Git, tickets, chat, email, the docket, or any audit artifact — only the `credential_ref`.
- `sap_client` (e.g. `100`)
- `sap_language` (default `'EN'`)
- `gateway_services[]` — list of activated services we may call.

Smoke test: hit `/$metadata` then one entity with `$top=1` before activating the reader.

---

## 8. Known Gaps

1. **Real-tenant Gateway OData** end-to-end — not yet exercised.
2. **mTLS / X.509 client cert** auth — not yet a first-class method on `ResolvedCredentials`.
3. **BTP Cloud Connector** integration for ECC-on-prem.
4. **Adaptive throttle / backoff** for Gateway rate limits.
5. **Delta strategies beyond `$filter` by date** — would require per-entity decision (no OData V4 `$delta` support on classic ECC).
6. **ABAP Transport runbook** — needs documented onboarding playbook (current text is procedural sketch).
7. **Catalogue of which ECC entities have S/4HANA Public OData equivalents** — informs migration conversations with prospective customers.

---

## 9. References

| Resource | Link |
|---|---|
| ADR — SAP API admission stance (D384) | [ADR-d2cdb9](../../../governance/adrs/ADR-d2cdb9.md) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| Companion source page | [SAP S/4HANA](../sap-s4hana.md) |
| Companion appendix — SAP licensing & catalogue rules | [sap-licensing-reference.md](../sap-licensing-reference.md) |
| SAP API Policy v.4/2026 | https://www.sap.com/docs/download/2026/04/dce9aee4-497f-0010-bca6-c68f7e60039b.pdf |
| SAP Note 3255746 (ODP RFC ban) | https://me.sap.com/notes/3255746 |
| SAP ERP Help Portal | https://help.sap.com/docs/SAP_ERP |
| SAP Gateway Foundation | https://help.sap.com/docs/SAP_NETWEAVER_750/68bf513362174d54b58cddec28794093 |
| leanx.eu SAP table reference | https://leanx.eu/en/sap/table/ |
| Predecessor — legacy v2 SAP ECC reference | legacy-v2-archive/docs/reference/sources/sap-ecc.md |

## 10. Changelog

- **2026-07-13** — migrated flat `sap-ecc.md` → `sap-ecc/` docket folder per **DEC-8570d4 (D526)**. Reference narrative kept in `index.md`; sign-indicator OC pattern → `contracts.md`; table footprint → `catalog.md`; onboarding runbooks retained here with execution log in `onboarding-log.md`; simulator proof → `evidence.md`. Relative links re-depthed one level; inbound links rewritten. Content otherwise unchanged.
- **2026-07-07** — added Source-System Semantics: Sign Handling (SHKZG debit/credit indicator on BSID/BSAD/BSIK/BSAK/BSEG, the `role: "sign_indicator"` OC pattern, currency rounding). Per TSK-04e6df ERP pitfall remediation. Now relocated to [contracts.md](contracts.md) §Sign-indicator OC pattern.
- **2026-04-28** — initial v3 page. Supersedes `legacy-v2-archive/docs/reference/sources/sap-ecc.md`. Reconciled against **DEC-d2cdb9 (D384)**. *[Superseded wording: this entry's original "Gateway-published OData = sanctioned" and `proof_status: shape_tested` framings are superseded by the 2026-07-13 docket migration + Amendment 3 — access paths are now researched candidates pending the governed authority objects (§4.A), and maturity is `designed`. Retained here only as historical record.]* Dropped Named User access model. Maintenance-window framing tightened (2027 mainstream, extended thereafter).
