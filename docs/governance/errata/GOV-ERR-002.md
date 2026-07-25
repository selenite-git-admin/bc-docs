---
id: GOV-ERR-002
title: "DEC-97445d applied-instance clause (c): re-signing canary B is structurally impossible; the EXACT_REPROOF canary moves to a fresh subject"
status: adopted
authority: authoritative
affected: docs/governance/adrs/ADR-97445d.md (bc-docs main `4c63d79`) — Decision, applied-instance clause (c) "canary B re-signed by the auditor as enforcement-2 seq 1/2 and republished"
temporary_governance:
  - AuditHub schema (bc_audit_dev audit_execution) — code/DDL is SoT for run/packet identity
  - docs/MEMO-Claude-feed-epoch-successor-enforcement-2-2026-07-25.md items 3.3–3.4 (corrected by this erratum)
target_resolution: None required beyond this erratum — doctrine and clauses (a), (b) [as corrected by GOV-ERR-001], and (d) stand; this erratum governs the corrected reading of clause (c).
opened: 2026-07-25
---

# GOV-ERR-002 — DEC-97445d clause (c): re-sign is impossible; the canary moves to a fresh subject

## Contradiction summary

Clause (c) directed the auditor to re-sign canary B (request `650d3139`, audit run `65c3eb5b`) onto
enforcement-2. Verified live against the auditor substrate: `audit_execution.audit_run` and
`audit_execution.work_item` are both `UNIQUE (request_uid)`, and `response_packet_outbox` is
`UNIQUE (work_item_uid)` — one request maps to exactly one run, one work item, and one packet, forever.
The retained run is CLOSED and its outbox row immutably binds the enforcement-1 packet digest. The
auditor's accepted M6 publication service additionally refuses on run-state and preflight, as designed.
There is no sanctioned lane to re-sign a closed run onto a new feed, and none should be built.

The platform mirror-image is equally guarded: the subject (MCV `95ff564c`) is `audit_pending`
(requestAudit is approved→audit_pending only), and no existing request-supersession class fires for a
request that is pin-current at unchanged closure. A "stranded by feed retirement" supersession class
would be new machinery for a population of one — it fails the DEC-97445d line-drawing rule.

## Corrected reading of clause (c)

The EXACT_REPROOF arm is proven on a **fresh subject** ("canary B-prime") through entirely existing
paths: an approved corrective-successor member of the accepted v4 manifest's reproof-admissible cohort
that already holds an EXACT row in `mcf.exactness_reproof_evidence` (56 such candidates verified
2026-07-25). Lane: platform `requestAudit` (approved → audit_pending, fresh request, metric-audit-request
seq 3) → auditor opens a FRESH work item/run for that request → signs and publishes on enforcement-2 as
its genesis seq 1/2 → platform consumes through the governed workflow → admit with basis EXACT_REPROOF.

## Disposition of the stranded pair

MCV `95ff564c` (canary B, pin-current request, permanently unanswerable after the epoch cut) parks in
`audit_pending` alongside `e44a1c1e` (canary A's halt residue, whose r2-stamped request already
qualifies for class-(b) authority-inadmissible supersession under existing machinery whenever exercised).
Both are documented epoch residue: preserved, unreferenced, dispositioned later through existing or
future correction machinery — never hand-edited.

## Doctrine impact

None. Both refusals are positive proofs of the fail-closed identity model on each side.
