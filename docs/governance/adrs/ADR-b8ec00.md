---
uid: DEC-b8ec00
title: "BF-BO Catalog Expansion Factory"
description: "D409 — multi-agent BF-BO catalog expansion: agents recommend, only governed endpoints/DBCPs mutate state. Closed-set verdicts + role split + write boundaries."
status: decided
date: 2026-05-17T07:36:46.549Z
project: bc-docs
domain: contracts
subdomain: catalog
focus: governance
---

# BF-BO Catalog Expansion Factory

## Context

D408 (DEC-1ce490) made `contract.business_field` the certified BF-BO catalog and left six residual streams (45 A1 orphan CFs, 3 depreciation flow CFs, 1 REVIEW row, 1 INSUFFICIENT_CONTEXT row, 11 NEEDS_EVIDENCE rows, 1 ISO 20022 row) that cannot be cleared by mechanical re-runs. The residuals require *judgment* on standards-tier evidence — and the next waves (depreciation, tax, treasury, payroll, derivatives) will be the same shape at larger volume. Two failure modes must be prevented: (a) "mega onboarding" / coverage pressure that bulk-admits weakly-defined rows to clear queues, and (b) LLM auto-certification that fabricates evidence and silently re-decides BF/BO meaning. The disciplined response is a factory with a bounded review packet, a closed-set verdict, a bounded write surface (the four D408 endpoints + 1q-D/E/G DBCP patterns), and a three-role split (Explorer / Skeptic / Moderator) that ensures evidence is challenged before reaching the operator. Foundation invariants directly invoked: I (meaning evaluated once — agents may not re-decide meaning), IV (all references explicit — typed evidence with citations), VI (evidence emitted not inferred — standards-tier dominates internal-tier). The framework is filed at v0.1 SOP plus a reusable prompt scaffold; the verdict taxonomy and evidence types are explicitly evolving and will be re-versioned after the pilot lands.

## Thesis

BareCount may scale BF-BO catalog review with multiple agents, but **agents may only produce evidence packets and recommendations; state changes remain exclusively through governed endpoints/scripts.** The factory adds review capacity without re-introducing the failure mode D408 was created to remove.

## Why D409 exists after D408

D408 (DEC-1ce490) made `contract.business_field` the certified BF-BO catalog. Its closeout (SES-c5af8c, 2026-05-17) leaves six residual streams that cannot be cleared mechanically:

- 45 orphaned CFs from DBCP-1q-E (A1 MISMATCH `cc_field_mapping` removal).
- 3 P&L depreciation flow CFs requiring a new `asset_depreciation_expense_amount` BF.
- 1 REVIEW `cc_field_mapping` row (`change_in_value_of_underlying_asset`).
- 1 INSUFFICIENT_CONTEXT `cc_field_mapping` row (`total_asset_value`).
- 11 `NEEDS_EVIDENCE` definition rows pending operator IFRS / XBRL US-GAAP / OAGIS sourcing.
- 1 ISO 20022 row (`iso20022_camt_xchg_rate`) whose *shape* is the open question, not its admission.

These six streams plus the next waves (depreciation, tax, treasury, payroll, derivatives) require judgment on standards-tier evidence, not more cycles of the D408 endpoints. D409 is the workflow that supplies that judgment at scale.

## The problem with mega-onboarding / coverage pressure

Catalog coverage is an *output* of admitting only what is defensible, never an *input* that drives admission. The historical failure modes — silent placeholder-definition admission (the 462 rows D408 found), funnel padding (bulk re-pointing CFs to share one source column to unblock MCs), LLM auto-certification — all share one shape: **a coverage number is treated as the success metric, and the evidence boundary is bent to hit it.** D409 forbids row-count KPIs and replaces them with packet-throughput at a fixed evidence bar.

## Core rule

> **Agents may recommend; only governed endpoints/scripts may change state.**

This is non-negotiable. Every agent prompt repeats it. Every halt rule enforces it.

## The six verdicts (closed set)

| Verdict | Meaning |
|---|---|
| `ADMIT_READY` | Standards-tier evidence survives Skeptic review; no surviving objection |
| `NEEDS_EVIDENCE` | May be defensible but the packet's evidence is incomplete or all-internal |
| `DEMOTE_RECOMMENDED` | Cannot be defended under current standards; no upgrade path visible |
| `REBIND_RECOMMENDED` | Defensible but currently bound to the wrong target |
| `DUPLICATE_OR_MERGE` | Restates an already-certified BF/BO; merge or alias, do not admit parallel |
| `HOLD` | Halt rule fired, or packet exposed a structural gap larger than itself |

The set is closed. New verdicts require a versioned amendment of the SOP, not a per-packet exception.

## The three roles

