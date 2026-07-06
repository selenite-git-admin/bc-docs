---
uid: DEC-ce6e2b
title: "Section rename: The Runtime → The Operating Model"
description: "Rename second top-level section to better describe its 17-chapter scope (operating spec, not pure execution)."
status: decided
date: 2026-04-25T13:27:39.975Z
project: bc-docs
domain: docs
subdomain: structure
focus: section-naming
---

# Section rename: The Runtime → The Operating Model

## Context

"The Runtime" undersells the section's actual contents. The 17 chapters split into roughly five categories — catalog and inventory (Sources and the Catalog, Business Vocabulary, Metric Catalog), composition rules (Contract Chain Assembly, Quality Gates and Chain Integrity), execution acts (Connectors and Readers, Admission and Observation, Canonical Evaluation, Metric Evaluation, Action Evaluation), proof emission (Evidence and Lineage), and tenancy frame (Tenancy and Binding, Tenant Extensions and Overrides, Tenant Entitlement Enforcement, Fiscal Time and Temporal Gates, Chain Completeness and Verdict). Only ~5 of 17 are pure execution. "Runtime" in computer-science usage connotes execution narrowly and is structurally narrower than the section contents. "The Operating Model" is the established architectural term for a layer that describes how a system delivers value: artifacts, composition rules, acts, proof, and governance frame. It captures both static structure and dynamic behavior. Foundation gives the laws; The Operating Model gives the embodied operating spec; The Platform gives the implementation. Three viable alternatives were considered and rejected: keep "The Runtime" with broader Overview framing (leaves the dissonance), "The Working Model" (carries prototype connotation in scientific contexts), "BareCount Model" (asymmetric in a six-section spine — only one section would carry the brand — and not self-describing). A faint collision with "Platform Operations" was discussed and accepted: the two terms differ grammatically (operating-as-adjective vs. operations-as-plural-noun) and conceptually (spec vs. activity); the Operating Model: Overview chapter Boundaries-with-Other-Sections subsection distinguishes them. This rename is the first formal section-rename ADR. The earlier informal rename (The Operating System → The Runtime, recorded only in HANDOFF decision 13) was not ADR-tracked.

## Decision

The second top-level section of bc-docs-v3 is renamed from "The Runtime" to "The Operating Model". The section folder moves from `docs/runtime/` to `docs/operating-model/`. The section opener title becomes "The Operating Model: Overview". Cross-references in chapter prose are updated to "the Operating Model" or "The Operating Model" as the new canonical name. Frontmatter `section:` fields and bc-admin sync-docs SECTION_LABELS are updated accordingly. The contract-execution-runtime scope clarification (HANDOFF decision 16) is preserved by the section opener; the rename does not broaden the section's authoritative scope.
