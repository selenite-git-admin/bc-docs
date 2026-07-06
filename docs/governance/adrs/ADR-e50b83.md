---
uid: DEC-e50b83
title: "Master port reservation — all local dev services"
description: "Fixed port assignments for all dev services: 3000s=frontends, 3100s=APIs, 4000s=dev tools. No port may change without updating this table."
status: implemented
subdomain: port-allocation
focus: dev-port-governance
date: 2026-02-28
project: bc-portal
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Master port reservation — all local dev services

## Context

Port 3000 was shared by 3 frontends causing conflicts. bc-core at 3001 was too close to frontend range. Clean separation: 3000s=frontends, 3100s=APIs, 4000s=dev tools. Eliminates ~30% session time lost to port conflicts and stale processes.

## Decision

Fixed port assignments for all BareCount projects to eliminate conflicts. Frontends: 3000-3099 (bc-portal 3000, Datajettyadminportal 3010, legacy BareCount intra-site 3020). APIs: 3100-3199 (bc-core 3100). Dev tools: 4000-4099 (DevHub 4000, bc-core-dashboard 4100). Databases: PostgreSQL 5434, Redis 6379. All projects must read port from env or config — never hardcode.

## Options Considered

N/A

## Consequences

N/A
