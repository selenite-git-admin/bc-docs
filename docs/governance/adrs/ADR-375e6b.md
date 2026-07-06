---
uid: DEC-375e6b
title: "KPIDepot Enrichment — Classification & Formula Decomposition Rules"
description: "Classification rules for KPIDepot metric enrichment — direction, type, formula decomposition, category mapping, unit types, and knowledge quality standards"
status: implemented
subdomain: metric-architecture
focus: kpi-classification-rules
date: 2026-03-28
project: bc-core
domain: metrics
authority: authoritative
migrated_from: legacy v2 archive
---


# KPIDepot Enrichment — Classification & Formula Decomposition Rules

## Context

Established during AP segment batch 1 (KPIs 6-15) quality review. Codified to ensure consistency across all 396 Finance KPIs in 9 segments. Prevents classification drift between sessions and provides a reviewable ruleset for the user.

## Decision

Standard classification and formula decomposition rules for KPIDepot metric enrichment across all 9 Finance segments (396 KPIs).

**direction_code rules:**
- Metrics where both extremes are bad (e.g. payment timing, volume indicators) → `target_is_optimal`
- Pure cost/error/risk metrics → `lower_is_better`
- Pure quality/compliance/savings metrics → `higher_is_better`

**type_code rules:**
- (A / B) or (A / B) * 100 → `ratio`
- Count or sum of X → `measure`
- A - B (delta/savings) → `variance`
- Score-based composites → `measure`

**Formula decomposition for non-standard KPIs:**
- "No standard formula" KPIs → express as the most meaningful quantifiable ratio/measure. Document the interpretation in verification maker_b_output.
- "Total cost of X" → decompose into component inputs (e.g. license + implementation + maintenance) for better variable binding granularity.
- "Score based on criteria" → use `O1 = I1` with a score unit_type_code and note the scoring methodology in knowledge.
- "Distribution" metrics → express as the primary percentage of interest.

**category_code mapping from BSC perspective:**
- Financial → cost, profitability, efficiency, or growth (context-dependent)
- Internal Process → efficiency, quality, or productivity
- Customer → satisfaction or quality
- Learning & Growth → cost or quality (for technology investments)

**unit_type_code rules:**
- Never concrete units (USD, hours, invoices) — always abstract 8 codes
- Time durations → `days`
- Monetary amounts → `currency`
- Ratios expressed as percentage → `percentage`
- Ratios not expressed as percentage → `ratio`
- Simple counts → `count`
- Composite scores → `score`

**Knowledge quality standards:**
- threshold_notes must include specific benchmarks with ranges (Excellent/Good/Needs improvement or Top quartile/Median/Bottom quartile)
- stakeholders must include 3 relevant roles with specific interests
- drivers must include 2-3 drivers with direction and description
- definition_context must explain when/why the metric matters and measurement frequency

## Options Considered

N/A

## Consequences

N/A
