---
uid: DEC-6fc629
title: "Build All Custom UinBAT Readers — No Airbyte Runtime Dependency"
description: "All connectors built as native UinBAT Readers. ~8 protocol readers cover ~50+ providers via flavors. Airbyte code is reference only."
status: implemented
subdomain: readers
focus: connector-strategy
date: 2026-03-17
project: bc-core
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Build All Custom UinBAT Readers — No Airbyte Runtime Dependency

## Context

1. Airbyte connectors are ETL pipes — they extract/flatten/dump. BareCount needs UinBAT Readers that admit under contracts, emit SOs with Evidence/Lineage, and respect the observation model. Using Airbyte would require a translation wrapper on top, creating dual maintenance burden.

2. Protocol clustering reduces build effort from ~50 individual connectors to ~8 protocol readers with configuration-driven flavors. This is proven by the Exchange Rate Reader pattern (DEC-b10dad).

3. The 33+ providers without Airbyte coverage (Procurement, SCM, MES, India Stack) are exactly BareCount's target domains. Building native readers for these creates defensible value that no competitor with Airbyte dependency can match.

4. Even for the 27 providers WITH Airbyte connectors, the native reader approach is preferred because: (a) no external dependency risk, (b) no paradigm mismatch, (c) Airbyte source code serves as free reference documentation.

5. Connector research documented at bc-docs/architecture/connector-availability-research.md confirms API accessibility for all target providers — the protocols are well-documented and the build risk is low.

## Decision

BareCount will build all connectors as native UinBAT Readers. No Airbyte connectors will be used as runtime dependencies. Airbyte open-source connector code may be referenced for API documentation, pagination patterns, and auth quirks, but the runtime path is always a BareCount-native reader that emits Source Objects with Evidence/Lineage at the Admission Boundary.

Key principles:
1. **Protocol-cluster approach**: ~8 protocol readers cover ~50+ providers via flavor configurations (same pattern as Exchange Rate Reader DEC-b10dad)
   - OData v4 Reader → SAP S/4, Dynamics 365, Dynamics BC (~8 providers)
   - REST/OAuth 2.0 Reader → Coupa, Workday, ServiceNow, Zuora, etc. (~15 providers)
   - OPC UA Reader → All MES providers (Siemens, AVEVA, Rockwell) (~3 providers)
   - SDMX Reader → All public statistical agencies (ECB, Eurostat, IMF, World Bank) (~6+ providers)
   - SOAP/XML Reader → Tally, legacy systems
   - ODBC Reader → Busy, legacy on-prem
   - GraphQL Reader → Shopify, modern APIs
   - SFTP/Flat-file Reader → Bank statements, legacy exports

2. **Each flavor has its own Admission Contract** — source-specific field mappings, auth config, rate limits
3. **Airbyte's existence = signal of API maturity** — where Airbyte connectors exist, the API is well-documented and the reader will be straightforward to build
4. **The 33+ providers with no Airbyte coverage are the competitive moat** — Procurement (Coupa, GEP, Jaggaer), Supply Chain (Kinaxis, Blue Yonder), India Stack (Tally, GSTN, Busy, Darwinbox)

Build phases:
- Phase 1: Protocol Readers (OData, REST/OAuth, OPC UA, SDMX) — covers ~32 providers
- Phase 2: India Stack (Tally XML, GSTN, Busy ODBC, Darwinbox) — market differentiator
- Phase 3: Niche/Closed ecosystems (Infor ION, Epicor REST, SAP RFC legacy)

## Options Considered

N/A

## Consequences

N/A
