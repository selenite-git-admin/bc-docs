---
uid: DEC-c40e7a
title: "Cloud realization of the DB foundation — RDS PostgreSQL 17 on the versioned spine (W1.6 + the W2/W4 cloud items)"
description: "With budget approved (2026-09-17), the cloud items previously deferred as budget-gated become active: realize the DB foundation on RDS PostgreSQL 17 in ap-south-1 through bc-infra (retiring the dormant Aurora construct), apply the schema by invoking the bc-db runner as a deployment stage so build==dump==live holds on the managed instance, source platform and tenant credentials from Secrets Manager (RDS-managed master password; no human credential handling), and prove the AWS-Shared service recovery drill plus the W4 durability objectives. Design brief with acceptance criteria and a unit sequence; non-production provisioning proceeds autonomously through reviewed units carrying a stated cost ceiling and teardown plan, and production stays Gate-④."
status: proposed
subdomain: spine
focus: cloud-realization
date: 2026-09-17
project: platform
domain: platform
refs:
  - type: decision
    uid: DEC-1918d0
    label: "RDS PostgreSQL decided (Aurora rejected) — this realizes it and retires the dormant Aurora construct"
  - type: decision
    uid: DEC-b1a286
    label: "Live DB is ground truth; the versioned spine is the change mechanism — extended to the cloud instance via a schema-apply deployment stage"
  - type: decision
    uid: DEC-0e4547
    label: "Operating model + the four operator-only gates — production cutover remains Gate-④"
---

# Cloud realization of the DB foundation — RDS PostgreSQL 17 on the versioned spine (W1.6 + the W2/W4 cloud items)

## Context

The DB-foundation program's autonomously-reachable engineering is complete: the schema spine, runner, recovery mechanism, tenant fleet lifecycle, onboarding substrate, and curated-content machinery are built and merged (W0–W3). The remaining exit items across the program were deferred as **budget-gated cloud work**, not open engineering:

- **W1.6** — cloud realization of the version contract and bc-infra realignment (§8.6).
- **W2 #4** — platform and tenant credentials in a secrets manager.
- **W2 #6** — the AWS-Shared service recovery drill.
- **W4** — full durability (PITR, D10 objectives), off-account escrow (NFR-6, D9), residency (D11), object-store lifecycle (FR-20), benchmark (NFR-9).

Budget is approved (operator, 2026-09-17), so these become active. This brief opens the **cloud-realization track** and defines its units and acceptance criteria.

**Current cloud state — scoped to a read-only inventory (account `546549546538`; regions queried: `ap-south-1` and `us-east-1`; services queried: RDS, Secrets Manager, CloudFormation, S3, Cognito):**
- **No RDS** instances or clusters in either region (verified `0/0`). The BareCount **database tier is greenfield.**
- **CloudFormation complete stacks in ap-south-1** are `afcs-mvp2-devhub-backup`, `bc-dev-0200-auth` (Cognito), and `CDKToolkit`. **No platform-infra stack is deployed** — a `PlatformInfraStack` template exists only as a `cdk.out` synth artifact, not a deployed stack.
- **Secrets Manager (ap-south-1) does contain secrets** — `DataJetty-dev-AdminMySQLDBSecret`, `odoo_enterprise_subscription_id`, `bc-demo/odoo-ent/admin` — but **none is a BareCount platform or tenant database secret.**
- S3 holds `barecount-dev-artifacts` (DB snapshots) and `barecount-evidence-worm-dev`.
- bc-infra is CDK (TypeScript) with a **dormant `cdk/lib/constructs/aurora-postgres.ts`** construct encoding the rejected Aurora option (DEC-1918d0). Data residency is India (ap-south-1).

Beyond this inventory boundary (other regions/services/accounts) nothing is asserted.

## Decision

Realize the DB foundation as a managed **RDS PostgreSQL 17** instance in `ap-south-1`, driven by the same versioned spine, with credentials and recovery handled by managed services. The realization is delivered as reviewed units; nothing in this brief provisions anything.

