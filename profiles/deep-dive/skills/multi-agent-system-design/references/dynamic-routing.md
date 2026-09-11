# Dynamic Routing for Multi-Agent Systems

## Circuit Breaker Pattern

Prevents cascading failures when a model or tool is failing.

| State | Behavior |
|---|---|
| CLOSED | Normal operation, requests pass through |
| OPEN | All requests fail fast, no retries |
| HALF_OPEN | One trial request to test recovery |

Transition rules:
- CLOSED → OPEN: after N consecutive failures (default: 3)
- OPEN → HALF_OPEN: after cooldown period (default: 60s)
- HALF_OPEN → CLOSED: on success
- HALF_OPEN → OPEN: on failure

## Retry with Exponential Backoff

| Attempt | Delay |
|---|---|
| 1 | 1s |
| 2 | 2s |
| 3 | 4s |
| 4 | 8s |
| 5 | 16s |

Maximum retries: 5. After exhausting retries, escalate to next model.

## Cascade Routing (Sedai Pattern)

Start with cheap/fast model, escalate only when needed.

```
1. Try flash model (cheap, fast)
   → success: done
   → failure: escalate
2. Try mid-tier model
   → success: done
   → failure: escalate
3. Try premium model
   → success: done
   → failure: human escalation
```

## Dynamic Model Selection

Weighted scoring (40% task fit, 25% user preference, 20% cost, 15% speed):
- **Task fit**: Does the model match task complexity?
- **User preference**: Has the user preferred this model?
- **Cost**: Token cost per request
- **Speed**: Response latency

## Semantic Checkpointing

Preserve execution history to enable informed re-computation:
- Save state at each pipeline stage
- On failure, recover from last valid state
- Include error diagnostics in checkpoint
- Never naive retry — always informed recovery

## 4-Tier Watchdog

| Tier | Monitors | Action |
|---|---|---|
| 1 | Individual agent health | Alert + retry |
| 2 | Inter-agent communication | Reroute + checkpoint |
| 3 | Pipeline stage health | Escalate + recovery |
| 4 | System-level health | Degraded mode + alert |

## AI Triage

For unclear cases, use LLM to diagnose:
- Is this a transient error? → Retry
- Is this a model limitation? → Escalate
- Is this a data issue? → Reprocess
- Is this a configuration issue? → Alert + halt
