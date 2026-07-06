---
metric: platform-wide-semantic-definitions-authority
metric_version: n/a
tenant: platform
source_system: n/a
work_type: grammar-extension
session_uid: SES-a223ea
date: 2026-05-12
status: decision-pending
related_commits: []
related_tasks: []
related_adrs:
  - DEC-69f09e   # D148 — ISO 11179 Technical Naming Standard
  - DEC-5017fe   # D139 — Standard Field Registry (ISO 11179 MDR for observation vocabulary)
  - DEC-d72560   # D301 — Canonical Field as 3rd Contract Primitive
  - DEC-f66378   # D292 — BO-Scoped BF naming + D294 five shared dimensions
  - DEC-9a5dc0   # CF Boundary rule (provenance for CFs)
  - DEC-339c97   # External standards provenance
  - DEC-b5631b   # Field Data Type Quality Gate
  - DEC-aa6251   # D255 — BO and BF as Contract Primitives
  - DEC-616e02   # D103 — Business Object Model
  - DEC-683cf3   # BO tiers (basic vs derived)
  - DEC-9d1f4b   # D327 — Shared dimension normalization
  - DEC-ebf0b4   # D268 — Session Discipline
  - DEC-804874   # D366 — L-Node Semantic Gate (semantic_family enum origin)
related_mwrs:
  - 2026-05-12-semantic-base-audit-SES-a223ea.md       # the failure audit this design responds to
  - 2026-05-12-tier1-cf-certification-design-SES-a223ea.md   # the narrower Tier-1 design this absorbs and extends
  - 2026-05-11-total-revenue-production-gap-SES-1c080e.md   # service-gap noted (CF-PATCH endpoint absent)
related_change_records:
  - CHG-a880b3
repair_location: B
affected_boundary: canonical_evaluation
foundation_gate: passed
---

# Semantic Definitions Authority — design

> **ADR-grade design. Decision-pending.** This MWR proposes the platform's standing governance for Business Field (BF), Business Object (BO), Canonical Field (CF), semantic_family, definitions, aliases, certification state, provenance, and Meaning-once validation. It does **not** file an ADR, author DBCPs, propose DDL changes, or implement endpoints. It is the design frame the operator reviews before any implementation proceeds. The work stops at the "design ready for ADR promotion" line.

## Revision history

| Revision | Date | Changes |
|---|---|---|
| R1 | 2026-05-12 (initial) | First draft of the SDA design covering §0–§19. Six C-conflicts surfaced. Q1–Q10 left as open questions. |
| R2 | 2026-05-12 PM | Operator-directed patches + settled Q1–Q10 defaults. See "Revision R2 details" below. Phase 0 authorised. |
| R3 | 2026-05-12 PM | Consistency sweep prior to Phase 0 implementation. Six remaining inconsistencies patched (Patches 8–13). See "Revision R3 details" below. Phase 0 cleared to begin. |
| **R3.1** | **2026-05-12 PM** | **Phase 0.1 cleanup verified §C3 live state.** Implementing session: `SES-4a7efb` (bc-core, closed). Implementing commit: `bc-core@cb4b972` (`feat(sda): Phase 0 read-only Semantic Definitions Authority projection`). §C3 rewritten: the unique index IS applied in the live DB as `canonical_field_field_name_key` (Drizzle name `uq_canonical_field__name` is drift-only). Phase 0 diagnostic tightened to distinguish strict single-column unique indexes from composite indexes that merely include `field_name`. Audit MWR §Pass 4 corrected in lockstep (A4 added). |

### Revision R2 details (this revision)

Seven targeted patches applied to the design body:

1. **Lifecycle state count clarified** (§C1, §4) — six certification states only (`proposed`, `reviewing`, `certified`, `deprecated`, `superseded`, `withdrawn`); `archived` is **not** a seventh state, it is a separate `is_archived` boolean flag (visibility only, settable when state ∈ {superseded, withdrawn}). State machine and transitions table updated.
2. **bc-ai red verdict rewritten** (§6) — AI is advisory evidence requiring **human acknowledgement**, never autonomous authority. AI never autonomously blocks. Deterministic gates are the only hard law. Red / amber / unverified verdicts require acknowledgement with rationale; the AI verdict itself does not block state transition.
3. **G9 tightened** (§5) — runs at the moment a *new or modified* candidate reference is being authored; validates that the candidate's target primitive is in the per-authoring-path allowed-state set. Does **not** scan existing references to a primitive at certification time.
4. **G10 tightened** (§5) — signature computed via canonical JSON serialization (sorted keys, no insignificant whitespace) so semantically-equivalent JSON bodies collide deterministically. `replace` flow excludes the row being replaced from the collision search. Three collision classes distinguished: **Class-A certified-blocking** (Sev-1, non-overridable), **Class-B proposed/reviewing-review** (Sev-2, overridable with rationale), **Class-C deprecated/superseded/withdrawn** (informational, not blocking).
5. **G2 split** (§5) into **G2a exact-identity uniqueness** (byte-identical match → non-overridable) and **G2b normalized-form collision** (normalized match → overridable with rationale + acknowledgement).
6. **Phase 0 wording corrected** (§11) — Phase 0 is **strictly read-only projections**. No DDL, no DBCP, no status migration, no enforcement, no preflight, no gate evaluation. The `draft → proposed` bulk status migration is **Phase 1 DBCP-1d** (governed write), not a Phase 0 action.
7. **Override matrix added** (§5.5) — every gate's overridability is now explicit. **Non-overridable gates: G2a, G5, G6, G7, G8, G10 Class-A.** These six form the SDA's structural floor. All other gates are overridable via D366-style mechanic (rationale ≥ 40 chars + auto-spawned follow-up task) or compat-mode-controlled (G9). AI advisory verdicts are not blocking; acknowledgement is the lock.

Operator defaults for Q1–Q10 settled in §10:

| Q | Settled |
|---|---|
| Q1 | Route prefix `/api/semantic-definitions/*` (top-level, readable). Module name `sda` stays as the codebase shorthand. |
| Q2 | Two alias tables: existing `business_field_alias` (source-system) + new `vocabulary_name_alias` (historical/supersession). |
| Q3 | Central `primitive_supersession` table. |
| Q4 | Central append-only `primitive_provenance` table; existing per-primitive columns retained as current projection. |
| Q5 | Follow existing master-table naming convention; Phase 0 verifies. |
| Q6 | Cognito `sub` + role-at-action-time stored on certification_record. |
| Q7 | Per-integration shadow/block flags with visible counters. No blind fixed date. |
| Q8 | bc-ai async by default; certification proceeds only with explicit unverified acknowledgement if advisory evidence missing at decision time. |
| Q9 | D366-style override (rationale + follow-up task), only for gates marked overridable. |
| Q10 | Single umbrella SDA ADR + DBCPs + per-phase implementation MWRs. |

Body sections affected by R2: §C1 (lifecycle resolution), §4 (state machine + transitions table), §5 (G2/G2a/G2b, G9, G10), §5.5 (new override matrix), §6 (AI handling rewrite), §7 (route prefix), §9 (storage model — settled Q2/Q3/Q4), §10 (replaced with settled decisions), §11 (Phase 0 + Phase 1 wording), §14 (file list reflecting new module path), §17 (state of play). All other sections unchanged.

### Revision R3 details (this revision)

Six consistency patches applied prior to Phase 0 implementation:

8. **`/sda/*` → `/api/semantic-definitions/*` swept throughout.** All 56 occurrences of the `/sda/` shorthand replaced with the full route. The intro paragraph in §7 now states: "All routes below use the full `/api/semantic-definitions/...` prefix — no shorthand in this design." No place left where shorthand is implied.
9. **AI cannot auto-transition state.** §4 transitions table row for `reviewing → proposed` no longer reads "or AI-gate fail (auto, with operator override)" — it now reads "platform_admin (only). AI never auto-transitions. A deterministic gate fail surfaces on the certification record; the human acts by calling return-to-author." Consistent with §6 (AI is advisory, never autonomous).
10. **Profile P5 hyphenation contradiction resolved.** P5 was previously labelled "snake_case, closed enum from D366" while listing hyphenated values (`measure-currency`, `dim-calendar-date`, etc.). P5 is now correctly labelled **hyphenated identifier (kebab-style for compound terms)** with regex `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`. The divergence from DEC-69f09e is documented explicitly: D366's hyphenation is preserved verbatim for the semantic_family enum specifically; the umbrella SDA ADR (Q10) records this reconciliation. Not generalised to other enums.
11. **Archive endpoint row in §7 fixed.** Previously "move `superseded → archived` (optional) | grace window elapsed". Now correctly: "set `is_archived = true` (visibility flag; does **not** change `certification_state_code`). Permitted only when state ∈ {superseded, withdrawn}. Reversed by `POST .../unarchive`." Consistent with §4 (archived is a flag, not a state).
12. **Stale "open Q1–Q10" / "operator-pending" language swept.** §C1 resolution prose now reads "Resolution (R2 accepted by operator, then refined in R3)" instead of "Proposed resolution (operator-pendings)". §C2 similarly updated. §C4 conflict-implication prose no longer asks "is snake_case the rule or a profile?" — that question is answered by §3 profile system. §15 non-decisions and §18 evidence cross-references updated to point at "settled decisions" instead of "open questions". Historical mention of "Q1–Q10 left as open questions" remains only inside the R1 revision-history row, which is correct.
13. **Risk R-2 corrected.** The mitigation no longer reads "AI verdicts are persisted alongside but not gate-blocking unless operator explicitly configures them as such." It now reads: "**bc-ai is never gate-blocking — by config or otherwise.** Deterministic gates are the only blocking authority. A non-green AI verdict or a missing one requires an explicit human acknowledgement with rationale; the acknowledgement is the lock, not the AI verdict itself. There is no operator-configurable knob that promotes AI to a gate." Consistent with §6.

Body sections affected by R3: revision-history (this block), §C1 / §C2 / §C4 (resolution prose), §3 P5 (hyphenation profile), §4 transitions (no AI auto-transition), §7 (all routes full-form; archive endpoint set-flag), §12 risk R-2, §15 non-decisions, §18 evidence cross-reference. No semantic changes; only consistency. All other sections unchanged.

**With R3 landed, Phase 0 implementation can begin.** A new session is opened for the Phase 0 slice.

---

## 0. Purpose and stance

BareCount is a contract-discipline platform. It enforces contracts on customer data — admission contracts, canonical schemas, metric contracts. But the platform's *own vocabulary* (BF, BO, CF, semantic_family) is currently not governed by any standing authority. The recent semantic-base audit found that vocabulary drift accumulates faster than diagnostic passes can catch it.

The Semantic Definitions Authority (**SDA**) is the standing fix. Where the current chapters describe governance procedurally (and the implementation drifts from them silently), the SDA is the single service surface that:

- **owns the canonical state** for BF / BO / CF identity, certification, supersession, aliasing, and provenance
- **enforces deterministic gates** at every authoring path before any reference accepts a primitive
- **integrates bc-ai as advisory evidence**, not authority — AI verdicts are recorded as inputs to certification, never as certifying acts
- **emits projection endpoints** consumed by readiness, formula-audit, chain-status, and tenant-binding so those surfaces stop re-deriving semantics from raw rows

This design does not invent new philosophy. It reconciles the existing governance (DEC-69f09e, DEC-5017fe, DEC-d72560, business-vocabulary.md, the onboarding chapters) into one implemented authority with no per-vocabulary drift between docs and code.

## 1. Conflicts found in governing sources — proposed resolutions

