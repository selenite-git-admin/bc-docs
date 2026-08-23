---
uid: DEC-e93a19
title: "SAP Table Reference — separate catalog table"
description: "Store 50K+ SAP table names in a lightweight sap_table_reference table, separate from the 6-tier source hierarchy which requires moduleId FK."
status: implemented
subdomain: sap-catalog
focus: sap-table-reference-index
date: 2026-03-06
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# SAP Table Reference — separate catalog table

## Context

source_object.moduleId is NOT NULL with FK constraint — can't dump 50K+ tables without proper module assignment. A separate lightweight table provides queryability ("does BareCount know table X?"), coverage tracking, and classification without polluting the operational 6-tier hierarchy. JSON catalog file (leanx-catalog.json) remains the static reference committed to git; DB table enables API queries and future admin UI for coverage planning.

## Decision

All discovered SAP table names (~50K-100K from leanx.eu) stored in registry.sap_table_reference as a lightweight reference index. Separate from the 6-tier source hierarchy (source_object requires moduleId FK, impractical for 50K+ unclassified tables). Coverage lifecycle: discovered → fields_available → registered. Tier classification: core (transactional/master data) | extended (config/supporting) | reference (everything else). Auto-classification heuristics for ~80 known core tables; bulk remains as 'reference/unknown'. Seed runs as part of npm run seed:registry.

## Options Considered

N/A

## Consequences

N/A
