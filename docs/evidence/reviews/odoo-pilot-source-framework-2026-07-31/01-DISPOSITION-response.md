# Disposition Record — Odoo Pilot Review (Codex)

**Outcome: ACCEPTED WITH BOUNDARY** (design accepted; execution gated; no build authorized).
**Reviewed artifact:** `bc-docs@f38a5882322a80aa7071dca3f91fdd44aabb3f17` cover
`.../00-REVIEW-PACKAGE.md`. **`bc-pilot` @ `9f1cc8c`.**
**Cover SHA-256 (Codex-claimed):** `3be7d70af27152c452bae9796a25fbe73934ff9e2c349b9113a5134901e68465`
**— independently VERIFIED 2026-07-31** (`git cat-file blob` and `git show` both hash to this;
so the disposition binds to the exact reviewed content).

## Verdict summary
6 VERIFIED (2×@4, 4×@5 where 5s are the doctrine/code-checked items) · 3 QUALIFIED (@4) ·
0 CONTRADICTED · 0 NOT_PROVEN. Codex inspected bc-core first-hand (reader interface,
canonical-resolution.service, ccv2 resolver, metric-variable binding/resolver, source
catalog, platform library) plus the pinned bc-docs + bc-pilot artifacts. Read-only; no
gates/tests/DB/PR mutations run.

## Obligations carried forward (what "with boundary" binds us to)

**GATING (block the named unit):**
- **G1 — Phase 1 gate transcripts.** The clean rebuild must **publish actual gate
  transcripts + AMI evidence before build sign-off / AMI reliance** (gate-battery QUALIFIED).
  → the next gated unit. Tracked.
- **G2 — Console DBCP + drift.** Present the `platform.pilot_profile` **DBCP before any
  table/endpoint build**; resolve the `library_status`/API status **naming drift** in
  implementation (console QUALIFIED). Already in D §6. Tracked.
- **G3 — Reader serializer.** Build the ORM domain serializer **hardened, with negative
  tests for nested domain/field-list flattening; no writes from the executor** (serializer
  QUALIFIED). Reader §4 impl is a later gated unit. Tracked.

**STANDING (doctrine to preserve, no new work):**
- Keep "**source richness ≠ metric realization**"; keep Tier-2 modules demand-gated (VERIFIED 4).
- Preserve the "**backdated books / forward-only behavioral (CRM-velocity)**" limit in every
  consumer-facing doc where pilot evidence is shown (VERIFIED 4).
- Future BC/SFDC realizations stay under `systems/<vendor>` **without moving the profile SSOT** (VERIFIED 4).
- **Do not claim direct no-company rejection** — fiscal-calendar gate is the real fail-closed
  path; a hard no-company rule is new work only if separately authorized (VERIFIED 5).
- Keep the **MC source-column-free**; the BC zero-edit portability proof is a later Track-C
  unit (VERIFIED 5).
- **Sequencing:** AR/AP totals may proceed after reader/SC/AC gates; **GL-classification
  metrics wait on D515/D498 runtime wiring** (`classify_by_binding`/`fiscal_period_end_date`
  unwired) (VERIFIED 5).
- Keep source-world projection **out of the intrinsic audit evidence and PASS/REJECT** (audit
  independence, VERIFIED 4).

## Hard exclusions still in force (Codex)
No build authorization · no SC/AC/OC/CC/MC authoring over Odoo · no live/source execution ·
no platform mutation · intrinsic metric audit remains SAP ECC.

## Next gated unit (Codex-stated)
**Phase 1 clean rebuild → gate transcripts + AMI evidence**, then **Phase 2 Source Catalog
registration DBCP**. Reader §4 implementation is a later gated unit; chain §5 is Track-C only.

## Full ledger
See the disposition ledger table in the package cover §5 (living copy in
`REVIEW-PACKAGE-odoo-pilot-2026-07-31.md`), populated from this disposition.
