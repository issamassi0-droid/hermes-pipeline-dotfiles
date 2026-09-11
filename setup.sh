#!/usr/bin/env bash
# setup.sh — Cabinet-Office System Setup v2.0
# Usage:
#   bash setup.sh              # full setup (pull, merge, verify, import)
#   bash setup.sh --pull       # pull latest changes only
#   bash setup.sh --merge      # merge origin/main → local
#   bash setup.sh --verify     # verify system integrity
#   bash setup.sh --import     # import all changes to local
#   bash setup.sh --fix-remote # fix remote HEAD to point to main
#   bash setup.sh --help       # show help

set -eo pipefail

SYSTEM_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$SYSTEM_ROOT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}⚠${NC} $1"; }
err() { echo -e "${RED}✗${NC} $1"; }

# ── Fix remote HEAD ────────────────────────────────────────────────
fix_remote_head() {
    echo "--- Fixing remote HEAD → main ---"
    git remote set-head origin main 2>/dev/null || true
    git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main 2>/dev/null || true
    ok "Remote HEAD set to main"
}

# ── Pull latest ────────────────────────────────────────────────────
pull_latest() {
    echo "--- Pulling latest changes ---"
    git fetch origin --prune 2>&1 | tail -3
    
    # Pull from origin/main
    git pull origin main --rebase 2>&1 | tail -3 || {
        warn "Pull with rebase failed — trying merge"
        git pull origin main --no-edit 2>&1 | tail -3
    }
    
    ok "Pulled latest changes"
}

# ── Merge origin/main → local ──────────────────────────────────────
merge_branches() {
    echo "--- Merging origin/main → local ---"
    git checkout main 2>/dev/null || git checkout -b main origin/main
    
    # Fetch latest
    git fetch origin main 2>&1 | tail -2
    
    # Merge
    git merge origin/main --no-edit 2>&1 | tail -5 || {
        warn "Merge conflict — attempting rebase"
        git merge --abort 2>/dev/null || true
        git rebase origin/main 2>/dev/null || err "Rebase failed — manual intervention needed"
    }
    
    ok "Merged origin/main → local"
}

