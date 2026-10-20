---
uid: DEC-4aa1ff
title: "Canonical legal-entity identity: a platform-minted LE id is the partition axis of the object progression; source company keys are confirmed cross-references; identity is declared at tenant onboarding and realized at source onboarding"
description: "Executes DEC-c05551 B1's deferred opaque-LE-id migration; declared→realized LE lifecycle; the DEC-bacbf5 mapping becomes the xref to the canonical id; attribute survivorship; LE as an explicit evaluation partition (fixes the tenant-wide D-7 assertion); raw-key LE references banned; amends DEC-c05551, DEC-bacbf5, DEC-103acb and the DEC-fa7c63 D-7 enforcement."
status: proposed
date: 2026-10-20T05:05:30.854Z
project: bc-core
domain: tenants
subdomain: tenant-dim/legal-entity
focus: identity-resolution
amends:
  - DEC-c05551
  - DEC-bacbf5
  - DEC-103acb
  - DEC-fa7c63
---

# Canonical legal-entity identity: a platform-minted LE id is the partition axis of the object progression; source company keys are confirmed cross-references; identity is declared at tenant onboarding and realized at source onboarding

## Context

ADR-c05551 and ADR-bacbf5 already decide the separation of LE identity from source keys, the many-to-one binding and tenant ≠ LE. What remains open is the identity form (B1 was deferred: a free-text tenant label is still the PK), the point where identity is established, attribute survivorship, and above all the partition. Evaluation today is a de-facto tenant=LE, because checkScopeEntity refuses any multi-LE tenant, and the scheduler still uses '*'. Minting a platform id, realizing it against source evidence, keeping source keys as confirmed xrefs and making the LE the explicit partition axis closes these gaps with declarations, not resolver patches. That is consistent with the ERP/MDM practice the operator cited and with Invariants I–VI.

## Grounding (2026-10-20, bc-core and bc-docs origin/main, platform DB read-only; no tenant read)

**Operator thesis, via the Chief, with ERP/MDM research:**
1. A tenant owns a set of legal entities (LEs).
2. An LE's identifier lives in the source system, so tenant onboarding should carry a display name and intent, not a free-text identity.
3. The same real-world LE in several sources (Odoo, SFDC) must reconcile to one canonical LE: first source wins, later sources are mapped.
4. The design should follow how ERP and MDM systems do it.
5. The whole progression (observe, admit, evaluate, CO, metric snapshot) repeats per LE, so canonical-LE identity is the **partition axis**, not a side dimension.

The research's core finding: a source-agnostic platform mints its own canonical LE id and treats every source id as a cross-reference.

**Already decided (not re-decided here):**
- **DEC-c05551:** LE identity is canonical and separate from any source key. A governed, versioned, many-to-one source→entity binding is applied at the canonical boundary, and an unbound key is refused, never wildcarded.
- **DEC-bacbf5:**
  - D1: a tenant is not an LE (one or more per tenant), and LE declarations carry no source identifiers.
  - D2: a connection belongs to exactly one tenant.
  - D3: the mapping is keyed on an immutable key domain plus `connection_id`, in value_keyed or connection_scoped shape.
  - D4: a source-onboarding completeness predicate.
- **DEC-ea4523:** no `'*'` LE.
- **DEC-7a8cbc:** binding-realized issuer identity.
- **Most of the research model is therefore already doctrine.**

