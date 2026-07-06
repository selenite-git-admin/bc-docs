---
uid: DEC-ffee4e
title: "Retire bc-ai — port the BCF registry-authoring panel in-process into bc-core, roster preserved"
description: "bc-ai retired; BCF panel (Opus 4.7 / DeepSeek V3.2 Bedrock / GPT-5.5, v1.3 prompts) ported in-process into bc-core behind BCF_PANEL_MODE switch; budget guard deferred to tenant-wise price controller"
status: implemented
date: 2026-07-03T10:20:06.094Z
project: bc-core
domain: platform
subdomain: bcf-panel
focus: runtime
supersedes: DEC-14fb98
---

# Retire bc-ai — port the BCF registry-authoring panel in-process into bc-core, roster preserved

## Context

Ground study SES-2a76e7 (2026-07-03, study doc barecount-devhub/.claude/bc-ai-retirement-ground-study-2026-07-03.md): the BCF panel is bc-ai's only live workload (1,169 bcf.panel_output_record rows, near-daily for 3 weeks; every other flow idle since 2026-05-15; housekeeping scheduler disabled per D269; all 20 recent commits BCF-only). bc-core already runs the identical pattern in-process (MCF M12 three-vendor panel) with all four AI SDKs installed, so ~60-70% of the port is reuse; the seam is DI-clean so callers are untouched. Retiring bc-ai removes an always-on Python service, a duplicate key/env set, a Cognito service-user hop, and a fail-open telemetry seam, and brings the BCF panel under bc-core's TS strict/QA gates and the off-pool dual-Maker cost lever.

## Decision

The bc-ai Python service is retired after a phased cutover. Its only live workload — the BCF registry-authoring panel (B6 Track 2, Maker/Checker/Moderator) — moves in-process into bc-core behind the existing DI seam (REGISTRY_AUTHORING_PANEL_CLIENT token): a new InProcessRegistryAuthoringPanelClient implements the same RegistryAuthoringContextPacket → {panelRunUid, verdictCode} contract, selected via env switch BCF_PANEL_MODE (default remains 'bc-ai' until one-then-many parity is proven, then flips to 'in-process').

Locked points:
1. **Roster preserved exactly** (operator decision 2026-07-03): Claude Opus 4.7 Maker (Anthropic API, ephemeral prompt cache), DeepSeek V3.2 Checker (Bedrock Converse), GPT-5.5 Judge/Moderator (OpenAI). The calibrated v1.3 prompts (DEC-663a46) migrate verbatim; no calibration impact.
2. **Hard budget guard deferred** (operator delegated; Claude's call): no daily-USD hard cap is ported now. Dev spend is operator-monitored in vendor consoles; advisory cost telemetry is carried through. A tenant-wise price controller is filed as a parked production task and will be designed with production tenancy.
3. **Panel semantics unchanged**: A1 grounding checks (evidence deep-equal, name-collision, f3_input presence, malformed-APPROVE downgrade per Invariant V), verdict enum APPROVE_FOR_DRAFT | OPERATOR_REVIEW | REJECT_DEFECT, and the NF1 panel_output_record shape are ported byte-compatible. Panel-output emission and BCF telemetry become in-process service calls (HTTP hop, Cognito service-user auth, and fail-open telemetry seam are deleted).
4. **Phased retirement**: Phase 1 port behind switch → Phase 2 flip default (bc-ai idle = instant rollback) → Phase 3 retire residual consumers (bc-core M11 EnrichmentProcessor polling an empty queue; bc-admin kpi/ask drawer and metric-verify gate on the legacy metric stack; devhub housekeeping proxy and process-audit tool) → Phase 4 stop bc-ai, archive repo read-only, disposition its open tasks (cf_classifier / bf_admission_review / cf_dedup panels re-home to bc-core if still wanted; D235 ChromaDB RAG phases re-scope or abort).

Supersedes DEC-14fb98 (bc-ai owns its SQLite DB) — the SQLite store held only budget/evidence logs; the durable NF1 records already live in bc-core Postgres, so no data migration occurs.
