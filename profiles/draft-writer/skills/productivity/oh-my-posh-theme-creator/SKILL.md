--- 
name: oh-my-posh-theme-creator
version: 1.0.0
author: Hermes Agent
license: MIT
description: |2
 Create and customize Oh My Posh themes.
---

# Oh My Posh Theme Creator

A class-level skill for creating and customizing Oh My Posh themes. Provides procedures for reading, modifying, and creating Oh My Posh theme JSON files with controlled segment layouts, color palettes, powerline symbols, and template strings.

## When to Use

- User asks to "create a new theme based on this one", "change colors", "replace logo", "use arc chars instead of triangles"
- User wants to modify an existing Oh My Posh theme JSON
- User wants to brighten/darken colors, change powerline symbols, or modify segment templates

## Procedure

### Step 1: Read Reference Theme
1. Locate source Oh My Posh theme JSON (e.g., velvet.omp.json)
2. Read with read_file to inspect $schema, blocks, segments
3. Identify segments to modify: background, foreground, template, style, powerline_symbol, leading/trailing diamonds, options
4. Note $schema URL for validation

### Step 2: Identify Modifications
1. Color changes: Replace background/foreground hex. Brighter: add orange/yellow/red. Muted: lower-intensity hex.
2. Powerline symbol: Change from /\ue0b4 to arc chars like 🡠/🡡. Update all segments uniformly.
3. Diamonds: Change leading/trailing diamonds from /\ue0b0 to other unicode.
4. Template: Modify to add/remove arc chars, change folder icons, adjust depth, reposition.
5. Options: Adjust max_depth, home_icon, folder_separator_icon, style (agnoster_short, diamond, powerline).
6. Record each decision point.

### Step 3: Write New Theme JSON
1. Create new JSON with same $schema structure
2. Apply all modifications, keeping layout intact
3. Ensure all required fields present and valid per schema
4. write_file to new path
5. Verify with oh-my-posh print primary

### Step 4: Activate Theme
1. Run eval "$(oh-my-posh init bash --config <path>)"
2. Confirm with oh-my-posh print primary
3. Instruct user to add eval to shell RC

## Pitfalls

- Grep template for ~ before adding arc chars — home icon interacts with arc insertion
- Do not remove powerline_symbol from one segment without updating adjacent segment's diamonds
- Brightening colors can produce low contrast — always verify with oh-my-posh print
- Never edit config.yaml by hand — use oh-my-posh init and eval pattern
- When replacing triangle chars (\ue0b6/\ue0b0) with arc chars (🡠/🡡), update ALL segments consistently
- $schema must match installed oh-my-posh version

## References

### references/ohmyposh-segments.md
Detailed reference of all Oh My Posh segment types and valid values.

### references/ohmyposh-schema.md
Full schema specification from official Oh My Posh repo.

### templates/ohmyposh-sweet-template.json
Starter template with minimal one-segment layout.

## Examples

### Example 1: Brighten OS segment
```json
{...}
```

Brightens background from #9a8830 to #ffb845, replaces triangles with arcs.

### Example 2: Add arc after ~
```json
"template": " \uf07b {{ .Path }} 🡡 ",
```

## Verification

- read_file written JSON, confirm valid
- oh-my-posh print primary --config <path> --plain --pwd <dir> — clean output
- Check segments render without broken powerline chains
- Confirm activates with eval "$(oh-my-posh init bash --config <path>)"
