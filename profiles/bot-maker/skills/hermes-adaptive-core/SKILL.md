# Hermes Skill Specification

## Overview
- **Name**: `hermes-adaptive-core`
- **Identifier**: `python_automation_agent.hermes_adaptive_core`
- **Version**: `3.7.0`
- **Execution Mode**: `Async / Non-Blocking`
- **Isolation Strategy**: `Circuit Breaker & Isolated Async Boundary`

---

## Metadata Declaration Standard

Every skill module within the directory must export a `__skill_metadata__` dictionary and an asynchronous `execute` function.

```python
__skill_metadata__ = {
 "id": "pandas_data_pipeline_engine",
 "macro_cluster": "python_automation_agent",
 "micro_entity": "pandas_data_pipeline_engine",
 "keywords": [
 "pandas",
 "exchange",
 "matching_algorithm",
 "staff_transfer",
 "csv"
 ],
 "priority": 10,
 "timeout_seconds": 3.0
}

async def execute(payload: dict) -> dict:
 """
 Skill entry point called by IsolatedSkillExecutor.
 """
 # Core processing logic
 return {"status": "completed", "output": payload}
```

---

## Changelog
- **3.7.2**: Generic provider health monitor (multi-provider failover, no proxy restart)
- **3.7.1**: Provider health monitor with auto-reconnect (`provider_health.py`)
- **3.7.0**: LRU query cache, lazy skill loading, fuzzy-match cache function
- **3.6.0**: Circuit breaker per skill, failed-import TTL, watchdog debounce, sys.path leak fix, SkillEntry dataclass, priority-ordered fuzzy routing, health tracking
- **3.5.0**: Initial adaptive routing with lock-free registry

## Architecture
- `LockFreeSkillRegistry` — atomic index pointer, no lock contention
- `IsolatedSkillExecutor` — timeout-bounded async execution with circuit breaker
- `SkillDirectoryWatcher` — debounced filesystem watcher
- `MicroRoutedAdaptiveRouter` — main entry point, routes by exact ID then priority-ordered fuzzy match

## Reference
- `references/optimization-patterns.md` — performance targets, cache/lazy/AST patterns