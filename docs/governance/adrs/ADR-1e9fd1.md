---
uid: DEC-1e9fd1
title: "Observed Indicators — compositionCode 'observed' for External Reference Metrics"
description: "Add compositionCode 'observed' for externally sourced reference indicators (credit ratings, indices, FX rates, benchmarks)"
status: superseded
superseded_by: DEC-9dce29
date: 2026-04-04T13:28:11.039Z
project: bc-core
domain: metrics
migrated_from: legacy v2 archive
---

# Observed Indicators — compositionCode 'observed' for External Reference Metrics

## Context

Metrics like credit ratings, stock indices, currency rates, and benchmark rates are not KPIs (no formula, no internal computation) but are essential context for KPIs that are computed. Rather than creating a separate system, they fit naturally in the existing metric_definition table with a new compositionCode. The Exchange Rate Reader architecture (D043) already handles sourcing external rates — observed indicators generalize that pattern to all external reference data.

## Decision

Add 'observed' to metric_definition.compositionCode enum (joining primary, derived, composite). Observed metrics are externally sourced reference indicators — not internally computed KPIs. They have no formula, no variable decomposition, and are directly ingested from external feeds via Readers.\n\nExamples: Credit Ratings (S&P/Moody's/Fitch), Stock Indices (Sensex, Nifty 50), Currency Rates (USD/INR, EUR/USD), Benchmark Rates (SOFR, LIBOR), Commodity Prices (Brent, Gold), Macro Indicators (CPI, GDP growth).\n\nUI treatment:\n- Formula tab: 'Externally observed — no computation' (not 'No formula yet')\n- Variables section: N/A\n- Knowledge section: Applies normally (definition, stakeholders, thresholds)\n- Source binding: Links to the Reader/Source providing the value (ECB Reader for EUR rates, BSE feed for Sensex)\n\nThese indicators provide essential context for computed KPIs — a CFO reviewing DSO needs the credit rating trend; a treasurer evaluating FX hedging needs actual currency rates. They belong in the Metric Catalog alongside KPIs but are clearly marked as observed, not computed.
