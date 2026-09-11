#!/usr/bin/env bash
# route-check.sh — generic templated route/health smoke checker for the
# Deployment Smoke Test skill (Section 4 of SKILL.md).
#
# Unlike a project-specific script with a hardcoded route list, this one
# takes the base URL and route list as arguments/env vars — fill them in
# per project from Phase 0.3 / 5.4 of references/smoke-test-sop.md rather
# than assuming any specific path.
#
# Usage:
#   BASE_URL="http://localhost:8080" \
#   ROUTES="/ /health /api/status" \
#   bash route-check.sh
#
# Optional auth support (only if the project's OWN smoke-test tooling
# already creates a disposable test account — don't invent this for a
# project that doesn't already do it):
#   AUTH_LOGIN_URL, AUTH_EMAIL, AUTH_PASSWORD, AUTH_COOKIE_JAR
set -uo pipefail

BASE_URL="${BASE_URL:-http://localhost:8080}"
ROUTES="${ROUTES:-/}"
COOKIE_JAR="${AUTH_COOKIE_JAR:-}"

echo "== Route/health check against $BASE_URL =="

if [ -n "${AUTH_LOGIN_URL:-}" ] && [ -n "${AUTH_EMAIL:-}" ] && [ -n "${AUTH_PASSWORD:-}" ]; then
  COOKIE_JAR="${COOKIE_JAR:-/tmp/route-check-cookies.txt}"
  echo "  Attempting login at $AUTH_LOGIN_URL as $AUTH_EMAIL ..."
  curl -s -o /dev/null -c "$COOKIE_JAR" -b "$COOKIE_JAR" \
    -X POST "$AUTH_LOGIN_URL" \
    -d "email=$AUTH_EMAIL&password=$AUTH_PASSWORD" \
    -w "  Login response: %{http_code}\n" || echo "  Login attempt failed (continuing anonymously)"
fi

pass=0
fail=0

for route in $ROUTES; do
  url="${BASE_URL%/}${route}"
  if [ -n "$COOKIE_JAR" ] && [ -f "$COOKIE_JAR" ]; then
    code=$(curl -s -o /dev/null -w "%{http_code}" -b "$COOKIE_JAR" "$url")
  else
    code=$(curl -s -o /dev/null -w "%{http_code}" "$url")
  fi

  if [[ "$code" =~ ^2[0-9]{2}$ ]] || [[ "$code" =~ ^3[0-9]{2}$ ]]; then
    echo "  [OK]   $route -> $code"
    pass=$((pass+1))
  else
    echo "  [FAIL] $route -> $code"
    fail=$((fail+1))
  fi
done

echo
echo "== Summary: $pass passed, $fail failed =="

[ "$fail" -eq 0 ]