**Gaps found:**
- **G1. Identity equals a tenant-typed label.** `tenant_dim.dim_legal_entity.legal_entity_code` (free text typed at tenant onboarding, e.g. `KAVERI-IN`) is the primary key and the join key for `tax_registration`, `organization.fiscal_calendar_config`, the binding target, CO LE values and the metric scope. DEC-c05551 **B1 explicitly deferred** the opaque-id migration to "a later, separately-reviewed identity migration" that must define the key transition, every FK/reference/evidence surface, historical-query semantics and rollback. This ADR is that proposal.
- **G2. Identity is established at tenant onboarding.** DEC-bacbf5 D1 and DEC-103acb require an LE to be declared at tenant onboarding, and that declaration *is* the identity. No source evidence is ever required for an LE to exist.
- **G3. No attribute survivorship.** Legal name, registration and tax id carry no source provenance. Multi-source attribute conflicts have no rule.
- **G4. Evaluation is not LE-partitioned.** `co-candidate-reader.ts` `checkScopeEntity` reads every CO of the grain for the tenant and **refuses the whole evaluation** if any CO belongs to another LE. That is DEC-fa7c63 D-7 ("scope: one legal entity E") enforced as a tenant-wide assertion, so a tenant with two LEs on one grain can be evaluated for neither. It contradicts DEC-bacbf5 D1. In addition, `runtime-scheduler.service.ts` defaults `legalEntityCode` to `'*'` (env `BC_SCHEDULE_LEGAL_ENTITY`), contrary to DEC-ea4523.
- **G5. Raw source keys used as the LE reference (Inv-IV):**
  - OC field mappings put `company_id` straight onto the LE reference: oc-3kgrr 1.1.0/1.2.0/1.3.0, oc-jbpz8 1.0.0/1.1.0, oc-c0q9s 1.0.0.
  - The SAP provenance-bound bukrs fiscal route (DEC-ea4523) uses the source company code as the LE code. It is the "degenerate case" DEC-c05551 point 5 tolerated.
  - TSK-1ec1a7 already rules the OC/CC pair fix and a fiscal-LE gate for cc-das36 and cc-7174p.

## Decision

**D1. Canonical LE identity is platform-minted and opaque.**
- Each LE gets an opaque, immutable, never-reused identifier (D560 doctrine, e.g. `LE-xxxxxx`). It is minted by a governed writer and is never derived from a source key, a tax id or the tenant's label.
- `legal_entity_code` becomes a tenant **label**, unique per tenant **and never reused**, changeable only by a governed rename event that never changes the id.
- **Hinge-phase freeze (Codex gen-c02c55-01, finding 1).** Until a tenant's D9 cutover, `legal_entity_code` **is** the key: tenant-DB xrefs FK to it (bc-db tenant/0002), and COs, calendars, tax registrations and metric scope carry it. So during that phase:
  - **`legal_entity_code` is immutable.** A rename is refused (`422 refusal_code: legal_entity_code_locked_until_cutover`). Only `display_name` and `intent_text` may be revised.
  - **Code renames unlock only after cutover,** when the immutable canonical id and the D9 alias semantics exist.
- Display name, country, functional currency and the optional registration, tax id and LEI are **attributes** with recorded provenance (D4).
- Every reference to an LE (FKs, CO LE fields, fiscal calendar, tax registration, xref, metric scope, snapshots, evidence) uses the canonical id.

**D2. Lifecycle: declared at tenant onboarding, realized at source onboarding.**
- **Tenant onboarding records an LE *declaration*:** display name and intent (for example "the Indian operating company"), optional identifiers, functional currency and the fiscal-calendar intent. The governed writer mints the canonical id **in state `declared`**, so the calendar and tax configuration attach to a stable id from the start and nothing is re-keyed later. A declaration carries **no source identifier** (DEC-bacbf5 D1 kept) and is **not an authoritative identification**.
- **Source onboarding realizes it.**
  - The connection's entity master is *discovered* as evidence: Odoo `res.company`, SAP company codes, SFDC legal entity, a QuickBooks realm.
  - Each discovered source entity is disposed by **one explicit, confirmed, governed act** with an actor and a rationale. It either:
    - (a) adds an xref to an existing canonical LE; or
    - (b) fulfils an open declaration, moving the LE `declared → realized`; or
    - (c) creates a new LE, realized at birth, for an entity found only in the source.
  - The platform may *propose* matches (equal registration or tax id, name similarity) **as evidence only**. **It never infers a mapping.**
