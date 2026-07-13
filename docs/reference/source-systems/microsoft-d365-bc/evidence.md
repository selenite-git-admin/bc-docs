---
uid: SRC-e4a7b2-evidence
slug: microsoft-d365-bc-evidence
title: "Microsoft Dynamics 365 Business Central — Evidence"
description: "Proof entries for Microsoft Dynamics 365 Business Central — no governed evidence, no ungoverned background, no simulator coverage (proof_status: designed); first-hand proof pending."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — evidence INDEX/projection; authority = audit substrate
domain: enterprise-erp
subdomain: microsoft
focus: evidence
docket_of: microsoft-d365-bc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
  - DEC-6cb4f3   # D385 — proof-status taxonomy
---

# Microsoft Dynamics 365 Business Central — Evidence

> **Evidence is INDEXED here; audit authority lives in the audit substrate (D526 Amendment 1).** This page is a
> human-readable index/projection — **not** the evidence authority. Every substantive row must resolve to a
> governed, immutable/append-only, digest-bound (eventually signed) evidence record; the `Evidence UID/digest`
> column is that binding. Prose only summarizes the governed object.

Zero-claims rule (D385): no external "we work with Business Central" claim runs ahead of a first-hand entry.
First-hand proof is **entity/scope-specific**, never a whole-system promotion. Cover: [index.md](index.md).

## Ungoverned historical background — none exists

`proof_status` is **`designed`**, and — plainly — **there is no evidence of any kind, governed or ungoverned**:

- **No simulator coverage exists.** bc-sdg has no Business Central simulator profile (contrast SAP ECC, which
  has an ungoverned simulator run in its docket). Nothing to index, not even as narrative background.
- **No executor has ever run.** No API v2.0 call, no OData read, no webhook handshake, no Microsoft Entra
  token exchange has been executed by BareCount against any Business Central instance, real or simulated.
- **No customer or vendor instance has ever been touched.** All current design is documentation-driven
  (Learn application reference + BCApps source + API v2.0 docs — see [index.md](index.md) §6.5 and
  [catalog.md](catalog.md)).

Coordinates that would need pinning for the *first* evidence entry of any kind — **all ⧗ PENDING, nothing to
fill today**:

| Field | Value |
|---|---|
| Date | ⧗ PENDING — no run has occurred |
| Conformance target (profile or real instance + base-application version) | ⧗ PENDING |
| Simulator/instance build + source digest | ⧗ PENDING |
| Dataset / seed digest | ⧗ PENDING |
| Executor / runtime commit | ⧗ PENDING — no executor exists |
| Reader-flavor version | ⧗ PENDING — `microsoft-d365-bc-rest-v2` / `-custom-api` / `-webhook` are candidate labels only |
| Test/run UID + assertions | ⧗ PENDING |
| Catalog/schema snapshot | ⧗ PENDING — no seed load executed (see [catalog.md](catalog.md)) |
| Result receipt + producer identity | ⧗ PENDING |
| **Evidence UID/digest** | **⧗ PENDING — no evidence object exists** |

## First-hand evidence (real customer/vendor instance)
| Date | Verified entities (scope) | Instance (pseudonymous UID) | Source version + catalog/mapping root | Metric snapshots (MCV) | Evidence UID/digest |
|---|---|---|---|---|---|
| _none — no first-hand proof_ | | | | | |

**No Business Central entity has been verified first-hand against any instance.** Promotion to
`first_hand_proven` is per-entity/scope and requires a governed evidence UID here; update [index.md](index.md)
`proof_status` + `source_realization_refs[]` for that exact scope only. Customer identity stays out of Git —
pseudonymous UID + digest + allowed scope only; raw evidence lives in the restricted store.

## Source-realization packages & audit decisions (projection)
Metrics realized end-to-end against Business Central (MCV + snapshot refs) will be **indexed here; audit
authority lives in the audit substrate** (D525 per-source-realization audit program: PASS/REJECT/
OPERATOR_REVIEW scoped to an exact realization package). This docket renders each decision as a labelled
"derived projection" (governed decision UID/digest), never as its own authority;
`source_realization_refs[]` / `audit_decision_refs[]` in [index.md](index.md) hold the UIDs. Today both are
empty.
