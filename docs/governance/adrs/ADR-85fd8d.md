---
uid: DEC-85fd8d
title: "Directory entry rejection: a terminal, evidenced intent state for a Metric Directory entry (extends DEC-b5c7ff and DEC-5842d4)"
description: "A Metric Directory entry can be rejected through one governed act that records its evidence in the same transaction; rejected is terminal. Extends, does not supersede, DEC-b5c7ff and DEC-5842d4."
status: decided
date: 2026-10-02T12:53:58.868Z
project: bc-docs
domain: metrics
subdomain: metrics/metric-directory
focus: lifecycle
---

# Directory entry rejection: a terminal, evidenced intent state for a Metric Directory entry (extends DEC-b5c7ff and DEC-5842d4)

## Context

The balance goal needs a recorded end for entries that will not be built. Archive cannot carry it (reasonless, mutable, already meaning hidden), and the existing log cannot either (ungated, with no effect on state). One gated act with same-transaction evidence and a terminal rule gives a rejection that is true by construction, and reuses the directory's own append-only log.

## Context

The fleet is clearing the Metric Directory to a balance: every registered entry ends certified (derived through its realization) or rejected. The directory cannot record a rejection today.

Read at bc-core origin/main and the live platform database, read-only, 2026-10-02:
- `metric_directory.member.intent_state_code` allows only `planned` and `blocked`. DEC-b5c7ff D2: a member "owns ONLY its intent state (planned | blocked + reason)".
- `metric_directory.directory_decision` is append-only (`trg_directory_decision_immutable`), and its `decision_kind` CHECK already allows `rejection`. But DEC-5842d4 Phase 1 keeps it ungated, so a rejection row changes nothing.
- `archiveMember` sets the mutable `archived_at`, refuses a realized member, and discards its rationale (metric-directory.service.ts:1542-1545). Archive hides an entry; it records no decision.
- `revokeMemberRealization` is the precedent for a gated directory act: authority_ref plus rationale, the member lock, an append-only event in one transaction.

The design is barecount-devhub artifacts/architect/DESIGN-directory-entry-rejected-2026-10-02.md (PR 233, commit f8b10fb8).

## Decision

1. **State.** `intent_state_code` gains `rejected`. The intent set becomes planned | blocked | rejected. A rejected entry has no blocker.
2. **One governed act.** rejectMember(member, authority_ref, rationale of at least 40 characters), behind the operator role, in one transaction:
   - lock the member;
   - refuse a realized entry, or one with an operative realization (a built metric is withdrawn through MCF, not rejected here);
   - refuse an entry that is already rejected;
   - append one `directory_decision` row of kind `rejection`, carrying the member, the rationale, and in references_json the authority_ref and any prior blocker;
   - set the state, and clear the blocker.
   Planned, blocked and archived entries can be rejected.
3. **The evidence is the existing log; no new table.** For this kind the log is no longer ungated:
   - a database rule refuses a move into `rejected` unless a `rejection` decision for that member was written in the same transaction;
   - a `rejection` row must carry the member and an authority_ref.
4. **Terminal.**
   - The state never changes away from `rejected`.
   - A rejected entry cannot be realized or authored (the realization guard and the M12 door of DEC-fa9424 refuse it).
   - The feasibility re-evaluation skips it.
   - A wrong rejection is not undone: the idea is registered again as a new entry that references the rejected one.
5. **Authority.** Each rejection's authority_ref cites the operator's standing grant for the directory-clearing program. That grant is desk grant `2026-10-02T12-55-08-285Z-0a35dc47` (request 193), and every rejection row names it.
6. **No backfill.** The migration rejects nothing; each rejection is its own act.
7. **The migration** is the DB Controller's: a bc-db forward migration with its DBCP and the operator's DB yes, holding the rules of points 1, 3 and 4 with red-first vectors.
8. **Vocabulary.** "Entry rejected in the directory" joins slice 1, group 3. It is always said with its subject, never as plain "rejected".

This ADR extends DEC-b5c7ff (its D2 intent set) and DEC-5842d4 (its Phase-1 ungated log, for the rejection kind). It supersedes neither; their other points stand.

## Foundation gate

- Location C (intent binding, DEC-b5c7ff's own location), with the coupling held in the database.
- Not lower: a view that inferred "rejected" from archive plus a log row would infer proof.
- III: terminal; corrections are new entries.
- IV: authority_ref is explicit.
- VI: the evidence row is written with the act, in the same transaction.

## Status

Decided on 2026-10-02 by the operator's desk grant `2026-10-02T12-55-08-285Z-0a35dc47` (text SHA-256 `0a35dc479201702f057a67b7d82b9dfd2ac339aeb599ed91196a34e643c6591f`, request 193). The grant approves this ADR as written in bc-docs pull request 160 at commit 66561c16, and records the clearing-program standing grant of point 5. The only changes since that commit are this status paragraph and the grant id in point 5.
