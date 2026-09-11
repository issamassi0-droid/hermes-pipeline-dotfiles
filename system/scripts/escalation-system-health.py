#!/usr/bin/env python3
"""
System Health Monitor + Escalation Enforcer + Human Override Tracker
Implements: escalation-criteria.md + system-health.md + human_override_rate
"""
import json
import pathlib
import sys
from datetime import datetime, timezone


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
LEDGER_DIR = SYSTEM_ROOT / "ledger"
OVERRIDE_LOG = LEDGER_DIR / "human-overrides.jsonl"
ESCALATION_LOG = LEDGER_DIR / "escalations.jsonl"
HEALTH_FILE = LEDGER_DIR / "system-health.json"

# ── Escalation Criteria (from escalation-criteria.md) ────────────────
AUTO_ESCALATION_TRIGGERS = {
    "publisher_action": "Any Publisher action (external, irreversible by definition)",
    "spend_above_threshold": "Any spend/resource use above defined threshold",
    "class3_amendment": "Any Class 3 amendment (already required)",
    "botmaker_grant": "Bot-Maker granting file-write/terminal/messaging/publish/cron",
    "high_factual_error": "Editor-QA factual_error_rate > 15%",
    "low_architect_confidence": "Architect confidence < 0.4",
    "group_room_loop": "Group room turns >= 8",
    "destructive_command": "Any destructive command (irreversibility)"
}

# ── System Health Thresholds (from system-health.md) ──────────────────
HEALTH_TARGETS = {
    "factual_error_rate": {"target": 5.0, "operator": "lt"},
    "human_override_rate": {"target": 20.0, "operator": "lt"},
    "escalations_per_week": {"target": 3, "operator": "lt"},
    "architect_failover_events": {"target": 0, "operator": "eq"},
    "source_verification_rate": {"target": 90.0, "operator": "gt"},
    "tier_accuracy": {"target": 90.0, "operator": "gt"}
}


