---
uid: DEC-c3fef3
title: "Runner dual-write — operational logs to platform, business data to tenant"
description: "UinBAT Reader writes operational telemetry to platform DB and business data (SOs, COs, evidence) to the tenant's database at execution time."
status: superseded
date: 2026-03-03
project: bc-core
domain: database
authority: retired
migrated_from: legacy v2 archive
---


# Runner dual-write — operational logs to platform, business data to tenant

## Context

Superseded by D087/D089 implementation. Dual-write mechanism now uses operations schema (not registry.admission_run). Tenant writes use t_{slug} schemas.

## Decision

UinBAT Reader performs dual-write at execution time: operational telemetry (admission run status, duration, record counts, errors) writes to the platform DB (registry.admission_run). Business data (observed records, source objects, admitted records, evaluations, canonical objects, metric snapshots, action objects, evidence, lineage) writes to the tenant's database. Tenant is resolved at runtime via tenant binding on the admission contract. Tenants can see operational data from the platform DB that pertains to them (their admission runs, reader health).

## Options Considered

N/A

## Consequences

N/A
