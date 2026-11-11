---
id: ADR-ERR-014
title: "DEC-45200d: §6 fingerprint element is additive (not a basis version bump); §1 grammar omits the root-only admission the engine enforces and attributes to the ADR"
status: adopted
authority: authoritative
affected: "docs/governance/adrs/ADR-45200d.md (DEC-45200d, D690; bc-docs main `1290104`) — §6 (Chain status and fingerprint), the clause \"under a basis version bump\"; and §1 (Grammar), the absent root-only admission rule"
resolution: "correction recorded here; DEC-45200d's decision is unchanged. (a) The event-CC fingerprint element is ADDITIVE — carried only by an aggregate_as_of MCV — so no stored non-schedule verdict stales on serve; the consequence (a re-cut event CC stales the verdict) holds for aggregate_as_of MCVs only. (b) aggregate_as_of is admitted only as the formula root; a node over an as-of node is refused. Realized by bc-core #1047 (`f7026d8f`) + bc-db #158."
opened: 2026-11-11
---

# ADR-ERR-014 — DEC-45200d §6 fingerprint mechanism and §1 root-only admission

Architect-lane correction surfaced by the Fork-A engine build (bc-core PR #1047 head
`f7026d8f`, bc-db PR #158). Both items were verified by direct read of the served engine
code, not by review consensus. The DECISION of DEC-45200d is unchanged; two prose facts are
corrected so the Codex-approved ADR matches the decided-and-built behavior before the engine
PRs go to Codex on the platform lane.

## Contradiction summary

**(a) §6 — fingerprint "basis version bump".** DEC-45200d §6 states:

> "The dependency fingerprint basis (and its DB-trigger mirror) includes the event CC
> version, **under a basis version bump**, so a re-cut event CC stales the verdict."

A *basis version bump* bumps a shared basis element (the check-set / fingerprint version)
that every MCV's fingerprint is hashed over, which would re-key and stale **every** stored
verdict on the serve that ships the schedule capability. That is not what was decided or
built: the event-CC element is **additive**.

**(b) §1 — root-only admission.** DEC-45200d §1 (Grammar) defines `aggregate_as_of` as an
MC formula node (operand `variable_ref`) but never states *where in the formula tree* the
node may appear. The engine admits it **at the formula root only** and refuses a nested one,
citing this ADR by uid as the authority — so the code attributes a rule to DEC-45200d that
the ADR text does not contain.

## Implementation behavior (bc-core `f7026d8f`)

**(a) Additive fingerprint element** — `src/registry/mcf/chain-status-fingerprint.ts`:

- The fingerprint tuple tag is the fixed literal `'mcv-chain-status-dependency-fingerprint-v1'`
  (line ~79); it does **not** change on the serve that adds the schedule capability.
- The `schedule_event_cc` element is pushed onto the tuple **only when**
  `mcv.scheduleEventEntityId !== undefined` (lines ~87–91). `scheduleEventEntityId` is
  `undefined` for every non-`aggregate_as_of` MCV (interface doc, lines ~38–43: *"Undefined
  for every other MCV (their fingerprints stay byte-identical)"*), so every non-schedule
  MCV's stored fingerprint is byte-identical before and after serve — **no stored verdict
  goes stale on the capability serve-move.**
- The consequence DEC-45200d §6 asserts — *a re-cut event CC stales the verdict* — is
  **preserved, scoped to `aggregate_as_of` MCVs**: for those, the event entity's CC versions
  are a fingerprint input (via `grainCcVersions.get(e)`), so a re-cut/withdrawn event CC
  moves the fingerprint and forces `stale`.
- The element mirrors the already-ratified **additive** bridge-head precedent
  (DEC-eb612b §6.3, same file, lines ~54–59), which is additive for exactly this
  "no stored row goes stale on serve" reason.
- The separate constant `CHAIN_STATUS_CHECK_SET_VERSION` (= `'mcv-chain-status-checks-v2'`,
  line ~25) is the check-set-shape version; it bumps only when the chain-status CHECK SET
  changes shape (a different concern) and was **not** bumped to add the event-CC element.
- **DB-trigger mirror:** no DDL is required — the bc-db 0062 ccv trigger already covers the
  event entity, so the mirror tracks the additive element without a schema change or a
  mirror-version bump.

**(b) Root-only admission** — `src/registry/mcf/formula-canonicalization.service.ts`:

- `assertAsOfAtRootOnly(normalized, true)` is run at canonicalization (line ~129).
- A non-root `aggregate_as_of` throws `InvalidAstError("aggregate_as_of is admitted only as
  the formula root (one declared schedule per metric, DEC-45200d)")` (lines ~624–636).
- `src/common/formula/as-of-schedule-declaration.ts` (lines ~133–134): *"v1 admits the node
  at the ROOT only (one schedule per metric — the runtime binds one ScheduleDescriptor per
  spec)."* Rationale: a nested `aggregate_as_of` has no evaluation path.
- Covered by `src/registry/mcf/as-of-schedule-grammar.spec.ts` ("a NESTED aggregate_as_of is
  refused (v1: one schedule per metric, at the root)").

## Resolution (what DEC-45200d should be read to say)

- **§6**, in place of "under a basis version bump": the event-CC version is an **additive**
  fingerprint element carried **only by an `aggregate_as_of` MCV** (no basis version bump);
  every other MCV's fingerprint is byte-identical, so no stored non-schedule verdict stales
  on the capability serve. The stated consequence — *a re-cut event CC stales the verdict* —
  holds **for `aggregate_as_of` MCVs**. The DB-trigger mirror tracks the additive element
  with no DDL (bc-db 0062 ccv trigger already covers the event entity).
- **§1**, added: `aggregate_as_of` is admitted **only as the formula root** — one declared
  schedule (one `ScheduleDescriptor`) per metric; a node composed *over* an as-of node
  (e.g. a ratio or aging node) is refused at canonicalization. A ratio/aging metric built on
  an as-of value is a separate design act, not within DEC-45200d's grammar.
- **No design change.** The eight parts of DEC-45200d (grammar, assembly, guards, sourcing,
  evidence, chain status + fingerprint, numeric domain, proof vectors), the hashed schedule
  declaration, the declared/hash-bound `anchor_sign`, the dual proof inputs and the exact
  kernel are all unchanged. Only the §6 mechanism wording and the §1 omission are corrected.

## Resolution state

`adopted` — the built behavior (additive fingerprint element; root-only admission) is the
correct engineering and is the architect-confirmed decided behavior; the correction is
recorded here and the decision stands. The realizing engine PRs — bc-core #1047 (`f7026d8f`)
and bc-db #158 — are on the platform (Codex) lane as drafts at authoring time; they are the
code of record for this correction once they land.

## References

- `docs/governance/adrs/ADR-45200d.md` (DEC-45200d, D690; bc-docs main `1290104`) — §1, §6
- DEC-c741a3 (parent: P-aware signed as-of aggregate), DEC-eb612b §6.3 (additive bridge-head
  fingerprint precedent)
- bc-core PR #1047 (`claude/fork-a-asof-engine`, head `f7026d8f`):
  `src/registry/mcf/chain-status-fingerprint.ts`,
  `src/registry/mcf/formula-canonicalization.service.ts`,
  `src/common/formula/as-of-schedule-declaration.ts`,
  `src/registry/mcf/as-of-schedule-grammar.spec.ts`
- bc-db PR #158 (migration 0067) — the forward DB act under the operator's DB-yes
- Errata schema: `docs/governance/errata/README.md` (ADR-ERR family — correct a decided ADR's
  clause without rewriting the ADR)
- NC-626ec7 (open Foundation NC; DEC-45200d's Boundary — not closed by this ADR or this
  erratum)
