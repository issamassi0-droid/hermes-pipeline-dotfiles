---
name: hyprland-screen-shaders
description: 'Use when editing Hyprland screen shaders and mode pipelines.'
---

Use when developing or tuning Hyprland screen shaders and Omarchy-style plugin mode pipelines.

## Workflow
1. Inspect the plugin structure first: `shaders/*.frag`, `InkModel.js` or equivalent mode registry, `cycle.sh` or mode-switch script, and `Service.qml` / IPC validation.
2. Add the new shader file with clearly named `const` knobs at the top: `VIBRANCE`, `GAMMA`, `CONTRAST`, plus any per-channel tweaks.
3. Update the mode registry/model to normalize, detect, label, describe, and cycle the new mode.
4. Update the shell/script layer to parse, validate, apply, and restore the new mode.
5. Update IPC/service validation checks to accept the new mode string.
6. Test by cycling through all modes and verifying the new mode appears between its neighbors.

## GLSL Parameter Cheat Sheet
- `GAMMA < 1.0` brightens midtones; `GAMMA > 1.0` darkens midtones.
- `VIBRANCE` (or saturation mix) at `1.0` = unchanged; lower = more muted.
- `CONTRAST` at `1.0` = unchanged; lower = softer curves.
- Per-channel tweaks go AFTER contrast/gamma, in a single multiply with smoothstep-based blending.
- **Clamp exactly once, at the end**, after all color math and before gamma. Intermediate clamping causes white-layer artifacts.

## Common Pitfalls
- **White layer / halo**: caused by intermediate `clamp()` or by gamma pushing values above 1.0 before the final clamp. Fix by removing early clamps and doing one final clamp.
- **Shader not applying**: Hyprland may not repaint until the next damaged frame. Call `hl.dsp.force_renderer_reload()` after setting the shader.
- **Mode not persisting**: ensure the mode string is accepted in ALL validation checks (model, script case statement, IPC handler).
- **Green/yellow tint too strong**: reduce the green scale factor or tighten the smoothstep range so the tint only affects darker pixels.

## Iterative Tuning Pattern
When the user requests numeric changes, update only the requested constant(s) and keep all other knobs stable. Typical sequence:
1. Brightness → adjust `GAMMA`.
2. Saturation → adjust `VIBRANCE`.
3. Softness → adjust `CONTRAST`.
4. Color cast → adjust per-channel mix vector.
5. If a white layer appears, refactor to single-pass with single final clamp.

## File References
- `references/glsl-parameter-cheatsheet.md` — quick reference for gamma, vibrance, contrast, and clamping patterns.
- `references/inkmode-plugin-map.md` — concrete example of mode pipeline files and their roles.
