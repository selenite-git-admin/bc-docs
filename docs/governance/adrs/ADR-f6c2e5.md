---
uid: DEC-f6c2e5
title: "Global auth guard on bc-core with @Public() exceptions"
description: "Register JwtAuthGuard and RolesGuard as global APP_GUARD. All endpoints protected by default; only @Public() decorator exempts specific routes."
status: implemented
subdomain: nestjs-guards
focus: secure-by-default
date: 2026-02-26
project: bc-core
domain: auth
authority: authoritative
migrated_from: legacy v2 archive
---


# Global auth guard on bc-core with @Public() exceptions

## Context

Secure by default — new endpoints are automatically protected without developer remembering to add guards. Only explicit opt-out via @Public(). Prevents the current situation where all business endpoints (admission, evaluation, metric, action) are unprotected.

## Decision

Register JwtAuthGuard and RolesGuard as global APP_GUARD in NestJS. All endpoints protected by default. Use @Public() decorator to exempt specific routes (health, swagger, login callback).

## Options Considered

N/A

## Consequences

N/A
