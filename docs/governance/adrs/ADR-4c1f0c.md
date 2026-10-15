---
uid: DEC-4c1f0c
title: "Reviewed engine-bytes authority is single-sided in bc-core — RUNTIME_SOURCE_PINS re-hashed at CI plus the auditor App head-pinned attestation; the external C4 dependency-record half is retired"
description: "Reviewed engine-bytes authority is single-sided in bc-core — RUNTIME_SOURCE_PINS re-hashed at CI plus the auditor App head-pinned attestation; the external C4 dependency-record half is retired"
status: proposed
date: 2026-10-15T14:08:03.921Z
project: bc-core
domain: metrics
subdomain: metrics/mcf-runtime-authority
focus: runtime: single-sided in-repo engine-bytes reviewed-authority (CI re-pin guard + App attestation)
---

# Reviewed engine-bytes authority is single-sided in bc-core — RUNTIME_SOURCE_PINS re-hashed at CI plus the auditor App head-pinned attestation; the external C4 dependency-record half is retired

## Context

bc-core #954 (the `aggregate_as_of` PE-MC engine change; DEC-3926bf Amd 2 / M13) passed Codex engine-lane review at head H=`6a1a960bcaaeb7962c3783ad95d67f2c7e7b0d42` but could not merge: Codex's gen-2b0f15-02 boundary required an external **C4 reviewed-successor publication** binding the new engine bytes with a recomputed `record_digest`, and that publication has no authorized home — DEC-44456d scoped bc-external-audit to the exchange mailbox, the Auditor App is deliberately not installed there, and commit `df16a9d0` removed the C4 publication, its implementation and its fixtures. Meanwhile the in-repo authority (`RUNTIME_SOURCE_PINS` + the CI re-pin guard) already emits and proves the engine-bytes authority deterministically at CI; the external half is a retired-framing duplicate. Operator decided (2026-10-15, relayed by the Chief) to make the authority single-sided in-repo rather than revive the retired external machinery. This unblocks #954 on gates that already pass green at H and aligns the engine-bytes-authority model with DEC-c48b0f and DEC-44456d.

The historical model (authority_refs `D450` / `DEC-2411e4` in `closure-runtime-authority.ts`) was two-sided by design: bc-core holds the engine runtime descriptor and the auditor **independently re-derives the same descriptor from its published `c4-dependency-record-authority`, so the two `record_digest`s match byte-for-byte**. That external half is what is retired here. The verifier-v2 engine *identity* (`DEC-2411e4`) is unchanged.

## Decision

The authority that the SERVED metric-evaluation engine equals the AUDITOR-REVIEWED bytes is recorded SOLELY in bc-core and proven at CI. `closure-runtime-authority.ts` holds `RUNTIME_SOURCE_PINS` (the utf8-LF sha256 of each engine-defining source); `closure-dependency-record.service.spec.ts` re-hashes every pinned source against its on-disk bytes on every CI run and fails the build on any drift (the re-pin guard). Combined with the auditor App head-pinned PR approval (`bc-auditor-app[bot]`, distinct from the PR author) and green head-pinned CI, these three are the complete, drift-proof, **EMITTED** proof (Invariant VI) that the served engine == the reviewed bytes.

