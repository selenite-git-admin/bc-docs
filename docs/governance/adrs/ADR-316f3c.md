---
uid: DEC-316f3c
title: "bc-seed — Standalone Catalog Sourcing Service (MongoDB, Port 4200)"
description: "bc-seed: standalone Node.js + MongoDB service for catalog sourcing. Port 4200. On-demand scraping, S3 import, field-level query API."
status: implemented
subdomain: catalog-sourcing
focus: bc-seed-service
date: 2026-04-03T07:03:15.008Z
project: bc-core
domain: sources
migrated_from: legacy v2 archive
---

# bc-seed — Standalone Catalog Sourcing Service (MongoDB, Port 4200)

## Context

Source catalog sourcing is a distinct workload from the core API — different data model (document vs relational), different access patterns (bulk import + on-demand scrape vs CRUD), different lifecycle (scraper data is raw, contracts are governed). MongoDB suits the document-shaped scraper data (nested fields, schema-less across sources). Standalone service keeps bc-core focused on governed contract operations. Docker MongoDB consistent with existing infrastructure (PostgreSQL, Redis already Docker).

## Decision

Create bc-seed as a standalone Node.js service with MongoDB backend for catalog sourcing. Separation of concerns from bc-core — bc-seed handles external data acquisition (scraping, caching, verification), bc-core handles governed contract instances. Port 4200, Docker MongoDB on 27017. On-demand scraping from sapdatasheet.org with HTML parsing. S3 archive import for bulk loading. Queryable API for field-level metadata.
