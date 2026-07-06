---
uid: DEC-f5111d
title: "Retire Accountability Boundary, Responsibility object, and Accountable state from Foundation Specification"
description: "Retire Accountability Boundary, Responsibility object, Accountable state from Foundation — covered by Evidence/Lineage/Governance in v2"
status: implemented
subdomain: foundation-spec
focus: retirement
date: 2026-04-01T03:54:37.965Z
project: bc-docs
domain: foundation
authority: authoritative
migrated_from: legacy v2 archive
---

# Retire Accountability Boundary, Responsibility object, and Accountable state from Foundation Specification

## Context

During bc-docs to legacy v2 archive migration audit, document-by-document cross-reference showed these 3 concepts (responsibility.md, accountable-state.md, accountability-boundary.md) have no v2 equivalent. v2 achieves the same accountability through structural mechanisms (Evidence, Lineage, contract governance audit trail) rather than a dedicated runtime object. The Accountability Boundary added complexity without operational distinction from Evidence emission. Retiring simplifies the Foundation spec while preserving accountability guarantees through existing v2 mechanisms.

## Decision

The legacy Foundation Specification defined an Accountability Boundary, a Responsibility object (explicit binding between preserved record and accountable actor), and an Accountable state (terminal state when responsibility is bound). These concepts have no equivalent in legacy v2 archive. The v2 execution model achieves accountability structurally through Evidence Objects (immutable proof at every boundary), Lineage Objects (structural trace of derivation), and the Activity Log (platform audit trail). Explicit responsibility binding is handled by contract governance (who approved, who authored) rather than a separate runtime object. These three legacy concepts are formally retired and will not be migrated to v2.
