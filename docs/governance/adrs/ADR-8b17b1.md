---
uid: DEC-8b17b1
title: "Demo estates, not pilots: few-deep flagships per (domain × geography), Odoo-base, isolated per install"
description: "BareCount's demonstration environments are permanent, lifelong-maintained demo/reference estates — few-deep flagships, one per (domain × geography), Odoo-base, isolated per install, IN-first."
status: decided
date: 2026-08-08T13:54:27.413Z
project: bc-synth
domain: sources
subdomain: sources/demo-estates
focus: strategy
supersedes:
  - DEC-076521
  - DEC-3b23de
---

# Demo estates, not pilots: few-deep flagships per (domain × geography), Odoo-base, isolated per install

## Context

Driven by the strict no-tenant-data posture: BareCount can never demo on a customer's system, so it must own realistic source systems of its own — **the demo estate is the FORCED CONSEQUENCE of that posture, not a convenience.** "Pilot" mis-frames it twice: it implies *temporary* (these never retire) and a *rehearsal before real data* (there is no "later, on real data" — by posture there never can be).

The differentiating sales asset is the **FRONT-DOOR PROOF**: a real ERP (real GL, real documents) read through published contracts (SC/AC→OC→CC→MC) with no privileged hook demonstrates the trust boundary itself — *"we can't show your data because we never touch it; here's ours, read the same way yours would be."* That is stronger than any dashboard.

**Familiarity is the game-changer, and DOMAIN familiarity beats ERP familiarity** (a real-estate CFO cares about leases/occupancy/NOI/straight-line-rent, not whether the box is Odoo) — which is why the primary axis is domain-then-geography and Odoo-as-base is acceptable: the mechanism is source-agnostic (reader flavors), so the promise extends to their ERP when the time comes.

**Few-deep beats broad-shallow** because every estate is a LIFELONG maintenance commitment; one source system collapses the reader-flavor, version-upgrade, and probed-quirk surface. **Geography is a real localization build** (VAT vs GST, IFRS vs Ind-AS, per-country chart + statutory params) — supported by the jurisdiction abstraction (generic laws over an envelope) but budgeted as work, not a copy.

**Fleet guardrails (Claude enforces going forward):**
1. Pin ONE Odoo version across the whole fleet; upgrade deliberately as a fleet op, never chase releases per-estate (drift multiplies every quirk).
2. COLD-STORAGE the estates (stop when idle, pay only EBS) and WARM-UP-TO-TODAY (roll the world forward via forward_build / D556) before a pitch, so a stopped estate never shows stale data. The runbook re-resolves the IP on each start.
3. The realism bar (NO AMI without operator review) is now a standing property of a customer-facing surface, not a one-time build gate.

Operator decided this across a 2026-08-08 conversation and offloaded ownership to Claude — recording, applying the reframe, and enforcing the guardrails.

## Decision

BareCount's demonstration environments are permanent, lifelong-maintained, customer-facing **DEMO/REFERENCE ESTATES — not pilots.**

1. **Portfolio shape: FEW, DEEP flagships**, one per (industry domain × geography), built **India-first** (manufacturing = flagship #1, then further IN domains) then EU/USA as we spread.
2. **Odoo is ALWAYS the base source system.** Multi-ERP breadth is deliberately declined on cost/effort grounds — **SAP ECC stays in the AUDIT lane (D525), never the demo lane.**
3. **Each estate runs on ONE dedicated server/installation; domains are NEVER clubbed on one machine** (also unrealistic — unrelated industries don't share an ERP install).
4. **A domain = a profile + operational generators + a metric catalog** over shared finance/statutory/forward-build/close/gate machinery (~2/3 of the machinery is domain-agnostic; the metric catalog is the real per-domain product surface).
5. **"Pilot" is retained ONLY for genuine throwaway scratch** (e.g. `scratch_anglo` DBs — build, prove, discard).
6. **Rename code strings (`pilot_ent`, `pilots/`) OPPORTUNISTICALLY** — the runbook is byte-bound and a rename mid-flight spends the governed-run grant; fix the doctrine now, the strings when a change is already in flight.

Related: D524 (pilot source = BC + Odoo), D525 (audit stays on SAP ECC), D526 (source-system docket), D556 (period close), and the source-as-backbone decision (readers function-scoped + source-agnostic).
