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

Lowercase, ASCII, hyphen-delimited. **Nameable** resources (§7 class A) always get an explicit physical name — CDK auto-generated ids are not used; non-nameable resources are identified per §7 rather than by a physical name.

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

Roles are drawn from a **closed, versioned, machine-readable registry** — the implementation contract the Aspect loads, not prose examples. The registry is `reference/schemas/aws-naming-registry.v1.json` (versioned by filename; amendments bump the version). It defines a `_common` role set (`role`, `exec-role`, `task-role`, `logs`, `key`, `sg`, `client-sg`) plus per-domain roles (e.g. `dbs`: `pg`, `master`, `subnet-group`, `param-group`; `dbap`/`ntw`: `project`, `nat`, `igw`, `egress`, `public`, `nat-eip`, `public-rt`, `egress-rt`, `flow-log`). Adding a role is a registry-version amendment; there is no free-form role. This keeps `-sg` from drifting into `-security-group`.

### 4. Tenant identity — immutable id in names, slug in tags

Per-tenant resource names use an **immutable tenant id**, never the human slug. A slug is a mutable business attribute; embedding it in a stateful resource name (an RDS instance, an S3 bucket) means a rebrand or correction changes the physical name, which CloudFormation implements as a **replacement — i.e. data loss**. Slugs also permit characters (`_`, uppercase) that RDS identifiers forbid. The human slug is carried in a tag (`tenant-slug`) for discoverability; the id is what appears in names.

### 5. Tags (required on every taggable resource)

`project`, `track`, `env` (`non-prod` | `prod`), `unit`, and `Name` (equal to the physical name). Per-tenant resources additionally carry `tenant-slug`. The zero-orphan teardown sweep keys on `track`.

### 6. Global-namespace exceptions

Some namespaces are global across all AWS accounts, so region alone is insufficient:

- **S3 buckets** append the account id: `{base}-{role}-{account}` (≤ 63 chars, no uppercase or underscore).
- **Cognito hosted-UI domain prefixes** append the account id, or use a custom domain.

### 7. Resource classes — three, mutually exclusive

Not every AWS resource has a settable physical name, and not every non-nameable one is taggable, so a single "every physical name follows the format" rule is impossible. The registry (§3 file) partitions **every governed resource type into exactly one of three classes**, and the Aspect fails synth on any encountered type that is in none (forcing a registry amendment — the classification is complete by construction):

- **Class A — nameable** (`classA_nameable`): a configurable physical-name property that MUST equal the convention name; carries the required tags. The registry maps each type to its property: `AWS::RDS::DBInstance`→`DBInstanceIdentifier`, `AWS::EC2::SecurityGroup`→`GroupName`, `AWS::IAM::Role`→`RoleName`, `AWS::S3::Bucket`→`BucketName`, `AWS::KMS::Alias`→`AliasName`, `AWS::Cognito::UserPoolDomain`→`Domain`, `AWS::Logs::LogGroup`→`LogGroupName`, … .
- **Class B — non-nameable but taggable** (`classB_nonNameableTaggable`): CloudFormation names it and it has no *usefully settable* name property, but it IS taggable, so it is identified by its **`Name` tag** (= convention name) plus the required tags: `AWS::KMS::Key`, `AWS::EC2::VPC`/`Subnet`/`RouteTable`/`InternetGateway`/`NatGateway`/`EIP`/`FlowLog`, `AWS::RDS::DBParameterGroup`. A **KMS key** is the canonical case — no key name, so identified by its companion alias `alias/{base}-key` (class A) plus a `Name` tag `{base}-key`. (`DBParameterGroup` is class B because the CDK L2 creates its L1 lazily on bind, so its physical name isn't reliably settable; the `Name` tag is.)
- **Class C — non-nameable/non-taggable or contract-named** (`classC_nonNameableNonTaggable`): structural glue with neither a name property nor tag support, plus resources named by a separate contract — so neither the name check nor the tag check applies: `AWS::EC2::Route`, `AWS::EC2::VPCGatewayAttachment`, `AWS::EC2::SubnetRouteTableAssociation`, `AWS::IAM::Policy` (inline), `AWS::EC2::SecurityGroupIngress`, `AWS::SecretsManager::SecretTargetAttachment`, `AWS::SSM::Parameter` (governed by the SSM path contract `/bc/{stage}/{domain}`, not this convention), `AWS::CDK::Metadata` (tool-injected). Identity is the CDK construct path / CFN logical id within its (already-conformant) stack; the Aspect asserts neither a physical name nor tags for these. (This class list was completed during first rollout as real stacks were synthesized; additive only.)

### 8. Enforcement — a CDK Aspect at synth time (fail-closed)

A guardrail Aspect (in the shared guardrails package) loads the §3 registry and enforces, failing synth on violation:

1. **Class dispatch by resource type.** Class A: the mapped physical-name property equals the convention name. Class B: the `Name` tag equals the convention name. Class C: no name/tag assertion (identity is the logical id). **Any type in none of the three classes fails synth closed** (must be added to the registry). **Unresolved CDK tokens also fail closed** (concrete names required, per the no-auto-id rule).
2. The `{region}` segment equals the short code of the stack's deploy region.
3. `{dom}` and `{role}` are members of the registry; `{tenant}` matches `^[a-z0-9]{1,12}$`.
4. The name fits the target service's length limit (from the registry's `lengthLimits`: RDS identifier ≤ 63, IAM role ≤ 64, S3 ≤ 63, ELB/target-group ≤ 32, KMS alias ≤ 256, Cognito domain ≤ 63, …).
5. Class A and B resources carry all required tags; class C is exempt (not taggable). Global-namespace class-A types (registry `globalNamespaceExceptions`: S3 bucket, Cognito `UserPoolDomain`) additionally append the account suffix.

The type→name-property map, the non-nameable set, the length limits, and the exception map all live in the versioned registry file, so the Aspect is data-driven, not hardcoded.

### 9. Standing rules from the adversarial review

- **Development secrets** are created with force-delete (no recovery window), so a dev rebuild can reuse the deterministic secret name immediately.
- **Tenant-facing load balancers / target groups** (32-char cap) do not put the tenant id in the resource name; they use one shared load balancer with host/path routing (tenant in the rule) or a hashed token.
- **Tenant fleet at scale** uses one stack per tenant, budgeted against the CloudFormation per-stack resource, per-account stack, and per-region export limits (a tenant-lifecycle design constraint, recorded where that lifecycle is owned).
- **Teardown order**: a stack that injects resources into another stack's VPC must be destroyed before the VPC owner; construct-created log groups are set to destroy-on-removal so they do not orphan.

## Worked example (region ap-south-1 = `aps1`)

- Database stack `bcp-dev-aps1-dbs` → RDS instance `bcp-dev-aps1-dbs-pg`, SGs `bcp-dev-aps1-dbs-sg` / `bcp-dev-aps1-dbs-client-sg`, secret `bcp-dev-aps1-dbs-master`. The **KMS alias** (nameable) is `alias/bcp-dev-aps1-dbs-key`; the **KMS key** (non-nameable) carries `Name = bcp-dev-aps1-dbs-key` and is identified by that alias — the Aspect checks the alias name and the key's Name tag, not a key name.
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
