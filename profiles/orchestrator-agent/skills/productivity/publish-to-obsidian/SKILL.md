---
name: publish-to-obsidian
description: Publish to Obsidian vault with frontmatter and paths.
---

# Publish to Obsidian Skill

Direct local publishing to Obsidian vault — no agent round-trip, no async delays.
Uses `write_file` with validated paths and generated frontmatter.

## When to Use

- Publishing guides, notes, logs, research, daily notes
- Any content that belongs in `/home/massi/ObsidianVault/`
- When you need **immediate, verified** file creation
- Generating proper YAML frontmatter for Obsidian

## Vault Structure (User Convention)

```
/home/massi/ObsidianVault/
├── Articles/ # Polished articles, blog posts
├── Brain/ # Second brain / Zettelkasten
├── Guides/
│ ├── Linux/ # Linux guides (Omarchy, etc.)
│ ├── Dev/ # Development guides
│ └── Tools/ # Tool tutorials
├── Journal/ # Daily journals
├── Logs/ # Session logs, agent runs
├── Notes/ # Raw notes, fleeting thoughts
└── .obsidian/ # Obsidian config (don't touch)
```

## Core Functions

### 1. `publish_to_obsidian()` — Main entry point

```python
publish_to_obsidian(
 content: str,
 title: str,
 folder: str = "Notes",
 tags: list = None,
 aliases: list = None,
 description: str = "",
 links: list = None,
 author: str = "@architect",
 version: str = "1.0",
 frontmatter_extras: dict = None
) -> dict # {path, bytes, verified, frontmatter}
```

### 2. `resolve_vault_path()` — Path resolution

```python
resolve_vault_path(folder: str, title: str) -> str
```

### 3. `generate_frontmatter()` — YAML frontmatter

```python
generate_frontmatter(
 title: str, folder: str, tags: list, aliases: list,
 description: str, links: list, author: str, version: str, extras: dict
) -> str
```

### 4. `append_wikilinks()` — Add related notes section

```python
append_wikilinks(content: str, links: list) -> str
```

## Usage Examples

### Publish a guide
```python
result = publish_to_obsidian(
 content=guide_markdown,
 title="Omarchy Linux Learning Guide - 7-Day Path",
 folder="Guides/Linux",
 tags=["omarchy", "linux", "hyprland", "guide", "learning-path"],
 aliases=["Omarchy 7-Day Guide", "Omarchy Learning Path"],
 description="Complete structured learning path for Omarchy Linux",
 links=["Notes/omarchy-50-features-guide-bilingual.md"],
)
print(f"Published to: {result['path']}")
```

### Publish a session log
```python
publish_to_obsidian(
 content=log_content,
 title=f"Session Log - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
 folder="Logs",
 tags=["session", "log", "architect"],
 frontmatter_extras={"session_id": "abc123", "model": "nemotron-3-ultra-free"}
)
```

### Publish a raw note
```python
publish_to_obsidian(
 content=note_content,
 title="Quick thought on Hyprland animations",
 folder="Notes",
 tags=["hyprland", "animation", "fleeting"]
)
```

## Frontmatter Template

```yaml
---
title: "<title>"
description: "<description>"
tags:
 - <tag1>
 - <tag2>
created: "<ISO8601 with timezone>"
updated: "<ISO8601 with timezone>"
author: "<author>"
version: "<version>"
folder: "<folder>"
aliases:
 - <alias1>
 - <alias2>
---
```

## Safety Rules

- **Never** write outside `/home/massi/ObsidianVault/`
- **Always** verify write with `verified: true`
- **Sanitize** filenames (remove `/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`)
- **Create** parent directories automatically
- **Preserve** existing files — overwrite only on explicit intent

## Implementation

The skill provides a Python module at `scripts/obsidian_publisher.py`
with all functions above. Import and use directly in `execute_code`
or from other skills.

```python
from scripts.obsidian_publisher import publish_to_obsidian
```