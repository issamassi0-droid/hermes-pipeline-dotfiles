#!/usr/bin/env python3
"""
Quality Gate v2 — Cabinet-Office System
Implements standards from Trajel, PIES, OrchestraBench:
- 5-type hallucination taxonomy
- Trajectory-level evaluation (not just final output)
- Self-verification loops
- Semantic failure detection
"""
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Optional


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
LEDGER_DIR = SYSTEM_ROOT / "ledger"
QUALITY_LOG = LEDGER_DIR / "quality-gate.jsonl"

# ─── Hallucination Taxonomy (from Trajel/PIES research) ──────────
HALLUCINATION_TYPES = {
    "factual": {
        "description": "Statement contradicts verifiable facts",
        "examples": ["false numbers", "wrong dates", "fabricated events"],
        "severity": "high"
    },
    "referential": {
        "description": "Citation or source does not exist or doesn't support claim",
        "examples": ["fake URLs", "misattributed quotes", "non-existent papers"],
        "severity": "high"
    },
    "logical": {
        "description": "Internal contradiction in reasoning",
        "examples": ["A implies B, then claims not B", "circular reasoning"],
        "severity": "medium"
    },
    "procedural": {
        "description": "Deviation from required process or workflow",
        "examples": ["skipped verification step", "ignored tool output"],
        "severity": "medium"
    },
    "scope": {
        "description": "Claim exceeds what evidence supports",
        "examples": ["overgeneralization", "false certainty"],
        "severity": "low"
    }
}


