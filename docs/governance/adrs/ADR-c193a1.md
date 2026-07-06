---
uid: DEC-c193a1
title: "Server-Side Onboarding Orchestrator — SSE streaming for all onboarding workflows"
description: "Server-side orchestrator with SSE for all onboarding workflows. Eliminates client-side sequential HTTP overhead. BF/BO: 30 min → 1 min."
status: implemented
date: 2026-04-08T08:10:16.220Z
project: platform
domain: platform
migrated_from: legacy v2 archive
---

# Server-Side Onboarding Orchestrator — SSE streaming for all onboarding workflows

## Context

1. Client-side sequential HTTP calls (5 round-trips per Noun) made BF/BO onboarding take 30+ min for Finance domain. Server-side orchestration eliminates HTTP/auth/serialization overhead per step. 2. SSE streaming gives real-time progress without polling. 3. Pattern is reusable for all onboarding workflows — source registration (register system → verify → create SC → create AC), metric registration (browse seed → create definition → verify → create MC). 4. Server has direct access to all services — no self-HTTP-calls needed.

## Decision

All multi-step onboarding workflows use server-side orchestration with SSE progress streaming. Single HTTP call per operation, all steps execute in-process. Frontend renders SSE events. Applies to: BF/BO onboarding (D295), source system registration, metric registration, and any future multi-step workflow. Pattern: POST /api/onboarding/{workflow}/{target} → SSE stream with per-step progress events.
