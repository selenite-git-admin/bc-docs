---
id: privacy-and-the-immutable-fact
order: 49
title: "Privacy and the Immutable Fact"
status: drafting
authority: authoritative
depends_on: [the-authority-model, the-object-model, the-invariants, evidence-and-lineage, audit-and-activity-logging, infosec-and-access-control]
governing_sources:
  - The Authority Model
  - The Object Model
  - The Invariants
  - Evidence and Lineage
  - Audit and Activity Logging
governing_adrs:
  - DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object; sentinel-based privacy erasure for the immutable-fact platform; PII registry, nullification request, nullification action, DSAR response, retention policy schema)
  - DEC-1918d0 (Two-database split; the platform DB versus per-tenant DB topology that the nullification mechanism acts against)
  - DEC-771baf (Tenant database topology; per-tenant DB schemas the nullification engine traverses)
  - DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria; Privacy is excluded from the Type I scope)
errata_referenced: []
v2_sources: []
diagrams: []
---

# Privacy and the Immutable Fact

## Scope

This chapter records the platform's privacy posture and the resolution of the apparent tension between Foundation Invariant III (authoritative objects are immutable and append-only) and the right-to-be-forgotten obligations of GDPR, India's DPDP Act 2023, and California's CCPA. It states the sentinel-based nullification mechanism per `DEC-bd5492`, the per-jurisdiction deadline encoding, the PII tier model (T1 through T5), the database tables that hold the nullification substrate, the NestJS services that carry the operational discipline, the evidence-extension pattern that preserves the audit chain, the S3 WORM marker pattern, the runtime boundary between operational metadata (which is nullifiable) and authoritative state (which is not), and the implementation phases that record what is wired in the readiness baseline versus what is queued.

This chapter does not redefine the immutability invariant (The Object Model and The Invariants), the audit substrate that records the nullification act (Audit and Activity Logging), the access boundary that authorizes a Data Subject Access Request (InfoSec and Access Control), or the SOC 2 Privacy criterion's scope (SOC 2 Conformance records the deferral per `DEC-ae331f`).

**Governing source.** outline.md §4.8; DEC-bd5492.

## The Foundation Tension

Foundation Invariant III states: "Once produced, an authoritative object is never altered. Corrections, adjustments, and reinterpretations are expressed only as new object versions. All versions coexist." The invariant is binding for Source Object, Canonical Object, Metric Snapshot, Action Object, Evidence Object, and Lineage Object.

GDPR Article 17, DPDP Act Section 12, and CCPA Section 1798.105 each grant a Data Subject the right to have their personal data erased upon request. The naive reading collides with Invariant III: erasure implies modification, modification implies version delta, version delta is not the same act as deletion.

`DEC-bd5492` resolves the collision by distinguishing two state classes.

| State class | Examples | Treatment |
|---|---|---|
| Authoritative state | Source Object, Canonical Object, Metric Snapshot, Action Object, Evidence Object, Lineage Object | Bound by Invariant III; never altered; corrections produce new versions |
| Operational metadata | Personal data fields in control-plane records (tenant subscription contact, admin user identity, activity actor name); PII fields embedded in tenant-DB operational records; PII paths in S3 WORM archives | Nullifiable; the field is the unit of erasure, not the row |

The platform's resolution: personal data is operational metadata, not structural fact. Erasure of personal data is a sentinel-based field overwrite that preserves row existence, primary-key identity, foreign-key references, chain shape, and audit evidence.

**Governing source.** The Object Model (Invariant III); DEC-bd5492.

## The Sentinel-Based Nullification Mechanism

Per `DEC-bd5492`, an erasure request triggers a deterministic field overwrite. The mechanism is not deletion; the row remains in place, the structural fact is preserved, and the field carries a sentinel value.

| Aspect | Form |
|---|---|
| Sentinel format | `[NULLIFIED:NUL-xxxxxx]` where `NUL-xxxxxx` is the per-request code (six hex characters) |
| Operation type | UPDATE setting the column value to the sentinel; never DELETE |
| Row preservation | Primary key, foreign keys, sibling columns unchanged |
| Chain preservation | Lineage and Evidence rows that reference the row continue to resolve |
| Reversibility | None; the original value is hashed (SHA-256) and stored in `nullification_action.original_value_hash`; the hash is one-way evidence, not a recovery key |
| Idempotency | A second request against an already-nullified field is a no-op; the sentinel is the terminal state |

The sentinel format is recognizable: a consumer reading a nullified field can detect the sentinel and handle it as honest absence rather than as missing data.

**Governing source.** DEC-bd5492; `bc-core/src/nullification/nullification-executor.service.ts`.

