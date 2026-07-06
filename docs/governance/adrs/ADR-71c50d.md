---
uid: DEC-71c50d
title: "Universal Protocol Readers — Connector Reclassification & Onboarding-Embedded Provisioning"
description: "Reclassify 21 source-specific connectors to ~8 universal protocol connectors. Auto-provision readers from package tier. Superseded."
status: superseded
date: 2026-03-17
project: bc-admin
domain: database
authority: retired
migrated_from: legacy v2 archive
---


# Universal Protocol Readers — Connector Reclassification & Onboarding-Embedded Provisioning

## Context

SUPERSEDED by DEC-f656a6 (D086). This decision was incorrectly numbered D084, which conflicts with Dynamic Tenant Provisioning (DEC-f82a8a). Content moved to D086 unchanged.

## Decision

1. **Reclassify connectors from source-specific to universal protocols.** Current 21 source×method connectors collapse to ~8 universal protocol connectors (odata-v4, odata-v2, rest-json, sdmx, salesforce-rest, servicenow-table, tally-xml, jira-rest). Source system identity moves to the Connection level, not the Connector level.

2. **Connector is not a customer-facing concept.** Customers never see "connectors." Protocols are embedded in the system onboarding wizard as "connection methods" (already implemented in ConnectionSetupPage.tsx). The customer picks a system → picks a protocol → enters credentials → tests → done.

3. **Package-based reader auto-provisioning.** After connection is created, the platform auto-provisions reader flavors based on the customer's package tier (Finance Essentials, Finance Complete, Full ERP, CRM, HR, Custom). No manual reader-to-connection binding.

4. **Protocol Readers replace per-source executors.** One Protocol Reader implementation per protocol handles all source systems in that protocol cluster. Per-source variation is handled by flavorConfig (JSON), not separate executor classes. ~2,200 lines of protocol code + JSON configs replaces ~33,600 lines of duplicated executors.

5. **Admin sees universal connectors as platform infrastructure.** bc-admin Protocol Registry shows the 8 universal connectors with capabilities, supported auth methods, and all connections using them. bc-admin also manages package definitions (which readers per tier).

## Options Considered

N/A

## Consequences

N/A
