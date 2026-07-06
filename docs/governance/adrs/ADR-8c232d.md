---
uid: DEC-8c232d
title: "Metric Catalog: 2-page flat navigation, drop domain/module drill-down"
description: "bc-admin Metric Catalog uses flat list + KPI detail only. Domain/module drill-down is a customer UX pattern for bc-portal, not admin."
status: implemented
subdomain: navigation-ia
focus: metric-catalog-flatten
date: 2026-03-12
project: bc-admin
domain: contracts
refs:
  - type: decision
    label: "D051"
authority: authoritative
migrated_from: legacy v2 archive
---


# Metric Catalog: 2-page flat navigation, drop domain/module drill-down

## Context

Platform team already knows the domain model — they need search/filter/click-to-edit, not guided browsing. The intermediate pages (domain detail, module detail) added 2 extra clicks without adding value. Domain and module filters on the list page already provide the same grouping capability. Simplifies route structure from 4 levels to 2, removes ~19K of intermediate page code, and reduces registered screens from 4 to 2.

## Decision

Metric Catalog in bc-admin uses 2 pages only: flat list (/catalog/metrics) → KPI detail (/catalog/metrics/:contractId). Remove MetricDomainDetailPage and MetricModuleDetailPage. Domain/module drill-down browsing is a customer-facing UX pattern that belongs in bc-portal (D051), not in the platform team's authoring tool.

## Options Considered

N/A

## Consequences

N/A
