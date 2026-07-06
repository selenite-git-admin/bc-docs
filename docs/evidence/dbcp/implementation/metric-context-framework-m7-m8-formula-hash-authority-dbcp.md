---
uid: metric-context-framework-m7-m8-formula-hash-authority-dbcp
title: MCF M7/M8 Formula AST + Hash/Signature Authority DBCP (combined)
description: Combined design-blueprint for MCF gates M7 (Formula AST authority + canonicalization + 4 hashes) and M8 (composite package signature hash) per operator-accepted preflight decisions D-M7-1..D-M7-8 (`454bfeb`). Patched 2026-05-27 per review findings: B-1 mock backward-compat claim removed (mock signature MUST be updated in impl PR; `metricContractVersionUid` stays REQUIRED per operator decision); B-2 MCF §8.7 intermediate hash `grain_filter_temporal_dimension_signature_hash` RESTORED (package_signature_hash now composes formula_intent_hash + variable_binding_set_hash + grain_filter_temporal_dimension_signature_hash per MCF §8.7 verbatim); M-3 trigger amendment ADDED to scope (`fn_mcv_descriptive_immutability_check` must include `formula_ast_canonical_json` in enumerated column set); M-4 service-side placeholder-AST rejection ADDED to `approveForActivation`; M-1 role-vs-BC identity semantics CLARIFIED in §5.3 + §7; M-2 `clause_expression_json` RESTORED to filter hash canonical shape; M-5 BCF snapshot read-as-stored note ADDED; M-6 JCS-array encoding ADOPTED for identity tuple composition + intermediate hash; M-7 JCS library version pinning DISCIPLINE specified; M-8 forbidden-patterns test count corrected to 7. Single bundle algorithm-version marker `mcf-hash-v1` covering all 6 hashes; RFC 8785 JSON Canonicalization Scheme for AST + filter + binding + temporal-kernel + identity-tuple + intermediate-hash array serialization; binding-set canonical order by `variable_role_code`; computed-dim resolver canonicalization uses tenant-invariant kernel (identity hash excludes resolver paths; package signature includes only kernel + dimension_class_code + role_in_formula_code + source_business_concept_id). Two TypeScript implementation services (FormulaCanonicalizationService for AST + 3 sub-hashes; PackageSignatureService for composite + identity hashes + intermediate hash) plus McfHashComputerCoordinator implementing the M4 McfHashComputer interface. Production guard (mcf-mock-* + legacy mock-*) preserved. Substrate impact: ONE new jsonb column `formula_ast_canonical_json` on `mcf.metric_contract_version` + ONE M3 trigger amendment (CREATE OR REPLACE FUNCTION on `fn_mcv_descriptive_immutability_check` adding `formula_ast_canonical_json` to enumerated column set); ONE small DDL apply gate after this DBCP merges, applies both changes atomically inside BEGIN/COMMIT. McfHashComputer interface widened to REQUIRE `metricContractVersionUid` in addition to `metricContractUid` (mock signature update in impl PR; mock body ignores the new field). 12 risks (R-1..R-12) + 10 operator approvals (O-1..O-10) + test plan (golden canonicalization fixtures + hash determinism + order-insensitivity + tenant-poisoning + placeholder-rejection + trigger-immutability + M4 integration). Docs-only DBCP. No bc-core edits. No DDL applied. No MCF metric contracts. No M5/M11+ panel work. No BCF touches. Recommended next gate: combined M7/M8 implementation PR (NO DB APPLY); separate small-DDL apply gate after implementation PR merges.
status: draft
date: 2026-05-27
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m7-m8-formula-hash-authority-dbcp
---

# MCF M7/M8 Formula AST + Hash/Signature Authority DBCP (combined)

## 1. Scope and grounding

### 1.1 Purpose

