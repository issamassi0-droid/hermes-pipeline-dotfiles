---
name: youtube-research-to-system
description: "YouTube research to system change workflow."
version: 1.0.0
author: deep-dive
license: MIT
metadata:
 hermes:
 tags: [YouTube, Research, Synthesis, System-Change]
 related_skills: [research, youtube-content]
---

# YouTube Research → System Change

A class-level skill for the end-to-end workflow: search YouTube for videos about a topic, read full transcripts, synthesize findings across sources, and implement concrete changes to a system.

## When to use

When the user asks to research a topic, find similar experiences online, and turn findings into system changes. This is NOT just summarization — it's research that produces actionable output.

## Procedure

### Step 1: Search YouTube
```bash
web_search("site:youtube.com <topic>", limit=10)
```
If results are thin, broaden: `web_search("<topic> experience review tutorial", limit=10)`.

### Step 2: Select and read full transcripts
For each promising video, fetch the transcript:
```bash
uv run python ~/.hermes/profiles/<profile>/skills/media/youtube-content/scripts/fetch_transcript.py "<url>" --timestamps
```
**Read all transcripts fully.** Do not skip videos. The value is in cross-referencing multiple sources.

### Step 3: Extract and synthesize
From each transcript, extract:
- **Personal experiences** — what the creator/subject went through
- **Lessons learned** — key takeaways and insights
- **Contradictions** — where videos disagree (and what that means)
- **Unique angles** — what each video adds that others don't
- **Depth indicators** — which videos go surface-level vs. deep

Synthesize across sources into a coherent picture. Identify patterns that appear across multiple creators.

### Step 4: Map to concrete changes
Translate findings into specific system modifications:
- New contracts/protocols to add
- New agents or roles to register
- Configuration changes to existing files
- New files or directories to create

### Step 5: Implement
Apply changes as file edits. Use `write_file`, `patch`, and `terminal` as appropriate.

### Step 6: Document
Write a synthesis report and append entries to CHANGELOG.md.

## Resource-Conserving Principle

This workflow prioritizes **high-impact, low-token** changes. The goal is not to build elaborate new systems but to modify what exists to produce better results faster.

When proposing changes:
- Prefer configuration additions over new code
- Prefer protocol additions over new agents
- Prefer small edits that serve multiple purposes over large standalone additions
- Never waste tokens on features the user hasn't asked for

## Output Format

Save findings to `/home/massi/.hermes/system/research/<date>-<topic>-synthesis.md` with:
- Sources list (video titles, links, key timestamps)
- What people experience (synthesis)
- Recommended videos section
- Where videos disagree
- Concrete changes proposed and implemented

## Pitfalls

- **Don't just summarize** — the value is in cross-source synthesis and actionable mapping
- **Don't skip transcripts** — reading the actual text reveals details that search descriptions miss
- **Don't over-engineer** — resource-constrained system (old laptop, free APIs) means small, efficient changes beat large architectures
- **Don't fabricate** — if a transcript is unavailable or unclear, say so. Never invent content.
- **Don't forget the system layer** — every change should reinforce or extend the contracts at `/home/massi/.hermes/system/`

## System Contracts Reference

All changes made through this workflow should respect the system contracts:
- `/home/massi/.hermes/system/registry.json` — agent registry
- `/home/massi/.hermes/system/protocol.md` — inter-agent protocol
- `/home/massi/.hermes/system/routing.yaml` — routing and scoring rules
- `/home/massi/.hermes/system/quality-charter.md` — quality standards
- `/home/massi/.hermes/system/evolution.md` — evolution loop
- `/home/massi/.hermes/system/ledger-schema.json` — task ledger structure
