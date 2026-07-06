---
uid: DEC-ab0b7c
title: "bc-admin stack: React 18 + Vite + Radix UI + TailwindCSS v4 (same as bc-portal)"
description: "bc-admin mirrors bc-portal stack: React 18, Vite, Radix UI, TailwindCSS v4. One stack across both frontends."
status: implemented
subdomain: bc-admin
focus: tech-stack
date: 2026-02-28
project: bc-admin
domain: frontend
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-admin stack: React 18 + Vite + Radix UI + TailwindCSS v4 (same as bc-portal)

## Context

Consistency across frontends. Same Cognito auth, same component primitives, same design tokens. Platform team and customer team share one visual language. Reduces cognitive overhead when switching between portals.

## Decision

bc-admin uses identical stack to bc-portal: React 18, TypeScript, Vite + SWC, Radix UI, TailwindCSS v4 (oklch tokens), TanStack Query v5, amazon-cognito-identity-js, Lucide React icons. Design system copied from bc-portal as foundation.

## Options Considered

N/A

## Consequences

N/A
