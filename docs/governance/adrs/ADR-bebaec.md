---
uid: DEC-bebaec
title: "Chain Completeness SSOT — Definition of Complete + Persisted Chain Status"
description: "Persisted chain status SSOT with locked 7-link definition of complete and version-aware tracing"
status: implemented
date: 2026-04-13
project: bc-core
domain: contracts
refs:
  - type: decision
    uid: DEC-bef347
    label: "D253 Structural Completeness"
  - type: decision
    uid: DEC-d72560
    label: "D301 Canonical Field — 3rd Contract Primitive"
  - type: decision
    uid: DEC-9a5dc0
    label: "D302 CF Boundary Rule"
  - type: decision
    uid: DEC-cc8fd9
    label: "D303 E2E Chain Test Bench"
  - type: decision
    uid: DEC-da4c51
    label: "D283 Contract Trust Chain"
  - type: decision
    uid: DEC-ebf0b4
    label: "D268 Session Discipline & Data Integrity"
migrated_from: legacy v2 archive
---

# Chain Completeness SSOT — Definition of Complete + Persisted Chain Status

## Context

The contract chain (SC -> AC -> OC -> CC -> MC -> IC) is the backbone of BareCount's execution model. Every metric must trace from its formula variables through canonical fields, business fields, observation mappings, admission contracts, and source fields to be computable.

**Problem:** No locked definition of "complete" exists. Each Claude session computes chain completeness from scratch using `IntegrityService` (stateless, 1,341 lines) and picks its own measurement dimension:

| Session | What It Measured | Number Reported |
|---------|-----------------|-----------------|
| Mar 26 | 5-pill visibility (does each contract exist?) | 100% Finance |
| Apr 11a | BF->OC->source routing | 250/825 MCs (30%) |
| Apr 11b | Real field_mappings after bypass removal | 237 BF gaps |
| Apr 12a | MC structural soundness post-archiving | 545/632 (86%) |
| Apr 12b | Grain CC field_mapping coverage | 22/51 CCs |

All numbers were "correct" — they measured different dimensions. Additionally, `IntegrityService` has 5 known bugs that skew results (see Bugs section below).

**Version gap:** Contract versions have no single-active enforcement. MC co_bindings reference CC names (version-ambiguous), not version IDs. Activation doesn't auto-supersede the previous active version.

## Decision

### 1. Definition of Complete

#### Per-Variable Resolution Chain (L1-L7)

Every MC input variable must traverse 7 links. Break at any link = metric cannot compute for that variable.

```
MC variable (field_code: e.g. "net_revenue")
  |
  L1: CF registered         canonical_field.field_name = variable exists
  |
  L2: CF->BF mapped         cc_field_mapping resolves CF -> BF for this CC
  |
  L3: BF in CC schema       Exact match in CC version's resolved_schema
  |                          (NOT suffix match — "amount" must not match "line_items.amount")
  |
  L4: BF->source mapped     OC field_mapping maps BF -> source_field
  |                          (aggregate ALL OCs for this BO, not first-OC-wins)
  |
  L5: AC covers source      OC source_references has active AC for the source_table
  |                          that provided the L4 mapping (per-field, not per-CC)
  |
  L6: Reader bound           OC has reader_id linked to active reader
  |
  L7: Source field trace     Governance gate — source field traced to catalog registration
```

#### Per-Contract Checks (C1-C5)

```
C1: Contract exists, not archived
C2: Governance state = 'active' (or within transition window)
C3: All D253 required body keys present
C4: Quality gate passes (CR-QG-xx-001 for the contract type)
C5: Bindings complete
    - CC: all BFs in field_selection have cc_field_mapping to CFs
    - MC: all formula variables bound to registered CFs via co_bindings
```

#### End-to-End Chain Checks (E1-E3)

```
E1: Every MC variable passes L1-L7 (zero broken links)
E2: Every grain CF has cc_field_mapping in every bound CC
E3: At least one source system has:
    SC(active) + AC(active) + OC(active) + Reader + field_mappings
```

#### Chain Verdict

| Verdict | Condition |
|---------|-----------|
| `complete` | E1 + E2 + E3 all TRUE |
| `partial` | Variables break at L4-L6 (source-side gaps, fixable with data/mappings) |
| `broken` | Variables break at L1-L3 (structural problems, needs contract edits) |
| `unlinked` | co_bindings reference non-existent CCs |

### 2. Persisted SSOT Tables

Two new tables in `contract` schema (registry metadata, not runtime telemetry). The existing `execution.chain_status` is unchanged (tracks tenant runtime object counts).

