---
title: "DevHub Decision-Registration Integrity Repair — Closeout"
description: "Closeout for the good-faith preservation-first repair pass on ADR/decision-registry drift surfaced by the 2026-06-22 audit. Records every action taken, every documented exception, and confirms no content was lost or files were deleted."
date: 2026-06-22
project: bc-docs
domain: governance
subdomain: adr-registry
focus: governance
authority: reference
---

# DevHub Decision-Registration Integrity Repair — Closeout (2026-06-22)

## Scope and posture

This closeout records the good-faith repair pass that followed the [Decision-Registration Integrity Audit](../../audits/implementation/devhub-decision-registration-integrity-audit-2026-06-22.md). The repair operated under the operator's primary principle: **no ADR doctrine is lost; preservation always wins over delete + recreate.**

The repair used `devhub_decision_update` (status reconciliation only, since the tool cannot edit title or file_path), file frontmatter additions, and body notice insertions. The repair did **not** use `devhub_decision_record` (which would mint a new UID and create a new file) and did **not** use direct SQL.

## Tool inventory

| Tool | Used? | Notes |
|---|---|---|
| `devhub_decision_record` | **No** | Would have minted new UIDs and created new ADR files. Operator hard stop: "If a tool tries to mint a new UID when the intent is only to register an existing file, stop for that item and choose a preservation-safe alternative." Every FILE_ONLY_UNEXPLAINED case was preserved as a file-side authority exception with a frontmatter note + body notice instead. |
| `devhub_decision_update` | Yes — 1× pre-patch + 3× post-patch | **Tool extended mid-session.** Pre-patch: exposed only status / rationale_text / subdomain_text / focus_text — used once for the DEC-03db11 status reconciliation. Operator authorized a follow-up patch adding `title_text` / `file_path` / `description_text` as optional updatable fields (see §10 below). Post-patch: used 3× for the PATH_MISMATCH repairs (DEC-9d1f4b, DEC-4a8abb, DEC-c0290f). All four calls were preservation-safe — only optional fields explicitly passed, no existing field overwritten without operator-supplied value. |
| `devhub_doc_scan` | Yes — once | Refreshed the doc-registry index after the file-side edits. Result: 868 files scanned, 3 added (this closeout + the audit doc + one earlier file), 1 updated. |
| Direct SQL / DB write | **No** | The PATH_MISMATCH repairs originally appeared to require direct SQL because the unpatched `devhub_decision_update` did not expose title / file_path. Operator authorized a tool-layer patch instead (§10); the three repairs then ran through the supported API path. Hard stop honoured — no direct SQL was used. |
| `Edit` (file frontmatter + body notices) | Yes — 11 files | All edits add a `devhub_registration:` frontmatter field and/or a body notice block at the top of the body, after the title heading. No historical body content was modified. |
| `Write` (new files) | Yes — closeout doc only | This file. The audit doc was created in the previous turn. No ADR files were created. |
| `adr-audit.js` patch | **Deferred** | Patch is non-trivial — would require connecting to the decision registry or persisting registry snapshots. Operator condition for inclusion was "small and obviously reports these drift classes." Deferred to a follow-up. Detail in §9 of this closeout. |
| File deletion / rename | **No** | Operator hard stop honoured. The single `DUPLICATE_DECISION` file (`ADR-DEC-e82f0a.md`) was quarantined by frontmatter / body notice, not removed or renamed. |

## Repairs completed — item by item

### Item 1 — `DEC-7a1c98` (DOCUMENTED_SUPERSEDED_FILE_ONLY)

| Field | Value |
|---|---|
| Original state | File `ADR-7a1c98.md`: `status: superseded`, `superseded_by: DEC-54f221`, body supersession notice present. No decision-registry row. Doc-registry indexed as `DOC-4ccba8`. |
| Repair | **None — already resolved.** Per operator instruction: "do not re-register it or re-mint it." |
| Tool used | None |
| Post-repair verification | File frontmatter unchanged. Cross-references in audit + closeout point here. |
| Residual risk | None — this is the documented exception that triggered the audit. |

### Item 2 — `DEC-9a5dc0` (FILE_ONLY_UNEXPLAINED)

