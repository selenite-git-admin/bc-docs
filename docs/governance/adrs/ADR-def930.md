---
uid: DEC-def930
title: "Pilot master-data framework — shared profile spine + real-system seeding adapters + living data (extends DEC-b0839a, DEC-9ec48f)"
description: "Trio data coherence = one shared profile ('mfg-in', promoted from Manufacturing Co) seeded into real Odoo/BC/SFDC via posting adapters; living catch-up continuation supersedes snapshot regeneration for real systems (exercises DEC-b0839a's parked-daemon clause); stable cross-system IDs; vendor engine = coherence gate"
status: decided
date: 2026-07-29T16:40:55.904Z
project: platform
domain: sources
subdomain: synthetic-data
focus: master-data-framework
---

# Pilot master-data framework — shared profile spine + real-system seeding adapters + living data (extends DEC-b0839a, DEC-9ec48f)

## Context

Per-system generation would produce three disconnected data islands (no shared customer), defeating cross-system meaning. The snapshot/fresh-spin model existed to hand-guarantee coherence in a simulator; real systems make that machinery unnecessary (posting engines enforce coherence natively) while a living source uniquely enables reader-runtime testing (scheduling/delta/rerun/failure). Catch-up continuation preserves the original 'freshness automatic' property and the D537 stop-when-idle cost model simultaneously. Promoting the existing proven deterministic Manufacturing Co profile avoids inventing a parallel scheme and honors DEC-b0839a's one-core-many-projections rule; verified inventory shows it is the only deep profile in the decomposed bc-sdg (six were decided, two inline exist, apex-motors machinery absent).

## Decision

Founder-decided 2026-07-29 (D537 workstream). Cross-system data coherence for the pilot source trio (Odoo + Business Central + Salesforce) comes from ONE shared profile spine, seeded into each REAL system, kept fresh by LIVING continuation — not by per-system generation and not by snapshot regeneration.

1. MODEL: Profile × Projection × Time. Profile = source-agnostic company world (master entities + correlated semantic-fact transactional stream; reuses DEC-9ec48f's profile concept and DEC-b0839a's semantic-fact seam). Projection = per-system SEEDING/CONTINUATION adapter that POSTS the profile's facts INTO the real system via its own APIs/posting engine (supersedes read-only projection views, which were simulator-era). Time = LIVING: initial deterministic multi-year seed (date-relative, seeded), then catch-up continuation.

2. LIVING DATA SUPERSEDES FRESH-SPIN-PER-DEMO for real systems. DEC-b0839a's snapshot model solved simulator problems (hand-maintained coherence, daemon cost). Real vendor posting engines ARE the coherence gate — incoherent state is unrepresentable — and a living source is the superior test surface for the UniBAT reader runtime (scheduling, delta/watermark reads, rerun idempotency, late/backdated documents, failure injection by stopping the instance). This exercises DEC-b0839a's explicitly parked daemon clause ("long-lived lab/sandbox profiles… additive, not contradictory") — additive, no supersession of DEC-b0839a for the simulator/demo path.

3. COST: catch-up continuation generator — instances stop when idle; on wake the generator posts the missed days (correctly dated, idempotent by fact_id) then resumes. Freshness automatic without regeneration or 24/7 compute. Continuous posting only during active reader-test windows.

4. PILOT PROFILE: promote bc-sdg's existing 'Manufacturing Co' SimulatorProfile to shared trio profile 'mfg-in' (already the mid-scale Indian company: INR, FY-April, 200 customers/100 vendors, deterministic seed, fiscal multipliers, settlement + adversarial edge-case dials). Add: (a) committed master-entity identity registry with stable cross-system IDs (CUST-/VEND-/ITEM-) mapped to each system's reference field — the cross-system join key, aligned to canonical/BCF identity at contract time, never a parallel platform identity; (b) source-agnostic semantic-fact stream with O2C correlation (SFDC opportunity → same-customer invoice). apex-motors is NOT resurrected (demo-storyboard profile; not present in the decomposed bc-sdg tree).

5. ADAPTER RULES: no raw SQL ever (vendor engine = coherence); idempotent by fact_id via each system's external-reference field; posting dates = fact dates (backdated-posting windows verified per system); within each system's API limits.

Spec: barecount-devhub/.claude/SPEC-pilot-master-data-framework-2026-07-29.md. Scope boundaries unchanged: no SC/AC/OC/CC or metrics (Track-C-gated); infra-green ≠ pilot-green.

## Amendment 1 — Odoo suite (ERP + CRM) as the base world engine (founder, 2026-07-29)

Odoo CRM (crm + sale, Community/LGPL) is installed alongside ERP in the same instance, and the Odoo suite becomes the **base/world system**: the generation driver writes only the funnel head (leads/opportunities + conversion + payment-behavior dials); Odoo's native flows materialize the correlated world (opportunity → SO → invoice → payment → GL on one res.partner spine) with vendor-enforced integrity — replacing the hand-authored O2C correlation stream. Downstream systems become projections of this one world: SFDC ← Odoo CRM (REST re-post), BC ← Odoo ERP documents (re-posted through BC's own engine), and — future, out of trio scope — SAP-shaped projections from Odoo GL to feed the SDG simulator/demo path. Boundaries: the neutral spine remains the master-identity registry + generation-intent driver (Odoo is the materialization engine, not the definition of truth; projections consciously map Odoo→target semantics); Odoo-as-pilot-source (D524 portability proof) and Odoo-as-base-engine are separate roles of the same instance, never conflated in claims.

## Amendment (2026-08-07, DEC-908548 / D555)

The scope boundary "no SC/AC/OC/CC or metrics (Track-C-gated)" is AMENDED per DEC-908548: SC + AC authoring for Odoo and D500 soft-references are RELEASED (Track-C condition satisfied by the D541 successor state). OC/CC + metric realization remain held. All other content of this ADR stands.
