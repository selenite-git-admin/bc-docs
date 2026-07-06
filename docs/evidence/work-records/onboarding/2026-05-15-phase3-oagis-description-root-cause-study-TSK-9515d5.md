---
title: "Phase 3 OAGIS description root-cause study"
task: TSK-9515d5
date: 2026-05-15
status: study
type: rca
authority: DEC-a49413
related:
  - DEC-a49413   # §11 BF SDA-trust predicate; §12 BF semantic remediation
  - 2026-05-15-phase3-medium-bf-semantic-remediation-plan-TSK-9515d5.md
  - 2026-05-15-phase2-multi-high-bf-semantic-remediation-closeout-TSK-9515d5.md
---

# Phase 3 OAGIS Description Root-Cause Study (TSK-9515d5)

**Status:** read-only investigation; no remediation performed. Phase 3 apply **remains halted** pending operator decision on the remediation strategy proposed in §5.

**TL;DR.** Phase 3 is not "harder review" — it is structurally non-viable as currently framed:

- **All 462 Phase 3 BF definitions in the live DB are the literal string `"<bf_name> from OAGIS undefined"`.** Not blank, not real OAGIS text — every BF carries the same broken fallback template.
- **All 732 OAGIS field descriptions in the raw scrape are blank.** Phase 3 BFs cluster on shared, generic OAGIS components (`description`, `note`, `role`, `identifier`, `variation-identifier`) whose `title=""` on the OAGIS docs page.
- **The onboarding service has a one-line bug.** `oagis-onboarding.service.ts:201` falls back to `` `${field.bf_name} from OAGIS ${comp.name}` `` — but the seed schema does not carry `comp.name`. 210/210 sampled components show `comp.name === undefined`, so the fallback always produces `"... from OAGIS undefined"`.
- **Recoverable parent context exists in the local archive.** 592/732 candidates (81%) have a non-blank component-level description; 732/732 (100%) have a non-blank noun-level description. The data is there; the onboarding code referenced the wrong field name.

The Phase 3 packet's "0 PICK / 462 REVIEW" outcome was not the SOP being conservative — it was a faithful reflection of an upstream evidence gap. Proceeding with Phase 3 apply under the current SOP would write `standardRef` values for BFs whose definitions still contain the literal `"undefined"`. The §12 endpoint would accept this (the four §12 columns are independent of the definition column) but the audit trail would be permanently noisy. **Phase 3 should not run until the BF definition gap is closed.**

---

## 1. Authority and scope

| Authority | Reference |
|---|---|
| Decision | **DEC-a49413** §11 (BF SDA-trust predicate) and §12 (post-certify BF semantic remediation endpoint) — unchanged |
| Task | **TSK-9515d5** — Phase 3 investigation |
| Phase 3 SOP | [2026-05-15-phase3-medium-bf-semantic-remediation-plan-TSK-9515d5.md](2026-05-15-phase3-medium-bf-semantic-remediation-plan-TSK-9515d5.md) (commit `841d9f9`) |
| Phase 3 packet | `bc-core/scripts/audit-output/phase3-medium-selection-packet-seed-20260515.md` (commit `92b9341`) |
| Generator | `bc-core/scripts/build-phase3-medium-packet.mjs` (commit `92b9341`) |

Read-only. No DB writes, no remediation, no metric promotion, no apply. Evidence sources: PG `business_field`, Mongo `bc_seed.seed_oagis_components` + `seed_bo_crosswalk`, local raw scrape archive `barecount-devhub/data/oagis-finance-extract.json`, scraper `barecount-devhub/scripts/oagis-scraper.mjs`, onboarding service `bc-core/src/registry/oagis-onboarding.service.ts`.

---

## 2. Findings by question

### Q1 — Are Phase 3 OAGIS field descriptions truly blank in the raw scrape, or did Mongo / onboarding lose them?

**Truly blank at the source.** Quantified across all 732 MEDIUM candidates over the 462-BF Phase 3 cohort:

| Scrape evidence | Count |
|---|---:|
| Field slug not found in scrape | **0** |
| Field present, `description === ""` (blank) | **732** |
| Field present, `description` non-blank | **0** |

