---
uid: DEC-cb906b
title: "master_system_type reference table for software system categories"
description: "New master.master_system_type table (17 types: erp, crm, itsm, etc.) as controlled vocabulary for source_system.system_type. Dynamic filter chips per category."
status: implemented
subdomain: master-data
focus: system-type-master
date: 2026-03-21
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# master_system_type reference table for software system categories

## Context

Follows same pattern as master_function, master_subfunction, master_industry — controlled vocabulary backed by reference table. Dynamic chips ensure Third Party shows only its types (Advertising, Billing, Payments) while Enterprise shows its types (ERP, CRM, ITSM), avoiding empty filter results.

## Decision

New master.master_system_type table (slug PK, display_name, sort_order) holds controlled vocabulary for software system categories. 17 active types: erp, crm, accounting, procurement, mes, supply-chain, hcm, itsm, analytics, project-management, payments, billing, advertising, currency, economic-data, tax, regulatory. source_system.system_type FK references this table. Source Catalog type filter chips are dynamic — derived from actual data per category, not hardcoded.

## Options Considered

N/A

## Consequences

N/A
