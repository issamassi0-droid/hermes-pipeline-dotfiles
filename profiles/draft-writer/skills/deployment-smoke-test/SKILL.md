---
name: deployment-smoke-test
description: >
  End-to-end deployment smoke testing — auto-detect a project's own build/run
  tooling, deploy it, verify health, and produce a pass/fail report. Use when
  asked to "run a smoke test", "verify the deployment", "test service
  availability", or "end-to-end check". Works against any stack (Node, Python,
  Go, Rust, Docker Compose, etc.) by discovering the project's own tooling
  first.
---

# Deployment Smoke Test

Run a project's own build/deploy/health-check cycle end to end and produce a
pass/fail report — without assuming a specific stack, Makefile, port list, or
service naming.

Every concrete command below is something the agent **discovers first**, then
runs. Nothing is hardcoded to a port number, container name, or package
manager — those all vary per project.

## Deployment Mode Selection

Most projects support at least one of:

- **Local/native mode** — services run directly on the host using the
  project's own package manager(s) and run scripts.
- **Container mode** — services run via Docker/Podman/Compose (or a
  project-specific container orchestration).

**Selection strategy:**

- If the user explicitly asks for a mode, use it.
- If a containerized attempt hits network/registry issues, fall back to local
  mode automatically and say so.
- Default to whichever mode has the lower setup cost for this repo — often
  local, but check for a `docker-compose.yml`/`Dockerfile` plus a documented
  one-command bring-up first; if that exists and is simpler than the local
  toolchain, prefer it.

## Standard Operating Procedure (SOP)

### Phase 0: Stack Discovery

Before anything else, discover:

1. **Repo root markers** — confirm the working directory is the project root
   (look for `README`, a manifest file — `package.json`, `pyproject.toml`,
   `go.mod`, `Cargo.toml`, `Makefile`, `docker-compose.yml`, etc.).
2. **Build/run tooling** — read `Makefile` targets, `package.json` scripts,
   `pyproject.toml`/`tox.ini` sessions, or a documented `CONTRIBUTING.md`/README
   "Quick Start" section. Prefer whatever single command the project's own
   docs present as the canonical way to install, run, and stop services.
3. **Ports and health endpoints** — read `docker-compose.yml`, `.env.example`,
   or config files for exposed ports; read the README or API docs for a
   health-check route (commonly `/health`, `/healthz`, `/status`, or a
   documented equivalent). If none is documented, treat "the main entrypoint
   returns HTTP 200" as the minimum health check.
4. **Required environment/config** — identify `.env.example` or equivalent,
   and which variables are mandatory (API keys, DB URLs) vs optional.

`scripts/stack-detect.sh` automates steps 1–3 for common stacks and prints a
summary the agent can act on; treat its output as a starting point, not ground
truth — always cross-check against the README when the script's guess and the
docs disagree.

### Phase 1: Code Update Check

1. Confirm the working directory is the project root (Phase 0.1).
2. `git status` — check for uncommitted changes; if present, ask whether to
   proceed, commit, or stash before pulling (don't silently discard).
3. `git pull` (or the project's documented update command) to fetch the latest
   code.
4. `git log -1 --oneline` — record the commit pulled, for the report.

### Phase 2: Environment Check

For whichever mode was selected, verify the required tools are present and at
a compatible version (language runtime, package manager, any reverse proxy or
database the project needs locally) — derived from Phase 0's discovery, not a
fixed list. Verify the ports the project's own config says it needs are free
(or occupied only by a prior instance of this same project).

### Phase 3: Configuration Preparation

1. Check whether the project's config file(s) exist; if the project has a
   documented "generate config" command, run it, otherwise copy from the
   documented example file.
2. Check whether required secrets/env vars are set (per Phase 0.4).

### Phase 4: Deployment Execution

Run the project's own documented install → build → start sequence for the
selected mode. Wait for a reasonable startup window (the project's docs may
state one; otherwise budget ~60–120s and poll rather than guessing a fixed
sleep) before health-checking.

### Phase 5: Service Health Check

1. Confirm the expected processes/containers are actually running.
2. Hit the discovered entrypoint URL and confirm it returns success (HTTP 2xx,
   or whatever the project documents as "up").
3. Hit the discovered health endpoint, if one exists, and confirm it reports
   healthy.
4. If the project has documented critical routes/pages beyond the health
   endpoint (a login page, a core API route), spot-check those too —
   `scripts/route-check.sh` is a generic templated version of this check; adapt
   its route list to the project rather than assuming any specific path.
5. If the project has authentication that would otherwise redirect a health
   check to a login page, check whether it exposes an anonymous health/ready
   endpoint first; only create/use a disposable test account if the project's
   own smoke-test tooling already does so.

### Optional Functional Verification

If relevant to the project: confirm any documented capability listing loads;
send one minimal end-to-end request through the main workflow the project
exists to serve.

### Phase 6: Generate the Test Report

Use `templates/smoke-test-report.template.md`. Include: overall pass/fail
conclusion, per-phase results, the commit tested, the mode used
(local/container), explicit health-check results, and any warnings encountered
that didn't block success. Don't substitute a free-form summary for the
template.

## Execution Rules

- Follow the phase sequence; every step should be safe to repeat (idempotent).
- On failure, stop, report the issue, and consult
  `references/troubleshooting.md` for the matching symptom category before
  improvising a fix.
- Ask for confirmation before a potentially destructive operation (e.g.
  overwriting an existing config file, discarding uncommitted changes).
- Prefer the lower-setup-cost mode to avoid unnecessary network/tooling
  failures.
- The final report must use the template — not a free-form summary — and must
  state pass/fail per case, not just an overall verdict.
- If optional functional verification wasn't run, don't present it as a
  separate "skipped" phase in the report.

## Bundled files

```
deployment-smoke-test/
├── SKILL.md
├── references/
│   ├── smoke-test-sop.md          ← detailed, stack-agnostic step-by-step procedure
│   └── troubleshooting.md         ← symptom-indexed troubleshooting playbook
├── scripts/
│   ├── stack-detect.sh            ← discovers build/run tooling, ports, health endpoints
│   └── route-check.sh             ← generic templated route/health smoke checker
└── templates/
    └── smoke-test-report.template.md  ← report shape to fill in
```
