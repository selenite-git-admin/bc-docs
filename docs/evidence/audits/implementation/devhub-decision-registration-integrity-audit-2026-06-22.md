---
title: "DevHub Decision-Registration Integrity Audit"
description: "Read-only audit: file-side vs decision-registry vs doc-registry; classifies every ADR file; surfaces drift cases analogous to DEC-7a1c98."
date: 2026-06-22
project: bc-docs
domain: governance
subdomain: adr-registry
focus: governance
authority: reference
---

# DevHub Decision-Registration Integrity Audit — 2026-06-22

## Scope and posture

This is a read-only audit triggered by the DEC-7a1c98 protocol gap (hand-filed ADR not decision-registered, since superseded by canonically-registered DEC-54f221). The audit determines whether similar drift exists elsewhere in the 430-file ADR corpus.

**No registry mutations were performed.** No `devhub_decision_record`, `devhub_decision_update`, `devhub_doc_update`, or any other write tool was invoked. No ADR file was edited. No DB write was attempted.

## 1. Inventory totals

| Surface | Count | Method |
|---|---|---|
| ADR files (`bc-docs-v3/docs/adrs/ADR-*.md`) | 430 | filesystem scan |
| Unique frontmatter UIDs in files (DEC-* hex form) | 426 | grep `^uid: DEC-` + dedupe; excludes `DEC-pending` + template placeholders |
| Non-hex frontmatter UIDs (in addition to the 426) | 2 | `DEC-d315ve`, `DEC-d316mr` |
| Frontmatter UID `DEC-pending` | 1 | `ADR-chain-invariants.md` |
| Decision-registry rows (sum of all 5 statuses) | 424 | `decided`(101) + `proposed`(15) + `superseded`(62) + `reversed`(6) + `implemented`(240) |
| File↔registry overlap (UIDs present in both) | 422 | `comm -12` |

Cross-status duplicates within the decision registry: **none** — every registered UID appears in exactly one status row.

## 2. Classification summary

| Classification | Count |
|---|---|
| OK (file UID in registry; canonical `ADR-{shortUid}.md` filename; frontmatter UID matches; status not in dispute) | ~420 |
| `DOCUMENTED_SUPERSEDED_FILE_ONLY` | 1 |
| `FILE_ONLY_UNEXPLAINED` | 5 |
| `REGISTRY_ONLY` | 2 |
| `PATH_MISMATCH` (registry `file_path` basename ≠ canonical `ADR-{shortUid}.md`) | 4 |
| `STATUS_MISMATCH` (file `status:` ≠ registry status) | 1 |
| `SUPERSESSION_MISMATCH` (file carries `superseded_by:` while status is `reversed`) | 1 |
| `DUPLICATE_DECISION` (one UID, two ADR files) | 1 |
| `DUPLICATE_CONTENT_RISK` (registry row and file_only ADR carry the same doctrine under two different UIDs) | 1 pair |
| `UID_FORMAT_NON_CANONICAL` (UID short form is not 6 hex chars) | 2 |
| `UID_PENDING` (placeholder UID `DEC-pending` not yet allocated) | 1 |

Numbers add up across categories with some overlap: e.g. `DEC-d315ve` is both `FILE_ONLY_UNEXPLAINED` (no registry row) and `UID_FORMAT_NON_CANONICAL` (UID can never be registered under the current allocator regex).

## 3. Defects requiring correction

### 3.1 `PATH_MISMATCH` (4 cases)

Registry rows whose `file_path` basename does not equal the canonical `ADR-{shortUid}.md`. The file at the registered path exists, but its frontmatter `uid:` is for a different DEC. The four mismatches form what looks like a once-off shift in two adjacent regions of the registry.

| Registry UID | Registry status | Registry `file_path` | File's actual frontmatter UID | File's actual title |
|---|---|---|---|---|
| `DEC-9d1f4b` | decided | `docs/adrs/ADR-4a8abb.md` | `DEC-4a8abb` | MC Constant Value Propagation — End-to-End (D329) |
| `DEC-4a8abb` | decided | `docs/adrs/ADR-cbc07b.md` | `DEC-cbc07b` | Type Conformance Enforcement — Source Object through Metric Snapshot (D331) |
| `DEC-224f7a` | implemented | `docs/adrs/ADR-e8a4d2.md` | `DEC-e8a4d2` | Definition is the canonical parent — fold contract page into definition page, drop reverse FK |
| `DEC-c0290f` | implemented | `docs/adrs/ADR-637072.md` | `DEC-637072` | Derived Canonical Fields — Compute Rules in CC Field Mapping (D330) |

