---
name: obsidian-2nd-brain
description: Build a second brain in Obsidian with layered rules.
version: 0.1.0
author: Hermes
platforms: [linux, macos]
metadata:
 hermes:
 tags: [Obsidian, Productivity, Second-Brain, Knowledge-Management, Workflow]
---

# Obsidian 2nd Brain (Second Brain Prompt Pack)

Build a second brain in Obsidian — a structured vault with layered ownership, a nightly compile job, and a routing system that keeps an agent from guessing where to write. This skill captures the system from the prompt pack: the folder structure, the ownership rule, the context rule, the compile workflow, and the scheduled jobs.

This is the system itself, not a summary. Use it to implement the vault, explain the layers, or guide a user through each step of the build.

## When to Use

- User asks to "build a second brain" in Obsidian
- User mentions "The Second Brain Prompt Pack"
- User wants to set up a vault with `/0-raw`, `/1-wiki`, `/2-digest`
- User asks about the ownership rule (one writer per layer)
- User wants to set up the `/learn` compile command
- User asks about the nightly compile or scheduling
- User asks about `context-rule.md` or the routing table
- User asks about the difference between agent memory and the vault

## Prerequisites

- Obsidian installed and a vault path known (e.g., `/home/massi/ObsidianVault`)
- The user has write access to that vault directory
- The agent has file tools: `read_file`, `write_file`, `patch`, `terminal`

## The Mental Model

### The Three Layers

| Layer | Purpose | Writer |
|-------|---------|--------|
| `/0-raw` | Capture inbox. User writes here, nothing else does. | User only |
| `/1-wiki` | Compiled pages. Nightly job rewrites from raw. | Nightly job only |
| `/2-digest` | Briefs and reviews. Scheduled jobs write here. | Scheduled jobs only |

**The ownership rule:** one writer per layer. The user writes to 0-raw and identity.md. The nightly compile job writes to 1-wiki. Scheduled jobs write to 2-digest. Without it, the agent eventually overwrites something the user wrote, and the day you stop trusting the vault is the day you stop opening it.

### What Each Layer Holds

- **0-raw** is the archive. It grows by adding, nothing is ever deleted, and it answers "where did I write that down." Lose it and it is gone forever.
- **1-wiki** is what the agent compiles out of the archive. It grows by rewriting, so one new call transcript can update six pages in a single pass. Lose it and one command rebuilds it.
- **2-digest** holds briefs and reviews from scheduled jobs.

### Root Files

| File | Purpose |
|------|---------|
| `identity.md` | Who the user is and how they decide. User owns it. |
| `projects.md` | Live state of what they are building. |
| `tasks.md` | Open loops. |
| `AGENTS.md` | The map. Read first, every session. |
| `router.md` | Where everything lives — routing table. |
| `context-rule.md` | How the agent is allowed to answer. |

## The Build Process

### Step 1: Give the agent a personality (optional)

