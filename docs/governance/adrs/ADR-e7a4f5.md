---
uid: DEC-e7a4f5
title: "Readers are domain-bound, not source-bound"
description: "A reader like AR Invoice Reader reads AR invoices from any source. Source category is a connector/provider property, not a reader property."
status: implemented
subdomain: readers-and-flavors
focus: domain-bound-readers
date: 2026-03-13
project: platform
domain: readers
authority: authoritative
migrated_from: legacy v2 archive
---


# Readers are domain-bound, not source-bound

## Context

A reader like AR Invoice Reader reads AR invoices regardless of source system (SAP, Oracle, SDG). Source-binding is a property of the target source (flavor), not the reader itself.

## Decision

Readers are domain-specific ingress components (e.g., "AR Invoice Reader" reads AR invoices from any source). Source Category is a connector/provider property, not a reader property. The reader list page uses only domain pills for filtering, no source category tier.

## Options Considered

N/A

## Consequences

N/A