| Field | Value |
|---|---|
| Original state | File `ADR-9a5dc0.md`: full ADR for D302 (CF Boundary — Reporting Standards Promote to Canonical Fields), `status: decided`. No registry row. Referenced as live D302 by `ADR-chain-invariants.md` and `ADR-cbc07b.md`. |
| Repair | Added `devhub_registration:` frontmatter field + body notice block at top, classifying as `FILE_ONLY_UNEXPLAINED` with preservation justification and cross-link to audit + closeout. |
| Tool used | `Edit` |
| Post-repair verification | File frontmatter shows the new `devhub_registration:` field; body notice precedes `## Context`. No body content modified. |
| Residual risk | Registry row still absent — would require `devhub_decision_record` (mints new UID, breaks cross-references) or direct DB write (out of scope). Documented as preservation-safe exception. |

### Item 3 — `DEC-cbc07b` (FILE_ONLY_UNEXPLAINED + PATH_MISMATCH context)

| Field | Value |
|---|---|
| Original state | File `ADR-cbc07b.md`: full ADR for D331 (Type Conformance Enforcement), `status: proposed`. No registry row under DEC-cbc07b. The registry row `DEC-4a8abb` carries the same title and `file_path: docs/adrs/ADR-cbc07b.md` — the registry tracks this doctrine under the wrong UID. |
| Repair | Added `devhub_registration:` frontmatter field + body notice block at top, classifying as `FILE_ONLY_UNEXPLAINED` paired with the PATH_MISMATCH on `DEC-4a8abb`. Notes the registry's misalignment and that title/file_path correction is out of tool scope. |
| Tool used | `Edit` |
| Post-repair verification | File frontmatter shows new field; body notice in place. |
| Residual risk | Title/file_path correction on `DEC-4a8abb` registry row still needs operator action (direct DB write or future tool extension). |

### Item 4 — `DEC-e8a4d2` (FILE_ONLY_UNEXPLAINED + DUPLICATE_CONTENT_RISK with `DEC-224f7a`)

| Field | Value |
|---|---|
| Original state | File `ADR-e8a4d2.md`: full ADR for "Definition is the canonical parent…", `status: implemented`. Registry has the equivalent row under `DEC-224f7a` whose `file_path` already points at `ADR-e8a4d2.md`. |
| Repair | Added `devhub_registration:` frontmatter + body notice. Both surfaces document the dual-UID situation; file-side UID `DEC-e8a4d2` chosen as authority for inbound cross-references. |
| Tool used | `Edit` |
| Post-repair verification | File frontmatter and body show explicit cross-link to `DEC-224f7a` registry row. |
| Residual risk | Registry row `DEC-224f7a` still tracks the same doctrine under a different UID — operator decides whether to (a) leave both, (b) collapse by renaming the registry UID (direct DB write, out of scope), or (c) accept indefinitely. |

### Item 5 — `DEC-d315ve` (UID_FORMAT_NON_CANONICAL + FILE_ONLY_UNEXPLAINED)

| Field | Value |
|---|---|
| Original state | File `ADR-d315ve.md`: D315 — Metric Evaluation Verification Framework, `status: decided`. UID short form `d315ve` not 6 hex chars; allocator regex `[0-9a-f]{6}` cannot accept it. |
| Repair | Added `devhub_registration:` frontmatter + body notice classifying as historical file-side exception. Preservation over forced rename / successor minting per operator doctrine. |
| Tool used | `Edit` |
| Post-repair verification | File frontmatter and body explicitly call out the non-canonical UID. |
| Residual risk | UID can never be registered under the current allocator. Inbound cross-references use the non-canonical UID. To formalize, operator would mint a canonical successor and supersede this file; that path is documented in the notice but not executed. |

### Item 6 — `DEC-d316mr` (UID_FORMAT_NON_CANONICAL + FILE_ONLY_UNEXPLAINED)

Same pattern as Item 5; symmetric repair via `Edit` (frontmatter + body notice). Same residual risk.

### Item 7 — `DEC-224f7a` (REGISTRY_ONLY + DUPLICATE_CONTENT_RISK)

| Field | Value |
|---|---|
| Original state | Registry row `DEC-224f7a` (`status: implemented`, title "Definition is the canonical parent…", `file_path: docs/adrs/ADR-e8a4d2.md`). No canonical `ADR-224f7a.md` file exists; the registered file_path correctly resolves to the `DEC-e8a4d2` file. |
| Repair | **Documented via Item 4 notice.** No registry mutation — `devhub_decision_update` cannot edit title or file_path, so the row's UID-vs-file inconsistency cannot be tooled. The pairing is recorded inside `ADR-e8a4d2.md`'s new body notice; the registry row is preserved as-is. |
| Tool used | None on registry side |
| Post-repair verification | Audit and closeout cross-link the pair. |
| Residual risk | Collapsing the two UIDs requires either renaming the registry UID (direct DB write) or accepting the dual-UID indefinitely. |

