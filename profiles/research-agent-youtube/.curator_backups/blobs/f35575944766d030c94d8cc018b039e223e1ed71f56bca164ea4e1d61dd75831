# Self-Learning and Evolution in Multi-Agent Systems

## Learning Extraction

From each completed mission, extract:

| Category | What to Look For |
|---|---|
| Quality issues | What problems occurred? |
| Tool usage | Which tools worked/failed? |
| Routing decisions | Which models performed well? |
| Process observations | What improvements were identified? |

## Pattern Identification

Aggregate learnings across missions to find recurring patterns:
- Quality issue types with frequency counts
- Tool success rates
- Routing success rates by model
- Process improvement themes

## Skill Generation

From patterns, generate reusable skills:
- **Quality skills**: Check for and prevent specific issue types
- **Tool skills**: Optimized usage patterns for specific tools
- **Routing skills**: Model selection patterns for task types

Trigger threshold: Pattern must appear 3+ times before skill generation.

## Evolution Proposals

Feed learnings into the evolution loop:

| Pattern | Proposal |
|---|---|
| Recurring quality issue | Add explicit check to quality charter |
| Low model success rate (<60%) | Deprioritize model in registry |
| High model success rate (>90%) | Prioritize model for similar tasks |
| Tool failure pattern | Update tool usage guidelines |

## Evolution Classes

| Class | Risk | Approval |
|---|---|---|
| 1 | Low (additive changes) | Auto-apply after 7 days + regression test |
| 2 | Medium (structural changes) | Architect sign-off required |
| 3 | High (scoring logic changes) | Explicit user approval required |

## Regression Testing

Before auto-applying Class 1 amendments:
1. Run against fixed regression set (last 20 missions)
2. Compare quality metrics before vs after
3. If any metric regresses >10%, downgrade to Class 2

## Continuous Improvement Loop

```
Mission Complete → Extract Learnings → Identify Patterns
      ↑                                        ↓
   Re-deploy ← Apply Amendments ← Generate Proposals
```

## Key Insight from GEPA (ICLR 2026)

Self-improvement comes from:
1. Rich feedback signals (not just pass/fail)
2. Semantic understanding of errors (not just error codes)
3. Candidate diversity (not just one retry strategy)
4. Efficient selection (not just brute force)

## Memory vs Skill

- **Memory**: Who the user is, current state, conventions
- **Skill**: How to do this class of task for this user

Self-learning feeds into skills, not just memory. Each improvement should be actionable in future sessions.
