---
uid: DEC-a1290e
title: "v3 tenant metric read surface (/beyond) is MCF-native, not a legacy bridge"
description: "v3 tenant metric read surface (/beyond) is MCF-native, not a legacy bridge"
status: decided
date: 2026-07-02T10:18:35.472Z
project: bc-core
domain: metrics
subdomain: metrics/tenant-read
focus: runtime
---

# v3 tenant metric read surface (/beyond) is MCF-native, not a legacy bridge

## Context

The existing tenant-views metric surface (TenantMetricCatalogService, /api/t/metrics/*) reads the legacy stack — contract.metric_contract (0 rows), metric_definition, and progression.metric_snapshot_index (does not exist in tenant DBs). All 52 real metrics are authored in MCF (mcf.metric_contract); the only governed snapshot lives in progression.metric_evaluation + fact.ms_ (DEC-5ea578). Bridging the legacy surface to MCF would be perpetually patchy (two authorities, snapshot_index provisioning, name-lookup gaps already observed — ContractNameLookup only queries legacy). A clean MCF-native read surface for the v3 /beyond canvas aligns with the greenfield v3 pivot (legacy = inspiration) and the mcf-legacy-bridge 'MCF wins' policy, and lets the first real metric (AR Balance, ₹10,306,696.90 as of FY2025-26 P06 on pilot1) render without carrying legacy debt. Reads never trigger evaluation (Foundation: reads do not evaluate; repair-location F).

## Decision

The customer-facing /beyond (v3) metric surface reads the MCF + governed-snapshot stack DIRECTLY and does not bridge the legacy metric stack. New tenant-scoped bc-core endpoints under /api/t/beyond/*: (1) GET /metric-functions — active mcf.metric_contract (current MCV) grouped by function_code, joined to master.master_function for label/sort_order, with total + snapshotBacked (count of metrics in the function that have a governed snapshot for this tenant = an accepted progression.metric_evaluation + a fact.ms_ row); (2) GET /metrics?function= — MCF metric rows (id = metric_contract_uid, name = mc_name, displayName, subfunction via master.master_subfunction, snapshotBacked, and the latest governed snapshot value + fiscal_period + evaluatedAt when producing); (3) GET /metrics/:mcUid/snapshot — latest accepted evaluation for this tenant resolved MCF-aware (mc_name from mcf.metric_contract, version normalized to semver) → fact.ms_<name>_v<ver>. Reads are MCF-only; nothing legacy (contract.metric_contract, metric_definition, progression.metric_snapshot_index — all empty/absent). Visibility = ALL active MCF metrics grouped by function with a producing/has-data overlay; subscription-plan entitlement (DEC-4aa2fd/D475) is a deferred overlay, not a gate. bc-portal /beyond repoints its two LHS hooks (function-counts, per-function list) to these endpoints via a new beyond-metrics.ts api module; the legacy /metrics pages and TenantMetricCatalogService are left untouched.