### Item 8 — `DEC-b752cf` (REGISTRY_ONLY — test row)

| Field | Value |
|---|---|
| Original state | Registry row `DEC-b752cf` ([reversed], title "Test auto-allocation (D334 verification)"). No ADR file exists. |
| Repair | **None.** The title already self-identifies as a D334 verification test, and the status is already `reversed`. No further documentation needed — the row's own metadata communicates its nature. Closeout records the row as an intentional test artifact. |
| Tool used | None |
| Post-repair verification | Registry row unchanged. |
| Residual risk | None. Operator may clean up the test row in a separate registry-hygiene pass if desired. |

### Item 9 — `DEC-9d1f4b` (PATH_MISMATCH) — **RESOLVED**

| Field | Value |
|---|---|
| Original state | Registry row `DEC-9d1f4b`: title "MC Constant Value Propagation", `file_path: docs/adrs/ADR-4a8abb.md`. File `ADR-9d1f4b.md` carries D327 (Shared Dimension Normalization). |
| Repair | (i) File-side: added `devhub_registration:` frontmatter + body notice to `ADR-9d1f4b.md`. (ii) Tool extended (§10). (iii) Registry-side: PATCHed via the patched API — title → "Shared Dimension Normalization in CC Field Selection", file_path → "docs/adrs/ADR-9d1f4b.md". (iv) File-side notice updated to record resolution. |
| Tool used | `Edit` (file twice) + `devhub_decision_update` semantics via direct HTTP PATCH (post-patch) |
| Post-repair verification | API GET returns title and file_path aligned with file. PATH_MISMATCH sweep confirms zero residual mismatch for this UID. |
| Residual risk | None. |

### Item 10 — `DEC-4a8abb` (PATH_MISMATCH) — **RESOLVED**

Same pattern as Item 9. Registry row `DEC-4a8abb` post-repair: title="MC Constant Value Propagation — End-to-End", file_path="docs/adrs/ADR-4a8abb.md", description aligned with file frontmatter. File-side notice updated to RESOLVED.

### Item 11 — `DEC-c0290f` (PATH_MISMATCH + duplicate-doctrine in registry) — **RESOLVED**

| Field | Value |
|---|---|
| Original state | Registry row `DEC-c0290f`: title "Derived Canonical Fields — Compute Rules in CC Field Mapping", `file_path: docs/adrs/ADR-637072.md` — duplicated the doctrine of `DEC-637072`. File `ADR-c0290f.md` is "Metric Evaluation Engine — Universal Formula Engine…". |
| Repair | (i) File-side notice added. (ii) Tool extended (§10). (iii) Registry-side: PATCHed — title → "Metric Evaluation Engine — Universal Formula Engine with Schedule-Driven Orchestration", file_path → "docs/adrs/ADR-c0290f.md", description aligned. (iv) Side effect: the duplicate-doctrine condition collapses — `DEC-637072` is now the only registry row carrying the "Derived Canonical Fields" doctrine. (v) File-side notice updated. |
| Tool used | `Edit` (file twice) + direct HTTP PATCH against patched API |
| Post-repair verification | API GET returns the updated title / file_path. PATH_MISMATCH sweep confirms zero residual mismatch for this UID. `DEC-637072` remains canonical for the "Derived Canonical Fields" doctrine; no other registry row claims that title. |
| Residual risk | None. |

### Item 12 — `DEC-03db11` (STATUS_MISMATCH)

| Field | Value |
|---|---|
| Original state | File `ADR-03db11.md`: `status: superseded`, `superseded_by: DEC-ec9e89`. File `ADR-ec9e89.md`: `supersedes: DEC-03db11`. Supersession pair fully declared at the file layer. Registry status: `reversed` — the outlier. |
| Repair | Updated registry status `reversed` → `superseded` via `devhub_decision_update(project_slug=bc-docs, decision_uid=DEC-03db11, status=superseded)`. |
| Tool used | `devhub_decision_update` (1 call) |
| Post-repair verification | Tool response: `Decision DEC-03db11 "Contract Body Principle — JSON-First, Catalog-Separate" -> superseded`. File and registry are now aligned. |
| Residual risk | None on this item. |

