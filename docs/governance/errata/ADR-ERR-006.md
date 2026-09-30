---
id: ADR-ERR-006
title: "DEC-a4e550 names a decision-file path that no longer exists"
status: adopted
authority: authoritative
affected: DEC-a4e550 (D221) — Decision, the sentence "All decisions are stored as markdown files in bc-docs/architecture/decisions/DEC-xxxxxx.md"
resolution: correction recorded here; the decision stands; ADR files live at docs/governance/adrs/ADR-{uid}.md under the DEC-3395bc layout, and the DevHub allocator writes them there
opened: 2026-09-30
---

# ADR-ERR-006 — DEC-a4e550 names a decision-file path that no longer exists

## Contradiction summary

DEC-a4e550 (Documentation Registry in DevHub and the standard ADR file format, `implemented`, 2026-03-26) says: "All decisions are stored as markdown files in `bc-docs/architecture/decisions/DEC-xxxxxx.md`". Verified on 2026-09-30 at bc-docs main `aa5b743`: no such directory exists. Every ADR file lives at `docs/governance/adrs/ADR-{uid}.md`, the layout DEC-3395bc fixed (governance peers `adrs` and `errata` beside the section folders), and the DevHub decision route writes new files to that path (barecount-devhub `src/routes/decisions.js`, the `adrDir` resolved from the documentation registry's `decisions` section).

## Implementation behavior

The allocator, the auditor (`scripts/docs-control/audit_adrs.py`), the registry generator and every cross-reference in the documentation use `docs/governance/adrs/`. The old path appears only in this ADR's text and in a handful of pre-migration chapters that the documentation integrity register lists.

## Resolution state

**Adopted as a correction; DEC-a4e550 is not rewritten.** Its decision (ADR files are the truth, DevHub holds metadata, one standard file format) stands. Readers substitute the current path.

## References

- DEC-a4e550 — Documentation Registry in DevHub and the standard ADR file format
- DEC-3395bc — the bc-docs layout
- `docs/development/the-authority-model.md`, "Recording a new decision" (step 4: the system writes the ADR at the canonical path)