The external, two-sided C4 `dependency-record-authority` publication in bc-external-audit — where the auditor independently re-derived a matching `record_digest` byte-for-byte — is NOT part of the authority and is NOT required to merge an engine change. The verifier-v2 engine IDENTITY (`DEC-2411e4`) is unchanged; only the publication locus of the reviewed-bytes authority changes. Repair location **D** (the authority declaration lives in the engine's own repo, CI-re-hashed) is Foundation-faithful: the proof that the served engine equals the reviewed bytes is emitted at, and travels with, the engine and is re-checked deterministically at CI, rather than inferred from a separable external publication that can drift.

**The merge gate for an engine change is therefore:** the in-repo `RUNTIME_SOURCE_PINS` re-pin guard (green) + the App head-pinned attestation + green head-pinned CI. No external C4 reviewed-successor publication is required.

This ADR supersedes nothing live: the external-audit-engine framing was already retired (DEC-3d6eeb superseded by DEC-c48b0f) and the external C4 machinery already removed from bc-external-audit (DEC-44456d point 6, commit `df16a9d0`); this ADR completes that retirement for the runtime engine-bytes authority specifically and declares the positive single-sided model.

## Foundation Gate (DEC-79b62f)

Repair **D** (evaluation implementation — the engine's own repo). Design act (DEC-c48b0f): the changed **declaration** is the engine-bytes *authority model* (where the reviewed-bytes proof is recorded), not a detector; it is named here, not merely implemented.

1. **Why D?** The authority is "the served evaluation engine == the reviewed bytes." That binding is a property of the engine implementation and belongs with the engine, in its own repo, where it can be re-checked deterministically against the actual source on every build. The in-repo `RUNTIME_SOURCE_PINS` + the CI re-pin guard are exactly that.
2. **Why not an upper layer (A/B/C)?** This is not a meaning, contract, or binding gap — the engine's meaning (mcf-verifier-v2, `DEC-2411e4`) and the evaluator contract are unchanged. The only question is *where the reviewed-bytes authority is recorded and proven*, which is an implementation-locus (D) question, not an upper-layer specification gap. A/B/C stay as they are.
3. **Why not a lower layer (E/F)?** No working lower implementation is bypassed. A read-model/projection could not prove "served == reviewed bytes" without re-deriving over the source (the forbidden reads-trigger-evaluation); the proof must be emitted at build/CI over the actual engine source, which is D.
4. **Design or execution act (DEC-c48b0f)?** DESIGN — the declaration that the reviewed-bytes authority is single-sided in-repo and that the external C4 half is retired. Each per-change re-pin + its CI run is execution, gated separately.

**Invariant VI (evidence emitted, not inferred).** The single-sided model *strengthens* Invariant VI: the proof is emitted deterministically at CI over the on-disk engine source (the re-pin guard), not inferred from, or reconstructed against, a separate external publication that can silently drift from the served bytes. A second, separately-published copy that must be kept byte-identical is a drift surface, not additional evidence.

## Scope and shape

- **Authority surface (in-repo, bc-core):** `src/registry/mcf/closure-runtime-authority.ts` — `RUNTIME_SOURCE_PINS` (per engine-defining source: `path` + `utf8_lf_sha256`), plus `EXECUTION_ENGINE_RUNTIME_RECORD` and `NUMERIC_REPRESENTATION_RUNTIME_RECORD` descriptors. `src/registry/mcf/closure-dependency-record.service.spec.ts` — the re-pin guard that re-hashes each pinned source against disk at CI.
- **The three-part gate** for any engine-byte change: (1) the re-pin guard is green (every pinned source's on-disk utf8-LF sha256 == its pin); (2) the auditor App head-pinned approval is present (bc-auditor-app[bot], distinct from the author); (3) head-pinned CI is green. All three bind the exact PR head.
- **Retired:** the external `c4-dependency-record-authority` publication in bc-external-audit and the auditor's independent byte-for-byte re-derivation of a matching `record_digest`. The `authority_refs` tag on the in-repo runtime descriptors (`['D450','DEC-2411e4']`) is preserved for provenance; `DEC-2411e4` (verifier-v2 identity) stays authoritative. No external publication locus is to be stood up for engine-byte changes.
- **Out of scope / unchanged:** the mcf-verifier-v2 algorithm (`DEC-2411e4`); the evaluator contract and PE-MC/M13 evaluator capability (`DEC-c741a3`); `aggregate_as_of` authoring and admission (a separate later act); all non-engine dependency records the closure assembles.

## Evidence (grounded at head H; recomputed in-unit, not relayed)

- **In-repo pins bind real bytes @ H.** `closure-runtime-authority.ts` `RUNTIME_SOURCE_PINS` pins four sources; each file fetched at H and recomputed utf8-LF sha256 == its pin: `formula-execution.engine.ts` `sha256:5f5140892463150f96815b5472577ce9caf1e35c7ecf442fd31b10786ad95df6`; `resolver-fixture-config.interpreter.ts` `sha256:cdafaadce3cddc99a45ec964fb5fadd9e82f011c17acb6cc8e37237dd2e5fe49`; `mcf-evaluation-policy.spec.ts` `sha256:0fbfaeb54d5eebebaf752e57c4f2d41842f5a5caf9fa67851a4b0771aae78f95`; `mcf-evaluation-policy.ts` `sha256:623ff0585fa43ea8056eb4f36cc6b8b8ac59f3d5fd23e105527c57d2e79a0f28`.
- **The re-pin guard is real and drift-proof.** `closure-dependency-record.service.spec.ts` (test "each pinned utf8-LF sha256 still matches the on-disk engine source (re-pin guard)") reads each pinned source from disk, normalizes CRLF→LF, sha256s it, and asserts it equals the pin, failing with "drifted from its pin — re-pin + re-coordinate with the auditor." It runs on every CI run.
- **Head-pinned auditor + CI @ H.** Auditor App approval review `5534008280` (bc-auditor-app[bot], APPROVED, commit == H); CI run `38742954053` conclusion success (7 jobs, quality-gate) at headSha == H.
- **The external half was self-contained/divergent and is retired.** bc-external-audit `references/c4-dependency-record-authority-v1.json` (publication `bc-c4-dependency-record-authority-publication-v1`, authority_revision `2026-07-13.1`) bound the pre-change engine `sha256:e7e9dc59…cf51` with execution_engine `record_digest sha256:d6439cf9…a826595`; it was removed in commit `df16a9d0` under DEC-44456d point 6. (In-code citations independently confirmed by Platform [SES-6cd29a] and re-verified here.)

## Status

Proposed. Operator-decided direction (2026-10-15, Option 2, relayed by the Chief); Foundation gate passed (Repair D, design act). The decided-status flip takes a **recorded, byte-bound operator desk grant** against the ADR text at an exact head (the DEC-346ae7/#182 and DEC-c741a3/#191 precedent — decided status needs a recorded grant, not a chat relay). Because this ADR changes the engine-change merge gate and the auditor's attestation model, it goes to **Codex for a design review** before the decided flip. Once decided, bc-core #954's merge gate is the in-repo re-pin guard + App attestation + green CI (all green @ H), and the external C4 reviewed-successor requirement is formally withdrawn (gen-d02b18 resolved accordingly).

## References

- **DEC-79b62f** (the Foundation gate), **DEC-c48b0f** (design vs execution act; "external audit" framing retired), **DEC-44456d** (bc-external-audit revived as exchange-only; C4 machinery retired, point 6 / commit `df16a9d0`).
- **DEC-3d6eeb** (external metric-correctness audit engine — the external-audit-engine framing; superseded by DEC-c48b0f) — the ancestor of the external C4 dependency-closure manifest.
- **DEC-2411e4** (verifier-v2 engine identity — unchanged by this ADR).
- **DEC-3926bf** Amd 2 / **DEC-c741a3** (M13 PE-MC as-of conditional aggregate) — the engine change (#954) that this authority model gates.
- In-repo: `src/registry/mcf/closure-runtime-authority.ts`, `src/registry/mcf/closure-dependency-record.service.ts`, `src/registry/mcf/closure-dependency-record.service.spec.ts`, `src/registry/mcf/dependency-record-authority.ts`.
