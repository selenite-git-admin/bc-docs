# Implementation Design Package — Odoo Pilot Source Realization

**Status:** DRAFT for independent review (Codex auditor PoV). NOT an authorization to build.
**Prepared:** 2026-07-30 · **Authority context:** D537 (pre-staging) · D538 (master-data
framework) · D539 (no platform FX) · D524 (BC+Odoo pilot, **Track-C hold**) · D526 (source
dockets) · D519/D523 (audit = governance confidence, not certification).
**Scope decision (operator, 2026-07-30):** FULL STACK — world → reader → chain → projection.

> **⟳ RECONCILED 2026-07-31 (read before reviewing).** After this package was drafted, the
> operator decoupled source-side from metric-side. The **source-side** is now owned by
> `FRAMEWORK-odoo-target-company-profiles.md` + the **`bc-pilot`** repo (world engine) +
> `DESIGN-bc-admin-profile-console.md` (read model). This package is therefore the
> **DEFERRED E2E platform-integration design** — its load-bearing content is **§4 (reader)
> and §5 (contract chain), Track-C-gated**. **§3 (world) and §3.5 (catalog) are SUPERSEDED**
> by the framework doc; they remain here only as the context §4/§5 assume, not as the
> build spec. Read the framework doc first; read this for the reader + chain design.

---

## 0. What this package is, and what it is not

This is the end-to-end **design** for realizing Odoo as BareCount's first pilot source
system, from synthetic-but-realistic source data through to metric output. It exists so an
independent auditor (Codex) can read the whole path *before* the expensive clean build,
and find design defects while they are cheap.

**It is a design for review. It is NOT:**
- an authorization to author or activate any SC/AC/OC/CC/MC over Odoo — that is **held
  until Track C** (D524). Section 4 designs the chain *shape*; building/activating it is
  out of scope and explicitly gated.
- a platform certification. Codex's role here is **governance confidence** — is the
  design coherent, complete, and free of the class of defect the dry-run surfaced? — not
  "does the platform work" (D519/D523).
- part of the intrinsic metric audit, which stays on SAP ECC (D524 audit-independence
  boundary). This is a separate source-realization lane.

**Evidence base:** the 2026-07-30 dry-run — a full 5-FY, 3-company Indian-manufacturer
world built in a real Odoo 17 instance, all verification gates green, AMI
`ami-0de1ac3735186651f`. The dry-run is the *input* to this design, not part of it. Its
scars (≈1,730 cancelled documents across three remediation waves) are the reason several
design rules below exist; each is cited.

---

## 1. Section map (what Codex reviews)

| § | Title | Readiness | Primary artifact |
|---|---|---|---|
| 2 | Design boundaries & doctrine conformance | READY | this doc |
| 3 | World-engine chronological rebuild | READY | `PLAN-odoo-pilot-v2` §1 + gate battery |
| 3.5 | **Source Catalog onboarding — THE platform entry point** | READY (bc-core-cited) | live `source.*` catalog, 2026-07-30 |
| 4 | Odoo Reader Flavor + executor + ORM domain serializer | READY (bc-core-cited) | reader architecture map, 2026-07-30 |
| 5 | Contract-chain SHAPE over Odoo (SC/AC→OC→CC→MC) — design only, Track-C-gated | READY (bc-core-cited) | contract-chain map, 2026-07-30 |
| 6 | Cross-system projection order (Odoo→BC→SFDC via shared registry) | READY | D538 join-key model |
| 7 | Open shortcomings & accepted limits | READY | dry-run ledger |
| 8 | Review protocol & disposition ledger | READY | this doc |
| 9 | **Phased execution & Track-C boundary** | READY | this doc |

---

## 2. Design boundaries & doctrine conformance

Each of the six Foundation invariants, and how the pilot design honors it:

