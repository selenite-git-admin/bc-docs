---
uid: SRC-b3e7c2-evidence
slug: tally-prime-evidence
title: "Tally Prime — Evidence"
description: "Proof entries for Tally Prime — none of any kind (proof_status: designed); no simulator coverage, no executor, no instance ever read; first-hand proof pending."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — evidence INDEX/projection; authority = audit substrate
domain: accounting
subdomain: tally
focus: evidence
docket_of: tally-prime
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
  - DEC-6cb4f3   # D385 — proof-status taxonomy
---

# Tally Prime — Evidence

> **Evidence is INDEXED here; audit authority lives in the audit substrate (D526 Amendment 1).** This page is a
> human-readable index/projection — **not** the evidence authority. Every substantive row must resolve to a
> governed, immutable/append-only, digest-bound (eventually signed) evidence record; the `Evidence UID/digest`
> column is that binding. Prose only summarizes the governed object.

Zero-claims rule (D385): no external "we work with Tally" claim runs ahead of a first-hand entry. First-hand
proof is **entity/scope-specific**, never a whole-system promotion. Cover: [index.md](index.md).

## Current state — no evidence of any kind

`proof_status` is **`designed`** and, stated plainly: **there is nothing to index.**

- **No governed evidence object** exists for Tally Prime.
- **No simulator coverage** — unlike SAP ECC, there is no bc-sdg Tally profile, so not even *ungoverned
  historical background* exists to record here.
- **No executor** for any Tally surface has ever run, against anything.
- **No customer or vendor instance** has ever been read.

The first evidence entry of any kind would be a shape exercise (simulator profile or sandbox instance) whose
governed evidence object pins the coordinates below. All values are **⧗ PENDING — no run exists to pin**:

| Field | Value |
|---|---|
| Date | ⧗ PENDING — no run |
| Conformance profile / target | ⧗ PENDING (simulator profile or exact-release TallyPrime instance) |
| Simulator/instance build + release + source digest | ⧗ PENDING |
| Dataset / seed digest | ⧗ PENDING |
| Executor / runtime commit | ⧗ PENDING (no executor exists) |
| Reader-flavor version | ⧗ PENDING (no flavor registered — [index.md](index.md) §2) |
| Test/run UID + assertions | ⧗ PENDING |
| Catalog/schema snapshot | ⧗ PENDING ([catalog.md](catalog.md): no seed loaded) |
| Result receipt + producer identity | ⧗ PENDING |
| **Evidence UID/digest** | **⧗ PENDING — no governed evidence object exists** |

Minting a governed evidence object with these coordinates populated is what would promote maturity to
`shape_tested` — a simulator/sandbox run without the governed object does **not** lift `proof_status`.

## First-hand evidence (real customer/vendor instance)
| Date | Verified entities (scope) | Instance (pseudonymous UID) | Source release + catalog/mapping root | Metric snapshots (MCV) | Evidence UID/digest |
|---|---|---|---|---|---|
| _none — no first-hand proof_ | | | | | |

**No Tally Prime entity has been verified first-hand against a real instance.** Promotion to
`first_hand_proven` is per-entity/scope and requires a governed evidence UID here; update [index.md](index.md)
`proof_status` + `source_realization_refs[]` for that exact scope only. Customer identity stays out of Git —
pseudonymous UID + digest + allowed scope only; raw evidence lives in the restricted store.

## Source-realization packages & audit decisions (projection)
Metrics realized end-to-end against Tally Prime (MCV + snapshot refs) will be **indexed here; audit authority
lives in the audit substrate.** No source-realization audit (D525) exists for Tally Prime. This docket renders
any future decision as a labelled "derived projection" (governed decision UID/digest), never as its own
authority; `source_realization_refs[]` / `audit_decision_refs[]` in [index.md](index.md) hold the UIDs.
