# Model Gateway — Dynamic Model Interaction

The Model Gateway selects AI models per task, caches results, tracks costs, and falls back automatically. Added in v1.2.0.

## Contract Files

| File | Purpose |
|---|---|
| `model-gateway.md` | The contract — selection weights, fallback chain, caching TTL |
| `model-registry.json` | User-configured models with costs, tiers, speed, best_for tasks |
| `model-gateway.sh` | Executable — select, cache-get/set, log, budget, status |

## Selection Algorithm

```
Score = 0.4*fit + 0.25*preference + 0.2*budget + 0.15*speed
```

Where:
- fit = 1.0 if task in model.best_for else 0.5
- preference = model-preferences.json[agent:task].acceptance_rate or 0.5
- budget = 1.0 if free else 0.7
- speed = 1.0 if fast else 0.7

Filter: enabled=true AND tier >= complexity_needed AND context_window >= needed

## Fallback Chain

```
User default → Alternative SLM → Human escalation
```

Configurable in model-registry.json settings.fallback_chain.

## Caching

- Key: hash(normalized_query + model_id + skill)
- TTL: 3600s (1 hour) for search, 86400s (24h) for factual
- Max: 1000 entries, LRU eviction
- Hit rate target: >30% for repeated tasks

## Context Window Profiles

| Profile | Tokens | Max Contracts | Label |
|---|---|---|---|
| small | 8,000 | 1 | 8K |
| medium | 32,000 | 3 | 32K |
| large | 128,000 | 6 | 128K |
| xlarge | 200,000 | 8 | 200K |
| max | 1,000,000+ | 9 | 1M+ |

## Commands

| Command | Purpose |
|---|---|
| `select <task> <complexity> <agent>` | Pick best model |
| `execute <model_id> <prompt>` | Call model with fallback |
| `cache-get <hash>` | Check cache |
| `cache-set <hash> <response>` | Store in cache |
| `log <model> <in> <out> <cost> <agent> <stage> <mission>` | Record usage |
| `budget` | Show cost summary |
| `status` | Gateway overview |

## Pitfalls

- **Cache must be bounded.** Unbounded cache serves stale data and costs memory. Always set TTL and max entries.
- **Selection weights are fixed.** Do not randomize or per-agent customize without logging why.
- **Fallback chain must always end in human.** A chain that ends in a model that may fail is a silent failure.
- **Free models preferred.** The system is designed for users with no budget. Cost=0 models score higher.