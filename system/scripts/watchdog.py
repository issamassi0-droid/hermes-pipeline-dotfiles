#!/usr/bin/env python3
"""
4-Tier Watchdog + Semantic Checkpointing — Cabinet-Office System
Implements production-grade resilience patterns from research.
"""
import json
import pathlib
import time
import hashlib
import threading
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
LEDGER_DIR = SYSTEM_ROOT / "ledger"
CHECKPOINT_DIR = LEDGER_DIR / "checkpoints"
WATCHDOG_LOG = LEDGER_DIR / "watchdog.jsonl"

CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)


# ─── Tier 1: Process Monitor ──────────────────────────────────────
class ProcessMonitor:
    """Monitors agent process health (heartbeat, timeout, stall)."""
    
    def __init__(self, agent: str, timeout: float = 15.0):
        self.agent = agent
        self.timeout = timeout
        self.last_heartbeat = time.time()
        self.status = "healthy"
    
    def beat(self):
        """Record heartbeat."""
        self.last_heartbeat = time.time()
        self.status = "healthy"
    
    def check(self) -> dict:
        """Check if agent is responsive."""
        elapsed = time.time() - self.last_heartbeat
        
        if elapsed > self.timeout * 3:
            self.status = "dead"
        elif elapsed > self.timeout * 2:
            self.status = "stalled"
        elif elapsed > self.timeout:
            self.status = "slow"
        else:
            self.status = "healthy"
        
        return {
            "agent": self.agent,
            "status": self.status,
            "elapsed_seconds": round(elapsed, 1),
            "timeout": self.timeout
        }


# ─── Tier 2: Semantic Checkpoint ──────────────────────────────────
class SemanticCheckpoint:
    """
    Checkpoints agent state after each atomic step.
    On crash, resumes from last checkpoint (not from scratch).
    """
    
    def __init__(self, mission_id: str):
        self.mission_id = mission_id
        self.checkpoints = []
        self.dir = CHECKPOINT_DIR / mission_id
        self.dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, step: str, state: dict) -> dict:
        """Save a semantic checkpoint after completing a step."""
        checkpoint = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step": step,
            "state": state,
            "index": len(self.checkpoints)
        }
        
        # Save to disk
        cp_file = self.dir / f"cp_{checkpoint['index']:04d}.json"
        cp_file.write_text(json.dumps(checkpoint, indent=2))
        
        self.checkpoints.append(checkpoint)
        return checkpoint
    
    def get_latest(self) -> Optional[dict]:
        """Get the latest checkpoint for recovery."""
        if self.checkpoints:
            return self.checkpoints[-1]
        
        # Try loading from disk
        cp_files = sorted(self.dir.glob("cp_*.json"))
        if cp_files:
            latest = json.loads(cp_files[-1].read_text())
            self.checkpoints = [latest]
            return latest
        return None
    
    def recover(self) -> Optional[dict]:
        """Recover from last checkpoint."""
        latest = self.get_latest()
        if latest:
            return {
                "status": "recovered",
                "from_step": latest["step"],
                "from_index": latest["index"],
                "state": latest["state"]
            }
        return {"status": "no_checkpoint"}


# ─── Tier 3: AI Triage Agent ──────────────────────────────────────
class AITriage:
    """
    When mechanical monitoring can't determine the situation,
    a short-lived AI agent analyzes: stuck / waiting / crashed.
    """
    
    def __init__(self, agent: str):
        self.agent = agent
        self.history = []
    
    def analyze(self, recent_output: str, elapsed: float) -> dict:
        """Analyze agent state (simplified rule-based version)."""
        # In production, this would invoke an LLM
        # For now, use heuristic rules
        
        result = {
            "agent": self.agent,
            "verdict": "continue",
            "confidence": 0.0,
            "reasoning": ""
        }
        
        if elapsed > 60:
            result["verdict"] = "kill"
            result["confidence"] = 0.9
            result["reasoning"] = f"No response for {elapsed:.0f}s — likely dead"
        elif elapsed > 30:
            result["verdict"] = "restart"
            result["confidence"] = 0.7
            result["reasoning"] = f"Slow response ({elapsed:.0f}s) — restart recommended"
        elif "error" in recent_output.lower() or "exception" in recent_output.lower():
            result["verdict"] = "restart"
            result["confidence"] = 0.6
            result["reasoning"] = "Error detected in output"
        else:
            result["verdict"] = "continue"
            result["confidence"] = 0.95
            result["reasoning"] = "Agent appears healthy"
        
        self.history.append(result)
        return result


