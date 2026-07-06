---
uid: DEC-8cbae7
decision_code: D349
title: "bc-portal Design System Governance — canonical source, token rule, component registry"
description: "Declares shadcn/ui + globals.css as the canonical DS, bans arbitrary hex in className, requires ComponentRegistry for all non-primitive components"
status: superseded
superseded_by: DEC-9a3c6a
subdomain: bc-portal
focus: design-system-governance
date: 2026-04-18
project: bc-portal
domain: frontend
refs:
  - type: document
    path: "dev-guides/bc-portal/design-system-inventory.md"
    label: "DS Inventory (4-layer map)"
  - type: document
    path: "dev-guides/bc-portal/audit-report-2026-04-18.md"
    label: "bc-portal Audit Report 2026-04-18"
migrated_from: legacy v2 archive
---

# bc-portal Design System Governance (D349)

## Context

bc-portal accumulated four coexisting DS layers organically:
1. shadcn/ui primitives (`components/ui/`, 47 files)
2. CSS variable tokens (`styles/globals.css`, 58 variables)
3. Hardcoded gradient/status hex colors (323 occurrences, 66 files)
4. ComponentRegistry governance catalog (68 entries vs ~140 actual)

The existing `DesignSystemBlueprint.tsx` page (`/design-system`) is a well-structured living style guide with 15 sections replacing 40+ retired library pages. It was missing a full token reference — closed April 2026 (live TokenSwatch components now render all 58 CSS variables directly from globals.css).

No rule prevented new hardcoded hex values. Without enforcement the 323-count grows each sprint and dark mode becomes unimplementable.

## Decision

### Canonical DS Source

| Layer | Source | Authority |
|-------|--------|-----------|
| Primitives | `components/ui/` (shadcn/ui, unmodified) | shadcn/ui upstream |
| Tokens | `styles/globals.css` (`:root` CSS variables) | This file only |
| Reference | `DesignSystemBlueprint.tsx` at `/design-system` | Living style guide |
| Catalog | `design-system/ComponentRegistry.ts` | Manual, maintained by authors |

### Rules

**Rule 1 — Token-first colors.** All color values in JSX className or style props must reference a CSS variable from `globals.css`. Arbitrary hex in Tailwind arbitrary values (`bg-[#A25BFF]`, `text-[#7263FF]`, `from-[#A25BFF]`) are prohibited. Exception: add `// ds-approved: no-token` inline comment with justification.

**Rule 2 — ComponentRegistry required.** Every component above the `ui/` primitive layer must be registered in `ComponentRegistry.ts` before merging. Required fields: `id`, `name`, `path`, `category`, `version`.

**Rule 3 — shadcn/ui unmodified.** No business logic in `components/ui/`. Wrap in `components/common/` instead.

**Rule 4 — DesignSystemBlueprint as documentation target.** New tokens added to `globals.css` appear automatically in ColorsSection via live TokenSwatch rendering. New component categories need a section in DesignSystemBlueprint.

### Grandfathered Escape Hatches

Documented in `ColorsSection.tsx` with amber "pending migration" badges:
- **Gradient colors** — `from-[#A25BFF] via-[#7263FF] to-[#5972FF]` on buttons/badges → pending `--gradient-primary-*` tokens
- **Status colors** — `#10B981`, `#F59E0B`, `#EF4444` → pending `--status-positive/warning/negative` tokens

## Options Considered

### Option A: Token-first with lint enforcement (chosen)
Stops bleeding immediately. Migration is one component at a time, low-risk.

### Option B: TypeScript color constants file (rejected)
Less powerful — no dark mode toggle, no Tailwind utility integration, not native to CSS variable system.

### Option C: Status quo + documentation (rejected)
Without a lint rule the 323-count grows. Dark mode becomes impossible.

## Consequences

- ESLint rule needed to ban arbitrary hex in className — DevHub task TSK-42e6ee
- ComponentRegistry needs ~72 new entries — captured in TSK-4b7cb8
- Gradient/status token migration is later, not blocking
- `DesignSystemBlueprint.tsx` is mandatory reference before implementing any new component pattern
