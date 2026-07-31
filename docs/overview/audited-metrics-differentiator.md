---
id: audited-metrics-differentiator
order: 3
title: "Audited Metrics Differentiator"
status: drafting
authority: informative
depends_on: [platform-overview, structural-differentiators, the-invariants]
governing_sources:
  - Foundation (the locked architectural authority)
  - The Invariants
  - The Authority Model
  - The Contract Grammar
  - The Evaluation Boundaries
governing_adrs:
  - DEC-67f399 (D521 - base/derived composition doctrine; hybrid forbidden)
  - DEC-29c80b (D523 - single-plane audit lifecycle; SUPERSEDED by DEC-793e13 on the "externally audited" claim)
  - DEC-793e13 (D540 - audit exchange retired; active means PANEL-CERTIFIED, not externally audited)
errata_referenced: []
---

# Audited Metrics Differentiator

> **CORRECTION — 2026-07-31, DEC-793e13 (D540).** The external metric-audit exchange is retired. BareCount
> does **not** externally audit its own metrics; it **panel-certifies** them in-process. Anywhere this draft
> implies independent or external audit of a metric, read *panel-certified*. The distinction is not
> cosmetic: an external audit is performed by a party that cannot be overruled by the audited, and no such
> party is in the loop today. Do not carry the phrase "externally audited" into any narrative, deck,
> website, sales material or product surface derived from this document.
>
> This does not weaken what is claimable. A recorded cross-family maker/checker/moderator panel act per
> metric, with immutable decision and evidence, remains a real and defensible differentiator (DEC-05815d,
> preserved). If genuine independence is ever required, canonical decision records can be exported and
> counter-signed by a third party.

## Purpose

This document collects the technical reference points for a future BareCount brand and product narrative:

> Most metric platforms provide curated metrics. BareCount is building independently audited, calculator-grade metrics.

This is not current marketing copy and does not authorize a public claim that every BareCount metric is already audited. It defines what the claim must mean, which mechanisms make it defensible, and which proof must exist before the language is used without qualification.

"Independent" in this document means an audit subsystem with separate repository, database, rulebook, validators, signing authority, and decision stream from the platform that authors and consumes metrics. It does not mean an accredited third-party certification body, and it must never be presented as ISO certification, accreditation, or a statutory audit.

## The category distinction

### Curated

A curated metric has been selected, named, organized, or documented by a person, vendor, community, or model. Curation may be valuable, but by itself it does not prove that:

- the definition names the quantity actually computed;
- the formula faithfully implements the definition;
- the source object and field carry the assumed business meaning;
- grain, time, sign, currency, unit, null, duplicate, precision, and rounding behavior are correct;
- upstream metric dependencies resolve to exact audited versions;
- the reviewed version is the version executed in production;
- later source, contract, dependency, policy, or runtime drift has not invalidated the conclusion.

### Verified

A verified metric has passed deterministic checks against a stated contract. Verification can establish schema validity, package identity, dependency closure, composition, executable exactness limits, lifecycle eligibility, and other machine-recomputable facts. It does not independently establish that the business definition, formula intent, or source realization is contextually correct.

### Audited

An audited metric has been independently assessed against governed evidence across separate correctness axes. At minimum:

1. **Integrity:** exact subject, package, closure, authority, evidence, and dependency identities are recomputed.
2. **Definition:** the named business quantity, population, boundary, timing, and exclusions are correct.
3. **Formula:** the executable computation implements the definition, including edge semantics.
4. **Source realization:** the exact source system, release, object, field, configuration, and transformation mean what the metric assumes.
5. **Adversarial review:** the evidence is tested for contradictions, false passes, unsupported inference, and correlated reasoning errors.
6. **Reconciliation:** dissent is preserved and one schema-valid report, NC set, and decision candidate is assembled without majority vote overriding a blocking defect.

The audit binds an exact Metric Contract Version, package digest, dependency-closure root, Directory intent/realization coordinates, authority revisions, methodology, policy, engine, evidence digests, and signed request/report/decision chain. It does not attach a timeless badge to a metric name.

