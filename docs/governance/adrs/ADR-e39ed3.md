---
uid: DEC-e39ed3
title: "AWS resource naming and tagging convention — scope/stage/region/domain, immutable tenant id, Aspect-enforced"
description: "A single, machine-enforceable naming and tagging convention for all BareCount AWS resources, so the infrastructure stays legible and maintainable as it grows beyond the first database stack. Names are bcp/bct scope, stage, region, a closed domain code, an optional immutable tenant id, and a closed role; the human tenant slug lives only in tags. Region sits in the base for multi-region readiness. A CDK Aspect enforces the format, the closed registries, the five required tags, and per-service length limits at synth time. Ratified after an adversarial review that surfaced global-namespace, length, and stateful-rename failure modes."
status: proposed
subdomain: infrastructure
focus: naming-convention
date: 2026-09-17
project: platform
domain: platform
refs:
  - type: decision
    uid: DEC-c40e7a
    label: "Cloud realization on RDS — the first stacks this convention governs (database, schema-apply)"
  - type: decision
    uid: DEC-1918d0
    label: "Deployment and database architecture — the Infrastructure chapter this convention supports"
  - type: decision
    uid: DEC-324d9e
    label: "Subscription tiers and hosting variants — the platform/tenant split the scope segment encodes"
---

# AWS resource naming and tagging convention — scope/stage/region/domain, immutable tenant id, Aspect-enforced

## Context

The cloud realization (DEC-c40e7a) began with a single database stack and its schema-apply runner. Even across those two stacks the resource names diverged into two schemes — a function-anchored one (`bc-dev-platform-db`, `bc-dev-platform-db-client`) and a series-anchored one (`bc-dev-0301-db-apply-*`) — alongside CDK auto-generated physical ids such as `bc-dev-0300-database-platformdbinstancebf109930-9ijhxwzu2cfe`. As the infrastructure grows to networking, tenant databases, compute, caching, APIs, and observability, an ad-hoc scheme becomes unmaintainable and unenforceable.

This decision fixes one convention for every AWS resource, chosen so that a name is self-describing (no lookup table of numeric codes), traceable to its owning stack, safe against the AWS constraints that only surface at deploy time, and enforceable by code rather than by review discipline. It was ratified after an adversarial review that stress-tested a first draft and surfaced concrete failure modes: global-namespace collisions for region-less names, per-service name-length overflows, and data-loss on any rename of a stateful resource whose name embeds a mutable business attribute.

## Decision

### 1. Format

```
{scope}-{stage}-{region}-{dom}[-{tenant}]-{role}
```

Lowercase, ASCII, hyphen-delimited. Physical names are always set explicitly; CDK auto-generated ids are not used.

- **`{scope}`** — `bcp` = BareCount Platform (and shared/cross-cutting infrastructure such as the VPC) · `bct` = BareCount Tenant.
- **`{stage}`** — `dev` · `stg` · `prod`.
- **`{region}`** — the region short code (`aps1` = ap-south-1, `use1`, `usw2`, `euw1`, `euc1`, `apse1`, `apse2`, `apne1`). It sits in the base so the convention is multi-region-ready and so global-namespace resources (IAM, S3, Cognito) do not collide across regions in one account.
- **`{dom}`** — a closed domain-code registry (§2).
- **`{tenant}`** — present only for `bct` resources: an **immutable tenant id** matching `^[a-z0-9]{1,12}$`. Never the human tenant slug (§4).
- **`{role}`** — a closed role registry naming the specific resource within its stack.

The **stack base** is `{scope}-{stage}-{region}-{dom}`; every resource in the stack is named `{base}[-{tenant}]-{role}`. Because the tenant id contains no hyphen and always precedes the role, a name parses unambiguously even when a role contains hyphens (`client-sg`).

### 2. Domain registry (closed)

`ntw` network · `aut` auth (Cognito) · `dbs` database (RDS) · `dbap` db-apply (schema-apply runner) · `sto` storage (S3) · `cmp` compute (ECS/Lambda) · `cch` cache (Redis/ElastiCache) · `api` API · `msg` queues (SQS/SNS) · `evt` events (EventBridge) · `dns` Route 53 · `cdn` CloudFront · `sct` application secrets · `reg` container registry (ECR) · `waf` WAF · `cer` ACM certificates · `obs` observability.

Adding a domain is a registry amendment; there is no catch-all. Security groups and KMS keys are roles within their owning stack (`-sg`, `-key`), not a separate domain.

### 3. Role registry (closed, per domain)

