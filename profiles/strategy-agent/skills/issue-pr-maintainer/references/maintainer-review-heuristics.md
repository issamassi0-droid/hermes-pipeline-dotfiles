# Filling in project-specific review heuristics

The original single-project version of the Issue & PR Maintainer skill
hardcoded a fixed list of "high-signal areas" (e.g. "package X must never
import package Y", specific ports, a specific compatibility surface). That
list only made sense for one repository. This file replaces it with a
short procedure for deriving the equivalent list for *whatever* repository
the agent is currently working in — do this once per project and reuse the
result across runs.

## Where to look

1. **`CONTRIBUTING.md` / architecture docs** — most maintained projects
 document their layering rules, security-sensitive areas, and public
 contracts somewhere. Read it first.
2. **Existing PR review comments** (search closed PRs for recurring
 maintainer feedback) — the same objection showing up repeatedly is a
 heuristic the project already enforces informally.
3. **Module/package boundaries visible in the code** — directory
 structure, import graphs, and any lint rule that already restricts
 cross-module imports are direct evidence of an intended boundary.
4. **CI configuration** — job names and their trigger paths reveal what
 the maintainers consider a distinct, separately-validated surface
 (e.g. a job that only runs on changes under a specific path is telling
 you that path is treated as its own contract).
5. **Public API / schema files** — anything versioned, published, or
 consumed by an external client is a compatibility boundary even if no
 in-repo caller is visible.

## What to record

For each heuristic found, capture it in one line, in the same shape as
these DeerFlow-specific examples that originally lived in this file (kept
here only as illustrations of the *shape*, not as heuristics that apply to
other repos):

```text
- `<layer/module>` must not import `<other layer/module>`.
- `<component>` may depend on `<other component>`; the reverse must stay
 false / that direction must stay publishable and consumer-agnostic.
- `<surface>` (e.g. a specific API route family, a message/event schema,
 a UI behavior) is a contract surface — changes there need extra scrutiny.
- `<area>` (e.g. sandbox permissions, credential handling, remote
 execution) is security-sensitive — findings there need proof and
 remediation, not vague assertions.
- `<surface>` (default config/behavior, persistence schema, public
 API/event shape, a long-lived process's lifecycle) is
 compatibility-sensitive.
- User-facing or developer-facing docs should track behavior changes in
 `<area>`.
```

Once this list exists for a project, treat it the same way Section 2 of
`SKILL.md` treats the original DeerFlow-specific list: as background
context that shapes which findings get flagged and at what severity,
re-derived only when the project's architecture materially changes.

## Validation command discovery

Alongside the heuristics list, record which command actually validates
each surface (see the "Validation Guidance" table in `SKILL.md` Section
2) — pulled from the project's own `Makefile`/`package.json`/CI config,
not assumed. Keep both lists together; they're usually discovered in the
same pass through the project's docs and CI config.
