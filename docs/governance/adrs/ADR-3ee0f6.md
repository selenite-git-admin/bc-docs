---
uid: DEC-3ee0f6
title: "Per-tenant S3 archive bucket — provisioned at tenant onboarding"
description: "Each tenant gets its own S3 archive bucket (bc-archive-{slug}-{env}) with Object Lock, provisioned at tenant onboarding. Supersedes the single-bucket-with-prefix layout from DEC-14592e on bucket structure only; the WORM/Object-Lock principle and JSONL format from DEC-14592e remain in force."
status: decided
date: 2026-04-28T01:21:28.072Z
project: bc-core
domain: database
subdomain: s3-archive
focus: per-tenant-bucket
supersedes: DEC-14592e
---

# Per-tenant S3 archive bucket — provisioned at tenant onboarding

## Context

D369's three-layer architecture (progression metadata + fact projection + S3 raw archive) chose physical isolation at the DB layer (per-tenant database tbc_{slug}_dev, D162/D167). The WORM-vault layer should match. Per-tenant bucket gives hard physical isolation, clean tenant offboarding (bucket-delete = data gone), per-tenant retention/KMS pathway, trivial cost attribution. The standard "single bucket / tenant prefix" pattern wins at >1k tenants on bucket-count-ceiling grounds; at our scale (well under 100 tenants for the foreseeable future) the operational simplicity of physical isolation dominates. DEC-14592e's "s3://barecount-data/{tenant_id}/..." layout is the layout this decision replaces; everything else in DEC-14592e (Object Lock COMPLIANCE mode, 7yr retention, JSONL format, write-after-RDS sequencing) stays.

# Per-Tenant S3 Archive Bucket

## Decision

Each tenant has its own S3 archive bucket. The bucket is provisioned at tenant onboarding (Step 3/4 of the tenant onboarding SOP) alongside the tenant database, not pre-provisioned by infrastructure ahead of time.

### Naming

- Bucket: `bc-archive-{tenant_slug}-{env}` where `env ∈ {dev, prod}`
- Region: `ap-south-1` (matches the platform region)
- Slug sanitization: lowercase, no underscores; tenant-slug must already conform to AWS bucket naming (3-63 chars, lowercase, hyphens permitted, no underscores). The seed/onboarding script asserts this before attempting CreateBucket.

### Object Lock

- COMPLIANCE mode, 7-year default retention.
- Object Lock MUST be enabled at bucket creation — AWS does not allow adding Object Lock to an existing bucket. Onboarding script enables `ObjectLockEnabledForBucket=true` and writes the default retention rule via `PutObjectLockConfiguration` immediately after `CreateBucket`.
- Per-tenant retention overrides are a future amendment; today every tenant gets 7 years.

### Encryption

- SSE-KMS with a single shared `bc-archive` CMK to start.
- Per-tenant CMK is a future amendment for BYOK / regulated tenants. Default-shared keeps key-rotation operationally simple.

### Object key layout

Drop the leading `{tenantSlug}/` prefix from `S3ArchiverService.buildKey` since the bucket is now tenant-specific. New layout:

```
{contractFamily}/{contractName}/{versionCode}/{yyyy-mm-dd}/{runId}.jsonl
```

The JSONL line envelope (`tenantSlug`, `runId`, `progressionRowId`, `recordId`, `archivedAt`, `payload`) stays intact for self-describing archives.

### Provisioning sequence (tenant onboarding)

Per the SOP at `bc-docs-v3/docs/onboarding/tenant-onboarding.md`, Step 3 (tenant identity provisioning) and Step 4 (tenant DB schema creation) gain a sibling action: create the archive bucket. The seed script `bc-core/src/registry/seed/seed-tenant-dbs.ts` is the appropriate home for AWS Shared and AWS Separate variants. BYO-DB and BC-Agent variants negotiate bucket placement on the customer's AWS account through the Onboarding Record (DEC-a67518) — out of scope for this ADR.

### Sandbox1 audit gap

The sandbox1 tenant exists pre-decision. Archives missed between M4.2e shipdate (Apr 28 2026) and M2.2c live-on-sandbox1 are accepted as documented drift — no replay path. Recorded here as the audit-completeness drift for the M4.2e arc. Sandbox1's archive bucket is created as a one-shot follow-up; archives start fresh from that point.

### IAM model

- Tenant-onboarding role (the Lambda/EC2/etc. that runs the onboarding script): `s3:CreateBucket`, `s3:PutObjectLockConfiguration`, `s3:PutBucketEncryption`, `s3:PutBucketPolicy` scoped to `arn:aws:s3:::bc-archive-*`.
- bc-core writer role (production runtime): `s3:PutObject`, `s3:GetObject`, `s3:GetObjectLockConfiguration` scoped to the same prefix.
- bc-core does NOT have CreateBucket — onboarding-only.
- Tenant offboarding role: separate, sized to permit `s3:DeleteBucket` only after retention has elapsed (Object Lock COMPLIANCE prevents deletion of locked objects regardless).

## Supersession scope

This decision supersedes DEC-14592e's "S3 bucket structure" section only. The following remain in force:
- WORM enforcement via Object Lock COMPLIANCE mode
- JSONL line format with envelope metadata
- Synchronous write-after-RDS sequencing for primary boundaries
- 7-year default retention for financial data
- ap-south-1 region
- The cost-savings rationale and recovery use cases

## Consequences

- Tenant onboarding gains a new failure mode (bucket creation can fail). Mitigation: onboarding is already a multi-step procedure with a repair state; bucket creation slots in alongside DB creation under the same repair semantics.
- AWS account bucket-count ceiling is the long-term capacity question. Default is 100, raisable to ~1000 via support ticket. At one bucket per tenant, this caps the platform at ~1000 tenants on the current AWS account before architectural revision. Acceptable for current horizon.
- Tenant offboarding becomes operationally cleaner — no "delete prefix from shared bucket" cleanup, just delete the bucket once retention elapses.
- Per-tenant bucket policies become possible (e.g. region-pinning for compliance, replication targets per regulatory regime). Not required day one.
- Sandbox1 carries an audit-completeness gap from M4.2e shipdate to M2.2c shipdate. Accepted; recorded here.

## Implementation tracking

- Code: `bc-core/src/progression/s3-archiver.service.ts` refactored to resolve bucket per tenant.
- Wiring: 3 progression writers (`boundary/admission.service.ts`, `boundary/canonical-resolution.service.ts`, `boundary/metric.service.ts`).
- Onboarding: SOP step + seed script.
- Existing TSK-83b9ed re-scoped from "provision one bucket via bc-infra" to "wire bucket creation into onboarding script".
