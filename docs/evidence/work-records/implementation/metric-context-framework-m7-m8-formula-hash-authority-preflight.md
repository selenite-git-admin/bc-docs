---
uid: metric-context-framework-m7-m8-formula-hash-authority-preflight
title: MCF M7/M8 Formula AST + Hash/Signature Authority Preflight
description: Docs-only preflight that frames the next substrate/service gate after M4 (lifecycle certification live). M4 ships the McfHashComputer interface + MockMcfHashComputer (with substrate-compatible `mcf-mock-v1` marker post-PR #108) + a production guard that rejects `mcf-mock-*` and legacy `mock-*` markers — so the M4 service is operationally dormant for real-metric authoring until a real implementation lands. This preflight covers the formula AST authority service (M7 per build plan) + package signature hash service (M8) + identifies whether to split or combine them into one DBCP. It enumerates the 6 hash columns on mcf.metric_contract (formula_intent_hash, variable_binding_set_hash, filter_set_hash, identity_tuple_hash, package_signature_hash, hash_algorithm_version) that the M3 state-transition trigger requires non-null at review→approved; the canonicalization surface MCF §7-§8 specifies for each; the M7/M8 ownership boundary options; the algorithm-version naming discipline already enforced by substrate CHECK `^mcf-[a-z-]+-v[0-9]+$`; the production guard relationship to mock detection; risks; and 8 operator decisions required before any M7/M8 DBCP can open. Recommendation: **combined M7/M8 DBCP** to keep canonicalization rules + algorithm-version discipline + interface contract under a single governance document, since the McfHashComputer.computeAllForApproval interface returns all 6 hashes from one call regardless of internal ownership split. Docs-only. No bc-core edits. No DDL. No MCF metric contracts. No M11+ panel work. No BCF data touches.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m7-m8-formula-hash-authority-preflight
---

# MCF M7/M8 Formula AST + Hash/Signature Authority Preflight

## 1. Scope and grounding

### 1.1 Purpose

Frame the next substrate/service gate in the MCF arc now that M4 (lifecycle certification + transition authority) is live and verified. M4 declares the `McfHashComputer` interface but ships only `MockMcfHashComputer`. The real implementations — the formula AST normalizer + identity hasher (per MCF §7-§8) and the composite package signature hasher (per MCF §8.7) — are the build-plan M7 and M8 gates. This preflight scopes those gates, identifies the open design questions, and recommends whether to open them as one combined DBCP or as two sequential DBCPs.

This is a **docs-only preflight**. It does not write a DBCP. It does not apply DDL. It does not edit bc-core. It does not author M11+ panel work. It enumerates what an operator-approved DBCP would need to decide.

### 1.2 What this preflight is and is not

| | This preflight |
|---|---|
| Is | A docs-only framing of the M7/M8 scope + open questions + operator decisions + DBCP-shape recommendation |
| Is | The formal record of "M4 is live but operationally dormant; here is the bounded path to first-real-metric capability" |
| Is not | The M7 DBCP itself (next gate; designs the formula AST substrate + service + canonicalization implementation) |
| Is not | The M8 DBCP itself (next gate; designs the composite hash service + algorithm-version registry) |
| Is not | An M2/M3/M4 substrate change — those gates are closed and live |
| Is not | A bc-core code edit |
| Is not | A real-metric authoring action — substrate stays empty pending M11+ panel |

### 1.3 Source documents consumed

| Source | Role | Commit / location |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority | `bc-docs-v3/docs/adrs/ADR-c3e57f.md` |
| MCF requirements §7 (Formula AST) | Closed AST node taxonomy v1, forbidden patterns, immutability, type promotion, executable-deterministic interpretation | `metric-context-framework-requirements.md` §7 |
| MCF requirements §8 (Normalization + identity hash) | 7 normalization rules, structural sort key, hash construction, algorithm versioning, §8.7 composite package signature hash | same doc §8 |
| MCF requirements §12 (Self-Verification Fixtures) | How fixtures bind to `package_signature_hash`; stale-fixture rule (§12.7) | same doc §12 |
| MCF requirements §13 (PE-MC checks) | PE-MC-5 (Formula AST validity), PE-MC-10 (Self-verification fixture passes) — the gates that downstream M9/M10/M12 enforce against M7/M8 outputs | same doc §13 |
| MCF build plan §4.3 Gates M7 + M8 | T-shirt sizing (M7=XL, M8=S), inputs, dependencies, primary risks | `metric-context-framework-build-plan.md` |
| M2 DBCP + live schema | Hash columns on `mcf.metric_contract`: 6 hash columns (5 hash + 1 algorithm-version marker), nullable in M2, NOT-NULL enforced at `review → approved` by M3 trigger | `metric-context-framework-m2-identity-substrate-dbcp.md` + `bc-core/src/database/schema/mcf/metric-contract.ts` |
| M3 DBCP + live trigger | M3 state-transition trigger requires all 6 parent hash columns non-null at `review → approved` | `metric-context-framework-m3-lifecycle-substrate-dbcp.md` + live trigger `mcf.fn_mcv_state_transition_check` |
| M4 DBCP §7 + live service | `McfHashComputer` interface declaration; `MockMcfHashComputer`; §7.5 production guard | `metric-context-framework-m4-lifecycle-certification-dbcp.md` (3983530) + `bc-core/src/registry/mcf/mcf-hash-computer.{interface,mock}.ts` + `mcf-cert-writer.service.ts` |
| M4 apply closeout | Confirms M4 service live; `MockMcfHashComputer` returns substrate-compatible `mcf-mock-v1` (per PR #108); production guard rejects `mcf-mock-*` + legacy `mock-*` | `mcf-m4-ddl-apply-closeout.md` (`c2bc3fc`) |
| Live `mcf.metric_contract` CHECK | `mc_hash_algorithm_version_chk` regex `^mcf-[a-z-]+-v[0-9]+$` (verified empirically against bc_platform_dev) | `bc-core/docker/redesign/04-mcf-substrate.sql` + live constraint definition |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — read-only this session |
| No DDL applied or drafted | ✓ — docs-only |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No certification rows written | ✓ — M4 service operationally dormant |
| No BCF data touched | ✓ — `concept_registry.*` unchanged |
| No M11/M12 panel work | ✓ — gated on M9/M10 which gate on M7/M8 |
| No M5 panel substrate work | ✓ — not in scope |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |
| No new M7 or M8 DBCP opened | ✓ — preflight only |

---

## 2. Current live substrate/service state after M4

### 2.1 What is live

After PR #109 closeout (`c2bc3fc` on bc-docs-v3; bc-core main `2a603ce`):

**Substrate (10 `mcf.*` tables, all empty):**

| Table | Origin | Row count | Hash columns |
|---|---|---|---|
| `mcf.metric_contract` | M2 | 0 | **6 hash columns nullable** until first `review → approved`: `formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash`, `package_signature_hash`, `hash_algorithm_version` |
| `mcf.metric_contract_version` | M2 | 0 | — |
| `mcf.metric_variable_binding` | M2 | 0 | — |
| `mcf.metric_filter_clause` | M2 | 0 | — |
| `mcf.metric_computed_dimension_ref` | M2 | 0 | — |
| `mcf.metric_contract_revision` | M3 | 0 | — |
| `mcf.metric_supersession` | M3 | 0 | — |
| `mcf.certification_record` | M3 cert-amendment | 0 | — |
| `mcf.metric_publication_eligibility_result` | M4 | 0 | — |
| `mcf.metric_cert_writer_idempotency` | M4 | 0 | — |

**Seeds on shared substrate:**

| Table | Mcf rows |
|---|---|
| `contract.framework_policy` | 1: `mcf_v1` / `1.0.0` |
| `contract.operator_confirm_rule` | 2: `mcf_metric_transition_approved_to_active` + `mcf_metric_supersede_active_to_superseded` (both `action_code='require_operator_confirm'`) |

**Service layer (bc-core main `2a603ce`):**

| Symbol | Location | Status |
|---|---|---|
| `McfCertWriterService` (5 methods) | `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` | Live; integration-tested 7/7 PASS |
| `McfHashComputer` interface | `bc-core/src/registry/mcf/mcf-hash-computer.interface.ts` | Live; declares `computeAllForApproval(input: { metricContractUid }): Promise<ParentHashes>` returning the 6 hashes |
| `MockMcfHashComputer` | `bc-core/src/registry/mcf/mcf-hash-computer.mock.ts` | Live; returns `hashAlgorithmVersion='mcf-mock-v1'` (substrate-compatible per PR #108) |
| `assertProductionHashAlgorithm` guard | inside `McfCertWriterService.approveForActivation` | Live; rejects `startsWith('mcf-mock-')` or `startsWith('mock-')` when `NODE_ENV === 'production'` (defense-in-depth for legacy markers) |

### 2.2 The 6 hash columns on `mcf.metric_contract` — substrate-level

```sql
-- M2 DDL (docker/redesign/04-mcf-substrate.sql) — live columns
formula_intent_hash         text  -- nullable until review→approved
variable_binding_set_hash   text  -- nullable until review→approved
filter_set_hash             text  -- nullable until review→approved
identity_tuple_hash         text  -- nullable until review→approved
package_signature_hash      text  -- nullable until review→approved
hash_algorithm_version      text  -- nullable until review→approved

-- M2 CHECK constraints (5 hash format + 1 version format)
mc_formula_intent_hash_fmt_chk        : <col> IS NULL OR <col> ~ '^sha256:[0-9a-f]{64}$'
mc_variable_binding_set_hash_fmt_chk  : same
mc_filter_set_hash_fmt_chk            : same
mc_identity_tuple_hash_fmt_chk        : same
mc_package_signature_hash_fmt_chk     : same
mc_hash_algorithm_version_chk         : <col> IS NULL OR <col> ~ '^mcf-[a-z-]+-v[0-9]+$'

-- Partial UNIQUE on identity tuple — only when populated and not archived
idx_mcf_mc_identity_active = UNIQUE (identity_tuple_hash, hash_algorithm_version) WHERE archived_at IS NULL AND identity_tuple_hash IS NOT NULL
```

The substrate enforces:
- Hash format: `sha256:<64 hex chars>` (when non-null) for all 5 hash columns
- Algorithm version: `mcf-<lowercase-letters-and-hyphens>-v<digits>` (when non-null)
- Partial uniqueness: an `(identity_tuple_hash, hash_algorithm_version)` tuple may exist at most once across non-archived MCs

### 2.3 The M3 state-transition trigger NOT-NULL gate at `review → approved`

The M3 trigger (`mcf.fn_mcv_state_transition_check`, BEFORE UPDATE) rejects any `review → approved` transition on `mcf.metric_contract_version` if the parent `mcf.metric_contract` row has ANY of the 6 hash columns NULL. This is the substrate gate that forces hash population before activation can proceed. The `McfCertWriterService.approveForActivation` method computes and UPDATEs all 6 hash columns on the parent MC inside the same tx as the state UPDATE, exactly to satisfy this gate (per M4 DBCP §5.3 race-correctness binding).

### 2.4 The M4 `McfHashComputer` interface boundary

```typescript
// bc-core/src/registry/mcf/mcf-hash-computer.interface.ts
export interface ParentHashes {
  formulaIntentHash: string;          // 'sha256:<64-hex>'
  variableBindingSetHash: string;     // 'sha256:<64-hex>'
  filterSetHash: string;              // 'sha256:<64-hex>'
  identityTupleHash: string;          // 'sha256:<64-hex>'
  packageSignatureHash: string;       // 'sha256:<64-hex>'
  hashAlgorithmVersion: string;       // 'mcf-<lowercase>-v<digits>'
}
export interface McfHashComputer {
  computeAllForApproval(input: { metricContractUid: string }): Promise<ParentHashes>;
}
```

M4 declares this interface and ships `MockMcfHashComputer` against it. M7 + M8 (or a combined gate) are the real implementations.

---

## 3. Why real metric authoring is still blocked

Despite the M4 substrate + service being live, real-metric authoring against `bc_platform_dev` cannot proceed for **four** independent reasons:

| # | Block | Resolution gate |
|---|---|---|
| 1 | **`McfHashComputer` has no real implementation.** Only `MockMcfHashComputer` exists. In non-production environments (NODE_ENV ≠ production) the mock returns substrate-compatible hashes that *can* be persisted to `mcf.metric_contract`. But these hashes are deterministic-from-uid only — they encode no actual formula identity. Using them for real metrics would create rows whose identity tuple is meaningless. | M7 (formula AST hasher) + M8 (composite package hasher) |
| 2 | **Production guard hard-rejects mock markers.** Even if a developer mistakenly wired `MockMcfHashComputer` into production, `assertProductionHashAlgorithm` throws `ConfigurationError` before any hash UPDATE. This is a deliberate safety net that means real metrics cannot be created in production via the mock. | M7 + M8 (real impl returning `mcf-formula-v1` / `mcf-package-v1` style markers that pass the guard) |
| 3 | **No formula AST substrate exists yet.** The `mcf.metric_contract_version` table has no column for the canonical formula AST today (per M2 DBCP). The build plan calls for `mcf.metric_formula_ast` substrate in M7. Without storage for the AST, the hash computer has nothing structural to hash from — it would be hashing nothing. | M7 (substrate) |
| 4 | **No authoring panel exists.** Real-metric authoring per MCF §11.3 is a panel act, not a hand-built service call. The panel is M5 (substrate) + M11 (implementation), both of which depend on M7+M8 having stabilized the formula AST + hash contracts. | M5 → M11 (gated on M7+M8) |

**Net:** Block 1 is the proximate cause. Blocks 2-4 are downstream consequences. M7+M8 are the unblocking gates for real-metric capability at the service layer; M5+M11 are the unblocking gates for operator-facing authoring.

This preflight scopes M7+M8 only.

---

## 4. Formula AST authority requirements

### 4.1 What "authority" means here

Per MCF §7.1 + L4 working rule lock (build plan): the Formula AST is the **structural truth** of an MC's computation. Rendered text forms may exist for display, but they are not authority. Two MCs with identical ASTs but different rendered text are the same MC; two MCs with different ASTs but identical rendered text are different MCs.

The M7 service is the **authority surface** for formula ASTs. It accepts AST input (not text), validates against a closed taxonomy, normalizes per MCF §8, and emits the canonical identity hash. No other surface in the platform constructs or alters ASTs.

### 4.2 Closed AST node taxonomy v1 (MCF §7.2 — locked)

The 9 node types of the v1 taxonomy:

| Node | Role | Type signature |
|---|---|---|
| `variable_ref` | reference to a bound MC variable (points at a BCF BC) | BC's representation term + unit |
| `literal` | constant with explicit representation term + unit | literal's type |
| `aggregate` | `SUM`/`AVG`/`COUNT`/`COUNT_DISTINCT`/`MIN`/`MAX`/`MEDIAN`/`PERCENTILE(p)` | value-kind aligned with operand |
| `arithmetic` | `+`/`-`/`*`/`/`/`MOD` (type-checked per §7.5) | dominant operand type |
| `comparison` | `<`/`<=`/`=`/`>=`/`>`/`!=` | boolean |
| `case` | `CASE WHEN <comparison> THEN <expr> ELSE <expr>` (typed branches must agree) | common type of branches |
| `window` | `LAG`/`LEAD`/`MOVING_AVG(window)` | operand type |
| `time_anchor_resolution` | resolves time-anchor BC to (fiscal_period, fiscal_year) per D364/D365 | `(fiscal_period, fiscal_year)` tuple |
| `bucket_assign` | maps numeric/date to closed-enum bucket label | text-kind bucket label |

Adding a node type is an ADR-governed MCF Grammar change. The M7 DBCP should restate the v1 closure and document the procedure for v2 (post-M7 amendment).

### 4.3 Forbidden patterns (MCF §7.3 — substrate-enforced after M7)

- Arbitrary SQL — no raw query embedding
- External function calls — no `EXEC(...)` or external code
- Side effects — no AST node may write state
- Free-text reference resolution — no `"resolve('unit_price')"`; references are by BCF id only
- Implicit unit conversion — type/unit mismatch at bind time rejects the bind (per §6.3 check 4)
- Aggregation outside grain — every aggregate operates within the MC's grain
- Recursion / self-reference — no `variable_ref` to the MC's own output

The M7 service is responsible for **detecting and rejecting** these patterns at AST construction time (before the AST ever enters the substrate). PE-MC-5 (per §13) is the downstream check that confirms the rejection held.

### 4.4 Type promotion rules (MCF §7.5 — locked)

The 6 explicit type promotion rules for `arithmetic` nodes. Anything outside this list requires explicit literal conversion. The M7 type-checker must implement and reject violations.

### 4.5 Executable-deterministic interpretation (MCF §7.6)

Every node in the closed taxonomy has a single deterministic execution semantics. M7 is the authority for what each node MEANS. M10 (deterministic verifier service) is the consumer that exercises ASTs against fixtures.

This is the M7-vs-M10 boundary: M7 declares the semantics; M10 executes them. M7 does NOT ship an execution engine. M7 ships a static type-checker + normalizer + hasher.

---

## 5. Hash/signature requirements

The 6 substrate columns + what each represents semantically (per MCF §4.2, §8.4, §8.7):

### 5.1 `formula_intent_hash`

**Definition:** sha256 of the canonical serialization of the **normalized AST** (per MCF §8.1-§8.4).

**Input surface:** the normalized AST tree (no other inputs).

**Algorithm version marker:** e.g. `mcf-formula-v1`.

**Identity role:** Part of MC structural identity tuple per §4.2. Two MCs with identical formula ASTs (after normalization) share this hash.

**Owner per build plan:** M7 (formula AST service).

### 5.2 `variable_binding_set_hash`

**Definition:** sha256 of the canonical serialization of the **ordered/named variable binding set**. Each binding contributes `(role_label, bound_entity_or_bc_id, bind_time_check_result_signature)`.

**Input surface:** the ordered binding set from `mcf.metric_variable_binding`.

**Algorithm version marker:** can share `mcf-formula-v1` or have its own marker (e.g. `mcf-binding-v1`) — an open question (§11 below).

**Identity role:** Contributes to MC identity tuple per §4.2 (distinguishes two MCs whose formulas are identical but whose bindings differ — e.g. `sum(NETPR)` over different bound BCs).

**Owner:** ambiguous in the build plan; MCF §8.7 implicitly says M7-adjacent (the per-binding canonicalization), but it could equally live in M8 since it's an input to the composite. **Operator decision required** (§11 below).

### 5.3 `filter_set_hash`

**Definition:** sha256 of the canonical serialization of the **sorted filter clause set** from `mcf.metric_filter_clause`. Per MCF §4.5, filters are set-semantic for identity (order does not matter; sorting is part of canonicalization).

**Input surface:** the sorted filter clause set (each clause is a sub-AST).

**Algorithm version marker:** shared with `formula_intent_hash` (filters are sub-ASTs) or its own marker. **Operator decision required.**

**Identity role:** Contributes to MC identity tuple per §4.2 (two MCs with identical formula but different filter sets are distinct MCs).

**Owner:** same ambiguity as `variable_binding_set_hash`.

### 5.4 `identity_tuple_hash`

**Definition:** sha256 of the composite identity tuple per MCF §4.2. The exact composition is implicit in MCF §4.2 + §8 but not spelled out as a single formula. Most likely:

```
identity_tuple_hash = sha256(
  formula_intent_hash + ':' +
  variable_binding_set_hash + ':' +
  filter_set_hash + ':' +
  grain_entity_id + ':' +
  temporal_gate_signature
)
```

The exact composition recipe is **open** and requires M7/M8 DBCP fixing (§11 below).

**Input surface:** the 3 preceding hashes + grain entity id + temporal gate signature.

**Algorithm version marker:** likely `mcf-identity-v1`.

**Identity role:** The substrate-enforced identity (partial UNIQUE on `mcf.metric_contract`). Two MCs with the same `identity_tuple_hash` + same `hash_algorithm_version` cannot both exist non-archived.

**Owner:** Composite; M7 per build plan (composes from formula/binding/filter hashes); but could be M8 since it's a composite (parallel to `package_signature_hash`).

### 5.5 `package_signature_hash`

**Definition:** sha256 of the composite package per MCF §8.7:

```
package_signature_hash = sha256(
  formula_ast_hash + ':' +
  variable_binding_set_hash + ':' +
  grain_filter_temporal_dimension_signature_hash
)
```

where `grain_filter_temporal_dimension_signature_hash` is `sha256(canonical_serialization(grain_entity_id, sorted_filter_clause_set, temporal_gate_spec, sorted_computed_dimension_ref_set))`.

**Input surface:** the composite of all MC-shape axes. Adds `computed_dimension_ref_set` to the identity inputs (which `identity_tuple_hash` does not directly include).

**Algorithm version marker:** `mcf-package-v1`.

**Verification role per MCF §8.7:** This hash is the **binding key for self-verification fixtures** (M9 + §12.7 stale-fixture rule). It is NOT the identity hash; it is the verification hash. A fixture becomes stale the moment ANY contributing axis changes.

**Owner per build plan:** M8 (composite package signature service).

### 5.6 `hash_algorithm_version`

**Definition:** text marker per substrate CHECK `^mcf-[a-z-]+-v[0-9]+$`. Records the algorithm generation used to compute the other 5 hashes.

**Open question:** does each hash carry its own version (5 markers) or is there a single global "MC hash algorithm version" that covers all 5? MCF §8.6 and §8.7 mention `mcf-formula-hash-v1` and `mcf-package-hash-v1` as parallel markers, implying per-hash versioning. The substrate has only ONE column (`hash_algorithm_version` on `mcf.metric_contract`), implying single global versioning. **Resolution requires M7/M8 DBCP.**

If per-hash versioning is needed, either:
- (a) the substrate column needs a structured format (e.g. `formula=mcf-formula-v1,package=mcf-package-v1`) — substrate change, scope-violating for M7
- (b) only the *composite* algorithm version is stored, and per-hash versions are implicit in the composite version
- (c) the substrate column is bumped only when ANY contributing algorithm bumps, with the composite version encoding the bundle (e.g. `mcf-bundle-v1` covers `formula-v1 + binding-v1 + package-v1`)

Option (b) or (c) are non-substrate-breaking. **Operator decision required.**

---

## 6. Boundary between M7 and M8

### 6.1 Build plan split (current)

| Gate | T-shirt | Scope per build plan §4.3 |
|---|---|---|
| M7 | XL | `mcf.metric_formula_ast` substrate; authoring service; closed AST taxonomy; normalization (§8.2); `formula_intent_hash` (§8.4); bind-time checks (§6.3) |
| M8 | S | Composite `package_signature_hash` per §8.7; algorithm-versioned (`mcf-package-hash-v1`); auto-population trigger on `mcf.metric_contract_version` write |

### 6.2 What the McfHashComputer interface implies

The `computeAllForApproval` method returns **all 6 hashes** from one call. From the M4 service's perspective, there is no observable split: it requests "all 6 hashes for this MC" and gets them. Whether one or two backend services compute them is an implementation detail of the binding.

Per M4 DBCP §7.2 (verbatim): *"A plausible decomposition might place the six hashes across files like: a formula intent hasher (M7-owned) ... a package signature hasher (M8-owned) ... a composing service that implements McfHashComputer (could be M7 or M8 or shared). M7 and M8 DBCPs will fix the actual filenames + class names + ownership boundary."*

### 6.3 Three boundary options

**Option A — Split per build plan (M7 = 4 hashes + AST; M8 = composite package hash).**
- M7 owns: `formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, `identity_tuple_hash` + AST substrate + canonicalization
- M8 owns: `package_signature_hash` (composes from M7 outputs + grain/filter/temporal/dim signature)
- `hash_algorithm_version` marker: composed (M8 reports the marker that names both M7 + M8 algorithm generation)
- **Pro:** smaller M8 gate; explicit algorithm-version handoff
- **Con:** M7+M8 DBCPs need cross-coordination; M8 cannot ship before M7; canonicalization rules for `variable_binding_set_hash` / `filter_set_hash` straddle the boundary

**Option B — Combined M7+M8 single gate.**
- One DBCP covers: AST substrate + canonicalization + all 6 hashes + algorithm-version registry + bind-time checks
- **Pro:** one document; one algorithm-version discipline; one implementation; no cross-DBCP coordination; the `McfHashComputer` interface is unified at the contract level
- **Con:** XL gate gets bigger; harder review surface; deferring M8's composite hash inside M7 risks scope creep

**Option C — Split with shared canonicalization library (M7 = AST + normalization library; M8 = all 6 hashes + algorithm versions).**
- M7 owns: AST substrate, taxonomy implementation, normalization, bind-time checks — but NO hashes
- M8 owns: all 6 hashes + algorithm-version registry + `McfHashComputer` implementation; consumes M7's normalized AST + the canonical serialization library
- **Pro:** clean separation of *structure* (M7) from *identity* (M8); single owner for hash + algorithm versioning; M8 is XL not S (the work moves)
- **Con:** changes the build plan's T-shirt sizing; M7 becomes "AST service only" without identity hash

### 6.4 Recommendation (deferred to operator)

This preflight does NOT pick. **Recommended next gate (§12 below) is a combined M7/M8 DBCP** that the operator can review and split if the DBCP becomes too large. Splitting after the fact is a smaller cost than coordinating two DBCPs without seeing them written.

---

## 7. Canonicalization questions

The canonicalization surface is the make-or-break design decision: get it wrong and every MC ever authored carries the bug.

### 7.1 AST canonical JSON shape

**Open question.** MCF §8.3 specifies a `sort_key` recursive definition, but not the exact JSON serialization format that produces it. Candidates:
- (a) Plain JSON with sorted keys, no whitespace (RFC 8785 JCS)
- (b) Custom positional serialization (e.g. `"a:SUM:(v:bc-123)"`)
- (c) CBOR canonical encoding (RFC 8949 §4.2.1)

Each has different cross-language portability + storage tradeoffs. **The M7 DBCP must fix this.** Once fixed, changing it is an algorithm-version bump.

### 7.2 Binding-set ordering

**Open question.** MCF §8.7 says "ordered/named variable binding set" — but what's the ordering key? Options:
- (a) `role_label` alphabetic
- (b) `bound_bc_id` UUID-lexicographic
- (c) `(role_label, bound_bc_id)` composite
- (d) insertion order (NOT identity-stable; rejected)

Per MCF §6.1 the binding act is named: variables have role labels (`numerator`, `denominator`, `time_anchor`). Most likely (a) `role_label` alphabetic. **The M7 or M8 DBCP must fix this.**

### 7.3 Filter ordering

**Open question.** MCF §4.5 declares filters set-semantic for identity. The sort key needs to be defined. Per §8.3 `sort_key(comparison)` is suggested for filter sub-ASTs. **The M7 DBCP must fix this.**

### 7.4 Temporal gate params canonicalization

**Open question.** MCF §4.4 declares the closed enum of `temporal_gate_shape` values (instantaneous / trailing_window / period_aggregate / point_in_time / as_of / rolling_window). Each shape has parameters (e.g. `trailing_window(30, day)`). The canonicalization of these params (e.g. `{"days": 30, "unit": "day"}` vs `{"unit": "day", "window": 30}`) needs to be fixed for `identity_tuple_hash` + `package_signature_hash` to be stable. Per §4.7 the temporal gate is identity-bearing; the param canonicalization affects identity. **The M7 or M8 DBCP must fix this.**

### 7.5 Package signature input surface

**Open question.** Per MCF §8.7, the package signature hash includes `(grain_entity_id, sorted_filter_clause_set, temporal_gate_spec, sorted_computed_dimension_ref_set)`. Open at the column level:
- Does `grain_entity_id` flow as the raw UUID or as a hash of the entity's BCF record content? (If the entity's identity changes via BCF supersession, does the MC's package hash also change?)
- Are `mcf.metric_contract_version` descriptive columns (display_name, threshold_json, ownership) included? Per §4.7 they are NOT identity-bearing; per §8.7 they are NOT in the package signature. But this needs explicit confirmation in the DBCP.
- Are `mcf.metric_computed_dimension_ref` resolver configs included verbatim, or hashed-then-included? (Resolver config might contain tenant-specific paths that shouldn't poison the identity-hash space.)

**The M7 or M8 DBCP must fix all three.**

### 7.6 Computed dimension ref canonicalization

**Open question.** Per MCF §9.2, computed dimensions have a "governing configuration" reference. The canonicalization of this reference (UUID vs path vs path+version) affects the package hash. **The M7 or M8 DBCP must fix this.**

---

## 8. Algorithm-version discipline

### 8.1 Allowed naming pattern (already substrate-enforced)

The live M2 substrate CHECK `mc_hash_algorithm_version_chk` enforces regex `^mcf-[a-z-]+-v[0-9]+$`. Examples that pass:
- `mcf-formula-v1`, `mcf-binding-v1`, `mcf-filter-v1`, `mcf-identity-v1`, `mcf-package-v1`
- `mcf-canonical-v1`, `mcf-mock-v1` (latter caught by service guard for production)
- `mcf-amendment-verifier-v1` (used by M3 cert-amendment verifier)

Examples that fail (substrate rejects):
- `mock-1.0.0` (wrong prefix), `mcf-v1` (no middle segment), `mcf-m4-verifier-v1` (digit in middle segment), `mcf-formula-1.0` (no `v` + non-digit suffix)

### 8.2 Per-hash vs single-global versioning

Per §5.6 above — open question. The substrate column is single. Two viable answers:
- **Single global "bundle" version** — `mcf-bundle-v1` encodes the bundle of (formula-v1, binding-v1, filter-v1, identity-v1, package-v1). Bumping any sub-algorithm bumps the bundle. **Pro:** one column, one truth. **Con:** harder to upgrade one hash without bumping all.
- **Per-hash version** — each hash has its own marker; the column stores the "composite" (e.g. `mcf-bundle-v1` resolves via registry to specific sub-versions). **Pro:** independent upgrade paths. **Con:** requires a version-registry artifact.

**Operator decision required.** Recommended position: single global bundle (Option A); per-hash versioning can ship later as an amendment if needed.

### 8.3 Upgrade strategy

Per MCF §8.6: "If the normalization rules change (e.g. v2 adds a new normalization step), the algorithm version increments. Existing MCs retain their v1 hash; new MCs receive v2 hashes. The substrate UNIQUE constraint includes the algorithm version, so cross-version collisions are impossible."

This is locked. M7/M8 DBCP must restate the rule and describe the operational sequence:
1. Algorithm change proposal → ADR
2. New algorithm version constant ships in M7/M8 service
3. M7/M8 service uses the new version for ALL new hash computations from that point forward
4. Existing `active` MCs retain their old hashes (per Foundation Invariant III)
5. Existing `draft` MCs whose hashes were not yet committed (i.e. not yet `review → approved`) are re-hashed at approval time with the new version

Re-hashing in-flight `draft` MCs is the only non-immutable case. The DBCP must specify how this is detected (e.g. "if `mcf.metric_contract.hash_algorithm_version IS NULL`, re-hash with current version") and that the new hash is what enters the partial UNIQUE.

### 8.4 No mock in authority-bearing paths

The M4 production guard (`assertProductionHashAlgorithm`) is the in-service rejection per DBCP §7.5. The substrate CHECK `mc_hash_algorithm_version_chk` is the substrate-layer rejection — it accepts `mcf-mock-v1` because that conforms to the regex, but the production guard's `startsWith('mcf-mock-')` check rejects it. Defense-in-depth: also rejects legacy `startsWith('mock-')`.

The M7/M8 DBCP should:
- Restate the production-guard contract (mock markers detected; rejected in `NODE_ENV='production'`)
- Specify that the real M7/M8 implementation MUST use a non-mock marker (`mcf-formula-v1`, `mcf-package-v1`, etc.)
- Specify the operational sequence for switching `MockMcfHashComputer` → real `McfHashComputer` in production wiring (NestJS module DI binding; no service code change)

---

## 9. Relationship to M4 `McfHashComputer`

### 9.1 Real implementation contract

M7 (or combined M7/M8) must ship a class implementing `McfHashComputer.computeAllForApproval(input: { metricContractUid }): Promise<ParentHashes>`. The implementation contract:

- **Deterministic:** same `metricContractUid` → same hashes (modulo `hashAlgorithmVersion` changes)
- **Idempotent:** read-only against `mcf.*` tables; never writes
- **In-tx-safe:** the call happens inside the `approveForActivation` work tx, with the parent MC + all child rows already locked under SELECT FOR UPDATE (per M4 §5.3 race-correctness binding). M7/M8 service must use the same DB connection / tx context — likely via injection, not via creating a fresh connection
- **Returns substrate-compatible markers:** `hashAlgorithmVersion` matches `^mcf-[a-z-]+-v[0-9]+$` and is non-mock
- **Returns sha256-format hashes:** each of the 5 hash strings matches `^sha256:[0-9a-f]{64}$`

### 9.2 How M4 should consume it

No change to M4 service code is required when M7/M8 ships. The wiring change is:

```typescript
// Before (M4 dev/test): mock injection
McfModule.providers = [
  { provide: McfHashComputer, useClass: MockMcfHashComputer },
  ...
];

// After M7/M8 ships: real impl in production module
McfModule.providers = [
  { provide: McfHashComputer, useClass: Mcf7M8HashComputer },  // real impl
  ...
];
```

Tests can continue to use `MockMcfHashComputer` (the non-production guard permits it). Integration tests against `bc_platform_dev` will use whichever is wired into the test module — for now they use the mock (per `mcf-cert-writer.service.integration.spec.ts`), which works because the substrate CHECK admits `mcf-mock-v1`.

### 9.3 Test / mock boundary

The mock stays. Per MCF §8 + §7.6 the real hashes encode formula identity; the mock encodes only `metricContractUid` identity. Tests that don't care about formula identity (idempotency, transaction discipline, etc.) can continue to use the mock. Tests that require real hash semantics (e.g. M9 fixture binding tests) will need the real implementation.

The M7/M8 DBCP should specify whether the mock continues to ship (recommended: yes — for service-layer unit tests in M4 + future MCF service tests that don't depend on hash semantics) and whether a separate `mcf-test-fixtures` package emerges for real-implementation integration testing.

---

## 10. Risks and stop conditions

### 10.1 Design risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-1 | **Canonicalization spec lock-in.** Once M7/M8 ships and the first real MC's hash is committed, the canonicalization rules become load-bearing. Changing them requires version bump + audit. | High | DBCP review surface for canonicalization questions §7.1–§7.6 must be tight. Operator review of canonical JSON serialization format is non-optional. |
| R-2 | **AST taxonomy v1 closure incompleteness.** MCF §7.2 declares 9 node types. If real-metric authoring discovers a needed 10th, supersession of in-flight MCs is messy. | High | Per build plan M7 primary risk note. Mitigation: at M7 DBCP, walk the BCF-enrichment slice's first 10 metrics (per `mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md`) to validate the taxonomy covers their formulas. |
| R-3 | **Per-hash vs global versioning ambiguity.** Substrate has one column; MCF §8 docs imply parallel markers. If picked wrong, upgrade migration is painful. | Medium | Operator decision required (§11). Recommended: single global bundle marker. |
| R-4 | **In-tx hash computation slowness.** Per M4 §5.5, `approveForActivation` slow-flag = 5s. With real M7/M8, hash cost scales with binding + filter + dim-ref count. | Medium | DBCP should specify slow-flag thresholds + per-method tx lifetime budgets matching MC complexity. |
| R-5 | **Mock leakage into production.** Defense-in-depth (substrate CHECK + service guard) holds today, but DI mis-wiring is a real risk. | Low | Already mitigated by §7.5 production guard. M7/M8 DBCP should add a startup check that logs the wired `McfHashComputer.constructor.name` in production. |
| R-6 | **Combined-DBCP scope creep.** If M7+M8 are combined, the document risks growing past review-tractable size. | Medium | Allow split mid-review if size warrants. |
| R-7 | **identity_tuple_hash composition not in MCF §8.** MCF §4.2 names the identity tuple but doesn't spell out the hash composition formula. §5.4 above proposes one. | Medium | Operator must lock the composition formula in the DBCP. Substrate UNIQUE depends on this being stable. |
| R-8 | **Computed-dimension resolver config tenant-poisoning.** If `resolver_config_json` is hashed verbatim into package_signature_hash, tenant-specific paths could make the same MC's hash differ per tenant. | Medium | DBCP must specify the canonicalization for resolver configs (e.g. extract tenant-invariant kernel; hash that). |

### 10.2 New risks surfaced by this preflight

| # | Risk | Mitigation |
|---|---|---|
| R-9 | **No `mcf.metric_formula_ast` substrate exists.** M7 ships it; M8 consumes it. If M8 ships before M7, M8 has nothing to hash. | Sequencing: M7 substrate before M8 service. Single combined DBCP elides the dependency. |
| R-10 | **Language portability.** M7/M8 canonical serialization may need cross-language re-implementation (e.g. for bc-ai panel proposals). Custom positional formats vs RFC 8785 JCS make different ports easier. | DBCP §7.1 choice matters. RFC 8785 JCS has the broadest language support. |

### 10.3 Stop conditions

The M7/M8 DBCP STOPS and re-frames if any of these surface:

- Operator wants to add a 10th AST node type before locking the taxonomy → re-open MCF §7.2 in an amendment-ADR before DBCP opens.
- The canonical serialization format choice (§7.1) requires substrate change (e.g. needs a `formula_ast_canonical_json` column on `mcf.metric_contract_version`) → that's M2 substrate amendment territory; sequence appropriately.
- Operator wants per-hash versioning instead of global bundle → substrate column may need restructuring; flag M2 amendment requirement.

---

## 11. Operator decisions needed

The operator must resolve these 8 questions before any M7/M8 DBCP can open:

| # | Decision | Options | Recommended |
|---|---|---|---|
| **D-M7-1** | **Combined M7+M8 DBCP, or two separate?** | (A) combined; (B) split per build plan | (A) combined — see §6.4 |
| **D-M7-2** | **Boundary split if combined doc-but-split-impl, or single impl?** | (A) one service class implementing all 6 hashes; (B) two services with a coordinator; (C) per build plan (M7 = 4 hashes + AST; M8 = composite) | (B) — clear ownership; permits independent algorithm-version bumps later |
| **D-M7-3** | **AST canonical JSON serialization format (§7.1).** | (a) RFC 8785 JCS; (b) custom positional; (c) CBOR canonical | (a) RFC 8785 JCS — broadest language portability |
| **D-M7-4** | **Hash algorithm versioning granularity (§8.2).** | (A) single global bundle marker; (B) per-hash markers via registry | (A) single global bundle — substrate column is single; per-hash can ship as amendment |
| **D-M7-5** | **identity_tuple_hash composition formula (§5.4 / R-7).** | (a) `sha256(formula + binding + filter + grain + temporal)`; (b) include computed-dim refs too; (c) operator-specified other shape | (a) — matches §4.2 identity tuple inputs without computed-dim refs (the latter belong in package signature per §8.7) |
| **D-M7-6** | **Binding-set ordering key (§7.2).** | (a) role_label alphabetic; (b) bound_bc_id UUID-lex; (c) composite | (a) — role labels are the named anchors per §6.1 |
| **D-M7-7** | **Computed-dimension resolver config canonicalization (§7.6, R-8).** | (a) hash verbatim resolver_config_json; (b) extract tenant-invariant kernel + hash; (c) exclude from package hash | (b) — protects against tenant-poisoning per R-8 |
| **D-M7-8** | **Real implementation language (bc-core TS only, or shared with bc-ai Python).** | (a) bc-core TS only; (b) parallel implementations in TS + Python; (c) port via WASM | (a) — bc-core is the authority; bc-ai consults but does not author hashes |

These 8 decisions are the **operator-approval gate** before any M7/M8 DBCP opens. The DBCP authoring session should not begin until all 8 are answered (or explicitly deferred with rationale).

---

## 12. Recommended next gate

### 12.1 Recommendation

**Open a single combined M7/M8 DBCP** at `bc-docs-v3/docs/implementation/metric-context-framework-m7-m8-formula-hash-authority-dbcp.md`.

Rationale (per §6.4):
- The 6 hashes interlock; splitting the design across two DBCPs risks coordination drift
- The `McfHashComputer.computeAllForApproval` interface unifies the 6 hashes at the contract level; one DBCP that owns this contract is cleaner
- Single algorithm-version discipline doc (per D-M7-4)
- The DBCP can still ship implementation as **two service classes** internally (per D-M7-2 Option B) — combined DBCP does not force combined implementation
- If the DBCP grows past review-tractable size during authoring, split is a small cost; the inverse (merging two half-written DBCPs) is larger

### 12.2 Alternative if combined is rejected

If the operator prefers the build-plan split:
- **M7 DBCP first** — substrate (`mcf.metric_formula_ast` if needed; canonicalization library; 4 hashes) + service (AST authoring, bind-time checks, formula_intent_hash + variable_binding_set_hash + filter_set_hash + identity_tuple_hash) + `McfHashComputer` interface implementation for the 4 hashes
- **M8 DBCP second** — composite `package_signature_hash` service that consumes M7 outputs + grain/filter/temporal/dim-ref signature; algorithm-version registry; updates `McfHashComputer` implementation to populate the 5th hash

Sequencing: M7 DBCP → M7 implementation PR → M7 apply (no DDL if substrate doesn't change) → M8 DBCP → M8 implementation PR → M8 apply. Cumulative gates: ~8 sessions vs ~4 for combined.

### 12.3 What this preflight does NOT open

| | Status |
|---|---|
| M7 DBCP | NOT OPEN — operator decisions §11 required first |
| M8 DBCP | NOT OPEN — same |
| Combined M7/M8 DBCP | NOT OPEN — recommended next gate, but operator decisions §11 required first |
| M5 panel substrate | unchanged — gated on M7+M8 |
| M9 fixture substrate | unchanged — gated on M7+M8 |
| M10 verifier engine | unchanged — gated on M9 |
| M11 panel implementation | unchanged — gated on M5+M9+M10 |
| Real MCF metric authoring | unchanged — substrate stays empty until M11 |
| bc-core code edits | none this session |
| bc-ai changes | none this session |

---

## Document verification

- **Scope clear** — §1 frames as docs-only preflight; §1.4 discipline assertions enumerate what this session does NOT do (8 negatives).
- **Live state captured** — §2 enumerates 10 mcf.* tables + 6 hash columns on `mcf.metric_contract` + M3 trigger gate + M4 service + production guard.
- **Block enumeration** — §3 itemizes the 4 independent blocks to real-metric authoring; M7+M8 unblocks 2 of them (real hash impl + production-guard-permitted markers).
- **Formula AST requirements summarized** — §4 restates the 9-node taxonomy v1, forbidden patterns, type promotion rules, M7-vs-M10 boundary.
- **6 hash columns fully specified** — §5 covers each (definition, input surface, algorithm version marker, identity/verification role, ownership).
- **M7/M8 boundary options** — §6 presents 3 options (split-per-build-plan / combined / split-with-shared-canonicalization-library) with recommendation deferred to §12.
- **Canonicalization questions itemized** — §7 lists 6 open canonicalization sub-questions that the DBCP must lock.
- **Algorithm-version discipline restated** — §8 covers substrate-CHECK-enforced pattern, per-hash vs global, upgrade strategy, no-mock-in-authority.
- **M4 interface relationship** — §9 spells out the real-implementation contract, M4 consumption (no service code change; DI swap), test/mock boundary.
- **Risk register** — §10 enumerates 10 risks (R-1..R-10) with severity + mitigation; 3 stop conditions.
- **Operator decisions enumerated** — §11 lists 8 decisions (D-M7-1..D-M7-8) with options + recommendation; explicit gate before any M7/M8 DBCP can open.
- **Recommended next gate** — §12 recommends combined M7/M8 DBCP; alternative split path also specified; explicit list of what this preflight does NOT open.
- **No DDL, no code, no metric authoring, no BCF touches.** This doc only.
