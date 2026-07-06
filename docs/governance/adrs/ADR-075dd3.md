---
uid: DEC-075dd3
title: "Old readers/flavors retired — fresh assets with SDG executor configs"
description: "11 old readers deprecated (wrong SAP field names). 5 fresh readers created with proper SDG OData V4 executor configs."
status: implemented
subdomain: readers-and-flavors
focus: one-time-cleanup-action
date: 2026-03-25
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Old readers/flavors retired — fresh assets with SDG executor configs

## Context

Old configs were created before the execution engine was wired. Rather than patching, clean slate ensures consistency. Each reader now has exactly 1 flavor with correct executor config, 1 OC binding, and 1 SDG connection.

## Decision

All 11 readers and flavors created Mar 24 retired (status=deprecated, archived_at set). They had old observation schema configs (SAP field names BELNR/BUKRS) incompatible with SDG OData V4 executor (CompanyCode/AccountingDocument). 5 fresh readers created with proper SDG executor config (sourceEntity, keyFields, batchSize), each linked to observation contract and SDG connection.

## Options Considered

N/A

## Consequences

N/A
