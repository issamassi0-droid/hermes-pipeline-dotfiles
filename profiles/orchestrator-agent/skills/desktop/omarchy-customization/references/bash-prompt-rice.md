# Bash prompt rice — current design (2026-09)

One-line PS1 in `~/.bashrc`. Chip-style backgrounds like a Yazi selected item.

## Prompt structure

```
[bg #ceb023] user@host [/bg] | [bg dimmed-orange] ~/path [/bg] git-branch $
```

- `user@host`: bold black text on bright yellow `#ceb023`
 (truecolor `48;2;206;176;35`), spaces INSIDE the background on both sides.
- Plain `|` separator (no background) between host and path.
- Directory (`\w`): bold black on dimmed orange `48;2;160;90;30`, leading
 space inside the background, no trailing space (the `|` separates).
- Git branch: soft purple. `$`: muted yellow (256-color 143).
- Color variables live at the top of `~/.bashrc`; GREEN is muted
 sage/olive (256-color 100–108 range).

## User preferences learned through iteration

- Rejected rounded corners via `╭╮` glyphs — terminals can't do true rounded
 corners in a single-line prompt; don't retry glyph hacks.
- Rejected too-dark greens (22, 64 look olive/muddy). Sage (108) or olive
 (100) are accepted.
- Rejected a dark `DIM` dollar sign — muted yellow (143) is the current pick.
- "Reduce alpha / glow effect" on a truecolor background = multiply the RGB
 channels toward the dark terminal bg. ~50% was too dim, ~80% accepted.
- Spaces padding a background chip must be INSIDE the color escape sequence
 so they render as part of the chip.

## Editing pitfalls

1. **`patch` tool escape-drift**: PS1 lines contain `\u`, `\h`, `\$`; the
 tool's JSON escaping doubles backslashes on match and refuses the edit.
 Do NOT use `patch` on the PS1 line — use a python3 file rewrite:
 ```python
 with open('/home/massi/.bashrc') as f: c = f.read()
 c = c.replace('old', 'new')
 with open('/home/massi/.bashrc', 'w') as f: f.write(c)
 ```
2. **`sed` eats backslashes** in the replacement when the pattern has `\$`.
 Verify every edit with: `grep 'PS1=' ~/.bashrc | grep -v '^#'`.
3. Colors use 256-palette (`38;5;N`) for text, truecolor (`48;2;R;G;B`)
 when an exact hex matters (e.g. `#ceb023` → `48;2;206;176;35`).
4. After every change, tell the user to run `source ~/.bashrc`.
