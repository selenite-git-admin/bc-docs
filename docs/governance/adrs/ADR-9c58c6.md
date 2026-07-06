---
uid: DEC-9c58c6
title: "Article-drop refinement: 'The Operating Model' → 'Operating Model' in label positions"
description: "Refinement to DEC-ce6e2b. Drops the definite article from the section's canonical name to remove asymmetry in the six-section spine."
status: decided
date: 2026-04-25T14:12:26.776Z
project: bc-docs
domain: docs
subdomain: structure
focus: section-naming
---

# Article-drop refinement: 'The Operating Model' → 'Operating Model' in label positions

## Context

After the section rename DEC-ce6e2b ("The Runtime" → "The Operating Model") and the third-section rename DEC-376587 ("The Platform" → "Implementation"), the spine reads Foundation, The Operating Model, Implementation, Governed Authoring, Platform Operations, Compliance. Only one section carries a definite article, which the founder flagged as visual asymmetry in the LHS panel. Dropping "The" treats "Operating Model" as a proper noun in the same register as Foundation, Implementation, Compliance. The reading "Operating Model" is grammatically defensible: compound proper-noun phrases like "Operating System", "Information Architecture", "Trust Surface" function as bare names in label contexts and take a lowercase article inline only when grammar requires it. The articleless form aligns the section's surface treatment with how Foundation is treated throughout the documentation. Founder authorized minimum scope (sidebar + title) but the refinement extends to all label positions to prevent residual asymmetry where, say, the sidebar says "Operating Model" but a HANDOFF section listing or outline table row still says "The Operating Model". Body prose inline references receive a mechanical case fix (capital-T mid-sentence becomes lowercase-t article + capitalized name) so grammar stays natural without making "Operating Model" feel stilted as a bare proper noun in inline use. Refinement to DEC-ce6e2b; does not supersede or reverse the original rename, only adjusts the surface form of the canonical name.

## Decision

The Operating Model section's canonical name drops the definite article and is now "Operating Model" (no "The"). The change applies to all label positions: sidebar/panel rendered by bc-admin, chapter title in frontmatter and H1, outline section heading and chapter-row labels, section listings in HANDOFF / README / outline. In body prose mid-sentence the lowercase article "the Operating Model" appears when grammar requires it, the same way one writes "the Foundation chapter" or "the United States" — the article is grammatical, not part of the formal name. Sentence-start references like "The Operating Model in this documentation describes..." retain the capital "T" only as start-of-sentence article, not as part of the name. Section folder name `docs/operating-model/` and file slugs are unchanged (already article-free).
