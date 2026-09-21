---
title: Structural Integrity — Program (SSOT)
status: drafting
date: 2026-09-21
anchor_task: TSK-f38fb6
lineage: >
  Track S (Structure) of Platform Readiness & Legibility — spun off 2026-09-21 and, on grounded
  study, reframed from "code movement" to "structural integrity across four planes" and renamed
  Structural Integrity (operator-approved, SES-2b96b2). Successor after Codex d619-001 CHANGES
  REQUIRED — the two plane-c "coherence gaps" were reclassified on reachability/behaviour evidence
  (see §2).
governing_adrs: >
  DEC-33d436/D606 (parent program mandate + four-track model — Track S is the deferred track this
  program executes); DEC-c48b0f/D541 (the design/execution intake gate — the engine of the coherence
  method); DEC-0d5b39 + DEC-01bd6b (the decided target for the BoundaryModule split, plane a);
  DEC-3aa336 (registry/mcf single home + registry-root cleanup, plane a scope boundary);
  DEC-623f8f/D370 (ADR hygiene policy — plane b's existing owner); DEC-1918d0/D162 (platform DB
  schema model — declares 82 tables across 12 schemas and DELEGATES the authoritative inventory to
  architecture/database/schema-map.md; a plane-d specimen: the inline count is stale vs the live 20
  application schemas); DEC-b1a286 (schema authority chain — live DB is ground truth, docker/redesign
  is the mechanism, Drizzle is a type surface). This program's own EXECUTION ADR is DEC-027ef6/D619
  (it names the Codex exchange family `d619-`; locks the four-plane framework, the coherence method,
  the package discipline, the ownership rule, and the sequencing), and re-decides nothing.
related: >
  Platform Readiness & Legibility (implementation/platform-readiness-program.md, TSK-4b2404) — parent.
  Legacy Metric Corpus Retirement (D608, TSK-d21b97) — REFERENCED owner of the legacy metric-* DROP
  (whose named target contract.metric_contract is absent from the live DB — reconcile first).
  Platform DB Foundation (overview/platform-db-foundation.md, TSK-cc348a) — REFERENCED owner of the
  schema SSOT / tenant substrate. ADR hygiene punch-list (TSK-f720ba/d3e83a/1557c5/0c4e67/c4c8a3/
  2d166b) — REFERENCED owner of plane-b content items. Platform/tenant boundary drift (DEC-96cc78/
  D612) — REFERENCED, not absorbed.
---

# Structural Integrity — Program (SSOT)

**One line.** Bring `bc-core` and its records into **structural integrity** — the state where what is
**decided** (ADRs), **documented** (bc-docs), **coded** (bc-core), and **in the database** all agree —
and keep the code's structure honest. Track S of Platform Readiness.

