---
uid: DEC-ace519
title: "Tech stack: Node.js + TypeScript + PostgreSQL + Fastify + Drizzle"
description: "bc-sdg uses Node.js + TypeScript + PostgreSQL + Fastify + Drizzle ORM. Same DB patterns as bc-core."
status: implemented
subdomain: tech-stack
focus: bc-sdg-fastify-drizzle
date: 2026-03-02
project: bc-sdg
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Tech stack: Node.js + TypeScript + PostgreSQL + Fastify + Drizzle

## Context

Must handle 60M+ records across 6 profiles. PostgreSQL handles this without strain. SQLite would choke on concurrent reads (OData serving) + writes (daily generation). Same stack as bc-core means one team, one language, shared patterns. Fastify chosen over Express for throughput on the OData serving layer.

## Decision

bc-sdg uses Node.js + TypeScript (same as bc-core), PostgreSQL for persistent state (separate bc_sdg database on same Docker instance), Fastify for OData server (2-3x faster than Express, schema validation built-in), Drizzle ORM for type-safe queries and batch inserts. Worker threads for parallel generation across modules. Month-by-month streaming generation — never hold 18 months in memory. Same language/stack as bc-core for team maintainability.

## Options Considered

N/A

## Consequences

N/A
