---
uid: DEC-01df6b
title: "Metric Catalog Tables are Derived from contract_json — JSON Authored, Catalog Decomposed"
description: "contract_json is authored, catalog tables (metric_formula, metric_formula_variable, metric_binding) are derived by decomposition. No direct writes to catalog tables. Evaluator reads JSON only. UI reads catalog only. Rebuild-safe."
status: implemented
subdomain: metric-architecture
focus: json-authored-derived
date: 2026-04-02T05:06:59.159Z
project: bc-docs
domain: foundation
migrated_from: legacy v2 archive
---

# Metric Catalog Tables are Derived from contract_json — JSON Authored, Catalog Decomposed

## Context

Three catalog tables duplicated contract_json content (formula, variables, bindings) creating dual-source-of-truth risk. D232 established JSON-first for execution. The compile model (catalog → JSON) was rejected because formula + variables + co_bindings must be internally consistent — authoring as separate rows then compiling creates consistency risk at the seams. JSON-authored, catalog-derived is safe because decomposition is lossless and repeatable.

## What

For Metric Contracts, the contract_json body is the single authored source of truth. The catalog tables (metric_formula, metric_formula_variable, metric_binding) are derived — decomposed from contract_json on version creation for UI queryability.

### Direction

```
contract_json (authored) → decompose → catalog tables (derived)
```

NOT the reverse. NOT bidirectional.

### Rules

1. contract_json is authored directly (via UI form that produces JSON, or via API)
2. On version creation, system decomposes contract_json into catalog tables
3. Metric Evaluator reads contract_json ONLY — never catalog tables
4. UI reads catalog tables for display, search, filtering
5. If catalog and contract_json disagree → contract_json wins
6. Catalog tables can be rebuilt from contract_json at any time
7. No direct writes to metric_formula, metric_formula_variable, metric_binding — they are derived artifacts

### Table Classification

| Table | Role | Source of Truth? |
|-------|------|-----------------|
| metric_contract + _version | Contract identity + contract_json | YES — authoritative |
| metric_definition | Catalog identity (name, description) | Derived from header |
| metric_formula | Formula text, SQL logic | Derived from body.formula, body.sql_logic |
| metric_formula_variable | Variable bindings | Derived from body.variables[] |
| metric_binding | CO bindings | Derived from body.co_bindings[] |
| metric_definition_knowledge | Narrative, context, peer comparisons | Independent — NOT contract content |
| metric_formula_verification | AI verification results | Independent — NOT contract content |
| metric_enrichment_job | Enrichment tracking | Independent — NOT contract content |

### Why Not Catalog → JSON (compile model)?

Source Catalog uses catalog → JSON because catalog tables are the natural entry point for source metadata (scraped, discovered, imported). For metrics, the risk is different — formula, variables, and CO bindings must be internally consistent. Authoring them as separate table rows then compiling creates consistency risk at the seams. Authoring as one JSON document guarantees internal consistency. Decomposition is safe — compilation is not.

### Applies To

This decision applies to Metric Contracts specifically. Other families (SC, AC, OC, CC, IC) do not have equivalent catalog table duplication — their contract_json IS the only representation.