### Calculator-grade

Calculator-grade is the operational admission claim. It requires a current effective PASS decision for the exact version and identities being consumed, with all admission predicates satisfied. A historically passed but revoked, superseded, drifted, invalidated, stale, non-exact, or differently bound version is not calculator-grade.

The intended customer-facing ladder is therefore:

| Level | Meaning | What it does not imply |
|---|---|---|
| Curated | Selected and documented | Correctness |
| Verified | Deterministic structural checks passed | Contextual correctness |
| Audited | Independently assessed against governed evidence | Current production admission |
| Calculator-grade | Audited, admitted, current, and consumable under the gate | External certification or universal fitness |

## Why the difference is structural

The differentiator is not the word "audit" or a review checklist. It is the separation and closure of the system:

- the platform authors metrics but cannot issue its own auditor verdict;
- the auditor receives an immutable, signed request for an exact package and closure;
- the auditor maintains its own governed PostgreSQL store and authority/rulebook history;
- platform and auditor validators independently implement the pinned wire contracts and agree on cross-engine vectors;
- AI/Desktop panel outputs are unsigned analysis, not authority;
- the audit server validates, reconciles, signs, and publishes governed artifacts without giving models the signing key;
- reports, findings, NCs, compliance responses, decisions, supersessions, revocations, and later invalidations remain append-only;
- bc-core imports only authenticated, registered, sequence-continuous feed events;
- relational closure proves request to publication to report to finding/NC to decision consistency;
- lifecycle admission fails closed when required evidence or currency is absent.

This allows BareCount to say more than "experts reviewed our KPI library." The intended claim is reproducible: a reviewer can identify the exact audited object, evidence, rules, decision, current status, and reason the platform permits or refuses consumption.

## Contextual authority discipline

Contextual audit is evidence-led, not transcript-led. Panel transcripts, model memory, search snippets, and AI summaries are discovery material only. Calculator-grade conclusions require governed sources under a versioned source-authority policy.

The authority system distinguishes controlling standards and regulation, source-system publisher evidence, qualified professional guidance, and uncontrolled explanatory material. Scores are capped when authority facts, release match, exact object/field locators, publisher independence, or conflict resolution are missing. A polished consensus cannot raise an axis above the evidence-supported cap.

This is especially important for source realization. The audit scope is not limited to SAP or ERP systems. Every onboarded source system must prove the exact release, object, field, configuration, and transformation semantics used by the metric.

## Evidence a customer should eventually be able to inspect

For each calculator-grade metric version, the product should expose or report:

- stable metric and version identity;
- human name and definition;
- formula intent and executable identity;
- exact package and dependency-closure digests;
- origin classification and Directory realization or governed off-pool exception;
- audit date, methodology, policy, engine, and authority revisions;
- definition, formula, and source-realization scores and rationales;
- structural, Foundation, semantic-conformance, and exactness outcomes;
- counted source citations and their authority qualifications;
- open blocking and nonblocking NCs;
- current decision state, supersession/revocation/invalidation status, and currency;
- evidence and reproduction coordinates appropriate to the customer's access rights.

The UI may summarize these facts, but the summary must derive from governed records. A badge must never become a second source of truth.

## Current implementation position

The following foundations exist or have been independently reviewed:

- versioned Directory intent and realization authority;
- base/derived composition doctrine with hybrid rejection;
- deterministic exactness analysis and evaluation-policy/package identity;
- independent audit repository, PostgreSQL governance/execution store, rulebook, authority pinning, and startup checks;
- governed Desktop/MCP work items, verified context packages, leases, recovery, structured submissions, and bounded panel roles;
- pinned request/report/NC/CR/decision/feed-registration wire contracts and independently implemented cross-engine validators;
- signed request outbox/publication and authenticated inbound feed substrate;
- accepted C3 decision-stream design covering report, finding, NC, decision, supersession, REVOKE, structural/effective heads, and permanent child-set closure.

