---
uid: DEC-affb24
title: "17 shared services as NestJS modules in bc-core"
description: "bc-core organizes 17 cross-cutting concerns as NestJS modules (auth, contracts, metrics, etc.). Module-per-domain pattern."
status: implemented
subdomain: bc-core-architecture
focus: service-organization
date: 2026-02-23
project: bc-core
domain: contracts
authority: authoritative
migrated_from: legacy v2 archive
---


# 17 shared services as NestJS modules in bc-core

## Context

Shared Services Developer Playbook in legacy documentation site defines 17 services with explicit API contracts, event schemas, and boundaries. Explicitly out of scope: ERP/CRM connectors, data models, business workflows, KPI/domain logic. Maps cleanly to NestJS module-per-service pattern. Platform-documentation adds higher-level 3-plane architecture (Core/Control/Data) for later phases.

## Decision

All 17 shared platform services (Auth, RBAC, Audit, Health, Secrets, Encryption, Notification, Messaging, Scheduler, Logging, Telemetry, Gateway, Discovery, Feature Flags, IDs, Tenancy, Config) live as NestJS modules inside bc-core/apps/api/src/. These are cross-cutting utility services with no business logic. Phase 1A covers Auth, RBAC, Tenancy, Health, Config. Remaining services in later phases. Canonical service catalog: legacy documentation site/docs/platform/shared_services/shared_services_developer_playbook.md

## Options Considered

N/A

## Consequences

N/A
