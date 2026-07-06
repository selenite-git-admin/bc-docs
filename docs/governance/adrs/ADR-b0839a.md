---
uid: DEC-b0839a
title: "SDG Coherent Snapshots and Multi-Projection Architecture"
description: "One SDG with many profiles and many projection adapters; Apex demo source data is a coherence-gated active snapshot, not a running source system. Extends DEC-076521 for the demo path."
status: decided
date: 2026-05-10T06:57:03.577Z
project: bc-synth
domain: metrics
subdomain: synthetic-data
focus: architecture
---

# SDG Coherent Snapshots and Multi-Projection Architecture

## Context

Demos are one-time fresh sessions, not multi-day autonomous operations. The 30-minute CFO Pack demo never observes wall-clock time-pass within a session — every prospect sees a fresh state. A continuously-living source system pays daemon-shaped architecture cost (state machines, cadence machinery, between-tick semantics, idempotency on replayed decisions) for an outcome the demo never observes. Snapshots make coherence stronger (frozen state cannot race with a live emit), make the storyboard's quarterly-rotation requirement land at regen time rather than runtime, and decouple Apex's demo path from production-only daemon framing without forfeiting the option to run daemon mode for future long-lived lab/sandbox profiles. Crucially, this pivot keeps DEC-076521's locked source identity (source_system='s4hana', canonical S/4 reader pull path, no push-to-bc-core, bc-sdg as the simulated SAP endpoint) entirely intact — only the upstream "what writes the data into bc-sdg's storage" changes.

# SDG Coherent Snapshots and Multi-Projection Architecture

## Context

bc-sdg is the synthetic data origin for BareCount demo and dev tenants. Two prior framings shaped the codebase:

- **DEC-049cb1 (D395, superseded)** — locked a daemon model: per-pattern arc state machines, daily-emit Lambda + monthly-close + quarterly-pattern-refresh + hourly-coherence + monthly-rollover + custom `apex-emitter` source system + push-to-bc-core. Already abandoned.

- **DEC-076521 (D396, decided)** — corrected the source-identity error in DEC-049cb1: Apex tenant uses canonical SAP S/4HANA (`source_system='s4hana'`) via existing `SapOdataV4Executor` + `sap-s4-cloud-odata` reader flavor; bc-sdg's 4200/6200 OData server is the data origin under a profile-parameterised SDG-SAP framing. Components A (world-state persistence) / B (pattern engine) / C (bookkeeping-correct posting) / E (Lambda+EventBridge orchestration) were preserved-in-spirit; Component D (push) was thrown away.

Two things we have learned by attempting to implement DEC-076521's daemon framing:

1. **The CFO Pack demo never observes time-pass within a session.** Storyboard §1 calls "the moment a Group CFO realises she no longer has to negotiate truth" the entire pitch. The 30-minute role tour is "what is true at as_of_date" navigation; nobody advances time mid-presentation. A continuously living source pays for an outcome the demo session never displays.

2. **Coherence is stronger when state is frozen.** Storyboard §9 declares 8 identity-level assertions (CCC = DSO + DIO − DPO; xPress same-party net = vendor − loan; Σ BSEG = GLT0; etc.) that must hold by construction. A daemon-shaped coherence checker has to reason about a state that may be moving under it; a snapshot-shaped checker runs once against frozen state and can fail-loud and block the snapshot from going active. The "data settles" claim cannot erode silently — strict gating is the strongest enforcement of the Demo Operations hard contract.

A second observation, orthogonal to the daemon-vs-snapshot question:

3. **Profile and source system are not the same thing.** "Apex Motors" is a tenant brand and a story shape (5 BUs, NBFC arm, 1100-PLT plating event, MetroLink delinquency). "SAP S/4HANA" is one possible source system that an Apex deployment might be observed through; "Oracle Fusion Receivables" is a different one. A future apex-on-Oracle deployment is the same Apex story, viewed through a different ERP. Coupling the synthetic-data generator to one ERP per profile would force duplicating Apex's world per ERP — paying for an architectural fork that the semantic facts do not require.

This ADR locks the architecture for both: snapshot semantics for the demo path, and a multi-projection model that lets one SDG core feed any number of source-system projections.

## Definitions

