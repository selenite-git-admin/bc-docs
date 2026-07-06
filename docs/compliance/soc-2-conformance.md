---
id: soc-2-conformance
order: 48
title: "SOC 2 Conformance"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, decision-and-change-procedure, audit-and-activity-logging, infosec-and-access-control, risk-and-vendor-management, iso-27001-conformance, privacy-and-the-immutable-fact, chain-completeness-and-verdict]
governing_sources:
  - The Authority Model
  - DevHub
  - Decision and Change Procedure
  - Audit and Activity Logging
  - InfoSec and Access Control
  - ISO 27001 Conformance
  - Chain Completeness and Verdict
governing_adrs:
  - DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria; Type I first on Security plus Confidentiality plus Processing Integrity, with Availability and Privacy added per maturity gates)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; the D268 ten-rule policy)
  - DEC-bebaec (Chain Completeness SSOT; the platform's processing-integrity authority)
  - DEC-804874 (L-Node Verification with Semantic Family Classification; the session-close gate per D366)
  - DEC-1918d0 (Two-database split; the confidentiality control)
  - DEC-771baf (Tenant database topology; the confidentiality refinement)
  - DEC-3395bc (bc-docs-v3 SSOT cutover; the docs anti-scraping mechanism)
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact; the supplier-side preventive control)
  - DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object; the privacy mechanism deferred from the SOC 2 Type I scope per DEC-ae331f)
  - DEC-623f8f (ADR Hygiene Policy; the eight ADR lifecycle rules that operate as part of CC1 control environment)
  - DEC-8391fd (Process audit harness driven by Gemini; the CC4 monitoring substrate beyond ADR hygiene and code quality)
errata_referenced: []
v2_sources: []
diagrams: []
---

# SOC 2 Conformance

## Scope

This chapter records the platform's SOC 2 conformance posture in the readiness baseline. It states the staged-pursuit decision per `DEC-ae331f` (Type I engagement first, on reduced criteria; Type II and the additional criteria gated on maturity), the platform's chosen Trust Services Criteria scope (Security, Confidentiality, Processing Integrity), the Common Criteria mapping for the Security category as it consumes the platform's substrate, the Confidentiality and Processing Integrity mappings, the explicit deferral of Availability and Privacy to future engagements, and the gap inventory between the as-built substrate and a Type I attestation report.

This chapter does not redefine the InfoSec controls (InfoSec and Access Control), the change-record substrate (Decision and Change Procedure), the audit substrate (Audit and Activity Logging), the chain-completeness SSOT (Chain Completeness and Verdict), or the privacy mechanism (Privacy and the Immutable Fact). Each governs its own claims; this chapter records the SOC 2 conformance perspective.

This chapter is honest per pattern 81: the platform has not undergone a SOC 2 audit. There is no SOC 2 Type I report, no Type II report, and no auditor engagement underway in the readiness baseline. The chapter records what the substrate provides and what a future Type I audit would surface as the in-scope control evidence and the queued-control gaps. Aspirational SOC-2-grade attestation claims are not made.

**Governing source.** outline.md §4.8; DEC-ae331f.

## Staged Pursuit per DEC-ae331f

`DEC-ae331f` records the platform's compliance pursuit posture for SOC 2 specifically. The decision is staged.

| Aspect | Form |
|---|---|
| Engagement type | SOC 2 Type I first; Type II added per maturity gates |
| Trust Services Criteria scope | Three of five: Security (Common Criteria), Confidentiality, Processing Integrity |
| Excluded criteria | Availability and Privacy |
| Availability gate | Added when uptime, observability, and incident discipline are demonstrably mature; signals include one full operating window without an SLO breach, observability stack fully instrumented, incident-response procedure documented with post-mortem discipline |
| Privacy gate | Added when product scope grows to include regulated personal data beyond incidental identity and admin data |

The platform's SOC 2 stance is forward-looking. Type I engagement is the first audit; Type II requires the operating window's evidence accumulation that Type I makes possible.

**Governing source.** DEC-ae331f.

## Common Criteria: Security (CC)

The Common Criteria are the SOC 2 baseline that every engagement honors. The CC categories map to the platform's substrate as follows.

