# Marketplace Listing — Bevel Modifier Presets

## Short Description (160 chars)
Save your tuned Bevel modifier parameters as a named preset and recall them on any Bevel modifier in any .blend file. Uses Blender's built-in preset system.

## Long Description

The Bevel modifier has no built-in preset system. Hard-surface modelers tune the same parameter combinations across projects — Offset Type, Width, Segments, Limit Method, Angle, Profile, Shading flags — and have no way to save those setups for reuse in another file.

**How it works:**
- Add a **Bevel Presets** panel to the Properties Editor's Modifier tab, visible whenever the active modifier is a Bevel
- **[+]** saves all 22 writable Bevel modifier properties as a named preset
- The dropdown lists every saved preset; selecting one applies it to the active Bevel modifier
- **[-]** removes the selected preset

Presets are stored in Blender's standard preset directory — the same place Render and Cycles presets live — so they persist across .blend files and across Blender restarts.

## Features

- Save and recall the full Bevel modifier parameter set (22 properties on Blender 4.2 LTS)
- Lives in the Properties Editor's Modifier tab, only visible when a Bevel modifier is active
- Uses Blender's built-in `AddPresetBase` infrastructure — no new UI patterns to learn
- Presets persist across .blend files and across Blender restarts

## Requirements

- Blender 4.2 LTS or later (validated baseline)

## Tags

modifier, bevel, preset, hard-surface, workflow, modeling