The scraper's regex (line 212, `oagis-scraper.mjs`) extracts `description` from the HTML `title="..."` attribute on each field link. The Phase 3 cohort points at OAGIS fields whose `title` attribute is empty in the rendered HTML — most commonly because the OAGIS authors did not add a tooltip on heavily-reused generic components (`description`, `note`, `role`, `identifier`, etc.). This is faithful capture, not a scraper defect.

Sample blank-description fields:

```
allocate_resource_dtl_description → allocate-resource-header#description
allocate_resource_dtl_description → allocate-resource-detail#description
allocate_resource_dtl_note        → allocate-resource-header#note
allocate_resource_dtl_note        → allocate-resource-detail#note
allocate_resource_hdr_description → allocate-resource-header#description
```

These are exactly the OAGIS fields one would expect: a generic `description` slot on a header component, a generic `note` slot, etc.

### Q2 — For blank scalar fields, does useful semantic text exist on parent surfaces?

**Yes, abundantly.** Quantified across all 732 candidates:

| Recoverable parent context | Count of candidates |
|---|---:|
| Component-level `description` non-blank | **592** (81%) |
| Noun-level `description` non-blank | **732** (100%) |
| Noun-level `display_name` present (global, 133 / 133) | **732** (100%) |

The component description is a human-authored OAGIS paragraph explaining what the parent component covers. Example: for `invoice-header`, the component description begins *"Information that applies to the entire invoice document. The Header supports summary amounts for line items, charges, taxes and allowances..."* The noun description is similar at a higher level.

A defensible synthetic BF definition can be built from `field.name` + `component.display_name` + `component.description` + `noun.display_name`. The local scrape archive carries all four; the Mongo seed carries all four.

### Q3 — Why did BF definitions become strings like `"description from OAGIS undefined"`?

**One-line bug in onboarding fallback path.** `bc-core/src/registry/oagis-onboarding.service.ts:201`:

```js
definition: field.description || `${field.bf_name} from OAGIS ${comp.name}`,
```

When `field.description` is empty (Phase 3 cohort condition by §Q1), the JS short-circuit evaluates the template literal. The template reads `comp.name`. **The seed schema does not carry `comp.name`.** The Mongo `seed_oagis_components` documents look like:

```json
{
  "slug": "invoice-header",
  "display_name": "Invoice Header",
  "description": "Information that applies to the entire invoice document...",
  "source_url": "https://www.oagidocs.org/docs/invoice-header",
  "fields": [...]
}
```

No `name` field. Verified by sampling 158 nouns / 210 components from the seed: **210 / 210 components have `comp.name === undefined`**. The scraper writes `slug`, `display_name`, `description`, `source_url`, `field_count`, `component_count`, `fields` — never `name`. The onboarding code referenced a field that was never produced by the upstream scraper.

`comp.name` evaluates to `undefined`; JavaScript template-literal coercion produces the string `"undefined"`; the BF definition becomes `"<bf_name> from OAGIS undefined"`.

The same line of code (199–201) is the **only path** by which a fallback definition can land in `business_field.definition` for OAGIS-onboarded BFs. There is also a sibling fallback at line 301 for BO definitions that uses `comp.description || noun.description || \`${boName} business object from OAGIS\`` — which correctly falls back through real fields. The BF-level fallback should follow the same pattern.

### Q4 — How many Phase 3 rows are affected by each pattern?

| Pattern | Count |
|---|---:|
| BF definition is the literal `"<X> from OAGIS undefined"` | **462 / 462** |
| BF definition contains the literal substring `"undefined"` | **462 / 462** |
| OAGIS source description (any MEDIUM candidate) blank | **732 / 732 candidates across 462 BFs** |
| Phase 3 BFs with multiple MEDIUM candidates | **249 / 462 (~54%)** |
| Phase 3 BFs with single MEDIUM candidate | **213 / 462 (~46%)** |

**Top properties in the Phase 3 cohort:**

