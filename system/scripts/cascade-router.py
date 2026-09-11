#!/usr/bin/env python3
"""
Cascade Router — Cabinet-Office System
Starts with cheap model, escalates only when needed.
Based on Sedai's cascade routing pattern.
"""
import json
import pathlib
import time
from datetime import datetime, timezone
from typing import Optional


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
MODEL_REGISTRY = SYSTEM_ROOT / "model-registry.json"
CASCADE_LOG = SYSTEM_ROOT / "ledger" / "cascade-decisions.jsonl"

# ─── Cascade Configuration ────────────────────────────────────────
CASCADE_CHAIN = [
 {"id": "meituan-longcat-2.0-free", "tier": "standard"},
 {"id": "ling-3.0-flash-fin-free", "tier": "standard_plus"},
 # Add more models as needed: claude-sonnet, gpt-4o, etc.
]


class CascadeRouter:
 """
 Starts with cheap/fast model.
 Escalates to stronger model only if the cheap one fails or struggles.
 
 Escalation signals:
 - Multiple tool call failures
 - Repetitive output (stuck in loop)
 - Low confidence in response
 - Explicit request for escalation
 """
 
 def __init__(self, model_chain: list = None):
 self.model_chain = model_chain or CASCADE_CHAIN
 self.escalation_count = 0
 
 def route_with_fallback(self, task: str, agent: str = "architect") -> dict:
 """
 Route task through cascade chain.
 Tries each model in order until one succeeds.
 """
 results = []
 
 for i, model in enumerate(self.model_chain):
 model_id = model["id"]
 tier = model["tier"]
 
 try:
 # Simulate model call (in production: actual API call)
 success, output, confidence = self._try_model(task, model_id)
 
 result = {
 "model": model_id,
 "tier": tier,
 "success": success,
 "confidence": confidence,
 "output_preview": output[:100] if output else None,
 "escalated": False
 }
 
 if success and confidence >= 0.6:
 result["escalated"] = (i > 0)
 results.append(result)
 return self._build_decision(task, agent, results, final_model=model_id)
 else:
 # Failed or low confidence — escalate
 result["escalated"] = True
 results.append(result)
 continue
 
 except Exception as e:
 # Model failed — escalate
 results.append({
 "model": model_id,
 "tier": tier,
 "success": False,
 "error": str(e),
 "escalated": True
 })
 continue
 
 # All models failed
 return self._build_decision(task, agent, results, final_model="human")
 
 def _try_model(self, task: str, model_id: str) -> tuple:
 """
 Try a model on the task.
 Returns: (success, output, confidence)
 """
 # In production: actual API call
 # Simulated: based on model tier and task complexity
 task_len = len(task)
 has_complex_keywords = any(kw in task.lower() for kw in ["analyze", "design", "compare", "evaluate"])
 
 if "meituan" in model_id:
 # Standard model: good for simple tasks
 if has_complex_keywords or task_len > 200:
 return False, "Task too complex for this tier", 0.3
 return True, "Task completed successfully", 0.8
 
 elif "ling-3.0" in model_id:
 # Standard+ model: good for medium complexity
 if has_complex_keywords and task_len > 300:
 return True, "Task completed with moderate confidence", 0.65
 return True, "Task completed successfully", 0.85
 
 return False, "Unknown model", 0.0
 
 def _build_decision(self, task: str, agent: str, results: list, final_model: str) -> dict:
 """Build the final routing decision."""
 decision = {
 "timestamp": datetime.now(timezone.utc).isoformat(),
 "task": task[:100],
 "agent": agent,
 "final_model": final_model,
 "attempts": len(results),
 "cascade_path": [r["model"] for r in results],
 "escalated": any(r.get("escalated") for r in results),
 "results": results
 }
 
 # Log decision
 CASCADE_LOG.parent.mkdir(parents=True, exist_ok=True)
 with open(CASCADE_LOG, "a") as f:
 f.write(json.dumps(decision) + "\n")
 
 return decision
 
 def get_cascade_stats(self) -> dict:
 """Get cascade routing statistics."""
 if not CASCADE_LOG.exists():
 return {"total_decisions": 0}
 
 with open(CASCADE_LOG) as f:
 decisions = [json.loads(line) for line in f if line.strip()]
 
 if not decisions:
 return {"total_decisions": 0}
 
 escalated = sum(1 for d in decisions if d.get("escalated"))
 avg_attempts = sum(d["attempts"] for d in decisions) / len(decisions)
 
 return {
 "total_decisions": len(decisions),
 "escalated": escalated,
 "escalation_rate": f"{(escalated/len(decisions)*100):.1f}%",
 "average_attempts": round(avg_attempts, 2)
 }


# ─── CLI ──────────────────────────────────────────────────────────
if __name__ == "__main__":
 print("=== Cascade Router Test ===\n")
 
 router = CascadeRouter()
 
 # Test 1: Simple task (should succeed with first model)
 print("[Test 1] Simple task")
 result = router.route_with_fallback("What is the capital of France?", agent="@publisher")
 print(f" Final model: {result['final_model']}")
 print(f" Attempts: {result['attempts']}")
 print(f" Escalated: {result['escalated']}")
 print()
 
 # Test 2: Complex task (should escalate)
 print("[Test 2] Complex task")
 result = router.route_with_fallback(
 "Analyze and compare the architectural patterns of multi-agent AI systems, "
 "evaluating Byzantine fault tolerance, semantic checkpointing, and cascade routing tradeoffs",
 agent="@strategist"
 )
 print(f" Final model: {result['final_model']}")
 print(f" Attempts: {result['attempts']}")
 print(f" Cascade path: {result['cascade_path']}")
 print(f" Escalated: {result['escalated']}")
 print()
 
 # Test 3: Medium task
 print("[Test 3] Medium task")
 result = router.route_with_fallback("Write a 500 word blog post about AI trends", agent="@draft-writer")
 print(f" Final model: {result['final_model']}")
 print(f" Attempts: {result['attempts']}")
 print()
 
 # Stats
 print("[Stats]")
 stats = router.get_cascade_stats()
 print(json.dumps(stats, indent=2))
 
 print("\n✓ Cascade Router working")
