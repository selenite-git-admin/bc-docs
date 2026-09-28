---
uid: DEC-f4a6b9
title: "Engineering rule catalogue and responsibility registry (one job, one owner)"
description: "Code rules as a governed catalogue climbing mirror → advisory → ratchet → gate; a responsibility registry so each job, table and external system has exactly one owner."
status: decided
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

### What the security rule promises (operator ruling 2026-09-27, option A)

- DevHub never shows values from secret stores (.env files, AWS credentials, Secrets Manager), and reads none, with one exception (amended 2026-09-27, operator): the once-a-day vendor-billing job, running as its own process, reads named usage-read keys into memory for vendor billing calls and saves only numbers. The keys are the operator's exact boundary: ANTHROPIC_BILLING_KEY (a non-workspace service-account key whose account has the Billing role) and OPENAI_USAGE_READ_KEY (a read-only admin key), from the billing secret through its billing-reader role, plus DEEPSEEK_API_KEY. Automated Anthropic billing is parked: Claude Console service accounts can currently be created only as Developer or Admin, so the specified key cannot be minted. Until the operator directly resolves that, no Anthropic key is stored for billing and Anthropic spend is read in the console. Any different credential needs a new direct operator decision before it enters this design. It never uses an org-admin key; those stay in the vendor consoles (credential program TSK-088714). Failures are saved as fixed categories only. The web server never holds a key. Separately (2026-09-28, operator; ADR DEC-6be41d): the credential probe and the credential-rotation helper are separate local processes outside DevHub that may hold a value only transiently; DevHub itself gains no secret access and receives only fixed metadata from them. Credentials are never in DevHub.
- It never shows a value it has flagged as a secret. Findings are kind and line only.
- Code names and file paths are shown as they appear in git. Whoever can open DevHub, which is localhost only, can already read these repos.
- Redacting key-shaped names is a best-effort safety net, not a guarantee. Pattern matching cannot recognise every credential format; hex-only strings are kept so commit SHAs stay readable.
- A secret written into code is the security rule's job to flag.

This scope follows Codex gen-a0deba-02, which showed that pattern redaction cannot be complete.

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

Where a rule overlaps @barecount/eslint-config (length, smell), the written threshold in the source ADR (DEC-ee6018) is the authority. When such a rule reaches ratchet, one of the two stops checking it: either the ESLint rule is aligned to the threshold and the scanner reports ESLint's result, or the ESLint rule is dropped. Until then the scanner's check is a mirror and ESLint keeps its current settings.

## Consequences

- DevHub Codebase > Hotspots is the mirror for section 1, and Codebase > Responsibilities (renamed from Ownership, operator 2026-09-27) is the mirror for section 2.
- The 17 tables with more than one writer in bc-core are adjudicated one at a time with the D619 method before the "no new second owner" ratchet starts. The ratchet's first baseline is whatever remains after that.
- Which rules move to ratchet first is an operator decision, backed by each rule's sampled precision. The evaluation path (pipeline code) goes first.
- Scan history, the shared scanner package and the per-repo baselines are separate follow-up units; this ADR does not change any repo's CI.
