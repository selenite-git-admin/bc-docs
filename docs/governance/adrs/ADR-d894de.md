---
uid: DEC-d894de
title: "Workflow Governance: SOP + Programmatic Flow + UI Control Plane"
description: "All workflows require SOP + programmatic flow + UI control plane. No black boxes."
status: implemented
subdomain: governance
focus: workflow-three-leg
date: 2026-04-03T15:30:46.670Z
project: platform
domain: governance
migrated_from: legacy v2 archive
---

# Workflow Governance: SOP + Programmatic Flow + UI Control Plane

## Context

Prior sessions ran bulk scripts with no UI visibility, producing unverifiable data that had to be flushed. The operator must always see what is happening and be able to intervene. SOPs are foundation documents, not ad-hoc playbooks.

## Decision

Every system workflow must have three components: (1) a foundation SOP defining the rules, (2) a programmatic implementation that does the work, (3) a UI control plane that triggers, monitors, and shows results. No workflow may execute without UI visibility. Both programmatic and manual paths follow the same SOP. No black boxes.
