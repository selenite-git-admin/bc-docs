---
title: The Metric Lifecycle — Companion
description: What the lifecycle states MEAN — the hand-authored companion to the generated lifecycle and enforcement-surface maps. Descriptive layer; meaning, history, and doctrine in one place.
authority: descriptive
---

# The Metric Lifecycle — Companion

**Authority position (DEC-5a9dee ladder):** this is a LEVEL-5 descriptive document. Foundation
names the families and their states (The Contract Grammar); ADRs carry intent; the generated
`reference/lifecycle-map.md` and `reference/enforcement-surface-map.md` carry the enforced
machinery (level 3); the substrate is fact (level 4). This companion carries **meaning** — what a
state asserts, how that meaning came to be, and the doctrine that governs change. It never
restates a transition matrix; where machinery matters, it cites the maps. If this document ever
disagrees with them, they win.

**Provenance:** produced by the lifecycle authority study (2026-08-02/03; register + amendment
ledger at `barecount-devhub/artifacts/lifecycle-study/`, ratified ACCEPTED WITH BOUNDARY). The
study's founding observation: the lifecycle was re-derived on the flow every session because no
single document said what the states mean. This is that document.

## 1. The lifecycle in one paragraph

A metric begins as **intent** in the Metric Directory (a Member: what should exist, and why),
takes **meaning** through the Business Concept Registry (concepts its contract will bind — never
raw source vocabulary), becomes a **contract** in MCF (a draft MCV authored by the admission
panel from a seed candidate), and earns **`active`** only through certification (a second panel
judging the frozen package, then the C8-gated admission). Runtime consumers select `active`;
tenants see what runtime computes. Every arrow between families is a reference, never shared
state — the families are decoupled by design.

## 2. What each MCF state ASSERTS

| State | Assertion (what a reader may rely on) |
|---|---|
| `draft` | An admission-panel-approved proposal exists as substrate. Nothing about correctness. Abandonable (draft/review only — active metrics are never abandoned). |
| `review` | Under governed review. Same correctness claim as draft: none. |
| `approved` | Review complete; the package may be frozen and certification requested. Realization may point here (the directory may reference approved MCVs) — approval is NOT a correctness certificate. |
| `audit_pending` | **Awaiting certification — the honest raw-material state** (DEC-21ca17). Holds both never-certified feedstock and withdrawn subjects re-entering the lane. Nothing in this state reaches runtime. |
| `active` | **Panel-certified and calculator-grade** (DEC-793e13 as restated by DEC-c48b0f), runtime-computed, tenant-visible. The full assertion holds only for `certified_active` (live `audit_admit` cert); see §3 for the labelled exceptions. |
| `audit_blocked` | Certification-plane invalidation (C6: revocation, blocking NC, signer compromise). **Currently a dead-end by substrate**: reachable, exit hard-closed — a standing open design item (ledger E-2), deliberately not papered over here. |
| `superseded` | Replaced by an activated successor; preserved, addressable history (Invariant III). Re-enterable to `audit_pending` through governed reintake — "superseded" is terminal for identity, not for the audit lane. |

## 3. The meaning-history of `active` — read this before trusting old records

`active` is the one state whose meaning CHANGED over the platform's life. The dated record
(study finding F-030; every step individually sanctioned, the widening never restated until now):

1. **2026-06 (DEC-3f093f):** M14 activation is "a state change on the MCF substrate only… does
   not imply product or runtime visibility." Activation wrote a `metric_transition` cert. 343
   metrics activated under this meaning.
2. **2026-07-02 (DEC-a1290e):** the tenant read surface goes MCF-native — `active` now implies
   tenant visibility.
3. **2026-07-15 (C8, migration 46):** `approved → active` closes; certification becomes the only
   door. `active` is now supposed to assert "certified".
4. **2026-08-01 (DEC-c48b0f):** doctrine catches up — certification is an MCF lifecycle act;
   "an MCV reaches `active` only with a certification record."
5. **2026-08-02 (DEC-21ca17):** the grandfathered population is dispositioned — 226 never-audited
   legacy actives demoted to `audit_pending` through governed reintake (batch `89952e2c`; a
   named residue without resolvable directory identity remained active, pending identity
   minting — hard deadline: before the first real tenant). **The residue's current count is
   read from the readiness projection's `residue_legacy_active` line, never from this
   document** — it shrinks as its disposition completes.

Consequently the readiness projection (DEC-b049f6) renders `active` as a three-way split —
`certified_active` / `residue_legacy_active` / `unattributed_active` (an anomaly bucket, exposed
even at zero) — and no surface may merge those lines. When reading any record dated before
2026-07-15, remember: `active` then asserted publication, not certification.

## 4. The two-panel spine

Two panels, two questions, two moments (DEC-c48b0f):

- **Admission (M12: maker/checker/judge)** judges a PROPOSAL — should this metric exist, is it
  well-formed. Output: a draft MCV. The judge's holding is the consensus verdict.