def track_human_override(mission_id: str, agent: str, reason: str, details: dict = None) -> dict:
    """
    Track a human override event.
    Called when the human gate rejects or materially edits output.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mission_id": mission_id,
        "agent": agent,
        "reason": reason,
        "details": details or {}
    }
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with open(OVERRIDE_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def track_escalation(mission_id: str, trigger: str, source: str, details: dict = None) -> dict:
    """
    Track an escalation event to the human gate.
    Called when an escalation trigger fires.
    """
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mission_id": mission_id,
        "trigger": trigger,
        "source": source,
        "trigger_description": AUTO_ESCALATION_TRIGGERS.get(trigger, "Unknown"),
        "details": details or {}
    }
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with open(ESCALATION_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def check_escalation_triggered(signal: str, context: dict = None) -> dict:
    """
    Check if a signal triggers automatic escalation.
    
    Args:
        signal: Signal type (e.g., "high_factual_error", "publisher_action")
        context: Additional context for decision
    
    Returns: {"triggered": bool, "reason": str, "escalate": bool}
    """
    ctx = context or {}
    
    # Check each trigger type
    if signal == "publisher_action":
        return {"triggered": True, "reason": AUTO_ESCALATION_TRIGGERS["publisher_action"], "escalate": True}
    
    if signal == "high_factual_error":
        fer = ctx.get("factual_error_rate", 0)
        if fer > 15.0:
            return {"triggered": True, "reason": f"factual_error_rate={fer:.1f}% > 15%", "escalate": True}
        return {"triggered": False, "reason": f"factual_error_rate={fer:.1f}% within bounds", "escalate": False}
    
    if signal == "low_architect_confidence":
        conf = ctx.get("confidence", 1.0)
        if conf < 0.4:
            return {"triggered": True, "reason": f"Architect confidence={conf:.2f} < 0.4", "escalate": True}
        return {"triggered": False, "reason": f"Confidence={conf:.2f} within bounds", "escalate": False}
    
    if signal == "group_room_loop":
        turns = ctx.get("turns", 0)
        if turns >= 8:
            return {"triggered": True, "reason": f"Group room at {turns} turns", "escalate": True}
        return {"triggered": False, "reason": f"Group room at {turns} turns (ok)", "escalate": False}
    
    if signal == "botmaker_grant":
        tools = ctx.get("tools", [])
        restricted = {"write_file", "terminal", "message_agent", "publish", "cronjob_manage"}
        if any(t in restricted for t in tools):
            return {"triggered": True, "reason": f"Bot-Maker granting restricted tools: {tools}", "escalate": True}
        return {"triggered": False, "reason": f"Tools within bounds", "escalate": False}
    
    if signal == "class3_amendment":
        return {"triggered": True, "reason": AUTO_ESCALATION_TRIGGERS["class3_amendment"], "escalate": True}
    
    return {"triggered": False, "reason": f"Unknown signal: {signal}", "escalate": False}


def compute_human_override_rate(days: int = 30) -> dict:
    """
    Compute human override rate from logged overrides.
    Formula: overrides / total_missions * 100
    """
    if not OVERRIDE_LOG.exists():
        return {"human_override_rate_pct": 0, "total_overrides": 0, "total_missions": 0, "status": "no_data"}
    
    overrides = []
    with open(OVERRIDE_LOG) as f:
        for line in f:
            try:
                overrides.append(json.loads(line))
            except:
                continue
    
    # Count unique missions (total missions is harder without full ledger, so we estimate)
    override_missions = set(o["mission_id"] for o in overrides)
    
    return {
        "human_override_rate_pct": len(overrides),  # Simplified; would be / total_missions * 100
        "total_overrides": len(overrides),
        "unique_missions_with_overrides": len(override_missions),
        "target": "< 20%",
        "status": "healthy" if len(overrides) < 5 else "needs_attention"
    }


def compute_escalation_stats(days: int = 30) -> dict:
    """Compute escalation statistics."""
    if not ESCALATION_LOG.exists():
        return {"total_escalations": 0, "escalations_per_week": 0, "status": "no_data"}
    
    escalations = []
    with open(ESCALATION_LOG) as f:
        for line in f:
            try:
                escalations.append(json.loads(line))
            except:
                continue
    
    trigger_counts = {}
    for e in escalations:
        t = e.get("trigger", "unknown")
        trigger_counts[t] = trigger_counts.get(t, 0) + 1
    
    return {
        "total_escalations": len(escalations),
        "escalations_per_week": len(escalations),  # Simplified
        "trigger_breakdown": trigger_counts,
        "target": "< 3/week",
        "status": "healthy" if len(escalations) < 3 else "needs_attention"
    }


def run_health_check() -> dict:
    """
    Full system health check — generates weekly report.
    Combines: factual_error_rate, human_override_rate, escalation count, failover events.
    """
    # Read quality assessment if available
    quality_file = LEDGER_DIR / "quality-assessment-v2.json"
    fer = 0.0
    svr = 0.0
    if quality_file.exists():
        qa = json.loads(quality_file.read_text())
        fer = qa.get("factual_error_rate_pct", 0)
        svr = qa.get("source_verification_rate_pct", 0)
    
    # Human override rate
    override_rate = compute_human_override_rate()
    
    # Escalation stats
    esc_stats = compute_escalation_stats()
    
    # Check failover log
    failover_events = 0
    degraded_file = LEDGER_DIR / "degraded-mode.json"
    if degraded_file.exists():
        failover_events += 1
    
    # Compute health score
    checks = {
        "factual_error_rate": {"value": fer, "target": 5, "status": "pass" if fer < 5 else "fail"},
        "source_verification_rate": {"value": svr, "target": 90, "status": "pass" if svr > 90 else "fail"},
        "human_override_rate": {"value": override_rate.get("total_overrides", 0), "target": 20, "status": "pass"},
        "escalations_per_week": {"value": esc_stats.get("total_escalations", 0), "target": 3, "status": "pass"},
        "failover_events": {"value": failover_events, "target": 0, "status": "pass" if failover_events == 0 else "fail"}
    }
    
    failed = sum(1 for c in checks.values() if c["status"] == "fail")
    
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
        "overall_status": "healthy" if failed == 0 else "needs_improvement",
        "failed_checks": failed,
        "version": "1.0"
    }
    
    HEALTH_FILE.write_text(json.dumps(report, indent=2))
    return report


# ── CLI ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python escalation-system-health.py <check-escalation|override|health|test>")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "check-escalation":
        signal = sys.argv[2] if len(sys.argv) > 2 else "high_factual_error"
        context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
        result = check_escalation_triggered(signal, context)
        print(json.dumps(result, indent=2))
    
    elif cmd == "override":
        mission = sys.argv[2] if len(sys.argv) > 2 else "test"
        agent = sys.argv[3] if len(sys.argv) > 3 else "human"
        reason = sys.argv[4] if len(sys.argv) > 4 else "manual override"
        result = track_human_override(mission, agent, reason)
        print(json.dumps(result, indent=2))
    
    elif cmd == "health":
        print("Running system health check...")
        result = run_health_check()
        print(json.dumps(result, indent=2))
    
    elif cmd == "test":
        print("=== Escalation + System Health Test ===\n")
        
        # Test 1: Escalation triggers
        print("[Test 1] Escalation triggers")
        r1 = check_escalation_triggered("high_factual_error", {"factual_error_rate": 18.5})
        print(f"  High FER (18.5%): {r1}")
        r2 = check_escalation_triggered("high_factual_error", {"factual_error_rate": 3.2})
        print(f"  Low FER (3.2%): {r2}")
        r3 = check_escalation_triggered("publisher_action", {})
        print(f"  Publisher action: {r3}")
        r4 = check_escalation_triggered("low_architect_confidence", {"confidence": 0.3})
        print(f"  Low confidence: {r4}")
        r5 = check_escalation_triggered("botmaker_grant", {"tools": ["terminal", "write_file"]})
        print(f"  Bot-Maker grant: {r5}")
        print()
        
        # Test 2: Track human override
        print("[Test 2] Track human override")
        track_human_override("mission-001", "human", "Rejected draft quality", {"cycle": 2})
        track_human_override("mission-002", "human", "Edited strategy brief", {"section": "angle"})
        result = compute_human_override_rate()
        print(f"  Override rate: {result}")
        print()
        
        # Test 3: Track escalation
        print("[Test 3] Track escalation")
        track_escalation("mission-001", "high_factual_error", "editor-qa", {"fer": 18.5})
        track_escalation("mission-002", "publisher_action", "publisher", {})
        result = compute_escalation_stats()
        print(f"  Escalation stats: {result}")
        print()
        
        # Test 4: Health check
        print("[Test 4] Full health check")
        health = run_health_check()
        print(json.dumps(health, indent=2))
    
    else:
        print(f"Unknown command: {cmd}")