#### `contract.chain_trace` — per (MC version x variable x CC version)

Stores the L1-L7 result for every variable in every MC, with full provenance (which OC, AC, reader, source field resolved).

#### `contract.chain_status` — per MC active version (aggregated)

Stores variable counts (complete/partial/broken), grain check (E2), live source check (E3), and the chain verdict. PK = (metric_contract_id, metric_version_code).

### 3. Version Model — Single Active + Transition Window

- Steady state: at most ONE active version per contract
- Transition: when activating a new version, the old active gets `supersede_after = now() + 48h`
- During transition: chain traces BOTH active versions independently
- After transition: expired versions auto-supersede; old traces cleaned on next refresh
- Application-level enforcement (not DB constraint) to allow transition windows

New column on all 5 version tables: `supersede_after timestamptz`

### 4. ChainStatusService (replaces stateless IntegrityService as SSOT)

- Event-driven refresh: triggered by contract activation, CC/OC changes, field_mapping changes
- On-demand refresh: `POST /registry/chain-status/refresh`
- API reads serve from persisted table (no recompute on read)
- IntegrityService kept as-is for backward compat (bc-admin UI), deprecated later

## IntegrityService Bugs Fixed in ChainStatusService

| # | Bug | Location | Fix |
|---|-----|----------|-----|
| 1 | Suffix matching false positive | `fieldExistsInSchema` L1087 | Exact match only |
| 2 | Admission is per-CC not per-field | `getAdmissionReaderChain` L1198 `.slice(0,1)` | Per-field: trace AC for the OC that provided L4 mapping |
| 3 | Two binding sources, first wins | `getBindingsForMetric` L710 | Canonical: use contract_json co_bindings (current standard) |
| 4 | Coverage requires Reader but chain doesn't | L638 vs L980 | Unified: Reader is L6, separate boolean |
| 5 | Computed BFs bypass mapping | `getMappingFields` L1148 | Computed BFs: L4=true with `source_field='computed'`, explicit flag |

## Options Considered

### Option A: Fix IntegrityService in-place (rejected)

Still stateless (no persistence), every session recomputes, no version tracking. The fundamental problem (no SSOT, no locked definition) remains.

### Option B: Materialized view (rejected)

Complex multi-table join doesn't fit materialized view pattern. No event-driven refresh. No version-aware tracing.

### Option C: New persisted service + tables (chosen)

Full version awareness, event-driven refresh, stable numbers across sessions, diagnostic drill-down via chain_trace. Two systems coexist until IntegrityService deprecated.

### Version: Single active + transition window (chosen)

Strict single-active too rigid for production. Unrestricted multi-active too ambiguous. Transition window is the pragmatic middle: controlled coexistence for 48h, then auto-cleanup.

## Consequences

### Positive

- Every session reads the same numbers from the same table
- Chain verdict is stable across sessions
- Break points are precise (link-level, not aggregate)
- Version transitions are safe and auditable
- 5 known bugs fixed

### Negative

- Two chain-checking systems coexist until bc-admin migrated
- Event-driven refresh adds coupling to contract lifecycle
- chain_trace table grows (est. ~50K rows for current portfolio)

### Neutral

- Existing bc-qa SQL invariants (14 checks) remain valid as independent cross-checks
- D303 E2E test bench can validate against chain_status table

## Errata

### 2026-05-09 — execution.chain_status renamed to execution.boundary_progression (audit C-3 follow-up)

`audit-metric-taxonomy-2026-05-09.md` C-3 (P1) and DEC-a8b33e §6 flagged a name collision: the platform had two tables named `chain_status`, one in each schema:

| Table | Grain | Tenant scope | Question answered | Owner ADR |
|---|---|---|---|---|
| `contract.chain_status` | metric_contract × version | none (catalog) | Is this MC chain-complete and shippable? `chain_verdict ∈ {complete,partial,broken,unlinked}`, L1-L7 link presence | This ADR (D305) |
| `execution.chain_status` *(was)* | tenant × contract × object_type | per-tenant runtime | How many records of each object type have flowed for this tenant + contract? `total_count`, `last_created_at` | D169 / D170 |

The two carry **genuinely distinct meaning** — D305 chain quality is per-MC catalog authoring-time; the execution table is per-tenant runtime boundary counts. They are not duplicates. The collision was naming, not data.

**Resolution: Path A (DEC-a8b33e §6).** The execution table is renamed `execution.chain_status → execution.boundary_progression`, with a one-release compatibility window for the legacy endpoint.

**Implementation summary:**

