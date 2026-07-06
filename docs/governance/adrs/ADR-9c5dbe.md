---
uid: DEC-9c5dbe
title: "Operations group removed — ops monitoring lives on Dashboard + object detail pages"
description: "No standalone Operations nav group. Ops monitoring surfaces on Dashboard and individual object detail pages instead."
status: implemented
subdomain: bc-admin
focus: nav-cleanup
date: 2026-03-13
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Operations group removed — ops monitoring lives on Dashboard + object detail pages

## Context

Admission Cycles is now visible on SO Detail page recent observations. Boundary health is now a dashboard widget. Separate Operations nav group was redundant after D062 pivoted contracts/admission on SO context.

## Decision

Operations nav group (Admission Cycles, Boundaries) removed. Operations data surfaces in two places: (1) Dashboard — aggregate operations monitor with admission summary stats and boundary health table, (2) SO Detail page — per-object admission history and evidence. Principle: ops data lives on the object it operates on, not in a separate silo. Cross-object aggregate monitoring is a dashboard concern.

## Options Considered

N/A

## Consequences

N/A
