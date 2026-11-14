---
uid: DEC-5982ec
title: "The point_in_time family reshape: re-declare each member's true temporal meaning (shape and definition), grouped by target shape; the as_of/flow targets are gated on the per-input period predicate"
description: "The point_in_time family reshape: re-declare each member's true temporal meaning (shape and definition), grouped by target shape; the as_of/flow targets are gated on the per-input period predicate"
status: proposed
date: 2026-10-07T02:58:35.170Z
project: bc-core
domain: metrics
subdomain: contracts/metric-shape-semantics
focus: point_in_time family reshape: per-member disposition by target shape, name↔definition fidelity, the TSK-36440f gate, active exposure
---

# The point_in_time family reshape: re-declare each member's true temporal meaning (shape and definition), grouped by target shape; the as_of/flow targets are gated on the per-input period predicate

## Context

DEC-d0b66a settled point_in_time's semantics on a single member and named reshape as its own design act (Decisions 5/6); this carries it across the family. The defect is a meaning-fidelity defect (Invariant I, meaning evaluated once and correctly): substrate shows all 16 flows defined verbatim as "As-of (point-in-time) snapshot balance (sum)... a stored balance/stock read as-of the reporting date" though they are period flows. The cumulative_to_date journal-entry-line family (current_asset_balance, total_asset_balance, earnings_to_date, receivable_control_balance, ...) expresses the same concepts correctly ("sum of amount_input... over period to date", real period-end selection) and is both the reshape target pattern and the evidence the GL-grain stocks are duplicates. Correcting the directory classification or the evaluator without first re-declaring the shape+definition would be lower-layer compensation for an upper-layer declaration gap (forbidden, DEC-c48b0f). Grounded at bc_platform_dev mcf.metric_contract/_version and bc-docs/bc-core origin/main, 2026-10-07.

## Decision

Applies the decided DEC-d0b66a across the whole point_in_time family (49 contracts = 27 distinct base concepts + 22 __tacorr duplicate variants). (1) The reshape target is each member's economic meaning, not its current wrong shape (Inv I). (2) Per-member disposition by target shape: 6 stocks -> as_of (gated); 5 counts -> as_of count (gated); 16 flows -> period_aggregate or cumulative_to_date, never as_of (Metric's per-member period-vs-YTD call); plus 2 related none-shape defects -> period_aggregate and 1 as_of member (total_cash_balance) to declare its closing basis. Stocks sub-decision: the GL-grain stocks are wrong-shaped duplicates of concepts already correct in the cumulative_to_date JEL family, so where the concept is the same the faithful repair is supersession-by-existing-JEL-member, not a parallel as_of reshape; Metric confirms duplicate-vs-distinct-grain per stock. (3) Name<->definition fidelity is corrected in the same act: every flow is NAMED as a flow but DEFINED as an as-of stock snapshot, so the definition wording is re-authored to its true flow/cumulative meaning; shape alone is not enough. (4) Gate: all as_of/count-as_of/flow reshapes are sequenced AFTER TSK-36440f (the per-input period predicate), because without real period selection as_of is as degenerate as point_in_time; this ADR declares targets and defers execution, builds nothing. (5) Active exposure: 6 members produce today (5 counts + current_liabilities via its active __tacorr variant) emitting a date-less current snapshot presented as an as-of value; the other 21 concepts are latent (no current version). (6) Foundation: repair location B (declaration of true temporal meaning), a design act (not a detector), no lower-layer compensation (DEC-c48b0f), Inv III preserved (reshape mints/supersedes, never mutates).