The unqualified public product claim remains pending until Track C implementation and proof complete the end-to-end path, including lifecycle states, admission gate, invalidation/cascade behavior, shadow operation, enforcement cutover, and a real audit/NC/remediation/re-audit scenario.

## Daily decision authority and the regulatory-filing boundary

BareCount's primary product role is a **daily calculator-grade metric authority for management,
CXO, and Board use**. This is not a lesser version of a filing product. Statutory filing tools are
periodic downstream systems: they assemble approved financial statements or disclosures, map them
to prescribed formats or taxonomies, and manage submission. They do not ordinarily provide the
continuously governed, version-exact definition, formula, source realization, dependency closure,
calculation, contextual audit, and current-admission plane BareCount is building for everyday
decision-making.

The product boundary has three distinct levels:

1. **Calculator-grade management reporting** is the present target. BareCount computes and serves
   governed daily metrics with reproducible lineage and current audit status for management and
   Board decisions.
2. **Filing-supporting metrics** are a future controlled integration target. An exact BareCount
   result may enter a customer's disclosure or filing workpapers only when it is reconciled to the
   customer's approved close, bound to the reporting entity/period/scope, approved through the
   customer's controls, and exported with an inspectable evidence package.
3. **Regulatory filing system of record** is not a current BareCount claim. BareCount does not by
   implication own statutory books, group consolidation, eliminations, foreign-currency
   translation, accounting estimates and adjustments, tax, financial-statement approval, taxonomy
   judgment, XBRL instance creation, or regulator submission.

The intended controlled flow is therefore:

```text
Source systems -> accounting close/consolidation -> approved balances/statements
                                           |-> statutory filing/disclosure system
                                           |-> BareCount metric calculation
                                                   -> reconciliation and evidence
                                                   -> Board reporting or controlled filing workpaper
                                                   -> human-approved disclosure/filing system
```

For a filing-supporting use, BareCount should emit an **attested metric package** that binds at
least the exact Metric Contract Version, formula and runtime identity, reporting entity/period and
scope, source realization and snapshots, input balances, result, reconciliation to the closed
ledger or approved statement line, adjustments, approvals, audit decision, unresolved NCs,
restatement lineage, and destination disclosure/taxonomy coordinate. The destination filing
authority remains external to BareCount unless a separately governed future program deliberately
assumes it.

This boundary permits a strong but honest market position:

> BareCount produces calculator-grade, independently auditable metrics for daily management,
> Board, and controlled disclosure workflows. It can support regulatory reporting where an
> approved metric is mapped into the customer's governed filing process; it is not itself the
> statutory books, consolidation engine, or filing authority.

Selected metric-based regulatory disclosures may become bounded future assurance programs without
turning BareCount into a complete filing platform. Each such program requires its own governing
standard, applicability, source scope, control mapping, reconciliation, approval, export, and claim
review.

## Deferred metric-centered collaboration

After Track C E2E acceptance, add a bounded customer-portal collaboration layer so BareCount can
become the daily workspace around a trusted metric, not merely the place where its value is viewed.
The first unit should remain deliberately smaller than a general chat product:

- governed metric knowledge, definition, formula, source realization, and audit status remain
  read-only projections of their platform authorities;
- tenant users may create attributed, timestamped, versioned, and supersedable pinned notes that
  explain a business situation without changing metric meaning or execution;
- a metric discussion supports replies, mentions, attachments, resolution, and links to a displayed
  value, period, entity, comparison, anomaly, or finding;
- a discussion message is non-authoritative unless promoted through a governed action into a pinned
  note, task, exception, correction request, or audit request;
- conversation attaches to the stable metric identity, while each relevant item may additionally
  bind the exact Metric Contract Version, tenant, reporting entity, period, and calculated snapshot;
  this prevents later discussion from being misapplied to a different version or number;
- customer collaboration records live in the tenant/customer collaboration plane, not
  `metric_audit.*`, MCF, or Metric Directory; and
- no portal note or message may directly mutate a Metric Contract, source mapping, audit verdict,
  or calculator-grade admission state.

