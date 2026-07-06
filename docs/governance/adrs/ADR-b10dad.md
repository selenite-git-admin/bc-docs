---
uid: DEC-b10dad
title: "Exchange Rate Reader: One reader, flavor-detected, source-specific contracts"
description: "Single exchange_rate_reader with multiple flavors (ECB, OER, FRED). Each flavor has its own admission contract."
status: implemented
subdomain: readers
focus: flavor-pattern-reference
date: 2026-02-27
project: bc-core
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Exchange Rate Reader: One reader, flavor-detected, source-specific contracts

## Context

Confirmed against three authoritative sources: (1) Component Ref 090 Section 7.1 — "Each UinBAT Reader operates under one or more Admission Contracts", (2) Patent Section 4.2 — "multiple Source Contracts may exist to handle different flavors... resolved at runtime", (3) Patent Section 4.4 — Flavour Detection as dynamic probing mechanism. Foundation spec (LOCKED) confirms admission is contract-bound, rejection = absence = non-occurrence. Full architecture doc: bc-docs/02-component-references/exchange-rate-reader-architecture.md

## Decision

ONE Exchange Rate Reader with multiple flavors (ECB SDMX, OER, FRED). Each flavor has its own source-specific admission contract resolved at runtime via flavor detection. All flavors emit the same Exchange Rate Source Object structure. Domain: currency/exchange data. Reader handles north-side only (admission). South-side (canonical evaluation, metrics, actions) is not the reader's concern. Rejection handling (bad weather) is a Control Plane concern (TSK-2607e2). bc-core seed needs consolidation from two separate readers to one (TSK-ef20e4).

## Options Considered

N/A

## Consequences

N/A
