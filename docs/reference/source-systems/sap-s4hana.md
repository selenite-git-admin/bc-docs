---
uid: SRC-7a3e1f
slug: sap-s4hana
title: "SAP S/4HANA"
description: "BareCount source-admission posture. Vendor facts must be verified during source onboarding."
type: source-systems
status: published
domain: enterprise-erp
subdomain: sap
focus: governance
proof_status: shape_tested
last_verified_at: 2026-04-28
official_docs_url: https://api.sap.com/products/SAPS4HANACloud/apis/all
reader_flavors:
  - sap-s4-cloud-odata
  - sap-s4-onprem-cds
admission_contract_versions: []
governing_adrs:
  - DEC-d2cdb9   # D384 — SAP API admission stance
  - DEC-6cb4f3   # D385 — Source Systems framework
supersedes: legacy-v2/reference/sources/sap-s4hana.md
---

# SAP S/4HANA

This page records BareCount's source-admission posture for SAP S/4HANA. It is not a static vendor fact sheet.

Product-market descriptions, customer counts, pricing, release cadence, API limits, and licensing terms must be re-verified from official vendor documentation during source onboarding. Keep tenant-specific verification in onboarding evidence, not in this page.

---

## 1. Proof Status

**Proof status:** `shape_tested`.

What this means concretely:

- The OData V4 executor (`bc-core/src/boundary/reader-runtime/executors/sap-odata-v4.executor.ts`) has been validated against the BareCount internal simulator at `bc-sdg` port 6100 (which mimics SAP OData V2/V4 protocol shapes). Pagination, CSRF token fetch, date filter, multi-entity fetch, and authorization-header injection all work in that environment.
- **Zero validation against a real SAP S/4HANA tenant.** No Communication Arrangement has been provisioned, no real OAuth flow exercised, no real Published-API entity ever consumed.
- Until a real S/4HANA instance has produced metric snapshots through the BareCount chain end-to-end, **no external "we work with SAP S/4HANA" claim may be made.** This is the standing zero-claims rule and applies even to investor / sales / website copy.

`proof_status` will be promoted to `first_hand_proven` only after §9 Verified Coverage gains an entry with a real (anonymised) customer instance and date.

---

## 2. Reader Flavor Binding

| Flavor | Target | Executor | AC version |
|---|---|---|---|
| `sap-s4-cloud-odata` | S/4HANA Cloud (Public/Private Edition) | `SapOdataV4Executor` | — (not yet built) |
| `sap-s4-onprem-cds` | S/4HANA on-prem with CDS Published Views | `SapOdataV4Executor` (CDS Published APIs are V4 OData) | — (not yet built) |

The executor file is shared across both flavors; flavor differences are config (auth method, base URL, optional Cloud Connector hop, scenario whitelist). Each flavor will get its own admission-contract version per metric domain (AR, AP, GL, etc.) when first scoped against a real tenant.

The ECC simulator path uses `SapOdataV2Executor` and is documented separately on the SAP ECC reference page; it is **not** a sanctioned production path under D384.

---

## 3. What BareCount Admits

### 3.1 Metadata (Source Catalog seed)

CDS view definitions, field metadata, key/foreign-key relationships, value-help associations. Used to seed Source Catalog Tier 5 (Source Tables) and Tier 6 (Fields). Acquired without admitting customer business data, via:

- **Public catalogue** — pre-seeded from SAP Cloudification Repository (`github.com/SAP/abap-atc-cr-cv-s4hc`, released CDS view catalog), CDS Finder Excel field-level mappings, and `se80.co.uk` definitions. None of this touches a customer system.
- **Customer-specific extension** — when the customer has Z-tables or custom CDS views, a BareCount-published ABAP transport (read-only DDIC reader) can be installed and run by the customer's Basis team. Indirect Static Read.

### 3.2 Business data (UniBAT Reader admission)

Posted business records — journal entries, sales orders, deliveries, billing documents, purchase orders, goods movements, master data — admitted via the reader flavors above. Per-record observation is contracted through the admission contract bound to the flavor; canonical resolution and metric snapshots follow the standard chain.

The exact entity coverage planned for the first `sap-s4-cloud-odata` build is being catalogued by **TSK-0c031b** (parked, pulled when first SAP customer signs).

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

### 6.1 Protocol

