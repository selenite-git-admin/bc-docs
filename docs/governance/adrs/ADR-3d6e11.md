---
uid: DEC-3d6e11
title: "DAG Support in Contract JSON Shapes — Derived CO Evaluation + Secondary Metric Evaluation"
description: "Formalizes contract_json shapes for derived COs (CO-to-CO DAG) and secondary metrics (Metric-to-Metric DAG)"
status: implemented
subdomain: dag-support
focus: derived-co-secondary-metric
date: 2026-03-24
project: bc-infra
domain: database
refs:
  - type: decision
    label: "D200"
  - type: decision
    label: "D201"
authority: authoritative
migrated_from: legacy v2 archive
---


# DAG Support in Contract JSON Shapes — Derived CO Evaluation + Secondary Metric Evaluation

## Context

Foundation spec explicitly defines two DAGs: derived COs (CO→CO) and secondary metrics (Metric→Metric). DB infrastructure exists (business_object_relation, contract_lineage, metric_binding). The gap is in the contract_json shapes inside mapping and metric contract versions — they only handle the primary path (SO→CO, CO→Metric) today. Formalizing the JSON shapes and meta-schemas closes the gap without new tables.

## Foundation Spec Requirements

**CO DAG** (canonical-object.md line 16): "A derived Canonical Object is created from one or more existing Canonical Objects evaluated under a Contract. Derived Canonical Objects form a directed acyclic graph."

**Metric DAG** (metric-snapshot.md line 16): "A Metric Snapshot may also reference one or more upstream Metric Snapshots. This permits secondary and derived metrics that compose measurements from previously finalized snapshots, forming a directed acyclic graph."

**Metric Evaluation** (metric-evaluation.md line 14): "A Metric Evaluation is created in reference to one or more Canonical Objects and/or one or more upstream Metric Snapshots, and exactly one Metric Contract."

**Metric Snapshot** (metric-snapshot.md line 28): "A Metric Snapshot must reference one or more Canonical Objects, or one or more upstream Metric Snapshots, or both."

## DB Infrastructure (already exists)

- `business_object_relation` — BO-level DAG (derives_from, composes, relates_to)
- `business_object.tier_code` — basic | derived
- `contract.contract_lineage` — generic cross-contract DAG edges
- `metric.metric_binding` — metric → canonical contract binding

No new tables needed.

## What's Missing: contract_json Shapes

### 1. Canonical Mapping — evaluation_type field

`canonical_mapping_version.mapping_json` must support both primary and derived evaluation:

```json
// PRIMARY (SO → CO via Admitted Records)
{
  "evaluation_type": "primary",
  "source_bindings": [
    { "observation_contract_id": "uuid", "role": "primary", "field_contributions": [...] }
  ],
  "resolution_rules": { "business_key": [...], "temporal_field": "..." }
}

// DERIVED (CO → CO via upstream Canonical Objects)
{
  "evaluation_type": "derived",
  "upstream_bindings": [
    { "canonical_contract_id": "uuid", "role": "input", "field_contributions": [...] }
  ],
  "derivation_rules": { "aggregation": "...", "composition": "..." }
}
```

### 2. Metric Contract — input_type field

`metric_contract_version.contract_json` must support primary, secondary, and composite:

```json
// PRIMARY (CO → Metric)
{
  "input_type": "primary",
  "input_bindings": [
    { "canonical_contract_id": "uuid", "fields_used": [...] }
  ],
  "formula": "...", "temporal_gate": {...}, "indicators": [...]
}

// SECONDARY (Metric → Metric, DAG)
{
  "input_type": "secondary",
  "upstream_metric_bindings": [
    { "metric_contract_id": "uuid", "snapshot_role": "input" }
  ],
  "formula": "...", "temporal_gate": {...}, "indicators": [...]
}

// COMPOSITE (CO + Metric → Metric, both inputs)
{
  "input_type": "composite",
  "input_bindings": [...],
  "upstream_metric_bindings": [...],
  "formula": "...", "temporal_gate": {...}, "indicators": [...]
}
```

### 3. Meta-Schema Validation

Update `contract.contract_meta_schema` entries:
- `barecount/canonical-mapping/v1` — add evaluation_type enum, upstream_bindings shape
- `barecount/metric/v1` — add input_type enum, upstream_metric_bindings shape

### 4. Cycle Detection Invariant

Foundation spec: "must not form a reference cycle" (both CO and Metric).

The `contract_lineage` table can enforce this at write time — before inserting a new edge, traverse the graph to confirm no cycle is created. Implement as a DB function or application-level check.

## Impact on D200/D201

- D201 (BO Enrichment): No impact — BO tier_code and business_object_relation already model the DAG. Enrichment marks derived BOs correctly.
- D200 (Reader Wizard): Step 8 (Canonical Mapping) must present evaluation_type choice. For derived COs, the wizard selects upstream canonical contracts instead of observation contracts.
- D200 Phase 2 (AI Mapping): For derived COs, the AI mapper suggests upstream CO field contributions instead of source field mappings.

## Consequences

N/A
