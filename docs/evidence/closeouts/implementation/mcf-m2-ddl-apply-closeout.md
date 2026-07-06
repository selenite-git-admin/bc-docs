---
uid: mcf-m2-ddl-apply-closeout
title: MCF M2 Identity Substrate — Live DDL Apply Closeout
description: Closeout for the MCF M2 Identity Substrate live DDL apply against bc_platform_dev on 2026-05-26. Applied docker/redesign/04-mcf-substrate.sql (DDL pinned at bc-core PR #101 / 92a9056; sha256 67289dbe7c336d9e2eff1ef937ad56088aa30dda8aee90f3dcb6f61d1eb86c82) under explicit operator approval per CLAUDE.md Database Change Protocol. Dry-run all 6 preconditions PASS; psql exit 0; post-apply verifier all 12 checks PASS. mcf schema + 5 expected tables present; column counts match design; no FK to concept_registry.* or legacy contract.metric_contract*; tables empty. Evidence artifacts committed to bc-core via PR #102. Operational observations captured (psql client path, bc-postgres MCP schema cache). M3 stays closed; no MCF metric contracts created.
status: draft
date: 2026-05-26
project: bc-docs
domain: contracts
subdomain: catalog
focus: mcf-m2-apply-closeout
---

# MCF M2 Identity Substrate — Live DDL Apply Closeout

## 1. What landed

The MCF M2 Identity Substrate DDL was applied live against `bc_platform_dev` on **2026-05-26**. The substrate (5 tables + indexes + comments under the new `mcf` schema) is now physically present and structurally validated. This caps the BCF-to-MCF Step 4 readiness handoff (`bc-docs-v3 1d73308` §9.4 recommendation: "Open MCF M2 DDL apply under Database Change Protocol").

| | Value |
|---|---|
| DDL source | `bc-core/docker/redesign/04-mcf-substrate.sql` |
| Pinned at | bc-core PR #101 / commit `92a9056` (HEAD = origin/main) |
| DDL sha256 | `67289dbe7c336d9e2eff1ef937ad56088aa30dda8aee90f3dcb6f61d1eb86c82` |
| Target DB | `bc_platform_dev` (port 5435; bc-postgres container, postgres 17.8) |
| Authority | ADR DEC-c3e57f / D422 + M2 DBCP design doc |
| Operator approval | explicit "Approved. Proceed..." in conversation per CLAUDE.md Database Change Protocol |

## 2. Apply outcome

| Step | Tool | Outcome |
|---|---|---|
| Dry-run | `node scripts/mcf-m2-dry-run.mjs` | **exit 0** — 6/6 preconditions PASS (legacy 3 tables present, mcf schema absent, mcf tables absent, referenced schemas present, candidate JSONB CHECK enum complete, DDL parse + counts + hash) |
| Live apply | `psql $env:DATABASE_URL -v ON_ERROR_STOP=1 -f docker/redesign/04-mcf-substrate.sql` | **exit 0** — 33 statements executed (1 CREATE SCHEMA + 1 COMMENT ON SCHEMA + 3 COMMENT ON TABLE + 5 CREATE TABLE + 4 UNIQUE INDEX + 9 INDEX + 10 COMMENT ON COLUMN) |
| Post-apply verify | `node scripts/mcf-m2-post-apply-verification.mjs` | **exit 0** — 12/12 checks PASS |

### 2.1 Post-apply 12-check summary (all PASS)

1. `mcf` schema present
2. Exactly 5 mcf tables present: `metric_contract`, `metric_contract_version`, `metric_variable_binding`, `metric_filter_clause`, `metric_computed_dimension_ref`
3. Column counts match design: 17 / 15 / 13 / 9 / 9
4. Hash columns nullable (M2 discipline; NOT NULL added by M3 lifecycle gate later)
5. Partial UNIQUE on `identity_tuple_hash` with `WHERE archived_at IS NULL AND identity_tuple_hash IS NOT NULL` predicate
6. 17 closed-enum CHECK constraints present
7. `candidate_source_ref_json.source_type` CHECK with full enum (`seed_metric` / `metric_definition` / `operator_direct` / `legacy_metric_contract` / `other`)
8. No FK from `mcf.*` to legacy `contract.metric_contract*` or `metric.metric_binding`
9. No FK from `mcf.*` to `concept_registry.*` (service-level validation per design §12)
10. `COMMENT ON TABLE` on 3 legacy tables mentions D422 + HISTORICAL
11. `COMMENT ON COLUMN` on 10 M3/M7/M8/M9-owned placeholders mentions D422
12. All 5 `mcf.*` tables empty (substrate-only apply; no row writes)

## 3. Evidence

Audit artifacts committed to bc-core via [PR #102](https://github.com/selenite-git-admin/bc-core/pull/102) under `scripts/audit-output/`:
- `mcf-m2-dry-run-2026-05-26T12-58-07-935Z.summary.md` + `.precondition.jsonl` + `.planned-sql.sha256.txt`
- `mcf-m2-post-apply-2026-05-26T13-01-55-568Z.summary.md` + `.evidence.jsonl`

The post-apply summary contains the full per-check JSON for downstream audit. The DDL hash file (`.planned-sql.sha256.txt`) pins what was applied for future drift detection.

## 4. Operational observations

These are not captured in the audit artifacts and warrant preservation for future sessions.

### 4.1 psql client not on PATH

Local PATH did not contain `psql`. Discovered local install at `C:\Program Files\PostgreSQL\18\bin\psql.exe` (psql 18 client connecting to postgres 17.8 server via port 5435 — compatible across this major-version gap for basic DDL).

For future apply gates: either add the psql install directory to PATH, or invoke psql via its absolute path through PowerShell's call operator (`&`). The CLAUDE.md Dev Service Management section may want a note that psql is locally installed at `C:\Program Files\PostgreSQL\18\bin\psql.exe`.

### 4.2 bc-postgres MCP schema-cache lag

`bc-postgres` MCP `pg_server_info` shows `schemas: [concept_registry, contract, master, metric, runtime, source]` AFTER the apply — the newly-created `mcf` schema does NOT appear in this list. However:

- Direct `pg_query` against `information_schema.schemata WHERE schema_name = 'mcf'` correctly returns 1 row.
- The 5 mcf tables are visible via `pg_query` against `information_schema.tables WHERE table_schema = 'mcf'`.

Inference: the MCP caches the schema-discovery list at process start. Restarting the MCP host (Claude Code session relaunch or equivalent) should refresh the list. **Not a substrate issue**; the schema is real and queryable.

For future MCF authoring sessions: if `mcf` does not appear in `pg_server_info.schemas`, restart the MCP host before relying on schema-allowlist behavior against `mcf.*` tables. Add `mcf` to `PGMCP_SCHEMAS` in `barecount-devhub/.claude/settings.json` if scripted bc-postgres reads against `mcf.*` are needed.

### 4.3 PowerShell vs Bash for psql apply

The apply command was specified in PowerShell syntax (`$env:AWS_PROFILE = 'barecount'; psql $env:DATABASE_URL ...`). The PowerShell tool was used directly. `bc-core/.env` was sourced inline by reading `DATABASE_URL` and `AWS_PROFILE` lines and `Set-Item -Path "env:$name" -Value $value`.

For future apply gates: PowerShell with explicit `$env:` reads of `.env` works cleanly; the `Get-Content .env | Where-Object {...}` + `Set-Item -Path "env:..."` pattern is reusable.

## 5. What stays closed

- **MCF M3** — not opened. M3 lifecycle substrate (revision + supersession + immutability triggers) is the next gate after M2 apply; awaits operator authorization.
- **MCF metric contracts** — none created. The 5 mcf.* tables are empty per check #12.
- **B6-v2 retrofit** — not opened. No hard trigger from this apply.
- **MCF M2 DDL further changes** — none. The merged PR #101 design held; no amendments were needed in dry-run or post-apply.
- **bc-postgres MCP write access** — unchanged. `allow_write: false` confirmed across this session. The psql apply used the operator's own DATABASE_URL credential, not bc-postgres MCP.

## 6. Step 4 arc summary — now complete from BCF authoring to MCF substrate

| Step | Closeout / Artifact | Date |
|---|---|---|
| Pre-execution plan | bc-docs-v3 `248b004` | 2026-05-26 |
| Initial execution | bc-docs-v3 `3b4c71b` | 2026-05-26 |
| Publication-confirm | bc-docs-v3 `2d9710e` | 2026-05-26 |
| Posted-amount resolution | bc-docs-v3 `1ca8ead` | 2026-05-26 |
| bc-ai panel prompt fix | bc-ai `7ff8446` (PR #18) | 2026-05-26 |
| CI · invoice id resolution | bc-docs-v3 `63dc112` | 2026-05-26 |
| BCF-to-MCF readiness handoff | bc-docs-v3 `1d73308` | 2026-05-26 |
| **MCF M2 DDL apply** | bc-docs-v3 (this doc) + bc-core PR #102 | **2026-05-26** |

Eight closeouts on a single day caps the Step 4 BCF enrichment + readiness + MCF substrate landing. The 8 of 10 representative metrics from the readiness handoff `1d73308` §6 are now bindable AND have substrate to be authored into.

## 7. Recommended next gate

Per the readiness handoff `1d73308` §9 + §10, the next operator-controlled gates are:

1. **MCF M3 — lifecycle substrate** (substrate-only). Adds `mcf.metric_contract_revision` + `mcf.metric_supersession` + immutability triggers + NOT-NULL transition rules on hash columns when `governance_state_code` reaches `approved`. Requires a separate operator-authorized Database Change Protocol session. **NOT OPENED in this session.**
2. **Step-4-bis enrichment** for Metrics 3 + 6 (parallel workstream; independent of MCF M3).
3. **Continue monitoring** the bc-ai prompt fix (PR #18) — two F4-v2 createCharacteristic runs since merge, both clean.

This closeout does NOT open any of these.

## Document verification

- **Apply event captured** — DDL source, sha256, target DB, authority, operator approval pattern.
- **All three apply steps recorded** with exit codes — dry-run / live psql / post-apply verifier all exit 0.
- **All 12 post-apply checks PASS** — itemized in §2.1.
- **Operational observations preserved** (§4) — psql client path, bc-postgres MCP cache lag, PowerShell .env pattern.
- **No code changes, no further DDL, no row writes.** This doc only.
- **Closed gates restated** (§5) — M3 + MCs + B6-v2 + DDL amendments + bc-postgres write all stay closed.
