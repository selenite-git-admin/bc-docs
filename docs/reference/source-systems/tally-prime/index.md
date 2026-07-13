---
uid: SRC-b3e7c2
slug: tally-prime
title: "Tally Prime"
description: "Tally Prime admission research: candidate access paths (XML request/response over HTTP on the Tally gateway port, ODBC read, TDL-based exports) for a customer-hosted desktop accounting system; permissibility per customer/release is a clearance decision against the governed authority objects, not asserted here."
type: source-systems
status: published
domain: accounting
subdomain: tally
focus: governance
authority_role: projection        # D526 Amendment 1 — projection, not an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. Requires governed evidence. ---
proof_status: designed            # NO governed evidence object exists; no executor, no simulator profile, no customer engagement. Promote only when a governed proof-scope/evidence object is minted.
proof_scope_refs: []              # governed source-proof-scope UID — none
source_realization_refs: []       # governed source-realization-package UID — none
audit_decision_refs: []           # signed audit-decision UID — none (no realization audit run for Tally Prime)
# --- exact governed reference coordinates — authority is the REFERENCED object, not these strings; ⧗ = capability/registration pending ---
source_registry_ref: null         # SRC registry UID + exact provider/system/release (⧗ pending source-registration)
reader_flavor_versions: []        # exact reader-flavor version UID + digest (⧗ pending; no flavor built — see §2)
catalog_root: null                # source-catalog snapshot / mapping-root digest (⧗ pending)
contract_set_ref: null            # SC/AC/OC/CC version-set UID or contract-set digest (⧗ pending)
admission_contract_versions: []   # AC version UIDs realized against Tally Prime — none authored (see contracts.md)
official_research_refs: []        # structured {source, version, retrieved_at, digest} per official citation (⧗ digest capture pending — 3rd capability gate)
last_verified_at: 2026-07-13
official_docs_url: https://help.tallysolutions.com/integration-with-tallyprime/
system_type_code: tally_prime     # label; authority = source_registry_ref
reader_flavors: []                # none registered; candidate flavor labels listed in §2 only
catalog_ref: catalog.md           # human link; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendments 1/2/3)
supersedes: docs/reference/source-systems/tally-prime.md
---

# Tally Prime

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions (D525). `proof_status` below is **evidence maturity,
> not an audit verdict**. Reference narrative is here; concrete artifacts are referenced via the sibling files
> under [Docket Contents](#docket-contents).

Tally Prime (Tally Solutions Pvt. Ltd.) is a desktop accounting and business-management application widely used by small and mid-size businesses, particularly in India. It is **customer-hosted, on-premise, desktop-class software**: company data lives in local company data files on the customer's machine or LAN server, and the application — not a vendor cloud — is the integration endpoint. There is no vendor-hosted API for a customer's books; every integration surface (XML request/response over HTTP on the Tally gateway port, ODBC read, TDL-based exports) is served by the customer's own running TallyPrime instance, which is frequently **not internet-exposed**. This shapes everything below: network path and access control are the dominant onboarding questions, not API entitlement tiers.

Under the Source Systems framework (**DEC-6cb4f3 / D385**) BareCount researches the officially documented integration surfaces as **candidate access paths**. Which path is permissible and workable for a given customer/release is a **clearance decision** made against the governed authority objects (see §4.A), not asserted here.

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / commercial / technical / gaps), onboarding runbooks, references, changelog |
| [contracts.md](contracts.md) | Contracts authored against Tally Prime (none yet) + candidate OC-pattern questions |
| [catalog.md](catalog.md) | Candidate Tally object footprint (vouchers, ledgers, masters) — all registration pending |
| [onboarding-log.md](onboarding-log.md) | Dated onboarding-execution log (empty — no runs) |
| [evidence.md](evidence.md) | Proof entries — none; no simulator coverage; first-hand pending |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1).

**Evidence maturity — `designed`** as of 2026-07-13. Evidence maturity requires *governed* evidence; none exists for Tally Prime, so no maturity above `designed` can be projected.