**What the grounded study concluded (honest, post-review).** **No coherence gap was found in the cells
assessed** — but the sweep was **breadth-first, not a per-cell audit** (§3 marks most cells not-assessed),
so this is "no gap found where looked," not "everything verified coherent." The RT "destructive delete"
this program first elevated is **unreachable** and its intended design **already exists** (§2). The L5
resolver routes **fail safe** (refuse) — the failure-mode claim was corrected — but whether an
empty-legacy dependency satisfies their **advertised route contract** is an **OPEN adjudication**
(SI-L5-1, Foundation-gated before any removal/repointing). What remains is **governance-trail + legibility
hygiene plus that one open L5 contract question** — so ceremony scales down, but L5 is not closed. The
value is docs↔code↔ADR consistency (the parent program's ~24% docs≠code cause), not file-moving (~9%).

## 1. The four planes

| Plane | Name | Question |
|---|---|---|
| **a** | Physical code structure | Are the largest artifacts cohesive; is dead code removed? |
| **b** | Decision / doc hygiene | Is the ADR estate self-consistent and its status truthful? |
| **c** | Decision ↔ code ↔ DB coherence | Does reality match what was decided and documented? |
| **d** | SSOT / authority structure | Are the authority documents numerically true to substrate? |

## 2. Grounded state (SES-2b96b2; verdicts authoritative, earlier hypotheses marked historical)

**Note on method:** an early inventory pass produced hypotheses; several were **overturned by
verification.** Only the verified verdicts below are authoritative. Where a hypothesis was wrong, it is
named so the correction is legible — not carried as a live claim.

### Plane a — physical code structure
- **The five decided moves** (confirmed by count, `bc-core` `53bb1115…`): registry↔boundary decoupling
  (31 boundary files import registry); cert-writer `mcf-cert-writer.service.ts` 3,768 LOC; McfReadService
  `mcf-read.service.ts` 1,992 LOC; registry-root cleanup (36 loose depth-1 `.ts`, minus D608-owned legacy
  and the by-name-retained `intake-queue.*`); BoundaryModule split (24 controllers). Legibility only.
- **Dead / unreachable residue** (removal is plane a, and **410-contract-careful** — see §6, package
  SI-A-1): `ReaderRepository.deleteReader` (the hard-delete cascade) has **no production caller** —
  `ReaderController` → `ReaderService.deleteReader` throws `ForbiddenException` unconditionally
  (`reader.service.ts:170`, tested by `reader.service.governance.spec.ts`); it is latent residue.
  Legacy `canonical_mapping` resolver routes; ~10 retired-but-mounted 410 controllers;
  `observation_field_map` dead schema def (guard-tested, unwired).

### Plane b — decision / doc hygiene
- **Doctrine-without-ADR (the clearest real item).** Rules stated only in CLAUDE.md with no backing ADR:
  the **Core Dashboard retirement has no decision record at all**; IntegrityService's deprecation
  *lifecycle* (only the gate-off is ADR'd, DEC-29b518/DEC-d9fa49); the auth-bypass ban (no bc-core-scoped
  ADR); code comments citing "CLAUDE.md" as authority instead of the governing ADR.
- **ADR-not-updated-post-implementation.** ADR-42b9c0's "closing commit" note was never added; ADR-324d9e
  never flags its Stripe half is unbuilt; the S2 UI placeholder over-promises RBAC a 1-table schema can't
  back; the seed `connectors.csv` has no `odoo` entry though the executor exists.
- **Hygiene mechanism (narrowed).** `audit_adrs.py` **already** checks stuck-`proposed` age **and runs in
  CI on each PR/push** (so stuck-proposed is *covered*, not blind — earlier stale saved reports are a
  different thing). What it does **not** check: `decided`-but-not-implemented, and status-vs-body
  contradiction. Those two are the real mechanism gap (SI-B-3).

### Plane c — decision ↔ code ↔ DB coherence
**Both first-elevated items were reclassified on verification — the substrate is coherent here.**
- **RT "destructive delete" — RECLASSIFIED to unreachable residue (not a live gap).** The hard-delete is
  behind the closed `ReaderService.deleteReader` (above). The intended teardown design **already exists**
  and is decided: hard delete is deferred to the **D564 governed expunge** (inventory + backup + evidence
  + operator gate) and legitimate retire is the soft `archiveReader` (per `reader.service.ts:163-169`
  docstring). No Invariant III violation is asserted; the 5-vs-140 `admission_run`/`run_summary` count
  difference is **not** attributed to reachable deletion (unproven; see §2.1).
- **L5 resolver routes — failure-mode corrected, contract adjudication OPEN.** `resolveRun` →
  `loadBindingAndEnvelope` **throws `NotFoundException`** on absent binding/version/mapping
  (`canonical-resolution.service.ts:357,360,368`), and `findBindingsReferencingOc` no-ops (`:271`) — so the
  earlier "silently returns nothing" claim was wrong: the routes **fail safe** (refuse). **But safe refusal
  is not coherence.** `OrchestratorController` and `TestBenchExecutionController` still **advertise
  canonical-resolution** and call `resolveRun` over a **permanently-empty legacy `contract.canonical_mapping`
  dependency**; whether that satisfies the advertised route contract, and whether the routes should be
  removed / repointed to the CC-v2 resolver, is **unadjudicated and OPEN.** This is **SI-L5-1** — an open
  contract/reachability adjudication that **passes the Foundation gate before any removal/repointing**, and
  needs governing retirement-or-coexistence authority. It is **not** folded into SI-A-1 as cosmetic residue.
- **Confirmed coherent (verified, not drift):** cert/eval **idempotency is active + DEC-5ea578-backed**;
  `mcf-realization-projection` v1/v2 is **coherent versioned coexistence** (v2 closes v1's gaps for a
  different consumer; migration 42 Codex-accepted) — not an unfinished supersession; the dual
  `certification_record` is an intentional BCF/MCF split; tenant `evidence.*` is correctly tenant-scoped.
- **Hand-off (not this program):** tenant `evidence.*` immutability triggers are written but not deployed
  (ADR-09fb2f) → DB-Foundation / tenant; `contract.metric_contract` (D608 DROP target) is **absent** from
  the live DB → D608 must re-point before any DROP.

### Plane d — SSOT / authority
- **DEC-1918d0/D162** declares **82 tables across 12 schemas** and **delegates** the authoritative
  inventory to `architecture/database/schema-map.md`; the live DB has **20 application schemas** (§2.1) —
  so the inline count is stale and the real check is schema-map.md currency (DB-Foundation-coordinated).
- CLAUDE.md's MCF snapshot (5 contracts) is stale vs the live 433.

### 2.1 Reproducibility record (exact, read-only)

Static counts are pinned to full commits and reproduced by the commands in Appendix B. DB counts are a
single read-only observation and are labelled as such — **they do not reconstruct the prior study's state
or prove any deletion history.**

- **Pins:** `bc-core` `53bb1115d9b1c4d841750cce31eb2f60f3174d76`; `bc-docs` base
  `3a9b3e986420ba79b21a5e0f0f838ba9e703de36`. Measured against `origin/main` refs at author time; the
  commands in Appendix B use the full SHAs so they are reproducible after the refs move.
- **DB observation (`bc_platform_dev`, read-only, `BEGIN READ ONLY`, observed 2026-09-21):**
  `information_schema.schemata` = **54** rows total — this **includes** `pg_catalog`/`pg_toast`/temp
  schemas and **varies** (e.g. 54 at 2026-09-21T10:28:43Z); **22** non-pg schemas (`schema_name NOT LIKE
  'pg_%'`); **20** application schemas (also `NOT IN ('public','information_schema')`); **258** application
  base tables (`table_type='BASE TABLE'`, same filters). The **pg_ filter is essential** — the raw total is
  not the schema count. `mcf.metric_contract` = 433; `to_regclass('contract.metric_contract')` = NULL
  (absent); `contract.canonical_mapping` = 0; `runtime.admission_run` = 5; `execution.run_summary` = 140 —
  these five are attributed to the **immutable prior proof** (Codex d619-001, observed
  2026-09-21T09:10:48Z, its scope unchanged) and re-run executably in Appendix B. The 5-vs-140 difference is
  a **current observation, not evidence of deletion.**
- **Counts sourced from the read-only sweep (SES-2b96b2), not independently re-pinned in this package** —
  the lane/plane verdicts (§3), the doctrine-without-ADR list, and the ADR status distribution — are
  labelled *study-derived* in §3 and the backlog, and each carries its file:line or ADR-uid evidence
  rather than a bare count.

## 3. Lane × plane integrity matrix

Function/lane × plane {a code · b doc · c coherence · d authority}. Each mark is a **verified verdict whose
cell note pins the evidence**, not a coverage colour: 🟢 verified-coherent (coordinate cited) · 🟡
residue/minor drift (coordinate cited) · 🔴 real gap (coordinate cited) · ⚪ **not assessed this pass** (the
breadth sweep touched the lane but did not per-cell verify). **Most cells are ⚪** — this was a breadth-first
sweep, not a per-cell audit. The honest global read is **"no coherence gap was found where assessed,"** not
"everything is verified coherent." Package priority (§6) is a separate axis.

| Lane | a | b | c | d | Evidence / note (owner) |
|---|:--:|:--:|:--:|:--:|---|
| S1 Auth | ⚪ | ⚪ | ⚪ | ⚪ | not assessed this pass |
| S2 User/access | ⚪ | 🟡 | ⚪ | ⚪ | b: RBAC over-promise copy (bc-admin AppRouter:277) + ADR-42b9c0 closing note absent (this prog) |
| S3 Tenant lifecycle | ⚪ | 🟢 | 🟢 | ⚪ | b/c: onboarding_record writes cite DEC-7df811 (tenant-management.repository.ts:98-101); `retired` status self-disclosed in the ADR |
| S4 Pricing | ⚪ | 🟡 | ⚪ | ⚪ | b: ADR-324d9e omits its own Stripe-unbuilt disclosure (this prog/punch-list) |
| L1 Source | ⚪ | ⚪ | 🟢 | ⚪ | c: `catalog_retirement_log` is governed append-only (CatalogRetirementService, DEC-e1312a) |
| L2 SC+AC | ⚪ | ⚪ | 🟡 | ⚪ | c: 305:305 is a workflow convention, not a DB unique (source-contract.ts index) |
| L4 OC | 🟡 | ⚪ | ⚪ | ⚪ | a: `observation_field_map` dead schema def, guard-tested → SI-A-1 |
| L5 CC | 🟡 | ⚪ | 🟡 | ⚪ | a: legacy resolver mounted; c: routes **fail-safe** (refuse, :357/360/368) BUT whether an empty-legacy dependency satisfies the advertised route contract is **unadjudicated — OPEN** → SI-L5-1 (Foundation-gated) |
| L6 MCF | 🟡 | ⚪ | ⚪ | ⚪ | a: cert-writer 3,768 + McfRead 1,992 LOC (size finding) → SI-A-2…6 |
| L7 Reader | 🟡 | 🟡 | ⚪ | ⚪ | a: unreachable `deleteReader` residue (reader.service.ts:170); b: stale memory note + connectors.csv drift |
| L9 Chain/Readiness | 🟡 | ⚪ | ⚪ | ⚪ | a: 410 readiness stubs + metric-funnel mounted (410-careful) → SI-A-1 |
| L10 Tenant onboarding | ⚪ | ⚪ | 🟢 | ⚪ | c: onboarding_record inert pending bc-db 0006 gate — intentional/known (DEC-7df811) |
| RT Runtime | 🟡 | ⚪ | ⚪ | ⚪ | a: dead idempotency guard + unreachable deleteReader; the delete-path reachability is verified closed (reader.service.ts:170) |
| EV Evidence | ⚪ | ⚪ | 🟡 | ⚪ | c: tenant `evidence.*` immutability triggers not deployed (ADR-09fb2f) → **DB-Foundation** |
| GOV Governance | ⚪ | 🔴 | ⚪ | 🟡 | b: doctrine-without-ADR (Core Dashboard no ADR) + hygiene mechanism gap (this prog); d: D162 inline count stale vs live 20 |
| L3 · L8 · S5 · TS · A1 | ⚪ | ⚪ | ⚪ | ⚪ | peer-owned / design-pending — not assessed |

## 4. The method — how a gap is adjudicated

Generalized from the T6 gate lesson and DEC-c48b0f/D541: (i) pin the load-bearing assertion; (ii) name the
expected code/DB surface; (iii) read substrate read-only; (iv) verdict + plane — coherent / design-gap /
execution-gap. **Verification includes reachability** (trace the call path from the controller/service, not
only the leaf method) — the lesson from d619-001, where two "gaps" were unreachable/fail-safe. Reads never
trigger evaluation; no substrate hand-edits.

## 5. Ownership & discipline

**Reference, don't absorb.** The program owns the unowned drift + the map + the method. D608 (TSK-d21b97),
DB Foundation (TSK-cc348a), the ADR-hygiene punch-list (D370), and DEC-96cc78/D612 remain their owners.

### 5.1 Design-cum-implementation packages — no refactor in isolation
Every package carries macro (connection map: what it touches / depends on / couples to) and micro (target
state, file-level steps, D541 verdict, acceptance) vision, plus a plain-English note. **Codex approves each
package before any code**; the PR implements an approved package. Any unit that touches a Foundation
boundary or invariant additionally passes the Foundation gate (`bc-docs/docs/foundation/the-invariants.md`)
— **SI-L5-1** (the open L5 route-contract adjudication) is such a case and passes the gate before any
removal/repointing; the gate applies to any future coherence unit.

### 5.2 Safe-window discipline with active peers (standing rule)
Re-confirm the safe window with active peers (foremost Tenant Readiness / TSK-d73f01) **immediately before
each code move** — not once. Treat every targeted element as potentially-active; the shared surfaces
(`src/__architecture__/*.snapshot.json`, `app.module.ts`, `src/attestation/`) are coordinate-first. A move
that can't get a fresh window waits.

## 6. Package set — reprioritized (real + cheap first; plain-English)

Priority reflects the honest post-review picture: the governance-trail and doc-number items are the real,
cheap value; residue removal is careful (410 contracts); the physical moves are last. **SI-RT-1 is
withdrawn** (unreachable; the design already exists). **SI-L5-1 stays OPEN** — the L5 route-contract
adjudication (Foundation-gated), **not** folded into SI-A-1 as cosmetic residue.

- **SI-B-1 · plane b · first.** *Plain: write the missing ADRs for rules that live only in CLAUDE.md — the
  Core Dashboard was retired with no record at all; IntegrityService's lifecycle; the auth-bypass ban — and
  fix code comments that cite CLAUDE.md instead of the real ADR.* The clearest genuine gap.
- **SI-D-1 · plane d · first.** *Plain: fix the docs whose numbers drifted from the live DB — D162's inline
  "12 schemas" vs the live 20 (and confirm schema-map.md currency with DB-Foundation); CLAUDE.md MCF
  5→433.* One-liners.
- **SI-B-3 · plane b · leverage.** *Plain: add two checks to the ADR health-check — "decided but never
  built" and "status says X but the body says not-X".* Stuck-proposed is already checked; these two aren't.
  Makes the program self-closing. Hand to D370 tooling.
- **SI-L5-1 · plane c · open adjudication (Foundation-gated).** *Plain: the two "resolve" API routes still
  advertise canonical-resolution over an old, permanently-empty mapping table. They refuse safely (no bad
  data), but whether they should keep advertising that contract — or be removed / repointed to the current
  resolver — is an open question.* Adjudicate the route contract + reachability; needs governing
  retirement-or-coexistence authority; **passes the Foundation gate before any removal/repointing.** Not
  cosmetic residue.
- **SI-A-1 · plane a · careful.** *Plain: remove dead/unreachable code and retired route-mounts — the
  unreachable `deleteReader`, the 410 controllers, the dead schema def* (the L5 resolver routes are **not**
  here — they are the open SI-L5-1 adjudication above).
  **Not "no behaviour change":** removing a 410 route changes its observable contract (410→404), and
  DEC-b049f6 deliberately chose 410. Requires a **route-by-route inventory** and, per route, either
  **preserve the 410 compatibility surface** or an **approved retirement-contract amendment** with caller
  impact + response tests. Unreachable non-HTTP residue (the `deleteReader` method) is a plain deletion.
- **SI-A-2…6 · plane a · last.** *Plain: structural cleanup of the largest files/modules — decouple
  boundary↔registry, split the two god-services, file the registry root, split BoundaryModule.* Legibility
  only; lowest-blast-first; the type/util relocation is the **first physical-relocation touch** (it changes
  no provider/route so it's snapshot-clean — but it is not "the first code touch," since SI-B-3/SI-A-1 can
  change code earlier).

**Hand-offs (reference-not-absorb):** `contract.metric_contract` phantom DROP target → D608; tenant
`evidence.*` immutability → DB Foundation; 4 stuck-`proposed` ADRs → punch-list (TSK-1557c5); realization
v1/v2 = coherent, no action; BCF cert Phase-A3 cutover → BCF.

## 7. Sequencing

1. **Map + method** (this SSOT + ADR DEC-027ef6/D619) → Codex exchange (`d619-`).
2. **Real + cheap first** — SI-B-1 (doctrine→ADR) and SI-D-1 (doc numbers).
3. **Leverage** — SI-B-3 (self-closing hygiene checks).
4. **Careful residue** — SI-A-1 (route-by-route, 410-contract-preserving).
5. **Open adjudication** — SI-L5-1 (the L5 route-contract question; Foundation-gated; not scheduled as a
   removal until adjudicated).
6. **Hand-offs** throughout.
7. **Physical moves last** — SI-A-2…6; the type/util relocation is the first *physical-relocation* touch;
   BoundaryModule last.

Every code step re-confirms a fresh safe window (§5.2) and is Codex-approved as a package (§5.1) first.

## 8. Authority & provenance

Executes Platform Readiness & Legibility §5 (Track S) + §7, DEC-33d436/D606. **Execution & sequencing ADR:
DEC-027ef6/D619** (names the Codex family `d619-`). Method engine: DEC-c48b0f/D541. Plane-a move decisions:
DEC-0d5b39 + DEC-01bd6b + DEC-3aa336. Plane-b policy: DEC-623f8f/D370. Plane-d specimen: DEC-1918d0/D162
(82 tables / 12 schemas, delegates to schema-map.md), DEC-b1a286. Referenced owners: D608 (TSK-d21b97), DB
Foundation (TSK-cc348a), the punch-list, DEC-96cc78/D612. Anchor: **TSK-f38fb6**. Ground study: SES-2b96b2
(2026-09-21). Successor to Codex d619-001 CHANGES REQUIRED.

### Appendix A — the five physical moves (plane a detail)
Lowest-blast-first. registry↔boundary decoupling splits into type/util relocations (the snapshot-clean
first physical-relocation touch) and service inversions (coordinated per shared surface). cert-writer and
McfReadService are **within-home file decompositions** behind a preserved facade — a different act from the
DEC-3aa336-forbidden *folder* reshuffle (M12 paths + prompt assets untouched); the Codex exchange
adjudicates that reconciliation before any mcf code moves. registry-root cleanup excludes the D608-owned
legacy `metric-*` files and the retained `intake-queue.*`. BoundaryModule → 4 boundaries + 2
axis-orchestrators (DEC-0d5b39/01bd6b) is highest blast, last.

### Appendix B — reproducibility commands
```
# plane a (git-ref against full SHA; local main diverged via squash-merge)
C=53bb1115d9b1c4d841750cce31eb2f60f3174d76
git grep -l -E "from ['\"].*/registry/" $C -- 'src/boundary/*.ts' | grep -v '\.spec\.' | wc -l   # 31
git show $C:src/registry/mcf/mcf-cert-writer.service.ts | wc -l                                   # 3768
git show $C:src/registry/mcf/mcf-read.service.ts | wc -l                                          # 1992
git ls-tree $C --name-only src/registry/ | grep '\.ts$' | grep -v '\.spec\.' | wc -l              # 36
# reachability (Finding 1): the delete is closed at the service
git show $C:src/registry/readers/reader.service.ts | sed -n '170,175p'   # throws ForbiddenException
git grep -n "deleteReader" $C -- 'src/**/*.ts' | grep -v '\.spec\.'      # no repository caller
# L5 fail-safe (Finding 2)
git show $C:src/boundary/canonical-resolution.service.ts | sed -n '355,368p'  # NotFoundException
# DB observation (read-only). In psql: \set ON_ERROR_STOP on
BEGIN READ ONLY;
-- schema scope (the raw total is NOT the schema count; the pg_ filter is essential)
SELECT count(*) FROM information_schema.schemata;                                             -- 54 (incl pg_*/temp; varies)
SELECT count(*) FROM information_schema.schemata WHERE schema_name NOT LIKE 'pg_%';           -- 22 (non-pg)
SELECT count(*) FROM information_schema.schemata
  WHERE schema_name NOT LIKE 'pg_%' AND schema_name NOT IN ('public','information_schema');   -- 20 (application)
SELECT count(*) FROM information_schema.tables
  WHERE table_type = 'BASE TABLE' AND table_schema NOT LIKE 'pg_%'
    AND table_schema NOT IN ('public','information_schema');                                  -- 258 (application base tables)
-- retained counts (attributed to prior proof d619-001, observed 2026-09-21T09:10:48Z)
SELECT count(*) FROM mcf.metric_contract;                                                     -- 433
SELECT to_regclass('contract.metric_contract');                                              -- NULL (absent)
SELECT count(*) FROM contract.canonical_mapping;                                             -- 0
SELECT count(*) FROM runtime.admission_run;                                                  -- 5
SELECT count(*) FROM execution.run_summary;                                                  -- 140
COMMIT;
```
