---
uid: DEC-d2cdb9
title: "SAP data admission stance under SAP API Policy v.4/2026"
description: "BareCount admits SAP customer data only through SAP-sanctioned Published APIs / CDS Published views / BDC Connect — no ODP RFCs, no undocumented OData, no scraping of customer systems."
status: decided
date: 2026-04-28T13:08:47.018Z
project: barecount-devhub
domain: sources
subdomain: sap
focus: governance
---

# SAP data admission stance under SAP API Policy v.4/2026

## Context

SAP API Policy v.4/2026 (published April 2026) restricts SAP system access to Published APIs only and prohibits large-scale extraction or replication except through SAP-endorsed paths. SAP Note 3255746 prohibits ODP RFC use by third parties. BDC Connect formalizes the only sanctioned route for sharing SAP Data Products with third-party systems, with contractual restrictions on onward distribution.

Many ETL incumbents (Theobald, Fivetran-ODP, classic Databricks-ODP) became non-compliant for new deployments overnight. BareCount never relied on those rails, so we lose nothing — but we have not yet built a Published-API reader flavor for real SAP tenants either (the bc-sdg port-6100 ECC simulator imitates RFC/table shapes for testing, not production access).

Our reader-flavor + admission-contract model (DEC-b10dad / D043) maps cleanly onto a "one reader, multiple sanctioned flavors" pattern: Published OData (S/4HANA Cloud), CDS-view Published APIs (S/4HANA on-prem), BDC Connect (BDC tenants). Each flavor carries its own admission contract version; the canonical layer remains access-path agnostic; only mapping bindings differ between flavors (OData entity property vs. table/field).

Recording this stance now (proposed) gives us a referenceable position when enterprise prospects ask "how do you handle SAP under the new policy?" — and forces a clean separation between what the ECC simulator is for (internal testing) and what real-tenant onboarding requires (a Published-API flavor we still need to build).

## Context

SAP published **API Policy v.4/2026** in April 2026, which:
- Restricts SAP system access to **Published APIs** only (those listed on SAP Business Accelerator Hub or in official product documentation).
- Explicitly prohibits use of internal, private, or non-published APIs.
- Prohibits "scraping, harvesting, or systematic and/or large-scale data extraction or replication, except through SAP-endorsed architectures, data services, or service-specific pathways expressly identified for such purposes."

Concurrently, **SAP Note 3255746** (originally Feb 2024, reinforced 2026) prohibits use of ODP RFC modules by third-party applications. **BDC Connect** is the formal sanctioned channel for sharing SAP Data Products with third-party systems, with contractual restrictions on onward distribution outside the SAP BDC ecosystem.

Industry impact: classic ETL paths used by Theobald, Fivetran-ODP, and Databricks-ODP integrations are now non-compliant for new deployments. SAP's own answer is Joule + AI Agent Hub; the third-party agentic ecosystem has been narrowed to Published-API consumers and sanctioned BDC partners.

## Decision

BareCount admits SAP customer data **only** through SAP-sanctioned interfaces. Three sanctioned flavors of the SAP reader, each implemented under the D043 multi-flavor model with its own admission contract version:

1. **`sap-s4-cloud-odata`** — S/4HANA Cloud Published OData APIs (Business Accelerator Hub catalogue).
2. **`sap-s4-onprem-cds`** — CDS view-based Published APIs for S/4HANA on-prem.
3. **`sap-bdc-connect`** — BDC Connect for tenants on SAP Business Data Cloud (subject to a separate "Third-Party Connector" partnership decision when the first BDC tenant arrives).

The following are **explicitly out of scope** for production tenants:
- ODP RFC modules (banned by SAP Note 3255746).
- Undocumented or internal OData services.
- Direct table reads via custom RFCs.
- Any form of scraping against a customer's SAP system.

The **bc-sdg port-6100 SAP ECC simulator** remains in scope for **internal testing only**. It does not represent any production reader path. Tests against it prove the reader/admission/canonical chain mechanically; they do not prove fitness for live SAP tenant onboarding.

The **BareCount SAP Table Scraper** (S3 artefact `s3://barecount-dev-artifacts/sap-table-scraper/`) is confirmed to scrape only **public SAP documentation** (`help.sap.com` table catalogue metadata), never customer SAP systems. This is out of scope of the policy. A README note will record this.

The **canonical layer remains access-path agnostic**. Only **mapping bindings** (CC field-mapping rows, OC field maps) differ between flavors — e.g. `sap-s4-cloud-odata` flavor binds canonical fields to OData entity property names, `sap-s4-onprem-cds` binds to CDS view field names, an ECC-flavour binds to BSID/BUDAT-style table fields. The metric contract layer never sees the difference.

## Consequences

- Production SAP-tenant onboarding requires building **at least the `sap-s4-cloud-odata` flavor** before the first real S/4HANA tenant. The simulator-shaped reader does **not** count. A parked task captures the cataloguing precondition: enumerate which SAP Published OData entities cover the metric chain we exercise today.
- Some metrics currently computed via simulator paths may have **no clean Published-API equivalent**. Those gaps must be discovered before tenant onboarding, not during it.
- Becoming a **BDC Connect "Third-Party Connector"** is a separate, larger decision (likely involves SAP partnership, certification, and contractual review of onward-distribution restrictions for our multi-tenant model). Park until first BDC tenant.
- Positions BareCount as a **compliant semantic / observation layer** on top of SAP data, not a replication tool. Strengthens enterprise narrative: contracted access, audit trail, narrow surface — all of which the new policy implicitly endorses.
- Keeps SAP as **one source among many** in the BareCount cross-system semantic-layer story. Avoids being framed (internally or by prospects) as "yet another SAP analytics tool."

## Alternatives considered

- **Status quo (continue as if simulator-shaped path is fine for production)** — rejected; non-compliant for any real SAP tenant.
- **Build a proprietary RFC connector** — rejected; explicitly prohibited by SAP Note 3255746 and the new policy.
- **Single SAP reader with internal branching** — rejected; violates the D043 reader-flavor model (each sanctioned access path is a different observation surface and deserves a distinct admission contract version).
- **Defer the stance until first SAP tenant arrives** — rejected; we get asked the question by enterprise prospects now, and the architectural decisions ripple into reader/AC/CC modelling that we are doing today.

## Procedure to flip to `decided`

1. Founder/architect (anant) reads this ADR and either accepts as-is or annotates revisions.
2. On acceptance, status flips `proposed → decided` via `devhub_decision_update`.
3. Parked task (`sap-published-api-flavor` cataloguing) is referenced from the ADR; first concrete implementation work flips status `decided → implemented` once the first Published-API flavor ships, gated by a `closes: DEC-xxxxxx` commit token per ADR Hygiene Policy (DEC-623f8f / D370).
