# Bevel Modifier Presets

Save the parameter set of a Bevel modifier as a named preset, then recall it on a new modifier in any .blend file.

## The Problem

The Bevel modifier has no built-in preset system. Hard-surface modelers tune the same parameter combinations repeatedly across projects — Offset Type, Width, Segments, Limit Method, Angle, Profile, Shading flags — and have no way to save those tuned setups for reuse in another file.

Workarounds: dig through an old .blend, copy-paste the modifier between objects, or write the values down. None of them travel across projects without manual copying.

## The Solution

Add the **Bevel Presets** panel to the Properties Editor's Modifier tab. It appears whenever the active modifier is a Bevel. The panel has three controls:

- A **preset dropdown** listing every saved preset
- A **[+]** button to save the current Bevel modifier's parameters as a new named preset
- A **[-]** button to delete the selected preset

Presets are stored as `.py` files in Blender's preset directory (`scripts/presets/bevel_modifier/`). They persist across .blend files and across Blender restarts — the same place Blender's built-in Render and Cycles presets live.

The full writable Bevel modifier property surface is captured (22 properties in Blender 4.2 LTS): `affect`, `angle_limit`, `face_strength_mode`, `harden_normals`, `invert_vertex_group`, `limit_method`, `loop_slide`, `mark_seam`, `mark_sharp`, `material`, `miter_inner`, `miter_outer`, `offset_type`, `profile`, `profile_type`, `segments`, `spread`, `use_clamp_overlap`, `vertex_group`, `vmesh_method`, `width`, `width_pct`.

## Installation

1. Download `bevel_presets.py`
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Usage

1. Add a Bevel modifier to any object and tune the parameters until it looks right
2. In the Properties Editor's Modifier tab, expand the **Bevel Presets** panel
3. Click **[+]**, enter a name (e.g. "Sharp Panel Edge"), confirm
4. Open another .blend file, add a Bevel modifier, expand **Bevel Presets**, select the saved preset from the dropdown
5. The 22 parameters apply instantly — tweak further if needed

## Compatibility

- Blender 4.2 LTS (validated baseline). May work on earlier versions, but four of the 22 captured properties (`affect`, `vmesh_method`, `spread`, `width_pct`) need verification on 4.0 / 4.1 before broadening the support claim.
- Uses Blender's built-in `AddPresetBase` and `Menu.draw_preset` infrastructure — the same machinery as Render Properties presets

## Notes

- **Custom Profile curve points are not stored** in the preset. The preset records `profile_type` (Superellipse vs Custom) and the `profile` value, but not the custom-curve control points. Blender's existing **Save Profile As** mechanism in the Custom Profile widget handles curve persistence.
- **One Bevel modifier at a time.** The save and load operators act on the active modifier in the Properties panel (`context.active_object.modifiers.active`). To preset-load several Bevels on the same object, select each in turn and load.
- Presets are user-config-scoped, not embedded in the .blend. Sharing a preset with a teammate means copying the `.py` from `scripts/presets/bevel_modifier/` — same model as Render presets.
