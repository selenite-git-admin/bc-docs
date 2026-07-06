---
uid: DEC-e8a4d2
title: "Definition is the canonical parent — fold contract page into definition page, drop reverse FK"
description: "Metric Definition is the parent of MC; surfaces fold under it. Forward FK on metric_contract.metric_definition_id is the single source of truth; promoted_contract_id reverse column dropped."
status: implemented
date: 2026-04-16
project: bc-core
domain: metrics
refs:
  - type: decision
    uid: DEC-ecec75
    label: "D068 — One contract per KPI"
  - type: decision
    uid: DEC-1918d0
    label: "D162 — Database rules (one source of truth, FK constraints mandatory)"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry has an equivalent row under UID DEC-224f7a (title "Definition is the canonical parent — fold contract page into definition page, drop reverse FK", file_path docs/adrs/ADR-e8a4d2.md). DUPLICATE_CONTENT_RISK per Decision-Registration Integrity Audit 2026-06-22 §3.4. File-side UID DEC-e8a4d2 is the authority used by inbound cross-references; do not re-mint.
---

# Definition is the canonical parent — fold contract page into definition page, drop reverse FK

> **Decision-registration integrity (2026-06-22).** Classified `FILE_ONLY_UNEXPLAINED` (file side) **paired with** `REGISTRY_ONLY` + `DUPLICATE_CONTENT_RISK` (registry side) in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.3–§3.4 and resolved as a documented exception in the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md). The DevHub decision-registry row carrying this same doctrine is `DEC-224f7a` (its `file_path` already points at this file). The file-side UID `DEC-e8a4d2` is the canonical authority for inbound cross-references; the registry row remains under `DEC-224f7a` because `devhub_decision_update` cannot mutate UIDs. Content below is preserved verbatim per Foundation Invariant III.

## Context

The Metric Catalog had three distinct surfaces for the same conceptual entity:
- `MetricCatalogPage` (list of definitions) at `/catalog/metrics`
- `MetricDefinitionDetailPage` at `/catalog/metrics/definition/:id` (catalog metadata + 5D + knowledge)
- `MetricContractDetailPage` at `/catalog/metrics/:contractId` (contract JSON, mapping, output, readiness)
- `MetricContractsPage` (list of contracts) at `/registry/contracts/metric` (a separate top-nav item)

Two pages for the same concept; an extra "Metric Contracts" item in the top nav. Operators had two homes for one mental model.

Worse, the schema had a **reverse-FK smell**: `metric.metric_definition.promoted_contract_id` (parent → child FK) duplicated the relationship already expressed by `contract.metric_contract.metric_definition_id` (child → parent FK). Both columns existed; both were 0% populated. The list page papered over the broken FK with a name-string match (`mc__<name>` ↔ `<name>`), making the UI lie.

The orphan count on April 16: **589 active metric_contract rows had `metric_definition_id = NULL`** despite all 589 names being deterministically resolvable to definitions via the `mc__` prefix pattern.

## Decision

### Schema (one canonical link)

The forward FK is the single source of truth:
- `contract.metric_contract.metric_definition_id` is **NOT NULL** with FK constraint `fk_metric_contract__metric_definition`
- `metric.metric_definition.promoted_contract_id` is **DROPPED**
- A definition→contract lookup is a query, not a stored column: `SELECT metric_contract_id FROM contract.metric_contract WHERE metric_definition_id = ?`

Cardinality is `1 def : N contracts` — a single reverse FK can't express that anyway.

### UX (one canonical page)

`MetricDefinitionDetailPage` at `/catalog/metrics/definition/:defId` is the single home for a metric. It exposes 8 tabs:

| Tab | Source | Gating |
|---|---|---|
| Definition · Formula · Verification · Knowledge | catalog metadata | always |
| Contract · Mapping · Output | contract-scoped (`promotedContractId`) | only if linked contract; else CTA |
| Readiness | Step 0 (Defined) → Step 1 (Contract Bound) → Steps 2-4 (Formula / Chain / Reader from `<ChainReadinessJourney />`) | always |

URL-driven tab state via `?tab=X`.

`MetricContractDetailPage` and `MetricContractsPage` are deleted. Old routes (`/catalog/metrics/:contractId`, `/registry/contracts/metric/:contractId`) redirect via `<ContractRedirect />` which resolves contract → definition through the canonical FK. The top-nav "Metric Contracts" item is removed (folded into Metric Catalog).

### Data backfill

