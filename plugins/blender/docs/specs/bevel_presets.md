# Plugin Spec: Bevel Modifier Presets

## Problem Statement

The Bevel modifier has no built-in preset system. Hard-surface modelers tune the same
parameter combinations repeatedly across projects — Width Type, Width, Segments, Limit
Method, Angle/Weight thresholds, Custom Profile shape, Shading — and have no way to
save those tuned setups for reuse in another .blend file.

Existing alternatives are either clunky free addons (parameter dumps, no UI integration)
or polished paid addons. RCS request "Saving Bevel Custom Presets" has 67 net votes and
10 replies; the surrounding workflow is well-understood and the gap is real in Blender 5.1.

This addon adds a named preset system for Bevel modifier configurations, persisted in the
user config directory so presets travel between .blend files without import/export rituals.

## Proposed Solution

A small operator + preset menu that mirrors Blender's existing Operator Preset pattern
(the "+" button seen on the Render Properties panel and many operator redo panels):

1. **Save Preset** — captures the active object's selected Bevel modifier's full parameter
   set to a `.py` file in `bpy.utils.user_resource('CONFIG')/presets/bevel_modifier/`
2. **Load Preset** — reads a preset file and applies its parameters to the active Bevel
   modifier on the active object
3. **Delete Preset** — removes the preset file
4. **Preset menu** — a dropdown in the Bevel modifier panel listing all saved presets;
   selecting one loads it

