# PLAN - bc-external-audit repository shutdown and cleanup

Status: REVIEW PACKET ONLY - not authorized for execution
Author: Codex auditor session
Date: 2026-08-01
Scope: `selenite-git-admin/bc-external-audit` remote and local `C:\MyProjects\bc-external-audit*` worktrees

## 1. Purpose

This packet proposes a governed shutdown plan for the `bc-external-audit` proving-ground repository.
It is a design and review artifact only. It does not authorize local deletion, directory moves, remote
archive, PR closure, branch deletion, database mutation, KMS/key changes, or CI/app credential changes.

## 2. Decision basis

The shutdown is supported by existing governance, with one important scope correction:

| Document | Path | SHA-256 | Relevance |
|---|---|---:|---|
| DEC-b7d74b | `C:\MyProjects\bc-docs\docs\governance\adrs\ADR-b7d74b.md` | `c640a42f4f6821a40106f3c1a1d62c3e16cab680d3f20dee0c3ce3d1aa5b198a` | Retires the signed audit courier / response transport and preserves checker trust plus admission gates. |
| GOV-ERR-003 | `C:\MyProjects\bc-docs\docs\governance\errata\GOV-ERR-003.md` | `8c70279fa6fec6c44a615ed950d3bc400e2b17c081322d9d5c0ed20a5e03a055` | Narrows DEC-b7d74b: the response lane is retired; request publication stays. |
| AuditDocHub interim blueprint | `C:\MyProjects\bc-external-audit\docs\audithub-interim-blueprint-and-todo.md` | `7cbd5be011540555e212eabd6475fc79230441a0af8b3dfa27571fc22f369019` | Defines `bc-external-audit` as a temporary proving ground whose retained learning should migrate. |
| Courier retirement memo | `C:\MyProjects\bc-external-audit-ramp5\docs\MEMO-Claude-courier-retirement-and-publish-halt-2026-07-25.md` | `9c312733c28abd4816f0e5d2b17af3fbd5d3aea440fb379b90d6278244cdf2bf` | Operational halt memo for the retired response-publish driver. |

Correct reading: retire the repository as a courier/proving-ground implementation, not the independent
checker role, not `bc-auditor-app` review identity, not the request lane, and not the platform admission
gate or CRV/checker doctrine.

## 3. Observed state on 2026-08-01

- Local `C:\MyProjects` contains 47 `bc-external-audit*` directories.
- These directories are mostly registered git worktrees of the same repository.
- The remote is `https://github.com/selenite-git-admin/bc-external-audit.git`.
- Remote state observed through GitHub CLI: private, default branch `main`, not archived.
- Remote open PR count observed through GitHub CLI: 10.
- Canonical worktree `C:\MyProjects\bc-external-audit` is dirty with 169 `git status --short` entries.
- Other dirty worktrees observed: `bc-external-audit-b2-custody-fresh`,
  `bc-external-audit-b3-refresh-fresh`, `bc-external-audit-m6-design`,
  `bc-external-audit-m6-r4-probe`, `bc-external-audit-rdl3-compat-implementation`,
  and `bc-external-audit-v3-materialization-dbcp-r3`.
- A registered temporary worktree also exists outside `C:\MyProjects`:
  `C:\Users\anant\AppData\Local\Temp\bc-pr66-reviewed-5be832e`.

This state is not cleanup-ready. The first execution unit must preserve local bytes before any
removal or remote archival action.

## 4. Target end state

1. `bc-external-audit` remote remains available as a read-only historical archive.
2. One local archive copy remains recoverable and hash-manifested.
3. Redundant local worktrees are removed only after byte preservation and manifest verification.
4. Durable governance and architecture knowledge lives in `bc-docs`.
5. Historical exchange/evidence artifacts live in `barecount-devhub`.
6. Live platform code and tests remain in `bc-core`; retired courier code is not copied into live systems.
7. Environment variables, app registrations, jobs, and keys tied only to the retired courier are identified
   for later decommission, not silently removed.

## 5. Relocation map

| Material class | Current examples | Destination | Rule |
|---|---|---|---|
| Shutdown decision, doctrine, closure receipt | ADR/errata/this packet | `bc-docs` | Canonical governance home. |
| AuditDocHub architecture and deferred controls | interim blueprint and named architecture inputs | `bc-docs` | Promote by manifest; do not perform ad hoc moves. |
| Historical exchange packets, reviews, relays, closures | `barecount-devhub/artifacts/metric-audit`, `bc-external-audit-ramp5/docs` mirrors | `barecount-devhub` archive area | Preserve byte identity and old path references. |
| Live checker/admission behavior | request import, c1-c12 gate, CRV-derived imports | `bc-core` | Only live runtime surfaces belong here. |
| Retired response courier implementation | KMS signing, response feed, outbox/pickup transport, epoch cut machinery | remote/local archive only | Do not migrate into live repos. |
| Auditor-session operating discipline | `AUDITOR-SESSION-KIT` and session startup rules | `bc-docs` plus active Codex skill | Preserve if still used by checker sessions. |
| Database/KMS operational evidence | backups, apply closures, key identifiers | evidence archive plus later decommission DBCP | Do not drop DB evidence or disable keys without a separate gate. |

