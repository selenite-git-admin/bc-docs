---
uid: DEC-2f406b
title: "D230 Addendum — Dossier ID scheme, frontmatter, diagrams, awesome-pages"
description: "5 D230 refinements from Phase 3a: readable IDs, 4-field frontmatter, parent field, inline mermaid, awesome-pages"
status: implemented
subdomain: documentation
focus: dossier-conventions
date: 2026-03-30
project: bc-docs
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# D230 Addendum — Dossier ID scheme, frontmatter, diagrams, awesome-pages

## Context

Based on Phase 3a authoring experience: hex IDs are unreadable in 100+ file dossiers, verbose frontmatter creates inconsistency across agents, separate diagram files add nav overhead, explicit mkdocs nav doesn't scale beyond 1 module.

## Decision

5 refinements to D230 based on Phase 3a authoring experience:

1. **Readable ID scheme** — Dossier IDs use `DOS-{component}-{section}` (e.g., DOS-sc0001-03) instead of D230's hex UIDs. Hex UIDs reserved for DevHub entities. Rationale: documentation is a human navigation problem; readability > collision avoidance.

2. **Minimal frontmatter** — Section files have 4 required fields only: id, slug, section, parent. Rich fields (refs, authored_by, last_validated) are optional and added as content matures. Component index files keep richer frontmatter (xref, status, completeness).

3. **Parent field replaces component+module** — `parent: DOS-sc0001` is cleaner than separate component + module fields. Component and module are derivable from parent's frontmatter.

4. **Inline mermaid diagrams** — ERDs in Section 03, flow diagrams in Section 02. No separate diagrams/ directories. Every component gets both diagram types.

5. **awesome-pages plugin** — mkdocs.yml uses top-level nav only. Per-directory .pages files control ordering within modules and components. Prevents 800+ line nav explosion.

## Options Considered

N/A

## Consequences

N/A
