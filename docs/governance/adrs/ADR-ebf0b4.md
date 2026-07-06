---
uid: DEC-ebf0b4
title: "Session Discipline & Data Integrity Rules (NOT-TO-DO)"
description: "10 mandatory rules preventing bulk data generation, cosmetic status fixes, and unverified chain wiring"
status: implemented
subdomain: devhub-governance
focus: discipline-rules
date: 2026-04-03
domain: governance
authority: authoritative
decision_code: D268
migrated_from: legacy v2 archive
---

# Session Discipline & Data Integrity Rules (NOT-TO-DO)

## Context

PLN-c028cd Phase 3+ session (2026-04-03) attempted to wire the full finance contract chain end-to-end via bulk seed scripts. Created 55 observation contracts, 1,022 field maps, 48 source contracts, 43 admission contracts, and 221 reader bindings. The integrity chain UI showed green/full status for most KPIs.

**The problem:** None of it could actually produce metric snapshots. The chains were structurally present but functionally hollow. 591 business fields were cosmetically marked as "derived" to suppress partial status. The user correctly identified this as a Potemkin village and ordered a full revert.

**The cost:** ~9 hours of session time wasted. All data reverted. Trust damaged. If this had happened in production with a tenant's data, it would violate audit integrity and destroy confidence in the platform's observability promise.

**Root cause:** Speed was prioritized over correctness. Bulk generation was used instead of individual verification. Script output was trusted as proof instead of independent verification.

## Decision

10 mandatory rules, organized in three categories. All Claude sessions MUST obey these rules. Violation of any rule must be self-reported at session close.

### Data Integrity (absolute — no exceptions)

**Rule 1: Never bulk-generate contract chain data.**
Each observation contract, admission contract, and reader binding must be built individually with verified field mappings. If it takes 10 sessions to do 45 BOs properly, that's the cost. Bulk INSERT scripts for contract chain layers are prohibited.

**Rule 2: Never mark data as something it isn't.**
No cosmetic status changes — marking fields "derived" when they're unmapped, marking chains "full" when they can't produce output, setting governance_state to "approved" without review. Honest amber/red is always better than fake green.

**Rule 3: Never modify business field metadata without a verified source.**
Changes to source_aliases, contract_json, business field classifications, or any chain metadata must trace to a verified source: SAP DDIC documentation, user-approved design, or auditable reference. "AI suggested it" is not sufficient alone.

**Rule 4: One-then-many.**
Before scaling any data operation to N records, prove it works end-to-end on ONE record — with the user seeing the proof. The proof must demonstrate the full chain (metric contract > canonical > observation > admission > reader > source) producing a real result, not just status indicators.

### Session Discipline

**Rule 5: Plan granularity matches risk.**
Data-touching steps must be individual line items in the session plan, not grouped. "Create 55 OCs" is not a valid plan step. "Create OC for gl_journal_entry, verify field chain end-to-end, confirm metric snapshot path" is. Each step must be independently reversible.

**Rule 6: Checkpoint after every data mutation.**
Not after completing a batch — after each individual mutation. The checkpoint must state: (a) exactly what changed, (b) how to verify the change independently, (c) how to revert if wrong. Use devhub_session_checkpoint.

**Rule 7: Self-audit at session close.**
Every devhub_session_close must include a discipline report answering:
- Which of the 10 rules were relevant this session?
- Were any rules tested (temptation to violate)?
- Were all rules obeyed?
- Any near-misses to flag?

### Verification

**Rule 8: Proof before proceeding.**
After any data change, show the user the actual state via independent query or API call — not a summary of what the script claims it did. The verification must use a different code path than the mutation.

**Rule 9: Never trust script output as verification.**
The script that creates data cannot also be the verification. "Script said: 55 OCs created" is not proof. An independent SELECT count(*) or API call is proof. Script logs are breadcrumbs, not evidence.

### Escalation

**Rule 10: If a shortcut tempts, stop and flag it.**
If the "fast" path involves bulk generation, cosmetic fixes, skipping verification, or assuming correctness — that is the signal to pause and discuss with the user. Say: "I see a shortcut here but Rule N says I should not. Here is the proper path and what it costs." Speed is not a value. Correctness is.

## Consequences

- Sessions will be slower. Data work will take multiple sessions instead of one. This is correct.
- Honest partial/amber status will be visible longer. This builds trust instead of eroding it.
- Every session close includes a discipline self-audit. This creates accountability.
- Violations are logged. Repeated violations trigger process review.

## Enforcement

- Rules are in CLAUDE.md (loaded every session).
- Rules are in auto-memory (persists across conversations).
- Self-audit is mandatory at session close.
- User can invoke D268 by name to remind Claude of these rules mid-session.

## References

- PLN-c028cd Phase 3+ session (SES-0ed6d0) — the failure that prompted this decision
- Revert script: bc-seed/scripts/revert-finance-chain.cjs
- Database Change Protocol (CLAUDE.md) — complementary, covers schema changes
- Database Rules (D162) — complementary, covers data design