Following the operator's stop condition: where docs conflict, the conflict is named and a resolution is proposed (not silently invented). The operator accepts or revises before any implementation.

### C1 — Three certification lifecycles in three governing sources

| Source | Lifecycle declared | Where |
|---|---|---|
| DEC-d72560 (D301) | `draft` (default state; lifecycle not explicit) | DDL `status_code` default |
| DEC-5017fe (D139) | `draft → registered → deprecated → retired` | §Registry Structure |
| business-vocabulary.md | `proposed → reviewing → certified → superseded → withdrawn` | §Certification Lifecycle |
| DDL CHECK on `contract.canonical_field` | `status_code IN ('draft', 'certified', 'deprecated')` | `canonical-field.ts:52` |
| Implementation — BF service | `draft → certified` (binary; terminal certified) | `standard-field.service.ts:17` |
| Implementation — BO service | `draft → approved` (binary) | per BF/BO onboarding chapter |
| Implementation — CF service | `draft` only — no transitions exist | `canonical-field.service.ts` lacks any certify path |

**Conflict:** five different effective lifecycles across docs and code.

**Resolution (R2 accepted by operator, then refined in R3):** adopt **business-vocabulary.md as authoritative** for the unified lifecycle, extended by one state — `deprecated` — to cover the conventional "no longer recommended, but still queryable, not yet superseded" semantic. **The unified lifecycle is exactly six states.** `archived` is **not** a seventh state; it is a separate `is_archived` boolean visibility flag that hides a row from default listings once it has reached a terminal lifecycle state (`superseded` or `withdrawn`). The flag does not change `certification_state_code`.

```
proposed → reviewing → certified → deprecated → superseded   (terminal; supersession link required)
              │                                        ┌─────────── + is_archived flag
              │                                        │             (visibility only; hides from
              ▼                                        │             default listings; not a state)
        withdrawn   (terminal; pre-certification rejection)
                                                       │
                                                       └─── + is_archived flag (same as above)
```

The six certification states:

- `proposed` — registered with provenance; not yet reviewed (replaces ad-hoc `draft`)
- `reviewing` — under gate evaluation (deterministic + AI advisory)
- `certified` — admissible to contract authoring; meets all gates
- `deprecated` — discouraged from new authoring; still resolves for existing references
- `superseded` — replaced by another primitive; supersession link mandatory; terminal
- `withdrawn` — pre-certification rejection; terminal

`is_archived` is a boolean column on the primitive's row. It is settable only when the row is in `superseded` or `withdrawn` (DB CHECK constraint). Setting `is_archived = true` removes the row from default API listings; it remains queryable via explicit `?includeArchived=true` flag for historical audit. **`certification_state_code` and `is_archived` are independent dimensions** — one is the governance state, the other is a visibility control.

Existing rows in `draft` migrate to `proposed` via a Phase 1 governed DBCP write (not Phase 0 — see §11). The `draft` value remains accepted on read for backward compatibility through a defined sunset window (§Compatibility Plan).

### C2 — Primitive name disagreement: Business Field vs Standard Field

| Source | Name | Used by |
|---|---|---|
| business-vocabulary.md | "Business Field" | All other governing docs + ADR text in DEC-d72560, DEC-aa6251 |
| DEC-5017fe (D139) | "Standard Field" | The ADR itself |
| bc-core controller | `StandardFieldController` | Class name |
| bc-core route | `/business-fields` | The route prefix |

**Conflict:** the controller is named `StandardField*` but routes are `/business-fields`; the documents use both names interchangeably and DEC-5017fe uses "Standard Field" everywhere.

**Resolution (R2 accepted by operator):** **Business Field** is the canonical term for the primitive everywhere; **Standard Field Registry** is the canonical term for the *governance facility* (ISO 11179 MDR) that registers BFs. The controller, service, and repository are renamed `BusinessField*` in a follow-up rename pass (out of scope for this design). The route is already `/business-fields`; this is a code-only rename.

### C3 — CF uniqueness — declared, indexed, observed and now verified

| Source | Claim |
|---|---|
| DEC-d72560 | `field_name TEXT NOT NULL UNIQUE` in DDL |
| Drizzle schema (`canonical-field.ts:46`) | `uniqueIndex('uq_canonical_field__name').on(table.fieldName)` |
| canonical-field-seeding.md §Quality Checks | "No duplicate `field_name` — Zero rows" |
| Audit MWR §Pass 4 (original) | 12+ stem-clusters that appeared to contain literal name duplicates |
| **Phase 0 live diagnostic** | `enforcesGlobalFieldNameUniqueness: true`; `canonical_field_field_name_key` is the live unique index; `exactDuplicateCount: 0`; `liveIndexNameDriftFromDrizzle: true` |

**Resolution (verified by Phase 0 implementation 2026-05-12 PM):**

- A unique single-column index on `contract.canonical_field(field_name)` is **applied in the live database** under the name `canonical_field_field_name_key` (PostgreSQL auto-generated when the constraint was declared without an explicit name).
- The Drizzle schema declares the same constraint under the name `uq_canonical_field__name`. **These names do not match**, but the constraint *behavior* is identical: byte-identical `field_name` collisions are rejected by the database.
- The audit MWR's earlier finding of "literal duplicates" was a misread of the stem-grouping output — actual byte duplicates count is **zero**. See audit MWR §Pass 4 "Corrected finding" (R3 PM A4).
- A composite unique index that *includes* `field_name` would NOT count as enforcing global uniqueness; the Phase 0 diagnostic distinguishes the two cases (`strictSingleColumnIndexes` vs `compositeIndexesIncludingFieldName`).

**Residual issues for downstream phases:**

1. **G2b normalized-form near-duplicates** — 172 stem-clusters covering 403 CFs registered with different byte strings that normalise to the same form (`Asset Age` vs `asset_age`, etc.). The DB unique index does not prevent these because the strings differ at the byte level. SDA Phase 1 G2b gate + Tier-1 design's survivor selection cover the cleanup.
2. **Drizzle / live index-name drift** — code declares `uq_canonical_field__name`; DB applied `canonical_field_field_name_key`. Cosmetic but real. Phase 1 or a small standalone DBCP can rename the live index to match the Drizzle declaration (or vice versa, alter the Drizzle declaration to match what shipped).

### C4 — Naming standard for CFs vs DB columns

DEC-69f09e (D148) prescribes snake_case for DB columns / API fields / JSON keys. The chapter is explicit about its scope:

> Scope. In: All code, schemas, APIs, databases across all BareCount repos. Out: External system identifiers (SAP BKPF, Salesforce Account__c), UI display labels, foundation business vocabulary.

CFs are **business vocabulary at the metric-input boundary**. Are they "DB columns" (snake_case mandatory) or "foundation business vocabulary" (out of scope)? The two governing-source readings:

- **canonical-field-seeding.md §Naming Rules** — "snake_case, globally unique. ISO 11179 naming per DEC-69f09e."
- **canonical-field-seeding.md §Forbidden Patterns** — "BO-prefixed names → rejected at validation layer"
- **DEC-d72560 §1** — `field_name TEXT NOT NULL UNIQUE` with no case discipline declared at the ADR layer

**Conflict implication:** the documents say snake_case is mandatory for CFs, but the implementation accepts Title Case With Spaces today (audit found 122). The R2 resolution treats this not as a single global rule but as a *profile system* (§3) — CFs follow Profile P3 (snake_case, formula-variable-shaped, no BO prefix), with explicitly governed divergences elsewhere (e.g. P5 semantic_family preserves D366 hyphenation — see Patch 10 in revision history).

**Proposed resolution:** see §3 (Vocabulary-specific ISO profiles). The SDA recognises **five distinct naming profiles** — each vocabulary surface has its own profile rather than one rule for everything. CFs follow the CF profile (snake_case, formula-variable-shaped). 122 non-snake-case CFs are profile violations; they enter the cleanup workflow in Phase 4.

### C5 — Semantic family — closed enum referenced but never enforced

The `semantic_family` column was added to `canonical_field` (visible in `canonical-field.ts:39`) with a code comment naming a 24-value closed enum per D366 / ADR-804874:

```
identifier, code, name, text, measure-currency, measure-count, measure-ratio,
measure-percent, measure-score, date, period, datetime, duration, dim-calendar-date,
dim-fiscal-period, dim-currency, dim-country, dim-legal-entity, dim-gl-account,
dim-cost-center, dim-customer, dim-vendor, dim-product
```

There is no CHECK constraint enforcing the enum. There is no service path that populates `semantic_family`. The audit found all 603 CFs with `semanticFamily = NULL`.

**Implementation drift:** the closed enum exists in code comment only. Neither the DB nor the service enforces it.

**Proposed resolution:** Phase 1 publishes the closed enum as a master table (`master.semantic_family`) and the SDA's certification gate requires non-null `semantic_family` ∈ enum before promotion to `certified`. Existing `proposed` rows can have NULL `semantic_family`; promotion is blocked until populated. Phase 4 backfills.

### C6 — Reference-time certification enforcement absent

| Source | Claim | Implementation |
|---|---|---|
| business-vocabulary.md | "A primitive must be certified before a contract version can reference it" | None of the reference paths check |
| BF/BO onboarding chapter | BO approval checks "All BFs certified" | **Confirmed enforced** at BO approval (`cc-onboarding.service.ts:348`) |
| canonical-field-seeding.md | "Every CF must be certified before CC reference" *(implied; not explicit in chapter)* | **Not enforced.** `cc_field_mapping` create accepts `proposed`/`draft` CFs (`cc-onboarding.service.ts:463–499`) |
| DEC-d72560 §Risks | "CF status lifecycle (draft → certified → deprecated); MC validation gate checks CF status." | **Not implemented.** MC onboarding does not check CF certification status |

**Implementation drift:** BO approval enforces BF certification, but **no other path enforces CF certification.** cc_field_mapping create, mc_binding create, MC version activate — all accept uncertified CFs.

**Proposed resolution:** Phase 2 of the SDA integrates certification gates at every reference path. CFs in `proposed`, `reviewing`, `withdrawn`, `superseded` cannot be referenced by new authoring; `certified` and `deprecated` (with warning) can.

## 2. Authority boundary

### Owns

The SDA is the **single authority** for:

| Entity | What SDA owns |
|---|---|
| Business Field | identity (`field_id`), name, definition, data_type, representation_term, object_class, property, pii_classification, provenance (source_standard + standard_ref), certification state, supersession link, aliases (`business_field_alias`) |
| Business Object | identity, name, definition, function/subfunction/industry codes, tier_code, composition (BFs + roles), provenance, certification state, supersession link |
| Canonical Field | identity (`canonical_field_id`), name, display_name, function/subfunction, data_type, role, **semantic_family**, unit_type_code, description, provenance, certification state, supersession link |
| Semantic Family | the closed enum of family codes (24 values from D366), per-family compatible operators and units |
| Definition | the structured definition body per primitive (definition_text, semantic_intent, examples, governing-source citation) |
| Provenance | the standards-source record per primitive (source_standard ∈ {oagis, iso_20022, xbrl_gaap, ifrs, uncefact, bc_standard, computed}; standard_ref) — append-only history |
| Aliases | source-system alias records for BFs (`business_field_alias`), historical-name aliases for CFs after supersession |
| Certification Record | the persisted artifact of a certification act: gate results, AI advisory record, certifier identity, timestamp, governing-source citation |
| Meaning-once Validation | the platform-wide invariant that the `(canonical_contract, business_field, resolution_rule, filter_signature, compute_signature)` signature in `cc_field_mapping` cannot resolve to more than one *certified* CF; the SDA's validation surface returns this verdict before mapping authoring proceeds |

