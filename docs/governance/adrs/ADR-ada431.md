---
uid: DEC-ada431
title: "Source Category — Reader/Provider trust-tier classification"
description: "Sources classified into trust tiers (Enterprise, Third Party, Public) based on reader and provider characteristics."
status: implemented
subdomain: source-catalog
focus: trust-tier-classification
date: 2026-03-04
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Source Category — Reader/Provider trust-tier classification

## Context

The existing Provider `domain` field classifies WHAT the data is (business meaning). sourceCategory classifies WHERE it comes from (trust tier). These are independent axes both needed for operational visibility. Enterprise = internal systems (SAP, Oracle), third_party = licensed external providers (Bloomberg, Refinitiv), public = open reference data (ECB, FRED). This distinction drives data governance, SLA expectations, and cost attribution. Not in foundation spec but does not conflict — it's operational metadata on the Reader, not on the admission boundary or Source Objects.

## Decision

Readers carry a `sourceCategory` field with enum values: enterprise | third_party | public. This classifies the trust/origin tier of the data source — orthogonal to the business `domain` field (finance, reference_data, etc.). Stored on registry.reader table with index. Exposed as first filter in Reader Management UI with cascading: Source Category → Domain → Subdomain → Status → Search. Labels: Enterprise Sources, Third Party Sources, Public Sources. Default: enterprise.

## Options Considered

N/A

## Consequences

N/A
