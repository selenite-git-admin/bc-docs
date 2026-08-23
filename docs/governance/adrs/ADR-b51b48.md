---
uid: DEC-b51b48
title: "SAP Landscape Scanner — connector-level discovery + compatibility report"
description: "SAP landscape scanner discovers installed modules and tables per system, produces compatibility report for reader coverage."
status: implemented
subdomain: sap-catalog
focus: sap-landscape-scanner
date: 2026-03-02
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# SAP Landscape Scanner — connector-level discovery + compatibility report

## Context

Pre-sales tool: connect to prospect's sandbox, scan in 5 minutes, show exact coverage. Eliminates guesswork during scoping. Also validates authorization setup during onboarding — surfaces missing auth objects before go-live.

## Decision

Each SAP connector in bc-core includes a landscape scanner that: (1) Discovers available CDS views/entity sets via $metadata. (2) Probes authorization — tests which entities the connection user can read ($top=1 per entity, check 200/403/404). (3) Maps coverage — compares discovered+authorized entities against BareCount's CDS coverage matrix (shared with bc-sdg). (4) Reports — generates compatibility report showing: landscape version, active modules, coverage percentage, fully covered process chains, authorization gaps, activatable KPIs, recommended actions. Scanner lives in bc-core connector module. UI in bc-admin ("Scan Landscape" button on connection detail). The CDS Coverage Matrix is the shared source of truth between scanner (inbound: what can we read?) and bc-sdg (outbound: what should we generate?). No PDF export. No auto-profile generation from scanner output.

## Options Considered

N/A

## Consequences

N/A
