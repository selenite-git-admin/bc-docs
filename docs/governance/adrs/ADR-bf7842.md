---
uid: DEC-bf7842
title: "DevHub is dev/ops coordination; bc-core owns the metric-authoring domain (generation, pre-spend validation, enforcement)"
description: "DevHub is dev/ops coordination; bc-core owns the metric-authoring domain (generation, pre-spend validation, enforcement)"
status: decided
date: 2026-07-07T16:13:00.592Z
project: bc-core
domain: metric-runtime
subdomain: mcf-authoring
focus: architecture-boundary
---

# DevHub is dev/ops coordination; bc-core owns the metric-authoring domain (generation, pre-spend validation, enforcement)

## Context

No rationale recorded.

## Decision

CONTEXT. The MCF metric-authoring toolchain accreted in the barecount-devhub repo for Claude-session convenience: the envelope generator (.claude/tools/mcf-author-family/author-family.mjs), a pre-spend validator (src/lib/metric-preflight.js), and the pipeline driver (src/lib/metric-drive.js), surfaced as devhub_metric_* MCP tools. This put PLATFORM DOMAIN logic in the dev/ops coordination hub. The concrete harm is proven, not theoretical: the devhub preflight DRIFTED from bc-core's enforcement — it caught only fixture-type==data_type while bc-core's real C-FX engine caught the non-currency representation failure (SES-3ccc24). Two copies of the same envelope grammar / C-FX / grain rules inevitably diverge. bc-core is already the enforcement of record (FixtureStructuralCheckService C-FX, D441 guard, formula-canonicalization AST grammar, package-signature temporal-gate kernel, identity-collision, PE-MC-1..16), and every validator already exists there as a pure, reusable function.

DECISION. (1) DevHub's role is dev/ops COORDINATION only — sessions, tasks, plans, decisions/ADRs, doc/API scans, chain-status reads, QA orchestration. It must not host platform domain logic. (2) bc-core owns the metric-authoring domain END-TO-END and is the SINGLE SOURCE of the envelope rules: generation grammar, pre-spend validation, and enforcement — the pre-spend validation IS the same code the panel/materialize/PE-MC enforce with. (3) The existing devhub metric-* tooling migrates to bc-core incrementally; whatever remains in devhub is a THIN CLIENT that calls bc-core and holds no domain rules. Fail-closed: if bc-core is unreachable the client BLOCKs (no offline shadow rules).

MIGRATION ORDER (incremental, each unit independently safe; no big-bang). Phase 1 — PREFLIGHT: add a governed pre-spend endpoint POST /api/mcf/authoring/validate-envelope that composes bc-core's existing pure validators (D441 + C-FX structural checks + AST grammar + temporal-gate kernel + binding-snapshot + identity-collision + filter-translation); repoint devhub_metric_preflight and metric-drive's preflight step to call it; delete the duplicated rules from devhub metric-preflight.js. This kills the drift and is the highest-value first step. Phase 2 — GENERATOR: envelope generation becomes a bc-core capability (grammar-owned in core); the devhub generator becomes a thin caller or is removed. Phase 3 — DRIVE: devhub metric-drive becomes a pure sequencer over bc-core endpoints, holding no domain reconciliation logic.

CONSEQUENCES. One source of validation truth (no drift). DevHub preflight/drive become thin clients; a bc-core outage fails them closed rather than silently applying stale local rules. Enforcement lives at its boundary (Foundation-aligned: no lower-layer or duplicated compensation). No DB schema change (validation is stateless/read-only). Supersedes the framing in PLN-457cd0 Decision #8 that placed a standing pre-spend validator in DevHub as "Layer 2" — the pre-spend validator is a bc-core endpoint; DevHub only calls it.