- **Only a `realized` LE can be evaluated.**
- **Inv-VI records (Codex gen-c02c55-01).** Each of these emits its own governed record:
  - the declaration;
  - each S7 confirmation;
  - the `declared → realized` transition;
  - each readiness result.

  Proposed matches remain evidence only.
- **`exclude` disposition** (a dormant or foreign source entity):
  - creates **no** xref;
  - every future record carrying that key is still refused at canonical realization (`unresolved_source_binding`);
  - it counts as *dispositioned* in coverage but **never** as *mapped*.

**D3. The cross-reference is the DEC-bacbf5 mapping, retargeted to the canonical id.**
- The xref is the existing two-step key-domain declaration plus mapping revision: `(connection_id, key_domain, source_key_value) → canonical LE id`. It is immutable, as-of, exactly-one, with governance events and lineage (DEC-c05551 B3).
- One canonical LE has many xrefs: across connections and source systems, and many source companies to one LE.
- Cross-source reconciliation (Odoo company 1 and SFDC account X are the same LE) is the D2(a) confirmed act on the second source.
- **The first source to realize an LE does not own the identity.** The platform owns it. "First-source-wins" applies to attributes only (D4).
- **One server-side binding invariant for every writer (Codex gen-c02c55-01, finding 2).**
  - **The confirmed lane:** every mapping revision records its `writer_lane_code`.
    - **`confirmed_disposition`** is written only by the S7 disposition service. It references the candidate and its disposition event, and it is the **only** lane that can move an LE `declared → realized` or count as **mapped** coverage.
  - **The legacy lane:** **`legacy_direct`** is the existing `POST key-domains/:keyDomainId/bindings`. It is kept so current label-key tenants and the prove-on-one keep working.
    - It is restricted to `operator` and `platform_admin`; `tenant_admin` is removed.
    - It requires a ≥40-character rationale.
    - It **cannot realize an LE, cannot create one, and never counts toward candidate coverage or D8 readiness.**
    - Its rows stay valid for canonical **resolution**, with DEC-c05551 B3 lineage, so existing evaluation is unchanged.
    - Existing bindings are grandfathered as `legacy_direct`.
  - **Enforcement is server-side, not UI-only:**
    - a sole-writer architecture test: only the disposition service and the legacy-lane service may call the DB binding writer (the `source-identity.sole-writer.spec.ts` pattern);
    - the lane is derived by the service, never taken from the request body;
    - a direct-call bypass test: a legacy-lane write leaves the LE `declared` and its coverage unchanged.

**D4. Attribute survivorship.**
- Source-supplied legal attributes (legal name, registration, tax id) **survive from the first realizing xref**, with lineage naming that xref.
- Tenant-declared attributes (display name, intent) are declarations and govern display.
- A later source's differing value is **recorded as an attribute observation and surfaced as a data-quality signal**, never overwritten and never buried.
- An attribute change is a new attribute revision (Inv-III). Changing the surviving value is a governed act.

**D5. The LE is the explicit partition axis of the object progression.**
- Every CO of an LE-bearing CC (fiscal, or carrying an issuing or recording LE reference) carries **exactly one canonical LE id**, realized through the declared binding derivation. An unbound or unresolved CO is refused, never wildcarded.
- An LE-scoped evaluation **selects the partition**: the COs whose LE is E. It does not assert that the tenant has a single LE. DEC-fa7c63 D-7's meaning ("one legal entity E") is unchanged; only its enforcement changes. Unbound COs and composite operand mismatches (E, currency, calendar, T) still refuse.
- Fiscal periods, metric snapshots, evidence and the portal LE filter are keyed by the canonical id.
- Scheduled campaigns iterate the tenant's **realized** LEs. The `'*'` scheduler default is removed.
- Cross-LE aggregation (consolidation, eliminations) is out of scope. It will be a declared consolidation entity in a follow-on ADR, never an implicit cross-partition sum.