Two-cluster pattern (decided block + implemented block) suggests an earlier ADR-file rename or UID re-allocation pass that didn't carry through to the registry's `file_path` column. Compounded by the fact that the registry row's *title* matches the *file it points at*, not the file at the canonical path — i.e. it is the **registered UID** that has drifted, not the title or the file content. See §3.4 for the matching `DUPLICATE_CONTENT_RISK`.

### 3.2 `FILE_ONLY_UNEXPLAINED` (5 cases)

ADR files exist with hex-form UIDs but no corresponding row in any status of the decision registry. These are most likely hand-filed (file-only) ADRs where `devhub_decision_record` was not called and no successor-supersession exception is documented.

| File | File UID | File status | Date | Notes |
|---|---|---|---|---|
| `ADR-9a5dc0.md` | `DEC-9a5dc0` | decided | 2026-04-11 | "CF Boundary — Reporting Standards Promote to Canonical Fields". Referenced as D302 in `ADR-chain-invariants.md` and `ADR-cbc07b.md`. Carries valid frontmatter + body. |
| `ADR-cbc07b.md` | `DEC-cbc07b` | proposed | 2026-04-15 | "Type Conformance Enforcement — Source Object through Metric Snapshot" (D331). Frontmatter includes literal `decision_code: D331` — CLAUDE.md says never specify `decision_code` when calling `devhub_decision_record` (allocator owns it). Hand-filing is the simplest explanation. Note: the *registry* uses the same doctrine under `DEC-4a8abb` per §3.1 PATH_MISMATCH. |
| `ADR-e8a4d2.md` | `DEC-e8a4d2` | implemented | 2026-04-16 | "Definition is the canonical parent — fold contract page into definition page, drop reverse FK". The registry uses the *same doctrine* under `DEC-224f7a` (see §3.4). |
| `ADR-d315ve.md` | `DEC-d315ve` | decided | 2026-04-14 | "D315 — Metric Evaluation Verification Framework". `d315ve` is not 6 hex chars; the UID can never be registered under the `[0-9a-f]{6}` allocator. Looks like a vanity UID matching the D-code. Also `UID_FORMAT_NON_CANONICAL`. |
| `ADR-d316mr.md` | `DEC-d316mr` | decided | 2026-04-14 | "D316 — Metric Readiness Scheduler". Same non-hex pattern; same classification. |

### 3.3 `REGISTRY_ONLY` (2 cases)

Decision-registry rows that exist but the registered ADR file is missing.

| Registry UID | Registry status | Title | Notes |
|---|---|---|---|
| `DEC-224f7a` | implemented | "Definition is the canonical parent — fold contract page into definition page, drop reverse FK" | Registry `file_path` is `docs/adrs/ADR-e8a4d2.md` (a `PATH_MISMATCH` per §3.1). The canonical file `ADR-224f7a.md` does **not** exist on disk. The content lives in `ADR-e8a4d2.md` under a different UID — `DUPLICATE_CONTENT_RISK`, see §3.4. |
| `DEC-b752cf` | reversed | "Test auto-allocation (D334 verification)" | The registry description itself flags this as a D334 verification test, i.e. a deliberate test row, not a real decision. No `ADR-b752cf.md` exists. Treat as intentional test artifact, not a defect; eligible for registry cleanup if operator chooses. |

### 3.4 `DUPLICATE_CONTENT_RISK` (1 pair)

Same doctrine recorded under two UIDs — once in a file with no registry row, once in a registry row with no canonical file.

| Surface | UID | Title |
|---|---|---|
| File only | `DEC-e8a4d2` (`ADR-e8a4d2.md`, status `implemented`) | Definition is the canonical parent — fold contract page into definition page, drop reverse FK |
| Registry only | `DEC-224f7a` (status `implemented`; `file_path: ADR-e8a4d2.md`) | Definition is the canonical parent — fold contract page into definition page, drop reverse FK |

The registry row `DEC-224f7a` already points at `ADR-e8a4d2.md` (the `DEC-e8a4d2` file). It's plausibly the same doctrine that exists under two UIDs — file under `DEC-e8a4d2`, registry under `DEC-224f7a`. Operator decides which is canonical; do not mint a third.

### 3.5 `DUPLICATE_DECISION` (1 case)

One frontmatter UID, two ADR files on disk.

