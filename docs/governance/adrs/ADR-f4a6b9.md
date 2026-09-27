---
uid: DEC-f4a6b9
title: "Engineering rule catalogue and responsibility registry (one job, one owner)"
description: "Code rules as a governed catalogue climbing mirror → advisory → ratchet → gate; a responsibility registry so each job, table and external system has exactly one owner."
status: proposed
date: 2026-09-27T10:06:11.273Z
project: barecount-devhub
domain: governance
subdomain: governance/engineering-standards
focus: code-integrity
---

# Engineering rule catalogue and responsibility registry (one job, one owner)

## Context

The operator's goal (2026-09-27) is for BareCount to be a calculator-grade platform. The DevHub scan (barecount-devhub #76) showed the gap.

**Code quality in bc-core:**
- 523 of 2,211 files pass every checked rule.
- In pipeline code, src/boundary: 79 of 90 source files fail the docs rule, and 38 fail the calculator rule. Examples: Number(value) inside the canonical and action evaluation engines; day counts from rounded milliseconds.
- The written standard (DEC-ee6018: 60/40 lines) is not what eslint.config.mjs enforces (100 lines as a warning; 40 only in src/boundary, where long functions pass on eslint-disable).

**One job, one owner:** 17 of the 201 tables that bc-core source writes are written from more than one module. Examples:
- progression.metric_run: progression has a repository, and boundary's governed-metric-persistence adapter also updates the table directly.
- runtime.admission_run: a raw-SQL insert in reader-runtime, and a registry repository.
- ai_telemetry run and call ledgers: parallel ABC and BCF writers.

Duplication here is mostly generational, a v2 built beside v1, which is why the registry has a retiring state with successor and sunset. 80 platform tables carry DB immutability/guard triggers. Trigger names do not tell column-scoped guards (business_concept pointers) from whole-row ones, so immutability findings are review candidates, not violations.

**Why the ladder.** DEC-b7d74b's lesson is that audit machinery must earn its keep, so nothing starts as a gate: every rule proves its precision at mirror first.

**Why one implementation.** DEC-5b760c places enforcement in per-repo CI; one implementation per rule avoids two diverging versions of the same check.

**Operator rulings recorded 2026-09-27:**
- dev-only connection strings: exempt, but watched;
- docs: 100% in pipeline code, 50% elsewhere;
- the sql-safe marker.

**Relates to:** DEC-027ef6/D619, DEC-ee6018, DEC-1918d0/D162 (rule 4: one source of truth per value), DEC-5b760c, DEC-b7d74b, and the Foundation invariants (I, III, VI).

## 1. Engineering rule catalogue

The code rules BareCount holds itself to form one governed catalogue: this ADR plus the rules table the DevHub code scan implements.

**What each rule carries:**
- the principle behind it;
- the ADR it comes from;
- its scope (all code, source only, or pipeline/evaluation code only);
- its threshold;
- its enforcement stage.

**The enforcement ladder.** Every rule climbs mirror → advisory → ratchet → gate. It never starts as a gate.
- **mirror:** shown on DevHub Codebase > Hotspots.
- **advisory:** listed, never failing.
- **ratchet:** CI fails on new violations only, against a committed, shrink-only baseline.
- **gate:** CI fails on any violation.

A rule moves up one stage on operator approval, backed by evidence: its precision is sampled by hand and its failing count is known.

**The rules at adoption, all at mirror unless noted:**

| Rule | What it checks |
|---|---|
| security | No secrets in code, eval-like calls, shell or SQL injection patterns, XSS sinks, TLS off or auth bypass. Findings are kind and line only, never a value. |
| calculator (pipeline code only) | Deterministic: no clock reads, no Math.random. Exact: no parseFloat, Number(), toFixed or Math.round. Fail-loud: no catch that swallows the error and returns a default. |
| length | File ≤ 1,000 lines; functions ≤ 60 lines, or 40 in pipeline code (DEC-ee6018), counted like ESLint. |
| lint | No eslint-disable. |
| tests | A same-name spec or test file exists. |
| docs | A header comment, and the public API documented: 100% in pipeline code, 50% elsewhere. |
| smell | No explicit any, TODO/FIXME, console.log or nested ternary. |
| dup-in-file, dup-across | No 8-line block repeated within a file, or shared with another file. |
| dead | No unreferenced file, unused export or unreachable statement. |
| performance | No await inside a loop, no sync I/O; Python: no remote/DB call in a loop, no 3-deep loops. |

**Advisory at adoption:**
- lookups inside loops;
- weak hashes;
- localhost-only connection strings. These fail as dev-password-reused if the same password appears with a non-local host.
- raw SQL carrying `sql-safe: <reason of 20+ characters>`.

**Candidate rules** (added to the scan at mirror as they are built):
- immutability: no UPDATE/DELETE on DB-protected tables outside declared writers;
- no import cycles, with layers depending downward only;
- no god services (more than about 8 injected dependencies);
- branching complexity ≤ about 10;
- no mocks in tests (D082).

## 2. Responsibility registry: one job, one owner

This extends D619 (DEC-027ef6) with the question "does exactly one place own each job?".

**Declare.** A machine-readable registry in each code repo (bc-core first: `src/__architecture__/responsibilities.json`) lists each capability with:
- its **owner** module;
- what it **owns**: the tables it alone writes, the external systems it alone calls, its route families;
- its **state**: `active`, or `retiring` with a named successor and a sunset date. Old-plus-new generations are allowed temporarily, never forgotten.

**Detect.** Objective signals:
1. single writer per table, resolved to schema.table through imports, plus raw SQL;
2. single client per external system;
3. single controller per route family.

A heuristic signal, look-alike services, produces candidates only.

**Adjudicate** each candidate with the D619 method: true duplicate (merge or delete one), layered (one delegates to the other, fine), or generational (register as retiring).

**Enforce.** A shrink-only "no new second owner" ratchet in CI.

## 3. One implementation per rule

Each rule is implemented once: in the DevHub code scanner. Per DEC-5b760c, enforcement lives in each repo's CI. The scanner is therefore published as a CodeArtifact package that each repo's CI runs against its own baseline, the way @barecount/eslint-config is shared. No rule is implemented twice.
