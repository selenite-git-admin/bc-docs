---
uid: DEC-9ab097
title: "Metric Catalog: flat table, not card catalog"
description: "bc-admin metric catalog uses a flat DataTable with filters, not card-based layout. Better for 700+ KPIs."
status: implemented
subdomain: metric-catalog
focus: flat-table-ui
date: 2026-03-12
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Metric Catalog: flat table, not card catalog

## Context

bc-admin is the platform team's authoring tool, not the customer-facing catalog (that's bc-portal per D051). Platform users need to scan, search, and drill into 700+ KPI contracts efficiently. A dense table with URL-synced filters, keyboard navigation, and cursor pagination serves this workflow better than a browse-oriented card layout. The card/catalog experience belongs in bc-portal where business users explore metrics by domain.

## Decision

Metric Catalog in bc-admin uses a flat sortable/filterable table — not a visual card-based catalog layout. Each row links directly to the KPI spec detail page. Domain/Module/Tier are columns with sort+filter, not visual groupings.

## Options Considered

N/A

## Consequences

N/A
