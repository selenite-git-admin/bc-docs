---
uid: DEC-ea5074
title: "SC/AC Naming Convention — sc__{system}__{table}"
description: "SC/AC Naming Convention — sc__{system}__{table}"
status: superseded
superseded_by: DEC-3fe389
subdomain: naming-convention
focus: vocabulary
date: 2026-04-06T02:15:56.773Z
project: bc-core
domain: contracts
migrated_from: legacy v2 archive
---

# SC/AC Naming Convention — sc__{system}__{table}

> **Superseded by DEC-3fe389 (D560), 2026-08-08.** Contract identity is now the UUID alone (sole
> authority) plus one opaque speakable per-family uid (`SC-`/`AC-…`); semantic `sc__{system}__{table}`
> names are retired. This ADR's own admission — "the sourceObjectId UUID is the real identity; the name
> is a slug" — and its bet on "0 cross-version collisions today" (which Odoo editions/majors break) are
> exactly what motivated the supersession.

## Context

Short, deterministic, collision-free with current data. System slug disambiguates ecc vs s4hana. Version not needed since s4hana Cloud and On-Premise have zero overlapping table names. Replaces verbose displayName pattern (e.g. "Accounting Document Header Source Contract") with clean uppercase format.

## Decision

Source and Admission contracts follow deterministic naming:

DB name: sc__{system}__{table} / ac__{system}__{table}
Display name: SC {SYSTEM} {TABLE} / AC {SYSTEM} {TABLE}

Examples: sc__ecc__bkpf → SC ECC BKPF, ac__s4hana__acdoca → AC S4HANA ACDOCA

No version segment needed — 0 cross-version table name collisions exist today between s4hana Cloud and On-Premise. 61 cross-system collisions (ecc vs s4hana) are disambiguated by the system slug. The sourceObjectId UUID is the real identity; the name is a human-readable slug.
