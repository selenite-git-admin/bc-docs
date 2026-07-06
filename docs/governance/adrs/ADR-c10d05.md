---
uid: DEC-c10d05
title: "bc-core Base Refactoring — Build, Type Safety, Error Handling, Module Structure"
description: "6-phase bc-core refactoring: build config, SQL injection, error handling, repository decomposition, orchestrator resilience, module structure"
status: decided
date: 2026-04-08T11:48:51.275Z
project: bc-core
domain: platform
migrated_from: legacy v2 archive
---

# bc-core Base Refactoring — Build, Type Safety, Error Handling, Module Structure

## Context

Recurring session failures traced to: stale build artifacts (deleteOutDir:false), silent error swallowing (8 empty catches), SQL injection vectors (string interpolation in raw SQL), 1,705-line god repository, best-effort orchestrator with no failure classification. Cross-model audit (Gemini) provided fresh perspective on root causes Claude had been working around.

## Decision

6-phase refactoring of bc-core addressing systemic issues identified by cross-model audit (Gemini CLI + Claude verification). Phase 1: deleteOutDir fix + schema cleanup + vitest config. Phase 2: SQL injection hardening in contract.repository.ts. Phase 3: Empty catch visibility. Phase 4: contract.repository.ts decomposition (1,705→6 files). Phase 5: Orchestrator resilience + bulk operation consistency. Phase 6: Module rename + seed decomposition.
