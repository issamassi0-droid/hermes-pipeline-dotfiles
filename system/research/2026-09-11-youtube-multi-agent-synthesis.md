# YouTube Multi-Agent System Research — Synthesis & Missing Ideas

**Date:** 2026-09-11
**Sources:** 4 deep-dive videos (full transcripts read)
**Goal:** Find what other Hermes multi-agent builders are doing that this system doesn't have yet, and implement the highest-value gaps.

---

## The Four Systems Researched

### 1. Julian Goldie — "Agent OS" (2 videos)
- **Scale:** 4,000+ members in AI Profit Boardroom
- **Core insight:** "Shared memory vault is what makes the system stick."
- **Architecture:** Multiple agents reading/writing to a shared Obsidian vault. Multi-gateway (laptop + server + cloud). Cron-triggered pipelines.
- **Key innovation:** The "Oracle Radar" — 4-layer pipeline: Alarm (cron) → Eyes (live search) → Judge (scoring across 6 relevance signals) → Messengers (multi-format output: social post, video outline, SEO article).
- **Memory:** Persistent Chrome memory, durable notepads.

### 2. Callum (Waterloots) — Bot Mode Deep Dive
- **Scale:** Solo operator, research team
- **Core insight:** "It's not just about specialization, it's also about efficiency."
- **Architecture:** Orchestrator + Researcher + Librarian. Group rooms with turn limits. Tool pruning per agent.
- **Key innovations:**
 - **Tool pruning:** Each agent gets ONLY the tools it needs (researcher doesn't get wiki skill, orchestrator doesn't get web search). This saved 20 minutes of wasted tool calls in his test.
 - **Keep bots warm:** 3→5 bots kept loaded for instant switching.
 - **Group room turn limits:** Prevents infinite loops between agents — the room has a default number of turns before requiring human input.
 - **Local + cloud delegation:** Researcher on cheaper model, orchestrator on powerful model.
 - **"Refine" command:** After a session, agents self-review and save learnings to memory.

### 3. Kanban Board Multi-Agent Workflow (the goldmine video)
- **Scale:** 18 workers in parallel, 97 tasks in one run
- **Core insight:** "It isn't setting up the agents themselves, it's getting them to work together on one job without stepping on each other."
- **Architecture:** Scouts (X + Web) → Orchestrator (judge with rubric) → Parallel Researchers (3 per issue) → Analyst/Video Producer → Human Gate (Telegram) → Builder/Tester → Deliverables.
- **Key innovations:**
 - **Deduplication layer:** Multiple scouts find the same things — the orchestrator deduplicates before routing.
 - **Scoring rubric:** 5-axis rubric (frequency, pain intensity, solvability, solution gap, strategic fit) with a cutoff score (65/100) to decide build vs video vs shelve.
 - **Human gate via Telegram:** The ONLY place the human is in the loop. A single message: "4 proposals awaiting your approval." Reply approve/shelve/modify.
 - **Self-healing:** The system detected its own bug (writing to temp directories) and regenerated the deliverable — no human intervention.
 - **State survives restarts:** SQLite board means a crash loses nothing.
 - **Open-sourced the workflow skeleton:** "Tombi Studio Hermes multi-agent workflow" — a generalized template anyone can adapt.

---

## What This System Already Has (from the 2026-09-11 build)

| Feature | Status |
|---|---|
| 10-agent registry with ministries | ✅ registry.json |
| Inter-agent protocol (8 payload types) | ✅ protocol.md |
| Task ledger per mission | ✅ ledger-schema.json |
| 4-tier dynamic routing | ✅ routing.yaml |
| Quality charter with evidence labels | ✅ quality-charter.md |
| Self-improving evolution loop | ✅ evolution.md |
| Bootstrap / restore | ✅ bootstrap.sh |
| Status dashboard | ✅ status.html |

---

## Missing Ideas (ranked by impact × implementability)

### 🔴 Tier 1: Highest Impact — Implement Now

