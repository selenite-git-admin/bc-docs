---
uid: POV-reader-governance-first-principles-2026-07-01
title: "UniBAT Reader — First-Principles Governance PoV (through the Connector/Connection lens)"
description: "A grounded point of view on the Reader as an architectural corner-piece: its five-layer physical topology (Connector → Connection → Reader → Flavor → Binding), the multi-tenancy reconciliation (flavor.connection_id is vestigial; connection resolves per-tenant at admission), a governance-maturity scorecard against BCF/MCF, the missing Reader requirements grammar, the target lifecycle state machine, and an honest audit of the reactive DEC-17112b work. Requirements-first, not reactionary."
status: draft
authority: study
date: 2026-07-01
project: bc-core
domain: readers
---

# UniBAT Reader — First-Principles Governance PoV

## 0. Why this document exists

We built the Reader authoring surface (DEC-17112b) **reactively** — to rescue the pilot AR chain — and crystallized a flavor-topology policy (P-F1..P-F8) from the mess we found. That is not the requirements-first, ground-up governance BCF and MCF received. The Reader is the platform's **admission boundary** (repair-location A) and the *only* place where physical reality — Connectors, Connections, credentials, tenancy — meets the contract chain. Once tenants are in production, altering this structure is expensive. This PoV is the deliberate study we skipped: grounded in the docs, read through the Connector/Connection lens, measured against the platform's own governance bar, and honest about what the reactive work got right and wrong.

**Grounding:** docs (`connectors-and-readers.md`, `reader-creation.md`, `the-evaluation-boundaries.md`, `the-invariants.md`, ADR-771baf, ADR-17112b), the `runtime.*` schema, and live `bc_platform_dev` data (2 connectors, 3 connections, 143 admission_runs). Two research sweeps (architecture + BCF/MCF governance patterns) underpin it.

## 1. The five-layer topology (grounded)

The Reader is **not** the three layers my reactive study modeled. It is five, spanning physical→semantic:

| Layer | Scope | Owns | Tenancy |
|---|---|---|---|
| **Connector** (`runtime.connector` + protocol + provenance) | platform, source-system-agnostic *driver* | protocol family, `executor_class`, auth methods, capability, provenance | none |
| **Connection** (`runtime.connection` + config + check) | **tenant-owned instance** | endpoint URI, credentials (`authentication_json`, off-DB secret surface), environment, health checks | **tenant** (the *only* tenant-scoped layer) |
| **Reader** (`runtime.reader`) | platform, subfunction | the admission boundary for a subfunction; schedule/retry/circuit-breaker (`operational_config_json`) | none |
| **Flavor** (`runtime.reader_flavor`) | platform, `(source_system, scenario)` | how to read that subfunction from one system; → Connector (protocol) | none (see §2) |
| **Binding** (`reader_binding` AC + `reader_observation_binding` OC) | platform, per source entity | which SC/AC/OC versions govern each entity | none |
| *execution:* **admission_run** | per run | records observed/admitted/rejected + which flavor/connection/contract | records tenant |

The UniBAT commitments (`connectors-and-readers.md`): **Universal** (one Reader pattern, all systems), **Business-Aware** (SO keyed by Business Field codes, not source fields), **Transactions** (one transaction → one Source Object), **Reader-not-Transformer** (admits, never derives). Specialization lives in Connector (protocol) + Flavor (system) — never the Reader.

## 2. The multi-tenancy reconciliation (the deepest finding)

**The reactive model and the live schema appeared to contradict on where tenancy binds. The docs resolve it — in P-F6's favor — and expose an unbuilt mechanism.**

- **Intended design (docs):** `reader-creation.md` §Boundary: *"The Tenant Connection is paired with the Reader Flavor at runtime; the Reader is platform-scoped, the Connection is tenant-scoped."* So the Flavor is tenant-agnostic; the tenant's Connection is resolved **per-tenant at admission time**. This is exactly P-F6.
- **Implemented reality (drift):** `reader-runtime.service.ts:111` resolves the connection as `getConnection(flavor.connectionId)` — a **fixed** connection pinned on the flavor. There is **no per-tenant resolution**. Live: 54 of 55 flavors carry a `connection_id`.
- **Consequence:** with no runtime mechanism to resolve "this tenant's connection for this flavor," the only way to serve a second tenant was to **clone the flavor per tenant** — which is exactly the `apex-*` flavors I called "leakage." They were a *workaround for a missing mechanism*, not mere sloppiness.

