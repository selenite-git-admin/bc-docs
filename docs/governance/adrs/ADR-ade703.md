---
uid: DEC-ade703
title: "Drop monorepo — single-project NestJS for bc-core"
description: "Monorepo → single-project NestJS. Inline types, flatten structure, fix build config with guardrails."
status: implemented
date: 2026-04-09T02:16:08.724Z
project: bc-core
domain: infrastructure
migrated_from: legacy v2 archive
---

# Drop monorepo — single-project NestJS for bc-core

## Context

The monorepo structure (apps/api + packages/types) was the root cause of recurring SWC/dist/path issues across 8+ sessions (SES-54dd54 through SES-3a323b). NestJS docs explicitly warn against using direct SWC builder in monorepo mode. The entryFile misconfiguration (api/src/main vs main) created nested dist/api/src/ output. deleteOutDir fix was applied and reverted within 2 commits because it broke SWC watch mode on Windows. pm2 was disabled entirely as a workaround. packages/types had only 7 type files with zero runtime dependencies, consumed only by apps/api — no cross-repo sharing justified the monorepo overhead. Single-project eliminates the entire class of monorepo+SWC incompatibilities and enables clean Docker/Fargate deployment path.

## Decision

bc-core is restructured from an npm workspace monorepo (apps/api + packages/types) to a standard single-project NestJS application. The packages/types package (7 type-only files) is inlined into src/types/. The apps/api/ directory is flattened to the project root. Build config is rewritten for single-project mode with SWC, explicit .swcrc, and build guardrails (prebuild config validation + postbuild output validation).
