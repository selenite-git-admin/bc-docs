---
uid: DEC-824ae2
title: "Data Sources UI — redesign from execution model, not pipeline thinking"
description: "Pause Data Sources UI. Current design used pipeline philosophy. Must redesign from BareCount execution model (boundaries, readers, SOs)."
status: implemented
subdomain: bc-admin-ia
focus: data-sources-redesign
date: 2026-03-03
project: platform
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# Data Sources UI — redesign from execution model, not pipeline thinking

## Context

The root cause of repeated confusion and rework in the Data Sources section is that the UI was imagined before the architecture. Terms like 'Connected Sources', 'Sync Health', tabs like 'Readers' on connection detail pages — all reflect ETL/pipeline thinking. BareCount's model is fundamentally different: readers observe business objects (not 'extract data'), admission is contract-bound validation (not 'import'), and the progression SO→CO→Metric→Action is fixed. The UI must reflect this model to be coherent.

## Decision

Pause all Data Sources UI implementation. The current section was designed with data pipeline philosophy (connections, sync health, contract alerts) before the architecture/patent was locked. The UI must be redesigned from the BareCount execution model: Admission Boundary, UinBAT Readers, Source Objects, Admission Contracts. A dedicated design session will define user personas, journeys, and information architecture before any further code changes.

## Options Considered

N/A

## Consequences

N/A
