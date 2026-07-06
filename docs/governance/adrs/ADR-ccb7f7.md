---
uid: DEC-ccb7f7
title: "Source Discovery Model — reconnaissance, not extraction"
description: "Discovery is metadata reconnaissance only — reveals what exists in a tenant's source system without reading or admitting any data. No SOs produced."
status: implemented
subdomain: foundational-architecture
focus: discovery-as-reconnaissance
date: 2026-03-08
project: bc-core
domain: database
refs:
  - type: decision
    label: "D030"
authority: authoritative
migrated_from: legacy v2 archive
---


# Source Discovery Model — reconnaissance, not extraction

## Context

UinBAT Reader is business-aware (Component Ref 090) — reads ONLY contracted objects/fields. "Admit everything" is pipeline behavior, structurally forbidden (D009). Discovery and admission are completely different concerns with different outputs, resource costs, and governance. Scenario 7 confirmed: drift is reactive (contract-shielded), re-discovery is proactive (metric expansion).

## Decision

Source discovery is metadata reconnaissance — it reveals what exists in a tenant's source system without reading, admitting, or extracting any data.

**Discovery is:**
- Metadata scan (e.g., SFDC describe() API, SAP $metadata, Tally export catalog)
- No Source Objects produced, no DB writes to boundary schema, no reader execution
- Results stored as discovery metadata (separate from Source Catalog operational data)
- Informational: "Tenant X has 27 sObjects with 500+ fields"

**Discovery is NOT:**
- Extraction (no data movement)
- Admission (no contract evaluation)
- A mandate to read everything discovered

**Periodic re-discovery:**
- Scheduled scans (cadence configurable per tenant) detect NEW objects and NEW fields
- Purpose: identify new metric activation opportunities (continuous Phase 2)
- NOT for schema drift detection — drift is handled reactively via alerts → tickets → SOP

**Schema drift handling:**
- Detected at runtime by source contract drift_detection and admission contract validation
- Alert fires automatically → ticket created in platform ticket system (D030)
- Tenant admin can see the ticket
- Platform team resolves via SOP: investigate, author new contract version, activate

**Discovery results lifecycle:** discovered → reviewed → contracted (or: discovered → noted → not contracted)

## Options Considered

N/A

## Consequences

N/A