# ─── Tier 4: Quality Gate ─────────────────────────────────────────
class QualityGate:
    """
    Even if agent hasn't crashed, it may produce low quality.
    Quality assurance = highest form of fault tolerance.
    """
    
    def __init__(self):
        self.rules = [
            self._check_evidence_grades,
            self._check_source_count,
            self._check_claim_density,
            self._check_hallucination_markers
        ]
    
    def evaluate(self, output: str, sources: list) -> dict:
        """Run quality checks on agent output."""
        issues = []
        
        for rule in self.rules:
            issue = rule(output, sources)
            if issue:
                issues.append(issue)
        
        passed = len(issues) == 0
        
        return {
            "passed": passed,
            "issues": issues,
            "score": max(0, 1.0 - len(issues) * 0.2),
            "recommendation": "accept" if passed else "revise"
        }
    
    def _check_evidence_grades(self, output: str, sources: list) -> Optional[str]:
        """Check if claims have evidence grades."""
        ungraded = sum(1 for s in sources if s.get("evidence_grade") in ("[U]", "[H]", "[X]", None))
        if ungraded > len(sources) * 0.5:
            return f"{ungraded}/{len(sources)} sources ungraded"
        return None
    
    def _check_source_count(self, output: str, sources: list) -> Optional[str]:
        """Check minimum source count."""
        if len(sources) < 2:
            return "Insufficient sources (minimum 2)"
        return None
    
    def _check_claim_density(self, output: str, sources: list) -> Optional[str]:
        """Check if output has enough substance."""
        if len(output) < 100:
            return "Output too short (< 100 chars)"
        return None
    
    def _check_hallucination_markers(self, output: str, sources: list) -> Optional[str]:
        """Check for potential hallucination markers."""
        markers = ["i think", "i believe", "probably", "might be", "i'm not sure"]
        found = [m for m in markers if m.lower() in output.lower()]
        if len(found) > 3:
            return f"Hallucination markers detected: {found}"
        return None


# ─── Main Watchdog (4-Tier) ───────────────────────────────────────
class Watchdog:
    """
    4-tier watchdog system:
    1. Process Monitor (heartbeat/timeout)
    2. Semantic Checkpoint (resume from crash)
    3. AI Triage (diagnose unclear cases)
    4. Quality Gate (validate output quality)
    """
    
    def __init__(self, mission_id: str):
        self.mission_id = mission_id
        self.monitors = {}
        self.checkpoint = SemanticCheckpoint(mission_id)
        self.triage = {}
        self.quality_gate = QualityGate()
    
    def register_agent(self, agent: str, timeout: float = 15.0):
        """Register an agent for monitoring."""
        self.monitors[agent] = ProcessMonitor(agent, timeout)
        self.triage[agent] = AITriage(agent)
    
    def heartbeat(self, agent: str):
        """Record agent heartbeat."""
        if agent in self.monitors:
            self.monitors[agent].beat()
    
    def save_checkpoint(self, step: str, state: dict):
        """Save a semantic checkpoint."""
        return self.checkpoint.save(step, state)
    
    def check_all(self) -> dict:
        """Run full system check."""
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mission_id": self.mission_id,
            "agents": {},
            "overall": "healthy"
        }
        
        for agent, monitor in self.monitors.items():
            check = monitor.check()
            results["agents"][agent] = check
            
            if check["status"] in ("dead", "stalled"):
                results["overall"] = "degraded"
                
                # Tier 3: AI Triage for unclear cases
                triage_result = self.triage[agent].analyze(
                    recent_output=check.get("last_output", ""),
                    elapsed=check["elapsed_seconds"]
                )
                results["agents"][agent]["triage"] = triage_result
        
        return results
    
    def validate_output(self, output: str, sources: list) -> dict:
        """Tier 4: Quality gate validation."""
        return self.quality_gate.evaluate(output, sources)
    
    def do_recover(self) -> dict:
        """Recover from last checkpoint."""
        return self.checkpoint.recover()


# ─── CLI ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== 4-Tier Watchdog Test ===\n")
    
    wd = Watchdog("test-mission-001")
    wd.register_agent("@omni-researcher")
    wd.register_agent("@strategist")
    
    # Tier 1: Process monitoring
    print("[Tier 1] Process Monitor")
    wd.heartbeat("@omni-researcher")
    wd.heartbeat("@strategist")
    check = wd.check_all()
    print(f"  Overall: {check['overall']}")
    for agent, status in check['agents'].items():
        print(f"  {agent}: {status['status']}")
    print()
    
    # Tier 2: Semantic checkpoint
    print("[Tier 2] Semantic Checkpoint")
    wd.save_checkpoint("research_complete", {
        "sources": 5,
        "claims": 8,
        "confidence": 0.82
    })
    wd.save_checkpoint("strategy_built", {
        "angle": "multi-agent architecture",
        "structure": "3-layer"
    })
    recovery = wd.do_recover()
    print(f"  Recovery: {recovery}")
    print()
    
    # Tier 3: AI Triage
    print("[Tier 3] AI Triage")
    triage = wd.triage["@omni-researcher"].analyze(
        recent_output="Research complete with 5 sources",
        elapsed=45.0
    )
    print(f"  Verdict: {triage['verdict']} (confidence: {triage['confidence']})")
    print(f"  Reasoning: {triage['reasoning']}")
    print()
    
    # Tier 4: Quality Gate
    print("[Tier 4] Quality Gate")
    test_output = "The analysis shows that multi-agent systems are effective."
    test_sources = [
        {"url": "https://example.com/1", "evidence_grade": "[V]"},
        {"url": "https://example.com/2", "evidence_grade": "[M]"}
    ]
    quality = wd.validate_output(test_output, test_sources)
    print(f"  Passed: {quality['passed']}")
    print(f"  Score: {quality['score']}")
    print(f"  Issues: {quality['issues']}")
    print()
    
    print("✓ 4-Tier Watchdog working")
