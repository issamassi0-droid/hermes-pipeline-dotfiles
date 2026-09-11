#!/usr/bin/env python3
"""
Architect Heartbeat Monitor — detects stalls and triggers failover.
Writes heartbeat every 5 minutes; triggers DEGRADED MODE after 3 misses.
"""
import json
import os
import pathlib
import sys
import time
from datetime import datetime, timezone, timedelta


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
HEARTBEAT_FILE = SYSTEM_ROOT / "ledger" / "architect-heartbeat.json"
LOG_FILE = SYSTEM_ROOT / "ledger" / "architect-heartbeat.log"
STALE_THRESHOLD_MINUTES = 15


def now():
    return datetime.now(timezone.utc).isoformat()


def write_heartbeat(mission_id: str = "idle") -> dict:
    """Write a heartbeat timestamp."""
    hb = {
        "timestamp": now(),
        "mission_id": mission_id,
        "status": "active"
    }
    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT_FILE.write_text(json.dumps(hb))
    
    # Append to log
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(hb) + "\n")
    
    return hb


def check_heartbeat() -> dict:
    """Check if architect heartbeat is fresh."""
    if not HEARTBEAT_FILE.exists():
        return {"status": "no_heartbeat", "action": "enter_degraded_mode"}
    
    hb = json.loads(HEARTBEAT_FILE.read_text())
    last_seen = datetime.fromisoformat(hb["timestamp"])
    now_dt = datetime.now(timezone.utc)
    
    # Handle naive datetime (if stored without timezone)
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    
    delta = now_dt - last_seen
    delta_minutes = delta.total_seconds() / 60
    
    if delta_minutes >= STALE_THRESHOLD_MINUTES:
        return {
            "status": "stale",
            "last_seen": hb["timestamp"],
            "delta_minutes": round(delta_minutes, 1),
            "action": "enter_degraded_mode",
            "message": f"Architect stale for {delta_minutes:.0f} minutes — DEGRADED MODE"
        }
    
    return {
        "status": "healthy",
        "last_seen": hb["timestamp"],
        "delta_minutes": round(delta_minutes, 1),
        "action": "continue"
    }


def enter_degraded_mode(reason: str) -> dict:
    """Trigger degraded mode — pause all missions, notify human."""
    degraded = {
        "timestamp": now(),
        "mode": "DEGRADED",
        "reason": reason,
        "actions": [
            "Pause all in-flight missions",
            "Log as blocker",
            "Notify human directly (not through Architect)",
            "No new missions accepted"
        ]
    }
    degraded_file = SYSTEM_ROOT / "ledger" / "degraded-mode.json"
    degraded_file.write_text(json.dumps(degraded, indent=2))
    return degraded


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python architect-heartbeat.py [beat|check|degraded]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "beat":
        mission = sys.argv[2] if len(sys.argv) > 2 else "idle"
        result = write_heartbeat(mission)
        print(json.dumps(result))
    
    elif cmd == "check":
        result = check_heartbeat()
        print(json.dumps(result))
        if result["action"] == "enter_degraded_mode":
            degraded = enter_degraded_mode(result.get("message", "stale heartbeat"))
            print(json.dumps(degraded))
    
    elif cmd == "degraded":
        reason = sys.argv[2] if len(sys.argv) > 2 else "manual trigger"
        result = enter_degraded_mode(reason)
        print(json.dumps(result))
    
    else:
        print(f"Unknown command: {cmd}")
