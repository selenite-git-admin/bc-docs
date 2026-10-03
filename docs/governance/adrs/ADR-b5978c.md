---
uid: DEC-b5978c
title: "Certification panel fitness is a declared multi-run standard; a moderator overrules a refutation only by citing the answer"
description: "Panel-2 calibration fitness is computed over a pre-declared N=5 calibration set with an asymmetric predicate; a moderator VERIFIED over a refutation requires a cited, grounded answer enforced in derivePanelOutcome; structured attribution; bounded transport retry (incomplete is not a verdict); deterministic rules replace panel judgement for grain/temporal/closure/misbound; manifest record; registration stays the operator's act. Interim: new certifications pause until D2 lands."
status: proposed
date: 2026-10-03T08:43:30.853Z
project: bc-core
domain: metrics
subdomain: metric-certification/panel-calibration
focus: governance
---

# Certification panel fitness is a declared multi-run standard; a moderator overrules a refutation only by citing the answer

## Summary

A non-deterministic judge cannot be certified fit on a single sample. The calibration evidence (F1–F10) shows the moderator alone decides and can overrule a correct refutation, which put three planted defects through in one run. A declared multi-run standard and a structural overrule rule make "fit" a recorded, recomputable claim (Invariant VI). Moving mechanical defect classes to deterministic rules (DEC-c48b0f item 4) removes the panel's least reliable judgements.

## Context

The certification panel (panel 2 under DEC-c48b0f: assessor, adversary, moderator) gives different calibration results from run to run on the same harness and roster. On 2026-10-03 there were three runs: v10 run 1 verified three planted defects; the v10 rerun was clean; and the v9 run missed one attribution. The grounded study is barecount-devhub `artifacts/architect/panel-fitness-2026-10-03/STUDY-certification-panel-fitness-standard.md` @31707112 (PR 240, deliverable DLV-f0beb6). The three transcripts are preserved beside it (sha256 76ae319e…, b603bc27…, 6d7c5024…). Findings, read at bc-core 832215bcc:

- **F1.** Fitness is computed over one corpus pass (`audit-panel-calibration.service.ts:303-305, 336-340`). The service itself says model non-determinism is not covered (`:221-222`).
- **F2.** No code reads `fit_for_registration`. Registration checks only the shape of the evidence reference. The one live registration cites the r23 report, whose fitness is false. That is lawful: under DEC-d3b916 clause 3, registration is an operator judgement on cited evidence.
- **F3.** In every completed case of the nine runs on record, the adversary refuted, the sound positive included. So every case escalates, and the moderator's ruling governs alone (`audit-panel-rules.ts:81, 115-121`).
- **F4.** Nothing in the prompt, the derivation or the DB guard limits a moderator's overrule of a refutation.
- **F5.** Attribution is a substring match over all seats' outputs (`:390-394`). It is too strict, because a correct rejection in other words counts as a miss. It is too loose, because a refutation the moderator overruled still counts as found.
- **F6.** The measured N=3 arms all fall short:
  - baseline: 20/27 correct, 6/9 stable;
  - temperature 0: 19/27, 4/9;
  - moderator-cite sentence: 22/27, 4/9, which fails its pre-stated tolerance.
- **F7.** Production certification runs the panel once per certification run (`certification-panel-decision.lane.ts:264-274`).
- **F8.** The prompt version is never recorded.
- **F9.** Vendor errors are not retried, and the pre-corpus smoke has no retry, so a DeepSeek no-submit (DSML) leak aborts a whole calibration.
- **F10.** The unstable classes are the ones DEC-c48b0f item 4 says belong to deterministic rules.

## Decision

**D1. Fitness is a calibration set, not a calibration run.**
- Fitness is computed over N complete corpus runs, with N declared before the first run. All runs use the same harness commit, corpus digest, roster and prompt version, and each uses a fresh clone. Every run is recorded; none is discarded.
- **N = 5.** The predicate is asymmetric:
  - no planted-defect case is verified in any run;
  - each positive is verified in at least N−1 runs;
  - each negative is attributed (D3) in at least N−1 runs;
  - each case completes (D4) in at least N−1 runs, or the set is inconclusive.
- **What "fit" evidences, and its limit:** with 8 negatives, zero false verifications in 40 trials bounds the per-trial false-verify rate below about 7.5% at 95% confidence. "Fit" claims no more than that.

