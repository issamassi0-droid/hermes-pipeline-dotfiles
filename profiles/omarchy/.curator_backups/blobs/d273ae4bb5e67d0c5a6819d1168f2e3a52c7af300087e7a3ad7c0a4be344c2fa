---
name: omarchy-theming
description: Create full Omarchy themes — palette, shell, GTK, terminals.
trigger: Use when creating or updating an Omarchy theme — theming Hyprland, Quickshell, GTK, terminals, Tmux, Wofi, VS Code, and the install/hook pipeline.
---

# Omarchy Theming

## Palette-first design
Pick 3 desaturated accent colors before touching any file. The Japon theme uses:
- Darken orange `#c4682a` — primary (borders, active, selected)
- Darken cyan `#3a8a8a` — secondary (menus, accents)
- Darken yellow `#a89030` — tertiary (highlights, numbers)
- Background `#141210`, Foreground `#d1c8b0`, Muted `#7a7060`, Border `#8a7a60`

## Theme directory structure
```
~/.config/omarchy/themes/<name>/
  colors.toml          # single source of truth
  palette.txt          # human-readable palette
  gtk.css              # GTK3/GTK4 Adwaita override
  hyprland.conf        # border/decoration
  shell.toml           # bar, controls, popups, menu, lock, workspace
  shell.controls.toml  # control chrome (normal/hover/focus/selected)
  quickshell/Theme.qml # QtObject color palette for QML
  workspace.qml        # workspace indicator widget
  workspace.manifest.json   # ⚠️ id MUST match the installed plugin dir name
  plugins/<plugin>/     # theme-shipped plugin QML (installed by hook)
  backgrounds/<name>-wallpaper.png
  hooks/<name>-theme-set.sh
  install.sh
  alacritty/alacritty.toml
  kitty/kitty.conf
  foot/foot.ini
  ghostty/ghostty.conf
  tmux/tmux.conf
  wofi.css
  vscode/<name>-color-theme.json
  README.md
```

## File creation order
1. `colors.toml` + `palette.txt` — define the palette
2. `shell.toml` + `shell.controls.toml` — shell surfaces
3. `hyprland.conf` — border/blur/decoration + wallpaper (swaybg)
4. `gtk.css` — GTK color variables
5. `quickshell/Theme.qml` — QtObject with all colors
6. `quickshell/<name>/shell.qml` — bar UI theming
7. `workspace.qml` + `workspace.manifest.json` — workspace indicators
8. Terminal configs (alacritty, kitty, foot, ghostty)
9. `tmux.conf`, `wofi.css`, VS Code theme
10. `backgrounds/<name>-wallpaper.png` — matching wallpaper (see references/wallpaper-generation.md)
11. `hooks/<name>-theme-set.sh` — apply hyprland borders + reload quickshell
12. `install.sh` — clone check, hook install, `omarchy theme set <name>`
13. `README.md`

## Key patterns

### colors.toml
- `background`, `foreground`, `selection_foreground`, `selection_background`
- `accent`, `cursor`
- ANSI palette color0-color15
- Surfaces: surface0 (darkest), surface1, surface2, surface3
- `border`, `border_alpha`, `text_primary`, `text_secondary`, `icon`

### shell.toml
- [bar], [hyprland], [controls], [spacing], [font], [popups], [tooltip], [notifications], [launcher], [menu], [polkit], [lock], [image-picker], [workspace]
- ⚠️ No duplicate section headers — TOML rejects `[hyprland]` twice

### hyprland.conf
- `col.active_border = rgba(<hex>ff)` — full opacity accent
- `col.inactive_border = rgba(<hex>55)` — semi-transparent
- `rounding = 0` for sharp 90s minimal
- `exec-once = swaybg -i ~/.config/omarchy/themes/<name>/backgrounds/<name>-wallpaper.png -m fill` — set wallpaper (swaybg must be installed; `pacman -S swaybg`)

