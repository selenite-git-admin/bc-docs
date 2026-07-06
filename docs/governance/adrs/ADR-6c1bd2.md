---
uid: DEC-6c1bd2
title: "system_type_code on source_system, not source_provider"
description: "System type (ERP, CRM, HCM etc.) belongs on source_system not provider. A provider like SAP makes systems of many types."
status: implemented
subdomain: source-systems
focus: type-on-system
date: 2026-03-21
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# system_type_code on source_system, not source_provider

## Context

Provider-level type conflated "what software does this vendor make" with business function. SAP filtered as ERP showed 8 systems including Ariba (procurement) and SuccessFactors (HCM). Moving type to system level lets the Source Catalog page correctly show only ERP systems when ERP is selected — S/4HANA, ECC, Business One from SAP; Dynamics 365 from Microsoft; etc.

## Decision

system_type_code (ERP, CRM, ITSM, MES, HCM, etc.) belongs on source.source_system, not source.source_provider. A provider (SAP SE) makes systems across many types — S/4HANA is ERP, Ariba is Procurement, SuccessFactors is HCM. The provider has no single type. Backed by master.master_system_type reference table (19 slugs). source_provider.function_code dropped entirely.

## Options Considered

N/A

## Consequences

N/A
