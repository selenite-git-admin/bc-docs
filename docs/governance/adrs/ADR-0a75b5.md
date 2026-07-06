---
uid: DEC-0a75b5
title: "Registry schema circular import fix — pg-schema.ts extraction"
description: "Extract registrySchema to dedicated pg-schema.ts leaf file to break barrel re-export circular dependency. Fixed 14 test failures."
status: implemented
subdomain: schema-organization
focus: circular-import-prevention
date: 2026-02-27
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Registry schema circular import fix — pg-schema.ts extraction

## Context

When index.ts re-exports from table files and table files import registrySchema from index.ts, Vitest resolves the circular dependency differently than runtime Node.js, causing registrySchema to be undefined in tests. Extracting to a leaf file with no imports breaks the cycle. Fixed 14 test failures.

## Decision

Extract registrySchema (pgSchema('registry')) to a dedicated pg-schema.ts file. All table definition files import from ./pg-schema instead of ./index to prevent circular imports through barrel re-exports.

## Options Considered

N/A

## Consequences

N/A
