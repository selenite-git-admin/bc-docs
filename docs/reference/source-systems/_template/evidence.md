---
uid: SRC-TEMPLATE-evidence
slug: _template-evidence
title: "<System Name> — Evidence"
description: "Proof entries for <System Name> — simulator runs, first-hand verifications, metric snapshots realized."
type: source-systems-docket
status: draft
authority_role: projection      # D526 Amendment 1 — evidence INDEX/projection; authority = audit substrate
domain: <domain>
subdomain: <vendor-family>
focus: evidence
docket_of: _template
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
  - DEC-6cb4f3   # D385 — proof-status taxonomy
---

# <System Name> — Evidence

> **Evidence is INDEXED here; audit authority lives in the audit substrate (D526 Amendment 1).** This page is
> a human-readable evidence index/projection — **not** the evidence authority. Every substantive row resolves
> to a governed, immutable/append-only, digest-bound (eventually signed) evidence record. The `Ref` column
> must be a governed evidence UID/digest, not a narrative pointer; prose only summarizes that object.

Zero-claims rule (D385): external claims run only as far as first-hand proof. First-hand proof is
**entity/scope-specific**, never a whole-system promotion. Each row binds an exact source-realization coordinate.

## Shape-tested evidence (simulator / sandbox)
| Date | Conformance profile + sim build | Dataset/seed digest | Executor/runtime + reader-flavor version | Assertions/run UID | Evidence UID/digest |
|---|---|---|---|---|---|
| _none yet_ | | | | | |

> A simulator proves conformance to a **declared simulator profile**, not the real source system. Name the exact profile and build.

## First-hand evidence (real customer/vendor instance)
| Date | Verified entities (scope) | Instance (pseudonymous UID) | Source release + catalog/mapping root | Metric snapshots (MCV) | Evidence UID/digest |
|---|---|---|---|---|---|
| _none yet — no first-hand proof_ | | | | | |

> Customer identity stays out of Git — pseudonymous UID + digest + allowed scope only. Raw evidence lives in the restricted store.

## Source-realization packages & audit decisions (projection)
<Governed source-realization-package UIDs and their signed audit decisions (PASS/REJECT/OPERATOR_REVIEW),
decided in the audit substrate per D525. Rendered here as a "derived projection" with exact decision UID/digest;
never restated as this docket's authority. Update `source_realization_refs[]` / `audit_decision_refs[]` in
[index.md](index.md) accordingly.>