| Common Criterion | Platform substrate |
|---|---|
| CC1 Control Environment | `CLAUDE.md`, the founder discipline, the Decision and Change Procedure substrate, the eight ADR hygiene rules per `DEC-623f8f`, the ten D268 rules per `DEC-ebf0b4` |
| CC2 Communication | DevHub session boot, the `change_records` table, the `plan_approvals` table, the per-session activity log |
| CC3 Risk Assessment | DevHub `risks` table per Risk and Vendor Management; per-row category, likelihood, impact, score, mitigation, owner, status |
| CC4 Monitoring | bc-qa audits (on-demand) per Quality Assurance; ADR hygiene audit; audit harness per `DEC-8391fd`; `audit_findings` table |
| CC5 Control Activities | bc-qa preventive gates (ESLint, ts-strict, no-eval); pre-commit hook; the change-record approval procedure; the L-node semantic gate at session close per `DEC-804874` |
| CC6 Logical and Physical Access | Cognito JWT authentication; ScopeGuard; `@PlatformOnly()` and tenant-scoped decorators; two-database split per `DEC-1918d0`; per-tenant topology per `DEC-771baf` |
| CC7 System Operations | Operations section chapters (Deployment Topology, Observability and Telemetry, Performance and Scale, Incident and Change Management) |
| CC8 Change Management | Decision and Change Procedure; the change-record plan-and-report pair; the D268 self-audit at session close |
| CC9 Risk Mitigation | The DevHub risk register; the L-node gate that blocks regression at session close; the QA NC register; the supersession-pair discipline |

Each row identifies the substrate that operates in the readiness baseline. The audit's substantive question (whether the substrate's design is suitably described and whether controls are suitably designed) is the Type I scope. Whether the controls operated effectively across an operating window is the Type II scope and is not addressed by Type I.

**Governing source.** Per-row referent (Decision and Change Procedure, DevHub, Risk and Vendor Management, Quality Assurance, InfoSec and Access Control, Operations chapters).

## Confidentiality (C)

The Confidentiality category covers the platform's information-protection mechanisms.

| Subject | Substrate |
|---|---|
| Tenant data isolation | Two-database split per `DEC-1918d0`; per-tenant topology per `DEC-771baf`; the connection-isolation discipline at the bc-core auth boundary |
| Platform-vs-tenant scope enforcement | `@PlatformOnly()` decorator and `ScopeGuard` per InfoSec and Access Control |
| Documentation surface protection | Docs anti-scraping per `DEC-3395bc`: JWT-guarded endpoints, rate limiting (sixty per minute, one thousand per day per Cognito subject), JSONL audit log, invisible Markdown watermark, private cache header |
| In-transit confidentiality | TLS at the application layer; AWS-managed certificates |
| At-rest confidentiality | AWS-managed encryption at the RDS and S3 layer; deploy-coordinate detail owned by Infrastructure |
| Auth boundary | AWS Cognito JWT issuance; RS256 signature validation against the JWKS endpoint |

The substrate's central confidentiality claim: a misrouted query at the runtime layer fails at the database connection boundary rather than leaking data, because the connection is scoped by tier (platform vs tenant). Application-level scope checks are defense in depth; the structural isolation is the load-bearing control.

**Governing source.** InfoSec and Access Control; DEC-1918d0; DEC-771baf; DEC-3395bc.

## Processing Integrity (PI)

The Processing Integrity category is the platform's strongest Trust Services Criteria alignment because the contract grammar IS processing integrity. The Foundation Invariants and the Operating Model contract chain are designed for processing-integrity claims.

| Subject | Substrate |
|---|---|
| Defined inputs and outputs | The Contract Grammar (Foundation); per-contract-family declared shape |
| Authoritative state production at boundaries | The Evaluation Boundaries (Foundation); progression objects produced only at governed boundary acts |
| Immutability and append-only authoritative state | The Object Model Invariant III; corrections produce new versions |
| Evidence emission | Invariant VI; every governed boundary act emits Evidence; no authoritative state without Evidence |
| Lineage emission | Per-progression-object Lineage rows; the proof chain is reconstructable |
| Chain completeness verdict | `DEC-bebaec` (Chain Completeness SSOT); the persisted `chain_status` table is the canonical processing-integrity verdict |
| L-node semantic verification | `DEC-804874` (L-Node Verification with Semantic Family Classification); per-MC L1 through L8 verdicts |
| Session-close gate | The L-node gate per CLAUDE.md (Session Protocol step six); regression in the chain semantic state during a session window blocks close |

