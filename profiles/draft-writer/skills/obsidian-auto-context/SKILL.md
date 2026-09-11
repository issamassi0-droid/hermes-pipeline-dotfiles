---
name: obsidian-auto-context
description: >
 Automatically captures Hermes agent session context — research findings,
 decisions, tool outputs, and task summaries — into an Obsidian vault as
 linked, tagged Markdown notes. Supports daily notes, backlinks, and
 redaction of secrets. Turns disposable chat sessions into a permanent,
 searchable second brain.
version: 1.0.0
author: SkillForge Labs
license: MIT
platforms: [linux, macos, windows]
metadata:
 hermes:
 tags: [obsidian, memory, second-brain, research, productivity, context]
 category: productivity
 requires_toolsets: [obsidian, file, memory]
 fallback_for_toolsets: [memory]
---

# Obsidian Auto-Context

Capture what your agent learns before it disappears. This skill writes the
substance of each Hermes session — key findings, decisions, and action items —
into your Obsidian vault as clean, linked Markdown, so future sessions (and
future you) can retrieve it instead of rebuilding context from scratch.

## Why this exists

Agent sessions are brilliant and ephemeral. The reasoning evaporates when the
chat ends. This skill makes the output survive: every research pass becomes a
dated, tagged note in your vault, wiki-linked to related entities, and safe
(secrets are stripped before anything is written to disk).

## When to use

Follow the `obsidian_second_brain` permission protocol before writing:

- **High Value & Decisive**: Clear, conflict-free result achieved → log immediately.
- **Ambiguous or Mixed Session**: Contains both valuable ideas and trial-and-error → pause and request user confirmation first.
- **Low Value or Failed Experiments**: No usable outcome → remain silent.

Auto-capture triggers:
- End of a research or analysis session
- After making or recording a decision
- After creating or updating a skill or workflow
- On a scheduled cron summary (daily/weekly rollup)
- Manually, any time: `obsidian-save`

## What it writes

For each capture, one Markdown note in your existing `obsidian_second_brain` format:

- **Frontmatter** — `uuid`, `date`, `time`, `tags`, `source: hermes`, `session`, `status`, `confidence`
- **Abstract callout** — `> [!ABSTRACT]` with 1-sentence summary
- **Key findings** — bulleted, each with its source/link where available
- **Decisions** — what was decided and why (if any)
- **Action items** — `- [ ]` checkboxes
- **Links** — `[[wiki-links]]` to entities mentioned (people, tools, tickers, projects)

Notes land in `Logs/YYYY-MM-DD/` by default and are appended to
that day's daily note in `Journal/` under a `## Sessions` heading.

## How it works

1. At session end (or on trigger), the skill collects the session transcript
 and any tool results already in context.
2. It runs `references/redact.py` over the text to strip secrets
 (API keys, tokens, `.env`-style values, emails if configured).
3. It asks the model to produce the structured note above.
4. It writes the note via the `file` toolset into `Logs/YYYY-MM-DD/`
 and links it into the daily note in `Journal/` under `## Sessions`.

## Configuration

Set these in your Hermes config or `.hermes.md`:

```
OBSIDIAN_VAULT_PATH /home/massi/ObsidianVault (your existing vault)
SESSIONS_FOLDER Logs (your existing Logs/ directory)
REDACT_EMAILS true/false, default false
DAILY_NOTE_FOLDER Journal (default: Journal, matches your vault)
```

The skill writes session notes into `Logs/YYYY-MM-DD/` and appends them to the daily note in `Journal/` under a `## Sessions` heading.

## Example output

```markdown
---
uuid: "20260906-000000"
date: 2026-09-06
time: 00:00:00
tags:
 - session-log
 - hermes-agent
 - second-brain
topics: []
source: hermes
session: obsidian-auto-context
status: completed
confidence: high
---

> [!ABSTRACT] 💡 Executive Summary (TL;DR)
> - **Final Outcome:** [Single sentence capturing the exact result or decision]
> - **Verified Tools/Code:** `[Exact modules or scripts implemented]`

---

# Session — [Topic]

## Key findings
- Finding 1 with source link
- Finding 2

## Decisions
- Decision made and why

## Action items
- [ ] Action item 1

## Links
[[Entity1]] · [[Entity2]]
```

## Install

```
hermes skills install github.com/SkillForge-Labs/obsidian-auto-context
```

Then set `OBSIDIAN_VAULT_PATH` and run `obsidian-save` at the end of any session.

---

Built by **SkillForge Labs** — tools & context systems for AI-agent builders.
Free and MIT-licensed. If it saves you time, a star on the repo helps others find it.
