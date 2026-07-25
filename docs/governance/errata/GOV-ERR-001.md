---
id: GOV-ERR-001
title: "DEC-97445d applied-instance clause (b): cross-feed registration supersession is structurally invalid"
status: adopted
authority: authoritative
affected: docs/governance/adrs/ADR-97445d.md (bc-docs main `4c63d79`) — Decision, applied-instance clause (b) "using feed_registration.supersedes_registration_uid = fa3b388d-bab2-40e9-b81f-ff89010792c2"
temporary_governance:
  - bc-core metric_audit.fn_feed_registration_guard (DB guard — code is SoT for chain semantics)
  - artifacts/metric-audit/MEMO-feed-epoch-successor-enforcement-2-2026-07-25.md (devhub `a9b6a47`) — item 3.2 "Declare supersession of registration fa3b388d…" is corrected by this erratum
target_resolution: None required beyond this erratum — the doctrine and every other clause of DEC-97445d stand unchanged; this erratum governs the corrected reading of clause (b).
opened: 2026-07-25
---

# GOV-ERR-001 — DEC-97445d clause (b): cross-feed registration supersession is structurally invalid

## Contradiction summary

DEC-97445d's applied instance, clause (b), directed the successor-feed C1 registration for
`bc-external-audit.metric-audit-decision.enforcement-2` to declare
`supersedes_registration_uid = fa3b388d-bab2-40e9-b81f-ff89010792c2` (the enforcement-1 registration).

The platform substrate refuses this, correctly. `metric_audit.fn_feed_registration_guard` binds
`supersedes_registration_uid` to a **within-feed-name** chain: the first registration of a feed name
must not supersede anything (`first registration for <feed> must not supersede`, P0001), and any later
registration must supersede exactly that same feed's current un-superseded head
(`fn_effective_feed_registration` resolves heads per feed name). Cross-feed supersession is not what
the column means.

Observed live 2026-07-25: import attempt `d954fe39-ec14-4181-824a-359e6f25956a` (control-1 seq 2,
envelope digest `sha256:a0d7a92e…`) was rejected fail-closed at the projection guard — no feed event
appended (control-1 head remains seq 1), no verified attempt row, no registration row. Sequence 2
remains free.

## Corrected reading of clause (b)

The enforcement-2 registration is a **first registration**: `supersedes_registration_uid` is absent/null.
Enforcement-1's retirement is effected — as the rest of DEC-97445d already provides — by:

1. the ratified decision itself (this ADR),
2. the platform consumer's program-feed constant moving to enforcement-2 (the reviewed PR in clause (d)), and
3. the evidence linkage carried in the registration envelope's subject (which binds the ratified memo's
   sha256 `dfd9f779…`) and the auditor-side bootstrap `authority_ref`.

Registration supersession plays no role in an epoch cut across feed names. Enforcement-1's registration
remains the un-superseded head of its own (retired) feed name — which is historically accurate.

## Doctrine impact

None. The doctrine (re-anchor by successor registration, never mutation) and all other clauses stand.
The refusal itself is a positive proof of the substrate's fail-closed chain-position guard.
