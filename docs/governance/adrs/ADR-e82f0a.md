---
uid: DEC-e82f0a
title: "bc-portal AI Assistant — unified drawer replacing help, dual retrieval (catalog + articles)"
description: "bc-portal gets a unified AI assistant drawer that replaces the static help drawer; grounded on catalog+snapshots and help articles via RAG; shares bc-ai backend with bc-admin"
status: implemented
subdomain: bc-portal
focus: ai-assistant
date: 2026-03-29
project: bc-portal
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-portal AI Assistant — unified drawer replacing help, dual retrieval (catalog + articles)

## Context

bc-admin and bc-portal serve fundamentally different users (platform operators vs tenant employees) with different data contexts (catalog definitions vs live snapshots). Keeping UI implementations separate avoids forced abstraction too early. Merging the help drawer eliminates competing RHS panels and elevates help from static browsing to AI-grounded answers. The bc-ai backend is already multi-context capable (context: platform vs tenant). Help article RAG is a one-time indexing task; article maintenance stays editorial.

## Decision

bc-portal will have a dedicated AI assistant drawer that:
1. Replaces the existing static help drawer entirely
2. Uses the shared bc-ai backend (port 4300) with tenant context
3. Has two retrieval sources: catalog_direct (metric definitions + snapshots) and a new help_retriever (RAG over help articles)
4. Haiku intent classifier gains a new query_type: metric_query | help_query | mixed
5. UI component structure mirrors bc-admin drawer (same pattern, separate implementation — no shared package yet)
6. Help articles remain editorially maintained; RAG indexing in bc-ai makes them AI-accessible

## Options Considered

N/A

## Consequences

N/A
