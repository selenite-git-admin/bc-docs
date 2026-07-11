---
uid: DEC-31dc55
title: "GL sign-convention and currency-declaration doctrine — ledger-signed canonical, metric-layer presentation, mandatory declarations"
description: "GL sign-convention and currency-declaration doctrine — ledger-signed canonical, metric-layer presentation, mandatory declarations"
status: decided
date: 2026-07-11T10:09:43.149Z
project: bc-core
domain: data-platform
subdomain: metric-semantics
focus: governance
---

# GL sign-convention and currency-declaration doctrine — ledger-signed canonical, metric-layer presentation, mandatory declarations

## Context

No rationale recorded.

## Decision

Response to the external audit's Class C finding (metric-correctness-audit-v1, current_ratio contextual 2/5): GL-derived metrics carried no sign policy and declared aggregation_currency_code=document_currency over SAP local-currency (HSL*) fields. DOCTRINE: (1) The CANONICAL layer stays LEDGER-SIGNED — GLT0/FAGLFLEX* HSL values are signed source reality (debit positive, credit negative per SAP convention); cc__gl_account's closing_balance/net_movement remain sign-neutral pass-throughs of that reality (source fidelity; consistent with the TSK-54a7f4 precedent: canonical sign-neutral, sign semantics composed at the metric layer). Normalizing signs at the canonical layer would destroy ledger truth and is REFUSED. (2) PRESENTATION normalization is declared at the METRIC layer via explicit formula arithmetic: credit-normal balance metrics (liabilities, equity — and any revenue-side GL aggregates) negate explicitly in the formula AST (multiply by -1 literal, the same mechanism as the existing ×100 rate metrics), so the declared formula IS the sign convention — transparent, auditable, no hidden transforms. (3) Every GL-derived MC MUST declare: (a) its sign convention in description_text and formula (presentation-positive vs ledger-signed), and (b) the CORRECT aggregation_currency_code — local_currency for HSL-derived values (already in the allowed vocabulary; document_currency on HSL metrics is a defect). (4) AFFECTED-SET REMEDIATION is a governed retire/re-mint CASCADE, bases before compositions (metric_input bindings pin MC uid + version, so base re-mints orphan dependent compositions until they are re-minted too): credit-normal bases (current_liabilities, total_liabilities, total_equity) get negation + currency fixes; debit-normal bases (current_assets, total_assets) and all other GLT0-derived metrics get the currency-declaration fix; dependent compositions (current_ratio, working_capital, net_working_capital_ratio, equity_ratio, financial_leverage_ratio, solvency/returns ratios binding these bases) re-mint after their bases. (5) The cash-flow movement family (change_in_*, investing/financing/net movements, OCF/FCF compositions) requires a SEPARATE sign-correctness study before re-mint: the run-8 accounting-equation composition (+liability/equity movement − asset movement) was authored contract-first with zero admitted GL data and may assume unsigned movements; under ledger signs the faithful identity is ΔCash = −Σ(non-cash ledger movements) uniformly — the study must derive the correct composition from the ledger-signed identity and re-mint accordingly. Never calibrate the answer against simulator output (SDG is not the source). Mitigating fact recorded: no affected metric was ever runtime-evaluated (zero GLT0 admissions in any tenant); all defects are contract-level, caught pre-runtime by the external audit.
