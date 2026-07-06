---
uid: DEC-b79d16
title: "Source docs at bc-docs/sources/ (root level, not architecture/)"
description: "Source system documentation lives at bc-docs/sources/ root level, not nested under architecture/. Flat discovery."
status: implemented
subdomain: documentation-structure
focus: source-knowledge-base-layout
date: 2026-03-07
project: bc-core
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# Source docs at bc-docs/sources/ (root level, not architecture/)

## Context

Source onboarding docs cover external system knowledge (SAP licensing, Salesforce API models, Tally ODBC) which is not BareCount architecture. architecture/ is reserved for internal platform design (source catalog, connector ecosystem, data admission modules). Separating them prevents architecture/ from becoming a catch-all and gives sources/ room to grow into a comprehensive external system knowledge base.

## Decision

Per-source knowledge base (onboarding guides, licensing analysis, reference archives) lives at bc-docs/sources/ as an independent root-level folder, not under architecture/. Rationale: architecture/ describes how BareCount is built (internal platform design). sources/ describes external systems BareCount connects to — their licensing, APIs, data models. These are distinct concerns. sources/ can grow beyond onboarding to include integration patterns, compatibility matrices, and source-specific technical references.

## Options Considered

N/A

## Consequences

N/A