**D6. Reorganizations and non-1:1 sources.**
- An LE is never merged, split or re-identified in place. Mergers, splits and re-domiciliations are effective-dated **supersession events** with successor ids. Xref revisions are effective-dated, and history keeps its original LE (Inv-III, Inv-V).
- **One source key → many LEs** (for example SAP shared-services codes) cannot be resolved per record. It needs a finer declared key domain (segment or profit centre) or it is a recorded refusal. It is never guessed.
- **Many keys → one LE** is native (D3).
- **A source with no natural company key** uses DEC-bacbf5's `connection_scoped` shape with a human-confirmed mapping.

**D7. No raw source key is ever an LE reference (Inv-IV).**
- No OC may map a source company key directly as the LE reference. Resolution happens only through the declared xref derivation (`resolve_source_entity_binding`).
- The SAP bukrs special route retires: bukrs becomes the key value of a value_keyed key domain.
- The fiscal-LE gate (TSK-1ec1a7 amendment 1) generalizes to: *"an LE-bearing CC resolves each CO to a canonical LE id through exactly one declared xref derivation."* The SAP alternative branch is removed when bukrs is xref'd.

**D8. Completeness and readiness (amends DEC-103acb and DEC-bacbf5 D4).**
- **Tenant-onboarding completeness:** at least one LE *declared*, each with its fiscal calendar.
- **Evaluation readiness per LE:** realized, calendar in force, and every entitled source key on every feeding connection xref'd (the DEC-bacbf5 D4 predicate, now per LE).
- Birth ends in `onboarding_incomplete` (bc-db 0034 + the birth/activation split, TSK-49f8d8). Readiness is a computed, recorded result, never a controller's read (Inv-VI).

**D9. Migration contract (DEC-c05551 B1; Codex gen-c02c55-01, the D9 finding). DEFERRED program; no part starts until a reviewed D9 successor at a pinned head.**

- **D9.1 Identity discriminator (persisted, never inferred).** Every LE-bearing persisted value carries its key form explicitly, as `legal_entity_key_form_code` ∈ {`label_v1`, `canonical_id_v1`}:
  - **Contract-produced facts** (CO fact tables, metric snapshot tables): declared **per contract version** in the CC/MC body header. A fact table is wholly one form, because a form change is a new major version and a new table.
  - **Tenant skeleton rows** (xref/mapping revisions, binding-selection lineage, calendar revisions, tax registrations, attribute families, evidence/proof-scope rows): a `legal_entity_key_form_code` column, added by a bc-db tenant migration, stamped at write.
- **D9.2 Immutable old-code lookup.** A new append-only `tenant_dim.legal_entity_code_alias`:
  - columns: `legal_entity_code`, `legal_entity_id`, `valid_from`, `valid_to`, `reason_code` ∈ {`cutover`, `rename`}, governance event;
  - one row per code at cutover and per later rename;
  - **codes are never reused within a tenant**, even after a rename (a unique constraint over the alias history);
  - so any old `label_v1` value resolves deterministically to exactly one `legal_entity_id` for the time it was written.
- **D9.3 Mixed-history query rule.** A read spanning both forms resolves **every row to `legal_entity_id`**:
  - `canonical_id_v1` rows directly;
  - `label_v1` rows via the alias **as-of the row's recorded time** (`recorded_at`; for COs, the evaluation's `recorded_at`).

  Then:
  - results group and filter by `legal_entity_id` and display the current label;
  - old rows are never rewritten;
  - **snapshot ↔ CO ↔ binding-lineage joins** go through `legal_entity_id` after resolution;
  - a row whose code has no alias is a recorded read refusal (`unresolved_legal_entity_alias`), never a guess.
