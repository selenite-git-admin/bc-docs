---
uid: DEC-c4c742
title: "The Governed Selection — defining the Invariant-IV reserved selection artifact (as-of/state selection)"
description: "Define §IV's reserved governed-selection artifact: a declared, versioned, Lineage-recorded P-parameterized selection of immutable object versions = the Foundation home for as-of/state metrics."
status: decided
date: 2026-06-29T09:21:11.528Z
project: bc-core
domain: metrics
subdomain: as-of-selection
focus: foundation
---

# The Governed Selection — defining the Invariant-IV reserved selection artifact (as-of/state selection)

## Context

State-as-of-P metrics (balance, stock, outstanding, aging) are not flow aggregations: a state at P is the derived consequence of every state-changing event up to P, read through a clock only P advances. The progression is event-native, so this class has no native home — and the obvious shortcuts (read the current status flag; "latest" at read time; an ad-hoc query) are exactly what Invariant IV disallows, because a stored status is as-of-now (knowledge time) and silently misclassifies any historical P. Invariant IV anticipated this and RESERVED the governed selection artifact ("future definition … not assumed to exist in the current runtime"); this fills that slot rather than inventing a new invariant. Motivated by Route B (DEC-83fda0) and an operator-led problem-framing pass (SES-8f76ae) that reduced as-of to its irreducible form: a P-parameterized governed selection over immutable dated facts, with full-clearing reusing the existing dated receivable canonical and the postings-clearings netting deferred as the partial-settlement generalization.

## Decision

Define the Invariant-IV reserved "governed selection artifact" as THE GOVERNED SELECTION: a declared, versioned rule that, given a selection parameter (the as-of point P), resolves from the immutable authoritative-object set the specific object versions that constitute a named state, and records the resolved set in Lineage. It is performed once at an evaluation boundary as the input-selection of an evaluation act; its result is an immutable, recorded object version (an ordinary Metric Snapshot for a state-metric — no new object type). The MCF temporal_gate shapes (as_of, cumulative_to_date) are its metric-grammar surface.

THREE LOCKS (operator-confirmed, SES-8f76ae):
1. SLOT — the governed selection is the GENERAL artifact filling §IV's reserved slot. Single-reference-to-single-version resolution is the degenerate set-of-one case; as-of state-selection is the general set case. Both honour: versioned rule + resolved versions recorded in Lineage.
2. KNOWLEDGE-TIME — the base case evaluates at CURRENT knowledge. Invariant V already makes re-evaluation a distinct act producing a distinct version, so the bitemporal record (as-of-P-known-at-K) accumulates immutably and audit READS it. Knowledge-time querying is NOT built now.
3. HOME — a dedicated Foundation chapter foundation/the-governed-selection.md, a pointer at the-invariants.md §IV (the "Governed selection artifact" row moves Reserved -> Defined), and this ADR.

SHAPE: PARAMETER P is a governed evaluation input (never the system clock / "now" / read-time). PREDICATE is a declared rule over the candidate objects' STAMPED fields (effective times + immutable attributes) and P, referencing only stamped values — no read-time resolution, no calendar lookup at evaluation. RESOLVED SET is the immutable object versions satisfying the predicate at P, recorded in Lineage.

GUARANTEES: I — produced once at the boundary, consumers read the recorded result. III — result immutable. IV — the rule is versioned; the resolved set is recorded in Lineage. V — re-evaluation is a distinct act/version; audit reads the version it wants, never reruns to reconstruct. VI — the resolved set is emitted as evidence. The §IV disallowed behaviours ("latest"/read-time, time-based inference, query-driven selection not represented by a governed artifact) are the stored-status-flag shortcut and are forbidden by construction — membership is derived from the predicate at P, never stored-and-read (a stored status is as-of-now/knowledge-time, not as-of-P/effective-time).

FIRST INSTANCE to build: "outstanding in last 30 days, as of P" = a governed selection over the receivable Canonical Objects, predicate {clearing-effective-time > P OR absent} AND {P - anchor-effective-time in [0,30] days}, over cc__customer_invoice_arpi_slice's existing dated COs (no new surfaces), the metric summing amount over the resolved set.
