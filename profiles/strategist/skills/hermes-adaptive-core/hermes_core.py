#!/usr/bin/env python3
"""
Hermes Core v3.6 - Adaptive Skill Router & Isolation System
Handles lock-free skill indexing, directory isolation, dynamic reloading,
circuit-breaker execution, and non-blocking async execution.
"""

import os
import sys
import time
import asyncio
import logging
import importlib.util
import signal
import ast
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Set, Callable

logger = logging.getLogger("HermesCore")

# Optional Watchdog integration with graceful fallback
try:
 from watchdog.events import FileSystemEvent, FileSystemEventHandler
 from watchdog.observers import Observer
 WATCHDOG_AVAILABLE = True
except ImportError:
 WATCHDOG_AVAILABLE = False
 FileSystemEventHandler = object
 FileSystemEvent = object
 Observer = None

# Directories and files to strictly ignore during skill indexing
EXCLUDED_DIRECTORIES: Set[str] = {
 ".venv", "venv", "__pycache__", "tests", "test",
 "site-packages", ".git", ".pytest_cache", "node_modules",
 "dist", "build", ".eggs",
}

EXCLUDED_FILES: Set[str] = {
 "__init__.py", "setup.py", "conftest.py", "test_runner.py",
 "patch_router.py",
}

# Failed-import backoff: module_name -> (first_failure_time, retry_after_seconds)
_failed_imports: Dict[str, float] = {}
_FAILED_IMPORT_TTL = 300 # retry after 5 minutes

# Watchdog debounce: path -> last-fire timestamp
_watchdog_last_fire: Dict[str, float] = {}
_WATCHDOG_DEBOUNCE_SEC = 2.0

# Query→skill LRU cache: avoids repeated fuzzy scans
_query_cache: Dict[str, Optional[str]] = {}
_QUERY_CACHE_MAX = 128


@dataclass
class SkillHealth:
 failures: int = 0
 last_failure: float = 0.0
 circuit_open: bool = False
 circuit_opened_at: float = 0.0
 CIRCUIT_RESET_SEC = 60.0

 def record_failure(self) -> None:
 self.failures += 1
 self.last_failure = time.monotonic()
 if self.failures >= 3:
 self.circuit_open = True
 self.circuit_opened_at = time.monotonic()

 def record_success(self) -> None:
 self.failures = 0
 self.circuit_open = False

 def can_execute(self) -> bool:
 if not self.circuit_open:
 return True
 if time.monotonic() - self.circuit_opened_at > self.CIRCUIT_RESET_SEC:
 self.circuit_open = False
 self.failures = 0
 return True
 return False


@dataclass
class SkillEntry:
 file_path: str
 metadata: dict
 _module: Any = None
 health: SkillHealth = field(default_factory=SkillHealth)
 _loaded: bool = False

 @property
 def module(self) -> Any:
 if not self._loaded:
 self._load()
 return self._module

 def _load(self) -> None:
 spec = importlib.util.spec_from_file_location(
 self.metadata.get("id", os.path.splitext(os.path.basename(self.file_path))[0]),
 self.file_path,
 )
 if spec and spec.loader:
 module = importlib.util.module_from_spec(spec)
 sys.modules[self.metadata.get("id", os.path.splitext(os.path.basename(self.file_path))[0])] = module
 spec.loader.exec_module(module)
 self._module = module
 self._loaded = True


class LockFreeSkillRegistry:
 """Atomic registry pointer for high-concurrency lock-free skill retrieval."""

 def __init__(self) -> None:
 self._index: Dict[str, SkillEntry] = {}

 def swap_index(self, new_index: Dict[str, SkillEntry]) -> None:
 self._index = new_index

 def get_skill(self, skill_id: str) -> Optional[SkillEntry]:
 return self._index.get(skill_id)

 def list_skills(self) -> List[str]:
 return sorted(self._index.keys())

 def list_with_metadata(self) -> List[dict]:
 return [
 {"id": sid, "metadata": e.metadata, "health": e.health}
 for sid, e in self._index.items()
 ]


