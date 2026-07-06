---
title: Finance Package v0 — Gold Universe (Planning SSOT)
description: Provenance and usage rules for the re-homed 1241-row classified finance metric master ("gold snapshot") — the planning SSOT for Finance Package v0 candidate selection. Explicitly NOT runtime substrate; authoring still flows exclusively through mcf.seed_metric → intake → M12 panel. Locked by DEC-a7fe72 (D440).
status: active
date: 2026-06-11
project: bc-core
domain: metrics
subdomain: metric-portfolio
focus: planning
---

# Finance Package v0 — Gold Universe (Planning SSOT)

> **What this is.** The governed home of the 1241-row classified finance metric master ("gold snapshot"), re-homed per **DEC-a7fe72 (D440) Lock 1** after the live table was wiped. It is the **planning SSOT** for Finance Package v0 candidate selection and packaging. **It is NOT runtime substrate**: nothing reads it at evaluation, binding, or admission time, and no authoring path starts from it directly — authoring flows exclusively through `mcf.seed_metric` → intake → M12 panel → governed gates.

## Artifact

| Property | Value |
|---|---|
| Data file | [`docs/assets/data/finance-gold-metric-definition-1241-2026-06-09.tsv`](../../../assets/data/finance-gold-metric-definition-1241-2026-06-09.tsv) |
| Rows | 1241 (+1 header row) · 37 columns |
| Integrity | Data rows are byte-identical to the source COPY block. `sha256(data rows) = 183996bb91ee3cce3457adebee314b33d0500e059d4a3c832c39aeb007776324` |
| NULL convention | PostgreSQL COPY text format: `\N` = NULL; `\t`/`\n` inside text are backslash-escaped (one row per line) |

## Provenance

- **Origin:** `metric.metric_definition` (bc-core platform DB), as of the **2026-06-09 pre-reset golden snapshot**. The live table was emptied during the 2026-06-09/10 resets ("metric-zero"); at re-homing time it held **0 rows**, and the only surviving copy was the COPY block inside `bc-core/docker/redesign/golden-snapshot-pre-reset-2026-06-09.sql` (772,206,415 bytes). The June-10 `pre-metric-zero` dump and the other golden snapshots also contain 0 rows for this table.
- **Extraction (reproducible):**
  ```bash
  cd bc-core/docker/redesign
  awk '/^COPY metric\.metric_definition /{f=1;next} /^\\\.$/{f=0} f' \
    golden-snapshot-pre-reset-2026-06-09.sql > gold-metric-definition-1241.tsv
  ```
  The header row in the governed TSV was prepended from the COPY column list in the same dump; data rows were not modified.
- **Re-homed:** 2026-06-11, SES-20c056, per operator lock (DEC-a7fe72 Lock 1).

## What the data is (measured 2026-06-11)

- All 1241 rows: `function_code = 'finance'`, across **21 subfunctions** (largest: general_finance 204, accounts_payable 111, fpa 101, general_ledger 98, revenue_accounting 97; smallest: financial_reporting 6).
- **Status:** 1214 `draft` · 25 `deprecated` · 2 `active` (`ar_growth_rate`, `revenue_collection_rate` — historical labels only; nothing is live).
- **5D classification fully populated:** purpose (operational 354 / performance 342 / efficiency 324 / diagnostic 110 / predictive 83 / reference 28), shape (scalar 1215 / distribution 21 / time_series 4 / ratio_pair 1), temporality (`period` × 1241), precision, impact.
- **`formula_hint` is NULL on every row.** Formulas live only in the seed reservoir (`mcf.seed_metric`); planning joins gold ↔ seeds by exact `metric_name`.
- `seed_ref` populated; `temporality_kind` NULL throughout.

## Reconciliation vs the seed reservoir (no double-count)

| Measure | Count |
|---|---|
| Gold rows | 1241 (1216 non-deprecated) |
| Live seeds (all functions) | 12,501 |
| Gold ∩ seeds (exact name) | 894 |
| **`gold_only_unmatched`** | **347** — quarantined per DEC-a7fe72 Lock 4: catalogued, **never authored** until matched to seed/formula/source concepts or deliberately rewritten through the governed seed path. Sampled class: APQC-style org/FTE/IT-cost benchmark metrics + probable name drift. |
| Finance seeds not in gold | 388 — triage appendix, not counted in package totals |

## Usage rules (from DEC-a7fe72)

1. **Planning only.** Package structure, candidate counts, and readiness buckets derive from this artifact joined to seed formulas. It never feeds runtime.
2. **Execution-narrow.** Finance Package v0 execution scope = AR invoice/billing + AR collections flow (invoice-grain) + one revenue/net-revenue family + cash only if low-friction. AP excluded until vendor-side BCF entities exist (Lock 2/5).
3. **Grammar honesty.** The `average_days_to_collect` specimen (panel/preflight only) gates the date-diff family; failures shrink scope — no SDG calibration to fake expressibility (Lock 3).
4. **Not authoritative.** Source artifacts may be inaccurate or incomplete (operator caveat, survey §10); every count above is a measurement of the artifact, not ground truth.

## References

- ADR: [`DEC-a7fe72` (D440)](../../../governance/adrs/ADR-a7fe72.md) — Finance Package v0 scope lock + this re-homing
- Ground survey packet: `bc-core/scripts/audit-output/finance-package-v0-ground-survey-2026-06-11.md` (SES-20c056; verification appendix has copy-paste SQL/awk for every number)
- AR precedent matrix: `bc-core/scripts/audit-output/phase0-ar-portfolio-matrix-2026-06-11.md`
- Trust-chain + PE-MC-11 authority: [`DEC-1002c9` (D439)](../../../governance/adrs/ADR-1002c9.md)
