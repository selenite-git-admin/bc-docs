---
uid: DEC-ec9e89
title: "Contract Governance Model — Master Shape, Platform Instance, Tenant Override"
description: "Three-level contract model: one master shape per family (contract_meta_schema), N platform instances (contract_json), tenant overrides (contract_binding). Field-level governance: overridable (value substitution), extensible (array addition), fixed (immutable). New contract requests via workflow for tenant-commissioned contracts."
status: implemented
subdomain: governance
focus: master-shape
date: 2026-04-01T06:19:30.108Z
project: bc-docs
domain: foundation
supersedes: DEC-03db11
authority: authoritative
migrated_from: legacy v2 archive
---

# D233: Contract Governance Model — Master Shape, Platform Instance, Tenant Override

## Context

BareCount contracts govern every boundary in the data progression chain. Six families exist:
Source (SC), Admission (AC), Observation (OC), Canonical (CC), Metric (MC), Intervention (IC).

Two problems existed before this decision:

1. **No single-location principle.** 46 canonical and 54 metric contracts each carry a full JSON body — shape definition duplicated in every instance. The runtime has no canonical "what does a metric contract look like?" — it infers it from the instances.

2. **No tenant customisation model.** Tenants need to customise contracts (thresholds, Z-fields, Z-tables) but there was no formal mechanism. Ad-hoc overrides risked inconsistency and dual sources of truth.

The AWS IAM policy model resolves both. IAM has one policy schema, thousands of policy instances, and per-account inline policies — all three levels cleanly separated, no duplication.

## Decision

### Three-Level Contract Model

```
Level 1 — Master Shape  (1 per family, locked)
  Storage:  contract.contract_meta_schema
  Source:   legacy-v2/docs/system/foundation/contract-schemas/
  Purpose:  Defines the shape. Declares field governance. Runtime loads this once.

Level 2 — Platform Instance  (N per family)
  Storage:  contract_json on {family}_contract_version table
  Purpose:  Instance-specific values only. Nothing structural.
            e.g. metric MT-04105: formula text, CO binding IDs, default thresholds

Level 3 — Tenant Override  (per tenant, per contract)
  Storage:  tenant.contract_binding (override_json + extensions_json)
  Purpose:  Tenant customisation within bounds declared by master shape.
```

### Field-Level Governance (declared in master shape)

Every field in the master shape carries one of three governance attributes:

| Attribute | Meaning | Applies to |
|-----------|---------|------------|
| `fixed` | Tenant cannot touch. Platform-only. | formula, co_bindings, evaluation_tier |
| `overridable` | Tenant can substitute the value. | thresholds, drift_detection.enforcement, temporal_gate |
| `extensible` | Tenant can add items to the array. | source fields (Z-fields), admission rules |

### Override Cases by Family

**Metric (MC):** Value override only. Thresholds are `overridable`. Formula and co_bindings are `fixed`. Tenant cannot change how the metric is computed — only what constitutes excellent/good/warning/critical for their business context.

**Source (SC):** Both override types apply.
- `overridable`: drift_detection enforcement (strict → warn for a lenient tenant)
- `extensible`: fields[] — tenant adds Z-fields (ZZVENDOR, ZZREGION, ZZCOST_CENTER) to a platform-defined standard table contract

**Admission (AC):** Both override types.
- `overridable`: max_observation_age, validation_policy severity
- `extensible`: admissibility_rules[] — tenant adds custom business rules on top of platform defaults

**Canonical (CC):** Fixed only. The universal CO shape is platform-defined and immutable per tenant.

**Observation (OC):** Fixed only. Field mapping is platform-defined.

**Intervention (IC):** Value override only. Escalation chain contacts are `overridable`.

### New Contract Request Workflow (Tenant-Commissioned Contracts)

When a tenant needs a contract for a structure that has no platform equivalent (e.g., SAP Z-table ZZPURCHASE_REQUESTS, custom Salesforce object), they cannot self-serve — they submit a contract request:

```
Tenant requests → Platform team creates instance → Scoped to requesting tenant
→ Same master shape applies → Bound via contract_binding
```

This is equivalent to AWS inline policies — same policy schema, new instance, scoped to one account. Not a schema change. Not a bypass. A new instance of the existing master.

### Runtime Evaluation

```
1. Load master shape from contract_meta_schema (category + version)
2. Load platform instance from contract_json
3. Load tenant override from contract_binding (if exists)
4. Merge: instance values + tenant overrides (only overridable/extensible fields)
5. Execute against merged effective contract
```

No joins across 54 JSONs. One master, one instance, one override. Three reads.

## Consequences

### Positive
- Shape defined once — no duplication across instances
- Tenant customisation is explicit and bounded — governed, not ad-hoc
- Runtime is simple — three reads, deterministic merge
- New tenant-specific contracts follow the same model — no special casing
- Foundation JSON schemas have a clear, permanent role: they ARE the master shapes

### Negative
- `contract_meta_schema` table needs populating (currently empty or underused)
- Existing 46 canonical + 54 metric contract_json bodies need trimming (remove structural duplication)
- `contract_binding` needs `extensions_json` column for extensible fields (source, admission)
- Tenant-commissioned contract request workflow does not exist yet — needs design

## Options Considered

**A. Instance-only (current state):** Each contract_json carries the full body. No master. No tenant model. Rejected — shape duplicated N times, no tenant customisation path.

**B. Relational normalization:** Normalize all contract bodies into tables. Rejected — variable-shape bodies (source schema declarations, admission rule sets) resist normalization without EAV anti-patterns.

**C. Three-level model with field governance (chosen):** Master + instance + override. Clean separation of concerns. AWS-validated at scale.
