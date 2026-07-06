---
uid: STUDY-metric-eval-boundary-2026-07-01
title: "Metric Evaluation Boundary — Governance-Parity Study & Spec"
description: "First-principles metric algebra + as-built coherence map + 5-dimension engine audit + the closure rule + the target governed metric-evaluation boundary. Establishes that the evaluation boundary is essentially unbuilt for the 51 governed (mcf.*) metrics and must be built to BCF/MCF-grade governance from the algebra, SDG-blind. Spawns the ADR build sequence."
status: drafting
authority: study
date: 2026-07-01
project: bc-core
domain: metrics
subdomain: metric-runtime
governing_sources:
  - The Invariants — I (meaning once), IV (explicit references), V (non-replayable), VI (evidence emitted)
  - The Evaluation Boundaries — the metric boundary
  - The Object Model — the Metric Snapshot
  - The Governed Selection (DEC-c4c742) + The General Metric Runtime (DEC-483f1e)
---

# Metric Evaluation Boundary — Governance-Parity Study & Spec

## 0. Why this document exists

The metric **authoring** layer (BCF + MCF) matured into a governed framework: closed grammars, publication-eligibility gates (PE-MC), versioning + supersession, immutability, evidence, ADR + DBCP discipline. It governs **51 active metric contracts** (`mcf.metric_contract_version`, 52 versions / 51 active, verified 2026-07-01).

The metric **evaluation** layer underneath it grew organically, one metric-shape at a time (`as_of`, derived canonical fields, reference grouping, cross-entity, composite `metric_input`). Each capability was added to unblock a specific metric, never checked against a complete map of *what a metric mathematically is*. This study builds that map (the **metric algebra**), places the as-built engine and store on it (the **coherence map**), audits the engine along five governance dimensions, and states the **target**: a metric-evaluation boundary at the same governance bar as BCF/MCF — designed from the algebra, not retrofitted.

**Headline finding.** The evaluation boundary is essentially **unbuilt** for the governed metrics. Two independently-verified facts — kept deliberately separate — establish this:

- *Code structure:* the engine that matches the governed metrics (`governed-metric-runtime`) is test-only — `evaluateGovernedMetric` has no production callers. The production-wired engine (legacy `MetricEvaluationEngine`) reads the envelope substrate `contract.metric_contract_version`.
- *Live data (bc_platform_dev + tbc_pilot1_dev, 2026-07-01 — full transcript in §10):* `contract.metric_contract_version` = **0 rows** (the wired engine has nothing to read); all 52 governed metric versions (51 active, 1 review) are in `mcf.*`; and the sole live tenant `tbc_pilot1_dev` has **no `fact.ms_*` tables provisioned** and `progression.metric_evaluation` = **0 rows**.

Together: **no live metric is currently evaluated or persisted** — the boundary is genuinely greenfield. Good news for coherence: we build it correctly from first principles rather than retrofit a load-bearing engine. (The stale DDL header comment in `04-mcf-substrate.sql` citing 1,022 MCV rows is superseded by the live count of 52.)

## 1. Governing principle: the runtime is SDG-blind

The object progression — `Source State → Reader → Source Object → Canonical Evaluation → Canonical Object → Metric Evaluation → Metric Snapshot → Action Object` — is a **real, source-agnostic runtime**. The Synthetic Data Generator (SDG) is a **source system hidden behind the Reader boundary**. Nothing downstream of the Reader knows or cares whether the source is synthetic or a real SAP system.

Consequences that bind this design:

1. There is **no "SDG phase" of the runtime.** The evaluation boundary is a real runtime component that is simply unbuilt. Prior "SDG-phase I/O" language was a mislabel and is retired.
2. **SDG conforms to the runtime's contracts** (Source Contracts / Reader expectations), never the reverse. The engine, the evidence, and the store carry **no SDG awareness**.
3. Therefore the evaluation boundary is designed to Foundation + the algebra, and validated the same way whether the ultimate source is SDG or production.

## 2. The metric algebra — what a metric *is*

A metric is a function producing a **recorded measurement**. It factors into four orthogonal axes. Every metric shape the platform will ever need is a point in this space; every mechanism must map to exactly one axis.

### Axis 1 — Selection (which values enter)
- **Temporal frame** — the fundamental split:
  - **Flow** — values whose *event* falls in an interval; integrate over `[t0, t1]`. Sub-forms: bounded period, trailing window, cumulative-to-date.
  - **Stock / state** — the value that *exists* at an instant P, net of all events ≤ P. Sub-forms: as-of balance (open-at-P), point-in-time.
  - These are mathematically different operations (integral over interval vs state at instant). **A single metric may need different frames for different inputs** — DSO is a stock numerator over a flow denominator. This is the load-bearing structural fact.
- **Source** — which canonical-object population (one entity; or several joined by a stamped reference — cross-entity).
- **Filter** — predicates narrowing the population.
- **Partition / grain** — computed for the whole population or *per* a key (per customer, per period). Orthogonal: any selection can be partitioned.

### Axis 2 — Aggregation (fold a set to value(s))
`sum / count / distinct-count / min / max / avg / median / percentile` today; `weighted-avg, stddev, first/last` foreseeable. A fold over the selected set → one value per partition.

### Axis 3 — Combination (algebra over aggregates)
Arithmetic (ratio, difference, product), conditional (`case`), and **composition over other metrics** (a DAG — DSO = AR-metric ÷ revenue-metric × days). Combination and composition are the same algebra at two levels (intra-metric formula; inter-metric DAG).

