---
id: lessons-platform-readiness-umbrella
order: 44
title: "Lessons: Platform Readiness umbrella (2026-09-25 to 27)"
status: drafting
authority: informative
depends_on: [devhub, decision-and-change-procedure, dev-workstation-mac-mini]
governing_sources:
  - Tenant Readiness Program (implementation/tenant-readiness-program.md)
  - DevHub plan PLN-31c4a1 (the umbrella roadmap)
governing_adrs:
  - DEC-081931 (the permanent gen- Codex exchange)
errata_referenced: []
---

# Lessons: Platform Readiness umbrella (2026-09-25 to 27)

## What happened

The umbrella ran for three days. It ended on 2026-09-27, when the journal-entry pilot was proven on Kaveri: MLS 15 to 23 went green for `total_journal_entries`, per legal entity, with the server logged in only as the restricted runtime roles. The operator asked for these lessons to be written down before the next arcs are set up, and called them critical. The record of the run is in the [Tenant Readiness Program](../implementation/tenant-readiness-program.md), §3.0, §5.0 and §8.

Read this before you design any new multi-session program.

## The lessons

### 1. When the work depends on itself, one executor beats many

- **Day one:** eight sessions worked in parallel. They produced 179 Codex messages, 71 "changes required" replies and 44 pull requests, and the live system did not move at all.
- **Day two:** one session did the work in order. It completed six live steps in about four hours, and most were cleared by the auditor on the first round.

Parallel sessions pay off only for lanes that are really independent. The DevHub refactor lane was one: it had its own worktree, a snapshot database and no auditor traffic.

### 2. Keep a minimal path, and measure how far the live system moved

Put the shortest path to the next real outcome at the top of the plan. Count progress in live steps completed, not in pull requests merged. Never put an optional proof in front of a step that doesn't need it.

### 3. Review in proportion, and cap the rounds

The operator's standing instruction to the auditor was:
- block only for wrong data, irreversible loss, or a security risk beyond the accepted residuals;
- treat everything else as a follow-up;
- stop after two review rounds, then escalate.

It worked. Most steps were cleared on the first round, and the one step that needed a third round was escalated cleanly.

### 4. Give the operator one place to act

The Operator Desk page holds every pending operator action as a card: the exact text to copy, why it is needed, and a recommendation. The same text goes into chat for when the operator is remote. Only the coordinating session posts cards.

Label every grant with the step it belongs to. Once, a grant for one migration was pasted into the thread for another.

### 5. Watch for silent stalls

Things stopped without saying so:
- the auditor halted silently when it ran under a restricted profile;
- background waiters died when the machine restarted;
- the Mac restarted three times.

Use the stall watcher, which reports pending grants and unanswered messages, and the shallow-repository watchdog. After any restart, bring the servers back up and run the health checks.

### 6. Keep the grant chain

Each live step went through the same chain:
1. rehearsal on a throwaway copy;
2. the auditor's "execution cleared";
3. the operator's grant, sent directly to the auditor;
4. the auditor's saved copy of that grant;
5. the executor compares that copy to the expected text, byte for byte;
6. the step runs once;
7. a closure record;
8. the coordinator checks the live result read-only.

It held every time. Word grants so that nothing in them can be changed by a chat window: avoid underscores, email addresses and links.

### 7. Check results independently, read-only

After every live step, the coordinator re-checked the live state with read-only queries. Nothing was wrong this time. Earlier, the same habit, together with rehearsals, caught a stale database identifier, a fix that never loaded, and a worker that ran without its guard.

### 8. Hygiene traps cost hours

- **Shallow fetches** in shared repositories cut history for every session.
- **Test specs that default to the live database.**
- **`psql` exiting 0** after a `\quit` with an error code.
- **Rehearsal containers and volumes left behind.** A reused rehearsal volume kept an old password. Five later rehearsals then failed in a way that looked like a random flake.
- **Stale DevHub sessions** after restarts.
- **Relay caps on messages:** at most ten without operator input.
- **Scheduled tasks stuck** on permission prompts.

### 9. One owner makes scope decisions

The coordinator decides placement, order and what gets parked. Other sessions propose. When two sessions wrote to the same task's details, a decision was lost. Always read the current text and merge into it before writing.

### 10. Rehearse all the way to the final step

The last full rehearsal on a throwaway copy ran every step, including the final metric evaluation. It found that the evaluation engine refused to count values that were dates, so the final step would have failed on the live system after every other step had already landed. Fixing it took one small change and one extra server move. Rehearse the final outcome, not just the steps that lead to it, before you start the live steps.

## What carries forward

The open items are DevHub tasks under PLN-31c4a1, tagged `carry-over`. §5.0 of the [Tenant Readiness Program](../implementation/tenant-readiness-program.md) lists them. The largest are:
- the evidence proof step (MLS-24);
- the portal display (MLS-25);
- the DSO metric on Kaveri, which is the program's real destination.
