---
uid: DEC-dc5d52
title: "Authority by derivation — platform-internal evidence is the sole intrinsic authority class"
description: "Metric semantic authority is asserted by BCF/MCF derivation, not external publisher citation; curators are DISCOVERY_ONLY and non-retainable."
status: decided
date: 2026-07-24T03:34:09.368Z
project: bc-core
domain: governance
subdomain: metric-audit
focus: governance
---

# Authority by derivation — platform-internal evidence is the sole intrinsic authority class

## Context

Two verified facts made the citation-based authority model untenable. (1) THE CITATION MODEL WAS NEVER ACTUALLY USED. Across the entire audit corpus (bc_audit_dev.audit_execution.response_packet_outbox), all 456 citations resolve to BareCount's own artifacts: 304 labelled "IFRS Foundation"/NORMATIVE, 146 "BareCount"/PRIMARY_AUTHORITATIVE, 6 "bc-external-audit" — every one pointing at platform:// substrate, docs/ramp5-exchange/evidence-*.json (AuditHub-retained bundles whose fragments are URL-encoded BareCount coordinates), or audit-run-artifact:. Not one citation points at an external publisher's document. The IFRS Foundation/NORMATIVE label is a pre-PR#68 compiler default stamped over internal locators (the TSK-877000 defect) and was never load-bearing. (2) EVERY AXIS ALREADY SITS AT THE PLATFORM-EVIDENCE CAP. All 78 packets score exactly 4 on each of definition, formula, canonical_input_semantics; nothing scores 5. The formula-axis rationale already says so in words: "Scored at the platform-evidence policy cap (4)." The corpus has been operating under authority-by-derivation de facto while declaring authority-by-citation de jure.

Separately, the operator directed that no external source be named or cited, including in internal records, to avoid creating a derivative-work or licence hook against curated compilations. The underlying formulas and definitions are public-domain facts; the curator's contribution is selection and arrangement, which is precisely what must not be retained.

This also aligns the audit track with Invariant I: meaning is evaluated once, at its own boundary. Importing an external publisher's meaning is a form of meaning drift.

## Decision

1. AUTHORITY BY DERIVATION. A metric's semantics are defensible because BCF concepts + MCF grammar + the pinned methodology derive them — not because a third party published them.

2. SOLE LEGAL PUBLISHER. `barecount` (publisher_class platform_internal, authority_rank 2, PRIMARY_AUTHORITATIVE) is the only legal publisher for platform-retained evidence; `bc-external-audit` remains legal for auditor-retained artifacts. Stamping an external publisher onto a `platform://` or AuditHub-bundle locator is prohibited. This is the forward-looking form of the TSK-877000 fix.

3. AXIS CEILING 4, BY INTENT. Score 5 requires two independent external rank-<=3 publishers; this doctrine forecloses that path. Nothing in the corpus scores 5 today, so the ceiling is declaratory, not a downgrade.

4. CURATORS ARE DISCOVERY_ONLY AND NON-RETAINABLE. Aggregators (KPI Depot, APQC-as-republished, textbook houses) may be consulted at authoring time as a verification oracle. Their prose, taxonomy, thresholds and arrangement must not be ingested, retained, cited, or carried into any governed record. This already matches qualifying_citation_rules.excluded_source_classes (search_result_snippets_and_aggregator_summaries).

5. NAMING A STANDARD IS NOT ATTRIBUTION. The mcf.evidence_source_allowlist entries (ifrs, gaap, xbrl_us_gaap, oagis, isa95) are retained. Naming a standard is nominative use and carries no derivation; the exposure is copying a standard's text, which this ADR does not authorise.

6. r4 AUTHORISED TO BE AUTHORED — NOT PINNED. source-authority-policy-v1.r4 is authorised, retiring external standard_setter and professional_body entries from the qualifying path and reducing the registry to platform_internal plus source_system_vendor (corroborative-only). AUTHORING r4 AND PINNING IT ARE SEPARATE ACTS. Rotating metric_audit.intrinsic_authority_pin to r4 is a governed write against live substrate with corpus-wide effect and requires its own DBCP, auditor notification, and operator authorisation. Nothing in this ADR permits a rotation.

