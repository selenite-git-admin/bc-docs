---
uid: DEC-e7b1c9
title: "E2E Execution Chain — Issues Found and Permanent Fixes"
description: "Documents 6 blocking issues found during first full E2E proof (500 GL JE records x 4 boundaries x 5 metrics) with root causes and permanent fixes."
status: implemented
subdomain: e2e-runbook
focus: bug-postmortem-record
date: 2026-03-25
project: bc-core
domain: database
refs:
  - type: decision
    label: "D089"
  - type: decision
    label: "D078"
authority: authoritative
migrated_from: legacy v2 archive
---


# E2E Execution Chain — Issues Found and Permanent Fixes

## Context

Documenting these issues prevents the same debugging cycles in future sessions. Each issue took 15-45 minutes to diagnose; with this record, the fix is known in advance.

During the first full E2E proof (500 GL JE records × 4 boundaries × 5 metrics), 6 blocking issues were discovered and fixed. This decision documents the root causes and permanent solutions to prevent recurrence.

## Issue 1: Executor Registration Scope Bubbling (Phase 0.1)

**Symptom:** `onModuleInit` registers executors into a Map, but at request time `Available: []`.
**Root Cause:** NestJS DI scope bubbling — when any dependency in the chain is REQUEST-scoped (e.g., tenant connection), the entire provider tree becomes request-scoped. The Map populated during module init exists on a different instance than the one serving requests.
**Fix:** Created `ExecutorRegistryService` as a standalone global singleton (not part of the scoped provider tree). Executors register via `onModuleInit` into this global service. The resolver reads from it at request time.
**Permanent Rule:** Any service that needs to survive across request scopes must be extracted into a global singleton provider, injected via module `exports` with `@Global()`.

## Issue 2: Database-Per-Tenant Routing (Phase 0.2)

**Symptom:** Queries hit `tbc_selenite` schema in the wrong database.
**Root Cause:** Old code used schema-per-tenant (`SET search_path = tbc_{slug}`) within a single `bc_tenant` database. D089 mandates database-per-tenant — each tenant gets its own database named `tbc_{slug}`.
**Fix:** `TenantConnectionService` creates a per-request Drizzle connection to `tbc_{slug}` database directly. Connection string: `postgres://.../{tbc_slug}`.
**Permanent Rule:** Tenant data always lives in a dedicated database `tbc_{slug}`, never in a shared database with schema isolation. `TENANT_DATA_DB` token resolves to the tenant-specific database.

## Issue 3: MappingBindingRepository Schema Mismatch (Phase 1.3)

**Symptom:** `Failed query: select ... from "master"."mapping_binding"` — table doesn't exist.
**Root Cause:** D078 renamed `master.mapping_binding` → `contract.canonical_mapping` (with column renames: `binding_id` → `canonical_mapping_id`, `binding_name` → `mapping_name`, `binding_status` → `status_code`, `binding_json` → `mapping_json`, etc.). The Drizzle schema in `master/mapping-binding.ts` was never updated. The `registry/index.ts` barrel still re-exported the old schema.
**Fix:** (1) Updated `registry/index.ts` to re-export `canonicalMapping as mappingBinding` from `contract/canonical-mapping.ts`. (2) Rewrote `MappingBindingRepository` to use `canonicalMapping.*` property names.
**Permanent Rule:** After any D078-style table rename, grep all repositories and barrel exports for the old table name. The Drizzle schema file and all consumers must be updated in the same PR. Dead schema files must be deleted.

## Issue 4: Mapping JSON Format Mismatch (Phase 1.3)

**Symptom:** `Cannot read properties of undefined (reading 'filter')` on `body.source_dependencies`.
**Root Cause:** The `canonical_mapping_version.mapping_json` uses format `{ source_bindings, resolution_rules }` but the `CanonicalResolutionService` expects `{ source_dependencies, canonical_mapping, join_context }`. Two schema versions exist — the seed data uses the newer compact format, the service code expects the older verbose format.
**Fix:** Added `normalizeMappingBody()` adapter that translates `source_bindings` → `source_dependencies` with wildcard entity matching (`*`), and generates empty `canonical_mapping` (triggering passthrough mode in the evaluation engine).
**Permanent Rule:** The mapping JSON schema must be versioned (e.g., `$schema: "barecount/mapping/v2"`). The resolution service must check the schema version and dispatch to the correct parser. Never assume a single format.

## Issue 5: Canonical Payload Field Names (Phase 1.3)

**Symptom:** All 500 evaluations rejected: "Required source field 'document_number' is missing".
**Root Cause:** The canonical mapping's `field_contributions` use snake_case canonical names (`document_number`), but the observed payload has CamelCase SAP API names (`AccountingDocument`). The evaluation engine looked for snake_case fields in a CamelCase payload.
**Fix:** For source_bindings format, set `canonical_mapping = []` (empty), which triggers the evaluation engine's passthrough mode — the full observed payload becomes the canonical payload without field renaming.
**Permanent Rule:** Field renaming (source → canonical) belongs at the **observation contract** level (field_map), not at the canonical resolution level. The canonical resolution boundary should receive already-normalized payloads, or explicitly declare the source→canonical mapping with both field names.

## Issue 6: Stale Evaluations Blocking Re-runs (Phase 1.3)

**Symptom:** Second resolve attempt fails with UNIQUE constraint violation on `evaluation.admitted_record_id`.
**Root Cause:** First resolve attempt created 500 rejected evaluations. The UNIQUE constraint on `admitted_record_id` prevents a second evaluation for the same AR. No idempotency handling in the resolve endpoint.
**Fix:** Manually `DELETE FROM boundary.evaluation` before retrying.
**Permanent Rule:** The resolve endpoint must be idempotent — either (a) check for existing evaluations and skip/update, or (b) use `ON CONFLICT DO UPDATE` for upsert semantics. Add a `force: true` option for re-resolution that clears previous evaluations for the run.

## Consequences

N/A
