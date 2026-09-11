#!/usr/bin/env python3
"""
Obsidian Vault Publisher

Direct local publishing to /home/massi/ObsidianVault/ with proper
frontmatter, path resolution, and Obsidian-flavored Markdown.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import yaml

VAULT_ROOT = Path("/home/massi/ObsidianVault")

def sanitize_filename(name: str) -> str:
    """Sanitize string for safe filesystem usage."""
    name = re.sub(r'[\\/:*?"<>|]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name[:200]

def resolve_vault_path(folder: str, title: str) -> Path:
    """Resolve absolute path for a note in the vault."""
    safe_title = sanitize_filename(title)
    folder_path = VAULT_ROOT / folder
    folder_path.mkdir(parents=True, exist_ok=True)
    return folder_path / f"{safe_title}.md"

def generate_frontmatter(
    title: str,
    folder: str,
    tags: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    description: str = "",
    links: Optional[List[str]] = None,
    author: str = "@architect",
    version: str = "1.0",
    extras: Optional[Dict[str, Any]] = None
) -> str:
    """Generate YAML frontmatter for Obsidian."""
    now = datetime.now().astimezone().isoformat(timespec='seconds')
    
    fm = {
        "title": title,
        "description": description,
        "tags": tags or [],
        "created": now,
        "updated": now,
        "author": author,
        "version": version,
        "folder": folder,
    }
    
    if aliases:
        fm["aliases"] = aliases
    
    if extras:
        fm.update(extras)
    
    yaml_str = yaml.dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    return f"---\n{yaml_str}---\n"

def append_wikilinks(content: str, links: Optional[List[str]]) -> str:
    """Append a 'Related Notes' section with wikilinks."""
    if not links:
        return content
    
    link_lines = [f"- [[{link.replace('.md', '')}]]" for link in links]
    related_section = "\n## 🔗 Related Notes\n\n" + "\n".join(link_lines) + "\n"
    return content.rstrip() + "\n\n" + related_section

def publish_to_obsidian(
    content: str,
    title: str,
    folder: str = "Notes",
    tags: Optional[List[str]] = None,
    aliases: Optional[List[str]] = None,
    description: str = "",
    links: Optional[List[str]] = None,
    author: str = "@architect",
    version: str = "1.0",
    frontmatter_extras: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Publish content to Obsidian vault.
    
    Returns:
        dict with keys: path (str), bytes (int), verified (bool), frontmatter (str)
    """
    file_path = resolve_vault_path(folder, title)
    
    frontmatter = generate_frontmatter(
        title=title, folder=folder, tags=tags, aliases=aliases,
        description=description, links=links, author=author,
        version=version, extras=frontmatter_extras
    )
    
    full_content = frontmatter + "\n" + append_wikilinks(content, links)
    
    file_path.write_text(full_content, encoding='utf-8')
    
    verified = file_path.exists() and file_path.stat().st_size > 0
    bytes_written = file_path.stat().st_size if verified else 0
    
    return {
        "path": str(file_path),
        "bytes": bytes_written,
        "verified": verified,
        "frontmatter": frontmatter
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        test_content = sys.argv[1]
    else:
        test_content = "# Test Note\n\nThis is a test."
    
    result = publish_to_obsidian(
        content=test_content,
        title="Test Note from Skill",
        folder="Notes",
        tags=["test", "skill"],
        description="Test publish from publish-to-obsidian skill"
    )
    print(f"Result: {result}")