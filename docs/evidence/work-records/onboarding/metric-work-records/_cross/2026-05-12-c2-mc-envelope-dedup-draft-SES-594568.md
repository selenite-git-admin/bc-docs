---
metric: sda-c2-mc-envelope-deduplication
metric_version: n/a
tenant: platform
source_system: n/a
work_type: adr-draft
session_uid: SES-594568
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-a17d0f
  - DEC-d72560
  - DEC-ecec75
related_mwrs:
  - 2026-05-12-c1-bf-cf-compatibility-amendment-draft-SES-594568.md
  - 2026-05-12-pool1-trust-audit-46-producing-SES-594568.md
  - 2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md
related_change_records:
  - CHG-28ab0c
repair_location: B
affected_boundary: contract_authoring
foundation_gate: passed
---

# Lane C C2 — MC envelope deduplication policy — ADR draft

> **Filed as [DEC-889238](../../../../../governance/adrs/ADR-889238.md) (D405) on 2026-05-12.**

> **Draft only. Not filed as ADR yet.** A small, decision-only ADR establishing MC envelope governance as a peer authority to SDA, and codifying the deduplication rule. No code, no schema, no DBCP. After operator review, the substance is filed via `devhub_decision_record`.

## 0. Stance

The SDA umbrella ADR (DEC-a17d0f) governs **primitives** — BF / BO / CF / semantic_family. It does not govern **MC envelopes**. MC envelopes consume SDA-certified primitives but are themselves authored elsewhere, and the platform today has no authority that prevents two MCs with identical semantics from being registered separately.

The Apex Pool 1 trust audit surfaced three duplicate-MC pairs concretely:

| Pair | Subfunctions | Status |
|---|---|---|
| `mc__roa_return_on_assets` / `mc__return_on_assets_roa` | capital_structure_optimization / fixed_assets | Both producing, both UNTRUSTED in Pool 1, both carrying D335-R4 |
| `mc__net_working_capital_ratio` / `mc__working_capital_as_of_revenue` | treasury / treasury | Both 7-evaluated-accepted with snapshot-linkage gap |
| (Suspected) `mc__fixed_asset_turnover` / `mc__fixed_asset_turnover_ratio` | fpa / general_ledger | Suspected from naming; not yet confirmed via fingerprint |

The number of duplicates among the 376 platform MCs is unknown — no scan exists today. The pattern, however, is now-known: same formula + same input CF set, registered as two distinct MCs in different subfunctions.

This is **envelope-layer funnel-padding** — the analogue of cc_field_mapping G10 collision, one layer up. Each duplicate inflates apparent metric coverage without adding semantic value.

C2 establishes the authority and the rule. **It does not implement.**

## 1. Context

### 1.1 Why no authority owns this today

DEC-a17d0f governs primitives. DEC-ecec75 (D068 metric architecture) establishes that an MC is a computation contract over CFs, but does not codify uniqueness across MCs. The metric-seed-catalog playbook (`onboarding/metric-seed-catalog-management.md`) describes how MCs are seeded, but assumes the seeded names are distinct — no gate runs at seed time or at MC creation.

The result: an operator (or AI-assisted catalog import) can register two MCs that compute the same thing under different names, and the platform accepts both.

### 1.2 Why the SDA cannot absorb this

SDA G10 (Meaning-once) governs `cc_field_mapping` signatures. That gate fires at the BF→CF translation layer. MC envelope duplication is one layer **above** — at the MC→CF binding layer, after translation. Stretching G10 to cover MC envelopes would conflate two different authorities (primitive governance + envelope governance) and complicate the SDA's already-large scope.

Per the operator's execution-plan principle (*"do not reopen DEC-a17d0f"*), this is the right call. A peer authority is the cleaner shape.

### 1.3 Why this matters for trust

The Pool 1 audit's "46 producing MCs reduce to 1 HIGH + 3 LOW" result is partly driven by duplicate registration. The 14 MCs sharing the `cc__actual_ledger.actual_ledger_amount/sum` fingerprint are not all envelope-duplicates of each other (their formulas may differ), but **some adjacent pairs are**. Without a gate at MC creation, every per-cluster SDA Phase 1 adjudication risks producing two "winners" because each existed pre-deduplication. C2's gate, even shipped after the SDA work, would prevent this from recurring in future authoring.

## 2. Decision

