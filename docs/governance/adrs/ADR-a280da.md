---
uid: DEC-a280da
title: "Process Auditor Agent — Gemini-Powered Independent Session Governance"
description: "Independent Gemini auditor for Claude session process compliance — SOP adherence, quality gates, claim-vs-reality cross-checks"
status: implemented
date: 2026-04-09T12:00:36.821Z
project: bc-ai
domain: governance
migrated_from: legacy v2 archive
---

# Process Auditor Agent — Gemini-Powered Independent Session Governance

## Context

Claude auditing its own work is a blind spot — same model, same biases, same failure modes. Cross-family verification (Gemini auditing Claude) catches SOP deviations, claim mismatches, skipped gates, and perfunctory self-audits that self-review cannot detect. Extends DEC-8391fd (Gemini architecture audit) to per-session governance.

## Decision

Gemini 2.5 Pro process auditor in bc-ai independently verifies Claude session compliance. On-demand trigger, caller-provided context, 4-layer audit checklist (protocol, SOP, claims, gates), weighted scoring model, findings stored in DevHub.
