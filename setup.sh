#!/usr/bin/env bash
# setup.sh — Cabinet-Office System Setup
# Usage:
#   bash setup.sh              # full setup (pull, merge, verify)
#   bash setup.sh --pull       # pull latest changes only
#   bash setup.sh --merge      # merge master → main locally
#   bash setup.sh --fix-remote # fix remote HEAD to point to main
#   bash setup.sh --verify     # verify system integrity

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
    # Also update the default branch on remote
    git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main 2>/dev/null || true
    ok "Remote HEAD set to main"
}

# ── Pull latest ────────────────────────────────────────────────────
pull_latest() {
    echo "--- Pulling latest changes ---"
    git fetch origin --prune 2>&1 | tail -3
    
    # If local branch is main and remote has master
    if git branch -r | grep -q "origin/master" && git branch -r | grep -q "origin/main"; then
        warn "Both master and remote/main exist — merging..."
        
        # Merge master into main if needed
        git checkout main
        git merge origin/master --no-edit 2>/dev/null || {
            warn "Merge conflict — attempting rebase"
            git merge --abort 2>/dev/null || true
            git rebase origin/master 2>/dev/null || err "Rebase failed — manual intervention needed"
        }
    fi
    
    # Pull from origin/main
    git pull origin main --rebase 2>&1 | tail -3 || {
        warn "Pull with rebase failed — trying merge"
        git pull origin main --no-edit 2>&1 | tail -3
    }
    
    ok "Pulled latest changes"
}

# ── Merge master → main ────────────────────────────────────────────
merge_branches() {
    echo "--- Merging master → main ---"
    git checkout main
    
    # Fetch master
    git fetch origin master 2>&1 | tail -2
    
    # Check if master has commits not in main
    AHEAD=$(git rev-list --count main..origin/master 2>/dev/null || echo "0")
    
    if [ "$AHEAD" -gt 0 ]; then
        warn "master is $AHEAD commits ahead of main — merging..."
        git merge origin/master --no-edit 2>&1 | tail -5
        ok "Merged master → main"
    else
        ok "master is already up to date with main"
    fi
    
    # Push merged main
    git push origin main 2>&1 | tail -3
    ok "Pushed merged main"
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
    
    # Check system files
    for f in system/registry.json system/protocol.md system/cabinet-office.py system/bootstrap.sh; do
        if [ -f "$f" ]; then
            ok "Found: $f"
        else
            err "Missing: $f"
        fi
    done
    
    # Check scripts
    for s in protocol-engine.py context-budget.py output-validator.py dedup-v2.py quality-assessment-v2.py escalation-system-health.py; do
        if [ -f "system/scripts/$s" ]; then
            ok "Script: $s"
        else
            err "Missing script: $s"
        fi
    done
    
    # Check profiles
    PROFILE_COUNT=$(ls -d profiles/*/ 2>/dev/null | wc -l)
    if [ "$PROFILE_COUNT" -ge 11 ]; then
        ok "Profiles: $PROFILE_COUNT agents"
    else
        warn "Profiles: $PROFILE_COUNT (expected 11)"
    fi
    
    echo ""
    echo "--- Quick test ---"
    python3 system/cabinet-office.py status 2>&1 | head -8
}

# ── Import all changes (full sync) ─────────────────────────────────
import_all() {
    echo "╔══════════════════════════════════════════╗"
    echo "║  Cabinet-Office System Setup             ║"
    echo "╚══════════════════════════════════════════╝"
    echo ""
    
    # Step 1: Fix remote HEAD
    fix_remote_head
    echo ""
    
    # Step 2: Pull latest
    pull_latest
    echo ""
    
    # Step 3: Merge if needed
    merge_branches
    echo ""
    
    # Step 4: Verify
    verify_system
    echo ""
    
    ok "Setup complete!"
    echo ""
    echo "Quick commands:"
    echo "  python3 system/cabinet-office.py run \"task\" --tier tier_2"
    echo "  python3 system/cabinet-office.py status"
    echo "  python3 system/cabinet-office.py health"
}

# ── Main ───────────────────────────────────────────────────────────
case "${1:-}" in
    --pull)       pull_latest ;;
    --merge)      merge_branches ;;
    --fix-remote) fix_remote_head ;;
    --verify)     verify_system ;;
    --help|-h)    echo "Usage: bash setup.sh [--pull|--merge|--fix-remote|--verify]" ;;
    *)            import_all ;;
esac
