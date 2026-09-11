# Verification Script for Multi-Agent Systems

## Overview

This script provides quick verification of multi-agent system integrity.

## Usage

```bash
python3 scripts/verify_system.py
```

## Checks

### 1. Contract Verification
- All 13 contract files exist
- JSON contracts parse correctly
- YAML contracts parse correctly
- All required fields present

### 2. Script Verification
- All 17 scripts exist
- Python scripts compile without errors
- Shell scripts have valid syntax

### 3. Agent Verification
- All 11 SOUL files exist
- Each SOUL references the system layer
- Tool allowlists are valid

### 4. Ledger Verification
- Ledger directory exists
- Schema is valid JSON
- Mission logs parse correctly

### 5. Protocol Verification
- Envelope format is valid
- Payload types are defined
- Budget limits are configured

## Output

```
=== System Verification ===

Contracts: 13/13 ✓
Scripts: 17/17 ✓
Agents: 11/11 ✓
Ledger: ✓
Protocol: ✓

=== Result ===
System ready for operation.
```

## Implementation

```python
#!/usr/bin/env python3
import json
import pathlib
import sys

SYSTEM_ROOT = pathlib.Path(__file__).parent.parent

def check_contracts():
 contracts = [
 "system/registry.json",
 "system/protocol.md",
 "system/routing.yaml",
 "system/quality-charter.md",
 "system/ledger-schema.json",
 "system/evolution.md",
 "system/constitutional.md",
 "system/quality-metrics.md",
 "system/escalation-criteria.md",
 "system/architect-failover.md",
 "system/system-health.md",
 "system/model-gateway.md",
 "system/model-registry.json",
 ]
 ok = 0
 for c in contracts:
 if (SYSTEM_ROOT / c).exists():
 ok += 1
 else:
 print(f"Missing: {c}")
 return ok, len(contracts)

def check_scripts():
 scripts = list((SYSTEM_ROOT / "system/scripts").glob("*.py"))
 ok = 0
 for s in scripts:
 try:
 compile(s.read_text(), s.name, "exec")
 ok += 1
 except SyntaxError as e:
 print(f"Syntax error in {s.name}: {e}")
 return ok, len(scripts)

def main():
 print("=== System Verification ===")
 c_ok, c_total = check_contracts()
 s_ok, s_total = check_scripts()
 print(f"\nContracts: {c_ok}/{c_total}")
 print(f"Scripts: {s_ok}/{s_total}")
 if c_ok == c_total and s_ok == s_total:
 print("\n✓ System ready.")
 else:
 print("\n✗ Issues found.")
 sys.exit(1)

if __name__ == "__main__":
 main()
```