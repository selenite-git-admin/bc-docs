---
uid: DEC-b39a00
title: "bc-admin Platform Audit — Menu Restructure, Tenant Group, TopBar+LeftBar Layout"
description: "Comprehensive bc-admin restructure: TopBar+LeftBar layout, Tenant as top-level group, Operations surfaced, Pricing greenfield, 87 requirements scored"
status: decided
subdomain: bc-admin
focus: information-architecture
date: 2026-03-16
project: bc-admin
domain: platform
refs:
  - type: decision
    uid: DEC-005ea7
    label: "D153: Single production environment — simplifies tenant UX"
  - type: decision
    uid: DEC-0b3c08
    label: "D112/D053: Master/Tenant-Override — defines contract scoping in tenant group"
  - type: document
    path: "component-references/admin-portal-information-architecture.md"
    label: "Admin portal IA component reference"
  - type: document
    path: "architecture/admin-portal.md"
    label: "Admin portal architecture doc"
authority: authoritative
migrated_from: legacy v2 archive
---

# bc-admin Platform Audit — Menu Restructure

## Context

After e2e implementation of execution workflows, a comprehensive audit of bc-admin revealed 46 of 87 requirements missing or stub. The two biggest gaps: Tenant group (21 missing) and Pricing & Subscription (12 missing). Operations group existed but was hidden from nav. The topbar was wasted space (logo + logout only).

## Decision

### 1. TopBar + Contextual LeftBar Layout

Match bc-portal's section-first pattern:
- **TopBar** (dark, 60px): section dropdowns + global search + alert bell + user profile
- **LeftSidebar**: contextual — shows sub-items for active section only

### 2. Menu Structure

```
TopBar: [Dashboard] [Registry] [Operations] [Tenant] [Platform] [Pricing] [Tickets]

Registry:        Operations:        Tenant:              Platform Infrastructure:
├─ Source Catalog ├─ Admission Runs  ├─ Tenant Registry    ├─ Standard Fields
├─ Source Chain   ├─ Boundary Monitor├─ Tenant Config      ├─ Masters
├─ Contract Reg.  ├─ Connection Health├─ Tenant Health     ├─ Users & RBAC
├─ Canonical Map  ├─ Integrity Report├─ Contract Scoping  ├─ Libraries (SBOM)
├─ Metric Chain   ├─ Activity Log    └─ Tenant Infra      └─ Service Health
├─ Onboarding    └─ Rejection Summary
└─ Data Generators
```

### 3. Key Structural Changes

- **Tenant extracted** from Platform (semantically wrong to have Tenants under Platform Infrastructure)
- **Tenant data isolation enforced**: platform sees config/metadata/health, NOT tenant data
- **Evidence Explorer & Lineage Viewer are bc-portal features**, not bc-admin — tenant-scoped data
- **Pricing & Subscription** — new greenfield group (spec exists in bc-docs, nothing built)
- **Tickets & Incidents** — cross-cutting action inbox

### 4. Requirements Scorecard

87 total requirements across 11 groups. 37 done, 4 partial, 46 missing/stub.

## Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **TopBar + contextual LeftBar (chosen)** | Matches bc-portal, reduces scroll, visual consistency | Requires layout rewrite |
| Keep everything in sidebar | No layout change | Sidebar becomes unusably long with 40+ items |
| Mega-menu | All items visible at once | Complex to build, overwhelming |

## Consequences

1. **Visual consistency** across bc-admin and bc-portal
2. **Tenant group visible** — 21 missing requirements now have a home
3. **Operations surfaced** — was hidden, now first-class nav group
4. **Pricing is greenfield** — needs bc-core APIs before bc-admin UI
5. **bc-admin = Contracts view, bc-portal = Catalog view** (audience-based rendering)
