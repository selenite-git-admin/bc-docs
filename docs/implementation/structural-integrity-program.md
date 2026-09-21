---
title: Structural Integrity — Program (SSOT)
status: drafting
date: 2026-09-21
anchor_task: TSK-f38fb6
lineage: >
  Track S (Structure) of Platform Readiness & Legibility — spun off 2026-09-21 and, on grounded
  study, reframed from "code movement" to "structural integrity across four planes" and renamed
  Structural Integrity (operator-approved, SES-2b96b2).
governing_adrs: >
  DEC-33d436/D606 (parent program mandate + four-track model — Track S is the deferred track this
  program executes); DEC-c48b0f/D541 (the design/execution intake gate — the engine of the coherence
  method); DEC-0d5b39 + DEC-01bd6b (the decided target for the BoundaryModule split, plane a);
  DEC-3aa336 (registry/mcf single home + registry-root cleanup, plane a scope boundary);
  DEC-623f8f/D370 (ADR hygiene policy — plane b's existing owner); DEC-1918d0/D162 (platform DB
  schema model — a plane-d specimen: it declares 11 schemas, the live DB holds 20); DEC-b1a286
  (schema authority chain — live DB is ground truth, docker/redesign is the mechanism, Drizzle is a
  type surface). This program's own EXECUTION ADR is DEC-027ef6/D619 (it names the Codex exchange
  family `d619-`; locks the four-plane framework, the coherence method, the package discipline, the
  ownership rule, and the sequencing), and re-decides nothing.
related: >
  Platform Readiness & Legibility (implementation/platform-readiness-program.md, TSK-4b2404) — parent;
  its ~9%/24%/24% stall analysis is why this program weights integrity over file-moving.
  Legacy Metric Corpus Retirement (D608, TSK-d21b97) — REFERENCED owner of the legacy metric-* DROP
  (whose target contract.metric_contract this study found ABSENT from the live DB — reconcile first).
  Platform DB Foundation (overview/platform-db-foundation.md, TSK-cc348a) — REFERENCED owner of the
  schema SSOT / tenant substrate. ADR hygiene punch-list (TSK-f720ba/d3e83a/1557c5/0c4e67/c4c8a3/
  2d166b) — REFERENCED owner of plane-b content items. Design-plane vs execution-plane couplings
  (finding, TSK-b5ab8a) — the coherence theme, plane c. Platform/tenant boundary drift (DEC-96cc78/
  D612) — REFERENCED, not absorbed.
---

# Structural Integrity — Program (SSOT)

**One line.** Bring `bc-core` and its records back into **structural integrity** — the state where what is
**decided** (ADRs), **documented** (bc-docs), **coded** (bc-core), and **in the database**
(`bc_platform_dev`) all agree — and keep the code's own structure honest. Spun off as Track S of
Platform Readiness; reframed on grounded study from "move some files" to "reconcile the four planes."

**Why the reframe.** The parent program's stall analysis is load-bearing: code structure caused **~9%**
of stalls, while **docs≠code (24%)** and **missing-decision / wrong-plane (24%)** dominated. Moving
files is the *cheap, low-value* work. The value is in the **coherence** the operator named: decision ↔
doc ↔ code ↔ DB. A grounded study (SES-2b96b2, 2026-09-21) confirmed the drift is real and
**concentrated in exactly that coherence plane** — so this program's center of gravity is there, not on
the file moves.

## 1. The four planes

Structural integrity is measured across four planes. The letters are a working shorthand, not a new
artifact family.

| Plane | Name | Question | Grounded weight |
|---|---|---|---|
| **a** | Physical code structure | Are the largest artifacts cohesive; is the dependency direction honest? | **low** (~9%) — one small sub-track |
| **b** | Decision / doc hygiene | Is the ADR estate self-consistent and its status truthful? | moderate; mostly owned; one **mechanism** gap |
| **c** | Decision ↔ code ↔ DB coherence | Does reality match what was decided and documented? | **the core** — where the drift lives |
| **d** | SSOT / authority structure | Are the authority documents themselves numerically true to substrate? | real, narrow, unowned |

## 2. Grounded state (SES-2b96b2, read-only against `origin/main` + live `bc_platform_dev`)

