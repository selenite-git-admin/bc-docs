---
uid: DEC-a67bae
title: "Locked lane taxonomy — L1–L10 boundaries, not-a-lane register, retirement list (amends D581)"
description: "Locks the D581 onboarding lanes to strict one-lane-per-surface boundaries, registers what is not-a-lane and what is retired; no audit runway (certification is an L6 capability, not a lane)."
status: decided
date: 2026-08-24T05:41:42.464Z
project: platform
domain: sources
subdomain: onboarding-runway
focus: scoping
---

# Locked lane taxonomy — L1–L10 boundaries, not-a-lane register, retirement list (amends D581)

## Context

Mid-journey changes had eroded confidence in the D581 onboarding lanes; the operator asked to clean scope BEFORE building any tooling over it — tooling on an unclear taxonomy only automates the confusion. A grounded enumeration (not memory) showed the platform is three macro-domains and the lanes correctly model only onboarding; the "overlapping/unclear small lanes" feeling traced to two knots (the 3-generation metric surface; the 4-way integrity tangle) plus retired debris (`metric_audit.*`) masquerading as a live gap. Verification against ground TWICE overturned confident-but-wrong findings — the proposed "audit runway" (retired substrate) and an L7 "drift" that was really dual-baseline divergence — which is itself the argument for the downstream machine object: it can only earn trust if every probe verifies against a single authoritative source. Hence the dual-DDL-baseline (TSK-237f9d) is the true root-cause blocker and gates the machine-object build (Phase M).

## Decision

Amends DEC-ce4314/D581 (does NOT supersede it — the organizing decision remains valid). From a grounded coverage map (every bc-core @Controller + platform DDL table + devhub tool, diffed against the 10 lane READMEs), the onboarding runway scope is locked:

1. LANE SET = L1–L10, unchanged in count. No 11th lane. Assignment rule = STRICT ONE-LANE-PER-SURFACE (a controller/table belongs to exactly one lane; a surface that appears to serve two lanes is a signal to split responsibility, not to dual-tag).

2. CERTIFICATION IS NOT A LANE. External metric-audit was retired by DEC-c48b0f/D541; its in-process replacement — certification (`mcf.certification_record`; panel-2 certifies the frozen package before activation) — is a CAPABILITY of L6 / the metric-lifecycle, not an onboarding artifact family. There is NO audit runway.

3. NOT-A-LANE REGISTER (out of scope, per D581's own carve-out — these are what lanes depend on / run on / are governed by): runtime & execution (`/t/*` engines, tenant `progression`/`fact`/`evidence`); privacy & retention (`operations.*` nullification/PII/DSAR); platform masters & dims (`master.*`); platform ops & admin (`admin/*`, support, pricing, infrastructure, test_bench, schema-provisioner, telemetry).

4. RETIREMENT LIST (dead code to remove, NOT to lane): (a) legacy pre-MCF `metric.*` schema + ctrls `metric-catalog` / `metric-catalog/definitions` / `metric-definitions` / `metric-reference` (superseded by L6 MCF + L8 directory); (b) retired external-audit `metric_audit.*` schema + `mcf/metric-audit-*` ctrls (D541 — MUST carve out the still-live certification substrate before any drop; controller-by-controller live-vs-dead split, not a blind schema drop); (c) dead SAP source-reference ctrls `onboarding` + `sap-reference/*` (D564 Odoo-only; SAP stays only in the D525 audit lane).

5. Per-lane boundary corrections recorded; 5 candidate doc≠code drift findings adjudicated — 2 real fixes applied to READMEs (L10 envelope→progression per D369; L5 resolve-canonical→`t/ccv2-resolve`), 2 RECLASSIFIED to the dual-DDL-baseline root cause (L7 `runtime.connection`, L9 `contract.chain_status` — not doc errors but baseline divergence), 1 annotation (views cited as tables).

## Authority artifacts

In `barecount-devhub`:
- `artifacts/lanes/LOCKED-LANE-TAXONOMY-2026-08-24.md` — this decision, in full.
- `artifacts/lanes/COVERAGE-MAP-lane-scope-2026-08-24.md` — the grounded evidence.
- `artifacts/lanes/DESIGN-lane-framework-machine-governed-2026-08-24.md` — the machine-object build that will MODEL this taxonomy (Phase M), gated on the DDL-baseline fix TSK-237f9d.

## Related

- DEC-ce4314 / D581 — the organizing decision this amends (10 source-classified lanes).
- DEC-c48b0f / D541 — retired external metric-audit → certification.
- D564 (SAP retirement, Odoo-only) · D525 (SAP audit lane) · D369 (envelope→progression).
