---
uid: DEC-d5c352
title: "SAP Data Acquisition Strategy — Phase 1: sapdatasheet.org"
description: "Use sapdatasheet.org as primary source for SAP table metadata. Airbyte, PyRFC, Cloudification Repo all rejected for Phase 1 due to coverage gaps."
status: implemented
subdomain: data-acquisition
focus: sap-source-strategy
date: 2026-03-08
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# SAP Data Acquisition Strategy — Phase 1: sapdatasheet.org

## Context

Research confirmed: (1) Airbyte has no SAP RFC/OData connector — dead end, (2) All RFC libraries (PyRFC, node-rfc) are archived and require proprietary SAP NW RFC SDK + live SAP system, (3) Cloudification Repo only tracks released API objects — 57/9,810 match (0.6%), (4) Leanx/SE80 do NOT have applicationComponent — only DDIC metadata, (5) sapdatasheet.org has complete TADIR→TDEVC→COMPONENT chain as public website with structured HTML. Full strategy documented in bc-docs/component-references/sap-data-acquisition-strategy.md.

## Decision

Use sapdatasheet.org as primary source for SAP table applicationComponent metadata. Airbyte, Meltano, PyRFC, node-rfc all rejected for Phase 1. Live SAP system access deferred to Phase 3. Cloudification Repo yields only 0.6% coverage — insufficient as primary source.

## Options Considered

N/A

## Consequences

N/A
