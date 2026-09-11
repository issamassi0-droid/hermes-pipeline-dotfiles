#!/usr/bin/env python3
"""
Self-Learning Engine — Cabinet-Office System
Extracts learnings from mission history and feeds them back into the pipeline.
Based on GEPA (ICLR 2026) and Hermes Agent's skill generation.
"""
import json
import pathlib
import re
from datetime import datetime, timezone
from typing import Optional


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
LEDGER_DIR = SYSTEM_ROOT / "ledger"
LEARNINGS_FILE = LEDGER_DIR / "learnings.jsonl"
SKILLS_DIR = SYSTEM_ROOT / "skills-generated"


class SelfLearningEngine:
 """
 Self-improvement mechanism:
 1. Extract learnings from mission history
 2. Identify patterns across missions
 3. Generate reusable skills
 4. Feed learnings back into evolution loop
 """
 
 def __init__(self):
 self.learnings = []
 self.skills = []
 SKILLS_DIR.mkdir(parents=True, exist_ok=True)
 
 def extract_learnings(self, mission_id: str, mission_report: dict) -> list:
 """
 Extract learnings from a completed mission.
 
 Learnings categories:
 - tool_usage: Which tools worked/failed
 - quality_issues: What quality problems occurred
 - routing: Which models performed well
 - process: What process improvements were identified
 """
 learnings = []
 
 # 1. Extract from quality issues
 if "quality_issues" in mission_report:
 for issue in mission_report["quality_issues"]:
 learnings.append({
 "category": "quality",
 "type": issue.get("type", "unknown"),
 "description": issue.get("description", ""),
 "mission_id": mission_id,
 "timestamp": datetime.now(timezone.utc).isoformat()
 })
 
 # 2. Extract from tool usage
 if "tool_usage" in mission_report:
 for tool, result in mission_report["tool_usage"].items():
 learnings.append({
 "category": "tool",
 "tool": tool,
 "success": result.get("success", False),
 "description": result.get("description", ""),
 "mission_id": mission_id,
 "timestamp": datetime.now(timezone.utc).isoformat()
 })
 
 # 3. Extract from routing decisions
 if "routing_decisions" in mission_report:
 for decision in mission_report["routing_decisions"]:
 learnings.append({
 "category": "routing",
 "model": decision.get("model"),
 "success": decision.get("success"),
 "score": decision.get("score"),
 "mission_id": mission_id,
 "timestamp": datetime.now(timezone.utc).isoformat()
 })
 
 # 4. Extract from process observations
 if "process_observations" in mission_report:
 for obs in mission_report["process_observations"]:
 learnings.append({
 "category": "process",
 "description": obs,
 "mission_id": mission_id,
 "timestamp": datetime.now(timezone.utc).isoformat()
 })
 
 # Save learnings
 self.learnings.extend(learnings)
 self._save_learnings(learnings)
 
 return learnings
 
 def identify_patterns(self) -> dict:
 """
 Identify patterns across all recorded learnings.
 Returns: Patterns by category with frequency counts.
 """
 patterns = {
 "quality_issues": {},
 "tool_success": {},
 "routing_success": {},
 "process_improvements": {}
 }
 
 for learning in self.learnings:
 category = learning.get("category")
 
 if category == "quality":
 issue_type = learning.get("type", "unknown")
 patterns["quality_issues"][issue_type] = patterns["quality_issues"].get(issue_type, 0) + 1
 
 elif category == "tool":
 tool = learning.get("tool", "unknown")
 if tool not in patterns["tool_success"]:
 patterns["tool_success"][tool] = {"success": 0, "fail": 0}
 if learning.get("success"):
 patterns["tool_success"][tool]["success"] += 1
 else:
 patterns["tool_success"][tool]["fail"] += 1
 
 elif category == "routing":
 model = learning.get("model", "unknown")
 if model not in patterns["routing_success"]:
 patterns["routing_success"][model] = {"success": 0, "fail": 0}
 if learning.get("success"):
 patterns["routing_success"][model]["success"] += 1
 else:
 patterns["routing_success"][model]["fail"] += 1
 
 elif category == "process":
 desc = learning.get("description", "")[:50]
 patterns["process_improvements"][desc] = patterns["process_improvements"].get(desc, 0) + 1
 
 return patterns
 
 def generate_skill(self, pattern: dict) -> Optional[dict]:
 """
 Generate a reusable skill from identified pattern.
 Based on Hermes Agent's skill generation (5+ tool invocations trigger skill).
 """
 skill = None
 
 # Generate quality skill
 if pattern.get("category") == "quality_issue":
 skill = {
 "name": f"quality_check_{pattern.get('issue_type', 'generic')}",
 "category": "quality",
 "description": f"Check for and prevent {pattern.get('issue_type', 'quality')} issues",
 "trigger": pattern.get("description", ""),
 "actions": [
 "Review output for common quality markers",
 "Verify evidence grades on claims",
 "Run self-verification loop"
 ],
 "generated_at": datetime.now(timezone.utc).isoformat(),
 "source_pattern": pattern
 }
 
 # Generate tool skill
 elif pattern.get("category") == "tool_success":
 skill = {
 "name": f"tool_usage_{pattern.get('tool', 'generic')}",
 "category": "tool",
 "description": f"Optimized usage pattern for {pattern.get('tool', 'tool')}",
 "trigger": f"Task requires {pattern.get('tool', 'specific tool')}",
 "actions": pattern.get("successful_actions", []),
 "generated_at": datetime.now(timezone.utc).isoformat(),
 "source_pattern": pattern
 }
 
 # Generate routing skill
 elif pattern.get("category") == "routing_success":
 skill = {
 "name": f"routing_{pattern.get('model', 'generic')}",
 "category": "routing",
 "description": f"Routing pattern for {pattern.get('model', 'model')}",
 "trigger": pattern.get("task_type", "task complexity match"),
 "actions": [
 f"Use {pattern.get('model')} for {pattern.get('task_type', 'similar tasks')}",
 f"Expected score: {pattern.get('expected_score', 'unknown')}"
 ],
 "generated_at": datetime.now(timezone.utc).isoformat(),
 "source_pattern": pattern
 }
 
 if skill:
 self.skills.append(skill)
 self._save_skill(skill)
 
 return skill
 
 def get_relevant_skills(self, task: str, category: str = None) -> list:
 """
 Get skills relevant to a task.
 Simple keyword matching (in production: semantic search).
 """
 relevant = []
 task_lower = task.lower()
 
 for skill in self.skills:
 if category and skill.get("category") != category:
 continue
 
 # Check if skill trigger matches task
 trigger = skill.get("trigger", "").lower()
 if any(word in task_lower for word in trigger.split() if len(word) > 3):
 relevant.append(skill)
 
 return relevant
 
 def _save_learnings(self, learnings: list):
 """Save learnings to disk."""
 LEDGER_DIR.mkdir(parents=True, exist_ok=True)
 with open(LEARNINGS_FILE, "a") as f:
 for learning in learnings:
 f.write(json.dumps(learning) + "\n")
 
 def _save_skill(self, skill: dict):
 """Save skill to disk."""
 skill_file = SKILLS_DIR / f"{skill['name']}.json"
 skill_file.write_text(json.dumps(skill, indent=2))
 
 def get_learning_stats(self) -> dict:
 """Get learning statistics."""
 patterns = self.identify_patterns()
 
 return {
 "total_learnings": len(self.learnings),
 "total_skills_generated": len(self.skills),
 "patterns_identified": patterns,
 "quality_issue_types": len(patterns.get("quality_issues", {})),
 "tool_success_rates": {
 tool: data["success"] / (data["success"] + data["fail"])
 for tool, data in patterns.get("tool_success", {}).items()
 if (data["success"] + data["fail"]) > 0
 }
 }
 
 def get_evolution_proposals(self) -> list:
 """
 Generate evolution proposals based on accumulated learnings.
 Feeds into the evolution loop (evolution.md).
 """
 proposals = []
 patterns = self.identify_patterns()
 
 # Propose quality improvements
 for issue_type, count in patterns.get("quality_issues", {}).items():
 if count >= 3: # Threshold
 proposals.append({
 "target": "quality-charter.md",
 "change": f"Add explicit check for {issue_type} issues",
 "evidence": f"{count} occurrences across missions",
 "risk": "low",
 "class": 1
 })
 
 # Propose routing improvements
 for model, data in patterns.get("routing_success", {}).items():
 total = data["success"] + data["fail"]
 if total >= 5:
 success_rate = data["success"] / total
 if success_rate < 0.6:
 proposals.append({
 "target": "model-registry.json",
 "change": f"Deprioritize {model} (success rate: {success_rate:.0%})",
 "evidence": f"{data['success']}/{total} successes",
 "risk": "low",
 "class": 1
 })
 elif success_rate > 0.9:
 proposals.append({
 "target": "model-registry.json",
 "change": f"Prioritize {model} for similar tasks (success rate: {success_rate:.0%})",
 "evidence": f"{data['success']}/{total} successes",
 "risk": "low",
 "class": 1
 })
 
 return proposals


