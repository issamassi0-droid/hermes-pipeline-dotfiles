# Deployment Smoke Test — generic Standard Operating Procedure

This is the detailed, stack-agnostic version of Section 4 in `SKILL.md`.
Every step that used to name a specific tool, port, or Makefile target now
says how to *discover* the equivalent for the project actually being
tested. Run `scripts/stack-detect.sh` first — it automates most of Phase 0
below and prints a summary to work from.

## Phase 0: Stack Discovery

### 0.1 Confirm the project root

**Objective:** verify the working directory is the project root.

**Steps:**
1. `pwd`.
2. Check for at least one manifest/marker file: `README*`, `package.json`,
 `pyproject.toml`, `go.mod`, `Cargo.toml`, `Makefile`,
 `docker-compose*.yml`, `Dockerfile`.

**Success criteria:** at least one manifest file is present and its
declared name/description matches what's being tested.

### 0.2 Identify build/run tooling

**Steps:**
1. If a `Makefile` exists, run `make help` or read its targets for
 install/build/start/stop/test verbs.
2. If `package.json` exists, read its `scripts` block for `dev`,
 `build`, `start`, `test` equivalents.
3. If `pyproject.toml`/`tox.ini`/`noxfile.py` exists, read their defined
 sessions/commands.
4. If `docker-compose*.yml` exists, read its services, exposed ports, and
 any healthcheck blocks — these are often the most reliable source of
 truth for both "how do I start this" and "what port does it expose".
5. Check `README.md`/`CONTRIBUTING.md` for a "Quick Start" or "Getting
 Started" section — this is frequently the canonical, human-maintained
 version of the above and should win in case of disagreement with an
 inferred command.

**Output:** a short table of {step: install, build, start (local), start
(container), stop, health-check} → the concrete command, with its source
noted (Makefile / package.json / docker-compose / README).

### 0.3 Identify ports and health endpoints

**Steps:**
1. Search `docker-compose*.yml` `ports:` blocks.
2. Search `.env.example`/`.env.sample`/config files for a `PORT` or
 similar variable.
3. Search the README/API docs for a documented health-check route
 (`/health`, `/healthz`, `/status`, `/ping`, or similar).
4. If nothing documented, fall back to: "the main entrypoint URL returns
 HTTP 2xx" as the minimum bar.

### 0.4 Identify required environment/config

**Steps:**
1. Look for `.env.example`, `.env.sample`, or an example config file
 (`config.example.*`).
2. Note which variables look mandatory (API keys, database URLs,
 secrets) vs optional (feature flags, log level).

---

## Phase 1: Code Update Check

### 1.1 Confirm current directory
Same as Phase 0.1.

### 1.2 Check Git status
1. `git status`.
2. If there are uncommitted changes, recommend the user commit or stash
 first to avoid conflicts while pulling. If they confirm they want to
 continue anyway, this step can be skipped — never discard silently.

### 1.3 Pull the latest code
1. `git fetch origin <default-branch>` (discover the default branch —
 don't assume `main`; check `git remote show origin` or the repo's
 default-branch setting).
2. `git pull origin <default-branch>`.

**Success criteria:** command succeeds; output shows "Already up to date"
or new commits pulled successfully.

### 1.4 Confirm the update
1. `git log -1 --oneline` — record the commit hash and message for the
 report.

---

## Phase 2: Deployment Mode Selection and Environment Check

### 2.1 Choose deployment mode
1. Prefer whichever mode has lower setup cost for this repo (often local,
 but a documented one-command Compose bring-up may be simpler — check
 both before deciding).
2. If the user explicitly requests a mode, use it.
3. If a containerized attempt hits network/registry issues, switch to
 local mode automatically and say so.

### 2.2 Local/native mode environment check
For each tool identified in Phase 0.2 (language runtime, package
manager, any local reverse proxy, database, etc.):
1. Run its version-check command (`node --version`, `python3 --version`,
 `go version`, etc.).
2. Compare against any version constraint stated in the manifest
 (`engines` in `package.json`, `python_requires` in `pyproject.toml`,
 a `go.mod` `go` directive, etc.).

