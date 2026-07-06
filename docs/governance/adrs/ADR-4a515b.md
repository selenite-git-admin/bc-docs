---
uid: DEC-4a515b
title: "All 4 process chains from day one — P2P, O2C, R2R, Plan-to-Produce"
description: "bc-sdg covers P2P, O2C, R2R, Plan-to-Produce simultaneously. All chains feed FI via SAP integrated posting model"
status: implemented
subdomain: synthetic-data-coverage
focus: sap-process-chain-breadth
date: 2026-03-02
project: bc-sdg
domain: subscription
authority: authoritative
migrated_from: legacy v2 archive
---


# All 4 process chains from day one — P2P, O2C, R2R, Plan-to-Produce

## Context

Partial coverage looks like a prototype. Full chain coverage demonstrates enterprise readiness. Each chain tests different BareCount capabilities: P2P tests 3-way match integrity, O2C tests aging/dunning, R2R tests period close, P2P tests variance analysis.

## Decision

bc-sdg covers all 4 SAP process chains simultaneously: (1) Procure to Pay (MM + AP + FI) — PO → GR → Invoice → 3-way match → Payment. (2) Order to Cash (SD + AR + FI) — SO → Delivery → Billing → Payment → Dunning. (3) Record to Report (FI + CO) — Journal entries, period close, intercompany, allocations. (4) Plan to Produce (PP + MM + CO) — BOM → Routing → Prod Order → Confirmation → GI/GR → Variance. All chains feed FI automatically via SAP's integrated posting model, with ACDOCA/BKPF as the common sink. SAP modules covered: FI, CO, MM, SD, PP, QM (for pharma), RE-FX (for real estate).

## Options Considered

N/A

## Consequences

N/A
