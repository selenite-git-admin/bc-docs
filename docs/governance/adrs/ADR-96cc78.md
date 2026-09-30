---
uid: DEC-96cc78
title: "Platform Runtime/Operations surfaces are tenant-attributed; admission-run records stay platform metadata"
description: "Platform Runtime/Operations surfaces are tenant-attributed; admission-run records stay platform metadata"
status: decided
date: 2026-09-20T11:18:10.115Z
project: bc-core
domain: platform
subdomain: platform-tenant-boundary
focus: governance
---

# Platform Runtime/Operations surfaces are tenant-attributed; admission-run records stay platform metadata

## Context

> **Read with the decision record (2026-09-30).** The Context and the numbered proposal below are the proposal as written on 2026-09-20. It treated platform `runtime.admission_run` as drift to be moved to the tenant database; the operator decided the opposite. Admission-run records are platform metadata written by the executor and stay in the platform database. The "Decision record (2026-09-30)" section at the end governs.

During the bc-admin UI quality pass (SES-9c706c, 2026-09-20), the platform Operations "Boundary Health" surface was found to display a tenant's admission throughput (Kaveri — 42,976 admitted) as an **unattributed headline**, read directly from platform-resident `runtime.admission_run`. A grounded study (bc-docs PR #44) reconciled this against the ratified platform/tenant boundary and found: the platform must never read/write a tenant DB (DEC-771baf/D232), with one bounded, audited, tenant-explicit inspection carve-out (DEC-f0e78e); admission run records belong in the **tenant DB**, with only aggregates platform-side in `execution.boundary_progression` (DEC-81cd26/D168, DEC-3196eb); the operator surface must **pivot on explicit tenant selection** (ADR-952faa D-4); and `runtime.admission_run`'s platform residence is **drift** whose physical home was formally **deferred** (DEC-01bd6b §H). This ADR is **Phase 0** of the remediation — it fixes the design direction so the UI-plane and data-placement execution acts have a ratified authority to follow, and it is a **design act** (not an execution net) per the D541 plane check.

## Decision

PROPOSED reconciliation ADR (Phase 0 of the platform/tenant boundary remediation). Grounds: grounded study bc-docs PR #44 (docs/evidence/work-records/implementation/platform-tenant-boundary-runtime-operations-study-2026-09-20.md), SES-9c706c 2026-09-20. Trigger: bc-admin Operations Boundary Health shows tenant-runtime figures (Kaveri admission throughput 42976, from platform-resident runtime.admission_run) with NO tenant attribution, contradicting the ratified boundary.

CONTEXT (ratified authorities): DEC-771baf/D232 platform NEVER reads/writes tenant DB (contracts=platform definitions, data=tenant instances). DEC-f0e78e (latest) the ONLY carve-out is a bounded, read-only, AUDITED platform-inspection surface (/api/admin/inspection/*) returning scalars/counts (never raw tenant rows), tenant as an EXPLICIT parameter + inspection_meta envelope + synchronous audit; per-section degrade to state=unavailable. ADR-952faa D-4 the operator surface must pivot on explicit tenant selection (no platform-only mode that hides tenant-runtime evidence). DEC-81cd26/D168 + DEC-3196eb + architecture.md:94 admission RUN records belong in the TENANT DB (execution data); platform holds only AGGREGATES in execution.boundary_progression (data-model-and-schema.md:151); runtime schema is for definitions. DEC-01bd6b section H physical run-substrate home was DEFERRED. DEC-ecd55c/DEC-81cd26 runtime.connection is platform-resident BUT requires a populated tenant_id (ownership-by-column).

DECISION (decided 2026-09-30 by the operator, as amended in "Decision record" below):
1. bc-admin Operations/Runtime surfaces are re-scoped to tenant-attributed platform-ops: every tenant-runtime figure is sourced via the bounded attestation surface (/api/admin/inspection/*) or platform-side execution.* aggregates, attributed to an EXPLICITLY selected tenant, with inspection_meta rendered, reads audited, and per-section ok/unavailable/broken degradation. Removes the unattributed-headline / evaluation-refusal anti-pattern. IMPLEMENTS DEC-f0e78e + 952faa D-4 (execution act on the UI plane).
2. ~~Resolve the DEC-01bd6b section-H deferral toward moving admission run records to the tenant DB.~~ **Rewritten 2026-09-30, see "Decision record" point 2.** Admission run records are platform metadata and stay in the platform database.
3. runtime.connection.tenant_id MUST be populated on tenant-scoped rows (fix writer + backfill) per D168/DEC-ecd55c; runtime.webhook_endpoint tenant_id remains NULL-permissible for platform/operator-scope sinks (notifications-and-webhooks.md:110) until per-tenant external alerting lands.

FOUNDATION GATE: design act (reconciling a governance-boundary + data-placement declaration), not an execution net; repair locations A/B (boundary + contract semantics) and E (storage/projection). Design-vs-execution (D541): this is the design act that must precede any UI/DB execution net. Tasks TSK-df381f (UI, now), TSK-c363d2 (admission_run home, ADR-first), TSK-96684d (connection.tenant_id). Codex-audited. Amends the DEC-01bd6b section-H deferral; supersedes nothing.

## Decision record (2026-09-30)

The operator decided this ADR on 2026-09-30 (controller charter report, Part D, decision 7, as revised; desk grant `2026-09-30T10-43-50-336Z-6704da90`, text sha256 `6704da9069452755180a9c251061b112a194f10a14ce6224c7ffd45954afab8b`), with these changes to the proposal above:

1. **Decision 1 stands for the Boundary Health surface, sourced from platform metadata.** Admission run records are written by the executor into the **platform** database: `runtime.admission_run`, `runtime.admission_run_context` and `runtime.admission_run_disposition` (bc-core `src/boundary/reader-runtime/resolved-admission-context.ts`, `src/registry/readers/reader.service.ts`), each run carrying `tenant_id`. They are metadata about execution, not tenant business data, so bc-admin reads them without any tenant-database crossing. What was wrong is only that the figure was shown with no tenant. Every figure on the surface is attributed to its tenant.
2. **Point 2 of the proposal is rewritten.** The DEC-01bd6b section-H question is resolved the other way: admission run records stay in the platform `runtime` schema as metadata. Tenant business data stays in the tenant database, and the platform still never reads or writes a tenant database (DEC-771baf, DEC-f0e78e).
3. **Point 3 stands** (`runtime.connection.tenant_id` populated on tenant-scoped rows).
4. **The runtime page family (deferred).** bc-admin's Runtime Console, Runtime Events, Value Audit and Data Readiness pages read tenant-database tables today (`progression.evaluation_campaign`, `runtime_event`, `reader_watermark`, `webhook_delivery`, `metric_audit_verdict`), via a tenant header from `src/api/runtime.ts` that only `super_admin` can use (bc-core `TenantClaimGuard`). The remedy is for the executor also to write a **platform-side summary** that bc-admin reads, attributed by tenant. That is a later unit, with its own design and database change.
5. **Guard.** bc-admin keeps a boundary test that fails on any new tenant-header send outside a shrink-only allowlist (bc-admin PR 57, `src/__architecture__/tenant-header-boundary.test.ts`). The allowlist reaches zero when point 4 lands.

**Owners:** the bc-admin surfaces are the Admin Portal Controller's (TSK-df381f). The platform-side summary written by the executor is the Platform Controller's, with the DB Controller for its table. Point 3 is the DB Controller's (TSK-96684d). TSK-c363d2 (move admission runs to the tenant DB) is resolved by point 2.