# ── Verify system ──────────────────────────────────────────────────
verify_system() {
    echo "--- Verifying system integrity ---"
    
    # Check git status
    if [ -z "$(git status --porcelain 2>/dev/null)" ]; then
        ok "Working tree clean"
    else
        warn "Uncommitted changes present"
        git status --short | head -10
    fi
    
    # Check branch
    BRANCH=$(git branch --show-current)
    if [ "$BRANCH" = "main" ]; then
        ok "On branch: main"
    else
        err "Not on main branch (currently: $BRANCH)"
    fi
    
    # Check remote HEAD
    REMOTE_HEAD=$(git remote show origin 2>/dev/null | grep "HEAD branch" | awk '{print $NF}')
    if [ "$REMOTE_HEAD" = "main" ]; then
        ok "Remote HEAD: main"
    else
        warn "Remote HEAD: $REMOTE_HEAD (should be main)"
    fi
    
    # Check all contracts (13 files)
    CONTRACTS=(
        "system/registry.json"
        "system/protocol.md"
        "system/routing.yaml"
        "system/quality-charter.md"
        "system/ledger-schema.json"
        "system/evolution.md"
        "system/constitutional.md"
        "system/quality-metrics.md"
        "system/escalation-criteria.md"
        "system/architect-failover.md"
        "system/system-health.md"
        "system/model-gateway.md"
        "system/model-registry.json"
    )
    
    local contract_ok=0
    local contract_fail=0
    for f in "${CONTRACTS[@]}"; do
        if [ -f "$f" ]; then
            ok "Contract: $f"
            ((contract_ok++))
        else
            err "Missing contract: $f"
            ((contract_fail++))
        fi
    done
    
    # Check all scripts (10 files)
    SCRIPTS=(
        "system/scripts/protocol-engine.py"
        "system/scripts/context-budget.py"
        "system/scripts/architect-heartbeat.py"
        "system/scripts/output-validator.py"
        "system/scripts/dedup.py"
        "system/scripts/dedup-v2.py"
        "system/scripts/quality-assessment.py"
        "system/scripts/quality-assessment-v2.py"
        "system/scripts/escalation-system-health.py"
        "system/scripts/validate-real-output.py"
    )
    
    local script_ok=0
    local script_fail=0
    for s in "${SCRIPTS[@]}"; do
        if [ -f "$s" ]; then
            ok "Script: $s"
            ((script_ok++))
        else
            err "Missing script: $s"
            ((script_fail++))
        fi
    done
    
    # Check CLI and bootstrap
    if [ -f "system/cabinet-office.py" ]; then
        ok "CLI: system/cabinet-office.py"
    else
        err "Missing CLI: system/cabinet-office.py"
    fi
    
    if [ -f "system/bootstrap.sh" ]; then
        ok "Bootstrap: system/bootstrap.sh"
    else
        err "Missing bootstrap: system/bootstrap.sh"
    fi
    
    # Check profiles
    PROFILE_COUNT=$(ls -d profiles/*/ 2>/dev/null | wc -l)
    if [ "$PROFILE_COUNT" -ge 11 ]; then
        ok "Profiles: $PROFILE_COUNT agents"
    else
        warn "Profiles: $PROFILE_COUNT (expected 11)"
    fi
    
    # Check reports
    if [ -f "ObsidianVault/Articles/Cabinet-Office-System-Report-Ar.md" ]; then
        ok "Arabic report"
    else
        warn "Missing Arabic report"
    fi
    
    if [ -f "ObsidianVault/Articles/Cabinet-Office-System-Report-En.md" ]; then
        ok "English report"
    else
        warn "Missing English report"
    fi
    
    echo ""
    echo "--- Summary ---"
    echo "Contracts: $contract_ok OK, $contract_fail missing"
    echo "Scripts: $script_ok OK, $script_fail missing"
    echo "Profiles: $PROFILE_COUNT agents"
}

# ── Import all changes to local ────────────────────────────────────
import_all() {
    echo "╔══════════════════════════════════════════╗"
    echo "║  Cabinet-Office System Setup v2.0       ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    
    # Step 1: Fix remote HEAD
    fix_remote_head
    echo ""
    
    # Step 2: Pull latest
    pull_latest
    echo ""
    
    # Step 3: Merge
    merge_branches
    echo ""
    
    # Step 4: Make scripts executable
    echo "--- Making scripts executable ---"
    chmod +x system/scripts/*.py 2>/dev/null || true
    chmod +x system/scripts/*.sh 2>/dev/null || true
    chmod +x system/cabinet-office.py 2>/dev/null || true
    chmod +x system/bootstrap.sh 2>/dev/null || true
    chmod +x system/model-gateway.sh 2>/dev/null || true
    ok "Scripts executable"
    echo ""
    
    # Step 5: Verify
    verify_system
    echo ""
    
    # Step 6: Quick test
    echo "--- Quick test ---"
    python3 system/cabinet-office.py status 2>&1 | head -8
    echo ""
    
    ok "Setup complete!"
    echo ""
    echo "Quick commands:"
    echo "  python3 system/cabinet-office.py run \"task\" --tier tier_2"
    echo "  python3 system/cabinet-office.py status"
    echo "  python3 system/cabinet-office.py health"
    echo "  python3 system/cabinet-office.py quality"
}

# ── Main ───────────────────────────────────────────────────────────
case "${1:-}" in
    --pull)       pull_latest ;;
    --merge)      merge_branches ;;
    --fix-remote) fix_remote_head ;;
    --verify)     verify_system ;;
    --import)     import_all ;;
    --help|-h)
        echo "Cabinet-Office System Setup v2.0"
        echo ""
        echo "Usage: bash setup.sh [option]"
        echo ""
        echo "Options:"
        echo "  --pull       Pull latest changes from origin/main"
        echo "  --merge      Merge origin/main into local branch"
        echo "  --fix-remote Fix remote HEAD to point to main"
        echo "  --verify     Verify system integrity"
        echo "  --import     Full import (pull + merge + verify + test)"
        echo "  --help       Show this help"
        echo ""
        echo "Without options: runs full import"
        ;;
    *) import_all ;;
esac
