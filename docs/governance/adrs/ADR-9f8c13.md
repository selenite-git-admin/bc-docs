---
uid: DEC-9f8c13
title: "Contract Registry — dedicated menu group with per-type surfaces"
description: "Contracts get their own nav group in bc-admin with separate pages per contract family (SC, AC, OC, CC, MC, IC)."
status: implemented
subdomain: contract-chain
focus: contract-registry-ui
date: 2026-03-14
project: bc-core
domain: database
refs:
  - type: decision
    label: "D069"
authority: authoritative
migrated_from: legacy v2 archive
---


# Contract Registry — dedicated menu group with per-type surfaces

## Context

1. Contracts are first-class entities — they deserve their own home, not scattered across reader/connector/metric detail pages
2. All stakeholders (platform engineers, domain owners, governance reviewers) need a single place to find, create, and manage contracts
3. Current sidebar has contracts hidden behind deep links and drill-downs — discovery is poor
4. D069 retired extraction contracts and introduced Observation Schema — the UI must reflect this
5. Per-type pages enable category-specific filters, create flows, and documentation
6. Reader/Connector detail pages become cleaner — they reference contracts instead of duplicating content
7. Aligns with ISO 27001 A.14.2.1 — clear ownership and lifecycle management surfaces for all contract types

## Decision

Restructure contracts UI into a dedicated **Contract Registry** sidebar menu group. Each contract type gets its own list page + shared detail page. All stakeholders manage contract lifecycle from this single home. Other surfaces (Reader Detail, Connector Detail, Metric pages) **reference** contracts via links — they never inline contract content.

**Sidebar structure:**
```
Contract Registry (menu group)
  ├── Source Contracts        /registry/contracts/source
  ├── Admission Contracts     /registry/contracts/admission
  ├── Observation Contracts   /registry/contracts/observation
  ├── Canonical Contracts     /registry/contracts/canonical
  ├── Metric Contracts        /registry/contracts/metric
  └── Action Contracts        /registry/contracts/action
```

**Changes from current state:**
1. Kill the hub landing page (`ContractsPage.tsx` with 5 chain cards) — replace with direct per-type pages
2. Retire `extraction` contract category (D069) — replaced by Observation Schema on flavor
3. Rename `intervention` → `action` (vocabulary alignment)
4. Add `observation` as new contract category
5. Remove `ai` contracts for now (no AI chain implemented)
6. Move sidebar entries from scattered locations into one **Contract Registry** group
7. Reader Detail: remove Contract Chain + Unlinked Contracts cards; Observation Contracts card references contracts via compact triplet links
8. Shared `ContractDetailPage` stays — all types use it with category-specific rendering
9. Contract Scoping page (`/registry/contracts/scoping`) stays as a cross-cutting view

**Contract types (6, post-D069):**
- `source` — declares expected schema of projected fields per source table/object
- `admission` — validates observations at admission boundary
- `observation` — maps source fields → standard fields per reader flavor (NEW, replaces extraction)
- `canonical` — defines CO evaluation rules (source-agnostic)
- `metric` — computation contract (formula + temporal gate + thresholds)
- `action` — defines AO outcome triggers (renamed from intervention)

**Each per-type page provides:**
- Filtered list view with search, governance state filter, domain filter
- Reuses `ContractListByChain` component with category filter
- Create contract dialog (pre-filled category)
- Row click → shared ContractDetailPage

## Options Considered

N/A

## Consequences

N/A
