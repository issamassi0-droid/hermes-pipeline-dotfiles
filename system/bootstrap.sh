#!/usr/bin/env bash
# bootstrap.sh — one-command system boot / restore
# Usage:
#   bash bootstrap.sh              # verify current system state
#   bash bootstrap.sh --install    # (re)install system layer, do not touch SOULs
#   bash bootstrap.sh --restore    # restore SOULs + system layer from backup
#   bash bootstrap.sh --rollback <id>  # roll back a single CHANGELOG entry
#   bash bootstrap.sh --status     # print a status table
set -euo pipefail

HERMES_ROOT="${HERMES_ROOT:-$HOME/.hermes}"
SYSTEM_ROOT="$HERMES_ROOT/system"
PROFILES_ROOT="$HERMES_ROOT/profiles"
LEDGER_ROOT="$SYSTEM_ROOT/ledger"
ARCHIVE_ROOT="$HOME/ObsidianVault/Logs/ledger-archive"
BACKUP_ROOT="$SYSTEM_ROOT/backups"
CHANGELOG="$SYSTEM_ROOT/CHANGELOG.md"

have() { command -v "$1" >/dev/null 2>&1; }

log()  { printf '\033[2m[bootstrap]\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m[ ok ]\033[0m %s\n' "$*"; }
warn() { printf '\033[33m[warn]\033[0m %s\n' "$*"; }
err()  { printf '\033[31m[fail]\033[0m %s\n' "$*" >&2; }

require_files() {
  local missing=0
  for f in registry.json protocol.md ledger-schema.json routing.yaml quality-charter.md evolution.md; do
    if [[ ! -f "$SYSTEM_ROOT/$f" ]]; then
      err "missing: $SYSTEM_ROOT/$f"
      missing=$((missing+1))
    fi
  done
  [[ $missing -eq 0 ]] || return 1
  ok "system layer complete (6 contracts present)"
}

require_dirs() {
  mkdir -p "$LEDGER_ROOT" "$ARCHIVE_ROOT" "$BACKUP_ROOT"
  ok "directories ready: ledger, archive, backups"
}

check_profiles() {
  local names=(analytics architect bot-maker deep-dive draft-writer editor-qa omarchy omni-researcher publisher strategist scout)
  local found=0
  for n in "${names[@]}"; do
    if [[ -f "$PROFILES_ROOT/$n/SOUL.md" ]]; then
      found=$((found+1))
    else
      warn "profile SOUL missing: $n"
    fi
  done
  ok "profiles found: $found/${#names[@]}"
}

check_hermes() {
  if have hermes; then
    ok "hermes CLI present: $(hermes --version 2>/dev/null | head -1)"
  else
    warn "hermes CLI not on PATH — restore will need it"
  fi
}

