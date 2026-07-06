---
uid: DEC-2e801a
title: "Lock Beyond canvas as the post-dashboard interface for bc-portal"
description: "Lock /beyond as the single post-dashboard canvas; opt1-4 experiments retired; dashboards archived to src/pages/v2/."
status: superseded
subdomain: bc-portal
focus: canvas-lock
superseded_by: DEC-7e76b9
date: 2026-04-19T07:40:26.108Z
project: bc-portal
domain: frontend
migrated_from: legacy v2 archive
---

# Lock Beyond canvas as the post-dashboard interface for bc-portal

## Context

The dashboard paradigm buried BareCount's core differentiator — 12K contract-governed metrics, each replayable back to source. A metric-first canvas where every value exposes its L1-L7 provenance turns the contract chain moat into a visible product surface. "Go Beyond Dashboards" (the marketing tagline) becomes a literal UI claim: talk to your governed metrics, drag one into Rooth, drill into unfakeable provenance. Single chrome-free page enforces focus; single file (BeyondCanvas.tsx) keeps tightly-coupled drag/focus/expand state coherent.

## Decision

bc-portal adopts a single chrome-free canvas at /beyond as the primary interface, replacing the dashboard paradigm. Structure: 20% grey LHS (function accordion with in-card sub-function filter, internal scroll for 12K+ metric scale, metric drill-down) + white center (Rooth AI conversation with drag/focus/expand on metrics) + white RHS (rail + expanded tab for Alerts/Downloads/Actions). Full-screen MetricDetailView renders L1-L7 contract chain + hero value + sparkline + source provenance per metric. /beyond/opt1-4 experimental routes removed; dashboard pages preserved under src/pages/v2/ per D353 will-restore rule.