| Term | Definition |
|---|---|
| **Profile** | Target company / story shape and semantic world. Example: `apex-motors` (auto-OEM, 5 BUs, NBFC arm, the 7 storyboard narrative events). The profile names what is true about the business; it does not name how the data is observed. |
| **Snapshot** | Coherent generated state for a single tuple `(profile_code, as_of_date, seed, generator_version)`. A snapshot contains 12–24 months of historical transactional rows plus the storyboard's narrative events placed at specific dates inside that window, with all lifecycle states (paid / open / overdue / cleared / disputed) precomputed at `as_of_date`. |
| **Semantic fact** | A profile-level, source-system-agnostic business record. Examples: customer_invoice, accounting_document, accounting_line, receivable_open_item, payment_clearing. Semantic facts are what a snapshot writes. |
| **Projection adapter** | Source-system-specific view over the snapshot's semantic facts. Examples (current and future): `s4hana`, `oracle-fusion`, `netsuite`, `sap-ecc-legacy`. An adapter renames and reshapes semantic facts into source-entity sets a real customer's ERP would expose. |
| **Projection flavor** | Protocol/version/shape within an adapter. Examples: `s4hana-cloud-odata-v4`, `s4hana-onprem-cds`, `oracle-fusion-rest-v1`, `netsuite-suiteql`. A flavor names the wire shape; an adapter names the source-system family. |

A tenant binds to **a profile + a projection flavor**. Today this binding is expressed via `runtime.connection.endpoint_uri` plus the tenant's `runtime.reader_binding`. The binding pair is independent: Apex bound to `(apex-motors, s4hana-cloud-odata-v4)` today; a future Apex-on-Oracle dev tenant could bind to `(apex-motors, oracle-fusion-rest-v1)` against the same SDG snapshot.

## Decisions

### D1. One SDG, many profiles, many projection adapters

bc-sdg is one repository, one process per environment, one core data store. Inside it:

- A **profile registry** declares profiles. Each profile owns a manifest, a generator function, a narrative-event registry, and a coherence-assertion registry.
- A **projection-adapter layer** sits between the snapshot store and the OData / REST / SQL surface bc-core readers consume. Each adapter targets one source-system family and translates SDG semantic facts into that family's entity sets.
- Profiles do not know about projection adapters; adapters do not know about profile narrative semantics. Both share only the semantic-fact schema.

**Forbidden:** creating a separate SDG repo / process / store per ERP. **Forbidden:** treating `apex-motors` as synonymous with S/4. **Forbidden:** baking `source_system_code` into snapshot identity.

### D2. Apex demo uses coherent active snapshots, not a running source system

For the Apex tenant on the CFO Pack demo path, source data is a **single active snapshot** generated by `generateProfileSnapshot(profileCode, asOfDate, seed) → snapshot_id`. The snapshot:

- Spans 12–24 months of historical transactional data ending at `as_of_date`.
- Embeds the storyboard's 7 narrative events as deterministic placements inside that window (e.g. MetroLink last-paid-on = `as_of_date − 56 days`; xPress NBFC loan opened `as_of_date − 18 months`; 1100-PLT chemical-bath failure mid-month around `as_of_date − 60 days`).
- Carries precomputed lifecycle states (paid / open / overdue / cleared / disputed) for every transactional record, deterministic from `(invoice_date, payment_date_or_null, dispute_state, as_of_date)`.

Generation is a pure function of inputs. `(profile_code, as_of_date, seed, generator_version)` re-run produces identical content. No state machines, no daily ticks, no between-tick idempotency reasoning.

### D3. DEC-076521 still governs source identity and reader pull path

