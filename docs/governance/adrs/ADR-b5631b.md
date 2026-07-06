---
uid: DEC-b5631b
title: "Field Data Type Quality Gate — Mandatory Validation at AI Verify and Registration"
description: "Two-layer quality gate: AI verify flags missing types + DTO enum validation. 9-value BareCount type vocabulary."
status: implemented
subdomain: ai-verification
focus: data-type-gate
date: 2026-04-05T15:38:00.716Z
project: bc-core
domain: sources
migrated_from: legacy v2 archive
---

# Field Data Type Quality Gate — Mandatory Validation at AI Verify and Registration

## Context

BKPF (critical SAP table) was registered with zero data types on fields — no gate caught it. All 6,985 seed fields have blank data_type_code. Without type information, downstream contract chain (SC→AC→CC→MC) cannot validate field bindings. Defense in depth: AI catches bad seed data early, DTO prevents untyped fields from entering the platform.

## Decision

Add two-layer quality gate for field data types: (1) bc-ai table-verify flags tables with missing field types, (2) bc-core DTO validates dataTypeCode against a 9-value enum. BareCount normalized type vocabulary: string, integer, decimal, date, datetime, time, boolean, text, binary. Native types (SAP ABAP, SaaS generic) are mapped to BareCount types at registration time. native_type_text is preserved as-is for provenance.
