---
uid: DEC-1ab381
title: "Platform ticket system — failed runs auto-create incidents"
description: "Failed admission runs auto-create tickets for platform operators. Lightweight incident tracking with lifecycle and assignee, not full ITSM."
status: decided
subdomain: platform-ops
focus: incident-tracking
date: 2026-03-03
project: bc-admin
domain: database
authority: evolving
migrated_from: legacy v2 archive
---


# Platform ticket system — failed runs auto-create incidents

## Context

Failed runs currently have no escalation path — they appear as a status in the admission runs table but require manual discovery. Auto-ticketing ensures platform operators are alerted to failures, can track resolution, and maintain an audit trail. Lightweight design avoids over-engineering — this is not a full ITSM tool, just operational incident tracking for the BareCount platform.

## Decision

Failed admission runs automatically create a ticket/incident in a lightweight platform ticket management system. Tickets live in the platform DB (new registry.ticket or platform.ticket table). Each ticket captures: title, severity, source reference (run ID, reader ID, tenant ID), status lifecycle (open → acknowledged → in-progress → resolved → closed), assignee, timestamps, and notes. bc-admin gets a Tickets/Incidents management page for platform operators. Tickets can also be created manually for other operational issues.

## Options Considered

N/A

## Consequences

N/A