The chain integrity SSOT and the L-node gate are the load-bearing PI controls. The Foundation invariants provide the discipline; the Operating Model's contract chain is the runtime; the persisted verdict tables are the audit trail. A SOC 2 PI audit reads these substrates as the primary evidence.

**Governing source.** Foundation; Operating Model: Chain Completeness and Verdict; DEC-bebaec; DEC-804874.

## Availability (A): Excluded from Type I per DEC-ae331f

Availability is excluded from the Type I scope. The platform's current operational substrate is recorded in Operations: Performance and Scale (the per-tenant isolation), Operations: Observability and Telemetry (the emission surfaces), and Operations: Incident and Change Management (the incident triage path). Per `DEC-ae331f`, Availability is added to the Type II scope after the maturity gate.

| Maturity gate | Form |
|---|---|
| One full operating window without SLO breach | The platform completes an uptime measurement across its first pilot tenant cycle |
| Observability stack fully instrumented | CloudWatch dashboards, structured log aggregation, metric and trace surfaces are wired |
| Incident-response procedure documented with post-mortem discipline | The Operations: Incident and Change Management chapter is operationalized; per-incident post-mortems are recorded as governed change-record artifacts |

The platform's readiness-baseline discipline is honest about the gap: there are no SLAs, no on-call rotation, and no formal status page. The substrate exists but is operator-driven; SOC 2 Availability conformance requires the substrate's operational maturity that the platform has not yet demonstrated.

**Governing source.** DEC-ae331f; Operations: Incident and Change Management; Operations: Observability and Telemetry; Operations: Performance and Scale.

## Privacy (P): Excluded from Type I per DEC-ae331f

Privacy is excluded from the Type I scope per `DEC-ae331f`. The platform's privacy mechanism (sentinel-based nullification per `DEC-bd5492`) is operationally implemented per Privacy and the Immutable Fact. The exclusion is not a gap in the mechanism but a scope decision: the readiness-baseline product scope does not include regulated personal data beyond incidental identity and admin data, and the Trust Services Criterion is not in scope until that grows.

When the Privacy criterion is added, the substrate to audit is recorded in Privacy and the Immutable Fact: the `nullification_request`, `nullification_action`, `dsar_response`, `pii_field_registry`, and `retention_policy` tables; the per-jurisdiction deadline encoding (GDPR Article 17, DPDP Act Section 12, CCPA 1798.105); the sentinel-based field-overwrite mechanism that preserves chain shape; the evidence-extension pattern.

**Governing source.** DEC-ae331f; Privacy and the Immutable Fact; DEC-bd5492.

## Type I vs Type II Scope Distinction

A SOC 2 Type I report attests that controls are suitably designed. A SOC 2 Type II report attests that controls operated effectively across a reporting period (typically six to twelve months).

| Audit aspect | Type I | Type II |
|---|---|---|
| Period covered | Point in time | Reporting period (six to twelve months typical) |
| Evidence | Description and design | Description, design, plus operating effectiveness across the period |
| Controls testing | Design effectiveness only | Design plus operating effectiveness with samples |
| Maturity required | Controls designed and implemented | Controls operating consistently across the period |
| Engagement order | Earlier (a substrate baseline) | Later (with operating-window evidence) |

Per `DEC-ae331f`, the platform's first engagement is Type I on the three reduced-scope criteria. Type II follows once the operating-window evidence accumulates.

**Governing source.** AICPA SOC 2 Trust Services Criteria; DEC-ae331f.

## Constraints

| Constraint | Form |
|---|---|
| Type I first | The first audit is Type I; Type II is gated on maturity |
| Reduced TSC scope | Security plus Confidentiality plus Processing Integrity only; Availability and Privacy are excluded from the first engagement |
| No audit underway in the readiness baseline | The chapter records substrate, not attestation; no SOC 2 report exists |
| The chain integrity SSOT is the PI substrate | The persisted `chain_status` and `l_node_semantic_verdict` tables are the canonical PI authority; ad-hoc PI claims are not made |
| The two-database split is the C substrate | Confidentiality is structural; cross-tier prevention is connection-isolation, not application-level |
| The change-record plan-and-report pair is the CC8 substrate | Every governed change carries the plan and the report |

