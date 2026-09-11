---
name: issue-pr-maintainer
description: >
  Comment-only handling of code-hosting platform issues and pull requests —
  triage, post/draft comments, review diffs, compare competing PRs against an
  issue's acceptance criteria. For maintainers or trusted agents acting on
  their behalf. Includes posting gate, no-question policy, heuristics fill-in
  procedure, and validation guidance. Use when handling a bounded set of
  issues or PRs on GitHub/GitLab.
---

# Issue & PR Maintainer

Comment-only handling of code-hosting-platform issues and pull requests.
Resolve scope, inspect evidence, and prepare or post issue comments and PR
review comments. Keep the work comment-scoped — do not turn it into coding,
branch management, release work, or other maintainer operations unless
separately asked.

## Core Rule

This is a comment-plane skill. When the maintainer asks to process, handle,
comment on, or review a bounded set of issues or PRs, proceed without asking
follow-up questions. Treat that request as authorization for one public issue
comment per selected non-skipped issue and one PR review comment per selected
PR with high-confidence findings. If a PR has no high-confidence findings, do
not post a public comment; report that result to the maintainer only.

The maintainer's normal interaction: provide scope; receive posted
comment/review URLs, clean results, skipped items, failures, or drafts. Do
not offload technical analysis to the maintainer — make the best
evidence-backed recommendation in the comment itself: risk, impact, likely
fix, validation path.

Output only the run result or comment draft. Do not announce the skill name
or that no code was edited unless asked for process details.

Match the dominant language of the issue or PR unless told otherwise.

## Artifact Resolution

Use the code-hosting platform's own tooling (`gh`, `glab`, or REST API) to
resolve artifact type and scope. Do not ask the maintainer to clarify when
the API can determine the answer.

1. Determine the target repository from the conversation, the current git
   remote, or an explicit URL/flag — never assume a hardcoded default repo.
2. For URLs, route `/issues/<number>` to Issue Flow and `/pull/<number>` (or
   `/merge_requests/<number>` on GitLab) to PR Review Flow.
3. For typed numbers, use a typed lookup (fetch metadata, body, labels,
   author, comments, changed files, reviews, CI/status-check rollup).
4. Normalize multiple explicit references (`#123`, `# 123`, bare `123`) into
   a de-duplicated, order-preserving number list.
5. For untyped numbers, try PR lookup first; if it fails, try issue lookup.
6. For batches, use the platform's list/search endpoint for issues and PRs
   separately rather than a mixed feed.
7. Respect maintainer-provided count or time window. If broad and
   underspecified, choose a practical recent slice, state the slice used,
   prioritize newest and highest-risk items, and report any unprocessed
   remainder.
8. For "recent/latest" without a count, use a small default recent slice.
9. Use the platform's lower-level API when list/view calls lack required
   fields.
10. Use full-text/web search only as a fallback when the platform API can't
    express the filter.
11. When an issue has more than one candidate resolving PR, gather them all
    before reviewing: linked/development PRs, closing keywords found via
    timeline cross-reference, PRs that merely mention the issue.
12. If no artifact type, number, URL, count, time window, or searchable scope
    can be resolved, stop with a compact "scope unresolved" report.

Use concise repo-local references (`#123`, `PR #123`) in reports and
comments. Include full URLs only for posted comment/review links returned by
the platform, or when the maintainer supplied an explicit URL.

## Existing Coverage and Re-Runs

Existing comments suppress duplicate **posting**, not **analysis**. Always
analyze the artifact in full, then post only the net-new delta over what's
already covered.

1. Read existing maintainer/trusted-agent comments and reviews as prior
   coverage.
2. Analyze the artifact fully regardless of what already exists.
3. Keep only net-new, high-confidence items not already materially covered.
4. Non-empty delta: post one comment that explicitly builds on the prior
   coverage and states only the new items.
5. Empty delta: post nothing public; report "Already covered" to the
   maintainer with the existing comment/review URL.
6. Idempotency: treat your own earlier skill-authored comments as
   already-covered.

RFC-labelled issues are the one hard skip by default: no analysis, no post
unless the maintainer explicitly overrides.

## Issue Flow

Start every issue with a cheap precheck:

1. Fetch metadata, labels, author, body, existing comments.
2. If labelled/titled/bodied as RFC, classify `rfc-no-comment`, skip deep
   analysis, don't post publicly unless overridden.
3. Existing maintainer/trusted-agent comments are prior coverage, not an
   automatic skip — analyze fully, post only net-new delta.
4. Report already-covered or skipped issues to the maintainer only.

For non-skipped issues:

1. Read enough context to avoid guessing: body, comments, screenshots, logs,
   reproduction details, linked artifacts, relevant code/docs.
