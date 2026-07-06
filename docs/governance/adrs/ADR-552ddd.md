---
uid: DEC-552ddd
title: "Separate catalog_status and verification_status on source entities"
description: "Split lifecycle into catalog_status (governance) and verification_status (metadata quality) on all 6 source tables"
status: implemented
subdomain: validation-lifecycle
focus: status-decomposition
date: 2026-03-23
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Separate catalog_status and verification_status on source entities

## Context

Split entity lifecycle into three independent concerns:

1. **catalog_status** (existing) — governance: registered → approved → deprecated → retired. Human-controlled.
2. **verification_status** (new) — metadata quality: unverified → verified → disputed → manually_verified → rejected. AI + Human opinion.
3. **validation_status** (new) — runtime proof: not_validated → validated. Set by successful admission run. Binary stamp, not a lifecycle.

Verification is opinion. Validation is fact. All three are orthogonal — a module can be approved + disputed + not_validated simultaneously.

Existing 254K approved entities keep catalog_status='approved', verification_status='unverified', validation_status='not_validated' (go-forward, not retroactive).

## Decision

Split entity lifecycle into two independent concerns:

1. **catalog_status** (existing) — governance lifecycle: registered → approved → deprecated → retired. Human-controlled.
2. **verification_status** (new column) — metadata quality: unverified → verified → disputed → manually_verified | rejected. AI + Human.

Add `verification_status TEXT NOT NULL DEFAULT 'unverified'` with CHECK constraint `('unverified','verified','disputed','manually_verified','rejected')` to all 6 source tables: source_provider, source_system, source_version, source_module, source_object, source_field.

catalog_status CHECK updated to: ('registered','approved','deprecated','retired').

Existing 254K approved entities keep catalog_status='approved', verification_status='unverified' (go-forward, not retroactive).

## Options Considered

N/A

## Consequences

N/A
