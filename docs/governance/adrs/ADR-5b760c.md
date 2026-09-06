---
uid: DEC-5b760c
title: "QA enforcement consolidates into per-repo CI; DevHub is the sole NC authority; bc-qa repo retires and archives"
description: "QA enforcement consolidates into per-repo CI; DevHub is the sole NC authority; bc-qa repo retires and archives"
status: decided
date: 2026-08-24T03:20:51.650Z
project: bc-qa
domain: development
subdomain: qa-tooling
focus: governance
---

# QA enforcement consolidates into per-repo CI; DevHub is the sole NC authority; bc-qa repo retires and archives

## Context

No rationale recorded.

## Decision

Per-repo CI becomes the ONLY QA enforcement home; the cross-repo audit mechanism retires; the bc-qa repo archives. Supersedes no ADR: the bc-qa-as-own-repo arrangement was never separately decided — devhub CLAUDE.md mis-cites DEC-ee6018 for it, but DEC-ee6018 is the Power of Ten coding rules, which REMAIN fully in force (status: implemented) and continue to be enforced through @barecount/eslint-config from its new home. This decision changes where QA runs, not what QA requires. Evidence basis: the first-ever compliance-gate run against bc-core (2026-08-24, SES-adfc8e) — executed once in the mechanism's 5-month life — returned a verdict dominated by defects in the gate itself: the BLOCK-severity forbidden-vocab check was vacuous (scanned 7 nonexistent directories, never touched src/boundary, masking ~156 real hits), the only BLOCK was two false positives (the D575 freeze-confirmatory test and the envelope-import detector flagged as freeze violators), the persisted report kept only a 25-line summary, and the "centralized" file NC register had never been written by the tooling (NCs live in the DevHub DB). Five NCs: cb5589, 95ece3, bdb43e, e886b3, 04b0bb. Meanwhile the QA that works — eslint with @barecount/eslint-config (Power of Ten), typecheck, the full test suite, the column-name gate, the toolchain doctor — runs in bc-core CI on every push. Demote-ceremony applied to QA: a gate that runs on every push beats an audit that runs never. DISPOSITIONS: (1) each repo's CI is its QA enforcement authority; severity policy lives in each repo's own lint/test config — gate-config.json dissolves; (2) the DevHub database is the single NC authority; audits/nc-register.json is retired (resolves NC-04b0bb); (3) @barecount/eslint-config SOURCE moves to bc-core tools/eslint-config, published to CodeArtifact under the unchanged package name — consumers (bc-admin, bc-portal, devhub, bc-sdg) are unaffected; (4) the two unique checks port to bc-core as vitest-native architecture tests: frozen-imports (with frozen-registry.json moving in-repo beside the code it freezes, import-specifier parsing, refusal-test exemption class — resolves NC-95ece3) and forbidden-vocab (scanning src/boundary + src/registry/readers, failing closed when zero files scanned, materialization carve-out — resolves NC-cb5589); (5) the shell audit layer, compliance gate, reports directory, nc-manage.sh, and hook templates retire with the repo (in-repo pre-commit hooks already installed keep working; optional convenience, never authority); (6) check-chain-invariants.sh is preserved by the archive and its logic re-homes under the chain-invariants track when that track needs it; (7) the bc-qa repository is archived: ARCHIVED.md pointer, GitHub archive flag, local working copy moved to _archived-repos. Execution order is coverage-gap-safe: port PR to bc-core first (review flow), archive after the source is copied.
