---
title: "Legacy Metric Contract Authoring Door — guard study (read-only)"
description: D429 Step 3. A read-only audit of every path that creates/updates legacy contract.metric_contract* / Metric Contract envelopes outside the MCF-governed path, classified into runtime readers, historical/seed scripts, admin/API authoring endpoints, tests, and MCF materialization target. Confirms which paths still accept free fields_used / free canonical_contract. Recommends a narrow guard that blocks new legacy MC authoring unless maintenance-approved, while preserving runtime reads and the future MCF materialization writer, without wiping data and without implementing D430/D431. Authorizes no code, schema, DB, or service change — held.
status: draft
date: 2026-06-07
project: bc-core
domain: contracts
subdomain: metric-authoring
focus: governance
---

# Legacy Metric Contract Authoring Door — guard study (read-only)

> **What this is.** D429 **Step 3**. A read-only audit of every path that can create/update a legacy `contract.metric_contract*` / Metric Contract envelope outside the MCF-governed path, plus a narrow guard proposal. It **authorizes nothing** — no code, schema, DB, or service change; no data wipe; D430/D431 not implemented; MCF materialization stays paused.
>
> **Method.** Three read-only subagents over `bc-core` (admin/API + service write paths; seed/historical scripts; runtime readers + MCF target + tests), file:line evidence retained. Live counts: legacy `contract.metric_contract` = **1022 versions / 780 parents / 2 active**.
>
> **Decision status (2026-06-07): LOCKED.** Recorded in the Step-3 ADR. **G2 only** — a repository-layer refuse-to-author guard at the legacy MC *create* choke point; **no G3 DB trigger** this step; escape = env flag **+** a logged `maintenanceApproval`/rationale (both); **block create-authoring only** (parent + version) — activation is NOT gated here (Step 4 owns activation / fail-open gates); preserve runtime reads, audit-metadata updates, tests/fixtures (test env exempt), and the future MCF materialization writer. Implementation deferred to a later DBCP; MCF materialization remains paused.

---

## Headline

**The legacy door is open through two write surfaces, both of which still accept free `co_bindings` (free `canonical_contract`, free `fields_used`).** The narrow fix is a **repository-layer refuse-to-author guard, env-gated and default-blocked** — mirroring the D429 Step-1 `BCCORE_ALLOW_CONTRACT_BODY_REWRITE` pattern — placed at the single choke point through which all legacy metric writes pass. It blocks **new** legacy authoring while leaving runtime reads, audit metadata, MCF `mcf.*` writes, and the (not-yet-built) MCF→`contract.metric_contract` materialization writer untouched.

This is a **door guard, not a shape fix.** The shape (free `co_bindings`) is corrected later by D430 (canonical concept identity) + D431 (observation concept identity) + the future MCF materialization writer. Until those land, the legacy free-shape envelope is still the only metric-authoring shape, so tightening the *schema* now is premature — we close the *door* instead.

---

## The free-fields finding (the operator's specific question)

**Yes — every legacy create path accepts free fields, with no create-time grounding.** `metric-v1.schema.json:52-66`:

```json
"co_bindings": { "type": "array", "minItems": 1, "items": {
  "required": ["canonical_contract", "role"], "additionalProperties": false,
  "properties": {
    "canonical_contract": { "type": "string" },        // required, NO enum/pattern/existence
    "role": { "type": "string", "enum": ["primary","secondary","reference"] },
    "fields_used": { "type": "array", "items": { "type": "string" } }  // optional, NO constraint
  } } }
```

