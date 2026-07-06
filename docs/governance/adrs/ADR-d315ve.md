---
uid: DEC-d315ve
title: "D315 — Metric Evaluation Verification Framework"
description: "Two-layer verification: formula audit (start-of-line) + algebraic invariant gate (end-of-line) for metric computation correctness"
status: decided
date: 2026-04-14
project: bc-core
domain: metrics
refs:
  - type: decision
    uid: DEC-bebaec
    label: "D305 — Chain Completeness SSOT"
  - type: decision
    uid: ADR-c0290f
    label: "Metric Evaluation Engine — grain, formula, temporal gate"
migrated_from: legacy v2 archive
devhub_registration: doc-registry indexed; decision-registry row absent. UID short form `d315ve` does not match the allocator regex [0-9a-f]{6}, so this UID can never be registered under the current `devhub_decision_record` allocator. Classified UID_FORMAT_NON_CANONICAL + FILE_ONLY_UNEXPLAINED per Decision-Registration Integrity Audit 2026-06-22 §4.3. File-side authority preserved; no re-mint, no rename.
---

# D315 — Metric Evaluation Verification Framework

> **Decision-registration integrity (2026-06-22).** Classified `FILE_ONLY_UNEXPLAINED` + `UID_FORMAT_NON_CANONICAL` in the [integrity audit](../../evidence/audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md) §3.2 / §4.3 and preserved as a historical file-side exception in the [repair closeout](../../evidence/closeouts/implementation/devhub-decision-registration-integrity-repair-closeout-2026-06-22.md). The UID short form `d315ve` cannot be registered under the current allocator regex `[0-9a-f]{6}`. Inbound cross-references address this file by its non-canonical UID `DEC-d315ve`; preservation chosen over forced rename or successor minting per operator doctrine. Content below is preserved verbatim per Foundation Invariant III.

## Context

The Metric Evaluation Engine (`metric-evaluation-engine.service.ts`) is the terminal quality gate in BareCount. Every metric snapshot that reaches a dashboard, report, or action trigger passes through it. A wrong number here is not a bug — it is a platform integrity failure equivalent to a wrong bank balance.

**Audit findings (2026-04-14, Claude + Gemini independent review):**

- **0 of 29 tests** cover the formula parser (the actual production code path)
- `Number.isFinite()` not checked on any output — `Infinity` passes as valid
- `Number(null) === 0` and `Number('') === 0` — missing data silently becomes zero
- Bare variables implicitly SUM across payloads — engine guesses intent
- No rounding standard — IEEE 754 floating-point used for currency
- Temporal gate counts distinct periods but not continuity (12 copies of January passes "12 months required")
- No cross-metric conservation checks

**Root insight:** The platform currently has QA only at end-of-line (post-computation). It needs QA at start-of-line (formula audit) as well — two independent safety nets.

## Decision

Implement a two-layer verification framework with an optional third layer for on-demand deep verification.

### Layer 1: Formula Audit Table (Start-of-Line QA)

A static analysis pass that audits ALL metric formulas before any data flows. Runs once on platform boot, repeats when any MC formula changes.

**What it produces:** A cross-reference table of every metric contract's formula, parsed into normalized form, with consistency checks.

**Checks performed:**

| Check | Description | Example Finding |
|-------|-------------|-----------------|
| **Field existence** | Every `field_code` in formula resolves to a CF in `cc_field_mapping` | `open_item_amount` exists in CC, `bogus_field` does not |
| **Duplicate computation** | Two MCs computing the same formula on same CC → flag | `mc__total_ar` and `mc__ar_total` both = `SUM(open_item_amount)` |
| **Unit consistency** | SUM of amounts vs COUNT of identifiers → different units | Can't add `SUM(amount)` + `COUNT(invoices)` in a formula |
| **Conservation law derivation** | If MC-A = SUM(x) and MC-B = AVG(x), derive: MC-A == MC-B × COUNT | Auto-detected from formula structure |
| **Circular dependency** | MC-A references MC-B which references MC-A via upstream snapshots | Prevents infinite loops in secondary metrics |
| **Grain compatibility** | MC grain keys must exist in the CC's field set | Grain `company_code` must resolve via BF→CF mapping |
| **Temporal gate validity** | `required_periods` + `completeness_threshold` are sensible | `required_periods: 0` or `completeness_threshold: 0` = effectively disabled |
| **Aggregation coverage** | Every input variable must have explicit aggregation (no bare variables) | `Revenue - Cost` should be `SUM(Revenue) - SUM(Cost)` |

**Storage:** `contract.formula_audit` table — one row per MC, columns for each check (pass/warn/fail), refreshed on MC activation.

**Gate:** MC cannot transition to `active` status if any formula audit check is `fail`. Warnings are logged but don't block.

### Layer 2: Algebraic Invariant Gate (End-of-Line QA)

Post-computation verification predicates derived from the formula structure. Runs on EVERY metric evaluation. Cost: ~0.1ms per evaluation (negligible).

**Per-function invariants (always enforced):**

