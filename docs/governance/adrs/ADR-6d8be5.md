---
uid: DEC-6d8be5
title: "D225: Bottom-Up Canonical Chain Generation from Metric Formula Variables"
description: "Generate Business Fields, Business Objects, Canonical Contracts, and Metric Contracts bottom-up from 2,210 metric formula variables — the metrics define the vocabulary"
status: superseded
subdomain: contract-chain
focus: bottom-up-generation
superseded_by: DEC-f1dae0
date: 2026-03-29
project: bc-core
domain: canonical
refs:
  - type: decision
    uid: DEC-616e02
    label: "D112: Business Object Model"
  - type: decision
    uid: DEC-5017fe
    label: "D069: Standard Field Registry"
  - type: decision
    uid: DEC-29c324
    label: "D021: Metric contracts reference N canonical objects"
  - type: decision
    uid: DEC-3d6e11
    label: "D203: DAG Support — Derived CO + Secondary Metric"
  - type: decision
    uid: DEC-0e3c64
    label: "Observation Contract is Canonical-Chain (bridge)"
  - type: decision
    uid: DEC-1b32a9
    label: "Canonical contracts are source-agnostic"
  - type: document
    path: "playbooks/kpi-enrichment-playbook.md"
    label: "KPI Enrichment Playbook"
  - type: document
    path: "architecture/database/schema-map.md"
    label: "Database Schema Map"
authority: authoritative
migrated_from: legacy v2 archive
---

# D225: Bottom-Up Canonical Chain Generation from Metric Formula Variables

## Context

Finance KPI enrichment is 100% complete: 687 metric definitions across 19 subfunctions, each with a formula and normalized variables. The `metric_formula_variable` table contains 2,210 rows:

| Role | Count | Unique field_names |
|------|-------|--------------------|
| input | 959 | 959 |
| output | 653 | 653 |
| constant | 10 | 10 |
| **Total** | **2,210** | **1,604** |

The canonical chain below metric contracts is empty: 0 Business Fields, 0 Business Objects, 0 Canonical Contracts, 0 Metric Bindings, 1 Metric Contract (DSO prototype).

Most-shared input fields (cross-metric reuse): total_invoices_issued (15 metrics), net_sales (14), net_income (14), total_revenue (13), total_debt (13), cash_flow_from_operations (12).

Composition distribution: 686 primary, 1 derived.

## Decision

Build bottom-up from metric formula variables. The 1,604 unique field_names already in the database are the source of truth for what the canonical layer must contain.

### The Complete Flow

```
SOURCE CHAIN                    CANONICAL CHAIN                 METRIC CHAIN
(source-specific)               (source-agnostic)               (source-agnostic)

Source Contract ──┐             Business Field (vocabulary)      Metric Contract
(schema)          │                    │                         ├── metric_binding → N CCs
                  │             Business Object (domain entity)  ├── upstream_metric_bindings (DAG)
Admission Contract│                    │                         └── contract_json: formula +
(validation)      │             Canonical Contract (1 per BO)        temporal_gate + thresholds
                  │                    │
    ┌─────────────┘             Canonical Mapping
    │                           (source-specific wiring)
    ▼
Observation Contract ◄── BRIDGE: maps source fields → business fields
(field_map: source_field_name → business_field_id)
```

### Key Architectural Points

**1. Observation Contract is the bridge between chains**

Source chain contracts are Source + Admission only. The Observation Contract sits on the boundary connecting both chains:
- Source side: references source_contract_id, knows source field names (e.g., SAP BUKRS)
- Canonical side: maps to business_field_id (e.g., company_code)
- It is the ONLY entity that touches both chains

**2. Variable role determines field classification**

- Input variables (I1, I2...) → Business Object fields (consumed from COs)
- Output variables (O1) → Business Fields too (for DAG: output of metric A becomes input of metric B)
- Formula constants (percentage_multiplier, unity, z_weights) → formula variables only, NOT business fields
- Domain constants (days_in_year, rate_multiplier) → Business Fields when reused across metrics as reference data

**3. Metric DAG: output of one metric can be input of another**

- `composition_code`: primary (686), derived (1+), composite (both CO + metric inputs)
- Downstream metrics reference upstream metrics via `upstream_metric_bindings` in contract_json
- Output fields live in "metric output" Business Objects that downstream metrics bind to
- `input_type` enum in contract_json: primary | secondary | composite

**4. Business Object granularity: domain entity level (~40-50 for Finance)**

Option B chosen over per-subfunction (~19). Domain entity level: ap_invoice, ap_payment, ap_aging, ar_invoice, gl_journal_entry, treasury_position, etc. Each BO = one canonical object type resolved at the Canonical Evaluation boundary.

**5. Canonical layer first, source chain later**

Source + Admission contracts are per-source-system (one set per SAP instance, per Salesforce org). Metric contracts are fully source-agnostic. Build the canonical layer (BF → BO → CC) first, then metric contracts, and leave source chain for when real systems connect.

### Implementation Phases

| Phase | What | Count (Finance) | Source of Truth |
|-------|------|-----------------|-----------------|
| 1 | Business Fields | ~1,600 | metric_formula_variable.field_name (deduplicated) |
| 2 | Business Objects | ~40-50 | Cluster input fields by subfunction + domain entity |
| 3 | BO-Field junction | ~3,000-5,000 | Map each input field to its BO |
| 4 | Canonical Contracts | ~40-50 (1 per BO) | Auto-generate from BO definition |
| 5 | Metric Contracts | 687 | Promote each metric_definition |
| 6 | Metric Bindings | ~1,500-2,000 | Each MC → N CCs based on input fields used |
| 7 | Contract Lineage | ~2,000+ | MC depends_on CC, derived MC depends_on upstream MC |

## Options Considered

### Option A: Top-Down (Source → Canonical → Metric)
Design BOs speculatively from domain knowledge, then map metrics to them.
**Rejected:** Requires guessing what fields metrics need. We already have the answer in formula variables.

### Option B: Bottom-Up from Metric Variables (CHOSEN)
Extract BOs and BFs from the 2,210 formula variables that already exist.
**Chosen:** Every field is justified by at least one metric. No speculative design.

### Option C: Hybrid — Domain Templates + Variable Validation
Start with ISO 20022/CEFACT BO templates, validate against variable field_names.
**Deferred:** Good for future enrichment of external standards provenance, but unnecessary for initial generation.

## Consequences

### Positive
- Every Business Field justified by at least one metric formula
- No speculative BO design
- Canonical layer immediately useful for metric contract generation
- Source chain can be connected incrementally without blocking metrics

### Negative
- BOs derived from metric inputs may not perfectly match source system entity boundaries
- Some fields may cluster ambiguously between BOs (requires domain judgment)

### Risks
- Field deduplication: same field_name may have different meanings across subfunctions
- BO clustering: automated grouping may produce suboptimal entity boundaries (mitigated by human review)
- DAG support: only 1 derived metric exists today — DAG plumbing designed but lightly tested
