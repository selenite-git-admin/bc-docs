---
uid: DEC-93be49
title: "clearing_date is a source-agnostic as_of-close semantic field; its per-source difference is resolved at the binding layer, and members are clean at the platform plane when shaped as_of"
description: "clearing_date is a source-agnostic as_of-close canonical field whose per-source difference is a binding-layer concern; correctly as_of-shaped clearing_date directory members are clean at the platform plane"
status: decided
date: 2026-10-06T02:51:20.838Z
project: platform
domain: platform
subdomain: metric-shape-semantics
focus: clearing_date as_of-close semantics; source-agnostic binding (SAP native vs Odoo reconciliation-derived); the directory-clean condition for the as_of family
---

# clearing_date: source-agnostic as_of-close semantic field, bound per source, clean when as_of-shaped

**Status:** decided. Authority: operator grant `2026-10-06T02-48-59-826Z-f04c9003` (text_sha256 `f04c9003d5a09fe6ae3de47a8127f24d7e0188df2206242e918c3acbb119c0ab`; bc-exchange desk, method totp) — decides the clearing_date semantics and authorizes recording decided + the auditor conducting bounded reviews through acceptance at the then-current head + merge on a green exact head. Author: Architect SES-b9b0ef. Grounded at bc-core `origin/main` cc08875b, live `concept_registry`, and the Metric controller's read-only Odoo `v3_lc5` window. Companion lever to DEC-d0b66a (point_in_time); kept strictly separate from it.

## Context

The clean-directory work (DEC-ca8943, DEC-b36e15) left a family of directory members that reference `clearing_date` classed NOVEL pending a declaration of what clearing_date is and how a member using it is classified. clearing_date is also the field where a single semantic input ("the date an open item is cleared") is supplied very differently by two sources — a native column in SAP, an absent column in Odoo — so the declaration must state where that difference is resolved without changing the field's meaning or any metric contract. Unlike point_in_time, the relevant runtime (`as_of`) is already built and correct, so this ADR records built behaviour plus the source-agnostic binding principle.

## Decision

1. **clearing_date is a SOURCE-AGNOSTIC semantic canonical field** — "the date an open item is cleared" (`src/registry/seed/seed-standard-fields.ts:306`; objectClass `clearing`, representationTerm `date`). Its meaning is evaluated once (Invariant I) and is independent of any source's physical shape.

2. **clearing_date carries as_of CLOSE semantics.** A position is OPEN at reporting point P when its closing field (clearing_date) is absent OR `> P`; CLOSED by P when clearing_date is present AND `<= P`. This is implemented and correct at cc08875b: `src/boundary/governed-selection.ts:15` ("Open at P is DERIVED here"), `:127-129` (`open_at`), `:131-133` (`closed_at`), `:91-98` (`stampedDate` null on absent/invalid); `src/boundary/select-by-gate.ts:186-214` (`selectAsOf`, `selective: true`). There is NO declared-but-unbuilt runtime gap for the as_of path — contrast DEC-d0b66a, where the point_in_time runtime predicate is unbuilt.

3. **The per-source difference is resolved by BINDING (C-layer), never in the metric contract** (DEC-c220e4 source-agnosticism; "no formulas tied to fact shape — a Metric Contract declares semantic inputs and onboards a second source through binding without MC edits"). SAP binds clearing_date to its native column (seed `sourceAliases`, SAP `AUGDT`/`AUGBL`). Odoo binds it to a governed canonical derivation: `clearing_date(item) = MAX(account.partial.reconcile.max_date)` over the partials of the open item's `full_reconcile_id` on `account.move.line`; NULL when `full_reconcile_id` is NULL (the item is open: `reconciled = false`, `amount_residual != 0`). Both bindings produce the same semantic field; the metric contract is unchanged across sources (Invariant IV — references are explicit and per-source).

4. **Platform-plane clean condition.** A clearing_date directory member is CLEAN at the platform plane when it is shaped as an `as_of` member with clearing_date as the `closing_field` (the built, correct runtime of Decision 2). A member that mis-uses clearing_date — as a raw field, a `point_in_time` anchor, or a period filter — is NOT clean and must be RE-SHAPED to `as_of`. Classification is per-member on shape; this ADR declares the rule, it does not assert that every member is already correctly shaped.

5. **The Odoo binding is Phase-C tenant provisioning, not a platform-plane blocker.** The reconciliation-derived clearing_date binding (Decision 3, Odoo) is NOT built in bc-core today (`clearing_date` appears only in seeds and metric-contract field references; no derivation code at cc08875b). That binding is authored at tenant provisioning (C-layer, Phase-C, the Kaveri demo tenant) and does NOT block the platform-plane member DEFINITION from being clean — consistent with the platform-plane-only scope of the current drive. For SAP-shaped sources the field is native and immediately available.

6. **Foundation.** Meaning is evaluated once (I): clearing_date's as_of-close meaning is fixed; binding resolves the source (IV) without a metric-contract or evaluator edit, so there is no lower-layer compensation for an upper-layer gap (DEC-c48b0f). Repair location B (the semantic declaration) + C (the per-source binding). This is a design act — declaring a missing shape-semantic — not a detector. Contrast DEC-d0b66a: there the platform-plane runtime predicate was unbuilt; here the as_of runtime is built and only the tenant-plane Odoo binding is outstanding, a materially different and non-blocking situation.

## References

bc-core cc08875b: `src/boundary/governed-selection.ts:15,91-98,127-133`; `src/boundary/select-by-gate.ts:186-214`; `src/registry/seed/seed-standard-fields.ts:295-312`; `src/registry/seed/generate-gold-contracts.ts:163,308`; `src/registry/seed/metric-kpi-cfo.ts` (`ar_customer_payment_canonical` / `ap_vendor_payment_canonical` clearing_date references). Metric's Odoo v3_lc5 Q1–Q4 derivation spec (`account.partial.reconcile.max_date` over `full_reconcile_id`). DEC-c220e4 (source-agnosticism), DEC-ca8943 (entry gate), DEC-b36e15 (pool-readiness), DEC-d0b66a (point_in_time — companion lever, kept separate); `foundation/the-invariants.md`; `foundation/the-evaluation-boundaries.md`; `foundation/the-contract-grammar.md`.