| property | count | type of OAGIS field |
|---|---:|---|
| `description` | 168 | generic text slot reused across components |
| `note` | 158 | generic note slot |
| `variation_identifier` | 82 | identifier on variant lines |
| `ccrid` / `gtinid` / `role` | 6 each | small reusable identifiers / roles |
| various `*_date_time` | 2–3 each | timestamps where source OAGIS field has no tooltip |

These are precisely the shared, generic OAGIS slots — the cohort isn't a random sample of legacy BFs; it's a tight cluster of "the OAGIS components that don't carry tooltip descriptions."

### Q5 — Can we derive a defensible enriched BF definition from local OAGIS evidence?

**Yes, for 100% of Phase 3 BFs**, using a defined synthesis rule against fields the local seed already carries. Proposed synthetic-definition template (operator-confirmable, not yet implemented):

```
`${field.name} on ${component.display_name} — ${component.description.slice(0, 240)} (OAGIS noun: ${noun.display_name})`
```

Worked example for `allocate_resource_hdr_description` → OAGIS `allocate-resource-header#description`:

> `"Description on Allocate Resource Header — Information common across the resource allocation request, including identifiers and timestamps for the allocation event (OAGIS noun: Allocate Resource)."`

The definition is fully traceable to local seed fields (component `display_name`, component `description`, noun `display_name`), carries real semantic content, and is byte-identical to a synthesizable template that can be re-derived deterministically at audit time. **It is NOT operator-authored prose — it is a structured projection of authoritative seed text.**

For the remaining 19% (140 / 732 candidates) whose **component description is blank**, the synthesis falls back to noun-level context, which is universal. The text loses specificity but remains traceable.

This is preferable to the current state (`"description from OAGIS undefined"` × 462) by every conceivable axis: traceability, semantic content, audit cleanliness, and downstream model behaviour (the LLM-based dedup gate at `callBfDedup` would never have to reason about the literal `"undefined"`).

### Q6 — Should Phase 3 be split into sub-phases?

**Yes — three sub-phases recommended.**

| Sub-phase | Cohort | Rationale |
|---|---|---|
| **3a — definition backfill** | All 462 BFs | Replace `"... from OAGIS undefined"` with the synthetic template from §Q5. **Not a §12 remediation.** This is a BF `definition` column update, not a `standard_ref` write. Needs a separate governed write path (see §7 below). |
| **3b — §12 remediation, single-MEDIUM** | 213 single-MEDIUM rows | After 3a backfills definitions, these rows have a real BF definition + one MEDIUM candidate. Operator review burden lower because there's no disambiguation. AI heuristic relaxes to "single-MEDIUM-NS + scrape-corroborated + frozen-table-valid → PICK" since the property-in-description check is unhelpful when source descriptions are blank. |
| **3c — §12 remediation, multi-MEDIUM** | 249 multi-MEDIUM rows | After 3a + Phase 2 R1/R3/R4/R5 secondary heuristics, expect a substantial AI-PICK rate (header vs line vs detail vs item disambiguation). Residual REVIEW rows go to operator manual selection. |

Sequencing must be 3a → 3b → 3c. Without 3a, 3b and 3c would write `standard_ref` against BFs whose definitions contain `"undefined"`.

### Q7 — Is there a bug in the scraper or seed schema that should be fixed before continuing?

**Two bugs identified, neither in the scraper:**

1. **Onboarding fallback references a non-existent seed field.** `oagis-onboarding.service.ts:201` reads `comp.name`. The seed schema does not provide it. Either:
   - **(a)** Patch the fallback to read `comp.display_name || comp.slug` and walk to noun fallback (`|| noun.display_name`) before settling on the generic OAGIS string. This is the minimum fix.
   - **(b)** Patch the fallback to use the synthetic-template form from §Q5, producing structured definitions that are useful in their own right, not just placeholders.

   Recommend **(b)** — it makes the fallback semantically valuable rather than a sentinel.

