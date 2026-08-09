---
uid: DEC-011ed2
title: "Catalog admission architecture: thin orchestrator + per-source adapters + shared ingest (no global monolith)"
description: "Catalog admission = generic orchestrator delegating to registered per-source child adapters; a shared ingest built once; global extract contract; governed per-source field-mapping data. Extends D557, complements D562."
status: decided
date: 2026-08-09T04:43:38.973Z
project: bc-core
domain: sources
subdomain: sources/catalog-admission
focus: architecture
---

# Catalog admission architecture: thin orchestrator + per-source adapters + shared ingest (no global monolith)

## Context

The catalog admission service is GLOBAL — it admits every source system's catalog (Odoo, SAP, BC, Salesforce), whose model taxonomies we do not know in advance. Operator direction (2026-08-09): the main service must call source-system-specific child services; a global scope will never work smoothly, and putting all sources in one block renders it unmaintainable. Two failure modes of a global monolith: (a) over-normalize and lose each source's real semantics; (b) accumulate unmaintainable per-source branches. A whitelist (admit only the universal 'table') stays correct for any future source; a blacklist of one source's reject kinds silently mis-handles the next source. DRY: the extract-consumption (parse -> governed writes) is identical for all sources, so it is built ONCE (shared ingest) and thin adapters call it, rather than N reimplementations. This mirrors existing per-source patterns already in the platform (reader flavors are per-source; the extractor is per-source). Timing: today's ExtractAdmissionService is ALREADY Odoo-coupled (mapFieldType with Odoo ttypes, the transient field, the objectType='table' hardcode) — extracting the Odoo adapter now, with only one source onboarded, is clean, with nothing to disentangle later. Keeping source-specific field mapping as governed DATA (a per-source mapping table) rather than code matches the platform's treatment of SAP mapping as universal/governed and minimizes per-source code to near-zero.

## Decision

Catalog admission is structured as a THIN GENERIC ORCHESTRATOR that delegates all source-specific work to registered PER-SOURCE CHILD ADAPTERS (OdooCatalogAdapter, later SapCatalogAdapter, etc.), resolved by system_code. There is NO global monolithic admission service that embeds source vocabulary.

THREE LAYERS:
1. Per-source EXTRACTOR (bc-sdg/systems/<sys>) emits a single GLOBAL EXTRACT CONTRACT — one common schema for every source: objects tagged with a source-agnostic object_type (table | view) + their raw native field descriptors. Source -> common SHAPE normalization (e.g. Odoo model classification via _abstract/_transient/_auto + pg_class relkind) lives HERE, in the source-specific extractor.
2. SHARED INGEST (bc-core, generic — the same for all sources, built ONCE): artefact evidence + mechanical verification, the governed source_object / source_field / typing writes, the substrate guards, and the ADMISSIBILITY WHITELIST. Every adapter CALLS this; none re-implements extract-parsing.
3. Thin per-source ADAPTER (bc-core): invokes its source's extractor, supplies source config, and calls the shared ingest. It owns only what is irreducibly source-specific. Registered by system_code (DI/factory).

RULES:
- The orchestrator and shared ingest NEVER contain source vocabulary. Admission WHITELISTS the universal object_type='table' (admit only that); it NEVER blacklists per-source reject kinds (abstract/transient/structure/pool). A whitelist stays correct for future sources whose shape is unknown; a blacklist of Odoo terms would silently mis-handle SAP structures/pools, etc.
- Field-type mapping (native type -> governed vocab) is a GOVERNED PER-SOURCE MAPPING TABLE (data, not code), applied by the shared ingest; the adapter owns only its rows. So a new source = a thin adapter + config + governed mapping rows, with ZERO orchestrator/ingest changes.
- Extract-consumption (verify -> write catalog -> guards) is built once and shared; it is not rebuilt per adapter.

This EXTENDS DEC-3078ce (D557) catalog-onboarding (the admit/verify/approve lifecycle is unchanged) and provides the STRUCTURAL MECHANISM for DEC-88870a (D562) — D562 is the admission-scope POLICY (only real source objects; non-tables are contamination); this ADR is HOW that policy is enforced without a global monolith.
