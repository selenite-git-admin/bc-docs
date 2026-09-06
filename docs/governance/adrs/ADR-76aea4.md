---
uid: DEC-76aea4
title: "Supplement to the legacy-doctrine supersession register (DEC-b390ef) — 3 bc-sdg/SAP ADRs missed by the 2026-08-23 sweep"
description: "Supplement register catching 3 bc-sdg / synthetic-SAP ADRs that DEC-b390ef missed on 2026-08-23; supersedes them under the same doctrinal basis (SAP retired D564; bc-sdg archived 2026-09-06)./"
status: decided
date: 2026-09-06T15:17:27.503Z
project: bc-docs
domain: governance
subdomain: adr-lifecycle
focus: supersession
supersedes:
  - DEC-b0839a
  - DEC-594211
  - DEC-2589d0
---

# Supplement to the legacy-doctrine supersession register (DEC-b390ef) — 3 bc-sdg/SAP ADRs missed by the 2026-08-23 sweep

## Context

The 2026-08-23 legacy-doctrine register (DEC-b390ef) superseded 33 retired-design ADRs but a 2026-09-06 re-scan (SES-3b0f66), run at operator request while closing the bc-sdg archival arc, found 3 bc-sdg/synthetic-SAP ADRs it missed — leaving them decided/implemented while describing designs whose substrate no longer exists (bc-sdg archived; SAP catalog expunged D564). Per the supersession-pair authority rule, a superseded ADR must be named by a successor's own text; DEC-b390ef designates a register entry as the mechanism. This supplement supplies that authority for the 3 misses and flips them in the same commit, keeping the ADR estate hygiene-clean without retroactively editing the dated 2026-08-23 decision.

## Decision

The three ADRs below are **superseded**, effective this decision's date. Each receives `status: superseded` and `superseded_by: DEC-<this uid>`; this ADR carries them in `supersedes:`. This is a **supplement to DEC-b390ef** (the 2026-08-23 legacy-doctrine supersession register): a 2026-09-06 re-scan of all 569 ADRs (session SES-3b0f66, at operator request during the bc-sdg archival) found three bc-sdg / synthetic-SAP-era ADRs that the original sweep missed. They belong to DEC-b390ef's "SAP as a live source" / "bc-sdg" families and are retired on the same doctrinal basis; DEC-b390ef itself states that where a retirement ADR does not name what it supersedes, "a register entry is required (this ADR is the template)." This is that entry.

| Superseded ADR | What it locked | Why retired |
|---|---|---|
| **DEC-b0839a** [was decided] "SDG Coherent Snapshots and Multi-Projection Architecture" | The bc-sdg SDG-SAP snapshot generator + Apex demo path (`source_system='s4hana'`, `SapOdataV4Executor` via bc-sdg's OData server). Extends the superseded DEC-076521 (prose-only, no frontmatter pair). | bc-sdg archived 2026-09-06; SAP-as-live-source retired (DEC-b390ef); Apex historical demo tenant retired. |
| **DEC-594211** [was implemented] "Source System Simulators — Per-System-Type Synthetic Data Architecture" | Decompose bc-sdg into per-system simulators (sdg-sap-ecc, sdg-salesforce). | Premise (bc-sdg) archived 2026-09-06; the synthetic-simulator architecture is retired. |
| **DEC-2589d0** [was implemented] "Port 4200 for bc-sdg OData server" | Reserves dev port 4200 for the bc-sdg OData server. | bc-sdg archived; server gone; ports 4200/6100 freed. |

Doctrinal basis (cited, not re-decided): **DEC-ea9bdc** (SAP catalogs + chain declared contamination), **DEC-296505** (D564 expunge), **DEC-8b17b1** (D561 demo estates, Odoo base), and the **2026-09-06 bc-sdg archival** (bc-core PR #723 / TSK-fc8606 removed the sdg_odata executor; TSK-efb8f5 deleted the DB residue; repo archived to _archived-repos/bc-sdg-archived-2026-09-06).

Supersession means the design is **no longer authoritative**; the three ADRs remain as history and are not edited beyond their two frontmatter lines. This supplement does **not** modify DEC-b390ef or re-decide its basis. The real-SAP transport executors themselves stay dormant-not-retired per DEC-0a614d (D594) — that is a separate, still-live decision and is NOT superseded here.

Consequences: the `docs:audit:adrs` pair rule is satisfied for all three. Future DEC-b390ef-family misses, if any, follow this same supplement pattern.

Operator decision record: ruled by anant on 2026-09-06 ("approved. Do it.") delegating to Claude (co-owner / Principal Architect); text recorded on that ruling.
