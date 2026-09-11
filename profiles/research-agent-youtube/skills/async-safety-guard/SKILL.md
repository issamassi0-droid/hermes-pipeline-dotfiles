---
name: async-safety-guard
description: >
 Async/blocking-IO safety guarding for any async runtime (asyncio, Node's
 event loop, Go goroutines, etc.). Scan for blocking operations on a hot
 path, fix or guard them, and prove the guard with a fails-to-fail test.
 Use when a change touches code on a shared event loop / worker thread that
 may perform a blocking operation, or when adding a regression test that
 proves a fix actually guards against re-blocking.
---

# Async/Blocking-IO Guard

Ship async-path changes together with a regression test that proves the
runtime's blocking-call detector (if the project has one) or a purpose-built
check actually sees the new code. A dynamic/runtime detector only catches a
blocking call on a path some test executes — this skill closes that gap.

This is a generic *shape*; it does not assume Python/asyncio. Any runtime
with a single-threaded event loop, a fixed-size worker pool, or an equivalent
"must not block on this thread" constraint fits.

## Domain ingredients (identify before starting)

1. **Static or dynamic detector** — something that can scan a diff (or the
 whole tree) and emit located candidates. If the project already has one
 (a linter rule, a runtime gate like Python's Blockbuster, an ESLint rule
 against sync fs calls, `go vet` custom analyzer), use it. If not,
 `grep`/`ast-grep` for the blocking primitives of that runtime is an
 acceptable substitute — state that you're using a substitute.
2. **A gate that fails when the bad pattern executes** — a test suite, lint
 step, or CI job. Find its invocation command from the project's own
 tooling (`Makefile`, `package.json` scripts, `tox.ini`, CI config).
3. **A test location for guard tests** — wherever the project keeps
 regression tests for this concern.
4. **Good-test rules for that gate** — see `references/async-safety-anchor-rules.md`.
5. **A teeth definition** — how to make the gate fire on purpose, to prove
 it isn't fake coverage.

## When to use

- A change touches code that runs on a shared event loop / worker thread and
 may perform a blocking operation there (Mode A — your own diff).
- A maintenance triage round over the existing codebase (Mode B).

## SOP (router)

### Step 0 — Scope (deterministic)

**Mode A — your own diff** (default, pre-PR).

1. Identify the diff base (`git merge-base HEAD <base>`), and commit your
 work first — an uncommitted diff won't be selected by most detectors.
2. Run the project's blocking-IO/async-safety detector against
 `<base>...HEAD` if one exists; otherwise scan the changed files for the
 runtime's known blocking primitives.
3. The candidate set is: findings on lines the diff added, **plus** findings
 that are new versus the merge base (this catches a new async caller
 exposing an old sync helper whose blocking line isn't itself in the diff).
4. If the list is empty: no blocking-IO surface *that the detector can see in
 the changed files*. Reachability across file boundaries is usually a blind
 spot — if the diff adds an async call into a helper defined in another
 file, check that helper manually before stopping.

**Mode B — full-repo triage round.**

1. Run the project's full-repo detector target (discover the exact command
 from the project's own tooling).
2. Work HIGH-priority findings first; do not start MEDIUM until every HIGH
 is dispositioned (fixed, guarded, or recorded NO-ACTION).

**Batching policy (PR sizing).** One fix unit per PR while any HIGH remains —
usually a single HIGH, but two HIGHs resolved by the same one-place fix
belong together. Once no HIGH remains, MEDIUM/LOW may be batched (roughly
five per round, grouped by module or disposition). A new detector rule never
batches with anything else — it ships alone.

### Step 1 — Judge each candidate (router)

- **Already offloaded** → **GUARD**: add/extend a regression test that locks
 the offload.
- **Still on the sensitive thread, not offloaded** → **FIX+GUARD**: offload
 the production code first, then add the guarding test.
- **Not actually exposed / acceptable** → **NO-ACTION**: record one line of
 why.
- **Cross-file caveat**: most static detectors only trace same-file
 reachability. If the candidate is a sync helper, check for async callers in
 other files before deciding NO-ACTION.

### Step 2 — Apply the fix, then re-scan (FIX+GUARD only)

Offload the blocking call in production code, then re-run the Step 0 scan
and confirm the candidate is gone. Match findings by a stable key —
**(path, function, symbol)**, never by line number.

- The finding must actually disappear. If it still shows, the pattern wasn't
 removed — go back before touching any test.
- GUARD / NO-ACTION routes skip this step: a residual finding there is
 *expected*.

### Step 3 — Check for an existing guard test

Look for a test that already drives the real production entry point through
this candidate's branch.

- Already covers this branch → go to Step 5 (re-verify teeth).
- Covers the entry point but not this branch → extend that test.
- None exists → create one, following the project's existing test conventions
 (or `templates/anchor.template.py` as a Python/asyncio starting point).

### Step 4 — Generate / extend the guard test

Follow `references/async-safety-anchor-rules.md`. Drive the *specific* branch
being protected, not just the happy path. Never bypass the sensitive-thread
surface with a test-only wrapper.

### Step 5 — Verify teeth (mandatory)

1. Reintroduce the block (GUARD: temporarily revert the offload; FIX+GUARD:
 run against the pre-fix code).
2. Run the project's gate → it **must fail (RED)**.
3. Restore the fix → it **must pass (GREEN)**.

A real block that stays GREEN means the detector has no rule for that
primitive — that's the rare **RULE** route: see
`references/async-safety-anchor-rules.md` for the admission criteria before
adding a new detector rule (it has repo-wide blast radius).

### Step 6 — Deliver

Commit the guard test(s) with the change; the project's gate passes GREEN.
In the PR/commit message, note: candidates found, each disposition, the
re-scan result, and the teeth evidence (red→green). Include the reason for
any NO-ACTION. A new detector rule, if any, goes in its own commit with the
Step 5 evidence.

## Bundled files

```
async-safety-guard/
├── SKILL.md
├── references/
│ └── async-safety-anchor-rules.md ← generic teeth/anchor rules
└── templates/
 └── anchor.template.py ← illustrative Python/asyncio guard-test skeleton
```