**D2. A moderator overrules a refutation only by citing the answer, enforced in code.**
- On a refuted run, a moderator ruling of PANEL_VERIFIED counts only if the moderator output carries a `refutation_answer`: the refutation answered, plus the exhibit ids of the package sections that answer it.
- The ids are validated by the existing exhibit-grounding mint; an unmintable citation is the existing `unmintable_exhibit_citation` class.
- Without a valid answer, the refutation stands and `derivePanelOutcome` yields PANEL_REJECTED. An absent field is never read as permission.
- A refutation counts only with a non-empty `refutation_target`.
- The prompt states the same rule, but the derivation is the enforcer.
- A matching DB-guard refusal is optional phase 2, which is DDL and needs the operator's database yes.

**D3. Attribution is structured.** Each planted case declares its `defect_class`. The prevailing position must name that class, from a closed list, in a structured field. Comparison is exact; no substring search.

**D4. A transport fault is not a verdict.**
- Every seat act, and the pre-corpus smoke, retries a transport-class failure under one declared, bounded policy: at most 2 retries, each attempt recorded, the first refusal kept. Transport classes are vendor/HTTP errors, no submit call (the DSML leak), and a malformed envelope.
- A case that still fails is *incomplete*: never a pass, never a fail.
- An inconclusive set is re-run as a new set, and the old one stays on record.
- The DSML leak itself is fixed in the engine lane.

**D5. Rules before judgement.** Under DEC-c48b0f item 4, each defect class that gets a deterministic PE-MC check leaves the panel corpus and joins the substrate-proven classes. The order is wrong grain, then temporal boundary (TSK-e4a016 part 2), then closure omission and misbound input. The panel keeps definition↔formula fidelity, ambiguity and filter semantics. This is the durable fix.

**D6. The record (phase 1, no DDL).**
- A calibration set is a committed manifest holding: set id, N, predicate version, harness commit, corpus digest, roster, prompt version, and each run's transcript sha256. The transcripts are committed beside it.
- The verdict is a pure function of the manifest, so a reader can recompute it.
- `calibration_evidence_ref` cites the manifest.
- Each panel run records the prompt version it ran under.
- Phase 2 (DDL, the operator's yes): `mcf` calibration-set tables and a prompt-version pin on the registration.

**D7. Registration stays the operator's act (DEC-d3b916 clause 3).**
- It cites a calibration-set manifest and its computed verdict.
- Registering against a set that is *not fit* or *inconclusive* needs the operator's explicit acknowledgement text, of at least 40 characters, recorded with it.
- A prompt-version change needs a new set.

**Interim (reliability first).** New certifications pause until D2 lands and a calibration set under D1 has been run. Metrics already active keep their status.

## Out of scope (follow-on decisions)

- Production certification runs the panel once per metric (F7), so even a fit panel's per-run error rate carries into every certification. k-of-n at certification, or a second-run review, is for a separate ADR.
- So is the retroactive question: metrics already active were certified on a single run.

## Foundation gate

- **Location B, enforced at D.** What "fit" means is an undeclared semantic of the certification contract. This is a design act (DEC-c48b0f item 5).
- **Not an upper layer.** Invariant VI and DEC-c48b0f are sound as they stand.
- **Not a lower layer.** Prompt tuning or re-running until a pass would be compensation.
- **Invariant VI.** One sample cannot evidence a rate, so "fit" is computed from a pre-declared, fully recorded set, and discarding a run is selection.
- **Invariant V.** Each run is a distinct act, never a replay. A rejected certification is never re-rolled in place.
- **Invariant I.** Untouched: calibration evaluates the panel, not a metric's meaning.

## Authority and status

- The operator signed off the recommended set (D1 N=5, D2 in the derivation, D3, D4, D5, D6 phase 1, D7) and the reliability-first interim on 2026-10-03, relayed by the Chief Controller.
- This record is **proposed** until the operator's grant is recorded at the bc-exchange desk. It moves to **decided** citing that grant_id and text_sha256.
- It amends the calibration methodology of DEC-05815d, which DEC-d3b916 clause 2 names as the methodology authority, without superseding it.
- Builds: Platform's engine lane builds D2–D5, reviewed against this ADR by the Architect. Engine code takes the normal Codex review. Calibration results go to the operator through the Chief.
