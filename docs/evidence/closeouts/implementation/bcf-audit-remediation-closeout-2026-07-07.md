---
title: BCF Audit Remediation Program — Closeout
type: implementation
domain: contracts
authority: informative
date: 2026-07-07
status: closed
related:
  - DEC-14f5b6
  - DEC-1fbaf1
  - DEC-61850f
  - DEC-02f5a9
---

# BCF Audit Remediation Program — Closeout (2026-07-06 → 2026-07-07)

One-day arc: full-sweep BCF audit → 13-gap register → complete remediation. Working record
lives in barecount-devhub (`.claude/bcf-audit-2026-07-06.md` + session change records
SES-f08fa5 → SES-63b9ea); this closeout is the durable pointer.

## What the audit found (SES-f08fa5)

Five-dimension full sweep (completeness / coverage / uniqueness / clarity / accuracy) over the
live registry (136 entities, 612 true-active BCs at audit time) plus doctrine grounding
(BO-BF → SDA → DEC-02f5a9 Registry evolution). Register G1–G13. Three findings were
same-day-corrected as `lifecycle_state`-filter artifacts — the counting hazard that later
became G10's fix.

## What shipped, where

| Gap | Disposition | Vehicle |
|---|---|---|
| G3 classification | CLOSED — all 136 entities carry `family_code` (seed-metric function vocabulary); demand-linkage view live | bc-core PR #420 + R4 batch; view artifact in devhub `.claude/` |
| G4 review queue | CLOSED — disposition surface (4 write-once columns + endpoint) + 481/481 backlog disposed; rejection-log finding explained (legacy BF-era table; B6 D2 parks deliberately) | PR #420 + #421-adjacent backfill |
| G5 value sets | CLOSED — 10 status BCs backfilled from governed prose; corpus: 0 status/strategic_filter without VS | BCV surface (PR #421) ceremony |
| G6 effective-date drift | CLOSED — 7/7 supersessions; 3 occurrence atoms authored (`filing date`, `submission date`, `assessment date`) | SES-190c83/7f4830 ceremonies |
| G7 identity | CLOSED — 0 of 136 entities without identity-bearing concepts (Employee + 6 CRM entities; 4 party-key atoms) | panel + operator-direct ceremonies |
| G8 dup-defense | CLOSED — intake pre-check refuses substrate duplicates before Maker spend | PR #420 |
| G9 role coherence | CLOSED — 7 role alignments + admission-time identity_role × semantic_role gate | PR #420 gate + #421 ceremony |
| G10 lifecycle encoding | CLOSED — withdrawal transitions state; 23 rows backfilled; coherence CHECK validated | main `11e3591` (closes TSK-737fbf) |
| G2 measurement semantics | CLOSED — DEC-14f5b6 (D496) decided → **implemented**: `measure_class` + `context_concept_id` on BC versions; currency-like-unit gate; 8 currency siblings authored; **86/86 amount-role BCs classified, 0 monetary without context** (line entities reference the parent document's currency concept) | PR #422 (`e493237`, closes DEC-14f5b6) |
| G1 CC/OC concept stamping | OPEN BY DESIGN — sequenced behind C0 (TSK-50a2b6) + F1-B1 closure; unchanged from DEC-a6258b/DEC-4a17e0 deferral | — |
| G11 aliases | DEFERRED — until second-source onboarding forces it | — |
| G12 thin templates | DEFERRED — editorial enrichment batch, low severity | — |
| G13 reference authoring | UNCHANGED — DEC-d468e2 deferral stands | — |

New governance surfaces (all bc-core, merged): concept-version-amendment recommendation
surface (the BCV path — descriptive amendments under the same concept_id), panel-run
disposition (write-once), classification passthrough on entity versions, mandatory
`businessFunctionCode` on B6 runs (panel-emitted value always wins), explicit
`semanticRole`/`canonicalValueSet` on the operator-direct BC authoring surface.

## Substrate end-state (2026-07-07)

136 active entities (all classified, all identity-bearing) · ~630 active BCs ·
173 active characteristics · 0 status/strategic_filter BCs without value sets ·
0 amount-role BCs without measure_class · 0 monetary BCs without currency context ·
0 undisposed OPERATOR_REVIEW panel runs · effective-date corpus drift-free.

## Named tails (tracked, none blocking)

Panel-rubric REQUIRED amount-declaration (prompt-version bump; roster calibration-locked) ·
UOM-sibling wave for 11 quantity_uom BCs · ~6 fixed_unit NULL unit anchors (supersession) ·
PE-MC mixed-currency engine gate (TSK-e2a32b — now computable from substrate) ·
pending_action review-queue subject refinement (166 rows) · seed-side `function_code`
hygiene (1,186 NULL — mcf, not BCF) · operations/executive vocabulary waves per the
demand-linkage view.