2. Classify the surface using whatever categories fit the project (derive
   from the project's actual module boundaries).
3. Classify actionability:
   - `ready-to-fix`: bounded, evidence sufficient, validation path clear.
   - `needs-more-evidence`: repro, logs, environment, screenshots missing.
   - `defer-or-close`: duplicate, stale, unsupported, unactionable, or out of
     scope.
   - `rfc-no-comment`: RFC issue; skip public comments by default.
4. Produce a public-safe comment from the analysis, not the labels:
   - One natural opener tied to the issue context. `Thanks @author.` when it
     reads naturally for a reporter-authored issue; omit for bots or
     maintainer-authored tracking issues.
   - The opener states something specific about the next step or boundary —
     not a generic assessment.
   - Smallest stable template:

```text
Thanks @author. <one specific sentence framing the fix, investigation, or missing evidence.>

Recommended solution:
- ...

Validation:
- ...
```

   - Add `Evidence:` only when citing concrete code/logs/repro helps.
   - Add `Risk:` only when architecture, security, public API, default
     behavior, or compatibility impact must be called out.
   - Add `Missing info:` only when the issue can't be diagnosed without more
     evidence.
   - Put relevant files/components inside `Evidence:`/`Recommended solution:`
     bullets rather than separate metadata fields.
5. Immediately before posting, refresh comments; fold any equivalent comment
   that appeared during analysis into prior coverage, post only the remaining
   delta.
6. Post one issue comment if posting is authorized; otherwise return the same
   text as `Reply draft`.

Never expose private reasoning, credentials, internal-only context, or
unsupported promises. Never say a fix was made unless a separate coding
workflow actually changed code.

## PR Review Flow

Start every PR with a cheap precheck:

1. Fetch metadata, changed file list, CI/status-check summary, existing
   reviews/comments/threads.
2. Existing maintainer/trusted-agent reviews are prior coverage, not an
   automatic skip — review fully, post only net-new delta.
3. Read the CI status as signal, not verdict. A failing required check is
   itself a reportable finding (build failure = P0; failing tests/lint =
   P1/P2 by impact). Green checks lower risk but never excuse reading the
   actual changed code.
4. Report already-covered or clean PRs to the maintainer only.

### Diff Base Rule

Before reviewing a local PR branch or local diff, fetch the base repository's
target branch and compare against a fresh remote-tracking ref — never a
possibly-stale local default branch.

- For fork checkouts, prefer the upstream remote's fetched base branch.
- For direct checkouts, use the base remote's fetched branch.
- Prefer the platform's own PR base metadata for the target branch.
- Refresh the comparison ref explicitly, then `BASE=$(git merge-base HEAD
  <base-remote>/<base-branch>)` and `git diff "$BASE"...HEAD`.
- Resolve the PR head explicitly for fork PRs whose branch isn't on the base
  repo.
- Re-check the head SHA immediately before posting; if it moved during
  analysis, re-review the new diff or abort.
- For uncommitted local changes, review committed branch changes against the
  fresh base first, then include working-tree changes separately.
- If the base remote/branch can't be established, use the platform's own
  files/diff API as the source of truth.

Before posting a PR review comment:

1. Review only the current diff against the fresh base and changed files.
   Don't comment on unrelated pre-existing code unless the diff makes it newly
   risky.
2. Don't report low-confidence guesses — omit the finding if evidence is
   insufficient.
3. Prioritize correctness, safety, maintainability, production risk,
   compatibility, and missing critical tests over style.
4. Report concrete architecture, security, public API, default-behavior, and
   compatibility problems the diff causes or exposes.
5. Check changed behavior, edge cases, error paths, state mutation,
   transactions/locks, cache invalidation, cleanup, security boundaries,
   missing tests, performance/reliability, API compatibility.
6. Immediately before posting, refresh reviews/comments and fold any
   equivalent review that appeared during analysis into prior coverage; post
   only the remaining delta.
7. Apply the Posting Gate. If it yields public findings, post one PR review
   comment in the PR's language. Otherwise post nothing public and report the
   result plus any sub-threshold items as `Maintainer notes`.

For public reviews with findings, open with one short line matching the
finding count — singular for exactly one finding, plural for more. Omit the
mention for bots or where it adds noise.

For each finding:

```text
[P0/P1/P2] Title

- Location: file and line/range
- Problem: what can go wrong
- Evidence: why the diff causes it
- Suggested fix: concrete minimal fix
- Test: what test should cover it
```

Severity guide:

- `P0`: causes outage, data loss, security breach, or build failure.
- `P1`: likely production bug, serious regression, broken compatibility, or
  high-risk security/architecture issue.
- `P2`: correctness, maintainability, or test concern with lower risk.

### Posting Gate

Posting depends on BOTH confidence (is it real?) and severity (how bad if
real) — independent axes.

- Post publicly only items that are high-confidence AND at least P2.
- For a public P2, additionally require the diff itself introduces or
  worsens the issue. Don't raise a public P2 for pre-existing behavior the
  diff only touches, or for a net improvement over the prior state.
- A high-confidence P0/P1 is always worth posting. A low-confidence P1 is not
  — omit it or route it to `Maintainer notes` as a hypothesis.
- Sub-threshold but real observations go to `Maintainer notes`, never a public
  comment.

No compliments, summaries, or general advice. For sensitive security issues,
describe impact and remediation without exploit instructions.

## Batch Handling

When scope has multiple artifacts, cluster before reviewing, synthesize after.

Cluster by relatedness, not type. Group artifacts sharing files, interfaces,
or the same issue/feature into one cluster; same-type artifacts touching
disjoint files are independent.

- Related cluster: review in ONE shared context so cross-artifact reasoning is
  possible. If it doesn't fit one context, fan out per sub-group and reconcile
  in a synthesis pass.
- Independent clusters: may run in parallel; offloading a large/independent
  batch to one sub-task per cluster keeps the main context clean.

After per-artifact review, run one synthesis pass and report it to the
maintainer: overlapping files and merge-order/conflict surface, duplicate or
competing solutions, composition risk.

## Competing PR Comparison

When several PRs target the same issue, compare rather than review in
isolation.

1. Pull the issue's acceptance criteria — that's the rubric anchor.
2. Score each PR on: does it resolve the issue's ask; correctness and
   edge/error-path coverage; test quality; blast radius and compatibility;
   maintainability.
3. Report a maintainer-facing comparison — strongest PR and why, what each is
   missing.
4. Keep the public surface constructive and per-PR: post each PR's own
   gate-passing findings normally. Never publicly rank PRs against each other;
   winner selection stays in the maintainer report.

## No-Question Policy

Don't ask the maintainer routine clarification questions — the point is to
turn scope into comments through a fixed workflow.

Stop without asking only when:

- no issue/PR scope can be resolved through URLs, numbers, list/view/API
  calls, or search fallback;
- authentication, repository access, or comment posting fails;
- the requested action is outside comment-only scope;
- posting would require private credentials, private security details, or
  non-public context.

Return a compact failure report with the attempted path and the smallest
next action.

## Review Heuristics (fill in per project)

Before using this skill on a new repository, spend one pass identifying its
own high-signal areas — the equivalent of "layer X must not import layer Y",
"this surface is a public/compatibility contract", "this directory is
security-sensitive". Good sources: `CONTRIBUTING.md`, architecture docs,
existing PR review comments, and the module boundaries visible in the
codebase. Record them once (e.g. in
`references/maintainer-review-heuristics.md`) and reuse them across runs.

## Validation Guidance

Discover the validation command per surface from the project's own tooling
(`Makefile`/`package.json`/`tox.ini`/CI config) rather than assuming one.

| Surface | What to look for |
| --- | --- |
| Backend/API/service code | the project's lint + unit-test target |
| Concurrency-sensitive code | the project's async-safety/blocking-IO gate |
| A documented internal boundary | a boundary/lint test if the project has one |
| Frontend/UI | the project's format/lint/typecheck/build/test chain |
| Cross-service or API contract changes | a replay/contract test if the project has one |
| User-facing workflow changes | an E2E test suite if present |
| Deploy/infra changes | a smoke test |
| Docs-only | a targeted read-through; no command needed |

## Output

For Issue Flow:

```text
Run result:
Posted:
Skipped:
Already covered:
Failed:
Maintainer notes:
Per issue:
  Issue:
  Surface:
  Actionability:
  Risk:
  Comment:
  Validation:
  Comment status:
```

For PR Review Flow:

```text
Run result:
Reviewed:
Skipped:
Clean:
Already covered:
Failed:
Maintainer notes:
Per PR:
  PR:
  Public review:
  Findings:
  Review status:
```

For analysis-only requests, replace `Posted`/`Reviewed` with `Drafted` and
include the comment/review text without posting.

For batches, prefer a compact maintainer-facing table after the headline
counts:

```text
| Artifact | Status | Public action | Notes |
| --- | --- | --- | --- |
| #123 | posted | comment URL | short reason |
| PR #456 | reviewed | review URL | P1: finding title |
| PR #789 | clean | none | No high-confidence review findings. |
| #321 | already covered | none | existing maintainer comment |
```

For multi-artifact batches, follow the table with a `Batch synthesis` block
(overlapping files, merge-order/conflict surface, duplicate or competing
solutions, composition risk) and, when issues had competing PRs, a
`Competing PR comparison` block. Both are maintainer-only.

Omit empty categories, no-op fields, routine command output, and raw logs.
Report meaningful changes, evidence, and options.

## Bundled files

```
issue-pr-maintainer/
├── SKILL.md
└── references/
    └── maintainer-review-heuristics.md   ← how to fill in project-specific review heuristics
```