#### M1. Shared Memory Vault
**Source:** Julian Goldie
**Gap:** Each agent's memory is isolated. The user already uses Obsidian — this is a natural extension.
**What:** A shared Obsidian directory that all agents can read/write to. Brand voice, past work, audience knowledge, source ledger — all in plain Markdown files.
**Why it matters:** "Without that, every new agent means re-explaining your brand, your voice, and your audience over and over. With it, you brief once."
**Implementation:** Add `shared_workspace` to ledger-schema.json. Add `vault_path` to registry.json per agent. Protocol: agents write summaries to vault, not just to each other.

#### M2. Tool Pruning per Agent
**Source:** Callum
**Gap:** The registry lists `can_dm` but not tool scope. An agent with every tool wastes tokens and may do work outside its role.
**What:** Each agent has an explicit `tools` allowlist in its SOUL, not just "bundled skills."
**Why it matters:** Callum's researcher wasted 20 minutes on task delegation loops because it had access to sub-agent spawning. After pruning: the agent stayed in its lane.
**Implementation:** Add `tool_scope` to registry.json per agent. Architect checks tool scope during triage.

#### M3. Human Gate with Single Approval Point
**Source:** Kanban workflow
**Gap:** The system has editor-qa approval but no single, mobile-friendly approval moment before execution.
**What:** One message to the user (desktop or Telegram) listing proposals. Reply approve / shelve / modify.
**Why it matters:** Keeps the human in the loop at exactly the right moment — after all the research, before any expensive build.
**Implementation:** Add `human_gate` stage to the pipeline. Architect formats proposals. User replies. Pipeline continues or halts.

#### M4. Deduplication Layer
**Source:** Kanban workflow
**Gap:** Multiple researchers or scouts will find the same sources. The system has no mechanism to detect or handle this.
**What:** Before routing to the next stage, the orchestrator checks for duplicate claims/sources against what's already in the ledger.
**Why it matters:** Saves tokens, saves time, prevents the "18 workers all finding the same 3 sources" failure mode.
**Implementation:** Add `deduplication` pass between research and strategy stages. Research.json includes source fingerprints.

#### M5. Scoring Rubric for Routing
**Source:** Kanban workflow
**Gap:** Routing uses qualitative judgment, not quantitative scoring.
**What:** A configurable rubric (5 axes, each 0-20, total 100) that the judge agent uses to decide: build / write / shelve.
**Why it matters:** Makes routing auditable and tunable. "65/100 cutoff" is a number you can adjust based on how many proposals you're getting.
**Implementation:** Add `scoring_rubric` to routing.yaml. Orchestrator uses it during triage.

#### M6. Group Room Turn Limits
**Source:** Callum
**Gap:** The protocol has a 12-message budget but no per-conversation turn limit. Two agents could burn the entire budget in one loop.
**What:** Group chats (multi-agent conversations) have a configurable turn limit (default: 8 turns). After that, the conversation pauses and waits for human direction.
**Why it matters:** Prevents the classic failure mode where researcher and orchestrator loop forever.
**Implementation:** Add `group_room_turn_limit` to protocol.md. Architect enforces.

#### M7. Persistent Workspace Directory
**Source:** Kanban workflow
**Gap:** Ledger files exist but there's no shared working directory for artifacts (drafts, prototypes, research reports).
**What:** A well-known directory structure where all agents read/write working artifacts. Survives restarts. Auditable.
**Why it matters:** The Kanban video showed a self-healing moment: the agent wrote slides to a temp directory, detected the error, and regenerated to a persistent directory. Without persistent workspace, the second save would have also failed.
**Implementation:** Add `workspace_path` to registry.json. Each mission gets a subdirectory.

---

### 🟡 Tier 2: High Impact — Requires More Setup

#### M8. Scout Pattern for Continuous Monitoring
**Source:** Kanban workflow
**Gap:** Omni-researcher does one-shot research. No agent continuously monitors sources.
**What:** A "scout" agent profile that runs on cron, sweeping X/Reddit/web for new developments, feeding findings into a shared inbox.
**Why it matters:** Enables the "detect → validate → route → ship" pipeline that the Kanban video demonstrated.
**Implementation:** New agent type `scout` in registry.json. Cron-triggered. Writes to `workspace/inbox/`.

