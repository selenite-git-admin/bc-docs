---
uid: DEC-f656a6
title: "Universal Protocol Readers — Connector Reclassification & Onboarding-Embedded Provisioning"
description: "Reclassify 21 source-specific connectors into ~8 universal protocol connectors (OData V4, REST, SDMX, etc.). Source identity moves to Connection level."
status: implemented
subdomain: reader-architecture
focus: protocol-readers
date: 2026-03-17
project: bc-admin
domain: database
refs:
  - type: decision
    label: "D084"
authority: authoritative
migrated_from: legacy v2 archive
---


# Universal Protocol Readers — Connector Reclassification & Onboarding-Embedded Provisioning

## Context

21 source-specific connectors growing linearly is unsustainable. Protocol-level connectors give O(1) code growth — adding a new source = JSON flavorConfig, not a new executor. Onboarding-embedded provisioning reduces customer workflow from 4 separate steps to 1 wizard. bc-portal already has 90% of the wizard built (AddConnectionPage + ConnectionSetupPage). Renumbered from D084 to D086 to resolve conflict with Dynamic Tenant Provisioning (DEC-f82a8a).

Replaces DEC-71c50d (was incorrectly numbered D084, which conflicts with Dynamic Tenant Provisioning DEC-f82a8a).

## Connector Reclassification

Reclassify connectors from source-specific (21 connectors: SAP-S4-OData, Salesforce-REST, etc.) to universal protocol connectors (~8 protocols). Source system identity moves to the Connection level.

### Protocol Registry (2 tabs)

**Universal** (open standard, N source systems per protocol):
- OData V4 (SAP S/4HANA, Oracle, Dynamics 365, SuccessFactors)
- OData V2 (SAP ECC, legacy SAP)
- REST+OAuth2 (Zoho, HubSpot, Xero, QuickBooks, generic REST)
- SDMX (ECB, IMF, OECD, Eurostat, World Bank)

**Proprietary** (vendor-locked, 1 ecosystem per protocol):
- Salesforce REST+SOQL (Salesforce CRM, CPQ, Service Cloud)
- Tally XML (Tally Prime)
- ServiceNow Table API (ServiceNow ITSM)
- Jira/Atlassian REST (Jira, Confluence)

### Data Model Shift
- connector.protocolName, connector.transportType, connector.executorClass (new)
- connector.vendor, connector.sourceSystem (removed — move to connection)
- connection.vendor, connection.sourceSystem (authoritative)
- connection.protocolId → FK to protocol connector

## Onboarding-Embedded Provisioning

Customer selects system → protocol auto-selected → credentials entered → tested → done. No separate connector/connection/reader workflows. Readers auto-provisioned based on subscription package.

### Package-Based Auto-Provisioning
After connection creation, readers auto-provisioned by tier:
- Finance Essentials, Finance Complete, Full ERP, CRM, HR, Custom

## Implementation Plan: PLN-ce1bc4

Phase 1: bc-core foundation (TSK-cebf3a)
Phase 2: bc-admin protocol registry UI (TSK-88c5f4)
Phase 3: bc-portal onboarding wizard (TSK-998b46)

## Consequences

N/A
