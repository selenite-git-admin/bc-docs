---
uid: DEC-d3492b
title: "as_of selection mode 'latest_observation' — per-series latest-snapshot governed selection (per-period balances)"
description: "as_of selection mode 'latest_observation' — per-series latest-snapshot governed selection (per-period balances)"
status: decided
date: 2026-07-11T08:18:36.713Z
project: bc-core
domain: data-platform
subdomain: metric-runtime
focus: governance
---

# as_of selection mode 'latest_observation' — per-series latest-snapshot governed selection (per-period balances)

## Context

No rationale recorded.

## Decision

Additive extension of the D465 governed-selection vocabulary (DEC-483f1e; select-by-gate.ts — the module whose own doctrine declares per-shape predicates arrive as follow-ups): the as_of temporal-gate shape gains a second SELECTION MODE, 'latest_observation', alongside the existing open/closed-item relation. Declaration (mcf.metric_contract.temporal_gate_params_json): { selection: 'latest_observation', anchor_field, series_key_fields: [..], tiebreak_field? } — mutually exclusive with closing_field/relation/age_band (a different selection kind within the same as-of state family). Semantics (pure, clock-free, stamped-fields-only per the boundary-independent rules): group candidate COs by the declared series key (e.g. bank_account_identifier); per series member, resolve exactly the candidate with the MAXIMUM stamped anchor_field ≤ P (ties broken by tiebreak_field, then stable ref order); candidates with null or future anchors are excluded; series members with no candidate ≤ P are absent from the resolved set (no fabricated zero). Carry-forward across periods is INHERENT — candidates are not period-bounded and P does the scoping, so an account whose last statement precedes the period still resolves its latest known balance (the faithful as-of cash-position semantic; unbounded lookback is the declared meaning, staleness is governed by status filters). The resolved set is recorded in Lineage (Invariants IV + VI); selection is read-time predicate application, never re-evaluation (Invariant V; reads do not trigger evaluation). Rationale for locus: statements/period balance rows are REAL observations that must survive as COs (collapsing them at the canonical layer would destroy evidence — Invariant VI); period-snapshot semantics belong to the metric runtime's governed selection, exactly where as_of open-item state selection already lives. First consumers: total_cash_balance and the bank cash-position family over FEBKO statement rows (TSK-d6a5f0), and GL per-period closing balances over period-grain balance rows. Gate shape vocabulary (the seven shapes) is UNCHANGED; PE-MC-14 alignment untouched (as_of family membership already covers it).
