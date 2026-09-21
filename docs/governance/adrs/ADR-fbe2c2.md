---
uid: DEC-fbe2c2
title: "bc-core-dashboard retirement — superseded by bc-admin (backfill)"
description: "Backfill decision record (SI-B-1 / D619) for the bc-core-dashboard project retirement, which occurred 2026-07-07 with no ADR. Retired because superseded by bc-admin, and the realization that bc-core (the API) does not need its own dashboard surface. Recorded under attributed operator ratification (2026-09-21) as the original ARCHIVED.md is absent."
status: decided
date: 2026-09-21T11:16:39.109Z
project: platform
domain: platform
subdomain: repo-lifecycle
focus: retirement
---

# bc-core-dashboard retirement — superseded by bc-admin (backfill)

## Context

See decision text below.

## Context

`bc-core-dashboard` was a standalone development dashboard repo for the bc-core API. It was **retired on 2026-07-07** and archived to `C:\MyProjects\_archived-repos\bc-core-dashboard-2026-07-07` (freeing port 4100). No decision record was created at the time, and the archive's `ARCHIVED.md` is **absent**, so this ADR **backfills** the retirement under **attributed operator ratification (2026-09-21)** rather than a recovered original authority. This backfill was surfaced by the Structural Integrity program (DEC-027ef6/D619), package SI-B-1 — "no ADR was found in the searched corpus" for this retirement.

The only prior ADR mentions are contextual and pre-date the retirement: `DEC-890417` (pm2 dev-service management — itself **superseded by DEC-9b23a7**) and `DEC-e50b83` (port reservation) list bc-core-dashboard as an *active* service.

## Decision

The **bc-core-dashboard project is retired**, effective **2026-07-07** (historical; recorded 2026-09-21). Rationale (operator-ratified):
1. It was **superseded by bc-admin** — administrative and observability surfaces for the platform live in the bc-admin console.
2. **bc-core (the API) does not need its own dashboard surface**; a dedicated core dashboard is not part of the architecture.

The repo is archived (read-only) at the path above; port 4100 is freed (already reflected in the DEC-e50b83 port table).

**Scope of this record.** This ADR annotates **only** the bc-core-dashboard **dashboard mention** in DEC-890417 and DEC-e50b83. It does **not** supersede or alter those decisions' pm2 or port-reservation policy (DEC-890417 is already superseded by DEC-9b23a7; follow that successor for pm2 policy). Historical effective date (2026-07-07) and this record date (2026-09-21) are both preserved.

## Consequence

The platform's admin/observability story is single-homed in bc-admin. The bc-core-dashboard repo remains addressable as an archive for historical reference; no live service, port, or dependency remains.