## Per-Jurisdiction Encoding

`DEC-bd5492` encodes the per-jurisdiction deadlines in the `NullificationService` legal-basis logic.

| Regulation | Right | Deadline |
|---|---|---|
| GDPR Article 17 (EU 2016/679) | Right to Erasure | Thirty days from request acknowledgment |
| GDPR Article 15 | Right of Access (DSAR) | Thirty days from request acknowledgment |
| GDPR Article 20 | Data Portability | Thirty days from request acknowledgment |
| DPDP Act Section 12 (India 2023) | Right to Erasure | Thirty days from request acknowledgment |
| DPDP Act Section 11 | Right of Access | Thirty days from request acknowledgment |
| CCPA Section 1798.105 (California 2018, CPRA 2020) | Right to Delete | Forty-five days from request acknowledgment |
| CCPA Section 1798.100 | Right to Know | Forty-five days from request acknowledgment |

The deadline is recorded on the `nullification_request` row at intake; the operator-facing surface tracks the deadline against current time.

Per pattern 88, the regulations are enumerated per-instance. GDPR Articles 16 (Rectification) and CCPA Section 1798.140(v) (CPRA Right to Correct) are out of nullification scope: rectification is a content correction, not an erasure, and the platform handles content correction through the new-version mechanism per Invariant III rather than through nullification.

**Governing source.** DEC-bd5492; `bc-core/src/nullification/nullification.service.ts` (legal-basis encoding).

## The PII Tier Model

`DEC-bd5492` defines five PII tiers. The tier governs whether a field is nullified by request and the priority of the erasure act.

| Tier | Class | Examples | Erasure rule |
|---|---|---|---|
| T1 | Direct identifier | email, firstName, lastName, cognitoSub | Nullify on request |
| T2 | Indirect identifier | createdByName, updatedByName, owner-name JSON paths | Nullify on request |
| T3 | Behavioral | ipAddress, userAgentText, actorId | Nullify on request |
| T4 | Sensitive business | authenticationJson, record.* business data containing PII | Nullify on DSAR |
| T5 | Structural | tenantId, contractId, timestamps, hashes | Never nullified; structural identifiers preserve chain integrity |

The `pii_field_registry` table catalogs which columns across the platform DB and the tenant DB carry which PII tier; the operator seeds the registry. The registry is the authority for "what is PII" and is read by the nullification engine to decide what to overwrite.

**Governing source.** DEC-bd5492; `bc-core/src/database/schema/operations/pii-field-registry.ts`.

## The Five-Table Substrate

`DEC-bd5492` declares five tables in the `operations` schema. The tables are wired in bc-core's Drizzle schema; the schema migration is committed.

| Table | Purpose |
|---|---|
| `pii_field_registry` | Catalogs PII columns across platform and tenant DBs with sensitivity tier and masking strategy; the seeded registry is the authority for what is PII |
| `nullification_request` | The DSAR or erasure-request master row; carries `subjectIdentifier`, `legalBasis`, `subjectTenantId`, lifecycle state (`pending`, `approved`, `in_progress`, `completed`, `partially_completed`, `failed`) |
| `nullification_action` | Per-field audit trail; one row per field overwritten; carries `originalValueHash` (SHA-256), `sentinelApplied`, `evidenceId` linkage, `executedAt` |
| `dsar_response` | DSAR download tracking; time-limited token (default seven-day expiry); the DSAR package is delivered through the token |
| `retention_policy` | Auto-nullification schedule per sensitivity tier or per record category; the engine evaluates active policies and creates nullification requests |

Each table's schema is defined as a Drizzle declaration under `bc-core/src/database/schema/operations/`. The tables are present in the canonical DDL; the migration has run against the staged platform DB.

**Governing source.** DEC-bd5492; `bc-core/src/database/schema/operations/`.

## The Operational Service Surface

bc-core's `NullificationModule` carries six services that operationalize the nullification mechanism.

| Service | Responsibility |
|---|---|
| `NullificationService` | Request lifecycle management: create, approve, reject, mark in-progress, complete; encodes the per-jurisdiction deadline |
| `NullificationExecutorService` | Field-masking engine: reads the PII registry, executes the UPDATE statements, records the per-field `nullification_action` row, computes the SHA-256 of the original value before overwrite |
| `DsarService` | Data Subject Access Request discovery: scans platform DB and tenant DB columns matched by the PII registry; assembles the JSON DSAR package; issues the time-limited download token |
| `NullificationEvidenceService` | Evidence-chain extension: creates a new Evidence row with `evidenceType: 'nullification'` referencing the original content hashes, the affected evidence IDs, and the legal basis |
| `S3NullificationService` | S3 WORM marker placement: lists tenant-prefixed S3 objects and places a `.nullified` companion marker recording the request code, legal basis, subject identifier, PII paths, and the nullification timestamp |
| `RetentionService` | Retention-policy evaluation: reads active policies from `retention_policy`; creates auto-erasure `nullification_request` rows when the retention window elapses |

