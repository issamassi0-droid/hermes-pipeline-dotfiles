# System Contracts — v1.1.0 Patch Notes

**Released:** 2026-09-11
**Based on:** YouTube research synthesis (4 videos, full transcripts)

## What's New

### 1. Shared Memory Vault (M1)
Added `vault` section to registry.json and protocol.md. All agents read/write to a shared Obsidian directory.

### 2. Tool Pruning per Agent (M2)
Added `tools` allowlist per agent in registry.json. No agent may use a tool outside its allowlist.

### 3. Deduplication Layer (M4)
Added `dedup` payload type and deduplication pass between research → strategy stages.

### 4. Scoring Rubric (M5)
Added `rubric` section to routing.yaml. 5-axis rubric (0-100) for judge decisions.

### 5. Group Room Turn Limits (M6)
Added `group_room_turn_limit` to protocol.md (default: 8 turns).

### 6. Persistent Workspace Directory (M7)
Added `workspace` section to ledger-schema.json. Each mission gets a working directory.

### 7. Human Gate (M3)
Added `human_gate` stage and `proposal` payload type. Single approval moment before execution.

---

## Files Modified
- `registry.json` — vault + tools sections
- `protocol.md` — dup, proposal, group_room_turn_limit
- `routing.yaml` — rubric + human_gate
- `ledger-schema.json` — workspace section
- `quality-charter.md` — self_healing article

---

*Authored by @deep-dive based on YouTube research. All changes logged in CHANGELOG.md.*