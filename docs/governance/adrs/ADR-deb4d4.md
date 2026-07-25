---
uid: DEC-deb4d4
title: "Feed-integrity hardening package: rehearsal lane, zero-deferral rule, lane-retired supersession, enforcement-3 cut, evidence retention, vector siblings"
description: "Rehearsal lane gates all live audit traffic; zero-deferral in the signing path; enforcement-3 cut; lane-retired supersession un-strands 12; byte retention + cross-engine vector siblings"
status: decided
date: 2026-07-25T09:08:17.526Z
project: bc-core
domain: metrics
subdomain: metric-audit/exchange-feed
focus: governance
---

# Feed-integrity hardening package: rehearsal lane, zero-deferral rule, lane-retired supersession, enforcement-3 cut, evidence retention, vector siblings

## Context

Three canaries plus one ten-member batch consumed a wave's time because the two-engine contract was discovered one production refusal at a time: CF-R3 recompute divergence, closure-derivation divergence, authority-stamp inheritance — each landing in an append-only lane where mistakes become permanent signed bytes, burned one-shot request identities, or wedged feeds. The platform surfaces canary-hardened cleanly (no new platform defect after their first exercise); the auditor pipeline never got the same conformance treatment, and its one known-deferred defect produced the single most expensive failure of the program. The failure space of a packet is finite and enumerable (signature, registration, sequence, prior digest, schema, pin fields, recompute rules, basis rules) — so a rehearsal gauntlet converges where live-lane discovery spins. Line-rule accounting: the lane-retired strand shape has recurred at scale (12 subjects) and earns its supersession class; the epoch cut has recurred once and stays on existing paths with an explicit third-occurrence tripwire.

## Decision

One package, operator-ratified 2026-07-25, closing the integration-defect loop that consumed the canary suite and halted W2a batch 1. Six parts, sequenced:

1. REHEARSAL LANE (gate for ALL future live traffic): a read-only conformance surface that runs a candidate auditor packet through every live gate — batch-wide drift, wire validation (report + decision, C1), pin binding, registration/sequence expectation — WITHOUT any commit, append, or acknowledgement. Refusals become free. No packet reaches an enforcement feed until the same auditor pipeline version passed the full gauntlet dry.

2. ZERO-DEFERRAL RULE (signing path): no defect inside signed bytes is ever again recorded as a non-blocking caveat. The W2a halt was caused by exactly such a deferral (auditor run-row authority inheritance, flagged at B-prime): ten unimportable signed packets, twenty wedged ledger sequences, ten burned requests.

3. AUDITOR FIX FIRST: Codex root-causes and fixes the run-row authority inheritance defect and proves it through the rehearsal lane before any re-signing.

4. ENFORCEMENT-3 EPOCH CUT (D533 applied instance #2): enforcement-2 is wedged — the auditor ledger holds sequences 5-24 whose signed decision payloads carry the retired r3 source policy and can never import (V-D8 class). Cut via the existing registration paths per DEC-97445d: retire enforcement-2 after its imported head (seq 4), bootstrap + C1-register enforcement-3 (first registration, no cross-feed supersession per GOV-ERR-001), one reviewed constant flip. Stale rows preserved. The standing epoch/disposition machinery question that D533 named as triggered by a second cut is DECIDED AS: still not built — the cut path via existing registrations is proven and cheap; a THIRD cut after the rehearsal lane exists would evidence a deeper defect and reopen the question.

5. LANE-RETIRED SUPERSESSION CLASS (new class d): a request may be superseded when its response lane is provably retired with no decision ever imported for it — evidence-based and fail-closed (both conditions verified in-tx), never operator discretion. Un-strands all 12 lane-stranded subjects (95ff564c, 06e1087f, the 10 W2a members); e44a1c1e recovers via existing class (b). Design goes to Codex for disposition before implementation.

6. EVIDENCE-CONTRACT COMPLETION: (a) request-time closure-manifest byte retention (the emit path already holds the manifest at freeze; retain it append-only, keyed by request — Invariant VI: evidence is emitted, not inferred); (b) vector siblings for every cross-engine derivation that today exists only as two codebases — closure-assembly vectors, authority-stamp vectors, full-packet conformance vectors — exchanged and digest-pinned like the gate-5 wire set.

Resume criterion: W2 live traffic resumes only after the rehearsal lane is green for the auditor pipeline version in use. Un-strand sweep is the package's first delivery after parts 3-5 land.