class IsolatedSkillExecutor:
 """Safely executes loaded skill modules in an isolated async boundary."""

 @staticmethod
 async def execute_skill(skill_module: Any, payload: dict, timeout: float = 3.0) -> dict:
 if not hasattr(skill_module, "execute"):
 raise AttributeError("Skill module missing required async 'execute(payload)' function.")

 try:
 if asyncio.iscoroutinefunction(skill_module.execute):
 res = await asyncio.wait_for(skill_module.execute(payload), timeout=timeout)
 else:
 loop = asyncio.get_running_loop()
 res = await asyncio.wait_for(
 loop.run_in_executor(None, skill_module.execute, payload),
 timeout=timeout,
 )

 if isinstance(res, dict):
 return res
 return {"status": "success", "result": res}

 except asyncio.TimeoutError:
 logger.error(f"Execution timed out after {timeout}s.")
 return {"status": "error", "reason": "TimeoutExceeded"}
 except asyncio.CancelledError:
 logger.warning("Skill execution cancelled.")
 return {"status": "error", "reason": "Cancelled"}
 except Exception as err:
 logger.error(f"Execution failure: {err}")
 return {"status": "error", "reason": str(err)}


class SkillDirectoryWatcher(FileSystemEventHandler if WATCHDOG_AVAILABLE else object):
 """Monitors directory changes with debouncing and triggers index rebuilds."""

 def __init__(self, reload_callback: Callable[[], None]) -> None:
 self.reload_callback = reload_callback

 def on_any_event(self, event) -> None:
 if WATCHDOG_AVAILABLE and event.is_directory:
 return
 src = getattr(event, "src_path", "")
 if not src.endswith(".py"):
 return
 now = time.monotonic()
 last = _watchdog_last_fire.get(src, 0.0)
 if now - last < _WATCHDOG_DEBOUNCE_SEC:
 return
 _watchdog_last_fire[src] = now
 path_parts = set(src.split(os.sep))
 if not path_parts.intersection(EXCLUDED_DIRECTORIES):
 self.reload_callback()


class MicroRoutedAdaptiveRouter:
 """Main routing and discovery engine for Hermes skills."""

 def __init__(self, skills_dir: str = "~/.hermes/skills") -> None:
 self.skills_dir = os.path.abspath(os.path.expanduser(skills_dir))
 self.registry = LockFreeSkillRegistry()
 self.executor = IsolatedSkillExecutor()
 self.observer: Optional[Any] = None
 self._added_syspaths: List[str] = []
 self._shutdown = False

 # Initial index construction
 self.rebuild_skill_index()

 # Graceful shutdown
 signal.signal(signal.SIGTERM, self._on_shutdown)
 signal.signal(signal.SIGINT, self._on_shutdown)

 # Initialize watchdog if environment permits
 if WATCHDOG_AVAILABLE and Observer:
 try:
 self.event_handler = SkillDirectoryWatcher(reload_callback=self.rebuild_skill_index)
 self.observer = Observer()
 self.observer.schedule(self.event_handler, str(self.skills_dir), recursive=True)
 self.observer.daemon = True
 self.observer.start()
 logger.info("Watchdog observer active for live hot-reloading.")
 except Exception as err:
 logger.warning(f"Could not start Watchdog observer: {err}")
 else:
 logger.warning("Watchdog package not installed. File hot-reloading disabled.")

 def _on_shutdown(self, signum: int, frame: Any) -> None:
 logger.info(f"Signal {signum} received, shutting down gracefully.")
 self._shutdown = True
 self.stop_watcher()

 def rebuild_skill_index(self) -> None:
 """Scans the skill directory while completely skipping venvs and non-skill files."""
 new_index: Dict[str, SkillEntry] = {}

 if not os.path.exists(self.skills_dir):
 logger.error(f"Skills directory does not exist: {self.skills_dir}")
 self.registry.swap_index(new_index)
 return

 # Clean stale sys.path entries from previous rebuilds
 for p in self._added_syspaths:
 if p in sys.path:
 sys.path.remove(p)
 self._added_syspaths.clear()

 # Expire old failed-import cache entries
 now = time.monotonic()
 expired = [m for m, t in _failed_imports.items() if now - t > _FAILED_IMPORT_TTL]
 for m in expired:
 del _failed_imports[m]

 for root, dirs, files in os.walk(self.skills_dir):
 dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES]

 if root not in sys.path:
 sys.path.insert(0, root)
 self._added_syspaths.append(root)

 for file in files:
 if not is_valid_skill_file(file):
 continue

 file_path = os.path.join(root, file)
 module_name = os.path.splitext(file)[0]

 # Respect failed-import backoff
 if module_name in _failed_imports:
 continue

 try:
 spec = importlib.util.spec_from_file_location(module_name, file_path)
 if spec is None or spec.loader is None:
 continue

 # Load once to extract metadata; actual module is lazy-loaded later
 metadata = _extract_metadata(file_path)
 if metadata is None:
 continue
 skill_id = metadata.get("id", module_name)

 new_index[skill_id] = SkillEntry(
 file_path=file_path,
 metadata=metadata,
 )
 logger.debug(f"Loaded skill: {skill_id} from {file_path}")

 except (ImportError, ModuleNotFoundError) as err:
 _failed_imports[module_name] = now
 logger.warning(f"Skipped {file_path}: {err}")
 except Exception as err:
 logger.error(f"Failed loading {file_path}: {err}")

 self.registry.swap_index(new_index)
 logger.info(f"Index rebuilt: {len(new_index)} skills")

 async def route_and_execute(self, query_or_id: str, payload: Optional[dict] = None) -> dict:
 """Routes natural language queries or direct skill IDs to execution."""
 start_time = time.perf_counter()

 if payload is None:
 payload = {"query": query_or_id}

 skill_entry = self.registry.get_skill(query_or_id)

 # Fuzzy-match fallback with priority ordering (LRU-cached)
 if skill_entry is None:
 skill_entry = _cached_fuzzy_match(query_or_id, self.registry._index)

 if skill_entry is None:
 elapsed_ms = (time.perf_counter() - start_time) * 1000.0
 return {"status": "error", "reason": f"Skill or intent matching '{query_or_id}' not found.", "latency_ms": elapsed_ms}

 # Circuit breaker check
 if not skill_entry.health.can_execute():
 elapsed_ms = (time.perf_counter() - start_time) * 1000.0
 return {"status": "error", "reason": f"Skill '{skill_entry.metadata.get('id')}' circuit open (3+ failures).", "latency_ms": elapsed_ms}

 metadata = skill_entry.metadata
 timeout = metadata.get("timeout_seconds", 3.0)

 result = await self.executor.execute_skill(skill_entry.module, payload, timeout=timeout)
 elapsed_ms = (time.perf_counter() - start_time) * 1000.0
 result["latency_ms"] = elapsed_ms

 # Update health
 if result.get("status") == "error":
 skill_entry.health.record_failure()
 else:
 skill_entry.health.record_success()

 return result

 def stop_watcher(self) -> None:
 if self.observer and self.observer.is_alive():
 self.observer.stop()
 self.observer.join(timeout=5)


