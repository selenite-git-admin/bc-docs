---
title: "D409 cc__intangible_asset — PARKED"
date: 2026-05-17
authority: DEC-b8ec00 (D409 — BF-BO Catalog Expansion Factory)
sop: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md
scope_decision: bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-intangible-asset-cc-scope-decision-DEC-b8ec00.md
gap_report: bc-core/scripts/audit-output/d409-intangible-asset-first-apply-bo-approval-gap-2026-05-17.md
session: SES-17fd55
type: parking-record
status: PARKED_GOVERNANCE_GAP
sublane: GREENFIELD_BO_COMPOSITION
---

# D409 cc__intangible_asset — PARKED

**Status:** `PARKED_GOVERNANCE_GAP / GREENFIELD_BO_COMPOSITION`

## Why

- BF `intangible_asset_amortization_expense_amount` is **admitted** (certified_catalog, US-GAAP, ASC 350-30-35-6) and remains in the catalog.
- BO `intangible_asset` is **created** but in `draft` and not approvable with one field. BO approval requires ≥4 fields covering identifier / dimension / temporal / business-key roles AND a `certify`-action ledger row per BF (D409's `admit_bf_from_candidate_import` action doesn't satisfy the gate).
- CC `cc__intangible_asset` is **blocked** until the BO is approved with a real composition.

## Decision

**Do not chase row-by-row.** The greenfield-CC path needs a different shape than the "narrow first apply" doctrine — at minimum a wider initial BO composition + a bridge from D409's admission semantics to BO approval's SDA-evidence requirement. Both are governance work, not factory work. The factory machinery is intact; cc__intangible_asset waits.

## What's preserved

- BF `intangible_asset_amortization_expense_amount` in `certified_catalog` (no rollback).
- BO `intangible_asset` row in `draft` with 1 measure-role field (no rollback).
- Apply script at `bc-core/scripts/apply-d409-intangible-asset-first-apply.mjs` is idempotent on the partial state and reusable when the parking lifts.

## When to revisit

When the operator decides to:
1. **Author 4+ more BFs** for the BO composition (identifier / dimension / temporal / business-key roles), AND
2. Either **bridge the SDA-evidence gap** via `POST /api/standard-fields/bulk-certify` after admission, OR **change the BO approval gate** to accept `admit_bf_from_candidate_import` as equivalent to `certify` (governance change).

Until then, do not retry, do not over-design, do not chase.

## Implication for the scope decision

The scope decision (bc-docs-v3@a9bf375) chose "broad CC scope, narrow first apply". This works for binding into existing CCs (cc__credit, cc__asset). For greenfield CCs the "narrow first apply" doctrine is incomplete — the BO approval gate enforces a minimum-coherence floor that no single-BF composition can clear. A future scope-decision revision (when the operator next opens cc__intangible_asset) should record this distinction.

## References

- Scope decision: `bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-intangible-asset-cc-scope-decision-DEC-b8ec00.md`
- BO approval gap report: `bc-core/scripts/audit-output/d409-intangible-asset-first-apply-bo-approval-gap-2026-05-17.md`
- Apply script (idempotent): `bc-core/scripts/apply-d409-intangible-asset-first-apply.mjs`
