---
uid: DEC-0f61dd
title: "Source system catalog uses business function names, not tech abbreviations"
description: "Replace ERP/CRM/HRMS tabs with business function names (Finance & Operations, Sales & Customers, etc.). Drop Data Storages section."
status: implemented
subdomain: naming
focus: business-function-naming
date: 2026-02-27
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Source system catalog uses business function names, not tech abbreviations

## Context

Users think in business functions, not system categories. A CFO looks for "Finance", not "ERP". Aligns with BareCount's domain-aware philosophy — UinBAT Readers are domain-aware, and the catalog should reflect business domains. Tech abbreviations create unnecessary jargon barrier for business users.

## Decision

Replace tech abbreviation tabs (ERP, CRM, HRMS, ITSM, MES) with business function names: Finance & Operations, Sales & Customers, Marketing & Advertising, People & Workforce, IT & Service Management, Manufacturing, External Sources. Tab order reflects business priority with Marketing at #3. Drop Data Storages section entirely (Snowflake, S3, databases are delivery mechanisms not source systems).

## Options Considered

N/A

## Consequences

N/A
