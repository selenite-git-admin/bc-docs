---
uid: DEC-b390ef
title: "Legacy-doctrine supersession register — retired-design ADRs formally superseded by family"
description: "One governed act that supersedes 33 still-live ADRs whose designs were retired by later doctrine (BF/BO/CF vocabulary, SAP as a source, bc-ai, the D305/D366 chain-status substrate, the external-audit programme, historical demo tenants, the Mongo bc-seed store). The retirement decisions themselves disclaim supersession; this register supplies the missing authority so the D370 pair rule can apply."
status: decided
date: 2026-08-23T03:22:48.886Z
project: bc-docs
domain: governance
subdomain: adr-lifecycle
focus: supersession
supersedes:
  - DEC-1ce490
  - DEC-2e4cb3
  - DEC-339c97
  - DEC-616e02
  - DEC-683cf3
  - DEC-68f2c7
  - DEC-9361cd
  - DEC-9bffcd
  - DEC-aa6251
  - DEC-b8ec00
  - DEC-c338b3
  - DEC-f1dae0
  - DEC-f66378
  - DEC-9a5dc0
  - DEC-b7affa
  - DEC-637072
  - DEC-010bf9
  - DEC-523a5d
  - DEC-77f4b5
  - DEC-7e3779
  - DEC-b51b48
  - DEC-d2cdb9
  - DEC-d53320
  - DEC-d5c352
  - DEC-e93a19
  - DEC-fc41a3
  - DEC-076521
  - DEC-e9294b
  - DEC-bebaec
  - DEC-804874
  - DEC-253be2
  - DEC-3b23de
  - DEC-316f3c
---

# Legacy-doctrine supersession register — retired-design ADRs formally superseded by family

## Context

D370 (DEC-623f8f) requires that a superseded ADR be named by a successor. The ADRs that retired several designs were written as operational decisions and say so — DEC-6c57e2 (D417) and DEC-a19428 (D418) both state "Does not supersede any ADR"; DEC-ea9bdc declares the SAP catalogs contamination without naming prior ADRs; DEC-ffee4e supersedes only DEC-14fb98; DEC-c48b0f only DEC-3d6eeb; DEC-7ab22b names none. The result was 33 ADRs still carrying implemented/decided while describing designs that no longer exist in the platform (verified 2026-08-23 against the live platform DB and mounted bc-core code: the BF/BO/CF tables are absent everywhere, dropped under D418 Gate 5.1; G11 was never built; cc_field_mapping is gone). The bc-auditor review of bc-docs PR #9 (5001532360) correctly refused supersession pairs that lacked authority in the successor's own text. This register is that authority, issued by the operator as a single decision act rather than 33 edits.

## Decision

1. The ADRs listed below are **superseded**, effective on this decision's date. Each receives `status: superseded` and `superseded_by: DEC-<this uid>`; this ADR carries them in `supersedes:`. The **doctrinal basis** column names the decision whose content retired the design; it is cited, not re-decided here.
2. Supersession here means the design is **no longer authoritative**; the superseded ADRs remain as history and are not edited beyond their two frontmatter lines.
3. Explicitly **not** superseded (kept live): DEC-65dc86 (the BCF-forward transition decision itself), DEC-4a17e0 (BCF-era OC field-level identity), and every retirement decision cited as basis.

| Family | Superseded ADRs | Doctrinal basis |
|---|---|---|
| BF/BO vocabulary (Business Field / Business Object model, catalog, versioning, composition, provenance, factory) | DEC-1ce490, DEC-2e4cb3, DEC-339c97, DEC-616e02, DEC-683cf3, DEC-68f2c7, DEC-9361cd, DEC-9bffcd, DEC-aa6251, DEC-b8ec00, DEC-c338b3, DEC-f1dae0, DEC-f66378 | DEC-02f5a9 §3–4 (vocabulary identity model unsound; greenfield BCF rebuild), DEC-6c57e2 (D417 quarantine: legacy stack semantically non-authoritative), DEC-a19428 (D418 retirement). Substrate physically dropped under D418 Gate 5.1 (bc-core 03126db3, 2026-05-25). |
| CF boundary (Canonical Field as vocabulary primitive) | DEC-9a5dc0, DEC-b7affa | DEC-02f5a9 §2 (CF collapsed into BCF), DEC-6c57e2 |
| Derived canonical fields in `canonical_mapping` | DEC-637072 | DEC-7d2f8c (D461/D462: derivation home = CC body) |
| SAP as a live source (catalogs, landscapes, scanner, acquisition, admission stance, demo hooks, chain generation) | DEC-010bf9, DEC-523a5d, DEC-77f4b5, DEC-7e3779, DEC-b51b48, DEC-d2cdb9, DEC-d53320, DEC-d5c352, DEC-e93a19, DEC-fc41a3, DEC-076521 | DEC-ea9bdc (SAP catalogs and their contract chain declared contamination), DEC-296505 (D564 expunge), DEC-8b17b1 (D561 demo estates, Odoo base) |
| bc-ai service | DEC-e9294b | DEC-ffee4e (D483 retire bc-ai; panels in-process) |
| D305 / D366 chain-status substrate | DEC-bebaec, DEC-804874 | DEC-7ab22b, DEC-9c0da7 (D481 runtime doctrine) — tables dropped Runtime Spine R3/R6 |
| External-audit programme | DEC-253be2 | DEC-793e13 (D540 exchange retired), DEC-c48b0f (D541 certification is an MCF lifecycle act) |
| Historical demo tenants (sandbox1, apex) | DEC-3b23de | DEC-8b17b1 (D561); those tenant databases no longer exist (pilot1 is live) |
| Mongo bc-seed catalog service | DEC-316f3c | DEC-0b5a4c Amendment 1 (D551: direct admission; bc_seed retired) |

Consequences: the `docs:audit:adrs` pair rule is satisfied for all 33. Future retirement ADRs SHOULD name what they supersede, or a register entry is required (this ADR is the template). DEC-cbc07b is not in this register: it is reversed separately by operator ruling of 2026-08-23 (stuck proposal withdrawn).

Operator decision record: ruled by anant on 2026-08-23 ("1. B", then "approve register") in DevHub session SES-a1d30b; text approved before recording.
