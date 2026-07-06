---
uid: bcf-mcf-panel-workbench-alignment-note
title: BCF / MCF Panel Workbench Alignment Note
description: Short alignment note that reconciles three positions on the panel architecture for the Business Context Framework (BCF) and the Metric Context Framework (MCF). (1) BCF requirements doctrine — governed tool workbench with same-workbench rule, closed read-tool surface, per-agent transcripts (locked in commit 1d7d209). (2) BCF v1 implementation — already built and uses a bounded authoring-context packet assembled by bc-core from governed F5 reads as the v1 retrieval vehicle; BCF enrichment proceeds on this v1. (3) MCF doctrine — explicit workbench-not-packet wording locked in M0 commit 6ce9451; MCF starts with workbench because it is not yet implemented and metric authoring requires broader read awareness than BCF v1 currently exposes. The note is descriptive and informative, not an ADR and not a build plan. It exists to prevent future confusion when a reader sees the BCF v1 packet implementation alongside the requirements doctrine and wonders which is the target.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: alignment-note
---

# BCF / MCF Panel Workbench Alignment Note

## 1. Purpose

This note aligns three positions that, read together, can look like contradictions but are not:

1. **BCF requirements doctrine** — the Business Context Framework requirements doc (`business-context-framework-requirements.md`, post commit `1d7d209`) frames the panel as a **governed tool workbench**: same-workbench rule for consensus validity, closed read-tool surface, per-agent immutable transcripts, no raw DB / SQL access, no packet-in / verdict-out function.
2. **BCF v1 implementation** — the bc-core / bc-ai code that ships BCF authoring today uses a **bounded authoring-context packet** assembled from governed F5 reads as the v1 retrieval vehicle that the panel consumes.
3. **MCF doctrine** — the MCF M0 pre-M1 decision packet, after correction in commit `6ce9451`, locks the **governed workbench, not packet** framing as a mandatory M1 ADR snippet (§14.9), with allowed read tool surface and forbidden surfaces enumerated.

The three positions are coherent once the relationship is named explicitly. This note names it.

**Scope and discipline:**

- This is a docs alignment note — descriptive, informative.
- Not an ADR. No new authority is created.
- Not a build plan. No gates are sequenced.
- Not a code-change instruction. BCF v1 implementation is not modified.
- Not a doctrine revision. BCF requirements doctrine and MCF M0 doctrine are unchanged.

The note exists so that a future reader who sees the BCF v1 packet implementation alongside the requirements doctrine does not need to re-derive whether one is wrong, which is the target, or how MCF should differ.

---

## 2. Current BCF state

### 2.1 What is built

BCF registry architecture is materially built and in use today:

- **Concept Registry substrate** — `concept_registry.entity`, `concept_registry.business_concept`, `concept_registry.characteristic` (confirmed intact per D418 Gate 5.3 verification in SES-fe15e0).
- **F3 authoring service** — bc-core service path for BCF concept authoring writes.
- **F5 read surface** — governed read endpoints exposing concept registry shape for downstream consumption.
- **Panel-output record ingest** — the substrate path that records panel verdicts as immutable authoring records per BCF requirements §Chapter 7.
- **Registry authoring panel run path** — the operational chain from candidate intake through panel consensus to publication eligibility.
- **bc-admin browse / publication / provenance surfaces** — operator console for inspecting concepts, publication gates, provenance, panel run history.

### 2.2 What remains pending

- **BCF enrichment** is ongoing. The Registry contains the substrate carved out in the BCF arc (Sales Order Line entity, unit-price BC, lead time, cycle time characteristics confirmed active per CLAUDE.md / D418 Gate 5.3 baseline). Broader concept population is operator-paced.
- Enrichment scope is bounded by current operator priorities, not by an attempt to author every conceivable BC.

### 2.3 BCF v1 panel retrieval — the packet

BCF v1 panel retrieval uses a **bounded authoring-context packet** as the v1 retrieval vehicle:

- `bc-core` `registry-authoring-context.builder.ts` assembles the packet from governed F5 reads (Registry slices relevant to the candidate area, lifecycle history, prior panel outputs).
- `bc-ai` `registry_authoring_panel.py` consumes the packet, runs the three-model consensus over its contents, and emits the verdict.
- The packet is **bounded** in the sense that it carries only what bc-core's builder decided to put in it; the panel does not call additional tools mid-run.

This is acceptable for BCF v1 because (a) bc-core assembles the packet from governed F5 reads (not raw DB access), (b) the BCF enrichment scope is currently narrow enough that the packet's bounded slice is sufficient for the panel's reasoning, and (c) the alternative (full governed read-tool workbench) was not required to ship v1 of the BCF panel.

---

## 3. Doctrine

