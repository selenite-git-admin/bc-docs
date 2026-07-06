---
uid: DEC-586ccb
title: "F06 Service Catalog — Catalog SVS as First Service"
description: "Establishes F06 Service Catalog — the foundation section housing all platform operational services. First service: Catalog SVS (Sourcing-Verification-Seeding) — 4-stage gated pipeline."
status: implemented
subdomain: foundation-spec
focus: service-catalog
date: 2026-04-03
project: bc-core
domain: foundation
authority: authoritative
migrated_from: legacy v2 archive
---

# F06 Service Catalog — Catalog SVS as First Service

## Context

BareCount Foundation defines the execution model (F01), the patent (F02), contract schemas (F03), solution architecture (F04), and data quality control (F05). But it has no section defining the **operational services** that keep the platform's data infrastructure healthy.

Session evidence exposed the gap: blind seeding of 14,459 source contracts from unverified scraper data created false readiness — cartesian-product observation contracts, 0% field mapping accuracy, wrong source tables. The AI field-map enrichment pipeline (maker-checker-gate) works correctly but produces RED results when fed unverified input. The platform needs governed services with quality gates.

## Decision

### 1. Establish F06: Service Catalog

A new foundation section (`F06: Service Catalog`) that defines all platform-level operational services. Each service has:

- **Purpose** — what problem it solves
- **Pipeline** — ordered stages with gates between them
- **Inputs/Outputs** — what it consumes and produces
- **Quality Gates** — what must pass before the next stage
- **Ownership** — which team/role operates it

### 2. Catalog SVS Service (First F06 Service)

**Catalog SVS** (Sourcing-Verification-Seeding) governs the lifecycle of source catalog data from external scraper sources through AI-verified quality gates to seeded contract instances and field-level mappings.

#### Pipeline

```
STAGE 1: SOURCING          STAGE 2: VERIFICATION       STAGE 3: SEEDING            STAGE 4: FIELD MAPPING
─────────────────          ──────────────────          ─────────────────           ───────────────────
Scraper outputs            AI + schema validation      DB writer                   AI maker-checker-gate
S3 cache archives          Cross-source reconcile      source_object/field         BF.source_aliases
leanx / se80 / sds         Dedup, rank, classify       SC + AC + OC               OC field_mappings

    │                          │                          │                          │
    ▼                          ▼                          ▼                          ▼
  GATE: file exists          GATE: verification         GATE: structural           GATE: confidence
  valid JSON                 score ≥ threshold          completeness               ≥ 0.85 (green)
  field count > 0            no critical conflicts      D253 compliance            checker agreement
```

#### Stage 1: Sourcing

Raw metadata extraction from external sources. No DB writes. Multiple sources per table.

| Source | Archive | Tables | Fields | Notes |
|--------|---------|--------|--------|-------|
| leanx.eu | `fields-leanx.tar.gz` (2.1MB) | 8,912 ECC | Per-table JSON | Cloudflare-gated, Playwright scraper |
| se80.co.uk | `fields-se80.tar.gz` (84KB) + `fields-s4.tar.gz` (4.7MB) | 32 ECC + 18,024 S/4HANA | Per-table JSON | In-browser fetch bypass |
| sapdatasheet.org | `sds-cache-full-110k.tar.gz` (796MB) | 110,000+ | Per-table HTML cache | Richest source — descriptions, types, lengths |

**S3 location**: `s3://barecount-dev-artifacts/sap-table-scraper/`

**Gate**: File exists, valid JSON/HTML, field count > 0, table name matches SAP naming convention.

#### Stage 2: Verification

Before any table enters the source catalog, it passes through verification:

1. **Schema Validation** — field count > 0, key fields present, types consistent with SAP conventions
2. **Cross-Source Reconciliation** — merge fields from multiple scrapers (leanx + sds may both have BSID), flag conflicts in field count/types/names
3. **Module Classification** — assign SAP module (FI, CO, SD, MM, etc.) and tier (T1 core / T2 extended / T3 reference)
4. **Relevance Scoring** — does this table matter for any known BO? Does it appear in the SAP_KEY_TABLES mapping?
5. **AI Quality Gate** — Gemini checker: "Is this a real SAP table? Are these fields consistent with its documented purpose?"

**Output**: Verified Table Manifest — one record per table with:
- `table_name`, `module`, `tier`, `field_count`, `key_fields[]`
- `sources[]` — which scrapers provided data, with field counts per source
- `verification_score` (0-1), `conflicts[]`, `ai_verdict` (pass/review/reject)

**Gate**: `verification_score ≥ 0.7`, no critical conflicts, AI verdict != reject.

#### Stage 3: Seeding

Only verified tables get seeded. Creates:

1. `source.source_object` + `source.source_field` — catalog entries with real field data
2. `contract.source_contract` + version — D253-compliant SC with field schema in `contract_json`
3. `contract.admission_contract` + version — D253-compliant AC with domain-aware DQC rules
4. `contract.observation_contract` + version — OC linking to CC via `business_object_code`, with `field_mappings` placeholder

**Gate**: D253 structural completeness (all keys present, uniform structure across family).

#### Stage 4: Field Mapping

AI-powered BF enrichment using bc-ai maker-checker-gate pipeline:

1. **Input**: BF definitions (business field name + definition + data_type) + verified source fields (SAP field name + native type + description)
2. **Maker** (Gemini 2.5 Flash): suggests field-level mappings with confidence and reasoning
3. **Checker** (Gemini 2.5 Flash): validates mappings independently
4. **Gate** (Gemini 2.5 Flash): compares maker/checker, issues PASS/FAIL/RETRY
5. **Output**: `BF.source_aliases` JSONB — per-system field references with confidence scores
6. **Regenerate**: OC `body.field_mappings` from `BF.source_aliases`

**Gate**: Pipeline routing = green (combined confidence ≥ 0.85). Amber = needs human review. Red = reject.

### 3. Other F06 Services (Future)

F06 will house all foundation services. Planned:

| Service | Purpose | Status |
|---------|---------|--------|
| **Catalog SVS** | Source catalog lifecycle (this ADR) | Decided |
| **Contract Constructor** | Contract instance generation from templates | Planned |
| **Chain Integrity Auditor** | Continuous chain health monitoring | Exists (integrity.service.ts) |
| **KPI Enrichment Service** | Metric definition + BO/BF generation | Exists (bc-ai agents) |
| **Evidence Recorder** | Immutable audit trail for all evaluations | Planned |

## Consequences

1. No more blind seeding — all source catalog writes go through SVS pipeline
2. Field mappings are AI-verified with maker-checker-gate confidence scores
3. False readiness eliminated — coverage matrix shows real per-system accuracy
4. Scraper data (800MB+ in S3) becomes usable through verification gates
5. Foundation section F06 provides a home for all operational services

## Governing Decisions

| ADR | Title | Relation |
|-----|-------|----------|
| D253 (DEC-bef347) | Structural Completeness | SVS Stage 3 enforces D253 on all seeded contracts |
| D255 (DEC-aa6251) | Contract Primitives (BO/BF) | SVS Stage 4 enriches BF.source_aliases |
| D244 | Master Shapes | SVS validates against locked JSON schemas |
| D043 | Exchange Rate Reader | Reader architecture that SVS plugs into |
