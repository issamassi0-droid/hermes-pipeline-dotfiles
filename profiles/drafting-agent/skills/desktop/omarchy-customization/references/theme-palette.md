# Theme Color Palette — mapping pattern

## palette.txt (single source of truth)

Flat token definitions, ordered dark → light, with RGB comments:

```
base = #141210 # (20,18,16) background / darkest
surface = #1e1c18 # (30,28,24) panels, menus
surface2= #2a2620 # (42,38,32) elevated, borders
muted = #7a7060 # (122,112,96) dimmed foreground
border = #8a7a60 # (138,122,96) hairline borders
text = #d1c8b0 # (209,200,176) foreground / lightest

# Accents
orange = #b87030 # (184,112,48) muted orange
cyan = #4a8878 # (74,136,120) slightly matte green
yellow = #9a8830 # (154,136,48) matte yellow
```

## colors.toml — mapping palette tokens to Omarchy keys

Each accent appears in 3 places: `accent`, `color1/color9` (ANSI red), and the shell.toml `active`/`border` values. When changing a palette token, update all three locations plus every file that hardcodes the hex value (gtk.css, wofi.css, terminal configs, QML).

## QML color values

QML files in the theme (workspace.qml, quickshell/Theme.qml) hardcode the accent hex as `Qt.rgba(r/255, g/255, b/255, alpha)`. Convert hex → rgba:

```python
# #b87030 → Qt.rgba(184/255, 112/255, 48/255, alpha)
```

## Verification

After editing: `omarchy theme set <name>` then `omarchy restart shell`.
Check no old palette tokens leak via: `grep -rn '#c4682a\|#3a8a8a\|#a89030' .` (should return nothing except README comparison notes).