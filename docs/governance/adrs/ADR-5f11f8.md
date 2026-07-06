---
uid: DEC-5f11f8
title: "Canonical evaluation has internal layering — primary COs (from SOs) and derived COs (from other COs)"
description: "Two CO tiers: primary COs resolved from Source Objects, derived COs computed from other COs. Executed in dependency order."
status: implemented
subdomain: canonical-evaluation
focus: tier-layering
date: 2026-03-01
project: bc-core
domain: database
refs:
  - type: decision
    label: "D022"
authority: authoritative
migrated_from: legacy v2 archive
---


# Canonical evaluation has internal layering — primary COs (from SOs) and derived COs (from other COs)

## Context

Real enterprise data includes both direct observations (invoices from BKPF+BSEG) and computed aggregates (AP aging buckets, vendor liability snapshots). Both are canonical business entities — they represent "what is," not "how are we doing" (which would be metrics). AP Aging is not a quality metric; it's a business state snapshot. Forcing these into the metric chain would be semantically wrong. Internal layering within canonical evaluation (Tier 1: from SOs, Tier 2: from COs) preserves the three-chain model while supporting the full range of canonical business objects found in the bc-portal dummy data (7 AP entities, 2 of which are fully derived).

## Decision

Canonical evaluation resolves COs in two tiers, executed in dependency order:

**Tier 1 — Primary COs:** Resolved from N Source Objects (via admission contracts). These are direct observations of external business state. Examples: Vendor Invoice (BKPF + BSEG + RSEG), GL Account (SKA1 + SKAT), Exchange Rate (ECB SDMX).

**Tier 2 — Derived COs:** Resolved from other COs, not from SOs. These represent computed or aggregated business state. Examples: AP Aging Bucket (from Vendor Invoice + Vendor Payment COs), Vendor Liability Snapshot (aggregation of open AP COs).

The evaluation engine must resolve in topological order — all Tier 1 COs before any Tier 2 CO that depends on them. A derived CO's source_dependencies reference canonical contracts, not admission contracts.

This does NOT break the three-chain model (D022). It is internal to canonical evaluation within the Source Chain. No same-layer back-references — the dependency graph is a DAG (directed acyclic). Derived COs are still COs — they represent canonical business state, not measurements (which would be metrics).

**Impact on canonical meta-schema:** The `source_dependencies[]` array in a canonical contract body can reference:
- Admission contracts (for primary COs — Tier 1)
- Canonical contracts (for derived COs — Tier 2)

The `contract_category` field in each dependency entry distinguishes: `"admission"` = primary CO, `"canonical"` = derived CO.

## Options Considered

N/A

## Consequences

N/A