Design the combined M7 + M8 services that unblock real MCF metric authoring. M4 ships the `McfHashComputer` interface + a `MockMcfHashComputer` (substrate-compatible `mcf-mock-v1` post-PR #108) + a production guard. This DBCP designs the **real implementation** that replaces the mock in production: a Formula AST canonicalization service producing 4 hashes + a Package Signature service producing the composite hash + a coordinator implementing the M4 interface.

The DBCP follows the operator-accepted preflight (`454bfeb`) recommendations and the 8 locked operator decisions enumerated in §2.

### 1.2 What this DBCP is and is not

| | This DBCP |
|---|---|
| Is | A combined docs-only design blueprint for M7 (Formula AST authority + 4 hashes) and M8 (composite package signature hash) under one document, with two service classes + one coordinator per D-M7-2 |
| Is | The formal trigger for a sequenced implementation arc (DBCP → impl PR → small-DDL apply gate → evidence PR) |
| Is not | A code edit — bc-core stays unchanged this session |
| Is not | A DDL apply — the single substrate change (`formula_ast_canonical_json` column add) is a separate operator-authorized session |
| Is not | A MCF metric authoring action — substrate stays empty |
| Is not | An M5 / M9 / M10 / M11 work item — those are downstream and gated on this DBCP |
| Is not | A BCF DBCP — `concept_registry.*` is read-only consumed (FK-less per existing MCF discipline) |

### 1.3 Source documents consumed

| Source | Role |
|---|---|
| M7/M8 preflight (`454bfeb`) | Decision options + recommendations the operator accepted |
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority; Decision 7 (closed AST taxonomy) |
| MCF requirements §4.2 (identity tuple) | Identity-bearing columns + composition |
| MCF requirements §4.4 (temporal gate enum) | Closed shape codes |
| MCF requirements §4.5 (filter set semantics) | Set-semantic identity |
| MCF requirements §6 (binding model) | Bind-time checks; role labels |
| MCF requirements §7 (Formula AST) | Closed 9-node taxonomy v1; forbidden patterns; type promotion; executable-deterministic interpretation |
| MCF requirements §8 (Normalization + identity hash + §8.7 package signature) | Normalization rules; structural sort key; algorithm versioning; composite hash composition |
| MCF requirements §9 (Computed dimensions) | Closed dimension_class_code enum; resolver config |
| MCF requirements §12 (Self-Verification Fixtures) | Why package_signature_hash is the fixture-binding key; stale-fixture rule (§12.7) |
| MCF requirements §13 (PE-MC checks) | PE-MC-5 (AST validity), PE-MC-10 (fixture passes) — downstream consumers |
| M2 DBCP + live substrate | 6 hash columns on `mcf.metric_contract`; format CHECKs; partial UNIQUE on identity tuple |
| M3 DBCP + live trigger | NOT-NULL gate at `review → approved` for all 6 parent hash columns |
| M4 DBCP §7 + live service | `McfHashComputer` interface (current signature: `computeAllForApproval(input: { metricContractUid }): Promise<ParentHashes>`); production guard |
| M4 apply closeout (`c2bc3fc`) | M4 substrate live + dormant; mock returns `mcf-mock-v1`; guard rejects `mcf-mock-*` and legacy `mock-*` |
| RFC 8785 (JSON Canonicalization Scheme) | The chosen canonical JSON serialization standard (D-M7-3) |
| Live child-row schemas | `mcf.metric_variable_binding` (with `variable_role_code` + `structural_sort_key` pre-computed); `mcf.metric_filter_clause` (with `operator_code` enum + `structural_sort_key`); `mcf.metric_computed_dimension_ref` (with `dimension_class_code` enum + `resolver_config_ref_json` + `resolver_params_hash` + `structural_sort_key`) |

### 1.4 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits this session | ✓ — read-only |
| No DDL applied | ✓ — DBCP designs the substrate change; apply is a separate gate |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No certification rows written | ✓ — M4 service operationally dormant |
| No BCF data touched | ✓ — `concept_registry.*` read-only |
| No M5 panel substrate work | ✓ — downstream |
| No M11/M12 panel work | ✓ — downstream |
| No M9/M10 fixture/verifier work | ✓ — downstream |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

---

## 2. Accepted operator decisions (D-M7-1..D-M7-8)

Per operator-accepted preflight recommendations (`454bfeb`):

| # | Decision | Locked |
|---|---|---|
| **D-M7-1** | Combined M7/M8 DBCP (single document) | ACCEPTED |
| **D-M7-2** | Two TypeScript implementation services + coordinator: `FormulaCanonicalizationService` (AST + 3 sub-hashes), `PackageSignatureService` (composite + identity hashes), `McfHashComputerCoordinator` (implements the M4 `McfHashComputer` interface) | ACCEPTED |
| **D-M7-3** | RFC 8785 JSON Canonicalization Scheme (JCS) for AST / filter / binding / temporal-kernel canonical serialization | ACCEPTED |
| **D-M7-4** | Single global bundle algorithm-version marker for v1, conforming to substrate regex `^mcf-[a-z-]+-v[0-9]+$`. **This DBCP selects `mcf-hash-v1`** as the final value (shortest substrate-compatible name; semantic clear). | ACCEPTED — value fixed by this DBCP |
| **D-M7-5** | Binding-set canonical ordering by `variable_role_code` alphabetic | ACCEPTED — substrate column confirmed |
| **D-M7-6** | Computed-dim resolver canonicalization: identity hash excludes tenant-specific resolver config; package signature includes the kernel `(dimension_class_code, role_in_formula_code, source_business_concept_id)` only | ACCEPTED |
| **D-M7-7** | Real implementation in bc-core TypeScript only | ACCEPTED |
| **D-M7-8** | `identity_tuple_hash = sha256(formula_intent_hash + variable_binding_set_hash + filter_set_hash + grain_entity_id + temporal_gate_shape_code + temporal_gate_params_kernel)`; computed-dim refs in package signature | ACCEPTED |

Two DBCP-introduced design decisions that **operator must confirm at O-1..O-2 (§16)**:

| # | Decision | DBCP position |
|---|---|---|
| **D-M7-9** | Algorithm version marker exact value | `mcf-hash-v1` (substrate-compatible; brand-neutral; bundle-scoped) |
| **D-M7-10** | `McfHashComputer` interface widening: REQUIRE `metricContractVersionUid` alongside `metricContractUid` in `computeAllForApproval` input | Widening is required — bindings/filters/dim refs live at the MCV level (verified live: `mcf.metric_variable_binding.metric_contract_version_uid`); without the version uid, the hash computer cannot resolve which MCV's child rows to read. **The new field is REQUIRED (non-optional)** per operator decision — `MockMcfHashComputer` signature MUST be updated in the impl PR (one-line change to method parameter type; mock body may ignore the field). Production guard semantics are unchanged (guard checks `hashAlgorithmVersion` prefix, not the input shape). |

---

## 3. Current live MCF state and why real metric authoring remains blocked

### 3.1 Live state recap (after M4 evidence apply)

After bc-core `2a603ce` + bc-docs-v3 `454bfeb`:

- **10 `mcf.*` tables live, all empty.** Identity-bearing child rows at MCV level: `metric_variable_binding` (with `variable_role_code` + `structural_sort_key` pre-computed); `metric_filter_clause` (with `operator_code` enum + `structural_sort_key`); `metric_computed_dimension_ref` (with `dimension_class_code` enum + `resolver_config_ref_json` + `resolver_params_hash` + `structural_sort_key`). Identity-bearing parent columns on `mcf.metric_contract`: 6 hash columns + `grain_entity_id` + `temporal_gate_shape_code` + `temporal_gate_params_json`.
- **M3 state-transition trigger** rejects `review → approved` if any of the 6 parent hash columns is NULL.
- **M4 service `McfCertWriterService`** live; integration-tested 7/7 PASS; calls `McfHashComputer.computeAllForApproval` inside `approveForActivation` after locking parent MC + child rows.
- **`McfHashComputer` interface** declared; only `MockMcfHashComputer` implements it (returns `mcf-mock-v1` hashes derived deterministically from `metricContractUid`).
- **Production guard** rejects `startsWith('mcf-mock-')` or `startsWith('mock-')` in `NODE_ENV='production'`.
- **No `mcf.metric_formula_ast`** table exists. The canonical AST is not stored anywhere today.
- **Seed substrate:** 1 `contract.framework_policy` mcf row + 2 `contract.operator_confirm_rule` mcf rows; `operator_confirm_rule.action_code` CHECK unchanged.

### 3.2 Why real metric authoring remains blocked

| # | Block | Resolved by |
|---|---|---|
| 1 | Mock-only `McfHashComputer` produces formula-identity-meaningless hashes | M7+M8 real implementation (this DBCP) |
| 2 | Production guard rejects `mcf-mock-*` marker | M7+M8 emits `mcf-hash-v1` (passes guard) |
| 3 | No AST substrate column → no place to store the canonical AST | M7 ships `formula_ast_canonical_json` column add (small DDL change) |
| 4 | No authoring panel (M5/M11) | Out of scope; M5/M11 are downstream gates |

This DBCP resolves blocks 1, 2, and 3. Block 4 (panel) is the gate after this one ships.

---

## 4. Formula AST v1 canonical model

### 4.1 Closed 9-node taxonomy v1 (locked from MCF §7.2; restated)

| Node kind | Role | Type signature | Required fields |
|---|---|---|---|
| `variable_ref` | Reference to a bound MC variable | BC's representation term + unit | `{kind: "variable_ref", role: <variable_role_code>}` |
| `literal` | Constant with explicit rep-term + unit | literal's type | `{kind: "literal", representation_term: <text>, unit: <text>, value: <json-scalar>}` |
| `aggregate` | `SUM`/`AVG`/`COUNT`/`COUNT_DISTINCT`/`MIN`/`MAX`/`MEDIAN`/`PERCENTILE(p)` | value-kind aligned with operand | `{kind: "aggregate", op: <enum>, operand: <node>, percentile_p?: <number when op=PERCENTILE>}` |
| `arithmetic` | `+`/`-`/`*`/`/`/`MOD` | dominant operand type per §7.5 | `{kind: "arithmetic", op: <enum>, left: <node>, right: <node>}` |
| `comparison` | `<`/`<=`/`=`/`>=`/`>`/`!=` | boolean | `{kind: "comparison", op: <enum>, left: <node>, right: <node>}` |
| `case` | `CASE WHEN <comparison> THEN <expr> ELSE <expr>` | common type of branches | `{kind: "case", branches: [{when: <node>, then: <node>}, ...], else: <node>}` |
| `window` | `LAG`/`LEAD`/`MOVING_AVG(window)` | operand type | `{kind: "window", op: <enum>, operand: <node>, window_spec: {duration: <int>, unit: <enum>}}` |
| `time_anchor_resolution` | Resolves time-anchor BC to (fiscal_period, fiscal_year) | tuple | `{kind: "time_anchor_resolution", time_anchor: <node>}` |
| `bucket_assign` | Maps numeric/date to closed-enum bucket label | text-kind label | `{kind: "bucket_assign", operand: <node>, bucket_spec: {boundaries: [<value>, ...], labels: [<text>, ...]}}` |

**Adding a node type is an ADR-governed MCF Grammar change.** The DBCP locks v1 at these 9.

### 4.2 Closed operators within nodes

| Node | Operator enum (closed) |
|---|---|
| `aggregate.op` | `sum`, `avg`, `count`, `count_distinct`, `min`, `max`, `median`, `percentile` |
| `arithmetic.op` | `plus`, `minus`, `multiply`, `divide`, `mod` |
| `comparison.op` | `lt`, `lte`, `eq`, `gte`, `gt`, `neq` |
| `window.op` | `lag`, `lead`, `moving_avg` |
| `window.unit` | `day`, `week`, `month`, `quarter`, `year`, `fiscal_period`, `fiscal_year` |
| `bucket_spec.boundary_type` | `numeric`, `date` |

The enum values use **snake_case** consistently. Display forms (`SUM`, `+`) are not part of the AST.

### 4.3 Type / scale discipline (locked from MCF §7.5)

The 6 explicit type-promotion rules apply to `arithmetic` nodes; outside these rules requires an explicit literal cast. The M7 canonicalization service implements the type-checker and rejects violations BEFORE hash computation (so no invalid AST ever receives a hash).

| Combination | Result | Rule |
|---|---|---|
| `currency × number` | `currency` (unit preserved) | promote-numeric |
| `currency × currency` | **REJECT** (`MC_DEFECT_UNIT_PROMOTION`) | no currency-squared |
| `count × number` | `count` | promote-numeric |
| `duration × number` | `duration` | promote-numeric |
| `date - date` | `duration` | derived-arithmetic |
| `date + duration` | `date` | derived-arithmetic |
| any other | **REJECT** (explicit literal cast required) | no-implicit-promotion |

### 4.4 Forbidden patterns (locked from MCF §7.3)

The canonicalization service REJECTS:

- Arbitrary SQL — no string-typed escape hatches
- External function calls — no `EXEC(...)`, no plug-in operators
- Side effects — no AST node may write state
- Free-text reference resolution — no `"resolve('unit_price')"`; references by `variable_role_code` (bound to BCF) only
- Implicit unit conversion — type/unit mismatch rejects
- Aggregation outside grain — every `aggregate` operates within the MC's grain
- Recursion / self-reference — `variable_ref` cannot target the MC's own output

PE-MC-5 (per MCF §13) re-asserts these structurally at publication eligibility evaluation; the M7 canonicalization service is the **upstream** rejection.

---

## 5. Canonical JSON rules

### 5.1 RFC 8785 JCS adoption (per D-M7-3)

The DBCP adopts **RFC 8785 JSON Canonicalization Scheme** verbatim for all canonicalization in M7/M8. JCS is broadly portable, simple to implement, and has stable reference implementations in TypeScript / Python / Go / Rust. Re-using a standard avoids inventing custom positional serialization (preflight §7.1 Option (b)).

### 5.2 JCS rules summarized (informative)

| Rule | RFC 8785 § | Effect |
|---|---|---|
| Object keys sorted | §3.2.3 | UTF-16 code unit lexicographic order (NOT byte order); deterministic across implementations |
| No insignificant whitespace | §3.2.1 | Output is a single line per object |
| Numbers serialized per ES6 `JSON.stringify` semantics | §3.2.2.3 | Trailing zeros stripped; `-0` becomes `0`; scientific notation thresholds match ES6 |
| Strings serialized per RFC 8259 + ES6 escape rules | §3.2.2.2 | Specific control character escapes; non-ASCII passed through as UTF-8 |
| `null` is preserved as `null` | §3.2 | NOT omitted |

### 5.3 MCF-specific normalization layered ABOVE JCS

JCS produces a deterministic byte sequence from a given JSON value. MCF's structural normalization (per MCF §8.2) operates on the AST **before** JCS serialization:

| MCF normalization rule (§8.2) | Order |
|---|---|
| 1. Commutative operator ordering | First — operands of `+`, `*`, `=`, `!=` sorted by structural sort key |
| 2. Constant folding | After ordering — literal-only sub-expressions pre-computed |
| 3. Variable identity discipline | After ordering — canonical AST stores `variable_role_code` (NOT label aliases). See §5.3.1 below for the role-vs-BC identity reconciliation with MCF §8.2 rule 3 wording. |
| 4. De Morgan canonicalization | After ordering — `NOT (A AND B)` → `(NOT A) OR (NOT B)` |
| 5. CASE branch ordering | After ordering — branches sorted by left-side BC id within equivalent comparisons |
| 6. Empty-filter elimination | After ordering — no-op filters removed |
| 7. Aggregate operand canonicalization | Recursive — applies to operand subtree |

The result is a **normalized AST** which is then serialized via JCS to produce the canonical bytes that are hashed.

### 5.3.1 Role-vs-BC identity reconciliation (per M-1 review finding)

MCF requirements §8.2 rule 3 wording reads literally as: *"the canonical form uses the bound BC id, not the variable label."* This DBCP makes the **explicit tighter choice** that BOTH `variable_role_code` (in the formula AST) AND `bound_business_concept_id` (in the binding hash, per §7) are identity-bearing:

| Identity carrier | Where stored in canonical input | Effect of change |
|---|---|---|
| `variable_role_code` | `formula_ast_canonical_json` `variable_ref.role` field | Renaming the role from `numerator` to `top_line` (with same BC binding) → `formula_intent_hash` changes |
| `bound_business_concept_id` | `variable_binding_set_hash` input row | Rebinding the role to a different BC (same role label) → `variable_binding_set_hash` changes |

Both are protected. The substrate's `UNIQUE (mcv_uid, variable_role_code)` constraint already treats role as identity, and the DBCP's design extends that to the formula hash. This is a **tighter identity** than the literal reading of MCF §8.2 rule 3.

**Reconciliation note for MCF requirements doc:** MCF §8.2 rule 3 wording should be amended in a follow-up requirements-doc edit to reflect this design: *"variable name aliases are stripped; the canonical form uses `variable_role_code` (NOT panel-display aliases of it), and the bound BC id is carried separately in the variable binding set hash."* This DBCP supersedes MCF §8.2 rule 3 wording until the reconciliation lands.

### 5.4 Field ordering inside AST nodes

All AST node objects are serialized via JCS, which sorts keys alphabetically. Examples:

| AST node (logical) | Canonical JSON (after MCF normalization + JCS) |
|---|---|
| `variable_ref` to role `numerator` | `{"kind":"variable_ref","role":"numerator"}` |
| `aggregate` SUM over `variable_ref(qty)` | `{"kind":"aggregate","op":"sum","operand":{"kind":"variable_ref","role":"qty"}}` |
| `arithmetic` `qty + adj` (commutative; sorted by sort_key) | `{"kind":"arithmetic","left":{"kind":"variable_ref","role":"adj"},"op":"plus","right":{"kind":"variable_ref","role":"qty"}}` (sort by `sort_key`: `v:adj` < `v:qty`) |

### 5.5 Null / omission rules

| Field type | Rule |
|---|---|
| Optional structural field | OMITTED when absent (e.g. `percentile_p` omitted when `aggregate.op !== 'percentile'`) |
| Required structural field | MUST be present; `null` only when explicit semantic meaning |
| Empty string | NOT permitted in any required text field — schemas reject upstream |
| Empty array | PRESENT as `[]` when the array slot is required (e.g. `case.branches` is required even when length 0 — but length 0 is rejected by the type-checker before hashing) |

Null is never used as a "skip this field" marker. JCS preserves `null` literally.

### 5.6 Number normalization

JCS §3.2.2.3 specifies ES6 `JSON.stringify` semantics:

| Input | Canonical |
|---|---|
| `1.0` | `1` |
| `1.10` | `1.1` |
| `-0` | `0` |
| `1.0e10` | `10000000000` |
| `0.0000001` | `1e-7` (ES6 threshold) |
| `1.2345e+21` | `1.2345e+21` |

The DBCP RECOMMENDS implementations rely on a well-tested JCS library (e.g. `canonicalize` npm package for TypeScript) rather than re-implement the rules.

**JCS library version pinning discipline (per M-7 review finding):** The chosen JCS library version MUST be pinned in `package.json` with an exact semver (no `^` or `~`); the resolved version's SHA MUST be locked in the lock file. Upgrading the JCS library is a **governance-gated** event because the entire v1 hash algorithm depends on JCS correctness — a silent library upgrade that changed canonicalization behavior would silently fork the algorithm. The golden hash anchor test (§14.7) re-validates every JCS library change; any anchor change means the bundle algorithm version (§12.4) MUST bump. The impl PR ships a CI check that asserts `package-lock.json` entry for the JCS library is unchanged when the M7/M8 source has not changed (defense against undeclared lib-upgrade).

### 5.7 String normalization

| Aspect | Rule |
|---|---|
| Unicode | Strings stay as UTF-16 code units per JS; JCS encodes to UTF-8 for hashing |
| Control characters | Escaped per RFC 8259 specific list (`\b \f \n \r \t` + `\u00XX`) |
| Non-ASCII printable | Passed through as UTF-8 (NOT `\u` escaped) |
| Trim / case | NOT applied — formula text fields are role codes / enum values which are already controlled |

---

## 6. Formula intent hash

### 6.1 Input surface

| Source | Field |
|---|---|
| Stored canonical AST | `mcf.metric_contract_version.formula_ast_canonical_json` (NEW column per §13) |

No other inputs. The hash is over the formula **structure**, not the bindings, filters, grain, or temporal gate.

### 6.2 Canonicalization

1. Read `formula_ast_canonical_json` from the locked MCV row.
2. Apply MCF §8.2 normalization rules in order (§5.3 above).
3. Serialize the normalized AST via RFC 8785 JCS.
4. Compute `sha256` over the UTF-8 bytes.

### 6.3 Output format

`sha256:<64 hex>` per substrate CHECK `mc_formula_intent_hash_fmt_chk`.

### 6.4 Ownership

`FormulaCanonicalizationService.computeFormulaIntentHash(mcvUid: string): Promise<string>` (per D-M7-2).

---

## 7. Variable binding set hash

### 7.1 Input surface

`SELECT * FROM mcf.metric_variable_binding WHERE metric_contract_version_uid = <mcvUid> ORDER BY variable_role_code ASC`. Each row contributes:

| Field | Identity-bearing | Reason |
|---|---|---|
| `variable_role_code` | YES | Ordering anchor + identity per D-M7-5 |
| `role_kind_code` (input / output / constant) | YES | Distinguishes the binding shape |
| `bound_business_concept_id` (UUID) | YES | The bound BCF BC (for input/output) |
| `bound_entity_id` (UUID) | YES | The bound BCF Entity (for grain bindings) |
| `constant_value_json` | YES | The constant payload (for constants) |
| `representation_term_snapshot` | YES | Type contract |
| `unit_code_snapshot` | YES | Unit contract |
| `data_type_snapshot` | YES | Data type contract |
| `bind_time_check_results_json` | **NO** | Audit-only; not identity-bearing |
| `structural_sort_key` (denormalization) | NO | Re-derivable; not used in hash input |
| `created_at` | NO | Audit timestamp |
| `metric_variable_binding_uid` | NO | Primary key only |

### 7.2 BCF ID treatment

`bound_business_concept_id` and `bound_entity_id` flow as **raw UUIDs** into the canonical JSON. Rationale:
- UUIDs are immutable per BCF Foundation Invariant III.
- If a BCF concept is later superseded, that creates a new BCF UUID; the MC's variable binding still references the OLD UUID until the panel changes the binding (which is a supersession event in MCF).
- Hashing the BCF row's *content* would couple MCF identity to BCF mutations — wrong layering.

**Role-vs-BC dual identity (per §5.3.1):** BOTH the `variable_role_code` (carried in the formula AST per §5.3.1) AND the `bound_business_concept_id` (carried here) are identity-bearing. Two MCs with the same formula AST shape but different role→BC bindings produce different `variable_binding_set_hash` values. Two MCs with the same role→BC bindings but different role labels produce different `formula_intent_hash` values (because the role label is in the AST). Both axes are protected.

### 7.2.1 BCF snapshot read-as-stored discipline (per M-5 review finding)

The `representation_term_snapshot`, `unit_code_snapshot`, and `data_type_snapshot` columns are **at-bind-time snapshots** captured when the binding row was inserted. They are NOT re-read from current BCF state at hash compute time. Rationale:

- If a future BCF supersession of the bound BC produces a new content shape (e.g. unit changes from `EUR` to `USD`), the MC's existing binding row's snapshot columns remain unchanged.
- MCF identity must NOT silently move when BCF moves — supersession of the MC is the explicit path for adopting new BC content.
- The hash computer (`FormulaCanonicalizationService.computeVariableBindingSetHash`) reads snapshot columns **as-stored** and MUST NOT refresh from current `concept_registry.*` state.

This is the test boundary for the tenant-poisoning + BCF-mutation-coupling concerns (see also §11.2 + §14.4). The impl PR's golden-fixture tests must include a case where a BCF UUID's content has changed after MC creation, and assert the hash is unchanged because the snapshot was preserved.

### 7.3 Canonical ordering

Per D-M7-5: rows sorted by `variable_role_code` ASC (lexicographic per JCS § 3.2.3). The substrate has `UNIQUE (metric_contract_version_uid, variable_role_code)` so order is deterministic.

### 7.4 Canonicalization

1. Read rows ordered by `variable_role_code`.
2. Project to canonical JSON shape:
   ```json
   [
     {
       "role": "<variable_role_code>",
       "role_kind": "<role_kind_code>",
       "bound_business_concept_id": "<uuid|null>",
       "bound_entity_id": "<uuid|null>",
       "constant_value": <json|null>,
       "representation_term": "<text|null>",
       "unit_code": "<text|null>",
       "data_type": "<text|null>"
     },
     ...
   ]
   ```
3. Apply JCS to the JSON array.
4. Compute `sha256`.

### 7.5 Output format

`sha256:<64 hex>` per substrate CHECK.

### 7.6 Ownership

`FormulaCanonicalizationService.computeVariableBindingSetHash(mcvUid: string): Promise<string>`.

---

## 8. Filter set hash

### 8.1 Input surface

`SELECT * FROM mcf.metric_filter_clause WHERE metric_contract_version_uid = <mcvUid>`. Each row contributes:

| Field | Identity-bearing | Reason |
|---|---|---|
| `clause_role_code` (where / having / pre_filter) | YES | Semantic position of the filter |
| `clause_expression_json` | YES | The sub-AST expression |
| `bound_business_concept_id` | YES | Subject BC reference |
| `operator_code` (eq / ne / lt / lte / gt / gte / in / not_in / is_null / is_not_null / between) | YES | Operator |
| `literal_value_json` | YES | RHS payload (conditional on operator) |
| `structural_sort_key` | NO | Denormalization; ordering key derived inline |
| `created_at` | NO | Audit |

### 8.2 Operator / literal canonicalization

| Aspect | Rule |
|---|---|
| `operator_code` | snake_case enum value (substrate CHECK already enforces) |
| `literal_value_json` for `in` / `not_in` | Array elements canonicalized by JCS (number normalization per §5.6) |
| `literal_value_json` for `between` | `{lower: <value>, upper: <value>}` with both bounds normalized |
| `literal_value_json` for `is_null` / `is_not_null` | MUST be NULL (substrate CHECK already enforces) |

### 8.3 Set-semantic ordering

Per MCF §4.5, filters are set-semantic for identity. The DBCP defines the canonical order as:

```
sort_key(filter) = JCS-serialize({
  role: clause_role_code,
  operator: operator_code,
  subject_bc: bound_business_concept_id,
  literal: literal_value_json,
  expression: <jcs-normalized clause_expression_json>
})
```

Filter rows are sorted by `sort_key(filter)` ASC (JCS-canonical bytes, lexicographic). The denormalized `structural_sort_key` column on the substrate is RECOMMENDED to be kept in sync via M7 service writes; the canonical computation does NOT rely on the stored value (defense in depth).

### 8.4 Empty filter set

When no filter rows exist for the MCV, the canonical input is the empty array `[]`. `sha256("[]")` is a sentinel hash that guarantees identity tuple computation has a value (per MCF §4.5 set-semantic).

### 8.5 Canonical JSON shape (per M-2 review finding)

```json
[
  {
    "role": "<clause_role_code>",
    "operator": "<operator_code>",
    "subject_bc": "<uuid|null>",
    "literal": <json|null>,
    "expression": <jcs-normalized clause_expression_json>
  },
  ...
]
```

Sorted as in §8.3, then JCS-serialized, then sha256.

**`clause_expression_json` inclusion rationale (per M-2 review finding):** The substrate `clause_expression_json jsonb NOT NULL` stores the full sub-AST of the clause. For simple operators (`eq`, `lt`, `is_null`) the expression is derivable from `(operator, subject_bc, literal)` and the `expression` field is redundant but harmless. For complex nested filter expressions (e.g. a `case` sub-expression as the LHS of a comparison) the `expression` field carries identity not derivable from the simple-operator triple. Including it unconditionally in the canonical shape is the safe choice: identity-bearing per §8.1, present in the hash, no derivation ambiguity. The M7 canonicalization service applies MCF §8.2 normalization to `clause_expression_json` BEFORE JCS-serializing it.

### 8.6 Ownership

`FormulaCanonicalizationService.computeFilterSetHash(mcvUid: string): Promise<string>`.

---

## 9. Temporal gate input kernel

### 9.1 Input surface

| Source | Field |
|---|---|
| `mcf.metric_contract` | `temporal_gate_shape_code` (closed enum per MCF §4.4) |
| `mcf.metric_contract` | `temporal_gate_params_json` (jsonb, shape-dependent) |

### 9.2 Closed shape enum (MCF §4.4)

| `temporal_gate_shape_code` | Params kernel fields | Notes |
|---|---|---|
| `instantaneous` | `{}` (empty) | No params; per-event snapshot |
| `trailing_window` | `{duration: <int>, unit: <enum>}` | Sliding window |
| `period_aggregate` | `{period_type: <enum>}` | Aggregate over a complete period |
| `point_in_time` | `{anchor_role: <variable_role_code>}` | Resolves to one observation |
| `as_of` | `{anchor_role: <variable_role_code>}` | Same shape as `point_in_time`; semantic difference |
| `rolling_window` | `{duration: <int>, unit: <enum>, period_type: <enum>}` | Rolling per period |

### 9.3 Tenant-invariant kernel definition (per D-M7-6)

The kernel is the **identity-bearing subset** of `temporal_gate_params_json`. Tenant-specific resolver paths (e.g. fiscal calendar config UUIDs, calendar version selectors) are EXCLUDED. Per shape:

| Shape | Kernel JSON |
|---|---|
| `instantaneous` | `{}` |
| `trailing_window` | `{"duration": <int>, "unit": "<unit-enum>"}` |
| `period_aggregate` | `{"period_type": "<enum>"}` |
| `point_in_time` | `{"anchor_role": "<role-code>"}` |
| `as_of` | `{"anchor_role": "<role-code>"}` |
| `rolling_window` | `{"duration": <int>, "period_type": "<enum>", "unit": "<unit-enum>"}` |

Any field present in `temporal_gate_params_json` but NOT listed in the kernel for the row's shape is IGNORED for identity hashing. This is the **tenant-poisoning prevention** mechanism (per preflight R-8): a tenant-specific path attached to the `temporal_gate_params_json` does not affect identity.

### 9.4 Temporal gate kernel canonicalization

1. Read `temporal_gate_shape_code` + `temporal_gate_params_json` from the locked parent MC row.
2. Project to kernel JSON per §9.3 (drop non-kernel fields).
3. **No pre-concatenation at this stage.** The shape code and the kernel JSON object are contributed as **two separate elements** to the JCS-canonical identity-tuple array per §10.1 (`temporal_gate_shape_code` as element 5; `temporal_gate_params_kernel` as element 6). The JCS serializer handles their individual encoding when the full array is serialized.
4. The same two elements feed the intermediate `grain_filter_temporal_dimension_signature_hash` per §11.1 (where they appear as elements 3 and 4 of that array).

### 9.5 No separate hash column

The temporal gate kernel is NOT its own hash column on `mcf.metric_contract` — it composes directly into `identity_tuple_hash` (§10). This keeps the substrate column count at 6 (which the M2/M3/M4 substrate already provides).

---

## 10. Identity tuple hash

### 10.1 Exact composition (per D-M7-8 + M-6 review finding — JCS-array encoding)

```
identity_tuple_hash = sha256(UTF-8 bytes of JCS-canonical JSON array:
  [
    formula_intent_hash,                            /* sha256:<64hex> string */
    variable_binding_set_hash,                      /* sha256:<64hex> string */
    filter_set_hash,                                /* sha256:<64hex> string */
    grain_entity_id,                                /* parent MC.grain_entity_id, UUID string */
    temporal_gate_shape_code,                       /* parent MC.temporal_gate_shape_code */
    temporal_gate_params_kernel                     /* JSON object per §9.3 */
  ]
)
```

**Why JCS-array (per M-6 review finding):** The earlier draft used string-concatenation with `:` separators. That form is theoretically vulnerable to input-boundary collisions (closed-enum + fixed-length-hash invariants prevented practical collisions, but the encoding was not cryptographically clean). JCS-array encoding eliminates the ambiguity: each tuple element is a distinct JSON array element, separated by the JSON-array syntax (`,` between elements; quoted strings; literal JSON values for the kernel). No input value can "extend" into another's slot because JSON parser unambiguously delimits each element. Operator decision D-M7-8 specified the input set; this DBCP fixes the encoding without changing the inputs.

The 6-element identity-tuple array contains 3 distinct value types: **3 sha256-prefixed hash strings** (elements 1-3: `formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash` — JSON-encoded as quoted strings like `"sha256:abc..."`), **2 plain text values** (element 4: `grain_entity_id` as a UUID string; element 5: `temporal_gate_shape_code` as a closed-enum string), and **1 JSON object** (element 6: `temporal_gate_params_kernel`, a structured kernel per §9.3, which JCS serializes inline).

### 10.2 Exclusions

The following are explicitly NOT in `identity_tuple_hash`:

| Field | Reason |
|---|---|
| `mc_name` | Descriptive; per MCF §4.7 not identity-bearing |
| `display_name` | Descriptive |
| `created_by_name` | Audit |
| `created_at` / `updated_at` | Audit |
| `archived_at` | Lifecycle, not identity |
| `candidate_source_ref_json` | Provenance, not identity |
| `mcf.metric_computed_dimension_ref.*` | Per D-M7-8: computed-dim refs belong in package signature, not identity |
| Any `mcf.metric_contract_version` descriptive columns | Versions revise descriptive-only attributes per §4.6 |

### 10.3 Output format

`sha256:<64 hex>` per substrate CHECK `mc_identity_tuple_hash_fmt_chk`.

### 10.4 Collision / algorithm-version discipline

The substrate enforces partial UNIQUE on `(identity_tuple_hash, hash_algorithm_version) WHERE archived_at IS NULL`. Two MCs with the same identity tuple under the same algorithm version cannot both be non-archived. Algorithm version bumps create a new partial-uniqueness namespace (per MCF §8.6); v1 and v2 MCs do not collide.

### 10.5 Ownership

`PackageSignatureService.computeIdentityTupleHash(mcvUid: string, contributingHashes: {formulaIntentHash, variableBindingSetHash, filterSetHash}): Promise<string>`.

Inputs to this method come from `FormulaCanonicalizationService` (the 3 sub-hashes) plus `PackageSignatureService` reads parent MC columns directly (grain_entity_id + temporal_gate_shape_code + temporal_gate_params_json) under the existing M4 lock.

### 10.6 AMENDMENT — `mcf-hash-v2`, computed-dimension identity (D470 / DEC-327d4e, 2026-06-30)

D-M7-8 deliberately **excluded** computed-dimension refs from identity (§10.2), on the reasoning that grouping was a package-signature axis only. That is **wrong for grouped metrics**: a top-N / distribution metric (e.g. *top-10 customers by AR balance*) shares its base metric's six identity inputs exactly, so under v1 it collides with the ungrouped base (*AR balance*) at the partial-UNIQUE index and at the L-V1h materialization gate — yet it is a genuinely distinct metric. This amendment corrects that.

**v2 composition (backward-compatible).** `identity_tuple_hash` gains a 7th element — the **sorted computed-dimension kernel set** (the same projection §11.2 already feeds into the intermediate/package-signature hash: `dimension_class_code` + `role_in_formula_code` + `source_business_concept_id`, sorted by canonical key; resolver paths excluded). The element is appended **only when the set is non-empty**:

```
identity_tuple_hash (v2) = sha256(JCS-array:
  [ formula_intent_hash, variable_binding_set_hash, filter_set_hash,
    grain_entity_id, temporal_gate_shape_code, temporal_gate_params_kernel
    (, sorted_computed_dimension_ref_kernel_set)  ← ONLY when grouped ]
)
```

For an **ungrouped** metric the element is omitted, so the array is the identical 6-element v1 tuple — **byte-for-byte**. This is the load-bearing property of the amendment.

**Why backward-compatible and NOT a restamp.** Active-MC identity columns (including `identity_tuple_hash` + `hash_algorithm_version`) are **immutable** — enforced by `mcf.fn_mc_active_immutability_check()`. Rewriting them in place on the live v1 corpus is a historical rewrite (Foundation **Invariant III**) and the trigger rejects it. So the v1 corpus is **never restamped**. Instead, v2's byte-compatibility for the ungrouped case lets a new v2 candidate be compared **directly against stored v1 hashes**.

**Collision discipline (supersedes §10.4's namespace-separation claim for the L-V1h gate).** The L-V1h materialization gate (`metric-authoring-materialization.service.ts`) and its `mcf-read` preflight mirror compare the candidate's stored-hash **across all algorithm versions — no `hash_algorithm_version` filter**:

- ungrouped v2 candidate vs frozen v1 ungrouped MC → identical bytes → collision **caught** (dedup against the immutable corpus preserved);
- grouped v2 candidate → distinct 7-element hash → matches no ungrouped (v1 or v2) row → **admitted**;
- only **emitted** (stored) hashes are compared — the gate never re-infers a v2 identity for a v1 metric (Foundation **Invariant VI**: evidence emitted, not reconstructed).

The partial-UNIQUE index `(identity_tuple_hash, hash_algorithm_version)` is retained as a same-version write backstop; the L-V1h gate is the authoritative cross-version dedup.

**Known residual (accepted by design).** A metric minted **grouped under v1** (dim-blind) permanently carries its *exact* ungrouped base's v1 identity. Exactly one such row exists: `top5-customers-by-gross-invoiced-amount` (`e73c91d7-…`). Concrete cost: that one specific ungrouped base (`SUM(gross_amount)` at the same grain/gate/filter) cannot be authored while top5 is active (L-V1h collision); any base differing in grain/gate/filter is unaffected, and all *new* grouped metrics are correct. **This is NOT correctable through any governed path** — supersession (the rebind service) is identity-PRESERVING (`mcf-mcv-binding-refresh-rebind-dbcp`: same identity/formula/grain/gate/filters, only bindings move), `metric-authoring-materialization` hardcodes `supersedes_version_uid=null`, and active metrics cannot be abandoned (DRAFT/REVIEW only). Correcting it would require purpose-built active-metric-replacement machinery, unwarranted here. **Accepted as a known limitation** (operator decision, 2026-06-30); top5 stays as-is. (An earlier draft proposed "re-mint via supersession" — that mechanism does not exist; supersession cannot change identity under Invariant III + identity-evaluated-once.)

**Version marker.** `MCF_HASH_ALGORITHM_VERSION = 'mcf-hash-v2'`. New mints stamp v2 regardless of grouping; for ungrouped mints the bytes coincide with v1 by design. Golden anchors (§14.7): the coordinator golden's `identity_tuple_hash` is **unchanged** (its fixture is ungrouped → byte-identical to v1); only `hash_algorithm_version` advances to v2.

---

## 11. Package signature hash

### 11.1 Exact composition (per MCF §8.7 verbatim + D-M7-6 + D-M7-8 + B-2/M-6 review findings)

Per MCF requirements §8.7 (verbatim), `package_signature_hash` is composed via a named **intermediate hash** `grain_filter_temporal_dimension_signature_hash`:

```
grain_filter_temporal_dimension_signature_hash = sha256(UTF-8 bytes of JCS-canonical JSON array:
  [
    grain_entity_id,                                /* parent MC.grain_entity_id, UUID string */
    filter_set_hash,                                /* sha256:<64hex> string per §8 */
    temporal_gate_shape_code,                       /* parent MC.temporal_gate_shape_code */
    temporal_gate_params_kernel,                   /* JSON object per §9.3 */
    sorted_computed_dimension_ref_kernel_set       /* JSON array per §11.2 */
  ]
)

package_signature_hash = sha256(UTF-8 bytes of JCS-canonical JSON array:
  [
    formula_intent_hash,                            /* sha256:<64hex> per §6 */
    variable_binding_set_hash,                      /* sha256:<64hex> per §7 */
    grain_filter_temporal_dimension_signature_hash  /* sha256:<64hex> per the intermediate above */
  ]
)
```

**Intermediate-hash rationale (per B-2 review finding):** The named `grain_filter_temporal_dimension_signature_hash` is MCF §8.7's verbatim third input to `package_signature_hash`. The earlier DBCP draft inlined all 7 inputs into a single flat concatenation, diverging from MCF §8.7 and breaking the downstream M9 fixture-binding contract (per MCF §12.7 stale-fixture rule, fixtures bind to the component sub-hashes including `grain_filter_temporal_dimension_signature_hash`). This patched §11.1 restores the intermediate hash so M9 can cite it directly.

**JCS-array encoding (per M-6 review finding):** Both the intermediate hash AND the final package signature hash use JCS-canonical JSON array encoding (same rationale as §10.1). No string-concatenation ambiguity.

The first 2 inputs to `package_signature_hash` are the identity-tuple's first 2 contributors. The 3rd input (`grain_filter_temporal_dimension_signature_hash`) carries the grain + filter + temporal + computed-dim axes — distinguishing package signature from identity tuple by including computed-dim refs (which `identity_tuple_hash` excludes per §10.2 + D-M7-8).

### 11.2 Computed-dim ref kernel set

Per D-M7-6: for each row in `mcf.metric_computed_dimension_ref WHERE metric_contract_version_uid = <mcvUid>`, the kernel contributes:

| Field | Included | Reason |
|---|---|---|
| `dimension_class_code` (fiscal_period / fiscal_year / fiscal_quarter / calendar_quarter / calendar_week_iso / derived_grain / bucket_label) | YES | Identity-bearing per §9.2 |
| `role_in_formula_code` (grain / filter / group_by) | YES | Identity-bearing — same dim class with different role is a different metric |
| `source_business_concept_id` | YES | The BCF source that's transformed by the computed dimension |
| `resolver_config_ref_json` | **NO — tenant-specific paths excluded per D-M7-6** | Tenant-poisoning prevention |
| `resolver_params_hash` | **NO** | Already covers tenant-specific params; would re-introduce tenant-poisoning |
| `structural_sort_key` | NO | Denormalization |

Canonical JSON shape per row:
```json
{
  "dimension_class": "<dimension_class_code>",
  "role_in_formula": "<role_in_formula_code>",
  "source_business_concept_id": "<uuid|null>"
}
```

### 11.3 Ordering

Rows sorted by JCS-canonical-serialization of the kernel object (lexicographic). Computed inline; the substrate `structural_sort_key` is denormalization not consulted.

### 11.4 Empty computed-dim ref set

When no computed-dim ref rows exist, the canonical input for the computed-dim kernel set is `[]` (empty JSON array). The intermediate `grain_filter_temporal_dimension_signature_hash` is still well-defined (sha256 of a JCS-canonical 5-element array whose 5th element is the empty array). `package_signature_hash` and `identity_tuple_hash` remain **structurally distinct** because they are JCS-canonical arrays of different lengths and compositions:

- `identity_tuple_hash` = `sha256(JCS([formula_intent_hash, variable_binding_set_hash, filter_set_hash, grain_entity_id, temporal_gate_shape_code, temporal_gate_params_kernel]))` — 6 elements
- `package_signature_hash` = `sha256(JCS([formula_intent_hash, variable_binding_set_hash, grain_filter_temporal_dimension_signature_hash]))` — 3 elements

Two JSON arrays of different lengths cannot serialize to the same JCS byte sequence, so the two hashes cannot collide regardless of the computed-dim ref set being empty or populated.

### 11.5 Includes/excludes summary

| In package signature? | Input |
|---|---|
| YES | formula intent hash, variable binding set hash, filter set hash, grain entity id, temporal gate shape + kernel, computed-dim ref kernel set |
| NO | tenant-specific resolver paths, tenant fiscal calendar config UUIDs, resolver params hash (already covered by D-M7-6), descriptive columns, audit columns, child row UUIDs |

### 11.6 Package-level audit use

Per MCF §8.7 + §12: the `package_signature_hash` is the **binding key for self-verification fixtures** (M9). A fixture is authored against a specific `package_signature_hash` and becomes stale per §12.7 the moment ANY contributing axis changes. The hash is computed in the substrate authoring path (M7/M8), not the client, so the binding cannot be forged.

`formula_intent_hash` alone remains the identity-tuple component for MC identity (per this DBCP §10 and MCF requirements §4.2). The composite `package_signature_hash` is for verification binding only; it does NOT replace MC identity.

### 11.7 Ownership — `computePackageSignatureHash`

`PackageSignatureService.computePackageSignatureHash(mcvUid: string, contributingHashes: {formulaIntentHash, variableBindingSetHash, filterSetHash}): Promise<string>`.

### 11.8 Ownership — `computeGrainFilterTemporalDimensionSignatureHash`

```typescript
PackageSignatureService.computeGrainFilterTemporalDimensionSignatureHash(
  mcvUid: string,
  contributingHashes: { filterSetHash: string },
): Promise<string>
```

**Visibility: public (service-level).** This method is callable directly by:
- `McfHashComputerCoordinator` when composing `package_signature_hash` (passes the precomputed `filterSetHash` from `FormulaCanonicalizationService`)
- M9 fixture-binding (per MCF §12.7 stale-fixture rule) when comparing the fixture's bound intermediate hash against the MC's current intermediate hash
- The §14.7 `GOLDEN_V1_INTERMEDIATE` golden anchor test

The method is NOT returned via `ParentHashes` (the M4 `McfHashComputer.computeAllForApproval` return shape stays unchanged per D-M7-10 — the interface widening is INPUT-only). Per §14.7 line 1044, the intermediate hash is service-level public, not returned through the coordinator interface.

**Parameter rationale:** `mcvUid` is needed to read `grain_entity_id`, `temporal_gate_shape_code`, `temporal_gate_params_json` from the locked parent MC row, plus the computed-dim refs from `mcf.metric_computed_dimension_ref WHERE metric_contract_version_uid = mcvUid`. `contributingHashes.filterSetHash` is passed in (not recomputed) to avoid duplicating `FormulaCanonicalizationService` work and to keep the §12.2 class-separation diagram intact (`PackageSignatureService` does NOT depend on `FormulaCanonicalizationService`).

---

## 12. `McfHashComputer` real implementation contract

### 12.1 Interface widening (D-M7-10 — operator must confirm)

Current M4 interface:
```typescript
export interface McfHashComputer {
  computeAllForApproval(input: { metricContractUid: string }): Promise<ParentHashes>;
}
```

Required widening:
```typescript
export interface McfHashComputer {
  computeAllForApproval(input: {
    metricContractUid: string;
    metricContractVersionUid: string;   // ADDED — required to resolve MCV-scoped child rows
  }): Promise<ParentHashes>;
}
```

**Compatibility (corrected per B-1 review finding):** The new field is **REQUIRED** (non-optional). This means:
- `MockMcfHashComputer.computeAllForApproval(input: { metricContractUid: string })` signature MUST be widened to `(input: { metricContractUid: string, metricContractVersionUid: string })` in the impl PR. The mock's body may continue to ignore the new field (placeholder hashes are still derived from `metricContractUid` only), but its method signature must match the interface.
- The M4 service's `approveForActivationInTx` call site at `mcf-cert-writer.service.ts` adds `metricContractVersionUid: input.metricContractVersionUid` to the call argument — a one-line change inside the existing locked-MCV scope.
- Existing M4 unit tests for `MockMcfHashComputer.computeAllForApproval` (the `MockMcfHashComputer` direct-call tests in `mcf-cert-writer.service.spec.ts`) need updating to pass the new field. Same for any integration tests that exercise the mock's `computeAllForApproval` directly.

**Updated impl PR deliverables in §17.1 reflect these touch points.** This DBCP does NOT claim "existing M4 tests pass unchanged" — that claim was incorrect; tests that invoke `computeAllForApproval` need a one-line argument update to compile under the widened interface.

### 12.2 Three TypeScript classes (per D-M7-2)

| Class | File | Responsibility |
|---|---|---|
| `FormulaCanonicalizationService` | `bc-core/src/registry/mcf/formula-canonicalization.service.ts` | Reads stored AST + child rows; produces `formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`; implements §4–§8 of this DBCP |
| `PackageSignatureService` | `bc-core/src/registry/mcf/package-signature.service.ts` | Reads parent MC columns (grain, temporal gate) + computed-dim refs; produces `identity_tuple_hash` + `package_signature_hash`; implements §9–§11 |
| `McfHashComputerCoordinator` | `bc-core/src/registry/mcf/mcf-hash-computer-coordinator.service.ts` | Implements the M4 `McfHashComputer` interface; calls the two services in sequence; returns the 6-tuple result + algorithm version `mcf-hash-v1`; **NestJS @Injectable** |

Class diagram:
```
McfCertWriterService (existing — M4)
    ↓ (DI)
McfHashComputer (interface — existing M4)
    ↑ implements
McfHashComputerCoordinator (new — M7/M8)
    ↓ uses           ↓ uses
FormulaCanonicalization PackageSignature
   Service                 Service
   (new — M7)              (new — M8)
```

### 12.3 Algorithm version marker

The coordinator returns `hashAlgorithmVersion: 'mcf-hash-v1'` (per D-M7-9). Substrate CHECK admits this value (`^mcf-[a-z-]+-v[0-9]+$` matches `mcf-hash-v1`). Production guard accepts it (doesn't start with `mcf-mock-` or `mock-`).

### 12.4 Algorithm-version upgrade strategy

Per MCF §8.6:
1. Algorithm change proposal → ADR (e.g. new normalization rule added in v2)
2. Implementation increments constant: `MCF_HASH_ALGORITHM_VERSION = 'mcf-hash-v2'`
3. From the deploy time forward, all NEW hash computations use `'mcf-hash-v2'` as the marker
4. Existing `active` MCs retain their v1 hash (per Foundation Invariant III — historical immutability)
5. Existing `draft` MCs whose hashes are not yet committed re-hash with v2 at approval time

Substrate partial UNIQUE on `(identity_tuple_hash, hash_algorithm_version)` keeps v1 and v2 in separate namespaces.

### 12.5 How M4 consumes it

M4 service code changes (impl PR deliverables): (1) one-line input-widening update at the `computeAllForApproval` call site per §12.1; (2) a service-side **placeholder-AST guard** added inside `approveForActivationInTx` before the hash compute (per M-4 review finding, see §12.5.1 below). The DI wiring change is at the NestJS module:

```typescript
// Production wiring (post-M7/M8 ship)
@Module({
  providers: [
    { provide: McfHashComputer, useClass: McfHashComputerCoordinator },
    FormulaCanonicalizationService,
    PackageSignatureService,
    McfCertWriterService,
    // ...
  ],
})
```

In test modules, `useClass: MockMcfHashComputer` continues to work — the mock is kept (per preflight §9.3) with its signature updated per §12.1.

### 12.5.1 Service-side placeholder-AST guard (per M-4 review finding)

The new column `mcf.metric_contract_version.formula_ast_canonical_json` has a placeholder DEFAULT per §13.2. The DBCP cannot rely solely on PE-MC-5 evaluation by the caller of `approveForActivation` to catch the placeholder, because the M4 service trusts the caller's `peEligibilityResults` verdicts without re-verifying. The impl PR therefore adds a service-side guard.

**Prerequisite — extend the existing locked SELECT** (`lockMcvAndAssertState` in `mcf-cert-writer.service.ts`): the live SQL currently SELECTs only `metric_contract_uid, governance_state_code`. The impl PR MUST extend it to also SELECT `formula_ast_canonical_json` AND `metric_contract_version_uid` (the latter for the error message). This is a one-line change to the SELECT projection. The return type of `lockMcvAndAssertState` widens accordingly.

```typescript
// Inside McfCertWriterService — extended row type returned by lockMcvAndAssertState:
type LockedMcvRow = {
  metric_contract_uid: string;
  metric_contract_version_uid: string;
  governance_state_code: string;
  formula_ast_canonical_json: unknown;
};

// Inside McfCertWriterService.approveForActivationInTx, after locking the MCV
// row but BEFORE calling hashComputer.computeAllForApproval:
private assertNonPlaceholderAst(mcvRow: LockedMcvRow): void {
  const ast = mcvRow.formula_ast_canonical_json as { kind?: string } | null;
  if (!ast || ast.kind === 'placeholder') {
    throw new InvalidStateError(
      `MCV ${mcvRow.metric_contract_version_uid} has placeholder formula AST; ` +
      `cannot approve. The M7 createMetricDraft path must replace the placeholder ` +
      `with a real AST before approveForActivation is called.`,
    );
  }
}
```

This adds a private helper (~7 lines) + one call from `approveForActivationInTx` + the SELECT extension. Listed in §17.1 impl PR deliverables. It is service-enforced (not substrate CHECK) for the same reason §13.3 defers the substrate CHECK: detecting the placeholder via service code is cheaper than a Postgres-side regex / JSON predicate.

### 12.6 Production mock guard preserved

The M4 service's `assertProductionHashAlgorithm` (per M4 DBCP §7.5) continues to fire. Behavior under `NODE_ENV='production'`:

| Marker returned by `McfHashComputer` | Matches guard predicate? | Outcome |
|---|---|---|
| `mcf-hash-v1` (real `McfHashComputerCoordinator`) | NO — does not match `startsWith('mcf-mock-')` or `startsWith('mock-')` | **Guard accepts.** Production wiring proceeds normally. |
| `mcf-mock-v1` (current `MockMcfHashComputer` post-PR #108) | YES — matches `startsWith('mcf-mock-')` | **Guard rejects** with `ConfigurationError`. Intentional — prevents accidental mock leakage into production. |
| `mock-1.0.0` (legacy pre-PR #108 mock marker, if it appears anywhere) | YES — matches `startsWith('mock-')` (defense-in-depth) | **Guard rejects** with `ConfigurationError`. |

Under non-production environments (`NODE_ENV !== 'production'`), the guard returns early per M4 DBCP §7.5 — all markers pass, including the mock. This permits the existing M4 unit + integration tests with `MockMcfHashComputer` to continue functioning unchanged.

### 12.7 In-tx semantics

Per M4 DBCP §5.3: `approveForActivation` already locks parent MC + all child rows for the MCV under `SELECT FOR UPDATE` before calling `hashComputer.computeAllForApproval`. The real coordinator's reads happen INSIDE that lock scope. Two consequences:

- **Determinism guarantee:** The coordinator reads through the M4-supplied tx, so concurrent writes are blocked. Same input → same output.
- **In-tx read budget:** The coordinator + services do read-only queries (no writes). Cost dominated by the 3 child-row counts (binding × filter × dim-ref) and is sub-linear in MC complexity. M4 §5.5 slow-flag (5s) is comfortable.

### 12.8 Determinism contract

The real implementation MUST satisfy:

| Property | Test |
|---|---|
| Determinism | Same input → same output across runs |
| Idempotency | Calling twice changes nothing externally (read-only) |
| Order-insensitivity | Re-reading child rows in different DB order produces same hash (because canonical ordering is by `variable_role_code` / filter sort_key / dim-ref kernel sort_key — NOT by row insertion order) |
| Tenant-invariance | Same MC across two tenants produces same hashes if and only if all identity-bearing inputs are identical (tenant-specific resolver paths don't leak in per §9.3 / §11.2) |

---

## 13. Substrate / Drizzle / DDL impact

### 13.1 Decision summary

| Substrate change? | Where | Reason |
|---|---|---|
| YES — ONE new column | `mcf.metric_contract_version.formula_ast_canonical_json` jsonb NOT NULL | The canonical AST must be stored; today no column exists. Without storage, M7/M8 has nothing to hash. |
| YES — ONE trigger amendment | `mcf.fn_mcv_descriptive_immutability_check` (CREATE OR REPLACE FUNCTION) | Per M-3 review finding: the trigger's enumerated "pure state-only UPDATE" column list MUST include `formula_ast_canonical_json` to enforce identity-bearing immutability at the trigger layer. Without this amendment, a same-tx UPDATE of (formula_ast_canonical_json + governance_state_code) on a draft/review row would slip past the trigger because the trigger doesn't know to check the new column. See §13.2.1 below for the trigger amendment DDL. |
| NO new table | (no `mcf.metric_formula_ast` table) | A single column on the version row is sufficient; a separate table would add a FK + index without benefit (1-to-1 with the version). |
| NO change to other tables | (no changes to `mcf.metric_contract`, child tables, or anything outside `mcf.metric_contract_version` + the M3 trigger function on `mcf.metric_contract_version`) | The 6 hash columns on parent MC stay; child tables already carry all identity-bearing fields. |

### 13.2 New column DDL

```sql
ALTER TABLE mcf.metric_contract_version
  ADD COLUMN formula_ast_canonical_json jsonb NOT NULL DEFAULT '{"kind":"placeholder","reason":"created_before_m7_apply"}'::jsonb;

-- After apply, the placeholder default supports the NOT NULL constraint for any
-- pre-existing rows (substrate is currently empty per closeout, so no rows
-- are affected; the default is defensive). The placeholder AST is not a valid
-- formula AST — it would FAIL PE-MC-5 if any MC tried to reach 'approved'
-- with it, which by construction never happens since the M7/M8 services
-- replace it on first authoring.

COMMENT ON COLUMN mcf.metric_contract_version.formula_ast_canonical_json IS
  'Canonical normalized AST per MCF §7-§8 + DBCP M7/M8. Serialized via RFC 8785 JCS after MCF §8.2 normalization. Hashed by FormulaCanonicalizationService.computeFormulaIntentHash; the hash lives on the parent mcf.metric_contract row. Per Foundation Invariant III, immutable once the parent MC reaches active state. Trigger fn_mcv_descriptive_immutability_check enforces this at the substrate layer (column added to its enumerated set per M-3 review finding; see §13.2.1).';
```

### 13.2.1 M3 descriptive-immutability trigger amendment (per M-3 review finding)

The live M3 trigger `mcf.fn_mcv_descriptive_immutability_check` (created in `docker/redesign/05-mcf-lifecycle-substrate.sql` lines 208-236) detects "pure state-only UPDATE" by checking that the 10 currently-enumerated columns are unchanged. Adding `formula_ast_canonical_json` without updating the trigger leaves an enforcement gap (verified empirically in M-3 finding):

- ✅ UPDATE-only-formula_ast on `approved` row → still rejected by the trigger's second IF (`OLD.state IN ('approved','superseded')`) — correct.
- ❌ UPDATE formula_ast + state from `draft → review` on a draft row → trigger's first IF says state changed AND **listed** columns unchanged; formula_ast not in the list, so AND-chain succeeds; trigger returns NEW. PERMITTED, but identity-bearing AST should not mutate at the same time as a state transition.
- ❌ UPDATE-only-formula_ast on `review` row → trigger falls through to RETURN NEW. PERMITTED, but identity-bearing AST should not mutate at review state per MCF §4.6.

Trigger amendment DDL (CREATE OR REPLACE FUNCTION wrapped in the same BEGIN/COMMIT as the column add):

```sql
CREATE OR REPLACE FUNCTION mcf.fn_mcv_descriptive_immutability_check()
RETURNS TRIGGER AS $$
BEGIN
  -- If only the state column changed, permit (state-transition trigger handles
  -- the state-change validation separately).
  -- M7/M8 amendment: formula_ast_canonical_json added to the enumerated set
  -- so changes to it AT THE SAME TIME as a state transition are NOT treated
  -- as "pure state-only" — they get rejected by the third IF below.
  IF OLD.governance_state_code IS DISTINCT FROM NEW.governance_state_code AND
     OLD.metric_contract_uid           IS NOT DISTINCT FROM NEW.metric_contract_uid           AND
     OLD.version_code                  IS NOT DISTINCT FROM NEW.version_code                  AND
     OLD.version_seq                   IS NOT DISTINCT FROM NEW.version_seq                   AND
     OLD.description_text              IS NOT DISTINCT FROM NEW.description_text              AND
     OLD.function_code                 IS NOT DISTINCT FROM NEW.function_code                 AND
     OLD.subfunction_code              IS NOT DISTINCT FROM NEW.subfunction_code              AND
     OLD.owner_json                    IS NOT DISTINCT FROM NEW.owner_json                    AND
     OLD.tags                          IS NOT DISTINCT FROM NEW.tags                          AND
     OLD.threshold_json                IS NOT DISTINCT FROM NEW.threshold_json                AND
     OLD.supersedes_version_uid        IS NOT DISTINCT FROM NEW.supersedes_version_uid        AND
     OLD.formula_ast_canonical_json    IS NOT DISTINCT FROM NEW.formula_ast_canonical_json    THEN
    -- Pure state-only UPDATE — state-transition trigger handles it.
    RETURN NEW;
  END IF;

  -- Rule 1: approved + superseded states reject ALL non-state mutations
  -- (Q1 invariant: approved is locked; superseded is terminal). The error
  -- message is general because the reject covers any column (tags, owner,
  -- threshold, AST — anything).
  IF OLD.governance_state_code IN ('approved', 'superseded') THEN
    RAISE EXCEPTION 'mcf.metric_contract_version % is in state % — no non-state mutations permitted (Q1: approved is locked; superseded is terminal; per M3 DBCP + M7/M8 DBCP §13.2.1)', OLD.metric_contract_version_uid, OLD.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;

  -- Rule 2 (M7/M8 amendment): identity-bearing column mutation is rejected
  -- when state was 'review' (regardless of state change in same UPDATE) and
  -- when state IS changing in the same UPDATE (any source state). Per MCF §4.6:
  -- identity-bearing changes are supersession territory; they cannot be mixed
  -- with state transitions or applied at review.
  IF (OLD.governance_state_code = 'review' AND
      OLD.formula_ast_canonical_json IS DISTINCT FROM NEW.formula_ast_canonical_json) OR
     (OLD.governance_state_code IS DISTINCT FROM NEW.governance_state_code AND
      OLD.formula_ast_canonical_json IS DISTINCT FROM NEW.formula_ast_canonical_json) THEN
    RAISE EXCEPTION 'mcf.metric_contract_version %: formula_ast_canonical_json is identity-bearing and cannot change at state=% nor in the same UPDATE as a state transition (per MCF §4.6; M7/M8 DBCP §13.2.1). Use supersession.', OLD.metric_contract_version_uid, OLD.governance_state_code
      USING ERRCODE = 'check_violation';
  END IF;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Three IFs, three semantic roles:**
1. **First IF — permit pure state-only UPDATEs.** All enumerated columns (now including `formula_ast_canonical_json`) unchanged; state-transition trigger handles the validation.
2. **Second IF — reject all non-state mutations on approved/superseded rows.** General-purpose Q1 lock; error message covers any column. (Per L-NEW-1: this restores the original M3 trigger's clearer message for the lock case.)
3. **Third IF — reject identity-bearing AST mutation on review state OR in mixed state+AST UPDATEs.** Specific to `formula_ast_canonical_json`; supersession discipline per MCF §4.6.

**B-NEW-1 closes** because the third IF catches both `(state=review AND AST changed)` AND `(state changed AND AST changed)` — covering the previously-missed `draft → review + AST change` case. Drafts may still freely mutate AST while state stays `draft` (no IF fires; default `RETURN NEW`).

**Apply timing:** Both the column add AND the trigger amendment ship in the same DDL file `07-mcf-formula-ast-storage.sql` inside one BEGIN/COMMIT. The dry-run + post-apply verifier (§14.8) cover both.

**Rollback:** Reverting the trigger amendment requires restoring the pre-amendment trigger body. The rollback DDL `07-mcf-formula-ast-storage-rollback.sql` captures the pre-amendment trigger body at dry-run time (mirrors the M3 cert-amendment pre-amendment-trigger-body.sql discipline) and emits the restoration `CREATE OR REPLACE FUNCTION` alongside the column DROP.

### 13.3 Optional substrate CHECK (deferred)

A substrate CHECK enforcing JCS canonical form (e.g. `formula_ast_canonical_json::text ~ <regex>`) is **NOT shipped in this DBCP**. Reason: JCS canonical form is structurally hard to express as a regex; relying on the M7 service to write canonical JSON + a verification check at PE-MC-5 is cheaper. The DBCP recommends a service-level invariant check that re-serializes and compares.

### 13.4 Drizzle schema change

```typescript
// bc-core/src/database/schema/mcf/metric-contract-version.ts
export const metricContractVersion = mcfSchema.table('metric_contract_version', {
  // ... existing columns ...
  formulaAstCanonicalJson: jsonb('formula_ast_canonical_json').notNull().default(
    sql`'{"kind":"placeholder","reason":"created_before_m7_apply"}'::jsonb`
  ),
});
```

One column addition; one default. No FK changes; no index changes.

**Drizzle vs DDL byte-match discipline (low cleanup):** The Drizzle `.default(sql\`...\`)` expression and the DDL `DEFAULT '...'::jsonb` literal MUST produce byte-identical default values. The post-apply verifier (§14.8) re-reads the column's `pg_attrdef.adsrc` via `pg_get_expr` and asserts byte-equality with the Drizzle schema's stored default expression. Any divergence indicates a Drizzle codegen drift.

### 13.5 No MCF metric row creation

The DDL apply gate does NOT INSERT any rows into MCF tables. The DEFAULT value handles any pre-existing rows (there are none in `mcf.metric_contract_version` per the closeout), and going forward `createMetricDraft` must populate the column with a real (non-placeholder) AST at intake.

### 13.6 Apply sequencing

| Gate | What |
|---|---|
| THIS DBCP | Docs only — no DDL, no apply |
| Next gate: M7/M8 impl PR (NO DB APPLY) | bc-core: 3 new TS service files + Drizzle schema column add + DDL file at `docker/redesign/07-mcf-formula-ast-storage.sql` + dry-run script + post-apply verifier + integration tests; NO actual psql apply |
| After impl PR merge: M7/M8 DDL apply gate (small) | Separate operator-authorized session: dry-run → operator approval → psql apply → post-apply verifier (mirrors M4 apply gate pattern at smaller scale) |
| After apply: M7/M8 evidence PR | Audit artifacts (basis-of-apply dry-run + post-apply verifier evidence) committed to bc-core; closeout doc on bc-docs-v3 |

---

## 14. Test and verifier plan

### 14.1 Unit tests (in `bc-core/src/registry/mcf/`)

| Test | Scope |
|---|---|
| **FormulaCanonicalizationService — golden AST fixtures** | 12 golden ASTs covering every node type (variable_ref / literal / aggregate / arithmetic / comparison / case / window / time_anchor_resolution / bucket_assign + 3 nested composites); assert exact canonical JSON byte sequence + exact `sha256:` hash; locks the v1 algorithm forever (changing a golden fixture means algorithm version bump) |
| **JCS round-trip** | Re-serializing a canonical JSON value MUST produce identical bytes |
| **MCF normalization rules applied in order** | 7 unit tests, one per MCF §8.2 rule (commutative ordering / constant folding / variable-rename invariance / De Morgan / CASE branch ordering / empty-filter elimination / aggregate operand recursion) |
| **Forbidden patterns rejected** | **7 unit tests** (one per MCF §7.3 pattern, corrected from earlier "6" per M-8 review finding) — each asserts the canonicalization service throws BEFORE hash computation |
| **Type promotion enforced** | 6 unit tests per MCF §7.5 — currency-squared rejection, count×number promotion, etc. |
| **Binding ordering by variable_role_code** | Tests with bindings in DB-insertion-order ≠ alphabetic order; assert canonical hash matches alphabetic-ordered hash |
| **Filter ordering by sort_key** | Same pattern with filters |
| **BCF UUID treatment** | Test that swapping a BCF UUID for a different UUID changes the binding hash; test that the same UUID across two tenants produces the same hash |
| **Empty filter set sentinel hash** | Locks the empty-filter `sha256("[]")` value |

### 14.2 Unit tests for PackageSignatureService

| Test | Scope |
|---|---|
| **Identity tuple hash composition (JCS-array per §10.1)** | Given 3 sub-hashes + grain UUID + temporal shape + kernel JSON, assert exact composed sha256 via JCS-canonical 6-element JSON array. Locks JCS-array encoding as the v1 form. |
| **Temporal gate kernel projection** | For each of the 6 shape enum values, assert kernel JSON omits tenant-specific paths |
| **Intermediate `grain_filter_temporal_dimension_signature_hash` (per B-2)** | Given grain UUID + filter_set_hash + temporal shape + kernel + sorted dim-ref kernel set, assert exact JCS-array sha256. Locks the MCF §8.7 intermediate hash that M9 fixture binding cites. |
| **Package signature hash composition (per B-2)** | Composes `[formula_intent_hash, variable_binding_set_hash, grain_filter_temporal_dimension_signature_hash]` via JCS-canonical 3-element array → sha256. Asserts the MCF §8.7 verbatim form. |
| **Computed-dim resolver kernel** | Test that swapping `resolver_config_ref_json` (tenant-specific) does NOT change `package_signature_hash` |
| **Computed-dim role_in_formula sensitivity** | Test that the same dimension_class with different `role_in_formula_code` produces a different hash |
| **BCF snapshot read-as-stored (per M-5)** | Insert binding with `representation_term_snapshot='EUR'`; simulate BCF supersession by creating a parallel BCF record with content `'USD'`; assert variable_binding_set_hash unchanged (the snapshot is the as-stored EUR; the new BC record does NOT propagate). |

### 14.3 Unit tests for McfHashComputerCoordinator

| Test | Scope |
|---|---|
| **Algorithm version is `mcf-hash-v1`** | Coordinator's `computeAllForApproval` returns `hashAlgorithmVersion: 'mcf-hash-v1'` |
| **Production guard interaction** | Inject mock; in `NODE_ENV='production'`, M4 guard catches before any DB write — assert no DB writes attempted |
| **Coordinator delegates correctly** | Spy on `FormulaCanonicalizationService` + `PackageSignatureService`; assert each method called once per `computeAllForApproval` |
| **Interface widening — REQUIRED field (per B-1)** | Coordinator REQUIRES both `metricContractUid` + `metricContractVersionUid` in input. Test passes both; mock's updated signature also accepts both (mock body ignores `metricContractVersionUid` but signature must match). Test that calling the coordinator with only `metricContractUid` (no version uid) fails TypeScript compile (smoke check via type-level assertion). |

### 14.3.1 Unit tests for service-side placeholder-AST guard (per M-4)

| Test | Scope |
|---|---|
| **`approveForActivation` rejects placeholder AST** | Insert synthetic MCV with `formula_ast_canonical_json = '{"kind":"placeholder","reason":"created_before_m7_apply"}'`. Call `approveForActivation`. Assert `InvalidStateError` thrown BEFORE `hashComputer.computeAllForApproval` is called. Use the spy from §14.3 to confirm the hash computer was never invoked. |
| **`approveForActivation` accepts real AST** | Same setup with `formula_ast_canonical_json = <valid v1 AST>`. Assert hash compute fires + state UPDATE proceeds. |

### 14.3.2 Unit / integration test for M3 trigger amendment (per M-3)

| Test | Scope |
|---|---|
| **UPDATE-only-formula_ast on `approved` row rejected by trigger** | Insert synthetic MCV at state='approved' with valid v1 AST. UPDATE only `formula_ast_canonical_json`. Assert `check_violation` error citing the amended trigger's RAISE message. |
| **UPDATE-only-formula_ast on `review` row rejected by trigger** | Same with state='review'. Assert rejection — identity-bearing column cannot mutate at review state per amended trigger **third IF** (first disjunct: `OLD.state='review' AND AST changed`). |
| **UPDATE-only-formula_ast on `draft` row PERMITTED** | Same with state='draft'. Assert no error (drafts may freely mutate AST). |
| **UPDATE state-only (no formula_ast change) on draft → review PERMITTED** | Pure state-only UPDATE; assert trigger returns NEW per first IF. |
| **UPDATE state + formula_ast simultaneously on draft → review REJECTED** | First IF doesn't fire (formula_ast changed breaks AND-chain). Second IF doesn't fire (OLD state is `draft`, not approved/superseded). **Third IF fires via the `OLD.state IS DISTINCT FROM NEW.state AND AST changed` disjunct** (per the B-NEW-1 patch to §13.2.1). Error message cites the supersession-discipline rationale per MCF §4.6. |
| **UPDATE state-only (no AST change) draft → review PERMITTED** | First IF fires — all listed columns (including `formula_ast_canonical_json`) unchanged; state transition handled by separate state-transition trigger. |
| **UPDATE state-only (no AST change) draft → review WHEN approved-state second IF would NOT fire** | Confirms the second IF only fires for approved/superseded, not draft/review state-only transitions. |

### 14.4 Tenant-poisoning tests

A specific test class because R-8 from the preflight surfaced the failure mode:

| Test | Scope |
|---|---|
| **Same MC across two tenant resolver configs → same identity_tuple_hash** | Insert MCV with computed-dim ref pointing at tenant-A resolver config; compute identity hash. Change resolver_config_ref_json to point at tenant-B config; recompute. Assert hashes are identical. |
| **Same MC → same package_signature_hash** | Same setup; assert package signature hash also identical (because kernel excludes resolver paths per §11.2). |
| **Different computed-dim class → different hashes** | Change `dimension_class_code` from `fiscal_period` to `calendar_quarter`; assert both identity and package hashes change. |

### 14.5 Order-insensitivity integration tests

Against live DB (gated on `BCCORE_INTEGRATION_DB=1`, mirrors M4 integration spec pattern):

| Test | Scope |
|---|---|
| **Binding insertion order does not affect hashes** | Create MCV; insert bindings A/B/C in order; compute hashes. Truncate; insert C/B/A; compute hashes. Assert all 6 hashes identical. |
| **Filter insertion order does not affect hashes** | Same pattern with filters. |
| **Computed-dim ref order does not affect hashes** | Same pattern. |

### 14.6 Integration test: M4 `approveForActivation` works end-to-end

Existing M4 integration spec passes 7/7 with the mock. The M7/M8 implementation PR adds 1 new integration test:

| Test | Scope |
|---|---|
| **approveForActivation with real M7/M8** | Author a draft MC + MCV with a real formula AST + bindings + filters; submit for review; approveForActivation with the real coordinator; assert the parent MC's 6 hash columns post-commit contain the real hashes (not mock); assert algorithm version = `mcf-hash-v1`. |

### 14.7 Golden hash anchor (forever-fixture)

Two anchor test cases at two layers — coordinator (returns `ParentHashes` per M4 interface) and `PackageSignatureService` (computes the intermediate `grain_filter_temporal_dimension_signature_hash` per B-2). The split is required because `ParentHashes` does not include the intermediate hash (the M4 interface contract is unchanged by this DBCP for the return shape; only the input is widened per D-M7-10). The intermediate hash method is **public at the service level** (per §11.8) so M9 fixture binding and this golden anchor can call it directly; it is NOT exposed through `ParentHashes`.

**Common golden test inputs (used by both anchors):**

```typescript
// Canonical "DSO" formula MC:
//   formula AST = (avg of (receivable_balance / sales_run_rate))
//   bindings: receivable_balance → BC <uuid-1>; sales_run_rate → BC <uuid-2>
//   filters: where bound_business_concept_id = <uuid-3>, operator = is_not_null
//   grain: <uuid-grain>
//   temporal: trailing_window(30, day)
//   computed-dim: fiscal_period role=grain source=<uuid-source>
```

**Coordinator-level golden anchor** — asserts what `McfHashComputer.computeAllForApproval` returns (matches the `ParentHashes` shape from `bc-core/src/registry/mcf/mcf-hash-computer.interface.ts`):

```typescript
const GOLDEN_V1_COORDINATOR: ParentHashes = {
  formulaIntentHash: 'sha256:...',
  variableBindingSetHash: 'sha256:...',
  filterSetHash: 'sha256:...',
  identityTupleHash: 'sha256:...',
  packageSignatureHash: 'sha256:...',
  hashAlgorithmVersion: 'mcf-hash-v1',
};
```

**`PackageSignatureService`-level golden anchor** — asserts the intermediate hash that the service computes but the coordinator does NOT expose:

```typescript
const GOLDEN_V1_INTERMEDIATE = {
  grainFilterTemporalDimensionSignatureHash: 'sha256:...',
};
// Test directly against PackageSignatureService.computeGrainFilterTemporalDimensionSignatureHash(
//   mcvUid,
//   { filterSetHash: GOLDEN_V1_COORDINATOR.filterSetHash },  // per §11.8 signature
// )
```

**Forever-lock governance (per L-1 review finding):** Implementation supplies the exact hash values when the impl PR computes them; **once the impl PR merges, those values are forever-locked under the `mcf-hash-v1` bundle marker per §12.4**. Any subsequent change to a golden value MUST be accompanied by an algorithm-version bump to `mcf-hash-v2` (and migration plan for in-flight metrics per MCF §8.6). A subsequent PR that quietly updates the golden values without a version bump MUST be rejected at review — the CI check from §5.6 (JCS library lockfile-pin) is one safeguard; the golden-fixture file itself becomes a governance artifact tracked by code review.

**On NOT widening `ParentHashes`:** The intermediate hash is exposed via the public service-level method `PackageSignatureService.computeGrainFilterTemporalDimensionSignatureHash` (per §11.8) but is NOT added to `ParentHashes`. Extending `ParentHashes` to include it would be a M4-interface change beyond D-M7-10's scope (which only widens the INPUT). The coordinator return shape is stable; M9 fixture binding (per MCF §12.7) reads the intermediate hash directly from `PackageSignatureService` via the public method declared in §11.8 (or recomputes deterministically — same inputs guaranteed).

### 14.8 Verifier scripts

The M7/M8 implementation PR ships:
- `bc-core/scripts/mcf-m7-m8-dry-run.mjs` — pre-apply: confirms `formula_ast_canonical_json` column is ABSENT on `mcf.metric_contract_version` (clean slate); confirms M3 trigger `fn_mcv_descriptive_immutability_check` body does NOT yet enumerate `formula_ast_canonical_json` (clean-slate for the trigger amendment per §13.2.1); captures pre-amendment trigger body snapshot to a `.pre-amendment-trigger-body.sql` artifact (mirrors M3 cert-amendment rollback-safety discipline); DDL file parses + sha256 captured
- `bc-core/scripts/mcf-m7-m8-post-apply-verification.mjs` — post-apply: confirms column PRESENT + NOT NULL + Drizzle default byte-matches DDL default (per §13.4 low cleanup); confirms M3 trigger body now enumerates `formula_ast_canonical_json` (exact-occurrence check); runs an end-to-end real-hash test against synthetic MCV (tx-rolled-back); runs the M-3 trigger immutability tests from §14.3.2 (tx-rolled-back).

### 14.9 No load testing in M7/M8

Per M4 pattern: load testing is deferred to M11+ panel when realistic concurrent operations exist.

---

## 15. Risks and mitigations

### 15.1 Design risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| R-1 | **Golden fixture lock-in.** Once the M7/M8 impl PR merges and the first real MC is authored, the golden v1 hashes become forever-locked. Any algorithm change requires v2 + migration. | High | Tight DBCP review surface; canonicalization rules in §4–§11 are spelled out; algorithm version `mcf-hash-v1` semantic is "bundle that covers all 6 hashes" so partial changes also bump the bundle. |
| R-2 | **AST taxonomy v1 closure incompleteness.** If panel authoring of the first 10 metrics surfaces a 10th node type, supersession + algorithm bump is required. | Medium | Pre-implementation: walk the BCF-enrichment slice's representative metrics (per `mcf-step-4-first-representative-metrics-and-bcf-enrichment-slice.md`) and confirm the 9-node taxonomy covers all of them. If not, taxonomy amendment opens BEFORE this DBCP's impl PR. |
| R-3 | **JCS implementation drift between languages.** RFC 8785 is portable, but library quality varies. | Low | bc-core TS only per D-M7-7; use the well-tested `canonicalize` npm package. Avoid hand-rolling JCS. |
| R-4 | **Temporal gate kernel completeness.** §9.3 lists 6 shapes with explicit kernels. If a 7th shape is added in v2, the kernel projection must be updated. | Medium | The DBCP locks the v1 kernel projections in §9.3; future shape additions require an ADR + algorithm version bump. |
| R-5 | **Tenant-poisoning regression.** A future panel implementation might leak tenant-specific paths into the canonical input by accident (e.g. by storing them in `clause_expression_json`). | Medium | Tenant-poisoning tests (§14.4) lock the invariant. Panel review at PE-MC-1 should re-verify. |
| R-6 | **MCV-scope vs MC-scope tension.** Bindings/filters/dim refs are at MCV level in the substrate, but identity-bearing per MCF §4.2. Without runtime enforcement that "all MCVs under a parent share identity", a future bug could create an MCV whose child rows produce a different hash than the parent stores. | Medium | M7 hash computer always reads the MCV under review (per D-M7-10 widening) — the parent's hash columns reflect ONLY the version that triggered the last hash population. The DBCP recommends a future M3 amendment to add a parent-vs-MCV consistency check at activate, but it's NOT in this DBCP scope. |
| R-7 | **`formula_ast_canonical_json` placeholder default.** The DEFAULT `'{"kind":"placeholder",...}'` is structurally valid JSON but is NOT a valid v1 AST. | Low (closed per M-4 review patch) | **CLOSED by §12.5.1 service-side guard:** `approveForActivation` now rejects placeholder AST BEFORE hash compute (no longer relies solely on PE-MC-5 caller verdicts). Defense in depth: M3 trigger amendment (§13.2.1) also rejects post-draft AST mutation to placeholder. Future substrate CHECK rejecting the literal placeholder string remains a non-blocking follow-up. |
| R-8 | **Mock signature update required.** Adding REQUIRED `metricContractVersionUid` to the interface means `MockMcfHashComputer` signature MUST be updated; existing M4 tests calling `computeAllForApproval` directly need the new field in their argument. | Low (acknowledged per B-1 review patch) | TypeScript compile catches signature mismatch immediately. Impl PR deliverables (§17.1) explicitly list `mcf-hash-computer.mock.ts` + relevant test files. The DBCP no longer claims tests pass unchanged. |
| R-9 | **Per-hash algorithm version drift in v2.** Operator chose single global marker (D-M7-4) but a future M9/M10 might want to evolve `package_signature_hash` independently of `formula_intent_hash`. | Medium | Per-hash versioning can ship as a future substrate amendment (multi-marker column). For v1, single bundle is the operator's accepted simplification. |
| R-10 | **In-tx hash compute cost.** Real AST normalization + JCS + sha256 for 6 hashes adds latency to `approveForActivation` (currently 1ms with mock; estimate <100ms with real impl for moderately complex MCs). | Medium | M4 slow-flag is 5s — 50× headroom. Profile in the impl PR; bench against a complex synthetic MC (e.g. 5 bindings × 10 filters × 3 computed-dim refs). |
| R-11 | **DDL apply gate timing.** Operator wants implementation PR before apply. If the column add is part of the impl PR but not applied, integration tests would fail (column doesn't exist on live DB). | Medium | The integration spec already conditions on `BCCORE_INTEGRATION_DB=1`; the M7/M8 spec additionally conditions on the column existing (similar pattern to M4 integration spec checking for M4 tables). |
| R-12 | **JCS-array vs string-concat composition divergence from earlier DBCP draft (per M-6 review finding).** This patched DBCP changes `identity_tuple_hash` + `package_signature_hash` + new `grain_filter_temporal_dimension_signature_hash` from string-concat-with-colons to JCS-canonical JSON arrays. The earlier draft's golden hashes (if any were computed pre-patch) would NOT match the patched-DBCP-correct values. | Medium | Mitigated by the fact that this patch lands BEFORE the impl PR opens — no golden values have been computed yet. The impl PR's golden hash anchor (§14.7) computes values against the patched DBCP's JCS-array form. Pre-patch sketches in `bc-docs-v3/docs/scratch/` (none exist; checked) would also not exist. |

### 15.2 Stop conditions

The M7/M8 implementation PR STOPS and re-frames if:
- AST taxonomy review (R-2) surfaces a 10th node type → ADR for taxonomy amendment before impl
- JCS library audit reveals correctness bugs in chosen `canonicalize` package → switch library or vendor own implementation
- Real-hash benchmark (R-10) exceeds 1s for a representative MC → optimize before merge
- Operator decides per-hash versioning is needed for v1 (override D-M7-4) → DBCP amendment

---

## 16. Operator approvals before M7/M8 implementation PR

Before the M7/M8 implementation PR opens, the operator approves these 10 items:

| # | Approval item |
|---|---|
| **O-1** | Confirm D-M7-9: algorithm version marker exact value = `mcf-hash-v1` (or override) |
| **O-2** | Confirm D-M7-10: `McfHashComputer` interface widened to **REQUIRE** `metricContractVersionUid` (mock signature update + M4 service call site + any direct mock-test arguments per B-1 review patch) |
| **O-3** | Confirm AST taxonomy v1 closure (9 nodes per §4.1) covers BCF-enrichment slice's representative metrics — taxonomy walk before impl |
| **O-4** | Confirm RFC 8785 JCS library choice (recommended: `canonicalize` npm package) + version-pinning discipline per §5.6 (exact semver in package.json; lockfile-pinned; CI check against silent upgrade) |
| **O-5** | Confirm `formula_ast_canonical_json` column add on `mcf.metric_contract_version` with placeholder default (or alternative: separate `mcf.metric_formula_ast` table) |
| **O-6** | Confirm test plan (§14) — 12+ golden fixtures + JCS round-trip + **7** normalization rules + **7** forbidden patterns (per M-8) + 6 type promotions + binding/filter/dim-ref ordering tests + tenant-poisoning tests + BCF snapshot read-as-stored test (per M-5) + placeholder-AST guard tests (per M-4) + trigger-immutability tests (per M-3) + intermediate hash test (per B-2) + M4 integration test + golden hash anchor (with forever-lock governance per L-1) |
| **O-7** | Confirm sequencing — M7/M8 impl PR (NO DB APPLY) → small-DDL apply gate (separate session, applies column add + trigger amendment atomically in one BEGIN/COMMIT per §13.2.1) → M7/M8 evidence PR |
| **O-8** | Approve the next gate: M7/M8 combined implementation PR (NO DB APPLY) |
| **O-9** (new per M-3) | Confirm M3 trigger amendment shipped as part of the M7/M8 DDL file — `fn_mcv_descriptive_immutability_check` gets `formula_ast_canonical_json` added to its enumerated set + a third-IF rejection for review-state identity-bearing mutations (per §13.2.1). |
| **O-10** (new per M-4) | Confirm service-side placeholder-AST guard added to `McfCertWriterService.approveForActivationInTx` (per §12.5.1). Rejects `formula_ast_canonical_json.kind === 'placeholder'` before hash compute. |

---

## 17. Recommended next gate

### 17.1 Recommendation: open combined M7/M8 implementation PR (NO DB APPLY)

The implementation PR ships:

| Deliverable | Location |
|---|---|
| Formula canonicalization service | `bc-core/src/registry/mcf/formula-canonicalization.service.ts` |
| Package signature service | `bc-core/src/registry/mcf/package-signature.service.ts` (computes intermediate `grain_filter_temporal_dimension_signature_hash` per B-2 + final `package_signature_hash` + `identity_tuple_hash`; all via JCS-array encoding per M-6) |
| McfHashComputer coordinator | `bc-core/src/registry/mcf/mcf-hash-computer-coordinator.service.ts` |
| Interface widening (B-1 fix) | `bc-core/src/registry/mcf/mcf-hash-computer.interface.ts` (REQUIRED `metricContractVersionUid` added — one-line change to input type) |
| **Mock signature update (per B-1)** | `bc-core/src/registry/mcf/mcf-hash-computer.mock.ts` (one-line change to `computeAllForApproval` parameter type to match widened interface; body continues to ignore the new field) |
| M4 service call-site update | `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` (one-line change at `approveForActivationInTx` call site inside locked-MCV scope) |
| **Service-side placeholder-AST guard (per M-4)** | `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` — three coordinated changes per §12.5.1: (1) extend `lockMcvAndAssertState` SELECT to include `formula_ast_canonical_json` AND `metric_contract_version_uid`; (2) widen the locked-row return type; (3) add `assertNonPlaceholderAst` private helper (~7 lines); (4) call the helper from `approveForActivationInTx` immediately after the lock and BEFORE `hashComputer.computeAllForApproval`. Net ~12 lines of service code. |
| **Existing M4 unit test updates (per B-1)** | `bc-core/src/registry/mcf/mcf-cert-writer.service.spec.ts` — update any test that constructs `computeAllForApproval` arguments directly (mock-DB path) to include `metricContractVersionUid` field. Update production-guard tests if they directly invoke `MockMcfHashComputer.computeAllForApproval`. |
| Drizzle schema column add | `bc-core/src/database/schema/mcf/metric-contract-version.ts` (Drizzle default byte-matches DDL default per §13.4) |
| **Forward DDL (column + trigger amendment per M-3)** | `bc-core/docker/redesign/07-mcf-formula-ast-storage.sql` — ONE file wrapped in BEGIN/COMMIT containing: (1) `ALTER TABLE mcf.metric_contract_version ADD COLUMN formula_ast_canonical_json jsonb NOT NULL DEFAULT ...` AND (2) `CREATE OR REPLACE FUNCTION mcf.fn_mcv_descriptive_immutability_check()` with extended column enumeration per §13.2.1. Both changes commit atomically or roll back atomically. |
| **Rollback DDL (per L-3 guard clarification)** | `bc-core/docker/redesign/07-mcf-formula-ast-storage-rollback.sql` — wrapped in BEGIN/COMMIT with `DO/RAISE EXCEPTION` precondition: refuses if any row in `mcf.metric_contract_version` has `formula_ast_canonical_json` that is NOT the literal placeholder JSON (i.e. any real AST exists). On success: `DROP COLUMN formula_ast_canonical_json` + restore pre-amendment trigger body from snapshot captured at dry-run time. |
| Dry-run script | `bc-core/scripts/mcf-m7-m8-dry-run.mjs` (captures pre-amendment trigger body to `.pre-amendment-trigger-body.sql` for rollback safety per §14.8) |
| Post-apply verifier | `bc-core/scripts/mcf-m7-m8-post-apply-verification.mjs` (column structure + Drizzle default byte-match + trigger amendment exact-occurrence + end-to-end real-hash + M-3 trigger immutability tests per §14.8 + §14.3.2) |
| Unit tests | per §14.1–§14.3 (including §14.3.1 placeholder guard + §14.3.2 trigger immutability) |
| Integration tests | per §14.5–§14.6, gated on `BCCORE_INTEGRATION_DB=1` AND column presence |
| Module wiring | NestJS module providers updated to bind real coordinator |
| **CI lockfile-pin check (per M-7)** | CI step asserting `package-lock.json` JCS-library entry unchanged when M7/M8 source unchanged (silent-upgrade detection) |

PR title (suggested): `feat(mcf): M7/M8 Formula AST + Hash/Signature Authority — FormulaCanonicalization + PackageSignature + McfHashComputerCoordinator (NO DB APPLY)`

### 17.2 Subsequent gate: small DDL apply

After the impl PR merges, a separate operator-authorized session applies the DDL (column add + M3 trigger amendment per §13.2.1, atomically in one BEGIN/COMMIT). Mirrors M4 + M3-cert-amendment apply gate patterns at smaller scale:
1. `node scripts/mcf-m7-m8-dry-run.mjs` → expect exit 0 (column absent + trigger body does NOT yet enumerate `formula_ast_canonical_json` + pre-amendment trigger body captured + DDL parses + sha256)
2. STOP for operator approval
3. `psql -v ON_ERROR_STOP=1 -f docker/redesign/07-mcf-formula-ast-storage.sql` → expect exit 0 (both column ADD + trigger CREATE OR REPLACE FUNCTION commit atomically)
4. `node scripts/mcf-m7-m8-post-apply-verification.mjs` → expect exit 0 (column present + Drizzle default byte-match + trigger body now enumerates the column + synthetic-MCV hash round-trip + M-3 trigger immutability tests pass)

### 17.3 Subsequent gate: M7/M8 evidence PR

Mirrors M4 evidence PR pattern: audit artifacts + bc-docs-v3 closeout doc.

### 17.4 What stays closed

| | Status |
|---|---|
| M7/M8 impl PR | Operator authorizes next; not opened by this DBCP |
| M7/M8 DDL apply | Pending impl PR |
| M7/M8 evidence PR | Pending apply |
| M5 panel substrate | Closed; gated on M7/M8 |
| M9 fixture substrate | Closed; gated on M7/M8 |
| M10 verifier engine | Closed; gated on M9 |
| M11 / M12 panel impls | Closed; gated on M5+M9+M10 |
| M14 / M15 REST endpoints | Closed; gated on M11 |
| Real MCF metric contracts | Closed; substrate stays empty until M11 |
| BCF data | Untouched |

---

## Document verification

- **Scope clear** — §1 frames as docs-only DBCP; §1.4 enumerates 9 discipline assertions.
- **Operator decisions accepted** — §2 itemizes D-M7-1..D-M7-8 + 2 DBCP-introduced D-M7-9/D-M7-10 requiring O-1/O-2 confirmation.
- **Live state captured** — §3 enumerates 10 mcf.* tables + 6 hash columns + M3 trigger + M4 service + 4 blocks to authoring with the 3 this DBCP resolves.
- **Formula AST v1 canonical model** — §4 restates 9-node taxonomy + closed operators (snake_case) + 6 type promotion rules + 7 forbidden patterns.
- **Canonical JSON rules** — §5 adopts RFC 8785 JCS verbatim + layers MCF §8.2 normalization above + specifies null/omission/number/string rules + JCS library version-pinning discipline (per M-7). Role-vs-BC identity reconciliation in §5.3.1 (per M-1).
- **6 hash specifications + 1 intermediate** — §6–§11 each define input surface + canonicalization + output format + ownership for `formula_intent_hash`, `variable_binding_set_hash`, `filter_set_hash`, temporal gate kernel, `identity_tuple_hash`, `package_signature_hash` (per B-2 restored MCF §8.7 verbatim via named intermediate `grain_filter_temporal_dimension_signature_hash`). Tenant-poisoning prevention surfaced explicitly in §9.3 + §11.2. JCS-array encoding adopted for identity tuple + intermediate hash + package signature (per M-6). BCF snapshot read-as-stored discipline in §7.2.1 (per M-5). `clause_expression_json` included in filter canonical shape in §8.5 (per M-2).
- **`McfHashComputer` real implementation** — §12 specifies the interface widening (D-M7-10 — REQUIRED field per B-1 review correction; mock signature update required), 3 TypeScript classes, algorithm version `mcf-hash-v1`, upgrade strategy, M4 consumption (including service-side placeholder-AST guard per §12.5.1 / M-4), production guard preservation, in-tx semantics, determinism contract.
- **Substrate impact** — §13 declares ONE new column (`formula_ast_canonical_json` jsonb NOT NULL with placeholder default) on `mcf.metric_contract_version` + ONE M3 trigger amendment (per §13.2.1 / M-3) that adds the column to the descriptive-immutability enumerated set and rejects review-state identity-bearing mutations. Both ship in one BEGIN/COMMIT DDL file. Drizzle default byte-match discipline per §13.4.
- **Test plan** — §14 covers unit tests for each service + tenant-poisoning + order-insensitivity + BCF snapshot read-as-stored (per M-5) + placeholder-AST guard tests (per M-4) + trigger immutability tests (per M-3) + intermediate hash test (per B-2) + M4 integration + golden hash anchor with forever-lock governance (per L-1).
- **Risk register** — §15 enumerates 12 risks (R-1..R-12) with severity + mitigation; 4 stop conditions. R-7 closed by §12.5.1; R-8 updated for B-1 fix; new R-12 for the JCS-array transition.
- **Operator approvals enumerated** — §16 lists 10 approvals (O-1..O-10) the operator must give before the M7/M8 implementation PR can open. O-9 (M3 trigger amendment per M-3) and O-10 (service-side placeholder guard per M-4) added by this review patch.
- **Next gate recommended** — §17 specifies the M7/M8 impl PR (NO DB APPLY) + subsequent small-DDL apply gate (column + trigger amendment atomic per §17.2) + evidence PR; §17.4 enumerates closed gates. Deliverables list (§17.1) includes mock signature update + service-side placeholder guard + M4 test updates + CI lockfile-pin check.
- **No DDL, no code, no metric authoring, no BCF touches** this session — this DBCP only.

### Patch log (2026-05-27)

| Finding | Patched section(s) |
|---|---|
| B-1 mock backward-compat claim removed | §2 (D-M7-10), §12.1, §15 R-8, §17.1 deliverables |
| B-2 intermediate hash restored | §11.1 (+ frontmatter, §14.2, §17.1) |
| M-1 role-vs-BC reconciliation | §5.3 rule 3, new §5.3.1, §7.2 |
| M-2 `clause_expression_json` in canonical shape | §8.3 sort_key, §8.5 |
| M-3 M3 trigger amendment in DDL scope | new §13.2.1, §13.1, §13.6 implicit, §14.3.2, §14.8, §17.1, §17.2, O-9 |
| M-4 service-side placeholder guard | new §12.5.1, §14.3.1, §15 R-7 closed, §17.1, O-10 |
| M-5 BCF snapshot read-as-stored | new §7.2.1, §14.2 |
| M-6 JCS-array encoding | §10.1, §11.1, §15 R-12 added |
| M-7 JCS library version pinning | §5.6, §17.1 CI check |
| M-8 forbidden-patterns count 6→7 | §14.1 |
| L-1 golden hash anchor governance | §14.7 |
| L-3 rollback DDL guard clarification | §17.1 |
| Drizzle byte-match | §13.4 |
