---
uid: SRC-a8c3e7-onboarding-log
slug: odoo-erp-onboarding-log
title: "Odoo ERP — Onboarding Log"
description: "Dated onboarding-execution log for Odoo ERP (customer-side + BareCount-side runs) — no runs yet."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: enterprise-erp
subdomain: odoo
focus: onboarding
docket_of: odoo-erp
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Odoo ERP — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Chronology may be hand-authored, but **outcome/proof fields
> must be emitted or referenced** — each real run links a governed onboarding-session receipt (source scope,
> contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence digests). An
> author-entered "success" does not prove execution. Customer identity stays out of Git (pseudonymous UID only).

Chronological record of Odoo ERP onboarding runs. Runbook definitions live in [index.md](index.md) §7; this logs
their *execution* by reference to emitted receipts. One entry per onboarding attempt/session.

## Runbook (summary)
- **Customer-side:** confirm hosting variant / edition / plan / exact version (Online external-API access is
  plan-gated) → dedicated read-only API user → API key (Preferences → Account Security → New API Key) → network
  path → **provision credential via governed secret-ingress**, yielding `credential_ref` + receipt → hand
  BareCount only the server URL, database name, API-user login, `credential_ref`, and installed-module
  inventory — never a raw key. Detail: [index.md](index.md) §7.1.
- **BareCount-side:** per-tenant connection profile (`system_type_code: odoo_erp`, endpoint, `database_name`,
  `odoo_version`, `auth.method: odoo_apikey`, `auth.credential_ref`) → smoke test authenticate +
  `res.company` `search_read` (limit 1) + `fields_get` on one in-scope model. Detail: [index.md](index.md) §7.2.

## Execution log
| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _no onboarding run of any kind yet_ | — | — | — | — | — (no executor exists; no instance — real or simulated — ever exercised; see [evidence.md](evidence.md)) |

<Per-run detail blocks below, newest first, when onboarding begins.>