The doctrinal position — BCF requirements doctrine and MCF doctrine align here:

- **Governed tools are safe enough to reason; raw substrate access is dangerous.** The panel must operate on governed surfaces, not on raw DB tables or unscoped query results.
- **The panel should have broad governed read awareness of governed platform surfaces, not arbitrary DB access.** Read access is wide; substrate write authority remains narrow and gated.
- **Package / proposal / output is the result of investigation, not the input cage.** Whatever the panel emits — a BCF concept proposal, an MCF metric package — is the consequence of the panel's reasoning, not a transformation of a pre-loaded bundle.
- **Same-workbench rule** is the consensus validity precondition. Three models must operate against the same governed surfaces (same allowed tool set, same evidence-source allowlist, same registry snapshot id, same policy version, same operator-context hash) for their verdicts to constitute consensus.

The doctrine is the target. Implementation may stage toward it.

---

## 4. BCF v1 interpretation

### 4.1 What v1 packet means

The bounded authoring-context packet that bc-core assembles for BCF v1 is a **v1 retrieval vehicle**. It is the mechanism by which today's BCF panel sees governed Registry content. It is the implementation choice for shipping v1 — a fixed bundle is simpler to assemble than a tool-call interface, and BCF v1's enrichment scope is narrow enough that a bundle suffices.

### 4.2 Why it is acceptable as v1

Three conditions make the v1 packet acceptable:

1. **bc-core assembles it from governed F5 reads.** The packet does not contain raw DB rows, raw SQL results, or substrate fragments. Every field in the packet traces to a governed F5 endpoint that itself enforces read discipline.
2. **BCF enrichment scope is currently narrow.** The panel's reasoning surface is small enough that what bc-core can pre-assemble is sufficient. The panel does not currently need to discover, compare, or probe across surfaces the packet cannot anticipate.
3. **v1 shipped under operator awareness.** The packet model was the chosen path for BCF v1; operator and architecture review accepted it as the shipping mechanism.

### 4.3 What it is not

The v1 packet is **not** any of these:

