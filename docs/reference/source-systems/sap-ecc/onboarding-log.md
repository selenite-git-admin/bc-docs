---
uid: SRC-b4c92d-onboarding-log
slug: sap-ecc-onboarding-log
title: "SAP ECC — Onboarding Log"
description: "Dated onboarding-execution log for SAP ECC (customer-side + BareCount-side runs)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: enterprise-erp
subdomain: sap
focus: onboarding
docket_of: sap-ecc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# SAP ECC — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Chronology may be hand-authored, but **outcome/proof fields
> must be emitted or referenced** — each real run links a governed onboarding-session receipt (source scope,
> contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence digests). An
> author-entered "success" does not prove execution. Customer identity stays out of Git (pseudonymous UID only).

Chronological record of ECC onboarding runs. Runbook definitions live in [index.md](index.md) §7; this logs
their *execution* by reference to emitted receipts. One entry per onboarding attempt/session.

## Runbook (summary)
- **Customer-side:** Gateway-published OData (verify `SAP_GWFND` → activate service → technical Communication-type user → network path → **provision credential via governed secret-ingress**, yielding `credential_ref` + receipt → hand BareCount only the endpoint URL + `credential_ref`, never a raw secret) **or** ABAP Transport (import `ZBCNT_META_EXPORT` → run under licensed user → send JSON via the agreed governed channel). Detail: [index.md](index.md) §7.1–7.2.
- **BareCount-side:** per-tenant connection profile (`system_type_code: sap_ecc`, endpoint, auth, `sap_client`, gateway services) → smoke test `/$metadata` then one entity `$top=1`. Detail: [index.md](index.md) §7.3.

## Execution log
| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _no real-tenant onboarding yet_ | — | — | — | — | — (only bc-sdg simulator exercised — see [evidence.md](evidence.md)) |

<Per-run detail blocks below, newest first, when real onboarding begins.>
