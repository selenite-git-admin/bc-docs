---
uid: DEC-6a1b47
title: "Add OER flavor as second exchange rate source to prove CO convergence"
description: "Open Exchange Rates added as second exchange rate flavor. Different SO structure must produce identical CO — proves canonical convergence."
status: decided
subdomain: reader-flavors
focus: exchange-rate-convergence-proof
date: 2026-02-28
project: bc-core
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Add OER flavor as second exchange rate source to prove CO convergence

## Context

A single source (ECB) doesn't adequately test the canonical evaluation boundary. Two sources with different SO shapes converging to one CO shape demonstrates the architectural purpose of canonical evaluation.

## Decision

Add Open Exchange Rates (OER) as second flavor for the exchange rate reader. ECB SO and CO are near-identical (field renaming only). OER has different source payload structure but must produce identical CO schema. This proves canonical evaluation adds real value — multi-source convergence to single canonical form.

## Options Considered

N/A

## Consequences

N/A
