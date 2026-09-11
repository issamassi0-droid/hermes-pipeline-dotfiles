#!/usr/bin/env bash
# model-gateway.sh — Dynamic model selection gateway
set -eo pipefail

SYSTEM_ROOT="$(cd "$(dirname "$0")" && pwd)"
MODEL_REGISTRY="$SYSTEM_ROOT/model-registry.json"
PREFERENCES_FILE="$SYSTEM_ROOT/model-preferences.json"
LOG_DIR="$SYSTEM_ROOT/ledger/model-logs"
CACHE_DIR="$SYSTEM_ROOT/ledger/model-cache"

mkdir -p "$LOG_DIR" "$CACHE_DIR"

now() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
today() { date -u +"%Y-%m-%d"; }

# ── select: pick best model ───────────────────────────────────────
cmd_select() {
  local task="${1:-general}" complexity="${2:-medium}" agent="${3:-unknown}"
  MODEL_REGISTRY="$MODEL_REGISTRY" PREFERENCES_FILE="$PREFERENCES_FILE" \
    python3 - "$task" "$complexity" "$agent" << 'PYEOF'
import json, sys, os, pathlib
task, complexity, agent = sys.argv[1], sys.argv[2], sys.argv[3]
reg = json.loads(pathlib.Path(os.environ["MODEL_REGISTRY"]).read_text())
prefs = {}
pp = os.environ.get("PREFERENCES_FILE", "")
if pp and pathlib.Path(pp).exists():
    prefs = json.loads(pathlib.Path(pp).read_text())
tier_map = {"low": "standard", "medium": "standard_plus", "high": "capable", "critical": "capable"}
min_tier = tier_map.get(complexity, "standard")
tier_order = ["lightweight", "standard", "standard_plus", "capable"]
enabled = [m for m in reg["models"] if m.get("enabled")]
candidates = [m for m in enabled if tier_order.index(m["tier"]) >= tier_order.index(min_tier)]
if not candidates: candidates = enabled
best = None; best_score = -999
for m in candidates:
    fit = 1.0 if task in m.get("best_for", []) else 0.5
    pk = f"{agent}:{task}"
    pref_score = prefs.get(pk, {}).get("acceptance_rate", 0.5)
    budget_score = 1.0 if m["cost_per_1m_tokens"]["input"] == 0 else 0.7
    speed_score = 1.0 if m["speed"] == "fast" else 0.7
    score = 0.4*fit + 0.25*pref_score + 0.2*budget_score + 0.15*speed_score
    if score > best_score:
        best_score = score; best = m; best["_score"] = round(score, 3)
if best:
    print(json.dumps({
        "selected": best["id"], "provider": best["provider"],
        "tier": best["tier"], "score": best["_score"],
        "reason": f"task={task}, complexity={complexity}",
        "fallback_chain": reg["settings"]["fallback_chain"]
    }))
else:
    print(json.dumps({"error": "no_model_available", "fallback": "human"}))
PYEOF
}

# ── execute: call model ────────────────────────────────────────────
cmd_execute() {
  local model_id="${1:-}" prompt="${2:-}"
  [[ -z "$model_id" ]] && echo '{"error":"no model_id"}' && return 1
  python3 -c "import json;print(json.dumps({'model':'$model_id','status':'dispatched','prompt_tokens':${#prompt},'timestamp':'$(now)'}))"
}

# ── cache-get ─────────────────────────────────────────────────────
cmd_cache_get() {
  local cache_hash="${1:-}" cache_file="$CACHE_DIR/${cache_hash}.json"
  [[ -f "$cache_file" ]] || { echo '{"cache":"miss"}'; return 0; }
  local age=$(( $(date +%s) - $(stat -c %Y "$cache_file") ))
  local ttl=$(python3 -c "import json,pathlib; print(json.loads(pathlib.Path('$MODEL_REGISTRY').read_text())['settings']['cache_ttl_seconds'])")
  if (( age < ttl )); then cat "$cache_file"; else echo '{"cache":"miss","reason":"expired"}'; fi
}

# ── cache-set ─────────────────────────────────────────────────────
cmd_cache_set() {
  local cache_hash="${1:-}" response="${2:-}"
  echo "$response" > "$CACHE_DIR/${cache_hash}.json"
  echo '{"cache":"set"}'
}

# ── log: record model call ────────────────────────────────────────
cmd_log() {
  local model_id="${1:-}" in_tok="${2:-0}" out_tok="${3:-0}" cost="${4:-0}" agent="${5:-}" stage="${6:-}" mission="${7:-}"
  echo "{\"ts\":\"$(now)\",\"model\":\"$model_id\",\"in\":$in_tok,\"out\":$out_tok,\"cost\":$cost,\"agent\":\"$agent\",\"stage\":\"$stage\",\"mission\":\"$mission\"}" >> "$LOG_DIR/$(today).jsonl"
  echo '{"logged":true}'
}

# ── budget: cost summary ──────────────────────────────────────────
cmd_budget() {
  local total=0
  for f in "$LOG_DIR"/*.jsonl; do
    [[ -f "$f" ]] || continue
    total=$(python3 -c "import json; lines=open('$f').readlines(); print(sum(json.loads(l)['cost'] for l in lines)+$total)" 2>/dev/null || echo "$total")
  done
  echo "{\"daily_cost_usd\":$total,\"status\":\"within\"}"
}

# ── status: gateway overview ──────────────────────────────────────
cmd_status() {
  local enabled=$(python3 -c "import json,pathlib; print(len([m for m in json.loads(pathlib.Path('$MODEL_REGISTRY').read_text())['models'] if m.get('enabled')]))" 2>/dev/null || echo 0)
  local cache=$(ls "$CACHE_DIR"/*.json 2>/dev/null | wc -l)
  echo "{\"models_enabled\":$enabled,\"cache_entries\":$cache}"
}

# ── main ──────────────────────────────────────────────────────────
case "${1:-}" in
  select)    cmd_select "${2:-}" "${3:-}" "${4:-}" ;;
  execute)   cmd_execute "${2:-}" "${3:-}" ;;
  cache-get) cmd_cache_get "${2:-}" ;;
  cache-set) cmd_cache_set "${2:-}" "${3:-}" ;;
  log)       cmd_log "${2:-}" "${3:-}" "${4:-}" "${5:-}" "${6:-}" "${7:-}" "${8:-}" ;;
  budget)    cmd_budget ;;
  status)    cmd_status ;;
  *) echo '{"error":"usage: select|execute|cache-get|cache-set|log|budget|status"}' ;;
esac
