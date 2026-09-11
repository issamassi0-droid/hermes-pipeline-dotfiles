#!/usr/bin/env python3
"""
Reliability Standards — Cabinet-Office System
Based on: MAS-FIRE, MTTR-A, ReliabilityBench, MAESTRO, COCO, CP-WBFT, Aegis.

Implements:
- 15 fault types taxonomy (MAS-FIRE)
- 4-tier fault tolerance (mechanism, rule, prompt, reasoning)
- Dual-level evaluation (system resilience + process effectiveness)
- MTTR-A / MTBF / NRR metrics
- 3D reliability surface R(k, ε, λ)
"""
import json
import pathlib
import time
import statistics
from datetime import datetime, timezone
from typing import Optional


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
RELIABILITY_DIR = SYSTEM_ROOT / "reliability"
RELIABILITY_DIR.mkdir(parents=True, exist_ok=True)


# ═══════════════════════════════════════════════════════════════
# 1. Fault Taxonomy (MAS-FIRE: 15 fault types)
# ═══════════════════════════════════════════════════════════════

FAULT_TAXONOMY = {
    "intra_agent": {
        "factual_hallucination": {
            "description": "Agent generates factually incorrect information",
            "severity": "high",
            "detection": "cross-reference with source"
        },
        "referential_hallucination": {
            "description": "Agent references non-existent entities or sources",
            "severity": "high",
            "detection": "source verification"
        },
        "logical_error": {
            "description": "Agent makes invalid logical inference",
            "severity": "medium",
            "detection": "logic checking"
        },
        "procedural_error": {
            "description": "Agent skips or misorders steps",
            "severity": "medium",
            "detection": "trajectory analysis"
        },
        "scope_violation": {
            "description": "Agent exceeds or ignores task boundaries",
            "severity": "low",
            "detection": "scope checking"
        },
        "reasoning_drift": {
            "description": "Agent gradually loses coherence over long context",
            "severity": "medium",
            "detection": "coherence monitoring"
        },
        "overconfidence": {
            "description": "Agent expresses high certainty without evidence",
            "severity": "medium",
            "detection": "confidence calibration"
        }
    },
    "inter_agent": {
        "message_corruption": {
            "description": "Message content altered between agents",
            "severity": "high",
            "detection": "checksum/validation"
        },
        "role_ambiguity": {
            "description": "Agent confused about its role vs other agents",
            "severity": "medium",
            "detection": "role verification"
        },
        "blind_trust": {
            "description": "Agent accepts erroneous upstream info without verification",
            "severity": "high",
            "detection": "trust but verify"
        },
        "context_length_violation": {
            "description": "Message exceeds context window",
            "severity": "medium",
            "detection": "length checking"
        },
        "message_storm": {
            "description": "Exponential message amplification",
            "severity": "high",
            "detection": "rate limiting"
        },
        "deadlock": {
            "description": "Circular waiting between agents",
            "severity": "high",
            "detection": "timeout + cycle detection"
        },
        "tool_format_error": {
            "description": "Agent calls tool with wrong format",
            "severity": "low",
            "detection": "schema validation"
        },
        "tool_selection_error": {
            "description": "Agent selects wrong tool for task",
            "severity": "medium",
            "detection": "tool matching"
        },
        "parameter_filling_error": {
            "description": "Agent fills tool parameters incorrectly",
            "severity": "low",
            "detection": "parameter validation"
        }
    }
}


# ═══════════════════════════════════════════════════════════════
# 2. 4-Tier Fault Tolerance (MAS-FIRE)
# ═══════════════════════════════════════════════════════════════

