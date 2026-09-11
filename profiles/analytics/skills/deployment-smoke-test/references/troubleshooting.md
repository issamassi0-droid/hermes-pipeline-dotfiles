# Deployment Smoke Test — Troubleshooting Playbook (generic)

Organized by symptom category rather than by any one project's specific
tools, so it applies regardless of language/runtime/orchestrator. Where a
concrete command is shown, treat the tool name as an example — substitute
the project's actual package manager, runtime, or reverse proxy.

## Code Update Issues

### `git pull` fails with a merge-conflict warning

**Symptoms:**
```
error: Your local changes to the following files would be overwritten by merge
```

**Options:**
1. Commit local changes first: `git add . && git commit -m "..." && git pull`.
2. Stash them: `git stash && git pull && git stash pop`.
3. Discard them (destructive — confirm with the user first):
 `git reset --hard HEAD && git pull`.

---

## Local/Native Mode Environment Issues

### A required runtime/tool is missing or too old

**Symptoms:** a version-check command fails, or reports a version below
what the manifest requires (`engines` in `package.json`, `go.mod`'s `go`
directive, `python_requires`, etc.).

**Options:**
1. Use the project's documented version manager if one exists (`nvm`,
 `pyenv`, `rustup`, `asdf`, etc.) to install/switch to the required
 version.
2. Otherwise install from the tool's official site/instructions.
3. Re-verify with the version-check command before continuing.

### A required package manager is not installed

**Symptoms:** `command not found: <pnpm|uv|poetry|cargo|...>`.

**Options:**
1. Use the package manager's own official install script/command (check
 its docs — don't guess a generic `apt`/`brew` name that may not exist
 for niche tools).
2. Re-verify with `<tool> --version`.

### A required local service (reverse proxy, database, cache) is not
installed

**Symptoms:** `command not found: <nginx|redis-server|postgres|...>`.

**Options:**
1. macOS: `brew install <tool>`.
2. Debian/Ubuntu: `sudo apt update && sudo apt install <tool>`.
3. RHEL/CentOS: `sudo yum install <tool>`.
4. Verify with the tool's version flag.

### A required port is already in use

**Symptoms:**
```
Error: listen EADDRINUSE: address already in use :::<port>
```

**Options:**
1. Find the process: `lsof -i :<port>` (macOS/Linux) or `netstat -ano |
 findstr :<port>` (Windows).
2. Stop it: `kill -9 <PID>` (macOS/Linux) or `taskkill /PID <PID> /F`
 (Windows).
3. Or stop the project's own services first, using its documented stop
 command, if the occupying process turns out to be a prior instance of
 this same project.

---

## Dependency Installation Issues

### Install fails due to network timeout

**Symptoms:** timeouts/connection failures while installing dependencies.

**Options:**
1. Configure the package manager to use a mirror registry if the
 project's docs suggest one, or if the user is in a region with known
 registry latency.
2. Retry the install command.
3. Check for a documented offline/vendored-dependencies mode.

### A specific package manager's install step fails

**Symptoms:** errors during `npm install`/`pnpm install`/`uv sync`/`pip
install`/`cargo build`/etc.