### §1 — MC envelope governance is a peer authority to SDA

A new authority — **MC Envelope Governance** — is established. It is structurally a peer to SDA:

| Authority | Owns |
|---|---|
| SDA (DEC-a17d0f) | BF / BO / CF / semantic_family / certification / supersession / aliases / Meaning-once at cc_field_mapping |
| **MC Envelope Governance** (this ADR) | MC envelopes — uniqueness, lifecycle (future scope), structural integrity (formula↔variables↔grain consistency); deduplication; cross-domain scope (C3) |

The two authorities communicate via service-layer reads (MC envelope governance reads SDA's `certification-state` projection at write-time to verify referenced CFs are admissible; SDA does not call into MC envelope governance — no cycle).

For Phase 1, MC Envelope Governance ships **only** the deduplication gate from this ADR + the cross-domain scope gate from C3. The full lifecycle / state-machine for MC envelopes is **deferred** to a future ADR (analogous to SDA's six-state lifecycle, but for MCs). Today's MC envelope status fields (`activation_status` etc.) remain in place unchanged.

### §2 — Deduplication rule

Two MC envelopes are **duplicates** when **all** of the following hold:

1. **Same canonical formula text.** Defined as `formula_text` after the canonical-normalization function `normalize_formula()` (specified at implementation time; in this ADR it suffices that whitespace, operator-spacing, and variable-name case are normalized so semantically-identical formulas produce byte-identical canonical strings).
2. **Same set of input variable CFs.** The unordered set of `metric_contract_version.body.variables[].field_code` where `role = 'input'` matches.
3. **Same set of output variable CFs.** Same applied to `role = 'output'`.
4. **Same set of constant variable CFs.** Same applied to `role = 'constant'`.
5. **Same grain CF.** The CR-QG-MC-GRAIN grain anchor matches (or both are null if grain is implicit).
6. **Same temporal pattern.** If both have a temporal gate, the gate semantics match (rolling window, as-of-date, etc.). If one has a temporal gate and the other doesn't, they are **not duplicates** — different metrics.

**Not a duplicate:**

- Same formula text but different CFs: different metric (different semantics — same shape, different inputs).
- Same CFs but different formula: different metric (e.g. sum vs ratio of the same inputs).
- Same formula + CFs + grain but **different temporal pattern**: different metric (rolling-12-month vs as-of-period).
- Same formula + CFs + grain + temporal pattern but different `function_code` or `subfunction_code`: **duplicates.** Function/subfunction are **categorization metadata**, not semantic distinction. Apex's `mc__roa_return_on_assets` (capital_structure_optimization) and `mc__return_on_assets_roa` (fixed_assets) are duplicates regardless of subfunction.

### §3 — Where the dedup gate fires

| Gate point | Behaviour |
|---|---|
| **MC envelope create** | Run dedup check on the candidate MC's fingerprint. If any existing MC envelope matches per §2, reject with the matching MC's UID + name. **Block.** |
| **MC version activation** | Run dedup check again (in case other MCs were activated between create-time and activate-time). Same block behaviour. |
| **MC envelope deprecate / supersede** | No dedup check (downstream of survivor selection). |
| **Tenant binding** | No dedup check (binding is per-MC; dedup is per-envelope-vs-envelope, not per-tenant). |
| **Read-only projection** (retroactive surface) | `GET /api/metric-envelope/duplicates` — lists all existing duplicate fingerprints with their constituent MCs. **Read-only.** Operator-driven case-by-case adjudication; no auto-resolution. |

### §4 — Survivor selection

When a duplicate is detected (at write time or retroactively):

- **Default — older `created_at` wins.** First-registered MC is canonical; later MCs are non-survivors.
- **Operator override.** The operator may select the newer (or any non-default) MC as survivor with a rationale ≥40 chars. The override is recorded on the MC envelope governance audit ledger (future table; named here as `mc_envelope_audit_record` — analogous to SDA's `contract.certification_record` per DEC-a17d0f §7).

### §5 — Non-survivor handling

The non-survivor is marked **superseded** with a mandatory supersession link to the survivor. **`superseded` is terminal:**

- All existing `metric_binding` rows targeting the non-survivor remain operative (Foundation Invariant III: state is immutable; existing references are not retroactively broken).
- New `metric_binding` writes targeting the non-survivor are **rejected** (Phase 2 tenant-binding integration — see §7).
- Existing snapshots produced under the non-survivor are unaffected.
- The non-survivor's `field_code` (i.e. its MC name) becomes a **historical alias** on the survivor, queryable via the MC envelope read surface (future).

`withdrawn` is **not** the right state for non-survivors — `withdrawn` is for MCs that never reached production. Non-survivor MCs may have produced snapshots and have bindings; they need the `superseded` semantic to preserve historical references.

### §6 — Override path

Two override scenarios:

1. **At MC envelope create-time** — operator authors a new MC that the dedup gate identifies as a duplicate, but believes the new MC is materially different (e.g. the dedup heuristic missed a semantic distinction the operator can name). Override requires rationale ≥40 chars + an auto-spawned follow-up task tagged `mc-envelope-dedup-override`. The override is recorded; the new MC is created in `active` state alongside the existing one. **Both are then visible in the `/duplicates` projection** — accountable.
2. **At retroactive adjudication** — operator examines a duplicate pair in the projection and selects a non-default survivor. Override requires rationale ≥40 chars + follow-up task tagged `mc-envelope-dedup-survivor-override`.

Override accumulation is visible per-period to detect "the override mechanic is becoming the path of least resistance" — same governance discipline as SDA Phase 1 overrides (DEC-a17d0f §4.5).

### §7 — Where Phase 1 starts and what is deferred

**Phase 1 MC Envelope Governance scope (minimum):**

- `POST /api/metric-envelope/{mcId}/check-duplicates` — preflight gate; called by MC creation endpoint and MC version activation endpoint.
- `GET /api/metric-envelope/duplicates` — retroactive read projection.
- `POST /api/metric-envelope/{mcId}/supersede` — operator action: mark non-survivor superseded.
- `mc_envelope_audit_record` table — audit ledger for dedup decisions and overrides (named here; **DBCP authored later, not in this ADR**).

**Explicitly deferred to a future ADR:**

- Full MC envelope lifecycle (six-state, analogous to SDA primitives).
- Bulk retroactive sweep of existing duplicates.
- MC envelope alias management.
- Integration with `metric_binding` rejection (Phase 2).
- The `normalize_formula()` canonical specification (implementation-time decision).

This ADR establishes the **authority + the deduplication rule**. Everything else is downstream work.

## 3. Options Considered

**Option A — Continue without an authority.** Status quo. Rejected per §1.3 — duplicate registration is mathematically inevitable as the catalog grows, and the Apex audit already shows it occurring.

**Option B — Extend SDA to cover MC envelopes (chosen against).** Add MC envelope deduplication as another SDA gate. Rejected because (i) SDA's existing scope is already large; (ii) MC envelopes and SDA primitives are different governance surfaces with different lifecycles; (iii) per operator direction, "do not reopen DEC-a17d0f" — extending its scope is a reopen, even if the addition is small.

**Option C — Peer authority (chosen).** New MC Envelope Governance authority alongside SDA. Each owns a clean slice. Both can evolve independently (e.g. MC envelope state machine can be different shape from SDA's six-state lifecycle). This is the cleaner separation.

**Option D — Defer the authority and just author the dedup gate inline in the existing MC creation service.** Rejected because (i) the dedup rule has its own logic (formula normalization, set comparison, supersession), (ii) cross-domain scope from C3 lives in the same authority, (iii) future MC envelope lifecycle needs a home.

## 4. Consequences

### Positive

1. **Duplicate MC registration is prevented at write time** going forward.
2. **Existing duplicates are surfaced via projection**, not auto-resolved — operator retains judgment per pair.
3. **Supersession is foundationally correct** — bindings and historical snapshots are preserved.
4. **Subfunction stops masking duplicates** — the rule explicitly treats subfunction as categorization, not semantic distinction. This was a real gap in the Apex audit (3 observed pairs span different subfunctions).
5. **Authority separation keeps SDA scope tight** — DEC-a17d0f remains the primitive authority, not stretched to MCs.

### Negative

1. **New service surface to build** — MC Envelope Governance is a new module in bc-core. Justified by the recurring need (this and C3 both need it); not justified for a one-time concern.
2. **Existing duplicates require per-pair operator review** — there's no automation; each pair is a small adjudication. Acceptable; the count is bounded (likely <50 platform-wide).
3. **`normalize_formula()` correctness is implementation-critical** — if formulas normalize too aggressively, legitimate distinctions collapse into false duplicates; if not aggressively enough, real duplicates miss detection. Mitigation: ship conservative (under-detect) first; tighten with evidence.
4. **Subfunction-as-categorization-only** may surprise operators who use subfunction to express semantic distinction. Mitigation: documentation + override path covers cases where a real distinction exists despite identical fingerprints.

### Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `normalize_formula()` produces false duplicates | Medium | Medium | Conservative normalization first; tighten with override evidence; operator review per override |
| Operator override becomes the path of least resistance | Medium | Medium | D366-style ≥40-char rationale + auto-spawned follow-up task; aggregate override count visible in projection |
| Retroactive adjudication backlog grows | Medium | Low | Bounded population (likely <50 pairs platform-wide); operator-driven, not auto |
| Constants role variation creates false-distinct duplicates | Medium | Low | Constant CFs included in §2.4 set comparison; same constants → same fingerprint |

## 5. Decision boundary

**Decided here:**

- MC Envelope Governance is a peer authority to SDA.
- The deduplication rule (§2): same formula + same CF sets (input/output/constant) + same grain + same temporal pattern; function/subfunction not part of fingerprint.
- Gate fires at MC envelope create + MC version activate.
- Default survivor: older `created_at`; operator override available.
- Non-survivor: `superseded` (not `withdrawn`).
- Override mechanic: D366-style rationale + follow-up task.
- Phase 1 service scope (§7).

**Not decided here:**

- Full MC envelope lifecycle (six-state or otherwise).
- `normalize_formula()` exact specification (implementation-time).
- The schema of `mc_envelope_audit_record` (future DBCP).
- Bulk retroactive sweep policy (case-by-case is the default).
- Integration with `metric_binding` rejection at Phase 2.
- Cross-domain scope (C3 — separate ADR draft).

## 6. References

- **DEC-a17d0f** (D403) — SDA umbrella ADR. C2's peer authority sits alongside it.
- **DEC-d72560** (D301, superseded by DEC-a17d0f on lifecycle) — CF as 3rd primitive; the MC envelope consumes its CF outputs.
- **DEC-ecec75** (D068) — Metric architecture (one contract per KPI); the metric envelope shape this ADR governs.
- **Evidence MWRs:**
  - [Pool 1 trust audit](../../../../audits/onboarding/2026-05-12-pool1-trust-audit-46-producing-SES-594568.md) — 3 observed duplicate pairs.
  - [Apex Phase 0 readiness walkthrough](2026-05-12-apex-phase0-readiness-walkthrough-SES-594568.md) §A4 — MC envelope duplicates flagged as governance scope #2.
  - [C1 BF-CF compatibility amendment draft](2026-05-12-c1-bf-cf-compatibility-amendment-draft-SES-594568.md) — parallel Lane C decision.

## 7. Operator review checklist

- [ ] §1 — peer-authority shape (not SDA extension) accepted
- [ ] §2 — six-element duplicate fingerprint accepted (formula + input CFs + output CFs + constant CFs + grain + temporal)
- [ ] §2 — subfunction explicitly NOT part of fingerprint accepted
- [ ] §3 — gate fires at MC envelope create + version activate accepted
- [ ] §4 — older `created_at` as default survivor accepted
- [ ] §5 — `superseded` (not `withdrawn`) for non-survivor accepted
- [ ] §6 — D366-style override mechanic accepted
- [ ] §7 — Phase 1 scope (preflight + projection + supersede + audit ledger) accepted; broader lifecycle deferred
- [ ] Approved for filing as ADR: _yes / no_

## 8. After this draft is approved

If the operator decides to close Lane C and file all three ADRs (C1 amendment, C2, C3) before Phase 1 implementation:

1. File C1 as amendment to DEC-a17d0f via `devhub_decision_record` per the C1 §14 plan.
2. File **this ADR** (C2) as a new ADR via `devhub_decision_record`. Title: "MC Envelope Governance and Deduplication Policy". No `supersedes_ref`. Domain: `contracts`. Subdomain: `mc-envelope`. Focus: `governance`.
3. File C3 as a separate new ADR (the cross-domain scope policy) as the third sibling.

After filing, the three ADRs collectively close the Lane C governance scope gaps surfaced by the Apex audit. Phase 1 implementation work for both SDA and MC Envelope Governance authorities can then proceed against a stable governance baseline.
