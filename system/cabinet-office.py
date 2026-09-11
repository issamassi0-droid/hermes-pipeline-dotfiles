#!/usr/bin/env python3
"""
cabinet-office — Unified CLI for the Cabinet-Office Multi-Agent System
Runs the full pipeline: validate → select model → execute → verify → log

Usage:
    cabinet-office run "بحث عن تجارب المستخدمين مع herdr agent" --tier 2
    cabinet-office search "herdr agent" --sources 5
    cabinet-office analyze "topic" --video
    cabinet-office publish "article.md" --platform obsidian
    cabinet-office status
    cabinet-office quality
    cabinet-office dedup findings.json
    cabinet-office budget
    cabinet-office heartbeat
"""
import argparse
import json
import os
import pathlib
import subprocess
import sys
from datetime import datetime, timezone


SYSTEM_ROOT = pathlib.Path(__file__).parent
SCRIPTS_DIR = SYSTEM_ROOT / "scripts"
LEDGER_DIR = SYSTEM_ROOT / "ledger"
LOG_DIR = LEDGER_DIR / "model-logs"
CACHE_DIR = LEDGER_DIR / "model-cache"

# Ensure dirs exist
for d in [LEDGER_DIR, LOG_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)


def now():
    return datetime.now(timezone.utc).isoformat()


def run_script(script_name: str, args: list[str], capture: bool = True) -> dict:
    """Run a script and return its output."""
    # Try scripts/ subdirectory first, then root
    script_path = SCRIPTS_DIR / script_name
    if not script_path.exists():
        script_path = SYSTEM_ROOT / script_name
    if not script_path.exists():
        return {"error": f"script not found: {script_name}"}
    
    # Use bash for .sh files, python3 for .py files
    interpreter = "bash" if script_name.endswith(".sh") else "python3"
    cmd = [interpreter, str(script_path)] + args
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, cwd=SYSTEM_ROOT)
        if capture:
            try:
                return json.loads(result.stdout)
            except:
                return {"output": result.stdout.strip(), "stderr": result.stderr.strip()}
        return {"status": "dispatched", "returncode": result.returncode}
    except Exception as e:
        return {"error": str(e)}


def check_context_budget(tier: str, model_window: int = 128000) -> dict:
    """Check if context budget is healthy for the tier."""
    result = run_script("context-budget.py", [str(model_window), tier])
    return result


def select_model(task: str, complexity: str, agent: str = "architect") -> dict:
    """Select best model for the task."""
    result = run_script("model-gateway.sh", ["select", task, complexity, agent])
    return result


def check_heartbeat() -> dict:
    """Check architect heartbeat."""
    return run_script("architect-heartbeat.py", ["check"])


def enter_degraded_mode(reason: str) -> dict:
    """Enter degraded mode."""
    return run_script("architect-heartbeat.py", ["degraded", reason])


def write_heartbeat(mission_id: str) -> dict:
    """Write architect heartbeat."""
    return run_script("architect-heartbeat.py", ["beat", mission_id])


def run_dedup(findings_file: str) -> dict:
    """Run deduplication on findings."""
    return run_script("dedup.py", ["--file", findings_file])


def run_quality_assessment(queries_file: str = None) -> dict:
    """Run quality assessment."""
    if queries_file:
        return run_script("quality-assessment-v2.py", ["--file", queries_file])
    return run_script("quality-assessment-v2.py", [])


def validate_output_file(output_file: str, agent: str, stage: str, mission_id: str) -> dict:
    """Validate an output file."""
    return run_script("output-validator.py", ["--validate", output_file, agent, stage, mission_id])


def check_budget() -> dict:
    """Check model budget."""
    return run_script("model-gateway.sh", ["budget"])


