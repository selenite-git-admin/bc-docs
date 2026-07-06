---
uid: DEC-ee6018
title: "Power of Ten — Adapted Coding Rules for BareCount"
description: "Adaptation of Holzmann's NASA/JPL Power of Ten rules for the BareCount Node.js/TypeScript stack"
status: implemented
subdomain: qa-standards
focus: power-of-ten-rules
date: 2026-04-02
project: platform
domain: governance
refs:
  - type: source
    label: "Holzmann, G.J. (2006). The Power of Ten — Rules for Developing Safety Critical Code. NASA/JPL."
  - type: decision
    label: "D162 — Database Rules"
  - type: decision
    label: "D148 — Naming Conventions (ISO 11179)"
migrated_from: legacy v2 archive
---

# Power of Ten — Adapted Coding Rules for BareCount

## Context

BareCount is a financial observation platform where correctness matters. The
execution model (SO -> CO -> Metric Snapshot -> AO) is designed for auditability
and traceability. Code quality in the evaluation pipeline directly affects the
trustworthiness of financial metrics.

Gerard Holzmann's *Power of Ten* (NASA/JPL, 2006) defines 10 rules for
safety-critical C code. The rules sacrifice developer convenience for
verifiability. While BareCount is not aerospace, the same philosophy applies:
**constrain the language to a subset that tooling can verify automatically.**

With ~100K lines across bc-core and bc-admin and a single developer, manual
review is not feasible. These rules are designed to be **machine-enforced** via
ESLint, TypeScript strict mode, and pre-commit hooks.

## Decision

Adopt the following 10 adapted rules across bc-core and bc-admin. Enforce via
tooling. Existing code is grandfathered — violations are fixed opportunistically
as files are touched.

---

### Rule 1: Simple Control Flow

**Original:** No goto, setjmp, longjmp, or recursion.

**BareCount adaptation:**
- No recursion in the evaluation pipeline (`/src/evaluation/`, `/src/readers/`,
  `/src/canonical/`, `/src/metrics/`). Recursion is permitted elsewhere (e.g.,
  tree traversal in UI components) but must have a proven termination condition.
- Maximum nesting depth of **3 levels** (if/for/try). If you need a 4th level,
  extract a function.
- No `goto`-like patterns: no `break` with labels, no `continue` in nested
  loops.

**Enforced by:** `eslint: max-depth: 3`

---

### Rule 2: Bounded Iteration

**Original:** All loops must have a fixed upper bound.

**BareCount adaptation:**
- Prefer `Array.map()`, `.filter()`, `.reduce()`, `for...of` over `while` loops.
- Every `while` loop must have a maximum iteration guard:
  ```js
  let guard = 0;
  while (condition && guard++ < MAX_ITERATIONS) { ... }
  ```
- No infinite loops (`while(true)`) except in explicitly marked long-running
  services (e.g., queue consumers) which must have a shutdown signal.

**Enforced by:** Code review guidance (Claude sessions). Consider a custom
ESLint rule if `while(true)` proliferates.

---

### Rule 3: No Late-Stage Dynamic Allocation

**Original:** No dynamic memory allocation after initialization.

**BareCount adaptation (reinterpreted for GC language):**
- No dynamic `require()` or `import()` in request handlers. All modules loaded
  at startup.
- No runtime `eval()`, `new Function()`, or `vm.runInContext()`.
- Connection pools, caches, and singletons initialized at boot, not on first
  request.
- Drizzle schema objects are static — no runtime schema construction.

**Enforced by:** `eslint: no-eval`, `no-new-func`, `no-restricted-syntax` for
dynamic `require`. Service initialization pattern enforced by code review.

---

### Rule 4: Function Length Limit

**Original:** No function longer than 60 lines (one printed page).

**BareCount adaptation:**
- Maximum **60 lines** per function (excluding blank lines and comments in the
  count where the tool supports it).
- Route handlers count as functions. If a handler exceeds 60 lines, extract
  service/helper functions.
- Database seed scripts are exempt (bulk data setup is inherently long).

**Enforced by:** `eslint: max-lines-per-function: { max: 60, skipBlankLines: true, skipComments: true }`

---

### Rule 5: Assertions at Boundaries

**Original:** Minimum two assertions per function.

**BareCount adaptation (targeted, not blanket):**
- Every **evaluation boundary** function (Admission, Canonical Evaluation,
  Metric Evaluation, Action Evaluation) must validate:
  1. Input object shape/type (the object arriving at the boundary)
  2. Output object completeness (the object leaving the boundary)
