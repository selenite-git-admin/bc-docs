---
uid: DEC-2d5df2
title: "Drop dark mode from bc-portal"
description: "Remove partial .dark block from globals.css. No dark toggle existed; CSS was dormant. Re-enable later after hex migration and design spec finalization."
status: implemented
subdomain: bc-portal
focus: theme-policy
date: 2026-04-18
project: bc-portal
domain: frontend
refs:
  - type: decision
    uid: DEC-142237
    label: "D352 — DS Governance (amended by this)"
migrated_from: legacy v2 archive
---

# D354 — Drop dark mode from bc-portal

## Context

`globals.css` contained a `.dark { ... }` token override block with OKLCH dark-mode values for all 58 CSS variables, along with the Tailwind 4 directive `@custom-variant dark (&:is(.dark *));` that wires the `dark:` class-variant modifier. The infrastructure was installed but **no user-facing dark mode toggle ever shipped** — no code adds the `.dark` class to `document.documentElement` or any ancestor, so the override block was permanently dormant.

Meanwhile, 135 hardcoded hex values across 66 component files (D352 finding) bypass the token system entirely. Any hardcoded hex would display with its light-mode value even if `.dark` were activated, producing a broken hybrid where some elements respect the dark palette and others don't.

Keeping the dormant dark-mode infrastructure:
- Implies a working dark mode exists (it doesn't)
- Doubles the token value maintenance surface (two values per token)
- Complicates the D352 migration argument ("migrate hex for dark mode") when dark mode is not actually a goal today
- Produces dual-value swatches in the DS Blueprint that will never match reality

D352 Rule 3 ("Dark mode readiness") is amended by this decision.

## Decision

1. **Remove the `.dark { ... }` block** from `apps/web/src/styles/globals.css` (34 lines, all OKLCH overrides).
2. **Remove the `@custom-variant dark (&:is(.dark *));` directive** at the top of globals.css.
3. **Retain shadcn/ui `dark:` Tailwind variants** inside primitive components in `src/components/ui/*` — these are upstream shadcn patterns that become no-ops without the custom-variant directive. Leaving them simplifies future shadcn upgrades.
4. **Retain OKLCH values in `:root`** (e.g., `--foreground: oklch(0.145 0 0)`) for colors that were always OKLCH — they still work in light mode.
5. **Token values in `:root`** become the sole source of truth. No dual-value maintenance.

### Re-enablement path (future)

If dark mode is a product goal later:

1. Complete 135 hex → token migration (eliminates the partial-state risk).
2. Design spec finalizes dark palette (explicit OKLCH values per token).
3. Restore the `.dark` block with the new palette.
4. Restore `@custom-variant dark (&:is(.dark *));`.
5. Add theme toggle component + state (localStorage or user preference) to add/remove `.dark` class on `<html>`.
6. Audit all components for dark-mode regressions (shadcn `dark:` variants start firing again).

This is a real-scope initiative, not a cleanup task. Tracked as future work when prioritized.

## Options Considered

### Option A: Drop entirely, restore later (chosen)

Clean state today. Re-enable as a scoped initiative with real design buy-in.

### Option B: Keep the infrastructure, add a toggle (rejected)

Would require migrating 135 hex values first, defining dark palette, and full visual QA. Too much for a cleanup pass; wrong time.

### Option C: Keep the `.dark` block but remove `@custom-variant` (rejected)

Half-measure. The CSS would sit unused. No maintenance win.

### Option D: Leave as-is (rejected)

Perpetuates the illusion of dark mode support and keeps the 135-hex migration argument misaligned.

## Consequences

### Positive

- **Honest state** — docs and code match reality.
- **Simpler token maintenance** — one value per token.
- **DS Blueprint accurate** — swatches show actual rendered colors.
- **D352 hex migration argument simplifies** to governance/consistency, not dark-mode readiness.
- **No functional change** for any user — dark mode was never visible.

### Negative

- **Future dark mode requires full migration** again (palette + toggle + QA).
- **Shadcn `dark:` variants remain** in `ui/` components — minor noise in code, but harmless.

### Risks

- **Later re-enablement is more expensive** than toggling — but that's the honest cost of doing dark mode right.
- **New developers may add `dark:` classes** habitually. Mitigation: update D352 SOP to clarify dark mode is out of scope.

## Amendments to D352

D352 Section "Rule 3 — Dark mode readiness" is superseded by this ADR. The other D352 rules (canonical sources, registry enforcement, hex ban) remain in force.

## Implementation Status

Completed in SES-92dc4e (2026-04-18):
- ✅ `@custom-variant dark` directive removed from globals.css
- ✅ `.dark { ... }` block removed from globals.css
- ✅ D354 recorded (this ADR)
- ✅ D352 Rule 3 noted as superseded
