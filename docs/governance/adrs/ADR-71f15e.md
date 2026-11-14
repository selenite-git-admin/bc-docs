---
uid: DEC-71f15e
title: "Platform Refactor Program: park the Demoed drive and the controller fleet; refactor the platform one function at a time against a functional map"
description: "The operator's decision of 2026-11-13, approved 2026-11-14: park the Demoed drive and the controller fleet; refactor the whole platform one function at a time (define, audit, modify, prove, lock); the program is bc-docs docs/development/platform-refactor-program.md."
status: proposed
date: 2026-11-14T01:33:34.942Z
project: bc-docs
domain: development
subdomain: development/program
focus: governance
---

# Platform Refactor Program: park the Demoed drive and the controller fleet; refactor the platform one function at a time against a functional map

## Context

A retrospective and review of 2026-11-13 found that the platform's central mechanisms exist once and are driven by declarations, while around them there are many ways to perform each act, small breaks on the obvious route, documents that describe a system that has since changed, and hand-offs that were never designed. Sessions therefore invented a path at each junction. The definition of a finished metric had been replaced about a dozen times. Twelve earlier cleanups failed because each added a text and retired none and none had an executable check. The program was reviewed by the auditor on threads gen-69def7, gen-a649ce and gen-a708d2 and accepted with boundary for the operator's decision.

## Decision

The Demoed drive and the controller-fleet method are parked. The platform is refactored one function at a time against a functional map of the whole platform. Each function passes five steps (define, audit, modify, prove, lock) and ends in commands that are the only way to perform its acts, one chapter of a single developer guide, and a lock. The hand-offs between functions are designed first as twelve stitch contracts. DevHub and bc-docs are made trustworthy first. No metric, contract or business concept is authored outside the program until its function reaches its Modify step. The full statement, the order of work in twelve phases, the definition of done for the program and the register of rulings are in bc-docs docs/development/platform-refactor-program.md and its annexes. Rulings decided by the operator: F1 (metrics are not positioned as the product), T1 (a tenant subscribes to a package; a package holds many metrics; a metric may be in more than one package), T2 (subscription is designed in full and only what the thread needs is built), T3 (a value-affecting change reaches a tenant only when the tenant's admin or a designated role or user accepts it), G2 (the DevHub backlog is swept), G5 (DevHub stays on its present database for now), G3 (unused DevHub tools are stopped, then removed), G30 (the rules for sessions live in a bc-docs chapter), G34 (the Chief owns every function until phase 12).
