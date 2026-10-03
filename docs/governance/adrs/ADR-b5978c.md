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
- Fitness is computed over a calibration set of N recorded corpus **attempts**, with N declared before the first attempt. Every attempt uses the same harness commit, corpus digest, roster and prompt version, and a fresh clone. Every attempt is recorded and none is discarded. Because D4 allows a case to end incomplete, an attempt is not necessarily a complete corpus run.
- **N = 5.** The predicate is asymmetric, and every count is over **completed** observations:
  - no planted-defect case is verified in any completed observation;
  - each positive is verified in at least N−1 attempts;
  - each negative is attributed (D3) in at least N−1 attempts;
  - each case completes (D4) in at least N−1 attempts; otherwise the set is *inconclusive*.
- **What "fit" claims, and what it does not.**
  - "Fit" is an observed statement about this fixed corpus under this roster and prompt version: in every completed observation, no planted defect was verified, and the sound case and the attributions held as above.
  - The manifest reports the completed-observation count for each case, which is the denominator.
  - "Fit" claims **no** statistical bound on a false-verify rate. The attempts repeat the same planted cases; their independence is not established; and no sampling model is defined that would make them representative.
  - A fixed corpus says nothing about defect classes it does not contain, or about unseen packages.
  - Any rate claim needs a separate decision that defines the estimand, the sampling assumptions and the calculation.

**D2. A moderator's overrule of a refutation must carry a structured, grounded answer, enforced in code. Whether the answer is correct is measured, not proven.**
- On a refuted run, a moderator ruling of PANEL_VERIFIED counts only if the moderator output carries a `refutation_answer` that passes these structural checks in `derivePanelOutcome`:
  - (a) its `target` equals the adversary's non-empty `refutation_target` exactly;
  - (b) it cites at least one exhibit id;
  - (c) each cited id was minted for the moderator seat in this run (the existing exhibit-grounding mint).
- If any check fails, the refutation stands and the run is PANEL_REJECTED. An absent field is never read as permission.
- A refutation counts only with a non-empty `refutation_target`.
- **What the structural checks do not prove.** They do not establish that the cited text answers the allegation. A minted but irrelevant citation passes them. Whether answers are *semantically* correct is an empirical question, answered by calibration.
  - Before D2 may be claimed to address overrule safety, the corpus gains at least one negative case whose package holds a plausible but non-answering section. A moderator that cites that section to overrule the refutation must show up as a false verification under D1.
- **Retry classes.** An id that fails to mint uses the existing `unmintable_exhibit_citation` retry class. A minted but irrelevant answer is not a transport or structural failure: it is the moderator's ruling, recorded as such, and calibration catches it.
- The prompt states the same rule. The derivation enforces the structure.
- A matching DB-guard refusal is optional phase 2. It is DDL and needs the operator's database yes.

**D3. Attribution is structured.** Each planted case declares its `defect_class`. The prevailing position must name that class, from a closed list, in a structured field. Comparison is exact; there is no substring search.

**D4. A transport fault is not a verdict.**
- Every seat act, and the pre-corpus smoke, retries a transport-class failure under one declared, bounded policy: at most 2 retries, with the first refusal kept. Transport classes are a vendor/HTTP error, no submit call (the DSML leak), and a malformed envelope.
- **Every attempt is durably recorded, including when all retries fail.** An incomplete case's transcript entry carries its full attempt list (each attempt's class and refusal), not only a final error string.
- A case that still fails after its retries is *incomplete*: never a pass, never a fail.
- An inconclusive set is re-run as a new set, and the old one stays on record.
- The DSML leak itself is fixed in the engine lane.

**D5. Rules before judgement.** Under DEC-c48b0f item 4, each defect class that gets a deterministic PE-MC check leaves the panel corpus and joins the substrate-proven classes. The order is wrong grain, then temporal boundary (TSK-e4a016 part 2), then closure omission and misbound input. The panel keeps definition↔formula fidelity, ambiguity and filter semantics. This is the durable fix.

**D6. The record (phase 1, no DDL).**
- A calibration set is a committed manifest. It holds the set id, N, the predicate version, the harness commit, the corpus digest, the roster, the prompt version, and each attempt's transcript sha256. The transcripts are committed beside it.
- The verdict is a pure function of the manifest **plus the hash-verified transcripts it names**, so a reader can recompute it.
- `calibration_evidence_ref` cites the manifest (`<path>=sha256:<hex>`, the existing CHECK shape).
- In phase 1 the prompt version is recorded as provenance in each calibration transcript, beside the harness commit, and in the manifest.
- Phase 2 (DDL, the operator's yes): `mcf` calibration-set tables, a prompt-version column on panel runs, and a prompt-version pin on the registration.

**D7. Registration stays the operator's act (DEC-d3b916 clause 3).**
- It cites a calibration-set manifest and its computed verdict.
- Registering against a set that is *not fit* or *inconclusive* needs the operator's explicit acknowledgement, of at least 40 characters.
  - Phase 1 record path: the acknowledgement is a recorded operator grant at the bc-exchange desk. Its `grant_id` and `text_sha256` are written into the manifest before registration, so the registration's evidence reference covers it. The existing registration row has no field for either.
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

## Review

- **Codex round 1** (gen-1b9e88-01, reply commit dacbe1a5, sha256 e8129a28…): CHANGES REQUIRED, with two blocking findings.
  - D1's confidence bound was unsupported. It is removed. "Fit" is now an observed statement about the fixed corpus, with the completed-observation denominator recorded, and N counts attempts.
  - D2 overstated what structural validation proves. It now names the exact structural checks, leaves semantic correctness to measurement, and requires a plausible cited non-answer negative case.
  - The implementation boundaries Codex named are folded in: D4 records attempts durably even when every retry fails; D6's verdict is recomputed from the manifest plus the hash-verified transcripts; D7 records the acknowledgement as a desk grant written into the manifest; and phase 1 records the prompt version in the transcript.
