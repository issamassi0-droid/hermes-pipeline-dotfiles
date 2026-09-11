# Ink Mode Plugin Structure Map

## Files and Roles
- `shaders/*.frag` — GLSL screen shaders, one per mode
- `InkModel.js` — JavaScript mode registry used by QML
  - `normalize(mode)` — whitelist valid modes
  - `fromHyprctl(output)` — parse hyprctl output to mode name
  - `nextMode(mode)` — cycle order
  - `label(mode)` — human-readable name
  - `description(mode)` — tooltip/description text
- `cycle.sh` — CLI/script interface
  - `mode_from_hypr()` — parse hyprctl JSON
  - `read_desired()` / `write_desired()` — persist mode to state file
  - `apply()` — case statement applying each mode
  - `next_mode()` — cycle order for CLI
  - `set_shader()` — calls hyprctl and forces reload
- `Service.qml` — QML service for IPC
  - `desiredProbe` — reads saved mode on startup
  - `diskProbe` — detects desync between saved and live mode
  - `statusProbe` — polls current live mode
  - Validation checks must accept all mode strings
- `BarWidget.qml` — bar icon widget (usually no mode-list changes needed)
- `manifest.json` — plugin metadata, bump version on new mode
- `README.md` — user-facing docs with mode table

## Mode Ordering Convention
Place new modes between existing ones in the cycle:
`normal → lighten → [new mode] → color-ink → ink → normal`

## Adding a New Mode Checklist
1. Create `shaders/newmode.frag`
2. Add mode to `InkModel.js` normalize/fromHyprctl/nextMode/label/description
3. Add mode to `cycle.sh` variable, parse, case, next_mode, usage
4. Add mode to `Service.qml` validation checks (2 places)
5. Update `manifest.json` version
6. Update `README.md` mode table and cycle description
