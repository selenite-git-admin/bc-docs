---
uid: DEC-3fc279
title: "Source Landscape — per-source reference indexes, separate from Source Catalog"
description: "Source Landscape holds external reference indexes (SAP 245K tables, SFDC objects). Catalog minus Landscape equals onboarding gap"
status: superseded
superseded_by: DEC-05140c
subdomain: source-landscape
focus: landscape-as-separate-section
date: 2026-03-09
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Source Landscape — per-source reference indexes, separate from Source Catalog

## Context

SAP reference catalogs (245K tables) were buried inside an Onboarding provider detail page. Other sources will also need reference indexes. Source Landscape as a dedicated section under Registry gives each source's universe a proper home, clearly separated from the contracted Source Catalog. The naming pair (Catalog vs Landscape) makes the distinction intuitive.

## Decision

Source Landscape is a new Registry section containing per-source reference indexes:
- SAP: 245K ABAP dictionary tables, 7.6K CDS views, 8.8K field mappings
- SFDC: standard objects catalog (future)
- Tally: voucher types + masters catalog (future)
- Others as onboarded

**Source Catalog** = what BareCount has brought in (contracted, admitted, 6-tier hierarchy)
**Source Landscape** = what the external world has (reference indexes, planning tool)
**Gap** = Landscape − Catalog = onboarding work remaining

Source Landscape is NOT part of Source Catalog. Reference entries are not contracted or admitted. They exist for planning and discovery purposes.

UI pattern: landing page with cards per source → drill into tabbed explorer per source (e.g., SAP: Tables | CDS Views | Field Mappings). Scales to N sources without deep nesting.

The Readiness Dashboard in Onboarding uses this gap (Landscape − Catalog) to show per-provider readiness.

## Options Considered

N/A

## Consequences

N/A
