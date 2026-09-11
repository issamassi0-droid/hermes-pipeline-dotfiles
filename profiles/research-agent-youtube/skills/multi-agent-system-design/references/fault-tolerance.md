# Fault Tolerance in Multi-Agent Systems

## MAS-FIRE Fault Taxonomy (15 types)

### Intra-Agent Faults (7 types)

| Fault Type | Description | Severity | Detection |
|---|---|---|---|
| Factual hallucination | Agent generates factually incorrect information | High | Cross-reference with source |
| Referential hallucination | Agent references non-existent entities | High | Source verification |
| Logical error | Agent makes invalid logical inference | Medium | Logic checking |
| Procedural error | Agent skips or misorders steps | Medium | Trajectory analysis |
| Scope violation | Agent exceeds task boundaries | Low | Scope checking |
| Reasoning drift | Agent loses coherence over long context | Medium | Coherence monitoring |
| Overconfidence | Agent expresses certainty without evidence | Medium | Confidence calibration |

### Inter-Agent Faults (8 types)

| Fault Type | Description | Severity | Detection |
|---|---|---|---|
| Message corruption | Message content altered between agents | High | Checksum/validation |
| Role ambiguity | Agent confused about its role | Medium | Role verification |
| Blind trust | Agent accepts erroneous upstream info | High | Trust but verify |
| Context length violation | Message exceeds context window | Medium | Length checking |
| Message storm | Exponential message amplification | High | Rate limiting |
| Deadlock | Circular waiting between agents | High | Timeout + cycle detection |
| Tool format error | Agent calls tool with wrong format | Low | Schema validation |
| Tool selection error | Agent selects wrong tool | Medium | Tool matching |
| Parameter filling error | Agent fills parameters incorrectly | Low | Parameter validation |

## 4-Tier Fault Tolerance

| Tier | Description | Handles | Activation Target | Recovery Target |
|---|---|---|---|---|
| Mechanism | Architectural redundancy and retry | Tool format/selection/parameter errors | 85% | 100% |
| Rule | Hardcoded procedural logic | Message storms, deadlock, context violations | 100% | 100% |
| Prompt | Semantic robustness of instructions | Role ambiguity, blind trust | 100% | 79% |
| Reasoning | LLM semantic understanding | Hallucinations, logical errors, drift | 85% | 61% |

## MTTR-A / MTBF / NRR

- **MTTR-A** (Mean Time-to-Recovery for Agentic Systems): Average time to detect drift and restore coherent operation. Target: < 10s.
- **MTBF** (Mean Time Between Cognitive Faults): Average stable duration between drift events.
- **NRR** (Normalized Recovery Ratio): NRR = MTBF / (MTBF + MTTR-A). Target: > 0.8.

## Byzantine Fault Tolerance (CP-WBFT)

- LLM-based agents show stronger skepticism with erroneous message flows.
- Weighted consensus: assign higher weight to more credible agents.
- BFTI (Byzantine Fault Tolerance Improvement): percentage improvement from initial to final accuracy.
- Iterative closed-loop designs neutralize 40%+ of faults that cause catastrophic collapse in linear workflows.

## Key Findings from Research

- 75% of MAS failures are "silent gray errors" — no exception thrown, output looks valid, but content is factually wrong (MAESTRO).
- Linear architectures (MetaGPT) collapse under blind trust faults (0% robustness). Iterative closed-loop designs (Table-Critic) achieve 79-91% robustness (MAS-FIRE).
- Stronger foundation models do NOT uniformly improve robustness. Architectural topology matters as much as model capability.
- Rate limiting is the most damaging fault type — agents struggle with backoff and retry logic (ReliabilityBench).
