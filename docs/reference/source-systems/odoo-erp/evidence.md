---
uid: SRC-a8c3e7-evidence
slug: odoo-erp-evidence
title: "Odoo ERP — Evidence"
description: "Proof entries for Odoo ERP — no governed evidence and no ungoverned historical background of any kind (proof_status: designed); first-hand proof pending."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — evidence INDEX/projection; authority = audit substrate
domain: enterprise-erp
subdomain: odoo
focus: evidence
docket_of: odoo-erp
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
  - DEC-6cb4f3   # D385 — proof-status taxonomy
---

# Odoo ERP — Evidence

> **Evidence is INDEXED here; audit authority lives in the audit substrate (D526 Amendment 1).** This page is a
> human-readable index/projection — **not** the evidence authority. Every substantive row must resolve to a
> governed, immutable/append-only, digest-bound (eventually signed) evidence record; the `Evidence UID/digest`
> column is that binding. Prose only summarizes the governed object.

Zero-claims rule (D385): no external "we work with Odoo" claim runs ahead of a first-hand entry. First-hand
proof is **entity/scope-specific**, never a whole-system promotion. Cover: [index.md](index.md).

## Connector-scope reachability evidence (2026-08-10) — NOT admission, NOT a maturity claim

A JSON-RPC reader executor (`OdooJsonRpcProtocolReader`) has been **built** (bc-core PR #675, DEC-12558e) and
registered as connectors (`odoo-jsonrpc` + `odoo-ent-v19`, status `available`), and the real `pilot_ent` Odoo 19
EE instance has been **exercised for connector reachability**: rung-1 (container-internal, authenticated —
`login_uid=2`, res.company + 49,720 account.move + 366 res.partner) and rung-3 (external endpoint reachable, Odoo
`19.0+e-20260806`, 200/96ms). Both read-only (S-32).

This is **connector-reach evidence, not admission**: no Source Object / Canonical Object / Metric Snapshot has
been produced through the BareCount chain (OC/CC/MC held under **D555**), and **no governed
source-realization/audit object has been minted**. `proof_status` therefore stays **`designed`** — the maturity
ladder measures admission/realization evidence, which connector reachability does not satisfy. Governance trail
for the reachability evidence: bc-core #675 (`d78e1747`) / #676, DevHub CHG-4a10b5; minting a governed
proof-scope/evidence object to formally advance `proof_status` is a pending follow-up.

(No simulator/sandbox profile exists for Odoo ERP — unlike SAP ECC's ungoverned bc-sdg run. The evidence above is
against the real `pilot_ent` instance, connector-scope only.)

## Audit-grade coordinates for the first evidence object (all ⧗ PENDING)

Minting a governed evidence object with these coordinates populated is what would promote maturity to
`shape_tested`. Nothing below is pinned today:

| Field | Value (to pin) |
|---|---|
| Date | ⧗ no run has occurred |
| Conformance profile | ⧗ none exists (an Odoo simulator/sandbox profile would prove conformance to *that profile*, not Odoo) |
| Simulator/sandbox build + source digest | ⧗ PENDING |
| Dataset / seed digest | ⧗ PENDING |
| Executor / runtime commit | ⧗ PENDING (no executor built — [index.md](index.md) §2, §8) |
| Reader-flavor version | ⧗ PENDING (no flavor registered) |
| Test/run UID + assertions | ⧗ PENDING (candidate checks: authenticate flow, domain-DSL serialization, `offset`/`limit` paging, `fields_get` harvest) |
| Catalog/schema snapshot | ⧗ PENDING (`catalog_root: null`) |
| Result receipt + producer identity | ⧗ PENDING |
| **Evidence UID/digest** | **PENDING — no governed evidence object exists** |

## First-hand evidence (real customer/vendor instance)
| Date | Verified entities (scope) | Instance (pseudonymous UID) | Source release + catalog/mapping root | Metric snapshots (MCV) | Evidence UID/digest |
|---|---|---|---|---|---|
| _none — no first-hand proof_ | | | | | |

**No Odoo ERP entity has been verified first-hand against a real customer instance.** Promotion to
`first_hand_proven` is per-entity/scope and requires a governed evidence UID here; update [index.md](index.md)
`proof_status` + `source_realization_refs[]` for that exact scope only. Customer identity stays out of Git —
pseudonymous UID + digest + allowed scope only; raw evidence lives in the restricted store.

## Source-realization packages & audit decisions (projection)

Metrics realized end-to-end against Odoo ERP (MCV + snapshot refs) will be **indexed here; audit authority lives
in the audit substrate.** Under the **D525** per-source-realization audit program, any future Odoo ERP
realization audit scopes its PASS/REJECT/OPERATOR_REVIEW to an exact realization package. This docket renders
each decision as a labelled "derived projection" (governed decision UID/digest), never as its own authority;
`source_realization_refs[]` / `audit_decision_refs[]` in [index.md](index.md) hold the UIDs.