Roles are drawn from a closed, versioned allow-list, e.g. `pg`, `sg`, `client-sg`, `key`, `master`, `nat`, `igw`, `egress`, `role`, `exec-role`, `task-role`, `project`, `logs`, `bucket`, `fn`, `cluster`, `service`, `tg`. A new role is a registry amendment. This keeps `-sg` from drifting into `-security-group`, and so on.

### 4. Tenant identity — immutable id in names, slug in tags

Per-tenant resource names use an **immutable tenant id**, never the human slug. A slug is a mutable business attribute; embedding it in a stateful resource name (an RDS instance, an S3 bucket) means a rebrand or correction changes the physical name, which CloudFormation implements as a **replacement — i.e. data loss**. Slugs also permit characters (`_`, uppercase) that RDS identifiers forbid. The human slug is carried in a tag (`tenant-slug`) for discoverability; the id is what appears in names.

### 5. Tags (required on every taggable resource)

`project`, `track`, `env` (`non-prod` | `prod`), `unit`, and `Name` (equal to the physical name). Per-tenant resources additionally carry `tenant-slug`. The zero-orphan teardown sweep keys on `track`.

### 6. Global-namespace exceptions

Some namespaces are global across all AWS accounts, so region alone is insufficient:

- **S3 buckets** append the account id: `{base}-{role}-{account}` (≤ 63 chars, no uppercase or underscore).
- **Cognito hosted-UI domain prefixes** append the account id, or use a custom domain.

### 7. Enforcement — a CDK Aspect at synth time (fail-closed)

A guardrail Aspect (in the shared guardrails package) enforces, and fails synth on violation:

1. Every physical name begins with its stack base; **unresolved CDK tokens fail closed** (concrete names are required, per the no-auto-id rule).
2. The `{region}` segment equals the short code of the stack's deploy region.
3. `{dom}` and `{role}` are members of their registries; `{tenant}` matches `^[a-z0-9]{1,12}$`.
4. The name fits the target service's length limit (RDS identifier ≤ 63, IAM role ≤ 64, S3 ≤ 63, ELB/target-group ≤ 32, KMS alias ≤ 256, …).
5. All required tags are present.

The Aspect maps each resource type to its physical-name property (`bucketName`, `roleName`, `functionName`, …).

### 8. Standing rules from the adversarial review

- **Development secrets** are created with force-delete (no recovery window), so a dev rebuild can reuse the deterministic secret name immediately.
- **Tenant-facing load balancers / target groups** (32-char cap) do not put the tenant id in the resource name; they use one shared load balancer with host/path routing (tenant in the rule) or a hashed token.
- **Tenant fleet at scale** uses one stack per tenant, budgeted against the CloudFormation per-stack resource, per-account stack, and per-region export limits (a tenant-lifecycle design constraint, recorded where that lifecycle is owned).
- **Teardown order**: a stack that injects resources into another stack's VPC must be destroyed before the VPC owner; construct-created log groups are set to destroy-on-removal so they do not orphan.

## Worked example (region ap-south-1 = `aps1`)

- Database stack `bcp-dev-aps1-dbs` → `bcp-dev-aps1-dbs-pg`, `bcp-dev-aps1-dbs-sg`, `bcp-dev-aps1-dbs-client-sg`, `alias/bcp-dev-aps1-dbs-key`, `bcp-dev-aps1-dbs-master`.
- Schema-apply stack `bcp-dev-aps1-dbap` → `bcp-dev-aps1-dbap-project`, `bcp-dev-aps1-dbap-nat`, `bcp-dev-aps1-dbap-egress`, `bcp-dev-aps1-dbap-role`.
- Future tenant database → `bct-dev-aps1-dbs-{tenantid}-pg`, `bct-dev-aps1-dbs-{tenantid}-sg`, with `tenant-slug` in tags.

## Consequences

- Every resource name is self-describing and traceable to its stack; the convention is enforced by code, so drift fails the build rather than passing review.
- Existing cloud-realization stacks are renamed to the convention; because renaming stateful resources is a replacement, this is done while the environment is torn down (the cloud-realization track already tears down to zero standing cost between drills), not against live data.
- The convention is the input to the shared guardrails package's naming Aspect; the registries live with that package and are versioned.

## Not decided here

- The multi-account boundary (whether `dev`/`stg`/`prod` are separate accounts) — the convention is correct under either, and the region segment plus the account-suffixed global-namespace exceptions keep names unique in both.
- The tenant-fleet stack topology and quotas (owned by the tenant-lifecycle decision).
- The guardrails package's internal structure and release process (its own decision).