backup_current() {
  local stamp; stamp=$(date -u +%Y%m%dT%H%M%SZ)
  local dest="$BACKUP_ROOT/$stamp"
  mkdir -p "$dest"
  cp -a "$SYSTEM_ROOT"/* "$dest"/ 2>/dev/null || true
  for n in analytics architect bot-maker deep-dive draft-writer editor-qa omarchy omni-researcher publisher strategist; do
    [[ -f "$PROFILES_ROOT/$n/SOUL.md" ]] && cp -a "$PROFILES_ROOT/$n/SOUL.md" "$dest/$n.SOUL.md"
  done
  ok "backup written: $dest"
}

status_table() {
  printf '\n%-24s %-8s %-10s %s\n' "AGENT" "SOUL" "TIERS" "STATUS"
  printf '%-24s %-8s %-10s %s\n' "------------------------" "------" "--------" "------"
  local data
  if have jq && [[ -f "$SYSTEM_ROOT/registry.json" ]]; then
    data=$(jq -r '.agents[] | [.name, (.tiers_served|join(",")), (.entrypoint|tostring)] | @tsv' "$SYSTEM_ROOT/registry.json")
  else
    data=$'architect\t0,1,2,3\ttrue\nomni-researcher\t1,2,3\tfalse\ndeep-dive\t2,3\tfalse\nstrategist\t2,3\tfalse\ndraft-writer\t2,3\tfalse\neditor-qa\t2,3\tfalse\npublisher\t1,2,3\tfalse\nanalytics\t2,3\tfalse\nbot-maker\tall\ttrue\nomarchy\t0,1\ttrue'
  fi
  while IFS=$'\t' read -r name tiers entry; do
    local soul="missing"
    [[ -f "$PROFILES_ROOT/$name/SOUL.md" ]] && soul="ok"
    printf '%-24s %-8s %-10s %s\n' "$name" "$soul" "$tiers" "$([[ "$entry" == "true" ]] && echo 'entrypoint' || echo 'worker')"
  done <<< "$data"
  printf '\n'
}

cmd_status() {
  require_files
  require_dirs
  check_hermes
  check_profiles
  status_table
}

cmd_install() {
  log "verifying + scaffolding system layer only (SOULs untouched)"
  require_dirs
  require_files || true
  [[ -f "$CHANGELOG" ]] || printf '# System Changelog\n\nFormat: `id | timestamp | target | before-hash | after-hash | proposer | approver | summary`\n\n' > "$CHANGELOG"
  ok "install complete"
}

cmd_restore() {
  local stamp="${1:-}"
  if [[ -z "$stamp" ]]; then
    stamp=$(ls -1 "$BACKUP_ROOT" | sort | tail -1)
    [[ -n "$stamp" ]] || { err "no backups found"; exit 1; }
    warn "no stamp given — using latest: $stamp"
  fi
  local src="$BACKUP_ROOT/$stamp"
  [[ -d "$src" ]] || { err "backup not found: $src"; exit 1; }
  cp -a "$src"/*.json "$SYSTEM_ROOT"/ 2>/dev/null || true
  cp -a "$src"/*.md "$SYSTEM_ROOT"/ 2>/dev/null || true
  cp -a "$src"/*.yaml "$SYSTEM_ROOT"/ 2>/dev/null || true
  for f in "$src"/*.SOUL.md; do
    [[ -e "$f" ]] || continue
    local name; name=$(basename "$f" .SOUL.md)
    cp -a "$f" "$PROFILES_ROOT/$name/SOUL.md"
    ok "restored SOUL: $name"
  done
  ok "restore complete from $src"
}

cmd_rollback() {
  local id="${1:?rollback needs a changelog entry id}"
  [[ -f "$CHANGELOG" ]] || { err "no changelog"; exit 1; }
  warn "rollback not yet automated — grep $CHANGELOG for entry $id and revert manually"
}

case "${1:-}" in
  --install)  cmd_install ;;
  --restore)  shift; cmd_restore "${1:-}" ;;
  --rollback) shift; cmd_rollback "${1:-}" ;;
  --status)   cmd_status ;;
  ""|--check) cmd_status ;;
  *) err "unknown option: $1"; exit 2 ;;
esac
# ── Cron Scheduler (optional) ──────────────────────────────────────
# Usage: echo "0 9 * * * /home/massi/.hermes/system/bootstrap.sh --cron-run" | crontab -
cron_run() {
  echo "[$(date)] ▶ Cron-triggered pipeline start"
  bash /home/massi/.hermes/system/bootstrap.sh --mission "cron-$(date +%Y%m%d%H%M)"
}
export -f cron_run

# ── Dynamic Context Detection (M13) ─────────────────────────────────
# Detects model context window and selects loading profile
detect_context_window() {
  local model="${1:-auto}"
  case "$model" in
    *"gpt-4o"*)           echo "xlarge" ;;
    *"gpt-4o-mini"*)      echo "large"  ;;
    *"gpt-3.5"*)          echo "medium" ;;
    *"claude-sonnet"*)    echo "xlarge" ;;
    *"claude-haiku"*)     echo "large"  ;;
    *"gemini-1.5-pro"*)   echo "max"    ;;
    *"gemini-1.5-flash"*) echo "max"    ;;
    *"grok-3"*)           echo "large"  ;;
    *"grok-4"*)           echo "xlarge" ;;
    *"ling-3.0"*)         echo "large"  ;;
    *)                    echo "medium" ;;
  esac
}

# Returns the contracts to load for a given profile
get_contracts_for_profile() {
  local profile="$1"
  case "$profile" in
    small)    echo "registry.json" ;;
    medium)   echo "registry.json protocol.md routing.yaml" ;;
    large)    echo "registry.json protocol.md routing.yaml quality-charter.md ledger-schema.json evolution.md" ;;
    xlarge)   echo "registry.json protocol.md routing.yaml quality-charter.md ledger-schema.json evolution.md README.md status.html" ;;
    max|*)    echo "registry.json protocol.md routing.yaml quality-charter.md ledger-schema.json evolution.md README.md status.html CHANGELOG.md" ;;
  esac
}

# Check if a tier is compatible with the given context profile
check_tier_compatibility() {
  local profile="$1"
  local tier="$2"
  case "$profile" in
    small)  [[ "$tier" == "tier_0" ]] && return 0 || return 1 ;;
    medium) [[ "$tier" =~ tier_[01] ]] && return 0 || return 1 ;;
    large)  [[ "$tier" =~ tier_[012] ]] && return 0 || return 1 ;;
    xlarge|max) return 0 ;;
    *) return 1 ;;
  esac
}
