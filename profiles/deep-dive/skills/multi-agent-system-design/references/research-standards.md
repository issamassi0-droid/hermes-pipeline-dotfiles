# Research Standards for Multi-Agent Systems

## Overview

Key research frameworks for evaluating multi-agent AI systems (2025-2026).

## MAS-FIRE (Fault Injection and Reliability Evaluation)

**Source**: arXiv:2602.19843

Systematic framework for fault injection and reliability evaluation of LLM-based MAS.

### 15 Fault Types
- **Intra-agent (7)**: Factual hallucination, referential hallucination, logical error, procedural error, scope violation, reasoning drift, overconfidence
- **Inter-agent (8)**: Message corruption, role ambiguity, blind trust, context length violation, message storm, deadlock, tool format error, tool selection error, parameter filling error

### 4-Tier Fault Tolerance
| Tier | Description | Activation Target | Recovery Target |
|------|-------------|-------------------|-----------------|
| Mechanism | Architectural redundancy and retry | 85% | 100% |
| Rule | Hardcoded procedural logic | 100% | 100% |
| Prompt | Semantic robustness of instructions | 100% | 79% |
| Reasoning | LLM semantic understanding | 85% | 61% |

### Key Finding
Iterative closed-loop designs neutralize 40%+ of faults that cause catastrophic collapse in linear workflows.

## MTTR-A (Mean Time-to-Recovery for Agentic Systems)

**Source**: arXiv:2511.20663

Runtime reliability metric measuring cognitive recovery latency.

- **MTTR-A**: Average time to detect drift and restore coherent operation. Target: < 10s.
- **MTBF**: Mean Time Between Cognitive Faults. Average stable duration between drift events.
- **NRR**: Normalized Recovery Ratio = MTBF / (MTBF + MTTR-A). Target: > 0.8.

## ReliabilityBench

**Source**: arXiv:2511.20663

3D reliability surface R(k, ε, λ):
- **k**: Consistency under repeated execution
- **ε**: Robustness to semantic perturbation
- **λ**: Fault tolerance under controlled failures

### Key Findings
- Perturbations alone reduce success from 96.9% to 88.1% (8.8% decline)
- Rate limiting is the most damaging fault type
- ReAct is more robust than Reflexion under combined stress
- Gemini 2.0 Flash achieves comparable reliability to GPT-4o at 1/82nd the cost

## MAESTRO (Multi-Agent Evaluation Suite)

**Source**: arXiv:2601.00481

Standardized evaluation suite for testing, reliability, and observability of LLM-based MAS.

### Key Finding
75% of MAS failures are "silent gray errors" — no exception thrown, output looks valid, but content is factually wrong.

## COCO (Cognitive Operating System with Continuous Oversight)

**Source**: arXiv:2508.13815

Framework for asynchronous self-monitoring and adaptive error correction.

### Key Components
1. **Contextual Rollback Mechanism**: Stateful restart preserving execution history
2. **Bidirectional Reflection Protocol**: Mutual validation between monitoring and execution
3. **Heterogeneous Cross-Validation**: Ensemble disagreement to detect systematic biases

### Result
6.5% average performance improvement, achieving 95.1% of SOTA performance with 30x smaller model.

## CP-WBFT (Confidence Probe-based Weighted Byzantine Fault Tolerance)

**Source**: arXiv:2511.10400

Byzantine fault tolerance mechanism for LLM-based agents.

### Key Finding
LLM-based agents show stronger skepticism with erroneous message flows, enabling weighted consensus that achieves 85.7% fault tolerance even with 6/7 agents being Byzantine.

## Aegis (Automated Error Generation and Attribution)

**Source**: arXiv:2509.14295

Framework for automated error generation and attribution in multi-agent systems.

### Key Contribution
9,533 trajectories with annotated faulty agents and error modes, enabling supervised fine-tuning, reinforcement learning, and contrastive learning for error attribution.