#### M9. Cron-Triggered Full Pipelines
**Source:** Julian Goldie + Kanban
**Gap:** The system has cron for evolution review but no cron-triggered content/monetization pipelines.
**What:** A pipeline that starts from a cron job, not a user command. Every morning: scout → research → judge → human gate → build.
**Why it matters:** "That runs on its own every single day before anyone opens a laptop."
**Implementation:** Add `pipeline_trigger` to routing.yaml. Architect can launch a pipeline on schedule.

#### M10. Multi-Model Strategy Within a Tier
**Source:** Callum
**Gap:** routing.yaml mentions model selection by tier but not per-agent specialization within a tier.
**What:** Researcher on cheap/fast model (e.g., Nemotron). Orchestrator on powerful model (e.g., GPT-5.5). Librarian on local model.
**Why it matters:** "Find any type of repeatable work... delegate specific tasks or bots to local models so that a more powerful cloud agent can delegate to local models to do most of the work and still maintain the same level of quality but significantly reduce the cost."
**Implementation:** Add `model_preference` to registry.json per agent. Architect respects it during spawning.

#### M11. Self-Healing at Runtime
**Source:** Kanban workflow
**Gap:** The system has crash recovery in evolution.md but no operational self-healing during a run.
**What:** If an agent detects its own output is broken (wrong path, missing file, format error), it attempts a self-repair before escalating.
**Why it matters:** The Kanban video showed the agent detecting it wrote slides to a temp directory and regenerating to a persistent directory — no human needed.
**Implementation:** Add `self_healing` rules to quality-charter.md. Max 1 self-repair attempt per failure, then escalate.

#### M12. "Refine" / Self-Review Command
**Source:** Callum
**Gap:** No mechanism for agents to learn from their own sessions.
**What:** After a group session, the orchestrator runs a "refine" pass: what worked? what should change? Updates memory files.
**Why it matters:** Over time, agents get better at coordination without explicit reprogramming.
**Implementation:** Add `refine` payload type to protocol.md. Triggered after mission close.

---

### 🟢 Tier 3: Nice-to-Have — Future

#### M13. Open Source Workflow Templates
**Source:** Kanban video (open-sourced his workflow)
**Gap:** No reusable skeletons for common tasks.
**What:** A library of workflow templates (content pipeline, research sprint, code review, etc.) that can be instantiated with one command.
**Implementation:** `system/templates/` directory.

#### M14. Telegram as Human Interface
**Source:** Kanban workflow
**Gap:** The user's system is desktop-only for human interaction.
**What:** Proposals, approvals, and alerts delivered via Telegram. User can approve from phone.
**Implementation:** Requires Telegram bot setup. Add `telegram_output` option to registry.json.

#### M15. Multi-Gateway / Fleet Strip
**Source:** Julian Goldie
**Gap:** All agents run on one machine.
**What:** Register multiple backends (laptop, server, cloud) in one roster. Agents can run on different machines.
**Implementation:** This is a Hermes desktop app feature, not a system-layer feature. Just note it.

#### M16. "Keep Bots Warm" Runtime Optimization
**Source:** Callum
**Gap:** No agent preloading.
**What:** Keep 3-5 bots loaded in RAM for instant switching.
**Implementation:** Hermes desktop app setting, not system-layer.

---

## What I'm Implementing Right Now (Tier 1)

1. **M1. Shared Memory Vault** → extend registry.json + protocol.md
2. **M2. Tool Pruning** → extend registry.json
3. **M4. Deduplication Layer** → extend protocol.md
4. **M5. Scoring Rubric** → extend routing.yaml
5. **M6. Group Room Turn Limits** → extend protocol.md
6. **M7. Persistent Workspace** → extend ledger-schema.json
7. **M3. Human Gate** → extend protocol.md + routing.yaml

---

*Research by @deep-dive, 2026-09-11. Sources: full transcripts of z40Du-SgLiQ, 3RoK0rrOHCA, 4ATb63ZjZNk, EKVRqcpTT6s.*