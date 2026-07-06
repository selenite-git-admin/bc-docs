---
uid: DEC-2dab98
title: "Use postgres.js (not pg/node-postgres) as PostgreSQL driver"
description: "postgres.js chosen over node-postgres (pg) as the Drizzle ORM PostgreSQL driver for bc-core"
status: implemented
subdomain: driver-stack
focus: runtime
date: 2026-02-23
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Use postgres.js (not pg/node-postgres) as PostgreSQL driver

## Context

postgres.js is the primary driver recommended by Drizzle ORM docs. Zero dependencies, native TypeScript types (no @types needed), modern Promise-based API, simpler connection pooling. Drizzle team maintains tighter integration with postgres.js. Both support pgSchema() for multi-tenant, but postgres.js integration is more battle-tested in Drizzle ecosystem.

## Decision

Use postgres.js (npm: postgres@3.4.8) as the PostgreSQL driver for Drizzle ORM. Not pg (node-postgres).

## Options Considered

N/A

## Consequences

N/A
