#!/usr/bin/env python3
"""
Output Validator & Factual Error Tracker — Cabinet-Office System v1.0
- Rejects outputs with ungraded claims
- Measures factual_error_rate against sources
- Tracks errors per mission for the evolution loop
"""
import json
import math
import re
import pathlib
import sys
from collections import Counter
from datetime import datetime, timezone


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
LEDGER_DIR = SYSTEM_ROOT / "ledger"
ERROR_LOG = LEDGER_DIR / "factual-errors.jsonl"
VALIDATION_LOG = LEDGER_DIR / "output-validations.jsonl"

# Evidence grades (must appear after each claim)
EVIDENCE_GRADES = {"[V]", "[M]", "[U]", "[H]", "[X]"}

# Claim separators — how claims are delimited in output
CLAIM_SPLIT_PATTERNS = [
    r'(?:\d+\.\s+)',           # "1. ", "2. ", etc.
    r'(?:[-•*]\s+)',           # "- ", "• ", "* "
    r'(?:\n\s*\n)',            # blank line separator
    r'(?<=\.)\s+(?=[A-Z])',    # sentence boundary
]


def tokenize(text: str) -> set[str]:
    stopwords = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'it', 'its', 'this', 'that',
        'these', 'those', 'i', 'we', 'you', 'he', 'she', 'they', 'them', 'their',
        'from', 'into', 'about', 'between', 'through', 'during', 'before',
        'after', 'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under',
        'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where',
        'why', 'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most',
        'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
        'so', 'than', 'too', 'very', 'just', 'because', 'as', 'until', 'while',
        'if', 'any', 'also', 'new', 'said', 'says', 'say', 'one', 'two',
        'first', 'last', 'long', 'great', 'little', 'right', 'old', 'big',
        'high', 'different', 'small', 'large', 'next', 'early', 'young',
        'important', 'public', 'bad', 'good', 'make', 'made', 'get', 'go',
    }
    return set(w for w in re.findall(r'[a-z]+', text.lower()) if w not in stopwords and len(w) > 2)


def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


def extract_claims(output: str) -> list[dict]:
    """
    Extract claims from agent output.
    Returns list of {"text": "...", "grade": "[V]" or None, "has_grade": bool}
    """
    claims = []
    
    # Try to split by numbered items first
    numbered = re.split(r'(?:\d+\.\s+)', output)
    if len(numbered) > 2:
        chunks = [c.strip() for c in numbered if len(c.strip()) > 15]
    else:
        # Split by sentences
        chunks = [s.strip() for s in re.split(r'(?<=\.)\s+(?=[A-Z])', output) if len(s.strip()) > 15]
    
    for chunk in chunks:
        # Check if chunk ends with an evidence grade
        grade = None
        has_grade = False
        for g in EVIDENCE_GRADES:
            if chunk.rstrip().endswith(g):
                grade = g
                has_grade = True
                break
            # Check if grade appears at end with punctuation
            if re.search(re.escape(g) + r'\s*$', chunk.rstrip()):
                grade = g
                has_grade = True
                break
        
        claims.append({
            "text": chunk.strip(),
            "grade": grade,
            "has_grade": has_grade
        })
    
    return claims


def validate_output(output: str, agent_name: str, stage: str, mission_id: str) -> dict:
    """
    Validate an agent output:
    1. Extract claims
    2. Check each has evidence grade
    3. Count violations
    4. Return validation result
    
    Returns: {"valid": bool, "violations": [...], "claims": [...], "action": "..."}
    """
    claims = extract_claims(output)
    
    violations = []
    for i, claim in enumerate(claims):
        if not claim["has_grade"]:
            violations.append({
                "claim_index": i,
                "claim_text": claim["text"][:100],
                "missing": "evidence_grade"
            })
    
    total_claims = len(claims)
    graded = sum(1 for c in claims if c["has_grade"])
    ungraded = len(violations)
    
    # Action determination
    if ungraded == 0:
        action = "approve"
    elif ungraded <= 2:
        action = "rewrite_once"
    else:
        action = "escalate_to_editor_qa"
    
    result = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mission_id": mission_id,
        "agent": agent_name,
        "stage": stage,
        "total_claims": total_claims,
        "graded_claims": graded,
        "ungraded_claims": ungraded,
        "grading_rate": f"{(graded/total_claims*100):.1f}%" if total_claims > 0 else "N/A",
        "valid": ungraded == 0,
        "action": action,
        "violations": violations
    }
    
    # Log validation
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    with open(VALIDATION_LOG, "a") as f:
        f.write(json.dumps(result) + "\n")
    
    return result


