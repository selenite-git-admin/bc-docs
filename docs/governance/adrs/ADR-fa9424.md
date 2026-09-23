---
uid: DEC-fa9424
title: "Metric authoring is Directory-primary — Member-anchored M12 door in bc-admin; retire the seed-primary Register entry"
description: "The Directory Member becomes the sole UI authoring entry (member-anchored M12 panel door, no-black-box); the seed-primary Register page/nav retires, POST /mcf/intakes/from-seed 410-retires, intake-queue control plane re-homes; Catalog copy corrected (TSK-1a2a15)."
status: proposed
date: 2026-09-20T07:35:44.015Z
project: bc-core
domain: metrics
subdomain: metric-directory/authoring
focus: ui-control-plane
---

# Metric authoring is Directory-primary — Member-anchored M12 door in bc-admin; retire the seed-primary Register entry

## Context

Ratified doctrine (metric-directory.md §8, D422/D506) makes the Directory the worklist authority and seeds secondary, but bc-admin still teaches the inverted model: Register Metric is the promoted "Onboarding" entry while the Directory door is free-form (never sets directory_member_uid) and MemberDetailPage has no authoring action. The bc-core chain is already member-anchored end to end (intake → panel provenance → M12.5 keystone stamp; D523 typed realization ledger). Live substrate proves the seed path dead: 6 of 433 MCs ever came from seed_metrics vs 238 member-keystoned operator-direct; member-anchored authoring happens only via the MCP drive — a DEC-d894de three-leg gap (programmatic flow without UI control plane). Surfaced by operator in SES-9c706c when a Register-button merge into the Catalog was caught contradicting doctrine and reverted.

## Decision

bc-admin metric authoring becomes Directory-primary per metric-directory.md §8 and D506: (D1) the Member is the only UI worklist entry for authoring a new metric — free-form memberless candidate authoring retires with the seed door; (D2) the M12 door becomes member-anchored (route /catalog/metrics/directory/members/:memberUid/author; identity locked to the member; hints derived from group grain + knowledge; directory_member_uid threaded to intake), entered from MemberDetailPage and a Members-tab row action; (D3) the UI leg keeps the M11/M12 intake path — the D507 Phase-1.6 envelope generator remains the drive path's deterministic leg; (D4) realization stays a separate explicit governed act (PATCH members/:uid/realize onto the D523 typed ledger), offered pre-filled after a member-anchored materialize — never auto-emitted; (D5) the seed-primary Register entry retires: nav entries removed, /catalog/metrics/register redirects to the Directory, POST /mcf/intakes/from-seed 410-retires, the intake-queue control-plane tab re-homes to the Directory page, seed reservoir data retained as evidence; (D6) MetricCatalogPage's three stale seed-primary texts corrected; (D7) no-black-box visibility unchanged (BCF/MCF minimal pattern) plus visible member context; (D8) lands after the held ui-quality-pass branch, no schema changes, no new dependence on candidate_source_ref_json (provenance only).