This ADR does **not** modify DEC-076521 §0 (`source_system='s4hana'`) or §1 (canonical S/4 reader chain via `SapOdataV4Executor` + `sap-s4-cloud-odata` flavor + bc-sdg's V4 endpoint). The Apex tenant's Trust Chain still reads exactly as a real S/4HANA customer's would. The only thing this ADR changes is what writes the data into bc-sdg's storage — the daemon framing in DEC-076521 §2 (story-pattern engine), §3 row B (Pattern engine), and §3 row E (Lambda + EventBridge orchestration) is extended/superseded for the Apex demo path by the snapshot model below.

The replaced framing is parked, not deleted: a future long-lived "lab tenant" or non-demo profile could revive the daemon shape on its own track without affecting Apex.

### D4. Source lifecycle states are precomputed inside the snapshot

A `customer_invoice` row carries its own `lifecycle_state ∈ {paid, open, overdue, cleared, disputed}` set deterministically at generation time as a function of `(invoice_date, payment_date_or_null, dispute_state, as_of_date)`. A `receivable_open_item` row exists or does not exist based on the precomputed state of the parent invoice — no aging logic at OData read time, no time-dependent computation in the projection layer.

Why precompute: the demo session reads a frozen state. Recomputing aging on every OData hit would (a) move the temporal-truth boundary away from the snapshot generator, where it belongs, and (b) make the coherence checker harder to reason about.

### D5. Active snapshot is coherence-gated

The 8 storyboard coherence assertions (storyboard §9) run once at the end of `generateProfileSnapshot()`. Verdict logic:

- **Pass** → the new snapshot is committed with `status='active'`; the previously active snapshot is auto-flipped to `status='archived'`. The single-active-per-profile partial unique enforces the invariant.
- **Fail** → the new snapshot is committed with `status='pending'`; the previously active snapshot remains active. An operator must explicitly investigate, override, or regenerate. **No silent activation.**

This is the strongest enforcement of the Demo Operations hard contract "the *data settles* claim cannot erode silently". Failed coherence cannot reach a demo prospect.

### D6. Transactional rows are snapshot-scoped; master/reference rows remain profile-scoped for v1

| Table family | Scope | Why |
|---|---|---|
| Transactional facts (customer_invoice, accounting_document, accounting_line, receivable_open_item, payment_clearing, …) | `(snapshot_id, natural_key)` | Volume varies per snapshot; lifecycle states differ per `as_of_date`; archived snapshots must be queryable by snapshot_id without contaminating active queries. |
| Master / reference (entity, gl_chart, cost_center, standard_cost) | `(profile_code, natural_key)` | Invariant across snapshots of the same profile. The 5 Apex BUs and 8 storyboard GL accounts do not change between regen-with-different-seed runs. |
| Coherence verdicts (coherence_check) | `(snapshot_id, assertion_id)` | A check belongs to one snapshot. |
| Generation metadata (generation_log) | one row per `generate()` invocation | Tracks generator_version, duration, row counts, coherence verdict. |

If a future profile evolves master data over time (a new BU added, GL chart restated), the model can promote master to snapshot-scoped at that point. Defer until needed.

### D7. Previous snapshots are archived, not deleted

The `snapshot.status` ladder is `pending` → `active` → `archived` → `deprecated`. Generation flips a passing new snapshot to active and the previous active to archived. No deletion in the default path. Three layers protect history:

- Archived snapshots stay queryable by `snapshot_id` (operators can dig into them via SQL, or via a future snapshot-diff command).
- `snapshot archive <id>` and `snapshot restore <id>` allow flipping an old snapshot back to active without regenerating — useful for reproducing a prior demo.
- `snapshot prune --keep N` flips old archived ones to `deprecated`; a separate explicit `snapshot purge --status deprecated` actually drops the rows (CASCADE on `snapshot.snapshot_id`). Active is never prunable.

OData/API projections filter strictly: `WHERE snapshot.status = 'active' AND snapshot.profile_code = <bound profile>`. A reader cannot accidentally see archived or deprecated state.

### D8. Future Oracle/NetSuite projections map the same semantic facts, not new SDGs

The semantic-fact schema is the seam. When apex-on-Oracle becomes a real demo target, the work is:

1. Add an `oracle-fusion` projection adapter under `src/sdg/projections/oracle-fusion/`.
2. Map snapshot semantic facts (`customer_invoice`, `accounting_document`, …) to Oracle Fusion entity sets (`ReceivablesInvoiceTransactionsAll`, `XlaJournalLines`, …).
3. Bind the apex-motors profile to the oracle-fusion adapter via a tenant `runtime.connection`.

What does **not** happen: a separate SDG repo, a duplicate `apex_world` schema for Oracle, an `apex_oracle-emitter` source system. The semantic facts are written once by the profile generator; adapters are read-only views.

## DSO First Vertical Slice

The first concrete instance of this architecture covers DSO at Apex via the S/4 projection. Semantic facts and their S/4 projections:

| Semantic fact (SDG core) | S/4 projection (entity set) | Future Oracle Fusion projection example |
|---|---|---|
| `customer_invoice` | `I_BillingDocument` | `ReceivablesInvoiceTransactionsAll` |
| `accounting_document` | `BKPF` (or `I_AccountingDocument` for V4 cloud) | `XlaAeHeaders` |
| `accounting_line` | `BSEG` (or `I_AccountingDocumentItem`) | `XlaAeLines` |
| `receivable_open_item` | `BSID` | `ArTransactionsAll` (with status filter) |
| `payment_clearing` | `BSAD` (cleared AR) | `ArReceivableApplicationsAll` |

The DSO formula needs `accounts_receivable_balance` (from `receivable_open_item`) and `total_credit_sales` (from `customer_invoice`). Both come from the same snapshot, both projected through the same adapter at the same active version.

The first projection adapter to land is **S/4 Cloud OData V4** because DEC-076521 locks `source_system='s4hana'` for the Apex demo today. Other adapters are explicitly out of scope for the first slice.

## Caution on existing `vbrk` table

Phase 2.1 introduced `sdg_world.vbrk` as a SAP-shape table (VBELN-style key, NETWR amounts, F2 billing type). At the time, daemon framing implied no projection layer — vbrk was both core and adapter.

Under the architecture this ADR locks, that double role is wrong: the core should hold a source-system-agnostic `customer_invoice` fact; the S/4 adapter should rename it to `I_BillingDocument` at projection time. If `vbrk` is preserved as the canonical core table, the Oracle projection would have to rename a SAP-shape table back into Oracle terminology — an impedance mismatch the design is meant to prevent.

**Resolution rule (deferred to next slice):** treat `sdg_world.vbrk` as a **first-adapter staging table for the S/4 projection**. It stays usable until the next slice consciously decides between two paths:

- **Path A — promote to core (rename).** `vbrk` → `customer_invoice` with column renames (BillingDocument → invoice_number, NETWR → net_amount, etc.). The S/4 projection then maps `customer_invoice` → `I_BillingDocument` at OData fetch time.
- **Path B — keep `vbrk` as S/4 staging, add neutral core.** New table `sdg_world.customer_invoice` becomes the snapshot's authoritative store; `vbrk` (and any future `oracle_ar_transactions`) become per-adapter projection tables fed from `customer_invoice` at generation time.

This ADR does NOT lock between A and B; it locks only that the current `vbrk` table cannot become the permanent core abstraction by inertia. The next-session DDL request must surface this choice explicitly.

## Consequences

- **No 6100 Apex shortcut.** The 6100 in-memory ECC simulator remains for sandbox1 only. Apex must not be served from it: the Trust Chain identity would shift to `source_system='sap_ecc'` and undermine the demo positioning. (Reaffirms DEC-076521 §0.)
- **No push-to-bc-core.** Reaffirms DEC-076521 §1. bc-sdg is pull-only from bc-core's perspective. The 6200 SDG-SAP server emits OData; bc-core's reader fetches.
- **No one-generator-per-ERP fork.** A new ERP target = a new projection adapter, not a new SDG. Snapshots are written once.
- **No `source_system` field in `snapshot` identity.** Snapshot identity is `(profile_code, as_of_date, seed, generator_version)`. Source system is a property of the projection adapter that serves the snapshot, not of the snapshot itself.
- **Local demo refresh becomes:** `snapshot generate` → coherence gate → reader pull. Three commands, three concerns, each verifiable.
- **Existing daemon CLI surface (`sdg sap tick`, `sdg sap seed`, `sdg sap status`)** remains usable until the snapshot CLI lands; deletion is sequenced after the snapshot CLI is operational so we never lose the ability to test the existing apex-motors world during the transition.
- **`generation_log` is new; legacy `emit_log` is preserved for now.** Existing emit_log rows from prior dev work are not destroyed; the next slice will introduce `generation_log` alongside, and a future cleanup may rename or drop emit_log only when no path references it.
- **Daemon mode is parked, not deleted as a concept.** A future ADR may revive the daemon framing for a long-lived lab/sandbox profile that explicitly wants live cadence semantics. That ADR would be additive to this one, not contradictory.

## Out of scope for this ADR

- Implementing Oracle / NetSuite / any non-S/4 projection adapter.
- AWS / EventBridge / Lambda deployment mechanics.
- Phase 2 DDL (snapshot table, snapshot_id columns, vbrk core-vs-staging decision). Next session under DBCP.
- Reader execution against any tenant.
- Platform DB onboarding (S/4 SC + OC + flavor + canonical_mapping + tenant bindings — Phase 2.4 / 2.5 of the prior plan; sequencing unchanged).
- Bridging the 4200 multi-profile server to `sdg_world` (TSK-5f16b0 — orthogonal).
- Cross-snapshot diff tooling.
- Snapshot-export / portable-snapshot artifacts (e.g. zip-and-share for offline reproduction).

## Schema and code implications for the next session

This is **not** an implementation list — it is the ground truth the next slice must address. Each item gates on its own DBCP ack.

### Schema

1. New `sdg_world.snapshot` table:
   - Columns: `snapshot_id TEXT PRIMARY KEY`, `profile_code TEXT NOT NULL`, `as_of_date DATE NOT NULL`, `seed TEXT NOT NULL`, `generator_version TEXT NOT NULL`, `horizon_months INT NOT NULL`, `status TEXT NOT NULL` (pending|active|archived|deprecated), `summary_json JSONB NOT NULL`, `generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`, `archived_at TIMESTAMPTZ`.
   - Natural key UNIQUE on `(profile_code, as_of_date, seed)`.
   - Partial UNIQUE on `(profile_code) WHERE status='active'` — enforces single-active-per-profile.
2. `snapshot_id` column on transactional tables (current and any future). At minimum: `customer_invoice` (or `vbrk`), `accounting_document` (or `bkpf`), `accounting_line` (or `bseg`), `coherence_check`. Each `ALTER TABLE` is its own DBCP ack and must include the natural-key replacement (drop old UNIQUE, add `(snapshot_id, …)` UNIQUE).
3. `generation_log` table (new): one row per `generateProfileSnapshot()` invocation; tracks `generator_version`, `duration_ms`, `coherence_verdict`, `row_counts_json`. Legacy `emit_log` left in place untouched.
4. Resolution between Path A (promote vbrk to core via rename) vs Path B (keep vbrk as S/4 staging, add neutral `customer_invoice` core). This decision must precede the snapshot_id rollout on transactional tables.
5. **Deferred** until snapshot CLI lands and daemon CLI retires: drop `period_state`, `pattern_state`. Until then they remain inert.

### Code

1. New `generateProfileSnapshot(profileCode, asOfDate, seed, horizon=24): SnapshotPlan` — pure function returning a plan. Reuses `core/document-balancer.ts` (assertBalanced, buildCustomerInvoice).
2. New `applySnapshot(plan): SnapshotApplyResult` — atomic transaction: writes the snapshot row, all transactional rows, runs coherence checker, sets status to `active` or `pending` based on verdict, flips prior active to archived.
3. Coherence checker (Phase-4 work in the prior plan, now elevated to gate-blocker): runs the 8 storyboard assertions against the snapshot's frozen state.
4. New CLI surface: `sdg sap snapshot generate|list|active|archive|restore|prune|purge`. Existing `sdg sap tick|seed|seed-entities|status` remain operational until the snapshot CLI is proven; sequenced retirement after.
5. Refactor: `delinquent_fleet` emitter logic from `posting/delinquent-fleet.ts` becomes a callable invoked by the snapshot generator's invoice-history walk. The emit-side framing (PostingBatch.billingDoc, persistBatch's emit_log fence) stays usable for backwards-compat during the transition.
6. 6200 V4 handler: filter by `WHERE snapshot.status='active' AND snapshot.profile_code = <path-derived>`. Existing V2 routes preserved.
7. Manifest reframe: `apex-motors/manifest.ts` `patternsProvided[]` → `narrativeEvents[]` with placement-rule semantics (e.g. `placementRule: 'as_of - 56 days'` for MetroLink). Coherence assertions, entitiesProvided, profile metadata unchanged.
8. New: per-projection adapter directory `src/sdg/projections/<adapter>/<flavor>/handler-vN.ts`. The S/4 adapter at `src/sdg/projections/s4hana/cloud-odata-v4/handler.ts` is the first. The current `src/sdg/odata/handler-v4.ts` becomes the seed for this directory move (or stays at its current path with a re-export — file move is its own commit).

## Cross-references

- DEC-076521 (D396, decided) — Apex source identity and reader pull path. **Authoritative for §0/§1; daemon framing in §2 + §3 row B + §3 row E extended/superseded by this ADR for the Apex demo path.**
- DEC-049cb1 (D395, superseded by DEC-076521) — original daemon-with-push framing. No additional change here.
- DEC-d2cdb9 (D384) — SAP API admission stance (Published OData / CDS Published Views). Unchanged.
- DEC-6cb4f3 (D385) — Source Systems framework. Unchanged; multi-projection is consistent with it.
- DEC-28b176 (D394) — Metric Readiness Model. Unchanged.
- DEC-771baf — Tenant database architecture. Unchanged.
- DEC-1918d0 — Database rules. Unchanged; this ADR introduces no JSONB-on-queryable-data and no denormalised counters.
- `bc-sdg/CLAUDE.md` — operator orientation; this ADR adds the multi-profile/multi-projection framing.
- `bc-docs-v3/docs/operating-model/demo-plan-cfo-pack-storyboard.md` — storyboard the apex-motors profile is the data origin for. Storyboard §9 coherence assertions are the gate this ADR's coherence checker enforces.
