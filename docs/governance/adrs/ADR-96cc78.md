---
uid: DEC-96cc78
title: "Platform Runtime/Operations surfaces are tenant-attributed via bounded attestation; reconcile runtime.admission_run to the ratified tenant-DB execution home"
description: "Platform Runtime/Operations surfaces are tenant-attributed via bounded attestation; reconcile runtime.admission_run to the ratified tenant-DB execution home"
status: proposed
date: 2026-09-20T11:18:10.115Z
project: bc-core
domain: platform
subdomain: platform-tenant-boundary
focus: governance
---

# Platform Runtime/Operations surfaces are tenant-attributed via bounded attestation; reconcile runtime.admission_run to the ratified tenant-DB execution home

## Context

During the bc-admin UI quality pass (SES-9c706c, 2026-09-20), the platform Operations "Boundary Health" surface was found to display a tenant's admission throughput (Kaveri — 42,976 admitted) as an **unattributed headline**, read directly from platform-resident `runtime.admission_run`. A grounded study (bc-docs PR #44) reconciled this against the ratified platform/tenant boundary and found: the platform must never read/write a tenant DB (DEC-771baf/D232), with one bounded, audited, tenant-explicit inspection carve-out (DEC-f0e78e); admission run records belong in the **tenant DB**, with only aggregates platform-side in `execution.boundary_progression` (DEC-81cd26/D168, DEC-3196eb); the operator surface must **pivot on explicit tenant selection** (ADR-952faa D-4); and `runtime.admission_run`'s platform residence is **drift** whose physical home was formally **deferred** (DEC-01bd6b §H). This ADR is **Phase 0** of the remediation — it fixes the design direction so the UI-plane and data-placement execution acts have a ratified authority to follow, and it is a **design act** (not an execution net) per the D541 plane check.

## Decision

PROPOSED reconciliation ADR (Phase 0 of the platform/tenant boundary remediation). Grounds: grounded study bc-docs PR #44 (docs/evidence/work-records/implementation/platform-tenant-boundary-runtime-operations-study-2026-09-20.md), SES-9c706c 2026-09-20. Trigger: bc-admin Operations Boundary Health shows tenant-runtime figures (Kaveri admission throughput 42976, from platform-resident runtime.admission_run) with NO tenant attribution, contradicting the ratified boundary.

CONTEXT (ratified authorities): DEC-771baf/D232 platform NEVER reads/writes tenant DB (contracts=platform definitions, data=tenant instances). DEC-f0e78e (latest) the ONLY carve-out is a bounded, read-only, AUDITED platform-inspection surface (/api/admin/inspection/*) returning scalars/counts (never raw tenant rows), tenant as an EXPLICIT parameter + inspection_meta envelope + synchronous audit; per-section degrade to state=unavailable. ADR-952faa D-4 the operator surface must pivot on explicit tenant selection (no platform-only mode that hides tenant-runtime evidence). DEC-81cd26/D168 + DEC-3196eb + architecture.md:94 admission RUN records belong in the TENANT DB (execution data); platform holds only AGGREGATES in execution.boundary_progression (data-model-and-schema.md:151); runtime schema is for definitions. DEC-01bd6b section H physical run-substrate home was DEFERRED. DEC-ecd55c/DEC-81cd26 runtime.connection is platform-resident BUT requires a populated tenant_id (ownership-by-column).

DECISION (proposed, for Codex + operator + Platform DB Foundation ratification):
1. bc-admin Operations/Runtime surfaces are re-scoped to tenant-attributed platform-ops: every tenant-runtime figure is sourced via the bounded attestation surface (/api/admin/inspection/*) or platform-side execution.* aggregates, attributed to an EXPLICITLY selected tenant, with inspection_meta rendered, reads audited, and per-section ok/unavailable/broken degradation. Removes the unattributed-headline / evaluation-refusal anti-pattern. IMPLEMENTS DEC-f0e78e + 952faa D-4 (execution act on the UI plane).
2. Resolve the DEC-01bd6b section-H deferral in principle toward the ratified design: admission RUN records to tenant DB (progression.admission_run per D168); platform-side admitted/observed AGGREGATES to execution.boundary_progression; the drifted platform-resident runtime.admission_run is retired/repointed. EXECUTION of this data-placement move is owned by Platform DB Foundation (DEC-75fc71, SES-998962), DBCP-gated, coordinated not merged. If DB Foundation ratifies keeping a platform run-metadata table instead, this ADR is amended accordingly, but the UI (decision 1) must still attribute by tenant regardless of physical home.
3. runtime.connection.tenant_id MUST be populated on tenant-scoped rows (fix writer + backfill) per D168/DEC-ecd55c; runtime.webhook_endpoint tenant_id remains NULL-permissible for platform/operator-scope sinks (notifications-and-webhooks.md:110) until per-tenant external alerting lands.

FOUNDATION GATE: design act (reconciling a governance-boundary + data-placement declaration), not an execution net; repair locations A/B (boundary + contract semantics) and E (storage/projection). Design-vs-execution (D541): this is the design act that must precede any UI/DB execution net. Tasks TSK-df381f (UI, now), TSK-c363d2 (admission_run home, ADR-first), TSK-96684d (connection.tenant_id). Codex-audited. Amends the DEC-01bd6b section-H deferral; supersedes nothing.
