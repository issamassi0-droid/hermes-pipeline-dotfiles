#!/usr/bin/env python3
"""
Context Budget Calculator — measures remaining context after loading contracts.
Prevents context rot by refusing to load contracts that exceed budget.
"""
import json
import math
import pathlib
import sys


SYSTEM_ROOT = pathlib.Path(__file__).parent.parent
REGISTRY = json.loads((SYSTEM_ROOT / "registry.json").read_text())

# Approximate tokens per character for different languages
# English: ~4 chars/token, Arabic: ~2.5 chars/token (more complex script)
CHARS_PER_TOKEN = 3.5


def estimate_tokens(text: str) -> int:
    """Rough token estimate."""
    return math.ceil(len(text) / CHARS_PER_TOKEN)


def load_contract(name: str) -> str:
    """Load a contract file."""
    path = SYSTEM_ROOT / name
    if path.exists():
        return path.read_text()
    return ""


def calculate_context_budget(
    model_context_window: int,
    tier: str,
    system_prompt_overhead: int = 500,
    safety_margin: int = 0.20
) -> dict:
    """
    Calculate how many tokens remain for actual work after loading contracts.
    
    Args:
        model_context_window: Total context window (e.g., 8000, 32000, 128000)
        tier: Tier level ("tier_0", "tier_1", "tier_2", "tier_3")
        system_prompt_overhead: Fixed overhead for system prompt
        safety_margin: Fraction to reserve (0.20 = 20%)
    
    Returns:
        Budget breakdown
    """
    # Get contracts to load for this tier
    tier_overrides = REGISTRY.get("lazy_loading", {}).get("tier_overrides", {})
    tier_config = tier_overrides.get(tier, {})
    max_contracts = tier_config.get("max_contracts", 9)
    force_contracts = tier_config.get("force", [])
    
    priority_order = REGISTRY.get("lazy_loading", {}).get("priority_order", [])
    
    # Select contracts up to max_contracts
    contracts_to_load = []
    for name in priority_order:
        if len(contracts_to_load) >= max_contracts:
            break
        if name in force_contracts or len(contracts_to_load) < max_contracts:
            contracts_to_load.append(name)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_contracts = []
    for c in contracts_to_load:
        if c not in seen:
            seen.add(c)
            unique_contracts.append(c)
    contracts_to_load = unique_contracts
    
    # Calculate token usage
    contract_tokens = {}
    for name in contracts_to_load:
        text = load_contract(name)
        tokens = estimate_tokens(text)
        contract_tokens[name] = tokens
    
    total_contract_tokens = sum(contract_tokens.values())
    safety_tokens = math.floor(model_context_window * safety_margin)
    
    # Remaining budget for actual work
    remaining = model_context_window - system_prompt_overhead - total_contract_tokens - safety_tokens
    
    # Warning if remaining is negative or critically low
    status = "healthy"
    if remaining < 0:
        status = "overflow"
    elif remaining < model_context_window * 0.10:
        status = "critical"
    elif remaining < model_context_window * 0.20:
        status = "low"
    
    return {
        "model_context_window": model_context_window,
        "tier": tier,
        "contracts_loaded": contracts_to_load,
        "contract_tokens": contract_tokens,
        "total_contract_tokens": total_contract_tokens,
        "system_prompt_overhead": system_prompt_overhead,
        "safety_margin_tokens": safety_tokens,
        "remaining_for_work": remaining,
        "utilization_pct": round((total_contract_tokens + system_prompt_overhead + safety_tokens) / model_context_window * 100, 1),
        "status": status,
        "recommendation": _get_recommendation(status, tier)
    }


def _get_recommendation(status: str, tier: str) -> str:
    if status == "overflow":
        return f"OVERFLOW: Reduce contracts for {tier} or upgrade model"
    elif status == "critical":
        return f"CRITICAL: {tier} has <10% context remaining — reduce overhead"
    elif status == "low":
        return f"LOW: {tier} has <20% remaining — monitor closely"
    return f"HEALTHY: {tier} has sufficient context budget"


if __name__ == "__main__":
    if len(sys.argv) > 2:
        window = int(sys.argv[1])
        tier = sys.argv[2]
    else:
        window = 128000
        tier = "tier_2"
    
    result = calculate_context_budget(window, tier)
    print(json.dumps(result, indent=2))