- **D9.4 Cutover point (per tenant, a governed event).** `le_identity_cutover` is a recorded act per tenant. In one transaction, with lineage, it:
  - mints canonical ids for each declared or realized LE (the label tenant's LEs);
  - writes the `cutover` aliases;
  - re-points the tenant-skeleton FKs, by adding the id columns and keeping the code columns as immutable aliases;
  - stamps the tenant's form as `canonical_id_v1`.

  From then on:
  - only `canonical_id_v1` CC/MC versions activate for the tenant;
  - code renames unlock (D1);
  - new tenants are **born cut over** (no code-form history);
  - existing tenants, including `kaveri`, are cut over **only** by an explicit governed act, otherwise never.
- **D9.5 Rollback and recovery limits, per surface:**

  | Surface | Before cutover | After cutover |
  |---|---|---|
  | `dim_legal_entity`, `legal_entity_code_alias` | **Full rollback:** drop the unused additions (nothing references them) | No rollback. Aliases are permanent (Inv-III); recovery is a forward rename or supersession event |
  | Tenant-skeleton FKs (calendar, tax registration, attribute families, xref, lineage) | Full rollback (the id columns are unused) | Code columns kept as aliases, so readers can resolve by alias, but **writes stay on id**. No return to code-keyed writes |
  | CO facts and metric snapshots | n/a (they stay `label_v1` tables) | `canonical_id_v1` tables are immutable; recovery is a corrective new major version. Old `label_v1` tables stay readable through D9.3 |
  | Evidence and proof-scope rows | Unchanged | Stamped with form; read via D9.3 |
  | Portal filter, scheduler, partition selection | Read label | Read id, display the current label |

- **D9.6 Execution order** (each its own reviewed unit):
  1. the D9 successor design;
  2. the bc-db tenant migrations (alias table, form columns, id columns; operator DB yes each; never `fact.*`, TSK-4d297e);
  3. the engine (resolver form stamping, D9.3 reads, the cutover service);
  4. new major CC/MC versions in `canonical_id_v1`;
  5. a fresh greenfield tenant born cut over;
  6. bukrs retirement into the xref (operator decision 5).

## Knock-ons

- **(a) D3 / tenant onboarding:** reshaped as in D2 and D8. Intent and calendar are captured at tenant onboarding; identity is realized, with evidence, at source onboarding.
- **(b) The fiscal-LE gate:** generalizes as in D7. The rule is "resolve to the canonical LE via the xref", and the mechanism is the same derivation.
- **(c) The cc-das36 instance fix survives unchanged in shape.** It is oc-3kgrr 1.4.0 (drop the direct `company_id` LE mapping) plus cc-das36 3.0.0 (declare `resolve_source_entity_binding`), which is exactly the single-source case of this model. Under D9 only the *value* the derivation emits (label → canonical id) changes, and that comes with its own major CC version.
- **(d) CC-version ↔ tenant fan-out.** It is acceptable for **provisioning**: per-tenant fact tables are idempotent, empty and cheap. It becomes a smell only if provisioning or activation is read as **evaluability**. Evaluability must be the per-tenant, per-LE readiness of D8, so a global CC activation never implies that any tenant or LE can evaluate. The one real hazard in the fan-out is version regression (an older `pending_provisioning` version activating late), which the readiness newer-version guard closes. That guard is load-bearing (TSK-1ec1a7).

## Foundation (DEC-79b62f)

**Four questions:**
1. **Location: B**, what an LE identity is, where it is established and how attributes survive; **with C**, the xref binding. The partition selection is the D-layer execution of a declaration made at B.
2. **Not upper:** the sources are correct. Their entity masters are **evidence of** an LE, not its identity.
3. **Not lower:** the tenant-wide scope assertion, the `'*'` scheduler default and the bukrs route are lower-layer stand-ins for an undeclared partition and an undeclared identity. They are replaced by declarations, not patched in the resolver.
4. **Design act:** identity, lifecycle, survivorship and partition are all declared here. Every migration and engine change is a separately reviewed execution act.

**Invariants:**
- **I:** an LE's identity and attribute meaning are decided once, at their governed acts.
- **II:** the canonical id fixes the partition, and the progression order is unchanged.
- **III:** ids are never reused; attributes, xrefs and reorganizations are revisions or supersessions; history is never re-keyed.
- **IV:** every LE reference is an explicit, binding-realized canonical id, and raw-key references are banned.
- **V:** evaluations are per-LE fresh acts, never re-pointed.
- **VI:** realization, xref, survivorship conflicts and readiness are emitted records.

## Operator decisions: adopted 2026-10-20

**Provenance, stated plainly:** the operator adopted all five decisions on 2026-10-20. The Chief Controller relayed this from the operator's chat (SES-1e49e0). **A recorded, byte-bound desk grant is requested alongside this revision.** That grant, not the relay, is the authority this ADR cites. The ADR stays `proposed` until the Codex design review **and** the operator's terms gate (a recorded grant on the final bytes).

1. **Adopted.** A platform-minted opaque canonical LE id (D1), for **new tenants**. This executes DEC-c05551 B1's deferral.
2. **Adopted.** Mint at declaration: `declared → realized` (D2).
3. **Adopted.** Survivorship as D4: the first realizing source supplies legal attributes, the tenant declaration supplies display, and conflicts are surfaced and never overwritten.
4. **Adopted. Sequencing:**
   - **The cc-das36 instance fix and the prove-on-one resume now on the current label key.** That key is still governed by DEC-c05551 B1, and the fix is model-invariant (knock-on c).
   - **The opaque-id migration (D9) is DEFERRED** to its own later program, on new major CC versions and a fresh tenant.
5. **Adopted.** The SAP bukrs special route retires into the uniform xref **at migration** (D7). It is part of the deferred D9 program and does not apply now.

**D10. Per-LE attributes are extensible and governed** (operator requirement, 2026-10-20; detailed in the interface lock §1A).
- **The core LE stays minimal:** id, label, lifecycle state, xrefs and calendars. Nothing is ever added to it.
- **Every descriptive field is an LE attribute,** stored in typed, normalized, **append-only attribute-family revision tables** (at most 20 columns each; no JSONB, no EAV; DB rules 1 and 6):
  - `legal_entity_profile_revision` (single-valued): country, functional currency, posture, `reporting_standard_code`, LEI, legal name, registration number;
  - the existing multi-valued, effective-dated **`tax_registration`** (DEC-9c430b/D503), re-keyed to the canonical id.
- **Meaning:** each attribute is a published BCF concept on the Legal Entity entity (3bd1857e).
- **Binding:** one platform **attribute registry** row binds the concept to its family and column, cardinality, value domain (master | closed set | typed), `inherits_from`, completeness `required_rule` and provenance policy.
- **Adding an attribute** = a BCF concept + a bc-db tenant skeleton migration + a registry row.
  - Nothing changes in the API, UI or engine for **storage, validation, display and readiness**.
  - A **metric** that uses the attribute still declares its own metric semantics.
  - Registry publication checks schema, type, domain parity and as-of provenance at its own implementation gate.
  - `tax_registration` stays an instance (multi-valued) family.
- **Metrics** read attributes as-of through the LE partition key (the fiscal-calendar precedent), never copied into COs.
- **Reconciliation with ADR-103acb:**
  - `org_profile` stays tenant-level, and its `reporting_standard` is the default that `reporting_standard_code` (D2's deferred per-LE override) inherits.
  - The D1 per-LE mandatory fields and the D5 conditional tax rule become registry required rules.
  - `dim_legal_entity.fiscal_calendar_code` is retired (one source of truth: the calendar revisions).

**D11. Two planes: which surface owns each act** (operator refinement, 2026-10-20; a surface and ownership assignment, **not** a model change).
- **Platform plane: bc-admin (`platform_admin` / `operator`).** It does only minimal tenant provisioning:
  - register the tenant shell (P1: a served registration request that the owner-plane `tenant:lifecycle` birth executes; the served `POST /tenants` stays refused by design);
  - create the tenant admin user (P3: the existing `POST /api/admin/users`, DEC-42b9c0);
  - activate the tenant (P2: the governed activation act, refused unless the newest recorded completeness result is complete; 0034, TSK-49f8d8);
  - the technical part of source onboarding: connection, owning tenant, key domains, contract-tuple declarations;
  - the `legacy_direct` binding lane.
- **Tenant plane: the tenant app, bc-portal (`tenant_admin`, tenant-scoped).** It owns:
  - LE declaration (D2's "tenant onboarding" means onboarding **in the tenant app**, after the platform provisions the shell and admin user);
  - attributes (D10), calendars, readiness, and the tenant's completeness view;
  - by default, **realization**: discover, review and dispose candidates (S5–S8), and retire xrefs.
- **Open with the operator:** self-service realization (the default above) vs platform-assisted (S5–S8 in bc-admin, an operator acting for the tenant). The contracts are identical; only the rendering portal and the S7/S8 role change.
- **The tenant app must work while `onboarding_incomplete`** for the onboarding acts. Otherwise onboarding deadlocks: no LEs without activation, no activation without LEs. Evaluation-bearing features stay gated by per-LE readiness (D8).

**Boundary from Codex gen-c02c55-02 (folded).** `legacy_direct` rows stay valid for canonical resolution but never count toward D8 readiness. The now-track readiness and service review must prove two cases:
- (a) a legacy row never passes the new readiness gate as mapped coverage, consistent with DEC-bacbf5 D4's witnessed coverage;
- (b) the separately authorized label-key prove-on-one (kaveridemo2) is not regressed. It runs under the existing gates (binding resolution plus the fiscal-LE gate), not the new D8 readiness, until its LEs are realized through S7 or explicitly grandfathered by a recorded act.

The D9 successor must also settle physical old-row timestamps and the alias-interval mechanics (an interval end is derived or recorded **without updating a sealed row**), and prove cross-form CO/snapshot/lineage queries and missing-alias refusal before any cutover.

**Interface (locked for parallel build):** barecount-devhub `artifacts/architect/INTERFACE-LOCK-le-identity-tenants-menu-2026-10-20.md` at commit `7c5a01cd` (sha256 `eb338f07…`, PR #299; rev 4: rev 3, which Codex accepted with boundary in gen-c02c55-02, plus the D11 two-plane split). It contains the entity model, the governed-service API contracts (T1–T3, C1–C2, L1–L11, A1–A3, S1–S8) and the bc-admin Tenants-menu IA. Every shape carries `legal_entity_id`. **Only S7 (the `confirmed_disposition` lane) can realize an LE or count as mapped coverage.** The `legacy_direct` lane is restricted as in D3. Proposed matches are evidence only. **`legal_entity_code` is frozen until cutover** (D1).

**Next:**
1. A Codex design review (full depth, platform lane) of this ADR and the interface lock.
2. The operator's terms gate (a recorded grant on the final bytes).
3. Separately reviewed execution units, none of which runs before step 2:
   - **Now-track, on the label key:**
     - Platform: the G4 partition-selection fix, the `'*'` scheduler removal, the readiness newer-version guard and the generalized fiscal-LE gate (TSK-1ec1a7);
     - the governed services behind the interface, built on the label key under the interface's hinge (`legal_entity_id` = `legal_entity_code` until D9): declaration, source-entity discovery and candidates, S7 disposition (the xref), and the D10 attribute registry plus families (operator DB yes per migration);
     - DB: 0034 + the birth/activation split (TSK-49f8d8).
   - **Deferred program (D9):** the opaque-id mint and re-key (`dim_legal_entity`, families, xref, calendars, tax registration, CO LE values on new major CC versions), bukrs retirement, and a fresh tenant.
