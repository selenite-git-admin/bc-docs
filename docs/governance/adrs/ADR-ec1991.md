---
uid: DEC-ec1991
title: "Demo documentation split: the estate's authority lives in bc-demo; bc-docs holds the platform's view of the demo and the rules on shared assets"
description: "Names, file by file, which demo documentation is authoritative in bc-demo and which in bc-docs; sets the placement rule (a fact that changes with the estate lives in bc-demo, a rule that binds the platform or the operator lives in bc-docs, bc-docs points and never copies); records that the Foundry ops UI on port 8600 is an on-demand tool, not a stack service."
status: decided
date: 2026-09-30T11:28:50.312Z
project: bc-demo
domain: docs
subdomain: docs/demo-estates
focus: documentation-placement
---

# Demo documentation split: the estate's authority lives in bc-demo; bc-docs holds the platform's view of the demo and the rules on shared assets

## Context

The demo estate is documented in two repositories, and each side already states part of the split. The bc-demo README (main c9711057) says: "Platform documentation lives in bc-docs (D234 single root). Estate-bound content and narrative ... live with the estate in this repo, and the operational runbook lives with the scripts it drives; neither is platform documentation." ADR DEC-40b510, decision point 6, says product documentation lives in bc-docs under the single root (DEC-2347a3, D234) and names `docs/implementation/demo-estate-simulator-requirements.md` as the authoritative requirements and disposition register. ADR DEC-1c5af4, decision point 4, fixes three layers: global (the Foundry engine and console under `tooling/`), source system (`ops/RUNBOOK.md`) and world (each run package). ADR DEC-39514f makes the typed Foundry model the one authority for a world, with the generated RUNBOOK, the ops UI, the QA portfolio and the build plan as projections. ADR DEC-8b17b1 (D561) holds the demo-estates doctrine.

No single document says which files on each side are authoritative and which are pointers, and the two sides have drifted. Verified on 2026-09-30 by the Demo controller: the requirements register that DEC-40b510 calls authoritative carries `authority: derived` in its frontmatter; `docs/operations/demo-operations.md` is `authority: authoritative` by frontmatter but opens with a banner declaring its premise (the apex tenant on a SAP reader chain) superseded, with its rebase tracked as TSK-892697; the demo world's generated `RUNBOOK.md` has been hand-edited since 2026-09-04 although its header says it is generated (TSK-2e4fed, TSK-f75d85); no bc-docs chapter mentions the next world (lc6), whose design lives only in bc-demo; and the barecount-devhub project instructions list port 8600 (the Foundry ops UI) in the port table beside the always-on services, while nothing listens on it and it is not a process-compose service (DevHub `src/lib/stack-services.js` registers it as an on-demand tool with its start command; the ops-UI README documents `python sources/odoo19ee/tooling/ops-ui/ops_ui.py`).

The controller operating model (bc-docs `docs/development/the-controller-operating-model.md`, Demo section) records the split as a design property ("Authority is split by design") and names deciding it formally as one of the Demo controller's first units. The Chief Controller assigned that unit on 2026-09-30.

## Decision

### What bc-demo is authoritative for

bc-demo is the authority for everything that changes when the estate changes. The following files carry that authority; each is `authoritative` in its own layer under DEC-1c5af4.

| Layer | Authoritative file or set | What it governs |
|---|---|---|
| Repository | `README.md` | The repository layout, the collection-of-demos model, and this split |
| Global (Foundry) | `sources/odoo19ee/foundry/` (`SCHEMA.md`, `worlds.py` with the capability tree, `LESSONS.csv`, `DESIGN-*.md`, `design/metric-coverage/STUDY-GOVERNANCE.md`) | The world model, the method, scope (the capability tree is the only place scope lives), and the reload-versus-rebuild rule |
| Source system | `ops/RUNBOOK.md`, `ops/aws/*RUNBOOK.md`, `ops/mac/*RUNBOOK.md` | Box-level serving of any Odoo demo: hosts, ports, containers, the one build rule (no raw SQL), the licence rules as applied on the box, moves |
| World | `sources/odoo19ee/demos/<world>/model/world-model.json`, the typed model (DEC-39514f) | Each world's declared scope, decisions and build order. `world-spec.yaml` and the decision sheets under `runpkg/stages/*/` are the model's import surface, and `stage.json` is what the generated RUNBOOK is projected from; none of them is authority on its own |
| World design | `sources/odoo19ee/demos/<world>/design/*` (the living registers) and program documents such as `LC6-PROGRAM.md` | Realism, compliance, join keys, roster, treasury, UI surface, metric coverage; the design of the next world |

