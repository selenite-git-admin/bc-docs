---
uid: DEC-f0eb14
title: "System Documentation Framework — 4-Stream, Module-Component Architecture"
description: "Component-centric documentation framework: Foundation (F01-F02), Platform (P01-P10), Tenant (T01-T06), Common (C01-C02) streams with per-component dossiers"
status: implemented
subdomain: documentation
focus: framework-streams
date: 2026-03-30
project: bc-docs
domain: platform
refs:
  - type: decision
    uid: DEC-b80330
    label: "D230: Implementation approach — split dossiers, diagram layer, bc-docs structure"
authority: authoritative
migrated_from: legacy v2 archive
---


# System Documentation Framework — 3-Stream, Module-Component Architecture

## Context

Root cause of repeated session course corrections: documentation described conceptual model well but didn't reliably describe the implemented system. Sessions read beautiful theory but had no reliable map of what's actually built, what state each component is in, and what the real constraints are. 

Component-centric documentation with full dossiers per component ensures every question a session could ask is answered in one place. The 3-stream separation prevents platform/tenant confusion that caused multiple rollbacks. The one-name-everywhere principle prevents vocabulary drift that silently corrupted data.

Adopt a 3-stream, module-component documentation framework for all BareCount system documentation.

## Structure

Five documentation streams mapped to system boundaries:
- **Foundation Stream (Fxx)** — locked reference pillars (execution model, naming, patent). Every module refers to these; nobody modifies them without explicit approval.
- **Platform Stream (Pxx)** — platform DB, @PlatformOnly APIs, bc-admin UI
- **Tenant Stream (Txx)** — tenant DB, @TenantScoped APIs, bc-portal UI
- **Common Stream (Cxx)** — cross-stream shared concerns
- **AI Stream (Axx)** — bc-ai service (Python/FastAPI), agents, models, evidence, guardrails. Separate repo, separate runtime, serves all consumers.

## Foundation Stream Modules (F01–F02, LOCKED)

F01: Foundation — Execution Model specification, Forbidden Vocabulary, Naming Conventions (ISO 11179), Evaluation Boundaries, Object Lifecycle, Binding Chain
F02: Patent — Claims mapping, Prior art references, Patent-protected patterns

Authority: locked. Read-only reference. No session modifies these without explicit approval. Every dossier's Section 01 (Specification) references F01/F02 — it does not duplicate their content.

## Platform Stream Modules (P01–P10)

P01: Source Catalog (7 components) — Provider, System, Version, Module, Source Table, Source Field, Catalog Verification
P02: Contract Registry (10) — SC, AC, OC, CC, MC, IC, Contract Governance, Canonical Constructor, Canonical Map, Contract Chain Integrity
P03: Business Definitions (4) — Business Field, Business Object, Business Object Map, BO Verification
P04: Metric Catalog (7) — Metric Definition, Metric Formula, Metric Binding, Metric Constructor, Enrichment Job, Metric Map, Metric Integrity
P05: Runtime Definitions (6) — Connector, Reader, Reader Constructor, Admission Run, Reader Map, Reader Integrity
P06: Boundary Execution/Platform PoV (5) — Evaluation Engines, Orchestrator, Contract Validation, Reader Runtime, Execution Rollups
P07: Evidence & Lineage/Platform PoV (2) — Evidence Service, Lineage Service
P08: Tenancy (3) — Tenant Management, Tenant Provisioning, Contract Binding
P09: Platform Services (5) — Discovery, Library/SBOM, Packages, Support, Activity Log
P10: Master Data (6) — Functions & Subfunctions, Industries, System Types, Currencies, Countries, Statuses

## Tenant Stream Modules (T01–T06, to be detailed in separate session)

T01: Boundary Data (9 tenant tables)
T02: Evidence & Lineage Data (3 tables)
T03: Connections (3 tables)
T04: Execution Runs (4 tables)
T05: Tenant User & Goals (3 tables)
T06: Tenant Views (/api/t/* filtered reads)

## Common Stream Modules (C01–C02)

C01: Authentication — Cognito JWT, Guards, Scopes, platform_user
C02: Infrastructure — feature flags, email templates, notifications, idempotency

## AI Stream Modules (A01–A05)

A01: Agent Platform (5 components) — Model Registry, Evidence Store, Budget Controls, Cache & Pin, Prompt Management
A02: Construction Agents (7) — BO Composer, Field Mapper, Metric Tracer, Evaluation Advisor, Chain Auditor, Checker Agent, QA Gate
A03: KPI Assistant (6) — Intent Resolver, Catalog Retriever, Snapshot Retriever, Grounded Composer, Output Validator, Access Control
A04: Enrichment Pipeline (4) — Formula Enrichment, Knowledge Enrichment, Semantic Dedup, Maturity Promotion
A05: Guardrails & Trust (4) — Bedrock Guardrails, Tenant Fence, Help Article RAG, Exposure Protection

## Per-Component Dossier (9 sections)

1. Specification & Foundation — invariants, patent refs, forbidden vocabulary
2. Architecture — ADR references, relationships, position in master flow
3. Data Structure — DDL tables (authoritative), Drizzle schemas, columns, FKs, indexes
4. UI & API — endpoints, DTOs, UI pages
5. Data Seeding — seed scripts, golden snapshot coverage
6. Data Enrichment — AI verification, batch processing
7. Integrity Tests — validation rules, cross-component checks
8. Implementation Status — what works, what's scaffolding, DDL↔Drizzle alignment
9. Open Issues — contradictions, parked tasks, tech debt

## Per-Module Standard Components

Each module owns its full lifecycle (where applicable):
- Definitions (tables, CRUD)
- Constructor (guided creation workflow)
- Map (field tracing visualization)
- Integrity (chain completeness validation)
- Enrichment (AI/batch enhancement)
- Verification (AI confidence scoring)

No global grab-bag modules. Wizards, maps, integrity checks all live in their home module.

## Naming Principles

1. One name everywhere — docs = DB = API. No vocabulary-only renames.
2. Field map tables follow same pattern: observation_field_map, canonical_field_map
3. Map APIs follow same pattern: /api/reader-map, /api/canonical-map, /api/metric-map

## Planned Renames/Restructures

1. source.source_object → source.source_table (DDL+Drizzle+API)
2. canonical_mapping + canonical_mapping_version → canonical_field_map (fold into CC)
3. business_object_relation → business_object_map
4. New business schema (extract from contract)
5. /api/core-map → /api/reader-map
6. /api/mapping-bindings → /api/canonical-map

## Coverage Verification

75/75 platform DDL tables mapped to modules. Zero gaps. 4 Drizzle-only metric tables need DDL addition.

AI stream: 26 components across 5 modules. bc-ai is Python/SQLite — no DDL overlap with platform DDL. Coverage verified against D222, D223, DEC-e82f0a, DEC-d214ed, PLN-86b3fc.

## Consequences

N/A
