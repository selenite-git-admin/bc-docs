---
uid: DEC-a5df75
title: "Contract Registry — separate service vs API monolith"
description: "Contract registry stays inside bc-core as NestJS modules, not a separate microservice. Monolith-first approach."
status: superseded
superseded_by: DEC-856d61
date: 2026-03-02
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Contract Registry — separate service vs API monolith

## Context

DECIDED: Keep monolith for now. The code is already cleanly modular (RegistryModule vs BoundaryModule), making future extraction straightforward when needed. Split when: (a) separate teams own registry vs data plane, (b) uptime SLAs diverge, or (c) registry query load impacts runtime admission. Current architecture supports this split without refactoring — it's a deployment decision, not a code decision.

## Decision

Should the Contract Registry be split into its own service, separate from bc-core API? In production, both are critical components — API handles runtime boundary operations, Registry handles schema governance. Isolation would prevent a registry outage from affecting data admission and vice versa.

## Options Considered

N/A

## Consequences

N/A
