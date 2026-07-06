---
uid: DEC-76a91b
title: "Cloud-agnostic architecture — no cloud vendor lock-in"
description: "No direct cloud SDK dependencies. Standard PostgreSQL + HTTP REST + static SPA. Future storage/messaging via provider-abstraction interfaces."
status: decided
subdomain: portability
focus: cloud-vendor-neutrality
date: 2026-02-24
project: bc-portal
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# Cloud-agnostic architecture — no cloud vendor lock-in

## Context

Enterprise clients prefer hosting in their own environment — AWS, Azure, GCP, or on-premise. Cloud lock-in limits market reach and increases switching costs. Current stack (NestJS + Drizzle + PostgreSQL + React SPA) is fully portable. This must be preserved as the platform grows. Areas to watch: file storage (evidence exports, documents), async messaging (if orchestrator goes async), and secret management. Each should use an abstraction layer, not direct cloud SDK calls.

## Decision

All BareCount components (bc-core, bc-portal, DevHub) remain cloud-agnostic. No direct cloud SDK dependencies (AWS S3, SQS, Azure Blob, GCP Pub/Sub, etc.). Standard PostgreSQL for persistence, standard HTTP REST for APIs, static SPA for portal. Any future storage or messaging needs must go through provider-abstraction interfaces (e.g., StorageProvider, EventBus) so deployments work on AWS, Azure, GCP, or on-premise environments.

## Options Considered

N/A

## Consequences

N/A