2. **Suggestion scorer treats blank-vs-blank as `descriptionMatch=true`.** Not strictly a bug, but a latent fragility. `suggestForBf` in `standard-field.service.ts` and the packet generators all use:

   ```js
   const descriptionMatch = definition.length > 0 && fieldDescription === definition;
   ```

   This is correct **as long as the `definition.length > 0` guard stays in place** — two blank strings will not produce a false-positive description match. Worth pinning in a code comment that this guard must not be removed when refactoring. Phase 3 found no blank-blank false positives because the BF definitions are populated (with the broken fallback text). After 3a backfills, both sides remain non-blank in practice, but the guard is the safety net.

The **scraper is correct** — it faithfully captures the empty title attribute as `description: ""`. No change recommended there.

The **seed schema is correct** — it persists what the scraper produced. No change recommended.

---

## 3. Root cause

The Phase 3 evidence gap has two independent root causes, both upstream of the §12 contract and entirely unrelated to TSK-9515d5's Phase 1/2 mechanism:

1. **OAGIS source HTML carries no tooltip descriptions for shared generic components** (`description`, `note`, `identifier`, `role` slots). This is an OAGIS authoring choice, not a defect. Scrape is correct; seed is correct.

2. **Onboarding fallback bug** (`oagis-onboarding.service.ts:201`) produces the literal string `"undefined"` in BF definitions when both `field.description` and `comp.name` are absent. This is the deterministic outcome of the JS short-circuit + template-literal coercion when the referenced seed field doesn't exist. All 462 Phase 3 BFs were onboarded through this path and carry the same broken text.

The two together produce the observed state: 462 BFs that look like they need MEDIUM-grade semantic disambiguation but actually need their definitions fixed first.

---

## 4. Recommended remediation strategy

**Halt Phase 3 §12 apply.** Do not proceed with any of the 462 Phase 3 BFs under the current SOP. The Phase 3 SOP commit `841d9f9` and the packet commit `92b9341` remain as-is for historical record; both correctly classified the rows as REVIEW under the SOP's restricted heuristic. No SOP rollback needed.

**Author a Phase 3a sub-SOP for BF definition backfill.** Scope:

- Target: 462 BFs whose `business_field.definition` matches the regex `^\S+ from OAGIS undefined$`.
- Action: replace the definition column with the synthetic-template form from §Q5. **No `standard_ref` or other §12 column writes.**
- Endpoint: requires a new governed write path (see §6 below) — the §12 endpoint deliberately does not touch the `definition` column.
- QA: pre-apply 30-row review of the synthetic templates; final 50-row acceptance sample; same ≥49/50 threshold as Phase 1/2.
- Drift guard: same shape; refuse on cohort expansion; tolerate shrinkage.

**Author a Phase 3b sub-SOP** for §12 remediation of the 213 single-MEDIUM rows after 3a backfill. Relax the AI heuristic to `single-MEDIUM-NS + scrape-corroborated + frozen-table-valid → PICK` (drop the property-in-description check, which is structurally useless for blank-description sources).

**Author a Phase 3c sub-SOP** for §12 remediation of the 249 multi-MEDIUM rows after 3a. Reuse Phase 2's secondary heuristics R1/R3/R4/R5 directly.

If operator capacity is constrained, **3a is the only one of the three that is strictly required before any §12 progress.** 3b and 3c can be deferred indefinitely; the trade-off is just slower coverage growth.

---

## 5. Whether Phase 3 apply should remain halted

**Yes — halt confirmed.** Two reasons:

1. **Audit-trail integrity.** Writing `standard_ref` against a BF whose `definition` contains the literal `"undefined"` would create a permanent record in `contract.certification_record` (action_code=`remediate_bf_semantics`) where the BF being remediated has nonsensical text. Future operators (and AI agents) reading the audit trail would have to know about this study to understand why the trust evidence is paired with broken definitions. That is fragile.

2. **Downstream model behaviour.** The bc-ai dedup pipeline (when it runs) reads `bf.definition` as one of its primary inputs. Reasoning over the literal `"undefined"` is at best wasted compute and at worst produces misleading dedup verdicts.

A clean fix to BF definitions is cheap (synthetic template, all data local, deterministic) and produces a much better audit posture for the eventual Phase 3b / 3c §12 remediation.

---

