---
uid: DEC-afdb59
title: "BareCount Component Architecture Diagram — canonical reference"
description: "Official component architecture diagram showing all BareCount modules and their relationships. Canonical visual reference."
status: implemented
subdomain: architecture-docs
focus: canonical-diagram
date: 2026-03-06
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# BareCount Component Architecture Diagram — canonical reference

## Context

User explicitly requested a component/block diagram (not data flow). Foundation v2 corrections were applied directly to specification files (3641d59) before the diagram was drawn, ensuring accuracy. Draw.io chosen over Excalidraw/Figma for editability and version control (XML diffs cleanly).

## Decision

The canonical component architecture diagram for BareCount is maintained as a draw.io file at bc-docs/architecture/barecount-component-architecture.drawio. It reflects the corrected foundation v2 specification (commit 3641d59): 8 boundaries, 15 objects, 7 contract types, 11-state chain. The diagram is structural (component/block), not data flow. It shows 6 boundary zones stacked vertically with objects created at each boundary, a Contract sidebar with 7 types and governance lifecycle, and a Lineage Boundary indicator. CO and MS DAG self-references are shown. State annotations are included per zone.

## Options Considered

N/A

## Consequences

N/A
