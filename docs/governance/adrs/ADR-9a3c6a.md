---
uid: DEC-9a3c6a
title: "bc-portal Design System governance"
description: "Declare the canonical DS source (shadcn/ui + globals.css + DesignSystemBlueprint + ComponentRegistry), add ESLint rule banning arbitrary hex, require ComponentRegistry registration for new components."
status: implemented
subdomain: bc-portal
focus: design-system-governance
date: 2026-04-18
project: bc-portal
domain: platform
code: D356
refs:
  - type: document
    path: "dev-guides/bc-portal/design-system-inventory.md"
    label: "DS inventory (source finding — 4 layers, 323 hex violations)"
  - type: decision
    uid: DEC-04dade
    label: "D355 — bc-portal architecture & patterns (companion)"
  - type: document
    path: "playbooks/design-system-contribution-sop.md"
    label: "DS contribution SOP (operational)"
migrated_from: legacy v2 archive
---

# bc-portal Design System governance (D356)

## Context

The 2026-04-18 DS archaeology discovered four coexisting design system traces in bc-portal:

1. **shadcn/ui primitives** — 47 files in `components/ui/`, unmodified upstream
2. **CSS variable tokens** — 58 color variables + spacing/radius/typography in `styles/globals.css`
3. **Hardcoded semantic colors** — 323 hex values in 66 files bypassing tokens
4. **ComponentRegistry** — 1,064-line catalog of 68 components (understates the ~140 actual)

Plus a Design System page at `/design-system` (`DesignSystemBlueprint.tsx`) that consolidated 40+ previous library pages into 15 section components — a living style guide.

The user confirmed this mess exists ("multiple versions/traces") and asked for ONE canonical source to be declared and enforced. Layers 1, 2, and 4 are keepers. Layer 3 is the bleed to stop.

## Decision

### Canonical DS Stack

| Role | Authoritative location |
|------|-----------------------|
| **Primitives** | `components/ui/` — shadcn/ui, unmodified. Bump only on shadcn upgrade. No forks. |
| **Tokens** | `styles/globals.css` — `:root` and `.dark` blocks, exposed to Tailwind via `@theme inline` |
| **Reference documentation** | `pages/design-system/DesignSystemBlueprint.tsx` (route: `/design-system`) — 15 section components demonstrating tokens + components live |
| **Governance registry** | `components/design-system/ComponentRegistry.ts` — catalog of components above the `ui/` layer |

### Rules

**R1: Tokens, not hex.**
Any color usable by the business (primary, status, chart series, etc.) must be a CSS variable token with BOTH a `:root` and `.dark` definition. Arbitrary Tailwind hex values in className are banned.

**R2: ESLint rule enforces R1.**
`no-restricted-syntax` rule in `eslint.config.js` flags any `Literal` or `TemplateElement` matching `(bg|text|from|to|via|border|fill|stroke|ring|outline|shadow|accent|caret|decoration|placeholder|divide)-[#hex]`. Severity: `warn` during migration. 135 grandfathered violations exist as of 2026-04-18.

**R3: DesignSystemBlueprint is exempt.**
`src/pages/design-system/**` and `src/components/design-system/**` are exempt from R2 — they demonstrate patterns intentionally.

**R4: New components above `ui/` must register.**
Any new component in `components/common/`, `components/cards/`, `components/charts/`, `components/widgets/`, etc. must get an entry in `ComponentRegistry.ts` with: id, componentId, name, path, category, version, useCases. Component file must have a JSDoc `@designSystem` block.

**R5: shadcn/ui is inviolate.**
No custom logic, variants, or modifications inside `components/ui/`. Override behavior in a wrapping component in `components/common/`.

**R6: Token naming is semantic.**
`--status-positive` not `--green-500`. `--surface-elevated` not `--light-gray`. Design intent over visual appearance.

**R7: New tokens require light + dark + theme exposure.**
Skipping dark mode or the `@theme inline` block is a blocker.

**R8: Deprecated components stay in the repo** with `isDeprecated: true` in ComponentRegistry and a `console.warn` in dev mode. Deletion happens in a separate sprint once all call sites migrate.

### Migration stance

Opportunistic (not big-bang). New code follows these rules. Existing violations are:

- **135 hex-class violations** → migrate as the component is touched. Track via a `ds-migration` DevHub tag.
- **~72 unregistered components** → register as touched. No deadline.
- **Old-terminology components** (GoldenData, DataControls) → handled under D357 naming convention.

The grandfathered count must not grow. Code review references the lint output and rejects PRs that add new D356-R1 violations.

### Token section in DesignSystemBlueprint

The existing `ColorsSection.tsx` shows gradient previews and a small CSS Token Reference block. This is acceptable but should be expanded to include a full token swatch grid (all 58 variables) in both light and dark mode. Tracked as followup; not blocking this ADR.

## Options Considered

### Option A: shadcn/ui + globals.css + Blueprint + Registry as canonical (CHOSEN)

Keep what exists, declare it authoritative, add the lint rule, enforce via SOP.

**Why chosen:** The foundation is solid. The bleed is only hex usage. This option captures that intent with minimum new infrastructure.

### Option B: TypeScript color constants in `src/theme/colors.ts`

Centralize all colors as typed TS constants (`colors.primary`, `colors.statusPositive`). Import from everywhere.

**Rejected:** Weaker than CSS variables because it can't power dark mode toggling through the cascade. Tooling (Tailwind) expects CSS var tokens.

### Option C: Full rewrite to Tailwind v4 design tokens format

Migrate to Tailwind 4's native theme syntax (no `:root` — use `@theme` blocks directly).

**Rejected:** Globals.css already uses `@theme inline` which is the v4 pattern. The hybrid with `:root` is intentional to enable dark mode class-based switching. Rewrite is cosmetic.

## Consequences

### Positive

- Single canonical DS source — end of "which button variant do I use?"
- ESLint rule blocks new violations automatically at commit time
- Dark mode will work correctly on new code (existing hardcoded hex won't adapt, but migration will fix as touched)
- ComponentRegistry becomes the authoritative component catalog as new components register

### Negative

- 135 lint warnings visible on every lint run during migration
- ComponentRegistry is 68/~140 — registry gap will persist until caught up
- New-component JSDoc blocks add overhead per component

### Risks

- **Risk:** Developer bypasses the ESLint rule with `// eslint-disable-next-line` for convenience.
  **Mitigation:** Require justification comment. Review checks for justifications.
- **Risk:** ComponentRegistry falls further behind as components are added without registration.
  **Mitigation:** SOP step 3 in `design-system-contribution-sop.md` is explicit. PR review includes registry check.
- **Risk:** Token explosion — too many `--status-*` / `--surface-*` / etc. variants.
  **Mitigation:** DS lead reviews token additions. If 2+ callers don't exist, keep it local.

## Migration status

| Concern | Audit baseline | Status |
|---------|---------------|--------|
| Canonical stack declared | Ambiguous | Declared |
| ESLint hex rule | None | Active (warn) |
| Grandfathered violations | 135 | Tracked baseline |
| ComponentRegistry coverage | 68 / ~140 | Ongoing |
| Token section in Blueprint | Present, sparse | Expansion deferred |
| SOP published | None | `design-system-contribution-sop.md` |

## Enforcement

- **ESLint** — CI fails on any NEW D356-R1 violation (baseline = 135)
- **Review checklist** in `bc-portal-feature-sop.md` Step 10
- **Registry audit** — quarterly scan to count registered vs actual, keep gap closing
- **Audit re-run** at 6-month intervals
