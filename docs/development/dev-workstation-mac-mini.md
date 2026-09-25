---
id: dev-workstation-mac-mini
order: 43.5
title: "Development Workstation: Mac Mini and Laptop"
status: drafting
authority: authoritative
depends_on: [developer-experience, devhub]
governing_sources:
  - Developer Experience
  - DevHub
governing_adrs:
  - DEC-e50b83 (D046 — Port reservation table)
  - DEC-ecd55c (Credentials in AWS Secrets Manager)
  - DEC-e39ed3 (AWS naming and tagging convention; `sct` domain)
errata_referenced: []
---

# Development Workstation: Mac Mini and Laptop

How BareCount's local development environment is split between the **Mac Mini** and the **Windows laptop**: what runs where, how to use it every day, how to maintain it, and what to do when something breaks.

Set up on 2026-09-25 (DevHub session SES-f3d537). Read this before changing anything on either machine.

---

## 1. At a glance

| | Mac Mini (always on) | Windows laptop |
|---|---|---|
| Role | BareCount's development server | Your screen, and other projects |
| Runs for BareCount | Postgres, Redis (Docker via Colima). **Step 2, not yet:** DevHub, bc-core, bc-admin and bc-portal (process-compose), and the Claude sessions | Codex (the auditor); a browser for the BareCount apps. **Until step 2:** Claude sessions, DevHub and the app servers still run here, pointed at the Mac's database |
| Other projects | none | thecakit, accountant-tools, skf, and the Odoo demo world (for now) |
| Reached at | cable `10.10.10.2`; Tailscale `100.64.129.39` (`macmini`) | cable `10.10.10.1`; Tailscale `100.71.89.101` (`anant-zbook`) |

**Move status (2026-09-25):**
- **Step 1, done:** Postgres and Redis live on the Mac. All laptop consumers point at it: bc-core, the Claude MCP helper, and Codex's auditor.
- **Step 2, planned:** DevHub, the app servers and the Claude sessions move to the Mac.

---

## 2. Machines and access

### Mac Mini
- Apple M2 Pro, 16 GB RAM, macOS Sequoia, 460 GB disk.
- **Accounts:**
  - **`anant`** is the development account (administrator). All BareCount work runs here.
  - `amrutakulkarni` is a family member's everyday account. **Never touch it.** Remote Login (SSH) is restricted to `anant`.
- **Power:**
  - Never sleeps (`pmset sleep 0`) and restarts after a power cut (`autorestart 1`).
  - FileVault is off, so it boots without anyone at the screen.
- **After a reboot:** Tailscale starts at boot. **Automatic login for `anant` is on**, so Colima, the containers and the relays come back by themselves about 1 minute after boot. Reboot test passed on 2026-09-25; see §9.1.

### Network
There are two ways to reach the Mac. Use the cable whenever you're at the desk.