- API route handlers must validate request parameters at entry (already handled
  by validation middleware — ensure it's applied).
- Internal helper functions do NOT need assertions — trust internal code per
  project philosophy.

**Enforced by:** Code review guidance (Claude sessions check boundary functions
for input/output validation). Consider Zod schemas at boundaries.

---

### Rule 6: Minimal Scope

**Original:** Declare data objects at the smallest possible scope.

**BareCount adaptation:**
- `const` by default. Use `let` only when reassignment is necessary. Never
  `var`.
- No module-level mutable state (`let` at file top-level). Use closures or
  class instances if state is needed.
- Database connections, config objects, and caches are the only permitted
  module-level state, and they must be initialized once at startup.
- Avoid "god objects" -- don't pass a large context/state bag through multiple
  functions. Pass only what each function needs.

**Enforced by:** `eslint: prefer-const`, `no-var`. Module-level `let` detected
by `no-restricted-syntax`.

---

### Rule 7: Check All Returns

**Original:** Check the return value of all non-void functions. Validate all
parameters.

**BareCount adaptation:**
- No floating promises -- every async call must be `await`ed or explicitly
  handled with `.catch()`.
- No ignored `catch` blocks -- if you catch, log or handle. Empty `catch {}`
  is forbidden.
- API client responses must check HTTP status before using the body.
- Database query results must be checked for `null`/`undefined` before property
  access (TypeScript strict null checks enforce this).

**Enforced by:** `@typescript-eslint/no-floating-promises`,
`no-empty` (for catch blocks), `tsconfig: strictNullChecks: true`.

---

### Rule 8: Limit Metaprogramming

**Original:** Limit preprocessor use to file inclusions and simple macros.

**BareCount adaptation (reinterpreted as "limit magic"):**
- No `Proxy`, `Reflect`, `Object.defineProperty` for business logic. Permitted
  only in framework/infrastructure code with clear documentation.
- No decorator-heavy patterns (NestJS decorators are acceptable as framework
  convention, but custom decorators must be rare and documented).
- No conditional compilation via environment variables that changes code paths
  in production vs development (feature flags via database/config are fine).
- Build-time transforms (Vite plugins, Babel) kept to minimum.

**Enforced by:** `eslint: no-restricted-globals` for `Proxy`/`Reflect` in
`src/` (excluding infrastructure). Code review guidance.

---

### Rule 9: Limit Indirection

**Original:** No more than one level of pointer dereferencing, no function
pointers.

**BareCount adaptation:**
- Maximum **3 levels** of object property access: `a.b.c` is fine,
  `a.b.c.d.e` should be destructured or the intermediate object extracted.
- No deeply nested optional chaining: `a?.b?.c?.d?.e` signals a data model
  problem, not a code solution.
- Callback chains limited to 1 level -- use `async/await`, not nested
  `.then().then()`.
- Event emitter chains kept short -- an event handler should not emit another
  event that triggers another handler (max 1 level of event indirection).

**Enforced by:** Code review guidance. Consider `eslint: max-nested-callbacks: 2`.

---

### Rule 10: Compile Clean with Strict Analysis

**Original:** Compile with all warnings on, use static analysis daily.

**BareCount adaptation:**
- TypeScript `strict: true` (enables all strict checks).
- ESLint with `@typescript-eslint/recommended-type-checked` ruleset.
- Zero tolerance for `@ts-ignore` -- use `@ts-expect-error` with an explanation
  comment if genuinely needed, and these are tracked/counted.
- No `any` type in new code. Existing `any` types tracked and reduced over
  time.
- Pre-commit hook runs ESLint on staged files -- violations block the commit.
- CI runs the full lint + type-check -- PR cannot merge with violations.

**Enforced by:** `tsconfig.json` strict mode, ESLint CI check, pre-commit
hook (lint-staged + husky).

---

## Enforcement Strategy

### Tier 1: Automated (blocks commit/CI)
Rules 1, 4, 6, 7, 10 -- fully enforceable via ESLint + TypeScript config.

### Tier 2: Semi-automated (flagged in CI, not blocking initially)
Rules 3, 8, 9 -- custom ESLint rules or restricted syntax patterns.

### Tier 3: Review-time (Claude session guidance)
Rules 2, 5 -- require semantic understanding, enforced during development
sessions.

### Grandfathering Existing Code

- ESLint config applied to all files, but existing violations are
  **baseline-suppressed** (tracked, not blocking).
- When a file is modified, all violations in that file must be fixed (the
  "boy scout rule" -- leave it cleaner than you found it).
- A coverage score tracks % of files that pass all rules. Target: monotonically
  increasing.

## Consequences

**Benefits:**
- Machine-enforced consistency across 100K+ lines with zero manual review effort
- Catches common defect patterns (floating promises, unchecked nulls, deep
  nesting) before they reach production
- New code is automatically held to the standard
- Aligns with existing BareCount philosophy (fixed progression, forbidden
  vocabulary, DB rules)

**Costs:**
- Initial setup effort for ESLint config + pre-commit hooks (~2-4 hours)
- Some existing code will trigger warnings until touched and fixed
- Occasionally a rule will feel restrictive for a legitimate pattern -- use
  targeted `eslint-disable-next-line` with a comment explaining why

**Risks:**
- Over-suppression: if too many `eslint-disable` comments accumulate, the rules
  lose value. Track and review suppress count periodically.
- False sense of security: automated rules catch syntax/structure issues, not
  logic errors. Boundary assertions (Rule 5) remain the primary defense against
  semantic bugs.
