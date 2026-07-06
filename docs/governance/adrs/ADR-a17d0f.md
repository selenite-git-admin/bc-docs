---
uid: DEC-a17d0f
title: "Semantic Definitions Authority for governed vocabulary primitives"
description: "Establishes the Semantic Definitions Authority (SDA) as the platform authority for BF / BO / CF identity, certification, provenance, supersession, aliases, and Meaning-once validation. Defines six lifecycle states, five naming profiles, deterministic gates G1–G10, AI as advisory evidence only, and phased integration with CC / MC / CM / OC authoring."
status: superseded
date: 2026-05-12T05:33:26.970Z
project: platform
domain: contracts
subdomain: semantic-vocabulary
focus: governance
supersedes:
  - DEC-5017fe
  - DEC-d72560
superseded_by: DEC-02f5a9
---

# Semantic Definitions Authority for governed vocabulary primitives

## Context

Reconciles three governing sources (DEC-69f09e D148, DEC-5017fe D139, DEC-d72560 D301) and business-vocabulary.md, which currently declare five different effective certification lifecycles across docs and code, with no standing enforcement layer. Evidence MWRs: docs/onboarding/metric-work-records/_cross/2026-05-12-semantic-base-audit-SES-a223ea.md (drift audit: 603/603 CFs draft, 122 non-snake_case, 144 funnel-padding candidates, 21 shell CCs), docs/onboarding/metric-work-records/_cross/2026-05-12-tier1-cf-certification-design-SES-a223ea.md (narrower Tier-1 design absorbed and extended), docs/onboarding/metric-work-records/_cross/2026-05-12-semantic-definitions-authority-design-SES-a223ea.md (the design this ADR summarises; revisions R1 through R3.1, Phase 0 read-only projection authorised and shipped on bc-core@cb4b972).

## Context

BareCount enforces contracts on customer data, but the platform's own vocabulary — Business Field (BF), Business Object (BO), Canonical Field (CF), semantic_family — is currently not governed by any standing authority. Three ADRs (DEC-69f09e D148 ISO 11179 naming, DEC-5017fe D139 Standard Field Registry, DEC-d72560 D301 CF as 3rd primitive) plus `operating-model/business-vocabulary.md` and the onboarding chapters each prescribe governance procedurally, but the implementations have silently drifted away from them.

The 2026-05-12 semantic-base audit (MWR SES-a223ea) found six concrete conflicts (C1–C6):

- **C1** — Five different effective certification lifecycles across the four governing sources and three service implementations.
- **C2** — Primitive name disagreement: "Business Field" in docs vs `StandardField*` in the bc-core controller.
- **C3** — CF uniqueness: declared and indexed (Drizzle `uq_canonical_field__name`, live `canonical_field_field_name_key`); strict single-column uniqueness verified in the live DB by Phase 0 diagnostic; exact-byte duplicate count zero; the audit's earlier "literal duplicates" finding was a misread of stem-grouping output (corrected in audit MWR §Pass 4 A4).
- **C4** — Naming standard for CFs: snake_case mandated by `canonical-field-seeding.md` but 122 non-snake_case CFs accepted by the implementation.
- **C5** — `semantic_family` closed enum (24 values from D366) named in a code comment only; no DB CHECK, no service path, all 603 CFs `NULL`.
- **C6** — Reference-time certification enforcement absent: BO approval checks "all BFs certified" but no path enforces CF certification at cc_field_mapping create, MC variable binding, MC version activate, or CM/OC authoring.

These are not isolated bugs. Without a standing enforcement layer, vocabulary drift accumulates faster than diagnostic passes can catch it. The Semantic Definitions Authority (SDA) is the standing fix.

## Decision

The Semantic Definitions Authority is established as the **single platform authority** for the canonical state of governed vocabulary primitives. The SDA owns identity, certification, provenance, supersession, aliasing, and Meaning-once validation; it enforces deterministic gates at every authoring path; it admits bc-ai as advisory evidence requiring human acknowledgement, never as a certifying or blocking authority; and it emits projection endpoints consumed by readiness, formula-audit, chain-status, and tenant-binding so those surfaces stop re-deriving semantics independently.

### §1 Authority boundary

The SDA **owns** the canonical state for: Business Field, Business Object, Canonical Field, Semantic Family, Definitions, Provenance, Aliases, Certification Records, and the Meaning-once invariant on `cc_field_mapping`.