- **I — meaning evaluated once:** the world engine emits source-shaped facts only; all
  metric meaning is produced at the MC boundary. The dry-run proved the trap in reverse —
  when we let a lower layer (generic accrual rotation) manufacture a loan balance, it was
  meaningless; loans had to move to a real lifecycle. Rule: **no lower-layer compensation
  for a metric the contract underspecifies.**
- **II — object ordering fixed:** the chronological rebuild (§3) IS this invariant applied
  to generation — forward-only, no back-reference. Not cosmetic: it dissolves the entire
  inter-pass defect class (phantom remits, REV-chains) the layered dry-run hit.
- **III — state immutable:** append/supersede, never rewrite. The dry-run honored this the
  hard way — Odoo refused to unlink ever-posted moves, so corrections were *cancellations*,
  and cancelled twins are treated as absent by `state != cancel` idempotency.
- **IV — references explicit:** registry IDs (`CUST-`/`VEND-`/`ITEM-`/…) are the
  cross-system join keys, never platform identity; the platform resolves identity at
  contract time. FX amounts reference the source's own booked rate (D539), never "latest".
- **V — evaluation non-replayable:** open state is emitted as dated reconciliation events,
  never as an as-of-now status flag. Reader reads never trigger evaluation — **verified in
  §4.5**: the executor path is read→admit→fact-write only; evaluation is a separate
  downstream boundary the reader never calls.
- **Correction (§4.7):** an earlier version of these docs claimed canonical resolution
  "fails closed without a legal entity on the object." It does not — `pickLegalEntity`
  falls back to `'*'`; fail-closed is transitive via the fiscal-calendar gate. The world
  engine's per-document `company_id` is still correct; the justification was not. Whether a
  hard no-company⇒reject rule is wanted is an open design decision for the reviewer.
- **VI — evidence emitted:** the anomaly register (`anomalies.json`, 15 planted defects) is
  the falsifiable proof surface — evidence emitted, not inferred.

**Repair-location discipline:** the pilot spans A (source reality / reader / admission),
B (contract semantics), C (binding), D (evaluation), E (storage), F (read model). §4–5
must name which layer each design element lives in and confirm no layer compensates for a
gap in an upper one.

**The date doctrine (verified first-hand, 2026-07-30) — the finding that makes the pilot
worth building:** business dates (posting `date`, `invoice_date`, `invoice_date_due`,
reconciliation/clearing date) are fully backdatable and are spread across the 5-FY window;
Odoo-owned wall-clock metadata (`create_date`, CRM `date_closed`) is NOT backdatable. All
296 active finance MCVs read business dates → meaningful results. Only audit-log-derived
process-velocity (CRM stage-dwell) is compressed on a back-seed; the living-data window
fixes it forward. **This boundary must be stated to any metric consumer.**

---

## 3. World-engine chronological rebuild (READY)

Full design in `.claude/PLAN-odoo-pilot-v2-2026-07-30.md` §1. Summary for the reviewer:

- **One forward simulation loop**, not layered passes: `company_creation()` → per-month
  `master_deltas → operations → month_close → next_month_obligations`. Rationale and the
  defect classes it eliminates: PLAN §1.
- **Master data lives in the flow** (operator, 2026-07-30): customers/vendors onboard and
  churn in their month; machines are **bought as named-vendor bills and retired as
  disposals** (accumulated-depreciation writeback + gain/loss on sale) in their month.
- **Gate battery = the acceptance test** (all green on the dry-run): `verify/integrity.py`
  (per-company zero-sum, orphans, FX both-amounts), `verify/benchmarks.py` (profile
  financial-structure indicators — B2B, enforced ranges), `verify/coa_coverage.py`
  (per-company ≥70%; dry-run hit 97%), REV-chain + duplicate-remit regression guards.
- **Profile benchmarks** (operator design): `master.json.benchmarks` declares the
  B2B-manufacturer common-size envelope; the gate fails outside it. This is how the
  B2C-scale ad-spend error (caught by eye in the dry-run) becomes mechanical.
