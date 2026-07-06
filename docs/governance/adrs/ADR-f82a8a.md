---
uid: DEC-f82a8a
title: "Dynamic schema-per-tenant provisioning on tenant creation"
description: "POST /tenants auto-provisions tenant PostgreSQL schema (CREATE SCHEMA tenant_{slug}) and runs tenant-scoped migrations. No manual pre-creation needed."
status: superseded
superseded_by: DEC-1cdc5e
subdomain: tenant-provisioning
focus: provisioning-mechanism
date: 2026-03-17
project: bc-core
domain: database
refs:
  - type: decision
    label: "D073"
authority: authoritative
migrated_from: legacy v2 archive
---


# Dynamic schema-per-tenant provisioning on tenant creation

## Context

Schema-per-tenant is already working (D073). Automating schema creation closes the provisioning gap without the operational burden of database-per-tenant (N databases to manage/backup/migrate). Strong SQL isolation via search_path. Scales to hundreds of tenants on single RDS. Option B (separate DBs) reserved as future premium tier if compliance demands it.

## Decision

When a tenant is created via POST /tenants, bc-core automatically provisions the tenant's PostgreSQL schema (CREATE SCHEMA tenant_{slug}) and runs tenant-scoped migrations to create all required tables. Tenant status transitions: provisioning → active (success) or provisioning → failed (error). No manual schema pre-creation required. This extends the existing schema-per-tenant architecture (D073) with automated lifecycle management.

## Options Considered

N/A

## Consequences

N/A