**Governing source.** DEC-ae331f.

## Failure Modes

| Failure | Behavior |
|---|---|
| Type I engagement reveals an undocumented control | The control is added to the chapter and to the supporting substrate; an ADR records the addition |
| Type I engagement reveals a missing change record | The session is reconstructed from the activity log and the change record is written retroactively or the discipline gap is recorded honestly |
| The L-node gate fails open under bc-core outage | The gate's fail-open behavior per `DEC-804874` is documented; the audit reads the override rationale or the fail-open warning in the change record |
| The risk register has unregistered risks | The audit raises the gap; operator runs `devhub_risk_add` to create the rows |
| The NC register has unresolved blocking findings | The audit reads the NC register's lifecycle status; unresolved blocking NCs are an open finding |
| Maturity gate is missed | Type II engagement is deferred; the readiness window extends |

**Governing source.** DEC-ae331f; DEC-804874; Risk and Vendor Management; Quality Assurance.

## Drift Inventory

| Drift item | Status |
|---|---|
| No SOC 2 audit underway | Recorded; the chapter records substrate, not attestation |
| No SLAs, no on-call rotation, no formal status page (Availability gap) | Recorded per Operations: Incident and Change Management; the Type II Availability addition is gated on maturity |
| No formal management-review meeting cadence (CC1) | Recorded; the founder cold-read substrate carries the discipline in the readiness baseline |
| No automated continuous monitoring (CC4) | Recorded; bc-qa audits are on-demand; the CI integration point exists but is not wired |
| Audit logs are not append-only with HMAC signatures | Recorded; A.8.15 conformance via Audit and Activity Logging records the JSONL trail; cryptographic tamper-evidence is queued |
| Change-record approval is recorded but not enforced as a blocking gate at session close | Recorded; CC8 substrate exists; enforcement gate is queued |
| Privacy mechanism per `DEC-bd5492` has Phase 3 surface deferred (tenant DB nullification, JSONB masking) | Recorded per Privacy and the Immutable Fact; Privacy criterion is excluded from Type I scope per `DEC-ae331f` |
| Provider-pricing drift is not auto-tracked (CC3 risk-assessment depth) | Recorded; static price snapshots in bc-ai code are operator-updated; auto-tracking is queued |

**Governing source.** DEC-ae331f; Operations chapters; Privacy and the Immutable Fact.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| ISO 27001 Conformance | The ISO 27001 conformance posture | The companion SOC 2 posture per `DEC-ae331f`; the two conformance pursuits are coordinated |
| InfoSec and Access Control | The technical control surface | The CC6 logical-access mapping |
| Decision and Change Procedure | The change-record substrate, the ADR hygiene rules, the D268 session discipline | The CC1 and CC8 mappings |
| Audit and Activity Logging | The audit substrate | The CC2 monitoring substrate; the CC4 monitoring control |
| Risk and Vendor Management | The risk register and vendor inventory | The CC3 mapping |
| Quality Assurance | The bc-qa preventive control surface | The CC5 mapping |
| Chain Completeness and Verdict | The platform's processing-integrity authority | The PI mapping |
| Privacy and the Immutable Fact | The nullification mechanism | The future Privacy criterion's substrate |
| Operations: Incident and Change Management | The incident triage path | The CC7 mapping; the future Availability criterion's substrate |

**Governing source.** outline.md §4.8; The Authority Model.

## References

- The Authority Model
- DevHub
- Decision and Change Procedure
- Audit and Activity Logging
- InfoSec and Access Control
- Risk and Vendor Management
- Quality Assurance
- ISO 27001 Conformance
- Privacy and the Immutable Fact
- Chain Completeness and Verdict
- Operations: Incident and Change Management
- Operations: Observability and Telemetry
- Operations: Performance and Scale
- DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- DEC-bebaec (Chain Completeness SSOT)
- DEC-804874 (L-Node Verification with Semantic Family Classification)
- DEC-1918d0 (Two-database split)
- DEC-771baf (Tenant database topology)
- DEC-3395bc (bc-docs-v3 SSOT cutover)
- DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
- DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object)
- AICPA SOC 2 Trust Services Criteria (external authority)
