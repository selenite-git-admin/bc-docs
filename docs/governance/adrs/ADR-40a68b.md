---
uid: DEC-40a68b
title: "Full OData V4/V2 protocol fidelity — $metadata, $filter, $expand, $top/$skip, delta"
description: "bc-sdg OData server implements full protocol fidelity. Readers connect to it identically to real SAP — no shortcuts"
status: implemented
subdomain: odata-protocol
focus: sap-faithful-odata
date: 2026-03-02
project: bc-sdg
domain: readers
authority: authoritative
migrated_from: legacy v2 archive
---


# Full OData V4/V2 protocol fidelity — $metadata, $filter, $expand, $top/$skip, delta

## Context

100% real landscape simulation. If the OData layer is simplified, the pressure test doesn't prove reader robustness. Full protocol means readers are tested against realistic pagination, filtering, delta extraction — same challenges as production SAP.

## Decision

bc-sdg's Fastify OData server implements full OData protocol: $metadata document per entity set, $filter (basic operators), $expand for navigation properties, $top/$skip pagination, $count, $orderby, delta links for change tracking. V4 for S/4 Cloud, V2 for S/4 On-Prem/ECC. BareCount readers connect to bc-sdg identically to real SAP — no shortcuts, no simplified endpoints.

## Options Considered

N/A

## Consequences

N/A
