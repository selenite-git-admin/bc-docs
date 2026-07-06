---
uid: DEC-8e857a
title: "Design-system screen consolidation: 42 individual demos → 13 section pages"
description: "Consolidated 42 individual design-system demo routes into 13 section-level pages matching /design-system-* route structure."
status: implemented
subdomain: bc-portal
focus: design-system-routes
date: 2026-02-26
project: bc-portal
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# Design-system screen consolidation: 42 individual demos → 13 section pages

## Context

bc-portal Phase 3+5 restructure removed individual demo routes and replaced them with consolidated section pages (e.g. /design-system-core-components contains buttons, badges, tooltips). Registry must match actual routes.

## Decision

Consolidated 42 individual design-system demo screens (e.g. /button-demo, /cards-demo) into 13 section-level screens matching the new /design-system-* route structure. Old individual routes no longer exist in bc-portal AppRouter.

## Options Considered

N/A

## Consequences

N/A