```
SUM(x):   MIN(x) × COUNT(x) ≤ result ≤ MAX(x) × COUNT(x)
AVG(x):   MIN(x) ≤ result ≤ MAX(x)
COUNT(x): 0 ≤ result ≤ total_input_count
MIN(x):   result ≤ all(x)
MAX(x):   result ≥ all(x)
A / B:    if sign(A) == sign(B), result > 0
Output:   Number.isFinite(result) == true
Output:   result !== null && result !== undefined
```

**Implementation:** After the engine computes a result, the verification gate runs the invariants. If any invariant fails:

1. The metric evaluation is marked `verification_failed` (new status)
2. The snapshot is NOT created
3. Evidence is recorded with the failing predicate
4. Boundary ticket is raised

**This is not re-computation.** The invariants are derived from the algebraic properties of the aggregation functions. They verify the shape of the result, not the exact value.

### Layer 3: Deep Verification Toolkit (On-Demand)

Triggered by auditors, agents, or scheduled verification runs. Not on the hot path.

**Capabilities:**

| Tool | What it does | When to use |
|------|-------------|-------------|
| **Determinism proof** | Re-evaluate same COs + same contract → compare bit-exact to stored snapshot | After engine code changes |
| **Metamorphic probe** | Add/remove one CO → verify result changes in predicted direction | Regression testing |
| **Cross-metric conservation** | For MCs sharing same CC: verify SUM/AVG/COUNT relationships hold | Periodic audit |
| **Temporal consistency** | For same MC across periods: verify monotonicity/balance constraints | Period-close audit |
| **Precision audit** | Re-compute SUM using Kahan summation → compare to IEEE 754 SUM | Currency metrics |
| **Lineage trace** | Given snapshot ID → trace back through CO → admitted → source | Incident investigation |

**Exposure:**
- MCP tool: `devhub_metric_verify` (for Claude sessions)
- API: `POST /api/metric-verification/run` (for bc-admin UI)
- Scheduled: nightly sample verification (random 10% of active MCs)

## Engine Hardening (Prerequisites)

Before the verification framework, the engine itself needs these fixes:

| Fix | Priority | Detail |
|-----|----------|--------|
| Output finiteness gate | P0 | `Number.isFinite()` on every computed value |
| Null/empty rejection | P0 | Explicit check before `Number()` coercion — null and `''` must not become 0 |
| Bare variable error | P0 | Error if `payloads.length > 1` without aggregation wrapper |
| Decimal arithmetic | P1 | `decimal.js` for currency-typed metrics |
| Rounding rule | P1 | `rounding` field in contract envelope (banker's/up/down/none + precision) |
| Temporal continuity | P1 | Check period gaps, not just distinct count |
| Currency awareness | P2 | Reject mixed currencies or require conversion spec |

## Options Considered

### Option A: Verification as separate service (rejected)

Run verification in a separate process after snapshots are created.

Rejected: Wrong results would exist in the database (even briefly). Downstream consumers might read them before verification catches up. The gate must be synchronous and pre-persist.

### Option B: Re-computation as verification (rejected)

Verify by computing the same formula twice and comparing.

Rejected: Same code, same bugs. If the engine has a precision error, re-computation produces the same wrong answer. Algebraic invariants are independent of the computation — they verify properties, not values.

### Option C: Two-layer algebraic verification (chosen)

Start-of-line formula audit + end-of-line invariant gate. Two independent safety nets using different verification principles.

Chosen: Catches errors at two different stages. Formula audit catches definition-time mistakes (wrong formula, missing fields). Invariant gate catches computation-time errors (overflow, precision, engine bugs). Neither requires re-computation.

## Consequences

### Positive

- **No wrong metric snapshot can be created** — invariant gate blocks bad results before persistence
- **Formula errors caught before data flows** — audit table surfaces inconsistencies at MC activation time
- **Cross-metric conservation laws auto-derived** — platform-level consistency without manual rules
- **Audit trail for verification** — every snapshot has a verification status
- **Engine bugs become detectable** — invariants catch bugs the engine's own tests miss

### Negative

- Every metric evaluation adds ~0.1ms for invariant checks (negligible vs. DB writes)
- Formula audit table adds a new platform table and activation gate
- `decimal.js` dependency for currency precision
- MCs with `verification_failed` will need investigation — creates operational work

### Risks

- **False positives:** Overly strict invariants could block valid edge cases (e.g., legitimately negative sums). Mitigation: invariants are derived from mathematical axioms, not business rules — false positives indicate real issues.
- **Scope creep:** The toolkit (Layer 3) could become an unbounded project. Mitigation: Layer 3 is explicitly on-demand and non-blocking. Ship Layers 1-2 first.

## Implementation Sequence

1. Engine hardening (P0 fixes) — prerequisite
2. Layer 2: Algebraic invariant gate — immediate, in the engine
3. Layer 1: Formula audit table — `contract.formula_audit`, MC activation gate
4. Layer 3: Toolkit — MCP tools, API endpoints, scheduled runs
5. Test suite: formula parser tests (currently 0) + invariant verification tests
