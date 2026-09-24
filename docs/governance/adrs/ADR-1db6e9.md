---
uid: DEC-1db6e9
title: "Rooth: backend homed in bc-core as a config-gated module; UI stays in bc-portal"
description: "Rooth (role-pivoting AI conversation) backend lives in bc-core as a self-contained module, not its own repo; UI in bc-portal."
status: proposed
date: 2026-09-19T03:44:44.952Z
project: platform
domain: platform
subdomain: architecture/service-topology
focus: runtime
---

# Rooth: backend homed in bc-core as a config-gated module; UI stays in bc-portal

> **Status reconciliation (2026-09-24, bc-docs#59; TSK-0f1782): `proposed`, in both this file and the DevHub registry.**
> - **What happened:** the registry recorded this decision at 2026-09-19 03:44 UTC and flipped it to `decided` at 03:46 UTC, two minutes later.
> - **Why `decided` is not supported:** the flip is outside any DevHub session, and there is no review, ratification or approval record. The decision's own text still reads "Status: proposed direction … nothing is built". There is no `src/rooth/` in bc-core `main`.
> - **Correction:** the registry is corrected to `proposed` to match this evidence. This is explicit, recorded here and in TSK-0f1782.
> - **How it becomes `decided`:** by an explicit operator ratification of the topology (points 1–5), recorded with its evidence. Rooth's own design pass remains a prerequisite to any code.

## Context

Applying BareCount's de-facto repo-creation test (reconstructed from precedent; a canonical written rule may exist in bc-docs, unverified this session): a new repo is justified only with an independent release lifecycle, more than one real consumer, a different runtime/deploy target or tech discipline, AND an operational cost that is outweighed by those. Rooth fails the test today: a single real consumer (bc-portal), the same Node/TS runtime, and no independent-deploy payoff.

The decisive precedent is bc-ai (DEC-ffee4e / D483): a standalone AI service intended to serve all BareCount apps was RETIRED and folded in-process into bc-core because the separation cost cross-process coupling (including panel runs dying on bc-core restart) without paying for itself. The default is in-process; carve out only on a durable reason, per the bc-db (DEC-826390) and DevHub (DEC-376c9c) shapes. Homing Rooth in bc-core also keeps it co-located with the metric-knowledge / definition / tenant data it must read, avoiding the per-query cross-process hop that hurt bc-ai. The modularity contract preserves a cheap future extraction if the criteria ever flip, honouring the bc-ai lesson without paying its cost now.

Modelling the role signal as a governed bc-core reference (rather than the current per-metric stakeholders blob) is both a maintainability fix — per-metric hand-curated lists already drift, e.g. a KPI pack code written into stakeholders — and a topology fix: consumer and reference data sit in the same place with a clean seam, and stakeholders is confirmed as role/title labels (not personal data), resolving its PII over-classification.

## Decision

Rooth is an AI conversation feature that tailors framing to the VIEWER'S ROLE (e.g. CFO vs Credit Manager), never to named individuals.

1. Rooth's BACKEND is homed in bc-core as a single, self-contained, config-gated module (src/rooth/), NOT its own repository.
2. Rooth's UI stays in bc-portal (where it was designed) and reaches the backend through a thin bc-core API.
3. Modularity contract, so a future carve-out is a lift-out rather than a rewrite: (a) one public service/controller surface under src/rooth/, nothing outside imports its internals; (b) it reads metric-knowledge / metric definitions / tenant data through the EXISTING repositories and providers — no raw SQL and no private DB connection of its own; (c) a ROOTH_* environment gate mirroring BCF_PANEL_MODE for enable/disable and future out-of-process pointing; (d) it depends only on stable published surfaces, not other modules' internals.
4. The role signal Rooth consumes is a GOVERNED bc-core REFERENCE — a role vocabulary plus a role-to-function/subfunction relevance map — not a per-metric free-JSON field. Consequently metric.metric_knowledge.stakeholders (and the mcf.metric_knowledge_profile.stakeholders_json sibling) are declassified from operations.pii_field_registry (role labels are not personal data) and retired as per-metric fields in favour of the derived reference. That declassification/retirement is a separate schema/seed change requiring operator approval and is NOT part of this decision's execution.
5. Re-evaluate the home if Rooth later gains a second real consumer beyond bc-portal, needs a different runtime/deploy target, or acquires an independent release lifecycle whose value outweighs a separate deploy boundary — at which point a carve-out (bc-db / DevHub shape) earns its keep.

Status: proposed direction. Rooth still needs its own design pass (conversation contract, role-vocabulary source, read API) before any code; nothing is built.
