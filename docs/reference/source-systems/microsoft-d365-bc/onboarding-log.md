---
uid: SRC-e4a7b2-onboarding-log
slug: microsoft-d365-bc-onboarding-log
title: "Microsoft Dynamics 365 Business Central — Onboarding Log"
description: "Dated onboarding-execution log for Microsoft Dynamics 365 Business Central (customer-side + BareCount-side runs) — no run has ever been executed."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: enterprise-erp
subdomain: microsoft
focus: onboarding
docket_of: microsoft-d365-bc
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Microsoft Dynamics 365 Business Central — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Chronology may be hand-authored, but **outcome/proof fields
> must be emitted or referenced** — each real run links a governed onboarding-session receipt (source scope,
> contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence digests). An
> author-entered "success" does not prove execution. Customer identity stays out of Git (pseudonymous UID only).

Chronological record of Business Central onboarding runs. Runbook definitions live in [index.md](index.md) §7;
this logs their *execution* by reference to emitted receipts. One entry per onboarding attempt/session.

## Runbook (summary)
- **Customer-side:** API v2.0 S2S path (confirm subscription scope → Entra app registration with
  `API.ReadWrite.All` application permission + tenant-admin consent → Business Central **Microsoft Entra
  Applications** page entry with least-privilege read-only permission sets (applications cannot be SUPER) →
  select environment + companies → **provision credential via governed secret-ingress**, yielding
  `credential_ref` + receipt → hand BareCount only the Entra tenant ID + client ID + environment name +
  company IDs + `credential_ref`, never a raw secret) **or** custom-API extension path (deploy AL API pages →
  extend permission sets → record `{publisher}/{group}/{version}` coordinates). Detail:
  [index.md](index.md) §7.1–7.2.
- **BareCount-side:** per-tenant connection profile (`system_type_code: microsoft_d365_bc`, `entra_tenant_id`,
  `environment`, auth, `companies[]`) → smoke test: token → `GET /companies` → `$metadata` → one entity
  `$top=1`. Detail: [index.md](index.md) §7.3.

## Execution log
| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _no onboarding run has ever been executed_ | — | — | — | — | — (no simulator run either — see [evidence.md](evidence.md)) |

<Per-run detail blocks below, newest first, when onboarding begins.>