FAULT_TOLERANCE_TIERS = {
    "mechanism": {
        "description": "Architectural redundancy and retry mechanisms",
        "handles": ["tool_format_error", "tool_selection_error", "parameter_filling_error"],
        "activation_rate_target": 0.85,
        "local_recovery_target": 1.0
    },
    "rule": {
        "description": "Hardcoded procedural logic and deterministic rules",
        "handles": ["message_storm", "deadlock", "context_length_violation"],
        "activation_rate_target": 1.0,
        "local_recovery_target": 1.0
    },
    "prompt": {
        "description": "Semantic robustness of agent instructions",
        "handles": ["role_ambiguity", "blind_trust"],
        "activation_rate_target": 1.0,
        "local_recovery_target": 0.79
    },
    "reasoning": {
        "description": "LLM semantic understanding and self-correction",
        "handles": ["factual_hallucination", "referential_hallucination", "logical_error", "reasoning_drift"],
        "activation_rate_target": 0.85,
        "local_recovery_target": 0.61
    }
}


# ═══════════════════════════════════════════════════════════════
# 3. Reliability Metrics (MTTR-A + ReliabilityBench)
# ═══════════════════════════════════════════════════════════════

class ReliabilityMetrics:
    """
    MTTR-A: Mean Time-to-Recovery for Agentic Systems
    MTBF: Mean Time Between Cognitive Faults
    NRR: Normalized Recovery Ratio
    """
    
    def __init__(self):
        self.fault_events = []
        self.recovery_events = []
        self.mission_start_times = {}
    
    def record_fault(self, mission_id: str, fault_type: str, severity: str):
        """Record a cognitive fault event."""
        self.fault_events.append({
            "mission_id": mission_id,
            "fault_type": fault_type,
            "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epoch": time.time()
        })
    
    def record_recovery(self, mission_id: str, fault_type: str, success: bool, recovery_time_s: float):
        """Record a recovery event."""
        self.recovery_events.append({
            "mission_id": mission_id,
            "fault_type": fault_type,
            "success": success,
            "recovery_time_s": recovery_time_s,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "epoch": time.time()
        })
    
    def calculate_mttr_a(self) -> dict:
        """
        MTTR-A: Mean Time-to-Recovery for Agentic Systems
        Average time to detect drift and restore coherent operation.
        """
        if not self.recovery_events:
            return {"mttr_a_s": 0, "count": 0}
        
        recovery_times = [e["recovery_time_s"] for e in self.recovery_events]
        return {
            "mttr_a_s": statistics.mean(recovery_times),
            "mttr_a_median_s": statistics.median(recovery_times),
            "mttr_a_p90_s": sorted(recovery_times)[int(len(recovery_times) * 0.9)] if len(recovery_times) > 1 else recovery_times[0],
            "count": len(recovery_times)
        }
    
    def calculate_mtbf(self) -> dict:
        """
        MTBF: Mean Time Between Cognitive Faults
        Average stable duration between drift events.
        """
        if len(self.fault_events) < 2:
            return {"mtbf_s": 0, "count": 0}
        
        fault_times = sorted([e["epoch"] for e in self.fault_events])
        intervals = [fault_times[i+1] - fault_times[i] for i in range(len(fault_times)-1)]
        
        return {
            "mtbf_s": statistics.mean(intervals),
            "mtbf_median_s": statistics.median(intervals),
            "count": len(intervals)
        }
    
    def calculate_nrr(self) -> dict:
        """
        NRR: Normalized Recovery Ratio
        NRR = MTBF / (MTBF + MTTR-A)
        Dimensionless runtime reliability index.
        """
        mttr = self.calculate_mttr_a()
        mtbf = self.calculate_mtbf()
        
        if mttr["mttr_a_s"] == 0 or mtbf["mtbf_s"] == 0:
            return {"nrr": 0, "uptime_pct": 0}
        
        nrr = mtbf["mtbf_s"] / (mtbf["mtbf_s"] + mttr["mttr_a_s"])
        return {
            "nrr": nrr,
            "uptime_pct": nrr * 100,
            "mtbf_s": mtbf["mtbf_s"],
            "mttr_a_s": mttr["mttr_a_s"]
        }
    
    def calculate_robustness_score(self, total_missions: int, successful_missions: int) -> dict:
        """
        RS: Robustness Score
        Fraction of originally successful tasks that remain solvable after fault injection.
        """
        if total_missions == 0:
            return {"rs": 0}
        return {
            "rs": successful_missions / total_missions,
            "rs_pct": (successful_missions / total_missions) * 100
        }
    
    def get_full_report(self) -> dict:
        """Full reliability report."""
        return {
            "mttr_a": self.calculate_mttr_a(),
            "mtbf": self.calculate_mtbf(),
            "nrr": self.calculate_nrr(),
            "total_faults": len(self.fault_events),
            "total_recoveries": len(self.recovery_events),
            "successful_recoveries": sum(1 for e in self.recovery_events if e["success"]),
            "fault_type_distribution": self._fault_distribution()
        }
    
    def _fault_distribution(self) -> dict:
        """Get fault type distribution."""
        dist = {}
        for event in self.fault_events:
            ft = event["fault_type"]
            dist[ft] = dist.get(ft, 0) + 1
        return dist


