---
uid: DEC-ad76e9
title: "Three-Phase Tenant Onboarding — instant value, gap closure, consulting"
description: "Onboarding in three phases: Phase 1 instant value from platform defaults, Phase 2 gap closure, Phase 3 consulting engagement."
status: implemented
subdomain: tenant-onboarding
focus: phasing-model
date: 2026-03-08
project: bc-admin
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Three-Phase Tenant Onboarding — instant value, gap closure, consulting

## Context

Scenario planning (SES-6bb15f) established: every real tenant has customization (S1 rejected). Onboarding without automation = multi-week consulting per tenant (mini-SAP trap). Three-phase model separates product (scalable), platform (manageable), and consulting (premium). Phase 1 zero-human-effort is the scalability requirement. Client admin excluded from contract governance to protect CO→Metric integrity.

## Decision

Tenant onboarding follows a three-phase model with distinct effort levels, fee structures, and human involvement:

**Phase 1: Instant Value (automated, platform subscription fee, ZERO human effort)**
- Discovery scan completes
- Auto-match discovered objects/fields against existing canonical concepts using pre-built mapping templates
- bc-admin shows: "N metrics ready to activate NOW"
- Tenant activates with one click
- Standard source objects (SFDC Account, SAP BKPF) match known COs via templates
- MUST work without platform team involvement — this is the scalability gate

**Phase 2: Metric Gap Closure (AI-assisted + platform team review, platform subscription fee)**
- Tenant browses metric catalog: "I also want these metrics"
- bc-admin shows missing SOs for desired COs, matched against discovery results
- AI suggests field mappings for custom objects/fields based on naming, types, patterns
- Platform team reviews and approves AI suggestions (one-click approve, not authoring from scratch)
- New admission contracts + mapping bindings authored
- Additional metrics activated
- CONTINUOUS: periodic re-discovery reveals new fields → new metric opportunities

**Phase 3: Consulting (BC team + client, separate engagement fee)**
- "What else can we do with remaining discovered objects?"
- Objects outside current metric catalog (Tower__c, SubProject__c, etc.)
- BC team analyzes business meaning, proposes new canonical concepts, industry-specific metrics
- May lead to Industry Packs (TSK-b7dbef)
- Different engagement package, different fee — prevents BC from becoming client's data team

**Authorization boundary:**
- Client admin: CANNOT touch contracts, mappings, canonical wiring, reader configuration
- Platform team: Authors all contracts, reviews AI suggestions, governs canonical vocabulary
- New canonical concept creation: Requires BareCount approval (platform vocabulary expansion)
- Field scope decisions: BareCount decides which fields are metric-driving

## Options Considered

N/A

## Consequences

N/A
