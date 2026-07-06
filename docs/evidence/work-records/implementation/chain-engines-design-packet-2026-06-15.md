---
title: Chain Enrichment Engine + Chain Audit Service — Design Packet
status: decisions-locked
date: 2026-06-15
amended: 2026-06-16
project: bc-core
domain: governance
subdomain: chain-engines
focus: architecture
authors:
  - anant
sessions:
  - SES-9b9b71 (initial draft)
  - SES-74258f (D1-D8 lock + v1 scope sharpening)
---

> **2026-06-16 amendment — D1-D8 LOCKED.** Operator decisions captured below. v1 scopes sharpened per audit-defines-correctness framing.

# Chain Enrichment Engine + Chain Audit Service — Design Packet

## 1. Problem statement

Today the metric-promotion path expects every binding element — entity, characteristic, business concept, canonical contract field selection, observation contract mapping — to be **ready** before M12 panel admission. When something is missing or stale, the platform's strict gates (C-FX, L-V1 a-i, PE-MC, L-node, chain_status) detect the gap and **stop**. The operator must then manually run the right authoring service (B6 createEntity, S1 registerCharacteristic, BCF correction-recommendation, C5 confirm, F3 supersession, registry-publication, CC field_selection update, MCV rebind), re-trigger the panel, and re-hit the next gate. Iteration count is high.

The platform has the **detection surface** and the **governed write surface**, but lacks the **planner-executor** that composes them under strict governance, AND lacks an **independent read-only auditor** that can certify a chain is release-ready without trusting the authoring path.

## 2. Two-engine separation

| Engine | Direction | Role |
|---|---|---|
| **Chain Enrichment Engine** (CEE) | Write (compose existing governed writes) | Find gaps, build missing pieces via governed services, produce/repair the chain |
| **Chain Audit Service** (CAS) | Read-only, deterministic | Independently verify the chain against persisted substrate. Produce signed evidence. Never authors, never mutates |

**Rationale (Two-Person Rule / calculator-grade):** the auditor must not trust the author, even if the author used governed services. A failure mode like "MVB bound to a BC head that was later superseded" cannot be caught by trusting that the binding service was governed — the auditor must independently re-derive that the BCV reference is still current. The split also forces physical isolation: CAS uses a read-only DB role, CEE uses the existing write roles.

**Audit defines correctness (operator framing, 2026-06-16):** the enrichment engine should be built to satisfy the auditor, not the other way around. CAS specifies what "correct enough to proceed" means; CEE then plans toward that specification. This inverts the usual order — verifier before writer. It's TDD at the engine level: the auditor is the test, the enricher is the implementation.

**Production path:**
```
enrich/build chain (CEE)
  → M13/M14 certify (existing services)
    → independent chain audit (CAS, mode=pre_runtime_release_audit)
      → production release / runtime binding
```

## 3. Substrate inventory

### 3.1 Governed write endpoints (CEE's tool palette)

