---
title: "Mac Auditor Operations"
description: "Operator runbook for the Codex auditor on the Mac: what runs, who authorizes what, daily checks, installing a reviewed service change, deploying the desk, re-arming a held message, upgrading Codex, changing the auditor App's repositories, diagnosing kills, rollback, and setting the auditor up from scratch."
authority: authoritative
domain: operations
status: active
date: 2026-09-29
refs:
  - type: decision
    label: "DEC-44456d — the auditor runs on the Mac (account bcauditor)"
  - type: decision
    label: "DEC-081931 — the permanent gen- exchange"
  - type: doc
    label: "dev-workstation-mac-mini.md §10 — working with Codex from a session"
---

# Mac Auditor Operations

How to run the Codex auditor on the Mac Mini. The auditor has been the only BareCount auditor since 2026-09-28 13:46 UTC (switch grant `f5a0490b`). The laptop Codex no longer audits BareCount.

Sessions talk to Codex through the `codex-exchange` skill (see `dev-workstation-mac-mini.md` §10). This chapter is for the operator and for sessions that maintain the auditor itself.

## 1. What runs where

| Piece | Where | What it does |
|---|---|---|
| macOS account `bcauditor` | home `/Users/bcauditor`, mode 700 | Holds Codex's sign-in, the auditor App key (`~/.config/bc-audit/`), the read-only GitHub token (`~/.config/bc-audit/gh-readonly-token`) and the recorded grants (`~/grants/`). Your own account cannot read it. |
| Review service | launchd `co.selenite.bcauditor.shadow`, runs `~/auditor-service/shadow/watch.zsh` | Fetches the mailbox (`bc-external-audit` `docs/` on `origin/main`) every 60 s, reviews each waiting `gen-` message with `codex exec`, and publishes the reply. |
| Auditor App tools | `~/auditor-service/bc-audit-app` | The `bc_audit_app` MCP server. Writer runs use it to read PR evidence, approve and merge, under the App's own head, CI, actor and protection gates. |
| Desk (bc-exchange) | launchd `co.selenite.bcauditor.exchange`, http://127.0.0.1:3040 | Shows conversations, requests, grants, logs, performance and configuration (the rules). Grants are recorded here with a phone code. |
| Desk updater | launchd `co.selenite.bcauditor.exchange-update`, every 2 min | Deploys a new bc-exchange commit only after tests pass **and** an exact deploy grant exists (§4.2). |
| Alert watch | Claude scheduled task "Codex Auditor alert watch", every 10 min while the Claude app is open | Reads the desk and pushes one line to your phone when something needs you. It is read-only. |
| Codex program | `/opt/homebrew/Caskroom/codex/<version>/bin/codex` (Homebrew cask) | Shared by all accounts. It must not carry the quarantine flag (§4.4). |

The service's behaviour:
- **Capacity.** Up to 3 reviews run at once, and never two on one conversation.
- **Order and lanes.** The oldest message goes first. A message marked `Lane: platform` goes first, and one of the three slots is kept for platform messages (grant `ca5846c1`).
- **Held replies.** A reply that fails the publish check is retried with the refusal reasons. After 2 unpublished runs the message is held; 30 min later it gets **one** automatic retry, and after 3 it stays held for you.
- **Early kills.** A run killed at start is retried after 1, 2, 4, 8, 16, then every 30 min, and is never held for that.
- **Stalls.** A run older than 45 min with no new output for 15 min is stopped. That counts as a run.

## 2. Who authorizes what

