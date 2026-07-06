---
uid: DEC-22ed4b
title: "Material Master vs Product Master — distinct readers"
description: "Separate readers: material-master-reader (procurement/SAP MM) and product-master-reader (sales/CRM). Different business semantics, no merge."
status: implemented
subdomain: readers
focus: domain-separation
date: 2026-03-08
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Material Master vs Product Master — distinct readers

## Context

Different business semantics: materials are procurement-domain master data (MARA/MARC/MARD), products are sales-domain catalog data (SFDC Product2, PricebookEntry). Merging them would violate BareCount's domain-specific reader principle and lose admission precision.

## Decision

material-master-reader (procurement/materials) and product-master-reader (product/catalog) are separate readers. Material = input side (what you procure/manufacture, SAP MM dominated). Product = output side (what you sell/price, CRM dominated). They may share canonical overlap but that is south-side convergence, not reader-level conflation.

## Options Considered

N/A

## Consequences

N/A
