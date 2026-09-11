# Hybrid GPU: NVIDIA + AMD

Applies to: NVIDIA RTX 2060 (discrete, PCI vendor 0x10de) + AMD Renoir iGPU (internal display driver, PCI vendor 0x1002, card1-eDP-1).

## Layout

| GPU | Role | Vendor | DRM card |
|-----|------|--------|----------|
| AMD Renoir | Internal display (panel) | 0x1002 | card1 (eDP-1 connected) |
| NVIDIA RTX 2060 | Discrete (unused for display) | 0x10de | card0 (eDP-2 disconnected) |

Detect the active display GPU:
```bash
for card in /sys/class/drm/card*-eDP-*; do
    [ "$(cat "$card/status" 2>/dev/null)" = "connected" ] && echo "$(basename "$card")"
done
```

## Vulkan ICD Switching

**`~/.local/bin/vk-switch`** — toggle Vulkan between AMD and NVIDIA:
```bash
source ~/.local/bin/vk-switch amd     # AMD radeon Vulkan (default, low power)
source ~/.local/bin/vk-switch nvidia   # NVIDIA Vulkan (performance)
~/.local/bin/vk-switch status          # show current GPU + ICD
```

**`~/.local/bin/chromium-vk`** — launch Chromium with the selected ICD:
```bash
source ~/.local/bin/chromium-vk amd     # Chromium on AMD Vulkan
source ~/.local/bin/chromium-vk nvidia  # Chromium on NVIDIA Vulkan
```

Default Vulkan ICD is AMD, exported in `~/.bashrc`:
```bash
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/radeon_icd.json
```

## Chromium Flags

`~/.config/chromium-flags.conf` contains the stable flags:
```
--ozone-platform=wayland
--ozone-platform-hint=wayland
--enable-vulkan
--use-gl=angle
--use-angle=gl
--ignore-gpu-blocklist
--disable-accelerated-video-decode
--disable-accelerated-video-encode
--disable-gpu-driver-bug-workarounds
```

### AMD Vulkan (default)
Native AMD Vulkan via `--enable-vulkan` + default `VK_ICD_FILENAMES`. No special flags needed — Chromium picks up the AMD ICD automatically.

### NVIDIA Vulkan
Works natively too. The AMD default in `~/.bashrc` means Chromium uses AMD unless `vk-switch nvidia` is sourced first.

### SwiftShader Vulkan (software)
`--use-vulkan=swiftshader --use-angle=swiftshader-webgl` forces software rendering. Works reliably on both GPUs but **high CPU** — all rendering goes through the CPU. Use only for debugging flickering; not as a daily driver.

## Pitfalls

- **SwiftShader = high CPU.** It renders everything on the CPU. `--use-vulkan=swiftshader` eliminates flickering but makes the system sluggish. Remove these flags when GPU Vulkan is stable.
- **Hybrid flickering** is usually transient driver-state, not GPU-specific. Both NVIDIA and AMD Vulkan work — pick whichever suits your task.
- **`~/.bashrc` defaults to AMD.** If you want NVIDIA for a session, `source ~/.local/bin/vk-switch nvidia` before launching Chromium.
- **Do NOT add `--disable-gpu-sandbox`** to Chromium flags — Chromium warns about security/stability. It is unnecessary with the other flags.
- **`libva-mesa-driver`** provides VA-API hardware decode on AMD; keep it installed even when using NVIDIA for GL/Vulkan.
