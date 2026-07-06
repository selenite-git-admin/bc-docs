---
uid: DEC-a1110e
title: "Support schema — internal ticketing for platform & tenant issues"
description: "Two tables (ticket + comment) in support schema for internal issue tracking. Platform and tenant scoped."
status: implemented
subdomain: platform-tooling
focus: support-tickets
date: 2026-03-20
project: bc-core
domain: database
refs:
  - type: decision
    label: "D030"
authority: authoritative
migrated_from: legacy v2 archive
---


# Support schema — internal ticketing for platform & tenant issues

## Context

Operations schema tracks "how is the system running" (observability). Support schema tracks "what needs human attention" (action). Separate schema because ticketing will grow: SLA definitions, escalation chains, external system sync (Jira/ServiceNow), customer-facing portal. Keeping it separate from operations prevents clutter.

## Decision

Add `support` as 11th platform DB schema with 2 tables: `support.ticket` (category: admission_failure, connection_failure, contract_violation, drift_alert, manual; severity: critical/high/medium/low; status: open/acknowledged/in_progress/resolved/closed; source: system/user) and `support.ticket_comment` (FK to ticket). Tickets can be tenant-scoped (tenant_id) or platform-wide (NULL). System auto-generates tickets from failed runs (D030), users can create manual tickets.

## Options Considered

N/A

## Consequences

N/A
