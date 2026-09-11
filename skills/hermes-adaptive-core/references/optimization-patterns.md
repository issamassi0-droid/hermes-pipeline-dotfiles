# Optimization Patterns — hermes-adaptive-core v3.7+

## LRU Query Cache
- `_query_cache` (dict, max 128 entries) caches query → skill_id lookups.
- Avoids repeated O(n) fuzzy scans for the same query string.
- Cache key is the raw query string; eviction is FIFO via `pop(next(iter(dict)))`.
- Invalidated automatically on `rebuild_skill_index()` (cache is process-scoped).

## Lazy Skill Loading
- `SkillEntry` stores `file_path` + `metadata`, not the loaded module.
- `module` property triggers `_load()` on first access via `importlib.util`.
- Cold start: modules are NOT executed during indexing — only AST metadata extraction.
- `_loaded` flag prevents double-loading; `_module` holds the cached module reference.

## AST Static Metadata Extraction
- `_extract_metadata(file_path)` uses `ast.parse()` to read `__skill_metadata__` without executing the module.
- Handles: `ast.Dict` with `ast.Constant` keys/values, `ast.List` of constants.
- Zero imports, zero side effects, zero missing-dependency failures during indexing.
- Falls back to `{}` on parse failure — skill is skipped, not fatal.

## Fuzzy-Match Cache Function
- `_cached_fuzzy_match(query, index)` wraps the fuzzy search with LRU caching.
- Sorts candidates by `(-priority, id)` for deterministic ordering.
- Cache miss triggers full scan; cache hit returns in O(1).

## Performance Targets
| Metric | Target |
|---|---|
| Cold start | <150ms (AST-only indexing) |
| Exact route | <0.01ms |
| Fuzzy route (cached) | <0.005ms |
| Concurrency | >100K req/s |
| Warm rebuild | <100ms |