### Item 13 — `DEC-f8f925` (SUPERSESSION_MISMATCH — frontmatter `superseded_by` while status is `reversed`)

| Field | Value |
|---|---|
| Original state | File `ADR-f8f925.md`: `status: reversed`, `superseded_by: DEC-c3e57f`. Registry status: `reversed`. The file's body already contains an explicit "REVERSED — duplicate-allocation artifact" notice explaining that DEC-c3e57f is the canonical MCF foundational ADR and that DEC-f8f925 is preserved as audit trail per Foundation Invariant III. |
| Repair | **None.** The body already contains a complete operator-authored explanation. Removing the `superseded_by:` field would alter frontmatter that the operator wrote with intent (as a forward-pointer to the canonical, not a true supersession declaration). Per the operator's primary principle (preservation > over-ceremonialization), the file is left as-is. The closeout records this as a documented exception. |
| Tool used | None |
| Post-repair verification | File frontmatter unchanged; body notice intact. |
| Residual risk | `adr-audit.js` (if extended) might flag this as a supersession-pair anomaly. Acceptable false positive — body content explains the situation. |

### Item 14 — `ADR-DEC-e82f0a.md` (DUPLICATE_DECISION — malformed filename)

| Field | Value |
|---|---|
| Original state | Two files share UID `DEC-e82f0a`: `ADR-e82f0a.md` (canonical, `status: implemented`, registry-bound) and `ADR-DEC-e82f0a.md` (malformed filename, `status: decided`, longer older body). Registry has one row pointing at the canonical file. |
| Repair | Quarantined the malformed-filename file via frontmatter + body notice: changed `status: decided → superseded`, added `superseded_by: DEC-e82f0a`, added `authority: reference` (was `authoritative`), updated title to suffix `[QUARANTINED DUPLICATE FILE]`, updated description to flag the quarantine, added `devhub_registration:` field, and prepended a "QUARANTINED DUPLICATE FILE" warning block to the body. The body content below the warning is **unchanged**. The file was NOT renamed and NOT deleted per the operator hard stop. |
| Tool used | `Edit` (single file edit covering frontmatter + body header in one block) |
| Post-repair verification | File header now declares itself as quarantined duplicate; readers are redirected to `ADR-e82f0a.md`. |
| Residual risk | Filesystem still contains the malformed filename. Future deletion / rename is an operator decision; this closeout does not perform it. |

### Item 15 — `ADR-chain-invariants.md` (UID_PENDING placeholder)

| Field | Value |
|---|---|
| Original state | File `ADR-chain-invariants.md`: `uid: DEC-pending`, `status: proposed`. A placeholder UID; never allocated. |
| Repair | Added `devhub_registration:` frontmatter + body notice explaining the placeholder. Documented promotion path: `devhub_decision_record` with a fresh description; then mark this file as superseded by the result. Not executed in this session (would mint a new UID and require operator intent). |
| Tool used | `Edit` |
| Post-repair verification | File frontmatter + body explicitly call out the placeholder status. |
| Residual risk | Inbound references to `DEC-pending` (none expected — references are by filename) remain. To formalize, operator initiates the allocator call. |

## Preserved as historical exceptions (no content modification)

| UID / file | Preservation reason |
|---|---|
| `DEC-7a1c98` (`ADR-7a1c98.md`) | Already documented as superseded by `DEC-54f221` in prior session. No re-registration attempted. |
| `DEC-f8f925` (`ADR-f8f925.md`) | Operator-authored body already explains the reversed-duplicate-allocation status. No further notice needed. |
| `DEC-b752cf` (registry only) | Self-identifying test row. No file to add notice to. |
| `DEC-d315ve`, `DEC-d316mr` | Non-canonical UIDs that can never be registered under the current allocator regex. Preserved as file-side authorities. |
| `DEC-pending` (`ADR-chain-invariants.md`) | Placeholder UID, never allocated; preserved with note describing the promotion path. |
| `ADR-DEC-e82f0a.md` | Malformed-filename duplicate; quarantined by frontmatter + body notice rather than renamed or removed. |

## Remaining unresolved items (after tool extension + 3 repairs)