### Does not own

The SDA is **not** the authority for:

| Entity | Owning authority |
|---|---|
| Tenant data | per-tenant CC fact projection, runtime canonical objects |
| Runtime values | engine evaluation outcomes, evidence rows, metric snapshots |
| Reader execution | reader-runtime services |
| MC evaluation results | metric_evaluation_engine + evidence projections |
| Source catalog | source_registration / source_reference |
| CC envelope | canonical-contract authoring (consumes SDA-certified CF + BO references; does not author them) |
| MC envelope | metric-contract authoring (consumes SDA-certified CF references; does not author them) |
| Tenant binding decisions | tenant.contract_binding writer paths |

The SDA **emits** state that consumers read. It does **not** mutate runtime, tenant, or evaluation tables.

### Interacts with

The SDA interacts with each downstream surface via a typed contract:

| Consumer | Interaction shape |
|---|---|
| Canonical Contract (CC) onboarding | preflight call to validate that every BO + CF in the mapping is certified; receive Meaning-once verdict for each cc_field_mapping row |
| Metric Contract (MC) onboarding | preflight call to validate every variable CF is certified; reject MC version activation if any referenced CF is non-certified |
| Canonical Mapping (CM) authoring | preflight call to validate every BF source_field_ref points at a certified BF |
| Observation Contract (OC) authoring | preflight call to validate field_selection references certified BFs |
| Readiness / Formula Audit | read projection of SDA certification verdicts; stop independently re-deriving "is this clean" |
| Chain status | read SDA certification state for L1 (CF registered + certified), L2 (CF→BF mapped through certified BFs), L3 (BF in CC schema, BF certified), L7 (in catalog with non-superseded references) |
| Tenant binding | tenant-bind preflight rejects bindings to MCs that reference non-certified CFs |

## 3. Vocabulary-specific ISO 11179 profiles

DEC-69f09e is one rule for all technical names. The SDA recognises that **different vocabulary surfaces carry different naming constraints**. Five profiles, each with its own rule set:

### Profile P1 — Technical DB / API / JSON naming (DEC-69f09e literal)

- snake_case, mandatory representation term suffix
- Examples: `contract_id`, `admitted_ts`, `description_text`
- Applies: DB columns, JSON keys, API field names (kebab-case for routes)
- Authority: DEC-69f09e; SDA validates only when registering DB / API surfaces it owns

### Profile P2 — Business Field name profile

- snake_case, **BO-scoped** prefix mandatory unless one of the five shared dimensions
- Form: `{bo_prefix}_{property}` (e.g. `invoice_hdr_total_amount`, `receivable_hdr_amount`)
- Shared dimensions exempt: `company_code`, `currency_code`, `language_code`, `country_code`, `unit_of_measure`
- ISO 11179 decomposition required: `object_class` (= BO prefix) + `property` (= field slug) + `representation_term` (Amount, Code, Date, …)
- Length: ≤ 64 chars
- Authority: DEC-f66378 (D292/D294) + DEC-5017fe + business-vocabulary.md

### Profile P3 — Canonical Field name profile

