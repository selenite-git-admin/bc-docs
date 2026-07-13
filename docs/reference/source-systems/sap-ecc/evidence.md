---
uid: SRC-b4c92d-evidence
slug: sap-ecc-evidence
title: "SAP ECC — Evidence"
description: "Proof entries for SAP ECC — no governed evidence yet (proof_status: designed); bc-sdg simulator run is ungoverned historical background; first-hand proof pending."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — evidence INDEX/projection; authority = audit substrate
domain: enterprise-erp
subdomain: sap
focus: evidence
docket_of: sap-ecc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
  - DEC-6cb4f3   # D385 — proof-status taxonomy
---

# SAP ECC — Evidence

> **Evidence is INDEXED here; audit authority lives in the audit substrate (D526 Amendment 1).** This page is a
> human-readable index/projection — **not** the evidence authority. Every substantive row must resolve to a
> governed, immutable/append-only, digest-bound (eventually signed) evidence record; the `Evidence UID/digest`
> column is that binding. Prose only summarizes the governed object.

Zero-claims rule (D385): no external "we work with SAP ECC" claim runs ahead of a first-hand entry. First-hand
proof is **entity/scope-specific**, never a whole-system promotion. Cover: [index.md](index.md).

## Ungoverned historical background (simulator / sandbox — NOT a maturity claim)

`proof_status` is **`designed`**: no governed evidence object exists for ECC. The simulator run below is
**ungoverned historical background** — it predates governed evidence emission, so its `Evidence UID/digest` is
**PENDING**, it is **narrative only and cannot support an audit decision or lift `proof_status`** (Codex P0-2/P1).
Minting the governed evidence object (populating the coordinates below) is what would promote maturity to
`shape_tested`. Required coordinates to make it audit-grade:

| Field | Value (to pin) |
|---|---|
| Date | 2026-04-28 |
| Conformance profile | bc-sdg **SAP ECC OData V2 simulator profile** (proves conformance to *this profile*, not SAP ECC) |
| Simulator build/version + source digest | ⧗ pin exact bc-sdg build + profile digest |
| Dataset / seed digest | ⧗ pin seed digest (~1,368 AR records — narrative until digest-bound) |
| Executor / runtime commit | ⧗ pin `SapOdataV2Executor` commit + runtime-component digest |
| Reader-flavor version | `sap-ecc-odata-v2` — ⧗ pin exact version |
| Test/run UID + assertions | ⧗ pin run UID + asserted checks (CSRF flow, `/Date()/` decode, `$skiptoken` paging) |
| Catalog/schema snapshot | ⧗ pin catalog root exercised |
| Result receipt + producer identity | ⧗ pin receipt + producing service identity |
| **Evidence UID/digest** | **PENDING — governed evidence object not yet emitted** |

Per **DEC-d2cdb9 (D384)** the simulator is **not** a real customer source; this establishes protocol/profile-shape correctness only.

## First-hand evidence (real customer/vendor instance)
| Date | Verified entities (scope) | Instance (pseudonymous UID) | Source release + catalog/mapping root | Metric snapshots (MCV) | Evidence UID/digest |
|---|---|---|---|---|---|
| _none — no first-hand proof_ | | | | | |

**No SAP ECC entity has been verified first-hand against a real customer instance.** Promotion to
`first_hand_proven` is per-entity/scope and requires a governed evidence UID here; update [index.md](index.md)
`proof_status` + `source_realization_refs[]` for that exact scope only. Customer identity stays out of Git —
pseudonymous UID + digest + allowed scope only; raw evidence lives in the restricted store.

## Source-realization packages & audit decisions (projection)
Metrics realized end-to-end against ECC (MCV + snapshot refs) will be **indexed here; audit authority lives in
the audit substrate.** This ties into the **D525** per-source-realization audit program: the SAP ECC realization
audit for the ~370-MCV population scopes its PASS/REJECT/OPERATOR_REVIEW to an exact realization package. This
docket renders each decision as a labelled "derived projection" (governed decision UID/digest), never as its own
authority; `source_realization_refs[]` / `audit_decision_refs[]` in [index.md](index.md) hold the UIDs.
