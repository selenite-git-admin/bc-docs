---
uid: SRC-1b8e5a-onboarding-log
slug: oracle-fusion-onboarding-log
title: "Oracle Fusion Cloud ERP — Onboarding Log"
description: "Dated onboarding-execution log for Oracle Fusion Cloud ERP (customer-side + BareCount-side runs) — no run has ever been executed."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: enterprise-erp
subdomain: oracle
focus: onboarding
docket_of: oracle-fusion
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Oracle Fusion Cloud ERP — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Chronology may be hand-authored, but **outcome/proof fields
> must be emitted or referenced** — each real run links a governed onboarding-session receipt (source scope,
> contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence digests). An
> author-entered "success" does not prove execution. Customer identity stays out of Git (pseudonymous UID only).

Chronological record of Oracle Fusion onboarding runs. Runbook definitions live in [index.md](index.md) §7; this
logs their *execution* by reference to emitted receipts. One entry per onboarding attempt/session.

## Runbook (summary)
- **Customer-side:** REST path (confirm subscription scope → Confidential Application in the OCI IAM identity
  domain → read-only integration user → **provision credential via governed secret-ingress**, yielding
  `credential_ref` + receipt → hand BareCount only the pod base URL + `credential_ref` + scope, never a raw
  secret) **or** BICC path (provision BICC + enable data stores → configure extract target → grant read access
  via governed secret-ingress). Detail: [index.md](index.md) §7.1–7.2.
- **BareCount-side:** per-tenant connection profile (`system_type_code: oracle_fusion`, endpoint, auth,
  `module_scopes[]`) → smoke test: token + one resource `describe` + one single-row read. Detail:
  [index.md](index.md) §7.3.

## Execution log
| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _no onboarding run has ever been executed_ | — | — | — | — | — (no simulator run either — see [evidence.md](evidence.md)) |

<Per-run detail blocks below, newest first, when onboarding begins.>
