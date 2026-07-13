---
uid: SRC-TEMPLATE-onboarding-log
slug: _template-onboarding-log
title: "<System Name> — Onboarding Log"
description: "Dated per-onboarding runbook-execution log for <System Name> (customer-side + BareCount-side)."
type: source-systems-docket
status: draft
authority_role: projection      # D526 Amendment 1 — chronology + links; outcomes must be emitted/referenced
domain: <domain>
subdomain: <vendor-family>
focus: onboarding
docket_of: _template
governing_adrs:
  - DEC-8570d4   # D526 — Source-System Docket structure (+ Amendment 1)
---

# <System Name> — Onboarding Log

> **Projection, not authority (D526 Amendment 1).** Narrative/chronology may be hand-authored, but **outcome
> and proof fields must be emitted or referenced** — each run links a governed onboarding-session receipt
> (exact source scope, contract/catalog package, timestamps, actor/service identity, checks, outcome, evidence
> digests). An author-entered "success" does not prove execution.

Chronological record of onboarding runs. Runbook definitions live in [index.md](index.md); this logs their
*execution* by reference to emitted receipts. Customer identity stays out of Git — pseudonymous instance UID only.

## Runbook (summary)
- **Customer-side:** <steps — see index.md for detail>
- **BareCount-side:** <connection profile + smoke test — see index.md>

## Execution log
| Date | Session | Instance (pseudonymous UID) | Path | Outcome | Receipt UID/digest |
|---|---|---|---|---|---|
| _none yet_ | | | | | |

<Per-run detail below, newest first. Outcome/proof by emitted receipt reference; deviations noted in prose.>
