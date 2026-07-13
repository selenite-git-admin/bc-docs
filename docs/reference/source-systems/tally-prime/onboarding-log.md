---
uid: SRC-b3e7c2-onboarding-log
slug: tally-prime-onboarding-log
title: "Tally Prime — Onboarding Log"
description: "Dated onboarding-execution log for Tally Prime (customer-side + BareCount-side runs) — no runs have ever occurred."
type: source-systems-docket
status: published
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: accounting
subdomain: tally
focus: onboarding
docket_of: tally-prime
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# Tally Prime — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Chronology may be hand-authored, but **outcome/proof fields
> must be emitted or referenced** — each real run links a governed onboarding-session receipt (source scope,
> contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence digests). An
> author-entered "success" does not prove execution. Customer identity stays out of Git (pseudonymous UID only).

Chronological record of Tally Prime onboarding runs. Runbook definitions live in [index.md](index.md) §7; this
logs their *execution* by reference to emitted receipts. One entry per onboarding attempt/session.

## Runbook (summary)
- **Customer-side (live path):** confirm licence + exact release/TDL customizations → enable HTTP server (default port 9000) and/or ODBC → pin in-scope companies → choose network path (VPN or agent outbound tunnel; direct internet exposure of the gateway port is not an accepted path) → **provision any credential/VPN/agent secret via governed secret-ingress**, yielding `credential_ref` + receipt → hand BareCount only host/port + `credential_ref` + company list, never a raw secret. Detail: [index.md](index.md) §7.1.
- **Customer-side (export-drop path):** load the BareCount-published TDL export definition (⧗ not yet authored) → run for the agreed company/period scope → deliver files via the agreed governed channel. Detail: [index.md](index.md) §7.2.
- **BareCount-side:** per-tenant connection profile (`system_type_code: tally_prime`, bridge method, host/port, `credential_ref`, companies) → smoke test: one minimal XML `Export` read with the company loaded. Detail: [index.md](index.md) §7.3.

## Execution log
| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _no onboarding run has ever occurred_ | — | — | — | — | — (no simulator exercise exists either — see [evidence.md](evidence.md)) |

<Per-run detail blocks below, newest first, when onboarding begins.>
