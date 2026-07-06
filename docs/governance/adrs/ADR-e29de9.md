---
uid: DEC-e29de9
title: "BareCount is anti-pipeline: contract-first lifecycle system"
description: "BareCount is not a data pipeline. Meaning is resolved once at Evaluation Boundaries under immutable Contracts, preserved as COs, and never recomputed."
status: implemented
subdomain: platform-philosophy
focus: contract-first-identity
date: 2026-02-23
project: platform
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# BareCount is anti-pipeline: contract-first lifecycle system

## Context

Intra-site Foundation specification defines BareCount's structural commitments: no recomputation, no reinterpretation, no backfilling, no implicit joins, no shared authority across planes. The seven guarantees and six prohibitions are architectural constraints, not guidelines. Previous plan assumed HRMS domain and pipeline architecture — both are category errors per the Foundation.

## Decision

BareCount is NOT an HRMS, NOT a data pipeline platform, NOT an analytics tool. It is a contract-first system where meaning is resolved once at defined Evaluation Boundaries under immutable Contracts, preserved as Canonical Objects / Metric Facts, and only ever referenced — never recomputed. Architecture uses five isolated planes (Control, Evaluation, Execution, Evidence, Data) and a fixed lifecycle (Observed → Sourced → Admitted → Evaluated → Canonical → Finalized → Intervened → Evidenced → Accountable). Pipeline terminology (ingest, transform, materialize, downstream, stage, flow, job) is structurally forbidden. PLN-7c4d90's HRMS tables and pipeline phases are invalid and must be revised.

## Options Considered

N/A

## Consequences

N/A