28 endpoints inventoried (see [recon report](#) — sub-agent output). Grouped by purpose:

**BCF authoring (entity + characteristic + business concept):**
- POST `/api/bcf/registry/entities/:entityId/versions` — add entity version (B6)
- POST `/api/bcf/registry/concepts/:conceptId/versions` — add BC version
- POST `/api/bcf/registry/concepts/:conceptId/supersede` — F3 supersession
- POST `/api/bcf/registry/entities/:entityId/supersede` — entity F3 supersession
- POST `/api/bcf/registry/characteristics/admission-recommendations` (S1 + Phase 2b)
- POST `/api/bcf/registry/concepts/:conceptId/correction-recommendations`
- POST `/api/bcf/registry/entities/:entityId/correction-recommendations`
- POST `/api/bcf/registry/entities/:entityId/version-amendment-recommendations`
- POST `/api/bcf/registry-shape-certifications/confirm` (C5)
- POST `/api/bcf/registry-publications` (request + confirm phases)
- POST `/api/bcf/registry-authoring-runs` (B6 panel run)
- POST `/api/bcf/registry/phase3-orphan-repair` (R3)

**MCF promotion + lifecycle:**
- POST `/api/mcf/intakes/from-seed` + `/from-metric-definition` (M11)
- POST `/api/mcf/panel-runs` (M12)
- POST `/api/mcf/panel-runs/:panelRunUid/materialization-preflight` (M12.5 preflight)
- POST `/api/mcf/panel-runs/:panelRunUid/materialize` (M12.5)
- POST `/api/mcf/metric-contracts/:metricContractUid/evaluate-pe-mc` (M13)
- POST `/api/mcf/metric-contract-versions/:mcvUid/activate` (M14)
- POST `/api/mcf/metric-contract-versions/rebind` (MCV rebind)
- POST `/api/mcf/metric-contract-versions/:mcvUid/supersede` (M15)
- POST `/api/mcf/metric-contract-versions/:mcvUid/abandon`
- POST `/api/mcf/ops/billing-volume-retry-unlock` (one-shot retry)

**CEE composes these. CEE never bypasses these.**

### 3.2 Persisted-evidence read surface (CAS input)

11 tables, all read-only for CAS:

| Table | Records | Hash columns CAS re-derives against |
|---|---|---|
| `mcf.certification_record` | All MCF cert events (metric_create / metric_transition / metric_supersede) | `input_hash` (compared to current MCV `package_signature_hash`) |
| `mcf.metric_publication_eligibility_result` | Per-PE-MC verdict ledger (PE-MC-1..11) | None directly; `evidence_json` re-derivable |
| `mcf.metric_authoring_panel_run` + `_transcript` | M12 panel evidence | `workbench_fingerprint_hash` |
| `mcf.metric_self_verification_fixture` + `_result` | M9/M10 fixture + verifier results | `formula_intent_hash`, `package_signature_hash` (at-run vs current) |
| `mcf.metric_contract` + `_version` | Metric substrate | `identity_tuple_hash`, `package_signature_hash` (re-derive) |
| `mcf.metric_supersession` | Supersession edges | None |
| `mcf.role_grant_audit` | Role grant immutable ledger | None |
| `contract.chain_status` + `chain_trace` | L1-L7 link rollup | None (derived booleans) |
| `contract.l_node_semantic_verdict` (D366) | L1-L8 semantic verdict | `input_hash` |

## 4. Audit check mapping (operator's 11 checks)

| # | Check | Substrate reads | Pattern | Modes |
|---|---|---|---|---|
| 1 | BC active, version-bound, semantically correct | `business_concept`, `business_concept_version`, D442 `semantic_role`, `canonical_value_set` | A + B | pre_m12, regression |
| 2 | CC field selection covered by active OC union | `canonical_contract_version.field_selection`, `observation_contract_version.field_mapping` | A + B (re-compute OC union, compare) | pre_m12 |
| 3 | OC source mappings valid + role-disambiguated | `observation_contract_version.field_mapping`, D431 role labels | A | pre_m12 |
| 4 | No source-specific codes in MC filters | `metric_filter_clause` (D441 guard) | A (re-run D441 scan) | pre_m13 |
| 5 | Canonical values in canonical_value_set | `metric_filter_clause.literal_value_json` vs current `business_concept_version.canonical_value_set` | B (re-derive: literal must be in CURRENT canonical_value_set) | pre_m13, regression |
| 6 | MVB/MFC point to BCV, not BC heads | `metric_variable_binding.business_concept_version_uid`, `metric_filter_clause.business_concept_version_uid` (TSK-1ee570 B1) | A (NOT NULL) + B (BCV not superseded since binding) | pre_m14, regression |
| 7 | PE-MC gates replayable from persisted evidence | `metric_publication_eligibility_result.evidence_json` | A + B (re-run PE-MC engine against current substrate, diff) | pre_m14 |
| 8 | M13/M14 certs match current substrate hashes | `certification_record.input_hash`, `metric_contract.package_signature_hash` | B (re-derive package_signature_hash from current substrate; compare to cert-time hash. Drift = fail) | pre_m14, pre_runtime_release, regression |
| 9 | Runtime binding matches approved MC/MCV + tenant scope | `tenant.contract_binding`, `metric_contract_version.governance_state` | A + B | pre_runtime_release |
| 10 | No hidden dep on archived/superseded object | Deep walk: MC → MCV → MVB → BCV → BC → entity_version (check `archived_at` + `lifecycle_state`) | B (walk + verify) | pre_m14, pre_runtime_release, regression |
| 11 | No silent ambiguity: two OCs emit same canonical field without resolver | `observation_contract_version` cross-join on `field_mapping` | A (collision detect) | pre_m12 |

## 5. Audit modes — check applicability matrix

| Mode | Purpose | Applicable checks | Block downstream? |
|---|---|---|---|
| `pre_m12_audit` | Is substrate ready before authoring? | 1, 2, 3, 11 | If `red` — no M12 panel-run permitted |
| `pre_m13_audit` | Is draft MCV structurally sane before PE? | 1, 2, 3, 4, 5, 11 | If `red` — no M13 evaluate-pe-mc permitted |
| `pre_m14_audit` | Are PE rows complete + replayable? | 1, 2, 3, 4, 5, 6, 7, 10, 11 | If `red` — no M14 activate permitted |
| `pre_runtime_release_audit` | Safe to bind to tenant/runtime? | 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 (all) | If `red` — no tenant binding |
| `regression_audit` | Re-check active metrics after substrate changes | 1, 5, 6, 8, 10 (drift-sensitive subset) | If `red` — emit incident, do not auto-unbind |

**Mode chaining:** pre_m14 ⊇ pre_m13 ⊇ pre_m12 (strict superset). pre_runtime_release ⊇ pre_m14. regression is orthogonal — runs after the fact.

## 6. Decisions D1–D8 — LOCKED 2026-06-16

| D | Topic | Locked choice | Rationale |
|---|---|---|---|
| D1 | CEE trigger | **A** — operator-invoked v1 | Hybrid deferred to v2; prove pattern first |
| D2 | M12-from-CEE | **C** — deterministic prereq gate | Auto-invoke M12 only when chain status is `complete` + no L-node red |
| D3 | CEE rollback | **A** — per-step idempotency | No magical rollback; each governed endpoint commits independently |
| D4 | Audit evidence table | **Yes** — new `mcf.chain_audit_evidence` | Two-Person Rule: separate from authoring evidence |
| D5 | Finding taxonomy | `AUDIT_FINDING_REGISTRY_V1` (per §6.D5 below) | Fixed enum on findings_json[*].finding_code |
| D6 | Mode chaining | Strict superset | pre_m14 ⊇ pre_m13 ⊇ pre_m12; pre_runtime_release ⊇ pre_m14 |
| D7 | Determinism contract | `SERIALIZABLE READ ONLY` | Snapshot isolation; canonicalized findings; reproducible hash |
| D8 | Physical isolation | New role `chain_auditor_readonly` | Belt-and-suspenders against accidental writes |

**Sequencing:** ADR-B (CAS) **first**, then ADR-A (CEE). Auditor defines correctness; enricher implements toward it.

**V1 scope sharpening (operator, 2026-06-16):**
- **CAS v1 = `pre_m13_audit` only**, MCF draft MCV target. Other 4 modes deferred. Rationale: hits real recent pain (PE-MC-12, BCV pointers, canonical filters), runs before irreversible certification, can run read-only, exposes drift + chain gaps without solving runtime binding yet.
- **CEE v0 = `source_contract_gap_plan` target**, emits harness-compatible packet, **NO auto-apply**. Rationale: pairs with B-track FSCM via harness v1.1 sc.create_draft governed apply path. Builds engine on top of existing governance rails instead of new write surface.
- **Implementation sequence:** ADR-B decided → CAS v0 read-only impl → ADR-A decided → CEE v0 plan-only impl → B-track FSCM through these rails.

### Original decision narratives (preserved below for amendment history)



### D1: CEE trigger model
**Question:** Operator-invoked per seed/intake, always-on background sweep, or both?

**Options:**
- A. Operator-invoked only (POST /api/mcf/chain-enrichment/runs with target)
- B. Always-on sweep (cron over seed_metric queue)
- C. Both (operator can invoke; sweep handles backlog)

**Recommendation:** **A in v1, C in v2.** Operator-invoked first to prove the pattern; sweep adds operational tax we don't need until v1 is stable.

### D2: CEE human-judgment boundary
**Question:** Should CEE ever call M12 panel-run itself (M12 is an LLM-driven authoring service)?

**Options:**
- A. CEE only calls deterministic governed endpoints (B6, S1, C5, F3, publication, CC field_selection). For M12, CEE prepares the intake and **halts** for operator to invoke M12 manually.
- B. CEE calls M12 as a subroutine. Operator invokes CEE once; CEE walks the entire chain including LLM authoring.
- C. Hybrid: CEE auto-invokes M12 only when chain status indicates "all upstream substrate is ready"; otherwise halts for operator.

**Recommendation:** **C.** M12 is governed via panel composition (D444), so calling it from CEE is no different from operator calling it. But the safety gate is: CEE only invokes M12 when the *deterministic prerequisites* are met. Otherwise it halts.

### D3: CEE rollback semantics
**Question:** If step 5 of 8 fails, do steps 1-4 stay?

**Options:**
- A. Per-step idempotency. Each step is independently committed. Failure at step 5 leaves steps 1-4 in place. Operator decides whether to retry from step 5 or abandon.
- B. Per-run transaction. All steps wrapped in a transaction; failure at step 5 unwinds all.
- C. Per-phase: BCF phase commits independently of MCF phase; within each phase, all-or-nothing.

**Recommendation:** **A.** BCF substrate is heavily immutability-triggered; attempting transaction-level rollback across (entity create + char admit + BC publish + CC field add) is brittle. Per-step idempotency aligns with how the underlying services already work. CEE persists a run journal so retries pick up at the last completed step.

### D4: Audit evidence format
**Question:** Audit cert in existing `certification_record` (new action_code) or new `mcf.chain_audit_evidence` table?

**Recommendation:** **New table.** `certification_record` is authoring evidence. Mixing audit evidence blurs the Two-Person Rule. New table `mcf.chain_audit_evidence` with columns: `audit_evidence_uid`, `audit_mode_code`, `target_kind_code` (mc | mcv | tenant_binding), `target_uid`, `verdict_code` (green | yellow | red), `findings_json`, `input_substrate_snapshot_hash`, `audit_engine_version`, `computed_at`, `computed_by_role` (must be `chain_auditor_readonly`).

### D5: Finding taxonomy
**Question:** Code system for audit findings?

**Recommendation:** Fixed registry `AUDIT_FINDING_REGISTRY_V1`. One code per (operator's check × specific failure shape). Pattern: `AUDIT_C{N}_<shape>` where N is check index. Examples:
- `AUDIT_C1_BC_SUPERSEDED_NOT_REBOUND`
- `AUDIT_C2_OC_UNION_DOES_NOT_COVER_CC_FIELD`
- `AUDIT_C5_LITERAL_NOT_IN_CURRENT_CANONICAL_VALUE_SET`
- `AUDIT_C6_MVB_POINTS_TO_BC_HEAD`
- `AUDIT_C8_PACKAGE_SIGNATURE_HASH_DRIFT`
- `AUDIT_C10_DEEP_ARCHIVED_DEPENDENCY`
- `AUDIT_C11_OC_RESOLVER_AMBIGUITY`

CHECK constraint enum on `chain_audit_evidence.findings_json[*].finding_code`.

### D6: Mode chaining
**Recommendation:** Strict superset, as in §5. Each mode runs all earlier-mode checks. No "skip" path.

### D7: Determinism contract
**Recommendation:** Audit must read at a single point-in-time DB snapshot (`SET TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE`). Same substrate snapshot + same mode → identical `findings_json` (canonicalized) → identical `input_substrate_snapshot_hash`. Required for the signed-report claim.

### D8: Physical isolation
**Recommendation:** Two new DB roles:
- `chain_auditor_readonly` (READ-ONLY on all schemas) — CAS uses this exclusively
- `chain_enrichment_writer` (existing MCF + BCF write grants, no new privileges) — CEE uses this

CAS connection module reject any DDL/DML at the application layer (belt-and-suspenders). Audit cert table has trigger refusing INSERT unless `current_user = 'chain_auditor_readonly'`.

## 7. ADR-A: Chain Enrichment Engine — outline

**Status:** proposed

**Decision body:**
1. Introduce service `ChainEnrichmentService` at `bc-core/src/registry/mcf/chain-enrichment/`
2. Surface: `POST /api/mcf/chain-enrichment/runs` with target = `{kind: 'seed_metric', seed_metric_id}` or `{kind: 'mcv', mcv_uid}` or `{kind: 'intake', intake_queue_uid}`
3. Internal planning: read `chain_status` + `chain_trace` + `l_node_semantic_verdict` to identify gaps; produce ordered `EnrichmentPlan` of steps; each step references a governed endpoint + arguments
4. Execution: per-step idempotency (D3 = A); persist `ChainEnrichmentRun` journal with `step_results_json`
5. Halt conditions: (a) human-judgment boundary reached (e.g., canonical_value_set needs operator input), (b) governed endpoint returns 4xx, (c) M12 panel returns non-APPROVE
6. Resume: idempotent re-invocation skips completed steps; planner re-checks each completed step is still valid
7. New table `mcf.chain_enrichment_run` (run journal). New action_code `chain_enrichment_step` on `certification_record` for steps that mint certs
8. Vendor diversity: when CEE invokes M12, it uses standard D444 D1 panel composition; no special CEE-only composition

**Out of scope:**
- Substrate hand-edits, raw DML
- Bypassing C5 confirm
- Auto-resolving human-judgment decisions (those halt)
- Mutating tenant bindings (handled by tenant onboarding, not CEE)

**Why this location:** Repair location **D** (evaluation boundary implementation). Composes existing services; introduces no new contract grammar.

## 8. ADR-B: Chain Audit Service — outline

**Status:** proposed

**Decision body:**
1. Introduce service `ChainAuditService` at `bc-core/src/registry/mcf/chain-audit/` — physically isolated from MCF authoring services
2. Surface: `POST /api/mcf/chain-audit/runs` with `{mode: <one of 5>, target: {kind, uid}}`
3. New table `mcf.chain_audit_evidence` (per D4 above)
4. New DB role `chain_auditor_readonly` (per D8); service uses dedicated connection pool with this role
5. Finding taxonomy fixed `AUDIT_FINDING_REGISTRY_V1` (per D5); CHECK constraint enum on findings_json
6. Per-check implementation: each of the 11 checks has a dedicated executor function. Pattern A executors read + shape-verify. Pattern B executors re-derive + diff.
7. Deterministic: serializable read-only transaction; canonicalized findings; substrate snapshot hash stamped
8. Mode chaining: strict superset (D6); pre_m14 runs all pre_m12 + pre_m13 + pre_m14-specific checks
9. Output: signed evidence row + machine-readable verdict (green/yellow/red) + per-finding detail
10. Gating: callers (CEE, M13 evaluator, M14 activator, tenant binding flow) MAY query latest audit verdict for a target before allowing their action

**Out of scope:**
- Authoring or repair (CEE's job)
- Auto-remediation
- Real-time evaluation (this is governance, not runtime)
- Per-tenant runtime fact verification (different concern)

**Why this location:** Repair location **F** (read model + diagnostics). Read-only verifier over persisted substrate; introduces evidence shape but does not change semantics.

## 9. Open questions for operator

1. **D1 trigger:** lock A (operator-invoked v1) or jump to C (hybrid)?
2. **D2 M12-from-CEE:** lock C (deterministic prereqs gate M12 auto-invocation)?
3. **D3 rollback:** lock A (per-step idempotency)?
4. **D4 evidence table:** new `mcf.chain_audit_evidence` table OK?
5. **D7 isolation level:** SERIALIZABLE READ ONLY sufficient, or need explicit snapshot ID?
6. **D8 DB role:** create `chain_auditor_readonly` as new role, or use existing `barecount_ro` if one exists?
7. **Sequencing:** ADR-A first (enrichment) or ADR-B first (audit)? Recommendation: **B first** — auditor is the simpler/safer surface, and CEE's success criteria depend on the auditor's pass verdict.
8. **Scope discipline:** should the v1 ship support only one CEE target kind (e.g. `seed_metric`) and one audit mode (`pre_m12_audit`), then expand? Recommendation: **yes** — proves the pattern end-to-end on the narrowest slice.

## 10. References

- D305 ChainStatusService SSOT (ADR-bebaec)
- D366 L-node verification (ADR-804874)
- D422 MCF foundational (ADR-c3e57f)
- D425 Phase 2 panel composition (ADR-09f86b)
- D441 source-literal guard (ADR-46ff0a / ADR-61850f / ADR-6b35e0)
- D444 Phase 1 panel composition v3 (ADR-5cb154)
- TSK-1ee570 B1 BCV pointer columns
- TSK-08461b structured envelope tool
- MC chain integrity SOP `bc-docs-v3/docs/onboarding/mc-chain-integrity.md`
- Foundation invariants `bc-docs-v3/docs/foundation/the-invariants.md`
- Evaluation boundaries `bc-docs-v3/docs/foundation/the-evaluation-boundaries.md`
