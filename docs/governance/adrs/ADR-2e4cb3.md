---
uid: DEC-2e4cb3
title: "BO/BF is organizational grouping, not computational node in contract chain"
description: "Clarifies that BO/BF is organizational metadata, not a computational node. MC binds to CC outputs directly. Proven by DSO chain (first complete SC→AC→OC→CC→MC)."
status: implemented
date: 2026-04-09T10:13:22.682Z
project: bc-core
domain: contracts
migrated_from: legacy v2 archive
---

# BO/BF is organizational grouping, not computational node in contract chain

## Context

10 months of attempts to map SF→BF→Metric failed because BO/BF was treated as a computational middleman. The metric doesn't think in "business object fields" — it thinks in canonical fields which are often transformations of source fields, not 1:1 copies. The 45 BOs from D225 were "illusionary" because they were built as containers before knowing what goes in them. DSO proof-of-one succeeded by binding MC directly to CC field outputs (receivable_hdr_amount, invoice_hdr_total_amount) without requiring a BO mapping layer. The BO emerged as a natural grouping AFTER the canonical fields existed.

## Decision

MC (Metric Contract) inputs are canonical fields (CC outputs) or upstream metric snapshots. BO/BF is a grouping label for organizing fields by business domain — it is NOT a computational node in the contract chain. The contract chain is SC→AC→OC→CC→MC, where CC defines how SOs become COs (canonical fields), and MC consumes CC field outputs directly via co_bindings. The BO serves as an organizational container for BFs used by the CC onboarding flow (auto-deriving field_selection from BO composition), but is not required in the MC→CC binding path.
