---
uid: DEC-e9a1a7
title: "join_context Scope — same-source-system only, no cross-system joins"
description: "join_context in canonical mapping bindings is restricted to multi-table joins within the same source system. Cross-system joins are structurally forbidden."
status: implemented
subdomain: canonical-evaluation
focus: join-scope-constraint
date: 2026-03-08
project: platform
domain: database
refs:
  - type: decision
    label: "D021"
  - type: decision
    label: "D023"
authority: authoritative
migrated_from: legacy v2 archive
---


# join_context Scope — same-source-system only, no cross-system joins

## Context

Scenario 5 analysis (SES-6bb15f): proposed cross-system SAP+SFDC join was incorrect. All D023 examples are same-source multi-table. Cross-system join assumes fragile cross-references. Platform designed as "joint-less" ecosystem — convergence at CO level, aggregation at metric level. Operational enrichment fields have no metric bearing and are declined.

## Decision

join_context[] in canonical mapping bindings is restricted to multi-table joins within the SAME source system. Cross-system joins are not supported.

**Supported (same source system):**
- SAP BKPF + BSEG join on BUKRS+BELNR+GJAHR → AP Vendor Invoice CO
- SAP SKA1 + SKAT join on SAKNR+SPRAS → GL Account CO
- SFDC Opportunity + OpportunityLineItem join on OpportunityId → Sales Pipeline CO

**Not supported (cross-system):**
- SAP BKPF + SFDC AP_Invoice__c join on BELNR = SAP_Document_Number__c — DECLINED
- Cross-system "enrichment" with non-metric operational fields — DECLINED

**Cross-system pattern is CONVERGENCE, not JOIN:**
- SAP produces AP Vendor Invoice COs (from SAP data)
- SFDC produces AP Vendor Invoice COs (from SFDC data)
- Same canonical type, separate CO instances per source
- Metrics aggregate across CO instances at metric level (D021: metric references N COs)

**Rationale:**
1. D023 examples are all within same source system (BKPF+BSEG+RSEG, SKA1+SKAT)
2. Cross-system joins require customer-maintained cross-references (fragile, rarely clean)
3. Cross-system key consistency never guaranteed
4. Data timing differs across systems (ERP month-end vs CRM real-time)
5. Operational enrichment fields (vendor_contact, internal_notes) have zero metric bearing — declined by principle
6. Convergence + metric-level aggregation achieves the same analytical outcome without cross-system coupling

## Options Considered

N/A

## Consequences

N/A
