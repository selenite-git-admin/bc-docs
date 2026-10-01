---
id: iso-27001-conformance
order: 47
title: "ISO 27001 Conformance"
status: drafting
authority: authoritative
depends_on: [the-authority-model, devhub, decision-and-change-procedure, audit-and-activity-logging, infosec-and-access-control, risk-and-vendor-management, quality-assurance, mac-auditor-operations]
governing_sources:
  - The Authority Model
  - DevHub
  - Decision and Change Procedure
  - Audit and Activity Logging
  - InfoSec and Access Control
  - Risk and Vendor Management
  - Quality Assurance
  - Mac Auditor Operations (the independent auditor: what runs, who authorizes what)
governing_adrs:
  - DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria; readiness posture before certification, certification after pilot evidence)
  - DEC-ebf0b4 (Session Discipline and Data Integrity Rules; the D268 ten-rule policy that operates as the de facto information security discipline)
  - DEC-a4e550 (ADR-First Decision Workflow; ADR file as governance authority)
  - DEC-623f8f (ADR Hygiene Policy; the eight rules for ADR lifecycle and the `audit_adrs.py` check that runs in bc-docs CI)
  - DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact; the supplier-management control)
  - DEC-1918d0 (Two-database split; the access-restriction control)
  - DEC-771baf (Tenant database topology; the access-isolation refinement)
  - DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object; the information-deletion control)
  - DEC-ee6018 (Power of Ten adapted coding rules; the code-quality control)
  - DEC-5b760c (QA enforcement consolidates into per-repo CI; DevHub is the sole NC authority; bc-qa retired)
  - DEC-bebaec (Chain Completeness SSOT; the platform's processing-integrity authority)
  - DEC-804874 (L-Node Verification with Semantic Family Classification; the session-close gate that consumes the chain-status verdict)
  - DEC-3395bc (bc-docs SSOT cutover; the data-leakage-prevention surface for documentation)
  - DEC-8391fd (Process audit harness driven by Gemini; the internal-audit substrate beyond ADR hygiene and code quality)
  - DEC-081931 (Standing Claude-Codex exchange family gen-; the transport and protocol of independent review)
  - DEC-44456d (bc-external-audit as the auditor's home; the Mac auditor service under the bcauditor account; operator grants recorded on the desk)
  - DEC-fa7c63 (DSO family meaning; records that metric onboarding acts have no Codex role, grant ead781aa)
errata_referenced: []
v2_sources: []
diagrams: []
---

# ISO 27001 Conformance

## Scope

This chapter records the platform's ISO 27001 conformance posture for the readiness baseline. It states the staged-pursuit decision per `DEC-ae331f` (readiness phase first, certification after pilot evidence), the platform's choice of the ISO/IEC 27001:2022 revision (ninety-three Annex A controls in four themes A.5 Organizational, A.6 People, A.7 Physical, A.8 Technological), the per-control-family as-built mapping against the platform's current substrate, the explicit out-of-scope domains (A.6 People while the platform has no employees beyond the founder; portions of A.8 deferred per the readiness roadmap), the risk register and the non-conformity register that ISO 27001 mandates, the internal-audit substrate that the platform operates in the readiness baseline, the independent review of code changes by the auditor before merge (the one change-management control the platform practises daily), and the gap inventory between as-built and certification-ready posture.

This chapter does not redefine the InfoSec controls (InfoSec and Access Control), the change-record substrate (Decision and Change Procedure), the audit substrate (Audit and Activity Logging), or the risk register (Risk and Vendor Management).

This chapter is deliberately honest about the certification gap per pattern 81: the platform has not undergone an ISO 27001 audit. The chapter records what the platform's substrate provides in the readiness baseline and what a future audit would surface as gaps. Aspirational SRE-grade conformance claims are not made.

**Governing source.** DEC-3395bc; DEC-ae331f.

## Staged Pursuit per DEC-ae331f

`DEC-ae331f` records the platform's compliance pursuit posture. The decision is staged: ISO 27001 readiness phase (the platform implements the controls and documents the substrate); certification engagement after pilot evidence (the platform completes one full operating window with real tenant data before engaging an external auditor).

| Aspect | Form |
|---|---|
| Standard choice | ISO/IEC 27001:2022 (the four-theme Annex A revision) |
| Readiness posture | Readiness; the platform implements controls and documents substrate |
| Posture next | Certification after pilot evidence; engagement is forward-looking |
| Substrate documents | The internal ISMS documents at `barecount-devhub/ISO27001/` carry the Statement of Applicability, the Zero Day Analysis baseline, and the improvement roadmap |

The platform's ISMS documents under `barecount-devhub/ISO27001/` are operator-internal working documents; the canonical conformance posture is recorded in this chapter against the platform's drafted substrate. Per pattern 81: the canonical claim and the drift inventory are bidirectionally consistent; nothing in this chapter asserts a control that the substrate does not actually implement.

**Governing source.** DEC-ae331f; `barecount-devhub/ISO27001/`.

## A.5 Organizational Controls: Information Security Policies (A.5.1)

The platform's information-security policy surface is operational rather than formally documented. Three substrates carry the policy weight in the readiness baseline.

| Substrate | Form |
|---|---|
| `CLAUDE.md` (at the barecount-devhub repo root) | The agent-instruction policy surface; records the session protocol, the SOP compliance discipline, the dev-service management model, the AWS profile discipline, the database change protocol, the QA coding standards, and the don't-list |
| The Documentation System chapter and the chapter authority axis | The documentation-authority policy: every chapter declares `authority` (`authoritative`, `reference`, `evidentiary`) and `status` (`drafting`, `reviewing`, `locked`, `superseded`, `retired`); binding force requires `authority: authoritative` plus `status: locked` |
| `DEC-ebf0b4` (the D268 Session Discipline rules) | The ten-rule policy that governs engineering session behavior; rules cover bulk-generation prohibition, cosmetic status restraint, one-then-many, checkpoint discipline, self-audit at session close, independent verification |

The platform's stance: these substrates are the as-built information-security policy. Formal board-approved policy documents are queued; the operational policy substrate carries the discipline in the readiness baseline.

**Governing source.** CLAUDE.md; DEC-3395bc; DEC-ebf0b4.

## A.5.36 Compliance with Policies: The Change-Record Plan-and-Report Pair

`DEC-ebf0b4` (the D268 rules) and `DEC-a4e550` (the ADR-first procedure) anchor the compliance trail. The change-record substrate at the DevHub `change_records` table is the load-bearing artifact.

| Side | Form |
|---|---|
| Plan side | Written at session open or task transition to `wip`; carries `objective`, `approach`, `files_affected`, `risks`, `rollback` |
| Report side | Written at session close or task transition to `completed`; carries `summary`, `files_changed`, `commits`, `verification`, `decisions_made`, `risks_identified`, `followup_tasks`, `incidents`, `rollback_path` |

The pair shares a `ref_uid` (the session UID `SES-xxxxxx` or task UID `TSK-xxxxxx`) and produces a single `CHG-xxxxxx` row. The ISO 27001 plan-and-report discipline is the platform's compliance trail for governed changes.

**Governing source.** Decision and Change Procedure; DEC-ebf0b4; `barecount-devhub/src/db.js` (change_records schema).

## A.8.32 Change Management: Independent Review by the Auditor

In eight protected repositories (bc-core, bc-db, bc-docs, bc-admin, bc-portal, barecount-devhub, bc-demo, bc-infra), no change merges to `main` without one approving review and the repository's CI check, and the rule binds administrators too; in bc-exchange the same protection exists but an administrator can bypass it (branch protection read from the GitHub API on 2026-09-30). In practice the approving reviewer is an independent auditor. The auditor's own repository, `bc-external-audit`, has no branch protection: its changes are reviewed on the same exchange by practice and merged by the operator, and the drift inventory records the gap. The auditor is Codex, OpenAI's model, run by the Mac auditor service under its own macOS account (`bcauditor`) on the development Mac since 2026-09-28. It is independent of the builder (the Claude sessions) in three ways: it runs under a separate account whose home the builder cannot read; its standing instructions are versioned in its own repository, `bc-external-audit`, outside the builder's control (`DEC-44456d`); and it holds no authority of its own, so nothing the builder writes can enlarge what the auditor may do (`DEC-081931`, point 8).

This is the change-management control the platform practises in the readiness baseline. It complements the change-record pair (A.5.36): the pair records intent and outcome; the review is the independent check between them.

| Element | As-built |
|---|---|
| Transport | The permanent `gen-` exchange per `DEC-081931`: every review is a thread of numbered messages committed as files to `bc-external-audit` on `origin/main`. A message names the pull request and the exact commit under review. The auditor's reply binds the message it answers by that message's SHA-256. Reviewed bytes equal merged bytes because the message names the exact head and the merge is pinned to it (the App's head gate, or the operator's `--match-head-commit`) |
| Sender gate | The builder's publisher refuses a message unless the sending session is open in DevHub, and records the thread, number, commit and hash as a checkpoint on that session, which joins the review to the change record |
| Depth | `light` for documents, records and runbooks; `full` for schema, security, auth, cloud, secrets and anything that changes platform behaviour or evidence. The auditor may raise the depth, never lower it (`DEC-081931`, point 6) |
| Merge | The auditor's GitHub App merges only where a standing operator grant allows it, always at the exact head the auditor accepted, with all required checks green and a passing App attestation, and a merge never deploys anything: bc-core, bc-db, bc-portal and barecount-devhub (grant `2026-09-29T12-44-11-637Z-4e95a6b8`, text SHA-256 `4e95a6b899bfd3900c6bfc510a21e2468414b6ea5d151fac97140b3c6c5ab45e`; barecount-devhub merges also wait for no announced live window, grants `9603bf05` and `ce08a39b`), bc-docs (grant `2026-09-30T04-11-41-012Z-1bea8fcd`, text SHA-256 `1bea8fcd7119eb51bded1d7af86fd10db24a91fbfa572e639243e04d9945500a`, extending `67662fe8`; merging an ADR records its text only, and its status still follows the recorded authority), bc-exchange (grant `22d493f8`), and the Kaveri KPI arc's pull requests (grant `f610a97f`). The operator merges from their own account, pinned to the accepted head with `--match-head-commit`, whatever those grants do not cover: workflow files (the App has no Workflows permission), the auditor's own repository `bc-external-audit` (deliberately outside the App), and any repository or act outside them (Mac Auditor Operations, §2). The auditor's standing instructions stop it before approval or merge when the available GitHub actor is the pull request's author, when the App's capability check fails, or when CI or review evidence is unknown (`bc-external-audit` `service/codex/AGENTS.md`) |
| Authority | Only the operator's grants, recorded on the exchange desk (bc-exchange) with a phone code. A request, a message, a reply or a desk note is never authority. Each grant carries its text and the SHA-256 of that text; the desk's rules page restates the grants in rule language and says of itself that it is never authority |
| Evidence | The committed message and reply files with their hashes; the App's merge records; the grants list on the desk (`GET /api/grants-list`); the session checkpoint and change record in DevHub |

Three standing operator decisions bound the control. They are stated here once, with their sources, and not restated with authority elsewhere in this section.

| Decision | Rule | Source |
|---|---|---|
| The two-round cap | At most two review rounds per unit. If blocking findings remain after round two, the auditor stops and escalates to the operator instead of opening a third round. A finding blocks only if it can cause wrong or corrupted data, irreversible loss, or a security exposure beyond the accepted development residuals; everything else is a non-blocking follow-up, and a review never widens beyond the act under review | Grant `2026-09-28T15-48-14-601Z-6d37cbfc`, text SHA-256 `6d37cbfc59496f07112d01e026c90e65ce7fd8a359d1999b8b08aabd6bd1b9c1` (the operator's standing instruction of 2026-09-27, re-issued on the Mac). Desk rule R3 restates it |
| The narrow-fix exception | In the Kaveri KPI arc (plan PLN-c96901) only, when the final round finds a narrow issue and the builder fixes it at a new pinned commit, the auditor may do one more review limited to that fix and land it if accepted; anything wider goes to the operator | Grant `2026-09-28T14-37-08-243Z-d8b54d8c`, text SHA-256 `d8b54d8c2e3a842aae38d878040f0894089dfcdd5252dc77130b09e7b41514a5`. Desk rule R3 restates it |
| The metric-onboarding exclusion | The auditor has no role in metric onboarding. Authoring, certifying, admitting, binding and evaluating metric contracts, and the source reads they need, run under the operator's grants and the platform's own gates, including the independent source-value check before a batch goes live. The auditor does not review, clear or audit those acts. It keeps reviewing engine changes: code, schema, database grants, auth, cloud and serve moves | Grant `2026-09-29T08-34-38-377Z-ead781aa`, text SHA-256 `ead781aa17fb97e64ec6d856cf59e87943af1cfbdda7f5a1fd5d96b9bbc32a53`. Recorded in `DEC-fa7c63` (authority line) and in Operations: Serve Moves and Live Windows; desk rule R15 restates it |

What this control is not. It is not an ISO 27001 internal audit and not a certification body: the auditor reviews changes, it does not audit the management system. Its dispositions grant no authority (`DEC-081931`, point 5); acceptance of a change and permission to merge are separate acts, and the second comes only from the operator's grant. The desk's rules page is a restatement for operators and is never the source; the grants are.

**Governing source.** Mac Auditor Operations; DEC-081931; DEC-44456d; DEC-fa7c63; the grants named above, as recorded on the exchange desk.

## A.6 People Controls: Out of Scope In The Readiness Baseline

The readiness baseline has no employees; the founder is the sole human operator and AI agents are non-employees. Per `DEC-ae331f` and the platform's Statement of Applicability under `barecount-devhub/ISO27001/`, A.6 controls (screening, terms and conditions, awareness, discipline, termination, NDA) are marked Not Applicable. The scope expands when hiring begins; the readiness roadmap names this as a queued surface.

**Governing source.** DEC-ae331f; `barecount-devhub/ISO27001/`.

## A.7 Physical Controls: AWS Shared Responsibility

The platform's deployment substrate is AWS. Per Infrastructure (the Implementation chapter) the deployed surface in the readiness baseline is limited to AuthStack plus dormant PlatformInfraStack; the bulk of physical controls inherit from the AWS shared-responsibility model. The platform does not operate dedicated facilities; physical-control conformance is the AWS commitment, not the platform's own.

**Governing source.** Infrastructure; Operations: Deployment Topology.

## A.8 Technological Controls

A.8 is the largest control family. The platform's substrate maps to A.8 controls explicitly.

| Control | As-built |
|---|---|
| A.8.2 Privileged access | `@PlatformOnly()` decorator and ScopeGuard; bc-core auth boundary per InfoSec and Access Control |
| A.8.3 Information access restriction | Two-database split per `DEC-1918d0` and per-tenant topology per `DEC-771baf` |
| A.8.4 Access to source code | GitHub repositories in the founder's organization; access gated by GitHub identity |
| A.8.6 Capacity management | Per-tenant isolation; Operations: Performance and Scale records the per-tenant resource discipline |
| A.8.8 Management of technical vulnerabilities | Each repository's CI per `DEC-5b760c` (lint, typecheck, tests, the bc-core architecture gates); no developer-machine hook; Quality Assurance records the enforcement per repository |
| A.8.9 Configuration management | Per-repo `CLAUDE.md` and the Documentation System chapter; configuration declared in source-controlled files |
| A.8.10 Information deletion | Sentinel-based nullification per `DEC-bd5492`; Privacy and the Immutable Fact records the mechanism |
| A.8.11 Data masking | Out of scope in the readiness baseline; nullification mechanism handles the erasure case |
| A.8.12 Data leakage prevention | Docs anti-scraping per `DEC-3395bc`; JWT-guarded endpoints |
| A.8.13 Information backup | Docker compose volumes for development; the AWS RDS managed-service substrate for the staged deployment; backup posture is queued per Operations: Upgrade and Migration |
| A.8.14 Redundancy | Out of scope in the readiness baseline; the readiness roadmap names this as a queued surface |
| A.8.15 Logging | Audit and Activity Logging records the JSONL trail and the DevHub activity log |
| A.8.20 Network security | TLS in transit; AWS-managed network controls; `@PlatformOnly()` JWT guard at the application layer |
| A.8.22 Segregation of networks | AWS VPC topology owned by Infrastructure; the platform-vs-tenant DB separation is the access-isolation surface |
| A.8.23 Web filtering | Out of scope; the platform does not browse external content from runtime services |
| A.8.24 Use of cryptography | TLS in transit; AWS-managed at-rest encryption for RDS and Cognito; Cognito JWT signed by AWS using RS256 |
| A.8.25 Secure development lifecycle | Per-repository CI gates and branch protection; independent review before merge (A.8.32); the Decision and Change Procedure substrate |
| A.8.26 Application security requirements | The Power-of-Ten rule set encoded in `@barecount/eslint-config` |
| A.8.27 Secure system architecture | The Foundation Invariants and the contract grammar; structural correctness rather than ad-hoc security |
| A.8.28 Secure coding | The Power of Ten rules per `DEC-ee6018` as `@barecount/eslint-config` defines them, binding at the level each repository's CI applies (Quality Assurance, enforcement table) |
| A.8.29 Security testing in development | Test surfaces per Synthetic Data and Testing; bc-core unit and integration tests |
| A.8.30 Outsourced development | Out of scope in the readiness baseline; no outsourced development |
| A.8.32 Change management | Decision and Change Procedure; the change-record plan-and-report pair; independent review of every code change by the auditor before merge (A.8.32 Change Management: Independent Review by the Auditor) |
| A.8.33 Test information | Synthetic Data and Testing; the qa-bench tenant discipline |
| A.8.34 Information access during audit | Audit and Activity Logging; the JSONL trail and the DevHub activity log |

**Governing source.** Per-control referent (InfoSec and Access Control, Quality Assurance, Privacy and the Immutable Fact, Audit and Activity Logging, Synthetic Data and Testing, Decision and Change Procedure).

## A.5.20 Information Security in Supplier Relationships

The platform's supplier-management surface is recorded in Risk and Vendor Management. The eleven external vendors (AWS Cognito, AWS CodeArtifact, AWS Bedrock, AWS S3, AWS Secrets Manager, AWS RDS PostgreSQL, Stripe, npmjs.org, Anthropic, Google Gemini, OpenAI) each carry a documented surface, consumer chapter, and failure mode. The CodeArtifact supply-chain control per `DEC-441665` mitigates `RSK-cb8929` (npm registry compromise, package yanking, dependency compromise events) and is the load-bearing supplier-side preventive control.

The 2013 revision's A.14.2.1 control (referenced in CLAUDE.md as the historical citation for `RSK-cb8929`) maps to the 2022 revision's A.5.20 control. Both numbering systems are accepted; the chapter records the 2022 revision as the canonical scheme.

**Governing source.** Risk and Vendor Management; DEC-441665.

## Risk Register

ISO 27001 mandates a documented risk-treatment procedure. The platform's risk register is the DevHub `risks` table per Risk and Vendor Management. The schema records category, likelihood, impact, an auto-calculated score, mitigation, owner, status (`identified` through `closed`), and a review date. The MCP tool family `devhub_risk_*` is the operator surface.

The risk register is wired and operational. `RSK-cb8929` (npm supply chain) is a row in it, status `mitigated`, with the CodeArtifact mirror per `DEC-441665` as its treatment; earlier versions of this chapter said the row was missing, which was true before the reconciliation and is not now (verified against the register on 2026-09-30). The daily risk-review housekeeping digest (barecount-devhub TSK-a8ba06) reports scores, owners and overdue review dates; it found the register unchanged since 2026-04-29, eleven of twelve open risks without a review date, and the two critical risks without an owner. A review cadence that acts on the digest is queued.

**Governing source.** Risk and Vendor Management; `barecount-devhub/src/db.js` (risks schema).

## Non-Conformity Register

ISO 27001 mandates non-conformity tracking. The platform's register is the DevHub `qa_nc_records` table, the single non-conformance authority since `DEC-5b760c` (2026-08-24); the earlier bc-qa file register is retired and is not a register.

| Aspect | Form |
|---|---|
| The register | DevHub `qa_nc_records`; read through `GET /api/qa/nc` and the `devhub_qa_nc_*` tools; written through `POST /api/qa/nc` and `PATCH /api/qa/nc/:uid` |
| Lifecycle | `open`, `investigating`, `resolved`, `accepted`, `waived`; a waiver carries its reason; `resolved_at` is set on closure |
| Writer | None today. The rows were raised by the retired bc-qa audit; CI fails builds but writes no row; nothing has been raised or resolved since 2026-08-24 (as read on 2026-09-30: 1,581 rows, 1,566 open). Decided 2026-09-30 (grant `2026-09-30T12-40-45-252Z-594d93aa`, text SHA-256 `594d93aa12aa04e819ca474a43631993abccd659d2545228b245630da9c9e525`, decision 9): DevHub's own rule scan becomes the writer, proven first on one small repository (build TSK-aae076); the 1,565 bc-qa-era rows were waived the same day citing that grant, leaving NC-e886b3 open |
| Review | The daily NC-aging housekeeping digest (barecount-devhub TSK-b0685b) reports counts, aging and rows from retired tooling; it is read by the Compliance & Quality controller |

The gap is stated plainly: the register exists and is queryable, but it has no intake yet, so it is not evidence of a current non-conformity process. The writer is decided and not built; Quality Assurance records the decision, the build task and the proof the chapter waits for before claiming a writer.

**Governing source.** Quality Assurance; DEC-5b760c; `barecount-devhub/src/db.js` (qa_nc_records schema).

## Internal Audit Substrate

ISO 27001 expects scheduled internal audits. The platform has no internal audit of the management system. What it operates instead, in the readiness baseline, are three continuous or scheduled checks of narrower scope.

| Surface | Form |
|---|---|
| ADR hygiene | `scripts/docs-control/audit_adrs.py` in bc-docs, run in that repository's CI on every push and pull request (`adr-hygiene.yml`); merge-blocking on supersession issues, advisory on stuck-proposed and missing fields (`DEC-623f8f`) |
| Independent review of code changes | The auditor's review of every change before merge in the protected repositories (A.8.32); a change control, not an audit |
| Housekeeping digests | Three daily read-only scheduled tasks (session hygiene, NC aging, risk review) that write a dated digest to a DevHub task each; they change nothing and are read by the Compliance & Quality controller |

The bc-qa audit harness and the `devhub_qa_audit` tool that earlier versions of this chapter named were retired by `DEC-5b760c`; the Gemini-driven process audit per `DEC-8391fd` has one persisted run and is not scheduled. A documented internal-audit programme with a calendar remains a queued surface.

**Governing source.** DEC-623f8f; DEC-5b760c; `bc-docs/.github/workflows/adr-hygiene.yml`; the housekeeping tasks TSK-87a578, TSK-b0685b, TSK-a8ba06.

## Management Review

ISO 27001 expects a documented management-review cadence. The platform's readiness-baseline substrate is the founder cold-read on every chapter, the session-close discipline that records D268 self-audit and L-node gate verdicts, and the change-record plan-and-report pair that surfaces session-by-session learnings. A formal management-review meeting cadence is queued.

**Governing source.** DEC-ebf0b4; bc-docs founder cold-read discipline.

## Constraints

| Constraint | Form |
|---|---|
| Readiness, not certification | The platform is in readiness posture per `DEC-ae331f`; certification engagement is forward-looking |
| Standard choice is fixed | ISO/IEC 27001:2022; the four-theme Annex A revision |
| A.6 People is out of scope | The readiness baseline has no employees; the scope expands when hiring begins |
| A.7 Physical inherits from AWS | Shared-responsibility model; no dedicated facilities |
| A.8 Technological is the substrate weight | The platform's load-bearing conformance surface |
| Risk register is canonical | DevHub `risks` table; ADR cross-references point at the table row |
| Internal audit does not exist as such | ADR hygiene runs in CI, code review runs before merge, digests run daily; an audit programme with a calendar is queued |
| Independent review is a change control, not an audit | The auditor reviews every code change before merge under the operator's grants; it does not audit the management system and holds no authority of its own |

**Governing source.** DEC-ae331f; CLAUDE.md.

## Failure Modes

| Failure | Behavior |
|---|---|
| Audit finds an unrecorded risk | Operator runs `devhub_risk_add` to create the row; the session change record records the discovery |
| Audit finds an unflipped supersession pair | `audit_adrs.py` fails the bc-docs CI check; the ADR's frontmatter is amended and recommitted |
| Audit finds a non-conforming code path | A person raises the NC with `devhub_qa_nc_raise`; the register tracks the lifecycle; no tooling raises it today |
| Audit finds an unaudited governed sequence | Operator runs `devhub_process_audit_run` against the session's UID |
| Audit finds a missing change record | Operator writes the missing change record retroactively or accepts the discipline gap in the audit trail |
| Pilot evidence falls short of certification thresholds | Operator extends the readiness window; certification engagement is deferred until thresholds are met |

**Governing source.** DEC-623f8f; DEC-8391fd; Decision and Change Procedure.

## Drift Inventory

| Drift item | Status |
|---|---|
| Formal information-security policy documents are queued | Recorded; operational substrates carry the discipline in the readiness baseline |
| Scheduled internal-audit calendar is queued | Recorded; ADR hygiene and code review run continuously, digests daily; no audit of the management system exists |
| Scheduled risk-review cadence is queued | Recorded; a daily read-only digest exists (TSK-a8ba06); acting on it is not yet scheduled |
| Management-review meeting cadence is queued | Recorded; the discipline is the founder cold-read substrate in the readiness baseline |
| Network and segregation controls (A.8.20-A.8.22) are AWS-shared-responsibility in the readiness baseline | Recorded; in-platform application-layer controls carry the load |
| Backup posture (A.8.13) is queued | Recorded; the staged deployment relies on AWS RDS managed-service substrate |
| Redundancy (A.8.14) is out of scope in the readiness baseline | Recorded; the readiness roadmap names this as a queued surface |
| The risk register had no movement from 2026-04-29 to 2026-09-30; most open risks carry no review date and the two critical ones no owner | Recorded 2026-09-30 from the risk-review digest; assigning owners and dates is a Compliance & Quality unit |
| ISMS documents at `barecount-devhub/ISO27001/` are operator-internal | Recorded; they support the readiness posture; the public conformance position is this chapter |
| Statement of Applicability baseline is at the early-readiness percentage; the readiness roadmap drives the percentage upward | Recorded; the readiness roadmap is internal |
| The non-conformance register has no writer and has been frozen since 2026-08-24 | Recorded 2026-09-30; the writer is decided (DevHub's rule scan, TSK-aae076) and not yet built or proven |
| Coding-standard enforcement is uneven across repositories (warn-level rules bind only in bc-core and bc-portal; bc-admin does not lint) | Recorded 2026-09-30 per Quality Assurance; evening it out is queued with the Admin Portal and DevHub controllers |
| `bc-external-audit`, the auditor's own repository (the App tool server, the Mac service, the standing instructions), has no branch protection; its review on the exchange is practice, not enforced, and the operator merges it by hand | Recorded 2026-09-30; enforcement there is queued with the Audit Controller |

**Governing source.** DEC-ae331f; `barecount-devhub/ISO27001/`.

## Boundaries with Other Chapters

| Chapter | What it owns | What this chapter records |
|---|---|---|
| InfoSec and Access Control | The technical control surface | The conformance mapping that consumes the InfoSec controls |
| Decision and Change Procedure | The change-record plan-and-report pair, the ADR hygiene rules, the D268 session discipline | The conformance role of those substrates |
| Audit and Activity Logging | The audit substrate and the JSONL trail | The conformance mapping for A.8.15 Logging |
| Risk and Vendor Management | The risk register and vendor inventory | The conformance mapping for A.5.20 Supplier relationships |
| Quality Assurance | The per-repository enforcement, the coding rules as configured, the architecture gates, the non-conformance register's state | The conformance mapping for A.8.8, A.8.25 and A.8.28 |
| Privacy and the Immutable Fact | The nullification mechanism per `DEC-bd5492` | The conformance mapping for A.8.10 Information deletion |
| Operations: Upgrade and Migration | The migration discipline and backup posture | The conformance mapping for A.8.13 Information backup |
| Operations: Incident and Change Management | The incident triage path | The conformance mapping for the incident-response control |
| SOC 2 Conformance | The Trust Services Criteria mapping | The companion conformance posture per `DEC-ae331f` |
| Mac Auditor Operations | The auditor service, the exchange desk, the grants and their procedures | The conformance role of independent review as the A.8.32 change-management control |

**Governing source.** DEC-3395bc; The Authority Model.

## References

- The Authority Model
- DevHub
- Decision and Change Procedure
- Audit and Activity Logging
- InfoSec and Access Control
- Risk and Vendor Management
- Quality Assurance
- Privacy and the Immutable Fact
- SOC 2 Conformance
- Operations: Deployment Topology
- Operations: Upgrade and Migration
- Operations: Incident and Change Management
- Operations: Mac Auditor Operations
- Operations: Serve Moves and Live Windows
- DEC-ae331f (Staged pursuit of ISO 27001 readiness and SOC 2 Type I on reduced criteria)
- DEC-ebf0b4 (Session Discipline and Data Integrity Rules)
- DEC-a4e550 (ADR-First Decision Workflow)
- DEC-623f8f (ADR Hygiene Policy)
- DEC-441665 (NPM supply chain mitigation via AWS CodeArtifact)
- DEC-1918d0 (Two-database split)
- DEC-771baf (Tenant database topology)
- DEC-bd5492 (GDPR/DPDP/CCPA Nullification Object)
- DEC-ee6018 (Power of Ten adapted coding rules)
- DEC-5b760c (QA enforcement in per-repo CI; DevHub the sole NC authority)
- DEC-bebaec (Chain Completeness SSOT)
- DEC-804874 (L-Node Verification with Semantic Family Classification)
- DEC-081931 (Standing Claude-Codex exchange family gen-)
- DEC-44456d (bc-external-audit as the auditor's home; the Mac auditor service)
- DEC-fa7c63 (DSO family meaning; the metric-onboarding exclusion, grant ead781aa)
- ISO/IEC 27001:2022 (the international standard; external authority)