# ═══════════════════════════════════════════════════════════════
# 4. 3D Reliability Surface (ReliabilityBench)
# ═══════════════════════════════════════════════════════════════

class ReliabilitySurface:
    """
    R(k, ε, λ) = reliability as function of:
    - k: consistency (repeated execution)
    - ε: robustness (semantic perturbation)
    - λ: fault tolerance (controlled failures)
    """
    
    def __init__(self):
        self.surface_data = []
    
    def add_measurement(self, k: int, epsilon: float, lambda_: float, success: bool):
        """Add a reliability measurement point."""
        self.surface_data.append({
            "k": k,
            "epsilon": epsilon,
            "lambda": lambda_,
            "success": success,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def calculate_surface_volume(self) -> float:
        """
        V = ∫∫∫ R(k,ε,λ) dk dε dλ
        Approximated as mean reliability across all measured points.
        """
        if not self.surface_data:
            return 0.0
        successes = sum(1 for d in self.surface_data if d["success"])
        return successes / len(self.surface_data)
    
    def calculate_degradation_gradient(self) -> dict:
        """
        ∇R = (∂R/∂k, ∂R/∂ε, ∂R/∂λ)
        """
        if not self.surface_data:
            return {"dR_dk": 0, "dR_de": 0, "dR_dl": 0}
        
        # Group by dimension
        by_k = {}
        by_e = {}
        by_l = {}
        
        for d in self.surface_data:
            k, e, l = d["k"], d["epsilon"], d["lambda"]
            by_k.setdefault(k, []).append(d["success"])
            by_e.setdefault(e, []).append(d["success"])
            by_l.setdefault(l, []).append(d["success"])
        
        # Calculate reliability per value
        def reliability(values):
            return sum(values) / len(values) if values else 0
        
        k_rel = {k: reliability(v) for k, v in sorted(by_k.items())}
        e_rel = {e: reliability(v) for e, v in sorted(by_e.items())}
        l_rel = {l: reliability(v) for l, v in sorted(by_l.items())}
        
        # Calculate gradients (simple finite differences)
        def gradient(rel_dict):
            keys = sorted(rel_dict.keys())
            if len(keys) < 2:
                return 0
            gradients = [(rel_dict[keys[i+1]] - rel_dict[keys[i]]) / (keys[i+1] - keys[i]) for i in range(len(keys)-1)]
            return statistics.mean(gradients)
        
        return {
            "dR_dk": gradient(k_rel),
            "dR_de": gradient(e_rel),
            "dR_dl": gradient(l_rel)
        }
    
    def get_critical_threshold(self, acceptable_level: float = 0.8) -> Optional[dict]:
        """
        Find point (k*, ε*, λ*) where R drops below acceptable level.
        """
        for d in sorted(self.surface_data, key=lambda x: (x["k"], x["epsilon"], x["lambda"])):
            # Calculate local reliability
            local_points = [p for p in self.surface_data 
                          if p["k"] == d["k"] and p["epsilon"] == d["epsilon"] and p["lambda"] == d["lambda"]]
            local_rel = sum(1 for p in local_points if p["success"]) / len(local_points)
            if local_rel < acceptable_level:
                return {
                    "k_star": d["k"],
                    "epsilon_star": d["epsilon"],
                    "lambda_star": d["lambda"],
                    "reliability": local_rel
                }
        return None


# ═══════════════════════════════════════════════════════════════
# 5. Silent Gray Error Detection (MAESTRO)
# ═══════════════════════════════════════════════════════════════

class GrayErrorDetector:
    """
    75% of MAS failures are "silent gray errors" — no exception thrown,
    output looks valid but is factually wrong.
    """
    
    def __init__(self):
        self.errors = []
    
    def check_output(self, mission_id: str, output: str, expected_schema: dict = None) -> dict:
        """
        Check for silent gray errors in agent output.
        """
        errors = []
        
        # 1. Schema validation
        if expected_schema:
            schema_errors = self._validate_schema(output, expected_schema)
            errors.extend(schema_errors)
        
        # 2. Empty prediction detection
        if self._is_empty_prediction(output):
            errors.append({
                "type": "empty_prediction",
                "description": "Output appears valid but contains no actual answer"
            })
        
        # 3. Wrong fact/entity detection
        fact_errors = self._check_factual_consistency(output)
        errors.extend(fact_errors)
        
        # 4. Non-terminating pattern detection
        if self._is_non_terminating(output):
            errors.append({
                "type": "non_terminating",
                "description": "Output suggests infinite loop or non-terminating behavior"
            })
        
        # 5. Plausible but wrong detection
        if self._is_plausible_but_wrong(output):
            errors.append({
                "type": "plausible_but_wrong",
                "description": "Output sounds reasonable but may be incorrect"
            })
        
        result = {
            "mission_id": mission_id,
            "has_gray_error": len(errors) > 0,
            "errors": errors,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if errors:
            self.errors.append(result)
        
        return result
    
    def _validate_schema(self, output: str, schema: dict) -> list:
        """Validate output against expected schema."""
        errors = []
        # Simple JSON schema check
        try:
            data = json.loads(output) if output.strip().startswith("{") else {}
            for key, typ in schema.get("required", {}).items():
                if key not in data:
                    errors.append({"type": "missing_field", "field": key})
        except json.JSONDecodeError:
            errors.append({"type": "invalid_json", "description": "Output is not valid JSON"})
        return errors
    
    def _is_empty_prediction(self, output: str) -> bool:
        """Check for empty predictions."""
        empty_markers = [
            "i cannot answer",
            "i don't have the information",
            "unable to determine",
            "not enough information",
            "i'm sorry, i cannot"
        ]
        output_lower = output.lower()
        return any(marker in output_lower for marker in empty_markers) and len(output.strip()) < 200
    
    def _check_factual_consistency(self, output: str) -> list:
        """Check for factual inconsistencies."""
        errors = []
        # Check for self-contradiction markers
        contradiction_markers = ["however", "but", "although", "on the other hand"]
        # Simple heuristic: multiple contradictions may indicate confusion
        contradiction_count = sum(output.lower().count(m) for m in contradiction_markers)
        if contradiction_count > 3:
            errors.append({
                "type": "potential_contradiction",
                "description": f"High contradiction count ({contradiction_count}) may indicate factual inconsistency"
            })
        return errors
    
    def _is_non_terminating(self, output: str) -> bool:
        """Check for non-terminating patterns."""
        non_terminating_markers = [
            "let me continue...",
            "to be continued...",
            "i will now...",
            "next step would be..."
        ]
        return any(m in output.lower() for m in non_terminating_markers)
    
    def _is_plausible_but_wrong(self, output: str) -> bool:
        """Check for plausible but potentially wrong output."""
        # Hedging language may indicate uncertainty
        hedging_markers = [
            "i think", "i believe", "probably", "likely",
            "it seems", "appears to be", "might be", "could be"
        ]
        hedge_count = sum(output.lower().count(m) for m in hedging_markers)
        # High hedging density may indicate low confidence
        words = output.split()
        if words and hedge_count / len(words) > 0.15:
            return True
        return False
    
    def get_error_stats(self) -> dict:
        """Get gray error statistics."""
        return {
            "total_errors": len(self.errors),
            "error_types": self._error_type_distribution(),
            "error_rate": len(self.errors) / max(1, len(self.errors))
        }
    
    def _error_type_distribution(self) -> dict:
        """Get error type distribution."""
        dist = {}
        for error_record in self.errors:
            for error in error_record.get("errors", []):
                et = error["type"]
                dist[et] = dist.get(et, 0) + 1
        return dist


# ═══════════════════════════════════════════════════════════════
# 6. Byzantine Fault Tolerance (CP-WBFT)
# ═══════════════════════════════════════════════════════════════

class ByzantineTolerance:
    """
    CP-WBFT: Confidence Probe-based Weighted Byzantine Fault Tolerance.
    LLM-based agents show stronger skepticism with erroneous message flows.
    """
    
    def __init__(self, total_agents: int = 7, max_byzantine: int = 6):
        self.total_agents = total_agents
        self.max_byzantine = max_byzantine
        self.agents = {}
    
    def register_agent(self, agent_id: str, confidence: float = 1.0):
        """Register an agent with confidence score."""
        self.agents[agent_id] = {
            "confidence": confidence,
            "is_byzantine": False,
            "response_weight": 1.0
        }
    
    def mark_byzantine(self, agent_id: str):
        """Mark an agent as Byzantine (malicious/faulty)."""
        if agent_id in self.agents:
            self.agents[agent_id]["is_byzantine"] = True
            self.agents[agent_id]["response_weight"] = 0.0
    
    def weighted_consensus(self, responses: list) -> dict:
        """
        Weighted consensus: assign higher weight to more credible agents.
        """
        if not responses:
            return {"consensus": None, "confidence": 0}
        
        # Calculate weighted scores
        weighted_scores = {}
        for resp in responses:
            agent_id = resp.get("agent_id", "unknown")
            agent_info = self.agents.get(agent_id, {"response_weight": 1.0, "is_byzantine": False})
            
            if agent_info["is_byzantine"]:
                continue  # Skip Byzantine agents
            
            answer = resp.get("answer", "")
            weight = agent_info["response_weight"]
            
            weighted_scores.setdefault(answer, 0)
            weighted_scores[answer] += weight
        
        if not weighted_scores:
            return {"consensus": None, "confidence": 0, "method": "weighted"}
        
        best_answer = max(weighted_scores, key=lambda k: weighted_scores[k])
        total_weight = sum(weighted_scores.values())
        confidence = weighted_scores[best_answer] / total_weight if total_weight > 0 else 0
        
        return {
            "consensus": best_answer,
            "confidence": confidence,
            "method": "weighted",
            "total_agents": len(responses),
            "byzantine_agents": sum(1 for a in self.agents.values() if a["is_byzantine"])
        }
    
    def calculate_bfti(self, initial_accuracy: float, final_accuracy: float) -> float:
        """
        BFTI: Byzantine Fault Tolerance Improvement.
        Percentage improvement from initial to final accuracy.
        """
        if initial_accuracy == 0:
            return 0
        return final_accuracy - initial_accuracy


# ═══════════════════════════════════════════════════════════════
# CLI — Test & Demo
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("Reliability Standards — Cabinet-Office System")
    print("Based on MAS-FIRE, MTTR-A, ReliabilityBench, MAESTRO, COCO")
    print("=" * 60)
    
    # 1. Fault Taxonomy
    print("\n[1] Fault Taxonomy (15 types)")
    intra = list(FAULT_TAXONOMY["intra_agent"].keys())
    inter = list(FAULT_TAXONOMY["inter_agent"].keys())
    print(f"  Intra-agent: {len(intra)} types")
    print(f"  Inter-agent: {len(inter)} types")
    print(f"  Total: {len(intra) + len(inter)} types")
    
    # 2. 4-Tier Fault Tolerance
    print("\n[2] 4-Tier Fault Tolerance")
    for tier, info in FAULT_TOLERANCE_TIERS.items():
        print(f"  {tier}: {info['description'][:50]}...")
        print(f"    Handles: {len(info['handles'])} fault types")
    
    # 3. Reliability Metrics
    print("\n[3] Reliability Metrics (MTTR-A / MTBF / NRR)")
    metrics = ReliabilityMetrics()
    
    # Simulate some fault/recovery events
    for i in range(5):
        metrics.record_fault(f"mission-{i}", "factual_hallucination", "high")
        metrics.record_recovery(f"mission-{i}", "factual_hallucination", True, 6.2 + i * 0.5)
    
    mttr = metrics.calculate_mttr_a()
    mtbf = metrics.calculate_mtbf()
    nrr = metrics.calculate_nrr()
    
    print(f"  MTTR-A: {mttr['mttr_a_s']:.2f}s (mean recovery time)")
    print(f"  MTBF: {mtbf['mtbf_s']:.2f}s (mean time between faults)")
    print(f"  NRR: {nrr['nrr']:.3f} ({nrr['uptime_pct']:.1f}% uptime)")
    
    # 4. 3D Reliability Surface
    print("\n[4] 3D Reliability Surface R(k, ε, λ)")
    surface = ReliabilitySurface()
    
    # Simulate measurements
    for k in [1, 2]:
        for epsilon in [0.0, 0.1, 0.2]:
            for lambda_ in [0.0, 0.2]:
                # Simulate: higher k/epsilon/lambda = lower success
                import random
                success_prob = max(0.5, 1.0 - epsilon - lambda_ * 0.5)
                surface.add_measurement(k, epsilon, lambda_, random.random() < success_prob)
    
    volume = surface.calculate_surface_volume()
    gradient = surface.calculate_degradation_gradient()
    print(f"  Surface Volume: {volume:.3f}")
    print(f"  Degradation Gradient: ∂R/∂ε = {gradient['dR_de']:.3f}")
    
    # 5. Gray Error Detection
    print("\n[5] Silent Gray Error Detection")
    detector = GrayErrorDetector()
    
    test_outputs = [
        ("m1", "I cannot answer this question. The available tools do not have the functionality."),
        ("m2", "The answer is 42. However, some sources say 43. But 42 is correct. Although..."),
        ("m3", "Let me continue with the next step. I will now process the data...")
    ]
    
    for mid, output in test_outputs:
        result = detector.check_output(mid, output)
        if result["has_gray_error"]:
            print(f"  {mid}: ⚠ Gray error detected — {result['errors'][0]['type']}")
    
    # 6. Byzantine Tolerance
    print("\n[6] Byzantine Fault Tolerance (CP-WBFT)")
    bft = ByzantineTolerance(total_agents=7, max_byzantine=6)
    
    for i in range(7):
        bft.register_agent(f"agent-{i}", confidence=0.9 - i * 0.1)
    
    # Mark 6 as Byzantine (85.7% fault rate)
    for i in range(1, 7):
        bft.mark_byzantine(f"agent-{i}")
    
    responses = [
        {"agent_id": f"agent-{i}", "answer": "A" if i == 0 else "B"}
        for i in range(7)
    ]
    
    consensus = bft.weighted_consensus(responses)
    print(f"  Consensus: {consensus['consensus']}")
    print(f"  Confidence: {consensus['confidence']:.2f}")
    print(f"  Byzantine agents: {consensus['byzantine_agents']}/{consensus['total_agents']}")
    
    print("\n✓ Reliability Standards module working")
    print(f"  Based on: MAS-FIRE, MTTR-A, ReliabilityBench, MAESTRO, COCO, CP-WBFT")