- **Certification (assessor/adversary/moderator)** judges the FROZEN PACKAGE of a governed MCV —
  is the definition faithful to formula, bindings, grain, declared semantics. Output: a
  certification record, which the C8 gate requires for activation.

The sentence that reconciles "the panel is advisory" (DEC-3300f3) with "the holding is the
verdict" (DEC-09f86b): **verdicts gate what governed services may write, and only governed
services write.** Agents and panels recommend; substrate-guarded writers act.

**Rules before judgement** (DEC-c48b0f §4): anything machine-checkable — binding resolution,
grain agreement, currency policy, vocabulary conformance — belongs to deterministic surfaces
(PE-MC checks, `mcv_chain_status`), never to a panel. A rule discovered by a panel is a missing
rule; the remedy is the rule, not another panel run.

## 5. Plane separation — certification is not chain

Two questions, two homes (DEC-a6cdae): **certification** asks "is the definition correct" and
lives in the panel + certification records + C8. **Chain-readiness** asks "can it evaluate" and
lives in `mcv_chain_status` plus the preflight runtime-projection leg. A panel objection about
groundedness of chain facts is out of scope by design — answer with a scope statement, never a
prompt patch. The chain-health overlay on the readiness projection is display-only and must
never become a hidden gate (DEC-b049f6 boundary).

## 6. The corrective arcs

- **Withdrawal** (`active → audit_pending`; DEC-05815d, generalized by DEC-dd11e3): certification
  is valid-but-withdrawable — a certificate is a record of what was enforced at its time, and
  later evidence may suspend it. Withdrawal mints an `audit_reintake` cert, archives the
  withdrawn cycle's certs, and changes governance state, never history.
- **Reintake** (C7; migrations 48/53): the governed re-entry lane — accepted manifest → pinned
  members → operator-authorized batch → per-member cert + evidence + guarded flip. Identity is
  member-keyed: **no directory identity, no reintake** (the D546 residue exists precisely
  because of this).
- **Supersession** (M15; `active → superseded` paired with a successor's activation): built,
  never yet fired — its first real exercise is the pending D545 cohort supersession, which is
  therefore its commissioning test.
- **Abandon**: draft/review only, via the governed abandon surface; active metrics are never
  abandoned (identity immutability past draft).
- **Invalidation** (C6; `→ audit_blocked`): the certification-plane kill switch. Its missing
  exit is a known open item — do not design around it silently.

## 7. Eligibility basis and the numeric profile

Certification eligibility rides on numeric admissibility (DEC-545a4d, DEC-414ba2): **EXACT**
(scaled-decimal substrate) wins where available; **REPRODUCIBLE** (correctly-rounded, error
bound travels with the claim) is a distinct labelled basis, never a substitution. Both are
pinned to the runtime numeric profile (DEC-c4619b): under `binary64-v1` the entire
audit-eligible population collapses to NONE. **The eligibility of everything certified is
contingent on the profile staying `scaled-decimal-int-v1`** — a standing governance fact, not a
transient.

## 8. Cross-family doctrine

Intent, meaning, and contract live in three decoupled families; the lifecycle crosses them by
reference only. Two rules with teeth:

- **Identity is load-bearing:** governed lifecycle acts key on directory-member identity (C7
  tuples) — a metric without directory identity cannot complete every governed act (D546's
  operative proof). Mint identity first; never bypass the gate.
- **Judgement never travels:** no family stamps its verdicts onto another family's rows. MCF's
  agreement or friction with a concept or member is EVIDENCE (panel records, realization
  relations, rejection registers), surfaced through derived projections — never flag columns on
  BCF or Directory substrate (operator disposition 2026-08-03; parked build: cross-family
  friction projection).

## 9. The historical record, kept honest

The pre-C8 population (at the disposition act of 2026-08-02: 257 live subjects, of which 226
were demoted in batch `89952e2c` and the remainder held as named residue) is HISTORY, not
shame: every activation was sanctioned under the meaning of its
day, the M14 certs remain live as the record of those acts, and the disposition (DEC-21ca17)
carries its own stopping condition — complete before the first real tenant onboards. Foundation
errata FND-ERR-007/008 record the documentation gaps the same way. The platform's rule for its
own past: record it, date it, never rewrite it.

## 10. How to use this document

Start here for MEANING. Go to `reference/lifecycle-map.md` for the derived state machines, and
to `reference/enforcement-surface-map.md` for verbatim gate bodies — and regenerate both after
any substrate change before citing either. For intent behind any rule, chain-walk the ADR.
For any enforcement claim: cite the map, never memory (operator law, 2026-07-26 — now Foundation
doctrine via the DEC-5a9dee ladder).

**The numbers rule (operator, 2026-08-03):** this document — and every hand-authored durable
document — carries only **event-scoped historical constants**: numbers frozen by a completed,
dated act (a batch size, a cert count of a closed era), always anchored to the act that froze
them. **Live population counts never appear here**: anything a future act can change is read
from the generated maps or derived projections at the moment of use. A number without a date
and an act is a stat pretending to be history — remove it or anchor it.
