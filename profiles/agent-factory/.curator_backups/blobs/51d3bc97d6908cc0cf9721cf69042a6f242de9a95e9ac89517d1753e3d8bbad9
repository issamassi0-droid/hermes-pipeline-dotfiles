---
name: hermes-content-pipeline
description: Build Hermes multi-agent content pipeline with orchestrator.
version: 1.0.0
---

# Hermes Content Pipeline Builder

This skill guides building a fully automated, multi-agent content pipeline using Hermes profiles. It covers agent creation, orchestrator scripting, integration with Obsidian, and user preferences for local-first, token-efficient, and temporal-gated workflows.

## Overview

Create a pipeline that takes a mission brief, runs through Cabinet Office triage (Architect), then sequentially executes: Researcher → Strategist → Writer → Editor/QA → Publisher → Analytics. The pipeline respects token budgets, temporal freshness, immediate local Obsidian saves, and free model constraints.

## Prerequisites

- Hermes installed and `hermes` in PATH.
- Obsidian vault at `~/ObsidianVault`.
- Free models available (meituan/longcat-2.0:free, nemotron-3-ultra-free).
- Python 3.8+ for orchestrator script.

## Step-by-Step Procedure

### 1. Create Hermes Profiles

For each ministry, clone from `bot-maker`:

```bash
hermes profile create <name> --clone-from bot-maker
```

Profiles needed: `architect`, `omni-researcher`, `strategist`, `draft-writer`, `editor-qa`, `publisher`, `analytics`.

### 2. Write SOUL.md for Each Profile

Each `~/.hermes/profiles/<name>/SOUL.md` must contain:
- **Identity**: Who the bot is and its one-line purpose.
- **Creed**: 4–6 rules specific to its work.
- **Canon**: The five canon rules (Match Before Act, Labeled Truth, Confirm Irreversible, Read Before Write, Report Plainly), adapted to the domain.
- **Skills**: 4–6 skills with clear layers (e.g., Researcher: Intent Engine, Multi-Source Sweep, Deduplication, Credibility Classification, Resources Section, Fast Mode, Article Writing, Humanization, Related Questions).
- **Tools**: CLI commands, APIs, or scripts used.
- **Boundary**: Domain, refusal, and evidence lines.

**Critical requirements**:
- **Publisher**: Must have immediate local Obsidian save — no confirmation prompts. Save to `~/ObsidianVault/Articles/{category}/{slug}.md` immediately.
- **Architect**: Must include a Temporal Gate as Step 0 — verify current date/time and enforce temporal bounds per request class (news ≤7d, guides ≤6mo, deep reports ≤12mo).
- **All profiles**: Use free models only. Set in `profile.yaml` or via `hermes -m`.

### 3. Write profile.yaml

Each profile directory needs a `profile.yaml` with UI metadata:
- shape (e.g., hexagon, diamond, square, star)
- color (hsl notation)

Example:
```yaml
description: "Architect-Orchestrator — master intelligence"
shape: star
color: hsl(30 60% 50%)
```

### 4. Create Orchestrator Script

Write a Python script at `~/.local/bin/pipeline-orchestrator` that:
- Accepts a mission and optional tier (`--tier lite|standard|deep`).
- Calls Architect with the mission to get a routing ticket (JSON).
- Determines tier from Architect or override.
- Executes stages sequentially: Researcher → Strategist → Writer → Editor → Publisher → (Analytics for deep).
- Uses `hermes -p <profile> -z <prompt> --cli --no-restore-cwd` to get JSON responses.
- Saves intermediate JSON outputs to a temp directory.
- Generates a blind-spot coverage matrix.
- Returns final artifact path and workdir.

**Key implementation details**:
- Parse JSON responses from each stage; if not valid JSON, treat as raw text.
- Timeout each stage (typically 180–300s).
- Use `extract_json` to find the first JSON object in output.
- Pass previous stage outputs as context in prompts.

### 5. Create Hermes Skill for Invocation

Place a skill at `~/.hermes/skills/pipeline/SKILL.md` that tells any Hermes bot how to handle `pipeline` or `pipe` commands. It should execute `pipeline-orchestrator` with the given arguments and report results.

### 6. Add Shell Aliases

Append to `~/.bashrc`:
```bash
alias pipeline='~/.local/bin/pipeline-orchestrator'
alias pipe='pipeline'
alias piporch='~/.local/bin/pipeline-orchestrator'
```

### 7. Test Each Stage

- Test each profile individually with a simple prompt.
- Test the orchestrator end-to-end with a dry run (`--dry-run`).
- Verify publisher writes to Obsidian immediately.

## Pitfalls & Solutions

1. **Publisher test times out (exit 124)**: Ensure the orchestrator uses a reasonable timeout and that the publisher profile is correctly patched to save locally without confirmation. Retry with shorter prompts.

2. **Same-model blind spot for Editor/QA**: For high-stakes content, the editor-qa should use a different model family than draft-writer. If constrained to free models, document this limitation and rely on the Editor's strict verification rules.

3. **OpenCode launch issues**: Never spawn OpenCode; use Hermes commands directly. The orchestrator calls `hermes` CLI, and the Hermes skill invokes the orchestrator via terminal.

4. **Temporal stale data**: Architect must check current date/time first and enforce bounds. Ensure the Temporal Gate is Step 0 in Architect SOUL.md.

5. **Token budget overruns**: Architect must allocate per-agent token windows and enforce via prompt caps. Use the three-tier system (LITE=2k, STANDARD=15k, DEEP=50k) with writer-first reservation.

## User Preferences (for this user)

- **Free models only**: Use `meituan/longcat-2.0:free` and `nemotron-3-ultra-free`; never suggest paid APIs.
- **Obsidian first**: Publisher saves locally immediately — no confirmation prompts, no delays.
- **Aliases**: Prefer `pipeline`, `pipe`, `piporch` for quick invocation.
- **Avoid OpenCode**: Use Hermes skills and direct command execution; do not launch OpenCode.
- **Muted color palette**: When customizing, use warm, muted, low-blue colors for eye comfort.

## References

- Hermes documentation: https://hermes-agent.nousresearch.com/docs
- `hermes profile` commands: `hermes profile create`, `hermes profile list`
- SOUL.md template: see the system prompt for the Bot Template.
- Cabinet Office meta-architecture: see attached files for triage and tiering.
- Ministry of Bots architecture: for checkpoint-before-action patterns.

---
*This skill was born from building a complete content pipeline for user issamassi0-droid on 2026-09-09.