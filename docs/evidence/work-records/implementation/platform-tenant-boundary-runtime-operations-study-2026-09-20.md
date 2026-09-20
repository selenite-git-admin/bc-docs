---
title: Platform/Tenant Boundary — Runtime & Operations UI Study
description: Grounded study of the platform-vs-tenant data boundary as it applies to the bc-admin Runtime/Operations surfaces — what is ratified, what has drifted, keep/drop, acquisition paths, and a Codex-audited remediation plan.
status: evidence
date: 2026-09-20
project: platform
domain: platform
session: SES-9c706c
---

# Platform/Tenant Boundary — Runtime & Operations UI Study

**Trigger.** During the bc-admin UI quality pass (SES-9c706c, 2026-09-20), the platform **Operations → Boundary Health** page was found to show *"42,976 Admitted"* as a headline metric with **no tenant attribution**. Verified against `bc_platform_dev`: that number is a single tenant's admission throughput (`runtime.admission_run`, `tenant_id = kaveri`, 53,720 observed / 42,976 admitted). This study grounds the boundary question in the ratified design (bc-docs ADRs are the SSOT), reconciles it against the live DB/code state, and proposes a remediation plan.

> **Method.** Design authority from `C:\MyProjects\bc-docs` ADRs/chapters (quoted). Live state from `bc_platform_dev` (read-only) + bc-core code. Where design and state diverge, it is flagged; where the design is silent, that is stated rather than inferred.

## 1. The ratified rule

- **The platform must NEVER read or write a tenant DB.** *"Contracts are platform (definitions). Data is tenant (instances)."* — **DEC-771baf / D232** (`ADR-771baf.md:35`, `:69`), *implemented*.
- **One narrow exception:** a bounded, **read-only, audited** platform-inspection carve-out (`/api/admin/inspection/*`, `AdminInspectionModule`) that returns **scalars/counts only, never raw tenant rows**, with the **tenant as an explicit parameter** + an `inspection_meta` envelope `{operator_user_id, target_tenant, observed_at}` + synchronous audit; not available to routine services, writes, or `x-tenant-id`. — **DEC-f0e78e** (`ADR-f0e78e.md:67`, `:71`, `:156`, `:193`), *decided — latest authority*.

So the platform may show tenant **counts/summaries** — but only tenant-attributed, via the bounded contract, audited. A bare cross-tenant count with no tenant label is exactly the shape the envelope rule exists to prevent.

## 2. Keep / Drop / Fix