Three of the original four PATH_MISMATCH / drift items were resolved via the §10 tool extension and follow-up registry PATCHes. **One residual item** remains, requiring operator judgment (not a tooling gap):

| Item | Defect | Why repair was deferred | What's needed |
|---|---|---|---|
| `DEC-224f7a` registry row paired with file `ADR-e8a4d2.md` | DUPLICATE_CONTENT_RISK — same doctrine ("Definition is the canonical parent — fold contract page into definition page, drop reverse FK") is recorded under two UIDs: `DEC-224f7a` (registry) and `DEC-e8a4d2` (file). Both target the same `ADR-e8a4d2.md` file. | Resolving the duplicate is a UID-canonicalization decision, not a tooling gap. The registry's UID `DEC-224f7a` is mutable only as a row identity (and the existing `devhub_decision_update` deliberately does not expose `uid`). | Operator picks the canonical UID: (a) accept both indefinitely with the file-side notice as the bridge; (b) re-mint canonical via `devhub_decision_record`, mark the older as superseded, accept the new UID; (c) DB-level UID rename via a controlled migration. |

The file-side notice on `ADR-e8a4d2.md` already makes the dual-UID situation explicit, so option (a) is preservation-safe and requires no further action.

## Confirmation statements

- **No ADR content was lost.** All 11 file edits add new content (a `devhub_registration:` frontmatter field and/or a body notice block) and modify zero historical body lines. Frontmatter additions are net-new fields; no existing field's value was overwritten except on `ADR-DEC-e82f0a.md` (the duplicate file), where `status`, `superseded_by`, `title`, `description`, and `authority` were updated to reflect its quarantined-duplicate nature — the body content below is unchanged.
- **No ADR files were deleted.** The single `DUPLICATE_DECISION` candidate (`ADR-DEC-e82f0a.md`) was quarantined in place, not removed.
- **No direct SQL was used.** All registry interactions went through `devhub_decision_update` (or its underlying `PATCH /api/decisions/:uid` route). Four total registry mutations: 1 status reconciliation (`DEC-03db11`) + 3 title/file_path/description reconciliations (`DEC-9d1f4b`, `DEC-4a8abb`, `DEC-c0290f`).
- **`devhub_decision_record` was NOT used.** No new UID was minted; no new ADR file was auto-generated. Every FILE_ONLY_UNEXPLAINED case was preserved as a file-side authority exception, modelled on the `DEC-7a1c98` pattern.
- **`adr-audit.js` was NOT updated in this session.** The detection rules for the new drift classes (file-only, registry-only, path-mismatch, status-mismatch, duplicate-decision) require the script to either read the persisted registry state or call DevHub MCP tools. Either path is a non-trivial code change beyond the operator's "small and obviously reports these drift classes" condition. The patch is documented in §11 and is suitable for a follow-up session.

## 10. DevHub tooling patch — `devhub_decision_update` field expansion

Operator authorized a follow-up patch to `devhub_decision_update` so the three PATH_MISMATCH repairs (items 9–11) could land via the supported API path rather than direct SQL. The patch is **additive only**: existing parameters keep their pre-patch semantics; the new parameters are all optional.

### Files changed in `barecount-devhub`

| File | Change | Lines touched |
|---|---|---|
| `src/middleware/validate.js` | Added `title_text`, `subdomain_text`, `focus_text` to the `updateDecision` Zod schema as optional `z.string()`. (Prior behavior: `subdomain_text` and `focus_text` passed through `.passthrough()` but were undeclared; `title_text` was neither declared nor passed through to the SQL layer.) | 3 lines added inside the existing object literal |
| `src/routes/decisions.js` | Destructured `title_text` from `req.body` and added the conditional `UPDATE decisions SET title_text = ?` push to the dynamic params list. Mirror of the existing pattern for `file_path`, `description_text`, etc. | 2 lines added |
| `src/mcp-server.js` | Exposed `title_text`, `file_path`, and `description_text` on the `devhub_decision_update` Zod schema as optional fields and forwarded them in the PATCH body. Tool description updated to call out the audit-driven reconciliation use case. | ~10 lines added inside the existing tool registration |

### Safety properties of the patch

