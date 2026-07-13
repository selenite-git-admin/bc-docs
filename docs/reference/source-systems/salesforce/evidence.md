---
uid: SRC-a3c7e1-evidence
slug: salesforce-evidence
title: "Salesforce — Evidence"
description: "Proof entries for Salesforce — no governed evidence yet (proof_status: designed); bc-sdg simulator run and executor unit tests are ungoverned historical background; first-hand proof pending."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — evidence INDEX/projection; authority = audit substrate
domain: crm
subdomain: salesforce
focus: evidence
docket_of: salesforce
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
  - DEC-6cb4f3   # D385 — proof-status taxonomy
---

# Salesforce — Evidence

> **Evidence is INDEXED here; audit authority lives in the audit substrate (D526 Amendment 1).** This page is a
> human-readable index/projection — **not** the evidence authority. Every substantive row must resolve to a
> governed, immutable/append-only, digest-bound (eventually signed) evidence record; the `Evidence UID/digest`
> column is that binding. Prose only summarizes the governed object.

Zero-claims rule (D385): no external "we work with Salesforce" claim runs ahead of a first-hand entry.
First-hand proof is **entity/scope-specific**, never a whole-system promotion. Cover: [index.md](index.md).

## Ungoverned historical background (simulator / unit tests — NOT a maturity claim)

`proof_status` is **`designed`**: no governed evidence object exists for Salesforce. This is a **downgrade from
the flat page's `shape_tested`** — that claim rested on the background below, which predates governed evidence
emission, so its `Evidence UID/digest` is **PENDING**, it is **narrative only and cannot support an audit
decision or lift `proof_status`**. Minting the governed evidence object (populating the coordinates below) is
what would promote maturity to `shape_tested`. Required coordinates to make it audit-grade:

| Field | Value (to pin) |
|---|---|
| Date | 2026-04-28 (flat-page `last_verified_at` — exact run date ⧗ pin) |
| Conformance profile | bc-sdg **Salesforce REST simulator profile** (`bc-sdg/src/simulators/salesforce/rest-server.ts`, port 6110 — standard Salesforce REST JSON envelope, SOQL endpoint, 15/18-char ID format; proves conformance to *this profile*, not Salesforce) |
| Simulator build/version + source digest | ⧗ pin exact bc-sdg build + profile digest |
| Dataset / seed digest | ⧗ pin generator seed digest (deterministic `generateSalesforceData` seed — narrative until digest-bound) |
| Executor / runtime commit | ⧗ pin `SfdcRestExecutor` commit (`bc-core/src/boundary/reader-runtime/executors/sfdc-rest.executor.ts`) + runtime-component digest |
| Unit-test run | ⧗ pin `sfdc-rest.executor.spec.ts` commit + asserted checks (pagination via `nextRecordsUrl`, SOQL query encoding, OAuth bearer auth) |
| Reader-flavor version | `salesforce-rest-v66` — ⧗ pin exact version |
| Test/run UID + assertions | ⧗ pin run UID + asserted checks |
| Catalog/schema snapshot | ⧗ pin catalog root exercised |
| Result receipt + producer identity | ⧗ pin receipt + producing service identity |
| **Evidence UID/digest** | **PENDING — governed evidence object not yet emitted** |

The simulator is **not** a real customer source; at best this establishes protocol/profile-shape correctness
only.

## First-hand evidence (real customer/vendor instance)
| Date | Verified entities (scope) | Instance (pseudonymous UID) | Org API version + catalog/mapping root | Metric snapshots (MCV) | Evidence UID/digest |
|---|---|---|---|---|---|
| _none — no first-hand proof_ | | | | | |

**No Salesforce entity has been verified first-hand against a real customer org.** Promotion to
`first_hand_proven` is per-entity/scope and requires a governed evidence UID here; update [index.md](index.md)
`proof_status` + `source_realization_refs[]` for that exact scope only. Customer identity stays out of Git —
pseudonymous UID + digest + allowed scope only; raw evidence lives in the restricted store.

## Source-realization packages & audit decisions (projection)
Metrics realized end-to-end against Salesforce (MCV + snapshot refs) will be **indexed here; audit authority
lives in the audit substrate.** This ties into the **D525** per-source-realization audit program: any Salesforce
realization audit scopes its PASS/REJECT/OPERATOR_REVIEW to an exact realization package. This docket renders
each decision as a labelled "derived projection" (governed decision UID/digest), never as its own authority;
`source_realization_refs[]` / `audit_decision_refs[]` in [index.md](index.md) hold the UIDs.