| File | Filename pattern | Frontmatter UID | Frontmatter status | Frontmatter date |
|---|---|---|---|---|
| `ADR-e82f0a.md` | canonical | `DEC-e82f0a` | implemented | 2026-03-29 |
| `ADR-DEC-e82f0a.md` | malformed (double `DEC-` prefix in filename) | `DEC-e82f0a` | decided | 2026-03-29 |

Registry has exactly one row for `DEC-e82f0a` (implemented, `file_path: ADR-e82f0a.md`). The `ADR-DEC-e82f0a.md` file is an orphaned duplicate — older `status: decided` content, longer body, malformed filename. Most likely a tooling glitch where the auto-generator double-prefixed the filename.

### 3.6 `STATUS_MISMATCH` (1 case)

| UID | File status | Registry status | Notes |
|---|---|---|---|
| `DEC-03db11` | `superseded` (file frontmatter; `superseded_by: DEC-ec9e89`) | `reversed` | The file is set up as a supersession pair (target of `ADR-ec9e89.md` per §3.7) but the registry treats the decision as **reversed** rather than **superseded**. Two distinct lifecycle endings; the file and registry disagree on which one applies. |

### 3.7 `SUPERSESSION_MISMATCH` (1 case)

| UID | File status | File `superseded_by` | Registry status | Notes |
|---|---|---|---|---|
| `DEC-f8f925` | `reversed` | `DEC-c3e57f` | `reversed` | File and registry agree status is `reversed`, but the file still carries `superseded_by: DEC-c3e57f` — a stale field from an earlier intent. `ADR-c3e57f.md` (the would-be successor) is decided and live; the operator's stated endpoint for `DEC-f8f925` is reversal, not supersession. Field-level stale; no behavior impact, but ambiguous on read. |

### 3.8 Supersession-pair observations (not classified as defects)

The audit also surveyed all 19 ADRs with a `supersedes:` field. Two notes that do **not** rise to defect level:

- **Partial supersession** — `ADR-3ee0f6.md` declares `supersedes: DEC-14592e` and its description scopes the supersession to bucket structure only ("WORM/Object-Lock principle from DEC-14592e remain in force"). `DEC-14592e` retains `status: implemented` in both file and registry. This is by-design partial supersession, not a defect, but worth flagging since it's the one case where the supersession-pair flip is intentionally skipped.

- **Premature flip** — `ADR-95687d.md` is `status: proposed` and declares `supersedes: DEC-a25931`. `DEC-a25931` is already flipped to `superseded` (file + registry). The ADR Hygiene Policy (CLAUDE.md §"ADR Hygiene Policy") rule 1 is honoured at the file layer (target is `superseded`, has `superseded_by`), but the superseder is itself only `proposed`. If the proposed ADR is ever rejected, the target would need to flip back. Operator-aware; no remediation proposed by this audit.

## 4. Documented exceptions (already accepted; not defects)

### 4.1 `DEC-7a1c98` — the trigger of this audit

| Surface | State |
|---|---|
| File (`ADR-7a1c98.md`) | `status: superseded`, `superseded_by: DEC-54f221`; in-body supersession notice. |
| Decision registry | Row does not exist. Predecessor reference in `DEC-54f221`'s registry row carries the supersedes UID. |
| Doc registry | Indexed as `DOC-4ccba8` (per the original Path-A workaround). |
| Successor `DEC-54f221` | Decision-registered correctly; `ADR: docs/adrs/ADR-54f221.md`; `[decided] [contracts]`. |

Classification: `DOCUMENTED_SUPERSEDED_FILE_ONLY`. **No remediation required** — operator has explicitly recorded this as an intentional documented exception. Do not attempt to register `DEC-7a1c98` retroactively.

### 4.2 `DEC-pending`

`ADR-chain-invariants.md` carries `uid: DEC-pending`, `status: proposed`. This is a deliberate placeholder until a real UID is allocated. The registry contains no `DEC-pending` row. Classification: `UID_PENDING`. Eligible for normal allocation flow (run `devhub_decision_record` with a real description and let the allocator assign a UID) when the operator chooses to formalize.

### 4.3 `UID_FORMAT_NON_CANONICAL` — `DEC-d315ve`, `DEC-d316mr`

Both are dated 2026-04-14 with `status: decided` and full bodies. The UID short form mixes hex and non-hex characters (`d315ve`, `d316mr`) — likely D-code-as-vanity. The current allocator regex `[0-9a-f]{6}` will not accept these UIDs, so neither file can be re-keyed without a fresh allocator call (which mints a new UID). Operator decides whether to (a) preserve as-is under documented exception, or (b) mint successor ADRs that absorb the doctrine under canonical UIDs.

