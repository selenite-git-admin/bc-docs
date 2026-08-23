---
uid: DEC-fc41a3
title: "Source Chain Contract Generation — SAP ECC Finance"
description: "Source chain contracts for SAP ECC Finance — SC/AC per source object, BO-centric readers, two-tier BFs"
status: implemented
subdomain: source-onboarding
focus: sap-ecc-generation
date: 2026-03-29
project: bc-core
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Source Chain Contract Generation — SAP ECC Finance

## Context

Source chain is the missing layer connecting the source catalog (254K objects) to the existing canonical (46 CC) and metric (687 MC) chains. SAP ECC Finance (FI+CO+TR) is the first implementation. BO-centric readers align with D200 canonical-driven flow. Two-tier BFs separate raw observable fields from derived computation fields, enabling clean OC field mapping. Temporal consistency is guaranteed by BareCount's immutable append-only execution model.

## Decision

Generate Source Contracts (SC), Admission Contracts (AC), Observation Contracts (OC), and Readers for SAP ECC Finance domain.

**Scope:** SAP ECC modules FI (5,247) + CO (990) + TR (263) = ~6,500 source objects.

**Key decisions:**

1. **SC/AC are 1:1 with source objects** — one SC and one AC per source catalog object in FI+CO+TR. Function-agnostic (DEC-baaa09). ~6,500 each.

2. **Readers are BO-centric** — 46 readers, one per Business Object. Each reader observes the source tables relevant to its BO.

3. **OC is 1 per reader per source system** — 46 OCs for SAP ECC. Each OC's observation_field_map maps SAP fields → raw Business Fields.

4. **Temporal consistency is inherent** — BareCount's observe→preserve→evaluate model means each SO is an immutable snapshot at observed_at. Multiple readers reading the same table at different times is correct by design. Each observation is truth-at-that-moment. No retroactive updates.

5. **Two-tier Business Fields** — Add field_type_code to business_field: 'primary' (raw/identity fields mapped 1:1 to source fields via OC) and 'derived' (computed measures used by CC/MC evaluation). Existing 1,604 BFs are derived. ~150-250 new primary BFs needed.

6. **Model generalizes across source systems** — For normalized systems (SAP, Oracle EBS), readers group related tables. For self-contained systems (Salesforce, QuickBooks, Stripe), each API object naturally becomes its own reader. Source entity affinity determines grouping.

7. **Generation approach** — Domain-knowledge driven script for SC/AC bulk generation from source catalog. AI-assisted mapping for observation_field_map (SAP field → raw BF), with manual review in UI/script later.

**Counts:**
- SC: ~6,500 (FI+CO+TR objects)
- AC: ~6,500 (1:1 with SC)
- Readers: 46 (1 per BO)
- OC: 46 (1 per reader × SAP ECC)
- Primary BFs: ~150-250 (new raw/identity fields)
- observation_field_map: ~150-250 rows

## Options Considered

N/A

## Consequences

N/A