- **Explorer** — gathers BO / BF / CF context and evidence, lists anchors / aliases / mappings / definitions / standards refs, proposes an initial verdict. Forbidden from inferring evidence or picking outside the closed verdict set.
- **Skeptic** — attacks every Explorer recommendation; looks for weak evidence, bad BO scope, duplicate concepts, mapping mismatch, unit/type conflict; downgrades verdicts (e.g. `ADMIT_READY` → `NEEDS_EVIDENCE`). Forbidden from inventing parallel evidence; if new evidence is needed, the verdict is `NEEDS_EVIDENCE` and the packet re-queues.
- **Moderator** — consolidates Explorer + Skeptic output, produces the operator-facing packet, logs dissent. Forbidden from replacing the operator or hiding Skeptic objections.

All three roles are forbidden from calling any write endpoint.

## Write boundaries

The only mutation surface D409 may recommend is an **operator** call against one of:

- `POST /api/business-fields/admit-from-correction-required`
- `POST /api/business-fields/remediate-semantics`
- `POST /api/business-fields/correct-definition`
- `POST /api/business-fields/correct-type`
- D408-substrate DBCP scripts for demotion (1q-D pattern), `cc_field_mapping` removal (1q-E pattern), and additive CHECK enum expansion (1q-G pattern).

If a residual requires a write shape these surfaces do not cover (e.g. BF rename, ISO 20022 short-named BO creation), D409 emits a **DBCP draft** for operator review — it does not invent a new write inside the agent loop.

## Foundation invariant mapping

Repair-location classification (CLAUDE.md §Foundation Invariant Check): **B — contract / governance grammar**. The artifact is a governance primitive consumed by D408's endpoint substrate.

- **Invariant I (Meaning is evaluated once)** — agents may *recommend* meaning but never *commit* it; admission is the single meaning boundary, and it remains operator-driven through governed endpoints.
- **Invariant IV (All references are explicit)** — every evidence item carries `{type, citation, location, scope}`; free-form claims are not evidence.
- **Invariant VI (Evidence is emitted, not inferred)** — standards-tier citations (US-GAAP SDA / IFRS / XBRL / OAGIS / ISO 20022) dominate internal-tier (BO membership / CC reference / SDA projection / alias); an internal-alias-only packet may not reach `ADMIT_READY`.

## Non-goals (explicit)

D409 is **not**:

- A bulk certification path. Throughput is measured in defensible packets, not row counts.
- A standards-directory bulk import. Standards are cited as evidence per packet, not crawled into the catalog en masse.
- An LLM auto-certification framework. No verdict reaches the operator without surviving Skeptic review; the operator remains the decision authority.
- A direct-SQL promotion path. No SQL-against-`contract.*` outside DBCP discipline.
- A row-count KPI program. Coverage metrics are forbidden as success criteria.

## Pilot order

1. **`cc__credit` orphaned CFs (11 rows from DBCP-1q-C)** — smaller, more uniform; runs first as the workflow-validation control.
2. **A1 asset mapping residuals (45 orphan CFs from 1q-E + 1 REVIEW + 1 INSUFFICIENT_CONTEXT + 3 depreciation flow CFs)** — largest and most complex; the depreciation cluster is a `bo-modeling` packet that admits a new BF before rebinding orphans.
3. **ISO 20022 modeling review (`iso20022_camt_xchg_rate`)** — precedent-setting; the central question is whether the row's *shape* is defensible at all, with expected verdict skew toward `DEMOTE_RECOMMENDED` + a sibling `bo-modeling` packet for a properly modeled `camt`-shaped BF/BO.

Pilots run **sequentially**, not in parallel — the `G-Snapshot-Stable` quality gate (SOP §8) requires that no two packets touch overlapping catalog state simultaneously.

## Relationship to D408 and TSK-eae922

- **DEC-1ce490 (D408)** is D409's parent decision. D409 does not re-open D408 or re-litigate any closed row.
- **TSK-eae922** (D408 type-corrections-require-SDA-uplift, marked completed in SES-c5af8c) supplied the SDA-uplift pattern that the Explorer cites when recommending `ADMIT_READY` for A1-class subjects.
- **TSK-926c77** (bc-ai cf_classifier panel — Gemini Maker + OpenAI Checker + Claude Moderator) is the planned automation of the Explorer/Skeptic/Moderator trio. D409 is the governance contract that panel must satisfy; the panel itself remains a separate task and may not deploy until at least the cc__credit pilot has run with human-driven prompts.

## Companion artifacts

- **SOP v0.1** — `bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-bf-bo-catalog-expansion-factory-sop.md` (commit 15805cc, SES-5e0796). The operational source of truth: packet schema, evidence types, quality gates, halt rules, ingestion table.
- **Agent prompt scaffold** — `bc-docs-v3/docs/onboarding/metric-work-records/_cross/2026-05-17-d409-agent-prompt-scaffold.md` (this session). The reusable Explorer/Skeptic/Moderator prompt set + packet JSONL schema + worked example.
- **Future ADR amendments** — the verdict taxonomy and evidence types in SOP §5 / §4.3 are explicitly evolving; any change is a versioned SOP amendment plus a referenced ADR update.

## Status

`decided`. Pilot has not run. The first operational test is the `cc__credit` orphan-CF stream (11 rows) in a subsequent session.