### Plane a — physical code structure (the five decided moves)
Confirmed against `origin/main 53bb1115`: registry↔boundary decoupling (**31** boundary files import
registry, 68 lines); cert-writer extraction (`mcf-cert-writer.service.ts` **3,768 LOC**); McfReadService
split (`mcf-read.service.ts` **1,992 LOC**); registry-root cleanup (**36** loose depth-1 `.ts`, minus the
D608-owned legacy files and the by-name-retained `intake-queue.*`); BoundaryModule split (**24**
controllers, ~27 providers, 9 imported modules — highest blast, last). Context: 1,253 non-spec `.ts`, 84
modules, 240 `any`, 558 `eslint-disable` across 230 files. Move details + the DEC-3aa336
within-home-decomposition reconciliation are in §Appendix A.

### Plane b — decision / doc hygiene
**597 ADRs** (269 implemented / **183 decided** / 125 superseded / 11 proposed / 8 reversed). The estate
is **healthier than feared**: frontmatter supersession is **clean (0/73 mismatches, independently
verified)**; stale-doctrine leakage into live doctrine folders is **small** (1 confirmed: `bc-ai` read as
current in `operating-model/metric-management-system.md`; 1 naming drift: doc says `ChainStatusService`,
code is `McvChainStatusService`). Docs corpus is **1,178 `.md`**, but only **~9%** is living doctrine
(~74% is governance/evidence record-keeping) — any doctrine↔code reconciliation searches a small target
inside a large archival mass.

**The one systemic finding is a *mechanism* gap, not a content gap:** the ADR-hygiene audit
(`audit_adrs.py`, last run 2026-08-24, 31 ADRs stale) tracks supersession but **does not track
"decided-but-not-implemented" or "status-vs-body contradiction" at all.** So **183 `decided` ADRs sit as
an unmonitored implementation backlog**, and **4 `proposed` ADRs have now crossed the D370 30-day stuck
threshold** (09fb2f, 116641, 7a18af, 9e68e0) without the stale report showing it. Traceability side-note:
**52 of 125 superseded ADRs have no frontmatter successor pointer** (~42% untraceable — older/narrative
supersession).

### Plane c — decision ↔ code ↔ DB coherence (THE CORE)
One pattern, everywhere: **a governed decision or doc asserts X; the code or DB holds not-X.**

- **Legacy `metric-catalog` + `metric-definition` (~1,650 LOC) still fully mounted** in `app.module.ts`
  (`:314` `MetricCatalogModule`, `:120` `MetricModule`) *alongside* the live MCF stack — a complete
  parallel architecture. *Open question the trace resolves:* is the mount **authorized** by the
  mcf-legacy-bridge read-fallback sunset (coherent-by-design) or is it **execution-gap** drift?
- **`contract.metric_contract` — the DROP target named by D608/TSK-d21b97 — does not exist** in the live
  DB. A retirement pointed at nothing; **reconcile before any DROP.**
- **Two retired 410-only readiness stubs still wired** (`ReadinessModule` `app.module:359`,
  `MetricReadinessController` `contract.module:83`).
- **`IntegrityService` (1,132 LOC): injected, zero call sites** — inert but for admin/test-bench doors.
- **Idempotency guard + interceptor + two DB tables: zero wiring** — a *declared* safety net with no
  runtime existence (any route claiming idempotency has none). → [[TSK-a6814f]].
- **`mcf-realization-projection` v1 + v2 both mounted and called** — a supersession left running in
  parallel.
- **`metric.*` is only partially dead** (2 of 7 tables actively written; `mls_state_event` = 3,319) —
  "legacy" is coarser than reality; no blanket drop.
- Parent-session verified cases (cited, not re-derived): ADR-f44a71 route (a) misframed vs the real
  MLS-23 blocker; `metric.mls_state` keyed to legacy ids absent from `mcf.metric_contract_version`;
  DEC-568d0b/D615 cited as authority but absent from the docs tree.

### Plane d — SSOT / authority structure
The authority documents have **numerically drifted** from substrate: **DEC-1918d0/D162 declares 11
schemas; the live DB has 20 (258 tables).** CLAUDE.md's MCF snapshot says 5 contracts; the DB holds
**433**. These are true-at-authoring records that reality outgrew — and the plane-b mechanism gap is why
nothing flags them.

**Reproducibility.** Every count above is reproducible from `bc-core`/`bc-docs` at `origin/main`
`53bb1115` / `be4f6ce` via `git`-ref commands, and from `bc_platform_dev` via read-only `SELECT`
(`information_schema` / `COUNT(*)`; note the `bc-postgres` `pg_list_tables`/`pg_count` tools are broken
server-side and were bypassed). Full command list: §Appendix B.

## 3. The method — how a coherence gap is adjudicated