- snake_case, **NOT BO-scoped**, formula-variable-shaped
- Form: business-meaning name as it appears in metric formulas (`total_revenue`, `accounts_receivable_balance`, `dso_days`)
- Output CF form: `{metric_short_name}_{property}` (e.g. `dso_days`, `current_ratio_value`)
- Shared dimension CFs use the shared name verbatim: `company_code`, `currency_code`, …
- **No BO prefix** (a CF named `receivable_hdr_amount` is rejected — that's a BF name)
- Forbidden: spaces, Title Case, non-alphanumeric (except `_`)
- Length: ≤ 64 chars
- Authority: DEC-d72560 + canonical-field-seeding.md §Naming Rules

### Profile P4 — Metric formula variable profile

- The variable `field_code` in `metric_contract_version.body.variables[].field_code` **equals** the CF `field_name` (Profile P3). One profile, two surfaces.
- Variable role placeholders (`I1`, `O1`, `C1`, …) are internal to the MC body and do not pass through the CF profile.
- Authority: DEC-d72560

### Profile P5 — Semantic family code profile

- **Hyphenated identifier** form (kebab-style for compound terms), closed enum from D366. Lowercase ASCII alphanumerics with `-` separators on compound terms; simple terms are single words. **Not snake_case.**
- Forms: `identifier`, `code`, `name`, `text`, `measure-currency`, `measure-count`, `measure-ratio`, `measure-percent`, `measure-score`, `date`, `period`, `datetime`, `duration`, `dim-calendar-date`, `dim-fiscal-period`, `dim-currency`, `dim-country`, `dim-legal-entity`, `dim-gl-account`, `dim-cost-center`, `dim-customer`, `dim-vendor`, `dim-product`
- Regex: `^[a-z][a-z0-9]*(-[a-z0-9]+)*$`
- Authority: DEC-804874 (D366) §Section 3 (deterministic compatibility filter)
- **Documented divergence from DEC-69f09e.** DEC-69f09e prescribes snake_case for DB column values and JSON property values; P5 carries hyphenated enum values *as a value content convention specific to the semantic_family closed enum* (not a column name or JSON key). The umbrella SDA ADR (Q10) records this reconciliation explicitly: D366's hyphenation is preserved verbatim for the semantic_family enum and is not generalised to other value enums. The choice avoids an enum-wide rename (which would invalidate the existing D366 reference set) while keeping the divergence narrowly scoped and explicitly governed.

**One regex does not fit all five profiles.** The SDA's name-validation gate dispatches to the right profile based on the primitive type being registered.

## 4. Certification lifecycle (unified)

The SDA's certification state machine, applied uniformly to BF, BO, and CF. **Six states only.** `is_archived` is a separate visibility flag, not a state:

```
         ┌─────────┐       review        ┌──────────┐       gates pass        ┌──────────┐
         │proposed │ ───────────────────▶ │reviewing │ ──────────────────────▶ │certified │
         │(initial)│                       └──────────┘                         └──────────┘
         └─────────┘                            │                                    │
              │                                 │ gates fail                         │
              │  rejected pre-review            │ (back to proposed                  │ usage
              │                                 │ for fixes, or                      │ declines
              ▼                                 │ withdrawn if abandoned)            ▼
        ┌──────────┐                            ▼                              ┌───────────┐
        │withdrawn │                       ┌──────────┐                        │deprecated │
        │(terminal)│                       │withdrawn │                        │           │
        └──────────┘                       │(terminal)│                        └────┬──────┘
                                           └──────────┘                              │ replaced
                                                                                    ▼
                                                                              ┌───────────┐
                                                                              │superseded │
                                                                              │(terminal; │
                                                                              │ link req.)│
                                                                              └───────────┘

   Visibility flag (orthogonal to lifecycle):
   is_archived ∈ {false, true} — settable only when state ∈ {superseded, withdrawn}.
   `true` hides row from default listings; row remains queryable via ?includeArchived=true.
```

### Permitted transitions

| From | To | Trigger | Authorized by |
|---|---|---|---|
| `proposed` | `reviewing` | `POST /api/semantic-definitions/:type/:id/submit-for-review` | platform_admin or schema_author |
| `proposed` | `withdrawn` | `POST /api/semantic-definitions/:type/:id/withdraw` | platform_admin or schema_author |
| `reviewing` | `proposed` | `POST /api/semantic-definitions/:type/:id/return-to-author` (used when a deterministic gate failed and the issue is fixable, or when the certifier chooses to send back) | platform_admin (only). AI never auto-transitions. A deterministic gate fail surfaces the failure on the certification record; the human acts by calling return-to-author. |
| `reviewing` | `certified` | `POST /api/semantic-definitions/:type/:id/certify` after gate pass | platform_admin |
| `reviewing` | `withdrawn` | `POST /api/semantic-definitions/:type/:id/withdraw` | platform_admin or schema_author |
| `certified` | `deprecated` | `POST /api/semantic-definitions/:type/:id/deprecate` | platform_admin |
| `deprecated` | `superseded` | `POST /api/semantic-definitions/:type/:id/supersede` with `supersededBy: <new_id>` | platform_admin |
| `certified` | `superseded` | `POST /api/semantic-definitions/:type/:id/supersede` (skipping deprecated) | platform_admin |
| (visibility flag) | `is_archived = true` | `POST /api/semantic-definitions/:type/:id/archive` — only when state ∈ {superseded, withdrawn}; does not change lifecycle state | platform_admin |
| (visibility flag) | `is_archived = false` | `POST /api/semantic-definitions/:type/:id/unarchive` — reverses the flag; row reappears in default listings | platform_admin |

### Immutable fields after certification

Once `certified`, the following fields are **immutable** (any change requires supersession):

| Field | Reason |
|---|---|
| `field_name` (BF/CF) / `business_object_name` (BO) | Identity — references depend on the name |
| `data_type` (BF/CF) | Type-conformance gate at admission relies on this |
| `representation_term` (BF) | ISO 11179 grammar |
| `object_class` (BF) | ISO 11179 grammar; BO-scoping anchor |
| `tier_code` (BO) | basic vs derived governs evaluation semantics |
| Provenance record (all) | append-only history; new provenance records are added, never edited |

Mutable post-certification (with audit):

- `display_name`, `description_text` (with semantic-equivalence check via AI-advisory)
- `aliases` (additive only; deletion requires supersession)
- `subfunction_code` (with operator justification)

### Alias / supersession behaviour

When a primitive is `superseded`:

- The non-survivor row carries `superseded_by_id` pointing at the survivor.
- The non-survivor `field_name` becomes a historical alias on the survivor (queryable through `GET /api/semantic-definitions/cf?alias=<old_name>` or equivalent).
- Active references (cc_field_mapping rows, mc_binding rows, MC variable bindings) **remain pointing at the non-survivor** until migration; the SDA emits a "stale reference" projection consumed by the readiness surface so operators can sequence migration.
- New references to the non-survivor are **rejected** at the SDA preflight gate.
- The supersession is **non-retroactive** — historical metric snapshots produced under the non-survivor CF are unaffected (Foundation Invariant III).

### Backward compatibility for existing references

- Existing `cc_field_mapping` rows that point at non-certified CFs are **not** deleted by the SDA. They are reported as "compatibility-tier references" in the projection. The cleanup workflow (Phase 4) migrates them.
- During the migration window, the preflight gate operates in **shadow mode** by default — gate failures are logged but not blocking — and switches to **block mode** per-tenant or platform-wide on operator command. This is the same pattern used by the L-node semantic gate (D366).

## 5. Deterministic gates

Gates are mechanical pass/fail checks the SDA evaluates during `proposed → reviewing → certified` transitions. They are deterministic (same input → same verdict) and **do not depend on bc-ai**. AI-advisory verdicts run **alongside** the deterministic gates but do not replace them.

### Gate G1 — Naming profile compliance

- Input: `(primitive_type, name)`
- Check: name matches the profile regex (P2 for BF, P3 for CF, etc.)
- Verdict: pass / fail with the profile that was checked and the regex that did not match

### Gate G2a — Exact-identity uniqueness (non-overridable)

- Input: `(primitive_type, name)`
- Check: no other row in the same primitive's table has byte-identical `name` regardless of certification state. This is the DB-level `UNIQUE` constraint reified as a service-level pre-check. Same byte string → reject.
- Verdict: pass / fail with the colliding primitive's id and state
- **Non-overridable.** A byte-identical name collision is a Sev-1 hard failure. The DB unique index is the structural backstop; the SDA's G2a check rejects before the DB error so the caller gets a clean diagnostic rather than a constraint-violation message.
- Phase 0 verification (R3.1, completed 2026-05-12 PM): the live DB enforces strict single-column uniqueness on `contract.canonical_field(field_name)` via the index `canonical_field_field_name_key` (PostgreSQL auto-generated name). The Drizzle-declared name `uq_canonical_field__name` is index-name drift only, not a missing constraint. G2a uses the DB constraint as the structural backstop; the SDA's G2a service-level check is a pre-rejection diagnostic that returns a clean error before the DB constraint fires. No DBCP for *introducing* uniqueness is needed; a later governed migration can align the Drizzle declaration to the live index name (or vice versa).

### Gate G2b — Normalized-form collision (overridable with rationale + acknowledgement)

- Input: `(primitive_type, name)`
- Check: no certified, deprecated, or active (`proposed`/`reviewing`) primitive of the same type has `normalize(name) == normalize(input_name)` where `normalize = lowercase + trim + replace(non-alphanumeric, '_')`
- Verdict: pass / fail-review with the colliding primitive's id, current state, and the normalized form that collided
- **Overridable** with rationale (≥ 40 chars per D366 override pattern) + human acknowledgement. The override is recorded on the certification record; an auto-spawned follow-up task tracks the eventual semantic reconciliation between the two near-duplicate primitives.
- This catches `Asset Age`, `asset_age`, ` Asset Age `, `Asset-Age` as collisions even though the byte strings differ. Allows controlled exceptions for genuine cases (e.g. a CF named `dso_days` may collide with `DSO_Days` if the latter was historically registered — the override preserves intent).

### Gate G3 — Definition presence and quality

- Input: `description_text` (CF) or `definition` (BF/BO)
- Check: non-null, ≥ 1 sentence, no banned placeholder strings (TBD, TODO, placeholder, fixme, xxx)
- Verdict: pass / fail

### Gate G4 — Provenance presence

- Input: `(source_standard, standard_ref)`
- Check: `source_standard ∈ {oagis, iso_20022, xbrl_gaap, ifrs, uncefact, bc_standard, computed}`; `standard_ref` non-null when standard is external (not `bc_standard` or `computed`)
- Verdict: pass / fail

### Gate G5 — `semantic_family` populated and in enum (CF only)

- Input: `semantic_family`
- Check: `semantic_family ∈ master.semantic_family` (closed enum)
- Verdict: pass / fail

### Gate G6 — Data type / unit compatibility

- Input: `(data_type, unit_type_code, semantic_family)`
- Check: data_type and unit are mutually compatible per the semantic_family's compatibility matrix (e.g. `measure-currency` requires `data_type=number` and `unit_type_code=currency`)
- Verdict: pass / fail

### Gate G7 — BO-scoped naming (BF only)

- Input: `(field_name, business_object_code)`
- Check: `field_name` starts with `business_object_code + '_'` OR `field_name` is one of the five shared dimensions
- Verdict: pass / fail

### Gate G8 — Non-BO-prefixed name (CF only)

- Input: `(field_name, existing_BO_codes)`
- Check: `field_name` does not start with any `business_object_code + '_'` UNLESS the CF is explicitly registered as a shared-dimension CF and matches the five-dim list exactly
- Verdict: pass / fail

### Gate G9 — Candidate reference admissibility

- **Scope:** runs at the moment a *new or modified* CC field mapping, MC variable binding, CM field-resolution entry, or OC field-selection entry is being authored. **Does not** scan existing references to a primitive at certification time.
- Input: the candidate reference payload — e.g. `{authoring_path: 'cc_field_mapping_create', target_primitive_type: 'cf', target_primitive_id: <uuid>}`
- Check: the target primitive's current `certification_state_code` is in the per-authoring-path allowed-state set:

| Authoring path | Allowed target states |
|---|---|
| `cc_field_mapping` create / replace | `certified` only (writer side); read paths may resolve through `deprecated` for backward compat |
| MC variable binding (new) | `certified` only |
| MC variable binding (existing, version bump) | `certified` (preferred); `deprecated` permitted with warning recorded on the new MC version's certification record |
| `canonical_mapping_version.field_resolutions[]` (new entry) | BF must be `certified` |
| OC `field_selection[]` (new entry) | BF must be `certified` |

- Verdict: `pass` / `fail` with `{target_id, current_state, allowed_states}`. **`proposed`, `reviewing`, `withdrawn`, `superseded` are never permitted target states for new authoring.**
- Behaviour: rejection is at the candidate-reference moment only. **Existing references to a primitive are not affected** by this gate — when a primitive transitions `certified → deprecated`, existing references continue to resolve. The SDA's stale-reference projection surfaces the references for the operator's migration queue (§7), but G9 does not block primitive state transitions on the count of existing references.
- This is the operational shape of "must be certified before contract authoring references it" (business-vocabulary.md). The check fires at the authoring write, not at the primitive's own certification.

### Gate G10 — Meaning-once validation (cc_field_mapping authoring)

- **Scope:** runs on `POST /api/onboarding/cc/:id/field-mappings` (create) and `POST /api/onboarding/cc/:id/field-mappings/:mid/replace` (D330-R5 replace).
- **Signature:** computed via **canonical JSON serialization** — keys sorted alphabetically, no insignificant whitespace, normalised primitive forms — so semantically-identical `filter_json` / `compute_json` bodies produce byte-identical signatures regardless of authoring style. Signature = `sha256(canonical_json({cc_id, bf_id, rule, filter_canonical, compute_canonical}))`. Stable across re-orderings of JSON keys.
- **Exclude-current-row:** on `replace` flow, the row being replaced (`mapping_id`) is **excluded** from the collision search — replacing a row with the same signature pointing at the same CF is allowed (the case where the operator is correcting metadata without changing the signature). Without this exclusion, every D330-R5 replace would self-collide.
- **Three collision classes** (distinguished by the colliding CF's certification state):

| Collision class | Colliding CF state | Verdict | Override path |
|---|---|---|---|
| **Class-A — Certified-blocking** | Another `certified` CF already resolves through this signature | `fail-blocking` (Sev-1 hard) | **Non-overridable.** The cc_field_mapping authoring is rejected. Operator must either (a) author distinguishing `filter_json`/`compute_json` on one side, (b) target the existing CF instead and deprecate the candidate, or (c) deprecate the existing CF and supersede with the candidate. Foundation Invariant I in force. |
| **Class-B — Proposed/reviewing-review** | Another `proposed` or `reviewing` CF currently aims at this signature (i.e. it has a candidate cc_field_mapping under review) | `fail-review` (Sev-2 soft) | **Overridable with rationale + human acknowledgement.** Both candidates have not been certified yet; the operator names which one is the survivor and the other is `withdrawn`. The acknowledgement is recorded; both candidates' SDA records carry the cross-reference. |
| **Class-C — Deprecated / superseded / withdrawn** | Only `deprecated`, `superseded`, or `withdrawn` CFs occupy the signature | `pass` (with informational note) | None needed — these states are not blocking. The candidate proceeds; the deprecated/superseded CFs are surfaced in the response for operator awareness. |

- Verdict shape: `{verdict: 'pass'|'fail-blocking'|'fail-review', class: 'A'|'B'|'C'|'none', colliding: [{cf_id, cf_name, state, mapping_id}], signature, can_override: bool}`.
- This gate operationalises Foundation Invariant I (Meaning is evaluated once) at the cc_field_mapping authoring surface, distinguishing the hard certified-blocking case from the soft pre-certification review case.

### Gate ordering

Gates run in order G1 → G10 at certification (with G9 + G10 running only at reference-authoring time, not at primitive certification time). Any fail returns the verdict before subsequent gates run (short-circuit). The full verdict block is persisted as the certification record's `gateResults` (pass/fail per gate, detail message).

### 5.5 — Override matrix

Each gate carries an explicit overridability disposition. Non-overridable gates are **the only hard law** of the SDA — no operator override, no AI verdict, no human acknowledgement can bypass them. Overridable gates accept a D366-style override mechanic (rationale ≥ 40 chars + auto-spawned follow-up task per Q9) recorded on the certification record.

| Gate | Class | Overridable? | Override mechanic | Why |
|---|---|---|---|---|
| **G1** — Naming profile compliance | Deterministic | **Yes** | Rationale + follow-up task; common case is grandfathering an existing non-compliant primitive whose rename is queued | Profiles have legitimate exceptions (standards-sourced names that carry external grammar verbatim, historical pre-discipline rows) |
| **G2a** — Exact-identity uniqueness | Deterministic | **No** | None | Byte-identical name collisions violate the registry's primary-key discipline; DB UNIQUE index would reject too; no defensible exception |
| **G2b** — Normalized-form collision | Deterministic | **Yes** | Rationale + follow-up task; common case is intentional near-name where the operator picks one survivor over the cycle | Near-names can be intentionally distinct (e.g. `currency_code` and `currency_codes_supported_count` normalise to overlapping stems but are semantically distinct) |
| **G3** — Definition presence + quality | Deterministic | **Yes** | Rationale + follow-up task; primitive may be promoted with sparse description if the upstream standard's description is absent | Definition quality is a quality bar; some standards-sourced primitives have terse upstream descriptions; certification with terse description is acceptable with audit trail |
| **G4** — Provenance presence | Deterministic | **Yes** | Rationale + follow-up task | `bc_standard` and `computed` source_standards have no external `standard_ref`; override path handles the (rare) case of a `proposed` primitive moving forward without provenance pending resolution |
| **G5** — `semantic_family` populated and in enum | Deterministic | **No** | None | The closed enum is the deterministic compatibility filter (D366 §3); a `semantic_family = NULL` certification would break downstream type/unit checks; no defensible exception |
| **G6** — Data type / unit compatibility | Deterministic | **No** | None | A primitive whose declared type / unit / semantic_family are mutually incompatible would silently produce wrong values; structural correctness, not preference |
| **G7** — BO-scoped naming (BF only) | Deterministic | **No** | None | The five shared dimensions are the only exception list; the rule is absolute outside that list — adding a sixth exception requires an ADR amendment, not an operator override |
| **G8** — Anti-BO-prefix (CF only) | Deterministic | **No** | None | Same as G7 — the BO-prefix rule for CFs (i.e. CFs do NOT carry BO prefixes) is absolute; collapsing the BF/CF distinction at the registry layer breaks Foundation Invariant I |
| **G9** — Candidate reference admissibility | Deterministic | **Compat-mode-controlled** | Per-integration shadow ↔ block flag (Q7); in shadow mode all G9 fails are logged but not blocking; in block mode all G9 fails are hard rejections (no per-call override) | Reference-time gating; the override is operational (toggle the integration's mode), not per-call. Once an integration is in block mode, individual G9 failures are non-overridable for that integration. |
| **G10 Class-A** — Meaning-once-blocking (certified collision) | Deterministic | **No** | None | Foundation Invariant I (Meaning is evaluated once) is the platform's bedrock claim; a certified-CF collision is a structural violation, not a preference |
| **G10 Class-B** — Meaning-once-review (proposed/reviewing collision) | Deterministic | **Yes** | Rationale + follow-up task + cross-reference both candidates' certification records | Both candidates are still under review; the operator may legitimately name one as the survivor and withdraw the other |
| **AI advisory red** | Advisory | **Not a "gate" in the blocking sense** | Human acknowledgement with rationale (≥ 40 chars); the AI never autonomously blocks | Per §6: AI is advisory evidence requiring human acknowledgement, never autonomous authority |
| **AI advisory amber** | Advisory | Not blocking; acknowledgement only | Human acknowledgement of AI rationale (free-text) | Same as above |
| **AI advisory unverified** | Advisory | Not blocking; acknowledgement only | Explicit unverified acknowledgement with rationale (≥ 40 chars) per Q8 | The async AI verdict may land later; the certifier proceeds with the gap recorded |

**Summary of hard-law (non-overridable) gates:** G2a, G5, G6, G7, G8, G10 Class-A. These six form the **non-negotiable structural floor**. Every other gate has a documented override path with audit trail.

**Compat-mode gates** (G9, and integration-level gate enforcement in Phase 2) are not per-call overridable — they are toggled at the integration level via Q7's shadow/block flags. The operator chooses when an integration moves from shadow to block; once in block mode, the gate enforces uniformly for that integration.

**Override audit:** every override is recorded on the certification record with `{gate_code, rationale, certifier_sub, certifier_role, timestamp, followup_task_uid}`. The follow-up task is auto-spawned per D366 pattern and tagged `sda-override`. Aggregate override counts are visible in the SDA's projection surface so the operator can see whether overrides are accumulating (a signal that gate semantics may need revision).

## 6. bc-ai use — advisory evidence, never autonomous authority

The SDA admits bc-ai as **advisory evidence requiring human acknowledgement**, never as a certifying or blocking authority. **AI verdicts never autonomously decide anything.** They are inputs to the certification record. The deterministic gates (§5 G1–G10) remain the **only hard law** that blocks or admits a primitive. AI evidence is recorded alongside; a human action is the only path forward.

### AI advisory surfaces

| Surface | Purpose | Output shape |
|---|---|---|
| `POST /ai/api/semantic-definitions/dedup-candidates` | semantic dedup — for a candidate name + definition, return existing primitives that may be duplicates | list of `{primitive_id, similarity_score 0–1, rationale, candidate_match_evidence}` |
| `POST /ai/api/semantic-definitions/near-name-review` | for a name cluster, classify each pair as duplicate / near-duplicate / distinct | per-pair `{verdict ∈ {red, amber, green}, rationale}` |
| `POST /ai/api/semantic-definitions/definition-quality` | for a definition, return `{verdict, issues[]}` where issues include placeholder language, circular definitions, missing intent | red/amber/green |
| `POST /ai/api/semantic-definitions/semantic-family-suggest` | for a primitive, suggest a `semantic_family` value | `{suggested_family, confidence, rationale}` |
| `POST /ai/api/semantic-definitions/provenance-suggest` | suggest a likely `(source_standard, standard_ref)` based on name + definition | candidate list with confidence |
| `POST /ai/api/semantic-definitions/bf-vs-cf-boundary` | for a name, classify whether it looks like a BF or CF | verdict + rationale |
| `POST /ai/api/semantic-definitions/mapping-meaning-once-explain` | given a cc_field_mapping authoring attempt that triggered G10, explain whether the existing collision is a defensible distinction the author needs to make explicit (filter/compute), or a true duplicate | red/amber/green + actionable hint |
| `POST /ai/api/semantic-definitions/maker-checker-verdict` | composite — given a primitive at `reviewing`, return overall red/amber/green | aggregated verdict with per-aspect breakdown |

Each AI response carries:

- `verdict` (red / amber / green / unverified)
- `confidence` (0.0 – 1.0)
- `rationale` (text)
- `candidate_matches` (list, where applicable)
- `model_id` + `prompt_hash` + `timestamp` (audit trail)

### AI verdict handling — human acknowledgement, never autonomous block

AI verdicts are advisory evidence. They never autonomously transition state, never autonomously block, never autonomously certify. They produce a **human-acknowledgement requirement**, recorded on the certification record. The deterministic gates (§5) are the only blocking authority.

| AI verdict | SDA behaviour |
|---|---|
| `green` (with confidence ≥ threshold) | Recorded as supporting evidence on the certification record. No human acknowledgement step required from the AI side. Deterministic gates still determine state transitions. |
| `amber` | Recorded as caveat evidence. Human acknowledgement of the AI rationale is required before `reviewing → certified`. The acknowledgement is captured in `certification_record.advisory_acknowledgements[]` with the certifier's identity + timestamp + free-text response to the AI rationale (≥ 1 char; no strict char count required since the AI verdict is advisory, not blocking). |
| `red` | Recorded as challenge evidence. The AI's red rationale becomes part of the certification record. The certifier **must explicitly acknowledge** the red verdict to proceed — but **the AI does not block**. Acknowledgement requires a rationale (≥ 40 chars per D366 pattern) explaining why the certifier disagrees with or accepts the AI challenge. Deterministic gates still rule: if any deterministic gate is failing, certification is blocked regardless of AI acknowledgement. |
| `unverified` (AI surface unreachable, or AI confidence below threshold, or AI queue not yet returned a verdict for an async invocation) | Recorded as missing evidence. Certifier may proceed by recording an explicit **unverified acknowledgement** (≥ 40 chars rationale per D366) on the certification record. Asynchronous bc-ai mode is default (Q8): the AI verdict can land later and be appended to the record as supporting / challenge evidence; it does not retroactively invalidate the certification. |

**Hard rules:**

1. **AI never blocks autonomously.** The certifier sees the AI verdict, may agree or disagree, must explicitly acknowledge non-green and unverified verdicts with a rationale, and proceeds (or chooses not to). The lock is on the human acknowledgement, not the AI verdict itself.
2. **Deterministic gates are the only law.** If a deterministic gate fails, certification is blocked regardless of AI verdict. If all deterministic gates pass, certification can proceed once any required human acknowledgements are recorded.
3. **Every AI verdict is persisted** on `certification_record.advisory_verdicts[]` with `{surface, verdict, confidence, rationale, model_id, prompt_hash, timestamp, acknowledgement (nullable)}`. The audit trail shows whether the AI was consulted, what it said, and how the certifier responded.
4. **Async bc-ai is the default.** Submission to `reviewing` queues the AI advisory work; the verdicts return on the SDA's projection surface as they land. The certifier checks the record state before promoting to `certified`; missing verdicts are treated as `unverified` and require explicit acknowledgement to proceed.

The SDA never silently certifies. The certifier's human acknowledgement (or non-acknowledgement) is the lock, with AI evidence informing the decision.

## 7. Service / API shape

The SDA is a single bc-core controller area at **`/api/semantic-definitions/*`** (per settled Q1; internal module name `sda` per the codebase). Endpoints are read-mostly with a small set of state-mutating endpoints per certification act. All routes below use the full `/api/semantic-definitions/...` prefix — no shorthand in this design.

### Read endpoints

| Endpoint | Purpose |
|---|---|
| `GET /api/semantic-definitions/{cf|bf|bo}` | paginated list with filters (status, function, subfunction, profile-compliance, has-provenance, has-semantic-family) |
| `GET /api/semantic-definitions/{cf|bf|bo}/:id` | single primitive with full state |
| `GET /api/semantic-definitions/{cf|bf|bo}/:id/certification-record` | the certification record (gate results + AI verdicts + operator notes + timestamps) |
| `GET /api/semantic-definitions/{cf|bf|bo}/:id/references` | who references this primitive: CCs, MCs, mappings, MCV bindings |
| `GET /api/semantic-definitions/{cf|bf|bo}/:id/aliases` | name aliases (including superseded names that now alias to this row) |
| `GET /api/semantic-definitions/{cf|bf|bo}/:id/provenance` | append-only provenance history |
| `GET /api/semantic-definitions/semantic-families` | closed enum of semantic_family codes + per-family unit/type compatibility |
| `GET /api/semantic-definitions/projection/certification-state` | bulk projection — for every primitive, current state; consumed by readiness / chain-status / formula-audit |
| `GET /api/semantic-definitions/projection/meaning-once-violations` | the cc_field_mapping group-by signature with multiple certified CFs — same query as audit Pass 5, now a continuously-available projection |
| `GET /api/semantic-definitions/projection/stale-references` | references pointing at non-certified or superseded primitives — for cleanup queues |

### Write endpoints (each gate-protected)

| Endpoint | Purpose | Gates applied |
|---|---|---|
| `POST /api/semantic-definitions/{cf|bf|bo}` | register (state = `proposed`) | G1, G2 (warning), G3 minimal |
| `PATCH /api/semantic-definitions/{cf|bf|bo}/:id` | update mutable metadata (proposed state only; certified state allows narrow updates) | G1, G3 |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/submit-for-review` | move to `reviewing`; triggers AI advisory + deterministic gate runs | all gates evaluated; verdicts persisted |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/certify` | move `reviewing → certified` | requires all gates pass OR explicit operator override with rationale |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/return-to-author` | move `reviewing → proposed` | none |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/withdraw` | move `proposed`/`reviewing → withdrawn` | none |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/deprecate` | move `certified → deprecated` | none (operator decision) |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/supersede` | move `{certified, deprecated} → superseded` | requires `supersededBy: <new_id>` pointing at a `certified` primitive of same type |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/archive` | set `is_archived = true` (visibility flag; does **not** change `certification_state_code`). Permitted only when state ∈ {superseded, withdrawn}. Reversed by `POST .../unarchive` (sets flag back to `false`). | DB CHECK constraint enforces state precondition; idempotent re-archive is a no-op |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/aliases` | add a name alias | G2 (alias must not collide with another primitive's certified name) |
| `POST /api/semantic-definitions/{cf|bf|bo}/:id/provenance` | append a provenance record | G4 |

### Validation / preflight endpoints (consumed by CC/MC/CM/OC onboarding)

| Endpoint | Purpose |
|---|---|
| `POST /api/semantic-definitions/preflight/cc-field-mapping` | validate a candidate cc_field_mapping row — runs G9 (refs certified) + G10 (Meaning-once) |
| `POST /api/semantic-definitions/preflight/mc-variable-binding` | validate a candidate MC variable's `field_code` — runs G9 |
| `POST /api/semantic-definitions/preflight/cm-field-resolution` | validate a candidate canonical_mapping_version field_resolutions entry — runs G9 on the BF |
| `POST /api/semantic-definitions/preflight/oc-field-selection` | validate a candidate OC field_selection — runs G9 on the BFs |

Preflight returns `{verdict: pass | fail, gateResults, advisoryNotes}` and is **non-mutating** — it does not record a certification act. The CC/MC/etc. onboarding service is the one that records the binding; the preflight is a callable check the onboarding service runs first.

### Migration / compatibility surfaces

| Endpoint | Purpose |
|---|---|
| `POST /api/semantic-definitions/migration/scan-existing-references` | one-time read-only scan — produces the migration queue of references pointing at `proposed`/`withdrawn`/`superseded` primitives |
| `GET /api/semantic-definitions/migration/compat-mode-status` | reports whether the SDA is in shadow (log-only) or block mode |
| `POST /api/semantic-definitions/migration/compat-mode` | flip shadow ↔ block mode (operator action) |

Compat-mode behaviour is the safety valve. Shadow mode = preflight calls log verdicts but do not reject — used during Phase 0–3 rollout. Block mode = preflight rejections are enforced — used after cleanup completes.

## 8. Integration points (governed call sites)

The SDA's authority is realised by **every authoring path calling the SDA before mutating state**. The integration points:

| Authoring path | Call site | SDA endpoint called |
|---|---|---|
| `POST /api/canonical-fields` (CF register) | `canonical-field.service.ts::createField` | becomes `POST /api/semantic-definitions/cf` |
| `POST /api/canonical-fields/batch` | `canonical-field.service.ts::batchCreate` | becomes `POST /api/semantic-definitions/cf` per row OR a new bulk path |
| `POST /api/business-fields` (BF register) | `standard-field.service.ts::createField` | becomes `POST /api/semantic-definitions/bf` |
| `POST /api/business-fields/:id/certify` | `standard-field.service.ts::certifyField` | replaced by `POST /api/semantic-definitions/bf/:id/certify` — the existing 9-gate logic moves into the SDA |
| `POST /api/business-objects` + `/approve` | `business-object.service.ts` | replaced by `POST /api/semantic-definitions/bo` + `POST /api/semantic-definitions/bo/:id/certify` |
| `POST /api/onboarding/cc/:id/field-mappings` | `cc-onboarding.service.ts::addMappings` | adds `await sda.preflight.ccFieldMapping(...)` before each row |
| `POST /api/onboarding/cc/:id/field-mappings/:mid/replace` (D330-R5) | `cc-onboarding.service.ts::replaceMapping` | adds `await sda.preflight.ccFieldMapping(...)` |
| `POST /api/onboarding/mc/*` | `mc-onboarding.service.ts` | adds `await sda.preflight.mcVariableBinding(...)` per variable |
| `POST /api/contracts/:id/versions/:v/activate` (MC version activate) | `contract.service.ts::activate` | rejects activation if any variable's CF is non-certified |
| `POST /api/mapping-bindings` + versions | `mapping-binding.service.ts` | adds preflight for each field_resolutions entry |
| `POST /api/onboarding/oc/*` | `oc-onboarding.service.ts` | adds preflight for field_selection |
| `POST /api/admin/readiness/tenant/:slug/bind` | `metric-readiness.service.ts` | rejects bind if MC is not "all CFs certified" |
| Formula audit | `formula-audit.service.ts` | reads SDA projection instead of re-deriving semantic checks |
| Chain status compute | `chain-status.service.ts` | reads SDA projection for L1 (CF registered + certified), L2 (CF→BF certified mapping), L3 (BF certified in CC) |

Each integration point is a one-line `await` to the SDA. The SDA's responses are structured; the authoring service is responsible for translating SDA failures into appropriate HTTP responses to the caller.

## 9. Storage model

The SDA mostly uses existing tables. Minimal additions are noted below; each requires a DBCP **out of scope of this design**.

### Existing tables (used as-is or minor schema additions)

| Table | Used by SDA | Notes |
|---|---|---|
| `contract.canonical_field` | CF identity, name, status | Column already exists for `semantic_family` (per `canonical-field.ts:39`). The CHECK constraint on `status_code` needs broadening to the 6-state enum (DBCP). |
| `contract.business_field` | BF identity, name, status | `status` column exists; lifecycle currently binary (draft / certified); CHECK constraint needs broadening to 6 states (DBCP). |
| `contract.business_object` | BO identity, name, status | Similar — binary lifecycle; CHECK constraint needs broadening (DBCP). |
| `contract.business_field_alias` | BF source-system aliases | Already exists per D299. SDA reads it; no schema change. |
| `contract.cc_field_mapping` | mapping reference targets | SDA does not own this table; consumes for G10 Meaning-once. |
| `master.unit_type` | unit_type_code enum source | Already exists; SDA reads for G6. |

### New tables (each requires DBCP — design names them; does not author DDL)

Per the settled Q2 / Q3 / Q4 / Q5 decisions in §10:

| Table | Purpose | Phase |
|---|---|---|
| `master.semantic_family` (Q5 — naming convention verified by Phase 0 before DBCP) | the closed enum from D366 + per-family compatibility metadata | Phase 1 (DBCP-1a) |
| `contract.certification_record` | per-primitive certification act audit (gate results, AI verdicts, acknowledgements, certifier Cognito `sub` + role-at-action-time per Q6, timestamp, governing-source citation, override rationale + follow-up task uid per Q9) | Phase 1 (DBCP-1c) |
| `contract.primitive_supersession` (Q3 — central table) | `{primitive_type, predecessor_id, successor_id, superseded_at, superseded_by_sub, rationale}` — covers BF / BO / CF supersession; supports multi-step chains | Phase 1 (DBCP-1e) |
| `contract.primitive_provenance` (Q4 — central append-only) | `{primitive_type, primitive_id, source_standard, standard_ref, registered_at, registered_by_sub}`; INSERT-only by service constraint; existing per-primitive `source_standard` / `standard_ref` columns are retained as a current-projection convenience for backward read compat | Phase 1 (DBCP-1f) |
| `contract.vocabulary_name_alias` (Q2 — second alias table) | historical / supersession aliases across BF / BO / CF (`{primitive_type, primitive_id, alias_name, alias_kind, created_at}` where `alias_kind ∈ {historical, supersession_predecessor}`); **separate from** existing `contract.business_field_alias` which keeps its source-system-alias role | Phase 3 (DBCP-3a) |
| (status enum + `is_archived` flag) | broadened `status_code` CHECK constraints on `contract.canonical_field`, `contract.business_field`, `contract.business_object`; new `is_archived BOOLEAN NOT NULL DEFAULT FALSE` column with CHECK constraint per §4 | Phase 1 (DBCP-1b) |

The existing `contract.business_field_alias` is **kept** in its current role (source-system aliases for BFs); the new `contract.vocabulary_name_alias` handles the new role (historical / supersession aliases across all three primitives). Two tables, two roles.

**Design discipline:** no DBCP is authored in this design. The shapes above are decision-locked for Phase 1 / Phase 3 implementation; the per-DBCP DDL is the next implementation pass once Phase 0 lands.

## 10. Operator decisions — settled (Q1–Q10)

The ten open questions are resolved by the operator on 2026-05-12. The settled answers are integrated throughout the design (§7 routes, §9 storage, §11 phases, §14 file list). Recorded here in one place for future readers.

| # | Question | **Settled answer** |
|---|---|---|
| **Q1** | Route prefix | **`/api/semantic-definitions/*`** — top-level, readable. Internal module name stays `sda`. Controller file `bc-core/src/registry/semantic-definitions/semantic-definitions.controller.ts`. |
| **Q2** | Alias storage | **Two tables.** Keep existing `contract.business_field_alias` for source-system aliases (BF→source-field). Add new `contract.vocabulary_name_alias` for historical / supersession aliases across BF / BO / CF. The two roles do not collapse into one table because they answer different questions. |
| **Q3** | Supersession storage | **Central `contract.primitive_supersession` table.** Carries `{primitive_type, predecessor_id, successor_id, superseded_at, superseded_by_sub, rationale}`. Supports multi-step chains (A → B → C) and cross-type supersession should that ever arise. Each primitive's own row remains in its own state (`superseded`) without needing a `superseded_by_id` column. |
| **Q4** | Provenance | **Central append-only `contract.primitive_provenance` table.** Carries `{primitive_type, primitive_id, source_standard, standard_ref, registered_at, registered_by_sub}`. Append-only (no UPDATE; only INSERT). Existing per-primitive `source_standard` / `standard_ref` columns **remain** as a current-projection convenience for backward read compat — they project the latest provenance row. |
| **Q5** | `semantic_family` master table naming | **Follow existing master-table naming convention after Phase 0 verifies it.** Phase 0's projection surface reads existing master tables; Phase 1 DBCP names the new table per the verified convention (e.g. `master.semantic_family` vs `master.master_semantic_family` — to be confirmed by Phase 0 read). |
| **Q6** | Certifier identity on certification_record | **Cognito `sub` + role-at-action-time, both stored.** The `sub` is the immutable identity anchor; the `role` snapshot captures who-was-acting (platform_admin, schema_author, etc.) at the time of the certification act, even if the user's roles change later. |
| **Q7** | Compat-mode rollout shape | **Per-integration shadow/block flags with visible counters. No blind fixed date.** Each integration point (cc_field_mapping, mc_variable_binding, cm_field_resolution, oc_field_selection, readiness/bind) has its own `compat_mode_code ∈ {shadow, block}` flag and an operator-visible counter of "shadow rejections that would have blocked if mode were block." Operator flips each integration to block when the counter is low / non-impactful for live tenants. |
| **Q8** | bc-ai integration | **Async by default.** Submission to `reviewing` enqueues AI advisory work; the verdict lands on the projection surface when it returns. Certification to `certified` proceeds only when (a) deterministic gates pass, and (b) any non-`green` AI verdicts have been acknowledged by the certifier, OR an explicit unverified acknowledgement (≥ 40-char rationale) is recorded if advisory evidence is missing at decision time. |
| **Q9** | Override mechanic | **D366-style: rationale ≥ 40 chars + auto-spawned follow-up task — but only for gates marked overridable in the §5.5 matrix.** Non-overridable gates (G2a, G5, G6, G7, G8, G10 Class-A) have **no override path**. |
| **Q10** | ADR shape | **Single umbrella SDA ADR.** Supersedes / amends DEC-5017fe and DEC-d72560 on lifecycle topics; amends DEC-69f09e on profile scoping. DBCPs per phase are filed as DBCP records (existing process); implementation MWRs per phase are filed under `_cross/` per existing convention. |

All ten questions are settled. The §7 service shape, §9 storage model, §11 phased plan, and §14 file list reflect these settled answers.

## 11. Implementation plan — phased

Each phase ships independently. Earlier phases are read-only / shadow-mode; later phases turn on enforcement.

### Phase 0 — Read-only authority projection + compatibility scan

**Goal:** establish the SDA service surface as **strictly read-only projections** over the existing contract registry. The status column is unchanged in DB (`draft` etc. remain as they are). No state machine. No certification flow. No gate enforcement. No status migration. Operator gets visibility into the as-is state via a single coherent SDA projection surface.

What Phase 0 ships:

- `GET /api/semantic-definitions/{canonical-fields | business-fields | business-objects}` — paginated, filtered read surfaces. Reads existing rows in their existing schema; presents `certification_state_code` by mapping the current `status_code` column (where `draft` is projected as `proposed` for display purposes — **projection only, no write**).
- `GET /api/semantic-definitions/projections/certification-state` — one row per primitive: name, type, projected-state, profile-compliant (per §3 profile regex), has-provenance, has-semantic_family, has-references, is-superseded-via-existing-data.
- `GET /api/semantic-definitions/projections/meaning-once-candidates` — group-by canonical-JSON signature with collision data per §5 G10 logic (excluding the under-replace row case, which only applies in active authoring).
- `GET /api/semantic-definitions/projections/stale-cc-field-mapping-references` — `cc_field_mapping` rows whose target CF is not in certified/deprecated state. Scope is explicitly `cc_field_mapping` only; the broader stale-reference surface (covering MC bindings, OC field_selection, CM field_resolutions, BO composition) lands in a later phase.
- `GET /api/semantic-definitions/projections/duplicate-name-clusters` — exact identity duplicates (G2a; current observed count: 0 — the live unique index prevents them) + normalized-form clusters (G2b; the residual cleanup work).
- `GET /api/semantic-definitions/projections/profile-violations` — per-primitive list of which §3 profile rule fails (e.g. CF name not snake_case, BF name not BO-scoped, etc.).
- One operational diagnostic surface (`/diagnostics/unique-index-state`): reports the live DB's strict single-column unique index on `contract.canonical_field(field_name)` (verified by Phase 0 as `canonical_field_field_name_key`); distinguishes strict vs composite indexes; surfaces exact-byte duplicate counts (G2a) for transparency. Read-only — no schema introspection writes.

**What Phase 0 explicitly does NOT do:**

- No DDL. No DBCP. No CHECK-constraint changes. No new tables. No `status_code` enum broadening.
- **No `draft → proposed` migration.** That is a governed Phase 1 DBCP write, not a Phase 0 action. Phase 0 only *projects* the new state names for display; the underlying `status_code` column is untouched.
- No certification flow. No `POST /certify`, `/submit-for-review`, `/deprecate`, etc. endpoints. Those land in Phase 1.
- No preflight endpoints. No integration into CC/MC/CM/OC onboarding services. Those land in Phase 2.
- No gate enforcement. No reject of any candidate authoring. No shadow-mode counters yet (counters arrive when gates arrive in Phase 1+).
- No bc-ai integration. AI advisory paths land with the certification flow in Phase 1.
- No contract-row writes anywhere. No registry mutation.

Phase 0 outputs are entirely a **read-side facade** over current registry rows. They make the SDA's intended view of the world visible without touching state. Operators and consumers can build against the projection endpoints; if Phase 1 is later revised, the projection endpoints remain (their shape is API-stable).

**Files touched in Phase 0** (subset of §14's full list):

- `bc-core/src/registry/semantic-definitions/semantic-definitions.controller.ts` (NEW) — read endpoints only
- `bc-core/src/registry/semantic-definitions/semantic-definitions-projection.service.ts` (NEW) — computes projections
- `bc-core/src/registry/semantic-definitions/semantic-definitions.module.ts` (NEW) — module wiring
- (no schema files, no DTO files for write paths, no preflight files, no AI files)

### Phase 1 — CF certification + preflight service (shadow mode)

**Goal:** the SDA can now certify primitives. The certify flow exists. Existing authoring paths still go through `/api/canonical-fields` etc. — no integration yet.

Phase 1 is the first phase with governed write paths. Each write is gated by a DBCP authored at the start of the phase.

**Phase 1 DBCPs (governed, operator-approved writes):**

| DBCP | Scope | Risk |
|---|---|---|
| DBCP-1a | Introduce `master.semantic_family` table seeded with the D366 24-value enum (Q5 — naming convention per existing master tables) | Low — new table, additive |
| DBCP-1b | Broaden `status_code` CHECK constraints on `contract.canonical_field`, `contract.business_field`, `contract.business_object` to accept the 6-state enum (`proposed`, `reviewing`, `certified`, `deprecated`, `superseded`, `withdrawn`); add `is_archived BOOLEAN NOT NULL DEFAULT FALSE` to each + a CHECK that `is_archived = true` only when `status_code ∈ {superseded, withdrawn}` | Med — alters existing tables; backward-compat: old `draft` value temporarily remains valid alongside the new states (drop `draft` from CHECK only after DBCP-1d migration completes) |
| DBCP-1c | Introduce `contract.certification_record` table (per-primitive audit ledger for gate results + AI verdicts + acknowledgements + certifier identity + Cognito sub + role-at-action-time per Q6) | Low — new table, additive |
| DBCP-1d | **Bulk status migration: `UPDATE` all `status_code = 'draft'` rows to `status_code = 'proposed'` across `canonical_field`, `business_field`, `business_object`.** Governed DBCP write; operator-approved; emits change record. Reversible via a paired reverse DBCP that flips the values back if rollback is invoked. **This is a write — not a Phase 0 action.** | Med — touches every existing row; must be transactional per table; verifies row counts before+after; emits a single change record per table with the count + UID range |
| DBCP-1e | Introduce `contract.primitive_supersession` table (per Q3 — central table covering BF/BO/CF supersession chains) | Low — new table, additive |
| DBCP-1f | Introduce `contract.primitive_provenance` table (per Q4 — central append-only provenance; existing per-primitive `source_standard` / `standard_ref` columns remain as a current-projection convenience for backward read compat) | Low — new table, additive |

**Phase 1 implementation work (post-DBCPs):**

- Implement deterministic gates G1, G2a, G2b, G3–G8 (G9 + G10 are reference-time gates — Phase 2)
- Implement bc-ai advisory endpoints (`POST /ai/semantic-definitions/*`) with async-by-default behaviour and `unverified` acknowledgement path (Q8)
- Implement state-transition endpoints: `POST /api/semantic-definitions/{cf|bf|bo}/:id/submit-for-review`, `/certify`, `/return-to-author`, `/withdraw`, `/deprecate`, `/supersede`, `/archive`, `/unarchive`
- Migrate existing `BF /certify` endpoint logic (the 9 gates in `standard-field.service.ts`) into the SDA's gate module, normalising onto G1–G8
- Existing authoring paths (`POST /api/canonical-fields`, `POST /api/business-fields`, etc.) remain available; they internally delegate registration to the SDA so all new rows go through the SDA's `proposed` state by default
- Stand up the SDA-side override mechanic (per Q9 + override matrix §5.5) — rationale + auto-spawned follow-up task only for overridable gates

**Outcome:** operators can certify primitives through the SDA. AI advisory runs asynchronously. Gate results + acknowledgements persisted. **No enforcement yet at reference paths** — that lands in Phase 2.

### Phase 2 — Onboarding integration gates (block mode opt-in)

**Goal:** CC / MC / CM / OC onboarding paths call SDA preflight. Operator opts each integration into block mode tenant-by-tenant or platform-wide.

- Implement preflight endpoints (`POST /api/semantic-definitions/preflight/*`)
- Wire `cc-onboarding.service.ts::addMappings` / `::replaceMapping` to call SDA preflight (G9 + G10)
- Wire `mc-onboarding.service.ts` and MC version activate path to call SDA preflight (G9)
- Wire `mapping-binding.service.ts` (CM authoring) to call SDA preflight (G9 on BFs)
- Wire `oc-onboarding.service.ts` (OC authoring) to call SDA preflight (G9 on BFs)
- Wire `metric-readiness.service.ts::bind` to reject non-certified bind candidates
- Compat-mode controls per-integration: each onboarding path can be in `shadow` (log) or `block` (reject) mode independently

**Outcome:** the authoring perimeter rejects bad new authoring while existing rows remain compatible.

### Phase 3 — Aliases, supersession, deprecation

**Goal:** the SDA supports the full lifecycle including supersession with reference migration.

- Implement `POST /api/semantic-definitions/{cf|bf|bo}/:id/deprecate`, `/supersede`, `/archive`
- Implement alias management endpoints
- Implement reference-migration helpers (a CC mapping with a superseded CF target gets a structured "migration available" projection; the operator-driven migration call repoints to the survivor)
- Migration is not automatic — every reference repoint is an operator action. The SDA surfaces what is needed; the operator drives it.

**Outcome:** the operator can deprecate, supersede, and migrate references in a governed way.

### Phase 4 — Cleanup workflow for existing drift

**Goal:** the platform's existing semantic-base failures (per the audit) flow through the SDA into a cleanup queue, work down through certified state.

- For each top-25 R4 funnel-padding candidate group: per-cluster governing-source review (defensible / duplicate / misclassification); apply the per-cluster remediation through the SDA's certify / deprecate / supersede paths
- For each G2b normalized-form near-duplicate cluster: pick survivor (per Tier-1 design's §3 criteria); deprecate non-survivors; migrate references. (G2a exact byte-identical duplicates: 0 observed in the live DB per the Phase 0 diagnostic; the unique index prevents them. The theoretical G2a class is defined in Tier-1 §2.a for completeness but does not surface as Phase 4 work today.)
- For each non-snake_case CF: G1 violation surfaces in the projection; operator decides rename + supersession plan
- For each NULL `semantic_family`: G5 violation surfaces in the projection; operator populates
- For the 21 shell-CC clusters: out of SDA scope (operator-level ADR work per the audit's Tier-4)

**Outcome:** the audit's findings flow through the SDA into resolution, not through a one-off cleanup script.

## 12. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **R-1: Shadow mode normalises non-compliance** | Med | High | The compat-mode controls are per-integration with operator-visible counters of "shadow rejections that would have blocked." Operator sees the cost of staying in shadow mode. |
| **R-2: AI advisory becomes load-bearing** | Med | High | **bc-ai is never gate-blocking — by config or otherwise.** Deterministic gates (§5) are the only blocking authority. AI verdicts are persisted as advisory evidence on the certification record. A non-green AI verdict (red/amber) or a missing one (`unverified`) requires an explicit **human acknowledgement** with rationale before `reviewing → certified` proceeds — but the acknowledgement is the lock, not the AI verdict itself. There is no operator-configurable knob that promotes AI to a gate. |
| **R-3: Lifecycle migration breaks existing references** | Low | High | Phase 0 inventory + Phase 1 status migration is single-direction (draft → proposed); existing references are not touched. Phase 3 supersession requires explicit operator-driven reference migration, not automatic. |
| **R-4: New tables (semantic_family, certification_record) collide with future schema work** | Low | Med | Names follow D148; DBCPs are individually reviewed; existing tables surface in design Q5. |
| **R-5: Cyclic dependency between SDA and onboarding services** | Med | Med | SDA exposes preflight endpoints; onboarding services call SDA but SDA does not call onboarding services. No cycle. |
| **R-6: Per-CC Meaning-once validation (G10) too slow for bulk authoring** | Med | Med | G10 reads from `cc_field_mapping` group-by; the projection is materialised (`GET /api/semantic-definitions/projection/meaning-once-violations`) and the preflight reads the projection. Bulk authoring goes through the same preflight; the projection refreshes incrementally. |
| **R-7: bc-ai unavailability creates a back-pressure on certifications** | Med | Med | `unverified` verdict path keeps certifications moving with explicit operator audit trail. |
| **R-8: Existing 603 CFs / 373 BFs cannot all be certified in any reasonable time** | High | Low | This is acceptable. Phase 4 is open-ended; the platform operates with most primitives at `proposed` for a long time. New authoring forces certification; existing authoring is grandfathered through compat mode. |
| **R-9: Operator override mechanic erodes the gate** | Med | High | Override requires ≥40-char rationale + auto-spawned follow-up task per D366 pattern. Overrides are queried and operator-visible. |
| **R-10: SDA is yet-another-controller adding surface area** | Med | Low | The alternative is keeping the drift. Compared to leaving every consumer to re-derive semantics, the SDA is a consolidation, not an addition. |

## 13. Rollback / compatibility plan

- **Phase 0 rollback:** none required — read-only endpoints, no state change.
- **Phase 1 rollback:** SDA endpoints remain but unused; existing CF / BF / BO authoring paths still work. The status column broadening + new tables remain; they are additive. Bulk `draft → proposed` migration is reversible (the SDA can flip back via a reverse DBCP — single SQL UPDATE; only allowable in rollback path).
- **Phase 2 rollback:** flip all integrations to shadow mode via `POST /api/semantic-definitions/migration/compat-mode`. Authoring paths revert to current behaviour. No data loss.
- **Phase 3 rollback:** deprecated / superseded primitives remain in their state; references are unaffected (Foundation Invariant III). Rolling forward is the recovery path.
- **Phase 4 rollback:** per-cluster migrations are individually reversible until references are repointed. Once references are repointed, the supersession is the new state of record.

The SDA is **additive** — it does not break existing endpoints. The compat mode flips between observe and enforce; rolling back to observe is the safety valve.

## 14. Files likely touched (no implementation in this design)

| File / Module | Touch type | Phase |
|---|---|---|
| `bc-core/src/registry/semantic-definitions/semantic-definitions.controller.ts` (NEW) | controller — `/api/semantic-definitions/*` routes | P0–P3 |
| `bc-core/src/registry/semantic-definitions/semantic-definitions.service.ts` (NEW) | core service | P1–P3 |
| `bc-core/src/registry/semantic-definitions/semantic-definitions.repository.ts` (NEW) | repo | P1–P3 |
| `bc-core/src/registry/semantic-definitions/semantic-definitions.module.ts` (NEW) | NestJS module wiring | P0 |
| `bc-core/src/registry/semantic-definitions/gates.ts` (NEW) | G1–G10 deterministic gates + override matrix | P1–P2 |
| `bc-core/src/registry/semantic-definitions/semantic-definitions-projection.service.ts` (NEW) | projection endpoints (Phase 0 read-only surface) | P0 |
| `bc-core/src/registry/semantic-definitions/semantic-definitions-preflight.controller.ts` (NEW) | preflight endpoints (G9 + G10) | P2 |
| `bc-core/src/registry/semantic-definitions/semantic-definitions-compat-mode.ts` (NEW) | per-integration shadow/block flags + counters (Q7) | P2 |
| `bc-core/src/registry/canonical-field.service.ts` | modify — delegate to SDA | P1 |
| `bc-core/src/registry/canonical-field.controller.ts` | modify — add certify/deprecate/etc. surfaces by passthrough | P1 |
| `bc-core/src/registry/standard-field.service.ts` (renamed BusinessFieldService) | modify — `certifyField` logic moves into SDA gates module | P1 |
| `bc-core/src/registry/business-object.service.ts` | modify — `approve` becomes `certify` via SDA | P1 |
| `bc-core/src/registry/cc-onboarding.service.ts` | modify — `addMappings`/`replaceMapping` call SDA preflight | P2 |
| `bc-core/src/registry/mc-onboarding.service.ts` | modify — call SDA preflight on variable bindings | P2 |
| `bc-core/src/registry/mapping-binding.service.ts` | modify — call SDA preflight on field_resolutions | P2 |
| `bc-core/src/registry/oc-onboarding.service.ts` | modify — call SDA preflight on field_selection | P2 |
| `bc-core/src/registry/contract.service.ts` | modify — MC version activate calls SDA preflight | P2 |
| `bc-core/src/registry/metric-readiness.service.ts` | modify — `bind` calls SDA preflight; reads SDA projection | P2 |
| `bc-core/src/registry/chain-status.service.ts` | modify — read SDA projection for L1/L2/L3/L7 | P2 |
| `bc-core/src/registry/formula-audit.service.ts` | modify — read SDA projection rather than re-derive | P2 |
| `bc-core/src/database/schema/contract/canonical-field.ts` | DDL — broaden status enum, add `semantic_family` CHECK | P1 (DBCP) |
| `bc-core/src/database/schema/contract/business-field.ts` | DDL — broaden status enum | P1 (DBCP) |
| `bc-core/src/database/schema/contract/business-object.ts` | DDL — broaden status enum | P1 (DBCP) |
| `bc-core/src/database/schema/contract/certification-record.ts` (NEW) | DDL — new table | P1 (DBCP) |
| `bc-core/src/database/schema/master/semantic-family.ts` (NEW) | DDL — new master table | P1 (DBCP) |
| `bc-core/src/database/schema/contract/vocabulary-name-alias.ts` (NEW) | DDL — `contract.vocabulary_name_alias` (Q2) | P3 (DBCP-3a) |
| `bc-core/src/database/schema/contract/primitive-supersession.ts` (NEW) | DDL — `contract.primitive_supersession` (Q3) | P1 (DBCP-1e) |
| `bc-core/src/database/schema/contract/primitive-provenance.ts` (NEW) | DDL — `contract.primitive_provenance` (Q4) | P1 (DBCP-1f) |
| `bc-ai/semantic_definitions/*` (NEW) | bc-ai service for advisory verdicts (async by default per Q8) | P1 |
| `bc-admin/src/pages/SemanticAuthority/*` (NEW) | UI for certification queue, projections, override flow | P1–P3 |
| `bc-docs-v3/docs/onboarding/canonical-field-seeding.md` | UPDATE — point at SDA endpoints; reconcile with C1 lifecycle resolution | P1 |
| `bc-docs-v3/docs/onboarding/business-field-and-business-object-onboarding.md` | UPDATE — reconcile lifecycle with C1 | P1 |
| `bc-docs-v3/docs/operating-model/business-vocabulary.md` | UPDATE — reflect SDA endpoint discipline | P1 |
| `bc-docs-v3/docs/adrs/ADR-{new-uid}.md` (NEW) | Semantic Definitions Authority ADR — supersedes/amends DEC-5017fe, DEC-d72560 on lifecycle topics | P1 |
| `bc-qa` audit rules | new checks for SDA gate compliance | P2–P3 |

**No implementation in this design.** Each file is a likely touch point; the actual surface set is finalised per phase when implementation is approved.

## 15. Non-decisions

This design does NOT:

- File any ADR. (`devhub_decision_record` not called.)
- File any DevHub task. (No `devhub_task_add` calls.)
- Author any DBCP. (DBCP shapes named in §9; DDL not written.)
- Author any DTO, endpoint stub, controller, service, or repository implementation.
- Mutate any contract registry row (no CF / BF / BO state changes).
- Run any reader, evaluation, chain refresh, or tenant-binding action.
- Use `pg_query` writes (read-only used only in audit; not in this design).
- Re-litigate the Q1–Q10 settled decisions (those are recorded in §10 as decision-locked for R2/R3; revision requires a new revision pass, not a non-decision).
- Author any per-CF, per-BF, per-BO certification action.
- Choose the survivor for any duplicate cluster (that work lives in the Tier-1 design and downstream).
- Author the new ADR text that supersedes DEC-5017fe / DEC-d72560 on lifecycle (proposed in §C1; ADR drafting is a separate act).
- Propose a specific compat-mode rollout schedule (Phase 2 controls left to operator).

## 16. Stop conditions encountered

Per the operator's stop conditions:

- **Doc conflicts found:** C1 (three lifecycles), C2 (BF vs Standard Field naming), C3 (CF uniqueness drift), C4 (CF naming standard scope), C5 (semantic_family enum not enforced), C6 (reference-time certification absent). Each is named with proposed resolution; **none invented silently.**
- **Implementation drift found:**
  - canonical-field.service.ts admits any string, no name validation, no certify path
  - canonical_field schema has `uniqueIndex` declared but audit found duplicates — verification needed in Phase 0
  - business-vocabulary.md prescribes 5-state lifecycle; BF service implements 2-state; CF service implements 1-state; DDL CHECK is 3-state
  - DEC-d72560 §Risks names "MC validation gate checks CF status" — not implemented
  - business-field-and-business-object-onboarding.md §BO Approval Gate says "All BFs certified" — confirmed enforced; the chapter also implies CF certification at CC reference time — not enforced
- **DB write or tenant action required:** none — this is a design document. Phase 1 onward will require DBCPs; the design names them but does not author them.

## 17. State of play — 2026-05-12 PM (R2)

The directional acceptance + seven patches + Q1–Q10 defaults applied. Settled:

- **C1–C6 resolutions:** directionally accepted; refinements applied per Patches 1–7.
- **Q1–Q10:** settled per §10.
- **5-phase rollout:** confirmed.
- **ADR shape:** single umbrella SDA ADR + DBCPs + per-phase implementation MWRs (Q10).
- **Phase 0:** **authorised** to proceed as a separate read-only implementation slice — projections only, no DDL, no status migration, no enforcement, no preflight gates. Per Patch 6 the `draft → proposed` migration is **Phase 1 DBCP-1d**, not Phase 0.

What remains before Phase 0 implementation begins:

- **(a)** Operator confirms this R2 patched design reads correctly end-to-end (one final pass over §C, §4, §5 (G2a/G2b/G9/G10), §5.5 override matrix, §6 AI handling, §10 settled decisions, §11 Phase 0 / Phase 1).
- **(b)** Operator confirms whether Phase 0 implementation begins **now** (new session, scoped implementation slice) or stays **paper-only** longer pending umbrella ADR draft + DBCP authoring sequence.
- **(c)** Once Phase 0 implementation is authorised to begin: a new session opens, a Phase 0 plan is saved, the `/api/semantic-definitions/*` controller + projection service are authored as additive read-only files. Existing tables and rows untouched.

## 18. Evidence

| Source | Used for |
|---|---|
| DEC-69f09e ([ADR-69f09e.md](../../../../../governance/adrs/ADR-69f09e.md)) | Naming standard scope and case discipline (P1 profile) |
| DEC-5017fe ([ADR-5017fe.md](../../../../../governance/adrs/ADR-5017fe.md)) | Standard Field Registry — ISO 11179 MDR alignment, two-tier model |
| DEC-d72560 ([ADR-d72560.md](../../../../../governance/adrs/ADR-d72560.md)) | CF as 3rd primitive, two-vocabulary model, CC as translator |
| [business-vocabulary.md](../../../../../operating-model/business-vocabulary.md) | 5-state lifecycle (C1 authoritative source), BO-scoping rule, five shared dimensions |
| [canonical-field-seeding.md](../../../../../onboarding/canonical-field-seeding.md) | CF naming rules (Profile P3), demand-driven CF authoring, quality checks (uniqueness post-hoc) |
| [business-field-and-business-object-onboarding.md](../../../../../onboarding/business-field-and-business-object-onboarding.md) | BF certification gate (9 gates → SDA G1–G8), BO approval gate, BF-to-source alias procedure |
| Audit MWR ([2026-05-12-semantic-base-audit-SES-a223ea.md](../../../../audits/onboarding/2026-05-12-semantic-base-audit-SES-a223ea.md)) | Headline drift evidence: 603 draft CFs, 122 non-snake_case, 144 R4 candidates, 21 shell CCs |
| Tier-1 design MWR ([2026-05-12-tier1-cf-certification-design-SES-a223ea.md](2026-05-12-tier1-cf-certification-design-SES-a223ea.md)) | Earlier narrower design absorbed by §3 (Profile P3), §4 (lifecycle), §10 (settled decisions), §11 Phase 4 (cleanup) |
| `bc-core/src/registry/canonical-field.controller.ts` + `.service.ts` + `.repository.ts` | Confirmed: no certify flow, no name validation, batch onConflictDoNothing keyed on fieldName |
| `bc-core/src/registry/standard-field.service.ts` | Confirmed: binary BF lifecycle, 9 gates implemented at certify; would inform SDA G1–G8 |
| `bc-core/src/registry/cc-onboarding.service.ts` | Confirmed: BO status checked (`statusCode === 'approved'`); CF status NOT checked; replaceMapping does not check CF certification |
| `bc-core/src/registry/mc-onboarding.service.ts` | Confirmed: CF existence checked via `findByName`; status NOT checked |
| `bc-core/src/database/schema/contract/canonical-field.ts` | Drizzle schema: `uniqueIndex('uq_canonical_field__name')`, CHECK `status_code IN ('draft','certified','deprecated')`, `semantic_family` column with code-comment closed enum (D366) — uncontrolled |

## 19. Closing note

The Semantic Definitions Authority is not a new philosophy — it is the **enforcement layer** that the existing governance (DEC-69f09e, DEC-5017fe, DEC-d72560, business-vocabulary.md) has always implied but never had. The audit confirmed that without a standing enforcement layer, vocabulary drift is mathematically inevitable: 100% of CFs draft, 122 non-snake_case, 144 R4 candidates. The SDA closes this gap by:

1. **Reconciling** the conflicting governance into one lifecycle (C1) and one set of profiles (§3).
2. **Owning** the certification act + record per primitive — no other service mutates state without going through the SDA.
3. **Enforcing** deterministic gates at every authoring path's reference time, not just at primitive registration.
4. **Admitting AI as advisory** with explicit audit trail and operator-override discipline — never as autonomous certification authority.
5. **Emitting projections** that readiness / chain-status / formula-audit / tenant-binding consume directly — eliminating independent re-derivation of semantics.

The design is decision-pending. Operator confirmation on §C resolutions and §10 questions gates the start of Phase 0.
