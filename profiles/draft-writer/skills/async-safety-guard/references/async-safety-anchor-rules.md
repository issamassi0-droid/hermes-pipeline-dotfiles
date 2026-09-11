# Async/blocking-IO guard rules — generic shape

This is the domain-agnostic shape the Async/Blocking-IO Guard section
(Section 1 of `SKILL.md`) instantiates. It's written so any single
sensitive-thread/event-loop domain (Python asyncio, Node's event loop, a Go
worker that must not block, a UI main thread) can reuse the flow without
re-deriving it. Don't add machinery for a second domain until one actually
appears (YAGNI).

## What a domain needs to supply

- A **static or dynamic detector** that can scan a diff (or the whole tree)
  and emit located candidates.
- A **gate** (test suite, lint rule, CI job) that fails when the bad
  pattern executes.
- A **test location** for guard tests (wherever the project's own
  regression-test conventions put this kind of test).
- **Good-test rules** for that gate (this file, generalized).
- A **teeth definition** — how to make the gate fire on purpose.

## A good guard test

- Calls the **real production entry point** — not a low-level helper,
  unless that helper *is* the entry point production actually executes.
- Does **not** bypass the sensitive surface with a test-only offload
  wrapper (e.g. a manual thread-pool dispatch in the test that the
  production code doesn't actually use).
- Uses **real local inputs** (filesystem, in-process state) when the bug
  shape matches — don't mock away the very thing being tested.
- Mocks **only** the external dependency boundary (a network service, a
  third-party API), never the offload/guard being verified.
- Drives the **specific branch** being protected (error path, cleanup
  path, a particular status code), not just the happy path.

## Teeth (the acceptance test)

A guard only counts if the gate actually fires when the code blocks:

1. Reintroduce the block (revert the offload, or run the pre-fix code).
2. Run the project's gate → the guard test **must fail** (RED).
3. Restore the fix → the guard test **must pass** (GREEN).

A green-on-happy-path test with no proven RED is fake coverage. Don't ship
it.

## The generic SOP (extraction seam)

1. **Scope (deterministic):** intersect the diff's added lines with the
   detector's findings → candidates this change introduced/touched. (Or,
   in triage mode, take the full finding list ordered by priority.)
2. **Judge (router):** per candidate — guard an existing fix / fix + guard
   / no-action / new detector rule (the gate can't see the primitive at
   all).
3. **Fix + re-scope (fixes only):** apply the fix, re-run the detector;
   the fixed candidate must vanish from the findings (match by a stable
   key, not line numbers). This is pattern-level feedback in seconds — it
   complements but never replaces step 5.
4. **Generate:** draft or extend a guard test per the good-test rules
   above, driving the specific branch.
5. **Verify teeth:** make the bad pattern happen → gate must fail;
   restore → gate must pass. A pattern that stays green while genuinely
   bad is the "new rule" signal, not a coverage success.
6. **Deliver:** commit the verified guard test; any gate-rule change ships
   in its own commit with the fails-to-fail evidence attached.

## The RULE route (rare; strict admission criteria)

Most detectors' built-in rules already cover the common blocking
primitives for their runtime. Two deliberate openings exist in this SOP:

1. **Coverage opening** (the normal case): the detector already sees the
   primitive — you only need a guard test so runtime detection executes
   the real business path and the gate prevents regression.
2. **Rule opening** (rare): you reintroduced a *real* block and the gate
   stayed GREEN — the detector has no rule for that primitive.

A new detector rule changes detection for the **entire** codebase's gate
run — global blast radius. Admission criteria for adding one:

- You have the **fails-to-fail guard test** as evidence: a good guard test
  (per the rules above) that drives a genuinely blocking path and stays
  green. No evidence, no rule.
- The primitive is a real blocking call (verified against its
  implementation or documentation), not a false positive of the static
  detector.
- The rule ships in its **own commit**, naming the primitive, the guard
  test that exposed the gap, and the suite-wide impact. Run the *entire*
  gate suite after adding it — a new rule can turn other previously-green
  tests red, and each such red is either a real latent bug (fix it) or
  rule overreach (narrow the rule).
- If you're not in a position to own that blast radius (e.g. an external
  contributor without merge authority over the gate config), escalate to
  a maintainer with the evidence instead of merging the rule yourself.

**Never add a runtime rule just because a path is untested** — that case
needs a guard test, not a rule.

## To add a second sensitive-thread domain

Supply a new fill doc (like this one, adapted) plus a detector for that
domain, and point the generic SOP above at both. Don't build the
abstraction speculatively before a second domain actually shows up.
