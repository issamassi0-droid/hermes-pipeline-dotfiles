"""Template: an async-safety guard test.

This is one concrete, illustrative instantiation (Python + asyncio +
pytest) of the generic shape described in
`references/async-safety-anchor-rules.md`. If the project you're working
in uses a different runtime (Node.js, Go, etc.), port the same *shape* —
call the real production entry point, mock only the external boundary,
drive the specific branch, prove RED then GREEN — using that runtime's own
test framework instead of copying this file verbatim.

Copy into wherever the project keeps its own regression/guard tests
(commonly a directory like `tests/blocking_io/`, `tests/async_safety/`, or
similar — follow the project's existing convention) and adapt.

If the project has its own runtime gate/conftest that already wraps every
test in a strict blocking-call detector (e.g. Python's Blockbuster), you
do NOT need to import or activate the detector yourself here — just drive
the real async entry point and let the project's own gate do its job. If
the project has no such gate yet, this test alone still has value as a
behavioral regression test, but it cannot prove blocking-IO protection by
itself — pair it with Step 5 of Section 1 in SKILL.md (verify teeth
against whatever gate the project *does* have, even a manual timing
check).

Teeth check before you commit (see
`references/async-safety-anchor-rules.md`):
  1. reintroduce the block  -> the project's gate command must FAIL
  2. restore the fix        -> it must PASS
"""

from __future__ import annotations

from pathlib import Path

import pytest

# from <project_module> import <real_async_entry_point>

pytestmark = pytest.mark.asyncio


async def test_<entry_point>_offloads_blocking_io_on_<branch>(tmp_path: Path) -> None:
    # Arrange: real inputs at the boundary the code blocks on (filesystem ->
    # tmp_path; HTTP/subprocess -> stub the external service). Mock ONLY the
    # external boundary, never the offload under test.

    # Act + Assert: call the REAL production async entry point and drive the
    # specific branch you are guarding (e.g. force a failure to hit the
    # cleanup path). If the entry point performs blocking IO on the event
    # loop, the project's gate should fail this test.
    #   await <real_async_entry_point>(...)
    raise NotImplementedError("Replace with the real async entry point call.")
