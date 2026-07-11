---
uid: DEC-585edb
title: "OC-v2 join reduce strategy 'sum' — many→one numeric aggregation over join children"
description: "OC-v2 join reduce strategy 'sum' — many→one numeric aggregation over join children"
status: decided
date: 2026-07-11T04:16:05.180Z
project: bc-core
domain: data-platform
subdomain: contract-grammar
focus: schema
---

# OC-v2 join reduce strategy 'sum' — many→one numeric aggregation over join children

## Context

No rationale recorded.

## Decision

Additive amendment to the DEC-0a187d multi-source join grammar (D508): the OC-v2 join_semantics reduce strategy vocabulary extends from {latest_by, first} to {latest_by, first, sum}. Strategy 'sum' aggregates Number(reduce.field) across ALL secondary rows sharing a join key (Σ per key) instead of picking one row. Fail-closed constraints: (1) 'sum' REQUIRES reduce.field; (2) the summed secondary table may map ONLY the reduce.field — mapping any other field from a sum-reduced table is rejected at build/validation time because non-aggregated fields are row-ambiguous under aggregation; (3) null semantics: rows with null/absent field values are skipped; a key with NO secondary rows leaves the mapped canonical field NULL (never a fabricated 0 — an invoice line with no delivery linkage must not silently read as delivered=0). Motivation: real delivered quantity is LIPS.LFIMG with MANY delivery lines per originating order line; the pick-one reducers (latest_by, first) cannot express it, and mapping billed quantity (FKIMG) as delivered was refused as semantically false (TSK-c008dc). Meaning is declared once in the OC join_semantics + CC field_selection and evaluated at the canonical boundary (Invariant I); join keys and the reduce field are explicit contract declarations (Invariant IV). Unlocks: total_delivered_quantity + order_fill_rate and any future many-child quantity/amount aggregation at a parent grain (deliveries per order line, payments per invoice, allocations per document).