7. SEED RESERVOIR QUARANTINED. mcf.seed_metric.raw_json retains third-party prose and arrangement for ~8,416 scraped rows. It is non-runtime and must be stripped to the fields actually consumed. No further curator ingestion is authorised.

CONSEQUENCES (verified read-only against live substrate 2026-07-24):

Unblocks TSK-877000 B2. assertExistingRequestsSuperseded (reintake.service.ts, origin/main) compares each projected decision against the current pin on nine fields, including source_authority_revision and source_authority_policy_digest. Evaluating the exact predicate: the 35 IFRS-labelled defect decisions (35 requests / 35 distinct MCVs) are admissible today (hence REQUEST_ALREADY_EXISTS) and become inadmissible after an r4 rotation (hence superseded, emit proceeds). This independently reproduces the recorded 35/36 split; the 36th historical row is already inadmissible.

BOUND 1 — B2 ONLY, B1 UNTOUCHED. All 35 still hold a live audit_reintake certification, so assertNotAlreadyIntaken refuses a second intake unchanged. Codex v5 ruling #1 (archive-on-cycle-close opener) remains REQUIRED. This ADR retires the class-(d) defect manifest and the B2 entry design — NOT correction-cycle Units 1-5 wholesale.

BOUND 2 — BLAST RADIUS IS THE WHOLE DECIDED CORPUS. All 38 live decisions across 36 MCVs carry the single r3 digest, so a rotation flips every one to authority-inadmissible, not just the 35. Nothing is rewritten (request_outbox is append-only) and re-emit is permitted, not triggered — but every decided MCV becomes re-emittable. Must be stated to the auditor.

BOUND 3 — ZERO OPERATIONAL STRAND; WINDOW IS CLOSING. metric_audit.fn_intrinsic_decision_refusal evaluates only audit_pending MCVs (c1_state_not_audit_pending). There are currently 0 MCVs in audit_pending; 339 are already active and are not re-evaluated against the pin. A rotation therefore strands no in-flight admission. That advantage disappears as soon as anything enters audit_pending.

ASSUMPTION ON RECORD: the predicate's `live` filter also requires closure_root == freshClosureRoot, computed in-transaction by ClosureResolverService and not reproducible in SQL. The 35's present REQUEST_ALREADY_EXISTS refusal is itself evidence that closure matches — had it drifted, class (a) would already fire.

NO SCORE OR VERDICT CHANGES. Relabelling IFRS Foundation/NORMATIVE to BareCount/PRIMARY_AUTHORITATIVE keeps every axis at 4, because checkGradeFloor (V-D8) needs one closure-bound rank-<=3 citation and barecount is rank 2.

FORMULA AUTHORITY FOR CONVENTION RATIOS BECOMES EXPLICITLY SELF-AUTHORED. The 2026-07-14 discovery report found only CFA Institute and APQC could ever have supplied external formula authority for DSO/DPO/turnover/margins; both are now out of scope. Accepted: those ratios are conventions, and BareCount's grammar deriving them is a stronger claim than a professional body having printed them.

THE P0/P1 EXTERNAL ACQUISITION PROGRAMME IS CANCELLED (FASB taxonomy, SEC Reg G, ESMA APM, PCAOB AS 2401, IAASB ISA 240, APQC OSB). Retained as historical context only.

IP POSTURE SHIFTS FROM "CITE CORRECTLY" TO "RETAIN NOTHING THIRD-PARTY". Non-attribution alone does not address contractual exposure — a curator's terms of use bind by contract regardless of whether the underlying facts are public domain. Non-retention does. Counsel review of any curator ToS before connecting remains outstanding and is NOT discharged by this ADR.

RISKS: auditor acceptance of r4 is required (the code-review engagement concluded 2026-07-19 and the operator is sole ratifier, but the pin rotation touches the exchanged wire contract); pin rotation is a governed act with live-substrate effect (DBCP + auditor sign-off apply); removing external publishers narrows any future path to score 5, accepted deliberately.
