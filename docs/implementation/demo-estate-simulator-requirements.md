---
id: demo-estate-simulator-requirements
title: "Demo-Estate Simulator (bc-demo v2) — Requirements & Disposition Registers"
status: approved
authority: derived
depends_on: [the-invariants]
governing_sources:
  - DEC-8b17b1 (D561 demo-estates doctrine)
  - D524 (pilot source = BC + Odoo)
  - Track-2 discovery (devhub artifacts/odoo-pilot/TRACK2-DISCOVERY-findings-and-benchmark-2026-08-10.md)
---

# bc-demo — Demo-Estate Simulator v2: Requirements & Disposition Register

**Status:** DRAFT for operator review · 2026-08-10 · Session SES-3b3307
**Decides:** what the product is, what it must achieve (externally-anchored), what of v1 crosses the
boundary and what does not, the future-ready repo layout, and the v2.0 acceptance gate.
**After review:** an ADR records the settled decisions; only then is the repo-level STRIP executed.

---

## 1. Product definition

**bc-demo is the simulator that builds and maintains BareCount's demo estates** (D561 / DEC-8b17b1:
few-deep flagships, one per industry-domain × geography, Odoo-base, isolated per install, maintained
lifelong). It is a **software product**, not a set of build scripts:

- **One product, N source-system adapters, N estate profiles.** v2.0 ships one adapter (Odoo 19
  Enterprise) and one profile (`mfg-in`). **The second adapter is already named by doctrine:
  Microsoft Business Central (D524: pilot source = BC + Odoo, Odoo-first)** — the global/system
  split below is roadmap, not speculation. The architecture must accept a second profile without
  touching the core, and a second adapter without touching profiles — but v2.0 builds **no
  speculative code generality**: the adapter *code* boundary is drawn where the Odoo adapter needs
  it and generalized when the BC adapter is built. The *artifact* boundaries (targets, locales,
  knowledge, validation) split global/system **now** — that costs nothing and is where migration
  pain would otherwise live.
- **Architecture principle — two streams, mirroring the platform itself.** Every artifact family
  declares its stream: **GLOBAL** (business semantics: what an order-to-cash lifecycle *means*,
  what realistic DSO *is*, what a month-close *must prove*) vs **SYSTEM-SPECIFIC** (how one ERP
  realizes it: which models, which posting calls, which quirks). Meaning is declared once at the
  global layer; adapters bind it to a system — the same philosophy as BareCount's own contract
  chain (source-agnostic MC, binding layer per source). Applies to targets (§2), locales (§2b),
  events (FR-2), knowledge (§8), and validation (FR-9).
- **Users:** the three of us today; demo-estate operations tomorrow. Consumers: the BareCount
  platform (observes estates as real source systems), sales demos, the catalog/metric lanes.
- **Why v2 exists:** v1 grew as 22 byte-bound repair waves of horizontal timeline-sweeps. Gaps
  migrated between layers (valuation → reconciliation → costing) because business events were never
  coupled to their full consequence chain, and every one-line fix cost a governance cycle because
  drivers were not a released artifact. v2 inverts both: **vertical event lifecycles under an apex
  orchestrator, shaped closed-loop to externally-benchmarked targets, released as versioned
  software.**

## 2. Realism requirements (externally anchored — the apex targets)

The product's output must land inside the **real sector distribution**, not inside bands we invent.
Anchors: listed Indian auto-component/precision-engineering comparables, FY25 (Sundram Fasteners net
~9.1%, Bharat Forge ~7.3%, Endurance ~7.2%; ancillary inventory-turn and asset-turn distributions).
Full derivation: devhub `artifacts/odoo-pilot/TRACK2-DISCOVERY-findings-and-benchmark-2026-08-10.md`.

**Structure (GLOBAL stream): a system-agnostic target hierarchy.**
`Global vocabulary → Profile values → Estate overrides`. The *vocabulary* (what DSO, collection
rate, net margin, clearing-residual mean) is global and versioned; a *profile* supplies the values/
bands for its domain×locale; an *estate* may override (e.g. a deliberately-distressed demo). The
discipline that keeps it system-agnostic: **a target may only be phrased in business vocabulary** —
if a target names a system object (an account, a model, a module) it is mis-specified; the adapter
maps business phrase → system realization. R-1..R-12 below are the mfg-in profile's values.

