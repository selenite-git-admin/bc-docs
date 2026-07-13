---
uid: DEC-58b56c
title: "First pilot source-system pair: D365 Business Central + Odoo — platform-proof over GTM optics"
description: "BC = first pilot source (chain proof to first_hand_proven, free real instance + MIT source); Odoo = second source (zero-MC-edit portability proof of ADR-3785f8 D3); platform confidence over GTM optics; SAP retained, Fusion deferred; implementation held until Track C"
status: decided
date: 2026-07-13T07:27:01.317Z
project: platform
domain: sources
subdomain: source-catalog
focus: pilot-strategy
---

# First pilot source-system pair: D365 Business Central + Odoo — platform-proof over GTM optics

## Context

SAP ECC structurally cannot reach first_hand_proven without a customer: SAP publishes no authentic data model (catalog seeded from leanx.eu/se80.co.uk community sources; sap-ecc.md records zero validation against a real tenant), which is exactly the pilot catch-22 SDG was built to break — SDG solves the data half but cannot solve the semantics-authority half. A verified 2026-07-13 survey of Tier-1/upper-mid ERP public documentation ranked BC #1 (only ERP combining vendor-authored field-level docs + openly-licensed readable posting source + free real instance), Oracle Fusion #2 (best pure public data dictionary — the SE11-shaped artifact SAP never published — but no trial instance), with Workday/Infor eliminated (login-gated). Odoo loses on GTM optics but wins as portability-proof second leg: total schema transparency, simplest onboarding cost, free instance. Founder explicitly ranked platform confidence above GTM optics: the pilot's job at this stage is to prove the architecture (chain E2E + multi-source portability), and a recognizable-logo realization (Fusion/SAP) can be added later at A/C-layer cost only, which is precisely what the portability proof makes credible. Study artifact: barecount-devhub .claude/STUDY-first-pilot-source-system-tier1-erp-2026-07-13.md.

## Decision

The first pilot-ready source system is Microsoft Dynamics 365 Business Central; Odoo (community edition, accounting core) is the designated SECOND source. Selection criterion is explicitly platform confidence over go-to-market optics (founder call, 2026-07-13): the pair maps 1:1 onto the platform's two unproven claims.

1. BC = chain proof. Full E2E (reader → SO → CO → metric → snapshot) against a REAL vendor system, targeting the first `first_hand_proven` entry in the source catalog (currently 0 of 59). Feasible with zero customers: free sandbox/Docker containers with CRONUS demo data, vendor-authored per-table reference on Microsoft Learn (CC BY 4.0), full application source MIT-licensed (github.com/microsoft/BCApps) so posting semantics are readable code, and an OData V4 API matching existing executor/SDG protocol competence.

2. Odoo = portability proof. Onboarding Odoo as the second source with ZERO metric-contract edits is the first real exercise of ADR-3785f8 Decision 3 (second source adds A/C legs only — touches neither canonical concepts nor MCs). LGPL source is the schema authority; accounting core is in the open community edition; free local instance.

Sequencing: BC first, then Odoo (one-then-many discipline, D268); never both in flight simultaneously. Implementation is HELD until Track C / current metric-architecture work lands (aligned with the Codex auditor memo timing, artifacts/metric-audit/MEMO-Codex-generic-source-systems-for-synthetic-pilots-2026-07-13.md / TSK-cfd3ab).

Data-origin pattern for both: prefer (a) reader against a real local instance with demo data, then (b) synthetic volume posted THROUGH the vendor's own posting APIs (coherence guaranteed by vendor code), before (c) any hand-built SDG simulator — reversing the SAP-era simulator-first pattern for source systems where a real instance is freely obtainable.

Explicitly NOT decided/discarded: SAP ECC is retained (shape-tested simulator, pitfall corpus, seed catalog; its realization is proven when a real SAP customer grants access, per D384 posture). Oracle Fusion Cloud ERP is the deferred enterprise-optics realization (best public data dictionary, no free instance) — addable later as new A/C legs; all metric contracts carry over untouched by construction. Codex's BC_GENERIC_ERP direction remains parked (TSK-cfd3ab) and stays relevant for CRM/HRMS/ITSM categories where no vendor publishes an open data model; its claim-boundary and versioning discipline (version-exact source identity, schema-vs-instance separation, scenario provenance, per-realization audit scope) applies wholesale to BC and Odoo realizations.