### quickshell/Theme.qml
- QtObject with `readonly property color` for each token
- Include `property color orange/cyan/yellow` for the 3 accents

### quickshell/<name>/shell.qml
- Bar UI widget: `ApplicationWindow` with transparent background
- Use theme colors for `Rectangle` fills, `Text` colors
- Include workspace indicators (Repeater model), clock Text with Timer
- Path: `~/.config/quickshell/<name>/shell.qml`
- Hyprland bind: `bind = SUPER, space, exec, quickshell -p ~/.config/quickshell/<name>/shell.qml`

### workspace.qml
- Rectangle with `property int workspaceNum`, `property bool active`
- Active uses accent color, inactive uses surface1

### hooks/<name>-theme-set.sh
- `hyprctl keyword general:col.active_border "rgba(<hex>ff)"`
- `hyprctl keyword general:col.inactive_border "rgba(<hex>55)"`
- Install theme-shipped plugins: copy `plugins/<plugin>/` into `~/.config/omarchy/plugins/<plugin>/`, then `omarchy-shell shell rescanPlugins` + `omarchy plugin enable <id>`
- Wire the bar in `~/.config/omarchy/shell.json`: left = `[{id: omarchy.menu}, {id: omarchy.spacer}]`, workspace plugin in center
- Reload quickshell if running
- Finish with `omarchy restart shell` — rescan alone does not re-render the bar

### Bar widgets via plugins (not the theme dir alone)
A theme's `workspace.qml` does nothing until installed as a plugin. Workflow:
1. Copy QML + manifest into `~/.config/omarchy/plugins/<dir>/` (dir name = manifest `id`)
2. `omarchy-shell shell rescanPlugins`
3. `omarchy plugin enable <id>`
4. Reference `<id>` in `shell.json` bar layout
5. `omarchy restart shell`

### install.sh
- Validates theme dir exists
- Copies hook to `~/.config/omarchy/hooks/theme-set.d/`
- Runs `omarchy theme set <name>`

## Git setup for GitHub
```bash
cd ~/.config/omarchy/themes/<name>
git init
git add -A
git commit -m "Initial <name> theme"
gh repo create <user>/omarchy-<name> --public --source=. --push
```

## Plymouth (boot splash) and SDDM (lock screen)

Omarchy uses Plymouth for the boot splash and SDDM for the lock screen shown at startup.

### Plymouth (boot splash)

Set the boot theme from an Omarchy theme:
```bash
omarchy plymouth set by theme <theme-name>
```
This reads `colors.toml` (`background`, `foreground`) and `unlock.png` from the theme dir.

Customize the Plymouth script for a theme:
1. Create `~/.config/omarchy/themes/<name>/plymouth/`
2. Copy `/usr/share/omarchy/default/plymouth/*` into it
3. Edit `omarchy.script` — set `Window.SetBackgroundTopColor`/`BottomColor` to RGB(0.xxx, 0.xxx, 0.xxx) from `colors.toml`
4. Edit `omarchy.plymouth` to point `ScriptFile` and `ImageDir` to the new paths
5. Apply: `omarchy plymouth set by theme <name>` (requires passwordless sudo or `pkexec`)

**Plymouth file locations:**
- User theme plymouth: `~/.config/omarchy/themes/<name>/plymouth/`
- System Plymouth: `/usr/share/plymouth/themes/omarchy/` (root-owned — do not edit directly)
- Required files: `omarchy.plymouth`, `omarchy.script`, `logo.png`, `lock.png`, `entry.png`, `bullet.png`, `progress_bar.png`, `progress_box.png`

### SDDM (lock screen at startup)

SDDM is the display manager (`systemctl status sddm`). Its theme config is in `/etc/sddm.conf.d/`.