| # | target | value (band) | v1 measured (defect) |
|---|---|---|---|
| R-1 | DSO | ~60d (45–75) | ~700d (F1a) |
| R-2 | collection rate | ≥95% of invoices cleared ≤90d past due | ~63% ever paid |
| R-3 | DPO | ~75d (45–90) | 800–950d (F1') |
| R-4 | payment clearing | receipts/disbursements clear to bank ≤7d; **no residual clearing balances at period close** | 5–19B accumulating (F1b) |
| R-5 | cash position | within sanctioned working-capital facilities | −3B / −9B beyond limits |
| R-6 | net margin | 6–10% | 15.6–17.2% (F2) |
| R-7 | gross margin | 25–40% | ~57% (F2: COGS under-costed) |
| R-8 | inventory turns | 4–6× (DIO 60–90d) | ~2× |
| R-9 | current ratio | 1.3–2.0 | up to 15.3 |
| R-10 | statutory bands | keep v1's proven set (PF/ESI, depreciation %, s.115BAA ~25.17%) | held |
| R-11 | valuation tie | GL Stock Valuation == physical on-hand to the rupee at close | held (keep) |
| R-12 | articulation | BS balances; RE ties to cumulative P&L; double-entry integrity | held (keep) |

**R-13 (reserved): Codex remediation acceptance criteria** — the independent auditor's criteria
(requested in evidence-v2, `bc-external-audit db1f5070`) are adopted verbatim as requirements when
they land. The regenerated books must move Codex off the adverse opinion.

## 2b. Locales (GLOBAL engine, LOCAL packs)

v1 already proved this factorization: the jurisdiction engine's self-test demonstrates the six laws
are **generic over the envelope, not written for India**, with `in.json` as pure data. v2 formalizes
it: **`locales/{in, us, eu-de, …}/`** are data packs — statutory parameters (PF/ESI/GST/TDS or their
local equivalents), tax regime, fiscal-calendar convention, depreciation schedules, labour rules —
consumed by the global jurisdiction/statutory/close engines. A **profile references a locale**
(`mfg-in` = domain(mfg) × locale(in)) rather than fusing it. v2.0 ships `locales/in/` extracted from
v1's `in.json` + statutory data; the engine stays global. (The word *jurisdiction* survives as the
engine's name; *locale pack* is the shipped data unit.)

## 3. Functional requirements

- **FR-1 Apex orchestrator.** A single conductor owns the simulated timeline. It schedules business
  events, drives each through its **full vertical lifecycle**, and runs period-close. No standalone
  timeline-sweep may post documents outside the orchestrator.
- **FR-2 Event lifecycles (vertical integration).** Each business event couples its complete
  consequence chain, e.g. O2C: SO → delivery → invoice → payment per terms (target-shaped) → bank
  receipt → **reconcile → sweep to bank**. P2P, make (MO→WO→labour→FG), payroll, statutory
  remittance, capex/loans, anomalies (planted *through* lifecycles, not as an after-pass).
- **FR-3 Closed-loop target shaping.** The targets in §2 are **input parameters** (per profile).
  The orchestrator shapes rates/timings/costs to land inside bands by construction, and the
  validation suite proves it after the fact. Targets live in a versioned schema, not in code.
- **FR-4 Period-close engine.** Month/FY close as first-class orchestrated acts: GST set-off,
  depreciation, statutory accruals, inventory revaluation (KR-3), tax provision — including
  boundary-straddling documents (KR-12: final revaluation reconciles the *uncapped* GL).
- **FR-5 Adapter boundary (Odoo 19 EE).** All source-system I/O behind one adapter: RPC/odoo-shell
  clients, posting primitives, model knowledge, probes. Core and profiles never import Odoo.
- **FR-6 Event ledger.** Deterministic event IDs; idempotent re-entry (re-running a window is a
  no-op); provenance per document (which event, which release). Replaces v1's ref-string-grep
  idempotency and ad-hoc counter dicts.
- **FR-7 Estate registry.** Each flagship install is a config: profile × adapter × targets × host
  identity (instance, db, uuid). The registry, not code, says what exists where.
- **FR-8 Validation suite as product code.** The gate battery (v1's gates + **new working-capital /
  margin / clearing / cash-facility gates** enforcing §2) runs as: unit tests (CI), acceptance run
  (per release), estate audit (against a live estate).
- **FR-9 Scoped checker service (do not wait for FY-end).** Checks are **temporally scoped services**
  the orchestrator invokes at each close boundary — and that can run standing against a **live
  estate** (D561: estates are maintained lifelong):
  - **Monthly** — hard invariants, fail-fast at every month close: double-entry integrity, valuation
    tie, clearing residual ≈ 0, cash within facilities, statutory postings present.
  - **Quarterly** — drift detection: **trailing-12-month** ratios (DSO/DPO/turns/margins) vs the
    §2 bands (TTM absorbs the seasonality that makes single-month ratios noisy). A drifting target
    is flagged the quarter it starts drifting, not at FY-end.
  - **Annual** — the full benchmark battery + statutory annual acts (provision trueup, s.115BAA
    effective rate, depreciation-to-revenue).
  Rationale from v1: F2 (margins ~2× sector) would have been caught at month ~3 by a quarterly TTM
  drift check; instead it survived 64 months of per-FY batteries and needed an external audit. Gates
  are split GLOBAL (business-semantics checks over trial balances/ratios — portable to any adapter)
  vs SYSTEM (adapter-level probes, e.g. Odoo clearing-account mechanics).

## 4. Non-functional requirements

- **NFR-1 Determinism.** Same (profile, targets, seed, release) ⇒ byte-equivalent business content.
- **NFR-2 Rebuild wall-clock.** ≤ v1 (~10h for 64 months); target <8h.
- **NFR-3 Release-versioned governance.** Development under normal SDLC (branch → CI → review →
  merge). Releases are SemVer git tags. **A governed estate-run pins exactly one release tag** —
  replacing v1's 31-blob manifests and per-fix runbook revisions (r1→r60). Codex reviews release
  candidates against §2/§7, not one-line diffs. The runbook becomes a thin, stable ops document.
- **NFR-4 CI from day one.** Gates: py lint + field-registry harness (KR tests' static side), unit
  tests, knowledge-register tests, no-orchestrator-bypass check (FR-1). Red CI blocks merge.
- **NFR-5 Observability.** Per-event and per-close structured logs; a build emits its own summary
  (counts, targets-vs-actuals) so drift is visible during the run, not at the battery.

## 5. Repo layout (future-ready)

```
bc-demo/
├── docs/                    # requirements (this), architecture, registers, ADR pointers
├── simulator/               # THE PRODUCT (Python package)
│   ├── core/
│   │   ├── orchestrator/    # timeline conductor, event scheduling
│   │   ├── events/          # lifecycle definitions (o2c, p2p, make, payroll, statutory, anomaly)
│   │   ├── close/           # period-close engine
│   │   ├── targets/         # target schema + calibration (the §2 bands as data)
│   │   └── ledger/          # event ledger: determinism, idempotency, provenance
│   ├── adapters/
│   │   └── odoo19ee/        # RPC client, posting primitives, model knowledge, probes
│   ├── engines/             # GLOBAL domain engines (statutory, jurisdiction, loans)
│   ├── locales/
│   │   └── in/              # locale pack: statutory params, tax regime, fiscal calendar (§2b)
│   ├── validation/
│   │   ├── global/          # business-semantics gates (portable): WC/margin/clearing/articulation
│   │   ├── scoped/          # FR-9 monthly/quarterly/annual runners
│   │   └── odoo19ee/        # adapter-level probes
│   └── profiles/
│       └── mfg-in/          # domain content + target values; references locales/in
├── estates/
│   └── pilot-ent/           # registry entry: profile × locale × adapter × targets × host identity
├── ops/                     # deployment (runtime/, infra/), thin stable runbook, host tooling
├── tests/
│   ├── knowledge/global/    # KR-G tests (business/accounting/temporal facts)
│   ├── knowledge/odoo19ee/  # KR-S tests (system quirks)
│   └── ...                  # unit + parity harness
├── legacy/                  # frozen v1 pilots/ (reference only, moved here at STRIP time)
└── .github/workflows/       # CI (NFR-4) + release tagging
```

## 6. Disposition register — repo level (executed only after review)

| asset | verdict | rationale |
|---|---|---|
| `src/` (TS dual simulator: SAP-ECC OData + Salesforce REST, core/event-graph, drizzle) | **STRIP** | A different product; canonical home remains **bc-sdg** (untouched), where the pilot1/ECC path may still depend on it |
| `dist/`, `data/` (generated), `package.json`, `package-lock.json`, `tsconfig.json`, `tools/*.mts` | **STRIP** | Build artifacts + TS-product tooling; regenerable in bc-sdg |
| `pilots/systems/odoo/extract/` (ir-schema extractor, pin c97a495) | **STRIP** | Catalog lane's tool; canonical home remains bc-sdg (their pins reference bc-sdg commits) |
| `pilots/` (everything else, pilot branch tree) | **MOVE → `legacy/`** | v1 of this product; frozen reference + mining source |
| git history (all branches) | **KEEP** | The mining substrate; W1–W22 archaeology stays queryable |

**bc-sdg itself: untouched.** Catalog-lane pins stay valid; ECC/SF simulator undisturbed; any
cleanup there is a separate, unhurried task.

## 7. Disposition register — code level (v1 `pilots/`, 78 files)

Verdicts: **ADOPT** (as-is library) · **ADAPT** (logic survives, new home/shape) · **REWRITE**
(replaced by v2 architecture) · **FREEZE** (reference only, stays in `legacy/`) · **OPS** (moves to
`ops/`, still used to operate the live estate).

| group | files | verdict | notes |
|---|---|---|---|
| Domain engines | `statutory.py`, `jurisdictions/jurisdiction.py` + `in.json`, `verify/_loan_selftest.py`, `verify/_statutory_selftest.py` | **ADOPT** → `engines/` | Proven (21-check + injection self-tests, Codex-reviewed); import as-is, wrap later only if needed |
| Validation suite | `verify/benchmarks.py`, `verify_valuation.py`, `verify_starvation.py` (W22 reset-aware), `verify_world.py`, `verify_lines.py`, `integrity.py`, `coa_coverage.py`, `verify_anomalies.py`, `close_completeness.py`, `world_shape.py`, `invariants.py`, `coverage.py`, `ap_parity.py`, `working_capital.py` | **ADOPT/ADAPT** → `validation/` | Battery core survives; gains the §2 WC/margin/suspense/bank-limit gates; `gate_battery.sh` ADAPTs into the acceptance runner |
| Posting primitives | `scenarios.py` (je(), invoice/bill/CN creators, remittances), `seed.py` (Odoo client, resolve/ensure masters), `statutory_post.py`, `opening_balance.py` | **ADAPT** → `adapters/odoo19ee/` + `core/events/` | The *primitives* survive; their *scheduling* moves to the orchestrator; `C[key]` counter plumbing and ref-grep idempotency replaced by the event ledger (FR-6) |
| Close logic | `month_close.py` (GST set-off, depreciation, revaluation incl. uncapped-GL final pass) | **ADAPT** → `core/close/` | Logic proven through W18–W22; becomes the close engine's first implementation |
| Conductor layer | `forward_build.py`, `bank_recon.py`, `anomalies.py`, `mrp_pass.py`, `sim/dynamics.py`, `master_gen.py`, `stage1_rebuild.sh`, `stage3–6*.sh`, `post_passes.sh`, `build_enterprise.sh` | **REWRITE** | The horizontal timeline-sweeps — the architectural point of v2. Their business *content* (volumes, mix, anomaly types, MO/WO shapes) is mined into `core/events/` + profile calibration |
| Setup/seeding | `setup_config.py`, `setup_bom.py`, `setup_mrp.py`, `setup_shell.py`, `onboarding_shell.py` | **ADAPT** → `adapters/odoo19ee/setup/` | Estate bootstrap (entities, charts, AVCO/anglo config, BoMs, opening stock) becomes the adapter's provisioning module |
| Harness | `tools/field_registry_check.py` + committed registries | **ADOPT** → CI (NFR-4) | Static reference checking becomes a merge gate |
| Runtime/infra | `runtime/` (Dockerfile, compose.enterprise, deploy_runtime, stage_payload, static_sweep), `infra/ec2-userdata*.sh` | **OPS** → `ops/` | Deployed and operates the live estate; versioned with the product |
| Runbook probes | `runbook/classify_addons.py`, `preflight.sh` (stale, TSK-4ab42521), `probe_modules.py`, `probe_l10n_payroll.py`, `rpc_read_proof.py`, `validate_registry.py` | **FREEZE** (preflight: REWRITE in `ops/`) | Probes were one-time evidence acts; a fresh, correct preflight ships with ops |
| Profile data | `profiles/mfg-in/` (master.json, profile.json, manifest/* incl. compose/split/verify_equivalence, anomalies.json, STORYBOOK.md, research/) | **ADOPT** → `simulator/profiles/mfg-in/` | The business world definition; gains the targets/calibration section (FR-3) |
| Docs | `README.md`s, `DESIGN-parent-child-manifest.md` | **FREEZE** | Superseded by docs/ |

## 8. Knowledge registers (the second-system antidote) — two segments

Every hard-won fact becomes an **executable test** before the code that depends on it is written.
Two segments: **KR-G (GLOBAL)** — business/accounting/temporal facts that hold in *any* ERP, shared
across adapters; **KR-S/<adapter>** — one register per adapter for system quirks. A future BC
adapter opens `KR-S/msbc` empty and fills it via doc-mining + probing before code.

### KR-G — global facts (`tests/knowledge/global/`)

| KR | fact | enforced by |
|---|---|---|
| G-1 | Perpetual GL↔physical inventory tie requires an explicit reconciliation act at period close (whatever the system's valuation mechanics) | close-engine test |
| G-2 | Bill-lag documents legitimately post past the FY boundary — the final close-true-up must reconcile the **current** (uncapped) balance, not a period-end snapshot | close-engine test |
| G-3 | Cumulative counters reset per invocation — any multi-window scoring must be reset-aware | validation test |
| G-4 | Anglo-saxon COGS posts at invoice-time document cost — GL drifts from move-cost physical without a bridging mechanism; nets ~0 only for balanced flows | close-engine test |
| G-5 | Sub-annual ratio checks must run on a trailing-12-month basis (single-month ratios are seasonally noisy) | FR-9 quarterly gates |
| G-6 | Searchability/computability of a field is **empirical, not derivable** — probe the live system, commit the answers (13 false positives from derivation in v1) | probe discipline, per adapter |

### KR-S/odoo19ee — Odoo 19 EE quirks (`tests/knowledge/odoo19ee/`)

| KR | fact | enforced by |
|---|---|---|
| S-1 | `stock.valuation.layer` removed; value lives on `stock.move.value`/`stock.quant.value` | adapter valuation reads |
| S-2 | `stock.quant.value` readable but **not searchable/aggregatable** (read_group returns no key) — read + sum in Python | adapter test |
| S-3 | Single-stock-leg tension: category `property_stock_valuation_account_id` serves BOTH mfg produce and buy/sell docs — irreconcilable with one account (Odoo realization of G-1) | close-engine test |
| S-4 | `account.account` codes **root-keyed** in `code_store` JSONB — code lookups need company context | adapter test |
| S-5 | `_ensure_code_is_unique`: create() vs write() **asymmetric** about `defer_account_code_checks` | provisioning test |
| S-6 | Supplier/customer `stock.location` shared (`company_id` NULL); `valuation_account_id` not company-dependent — per-company writes = last-wins | provisioning test |
| S-7 | `mrp_account._post_labour` hard-codes `date=context_today` — re-date via draft → name `/` → repost | make-lifecycle test |
| S-8 | Posted move `date` readonly (UserError) | event-ledger test |
| S-9 | `res.partner.property_product_pricelist` store=false | adapter test |
| S-10 | v19 renames: `payment.ref`→`memo`, `groups_id`→`group_ids`, `product.type`∈{combo,consu,service}+`is_storable`, `uom_po_id` gone, `ir.property` gone, `hr.contract` gone, `sale.order` no `done` | field-registry harness (CI) |
| S-11 | `odoo shell` needs `-c /etc/odoo/odoo.conf`; returns date objects; host modules not importable inside | adapter/ops test |

**Three feeder work items** (build-phase, before adapter code):
1. **v1 mining** — W1–W22 commit history + runbook §15; anything found joins a register as a test.
2. **Systematic doc-mining (operator direction)** — read the Odoo developer documentation *before*
   building: ORM semantics (compute/store/search — the S-2/S-9/G-6 class), accounting + anglo-saxon
   valuation docs (S-1/S-3 class), MRP, `l10n_in`, **release notes 17→18→19** (the S-10 renames come
   straight from release notes v1 never read), plus Odoo's own addon test suites (intended behavior)
   and OCA known-issue trackers. Cheaper knowledge per fact than v1's ~10h-per-lesson probing;
   deliverable = KR-S additions.
3. **Vendor demo-tooling study (read, don't build on).** (a) **Microsoft Contoso Demo Data Tool**
   ([microsoft/BCApps](https://github.com/microsoft/BCApps), MIT) — modular per-domain demo-data
   framework: pattern reference for our `profiles/` internals AND advance `KR-S/msbc` seeding (its
   AL code shows how BC wants documents created/posted — scouting for the doctrinal second
   adapter). (b) **Odoo's own `demo/` data + addon test suites** (in our Enterprise tarball) —
   canonical create/post sequences as Odoo's developers write them → `KR-S/odoo19ee` seeding.
   SAP IDES is proprietary/license-gated — excluded. **Boundary:** these tools populate a plausible
   current-state *snapshot*; they contain no multi-year history, close discipline, or calibration —
   the §11 differentiation. We mine their patterns and posting idioms; we do not adopt their
   skeleton.

## 9. v2.0 acceptance gate

- **A-1 Parity.** v2 rebuilds a 64-month `mfg-in` world that passes **all v1 battery gates** (the
  greens we already achieved: valuation tie, integrity, statutory bands, starvation, anomalies).
- **A-2 Realism.** The same build passes the **new gates** enforcing §2 (R-1…R-9) — the defects F1a,
  F1b, F1', F2 are impossible-by-construction, proven by measurement.
- **A-3 Independent audit.** Codex's remediation acceptance criteria (R-13) are met; opinion moves
  off adverse.
- **A-4 Determinism.** Two builds from the same (profile, targets, seed, release) produce equivalent
  worlds (NFR-1).
- **A-5 Operability.** Full rebuild ≤ 10h (NFR-2); the governed run pins one release tag (NFR-3).

## 10. Migration plan (strangler, no big-bang)

1. **Review this doc → ADR** (product framing, clone-and-strip, registers, release governance).
2. **Execute §6 STRIP** per register; move `pilots/` → `legacy/`; scaffold §5 layout + CI (NFR-4).
3. **Knowledge mining** (§8 first work item) — registers → executable tests.
4. **Core build:** ledger → orchestrator skeleton → O2C lifecycle end-to-end on a scratch DB (ONE
   event through invoice→payment→sweep, proven) → remaining lifecycles → close engine (ADAPT
   month_close) → target shaping.
5. **Parity build** on a fresh estate DB → A-1/A-2/A-4 → release v2.0.0-rc → Codex review (A-3) →
   operator realism review → v2.0.0.
6. v1 `legacy/` stays frozen; bc-sdg untouched throughout.

## 11. Prior art (surveyed 2026-08-10)

Three families exist; none occupies our position:

1. **Vendor demo companies** — SAP IDES/BBP, Microsoft BC's Cronus, Odoo demo data: hand-crafted
   **static snapshots**. Not generated, not multi-year coherent, not calibrated to sector reality,
   not regenerable per domain×locale.
2. **Synthetic ERP data generators** — configurable, seeded, probability-driven master+transaction
   generators. **Table-level output**: rows are fabricated, not posted through the application
   layer, so no ERP validation, no financial-statement articulation, no close discipline.
3. **Academic/ML synthetic ledgers** — VAE journal-entry synthesis, adversarial "deepfake"
   accounting entries (BKPF/BSEG), persona-conditioned LLM transaction generation, AML dataset
   generators. Optimize **statistical fidelity for model training / fraud research** — not
   ERP-native, not statement-coherent over years, not statutory-real, not auditable as books.

**bc-demo's position (no found occupant):** posts through a **live ERP's application layer** (real
validations, real close), produces a **multi-year coherent history**, **closed-loop calibrated to
real sector ratios** (§2), **statutory-real per locale** (§2b), and **gated by an independent
audit** (A-3). The survey also validates the two-stream design: every family above that attempted
realism did it per-system; none separated global business semantics from system realization.

Sources: [SAP IDES vs BBP](https://community.sap.com/t5/enterprise-resource-planning-blog-posts-by-members/sap-demo-systems-ides-ecc-vs-bbp-s-4hana/ba-p/13422550) ·
[ERP synthetic data generator (probability-driven)](https://github.com/scripts-and-tables/erp-synthetic-data-generator) ·
[Synthetic data for ERP systems](https://www.meegle.com/en_us/topics/synthetic-data-generation/synthetic-data-for-erp-systems) ·
[VAE journal-entry generation](https://onlinelibrary.wiley.com/doi/10.1002/isaf.70005) ·
[Adversarial learning of deepfakes in accounting](https://arxiv.org/pdf/1910.03810) ·
[Synthetic financial transaction benchmarks](https://arxiv.org/pdf/2412.14730) ·
[PersonaLedger (LLM + rule-grounded feedback)](https://arxiv.org/pdf/2601.03149) ·
[Tide AML dataset generator](https://arxiv.org/pdf/2603.01863) ·
[Synthetic data applications in finance](https://arxiv.org/pdf/2401.00081)