Projections are never authority: the demo's generated `RUNBOOK.md`, the ops UI, the QA portfolio and the build plan are rendered from the model and the stage manifests (DEC-39514f) and are regenerated, never hand-edited.

### What bc-docs is authoritative for

bc-docs is the authority for what the platform and the operator must know regardless of which estate exists.

| Chapter | Authority | What it governs |
|---|---|---|
| `docs/operations/odoo-enterprise-subscription.md` | `authoritative` | The one Odoo Enterprise subscription: the licensed database, activation, the rules that keep the licence where it is. The licence is a shared asset of the company, not a property of one world |
| ADR DEC-8b17b1 (D561) | ADR | The demo-estates doctrine: few deep flagships, one per domain and geography, Odoo as the base, one install per estate |
| ADR DEC-40b510 (D566), DEC-39514f, DEC-1c5af4 and this record | ADR | The founding decision, the model-as-authority decision, the layering, and the split |
| `docs/implementation/demo-estate-simulator-requirements.md` | `authoritative` for the requirements and disposition registers it holds (DEC-40b510, point 6); its frontmatter is corrected to say so | What the simulator must do; the disposition of every requirement |
| `docs/implementation/demo-estate-module-coverage.md`, `demo-estate-metric-coverage.md`, `demo-estate-max-coverage-rescope.md`, `demo-estate-program-status.md` | `reference` (today `derived`, which DEC-e0a8ca maps to `reference`) | The platform's view of coverage and status, derived from the estate; never the place to change scope |
| `docs/development/the-controller-operating-model.md`, Demo section | `authoritative` | The Demo controller's charter |
| `docs/operations/demo-operations.md` | historical | The apex tenant on a SAP reader chain. Its premise is superseded; its rebase or retirement stays with the Docs controller (TSK-892697). The rebase's target is the placement rule below, not a copy of bc-demo content |

### The placement rule

1. A fact that changes when the estate changes lives in bc-demo: hosts, containers, ports, build steps, gates, world scope, design registers, the next world's programme.
2. A rule that binds the platform or the operator whatever the estate lives in bc-docs: the licence rules, the doctrine, the founding and layering decisions, the requirements register, the controller charter.
3. bc-docs points; it never copies. A bc-docs chapter that needs an estate fact names the bc-demo file that holds it. A bc-demo file that needs a platform rule names the bc-docs chapter that holds it. Neither side restates the other's content.
4. A new world (lc6 and after) is designed and documented in bc-demo. bc-docs records only what the platform observes of it (coverage, status) once it serves.
5. Where a document on either side disagrees with this record, the document is corrected, not this record.

### The Foundry ops UI and port 8600

The Foundry ops UI (`sources/odoo19ee/tooling/ops-ui/ops_ui.py`) is an on-demand local tool started by hand, not a service of the Mac stack: it has no process-compose entry, nothing listens on port 8600 between uses, and DevHub's Servers page registers it as an on-demand tool with its start command. DEC-e50b83 does not reserve 8600 (its dev-tools range is 4000 to 4099); this record is the source of the 8600 reservation, as an exception to the ranges DEC-e50b83 lists, until an amendment of the master port decision consolidates the table. The barecount-devhub project instructions' port table is corrected in the same change to say "on demand" with the start command, in the style of the port 8100 row.

### Consequences

- bc-demo `README.md` cites this record under its split paragraph.
- The frontmatter of `demo-estate-simulator-requirements.md` is corrected to `authoritative` (DEC-40b510, point 6) in the same pull request as this record.
- The Docs controller's rebase of `demo-operations.md` (TSK-892697) targets the placement rule.
- The four coverage and status chapters keep their `derived` value until DEC-e0a8ca's sweep maps it.
- The stale wording of the Foundry and Odoo rows on DevHub's Servers page is a DevHub controller task, recorded at this decision.
