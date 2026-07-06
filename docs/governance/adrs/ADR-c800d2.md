---
uid: DEC-c800d2
title: "bc-admin v1.0.0 Lock — Scope & Architecture"
description: "Lock bc-admin v1.0.0 scope: 57 pages, chain-based nav, full source+admission contract lifecycle, drift detection, governance state machine."
status: implemented
subdomain: ui-architecture
focus: scope-lock
date: 2026-03-24
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# bc-admin v1.0.0 Lock — Scope & Architecture

## Context

v1.0.0 represents the platform admin capability to manage the full source chain: catalog → source contracts → admission contracts → governance lifecycle → drift detection. This is the minimum viable contract management surface for the platform launch.

## Decision

bc-admin v1.0.0 locked with: 57 pages (42 live + 15 placeholders), chain-based navigation (9 topbar sections), full contract lifecycle (source + admission), drift detection, governance state machine (draft/review/approved/active/superseded). SAP-specific routes removed — all systems treated equally. Admission contracts have their own DB table family (contract.admission_contract). Governance states aligned to DB constraint vocabulary. 28,918 contracts seeded (14,459 source + 14,459 admission). Archival is contract-level (archived_at), not a governance state.

## Options Considered

N/A

## Consequences

N/A