OData V4 for both Cloud and on-prem CDS Published Views. JSON payloads. `@odata.nextLink` for pagination, `$filter` for incremental date-range queries, `$select` for narrow projection, `$count` for totals.

The V4 executor (`SapOdataV4Executor`) handles:

1. CSRF token fetch (`x-csrf-token: Fetch`) and echo on subsequent requests.
2. Paginated query loop with configurable batch size.
3. Date-field filtering for incremental loads.
4. Multi-entity fetch in a single executor invocation.
5. Authorization header injection from `ResolvedCredentials`.
6. SAP-specific headers (`sap-client`, `sap-language`, `Accept: application/json`).

### 6.2 Authentication

Supported in the readiness baseline via `CredentialResolverService`:

- **Basic Auth** (technical user + password over TLS) — common for on-prem.
- **Bearer token** (OAuth 2.0) — for Cloud after the OAuth client_credentials grant has resolved a token.

**Gap**: end-to-end OAuth 2.0 client_credentials flow has been shape-tested but never run against a real SAP OAuth token endpoint. **Gap**: mTLS / X.509 client cert is not yet a first-class method on `ResolvedCredentials`. Both gaps are listed in §10.

### 6.3 Throughput and throttling

Communication Arrangement quotas are real and per-tenant. The executor does not yet implement adaptive backoff — large historical loads against a real tenant could trip throttling. Listed in §10.

### 6.4 Delta / incremental loads

Readiness baseline: simple `$filter` by date field (for example, a `PostingDate` lower bound). The executor supports `startPeriod` / `endPeriod`.

Future entity-by-entity decisions will use whichever is cleanest:
- OData V4 `$delta` (where SAP exposes it for the entity).
- `LastChangeDateTime` filter on entities that carry it.
- Change pointers (where applicable).

### 6.5 Schema discovery

OData `$metadata` document at the entity root yields entity types, properties, key fields. We do not yet auto-ingest `$metadata` to bootstrap admission contract creation; this is a future ergonomics improvement (the source catalogue in the readiness baseline is seeded from public sources — see §3.1).

### 6.6 Network plumbing

- **Cloud**: HTTPS direct to `https://<tenant>-api.s4hana.cloud.sap`. Customer may IP-allowlist BareCount's egress IPs (must be deterministic — NAT Gateway with reserved EIP). Gap: deterministic egress posture not yet documented.
- **On-prem**: either SAP Cloud Connector tunnel (preferred — no inbound holes in customer firewall) or direct VPN. Gap: Cloud Connector integration not yet built or documented.

---

## 7. Customer-Side Onboarding

Steps the customer's SAP admin (Basis team) must complete **before** BareCount can connect.

### 7.1 S/4HANA Cloud (Public / Private Edition)

