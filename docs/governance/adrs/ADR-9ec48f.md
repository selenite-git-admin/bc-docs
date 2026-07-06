---
uid: DEC-9ec48f
title: "Six customer profiles across industries — configurable company simulation"
description: "SDG ships six preset company profiles (retail, manufacturing, etc.) with configurable parameters for realistic demo data."
status: implemented
subdomain: synthetic-data-profiles
focus: customer-simulation-library
date: 2026-03-02
project: bc-sdg
domain: platform
authority: authoritative
migrated_from: legacy v2 archive
---


# Six customer profiles across industries — configurable company simulation

## Context

Turns bc-sdg into a sales tool. When meeting a pharma prospect, run PharmaCo profile. Auto prospect → AutoParts. They see their world in the demo. Different SAP versions per profile also proves multi-landscape handling.

## Decision

bc-sdg ships with 6 customer profiles: (1) MfgCo — Discrete Manufacturing, 10,000 Cr, S/4 Cloud. (2) PharmaCo — Pharmaceutical, 5,000 Cr, S/4 On-Prem. (3) AutoParts — Automotive Components, 20,000 Cr, ECC EHP8. (4) ChemCo — Process Manufacturing, 12,000 Cr, S/4 Cloud. (5) FMCG — Consumer Goods, 8,000 Cr, S/4 On-Prem. (6) RealEstateCo — Real Estate, 6,000 Cr, S/4 Cloud. Each profile defines company structure, master data volumes, transaction patterns, edge case frequencies, industry-specific processes, currency/tax profile. Build order: MfgCo first (most generic), then one-by-one.

## Options Considered

N/A

## Consequences

N/A
