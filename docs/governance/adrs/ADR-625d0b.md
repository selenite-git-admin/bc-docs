---
uid: DEC-625d0b
title: "Reader contract readiness: bound flavors / total flavors"
description: "Reader readiness = ratio of valid contract bindings to total flavors. Displayed as N/M bound with green/amber/gray color coding."
status: implemented
subdomain: readers
focus: readiness-metric
date: 2026-03-14
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Reader contract readiness: bound flavors / total flavors

## Context

Foundation docs (Component Ref 090, 091) define each flavor as a source-system-specific extraction variant that requires an admission contract binding to operate. Showing separate "Sources" and "Contracts" columns was misleading — a reader with 2 sources and 3 contracts appeared wrong. The correct model is 1 contract per flavor minimum, with shared contracts possible (e.g., Exchange Rate Reader: 3 flavors, 1 shared contract).

## Decision

Reader readiness is measured as the ratio of valid contract bindings to total flavors (target sources). Each flavor needs at minimum one active binding to a released admission contract. Display as "N/M bound" with color coding: green (all bound), amber (partial), gray (none). Orphaned bindings (contract deleted) are excluded from counts via innerJoin validation.

## Options Considered

N/A

## Consequences

N/A
