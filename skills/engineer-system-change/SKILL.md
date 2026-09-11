---
name: engineer-system-change
description: >
  First-principles evaluation of non-trivial system changes (RFCs, new
  APIs/fields/events, refactors, migrations, dependency bumps) before writing
  code. Use when assessing whether a proposed change should exist, choosing the
  smallest sufficient solution, and mapping consequences proportionally. Not
  for mechanical edits or dedicated diff review.
---

# Engineer System Change

Evaluate and carry out non-trivial software-system changes from first
principles. Use when assessing RFCs, issues, designs, features, refactors,
migrations, dependency changes, or proposed fields, events, APIs, modules,
and services whose need, consumers, system fit, validation, or rollback
require scrutiny.

Treat every proposed change as a hypothesis about a real system, not as an
implementation checklist. Establish whether the change should exist before
designing or building it, then keep the solution and process proportional to
the risk.

## Preserve the Task Boundary

- If asked only to assess, review, or plan, make no project or
  external-state changes.
- If explicitly asked to implement, including after an assessment, pass the
  decision gates before editing and verify the result afterward.
- Treat implementation permission as separate from permission to commit,
  push, deploy, publish, or update issues and pull requests.
- If repository truth matters, inspect the current target revision and
  relevant discussion. Don't rely on a stale checkout, an RFC alone, or
  remembered architecture.
- Separate verified facts, inferences, and unknowns. Don't turn missing
  evidence into a confident conclusion.

## Apply the Decision Gates

### 1. Ground the Problem

- Trace the current user workflow, failure, or code path before proposing a
  solution.
- State the undesirable observable behavior and the invariant or outcome that
  should replace it.
- Identify who is affected and which concrete decision or action changes.
- Check whether the existing system, configuration, documentation, or
  operating procedure already solves the problem.
- Enumerate adjacent product paths and workarounds, not only the proposed
  target surface. Explain precisely which accepted outcome each alternative
  fails; don't claim "the only option" from one missing UI control or code
  path.
- Treat an absent field, interface, abstraction, or standard as an
  observation, not proof of a requirement.

Return `STOP` only when evidence affirmatively shows no change is needed or
the affected workflow already achieves the outcome. Return `NEEDS_EVIDENCE`
when an unverified fact prevents the decision.

### 2. Name Semantic Consumers

For every proposed durable field, event, API, table, store, module, service,
or workflow, establish:

| Question | Required answer |
| --- | --- |
| Producer or lifecycle owner | What creates, updates, or owns it? |
| Committed consumer | Which named caller, component, operator, or user reads or acts on it now or as part of this same accepted slice? |
| Semantic use | What behavior, decision, or externally visible result changes after consumption? |
| Reachable path | Where does production reach consumption in the current system or proposed slice? |
| Absence test | Which verified scenario or accepted outcome fails if the addition is removed? |

Accept a proposed consumer only when it's tied to a verified current need and
committed integration in the same change. Don't accept a roadmap, possible
future evaluator, generic read/debug API, storage alone, or "future
flexibility" as a semantic consumer. If an addition has no such consumer,
remove or defer it.

Treat a public or externally-consumed contract as a compatibility boundary
even when no in-repository caller is visible — absence of a discoverable
caller is uncertainty, not proof no consumer exists.

### 3. Choose the Smallest Sufficient Change

Consider solutions in this order, stop at the first that fully satisfies the
verified outcome and invariants without shifting disproportionate recurring
cost, coupling, or risk downstream:

1. No product or code change
2. Documentation, configuration, or operating procedure
3. Reuse an existing capability
4. Make a local behavior fix
5. Extend an existing abstraction
6. Introduce a new abstraction
7. Introduce a new subsystem or migration path

- Minimize concepts, states, interfaces, irreversible decisions, and
  maintenance surface — not literal line count.
- Require a second current consumer, a demonstrated variation, or a hard
  boundary before generalizing a local solution.
- Prefer independently reversible slices over a comprehensive architecture
  rollout.
- Distinguish a real problem from an oversized solution. A valid verdict:
  "The problem is real; reduce the proposal to this smaller change."
