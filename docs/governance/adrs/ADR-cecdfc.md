---
uid: DEC-cecdfc
title: "Every act has a door: nothing is done without a screen or a command, and one act has one implementation"
description: "An act a person makes on the platform is Built only when a screen or a command reaches it; request-only is Partly built; one act has one implementation behind its doors."
status: decided
date: 2026-11-21T02:26:21.842Z
project: platform
domain: governance
subdomain: governance/product-discipline
focus: every act has a screen or a command; one implementation per act
---

# Every act has a door: nothing is done without a screen or a command, and one act has one implementation

## Context

The code-first service audit of 2026-11-21 read 386 service and controller classes of bc-core and found live requests that no screen and no command calls (by-hand observation and admission routes, older catalog routes), with checks nobody exercises. A door is where confirmation, a dry run, the role and the evidence reference are asked for the same way every time; a raw request skips them. An act with neither door is then either missing its door or dead code, which makes the audit a yes or no question. It also fits the confirmed intent of one metric's value reached by commands and proven against the source.

## Decision

Decided by the owner on 2026-11-21 during the workflow review, after the code-first service audit found live acts that only a raw request reaches. His words: "NOTHING should be allowed without UI or CLI. Hygiene/discipline -- that will save costly errors." and "Agreed on both, record the decision and update states."

1. An act a person makes on the platform (a feature of type functional on the Workflows page) is finished only when a screen or a command reaches it. An act that works by request only is Partly built, with the note "works by request only; no screen or command". This replaces the earlier rule of this review that a feature is Built when its request or command works even with no screen.

2. The rule applies to acts. A validation (a rule such as "refuse an ungoverned reader") and a quality ride on the act they belong to and need no door of their own. A feature the platform carries out by itself, on a schedule or an event, names its trigger instead of a door.

3. A customer's own system calling the platform (webhooks, machine credentials) is a legitimate door when it is declared as one on the feature.

4. The rule is discipline, not protection. A screen and a command both call the same request, and the request stays callable by anyone holding a token. "No screen calls it" is never a reason to call a request safe; the checks on the server must hold whatever doors exist.

5. Nothing new is accepted as done without its screen or command. An existing act with no door gets a command, gets a screen, or is retired; the list of such acts is the work list of the command-line program.

6. One act has one implementation. The owner raised it as a question in the same conversation ("any FEATURE should not be implemented in more than ONE way/door??") and confirmed this wording ("Yes, confirmed"): a screen and a command may both exist for an act, and both call the same single implementation, holding no logic of their own; two separate code paths that perform the same act are not allowed. Where two exist today (for example the older metric catalog and definition routes beside the governed catalog), one is retired.

No enforcement mechanism is built by this decision. The Workflows page shows which acts lack a door.
