---
uid: SRC-a4c6e9-evidence
slug: zoho-books-evidence
title: "Zoho Books — Evidence"
description: "Proof entries for Zoho Books — none of any kind (proof_status: designed); no simulator coverage, no governed evidence, no first-hand proof."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — evidence INDEX/projection; authority = audit substrate
domain: accounting
subdomain: zoho
focus: evidence
docket_of: zoho-books
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
  - DEC-6cb4f3   # D385 — proof-status taxonomy
---

# Zoho Books — Evidence

> **Evidence is INDEXED here; audit authority lives in the audit substrate (D526 Amendment 1).** This page is
> a human-readable index/projection — **not** the evidence authority. Every substantive row must resolve to a
> governed, immutable/append-only, digest-bound (eventually signed) evidence record; the `Evidence UID/digest`
> column is that binding. Prose only summarizes the governed object.

Zero-claims rule (D385): no external "we work with Zoho Books" claim runs ahead of a first-hand entry.
First-hand proof is **entity/scope-specific**, never a whole-system promotion. Cover: [index.md](index.md).

## Ungoverned historical background (simulator / sandbox)

**None.** Unlike SAP ECC, no bc-sdg simulator profile exists for Zoho Books, no executor has been built, and
no sandbox or trial organization has been exercised. There is no ungoverned historical background to record —
`proof_status` is **`designed`** on the strength of design documentation alone.

The coordinates a first (simulator- or sandbox-scoped) evidence entry would need to pin are listed below;
every one is ⧗ **PENDING** — nothing has been executed:

| Field | Value |
|---|---|
| Date | ⧗ PENDING — no run of any kind |
| Conformance profile | ⧗ PENDING (no Zoho Books simulator profile exists in bc-sdg) |
| Simulator/sandbox build/version + source digest | ⧗ PENDING |
| Dataset / seed digest | ⧗ PENDING |
| Executor / runtime commit | ⧗ PENDING (no executor exists) |
| Reader-flavor version | ⧗ PENDING (no flavor registered — `reader_flavor_versions: []`) |
| Test/run UID + assertions | ⧗ PENDING (candidate assertions when built: DC-correct token refresh, `organization_id` propagation, `page_context.has_more_page` paging, 429/44/45/1070 backoff) |
| Catalog/schema snapshot | ⧗ PENDING (`catalog_root: null`) |
| Result receipt + producer identity | ⧗ PENDING |
| **Evidence UID/digest** | **⧗ PENDING — no governed evidence object exists** |

## First-hand evidence (real customer/vendor instance)

| Date | Verified entities (scope) | Instance (pseudonymous UID) | Source edition + catalog/mapping root | Metric snapshots (MCV) | Evidence UID/digest |
|---|---|---|---|---|---|
| _none — no first-hand proof_ | | | | | |

**No Zoho Books entity has been verified first-hand against a real organization.** Promotion to
`first_hand_proven` is per-entity/scope and requires a governed evidence UID here; update
[index.md](index.md) `proof_status` + `source_realization_refs[]` for that exact scope only. Customer
identity stays out of Git — pseudonymous UID + digest + allowed scope only; raw evidence lives in the
restricted store.

## Source-realization packages & audit decisions (projection)

Metrics realized end-to-end against Zoho Books (MCV + snapshot refs) will be **indexed here; audit authority
lives in the audit substrate.** This ties into the **D525** per-source-realization audit program: any Zoho
Books realization audit scopes its PASS/REJECT/OPERATOR_REVIEW to an exact realization package. This docket
renders each decision as a labelled "derived projection" (governed decision UID/digest), never as its own
authority; `source_realization_refs[]` / `audit_decision_refs[]` in [index.md](index.md) hold the UIDs.
None exist.
