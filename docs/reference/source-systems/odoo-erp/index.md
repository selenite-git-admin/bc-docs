---
uid: SRC-a8c3e7
slug: odoo-erp
title: "Odoo ERP"
description: "Odoo ERP admission research: candidate access paths (XML-RPC/JSON-RPC external API; JSON-2 API from v19) under Odoo's published licensing and plan gates; permissibility per customer/edition/version is a clearance decision against the governed authority objects, not asserted here."
type: source-systems
status: published
domain: enterprise-erp
subdomain: odoo
focus: governance
authority_role: projection        # D526 Amendment 1 — projection, not an authority
# --- evidence maturity (D385): what evidence exists, at what scope. NOT an audit verdict. Requires governed evidence. ---
proof_status: designed            # NO governed evidence object exists; no executor built; no instance (real or simulated) ever exercised (see evidence.md). Promote only when a governed proof-scope/evidence object is minted.
proof_scope_refs: []              # governed source-proof-scope UID — none yet
source_realization_refs: []       # governed source-realization-package UID — none yet
audit_decision_refs: []           # signed audit-decision UID — none (no realization audit run for Odoo ERP)
# --- exact governed reference coordinates — authority is the REFERENCED object, not these strings; ⧗ = capability/registration pending ---
source_registry_ref: null         # SRC registry UID + exact edition/version (⧗ pending source-registration)
reader_flavor_versions: []        # exact reader-flavor version UID + digest (⧗ pending; no flavor registered — see §2)
catalog_root: null                # source-catalog snapshot / mapping-root digest (⧗ pending)
contract_set_ref: null            # SC/AC/OC/CC version-set UID or contract-set digest (⧗ pending)
admission_contract_versions: []   # AC version UIDs realized against Odoo ERP — none authored (see contracts.md)
official_research_refs: []        # structured {source, version, retrieved_at, digest} per official citation (⧗ digest capture pending — 3rd capability gate)
last_verified_at: 2026-07-13
official_docs_url: https://www.odoo.com/documentation/18.0/developer/reference/external_api.html
system_type_code: odoo_erp        # label; authority = source_registry_ref
reader_flavors: []                # none registered; candidate labels discussed in §2
catalog_ref: catalog.md           # human link; authority = catalog_root + source catalog (source.*)
docket_files:
  - contracts.md
  - catalog.md
  - onboarding-log.md
  - evidence.md
governing_adrs:
  - DEC-6cb4f3   # D385 — Source Systems framework
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendments 1/2/3)
supersedes: docs/reference/source-systems/odoo-erp.md
---

# Odoo ERP