- **No executor exists** for any Tally surface (XML-over-HTTP, ODBC, or agent-bridged) in the BareCount reader runtime.
- **No simulator coverage exists.** Unlike SAP ECC, there is no bc-sdg Tally profile — there is not even ungoverned historical background to index. See [evidence.md](evidence.md).
- **Zero validation against a real TallyPrime instance.** No customer or vendor instance has produced admissions through the BareCount chain.
- Promotion to `shape_tested` requires a **minted governed proof-scope/evidence object** with `proof_scope_refs[]` / `source_realization_refs[]` populated; `first_hand_proven` requires a real-instance entity/scope-specific governed evidence entry — **never** a whole-system promotion of "Tally Prime."
- Zero-claims rule (D385): until a real TallyPrime instance has produced metric snapshots end-to-end, **no external "we work with Tally" claim may be made.**

**Audit decision — none.** No source-realization audit (D525) has been run for Tally Prime; `audit_decision_refs[]` is empty. PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit substrate against an exact realization package; this docket would only ever render such a decision as a labelled "derived projection" with its governed UID/digest, never as its own authority.

---

## 2. Reader Flavor Binding

**Empty (`reader_flavors: []`)** — no reader flavor is registered or built for Tally Prime. Candidate flavor *labels* when scoping begins (labels only; authority would be `reader_flavor_versions[]`):

| Candidate flavor (label) | Target surface | Status |
|---|---|---|
| `tally-prime-xml` | XML request/response over HTTP against the TallyPrime gateway port (default 9000) | ⧗ not built |
| `tally-prime-odbc` | ODBC read against the TallyPrime ODBC server | ⧗ not built |
| `tally-prime-export` | TDL-based export files delivered via an agreed drop channel (no live connection) | ⧗ not built |
| `tally-prime-agent` | BareCount-deployed local agent bridging a non-internet-exposed instance over an outbound TLS tunnel | ⧗ not built (significant build — see §8) |

No AC version exists for any of these (see [contracts.md](contracts.md)).

---

## 3. What BareCount Admits

Planned admission scope — nothing below is registered or contracted yet (see [catalog.md](catalog.md)).

### 3.1 Metadata

Company master definitions: chart of accounts (ledgers and ledger groups), voucher type definitions (sales, purchase, journal, payment, receipt, contra, debit/credit note), cost centres, stock groups/items/units, and tax configuration (e.g. GST details for Indian deployments). Discoverable via XML `Export` requests, TDL collections, or the ODBC catalog — see §6.5.

### 3.2 Business data

Posted voucher records (sales, purchase, journal, payment, receipt, contra, debit/credit notes), ledger balances and transaction history, and stock movement records — scoped per company dataset (TallyPrime organizes books as per-company data files; a multi-company installation exposes each loaded company separately). Admitted via XML request/response over HTTP, ODBC read, or TDL-based export files.

Tally Prime has no service-oriented semantic model layer; the "object" observed is the TDL-defined report/collection or ODBC table projection over the company data file. Canonical resolution does the same job either way; only the binding differs.

---