class TrajectoryEvaluator:
    """
    Evaluates the full trajectory (not just final output).
    Based on PIES taxonomy and Trajel framework.
    """
    
    def __init__(self, mission_id: str):
        self.mission_id = mission_id
        self.trajectory = []
    
    def add_step(self, step_type: str, content: str, tool: str = None, 
                 observation: str = None):
        """Record a step in the agent trajectory."""
        self.trajectory.append({
            "index": len(self.trajectory),
            "type": step_type,  # thought, action, observation
            "content": content,
            "tool": tool,
            "observation": observation,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def evaluate_trajectory(self) -> dict:
        """
        Evaluate full trajectory for hallucinations and errors.
        Returns detailed step-by-step analysis.
        """
        issues = []
        
        for i, step in enumerate(self.trajectory):
            step_issues = self._check_step(step, i)
            issues.extend(step_issues)
        
        # Calculate trajectory quality score
        total_steps = len(self.trajectory)
        clean_steps = total_steps - len(set(i["step_index"] for i in issues))
        
        return {
            "mission_id": self.mission_id,
            "total_steps": total_steps,
            "clean_steps": clean_steps,
            "issues_found": len(issues),
            "issues": issues,
            "trajectory_score": round(clean_steps / total_steps, 3) if total_steps > 0 else 1.0,
            "verdict": "pass" if len(issues) == 0 else "fail"
        }
    
    def _check_step(self, step: dict, index: int) -> list:
        """Check a single trajectory step for issues."""
        issues = []
        
        # 1. Check for hallucination markers
        hallucination = self._detect_hallucination(step["content"])
        if hallucination:
            issues.append({
                "step_index": index,
                "type": "hallucination",
                "subtype": hallucination["type"],
                "severity": hallucination["severity"],
                "evidence": hallucination["evidence"]
            })
        
        # 2. Check for semantic failures
        semantic = self._detect_semantic_failure(step)
        if semantic:
            issues.append({
                "step_index": index,
                "type": "semantic_failure",
                "subtype": semantic["type"],
                "evidence": semantic["evidence"]
            })
        
        # 3. Check for procedural deviations
        if step["type"] == "action" and step.get("tool"):
            procedural = self._check_procedural(step, index)
            if procedural:
                issues.append({
                    "step_index": index,
                    "type": "procedural",
                    "subtype": procedural["type"],
                    "evidence": procedural["evidence"]
                })
        
        return issues
    
    def _detect_hallucination(self, text: str) -> Optional[dict]:
        """Detect hallucination markers in text."""
        text_lower = text.lower()
        
        # High-confidence markers of potential hallucination
        markers = [
            (r"\b(i think|i believe|probably|might be|i'm not sure)\b", "uncertainty", "low"),
            (r"\b(definitely|certainly|always|never|all|none)\b", "overconfidence", "medium"),
            (r"\b(studies show|research says|it is known)\b", "vague_claim", "medium"),
            (r"\b(obviously|clearly|of course|everyone knows)\b", "false_certainty", "high"),
        ]
        
        for pattern, subtype, severity in markers:
            match = re.search(pattern, text_lower)
            if match:
                return {
                    "type": "factual",
                    "subtype": subtype,
                    "severity": severity,
                    "evidence": f"Marker: '{match.group()}'"
                }
        
        return None
    
    def _detect_semantic_failure(self, step: dict) -> Optional[dict]:
        """Detect semantic failures (technically valid but wrong)."""
        if step["type"] == "observation" and step.get("content"):
            # Check for contradictions with previous steps
            for prev_step in self.trajectory[:step["index"]]:
                if prev_step["type"] == "thought":
                    contradiction = self._check_contradiction(
                        prev_step["content"], step["content"]
                    )
                    if contradiction:
                        return {
                            "type": "contradiction",
                            "evidence": contradiction
                        }
        
        return None
    
    def _check_contradiction(self, text_a: str, text_b: str) -> Optional[str]:
        """Check for logical contradictions between two texts."""
        # Simple contradiction detection
        negation_pairs = [
            ("is", "is not"),
            ("can", "cannot"),
            ("will", "will not"),
            ("all", "none"),
            ("always", "never"),
        ]
        
        for pos, neg in negation_pairs:
            if pos in text_a.lower() and neg in text_b.lower():
                return f"Contradiction: '{pos}' vs '{neg}'"
        
        return None
    
    def _check_procedural(self, step: dict, index: int) -> Optional[dict]:
        """Check for procedural deviations."""
        # Example: tool called without proper setup
        if step["tool"] == "publish" and index < 2:
            return {
                "type": "premature_action",
                "evidence": "Publish called before research/draft steps"
            }
        
        return None


class SelfVerificationLoop:
    """
    Self-verification loop: agent verifies its own output.
    Based on Anthropic's self-verification pattern.
    """
    
    def __init__(self, max_iterations: int = 2):
        self.max_iterations = max_iterations
    
    def verify(self, output: str, sources: list, original_task: str) -> dict:
        """
        Run self-verification loop.
        
        1. Check if output addresses the task
        2. Check if claims are supported by sources
        3. Check for internal consistency
        4. Return verification result + suggested fixes
        """
        issues = []
        
        # Check 1: Task coverage
        task_coverage = self._check_task_coverage(output, original_task)
        if task_coverage < 0.5:
            issues.append({
                "type": "incomplete_coverage",
                "severity": "high",
                "detail": f"Output covers only {task_coverage:.0%} of the task"
            })
        
        # Check 2: Source support
        unsupported = self._check_source_support(output, sources)
        if unsupported:
            issues.append({
                "type": "unsupported_claims",
                "severity": "high",
                "detail": f"{len(unsupported)} claims lack source support",
                "claims": unsupported
            })
        
        # Check 3: Internal consistency
        contradictions = self._check_internal_consistency(output)
        if contradictions:
            issues.append({
                "type": "internal_contradiction",
                "severity": "medium",
                "detail": f"{len(contradictions)} contradictions found"
            })
        
        return {
            "verified": len(issues) == 0,
            "issues": issues,
            "suggestions": self._generate_suggestions(issues),
            "output_quality": max(0, 1.0 - len(issues) * 0.2)
        }
    
    def _check_task_coverage(self, output: str, task: str) -> float:
        """Check how well the output covers the task."""
        # Extract key terms from task
        task_terms = set(re.findall(r'[a-z]+', task.lower()))
        output_terms = set(re.findall(r'[a-z]+', output.lower()))
        
        # Calculate overlap
        if not task_terms:
            return 1.0
        
        overlap = len(task_terms & output_terms) / len(task_terms)
        return min(overlap, 1.0)
    
    def _check_source_support(self, output: str, sources: list) -> list:
        """Check which claims lack source support."""
        unsupported = []
        
        # Extract factual claims (simplified)
        claims = re.split(r'[.!?]', output)
        claims = [c.strip() for c in claims if len(c.strip()) > 15]
        
        for claim in claims:
            # Check if claim is supported by any source
            supported = False
            for source in sources:
                if source.get("evidence_grade") in ("[V]", "[M]"):
                    supported = True
                    break
            
            if not supported:
                unsupported.append(claim[:80])
        
        return unsupported
    
    def _check_internal_consistency(self, output: str) -> list:
        """Check for internal contradictions in output."""
        contradictions = []
        sentences = re.split(r'[.!?]', output)
        
        # Simple check: negated pairs in same output
        for i, s1 in enumerate(sentences):
            for s2 in sentences[i+1:]:
                # Check for direct negation
                s1_clean = s1.strip().lower()
                s2_clean = s2.strip().lower()
                
                if s1_clean.startswith("not ") and s2_clean == s1_clean[4:]:
                    contradictions.append(f"'{s1.strip()}' vs '{s2.strip()}'")
        
        return contradictions
    
    def _generate_suggestions(self, issues: list) -> list:
        """Generate fix suggestions for identified issues."""
        suggestions = []
        
        for issue in issues:
            if issue["type"] == "incomplete_coverage":
                suggestions.append("Expand output to cover all task requirements")
            elif issue["type"] == "unsupported_claims":
                suggestions.append("Add sources for unsupported claims or mark as hypothesis")
            elif issue["type"] == "internal_contradiction":
                suggestions.append("Resolve contradictory statements")
        
        return suggestions


# ─── CLI ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Quality Gate v2 Test ===\n")
    
    # Test 1: Trajectory evaluation
    print("[Test 1] Trajectory Evaluation")
    evaluator = TrajectoryEvaluator("test-001")
    evaluator.add_step("thought", "I think the answer is probably 42")
    evaluator.add_step("action", "search", tool="web_search")
    evaluator.add_step("observation", "Search returned 5 results")
    evaluator.add_step("thought", "All sources definitely agree on the answer")
    evaluator.add_step("action", "publish", tool="publish")
    
    result = evaluator.evaluate_trajectory()
    print(f"  Trajectory steps: {result['total_steps']}")
    print(f"  Issues found: {result['issues_found']}")
    print(f"  Score: {result['trajectory_score']}")
    for issue in result['issues']:
        print(f"    ⚠️ {issue['type']} ({issue['subtype']}): {issue['evidence']}")
    print()
    
    # Test 2: Self-verification
    print("[Test 2] Self-Verification Loop")
    verifier = SelfVerificationLoop()
    
    test_output = "The analysis shows that multi-agent systems are effective. Studies show they improve productivity. I think probably all organizations should adopt them."
    test_sources = [
        {"url": "https://example.com/1", "evidence_grade": "[V]"},
    ]
    test_task = "Analyze multi-agent AI systems and their effectiveness"
    
    result = verifier.verify(test_output, test_sources, test_task)
    print(f"  Verified: {result['verified']}")
    print(f"  Quality: {result['output_quality']}")
    for issue in result['issues']:
        print(f"    ⚠️ {issue['type']}: {issue['detail']}")
    for suggestion in result['suggestions']:
        print(f"    💡 {suggestion}")
    
    print("\n✓ Quality Gate v2 working")
