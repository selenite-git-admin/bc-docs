---
uid: DEC-bc6be2
title: "Finance Package v0 — advance the date-derivation unlock; sanction date_offset OC transform for the date-diff family"
description: "Advance DEC-a7fe72: bring the date-derivation unlock forward; sanction a date_offset OC-grammar transform to observe due date = baseline (ZFBDT) + terms (ZBD1T), unblocking the date-diff family (average_days_to_collect). The D401 as_of packet (open-item aging/DSO) remains a separate later effort."
status: decided
date: 2026-06-27T13:34:59.026Z
project: platform
domain: metrics
subdomain: metric-portfolio
focus: governance
---

# Finance Package v0 — advance the date-derivation unlock; sanction date_offset OC transform for the date-diff family

## Context

No rationale recorded.

## Decision

> **⚠ MECHANISM CORRECTED by DEC-7d2f8c (D462), 2026-06-28.** The *sequencing* decision below ("the later time is now" for the date-diff family) **stands**. The *sanctioned mechanism* — a `date_offset` transform in the **observation** grammar producing due-date "at the observation boundary" — is **withdrawn as an Invariant-I violation**: the contract grammar forbids an Observation Contract from declaring canonical evaluation logic, and meaning is produced once **at the canonical boundary, by the Canonical Contract**. Corrected mechanism: the OC *observes* `baseline` (ZFBDT) + `terms` (ZBD1T); the **CC** derives `due = date_add(baseline, terms)` as a **1-hop canonical derived field**. The `clearing − due` subtraction (where `due` is derived) moves to the **metric boundary** (secondary-metric DAG). See DEC-7d2f8c. The `date_offset` OC-grammar enum + `transform_params` change in SCOPE below is **not to be built**.

Operator advances the DEC-a7fe72 (D440) sequence: "the later time is now" for the date-DIFF metric sub-family (average_days_to_collect, days-to-pay, and similar clearing-minus-due metrics).

AMENDS DEC-a7fe72 (does NOT supersede — Locks 1/2/4/5 + the roadmap-wide-execution-narrow principle stand): (a) Lock 3 made average_days_to_collect a grammar PROBE allowed to "shrink honestly"; (b) Lock 6 deferred the DSO/aging family to the D401/as-of packet (later build). This decision brings forward ONLY the date-derivation capability the date-diff sub-family needs — a derived due date = baseline date (ZFBDT) + net terms days (ZBD1T) — which is DISTINCT from and NARROWER than D401's as_of/open-item grammar. The D401 as_of packet (open-item canonical + as_of evaluator for aging/DSO-via-open-items) REMAINS a separate later effort; this is not its early build.

SANCTIONED MECHANISM: a date_offset transform in the OBSERVATION field-map grammar (observation boundary) so an OC observes due date = base_date_field + offset_field (unit=days). This is NOT A-layer/SDG compensation (Foundation Invariant I): the source genuinely emits ZFBDT + ZBD1T; due date is a real derivation produced once at the observation boundary from admitted primitives. OC transforms are currently declaration-level (no runtime evaluator; runtime application of ALL OC transforms is Bar-2-deferred), so this unblocks the PE-MC-11/D431 declaration gate; runtime computation lands with Bar-2.

SCOPE: (1) add date_offset to the observation grammar enum + transform_params {base_field, offset_field, offset_unit}; (2) OC version on the Customer Invoice cleared-item (BSAD) surface declaring due_date via date_offset; (3) CC cc__customer_invoice_arpi_slice v6.0.0 additive (live = v5.0.0 active, 9 fields, no due_date) adding due_date; (4) re-run PE-MC on the parked Avg Days draft MCV 3de1770a -> activate. COORDINATE with in-flight TSK-ca5dd3 (F1-B1 invoice-slice widening, WIP) on the same Customer Invoice OC/CC chain. Repair-location B (grammar) + A (observation declaration).
