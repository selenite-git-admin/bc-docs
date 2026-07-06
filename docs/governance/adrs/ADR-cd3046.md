---
uid: DEC-cd3046
title: "V2 seed data format — CSV, not JSON"
description: "All seed data uses CSV instead of JSON. Better git diffs, auditable in Excel, and the Contract Generation Service derives contracts from CSV catalog data."
status: implemented
subdomain: seed-format
focus: csv-seed-format
date: 2026-03-20
project: bc-core
domain: database
refs:
  - type: decision
    label: "D101"
authority: authoritative
migrated_from: legacy v2 archive
---


# V2 seed data format — CSV, not JSON

## Context

User directive. CSV is more appropriate for tabular seed data than nested JSON. Easier for non-developers to review and maintain. Better git diffs. Aligns with the data governance culture of the platform.

## Decision

V2 seed engine uses CSV files as the data source format instead of JSON. All seed data (master data, source catalog, KPIs, standard fields, connectors, etc.) stored as CSV in a seed-v2/data/ directory. Benefits: auditable in Excel/Sheets, git-diffable, lighter for tabular data, universal format. The seed engine reads CSV → maps to Drizzle schema → batch inserts. JSON contracts are replaced by the Contract Generation Service (D101) which derives contracts from CSV catalog data.

## Options Considered

N/A

## Consequences

N/A
