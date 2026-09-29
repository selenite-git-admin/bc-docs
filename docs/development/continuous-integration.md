---
id: continuous-integration
order: 40.5
title: "Continuous Integration and CI Runners"
status: drafting
authority: authoritative
depends_on: [build-and-release, quality-assurance, dev-workstation-mac-mini]
governing_sources:
  - Build and Release
  - Quality Assurance
  - "barecount-devhub scripts/ci/macbook-runner/README.md (the runner kit and its runbook)"
governing_adrs:
  - DEC-081931 (gen- exchange; every runner change was reviewed by Codex through it)
  - DEC-44456d (the auditor's home on the Mac; operator grants through bc-exchange)
errata_referenced: []
---

# Continuous Integration and CI Runners

Covers where BareCount's CI runs, what each repository requires before a merge, how jobs pick a runner, and how to operate and change the self-hosted MacBook runner. Set up 2026-09-26 to 2026-09-29 under TSK-e0dab5 (DevHub sessions up to SES-3d5597).

**Why this exists.** In September 2026, normal CI use went past GitHub's free 3,000 minutes a month. Paid minutes reached about $25 a day, with Linux the bulk of it and macOS at ten times the Linux rate. The goal was to move the heavy Linux jobs to hardware BareCount already owns, without weakening the isolation between untrusted PR code and the machines that hold credentials.

---

## 1. What each repository requires

Every repository runs GitHub Actions. Branch protection on `main` requires these checks:

| Repository | Workflows | Required checks |
|---|---|---|
| barecount-devhub | `ci.yml` | `quality-gate`, `unit-tests (ubuntu-latest)`, `unit-tests (macos-latest)` |
| bc-core | `ci.yml`, `docker-redesign-lockstep.yml`, `stale-branches.yml` | `quality-gate` |
| bc-db | `ci.yml` | `quality-gate` |
| bc-docs | `adr-hygiene.yml` | `adr-hygiene` |
| bc-admin | `ci.yml` | `build` |
| bc-portal | `ci.yml` | `quality-gate` |
| bc-demo | `ci.yml` | `test`, `build-gates` |
| bc-infra | `ci-validate.yml`, `cd-prepare.yml`, `cd-execute.yml` | `validate` |
| bc-external-audit | `auditor-checks.yml`, `service-ci.yml` | not protected |

A `quality-gate` job is the single aggregate check: it fails when any job it depends on did not succeed. Judge a run by `gh run view <id> --json conclusion`, never by the tail of `gh run watch`.

**barecount-devhub specifics** (barecount-devhub#100):
- a push that only changes `artifacts/**` does not run CI;
- the Linux unit tests run on pull requests;
- the Windows leg was removed once the auditor moved to the Mac;
- the macOS leg runs only when a pull request touches macOS-sensitive paths (the `os-sensitive` job: exchange scripts, hooks, the runner kit, OS-branching `src/lib` files, the server and housekeeping routes, package files, workflows). Otherwise `unit-tests (macos-latest)` still reports success, so the required check is met without paying for macOS minutes.

## 2. Where jobs run: the `pick-runner` job

bc-core and bc-db start every workflow with a small `pick-runner` job on a GitHub-hosted Ubuntu runner. It uses the read-only repository secret `RUNNER_STATUS_TOKEN` to ask GitHub whether a self-hosted runner labelled `bc-ci` is online (3 tries, 10 s apart):

- **online** → the heavy jobs run on `["self-hosted","Linux","ARM64","bc-ci"]`, the MacBook;
- **offline, or any error** → they run on `ubuntu-latest`, as before.

So switching the MacBook off never blocks CI; it only moves the cost back to GitHub.

**Routed to the MacBook:**
- bc-core: `static-analysis`, `vitest-shard (1..3)`, `e6b-db-integration`;
- bc-db: `unit-tests`, `backup-adoption`, `tenant-fleet`.

**Always GitHub-hosted:**
- `pick-runner` and `quality-gate` (seconds each);
- bc-db's `baseline-runner` and `capture-fixtures`, because `versions/contract.json` pins the linux/amd64 database engine. Measured 2026-09-29: plain-mode Lima has no Rosetta, and QEMU emulation ran the amd64 Postgres about 8 times slower to load and 12 times slower in throughput. They stay hosted for good (about $20–25 a month).

## 3. The MacBook runner

**The machine:** the spare M1 MacBook Pro, 8 GB, macOS 27, FileVault on. It stays on Wi-Fi only: never on the desk cable network, never on Tailscale. The installer checks this, and every job re-checks it.

**The kit:** barecount-devhub `scripts/ci/macbook-runner/`. Its `README.md` is the step-by-step runbook; this section is the model.

### 3.1 How a job runs

1. A hidden, non-admin account `ghrunner` holds everything. It keeps a **golden VM image** (Ubuntu 24.04 ARM64, Lima plain mode, no folders shared with macOS). The image holds no runner registration and is never booted after it is sealed; a digest check refuses to run if it changes.
2. One **worker** runs per slot, each as a LaunchDaemon `com.barecount.ci-worker.<slot>`. `SLOTS` in `config.sh` lists them. Today there are two: `bc-core-w1` and `bc-db-w1`.
3. Before each job, the worker proves **the boundary**:
   - the network rule above;
   - a root-owned canary listener on the Mac's loopback is up, yet unreachable from `ghrunner` (the macOS pf anchor `com.barecount.ci` is in force);
   - from inside a freshly cloned VM, the Mac's own loopback is unreachable, with a positive control so that a broken probe cannot read as "blocked".

   Only then does it ask GitHub for a **single-job (JIT) registration**. The registration exists only in memory and reaches the VM on stdin.
4. The VM runs exactly one job, then it is deleted and the registration is **proved gone** by an API read-back. If that cannot be proved, the worker registers nothing (fail closed), and CI falls back to GitHub-hosted.
5. Each slot has its own VM, ledger and runner name `mbp-<machine id>-<slot>-<UTC>`, so no slot can delete another's registration.

### 3.2 Why only one slot per repository

This was measured on 2026-09-29:

| Configuration | Result |
|---|---|
| One slot per repo, 3 GiB VMs (the original kit) | All jobs green; per-job time equal to or better than GitHub; median queue wait 11 min for bc-core, 6 min for bc-db |
| Two bc-core slots plus one bc-db slot, 2.5 GiB VMs | bc-core's eslint ran out of Node heap (Node sizes its heap from VM memory) |
| Two bc-core slots, 3 GiB VMs | Jobs took about 3 times longer (static-analysis 16 min against 2–4); host swap grew to 4 GB |
| **One slot per repo, 3 GiB VMs (current)** | static-analysis 3 min, vitest shards 4 min, e6b 4 min; swap back to about 1.25 GB |

On 8 GB, parallel jobs only trade queue time for swapping. Running more jobs at once needs a host with more memory (§7).

### 3.3 Operating it

| Action | How |
|---|---|
| On | Switch the MacBook on, plugged in, **lid open**. The workers start at boot. A closed lid sleeps it whatever the settings (seen 2026-09-29) |
| Stop | `bash activate.sh stop`, only **when no MacBook job is running** (check GitHub, or ask Claude). It must print `STOPPED CLEAN` |
| Start | `bash activate.sh` (refuses while a worker no longer in `SLOTS` is still installed) |
| Isolation proofs | `bash verify.sh` (registers nothing) |
| Change the kit or `SLOTS` | stop → `install.sh` from the new kit → `verify.sh` → `activate.sh` |
| Remove | `uninstall.sh`: halts unless every registration and VM is proved gone |
| Logs | `sudo sh -c "tail /Users/ghrunner/ci/logs/<slot>-worker.log"`. Each job logs free memory and swap |
| Other accounts | Keep other user sessions logged out; their apps take memory the VMs need |

**Stopping mid-job strands the job.** Stopping kills the VM, but GitHub keeps the lost job "in progress" and the runner "busy" until the job times out, up to 6 hours for jobs without `timeout-minutes`. Deleting a busy runner is refused (HTTP 422), so the stop reports `NOT CLEAN`. This happened three times on 2026-09-29.

**Recovery:**
- wait for GitHub's timeout; or
- with a recorded operator grant naming the run, force-cancel it (`POST /repos/<owner>/<repo>/actions/runs/<id>/force-cancel`), re-run `activate.sh stop`, and re-run the cancelled build afterwards.

The fix, a stop that lets a running job finish first, is TSK-72a75a.

## 4. Changing the runner: governance

The runner executes untrusted PR code on a machine BareCount owns, so every change to the kit follows one route:

1. **Pull request** to barecount-devhub, with the lifecycle test suite (`tests/lifecycle.test.sh`, run in CI). New safety behaviour must come with a test that fails when the behaviour is removed.
2. **Codex review** on a `gen-` thread (full depth). The reviews so far:
   - gen-7fdfc0 (design);
   - gen-2a988a (probes);
   - gen-9990f7 (slots; held after two rounds on a migration race and a probe-error gap);
   - gen-fc3f10 (remediation, 3 GiB, option C).
3. **Operator grant** in bc-exchange naming the exact head, for the reinstall, verify and activation. A cancel of anyone's CI run needs its own grant.
4. The operator reinstalls from a zip built with `git archive` from that exact head. Then comes a measured run, then the merge.

**Migrations are part of the kit.** Any installed worker that is no longer in `SLOTS` is stale. `install.sh` retires stale workers in a fixed order:
1. stop all of them;
2. prove each inactive with positive-absence probes: `launchctl print` exit 113 and `pgrep` exit 1; anything else, including a probe error, fails;
3. prove their registrations and VMs gone;
4. prove them still inactive;
5. only then remove their plists.

## 5. Isolation rules that must not regress

- **No self-hosted runner on the dev Mac Mini** (Codex gen-f1d734). It holds tokens in process arguments and a reachable Postgres superuser, and any PR could target such a runner.
- A Lima guest can reach **every** listener on the host's loopback through `host.lima.internal`. That is why the pf block for `ghrunner` exists, and why each job proves it first.
- The pf rule lets `ghrunner` reach only the VMs' fixed SSH ports (60300–60309) and blocks new connections (`flags S/SA`, `block return`) and UDP to everything else on loopback.
- The admin token lives only in `ghrunner`'s home, mode 600, and reaches `curl` on stdin. It never appears in process arguments, in files inside a VM, or in logs.
- Registration only ever happens after the boundary proofs, and a registration that cannot be proved deleted blocks the next one.

## 6. Cost

GitHub bills per job-minute, rounded up: Linux ×1, Windows ×2, macOS ×10. Daily spend peaked at about $25 on 2026-09-26/27 and was $0.02 early on 2026-09-29, with the MacBook live and the Windows and most macOS legs gone. What remains paid:
- bc-db's two amd64 jobs;
- the `pick-runner` and `quality-gate` seconds;
- the other repositories' CI;
- macOS legs on macOS-sensitive devhub PRs;
- any time the MacBook is off.

## 7. Options considered

| Option | Status |
|---|---|
| Runner on the dev Mac Mini | Rejected (isolation, §5) |
| Always-on EC2 box | Rejected: about $77/month, more than the saving |
| Free GitHub organisation | Rejected by the operator: too much risk to the existing setup |
| Golden image with a persistent runner identity | Rejected (Codex gen-a1af30); JIT registrations only |
| Several parallel slots on the 8 GB MacBook | Tried and reverted (§3.2) |
| x86 mini PC, 32 GB | Open: 4–6 parallel jobs and native amd64 (bc-db's hosted jobs could move too); one-time cost; needs a Linux port of the kit |
| EC2 spot machine per job (8 GB class; t3.micro/small are too small for eslint) | Open: parallel, amd64, cheap per minute; needs an isolated network with no IAM permissions for PR code, a cloud-change go and a Codex design review |

## 8. Where to look

- The kit and its runbook: barecount-devhub `scripts/ci/macbook-runner/README.md`.
- The routing: `pick-runner` in bc-core and bc-db `.github/workflows/ci.yml` (bc-core#864, bc-core#868, bc-db#85).
- The devhub CI shape: barecount-devhub#100. The slot kit: barecount-devhub#121.
- Open follow-ups: TSK-72a75a (drain on stop).
