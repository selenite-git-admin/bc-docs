---
uid: DEC-93be49
title: "clearing_date is a source-agnostic as_of-close semantic field; its per-source difference is resolved at the binding layer, and clearing_date members are clean at the platform plane when shaped as_of"
description: "clearing_date is a source-agnostic as_of-close semantic field; its per-source difference is resolved at the binding layer, and clearing_date members are clean at the platform plane when shaped as_of"
status: decided
date: 2026-10-06T02:51:20.838Z
project: bc-core
domain: metrics
subdomain: contracts/metric-shape
focus: clearing-date derivation, as_of close semantics, source-agnostic binding, directory-clean condition
---

# clearing_date is a source-agnostic as_of-close semantic field; its per-source difference is resolved at the binding layer, and clearing_date members are clean at the platform plane when shaped as_of

## Context

No rationale recorded.

## Decision

clearing_date is a SOURCE-AGNOSTIC semantic canonical field — "the date an open item is cleared" — with as_of CLOSE semantics: absent clearing_date = OPEN at P; present and ≤ P = CLOSED by P. The per-source difference is resolved by BINDING (C-layer), never in the metric contract: SAP binds clearing_date to the native column (AUGDT/AUGBL alias); Odoo binds it to a governed canonical derivation MAX(account.partial.reconcile.max_date) over the open item's full_reconcile_id (NULL when full_reconcile_id is NULL = open). A clearing_date directory member is CLEAN at the platform plane when shaped as an as_of member on the clearing_date closing_field; a member that mis-uses clearing_date (raw field, point_in_time anchor, or period filter) must be re-shaped to as_of. The Odoo reconciliation-derived binding is NOT built in bc-core today; that binding is authored at tenant provisioning (C-layer, Phase-C Kaveri) and does NOT block the platform-plane member definition. Authority: operator desk grant 2026-10-06T02-48-59-826Z-f04c9003 (text_sha256 f04c9003d5a09fe6ae3de47a8127f24d7e0188df2206242e918c3acbb119c0ab).</decision_text>
<parameter name="rationale_text">Grounded at bc-core cc08875b + live concept_registry + Metric's Odoo v3_lc5 Q1-Q4. clearing_date is seeded as a semantic canonical field (seed-standard-fields.ts:306; SAP alias) and consumed by metric contracts (ar_customer_payment_canonical / ap_vendor_payment_canonical). The as_of close runtime IS BUILT and correct (governed-selection.ts:127-133 open_at/closed_at; select-by-gate.ts:186-214 selective) — unlike point_in_time (DEC-d0b66a), there is no declared-but-unbuilt runtime gap for the as_of path, so correctly-shaped members are genuinely clean. Source-agnosticism (DEC-c220e4; "no formulas tied to fact shape; onboard a second source through binding without MC edits"): clearing_date's meaning is evaluated once (Invariant I); the source binding is explicit and per-source (Invariant IV) at C, not an evaluator or metric-contract edit (no lower-layer compensation). The Odoo binding being unbuilt is a tenant-plane provisioning concern, consistent with the Oct-2 platform-plane-only drive — it does not make the platform-plane definition unclean.</rationale_text>
<parameter name="description_text">clearing_date = source-agnostic as_of-close semantic field; per-source binding at C-layer; members clean when as_of-shaped; Odoo derivation is Phase-C.</parameter>
</invoke>