1. **Hosting — RDS PostgreSQL 17, not Aurora (DEC-1918d0).** A new bc-infra stack (`bc-dev-0NNN-database`) provisions a single-AZ RDS PostgreSQL instance pinned to the engine version the spine already pins (17.x, exact minor/parameter-group), in a private subnet with a scoped security group, a parameter group matching the spine's expectations, automated backups enabled, and deletion protection. The **dormant `aurora-postgres.ts` construct is retired** in the same unit.
2. **Credentials from Secrets Manager; no human handling (W2 #4).** The RDS **master password is AWS-managed** (generated and stored in Secrets Manager by RDS — no person, and not this agent, ever sees or types it). The platform owner/runtime roles and each tenant's owner/runtime credentials are stored as Secrets Manager secrets with rotation; consumers resolve them through the SSM/secrets contract, never plaintext or env-baked. This satisfies FR-9/FR-18/FR-19's credential custody in the cloud.
3. **Schema applied by the spine as a deployment stage (build==dump==live in the cloud).** A CD stage invokes the **bc-db runner** against the freshly provisioned instance under the governed owner identity — the same forward-only migrations, ledger, and from-zero equivalence that CI proves — so the managed instance is reproduced by the spine, not by a hand-loaded dump. The single environment definition (§8.5) is shared by app, infra, and tooling.
4. **AWS-Shared service recovery drill (W2 #6).** On a non-production cloud environment: provision → apply baseline via the runner → take a verified backup → restore into a fresh instance → parity-verify (the bc-db parity fingerprint) → run the bound monitor against the managed backups → record evidence. The bc-db `backup`/`monitor`/`retention`/`restore-drill` tooling runs against RDS (managed automated backups + PITR + the scheduler-independent monitor).
5. **W4 durability objectives — surfaced for decision.** PITR window, the D10 RPO/RTO numbers per DB category, the D9 off-account key-escrow arrangement, and D11 residency/object-store placement are operator/product decisions (see below); the drill and IaC encode whatever is decided.

**Two layers and the gates.** Layer A — design briefs, bc-infra IaC, the schema-apply stage, the drill harness, and rehearsals on disposable/local — is built and driven through auditor review like every prior unit. Layer B — creating real **non-production** AWS resources, provisioning secrets, and running the live drill — proceeds **autonomously through reviewed units**, under the operator's standing cloud-work authorization, gated by **three standing conditions, not a per-step operator confirmation**: (a) the unit is auditor-reviewed at its exact head; (b) it carries a **stated maximum expected monthly cost** for every real resource it creates; and (c) it carries a **teardown plan** (below). D9/D10/D11 remain open **product decisions**, required only when the unit that needs them is reached — they do not gate the earlier units. **Production is the one hard gate — Gate-④, operator-only**, regardless of budget; nothing in this track provisions or cuts over production. The agent uses the authorized `Claude.Assistant` profile (account `546549546538`, ap-south-1) for read/describe and for the reviewed provisioning steps; it does **not** handle plaintext credentials — RDS-managed master passwords remove the need, and any secret whose value would require human entry is the operator's.

## Budget and teardown (standing condition for every real-resource unit)

Every Layer-B unit states a cost ceiling and a teardown plan; the numbers below are the non-production dev profile (smallest workable, single-AZ). **Non-production monthly ceiling ≤ US$50.**

- **u4 — dev RDS instance:** `db.t4g.micro` (or smaller), single-AZ, ~20 GB gp3, automated backups within retention. **≤ ~US$25/mo.**
- **u5 — recovery-drill temporary restore instance:** same class, **short-lived (hours), torn down in the same run**, **≤ ~US$2 per drill**.
- **u6 — Secrets Manager secrets:** platform + per-tenant, at ~US$0.40/secret/mo. **≤ ~US$5/mo** at the current single-tenant scale.
- **u7 — durability:** PITR/backup storage bounded by the D10 retention decision; escrow/replication costs quantified when D9/D11 land. **Stated per its own unit.**

**Teardown plan (every real resource):** (1) all resources tagged `project=bc-db-foundation`, `track=cloud-realization`, `env=non-prod`, `unit=<u#>`; (2) a time/cost cap — a unit's resources are torn down when its purpose completes or the cap is hit; (3) retained-evidence policy — keep the drill evidence, parity fingerprints, and ledger records; delete the compute/storage; (4) deletion order — **disable deletion protection → delete the RDS instance (final snapshot only if evidence requires) → schedule-delete the secret → delete the security group → delete the parameter group → delete the subnet group**; (5) verification criterion — after teardown, a read-only sweep by tag returns **zero** surviving `track=cloud-realization` resources (an orphan is a fail-closed finding). The u5 drill **rehearses teardown** by tearing down its temporary restore instance and verifying zero orphans as its own acceptance criterion.

## Acceptance criteria (per unit)

- **u1 (this brief):** accepted design + unit sequence + the operator decisions enumerated.
- **u2 — bc-infra DB stack IaC:** `cdk synth` produces an RDS PostgreSQL 17 instance (pinned engine + parameter group), private subnet + scoped SG, RDS-managed master secret, automated backups + deletion protection; the Aurora construct is removed; cdk-nag clean; no resource created yet (synth + review only).
- **u3 — schema-apply deployment stage:** a CD stage that runs the bc-db runner against a target instance from the single environment definition, forward-only, recording the ledger; rehearsed against a disposable/local Postgres standing in for RDS.
- **u4 — provision non-prod cloud DB (Layer B):** `cdk deploy` of u2 to the dev environment under the standing Layer-B conditions (reviewed at head + stated ceiling ≤ ~US$25/mo + teardown plan); the instance is the pinned engine; the RDS-managed master secret exists; connectivity verified; resources tagged.
- **u5 — apply + AWS-Shared recovery drill (Layer B):** runner applies the baseline; backup → restore (temporary instance ≤ ~US$2, torn down in-run) → parity-verify → bound-monitor, evidence recorded; drill passes; teardown of the temporary instance verified (zero orphans by tag).
- **u6 — credentials wiring:** platform/tenant owner+runtime secrets provisioned and resolved through the contract; no plaintext; rotation configured.
- **u7 — W4 durability:** PITR + retention to the decided objectives; off-account escrow per D9; residency per D11; benchmark (NFR-9) recorded.

## Operator decisions needed

- **D9** — off-account key-escrow target and arrangement (NFR-6).
- **D10** — recovery objectives (acceptable data loss / downtime) per DB category (confirms/tightens the provisional NFR-5 numbers).
- **D11** — whether residency-driven object-store placement and per-tenant retention are wanted (an amendment to DEC-3ee0f6 if so).
- **Production (Gate-④)** — the production environment and its cutover are operator-only; non-production Layer-B units do not need a per-step operator go (they proceed under the standing reviewed-unit + budget + teardown conditions above).
- **IAM** — confirm the `Claude.Assistant` principal carries (or is granted) the permissions the provisioning units need; a deploy that fails on a missing permission is resolved by an operator policy grant, not by broadening scope unreviewed.

## Not decided here

- Instance sizing/class and non-production cost profile (smallest workable per §8.5), Multi-AZ posture, and the read-replica question (deferred until measured, §8.7).
- The production environment and its cutover — Gate-④, its own authorization.
- The exact secret/rotation schedule and the SSM key layout — settled in u6.

## Consequences

1. The DB foundation becomes reproducible on a managed instance by the same spine that CI proves — `build == dump == live` extends from local/disposable to RDS.
2. W1.6 is realized and the W2 cloud exit items (#4 credentials, #6 recovery drill) are completed on real infrastructure; W4 durability is opened with explicit objectives.
3. The rejected Aurora option is removed from bc-infra, ending the dormant-construct drift (aligns with DEC-1918d0).
4. No resource is created by this brief; every provisioning step is confirm-first and production remains operator-only (Gate-④).
