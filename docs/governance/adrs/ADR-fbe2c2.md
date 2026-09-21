---
uid: DEC-fbe2c2
title: "bc-core-dashboard retirement — superseded by bc-admin (backfill)"
description: "Backfill decision record (SI-B-1 / D619) for the bc-core-dashboard project retirement, which occurred 2026-07-07 with no ADR. Retired because superseded by bc-admin, and the realization that bc-core (the API) does not need its own dashboard surface. Recorded under attributed operator ratification (2026-09-21) as the original ARCHIVED.md is absent."
status: decided
date: 2026-09-21T11:16:39.109Z
project: bc-core
domain: platform
subdomain: repo-lifecycle
focus: retirement
---

# bc-core-dashboard retirement — superseded by bc-admin (backfill)

## Context

`bc-core-dashboard` was a standalone development dashboard repo for the bc-core API. It was **retired on 2026-07-07** and archived to `C:\MyProjects\_archived-repos\bc-core-dashboard-2026-07-07` (freeing port 4100). No decision record was created at the time, and the archive's `ARCHIVED.md` is **absent**, so this ADR **backfills** the retirement under **attributed operator ratification (2026-09-21)** rather than a recovered original authority. This backfill was surfaced by the Structural Integrity program (DEC-027ef6/D619), package SI-B-1 — "no ADR was found in the searched corpus" for this retirement.

The only prior ADR mentions are contextual and pre-date the retirement: `DEC-890417` (pm2 dev-service management — itself **superseded by DEC-9b23a7**) and `DEC-e50b83` (port reservation) list bc-core-dashboard as an *active* service.

## Decision

The **bc-core-dashboard project is retired**, effective **2026-07-07** (historical; recorded 2026-09-21).

**Rationale — operator-ratified (retrievable source).** The original authority/`ARCHIVED.md` is unrecoverable, so this record rests on operator ratification captured in session **SES-2b96b2 (2026-09-21)**, verbatim: *"The Core Dashboard was retired because it was superseded by bc-admin. And a realization that core (API) won't need a dashboard as such."* From that:
1. It was **superseded by bc-admin** — administrative/observability surfaces live in the bc-admin console.
2. **bc-core (the API) needs no dashboard surface of its own** — not part of the architecture.

**Scope of this record.** The repo is archived (read-only) at the path above and its port-4100 binding is freed. Two **pending** annotations follow from this retirement and are **not** yet applied by this ADR: a dated dashboard-only cross-reference to this ADR on the `DEC-e50b83` port-4100 entry (which still lists it) and on the `DEC-890417` dashboard mention. This ADR does **not** supersede or alter those decisions' port-reservation or pm2 policy (DEC-890417 is itself superseded by DEC-9b23a7; follow that successor for pm2 policy). Historical (2026-07-07) and record (2026-09-21) dates are both preserved.

## Consequence

The platform's admin/observability story is single-homed in bc-admin. The bc-core-dashboard repo remains addressable as an archive for historical reference, and its port-4100 binding is freed. This ADR records **retirement policy**; it does **not** assert an exhaustive runtime/dependency audit — any residual reference is inventoried under the pending annotations above.