The services are wired in `NullificationModule` and exported per the bc-core module convention. The HTTP controllers (`NullificationController`, `PiiRegistryController`, `DsarController`, `RetentionController`) expose the operator surface.

**Governing source.** `bc-core/src/nullification/`; DEC-bd5492.

## Evidence-Chain Extension Pattern

Per `DEC-bd5492`, the nullification act is itself a governed event that produces audit evidence. The pattern is extension, not modification: a new Evidence row is appended that records the erasure as a forward state advance.

| Pattern element | Form |
|---|---|
| Trigger | A nullification request is approved and the executor runs |
| New Evidence row | `evidenceType: 'nullification'`; payload references the original content hashes (SHA-256 of pre-overwrite values), the affected evidence IDs, the legal basis (regulation citation), the subject identifier, and the request UID |
| Original Evidence rows | Unchanged; their references to nullified columns resolve to the sentinel value after nullification, but the rows themselves remain |
| Chain reconstructability | The audit reconstructs the chain by reading the original Evidence row and the nullification Evidence row together; the original payload is hashed, not erased; the evidence of "what was here" is the hash, the evidence of "when it was nullified" is the new row |

The pattern preserves the audit trail required by ISO 27001 A.8.15 and the SOC 2 Common Criteria CC4 monitoring requirement; the audit can verify that the erasure act was governed (by the request row), authorized (by the legal basis), and recorded (by the new Evidence row).

**Governing source.** DEC-bd5492; `bc-core/src/nullification/nullification-evidence.service.ts`; Evidence and Lineage.

## S3 WORM Marker Pattern

S3 WORM (Write Once Read Many) archives are a separate substrate from the database tier. The S3 objects are immutable during their lock period; deleting them is not authorized while the lock holds. The platform's pattern: place a companion `.nullified` marker alongside the original object rather than deleting it.

| Aspect | Form |
|---|---|
| Original object | Untouched during the WORM lock period |
| Companion marker | Sibling object with the suffix `.nullified` containing the request code, legal basis, subject identifier, PII paths, and ISO 8601 timestamp |
| Read-path filter | The platform's S3 read path is queued to detect the marker and strip the PII paths before returning the bytes; not yet wired (recorded below) |
| Post-lock behavior | When the WORM lock period elapses, the object becomes deletable; the standard erasure path may then proceed |

The pattern preserves the WORM contract while satisfying the privacy obligation as far as the lock allows. The drift: the read-path filter is not yet wired; current readers see the original PII bytes from S3.

**Governing source.** DEC-bd5492; `bc-core/src/nullification/s3-nullification.service.ts`.

## What Is Erased and What Is Preserved

| Subject | Erased | Preserved |
|---|---|---|
| Direct identifiers (T1) | Yes; field overwritten with sentinel | Row, primary key, foreign keys |
| Indirect identifiers (T2) | Yes; field overwritten with sentinel | Same |
| Behavioral identifiers (T3) | Yes; field overwritten with sentinel | Same |
| Sensitive business data containing PII (T4) | Yes on DSAR; field overwritten with sentinel | Same |
| Structural identifiers (T5) | Never | Always |
| Authoritative state (Source Object, Canonical Object, Metric Snapshot, Action Object) | Never (the row is the structural fact); fields within the payload that carry PII are nullified per the registry | Row identity always |
| Original value | The field is overwritten | The SHA-256 hash is preserved as evidence of what was there |
| Audit records of the nullification act | Append-only; new Evidence row | Always |
| S3 WORM archives during lock period | Not deleted; companion marker placed | Original object preserved per WORM contract |

The pattern: nullify the field, preserve the structure, hash the original, extend the evidence chain. Pattern 86 (persistence-claim precision) governs the chapter's claim: the implementation matches the design intent for the field overwrite, the row preservation, and the original-value hash.

**Governing source.** DEC-bd5492; The Object Model.

## Constraints

| Constraint | Form |
|---|---|
| Sentinel is the terminal state | Once nullified, a field is not re-populated; the sentinel is final |
| Original value is hashed, never preserved | The hash is one-way evidence; recovery is not authorized |
| Authoritative-state rows are never deleted | The row preserves the structural fact; PII fields within are nullified |
| Per-jurisdiction deadlines are enforced | The request lifecycle tracks the deadline against current time |
| Tier T5 is never nullified | Structural identifiers are out of scope |
| Evidence-chain extension is mandatory | Every nullification act produces a new Evidence row |
| WORM contract is honored | S3 archives in the lock period are marked, not deleted |

