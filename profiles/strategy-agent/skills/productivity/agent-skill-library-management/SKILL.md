---
name: agent-skill-library-management
description: Use when checking, installing, or cleaning up agent skills.
---

# Agent Skill Library Management

Install, verify, and clean up third-party agent skills under `~/.hermes/skills/`.

## Check if already installed (do this FIRST — most requests are already satisfied)

1. List matching skill dirs: `ls /home/massi/.hermes/skills/ | grep -i <keyword>`. Also check `~/.agents/skills/` — cross-runtime installs land there as real dirs with symlinks into `~/.hermes/skills/`.
2. Confirm content loads: `skill_view(name)`. Treat `readiness_status: available` as proof.
3. Compare against the repo's README/skill list (web_extract) before concluding anything is missing. Answer with a per-skill table rather than a bare yes/no.

## Install paths, by source

- **Git repo with nested `skills/<name>/` layout** (e.g. kepano/obsidian-skills): flat clone will NOT register — Hermes expects each skill as a direct subdir with its own `SKILL.md`. Copy each inner skill dir up: `cp -r repo/skills/<name> /home/massi/.hermes/skills/<name>/`.
- **`npx skills add <owner>/<repo>`**: installs into `~/.agents/skills/` with symlinks into `~/.hermes/skills/`. Works, but leaves byte-identical `skills-<name>` mirror dirs — see dedupe below.
- **`npm install -g <cli>` for a skill's CLI dependency**: on the mise-managed node, verify the bin actually landed on PATH afterward; fall back to a manual symlink (see npm pitfall below).

## Dedupe `skills-*` mirrors

`npx skills` installs create a `skills-<category>-<name>` mirror copy alongside the categorized original. These are byte-identical duplicates that make bare-name `skill_view` lookups fail with "Ambiguous skill name".

- Only delete a `skills-*` dir after `diff -rq` proves it identical to its unprefixed counterpart; delete the MIRROR, keep the original.
- After cleanup, re-verify with `skill_view("<bare-name>")` resolving to exactly one match.

## npm/mise bin symlink pitfall

`npm install -g` under a mise-managed node installs the package into `~/.local/share/mise/installs/node/<ver>/lib/node_modules/<pkg>/` but may not create the PATH symlink.

- Locate the real bin from the package's `package.json` `bin` field, then `ln -sf <path-to-cli.js> ~/.local/bin/<name>` and `chmod +x`. Verify with `which <name> && <name> --version`.

## Restructure a multi-section skill into standalone skills

A downloaded skill bundle often ships as one `SKILL.md` with a router table pointing to sections, plus shared `references/`, `templates/`, `scripts/` dirs. If the user wants each section as its own activatable skill, split rather than keeping the monolith.

1. Create one dir per section under `~/.hermes/skills/<section-name>/`. Use a short, lowercase, hyphenated name — not the original bundle name.
2. Copy each section's owned files into the new dir: the section's prose becomes its `SKILL.md` (with its own YAML frontmatter `name` + `description`), and only the `references/` / `templates/` / `scripts/` files it actually uses come along. Shared files (e.g. a troubleshooting playbook used by only one section) go to that section's dir, not duplicated.
3. Write a fresh `SKILL.md` per section: frontmatter first, then the section's full prose (router, SOP, execution rules, output format) copied from the monolith and stripped of cross-section references. End with a `## Bundled files` tree listing only that section's files.
4. Delete the original monolith dir (or archive it out of `~/.hermes/skills/`) so the bare section names don't collide with a leftover parent.
5. Verify each new skill loads: `skill_view("<section-name>")` → `readiness_status: available`.

**Pitfall:** a download unpacked with brace expansion that never ran (e.g. `{references,templates,scripts}`) leaves a literal directory named `{references,templates,scripts}` — `rmdir` it; it's an empty artifact, not a real dir.

## Verification gate

Before reporting an install done: `skill_view` every installed skill and state the readiness status. A skill dir that exists but fails to load is not installed.