- **Not the long-term architecture.** The doctrinal target is a governed read-tool workbench. The v1 packet ships ahead of the workbench retrofit because v1 enrichment scope allows it.
- **Not a precedent that justifies expanding packet contents indefinitely.** Adding more pre-assembled fields to the packet to cover broader reasoning is the wrong path. The right path, when the panel needs broader reasoning, is to retrofit to a tool-call interface.
- **Not a reason to deny future governed read-tool workbench evolution.** BCF requirements doctrine continues to specify the workbench as the target. v1 is a station on the path, not the destination.
- **Not a discipline weakening.** v1 still enforces same-workbench rule (same packet contents across the three models for consensus), per-agent transcripts (each model's reasoning over the packet is recorded), and panel-output record immutability. The doctrine's discipline holds at v1; only the retrieval mechanism is bundle-vs-tool-call.

### 4.4 Threshold for B6-v2 retrofit

If BCF enrichment grows to a point where the packet's bounded slice is insufficient for the panel — e.g. the panel needs to discover concepts outside the candidate area, probe lifecycle history beyond what bc-core pre-assembled, or compare against multiple Registry slices the builder cannot anticipate — open a focused **BCF B6-v2 workbench retrofit** gate rather than expanding packet contents indefinitely.

This note does not specify what that retrofit looks like; it just names the trigger condition. The B6-v2 gate is a separate design effort governed by BCF requirements doctrine.

---

## 5. MCF implication

### 5.1 MCF starts at workbench, not packet

MCF is not yet implemented. Its M0 pre-M1 decision packet (`metric-context-framework-m0-pre-m1-decision-packet.md`, post commit `6ce9451`) explicitly locks the workbench framing as a mandatory M1 ADR snippet (§14.9 "MCF panel operates as a governed workbench, not a packet consumer"). MCF starts directly with the doctrinal target because:

- **It is not yet implemented.** There is no v1 packet to honour; MCF can choose its first implementation freely.
- **Metric authoring requires broader read awareness than vocabulary authoring.** A BCF concept proposal needs the concept's local area in the Registry; an MCF metric package needs:
  - **BCF Registry** — for variable bindings, grain entity, computed-dimension date sources.
  - **Candidate reservoirs** — Mongo `bc_seed.seed_metrics`, preserved `metric_definition` / `metric_knowledge`, operator-direct submissions.
  - **Source reality summaries** — what source / admission / observation contracts exist for a tenant; what fields exist.
  - **Fiscal / calendar configs and computed-dimension governing configs** — for `fiscal_period` / `fiscal_year` / `fiscal_quarter` resolution.
  - **Prior MCF drafts and active packages** — for duplicate-intent detection at PE-MC-9, for re-authoring orientation, for supersession context.
  - **Formula pattern library** — the 134 distinct legacy formula shapes (per gap survey Q-11) as weak-hint reference.
  - **Self-verification fixtures** — both proposed fixtures the panel is composing and prior fixture results for related packages.
  - **Readiness / chain / MLS summaries** — for runtime-readiness reasoning, for chain-completeness signals, for MLS state context.
- **A pre-assembled packet would be brittle by construction** for this surface count. The panel cannot reason about something the builder did not anticipate including. Pre-assembly that covers all of the above ahead of every panel run is operationally expensive; a tool-call interface lets the panel pull what it needs.

### 5.2 What MCF M1 consumes from M0

M1 (the foundational MCF ADR) consumes the corrected M0 §14.9 snippet from commit `6ce9451` as a mandatory named structural section of the ADR. The snippet enumerates:

- The trigger-not-cage framing for candidate-intent references.
- The allowed read tool surface (v1; ADR-amendable): 13 tool families spanning BCF Registry reads, reservoir reads, source reality summaries, fiscal calendar config, MCF state reads, panel history, formula library, chain status, readiness, MLS, evidence corpora.
- The forbidden tool surfaces: raw DB / SQL, tenant row-level data, substrate write tools, dropped BF/BO/CF/CM substrate, arbitrary application tables, unscoped operator notes, arbitrary internet retrieval, `concept_registry.*` writes (BCF authority territory), tools that bypass PE-MC-1..PE-MC-10 gates.
- The transcript discipline: every tool call logged with input hash + output hash + timestamp; citations must trace to transcript tool calls per PE-MC-1 grounding.

MCF M1 ADR thus encodes the doctrine as decided, with the tool surface explicit and amendable as a named section.

### 5.3 MCF does not inherit BCF v1 packet

MCF panel implementation should **not** copy BCF v1's `registry-authoring-context.builder.ts` + packet-consumer pattern. The MCF Metric Authoring Panel (build plan Gate M12) implements the tool-call workbench directly. This is the cleanest path because MCF can choose without backward-compatibility constraints.

---

## 6. Non-goals

This note explicitly does NOT:

- **Change BCF code.** No bc-core or bc-ai file is modified by this note.
- **Deprecate BCF v1.** v1 ships and continues to ship; BCF enrichment proceeds on v1 retrieval.
- **Implement MCF.** No MCF code is written. MCF M1 (foundational ADR) is the immediate next step in the MCF arc.
- **Decide an ADR.** This note is informational; authority lives in BCF requirements doctrine + MCF M1 ADR (when it lands).
- **Rewrite historical docs.** BCF requirements remain at commit `1d7d209`; MCF M0 packet remains at commit `6ce9451`; build plan remains at commit `40a9adc`.

---

## 7. Recommended future handling

1. **BCF enrichment continues on v1 packet retrieval.** No interruption. Operator-paced concept authoring proceeds as before.
2. **MCF M1 proceeds with workbench doctrine.** When the operator opens M1, the foundational MCF ADR records the workbench framing per the corrected M0 §14.9 snippet. No reference to BCF v1's packet shape is needed in M1.
3. **If BCF v1 packet retrieval becomes insufficient** — i.e. enrichment grows to require panel reasoning beyond what bc-core's builder can pre-assemble — **open a focused BCF B6-v2 workbench retrofit gate**. The retrofit is a separate design effort governed by BCF requirements doctrine; this note does not pre-specify it.
4. **If MCF implementation later wants to retroactively unify with BCF on a shared workbench substrate** — i.e. once BCF B6-v2 lands and MCF's workbench is shipping — that unification is a future architecture decision, not addressed here.

The three-position coherence holds as long as:
- BCF v1 packet is understood as v1 retrieval, not governing architecture.
- MCF starts at workbench because it has no v1 cost to honour.
- The doctrine (governed workbench, same-workbench rule, per-agent transcripts, closed read-tool surface, no raw DB) is the shared target of both frameworks.

---

## Document verification

- **All 7 required sections present** (§1 Purpose, §2 Current BCF state, §3 Doctrine, §4 BCF v1 interpretation, §5 MCF implication, §6 Non-goals, §7 Recommended future handling).
- **Explicit statement** that BCF v1 packet is the retrieval vehicle, not the governing architecture (§4.1, §4.3, §7).
- **No code-change instructions.** Non-goals (§6) confirm.
- **References MCF M0 correction commit `6ce9451`** (§1, §5.1, §5.2, §6).
- **References BCF doctrine commit `1d7d209`** (§1, §6).
- **References MCF build plan commit `40a9adc`** (§6 historical-docs preservation note).
- **No code/DB/schema files changed.** Single new doc commit to bc-docs-v3 main.