| Surface / table | Ratified design | Verdict |
|---|---|---|
| Operations/Runtime as **platform surfaces** | In-scope, but must **pivot on explicit tenant selection**, attribute every tenant figure, degrade per-section to `unavailable` when no tenant chosen (ADR-952faa **D-4** `:121`: *"no platform-only mode that hides tenant-runtime evidence"*; DEC-f0e78e `:263`, `:154`; ADR-952faa `:148`) | **KEEP — re-scope** |
| Boundary Health **"42,976 Admitted" (unattributed)** | Violates 952faa D-4 + DEC-f0e78e (`inspection_meta`/explicit tenant); sourced from a platform table, not the D-6 attestation | **DROP as built / FIX** |
| **`runtime.admission_run`** (platform DB, per-run counts) | Ratified home is the **tenant DB** (`progression.admission_run`, execution data) — DEC-81cd26/**D168** (`ADR-81cd26.md:27`), DEC-3196eb, `architecture.md:94`. Platform gets only **aggregates** via `execution.boundary_progression` (`data-model-and-schema.md:151`); `runtime` schema is for **definitions** (`:146`) | **DRIFT** — physical home formally **deferred** (DEC-01bd6b §H); `runtime-operations.md` self-contradicts (`:44` tenant vs `:62` platform) |
| **`runtime.connection.tenant_id = NULL`** | Platform-resident **by design** (D168 / **DEC-ecd55c** `:33`) **but `tenant_id` MUST be populated** — ownership-by-column; basis of the cross-tenant-leak fix (`ADR-ecd55c.md:42`) | **DESIGN VIOLATION / data gap** |
| **`runtime.webhook_endpoint.tenant_id = NULL`** | No ADR governs it; nearest rule allows NULL for platform/operator-scope sinks (current ticketing use) — `notifications-and-webhooks.md:110` | **Defensible now**; gap once per-tenant alerting lands |

## 3. Acquisition paths — designed or not?

- **`admission_run` → platform `runtime` schema: NOT designed — drift.** The reader-runtime writes per-run tenant records to a platform table (`bc-core boundary/reader-runtime/resolved-admission-context.ts:208/215`), but the ratified design routes run records to the **tenant DB** and only **aggregates** to platform `execution.*`. The physical home is explicitly **unreconciled/deferred** (DEC-01bd6b §H).
- **`connection` → platform, `tenant_id` NULL: half-designed.** Platform residence is intended; the missing `tenant_id` is a violation of the ownership model.
- **The read asymmetry is the drift, not the design.** The bc-admin page reads admission counts from the platform-resident (drifted) `runtime.admission_run` at `/boundaries/stats`, while evaluation/metric/action stats correctly live tenant-side (`progression.*`) and are refused ("require tenant scope"). The proper per-tenant read already exists at `/api/t/boundaries/stats` (`@CurrentTenant`, claim-bound). The design says treat **both** the same: explicit tenant + attestation/`execution.*` + per-section degrade.

## 4. Divergences (design vs live state)

1. `runtime.admission_run` in the platform DB contradicts the ratified tenant-DB home (D168/DEC-3196eb/`architecture.md:94`); no superseding ADR reversed it; physical home deferred (DEC-01bd6b §H); doc self-contradiction (`runtime-operations.md:44` vs `:62`).
2. `runtime.connection.tenant_id = NULL` violates D168/DEC-ecd55c (ownership-by-column).
3. Boundary Health's unattributed "42,976" contradicts 952faa D-4 + DEC-f0e78e, and bypasses the D-6 attestation surface.
4. The evaluation/metric refusal is directionally correct, but the designed answer is an **explicit tenant selector + attestation + per-section `unavailable`**, not an unattributed-count-plus-refusal split.
5. `webhook_endpoint` NULL `tenant_id` is design-silent — acceptable for the current platform/operator ticketing use.

## 5. Authority ledger

| Topic | Latest authority | Notes |
|---|---|---|
| Platform↔tenant boundary; inspection carve-out | **DEC-f0e78e** (decided) | Amends ADR-952faa D-4; clarifies D232/D368 |
| Base "platform never touches tenant DB" | **DEC-771baf / D232** (implemented) | Contracts=platform, data=tenant |
| Connection home + tenant_id ownership | **DEC-ecd55c** (implemented) affirms **DEC-81cd26/D168** | tenant_id required |
| Admission run home | Ratified **tenant DB** (D168 + DEC-3196eb + `architecture.md:94`); physical home **deferred** (DEC-01bd6b §H) | as-built `runtime.admission_run` = unreconciled drift |
| Platform run aggregates | `data-model-and-schema.md:151` (`execution.boundary_progression`) | admitted/observed counts only |
| Operator surface tenant-attribution | **ADR-952faa D-4** (decided) | "no platform-only mode that hides tenant-runtime evidence" |
| Webhook tenant scoping | none direct; `notifications-and-webhooks.md:110` | design silent |

## 6. Remediation plan (Codex-audited)

Tracked as **TSK-df381f** (bc-admin UI rework, now), **TSK-c363d2** (admission_run home, ADR-first), **TSK-96684d** (connection.tenant_id).

- **Phase 0 — Design (ADR):** reconcile the deferred `runtime.admission_run` physical home (DEC-01bd6b §H) and affirm the Operations/Runtime UI must source tenant figures via the bounded attestation surface + explicit tenant pivot (implementing DEC-f0e78e/952faa D-4). *Design act; Codex audits the ADR.*
- **Phase 1 — bc-admin UI rework:** explicit tenant selector (all active tenants); every tenant-runtime figure attributed + sourced via `/api/admin/inspection/*` or `execution.*` aggregates; `inspection_meta` rendered; audited reads; per-section `{ok|unavailable|broken}` degrade. Remove the unattributed-headline/refusal anti-pattern.
- **Phase 2 — `connection.tenant_id` data integrity:** fix the writer to set tenant_id (claim-bound); backfill the NULL row; consider NOT NULL (DBCP + DB-Foundation coordination).
- **Phase 3 — `admission_run` home migration** *(only if Phase-0 ADR moves it):* run records → tenant `progression.admission_run`; platform aggregates → `execution.boundary_progression`; repoint reader-runtime writer + platform read. **DBCP-gated; coordinate Platform DB Foundation (SES-998962, DEC-75fc71) — no DBCP without consent.**

**Gates:** each phase's design + each PR reviewed by the Codex external auditor (bc-core direct allowlist; bc-admin/bc-docs operator-relayed), dispositions byte-bound. No cosmetic type/lint polish on these surfaces until the re-scope lands (moot).

## Source references

`docs/governance/adrs/`: ADR-f0e78e, ADR-771baf, ADR-81cd26, ADR-ecd55c, ADR-3196eb, ADR-177c52, ADR-01bd6b, ADR-9c0da7, ADR-952faa, ADR-4c1396, ADR-75fc71, ADR-b1a286. Chapters: `docs/implementation/data-model-and-schema.md`, `docs/implementation/architecture.md`, `docs/operations/runtime-operations.md`, `docs/implementation/notifications-and-webhooks.md`, `docs/reference/data-dictionary/runtime.md`.
