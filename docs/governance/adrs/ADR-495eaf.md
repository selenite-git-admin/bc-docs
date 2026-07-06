---
uid: DEC-495eaf
title: "AWS Target Deployment Topology — Design Now, Deploy After E2E"
description: "Design AWS deployment topology now. Make local dev architecture-compatible. Do NOT build infra until Finance AR E2E works"
status: implemented
subdomain: aws-deployment
focus: deferred-deploy-contract
date: 2026-03-15
project: bc-admin
domain: database
authority: authoritative
migrated_from: legacy v2 archive
---


# AWS Target Deployment Topology — Design Now, Deploy After E2E

## Context

AWS deployment is not needed for the 4-week sprint but the architecture must be compatible. Designing the topology now prevents a rewrite later. Local Docker mimics the same two-connection pattern.

## Decision

Design the AWS deployment topology now. Document it. Make all local development architecture-compatible with the target. Do NOT build actual infrastructure (CDK, ECS, RDS) until after Finance AR E2E works.


## Options Considered

N/A

## Target Topology (ap-south-1, account 546549546538)

### Compute
- **bc-core API**: ECS Fargate (single service, two DB connections)
  - Platform DB connection (registry, masters, audit)
  - Tenant DB connection (boundary, evidence, tenant data)
  - Auto-scaling: 1-4 tasks based on CPU/memory
  - Health check: GET /api/health

### Database
- **Platform RDS**: PostgreSQL 16, db.t4g.medium
  - Schemas: public, platform, registry
  - Single instance, multi-AZ standby
  - Shared across all tenants
  - Backup: daily snapshots, 7-day retention
- **Tenant RDS**: PostgreSQL 16, db.t4g.medium (scales per tenant count)
  - Schemas: boundary, evidence, tenant (per-tenant via search_path)
  - SMB: schema-per-tenant in shared instance
  - Enterprise: dedicated RDS per tenant
  - Backup: daily snapshots, 30-day retention (tenant data is the product)

### Storage & CDN
- **bc-admin**: S3 + CloudFront (static SPA, admin.barecount.com)
- **bc-portal**: S3 + CloudFront (static SPA, app.barecount.com, tenant subdomains)
- **Artifacts**: S3 bucket (barecount-dev-artifacts) — already exists

### Auth
- **Cognito User Pool**: ap-south-1_pbyZXWjGs (already exists)
  - Portal client: 6094qlnfjal77as0p3uuae1u3g
  - Admin client: n992jbfti5sh0d1p1ub92gefo

### Cache
- **ElastiCache Redis**: For contract validation caching, session state (future)

### Networking
- **VPC**: Dedicated BareCount VPC
  - Public subnets: ALB, NAT Gateway
  - Private subnets: ECS tasks, RDS instances
  - No public DB access

## What to Do Now
1. Document this topology in bc-docs
2. Ensure local Docker setup mirrors the connection pattern (two DB connections)
3. Make all bc-core code use explicit platform vs tenant connections
4. Add DATABASE_URL_PLATFORM and DATABASE_URL_TENANT to .env.example

## What to Do After E2E Works
1. CDK stacks for VPC, RDS, ECS, S3/CloudFront
2. CI/CD pipeline (GitHub Actions → ECR → ECS)
3. Domain setup (barecount.com, admin/app subdomains)
4. Secrets Manager for DB credentials, Cognito secrets
5. CloudWatch monitoring + alarms

## Consequences

N/A