def is_valid_skill_file(filename: str) -> bool:
 if not filename.endswith(".py"):
 return False
 if filename in EXCLUDED_FILES:
 return False
 if filename.startswith("test_") or filename.endswith("_test.py"):
 return False
 return True


def _extract_metadata(file_path: str) -> Optional[dict]:
 """Static metadata extraction via AST — no execution, no imports."""
 try:
 with open(file_path) as f:
 source = f.read()
 tree = ast.parse(source)
 for node in ast.iter_child_nodes(tree):
 if isinstance(node, ast.Assign):
 for target in node.targets:
 if isinstance(target, ast.Name) and target.id == "__skill_metadata__":
 if isinstance(node.value, ast.Dict):
 result: Dict[str, Any] = {}
 for k, v in zip(node.value.keys, node.value.values):
 if isinstance(k, ast.Constant):
 if isinstance(v, ast.Constant):
 result[k.value] = v.value
 elif isinstance(v, ast.List):
 result[k.value] = [
 elt.value for elt in v.elts if isinstance(elt, ast.Constant)
 ]
 return result
 return {}
 except Exception:
 return None


def _cached_fuzzy_match(query: str, index: Dict[str, SkillEntry]) -> Optional[SkillEntry]:
 """LRU-cached fuzzy match: query → best SkillEntry (or None)."""
 if query in _query_cache:
 sid = _query_cache[query]
 return index.get(sid) if sid else None

 candidates = [
 (s_id, e) for s_id, e in index.items()
 if s_id.lower() in query.lower() or query.lower() in s_id.lower()
 ]
 candidates.sort(key=lambda x: (-x[1].metadata.get("priority", 0), x[0]))
 result = candidates[0][1] if candidates else None

 # Populate cache (simple LRU eviction)
 if len(_query_cache) >= _QUERY_CACHE_MAX:
 _query_cache.pop(next(iter(_query_cache)))
 _query_cache[query] = result.metadata.get("id") if result else None
 return result


if __name__ == "__main__":
 router = MicroRoutedAdaptiveRouter()
 print(f"Active Skills Index: {router.registry.list_skills()}")