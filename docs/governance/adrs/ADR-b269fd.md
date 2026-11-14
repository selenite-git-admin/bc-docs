---
uid: DEC-b269fd
title: "Demoed isolation-authority amendment: add bc_demo_prover (guarded proof-write surface) to DEC-89db41"
description: "Demoed isolation-authority amendment: add bc_demo_prover (guarded proof-write surface) to DEC-89db41"
status: decided
date: 2026-10-30T09:04:59.128Z
project: platform
domain: platform
---

# Demoed isolation-authority amendment: add bc_demo_prover (guarded proof-write surface) to DEC-89db41

## Context

No rationale recorded.

## Decision

Ratified by recorded operator grant 2026-10-30T09-01-20-016Z-62f0ef8b (text_sha256 62f0ef8b80eb18af63f7690f61a70b995b206ce6f1a5a0ebf70e7c3062ce44d7, TOTP, bc-exchange request 363, thread gen-74baaa). Amends DEC-89db41 (plane + isolation contract); DEC-89db41's other decisions are unchanged. Design accepted by Codex gen-74baaa-02. Enables the first build of the DEC-025bfc (D680) Demoed terminal.

AMENDMENT: DEC-89db41 literally defines demo-plane access as the SELECT-only bc_demo_runtime guarded transaction (RT(demo)). This amendment ADDS a SECOND demo-plane principal, bc_demo_prover, a LOGIN NOINHERIT owns-nothing login that:
- reaches ONLY the demo schema; NO CONNECT to any tbc_* tenant database; no reach to platform definition schemas or tenant schemas; owns nothing;
- holds EXECUTE only on a bounded, provisioned ALLOWLIST of demo proof-write SECURITY DEFINER routines (owned by bc_schema_owner, pinned search_path, PUBLIC EXECUTE revoked);
- is never acquired through RT(demo); its guarded transaction establishes session_user=bc_demo_prover + database + exact schema reach {demo} as the FIRST statement after BEGIN, before invoking the routine (inside the routine current_user is the owner, so it cannot serve as the caller-identity check).

bc_demo_runtime is UNCHANGED: SELECT-only, the Demoed read-time projection reader. The D575 isolation property is preserved and generalized, not weakened: no-tenant-reach for bc_demo_prover is proven three ways (no direct privilege path, no owner-rights path, synthetic-only governed contents); owner-only DDL and synthetic-lineage checks preserved.

ADOPTION GATES (unchanged by this amendment): a Codex isolation audit of bc_demo_prover before adoption; the bc-db forward migration implementing bc_demo_prover + the demo evaluation-evidence substrate + the SECURITY DEFINER routines is DB-change-gated (operator table/change/reason + grant-gated live apply; owner/grant-faithful restore proof incl served-login deny vectors); the bc-core demo-commit service + read-time projection are reviewed units; serve-move + first live proof act gated; positive AR Balance projection + known-hollow negative required before any Demoed label. No migration apply, build, or live act is authorized by this DEC.

FOUNDATION: design act (DEC-c48b0f), repair location A/C (admission principal + binding) on the demo plane's isolation contract; isolation (D575) preserved. This is the authority precondition for the DEC-025bfc proof-write surface.
