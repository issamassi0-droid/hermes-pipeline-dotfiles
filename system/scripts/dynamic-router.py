#!/usr/bin/env python3
"""
Dynamic Router — Cabinet-Office System
Routes tasks to optimal model based on complexity, cost, speed, and historical performance.
Implements patterns from NVIDIA NeMo Switchyard + Sedai + AC Router.
"""
import json
import pathlib
import time
import math
from datetime import datetime, timezone
from typing import Optional


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
LEDGER_DIR = SYSTEM_ROOT / "ledger"
ROUTING_LOG = LEDGER_DIR / "routing-decisions.jsonl"
MODEL_REGISTRY = SYSTEM_ROOT / "model-registry.json"

# ─── Routing Constants ────────────────────────────────────────────
COMPLEXITY_WEIGHT = 0.35
PREFERENCE_WEIGHT = 0.25
COST_WEIGHT = 0.20
SPEED_WEIGHT = 0.15
HISTORY_WEIGHT = 0.05

# Model capability tiers (lower = more capable)
CAPABILITY_TIERS = {
    "lightweight": 0,
    "standard": 1,
    "standard_plus": 2,
    "capable": 3,
    "max": 4
}

# Complexity levels
COMPLEXITY_LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4
}


class DynamicRouter:
    """
    Routes tasks to optimal model based on:
    1. Task complexity (35%)
    2. User preference history (25%)
    3. Cost efficiency (20%)
    4. Speed requirement (15%)
    5. Historical performance (5%)
    """
    
    def __init__(self):
        self.model_registry = self._load_registry()
        self.history = []
    
    def _load_registry(self) -> dict:
        """Load model registry."""
        if MODEL_REGISTRY.exists():
            return json.loads(MODEL_REGISTRY.read_text())
        return {"models": [], "settings": {}}
    
    def _load_history(self) -> list:
        """Load routing history."""
        if ROUTING_LOG.exists():
            with open(ROUTING_LOG) as f:
                return [json.loads(line) for line in f if line.strip()]
        return []
    
    def classify_complexity(self, task: str) -> str:
        """
        Classify task complexity using heuristic rules.
        In production, this would use an LLM classifier.
        """
        task_lower = task.lower()
        
        # Critical indicators
        critical_keywords = ["analyze", "compare", "evaluate", "synthesize", "critique", "design", "architect", "plan"]
        if any(kw in task_lower for kw in critical_keywords):
            return "critical"
        
        # High indicators
        high_keywords = ["research", "write", "create", "develop", "build", "implement", "optimize"]
        if any(kw in task_lower for kw in high_keywords):
            return "high"
        
        # Low indicators
        low_keywords = ["what is", "define", "list", "find", "lookup", "simple", "quick", "yes", "no"]
        if any(kw in task_lower for kw in low_keywords):
            return "low"
        
        return "medium"
    
    def route(self, task: str, agent: str = "architect", 
              prefer_cost: bool = False, prefer_speed: bool = False) -> dict:
        """
        Route a task to the optimal model.
        
        Args:
            task: Task description
            agent: Agent requesting the model
            prefer_cost: Optimize for cost
            prefer_speed: Optimize for speed
            
        Returns: Routing decision with model, score, and reasoning
        """
        complexity = self.classify_complexity(task)
        complexity_level = COMPLEXITY_LEVELS[complexity]
        
        # Get enabled models
        models = [m for m in self.model_registry.get("models", []) if m.get("enabled")]
        
        if not models:
            return {"error": "no_models_available", "fallback": "human"}
        
        # Score each model
        scores = []
        for model in models:
            score = self._score_model(model, complexity_level, agent, prefer_cost, prefer_speed)
            scores.append((model, score))
        
        # Select best model
        scores.sort(key=lambda x: x[1]["total"], reverse=True)
        best_model, best_score = scores[0]
        
        # Create decision
        decision = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task": task[:100],
            "agent": agent,
            "complexity": complexity,
            "selected_model": best_model["id"],
            "provider": best_model["provider"],
            "tier": best_model["tier"],
            "score": round(best_score["total"], 3),
            "breakdown": best_score["breakdown"],
            "alternatives": [
                {"model": m["id"], "score": round(s["total"], 3)}
                for m, s in scores[1:3]
            ],
            "reasoning": self._generate_reasoning(best_model, best_score, complexity)
        }
        
        # Log decision
        ROUTING_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(ROUTING_LOG, "a") as f:
            f.write(json.dumps(decision) + "\n")
        
        return decision
    
    def _score_model(self, model: dict, complexity_level: int, 
                     agent: str, prefer_cost: bool, prefer_speed: bool) -> dict:
        """Score a model for the given task."""
        
        # 1. Capability fit (can it handle the complexity?)
        model_tier = CAPABILITY_TIERS.get(model.get("tier", "standard"), 1)
        if model_tier >= complexity_level:
            capability_score = 1.0
        elif model_tier == complexity_level - 1:
            capability_score = 0.6
        else:
            capability_score = 0.2
        
        # 2. Task fit (is it good for this type of task?)
        best_for = model.get("best_for", [])
        task_lower = agent.lower()
        task_fit = 1.0 if any(bf in task_lower for bf in best_for) else 0.7
        
        # 3. Cost score (free = 1.0, paid = 0.7)
        cost_score = 1.0 if model["cost_per_1m_tokens"]["input"] == 0 else 0.7
        
        # 4. Speed score (fast = 1.0, medium = 0.7, slow = 0.4)
        speed_score = 1.0 if model.get("speed") == "fast" else 0.7
        
        # 5. Historical performance (from history)
        history_score = self._get_history_score(model["id"], agent)
        
        # Apply preference weights
        cost_weight = COST_WEIGHT * (1.5 if prefer_cost else 1.0)
        speed_weight = SPEED_WEIGHT * (1.5 if prefer_speed else 1.0)
        capability_weight = COMPLEXITY_WEIGHT
        preference_weight = PREFERENCE_WEIGHT
        history_weight = HISTORY_WEIGHT
        
        # Normalize weights
        total_weight = capability_weight + preference_weight + cost_weight + speed_weight + history_weight
        
        # Calculate weighted score
        total = (
            capability_weight * capability_score +
            preference_weight * task_fit +
            cost_weight * cost_score +
            speed_weight * speed_score +
            history_weight * history_score
        ) / total_weight
        
        return {
            "total": total,
            "breakdown": {
                "capability": round(capability_score, 3),
                "task_fit": round(task_fit, 3),
                "cost": round(cost_score, 3),
                "speed": round(speed_score, 3),
                "history": round(history_score, 3)
            }
        }
    
    def _get_history_score(self, model_id: str, agent: str) -> float:
        """Get historical performance score for a model-agent pair."""
        history = self._load_history()
        
        relevant = [
            h for h in history
            if h.get("selected_model") == model_id and h.get("agent") == agent
        ]
        
        if not relevant:
            return 0.5  # Neutral if no history
        
        # Calculate average score from recent history
        recent = relevant[-10:]  # Last 10 decisions
        avg_score = sum(d.get("score", 0.5) for d in recent) / len(recent)
        
        return min(avg_score, 1.0)
    
    def _generate_reasoning(self, model: dict, score: dict, complexity: str) -> str:
        """Generate human-readable reasoning for the decision."""
        breakdown = score["breakdown"]
        
        reasons = []
        if breakdown["capability"] >= 0.8:
            reasons.append("capability match")
        if breakdown["task_fit"] >= 0.8:
            reasons.append("task specialization")
        if breakdown["cost"] >= 0.9:
            reasons.append("cost efficient")
        if breakdown["speed"] >= 0.9:
            reasons.append("fast response")
        if breakdown["history"] >= 0.7:
            reasons.append("proven track record")
        
        if not reasons:
            reasons.append("best overall fit")
        
        return f"Selected {model['id']} for {complexity} task based on: {', '.join(reasons)}"
    
    def get_routing_stats(self) -> dict:
        """Get routing statistics."""
        history = self._load_history()
        
        if not history:
            return {"total_decisions": 0}
        
        model_counts = {}
        complexity_counts = {}
        avg_score = 0
        
        for h in history:
            model = h.get("selected_model", "unknown")
            complexity = h.get("complexity", "unknown")
            
            model_counts[model] = model_counts.get(model, 0) + 1
            complexity_counts[complexity] = complexity_counts.get(complexity, 0) + 1
            avg_score += h.get("score", 0)
        
        avg_score /= len(history)
        
        return {
            "total_decisions": len(history),
            "model_distribution": model_counts,
            "complexity_distribution": complexity_counts,
            "average_score": round(avg_score, 3)
        }