# ─── CLI ──────────────────────────────────────────────────────────
if __name__ == "__main__":
 print("=== Self-Learning Engine Test ===\n")
 
 engine = SelfLearningEngine()
 
 # Test 1: Extract learnings from a mission
 print("[Test 1] Extract Learnings")
 mission_report = {
 "quality_issues": [
 {"type": "missing_source", "description": "Claim without evidence grade"},
 {"type": "overconfidence", "description": "Used 'definitely' without verification"}
 ],
 "tool_usage": {
 "web_search": {"success": True, "description": "Found 5 relevant sources"},
 "publish": {"success": False, "description": "Failed without verification step"}
 },
 "routing_decisions": [
 {"model": "ling-3.0-flash", "success": True, "score": 0.85},
 {"model": "meituan-longcat", "success": False, "score": 0.3}
 ],
 "process_observations": [
 "Research phase was thorough but verification was skipped",
 "Publishing without QA review caused rejection"
 ]
 }
 
 learnings = engine.extract_learnings("mission-001", mission_report)
 print(f" Extracted {len(learnings)} learnings")
 for l in learnings[:3]:
 print(f" - {l['category']}: {l.get('description', l.get('type', ''))[:50]}")
 print()
 
 # Test 2: Identify patterns
 print("[Test 2] Identify Patterns")
 
 # Add more missions for pattern detection
 for i in range(2, 6):
 report = {
 "quality_issues": [
 {"type": "missing_source", "description": "Claim without evidence"},
 ],
 "tool_usage": {
 "web_search": {"success": True, "description": "Worked well"},
 "publish": {"success": False, "description": "Failed again"}
 },
 "routing_decisions": [
 {"model": "ling-3.0-flash", "success": True, "score": 0.8}
 ]
 }
 engine.extract_learnings(f"mission-00{i}", report)
 
 patterns = engine.identify_patterns()
 print(f" Quality issue types: {patterns['quality_issues']}")
 print(f" Tool success: {patterns['tool_success']}")
 print()
 
 # Test 3: Generate skills
 print("[Test 3] Generate Skills")
 skill_pattern = {
 "category": "quality_issue",
 "issue_type": "missing_source",
 "description": "Claims without evidence grades"
 }
 skill = engine.generate_skill(skill_pattern)
 if skill:
 print(f" Generated: {skill['name']}")
 print(f" Description: {skill['description']}")
 print(f" Actions: {skill['actions']}")
 print()
 
 # Test 4: Evolution proposals
 print("[Test 4] Evolution Proposals")
 proposals = engine.get_evolution_proposals()
 print(f" Proposals: {len(proposals)}")
 for p in proposals:
 print(f" → {p['target']}: {p['change']}")
 print()
 
 # Test 5: Stats
 print("[Test 5] Learning Stats")
 stats = engine.get_learning_stats()
 print(f" Total learnings: {stats['total_learnings']}")
 print(f" Skills generated: {stats['total_skills_generated']}")
 print(f" Tool success rates: {stats['tool_success_rates']}")
 
 print("\n✓ Self-Learning Engine working")
