---
uid: DEC-f44a71
title: "Tenant Readiness Program — execution & sequencing (Kaveri MLS 15-25 walk; route (a) tenant-scoped DSO fix)"
description: "Locks HOW the Tenant Readiness Program executes the Kaveri MLS 15-25 walk (not the readiness definition, which is DEC-33d436): spine, route (a) for the MLS-23 gate, governed-per-rung discipline, AWS-Shared v1 scope, and the grounded findings."
status: decided
date: 2026-09-21T04:27:25.324Z
project: bc-core
domain: platform
subdomain: tenant-readiness
focus: lifecycle
---

# Tenant Readiness Program — execution & sequencing (Kaveri MLS 15-25 walk; route (a) tenant-scoped DSO fix)

## Context

Platform Readiness & Legibility (DEC-33d436/D606) split readiness two-layered along the Metric Lifecycle States ladder (DEC-c9e623/D389): PLATFORM readiness = MLS 01-14 / lanes L1-L9 (CLOSED 2026-09-21), TENANT readiness = MLS 15-25 / lane L10. DEC-958d3a/D613 reclassified the single continuous *real* end-to-end run out of platform readiness (provable compositionally on a fixture) into tenant readiness, because it is inseparable from the interlocked governed onboarding stack. This ADR does NOT re-decide the readiness DEFINITION (that is DEC-33d436); it locks HOW the Tenant Readiness Program executes the Kaveri walk.

## Decision

1. **Spine = MLS 15-25, executed via lane L10 for one real tenant (Kaveri Precision Components) on the lc5 Odoo world.** The destination is a trusted, evidenced DSO KPI in bc-portal via account.move → journal_entry → DSO — end-to-end, fail-closed, no fixture. SSOT = bc-docs/docs/implementation/tenant-readiness-program.md.

2. **The MLS-23 gate (no active metric is evaluable over real canonical objects, TSK-afd7ff) is resolved by route (a): a tenant-scoped DSO/journal chain fix** — re-pin the OC / close the operand-projection gap for the Kaveri source specifically — NOT route (b), a corpus-wide metric fix. Rationale: route (a) is the leanest thing that makes DSO produce a real snapshot for Kaveri (the proof), is tenant-scoped and reversible, and keeps the corpus-wide remediation (TSK-afd7ff) as its own parked thread. Ceremony scales to consequence.

3. **Every rung is a governed step with its own foundation gate.** All writes go through governed services (POST /tenants, tenant-metric-binding, provisioning worker, admission/resolution/evaluation); nothing is hand-seeded past a cert gate; no DB row hand-edits; each rung transition is verified against substrate, not asserted. DBCP-with-consent is enforced (the Platform DB Foundation session is WIP — no DBCP without their consent).

4. **Scope: AWS-Shared tier only in v1; BYO-DB / BC-Agent / AWS-Separate flows and unhonored preference fields are HELD** (per the 2026-09-09 coordination, re-affirmed as DEC-568d0b/D615). The program consumes DB Foundation's verified POST /tenants contract and its deferred W2 items (tenant SoT + upgrade path, onboarding-record through the spine, Free package seed, tenant_infrastructure population, readiness projection, the PR #41 F3 target-preview contract) — convergence at MLS-20 is a W2 dependency, not a block.

5. **Three grounded findings (2026-09-21) are program tasks, not assumptions:** F-TR-1 the DEC-c9e623 MLS-16 signal table tenant.fiscal_calendar_config does not exist (only master.dim_fiscal_calendar); F-TR-2 MLS-19 activation service + MLS-21/22/23 tenant probes flagged not-yet-existing in D389 are unverified; F-TR-3 MLS-23 is gated by TSK-afd7ff. These are verified/closed as the walk reaches each rung.

## Sequencing

Thin-real-slice first: confirm lc5 up → provision Kaveri (MLS-15) → wire Odoo source (MLS-17/18) → resolve MLS-16 fiscal signal → bind (MLS-19) → provision fact tables via owner-worker (MLS-20) → admit + resolve (MLS-21/22) → route (a) makes DSO evaluable → snapshot (MLS-23) → evidence (MLS-24, gated by D575) → portal KPI (MLS-25). Refresh chain-status (TSK-aaa6ae) so MLS-14 readiness for the chosen metric reads true.

## Consequences

Anchor TSK-d73f01. Stand-up session SES-b5c14b. Full platform-readiness discipline (session protocol, foundation gate per rung, SOP compliance onboarding/tenant-onboarding.md + tenant-metric-binding.md, auditor-PR gate, RUN-THE-APP). This is an execution/sequencing lock; amendments follow the Decision and Change Procedure.