- **Generator rules the dry-run paid for:** idempotency = ref + `state != cancel`; one rnd
  stream per generator per month; reversal sources exclude their own outputs; registers
  built by discovery, not by logging creations.

**Open for reviewer:** the back-seed carries scar tissue (cancelled docs, compressed CRM
timestamps). The pilot world is a CLEAN one-command rebuild from this design; the dry-run
AMI is reference only. Does the reviewer accept "books history backdated, behavioral
history forward-only from go-live" as the honest data contract?

---

## 3.5 Source Catalog onboarding — THE platform entry point (repair location A)

**This is the first platform-side act — it precedes the reader (§4) and every contract
(§5).** Missed in the first draft; added on operator catch. A source system does not exist
to the platform until it is registered in the Source Catalog (the `source.*` schema, Tier-5
metadata: *what systems / objects / fields exist*). The Source Contract (§5 step 1) schemas
reference catalog objects; the reader's source entities (§4) must exist as catalog objects
first. This is CLAUDE.md's first canonical onboarding procedure — **Source Registration**
(`onboarding/source-registration.md`: register system → add tables → add fields) — and
`Seed Catalog Management`; MCP surface `devhub_register_source_stack`.

### 3.5.1 Catalog hierarchy (live, verified 2026-07-30)
`source.source_system` → `source.source_version` → `source.source_module` →
`source.source_object` → `source.source_field` (+ `source.source_provider` on the system).
Lifecycle `catalog_status`: planned → registered → approved; plus governed
`verification_status` / `validation_status`.

### 3.5.2 Live state — Odoo is ABSENT (greenfield confirmed, deeper than §5 said)
The live `bc_platform_dev` catalog holds **only two systems, both `approved`:**

| system | versions | modules | objects | fields |
|---|--:|--:|--:|--:|
| `ecc` (SAP ECC) | 1 | 26 | 14,569 | 222,572 |
| `s4hana` (SAP S/4HANA) | 2 | 39 | 16,273 | 259,405 |

**No Odoo row exists in the live catalog.** (Seed CSVs list `odoo-erp`/`odoo-crm` as
`planned`, but that seed was never loaded here — a correction to §5's seed-based read: Odoo
is greenfield at the catalog layer too, not merely at the contract layer.)

### 3.5.3 The onboarding, and the one scoping decision
Register, for the pilot: system **Odoo ERP** (provider Odoo S.A.) → version **17.0** →
module(s) **Accounting / Sales / Purchase** → the **objects the reader actually binds**
(`account.move`, `account.move.line`, `account.payment`, `account.bank.statement.line`,
`res.partner`, `account.account`) → their fields.