Create or edit the identity file (SOUL.md or the agent's memory) so the persona persists. Example: name the agent "Dave," define it as the AI Operator running the back office of a one-person business, thinking a step ahead, flagging issues, and speaking like a human.

### Step 2: Build the vault structure

Create the following at the vault root:

```
/0-raw/
/1-wiki/
/2-digest/
identity.md
projects.md
tasks.md
AGENTS.md
```

Write `AGENTS.md` explaining the ownership rule: user writes to 0-raw and identity.md, nightly compile writes to 1-wiki, scheduled jobs write to 2-digest. Also write `CLAUDE.md` containing one line: `read AGENTS.md in this folder.`

### Step 3: Load the user profile

Interview the user one question at a time to build `identity.md`: who they are, what they do, goals this year, how they want to be talked to, strengths and weaknesses, current projects. Write it into `identity.md` at the vault root.

### Step 4: Teach the difference between memory and vault

Save this to the agent's memory: the vault is the library; the agent's own memory files stay small and hold how the user works and who they are. Before answering anything about the user's work, read `identity.md` and `context-rule.md` from the vault root and follow that rule.

### Step 5: Pin the context rule

Create `context-rule.md` at the vault root:

1. Read `identity.md` and `projects.md` before answering anything.
2. Pull only the notes that match the question, follow their links one hop out, and cite every note used by name.
3. If the vault has the answer, never answer from training data.
4. If the vault does not have it, say so plainly.
5. When the user says "remember this," write it to the right layer yourself.

Reference it from `AGENTS.md` as read-first.

### Step 6: Add the routing

Add a routing table to `AGENTS.md`. For each kind of work, list which files to read, which to skip, and which skill to use. Create `router.md` next to it holding the routing map for the whole vault, and add one line to the top of every folder's `AGENTS.md`: `if what you need is not in this folder, go back to the root router.`

### Step 7: Turn on capture

When the user sends a voice note or a message that is just a thought, transcribe it if needed and append it to a dated file in `0-raw`. Do not title it, do not tag it, do not file it anywhere else. The nightly job sorts it. Save this as a permanent instruction.

**Capture must be frictionless.** No titling, no tagging, no filing. Say the thought and get on with your day. `0-raw` is allowed to be a mess; the nightly job is what sorts it.

### Step 8: The compile

Place a few real sources into `0-raw` first (call transcripts, video transcripts, emails). Then:

Read everything new in `0-raw`. File each item where it belongs: facts about the user into `identity.md`, tasks into `tasks.md`, project updates into `projects.md`, knowledge into the right page in `1-wiki`. When updating a wiki page, rewrite it so it stays one clean current version rather than a stack of appendices. Link related pages. Log what you changed and why.

Run it once by hand and read the log before automating it. Then turn it into a command: `/learn`.

### Step 9: Add departments

Inside `1-wiki`, create a folder for each part of the business: finance, marketing, operations, accounts. Give each one an `AGENTS.md` describing what belongs there and how that work should be handled. Rewrite `router.md` at the vault root to point at every department. Add the line to each department `AGENTS.md`: `if what you need is not in this folder, go back to the root router.`

**Do not create a raw inbox per department.** One `0-raw` stays at the root. Six inboxes means choosing a folder at capture, which kills friction. One client call updates finance, operations, and accounts in a single pass — filing it into one department's inbox biases the result before the compile starts.

If raw ever needs subdividing, partition by facts, not judgements. Date and source are facts (`/0-raw/2026-08/`); what a note is about is a judgement (`/0-raw/finance/` is wrong). Raw is the only layer you can never regenerate, so it should carry the least structure.

### Step 10: Schedule the night shift

Every night at 3am, run the vault compile skill against the vault. Then at 7am, write the brief to `2-digest/brief.md` and send the five-bullet version: project state, open loops with anything untouched for fourteen days flagged, what carried over, and one thing the user is avoiding that matters. Set both up as scheduled jobs.

Check what it actually built before trusting it: run the scheduled job now to see it work, and ask it to summarise what it created.

### Step 11: Prove it is compounding

`/journey` — a timeline of every skill created, every memory file updated, and every job running. One screen showing the thing got better rather than just bigger.

## The Context Rule (Exact Wording)

Create `context-rule.md` in the vault root:

```
1. Read identity.md and projects.md before answering anything.
2. Pull only the notes that match the question, follow their links one hop out, and cite every note you used by name.
3. If the vault has the answer, never answer from training data.
4. If the vault does not have it, say so plainly.
5. When I say "remember this", write it to the right layer yourself.
```

Rule four is the one that earns its place. Synthesis is exactly where an agent will confidently make something up, and demanding citations is what makes the output checkable.

## Testing the System

A second brain earns its name when it answers something no single file in it contains. Try these once there's a week of captures in the vault:

1. "Where do finance and operations disagree about the delivery date on this account?"
2. "Find everything I have said about pricing across my calls, emails, and posts, and tell me where I have contradicted myself."
3. "Pull every objection that came up across my last ten sales calls, rank them by how often they appeared, and draft the answer to the top one in my voice."

Check the citations every time. The answer should come off a compiled page, and that page should link back to the raw files it was built from.

## Four Ways These Die

1. **Context overload:** past a couple of thousand notes, throwing everything into the context window degrades the answer. That is what the compiled layer is for.
2. **Invented synthesis:** agents invent synthesis. That is why the context rule demands citations and the compile logs what it changed.
3. **No maintenance:** nothing here maintains its own quality. Run a weekly pass for contradictions and stale pages.
4. **Deletion risk:** telling an agent not to delete something is a suggestion, not a setting. Control access with read-only keys and scoped permissions. Keep the vault local and keep secrets out of it.

## Verification

After implementing the system, run:

```
ls /path/to/vault/ | grep -E "0-raw|1-wiki|2-digest|identity.md|projects.md|tasks.md|AGENTS.md|router.md|context-rule.md"
```

All files and directories should exist. Then check the ownership rule is documented in `AGENTS.md` and `context-rule.md` contains the five rules.

## Pitfalls

- **Raw inbox per department.** Don't do this — one inbox at the root keeps capture frictionless.
- **Stale wiki pages.** The compile rewrites pages, so a page that hasn't been updated in months may be stale. The weekly maintenance pass catches this.
- **Skipping the interview.** If `identity.md` is rushed, the agent knows nothing about the user, and every answer it writes is built on that file.
- **Scheduling without testing.** The first scheduled job should be run immediately to verify it works. Do not wait until 3am to find out.
- **No citations.** The context rule demands citations; without them, the output is uncheckable and the agent will eventually invent synthesis.

## References

- The source: `/home/massi/Downloads/The Second Brain Prompt Pack.md`
- Obsidian vault: the user's vault at the configured path
- The agent's memory: not a library — keep it small and focused on how the user works