589 active + 189 archived metric_contract rows backfilled from name-match. Match was deterministic (100% coverage, zero collisions) — the same name-match the SQL was hiding behind for derived columns. Then NOT NULL + FK constraint applied so future inserts can't create orphans. The `createMinimalMetricContract` repository method was the source of orphans (its INSERT omitted `metric_definition_id`); now it requires it.

## Options Considered

### Option A — Fold all surfaces into the definition page (chosen)

- One page per metric. One nav home. One mental model.
- Schema enforces parent-child relationship correctly.
- Aligned with D068 (one contract per KPI) and D162 rule 4 (one source of truth per value).

### Option B — Keep separate contract page, just fix the schema (rejected)

- Schema fix solves the data lie but doesn't address the UX duplication.
- Operator still has two homes for one concept.

### Option C — Definition page links out to contract page (rejected)

- Two-level navigation for what is logically one entity.
- Doesn't reduce surface count, just adds a hop.

## Consequences

### Positive

- Schema integrity: orphans physically impossible going forward (NOT NULL + FK).
- One canonical page per metric — no contradictory surfaces.
- The Metric Readiness Overview list now reads truth directly: 1,241 definitions with real gate distribution (`not_contracted` 652, `chain_complete` 568, `chain_incomplete` 13, `formula_failed` 8).
- The metric-reference API columns (`contractedStatus`, `chainStatus`, `chainedCount`, `isPromoted`, `promotedContractId`) are now FK-derived rather than name-matched; they reflect reality.

### Negative

- Doc update required: P04 metric-catalog dossier files reference the dropped `promoted_contract_id` column (specification, architecture, data-structure, integrity, status pages). Flagged as a follow-up task.
- Old code paths using `entry.isPromoted` / `entry.promotedContractId` continue to work (derived in SQL on the SELECT), but the underlying mechanism changed.

### Risks

- **Risk:** A future bulk data import path could repeat the orphan mistake. Mitigation: the FK constraint now refuses the insert.
- **Risk:** Multi-contract scenarios per definition (1:N) require a version selector on the contract-scoped tabs. Mitigation: the existing `useContractVersions` hook is already wired; today only 1:1 in practice but the pattern accommodates 1:N.

## Implementation summary

**Schema migration (executed in single transaction):**
```sql
UPDATE contract.metric_contract mc
SET metric_definition_id = md.metric_definition_id
FROM metric.metric_definition md
WHERE mc.metric_definition_id IS NULL
  AND md.metric_name = regexp_replace(mc.metric_contract_name, '^mc__', '');
ALTER TABLE contract.metric_contract ALTER COLUMN metric_definition_id SET NOT NULL;
ALTER TABLE metric.metric_definition DROP COLUMN promoted_contract_id;
```

The FK constraint `fk_metric_contract__metric_definition` already existed in `11-deferred-fks.sql`.

**Code changes:**
- `bc-core`: 14 files (DDL, Drizzle schema, services, repositories, controllers)
- `bc-admin`: 12 files (page consolidation, new shared components, route redirects, nav cleanup)
- `bc-admin` deletions: `MetricContractDetailPage.tsx`, `MetricContractsPage.tsx`

**New endpoints:**
- `GET /registry/metric-readiness/definition-list` — 1,241 def-keyed rows
- `GET /registry/metric-readiness/orphan-contracts` — 0 today (was 589 pre-backfill)
- `GET /registry/metric-readiness/chain-detail/:mcId` — 3-step journey
- `GET /registry/metric-readiness/tenant-data-list` — chain-complete MCs per tenant
- `GET /registry/metric-readiness/tenant-data-detail/:mcId` — 4-step data journey
- `GET /registry/metric-readiness/resolve-definition/:mcId` — for redirect component

**New shared components (bc-admin):**
- `ChainReadinessJourney.tsx` — 3-step tracker (Formula → Chain → Reader)
- `ContractRedirect.tsx` — contract→definition redirect
- `ContractTabBodies.tsx` — 3 tab bodies (Contract / Mapping / Output) for the def page

## Follow-ups

- Update P04 metric-catalog docs to remove `promoted_contract_id` references and reflect the new canonical FK.
- Re-snapshot golden DB (per Golden Snapshot SOP) — schema + data state changed substantially.
- Investigate the original creator of the 589 orphan contracts (DevHub change records, git history) — closed at the schema level but worth knowing for forensic completeness.
- Potential deletion of orphan `McIntegrityDetailPage.tsx` (no longer routed).
