---
uid: DEC-c897cd
title: "One approved vocabulary for status words: docs/reference/vocabulary.md is the only authority, and its first slice is the words for a metric's life"
description: "Makes one bc-docs page the only authority for status words and records its first slice as the operator approved it: the six groups of a metric's life (seed; candidate and the other seed statuses; registered; draft to certified, released and certification blocked; superseded, retired, abandoned; the tenant words available, subscribed, enabled or disabled, visible or hidden, reporting), his answers on available and on reversing a release, both tenant switches belonging to the tenant admin, and the clearing of the versions marked active without a certificate."
status: decided
date: 2026-10-01T06:41:57.846Z
project: bc-docs
domain: governance
subdomain: governance/vocabulary
focus: status-words
---

# One approved vocabulary for status words: docs/reference/vocabulary.md is the only authority, and its first slice is the words for a metric's life

> **Decided 2026-10-01.** The operator approved the first slice and directed this record: desk grant `2026-10-01T06-36-21-158Z-648f1a32` (text SHA-256 `648f1a32faeea25c5c2639d91617b00a6582ead9c8ccc7d3826db8d9c117d498`, recorded 2026-10-01T06:36:21Z, request 155): "Yes: I approve the first slice of the BareCount vocabulary as written on the Architect page in barecount-devhub pull request 187 at commit 141b1af35366c92bf0468fdb074c112ca82b15a4, built on my six groups: seed; candidate and the other seed statuses; registered; draft, in review, approved, awaiting certification, certified, released, certification blocked; superseded, retired, abandoned; and for a tenant available, subscribed, enabled or disabled, visible or hidden, reporting. My answers to the two questions on that page: available means released; and when a release is reversed the metric goes back to certified and tenants that already have it enabled keep it. Both tenant switches belong to the tenant admin. The versions marked active without a certificate are a defect and are cleared by option 1 of section 3a. Codex may check this revised page once more before it lands, and the Architect records an ADR that makes one bc-docs page the only authority for status words. Anant". The Decision section restates that grant and adds nothing to it.

## Context

On 2026-10-01 the operator named the problem in his words: "there is too much noise about number of metric and overlapping terms (active/avilable/active certified -- a huge trap) ... Numbers should never go in memory. Define what is done for metric and its life (not lifecycle)", and asked: "Let us build and maintain approved vocabulary / taxonomy and end this mess?" (DevHub TSK-c1d9ba).

The same status word had been used for four different things: a candidate, a metric on the platform, a metric for one tenant, and the route by which metrics are produced. Counts were repeated from memory and from old documents as fact. The existing glossary (`docs/reference/glossary/README.md`) is an A to Z of nouns and holds no status word.

The Architect drafted the page from the records (the seven Foundation states of a Metric Contract version, the live state and status columns, the code that writes each state) and the operator shaped it over several readings the same day: certified means deployable to a tenant, and nothing is active before certification; the versions marked active without a certificate are a defect left by a governance deadlock (DEC-21ca17); his own six groups of a metric's life; the tenant words and the two tenant switches; and "released" after certified. Codex reviewed two earlier revisions (thread gen-6e2223) and is to check the approved page once more before it lands, as the grant allows.

## Decision

1. **One authority for status words.** `docs/reference/vocabulary.md` in bc-docs is the only authority for the status words used for metrics and tenants in documents, screens, memory, briefs and tool output. Where another document disagrees with it, the page wins and the other document is corrected.

2. **The first slice, as the operator approved it.** The page's first slice is the Architect page of barecount-devhub pull request 187 at commit 141b1af35366c92bf0468fdb074c112ca82b15a4, built on the operator's six groups of a metric's life:
   - (1) seed;
   - (2) candidate and the other seed statuses;
   - (3) registered;
   - (4) draft, in review, approved, awaiting certification, certified, released, certification blocked;
   - (5) superseded, retired, abandoned;
   - (6) for a tenant: available, subscribed, enabled or disabled, visible or hidden, reporting.

3. **The operator's answers on that page.** Available means released. When a release is reversed, the metric goes back to certified, and tenants that already have it enabled keep it. Both tenant switches, enabled or disabled and visible or hidden, belong to the tenant admin.

4. **The versions marked active without a certificate** are a defect, not a status, and are cleared by option 1 of the page's section 3a: their directory identities are minted, they are moved to awaiting certification, and they are certified only through the panel.

## Consequences

Each is a follow-up under its owner. None is done by this record.

- **The page:** `docs/reference/vocabulary.md` carries the approved text, with the operator's two answers stated in place of the questions. The Docs Controller maintains it.
- **The clean-up:** memory, CLAUDE.md files, briefs and documents are rewritten to these words, and counts in them are replaced by where to read them (the Chief's clean-up unit). The page's section 4 lists the words no longer used and what to say instead.
- **The glossary** stays as the A to Z of nouns and points to this page for status words (Docs Controller).
- **What the page names as not built** stays not built until each is designed and built under its own gates: the release record, the tenant admin's two switches, the subscription record, a record of "done", a recorded tenant kind, and the way out of certification blocked. Any schema change needs the operator's yes.
- **The defect of section 3a** is cleared by the route DEC-21ca17 already decided (DevHub TSK-fa743d, Metric Controller).
- **A check that can go red** on a status word not on the page, in documents and screen text, is design only on the page (section 7); building it is a later unit.

## Non-goals

No change to Foundation, to the seven state names, or to any enforced transition. No schema, code or route change. No decision on whether "retired" is reserved for legitimate withdrawals: the page names it as a design act for the operator. No change to ADR DEC-c220e4, whose wording on certified metrics would change only once release exists.

## References

- `docs/reference/vocabulary.md` (this record's page)
- barecount-devhub `artifacts/architect/VOCABULARY-first-slice-metric-words-2026-10-01.md` at commit 141b1af35366c92bf0468fdb074c112ca82b15a4 (pull request 187), the approved text
- DEC-c220e4, DEC-21ca17, DEC-fa9424, DEC-c48b0f, DEC-79b62f; `docs/foundation/the-contract-grammar.md`; `docs/operating-model/metric-lifecycle.md`; `docs/reference/lifecycle-map.md`
- DevHub TSK-c1d9ba, TSK-77b055, TSK-fa743d