- **Optional everywhere.** None of the new fields are required; existing call sites (status-only update, status + rationale_text, etc.) work unchanged.
- **No table schema change.** The `decisions` table already had `title_text`, `description_text`, and `file_path` columns. The patch only extends the API/MCP surface to update them.
- **No supersession of the existing audit trail.** `logActivity()` still writes a `decision_${status}` row for every PATCH, identifying actor + status. (Field-level diffs are not journaled today; this is a follow-up if needed.)
- **No defaults applied.** A field is updated only if explicitly present in the request body; an absent field leaves the row unchanged. No "" → NULL or NULL → "" coercion.
- **Audit-driven actor name.** All four repair PATCHes carried `actor_name: "audit-repair-2026-06-22"`, making the rows traceable to this closeout.

### Verification

Node `--watch` (per `npm run dev`) picked up the changes immediately. The HTTP probe against `POST /api/decisions/DEC-9d1f4b` returned `200` with the new title and file_path echoed in the response body. Subsequent reads via `GET /api/decisions?status=…` show the new values persisted. A PATH_MISMATCH sweep across all `decided + implemented` rows post-repair returned exactly one residual hit — `DEC-224f7a -> ADR-e8a4d2.md` — which is the DUPLICATE_CONTENT_RISK item explicitly out of scope for the §10 patch (it needs a UID-canonicalization decision, not a title/file_path edit).

### Backward compatibility

The MCP tool description was extended (it now mentions title / description / file_path), so a previously-cached schema is still valid — old callers continue to work because the new fields are optional. Any caller that picks up the updated schema gains the three new parameters without behavior change to the others.

## 11. Recommended recurring audit process

To prevent drift accumulation, the closeout proposes the following:

1. **Extend `bc-docs-v3/scripts/adr-audit.js`** to add four new diagnostic outputs:
   - `fileOnlyUnexplained` — ADR files whose frontmatter UID does not appear in the decision registry AND whose body does not declare a documented exception (cross-reference to a successor or operator-authored notice).
   - `registryOnlyMissingFile` — registry rows whose `file_path` resolves to a file that does not exist.
   - `pathMismatch` — registry rows whose `file_path` basename does not equal `ADR-{shortUid}.md` (excluding the four accepted numeric early-pattern rows).
   - `statusMismatch` — registry rows whose status disagrees with the file's `status:` frontmatter.

   The script can read the registry by either (a) shelling out to `devhub_decision_list` for each status filter and parsing the output, or (b) querying SQLite directly (the registry is at `barecount-devhub/data/devhub.db`). Diagnostic-only — no writes.

2. **Run the script on a monthly cadence**, or before each major ADR-heavy milestone. The existing `node bc-docs-v3/scripts/adr-audit.js` invocation already prints supersession-pair issues; the new diagnostics would be additive.

3. ~~**Extend `devhub_decision_update` to support title / file_path edits**~~ — **DONE 2026-06-22** (see §10). The tool now accepts `title_text`, `description_text`, and `file_path` as optional updatable fields. Three of the four originally-deferred items resolved on the same day. Only `DEC-224f7a` remains, and that one needs a UID-canonicalization decision, not a tooling extension.

4. **At session boot**, surface any drift counts via `devhub_session_boot` so the operator sees them before starting work. Implementation: the `adr-audit.js` script writes a small JSON status file that `devhub_session_boot` reads. No new tool needed.

5. **CLAUDE.md amendment** (deferred): the ADR Hygiene Policy section (DEC-623f8f / D370) already lists 8 rules. Adding a 9th — "ADRs SHOULD be filed via `devhub_decision_record`; file-only ADRs require an explicit `devhub_registration:` frontmatter field documenting the exception" — formalizes the convention this audit + repair established. This is a small operator-owned amendment to CLAUDE.md; not done in this session.

## Cross-reference cascade after this repair

The audit doc, closeout doc, and the affected ADR files now form a closed cross-reference cluster. Inbound links to any of the file-only / path-mismatched / non-canonical UIDs continue to resolve at the filename level (none are changed). The closeout doc is the new single point of operator-visible truth for outstanding registry drift.

## Stop condition

Repair pass complete under the preservation-first doctrine. No direct SQL, no UID minting, no file deletion, no body rewrites. 12 of 15 audited items reached a fully repaired or fully documented state; 3 items have explicit deferred-to-operator notes with the exact tooling extension that would resolve them. The decision-registry status reconciliation for `DEC-03db11` is the single registry-side mutation. Awaiting operator direction on the deferred items.