| Route | Mac address | SSH name (laptop `~/.ssh/config`) | Speed | Use for |
|---|---|---|---|---|
| **Direct cable** (factory Cat6 through TP-Link TL-SG105E switch) | `10.10.10.2` | `macmini` | under 1 ms | everything at the desk, especially database traffic |
| **Tailscale** (private tailnet `tail9ffd71.ts.net`, operator's Selenite Google login) | `100.64.129.39` | `macmini-ts` | 10–120 ms | working away from the desk |

- **Cable addresses** are set by hand: laptop Ethernet `10.10.10.1/24`, Mac `10.10.10.2/24`, no gateway. Internet stays on Wi-Fi.
- **Home Wi-Fi does not connect the two machines:** it's the same network name, but they can't see each other. Don't rely on it.
- **At the desk, Tailscale** routes through the home router instead of the cable, so it's slower and jittery. Use the cable address there.
- **Tailscale on the Mac** runs as a boot-time system service, and its key expiry is **disabled**.
- **SSH key:** laptop `~/.ssh/macmini` (no passphrase), installed in the Mac's `anant` account.

---

## 3. Everyday use

### Start / stop BareCount on the Mac
Everything lives in `~/bc-stack/` on the Mac. See `~/bc-stack/README.md` for the port list.

| Task | Command (on the Mac, or `ssh macmini '…'` from the laptop) |
|---|---|
| Start the database and Redis (normally already running) | `~/bc-stack/up.sh` |
| See or manage containers (status, logs, restart) | `lazydocker` |
| Start the app servers (DevHub + bc-core; front ends start off) | `~/bc-stack/servers.sh up` |
| Dashboard for the app servers (logs, restart; `q` leaves it running) | `~/bc-stack/servers.sh ui` |
| Start or stop one server | `~/bc-stack/servers.sh start bc-admin` · `… stop bc-admin` |
| List servers and their state | `~/bc-stack/servers.sh ps` |
| Stop all app servers (containers keep running) | `~/bc-stack/servers.sh down` |

bc-core on the Mac starts with **`npm run start:dev:aws`**. That loads its secrets from AWS (§5); the Mac's `.env` holds only non-secret settings.

### Open bc-admin / bc-portal in the laptop browser
The Mac's firewall blocks the app ports from the network (§6). Use one SSH tunnel, then browse to `localhost` on the laptop:
```
ssh -N -L 3010:localhost:3010 -L 3000:localhost:3000 -L 3100:localhost:3100 macmini
```
- bc-admin: `http://localhost:3010`
- bc-portal: `http://localhost:3000`
- bc-core: `http://localhost:3100/api/health`

Cognito sign-in works unchanged, because the app still sees `localhost`. Away from the desk, use `macmini-ts` instead of `macmini`.

### Claude on the Mac
- The Claude desktop app is installed on the Mac, signed in as `anant`, with **Remote Control** on.
- **Drive sessions from anywhere:** from the laptop's Claude app, claude.ai/code, or the phone.
- **Cost:** Remote Control of a Mac session counts against the normal Max plan limits. It does **not** use cloud-session credits. The Mac must be awake with the Claude app running.
- **Memory:** Claude's BareCount memory is in `~/.claude/projects/-Users-anant-MyProjects-barecount-devhub/memory/`. It was copied from the laptop without `credentials_cognito.md`, and passwords were redacted.

### Working away from the desk (until step 2)
The laptop's `bc-core/.env` points at the **cable** address `10.10.10.2`, which only works at the desk. When away, change the host in `DATABASE_URL`, `TENANT_DATABASE_URL`, `BC_AUDIT_EXCHANGE_DATABASE_URL` and `REDIS_URL` to `100.64.129.39`, and change it back when you return. After step 2 this goes away, because bc-core and its database sit on the same machine.

---

## 4. Where everything is

### Ports (port reservation table, DEC-e50b83 / D046)
| Service | Mac listens on | Reached from the laptop |
|---|---|---|
| Postgres 17.11 (`bc-postgres`) | 127.0.0.1:5435 | `10.10.10.2:5435` / `100.64.129.39:5435`, via socat relays |
| Redis 7.4.7 (`bc-redis`) | 127.0.0.1:6379 | `10.10.10.2:6379` / `100.64.129.39:6379`, via socat relays |
| DevHub | 127.0.0.1:4000 (`HOST=127.0.0.1`, devhub#22) | relays to be added at step 2 |
| bc-core | :3100 (all interfaces; **firewall-blocked**) | SSH tunnel |
| bc-admin / bc-portal | localhost:3010 / localhost:3000 (Vite) | SSH tunnel |
| process-compose control | unix socket `~/bc-stack/pc.sock` (no TCP port) | only from the Mac |

### Files on the Mac (`~/bc-stack/`)
| File | Purpose |
|---|---|
| `README.md` | the port list |
| `up.sh` | Docker services: bc-core's `docker-compose.yml` plus `mac-ports.yml` (127.0.0.1-only ports, `restart: unless-stopped`), compose project `bc-core` |
| `install-relays.sh` | creates the four launchd relays: `com.barecount.relay-{5435,6379}` on the cable, and `com.barecount.relay-ts-{5435,6379}` on Tailscale |
| `process-compose.yaml`, `servers.sh` | the app servers |
| `firewall.sh` | macOS firewall setup (§6) |
| `health.sh` | one-command health check (§9.1): exit 0 = ALL OK |
| `logs/` | relay and process-compose logs |

### Settings files
- **Mac `~/.zprofile`:** Homebrew path; `BC_*_PATH` overrides (these replace DevHub's `C:/MyProjects` Windows fallbacks); `BC_DEV_SECRETS_PROFILE=default`; `AWS_REGION`; `DOCKER_HOST` pointing at Colima.
- **Mac `~/MyProjects/bc-core/.env`:** 29 non-secret settings. `AWS_PROFILE=default`.
- **Laptop `bc-core/.env`:** database and Redis URLs point at `10.10.10.2`. Pre-switch backups are in `%USERPROFILE%\.barecount-env-backups\`, **outside every repo**. Never keep `.env` backups inside a repo.
- **Laptop `%USERPROFILE%\.wslconfig`:** `memory=4GB` (was 8 GB).

---

## 5. Secrets and AWS access

- **App secrets:** bc-core's dev secrets live in **AWS Secrets Manager**, not in `.env` files. The secret is `bcp-dev-aps1-sct-secret` (bc-infra stack `bcp-dev-aps1-sct`, merged bc-infra#30), and it holds 9 names: the AI provider API keys and the service/test passwords.
  - **Loading:** `npm run start:dev:aws` (bc-core#819) loads them at startup. A variable that's already set in the environment wins. Values are never printed.
  - **Adding or changing a secret:** operator-run, on the laptop:
    - dry run: `npm run dev-secrets:fill -- --profile default`
    - write: `npm run dev-secrets:fill -- --profile default --apply`

    It reads `.env` exactly as bc-core does, writes privately, and verifies the read-back.
  - **Vendor admin keys** (`ANTHROPIC_ADMIN_KEY`, `OPENAI_ADMIN_KEY`) are **not** in AWS. They stay only on the laptop.
- **AWS access:** both machines currently use the operator's long-lived **`default`** key (IAM admin). On the Mac, only the `[default]` block was copied, into a file only `anant` can read.
  - This is an **operator decision (2026-09-25)**, made because the AWS console sign-in (IAM user + passkey MFA) was failing.
  - **The intended setup is already deployed but unused:** short-lived `aws login` sessions plus the MFA-only workstation role `bcp-dev-aps1-sct-role` (profiles `bc-login` / `bc-dev` exist on both machines). Switch to it once the console sign-in works. Open follow-up.
- **Package registry (CodeArtifact) login** lasts 12 hours. When `npm install` returns 401/403, run on the Mac:
  ```
  aws codeartifact login --tool npm --domain barecount --repository npm-mirror --region ap-south-1
  ```
  On the laptop, run `npm run codeartifact:refresh` in barecount-devhub.

---

## 6. Security on the Mac

- **macOS firewall on**, with stealth mode on, and automatic allowing of downloaded signed software **off**.
  - **Allowed** to accept outside connections: `socat1` (relays), `tailscaled`, and Apple built-ins such as SSH and Screen Sharing.
  - **Blocked:** `node` and `python3`.
  - **Verified:** a Node server on 0.0.0.0 cannot be reached from the laptop over either route.
- **Nothing listens on Wi-Fi.** Containers publish on 127.0.0.1 only. The relays bind only to the cable and Tailscale addresses. DevHub binds to 127.0.0.1.
- **Colima publishes container ports on every network by default.** Add containers only through `up.sh` / `mac-ports.yml`, never with a plain `docker run -p`.
- **When macOS asks "allow incoming connections?"** for anything other than socat or Tailscale, click **Deny**.

---

## 7. The database

- **Location:** the platform Postgres (`bc_platform_dev`, tenant databases, `bc_sdg`, `bc_audit_dev`) lives on the Mac. Cluster `system_identifier` **7689410286420172840**; the laptop's old cluster was 7619260324391063586.
- **Hand-off evidence:** 477/477 tables identical, ledger fingerprints identical. See `barecount-devhub/artifacts/infra/db-cluster-handoff-laptop-to-macmini-2026-09-25.md`.
- **Rollback:** the laptop's old containers are stopped, with their volumes kept until **2026-10-09**. To roll back:
  1. Restore the `.env` backups.
  2. Run `docker compose start postgres redis` in `C:\MyProjects\bc-core`.
  3. Carry across any writes made on the Mac since the move.
- **Taking a copy** (read-only on the source):
  ```
  ssh macmini 'DOCKER_HOST=unix://$HOME/.colima/default/docker.sock /opt/homebrew/bin/docker exec bc-postgres pg_dumpall -U barecount' > dump.sql
  ```

---

## 8. The laptop side

- **WSL memory cap:** 4 GB (`.wslconfig`). Real use is about 1 GB; the rest is Linux file cache.
- **After `wsl --shutdown` or a Docker Desktop problem:**
  1. **Quit** Docker Desktop from the taskbar icon, then start it again.
  2. **Never** click "Reset to factory defaults": it deletes every container, volume and image.
  3. If the "WSL integration with distro Ubuntu" error appears, **Skip** is safe. The Foundry does not need it: it drives Docker from Windows through the `bc-localhost-exec:1` helper.
- **Restart behaviour:**
  - Odoo containers restart by themselves.
  - thecakit and accountant-tools Postgres do **not** (`restart=no`). Run `docker start thecakit-foundation-postgres-1 accountant-tools-devhub-postgres-1`.
- **`localhost` on the laptop can reach a hanging WSL relay on IPv6 (`::1`).** Prefer `127.0.0.1` or the Mac's addresses in connection strings.

---

## 9. Maintenance

### 9.1 After a reboot or power cut
The Mac restarts by itself (`autorestart 1`), and Tailscale starts at boot. **Automatic login for `anant` is on** (operator decision, 2026-09-25; possible because FileVault is off). The trade-off: anyone with physical access to the Mac gets the `anant` session. Colima (the `sh.brew.colima` login agent), the containers (`restart: unless-stopped`) and the four relays (launchd agents) then start by themselves.

**Reboot test, 2026-09-25: passed.** No one touched the Mac.
- SSH answered about 30 s after the reboot.
- The health check was ALL OK about 50 s after boot.
- Cluster sysid unchanged.

In the first minute Colima's login agent restarted Docker once, so allow **about 1 minute** before relying on the database.

The app servers (process-compose) are **not** started at login. Start them with `~/bc-stack/servers.sh up`.

After any reboot, run **`ssh macmini '~/bc-stack/health.sh'`**. It checks the console user, the firewall, Tailscale, the cable address, Colima, both containers, the Postgres sysid, Redis, the four relays, the Wi-Fi ports and the app servers. Exit 0 means ALL OK.

Before a **planned** reboot, tell any session using the database. The outage is about 1–2 minutes.

### 9.2 Routine checks
| After… | Do this |
|---|---|
| `brew upgrade socat` or `brew upgrade tailscale` | re-run `~/bc-stack/firewall.sh`. Firewall rules name exact file paths, which change on upgrade |
| Node upgrade (nvm) | the new `node` gets an "allow?" prompt: **Deny**, or block it with `socketfilterfw --blockapp <new path>`; update the `PATH` in `process-compose.yaml` |
| `npm install` fails with 401/403 | CodeArtifact login (§5) |
| Colima memory (4 GB cap) | stop, then restart with `--memory N`. This takes the database down briefly, so coordinate |
| New Tailscale device | same Google account; disable key expiry only for always-on machines |
| Replacing the cable | factory-made Cat6 only (a hand-crimped cable caused link flapping). The laptop Ethernet adapter's power saving is **off** (set by RegistryKeyword: `*EEE`, `EEELinkAdvertisement`, `ULPMode`, `ReduceSpeedOnPowerDown`, `EnableK1`) |

### 9.3 Troubleshooting
| Symptom | Likely cause | Fix |
|---|---|---|
| `ssh macmini` times out | cable link down | check the link lights; `ping 10.10.10.2`; use `macmini-ts` meanwhile |
| laptop bc-core can't reach the database | Mac Colima/relays not running (reboot without sign-in) | §9.1; `launchctl list \| grep barecount` |
| Mac app unreachable from the laptop | firewall (by design) | use the SSH tunnel (§3) |
| `start:dev:aws` says "not signed in" | AWS credentials missing or expired | check `aws sts get-caller-identity` on the Mac |
| laptop Odoo `:8100` gives an empty reply | Docker Desktop port forwarding half-broken after a WSL restart | Quit and restart Docker Desktop |
| `docker` on the Mac: "Cannot connect" | `DOCKER_HOST` not set (non-login shell) | `export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock` |

---

## 10. Working with Codex (the auditor)

- Codex stays on the laptop. The review exchange travels through GitHub (`bc-external-audit`), so it works from either machine. **Push everything you want reviewed.**
- **Codex's auditor database settings** (`bc-external-audit/.env`) point at `10.10.10.2:5435`. Codex changed them itself.
- **The instant review nudge** (`127.0.0.1:45980`) is laptop-only. From the Mac, reviews rely on Codex's 5-minute polling unless Codex opens its listener to the cable or Tailscale address.

---

## 11. Open items

1. **Step 2:** move DevHub (copy `data/devhub.db`), the app servers and the Claude sessions to the Mac, and add the DevHub relays. Needs devhub#22 merged.
2. ~~Auto-login decision and a reboot test~~: done 2026-09-25 (§9.1).
3. **Fix the AWS console sign-in**, then:
   - check that an `aws login` session can assume `bcp-dev-aps1-sct-role`
   - move both machines off the long-lived `default` key
4. **Odoo demo world:** optionally move it to the Mac. It needs Rosetta for its amd64-only image (a Colima restart) and a Foundry config change through a bc-demo PR. It's small (about 0.3 GB), so it's low priority.
5. **bc-core `TENANT_DATABASE_URL`** points at `tbc_pilot1_dev`, which exists on neither machine.
6. **Delete the database dump files** on both machines (`bc-core/_archives/`) once the move is settled.

## 12. Records

In `barecount-devhub/artifacts/infra/`:
- `mac-mini-offload-runbook.md`: the original move plan
- `mac-move-inventory-2026-09-25.md`: the pre-move inventory
- `db-cluster-handoff-laptop-to-macmini-2026-09-25.md`: database hand-off evidence
- `dev-secrets-to-aws-design-2026-09-25.md`: the secrets design
- the `MSG-Claude-*` review requests

PRs: bc-infra#30, bc-core#819, barecount-devhub#21, barecount-devhub#22.