**Failure handling:** if a tool is missing or too old, look up its
official install instructions (or point the user to them) rather than
guessing a package-manager command that may not apply to their OS.

Check that the ports identified in Phase 0.3 are free, or occupied only
by a prior instance of this same project:
```bash
lsof -i :<port> # macOS/Linux
netstat -ano | findstr :<port> # Windows
```

### 2.3 Container mode environment check (if selected)
1. `docker --version` (or `podman --version`).
2. `docker info` (daemon reachable).
3. `docker compose version` (or the project's documented orchestration
 tool).
4. Confirm the ports from Phase 0.3 are free.

---

## Phase 3: Configuration Preparation

### 3.1 Project config file
1. Check whether the project's main config file exists (from Phase 0.4).
2. If the project has a documented "generate config" command, run it;
 otherwise copy from the documented example file.
3. Spot-check that at least the mandatory fields identified in Phase 0.4
 are set to something non-placeholder.

### 3.2 Environment file
1. Check whether `.env` (or equivalent) exists; if not, copy from the
 example.
2. Confirm mandatory variables (API keys, DB URLs, secrets) are set.

---

## Phase 4: Deployment Execution

### 4.1 Local/native mode
1. Run the project's documented dependency-check command, if any.
2. Run the project's documented install command(s) for each
 language/package manager involved.
3. Run any documented optional pre-warm step (e.g. pre-pulling a
 sandbox/runtime image) if the project defines one and it's relevant.
4. Start services using the project's documented start command, in
 background/daemon mode if available so the agent can continue
 health-checking without blocking.
5. Wait for startup — use a documented startup window if the project
 states one; otherwise poll the health endpoint every few seconds for
 up to ~120s rather than sleeping a fixed guess.

### 4.2 Container mode (if selected)
1. Run any documented init/pull step.
2. Run the project's documented "up"/start command (commonly `docker
 compose up -d` or a Make target wrapping it).
3. Wait for startup the same way as 4.1.5 — poll rather than a fixed
 sleep, using `docker compose logs`/`docker ps` to monitor progress if
 useful.

---

## Phase 5: Service Health Check

### 5.1 Process/container status
- Local: check the expected processes are running (`ps aux | grep
 <process-name-pattern>` derived from Phase 0.2, e.g. the actual binary
 or entrypoint script name — not a hardcoded example from another
 project).
- Container: `docker ps` and confirm the expected containers (from
 `docker-compose*.yml` service names) are `Up`.

### 5.2 Entrypoint check
```bash
curl -I <entrypoint-url>
```
**Success criteria:** HTTP 2xx (or whatever the project documents as its
success response).

### 5.3 Health endpoint check (if one exists)
```bash
curl <health-endpoint-url>
```
**Success criteria:** the documented healthy response (often a 200 with a
JSON body, or just a 200).

### 5.4 Additional documented routes (if any)
If the project documents other critical routes (an app shell, a core API
route family), spot-check those too. `scripts/route-check.sh` is a
templated helper — pass it the base URL and a list of routes to check;
don't assume any specific path belongs to every project.

### 5.5 Authenticated routes (if relevant)
If a route redirects to a login page when unauthenticated, prefer an
anonymous health/ready endpoint if the project exposes one. Only create a
disposable test account if the project's own tooling already does this
(don't invent new test-account machinery inside a generic smoke test);
document the account's default credentials and the environment variables
that override them if you do.

---

## Optional Functional Verification

Only if relevant to what the project actually does:
- Confirm any documented capability listing loads (available plugins,
 routes, models — whatever is the project's equivalent).
- Send one minimal end-to-end request through the project's main
 workflow.

---

## Phase 6: Generate the Test Report

1. Collect results from every phase actually run.
2. Record any failures with full error detail.
3. Fill in `templates/smoke-test-report.template.md` — don't substitute a
 free-form summary.
4. State pass/fail per case plus an overall conclusion, and list the
 mode used (local/container) and the commit tested.
5. Offer follow-up recommendations based on what failed, if anything.
