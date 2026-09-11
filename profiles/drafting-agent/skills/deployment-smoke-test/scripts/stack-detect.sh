#!/usr/bin/env bash
# stack-detect.sh — generic project stack discovery for the Deployment
# Smoke Test skill (Section 4 of SKILL.md).
#
# Prints a best-effort summary of: manifest files found, install/build/
# start/stop commands, and candidate ports/health endpoints. This is a
# starting point for the agent, not ground truth — always cross-check
# against the project's own README when this script's guess and the docs
# disagree (see references/smoke-test-sop.md, Phase 0).
#
# Usage: bash stack-detect.sh [project_root]
set -uo pipefail

ROOT="${1:-.}"
cd "$ROOT" || { echo "Cannot cd into $ROOT"; exit 1; }

echo "== Project root: $(pwd) =="
echo

echo "== Manifest files found =="
for f in README.md README.rst README.txt Makefile package.json \
 pyproject.toml setup.py setup.cfg tox.ini go.mod Cargo.toml \
 docker-compose.yml docker-compose.yaml compose.yml compose.yaml \
 Dockerfile .env.example .env.sample; do
 [ -e "$f" ] && echo " - $f"
done
echo

echo "== Makefile targets (if any) =="
if [ -f Makefile ]; then
 grep -E '^[a-zA-Z0-9_.-]+:' Makefile | sed 's/:.*//' | sort -u | sed 's/^/ - /'
else
 echo " (no Makefile)"
fi
echo

echo "== package.json scripts (if any) =="
if [ -f package.json ] && command -v node >/dev/null 2>&1; then
 node -e "try{const p=require('./package.json'); const s=p.scripts||{}; for (const k in s) console.log(' - '+k+': '+s[k]);}catch(e){console.log(' (could not parse package.json)')}"
elif [ -f package.json ]; then
 echo " (node not available to parse package.json; read it manually)"
else
 echo " (no package.json)"
fi
echo

echo "== Python project config (if any) =="
for f in pyproject.toml tox.ini setup.cfg; do
 if [ -f "$f" ]; then
 echo " --- $f ---"
 sed -n '1,40p' "$f" | sed 's/^/ /'
 fi
done
[ -f pyproject.toml ] || [ -f tox.ini ] || [ -f setup.cfg ] && true || echo " (none found)"
echo

echo "== Container orchestration (if any) =="
for f in docker-compose.yml docker-compose.yaml compose.yml compose.yaml; do
 if [ -f "$f" ]; then
 echo " --- $f: services & ports ---"
 grep -nE '^\s*[a-zA-Z0-9_-]+:\s*$|ports:|healthcheck:|- *"?[0-9]+:[0-9]+"?' "$f" | sed 's/^/ /'
 fi
done
echo

echo "== Candidate ports referenced in env/config examples =="
for f in .env.example .env.sample; do
 if [ -f "$f" ]; then
 grep -inE 'port' "$f" | sed 's/^/ /'
 fi
done
echo

echo "== Candidate health-check mentions in README =="
for f in README.md README.rst README.txt; do
 if [ -f "$f" ]; then
 grep -inE 'health|/healthz|/status|/ping|quick ?start|getting started' "$f" | head -20 | sed 's/^/ /'
 fi
done
echo

echo "== Git info =="
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
 echo " Repo: $(git remote get-url origin 2>/dev/null || echo 'unknown')"
 echo " Branch: $(git branch --show-current 2>/dev/null)"
 echo " Default branch (best guess): $(git remote show origin 2>/dev/null | sed -n '/HEAD branch/s/.*: //p')"
 echo " Last commit: $(git log -1 --oneline 2>/dev/null)"
else
 echo " (not a git repository)"
fi
echo

echo "== Next step =="
echo " Cross-check the above against README.md / CONTRIBUTING.md, then fill in"
echo " Phase 0 of references/smoke-test-sop.md before proceeding to Phase 1."