def measure_factual_error(
    output: str,
    sources: list[dict],
    similarity_threshold: float = 0.70
) -> dict:
    """
    Measure factual_error_rate of an output against its sources.
    
    Args:
        output: Agent output text
        sources: [{"url": "...", "text": "...", "evidence_grade": "[V]"}]
        similarity_threshold: Min similarity to count as supported
    
    Returns: {"factual_error_rate_pct": float, "claims": [...], "unsupported": [...]}
    """
    # Extract claims (ignore grades for this check)
    claims = re.split(r'(?<=\.)\s+(?=[A-Z])', output)
    claims = [c.strip() for c in claims if len(c.strip()) > 15]
    
    if not claims:
        return {"factual_error_rate_pct": 0, "claims": [], "unsupported": []}
    
    # Tokenize sources
    source_tokens = []
    for s in sources:
        t = s.get("text", "")
        if t:
            source_tokens.append(tokenize(t))
    
    if not source_tokens:
        return {"factual_error_rate_pct": 100, "claims": claims, "unsupported": claims}
    
    unsupported = []
    supported = []
    
    for claim in claims:
        claim_toks = tokenize(claim)
        best_sim = 0.0
        for st in source_tokens:
            sim = jaccard_similarity(claim_toks, st)
            best_sim = max(best_sim, sim)
        
        if best_sim >= similarity_threshold:
            supported.append({"text": claim[:80], "similarity": round(best_sim, 3)})
        else:
            unsupported.append({"text": claim[:80], "best_similarity": round(best_sim, 3)})
    
    error_rate = (len(unsupported) / len(claims)) * 100 if claims else 0
    
    return {
        "factual_error_rate_pct": round(error_rate, 2),
        "total_claims": len(claims),
        "supported": len(supported),
        "unsupported": len(unsupported),
        "unsupported_details": unsupported,
        "supported_details": supported
    }


def track_factual_error(mission_id: str, agent: str, stage: str, error_rate: float, details: dict):
    """Log a factual error measurement."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mission_id": mission_id,
        "agent": agent,
        "stage": stage,
        "factual_error_rate_pct": error_rate,
        "total_claims": details.get("total_claims", 0),
        "unsupported": details.get("unsupported", 0)
    }
    with open(ERROR_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def get_error_trend(days: int = 7) -> dict:
    """Read error log and compute trend."""
    if not ERROR_LOG.exists():
        return {"error": "no data"}
    
    entries = []
    with open(ERROR_LOG) as f:
        for line in f:
            try:
                entries.append(json.loads(line))
            except:
                continue
    
    if not entries:
        return {"error": "no entries"}
    
    rates = [e["factual_error_rate_pct"] for e in entries]
    return {
        "total_measurements": len(rates),
        "avg_error_rate": round(sum(rates) / len(rates), 2),
        "min_error_rate": min(rates),
        "max_error_rate": max(rates),
        "target": "< 5%",
        "on_track": (sum(rates) / len(rates)) < 5
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Demo with sample data
        sample_output = "The Cabinet-Office system uses a three-layer architecture. The model gateway dynamically selects AI models. The system has 11 agents. Each agent has specific tools and constraints."
        
        sample_sources = [
            {"url": "https://example.com/doc1", "text": "Cabinet-Office is a multi-agent AI system with three-layer architecture constitutional systemic and agentic", "evidence_grade": "[V]"},
            {"url": "https://example.com/doc2", "text": "Model gateway dynamically selects AI models based on task complexity and user preferences with weighted scoring", "evidence_grade": "[V]"},
            {"url": "https://example.com/doc3", "text": "The system comprises 11 intelligent agents each with defined roles tools and constraints", "evidence_grade": "[V]"},
        ]
        
        print("=== Output Validation ===")
        result = validate_output(sample_output, "strategist", "strategy", "demo-001")
        print(json.dumps(result, indent=2))
        
        print("\n=== Factual Error Measurement ===")
        error_result = measure_factual_error(sample_output, sample_sources)
        print(json.dumps(error_result, indent=2))
    
    elif sys.argv[1] == "--validate" and len(sys.argv) > 2:
        # Validate a file
        output_file = pathlib.Path(sys.argv[2])
        output = output_file.read_text()
        result = validate_output(output, sys.argv[3] if len(sys.argv) > 3 else "unknown", sys.argv[4] if len(sys.argv) > 4 else "unknown", sys.argv[5] if len(sys.argv) > 5 else "manual")
        print(json.dumps(result, indent=2))
    
    elif sys.argv[1] == "--trend":
        trend = get_error_trend()
        print(json.dumps(trend, indent=2))
    
    else:
        print("Usage: python output-validator.py [--validate output.json agent stage mission | --trend]")
