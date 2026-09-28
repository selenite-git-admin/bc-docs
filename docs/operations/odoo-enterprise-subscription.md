---
id: odoo-enterprise-subscription
order: 30.6
title: "Odoo Enterprise Subscription: the Licensed Demo Database"
status: drafting
authority: authoritative
depends_on: [demo-operations]
governing_sources:
  - Operator decisions 2026-09-27/28 (Odoo demo box on AWS, on demand; one licence)
  - bc-demo ops/aws/U4-AWS-RUNBOOK.md (the move to AWS)
  - barecount-devhub artifacts/odoo-pilot/RUNBOOK-mfg-in-world-build.md §7 SETUP.5 (the activation recipe)
governing_adrs: []
errata_referenced: []
---

# Odoo Enterprise Subscription: the Licensed Demo Database

BareCount's demo source is an Odoo 19 Enterprise world. We hold **one** Enterprise subscription. Odoo attaches that subscription to **exactly one database**, identified by the database's UUID (`ir_config_parameter` key `database.uuid`), not by its name or host. This chapter records which database holds it, how it is activated, and what must never happen to it. It also records the 2026-09 incident that made this chapter necessary.

## 1. The licensed database

| Item | Value |
|---|---|
| Database | `v3_lc5` (the Kaveri Precision Components world) |
| `database.uuid` | `631391a2-a8aa-11f1-914a-ae2307712264` |
| Host | AWS EC2 `i-0944d13adbafaa542` (ap-south-1), **on demand**: `~/bc-stack/odoo.sh up/down/status` on the Mac |
| Activated | 2026-09-28; `database.expiration_date` 2027-08-22, `expiration_reason` renewal |
| Subscription code | AWS Secrets Manager `odoo_enterprise_subscription_id` (a JSON object; key `odoo_enterprise_subscription_id`). Never printed or logged |
| Internal users | **One** active internal user (the one-user rule) |

No other Odoo database may carry the subscription code or contact Odoo's licence servers.

## 2. What happened (2026-08 to 2026-09)

1. **2026-08-07:** the pilot database `pilot_ent` on the AWS box was activated with the code (run `20260807T050857Z`). Odoo bound the subscription to **that** database's UUID (expiry 2027-08-22).
2. **Later the same day:** `pilot_ent` was rebuilt by drop-and-create (run `20260807T173017Z`). A recreated database gets a **new UUID**, so the subscription stayed bound to a UUID that no longer existed. Activation of the rebuilt database was deferred and never done.
3. **2026-08 to 2026-09:** the other demo worlds (`rc10_full`, `v2rc9`, the `v3_kpc*` worlds, `v3_scratch`, and `v3_lc5` on the laptop) were never registered. The build steps instead **pinned `database.expiration_date` far into the future** (2030 in `runpkg/stages/07-company-config/steps/apply_config.py`, 2036 in `simulator/adapters/odoo19ee/provision.py`) to hide Odoo's expiry banner. That masked every unregistered database's real licence state (see §5).
4. **2026-09-27:** `v3_lc5` was moved to AWS and the eight old worlds were deleted. Activating `v3_lc5` with the code made Odoo's server answer with a **30-day trial and clear the code**, because the subscription was still bound to the August UUID. Our side had no record of which database held it. The network, the host and the code were all fine: the same code and recipe had worked on this same box in August.
5. **2026-09-28:** Odoo's subscription manager unlinked the old database **as a one-off goodwill gesture** ("he cannot help every time"). Re-running the activation bound `v3_lc5`: expiry 2027-08-22, reason renewal.

**Root causes:**
- an activated database was destroyed without first unlinking it;
- rebuild-by-recreate changes the UUID;
- no record said which database held the licence;
- expiry pinning hid the problem.

## 3. Activating (or re-activating) the licensed database

Programmatic. Odoo's UI path is unreliable. On the box, via SSM, with Odoo running:

1. Pipe the code from Secrets Manager straight into `ir_config_parameter` as `database.enterprise_code`. The instance role fetches it, the key is extracted by name, and it goes to `psql` through stdin (`COPY … FROM STDIN`). **Never** into a shell variable, argv, output or transcript.
2. Trigger the check-in **explicitly**: `odoo shell` → `env['publisher_warranty.contract'].update_notification(None)`, then `env.cr.commit()`. A module update (`-u base --stop-after-init`) does **not** trigger it.
3. **Proof is Odoo's write-back, not our write:** `database.expiration_date` must **change**, `database.expiration_reason` must **not** be `trial`, and `database.enterprise_code` must still be set. If Odoo cleared the code or returned `trial`, the subscription is bound elsewhere: **stop** and go to §4.
4. If Odoo sends the subscription owner a confirmation email, the operator approves it.

The scripts used on 2026-09-28 live in `~/bc-stack/odoo-move/` (`activate-v3lc5.sh`, `trigger-v3lc5.sh`, run with `box-run.zsh`).

## 4. Rules that keep the licence where it is

1. **Never drop and recreate the licensed database.** Moves and restores must keep its `database.uuid`: capture and restore preserve it; verify it after every restore against §1.
2. **Before retiring or replacing the licensed database,** the operator asks Odoo (the subscription manager) to **unlink it first**, and only then is the new database activated. This is a planned, rare event. Odoo has said it will not keep doing it as a favour.
3. **Copies of the licensed database** (rehearsal restores, clones) run with **crons off** (`--max-cron-threads=0`), **never** trigger `update_notification`, and are dropped after use. A copy shares the UUID and the code, so it must never phone home.
4. **Other Odoo databases** (test worlds, new builds) never receive the code and never contact Odoo's licence servers.
5. **Do not pin `database.expiration_date`** to hide the expiry banner. It misrepresents the licence state. An unregistered build is a short-lived test object, not something shown to a CXO. The licensed database shows no banner because it is genuinely active.
6. **Record every activation, unlink or UUID change** in §1 of this chapter, in the same change.

## 5. Open follow-up

- Remove the expiry pinning from the demo build steps (`apply_config.py` B3, `provision.py` `ensure_database_expiration`), so builds no longer misstate licence state. Tracked as a bc-demo task.
