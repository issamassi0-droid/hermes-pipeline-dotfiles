# InkMode Shader Parameters — Reference

Plugin: `~/.config/omarchy/plugins/jinxnet.inkmode/`
Modes: normal, p3, srgb, wide, neo16, color-ink, ink

## Mode Matrix

| Mode | Shader | Matrix (RGB→XYZ) | Contrast | Gamma | Notes |
|------|--------|-------------------|----------|-------|-------|
| P3 | `p3.frag` | DCI-P3 primaries (D65) | 0.92 | 2.2 | Wide gamut, print-like |
| sRGB | `srgb.frag` | BT.709 primaries (D65) | 0.95 | 2.2 | Standard faithful |
| Wide | `wide.frag` | Adobe-like primaries (D65) | 0.88 | 2.2 | Warm desaturation |
| Neo16 | `neo16.frag` | Custom warm primaries | 0.86 | 2.0 | Low contrast, night |
| Color Ink | `color-ink.frag` | N/A (saturation mix) | 0.90 | N/A | SATURATION=0.45 |
| Ink | `ink.frag` | N/A (grayscale) | 0.88 | N/A | WARM tint |

## Shader Tuning Primitives

### Full sRGB linearization (p3/srgb/wide/neo16 shaders)
All four wide-gamut shaders use proper gamma 2.4 SRGB curve:
```glsl
vec3 srgbToLinear(vec3 c) {
    return mix(c / 12.92, pow((c + 0.055) / 1.055, vec3(2.4)), step(0.04045, c));
}
vec3 linearToSrgb(vec3 c) {
    return mix(c * 12.92, pow(clamp(c, 0.0, 1.0), vec3(1.0 / 2.4)) * 1.055 - 0.055, step(0.0031308, c));
}
```
Apply before matrix: `lin = srgbToLinear(pix.rgb)`, apply after: `color = linearToSrgb(color)`.

### 3×3 RGB matrix (wide-gamut shaders)
Baked from ICC profile primaries via XYZ intermediate:
```glsl
const mat3 M = mat3(
    <row0>,
    <row1>,
    <row2>
);
vec3 color = M * lin;
```
Construct: primaries → XYZ matrix → invert → scale white to (1,1,1) → transpose for GLSL column-major.

### Contrast
```glsl
color = (color - 0.5) * CONTRAST + 0.5;
```
Applied after matrix, before gamma revert. Range 0.80–0.95.

## ICC Profile Note

The profiles in `~/Documents/` are minimal wrappers (464–480 bytes, "saws/ctrl model by hand").
ImageMagick reports sRGB primaries for all three `.icc` files — they carry no real colorimetric data.
The Neo16 `.icm` (9880 bytes) is a real ICC with actual tag data.
Hyprland screen shaders expose only `sampler2D tex` — no extra textures for 3D LUTs, so matrix baking is the only viable approach.

## Cycle Script

`cycle.sh` manages mode switching and state file at `~/.local/state/omarchy/inkMode`.
Commands: `cycle`, `status`, `desired`, `restore`, `normal`, `p3`, `srgb`, `wide`, `neo16`, `color-ink`, `ink`, `--quiet`.

## Apply Changes

Edit the `.frag` file, then cycle off/on or run `omarchy-ctl restart`.
The state file preserves the last mode across login/theme changes.
