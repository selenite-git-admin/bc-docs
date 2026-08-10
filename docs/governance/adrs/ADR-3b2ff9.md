---
uid: DEC-3b2ff9
title: "Source-system approval is a derived projection of leaf approval — the identity tier is never asserted approved"
description: "Extends DEC-3078ce/D557 to the catalog identity tier: a module/version/system is 'approved' iff it transitively contains an approved (evidence-verified) object; approval is derived on read, never born-approved and never PATCH-set on the identity tier. Registered = admitted; approved = has evidence-verified content."
status: implemented
date: 2026-08-08T06:02:07.306Z
project: bc-core
domain: sources
subdomain: source-catalog
focus: governance
---

> **Implemented 2026-08-10** — bc-core PR #673 (merge `a73608e`), scoped to the **system tier only** per Codex disposition ACCEPTED-WITH-BOUNDARY (SHA-256 `D4D28893…C9D73F`). `effectiveCatalogStatus` is computed on read across the plain, enriched, and detail source-system paths (approved iff stored=`approved` OR an approved descendant object EXISTS); the `approved` filter is effective-aware. Live-verified: odoo stored=`registered` → effective=`approved`; grandfathered SAP rows unaffected. Version/module tiers deferred to TSK-3e933a. Companion bc-admin UI merged (`2875135`).

# Source-system approval is a derived projection of leaf approval — the identity tier is never asserted approved

## Context

The operator delegated the rule after the first Odoo admission showed approved objects under a registered system row, hiding the system from the approved-systems view. Deriving identity-tier approval from evidence-verified leaf approval (rather than adding an assertable identity-tier status) is the only option that cannot produce an approved-but-unverified envelope, adds no ceremony that catches a real defect, and stays coherent with the platform's projection-not-stored and earn-don't-assert doctrines (D557/D548/D526/D162 r2). Decided at the doctrine layer per the D541 fourth-gate question rather than compensated by a read filter.

## Decision

**Context.** DEC-3078ce (D557) made object and field approval evidence-bound governed acts but left the catalog IDENTITY tier (source_system / source_version / source_module) unspecified. The first live Odoo admission (2026-08-08) exposed the gap: 41 objects and 1,541 fields under `odoo / enterprise 19.0 / account` reached `approved/verified`, yet the system, version, and module rows stayed `registered` (born so at admission), so the bc-admin 'Approved source systems' view — which filters on system-tier `catalog_status` — hid Odoo entirely. The question the gap poses: what makes a source *system* approved?

**Decision — identity-tier approval is DERIVED, never asserted.**

1. **Derivation rule (bottom-up, transitive).** A module is approved-effective iff it has ≥1 approved object; a version iff it has ≥1 approved module; a system iff it has ≥1 approved version. The recursion bottoms out at object approval, which is evidence-bound under D557 pt 2/3 (verified against a hash-identified `source_catalog_artefact`, then operator-approved). Therefore an 'approved system' transitively means: this system has at least one operator-approved, evidence-verified piece of content — a status that cannot lie, because there is no way to assert it over empty or unverified content.

2. **No assertion on the identity tier.** No born-approved (identity rows are born `registered` at admission, as they already are), and no PATCH-to-approved. This extends D557 pt 3's stripping of status from the object/field update DTOs upward: the system/version/module update surfaces must not set an `approved` status either. The only operator-controlled identity-tier lifecycle is retirement — `registered` (active) → `deprecated` → `archived` — which are decisions about the identity itself, out of scope here.

3. **Computed on read, not stored.** Effective approval is a projection derived at query time, never a stored derivable column (D162 rule 2), directly analogous to DEC-b049f6/D548 making metric readiness a projection (McfReadinessProjection) rather than a stored dial, and to DEC-8570d4/D526's 'docket is a projection, not authority'.

**Rationale.** Earn-don't-assert is D557's core; this carries it up the identity chain so the same drift class — an 'approved envelope' sitting over unverified or absent content — is impossible at every tier, not just the leaf. A second, explicit operator approval gate at the identity tier would catch nothing the leaf approval act does not already gate (governance-must-earn-its-keep: name the defect a gate catches, or don't build it). Deriving instead of storing removes the demotion-drift hazard (an identity row left 'approved' after its last approved child is archived).

**Consequences (reviewed follow-up units — NOT part of this decision, NOT built here).**
- a. bc-core read model: the systems/versions/modules list endpoints and the 'Approved source systems' filter compute effective approval from leaf approval. Under this rule Odoo appears on the default approved view once ≥1 of its objects is approved (already true for the account module); until that unit ships, the 'Show registered' toggle is how the row is seen. A stopgap PATCH of the odoo system row to 'approved' is FORBIDDEN by this very decision.
- b. SAP reconciliation: the grandfathered SAP identity rows carry stored `catalog_status='approved'`. Transition predicate during migration: effective_approved = (stored = 'approved') OR (has ≥1 approved child) — so SAP never regresses. A later DBCP may backfill SAP identity rows to `registered` once the derived read model is authoritative; deferred under one-then-many, not required for Odoo.
- c. Retirement lifecycle (deprecated/archived) on the identity tier stays a separate explicit operator concern; this decision does not define it.

**Status:** decided as doctrine; implementation is reviewed follow-up units under the standard flow.
