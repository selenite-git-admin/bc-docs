---
uid: DEC-3078ce
title: "Source catalog onboarding workflow — evidence-bound verification, explicit transitions, no born-approved rows"
description: "Catalog governance v2: extract admission is the sole birth path for new-system rows (born registered/unverified, artefact-bound); verification is a mechanical governed act citing the artefact (D553 pt 4), not an AI panel; approval is an explicit operator transition; promotion stripped from PATCH; retirement is archival, never DELETE, for approved rows; SC/AC authoring follows approval."
status: decided
date: 2026-08-07T16:46:57.739Z
project: bc-core
domain: sources
subdomain: source-catalog
focus: governance
---

# Source catalog onboarding workflow — evidence-bound verification, explicit transitions, no born-approved rows

## Context

The operator flagged that catalog services predate the BCF/MCF governance era; a read-only study confirmed every gate the SOP describes is either dead (verify endpoint, log writers) or absent (promotion guard, transition enforcement, soft deletes), with the substrate holding no triggers at all. The trust mechanism that once justified a panel (hand-typed entries) is superseded by manifest-bound instance extracts whose evidence is mechanical — so the right-weight workflow binds status to evidence and explicit operator acts rather than to opinions, keeping ceremony proportional (D541 clause 4; governance-must-earn-its-keep). Deciding this before finishing UNIT-2 avoids minting more born-approved rows that would immediately need re-governing.

## Decision

Measured context (2026-08-07, SES-20d4d3, live substrate + code): the enforcement-surface map has no `source` section; `source.*` carries zero triggers and only vocabulary-enum CHECKs; `POST /api/ai/suggest/source-verify` does not exist in bc-core (orphaned by the D483 bc-ai retirement — BCF/MCF panels moved in-process, the catalog's surface never did); `operations.catalog_verification_log` has zero writers; `updateObject`/`updateField` accept `catalogStatus`/`verificationStatus` freely; `deleteObject`/`deleteField` are hard DELETEs and no catalog table has `archived_at`; `registerSourceStack` creates objects and fields born-`approved` with no verification act. The contract lane (SC/AC state machine + activation gates) is properly governed and is not changed by this decision.

**The workflow (middle-weight by design: evidence-bound and mechanical, per D541 clause 4 — rules before judgement; no panel for what a hash can check):**

1. **One birth path.** For a newly onboarded system, catalog rows (identity chain, objects, fields) are born through extract admission (D551 Amendment 1 input) at `catalogStatus: registered`, `verificationStatus: unverified`, bound to a `source_catalog_artefact`. Born-approved creation is retired for this path. (SAP's existing rows are grandfathered as-is; their disposition rides the deferred withdrawal, TSK-af584d.)

2. **Verification is a governed mechanical act.** For a self-describing source, `verified` means what D553 pt 4 says: the row is declared by a hash-bound, evidence-grade extract of the declared version (and later re-derivation refreshes it). The verification act cites the artefact and writes `operations.catalog_verification_log` — giving that table its writer at last. No AI panel: the panel compensated for hand-typed entries; a manifest-bound extract is stronger evidence than a model's opinion.

3. **Approval is an explicit operator transition** (`registered → approved`, requiring `verified`), exposed as a small transition surface; `deprecated`/`archived` are one-way beyond it. `catalogStatus` and `verificationStatus` are STRIPPED from the update DTOs — transitions happen only through the transition surface, each writing the verification log. A minimal substrate guard (mcf-pattern-lite trigger refusing backward transitions and unverified approvals) ships as its own DBCP — design here, apply separately gated.

4. **Retirement is archival.** A row that ever reached `approved` is never hard-deleted; `deleteObject`/`deleteField` refuse unless the row is still `registered`+`unverified`. (Full `archived_at` columns would breach nothing but are not required — `catalog_status='archived'` is the retirement state; hard-delete remains only for admission mistakes caught before verification.)

5. **SC/AC authoring FOLLOWS approval.** The one-call fused stack (create object+fields+SC+AC born-approved) is retired for new-system onboarding: `registerSourceStack` survives unchanged as the post-approval SC/AC author (it already handles existing objects), but its object/field-creation leg is not the birth path for extract-admitted systems. Sequence: admit → verify → approve → author SC/AC → (chain continues per SOPs).

**Consequences accepted:** bc-admin catalog screens that PATCH statuses will need repointing to the transition surface (follow-up task); the source-registration Onboarding chapter is annotated in the same change (its AI-verify endpoints are dead references post-D483); UNIT-2 (in flight) is reworked to these semantics before review. The workflow deliberately does NOT add: panels, couriers, certification records, or any transport — certification-grade ceremony is reserved for the metric lane.
