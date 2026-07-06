---
uid: DEC-03db11
title: "Contract Body Principle — JSON-First, Catalog-Separate"
description: "Unifies contract representation: JSON body for all 6 families. Metric contract_json (currently vestigial) gets a defined shape. Catalog tables (metric_definition, etc.) are UI convenience, not the contract."
status: superseded
superseded_by: DEC-ec9e89
date: 2026-04-01T05:08:02.723Z
project: bc-docs
domain: foundation
authority: authoritative
migrated_from: legacy v2 archive
---

# D232: Contract Body Principle — JSON-First, Catalog-Separate

## Context

BareCount is a contract-driven data progression platform. Six contract families govern the four execution boundaries:

| Chain | Contracts | Nature |
|-------|-----------|--------|
| Source | Source (SC), Admission (AC), Observation (OC) | Execution-only |
| Canonical | Canonical (CC), Mapping Binding | Business-bound |
| Metric | Metric (MC), Intervention (IC) | Business-bound |
| AI | AI (provisional) | TBD |

The original contract design was influenced by AWS patterns (JSON everywhere). Legacy foundation schemas in `legacy-v2/docs/system/foundation/contract-schemas/` defined JSON Schema shapes for each family. These were conceptual specs — never validated at runtime.

During implementation, two divergent patterns emerged:

1. **Source/Admission/Canonical/Observation** — contract body stored as `contract_json` (JSONB) on the version table. The JSON IS the contract.
2. **Metric** — body fully normalized across 8 tables (`metric_definition`, `metric_formula`, `metric_formula_variable`, `metric_knowledge`, `metric_binding`, `metric_formula_verification`, `metric_enrichment_job`, `metric_contract`). The `contract_json` column exists but is vestigial/empty.

The metric normalization happened because metric was the most heavily developed family — formula authoring, AI verification, enrichment pipelines, and catalog UI all drove table creation. This was UI-influenced, not contract-design-driven.

The asymmetry creates confusion: "is a contract a JSON document or a set of relational rows?" The answer must be one principle for all families.

## Decision

### Principle: The contract body is always a JSON document.

All six contract families store their body as a JSON document in `contract_json` on the `_version` table. This JSON is:

- **Versioned** — each version has its own frozen JSON body
- **Immutable** — once a version is approved, its JSON never changes
- **Self-contained** — the runtime reads one JSON document to execute, no joins required
- **Authoritative for execution** — the runtime binds to this, not to catalog tables

### Two-Layer Architecture

**Execution Layer (JSON):**
Every contract family produces a versioned JSON body. The runtime evaluation engine reads `contract_json` from the version table. No table joins, no JSONB queries — just read the document.

**Catalog Layer (relational, optional):**
Business-bound chains (canonical, metric) also maintain normalized catalog tables for UI queryability. These tables serve browsing, filtering, comparison, and display — NOT execution. Catalog is authoritative for display, contract JSON is authoritative for execution.

| Chain | Execution Layer | Catalog Layer |
|-------|----------------|---------------|
| Source (SC, AC, OC) | `contract_json` | None needed |
| Canonical (CC) | `contract_json` | `business_object`, `business_object_field` |
| Metric (MC, IC) | `contract_json` | `metric_definition`, `metric_formula`, `metric_knowledge`, `metric_binding` |
| AI | `contract_json` | TBD |

### Metric contract_json — now required

The metric `contract_json` body gets a defined shape. The existing 8 metric tables remain as the catalog layer. When a metric contract version is created/approved, the body is serialized into `contract_json` — formula, thresholds, CO bindings, temporal gate, output schema.

### Foundation Schemas Become Body Validators

The legacy JSON schemas in `legacy-v2/docs/system/foundation/contract-schemas/` are updated to match reality and registered in `contract_meta_schema` as body validators. Each family gets a v1 body schema that defines what goes inside `contract_json`.

## Consequences

### Positive
- One mental model for all contract families
- Contracts are portable — export/import as JSON, diff versions as JSON
- Runtime is simple — read one document per boundary evaluation
- Catalog layer is explicit — no confusion about what's "the contract" vs "the UI view"

### Negative
- Metric needs a defined contract_json body shape (new work)
- Existing metric catalog tables and contract_json may drift — need sync discipline or generation
- Legacy foundation schemas need updating to match implemented reality

## Options Considered

**A. JSON-first (chosen):** Contract body is always JSON. Catalog tables are separate UI concern.

**B. Relational-first:** Normalize all contract bodies into tables. Rejected — source/admission/canonical bodies are inherently variable-shape (schema declarations, rule sets). Normalizing pushes toward EAV patterns.

**C. Compile model:** Author in tables, compile to JSON at publish. Rejected — adds complexity (two representations + sync) without clear benefit over Option A.
