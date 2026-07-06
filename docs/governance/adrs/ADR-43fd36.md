---
uid: DEC-43fd36
title: "bc-admin = Contracts view, bc-portal = Catalog view — audience-based rendering"
description: "Same contract data rendered per audience: bc-admin shows contract authoring, bc-portal shows business-friendly catalog browsing"
status: implemented
subdomain: cross-frontend
focus: audience-split
date: 2026-03-09
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-admin = Contracts view, bc-portal = Catalog view — audience-based rendering

## Context

Business Catalog = friendly lens over canonical contracts. Metric Catalog = friendly lens over metric contracts. Having both Catalogs and a Contracts section in bc-admin shows the same data in two places. Clean split: admin authors contracts, customer browses catalogs.

## Decision

The same underlying contract data is rendered differently per audience:

**bc-admin (platform team):** Contracts view — author JSON bodies, manage versions, set governance state, bind contracts to readers/tenants. Organized by contract chain position (Admission, Canonical, Metric, AI).

**bc-portal (customer):** Catalog view — read-only, business-friendly browsing organized by domain. Business Catalog (canonical contracts rendered as domain → objects → fields). Metric Catalog (metric contracts rendered as domain → KPIs → formulas).

Business Catalog and Metric Catalog do NOT exist in bc-admin. They are bc-portal concepts. In bc-admin, admins work directly with canonical contracts and metric contracts.

Source Catalog appears in both: full 6-tier editable hierarchy in bc-admin, read-only connected sources view in bc-portal.

## Options Considered

N/A

## Consequences

N/A