## 6. Proposed future DBCP / ADR / SOP / code changes

### Code (bc-core, single commit recommended)

- **Patch `oagis-onboarding.service.ts:201`.** Change the BF definition fallback from `` `${field.bf_name} from OAGIS ${comp.name}` `` to the synthetic-template form. Also patch the BO-level fallback at line 301 for consistency, even though it already walks to noun.
- **Add a one-line guard comment** in `suggestForBf` (the description-match guard) noting that the `definition.length > 0` check must stay to prevent blank-vs-blank false positives.

### Read-only verification script (uncommitted; for the Phase 3a SOP review packet)

- A read-only tool that loads the 462 broken BFs, computes the proposed synthetic definitions from local seed data, emits a Markdown review packet identical in shape to the Phase 2 disambiguation packet. **Read-only.** Writes happen in 3a apply via the new governed endpoint.

### New governed write path (the only DBCP-level change required)

The §12 endpoint writes only the four SDA-binding columns. Patching BF `definition` requires a new endpoint or a new action_code. Two options:

- **DBCP-1q-A — new action_code `remediate_bf_definition`.** Extends `certification_record.action_code` CHECK constraint. New service method `remediateBfDefinition(fieldId, { definition }, certifier)`. Atomic UPDATE of one column + INSERT of one cert_record row. No §12 columns touched; no state transition. Mirrors §12 in shape, distinct in scope.
- **DBCP-1q-B — overload `remediate_bf_semantics` to optionally accept `definition`.** Smaller surface change, but mixes two concerns (definition vs SDA-binding columns) into one action. Audit trail loses signal.

**Recommend DBCP-1q-A** — distinct action_code, distinct service method, distinct SOP. Clean audit signal for the 462 row backfill. The Phase 3a SOP would reference this DBCP.

### SOPs

- **Phase 3a SOP** — BF definition backfill (synthetic template, 462 rows, ≥49/50 threshold, drift-guard same shape as Phase 1/2).
- **Phase 3b SOP** — §12 remediation, single-MEDIUM, 213 rows, relaxed AI heuristic.
- **Phase 3c SOP** — §12 remediation, multi-MEDIUM, 249 rows, Phase 2 secondary heuristics.

All three are sibling work-records under `_cross/`; none is an ADR amendment.

### No ADR changes

DEC-a49413's §11 + §12 invariants are unchanged. The BF definition is not a §12 concern. DEC-a17d0f (SDA umbrella) is unchanged.

---

## 7. Recommendation

Halt Phase 3 §12 apply until **DBCP-1q-A + the onboarding fallback fix + the Phase 3a SOP** are filed and approved. The work to close Phase 3a is small (deterministic synthesis from local seed; no AI authoring needed). After 3a closes, Phase 3b and Phase 3c are routine §12 work using already-built infrastructure.

In the meantime, the Phase 3 packet (`92b9341`) and SOP (`841d9f9`) remain as filed; they are correct under their own terms. This study supersedes the implicit assumption that Phase 3 §12 apply could proceed against the current cohort.

---

## 8. Cross-references

- `bc-docs-v3/docs/adrs/ADR-a49413.md` §11, §12 (unchanged)
- `bc-core/src/registry/oagis-onboarding.service.ts` line 201 (BF definition fallback bug)
- `bc-core/src/registry/oagis-onboarding.service.ts` line 301 (BO definition fallback — correct shape, reference template)
- `bc-core/src/registry/standard-field.service.ts` `suggestForBf` (description-match guard — must stay)
- `barecount-devhub/scripts/oagis-scraper.mjs` line 212 (regex extracts `description` from HTML `title` attribute — correct as-is)
- `barecount-devhub/data/oagis-finance-extract.json` (raw scrape archive; 133 nouns, 158 components, scraped 2026-04-06)
- Phase 3 SOP: `2026-05-15-phase3-medium-bf-semantic-remediation-plan-TSK-9515d5.md`
- Phase 3 packet: `bc-core/scripts/audit-output/phase3-medium-selection-packet-seed-20260515.md` (commit `92b9341`)
- Phase 2 closeout: `2026-05-15-phase2-multi-high-bf-semantic-remediation-closeout-TSK-9515d5.md` (commit `3e5d507`)