1. **Identify scenarios.** Each Published API is bound to a Communication Scenario with an ID like `SAP_COM_xxxx` (e.g. `SAP_COM_0760` for Journal Entry, `SAP_COM_0091` for Outbound Delivery). The exact list needed for BareCount's metric chain is being catalogued by **TSK-0c031b** and will be filled in here once that task completes.
2. **Create a Communication System** in the SAP Fiori "Communication Systems" app, representing BareCount. Set the host (BareCount's egress endpoint), enable Inbound (or Outbound, depending on direction).
3. **Create a Communication User** in the "Maintain Communication Users" app. Choose either:
   - OAuth 2.0 client credentials → SAP generates client_id and client_secret.
   - X.509 client certificate (mTLS) → upload certificate, SAP binds it to the user.
4. **Create a Communication Arrangement** for each scenario from step 1, binding the user to the scenario. This whitelists which OData endpoints we may call.
5. **Hand BareCount**: tenant base URL, client_id + client_secret (or cert), and the list of activated scenarios.

### 7.2 S/4HANA on-prem

1. **Activate OData services** in `/n/IWFND/MAINT_SERVICE` for the CDS Published API entities BareCount needs (e.g. `API_JOURNALENTRYITEMBASIC_SRV`).
2. **Choose network path**:
   - SAP Cloud Connector — install Connector in customer's network, configure access control to expose the activated services.
   - Direct VPN / IP allowlist — customer admits BareCount's egress IPs to the SAP gateway.
3. **Create a technical user** with read-only authorisations on the activated services. Store password securely — pass to BareCount via the agreed credential channel.
4. **Optionally provision an X.509 client certificate** for mTLS instead of password.
5. **Hand BareCount**: endpoint URL (or Cloud Connector identifier), credentials/cert.

---

## 8. BareCount-Side Onboarding

### 8.1 Connection profile

Per-tenant connection profile stored in `tbc_{slug}_dev`. Fields:

- `system_type_code: 'sap_s4hana_cloud'` or `'sap_s4hana_onprem'`
- `endpoint_url`
- `auth.method: 'oauth2_client_credentials' | 'basic' | 'mtls'`
- `auth.credential_ref` — reference to credential in external store; secrets never live in the DB
- `sap_client` (on-prem; defaults to `100`)
- `sap_language` (defaults to `'EN'`)
- `scenarios[]` — for Cloud, the activated Communication Arrangement scenario IDs

### 8.2 Credential storage

Reference-based via `CredentialResolverService` (`bc-core/src/registry/credential-resolver.service.ts`). The resolver returns a `ResolvedCredentials` with pre-built `Authorization` headers ready for the executor. Secrets never appear in the database.

### 8.3 Smoke test

Before activating the reader, run a no-side-effect smoke call:

1. Hit `/$metadata` on the first scenario's service root → confirms reachability + auth.
2. Hit one entity with `$top=1` → confirms response shape.
3. If both pass, mark the connection profile with the verification timestamp, then enable the reader.

---

## 9. Verified Coverage

**No SAP S/4HANA entity has been verified first-hand against a real customer instance in the reference baseline.**

This section will list, per entity, the verified date and the anonymised customer reference once first-hand verification occurs. Until then it remains empty by design — and `proof_status` cannot be `first_hand_proven`.

---

## 10. Known Gaps

Things to close before / during the first real S/4HANA tenant onboarding:

1. **OAuth 2.0 client_credentials** end-to-end against a real SAP OAuth token endpoint (only shape-tested in the readiness baseline).
2. **mTLS / X.509 client certificate** auth path — not yet a first-class method on `ResolvedCredentials`.
3. **SAP Cloud Connector** integration / documentation for on-prem tenants.
4. **Deterministic egress IPs** from AWS `ap-south-1` (NAT Gateway with reserved EIP) so customer firewalls can allowlist.
5. **Adaptive throttle / backoff** for Communication Arrangement rate limits during bulk loads.
6. **Delta strategies beyond date-range** — per-entity decision (`$delta` vs `LastChangeDateTime` vs change pointers).
7. **`$metadata` auto-ingestion** to bootstrap admission contract creation (ergonomics).
8. **Concrete `SAP_COM_xxxx` scenario list** for the metric chain — captured by TSK-0c031b.

Each gap is a candidate task when an SAP-tenant onboarding becomes real.

---

## 11. References

| Resource | Link |
|---|---|
| ADR — SAP API admission stance (D384) | [ADR-d2cdb9](../../governance/adrs/ADR-d2cdb9.md) |
| ADR — Source Systems framework (D385) | [ADR-6cb4f3](../../governance/adrs/ADR-6cb4f3.md) |
| Parked task — Published OData entity catalogue | TSK-0c031b |
| Companion appendix — SAP licensing & catalogue rules | [sap-licensing-reference.md](sap-licensing-reference.md) |
| SAP API Policy v.4/2026 | https://www.sap.com/docs/download/2026/04/dce9aee4-497f-0010-bca6-c68f7e60039b.pdf |
| SAP Note 3255746 (ODP RFC ban) | https://me.sap.com/notes/3255746 |
| SAP Business Accelerator Hub | https://api.sap.com/products/SAPS4HANACloud/apis/all |
| SAP Cloudification Repository (GitHub) | https://github.com/SAP/abap-atc-cr-cv-s4hc |
| SAP Help Portal — S/4HANA Cloud | https://help.sap.com/docs/SAP_S4HANA_CLOUD |
| SAP Digital Access licensing | https://www.sap.com/about/agreements/policies/digital-access.html |
| Predecessor — legacy v2 archive SAP S/4HANA reference | legacy-v2/reference/sources/sap-s4hana.md |

## 12. Changelog

Initial source-system page imported from v3. Import provenance is tracked by repository history, frontmatter `supersedes`, and the v4 documentation-control database.