- DB migration: `docker/redesign/migrations/20260509-c3a-execution-rename-chain-status-to-boundary-progression.sql` (one `ALTER TABLE` statement; Postgres auto-renames the PK constraint and indexes).
- bc-core: schema export `chainStatus` → `boundaryProgression`; repository method `listChainStatus` → `listBoundaryProgression`; new endpoint `GET /api/execution/boundary-progression` is canonical.
- bc-core: legacy endpoint `GET /api/execution/chain-status` was kept as a deprecated alias for one release window. **Removed 2026-05-10 in the C-2/C-3 paired compat-window cleanup commit** after a cross-repo grep confirmed zero consumers (bc-admin, bc-portal, devhub, website, dashboard, qa, sdg). The route now returns 404; clients must use `/api/execution/boundary-progression`.
- bc-admin: hook `useExecutionChainStatus` → `useExecutionBoundaryProgression`; type `ChainStatusRow` → `BoundaryProgressionRow`; `IntegrityReportPage` consumer migrated to the new endpoint; the page's table title is now "Boundary Progression by Contract".
- No D305 SSOT change. `contract.chain_status` is unchanged in name, shape, semantics, or owner. The errata exists here because D305 is the authority for the term "chain status" and any future reader investigating the term should find the resolution from the canonical entry point.

**What stays alive:** the boundary-progression table itself — it answers a real per-tenant runtime question that D305 cannot. It is **not** a candidate for retirement and should not drift into duplicating any column from `contract.chain_status`. If a future need pushes the two toward overlap, file an amending ADR rather than letting the names re-converge.

### 2026-05-14 — Pre-activation chain status computation (SES-594568, slice 0.8)

When the official `McOnboardingService.create()` path was first executed end-to-end during slice (1), a sequencing contradiction surfaced:

- **MLS-14 activation gate** (D391 / DEC-b8b825) reads `contract.chain_status.chain_verdict` via LEFT JOIN inside `ContractService.transitionState` and refuses with `MLS-14.chain_not_complete` (BLOCKER) when the verdict is anything other than `'complete'`.
- **ChainStatusService**, as originally implemented for D305, processes only **active** MC versions via `getActiveMcVersions()`. For a fresh MC about to be activated for the first time, no `chain_status` row exists at the moment MLS-14 evaluates it → `chain_verdict = NULL` → refusal for the wrong reason.

The 540 historical active MCs predate D391 (May 4 2026) and never traversed this combined gate. The first new MC promotion through the official path discovered the gap.

**Resolution (slice 0.8, `bc-core@d2a6fa3`):**

- New public method `ChainStatusService.refreshChainStatusForVersion(metricContractId, versionCode)` computes chain status for a specific MC version **regardless of `governance_state_code`**, persisting `chain_status` + `chain_trace` rows for that exact `(mcId, versionCode)` key. Idempotent.
- Upstream CCs/OCs remain active-state-filtered inside `processOneMcVersion` and its walkers — only the *target* MC version is exempt from the active filter, not its dependencies.
- `ContractService.transitionState` calls this method synchronously between the (deprecated) `IntegrityService.getKpiIntegrity` pre-gate and the `Mls14ActivationGate.evaluateAndLog` gate. Pre-activation chain status compute failures abort activation with `ForbiddenException` rather than letting MLS-14 see a missing row and refuse for the wrong reason.
- The catalog-wide `refreshChainStatus(mcId?)` method is unchanged — it retains its active-only semantics for the post-activation refresh case originally specified in D305 §4.

**Why this is not an ADR amendment:** D305 §4 said *"Event-driven refresh: triggered by contract activation, CC/OC changes, field_mapping changes"* — this remains true for the post-activation case. The pre-activation case was implicit in D305's overall design (the existence of MLS-14 reading `chain_status` would have required *some* mechanism to populate the row before the read) but never made explicit. This erratum codifies the sequencing now that the contradiction has surfaced.

**Companion code paths preserved as deprecated:**

- `IntegrityService.lookupStandardFields` was patched in the same slice (`status` → `status_code AS "status"`) only because `transitionState:456` still calls `IntegrityService.getKpiIntegrity` as a pre-gate. Per D305 §"IntegrityService Bugs Fixed in ChainStatusService," IntegrityService is deprecated; the patch is transitional and the comment in the code names it as such.
- `MetricWizardService.completeMetric` (parallel writer producing direct `INSERT INTO contract.metric_contract` + `contract.metric_contract_version`) was quarantined at both the service and controller layers in the same slice. The duplicate writer cannot execute via any path; the canonical replacement is `POST /api/onboarding/seed/:metric_definition_id/promote` (SeedPromotionService).