> **Docket cover — this is a PROJECTION, not an authority (DEC-8570d4 Amendment 1).**
> This `index.md` indexes and links governed objects; it does not create source registration, contract
> identity, catalog authority, evidence, or audit decisions. Registries own identities; the audit substrate
> owns evidence and PASS/REJECT/OPERATOR_REVIEW decisions (D525). `proof_status` below is **evidence maturity,
> not an audit verdict**. Reference narrative is here; concrete artifacts are referenced via the sibling files
> under [Docket Contents](#docket-contents).

Odoo is a modular open-core business-application suite. **This docket covers the Odoo ERP/accounting core**
(journal entries, invoices, payments, sales/purchase/stock documents exposed through the `account`, `sale`,
`purchase`, and `stock` model families). **Odoo CRM is out of scope** — it is a separate source system with its
own page ([odoo-crm.md](../odoo-crm.md)) and, when needed, its own docket.

Odoo ships in two editions: **Community** (open source, LGPLv3) and **Enterprise** (proprietary, subscription-
licensed), deployed as **Odoo Online** (vendor-managed SaaS), **Odoo.sh** (vendor PaaS), or **on-premise**
(self-hosted). All record data is reachable through the documented **external API** — XML-RPC/JSON-RPC through
v18 (deprecated from v19, removal scheduled for Odoo 22), and the **JSON-2 API** from v19. Which access path is
permissible for a given customer/edition/plan/version is a **clearance decision** made against the governed
authority objects (see §4.A), not asserted here.

Odoo releases **one major version per year** and supports the **three most recent** majors; schema and API
surface shift across majors, so every catalog and contract claim in this docket is version-scoped.

---

## Docket Contents

| File | Holds |
|---|---|
| **index.md** (this file) | Proof status, reader-flavor binding, reference (admits / legal / commercial / technical / gaps), onboarding runbooks, references, changelog |
| [contracts.md](contracts.md) | Contracts authored against Odoo ERP + the signed-columns / reconciliation OC design notes |
| [catalog.md](catalog.md) | Odoo model catalog footprint (`account.move`, `account.move.line`, …) |
| [onboarding-log.md](onboarding-log.md) | Dated onboarding-execution log |
| [evidence.md](evidence.md) | Proof entries — none of any kind yet; first-hand pending |

---

## 1. Proof Status (evidence maturity) & Audit Decisions

Two orthogonal vocabularies — never infer one from the other (D526 Amendment 1).

**Evidence maturity — `designed`** as of 2026-07-13. Evidence maturity requires *governed* evidence; none exists
for Odoo ERP, so no maturity above `designed` can be projected.

- **No ungoverned historical background exists either** (unlike SAP ECC's simulator run): no reader executor for
  any Odoo external API has been built, no Odoo instance — real or simulated — has ever been exercised, and no
  admission has been produced through the BareCount chain.
- Promotion to `shape_tested` requires a **minted governed proof-scope/evidence object** with
  `proof_scope_refs[]` / `source_realization_refs[]` populated; `first_hand_proven` requires a real-instance
  entity/scope-specific governed evidence entry — **never** a whole-system promotion of "Odoo ERP."
- Zero-claims rule (D385): until a real Odoo instance has produced metric snapshots end-to-end, **no external
  "we work with Odoo" claim may be made.**

**Audit decision — none.** No source-realization audit (D525) has been run for Odoo ERP; `audit_decision_refs[]`
is empty. PASS/REJECT/OPERATOR_REVIEW are decided and stored in the audit substrate against an exact realization
package; this docket would only ever render such a decision as a labelled "derived projection" with its governed
UID/digest, never as its own authority.

---

## 2. Reader Flavor Binding

**No reader flavor is registered for Odoo ERP** — `reader_flavors: []` and `reader_flavor_versions: []` are
empty because no executor exists and no flavor identity has been minted in the registry. Candidate flavor
*labels* from prior research (design intent only, not registered identities):

| Candidate label | Target | Executor | AC version |
|---|---|---|---|
| `odoo-erp-jsonrpc` | Odoo v14–v18 via `/jsonrpc` | — (not built) | — |
| `odoo-erp-json2` | Odoo v19+ via JSON-2 API | — (not built) | — |

A dedicated XML-RPC executor is not planned: it overlaps JSON-RPC capability and both sit on the same official
removal track (Odoo 22 — see §6.1). Registering either flavor is a registry act; this table cannot substitute
for it.

---

## 3. What BareCount Admits

### 3.1 Metadata

Chart of accounts (`account.account`, `account.group`); companies, currencies, exchange rates (`res.company`,
`res.currency`); fiscal positions, journals, tax configuration; partners (customers, vendors, contacts);
products, categories, warehouses, location hierarchy; model/field introspection via `fields_get()` and
`ir.model` / `ir.model.fields`. Stored as Source Catalog entries — see [catalog.md](catalog.md).

### 3.2 Business data

| Domain | Models |
|---|---|
| Journal Entries | `account.move` (`move_type = entry`), `account.move.line` |
| Customer Invoices | `account.move` (`move_type = out_invoice`, `out_refund`) |
| Vendor Bills | `account.move` (`move_type = in_invoice`, `in_refund`) |
| Payments | `account.payment` |
| Bank Statements | `account.bank.statement`, `account.bank.statement.line` |
| Sales Orders | `sale.order`, `sale.order.line` |
| Purchase Orders | `purchase.order`, `purchase.order.line` |
| Stock Moves | `stock.picking`, `stock.move` |
| Manufacturing | `mrp.production`, `mrp.bom`, `mrp.workorder` |

Unlike SAP's transparent tables, the "object" BareCount observes in Odoo is an **ORM model**: the external API
exposes model-level `search_read`, not SQL tables. Canonical resolution does the same job either way; only the
binding differs. Model availability depends on which modules the instance has installed (see §6.B).

---

> **Scope of §4–§6 (D526 Amendment 1).** Official, general research only — Odoo licensing/policy and the
> requirements any customer must satisfy. **No** tenant names, contracts, credentials, endpoints, approvals, or
> legal conclusions: those are governed-substrate objects referenced by pseudonymous UID/digest from
> onboarding-log.md / evidence.md. Retrieval date + digest for each official source are pinned in
> [References](#9-references) (⧗ digest TODO).

## 4. Legal & Licensing

### 4.A Platform Plane — Odoo legal & licensing (general)

> **Researched conditions — NOT clearance conclusions.** Nothing here is "sanctioned" or "banned" by BareCount
> assertion. Each condition holds only as supported by a **version-exact** official Odoo source (recorded in
> `official_research_refs[]` with retrieval date + exact version + content digest — ⧗ digest capture pending,
> 3rd capability gate) and, at runtime, by an exact-release **Platform Source Access Policy** plus the
> customer's **Tenant Source Authorization** (deferred governed authority objects, AuditHub/bc-core-owned).
> Which path is permissible for a given customer/edition/plan/version is a **clearance decision** made against
> those objects — not asserted here. This is assurance research, not legal advice.

**4.A.1 Edition licensing split (researched, official).** Per the official
[Odoo licenses page](https://www.odoo.com/documentation/18.0/legal/licenses.html):
- **Odoo Community** is licensed under **LGPLv3** (verified for Odoo 9–18; Odoo 8 was AGPLv3; v19 re-verification
  ⧗ pending). The accounting core — the `account` module ("Invoicing", carrying `account.move` /
  `account.move.line`) — is part of the Community codebase under `LGPL-3` per its
  [official manifest](https://github.com/odoo/odoo/blob/18.0/addons/account/__manifest__.py).
- **Odoo Enterprise** is governed by the **Odoo Enterprise Edition License v1.0**, which conditions use on a
  valid Odoo Enterprise Subscription for the correct number of users. The Enterprise addons (including the
  extended Accounting app) are proprietary; the exact Community-vs-Enterprise accounting-module split per
  version is ⧗ pending version-exact verification (the Enterprise repository is not publicly readable).
- Odoo Apps and website themes are typically under the **Odoo Proprietary License v1.0**.

**4.A.2 API access is plan-gated on Odoo Online (researched, official).** The official 18.0 external-API
reference states that external-API data access on Odoo Online is available only on *Custom* pricing plans — not
on the free/standard tiers. Whether a given customer's plan/edition permits external-API extraction is a
customer/Odoo determination verified at clearance time, not a BareCount conclusion. Self-hosted Community
carries no vendor plan gate for the API itself (LGPLv3 software); contractual constraints, if any, arise from
the customer's own agreements.

**4.A.3 Read vs write-back.** BareCount reads only today. The external API also exposes `create`/`write`/
`unlink`; if an Action Engine ever writes back into Odoo, the customer's subscription/plan terms and any
per-user licensing consequences must be resolved in the customer contract before activation — a customer/Odoo
determination.

**4.A.4 Maintenance/version horizon (researched, official).** Per Odoo's
[supported-versions policy](https://www.odoo.com/documentation/18.0/administration/supported_versions.html) and
[standard/extended support](https://www.odoo.com/documentation/19.0/administration/standard_extended_support.html):
one major (".0") release per year; the **three most recent majors** are supported; each major receives three
years of standard support (helpdesk, bug fixing, security updates), with paid extended support beyond. Bounds
per-version engineering investment and forces version-scoped catalog claims (§6.B).

### 4.B Tenant Connection Plane — customer authorization prerequisites (general, not tenant-specific)

What **any** Odoo customer must have/authorize before connection (stated generically — no named tenant, no
actual approval; those live in the governed substrate):
- **Vendor entitlement**: an edition/plan under which external-API access is available — on Odoo Online this
  means a *Custom* pricing plan (§4.A.2); on Odoo.sh / self-hosted, whatever the customer's subscription or
  LGPLv3 deployment provides.
- **Licensing posture**: a dedicated API user available for machine access (whether that user consumes a paid
  seat is a customer/Odoo determination); any write-back licensing consequences resolved *only if* write-back is
  ever in scope.
- **Scope authorization**: internal approval to expose the selected modules/models (accounting, sales, purchase,
  stock entities) to an external processor.
- **Contractual/security approvals** that must exist (MSA/DPA/Order-Form/security-review) — referenced
  generically; the actual executed documents are governed-substrate objects, never recorded here.
- **Residency / retention / subprocessor** considerations for the customer's data leaving Odoo (including
  Odoo Online / Odoo.sh hosting-region considerations for vendor-hosted instances).
- **Customer-side authorizer roles**: the Odoo administrator (API user creation, access rights, API-key
  issuance), the subscription owner (plan/edition confirmation, any write-back sign-off), and the data/security
  approver for scope.

---

## 5. Commercial

General access-model guidance (official/planning research; no tenant-specific commercial terms, no
readiness or pipeline claims).

| Model | Path | Cost (Odoo) | Notes |
|---|---|---|---|
| **Odoo Online (SaaS)** | Vendor-hosted; external API on *Custom* plan only | Plan pricing is a customer/Odoo determination | Managed; no custom server access |
| **Odoo.sh (PaaS)** | Vendor platform-hosted | Subscription is a customer/Odoo determination | Custom modules possible |
| **On-premise Enterprise** | Self-hosted, subscription-licensed | Subscription is a customer/Odoo determination | Full control |
| **On-premise Community** | Self-hosted, LGPLv3 | No vendor licence fee for the software itself | Accounting core (`account`) included; extended Enterprise apps absent |

Cost/permissibility per path is a **customer/Odoo determination** verified against the governed authority
objects (§4.A), not a BareCount conclusion. No volume/throughput cost figures are maintained here — Odoo
publishes no official API rate/volume pricing for these paths (⧗ re-verify at clearance time).

---

## 6. Technical

### 6.A Platform Plane — Odoo technical (general)

#### 6.1 Protocols

| Protocol | Endpoints | Status (official) |
|---|---|---|
| XML-RPC | `/xmlrpc/2/common`, `/xmlrpc/2/object` | Documented standard through v18. Deprecated; removal scheduled **Odoo 22 (fall 2028)** and **Online 21.1 (winter 2027)** |
| JSON-RPC | `/jsonrpc` | Same deprecation/removal track as XML-RPC (named in the official 19.0 deprecation notice) |
| **JSON-2 API** | model + method in URL path | New in **v19**; official successor to the RPC endpoints |
| REST | various | ⧗ unverified — prior research noted an experimental REST surface; not found in the official references during the 2026-07-13 verification pass |

The official deprecation notice also states that `@route(type='jsonrpc')` controllers (known as `type='json'`
until v18) are **not** covered by the RPC-endpoint removal.

#### 6.2 Authentication

- **XML-RPC / JSON-RPC (≤ v18 style):** two phases — `common.authenticate(db, login, password_or_apikey, {})`
  returns a `uid`; subsequent `object.execute_kw` calls pass `db`, `uid`, key/password plus `model`, `method`,
  `args`, `kwargs`.
- **API keys** (official since **v14.0**): generated per user under Preferences → Account Security → New API
  Key; used **in place of the password** with the same login. Odoo Online users are created without a local
  password and must set one (or use an API key) before RPC access works.
- **JSON-2 (v19+):** no `uid`/password at all — a bearer **API key** in the `Authorization` header; all
  arguments named (no positional calls).
- **OAuth:** no OAuth flow is documented for the external API in the official 18.0/19.0 references (Odoo's OAuth
  pages concern web-login identity providers, not RPC data access) — ⧗ re-verify per target version at
  clearance time.
- **mTLS / X.509:** not an Odoo-documented external-API method; not a first-class method on
  `ResolvedCredentials` either.

#### 6.3 ORM operations (the mental model)

The external API exposes the **ORM** — every record-level operation is `model.method(args)`:

- `search([domain])` — record IDs matching a domain expression; `search_count` for totals.
- `read(ids, fields)` / `search_read([domain], fields)` — record dicts.
- `fields_get()` — per-model field introspection; `ir.model` / `ir.model.fields` for instance-wide inspection.
- `create` / `write` / `unlink` — write operations (out of BareCount read-only scope; see §4.A.3).

For BareCount admission the primary operations are `search_read` and `fields_get`.

#### 6.4 Pagination and incrementality

- `search` / `search_read` accept `offset` and `limit` (official pagination mechanism).
- Delta candidate: domain filter on `write_date` — a standard ORM log-access field on ordinary models. ⧗ verify
  per model at AC design time: models defined with log-access disabled lack it, and the official per-model
  guarantee must be pinned against the exact target version.

#### 6.5 Schema discovery

`fields_get()` per model and `ir.model` / `ir.model.fields` introspection yield the effective per-instance
schema, including fields added by community/custom modules. Design-time reference for standard models is Odoo's
LGPL source code (`github.com/odoo/odoo`, e.g. `addons/account/models/`) — **provisional provenance until
version-exact verification** (see [catalog.md](catalog.md)).

#### 6.6 Throughput and network

- Odoo publishes no general external-API rate-limit specification in the researched references; effective limits
  are deployment-specific (Online plan limits ⧗ unknown; self-hosted limited by server sizing/reverse-proxy
  config). The (unbuilt) executor must assume conservative paging and configurable backoff.
- Network: HTTPS to the hosted URL (Online/Odoo.sh) or to the customer's self-hosted endpoint (direct,
  VPN, or IP-allowlisted).

#### 6.7 Known source semantics (design notes — ⧗ pending version-exact verification)

- **Journal items carry signed direction in separate columns**: `account.move.line` models debit and credit as
  separate columns rather than a SHKZG-style unsigned-amount + sign-indicator pattern. Contract-pattern
  consequences in [contracts.md](contracts.md).
- **Partial reconciliation**: open/cleared state of receivable/payable lines is derived through Odoo's
  reconciliation model (partial reconciliation records linking journal items), not a simple status flag —
  matters for AR/AP open-item metrics.
- **Document classes are an enumeration on one model**: invoices, refunds, bills, and plain entries are all
  `account.move` rows discriminated by `move_type` — discrimination belongs at the canonical boundary, never as
  MC literals.

These semantics are read from Odoo's LGPL source and prior research; each must be pinned against the exact
target version before any contract relies on it.

### 6.B Tenant Connection Plane — customer technical prerequisites (general)

What **any** Odoo customer must set up before a connection can be tested (general requirements; the step-by-step
execution runbook is §7, and concrete endpoints/accounts/results live only in the governed substrate):
- **Customer-side setup**: confirm hosting variant (Online / Odoo.sh / self-hosted), edition, plan (Online
  external-API access is plan-gated — §4.A.2), and the exact major version (drives protocol choice, §6.1).
- **Service account & minimum permissions**: a dedicated API user with **read-only** access rights scoped to
  exactly the models/modules in the agreed scope — no broader; an API key issued for that user (never a human
  user's personal credentials).
- **Endpoint / network allow-listing**: reachable HTTPS endpoint; IP-allowlisting or VPN for self-hosted
  deployments as the customer requires.
- **Modules that must be installed**: the model families in scope exist only if their modules are installed —
  at minimum the accounting core (`account` — "Invoicing"), plus `sale` / `purchase` / `stock` / `mrp` as
  scoped. Installed community/custom modules alter the effective schema and must be inventoried.
- **Connection-test & first-chain proof requirement**: authenticate + `res.company` `search_read` (limit 1) +
  `fields_get` on one in-scope model must pass before reader activation; a first governed chain run
  (SO→CO→MS) is the acceptance bar.
- **Version/customization verification**: pin the exact Odoo major/minor and the installed-module inventory —
  Odoo's schema shifts across yearly majors and per-instance modules add models/fields, so catalog universality
  is version- and instance-scoped (see [catalog.md](catalog.md)).

---

## 7. Onboarding Runbooks

Execution history of these runbooks is logged in [onboarding-log.md](onboarding-log.md). No execution has
occurred yet.

### 7.1 Customer-side

1. **Confirm hosting variant, edition, plan, and exact version** (Online / Odoo.sh / self-hosted; Community /
   Enterprise; on Online, whether the plan carries external-API access — §4.A.2). Version drives the protocol
   choice (§6.1).
2. **Create a dedicated API user** with read-only access rights limited to the modules/models in scope.
3. **Generate an API key** for that user (Preferences → Account Security → New API Key). On Odoo Online, note
   the official caveat that users are created without a local password.
4. **Choose the network path**: hosted URL over HTTPS, or VPN / IP-allowlist for self-hosted.
5. **Provision the credential via the approved secret-ingress mechanism (never person-to-person).** The customer
   submits the API key through the governed secret store, which returns a `credential_ref` + receipt. Hand
   BareCount only the **server URL, database name, API-user login, `credential_ref`, and the installed-module
   inventory** — **never the raw key.** No raw secret enters Git, a ticket, chat, email, the docket, or an
   audit artifact.

### 7.2 BareCount-side

Per-tenant connection profile in `tbc_{slug}_dev`:

- `system_type_code: 'odoo_erp'`
- `endpoint_url`
- `database_name`
- `odoo_version` — drives JSON-RPC vs JSON-2 protocol choice
- `auth.method: 'odoo_apikey'`
- `auth.credential_ref` — reference to a secret provisioned via the governed secret-ingress mechanism (yielding
  the `credential_ref` + receipt). Raw secrets never enter the DB, Git, tickets, chat, email, the docket, or any
  audit artifact — only the `credential_ref`.

Smoke test: authenticate; then `res.company.search_read([], ['name'], limit=1)`; then `fields_get` on one
in-scope model — all three must pass before activating the reader.

---

## 8. Known Gaps

1. **No executor exists** — neither `odoo-erp-jsonrpc` (v14–v18) nor `odoo-erp-json2` (v19+) is built; no reader
   flavor is registered.
2. **ORM domain-expression DSL** — the executor must serialize domain filters to the prefix-list shape Odoo
   expects.
3. **Schema introspection at AC design time** — `fields_get()` / `ir.model.fields` harvest per model, per
   instance.
4. **`write_date` delta strategy** — candidate default; per-model availability must be verified against the
   exact target version (§6.4).
5. **Plan/edition/protocol gate detection** — onboarding must surface (not silently pass) instances whose plan
   lacks external-API access or whose version sits on the RPC removal track (Odoo 22 / Online 21.1 — §6.1).
6. **Per-instance module discovery** — installed modules vary; the catalog is per-instance beyond the standard
   core.
7. **JSON-2 migration horizon** — customers approaching the RPC removal boundary need the JSON-2 path; the
   protocol-version gate must be enforced.
8. **Version-exact verification of source semantics** — §6.7 design notes (signed columns, partial
   reconciliation, `move_type`) are unpinned until verified against an exact release.
9. **Official-source digests** — `official_research_refs[]` capture (retrieval date + version + content digest)
   pending the shared capability gate (G3).

---

## 9. References

| Resource | Link |
|---|---|
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../../governance/adrs/ADR-6cb4f3.md) |
| ADR — Source-System Docket structure (D526) | [ADR-8570d4](../../../governance/adrs/ADR-8570d4.md) |
| Companion source page — Odoo CRM (separate system, future docket) | [odoo-crm.md](../odoo-crm.md) |
| Odoo External API (v18 — XML-RPC, API keys, plan gate) | https://www.odoo.com/documentation/18.0/developer/reference/external_api.html |
| Odoo External JSON-2 API (v19) | https://www.odoo.com/documentation/19.0/developer/reference/external_api.html |
| Odoo External RPC API — deprecation/removal notice (v19) | https://www.odoo.com/documentation/19.0/developer/reference/external_rpc_api.html |
| Odoo licenses (LGPLv3 / OEEL v1.0 / OPL v1.0) | https://www.odoo.com/documentation/18.0/legal/licenses.html |
| Odoo supported versions (yearly majors, 3 supported) | https://www.odoo.com/documentation/18.0/administration/supported_versions.html |
| Odoo standard & extended support | https://www.odoo.com/documentation/19.0/administration/standard_extended_support.html |
| Odoo install/hosting overview (Online / Odoo.sh / on-premise) | https://www.odoo.com/documentation/18.0/administration.html |
| Odoo Community source (official GitHub) | https://github.com/odoo/odoo |
| `account` module manifest ("Invoicing", LGPL-3) | https://github.com/odoo/odoo/blob/18.0/addons/account/__manifest__.py |
| Predecessor — flat v3 Odoo ERP page | `odoo-erp.md` |

## 10. Changelog

- **2026-07-13** — docket authored per **DEC-8570d4 (D526 + Amendments 1/2/3)**, restructuring the flat
  `odoo-erp.md` (removed by this docket migration; in git history at base `caeac53`). Official re-verification
  pass against odoo.com / official GitHub: **corrected** the flat page's "XML-RPC/JSON-RPC removal in v20 (fall
  2026)" to the official schedule — **removal in Odoo 22 (fall 2028) and Online 21.1 (winter 2027)**; pinned the
  edition-licensing split (Community LGPLv3 / Enterprise OEEL v1.0), the Odoo-Online *Custom*-plan API gate, the
  yearly-major + three-supported-versions cadence, hosting variants, and the `account` ("Invoicing") module's
  LGPL-3 Community placement. Legal content reframed as researched conditions pending clearance against the
  deferred governed authority objects (Amendment 3 pattern); credential handling rewritten to governed
  secret-ingress. `proof_status: designed` unchanged — no evidence of any kind exists.
- **2026-04-28** — predecessor flat page (initial v3 import); see `odoo-erp.md` changelog.
