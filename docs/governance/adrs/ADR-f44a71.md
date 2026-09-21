---
uid: DEC-f44a71
title: "Tenant Readiness Program — execution & sequencing (Kaveri MLS 15-25 walk; route (a) source-bounded DSO fix)"
description: "Locks HOW the Tenant Readiness Program executes the Kaveri MLS 15-25 walk (not the readiness definition, which is DEC-33d436): spine, route (a) for the MLS-23 gate (source-bounded, with shared-contract gating), governed-per-rung discipline, AWS-Shared v1 scope, and the grounded findings."
status: decided
date: 2026-09-21T04:27:25.324Z
project: bc-core
domain: platform
subdomain: tenant-readiness
focus: lifecycle
---

# Tenant Readiness Program — execution & sequencing (Kaveri MLS 15-25 walk; route (a) source-bounded DSO fix)

## Context

Platform Readiness & Legibility (DEC-33d436/D606) split readiness two-layered along the Metric Lifecycle States ladder (DEC-c9e623/D389): PLATFORM readiness = MLS 01-14 / lanes L1-L9 (CLOSED 2026-09-21), TENANT readiness = MLS 15-25 / lane L10. DEC-958d3a/D613 reclassified the single continuous *real* end-to-end run out of platform readiness (provable compositionally on a fixture) into tenant readiness, because it is inseparable from the interlocked governed onboarding stack. This ADR does NOT re-decide the readiness DEFINITION (that is DEC-33d436); it locks HOW the Tenant Readiness Program executes the Kaveri walk.

## Decision

1. **Spine = MLS 15-25, executed via lane L10 for one real tenant (Kaveri Precision Components) on the lc5 Odoo world.** The destination is a trusted, evidenced DSO KPI in bc-portal via account.move → journal_entry → DSO — end-to-end, fail-closed, no fixture. SSOT = bc-docs/docs/implementation/tenant-readiness-program.md.

2. **The MLS-23 gate (no active metric is evaluable over real canonical objects — attributed to TSK-afd7ff / DEC-958d3a) is resolved by route (a): a Kaveri-led / source-bounded DSO/journal chain repair** — re-pin the OC / close the operand-projection gap for the Kaveri source specifically — NOT route (b), a corpus-wide metric fix (which stays parked as TSK-afd7ff). Rationale: route (a) is the leanest thing that makes DSO produce a real snapshot for Kaveri (the proof), and keeps the corpus-wide remediation as its own parked thread. **Impact boundary (not inherently tenant-isolated):** CC/OC selection is platform-registry-wide — `CoCandidateReader.pickGrainCc` and `MetricChainReverseWalkService` select the single active CC by grain from the **platform** registry; there is no tenant-scoped CC selection. Therefore **any change to a shared OC/CC** (re-pin or operand projection) is **gated** on downstream-consumer impact review + certification/activation review + provisioning-fanout review, **unless** a supported tenant-isolation mechanism is used. Route (a) may **not** be asserted as tenant-only or reversible merely because Kaveri is the first run. Ceremony scales to consequence.

3. **Every rung is a governed step with its own foundation gate.** All writes go through governed services (POST /tenants, the `schema-provisioner` onboard endpoints / tenant-metric-binding as-built route, provisioning worker, admission/resolution/evaluation); nothing is hand-seeded past a cert gate; no DB row hand-edits; each rung transition is verified against substrate, not asserted. **MLS-14 readiness for the chosen metric is a verified prerequisite** to entering MLS-15+ (not merely a chain-status refresh "intended to read true"). DBCP-with-consent is enforced (the Platform DB Foundation session is WIP — no DBCP without their consent).

4. **Scope: AWS-Shared tier only in v1; BYO-DB / BC-Agent / AWS-Separate flows and unhonored preference fields are HELD** (per the 2026-09-09 coordination; cited as **DEC-568d0b/D615, publication/acceptance PENDING** — that record is not present in the reviewed docs tree, so it is referenced as pending authority, not an accepted immutable record). The program consumes DB Foundation's verified POST /tenants contract and its deferred W2 items (tenant SoT + upgrade path, onboarding-record through the spine, Free package seed, tenant_infrastructure population, readiness projection, the PR #41 F3 target-preview contract) — convergence at MLS-20 is a W2 dependency, not a block.

5. **Grounded findings (2026-09-21) are program tasks, not assumptions:** **F-TR-1** — the D389 MLS-16 signal name `tenant.fiscal_calendar_config` (a platform table) does not exist, but this is a **locator move, not missing machinery**: per ADR-f02230/D368 the config lives in the **tenant DB** as `organization.fiscal_calendar_config` (Drizzle schema + `FiscalCalendarService` tenant lookup + tenant-skeleton DDL present at bc-core `53bb1115`; relation exists, 0 rows, in `tbc_probe_unit4_dev`); remaining work = authoring Kaveri's config rows. **F-TR-2** — the MLS-19 as-built binding path exists (`schema-provisioner` `onboard-connector`/`onboard-metric`, 202 + worker-readiness poll, MCF reverse-walk; `nightly-reconcile` removed); per-rung gate completeness + MLS-21/22/23 tenant probes remain unverified. **F-TR-3** — the MLS-23 gate is attributed to TSK-afd7ff / DEC-958d3a and not independently re-reproduced this session. These are verified/closed as the walk reaches each rung.

## Sequencing

Thin-real-slice first: confirm lc5 up → provision Kaveri (MLS-15) → wire Odoo source (MLS-17/18) → author Kaveri's tenant-DB `organization.fiscal_calendar_config` (MLS-16; configuration, not a build — F-TR-1) → bind via the as-built `schema-provisioner` onboard route (MLS-19), **after** correcting the stale `tenant-metric-binding.md` SOP (it still mandates the removed `nightly-reconcile` + direct-UPDATE rollback) → provision fact tables via owner-worker (MLS-20) → admit + resolve (MLS-21/22) → route (a) makes DSO evaluable, subject to the Decision 2 shared-contract gating (MLS-23) → evidence (MLS-24, gated by D575) → portal KPI (MLS-25). **Verify** MLS-14 readiness for the chosen metric (refresh chain-status TSK-aaa6ae, then confirm against substrate — do not infer readiness from the refresh alone).

## Consequences

Anchor TSK-d73f01. Stand-up session SES-b5c14b. Full platform-readiness discipline (session protocol, foundation gate per rung, SOP compliance onboarding/tenant-onboarding.md + tenant-metric-binding.md — the latter to be corrected to the as-built route per F-TR-2, auditor-PR gate, RUN-THE-APP). This is an execution/sequencing lock; amendments follow the Decision and Change Procedure.
