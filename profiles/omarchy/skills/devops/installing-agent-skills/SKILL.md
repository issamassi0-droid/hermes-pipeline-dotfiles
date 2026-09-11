---
name: installing-agent-skills
description: Use when importing external skill repos into Hermes.
---

# Installing External Agent Skills into Hermes

## Procedure

1. Clone the source repo to /tmp: `git clone --depth 1 <repo> /tmp/<name>-src`.
2. Inspect the layout. Most Agent-Skills repos nest skills as `skills/<skill-name>/SKILL.md` (with optional `references/`, `scripts/`, `assets/` beside it).
3. Hermes only auto-discovers skills at `~/.hermes/skills/<skill-name>/SKILL.md` — one flat directory per skill. Do NOT clone the repo directly into ~/.hermes/skills; a nested clone never registers.
4. Copy each skill out flat:
 ```bash
 for d in <skill1> <skill2>; do
 mkdir -p ~/.hermes/skills/$d
 cp -r /tmp/<name>-src/skills/$d/* ~/.hermes/skills/$d/
 done
 ```
5. Verify each one loads and shows `readiness_status: available`: `skill_view(name="<skill>")`.
6. Clean up /tmp.

Before porting, check Hermes doesn't already ship an equivalent — search `~/.hermes/skills` and `~/.hermes/plugins` for overlapping names.

## CLI prerequisites

A ported skill may require a CLI binary. Check `which <tool>` first; install only what's missing. Use the user's free-tier/open-source preference when choosing a tool.

Pitfall — npm global installs on this machine may succeed without creating the bin symlink: mise-managed Node plus npm v11 sometimes skips it, so `which <tool>` fails after a clean `npm install -g`. Verify, and fix by symlinking the package's declared bin entry:

```bash
PKG=$(npm root -g)/<pkg> # grep package.json "bin" for the entry script
ln -sf $PKG/<bin-entry>.js ~/.local/bin/<tool> && chmod +x ~/.local/bin/<tool>
```

Then verify `which <tool>` and `<tool> --version` before declaring the skill operational.

## Pitfalls

- Check the skill's frontmatter for required commands/env vars — `skill_view` reports `missing_required_commands` and `missing_credential_files` up front; resolve these before telling the user it's active.
- The user may decline an install the first time it is proposed. Do not retry the same command in the same session; note it as a pending prerequisite and let the user run it themselves.
