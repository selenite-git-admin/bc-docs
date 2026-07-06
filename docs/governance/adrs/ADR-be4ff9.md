---
uid: DEC-be4ff9
title: "Serverless deployment: Lambda + Fargate split"
description: "Superseded deployment model: API on Lambda, readers on Fargate. Later refined by infrastructure decisions."
status: superseded
date: 2026-02-23
project: bc-admin
domain: contracts
authority: retired
migrated_from: legacy v2 archive
---


# Serverless deployment: Lambda + Fargate split

## Context

Lambda gives cost-efficient auto-scaling for bursty portal traffic (scales to zero). Fargate handles long-running admission work requiring stable connections to external data sources where cold starts are unacceptable. NestJS code remains deployment-agnostic — split is at entrypoint level only.

## Decision

Portal-facing APIs (admin portal, customer portal) deploy behind API Gateway + Lambda. Outward-bound data source communication (UinBAT Readers, admission) runs on Fargate for persistent connections. Same NestJS codebase, different entrypoints. RDS Proxy needed for Lambda→DB connection pooling. PENDING — details TBD (cold start mitigation, data APIs for activations, cost model).

## Options Considered

N/A

## Consequences

N/A
