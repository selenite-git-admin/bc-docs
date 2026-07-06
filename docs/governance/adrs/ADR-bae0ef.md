---
uid: DEC-bae0ef
title: "IC Simplification — Remove action_templates, Single Intervention with Numeric Target"
description: "IC simplified: no action_templates, no intervention type menu. One intervention per metric per cycle with numeric target. IC governs rules (who/how long/evaluation), Action Object carries the target."
status: implemented
subdomain: body-purity
focus: master-shape
date: 2026-04-02T05:17:39.631Z
project: bc-docs
domain: foundation
migrated_from: legacy v2 archive
---

# IC Simplification — Remove action_templates, Single Intervention with Numeric Target

## Context

action_templates over-engineered the intervention. The real-world flow is: tenant decides to intervene, sets a target number, assigns an owner, waits for cycle evaluation. No template selection needed. Simpler model, fewer governance edges, matches the foundation principle that the system does not decide — the tenant's only decision is the target and the owner.

## Decision

IC body simplified. The intervention IS the action — no template menu.

**Removed:** `action_templates[]` — tenant does not select from investigate/remediate/escalate categories. They simply create one Action Object with a numeric target and an owner.

**Model:**
1. Tenant sees metric outcome → decides to intervene
2. Creates Action Object: target value (number), owner (from assignee_pool)
3. Owner works during the cycle
4. Cycle ends → system evaluates: baseline vs actual → improved/deteriorated/no_change

**Target** lives on the Action Object (runtime tenant artifact), not on the IC. Set at creation time by tenant.

IC v1 body: 5 fields — activation_mode, trigger_conditions[] (conditional), assignee_pool, closure_window, evaluation_model. The IC governs the rules around intervention (who, how long, how to evaluate), not the intervention types.