# ─── CLI ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Dynamic Router Test ===\n")
    
    router = DynamicRouter()
    
    # Test 1: Simple query
    print("[Test 1] Simple query")
    result = router.route("What is the weather today?", agent="@architect")
    print(f"  Selected: {result['selected_model']} (score: {result['score']})")
    print(f"  Complexity: {result['complexity']}")
    print(f"  Reasoning: {result['reasoning']}")
    print()
    
    # Test 2: Research task
    print("[Test 2] Research task")
    result = router.route("Research multi-agent AI systems and compare their architectures", agent="@omni-researcher")
    print(f"  Selected: {result['selected_model']} (score: {result['score']})")
    print(f"  Complexity: {result['complexity']}")
    print(f"  Breakdown: {result['breakdown']}")
    print()
    
    # Test 3: Critical analysis
    print("[Test 3] Critical analysis")
    result = router.route("Analyze the security implications of autonomous AI agents and design a safety framework", agent="@strategist")
    print(f"  Selected: {result['selected_model']} (score: {result['score']})")
    print(f"  Complexity: {result['complexity']}")
    print()
    
    # Test 4: Fast mode
    print("[Test 4] Fast mode (prefer speed)")
    result = router.route("Quick summary of today's news", agent="@publisher", prefer_speed=True)
    print(f"  Selected: {result['selected_model']} (score: {result['score']})")
    print()
    
    # Test 5: Cost mode
    print("[Test 5] Cost mode (prefer cost)")
    result = router.route("Write a blog post about AI trends", agent="@draft-writer", prefer_cost=True)
    print(f"  Selected: {result['selected_model']} (score: {result['score']})")
    print()
    
    # Stats
    print("[Stats]")
    stats = router.get_routing_stats()
    print(json.dumps(stats, indent=2))
    
    print("\n✓ Dynamic Router working")
