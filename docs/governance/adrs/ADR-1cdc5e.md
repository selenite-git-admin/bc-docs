---
uid: DEC-1cdc5e
title: "Drop bc_tenant database — orphan with t_xxx schemas replaced by tbc_xxx"
description: "Dropped orphan bc_tenant database. App connects to tbc_{slug}_dev (separate DB per tenant). DDL init script no longer creates bc_tenant."
status: implemented
subdomain: tenant-topology
focus: tenant-db-naming
date: 2026-03-25
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Drop bc_tenant database — orphan with t_xxx schemas replaced by tbc_xxx

## Context

bc_tenant was created by DDL but nobody connected to it. The tbc_{slug} databases are the actual tenant databases. Having both caused confusion about which was authoritative.

## Decision

Dropped bc_tenant database containing t_selenite, t_acme, t_globex schemas. These were orphans — the app connects to tbc_selenite_dev (separate database per tenant). The DDL init script no longer creates bc_tenant.

## Options Considered

N/A

## Consequences

N/A