Generalized from the T6 gate lesson (*stop out-parsing an adversary; pin the declared enforcement
surface and check reality against it*) and the design/execution gate (DEC-c48b0f/D541). For each
load-bearing decision:

1. **Pin the assertion.** State the one load-bearing claim the DEC/doc makes.
2. **Name the expected surface.** The table/column, service/method, or contract row it should manifest in.
3. **Read substrate (read-only).** Does the surface hold the claim?
4. **Verdict + plane.** `coherent` | `design-gap` (declaration wrong/missing → a contract change) |
   `execution-gap` (code violates a correct declaration → a boundary fix). **Naming the plane IS the
   D541 intake** — it routes the fix and forbids compensating at the wrong layer.

Every reconciliation item is recorded as a citable change record (the `CHG-…` pattern). The program does
**not** re-run evaluation or hand-edit rows to "fix" a number — a diagnostic that mutates substrate is a
violation, not a repair.

## 4. Ownership — the program finds the *unowned* drift

The program's discipline is **reference, don't absorb.** Most integrity work already has an owner; the
program owns the **gaps between owners** and the **cross-plane map**.

| Cell | Owner | This program |
|---|---|---|
| Plane a — 5 code moves | **this program** | owns + executes (sub-track, last) |
| Plane b — ADR content items | punch-list (f720ba/d3e83a/1557c5/0c4e67/c4c8a3/2d166b) + D370 | references |
| Plane b — **hygiene mechanism gap** | *unowned* | **owns** (propose the missing checks) |
| Plane c — legacy metric corpus | D608 / TSK-d21b97 | references (+ feeds the target-absent finding) |
| Plane c — schema / tenant substrate | DB Foundation / TSK-cc348a | references |
| Plane c — design/execution couplings | TSK-b5ab8a | references |
| Plane c — **systematic decided-retired-still-mounted class** | *unowned* | **owns** (reconcile, hand off) |
| Plane d — **doc↔substrate number staleness** | *unowned* | **owns** (the small unowned fixes) |
| Platform/tenant boundary drift | DEC-96cc78/D612 | references |

## 5. Scope discipline — bounded, not a standing audit

An integrity umbrella can rot into a program that audits forever and ships little. Hard bound:

- The program produces **(i)** the cross-plane integrity **map**, **(ii)** the reusable **method** (§3),
  and **(iii)** a **finite reconciliation backlog** (§6). It hands each item to its rightful owner, does
  the small unowned ones itself under normal governance, and **closes** when the backlog is drained.
- **No standing re-audit.** The recurring check belongs in tooling (the plane-b mechanism fix), not in a
  perpetual program.
- **Ceremony scales to consequence.** A doc-number fix is a one-line PR; a code un-mount is an ADR-gated,
  worktree-isolated, Codex-reviewed move. The five physical moves keep the full parent-program discipline
  (worktree off `origin/main`, D541 intake per move, one small surgical move, lowest-blast-first,
  BoundaryModule last) precisely because they are the highest-collision, not the highest-value, work.

### 5.1 Design-cum-implementation packages — no refactor in isolation

Structure is interconnected; a change judged in isolation breaks a connection elsewhere. Therefore the
program's pre-refactor work product is a set of **design-cum-implementation packages**, not ad-hoc PRs:

- **Every package carries both planes of vision at once.** *Macro:* the connection map — what the item
  touches, what depends on it, which decisions/docs/DB surfaces it links, and which other packages it is
  coupled to. *Micro:* the exact target state, the file-level implementation steps, the D541
  design/execution verdict, and the acceptance evidence.
- **Packages are linked, not siloed.** A master (macro) package holds the whole-system map + method +
  sequencing + the package index; each micro package cross-references the master and any sibling it is
  coupled to. Reviewing one means seeing its connections.
- **Auditor approval precedes any code.** No refactor — not even a snapshot-clean relocation — begins
  until its package is Codex-approved through the program's exchange family. The package *is* the review
  unit; the PR implements an already-approved package.

### 5.2 Safe-window discipline with active peers (standing rule)

`bc-core` is a hot tree with **actively-working peers**, foremost **Tenant Readiness (TSK-d73f01)**, which
may be using targeted elements at any time. A one-time "clear" is not a standing clearance:

- **Re-confirm the safe window immediately before *each* code move** — not once at program start. The
  earlier coordination (registry/mcf and boundary reported free of the parked PR #764) informs the plan;
  it does **not** authorize a move weeks later without a fresh check.
- **Treat every targeted element as potentially-active** until the peer confirms otherwise for that
  window. The shared surfaces (`src/__architecture__/*.snapshot.json`, `app.module.ts`,
  `src/attestation/`) and any file the peer names are coordinate-first, whoever-merges-first-wins.
- **A refactor that cannot get a fresh safe window waits.** Legibility is never worth stepping on a WIP
  peer's active work.

## 6. Reconciliation backlog (grounded; grows as traces land)

Each item carries a plane, an intake verdict once traced, and an owner/hand-off. Live status stays in
git/PR/DevHub; this is the decomposition.

| # | Plane | Item | Intake (design/execution — pending trace) | Owner / hand-off |
|---|---|---|---|---|
| C-1 | c→a | legacy metric-catalog + metric-definition **module-mount** residue | **T1 (CHG-8d0836): write-contract COHERENT** — routes 410'd per D481, corpus 0 rows, bridge DEC-c3e57f/D422 retired; the MOUNT is removable dead-module residue, not live drift | this prog (physical dead-module removal, LOW blast) |
| C-2 | c | `contract.metric_contract` DROP target is a **phantom** | **T3 (CHG-8d0836): CONFIRMED reference-integrity gap** — target never physically exists; real retired corpus = `metric.metric_definition` (0 rows) | **D608 / TSK-d21b97** (re-point target before any DROP) |
| C-3 | c→a | 2 retired 410 readiness stub **mounts** | **T5 (CHG-277925): COHERENT contract** (routes 410-Gone, DEC-b049f6/D548-backed) + removable dead-module residue | this prog (physical dead-module removal) |
| C-4 | c+b | IntegrityService: gate-off coherent, lifecycle doctrine-only | **T6 (CHG-277925): gate-off DECIDED** (DEC-29b518/D429 + DEC-d9fa49/D547 — coherent); but the deprecation LIFECYCLE lives in CLAUDE.md ONLY (not an ADR) + a dead injection in contract.service.ts | this prog: promote lifecycle→ADR + R5 task (plane b) + remove dead injection (plane a) |
| C-5 | c | idempotency: **generic HTTP guard aspirational** | **T4 (CHG-8d0836): SPLIT** — cert/eval path ACTIVE + DEC-5ea578-backed (coherent); only the generic `IdempotencyGuard`/interceptor/`infrastructure.idempotency_keys` is built-unwired-undecided | this prog / [[TSK-a6814f]] — retire (DBCP) or decide+wire |
| C-6 | c | `mcf-realization-projection` v1+v2 parallel | in-progress supersession — finish or fork | this prog (coord auditor contract) |
| B-1 | b | hygiene mechanism blind to decided-not-implemented + status-vs-body | design-gap (missing check) | this prog → propose to D370 tooling |
| B-2 | b | 4 proposed ADRs > 30d (D370) | content | **punch-list / TSK-1557c5** |
| D-1 | d/b | D162 inline count (82 tbl / 12 schema) stale vs live 20/258 | **T2 (CHG-8d0836): DESIGN-GAP** — but D162 **delegates** authority to `architecture/database/schema-map.md`; real check = is schema-map.md current; Platform/Tenant split intact | **DB-Foundation owns schema evolution** — coordinate; this prog checks schema-map.md currency |
| D-2 | d | CLAUDE.md MCF numbers stale (5 vs 433) | doc fix | this prog (one-line) |
| **C-7** | c | **L5: retired `canonical_mapping` (0 rows) backs 2 live production-labeled routes** — OrchestratorController `POST /t/admission-runs/:runId/resolve` + TestBenchExecutionController `POST /t/test-bench/resolve-canonical` via fully-DI-wired `CanonicalResolutionService` (boundary.module:18,93,163) | **execution-gap** — `executeFullCycle` stopped calling it (R5/D481 "tail dead") but the controllers still expose routes hitting the empty table | this prog (retire/repoint to CC-v2 resolver) |
| **C-8** | c | **RT: `runtime.admission_run` HARD-DELETED on reader deletion** (reader.repository:308-317) while `execution.run_summary` (no reader FK) is not → 140 vs 5 | **Foundation — Invariant III tension** (destructive prune of execution history; no ADR describes the cascade asymmetry) | this prog → **Foundation gate + design ADR** (highest stakes) |
| **B-3** | b | **doctrine-without-ADR class** (T6-generalized): Core Dashboard retirement (**NO ADR at all**), IntegrityService lifecycle specifics, auth-bypass rule (no bc-core-scoped ADR), citation-drift (code cites CLAUDE.md not ADR-ea9bdc/1e55d3/a6cdae) | design-gap — promote to ADRs + add code→ADR breadcrumbs | this prog |
| **B-4** | b | **ADR-not-updated-post-implementation**: ADR-42b9c0 closing-commit note never added; ADR-324d9e never flags Stripe-unbuilt; S2 UI placeholder over-promises RBAC vs 1-table schema; connectors.csv seed vs code registry drift (no odoo) | doc-hygiene | this prog / punch-list |
| **A-6** | a | **dead-mount 410 residue class (~10 controllers)**: mcf-publication-activation, metric-funnel, tenant-metrics (whole 410); mls-backfill, admin-test-bench, mcf-intake, metric-definition (partial); integrity.controller @deprecated-but-live; observation_field_map dead schema | execution/cleanup — mostly coherent-by-design "explicit-410-response"; decide per-controller keep-vs-remove | this prog (low blast) |
| **D-3** | c | evidence.* immutability triggers written-but-never-deployed (ADR-09fb2f, proposed) | declared-not-deployed | **DB-Foundation / tenant** (coordinate) |
| A-1…A-5 | a | the 5 code moves | design act + behavior-preserved invariant | this prog (last, lowest-blast-first) |

**Trace batch 1 verdicts (CHG-8d0836, read-only, via Platform Readiness).** Net shapes: T2/T3 = *decision-names-stale-reality* (design-gap: stale count / phantom target); T4 = *aspirational-code-never-decided* (generic HTTP guard only); T1 = *coherent-contract + removable-residue*. Calibration: the substrate is **more coherent than the raw inventory implied** — the write contracts (legacy 410'd; cert/eval idempotency DEC-backed) hold; the real gaps are dead-mount residue, a phantom DROP target, a stale delegated count, and one aspirational guard.

**Trace batch 2 verdicts (CHG-277925) + lane sweep (SES-2b96b2).** T5 = another coherent-410 residue; T6 =
gate-off coherent but the lifecycle is doctrine-only (→ B-3); T7 = **not drift** (coherent v1/v2
coexistence). The lane sweep added C-7 (L5 live-routes-on-retired-table), C-8 (RT hard-delete — the one
Foundation concern), the B-3/B-4 doctrine + hygiene items, and the A-6 residue class. Confirmed
**coherent (not drift)**: dual certification_record (intentional BCF/MCF split), tenant `evidence.*`
(correctly tenant-scoped), the tenant/onboarding-record "orphan" (bc-db adoption gate, tracked).

## 6.1 The package set — design-cum-implementation, plain-English

The backlog groups into these packages. Each carries the plain-English note the operator approves on;
each is Codex-approved before any code. Priority is highest-consequence first, physical moves last.

- **SI-RT-1 · plane c · 🔴 Foundation.** *Plain: execution-history rows are permanently deleted when a
  reader is removed — that conflicts with the "history is never rewritten" rule.* Decide the correct
  behaviour (archive / soft-delete) and record it in an ADR. Backlog: C-8. Needs the Foundation gate.
- **SI-L5-1 · plane c · 🔴.** *Plain: two live "resolve" API routes still call an old, now-empty mapping
  table and can silently return nothing.* Retire or repoint them to the current CC-v2 resolver.
  Backlog: C-7.
- **SI-B-1 · plane b · 🟡.** *Plain: several "X is retired/deprecated" rules live only in CLAUDE.md, not a
  decision record — including a whole retired project with no ADR at all.* Write the missing ADRs; fix
  code comments that cite CLAUDE.md instead of the real ADR. Backlog: B-3 (+ the C-4 lifecycle clause).
- **SI-B-3 · plane b · 🟡 (leverage).** *Plain: the automated ADR health-check doesn't catch "decided but
  never built" or "memory says X but no ADR does".* Add those checks so this class is caught
  automatically — this makes the program self-closing. Backlog: B-1 → hand to D370 tooling.
- **SI-A-1 · plane a · 🟡 (low blast).** *Plain: delete code and route-mounts for features already retired
  — they still load but every call returns "gone".* No behaviour change; some 410 mounts are kept on
  purpose, so decide per-controller. Backlog: A-6 (+ C-1/C-3 legacy/readiness mounts).
- **SI-D-1 · plane d · 🟢 (quick).** *Plain: update the docs whose numbers drifted from the live database
  (schema count 11→20, metric count 5→433).* Coordinate schema-map.md currency with DB-Foundation.
  Backlog: D-1/D-2.
- **SI-A-2…6 · plane a · 🟢 (last).** *Plain: structural cleanup of the largest files/modules — decouple
  boundary↔registry, split the two god-services, file the registry root, split BoundaryModule.*
  Legibility only; last, lowest-blast-first (sub-unit 1a snapshot-clean is the first code touch).
  Backlog: A-1…A-5 (detail in Appendix A).

**Hand-offs (reference-not-absorb):** C-2 phantom DROP target → D608; D-3 evidence immutability → DB
Foundation/tenant; B-2 stuck-proposed ADRs → punch-list; C-6 realization v1/v2 → pending one auditor
consumption check; BCF cert Phase-A3 cutover → BCF.

## 7. Sequencing

1. **Map + method first** — this SSOT + the execution ADR (the authority surface) → stand up the Codex
   exchange (own d-family, own watcher port).
2. **Foundation + coherence first** — SI-RT-1 (through the Foundation gate) and SI-L5-1: the two genuine
   coherence gaps, highest consequence.
3. **Doctrine + leverage** — SI-B-1 (promote doctrine to ADRs) and SI-B-3 (self-closing hygiene check).
4. **Quick wins + residue** — SI-D-1 (doc numbers), then SI-A-1 (dead-mount removal, low blast).
5. **Hand-offs** throughout — to D608, DB-Foundation, the punch-list, BCF.
6. **The five code moves last** — one small surgical move at a time, lowest-blast-first (registry↔boundary
   sub-unit 1a — snapshot-clean — is the first *code* touch), BoundaryModule last.

Every code step re-confirms a fresh safe window with active peers (§5.2) and is Codex-approved as a
package (§5.1) before it begins.

## 8. Authority & provenance

Executes Platform Readiness & Legibility §5 (Track S) + §7 (unit ledger), DEC-33d436/D606. **Execution &
sequencing ADR: DEC-027ef6/D619** (this program's own; names the Codex exchange family `d619-`). Method engine:
DEC-c48b0f/D541. Plane-a move decisions: DEC-0d5b39 + DEC-01bd6b + DEC-3aa336. Plane-b policy:
DEC-623f8f/D370. Plane-d specimens: DEC-1918d0/D162, DEC-b1a286. Referenced owners: D608 (TSK-d21b97),
DB Foundation (TSK-cc348a), TSK-b5ab8a, the punch-list, DEC-96cc78/D612. Anchor: **TSK-f38fb6**. Ground
study: SES-2b96b2 (2026-09-21), measured against `bc-core origin/main 53bb1115`, `bc-docs origin/main
be4f6ce`, and live `bc_platform_dev`.

---

### Appendix A — the five physical moves (plane a detail)

Ranked lowest-blast-first. registry↔boundary decoupling splits into type/util relocations (sub-unit 1a,
snapshot-clean, first) and service inversions (1b+, coordinated per shared-surface). cert-writer and
McfReadService are **within-home file decompositions** behind a preserved facade — a different act from
the DEC-3aa336-forbidden *folder* reshuffle (M12 panel paths + prompt assets stay untouched); **the Codex
exchange adjudicates this reconciliation before any mcf code moves.** registry-root cleanup's true scope
excludes the D608-owned legacy `metric-*` files (delete-not-file) and the by-name-retained
`intake-queue.*`. BoundaryModule → 4 boundaries + 2 axis-orchestrators (DEC-0d5b39/01bd6b) is highest
blast, last.

### Appendix B — reproducibility commands

```
# plane a / d (git-ref against origin/main; local main diverged 391 commits via squash-merge)
git grep -l -E "from ['\"].*/registry/" origin/main -- 'src/boundary/*.ts' | grep -v '\.spec\.' | wc -l   # 31
git show origin/main:src/registry/mcf/mcf-cert-writer.service.ts | wc -l                                   # 3768
git show origin/main:src/registry/mcf/mcf-read.service.ts | wc -l                                          # 1992
git ls-tree origin/main --name-only src/registry/ | grep '\.ts$' | grep -v '\.spec\.' | wc -l              # 36
# plane b (bc-docs origin/main)
git ls-tree origin/main --name-only docs/governance/adrs/ | grep -c 'ADR-'                                 # 597
# plane c / d (live bc_platform_dev, read-only)
SELECT count(*) FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%';                        # 20
SELECT to_regclass('contract.metric_contract');                                                           # NULL (absent)
SELECT count(*) FROM mcf.metric_contract;                                                                  # 433
```
