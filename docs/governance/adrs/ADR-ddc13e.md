---
uid: DEC-ddc13e
title: "Concept↔source soft-reference layer — catalog-anchored, advisory, drives SDG + chain generation"
description: "Soft, advisory concept_registry.concept_source_reference (business_concept ↔ source.source_field FK) that generates SDG emission + draft OC/SC/AC; never read by evaluation (OC hard-bind stays authority); FK-to-catalog forbids un-onboarded refs so SDG/SC/AC/OC share one source-of-truth."
status: decided
date: 2026-07-07T13:10:53.447Z
project: bc-core
domain: sources
subdomain: source-reference
focus: codegen-scaffold
---

# Concept↔source soft-reference layer — catalog-anchored, advisory, drives SDG + chain generation

## Context

The SDG audit (SES-405040) showed the generator is capable (open-items, discount, SHKZG, opt-in FX all built) but SDG field-tuning + SC/AC/OC authoring are hand-done and drift-prone, and there was no link between the semantic concept layer (concept_registry) and the physical source catalog (source.source_field, 481k SAP fields already onboarded). A soft, catalog-anchored reference collapses 'hand-tune SDG per field + hand-author every contract' into 'declare the concept→field profile once, generate.' It compounds with catalog-first (D499): metrics catalogue against BCF concepts (lead); when demand pulls a metric, its chain is GENERATED from the soft-ref profile rather than authored. Making it a FK bridge between two EXISTING catalogs (not free strings) avoids drift and reuses the 481k-row source inventory. Keeping it advisory/design-time-only is the single rule that lets it exist without violating source-agnosticism — evaluation authority stays with the OC hard-bind.

## Decision

Add a SOFT, advisory, design-time reference layer linking a BCF business_concept to a physical source field, to serve as the single seed from which SDG field-emission, draft OC field_mappings, and SC/AC declarations are GENERATED — the structural spine of the SDG-optimization + catalog-first program (DEC-542722/D499, DEC-a6cdae/D498, D475).

**Table (approved 2026-07-07):** concept_registry.concept_source_reference
- reference_id uuid PK
- business_concept_id uuid FK → concept_registry.business_concept (source-agnostic; untouched)
- source_field_id uuid FK → source.source_field (the onboarded 481k-row catalog; encodes system→table→field)
- transform_hint text ('direct' | 'sign_from:SHKZG' | 'code_lookup:…')
- rank int default 1 (preferred candidate when >1)
- is_advisory boolean not null default true
- notes, added_by, added_at
- unique (business_concept_id, source_field_id); index each FK

**Foundational invariants this preserves:**
1. EVALUATION NEVER READS IT. The governed OC field_mapping hard-bind remains the sole authority of record at the evaluation boundary (Invariant IV). The soft-ref only generates a DRAFT of the OC; it is compiled into hard artifacts, never consumed at runtime. This is what keeps concepts source-agnostic (the cross-system portability test still holds — a second source gets its own soft-refs; the concept is untouched).
2. FK-TO-CATALOG ROBUSTNESS (operator insight, SES-405040): source_field_id FKs the onboarded source catalog, so a soft-ref CANNOT point at an un-onboarded field. Knowing a mapping (e.g. Oracle) is inert until that source is catalogued as source_system→version→module→object→field — the SAME catalog SC/AC bind against. Result: SDG, SC, AC, OC, and the soft-ref all anchor to ONE source-of-truth; no drift; catalog-onboarding is the explicit floor for any new source system, shared with SC/AC.

**Generator (separate build):** reads concept_source_reference ⋈ source_field ⋈ (walk to system) → emits (a) SDG field-emission profile, (b) draft OC field_mappings, (c) SC/AC declarations. Seed the soft-refs first for the concepts behind the current 108 chain-ready metrics.

**Implementation path:** governed platform-schema change — bc-core Drizzle schema + DDL in docker/redesign/, not a psql hand-create.
