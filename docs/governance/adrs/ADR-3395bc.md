---
uid: DEC-3395bc
title: "v3 docs reader: drop book wrapper, drop mkdocs, flat sections under docs/"
description: "Restructure bc-docs-v3 to drop the book metaphor, the mkdocs scaffolding, and chapter-numbered filenames; manifest schema renamed accordingly"
status: decided
date: 2026-04-25T02:49:04.327Z
project: bc-docs
domain: docs
subdomain: reader-architecture
focus: paths
---

# v3 docs reader: drop book wrapper, drop mkdocs, flat sections under docs/

## Context

Three issues drove this refactor. First, mkdocs.yml had never rendered anything; the bc-admin embedded reader (governed by DEC-b97390) is the only canonical renderer. A second nominal renderer that nobody honors is dead weight that fakes optionality. Second, the "book" metaphor was scaffolding to enforce linear narrative discipline during the v2→v3 reset; with 13 chapters drafted and the voice locked, the metaphor adds vocabulary churn ("book", "Part N", "Appendix") without reinforcing any new constraint. The structure is documentation. Third, the `book/` and `appendices/` wrappers placed assets and tooling as confusing peers to chapter content; consolidating everything content-related under `docs/` distinguishes prose from tooling cleanly. Dropping `ch-NN-` filename prefixes makes the frontmatter `order` field load-bearing rather than cosmetic, and removes a numbering convention that outline §2.14 had already abolished in chapter titles and headings. The amendment of DEC-b97390 is in path/schema only; the reader's existence, governance, and behavior contract are unchanged.

## Decision

bc-docs-v3 adopts a flat documentation layout: orientation files (README, HANDOFF, outline) at repo root, all content under `docs/` (sections, reference, assets), tooling under `scripts/`. The mkdocs setup (`mkdocs.yml`, `docs/index.md` stub) is deleted; the bc-admin embedded reader (DEC-b97390) is the single canonical renderer. Chapter filenames drop the `ch-NN-` prefix and use slugs only (`the-problem.md`, `the-solution.md`); chapter ids match the slug. Diagram filenames drop the `DG-ch{NN}-` prefix and use `DG-{slug}.svg`. Frontmatter `order` becomes the authoritative sort key for chapters within a section. The `appendices/` folder is renamed `docs/reference/`; the manifest renames `parts[]` to `sections[]` and `appendices[]` to `references[]`, and `manifest.book` to `manifest.docs`. The bc-admin reader routes change from `/docs/part/:partSlug/...` and `/docs/appendix/:appendixSlug/...` to `/docs/section/:sectionSlug/...` and `/docs/reference/:referenceSlug/...`. Reader URL for assets becomes `/docs/assets/diagrams/DG-{slug}.svg`. The `migration-manifest.md` (146KB v2 archaeology) is deleted. Existing ADRs in `docs/reference/adrs/` are not edited; their historical references to "book" and "Appendix" remain as evidence of the journey.
