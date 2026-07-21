---
uid: DEC-ec00f2
title: "Dual-model execution for judgment-bearing audit acts"
description: "Audit judgment (worksheets, bases, adversarial reviews, decisions) is executed by a non-Claude model; compilation stays cheapest-model; authority writes stay operator-only; no document review rounds"
status: decided
date: 2026-07-21T16:56:50.375Z
project: bc-core
domain: metrics
subdomain: metric-audit/execution-model
focus: governance
---

# Dual-model execution for judgment-bearing audit acts

## Context

Empirical basis from 2026-07-21: (a) the first end-to-end pilot (Claude as both platform driver and auditor) exposed that same-session self-adversarial-review only challenges what the author already intended; (b) the ramp-5 preflight had the counterparty model (Codex) catch a Claude-produced byte-custody defect (CRLF-tainted manifest digest pins) that Claude had walked past, while the platform gates symmetrically refused two defective Codex-era decisions (authority mismatch, unprojectable supersession) — mutual catching through code, not review rounds; (c) marginal cost of the cross-model auditor is near zero now that the exchange protocol (feed envelopes, evidence byte bundles, repo relay, operator-authorized bootstrap chain) is live. The prior two-engine engagement was concluded for ceremony fatigue (dual-repo paper relays, multi-round dispositions); this decision deliberately revives only the execution half under executable gates.

## Decision

The metric-audit machine runs a standing DUAL-MODEL EXECUTION arrangement, decided by the operator on 2026-07-21 after the first-wave pilot and the ramp-5 Codex engagement:

1. JUDGMENT GOES CROSS-MODEL. All judgment-bearing audit acts — worksheet axes and rationales, contextual-reference bases, adversarial reviews, and the resulting decisions — are executed by a NON-Claude model (currently OpenAI Codex driving the AuditHub engine in bc-external-audit). Rationale: the audited substrate (metric contracts, definitions, formulas, directory intents) was substantially authored by Claude-family sessions; a same-model auditor inherits the authorship priors, and a same-session self-review is structurally unable to challenge its own intent. This is the default for ALL cohorts and mandatory for wide-judgment cohorts (Class C sign/currency metrics, the 117 operator_review members).

2. COMPILATION IS MODEL-AGNOSTIC. Deterministic platform work — request staging (closure resolution, buildAuditRequest, publication signing), evidence byte reproduction, imports, projections, admission recomputation, admits — carries no judgment and no independence value; it runs on whichever model is cheapest/available per the cost-lean operating rule.

3. AUTHORITY STAYS WITH THE OPERATOR, regardless of model. Database authority appends (bootstrap successor chain), migrations, activations, signing-key acts: explicit operator authorization bound into a checkable artifact (authorized_by = the operator identity), NEVER agent self-authorization — on either side of the exchange.

4. NO DOCUMENT REVIEW ROUNDS. The dual-model value is execution independence over the machine protocol (signed envelopes, executable gates, append-only stores) — not paper relay. Repeated findings become gates (tests, refusals, schema pins), never runbook paragraphs, per the demote-ceremony doctrine (2026-07-20).

KNOWN LIMIT: dual-model does not remove correlated failure through SHARED CONTRACTS — both models read the same schemas and briefs, so a defect in the shared contract fools both until a real run hits it. The first real execution of any new surface remains the test that documents are not.