**Reconciliation (grounded PoV):**
1. **P-F6 is correct and matches the intended UniBAT design** — the Flavor is system-scoped and tenant-agnostic; tenancy lives in the Connection.
2. **`reader_flavor.connection_id` is vestigial** — the same single-pointer anti-pattern as the now-deprecated `observation_contract_id`. It should be removed and replaced by a runtime **connection resolver**: `(tenant, source_system, environment) → connection`, recorded on `admission_run.connection_id`.
3. **The Flavor legitimately keeps `connector_id`** (which *protocol driver*) — that's platform/agnostic. Connection ≠ Connector: the driver is shared; the credentialed instance is per-tenant.
4. **A latent schema question to settle:** `runtime.connection` lives in the **platform** DB, yet ADR-771baf says credentials live **tenant-side** (`operational.connection`, platform never writes tenant DB). The live `runtime.connection` rows (apex-sdg-odata, sap-ecc-simulator) suggest a dev shortcut. The resolver design must state which is authoritative — platform `runtime.connection` (with `tenant_id` filter) or a tenant-side connection read.

**This is the corner-piece decision.** Until the per-tenant connection resolver exists, "one system-agnostic reader serving many tenants" is aspirational — the runtime can't do it. This belongs in a Reader ADR (call it **#R5 — tenant connection resolution**) and gates any real multi-tenant pilot.

## 3. Governance-maturity scorecard (Reader vs BCF/MCF)

The BCF/MCF sweep extracted the eight elements that make those surfaces well-governed. The Reader, as it stands:

| # | Element (BCF/MCF standard) | Reader today | Grade |
|---|---|---|---|
| 1 | Explicit lifecycle states (draft→review→approved→active→superseded, schema+trigger) | only `draft/active/deprecated`; no review/approved; no substrate triggers | 🔴 |
| 2 | Gated transitions, fail-closed, evidence-bearing | `activateFlavor` gates on contract-resolvability only; no evidence persisted; **blind to connector/connection** | 🟠 |
| 3 | Immutable versioning (append-only; supersede, don't edit) | `reader_version` NULL; no flavor/reader versioning | 🔴 |
| 4 | Activation gates with evidence + break reasons | resolver emits 5 break codes (good); nothing persisted; contract-only | 🟠 |
| 5 | Authoring service, not CRUD (cert-verified) | `ReaderAuthoringService` built — but no `certification_record`, no actor/authz, no panel | 🟡 |
| 6 | Supersession/retirement with fail-closed consumer guard | `archiveFlavor` exists; **no consumer guard** (stranded bindings/admission_runs unchecked) | 🟠 |
| 7 | Cross-framework boundary (read-only) | reads SC/AC/OC read-only | 🟢 |
| 8 | Requirements grammar ("what must this express") | **none** — P-F1..P-F8 is a reactive fragment, not a requirements contract | 🔴 |

**Six of eight red/orange.** BCF's `RegistryAuthoringService` verifies a `certification_record_id` on every state change; MCF's M12 panel runs three-model consensus with grounded transcripts and PE-MC-1..10 evidence-bearing gates before `review→approved`. The Reader has none of that rigor. It is roughly **one-third governed**.

## 4. The Reader lifecycle (current vs target)

**Current:** each layer carries a bare `status_code` (`draft/active/deprecated`) and `archived_at`. Readers were bulk-seeded straight to `active` (P5 defect). There is no review/approved stage, no gated transition with evidence, no versioning, no supersession model. `operational_config_json` carries schedule/retry/circuit-breaker but no lifecycle governs them.

**Target (BCF/MCF parity), per layer:**

```
Connector : registered → validated(protocol reachable) → active → deprecated
Connection: draft → health-checked(connection_check pass) → connected → rotated/expired → archived
Reader    : draft → (flavors authored) → activatable? → active → superseded → retired
Flavor    : draft → chain-resolvable? + connector/connection wired? → active → superseded → archived
Binding   : bound(version-safe) → active → unbound(soft) → superseded
```

Each transition to `active` is a **fail-closed gate that emits evidence** (PASS/REJECT/OPERATOR_REVIEW + break reasons, persisted), mirroring PE-MC. Supersession runs through a **consumer guard** (a flavor/reader cannot be retired while active admission_runs or downstream CMs depend on it — the DEC-9d27a9 pattern applied to admission). Versioning is append-only (`reader_version`, `flavor` version), correction-by-supersession, never in-place edit (Invariant III).

The **documented** activation gate already exceeds my reactive one: `reader-creation.md` §Quality Gates specifies **CR-QG-RDR-003 (seven chain-integrity checks)** including *"Flavor has Connector (active)"* and Connection wiring — which my `ReaderChainResolver` **omits**. The target gate = CR-QG-RDR-003 ∪ chain-resolvability ∪ connection-health, with evidence.

## 5. The missing piece — a Reader Requirements Grammar

BCF and MCF each have an explicit "what this object must express" contract (BCF's PE1-PE6 publication-eligibility; MCF's MC identity tuple + formula authority). **The Reader has none.** We never debated its requirements. Grounded in the invariants + the UniBAT commitments, a Reader (and each layer) must express and guarantee:

- **R1 — Identity (Invariant IV):** a Reader is exactly `(source_category, function, subfunction)`; a Flavor exactly `(reader, source_system, scenario)`; a Binding exactly `(flavor, source_entity, environment) → {AC, OC} versions`. No identity may encode a table, a tenant, or a metric.
- **R2 — Ordering (Invariant II):** a Reader emits **Source Objects only**, never Canonical Objects. Every SO carries its Reader + Binding + SC/AC/OC versions as provenance.
- **R3 — Non-replayability (Invariant V):** every invocation is one `admission_run` producing new SOs with distinct identities; re-running never recreates prior objects.
- **R4 — Evidence (Invariant VI):** admitted **and rejected** observations both emit Evidence; counts (`observed/admitted/rejected`) are recorded, not inferred.
- **R5 — Resolvability (closure rule):** a Flavor activates only when every bound entity resolves `SC→AC→OC→CC` **and** the flavor has an active Connector **and** a resolvable tenant Connection. (Contract chain ∧ physical chain.)
- **R6 — Business-awareness:** SOs are keyed by Business Field codes, not source field names (portability: swap Connector+Flavor, keep SC/OC/CC).
- **R7 — Idempotency/resumability (#R2, unbuilt):** a partial admission_run must be re-admissible without double-emitting SOs.
- **R8 — Tenancy:** system-agnosticism holds — one Reader/Flavor serves all tenants; the tenant Connection is resolved per run, never pinned to the Flavor (§2).
- **R9 — Connectivity health:** activation and scheduled runs require a `connection_check`-passing Connection; a dead connection blocks admission, surfaced as evidence, not a silent failure.

This grammar is the artifact to author and lock **first** — everything else (lifecycle, gates, policy) derives from it.

## 6. Honest audit of the reactive work (DEC-17112b + P-F1..P-F8)

**Right:** the four-layer model + per-entity OC binding (Change A) is correct and doc-aligned; the version-safe binding pattern is sound; the `ReaderChainResolver` + break-reason taxonomy is the right *shape*; P-F1/P-F4/P-F7 (identity, one-flavor-many-entities, derived names) are correct; the authoring-service-not-CRUD direction is right.

**Partial / to revise:**
- **P-F6** is directionally right (tenancy not in the flavor) but **incomplete** — it declared the rule without building the connection-resolution mechanism that makes it real; `flavor.connection_id` still needs retirement (§2).
- **The activation gate is under-scoped** — contract-resolvability only; it **ignores Connector and Connection** that the *documented* CR-QG-RDR-003 already requires. A flavor can pass my gate and still be physically unable to read (our `sap-ecc` flavor is `active` with no connector/connection — active-but-unconnectable).
- **No lifecycle, no versioning, no evidence persistence, no consumer guard, no requirements grammar** (§3–§5).

**Wrong assumption corrected:** "greenfield, safe to wipe." There are **143 admission_runs** + real connections. A wipe must be a governed retirement with a consumer/history guard, not a delete.

## 7. Recommendation — requirements-first, then rebuild

Do **not** wipe/rebuild yet. Sequence:

1. **Author + lock the Reader Requirements Grammar** (§5) — the missing contract. Short ADR.
2. **Decide the multi-tenancy model** (§2) — ADR #R5: retire `flavor.connection_id`, build the `(tenant, source_system, environment) → connection` resolver, settle platform-`runtime.connection` vs tenant-side authority. *This gates any multi-tenant pilot.*
3. **Define the lifecycle state machine + evidence-bearing gates** (§4) to BCF/MCF parity — adopt CR-QG-RDR-003 ∪ chain-resolvability ∪ connection-health; persist gate evidence; add the supersession consumer guard.
4. **Re-examine P-F1..P-F8** against 1–3 — keep P-F1/P-F4/P-F7, complete P-F6 with the resolver, fold the rest into the lifecycle.
5. **THEN the governed wipe + rebuild** — retire the seed readers through a guarded retirement op; rebuild AR (and each in-scope subfunction) fresh through the now-complete surface, on the locked requirements.

Pilot note: the AR reader is `active` at contract-chain level (this session) but **not physically runnable** until #R5 (connection) lands — so P3/P4 depend on step 2 regardless.

## 8. Open questions for the operator

1. **Connection authority:** platform `runtime.connection` (tenant_id-filtered) or tenant-side `operational.connection` per ADR-771baf? (Affects the resolver.)
2. **Multi-tenant timing:** is the pilot single-tenant (`pilot1` only — flavor.connection_id tolerable short-term) or must #R5 land before pilot?
3. **Lifecycle depth:** full BCF/MCF-parity state machine (review/approved + certification + panel) for Readers, or a lighter operator-witnessed gate (no AI panel — Readers are infra, not semantic authorship)?
4. **Requirements scope:** is R1-R9 the right set, or are there admission guarantees (ordering across entities, cross-entity dedup, watermark/incremental) we must add before locking?