- Apply these gates recursively to your own recommendation — don't propose a
  new field, contract, abstraction, migration, or validation system without
  naming its consumer, checking existing mechanisms, and showing why a smaller
  change is insufficient.

### 4. Map Consequences and Verification Proportionally

Inspect only relevant dimensions, but don't omit one merely because the
proposal omits it: callers/downstream consumers; API, data, event, and UI
contracts; authorization, ownership, privacy, and trust boundaries;
persistence, migrations, replay, and side effects; concurrency, ordering,
retries, idempotency, and failure recovery; compatibility, dependencies,
performance, deployment, and operations; observability and rollback.

For state replay or retry features, explicitly distinguish restored
application state from external side effects that can't be undone. Label
material risk claims `VERIFIED`, `INFERENCE`, or `UNKNOWN`. Use an inference
to request a focused check, not to require new architecture as though the
claim were already proven. Evidence labels classify individual claims;
verdicts classify the overall decision. An `UNKNOWN` requires `NEEDS_EVIDENCE`
only when the unknown blocks a material decision.

Before implementation, require observed evidence for the current-system
claims that justify the decision and a proportional, executable verification
plan. Proposed checks are a verification plan, not observed evidence.

### 5. Implement Only the Justified Slice

- Reproduce the baseline first — encode it as a failing behavioral test when
  executable; otherwise state why and record a reproducible check.
- Change only the paths required by the accepted outcome and consumers.
- Reuse existing execution paths and contracts when they preserve the required
  semantics.
- Avoid speculative compatibility layers, selectors, shadow systems, canaries,
  or dual stacks unless an irreversible or high-risk transition requires them.
- Update repository guidance only when architecture, commands, or durable
  conventions actually change.

### 6. Prove the Result

- Map each important result claim to observed evidence: tests, contract
  checks, static analysis, runtime traces, benchmarks, or a reproducible
  manual check.
- Don't use the agent's own summary as proof.
- Verify negative boundaries and failure behavior, not only the happy path.
- State what remains unverified and how that uncertainty affects the verdict.
- Use focused regression checks for local reversible changes.
- Add targeted integration and adversarial checks for contract, persistence,
  security, concurrency, replay, or cross-component changes.
- Require a production-like rehearsal plus executable containment or rollback
  for irreversible changes or materially high-risk external side effects.

## Use Explicit Verdicts

- `STOP`: evidence affirmatively shows no current change is needed, or existing
  capability already achieves the accepted outcome.
- `REDUCE`: the problem is real, but the proposed scope or abstraction exceeds
  the evidence.
- `REVISE`: the problem and approximate scope are justified, but a
  correctness, contract, or failure-semantics defect must change first.
- `PROCEED`: problem, consumers, minimum solution, consequences, and a
  proportional verification plan are sufficiently established.
- `NEEDS_EVIDENCE`: a decision would be guesswork until a specific fact, code
  path, incident, or consumer is verified.

Don't force a binary approve/reject judgment when evidence is incomplete.
Choose the verdict from the condition blocking the earliest gate, not the gate
number: affirmative evidence no change is needed maps to `STOP`; a
decision-blocking unknown maps to `NEEDS_EVIDENCE`; a real problem with
unsupported scope or no committed consumer maps to `REDUCE`; a confirmed
correctness/contract/failure-semantics defect maps to `REVISE`. Use `PROCEED`
only when no gate is blocked. When more than one condition applies, give one
primary verdict and list the other required changes without inventing a
compound status. A verdict records the decision gate and never expands
authorization — after authorized implementation, separately report the
implemented slice, observed verification, and remaining uncertainty.

## Keep the Output Proportional

For a simple change, report only: problem and desired behavior; named semantic
consumer; smallest sufficient change; observed evidence and, before
implementation, the verification plan; verdict.

For a cross-boundary change or RFC, add: verified current-system facts;
existing alternatives and why they don't meet the accepted outcome; consumer
ledger for proposed additions; affected contracts and side effects; rejected
or deferred scope with reasons; failure, observation, and rollback strategy.

Don't create ceremonial documents or exhaustive matrices when a short
evidence-backed answer is sufficient. The workflow itself must not become
overengineering.
