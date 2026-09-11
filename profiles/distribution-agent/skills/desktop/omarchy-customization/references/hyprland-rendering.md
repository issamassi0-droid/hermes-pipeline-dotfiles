# Hyprland Rendering & Display Smoothness

Applies to: Hyprland v0.56.2 on DRM backend, NVIDIA RTX 2060 + AMD Renoir iGPU.

## rendering.lua — placement and contents

File: `~/.config/hypr/rendering.lua` (loaded via `require("hypr.rendering")` in `hyprland.lua`)

Supported in v0.56.2:
- `misc.vrr` — 0 off, 1 on (if monitor supports VRR)
- `misc.disable_hyprland_logo`, `misc.disable_splash_rendering`, `misc.animate_manual_resizes`
- `hl.exec_once()` for nvidia-settings composition pipeline

NOT supported in v0.56.2: `vsync`, `mouse_move_enhanced` keywords.

## NVIDIA tear-free fix

```bash
nvidia-settings --assign CurrentMetaMode='nvidia-auto-select +0+0 { ForceFullCompositionPipeline = On }'
```
Persists via xconfig. Verify: `nvidia-settings --query CurrentMetaMode`.

## After editing

```bash
hyprctl reload
hyprctl monitors # confirm no errors
hyprctl clients # confirm windows still mapped
```

## Free smoothing packages

- `libva-mesa-driver` — VA-API hardware video decode
- `gamemode` — auto GPU/CPU optimization