Presets store every Bevel modifier parameter except Custom Profile control points (handled
separately by Blender's existing Save Profile As / Load Profile mechanism). Custom Profile
is referenced by preset filename pointer if one is set.

## Host Application

- Application: Blender
- Minimum version: Blender 4.0+ (validated baseline; Bevel modifier RNA stable since 2.9x)
- API surfaces used:
  - `bpy.types.Operator` — Save / Load / Delete
  - `bpy.types.Menu` — preset dropdown (subclass of `bpy.types.Menu`, draw `bpy.utils.preset_paths`)
  - `bl_operators.presets.AddPresetBase` — reuse Blender's built-in preset infrastructure
  - `DATA_PT_modifiers` — append preset row to Bevel modifier sub-panel via
    `bpy.types.DATA_PT_modifiers.append()` (or modifier-specific draw extension)
  - `bpy.utils.user_resource('CONFIG')` — preset directory

## User Interface

### Bevel modifier panel — appended row

A new row at the top of every Bevel modifier sub-panel:

```
┌───────────────────────────────────────────┐
│ Bevel                                     │
│  Preset: [My Hard Edge ▾]  [+] [-]        │
│  Width Type: Offset                       │
│  Width: 0.02 m                            │
│  Segments: 3                              │
│  ... (rest of Bevel UI unchanged)         │
└───────────────────────────────────────────┘
```

- Dropdown: lists all `.py` files in the preset directory; "(none)" placeholder when empty
- `+` button: opens Save Preset dialog (asks for name)
- `-` button: deletes the currently selected preset (with confirm)

### F3 Search

- "Save Bevel Preset"
- "Load Bevel Preset"
- "Delete Bevel Preset"

## Inputs and Outputs

### Save Bevel Preset
- **Input:** active object with at least one Bevel modifier; preset name (string, validated)
- **Output:** new `.py` preset file in `CONFIG/presets/bevel_modifier/<name>.py`
- **Side effects:** none beyond filesystem write

### Load Bevel Preset
- **Input:** active Bevel modifier on active object; selected preset filename
- **Output:** parameters of the Bevel modifier are overwritten with preset values
- **Side effects:** one undo step

### Delete Bevel Preset
- **Input:** selected preset filename
- **Output:** preset file removed
- **Side effects:** none beyond filesystem delete

## Workflow

```
1. Tune a Bevel modifier on any object until it looks right
2. Click [+] in the Preset row; enter name "Sharp Panel Edge"
3. Open another .blend file
4. Add a Bevel modifier to a new object
5. Click Preset dropdown, select "Sharp Panel Edge"
6. Parameters apply instantly; tweak further if needed
```

## Technical Implementation Notes

### Reuse Blender's preset infrastructure

Subclass `bl_operators.presets.AddPresetBase`. Define `preset_values` as a list of RNA
paths capturing every Bevel modifier property:

```python
preset_values = [
    "modifier.width_type",
    "modifier.width",
    "modifier.segments",
    "modifier.limit_method",
    "modifier.angle_limit",
    "modifier.miter_outer",
    "modifier.miter_inner",
    "modifier.profile_type",
    "modifier.profile",
    "modifier.material",
    "modifier.use_clamp_overlap",
    "modifier.loop_slide",
    "modifier.harden_normals",
    "modifier.face_strength_mode",
    "modifier.mark_seam",
    "modifier.mark_sharp",
    "modifier.vertex_group",
    "modifier.invert_vertex_group",
    "modifier.edge_weight",
]
preset_subdir = "bevel_modifier"
```

`AddPresetBase` writes `.py` files that set these values when executed in Blender's
preset-execution context. Blender handles file IO and the preset menu rendering.

### Active modifier resolution

`context.active_object.modifiers.active` gives the currently-selected modifier in the
Properties panel from Blender 3.5+. Poll fails if there is no active object, no
modifiers, or the active modifier is not a Bevel.

## Edge Cases

- **No active object:** all operators poll-fail; UI row not drawn
- **Active modifier is not Bevel:** preset row not drawn on that modifier panel
- **Preset name collides with existing:** Save dialog warns and asks to overwrite
- **Preset file references a Custom Profile preset that no longer exists:** load proceeds
  with all other parameters; profile stays at modifier's current value; warning in status bar
- **Empty preset directory:** dropdown shows "(none)"; `-` button greyed out
- **User config directory not writable:** Save fails with a clear error; no partial file
- **Loading a preset onto a modifier with linked overrides:** standard Blender override
  rules apply; properties that cannot be overridden are skipped silently (Blender behaviour)

## Known Limitations

- **Custom Profile control points are not embedded** in the preset. Blender already has a
  separate save/load mechanism for the custom profile curve; the preset stores a reference
  to the named profile only. Embedding profile points would require either a binary blob
  in the preset .py or a parallel `.blend` per preset — both are heavier than this addon's
  scope warrants.
- **Bevel operator (Ctrl+B in Edit Mode) is not covered.** Only the Bevel modifier. The
  edge-mode operator has redo-panel preset support already via Blender's per-operator
  preset system; users who want operator presets can use the existing built-in flow.
- **Presets are user-config-scoped, not project-scoped.** A preset saved in a studio's
  shared template flow requires manual copy of the preset .py file to each user's
  CONFIG/presets/bevel_modifier/ directory. This matches how Render Property presets work.

## Acceptance Criteria

1. Addon installs without error on Blender 4.0+ (verify on 4.2 LTS and 5.1)
2. Bevel modifier panel shows the Preset row with dropdown, `+`, and `-` buttons
3. With a tuned Bevel modifier active, clicking `+` and entering "test_preset" creates
   a file at `CONFIG/presets/bevel_modifier/test_preset.py`
4. Opening a fresh .blend, adding a Bevel modifier, and selecting "test_preset" from the
   dropdown sets all 19 captured properties to the saved values
5. Loading a preset is a single undo step
6. Clicking `-` with "test_preset" selected and confirming removes the file
7. Dropdown shows "(none)" when the preset directory is empty
8. Preset row is hidden when no Bevel modifier is active
9. F3 Search lists all three operators
10. Preset survives Blender restart (filesystem, not blend-internal)
11. Loading a preset onto a modifier that already has different values overwrites all
    captured properties; non-captured properties (e.g., show_viewport) are untouched

## Origin

- Source: https://blender.community/c/rightclickselect/yygbbc/ — "Saving Bevel Custom Presets"
- Votes: 67 net, 10 replies
- Status verified: 2026-05-05 — gap still present in Blender 5.1