### Axis 4 — Result frame (what a Metric Snapshot *is*)
- **Cardinality** — one value (scalar) or many (one per partition group).
- **Time-stamp** — as-of an instant (stock) vs for a period (flow), **plus** knowledge-time (the evaluation instant).
- **Grain** — the dimensional key(s) the value is reported at.
- **Units / representation** — amount, count, ratio, days, percentage.
- **Lineage** — explicit references to the inputs that produced it (which COs; which upstream snapshots), varying by selection + composition.

### The coherence principle
Each axis has **exactly one** expression mechanism: time declared one way (per input, since inputs can legitimately differ), grain one way, combination/composition one algebra, and **one Metric Snapshot model** spanning every cardinality / frame / lineage combination.

## 3. As-built coherence map (engine + store)

### 3.1 The engine (two paths)
| Path | Substrate | Selection | Wired? |
|---|---|---|---|
| `governed-metric-runtime` (`src/boundary/`, DEC-483f1e) — `gate-spec-from-substrate → select-by-gate → partition(grain∪grouping) → FormulaExecutionEngine → optional top-N` | `mcf.*` (the 51 live metrics) | real temporal gates + governed selection; emits `GateSelection` | **No** — `evaluateGovernedMetric` has no production caller; no store wiring. Test-only. |
| legacy `MetricEvaluationEngine` (`metric.service`, envelope `contract_json`) | `contract.metric_contract_version` (**0 rows, empty**) | none (grain-grouping only) | Yes — `POST /t/metric-evaluation` + the `fact.ms_*` write path |

The aggregation algebra (shared `FormulaExecutionEngine`, `src/registry/mcf/`) is **mature and coherent**: 9 AST node kinds; 8 aggregates incl. median/percentile; typed arithmetic (`date−date→duration`); window ops `lag/lead/moving_avg`; 11 conjunctive filter operators. This part is sound and composes.

**Temporal shapes:** of 7 declared, only `as_of` and `trailing_window`/`rolling_window` actually select (`select-by-gate.ts:206-215`); `period_aggregate`, `cumulative_to_date`, `point_in_time`, `instantaneous` fall to identity (`selective:false`, "predicate pending"). The live distribution (`mcf.metric_contract`, 2026-07-01, §10) is stark: **`period_aggregate` = 37 of 52** metrics, **`as_of` = 15**, and the other five shapes = **0**. So the *majority* shape (37/52) does **no** temporal selection — it relies entirely on grain-grouping to bucket by period, with no gate predicate.

**Composite (`metric_input`):** schema-defined + gated (PE-MC-14 alignment, PE-MC-15 acyclicity) but the runtime **never resolves upstream snapshots** — composite metrics (DSO) are admitted, eligible, and **not evaluable**.

### 3.2 The store (sound design; not yet provisioned or transactional)
`fact.*` is the uniform store for the whole progression, generated per activated contract by a pure deterministic DDL generator (`ddl-generator.service.ts:23-26`):
```
fact.so_<sc>_v<ver>   Source Object      fact.co_<cc>_v<ver>   Canonical Object
fact.ms_<mc>_v<ver>   Metric Snapshot    fact.ao_<ic>_v<ver>   Action Object
```
`fact.ms_*` **is** the model for Metric Snapshots (grain columns + a `value`), with `progression.metric_evaluation` (lineage + status + `evaluated_at`) and `progression.metric_snapshot_index`. The store **design** is sound (pure, deterministic generator), but "design" is not "readiness" — two gaps separate them:

1. **Not provisioned in the live tenant.** `fact.ms_*` tables are generated on contract *activation*, which has not run for `tbc_pilot1_dev` — it currently holds **no** `fact.ms_*` / `fact.co_*` / `fact.so_*` tables at all (§10). So the store is a schema *generator* that is proven but unexercised for the pilot.
2. **The write act is not transactional** — see §4/§5: `fact.ms_*` + `snapshot_index` are awaited, but `progression.metric_evaluation` is fire-and-forget, so a snapshot can persist with no evaluation record.

A separate open question is *result-frame semantics*: a snapshot row does not distinguish **stock-as-of-P vs flow-over-period** as a first-class attribute (period is smuggled in as a grain key), and lineage records canonical-object refs only (no upstream-metric refs for composites).

## 4. Five-dimension engine audit (verdicts)

| # | Dimension | Verdict | Evidence |
|---|---|---|---|
| 1 | Entry point / wiring | **Split & unwired** | Governed engine test-only; wired engine reads empty substrate; nothing evaluated or persisted. |
| 2 | Governed enough | **Partial** | Pure/deterministic + Inv V (new id per act) + closed-enum gate shapes at runtime. But **no version-gating**, **no governance-state on the eval act**; operative path does no governed selection. |
| 3 | Error / failure modes | **Coherent, holey** | Good fail-closed taxonomy (gate params, unknown AST, filter clauses) + per-partition isolation (`rejectedGroups`). **Fail-open holes in the governed AST engine** (`formula-execution.engine.ts:430`): divide-by-zero → silent null; missing filter-input → row silently dropped; all-null aggregate → silent. NB the *legacy* engine fails **closed** on divide-by-zero (`metric-evaluation-engine.service.ts:613`, returns `Division by zero`) — but it is the path being retired, so the hole lives in the engine we are **promoting**. |
| 4 | Evidence / lineage (Inv VI) | **Not met** | `GateSelection` (resolved set + predicate) computed synchronously but **never persisted** (unwired); legacy `input_references_json` is **fire-and-forget**; no composite lineage; no filter/selection evidence. Evidence is *produced*, not *emitted-and-preserved*. |
| 5 | Table writes | **Partial / orphan-prone** | `fact.ms_*` + `snapshot_index` sync/awaited/atomic; but `progression.metric_evaluation` fire-and-forget → a fact row can orphan with no evaluation record. Only the legacy engine triggers writes. |