### 4.4 Numeric early-pattern ADRs `ADR-0001.md`..`ADR-0004.md`

UIDs `DEC-000001`..`DEC-000004` map to filenames `ADR-0001.md`..`ADR-0004.md`. Treated as an accepted historical naming pattern, not a `PATH_MISMATCH`. All four are registered (`status: superseded` in both file and registry).

## 5. Cross-reference check

For the file-only and registry-only UIDs surfaced in §3.2 and §3.3, the cross-references inside live `bc-docs-v3/docs/` chapters were spot-checked:

- `DEC-9a5dc0` is referenced from `ADR-chain-invariants.md` and `ADR-cbc07b.md`. Both references resolve to an existing file.
- `DEC-cbc07b` is referenced from `ADR-chain-invariants.md` and elsewhere. References resolve to an existing file.
- `DEC-e8a4d2` is the title-equivalent of `DEC-224f7a`. Cross-references in narrative docs would resolve under whichever UID is used.
- `DEC-d315ve` / `DEC-d316mr` are referenced under their non-hex UIDs by `ADR-cbc07b.md` and `ADR-chain-invariants.md`. References resolve to existing files.
- `DEC-7a1c98` references resolve (file present + DEC-54f221 cross-pointer).

Historical references inside preserved audit / pre-doctrine / Step 2 inventory docs to `DEC-7a1c98` (in §7 of `mcf-framework-audit-2026-06-22.md`, etc.) are intentionally preserved per Foundation Invariant III and are not defects.

## 6. Protocol-risk analysis