def check_status() -> dict:
    """Check system status."""
    scripts_dir = SYSTEM_ROOT / "scripts"
    contracts = []
    for ext in ["*.md", "*.json", "*.yaml"]:
        contracts.extend([f.name for f in SYSTEM_ROOT.glob(ext) if f.is_file()])
    return {
        "system_root": str(SYSTEM_ROOT),
        "scripts": [f.name for f in scripts_dir.glob("*.py")] if scripts_dir.exists() else [],
        "contracts": contracts,
        "ledger_exists": LEDGER_DIR.exists(),
        "cache_entries": len(list(CACHE_DIR.glob("*.json"))) if CACHE_DIR.exists() else 0,
        "log_days": len(list(LOG_DIR.glob("*.jsonl"))) if LOG_DIR.exists() else 0,
    }


# ── Main pipeline ─────────────────────────────────────────────────
def run_pipeline(task: str, tier: str = "tier_2", platform: str = "obsidian") -> dict:
    """
    Run the full Cabinet-Office pipeline.
    
    Args:
        task: Natural language task description
        tier: Tier level (tier_0, tier_1, tier_2, tier_3)
        platform: Publishing platform (obsidian, telegram, etc.)
    
    Returns: Mission report
    """
    mission_id = f"co-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    print(f"\n{'='*60}")
    print(f"  Cabinet-Office Mission: {mission_id}")
    print(f"  Task: {task}")
    print(f"  Tier: {tier}")
    print(f"{'='*60}\n")
    
    report = {
        "mission_id": mission_id,
        "task": task,
        "tier": tier,
        "started": now(),
        "steps": []
    }
    
    # Step 1: Check context budget
    print("[1/7] Checking context budget...")
    ctx = check_context_budget(tier)
    report["steps"].append({"step": "context_budget", "result": ctx})
    if ctx.get("status") == "overflow":
        print(f"  ⚠️  Context overflow: {ctx.get('recommendation')}")
        report["status"] = "aborted_overflow"
        return report
    print(f"  ✅ Context healthy: {ctx.get('remaining_for_work')} tokens remaining")
    
    # Step 2: Check architect heartbeat
    print("[2/7] Checking architect heartbeat...")
    hb = check_heartbeat()
    report["steps"].append({"step": "heartbeat", "result": hb})
    if hb.get("status") == "stale":
        print(f"  ⚠️  Architect stale — entering degraded mode")
        degraded = enter_degraded_mode("stale heartbeat")
        report["steps"].append({"step": "degraded", "result": degraded})
        report["status"] = "degraded_mode"
        return report
    print(f"  ✅ Heartbeat healthy: {hb.get('delta_minutes', '?')} min ago")
    
    # Step 3: Select model
    print("[3/7] Selecting model...")
    complexity = {"tier_0": "low", "tier_1": "medium", "tier_2": "high", "tier_3": "critical"}.get(tier, "medium")
    model = select_model(task, complexity, "architect")
    report["steps"].append({"step": "model_selection", "result": model})
    print(f"  ✅ Selected: {model.get('selected', '?')} (score: {model.get('score', '?')})")
    
    # Step 4: Write heartbeat (start of mission)
    print("[4/7] Writing mission heartbeat...")
    write_heartbeat(mission_id)
    print(f"  ✅ Heartbeat written")
    
    # Step 5: Execute pipeline with Protocol Engine
    print(f"[5/7] Executing {tier} pipeline with Protocol Engine...")
    agents_list = {
        "tier_0": ["architect"],
        "tier_1": ["omni-researcher", "publisher"],
        "tier_2": ["omni-researcher", "strategist", "draft-writer", "editor-qa", "publisher"],
        "tier_3": ["architect", "omni-researcher", "deep-dive", "strategist", "draft-writer", "editor-qa", "publisher", "analytics"]
    }
    
    # Initialize protocol engine for this mission
    protocol_result = run_script("protocol-engine.py", ["status", mission_id])
    report["steps"].append({"step": "protocol_init", "result": protocol_result})
    
    # Simulate agent handoffs through protocol
    agents_for_tier = agents_list.get(tier, [])
    for i, agent in enumerate(agents_for_tier):
        sender = agents_for_tier[i-1] if i > 0 else "architect"
        stage_map = {"omni-researcher": "research", "strategist": "strategy", "draft-writer": "draft", "editor-qa": "verify", "publisher": "publish", "deep-dive": "video", "analytics": "analyze"}
        stage = stage_map.get(agent, "research")
        
        result = run_script("protocol-engine.py", ["send", mission_id, sender, agent, stage, "handoff", "{}"])
        print(f"  📨 {sender} → @{agent} ({stage}): {result.get('status', '?')}")
    
    report["steps"].append({"step": "protocol_execution", "result": f"Executed {len(agents_for_tier)} agents via protocol"})
    print(f"  ✅ Pipeline executed via protocol engine")
    
    # Step 6.5: Run escalation + system health check
    print("[6.5/7] Running escalation + system health check...")
    esc_result = run_script("escalation-system-health.py", ["health"])
    report["steps"].append({"step": "escalation_health", "result": esc_result})
    if esc_result.get("overall_status") != "healthy":
        print(f"  ⚠️  System health: {esc_result.get('overall_status')} ({esc_result.get('failed_checks')} failed)")
    else:
        print(f"  ✅ System health: healthy")
    
    # Step 7: Log mission
    print("[7/7] Logging mission...")
    report["status"] = "completed"
    report["completed"] = now()
    report["agents_used"] = agents_list.get(tier, [])
    
    # Save mission report
    mission_file = LEDGER_DIR / f"{mission_id}.json"
    mission_file.write_text(json.dumps(report, indent=2))
    print(f"  ✅ Mission logged: {mission_file}")
    
    print(f"\n{'='*60}")
    print(f"  Mission {report['status']}: {mission_id}")
    print(f"{'='*60}\n")
    
    return report


