---
uid: DEC-89db41
title: "Graceful D575 generalization to runtime planes {tenant, demo} — the in-platform demo runtime plane (bc_demo_runtime)"
description: "Graceful D575 generalization to runtime planes {tenant, demo} — the in-platform demo runtime plane (bc_demo_runtime)"
status: decided
date: 2026-10-26T06:32:51.121Z
project: bc-core
domain: tenants
subdomain: runtime/isolation
focus: runtime-plane-generalization
---

# Graceful D575 generalization to runtime planes {tenant, demo} — the in-platform demo runtime plane (bc_demo_runtime)

## Context

The metric-catalog drive stalled because every recurring blocker was a tenant-plane crossing; the Demoed terminal (DRAFT-ADR-demoed-platform-terminal-2026-10-26.md, D2/D2-guard/D3) requires an end-to-end proof that lives in ONE plane and never crosses into a tenant. D575 OWNS the runtime-plane model and its isolation, so the correct repair layer is to generalize D575 (not to compensate lower, and not Option B's separate DB). The demo plane shares bc_platform_dev with the platform definition schemas, so — unlike the tenant plane which gets isolation free from a separate database — its isolation must be a structural, DB-enforced boundary plus the first-statement RT(demo) identity gate, so customer-data isolation is structural (not intent) and provable for a Codex isolation audit. Grounded in source (tenant-tx-runner.ts::runGuardedTenantTx, runtime-session-identity.ts RT gate, the three frozen d575-*.spec.ts, bc-db 0028). This DEC records ONLY the concrete, auditable plane generalization + isolation contract now; it REFERENCES the Demoed ADR draft, which stays a DRAFT and earns its own terminal-state DEC once DSO lands on the demo plane and proves it (no premature terminal-state scaffolding).

Accepted design: **r3** of `artifacts/architect/DESIGN-d575-demo-runtime-plane-2026-10-26.md` at **barecount-devhub commit 4c9d305b**, sha256 `d3b1525875403e97a8d388c95c442a41faae9d0e2827642c22fc00e88cdcde68`, which folds the Codex gen-e6598a two-round isolation audit (r2: a provider is not a guard; USAGE-deny does not close indirect reach; synthetic sole-writer ingress — and the r3 visibility-ordering correction). Chief co-signed (audit check #6, the PUBLIC-role footgun). The §4 audit contract is the Codex isolation-audit entry point; Codex acceptance is NOT build authorization.

## Decision

Generalize D575's single hard-coded "tenant" runtime plane to a declared set RuntimePlane ∈ {tenant, demo}, each with a runtime role, a GUARDED-TX surface, a first-statement identity predicate RT(plane), and a closed isolation boundary. The tenant plane is unchanged (bc_tenant_runtime, dedicated tbc_{slug} database, DB-isolated). The new demo plane is schema demo.* INSIDE bc_platform_dev (tenant-identical fact shapes, immutable/versioned), provisioned and OWNED by the owner-plane schema-provisioner; the non-escalating, owns-nothing login bc_demo_runtime owns nothing.

Demo access is ONLY through a **guarded demo transaction** — a branded GuardedDemoTx constructible only inside the demo runner, which BEGINs and runs RT(demo) as the FIRST statement before any work. There is **NO raw demo handle** (no demo analog of the deprecated forTenantData; no DEMO_DATA_DB that hands out a raw pool); the architecture gate registers zero unguarded demo sites and goes RED on a planted bypass. RT(demo) = RT's clauses with the role parameterized (not superuser/bypassrls/createrole/createdb/replication; member of no role; owns nothing) PLUS: **current_database() = bc_platform_dev** (a mis-scoped URL to another database is refused, not assumed); and a **schema-reach clause** requiring the login's reachable schemas via has_schema_privilege to be EXACTLY {demo} on EFFECTIVE privilege (already accounting for the non-removable PUBLIC membership — default public-schema USAGE/CREATE to PUBLIC is revoked). No fallback credential (DemoRuntimeCredentialAbsentError); refusals NEVER_DEGRADED.

The privilege boundary is closed for **BOTH direct and indirect reach**, specified as catalog postconditions the audit and the migration check: effective-privilege postconditions (incl. PUBLIC + default privileges) proving bc_demo_runtime reaches nothing outside demo for tables/views/sequences/routines/schemas; and a reachable-object allowlist/dependency check proving no demo-accessible view, SECURITY DEFINER routine, trigger or foreign table reads a customer or customer-adjacent relation or opens a remote tenant path (USAGE-deny alone is insufficient — bc-db 0028 exists because an owner-rights routine can run with owner rights). Grants are exact demo base objects (no default-privileges-on-future); no CONNECT on any tbc_* database (effective, after PUBLIC).

demo.* ingress is a **wholesale, immutable, synthetic fixture rebuild** written SOLELY by the owner plane, with a pre-publication customer-lineage rejection check that **gates VISIBILITY** (not a publication flag): load into an inaccessible staging area bc_demo_runtime cannot read, run the check, then atomic checked promotion into the readable demo fact tables (or a single transaction that loads AND checks and commits only on pass); served reads are restricted to previously-accepted immutable versions; the check fails closed BEFORE any new row is runtime-SELECT-able by bc_demo_runtime. (TSK-564901's dropped-column ruling reconciled.)

No-customer-lineage is therefore provable THREE ways: no direct privilege path, no indirect (owner-rights) path, and synthetic-only governed contents (D3 of the Demoed ADR draft). The three frozen d575-*.spec.ts architecture gates generalize plane-parametrically, shrink-only (tenant assertions unchanged, demo assertions added). Option B (a separate tenant-shaped demo DB) is rejected — it reintroduces the tenant hinge the design removes. Isolation is PRESERVED and generalized, not weakened. Design act (DEC-c48b0f); Repair B (declare the second plane + guarded surface + isolation contract + synthetic ingress) + C (bind bc_demo_runtime).

**DECIDED** — ratified by operator desk grant 2026-10-26T06-59-10-794Z-6adad783 (text_sha256 6adad783a82dabed2413adc9f4e1120f8c783b9743c4729607230da8e8a3cb1d), accepting r3. Design-only: the execution (bc-db migration for schema demo + role bc_demo_runtime + exact least-privilege grants + REVOKE from PUBLIC + catalog-postcondition checks, the guarded demo-tx runner + shrink-only spec generalization, the owner-plane fixture loader + admissibility check) is a SEPARATE operator-gated DBCP unit (validator change + DDL → terms gate + DB yes), not opened by this design act.
