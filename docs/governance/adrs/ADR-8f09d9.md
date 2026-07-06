---
uid: DEC-8f09d9
title: "Restore Computation Grain to Metric Contract Body"
description: "Add explicit grain[] to MC body — always required, same structure as CC grain, derived by constructor at generation time"
status: implemented
subdomain: metric-architecture
focus: grain-declaration
date: 2026-04-02
project: bc-core
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---

# D254: Restore Computation Grain to Metric Contract Body

## Context

ADR-0003 (the original 3-contract architecture) explicitly specified **aggregation grain** as part of the KPI Contract scope:

> "Scope: Metric definitions over GDP (formula, inputs, filters, **aggregation grain**, thresholds, data quality predicates, delivery SLAs)."

The legacy `metric-v1.json` implemented this as `computation_contract.grain` — a comma-separated string. During the D253 body restructure, grain was silently dropped. The current MC body has 8 required keys with no grain declaration.

Without grain, the Metric Evaluator has no declaration of what dimensional level a Metric Snapshot is produced at.

## Decision

**Add `grain` to the MC v1 body schema as the 9th required key. Always explicit — no implicit inheritance.**

Every MC declares its grain dimensions in the same array-of-objects format as CC grain. The contract says what it means. The Contract Constructor derives grain automatically at generation time.

### Why Explicit, Not Inherited

1. **Multiple COs (D021):** MCs bind to N CCs. Each CC may have different grain. `"inherit"` is ambiguous — inherit from which CC?
2. **DAG cases:** Secondary MCs (`input_type: "secondary"`) consume upstream Metric Snapshots, not COs. There is no CC to inherit from.
3. **D253 principle:** Same type = same shape = always. No magic, no runtime resolution.
4. **The contract says what it means:** A reader knows the output grain without chasing CC references.
5. **Constructor handles the work:** Grain is derived once at generation time, not maintained manually.

### Structure

Identical format to CC `body.grain`:

```json
"grain": [
  { "key": "company_code", "source": "business_field", "field_code": "company_code" },
  { "key": "fiscal_period", "source": "evaluation_period" }
]
```

### Schema

```json
"grain": {
  "type": "array",
  "minItems": 1,
  "items": {
    "type": "object",
    "required": ["key", "source"],
    "additionalProperties": false,
    "properties": {
      "key": { "type": "string", "description": "Grain dimension name" },
      "source": { "type": "string", "enum": ["business_field", "evaluation_period"] },
      "field_code": { "type": "string", "description": "Business field code (when source=business_field)" }
    }
  },
  "description": "Aggregation granularity of metric output — one Metric Snapshot per grain combination",
  "x-governance": "fixed"
}
```

### Two-Level Grain Model

| Level | Contract | Purpose | Example |
|-------|----------|---------|---------|
| **Canonical grain** | CC `body.grain` | Dimensional identity of one CO | `[company_code, fiscal_period]` |
| **Computation grain** | MC `body.grain` | Aggregation level of metric output | `[company_code, fiscal_period]` or `[fiscal_year]` (coarser) |

### Evaluator Behaviour

1. Collect COs/Metric Snapshots matching `co_bindings`
2. Group by MC `grain` dimensions
3. For each grain combination: apply `formula` using `variables`
4. Produce one Metric Snapshot per grain combination

When MC grain = CC grain: one-to-one, no aggregation.
When MC grain is coarser: aggregate across omitted dimensions before formula application.

### Constructor Derivation Rules

The Metric Contract Constructor derives grain as follows:

| Scenario | Derivation |
|----------|-----------|
| Single primary CC | Copy CC `body.grain` |
| Multiple primary CCs, same grain | Copy shared grain |
| Multiple primary CCs, different grain | Intersection of grain dimensions (common keys only) |
| Secondary MC (metric DAG) | Copy grain from primary upstream MC |
| Group-level rollup | Manual specification — constructor cannot infer aggregation intent |

### Examples

**Per-company per-period (same as CC):**
```json
{
  "grain": [
    { "key": "company_code", "source": "business_field", "field_code": "company_code" },
    { "key": "fiscal_period", "source": "evaluation_period" }
  ]
}
```

**Group-level rollup (coarser):**
```json
{
  "grain": [
    { "key": "fiscal_year", "source": "evaluation_period" }
  ]
}
```

## Governance

`x-governance: "fixed"` — computation grain is platform-defined. Tenants cannot override grain. Changing the grain changes the meaning of the metric value.

## MC Body After D254

9 required keys (was 8):

| Key | Governance | Description |
|-----|-----------|-------------|
| `input_type` | fixed | primary (COs) or secondary (upstream Metric Snapshots) |
| `formula` | fixed | Symbolic computation formula |
| `variables` | fixed | Named variable bindings (formula to CO fields) |
| `co_bindings` | fixed | Which CCs feed this metric |
| `temporal_gate` | fixed | When to evaluate (periods, completeness) |
| `unit` | fixed | Output unit (days, %, $, count, ratio) |
| `direction_code` | fixed | higher-is-better, lower-is-better, target-is-optimal |
| `thresholds` | overridable | 4-band classification |
| **`grain`** | **fixed** | **Explicit aggregation grain — array of {key, source, field_code}** |

## Impact

| Artifact | Change |
|----------|--------|
| `metric-v1.schema.json` | Add `grain` to body required + properties |
| `contract.contract_meta_schema` | Update metric v1 row in DB |
| 687 MC instances | Add grain to `contract_json` (constructor derives from CC grain) |
| `metric-v1.md` foundation doc | Add grain section |
| `contract-requirements-v1.md` | Update CR-MC-002 keys table |
| `05-generators.md` constructor doc | Update Metric Generator to include grain derivation |
| Portal Contract tab | Display computation grain dimensions |

## References

- ADR-0003 — Original 3-contract architecture ("aggregation grain" in KPI scope)
- D249 — MC body structure (LOCKED, now amended by this ADR)
- D253 — Structural completeness (all keys required)
- D233 — Three-level governance (grain is fixed)
