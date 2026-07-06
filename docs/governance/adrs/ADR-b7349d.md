---
uid: DEC-b7349d
title: "Reader execution: dev in-process, prod Fargate — no infra planning needed now"
description: "Readers run in-process during dev. Production uses Fargate tasks. No need to build execution infra until prod deployment."
status: decided
subdomain: reader-execution
focus: dev-inprocess-prod-fargate
date: 2026-02-28
project: bc-infra
domain: readers
authority: evolving
migrated_from: legacy v2 archive
---


# Reader execution: dev in-process, prod Fargate — no infra planning needed now

## Context

1. ReaderExecutor interface is already stateless and isolated — Fargate adoption is a wiring change, not an architecture change. 2. valuestream-data-infra proves the one-image/JOB_CODE pattern works. 3. Only new code for Fargate: runner.ts entry point (~50 lines), CDK stack, EventBridge sync. 4. No service/method changes required — executor, runtime, orchestrator, validation all unchanged. 5. User aligned to few containers reused for all jobs.

## Decision

Reader executors run inside the NestJS API process during development (triggered via POST /api/readers/:id/execute). Production deployment uses Fargate tasks following the valuestream-data-infra pattern: one Docker image, one ECS task definition, READER_ID as container override. The split point is above ReaderRuntimeService.executeReader() — everything below it stays identical. Infra work is deferred until dev is complete. The API endpoint remains available for on-demand/manual runs even after Fargate is in place.

## Options Considered

N/A

## Consequences

N/A