Customize the SDDM lock screen:
1. Copy the existing theme: `cp -r /usr/share/sddm/themes/omarchy ~/.config/omarchy/themes/<name>/sddm/`
2. Edit `Main.qml` — change `color: "#1a1b26"` to the theme background hex
3. Update `/etc/sddm.conf.d/99-omarchy-login.conf` — set `Current=omarchy` (or `omarchy-japon` for a custom theme)
4. Apply system changes requires sudo: `sudo sed -i 's/color: "#1a1b26"/color: "#141210"/g' /usr/share/sddm/themes/omarchy/Main.qml`

**SDDM theme files:** `/usr/share/sddm/themes/omarchy/` — `Main.qml`, `theme.conf`, `metadata.desktop`, `logo.png`, `lock.png`, `entry.png`, `bullet.png`

### Reference
See `references/lockscreen-setup.md` for the full step-by-step recipe.

## Pitfalls
- **TOML duplicate sections**: `shell.toml` must not have `[hyprland]` twice — merge into one section (the pop theme has this bug; avoid it)
- **QML file extensions**: `.qml` files need valid Qt syntax; `pragma Singleton` + `QtObject` for Theme.qml
- **Git identity**: set `user.email` and `user.name` before first commit, or git will fail
- **Quickshell config dir**: `~/.config/quickshell/` may not exist; create `<name>/shell.qml` subdir manually
- **omarchy theme set**: validates theme dir has `.git` or files; hook install is separate from theme apply
- **Palette consistency**: colors.toml, gtk.css, Theme.qml, and all terminal configs must use the same hex values — mismatch causes visual seams
- **Wallpaper not showing**: `swaybg` must be installed (`pacman -S swaybg`); the `exec-once` line in hyprland.conf sets it; verify with `hyprctl clients` after reload
- **Hyprland border override war**: a user `~/.config/hypr/looknfeel.lua` (or hyprland.lua) `general` block overrides theme borders on every `hyprctl reload` — a theme-set hook's `hyprctl keyword` gets clobbered. Persist the palette there too (set both the hook keyword for immediacy and the lua values for persistence).
- **Installed theme = code is stripped**: `omarchy theme set` stages a `.git`-bearing user theme but denies `alacritty.toml/foot.ini/ghostty.conf/kitty.conf/vscode.json/*.lua` (security policy). This breaks scripts that call `quickshell -r` (arg doesn't exist — just skip reload) and copies the hook into `~/.local/state/omarchy/current/theme/hooks/`. Fix bugs in the source theme dir, not the staged copy.
- **Theme-shipped plugin QML beats global**: the global `~/.config/omarchy/plugins/pop.workspace/` can drift from the theme palette. Ship `plugins/pop.workspace/` in the theme dir, have the hook copy it over, `omarchy plugin enable <id>`, swap `omarchy.workspaces` → the plugin id in `shell.json` bar layout, then `omarchy restart shell` (rescan alone doesn't re-render).
- **Quickshell shell.qml not loading**: the `-p` flag points to the shell.qml path; if the file or dir is missing, quickshell falls back to default — create `~/.config/quickshell/<name>/shell.qml` manually
- **Hook reloads quickshell**: the theme-set hook must restart quickshell (`quickshell -r`) or the new Theme.qml colors won't apply until next launch
- **Plugin manifest `id` must equal the plugin directory name AND the id referenced in `shell.json`** — a renamed id makes the widget silently never render (`omarchy plugin list` shows it but the bar layout resolves to nothing). Grep all three for the same string before restarting the shell.
- **Plugin enable requires rescan first**: a freshly copied plugin dir is unknown to `omarchy plugin enable` until `omarchy-shell shell rescanPlugins` runs; run rescan → enable → restart shell in that order.
- **Theme plugins dir is dead weight without the hook**: QML under `themes/<name>/plugins/` must be copied to `~/.config/omarchy/plugins/` by the theme-set hook or install.sh — nothing loads it from the theme dir.
- **Pillow for wallpaper generation**: PEP 668 blocks system pip and `uv pip install` refuses outside a venv — use `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install Pillow`, then run scripts with `/tmp/venv/bin/python3`.
- **Wallpaper generation**: see `references/wallpaper-generation.md` for the Pillow recipe and composition rules