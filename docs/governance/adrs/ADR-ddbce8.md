---
uid: DEC-ddbce8
title: "Unified Business Domain Taxonomy"
description: "Master taxonomy tables for business_domain (19 domains) and business_subdomain as single source of truth for cross-platform capability classification"
status: superseded
superseded_by: DEC-7bbdba
subdomain: taxonomy
focus: unified-business-vocabulary
date: 2026-03-14
project: bc-core
domain: platform
refs:
  - type: decision
    uid: DEC-5017fe
    label: "D139: Standard Field Registry — uses domain taxonomy for field classification"
  - type: decision
    uid: DEC-36d78f
    label: "D138: Reader Observation Schema — readers classified by business domain"
  - type: document
    path: "architecture/source-catalog.md"
    label: "Source Catalog architecture"
authority: authoritative
migrated_from: legacy v2 archive
---

# Unified Business Domain Taxonomy

## Context

Three independent domain vocabularies existed across the platform:
- 19 contract domains
- 9 reader domains (with different names — "customer" vs "customer_experience")
- 15 provider domains

Users filtering "Finance" on Readers expected to find related Source Objects and Contracts, but each entity used its own vocabulary. The same business capability had different names in different contexts.

## Decision

Create master taxonomy tables `business_domain` and `business_subdomain` as the **single source of truth** for business capability classification.

### Two-Axis Taxonomy

1. **Business Domain / Subdomain** (master tables) — 19 domains: finance, sales, supply_chain, manufacturing, human_resources, customer_experience, services, marketing, operations, it_operations, asset_management, governance, risk_compliance, quality, product_portfolio, project_management, rnd_engineering, boardroom, executive. Referenced by: readers, contracts, source objects, connectors.

2. **Provider Category** (on `source_provider`) — software market category (erp, crm, accounting, public_data). Different axis, stays on provider table. Renamed from `domain` to `provider_category`.

### Reader Classification

Reader columns: `business_domain` + `business_subdomain` (validated against master) + `entity_type` (journal_entry, purchase_order, opportunity).

### API-Driven

All UI pages fetch domain/subdomain options from `GET /business-domains` and `GET /business-subdomains` endpoints. No frontend hardcoding.

### Domain Remapping

Existing reader domains: customer → customer_experience, service → services, activity → operations, identity → governance, reference_data → finance.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Unified master taxonomy (chosen)** | One vocabulary everywhere, API-driven | Migration effort for existing data |
| Per-entity vocabularies | No migration | Permanent inconsistency, confusing UX |
| Provider-based taxonomy | Fewer entities | Providers are a different axis than business capabilities |

## Consequences

1. **Module stays source-catalog-internal** — not exposed as cross-cutting filter
2. **Master tables seeded** with 19 domains and subdomains
3. **All domain/subdomain text columns validate** against master values
4. **API-driven UI** — no hardcoded domain lists in frontend code
