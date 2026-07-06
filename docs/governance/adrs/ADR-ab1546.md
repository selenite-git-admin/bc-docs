---
uid: DEC-ab1546
title: "Shared types via @barecount/types npm package"
description: "Cross-project TypeScript types published as @barecount/types on CodeArtifact. Single source of truth for shared interfaces."
status: reversed
subdomain: type-sharing-strategy
focus: cross-repo-types
date: 2026-02-23
project: bc-portal
domain: subscription
authority: authoritative
migrated_from: legacy v2 archive
---


# Shared types via @barecount/types npm package

## Context

User chose shared npm package approach. Guarantees type sync between frontend and backend. Prevents drift that manual copying would cause. The @barecount/types package will contain API contracts (request/response envelopes), entity interfaces, and shared enums.

## Decision

Shared TypeScript types between bc-portal (React frontend) and bc-core (NestJS backend) will be managed via a @barecount/types package. This ensures type conformance across repos without manual copying. The types package will be a third package — can live inside bc-core as a monorepo workspace or as a standalone repo.

## Options Considered

N/A

## Consequences

N/A
