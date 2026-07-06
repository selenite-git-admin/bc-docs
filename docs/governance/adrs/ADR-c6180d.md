---
uid: DEC-c6180d
title: "Business Chain — nav group + onboarding workbench + bulk monitor"
description: "Business Chain nav group with seed browser, onboarding wizard, bulk monitor, BF/BO registries. Move BFs/BOs out of Platform/Canonical. Line-level BOs auto-inherit header temporal."
status: implemented
date: 2026-04-08T04:53:03.425Z
project: bc-admin
domain: contracts
migrated_from: legacy v2 archive
---

# Business Chain — nav group + onboarding workbench + bulk monitor

## Context

1. BFs and BOs are NOT canonical contracts — they are the business vocabulary layer between source discovery and canonical binding. Housing them under Platform (standard-fields) or Canonical was a category error. 2. The BF/BO onboarding SOP (Track A) requires a guided workflow UI, not just CRUD catalog pages. 3. Bulk domain onboarding (Finance: 461 BFs, 34 BOs) needs real-time progress monitoring — a new UX pattern for bc-admin. 4. Nav reads left-to-right: Source Chain (discover sources) → Business Chain (define vocabulary from standards) → Canonical Chain (map sources to vocabulary) → Metric Chain (define metrics on vocabulary). 5. Line-level BOs must be self-contained for Gate 2 compliance — temporal fields propagated from header during onboarding.

## Decision

### 1. New Nav Group: Business Chain

Insert between Source Chain and Canonical Chain:

```
Source Catalog → Source Chain → Business Chain → Canonical Chain → Metric Chain
```

**Business Chain** (5 pages):

| # | Page | Route | Purpose |
|---|------|-------|---------|
| 1 | Seed Browser | `/business-chain/seeds` | Browse OAGIS Nouns by domain. Preview components + fields. "Onboard" per Noun or "Onboard Domain" bulk action. |
| 2 | Onboard Wizard | `/business-chain/onboard/:noun` | SOP Track A materialized as UI. 6-step wizard: Review Fields → Create BFs → Certify → Compose BO → Verify → Approve. |
| 3 | Bulk Monitor | `/business-chain/bulk` | Process dashboard for domain-level bulk runs. Real-time progress per step. Per-item status (green/amber/red/pending). Gate failure drill-down. Retry + "Approve all passing" actions. |
| 4 | Business Fields | `/business-chain/fields` | BF registry — list/filter/detail. Moved from `/platform/standard-fields`. Status badges (draft/certified). |
| 5 | Business Objects | `/business-chain/objects` | BO registry — list/filter/detail with composition tree. Gate results inline. Verification history. |

### 2. Nav Moves

| Page | From | To |
|------|------|----|
| Standard Fields (SCR-4266f7) | `platform/standard-fields` → `/platform/standard-fields` | `business-chain/fields` → `/business-chain/fields` |
| Canonical Objects (SCR-edeb5d) �� BOs only | `canonical/business-catalog` → `/catalog/business` | `business-chain/objects` → `/business-chain/objects` |

### 3. Temporal Propagation (Option A)

Line-level BOs auto-inherit the header's temporal field during onboarding:

- When a multi-component Noun produces header + line BOs
- If the line BO has no temporal field in the OAGIS seed
- Auto-create a BO-scoped temporal BF: `{line_bo_name}_document_date_time`
- Copy definition from header's temporal field
- Add to line BO composition with `semantic_role: 'temporal'`

This ensures every BO is self-contained and passes Gate 2 without relaxing gate rules.

### 4. Bulk Monitor — New UX Pattern

The Bulk Monitor is a **process monitoring** surface, not a CRUD page. It tracks:

```
Domain Onboarding Run
├── Step 1: Create BFs ─── [====████████░░] 392/461
├── Step 2: Certify BFs ── [====██████░░░░] 310/461
├── Step 3: Create BOs ─── [waiting]
├── Step 4: Verify BOs ─── [waiting]
├── Step 5: Approve BOs ── [waiting]
└── Step 6: Relations ──── [waiting]
```

Per-item table below the progress bars:
- BF/BO name, status (pending/running/passed/failed), gate results
- Click to expand gate failure details
- Checkbox select + "Retry Failed" or "Approve All Passing" bulk actions

### 5. Onboard Wizard Steps

| Step | Action | API Call | Gate |
|------|--------|----------|------|
| 1. Review Fields | Browse Noun's scalar fields, toggle on/off | `GET /api/seed-catalog/oagis/nouns/:slug` | — |
| 2. Create BFs | Create BO-scoped BFs as draft | `POST /api/business-fields/bulk` | D268 one-then-many |
| 3. Certify BFs | Auto-certify standards-sourced (OQ-005) | `POST /api/business-fields/bulk-certify` | CR-QG-001 (9 gates) |
| 4. Compose BO | Create BO with field composition | `POST /api/business-objects` | Name uniqueness, FK validation |
| 5. Verify BO | AI verification (CR-BO-007) | `POST /api/business-objects/:id/verify` | 6-check AI verdict |
| 6. Approve BO | Run CR-QG-002 gate | `POST /api/business-objects/:id/approve` | 7 gates |

Each step shows results before proceeding. Gate failures show inline with explanations. User can fix and retry without restarting the wizard.

## Consequences

- SCR-4266f7 (Standard Fields) route changes from `/platform/standard-fields` to `/business-chain/fields`
- SCR-edeb5d (Canonical Objects) becomes BO-only and moves to `/business-chain/objects`
- 4 new screens to build (Seed Browser, Onboard Wizard, Bulk Monitor, BO Registry)
- Existing BF list page can be reused with route change
- Bulk Monitor introduces process monitoring pattern reusable for future chain operations