> **Scope of §4–§6 (D526 Amendment 2).** Official, general research only — vendor policy and the requirements any
> customer must satisfy. **No** tenant names, contracts, credentials, endpoints, approvals, or legal conclusions:
> those are governed-substrate objects referenced by pseudonymous UID/digest from onboarding-log.md / evidence.md.
> Retrieval date + digest for each official source are pinned in [References](#9-references) (⧗ digest TODO).

## 4. Legal & Licensing

### 4.A Platform Plane — Tally legal & licensing (general)

> **Researched conditions — NOT clearance conclusions.** Nothing here is "sanctioned" or "banned" by BareCount
> assertion. Each condition holds only as supported by a **version-exact** official Tally Solutions source
> (recorded in `official_research_refs[]` with retrieval date + exact version + content digest — ⧗ digest capture
> pending, 3rd capability gate) and, at runtime, by an exact-release **Platform Source Access Policy** plus the
> customer's **Tenant Source Authorization** (deferred governed authority objects). Which path is permissible for
> a given customer/release is a **clearance decision** made against those objects — not asserted here. This is
> assurance research, not legal advice.

**4.A.1 Licence model (researched).** Per official Tally licensing documentation
([TallyPrime licensing](https://help.tallysolutions.com/licensing-tallyprime/), [buy page](https://tallysolutions.com/buy-tally/)):
- **Silver** — single-user edition. **Gold** — multi-user edition for unlimited users on a LAN (licence activated on one system and shared to clients on the network).
- Commercial forms: **rental** (subscription for a defined period) and **perpetual** licence; a perpetual licence includes a one-year **Tally Software Services (TSS)** subscription, and upgrade to the latest release is gated on a valid TSS.
- Activation is via the customer's Tally.NET ID. A separate **Tally Virtual User (TVU)** licence type exists for virtualized access (RDP/thin client/Citrix), and a vendor cloud-access offering exists — these are customer-side deployment variants, not BareCount access paths.
- ⧗ Whether an integration connection consumes a user slot on a Silver (single-user) licence, and any licence terms specific to programmatic access, are **not answered by the pages reviewed** — pending version-exact verification of the licence agreement before any clearance decision.

**4.A.2 Integration terms — read vs write-back.** The official XML interface is bidirectional: `TALLYREQUEST` supports `Import`, `Export`, and `Execute`, and `Import` requests can **write vouchers and masters into Tally** ([XML integration](https://help.tallysolutions.com/xml-integration/)). **BareCount's posture is read-only**: only `Export`-class reads are in scope. Write-back (voucher creation) would be a separate governed decision with its own customer authorization — never activated implicitly.

**4.A.3 Support/version horizon (researched).** TallyPrime is actively maintained: official release notes cover releases 4.0 through **7.1** (current at retrieval, release notes updated 2026-05) ([release notes 7.1](https://help.tallysolutions.com/release-notes-tallyprime-7-1/)). A **TallyPrime Edit Log** variant exists alongside the standard release. Release upgrades are TSS-gated (§4.A.1), so a customer's installed release may lag the current one — release verification is a tenant-connection prerequisite (§6.B). No end-of-maintenance date for TallyPrime is published on the pages reviewed; ⧗ pending.

**4.A.4 No published third-party API policy located.** The pages reviewed document integration *mechanisms*, not a distinct third-party extraction/API policy of the SAP-API-Policy kind. Absence of a located policy is **not** clearance — the customer's licence agreement governs, and its integration-relevant terms are ⧗ pending version-exact verification.

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)

What **any** TallyPrime customer must have/authorize before connection (stated generically — no named tenant, no actual approval; those live in the governed substrate):
- **Valid Tally licence**: an active TallyPrime licence (Silver or Gold; rental or perpetual) covering the installation that will serve the integration surface. Educational-mode installations are not a valid basis for a production connection.
- **Licensing posture**: confirmation with the customer (and, where unclear, with Tally Solutions or their partner) that programmatic read access under their licence and edition is in order — a customer/vendor determination, not a BareCount conclusion.
- **Scope authorization**: internal approval to expose the selected company dataset(s) — and only those — to an external processor. TallyPrime is per-company-file; scope is naturally expressed as "which companies."
- **Contractual/security approvals** that must exist (MSA/DPA/Order-Form/security-review) — referenced generically; the actual executed documents are governed-substrate objects, never recorded here.
- **Residency / retention / subprocessor** considerations: the books are **customer-hosted on-premise data**; the connection moves accounting data off the customer's premises for the first time in many deployments, so residency, retention, and any subprocessor chain (e.g. a tunnel or agent relay) require explicit customer sign-off.
- **Customer-side authorizer roles** (generic): the business owner/finance controller who owns the books, the IT/network owner who authorizes gateway/ODBC enablement and the network path, and the data/security approver for scope and egress.

---

## 5. Commercial

General access-model guidance (official/planning research; no tenant-specific commercial terms, no readiness or ordering claims).

| Model | Path | Cost (vendor side) | Notes |
|---|---|---|---|
| **XML over HTTP (direct)** | Customer's running TallyPrime, gateway port reachable | Covered by the customer's TallyPrime licence; any incremental cost is a customer/Tally determination | Requires network reachability (§6.6) |
| **ODBC read** | Customer's running TallyPrime with ODBC enabled | As above | LAN-local by nature; remote use needs a network path |
| **TDL export drop** | Customer runs exports; files delivered via agreed channel | As above | No live connection required |
| **Agent bridge** | BareCount agent on/near the Tally host, outbound tunnel | Vendor cost as above; agent is BareCount-side build (§8) | For non-internet-exposed instances |

Vendor pricing (rental and perpetual, Silver and Gold) is published by Tally Solutions ([buy page](https://tallysolutions.com/buy-tally/)); per-customer cost and permissibility are a **customer/Tally determination** verified against the governed authority objects (§4.A), not a BareCount conclusion.

---

## 6. Technical

### 6.A Platform Plane — Tally technical (general)

#### 6.1 Protocol

Officially documented integration surfaces ([integration overview](https://help.tallysolutions.com/integration-with-tallyprime/)):

- **XML request/response over HTTP** — TallyPrime runs a built-in HTTP server ("TallyPrime as a server"). Enable via **F1 (Help) → Settings → Advanced Configuration → HTTP Server**; default port **9000**; external applications POST an XML envelope to `http://<tally-host>:9000`. The envelope is `<ENVELOPE>` with `HEADER` and `BODY`; `TALLYREQUEST` takes `Import`, `Export`, or `Execute`. Prerequisites: TallyPrime running on the configured port with **at least one company loaded**; HTTP/1.1 POST; UTF-8 (default), UTF-16, or ASCII content ([XML integration](https://help.tallysolutions.com/xml-integration/), [prerequisites](https://help.tallysolutions.com/pre-requisites-for-integrations/)).
- **ODBC** — enable via **Alt+Z (Exchange) → Configure → Client/Server configuration → ODBC: Yes** with a configured port; the driver registers a DSN (e.g. `TallyODBC64_9000`) and exposes loaded-company data to ODBC consumers such as Excel and Power BI, including periodic refresh ([ODBC integrations](https://help.tallysolutions.com/odbc-integrations/), [ODBC-to-Excel guide](https://help.tallysolutions.com/extracting-master-data-to-microsoft-excel-using-odbc-tally/)). ⧗ The exact supported SQL syntax subset is not pinned from official sources — pending.
- **TDL** — Tally Definition Language, Tally's native definition/customization language; reports, collections, and export shapes are TDL-defined, and TDL-based exports are an officially named integration approach ([TDL reference](https://help.tallysolutions.com/article/TDL/Welcome.htm), [TDL release notes](https://help.tallysolutions.com/tallyprime-developer-release-notes/)).
- **JSON** — officially listed as an integration format ("modern REST API-style integrations") on the integration overview page; ⧗ detailed semantics, port, and version availability pending version-exact verification before any reliance.

#### 6.2 Authentication

**Researched restriction:** the official integration prerequisites document **no API-level authentication mechanism** for the XML/HTTP surface ([prerequisites](https://help.tallysolutions.com/pre-requisites-for-integrations/)) — the XML envelope reserves header room for "authentication" but no concrete credential scheme is specified in the pages reviewed. Practical consequence: **access control is network-layer** (segmentation, VPN/tunnel termination, IP restriction, host firewall), optionally combined with Tally's own user/security-level controls inside the product. This is recorded as a researched restriction, ⧗ pending version-exact re-verification per release — not a BareCount conclusion about any specific deployment.

Any network credential, VPN key, or agent token used to reach a TallyPrime instance is still provisioned via the **governed secret-ingress mechanism only** (`credential_ref` + receipt) — see §7.

#### 6.3 Throughput

No formal rate limits are documented — TallyPrime is **desktop-class** software serving integration requests from the same process that serves the interactive user. Practical throughput is bounded by the host machine and by not degrading the customer's working session; the (future) executor must be conservative by design. ⧗ No official throughput guidance located — pending.

#### 6.4 Delta strategy

⧗ **Unresolved.** No officially documented change-tracking timestamp on voucher records was located in the integration pages reviewed. Candidate strategies (design research, unverified): full periodic export per company; date-range export on voucher date; voucher-number high-water mark plus periodic reconciliation. The **TallyPrime Edit Log** variant records edits and is a research lead for change detection — ⧗ pending official verification of its exposure via the integration surfaces.

#### 6.5 Schema discovery

TDL-defined reports/collections and the ODBC catalog (DSN-exposed tables over the loaded company) are the discovery surfaces; the XML `Export` interface returns TDL-report-shaped data. There is no public community catalogue of Tally shapes equivalent to the SAP table catalogues — catalog seeding will have to derive from official TDL documentation plus instance-level discovery. See [catalog.md](catalog.md).

#### 6.6 Network plumbing

TallyPrime has **no vendor-hosted cloud API for a customer's books**; the customer's running instance is the endpoint, and it is typically on a private LAN, often not internet-exposed. Candidate paths:
- **Customer-side VPN** to reach the gateway/ODBC port.
- **BareCount agent** on or beside the Tally host with an **outbound** TLS tunnel (avoids inbound exposure) — not yet built (§8).
- **TDL export drop** — customer runs exports and delivers files via the agreed governed channel; no live connection at all.
- Direct internet exposure of the gateway port is a **researched anti-pattern** given §6.2 (no API-level auth documented) — flagged as a restriction, not a clearance statement.

#### 6.7 Known semantics (research notes, pre-contract)

- **Voucher types** are the transaction taxonomy (sales, purchase, journal, payment, receipt, contra, debit/credit note) and are customer-extensible — custom voucher types must be discovered per instance, never assumed.
- **Ledger grouping**: ledgers roll up under a group hierarchy (chart-of-accounts structure); grouping is customer-editable above the reserved primary groups. ⧗ exact reserved-group list pending version-exact verification.
- **Company data periods**: books are organized per company data file with financial-year periods; backup/restore and data-path management operate at company-folder granularity ([backup/restore](https://help.tallysolutions.com/backup-restore-company-data-tally/)). Period handling for exports must be pinned per instance.

### 6.B Tenant Connection Plane — customer technical prerequisites (general)

What **any** TallyPrime customer must set up before a connection can be tested (general requirements; the step-by-step execution runbook is §7, and concrete endpoints/accounts/results live only in the governed substrate):
- **Customer-side setup**: enable the integration surface on the serving instance — HTTP server (F1 → Settings → Advanced Configuration) and/or ODBC (Alt+Z → Configure) — with the port pinned; keep TallyPrime running with the in-scope company/companies loaded during admission windows.
- **Company selection**: identify exactly which company dataset(s) are in scope; only those are loaded/exposed.
- **Service account / OS-level access + minimum permissions**: where the agent or export path is used, an OS-level service context on the Tally host with the minimum file/network permissions; inside Tally, a dedicated Tally user at a restricted security level for the connection where the customer uses Tally's user controls.
- **Network path**: VPN, BareCount agent with outbound tunnel, or export-drop channel — chosen explicitly, because the instance is rarely internet-exposed and SHOULD NOT be exposed directly (§6.6). Any credential/token/VPN material goes through governed secret-ingress (`credential_ref` + receipt) — never person-to-person, never raw.
- **Connection-test + first-chain proof requirement**: a minimal read (e.g. list-of-companies / one-collection `Export` with the company loaded) must pass before reader activation; a first governed chain run (SO→CO→MS) is the acceptance bar.
- **Release verification**: confirm the exact TallyPrime release (e.g. 5.x/6.x/7.x, standard vs Edit Log) and any **TDL customizations** loaded on the instance — TDL customization can alter report/collection shapes, so shape universality is instance-scoped until verified (see [catalog.md](catalog.md)).

---

## 7. Onboarding Runbooks

Execution history of these runbooks is logged in [onboarding-log.md](onboarding-log.md). **No run has ever been executed** — these are designed procedures, not proven ones.

### 7.1 Customer-side — live connection path (XML/ODBC)

1. **Confirm licence + release.** TallyPrime edition (Silver/Gold), licence form (rental/perpetual, TSS state), exact release, standard vs Edit Log, and any loaded TDL customizations.
2. **Enable the surface.** HTTP server via F1 → Settings → Advanced Configuration (default port 9000), and/or ODBC via Alt+Z → Configure → Client/Server configuration.
3. **Pin scope.** Which company dataset(s); ensure they are loaded during admission windows.
4. **Choose network path**: customer-side VPN, or BareCount agent with outbound tunnel (when built). Direct internet exposure of the gateway port is not an accepted path (§6.6).
5. **Provision any credential via the approved secret-ingress mechanism (never person-to-person).** VPN material, agent tokens, or any Tally-user secret go through the governed secret store, which returns a `credential_ref` + receipt. Hand BareCount only the **host/port, the `credential_ref`, and the in-scope company list** — **never a raw secret.** No raw secret enters Git, a ticket, chat, email, the docket, or an audit artifact. This applies even though Tally's own surface may carry no credential — the *network path's* credentials are still governed.

### 7.2 Customer-side — TDL export-drop path

1. Receive the BareCount-published TDL export definition (⧗ not yet authored — see §8).
2. Load it on the serving instance; run the export for the agreed company/period scope.
3. Deliver the export files via the agreed governed channel (S3 dropbox, SFTP, signed URL) — no live connection required.

### 7.3 BareCount-side

Per-tenant connection profile in `tbc_{slug}_dev` (designed shape — no executor exists yet):

- `system_type_code: 'tally_prime'`
- `bridge_method: 'vpn' | 'agent' | 'export_drop'`
- `tally_host`, `tally_port` (live paths)
- `auth.credential_ref` — reference to a secret provisioned via the governed secret-ingress mechanism (yielding the `credential_ref` + receipt). Raw secrets never enter the DB, Git, tickets, chat, email, the docket, or any audit artifact — only the `credential_ref`.
- `companies[]` — in-scope company dataset identifiers.

Smoke test (live paths): one minimal XML `Export` request (e.g. list of companies / one collection) with the company loaded, before any reader activation.

---

## 8. Known Gaps

1. **No executor** for any Tally surface (XML-over-HTTP, ODBC, export-file) — nothing exists in the reader runtime.
2. **BareCount Tally agent** — host service architecture, outbound-tunnel design, credential issuance/rotation/revocation, packaging. Significant build; blocking for non-internet-exposed instances (the common case).
3. **Delta strategy** — no officially documented change-tracking field located; candidate strategies unverified (§6.4); Edit Log exposure unverified.
4. **TDL export definition** — the BareCount-published TDL export (runbook §7.2) is not authored.
5. **JSON surface verification** — officially listed, semantics unpinned (§6.1).
6. **Catalog seed source** — no community catalogue equivalent to SAP's; seeding approach (official TDL docs + instance discovery) undesigned (see [catalog.md](catalog.md)).
7. **Licence-terms verification** — integration-relevant licence terms (programmatic access, user-slot consumption on Silver) unverified (§4.A.1).
8. **No simulator profile** — bc-sdg has no Tally profile; even pre-governed shape exercise is impossible today.

---

## 9. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| Predecessor flat page (restructured into this docket) | `tally-prime.md` |
| TallyPrime Help — Integration overview | https://help.tallysolutions.com/integration-with-tallyprime/ |
| TallyPrime Help — XML integration | https://help.tallysolutions.com/xml-integration/ |
| TallyPrime Help — Integration prerequisites | https://help.tallysolutions.com/pre-requisites-for-integrations/ |
| TallyPrime Help — ODBC integrations | https://help.tallysolutions.com/odbc-integrations/ |
| TallyPrime Help — ODBC extraction to Excel | https://help.tallysolutions.com/extracting-master-data-to-microsoft-excel-using-odbc-tally/ |
| TallyPrime Help — Licensing (Silver/Gold, rental/perpetual, TSS) | https://help.tallysolutions.com/licensing-tallyprime/ |
| Tally Solutions — Buy TallyPrime (editions + commercial forms) | https://tallysolutions.com/buy-tally/ |
| TallyPrime Help — Release notes 7.1 (current at retrieval) | https://help.tallysolutions.com/release-notes-tallyprime-7-1/ |
| TallyPrime Help — Backup/restore company data | https://help.tallysolutions.com/backup-restore-company-data-tally/ |
| TDL Reference | https://help.tallysolutions.com/article/TDL/Welcome.htm |
| TallyPrime Developer (TDL) release notes | https://help.tallysolutions.com/tallyprime-developer-release-notes/ |

⧗ Retrieval date for all official sources above: 2026-07-13. Content digests pending per the 3rd capability gate (`official_research_refs[]` empty until digest capture exists).

## 10. Changelog

- **2026-07-13** — authored `tally-prime/` docket folder per **DEC-8570d4 (D526)**, restructuring the flat `tally-prime.md` source page. All official facts re-verified against help.tallysolutions.com / tallysolutions.com on this date (XML-over-HTTP gateway + port 9000, ODBC, TDL, licensing model, release line, prerequisites). Flat-page claims not officially confirmable (JSON API detail, ODBC SQL-syntax limits, delta fields, licence integration terms) carried as ⧗ pending rather than asserted. `proof_status: designed`; all governed coordinates null/empty.
- **2026-04-28** — (predecessor flat page) initial v3 page, superseding the legacy v2 archive reference.
