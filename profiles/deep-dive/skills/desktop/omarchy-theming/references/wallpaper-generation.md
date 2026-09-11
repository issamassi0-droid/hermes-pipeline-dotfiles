# Wallpaper Generation — Minimal 90s Japanese Style

## Recipe (Pillow, Python)

```python
from PIL import Image, ImageDraw

# Palette — use theme colors
bg      = (20, 18, 16)       # #141210
orange  = (196, 104, 42)     # #c4682a
cyan    = (58, 138, 138)     # #3a8a8a
yellow  = (168, 144, 48)     # #a89030
muted   = (122, 112, 96)     # #7a7060
surface = (30, 28, 24)       # #1e1c18
fg      = (209, 200, 176)    # #d1c8b0

W, H = 1920, 1080
img = Image.new("RGB", (W, H), bg)
draw = ImageDraw.Draw(img)

# Elements (minimal composition):
# 1. Off-center circle (sun motif — Japanese flag reference)
cx, cy, r = 1480, 380, 180
draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=surface, outline=orange, width=3)

# 2. Horizontal rules
draw.rectangle([60, 140, 300, 143], fill=orange)   # top
draw.rectangle([60, 940, 400, 943], fill=cyan)      # bottom

# 3. Vertical accent left
draw.rectangle([57, 160, 60, 880], fill=yellow)

# 4. Grid squares bottom-right (2a2620 / cyan alternating)
grid_x, grid_y, cell = 1460, 780, 24
for row in range(3):
    for col in range(3):
        x = grid_x + col * (cell + 4)
        y = grid_y + row * (cell + 4)
        fill = orange if (row + col) % 2 == 0 else cyan
        draw.rectangle([x, y, x + cell, y + cell], fill=fill)

# 5. Horizontal line center-left (wabi-sabi balance)
draw.rectangle([80, 540, 500, 542], fill=muted)

# 6. Enso-style circle bottom-left
draw.ellipse([70, 880, 120, 930], outline=yellow, width=2)

# 7. Accent dot near circle
draw.ellipse([cx + r + 30, cy - 20, cx + r + 38, cy - 12], fill=fg)

# 8. Diagonal accent
draw.line([1700, 80, 1900, 260], fill=cyan, width=1)

img.save("~/.config/omarchy/themes/<name>/backgrounds/<name>-wallpaper.png")
```

## Design principles
- 3-5 visual elements max — whitespace is the design
- Use accent colors sparingly (one orange, one cyan, one yellow element)
- Off-center composition — avoid centering the main shape
- Thin lines (1-3px) — thick lines feel modern, not 90s minimal
- Grid/square patterns for texture without noise

## Requirements
- Python Pillow: `python3 -m venv /tmp/venv && /tmp/venv/bin/pip install Pillow`
- Output: PNG, 1920x1080 (or match monitor resolution)

## Setting the wallpaper
- `swaybg -i <path> -m fill` (install via `pacman -S swaybg`)
- Add to hyprland.conf: `exec-once = swaybg -i <path> -m fill`
- Alternatives: `swww`, `hyprpaper`, `feh` (swaybg is the standard for Hyprland)

## Pitfalls
- Pillow not installed by default — use venv, not --system (system Python is PEP 668 blocked)
- Image dimensions must match monitor resolution or Hyprland stretches/crops
- If wallpaper doesn't appear on reload: `killall swaybg && swaybg -i <path> -m fill`