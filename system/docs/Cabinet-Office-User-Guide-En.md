---
title: Cabinet-Office Multi-Agent System — How to Use It
type: guide
language: english
created: 2026-09-11
updated: 2026-09-11
version: "1.0"
tags: [cabinet-office, guide, usage, tutorial]
status: published
---

# Practical User Guide — How to Use the System Inside Hermes

> [!ABSTRACT]
> This guide explains how to use the Cabinet-Office Multi-Agent System from inside Hermes Agent chat.

---

## Method 1: From Inside Hermes Chat (Easiest)

You're currently talking to `@deep-dive` (YouTube research bot).

To use the ministry system, simply:

### 1. Research via @omni-researcher

```bash
"Research [your topic]"
```

This activates `@omni-researcher` and searches:
- Web
- Twitter/X
- Reddit
- News

### 2. YouTube Search via @deep-dive

```bash
"Search YouTube for [your topic]"
```

### 3. Writing via @draft-writer

```bash
"Write an article about [your topic]"
```

### 4. Quality Check via @editor-qa

```bash
"Check this text: [text]"
```

### 5. Publishing via @publisher

```bash
"Publish this article to [location]"
```

---

## Method 2: Direct Agent Usage

Each agent is a "profile" inside Hermes. To activate:

### 1. Send task to specific agent

```bash
# Type in Hermes chat:
"@omni-researcher: Research AI impact on education"

# Or:
"@strategist: Build a plan for writing a programming article"

# Or:
"@editor-qa: Verify these claims..."
```

### 2. Pipeline Sequence

```bash
# Step 1: Research
"@omni-researcher: Research latest cryptocurrency news"

# Step 2: Strategy
"@strategist: Convert research into investment plan"

# Step 3: Writing
"@draft-writer: Write report based on plan"

# Step 4: Verification
"@editor-qa: Verify every claim in report"

# Step 5: Publishing
"@publisher: Publish report to vault"
```

---

## Method 3: Unified CLI (12 Commands)

```bash
# Simple task (Architect only)
python3 ~/.hermes/system/cabinet-office.py run "What are best SEO practices?"

# Quick research (Researcher + Publisher)
python3 ~/.hermes/system/cabinet-office.py run "Research AI impact on education" --tier tier_1

# Full strategy (5 agents)
python3 ~/.hermes/system/cabinet-office.py run "Write article about future of programming" --tier tier_2

# Comprehensive analysis (8 agents)
python3 ~/.hermes/system/cabinet-office.py run "Analyze cryptocurrency market 2026" --tier tier_3

# Check system status
python3 ~/.hermes/system/cabinet-office.py status

# Check quality
python3 ~/.hermes/system/cabinet-office.py quality

# Check budget
python3 ~/.hermes/system/cabinet-office.py budget

# Extract lessons
python3 ~/.hermes/system/cabinet-office.py learn --mission m001
```

---

## Method 4: Individual Scripts (17 Scripts)

```bash
# Circuit breaker
python3 ~/.hermes/system/scripts/circuit-breaker.py --status

# Watchdog
python3 ~/.hermes/system/scripts/watchdog.py

# Dynamic routing
python3 ~/.hermes/system/scripts/dynamic-router.py --task "Write article about AI"

# Quality gate
python3 ~/.hermes/system/scripts/quality-gate.py --check output.md

# Self-learning
python3 ~/.hermes/system/scripts/self-learning.py --extract mission-report.json

# Reliability standards
python3 ~/.hermes/system/scripts/reliability-standards.py
```

---

## Tier System Explained

### Tier 0 — Immediate Decision (~11 seconds)
- **Agents:** Architect only
- **When to use:** Simple questions, quick decisions
- **Example:** "What is Japan's capital?"

### Tier 1 — Quick Research (~44 seconds)
- **Agents:** Researcher → Publisher
- **When to use:** Need quick information
- **Example:** "What are the latest SpaceX news?"

### Tier 2 — Strategy and Audit (~2:40 minutes)
- **Agents:** Researcher → Strategist → Writer → Auditor → Publisher
- **When to use:** Writing article, report, research
- **Example:** "Write an article about future of programming"

### Tier 3 — Comprehensive Analysis (~5:20 minutes)
- **Agents:** All 8
- **When to use:** Deep research, detailed report
- **Example:** "Analyze cryptocurrency market 2026"

---

## Agent Guide — Who to Ask and When?

| If you want... | Ask... | Technical | Tier |
|---|---|---|---|
| Comprehensive internet research | @omni-researcher | `research-agent-multi` | Tier 1+ |
| YouTube video search | @deep-dive | `research-agent-youtube` | Tier 2+ |
| Convert to idea or plan | @strategist | `strategy-agent` | Tier 2+ |
| Write article or report | @draft-writer | `drafting-agent` | Tier 2+ |
| Verify text quality | @editor-qa | `qa-agent` | Tier 2+ |
| Publish or distribute content | @publisher | `distribution-agent` | Tier 1+ |
| Measure content performance | @analytics | `analytics-agent` | Tier 3 |
| Create new bot | @bot-maker | `agent-factory` | Special |
| Fix system issue | @omarchy | `system-operator` | Special |
| Monitor sources | @scout | `source-monitor` | Tier 3 |
| Coordinate complex tasks | @architect | `orchestrator-agent` | All |

---

## Complete Practical Example

### Task: "Write an article about the future of programming"

```bash
# Step 1: Check system status
python3 ~/.hermes/system/cabinet-office.py status

# Step 2: Run the task
python3 ~/.hermes/system/cabinet-office.py run "Write article about future of programming 2026" --tier tier_2

# Step 3: Verify quality
python3 ~/.hermes/system/cabinet-office.py quality

# Step 4: Extract lessons
python3 ~/.hermes/system/cabinet-office.py learn --mission m001
```

### Or from inside Hermes chat:

```bash
@omni-researcher: Research future of programming 2026
@strategist: Build article plan from research results
@draft-writer: Write article based on plan
@editor-qa: Verify every claim
@publisher: Publish article to vault
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Agents aren't working | `python3 ~/.hermes/system/cabinet-office.py heartbeat --check` |
| Outputs are poor quality | `python3 ~/.hermes/system/cabinet-office.py quality` |
| Tokens run out quickly | `python3 ~/.hermes/system/cabinet-office.py budget` |
| Script error | `bash ~/.hermes/setup.sh --verify` |

---

## Optimal Usage Tips

### Do ✅
- Use Tier 0 for simple questions
- Check quality after every task
- Extract lessons from failed tasks
- Update system regularly: `bash setup.sh --pull`

### Don't ❌
- Don't use Tier 3 for simple tasks (wastes resources)
- Don't bypass the human gate
- Don't trust outputs without verification
- Don't forget current metrics are circular (Circular Validation)

---

> [!INFO] Guide Info
> **Version:** 1.0 | **Date:** 2026-09-11
> **System:** Cabinet-Office v1.7.0
> **Location:** ~/.hermes/system/
> **Commands:** 12 main commands + 17 scripts
> **Agents:** 11 specialized agents