---

## Addendum (2026-05-15, post-operator-challenge)

**The body of this study claimed OAGIS source descriptions are "truly blank at the source" (§Q1). That claim is wrong. Corrected below.**

The operator pushed back on the assertion that OAGIS would have empty fields. A re-scan of the scrape archive disproves the original framing:

| Scrape coverage (global, not just Phase 3) | Count |
|---|---:|
| Total fields across all 133 nouns + 25 shared components | **6,131** |
| Fields with non-blank description | **4,833** (79%) |
| Fields with blank description | **1,298** (21%) |

The scraper DOES capture descriptions for the majority of OAGIS fields. The blank 21% cluster on a small set of slugs:

| Blank slug | Occurrences |
|---|---:|
| `description` | 177 |
| `note` | 166 |
| `type-code` | 148 |
| `variation-identifier` | 88 |
| `net-volume-measure` | 14 |
| `debit-credit-code` | 12 |
| `gtinid` | 8 |
| `role` | 6 |
| `ccrid` | 6 |
| `agency-name` | 5 |
| … (38 more slugs) | … |

**48 distinct blank slugs in total, none of which are visited by the scraper as a standalone noun or shared component.** These are atomic CCTS (Core Components Type Specification) data types — OAGIS's bottom-of-the-stack reusable elements. OAGIS does document them, but at a layer the scraper does not crawl: each atomic type lives on its own `/docs/<slug>` page (or in the OAGIS CCTS XSD schemas), not embedded as a `title=""` attribute on the parent component's field link.

### Corrected root cause

There are now **three** independent issues, not two:

1. **OAGIS source HTML does carry descriptions for these fields — at a different URL layer the scraper does not visit.** OAGIS authoring is fine. The Phase 3 cohort is not "fields OAGIS forgot to describe"; it is "fields the scraper didn't crawl deeply enough."
2. **Onboarding fallback bug** (`oagis-onboarding.service.ts:201`, `comp.name` does not exist in seed schema) — still real, still produces the literal `"undefined"`.
3. **Scraper coverage gap** — the script iterates a fixed list of nouns + 25 hardcoded shared components. It does not attempt `https://www.oagidocs.org/docs/<field-slug>` for atomic types like `description`, `note`, `type-code`, `variation-identifier`, etc. The 48 distinct blank-description slugs map to standalone OAGIS docs pages that were never fetched.

### Implications for remediation strategy

The §5 recommendation in the body ("synthetic template from parent component context") was a workaround for a problem that has a cleaner upstream fix. The corrected sequence:

1. **Extend the scraper** to attempt a fetch of `https://www.oagidocs.org/docs/<slug>` for each scalar field whose `title=""` is blank in the parent component. Capture the standalone page's description (or noun-level description if the page itself is a noun). This is a one-time scraper run and uses the same regex + parser infrastructure; the change is the discovery list expansion.
2. **Re-load the seed** from the enriched scrape archive.
3. **Re-run `oagis-onboarding.service.ts`** for the 462 affected BFs to refresh their definitions from real source text. This still needs the new `remediate_bf_definition` governed write path (DBCP-1q-A from the body of this study) because the BFs are already certified; the existing onboarding code only writes definitions on initial create, not on a re-onboard.
4. **Patch the onboarding fallback bug** (line 201) anyway, for future BFs that hit a genuinely-blank source even after scraper extension.
5. **Then re-evaluate Phase 3.** With real OAGIS descriptions populated in `bf.definition`, the §11 suggestion service's `descriptionMatch` signal would activate for many of the 462 rows, promoting them from MEDIUM-NS to HIGH (and into Phase 2's already-closed remit) or to MEDIUM-D (operator-confirmable easy PICK).

### What changes vs the body recommendation

