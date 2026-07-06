---
uid: metric-context-framework-m4-lifecycle-certification-dbcp
title: MCF M4 — Lifecycle Certification / Transition Authority DBCP
description: Database Change Protocol design for MCF Gate M4 (lifecycle certification + transition authority), REWRITTEN post-M3-cert-amendment to target the live `mcf.certification_record` per-framework sibling table (per Option C from cert substrate correction preflight 637e667). Resolves all 20 preflight decisions (D-1 through D-20; D-19 reversed from "REUSE contract.certification_record" to "PER-FRAMEWORK SIBLING mcf.certification_record"; D-17 retired — old contract-cert-index no longer applies) and specifies the exact M4 surface — two new tables (`mcf.metric_publication_eligibility_result`, `mcf.metric_cert_writer_idempotency`), one TypeScript service (`McfCertWriterService`) with five methods covering all four lifecycle transitions writing to `mcf.certification_record`, one interface (`McfHashComputer`) declared by M4 and implemented by M7/M8 later, one mock (`MockMcfHashComputer`) shipped with M4 for synthetic-row tests with a mandatory production guard refusing `mock-*` algorithm versions in `NODE_ENV='production'`, two `contract.operator_confirm_rule` seed rows (always-confirm with ≥40-char rationale; `action_code='require_operator_confirm'` per corrected semantic distinction), one `contract.framework_policy` seed row for `scope_code='mcf'` (admissible post-amendment), single-transaction discipline with **in-tx hash computation** for `approveForActivation` after acquiring SELECT FOR UPDATE locks on MCV + parent MC + all child rows (race-correctness binding per §5.3), **cert-before-PE-rows ordering** in `activateMetric` for strict append-only discipline, per-action-code cert row population matrix over the **25-column `mcf.certification_record` sibling schema** (drops `governance_scope` + `target_registry_id` from the BCF-shared shape), operator-confirm boundary matching MCF §11.4, idempotency table with single-column PK on `idempotency_key` + stuck-pending cleanup (5-min timeout), `policyVersion` validation requiring active `framework_policy` row, error-handling and rollback story, implementation-sequencing options, dry-run preconditions that REFUSE TO PROCEED if DB is pre-amendment (M3 cert-amendment is a hard prerequisite), 14-check test plan including positive + negative trigger exercises plus production-guard and stuck-pending and cert-before-PE-rows tests against synthetic-row fixtures, risks updated to mark the old cert-reuse risk as RESOLVED-by-M3-amendment with new residual risk M4-depends-on-amendment. Patched post-review per §1.6 (13 P-* patches + 8 cleanup patches) + REWRITTEN per §1.6.2 cert-amendment rewrite round. Explicit non-responsibilities (formula AST algorithm, package signature algorithm, PE-MC evaluator, panel substrate/execution, REST/MCP endpoints, MCF contract rows, BCF writes, DDL apply, legacy MC reorganization, **modifications to M3 trigger or fk_mcs_cert FK or mcf.certification_record table itself — all M3-amendment-owned**). Doc-only design; no DDL applied; no bc-core schema edited; no MCF metric contracts created; no certification rows written.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m4-dbcp
---

# MCF M4 — Lifecycle Certification / Transition Authority DBCP

## 1. Scope and grounding

### 1.1 Purpose

The Database Change Protocol design for MCF Gate M4. This DBCP is the implementation specification that the next gate (M4 implementation PR) will realize verbatim. It resolves all 20 decisions left open in the M4 preflight (`bc-docs-v3 dd54f44`), then specifies the exact table, service class, interface, mock, seed rows, transaction patterns, validation rules, error semantics, concurrency strategy, test plan, and implementation sequencing.

The DBCP is **docs-only**. No DDL is applied. No bc-core source files are edited. No MCF metric contracts are created. No certification rows are written. This document is the design that an operator-authorized execution PR (or set of PRs — see §13) will later commit to bc-core, and that a subsequent Database Change Protocol session will later apply to `bc_platform_dev`.

### 1.2 Design surface vs. implementation sequencing

**Design surface (this DBCP):** the full lifecycle certification authority — one service class composing three cert writers + four transition orchestrators + one PE-result substrate + interface boundary for hash population + operator-confirm seeds. This is the operator's bundled framing from the preflight §1.5.

**Implementation sequencing (subject to D-1.b in §3):** the design surface may ship as **one PR** (everything together) or as **three sequenced sub-PRs** (substrate first, service second, seed-and-policy third). Sequencing is a tactical choice; the design is identical either way. Option weighing is in §13.

This is one of the explicit operator decisions (D-1) and the only one that affects how the implementation gate is structured, not what is built.

### 1.3 What this DBCP is and is not

| | This DBCP |
|---|---|
| Is | The full column-level + method-level + interface-level specification for the M4 surface. |
| Is | The formal resolution of all 20 preflight decisions with rationale. |
| Is | The transaction shape, validation rules, error semantics, concurrency strategy, test plan, and sequencing options. |
| Is not | A bc-core implementation. No source file is edited; no DDL committed. |
| Is not | A DDL apply. The `psql` apply is a separate operator-authorized Database Change Protocol session. |
| Is not | An M5 / M7 / M8 / M9 / M11 / M12 / M14 / M15 design. Those gates are downstream of M4. |
| Is not | A REST or MCP endpoint surface. Endpoints belong to M14 / M15 / endpoint-specific gates. |
| Is not | A panel substrate or execution. M4 cert writer accepts panel context as input; it does not invoke a panel. |
| Is not | A reorganization of legacy `contract.metric_contract*` or `metric.metric_binding`. §16 affirms the boundary. |

### 1.4 Source documents consumed

| Source | Role | Commit / location |
|---|---|---|
| MCF M1 ADR (DEC-c3e57f / D422) | Foundational authority; locks 5-state lifecycle + cert reuse + operator-confirm at `approved → active`; locks the seven guardrails | `ADR-c3e57f.md` |
| MCF requirements §10, §11.3, §11.4, §11.5, §13, §17.1, §17.3 | Lifecycle states, transition actor matrix, MCF actions requiring operator-confirm, Foundation Governance Substrate cert reuse, PE-MC-1..PE-MC-10 closed enum + verdicts, table inventory | `metric-context-framework-requirements.md` |
| MCF build plan §4.2 (Gates M3 / M4 / M14 / M15) + risk table R-13 | Gate scope, cross-framework Foundation Governance Substrate write coupling risk | `metric-context-framework-build-plan.md` |
| M4 preflight | 20 decisions D-1..D-20 with recommended defaults; non-responsibility list; cert column population matrix sketch | `metric-context-framework-m4-lifecycle-certification-preflight.md` (`dd54f44`) |
| M3 DBCP §6.3, §7, §8.3, §9, §11–§18 | Live trigger logic (`fn_mcv_state_transition_check`); cert lookup semantics at `→ active`; supersession trigger semantics at `→ superseded`; cert reuse pattern; DDL sequencing discipline; verifier structure; rollback DDL pattern | `metric-context-framework-m3-lifecycle-substrate-dbcp.md` (`3147bd4`+`938fb0f`) |
| M3 apply closeout | M3 substrate live state | `mcf-m3-ddl-apply-closeout.md` (`d1f67d0`) |
| **Live `mcf.certification_record` schema (25 cols, M3-cert-amendment-shipped)** | Per-column population matrix grounding — the per-framework sibling table that M4 writes to | `bc_platform_dev` |
| Live `contract.framework_policy` schema (12 cols; `scope_code` CHECK extended to admit `'mcf'` per amendment) | Policy seed row shape | `bc_platform_dev` |
| Live `contract.operator_confirm_rule` schema (7 cols; `scope` + `transition` CHECKs extended per amendment; `action_code` CHECK UNCHANGED per D-Correction-4) | Per-transition operator-confirm rule shape | `bc_platform_dev` |
| Live `contract.certification_record` schema (27 cols) | Reference only — BCF cert table; M4 does NOT write here post-D-19-reversal | `bc_platform_dev` |
| M3 lifecycle DDL + M3 cert-amendment DDL | The 7 triggers M4 service composes with (cert-lookup target now `mcf.certification_record`) | `bc-core/docker/redesign/05-mcf-lifecycle-substrate.sql` + `05a-mcf-cert-amendment.sql` |

### 1.5 Discipline assertions

| Assertion | Status |
|---|---|
| No bc-core source edits | ✓ — read-only this session |
| No DDL applied | ✓ — this DBCP is design-only |
| No MCF metric contracts created | ✓ — substrate stays empty |
| No certification rows written | ✓ — substrate stays empty |
| No legacy MC migration or reorganization | ✓ — §16 affirms |
| No M5 / M7 / M8 / M9 / M11 / M12 / M14 / M15 design | ✓ — references-only |
| No REST / MCP endpoint design | ✓ — service contract only |
| No BCF data touched | ✓ — unchanged |
| `bc-postgres` MCP `allow_write` | unchanged (`false`) |

### 1.6 Patch history (post-review)

This DBCP underwent a critical review after initial authoring (`ea20be2`). The review identified 13 findings (F-1 through F-13) plus 5 open questions (Q-1 through Q-5). The operator resolved all 5 open questions and approved patches P-1 through P-13. The current text reflects the patched design:

| Patch | Finding | Where patched | Resolution |
|---|---|---|---|
| P-1 | F-1 race-condition mitigation | §3.4, §5.2, §5.3, §8.3 | Hash computation moved INSIDE the `approveForActivation` tx, after acquiring SELECT FOR UPDATE locks on MCV + parent MC + all child rows. Q-1: correctness beats latency at the authority boundary. |
| P-2 | F-2 PE row ordering | §8.4.2 | Cert INSERT now precedes PE result row INSERT in `activateMetric`; PE rows reference `certification_record_id` at INSERT time. No backfill UPDATE — strict append-only. |
| P-3 | F-3 mock production guard | §3.5, §7.5 | M4 service throws `ConfigurationError` if `hashAlgorithmVersion` starts with `'mock-'` in `process.env.NODE_ENV === 'production'`. Q-2 resolved as throw-in-production. |
| P-4 | F-4 §3.4 vs §5.3 contradiction | §3.4, §5.2, §5.3, §8.3 | All three sections now consistently specify in-tx hash computation per P-1. |
| P-5 | F-5 R-14 wording | §15.2 R-14 | "Unconditionally" replaced with "conditionally per D-17". |
| P-6 | F-6 rollback DDL | §12.5 | `operator_confirm_rule` DELETE now uses `WHERE scope = 'mcf'` (authoritative discriminator) instead of `WHERE rule_uid LIKE 'mcf_%'` (convention). |
| P-7 | F-7 policy_version validation | §6.7, §6.8, §9.2 | Service validates `policyVersion` references an ACTIVE `framework_policy` row (`effective_to IS NULL OR effective_to > now()`). Archived versions cannot be referenced. Q-4 resolved as active-required. |
| P-8 | F-8 framework_policy lifecycle | §10.4 (new) | Documented lifecycle pattern: one active row per scope; amendments INSERT new + UPDATE old `effective_to`. |
| P-9 | F-9 idempotency PK | §11.3, §11.4 | Single-column PK on `idempotency_key` (Q-3 resolution); `action_code` is non-key metadata. Mismatched reuse throws `IdempotencyKeyReuseError`. |
| P-10 | F-10 stuck-pending cleanup | §11.6 (new) | Pending rows older than 5 minutes treated as orphaned; cleanup script promotes to `rolled_back`. |
| P-11 | F-11 D-17 condition concrete | §3.17, §14.1 check #7a | Condition: ship the partial index iff no existing index on `contract.certification_record` has `primitive_id` as leading column; mechanically verified by dry-run via `pg_indexes` query. |
| P-12 | F-12 PR line estimate | §13.1, §13.3 | Estimate revised to 2500–3500 lines; revisit-sequencing threshold raised to 4000 lines. |
| P-13 | F-13 M3 trigger dependency | §8.4.3 | Note pinning the M3 descriptive-immutability trigger's behavior on `is_current` UPDATEs against active rows. Future M3 amendments must preserve or coordinate. |

Q-5 (rehash-without-supersede escape path): deferred to M7/M8 DBCP per operator decision. M4 ships no escape path.

#### 1.6.1 Cleanup batch (post-verification review)

After the P-1..P-13 round, a second verification review (against `a248a4b`) identified 8 LOW findings — clarity/wording only; no substantive design changes. Patches P-14..P-21 applied:

| Patch | Finding | Where patched | Resolution |
|---|---|---|---|
| P-14 | L-7 §3.2 cert-payload constraint scope | §3.2 | Constraint clarified as "applies to certificate-writing methods only" (createMetricDraft / activateMetric / supersedeMetric); `approveForActivation` pre-assembles only `peEligibilityResults`; `submitForReview` needs no pre-assembly. |
| P-15 | L-3 §6.8 supersedesPrimitiveId misleading | §6.8 | Row clarified — `supersedes_primitive_id` is service-derived from `predecessorMetricContractVersionUid`, not a caller-exposed field on `CertContextInput`. |
| P-16 | L-8 §7.2 M7/M8 file names speculative | §7.2 | File list reframed as illustrative-only; M7/M8 DBCPs own final filenames. |
| P-17 | L-1 §11.1 lock row stale | §11.1 | `approveForActivation` lock row updated to "MCV + parent MC + ALL child rows" per §5.3 + §8.3. |
| P-18 | L-2 §11.3 "every write method" wrong | §11.3 | Explicit list: idempotencyKey accepted by createMetricDraft / activateMetric / supersedeMetric only in v1. |
| P-19 | L-4 §14.2 check #5 conditional missing | §14.2 #5 | Verdict bound to dry-run #7a outcome (PRESENT → absent; ABSENT → present). |
| P-20 | L-5 DDL apply order absent | §12.6 (new) | Explicit 5-step apply order with idempotency notes. Mirrors M3 DBCP §11. |
| P-21 | L-6 COMMENT statements unenumerated | §12.7 (new) | 2 required COMMENT ON TABLE + ≥8 required COMMENT ON COLUMN enumerated. §14.1 check #7 statement count updated. |

No substantive design change in this cleanup batch. Verification: P-1..P-13 (in-tx hash, cert-before-PE-rows, mock production guard, single-column idempotency PK, active-policy validation, scope-based rollback DELETE, D-17 mechanical check) all preserved verbatim.

#### 1.6.2 Cert-amendment rewrite (post-M3-amendment-apply)

The M4 DBCP's original cert-reuse design (D-19: write MCF certs into `contract.certification_record` scoped by `governance_scope='mcf'`) was rejected by 10 live Foundation Governance Substrate CHECK constraints at the M4 implementation pre-read. The correction preflight (`bc-docs-v3 637e667`) evaluated 3 options; the operator accepted Option C (hybrid): per-framework `mcf.certification_record` sibling table + additive shared CHECK extensions on `framework_policy` + `operator_confirm_rule`. The M3 cert-amendment DBCP (`bc-docs-v3 06d369c`, 8 P-Amendment patches) specified the substrate change; the amendment was implemented in bc-core PR #105 (squash `b059b18`), applied to `bc_platform_dev` under explicit operator approval, verified 15/15 PASS, and closed out at `bc-docs-v3 60efd9d`.

This DBCP is now rewritten to target the live `mcf.certification_record` sibling. P-22..P-29 substantive patches applied:

| Patch | Where rewritten | Resolution |
|---|---|---|
| P-22 | Frontmatter description + §3.19 D-19 | D-19 REVERSED — from "REUSE contract.certification_record" to "PER-FRAMEWORK SIBLING mcf.certification_record" (confirms M3 amendment / D-Correction-1 Option C). |
| P-23 | §3.17 D-17 | D-17 RETIRED — the conditional partial index on `contract.certification_record (governance_scope, action_code, primitive_id) WHERE governance_scope='mcf'` no longer applies because MCF certs do not write to `contract.certification_record`. The M3 cert-amendment already shipped `idx_mcf_cert_lookup` on the sibling for the trigger hot path. |
| P-24 | §2 live state recap | Updated to post-amendment state: 8 mcf.* tables (incl. `certification_record`); M3 trigger redirected to sibling; `fk_mcs_cert` redirected to sibling; shared CHECKs extended additively. |
| P-25 | §4.3 + §8.1/§8.4/§8.5 transaction bodies + §5.2 inside-tx list | All MCF cert INSERTs target `mcf.certification_record` (was `contract.certification_record`); `governanceScope: 'mcf'` field references removed (sibling has no such column). |
| P-26 | §9 cert column matrix | Renamed §9 title from `contract.certification_record row contract` to `mcf.certification_record row contract`. Matrix reduced from 27 to 25 columns: dropped `governance_scope` (single-table) and `target_registry_id` (BCF Registry Model A specific). |
| P-27 | §10.1 operator_confirm_rule seeds | Corrected semantic confusion: `operator_confirm_rule.action_code` populated as `'require_operator_confirm'` (enforcement directive), NOT `'metric_transition'` / `'metric_supersede'` (which are MCF cert action codes — they live on `mcf.certification_record.action_code`). Added §10.5 explicit distinction note. |
| P-28 | §14.1 dry-run preconditions + §14.2 verifier | Preconditions REWRITTEN: `mcf.certification_record` exists (M3 amendment applied); M3 trigger reads from sibling; `fk_mcs_cert` targets sibling; shared CHECKs admit `'mcf'` / `'active_to_superseded'`; `operator_confirm_rule.action_code` UNCHANGED (regression). REMOVED: old precondition for `contract.certification_record` `governance_scope='mcf'` index. ADDED guard: dry-run REFUSES TO PROCEED if DB is pre-amendment. |
| P-29 | §15 risks + §17 approvals + §13 sequencing + §12.5 rollback | Old cert-reuse risk (R-2) marked RESOLVED-by-M3-amendment. New residual risk R-15: M4 depends on M3 amendment being applied. M4 DDL apply order updated: no more `mcf.certification_record` CREATE TABLE (amendment did); no more `contract.*` CHECK ALTERs (amendment did); M4 ships only `mcf.metric_publication_eligibility_result` + `mcf.metric_cert_writer_idempotency` + MCF seed rows. M4 rollback DDL simplified to drop only the two M4-shipped tables + delete MCF seed rows. Approvals re-numbered. |

