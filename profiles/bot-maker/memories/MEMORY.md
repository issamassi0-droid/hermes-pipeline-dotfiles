User prefers to install LLM proxies in ~/.local/share/llm-proxy for persistence, and wants explicit steps for adding provider API keys via the proxy's API after admin account creation. User also pushes modified Omarchy plugins to personal GitHub repos (issamassi0-droid).
§
User prefers a muted, low-saturation color palette for both Hermes skins and bash prompt. Uses orange, muted yellow, muted sage green, gray, purple — warm but dimmed colors. Prefers dark gray text on muted yellow background for highlighted prompt segments.
§
User prefers InkMode Vibrance shader with VIBRANCE 0.65, GAMMA 1.18, CONTRAST 0.80, red scale 0.95, green 1.04, blue 0.92.
§
Omarchy rice: plugins in ~/.config/omarchy/plugins/ (each its own git repo); changes apply after `omarchy restart shell`. GitHub repos pushed via `gh repo create --public --source=. --push` (user approves). Forks pushed: omarchy-googletranslate, omarchy-expose, omarchy-ink-mode. Created themes: pop → japon → japon_pop_ws → japon-matte (matte variant: orange #b87030, yellow #9a8830, green #4a8878; bg #141210/fg #d1c8b0 unchanged). QML pitfalls: border+fill same alpha = invisible border; omarchy.* IDs reserved (use jp.*); all bar widgets need implicitHeight: root.barSize for alignment.
§
User rices bash PS1 iteratively: one-line chip-style. Edits via python3 heredoc (patch tool escape-drifts on PS1). Uses synth-shell alongside custom PS1; disabled greeter (bc missing).
§
User uses Obsidian vault at /home/massi/ObsidianVault/. Uses obsidian_second_brain skill to log sessions — writes to /home/massi/ObsidianVault/Logs/. Logs follow structured format: YAML frontmatter, > [!ABSTRACT] callout, headers, code blocks, wikilinks.
§
Skill curation: user shares GitHub agent-skill repos to check/install into ~/.hermes/skills. Installed: kepano obsidian-skills (5), defuddle CLI v0.19.3 (~/.local/bin), aaron SEO/GEO 16-skill bundle (~/.agents symlinks), aihero suite (teach, grill*, handoff). Gotchas: npx-skills installs create byte-identical `skills-`-prefixed mirrors that break bare-name skill_view — delete mirrors, keep originals; npm -g under mise skips bin symlinks — manually link into ~/.local/bin.
- Processed task for api_security_auditor
- Processed task for sqlite_fts_vector_engine
- Processed task for android_kernel_root_tuner
- Processed task for pandas_data_pipeline_engine