- **§Q1 claim is wrong.** OAGIS field descriptions are not truly blank at the source.
- **§4 strategy still works**, but the synthetic template is now the *fallback* for fields that remain blank after a scraper extension, not the primary remediation. Most of the 462 cohort can be cleanly enriched from real OAGIS text once the scraper visits the right URLs.
- **§6 proposes a new code change first** — extend the scraper. Estimated cost: one afternoon of work plus a new full crawl. The 48 atomic-type slugs are a small finite set; the extension is mechanical.
- **DBCP-1q-A is still required** to back-fill the 462 existing BF definitions; the onboarding code path only fires on initial create.

### Recommended next sequence (revised)

1. **One scraper extension commit** — for each blank-description scalar field, attempt to fetch `/docs/<slug>` and capture the standalone-page description. Re-run the full crawl. Compare blank-count before vs after.
2. **One Mongo re-load** from the enriched scrape archive (deterministic, replaces seed_oagis_components atomically).
3. **DBCP-1q-A** — new `action_code='remediate_bf_definition'` on `certification_record`. Governed endpoint that updates one column + writes one cert_record row.
4. **Phase 3a SOP** — BF definition backfill using the enriched seed (not the synthetic template). Operator-confirmable per row.
5. **Re-evaluate Phase 3 cohort** after 3a. Many BFs should reclassify out of Phase 3 entirely once their definitions are real.

### Halt status unchanged

Phase 3 §12 apply remains halted. The reason changes from "evidence gap at source" to "BF definitions are bug-shaped and need real text from a deeper scrape." Outcome is the same: do not write §12 columns against BFs whose `definition` contains `"undefined"`.

### Acknowledgement

The original §Q1 framing was a careless conclusion drawn from "scrape shows blank → OAGIS source must be blank." The operator caught this. The corrected framing — scraper coverage gap — is testable and actionable. Apology noted; the original body is left intact rather than rewritten so the path-of-error is preserved in the audit trail.

---

## Addendum 2 (2026-05-16, post-empirical-test — side-task SES-03f268)

**Addendum 1's premise was also wrong. Tested empirically; corrected below.**

Addendum 1 claimed the 21% blank-description cohort would be resolved by extending the scraper to fetch `https://www.oagidocs.org/docs/<slug>` for each blank atomic-type slug — i.e. "scraper coverage gap, fix by deeper crawl." The side-task implemented this (commit pending; enriched archive at `barecount-devhub/data/oagis-finance-extract-enriched-2026-05-15.json`) and the empirical result disproves the premise.

### What the scrape actually recovered

| Metric | Value |
|---|---:|
| Finance-archive scalar fields | 3,261 |
| Blank descriptions before enrichment | 773 |
| Unique blank slugs (atomic CCTS types) | 55 |
| Slugs resolved by `/docs/<slug>` fetch | 55 / 55 (100%) |
| **Distinct recovered text templates** | **2** |

All 773 recovered descriptions reduce to two boilerplate texts. 53 slugs share the primitive-type template ("This data type is based on the following data type primitives. String NormalizedString Token…"); 2 slugs (`debit-credit-code`, `time-zone-code`) share a code-list-values template. **Zero of the 55 standalone pages carry field-semantic prose.**

### Why this is structural, not a parser bug

OAGIS docs at `oagidocs.org` follow the UN/CEFACT **Core Components Technical Specification (CCTS)** three-layer model:

| Layer | URL pattern | What it documents |
|---|---|---|
| **L1 — Noun / component page** | `/docs/invoice-header` | Business-purpose text for the parent component (BIE root). Real semantics. Already captured (4,833 / 6,131 fields). |
| **L2 — Field-link tooltip on the L1 page** | `title=""` on each `<a>` to a typed field | True per-BIE field semantics, **when OAGIS authors wrote one.** Blank for ~21% of fields by deliberate authoring choice — generic slots (`description`, `note`, `code`, `identifier`) inherit from the type page. |
| **L3 — Atomic CCTS type page** | `/docs/description`, `/docs/debit-credit-code` | **Data-type definition only.** H1 = type name; H2s = "Data Type Description", "Supplementary Components", "Feedback". No "Usage" or "BIE Semantics" section. Body lists primitives (String/Token/NormalizedString) or code-list values. |