**Options:**
1. Clear that tool's cache (`pnpm store prune`, `uv cache clean`, `cargo
 clean`, etc.).
2. Remove and regenerate the lock file/`node_modules`/venv only if the
 project's own docs sanction this — it can mask a real incompatibility.
3. Reinstall and re-run with a verbose flag to capture the actual error.

---

## Local/Native Mode Service Startup Issues

### Services exit immediately after starting

**Symptoms:** the start command's process exits quickly instead of
staying up.

**Options:**
1. Check the project's log output (wherever it writes logs — often a
 `logs/` directory, or stdout if run in the foreground).
2. Check the project's config file for obvious errors.
3. Check required environment variables are set.
4. Confirm required ports are free.
5. Stop everything and restart with the documented stop/start commands.

### A local reverse proxy fails to start

**Symptoms:** the proxy process reports an error and exits, or a
`mkdir()`/temp-directory error appears in its log.

**Options:**
1. Check whether the proxy's config file references a temp/cache
 directory that doesn't exist yet — create it, or point the config at
 a directory the project's own start script already creates.
2. Validate the config syntax with the proxy's own `-t`/`--test`-style
 flag if it has one.
3. Confirm no other instance of the same proxy is already running
 (`ps aux | grep <proxy-name>`); stop it if so.

### Frontend/UI build fails

**Symptoms:** compilation errors in the frontend's log output.

**Options:**
1. Read the actual compiler/bundler error — it usually names the file
 and line.
2. Confirm the language runtime meets the manifest's version
 requirement.
3. Reinstall frontend dependencies (clear build cache/`node_modules`,
 reinstall) only if the error looks dependency-related, not
 code-related.
4. Restart services with the documented stop/start commands.

### Backend/API process fails to start

**Symptoms:** errors in the backend's log output.

**Options:**
1. Read the actual error/stack trace.
2. Check the config file exists and is valid.
3. Check dependencies are fully installed for the backend's language.
4. Confirm the process is actually running afterward, not just that the
 start command returned.

---

## Container Mode Issues

### Docker/Podman commands can't run

**Symptoms:**
```
Cannot connect to the Docker daemon
```

**Options:**
1. Confirm the container daemon/desktop app is actually running.
2. macOS: check the menu-bar icon; Linux: `sudo systemctl start docker`
 (or the daemon's actual service name).
3. Re-verify with `docker info`.

### Image pull fails

**Symptoms:**
```
Error pulling image: connection refused
```

**Options:**
1. Check network connectivity.
2. Configure a registry mirror if the project's docs suggest one.
3. Check whether a corporate proxy is required.
4. Fall back to local/native mode if containers keep failing — this is
 usually the fastest unblock.

---

## Configuration File Issues

### Main config file is missing or invalid

**Symptoms:**
```
Error: could not read <config file>
```

**Options:**
1. Regenerate it with the project's documented "generate config" command,
 or copy from the example file.
2. Check syntax (for YAML: consistent indentation, no tabs, a space
 after each colon); validate with a linter/formatter if one is
 available.

### A required secret/API key is not configured

**Symptoms:** the service starts but requests fail with authentication
errors.

**Options:**
1. Edit the environment file and set the missing key(s), matching the
 variable names the project's config actually references.
2. Restart services with the documented stop/start sequence for whichever
 mode is in use.
3. Confirm the config file references the environment variable by the
 correct name.

---

## Service Health Check Issues

### Entrypoint is not reachable

**Symptoms:** connection failure when visiting the entrypoint URL.

**Options (local mode):**
1. Confirm the relevant process (app server, reverse proxy) is actually
 running.
2. Check its logs.
3. Check firewall settings if testing from outside the host.

**Options (container mode):**
1. Confirm the relevant container is `Up` (`docker ps`).
2. Check its logs (`docker compose logs <service>` or `docker logs
 <container>`).
3. Check firewall/port-mapping settings.

### Health endpoint fails or times out

**Symptoms:** the documented `/health`-equivalent route errors or hangs.

**Options (local mode):**
1. Check the backend process's logs.
2. Confirm its config file exists and is valid.
3. Confirm dependencies are fully installed.
4. Confirm the process is actually running, not just that the start
 command exited 0.

**Options (container mode):**
1. Check the relevant container's logs.
2. Confirm the config file is correctly mounted into the container.
3. Confirm dependencies inside the image/container are complete.
4. Confirm the container is actually running (not restarting in a
 crash loop — `docker ps` shows restart count).

---

## Common Diagnostic Commands (generic)

### View running project processes (local mode)
```bash
ps aux | grep -E "<process-name-pattern>" | grep -v grep
```
Build `<process-name-pattern>` from what Phase 0.2 discovered — the
project's actual binary/entrypoint names, not an example from another
project.

### View logs
```bash
tail -f <log-directory>/*.log # if the project writes to files
# or, if run in foreground / via a process manager:
<project's documented "show logs" command>
```

### Stop all services
Use the project's own documented stop command (from Phase 0.2) — don't
assume one exists if it doesn't; foreground processes may just need
Ctrl+C or a `kill` of the recorded PID.

### Fully reset the local environment
1. Stop services (documented stop command, or kill recorded PIDs).
2. Clean build artifacts, if the project documents a clean command.
3. Regenerate config (Phase 3.1).
4. Reinstall dependencies (Phase 4.1).
5. Restart (Phase 4.1).

### View all container status
```bash
docker ps -a
docker stats
```

### Enter a container for debugging
```bash
docker exec -it <container-name> sh
```

### Fully reset the container environment
1. Stop and remove containers/volumes: `docker compose down -v` (adjust
 for the project's actual compose file/project name).
2. Clean build artifacts if documented.
3. Regenerate config.
4. Re-init and restart per the project's documented container commands.

---

## Get More Help

If the above doesn't resolve the issue:
1. Check the project's own issue tracker.
2. Re-read its README and any `docs/` directory — the authoritative
 source for that project's specific tooling.
3. Open a new issue with detailed error logs if the problem looks like a
 genuine project bug rather than a local environment gap.