**Governing source.** DEC-bd5492; The Object Model.

## Failure Modes

| Failure | Behavior |
|---|---|
| Nullification request against a non-existent subject identifier | The request fails validation at intake; HTTP 400; no rows written |
| Nullification request against a non-PII column | The PII registry rejects the request; the column is not in scope |
| Executor encounters a tenant DB dynamic table deferred in the readiness baseline | Per the implementation status, the executor skips the column with a recorded reason; the request status becomes `partially_completed` |
| Original-value hash computation fails | The action row is not written; the executor retries with logging |
| Evidence-extension service is not invoked from the executor | Per the drift inventory below, the evidence-chain row is not auto-created by the executor in the readiness baseline; the operator records the erasure manually or the wiring is added to bc-core |
| DSAR download token expires | The subject must request a new package; the original token is single-use within the configured download window |
| Retention policy evaluation runs against an unscheduled substrate | The policy engine logs an error; auto-nullification does not run; the policy remains queued |

**Governing source.** `bc-core/src/nullification/`; DEC-bd5492.

## Drift Inventory

| Drift item | Status |
|---|---|
| Tenant DB nullification execution is Phase 3 (deferred) | The `NullificationExecutorService` skips dynamic tables with a comment marking Phase 3; the runtime DSAR discovery for tenant DB is wired, but the erasure execution is queued |
| JSONB deep masking is Phase 3 (deferred) | The schema declares the `jsonbPath` column; the masking function is named in code as a future surface (`nullify_jsonb_paths`); the function is not yet implemented |
| Retention-policy automation is Phase 4 (partial) | The `RetentionService` exists and the table is declared; a scheduled evaluation has not been confirmed wired in the runtime |
| S3 read-path filter is Phase 4 (deferred) | The marker placement is wired; the read path that strips PII upon read is queued |
| `NullificationEvidenceService` is not invoked from the executor | The evidence-extension service exists and can create rows; the `NullificationExecutorService` does not call it after field overwrite; the wiring is queued |
| The PII registry is operator-seeded | Automated detection of PII columns is not wired; operator declares the registry per `DEC-bd5492`'s seeded baseline |
| DSAR submission acknowledgment to subject is not automated | The intake records the request; per-subject acknowledgment notification is queued |
| Per-tenant data residency assertion is not automated | Per-region jurisdiction confirmation at request intake is queued |
| SOC 2 Privacy criterion is excluded from Type I scope per `DEC-ae331f` | Recorded; the substrate is ready and operates in the readiness baseline, but the audit scope is forward-looking |
| Consent-and-purpose governance for DPDP Act Section 18 is not encoded | The PII tiers are defined; the per-tier consent rules are not encoded in the runtime; recorded as a regulatory-coverage gap |

**Governing source.** `bc-core/src/nullification/`; DEC-bd5492; DEC-ae331f.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| The Object Model | Invariant III (immutability) | The privacy-mechanism resolution that distinguishes operational metadata from authoritative state |
| The Invariants | The full invariant catalog | The Invariant III tension and the platform's resolution |
| Evidence and Lineage | The proof-chain authority | The evidence-extension pattern that nullification consumes |
| Audit and Activity Logging | The audit substrate | The per-nullification audit-row emission |
| InfoSec and Access Control | The auth boundary | The scope check that authorizes a DSAR submission and the executor's invocation |
| Decision and Change Procedure | The change-record substrate | The per-erasure change record (the request and the executor run together produce the trail) |
| ISO 27001 Conformance | The conformance posture | The A.8.10 (Information deletion) mapping |
| SOC 2 Conformance | The Trust Services Criteria mapping | The Privacy criterion's deferral per `DEC-ae331f` |
| Operations: Tenant Lifecycle and Subscription | The Subscription artifact and tier model | The end-of-tenant-relationship erasure trigger when a tenant offboards |

**Governing source.** outline.md §4.8; The Authority Model.

## References

- The Authority Model
- The Object Model
- The Invariants
- Evidence and Lineage
- Audit and Activity Logging
- InfoSec and Access Control
- Decision and Change Procedure
- ISO 27001 Conformance
- SOC 2 Conformance
- Operations: Tenant Lifecycle and Subscription
- DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object)
- DEC-1918d0 (Two-database split)
- DEC-771baf (Tenant database topology)
- DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria)
- GDPR (EU 2016/679; external authority)
- DPDP Act 2023 (India; external authority)
- CCPA / CPRA (California; external authority)