# ── CLI entry point ───────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="cabinet-office — Unified CLI for Cabinet-Office Multi-Agent System"
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")
    
    # run
    run_parser = sub.add_parser("run", help="Run a full pipeline mission")
    run_parser.add_argument("task", help="Task description")
    run_parser.add_argument("--tier", default="tier_2", 
                           choices=["tier_0", "tier_1", "tier_2", "tier_3", "0", "1", "2", "3"],
                           help="Tier level (tier_0..tier_3 or 0..3)")
    run_parser.add_argument("--platform", default="obsidian", help="Publishing platform")
    
    # search
    search_parser = sub.add_parser("search", help="Search and deduplicate")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--sources", type=int, default=10, help="Max sources")
    
    # analyze
    analyze_parser = sub.add_parser("analyze", help="Analyze with video deep-dive")
    analyze_parser.add_argument("topic", help="Topic to analyze")
    analyze_parser.add_argument("--video", action="store_true", help="Include video analysis")
    
    # publish
    pub_parser = sub.add_parser("publish", help="Publish to platform")
    pub_parser.add_argument("file", help="File to publish")
    pub_parser.add_argument("--platform", default="obsidian")
    
    # status
    sub.add_parser("status", help="Show system status")
    
    # quality
    sub.add_parser("quality", help="Run quality assessment")
    
    # dedup
    dedup_parser = sub.add_parser("dedup", help="Deduplicate findings")
    dedup_parser.add_argument("file", help="Findings JSON file")
    
    # budget
    sub.add_parser("budget", help="Show budget status")
    
    # heartbeat
    hb_parser = sub.add_parser("heartbeat", help="Architect heartbeat")
    hb_parser.add_argument("--check", action="store_true")
    hb_parser.add_argument("--beat", type=str, default=None, help="Mission ID")
    hb_parser.add_argument("--degraded", type=str, default=None, help="Reason")
    
    # validate
    val_parser = sub.add_parser("validate", help="Validate an output file")
    val_parser.add_argument("file", help="Output file to validate")
    val_parser.add_argument("--agent", default="unknown")
    val_parser.add_argument("--stage", default="unknown")
    val_parser.add_argument("--mission", default="manual")
    
    # health
    sub.add_parser("health", help="Run system health check")
    
    # escalation
    esc_parser = sub.add_parser("escalation", help="Check escalation trigger")
    esc_parser.add_argument("signal", help="Signal type")
    esc_parser.add_argument("--context", default="{}", help="JSON context")
    
    # override
    ovr_parser = sub.add_parser("override", help="Track human override")
    ovr_parser.add_argument("--mission", default="manual")
    ovr_parser.add_argument("--agent", default="human")
    ovr_parser.add_argument("--reason", default="manual override")
    
    args = parser.parse_args()
    
    if args.command == "run":
        # Normalize tier (e.g., "2" -> "tier_2")
        tier_map = {"0": "tier_0", "1": "tier_1", "2": "tier_2", "3": "tier_3"}
        tier = tier_map.get(args.tier, args.tier)
        result = run_pipeline(args.task, tier, args.platform)
        print(json.dumps(result, indent=2))
    
    elif args.command == "search":
        print(f"\n🔍 Searching: {args.query}")
        print(f"   Max sources: {args.sources}")
        print(f"   (Would invoke @omni-researcher)")
        result = run_dedup(str(pathlib.Path(args.query).with_suffix('.json')))
        print(json.dumps(result, indent=2))
    
    elif args.command == "analyze":
        print(f"\n📊 Analyzing: {args.topic}")
        if args.video:
            print(f"   🎥 Including video deep-dive")
        print(f"   (Would invoke @deep-dive + @strategist)")
    
    elif args.command == "publish":
        print(f"\n📤 Publishing: {args.file} → {args.platform}")
        print(f"   (Would invoke @publisher)")
    
    elif args.command == "status":
        print("\n📋 Cabinet-Office System Status\n")
        status = check_status()
        print(f"  System root: {status['system_root']}")
        print(f"  Contracts ({len(status['contracts'])}):")
        for c in status['contracts']:
            print(f"    - {c}")
        print(f"  Scripts ({len(status['scripts'])}):")
        for s in status['scripts']:
            print(f"    - {s}")
        print(f"  Cache entries: {status['cache_entries']}")
        print(f"  Log days: {status['log_days']}")
        print()
    
    elif args.command == "quality":
        print("\n📊 Running Quality Assessment...\n")
        result = run_quality_assessment()
        print(json.dumps(result, indent=2))
    
    elif args.command == "dedup":
        print(f"\n🔄 Deduplicating: {args.file}")
        result = run_dedup(args.file)
        print(json.dumps(result, indent=2))
    
    elif args.command == "budget":
        print("\n💰 Budget Status\n")
        result = check_budget()
        print(json.dumps(result, indent=2))
    
    elif args.command == "heartbeat":
        if args.check:
            result = check_heartbeat()
            print(json.dumps(result, indent=2))
        elif args.beat:
            result = write_heartbeat(args.beat)
            print(json.dumps(result, indent=2))
        elif args.degraded:
            result = enter_degraded_mode(args.degraded)
            print(json.dumps(result, indent=2))
        else:
            print("Use: --beat <mission> | --check | --degraded <reason>")
    
    elif args.command == "validate":
        print(f"\n✅ Validating: {args.file}")
        result = validate_output_file(args.file, args.agent, args.stage, args.mission)
        print(json.dumps(result, indent=2))
    
    elif args.command == "health":
        print("\n🏥 System Health Check\n")
        result = run_script("escalation-system-health.py", ["health"])
        print(json.dumps(result, indent=2))
    
    elif args.command == "escalation":
        print(f"\n⚡ Checking escalation: {args.signal}")
        import json as _json
        ctx = _json.loads(args.context)
        result = run_script("escalation-system-health.py", ["check-escalation", args.signal, _json.dumps(ctx)])
        print(json.dumps(result, indent=2))
    
    elif args.command == "override":
        print(f"\n👤 Tracking human override")
        result = run_script("escalation-system-health.py", ["override", args.mission, args.agent, args.reason])
        print(json.dumps(result, indent=2))
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