| Risk | Cases | Diagnosis |
|---|---|---|
| ADRs created outside `devhub_decision_record` | 5 unexplained + 1 documented (`DEC-7a1c98`) | Hand-filing produces file-only ADRs that lack a registry row. Detectable but not preventable in tooling today. |
| ADRs claiming DevHub registration where the registry disagrees | 0 explicit (no file carries a `devhub_registration:` claim that says "registered" where the registry doesn't); 1 documented exception (`DEC-7a1c98` whose `devhub_registration:` explicitly notes the gap) | No defects of this kind; the one note is honest about the gap. |
| Doc-registry indexing without decision-registry rows | 5 (the unexplained file-only group) + 1 documented (`DEC-7a1c98`) | The doc-scanner walks the filesystem and indexes everything it finds. Decision-registry registration is a separate explicit step (`devhub_decision_record`). The two registries diverge by design when the explicit step is bypassed. |
| File↔registry path drift | 4 (`PATH_MISMATCH`) | Old `file_path` strings inside registry rows persisted while files were renamed under newer UID allocations. The mismatch shows up because the registered title still matches the file at the old path, not the file at the canonical path. |
| Status drift | 1 (`STATUS_MISMATCH`, `DEC-03db11`) + 1 (`SUPERSESSION_MISMATCH`, `DEC-f8f925`) | File frontmatter and registry rows can drift independently; nothing today auto-syncs the two on lifecycle changes. |

## 7. Safe correction options per defect

These are **options for operator review**, not prescriptions. Every option carefully avoids minting a new UID for an existing ADR (per hard stops).

### 7.1 `PATH_MISMATCH` (§3.1) — 4 cases

For each affected row, two safe paths:

**Option A — Update registry `file_path` only** (no UID change): `devhub_decision_update` (read-only equivalent unavailable; this is a registry mutation) to point each registered UID at its canonically-named ADR file (`ADR-{shortUid}.md`). Requires the canonical file to actually exist with the matching frontmatter UID. Check:

| Registry UID | Canonical file would be | Exists? | Frontmatter UID matches? |
|---|---|---|---|
| `DEC-9d1f4b` | `ADR-9d1f4b.md` | yes | yes (uid `DEC-9d1f4b`, title "Shared Dimension Normalization in CC Field Selection") |
| `DEC-4a8abb` | `ADR-4a8abb.md` | yes | yes (uid `DEC-4a8abb`, title "MC Constant Value Propagation — End-to-End") |
| `DEC-224f7a` | `ADR-224f7a.md` | **no** | n/a |
| `DEC-c0290f` | `ADR-c0290f.md` | yes | yes (uid `DEC-c0290f`, title "Metric Evaluation Engine — Universal Formula Engine with Schedule-Driven Orchestration") |

So Option A is mechanically clean for `DEC-9d1f4b`, `DEC-4a8abb`, `DEC-c0290f`. For `DEC-224f7a`, no canonical file exists — Option A is blocked.

**Option B — Operator-driven reconciliation:**
The registry's *title* for `DEC-9d1f4b` says "MC Constant Value Propagation" but file `ADR-9d1f4b.md`'s title says "Shared Dimension Normalization" — they're different doctrines. Three sub-options:
- B1: Treat the registry row as canonical, mark the file as in error, operator authors a corrective file rename + frontmatter UID change. **High risk** — operator must verify the file's true intent.
- B2: Treat the file as canonical, update the registry row's title + description + file_path to match. Closes the drift on the file side.
- B3: Mint a new registry row for the file's content under a new UID, demote the existing registry row's path. **Violates the no-new-UID hard stop** — do NOT do this.

Recommend: read each ADR file pair (`ADR-{registry-uid}.md` vs `ADR-{registered-file-path}`) and inspect the historical commit log to determine which UID was the authoring intent. Then choose B1 vs B2. No action by this audit.

### 7.2 `FILE_ONLY_UNEXPLAINED` (§3.2) — 5 cases

For `DEC-9a5dc0`, `DEC-cbc07b`, `DEC-e8a4d2`: same problem class as `DEC-7a1c98`. Two paths:
- **Same as DEC-7a1c98 (intentional exception)** — leave file alone, accept `DOCUMENTED_SUPERSEDED_FILE_ONLY` status only if the operator marks each as superseded by a successor that *is* registered (analogous to DEC-54f221's role). Without a successor, this option doesn't apply.
- **Backfill into decision registry** — operator authors a fresh `devhub_decision_record` call that captures the same intent (atomic UID allocation; new file generated as `ADR-{newUid}.md`); then marks the original file as superseded by the new one and updates cross-references. **This mints a new UID** — explicitly excluded from this audit's actions.

For `DEC-d315ve`, `DEC-d316mr`: same paths, with the additional constraint that the existing UIDs can never be registered (non-hex). Successor minting (the new-UID path) is the only mechanical option for registration; the existing files would need to be marked superseded.

For `DEC-e8a4d2`: see §3.4 — it's a `DUPLICATE_CONTENT_RISK` with `DEC-224f7a`. Resolution belongs to the operator: decide which UID is canonical, then propagate. Both sides currently say `implemented` so this is also asymmetric.

### 7.3 `REGISTRY_ONLY` (§3.3) — 2 cases

For `DEC-224f7a`: see §3.4 — paired with `DEC-e8a4d2`. Either option from §3.4 closes both this and `DEC-e8a4d2`'s file-only state.

For `DEC-b752cf`: registry-only test row from D334 verification. Two safe paths:
- **Leave as-is** — accepts a test artifact in the registry. Low risk; cosmetic.
- **Operator-driven registry update** (`devhub_decision_update`) to clarify the test nature in the description, or to mark it for archival.

### 7.4 `DUPLICATE_DECISION` (§3.5) — 1 case (`ADR-DEC-e82f0a.md`)

Two safe paths:
- **Filesystem cleanup** — remove the malformed-filename file `ADR-DEC-e82f0a.md` after verifying its content is fully captured in `ADR-e82f0a.md`. The registry already points at `ADR-e82f0a.md`. **Filesystem mutation; deferred to operator.**
- **Preserve as historical artifact** — rename `ADR-DEC-e82f0a.md` to a clearly-archive-flagged path (e.g. `ADR-e82f0a.md.duplicate-2026-06-22`). **Filesystem mutation; deferred to operator.**

### 7.5 `STATUS_MISMATCH` (§3.6) — `DEC-03db11`

Operator clarifies whether D232 was reversed or superseded by `DEC-ec9e89`, then aligns the surface that disagrees. Likely the file is correct (it has explicit `superseded_by`) and the registry is stale. `devhub_decision_update` would close it.

### 7.6 `SUPERSESSION_MISMATCH` (§3.7) — `DEC-f8f925`

File-level cleanup: remove the stale `superseded_by:` field from `ADR-f8f925.md` frontmatter (it's reversed, not superseded). **File edit; deferred to operator.**

## 8. Recommended correction sequence

Strictly an audit recommendation; nothing has been executed.

1. **Document the protocol gap as a class** — file a single ADR (operator authors) generalizing the lesson from DEC-7a1c98 / DEC-54f221: "ADR files SHOULD be filed via `devhub_decision_record` unless an explicit documented-exception path applies; file-only ADRs accumulate as registry drift." This raises the ceiling — the rule already exists in CLAUDE.md ("`devhub_decision_record` — creates the DevHub metadata AND auto-generates the ADR file") but doesn't carry enforcement teeth in the audit script.

2. **Surface the audit findings in the existing ADR audit script** — `bc-docs-v3/scripts/adr-audit.js` already reports supersession-pair issues. Add the four detection rules surfaced here (file-only no-exception, registry-only no-file, path-mismatch, status-mismatch). Pure diagnostic, no writes. Operator-owned.

3. **Resolve PATH_MISMATCH (§3.1) — clean cases first** — for the three rows whose canonical file exists with matching frontmatter UID (`DEC-9d1f4b`, `DEC-4a8abb`, `DEC-c0290f`), the file_path correction is mechanical via `devhub_decision_update`. **One careful pass; not in this audit's scope.**

4. **Resolve the title-vs-file content drift inside PATH_MISMATCH** — for the same three rows, also reconcile the *title* drift between registry rows and the files at the canonical paths. This is an operator-judgment task per row (see §7.1 B1 vs B2).

5. **Resolve REGISTRY_ONLY + DUPLICATE_CONTENT_RISK pair (`DEC-224f7a` ↔ `DEC-e8a4d2`)** — operator picks the canonical UID; this audit can't make that call.

6. **Status / supersession drift (§3.6 + §3.7)** — single `devhub_decision_update` for `DEC-03db11`; one file-edit for `DEC-f8f925`. Both small.

7. **DUPLICATE_DECISION (§3.5)** — filesystem cleanup of `ADR-DEC-e82f0a.md` after operator verification.

8. **FILE_ONLY_UNEXPLAINED (§3.2)** — these are the highest-stakes items because each carries authoritative-looking doctrine but no registry presence. Operator decides per ADR whether to: (a) document as intentional exception (DEC-7a1c98 pattern, requires a registered successor), (b) mint a successor that absorbs the doctrine, or (c) leave as-is and accept drift. This audit takes no action.

9. **`DEC-d315ve` / `DEC-d316mr` (§4.3)** — special case of step 8 because the existing UID is unregistrable. Successor minting is the only mechanical path to registration.

## 9. Hard stops

None triggered during this audit. Specifically:

- No `devhub_decision_record` was called. No UIDs were minted.
- No `devhub_decision_update` was called. No registry rows were modified.
- No direct DB write was attempted.
- No ADR file was edited. No file was renamed or deleted.
- No DOC registry update was performed.
- The `devhub_doc_list type=decision` output was too large to inline (3,228 lines persisted to a tool-results file) and was not consumed in bulk — relied on the spot evidence that `bc-docs-v3/scripts/adr-audit.js` and `devhub_doc_scan` already keep the doc registry in sync with the filesystem (per CLAUDE.md "DevHub's document index is a derived scan — never the authority"). If the operator wants exhaustive doc-registry verification per ADR, that's a follow-up.

## 10. Decision-registry vs doc-registry semantics — clarified

Both registries hold pointers to the same ADR files but are populated by different mechanisms:

| Registry | Population mechanism | Authority |
|---|---|---|
| Decision registry (`decision` table; surfaced via `devhub_decision_list/record/update`) | Explicit registration via `devhub_decision_record` (atomic UID + D-code allocation + file creation). | Tracks the *decision lifecycle*: status, supersession chain, registered file_path, project, domain. |
| Doc registry (`document` table; surfaced via `devhub_doc_list/scan`) | Automatic filesystem scan walking `bc-docs-v3/docs/` (and v2 if `BC_DOCS_PATH` is overridden). | Tracks the *file inventory*: presence, frontmatter, freshness, document type derived from path. Per CLAUDE.md: "**DevHub's document index is a derived scan — never the authority.**" |

The decision registry is opt-in (someone has to call `devhub_decision_record`). The doc registry is opt-out (anything matching the scanner's filter is auto-indexed). This asymmetry is the root cause of every `FILE_ONLY_UNEXPLAINED` case — the file is doc-indexed automatically but not decision-registered.

The two surfaces can be reconciled but never made identical: the doc registry includes README files, audit reports, errata, and other documents that are not decisions; the decision registry includes test rows like `DEC-b752cf` that have no ADR file backing.

## 11. Explicit no-mutations statement

No registry mutations were performed during this audit. No ADR file was edited. No DB write was attempted. No `devhub_decision_record`, `devhub_decision_update`, `devhub_doc_update`, or any other write tool was invoked. The successor-ADR filing (`DEC-54f221`) referenced in §4.1 was performed in the prior session turn; this audit only inspects its result.