| Act | Who | How |
|---|---|---|
| Review a PR | Codex | Any session sends it on `gen-` (skill). |
| Merge in barecount-devhub, bc-core, bc-docs, bc-db, bc-admin, bc-portal, bc-demo, bc-infra, **bc-exchange** | Codex through the auditor App | Only under the App's gates and the recorded grants shown on the desk's Configuration page. For bc-exchange, grant `22d493f8`, with branch protection (`test` check and 1 approval). |
| Merge in **bc-external-audit** (the auditor's own service) | You | Say go to the session; it merges pinned to the accepted head. This repo is deliberately outside the App. |
| Install a service change | You | With your password (§4.1). |
| Deploy a desk change | You | Record the exact deploy grant on the desk (§4.2). |
| Anything live (database apply, serve move, cloud, secrets) | You | Your own recorded grant for that act. |

A request on the desk is never authority. Only a grant recorded with your phone code is. You can also answer a request with **Ask for changes** or **Decline** plus a comment; the requesting session reads it at `GET /api/requests/<id>`.

## 3. Daily check

1. Open http://127.0.0.1:3040. The dot before "Codex Auditor" should be green and blinking.
   - **Red:** read the banner; each alert names its thread and the next step.
   - **Amber:** the service is already retrying by itself; look again later.
2. Requests tab: approve, ask for changes, or decline what waits for you. **On hold** lists what Codex stopped for you.
3. If something looks slow, open Logs ("Review service" or "Kill snapshots") and Performance, both from the footer.

## 4. Procedures

### 4.1 Install a reviewed service change

**When:** a bc-external-audit PR under `service/shadow/` has Codex's acceptance at a pinned head and you said go, so it is merged pinned to that head.

1. **Build the App-helper folder**, a clean copy of the App server at the commit you run. Keep it outside any temporary folder:
   ```bash
   C=$(git -C ~/MyProjects/bc-external-audit rev-parse origin/main); B=~/bc-stack/bc-audit-app
   rm -rf $B && mkdir -p $B && git -C ~/MyProjects/bc-external-audit archive $C src package.json package-lock.json | tar -x -C $B && echo $C > $B/COMMIT
   (cd $B && npm ci --omit=dev --ignore-scripts --no-audit --no-fund)
   ```
   This is needed only when the App server (`src/`) changed. Otherwise reuse the existing folder.
2. **Check out the accepted head** in a clean worktree:
   ```bash
   git -C ~/MyProjects/bc-external-audit worktree add ~/MyProjects/_wt/bcea-install <accepted-head-sha>
   ```
3. **Install** (asks for your password):
   ```bash
   zsh ~/MyProjects/_wt/bcea-install/service/shadow/install-writer.zsh <accepted-head-sha> ~/bc-stack/bc-audit-app
   ```
   The script refuses unless the checkout is exactly that commit with no local changes. If a review is running, it waits for it to finish. It then copies the files, restarts the service, and runs the App check.
4. **Verify:**
   - The App check prints `"repository_scope_matches": true`.
   - Its deliberately wrong review call is refused by the server.
   - The desk's Logs → Review service shows `watching every 60s, up to 3 writer runs at once`.

### 4.2 Deploy a desk change

1. The PR is merged: by the App after Codex accepts it, or by hand.
2. Record on the desk exactly `Deploy bc-exchange commit <full sha of main>.` Usually a session posts this request and you approve it. After an App merge, that is the **merge commit's** sha.
3. Within about 2 minutes, Logs → Desk updates shows `updated <old> -> <new> (server restarted)`. Reload the desk page once.
4. To stop a pending deploy, record `Do not deploy bc-exchange commit <sha>.` The newer grant wins.

### 4.3 Re-arm a held message

**When:** a red alert says `<gen-id> is held … it needs re-arming`, meaning the automatic retry also failed. Open the conversation first: if the reply was refused, the refusal reasons are in Logs.

```bash
sudo rm -f /Users/bcauditor/auditor-shadow/runs/<gen-id>/<NN>/{writer-attempts,auto-retried,early-kills,early-next}
```

`<NN>` is the message number. The service picks the message up again within a minute.

### 4.4 Upgrade Codex (keep the quarantine flag off)

Homebrew marks downloaded casks with `com.apple.quarantine`. Your account cleared it the first time you ran Codex. The headless `bcauditor` daemon cannot, so macOS Gatekeeper kills every review run within a second of starting.
- **Symptom:** early kills (rc 137).
- **In the log:** `ASP: Security policy would not allow process … /codex`.
- **History:** on 2026-09-29 this caused several kill windows.

1. **Upgrade without the flag:**
   ```bash
   brew upgrade --cask --no-quarantine codex
   ```
2. **Verify both binaries are clear.** Each should print `No such xattr`:
   ```bash
   V=$(ls /opt/homebrew/Caskroom/codex | sort -V | tail -1)
   xattr -p com.apple.quarantine /opt/homebrew/Caskroom/codex/$V/bin/codex /opt/homebrew/Caskroom/codex/$V/bin/codex-code-mode-host
   ```
3. **If it was upgraded the normal way,** remove the flag from both. Only do this for a genuine OpenAI-signed binary:
   ```bash
   codesign --verify --strict /opt/homebrew/Caskroom/codex/$V/bin/codex && codesign -dv /opt/homebrew/Caskroom/codex/$V/bin/codex 2>&1 | grep TeamIdentifier   # expect 2DC432GLL2
   xattr -d com.apple.quarantine /opt/homebrew/Caskroom/codex/$V/bin/codex /opt/homebrew/Caskroom/codex/$V/bin/codex-code-mode-host
   ```
4. **Prove the auditor account can run it:**
   ```bash
   sudo -u bcauditor -H zsh -lc 'cd /tmp && codex exec --skip-git-repo-check -c sandbox_mode="read-only" "Reply with the single word OK."'
   ```
5. **Check the model.** The service pins its model and effort (`BC_AUDITOR_MODEL`, `BC_AUDITOR_EFFORT` in `watch.zsh`; shown on the desk's Configuration page). After an upgrade, confirm the next review runs normally.

### 4.5 Change the auditor App's repositories

The App refuses **every** action when its installed repositories differ from the service's list (`ALLOW=` in `service/shadow/watch.zsh`). On 2026-09-29 adding bc-exchange to the installation first blocked all App reviews and merges for about 40 minutes.

1. **List first.** Change `ALLOW` in a bc-external-audit PR, get Codex's acceptance, merge (your go) and install (§4.1).
2. **Installation second.** Change the installation in GitHub: Settings → GitHub Apps → bc-auditor-app → Configure → Repository access. Do it right after the install, or in the same minute.
3. **Verify.** The next App capability check shows `repository_scope_matches: true`. The install check in §4.1 prints it too.
4. **Authority.** A new repository needs your recorded grant. bc-external-audit stays outside the App (grant `22d493f8`).

### 4.6 Diagnose kills and stuck reviews

- **Desk first.**
  - Logs → Review service shows each run (`started`, `ran … rc=`, `publish`).
  - Logs → Kill snapshots shows load, memory and busiest processes at each early kill.
  - Performance shows run and queue times.
- **The macOS log.** In zsh, `log` is a shell built-in; always use `/usr/bin/log`:
  ```bash
  /usr/bin/log show --last 30m --style compact --predicate 'eventMessage CONTAINS "Security policy would not allow"'
  ```
  Any hit naming `codex` means the quarantine problem (§4.4).
- **The read-only GitHub token.** The auditor uses it to verify CI and reviews in repositories outside the App. To check it without printing it:
  ```bash
  sudo -u bcauditor -H zsh -c 'T=$(cat ~/.config/bc-audit/gh-readonly-token); curl -s -o /dev/null -w "%{http_code}\n" -H "Authorization: Bearer $T" https://api.github.com/repos/selenite-git-admin/bc-external-audit'
  ```
  The answer should be `200`. The token expires 2026-12-28; renew it in GitHub before then (fine-grained token `bcauditor-ro-bc-exchange-external-audit`).

### 4.7 Roll back

| What | How |
|---|---|
| Service | Check out the previous accepted commit in a clean worktree and run §4.1 with that sha. If the App's repository list differs between the two commits, change the installation to match (§4.5). |
| Desk | Record the deploy grant for the earlier bc-exchange commit (§4.2). |
| App repositories | Remove the repository from the installation **and** from `ALLOW` together. |

## 5. Set up the auditor from scratch

How the auditor was built, for a rebuild on a new Mac or after a loss. Where a step was done by hand and not recorded in a script, it says so. Credentials are always placed by the operator; a Claude session never handles their values.

**1. The account.**
- Create a standard macOS user `bcauditor`. It must not be an administrator.
- Close its home to other users: `sudo chmod 700 /Users/bcauditor`.

**2. Tools inside the account.**
- **Node:** nvm with Node 22.18.0. The services use `/Users/bcauditor/.nvm/versions/node/v22.18.0/bin/node`.
- **Codex:** the Homebrew cask, shared with the Mac. Install it with `brew install --cask --no-quarantine codex` (see §4.4).
- **Sign-in:** sign Codex in as `bcauditor@selenite.co` (paid plan) with `codex login`, run as bcauditor (`sudo -u bcauditor -H zsh -l`).

**3. Codex's standing instructions.**
- These are `~/.codex/AGENTS.md` and the auditor session skill in bcauditor's Codex folder.
- **Gap:** they are not yet versioned. ADR DEC-44456d point (c) calls for them in `bc-external-audit`. Until they are, a rebuild has no reviewed copy; copy them from the current account before retiring it.

**4. Credentials, placed by the operator.**

The desk's Configuration page shows whether each one is present.

| Credential | Path in the account | What it is |
|---|---|---|
| Auditor App key | `~/.config/bc-audit/bc-auditor-app.pem` | Private key of the GitHub App `bc-auditor-app` (installation on selected repositories, §4.5) |
| Read-only GitHub token | `~/.config/bc-audit/gh-readonly-token` | Fine-grained token `bcauditor-ro-bc-exchange-external-audit`: bc-exchange and bc-external-audit only; Actions, Contents, Metadata and Pull requests read-only; grant `bcceba17` |
| Mailbox deploy key | `~/.ssh/bcea_deploy` | Deploy key on bc-external-audit. It has **write** access, used to publish replies, although it is titled "read-only" on GitHub. |
| Desk deploy key | `~/.ssh/bcx_deploy` | Read-only deploy key on bc-exchange |
| Phone-code secret | `~/.local/share/bc-exchange/totp.secret` | Created in step 6 |
| AWS read-only profile | `bc-auditor-readonly` | ReadOnlyAccess in account 546549546538 |

**5. The mailbox.**
- Clone `bc-external-audit` to `/Users/bcauditor/MyProjects/bc-external-audit` over `bcea_deploy`.
- The service clones the other repositories in its `ALLOW` list by itself, read-only, on its first run.

**6. The desk (bc-exchange).**

Follow `bc-exchange/README.md`, Setup:
- Clone to `/Users/bcauditor/bc-exchange` over `bcx_deploy`.
- Load `co.selenite.bcauditor.exchange.plist`.
- Enrol your phone with `bin/totp-setup.mjs`. Run it in the macOS Terminal app, never in a Claude window.
- Run `bin/install-self-update.zsh`.

Later versions arrive through the gated updater (§4.2). A first install of a specific commit uses `bin/install-reviewed.zsh <sha>` after its deploy grant.

**7. The review service.**
- Build the App-helper folder and run `install-writer.zsh` as in §4.1.
- The first time, also load the daemon:
  ```bash
  sudo install -m 644 -o root -g wheel /Users/bcauditor/auditor-service/shadow/co.selenite.bcauditor.shadow.plist /Library/LaunchDaemons/
  sudo launchctl bootstrap system /Library/LaunchDaemons/co.selenite.bcauditor.shadow.plist
  ```
- The service starts in **shadow** mode: it reviews but publishes nothing.

**8. The App's repositories.**
- Install `bc-auditor-app` on exactly the repositories in the service's `ALLOW` list.
- The install check must show `repository_scope_matches: true` (§4.5).

**9. Make it the writer.**
- Record on the desk a grant containing exactly `the Mac auditor is the writer for the gen- exchange`.
- To switch back, record `the Mac auditor is not the writer for the gen- exchange`. The newest one wins, and a writer run in progress is stopped within 10 seconds.
- Only one auditor may ever write.

**10. Alerts.**
- In the Claude app, create the scheduled task "Codex Auditor alert watch" (every 10 minutes). Its prompt is kept in `~/.claude/scheduled-tasks/auditor-alert-watch/SKILL.md`.
- Click **Run now** once to approve its tools.

**Check the finished setup:**
- The desk dot is green.
- Configuration lists every credential as present.
- Logs → Review service shows `mode: writer` and `up to 3 writer runs at once`.
- A test message on a new `gen-` thread gets a published reply.

## 6. Where things live

| Thing | Path |
|---|---|
| Service files | `/Users/bcauditor/auditor-service/shadow/` |
| Run records per message | `/Users/bcauditor/auditor-shadow/runs/<gen-id>/<NN>/` (`reply.md`, `publish.json`, `writer-attempts`, `auto-retried`, `early-kills`, `early-next`, `stalled.txt`) |
| Logs | `/Users/bcauditor/auditor-shadow/logs/` (`watch.log`, `kills.log`, `exchange-update.log`); readable on the desk |
| Recorded grants | `/Users/bcauditor/grants/` |
| Service source | `bc-external-audit` `service/shadow/` (README there) |
| Desk source | `bc-exchange` (README there) |
