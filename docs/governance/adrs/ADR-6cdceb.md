---
uid: DEC-6cdceb
title: "bc-portal surface split — Beyond (viewing) + Settings/Workspace + Settings/Data Infra (plumbing)"
description: "bc-portal has three top-level surfaces: /beyond for viewing/insight, /settings/workspace for tenant admin, /settings/data-infra for data plumbing. Greenfield design, no retrofit."
status: implemented
subdomain: bc-portal
focus: information-architecture
date: 2026-04-19T15:03:15.324Z
project: bc-portal
domain: bc-portal
supersedes: DEC-04dade
migrated_from: legacy v2 archive
---

# bc-portal surface split — Beyond (viewing) + Settings/Workspace + Settings/Data Infra (plumbing)

## Context

The audit walk-through established that most legacy pages are "traditional SaaS data product" shaped — tab-heavy dashboards that compete with Beyond and dilute the thesis. A full cull is tempting but incomplete: some pages are genuine operational workflows (add connection, manage users, set policies) that Beyond is a bad fit for — those need forms and tables, not a canvas.

The three-surface split resolves this by category:
- Beyond handles *insight* (the thesis)
- Settings/Workspace handles *tenant admin* (forms, governance)
- Settings/Data Infra handles *platform plumbing* (connections, policies, compliance)

### Amendment 2026-04-19 — deferred questions locked

1. **Interventions** — mostly live inside Beyond as insight-driven action surfaces. Detailed design deferred to when that surface is built. No standalone `/interventions/*` top-level surface.

2. **Evidence / Lineage** — inside Beyond's trust-chain per metric. No global/cross-cutting audit surface. Nobody goes looking for evidence at the global level; it's only meaningful as "why should I trust THIS number". `/evidence/*` and `/lineage/*` standalone routes dissolve into Beyond's `MetricDetailView`.

3. **Canonical data / contracts** — not shown as a standalone surface. Already visible per-metric via the contract chain inside Beyond's trust surface. A standalone canonical-data browser would be architecture show-off with no tenant use case. `/canonical-data/*` routes (7 pages) dissolve. Settings/Data Infra is pure ops: connections, retention, residency, policies, backup, compliance, source registration, reader catalog.

**Net effect on surface inventory:**
- Beyond absorbs: viewing/insight + evidence/lineage (per-metric) + intervention action surfaces
- Settings/Workspace absorbs: all tenant admin
- Settings/Data Infra absorbs: pure plumbing (no canonical-data browser)
- Deletes: interventions standalone, evidence/lineage standalone, canonical-data standalone

Supersedes D355 (bc-portal architecture) for the surface/route shape. Refines D358/D360 (Beyond scope): Beyond is constrained to *viewing + provenance*, not operational workflows.

## Decision

bc-portal is organized into exactly three top-level surfaces:

1. **`/beyond`** — viewing / insight surface ONLY. Metric display, drill-down, trust chain, alerts, actions-derived-from-insight. Read-mostly. The "post-dashboard canvas" thesis (D358) stands; this decision *constrains* Beyond so it doesn't absorb operational workflows.

2. **`/settings/workspace`** — tenant administration. Org profile, business functions, teams, users & seats, subscription, security, fiscal context, exchange rates. Absorbs the current `/workspace/*` pages.

3. **`/settings/data-infra`** — data plumbing. Connections, source registration, reader catalog, retention, residency, policies, backup, compliance. Absorbs current `/data-sources/*` and `/data-infra/*`. Does NOT include a canonical-data browser — contract chain is exposed per-metric inside Beyond.

Anything that doesn't fit one of these three surfaces does not belong in bc-portal and requires a separate decision.

**Design method:** greenfield UX spec first. Design fresh from user mental model against the locked Design System (shadcn/ui canonical per D355). Reference old pages for domain knowledge (fields, workflows, edge cases) but do NOT copy layouts. Data files (connector configs, retention taxonomies, intervention categories, permission maps, master data) are salvaged and reused as reference; UI is rebuilt.

**Enabler:** no current page is wired to bc-core. Retrofit cost is zero. Cleanest possible moment to lock surface boundaries.
