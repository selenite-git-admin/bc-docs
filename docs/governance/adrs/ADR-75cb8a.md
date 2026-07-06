---
uid: DEC-75cb8a
title: "Machine-enforced metric-authoring drift guard — two layers: bc-core deterministic gates (authority) + DevHub MCP preflight/orchestrator (ergonomics)"
description: "Move metric-authoring rule compliance from human vigilance to machine gates: bc-core PE-MC source-agnostic-literal check + panel fail-fast (authority), DevHub MCP preflight + step-gated orchestrator (ergonomics)."
status: proposed
date: 2026-07-06T02:10:31.032Z
project: bc-core
domain: metrics
subdomain: mcf/governance
focus: governance
---

# Machine-enforced metric-authoring drift guard — two layers: bc-core deterministic gates (authority) + DevHub MCP preflight/orchestrator (ergonomics)

## Context

Grounded audit SES-464df9 (2026-07-06) proved the failure mode: both 2026-07-05 drift catches (a planned document_type_code='DR' MC filter; contract creation bundled with runtime evaluation in one pass) depended entirely on the operator noticing mid-session — and the identical violation class had ALREADY escaped ten days earlier when vigilance lapsed: 3 ACTIVE wave-2 MCs carry SAP BLART literals inside their formula ASTs, activated through the full panel + PE-MC + two-phase-confirm chain with no gate objecting. Rules that exist only in CLAUDE.md, memory files, and cookbooks are enforced at human level and fail at human level (operator's framing). The mega-program (PLN-457cd0, 12,507 candidates) multiplies session count by orders of magnitude, so per-session vigilance cannot scale. Enforcement is placed at the evaluation boundary (repair-location D, enforcing the declared B-rule at its boundary — not lower-layer compensation), consistent with Invariant I (meaning evaluated once, at the boundary) and the existing gate precedents (near-dup operator-confirm e88cc04, C-FX fail-fast 8bb4d4f). The DevHub layer exists because panel runs cost real money and the earliest possible catch is before intake, but it deliberately carries zero authority so its absence or failure never weakens the governed chain.

## Decision

Session-level rule compliance in metric authoring moves from human vigilance to machine enforcement, in two layers with a strict authority split.

LAYER 1 — bc-core governed gates (the AUTHORITY; build first, TSK-30672e):
1. A new deterministic PE-MC check ("source-agnostic literals", next free PE-MC number): a Metric Contract is REJECTED at evaluate time if any filter-clause literal or any string literal in formula_ast_canonical_json, compared against a code-role bound concept, is not a declared canonical value of that concept. Positive canonical-vocabulary allowlist, NOT a SAP-pattern blocklist — generalizes to any source system (D441 operationalized). Consequence: no MC carrying a source doc-type literal (DR/DZ/BLART/KR/KZ, or any future system's codes) can ever reach ACTIVE again.
2. A panel-time fail-fast mirroring the C-FX pattern (commit 8bb4d4f): APPROVE verdicts whose maker envelope contains such literals are downgraded to OPERATOR_REVIEW with operator_review_reason='source_literal_suspect' — the violation is caught before materialization, not after spend.
3. Validation corpus: the 3 ACTIVE wave-2 SAP-literal MCs found by audit SES-464df9 (cleared_customer_payment_amount, total_credit_sales, credit_sales_ratio) MUST fail the new check; the 80 clean MCVs MUST pass. Existing ACTIVE violators are NOT auto-invalidated (no historical rewrite, Invariant III); their remediation stays on TSK-853a3b via M15/M19.

LAYER 2 — DevHub MCP session guard (ERGONOMICS + spend protection; zero authority; TSK-36403f):
4. devhub_metric_preflight — validates a candidate recipe/envelope BEFORE any panel spend: the same source-literal scan (canonical vocabulary fetched from bc-core), base-vs-derived GRAIN test, C-FX fixture arithmetic pre-check, near-dup probe, envelope field-landmine lint. PASS/BLOCK with reasons.
5. devhub_metric_workflow — a step-gated state machine for the 8-step authoring spine: hands the session only the NEXT allowed step; structurally refuses runtime-evaluation steps inside a contract-creation workflow (the "separate units" rule becomes a state machine, not a memory note).
6. Authority split is absolute: DevHub tools are read-only against bc-core, never bypass governed endpoints, and fail closed with an explicit outage note; bc-core gates remain the enforcement of record even if the DevHub layer is skipped or down.