**Scoping decision for the reviewer — the deliberate contrast with SAP:** SAP's catalog was
bulk-imported exhaustively (14.5k objects). The Odoo pilot should register **only the
objects the world engine emits and the reader admits** — the ~6 finance entities above, not
the whole Odoo ORM. Rationale: the catalog is a governed registration surface
(`verification_status`), and registering thousands of never-read objects is unverifiable
noise. Register what is realized; grow the catalog as metrics demand more objects. (This is
the same "supply follows demand" discipline the world engine's Tier-2 deferrals follow.)

### 3.5.4 Relationship to the D526 docket
The source-system **docket is the human-readable projection** of this catalog registration
(D526: docket = projection, registry = authority). The docket's four-quadrant research
(Platform/Tenant × Legal/Technical) documents *what a real Odoo tenant connection requires*;
the catalog rows are the *governed substrate* the docket points at. Onboarding the catalog
is where the docket's "registered" material becomes platform truth. **Gate:** catalog
registration is Tier-5 metadata, not runtime data — but it is still a governed authoring
act, and (per §0) building it is part of the pilot execution lane, distinct from the
SAP-ECC audit lane.

---

## 4. Odoo Reader Flavor + executor + ORM domain serializer (TSK-82a767)

Designed against the current bc-core reader architecture (mapped 2026-07-30, cited).
**Repair location A** (source reality / admission boundary). Odoo is greenfield in code —
readers live under `src/registry/readers/` + `src/boundary/reader-runtime/` (there is no
`src/readers/`); no Odoo/JSON-RPC reader exists. But the pattern is proven: **SAP OData
executors already exist** (`src/boundary/reader-runtime/executors/sap-odata-v4.executor.ts`,
`sap-odata-v2`, plus `sdg-odata`, `sfdc-rest`), so this is a new sibling, not a new
subsystem.

### 4.1 Registration — three-level model (all in the `runtime` PG schema)
`Reader` → `Reader Flavor` → `Reader Binding`, per `src/database/schema/runtime/reader.ts`.
- **Reader** (`runtime.reader`, reader.ts:28-58): one `odoo-erp-reader` (domain ingress,
  `sourceSystemName='odoo'`, `functionCode='finance'`), modeled on the existing
  `exchange-rate-reader` (seed-registry-full.ts:550-566).
- **Reader Flavor** (`runtime.reader_flavor`, reader.ts:62-103): identity =
  `(readerId, sourceSystemName='odoo', scenarioCode)`; carries `connectorId`,
  `connectionId` (soft cross-DB ref, no FK), `configJson`, `statusCode`. The active-scenario
  partial unique index (reader.ts:99-101) enforces one ACTIVE flavor per scenario.
- **Reader Binding** + **Reader Observation Binding** (reader.ts:107-155, DEC-17112b):
  one binding per Odoo source entity (`account.move`, `account.move.line`,
  `account.payment`, `account.bank.statement.line`, `res.partner`, `account.account`) to
  its SC + per-entity OC. **Prerequisite: each of these entities must already be a
  registered Source Catalog object (§3.5).**
- Authored via `src/registry/readers/reader-authoring.service.ts` + DTOs
  (`create-reader-flavor.dto.ts`, `create-reader-binding.dto.ts`). **No schema change** to
  register the flavor — it's data.

### 4.2 Executor — new `odoo-jsonrpc.executor.ts` implementing `ReaderExecutor`
Interface `src/boundary/reader-runtime/reader-executor.interface.ts:23-54`: single
`execute(params) → { observations: RunObservationItem[], metadata }`. Design anchors from
the contract (interface.ts:16-17,40):
- **Stateless & deterministic**; **receives pre-resolved credentials** via `params.auth`
  — the executor NEVER resolves its own credentials (matches every existing executor).
- Registered in `src/boundary/boundary.module.ts` `onModuleInit` under a protocol key
  (e.g. `'OdooJsonRpcProtocolReader'`, D084), matched by `connector.executorClass`; the
  runtime coordinator resolves the executor by `connector.executorClass ?? flavor.name`
  (reader-runtime.service.ts:126-134).
- Emits `RunObservationItem { sourceSystemName, sourceEntityName, sourceKey, observedAt,
  observedPayloadJson, provenanceJson }` — `sourceKey` = Odoo `model,id`; `provenanceJson.
  source='odoo-jsonrpc'`. Exemplar: sap-odata-v4.executor.ts:157-189.

### 4.3 ORM domain serializer — the NET-NEW core (the actual TSK-82a767 gap)
**Confirmed design gap:** bc-core has **no generic domain/predicate serializer.** Existing
executors filter date-range-only (`buildDateFilter`, sap-odata-v4:340-352) or by config
lists (OER/FRED). Expressing "admit `account.move` where `state=posted` and company X over
window W" is net-new. Design:
- `flavorConfig` (per entity) = `{ model, domain: [[field, op, val], …], fields: [...],
  order }` — the flavor row's `configJson` is the free-form home (connector.ts pattern).
- A serializer translates the Odoo domain list → JSON-RPC `execute_kw(model,'search_read',
  [domain], {fields, offset, limit, order})`, paginating on `offset/limit` (the Odoo analog
  of SAP's `$top/$skip`).
- **Reference implementation exists**: the dry-run's `bc-sdg/tools/mfg-in-odoo/seed.py`
  `Odoo.kw()` already does exactly this domain→`search_read` translation (incl. the nested-
  list flattening trap). The production serializer is a hardened port of that, living in
  the executor.
- The window `[startPeriod,endPeriod]` injects as a `date` domain clause; the runtime
  already feeds per-entity watermark starts (reader-runtime.service.ts:182-187) for
  incremental/backfill.

### 4.4 Admission landing (SO)
Executor output → `AdmissionBatchService.admitReaderBatch` (batched 5000,
reader-runtime.service.ts:249-259) → `AdmissionService.admitSourceObject`
(admission.service.ts:57-100): AC-envelope validation → **`progression.admission`**
(authoritative, D369, progression.ts:44-73) + typed **`fact.so_<sc>_v<M>_<m>_<p>`** row
(fact-table-name.ts). The SO is synthesized in-memory (observation.service.ts:137-152); no
separate SO persistence (D369 M4.2e retired it).

### 4.5 Invariant V — reads must not trigger evaluation
The executor path is read → admit → fact-write only; canonical evaluation is a separate
downstream boundary the reader never calls (confirmed: admission emits an
`admission_run_completed` event, reader-runtime.service.ts:264-308; evaluation is not in
the reader call stack). **Design rule: the Odoo executor issues only `search_read` — never
a write, never a method that mutates Odoo or triggers platform evaluation.**

### 4.6 Connection & credentials — one design GAP to flag
Per-tenant connection: `runtime.connection` (tenantId, `endpointUri`, connection.ts:24-63)
+ `runtime.connection_config.authenticationJson`. Credentials resolve via
`CredentialResolverService` (credential-resolver.service.ts) — secrets **never** in the DB,
only a `credentialRef` (`env:VAR`). **GAPS for Odoo:**
- Odoo JSON-RPC auth is `db + login + password` (or API key) returning a **uid/session** —
  not one of the current strategies (`none`/`api_key`/`basic`/`oauth2_password`,
  :82-101). **New strategy needed**, and `ResolvedCredentials` (:11-35) needs a small
  extension to carry `uid`/`session`.
- **`ssm:` (managed secrets) is stubbed, not implemented** (:145-151). If the pilot needs
  managed Odoo secrets rather than env vars, that's a prerequisite, not a nice-to-have.

### 4.7 ⚠ DOCTRINE CORRECTION — "fail closed without a legal entity" is NOT enforced
My prior docs (README doctrine constraints, RUNBOOK, PLAN-v2) asserted "canonical
resolution fails closed without a company_id on the object." **The code says otherwise:**
`canonical-resolution.service.ts pickLegalEntity()` (:1140-1148) tries
`['legal_entity_code','company_code']` and **falls back to `'*'`** — it does NOT reject on a
missing company. Fail-closed only bites transitively, at fiscal-calendar resolution
(`enrichFiscalPeriod` :1102-1138 → `NoFiscalCalendarConfigException`) or on a missing/invalid
`posting_date` (:1113-1121). So:
- Putting `company_id` on every Odoo document (which the world engine does) remains correct
  and sufficient — but the *justification* was wrong.
- **Design decision for the reviewer:** if the pilot requires a hard "no company ⇒ reject"
  rule, that is a **new enforcement point** (candidate: AC validation, or `pickLegalEntity`)
  — it does not exist today. Otherwise we rely on the fiscal-calendar gate, which means
  every legal entity must have a calendar and there must be no permissive `'*'` calendar.
- Follow-up: correct the claim in README/RUNBOOK/PLAN (tracked; the world engine behavior
  is unchanged, only the stated reason).

---

## 5. Contract-chain SHAPE over Odoo (DESIGN ONLY — Track-C-gated)

> ⛔ **BUILD GATE:** everything in this section is design for review. Authoring or
> activating any SC/AC/OC/CC/MC over Odoo is **held until Track C** (D524). Nothing here
> authorizes a `publishChain` call or a contract write.

Designed against the current authoring surface (mapped 2026-07-30, cited). **Repair
locations B (contract semantics) + C (binding).** Confirmed **greenfield**: every seeded
contract fixture and OC/CC name in bc-core is SAP (ANLA/BSEG/ACDOCA…); Odoo exists only in
the source *catalog* (`seed-v2/data/source/systems.csv:70-71` `odoo-erp`/`odoo-crm`,
`planned`; 210 catalog field rows). No Odoo contract, binding, or fixture exists.

### 5.1 The minimum chain — 5 authored artifacts → snapshot
Per the current families (`src/registry/contracts/contract-families.ts:82-128`):

| # | Artifact | Declares | Authoring surface | Authored by publishChain? |
|---|---|---|---|---|
| 0 | **Source Catalog registration** (§3.5) | system→version→module→object→field exist | `source.*` schema | **No — prerequisite, see §3.5** |
| 1 | **Source Contract** | raw Odoo object schema (e.g. `account.move`) — references the catalog object | `contract.source_contract[_version]` (seed shape `seed/ar-source.json`) | **No — hand-authored/seeded** |
| 2 | **Admission Contract** | field acceptance + `identity_semantics.primary_key` + admissibility | `contract.admission_contract[_version]` (`seed/ar-admission.json`) → `admission.service.ts` → `progression.admission` + `fact.so_*` | **No — hand-authored/seeded** |
| 3 | **Observation Contract v2** | `field_mappings[]` (source_field→`business_concept_id`), `join_semantics[]`, `source_references[]` | `contract.observation_contract_version` | **Yes** (`buildOcV2Body`) |
| 4 | **Canonical Contract v2** | `grain[]`, `field_selection[]` (concept→canonical_field), `derivations[]`, `posting_date_field` | `contract.canonical_contract_version`; runtime SO→CO `CcV2CanonicalResolverService` → `progression.canonical_evaluation` + `fact.co_*` | **Yes** (`buildCcV2Body`) |
| 5 | **Metric Contract (MCF)** | formula AST + `metric_variable_binding` (variable→**concept**) | `mcf.metric_contract_version` + `mcf.metric_variable_binding` | **No — separate MCF authoring** |

→ **Metric snapshot** (output, not authored): `GovernedMetricEvaluationService` opens
`progression.metric_run`, gates over CanonicalObjects, writes `fact.ms_*` in one txn.

**Key design fact:** `publishChain` (`POST /api/contracts/chains`, PlatformOnly, D511)
authors **only #3–#4 in one call** and takes `sourceVersionId`/`sc_version_id`/`ac_version_id`
as **manual inputs** (`publish-chain.dto.ts:9-11,57-58` — no table→active-version
auto-resolution). So an Odoo onboarding is: seed SC+AC (steps 1–2) → `publishChain` (3–4) →
author MC (5). There is **no one-call SC→MC driver**; that's the honest shape, three
authoring acts, and it respects D268 (one chain per call, no bulk generation).

### 5.2 The portability test — CONFIRMED by the binding mechanism
D538 requires the *same* MC to onboard a second source (BC) with **no MC edits**. The map
confirms the mechanism, cited: `mcf.metric_variable_binding` binds each variable to a
**`bound_business_concept_id`** (a BCF concept) — **never a source column**; the
`mvb_role_target_chk` CHECK enforces it (`metric-variable-binding.ts:74`). At runtime
`metric-variable-resolver.ts` (header :19-21: "a metric declares SEMANTIC inputs (concepts),
not column names… CO column names are NEVER hardcoded") joins the binding's concept id to
the active CC's `field_selection` concept ids. So substituting Odoo→BC is done **entirely
in the OC/CC layer**: BC's OC-v2 + CC-v2 declare the *same* concepts on their canonical
fields, and `resolveVariables` re-derives the mapping by concept identity. **The MC does
not change.** This is the portability proof path, and it's real today — no new mechanism
needed.

### 5.3 Worked shape (illustrative — NOT an authored spec): "Total Receivables"
- **SC** `sc__odoo__account_move` — jsonschema of the `account.move` fields the world emits
  (name, move_type, state, date, invoice_date, invoice_date_due, partner_id, company_id,
  amount_total, currency_id, amount_total_signed…).
- **AC** `ac__odoo__account_move` — `primary_key = (company_id, name)`; admits
  `state=posted`, `move_type in (out_invoice,out_refund)`.
- **OC-v2** — `field_mappings` map `partner_id→Customer`, `amount_residual→Open Amount`,
  `date→Posting Date`, `company_id→Legal Entity` (concepts already declared by SAP's AR
  chain, so they exist in `concept_registry`).
- **CC-v2** — `grain[]` keyed to the receivable identity; `field_selection` binds those
  concepts to canonical fields; `posting_date_field=date`.
- **MC** — variable `receivable_open` bound to the *Open Amount* concept; formula
  `sum(receivable_open)` partitioned by the D495 aggregation-currency policy. **The same MC
  is what BC would reuse.**

### 5.4 ⚠ Runtime gap the reviewer must weigh
Two CC-v2 derivations **throw as not-yet-wired** at runtime (`ccv2-canonical-resolver.
service.ts:1019-1027`): **`classify_by_binding`** (tenant-scoped GL-account classification,
D515/D498) and **`fiscal_period_end_date`** (fiscal-calendar wiring). Consequence: a
**GL-account-balance metric that needs tenant-bound account classification cannot be
realized today** — it would hit an unwired derivation. Receivables/payables totals (5.3)
do **not** need it and are clear. **Design decision:** sequence Odoo finance metrics so the
classification-free ones (AR/AP totals, aging by date) come first; GL-classification metrics
wait on D515/D498 runtime wiring (separate work, flag as a dependency, not pilot-blocking
if we sequence around it).

---

## 6. Cross-system projection order (READY)

The shared registry (`master.json`) is the join-key spine (D538). Projection order and
per-system chronology:

1. **Odoo is the base world** (built here). Its `res.partner.ref` / `default_code` carry
   the registry IDs.
2. **BC second** (D524: BC first for *execution confidence*, Odoo for *platform
   confidence* — this package realizes Odoo first because its dry-run is done; BC
   realization is the zero-MC-edit portability proof).
3. **SFDC third** (the CRM plane; opportunities/accounts keyed to the same customers).
4. The **same customer** appears in Odoo (buyer), BC (subsidiary ledger), SFDC (account)
   under one registry ID — this is what lets a cross-system metric resolve one entity.
   Chronology replays per system from the registry `active_from`/`churned_from`.

**Open for reviewer:** does projecting the *same* correlated world into three systems risk
the audit-independence boundary (D524)? Position: no — projection is execution-side; the
metric audit stays on SAP ECC. Confirm.

---

## 7. Open shortcomings & accepted limits

(From the dry-run ledger — TSK-2a7357 + code annotations.)
- CRM stage-velocity not demonstrable on a back-seed (Odoo owns the timestamps) — living
  window only. **Accepted limit, stated.**
- Inventory: 0 stock.quant (consumable products) — real inventory/valuation is
  rebuild-native and lands with the MES/QA wave. **Deferred, demand-gated.**
- a2 duplicate-vendor-bill anomaly generator returns silently — **open bug.**
- Statement-line matching ~85%; suspense clears with it — **prove at gate.**
- Employee master / per-employee payroll — GL payroll is real; per-employee waits for HR
  wave (registry-first when it comes). **Deferred, demand-gated.**
- Multi-currency is the company's own rate table (correct, D539); no group consolidation
  entities yet. **Scoped out.**

## 8. Review protocol & disposition ledger

- Package committed to bc-docs on a review branch, SHA-pinned; the SHA is what goes to
  Codex (matches the D526 docket exchange pattern).
- Codex returns findings classified (as the docket enrichment did): VERIFIED / QUALIFIED /
  CONTRADICTED / NOT_PROVEN, confidence 1–5, per section.
- Disposition ledger (below) tracks each finding → response → resolution, both repos.
- Package stays "structurally reviewed; substantively pending" until each enforced §
  clears. Building the clean world (§3) may proceed on operator sign-off; the reader (§4)
  after its findings clear; the chain (§5) only at Track C.

| Finding | § | Codex verdict | Response | Status |
|---|---|---|---|---|
| _(populated on review)_ | | | | |

---

## 9. Phased execution & the Track-C boundary

The sections above are the full design. **Executing them as one program would be
over-ambitious** (operator observation, 2026-07-30) — so execution is **five bounded
phases**, each with independent value and a clear exit gate. Critically, the Track-C hold
(D524) falls *between* phases, not through them: **Phases 1–2 (and the code half of 3) sit
entirely outside the hold and can begin on operator sign-off**; the contract phases are
gated.

| Phase | Scope | Repair loc | Track-C? | Exit gate | Status |
|---|---|---|---|---|---|
| **1 · Odoo source world** | Chronological rebuild (PLAN-v2): company creation + 5-FY forward loop; modules `account,l10n_in,crm,sale_management,stock,purchase`; full realism + anomalies | A (source data) | **OUTSIDE** | gate battery green + AMI + cost-managed | **dry-run PROVEN**; phase = clean rebuild + productionize |
| **2 · Source Catalog registration** | Register Odoo ERP system→version→module→the ~6 finance objects→fields (§3.5); docket (D526) projects | A (Tier-5 metadata) | **OUTSIDE** | objects `approved`; catalog = docket authority | greenfield, small |
| **3 · Reader Flavor + serializer** | `odoo-jsonrpc` executor + ORM domain serializer + credential strategy (§4). **3a code** buildable now (read-only serializer proof vs live instance); **3b E2E admission** needs Phase-4 SC/AC | A/D (code) | 3a OUTSIDE · 3b gated | 3a: serializer reads live Odoo; 3b: data lands in `progression.admission` + `fact.so_*` | **the pilot blocker, TSK-82a767** |
| **4 · Contract chain + first metric** | SC→AC (hand) → `publishChain` OC+CC → MC → snapshot (§5), for ONE metric (Total Receivables, §5.3) | B/C/D | ⛔ **GATED** | the metric computes over Odoo E2E and **matches Odoo's own report** | greenfield authoring |
| **5 · Cross-system projection** | BC then SFDC via the shared registry (§6); the **zero-MC-edit portability proof** (same MC, second source) | C | GATED | same metric resolves across systems | later |

**Phase 1 module scope (your "all modules" question):** Phase 1 installs the modules the
*realized* finance-metric surface needs — the six above. The **Tier-2 modules (`hr` for
payroll headcount, `mrp` for MES, OCA helpdesk for ITSM) are demand-gated sub-phases**, each
triggered when a metric in that function reaches `active` (TSK-2a7357) — NOT bundled into
Phase 1. This keeps Phase 1 bounded and honest (we don't install a module no metric reads).
If a richer *demo* wants those modules present earlier, they can be installed with
finance-only data as a Phase-1 option — flag for operator call.

**Why this answers "too ambitious":** the program is five small phases, the first three are
unblocked today, and the single riskiest new-code item (the reader, Phase 3) is isolated
with a read-only proof step before anything depends on it. The Track-C milestone is a single
crisp event — Phase 4, one metric computing correctly over Odoo — not a big-bang cutover.

**Recommended immediate sequence (no hold touched):** Phase 1 clean rebuild → Phase 2
catalog registration → Phase 3a serializer proof. That produces a real, registered,
platform-observable Odoo source — everything up to the Track-C line — as the reviewable
milestone before any contract is authored.
