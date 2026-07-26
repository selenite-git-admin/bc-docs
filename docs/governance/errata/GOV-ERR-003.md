---
id: GOV-ERR-003
title: "DEC-b7d74b retirement scope is broader than the evidence supports: the request lane stays"
status: adopted
authority: authoritative
affected: docs/governance/adrs/ADR-b7d74b.md (bc-docs main `31907fc`) — Decision, "WHAT IS RETIRED (the courier, dev corpus)" clause, specifically "one-shot request/run/packet identity as the delivery model"
temporary_governance:
  - bc-core metric_audit.request_publication / metric-audit-request feed (code + substrate are SoT for the request lane)
  - docs/DESIGN-Claude-c11-checker-origin-respecification-v2-2026-07-26.md (auditor repo) §2 — the narrowed scope this erratum records
target_resolution: None required beyond this erratum — the doctrine, the preserved gate, the four maker/checker invariants and the honesty requirement of DEC-b7d74b all stand unchanged; this erratum narrows one clause of the applied instance.
opened: 2026-07-26
---

# GOV-ERR-003 — DEC-b7d74b retires the response lane, not the request lane

## Contradiction summary

DEC-b7d74b's retirement clause reads broadly enough to include the platform's **request** publication
lane ("one-shot request/run/packet identity as the delivery model"). The evidence does not support
retiring that lane, and the c11 design work surfaced why.

Measured live 2026-07-26:

| Lane | Record |
|---|---|
| `metric-audit-request` (platform → checker) | 27 publications, sequence 1→27 monotonic; **zero epoch cuts, zero wedged chains, zero strandings attributable to it** |
| response lane (checker → platform) | **two epoch cuts** (enforcement-1, enforcement-2), one pickup wall, one wedged chain, twelve stranded subjects |

Every incident the program suffered originated on the response lane. Request publication is
platform-side signing with the platform's own key, one KMS call at emit, with no cross-process protocol
and no counterparty coupling.

## Corrected reading

DEC-b7d74b retires the **response lane** — auditor packet signing, response-feed sequence chains and
prior-digest continuity, epoch cuts as recovery, outbox/pickup transport, one-shot run/packet identity as
the delivery model, and bootstrap-authority pinning as a program gate.

The **request lane is preserved**: requests continue to be emitted, signed and published on
`metric-audit-request`.

## Consequences (all reduce scope and risk)

1. `metric_audit.decision.request_uid` (NOT NULL, FK → `request_publication`) **requires no relaxation**.
   The c11 re-specification therefore touches two nullable widenings (`feed_event_uid`, `feed_mode`)
   instead of three couplings.
2. **CRV-002 requires no re-binding for the ongoing model.** The auditor's accepted re-binding
   (RESPONSE-Codex-D535-CRV-002, sha `aa7357e7…`) remains valid and more general, but the original
   "published request" clause continues to hold because requests continue to be published.
3. The one-shot burn hazard dissolves without retiring the lane: an incorrect verdict is superseded
   through the existing `decision.supersedes_decision_uid` chain, requiring no new request identity.

## Doctrine impact

None. The doctrine of DEC-b7d74b, the preserved admission gate and CRV catalogue, the four dual-model
maker/checker invariants, and the distinct-provenance honesty requirement all stand unchanged. This
erratum narrows one clause of the applied instance to match the measured evidence.
