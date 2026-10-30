---
uid: DEC-025bfc
title: "Demoed terminal-state: the earned metric-axis terminal (read-time projection over a preserved proof act)"
description: "Demoed terminal-state: the earned metric-axis terminal (read-time projection over a preserved proof act)"
status: decided
date: 2026-10-30T08:18:33.282Z
project: platform
domain: platform
subdomain: metric-lifecycle
focus: terminal-state
---

# Demoed terminal-state: the earned metric-axis terminal (read-time projection over a preserved proof act)

## Authority

Ratified by recorded operator grant `2026-10-30T08-16-46-443Z-259c0901` (text_sha256 `259c090176e6df7009bc865e4afa767f336f9a35782507122ab24a1fc9202cd2`, TOTP, bc-exchange request 362, thread gen-4fab1b). Design accepted by Codex gen-4fab1b-02 (ACCEPTED WITH BOUNDARY, two rounds). Earned by the AR Balance (`a11a88f4` v1) calculation-mechanism proof on the demo plane (dry, engine output == independent LC5 oracle to the cent across 4 legal-entity × period cells, double-verified; bc-core main `f9cfcadf`).

## Relationship to prior authority (boundary 1)

This DEC **amends DEC-89db41**. DEC-89db41 deferred the terminal-state decision with the literal prerequisite "once DSO lands on the demo plane and proves it." This DEC supersedes that specific trigger: the terminal-state is earned by a **PRIMARY** metric's calculation-mechanism proof on the demo plane (AR Balance), which serves DEC-89db41's rationale (a metric with a known in-tenant number reproduced on the demo plane) exactly as DSO would have. DEC-89db41's plane + isolation decisions are unchanged. This DEC **supersedes** the draft terminal ADR (`DRAFT-ADR-demoed-platform-terminal-2026-10-26`). Deciding this declaration does **not** confer `Demoed` on AR Balance or any metric.

## Decision

**T1 — `Demoed` is a platform terminal state** on the metric axis: a metric is `Demoed` when proven end-to-end against the in-platform, synthetic, frozen/versioned demo world, with no per-metric tenant crossing.

**T2 — `Demoed` is a read-time projection over a preserved, version-pinned PROOF ACT** (Foundation invariants I/IV/V/VI). A proof is established ONLY by an **explicit evaluation act** that **emits immutable evidence** (§VI: emitted with its act, never inferred by replay), binding: metric-contract version · demo-world version · the independent oracle value and its authorship/frozen-byte provenance · engine/build identity · cell scope · result (exact decimal). The terminal **projection reads that preserved evidence at read time and validates currency** — all pins present and current, proof present and not stale — returning `Demoed` / `not-Demoed` / `unknown`. It **never recomputes at read time, never treats a rerun as historical evidence, never creates proof on read** (§V non-replayable, §I meaning-once). `Demoed` is therefore **not a stored boolean** (how `active` lied) and **not a read-time recompute**; it is live re-validation of an emitted, immutable proof's currency. Any missing/stale pin or absent proof yields `not-Demoed`/`unknown`.

**T3 — Carry-forward is fail-closed** (boundary 2). A proof pinned to contract vN **cannot** be displayed as proof for vN+1. Carry-forward vN → vN+1 requires a **governed, preserved equivalence/bridge record** naming both versions and every checked pin, asserting equivalence of ALL value-affecting semantics (formula, gate, grain, temporal rule, source bindings, engine route) and the demo-world/oracle/proof-scope. Until that record exists and is validated, the projection returns `not-Demoed`/`unknown`; otherwise a fresh proof is required for vN+1.

**T4 — Oracle independence (evidenced, not a label).** The independent oracle is frozen-byte, provenance-stamped, authored independently of the metric contract (different family); it is **forbidden** to derive it from the evaluator output or the same contract-generation path.

**T5 — Scope.** `Demoed` means "calculates correctly against the frozen demo world," never "tenant X's live number." Tenant consumption keeps a thin, non-zero binding (C).

**T6 — Objective.** A predicate over a projected set (every provable seed `Demoed` or honestly dispositioned), never a count; counts are a live dial read (DEC-b049f6).

**T7 — Explicit non-goals of this DEC** (deferred, separately gated): the `seed→directory→catalog→demo` bc-admin dial; DSO and further metrics; the demo-plane writing-eval evidence routing (TSK-f4e038) — a **named dependency** of the post-DEC build (the proof act emits evidence through it), decided separately.

## Foundation fit

Design act (DEC-c48b0f). §I meaning-once; §III immutable/versioned demo world + immutable emitted proof; §IV explicit provenance (oracle bytes + pins); §V reads validate, never recompute; §VI evidence emitted by the act, projection reads it. Repair location **B** (terminal/contract semantics); decide-before-build.

## Consequences

First build (separately gated, AFTER this DEC): (i) the demo-plane proof act emitting immutable version-pinned evidence (depends on TSK-f4e038); (ii) the read-time `Demoed` projection over it, with the positive AR Balance read AND the known-hollow negative acceptance test (a known-hollow item MUST project `not-Demoed`). No terminal-state code lands before this DEC.
