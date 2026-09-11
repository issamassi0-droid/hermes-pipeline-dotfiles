---
name: pipeline
description: Run the multi‑agent content pipeline from any Hermes profile. Usage: 'pipeline "Write about ..."' or 'pipeline --tier lite "..."'
version: 1.0.0
---

# Pipeline Skill

When the user says `pipeline` or `pipe` followed by arguments, treat it as a request to run the pipeline orchestrator.

**Available commands:**

- `pipeline <mission>` – run with auto‑tier detection.
- `pipeline --tier lite|standard|deep <mission>` – force a tier.
- `pipeline --dry-run <mission>` – show the plan without executing.
- `pipe` is a synonym for `pipeline`.

**Action:**

Execute the shell command:

```bash
pipeline-orchestrator <arguments>
```

Capture stdout and stderr, and present the results to the user. If the output contains JSON, pretty‑print it. Always include the final vault path and the work directory.

**Fallback:**

If `pipeline-orchestrator` is not in `PATH`, assume it is at `~/.local/bin/pipeline-orchestrator`.

**Examples:**

- User: `pipeline "Compare React and Vue for 2026"`  
  → Run `pipeline-orchestrator "Compare React and Vue for 2026"`

- User: `pipe --tier lite "What is the latest Python version?"`  
  → Run `pipeline-orchestrator --tier lite "What is the latest Python version?"`

- User: `pipeline --dry-run "Explain quantum computing"`  
  → Run `pipeline-orchestrator --dry-run "Explain quantum computing"`

Always report the full output to the user, including the final artifact path.