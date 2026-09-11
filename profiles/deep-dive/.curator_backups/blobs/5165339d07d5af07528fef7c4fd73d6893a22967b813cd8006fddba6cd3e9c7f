# Quality Gates for Multi-Agent Systems

## Trajectory-Level Evaluation

Evaluate the full behavioral trace, not just the final output.

| Dimension | What to Measure |
|---|---|
| Tool selection | Was the correct tool chosen? |
| Argument validity | Were the arguments valid? |
| Recovery | Did the agent recover from mistakes? |
| Efficiency | How quickly did it converge? |

## 5-Type Hallucination Taxonomy

| Type | Description |
|---|---|
| Factual | Factually incorrect information |
| Referential | Non-existent entities or sources |
| Logical | Invalid logical inference |
| Procedural | Skipped or misordered steps |
| Scope | Task boundary violation |

## Silent Gray Error Detection

75% of multi-agent failures throw no exception. Detect:
- Empty predictions: output looks valid but contains no actual answer
- Plausible but wrong: sounds reasonable but may be incorrect
- Non-terminating patterns: suggests infinite loop
- Contradictions: self-conflicting statements

## Quality Metrics (3 Axes)

| Metric | Definition |
|---|---|
| factual_error_rate | % of claims failing independent verification |
| source_verification_rate | % of claims tagged [V] or [M] vs [U]/[H]/[X] |
| human_override_rate | % of missions where human gate rejected output |

## Evidence Grading

| Grade | Meaning |
|---|---|
| [V] | Verified against source |
| [M] | Modeled/inferred from data |
| [U] | Unverified |
| [H] | Hallucination flagged |
| [X] | Untranscribable/unverifiable |

## Self-Verification Loops

After each agent output:
1. Re-read the original task
2. Check for contradictions with prior outputs
3. Verify evidence grades on claims
4. Run consistency checks
5. If issues found, re-do the step

## Semantic Failure Detection

Output format looks fine, no errors thrown, but content is incorrect. Detection methods:
- Cross-reference with source material
- Independent verification by second agent
- Confidence calibration (hedging language detection)
- Schema validation + content validation