## 5. The closure rule (governing principle going forward)

> **No metric shape is admissible until the grammar can declare it, the publication gates can validate it, the engine can evaluate it, and the store can persist it — all four expressing the same thing.**

The incoherence this study found is **vertical layer-drift**, not horizontal scatter: today *grammar admits > gates validate > engine evaluates > store persists*, each cut at a different line (composite + 4 temporal shapes are admitted and gated but not evaluated). The closure rule forbids that drift as a standing discipline — the same role the contract grammar plays for BCF/MCF.

## 6. Target: the governed metric-evaluation boundary

Design goals (all SDG-blind; the engine reads COs and never knows their provenance):

1. **One wired engine.** Promote `governed-metric-runtime` to the production evaluation act over `mcf.*`; retire the empty envelope path (`contract.metric_contract_version` + legacy `MetricEvaluationEngine`).
2. **One temporal model** spanning the metric gate **and** per-input frames — uniformly for primary *and* composite inputs (subsumes `snapshot_selection_rule`; makes DSO's stock-numerator / flow-denominator expressible). Implement the four "predicate pending" shapes (`period_aggregate` etc.) so the gate actually selects.
3. **Composite execution.** Resolve `metric_input` upstream snapshots in the runtime (the DAG), so an admitted composite is an evaluable composite — enforced by the closure rule.
4. **A defined Evidence & Lineage object (Inv VI)** emitted *synchronously at the evaluation act* and *persisted*: the resolved input set (COs) per snapshot, the selection predicate, the rejections, and — for composites — upstream-snapshot refs. Result-frame carries the stock-vs-flow / as-of-vs-period stamp as a first-class attribute.
5. **Closed error taxonomy, fail-closed by default.** Replace the fail-open holes (divide-by-zero, missing filter-input, all-null) with typed, recorded rejections; keep per-partition isolation.
6. **A transactional evaluation act.** Replace the fire-and-forget `progression.metric_evaluation` write with an all-or-nothing act across evaluation record + snapshot rows + evidence; deterministic + non-replayable (Inv V).
7. **Version-gating.** Evaluation semantics keyed to the contract grammar version.

### 6.8 Input admissibility, deferral & the replay boundary (Foundation-grounded)
A scheduled/triggered evaluation is a **readiness check, not a compute mandate** (refines §8.2). This resolves a common confusion — *"Foundation says no re-evaluation."* It does not. **Invariant V forbids replay, not re-evaluation:** *"Subsequent evaluations against the same inputs are permitted, but they are distinct acts… They produce distinct object versions with their own Evidence and Lineage."* The forbidden thing is re-running a past act to recreate an *identical* historical outcome. A new act at a new knowledge-time producing a new superseding version is legal — and is exactly how both first-evaluation-on-arrival and restatement (§8.4) work. The one named trap: a late evaluation must be stamped with its **real** knowledge-time, never *"treated as equivalent to the original evaluation act"* (Invariant V, disallowed).

**Absent / inaccessible inputs → do not evaluate.** Two invariants force this independently:
- **Invariant II (ordering):** a Metric Snapshot *"derives from one or more Canonical Object versions… No object exists without its ordered predecessors."* With required COs absent, a snapshot would have **no predecessor** — a II violation, not a degraded result.
- **Invariant VI (evidence):** *"if no Evidence exists for an evaluation, the platform treats that evaluation as not having occurred,"* and it is disallowed to treat an absent record *"as a probably-successful evaluation."* A period with **no snapshot is a legitimate, observable state** — never fill it with a fabricated zero or placeholder.

**Two cases, treated differently:**
- **Source unreachable / zero required COs** → **defer** (no basis to evaluate). Evaluation occurs later, when the COs arrive, as a normal *first* act for that period.
- **Source observed, COs present (even if real-world-partial)** → evaluate **as-of the knowledge-time**, honestly labeled. Not "absent" — the true state as known now; later arrivals → a new superseding version.

**What a deferral records:** an *operational* run outcome on `progression.metric_run` (`status_code = deferred_inputs_unavailable`) with the missing-input references — **not** a Metric Snapshot and **not** synthesized evidence-of-evaluation, so it stays clear of the Invariant VI trap. "Why is there no Q2 snapshot?" then has an auditable answer: *inputs were not admissible as of the check at time T*.

**Design consequence:** the boundary needs an **input-admissibility gate** — the metric analogue of the source Admission Contract — deciding *evaluate-now vs defer* at each triggered point. The minimal check (required COs present + source observed + the `deferred_inputs_unavailable` run-state) lands in **ADR #1**; the fuller policy (period-closure / fiscal-calendar interaction, what "required" means per metric) is **ADR #2**.

## 7. Build sequence (ADRs)

The sequence splits into two clusters: **semantic correctness** (what a snapshot means) and **operational governance** (how the shared runtime is run, changed, and survives failure — from the operator design review captured in §§11–13). ADR #1 is filed; the rest are proposed scope.

**Cluster A — semantic correctness**
1. **Evaluation-boundary unification & wiring** — promote the governed runtime, retire the envelope path, the transactional idempotent act, the run object, the fail-closed deferral state. **Filed: DEC-5ea578 (D472), `proposed`.** (Closes Q1/Q5.)
2. **The metric temporal model + input admissibility** — one per-input temporal-frame grammar (flow/stock + sub-shapes), the four missing shape predicates, primary+composite uniformity, the bitemporal event-time column, and the period-closure / required-input policy behind the §6.8 admissibility gate. (Closes Q2 temporal + the DSO grammar gap.)
3. **Composite (metric DAG) execution** — resolve `metric_input` upstream snapshots at runtime. (Closes the Q1 composite gap.)
4. **Metric Snapshot evidence & lineage object (Inv VI) + serving layer** — the evidence object in the live `evidence` schema, the result-frame stock/flow stamp, the `metric_snapshot_index` read-model, and the tenant-facing metric read API (§14). (Closes Q4 + the store result-frame question.)
5. **Evaluation error taxonomy + runtime rule book** — fail-closed typed error union, version-gating, and the machine-checkable evaluation invariants (§11.3). (Closes Q2/Q3.)

**Cluster B — operational governance**
6. **Engine lifecycle & change-safety** — golden/characterization tests, shadow evaluation, `engine_version` stamping, progressive rollout, non-destructive rollback, hotfix fast-lane (§11.1).
7. **Observability & SLOs** — the four-signal telemetry + freshness / deferral / restatement SLIs (§11.2).
8. **Evaluation Orchestrator** — dependency-aware triggering + completeness, composing #2's closure signal with #3's DAG into the control plane (§13).

Each ADR closes under the closure rule (§5) and is validated SDG-blind (§1). DSO / turnover / CEI and the trailing-window family drop out as instances of the closed model — not as further bolt-ons.

## 8. NFRs, multi-tenancy & AWS deployment topology

**Decision (2026-07-01, amended):** build the evaluation boundary **local-first and deployment-portable** — proven end-to-end on local Postgres against `tbc_pilot1_dev`, then deployed to AWS by **adapter-swap + IaC, not rewrite**. This supersedes an initial "AWS-native from start" framing: local-first is the *honest* form of the §8.7 principle (*the AWS scale-out is a deployment change, not an engine rewrite*) and preserves the cost + iteration-speed advantage local development has given the platform. The condition that makes it safe is **§8.9** (portable seams + substrate parity). The distribution-shaping NFRs below are still structural, designed in from day one, and **environment-agnostic** — they hold identically local or cloud.

### 8.1 The multi-tenant spine
The metric **contract is a platform singleton** (authored/versioned/governed once in `mcf.*`, D164); **evaluation is a per-tenant fan-out** (same shared engine, each tenant's COs); the **snapshot + evidence are per-tenant** (`tbc_{slug}_dev.fact.ms_*` / `progression.*`, structurally isolated). Isolation is **connection-routed to the tenant DB, never a `tenant_id` filter in shared tables.** The corollary is the governance mandate: a shared engine executed against every tenant is **shared blast-radius** — one determinism bug is wrong numbers for all tenants at once. That is *why* the engine needs BCF/MCF-grade governance, not aesthetics.

### 8.2 Foundation gives the trigger model
"Reads do not trigger evaluation" (the-evaluation-boundaries.md) splits the SLA cleanly: **reads are pure store-lookups** of pre-computed snapshots (fast); **evaluation is always ahead-of-read**, driven by schedule (period close), source-arrival event (new COs admitted), or contract-version change — **never a dashboard read**. We never design "fast on-demand evaluation"; we design correct ahead-of-time evaluation + fast snapshot reads.

### 8.3 The evaluation run — first-class governed object
The structural piece that reconciles the invariants with scale. An **evaluation run** has a state machine (`queued → running → complete/failed/partial`), like MCF panel-runs. It is the idempotency boundary that reconciles **Inv V (non-replayable)** with **crash-safe retry**: a crashed worker *resumes the same run* (same `run_id` → idempotent snapshot writes); genuinely new evaluation (new data / new version) is a *new run* with new identity. **Retry ≠ replay.** Snapshot identity = `(metric, tenant, grain, period, contract_version, run_id)` → exactly-once under retry, monotonic under legitimate re-evaluation. Without the run object there is no safe distribution and no Inv-VI evidence anchor.

### 8.4 Bitemporality — forced in for finance-grade restatement
Every snapshot carries **two time axes**: **event time** (the business instant it is *as of*) and **knowledge time** (the instant it was evaluated). Late-arriving source data → a new evaluation at a later knowledge-time for the *same* event-time → a new immutable snapshot that **supersedes** (Inv III: append + supersede, never mutate). This answers "what did we believe AR was for Q1, as known on date X" — the restatement/audit question. The store must *stamp both axes* and never collapse them into a single "period" column (same fix as the §3.2 stock/flow result-frame gap).

### 8.5 The composite DAG is an invalidation problem
Composites (DSO) make evaluation a dependency graph: **ordering** (leaf metrics before composites — topological sort per tenant/period) and **invalidation propagation** (re-evaluating AR-balance must dirty + re-evaluate DSO). A build-system problem, not a flat list. The run carries a dependency *closure*.

### 8.6 NFR → design implication
| NFR | Shared-runtime reality | Design implication (v1, structural) |
|---|---|---|
| Isolation | one engine, N tenant DBs | connection-routed; no cross-tenant scope in any query or evidence row |
| Concurrency / noisy-neighbor | one tenant's close can starve others | per-tenant concurrency budget; the run is the unit of fairness |
| Scalability | metrics × tenants × periods | horizontal workers; parallel except the composite DAG |
| Resilience | crash mid-close | resumable runs (§8.3); per-partition + per-metric + per-tenant failure isolation |
| Consistency | immutable + restatements | bitemporal + append-supersede (§8.4); no in-place correction |
| Observability | audit ≠ ops | business **evidence** (Inv VI, `progression.*`) kept separate from engine **telemetry** (latency/queue/failure → CloudWatch) |
| Security / ISO 27001 | evidence holds financial data | least-privilege DB role (read CO, write MS+evidence, no DDL); KMS at rest; the immutable run *is* the A.12.4 audit trail |
| Cost | don't re-evaluate needlessly | **trigger discipline, not result caching** — evaluate only on a governed cause. The Inv-V-safe form of "don't recompute". |

### 8.7 AWS target topology (ap-south-1, `barecount` profile)
Reasoned from the execution model; to be grounded against `platform-infra-stack` in ADR #1.
- **Compute:** queue-driven **worker fleet on ECS Fargate**, *separate from the bc-core API* (the noisy-neighbor firewall). Not Lambda (15-min ceiling, cold starts, per-tenant DB connection churn).
- **Queue:** **SQS** for run jobs; composite DAG ordering via the run orchestrator (escalate to **Step Functions** if the DAG deepens). FIFO only where ordering is required.
- **Scheduling:** **EventBridge** for period-close + source-admission → "evaluate affected metrics".
- **Data:** **RDS Postgres** (platform + per-tenant); **RDS Proxy** once tenant count grows (workers × tenant DBs = connection explosion).
- **Cold storage:** **S3 + Object Lock** for archived snapshots/evidence — Object Lock *is* Inv III at the storage layer and the ISO retention story.
- **DR:** multi-AZ RDS.

**Engine-shaping recommendation:** design the engine as **resumable, idempotent, run-oriented, queue-consuming** so the AWS scale-out is a *deployment* change, not an engine rewrite.

### 8.8 Structural (bake into v1) vs tunable (defer)
- **Structural:** the run object + state machine; snapshot identity/idempotency; bitemporal stamping; the trigger model (schedule/event, never read); composite dependency closure; the queue-oriented worker seam.
- **Tunable:** worker count, RDS instance class, Fargate-vs-future-Lambda, retention windows, Step-Functions-vs-homegrown orchestrator.

### 8.9 Build & deployment strategy — local-first, portable seams
The engine is a **90/10 split**: ~90% (schema, evaluation act, transactionality, immutability as DB constraints, run state machine, idempotency, evidence/lineage) is **DB-centric + pure TypeScript and environment-identical**; ~10% is AWS-specific *edge* infra. Local Docker **Postgres 17.8 ≈ RDS Postgres 17**, so the hard, governance-bearing part behaves the same on a laptop and in the cloud.

**The one discipline that makes AWS an adapter-swap, not a rewrite:** *no AWS SDK import in the engine core.* The core sees thin ports; adapters are an interface + a small implementation, not a framework (YAGNI beyond these six):

| Seam | Local adapter | AWS adapter |
|---|---|---|
| Queue (run jobs) | in-process / `pg`-backed job table | SQS |
| Scheduler (triggers) | node timer / cron | EventBridge |
| Cold archive | filesystem (or deferred) | S3 + Object Lock |
| Connection pool | direct | RDS Proxy |
| Secrets | `.env` | Secrets Manager |
| Telemetry sink | pino → stdout | CloudWatch |

**Phased plan:**
1. **Build + prove locally** on `tbc_pilot1_dev` — the 51 metrics → snapshots + evidence + transactional runs. Governance-parity is earned here, cheaply.
2. **Honor the six seams** as thin ports from day one (the entire "deployment-suitable" tax).
3. **Deployment hardening** — AWS adapters + the IaC in `platform-infra-stack` + a **small distributed spike** (SQS + one Fargate worker + RDS Proxy) to validate what local cannot: queue **redelivery** (at-least-once → idempotency must hold), worker **crash/resume** under concurrency, **connection limits**. Mitigated up-front by designing idempotency in (§8.3) and simulating double-delivery + mid-run kill against the local `pg`-queue.
4. **Pilot on AWS.**

**Local ↔ RDS parity checklist:**
- Postgres **version + extension parity** — confirm any local extension is RDS-available (vanilla PG + Drizzle → low risk; verify before relying on any extension).
- A dedicated **least-privilege PG role** for the engine now (read CO, write MS + evidence, **no DDL**), mirroring the future IAM/DB grant — so the security posture is modeled locally, not bolted on at deploy.
- Optional **LocalStack** for SQS/S3 fidelity, used only in the phase-3 spike (not needed for phases 1–2).

## 9. Non-goals

Not a store redesign (the `fact.*` **design** is sound; §3.2 provisioning/transactionality gaps are in-scope). Not an authoring-layer change (BCF/MCF are the mature reference). Not SDG work (SDG conforms to the Source Contracts this runtime already expects). Not a rewrite of the aggregation algebra (mature). The work is the **evaluation boundary** — the span from an activated `mcf.*` metric contract to a persisted, evidence-bearing Metric Snapshot.

## 10. Evidence & verification transcript (2026-07-01)

All headline data-claims are live-verified here; this section separates **live-DB facts** from the **code-structure facts** cited inline. Re-runnable via the `bc-postgres` MCP (platform DB) and `postgres.js` against port 5435.

**Platform DB — `bc_platform_dev`** (via `pg_server_info` → connection `ok`, PostgreSQL 17.8):
```sql
-- legacy envelope vs governed substrate
SELECT 'contract.mcv', count(*) FROM contract.metric_contract_version   -- → 0
UNION ALL SELECT 'mcf.mcv', count(*) FROM mcf.metric_contract_version;  -- → 52

-- governed governance-state breakdown
SELECT governance_state_code, count(*) FROM mcf.metric_contract_version
GROUP BY 1;                                       -- → active 51, review 1

-- temporal shape distribution (finding #5)
SELECT temporal_gate_shape_code, count(*) FROM mcf.metric_contract
GROUP BY 1;                                       -- → period_aggregate 37, as_of 15  (total 52)
```

**Tenant DB — `tbc_pilot1_dev`** (the *only* live tenant; `SELECT datname FROM pg_database WHERE datname LIKE 'tbc_%'` → 1 row. NB `apex`/`selenite` from prior sessions no longer exist; stale `.env` still points at `tbc_selenite_dev`):
```sql
-- metric snapshot fact tables provisioned?
SELECT table_name FROM information_schema.tables
WHERE table_schema='fact' AND table_name LIKE 'ms_%';   -- → [] (none)
-- canonical / source object fact tables?
SELECT table_name FROM information_schema.tables
WHERE table_schema='fact' AND (table_name LIKE 'co_%' OR table_name LIKE 'so_%');  -- → [] (none)
-- evaluations recorded?
SELECT count(*) FROM progression.metric_evaluation;     -- → 0
```
`progression` schema exists with the run/evaluation tables (`metric_run`, `metric_evaluation`, `canonical_run`, …) but they are empty. **Conclusion:** the live tenant is greenfield — nothing evaluated, nothing persisted, no fact tables provisioned.

**Code-structure facts (static, not data):** `evaluateGovernedMetric` has no production callers (`governed-metric-runtime.ts:230`, impl+spec only); the four non-selective shapes return identity in `select-by-gate.ts:212`; governed AST divide-by-zero → `null` (`formula-execution.engine.ts:430`); legacy divide-by-zero → error (`metric-evaluation-engine.service.ts:613`); `progression.metric_evaluation` write is fire-and-forget (`metric.service.ts:52`) while `fact.ms_*`+index are awaited (`metric.repository.ts:213`).

**Prior contradicting artifact:** `04-mcf-substrate.sql:53` header comment cites 1,022 MCV rows / 729 active — **stale**, superseded by the live count of 52 above.

---

*Sections §§11–15 capture the operator design review of 2026-07-01. To keep reality separate from proposal, every claim carries a grounding tag:*
**[F]** Foundation invariant (quoted from `docs/foundation/the-invariants.md`) · **[L]** live-verified this session (§10) · **[C]** existing code/schema · **[T]** target — proposed, not built · **[X]** external framework influence.

## 11. Operational governance

### 11.1 Engine change-safety (rollout / rollback / hotfix)
The engine is shared blast-radius (§8.1), so a code change is the highest-risk act on the platform — one determinism defect is wrong numbers for every tenant at once.
- **[C]** The engine core (`FormulaExecutionEngine`, `src/registry/mcf/formula-execution.engine.ts`) is a pure AST interpreter (§3.1) — no `eval()`, consistent with Foundation coding rule 1 — so its output is fully reproducible for a given input. Determinism is the property that makes change *testable*.
- **[F]** State is immutable — Inv III: *"Produced authoritative objects are never altered in place"* — and each evaluation is a distinct versioned act — Inv V: *"Re-evaluation of the same inputs… yields a new version."* Together these make **rollback non-destructive**: a superseded engine version's outputs remain as immutable history; new evaluations route to the chosen version. You never un-write.
- **[F]** Inv VI requires Evidence to record *"the evaluation type, inputs, outputs, evaluation context, and outcome,"* so stamping the engine version on each evaluation is recording *evaluation context*, not new machinery. **[T]** the `engine_version` field is not yet emitted — ADR #6 scope.
- **[T]** Golden/characterization test corpus, shadow (dark-launch) evaluation, per-cohort progressive rollout, and a hotfix fast-lane are proposed, not built. Principle (grounded in determinism [C] + Inv V/III [F]): a change that alters any golden output is a *semantic* change (new engine version + re-evaluation decision); one that preserves all outputs is a safe refactor. **[X]** characterization testing (Feathers); canary/shadow deploys; feature-flag cohorts.

### 11.2 Observability & SLOs
- **[C]** `progression.metric_run` already persists `duration_ms`, `metrics_evaluated`, `metrics_computed`, `metrics_failed`, `error_count` (live schema, §10) — the telemetry substrate partly exists.
- **[F]** Operational telemetry is kept distinct from business Evidence — Inv VI Evidence lives on the authoritative chain; *"Retention governs observability. It does not redefine truth."* Engine metrics are diagnostics, never inputs to meaning.
- **[T] / [X]** Target: the four golden signals (latency, traffic, errors, saturation — Google SRE) plus domain SLIs — **freshness** (snapshot availability vs period close) and **deferral / restatement rate** (a restatement spike signals upstream data-lateness; a deferral spike signals source unavailability). Not implemented.

### 11.3 The runtime rule book
- **[C]** The platform already runs a separate *machine-checkable chain invariants* track (`docs/adrs/ADR-chain-invariants.md`, cited in CLAUDE.md). **[F]** the-invariants.md §"Testing a proposed behavior" defines a six-check matrix (Meaning, Ordering, Immutability, Reference, Replay, Evidence): *"A behavior that passes all six checks is consistent with the execution model. A behavior that fails any one is incorrect… regardless of intent or utility."*
- **[T]** Target: the analogous machine-checkable *evaluation* rule book — the six checks plus the closure rule (§5), idempotency/transactionality (ADR #1), and admissibility (§6.8) — expressed as **fail-closed runtime guards** + a proving test suite. **[X]** design-by-contract (Eiffel pre/post/invariants) + Power-of-Ten assertion density (already adopted in CLAUDE.md coding standards).

### 11.4 Safety & security guardrails
- **[F] / [C]** Tenant isolation is structural — separate tenant databases `tbc_{slug}_dev` (D167); the engine routes by connection, never a shared-table `tenant_id` filter (§8.1).
- **[C]** The DDL generator validates every contract-declared identifier against `IDENT_RE` (`ddl-generator.service.ts:95`) and maps `decimal`/`number` → `numeric` (`TYPE_MAP`, `:82`) — giving injection-safety on generated DDL and exact decimal arithmetic (no floating-point non-determinism, a silent correctness hazard for a financial engine).
- **[T]** Bounded-resource guards (partition/row/memory caps, query timeouts), circuit-breaker / poison-pill quarantine, and client read-API rate limiting are proposed. **[T, AWS-phase]** KMS-at-rest + Secrets Manager (§8.9). **[X]** Power of Ten (bounded resources), OWASP (injection, access control), ISO 27001 A.12.4 (the immutable run/evidence *is* the audit trail).

### 11.5 Retries
- **[F] / [ADR #1]** Idempotency (snapshot identity + `INSERT … ON CONFLICT DO NOTHING`, decision 3) makes retry safe — a retry or duplicate delivery cannot double-write or rewrite (Inv III). **[C]** Per-partition isolation (`rejectedGroups`, governed-metric-runtime) already localizes a partition failure.
- **[T]** Target: transient-vs-terminal error classification, exponential backoff + jitter, bounded attempts → dead-letter; source-absence handled as a **deferral re-checked on the next trigger** (ADR #1 decision 7), not a tight loop. **[F]** bounded attempts — Power of Ten (no unbounded loops). **[X]** Release It! (Nygard), SQS/DLQ, backoff+jitter.

## 12. Failure model

**Doctrine — [F]:** *it is always safe to emit no snapshot, and never safe to emit a wrong one.* Inv VI: if no Evidence exists the platform *"treats that evaluation as not having occurred,"* and treating an *"absent Evidence record… as a probably-successful evaluation"* is disallowed. So every failure resolves toward **absence-with-explanation**, never plausible-but-wrong.

Handling principles: fail-closed **[F Inv VI]**; immutability ⇒ corruption impossible by construction, a failed act produces no authoritative object **[F Inv III]**; no silent failure — every failure records a typed diagnostic **[F Inv VI]**; contain blast radius partition ⊂ metric ⊂ tenant ⊂ fleet **[§8.6]**; resumable, not restarted **[C / ADR #1]**; precise non-destructive recovery via version/run stamping **[F Inv III/V]**.

**FMEA** (handling column tagged by grounding):

| Layer | Failure | Handling |
|---|---|---|
| Input | source unreachable / zero required COs | **defer** — `deferred_inputs_unavailable`, no snapshot **[F Inv II/VI; ADR #1 dec.7]** |
| Input | partial (some partitions lack data) | evaluate admissible partitions, defer rest; late arrivals → superseding version **[F Inv V]** |
| Compute | divide-by-zero / null / overflow | fail-closed typed rejection for that partition; siblings proceed **[T — today fail-open, §4; ADR #5]** |
| Compute | unknown AST / bad contract | terminal, no retry, alert (should be caught at publication) **[C rule-book intent; T guard]** |
| Compute | resource blow-up | bounded-resource guard trips before OOM **[T]** |
| Infra | worker crash mid-run | reaper re-enqueues; new worker resumes same `run_id`, ON CONFLICT skips written partitions **[C run object; T reaper/lease]** |
| Infra | DB txn abort mid-write | full rollback — nothing persisted **[ADR #1 dec.4]** |
| Infra | DB / queue unreachable | transient → backoff; persistent → defer + alert **[T]** |
| Systemic | poison metric (always fails) | circuit-break + quarantine; rest keep running **[T]** |
| Systemic | **engine bug → wrong-but-valid numbers** | enumerate by `engine_version` + `run_id`, supersede the exact blast radius; bad rows stay marked-superseded **[F Inv III/V make this tractable; T detection = golden+shadow+anomaly]** |
| Serving | client reads mid-restatement | read-model serves last committed version; txn hides in-flight **[F Inv IV explicit versioned refs; T read-model]** |

The failure that matters for a life-critical platform is the **silent wrong number**, not the crash (crashes fail-closed and resume). It is only recoverable because immutability + version-stamping **[F Inv III/V]** make the affected set enumerable and supersedable — in a mutable store a bad value that overwrote the good one is unrecoverable.

**[X] Influences:** Release It! stability patterns (Nygard); Erlang/OTP supervision (isolate, crash cleanly, supervisor restarts — we *supersede*, never compensate, because of Inv III); FMEA (safety engineering — this table is the maintained artifact); Chaos engineering (the *validation* method — fault-inject in the phase-3 spike, §8.9; an un-fault-injected failure framework is a hypothesis, not a guarantee).

## 13. The Evaluation Orchestrator (control plane)

Two planes: the **engine is the data plane** **[C]** (evaluates one metric given admissible inputs, deterministically); the **orchestrator is the control plane** **[T — not built]** (decides *when* each metric is ready and in *what order*). A cron is time-blind; this is dependency-aware.

- **[F]** The orchestrator is the *temporal enforcement of Invariant II*. Inv II: the object sequence is *"non-skippable"* and *"A Metric Snapshot derives from one or more Canonical Object versions… No object exists without its ordered predecessors."* So the orchestrator will not trigger a metric before its CO predecessors exist.
- **[F]** Its triggers are completion-events / schedule / version-change — never reads (Inv I: *"Reads, queries, and consumer access do not trigger evaluation"*).
- **One dependency graph, two edge types** (grounded in Inv II ordering): **CO-cycle-completion edges** (a metric waits for its period's Canonical Objects to land) and **metric-snapshot edges** (composite: DSO ⟵ AR-balance + revenue). A node fires when all incoming edges are satisfied. **[C]** the CO-completion signal has a real anchor — `progression.canonical_run` carries a `status_code` state machine (live, §10), so "CO-cycle-complete = the required `canonical_run`(s) terminal for (contract, period)"; **[C]** the metric edge is `metric_input` + PE-MC-14/15 (§3.1).
- **Completeness signal [T]:** boundary-completion events (each `canonical_run` emits "complete for (contract, period)") + a **period-close** signal from the fiscal calendar (D363–365) for the "no more COs coming" question + a **watermark** grace window for late data (→ restatement, a new superseding version). **[X]** Flink/Beam watermark + window-trigger model.
- **Properties [T]:** dependency-aware (topological), readiness-gated (schedule proposes, admissibility disposes), durable state (persisted graph + watermarks survive restart), invalidation propagation (upstream restatement re-triggers dependents — §8.5), deadline/SLA-aware (escalate if a dependency misses period-close), backpressure (per-tenant budget), and an observable dependency-trace ("why hasn't DSO evaluated → waiting on revenue → waiting on CO cycle CC-X/Q2").
- **Portability [§8.9]:** the scheduler *transport* is a port (local timer → EventBridge); the *orchestration logic* is portable framework code. The DAG is **data-driven** (which COs landed is runtime state), so it must **not** be encoded into EventBridge or a static Step Functions state machine — those fire ticks; the orchestrator does the dependency resolution against persisted state.
- **[X]** Influences: Dagster software-defined assets + auto-materialize + freshness policies (closest fit); Airflow/Prefect sensors; Flink watermarks; Bazel dirty-propagation; incremental materialized-view maintenance (as new acts, never in-place "refresh" — the forbidden vocabulary).
- **Placement:** ADR #8, composing ADR #2 (closure signal) + ADR #3 (DAG).

## 14. Client serving layer (their data)

- **[C] / [L]** `fact.ms_*` is typed columnar — the generator maps each declared field to a typed PG column (`ddl-generator.service.ts`), per **[CLAUDE.md]** D162 Rule 1 (no JSONB for queryable data). **[L]** the legacy `envelope.metric_snapshot` uses `metric_value_json` (live, §10) and is being deprecated (ADR #1 decision 5). So the governed store **is** directly queryable (filter by dimension, period range, top-N) — a genuine platform capability that a JSONB store would foreclose.
- **[F]** A client metric API is a store read, not an evaluation — Inv I: *"Reads, queries, and consumer access do not trigger evaluation."* So reads are fast lookups of pre-computed snapshots, and evaluation is always ahead-of-read (§8.2).
- **[T]** Target: a tenant-scoped, JWT-guarded read API (never direct DB); a **stable read-model** (`metric_snapshot_index`, not present live [L]) over versioned physical tables so clients see "ARPI = value" not `ms_arpi_v1_0_0`; **lineage as a client audit feature** (Inv VI Evidence exists → expose which COs produced a number); bitemporal "as-reported-on-date-X" views (§8.4); export / portability.
- **[X]** star schema (Kimball); metrics semantic layer (dbt Semantic Layer, Cube).
- **Placement:** ADR #4 (evidence/lineage + serving).

## 15. Framework-influences appendix

All external **[X]** — adopted as *influence*, mapped to our model; none is our implementation.

| Framework | Mechanism borrowed | Applied at |
|---|---|---|
| Beam/Flink | event-time vs processing-time; watermarks; window triggers | knowledge-time vs event-time (§8.4); admissibility/completeness (§6.8, §13) |
| Bitemporal DB (Snodgrass) | valid-time + transaction-time | restatement model (§8.4) |
| Feature stores (Feast/Tecton) | point-in-time correctness; serve pre-computed | as-of stock reads; serving layer (§14) |
| Dagster | software-defined assets, auto-materialize, freshness | the orchestrator (§13) |
| Event sourcing / CQRS | append-only events + read projections | immutable snapshots + read-model (§14) |
| Release It! (Nygard) | circuit breaker, bulkhead, timeout, fail-fast | guardrails, retries, failure model (§11.4–11.5, §12) |
| Erlang/OTP | supervision, isolate-and-restart | run/worker recovery (§12) |
| Google SRE | four golden signals, SLO/error budget | observability (§11.2) |
| Power of Ten (NASA/JPL) | bounded resources, assertion density | guardrails, rule book (§11.3–11.4) — already in CLAUDE.md |
| Kimball / dbt Semantic Layer | star schema, semantic metrics interface | store + serving (§3.2, §14) |
| Chaos engineering (Netflix) | fault injection as validation | phase-3 spike (§8.9), failure model (§12) |
