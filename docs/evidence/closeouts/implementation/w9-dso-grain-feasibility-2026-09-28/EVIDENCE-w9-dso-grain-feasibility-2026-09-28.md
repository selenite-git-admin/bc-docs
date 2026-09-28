---
title: W9 DSO grain feasibility — existing invoice-grain MCs versus the journal-line balance on Kaveri (2026-09-28)
description: Read-only source evidence for the operator's 2026-09-28 ruling "journal lines + retire old", cited by ADR DEC-fa7c63 Amendment 1 (g).
status: closed
authority: implementation-checkpoint
date: 2026-09-28
project: bc-docs-v3
domain: metrics
subdomain: metrics/receivables
focus: dso-grain-feasibility
governing_adr: DEC-fa7c63
related_adrs: [DEC-83fda0, DEC-6fd09d, DEC-f44a71]
---

# W9 DSO grain feasibility (2026-09-28)

**Question** (the umbrella, on the operator's challenge "DSO has been authored for 6 months"): can the existing Customer-Invoice-grain DSO family be reused, with Kaveri's Odoo source onboarded by binding, and would it reproduce the lc5 coverage study's confirmed receivable balances?

**Method.**
- One pinned, read-only SQL run on Odoo v3_lc5, company 1 (Kaveri). SELECT only, inside `BEGIN … READ ONLY`.
- The runner starts the AWS box, runs the SQL through SSM in the database container and stops the box. There is no Odoo login and no web serve.
- The files are `u94-feas.sql`, `u94-feas-run.zsh` and `u94-feas-output.txt`, hashed in `MANIFEST.sha256`.
- The registry side (MC bindings, gates, chains) was read from `bc_platform_dev` under `BEGIN READ ONLY`.

**Result** (company currency, INR).

| As of | Receivable-line balance (D-1) | lc5 study, confirmed | Invoice grain, residual at P | Gap: non-invoice residual | `ar_balance` as declared |
|---|---:|---:|---:|---:|---:|
| 2024-03-31 | 1,173,945,368.13 | 1,173,945,368.13 | 1,173,495,368.13 | 450,000.00 | 974,792,869.57 |
| 2025-03-31 | 1,354,771,423.69 | 1,354,771,423.69 | 1,353,871,423.69 | 900,000.00 | 1,155,823,207.95 |
| 2025-09-30 | 1,645,980,292.08 | 1,645,980,292.08 | 1,644,630,292.08 | 1,350,000.00 | 1,397,247,472.49 |
| 2026-03-31 | 1,406,330,725.96 | 1,406,330,725.96 | 1,404,980,725.96 | 1,350,000.00 | 1,229,128,828.44 |
| 2026-08-31 | 1,997,244,184.68 | — | 1,995,894,184.68 | 1,350,000.00 | 1,528,031,175.32 |

- **The journal-line balance reproduces every lc5 value to the cent.**
- `ar_balance` as declared sums the open invoices' header gross amount in document currency, so USD invoices are added as INR numbers. It is 17–24% low.
- Invoice grain done right (company currency, residual from dated payment applications) still misses by the non-invoice receivable residual. Of the 2,898 non-invoice receivable lines, 2,637 are BNK1, 235 EXCH and 26 MISC.
- The face value of open invoices at 2026-08-31 is 2,023,548,678.12, 26.3M above the true balance, because of partially paid invoices.
- Billing FY2026-27 P03–P05: as declared (unsigned, document currency) 2,891,532,801.81, versus signed company currency 3,767,871,961.76.

**Ruling it supports:** ADR DEC-fa7c63 Amendment 1 (g). New journal-line-grained MCs; the invoice-grain DSO family is retired through the governed MCF path once they are live.
