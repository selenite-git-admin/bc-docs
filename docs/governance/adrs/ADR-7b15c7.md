---
uid: DEC-7b15c7
title: "Pause MCF materialization until contract governance hardening completes"
description: "Gate D428 MCF→contract.* materialization behind contract-governance hardening (immutability + canonical semantic identity + legacy-door close + fail-open gate fixes)."
status: decided
date: 2026-06-07T12:46:33.883Z
project: bc-core
domain: contracts
subdomain: governance
focus: materialization-gate
---

# Pause MCF materialization until contract governance hardening completes

## Context

The 2026-06-07 Foundation contract-governance audit found the legacy Metric Contract hand-typed-field smell (e.g. `mc__overdue_payables_pct`, `mc__ap_turnover_ratio` binding accounts-payable fields to the AR `cc__invoice_hdr`) is a SYMPTOM of two deeper gaps: (X1) no store enforces contract-version immutability — a shipped script rewrites ACTIVE canonical contract bodies in place, violating contract-grammar immutability-on-publish; and (X2) the Canonical boundary carries no field-level semantic identity, so meaning is not anchored where the Foundation requires it and downstream metrics hand-type field strings. Publishing MCF-authored metrics into `contract.*` before `contract.*` is Foundation-clean would entrench the same class of defect in the new store. The contract-governance substrate is therefore not yet strong enough to trust new Metric runtime materialization; pause until hardened, then resume. Source/Admission/Observation are aligned-in-role and need no rewrite.

## Decision

MCF→`contract.metric_contract*` materialization (the D428 "single clean published metric-contract store" step) is **PAUSED** until the contract-governance substrate is hardened. New Metric runtime materialization is not to be attempted or trusted until the gate below clears.

This does **not** reverse DEC-61f7c8/D428 (`contract.metric_contract*` remains the chosen published store) nor DEC-3f093f/D426 / DEC-c3e57f/D422. It gates the **timing** of D428's materialization step behind contract-governance hardening.

GATE (must complete, in order) — sourced from the Foundation contract-governance audit (`docs/implementation/foundation-contract-governance-audit-2026-06-07.md`):
1. **Contract-version immutability enforced at the store** (DBCP): active/superseded `*_contract_version` bodies cannot be modified in place; the `d365-enrich-cc-posting-date`-style active-body UPDATE is retired. (Foundation: contract-grammar immutability-on-publish; contracts are grammar, cf. Invariant III for objects.)
2. **Canonical Contract field-level semantic identity decided** (separate ADR): a canonical field declares its governed meaning (BCF Business-Concept / characteristic identity); MCF **consumes** it, never invents field mappings. (Foundation: Invariant I — meaning anchored at the Canonical boundary.)
3. **Legacy Metric Contract authoring door closed/guarded**: no new `contract.metric_contract` envelopes carrying free, semantically-ungrounded `fields_used`.
4. **Fail-open activation/publication gates fixed**: IntegrityService reading physically-dropped legacy mapping tables and treating `null` as pass; the dead `governance_state_code='released'` compatibility branch.
5. **Only after 1–4: resume D428 materialization.**

RESUME CONDITION: steps 1–4 landed + independently verified. Until then the materialization options memo (`mcf-materialization-boundary-options-2026-06-07.md`) and the ARPI `contract_json` synthesis proof (`mcf-arpi-contract-json-synthesis-proof-2026-06-07.md`) are **gated**; their canonical-binding finding is an **input to step 2**, not wasted work.

NON-GOALS: no panic-rewrite of the aligned admission-facing families (Source/Admission/Observation are aligned-in-role); the Intervention family misroute is parallel and non-blocking to the AR critical path.

This ADR exists so re-entry does not accidentally treat D428 materialization as "next." The next governed step is step 1 — the contract-version immutability DBCP — held for explicit operator approval before any apply.