## 6. Execution design

### Phase 0 - Review and approval

Required before any action:

- Review this packet.
- Decide whether open remote PRs are merged, closed as superseded, or retained as archival references.
- Decide whether the final archived remote should be `bc-external-audit` as-is or renamed before archive.
- Decide whether the future implementation repository is deferred or named now as `bc-auditdochub`.

### Phase 1 - Freeze and manifest

Produce a closure manifest containing:

- every local worktree path;
- git-dir/common-dir;
- branch or detached HEAD;
- full HEAD commit;
- upstream tracking branch when present;
- dirty file list;
- untracked file list;
- remote URL;
- last-write timestamp;
- archive disposition.

For every dirty worktree, produce:

- `git diff` patch;
- staged diff if any;
- untracked-file manifest;
- SHA-256 manifest for untracked retained files;
- compressed byte archive or archival branch commit.

Stop condition: any dirty worktree lacking preserved bytes.

### Phase 2 - PR and branch disposition

For the 10 open PRs:

- read title, head, base, CI status, and last update;
- classify as `merge`, `close-superseded`, `archive-only`, or `needs-human-decision`;
- record the disposition in a closure receipt;
- avoid branch deletion until after remote archive is verified.

Stop condition: any open PR without recorded disposition.

### Phase 3 - Knowledge relocation

Promote retained documents by manifest rather than bulk copy:

- old path;
- old repo commit;
- old SHA-256;
- document class;
- authority/evidence status;
- new destination;
- new SHA-256;
- pointer/backlink policy.

Historical references inside signed/hash-bound artifacts must not be rewritten. New index documents may
point to the historical paths and archive locations.

Stop condition: any authoritative or evidentiary document moved without hash manifest and pointer.

### Phase 4 - Local archive

Create one canonical local archive root, proposed:

`C:\MyProjects\_archive\bc-external-audit-2026-08-01`

Contents:

- bare git bundle or mirror clone;
- manifest from Phase 1;
- per-dirty-worktree preservation bundles;
- PR disposition receipt;
- relocation receipt;
- restore instructions.

Clean registered worktrees may be removed through `git worktree remove` only after the archive root has
been verified. Non-worktree directories, if any, must be moved only after path resolution confirms the
target remains inside the intended archive root.

Stop condition: archive cannot reconstruct a dirty working copy or identify its originating HEAD.

### Phase 5 - Remote archive

Before archiving GitHub:

- final closure receipt is committed and pushed;
- archival tag exists, proposed `archive/2026-08-01`;
- PR dispositions are recorded;
- default branch contains a shutdown pointer;
- branch-protection/ruleset implications are understood;
- owner/admin explicitly authorizes archive.

Remote archive command is intentionally excluded from this packet. It should be run only after the
closure receipt cites the final pushed commit and tag.

### Phase 6 - Adjacent cleanup

Open separate packets for:

- KMS key lifecycle and signature-verification retention;
- `bc_audit_dev` / audit database evidence retention or decommission;
- environment variable and secret cleanup;
- GitHub App / `bc-auditor-app` permission review;
- CI/workflow shutdown;
- Codex skill or session-kit relocation.

These are adjacent work items because they may affect live checker/review capabilities that are not
retired by DEC-b7d74b.

## 7. Non-actions

This packet does not authorize:

- deletion of any `C:\MyProjects\bc-external-audit*` directory;
- `git worktree remove`;
- `gh repo archive`;
- PR closure or merge;
- branch deletion;
- KMS key disablement or deletion;
- database drop, schema drop, role revoke, or evidence deletion;
- rewriting historical artifact paths inside signed/hash-bound records.

## 8. Review questions

1. Are PRs to be individually disposed, or may stale pre-retirement PRs be closed under one shutdown
   record?
2. Should the canonical local archive root be `C:\MyProjects\_archive\bc-external-audit-2026-08-01`?
3. Should `AUDITOR-SESSION-KIT` move into `bc-docs`, remain as a Codex skill only, or both?
4. Should the retired remote remain named `bc-external-audit`, or should any rename happen before archive?
5. Should `bc-auditdochub` be created now as an empty/future repo, or deferred until architecture is
   accepted?

## 9. Recommended review disposition

Accept this plan for Phase 1 only: freeze and manifest. Phase 1 is non-destructive and will produce the
evidence needed to approve or reject the later cleanup phases without guessing.