No design intent changes; the cert-writing semantics (single tx; cert-before-PE-rows; in-tx hash; production guard; idempotency; active-policy validation) are preserved verbatim. The change is **only the cert target** — sibling table instead of shared table — plus the consequential updates.

---

## 2. Current live M2 + M3 state (post-cert-amendment)

Per the M3 cert-amendment apply closeout (`bc-docs-v3 60efd9d`) + amendment evidence PR (`bc-core` PR #106 / `7b73c8f`), the live state of `bc_platform_dev` going into M4:

| Asset | State |
|---|---|
| `mcf` schema | present |
| `mcf.metric_contract` (17 cols, 0 rows) | identity-bearing parent; hash columns nullable in M2; identity-immutability trigger attached |
| `mcf.metric_contract_version` (15 cols, 0 rows) | descriptive body + `governance_state_code` (5-state CHECK enum); 3 triggers attached (state-transition + descriptive-immutability + revision-emit) |
| `mcf.metric_variable_binding` (13 cols, 0 rows) | child; immutability trigger attached |
| `mcf.metric_filter_clause` (9 cols, 0 rows) | child; immutability trigger attached |
| `mcf.metric_computed_dimension_ref` (9 cols, 0 rows) | child; immutability trigger attached |
| `mcf.metric_contract_revision` (9 cols, 0 rows) | M3-shipped; revision audit |
| `mcf.metric_supersession` (11 cols, 0 rows) | M3-shipped; **FK `fk_mcs_cert` REDIRECTED by amendment to `mcf.certification_record(certification_record_id)`** |
| **`mcf.certification_record` (25 cols, 0 rows)** | **M3-cert-amendment-shipped per-framework sibling. 10 CHECK constraints (incl. NF1 6-field all-or-none), 5 indexes (incl. `idx_mcf_cert_lookup` for trigger hot path), 1 cross-schema FK to `contract.panel_output_record`. Drops `governance_scope` + `target_registry_id` from BCF cert shape. This is where M4 writes all MCF certs.** |
| 7 trigger functions in `mcf` | all live |
| 7 triggers attached | all live |
| `mcf.fn_mcv_state_transition_check` cert-lookup target | **REDIRECTED by amendment** — queries `FROM mcf.certification_record cr WHERE primitive_type='metric_contract_version' AND ... AND is_archived_after IS NOT TRUE` at `→ active` |
| `contract.certification_record` (27 cols) | Foundation Governance Substrate; **NOT a target for MCF writes** (M4 writes to `mcf.certification_record` per the amendment). Still BCF substrate. |
| `contract.framework_policy` (12 cols) | BCF rows present. **CHECK extended by amendment**: `scope_code` admits `'mcf'` additively. No MCF row yet — M4 will seed. |
| `contract.operator_confirm_rule` (7 cols) | BCF rows present. **CHECKs extended by amendment**: `scope` admits `'mcf'`; `transition` admits `'active_to_superseded'`. `action_code` UNCHANGED (regression-asserted at amendment apply). No MCF rows yet — M4 will seed. |

M3 wrote the structural enforcement layer. M4 writes the service that produces rows satisfying that enforcement.

The state-transition trigger (`mcf.fn_mcv_state_transition_check()`, M3 DBCP §6.3) is the most consequential point of contact for M4:

- At INSERT: rejects rows that don't start at `'draft'`
- At `→ approved`: rejects unless parent has all 6 hashes NOT NULL
- At `→ active`: rejects unless a `mcf.certification_record` row exists with `primitive_type='metric_contract_version'`, `primitive_id=<mcv_uid>`, `action_code='metric_transition'`, `from_state_code='approved'`, `to_state_code='active'`, `is_archived_after IS NOT TRUE` (sibling table per M3 cert-amendment; trigger redirect verified at amendment apply check #6: exactly 1 `FROM mcf.certification_record` + 0 `FROM contract.certification_record`)
- At `→ superseded`: rejects unless a matching `mcf.metric_supersession` row exists with successor `state='active'` AND `is_current=TRUE`

M4 service methods produce rows that satisfy each of these in a single transaction.

---

## 3. M4 decision log D-1 through D-20

Each preflight decision is resolved here. The DBCP design (§§4–14) implements these resolutions verbatim.

### 3.1 D-1 — M4 scope (narrow vs bundled)

**Decision:** BUNDLED. M4 designs the full lifecycle certification authority — three cert writers (`metric_create`, `metric_transition`, `metric_supersede`) + the PE-result substrate + operator-confirm + framework-policy seeding + hash interface — as one coherent design surface.

**Why:** Build plan's three-gate split (Gate M4 PE substrate / Gate M14 publication path / Gate M15 supersession path) optimizes for endpoint-surface ownership, not service-contract coherence. The service contract is a single object (`McfCertWriterService`); splitting its design across three docs would fracture the transaction discipline and the operator-confirm semantics. The endpoint surfaces (REST/MCP) remain split per the build plan, but the service that those endpoints call is one.

**Sub-decision D-1.b — implementation sequencing.** The bundled design may ship as one PR or as up to three sub-PRs (substrate / service / seed-policy). See §13 for the tradeoff and recommendation.

### 3.2 D-2 — Transaction discipline (single tx vs two tx + idempotency)

**Decision:** SINGLE TX. Every M4 write method opens one DB transaction, INSERTs the cert (if applicable), INSERTs the supersession-row (if applicable), then issues the `governance_state_code` UPDATE. All commit or all roll back.

**Why:** Postgres trigger semantics: a `BEFORE UPDATE` trigger sees the same transaction's pending INSERTs via the transaction snapshot. The M3 state-transition trigger's `SELECT EXISTS (...)` against **`mcf.certification_record`** (sibling target post-amendment) returns true for the same-tx cert. Two-tx + idempotency adds orphan-cert risk between commits without behavioral benefit at expected throughput.

**Constraint (applies to certificate-writing methods only — `createMetricDraft`, `activateMetric`, `supersedeMetric`):** the caller pre-assembles the cert payload BEFORE invoking the method. The tx body does INSERT(s) + UPDATE and, for `approveForActivation`, in-tx hash computation per §5.3. Cert payload assembly (cert metadata, JWT context, panel-context lookup) is the caller's responsibility outside the tx for those three methods. For `approveForActivation` (no cert at this transition), the caller pre-assembles `peEligibilityResults` only. For `submitForReview` (no cert; minimal input), no pre-assembly is needed.

### 3.3 D-3 — `dryRun: boolean` parameter on write methods

**Decision:** YES. Every M4 write method accepts an optional `dryRun?: boolean` parameter. When `true`, the method runs the full transaction including INSERTs and UPDATEs (so the M3 triggers fire and validate), then **rolls back** rather than committing. Returns the would-be IDs and any trigger-error messages.

**Why:** Development ergonomics. Allows the caller to test "would this transition succeed?" without touching production data. Mirrors the M3 post-apply verifier's INSERT-then-ROLLBACK pattern (`mcf-m3-post-apply-verification.mjs`). Adds no surface beyond a parameter.

### 3.4 D-4 — Hash population responsibility (M4 / separate service / block)

**Decision:** SEPARATE SERVICE (Option B). M4 declares the `McfHashComputer` interface (§7). M7 and M8 ship implementations in their respective gates. M4 calls `McfHashComputer.computeAllForApproval(...)` **inside** the `approveForActivation` transaction, **after acquiring locks on the MCV + parent MC + all child rows** (per §5.3 race-correctness binding), and immediately before the state UPDATE.

**Why:** Clean gate boundary. M4 ships a complete `McfCertWriterService` contract that doesn't bottleneck on M7/M8 algorithm spec. M4 also ships `MockMcfHashComputer` (§7.3) for synthetic-row tests, so M4's behavior is fully testable in isolation. When M7/M8 land, dependency injection swaps the mock for the real implementation; the service contract is unchanged.

In-tx hash computation is a deliberate latency tradeoff: correctness at the authority boundary (cert + hash + state UPDATE all bind to the exact child rows that become `'approved'`) beats lower tx-lifetime. See §5.3 for the race that motivates this rule.

### 3.5 D-5 — `MockMcfHashComputer` in M4 PR (with production guard)

**Decision:** YES. The M4 implementation PR ships `MockMcfHashComputer` in `bc-core/src/registry/mcf/mcf-hash-computer.mock.ts` with deterministic placeholder hashes derivable from the input `metricContractUid` (e.g. `sha256("mock-formula:" + uid)`) and `hashAlgorithmVersion = 'mock-1.0.0'`.

**Production guard (mandatory).** The M4 service MUST throw a `ConfigurationError` when invoked in production (`process.env.NODE_ENV === 'production'`) with a hash computer whose output has `hashAlgorithmVersion.startsWith('mock-')`. The guard fires inside `approveForActivation` immediately after `hashComputer.computeAllForApproval(...)` returns and before the parent UPDATE. See §7.5 for the exact check.

**Why:** Required to test `approveForActivation` end-to-end against synthetic mcv rows before M7/M8 ship. The mock is clearly named (`Mock*`) so production code paths never accidentally consume it — but a wiring mistake (DI container misconfiguration, env-var misread) could still inject the mock in production. The runtime guard is the safety net.

### 3.6 D-6 — Per-transition operator-confirm matrix

**Decision:** Confirmed per MCF §11.4:

| Transition | Operator-confirm? | Rationale floor |
|---|---|---|
| `intake → draft` (creation) | NO (panel APPROVE is authoring authority) | n/a |
| `draft → review` | NO (AI-default) | n/a |
| `review → approved` | NO (AI-default; PE-MC-1..PE-MC-9 panel pass) | n/a |
| `approved → active` | **YES (always-confirm)** | ≥ 40 chars |
| `active → superseded` | **YES (always-confirm)** | ≥ 40 chars |

**Why:** Matches MCF §11.4 always-confirm stance at authority-bearing publication and supersession moments. AI default elsewhere. The two always-confirm transitions are also where the substrate (M3) requires cert evidence, so confirmation, cert authoring, and substrate enforcement align.

### 3.7 D-7 — Operator-confirm rule seeding location

**Decision:** DDL APPLY GATE. The M4 implementation PR ships INSERT statements for `contract.operator_confirm_rule` and `contract.framework_policy` in `bc-core/docker/redesign/06-mcf-cert-authority.sql` (or similar). The apply gate executes them.

**Why:** Consistent with M2 + M3 substrate gates — DDL + seed rows together in one apply. Avoids runtime "first-call" provisioning code paths that could fail silently.

### 3.8 D-8 — Seed `framework_policy` row for `scope='mcf'`

**Decision:** YES. M4 seeds one row in `contract.framework_policy`:

```sql
INSERT INTO contract.framework_policy (
  policy_uid, policy_version, scope_code, eligible_operations_json,
  consensus_requirement_json, sampling_rate,
  operator_confirm_rules_uid_list,
  notification_policy_json, calibration_regression_thresholds_json, adr_ref
) VALUES (
  'mcf_v1', '1.0.0', 'mcf',
  '["metric_create","metric_transition","metric_supersede"]'::jsonb,
  '{"models_required":3,"agreement_threshold":2,"models":["maker","checker","moderator"]}'::jsonb,
  0.10,
  ARRAY[
    'mcf_metric_transition_approved_to_active',
    'mcf_metric_supersede_active_to_superseded'
  ],
  '{}'::jsonb, '{}'::jsonb, 'DEC-c3e57f'
);
```

**Why:** Every cert row carries `policy_version` (referenced by the active `mcf` framework_policy row). Without the seed, the cert's `policy_version` is unverifiable. The 3-model panel consensus pattern + 10% sampling rate are conservative defaults; future amendment can tighten.

### 3.9 D-9 — Operator-confirm at `intake → draft`

**Decision:** NO. Creation does not require operator confirm.

**Why:** Panel APPROVE is the authoring authority for new metric contracts. Adding operator confirm at creation would create friction at the wrong layer (the operator's role is at publication, not authoring). The `metric_create` cert still exists for audit, but it carries `certifier_role_at_action='panel'` not `'operator'`.

### 3.10 D-10 — Audit row at `draft → review`

**Decision:** NO cert and NO audit row at `draft → review`. The transition is a simple state UPDATE through the M3 state-transition trigger.

**Why:** Review entry is a low-risk procedural step. Adding an audit row would inflate cert volume without corresponding governance value. If `review`-state observation is needed later, the existing `created_at` / state-column-change-by trigger output suffices (or a future amendment can add review-entry audit).

### 3.11 D-11 — Service location

**Decision:** `bc-core/src/registry/mcf/`. Follows the BCF pattern (`bc-core/src/registry/bcf/`).

### 3.12 D-12 — Service language

**Decision:** TypeScript using Drizzle ORM transactions (`db.transaction(async (tx) => {...})`).

**Why:** bc-core is TypeScript + Drizzle. No reason to introduce another stack for a backend service.

### 3.13 D-13 — Service shape (one class vs per-action split)

**Decision:** ONE CLASS — `McfCertWriterService`. Five public methods (`createMetricDraft`, `submitForReview`, `approveForActivation`, `activateMetric`, `supersedeMetric`).

**Why:** All methods share the same dependencies (`db`, `hashComputer`, JWT context resolver). Splitting into per-action services would replicate dependency-injection scaffolding without compositional benefit. If the surface grows beyond 5 methods (e.g. when supersession-of-supersession lands), split then.

### 3.14 D-14 — Test substrate (synthetic mcv rows)

**Decision:** YES. M4 PR ships test fixtures that INSERT synthetic mcv rows in a transaction and ROLLBACK at the end. Same pattern as `mcf-m3-post-apply-verification.mjs`.

**Why:** Tests must exercise the full M3 trigger composition (state graph, hash NOT-NULL, cert lookup, supersession check) against real DB behavior. Unit-test mocks of the trigger logic would diverge from substrate-actual semantics.

### 3.15 D-15 — `mcf.metric_publication_eligibility_result` shape

**Decision:** PER-PE-MC-ROW. One row per check (PE-MC-1, PE-MC-2, ..., PE-MC-10) per evaluation. Up to 10 rows per publication event.

**Why:** Finer query granularity. "Show me all PE-MC-4 (type/unit coherence) REJECT verdicts in the last 30 days" is a one-line query against per-row shape; the same against a single-JSONB-blob row requires JSON extraction. The table is append-only per Invariant V (immutable); no UPDATE path.

Column list in §4.2.

### 3.16 D-16 — FK from PE result to self-verification result

**Decision:** DEFER. The `satisfying_verification_result_uid` column exists (nullable text/uuid). No FK to `mcf.metric_self_verification_result` at M4 (that table ships in M9). A future DBCP amendment adds the FK when M9 lands.

**Why:** M4 ships before M9. Creating the FK now to a non-existent table would block apply. Nullable + FK-less is structurally correct; service-level validation will check the reference once M9 ships.

### 3.17 D-17 — Index on `contract.certification_record` for MCF lookups [RETIRED per P-23]

**Decision (post-cert-amendment rewrite):** **RETIRED.** The original D-17 specified a conditional partial index on `contract.certification_record (governance_scope, action_code, primitive_id) WHERE governance_scope='mcf'` for the M3 trigger's cert lookup hot path. Per Option C (cert substrate correction preflight `637e667`) the M3 trigger no longer reads from `contract.certification_record` — it reads from `mcf.certification_record` (the sibling table created by the M3 cert-amendment). The amendment already shipped `idx_mcf_cert_lookup (primitive_id, action_code, created_at DESC)` on the sibling for the trigger hot path (per M3 cert-amendment DBCP §4.5). No additional index on the shared `contract.certification_record` is needed by M4.

**M4 takes no action on D-17.** The amendment-shipped sibling index covers the trigger lookup. The M4 dry-run script no longer inspects `contract.certification_record` indexes.

### 3.18 D-18 — Rule UID prefix + scope tagging

**Decision:** YES — every MCF `operator_confirm_rule` row uses `rule_uid` prefix `mcf_*` and `scope = 'mcf'`. Mirrors the BCF prefix-and-scope convention.

**Why:** Avoid collision with BCF rules in the shared table. Allows the trigger / service to filter by scope cleanly.

### 3.19 D-19 — Cert sibling vs reuse [REVERSED per P-22 / post-cert-amendment rewrite]

**Decision (REVERSED from the original "REUSE" position):** **PER-FRAMEWORK SIBLING.** MCF rows write into the new `mcf.certification_record` table (created by the M3 cert-amendment per `bc-docs-v3 06d369c` and applied per `60efd9d`). No `governance_scope='mcf'` discriminator on a shared table; the sibling itself is the framework boundary. This realizes Option C (hybrid) from the cert substrate correction preflight (`bc-docs-v3 637e667`) — cert content is per-framework, while `framework_policy` and `operator_confirm_rule` remain shared infrastructure with additive CHECK extensions.

**Why the reversal:** The original D-19 "REUSE" was rejected at M4 implementation pre-read by 10 live Foundation Governance Substrate CHECK constraints on `contract.certification_record` — `governance_scope_chk` admits only `NULL` or `'registry'`; `action_code_chk` excludes MCF action codes; `primitive_type_chk` excludes `'metric_contract_version'`; `subject_kind_chk` excludes MCF kinds; `row_shape_chk` admits exactly two shapes (legacy XOR Registry) neither of which fits MCF; `scope_action_chk` couples them. The shared schema does NOT accommodate MCF; the original "no column gaps would have surfaced" rationale was based on column presence only, not CHECK admissibility. The correction preflight evaluated 3 options; Option C accepted by operator (D-Correction-1 through D-Correction-7); M3 cert-amendment applied; M4 now follows.

**Operational implication:** every M4 cert-write target is `mcf.certification_record` (sibling), not `contract.certification_record` (shared). The `mcf.certification_record` table has 25 columns (drops `governance_scope` + `target_registry_id`); CHECK constraints are tight to MCF semantics (per M3 cert-amendment §4.3). The M3 state-transition trigger reads the sibling (verified at amendment apply per closeout `60efd9d` check #6: exactly 1 `FROM mcf.certification_record` + 0 `FROM contract.certification_record`). The `mcf.metric_supersession.fk_mcs_cert` FK targets the sibling. The operator can confirm with one `SELECT 1 FROM mcf.certification_record LIMIT 0` (table exists post-amendment).

### 3.20 D-20 — Override discipline support

**Decision:** YES. Every M4 cert write accepts an optional `override` payload (`{ gateCode, rationaleText, followupTaskUid }`) that populates `override_gate_code` / `override_rationale_text` / `override_followup_task_uid` on the cert row.

**Why:** Operator override path is needed for emergency activations / supersessions when one or more PE-MC checks reported OPERATOR_REVIEW or REJECT but the operator has rationale to proceed. The cert columns already exist in `mcf.certification_record` (sibling mirrors the BCF cert's override-triplet pattern per M3 cert-amendment §4.2). Pass-through with no DBCP-level validation beyond non-empty when present.

---

## 4. Certification authority model

### 4.1 Conceptual model

M4 is the service layer that produces rows satisfying the M3 substrate gates. The three cert writers + four transitions compose as follows:

```
intake (pre-substrate)
  │
  │ createMetricDraft()
  │   → INSERT metric_contract + metric_contract_version + bindings + filters + dim refs
  │   → INSERT metric_create cert (action_code='metric_create')
  │   → single tx, all-or-nothing
  ▼
draft
  │
  │ submitForReview()
  │   → UPDATE governance_state_code: draft → review
  │   → no cert; service-only
  ▼
review
  │
  │ approveForActivation()
  │   → CALL hashComputer.computeAllForApproval() (returns 6 hashes)
  │   → UPDATE parent metric_contract: set 6 hash columns
  │   → INSERT N rows in metric_publication_eligibility_result (PE-MC-1..PE-MC-9 results)
  │   → UPDATE governance_state_code: review → approved
  │   → no cert; substrate enforces hash NOT-NULL gate; PE results stored for audit
  │   → single tx
  ▼
approved
  │
  │ activateMetric()
  │   → INSERT N rows in metric_publication_eligibility_result (PE-MC-1..PE-MC-10 results)
  │   → INSERT metric_transition cert (action_code='metric_transition',
  │      from_state_code='approved', to_state_code='active')
  │   → UPDATE governance_state_code: approved → active
  │      (M3 trigger reads the cert; flips is_current=TRUE on this row;
  │       demotes prior is_current=TRUE row to FALSE)
  │   → single tx; OPERATOR CONFIRM ≥ 40 chars rationale required
  ▼
active
  │
  │ supersedeMetric()
  │   → INSERT metric_supersede cert (action_code='metric_supersede',
  │      from_state_code='active', to_state_code='superseded')
  │   → INSERT mcf.metric_supersession row (FK to cert via certification_record_id)
  │   → UPDATE predecessor governance_state_code: active → superseded
  │      (M3 trigger reads supersession row; flips is_current=FALSE)
  │   → single tx; OPERATOR CONFIRM ≥ 40 chars rationale required
  │   → successor MCV must already be 'active' + is_current=TRUE
  ▼
superseded (terminal)
```

### 4.2 New table: `mcf.metric_publication_eligibility_result`

#### 4.2.1 Purpose

Per MCF §13 + §17.1: records the verdict + evidence per PE-MC check per evaluation. Cited by certs via `gate_results_json` for audit traceability. Append-only per Invariant V.

#### 4.2.2 Column specification

| # | Column | Type | Constraints | Notes |
|---:|---|---|---|---|
| 1 | `pe_result_uid` | uuid | NOT NULL PRIMARY KEY DEFAULT `gen_random_uuid()` | Stable identifier |
| 2 | `metric_contract_version_uid` | uuid | NOT NULL | The MCV the check applies to |
| 3 | `certification_record_id` | uuid | NULL | The cert this PE result was emitted for (nullable: pre-approve checks may exist before any cert is written) |
| 4 | `pe_check_code` | text | NOT NULL CHECK | One of PE-MC-1 through PE-MC-10 (closed 10-element enum) |
| 5 | `verdict_code` | text | NOT NULL CHECK | One of `PASS` / `REJECT` / `OPERATOR_REVIEW` (closed 3-element enum per MCF §13 PE summary table) |
| 6 | `evidence_json` | jsonb | NOT NULL DEFAULT `'{}'::jsonb` | Check-specific evidence (e.g. PE-MC-1 grounding citations; PE-MC-10 fixture verification ref) |
| 7 | `panel_run_uid` | uuid | NULL | The panel run that produced this verdict (M5 table; nullable + FK-less until M5 ships) |
| 8 | `verifier_version` | text | NULL | Algorithm version of the check; nullable for PE-MC-1..PE-MC-9 (panel-evaluated); set for PE-MC-10 (verifier-evaluated) |
| 9 | `satisfying_verification_result_uid` | uuid | NULL | PE-MC-10 only: the `mcf.metric_self_verification_result` row that satisfied this check. FK deferred until M9 ships (D-16). |
| 10 | `evaluated_at` | timestamptz | NOT NULL DEFAULT `now()` | When the verdict was produced |
| 11 | (none) | | | Total: 10 columns |

#### 4.2.3 Constraints

| Name | Definition |
|---|---|
| `mper_pe_check_code_chk` CHECK | `pe_check_code IN ('PE-MC-1','PE-MC-2','PE-MC-3','PE-MC-4','PE-MC-5','PE-MC-6','PE-MC-7','PE-MC-8','PE-MC-9','PE-MC-10')` |
| `mper_verdict_code_chk` CHECK | `verdict_code IN ('PASS','REJECT','OPERATOR_REVIEW')` |
| `fk_mper_mcv` FOREIGN KEY | `(metric_contract_version_uid) REFERENCES mcf.metric_contract_version(metric_contract_version_uid) ON DELETE RESTRICT` |
| `fk_mper_cert` FOREIGN KEY | `(certification_record_id) REFERENCES mcf.certification_record(certification_record_id) ON DELETE RESTRICT` (nullable — only enforced when populated; sibling table per M3 cert-amendment / D-19 reversed) |

Note: no FK on `panel_run_uid` (M5 deferred) or `satisfying_verification_result_uid` (M9 deferred). Both columns are plain uuid; service-level validation when those tables exist.

#### 4.2.4 Indexes

| Name | Type | Definition |
|---|---|---|
| `idx_mcf_mper_mcv_at` | non-unique | `(metric_contract_version_uid, evaluated_at DESC)` — supports "most recent PE-MC results for this MCV" queries |
| `idx_mcf_mper_cert` | non-unique | `(certification_record_id)` — supports "what PE-MC results did this cert reference?" |
| `idx_mcf_mper_check_verdict_at` | non-unique | `(pe_check_code, verdict_code, evaluated_at DESC)` — supports operator dashboards ("show all PE-MC-4 REJECT in last 30 days") |

#### 4.2.5 No UNIQUE on (mcv, check)

Multiple evaluations of the same check on the same MCV are allowed (e.g. retry after fixing a citation issue). Ordering by `evaluated_at DESC` gives the latest. Invariant V (non-replayable evaluation) means each evaluation is its own row.

### 4.3 Existing tables M4 writes to

| Table | Writes |
|---|---|
| `mcf.certification_record` | INSERTs from `metric_create` / `metric_transition` / `metric_supersede` action codes (sibling table per M3 cert-amendment; D-19 reversed per P-22) |
| `contract.operator_confirm_rule` | INSERT (seed, apply-time) of 2 MCF rows |
| `contract.framework_policy` | INSERT (seed, apply-time) of 1 MCF row |
| `mcf.metric_contract` | INSERTs via `createMetricDraft`; UPDATEs hash columns via `approveForActivation` |
| `mcf.metric_contract_version` | INSERTs via `createMetricDraft`; UPDATEs `governance_state_code` via the four transition methods |
| `mcf.metric_variable_binding` | INSERTs via `createMetricDraft` |
| `mcf.metric_filter_clause` | INSERTs via `createMetricDraft` |
| `mcf.metric_computed_dimension_ref` | INSERTs via `createMetricDraft` |
| `mcf.metric_supersession` | INSERTs via `supersedeMetric` |

No DELETEs anywhere — append-only + soft-archive discipline.

---

## 5. Transaction discipline

### 5.1 Single-transaction pattern

Every M4 write method wraps its DB operations in one `db.transaction(async (tx) => {...})`. The trigger fires inside the transaction and sees same-tx INSERTs. On any error, the entire transaction rolls back — no half-state.

### 5.2 What's inside the tx vs outside

**Inside the transaction (must roll back together):**
- `SELECT ... FOR UPDATE` on the target MCV + parent MC + all child rows under the MCV (for `approveForActivation` — see §5.3)
- `McfHashComputer.computeAllForApproval()` call (for `approveForActivation` — see §5.3 for the race-correctness rationale)
- All UPDATEs to `mcf.metric_contract` hash columns (`approveForActivation` only)
- All INSERTs into `mcf.certification_record` for this action (sibling table; D-19 reversed per P-22)
- All INSERTs into `mcf.metric_publication_eligibility_result` for this action
- All INSERTs into `mcf.metric_supersession` (`supersedeMetric` only)
- All other INSERTs into `mcf.*` tables (parent / version / child rows on `createMetricDraft`)
- The `governance_state_code` UPDATE on `mcf.metric_contract_version`
- For supersession: `SELECT FOR UPDATE` on predecessor and successor MCV rows (concurrency control)

**Outside the transaction (must complete before the tx opens):**
- Cert payload assembly (PE-MC result composition, JWT context resolution, panel context lookup)
- Input validation (schema validation, ≥40-char rationale check, `primitive_type`/`action_code` consistency check, `policyVersion` active-row check per §6.8)
- Idempotency-key lookup (check if a prior call with the same key already committed)

### 5.3 Why hash computation is inside the tx (race-correctness binding)

Hash computation for `approveForActivation` happens **inside** the transaction, **after** acquiring `SELECT FOR UPDATE` locks on:
1. The target MCV row (`mcf.metric_contract_version`)
2. The parent MC row (`mcf.metric_contract`)
3. All child rows under this MCV (`mcf.metric_variable_binding`, `mcf.metric_filter_clause`, `mcf.metric_computed_dimension_ref`), ordered by primary-key uuid

This is a deliberate latency tradeoff: **correctness at the authority boundary** (cert + hash + state UPDATE all bind to the exact child rows that become `'approved'`) **beats lower tx-lifetime**.

#### 5.3.1 The race that motivates the rule

If hashes were computed outside the tx from M2 child tables and passed in as a plain object:

1. T0: caller reads child rows for MCV X (state = `'review'`, child rows mutable per M3 substrate)
2. T1: caller computes hashes from the read snapshot
3. T2: an external writer INSERTs / UPDATEs / DELETEs a child row of MCV X (still permitted at `'review'`)
4. T3: caller opens tx, UPDATEs parent hashes (now stale relative to actual child rows), UPDATEs state to `'approved'`
5. Result: parent at `'approved'` carries hashes that disagree with the child-row contents. The cert that later authorizes `approved → active` binds to a `package_signature_hash` that does not match reality.

The M3 child-immutability triggers reject child UPDATEs only when the parent state is `'approved'`/`'active'`/`'superseded'` — not at `'review'`. So the race window is open during step 2-3.

#### 5.3.2 M4-only world vs M11+ world

In M4-only world, no service method modifies child rows after `createMetricDraft`, so the race is not exploitable today. **The DBCP locks the correct semantics now so that M11 panel iterations (which will modify bindings during `'review'`) inherit a sound boundary.** Tightening this later would require auditing all already-`'approved'` MCs for hash consistency — a larger problem.

#### 5.3.3 Lock acquisition order (deadlock avoidance)

All locks in the same tx, in this order — concurrent transactions on the same MC follow the same order, so no two transactions can deadlock:

1. MCV row (single row; locked via `for('update')`)
2. Parent MC row (single row)
3. Child rows under MCV (ordered by PK uuid ascending — deterministic across callers)

Concurrent transactions on different MCs touch disjoint locks.

#### 5.3.4 Pattern

```typescript
await db.transaction(async (tx) => {
  // 1. Lock target MCV and verify state
  const [mcv] = await tx.select(...).from(mcfMetricContractVersion)
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, input.metricContractVersionUid))
    .for('update');
  if (mcv.governanceStateCode !== 'review') throw new InvalidStateError(...);

  // 2. Lock parent MC and all child rows under this MCV (PK-ordered)
  await tx.select(...).from(mcfMetricContract).where(eq(..., mcv.metricContractUid)).for('update');
  await tx.select(...).from(mcfMetricVariableBinding).where(eq(..., mcv.metricContractVersionUid)).orderBy(...).for('update');
  await tx.select(...).from(mcfMetricFilterClause).where(eq(..., mcv.metricContractVersionUid)).orderBy(...).for('update');
  await tx.select(...).from(mcfMetricComputedDimensionRef).where(eq(..., mcv.metricContractVersionUid)).orderBy(...).for('update');

  // 3. Compute hashes from the LOCKED rows (M7/M8 implementation reads under the lock)
  const hashes = await this.hashComputer.computeAllForApproval({ metricContractUid: mcv.metricContractUid });

  // 4. Production guard against mock hash computer (see §7.5)
  this.assertProductionHashAlgorithm(hashes.hashAlgorithmVersion);

  // 5. UPDATE parent MC with the 6 hashes
  await tx.update(mcfMetricContract).set(hashes).where(...);

  // 6. INSERT PE-MC-1..PE-MC-9 result rows
  // 7. UPDATE state — M3 trigger fires; sees hashes NOT NULL; passes
});
```

See §8.3 for the full method body.

### 5.4 Save-point discipline

Some methods open nested logical units (e.g. `supersedeMetric` first INSERTs the cert, then INSERTs the supersession row, then UPDATEs predecessor state). Each step is part of the same tx; no save-points are used. If any step fails, the whole tx rolls back.

### 5.5 Transaction lifetime budget

Target depends on method (because `approveForActivation` performs in-tx hash computation per §5.3):

| Method | Target | p99 | Slow-flag threshold |
|---|---|---|---|
| `createMetricDraft` | <100 ms | <500 ms | >1 s |
| `submitForReview` | <50 ms | <200 ms | >500 ms |
| `approveForActivation` | <500 ms | <2 s | >5 s |
| `activateMetric` | <100 ms | <500 ms | >1 s |
| `supersedeMetric` | <150 ms | <600 ms | >1.5 s |

`approveForActivation`'s higher budget reflects in-tx hash computation. With `MockMcfHashComputer` the call is <1 ms; with real M7/M8 hashers the cost scales with binding/filter/dim-ref count. The M4 implementation PR ships a tx-duration logger that flags slow txns at the per-method threshold above.

A tx that exceeds the slow-flag threshold signals either (a) inadequate indexes, (b) lock contention, (c) inadvertent in-tx work (e.g. network calls), or (d) for `approveForActivation`, hash computation cost growing beyond projections (M7/M8 own).

---

## 6. `McfCertWriterService` contract

### 6.1 Service skeleton

```typescript
// bc-core/src/registry/mcf/mcf-cert-writer.service.ts
import type { PlatformDb } from '../../database/platform-db';
import type { McfHashComputer } from './mcf-hash-computer.interface';

export class McfCertWriterService {
  constructor(
    private readonly db: PlatformDb,
    private readonly hashComputer: McfHashComputer,
  ) {}

  async createMetricDraft(input: CreateMetricDraftInput): Promise<CreateMetricDraftResult>;
  async submitForReview(input: SubmitForReviewInput): Promise<SubmitForReviewResult>;
  async approveForActivation(input: ApproveForActivationInput): Promise<ApproveForActivationResult>;
  async activateMetric(input: ActivateMetricInput): Promise<ActivateMetricResult>;
  async supersedeMetric(input: SupersedeMetricInput): Promise<SupersedeMetricResult>;
}
```

### 6.2 Input / output types — `createMetricDraft`

```typescript
export interface CreateMetricDraftInput {
  metricContract: {
    grainEntityId: string;
    displayName: string;
    description?: string | null;
    candidateSourceRefJson?: object | null;
    temporalGateShapeCode?: string | null;
    temporalGateParamsJson?: object | null;
    // hashes left null at draft creation; populated by approveForActivation
  };
  metricContractVersion: {
    versionCode: string;
    versionSeq: number;
    descriptionText?: string | null;
    functionCode?: string | null;
    subfunctionCode?: string | null;
    ownerJson?: object | null;
    tags?: string[] | null;
    thresholdJson?: object | null;
    supersedesVersionUid?: string | null;
  };
  variableBindings?: VariableBindingInput[];
  filterClauses?: FilterClauseInput[];
  computedDimensionRefs?: ComputedDimensionRefInput[];
  cert: CertContextInput & {
    actionCode: 'metric_create';
    fromStateCode: null;
    toStateCode: 'draft';
    // For metric_create, certifier_role_at_action is usually 'panel' or 'system';
    // operator confirm is NOT required at intake per D-9.
  };
  dryRun?: boolean;
  idempotencyKey?: string;
}

export interface CreateMetricDraftResult {
  metricContractUid: string;
  metricContractVersionUid: string;
  certificationRecordId: string;
  committed: boolean;  // false if dryRun=true
}
```

### 6.3 Input / output types — `submitForReview`

```typescript
export interface SubmitForReviewInput {
  metricContractVersionUid: string;
  actorSub: string;  // who issued the transition
  actorRoleAtAction: 'panel' | 'operator' | 'system';
  dryRun?: boolean;
}

export interface SubmitForReviewResult {
  metricContractVersionUid: string;
  newStateCode: 'review';
  committed: boolean;
}
```

No cert is written. Service validates that the MCV's current state is `'draft'` before issuing the UPDATE; M3 trigger enforces.

### 6.4 Input / output types — `approveForActivation`

```typescript
export interface ApproveForActivationInput {
  metricContractVersionUid: string;
  actorSub: string;
  actorRoleAtAction: 'panel' | 'operator' | 'system';
  peEligibilityResults: PeEligibilityResultInput[];  // PE-MC-1 through PE-MC-9 (PE-MC-10 is later, at activateMetric)
  dryRun?: boolean;
}

export interface ApproveForActivationResult {
  metricContractVersionUid: string;
  newStateCode: 'approved';
  hashesApplied: ParentHashes;  // the 6 hashes written to parent MC
  peResultUids: string[];  // one uid per PE-MC result row inserted
  committed: boolean;
}

export interface PeEligibilityResultInput {
  peCheckCode: 'PE-MC-1' | 'PE-MC-2' | 'PE-MC-3' | 'PE-MC-4' | 'PE-MC-5' | 'PE-MC-6' | 'PE-MC-7' | 'PE-MC-8' | 'PE-MC-9' | 'PE-MC-10';
  verdictCode: 'PASS' | 'REJECT' | 'OPERATOR_REVIEW';
  evidenceJson: object;
  panelRunUid?: string | null;
  verifierVersion?: string | null;
  satisfyingVerificationResultUid?: string | null;
}

export interface ParentHashes {
  formulaIntentHash: string;
  variableBindingSetHash: string;
  filterSetHash: string;
  identityTupleHash: string;
  packageSignatureHash: string;
  hashAlgorithmVersion: string;
}
```

No cert at this transition (matches M3 substrate — only `metric_create`, `metric_transition`, `metric_supersede` carry certs).

### 6.5 Input / output types — `activateMetric`

```typescript
export interface ActivateMetricInput {
  metricContractVersionUid: string;
  cert: CertContextInput & {
    actionCode: 'metric_transition';
    fromStateCode: 'approved';
    toStateCode: 'active';
    certifierRoleAtAction: 'operator';  // always-confirm per D-6
    rationaleText: string;  // ≥40 chars validated at service layer
  };
  peEligibilityResults: PeEligibilityResultInput[];  // includes PE-MC-10
  dryRun?: boolean;
  idempotencyKey?: string;
}

export interface ActivateMetricResult {
  metricContractVersionUid: string;
  newStateCode: 'active';
  certificationRecordId: string;
  peResultUids: string[];
  isCurrentDemoted: string | null;  // previous active MCV's uid, if any was demoted
  committed: boolean;
}
```

The service validates `rationaleText.length >= 40` and `certifierRoleAtAction === 'operator'` before the tx opens.

### 6.6 Input / output types — `supersedeMetric`

```typescript
export interface SupersedeMetricInput {
  predecessorMetricContractVersionUid: string;
  successorMetricContractUid: string;
  successorMetricContractVersionUid: string;
  correctionClassCode: 'editorial' | 'meaning_bearing';
  cert: CertContextInput & {
    actionCode: 'metric_supersede';
    fromStateCode: 'active';
    toStateCode: 'superseded';
    certifierRoleAtAction: 'operator';
    rationaleText: string;  // ≥40 chars
  };
  dryRun?: boolean;
  idempotencyKey?: string;
}

export interface SupersedeMetricResult {
  predecessorMetricContractVersionUid: string;
  newStateCode: 'superseded';
  certificationRecordId: string;
  supersessionUid: string;
  committed: boolean;
}
```

Service validates:
- `rationaleText.length >= 40`
- `correctionClassCode in ('editorial', 'meaning_bearing')`
- Predecessor MCV is in state `'active'` AND `is_current=TRUE` (DB lookup)
- Successor MCV is in state `'active'` AND `is_current=TRUE` (DB lookup with `SELECT FOR UPDATE` inside the tx)
- Predecessor MC != successor MC (different parents)
- `mcs_rationale_min_length_chk` substrate CHECK will also enforce ≥40

### 6.7 Shared input — `CertContextInput`

```typescript
export interface CertContextInput {
  certifierSub: string;
  certifierRoleAtAction: 'panel' | 'operator' | 'system';
  certifierEmail?: string | null;
  panelRunUid?: string | null;
  promptVersion?: string | null;
  modelIdentityJson?: object | null;
  inputHash?: string | null;
  policyVersion: string;  // e.g. '1.0.0' — must match an ACTIVE framework_policy row with scope='mcf' (effective_to IS NULL OR effective_to > now())
  samplingStatus?: string | null;
  groundingCheckResult?: string | null;
  gateResultsJson: object;
  advisoryVerdictsJson?: object[];
  override?: {
    gateCode: string;
    rationaleText: string;
    followupTaskUid: string;
  } | null;
  rationaleText?: string;  // only required for action_codes with operator-confirm (transition, supersede)
}
```

### 6.8 Validation surface

The service validates BEFORE opening the tx:

| Validation | Applies to |
|---|---|
| `governanceScope === 'mcf'` (implied; always 'mcf' for this service) | All |
| `actionCode IN ('metric_create','metric_transition','metric_supersede')` | All cert writes |
| `primitiveType === 'metric_contract_version'` | All cert writes |
| For `metric_transition`: `fromStateCode === 'approved'` && `toStateCode === 'active'` | `activateMetric` |
| For `metric_supersede`: `fromStateCode === 'active'` && `toStateCode === 'superseded'`. The service derives `supersedes_primitive_id` on the cert row from `input.predecessorMetricContractVersionUid` (not a caller-exposed field on `CertContextInput`; see §8.5.2 step 2). | `supersedeMetric` |
| `certifierSub` non-empty | All |
| For operator-confirm actions: `certifierRoleAtAction === 'operator'` | activate, supersede |
| For operator-confirm actions: `rationaleText.length >= 40` | activate, supersede |
| `policyVersion` references an ACTIVE `framework_policy` row with `scope_code='mcf'` AND (`effective_to IS NULL` OR `effective_to > now()`) — archived policy versions cannot be referenced | All cert writes |
| `peEligibilityResults` array: each row has valid `peCheckCode` + `verdictCode` enums | approve, activate |
| For `supersedeMetric`: predecessor MC != successor MC | supersedeMetric |

Validation failures throw before the tx opens — no half-written state.

---

## 7. `McfHashComputer` interface boundary

### 7.1 Interface declaration

```typescript
// bc-core/src/registry/mcf/mcf-hash-computer.interface.ts
import type { ParentHashes } from './mcf-cert-writer.service';

export interface McfHashComputer {
  /**
   * Compute all six parent-MC hashes required by the M3 state-transition trigger
   * at review → approved. Reads variable bindings, filter clauses, computed-dim
   * refs from M2 tables under the supplied metricContractUid.
   *
   * Must be deterministic: same input → same output (modulo hashAlgorithmVersion).
   *
   * SHOULD be idempotent: calling twice with the same input should not change
   * anything externally (this contract reads only).
   */
  computeAllForApproval(input: {
    metricContractUid: string;
  }): Promise<ParentHashes>;
}
```

### 7.2 Boundary semantics

**M4 declares the interface.** M4 does NOT implement `computeAllForApproval` for production use. M4 ships only `MockMcfHashComputer` (§7.3) for testing.

**M7/M8 implement the interface.** M7 (formula AST) and M8 (package signature) ship implementations in their respective gates. The exact file layout is M7/M8 DBCP territory and may differ from any illustrative split sketched here. As an *illustrative example only* (not binding on the M7/M8 DBCPs), a plausible decomposition might place the six hashes across files like:

- A formula intent hasher (M7-owned)
- A variable binding set hasher (M7-owned)
- A filter set hasher (M7-owned)
- An identity tuple hasher (M7-owned; composes the prior three)
- A package signature hasher (M8-owned)
- A composing service that implements `McfHashComputer` (could be M7 or M8 or shared)

M7 and M8 DBCPs will fix the actual filenames + class names + ownership boundary. M4 only contracts to the interface, not to any file structure.

**Dependency injection.** The M4 service is constructed with whichever `McfHashComputer` implementation is appropriate for the context. Production wiring uses the real implementation when M7/M8 are live. Tests use the mock. The M4 service itself doesn't care.

### 7.3 `MockMcfHashComputer` shipped with M4

```typescript
// bc-core/src/registry/mcf/mcf-hash-computer.mock.ts
import { createHash } from 'crypto';
import type { McfHashComputer } from './mcf-hash-computer.interface';
import type { ParentHashes } from './mcf-cert-writer.service';

export class MockMcfHashComputer implements McfHashComputer {
  async computeAllForApproval(input: { metricContractUid: string }): Promise<ParentHashes> {
    const seed = input.metricContractUid;
    return {
      formulaIntentHash:       this.hash('mock-formula:' + seed),
      variableBindingSetHash:  this.hash('mock-bindings:' + seed),
      filterSetHash:           this.hash('mock-filters:' + seed),
      identityTupleHash:       this.hash('mock-identity:' + seed),
      packageSignatureHash:    this.hash('mock-signature:' + seed),
      hashAlgorithmVersion:    'mock-1.0.0',
    };
  }

  private hash(s: string): string {
    return createHash('sha256').update(s).digest('hex');
  }
}
```

The mock is deterministic per `metricContractUid`. Tests can assert that the hashes are consistent across calls.

### 7.4 Production-readiness contract

When M7/M8 land:
- The real implementation MUST produce the same hash for the same identity tuple, regardless of insertion order or run-time environment.
- The `hashAlgorithmVersion` value distinguishes algorithm generations (e.g. `'sha256-canonical-1.0'`).
- Algorithm changes require a new `hashAlgorithmVersion` value AND a migration plan for in-flight metrics (likely supersession with `correction_class='editorial'`). M4 ships no "rehash without supersede" escape path — that's an M7/M8 DBCP concern per Q-5.

These are M7/M8 DBCP concerns, not M4. M4 only declares the boundary.

### 7.5 Production guard against mock hash algorithm (mandatory)

The M4 service MUST refuse to commit `approveForActivation` when:
- `process.env.NODE_ENV === 'production'` (or whichever production-environment signal the deployment uses), AND
- The hash computer returned a `hashAlgorithmVersion` whose value starts with the literal string `mock-` (case-sensitive)

The check is implemented inside `approveForActivation`, immediately after the `McfHashComputer.computeAllForApproval(...)` call returns and before the parent MC hash UPDATE. Exact shape:

```typescript
private assertProductionHashAlgorithm(hashAlgorithmVersion: string): void {
  if (process.env.NODE_ENV === 'production' && hashAlgorithmVersion.startsWith('mock-')) {
    throw new ConfigurationError(
      `MCF M4: refusing to commit hashes with mock algorithm '${hashAlgorithmVersion}' ` +
      `in production. MockMcfHashComputer is for testing only. ` +
      `Check dependency-injection wiring — the production McfHashComputer should be ` +
      `the M7/M8 implementation (algorithm version prefix 'sha256-...' or similar non-mock).`
    );
  }
}
```

The guard is part of the M4 service contract — implementation MUST include it. The verifier (§14) tests it: a production-env synthetic run with `MockMcfHashComputer` MUST throw `ConfigurationError` before any DB write.

**Why this guard exists.** `MockMcfHashComputer` ships with the M4 implementation PR per D-5 because it's needed for synthetic-row tests. Nothing structural prevents a wiring mistake (DI container misconfigured, env-var misread, test fixture leaked into prod) from injecting the mock at runtime. The mock's deterministic-per-MC hashes look real (well-formed sha256 hex), so the M3 substrate trigger's NOT-NULL check would pass — but `package_signature_hash` would be content-blind. The runtime guard is the safety net.

**Non-production environments.** In development, CI, and test environments, the mock is permitted. The guard only fires for `production`.

**Future amendments.** When M7/M8 ship and the production wiring uses real implementations, the guard remains as defense-in-depth. Removing the guard later would lose the protection against future regressions.

---

## 8. Transition-specific design

### 8.1 `createMetricDraft` (intake → draft)

#### 8.1.1 Inputs

`CreateMetricDraftInput` per §6.2.

#### 8.1.2 Transaction body

```typescript
await db.transaction(async (tx) => {
  // 1. Insert parent MC (hashes null)
  const [mc] = await tx.insert(mcfMetricContract)
    .values({ ...input.metricContract })
    .returning();

  // 2. Insert MCV (state='draft' via column DEFAULT; trigger enforces INSERT-must-be-draft)
  const [mcv] = await tx.insert(mcfMetricContractVersion)
    .values({
      metricContractUid: mc.metricContractUid,
      governanceStateCode: 'draft',  // explicit for clarity; DEFAULT would also work
      ...input.metricContractVersion,
    })
    .returning();

  // 3. Insert child rows (bindings, filters, dim refs)
  if (input.variableBindings?.length) {
    await tx.insert(mcfMetricVariableBinding).values(
      input.variableBindings.map(b => ({ metricContractVersionUid: mcv.metricContractVersionUid, ...b }))
    );
  }
  // ... similar for filterClauses, computedDimensionRefs

  // 4. Insert metric_create cert
  const [cert] = await tx.insert(mcfCertificationRecord)
    .values({
      primitiveType: 'metric_contract_version',
      primitiveId: mcv.metricContractVersionUid,
      actionCode: 'metric_create',
      fromStateCode: null,
      toStateCode: 'draft',
      isArchivedAfter: null,
      // governance_scope column removed — sibling table is implicitly MCF-scoped (D-19 reversed per P-22)
      subjectKind: 'metric_contract_version',
      ...input.cert,
    })
    .returning();

  return {
    metricContractUid: mc.metricContractUid,
    metricContractVersionUid: mcv.metricContractVersionUid,
    certificationRecordId: cert.certificationRecordId,
    committed: !input.dryRun,
  };
});
```

If `dryRun=true`, the method wraps the above in an explicit ROLLBACK at the end of the tx.

#### 8.1.3 Substrate enforcement on this path

- M3 INSERT trigger (`fn_mcv_state_transition_check`) checks that `governance_state_code='draft'`. Passes.
- No cert lookup; the `metric_create` cert is service-contract-only (M3 DBCP §8.3).

### 8.2 `submitForReview` (draft → review)

#### 8.2.1 Transaction body

```typescript
await db.transaction(async (tx) => {
  // Validate current state via SELECT (M3 trigger also enforces)
  const [mcv] = await tx.select({ governanceStateCode: mcfMetricContractVersion.governanceStateCode })
    .from(mcfMetricContractVersion)
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, input.metricContractVersionUid))
    .for('update');  // serialize against concurrent state changes

  if (mcv.governanceStateCode !== 'draft') {
    throw new InvalidStateError(`Expected draft, got ${mcv.governanceStateCode}`);
  }

  await tx.update(mcfMetricContractVersion)
    .set({ governanceStateCode: 'review' })
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, input.metricContractVersionUid));
});
```

#### 8.2.2 Substrate enforcement

- M3 `fn_mcv_state_transition_check` validates `draft → review` is a legal transition. Passes.
- No cert.
- No revision-emit trigger fires (revision-emit only fires when prior state was `'active'`).

### 8.3 `approveForActivation` (review → approved)

Per §5.3, hashes are computed INSIDE the transaction after acquiring locks. There is no pre-transaction hash compute step. The pattern below realizes the race-correctness binding rule.

#### 8.3.1 Transaction body

```typescript
await db.transaction(async (tx) => {
  // 1. Lock target MCV and verify state
  const [mcv] = await tx.select(...).from(mcfMetricContractVersion)
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, input.metricContractVersionUid))
    .for('update');
  if (mcv.governanceStateCode !== 'review') throw new InvalidStateError(...);

  // 2. Lock parent MC + all child rows under this MCV (PK-ordered for deadlock avoidance)
  await tx.select(...).from(mcfMetricContract)
    .where(eq(mcfMetricContract.metricContractUid, mcv.metricContractUid))
    .for('update');

  await tx.select(...).from(mcfMetricVariableBinding)
    .where(eq(mcfMetricVariableBinding.metricContractVersionUid, mcv.metricContractVersionUid))
    .orderBy(mcfMetricVariableBinding.metricVariableBindingUid)
    .for('update');

  await tx.select(...).from(mcfMetricFilterClause)
    .where(eq(mcfMetricFilterClause.metricContractVersionUid, mcv.metricContractVersionUid))
    .orderBy(mcfMetricFilterClause.metricFilterClauseUid)
    .for('update');

  await tx.select(...).from(mcfMetricComputedDimensionRef)
    .where(eq(mcfMetricComputedDimensionRef.metricContractVersionUid, mcv.metricContractVersionUid))
    .orderBy(mcfMetricComputedDimensionRef.metricComputedDimensionRefUid)
    .for('update');

  // 3. Compute hashes from the LOCKED rows (no race possible — concurrent child mutations are
  //    blocked by the locks acquired in step 2)
  const hashes = await this.hashComputer.computeAllForApproval({
    metricContractUid: mcv.metricContractUid,
  });

  // 4. Production guard against mock hash computer (see §7.5)
  this.assertProductionHashAlgorithm(hashes.hashAlgorithmVersion);

  // 5. UPDATE parent MC with the 6 hashes
  await tx.update(mcfMetricContract).set(hashes)
    .where(eq(mcfMetricContract.metricContractUid, mcv.metricContractUid));

  // 6. INSERT PE-MC-1..PE-MC-9 result rows (no cert at this transition; certificationRecordId NULL)
  const peResults = await tx.insert(mcfMetricPublicationEligibilityResult)
    .values(input.peEligibilityResults.map(r => ({
      metricContractVersionUid: input.metricContractVersionUid,
      certificationRecordId: null,
      ...r,
    })))
    .returning();

  // 7. UPDATE state — M3 trigger fires and enforces hashes NOT NULL on parent
  await tx.update(mcfMetricContractVersion)
    .set({ governanceStateCode: 'approved' })
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, input.metricContractVersionUid));

  return {
    metricContractVersionUid,
    newStateCode: 'approved',
    hashesApplied: hashes,
    peResultUids: peResults.map(r => r.peResultUid),
    committed: !input.dryRun,
  };
});
```

#### 8.3.2 Substrate enforcement

- M3 state-transition trigger fires at the state UPDATE (step 7): validates `review → approved`, then checks parent's 6 hash columns NOT NULL. Both pass because step 5 populated them within the same tx.
- M3 descriptive-immutability trigger does NOT fire (no descriptive columns changed on the MCV; only state).
- No cert at this transition.

#### 8.3.3 Race-correctness binding (refers to §5.3)

The child-row locks acquired in step 2 prevent any concurrent INSERT / UPDATE / DELETE on the bindings, filters, or dim refs of this MCV during steps 3-7. The hashes computed in step 3 therefore bind to the exact child-row contents that become `'approved'` at step 7. No subsequent reader can find a parent at `'approved'` with hashes that disagree with the child-row state. This is the M4 design's core authority-boundary invariant.

### 8.4 `activateMetric` (approved → active)

#### 8.4.1 Pre-transaction validation

```typescript
if (input.cert.rationaleText.length < 40) {
  throw new InvalidInputError('rationale must be at least 40 characters');
}
if (input.cert.certifierRoleAtAction !== 'operator') {
  throw new InvalidInputError('approved->active transition requires operator role');
}
// idempotency check
if (input.idempotencyKey) {
  const existing = await this.lookupIdempotentResult(input.idempotencyKey);
  if (existing) return existing;
}
```

#### 8.4.2 Transaction body

Cert is INSERTed first; PE result rows are INSERTed second with `certification_record_id` populated at INSERT time. No backfill UPDATE — strict append-only discipline (resolves F-2 from the DBCP review).

```typescript
await db.transaction(async (tx) => {
  // 1. Verify MCV is in 'approved' state (locked)
  const [mcv] = await tx.select(...).where(...).for('update');
  if (mcv.governanceStateCode !== 'approved') throw new InvalidStateError(...);

  // 2. INSERT metric_transition cert FIRST (so PE rows can reference its id at INSERT time)
  const [cert] = await tx.insert(mcfCertificationRecord)
    .values({
      primitiveType: 'metric_contract_version',
      primitiveId: input.metricContractVersionUid,
      actionCode: 'metric_transition',
      fromStateCode: 'approved',
      toStateCode: 'active',
      isArchivedAfter: null,
      // governance_scope column removed — sibling table is implicitly MCF-scoped (D-19 reversed per P-22)
      subjectKind: 'metric_publication',
      ...input.cert,
    })
    .returning();

  // 3. INSERT PE-MC-1..PE-MC-10 result rows with cert_id at INSERT time (append-only; no UPDATE)
  const peResults = await tx.insert(mcfMetricPublicationEligibilityResult)
    .values(input.peEligibilityResults.map(r => ({
      metricContractVersionUid: input.metricContractVersionUid,
      certificationRecordId: cert.certificationRecordId,
      ...r,
    })))
    .returning();

  // 4. UPDATE state — M3 trigger fires; sees the cert just inserted (step 2); passes
  await tx.update(mcfMetricContractVersion)
    .set({ governanceStateCode: 'active' })
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, input.metricContractVersionUid));
  // M3 trigger ALSO flips is_current=TRUE on this row + demotes prior active (see §8.4.3)

  // 5. Persist idempotency key result for future retries
  if (input.idempotencyKey) {
    await this.persistIdempotentResult(tx, input.idempotencyKey, {...});
  }

  return { metricContractVersionUid, newStateCode: 'active', certificationRecordId: cert.certificationRecordId, peResultUids, isCurrentDemoted, committed: !input.dryRun };
});
```

#### 8.4.3 Substrate enforcement

- M3 trigger validates `approved → active`, then `SELECT EXISTS` on the cert. Same-tx INSERT (step 2) is visible. Passes.
- M3 trigger flips `is_current=TRUE` on this row, demotes prior active row via its own inner `UPDATE mcf.metric_contract_version SET is_current = FALSE WHERE ... AND is_current = TRUE`.
- M3 descriptive-immutability trigger on the activating MCV: this UPDATE changes only `governance_state_code`; the trigger's pure-state-only early-return path (M3 DBCP §7.3) permits it.
- **M3 trigger dependency note (resolves F-13).** M4's activation relies on M3's descriptive-immutability trigger NOT rejecting the M3-internal `is_current` UPDATE on the demoted active sibling. The M3 trigger handles this: when only `is_current` changes (state unchanged) on an `'active'`-state row, the trigger's "reject if OLD.state IN ('approved','superseded')" branch does NOT fire because OLD.state is `'active'`. This is a load-bearing M3 trigger behavior. If a future M3 amendment tightens descriptive-immutability to reject all non-state UPDATEs on `'active'` rows, M4's activation would break. The M4 implementation PR's integration test (§14.4 "Full lifecycle") exercises this path; any future M3 amendment must preserve this property or coordinate with an M4 amendment.

### 8.5 `supersedeMetric` (active → superseded)

#### 8.5.1 Pre-transaction validation

```typescript
if (input.cert.rationaleText.length < 40) throw new InvalidInputError(...);
if (input.cert.certifierRoleAtAction !== 'operator') throw new InvalidInputError(...);
if (!['editorial', 'meaning_bearing'].includes(input.correctionClassCode)) throw new InvalidInputError(...);
```

#### 8.5.2 Transaction body

```typescript
await db.transaction(async (tx) => {
  // 1. Lock both predecessor and successor MCV rows
  const [predecessor] = await tx.select(...).where(eq(..., input.predecessorMetricContractVersionUid)).for('update');
  if (predecessor.governanceStateCode !== 'active') throw new InvalidStateError(...);
  if (predecessor.isCurrent !== true) throw new InvalidStateError(...);

  const [successor] = await tx.select(...).where(eq(..., input.successorMetricContractVersionUid)).for('update');
  if (successor.governanceStateCode !== 'active') throw new InvalidStateError(...);
  if (successor.isCurrent !== true) throw new InvalidStateError(...);
  if (predecessor.metricContractUid === successor.metricContractUid) throw new InvalidInputError('supersession requires different parents');

  // 2. INSERT metric_supersede cert
  const [cert] = await tx.insert(mcfCertificationRecord)
    .values({
      primitiveType: 'metric_contract_version',
      primitiveId: input.predecessorMetricContractVersionUid,
      actionCode: 'metric_supersede',
      fromStateCode: 'active',
      toStateCode: 'superseded',
      supersedesPrimitiveId: input.predecessorMetricContractVersionUid,
      // governance_scope column removed — sibling table is implicitly MCF-scoped (D-19 reversed per P-22)
      subjectKind: 'metric_supersession',
      ...input.cert,
    })
    .returning();

  // 3. INSERT mcf.metric_supersession row
  const [supersession] = await tx.insert(mcfMetricSupersession)
    .values({
      predecessorMetricContractUid: predecessor.metricContractUid,
      predecessorMetricContractVersionUid: input.predecessorMetricContractVersionUid,
      successorMetricContractUid: input.successorMetricContractUid,
      successorMetricContractVersionUid: input.successorMetricContractVersionUid,
      correctionClassCode: input.correctionClassCode,
      operatorSub: input.cert.certifierSub,
      rationaleText: input.cert.rationaleText,
      certificationRecordId: cert.certificationRecordId,
      panelRunUid: input.cert.panelRunUid ?? null,
    })
    .returning();

  // 4. UPDATE predecessor state — M3 trigger fires; sees supersession + active successor
  await tx.update(mcfMetricContractVersion)
    .set({ governanceStateCode: 'superseded' })
    .where(eq(mcfMetricContractVersion.metricContractVersionUid, input.predecessorMetricContractVersionUid));

  return { ..., certificationRecordId: cert.certificationRecordId, supersessionUid: supersession.supersessionUid, committed: !input.dryRun };
});
```

#### 8.5.3 Substrate enforcement

- M3 state-transition trigger fires at the predecessor UPDATE:
  - Validates `active → superseded`
  - JOINs `mcf.metric_supersession` to find the row whose `predecessor_metric_contract_version_uid = predecessor_uid` — sees the same-tx INSERT
  - Validates successor's state = `'active'` AND `is_current = TRUE` — sees the locked successor row
  - Flips predecessor's `is_current` to FALSE
  - Passes
- Supersession's UNIQUE on `predecessor_metric_contract_uid` enforces "a predecessor MC can be superseded at most once" — second supersession of the same predecessor would fail at the INSERT.

---

## 9. `mcf.certification_record` row contract

### 9.1 Column population matrix (25 columns × 3 action codes — per the sibling shape from M3 cert-amendment §4.2)

The M4 service writes to `mcf.certification_record` (the per-framework sibling created by the M3 cert-amendment). The sibling table has 25 columns — it drops `governance_scope` (single-table; always implicitly MCF) and `target_registry_id` (BCF Registry Model A specific) from the contract-cert shape. CHECK constraints are tight to MCF semantics (see M3 cert-amendment §4.3).

| Column | metric_create | metric_transition | metric_supersede |
|---|---|---|---|
| `certification_record_id` | auto (`gen_random_uuid()`) | auto | auto |
| `primitive_type` | `'metric_contract_version'` (CHECK-enforced single value) | same | same |
| `primitive_id` | new MCV uid | activating MCV uid | predecessor MCV uid |
| `action_code` | `'metric_create'` (CHECK-enforced 3-element MCF enum) | `'metric_transition'` | `'metric_supersede'` |
| `from_state_code` | NULL (CHECK couples to action_code) | `'approved'` | `'active'` |
| `to_state_code` | `'draft'` (CHECK couples to action_code) | `'active'` | `'superseded'` |
| `is_archived_after` | NULL (active cert) | NULL | NULL |
| `gate_results_json` | from input `cert.gateResultsJson` | from input | from input |
| `advisory_verdicts_json` | from input `cert.advisoryVerdictsJson` or `[]` | from input | from input |
| `override_gate_code` | from input `cert.override?.gateCode` or NULL | same | same |
| `override_rationale_text` | from input `cert.override?.rationaleText` or NULL | same | same |
| `override_followup_task_uid` | from input `cert.override?.followupTaskUid` or NULL | same | same |
| `certifier_sub` | from input `cert.certifierSub` | same | same |
| `certifier_role_at_action` | from input (typically `'panel'` or `'system'`; CHECK admits `panel`/`operator`/`system`) | from input (must be `'operator'`) | from input (must be `'operator'`) |
| `certifier_email` | from input or NULL | same | same |
| `supersedes_primitive_id` | NULL (CHECK couples to action_code) | NULL | predecessor MCV uid (CHECK-enforced when action_code='metric_supersede') |
| `created_at` | auto (`now()`) | auto | auto |
| `panel_run_uid` | from input or NULL; FK to `contract.panel_output_record` enforced when non-NULL | from input or NULL | from input or NULL |
| `prompt_version` | from input | same | same |
| `model_identity_json` | from input | same | same |
| `input_hash` | from input (panel workbench fingerprint) | same | same |
| `policy_version` | from input (must reference ACTIVE `contract.framework_policy` row with `scope_code='mcf'`); always NOT NULL (outside NF1 all-or-none bundle per M3 amendment §4.3) | same | same |
| `sampling_status` | from input (part of NF1 all-or-none bundle) | same | same |
| `grounding_check_result` | from input (PE-MC-1 no-fabrication outcome; part of NF1 all-or-none bundle) | same | same |
| `subject_kind` | `'metric_contract_version'` (CHECK-enforced 3-element MCF enum) | `'metric_publication'` | `'metric_supersession'` |

**Columns NOT present on the sibling (dropped from BCF cert shape):**
- `governance_scope` — single-table sibling; the table name itself is the framework boundary. No discriminator needed.
- `target_registry_id` — BCF Registry Model A specific. Not applicable to MCF.

The 25 columns above (excluding the 2 dropped) match the M3 cert-amendment §4.2 spec exactly.

### 9.2 Required vs optional input fields per action

| Field | metric_create | metric_transition | metric_supersede |
|---|---|---|---|
| `certifierSub` | REQUIRED | REQUIRED | REQUIRED |
| `certifierRoleAtAction` | REQUIRED (any of panel/operator/system) | REQUIRED (must be 'operator') | REQUIRED (must be 'operator') |
| `rationaleText` | optional | REQUIRED (≥40 chars) | REQUIRED (≥40 chars) |
| `policyVersion` | REQUIRED (must reference ACTIVE `framework_policy` row: `effective_to IS NULL OR effective_to > now()`) | same | same |
| `gateResultsJson` | REQUIRED (panel's gate output) | REQUIRED (PE-MC-1..PE-MC-10 summary) | REQUIRED (supersession-justification summary) |
| `panelRunUid` | optional | optional (operator-initiated re-cert) | optional (operator-initiated supersession) |
| `inputHash` | required if panel-driven | required if panel-driven | required if panel-driven |
| `override` | optional | optional | optional |

### 9.3 Cert content invariants

- **Framework boundary is the table itself.** Every row in `mcf.certification_record` is implicitly MCF-scoped; no `governance_scope` column (D-19 REVERSED per P-22).
- **`primitive_type` is single-valued** (`'metric_contract_version'`) enforced by CHECK; no other primitive type writes to this table.
- **`action_code` is 3-valued** (`metric_create` / `metric_transition` / `metric_supersede`); CHECK couples to `from_state_code` / `to_state_code` pair per the M3 amendment's `mcf_cert_state_transition_chk`.
- **`subjectKind` is 3-valued** (one per action_code) and distinguishes the cert's purpose for downstream readers (audit dashboards, operator console).
- **`policy_version` is always NOT NULL** — every cert binds to an active `mcf` framework_policy version. Outside the NF1 all-or-none bundle (which has 6 panel-attestation fields, not BCF's 7 — per M3 amendment §4.3 P-Amendment-3 explanation).
- The `gateResultsJson` shape is a summary — full per-PE-MC detail lives in `mcf.metric_publication_eligibility_result`. Cert carries the verdict roll-up; PE result table carries the evidence.
- `advisory_verdicts_json` may carry panel-emitted advisories (recommendations that didn't block the verdict but are worth surfacing on the operator's review screen).

---

## 10. Framework policy / operator confirm rule design

### 10.1 `operator_confirm_rule` seeds (corrected per P-27)

M4 apply ships two INSERTs into the shared `contract.operator_confirm_rule` table. The M3 cert-amendment already extended this table's `scope` CHECK to admit `'mcf'` and its `transition` CHECK to admit `'active_to_superseded'`; both seeds below are now admissible at apply time.

```sql
INSERT INTO contract.operator_confirm_rule (
  rule_uid, scope, transition, action_code, predicate_ast_json, rationale_required
) VALUES (
  'mcf_metric_transition_approved_to_active',
  'mcf',
  'approved_to_active',
  'require_operator_confirm',
  '{"type":"true"}'::jsonb,
  TRUE
);

INSERT INTO contract.operator_confirm_rule (
  rule_uid, scope, transition, action_code, predicate_ast_json, rationale_required
) VALUES (
  'mcf_metric_supersede_active_to_superseded',
  'mcf',
  'active_to_superseded',
  'require_operator_confirm',
  '{"type":"true"}'::jsonb,
  TRUE
);
```

**Two corrections vs. the pre-rewrite seeds:**
1. **`transition` notation:** uses `_to_` underscore notation (`'approved_to_active'`, `'active_to_superseded'`) to match the live CHECK enum, not arrow notation (`'approved->active'`).
2. **`action_code` semantic fix (P-27):** populated as `'require_operator_confirm'` — the **enforcement directive** the rule asserts when matched. The pre-rewrite version used `'metric_transition'` / `'metric_supersede'`, which are **MCF cert action codes** (governed acts), not enforcement directives. These belong on `mcf.certification_record.action_code` (the cert table — see §9.1), not on `operator_confirm_rule.action_code` (the rule table). See §10.5 for the formal semantic distinction.

The `predicate_ast_json` is the trivial "always true" predicate per MCF §11.4 always-confirm stance. Future amendment may add risk-band predicates (e.g. "only require operator confirm if MC has tenants bound").

### 10.2 `framework_policy` seed

M4 apply ships one INSERT for the active `mcf` policy. The M3 cert-amendment already extended the `scope_code` CHECK to admit `'mcf'`, so the seed is admissible at apply time.

```sql
INSERT INTO contract.framework_policy (
  policy_uid, policy_version, scope_code,
  eligible_operations_json,
  consensus_requirement_json,
  sampling_rate,
  operator_confirm_rules_uid_list,
  notification_policy_json,
  calibration_regression_thresholds_json,
  adr_ref
) VALUES (
  'mcf_v1',
  '1.0.0',
  'mcf',
  '["metric_create","metric_transition","metric_supersede"]'::jsonb,
  '{"models_required":3,"agreement_threshold":2,"models":["maker","checker","moderator"]}'::jsonb,
  0.10,
  ARRAY['mcf_metric_transition_approved_to_active','mcf_metric_supersede_active_to_superseded'],
  '{}'::jsonb,
  '{}'::jsonb,
  'DEC-c3e57f'
);
```

### 10.3 Service-level enforcement of operator-confirm

The M4 service validates `certifierRoleAtAction === 'operator'` and `rationaleText.length >= 40` BEFORE the tx opens for both `activateMetric` and `supersedeMetric`. The substrate's `operator_confirm_rule` row is the audit/policy record; M4's pre-transaction validation is the runtime gate.

If future operator decision tightens `metric_create` to also be operator-confirm, an additional `operator_confirm_rule` row is added by amendment + the service is amended to validate the role/rationale for `createMetricDraft` too.

### 10.4 `framework_policy` lifecycle pattern (single-active-per-scope; amendments archive via `effective_to`)

The `contract.framework_policy` table supports policy versioning via the `effective_from` / `effective_to` columns. The MCF discipline:

- **One active row per (`scope_code`, time window).** At any moment, exactly one `framework_policy` row for `scope_code = 'mcf'` has `effective_to IS NULL OR effective_to > now()`.
- **Amendments INSERT a new row + UPDATE the old row's `effective_to`.** Never DELETE a `framework_policy` row — certs already written reference the row by `policy_version` and the historical record is preserved.
- **Cert validation requires active row.** Per §6.7 / §6.8 / §9.2, M4 cert writers reject input whose `policyVersion` does not match a currently-active `mcf` `framework_policy` row.

Concrete amendment pattern (example: tightening `consensus_requirement_json` after operator review):

```sql
-- Archive the prior active row
UPDATE contract.framework_policy
   SET effective_to = now()
 WHERE scope_code = 'mcf'
   AND policy_uid = 'mcf_v1'
   AND policy_version = '1.0.0'
   AND effective_to IS NULL;

-- Insert the new active row
INSERT INTO contract.framework_policy (
  policy_uid, policy_version, scope_code,
  eligible_operations_json,
  consensus_requirement_json,
  sampling_rate,
  operator_confirm_rules_uid_list,
  notification_policy_json,
  calibration_regression_thresholds_json,
  adr_ref
) VALUES (
  'mcf_v1', '1.1.0', 'mcf',
  '["metric_create","metric_transition","metric_supersede"]'::jsonb,
  '{"models_required":3,"agreement_threshold":3,"models":["maker","checker","moderator"]}'::jsonb,  -- tightened to unanimous
  0.10,
  ARRAY['mcf_metric_transition_approved_to_active','mcf_metric_supersede_active_to_superseded'],
  '{}'::jsonb, '{}'::jsonb, 'DEC-c3e57f'
);
```

After this amendment:
- Certs written under `policyVersion='1.0.0'` remain valid historical records.
- New cert writes must reference `policyVersion='1.1.0'` (the active row).
- A subsequent M4 amendment authors a fresh ADR for the policy change (or extends DEC-c3e57f with an errata).

Amendments to the policy are operator-authorized DBCP changes — the M4 implementation PR does NOT include any such amendment; the seed in §10.2 is the initial baseline.

### 10.5 Semantic distinction: cert `action_code` vs rule `action_code` (corrected per P-27)

These are **two different action_code columns on two different tables** with **two different meanings**. Confusing them was the documentation bug fixed in this rewrite per P-27:

| Column | Table | Meaning | Values |
|---|---|---|---|
| `action_code` | `mcf.certification_record` | **The governed act being authorized.** What did this cert authorize? | `'metric_create'`, `'metric_transition'`, `'metric_supersede'` (3-element MCF enum per M3 cert-amendment) |
| `action_code` | `contract.operator_confirm_rule` | **The rule's enforcement directive.** When this rule matches, what should the system do? | `'require_operator_confirm'`, `'route_to_operator_review'`, `'block'` (3-element enforcement enum; shared with BCF; **unchanged by M3 cert-amendment** per D-Correction-4) |

The `operator_confirm_rule` row asserts "when scope='mcf' and transition='approved_to_active', require operator confirm" — the directive (`require_operator_confirm`) is what the system enforces. The cert row that subsequently gets written (when the operator does confirm) records `action_code='metric_transition'` because the governed act being authorized is the publication transition. The two values live on different tables; they are not interchangeable.

**Reading discipline.** When this DBCP says "action_code", it is always disambiguated by the table:
- `mcf.certification_record.action_code` → MCF cert action codes
- `contract.operator_confirm_rule.action_code` → enforcement directives

**M4 makes no proposal to change `contract.operator_confirm_rule.action_code` CHECK** (per D-Correction-4 ACCEPTED). The current 3-element enum is correct.

---

## 11. Concurrency and idempotency

### 11.1 Concurrency control

Each M4 write method uses `SELECT ... FOR UPDATE` on the MCV row(s) it operates on, at the start of the transaction. This serializes concurrent operations against the same MCV.

| Method | Locked rows |
|---|---|
| `createMetricDraft` | none (creating new rows) |
| `submitForReview` | the MCV being transitioned |
| `approveForActivation` | **MCV + parent MC + ALL child rows under the MCV** (bindings + filters + dim refs), PK-ordered (per §5.3 race-correctness binding); see §8.3.1 step 1-2 |
| `activateMetric` | the MCV being activated; demotion of any sibling `is_current=TRUE` row is performed inside the M3 state-transition trigger's own UPDATE (not service-locked) |
| `supersedeMetric` | BOTH the predecessor MCV and the successor MCV (UUID-ordered per §11.2) |

### 11.2 Deadlock avoidance

In `supersedeMetric`, both rows are locked. To avoid deadlocks with concurrent transitions on the predecessor or successor, the service ALWAYS locks in `metric_contract_version_uid` order (lexicographic on the UUID). If predecessor's UUID < successor's UUID, lock predecessor first; otherwise lock successor first.

### 11.3 Idempotency-key semantics

**Methods that accept `idempotencyKey` in v1:** `createMetricDraft`, `activateMetric`, `supersedeMetric` (see input types in §6.2, §6.5, §6.6). These are the three certificate-writing methods.

**Methods that do NOT accept `idempotencyKey` in v1:** `submitForReview`, `approveForActivation`. These are AI-default state transitions with no operator retry semantics; if they fail, the panel re-runs and the service re-checks state at entry. A future amendment may extend idempotency-key support to these methods if operational evidence justifies it.

The service maintains a small idempotency table (`mcf.metric_cert_writer_idempotency` — see §11.4) keyed by `idempotency_key` (single column, globally unique within MCF scope). The `action_code` is non-key metadata. Before opening the tx, the service checks (for methods that accept the key):

- If a row with this key exists and was successful (`status='committed'`), return the cached result (no new tx).
- If a row with this key exists and the prior call is still in-flight (`status='pending'`), block until it completes (or surfaces as stuck-pending per §11.6).
- If no row exists, INSERT a "claim" row with status `pending`, open the tx, do the work, then UPDATE the idempotency row to `committed` (or `rolled_back` on failure).
- If a row with this key exists but its `action_code` does not match the current call's action, the service throws `IdempotencyKeyReuseError` — keys cannot be reused across different actions.

### 11.4 Idempotency table (M4 ships this)

```sql
CREATE TABLE mcf.metric_cert_writer_idempotency (
  idempotency_key text NOT NULL PRIMARY KEY,
  action_code text NOT NULL,
  result_json jsonb NULL,
  status text NOT NULL CHECK (status IN ('pending', 'committed', 'rolled_back')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_mcf_idempotency_status_at ON mcf.metric_cert_writer_idempotency (status, updated_at);
```

**Single-column PK on `idempotency_key`** (resolves F-9 from DBCP review). One key globally identifies one operation; `action_code` is metadata for diagnostics, not a key component. Mismatch (same key, different action) is a caller error — service throws `IdempotencyKeyReuseError` before opening the tx.

### 11.5 Idempotency for `dryRun`

`dryRun=true` calls do not write to the idempotency table. Each dry-run starts fresh.

### 11.6 Cleanup policy (committed / rolled_back / stuck-pending)

A nightly cleanup job (separate, not part of the M4 service code; can ship as a `scripts/mcf-idempotency-cleanup.mjs` in the M4 implementation PR, run via cron):

| Row state | Cleanup policy |
|---|---|
| `status='committed'` | Retain indefinitely (small table — ~1 row per MC operation; long-tail retention supports very-late retry idempotency claims) |
| `status='rolled_back'` and `updated_at < now() - interval '30 days'` | DELETE |
| `status='pending'` and `updated_at < now() - interval '5 minutes'` | Treat as **stuck-pending** (orphaned): set `status='rolled_back'`, append diagnostic note to `result_json` (`{"cleanup_reason":"stuck_pending_5min_timeout"}`), so future retries with the same key see the rolled-back state and can proceed |

**Why stuck-pending cleanup is needed.** If the service crashes between the "INSERT pending claim" step and the tx commit/abort, the pending row remains. Without cleanup, a future caller using the same key would block forever (waiting for the prior call to finish) or be rejected (depending on retry semantics). The 5-minute timeout is much longer than the longest expected M4 tx (`approveForActivation` slow-flag = 5 s per §5.5); pending rows older than 5 min are presumed orphaned.

The cleanup script itself uses a short tx; runs once per minute is reasonable. Stuck-pending detection is idempotent — running the cleanup script multiple times on the same row is safe.

---

## 12. Error handling and rollback

### 12.1 Error categories

| Category | Examples | Service behavior |
|---|---|---|
| Input validation | rationale <40 chars, wrong role, missing required field, unknown action_code | Throw before opening tx; nothing is written |
| State validation | MCV not in expected source state | Throw inside tx; tx rolls back; idempotency row marked `rolled_back` |
| Trigger rejection | M3 trigger refuses (e.g. hash NOT-NULL violation, missing successor) | Postgres raises `check_violation`; Drizzle surfaces as exception; tx rolls back |
| Concurrent modification | another tx held the lock and committed conflicting state | Postgres raises serialization failure; service retries with backoff (max 3 retries; configurable) |
| Connection failure | DB connection drop mid-tx | Postgres rolls back; service surfaces error to caller; idempotency-key retry path picks it up |
| Bug in service | unexpected exception | Tx rolls back; error logged + reported; idempotency marked `rolled_back` |

### 12.2 Rollback semantics

Postgres handles rollback automatically when the tx aborts. No application-level cleanup beyond updating the idempotency row's status. No two-phase commit. No saga pattern.

### 12.3 Partial-state recovery

There are no partial states. Either the tx commits (cert + state + audit all present) or it rolls back (nothing changed). No code path can leave half-state.

### 12.4 Diagnostic surface

When a M4 method throws, the error includes:
- The transition attempted
- The MCV uid
- The trigger error message (when applicable)
- The idempotency-key status (if any)

Logged at WARN for input/state validation; ERROR for unexpected. Caller decides whether to retry (idempotency key supports it).

### 12.5 Substrate rollback (rewritten per P-29)

The M4 implementation PR ships a companion rollback DDL (`bc-core/docker/redesign/06-mcf-cert-authority-rollback.sql`) that reverses **only what M4 forward-shipped**. The M3 cert-amendment substrate (mcf.certification_record table, trigger redirect, FK redirect, shared CHECK extensions) is owned by the M3 cert-amendment's own rollback path (per `05a-mcf-cert-amendment-rollback.sql`); M4 must NOT attempt to revert any of it.

```sql
BEGIN;
DROP TABLE IF EXISTS mcf.metric_cert_writer_idempotency;
DROP TABLE IF EXISTS mcf.metric_publication_eligibility_result;
DELETE FROM contract.operator_confirm_rule WHERE scope = 'mcf';
DELETE FROM contract.framework_policy WHERE scope_code = 'mcf';
COMMIT;
```

The DDL is `BEGIN/COMMIT` wrapped (per the M3 cert-amendment §9.4 atomicity discipline; mirrors that pattern). The `operator_confirm_rule` DELETE uses `WHERE scope = 'mcf'` (the authoritative discriminator) rather than `WHERE rule_uid LIKE 'mcf_%'` (a convention). The prefix is convention-only; `scope` is the substrate column that uniquely binds rows to MCF. The `framework_policy` DELETE uses the same scope-based discipline (`WHERE scope_code = 'mcf'`).

**Out of M4's rollback scope (M3-cert-amendment-owned):**
- `mcf.certification_record` table (and its indexes, CHECKs, FK to `contract.panel_output_record`)
- `mcf.fn_mcv_state_transition_check()` cert-lookup redirect to sibling
- `mcf.metric_supersession.fk_mcs_cert` redirect to sibling
- `contract.framework_policy_scope_code_chk` extension (`'mcf'` admission)
- `contract.operator_confirm_rule_scope_chk` extension (`'mcf'` admission)
- `contract.operator_confirm_rule_transition_chk` extension (`'active_to_superseded'` admission)

If those need to be rolled back, the operator runs `docker/redesign/05a-mcf-cert-amendment-rollback.sql` (a separate operator-authorized DCP gate) AFTER the M4 rollback completes. The M3-amendment rollback enforces preconditions via `DO $$ ... RAISE EXCEPTION ... END $$;` guards that require `mcf.certification_record` to have 0 rows + no MCF policy/rule rows — which the M4 rollback (above) achieves.

This is the same rollback discipline as M2 + M3 + M3-cert-amendment: safe only when the tables are empty. Service binaries are not "rolled back" by DDL — that's a code revert (git revert the implementation PR).

### 12.6 M4 DDL apply order (forward) — `docker/redesign/06-mcf-cert-authority.sql` (rewritten per P-29)

Mirrors M3 + M3-cert-amendment DBCP discipline. Single-file DDL; `ON_ERROR_STOP=1` at apply time; **wrapped in `BEGIN;...COMMIT;`** for whole-file atomicity (consistent with M3 cert-amendment §9.4). M4 ships only what M4 owns; M3 cert-amendment substrate is the strict prerequisite (verified by dry-run §14.1 #2a/#2b/#2c/#3a/#3b/#3c).

```sql
BEGIN;

-- Step 1: Create the two new M4-owned mcf.* tables (no FK ordering constraint
-- between them; order shown for cleanliness)
CREATE TABLE mcf.metric_publication_eligibility_result ( ... );  -- per §4.2 (10 cols, 2 CHECKs, 2 FKs incl. fk_mper_cert -> mcf.certification_record)
CREATE TABLE mcf.metric_cert_writer_idempotency ( ... );          -- per §11.4 (6 cols, single-col PK on idempotency_key, 1 status CHECK)

-- Step 2: Indexes on the new tables
CREATE INDEX idx_mcf_mper_mcv_at           ON mcf.metric_publication_eligibility_result (metric_contract_version_uid, evaluated_at DESC);
CREATE INDEX idx_mcf_mper_cert             ON mcf.metric_publication_eligibility_result (certification_record_id);
CREATE INDEX idx_mcf_mper_check_verdict_at ON mcf.metric_publication_eligibility_result (pe_check_code, verdict_code, evaluated_at DESC);
CREATE INDEX idx_mcf_idempotency_status_at ON mcf.metric_cert_writer_idempotency (status, updated_at);

-- Step 3: Seed rows for Foundation Governance Substrate (operator_confirm_rule + framework_policy)
-- The M3 cert-amendment already extended scope_code / scope / transition CHECKs to admit MCF.
-- These seeds are now admissible at apply time.
INSERT INTO contract.operator_confirm_rule (...) VALUES ('mcf_metric_transition_approved_to_active', 'mcf', 'approved_to_active', 'require_operator_confirm', ...);   -- per §10.1 (P-27 corrected)
INSERT INTO contract.operator_confirm_rule (...) VALUES ('mcf_metric_supersede_active_to_superseded', 'mcf', 'active_to_superseded', 'require_operator_confirm', ...); -- per §10.1 (P-27 corrected)
INSERT INTO contract.framework_policy        (...) VALUES ('mcf_v1', '1.0.0', 'mcf', ...);                                                                            -- per §10.2

-- Step 4: COMMENT ON TABLE / ON COLUMN annotations (see §12.7)
COMMENT ON TABLE mcf.metric_publication_eligibility_result IS '...';
COMMENT ON TABLE mcf.metric_cert_writer_idempotency IS '...';
COMMENT ON COLUMN mcf.metric_publication_eligibility_result.pe_check_code IS '...';
-- ... (full list in §12.7)

COMMIT;
```

**REMOVED post-rewrite (per P-23 / P-29):**
- ~~Step (creating `mcf.certification_record`)~~ — M3 cert-amendment shipped it.
- ~~Step (conditional cert-lookup index on `contract.certification_record`)~~ — D-17 RETIRED; no index on `contract.*` is M4's concern.
- ~~Step (ALTERing M3 trigger function)~~ — M3 cert-amendment shipped it.
- ~~Step (ALTERing `fk_mcs_cert` to point at sibling)~~ — M3 cert-amendment shipped it.
- ~~Step (extending shared CHECK enums on `framework_policy` + `operator_confirm_rule`)~~ — M3 cert-amendment shipped it.

#### 12.6.1 Why this order

- **Tables before indexes**: indexes reference their owning table.
- **Tables/indexes before seeds**: seeds INSERT into existing tables (`contract.operator_confirm_rule`, `contract.framework_policy`); these tables predate M4 — no creation needed. The CHECK extensions that admit MCF values were shipped by the M3 cert-amendment; M4 dry-run §14.1 #3a/#3b/#3c confirm they're in place before apply.
- **COMMENTs last**: COMMENTs are documentation; they don't affect any subsequent statement.

#### 12.6.2 Idempotency at the DDL layer

`CREATE TABLE` and `CREATE INDEX` (non-`IF NOT EXISTS`) are NOT idempotent — a re-apply against an already-applied DB would error on duplicate object names. Mirrors M2 + M3 + M3-cert-amendment discipline. The dry-run preconditions confirm the new objects are absent before apply.

`INSERT` statements are NOT idempotent at the substrate level (no `ON CONFLICT` clauses). The dry-run #5 + #6 preconditions confirm no MCF rows exist in `framework_policy` or `operator_confirm_rule` before apply.

The `BEGIN;...COMMIT;` whole-file wrapper guarantees that any in-flight failure rolls back the entire amendment atomically. Mirrors the M3 cert-amendment §9.4 discipline.

`COMMENT ON ...` is idempotent (re-COMMENT replaces).

### 12.7 COMMENT ON TABLE / COMMENT ON COLUMN enumeration

The M4 implementation PR ships annotations matching the M3 DBCP §10.2 discipline (one COMMENT per new table + key columns). Implementation team writes the text; the enumeration below specifies which targets MUST carry comments.

#### 12.7.1 COMMENT ON TABLE (2 required)

| Target | Content (summary) |
|---|---|
| `mcf.metric_publication_eligibility_result` | "Per-PE-MC publication eligibility result audit per MCF requirements §13 + §17.1. One row per (metric_contract_version, pe_check_code, evaluated_at). Append-only per Invariant V. PE-MC-10 row may cite a `mcf.metric_self_verification_result` (M9; FK deferred). `certification_record_id` populated at INSERT time when emitted within a cert-writing transition (`activateMetric`); NULL for pre-approve checks (`approveForActivation`). Cited by certs via `gate_results_json` summary." |
| `mcf.metric_cert_writer_idempotency` | "Idempotency claim table for MCF cert-writer service operations. Single-column PK on `idempotency_key`. Status enum: pending / committed / rolled_back. Cleanup per §11.6 (committed indefinite; rolled_back >30 days deleted; pending >5 min orphan-cleaned). Service-internal; not part of the governance audit trail." |

#### 12.7.2 COMMENT ON COLUMN (minimum-required set)

The implementation team should aim for parity with the M3 DBCP COMMENT density. At minimum, the following columns MUST carry COMMENTs:

| Target | Why |
|---|---|
| `mcf.metric_publication_eligibility_result.pe_check_code` | Closed 10-element enum; comment lists PE-MC-1..PE-MC-10 |
| `mcf.metric_publication_eligibility_result.verdict_code` | Closed 3-element enum: `PASS` / `REJECT` / `OPERATOR_REVIEW` (per MCF §13) |
| `mcf.metric_publication_eligibility_result.certification_record_id` | Nullable; populated at INSERT for cert-emitting transitions; FK-enforced when set |
| `mcf.metric_publication_eligibility_result.satisfying_verification_result_uid` | PE-MC-10 only; FK to `mcf.metric_self_verification_result` deferred until M9 ships |
| `mcf.metric_publication_eligibility_result.panel_run_uid` | FK to M5's `mcf.metric_authoring_panel_run` deferred until M5 ships |
| `mcf.metric_cert_writer_idempotency.idempotency_key` | Single-column PK; one key globally identifies one operation (per §11.3) |
| `mcf.metric_cert_writer_idempotency.action_code` | Non-key metadata for diagnostics; service throws `IdempotencyKeyReuseError` on action mismatch for the same key |
| `mcf.metric_cert_writer_idempotency.status` | Lifecycle enum: pending → committed OR pending → rolled_back |

Additional comments are encouraged but not required. M3 DBCP §10.2 sets the precedent for column-comment density.

#### 12.7.3 Dry-run statement count update

§14.1 check #7 mentions "≈ 2 COMMENT ON TABLE". The minimum COMMENT count is therefore **2 COMMENT ON TABLE + ≥8 COMMENT ON COLUMN** = ≥10 COMMENT statements. The dry-run script accepts any count ≥ this minimum.

---

## 13. Implementation sequencing options

### 13.1 Option A — Single PR (RECOMMENDED)

One PR ships everything:

| Layer | Files |
|---|---|
| DDL | `docker/redesign/06-mcf-cert-authority.sql` (PE result table + idempotency table + operator_confirm_rule seeds + framework_policy seed + optional index per D-17) |
| Rollback DDL | `docker/redesign/06-mcf-cert-authority-rollback.sql` |
| Drizzle | `src/database/schema/mcf/metric-publication-eligibility-result.ts`; `src/database/schema/mcf/metric-cert-writer-idempotency.ts`; `src/database/schema/mcf/index.ts` (re-exports) |
| Service | `src/registry/mcf/mcf-cert-writer.service.ts`; `src/registry/mcf/mcf-cert-writer.service.spec.ts` |
| Interface | `src/registry/mcf/mcf-hash-computer.interface.ts` |
| Mock | `src/registry/mcf/mcf-hash-computer.mock.ts` |
| Verifier | `scripts/mcf-m4-dry-run.mjs`; `scripts/mcf-m4-post-apply-verification.mjs` |

**Pro:** Single review, single apply, single closeout. Matches M2 + M3 pattern.
**Pro:** Service can be tested against substrate during PR review (synthetic-row integration tests).
**Con:** Larger PR — diff stat estimated at **2500–3500 lines** including comments/tests. Breakdown: DDL ~300 + 2 Drizzle schemas ~250 + service ~400 + interface + mock ~150 + unit spec ~600 + integration spec ~600 + dry-run + verifier scripts ~700 + type definitions ~200. Comparable to bc-core PR #103 (M3) at 1703 lines but with service-class additions. Still reviewable in a single sitting.

### 13.2 Option B — Three sub-PRs

| Sub-PR | Scope |
|---|---|
| M4a | Substrate only (DDL + Drizzle + rollback + dry-run + post-apply verifier). Mirrors M2 + M3 PR shape. |
| M4b | Service (`McfCertWriterService` + interface + mock + spec). Depends on M4a substrate being live for integration tests. |
| M4c | Operator-confirm rule + framework_policy seeds (small DDL + seed verification). Could be folded into M4a; separating it keeps governance changes auditable. |

**Pro:** Smaller individual PRs; easier review.
**Pro:** Substrate can be applied before service is finalized (live testing window).
**Con:** Three apply gates instead of one; more operator overhead.
**Con:** Cross-PR dependency complexity (M4b's tests need M4a applied).

### 13.3 Recommendation

**Option A — single PR.** The M2 + M3 single-PR-per-apply-gate pattern worked well. The full M4 surface fits in one reviewable PR. Operator overhead is minimized. Sub-PR split adds coordination cost without proportional benefit.

Per the revised estimate in §13.1 (2500–3500 lines), Option A remains acceptable. If the diff stat exceeds **4000 lines** during implementation (e.g. the verifier scripts grow well beyond projection), revisit sequencing then.

### 13.4 Operator decision

| # | Decision | Recommendation |
|---:|---|---|
| O-1 | Single PR (A) vs three sub-PRs (B)? | Option A (single PR) |

---

## 14. Test and verification plan

### 14.1 Dry-run script (`scripts/mcf-m4-dry-run.mjs`)

Rewritten per P-28 for post-amendment state. The dry-run is a hard gate: **it REFUSES TO PROCEED if the DB is pre-amendment** (any of preconditions #2a / #2b / #2c / #3a / #3b / #3c fail). M4 has the M3 cert-amendment as a strict prerequisite.

| # | Check | Pass criterion |
|---:|---|---|
| 1 | `mcf` schema present | YES |
| 2 | All **8** `mcf.*` tables present (M2 + M3 + cert-amendment): metric_contract, metric_contract_version, metric_variable_binding, metric_filter_clause, metric_computed_dimension_ref, metric_contract_revision, metric_supersession, **certification_record** | YES |
| **2a** | **`mcf.certification_record` exists** (M3 cert-amendment applied — hard prereq) | YES — otherwise ABORT with "M3 cert-amendment not applied; M4 dry-run refuses to proceed" |
| **2b** | **`mcf.fn_mcv_state_transition_check()` body references `FROM mcf.certification_record`** (via pg_get_functiondef text inspection; exactly 1 occurrence) AND does NOT reference `FROM contract.certification_record` (exactly 0 occurrences) | YES — otherwise ABORT |
| **2c** | **`mcf.metric_supersession.fk_mcs_cert` targets `mcf.certification_record`** (via pg_constraint JOIN on confrelid) | YES — otherwise ABORT |
| 3 | `mcf.metric_publication_eligibility_result` ABSENT (clean slate for M4 apply) | YES |
| **3a** | **`contract.framework_policy_scope_code_chk` admits `'mcf'`** (M3 cert-amendment shared CHECK extension applied) | YES — otherwise ABORT |
| **3b** | **`contract.operator_confirm_rule_scope_chk` admits `'mcf'`** (same) | YES — otherwise ABORT |
| **3c** | **`contract.operator_confirm_rule_transition_chk` admits `'active_to_superseded'`** (same) | YES — otherwise ABORT |
| 4 | `mcf.metric_cert_writer_idempotency` ABSENT (clean slate) | YES |
| 5 | `contract.framework_policy` has no row with `scope_code='mcf'` (clean slate for M4 seed; CHECK admits the value per #3a) | YES |
| 6 | `contract.operator_confirm_rule` has no rows with `scope='mcf'` (clean slate for M4 seeds; CHECK admits the value per #3b / #3c) | YES |
| 7 | DDL file parses; statement counts match expected (**2 CREATE TABLE** for the two M4-shipped mcf.* tables + 4 CREATE INDEX + 3 INSERT seeds + 2 COMMENT ON TABLE + ≥8 COMMENT ON COLUMN per §12.7); apply order matches §12.6 | YES |
| 8 | DDL file hash captured for drift detection | YES |

**REMOVED post-rewrite (per P-23 / P-28):**
- Old check #7a (D-17 mechanical index check on `contract.certification_record`) — D-17 RETIRED; MCF certs do not write to that table; the M3 cert-amendment already shipped `idx_mcf_cert_lookup` on the sibling for the trigger hot path.

**REMOVED from M4 DDL ship list (per P-29):**
- `CREATE TABLE mcf.certification_record` — M3 cert-amendment shipped it.
- 3 shared CHECK ALTERs (`framework_policy.scope_code` + 2 `operator_confirm_rule.*`) — M3 cert-amendment shipped them.
- M3 trigger function ALTER — M3 cert-amendment shipped it.
- `fk_mcs_cert` redirect — M3 cert-amendment shipped it.
- Conditional cert-lookup index on `contract.certification_record` — RETIRED per D-17 retirement.

### 14.2 Post-apply verifier (`scripts/mcf-m4-post-apply-verification.mjs`)

~14 checks:

**Structural (1–7):**
1. `mcf.metric_publication_eligibility_result` present with 10 columns + 2 CHECKs + 2 FKs + 3 indexes
2. `mcf.metric_cert_writer_idempotency` present with 6 columns (`idempotency_key`, `action_code`, `result_json`, `status`, `created_at`, `updated_at`) + single-column PK on `idempotency_key` + 1 index on `(status, updated_at)`
3. `contract.framework_policy` has 1 row with `scope_code='mcf'` and `policy_uid='mcf_v1'`
4. `contract.operator_confirm_rule` has 2 rows with `scope='mcf'` and expected rule_uids
5. **`contract.operator_confirm_rule_action_chk` UNCHANGED** (regression check — M4 must NOT have altered this CHECK; the enforcement-action enum (`require_operator_confirm` / `route_to_operator_review` / `block`) is correctly typed; the M4 DBCP pre-rewrite mistakenly populated this column with cert action codes — see §10.5 semantic distinction). Verifier asserts the constraint definition still contains exactly the 3 enforcement actions and excludes any MCF cert action codes.
6. All M2 + M3 + M3-cert-amendment tables still empty (verifier doesn't write production rows; includes `mcf.certification_record` from the amendment + the two new M4-shipped tables)
7. M3 + cert-amendment trigger functions + triggers + sibling-cert FK still present (regression check — M4 must not have touched M3 substrate or the cert-amendment-shipped objects). Specifically: M3 trigger body still references `mcf.certification_record` (not reverted); `fk_mcs_cert` still targets `mcf.certification_record`; shared CHECKs still admit `'mcf'` / `'active_to_superseded'`.

**Behavioral (8–13) — synthetic-row integration tests:**
8. `McfCertWriterService.createMetricDraft` against synthetic input: creates parent + version + child + cert in single tx; rolls back; verifies state.
9. `submitForReview`: synthetic MCV at `'draft'` → state changes to `'review'` in tx; rolls back.
10. `approveForActivation` with `MockMcfHashComputer`: synthetic MCV at `'review'` → hashes populated on parent → PE rows inserted → state `'approved'`; rolls back.
11. `activateMetric` with valid operator + ≥40 char rationale: synthetic MCV at `'approved'` → cert inserted → state `'active'` → `is_current=TRUE`; rolls back.
12. `activateMetric` with rationale <40 chars: throws InvalidInputError before tx opens; nothing written.
13. `supersedeMetric`: two synthetic MCVs (one active predecessor, one active successor) → cert + supersession row + predecessor flip; rolls back.

**Cleanup (14):**
14. All M2 + M3 + M4 tables empty after verifier completes (test rows wrapped in tx + rolled back).

### 14.3 Unit-test plan

| Test | Scope |
|---|---|
| `createMetricDraft` validates input shape | Mock db; assert validation throws on bad input |
| `activateMetric` validates rationale length | Mock db; assert throws on <40 char rationale |
| Idempotency-key lookup returns cached result | Mock db + idempotency state; assert no tx opened |
| Idempotency-key reuse across different actions throws | Mock db; same key + different `action_code` → `IdempotencyKeyReuseError` (per §11.3) |
| Hash computer interface called once per `approveForActivation` | Mock hash computer; assert call count |
| Mock hash computer returns deterministic hashes | Assert `computeAllForApproval('uid-1')` === `computeAllForApproval('uid-1')` |
| Concurrency lock order in `supersedeMetric` | Assert lower-UUID locked first regardless of input order |
| **Production guard throws on mock hash in production** | Set `process.env.NODE_ENV = 'production'`; inject `MockMcfHashComputer`; assert `approveForActivation` throws `ConfigurationError` before any DB write (per §7.5) |
| **Production guard permits non-mock hash in production** | Set `process.env.NODE_ENV = 'production'`; inject hash computer returning `hashAlgorithmVersion = 'sha256-canonical-1.0'`; assert no throw |
| **Production guard permits mock hash in non-production** | Default env (test/dev); `MockMcfHashComputer`; assert no throw — mock is permitted outside production |
| `policyVersion` referencing archived `framework_policy` row rejected | Mock db with `effective_to < now()` on the policy row; assert service throws before tx opens |

### 14.4 Integration-test plan (uses live DB)

Synthetic MCV setup helper inserts a parent MC + MCV in `'draft'` state, then the test exercises one or more M4 methods, then ROLLBACK. The setup + tests + rollback are wrapped in a single tx.

| Integration test | Behavior |
|---|---|
| Full lifecycle: draft → review → approved → active | Each transition succeeds; PE results recorded; cert at activation; `is_current` discipline; demote prior active sibling correctly (exercises §8.4.3 M3 trigger dependency) |
| Reverse transition rejected | UPDATE state from `'active'` back to `'approved'` rejected by M3 trigger |
| Approve without hashes populated rejected | M3 trigger rejects `review → approved` if M4 service somehow bypassed hash UPDATE (synthetic test by directly UPDATEing state) |
| **In-tx race-correctness binding** | In an `approveForActivation` tx, attempt a concurrent INSERT on `mcf.metric_variable_binding` from a separate connection — assert it blocks until the approveForActivation tx commits (per §5.3 child-row locks) |
| Supersession with successor not active rejected | M3 trigger rejects |
| Supersession of same MC (same parent) rejected | Substrate CHECK `mcs_different_mc_chk` enforces |
| Idempotency retry returns same cert id | First `activateMetric` commits; second call with same key returns same `certificationRecordId` without new INSERT |
| **Stuck-pending idempotency converts to `rolled_back`** | INSERT a synthetic `pending` row with `updated_at = now() - interval '6 minutes'`; run cleanup script; assert row's `status = 'rolled_back'` with `result_json` carrying the timeout-reason note (per §11.6) |
| **`activateMetric` cert-before-PE-rows ordering** | After commit, assert all PE result rows have non-null `certification_record_id` referencing the cert (no row was ever in null state post-commit; verifies F-2 / P-2 ordering) |
| Override field passes through to cert | `override.gateCode + rationaleText + followupTaskUid` populated on cert row |
| **`policyVersion` archived-row rejection** | Integration: archive the active policy (set `effective_to = now() - interval '1 hour'`); attempt `activateMetric` with `policyVersion='1.0.0'`; assert service throws `InvalidInputError` before opening the tx; assert no cert row written |

### 14.5 No load testing in M4

Load characterization is deferred until M11+ panel substrate exists to generate realistic concurrent operations. M4's correctness is tested at synthetic-row granularity; performance is monitored via the tx-duration logger.

---

## 15. Risks and stop conditions

### 15.1 Design risks

| # | Risk | Severity | Mitigation in this DBCP |
|---:|---|---|---|
| R-1 | Hash computer is mock at M4 ship time; real activation blocked until M7/M8 | Medium | Acceptable per §7. M4 ships complete service contract + `MockMcfHashComputer` for tests. Real activation deferred until M7/M8 land — operator awareness. |
| R-2 | ~~Cross-framework cert coupling: BCF + MCF share `contract.certification_record`~~ | **RESOLVED by M3 cert-amendment** (per P-29) | Original risk anticipated column-shape gaps in the BCF-shared cert table. At M4 implementation pre-read, 10 live CHECK constraints rejected the cert-reuse design altogether (not just column gaps). Resolution: cert substrate correction preflight (`637e667`) + M3 cert-amendment DBCP (`06d369c`) + M3 cert-amendment applied (closeout `60efd9d`). MCF now writes to per-framework `mcf.certification_record` sibling; cross-framework coupling concern is no longer applicable. |
| R-3 | `operator_confirm_rule` schema is shared; MCF rules use `mcf_*` prefix + `scope='mcf'` to avoid collision | Low | Per D-18. |
| R-4 | Transaction lifetime: in-tx hash computation (§5.3) extends `approveForActivation` tx beyond other methods | Medium | Per-method tx lifetime budgets specified in §5.5 (`approveForActivation` slow-flag = 5 s). With `MockMcfHashComputer` <1 ms; with real M7/M8 hashers cost scales with binding/filter/dim-ref count. PE-result composition is still outside the tx (caller pre-assembles). Tx-duration logger flags >threshold per method. |
| R-5 | Idempotency-key retry race: two concurrent calls with same key | Low | INSERT-with-claim discipline (§11.3) serializes. |
| R-6 | M11 panel substrate (M5) doesn't exist; cert's `panel_run_uid` and PE result table's `panel_run_uid` are nullable + FK-less | Low | Per design. When M5 ships, future amendment adds FKs. |
| R-7 | Hash population sequencing in `approveForActivation` (UPDATE hashes + UPDATE state both in same tx; if hash UPDATE fails, state stays `'review'`) | Low | By design — atomic. |
| R-8 | Supersession concurrency: two ops trying to supersede the same predecessor | Medium | `SELECT FOR UPDATE` on predecessor at tx open. UNIQUE on `mcf.metric_supersession.predecessor_metric_contract_uid` further enforces. |
| R-9 | PE-MC eligibility result table shape coupled to M11 panel output | Medium | DBCP fixes the per-PE-MC-row shape (D-15). M11 DBCP must match. Cross-DBCP coordination flagged in §17. |
| R-10 | `metric_create` cert is service-contract-only; bug in M4 service could create MCs without certs | Medium (per M3 DBCP §8.3) | M4 service tests cover the cert-write step. Discipline only; no substrate gate. |
| R-11 | Operator emails are PII; cert column stores them | Low | Column already exists on Foundation Governance Substrate; nullable. M4 service does not add storage; just populates if caller provides. |
| R-12 | `policy_version` lookup race: framework_policy row deleted/superseded between service validation and tx commit | Very low | `framework_policy` rows are append-only (`effective_to` for archival, not DELETE). Future amendment may add tx-time lock if needed. |

### 15.2 New risks surfaced by this DBCP

| # | Risk | Mitigation |
|---|---|---|
| R-13 | Idempotency table grows unbounded | Nightly cleanup job (separate, not in M4) deletes `rolled_back` rows >30 days |
| R-14 | ~~The optional cert index (D-17) is added conditionally~~ | **RETIRED per P-23** (D-17 retired in cert-amendment rewrite) | MCF certs no longer write to `contract.certification_record`; the M3 cert-amendment already shipped `idx_mcf_cert_lookup` on the sibling for the trigger hot path. M4 ships no index on `contract.*`. |
| **R-15** | **M4 depends on M3 cert-amendment being applied.** If a future operator (or automation) attempts to apply M4 against a pre-amendment DB (sibling table absent; trigger still reading `contract.certification_record`; FK still targeting `contract.*`; shared CHECKs not extended), the M4 implementation cannot work correctly — cert writes would target a non-existent table, or service-level validation would fail, depending on which path is exercised first. | Medium (per P-29) | M4 dry-run script (§14.1 #2a / #2b / #2c / #3a / #3b / #3c) **REFUSES TO PROCEED** if any of the 6 amendment-state preconditions fail. Operator sees a clear `"M3 cert-amendment not applied; M4 dry-run refuses to proceed"` error and must apply the amendment first per `bc-docs-v3 60efd9d` apply closeout. No M4 service code can run against a pre-amendment DB. |

### 15.3 Stop conditions

The M4 implementation PR (next gate) STOPS and re-frames if any of these surface:

- DBCP review reveals an `operator_confirm_rule` schema mismatch that the M4 design cannot accommodate → revisit D-18 (prefix + scope tagging strategy)
- `framework_policy` already has an `mcf_v1` row from a prior process (unexpected state) → STOP, investigate, do not seed duplicate
- M3 state-transition trigger turns out to have a corner case the M4 service triggers (e.g. UPDATE OF clause excludes some scenarios) → revisit M3 trigger logic before M4 ships
- Hash interface specification turns out to need data from M4 service context (e.g. workbench fingerprint) → re-examine D-4 (hash population responsibility)
- PE-MC eligibility result shape needs columns not in the §4.2 spec (e.g. specific evidence shape requirements from M11 design that isn't done yet) → defer the table to M11 DBCP if shape can't be locked

---

## 16. Non-responsibilities (recap; firm)

M4 explicitly does **NOT** ship:

- Formula AST canonicalization, parsing, or any algorithm (M7).
- Package signature hash composition (M8).
- Self-verification fixture substrate (M9) or verifier engine (M10).
- Metric Authoring Panel substrate (M5) or execution (M11).
- Metric Publication Panel substrate or execution (M12).
- PE-MC-1..PE-MC-10 check logic — M4 stores results; M11 computes them.
- REST or MCP endpoint surface — M14 (publication endpoint) and M15 (supersession endpoint).
- bc-admin authoring UI (M12 UI gate).
- bc-portal integration.
- Tenant binding lifecycle / MLS 15-25 substrate (M6 + D392).
- Reservoir intake hygiene (M11).
- BCF writes (BCF arc).
- `bc-postgres` MCP write-access widening.
- Real hash algorithm implementation (M7/M8 ship; M4 declares interface only).
- Reorganization of legacy `contract.metric_contract*`, `metric.metric_binding`, `metric.metric_definition`, or any other legacy MC corpus.
- Cross-schema FK from `mcf.*` to legacy `metric.*` (the cross-schema FKs from `mcf.*` are: `mcf.metric_supersession.certification_record_id → mcf.certification_record` (intra-schema post-amendment); `mcf.certification_record.panel_run_uid → contract.panel_output_record` (cross-schema, shipped by amendment); both DDL-only per existing MCF discipline). M4 ships one new cross-schema FK: `mcf.metric_publication_eligibility_result.certification_record_id → mcf.certification_record` (intra-schema; same table M4 writes to).
- Runtime evaluation surface (`metric.metric_evaluation_run` etc.) — that's evaluation-boundary substrate, not authoring.

---

## 17. Operator approvals required before M4 implementation

Before the M4 implementation PR is opened, the operator approves:

| # | Approval item |
|---:|---|
| O-1 | Confirm all 20 decisions D-1 through D-20 (§3) — accept the DBCP recommendations or override |
| O-2 | Confirm M4 implementation sequencing: Option A single PR (recommended) vs Option B three sub-PRs (§13) |
| O-3 | Confirm the `mcf.metric_publication_eligibility_result` table schema (§4.2) — 10 columns + 2 CHECKs + 2 FKs + 3 indexes; per-PE-MC-row shape per D-15 |
| O-4 | Confirm `mcf.metric_cert_writer_idempotency` table (§11.4) — single-column PK on `idempotency_key`; `action_code` as non-key metadata; status enum (`pending`/`committed`/`rolled_back`); cleanup policy per §11.6 (committed retained indefinitely; rolled_back >30 days deleted; pending >5 min treated as stuck-orphan) |
| O-5 | Confirm `McfCertWriterService` method signatures (§6) — 5 public methods with input/output types |
| O-6 | Confirm `McfHashComputer` interface boundary (§7); `MockMcfHashComputer` ships with M4 for tests; production guard (§7.5) refuses `hashAlgorithmVersion` starting with `'mock-'` in `NODE_ENV='production'` |
| O-7 | Confirm `operator_confirm_rule` + `framework_policy` seed rows (§10) — 2 + 1 INSERT statements in apply gate |
| O-8 | Confirm transaction discipline (§5) — single tx; SELECT FOR UPDATE locks; in-tx hash computation for `approveForActivation` after locking MCV + parent MC + all child rows (per §5.3 race-correctness binding); UUID-ordered lock acquisition in supersession; per-method tx lifetime budget per §5.5 |
| O-9 | Confirm test plan (§14) — 14-check verifier; 10 unit tests (including production-guard variants); integration tests against synthetic rows + rollback discipline (including in-tx race-correctness, stuck-pending cleanup, cert-before-PE-rows ordering, archived-policy rejection) |
| O-10 | Confirm cert column population matrix (§9.1) for all 3 action codes |
| O-11 | Confirm schema boundary holds (§16) — no legacy MC migration, no panel substrate, no endpoint surface, no UI |
| O-12 | Approve the next gate: M4 implementation PR (DDL + Drizzle + service + tests + dry-run + post-apply verifier; NO DB APPLY) |
| O-13 | Confirm D-19 reversal acknowledgment + dry-run hard-gate stance: M4 cert writes target `mcf.certification_record` (sibling); M4 dry-run REFUSES to proceed if DB is pre-amendment (preconditions §14.1 #2a / #2b / #2c / #3a / #3b / #3c); M4 service code cannot be exercised against pre-amendment substrate. M4 depends on M3 cert-amendment being applied (R-15). |

The DBCP commit captures the design; the M4 implementation PR is the next operator-authorized session.

---

## 18. Recommended next gate

### 18.1 Recommendation: open M4 implementation PR (NO DB APPLY)

**Next gate: open the M4 implementation PR.** Deliverables (assuming Option A single-PR sequencing):

- `bc-core/docker/redesign/06-mcf-cert-authority.sql` — the DDL file (PE result table + idempotency table + operator_confirm_rule seeds + framework_policy seed; `BEGIN;...COMMIT;` wrapped per §12.6). **No `mcf.certification_record` CREATE TABLE (amendment shipped it); no shared CHECK ALTERs (amendment shipped them); no M3 trigger ALTER (amendment shipped it); no conditional cert-lookup index (D-17 RETIRED per P-23).**
- `bc-core/docker/redesign/06-mcf-cert-authority-rollback.sql` — companion rollback DDL per §12.5 (`BEGIN;...COMMIT;` wrapped; reverses only what M4 ships; M3-cert-amendment substrate stays applied)
- `bc-core/src/database/schema/mcf/metric-publication-eligibility-result.ts` — Drizzle schema
- `bc-core/src/database/schema/mcf/metric-cert-writer-idempotency.ts` — Drizzle schema
- `bc-core/src/database/schema/mcf/index.ts` — re-export additions
- `bc-core/src/registry/mcf/mcf-cert-writer.service.ts` — service implementation (5 public methods)
- `bc-core/src/registry/mcf/mcf-cert-writer.service.spec.ts` — Vitest unit tests
- `bc-core/src/registry/mcf/mcf-cert-writer.service.integration.spec.ts` — integration tests against synthetic mcv rows
- `bc-core/src/registry/mcf/mcf-hash-computer.interface.ts` — interface declaration
- `bc-core/src/registry/mcf/mcf-hash-computer.mock.ts` — mock implementation
- `bc-core/scripts/mcf-m4-dry-run.mjs` — 8-precondition dry-run per §14.1
- `bc-core/scripts/mcf-m4-post-apply-verification.mjs` — 14-check verifier per §14.2

PR title (suggested): `feat(mcf): M4 Lifecycle Certification / Transition Authority — DDL + Service + Verifier (NO DB APPLY)` (mirrors PR #103).

PR body should explicitly state:
- DDL hash captured
- 8 dry-run preconditions PASS expected
- 14 post-apply checks PASS expected
- Single PR option A chosen
- M4 substrate operationally dormant until M11+ panel ships (no production write path yet)
- Hash computer is `MockMcfHashComputer` for tests; real activation blocked until M7/M8

### 18.2 Subsequent gate: M4 DDL apply

After the implementation PR merges, a separate operator-authorized session applies the DDL to `bc_platform_dev` (mirroring the M2 + M3 apply gates from earlier this arc). Per CLAUDE.md Database Change Protocol.

The apply gate runs:
1. Pre-apply dry-run (`node scripts/mcf-m4-dry-run.mjs`) → expect exit 0
2. STOP for explicit operator approval
3. `psql ... -f docker/redesign/06-mcf-cert-authority.sql` → expect exit 0
4. Post-apply verifier (`node scripts/mcf-m4-post-apply-verification.mjs`) → expect exit 0, 14/14 PASS

### 18.3 Subsequent gate: evidence PR

Mirroring M2 PR #102 + M3 PR #104 pattern, an evidence PR ships the audit artifacts (`scripts/audit-output/mcf-m4-*`) to bc-core main, accompanied by `docs/implementation/mcf-m4-ddl-apply-closeout.md` on bc-docs-v3 main.

### 18.4 What stays closed

| | Status |
|---|---|
| M4 implementation PR | Operator authorizes next; not opened by this DBCP |
| M4 DDL apply | Pending implementation PR |
| M4 evidence PR | Pending apply |
| M5 (panel substrate) | Closed; depends on M4 |
| M6 (tenant binding) | Closed |
| M7 (formula AST), M8 (package signature) | Closed; M4 declares the interface they'll implement |
| M9 (fixture substrate), M10 (verifier engine) | Closed |
| M11 (authoring panel), M12 (publication panel) | Closed |
| M14 (publication endpoint), M15 (supersession endpoint) | Closed |
| MCF metric contracts | None authored; tables stay empty |
| Real hash computer (vs Mock) | Closed; M7/M8 |
| Legacy MC reorganization | NOT IN M4 SCOPE (§16) |
| Step-4-bis (Metrics 3 + 6) | Parallel workstream; not in this gate |
| `bc-postgres` MCP write access | Unchanged (`allow_write: false`) |
| `PGMCP_SCHEMAS` `mcf` addition | Deferred per M2 closeout |

---

## Document verification

- **All 18 required sections present** (§1 Scope and grounding [incl. §1.6 patch history with §1.6.1 cleanup batch + §1.6.2 cert-amendment rewrite]; §2 Current live M2 + M3 + cert-amendment state; §3 Decision log D-1 through D-20 [D-17 RETIRED per P-23; D-19 REVERSED per P-22]; §4 Certification authority model; §5 Transaction discipline [incl. §5.3 race-correctness binding]; §6 `McfCertWriterService` contract; §7 `McfHashComputer` interface boundary [incl. §7.5 production guard]; §8 Transition-specific design; §9 `mcf.certification_record` row contract; §10 Framework policy / operator confirm rule design [incl. §10.4 lifecycle pattern + §10.5 cert vs rule `action_code` semantic distinction]; §11 Concurrency and idempotency [incl. §11.6 cleanup policy]; §12 Error handling and rollback; §13 Implementation sequencing options; §14 Test and verification plan; §15 Risks and stop conditions; §16 Non-responsibilities; §17 Operator approvals required before implementation; §18 Recommended next gate).
- **All 20 preflight decisions resolved** in §3 with rationale (D-17 retired + D-19 reversed per cert-amendment rewrite; remaining 18 unchanged).
- **All 29 post-review patches applied** per §1.6:
  - **P-1..P-13** substantive design patches (race-correctness binding, cert-before-PE-rows ordering, production mock-hash guard, single-column idempotency PK, active-policy validation, scope-based rollback DELETE, D-17 mechanical check at the time, etc.) resolving F-1 through F-13 per §1.6.
  - **P-14..P-21** cleanup-batch clarity patches (NF1 6-fields-not-7 note, "1 new file + 4 updates" wording, exact-occurrence trigger validation, explicit DDL statement total, framework_policy lifecycle pattern, DDL apply order, COMMENT enumeration) per §1.6.1.
  - **P-22..P-29** cert-amendment rewrite patches (D-19 REVERSED, D-17 RETIRED, live state recap update, cert INSERT target change to `mcf.certification_record`, §9 reduced to 25-column sibling shape, §10 `action_code` semantic correction + new §10.5 distinction table, §14 dry-run hard-gates with REFUSES-TO-PROCEED semantics, §15 R-2 RESOLVED + R-14 RETIRED + R-15 added) per §1.6.2.
- **Complete column-level spec** for `mcf.metric_publication_eligibility_result` (§4.2) and `mcf.metric_cert_writer_idempotency` (§11.4; single-column PK).
- **Full TypeScript interfaces** for `McfCertWriterService` (5 methods) and `McfHashComputer` (1 method) (§6, §7).
- **Per-action cert column population matrix** (§9.1) — all **25 columns × 3 action codes** (sibling shape post-amendment; drops `governance_scope` + `target_registry_id` from BCF cert shape).
- **Transaction patterns** explicit for all 5 service methods (§8) — including in-tx hash compute + child-row locks for `approveForActivation` (§8.3), cert-before-PE-rows ordering for `activateMetric` (§8.4.2), UUID-ordered locking for `supersedeMetric` (§8.5).
- **Production guard** specified (§7.5) — `ConfigurationError` on mock hash algorithm in production.
- **Concurrency strategy** specified (§11) — `SELECT FOR UPDATE` + UUID-ordered locking for supersession + single-column-PK idempotency-key table + stuck-pending cleanup.
- **Framework policy lifecycle** specified (§10.4) — single active row per scope; amendments archive via `effective_to`.
- **Test plan** with 14-check verifier (§14.2) + 10 unit tests + integration tests against synthetic mcv rows (including production-guard, stuck-pending cleanup, cert-before-PE-rows ordering, archived-policy rejection).
- **Schema-boundary affirmation** (§16) — no legacy MC migration, no panel substrate, no endpoint surface.
- **Implementation sequencing decision** (§13) — Option A single PR recommended; revised estimate 2500–3500 lines; revisit threshold 4000 lines.
- **No code changes, no DDL applied, no MCF metric contracts created, no bc-core file edits, no certification rows written.** Doc-only patch commit to bc-docs-v3 main.