The initial portal surface should provide `Notes` and `Discussion` views on metric detail, pinned
notes, threaded replies, `@mentions`, resolve/reopen, deep links, edit history, role-based
visibility, notifications, and promotion to a governed note or action. Opening trigger: Track C E2E
accepted and the tenant collaboration retention/access model approved. Until then this section is a
product-direction record, not implemented capability.

## Claim controls

Until the end-to-end gate is implemented and evidenced, permitted internal language is:

> BareCount is building a version-bound independent audit and admission system for calculator-grade metrics.

After successful shadow and enforcement proof, a stronger claim may become supportable:

> BareCount metrics marked calculator-grade are independently audited across definition, formula, source realization, structural integrity, and executable exactness, then admitted through a current fail-closed gate.

The following claims remain prohibited unless separately substantiated:

- "all BareCount metrics are audited" while any active/served population lacks current admission;
- "error-free," "guaranteed correct," or equivalent universal claims;
- "ISO certified," "accredited," "statutory audit," or "third-party certified" based on this internal independent subsystem;
- claims that a metric name, family, or historical version inherits another version's audit;
- claims that curation, panel consensus, structural verification, or a prior PASS alone equals calculator-grade currency.
- "regulatory filing ready," "statutory reporting system," or equivalent language unless the
  exact filing scope and its additional close, reconciliation, approval, taxonomy, submission, and
  external-assurance controls have been separately implemented and evidenced;
- claims that filing-supporting evidence transfers statutory preparer, management, Board, auditor,
  or filing-authority responsibility to BareCount.

## Brand-narrative seeds

Future narrative work may build from these technically supportable themes:

- **Audited, not merely curated.**
- **A metric is a governed calculation, not a dashboard label.**
- **Correct definition. Correct formula. Correct source. Exact version.**
- **Trust that can be inspected, reproduced, revoked, and renewed.**
- **Calculator-grade is an admission state, not a marketing adjective.**

These are narrative seeds only. Final customer language must pass documentation, legal/claim, language-system, and current-evidence review before publication.

## GTM positioning note: the missing trust layer

The strongest go-to-market position is not that BareCount invented metrics, formulas, dashboards, or
audit. Those categories already exist, and many individual formulas are common business knowledge.
The opportunity is that enterprise AI and enterprise analytics still lack a disciplined trust layer
between source systems and business-performance answers.

The hard gap is operational, not conceptual:

- everyone can name metrics;
- many tools can calculate or visualize them;
- AI can explain or summarize them;
- but very few systems bind definition, formula, source realization, runtime behavior, evidence,
  audit decision, lifecycle state, and revocation into one inspectable chain.

BareCount should therefore avoid the broad claim "we solved enterprise data." A sharper and more
credible claim is:

> BareCount is building the missing governed calculation and audit layer between enterprise systems
> and AI-generated business-performance answers.

For enterprise customers, this should translate into board-grade daily visibility, ERP-aware metric
governance, and evidence-backed confidence in the numbers used for management decisions. For AI
platforms and large technology partners, the more strategic framing is a semantic calculation trust
substrate: a way for AI systems to answer performance questions using governed definitions,
formulas, source mappings, exact versions, and reproducible calculation evidence.

This is not a claim that integration is trivial, that every source mapping is automatically correct,
or that BareCount replaces the customer's books, close process, filing tools, or statutory audit. It
is a claim that the trust substrate those systems need can be made explicit, versioned, audited, and
operational.

## Promotion condition

After Track C lands, this draft should be reconciled against the exact implemented migrations, services, tests, apply receipts, panel certification records, and final bc-docs authority revision. Only then should its accepted content be folded into the canonical product overview, structural differentiators, website, sales material, and product UI.

**Additional promotion gate (DEC-793e13):** before any of this reaches a customer-facing surface, every
audit claim must be restated in self-certification terms. "External-auditor acceptances" was a promotion
precondition under the retired exchange; no such acceptances exist or will exist under the current design,
and the phrase must not be satisfied by substituting the platform's own verdicts for a third party's.