The SDA **does not own**: tenant data, runtime values, reader execution, MC evaluation results, source catalog, CC envelope authoring (consumes SDA-certified references), MC envelope authoring (consumes), or tenant binding decisions.

The SDA **emits** state that consumers read. It does **not** mutate runtime, tenant, or evaluation tables. Foundation Invariants I (Meaning is evaluated once) and III (All state is immutable) are upheld.

### §2 Unified six-state certification lifecycle

`business-vocabulary.md` is adopted as authoritative for the lifecycle, extended by one state — `deprecated` — to cover "no longer recommended, but still queryable, not yet superseded". The unified lifecycle is **exactly six states**:

```
proposed → reviewing → certified → deprecated → superseded   (terminal; supersession link required)
              │                                  │
              ▼                                  ▼
        withdrawn (terminal; pre-cert reject)    is_archived = true
```

States:
- `proposed` — registered with provenance; not yet reviewed (replaces ad-hoc `draft`).
- `reviewing` — under gate evaluation.
- `certified` — admissible to contract authoring.
- `deprecated` — discouraged from new authoring; still resolves for existing references.
- `superseded` — replaced by another primitive; supersession link mandatory; terminal.
- `withdrawn` — pre-certification rejection; terminal.

`is_archived` is a **separate boolean visibility flag**, not a seventh state. Settable only when state ∈ {`superseded`, `withdrawn`}; hides the row from default listings while remaining queryable via `?includeArchived=true`. `certification_state_code` and `is_archived` are independent dimensions.

Permitted transitions, immutable-after-certification fields, alias / supersession behaviour, and backward compatibility for existing references are governed per the design MWR §4. The non-survivor's `field_name` becomes a historical alias on the survivor. Supersession is non-retroactive (Foundation Invariant III).

### §3 Five naming profiles (replaces single-rule reading of DEC-69f09e)

The SDA recognises that different vocabulary surfaces carry different naming constraints. **Five profiles**, each with its own rule set:

- **P1 — Technical DB / API / JSON naming.** snake_case, representation-term suffix. Authority: DEC-69f09e literal.
- **P2 — Business Field name profile.** snake_case, BO-scoped prefix mandatory unless one of the five shared dimensions; `{bo_prefix}_{property}` form; ISO 11179 decomposition required. Authority: DEC-f66378 (D292/D294) + DEC-5017fe + business-vocabulary.md.
- **P3 — Canonical Field name profile.** snake_case, **NOT** BO-scoped, formula-variable-shaped (`total_revenue`, `accounts_receivable_balance`). Authority: DEC-d72560 + canonical-field-seeding.md.
- **P4 — Metric formula variable profile.** Variable `field_code` in `metric_contract_version.body.variables[].field_code` equals the CF `field_name` (P3). One profile, two surfaces. Authority: DEC-d72560.
- **P5 — Semantic family code profile.** **Hyphenated identifier** (kebab-style for compound terms), closed enum from D366; regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`. Authority: DEC-804874 (D366) §3.

The SDA's name-validation gate dispatches to the right profile based on primitive type. One regex does not fit all five profiles.

### §4 Deterministic gates G1–G10

Gates are deterministic pass/fail checks evaluated during `proposed → reviewing → certified` transitions (G1–G8) and at reference-authoring time (G9, G10). They are the **only blocking authority**.

- **G1** — Naming profile compliance (P1–P5 dispatch). Overridable.
- **G2a** — Exact-identity uniqueness (byte-identical name). **Non-overridable.** DB UNIQUE index is the structural backstop; G2a returns a clean diagnostic before the DB constraint fires.
- **G2b** — Normalized-form collision (`normalize = lowercase + trim + replace(non-alphanumeric, '_')`). Overridable with rationale + human acknowledgement.
- **G3** — Definition presence and quality (non-null, ≥ 1 sentence, no banned placeholder strings). Overridable.
- **G4** — Provenance presence (`source_standard ∈ {oagis, iso_20022, xbrl_gaap, ifrs, uncefact, bc_standard, computed}`; `standard_ref` non-null when external). Overridable.
- **G5** — `semantic_family` populated and in master enum (CF only). **Non-overridable.**
- **G6** — Data type / unit compatibility per semantic_family compatibility matrix. **Non-overridable.**
- **G7** — BO-scoped naming (BF only); five shared dimensions exempt. **Non-overridable.**
- **G8** — Anti-BO-prefix (CF only); five shared dimensions exempt. **Non-overridable.**
- **G9** — Candidate reference admissibility (runs at the moment a *new or modified* reference is authored; does not scan existing references at certification time). Per-authoring-path allowed-state set: cc_field_mapping create/replace requires `certified`; MC variable binding new requires `certified`; MC variable binding version-bump permits `deprecated` with warning; CM field_resolutions and OC field_selection require `certified` BF. `proposed`/`reviewing`/`withdrawn`/`superseded` are **never** permitted target states for new authoring. Compat-mode-controlled per integration (Q7 shadow/block flags).
- **G10** — Meaning-once validation on cc_field_mapping authoring (Foundation Invariant I). Signature = `sha256(canonical_json({cc_id, bf_id, rule, filter_canonical, compute_canonical}))` with sorted keys and normalised primitives so semantically-identical bodies produce byte-identical signatures. `replace` flow excludes the row being replaced. Three collision classes:
  - **Class-A — Certified-blocking.** Another `certified` CF resolves through this signature. Sev-1, **non-overridable**.
  - **Class-B — Proposed/reviewing-review.** Another non-certified candidate aims at this signature. Sev-2, overridable with rationale + cross-reference both candidates.
  - **Class-C — Deprecated/superseded/withdrawn.** Informational only; not blocking.

**Hard-law (non-overridable) gates:** G2a, G5, G6, G7, G8, G10 Class-A. These six form the SDA's non-negotiable structural floor.

Overridable gates accept a D366-style override mechanic (rationale ≥ 40 chars + auto-spawned follow-up task tagged `sda-override`). Every override is recorded on the certification record. AI advisory verdicts are **not gates** and never autonomously block; non-green AI verdicts require explicit human acknowledgement, but the acknowledgement is the lock, not the AI verdict.

Gates run G1 → G10 in order; the first fail short-circuits. The full verdict block is persisted as the certification record's `gateResults`.

### §5 bc-ai as advisory evidence only

The SDA admits bc-ai as **advisory evidence requiring human acknowledgement, never as autonomous authority**. AI verdicts never transition state, never block, never certify; they are inputs to the certification record. The deterministic gates (§4) remain the only blocking authority.

- **green** — recorded as supporting evidence; no human acknowledgement required.
- **amber** — recorded as caveat; human acknowledgement required before `reviewing → certified`.
- **red** — recorded as challenge; certifier must explicitly acknowledge with rationale (≥ 40 chars) to proceed, but the AI does not block. If any deterministic gate fails, certification is blocked regardless of the AI acknowledgement.
- **unverified** (AI unreachable / async not returned / confidence below threshold) — explicit unverified acknowledgement (≥ 40 chars rationale) recorded; certification may proceed.

bc-ai is **async by default** (Q8). Submission to `reviewing` enqueues advisory work; verdicts land on the projection surface as they return. There is no operator-configurable knob that promotes AI to a gate.

Every AI verdict is persisted on `certification_record.advisory_verdicts[]` with `{surface, verdict, confidence, rationale, model_id, prompt_hash, timestamp, acknowledgement}`.

### §6 Service surface

The SDA is a single bc-core controller area at **`/api/semantic-definitions/*`** (internal module name `sda`). Read endpoints (`GET /{cf|bf|bo}`, `/:id`, `/:id/certification-record`, `/:id/references`, `/:id/aliases`, `/:id/provenance`, `/semantic-families`), projection endpoints (`/projection/certification-state`, `/projection/meaning-once-violations`, `/projection/stale-references`), state-mutating endpoints per certification act (`/submit-for-review`, `/certify`, `/return-to-author`, `/withdraw`, `/deprecate`, `/supersede`, `/archive`, `/unarchive`), preflight endpoints (`/preflight/cc-field-mapping`, `/preflight/mc-variable-binding`, `/preflight/cm-field-resolution`, `/preflight/oc-field-selection`), and compat-mode controls (`/migration/compat-mode`). Full endpoint list in design MWR §7.

Preflight endpoints are **non-mutating** — they do not record certification acts. The CC/MC/CM/OC onboarding service is the one that records bindings; preflight is a callable check the onboarding service runs first.

### §7 Storage model

The SDA mostly uses existing tables. Minimal additions are noted per Q2/Q3/Q4/Q5 settled decisions; each requires a DBCP authored as part of Phase 1 / Phase 3.

Existing tables used as-is or with minor CHECK-constraint broadening: `contract.canonical_field`, `contract.business_field`, `contract.business_object`, `contract.business_field_alias`, `contract.cc_field_mapping`, `master.unit_type`.

New tables (each requires DBCP):
- `master.semantic_family` — closed enum from D366 + per-family compatibility metadata (Phase 1 DBCP-1a).
- `contract.certification_record` — per-primitive audit ledger: gate results, AI verdicts, acknowledgements, certifier Cognito `sub` + role-at-action-time per Q6, timestamp, override rationale + follow-up task uid per Q9 (Phase 1 DBCP-1c).
- `contract.primitive_supersession` — central `{primitive_type, predecessor_id, successor_id, superseded_at, superseded_by_sub, rationale}` per Q3 (Phase 1 DBCP-1e).
- `contract.primitive_provenance` — central append-only `{primitive_type, primitive_id, source_standard, standard_ref, registered_at, registered_by_sub}` per Q4; existing per-primitive `source_standard` / `standard_ref` columns retained as current-projection convenience (Phase 1 DBCP-1f).
- `contract.vocabulary_name_alias` — historical / supersession aliases across BF / BO / CF per Q2; separate from existing `contract.business_field_alias` which keeps its source-system-alias role (Phase 3 DBCP-3a).

Status-enum broadening + `is_archived` flag on the three primitive tables: Phase 1 DBCP-1b. Bulk `draft → proposed` status migration: Phase 1 DBCP-1d (governed write, transactional per table, reversible via paired reverse DBCP).

**This ADR does not author DBCPs.** The shapes above are decision-locked for Phase 1 / Phase 3 implementation.

### §8 Integration points

Every authoring path calls the SDA before mutating state. Integration points (call site → SDA endpoint): CF / BF / BO register and certify (existing controllers delegate to SDA), `cc-onboarding.service.ts::addMappings` / `::replaceMapping` (SDA preflight G9 + G10), `mc-onboarding.service.ts` + MC version activate (preflight G9), `mapping-binding.service.ts` (preflight G9 on BFs), `oc-onboarding.service.ts` (preflight G9 on BFs), `metric-readiness.service.ts::bind` (rejects non-certified bind candidates), `formula-audit.service.ts` (reads SDA projection instead of re-deriving), `chain-status.service.ts` (reads SDA projection for L1/L2/L3/L7).

Each integration is a one-line `await` to the SDA. The SDA does not call back into onboarding services — no cycles.

### §9 Phased implementation plan

**Phase 0 — Read-only authority projection.** Strictly read-only projections over the existing contract registry. No DDL, no DBCP, no status migration, no enforcement, no preflight gates, no bc-ai. Ships the `/api/semantic-definitions/*` read surface and the projections (certification-state, meaning-once-candidates, stale-cc-field-mapping-references, duplicate-name-clusters, profile-violations, unique-index-state diagnostic). **Status: complete on bc-core@cb4b972 (SES-4a7efb closed 2026-05-12 PM).**

**Phase 1 — CF certification + preflight service (shadow mode).** First phase with governed write paths. DBCPs 1a–1f authored at phase start. Implements gates G1–G8, AI advisory endpoints (async by default per Q8), state-transition endpoints, bulk `draft → proposed` migration. No enforcement at reference paths yet.

**Phase 2 — Onboarding integration gates (block mode opt-in).** CC / MC / CM / OC onboarding paths call SDA preflight. Per-integration shadow/block flag with operator-visible counters of "shadow rejections that would have blocked" per Q7. Operator flips each integration to block when the counter is low.

**Phase 3 — Aliases, supersession, deprecation.** Full lifecycle including supersession with operator-driven reference migration. DBCP-3a introduces `contract.vocabulary_name_alias`.

**Phase 4 — Cleanup workflow for existing drift.** Audit findings flow through the SDA into a cleanup queue: G2b normalized-form clusters (172 stem-clusters / 403 CFs), 122 non-snake_case CFs, NULL `semantic_family` (all 603 CFs), 144 R4 funnel-padding candidates. 21 shell-CC clusters remain operator-level ADR work (out of SDA scope).

## Supersession

This ADR **supersedes** the following ADRs on lifecycle, certification, and naming-profile topics:

- **DEC-5017fe (D139)** — Standard Field Registry: ISO 11179 MDR alignment. The two-tier model (platform fields + tenant `z_` extension fields) and the ISO 11179 grammar (object_class / property / representation_term) remain in force as the BF profile (§3 P2). The lifecycle declared in DEC-5017fe (`draft → registered → deprecated → retired`) is **superseded** by the unified six-state lifecycle (§2). The naming "Standard Field" is **superseded** by "Business Field" for the primitive; "Standard Field Registry" remains the canonical term for the governance facility that registers BFs.

- **DEC-d72560 (D301)** — Canonical Field as 3rd Contract Primitive. The two-vocabulary model (BF source-side vs CF metric-side, CC as translator) and the `contract.canonical_field` + `cc_field_mapping` schema remain in force. The lifecycle implied by DEC-d72560 (single `draft` state, no transitions) is **superseded** by the unified six-state lifecycle (§2). The CF certification check named in DEC-d72560 §Risks ("MC validation gate checks CF status") is now implemented by the SDA preflight gate G9 (§4) and the `metric-readiness.service.ts::bind` integration (§8).

## Amends DEC-69f09e

This ADR **amends** DEC-69f09e (D148 ISO 11179 Technical Naming Standard) by clarifying the profile scope of the snake_case rule. DEC-69f09e prescribes snake_case for DB columns, JSON keys, and API field names — that scope remains in force as SDA Profile P1 (§3).

The amendment: vocabulary surfaces that DEC-69f09e leaves out of scope ("foundation business vocabulary", "external system identifiers") are now governed by four further profiles (P2 BF, P3 CF, P4 MC variable, P5 semantic_family) that the SDA dispatches to based on primitive type. P5 in particular carries hyphenated kebab-style enum values (`measure-currency`, `dim-calendar-date`, …) as a value-content convention specific to the D366 closed enum — this is a documented divergence from DEC-69f09e's snake_case rule, scoped narrowly to the semantic_family enum and not generalised to other value enums. The choice avoids invalidating the existing D366 reference set while keeping the divergence explicit and governed.

DEC-69f09e's authority over its in-scope surfaces (DB columns, JSON keys, API field names) is unchanged.

## Options Considered

**Option A — Continue with current per-service governance.** Each registry service (`canonical-field.service.ts`, `standard-field.service.ts`, `business-object.service.ts`) maintains its own lifecycle and gate set; CC/MC/CM/OC onboarding services each re-derive certification semantics from raw rows. Rejected: the 2026-05-12 audit found five different effective lifecycles, no enforcement of CF certification at reference time, and 603/603 CFs in `draft`. Drift is mathematically inevitable without a standing authority.

**Option B — Single Semantic Definitions Authority (chosen).** One service surface owns identity, certification, supersession, aliasing, provenance, and the Meaning-once invariant. Every authoring path calls the SDA before mutating. AI is advisory only. Phased rollout: read-only projections → certification flow → reference-time enforcement → supersession → cleanup.

**Option C — Per-vocabulary authority services (BF Authority, CF Authority, BO Authority).** Three services with parallel lifecycles. Rejected: the audit's drift was largely cross-vocabulary (CF references uncertified BFs, BO approval gate enforces BF but not CF). A single authority for the cross-cutting invariants (G9 reference-time, G10 Meaning-once, supersession across primitive types) is structurally cleaner.

**Option D — bc-ai as certifying authority.** AI-driven certification with operator override. Rejected: Foundation requires deterministic, replay-bounded evaluation (Invariant I + V). An AI verdict is not deterministic and not auditable as a structural law. bc-ai is admitted as advisory evidence only (§5).

## Consequences

### Positive

1. **One lifecycle, one place to look.** Six states across BF / BO / CF. The conflict between DEC-5017fe (four states), DEC-d72560 (one state), business-vocabulary.md (five states), and the implementations (binary / single / three-state CHECK) is resolved.
2. **Reference-time enforcement.** CC / MC / CM / OC authoring paths reject non-certified targets via SDA preflight. The 603 uncertified-CF backlog is contained by stopping new authoring against `proposed` rows; existing references are grandfathered via shadow mode.
3. **Meaning-once invariant operationalised.** G10 with canonical-JSON signatures and three collision classes makes Foundation Invariant I a write-time check on cc_field_mapping authoring.
4. **AI verdicts are auditable inputs, never silent authority.** Every AI advisory call is persisted with model_id + prompt_hash + acknowledgement; the certifier's response is the lock.
5. **Consumer surfaces stop re-deriving semantics.** Readiness, chain-status, formula-audit, tenant-binding read SDA projections instead of independently parsing registry rows.
6. **Override audit trail.** D366-style override mechanic (rationale + auto-spawned follow-up task) on overridable gates makes overrides visible and accountable; non-overridable gates have no override path.

### Negative

1. **New service surface to maintain.** SDA controller / service / repository / gates / projection / preflight / compat-mode modules add code surface area. Justified by the audit's drift evidence; the alternative is continued drift.
2. **Phase 1 schema changes touch every primitive table.** Status-enum CHECK broadening and `is_archived` column added to three tables; bulk `draft → proposed` migration touches all existing rows. Each change is a governed DBCP (1a–1f).
3. **Onboarding paths gain a synchronous preflight call.** CC / MC / CM / OC authoring becomes one network hop longer in Phase 2. Performance is non-load-bearing for authoring (low-frequency operator action), but the integration is now coupled.
4. **bc-ai is on the critical path of certification UX** even though it does not block. An unavailable bc-ai produces `unverified` verdicts requiring explicit acknowledgement; this is operational friction that the operator absorbs.
5. **Existing 603 CFs / 373 BFs cannot all be certified in any reasonable time.** Phase 4 is open-ended; the platform operates with most primitives at `proposed` for a long time. Acceptable: new authoring forces certification, existing authoring is grandfathered through compat mode.

### Risks

R-1 through R-10 in design MWR §12 carry forward into implementation. Key risks: shadow mode normalising non-compliance (mitigated by per-integration counters), AI becoming load-bearing (mitigated by structural rule that bc-ai is never gate-blocking by config or otherwise), and operator override eroding the gate (mitigated by ≥40-char rationale + auto-spawned follow-up task with `sda-override` tag, with aggregate override counts visible on the projection surface).

## Implementation status

- **Phase 0 — complete.** bc-core@cb4b972 (`feat(sda): Phase 0 read-only Semantic Definitions Authority projection`), session SES-4a7efb, 2026-05-12 PM. Phase 0 diagnostic verified strict single-column uniqueness on `contract.canonical_field(field_name)` via the live index `canonical_field_field_name_key` (PostgreSQL auto-generated; Drizzle-declared name `uq_canonical_field__name` is name drift only). Exact-byte duplicate count: zero. The audit MWR §Pass 4 was corrected in lockstep (A4 added).
- **Phase 1 onward — pending.** DBCPs 1a–1f, gates G1–G8 implementation, AI advisory endpoints, state-transition endpoints, bulk `draft → proposed` migration. Each DBCP requires explicit operator approval before execution. No Phase 1 work begins until this ADR is filed and the DBCP sequence is authored and approved.

## Decision boundary

This ADR **decides**:
- The SDA is the platform authority for BF / BO / CF / semantic_family identity, certification, provenance, supersession, aliases, and Meaning-once validation.
- The unified six-state lifecycle (§2).
- The five naming profiles (§3).
- Deterministic gates G1–G10 and the override matrix (§4).
- bc-ai is advisory evidence requiring human acknowledgement, never autonomous authority (§5).
- The service surface at `/api/semantic-definitions/*` (§6).
- The storage model (§7) including new tables, status-enum broadening, and `is_archived` flag.
- The integration call-site list (§8).
- The phased rollout plan (§9).
- Supersession of DEC-5017fe and DEC-d72560 on lifecycle / certification / naming-profile topics; amendment of DEC-69f09e on profile scoping.

This ADR **does not decide**:
- Per-DBCP DDL (DBCPs are authored separately, each operator-approved).
- Per-primitive certification acts (those are operator actions through the SDA's certify path in Phase 1).
- Survivor selection for any duplicate / near-duplicate cluster (Phase 4 work, per-cluster governing-source review).
- Compat-mode rollout schedule (Phase 2 controls left to operator per-integration).
- The bc-ai prompt set or model selection (Phase 1 implementation choice).
- The bc-admin UI for certification queue (Phase 1–3 implementation; no UI decision here).

## References

- **Design MWR:** [2026-05-12-semantic-definitions-authority-design-SES-a223ea.md](../../evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-semantic-definitions-authority-design-SES-a223ea.md) — full design body, R1 → R3.1 revision history, §C1–C6 conflict resolutions, §10 settled Q1–Q10 operator decisions, §11 phased plan, §12 risk register, §14 file-touch list.
- **Audit MWR:** [2026-05-12-semantic-base-audit-SES-a223ea.md](../../evidence/audits/onboarding/2026-05-12-semantic-base-audit-SES-a223ea.md) — drift evidence: 603 draft CFs, 122 non-snake_case, 144 R4 funnel-padding candidates, 21 shell CCs; §Pass 4 A4 correction on CF uniqueness.
- **Tier-1 design MWR:** [2026-05-12-tier1-cf-certification-design-SES-a223ea.md](../../evidence/work-records/onboarding/metric-work-records/_cross/2026-05-12-tier1-cf-certification-design-SES-a223ea.md) — earlier narrower design absorbed and extended by §3 (Profile P3), §2 (lifecycle), §10 (settled decisions), §9 Phase 4 (cleanup).
- **Superseded:** [DEC-5017fe](ADR-5017fe.md) (D139 Standard Field Registry), [DEC-d72560](ADR-d72560.md) (D301 Canonical Field as 3rd Contract Primitive).
- **Amended:** [DEC-69f09e](ADR-69f09e.md) (D148 ISO 11179 Technical Naming Standard) — profile scoping clarified in §3.
- **Related:** [DEC-f66378](ADR-f66378.md) (D292/D294 BO-Scoped BF naming + five shared dimensions), [DEC-aa6251](ADR-aa6251.md) (D255 BO and BF as Contract Primitives), [DEC-616e02](ADR-616e02.md) (D103 Business Object Model), [DEC-804874](ADR-804874.md) (D366 L-Node Semantic Gate — semantic_family enum origin, override pattern), [DEC-ebf0b4](ADR-ebf0b4.md) (D268 Session Discipline), [DEC-9d1f4b](ADR-9d1f4b.md) (D327 Shared dimension normalization), [DEC-b5631b](ADR-b5631b.md) (Field Data Type Quality Gate), [DEC-9a5dc0](ADR-9a5dc0.md) (CF Boundary rule), [DEC-339c97](ADR-339c97.md) (External standards provenance).
- **Foundation:** [the-invariants.md](../../foundation/the-invariants.md) (I — Meaning is evaluated once; III — All state is immutable; V — Evaluation is non-replayable), [the-evaluation-boundaries.md](../../foundation/the-evaluation-boundaries.md), [the-contract-grammar.md](../../foundation/the-contract-grammar.md).
- **Operating model:** [business-vocabulary.md](../../operating-model/business-vocabulary.md) (authoritative source for the lifecycle adopted in §2).
- **Onboarding chapters:** [canonical-field-seeding.md](../../onboarding/canonical-field-seeding.md), [business-field-and-business-object-onboarding.md](../../onboarding/business-field-and-business-object-onboarding.md), [source-and-admission-contract-creation.md](../../onboarding/source-and-admission-contract-creation.md), [canonical-contract-creation.md](../../onboarding/canonical-contract-creation.md), [metric-contract-creation.md](../../archive/onboarding/metric-contract-creation.md), [observation-contract-creation.md](../../onboarding/observation-contract-creation.md).
- **Phase 0 implementation:** bc-core@cb4b972 — `feat(sda): Phase 0 read-only Semantic Definitions Authority projection`. Session SES-4a7efb (closed). Phase 0 verified §C3 uniqueness state and tightened the unique-index diagnostic to distinguish strict single-column from composite indexes including `field_name`.

## Amendments

- [DEC-b7affa](ADR-b7affa.md) (D404, 2026-05-12) — Adds gate G11 (BF-CF semantic-family compatibility) to §4. Extends G5 to BFs. Names DBCP-1g for the future `business_field.semantic_family` column. Defers G11b code-vocabulary sub-gate. Does not change frontmatter status (per D370 hygiene policy: no amendment-pair rule).
