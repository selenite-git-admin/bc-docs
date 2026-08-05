---
uid: DEC-0b5a4c
title: "Source seed catalog moves to Postgres — Mongo bc_seed destined to retire; Odoo seeds greenfield through the new shape"
description: "Mongo bc_seed.seed_tables destined to retire; new source.seed_source_table (Postgres) is the seed store; Odoo 17 seeds greenfield from the live pilot instance; SAP migrates later one-then-many"
status: decided
date: 2026-08-05T01:59:54.169Z
project: bc-core
domain: sources
subdomain: sources/seed-catalog
focus: schema
---

# Source seed catalog moves to Postgres — Mongo bc_seed destined to retire; Odoo seeds greenfield through the new shape

## Context

Operator directive 2026-08-05 during the Odoo source-onboarding grounded study. Three grounds: (1) PATTERN ALREADY PROVEN — metric seeds made exactly this move (Mongo seed_metrics -> mcf.seed_metric, sole runtime authority since; TSK-6fd293 holds only the final Mongo retirement). Source seeds are the same class of curated platform reference data. (2) AUDITABILITY — the seed-catalog chapter itself records the known limitation that script-only Mongo writes bypass the audit substrate ("the audit substrate does not see the direct write"). Postgres brings seed writes under the same substrate as everything else. (3) TIMING — Odoo is about to be onboarded and has no Mongo legacy; seeding it greenfield through the new shape avoids creating one more migration burden, and the pilot instance provides version-exact instance-extract provenance that upgrades the docket from its provisional LGPL-scrape grade. Deferring SAP migration respects one-then-many: prove the shape on the greenfield system first.

## Decision

The MongoDB Seed Catalog (bc_seed.seed_tables) is destined to retire as the seed store for source-system schema. Its replacement is a Postgres table in the platform DB, following the proven Mongo-to-Postgres pattern already executed for metric seeds (mcf.seed_metric, which still carries mongo_id as the migration fingerprint).

1. NEW SHAPE (proposal — table creation itself is a DBCP requiring explicit operator approval at implementation): source.seed_source_table, sitting beside the catalog it feeds. Columns mirroring the seed document schema and the seed_metric audit pattern: seed_source_table_id uuid PK; system_slug, version_slug, module_code, table_name, display_name, description_text; fields_json jsonb (the per-field array — opaque payload consumed whole by registration Steps 2-3, never queried per-field, matching the seed_metric.raw_json precedent under D162 rule 1); provenance columns source_ref (lgpl-source | instance-extract | vendor-doc), source_hash, instance_identity_text, extracted_at; audit columns imported_at, updated_at, archived_at, status_code, mongo_id (nullable — set only for rows migrated from bc_seed). Unique (system_slug, version_slug, table_name). ≤20 columns, ISO 11179 naming per DEC-69f09e.

2. ODOO IS THE FIRST SYSTEM SEEDED THROUGH THE NEW SHAPE — greenfield, no migration burden, provenance source_ref='instance-extract' from the live pilot instance (Odoo 17 Community + l10n_in; measured 2026-08-05: 86 installed modules, 467 models, 8,895 fields). This satisfies the odoo-erp docket's own precondition ("verified against an exact Odoo release and the target instance's installed-module set") at a provenance grade the LGPL scrape never had.

3. SAP ecc/s4hana (19,506 + 27,415 tables in Mongo today) migrate LATER under one-then-many discipline (D268); Mongo store then freezes read-only and retires at its own gate. During transition, Source Registration reads Postgres for systems present there and Mongo otherwise — per-system source of truth, never a dual-write.

4. D269's rule survives unchanged in meaning: the seed catalog remains the ONLY entry point for tables and fields into Source Registration; only the store moves. Authoring remains script-only; the Postgres path additionally gains what Mongo could never give — the platform's own audit substrate sees the writes.

Onboarding chapters (seed-catalog-management.md, source-registration.md) are annotated with this direction; they continue to describe the Mongo as-built until migration lands.