- `canonical_contract` — any string; no check that the CC exists.
- `fields_used` — any string array; no check the fields exist in the CC.
- The only downstream check is the **activation** integrity gate (`contract.service.ts:462-477`), which fires on state transition and only blocks if variable bindings are *unresolved* — it does **not** validate field existence or concept relatedness. An AP field bound to an AR invoice CC passes every gate (the audit's X-evidence).

---

## Path inventory (the five buckets)

| # | Bucket | Path | file:line | Writes | Free fields? | Guard disposition |
|---|---|---|---|---|---|---|
| 1 | **Runtime readers** | metric evaluation `loadEnvelope → normalizeEnvelope → evaluate` | `metric.service.ts:118,172,815-871`; `metric-evaluation-engine.service.ts:165-203` | **READ only** (no INSERT/UPDATE) | n/a | **PRESERVE** |
| 3 | **Admin/API authoring** | `POST /contracts/:id/versions` → `createVersion` (category=metric) | `contract.service.ts:311-396` | new version (envelope body) | **YES** (meta-schema only) | **BLOCK** (the door) |
| 3 | Admin/API authoring | `POST /contracts` → `createContract` | `contract.service.ts:76-120` | new parent contract | n/a (parent) | **BLOCK** (paired) |
| 3 | Admin/API authoring | `activate` → `transitionState` | `contract.service.ts:421-596` | status → active | n/a | gate exists; **see note** |
| 3 | Admin/API (non-authoring) | metric-catalog `POST /metric-catalog/definitions` | writes `metric.metric_definition` only | not `contract.metric_contract*` | n/a | out of scope |
| — | **Repository choke point** | `createMinimalMetricContract()` | `contract-metrics.repository.ts:139-158` | new MC parent (+ tags) | **YES** | **BLOCK** (primary guard site) |
| — | Repository (metadata) | `formula-audit` UPDATE (audit_status_code, …) | `formula-audit.service.ts` | metadata UPDATE only | n/a | **PRESERVE** (not authoring; Step-1 allows metadata) |
| 2 | **Historical/seed scripts** | `d225-generate-phases-4-7.js` | `scripts/d225-generate-phases-4-7.js:~280-286` | **new MC + metric_binding** | **YES** | **BLOCK** — *currently UNGUARDED* |
| 2 | Historical/seed scripts | `generate-metric-contracts.ts` (full-registry seed) | `src/registry/seed/generate-metric-contracts.ts` | new MC envelopes | **YES** | **BLOCK** (env-gate) |
| 2 | Historical scripts (body rewrite) | `migrate-metric-contract-json.js`, `migrate-formulas-d315.mjs`, `finance-secondary-bindings.js`, +4 | scripts/* | UPDATE body | n/a (rewrite) | already **guarded** (Step-1 `BCCORE_ALLOW_CONTRACT_BODY_REWRITE`) |
| 2 | Historical (SQL) | `enrich-ar-metric-contracts.sql` | scripts/* | UPDATE body | n/a | already **retired** (D429 guard block) |
| 4 | **Tests** | `metric.repository.dual-write…spec`, `…progression-synthesis…spec`, readiness-ledger `insertMcFixture` | src/boundary/*, src/registry/* | new MC via **direct repo** | n/a | gated path must exempt test env |
| 5 | **MCF materialization target** | M12.5 `runMaterialization` / `mcf-cert-writer` | `metric-authoring-materialization.service.ts:22-25`; `mcf-cert-writer.service.ts:797-840` | writes **`mcf.*` only** (HA-1) | n/a | **PRESERVE** (different schema) |
| 5 | **Future MCF writer** | MCF→`contract.metric_contract*` (Step-5 synthesizer) | **does not exist yet** | (planned) | — | **PRESERVE-FUTURE** (authorized path) |

**Note on activation:** `transitionState→active` activates an *existing* draft; it does not author a new envelope. Blocking `createVersion`/`createMinimalMetricContract` stops new legacy drafts from existing in the first place, so activation needs no separate block for the Step-3 goal. (Whether to also freeze activation of the 2 currently-active / any draft legacy MCs is a smaller, separable question — flagged, not required here.)

---

## Recommended narrow guard strategy

**Primary — G2: repository-layer refuse-to-author guard, env-gated, default-blocked.** Place the check at the single choke point all legacy metric *creates* pass through — `ContractMetricsRepository.createMinimalMetricContract()` and the metric branch of the version writer (`contract-version.repository` create, when the parent `category='metric'`). Refuse the write unless an explicit maintenance approval is present:

- default: **blocked** with a clear error citing D429 Step 3.
- escape: `BCCORE_ALLOW_LEGACY_METRIC_AUTHORING=1` (mirrors the Step-1 script guard), optionally paired with a logged `maintenanceApproval` rationale.
- this covers the **API door, the scripts (incl. the unguarded `d225`), and direct seed inserts** in one place — the narrowest effective surface.

**Why repository-layer, not controller-layer:** a controller/service-only guard (G1) misses the scripts and seeds that call the repo directly. The repo method is the true choke point.

**Optional defense-in-depth — G3: `BEFORE INSERT` trigger on `contract.metric_contract(_version)`** with a session-GUC escape (`SET LOCAL bc.allow_legacy_metric_authoring='1'`), exactly mirroring the Step-1 immutability triggers. Catches even raw SQL. Heavier; can be a later layer once the repo guard is proven.

**Preserve, explicitly:**
- **Runtime reads** — untouched (read path performs no inserts).
- **`formula-audit` metadata UPDATEs** — untouched (not authoring; metadata-only; consistent with Step-1 which allows metadata changes).
- **MCF `mcf.*` writes** — untouched (different schema namespace).
- **Future MCF→`contract.metric_contract` materialization writer (Step 5)** — when built, it is an **authorized writer** that passes the guard via the env flag / GUC. The guard distinguishes *legacy ad-hoc authoring* (blocked) from the *governed MCF materialization writer* (permitted) — it is not keyed to the table alone.

**Tests:** the gated path exempts the test environment (e.g. `NODE_ENV==='test'` or the same env flag set in test setup) so the direct-repo fixtures (`insertMcFixture`, dual-write/progression-synthesis integration specs) keep working. (The contract-version-immutability integration spec only *reads* an existing active MC — unaffected.)

---

## What NOT to do (per operator scope)

- **No schema tightening** to reject free `fields_used`/`canonical_contract` — that is D430/D431 + the future materialization writer, not Step 3. Doing it now would break the only metric-authoring shape that exists.
- **No route/endpoint removal** — too blunt, harder to reverse, breaks tooling/tests.
- **No data wipe** — the 1022 legacy versions / 2 active stay as preserved state.
- **Do not resume MCF materialization;** do not implement D430/D431.

---

## Foundation gate (for the eventual guard)

- **Repair location:** the **contract-authoring surface** — governance of *writes* to `contract.metric_contract*`. Closest to **B** (contract-semantics governance) / the publication gate; the mechanism is an admission gate on the authoring path, not a change to evaluation/storage/read.
- **Invariant alignment:** preserves "reads do not trigger evaluation" (read path untouched); does not compensate for the upstream semantic gap (X2) at a lower layer — it simply **stops new ungrounded envelopes from being created** while the real shape fix (D430/D431) proceeds upstream. No DB row edits; no data mutation.
- **One-then-many / SERVICES-ONLY:** the guard lives in the service/repository layer (and optionally a DB trigger), not in ad-hoc scripts.

---

## Relationship to the D429 sequence

Step 1 (contract-version immutability) ✅ applied. Step 2 canonical identity (D430) ✅ decided; Observation identity (D431) ✅ decided. **Step 3 (this study)** closes the *authoring door* so no new ungrounded legacy metric envelopes are created while D430/D431 implementation and the future MCF materialization writer (Step 5) are built. Step 4 (fix fail-open activation gates X5/X4) and Step 5 (resume materialization) follow. The legacy free-shape door and the new concept-identity shape are complementary: Step 3 stops the bleeding; D430/D431 + MCF supply the correct forward shape.

## Decisions taken (locked 2026-06-07)

1. **G2 only — repository-layer refuse-to-author guard** at the legacy Metric Contract *create* choke point (`createMinimalMetricContract` + the metric branch of the version create). **No G3 DB trigger in this step.**
2. **Default = blocked. Escape requires the env flag (`BCCORE_ALLOW_LEGACY_METRIC_AUTHORING`) PLUS an explicit, logged `maintenanceApproval`/rationale** — both, not the flag alone.
3. **Block create-authoring only** — parent + version creation through the legacy path. **Activation is NOT gated here; Step 4 owns activation / fail-open gates (X5/X4).**
4. **Preserve** runtime reads, audit-metadata UPDATEs, tests/fixtures (test env exempt), and the future MCF materialization writer (an authorized writer that passes via the escape). The guard distinguishes legacy ad-hoc authoring (blocked) from the governed MCF materialization writer (permitted) — not keyed to the table alone.

Recorded in the Step-3 ADR; implementation (the repository guard) is deferred to a later DBCP. No code/schema/DB change here. MCF materialization remains paused.

## Scope guard

Read-only audit. No code, schema, DB, service change, PR, or panel. No data wipe. Runtime objects in `tbc_sandbox1_dev` not queried. MCF materialization remains paused. This memo recommends; the operator locks; only then is a guard DBCP drafted.
