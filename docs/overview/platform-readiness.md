---
title: Platform Readiness & Legibility — Overview
status: closed
date: 2026-09-19
anchor_task: TSK-4b2404
detail: implementation/platform-readiness-program.md
related: overview/platform-db-foundation.md
---

# Platform Readiness & Legibility

**Destination:** establish the platform engine conformance needed to produce **trusted**
metrics through the governed runway. Platform readiness is proven **compositionally**:
per-boundary CI proofs, fail-closed execution-plane seams, and evaluation/evidence E2E
integration coverage. The single continuous real-source run remains **tenant-readiness
milestone #1** (Kaveri/lc5); this closure does not claim that run has occurred.

**What "proven" means (DEC-958d3a/D613, 2026-09-21):** the four criteria remain streamlined ·
governed · documented · proven-once-E2E. Platform readiness satisfies the fourth criterion
with compositional evidence. Tenant readiness requires the continuous run through full
governed onboarding and depends on the Platform DB Foundation tenant substrate.

**Historical definition (2026-09-19, superseded):** a continuous fixture/sandbox traversal
was the platform proof, followed by a thin real-source demo slice. Amendment 2 replaces
that proof with compositional evidence and assigns the continuous run to tenant onboarding.

**Amendment 2 (2026-09-21, DEC-958d3a/D613):** engine-conformance is satisfied **compositionally** (bc-core CI on `main` green — `e6b-db-integration` + gates + vitest), **not** by a single continuous run; that continuous run is **reclassified to tenant-readiness milestone #1** (the Kaveri onboarding) because it is inseparable from the interlocked governed stack (cert-gated activation + provisioning fanout + owner worker). The platform-readiness gate is now the no-black-box doors + ADR-hygiene. **✅ CLOSED 2026-09-21:** L9 chain-audit door shipped (bc-core #808 + bc-admin #53, live-verified), S2 users door deferred (solo-founder), ADR-hygiene machine-clean (`supersessionIssues=0`) + punch-list triaged — **platform readiness is closed on engine-conformance**. The single continuous real run is tenant-readiness milestone #1 (the Kaveri onboarding), downstream. See the detail doc's close banner + DEC-958d3a.

**The platform functions (the stable spine):**
- **Shared:** S1 Auth · S2 User/access · S3 Tenant lifecycle · S4 Pricing · S5 Operator console
- **Runway (10 lanes):** L1 Source Catalog … L10 Tenant Onboarding (LOCKED, DEC-a67bae/D590)
- **Runtime & cross-cutting:** Runtime engine · Evidence/audit · Tenant self-service · **A1 Action/Intervention** *(design pending)*
- **Parked as cosmetic:** design-system/visual-language → a future dedicated UI refactoring program (not a function).

Each function is scored **backend / DB / UI** and carries its governing ADRs with real status —
a function with thin/no ADRs is itself a finding. Full matrix in the detail doc.

**Historical study snapshot (2026-09-19, before Amendment 2):** the metric authoring/certification
path is green (L1–L3, L6, L7). The **runtime execution-plane seam class is CLOSED** — all three
silent coupling seams merged to bc-core `main` (fail-closed, disposable-DB CI regression). What
remains on Track R: E6-B's first-*observed* evidence emit (FND-VI, **deferred** — rides on a real
metric run + operator-only auditor-store health) and the by-design fail-open follow-ups.
Legibility gaps (missing operator doors: L9 chain-audit, S2 users; the L8 Metric Directory UI shipped, PR #45) are
co-requisite, *not* cosmetic. L10's onboarding lane is green; its four operational tabs are
reclassified to S5 (deferred). S4 pricing is deferred-by-decision (v1 flat band, no plan binding)
and S2 RBAC unbuilt — neither blocks a compute demo.

**Three cuts of the space** (kept distinct for legibility): **4 tracks** (work axis — T closed /
R engine-conformance met compositionally / L disposition recorded in the closure / S deferred);
**the functions** (what the platform does); **design vs
execution plane** (DEC-c48b0f). A **unit ledger** with a mandatory design/execution intake gate
ties each unit of work to a function and a piece of the distance-to-destination.

**Current disposition and next gate (2026-09-21):** platform readiness is recorded as closed
on compositional engine-conformance, with L9 shipped, S2 users deferred, and ADR-hygiene
machine-clean plus the punch-list triaged. **Tenant readiness is next:** full Kaveri/lc5
onboarding (TSK-d73f01) must produce the continuous real-source run and first-observed E6-B
evidence emit, subject to the governed onboarding and auditor-store health prerequisites.
The deeper ADR sweep and by-design fail-open follow-ups remain tracked work.

**Tenant readiness progress (2026-09-26):** checked read-only against the live databases, the
first continuous real-source run has happened on Kaveri. On 2026-09-23, 10,744 Odoo journal
entries were observed, resolved to canonical rows and evaluated to one accepted snapshot
(`total_journal_entries` = 212 for FY2026-27/P05). This is **not yet tenant readiness**:
- the periods came from a catch-all fiscal calendar, not per legal entity (D623 is fixing that);
- the metric is not yet DSO;
- canonical resolution for the active contract has been refused since 2026-09-26 (open regression
  TSK-387779, fixed by D623 7c-c);
- its one evidence emit was written by the superuser, which does not count for proof (MLS-24);
- nothing has been shown in the portal.

The per-rung state, the queries and the log live in the tenant SSOT,
[implementation/tenant-readiness-program.md](../implementation/tenant-readiness-program.md)
§3.0 and §8. The live roadmap is DevHub plan PLN-31c4a1.

**Converges with** the [Platform DB Foundation](platform-db-foundation.md) program (bc-db,
TSK-cc348a), which productionizes tenant onboarding at scale; the two meet at the Kaveri demo
milestone.

→ Full detail — functions, per-function ADRs, the readiness matrix, the seams, the unit ledger,
and the punch-list: **[implementation/platform-readiness-program.md](../implementation/platform-readiness-program.md)**.
