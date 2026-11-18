---
uid: DEC-9ea3f4
title: "A Codex worker lane beside the auditor: runs, read-only studies and pre-reads only, on the same instance, with its own instructions and thread family"
description: "Proposed: spare Codex capacity is used through a worker lane (family wrk-) on the one existing Codex instance under bcauditor. It does only three kinds of work that land nothing: heavy test runs, read-only studies, and pre-reads of drafts. Its instructions are separate from the auditor's, which are not changed; it holds no authority, no App, no merge, no write to any repository but its reply; reviews always go first. Building code is out of scope."
status: proposed
date: 2026-11-18T02:11:49.037Z
project: barecount-devhub
domain: governance
subdomain: governance/audit-exchange
focus: worker-lane
---

# A Codex worker lane beside the auditor: runs, read-only studies and pre-reads only, on the same instance, with its own instructions and thread family

## Context

Operator direction, 2026-11-18 (chat, session SES-7decb4). Claude's Fable allowance was exhausted on 17 November (two workers died mid-task; reset 23 November) while the auditor answers in minutes and has spare capacity. The operator ruled out two things: (1) weakening the auditor's prompt or standing instructions by giving it builder work, and (2) a second Codex instance or sign-in, which he judges against the provider's fair use policy. He approved drafting a lane limited to the three kinds of work that produce nothing the auditor must later judge. DEC-44456d point 4 puts any change to the auditor's standing instructions, protocol or service under two gates (an auditor reviewer and the operator's terms gate) and says the builder proposes and never merges auditor code; this decision is therefore a proposal to the auditor and the operator, and nothing takes effect until both gates pass. Independence is the cost that is priced: with one instance, work the worker lane BUILT would be reviewed by the same model and login, so building is excluded; runs, studies and pre-reads yield evidence and notes, never a landing unit.

## Decision

PROPOSED. Nothing here is in force until the auditor's technical gate and the operator's terms gate of DEC-44456d point 4 pass, and the service change is merged by the auditor App.

1. ONE INSTANCE, TWO LANES. The existing Codex under the macOS account bcauditor (DEC-44456d) gains a second lane, the worker lane. No second account, no second sign-in, no second subscription.

2. WHAT THE WORKER LANE DOES. Exactly three kinds of task, each named in the task's Kind header:
   - run: run a named test file or mutation run at an exact commit of a named repository and report the result (counts, failures, durations, the commands, the commit), for example the 65 minute Docker file of the reference run or a missing mutation run;
   - study: a read-only reading of named repositories at exact commits, or of GitHub state, that ends in a written report (for example triage of parked pull requests, of a follow-ups task, of the secrets check's wrong lines);
   - preread: a reading of a draft the Chief will later put to the operator or the auditor (a desk request, an execution package, a runbook step), returning what is missing, unclear or wrong.

3. WHAT IT NEVER DOES. It writes no code for landing, opens no pull request, pushes no branch, and edits no file of any repository. It never approves, reviews or merges through the auditor App, and the App's tools are not given to its runs. It never writes a Disposition, a Verdict line or an execution clearance, and nothing it writes is authority, evidence of an independent check, or a substitute for the auditor's review. It makes no database write, no cloud change, no credential read or write, no host install, no service stop or restart. A task that asks for any of these is answered REFUSED with the reason.

4. SEPARATE INSTRUCTIONS; THE AUDITOR'S ARE NOT TOUCHED. The worker lane has its own instruction file and its own run prompt, versioned in bc-external-audit beside the auditor's and reviewed under the same two gates. The auditor's AGENTS.md, its barecount-auditor-session skill and its run prompts are not edited by this decision. A worker run must not load the auditor's standing instructions and an auditor run must not load the worker's: how the service guarantees that on one login (a separate Codex home for worker runs, or another mechanism) is the auditor's to state and is the first open question below. If it cannot be guaranteed, this decision is not implemented.

5. SEPARATE THREAD FAMILY. Worker tasks travel as committed files in the same mailbox under their own family, wrk- (thread wrk-<6 hex>, files TASK-Claude-wrk-<id>-<NN>-... and REPORT-Codex-wrk-<id>-<NN>-...), never under gen-. The gen- protocol, its validator and its publisher gates (DEC-081931) are unchanged. A worker report is hash-bound to its task as a gen- reply is to its message. The sender must hold an open DevHub session; one open task per thread; a thread ends with a close task.

6. REVIEWS GO FIRST. A worker run starts only when no gen- message is waiting and a review slot is free; a waiting review is never delayed for a worker task. The service caps worker runs (proposed: one at a time) and records each run (time, token use, outcome) with the auditor's run records, marked as worker runs, so the operator can see what the lane costs.

7. NO INDEPENDENCE IS CLAIMED FOR WORKER OUTPUT. A run result or a study from the worker lane is the builder side's working material. When a landing message to the auditor relies on one, the message says so in plain words (the thread and number), and the auditor judges the landing as it would any other, free to re-run or to ignore it. A preread never replaces the review of the real thing.

8. THE SAME ACCESS, NARROWED. Worker runs have the read access the auditor has (repositories by exact commit, GitHub read) and write only inside their own run folder. They are not given the App token, the grants folder as authority, or any database or cloud credential.

OPEN QUESTIONS (for the auditor, before any build):
   a. Can the service keep the two instruction sets fully apart on one login, and how?
   b. Can a run under bcauditor execute a Docker-bound test file at all (Docker runs under the operator's account on this Mac), and if not, which runs are possible?
   c. Does worker use draw from the same weekly allowance as reviews, and what cap protects the reviews?
   d. Is one session per wrk- thread the right continuity, as for gen-?

OUT OF SCOPE, AND NOT DECIDED HERE: any building of code by Codex; any use of the auditor's review in place of the Chief's independent worker check; any change to who merges.
