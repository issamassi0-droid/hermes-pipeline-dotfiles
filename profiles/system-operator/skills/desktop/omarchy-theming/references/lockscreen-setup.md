# Lock Screen and Boot Splash Setup

## Overview

Omarchy uses two layers for the lock screen experience:
- **Plymouth**: boot splash shown during startup before the desktop loads
- **SDDM**: display manager lock screen shown at startup/login

These are independent — update both for a consistent look.

## Plymouth (boot splash)

### Set from theme
```bash
omarchy plymouth set by theme <theme-name>
```
Reads `colors.toml` (`background`, `foreground`) and `unlock.png`.

### Customize a theme's Plymouth

1. Create the plymouth directory:
 ```bash
 mkdir -p ~/.config/omarchy/themes/<name>/plymouth
 ```

2. Copy base files:
 ```bash
 cp /usr/share/omarchy/default/plymouth/* ~/.config/omarchy/themes/<name>/plymouth/
 ```

3. Edit `omarchy.script` — replace `Window.SetBackgroundTopColor`/`BottomColor` with RGB from `colors.toml`:
 - `#141210` → `Window.SetBackgroundTopColor(0.078, 0.071, 0.063);`
 - `#d1c8b0` → `Image.Text(text, 0.820, 0.784, 0.690);`

4. Edit `omarchy.plymouth` to point to the new paths:
 ```
 ImageDir=/home/massi/.config/omarchy/themes/<name>/plymouth
 ScriptFile=/home/massi/.config/omarchy/themes/<name>/plymouth/omarchy.script
 ```

5. Ensure `unlock.png` exists at `$theme_dir/unlock.png`:
 ```bash
 cp /usr/share/omarchy/default/plymouth/lock.png ~/.config/omarchy/themes/<name>/unlock.png
 ```

6. Apply:
 ```bash
 omarchy plymouth set by theme <name>
 ```
 Requires sudo — if no terminal, use `pkexec`.

### Required Plymouth files
- `omarchy.plymouth` — theme descriptor
- `omarchy.script` — Plymouth script (background, logo, lock, entry, progress bar)
- `logo.png` — logo image
- `lock.png` — lock icon (also copied to `unlock.png`)
- `entry.png` — password entry field
- `bullet.png` — password bullet
- `progress_bar.png` — progress bar fill
- `progress_box.png` — progress bar background

## SDDM (lock screen)

### Current theme
```bash
cat /etc/sddm.conf.d/99-omarchy-login.conf
```
Currently `Current=omarchy`.

### Apply japon theme to SDDM

1. Copy the base theme to user config:
 ```bash
 cp -r /usr/share/sddm/themes/omarchy ~/.config/omarchy/themes/japon/sddm/
 ```

2. Update `Main.qml` background color:
 ```bash
 sed -i 's/color: "#1a1b26"/color: "#141210"/g' ~/.config/omarchy/themes/japon/sddm/Main.qml
 ```

3. Update system SDDM theme (requires sudo):
 ```bash
 sudo sed -i 's/color: "#1a1b26"/color: "#141210"/g' /usr/share/sddm/themes/omarchy/Main.qml
 ```

4. Set the SDDM config to use the custom theme:
 ```bash
 sudo tee /etc/sddm.conf.d/99-omarchy-japon.conf > /dev/null <<'EOF'
[Theme]
Current=omarchy-japon

[Users]
RememberLastUser=true
RememberLastSession=true
EOF
 ```

5. Restart SDDM to apply:
 ```bash
 sudo systemctl restart sddm
 ```

### SDDM theme files
- `Main.qml` — QML lock screen UI
- `theme.conf` — theme metadata
- `metadata.desktop` — display name and description
- `logo.png`, `lock.png`, `entry.png`, `bullet.png` — UI assets

## Pitfalls
- **Plymouth needs sudo** — `omarchy plymouth set by theme` writes to `/usr/share/plymouth/themes/`. Use `pkexec` if no terminal is available.
- **unlock.png must exist** — `omarchy-plymouth-set-by-theme` fails if `$theme_dir/unlock.png` is missing. Copy `lock.png` to `unlock.png`.
- **SDDM config is root-owned** — editing `/usr/share/sddm/themes/omarchy/Main.qml` requires `sudo`.
- **Plymouth reads colors.toml** — the `background` and `foreground` hex values from `colors.toml` are used for boot splash colors.
- **Both layers are independent** — Plymouth is the boot splash, SDDM is the lock screen. They don't share config.
