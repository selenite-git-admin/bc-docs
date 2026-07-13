---
uid: SRC-a4c6e9-onboarding-log
slug: zoho-books-onboarding-log
title: "Zoho Books — Onboarding Log"
description: "Dated onboarding-execution log for Zoho Books (customer-side + BareCount-side runs) — empty; no onboarding has occurred."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: accounting
subdomain: zoho
focus: onboarding
docket_of: zoho-books
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Zoho Books — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Chronology may be hand-authored, but **outcome/proof
> fields must be emitted or referenced** — each real run links a governed onboarding-session receipt (source
> scope, contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence digests). An
> author-entered "success" does not prove execution. Customer identity stays out of Git (pseudonymous UID
> only).

Chronological record of Zoho Books onboarding runs. Runbook definitions live in [index.md](index.md) §7;
this logs their *execution* by reference to emitted receipts. One entry per onboarding attempt/session.

## Runbook (summary)

- **Customer-side:** confirm plan + data center → create OAuth client (server-based or self client) in the
  customer's DC → grant read-only scopes for the agreed modules → select `organization_id`(s) →
  **provision client secret + refresh token via governed secret-ingress**, yielding `credential_ref` +
  receipt → hand BareCount only the DC/region, organization ID(s), and `credential_ref`, never a raw
  secret. Detail: [index.md](index.md) §7.1.
- **BareCount-side:** per-tenant connection profile (`system_type_code: zoho_books`, `region`,
  `organization_id`, `auth.credential_ref`) → smoke test: token refresh against the region's Accounts
  endpoint, `GET /organizations`, then one in-scope module list with `per_page=1`. Detail:
  [index.md](index.md) §7.2.

## Execution log

| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _no onboarding of any kind yet_ | — | — | — | — | — (no simulator run either — see [evidence.md](evidence.md)) |

<Per-run detail blocks below, newest first, when onboarding begins.>
