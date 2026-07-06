---
uid: DEC-3aa336
title: "MCF code layout — mcf/ is the consolidated home; two strays move in, five look-alikes deliberately stay out"
description: "mcf/ affirmed as consolidated MCF home; metric-authoring/ + mcf-readiness-bridge move in; intake-queue (shared), mc-envelope-governance (legacy), abc/, and sunset-headed metric-* files deliberately stay out"
status: implemented
date: 2026-07-04T03:46:41.913Z
project: bc-core
domain: platform
subdomain: code-layout
focus: refactor
---

# MCF code layout — mcf/ is the consolidated home; two strays move in, five look-alikes deliberately stay out

## Context

Operator asked whether mcf* should get the D484 treatment while context was warm. Ground inventory showed the premise differs: bcf had 9 homeless siblings; mcf already has its home and the apparent sprawl is mostly legacy-stack surface or shared substrate that would be MISfiled by a naive move. Scope kept to the two true strays (~7 files, 3 importers) — the ADR records why the rest stays so the question is not re-litigated at the next layout itch.

## Decision

Companion to DEC-9428e0 (D484). src/registry/mcf/ is affirmed as the single consolidated home of the live MCF stack — no internal reshuffle (the M12 panel paths and prompt assets are calibration-locked surfaces; the folder boundary already does its job).

Two genuinely-MCF strays move in: (1) src/registry/metric-authoring/ (the M12 metric-draft-review panel-run writer module) → src/registry/mcf/metric-authoring/; (2) src/registry/mcf-readiness-bridge.service{,.spec}.ts → src/registry/mcf/.

Five look-alikes deliberately STAY OUT, and this negative space is the substance of the decision: intake-queue.* remains at the registry root because it is the SHARED intake substrate (MCF intakes AND BCF C8 both stage through it — homing it under mcf/ would misstate ownership); mc-envelope-governance/ remains a peer because it governs the LEGACY metric_definition envelope surface (DEC-889238/DEC-af8247 era) and its fate belongs to the legacy-bridge sunset, not to live-MCF layout; abc/ remains a peer as a distinct panel family with its own future homing decision; the ~20 legacy metric-* root files (metric-definition/catalog/binding/funnel/readiness/knowledge/reference) are sunset-headed and will be deleted wholesale — relocating dying code is churn without value; and the 100+ remaining loose files at the registry root are a separate, unfiled cleanup decision.