OAGIS deliberately separates **Core Data Types (context-free, reusable)** from **Business Information Entities (context-specific, defined by composition)**. Per-BIE prose — what `invoice-header#description` means as distinct from `payable-line#description` — is **not authored on oagidocs.org**. Where it exists at all, it lives in the OAGIS release ZIP's XSD `<xsd:annotation><xsd:documentation>` blocks, and even there is frequently absent for trivially-named slots.

The L3 standalone pages therefore cannot supply field-purpose text for these slugs. The information is not present. This is not a scrape bug, a crawl-depth bug, or a temporal drift bug. **It is OAGIS authoring philosophy: type-layer documentation is canonical; BIE-layer per-field prose is implicit from "type identity + parent component."**

### Corrected root cause (final, three issues)

1. **L2 tooltips are blank for ~21% of fields by OAGIS authoring choice.** Faithful capture. No upstream fix available from oagidocs.org.
2. **Onboarding fallback bug** at `oagis-onboarding.service.ts:201` (`comp.name` does not exist in seed) — produces literal `"undefined"` whenever L2 is blank. **Patched in this side-task** to walk `comp.display_name ?? comp.title ?? comp.slug` + noun fallback. Side-task commit (TBD).
3. **L3 standalone CCTS type pages do not contain field-semantic text.** Empirically confirmed by the enriched-archive scrape. The §Q5 synthetic-template approach from the body of this study is the right path; the L3 scrape is not.

### Revised remediation strategy

The body's §Q5 synthetic-template approach is **restored as the canonical path** for Phase 3a, drawing on data already in the local archive (no further fetches needed):

- `field.name` / `field.bf_name`
- `component.display_name` / `component.title` / `component.slug`
- `component.description` (parent BIE prose — 81% non-blank)
- `noun.display_name` / `noun.noun`
- `standardRef` continues to point at the BIE URL: `${component.source_url}#${field.slug}`

The Phase 3a SOP MUST explicitly label the resulting definition text as **BareCount-authored from OAGIS structural context, not scraped OAGIS prose.** This is non-negotiable for audit-trail honesty: the text is a deterministic projection of OAGIS structural metadata, not OAGIS-authored prose.

### Open policy question (deferred to operator)

Once the synthetic template lands as canonical BF definitions, the `business_field.definition_standard` column needs a policy decision:

- **(P-OAGIS)** Keep `definition_standard='OAGIS'`. Rationale: text is fully traceable to OAGIS structural metadata (component+noun+CDT identity); `standardRef` points at the OAGIS BIE URL. Risk: future readers may interpret the BF as carrying OAGIS-authored prose, which it does not.
- **(P-BARECOUNT)** Switch to `definition_standard='BARECOUNT'` with `standardRef` retained for provenance. Rationale: prose authorship is BareCount's, not OAGIS's; cleanest audit posture. Risk: downstream filters that count "OAGIS-standard BFs" will see ~462 BFs drop out of that cohort; semantically still OAGIS-aligned via `standardRef`.

DBCP-1q-A is blocked on this decision. The new `action_code='remediate_bf_definition'` shape is uncontroversial; the question is what value of `definition_standard` the remediated rows should carry, which determines the service-method signature and the SOP wording.

### What this side-task did and did not produce

| Done | Not done (held) |
|---|---|
| L3 scraper extension (enrich-only mode), to permit empirical test | Mongo seed reload from L3-enriched JSON (operator: do not reload) |
| L3-enriched JSON committed as RCA evidence | Phase 3 §12 apply (remains halted) |
| Onboarding fallback patched (`comp.name` → `comp.display_name`/`title`/`slug` + noun fallback) | DBCP-1q-A authored (blocked on definition_standard policy) |
| This addendum filed | Phase 3a SOP filed (blocked on synthetic-template wording + definition_standard policy) |

### Halt status

Phase 3 §12 apply remains halted. Reason now: BF definitions need synthetic-template backfill via DBCP-1q-A, which is blocked on the definition_standard policy decision above. L1/L2 capture is sufficient input for the synthetic template (no further OAGIS fetches required).
