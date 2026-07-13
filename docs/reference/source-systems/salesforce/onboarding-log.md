---
uid: SRC-a3c7e1-onboarding-log
slug: salesforce-onboarding-log
title: "Salesforce — Onboarding Log"
description: "Dated onboarding-execution log for Salesforce (customer-side + BareCount-side runs)."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: crm
subdomain: salesforce
focus: onboarding
docket_of: salesforce
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Salesforce — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Chronology may be hand-authored, but **outcome/proof fields
> must be emitted or referenced** — each real run links a governed onboarding-session receipt (source scope,
> contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence digests). An
> author-entered "success" does not prove execution. Customer identity stays out of Git (pseudonymous UID only).

Chronological record of Salesforce onboarding runs. Runbook definitions live in [index.md](index.md) §7; this
logs their *execution* by reference to emitted receipts. One entry per onboarding attempt/session.

## Runbook (summary)
- **Customer-side:** verify API entitlement (edition or Professional Web Services API purchase) → create the
  connected app / External Client App with the agreed OAuth flow (client credentials with a designated execution
  user, or JWT bearer with an uploaded X.509 certificate) → dedicated integration user with API Enabled +
  read-only permission sets scoped to the agreed objects → IP relaxation / trusted ranges → **provision the
  consumer secret or JWT signing key via governed secret-ingress**, yielding `credential_ref` + receipt → hand
  BareCount only the My Domain URL, org ID, consumer key, and `credential_ref`, never a raw secret or private
  key. Detail: [index.md](index.md) §7.1.
- **BareCount-side:** per-tenant connection profile (`system_type_code: salesforce`, instance URL, org ID,
  pinned API version, auth method, `credential_ref`, agreed objects) → smoke test Describe Global then
  `SELECT Id FROM Account LIMIT 1`. Detail: [index.md](index.md) §7.2.

## Execution log
| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _no real-org onboarding yet_ | — | — | — | — | — (only bc-sdg simulator exercised — see [evidence.md](evidence.md)) |

<Per-run detail blocks below, newest first, when real onboarding begins.>
