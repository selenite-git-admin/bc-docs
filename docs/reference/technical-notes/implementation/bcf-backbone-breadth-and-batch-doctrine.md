---
uid: bcf-backbone-breadth-and-batch-doctrine
title: BCF — backbone breadth and batch execution doctrine
description: Operating doctrine for how BCF authors substrate breadth — backbone-slice design rather than fixed item counts, batch execution rules (full slice in one session, continue to exhaustion, no item/dollar caps), and the canonical-vs-source-diagnostic classification applied at breadth level. Companion to the Vocabulary Evidence Framework's §11; orthogonal to the per-characteristic admission checklist.
status: accepted
date: 2026-06-19
project: bc-docs
domain: contracts
subdomain: catalog
focus: governance
---

# BCF — backbone breadth and batch execution doctrine

> **What this is.** Operator-ratified doctrine for how BCF advances breadth
> coverage across entity backbones — how slices are chosen, when a backbone is
> "complete-enough", and how batches are executed. Companion to the **Vocabulary
> Evidence Framework** (per-characteristic admission rubric) and its
> [§11 amendment](business-concept-registry-vocabulary-evidence-framework.md#11-system-agnosticism-characteristic-hygiene-and-substrate-role-amendment-2026-06-19)
> (system-agnosticism + substrate-role distinction). This doc is not an
> admission rubric; it is breadth strategy and batch execution policy. Design /
> doctrine note. No code, no schema, no DBCP.

## 1. Purpose

Substrate breadth — how many entities are admitted, how many BCs each carries,
which backbone is filled next — is judged differently from per-characteristic
admission. The Vocabulary Evidence Framework governs whether a *candidate
characteristic* is admissible; this doc governs whether a *backbone* is
complete-enough to support metric work, and how the batches that fill backbones
are run.

The decisions here have been operating discipline for several months of BCF
breadth work (AR-side waves W1/W2A/W3-A/W3-B, AP-side Wave 0, PO header batch
of 10, Stage C lifecycle gap closure). This doc ratifies them in one place.

## 2. Backbone completion doctrine

### 2.1 Design by coherent backbone slice, not by fixed item count

A **backbone slice** is a coherent business surface — e.g. "Customer Invoice
header", "Customer Invoice Line Item", "Purchase Order header",
"Currency Exchange Rate", "Bank Statement Line". A slice is bounded by a single
entity (or a tightly coupled entity pair: header + lines) and includes the BCs
needed to make that entity load-bearing for downstream metrics, joins, and
filters.

- A slice is chosen for **coherence**, not for size.
- A slice may include 4, 7, 12, or more BCs depending on the entity's natural
  coverage surface.
- Splitting a slice across batches for arbitrary item-count reasons is
  discouraged — it produces partial backbones that don't unblock any metric.

### 2.2 Complete-enough rather than complete

A backbone is **complete-enough** when its load-bearing metric, join, filter,
and comparison fields are present. It is **not** required to admit every BC
that the source noun could in principle yield.

The test is whether the backbone supports the metric / reconciliation / audit
/ source-mapping workflows currently in scope or imminent. A backbone with five
or six well-chosen BCs supporting an analytical surface beats a backbone with
ten BCs that includes optional source-diagnostic classifiers nobody is reading.

### 2.3 Optional diagnostic classifiers can remain deferred

Per the
[Vocabulary Evidence Framework §11.3](business-concept-registry-vocabulary-evidence-framework.md#113-canonical-metric-substrate-vs-source-diagnostic-substrate)
canonical-vs-source-diagnostic distinction, a BC whose only function is source
diagnostic does **not** block backbone completion.

- Parked source-diagnostic BCs are recorded as **intentional deferrals with
  documented system-agnostic rationale**, not as open coverage gaps.
- Revisitation is triggered by **concrete workflow demand** (a metric,
  reconciliation, audit, or source-mapping workflow that requires the binding),
  not by elapsed time or substrate-completeness audits.

Worked example: Purchase Order × document type code (parked 2026-06-19, treated
as optional source-diagnostic substrate per the held characteristic-scope
hygiene packet). PO Header backbone is complete-enough for current breadth work
despite the parked verdict.

## 3. Batch execution doctrine

### 3.1 Run the full backbone slice in one session

A backbone slice is run end-to-end in one session. The slice's items are
sequential; the session is not interrupted to "split the batch into smaller
pieces" for cost or duration reasons.

Rationale:
- **Cache cadence**. The Maker / Checker / Moderator panel's ephemeral prompt
  cache is per-session; running adjacent items together captures cache reuse on
  the shared prefix. Splitting across sessions throws this away.
- **Coherence**. A backbone slice's items reinforce each other in the panel's
  context (same entity, similar shape) — the panel's evidence judgements are
  better when items are adjacent.
- **Operator review**. A complete-slice batch report is easier to read and
  decide on than a sequence of partial-slice reports.

### 3.2 No arbitrary item-count cap

There is no doctrinal cap on the number of items in a backbone batch. The
slice's natural size determines the batch size. Past batches have run from 3
items (residual retries) to 10 items (PO header backbone) to larger slices when
warranted.

A *technical* upper bound exists (Anthropic API stability, session-time budget,
operator attention span on a single report), but it is not 10, not 20, and not
a fixed number — it is whatever the slice is.

### 3.3 No dollar cap; report cost after

Batches are not pre-capped on USD. The Stage B telemetry retrofit (PRs #25/#26)
records every panel run's cost; the post-batch report includes
per-item and cumulative cost.

- Setting a dollar cap below the slice's natural cost would force the slice to
  be split (see §3.1).
- Cost is reported, not pre-bounded — operator reviews the cost in context
  alongside the substrate deltas. If the cost is unexpectedly high, the next
  batch's design is revisited; the current batch is not halted mid-slice.

### 3.4 Continue to exhaustion unless a fatal stop fires

A batch runs to exhaustion. Per-item failures do not halt the batch.

- **HTTP 400 from bc-core's authoring orchestrator** (validation refusal) →
  log, park, continue.
- **Panel `OPERATOR_REVIEW` verdict** → log, park, continue.
- **Per-item timeout** → log, continue.

A **fatal governance/platform stop** halts the batch. The fatal-stop list is
small and operator-defined; current members include:
- bc-core or bc-ai unhealthy (consecutive 5xx, sustained timeout, auth
  failure).
- A successful HTTP 200 that does not produce the expected telemetry trail
  (silent failure — telemetry is the audit substrate; missing telemetry is a
  fatal observability gap).
- Direct-write or governance-bypass detected.
- Schema mismatch affecting all items (not item-level evidence problems).
- Cross-registry mutation outside the expected scope.
- Prompt or cache-prefix drift across the batch (cache discipline failure).

This is the **continue-to-exhaustion** rule. It was ratified during Stage C
(Amendment 2) and used in the PO header batch of 10 (2 authored + 7 HTTP 400 +
1 parked = 10 terminal outcomes, zero fatal stops fired) and the PO residual
retry (2 authored + 1 parked = 3 terminal outcomes, zero fatal stops).

## 4. Current substrate state (2026-06-19)

Snapshot at the doctrine-ratification point. Numbers are an audit baseline, not
a permanent state; they are expected to evolve as breadth work proceeds. For
the current live state, query `concept_registry` directly.

| Surface | Count |
|---|---|
| Active entities | 17 |
| Active characteristics | 53 |
| Active business concepts | 123 |
| Active business concept versions | 123 |

### 4.1 Backbone coverage at ratification

| Backbone | Verdict | Comment |
|---|---|---|
| Customer / AR (CI, CILI, CP, CS, CIA, Customer, Credit Application, Credit Status, Remittance Advice, SO, SOL) | **rich** | Multi-axis metric work clear-to-run: DSO, billing accuracy, dispute rate, partial-payment, weighted aging. |
| Supply chain / logistics (Customer Shipment) | **usable** | Shipment-level metrics clear; cross-cutting fulfillment analytics weak until SO ↔ CS relationship is modelled. |
| Supplier / AP (Supplier, Supplier Invoice) | **usable** | AP DPO / aging metrics clear; AP master-data analytics lean until Supplier reaches Customer parity. |
| Procurement / PO (Purchase Order) | **usable** (complete-enough) | PO header metrics clear. PO × document type code parked as optional source-diagnostic substrate; does not block. |
| Banking / payments (Bank Statement, Bank Statement Line) | **usable** | Bank reconciliation metrics ready. |
| Treasury / currency (Currency Exchange Rate) | **purpose-complete** | No push needed. |
| GL / accounting | **not present** | No GL entity admitted. Foundation gap, not a current slice. |

### 4.2 Next recommended breadth slice

**Procurement line-item axis** — admit Purchase Order Line and Supplier Invoice
Line as a single coherent slice; bind ~6 BCs each, mostly reusing the
substrate's existing reuse spine (status, document number, currency code,
posting date, document date). Closes line-side AP/PO symmetry vs the AR-side
CILI/SOL coverage already in place; sets up three-way-match analytics. The
operator-deferred `document type code` characteristic-scope decision does NOT
gate this slice (see Vocabulary Evidence Framework §11.4 worked example).

This recommendation is doctrine-grade only — actual execution requires an
operator-authorised planning packet.

## 5. Cross-references

- **Per-characteristic admission rubric** —
  [Vocabulary Evidence Framework](business-concept-registry-vocabulary-evidence-framework.md)
- **System-agnosticism + substrate-role distinction** —
  [Vocabulary Evidence Framework §11](business-concept-registry-vocabulary-evidence-framework.md#11-system-agnosticism-characteristic-hygiene-and-substrate-role-amendment-2026-06-19)
- **Business Concept Registry conceptual model** —
  [Business Concept Registry](../../../implementation/business-concept-registry.md)
  (DEC-02f5a9)
- **BCF build plan** —
  [Business Context Framework build plan](../../../evidence/work-records/implementation/business-context-framework-build-plan.md)

## 6. Provenance

The doctrine in this doc was distilled from operator-held BCF packets and
recent breadth-work execution reports — cited as evidence of the operating
discipline that this doc ratifies, not as authoritative inputs:

- `barecount-devhub/.claude/bcf-substrate-inventory-and-backbone-audit-held-2026-06-19.md`
  — substrate audit feeding §4.
- `barecount-devhub/.claude/bcf-characteristic-scope-hygiene-decision-held-2026-06-19.md`
  — characteristic scope hygiene + `document type code` deferral feeding §2.3
  and §4.1's PO row.
- `barecount-devhub/.claude/bcf-batch-of-10-ap-backbone-held-2026-06-19.md`
  + execution report — evidence of the batch-execution discipline now ratified
  in §3.
- `barecount-devhub/.claude/bcf-stage-b-closeout-and-stage-c-pilot-plan-held-2026-06-18.md`
  — Stage C "Amendment 2" continue-to-exhaustion rule ratified in §3.4.

These packets are working notes, not load-bearing references for future
readers. The doctrine above stands on its own.

## 7. Non-goals

This doc deliberately does **not**:

- Author or admit any characteristic, BC, or entity.
- Specify the BCF authoring orchestrator's wire protocol, batch driver
  implementation, or panel-cache mechanics — those live in implementation
  notes and bc-core code.
- Replace per-characteristic admission rubric — that is the Vocabulary
  Evidence Framework's job.
- Decide GL or non-finance backbone work — those are domain-expansion
  decisions outside current scope.
- Lock the next batch — §4.2 is a recommendation, not an authorisation.

## Status

`accepted` — ratifies operating discipline established across BCF breadth work
2026-04 through 2026-06. Companion to the
[Vocabulary Evidence Framework §11 amendment](business-concept-registry-vocabulary-evidence-framework.md#11-system-agnosticism-characteristic-hygiene-and-substrate-role-amendment-2026-06-19)
(2026-06-19). Future BCF breadth slices and batch runs should be designed under
this doctrine.
